# Core modules for OmniSyntax: A Hybrid AI Code Tutor
from .auto_fix import AutoFixer
from .feature_utils import NUMERICAL_FEATURE_NAMES, extract_numerical_features
from .language_detector import detect_language
from .ml_engine import detect_error_ml
from .quality_analyzer import CodeQualityAnalyzer
from .static_pipeline import DetectionAnalysis, analyze_source, detect_all_errors_static, detect_errors_static
from .error_engine import detect_errors
from .multi_error_detector import detect_all_errors
from .syntax_checker import detect_all
from .tutor_explainer import explain_error

__all__ = [
    'AutoFixer',
    'CodeQualityAnalyzer',
    'DetectionAnalysis',
    'NUMERICAL_FEATURE_NAMES',
    'analyze_source',
    'detect_all',
    'detect_all_errors',
    'detect_all_errors_static',
    'detect_error_ml',
    'detect_errors',
    'detect_errors_static',
    'detect_language',
    'explain_error',
    'extract_numerical_features',
]
