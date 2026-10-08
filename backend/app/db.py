from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool
import logging

from app.config import settings
from app.models_db import Base

logger = logging.getLogger(__name__)

# Use NullPool to avoid connection pooling issues in Docker
engine = create_engine(
    settings.postgres_url,
    echo=False,
    poolclass=NullPool if settings.app_env == "production" else pool.QueuePool,
    pool_pre_ping=True,  # Test connections before using
    connect_args={"connect_timeout": 5} if "postgresql" in settings.postgres_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables and schema"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Run migrations
        db = SessionLocal()
        try:
            # Test connection
            db.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
