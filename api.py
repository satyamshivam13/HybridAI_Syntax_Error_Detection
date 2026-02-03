"""
REST API for Hybrid AI-Based Multi-Language Syntax Error Detection System
FastAPI-based API for integration with external tools and CI/CD pipelines
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


import uvicorn
from dotenv import load_dotenv
import os
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.error_engine import detect_errors
from src.auto_fix import AutoFixer
from src.quality_analyzer import CodeQualityAnalyzer


load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Language Syntax Error Detection API",
    description="AI-powered multi-language syntax error detection and auto-fix API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add SlowAPI rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class CodeCheckRequest(BaseModel):
    code: str = Field(..., description="Source code to check for errors")
    filename: Optional[str] = Field(None, description="Optional filename for language detection")
    language: Optional[str] = Field(None, description="Optional language override (Python, Java, C, C++)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "def test():\n    print('Hello')",
                "filename": "test.py"
            }
        }


class AutoFixRequest(BaseModel):
    code: str = Field(..., description="Source code to fix")
    error_type: str = Field(..., description="Type of error to fix")
    language: Optional[str] = Field(None, description="Programming language")
    line_num: Optional[int] = Field(None, description="Line number of error (0-indexed)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "def test()\n    pass",
                "error_type": "MissingColon",
                "language": "Python",
                "line_num": 0
            }
        }


class QualityCheckRequest(BaseModel):
    code: str = Field(..., description="Source code to analyze")
    language: str = Field(..., description="Programming language (python, java, c, cpp)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "def test():\n    pass",
                "language": "python"
            }
        }


class ErrorResponse(BaseModel):
    language: str
    predicted_error: str
    confidence: float
    tutor: Dict[str, str]
    rule_based_issues: List[Dict[str, Any]]
    has_errors: bool


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


# API Endpoints
@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Multi-Language Syntax Error Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    """Health check endpoint"""
    from src.ml_engine import model_loaded
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "supported_languages": ["Python", "Java", "C", "C++"],
        "ml_model_loaded": model_loaded
    }


@app.post("/check", response_model=ErrorResponse, tags=["Error Detection"])
@limiter.limit("100/minute")
async def check_code(request: CodeCheckRequest):
    # Input validation
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if len(request.code) > 100000:  # 100KB limit
        raise HTTPException(status_code=413, detail="Code too large")
    """
    Check code for syntax errors
    
    Detects syntax errors using ML + rule-based detection and provides:
    - Error type prediction
    - Confidence score
    - AI tutor explanations
    - Detailed rule-based issues
    """
    try:
        result = detect_errors(request.code, request.filename)
        
        return ErrorResponse(
            language=result["language"],
            predicted_error=result["predicted_error"],
            confidence=result["confidence"],
            tutor=result["tutor"],
            rule_based_issues=result.get("rule_based_issues", []),
            has_errors=result["predicted_error"] != "NoError"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing code: {str(e)}")


@app.post("/fix", response_model=AutoFixResponse, tags=["Auto-Fix"])
async def auto_fix(request: AutoFixRequest):
    """
    Automatically fix detected syntax errors
    
    Attempts to fix common syntax errors including:
    - Missing colons/semicolons
    - Indentation issues
    - Unmatched brackets
    - Unclosed strings
    - Missing imports/includes
    """
    try:
        fixer = AutoFixer()
        result = fixer.apply_fixes(
            request.code,
            request.error_type,
            request.line_num,
            request.language
        )
        
        return AutoFixResponse(
            success=result["success"],
            fixed_code=result.get("fixed_code"),
            changes=result.get("changes", []),
            error=result.get("error")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fixing code: {str(e)}")


@app.post("/quality", response_model=QualityResponse, tags=["Quality Analysis"])
async def analyze_quality(request: QualityCheckRequest):
    """
    Analyze code quality metrics
    
    Provides comprehensive quality analysis including:
    - Line counts (total, code, comments, blank)
    - Cyclomatic complexity
    - Comment ratio
    - Average line length
    - Quality score (0-100)
    - Improvement suggestions
    """
    try:
        analyzer = CodeQualityAnalyzer(request.code, request.language)
        result = analyzer.analyze()
        
        return QualityResponse(
            line_counts=result["line_counts"],
            complexity=result["complexity"],
            comment_ratio=result["comment_ratio"],
            avg_line_length=result["avg_line_length"],
            quality_score=result["quality_score"],
            suggestions=result["suggestions"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing quality: {str(e)}")


@app.post("/check-and-fix", tags=["Combined"])
async def check_and_fix(request: CodeCheckRequest):
    """
    Check code for errors and automatically suggest fixes
    
    Combined endpoint that:
    1. Detects errors
    2. Provides explanations
    3. Suggests auto-fixes if available
    """
    try:
        # Check for errors
        error_result = detect_errors(request.code, request.filename)
        
        # Attempt auto-fix if error detected
        fix_result = None
        if error_result["predicted_error"] != "NoError":
            fixer = AutoFixer()
            
            # Get line number from rule-based issues if available
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
                error_result["language"]
            )
        
        return {
            "error_detection": error_result,
            "auto_fix": fix_result,
            "has_errors": error_result["predicted_error"] != "NoError",
            "fix_available": fix_result is not None and fix_result.get("success", False)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


# Run the API
if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🚀 Starting Multi-Language Syntax Error Detection API")
    logger.info("=" * 80)
    logger.info("\n📡 API Documentation: http://localhost:8000/docs")
    logger.info("📊 Interactive Docs: http://localhost:8000/redoc")
    logger.info("🏥 Health Check: http://localhost:8000/health")
    logger.info("\n" + "=" * 80)
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(
        app,
        host=api_host,
        port=api_port,
        log_level="info"
    )
