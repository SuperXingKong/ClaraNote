from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_OPENAI_MODEL = "gpt-5.4"
DEFAULT_OPENAI_TIMEOUT_SECONDS = 30.0
DEFAULT_LLM_PROVIDER = "mock"
DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str = DEFAULT_OPENAI_MODEL
    openai_timeout_seconds: float = DEFAULT_OPENAI_TIMEOUT_SECONDS
    llm_provider: str = DEFAULT_LLM_PROVIDER
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS


def get_settings() -> Settings:
    timeout_raw = os.getenv("OPENAI_TIMEOUT_SECONDS")
    timeout = DEFAULT_OPENAI_TIMEOUT_SECONDS
    if timeout_raw:
        try:
            timeout = float(timeout_raw)
        except ValueError:
            timeout = DEFAULT_OPENAI_TIMEOUT_SECONDS

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        openai_timeout_seconds=timeout,
        llm_provider=os.getenv("LLM_PROVIDER", DEFAULT_LLM_PROVIDER).strip().lower(),
        cors_origins=parse_cors_origins(os.getenv("CORS_ORIGINS")),
    )


def parse_cors_origins(raw_value: str | None) -> tuple[str, ...]:
    if not raw_value:
        return DEFAULT_CORS_ORIGINS
    return tuple(origin.strip() for origin in raw_value.split(",") if origin.strip())
