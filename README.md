# Hermes RAG MCP Platform

A full-stack starter for combining:
- Hermes Agent
- RAG knowledge base
- MCP tool integration
- Vue control panel
- Ollama + cloud model routing

## Included

- Python FastAPI backend
- Vue 3 + Vite frontend
- FAISS-based RAG store
- MCP stub service layer
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

Visit: http://localhost:5173

## Notes

- The backend expects a local Hermes server at `http://localhost:8000` for agent integration.
- MCP endpoints are stubbed for easy extension.
- You can replace the in-memory RAG service with vector DB or external knowledge services later.

## Production extension ideas

- Add persistent vector DB (Qdrant / Pinecone / Weaviate)
- Add secure auth
- Add file upload UI
- Add real MCP servers for GitHub, Notion, filesystem, and web search
- Add cloud model use via OpenRouter / OpenAI / Anthropic
