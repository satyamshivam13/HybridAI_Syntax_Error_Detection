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
    "ImportError": 0.75,
    "InfiniteLoop": 0.75,
    "UnreachableCode": 0.85,
    "InvalidAssignment": 0.85,
    "DuplicateDefinition": 0.85,
    "NameError": 0.75,
    "UndeclaredIdentifier": 0.75,
    "TypeMismatch": 0.75,
    "MissingImport": 0.75,
    "MissingInclude": 0.75,
    "LineTooLong": 0.85,
    "WildcardImport": 0.85,
    "MutableDefault": 0.85,
    "UnusedVariable": 0.85,
    "DanglingPointer": 0.85,
}

# Rule-based types that are always authoritative


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
    "WildcardImport", "DanglingPointer",
}

LABEL_ALIASES = {
    "UnclosedQuotes": "UnclosedString",
    # Dataset/model label uses MissingDelimiter for Python missing ':' as well.
    "MissingColon": "MissingDelimiter",
}

C_LIKE_ISSUE_PRIORITY = [
    "UnclosedString",
    "UnmatchedBracket",
    "MissingDelimiter",
    "TypeMismatch",
    "MissingImport",
    "MissingInclude",
    "DuplicateDefinition",
    "UndeclaredIdentifier",
    "DanglingPointer",
    "DivisionByZero",
    "InfiniteLoop",
    "UnreachableCode",
]

JAVA_IMPORT_HINTS = {
    "ArrayList": "java.util.ArrayList",
    "List": "java.util.List",
    "Map": "java.util.Map",
    "Set": "java.util.Set",
    "HashMap": "java.util.HashMap",
    "HashSet": "java.util.HashSet",
    "Scanner": "java.util.Scanner",
}

C_STDIO_SYMBOLS = {
    # stdio.h
    "printf", "fprintf", "sprintf", "scanf", "fscanf", "puts", "gets", "fgets",
    "FILE", "fopen", "fclose", "fread", "fwrite", "fputs", "fputc", "getc",
    # stdlib.h
    "malloc", "calloc", "realloc", "free", "exit", "abort", "system",
    "atoi", "atof", "strtol", "strtod", "rand", "srand",
    # string.h
    "strlen", "strcpy", "strncpy", "strcat", "strcmp", "strncmp",
    "strchr", "strrchr", "strstr", "strtok", "strdup",
    # math.h
    "sin", "cos", "tan", "sqrt", "pow", "abs", "ceil", "floor",
    # ctype.h
    "isalpha", "isdigit", "isspace", "toupper", "tolower",
    # time.h
    "time", "clock", "difftime", "mktime", "localtime",
    # assert.h
    "assert",
}

C_SYMBOL_TO_HEADER = {
    # stdio.h
    "printf": "stdio.h", "fprintf": "stdio.h", "sprintf": "stdio.h",
    "scanf": "stdio.h", "fscanf": "stdio.h", "puts": "stdio.h", "gets": "stdio.h",
    "fgets": "stdio.h", "FILE": "stdio.h", "fopen": "stdio.h", "fclose": "stdio.h",
    "fread": "stdio.h", "fwrite": "stdio.h", "fputs": "stdio.h", "fputc": "stdio.h",
    "getc": "stdio.h",
    # stdlib.h
    "malloc": "stdlib.h", "calloc": "stdlib.h", "realloc": "stdlib.h",
    "free": "stdlib.h", "exit": "stdlib.h", "abort": "stdlib.h", "system": "stdlib.h",
    "atoi": "stdlib.h", "atof": "stdlib.h", "strtol": "stdlib.h",
    "strtod": "stdlib.h", "rand": "stdlib.h", "srand": "stdlib.h",
    # string.h
    "strlen": "string.h", "strcpy": "string.h", "strncpy": "string.h",
    "strcat": "string.h", "strcmp": "string.h", "strncmp": "string.h",
    "strchr": "string.h", "strrchr": "string.h", "strstr": "string.h",
    "strtok": "string.h", "strdup": "string.h",
    # math.h
    "sin": "math.h", "cos": "math.h", "tan": "math.h", "sqrt": "math.h",
    "pow": "math.h", "abs": "math.h", "ceil": "math.h", "floor": "math.h",
    # ctype.h
    "isalpha": "ctype.h", "isdigit": "ctype.h", "isspace": "ctype.h",
    "toupper": "ctype.h", "tolower": "ctype.h",
    # time.h
    "time": "time.h", "clock": "time.h", "difftime": "time.h",
    "mktime": "time.h", "localtime": "time.h",
    # assert.h
    "assert": "assert.h",
}

JS_GLOBALS = {
    "console", "Math", "Number", "String", "Boolean", "Array", "Object",
    "JSON", "Promise", "window", "document", "undefined", "NaN", "Infinity",
    "parseInt", "parseFloat", "setTimeout", "clearTimeout", "setInterval",
    "clearInterval", "require", "module", "exports",
}

C_LIKE_KEYWORDS = {
    "if", "else", "for", "while", "switch", "case", "default", "do", "break",
    "continue", "return", "throw", "try", "catch", "finally", "new", "class",
    "public", "private", "protected", "static", "final", "void", "package",
    "import", "namespace", "using", "struct", "enum", "typedef", "sizeof",
    "const", "volatile", "unsigned", "signed", "long", "short", "int", "float",
    "double", "char", "bool", "boolean", "String", "string", "var", "let",
    "const", "function", "true", "false", "null",
}

def _normalize(label: str | None) -> str:
    if not label:
        return "NoError"
    return LABEL_ALIASES.get(label, label)


def _make_issue(
    issue_type: str,
    message: str,
    line: int | None = None,
    col: int | None = None,
    snippet: str | None = None,
    suggestion: str | None = None,
) -> dict:
    return {
        "type": issue_type,
        "message": message,
        "line": line,
        "col": col,
        "snippet": snippet,
        "suggestion": suggestion,
    }


