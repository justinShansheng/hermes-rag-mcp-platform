import logging
from typing import Any

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.agent_service import HermesAgentService
from app.auth import require_api_key
from app.config import settings
from app.db import get_db
from app.llm_service import LLMService
from app.mcp_client import MCPClient
from app.rag_service import RAGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hermes")

app = FastAPI(title=settings.app_name, version="0.2.0")
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
agent_service = HermesAgentService()


@app.on_event("startup")
def startup_event() -> None:
    logger.info("Hermes platform starting (v0.2.0 production)")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": "0.2.0"}


@app.get("/api/health")
def api_health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "mode": settings.app_env,
        "version": "0.2.0",
    }


@app.get("/api/metrics")
def metrics(db: Session = Depends(get_db)) -> dict:
    return {
        "service": settings.app_name,
        "status": "healthy",
        "model": settings.default_model,
        "vector_store": settings.rag_vector_store,
    }


@app.post("/api/auth/register")
async def register(payload: dict, db: Session = Depends(get_db)) -> dict:
    from app.auth_utils import hash_password
    from app.models_db import User

    email = payload.get("email")
    password = payload.get("password")
    username = payload.get("username")

    if not email or not password or not username:
        raise HTTPException(status_code=400, detail="Missing required fields")

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": str(user.id), "email": email, "username": username}


@app.post("/api/auth/login")
async def login(payload: dict, db: Session = Depends(get_db)) -> dict:
    from app.auth_utils import create_access_token, verify_password
    from app.models_db import User

    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer", "user_id": str(user.id)}


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
async def list_sessions(user_id: str = Depends(require_api_key), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    from app.models_db import Session as SessionModel

    sessions = db.query(SessionModel).filter(SessionModel.user_id == user_id).all()
    return [{"id": str(s.id), "title": s.title, "model": s.model, "created_at": s.created_at.isoformat()} for s in sessions]


@app.post("/api/sessions")
async def create_new_session(
    payload: dict,
    user_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    from app.models_db import Session as SessionModel

    title = (payload.get("title") or "New session").strip() or "New session"
    model = payload.get("model") or settings.default_model

    session = SessionModel(user_id=user_id, title=title, model=model)
    db.add(session)
    db.commit()
    db.refresh(session)

    return {"id": str(session.id), "title": title, "model": model}


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    user_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    from app.models_db import Message, Session as SessionModel

    session = db.query(SessionModel).filter(SessionModel.id == session_id, SessionModel.user_id == user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(Message).filter(Message.session_id == session_id).all()
    return {
        "session": {"id": str(session.id), "title": session.title},
        "messages": [{"id": str(m.id), "role": m.role, "content": m.content} for m in messages],
    }


@app.get("/api/mcp/tools")
async def list_mcp_tools(user_id: str = Depends(require_api_key)) -> dict:
    return await mcp_client.list_tools()


@app.post("/api/rag/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    import os

    from app.models_db import Document

    safe_name = os.path.basename(file.filename or "document.txt")
    path = os.path.join(settings.uploads_dir, safe_name)
    os.makedirs(settings.uploads_dir, exist_ok=True)

    with open(path, "wb") as fh:
        fh.write(await file.read())

    doc = Document(user_id=user_id, filename=safe_name, file_path=path, file_size=os.path.getsize(path))
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "status": "uploaded",
        "filename": safe_name,
        "path": path,
        "document_id": str(doc.id),
    }


@app.post("/api/rag/index")
async def index_documents(
    payload: dict,
    user_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    files = payload.get("files", [])
    result = await rag_service.index_files(files)

    from app.models_db import Document

    for path in files:
        db.query(Document).filter(Document.file_path == path).update({"indexed": True})
    db.commit()

    return result


@app.post("/api/mcp/call")
async def call_mcp_tool(
    payload: dict,
    user_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    from app.models_db import ToolInvocation

    server = payload.get("server") or "filesystem"
    tool_name = payload.get("tool") or "list_dir"
    args = payload.get("args") or {}

    logger.info("MCP tool invocation: %s -> %s", server, tool_name)

    result = await mcp_client.call_tool(server=server, tool_name=tool_name, payload=args)

    invocation = ToolInvocation(
        user_id=user_id,
        server_name=server,
        tool_name=tool_name,
        args=args,
        result=result,
        status="ok" if result.get("status") == "ok" else "error",
    )
    db.add(invocation)
    db.commit()

    return result


@app.post("/api/chat")
async def chat(
    payload: dict,
    user_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    from app.models_db import Message, Session as SessionModel

    question = (payload.get("question") or "").strip()
    model = (payload.get("model") or settings.default_model).strip()
    session_id = payload.get("session_id")

    if not question:
        return {"answer": "Question cannot be empty.", "context": [], "tools": {}, "session_id": session_id}

    if session_id:
        session = db.query(SessionModel).filter(SessionModel.id == session_id, SessionModel.user_id == user_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = SessionModel(user_id=user_id, title=question[:48] or "New chat", model=model)
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = str(session.id)

    context = await rag_service.search(question, top_k=5)
    tools_status = await mcp_client.get_tools_status()

    user_msg = Message(session_id=session_id, role="user", content=question)
    db.add(user_msg)
    db.commit()

    try:
        answer_text = await rag_service.answer_with_context(question, context, model=model, llm_service=llm_service)
    except Exception:
        answer_text = await agent_service.chat(model=model, prompt=question)

    assistant_msg = Message(session_id=session_id, role="assistant", content=answer_text)
    db.add(assistant_msg)
    db.commit()

    return {
        "answer": answer_text,
        "context": context,
        "tools": tools_status,
        "model": model,
        "session_id": session_id,
    }
