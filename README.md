# Hermes RAG MCP Platform

Production-ready starter for building a complete AI workspace combining:
- Hermes Agent
- RAG knowledge base
- MCP tools
- Vue dashboard
- Ollama + cloud model routing

## Production architecture

- FastAPI API layer
- SQLite-backed session persistence
- Local vector store abstraction with Qdrant-ready extension
- central MCP registry
- model router with Ollama + OpenRouter
- Docker Compose deployment scaffold

## Included features

- chat sessions
- file upload and indexing
- session storage
- model switching
- tool registry and invocation
- health and metrics endpoints

## Local startup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

```bash
cd frontend
npm install
npm run dev
```

```bash
ollama serve
```

## Production checklist

- replace SQLite with PostgreSQL
- replace local FAISS with Qdrant / Pinecone
- add user RBAC and audit logging
- add monitoring and API rate limiting
- deploy behind Nginx + TLS
- secure secrets via environment management

## Core endpoints

- GET /health
- GET /api/health
- GET /api/metrics
- GET /api/models
- POST /api/chat
- POST /api/rag/upload
- POST /api/rag/index
- GET /api/session
- POST /api/sessions
- GET /api/mcp/tools
- POST /api/mcp/call

## Next implementation targets

- PostgreSQL migration
- Qdrant integration
- real Hermes runtime orchestration
- production tool execution telemetry
- multi-user dashboard and authorization
