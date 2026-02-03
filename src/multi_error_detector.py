"""
Multi-Error Detection Module
Detects ALL errors in code, not just the first one
"""

from .language_detector import detect_language
from .ml_engine import detect_error_ml
from .syntax_checker import detect_all
from .tutor_explainer import explain_error


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
                    'suggestion': issue.get('suggestion')
                })
            
            all_errors = list(error_types.values())
        
        return {
            'language': language,
            'errors': all_errors,
            'errors_by_type': {err['type']: [{'line': loc['line'], 'message': loc['message'], 'snippet': loc.get('suggestion', '')} for loc in err['locations']] for err in all_errors},
            'total_errors': sum(err['count'] for err in all_errors),
            'has_errors': len(all_errors) > 0,
            'rule_based_issues': rule_based_issues
        }
    
    # ------------------------------------------------
    # 2. Java / C / C++: Check multiple error types
    # ------------------------------------------------
    if language in ["Java", "C", "C++"]:
        lines = [l.strip() for l in code.splitlines() if l.strip()]
        
        # Check for missing semicolons
        missing_semicolons = []
        for i, l in enumerate(lines, 1):
            # Skip comments, preprocessor directives, and control structures
            if (l.startswith('//') or l.startswith('/*') or l.startswith('*') or 
                l.startswith('#') or l.endswith('{') or l.endswith('}') or
                l.startswith('import') or l.startswith('package') or
                l.startswith('using') or l.startswith('namespace')):
                continue
            
            is_control = any(keyword in l for keyword in [
                'if (', 'for (', 'while (', 'else', 'try', 'catch', 
                'switch (', 'case ', 'default:', 'do '
            ])
            
            if not is_control and not l.endswith(';') and not l.endswith('{') and not l.endswith('}'):
                if '=' in l or '(' in l:
                    missing_semicolons.append({'line': i, 'code': l})
        
        if missing_semicolons:
            all_errors.append({
                'type': 'MissingDelimiter',
                'count': len(missing_semicolons),
                'locations': missing_semicolons,
                'tutor': explain_error('MissingDelimiter')
            })
        
        # Check for unmatched brackets
        bracket_count = {'(': 0, '[': 0, '{': 0}
        for char in code:
            if char in bracket_count:
                bracket_count[char] += 1
            elif char == ')':
                bracket_count['('] -= 1
            elif char == ']':
                bracket_count['['] -= 1
            elif char == '}':
                bracket_count['{'] -= 1
        
        unmatched = [k for k, v in bracket_count.items() if v != 0]
        if unmatched:
            all_errors.append({
                'type': 'UnmatchedBracket',
                'count': sum(abs(v) for v in bracket_count.values()),
                'locations': [{'bracket': k, 'difference': v} for k, v in bracket_count.items() if v != 0],
                'tutor': explain_error('UnmatchedBracket')
            })
        
        # Check for unclosed strings
        single_quotes = code.count("'")
        double_quotes = code.count('"')
        if single_quotes % 2 != 0 or double_quotes % 2 != 0:
            all_errors.append({
                'type': 'UnclosedString',
                'count': 1,
                'locations': [{'single_quotes': single_quotes, 'double_quotes': double_quotes}],
                'tutor': explain_error('UnclosedString')
            })
    
    # ------------------------------------------------
    # 3. ML-based detection (as additional check)
    # ------------------------------------------------
    ml_error, confidence = detect_error_ml(code)
    
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
        'errors_by_type': {err['type']: [{'line': loc.get('line', 0), 'message': f"{err['type']} detected", 'snippet': loc.get('code', '')} for loc in err.get('locations', [])] for err in all_errors},
        'total_errors': sum(err['count'] for err in all_errors),
        'has_errors': len(all_errors) > 0,
        'rule_based_issues': []
    }


# Add to error_engine.py
def detect_errors_multi(code: str, filename: str | None = None):
    """
    Wrapper for multi-error detection
    Alias for detect_all_errors
    """
    return detect_all_errors(code, filename)
