"""
Shared Feature Utilities
========================
Single source of truth for numerical feature extraction.
Used by: ml_engine.py (inference), retrain_model.py (training).
"""

import re

NUMERICAL_FEATURE_NAMES = [
    'code_length', 'num_lines', 'has_division', 'has_type_conv',
    'missing_colon', 'missing_semicolon', 'compares_zero',
    'has_string_ops', 'has_type_decl', 'bracket_diff'
]

def extract_numerical_features(code: str) -> list:
    """
    Extract the 10 numerical features used by the ML model.
    Includes support for Python, Java, C, C++, and JavaScript.
    """
    lines = code.split('\n')

    return [
        len(code),
        len(lines),
        int('/' in code and '0' in code),
        int(bool(re.search(r'int\(|float\(|str\(|bool\(|Number\(|String\(', code))),
        int(':' not in code and bool(re.search(r'def |if |for |while |class |\{', code))),
        int(';' not in code and bool(re.search(r'printf|cout|System\.out|fprintf|console\.log', code))),
        int(bool(re.search(r'== 0|!= 0|=== 0|!== 0|/0|/ 0', code))),
        int(bool(re.search(r'\.upper\(\)|\.lower\(\)|\.split\(\)|\.join\(|\.strip\(\)|\.toUpperCase\(\)', code))),
        int(bool(re.search(r'\b(int|float|double|String|char|bool|let|const|var)\b', code))),
        code.count('(') - code.count(')'),
    ]
