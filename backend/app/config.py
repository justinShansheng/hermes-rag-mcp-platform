from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Application
    app_name: str = "hermes-rag-mcp-platform"
    app_env: str = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8001

    # Security
    api_key: str = "demo-key"
    jwt_secret: str = "demo-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # External APIs
    hermes_api_url: str = "http://localhost:8000"
    ollama_base_url: str = "http://localhost:11434"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Models
    default_model: str = "llama3.1:8b"
    available_models: list = [
        "llama3.1:8b",
        "qwen2.5:7b",
        "deepseek-r1:7b",
        "openrouter/gpt-4o-mini",
        "openrouter/claude-3.5-sonnet",
    ]

    # RAG
    rag_vector_store: str = "faiss"
    rag_collection_name: str = "hermes_docs"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_search: int = 5

    # Storage
    sqlite_path: str = "./data/app.db"
    uploads_dir: str = "./data/uploads"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "hermes_docs"

    # Database
    postgres_url: str = "postgresql://hermes:hermes@localhost:5432/hermes"

    # Cache
    redis_url: str = "redis://localhost:6379/0"

    # MCP Servers
    mcp_servers: dict = {
        "filesystem": {"enabled": True},
        "github": {"enabled": True},
        "web_search": {"enabled": True},
    }

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


try:
    settings = Settings()
    logger.info(f"Settings loaded: {settings.app_name} ({settings.app_env})")
    logger.info(f"Database: {settings.postgres_url.split('@')[1] if '@' in settings.postgres_url else 'unknown'}")
    logger.info(f"Ollama: {settings.ollama_base_url}")
except Exception as e:
    logger.error(f"Failed to load settings: {e}")
    raise
