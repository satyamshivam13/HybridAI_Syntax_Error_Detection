"""REST API for OmniSyntax."""

import logging
from collections import defaultdict, deque
from enum import Enum
from threading import Lock
from time import time
from typing import Any, Dict, List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src import config
from src import static_pipeline
from src.auto_fix import AutoFixer
from src.ml_engine import get_model_status
from src.quality_analyzer import CodeQualityAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

_API_VERSION = config.get_api_version()
_SUPPORTED_LANGUAGES = config.get_supported_languages()
_SUPPORTED_FIX_TYPES = set(config.get_supported_fix_error_types())

_LANGUAGE_ALIASES = {
    "python": "Python",
    "java": "Java",
    "c": "C",
    "c++": "C++",
    "cpp": "C++",
    "javascript": "JavaScript",
    "js": "JavaScript",
}

_FIX_TYPE_ALIASES = {item.lower(): item for item in _SUPPORTED_FIX_TYPES}

_REQUEST_LOG: dict[tuple[str, str], deque[float]] = defaultdict(deque)
_REQUEST_LOCK = Lock()


def _get_max_code_size() -> int:
    return config.get_max_code_size()


def _get_rate_limit_per_minute() -> int:
    return config.get_rate_limit_per_minute()


def _get_cors_origins_str() -> str:
    return config.get_cors_origins()


def _parse_cors_origins() -> tuple[list[str], bool]:
    origins = [origin.strip() for origin in _get_cors_origins_str().split(",") if origin.strip()]
    if not origins:
        origins = ["http://localhost:3000"]
    has_wildcard = "*" in origins
    allow_credentials = not has_wildcard
    if has_wildcard:
        logger.warning(
            "CORS_ORIGINS includes '*' so allow_credentials is forced to False for browser safety."
        )
    return origins, allow_credentials


def _raise_api_error(status_code: int, error_code: str, message: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail={"error_code": error_code, "message": message},
    )


def _validate_code_payload(code: str, field_name: str = "code") -> None:
    max_size = _get_max_code_size()
    if not code or not code.strip():
        _raise_api_error(400, "EMPTY_CODE", f"{field_name} cannot be empty")
    if len(code) > max_size:
        _raise_api_error(
            413,
            "PAYLOAD_TOO_LARGE",
            f"{field_name} exceeds maximum allowed size ({max_size} characters)",
        )


def _normalize_language(value: Any) -> str:
    if value is None:
        return value
    if isinstance(value, LanguageEnum):
        return value.value
    key = str(value).strip().lower()
    if key in _LANGUAGE_ALIASES:
        return _LANGUAGE_ALIASES[key]
    raise ValueError(
        f"Unsupported language: {value}. Supported values: {', '.join(_SUPPORTED_LANGUAGES)}"
    )


def _normalize_fix_type(value: Any) -> str:
    if isinstance(value, AutoFixErrorType):
        return value.value
    key = str(value).strip().lower()
    if key in _FIX_TYPE_ALIASES:
        return _FIX_TYPE_ALIASES[key]
    supported = ", ".join(sorted(_SUPPORTED_FIX_TYPES))
    raise ValueError(f"Unsupported fix error_type: {value}. Supported values: {supported}")


class _BaseRateLimiter:
    backend = "memory"

    def is_ready(self) -> tuple[bool, str | None]:
        return True, None

    def enforce(self, request: Request, scope: str) -> None:
        raise NotImplementedError()


