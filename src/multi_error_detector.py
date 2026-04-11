"""
Multi-error detection for OmniSyntax.

Python keeps its AST-backed path. C-like languages reuse the richer rule engine
from error_engine so the UI can show multiple findings in degraded ML mode.
"""

import ast as _ast

from .error_engine import (
    SEMANTIC_ERROR_TYPES,
    _collect_c_like_rule_based_issues,
    _should_run_semantic_ml,
    _should_suppress_java_undeclared_identifier,
)
from .language_detector import detect_language
from .ml_engine import (
    ModelInferenceError,
    ModelUnavailableError,
    detect_error_ml,
    get_model_status,
    is_model_available,
)
from .syntax_checker import detect_all
from .tutor_explainer import explain_error


def _group_issues(issues: list[dict]) -> list[dict]:
    grouped = {}
    for issue in issues:
        error_type = issue.get("type", "SyntaxError")
        if error_type not in grouped:
            grouped[error_type] = {
                "type": error_type,
                "count": 0,
                "locations": [],
                "tutor": explain_error(error_type),
            }
        grouped[error_type]["count"] += 1
        grouped[error_type]["locations"].append({
            "line": issue.get("line"),
            "col": issue.get("col"),
            "message": issue.get("message"),
            "suggestion": issue.get("suggestion"),
            "snippet": issue.get("snippet"),
        })
    return list(grouped.values())


def detect_all_errors(code: str, filename: str | None = None):
    """
    Detect all observable issues in the given snippet.

    Returns:
        dict: {
            "language": str,
            "errors": list[dict],
            "total_errors": int,
            "has_errors": bool,
            "rule_based_issues": list[dict],
            "degraded_mode": bool,
            "warnings": list[str],
        }
    """
    language = detect_language(code, filename)
    all_errors = []
    rule_based_issues = []
    python_ast_valid = False
    warnings: list[str] = []

    degraded_mode = not is_model_available()
    if degraded_mode:
        status = get_model_status()
        warnings.append(
            f"ML model unavailable; falling back to rule-based checks only ({status.get('error', 'unknown reason')})"
        )

    if language == "Python":
        try:
            _ast.parse(code)
            python_ast_valid = True
        except SyntaxError:
            rule_based_issues = detect_all(code)

        if rule_based_issues:
            all_errors.extend(_group_issues(rule_based_issues))

        should_run_ml = _should_run_semantic_ml(code, language) or not python_ast_valid
        if should_run_ml:
            try:
                ml_error, confidence = detect_error_ml(code)
            except (ModelUnavailableError, ModelInferenceError):
                ml_error, confidence = ("NoError", 0.0)

            if python_ast_valid:
                if (
                    ml_error in SEMANTIC_ERROR_TYPES
                    and confidence >= 0.65
                    and not any(error["type"] == ml_error for error in all_errors)
                ):
                    all_errors.append({
                        "type": ml_error,
                        "count": 1,
                        "locations": [{"confidence": confidence, "ml_detected": True}],
                        "tutor": explain_error(ml_error),
                    })
            elif not rule_based_issues and ml_error != "NoError" and confidence >= 0.65:
                if not any(error["type"] == ml_error for error in all_errors):
                    all_errors.append({
                        "type": ml_error,
                        "count": 1,
                        "locations": [{"confidence": confidence, "ml_detected": True}],
                        "tutor": explain_error(ml_error),
                    })
            elif ml_error in SEMANTIC_ERROR_TYPES and confidence >= 0.65:
                if not any(error["type"] == ml_error for error in all_errors):
                    all_errors.append({
                        "type": ml_error,
                        "count": 1,
                        "locations": [{"confidence": confidence, "ml_detected": True}],
                        "tutor": explain_error(ml_error),
                    })

    if language in ["Java", "C", "C++", "JavaScript"]:
        rule_based_issues = _collect_c_like_rule_based_issues(code, language)
        if rule_based_issues:
            all_errors.extend(_group_issues(rule_based_issues))

        if _should_run_semantic_ml(code, language):
            try:
                ml_error, confidence = detect_error_ml(code)
            except (ModelUnavailableError, ModelInferenceError):
                ml_error, confidence = ("NoError", 0.0)

            if (
                ml_error in SEMANTIC_ERROR_TYPES
                and confidence >= 0.65
                and not any(error["type"] == ml_error for error in all_errors)
                and not _should_suppress_java_undeclared_identifier(rule_based_issues, ml_error)
            ):
                all_errors.append({
                    "type": ml_error,
                    "count": 1,
                    "locations": [{"confidence": confidence, "ml_detected": True}],
                    "tutor": explain_error(ml_error),
                })

    return {
        "language": language,
        "errors": all_errors,
        "errors_by_type": {
            error["type"]: [
                {
                    "line": location.get("line", 0),
                    "message": location.get("message", f"{error['type']} detected"),
                    "snippet": location.get("snippet", ""),
                }
                for location in error.get("locations", [])
            ]
            for error in all_errors
        },
        "total_errors": sum(error["count"] for error in all_errors),
        "has_errors": len(all_errors) > 0,
        "rule_based_issues": rule_based_issues,
        "degraded_mode": degraded_mode,
        "warnings": warnings,
    }
