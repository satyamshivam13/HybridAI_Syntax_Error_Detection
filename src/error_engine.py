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
import builtins
import re

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

def _has_unclosed_strings(code: str) -> bool:
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
    return in_single or in_double

def _semantic_heuristic_ok(error_type: str, code: str, language: str) -> bool:
    """
    Guardrail heuristics to reduce semantic false positives on structurally valid code.
    """
    lines = [line for line in code.splitlines() if line.strip()]
    code_text = "\n".join(lines)

    if error_type == "InvalidAssignment":
        # Structurally-valid code should not be tagged as invalid assignment.
        return False

    if error_type == "DivisionByZero":
        return bool(re.search(r"[/%]\s*0(\.0+)?\b", code_text))

    if error_type in {"ImportError", "MissingImport", "WildcardImport"}:
        return bool(re.search(r"^\s*(import|from)\s+", code_text, flags=re.MULTILINE))

    if error_type == "MissingInclude":
        return bool(re.search(r"^\s*#include\s+", code_text, flags=re.MULTILINE))

    if error_type == "InfiniteLoop":
        return bool(
            re.search(r"\bwhile\s*\(\s*true\s*\)|\bwhile\s+true\b|\bwhile\s*\(\s*1\s*\)|\bfor\s*\(\s*;\s*;\s*\)", code_text, flags=re.IGNORECASE)
        )

    if error_type == "UnreachableCode":
        return bool(
            re.search(
                r"\b(return|break|continue|raise|throw)\b[^\n]*\n\s*[A-Za-z_#]",
                code_text,
                flags=re.IGNORECASE,
            )
        )

    if error_type == "MutableDefault":
        if language != "Python":
            return False
        return bool(
            re.search(
                r"def\s+\w+\s*\([^)]*=\s*(\[\]|\{\}|set\(|dict\(|list\()",
                code_text,
            )
        )

    if error_type == "LineTooLong":
        return any(len(line) > 120 for line in lines)

    if error_type == "DuplicateDefinition":
        if language != "Python":
            return bool(re.search(r"\b(class|interface|struct|void|int|float|double|char)\s+\w+\s*\(", code_text))
        try:
            tree = _ast.parse(code)
        except Exception:
            return False
        seen = set()
        for node in _ast.walk(tree):
            if isinstance(node, (_ast.FunctionDef, _ast.ClassDef)):
                name = node.name
                if name in seen:
                    return True
                seen.add(name)
        return False

    if error_type == "UnusedVariable":
        if language != "Python":
            return bool(re.search(r"\b(int|float|double|char|string|bool|auto|var|let|const)\b", code_text, flags=re.IGNORECASE))
        try:
            tree = _ast.parse(code)
        except Exception:
            return False
        assigned = set()
        loaded = set()
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Name):
                if isinstance(node.ctx, _ast.Store):
                    assigned.add(node.id)
                elif isinstance(node.ctx, _ast.Load):
                    loaded.add(node.id)
        return len(assigned - loaded) > 0

    if error_type in {"NameError", "UndeclaredIdentifier"} and language == "Python":
        try:
            tree = _ast.parse(code)
        except Exception:
            return False

        defined = set()
        used = set()
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Name):
                if isinstance(node.ctx, _ast.Store):
                    defined.add(node.id)
                elif isinstance(node.ctx, _ast.Load):
                    used.add(node.id)
            elif isinstance(node, (_ast.FunctionDef, _ast.ClassDef)):
                defined.add(node.name)
                for arg in node.args.args:
                    defined.add(arg.arg)
                if hasattr(node.args, "posonlyargs"):
                    for arg in node.args.posonlyargs:
                        defined.add(arg.arg)
                for arg in node.args.kwonlyargs:
                    defined.add(arg.arg)
                if node.args.vararg:
                    defined.add(node.args.vararg.arg)
                if node.args.kwarg:
                    defined.add(node.args.kwarg.arg)
            elif isinstance(node, (_ast.Import, _ast.ImportFrom)):
                for alias in node.names:
                    defined.add(alias.asname or alias.name.split(".")[0])

        builtin_names = set(dir(builtins))
        unresolved = {
            name for name in used
            if name not in defined and name not in builtin_names
        }
        return len(unresolved) > 0

    if error_type == "TypeMismatch":
        return bool(
            re.search(
                r"\b(int|float|double|char|bool|String|string)\b|int\(|float\(|str\(|bool\(",
                code_text,
            )
        )

    return True


def _append_warning(warnings: list[str], message: str) -> None:
    if message and message not in warnings:
        warnings.append(message)


def _safe_ml_prediction(code: str, warnings: list[str]) -> tuple[str, float] | None:
    try:
        return detect_error_ml(code)
    except ModelUnavailableError:
        status = get_model_status()
        _append_warning(
            warnings,
            f"ML model unavailable; semantic classification skipped ({status.get('error', 'unknown reason')})",
        )
        return None
    except ModelInferenceError as exc:
        _append_warning(warnings, f"ML inference failure; semantic classification skipped ({exc})")
        return None


def _attach_metadata(payload: dict, warnings: list[str]) -> dict:
    payload["degraded_mode"] = len(warnings) > 0
    payload["warnings"] = list(warnings)
    return payload

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

def _ml_semantic_check(code, language, rule_based_issues, warnings):
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
    
    ml_result = _safe_ml_prediction(code, warnings)
    if ml_result is None:
        return None
    ml_error, confidence = ml_result
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