class _MemoryRateLimiter(_BaseRateLimiter):
    backend = "memory"
    _call_count = 0
    _EVICT_EVERY = 500  # run eviction every N calls

    def enforce(self, request: Request, scope: str) -> None:
        rate_limit = _get_rate_limit_per_minute()
        if rate_limit <= 0:
            return

        identity_header = config.get_rate_limit_key_header()
        identity = request.headers.get(identity_header)
        if not identity:
            identity = request.client.host if request.client else "unknown"

        key = (scope, identity)
        now = time()
        with _REQUEST_LOCK:
            events = _REQUEST_LOG[key]
            while events and (now - events[0]) > 60.0:
                events.popleft()
            if len(events) >= rate_limit:
                _raise_api_error(
                    429,
                    "RATE_LIMIT_EXCEEDED",
                    f"Too many requests. Limit is {rate_limit} per minute.",
                )
            events.append(now)

            # M3: Periodic eviction of stale keys to prevent memory leak
            _MemoryRateLimiter._call_count += 1
            if _MemoryRateLimiter._call_count >= _MemoryRateLimiter._EVICT_EVERY:
                _MemoryRateLimiter._call_count = 0
                stale = [k for k, v in _REQUEST_LOG.items() if not v or (now - v[-1]) > 120.0]
                for k in stale:
                    del _REQUEST_LOG[k]


class _RedisRateLimiter(_BaseRateLimiter):
    backend = "redis"

    def __init__(self):
        self._client = None
        self._init_error: str | None = None
        redis_url = config.get_rate_limit_redis_url()
        if not redis_url:
            self._init_error = "RATE_LIMIT_BACKEND=redis requires RATE_LIMIT_REDIS_URL"
            return
        try:
            import redis  # type: ignore

            self._client = redis.from_url(redis_url)
        except Exception as exc:  # noqa: BLE001
            self._init_error = f"Redis backend unavailable: {exc}"

    def is_ready(self) -> tuple[bool, str | None]:
        if self._client is None:
            return False, self._init_error or "Redis rate limit backend is unavailable"
        return True, None

    def enforce(self, request: Request, scope: str) -> None:
        rate_limit = _get_rate_limit_per_minute()
        if rate_limit <= 0:
            return

        ready, reason = self.is_ready()
        if not ready:
            _raise_api_error(503, "RATE_LIMIT_BACKEND_UNAVAILABLE", reason or "Rate limiter unavailable")

        assert self._client is not None
        identity_header = config.get_rate_limit_key_header()
        identity = request.headers.get(identity_header)
        if not identity:
            identity = request.client.host if request.client else "unknown"
        key = f"omnisyntax:rl:{scope}:{identity}"

        current = int(self._client.incr(key))  # type: ignore[arg-type]
        if current == 1:
            self._client.expire(key, 60)
        if current > rate_limit:
            _raise_api_error(
                429,
                "RATE_LIMIT_EXCEEDED",
                f"Too many requests. Limit is {rate_limit} per minute.",
            )


class _InvalidRateLimiter(_BaseRateLimiter):
    backend = "invalid"

    def __init__(self, reason: str):
        self._reason = reason

    def is_ready(self) -> tuple[bool, str | None]:
        return False, self._reason

    def enforce(self, request: Request, scope: str) -> None:
        _raise_api_error(503, "RATE_LIMIT_BACKEND_UNAVAILABLE", self._reason)


def _build_rate_limiter() -> _BaseRateLimiter:
    backend = config.get_rate_limit_backend()
    valid_backend, valid_reason = config.is_rate_limit_backend_valid()
    if not valid_backend:
        return _InvalidRateLimiter(valid_reason or "Invalid rate-limit backend")
    if backend == "redis":
        limiter = _RedisRateLimiter()
        ready, reason = limiter.is_ready()
        if not ready:
            logger.warning("Redis rate-limit backend not ready: %s", reason)
        return limiter
    return _MemoryRateLimiter()


_RATE_LIMITER = _build_rate_limiter()


def _enforce_rate_limit(request: Request, scope: str) -> None:
    _RATE_LIMITER.enforce(request, scope)


def _enforce_api_auth(request: Request) -> None:
    valid, reason = config.is_runtime_auth_config_valid()
    if not valid:
        _raise_api_error(503, "AUTH_CONFIG_ERROR", reason or "Invalid auth runtime configuration")

    mode = config.get_api_auth_mode()
    if mode == "disabled":
        return

    header_name = config.get_api_key_header()
    provided_key = request.headers.get(header_name)
    if not provided_key:
        _raise_api_error(401, "AUTH_REQUIRED", f"Missing required header: {header_name}")
    if provided_key not in config.get_api_keys():
        _raise_api_error(403, "AUTH_INVALID", "Invalid API key")


