import logging
import os
from typing import Any

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.agent_service import HermesAgentService
from app.auth import require_api_key
from app.config import settings
from app.database import append_message, create_session, get_messages, get_session, init_db, list_sessions, upsert_session_last_updated
from app.llm_service import LLMService
from app.mcp_client import MCPClient
from app.rag_service import RAGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hermes")

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
rag_service = RAGService()
mcp_client = MCPClient()
llm_service = LLMService()
agent_service = HermesAgentService()
UPLOAD_DIR = os.path.abspath(settings.uploads_dir)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
def startup_event() -> None:
    logger.info("Hermes platform starting")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.get("/api/health")
def api_health() -> dict:
    return {"status": "ok", "service": settings.app_name, "mode": settings.app_env}


@app.get("/api/metrics")
def metrics() -> dict:
    return {"service": settings.app_name, "status": "healthy", "model": settings.default_model}


@app.post("/api/auth/token")
async def get_token(payload: dict) -> dict:
    provided = (payload.get("api_key") or "").strip()
    if not settings.api_key or provided == settings.api_key:
        return {"token": settings.api_key or "demo-key"}
    raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/api/models")
def models() -> dict:
    return {
        "local": ["llama3.1:8b", "qwen2.5:7b", "deepseek-r1:7b"],
        "cloud": [
            "openrouter/gpt-4o-mini",
            "openrouter/claude-3.5-sonnet",
            "openrouter/deepseek-chat",
        ],
    }


@app.get("/api/sessions")
async def sessions(_: Any = Depends(require_api_key)) -> list[dict[str, Any]]:
    return list_sessions()


@app.post("/api/sessions")
async def create_new_session(payload: dict, _: Any = Depends(require_api_key)) -> dict:
    title = (payload.get("title") or "New session").strip() or "New session"
    model = payload.get("model") or settings.default_model
    session_id = create_session(title=title, model=model)
    return {"id": session_id, "title": title, "model": model}


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, _: Any = Depends(require_api_key)) -> dict:
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session": session, "messages": get_messages(session_id)}


@app.get("/api/mcp/tools")
async def list_mcp_tools(_: Any = Depends(require_api_key)) -> dict:
    return await mcp_client.list_tools()


@app.post("/api/rag/index")
async def index_documents(payload: dict, _: Any = Depends(require_api_key)) -> dict:
    files = payload.get("files", [])
    return await rag_service.index_files(files)


@app.post("/api/rag/upload")
async def upload_file(file: UploadFile = File(...), _: Any = Depends(require_api_key)) -> dict:
    safe_name = os.path.basename(file.filename or "document.txt")
    path = os.path.join(UPLOAD_DIR, safe_name)
    with open(path, "wb") as fh:
        fh.write(await file.read())

    return {
        "status": "uploaded",
        "filename": safe_name,
        "path": path,
    }


@app.post("/api/mcp/call")
async def call_mcp_tool(payload: dict, _: Any = Depends(require_api_key)) -> dict:
    server = payload.get("server") or "filesystem"
    tool_name = payload.get("tool") or "list_dir"
    args = payload.get("args") or {}
    logger.info("MCP tool invocation: %s -> %s", server, tool_name)
    return await mcp_client.call_tool(server=server, tool_name=tool_name, payload=args)


@app.post("/api/chat")
async def chat(payload: dict, _: Any = Depends(require_api_key)) -> dict:
    question = (payload.get("question") or "").strip()
    model = (payload.get("model") or settings.default_model).strip()
    session_id = payload.get("session_id")

    if not question:
        return {"answer": "Question cannot be empty.", "context": [], "tools": {}, "session_id": session_id}

    if session_id:
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session_id = create_session(title=question[:48] or "New chat", model=model)

    context = await rag_service.search(question, top_k=5)
    tools_status = await mcp_client.get_tools_status()
    append_message(session_id, "user", question)

    try:
        answer_text = await rag_service.answer_with_context(question, context, model=model, llm_service=llm_service)
    except Exception:
        answer_text = await agent_service.chat(model=model, prompt=question)

    append_message(session_id, "assistant", answer_text)
    upsert_session_last_updated(session_id)

    return {
        "answer": answer_text,
        "context": context,
        "tools": tools_status,
        "model": model,
        "session_id": session_id,
    }
