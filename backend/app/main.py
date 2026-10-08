import os
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.llm_service import LLMService
from app.mcp_client import MCPClient
from app.rag_service import RAGService

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()
mcp_client = MCPClient()
llm_service = LLMService()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


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


@app.get("/api/mcp/tools")
async def list_mcp_tools() -> dict:
    return await mcp_client.list_tools()


@app.post("/api/rag/index")
async def index_documents(payload: dict) -> dict:
    files = payload.get("files", [])
    return await rag_service.index_files(files)


@app.post("/api/rag/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    safe_name = os.path.basename(file.filename or "document.txt")
    path = os.path.join(UPLOAD_DIR, safe_name)
    with open(path, "wb") as fh:
        content = await file.read()
        fh.write(content)

    return {
        "status": "uploaded",
        "filename": safe_name,
        "path": path,
    }


@app.post("/api/chat")
async def chat(payload: dict) -> dict:
    question = (payload.get("question") or "").strip()
    model = (payload.get("model") or settings.default_model).strip()
    if not question:
        return {"answer": "Question cannot be empty.", "context": [], "tools": {}}

    context = await rag_service.search(question, top_k=5)
    tools_status = await mcp_client.get_tools_status()

    try:
        answer = await rag_service.answer_with_context(question, context, model=model, llm_service=llm_service)
    except Exception as exc:
        answer = f"Model error: {exc}"

    return {
        "answer": answer,
        "context": context,
        "tools": tools_status,
        "model": model,
    }


@app.post("/api/mcp/call")
async def call_mcp_tool(payload: dict) -> dict:
    server = payload.get("server") or "filesystem"
    tool_name = payload.get("tool") or "list_dir"
    args = payload.get("args") or {}
    return await mcp_client.call_tool(server=server, tool_name=tool_name, payload=args)
