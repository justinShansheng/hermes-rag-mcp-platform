# Hermes RAG MCP Platform

A production-oriented starter for building a complete AI workspace combining:
- Hermes Agent
- RAG knowledge base
- MCP tools
- Vue dashboard
- local and cloud model routing

## Features

- FastAPI backend with auth and session persistence
- model router with Ollama + OpenRouter
- SQLite-ready session storage and upload workflow
- RAG indexing pipeline using vector store abstractions
- central MCP registry for filesystem, GitHub, and web search
- Docker Compose for local orchestration

## Production roadmap

- switch SQLite to PostgreSQL
- move from local FAISS to Qdrant/Pinecone
- add user RBAC and audit logs
- add tool-call telemetry and metrics
- deploy behind Nginx with TLS and secrets management

## Run locally

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

## Core endpoints

- GET /health
- GET /api/models
- POST /api/chat
- POST /api/rag/upload
- POST /api/rag/index
- GET /api/mcp/tools
- POST /api/mcp/call
- GET /api/sessions
- POST /api/sessions

## Next implementation target

The current production scope is to move this from local prototype to enterprise-ready backend: persistent storage, Qdrant indexing, tool telemetry, and deployment automation.