def _resolve_verification_status(original_error: str, result_error: str) -> str:
    if original_error == "NoError" and result_error != "NoError":
        return FixVerificationStatus.worsened.value
    if result_error == "NoError" and original_error != "NoError":
        return FixVerificationStatus.verified_removed.value
    if result_error != original_error and original_error != "NoError":
        return FixVerificationStatus.verified_improved.value
    if result_error == original_error:
        return FixVerificationStatus.unchanged.value
    return FixVerificationStatus.not_verified.value


def _verify_fix_result(
    *,
    original_code: str,
    fixed_code: str,
    language: str | None,
    filename: str | None,
    expected_original_error: str | None = None,
) -> "FixVerificationSummary":
    original_result = static_pipeline.analyze_source(original_code, filename, language).to_single_result()
    result_result = static_pipeline.analyze_source(fixed_code, filename, language).to_single_result()
    original_error = expected_original_error or original_result["predicted_error"]
    result_error = result_result["predicted_error"]
    status = _resolve_verification_status(original_error, result_error)
    verified = status in {
        FixVerificationStatus.verified_removed.value,
        FixVerificationStatus.verified_improved.value,
    }
    return FixVerificationSummary(
        verified=verified,
        status=status,
        original_error=original_error,
        result_error=result_error,
    )


app = FastAPI(
    title="OmniSyntax API",
    description="AI-powered multi-language syntax error detection and auto-fix API",
    version=_API_VERSION,
    docs_url="/docs" if config.is_api_docs_enabled() else None,
    redoc_url="/redoc" if config.is_api_docs_enabled() else None,
)

allowed_origins, allow_credentials = _parse_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeCheckRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "def test():\n    print('Hello')",
                "filename": "test.py",
                "language": "Python",
            }
        }
    )

    code: str = Field(..., description="Source code to check for errors")
    filename: Optional[str] = Field(None, description="Optional filename for language detection")
    language: Optional["LanguageEnum"] = Field(
        None,
        description="Optional language override (Python, Java, C, C++, JavaScript)",
    )

    @field_validator("language", mode="before")
    @classmethod
    def _validate_language(cls, value: Any) -> Any:
        return _normalize_language(value)


class AutoFixRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "def test()\n    pass",
                "error_type": "MissingColon",
                "language": "Python",
                "line_num": 0,
            }
        }
    )

    code: str = Field(..., description="Source code to fix")
    error_type: "AutoFixErrorType" = Field(..., description="Type of error to fix")
    language: Optional["LanguageEnum"] = Field(None, description="Programming language")
    line_num: Optional[int] = Field(None, ge=0, description="Line number of error (0-indexed)")

    @field_validator("language", mode="before")
    @classmethod
    def _validate_language(cls, value: Any) -> Any:
        return _normalize_language(value)

    @field_validator("error_type", mode="before")
    @classmethod
    def _validate_error_type(cls, value: Any) -> Any:
        return _normalize_fix_type(value)


class QualityCheckRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "def test():\n    pass",
                "language": "python",
            }
        }
    )

    code: str = Field(..., description="Source code to analyze")
    language: "LanguageEnum" = Field(..., description="Programming language")

    @field_validator("language", mode="before")
    @classmethod
    def _validate_language(cls, value: Any) -> Any:
        return _normalize_language(value)


class LanguageEnum(str, Enum):
    python = "Python"
    java = "Java"
    c = "C"
    cpp = "C++"
    javascript = "JavaScript"


