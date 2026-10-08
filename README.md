# Hermes RAG MCP Platform

Production-grade starter for building a complete AI platform combining:
- Hermes Agent
- RAG knowledge base
- MCP tools
- Vue dashboard
- Ollama + cloud model routing

## Architecture

```text
Frontend (Vue 3 + Vite)
        |
        v
FastAPI Backend
        |
   +---- RAG Layer (FAISS + embeddings)
   +---- MCP Adapters
   +---- LLM Router (Ollama / OpenRouter)
   +---- Session Storage
   +---- Auth + API Gateway
        |
        v
Hermes Agent / local model / cloud model
```

## Included

- FastAPI backend with auth and session persistence
- Vue 3 dashboard with chat, sessions, upload and model selection
- Persistent SQLite session storage
- RAG indexing + similarity search
- LLM routing for Ollama and OpenRouter
- MCP adapters for filesystem, GitHub and web search
- Docker Compose deployment template

## Run locally

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3) Ollama

```bash
ollama serve
```

### 4) Optional OpenRouter cloud access

Create `.env` with:

```env
OPENROUTER_API_KEY=your_key_here
API_KEY=demo-key
```

## Core API

- GET `/health`
- GET `/api/models`
- POST `/api/auth/token`
- GET `/api/sessions`
- POST `/api/sessions`
- GET `/api/sessions/{id}/messages`
- POST `/api/chat`
- POST `/api/rag/upload`
- POST `/api/rag/index`
- GET `/api/mcp/tools`
- POST `/api/mcp/call`

## Example calls

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Hermes Agent?","model":"llama3.1:8b"}'
```

```bash
curl -X POST http://localhost:8001/api/mcp/call \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{"server":"github","tool":"repo_info","args":{"repo":"justinShansheng/hermes-rag-mcp-platform"}}'
```

## Production roadmap

This project is now structured as a production-grade starter for:
- session persistence
- RBAC-ready auth
- vector search and retrieval
- tool invocation logging
- knowledge base indexing
- model routing and fallback
- Docker deployment

## Production next steps

- replace SQLite with PostgreSQL
- move to Qdrant or Pinecone for vector storage
- add real user auth and roles
- add tool execution logs and observability
- add deployment pipeline and reverse proxy
