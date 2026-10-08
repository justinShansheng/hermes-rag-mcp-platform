# Hermes RAG MCP Platform - Production Edition

## Overview

A production-grade AI platform combining:
- Hermes Agent orchestration
- RAG knowledge base with Qdrant
- MCP tool ecosystem
- PostgreSQL persistence
- Vue.js dashboard
- Local and cloud model routing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue.js Dashboard                          │
├─────────────────────────────────────────────────────────────┤
│                   FastAPI Backend (0.2.0)                   │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │   Sessions   │   Chat       │   Documents  │             │
│  │   & Auth     │   Service    │   & RAG      │             │
│  └──────────────┴──────────────┴──────────────┘             │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │   MCP        │   LLM        │   Agent      │             │
│  │   Registry   │   Router     │   Orches     │             │
│  └──────────────┴──────────────┴──────────────┘             │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL    │    Qdrant     │    Redis     │  Ollama     │
│  Sessions      │  Vector Store │    Cache     │   Models    │
│  Users, Docs   │  & Search     │              │             │
└─────────────────────────────────────────────────────────────┘
```

## Production Features

### Data Persistence
- PostgreSQL for user, session, document, and audit data
- Qdrant for semantic vector search
- Redis for caching and task queues

### Authentication & Authorization
- JWT token-based auth
- Role-based access control (RBAC)
- Audit logging for compliance

### AI Integration
- Hermes Agent runtime
- RAG with Qdrant vector store
- MCP tool registry (filesystem, GitHub, web search)
- Multi-model LLM router (Ollama + OpenRouter)

### Observability
- API usage metrics
- Tool invocation logs
- Audit trails
- Health check endpoints

## Setup

### Local Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```env
APP_ENV=development
POSTGRES_URL=postgresql://hermes:hermes@localhost:5432/hermes
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379/0
OLLAMA_BASE_URL=http://localhost:11434
API_KEY=demo-key
```

### Docker Compose Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

This starts:
- PostgreSQL (port 5432)
- Qdrant (port 6333)
- Redis (port 6379)
- Ollama (port 11434)
- FastAPI backend (port 8001)
- Vue frontend (port 5173)

## Core API Endpoints

### Auth
- POST `/api/auth/register`
- POST `/api/auth/login`

### Sessions
- GET `/api/sessions`
- POST `/api/sessions`
- GET `/api/sessions/{id}/messages`

### Chat
- POST `/api/chat`

### RAG
- POST `/api/rag/upload`
- POST `/api/rag/index`

### MCP
- GET `/api/mcp/tools`
- POST `/api/mcp/call`

### Admin
- GET `/admin/users`
- PUT `/admin/users/{id}/role`
- GET `/admin/audit-logs`

## Database Schema

key tables:
- `users` - user accounts and roles
- `sessions` - chat sessions
- `messages` - chat history
- `documents` - uploaded files
- `tool_invocations` - MCP tool call logs
- `audit_logs` - compliance tracking

## Deployment

Ready for deployment to:
- Docker Swarm
- Kubernetes
- AWS ECS
- Google Cloud Run
- Any container orchestration platform

## Next Steps

- [ ] Add Kubernetes manifests
- [ ] Add monitoring (Prometheus + Grafana)
- [ ] Add request logging (ELK stack)
- [ ] Add rate limiting and quota management
- [ ] Add webhook integrations
- [ ] Add real-time WebSocket chat
- [ ] Add model fine-tuning pipeline
