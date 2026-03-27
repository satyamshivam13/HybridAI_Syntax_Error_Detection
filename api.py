"""
REST API for OmniSyntax.
"""

import logging
import os
from collections import defaultdict, deque
from threading import Lock
from time import time
from typing import Any, Dict, List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from src.auto_fix import AutoFixer
from src.error_engine import detect_errors
from src.ml_engine import get_model_status
from src.quality_analyzer import CodeQualityAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration - read at runtime to support testing
_API_VERSION = "1.1.0"
_SUPPORTED_LANGUAGES = ["Python", "Java", "C", "C++", "JavaScript"]

_REQUEST_LOG: dict[tuple[str, str], deque[float]] = defaultdict(deque)
_REQUEST_LOCK = Lock()


def _get_max_code_size() -> int:
    """Get MAX_CODE_SIZE from config or environment."""
    return int(os.getenv("MAX_CODE_SIZE", "100000"))


def _get_rate_limit_per_minute() -> int:
    """Get rate limit from config or environment."""
    return int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))


def _get_cors_origins_str() -> str:
    """Get CORS_ORIGINS from config or environment."""
    return os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8501,http://localhost:8000",
    )


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


def _enforce_rate_limit(request: Request, scope: str) -> None:
    rate_limit = _get_rate_limit_per_minute()
    if rate_limit <= 0:
        return
    host = request.client.host if request.client else "unknown"
    key = (scope, host)
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


app = FastAPI(
    title="OmniSyntax API",
    description="AI-powered multi-language syntax error detection and auto-fix API",
    version=_API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
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
    language: Optional[str] = Field(
        None,
        description="Optional language override (Python, Java, C, C++, JavaScript)",
    )


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
    error_type: str = Field(..., description="Type of error to fix")
    language: Optional[str] = Field(None, description="Programming language")
    line_num: Optional[int] = Field(None, ge=0, description="Line number of error (0-indexed)")


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
    language: str = Field(..., description="Programming language (python, java, c, cpp, javascript)")


class ErrorResponse(BaseModel):
    language: str
    predicted_error: str
    confidence: float
    tutor: Dict[str, str]
    rule_based_issues: List[Dict[str, Any]]
    has_errors: bool
    degraded_mode: bool = False
    warnings: List[str] = Field(default_factory=list)


class AutoFixResponse(BaseModel):
    success: bool
    fixed_code: Optional[str]
    changes: List[str]
    error: Optional[str] = None


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


@app.get("/", tags=["Info"])
async def root():
    return {
        "message": "OmniSyntax API",
        "version": _API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    status = get_model_status()
    loaded = bool(status.get("loaded"))
    health_status = "healthy" if loaded else "degraded"
    degraded_reason = None if loaded else (status.get("error") or "ML model unavailable")
    return {
        "status": health_status,
        "version": _API_VERSION,
        "supported_languages": _SUPPORTED_LANGUAGES,
        "ml_model_loaded": loaded,
        "degraded_reason": degraded_reason,
        "max_code_size": _get_max_code_size(),
        "rate_limit_per_minute": _get_rate_limit_per_minute(),
    }


@app.post("/check", response_model=ErrorResponse, tags=["Error Detection"])
async def check_code(http_request: Request, request: CodeCheckRequest):
    _enforce_rate_limit(http_request, "check")
    _validate_code_payload(request.code)

    if request.language and request.language not in _SUPPORTED_LANGUAGES:
        _raise_api_error(
            400,
            "INVALID_LANGUAGE_OVERRIDE",
            f"Unsupported language override: {request.language}",
        )

    try:
        result = detect_errors(request.code, request.filename, request.language)
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
    _enforce_rate_limit(http_request, "fix")
    _validate_code_payload(request.code)

    try:
        fixer = AutoFixer()
        result = fixer.apply_fixes(
            request.code,
            request.error_type,
            request.line_num,
            request.language,
        )
        return AutoFixResponse(
            success=result["success"],
            fixed_code=result.get("fixed_code"),
            changes=result.get("changes", []),
            error=result.get("error"),
        )
    except HTTPException:
        raise
    except Exception:  # noqa: BLE001
        logger.exception("Unhandled exception in /fix")
        _raise_api_error(500, "INTERNAL_ERROR", "Unexpected error while fixing code")


@app.post("/quality", response_model=QualityResponse, tags=["Quality Analysis"])
async def analyze_quality(http_request: Request, request: QualityCheckRequest):
    _enforce_rate_limit(http_request, "quality")
    _validate_code_payload(request.code)

    try:
        analyzer = CodeQualityAnalyzer(request.code, request.language)
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


@app.post("/check-and-fix", tags=["Combined"])
async def check_and_fix(http_request: Request, request: CodeCheckRequest):
    _enforce_rate_limit(http_request, "check-and-fix")
    _validate_code_payload(request.code)
    if request.language and request.language not in _SUPPORTED_LANGUAGES:
        _raise_api_error(
            400,
            "INVALID_LANGUAGE_OVERRIDE",
            f"Unsupported language override: {request.language}",
        )

    try:
        error_result = detect_errors(request.code, request.filename, request.language)
        fix_result = None
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

        return {
            "error_detection": error_result,
            "auto_fix": fix_result,
            "has_errors": error_result["predicted_error"] != "NoError",
            "fix_available": bool(fix_result and fix_result.get("success", False)),
        }
    except HTTPException:
        raise
    except Exception:  # noqa: BLE001
        logger.exception("Unhandled exception in /check-and-fix")
        _raise_api_error(500, "INTERNAL_ERROR", "Unexpected error while processing request")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Starting OmniSyntax API")
    logger.info("=" * 80)
    logger.info("API documentation: http://localhost:8000/docs")
    logger.info("Interactive docs: http://localhost:8000/redoc")
    logger.info("Health check: http://localhost:8000/health")
    logger.info("=" * 80)
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=api_host, port=api_port, log_level="info")
