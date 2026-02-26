"""
Shared Feature Utilities
========================
Single source of truth for numerical feature extraction.
Used by: ml_engine.py (inference), retrain_model.py (training).
"""

NUMERICAL_FEATURE_NAMES = [
    'code_length', 'num_lines', 'has_division', 'has_type_conv',
    'missing_colon', 'missing_semicolon', 'compares_zero',
    'has_string_ops', 'has_type_decl', 'bracket_diff'
]


def extract_numerical_features(code: str) -> list:
    """
    Extract the 10 numerical features used by the ML model.

    IMPORTANT: any changes here must be followed by retraining the model,
    since the model expects this exact feature vector.
    """
    lines = code.split('\n')

    return [
        len(code),                                                   # code_length
        len(lines),                                                  # num_lines
        int('/' in code and '0' in code),                           # has_division
        int(any(t in code for t in ['int(', 'float(', 'str(', 'bool('])),  # has_type_conv
        int(':' not in code and any(kw in code for kw in ['def ', 'if ', 'for ', 'while ', 'class '])),  # missing_colon
        int(';' not in code and any(kw in code for kw in ['printf', 'cout', 'System.out', 'fprintf'])),  # missing_semicolon
        int('== 0' in code or '!= 0' in code or '/0' in code or '/ 0' in code),  # compares_zero
        int(any(op in code for op in ['.upper()', '.lower()', '.split()', '.join(', '.strip()'])),  # has_string_ops
        int(any(t in code for t in ['int ', 'float ', 'double ', 'String ', 'char ', 'bool '])),  # has_type_decl
        code.count('(') - code.count(')'),                          # bracket_diff
    ]
