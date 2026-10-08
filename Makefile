.PHONY: help install dev build up down logs clean deploy test

help:
	@echo "Hermes RAG MCP Platform - Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment (docker-compose)"
	@echo "  make down         - Stop development environment"
	@echo "  make logs         - Stream docker logs"
	@echo "  make build        - Build docker images"
	@echo ""
	@echo "Backend:"
	@echo "  make backend-install - Install Python dependencies"
	@echo "  make backend-run   - Run backend directly (requires PostgreSQL)"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-install - Install Node dependencies"
	@echo "  make frontend-dev  - Run frontend dev server"
	@echo ""
	@echo "Production:"
	@echo "  make prod-up      - Start production stack (docker-compose.prod.yml)"
	@echo "  make prod-down    - Stop production stack"
	@echo "  make deploy       - Deploy to production (requires docker, docker-compose)"


dev:
	docker-compose up -d
	@echo "✓ Development environment started"
	@echo "  Backend:  http://localhost:8001"
	@echo "  Frontend: http://localhost:5173"
	@echo "  Postgres: localhost:5432"
	@echo "  Qdrant:   http://localhost:6333"
	@echo "  Redis:    localhost:6379"
	@echo "  Ollama:   http://localhost:11434"

down:
	docker-compose down
	@echo "✓ Development environment stopped"

build:
	docker-compose build
	@echo "✓ Docker images built"

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf backend/.venv frontend/node_modules data/
	@echo "✓ Cleaned up"

backend-install:
	cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

@echo "✓ Backend dependencies installed"

backend-run:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

frontend-install:
	cd frontend && npm install
	@echo "✓ Frontend dependencies installed"

frontend-dev:
	cd frontend && npm run dev

prod-up:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✓ Production environment started"

prod-down:
	docker-compose -f docker-compose.prod.yml down
	@echo "✓ Production environment stopped"

deploy: build prod-down prod-up
	@echo "✓ Deployed to production"

test:
	@echo "Tests would run here"
