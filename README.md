# Hermes RAG MCP Platform

A full-stack starter for combining:
- Hermes Agent
- RAG knowledge base
- MCP tool integration
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
   +---- MCP Adapter
   +---- LLM Router (Ollama / OpenRouter)
        |
        v
Hermes Agent / local model / cloud model
```

## Included

- Python FastAPI backend
- Vue 3 control panel
- RAG indexing + similarity search
- LLM routing for Ollama and OpenRouter
- MCP adapter stub layer
- Docker Compose setup

## Quick Start

### 1) Install backend dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Install frontend dependencies

```bash
cd frontend
npm install
```

### 3) Start Ollama locally

```bash
ollama serve
```

If you want cloud models, create a `.env` file from `.env.example` and set `OPENROUTER_API_KEY`.

### 4) Start backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 5) Start frontend

```bash
cd frontend
npm run dev
```

### 6) Open UI

Visit:
- Frontend: http://localhost:5173
- Backend docs: http://localhost:8001/docs

## Example API calls

### Ask a question

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Hermes Agent?","model":"llama3.1:8b"}'
```

### Fetch available models

```bash
curl http://localhost:8001/api/models
```

### Index text files

```bash
curl -X POST http://localhost:8001/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{"files":["/path/to/file.txt"]}'
```

## Production extensions

- Add file upload endpoint and UI
- Add real MCP servers (GitHub, filesystem, web search, Notion)
- Add Qdrant or Pinecone persistence
- Add auth + user management
- Add model fallback policy
- Add observability and metrics

## Recommended next step

The next upgrade is to connect the backend to a real Hermes Agent session and a real MCP server catalog, then expose those tools in the Vue dashboard as cards and actions.