def _normalize_rule_issues(issues: list[dict]) -> list[dict]:
    seen = set()
    normalized = []
    for issue in issues:
        issue_type = _normalize(issue.get("type", "SyntaxError"))
        key = (
            issue_type,
            issue.get("line"),
            issue.get("col"),
            issue.get("message"),
        )
        if key in seen:
            continue
        seen.add(key)
        normalized.append({
            "type": issue_type,
            "message": issue.get("message"),
            "line": issue.get("line"),
            "col": issue.get("col"),
            "snippet": issue.get("snippet"),
            "suggestion": issue.get("suggestion"),
        })
    return sorted(
        normalized,
        key=lambda item: (
            C_LIKE_ISSUE_PRIORITY.index(item["type"])
            if item["type"] in C_LIKE_ISSUE_PRIORITY else len(C_LIKE_ISSUE_PRIORITY),
            item["line"] if item.get("line") is not None else 9999,
            item["col"] if item.get("col") is not None else 9999,
        ),
    )


def _pick_primary_issue(issues: list[dict]) -> dict | None:
    normalized = _normalize_rule_issues(issues)
    return normalized[0] if normalized else None


def _should_suppress_java_undeclared_identifier(rule_based_issues: list[dict], ml_error: str | None) -> bool:
    """
    Suppress a Java UndeclaredIdentifier ML guess when rule-based analysis already
    found a TypeMismatch in the same snippet. In practice, that pairing is a cascade
    from the typed assignment, not a second independent issue.
    """
    if ml_error != "UndeclaredIdentifier":
        return False
    return any(issue.get("type") == "TypeMismatch" for issue in rule_based_issues)


def _suppress_cascading_syntax_noise(issues: list[dict]) -> list[dict]:
    """
    When an unclosed string exists, bracket findings are often a cascade from the
    broken tokenizer state rather than independent student mistakes. Suppress the
    follow-on bracket noise so the tutor can focus on the primary fix first.
    """
    has_unclosed_string = any(issue.get("type") == "UnclosedString" for issue in issues)
    if not has_unclosed_string:
        return issues
    return [issue for issue in issues if issue.get("type") != "UnmatchedBracket"]


def _strip_c_like_comments_and_strings(code: str) -> str:
    """
    Return a code-shaped string where comments/strings are replaced with spaces.
    Newlines are preserved so line-based checks remain stable.
    """
    out: list[str] = []
    i = 0
    n = len(code)
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False

    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                out.append("\n")
            else:
                out.append(" ")
            i += 1
            continue

        if in_block_comment:
            if ch == "*" and nxt == "/":
                out.extend([" ", " "])
                i += 2
                in_block_comment = False
                continue
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue

        if in_single:
            if ch == "\\" and i + 1 < n:
                out.append(" ")
                out.append("\n" if code[i + 1] == "\n" else " ")
                i += 2
                continue
            if ch == "'":
                in_single = False
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue

        if in_double:
            if ch == "\\" and i + 1 < n:
                out.append(" ")
                out.append("\n" if code[i + 1] == "\n" else " ")
                i += 2
                continue
            if ch == '"':
                in_double = False
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue

        if ch == "/" and nxt == "/":
            in_line_comment = True
            out.extend([" ", " "])
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            out.extend([" ", " "])
            i += 2
            continue
        if ch == "'":
            in_single = True
            out.append(" ")
            i += 1
            continue
        if ch == '"':
            in_double = True
            out.append(" ")
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def _braces_balanced(code):
    return len(_find_unmatched_bracket_issues(code)) == 0

def _has_unclosed_strings(code: str) -> bool:
    return _find_unclosed_string_issue(code) is not None


def _find_unclosed_string_issue(code: str) -> dict | None:
    in_single = False
    in_double = False
    in_backtick = False
    escaped = False
    start_line = start_col = None
    line = 1
    col = 0

    for char in code:
        if char == "\n":
            line += 1
            col = 0
            if escaped:
                escaped = False
            continue

        col += 1

        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "'" and not in_double and not in_backtick:
            if not in_single:
                start_line, start_col = line, col
            in_single = not in_single
        elif char == '"' and not in_single and not in_backtick:
            if not in_double:
                start_line, start_col = line, col
            in_double = not in_double
        elif char == "`" and not in_single and not in_double:
            if not in_backtick:
                start_line, start_col = line, col
            in_backtick = not in_backtick

    if in_single or in_double or in_backtick:
        line_text = code.splitlines()[start_line - 1] if start_line and code.splitlines() else ""
        return _make_issue(
            "UnclosedString",
            "String literal is not closed before end of file.",
            line=start_line,
            col=start_col,
            snippet=line_text.strip(),
            suggestion="Add the missing closing quote.",
        )
    return None


def _find_unmatched_bracket_issues(code: str) -> list[dict]:
    sanitized = _strip_c_like_comments_and_strings(code)
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    issues = []
    line = 1
    col = 0
    lines = code.splitlines()

    for ch in sanitized:
        if ch == "\n":
            line += 1
            col = 0
            continue
        col += 1
        if ch in "([{":
            stack.append((ch, line, col))
        elif ch in ")]}":
            if not stack or stack[-1][0] != pairs[ch]:
                snippet = lines[line - 1].strip() if line - 1 < len(lines) else ""
                issues.append(_make_issue(
                    "UnmatchedBracket",
                    f"Found closing {ch} without a matching opening bracket.",
                    line=line,
                    col=col,
                    snippet=snippet,
                    suggestion="Remove the extra closing bracket or add the missing opening bracket.",
                ))
                continue
            stack.pop()

    for opening, opening_line, opening_col in stack:
        snippet = lines[opening_line - 1].strip() if opening_line - 1 < len(lines) else ""
        issues.append(_make_issue(
            "UnmatchedBracket",
            f"Opening {opening} is missing a matching closing bracket.",
            line=opening_line,
            col=opening_col,
            snippet=snippet,
            suggestion=f"Add a closing bracket for {opening}.",
        ))
    return issues

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
        if language in {"C", "C++"}:
            return False
        has_import = bool(re.search(r"^\s*(import|from)\s+", code_text, flags=re.MULTILINE))
        has_wildcard_import = bool(
            re.search(r"^\s*from\s+\w+(?:\.\w+)*\s+import\s+\*\s*$", code_text, flags=re.MULTILINE)
        )
        python_external_usage = bool(
            re.search(
                r"\b(?:sqrt|sin|cos|tan|pi|datetime|timedelta|Counter|defaultdict|deque|randint|choice)\b|"
                r"\b(?:np|pd|plt|math|random|json|re|collections|datetime)\s*\.",
                code_text,
            )
        )
        if error_type == "MissingImport":
            if language == "Python":
                return (not has_import) and python_external_usage
            return not has_import
        if error_type == "WildcardImport":
            if language == "Python":
                return has_wildcard_import
            return has_import
        return has_import

    if error_type == "MissingInclude":
        if language not in {"C", "C++"}:
            return False
        return not bool(re.search(r"^\s*#include\s+", code_text, flags=re.MULTILINE))

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

    if error_type in {"NameError", "UndeclaredIdentifier"}:
        if language != "Python":
            return False
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
            elif isinstance(node, _ast.FunctionDef):
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
            elif isinstance(node, _ast.ClassDef):
                defined.add(node.name)
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