class AutoFixErrorType(str, Enum):
    missing_delimiter = "MissingDelimiter"
    missing_colon = "MissingColon"
    missing_semicolon = "MissingSemicolon"
    indentation_error = "IndentationError"
    unmatched_bracket = "UnmatchedBracket"
    unclosed_quotes = "UnclosedQuotes"
    unclosed_string = "UnclosedString"
    missing_import = "MissingImport"
    missing_include = "MissingInclude"
    unused_variable = "UnusedVariable"
    unreachable_code = "UnreachableCode"
    wildcard_import = "WildcardImport"
    duplicate_definition = "DuplicateDefinition"
    invalid_assignment = "InvalidAssignment"
    infinite_loop = "InfiniteLoop"
    type_mismatch = "TypeMismatch"
    name_error = "NameError"
    undeclared_identifier = "UndeclaredIdentifier"
    division_by_zero = "DivisionByZero"
    mutable_default = "MutableDefault"
    line_too_long = "LineTooLong"


class FixVerificationStatus(str, Enum):
    verified_removed = "verified_removed"
    verified_improved = "verified_improved"
    unchanged = "unchanged"
    worsened = "worsened"
    not_verified = "not_verified"


class ErrorResponse(BaseModel):
    language: str
    predicted_error: str
    confidence: float
    tutor: Dict[str, str]
    rule_based_issues: List[Dict[str, Any]]
    has_errors: bool
    degraded_mode: bool = False
    warnings: List[str] = Field(default_factory=list)


class FixVerificationSummary(BaseModel):
    verified: bool
    status: str
    original_error: str
    result_error: str


class AutoFixResponse(BaseModel):
    success: bool
    generated: bool
    verified: bool
    fixed_code: Optional[str]
    changes: List[str]
    verification: Optional[FixVerificationSummary] = None
    error: Optional[str] = None


class CheckAndFixResponse(BaseModel):
    error_detection: ErrorResponse
    auto_fix: Optional[AutoFixResponse]
    has_errors: bool
    fix_available: bool


class QualityResponse(BaseModel):
    line_counts: Dict[str, int]
    complexity: int
    comment_ratio: float
    avg_line_length: float
    quality_score: float
    suggestions: List[str]


class HealthResponse(BaseModel):
    status: str
    version: str
    supported_languages: List[str]
    ml_model_loaded: bool
    degraded_reason: Optional[str] = None
    max_code_size: int
    rate_limit_per_minute: int
    auth_mode: str
    rate_limit_backend: str


class LivenessResponse(BaseModel):
    status: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    ready: bool
    reason: Optional[str] = None


class CapabilitiesResponse(BaseModel):
    status: str
    ml_model_loaded: bool
    degraded_mode: bool
    degraded_reason: Optional[str] = None
    auth_mode: str
    rate_limit_backend: str


@app.get("/", tags=["Info"])
async def root():
    docs_path = "/docs" if config.is_api_docs_enabled() else None
    return {
        "message": "OmniSyntax API",
        "version": _API_VERSION,
        "docs": docs_path,
        "health": "/health",
    }


@app.get("/health/live", response_model=LivenessResponse, tags=["Info"])
async def health_live():
    return {"status": "alive", "version": _API_VERSION}


@app.get("/health/ready", response_model=ReadinessResponse, tags=["Info"])
async def health_ready():
    auth_ok, auth_reason = config.is_runtime_auth_config_valid()
    backend_ok, backend_reason = config.is_rate_limit_backend_valid()
    limiter_ok, limiter_reason = _RATE_LIMITER.is_ready()
    if auth_ok and backend_ok and limiter_ok:
        return {"status": "ready", "ready": True, "reason": None}

    reasons = [reason for reason in [auth_reason, backend_reason, limiter_reason] if reason]
    return {
        "status": "not_ready",
        "ready": False,
        "reason": "; ".join(reasons) if reasons else "Runtime prerequisites missing",
    }


