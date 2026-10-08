import logging
import sys
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


class HealthCheck:
    """Health check for all platform services"""

    def __init__(self):
        self.services = {
            "backend": {"status": "unknown", "error": None},
            "postgres": {"status": "unknown", "error": None},
            "redis": {"status": "unknown", "error": None},
            "qdrant": {"status": "unknown", "error": None},
            "ollama": {"status": "unknown", "error": None},
        }

    async def check_postgres(self, postgres_url: str) -> bool:
        """Check PostgreSQL connection"""
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(postgres_url, echo=False, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.services["postgres"]["status"] = "healthy"
            logger.info("✓ PostgreSQL connected")
            return True
        except Exception as e:
            self.services["postgres"]["status"] = "unhealthy"
            self.services["postgres"]["error"] = str(e)
            logger.error(f"✗ PostgreSQL failed: {e}")
            return False

    async def check_redis(self, redis_url: str) -> bool:
        """Check Redis connection"""
        try:
            import redis
            r = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
            r.ping()
            self.services["redis"]["status"] = "healthy"
            logger.info("✓ Redis connected")
            return True
        except Exception as e:
            self.services["redis"]["status"] = "unhealthy"
            self.services["redis"]["error"] = str(e)
            logger.warning(f"✗ Redis unavailable: {e}")
            return False

    async def check_qdrant(self, qdrant_url: str) -> bool:
        """Check Qdrant connection"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=3) as client:
                resp = await client.get(f"{qdrant_url}/health")
                if resp.status_code == 200:
                    self.services["qdrant"]["status"] = "healthy"
                    logger.info("✓ Qdrant connected")
                    return True
        except Exception as e:
            self.services["qdrant"]["status"] = "unhealthy"
            self.services["qdrant"]["error"] = str(e)
            logger.warning(f"✗ Qdrant unavailable: {e}")
            return False

    async def check_ollama(self, ollama_url: str) -> bool:
        """Check Ollama connection"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=3) as client:
                resp = await client.get(f"{ollama_url}/api/tags")
                if resp.status_code == 200:
                    self.services["ollama"]["status"] = "healthy"
                    logger.info("✓ Ollama connected")
                    return True
        except Exception as e:
            self.services["ollama"]["status"] = "unhealthy"
            self.services["ollama"]["error"] = str(e)
            logger.warning(f"✗ Ollama unavailable: {e}")
            return False

    async def check_all(self, config) -> dict:
        """Check all services"""
        self.services["backend"]["status"] = "healthy"
        await asyncio.gather(
            self.check_postgres(config.postgres_url),
            self.check_redis(config.redis_url),
            self.check_qdrant(config.qdrant_url),
            self.check_ollama(config.ollama_base_url),
        )
        return self.services
