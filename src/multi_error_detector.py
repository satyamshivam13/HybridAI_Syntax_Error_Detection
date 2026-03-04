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

    # ------------------------------------------------
    # 1. Python: Use comprehensive rule-based detection
    # ------------------------------------------------
    if language == "Python":
        rule_based_issues = []
        try:
            # Avoid false positives from lexical scans when code is AST-valid.
            _ast.parse(code)
        except SyntaxError:
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

            all_errors = list(error_types.values())

        return {
            'language': language,
            'errors': all_errors,
            'errors_by_type': {
                err['type']: [
                    {
                        'line': loc['line'],
                        'message': loc['message'],
                        'snippet': loc.get('snippet', ''),
                    }
                    for loc in err['locations']
                ]
                for err in all_errors
            },
            'total_errors': sum(err['count'] for err in all_errors),
            'has_errors': len(all_errors) > 0,
            'rule_based_issues': rule_based_issues
        }

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
    try:
        ml_error, confidence = detect_error_ml(code)
    except (ModelUnavailableError, ModelInferenceError):
        ml_error, confidence = ("NoError", 0.0)

    # If ML detected an error not caught by rules, add it
    if ml_error != "NoError" and confidence >= 0.65:
        error_already_found = any(e['type'] == ml_error for e in all_errors)
        if not error_already_found:
            all_errors.append({
                'type': ml_error,
                'count': 1,
                'locations': [{'confidence': confidence, 'ml_detected': True}],
                'tutor': explain_error(ml_error)
            })

    return {
        'language': language,
        'errors': all_errors,
        'errors_by_type': {err['type']: [{'line': loc.get('line', 0), 'message': loc.get('message', f"{err['type']} detected"), 'snippet': loc.get('code', '')} for loc in err.get('locations', [])] for err in all_errors},
        'total_errors': sum(err['count'] for err in all_errors),
        'has_errors': len(all_errors) > 0,
        'rule_based_issues': []
    }


def detect_errors_multi(code: str, filename: str | None = None):
    """
    Wrapper for multi-error detection.
    Alias for detect_all_errors.
    """
    return detect_all_errors(code, filename)