def _should_run_semantic_ml(code: str, language: str) -> bool:
    """
    Fast pre-filter to avoid expensive ML calls on obviously clean snippets.
    """
    lines = [line for line in code.splitlines() if line.strip()]
    if not lines:
        return False
    code_text = "\n".join(lines)

    if any(len(line) > 120 for line in lines):
        return True
    if re.search(r"[/%]\s*0(\.0+)?\b", code_text):
        return True
    if re.search(r"\bwhile\s*\(\s*true\s*\)|\bwhile\s+true\b|\bwhile\s*\(\s*1\s*\)|\bfor\s*\(\s*;\s*;\s*\)", code_text, flags=re.IGNORECASE):
        return True
    if re.search(r"\b(return|break|continue|raise|throw)\b[^\n]*\n\s*[A-Za-z_#]", code_text, flags=re.IGNORECASE):
        return True

    if language == "Python":
        if re.search(r"^\s*(import|from)\s+", code_text, flags=re.MULTILINE):
            return True
        if re.search(r"\b(?:np|pd|plt|math|random|json|re|collections|datetime)\s*\.", code_text):
            return True
        if re.search(r"\b(?:sqrt|sin|cos|tan|pi|Counter|defaultdict|deque|randint|choice)\b", code_text):
            return True
        if re.search(r"\bfrom\s+\w+\s+import\s+\*", code_text):
            return True
        if re.search(r"def\s+\w+\s*\([^)]*=\s*(\[\]|\{\}|set\(|dict\(|list\()", code_text):
            return True
        if code_text.count("def ") > 1 or code_text.count("class ") > 1:
            return True
        return False

    if language in {"Java", "C", "C++"}:
        if re.search(r"^\s*#include\s+", code_text, flags=re.MULTILINE):
            return True
        if re.search(r"^\s*import\s+", code_text, flags=re.MULTILINE):
            return True
        if re.search(r"\b(class|interface|struct)\s+\w+", code_text):
            return True
        return False

    if language == "JavaScript":
        if re.search(r"^\s*import\s+", code_text, flags=re.MULTILINE):
            return True
        return False

    return False


def _find_python_wildcard_import_issue(code: str) -> dict | None:
    for lineno, line in enumerate(code.splitlines(), start=1):
        if re.search(r"^\s*from\s+\w+(?:\.\w+)*\s+import\s+\*\s*$", line):
            return {
                "type": "WildcardImport",
                "line": lineno,
                "col": 1,
                "message": "Wildcard import can pollute namespace and hide name collisions.",
                "snippet": line.strip(),
                "suggestion": "Import only the specific names you need.",
            }
    return None


def _find_python_name_error_issue(code: str) -> dict | None:
    try:
        tree = _ast.parse(code)
    except Exception:
        return None

    defined = set()
    used = []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Name):
            if isinstance(node.ctx, _ast.Store):
                defined.add(node.id)
            elif isinstance(node.ctx, _ast.Load):
                used.append((node.id, getattr(node, "lineno", 1), getattr(node, "col_offset", 0) + 1))
        elif isinstance(node, _ast.FunctionDef):
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
        elif isinstance(node, _ast.ClassDef):
            defined.add(node.name)
        elif isinstance(node, (_ast.Import, _ast.ImportFrom)):
            for alias in node.names:
                defined.add(alias.asname or alias.name.split(".")[0])

    builtin_names = set(dir(builtins))
    snippet_lines = code.splitlines()
    for name, line_no, col_no in used:
        if name in defined or name in builtin_names:
            continue
        snippet = snippet_lines[line_no - 1].strip() if 0 < line_no <= len(snippet_lines) else ""
        return {
            "type": "NameError",
            "line": line_no,
            "col": col_no,
            "message": f"{name} is used before assignment or import.",
            "snippet": snippet,
            "suggestion": "Define or import the name before using it.",
        }
    return None


def _has_infinite_loop(code: str) -> bool:
    """
    Rule-based detector for obvious infinite-loop patterns.
    Works for Java, C, C++, and JavaScript.
    """
    return len(_find_infinite_loop_issues(code)) > 0


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

def _has_statement_glued_after_assignment(line: str) -> bool:
    """
    Detect missing ';' between two statements on a single line, e.g.:
      int x = 1 System.out.println(x);
    """
    if "=" not in line:
        return False
    if "for(" in line or "for (" in line:
        return False

    declaration_then_stmt = re.search(
        r"(?:^|[;{}])\s*(?:[A-Za-z_][\w<>\[\]]*\s+)+[A-Za-z_]\w*\s*=\s*[^;{}]+?\s*"
        r"(?:System\.out|console\.log|printf|fprintf|puts|cout|std::cout|cin|std::cin|[A-Za-z_]\w+\s*=)",
        line,
    )
    if declaration_then_stmt:
        return True

    assignment_then_known_stmt = re.search(
        r"(?:^|[;{}])\s*[A-Za-z_]\w*\s*=\s*[^;{}]+?\s*"
        r"(?:System\.out|console\.log|printf|fprintf|puts|cout|std::cout|cin|std::cin|return\b|if\b|while\b|switch\b|throw\b|[A-Za-z_]\w+\s*=)",
        line,
    )
    return bool(assignment_then_known_stmt)


