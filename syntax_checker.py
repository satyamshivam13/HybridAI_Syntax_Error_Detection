import ast
import re
import tokenize
import io
from typing import List, Dict, Any, Tuple


def try_ast_parse(code: str) -> Tuple[bool, Any]:
    """Try parsing code with AST to detect syntax errors."""
    try:
        ast.parse(code)
        return True, None
    except Exception as e:
        return False, e


def detect_unclosed_quotes(code: str) -> List[Dict[str, Any]]:
    """Detect unclosed or unterminated string quotes safely, even when indentation is invalid."""
    issues = []
    try:
        import io, tokenize

        try:
            # Try tokenizing — any bad indentation or string will raise an error
            _ = list(tokenize.generate_tokens(io.StringIO(code).readline))
        except (tokenize.TokenError, IndentationError, SyntaxError) as e:
            msg = str(e)
            issues.append({
                "type": "UnclosedQuotes",
                "message": msg if msg else "Tokenizer failed — possible unterminated string or indentation issue.",
                "line": None,
                "suggestion": "Check for missing quotes or inconsistent indentation."
            })
        except Exception as e:
            # Absolute fallback for any unknown tokenizer failure
            issues.append({
                "type": "UnclosedQuotes",
                "message": f"Tokenizer crash: {e}",
                "line": None,
                "suggestion": "Check quotes and indentation."
            })
    except Exception as e:
        # Final global fail-safe
        issues.append({
            "type": "UnclosedQuotes",
            "message": f"Unexpected error: {e}",
            "line": None,
            "suggestion": "Unexpected parsing issue while checking quotes."
        })
    return issues


def detect_unmatched_brackets(code: str) -> List[Dict[str, Any]]:
    """Detect missing or extra brackets/parentheses."""
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    issues = []
    for lineno, line in enumerate(code.splitlines(), start=1):
        for col, ch in enumerate(line, start=1):
            if ch in "([{":
                stack.append((ch, lineno, col))
            elif ch in ")]}":
                if not stack:
                    issues.append({
                        "type": "UnmatchedBracket",
                        "message": f"Found closing {ch} without opening bracket.",
                        "line": lineno,
                        "col": col,
                        "suggestion": "Remove the extra closing bracket or add matching opening bracket."
                    })
                else:
                    top, tline, tcol = stack[-1]
                    if top == pairs[ch]:
                        stack.pop()
                    else:
                        issues.append({
                            "type": "UnmatchedBracket",
                            "message": f"Bracket mismatch: found {ch} but last opening is {top}.",
                            "line": lineno,
                            "col": col,
                            "suggestion": "Fix the matching bracket types."
                        })
    # If any opening bracket is left unmatched
    for (ch, lineno, col) in stack:
        issues.append({
            "type": "UnmatchedBracket",
            "message": f"Opening {ch} at line {lineno} has no matching closing bracket.",
            "line": lineno,
            "col": col,
            "suggestion": f"Add a closing bracket for {ch}."
        })
    return issues


def detect_missing_colon(code: str) -> List[Dict[str, Any]]:
    """Detect lines missing colon after control or function definitions."""
    issues = []
    keywords = ['def ', 'class ', 'if ', 'elif ', 'else', 'for ', 'while ', 'try', 'except', 'with ']
    for lineno, raw in enumerate(code.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        code_part = line.split('#', 1)[0].rstrip()
        for kw in keywords:
            if code_part.startswith(kw) or re.match(rf'^{kw[:-1]}\b', code_part):
                if not code_part.endswith(':'):
                    issues.append({
                        "type": "MissingColon",
                        "message": f"Probable missing ':' after statement starting with '{kw.strip()}'",
                        "line": lineno,
                        "snippet": raw.strip(),
                        "suggestion": "Add a ':' at the end of this line."
                    })
                break
    return issues


def detect_indentation_errors(code: str) -> List[Dict[str, Any]]:
    """Detect indentation problems using compile()."""
    issues = []
    try:
        compile(code, '<string>', 'exec')
    except IndentationError as e:
        issues.append({
            "type": "IndentationError",
            "message": str(e),
            "line": getattr(e, 'lineno', None),
            "suggestion": "Check indentation levels (use consistent tabs/spaces; prefer 4 spaces)."
        })
    except SyntaxError:
        # Skip non-indentation syntax errors
        pass
    return issues


def classify_syntax_error(exc: Exception) -> Dict[str, Any]:
    """Convert a SyntaxError or Exception from AST parsing into user-friendly info."""
    msg = str(exc)
    info = {
        "raw": msg,
        "type": "SyntaxError",
        "line": getattr(exc, 'lineno', None),
        "message": msg,
        "suggestion": None
    }

    if isinstance(exc, SyntaxError):
        text = exc.msg.lower() if hasattr(exc, 'msg') else msg.lower()
        if 'expected' in text and ':' in text:
            info["type"] = "MissingColon"
            info["suggestion"] = "Check for missing ':' after function/if/for/while/with/try/except/else."
        elif 'eof while scanning string literal' in text or 'unterminated string' in text:
            info["type"] = "UnclosedQuotes"
            info["suggestion"] = "It looks like a string wasn't closed properly."
        elif 'unexpected indent' in text or 'unindent does not match' in text:
            info["type"] = "IndentationError"
            info["suggestion"] = "Fix indentation (consistent spaces/tabs)."
        elif 'parenthesis' in text or 'closing parenthesis' in text:
            info["type"] = "UnmatchedBracket"
            info["suggestion"] = "Check parentheses/brackets."
    return info


def detect_all(code: str) -> List[Dict[str, Any]]:
    """Run all detectors and return combined list of issues."""
    issues = []
    issues += detect_unclosed_quotes(code)
    issues += detect_unmatched_brackets(code)
    issues += detect_missing_colon(code)
    issues += detect_indentation_errors(code)

    ok, exc = try_ast_parse(code)
    if not ok and exc is not None:
        sp = classify_syntax_error(exc)
        # Avoid duplicates
        if all(sp.get("message") != i.get("message") for i in issues):
            issues.append(sp)

    normalized = []
    for it in issues:
        normalized.append({
            "type": it.get("type"),
            "message": it.get("message"),
            "line": it.get("line"),
            "col": it.get("col"),
            "snippet": it.get("snippet"),
            "suggestion": it.get("suggestion")
        })

    def lineno_key(x):
        return (x['line'] if x['line'] is not None else 9999)

    return sorted(normalized, key=lineno_key)
