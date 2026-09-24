from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IA Orquestrador"
    environment: str = "development"
    database_url: str = "sqlite:///./orchestrator.db"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"
    command_timeout_seconds: int = 120
    codex_timeout_seconds: int = 180
    codex_enabled: bool = True
    claude_timeout_seconds: int = 180
    health_cache_seconds: int = 30
    project_context_cache_seconds: int = 15
    allow_commands: bool = False
    alexa_enabled: bool = True
    alexa_require_verification: bool = False
    alexa_skill_id: str = ""
    alexa_max_response_length: int = 7500
    alexa_request_timeout: int = 8
    alexa_allowed_user_ids: str = ""
    alexa_rate_limit_per_minute: int = 30
    workspace: Path = Path.cwd()
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
