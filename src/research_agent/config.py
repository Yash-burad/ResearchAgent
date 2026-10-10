from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    llm_provider: str = "ollama"
    default_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://localhost:11434"

    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    max_topics_discovered: int = 20
    max_topics_selected: int = 5
    max_sources_per_topic: int = 5
    request_timeout_seconds: int = 30

settings = Settings()