@app.get("/health/capabilities", response_model=CapabilitiesResponse, tags=["Info"])
async def health_capabilities():
    model_status = get_model_status()
    ml_loaded = bool(model_status.get("loaded"))
    degraded_reason = None if ml_loaded else (model_status.get("error") or "ML model unavailable")
    return {
        "status": "ok",
        "ml_model_loaded": ml_loaded,
        "degraded_mode": not ml_loaded,
        "degraded_reason": degraded_reason,
        "auth_mode": config.get_api_auth_mode(),
        "rate_limit_backend": config.get_rate_limit_backend(),
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    capabilities = await health_capabilities()
    readiness = await health_ready()
    loaded = capabilities["ml_model_loaded"]
    if not readiness["ready"]:
        health_status = "not_ready"
    elif loaded:
        health_status = "healthy"
    else:
        health_status = "degraded"
    return {
        "status": health_status,
        "version": _API_VERSION,
        "supported_languages": _SUPPORTED_LANGUAGES,
        "ml_model_loaded": loaded,
        "degraded_reason": capabilities["degraded_reason"],
        "max_code_size": _get_max_code_size(),
        "rate_limit_per_minute": _get_rate_limit_per_minute(),
        "auth_mode": config.get_api_auth_mode(),
        "rate_limit_backend": config.get_rate_limit_backend(),
    }


@app.post("/check", response_model=ErrorResponse, tags=["Error Detection"])
async def check_code(http_request: Request, request: CodeCheckRequest):
    _enforce_api_auth(http_request)
    _enforce_rate_limit(http_request, "check")
    _validate_code_payload(request.code)

    try:
        language = request.language.value if request.language else None
        result = static_pipeline.analyze_source(request.code, request.filename, language).to_single_result()
        return ErrorResponse(
            language=result["language"],
            predicted_error=result["predicted_error"],
            confidence=result["confidence"],
            tutor=result["tutor"],
            rule_based_issues=result.get("rule_based_issues", []),
            has_errors=result["predicted_error"] != "NoError",
            degraded_mode=result.get("degraded_mode", False),
            warnings=result.get("warnings", []),
        )
    except HTTPException:
        raise
    except Exception:  # noqa: BLE001
        logger.exception("Unhandled exception in /check")
        _raise_api_error(500, "INTERNAL_ERROR", "Unexpected error while checking code")


@app.post("/fix", response_model=AutoFixResponse, tags=["Auto-Fix"])
async def auto_fix(http_request: Request, request: AutoFixRequest):
    _enforce_api_auth(http_request)
    _enforce_rate_limit(http_request, "fix")
    _validate_code_payload(request.code)

    try:
        fixer = AutoFixer()
        language = request.language.value if request.language else None
        result = fixer.apply_fixes(
            request.code,
            request.error_type.value,
            request.line_num,
            language,
        )

        generated = bool(result.get("success", False))
        verification: Optional[FixVerificationSummary] = None
        success = False
        verified = False
        verification_error = None
        fixed_code = result.get("fixed_code")

        if generated and fixed_code is not None:
            try:
                verification = _verify_fix_result(
                    original_code=request.code,
                    fixed_code=fixed_code,
                    language=language,
                    filename=None,
                    expected_original_error=None,
                )
                verified = verification.verified
                success = verified
            except Exception as exc:  # noqa: BLE001
                verification_error = f"Fix verification failed: {exc}"
                verification = FixVerificationSummary(
                    verified=False,
                    status=FixVerificationStatus.not_verified.value,
                    original_error=request.error_type.value,
                    result_error=request.error_type.value,
                )

        error_message = result.get("error")
        if verification_error:
            error_message = (
                f"{error_message}; {verification_error}" if error_message else verification_error
            )

        return AutoFixResponse(
            success=success,
            generated=generated,
            verified=verified,
            fixed_code=fixed_code,
            changes=result.get("changes", []),
            verification=verification,
            error=error_message,
        )
    except HTTPException:
        raise
    except Exception:  # noqa: BLE001
        logger.exception("Unhandled exception in /fix")
        _raise_api_error(500, "INTERNAL_ERROR", "Unexpected error while fixing code")


@app.post("/quality", response_model=QualityResponse, tags=["Quality Analysis"])
async def analyze_quality(http_request: Request, request: QualityCheckRequest):
    _enforce_api_auth(http_request)
    _enforce_rate_limit(http_request, "quality")
    _validate_code_payload(request.code)

    try:
        analyzer = CodeQualityAnalyzer(request.code, request.language.value.lower())
        result = analyzer.analyze()
        return QualityResponse(
            line_counts=result["line_counts"],
            complexity=result["complexity"],
            comment_ratio=result["comment_ratio"],
            avg_line_length=result["avg_line_length"],
            quality_score=result["quality_score"],
            suggestions=result["suggestions"],
        )
    except HTTPException:
        raise
    except Exception:  # noqa: BLE001
        logger.exception("Unhandled exception in /quality")
        _raise_api_error(500, "INTERNAL_ERROR", "Unexpected error while analyzing quality")


@app.post("/check-and-fix", response_model=CheckAndFixResponse, tags=["Combined"])
async def check_and_fix(http_request: Request, request: CodeCheckRequest):
    _enforce_api_auth(http_request)
    _enforce_rate_limit(http_request, "check-and-fix")
    _validate_code_payload(request.code)

    try:
        language = request.language.value if request.language else None
        error_result = static_pipeline.analyze_source(request.code, request.filename, language).to_single_result()
        fix_response = None
        if error_result["predicted_error"] != "NoError":
            fixer = AutoFixer()
            line_num = None
            if error_result.get("rule_based_issues"):
                for issue in error_result["rule_based_issues"]:
                    if issue.get("line"):
                        line_num = issue["line"] - 1
                        break
            fix_result = fixer.apply_fixes(
                request.code,
                error_result["predicted_error"],
                line_num,
                error_result["language"],
            )
            generated = bool(fix_result.get("success", False))
            verified = False
            success = False
            verification = None
            verification_error = None

            fixed_code = fix_result.get("fixed_code")
            if generated and fixed_code is not None:
                try:
                    verification = _verify_fix_result(
                        original_code=request.code,
                        fixed_code=fixed_code,
                        language=error_result["language"],
                        filename=request.filename,
                        expected_original_error=error_result["predicted_error"],
                    )
                    verified = verification.verified
                    success = verified
                except Exception as exc:  # noqa: BLE001
                    verification_error = f"Fix verification failed: {exc}"
                    verification = FixVerificationSummary(
                        verified=False,
                        status=FixVerificationStatus.not_verified.value,
                        original_error=error_result["predicted_error"],
                        result_error=error_result["predicted_error"],
                    )

            error_message = fix_result.get("error")
            if verification_error:
                error_message = (
                    f"{error_message}; {verification_error}" if error_message else verification_error
                )

            fix_response = AutoFixResponse(
                success=success,
                generated=generated,
                verified=verified,
                fixed_code=fixed_code,
                changes=fix_result.get("changes", []),
                verification=verification,
                error=error_message,
            )

        response = CheckAndFixResponse(
            error_detection=ErrorResponse(
                language=error_result["language"],
                predicted_error=error_result["predicted_error"],
                confidence=error_result["confidence"],
                tutor=error_result["tutor"],
                rule_based_issues=error_result.get("rule_based_issues", []),
                has_errors=error_result["predicted_error"] != "NoError",
                degraded_mode=error_result.get("degraded_mode", False),
                warnings=error_result.get("warnings", []),
            ),
            auto_fix=fix_response,
            has_errors=error_result["predicted_error"] != "NoError",
            fix_available=bool(fix_response and fix_response.generated),
        )
        return response
    except HTTPException:
        raise
    except Exception:  # noqa: BLE001
        logger.exception("Unhandled exception in /check-and-fix")
        _raise_api_error(500, "INTERNAL_ERROR", "Unexpected error while processing request")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Starting OmniSyntax API")
    logger.info("=" * 80)
    if config.is_api_docs_enabled():
        logger.info("API documentation: http://localhost:8000/docs")
        logger.info("Interactive docs: http://localhost:8000/redoc")
    else:
        logger.info("API docs are disabled for this runtime")
    logger.info("Health check: http://localhost:8000/health")
    logger.info("=" * 80)
    api_host = config.get_api_host()
    api_port = config.get_api_port()
    uvicorn.run(app, host=api_host, port=api_port, log_level="info")
