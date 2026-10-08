from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "hermes-rag-mcp-platform"
    app_env: str = "production"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8001

    api_key: str = "demo-key"
    hermes_api_url: str = "http://localhost:8000"
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.1:8b"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    rag_vector_store: str = "faiss"
    rag_collection_name: str = "hermes_docs"

    sqlite_path: str = "./data/app.db"
    uploads_dir: str = "./data/uploads"
    qdrant_url: str = "http://localhost:6333"

    mcp_servers: dict = {
        "filesystem": {"enabled": True},
        "github": {"enabled": True},
        "web_search": {"enabled": True},
    }

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
