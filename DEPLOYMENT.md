# Hermes RAG MCP Platform - Deployment & Debugging Guide

## 快速启动

### Development
```bash
chmod +x startup.sh
./startup.sh dev
```

### Production
```bash
chmod +x startup.sh
./startup.sh prod
```

## 验证检查清单

### ✅ 启动服务验证

```bash
# 运行启动检查
python backend/startup_check.py
```

期望输出：
```
=== Environment Verification ===
✓ POSTGRES_URL: postgresql://hermes:hermes@localhost:5432/hermes
✓ OLLAMA_BASE_URL: http://localhost:11434
✓ API_KEY: demo-key

=== Import Verification ===
✓ FastAPI
✓ SQLAlchemy
✓ LangChain
✓ Sentence Transformers
✓ FAISS

=== Database Verification ===
✓ Database schema initialized
✓ Database has 8 tables

=== Services Verification ===
✓ backend: healthy
✓ postgres: healthy
✓ redis: healthy
✓ qdrant: healthy
✓ ollama: healthy
```

### ✅ 端口和环境变量检查

```bash
# 查看所有容器端口
docker-compose ps

# 期望结果：
# backend    -> 8001:8001
# frontend   -> 5173:5173
# postgres   -> 5432:5432
# redis      -> 6379:6379
# qdrant     -> 6333:6333
# ollama     -> 11434:11434
```

### ✅ WebSocket 聊天稳定性

```bash
# 测试 WebSocket 连接
wscat -c ws://localhost:8001/ws/chat

# 发送测试消息
{"question": "Hello", "model": "llama3.1:8b", "session_id": null}
```

期望响应：
```json
{"type": "status", "message": "Thinking..."}
{"type": "chunk", "content": "Hello", "index": 0}
{"type": "complete", "answer": "...", "model": "llama3.1:8b"}
```

### ✅ 数据库初始化检查

```bash
# 进入 PostgreSQL
docker-compose exec postgres psql -U hermes -d hermes

# 查看所有表
\dt

# 期望表:
# - users
# - sessions
# - messages
# - documents
# - tool_invocations
# - audit_logs

# 检查表结构
\d users
\d sessions
\d messages
```

### ✅ 权限链路检查

```bash
# 测试注册
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "testpass"}'

# 测试登录
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}'

# 期望获得 JWT token
```

## 常见问题排查

### 问题 1: PostgreSQL 连接失败

```bash
# 检查 PostgreSQL 容器状态
docker-compose logs postgres

# 检查连接字符串
echo $POSTGRES_URL

# 应该是: postgresql://hermes:hermes@postgres:5432/hermes (Docker)
# 或:    postgresql://hermes:hermes@localhost:5432/hermes (本地)
```

### 问题 2: WebSocket 连接超时

```bash
# 检查后端服务是否运行
curl http://localhost:8001/health

# 查看后端日志
docker-compose logs backend

# 确保前端指向正确的后端地址
# http://localhost:8001 (本地)
# http://backend:8001 (Docker)
```

### 问题 3: Ollama 模型加载失败

```bash
# 检查 Ollama 服务
curl http://localhost:11434/api/tags

# 拉取模型
curl -X POST http://localhost:11434/api/pull -d '{"name": "llama3.1:8b"}'

# 等待模型下载完成
```

### 问题 4: 数据库表不存在

```bash
# 手动初始化数据库
cd backend
python -c "from app.db import init_db; init_db()"

# 或运行 SQL 脚本
docker-compose exec postgres psql -U hermes -d hermes -f /docker-entrypoint-initdb.d/001_init_schema.sql
```

## 调试工具

### 查看日志
```bash
chmod +x logs.sh
./logs.sh backend       # 查看后端日志
./logs.sh frontend      # 查看前端日志
./logs.sh postgres      # 查看数据库日志
```

### 运行调试工具
```bash
chmod +x debug.sh
./debug.sh
```

输出示例：
```
[1] Checking Docker containers...
CONTAINER ID   IMAGE           PORTS
abc123         hermes-backend  8001:8001
def456         hermes-postgres 5432:5432

[2] Testing backend health...
{"status": "ok", "version": "0.2.0"}

[3] Testing database connection...
1

[4] Testing Ollama...
{"models": [{"name": "llama3.1:8b"}]}

[5] Testing Qdrant...
{"status": "ok"}

[6] Testing Redis...
PONG
```

## 停止服务

```bash
chmod +x shutdown.sh
./shutdown.sh
```

## 性能监控

```bash
# 监控资源使用
docker stats

# 查看容器资源限制
docker-compose ps -a --no-trunc
```

## 生产部署

### 使用 docker-compose.prod.yml

```bash
# 创建 .env.prod
cp .env.example .env.prod
# ��辑 .env.prod 使用生产配置

# 启动
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 使用 Kubernetes

```bash
# 创建命名空间
kubectl create namespace hermes

# 部署
kubectl apply -f k8s/ -n hermes

# 查看状态
kubectl get pods -n hermes
```

## 性能优化

### 后端
- 启用 uvicorn 多进程: `workers=4`
- 配置连接池大小
- 启用 Redis 缓存

### 前端
- 启用 Vite 代码分割
- 压缩静态资源
- 使用 CDN 加速

### 数据库
- 创建索引
- 启用行级安全
- 配置复制

## 备份和恢复

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U hermes hermes > backup.sql

# 恢复数据库
cat backup.sql | docker-compose exec -T postgres psql -U hermes -d hermes

# 备份向量数据库
cp -r hermes-qdrant-data ./backup/qdrant
```

## 下一步

- [ ] 配置 HTTPS/SSL
- [ ] 设置 Docker 容器日志驱动
- [ ] 配置监控告警（Prometheus + Grafana）
- [ ] 实施备份策略
- [ ] 配置自动扩展
