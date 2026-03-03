"""
error_engine.py
===============
Hybrid rule-based + ML error detection engine.

Two-layer design:
  Layer 1 — Structural validator (is there an error at all?)
    • Python:       ast.parse()  — perfect syntax validator
    • Java/C/C++:   brace balance + semicolon check

  Layer 2 — ML classifier (what kind of error is it?)
    • Only consulted when Layer 1 finds a problem, OR
    • After Layer 1 passes, to catch SEMANTIC errors (DivisionByZero,
      TypeMismatch, ImportError, etc.) which are syntactically valid.

Key insight:
  Semantic error types (DivisionByZero, TypeMismatch, ...) are in
  syntactically valid code — ast.parse() passes them. After a structural
  pass, ML is consulted at a high confidence threshold, but ONLY for
  semantic error types. Syntax error types (MissingColon, etc.) are
  NEVER reported when the structural validator passes — they would be
  false positives.
"""

import ast as _ast
import re

from .language_detector import detect_language
from .ml_engine import detect_error_ml
from .syntax_checker import detect_all
from .tutor_explainer import explain_error

# Confidence thresholds
SYNTAX_ERROR_THRESHOLD   = 0.65   # ML classifying a known syntax error
SEMANTIC_ERROR_THRESHOLD = 0.85   # ML classifying a semantic/runtime error
SHORT_CODE_SEMANTIC_THRESHOLD = 0.85  # Stricter bar for very short snippets
MIN_CODE_LINES_FOR_SEMANTIC = 4        # Below this, use SHORT_CODE_SEMANTIC_THRESHOLD

# Per-type minimum confidence for semantic errors (reduce false positives)
SEMANTIC_ERROR_THRESHOLDS = {
    "DivisionByZero": 0.85,
    "ImportError": 0.85,
    "InfiniteLoop": 0.85,
    "UnreachableCode": 0.85,
    "InvalidAssignment": 0.85,
    "DuplicateDefinition": 0.85,
    "NameError": 0.85,
    "UndeclaredIdentifier": 0.85,
    "TypeMismatch": 0.85,
    "MissingImport": 0.85,
    "MissingInclude": 0.85,
    "LineTooLong": 0.85,
    "WildcardImport": 0.85,
    "MutableDefault": 0.85,
    "UnusedVariable": 0.85,
}

# Rule-based types that are always authoritative
RULE_BASED_AUTHORITATIVE = {"MissingColon", "MissingDelimiter", "IndentationError"}

# All types the rule-based detector covers
RULE_BASED_TYPES = {
    "MissingColon", "IndentationError", "UnmatchedBracket",
    "UnclosedQuotes", "UnclosedString", "MissingDelimiter",
}

# Semantic/runtime error types — syntactically valid code can have these.
# After AST/structural pass, ML is consulted for these types only.
SEMANTIC_ERROR_TYPES = {
    "DivisionByZero", "TypeMismatch", "ImportError", "MissingImport",
    "MissingInclude", "InfiniteLoop", "InvalidAssignment", "LineTooLong",
    "DuplicateDefinition", "MutableDefault", "NameError",
    "UndeclaredIdentifier", "UnreachableCode", "UnusedVariable",
    "WildcardImport",
}

LABEL_ALIASES = {
    "UnclosedQuotes": "UnclosedString",
    # Dataset/model label uses MissingDelimiter for Python missing ':' as well.
    "MissingColon": "MissingDelimiter",
}

def _normalize(label):
    return LABEL_ALIASES.get(label, label)

def _braces_balanced(code):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in code:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return len(stack) == 0

def _semantic_heuristic_ok(error_type: str, code: str, language: str) -> bool:
    """Light heuristics to avoid obvious semantic false positives.
    (Currently bypassed to trust the high-accuracy ML model)."""
    return True

