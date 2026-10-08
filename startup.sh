#!/bin/bash

# Hermes Platform - Startup Script
# Usage: ./startup.sh [dev|prod]

set -e

ENV=${1:-dev}
echo "Starting Hermes Platform in $ENV mode..."

if [ "$ENV" = "dev" ]; then
    echo "\n[1/4] Running startup verification..."
    cd backend
    python startup_check.py
    cd ..
    
    echo "\n[2/4] Starting development stack..."
    docker-compose up -d
    
    echo "\n[3/4] Waiting for services to be ready..."
    sleep 10
    
    echo "\n[4/4] Services started!"
    echo "\n📋 Access points:"
    echo "  Frontend:  http://localhost:5173"
    echo "  Backend:   http://localhost:8001"
    echo "  API Docs:  http://localhost:8001/docs"
    echo "  Qdrant:    http://localhost:6333"
    echo "  Ollama:    http://localhost:11434"
    echo "  Postgres:  localhost:5432"
    echo "  Redis:     localhost:6379"
    echo ""
    
elif [ "$ENV" = "prod" ]; then
    echo "\n[1/2] Building production images..."
    docker-compose -f docker-compose.prod.yml build
    
    echo "\n[2/2] Starting production stack..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "\n✓ Production stack started!"
    echo "  Frontend:  http://localhost:5173"
    echo "  Backend:   http://localhost:8001"
    echo ""
else
    echo "Invalid environment: $ENV"
    echo "Usage: ./startup.sh [dev|prod]"
    exit 1
fi
