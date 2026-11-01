"""Runtime configuration.

Values come from environment variables, optionally loaded from ``backend/.env``.
They are read lazily (on every call) so tests can override them easily.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:  # python-dotenv is optional; plain environment variables still work
    pass


def openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY") or None


def openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def openai_base_url() -> str:
    """Any OpenAI-compatible endpoint works (OpenAI, Azure proxy, OpenRouter, Ollama...)."""
    return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")


def allowed_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def max_code_chars() -> int:
    try:
        return int(os.getenv("MAX_CODE_CHARS", "50000"))
    except ValueError:
        return 50000
