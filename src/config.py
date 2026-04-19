"""Unified runtime configuration for OmniSyntax."""

import os
from pathlib import Path


SUPPORTED_LANGUAGES = ["Python", "Java", "C", "C++", "JavaScript"]
SUPPORTED_FIX_ERROR_TYPES = [
    "MissingDelimiter",
    "MissingColon",
    "MissingSemicolon",
    "IndentationError",
    "UnmatchedBracket",
    "UnclosedQuotes",
    "UnclosedString",
    "MissingImport",
    "MissingInclude",
    "UnusedVariable",
    "UnreachableCode",
    "WildcardImport",
    "DuplicateDefinition",
    "InvalidAssignment",
    "InfiniteLoop",
    "TypeMismatch",
    "NameError",
    "UndeclaredIdentifier",
    "DivisionByZero",
    "MutableDefault",
    "LineTooLong",
]


def _get_bool_env(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_supported_languages() -> list[str]:
    return list(SUPPORTED_LANGUAGES)


def get_supported_fix_error_types() -> list[str]:
    return list(SUPPORTED_FIX_ERROR_TYPES)


def get_max_code_size() -> int:
    return int(os.getenv("MAX_CODE_SIZE", "100000"))


def get_rate_limit_per_minute() -> int:
    return int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))


def get_rate_limit_backend() -> str:
    return os.getenv("RATE_LIMIT_BACKEND", "memory").strip().lower() or "memory"


def is_rate_limit_backend_valid() -> tuple[bool, str | None]:
    backend = get_rate_limit_backend()
    if backend in {"memory", "redis"}:
        return True, None
    return False, "RATE_LIMIT_BACKEND must be one of: memory, redis"


def get_rate_limit_redis_url() -> str:
    return os.getenv("RATE_LIMIT_REDIS_URL", "").strip()


def get_rate_limit_key_header() -> str:
    return os.getenv("RATE_LIMIT_KEY_HEADER", "X-API-Key").strip() or "X-API-Key"


def get_api_version() -> str:
    return "1.2.0"


def get_cors_origins() -> str:
    return os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8501,http://localhost:8000",
    )


def get_models_dir() -> Path:
    return Path(__file__).parent.parent / "models"


def get_model_bundle_path() -> Path:
    return get_models_dir() / "bundle_metadata.json"


def is_production_mode() -> bool:
    return _get_bool_env("PRODUCTION", False)


def get_api_auth_mode() -> str:
    mode = os.getenv("API_AUTH_MODE", "api_key" if is_production_mode() else "disabled")
    return mode.strip().lower() or "disabled"


def get_api_keys() -> set[str]:
    raw = os.getenv("API_KEYS", "")
    return {token.strip() for token in raw.split(",") if token.strip()}


def get_api_key_header() -> str:
    return os.getenv("API_KEY_HEADER", "X-API-Key").strip() or "X-API-Key"


def allow_unsafe_public_api() -> bool:
    return _get_bool_env("ALLOW_UNSAFE_PUBLIC_API", False)


def is_api_docs_enabled() -> bool:
    default = not is_production_mode()
    return _get_bool_env("ENABLE_API_DOCS", default)


def get_api_host() -> str:
    return os.getenv("API_HOST", "0.0.0.0")


def get_api_port() -> int:
    return int(os.getenv("API_PORT", "8000"))


def get_api_reload() -> bool:
    return not is_production_mode()


def get_api_workers() -> int:
    return int(os.getenv("API_WORKERS", "4"))


def get_log_level() -> str:
    return os.getenv("LOG_LEVEL", "info")


def is_runtime_auth_config_valid() -> tuple[bool, str | None]:
    mode = get_api_auth_mode()
    if mode not in {"disabled", "api_key"}:
        return False, "API_AUTH_MODE must be one of: disabled, api_key"
    if mode == "api_key" and not get_api_keys():
        return False, "API_AUTH_MODE=api_key requires API_KEYS"
    if is_production_mode() and mode == "disabled" and not allow_unsafe_public_api():
        return False, "Production mode requires API auth unless ALLOW_UNSAFE_PUBLIC_API=true"
    return True, None


__all__ = [
    "SUPPORTED_LANGUAGES",
    "SUPPORTED_FIX_ERROR_TYPES",
    "get_supported_languages",
    "get_supported_fix_error_types",
    "get_max_code_size",
    "get_rate_limit_per_minute",
    "get_rate_limit_backend",
    "is_rate_limit_backend_valid",
    "get_rate_limit_redis_url",
    "get_rate_limit_key_header",
    "get_api_version",
    "get_cors_origins",
    "get_models_dir",
    "get_model_bundle_path",
    "is_production_mode",
    "get_api_auth_mode",
    "get_api_keys",
    "get_api_key_header",
    "allow_unsafe_public_api",
    "is_api_docs_enabled",
    "get_api_host",
    "get_api_port",
    "get_api_reload",
    "get_api_workers",
    "get_log_level",
    "is_runtime_auth_config_valid",
]

