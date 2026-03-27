"""
Unified configuration module for OmniSyntax.

Centralizes all configuration constants so they are maintained in one place
and can be consistently accessed across API, CLI, and Streamlit entry points.

Configuration values are read from environment variables at runtime to support
testing and dynamic configuration.
"""

import os
from pathlib import Path


def _get_supported_languages():
    """Get list of supported languages."""
    return ["Python", "Java", "C", "C++", "JavaScript"]


def _get_max_code_size():
    """Get maximum code size in bytes."""
    return int(os.getenv("MAX_CODE_SIZE", "100000"))


def _get_rate_limit_per_minute():
    """Get rate limit per minute (0 = disabled)."""
    return int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))


def _get_api_version():
    """Get API version."""
    return "1.1.0"


def _get_cors_origins():
    """Get CORS origins configuration."""
    return os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8501,http://localhost:8000",
    )


def _get_models_dir():
    """Get models directory path."""
    return Path(__file__).parent.parent / "models"


def _get_model_bundle_path():
    """Get model bundle metadata path."""
    return _get_models_dir() / "bundle_metadata.json"


def _get_production_mode():
    """Check if running in production mode."""
    return os.getenv("PRODUCTION", "false").lower() == "true"


def _get_api_host():
    """Get API host."""
    return os.getenv("API_HOST", "0.0.0.0")


def _get_api_port():
    """Get API port."""
    return int(os.getenv("API_PORT", "8000"))


def _get_api_reload():
    """Get API reload setting."""
    return not _get_production_mode()


def _get_api_workers():
    """Get number of API workers."""
    return int(os.getenv("API_WORKERS", "4"))


def _get_log_level():
    """Get log level."""
    return os.getenv("LOG_LEVEL", "info")


# Public properties using lazy evaluation
SUPPORTED_LANGUAGES = _get_supported_languages()
MAX_CODE_SIZE = _get_max_code_size()
RATE_LIMIT_PER_MINUTE = _get_rate_limit_per_minute()
API_VERSION = _get_api_version()
CORS_ORIGINS = _get_cors_origins()
MODELS_DIR = _get_models_dir()
MODEL_BUNDLE_PATH = _get_model_bundle_path()
PRODUCTION_MODE = _get_production_mode()
API_HOST = _get_api_host()
API_PORT = _get_api_port()
API_RELOAD = _get_api_reload()
API_WORKERS = _get_api_workers()
LOG_LEVEL = _get_log_level()

__all__ = [
    "SUPPORTED_LANGUAGES",
    "MAX_CODE_SIZE",
    "RATE_LIMIT_PER_MINUTE",
    "API_VERSION",
    "CORS_ORIGINS",
    "MODELS_DIR",
    "MODEL_BUNDLE_PATH",
    "PRODUCTION_MODE",
    "API_HOST",
    "API_PORT",
    "API_RELOAD",
    "API_WORKERS",
    "LOG_LEVEL",
]

