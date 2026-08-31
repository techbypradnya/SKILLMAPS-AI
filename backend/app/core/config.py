from __future__ import annotations

import os

from dotenv import load_dotenv

# Load .env here so settings are correct regardless of import order
load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.APP_NAME: str = "SkillGraph AI"
        self.ENV: str = os.getenv("ENV", "development")
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")

        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./skillgraph.db")

        self.VECTOR_BACKEND: str = os.getenv("VECTOR_BACKEND", "none")

        self.ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY") or None
        self.OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY") or None
        self.LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")
        self.LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

        self.CORS_ORIGINS: list[str] = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
        ).split(",")

    @property
    def llm_available(self) -> bool:
        if self.LLM_PROVIDER == "none":
            return False
        return bool(self.ANTHROPIC_API_KEY or self.OPENAI_API_KEY)


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