def _has_missing_semicolons(code):
    import re
    simple_statements = [
        r'^return\s+.+$', r'^cout\s*<<.*$', r'^cin\s*>>.*$',
        r'^printf\s*\(.*\)$', r'^fprintf\s*\(.*\)$', r'^puts\s*\(.*\)$',
        r'^std::cout\s*<<.*$', r'^std::cin\s*>>.*$',
    ]
    for l in [l.strip() for l in code.splitlines() if l.strip()]:
        if (l.startswith('//') or l.startswith('/*') or l.startswith('*') or
            l.startswith('#') or l.endswith('{') or l.endswith('}') or
            l.startswith('import') or l.startswith('package') or
            l.startswith('using') or l.startswith('namespace') or
            'class ' in l[:20]):
            continue
        is_control = any(kw in l for kw in [
            'if (', 'if(', 'for (', 'for(', 'while (', 'while(',
            'else', 'try', 'catch', 'switch', 'case ', 'default:', 'do '
        ])
        if not is_control and not l.endswith(';') and not l.endswith('{') and not l.endswith('}'):
            if any(re.match(pat, l) for pat in simple_statements):
                return True
            elif ('=' in l or ('(' in l and ')' in l)) and not l.startswith('}'):
                return True
    return False

def _ml_semantic_check(code, language, rule_based_issues):
    """
    After a structural pass, ask ML if there's a semantic/runtime error.
    Only returns an error if ML is highly confident AND the type is semantic.
    Short snippets require a stricter confidence threshold.
    Returns a result dict or None if no semantic error found.
    """
    code_lines = len([l for l in code.splitlines() if l.strip()])
    min_conf = (SHORT_CODE_SEMANTIC_THRESHOLD
                if code_lines < MIN_CODE_LINES_FOR_SEMANTIC
                else SEMANTIC_ERROR_THRESHOLD)
    
    ml_error, confidence = detect_error_ml(code)
    ml_error = _normalize(ml_error)
    per_type = SEMANTIC_ERROR_THRESHOLDS.get(ml_error, 0.0)
    min_conf = max(min_conf, per_type)

    if (ml_error in SEMANTIC_ERROR_TYPES
            and confidence >= min_conf
            and _semantic_heuristic_ok(ml_error, code, language)):
        return {
            "language": language,
            "predicted_error": ml_error,
            "confidence": confidence,
            "tutor": explain_error(ml_error),
            "rule_based_issues": rule_based_issues
        }
    return None


