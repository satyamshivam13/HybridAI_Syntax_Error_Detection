# Core modules for Hybrid AI-Based Multi-Language Syntax Error Detection System
from .error_engine import detect_errors
from .language_detector import detect_language
from .ml_engine import detect_error_ml
from .syntax_checker import detect_all
from .tutor_explainer import explain_error
from .auto_fix import AutoFixer
from .quality_analyzer import CodeQualityAnalyzer

__all__ = [
    'detect_errors',
    'detect_language',
    'detect_error_ml',
    'detect_all',
    'explain_error',
    'AutoFixer',
    'CodeQualityAnalyzer'
]