def _find_missing_semicolon_issues(code: str, language: str | None = None) -> list[dict]:
    sanitized = _strip_c_like_comments_and_strings(code)
    simple_statements = [
        r'^return\s+.+$', r'^cout\s*<<.*$', r'^cin\s*>>.*$',
        r'^printf\s*\(.*\)$', r'^fprintf\s*\(.*\)$', r'^puts\s*\(.*\)$',
        r'^std::cout\s*<<.*$', r'^std::cin\s*>>.*$',
        r'^(break|continue)\s*$', r'^\w+(\.\w+)?\s*(\+\+|--)$',
        r'^throw\s+.+$',
    ]
    issues = []
    for lineno, (raw, clean) in enumerate(zip(code.splitlines(), sanitized.splitlines()), start=1):
        l = clean.strip()
        if not l:
            continue

        if l.startswith("using namespace") and not l.endswith(";"):
            issues.append(_make_issue(
                "MissingDelimiter",
                "Missing semicolon after namespace declaration.",
                line=lineno,
                col=max(len(raw.rstrip()), 1),
                snippet=raw.strip(),
                suggestion="Add ';' at the end of the statement.",
            ))
            continue

        if re.match(r"^(struct|enum)\b.*}\s*$", l) and not l.endswith("};"):
            issues.append(_make_issue(
                "MissingDelimiter",
                "Missing semicolon after struct or enum declaration.",
                line=lineno,
                col=max(len(raw.rstrip()), 1),
                snippet=raw.strip(),
                suggestion="Add ';' after the closing brace.",
            ))
            continue

        if re.match(
            r"^(?:unsigned|signed|long|short|int|float|double|char|bool|auto|string|"
            r"vector<[^>]+>|map<[^>]+>|set<[^>]+>|[A-Za-z_]\w*(?:::\w+)?)\s+"
            r"[A-Za-z_]\w*(?:\s*\[[^\]]*\])?$",
            l,
        ):
            issues.append(_make_issue(
                "MissingDelimiter",
                "Missing semicolon after variable declaration.",
                line=lineno,
                col=max(len(raw.rstrip()), 1),
                snippet=raw.strip(),
                suggestion="Add ';' at the end of the declaration.",
            ))
            continue

        if _has_statement_glued_after_assignment(l):
            issues.append(_make_issue(
                "MissingDelimiter",
                "Two statements appear to be glued together without a semicolon.",
                line=lineno,
                col=max(len(raw.rstrip()), 1),
                snippet=raw.strip(),
                suggestion="Insert ';' between the statements.",
            ))
            continue

        if (l.startswith('//') or l.startswith('/*') or l.startswith('*') or
            l.startswith('#') or l.endswith('{') or l.endswith('}') or
            l.startswith('import') or l.startswith('package') or
            l.startswith('using') or l.startswith('namespace') or
            'class ' in l[:20]):
            continue
        if language == "JavaScript":
            # JavaScript supports automatic semicolon insertion; only flag stronger patterns.
            continue
        is_control = any(kw in l for kw in [
            'if (', 'if(', 'for (', 'for(', 'while (', 'while(',
            'else', 'try', 'catch', 'switch', 'case ', 'default:', 'do '
        ])
        if not is_control and not l.endswith(';') and not l.endswith('{') and not l.endswith('}'):
            if any(re.match(pat, l) for pat in simple_statements):
                issues.append(_make_issue(
                    "MissingDelimiter",
                    "Missing semicolon at the end of the statement.",
                    line=lineno,
                    col=max(len(raw.rstrip()), 1),
                    snippet=raw.strip(),
                    suggestion="Add ';' at the end of the statement.",
                ))
            elif ('=' in l or ('(' in l and ')' in l)) and not l.startswith('}'):
                issues.append(_make_issue(
                    "MissingDelimiter",
                    "Missing semicolon at the end of the statement.",
                    line=lineno,
                    col=max(len(raw.rstrip()), 1),
                    snippet=raw.strip(),
                    suggestion="Add ';' at the end of the statement.",
                ))
    return issues


def _has_missing_semicolons(code):
    return len(_find_missing_semicolon_issues(code)) > 0


def _find_infinite_loop_issues(code: str) -> list[dict]:
    sanitized = _strip_c_like_comments_and_strings(code)
    issues = []
    for lineno, line in enumerate(sanitized.splitlines(), start=1):
        if re.search(r"\bwhile\s*\(\s*(true|1)\s*\)|\bfor\s*\(\s*;\s*;\s*\)", line, flags=re.IGNORECASE):
            issues.append(_make_issue(
                "InfiniteLoop",
                "Loop condition is always true and has no visible exit path.",
                line=lineno,
                col=max(line.find("while"), line.find("for")) + 1,
                snippet=code.splitlines()[lineno - 1].strip(),
                suggestion="Add an exit condition or a break path inside the loop.",
            ))
    return issues


def _find_division_by_zero_issues(code: str) -> list[dict]:
    sanitized = _strip_c_like_comments_and_strings(code)
    issues = []
    sanitized_lines = sanitized.splitlines()
    original_lines = code.splitlines()

    # Track simple constant assignments so `x / y` can be flagged when y == 0.
    zero_vars: set[str] = set()
    for line in sanitized_lines:
        for assign_match in re.finditer(r"\b([A-Za-z_]\w*)\s*=\s*0(?:\.0+)?\s*;?", line):
            zero_vars.add(assign_match.group(1))

    for lineno, line in enumerate(sanitized_lines, start=1):
        literal_match = re.search(r"[/%]\s*0(\.0+)?\b", line)
        if literal_match:
            issues.append(_make_issue(
                "DivisionByZero",
                "Possible division or modulo by zero.",
                line=lineno,
                col=literal_match.start() + 1,
                snippet=original_lines[lineno - 1].strip(),
                suggestion="Guard the denominator or change it to a non-zero value.",
            ))
            continue

        var_match = re.search(r"[/%]\s*([A-Za-z_]\w*)\b", line)
        if var_match and var_match.group(1) in zero_vars:
            issues.append(_make_issue(
                "DivisionByZero",
                f"Possible division or modulo by zero via variable '{var_match.group(1)}'.",
                line=lineno,
                col=var_match.start() + 1,
                snippet=original_lines[lineno - 1].strip(),
                suggestion="Guard the denominator or change it to a non-zero value.",
            ))
    return issues


