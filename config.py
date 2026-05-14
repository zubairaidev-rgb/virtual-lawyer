"""
Project configuration for AI pipelines and external services.

Loads ``.env`` / ``env`` from the repository root, then exposes typed constants
such as ``GROQ_API_KEY`` and ``PIPELINE_CONFIG`` consumed by modules under ``src/``.
Adjust behaviour via environment variables (documented in keys inside ``PIPELINE_CONFIG``).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

_PROJECT_ROOT = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    # Load `.env` first, then plain `env` (some setups use the latter filename).
    load_dotenv(_PROJECT_ROOT / ".env")
    load_dotenv(_PROJECT_ROOT / "env")
except ModuleNotFoundError:
    # If `python-dotenv` isn't installed yet, we can still rely on
    # environment variables set by the shell.
    pass

# Groq API key used by the 2-stage / 3-stage formatting pipelines.
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# Default pipeline settings (used if the config is available to the pipelines).
PIPELINE_CONFIG: Dict[str, Any] = {
    "formatter_type": "groq",
    # Groq decommissioned `llama-3.1-70b-versatile`. Use a supported model.
    "formatter_model": "llama-3.3-70b-versatile",
    # Local long-term mode:
    # - "extractive": retrieval-first deterministic composer (fast, stable, no paid API required)
    # - "model": use local TinyLlama generation (slower, less stable)
    "stage1_mode": os.getenv("STAGE1_MODE", "extractive"),
    "stage1": {
        "max_new_tokens": 120,
        "temperature": 0.2,
        "top_k": 3,
        "context_max_length": 1200,
    },
    "stage2": {
        "temperature": 0.2,
        "max_tokens": int(os.getenv("STAGE2_MAX_TOKENS", "420")),
        "top_p": 0.9,
    },
    "grounding_guard": {
        # Groq-based citation/section grounding check before final response.
        "enabled": os.getenv("ENABLE_GROQ_GROUNDING_GUARD", "true").lower() == "true",
        "max_tokens": int(os.getenv("GROQ_GROUNDING_GUARD_MAX_TOKENS", "420")),
        "temperature": float(os.getenv("GROQ_GROUNDING_GUARD_TEMPERATURE", "0.0")),
        "timeout_s": int(os.getenv("GROQ_GROUNDING_GUARD_TIMEOUT_S", "12")),
    },
    "formatter_routing": {
        # Always use Groq formatter by default (can still be overridden per deployment via env).
        "always_on": os.getenv("GROQ_ALWAYS_ON", "true").lower() == "true",
        # Hybrid mode fallback controls (used only when always_on is false).
        "auto_enabled": os.getenv("AUTO_GROQ", "true").lower() == "true",
        "min_sources_for_skip": int(os.getenv("AUTO_GROQ_MIN_SOURCES_FOR_SKIP", "2")),
        "long_question_words": int(os.getenv("AUTO_GROQ_LONG_QUESTION_WORDS", "22")),
    },
    "reasoner": {
        # On by default: adds Stage 1.5 reasoning over the extractive draft. Set ENABLE_LOCAL_REASONER=false to skip (faster, less VRAM).
        "enabled": os.getenv("ENABLE_LOCAL_REASONER", "true").lower() == "true",
        "model_name": os.getenv("LOCAL_REASONER_MODEL", "Qwen/Qwen2.5-3B-Instruct"),
        "max_new_tokens": int(os.getenv("LOCAL_REASONER_MAX_NEW_TOKENS", "320")),
        "temperature": float(os.getenv("LOCAL_REASONER_TEMPERATURE", "0.2")),
        "top_p": float(os.getenv("LOCAL_REASONER_TOP_P", "0.9")),
        # Groq reasoning stage (fast + accurate) before final formatter.
        "groq_enabled": os.getenv("ENABLE_GROQ_REASONER", "true").lower() == "true",
        "groq_model": os.getenv("GROQ_REASONER_MODEL", "llama-3.3-70b-versatile"),
        "groq_max_tokens": int(os.getenv("GROQ_REASONER_MAX_TOKENS", "220")),
        "groq_temperature": float(os.getenv("GROQ_REASONER_TEMPERATURE", "0.15")),
        "groq_timeout_s": int(os.getenv("GROQ_REASONER_TIMEOUT_S", "18")),
    },
}