def detect_errors(code: str, filename: str | None = None):
    """
    Detect syntax and semantic errors using a hybrid approach.
    """

    language = detect_language(code, filename)
    rule_based_issues = []

    # =========================================================================
    # PYTHON
    # =========================================================================
    if language == "Python":

        # Layer 1: AST structural validation
        try:
            _ast.parse(code)
            ast_passed = True
        except SyntaxError:
            ast_passed = False
        if not ast_passed and "\\n" in code and "\n" not in code:
            # Handle datasets or inputs that store literal "\n" sequences.
            normalized = code.replace("\\n", "\n")
            try:
                _ast.parse(normalized)
                code = normalized
                ast_passed = True
            except SyntaxError:
                pass

        if ast_passed:
            # Code is syntactically valid Python.
            # Still check for semantic/runtime errors via ML.
            semantic = _ml_semantic_check(code, language, [])
            if semantic:
                return semantic
            # No semantic error detected either
            return {
                "language": language,
                "predicted_error": "NoError",
                "confidence": 1.0,
                "tutor": {
                    "why": "The Python code follows correct syntax rules.",
                    "fix": "No changes are required."
                },
                "rule_based_issues": []
            }

        # AST failed — classify the syntax error
        rule_based_issues = detect_all(code)
        for issue in rule_based_issues:
            if issue.get("type") in LABEL_ALIASES:
                issue["type"] = LABEL_ALIASES[issue["type"]]

        strong_issues = [i for i in rule_based_issues if i.get("type") in RULE_BASED_TYPES]

        if strong_issues:
            rb_error = strong_issues[0].get("type", "SyntaxError")

            # Authoritative types never overridden by ML
            if rb_error in RULE_BASED_AUTHORITATIVE:
                return {
                    "language": language,
                    "predicted_error": rb_error,
                    "confidence": 1.0,
                    "tutor": explain_error(rb_error),
                    "rule_based_issues": rule_based_issues
                }

            # Other rule-based types — ML can override if very confident
            ml_error, confidence = detect_error_ml(code)
            ml_error = _normalize(ml_error)
            code_lines = len([l for l in code.splitlines() if l.strip()])
            min_conf = (SHORT_CODE_SEMANTIC_THRESHOLD
                        if code_lines < MIN_CODE_LINES_FOR_SEMANTIC
                        else SEMANTIC_ERROR_THRESHOLD)
            per_type = SEMANTIC_ERROR_THRESHOLDS.get(ml_error, 0.0)
            min_conf = max(min_conf, per_type)
            # Only allow ML override for semantic errors with very high confidence
            if (ml_error in SEMANTIC_ERROR_TYPES
                    and confidence >= min_conf
                    and ml_error != "NoError"
                    and ml_error != rb_error
                    and _semantic_heuristic_ok(ml_error, code, language)):
                return {
                    "language": language,
                    "predicted_error": ml_error,
                    "confidence": confidence,
                    "tutor": explain_error(ml_error),
                    "rule_based_issues": rule_based_issues
                }

            return {
                "language": language,
                "predicted_error": rb_error,
                "confidence": 1.0,
                "tutor": explain_error(rb_error),
                "rule_based_issues": rule_based_issues
            }

        # Rule-based didn't classify → use ML for syntax error classification
        ml_error, confidence = detect_error_ml(code)
        ml_error = _normalize(ml_error)
        if confidence < SYNTAX_ERROR_THRESHOLD or ml_error == "NoError":
            return {
                "language": language,
                "predicted_error": "NoError",
                "confidence": confidence,
                "tutor": {
                    "why": "The code structure appears syntactically correct.",
                    "fix": "No changes are required."
                },
                "rule_based_issues": rule_based_issues
            }
        return {
            "language": language,
            "predicted_error": ml_error,
            "confidence": confidence,
            "tutor": explain_error(ml_error),
            "rule_based_issues": rule_based_issues
        }

    # =========================================================================
    # JAVA / C / C++
    # =========================================================================
    elif language in ["Java", "C", "C++"]:

        # Check for unclosed strings first (higher priority than other errors)
        in_single = False
        in_double = False
        escaped = False
        
        for char in code:
            if escaped:
                escaped = False
                continue
            if char == '\\':
                escaped = True
                continue
            if char == "'" and not in_double:
                in_single = not in_single
            elif char == '"' and not in_single:
                in_double = not in_double
        
        if in_single or in_double:
            return {
                "language": language,
                "predicted_error": "UnclosedString",
                "confidence": 1.0,
                "tutor": explain_error("UnclosedString"),
                "rule_based_issues": []
            }

        has_missing_semi = _has_missing_semicolons(code)
        has_unbalanced   = not _braces_balanced(code)

        if not has_missing_semi and not has_unbalanced:
            # Structurally valid — check for semantic errors via ML
            semantic = _ml_semantic_check(code, language, [])
            if semantic:
                return semantic
            return {
                "language": language,
                "predicted_error": "NoError",
                "confidence": 1.0,
                "tutor": {
                    "why": "The code follows valid syntax rules for this language.",
                    "fix": "No changes are required."
                },
                "rule_based_issues": []
            }

        ml_error, confidence = detect_error_ml(code)
        ml_error = _normalize(ml_error)
        if confidence >= SYNTAX_ERROR_THRESHOLD and ml_error in RULE_BASED_TYPES:
            return {
                "language": language,
                "predicted_error": ml_error,
                "confidence": confidence,
                "tutor": explain_error(ml_error),
                "rule_based_issues": []
            }

        if has_unbalanced:
            return {
                "language": language,
                "predicted_error": "UnmatchedBracket",
                "confidence": 1.0,
                "tutor": explain_error("UnmatchedBracket"),
                "rule_based_issues": []
            }

        return {
            "language": language,
            "predicted_error": "MissingDelimiter",
            "confidence": 1.0,
            "tutor": explain_error("MissingDelimiter"),
            "rule_based_issues": []
        }

    # =========================================================================
    # UNKNOWN LANGUAGE — ML only
    # =========================================================================
    ml_error, confidence = detect_error_ml(code)
    ml_error = _normalize(ml_error)
    if confidence < SYNTAX_ERROR_THRESHOLD or ml_error == "NoError":
        return {
            "language": language,
            "predicted_error": "NoError",
            "confidence": confidence,
            "tutor": {
                "why": "The code structure appears syntactically correct.",
                "fix": "No changes are required."
            },
            "rule_based_issues": rule_based_issues
        }
    return {
        "language": language,
        "predicted_error": ml_error,
        "confidence": confidence,
        "tutor": explain_error(ml_error),
        "rule_based_issues": rule_based_issues
    }
