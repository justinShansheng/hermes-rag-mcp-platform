#!/usr/bin/env python
"""
Startup verification script for Hermes platform.
Verifies all services are running and correctly configured.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("startup_check")

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "app"))


async def verify_environment():
    """Verify environment variables"""
    logger.info("\n=== Environment Verification ===")
    required_vars = [
        "POSTGRES_URL",
        "OLLAMA_BASE_URL",
        "API_KEY",
    ]
    optional_vars = [
        "OPENROUTER_API_KEY",
        "REDIS_URL",
    ]

    for var in required_vars:
        val = os.getenv(var, "")
        status = "✓" if val else "✗"
        logger.info(f"{status} {var}: {val[:50] if val else 'NOT SET'}")
        if not val:
            logger.error(f"Missing required env var: {var}")
            return False

    for var in optional_vars:
        val = os.getenv(var, "")
        status = "✓" if val else "○"
        logger.info(f"{status} {var}: {val[:50] if val else 'optional'}")

    return True


async def verify_database():
    """Verify database connection and schema"""
    logger.info("\n=== Database Verification ===")
    try:
        from app.config import settings
        from app.db import init_db, get_db_context

        # Initialize database
        init_db()
        logger.info("✓ Database schema initialized")

        # Test connection
        with get_db_context() as db:
            from sqlalchemy import text
            result = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.scalar()
            logger.info(f"✓ Database has {table_count} tables")
        return True
    except Exception as e:
        logger.error(f"✗ Database verification failed: {e}")
        return False


async def verify_services():
    """Verify external services"""
    logger.info("\n=== Services Verification ===")
    try:
        from app.health_check import HealthCheck
        from app.config import settings

        health = HealthCheck()
        results = await health.check_all(settings)

        for service, status in results.items():
            state = status["status"]
            icon = "✓" if state == "healthy" else "✗"
            logger.info(f"{icon} {service}: {state}")
            if status["error"]:
                logger.debug(f"  Error: {status['error']}")

        # Return True if critical services are healthy
        critical = ["backend", "postgres"]
        return all(results[s]["status"] == "healthy" for s in critical)
    except Exception as e:
        logger.error(f"✗ Services verification failed: {e}")
        return False


async def verify_imports():
    """Verify all critical imports"""
    logger.info("\n=== Import Verification ===")
    imports = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("langchain", "LangChain"),
        ("sentence_transformers", "Sentence Transformers"),
        ("faiss", "FAISS"),
    ]

    for module, name in imports:
        try:
            __import__(module)
            logger.info(f"✓ {name}")
        except ImportError as e:
            logger.error(f"✗ {name}: {e}")
            return False
    return True


async def main():
    """Run all verification checks"""
    logger.info("\n" + "=" * 50)
    logger.info("Hermes Platform - Startup Verification")
    logger.info("=" * 50)

    checks = [
        ("Environment", verify_environment),
        ("Imports", verify_imports),
        ("Database", verify_database),
        ("Services", verify_services),
    ]

    results = {}
    for name, check_fn in checks:
        try:
            result = await check_fn()
            results[name] = result
            status = "PASS" if result else "FAIL"
            logger.info(f"\n{name}: {status}")
        except Exception as e:
            logger.error(f"\n{name}: ERROR - {e}")
            results[name] = False

    # Summary
    logger.info("\n" + "=" * 50)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    logger.info(f"Summary: {passed}/{total} checks passed")
    logger.info("=" * 50 + "\n")

    if passed == total:
        logger.info("✓ All checks passed! Platform is ready.")
        return 0
    else:
        logger.error("✗ Some checks failed. See errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
