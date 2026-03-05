"""
Multi-Error Detection Module
Detects ALL errors in code, not just the first one.

Reuses structural validators from error_engine to avoid code duplication.
"""

import ast as _ast

from .language_detector import detect_language
from .ml_engine import detect_error_ml, ModelUnavailableError, ModelInferenceError
from .syntax_checker import detect_all
from .tutor_explainer import explain_error
from .error_engine import _braces_balanced, _has_missing_semicolons, _has_unclosed_strings


def detect_all_errors(code: str, filename: str | None = None):
    """
    Detect ALL syntax errors in the code

    Returns:
        dict: {
            'language': str,
            'errors': list of error dicts,
            'total_errors': int,
            'has_errors': bool
        }
    """
    language = detect_language(code, filename)
    all_errors = []
    rule_based_issues = []
    is_valid_python = False

    # ------------------------------------------------
    # 1. Python: Use comprehensive rule-based detection
    # ------------------------------------------------
    if language == "Python":
        try:
            # Rubber Duck Comment: We first try to parse the code with Python's built-in AST parser.
            # If it succeeds, the code is syntactically valid in Python, so we skip rule checks 
            # to avoid false positives (e.g., regex matching a bracket inside a string).
            _ast.parse(code)
            is_valid_python = True
        except SyntaxError:
            # Rubber Duck Comment: If AST parsing fails, there is a true SyntaxError.
            # We then run our custom `detect_all` function which uses regex/lexical scanning
            # to identify the exact cause (missing semicolon, unclosed string, etc.)
            rule_based_issues = detect_all(code)

        if rule_based_issues:
            # Group errors by type
            error_types = {}
            for issue in rule_based_issues:
                error_type = issue.get('type', 'SyntaxError')
                if error_type not in error_types:
                    error_types[error_type] = {
                        'type': error_type,
                        'count': 0,
                        'locations': [],
                        'tutor': explain_error(error_type)
                    }
                error_types[error_type]['count'] += 1
                error_types[error_type]['locations'].append({
                    'line': issue.get('line'),
                    'message': issue.get('message'),
                    'suggestion': issue.get('suggestion'),
                    'snippet': issue.get('snippet'),
                })

            all_errors.extend(list(error_types.values()))

    # ------------------------------------------------
    # 2. Java / C / C++: Reuse error_engine validators
    # ------------------------------------------------
    if language in ["Java", "C", "C++"]:
        # Check for unclosed strings
        if _has_unclosed_strings(code):
            all_errors.append({
                'type': 'UnclosedString',
                'count': 1,
                'locations': [{'message': 'Unclosed string literal detected'}],
                'tutor': explain_error('UnclosedString')
            })

        # Check for missing semicolons — reuse error_engine function
        if _has_missing_semicolons(code):
            all_errors.append({
                'type': 'MissingDelimiter',
                'count': 1,
                'locations': [{'message': 'Missing semicolon detected'}],
                'tutor': explain_error('MissingDelimiter')
            })

        # Check for unmatched brackets — reuse error_engine function
        if not _braces_balanced(code):
            all_errors.append({
                'type': 'UnmatchedBracket',
                'count': 1,
                'locations': [{'message': 'Unmatched brackets detected'}],
                'tutor': explain_error('UnmatchedBracket')
            })

    # ------------------------------------------------
    # 3. ML-based detection (as additional check)
    # ------------------------------------------------
    if not is_valid_python:
        try:
            ml_error, confidence = detect_error_ml(code)
        except (ModelUnavailableError, ModelInferenceError):
            ml_error, confidence = ("NoError", 0.0)

        # Rubber Duck Comment: ML models can hallucinate, so we only trust the prediction 
        # if confidence is >= 0.65. Furthermore, to avoid duplicating errors the rule-based scanner 
        # already found, we only add it if the error type isn't already in `all_errors`.
        if ml_error != "NoError" and confidence >= 0.65:
            error_already_found = any(e['type'] == ml_error for e in all_errors)
            if not error_already_found:
                all_errors.append({
                    'type': ml_error,
                    'count': 1,
                    'locations': [{'confidence': confidence, 'ml_detected': True}],
                    'tutor': explain_error(ml_error)
                })

    # ------------------------------------------------
    # 4. Construct Final Output
    # ------------------------------------------------
    # Rubber Duck Comment: Finally, we aggregate all errors found.
    # We construct 'errors_by_type' for convenient frontend display.
    # We use `.get('line', 0)` and other defaults to prevent crashes if a checker forgot a field.
    return {
        'language': language,
        'errors': all_errors,
        'errors_by_type': {
            err['type']: [
                {
                    'line': loc.get('line', 0),
                    'message': loc.get('message', f"{err['type']} detected"),
                    'snippet': loc.get('snippet', '')
                }
                for loc in err.get('locations', [])
            ]
            for err in all_errors
        },
        'total_errors': sum(err['count'] for err in all_errors),
        'has_errors': len(all_errors) > 0,
        'rule_based_issues': rule_based_issues
    }
