#!/bin/bash

# Debugging utility for Hermes Platform

echo "Hermes Platform - Debug Utility"
echo "================================"
echo ""

echo "[1] Checking Docker containers..."
docker-compose ps

echo ""
echo "[2] Testing backend health..."
curl -s http://localhost:8001/health | python -m json.tool || echo "Backend unavailable"

echo ""
echo "[3] Testing database connection..."
docker-compose exec -T postgres psql -U hermes -d hermes -c "SELECT 1;" 2>/dev/null || echo "Database unavailable"

echo ""
echo "[4] Testing Ollama..."
curl -s http://localhost:11434/api/tags | python -m json.tool || echo "Ollama unavailable"

echo ""
echo "[5] Testing Qdrant..."
curl -s http://localhost:6333/health | python -m json.tool || echo "Qdrant unavailable"

echo ""
echo "[6] Testing Redis..."
docker-compose exec -T redis redis-cli ping 2>/dev/null || echo "Redis unavailable"

echo ""
echo "Debug complete!"
