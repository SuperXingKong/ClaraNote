from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_OPENAI_MODEL = "gpt-5.4"
DEFAULT_OPENAI_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str = DEFAULT_OPENAI_MODEL
    openai_timeout_seconds: float = DEFAULT_OPENAI_TIMEOUT_SECONDS
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)


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
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        ),
    )
