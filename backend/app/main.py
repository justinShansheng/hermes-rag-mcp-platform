from fastapi import FastAPI, HTTPException
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
