"""Central configuration for the Supervisor Agent's own two LLM calls
(routing + synthesis). Specialist delegation (specialists/*.py) does NOT
use this config -- each specialist adapter calls into its own already-built
project (revops/investigator), which loads its own independent Config from
its own project's .env, exactly as if it were an external service. This
project's own config only governs code genuinely new to project 12.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Config:
    gemini_api_key: str | None
    llm_provider: str = os.environ.get("LLM_PROVIDER", "gemini")
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
    ollama_model: str = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    runs_dir: Path = PROJECT_ROOT / "runs"

    max_retries: int = 5
    initial_backoff_seconds: float = 2.0
    ollama_timeout_seconds: float = 240.0


def load_config() -> Config:
    provider = os.environ.get("LLM_PROVIDER", "gemini")
    api_key = os.environ.get("GEMINI_API_KEY")
    if provider == "gemini" and not api_key:
        raise RuntimeError("GEMINI_API_KEY not set. Add it to .env in the project root.")
    return Config(gemini_api_key=api_key)
