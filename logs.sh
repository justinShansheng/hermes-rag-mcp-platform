#!/bin/bash

# View logs from all services
echo "Hermes Platform - Service Logs"
echo "================================="
echo ""
echo "Available services:"
echo "  - postgres"
echo "  - qdrant"
echo "  - redis"
echo "  - ollama"
echo "  - backend"
echo "  - frontend"
echo ""

if [ -z "$1" ]; then
    echo "Showing all logs (Ctrl+C to exit)..."
    docker-compose logs -f
else
    echo "Showing logs for: $1"
    docker-compose logs -f $1
fi