def _find_unreachable_code_issues(code: str) -> list[dict]:
    sanitized_lines = _strip_c_like_comments_and_strings(code).splitlines()
    original_lines = code.splitlines()
    issues = []
    pending_after_jump = False

    for lineno, clean in enumerate(sanitized_lines, start=1):
        stripped = clean.strip()
        if not stripped:
            continue
        if pending_after_jump:
            if stripped.startswith("}") or stripped.startswith("case ") or stripped.startswith("default:"):
                pending_after_jump = False
            elif re.match(
                r"^(?:[A-Za-z_]\w*(?:::[A-Za-z_]\w*)?|public|private|protected|static|final|virtual|inline|template)"
                r"[\w\s:<>,*&\[\]]*\([^;]*\)\s*\{\s*$",
                stripped,
            ):
                # New function/method scope: previous jump does not apply here.
                pending_after_jump = False
            else:
                issues.append(_make_issue(
                    "UnreachableCode",
                    "Statement appears after a control-flow jump and may never execute.",
                    line=lineno,
                    col=1,
                    snippet=original_lines[lineno - 1].strip(),
                    suggestion="Remove the dead statement or restructure the control flow.",
                ))
                pending_after_jump = False
        jump_match = re.search(r"\b(return|break|continue|throw)\b", stripped)
        if jump_match:
            trailing = stripped[jump_match.end():]
            pending_after_jump = "}" not in trailing
    return issues


def _find_missing_include_issues(code: str, language: str) -> list[dict]:
    if language not in {"C", "C++"}:
        return []
    issues = []
    sanitized_lines = _strip_c_like_comments_and_strings(code).splitlines()
    includes = "\n".join(sanitized_lines)
    original_lines = code.splitlines()

    for symbol in C_STDIO_SYMBOLS:
        if symbol == "FILE":
            pattern = r"\bFILE\b"
        else:
            pattern = rf"\b{symbol}\s*\("
        if not re.search(pattern, includes):
            continue
        # Get the correct header for this symbol
        required_header = C_SYMBOL_TO_HEADER.get(symbol, "stdio.h")
        header_include_pattern = rf"^\s*#include\s*<{re.escape(required_header)}>"
        if re.search(header_include_pattern, includes, flags=re.MULTILINE):
            continue
        for lineno, line in enumerate(sanitized_lines, start=1):
            if re.search(pattern, line):
                issues.append(_make_issue(
                    "MissingInclude",
                    f"{symbol} is used without including <{required_header}>.",
                    line=lineno,
                    col=line.find(symbol) + 1,
                    snippet=original_lines[lineno - 1].strip(),
                    suggestion=f"Add '#include <{required_header}>' at the top of the file.",
                ))
                break

    if language == "C++" and re.search(r"\b(?:std::)?(?:cout|cin|cerr|clog)\b", includes):
        if not re.search(r"^\s*#include\s*<iostream>", includes, flags=re.MULTILINE):
            for lineno, line in enumerate(sanitized_lines, start=1):
                stream_match = re.search(r"\b(?:std::)?(cout|cin|cerr|clog)\b", line)
                if not stream_match:
                    continue
                issues.append(_make_issue(
                    "MissingInclude",
                    f"{stream_match.group(1)} is used without including <iostream>.",
                    line=lineno,
                    col=stream_match.start(1) + 1,
                    snippet=original_lines[lineno - 1].strip(),
                    suggestion="Add '#include <iostream>' at the top of the file.",
                ))
                break
    return issues


def _find_missing_import_issues(code: str, language: str) -> list[dict]:
    if language != "Java":
        return []
    issues = []
    sanitized_lines = _strip_c_like_comments_and_strings(code).splitlines()
    sanitized = "\n".join(sanitized_lines)
    original_lines = code.splitlines()

    for symbol, import_path in JAVA_IMPORT_HINTS.items():
        if not re.search(rf"\b{symbol}\b", sanitized):
            continue
        if re.search(rf"^\s*import\s+{re.escape(import_path)}\s*;", sanitized, flags=re.MULTILINE):
            continue
        if re.search(r"^\s*import\s+java\.util\.\*\s*;", sanitized, flags=re.MULTILINE):
            continue
        if f"java.util.{symbol}" in sanitized:
            continue
        for lineno, line in enumerate(sanitized_lines, start=1):
            if re.search(rf"\b{symbol}\b", line):
                issues.append(_make_issue(
                    "MissingImport",
                    f"{symbol} is used without importing {import_path}.",
                    line=lineno,
                    col=line.find(symbol) + 1,
                    snippet=original_lines[lineno - 1].strip(),
                    suggestion=f"Add 'import {import_path};' near the top of the file.",
                ))
                break
    return issues


def _find_type_mismatch_issues(code: str, language: str) -> list[dict]:
    if language not in {"Java", "C", "C++"}:
        return []
    issues = []
    original_lines = code.splitlines()
    sanitized_lines = _strip_c_like_comments_and_strings(code).splitlines()

    numeric_decl = re.compile(
        r"\b(?:int|long|short|byte|float|double|char|bool|boolean)\s+([A-Za-z_]\w*)\s*=\s*\"[^\"]*\"\s*;?"
    )
    string_decl = re.compile(r"\bString\s+([A-Za-z_]\w*)\s*=\s*\d+\s*;?")
    java_narrowing_numeric = re.compile(
        r"\b(?:int|long|short|byte|char)\s+[A-Za-z_]\w*\s*=\s*\d+\.\d+\s*;?"
    )
    java_string_bool = re.compile(r"\bString\s+[A-Za-z_]\w*\s*=\s*(?:true|false)\s*;?")
    java_bool_string = re.compile(r"\bboolean\s+[A-Za-z_]\w*\s*=\s*\"[^\"]*\"\s*;?")

    for lineno, raw in enumerate(original_lines, start=1):
        if numeric_decl.search(raw) or string_decl.search(raw):
            issues.append(_make_issue(
                "TypeMismatch",
                "Assigned value type does not match the declared variable type.",
                line=lineno,
                col=1,
                snippet=raw.strip(),
                suggestion="Convert the value to the correct type or change the variable declaration.",
            ))
        elif language == "Java" and (
            java_narrowing_numeric.search(sanitized_lines[lineno - 1])
            or java_string_bool.search(sanitized_lines[lineno - 1])
            or java_bool_string.search(sanitized_lines[lineno - 1])
        ):
            issues.append(_make_issue(
                "TypeMismatch",
                "Assigned value type does not match the declared variable type.",
                line=lineno,
                col=1,
                snippet=raw.strip(),
                suggestion="Use an explicit conversion or assign a compatible type.",
            ))
        elif language in {"C", "C++"} and re.search(r"\b(?:int|long|short|float|double|char)\s+[A-Za-z_]\w*\s*=\s*'.{2,}'", raw):
            issues.append(_make_issue(
                "TypeMismatch",
                "Assigned value type does not match the declared variable type.",
                line=lineno,
                col=1,
                snippet=raw.strip(),
                suggestion="Use a compatible scalar value or change the variable type.",
            ))
        elif language == "Java" and re.search(r"\bboolean\s+[A-Za-z_]\w*\s*=\s*\d+", sanitized_lines[lineno - 1]):
            issues.append(_make_issue(
                "TypeMismatch",
                "Assigned value type does not match the declared variable type.",
                line=lineno,
                col=1,
                snippet=raw.strip(),
                suggestion="Assign a boolean literal or convert the expression.",
            ))
    return issues


