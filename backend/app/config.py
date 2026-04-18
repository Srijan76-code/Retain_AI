"""
Centralized LLM Factory
========================
Provides `get_llm()` to create LLM instances with automatic API key
rotation across Gemini providers.
"""

from __future__ import annotations

import os
import threading
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

# ── API Key Pools ────────────────────────────────────────────────────────

_GEMINI_KEYS: list[str] = [
    k for k in [
        os.getenv("GOOGLE_API_KEY_1") or os.getenv("GOOGLE_API_KEY"),
        os.getenv("GOOGLE_API_KEY_2"),
    ] if k
]

# ── Thread-safe round-robin counters ─────────────────────────────────────

_lock = threading.Lock()
_counters: dict[str, int] = {"gemini": 0}


def _next_key(provider: str) -> str:
    """Return the next API key for the given provider (round-robin)."""
    if provider != "gemini":
        return os.getenv("GROQ_API_KEY_1") # Fallback

    pool = _GEMINI_KEYS

    if not pool:
        raise ValueError(
            f"No API keys configured for provider '{provider}'. "
            f"Check your .env file."
        )

    with _lock:
        idx = _counters[provider] % len(pool)
        _counters[provider] += 1

    key = pool[idx]
    print(f"[LLM Factory] Using {provider} key slot {idx + 1}/{len(pool)}")
    return key


# ── Public API ───────────────────────────────────────────────────────────

def get_llm(
    provider: Literal["gemini", "groq"] = "gemini",
    model: str | None = None,
    temperature: float = 0.3,
    **kwargs,
):
    """
    Create an LLM instance with automatic key rotation for Gemini.
    For Groq, it uses default keys unless overridden.
    """
    api_key = _next_key(provider)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.0-flash",
            google_api_key=api_key,
            temperature=temperature,
            **kwargs,
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=model or "llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY_1"),
            temperature=temperature,
            **kwargs,
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")
