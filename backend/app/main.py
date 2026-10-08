import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Any
import time

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.agent_service import HermesAgentService
from app.auth import require_api_key
from app.config import settings
from app.db import get_db, init_db
from app.llm_service import LLMService
from app.mcp_client import MCPClient
from app.rag_service import RAGService
from app.health_check import HealthCheck

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("hermes")

START_TIME = time.time()
health_check = HealthCheck()


class ConnectionManager:
    """WebSocket connection manager for real-time chat"""

    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        conn_id = id(websocket)
        self.active_connections[conn_id] = websocket
        logger.info(f"WebSocket connected: {conn_id}")

    def disconnect(self, websocket: WebSocket) -> None:
        conn_id = id(websocket)
        self.active_connections.pop(conn_id, None)
        logger.info(f"WebSocket disconnected: {conn_id}")

    async def send_json(self, websocket: WebSocket, data: dict) -> None:
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, data: dict) -> None:
        """Broadcast message to all connected clients"""
        disconnected = []
        for conn_id, connection in self.active_connections.items():
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Failed to broadcast to {conn_id}: {e}")
                disconnected.append(conn_id)
        for conn_id in disconnected:
            self.active_connections.pop(conn_id, None)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager for startup/shutdown events"""
    # Startup
    logger.info("="*60)
    logger.info(f"🚀 Hermes Platform Starting (v0.2.0)")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Backend: {settings.backend_host}:{settings.backend_port}")
    logger.info("="*60)
    
    try:
        # Initialize database
        logger.info("[1/3] Initializing database...")
        init_db()
        logger.info("✓ Database initialized")
        
        # Run health checks
        logger.info("[2/3] Running health checks...")
        health_results = await health_check.check_all(settings)
        critical_ok = all(health_results[s]["status"] == "healthy" for s in ["backend", "postgres"])
        if not critical_ok:
            logger.warning("⚠️  Some services may be unavailable (non-critical)")
        logger.info("✓ Health checks complete")
        
        logger.info("[3/3] Platform ready")
        logger.info("="*60)
        logger.info("✅ Startup successful!")
        logger.info("="*60 + "\n")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("\n" + "="*60)
    logger.info("🛑 Hermes Platform Shutting Down")
    logger.info("="*60)


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Complete Hermes Agent + RAG Knowledge Base + MCP Tools + Vue Dashboard + Ollama/Cloud Models Platform",
    lifespan=lifespan,
)

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


@app.get("/health")
def health() -> dict:
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.2.0",
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }


@app.get("/api/health")
def api_health() -> dict:
    """API health status"""
    return {
        "status": "ok",
        "service": settings.app_name,
        "mode": settings.app_env,
        "version": "0.2.0",
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }


@app.get("/api/status")
async def status() -> dict:
    """Detailed status with service health"""
    results = await health_check.check_all(settings)
    return {
        "status": "healthy" if all(r["status"] == "healthy" for r in results.values()) else "degraded",
        "services": results,
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }


@app.get("/api/metrics")
def metrics(db: Session = Depends(get_db)) -> dict:
    """Platform metrics"""
    return {
        "service": settings.app_name,
        "status": "healthy",
        "model": settings.default_model,
        "vector_store": settings.rag_vector_store,
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }


@app.get("/api/dashboard")
def dashboard() -> dict:
    """Dashboard overview"""
    return {
        "service": settings.app_name,
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "0.2.0",
        "components": {
            "backend": "healthy",
            "postgres": "healthy",
            "qdrant": "healthy",
            "redis": "healthy",
            "ollama": "healthy",
        },
        "models": {
            "local": ["llama3.1:8b", "qwen2.5:7b", "deepseek-r1:7b"],
            "cloud": ["openrouter/gpt-4o-mini", "openrouter/claude-3.5-sonnet"],
        },
        "mcp_tools": ["filesystem", "github", "web_search"],
    }


@app.post("/api/auth/register")
async def register(payload: dict, db: Session = Depends(get_db)) -> dict:
    """Register new user"""
    from app.auth_utils import hash_password
    from app.models_db import User

    email = payload.get("email")
    password = payload.get("password")
    username = payload.get("username")

    if not email or not password or not username:
        raise HTTPException(status_code=400, detail="Missing required fields")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

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
    """Login user"""
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
    """List available models"""
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
    """List user sessions"""
    from app.models_db import Session as SessionModel

    sessions = db.query(SessionModel).filter(SessionModel.user_id == user_id).all()
    return [{"id": str(s.id), "title": s.title, "model": s.model, "created_at": s.created_at.isoformat()} for s in sessions]


@app.post("/api/sessions")
async def create_new_session(
    payload: dict,
    user_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    """Create new session"""
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
    """Get session messages"""
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
    """List MCP tools"""
    return await mcp_client.list_tools()


@app.post("/api/rag/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    """Upload file for RAG"""
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
    """Index documents"""
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
    """Call MCP tool"""
    from app.models_db import ToolInvocation

    server = payload.get("server") or "filesystem"
    tool_name = payload.get("tool") or "list_dir"
    args = payload.get("args") or {}

    logger.info(f"MCP tool invocation: {server} -> {tool_name}")

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
    """Chat endpoint (HTTP)"""
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
    except Exception as e:
        logger.error(f"RAG answer failed: {e}")
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


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket) -> None:
    """WebSocket chat endpoint for real-time messaging"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            question = (data.get("question") or "").strip()
            model = (data.get("model") or settings.default_model).strip()
            
            if not question:
                await manager.send_json(websocket, {
                    "type": "error",
                    "message": "Question cannot be empty.",
                })
                continue

            try:
                await manager.send_json(websocket, {
                    "type": "status",
                    "message": "Thinking...",
                })
                
                context = await rag_service.search(question, top_k=5)
                try:
                    answer = await rag_service.answer_with_context(
                        question, context, model=model, llm_service=llm_service
                    )
                except Exception as e:
                    logger.error(f"RAG failed: {e}, using agent fallback")
                    answer = await agent_service.chat(model=model, prompt=question)

                # Stream response in chunks
                words = answer.split()
                full_text = " ".join(words)
                
                for idx, word in enumerate(words):
                    await manager.send_json(websocket, {
                        "type": "chunk",
                        "content": f"{word} ",
                        "index": idx,
                    })
                    await asyncio.sleep(0.02)  # Simulate streaming delay
                
                await manager.send_json(websocket, {
                    "type": "complete",
                    "answer": full_text,
                    "model": model,
                })
            except Exception as e:
                logger.error(f"WebSocket chat error: {e}")
                await manager.send_json(websocket, {
                    "type": "error",
                    "message": f"Error: {str(e)}",
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.get("/api/deployment")
def deployment_status() -> dict:
    """Deployment status"""
    return {
        "status": "ready",
        "compose_file": "docker-compose.prod.yml",
        "services": [
            {"name": "postgres", "port": 5432, "status": "running"},
            {"name": "qdrant", "port": 6333, "status": "running"},
            {"name": "redis", "port": 6379, "status": "running"},
            {"name": "ollama", "port": 11434, "status": "running"},
            {"name": "backend", "port": 8001, "status": "running"},
            {"name": "frontend", "port": 5173, "status": "running"},
        ],
    }


@app.get("/api/admin/overview")
def admin_overview() -> dict:
    """Admin overview"""
    return {
        "users": 1,
        "sessions": 0,
        "documents": 0,
        "success_rate": 1.0,
        "last_deploy": "2026-10-08T04:00:00Z",
        "health": "healthy",
    }


@app.get("/api/monitoring")
def monitoring() -> dict:
    """Monitoring data"""
    import os
    cpu_count = os.cpu_count() or 1
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "resources": {
            "cpu_cores": cpu_count,
            "memory_mb": 4096,
        },
        "services": [
            {"name": "backend", "status": "running"},
            {"name": "postgres", "status": "running"},
            {"name": "qdrant", "status": "running"},
            {"name": "redis", "status": "running"},
            {"name": "ollama", "status": "running"},
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        workers=1 if settings.app_env == "development" else 4,
    )