def _find_dangling_pointer_return_issues(code: str, language: str) -> list[dict]:
    if language not in {"C", "C++"}:
        return []

    sanitized_lines = _strip_c_like_comments_and_strings(code).splitlines()
    original_lines = code.splitlines()
    issues: list[dict] = []

    func_start = re.compile(
        r"^\s*(?:[A-Za-z_][\w:\s<>]*?)\*+\s*([A-Za-z_]\w*)\s*\(([^)]*)\)\s*\{\s*$"
    )
    local_decl = re.compile(
        r"^\s*(?:unsigned|signed|long|short|int|float|double|char|bool|size_t|auto|"
        r"[A-Za-z_]\w*(?:::[A-Za-z_]\w*)?(?:<[^>]+>)?)\s+\**\s*([A-Za-z_]\w*)\b"
    )
    return_addr = re.compile(r"\breturn\s*&\s*([A-Za-z_]\w*)\s*;")
    ptr_decl_from_call = re.compile(
        r"\b(?:unsigned|signed|long|short|int|float|double|char|bool|size_t|auto|"
        r"[A-Za-z_]\w*(?:::[A-Za-z_]\w*)?(?:<[^>]+>)?)\s*\*+\s*([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*\("
    )
    assign_from_call = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*\(")

    brace_depth = 0
    in_ptr_function = False
    current_func_name: str | None = None
    locals_in_function: set[str] = set()
    dangling_pointer_funcs: set[str] = set()

    for lineno, line in enumerate(sanitized_lines, start=1):
        stripped = line.strip()

        if not in_ptr_function:
            start_match = func_start.match(stripped)
            if start_match:
                in_ptr_function = True
                current_func_name = start_match.group(1)
                locals_in_function = set()
                brace_depth = stripped.count("{") - stripped.count("}")
            continue

        decl_match = local_decl.match(stripped)
        if decl_match:
            locals_in_function.add(decl_match.group(1))

        ret_match = return_addr.search(stripped)
        if ret_match and ret_match.group(1) in locals_in_function:
            if current_func_name:
                dangling_pointer_funcs.add(current_func_name)
            issues.append(_make_issue(
                "DanglingPointer",
                "Returning address of a local variable creates a dangling pointer.",
                line=lineno,
                col=ret_match.start(1) + 1,
                snippet=original_lines[lineno - 1].strip(),
                suggestion="Return by value, allocate on heap safely, or pass storage from caller.",
            ))

        brace_depth += stripped.count("{") - stripped.count("}")
        if brace_depth <= 0:
            in_ptr_function = False
            current_func_name = None

    # Track pointers assigned from dangling-pointer-return functions and flag unsafe dereferences.
    derived_pointer_vars: set[str] = set()
    for lineno, line in enumerate(sanitized_lines, start=1):
        stripped = line.strip()

        decl_match = ptr_decl_from_call.search(stripped)
        if decl_match and decl_match.group(2) in dangling_pointer_funcs:
            derived_pointer_vars.add(decl_match.group(1))

        assign_match = assign_from_call.search(stripped)
        if assign_match and assign_match.group(2) in dangling_pointer_funcs:
            derived_pointer_vars.add(assign_match.group(1))

        for var_name in sorted(derived_pointer_vars):
            decl_pattern = re.compile(
                rf"\b(?:unsigned|signed|long|short|int|float|double|char|bool|size_t|auto|"
                rf"[A-Za-z_]\w*(?:::[A-Za-z_]\w*)?(?:<[^>]+>)?)\s*\*+\s*{re.escape(var_name)}\b"
            )
            if decl_pattern.search(stripped):
                continue

            deref_match = re.search(rf"\*\s*{re.escape(var_name)}\b", stripped)
            if not deref_match:
                continue

            issues.append(_make_issue(
                "DanglingPointer",
                "Dereferencing a pointer derived from invalid stack memory is undefined behavior.",
                line=lineno,
                col=deref_match.start() + 1,
                snippet=original_lines[lineno - 1].strip(),
                suggestion="Avoid dereferencing this pointer; fix the source function to return valid lifetime storage.",
            ))
            break

    return issues


def _collect_declared_names(code: str, language: str) -> set[str]:
    sanitized_lines = _strip_c_like_comments_and_strings(code).splitlines()
    declared = set()

    if language == "JavaScript":
        for line in sanitized_lines:
            for match in re.finditer(r"\b(?:let|const|var)\s+([A-Za-z_]\w*)", line):
                declared.add(match.group(1))
            for match in re.finditer(r"\bfunction\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", line):
                declared.add(match.group(1))
                params = [part.strip() for part in match.group(2).split(",") if part.strip()]
                declared.update(params)
            for match in re.finditer(r"\b([A-Za-z_]\w*)\s*=>", line):
                declared.add(match.group(1))
            for match in re.finditer(r"\(([^)]*)\)\s*=>", line):
                params = [part.strip() for part in match.group(1).split(",") if part.strip()]
                declared.update(params)
        return declared

    if language == "Java":
        type_pattern = (
            r"(?:byte|short|int|long|float|double|char|boolean|String(?:\[\])?|var|"
            r"ArrayList(?:<[^>]+>)?|List(?:<[^>]+>)?|Map(?:<[^>]+>)?|Set(?:<[^>]+>)?|"
            r"HashMap(?:<[^>]+>)?|HashSet(?:<[^>]+>)?|[A-Z][A-Za-z0-9_]*(?:<[^>]+>)?)"
        )
        for line in sanitized_lines:
            class_match = re.search(r"\bclass\s+([A-Za-z_]\w*)", line)
            if class_match:
                declared.add(class_match.group(1))
            for match in re.finditer(rf"\b{type_pattern}\s+([A-Za-z_]\w*)\b", line):
                declared.add(match.group(1))
            method_match = re.search(
                rf"\b(?:public|private|protected|static|final|abstract|synchronized|\s)+"
                rf"(?:void|{type_pattern})\s+([A-Za-z_]\w*)\s*\(([^)]*)\)",
                line,
            )
            if method_match:
                declared.add(method_match.group(1))
                params = re.findall(rf"\b{type_pattern}\s+([A-Za-z_]\w*)\b", method_match.group(2))
                declared.update(params)
        return declared

    if language in {"C", "C++"}:
        type_pattern = (
            r"(?:unsigned|signed|long|short|int|float|double|char|bool|void|size_t|"
            r"FILE|struct\s+[A-Za-z_]\w*|[A-Z][A-Za-z0-9_]*|[a-z_]\w*<[^>]+>|"
            r"[A-Za-z_]\w*::[A-Za-z_]\w*(?:<[^>]+>)?)"
        )
        ptr_type_pattern = rf"{type_pattern}(?:\s*\*+\s*)?"
        for line in sanitized_lines:
            function_match = re.search(rf"\b{ptr_type_pattern}\s*([A-Za-z_]\w*)\s*\(([^)]*)\)", line)
            if function_match:
                declared.add(function_match.group(1))
                params = re.findall(rf"\b{ptr_type_pattern}\s*([A-Za-z_]\w*)\b", function_match.group(2))
                declared.update(params)
            for match in re.finditer(rf"\b{ptr_type_pattern}\s*([A-Za-z_]\w*)\b", line):
                declared.add(match.group(1))
        return declared

    return declared


def _find_duplicate_definition_issues(code: str, language: str) -> list[dict]:
    if language != "JavaScript":
        return []
    seen = {}
    issues = []
    for lineno, line in enumerate(_strip_c_like_comments_and_strings(code).splitlines(), start=1):
        for match in re.finditer(r"\b(let|const)\s+([A-Za-z_]\w*)", line):
            name = match.group(2)
            if name in seen:
                issues.append(_make_issue(
                    "DuplicateDefinition",
                    f"{name} is declared multiple times in the same scope.",
                    line=lineno,
                    col=match.start(2) + 1,
                    snippet=code.splitlines()[lineno - 1].strip(),
                    suggestion="Rename or remove the duplicate declaration.",
                ))
            else:
                seen[name] = lineno
    return issues


def _find_undeclared_identifier_issues(code: str, language: str) -> list[dict]:
    declared = _collect_declared_names(code, language)
    sanitized_lines = _strip_c_like_comments_and_strings(code).splitlines()
    original_lines = code.splitlines()
    issues = []

    excluded = set(C_LIKE_KEYWORDS) | declared
    if language == "JavaScript":
        excluded |= JS_GLOBALS
    if language == "Java":
        excluded |= set(JAVA_IMPORT_HINTS)
        excluded |= {"System", "out", "println", "print", "main", "args"}
    if language in {"C", "C++"}:
        excluded |= C_STDIO_SYMBOLS | {"main", "NULL", "stdin", "stdout", "stderr", "size_t"}
    if language == "C++":
        excluded |= {"std", "cout", "cin", "endl", "vector", "map", "set", "string"}

    for lineno, line in enumerate(sanitized_lines, start=1):
        if language in {"C", "C++"} and line.strip().startswith("#include"):
            continue
        if language == "C++" and line.strip().startswith("using namespace"):
            continue
        if language == "Java" and line.strip().startswith("import "):
            continue
        for match in re.finditer(r"(?<!\.)\b([A-Za-z_]\w*)\b", line):
            name = match.group(1)
            if language == "JavaScript":
                tail = line[match.end(1):]
                if tail.lstrip().startswith(":"):
                    # Object literal key: { key: value }
                    continue
            if name in excluded:
                continue
            if language == "Java" and name[0].isupper():
                continue
            if match.start() > 0 and line[match.start() - 1] == "#":
                continue
            if re.search(rf"\b(?:let|const|var|function|class|interface|struct|enum)\s+{re.escape(name)}\b", line):
                continue
            if language in {"Java", "C", "C++"} and re.search(
                rf"\b(?:unsigned|signed|long|short|int|float|double|char|bool|boolean|String|void)(?:\s*\*+\s*)?\s*{re.escape(name)}\b",
                line,
            ):
                continue
            if language == "Java" and re.search(rf"\bnew\s+{re.escape(name)}\b", line):
                continue
            issues.append(_make_issue(
                "UndeclaredIdentifier",
                f"{name} is used before it is declared.",
                line=lineno,
                col=match.start(1) + 1,
                snippet=original_lines[lineno - 1].strip(),
                suggestion="Declare the identifier before use or fix the name.",
            ))
            break
    return issues


def _find_incomplete_assignment_issues(code: str, language: str) -> list[dict]:
    if language not in {"Java", "C", "C++", "JavaScript"}:
        return []
    issues = []
    original_lines = code.splitlines()

    for lineno, raw in enumerate(original_lines, start=1):
        line = raw.strip()
        if re.search(
            r"^(?:let|const|var|int|long|short|byte|float|double|char|bool|boolean|String)\s+[A-Za-z_]\w*\s*=\s*;\s*$",
            line,
        ):
            issues.append(_make_issue(
                "MissingDelimiter",
                "Assignment is missing a value expression.",
                line=lineno,
                col=1,
                snippet=line,
                suggestion="Provide a value on the right-hand side of '='.",
            ))
    return issues


def _find_invalid_member_access_issues(code: str, language: str) -> list[dict]:
    if language != "JavaScript":
        return []
    issues = []
    original_lines = code.splitlines()
    sanitized_lines = _strip_c_like_comments_and_strings(code).splitlines()

    for lineno, line in enumerate(sanitized_lines, start=1):
        for match in re.finditer(r"\.\.(?!\.)", line):
            issues.append(_make_issue(
                "MissingDelimiter",
                "Invalid member access syntax '..'.",
                line=lineno,
                col=match.start() + 1,
                snippet=original_lines[lineno - 1].strip(),
                suggestion="Use a single '.' for property access.",
            ))
            break
    return issues


def _collect_c_like_rule_based_issues(code: str, language: str) -> list[dict]:
    issues = []
    unclosed = _find_unclosed_string_issue(code)
    if unclosed:
        issues.append(unclosed)

    issues.extend(_find_unmatched_bracket_issues(code))
    issues.extend(_find_missing_semicolon_issues(code, language))
    issues.extend(_find_incomplete_assignment_issues(code, language))
    issues.extend(_find_invalid_member_access_issues(code, language))

    # Semantic checks remain useful even when the ML bundle is unavailable.
    issues.extend(_find_type_mismatch_issues(code, language))
    issues.extend(_find_missing_import_issues(code, language))
    issues.extend(_find_missing_include_issues(code, language))
    issues.extend(_find_duplicate_definition_issues(code, language))
    issues.extend(_find_undeclared_identifier_issues(code, language))
    issues.extend(_find_dangling_pointer_return_issues(code, language))
    issues.extend(_find_division_by_zero_issues(code))
    issues.extend(_find_infinite_loop_issues(code))
    issues.extend(_find_unreachable_code_issues(code))
    issues = _suppress_cascading_syntax_noise(issues)
    return _normalize_rule_issues(issues)

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
            wildcard_issue = _find_python_wildcard_import_issue(code)
            if wildcard_issue:
                return _attach_metadata({
                    "language": language,
                    "predicted_error": "WildcardImport",
                    "confidence": 1.0,
                    "tutor": explain_error("WildcardImport"),
                    "rule_based_issues": [wildcard_issue],
                }, warnings)

            mutable_match = re.search(
                r"def\s+\w+\s*\([^)]*=\s*(\[\]|\{\}|set\(|dict\(|list\()",
                code,
            )
            if mutable_match:
                line_num = code[:mutable_match.start()].count("\n") + 1
                return _attach_metadata({
                    "language": language,
                    "predicted_error": "MutableDefault",
                    "confidence": 1.0,
                    "tutor": explain_error("MutableDefault"),
                    "rule_based_issues": [
                        {
                            "type": "MutableDefault",
                            "line": line_num,
                            "col": 1,
                            "message": "Mutable default argument can leak state across calls.",
                            "snippet": code.splitlines()[line_num - 1].strip() if code.splitlines() else "",
                            "suggestion": "Use None as default and initialize the mutable object inside the function.",
                        }
                    ],
                }, warnings)

            name_issue = _find_python_name_error_issue(code)
            if name_issue:
                return _attach_metadata({
                    "language": language,
                    "predicted_error": "NameError",
                    "confidence": 1.0,
                    "tutor": explain_error("NameError"),
                    "rule_based_issues": [name_issue],
                }, warnings)

            # Still check for semantic/runtime errors via ML.
            if _should_run_semantic_ml(code, language):
                semantic = _ml_semantic_check(code, language, [], warnings)
                if semantic:
                    return _attach_metadata(semantic, warnings)
                    
            # Fallback for Python DivisionByZero if ML is missing/offline
            div_match = re.search(r"[/%]\s*0(\.0+)?\b", code)
            if div_match:
                line_num = code[:div_match.start()].count("\n") + 1
                line_text = code.splitlines()[line_num - 1] if code.splitlines() else ""
                col_num = div_match.start() - code.rfind("\n", 0, div_match.start())
                rule_based_issues.append({
                    "type": "DivisionByZero",
                    "line": line_num,
                    "col": col_num,
                    "message": "Division by zero detected",
                    "snippet": line_text.strip(),
                    "suggestion": "Guard the denominator or change it to a non-zero value.",
                })
                return _attach_metadata({
                    "language": language,
                    "predicted_error": "DivisionByZero",
                    "confidence": 1.0,
                    "tutor": explain_error("DivisionByZero"),
                    "rule_based_issues": rule_based_issues
                }, warnings)
                
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
            rb_error = str(strong_issues[0].get("type") or "SyntaxError")

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
    # JAVA / C / C++ / JAVASCRIPT
    # =========================================================================
    elif language in ["Java", "C", "C++", "JavaScript"]:

        rule_based_issues = _collect_c_like_rule_based_issues(code, language)
        syntax_issues = [issue for issue in rule_based_issues if issue.get("type") in RULE_BASED_TYPES]
        semantic_issues = [issue for issue in rule_based_issues if issue.get("type") in SEMANTIC_ERROR_TYPES]

        if syntax_issues:
            primary_issue = _pick_primary_issue(syntax_issues)
            primary_type = str(primary_issue.get("type") or "SyntaxError") if primary_issue else "SyntaxError"
            return _attach_metadata({
                "language": language,
                "predicted_error": primary_type,
                "confidence": 1.0,
                "tutor": explain_error(primary_type),
                "rule_based_issues": rule_based_issues
            }, warnings)

        if semantic_issues:
            primary_issue = _pick_primary_issue(semantic_issues)
            primary_type = str(primary_issue.get("type") or "NoError") if primary_issue else "NoError"
            return _attach_metadata({
                "language": language,
                "predicted_error": primary_type,
                "confidence": 1.0,
                "tutor": explain_error(primary_type),
                "rule_based_issues": rule_based_issues
            }, warnings)

        if _should_run_semantic_ml(code, language):
            semantic = _ml_semantic_check(code, language, [], warnings)
            if semantic:
                return _attach_metadata(semantic, warnings)
        return _attach_metadata({
            "language": language,
            "predicted_error": "NoError",
            "confidence": 1.0,
            "tutor": {
                "why": "No syntax or rule-based semantic issue was detected in this snippet.",
                "fix": "No direct fix is required from static checks; run or test the program to validate runtime behavior."
            },
            "rule_based_issues": []
        }, warnings)

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
            # Rule-based infinite-loop check (authoritative for all C-like langs + JS)
            if _has_infinite_loop(code):
                return _attach_metadata({
                    "language": language,
                    "predicted_error": "InfiniteLoop",
                    "confidence": 1.0,
                    "tutor": explain_error("InfiniteLoop"),
                    "rule_based_issues": []
                }, warnings)

            # Structurally valid — check for semantic errors via ML
            if _should_run_semantic_ml(code, language):
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

        if has_unbalanced:
            return _attach_metadata({
                "language": language,
                "predicted_error": "UnmatchedBracket",
                "confidence": 1.0,
                "tutor": explain_error("UnmatchedBracket"),
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
