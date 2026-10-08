# Hermes RAG MCP Platform - Production Edition

## 🚀 Overview

A production-grade AI platform combining:
- **Hermes Agent** orchestration
- **RAG** (Retrieval-Augmented Generation) knowledge base with Qdrant/FAISS
- **MCP** tool ecosystem (Model Context Protocol)
- **PostgreSQL** persistence
- **Vue.js 3** dashboard
- **Local** (Ollama) and **cloud** (OpenRouter) model routing
- **Real-time** WebSocket chat
- **Monitoring** & **deployment** management

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue.js Dashboard (5173)                  │
├─────────────────────────────────────────────────────────────┤
│                   FastAPI Backend (0.2.0)                   │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │   Sessions   │   Chat       │   WebSocket  │             │
│  │   & Auth     │   Service    │   Live Chat  │             │
│  └──────────────┴──────────────┴──────────────┘             │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │   MCP        │   LLM        │   Agent      │             │
│  │   Registry   │   Router     │   Orches     │             │
│  └──────────────┴──────────────┴──────────────┘             │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL    │    Qdrant     │    Redis     │  Ollama     │
│  Sessions      │  Vector Store │    Cache     │   Models    │
│  Users, Docs   │  & Search     │              │   + Cloud   │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Core Capabilities
- ✅ **Real-time Chat** - WebSocket-based streaming responses
- ✅ **Multi-Model Support** - Local (Ollama: llama3.1, qwen2.5, deepseek) + Cloud (OpenRouter)
- ✅ **RAG Integration** - Upload docs, auto-index, semantic search
- ✅ **MCP Tools** - Filesystem, GitHub, Web Search integrations
- ✅ **User Authentication** - JWT tokens with roles (user/admin)
- ✅ **Monitoring Dashboard** - CPU, memory, uptime, service health
- ✅ **Deployment Status** - Container orchestration visibility
- ✅ **Admin Panel** - User management, audit logs, role control

### Data Persistence
- PostgreSQL for user, session, document, and audit data
- Qdrant/FAISS for semantic vector search
- Redis for caching and task queues

### Observability
- API usage metrics
- Tool invocation logs
- Audit trails for compliance
- Health check endpoints

## 🛠️ Setup

### Quick Start (Docker)

```bash
# Clone repository
git clone https://github.com/justinShansheng/hermes-rag-mcp-platform.git
cd hermes-rag-mcp-platform

# Copy environment
cp .env.example .env

# Start development stack
make dev

# Access services
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8001
# Qdrant:    http://localhost:6333
# Ollama:    http://localhost:11434
```

### Local Development

```bash
# Backend (requires Python 3.11+)
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (requires Node 18+)
cd frontend
npm install
npm run dev
```

### Production Deployment

```bash
# Using docker-compose.prod.yml
make prod-up

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Chat & Sessions
- `GET /api/sessions` - List user sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{id}/messages` - Get session messages
- `POST /api/chat` - Send message (HTTP)
- `WS /ws/chat` - Real-time chat (WebSocket)

### RAG
- `POST /api/rag/upload` - Upload document
- `POST /api/rag/index` - Index documents

### MCP Tools
- `GET /api/mcp/tools` - List available tools
- `POST /api/mcp/call` - Call MCP tool

### Monitoring
- `GET /api/health` - Health check
- `GET /api/metrics` - Basic metrics
- `GET /api/monitoring` - Detailed monitoring data
- `GET /api/dashboard` - Dashboard overview

### Admin
- `GET /api/admin/users` - List users
- `PUT /api/admin/users/{id}/role` - Update user role
- `GET /api/admin/audit-logs` - View audit logs

## 🗄️ Database Schema

### Tables
- `users` - User accounts and roles
- `sessions` - Chat sessions
- `messages` - Chat history
- `documents` - Uploaded files
- `tool_invocations` - MCP tool call logs
- `audit_logs` - Compliance tracking

## 🔧 Configuration

Edit `.env` to customize:

```env
# Local LLM
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.1:8b

# Cloud LLM
OPENROUTER_API_KEY=your-key-here

# Database
POSTGRES_URL=postgresql://hermes:hermes@localhost:5432/hermes

# Vector Store
QDRANT_URL=http://localhost:6333
RAG_VECTOR_STORE=faiss

# Security
API_KEY=your-api-key
```

## 📦 Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM for PostgreSQL
- **LangChain** - LLM orchestration
- **Sentence Transformers** - Embeddings
- **FAISS** - Vector indexing

### Frontend
- **Vue 3** - Reactive UI framework
- **Vite** - Build tool
- **WebSocket** - Real-time communication

### Infrastructure
- **PostgreSQL** - Relational database
- **Qdrant** - Vector database
- **Redis** - Cache & queues
- **Ollama** - Local LLM runtime
- **Docker** - Containerization

## 📊 Monitoring

Access the monitoring dashboard at `http://localhost:5173`:
- Real-time chat with streaming responses
- System metrics (CPU, memory, uptime)
- Service health status
- Document indexing progress
- User activity audit trail

## 🚀 Deployment Options

- Docker Swarm
- Kubernetes (manifests available)
- AWS ECS / Fargate
- Google Cloud Run
- DigitalOcean App Platform
- Azure Container Instances

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please submit PRs with:
1. Clear description of changes
2. Test coverage where applicable
3. Updated documentation

## 📧 Support

For issues and questions:
- GitHub Issues: https://github.com/justinShansheng/hermes-rag-mcp-platform/issues
- Discussions: https://github.com/justinShansheng/hermes-rag-mcp-platform/discussions
