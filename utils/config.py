"""
Configuration helper that loads .env and provides controlled precedence
between process environment variables and .env values.
Default precedence: environment variables override .env.
Set PREFER_DOTENV=true to make .env override environment variables for this process.

Supports explicit .env path via DOTENV_PATH or DOTENV_FILE.
"""

from __future__ import annotations

import os
from typing import Optional
from dotenv import load_dotenv, dotenv_values, find_dotenv


def _resolve_dotenv_path() -> Optional[str]:
    # Allow explicit override via env
    explicit = os.getenv("DOTENV_PATH") or os.getenv("DOTENV_FILE")
    if explicit and os.path.exists(explicit):
        return explicit
    # Fallback to auto-discovery from current working directory
    path = find_dotenv()
    return path if path else None


_DOTENV_PATH = _resolve_dotenv_path()
_DOTENV_MAP = dotenv_values(_DOTENV_PATH) if _DOTENV_PATH else {}

# Load into process env without overriding existing env vars
load_dotenv(dotenv_path=_DOTENV_PATH, override=False)


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get configuration with precedence control.

    Precedence (default):
    - env var -> .env -> default

    If PREFER_DOTENV=true:
    - .env -> env var -> default
    """
    prefer_dotenv = os.getenv("PREFER_DOTENV", "false").lower() == "true"

    env_val = os.getenv(key)
    dotenv_val = _DOTENV_MAP.get(key)

    if prefer_dotenv:
        return dotenv_val if dotenv_val not in (None, "") else (env_val if env_val not in (None, "") else default)
    return env_val if env_val not in (None, "") else (dotenv_val if dotenv_val not in (None, "") else default)