def detect_errors(code: str, filename: str | None = None, language_override: str | None = None):
    """
    Detect syntax and semantic errors using a hybrid approach.
    """
    warnings: list[str] = []
    if not is_model_available():
        status = get_model_status()
        _append_warning(
            warnings,
            f"ML model unavailable; falling back to rule-based checks only ({status.get('error', 'unknown reason')})",
        )

    if language_override in {"Python", "Java", "C", "C++", "JavaScript"}:
        language = language_override
    else:
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
            semantic = _ml_semantic_check(code, language, [], warnings)
            if semantic:
                return _attach_metadata(semantic, warnings)
            # No semantic error detected either
            return _attach_metadata({
                "language": language,
                "predicted_error": "NoError",
                "confidence": 1.0,
                "tutor": {
                    "why": "The Python code follows correct syntax rules.",
                    "fix": "No changes are required."
                },
                "rule_based_issues": []
            }, warnings)

        # AST failed — classify the syntax error
        rule_based_issues = detect_all(code)
        for issue in rule_based_issues:
            if issue.get("type") in LABEL_ALIASES:
                issue["type"] = LABEL_ALIASES[issue["type"]]

        strong_issues = [i for i in rule_based_issues if i.get("type") in RULE_BASED_TYPES]

        if strong_issues:
            rb_error = strong_issues[0].get("type", "SyntaxError")

            # AST already failed and rule-based found concrete syntax issue(s).
            # Keep syntax findings authoritative to prevent semantic false overrides.
            return _attach_metadata({
                "language": language,
                "predicted_error": rb_error,
                "confidence": 1.0,
                "tutor": explain_error(rb_error),
                "rule_based_issues": rule_based_issues
            }, warnings)

        # Rule-based didn't classify → use ML for syntax error classification
        ml_result = _safe_ml_prediction(code, warnings)
        if ml_result is None:
            return _attach_metadata({
                "language": language,
                "predicted_error": "SyntaxError",
                "confidence": 0.0,
                "tutor": explain_error("SyntaxError"),
                "rule_based_issues": rule_based_issues
            }, warnings)
        ml_error, confidence = ml_result
        ml_error = _normalize(ml_error)
        if confidence < SYNTAX_ERROR_THRESHOLD or ml_error == "NoError":
            return _attach_metadata({
                "language": language,
                "predicted_error": "NoError",
                "confidence": confidence,
                "tutor": {
                    "why": "The code structure appears syntactically correct.",
                    "fix": "No changes are required."
                },
                "rule_based_issues": rule_based_issues
            }, warnings)
        return _attach_metadata({
            "language": language,
            "predicted_error": ml_error,
            "confidence": confidence,
            "tutor": explain_error(ml_error),
            "rule_based_issues": rule_based_issues
        }, warnings)

    # =========================================================================
    # JAVA / C / C++
    # =========================================================================
    elif language in ["Java", "C", "C++"]:

        # Check for unclosed strings first (higher priority than other errors)
        if _has_unclosed_strings(code):
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
            semantic = _ml_semantic_check(code, language, [], warnings)
            if semantic:
                return _attach_metadata(semantic, warnings)
            return _attach_metadata({
                "language": language,
                "predicted_error": "NoError",
                "confidence": 1.0,
                "tutor": {
                    "why": "The code follows valid syntax rules for this language.",
                    "fix": "No changes are required."
                },
                "rule_based_issues": []
            }, warnings)

        ml_result = _safe_ml_prediction(code, warnings)
        if ml_result is None:
            ml_error, confidence = ("NoError", 0.0)
        else:
            ml_error, confidence = ml_result
        ml_error = _normalize(ml_error)
        if confidence >= SYNTAX_ERROR_THRESHOLD and ml_error in RULE_BASED_TYPES:
            return _attach_metadata({
                "language": language,
                "predicted_error": ml_error,
                "confidence": confidence,
                "tutor": explain_error(ml_error),
                "rule_based_issues": []
            }, warnings)

        if has_unbalanced:
            return _attach_metadata({
                "language": language,
                "predicted_error": "UnmatchedBracket",
                "confidence": 1.0,
                "tutor": explain_error("UnmatchedBracket"),
                "rule_based_issues": []
            }, warnings)

        return _attach_metadata({
            "language": language,
            "predicted_error": "MissingDelimiter",
            "confidence": 1.0,
            "tutor": explain_error("MissingDelimiter"),
            "rule_based_issues": []
        }, warnings)

    # =========================================================================
    # UNKNOWN LANGUAGE — ML only
    # =========================================================================
    ml_result = _safe_ml_prediction(code, warnings)
    if ml_result is None:
        return _attach_metadata({
            "language": language,
            "predicted_error": "NoError",
            "confidence": 0.0,
            "tutor": {
                "why": "The code structure could not be fully classified because ML is unavailable.",
                "fix": "Retry after restoring model compatibility."
            },
            "rule_based_issues": rule_based_issues
        }, warnings)
    ml_error, confidence = ml_result
    ml_error = _normalize(ml_error)
    if confidence < SYNTAX_ERROR_THRESHOLD or ml_error == "NoError":
        return _attach_metadata({
            "language": language,
            "predicted_error": "NoError",
            "confidence": confidence,
            "tutor": {
                "why": "The code structure appears syntactically correct.",
                "fix": "No changes are required."
            },
            "rule_based_issues": rule_based_issues
        }, warnings)
    return _attach_metadata({
        "language": language,
        "predicted_error": ml_error,
        "confidence": confidence,
        "tutor": explain_error(ml_error),
        "rule_based_issues": rule_based_issues
    }, warnings)
