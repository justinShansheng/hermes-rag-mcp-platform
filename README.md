# Hermes RAG MCP Platform

A starter for building a complete AI workspace combining:
- Hermes Agent
- RAG knowledge base
- MCP tool layer
- Vue dashboard
- Ollama + cloud model routing

## Included

- FastAPI backend
- Vue 3 dashboard
- Knowledge-base upload + indexing flow
- MCP stub adapters
- Local / cloud model routing
- Docker Compose template

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

Set in `.env`:

```env
OPENROUTER_API_KEY=your_key_here
```

## Useful API endpoints

- GET `/api/models`
- POST `/api/chat`
- POST `/api/rag/upload`
- POST `/api/rag/index`
- GET `/api/mcp/tools`
- POST `/api/mcp/call`

## Real-world next step

The production-ready follow-up is to connect real MCP servers such as:
- GitHub MCP
- Filesystem MCP
- Web Search MCP
- Notion / Obsidian MCP

Then expose them through the Vue dashboard and route agent requests through Hermes plus a persistent vector store.
