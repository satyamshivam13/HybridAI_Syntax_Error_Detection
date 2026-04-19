"""Typed semantic static analysis pipeline for OmniSyntax."""

from __future__ import annotations

import ast
import builtins
import importlib.util
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .language_detector import detect_language
from .ml_engine import get_model_status, is_model_available
from .syntax_checker import detect_all
from .tutor_explainer import explain_error


class ValueState(str, Enum):
    ZERO = "Zero"
    NONZERO = "NonZero"
    UNKNOWN = "Unknown"
    MAYBE_ZERO = "MaybeZero"


class ResolveState(str, Enum):
    RESOLVED = "Resolved"
    MISSING = "Missing"
    UNKNOWN = "Unknown"
    AMBIGUOUS = "Ambiguous"


@dataclass(frozen=True)
class ValueFact:
    state: ValueState
    constant: Any = None


@dataclass
class IRStatement:
    kind: str
    language: str
    raw: str
    line: int
    name: str | None = None
    target_type: str | None = None
    expression: str | None = None
    condition: str | None = None
    module: str | None = None
    symbol: str | None = None
    jump_kind: str | None = None
    scope_depth: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IRProgram:
    language: str
    code: str
    filename: str | None
    statements: list[IRStatement] = field(default_factory=list)
    syntax_issues: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Symbol:
    name: str
    kind: str
    line: int
    type_name: str | None = None
    value: ValueFact = field(default_factory=lambda: ValueFact(ValueState.UNKNOWN))
    imported_from: str | None = None


@dataclass
class SymbolTable:
    language: str
    symbols: dict[str, Symbol] = field(default_factory=dict)
    imports: set[str] = field(default_factory=set)
    includes: set[str] = field(default_factory=set)

    def declare(self, symbol: Symbol) -> bool:
        existed = symbol.name in self.symbols and symbol.kind in {"function", "class"}
        self.symbols[symbol.name] = symbol
        return not existed

    def value_of(self, name: str) -> ValueFact:
        return self.symbols.get(name, Symbol(name, "unknown", 0)).value


@dataclass
class Evidence:
    kind: str
    strength: float
    ambiguity: float = 0.0


@dataclass
class AnalysisIssue:
    type: str
    message: str
    line: int | None = None
    col: int | None = 1
    snippet: str | None = None
    suggestion: str | None = None
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "message": self.message,
            "line": self.line,
            "col": self.col,
            "snippet": self.snippet,
            "suggestion": self.suggestion,
            "confidence": self.confidence,
            "evidence": [e.__dict__ for e in self.evidence],
        }


@dataclass(frozen=True)
class DetectionAnalysis:
    language: str
    program: IRProgram
    symbols: SymbolTable
    issues: list[AnalysisIssue]
    primary: AnalysisIssue | None
    degraded_mode: bool
    warnings: list[str]
    pipeline: list[str]

    def to_single_result(self) -> dict[str, Any]:
        issues = [issue.as_dict() for issue in self.issues]
        if self.primary:
            predicted = self.primary.type
            confidence = self.primary.confidence
            tutor = explain_error(predicted)
        else:
            predicted = "NoError"
            confidence = ConfidenceCalibrator().no_error(self.program)
            tutor = {
                "why": "No semantic or structural issue was detected.",
                "fix": "No direct fix is required.",
            }
        return {
            "language": self.language,
            "predicted_error": predicted,
            "primary_error": issues[0] if issues else None,
            "confidence": confidence,
            "tutor": tutor,
            "rule_based_issues": issues,
            "errors": issues,
            "degraded_mode": self.degraded_mode,
            "warnings": self.warnings,
            "analysis_pipeline": self.pipeline,
            "confidence_model": {
                "kind": "evidence_calibrated",
                "constant_output": False,
                "value_states": [state.value for state in ValueState],
            },
        }

    def to_grouped_result(self) -> dict[str, Any]:
        single = self.to_single_result()
        grouped: dict[str, dict[str, Any]] = {}
        for issue in single.get("errors", []):
            kind = issue["type"]
            grouped.setdefault(
                kind,
                {
                    "type": kind,
                    "count": 0,
                    "locations": [],
                    "confidence": issue.get("confidence", 0.0),
                    "tutor": explain_error(kind),
                },
            )
            grouped[kind]["count"] += 1
            grouped[kind]["confidence"] = max(grouped[kind]["confidence"], issue.get("confidence", 0.0))
            grouped[kind]["locations"].append(
                {
                    "line": issue.get("line"),
                    "col": issue.get("col"),
                    "message": issue.get("message"),
                    "suggestion": issue.get("suggestion"),
                    "snippet": issue.get("snippet"),
                    "confidence": issue.get("confidence"),
                }
            )
        errors = list(grouped.values())
        return {
            "language": single["language"],
            "errors": errors,
            "primary_error": single.get("primary_error"),
            "errors_by_type": {
                err["type"]: [
                    {
                        "line": loc.get("line", 0),
                        "message": loc.get("message", f"{err['type']} detected"),
                        "snippet": loc.get("snippet", ""),
                    }
                    for loc in err.get("locations", [])
                ]
                for err in errors
            },
            "total_errors": sum(err["count"] for err in errors),
            "has_errors": bool(errors),
            "rule_based_issues": single.get("errors", []),
            "degraded_mode": single.get("degraded_mode", False),
            "warnings": single.get("warnings", []),
            "analysis_pipeline": single.get("analysis_pipeline", []),
            "confidence_model": single.get("confidence_model", {}),
        }


PRIORITY = [
    "UnclosedString",
    "UnmatchedBracket",
    "MissingDelimiter",
    "IndentationError",
    "TypeMismatch",
    "InvalidAssignment",
    "WildcardImport",
    "MissingImport",
    "ImportError",
    "MissingInclude",
    "UndeclaredIdentifier",
    "NameError",
    "DuplicateDefinition",
    "DanglingPointer",
    "DivisionByZero",
    "UnreachableCode",
    "InfiniteLoop",
    "MutableDefault",
    "UnusedVariable",
    "LineTooLong",
]

PY_BUILTINS = set(dir(builtins))
PY_ALIASES = {"np": "numpy", "pd": "pandas", "plt": "matplotlib.pyplot"}
JAVA_TYPES = {
    "ArrayList": "java.util.ArrayList",
    "LinkedList": "java.util.LinkedList",
    "List": "java.util.List",
    "Map": "java.util.Map",
    "HashMap": "java.util.HashMap",
    "Set": "java.util.Set",
    "HashSet": "java.util.HashSet",
    "Scanner": "java.util.Scanner",
}
C_SYMBOLS = {
    "printf": "stdio.h",
    "fprintf": "stdio.h",
    "stdout": "stdio.h",
    "stderr": "stdio.h",
    "FILE": "stdio.h",
    "malloc": "stdlib.h",
    "free": "stdlib.h",
    "strlen": "string.h",
    "strcmp": "string.h",
    "sqrt": "math.h",
}
CPP_SYMBOLS = {**C_SYMBOLS, "cout": "iostream", "cin": "iostream", "cerr": "iostream", "endl": "iostream", "vector": "vector", "size_t": "vector"}
JS_GLOBALS = {"console", "Math", "Number", "String", "Boolean", "Array", "Object", "JSON", "Promise", "Error", "undefined", "NaN", "Infinity"}
KEYWORDS = {
    "if", "else", "for", "while", "switch", "case", "do", "break", "continue",
    "return", "throw", "try", "catch", "finally", "new", "class", "public",
    "private", "protected", "static", "final", "void", "package", "import",
    "namespace", "using", "struct", "enum", "typedef", "sizeof", "const",
    "volatile", "unsigned", "signed", "long", "short", "int", "float",
    "double", "char", "bool", "boolean", "String", "string", "var", "let",
    "function", "true", "false", "null", "nullptr",
}


def _norm_type(kind: str | None) -> str:
    if kind == "UnclosedQuotes":
        return "UnclosedString"
    if kind == "MissingColon":
        return "MissingDelimiter"
    return kind or "SyntaxError"


def _snippet(code: str, line: int | None) -> str:
    lines = code.splitlines()
    if line and 1 <= line <= len(lines):
        return lines[line - 1].strip()
    return ""


def _safe_source_segment(code: str, node: ast.AST | None) -> str | None:
    if node is None:
        return None
    return ast.get_source_segment(code, node)


def _issue(program: IRProgram, kind: str, msg: str, line: int | None, strength: float, *, col: int | None = 1, suggestion: str | None = None, ambiguity: float = 0.0, evidence: str = "semantic") -> AnalysisIssue:
    return AnalysisIssue(_norm_type(kind), msg, line, col, _snippet(program.code, line), suggestion, [Evidence(evidence, strength, ambiguity)])


def _strip_comments(code: str) -> str:
    code = re.sub(r"//.*", lambda m: " " * len(m.group(0)), code)
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), code, flags=re.S)


def _string_start(code: str) -> tuple[int, int] | None:
    line = 1
    col = 0
    quote = None
    start = (1, 1)
    escaped = False
    for ch in code:
        if ch == "\n":
            if quote in {"'", '"'}:
                return start
            line += 1
            col = 0
            escaped = False
            continue
        col += 1
        if escaped:
            escaped = False
            continue
        if ch == "\\" and quote:
            escaped = True
            continue
        if ch in {"'", '"', "`"}:
            if quote == ch:
                quote = None
            elif not quote:
                quote = ch
                start = (line, col)
    return start if quote else None


def _bracket_issues(code: str) -> list[dict[str, int]]:
    clean = re.sub(r"(['\"`])(?:\\.|(?!\1).)*\1", " ", _strip_comments(code))
    stack: list[tuple[str, int, int]] = []
    pairs = {")": "(", "]": "[", "}": "{"}
    issues: list[dict[str, int]] = []
    line = 1
    col = 0
    for ch in clean:
        if ch == "\n":
            line += 1
            col = 0
            continue
        col += 1
        if ch in "([{":
            stack.append((ch, line, col))
        elif ch in ")]}":
            if not stack or stack[-1][0] != pairs[ch]:
                issues.append({"line": line, "col": col})
            else:
                stack.pop()
    issues.extend({"line": line, "col": col} for _, line, col in stack)
    return issues


def _target_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, (ast.Tuple, ast.List)):
        return ",".join(_target_name(x) or "?" for x in node.elts)
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _annotation(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _annotation(node.value)
    return None


class Parser:
    def parse(self, code: str, language: str, filename: str | None = None) -> IRProgram:
        return self._python(code, filename) if language == "Python" else self._c_like(code, language, filename)

    def _python(self, code: str, filename: str | None) -> IRProgram:
        program = IRProgram("Python", code, filename)
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            msg = str(exc).lower()
            # Syntax-level assignment target failures are surfaced as InvalidAssignment
            # so assignment shape semantics stay stable under parser perturbations.
            if "cannot assign to" in msg:
                program.syntax_issues.append({
                    "type": "InvalidAssignment",
                    "message": "Assignment target is not writable.",
                    "line": getattr(exc, "lineno", 1) or 1,
                    "col": getattr(exc, "offset", 1) or 1,
                    "suggestion": "Assign to a variable, attribute, or indexed target.",
                })
            if "was never closed" in msg or "does not match opening" in msg:
                program.syntax_issues.append({
                    "type": "UnmatchedBracket",
                    "message": "Bracket structure is not balanced.",
                    "line": getattr(exc, "lineno", 1) or 1,
                    "col": getattr(exc, "offset", 1) or 1,
                    "suggestion": "Add or remove the matching bracket.",
                })
            for raw in detect_all(code):
                program.syntax_issues.append({"type": _norm_type(raw.get("type")), "message": raw.get("message"), "line": raw.get("line"), "col": raw.get("col") or 1, "suggestion": raw.get("suggestion")})
            return program
        for node in ast.walk(tree):
            raw = ast.get_source_segment(code, node) or ""
            if isinstance(node, ast.Import):
                for alias in node.names:
                    program.statements.append(IRStatement("import", "Python", raw, node.lineno, name=alias.asname or alias.name.split(".")[0], module=alias.name))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    program.statements.append(IRStatement("import", "Python", raw, node.lineno, name=alias.asname or alias.name, module=node.module or "", symbol=alias.name))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                program.statements.append(IRStatement("definition", "Python", raw, node.lineno, name=node.name, target_type="function", metadata={"node": node}))
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                target = node.targets[0] if isinstance(node, ast.Assign) and node.targets else getattr(node, "target", None)
                value = getattr(node, "value", None)
                expr = _safe_source_segment(code, value if isinstance(value, ast.AST) else None)
                program.statements.append(IRStatement("assignment", "Python", raw, node.lineno, name=_target_name(target) if target else None, target_type=_annotation(getattr(node, "annotation", None)), expression=expr, metadata={"node": node}))
            elif isinstance(node, ast.While):
                program.statements.append(IRStatement("loop", "Python", raw, node.lineno, condition=ast.get_source_segment(code, node.test) or "", metadata={"node": node}))
            elif isinstance(node, ast.For):
                cond = f"{ast.get_source_segment(code, node.iter) or 'iter'}"
                program.statements.append(IRStatement("loop", "Python", raw, node.lineno, condition=cond, metadata={"node": node}))
            elif isinstance(node, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                jump_value = getattr(node, "value", None)
                jump_expr = _safe_source_segment(code, jump_value if isinstance(jump_value, ast.AST) else None)
                program.statements.append(IRStatement("jump", "Python", raw, node.lineno, expression=jump_expr, jump_kind=node.__class__.__name__.lower(), metadata={"node": node}))
        program.statements.sort(key=lambda s: (s.line, s.kind))
        return program

    def _c_like(self, code: str, language: str, filename: str | None) -> IRProgram:
        program = IRProgram(language, code, filename)
        start = _string_start(code)
        if start:
            program.syntax_issues.append({"type": "UnclosedString", "message": "String literal is not closed.", "line": start[0], "col": start[1], "suggestion": "Add the missing closing quote."})
            return program
        for raw in _bracket_issues(code):
            program.syntax_issues.append({"type": "UnmatchedBracket", "message": "Bracket structure is not balanced.", "line": raw["line"], "col": raw["col"], "suggestion": "Add or remove the matching bracket."})
        clean = _strip_comments(code)
        if language in {"C", "C++", "Java"}:
            for lineno, line in enumerate(clean.splitlines(), 1):
                stripped = line.strip()
                if _line_missing_delimiter(stripped):
                    program.syntax_issues.append({"type": "MissingDelimiter", "message": "Statement appears to be missing a delimiter.", "line": lineno, "col": max(1, len(line.rstrip())), "suggestion": "Add the required semicolon."})
        for lineno, line in enumerate(clean.splitlines(), 1):
            match = re.search(r"#include\s*[<\"]([^>\"]+)[>\"]", line)
            if match:
                program.statements.append(IRStatement("include", language, line.strip(), lineno, module=match.group(1)))
        clean = re.sub(r"^\s*#include[^\n]*", "", clean, flags=re.M)
        clean = re.sub(r"=\s*\{[^{}]*\}", "= ARRAY", clean)
        if language == "JavaScript":
            clean = clean.replace("= ARRAY", "= OBJECT")
            normalized_lines: list[str] = []
            for raw_line in clean.splitlines():
                stripped = raw_line.strip()
                if (
                    stripped
                    and not stripped.endswith((";", "{", "}"))
                    and not re.match(r"^(if|for|while|switch|catch|else|function)\b", stripped)
                ):
                    raw_line = raw_line.rstrip() + ";"
                normalized_lines.append(raw_line)
            clean = "\n".join(normalized_lines)
        for raw, line, depth, closed, block_id in self._split(clean):
            stmt = self._classify(raw, line, depth, closed, language)
            if stmt:
                stmt.metadata.setdefault("block_id", block_id)
                program.statements.append(stmt)
        program.statements.sort(key=lambda s: (s.line, s.scope_depth))
        return program

    def _split(self, code: str) -> list[tuple[str, int, int, str, int]]:
        out: list[tuple[str, int, int, str, int]] = []
        buf: list[str] = []
        line = 1
        start_line = 1
        depth = 0
        stmt_depth = 0
        block_stack = [0]
        next_block = 1
        parens = 0
        quote = None
        escaped = False

        def flush(closed: str) -> None:
            nonlocal buf, start_line, stmt_depth
            raw = "".join(buf).strip()
            if raw:
                out.append((raw, start_line, stmt_depth, closed, block_stack[-1]))
            buf = []
            start_line = line
            stmt_depth = depth

        for ch in code:
            if ch == "\n":
                line += 1
            if not buf and ch.isspace():
                continue
            if not buf and not ch.isspace():
                start_line = line
                stmt_depth = depth
            if escaped:
                escaped = False
                buf.append(ch)
                continue
            if ch == "\\" and quote:
                escaped = True
                buf.append(ch)
                continue
            if ch in {"'", '"', "`"}:
                quote = None if quote == ch else ch if not quote else quote
                buf.append(ch)
                continue
            if quote:
                buf.append(ch)
                continue
            parens += 1 if ch == "(" else -1 if ch == ")" and parens else 0
            if ch == "{" and parens == 0:
                flush("{")
                depth += 1
                block_stack.append(next_block)
                next_block += 1
                start_line = line
                stmt_depth = depth
                continue
            if ch == "}" and parens == 0:
                flush("}")
                depth = max(0, depth - 1)
                if len(block_stack) > 1:
                    block_stack.pop()
                start_line = line
                stmt_depth = depth
                continue
            if ch == ";" and parens == 0:
                flush(";")
                continue
            buf.append(ch)
        flush("eof")
        return out

    def _classify(self, raw: str, line: int, depth: int, closed: str, language: str) -> IRStatement | None:
        compact = " ".join(raw.split())
        if not compact:
            return None
        if re.match(r"^(return|throw|break|continue)\b", compact):
            kind = compact.split()[0]
            return IRStatement("jump", language, raw, line, expression=compact[len(kind):].strip(), jump_kind=kind, scope_depth=depth)
        if language == "Java" and compact.startswith("import "):
            module = compact.removeprefix("import ").strip()
            return IRStatement("import", language, raw, line, name=module.split(".")[-1], module=module, scope_depth=depth)
        if language == "Java" and re.match(r"^(?:public\s+)?class\s+([A-Za-z_]\w*)$", compact):
            name = compact.split()[-1]
            return IRStatement("definition", language, raw, line, name=name, target_type="class", scope_depth=depth)
        if language == "JavaScript" and re.match(r"^(?:let|const|var)\s+[A-Za-z_]\w*\s*=$", compact):
            return IRStatement("syntax", language, raw, line, scope_depth=depth, metadata={"issue": "MissingDelimiter"})
        if language == "JavaScript" and ".." in compact:
            return IRStatement("syntax", language, raw, line, scope_depth=depth, metadata={"issue": "MissingDelimiter"})
        loop = re.search(r"\bwhile\s*\((.*)\)\s*$", compact)
        if loop:
            return IRStatement("loop", language, raw, line, condition=loop.group(1), scope_depth=depth)
        loop = re.search(r"\bfor\s*\((.*)\)\s*$", compact)
        if loop:
            parts = [p.strip() for p in loop.group(1).split(";")]
            return IRStatement("loop", language, raw, line, condition=(parts[1] if len(parts) > 1 and parts[1] else "true"), scope_depth=depth, metadata={"init": parts[0] if parts else ""})
        fn = re.search(r"(?:^|\s)(?:(?:[\w:<>\[\]]+\s*[*&]?\s+)+)([A-Za-z_]\w*)\s*\(([^)]*)\)\s*$", compact)
        js_fn = re.search(r"\bfunction\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", compact) if language == "JavaScript" else None
        if (fn or js_fn) and "=" not in compact and not compact.startswith(("if", "for", "while", "switch", "catch")) and "<<" not in compact and ">>" not in compact and not compact.startswith(("System.", "console.")):
            m = fn or js_fn
            if m is None:
                return None
            return IRStatement("definition", language, raw, line, name=m.group(1), target_type="function", scope_depth=depth, metadata={"params": m.group(2)})
        dec = _declaration(compact, language)
        if dec:
            typ, name, expr = dec
            if expr and (
                (re.search(r"\b[A-Za-z_]\w*\s*\(", expr) and re.search(r"^\s*[-+]?\d+(?:\.\d+)?\s+\w", expr))
                or re.search(r"\)\s+[A-Za-z_]\w*", expr)
                or re.search(r"\b\d+\s+[A-Za-z_]\w*", expr)
                or ("<<" in expr and not re.search(r"[;{}]", expr))
            ):
                return IRStatement("syntax", language, raw, line, scope_depth=depth, metadata={"issue": "MissingDelimiter"})
            return IRStatement("assignment", language, raw, line, name=name, target_type=typ, expression=expr, scope_depth=depth, metadata={"declaration": True, "final": bool(re.search(r"\bfinal\b", compact))})
        assign = re.match(r"^([A-Za-z_]\w*)\s*([+\-*/%]?=)\s*(.+)$", compact)
        if assign:
            return IRStatement("assignment", language, raw, line, name=assign.group(1), expression=assign.group(3), scope_depth=depth, metadata={"operator": assign.group(2)})
        if re.match(r"^(?:[-+]?\d+|['\"`].*['\"`]|\([^)]*\))\s*=", compact):
            return IRStatement("syntax", language, raw, line, scope_depth=depth, metadata={"issue": "InvalidAssignment"})
        if language in {"C", "C++", "Java"} and closed != ";" and re.search(r"\b(int|double|float|char|String|boolean|return|printf|System\.out)\b", compact):
            return IRStatement("syntax", language, raw, line, scope_depth=depth, metadata={"issue": "MissingDelimiter"})
        return IRStatement("expr", language, raw, line, expression=compact, scope_depth=depth)


def _declaration(raw: str, language: str) -> tuple[str, str, str | None] | None:
    if language == "JavaScript":
        m = re.match(r"^(?:let|const|var)\s+([A-Za-z_]\w*)\s*(?:=\s*(.+))?$", raw)
        return ("var", m.group(1), m.group(2)) if m else None
    m = re.match(r"^(?:(?:public|private|protected|static|final|const|unsigned|signed|long|short)\s+)*([A-Za-z_][\w\.:<>\[\]]*(?:\s*[*&])?)\s+([A-Za-z_]\w*)\s*(?:=\s*(.+))?$", raw)
    if not m or m.group(2) in KEYWORDS:
        return None
    return (" ".join(m.group(1).split()), m.group(2), m.group(3))


def _line_missing_delimiter(stripped: str) -> bool:
    if not stripped or stripped.startswith(("//", "/*", "*", "#")):
        return False
    if stripped.endswith((";", "{", "}", ":")):
        return False
    if re.match(r"^(if|for|while|switch|catch|else|do|class|public class)\b", stripped):
        return False
    if "<<" in stripped:
        return True
    return bool(re.match(r"^(?:[\w:<>\[\]]+\s+[*&]?[\w]+|return\b|System\.out|printf\b|std::cout|std::cerr)", stripped))


class ExpressionEvaluator:
    def evaluate(self, expression: str | None, symbols: SymbolTable) -> ValueFact:
        if not expression:
            return ValueFact(ValueState.UNKNOWN)
        expr = self._normalize(expression)
        try:
            node = ast.parse(expr, mode="eval").body
        except SyntaxError:
            if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", expr):
                value = float(expr) if "." in expr else int(expr)
                return ValueFact(ValueState.ZERO if value == 0 else ValueState.NONZERO, value)
            if re.fullmatch(r"[A-Za-z_]\w*", expr):
                return symbols.value_of(expr)
            return ValueFact(ValueState.UNKNOWN)
        return self._eval(node, symbols)

    def denominator_states(self, expression: str | None, symbols: SymbolTable) -> list[ValueFact]:
        if not expression:
            return []
        try:
            node = ast.parse(self._normalize(expression), mode="eval").body
        except SyntaxError:
            return []
        states: list[ValueFact] = []

        def walk(item: ast.AST) -> None:
            if isinstance(item, ast.BinOp) and isinstance(item.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                states.append(self._eval(item.right, symbols))
            for child in ast.iter_child_nodes(item):
                walk(child)

        walk(node)
        return states

    def _normalize(self, expression: str) -> str:
        expr = expression.strip().rstrip(";")
        expr = re.sub(r"\btrue\b", "True", expr, flags=re.I)
        expr = re.sub(r"\bfalse\b", "False", expr, flags=re.I)
        expr = re.sub(r"\b(null|nullptr|undefined)\b", "None", expr)
        expr = expr.replace("&&", " and ").replace("||", " or ")
        expr = re.sub(r"(?<![=!<>])!(?!=)", " not ", expr)
        expr = re.sub(r"\([A-Za-z_][\w:<>\[\]]*\)", "", expr)
        expr = re.sub(r"\bnew\s+[A-Za-z_][\w:<>]*\s*", "", expr)
        expr = re.sub(r"([A-Za-z_]\w*)\s*\[[^\]]*\]", r"\1", expr)
        expr = expr.replace("std::", "")
        return expr

    def _eval(self, node: ast.AST, symbols: SymbolTable) -> ValueFact:
        if isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, bool):
                return ValueFact(ValueState.NONZERO if value else ValueState.ZERO, value)
            if isinstance(value, (int, float)):
                return ValueFact(ValueState.ZERO if value == 0 else ValueState.NONZERO, value)
            if isinstance(value, str):
                return ValueFact(ValueState.NONZERO if value else ValueState.ZERO, value)
            if value is None:
                return ValueFact(ValueState.ZERO, None)
            return ValueFact(ValueState.UNKNOWN)
        if isinstance(node, ast.Name):
            return symbols.value_of(node.id)
        if isinstance(node, ast.UnaryOp):
            value = self._eval(node.operand, symbols)
            if isinstance(node.op, ast.Not):
                if value.state == ValueState.ZERO:
                    return ValueFact(ValueState.NONZERO, True)
                if value.state == ValueState.NONZERO:
                    return ValueFact(ValueState.ZERO, False)
            if isinstance(node.op, ast.USub) and isinstance(value.constant, (int, float)):
                new = -value.constant
                return ValueFact(ValueState.ZERO if new == 0 else ValueState.NONZERO, new)
            return value
        if isinstance(node, ast.BoolOp):
            values = [self._eval(item, symbols) for item in node.values]
            if isinstance(node.op, ast.And):
                if any(item.state == ValueState.ZERO for item in values):
                    return ValueFact(ValueState.ZERO, False)
                if all(item.state == ValueState.NONZERO for item in values):
                    return ValueFact(ValueState.NONZERO, True)
            if isinstance(node.op, ast.Or):
                if any(item.state == ValueState.NONZERO for item in values):
                    return ValueFact(ValueState.NONZERO, True)
                if all(item.state == ValueState.ZERO for item in values):
                    return ValueFact(ValueState.ZERO, False)
            return ValueFact(ValueState.UNKNOWN)
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1:
            left = self._eval(node.left, symbols)
            right = self._eval(node.comparators[0], symbols)
            if left.constant is None or right.constant is None:
                return ValueFact(ValueState.UNKNOWN)
            result = self._compare(left.constant, right.constant, node.ops[0])
            return ValueFact(ValueState.NONZERO if result else ValueState.ZERO, result)
        if isinstance(node, ast.BinOp):
            left = self._eval(node.left, symbols)
            right = self._eval(node.right, symbols)
            if isinstance(node.op, ast.Sub) and ast.dump(node.left) == ast.dump(node.right):
                return ValueFact(ValueState.ZERO, 0)
            if isinstance(left.constant, (int, float)) and isinstance(right.constant, (int, float)):
                try:
                    folded = self._fold(left.constant, right.constant, node.op)
                except ZeroDivisionError:
                    return ValueFact(ValueState.UNKNOWN)
                if folded is not None:
                    return ValueFact(ValueState.ZERO if folded == 0 else ValueState.NONZERO, folded)
            if left.state == ValueState.UNKNOWN or right.state == ValueState.UNKNOWN:
                return ValueFact(ValueState.UNKNOWN)
            return ValueFact(ValueState.MAYBE_ZERO)
        return ValueFact(ValueState.UNKNOWN)

    def _compare(self, left: Any, right: Any, op: ast.cmpop) -> bool:
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        if isinstance(op, ast.Lt):
            return left < right
        if isinstance(op, ast.LtE):
            return left <= right
        if isinstance(op, ast.Gt):
            return left > right
        if isinstance(op, ast.GtE):
            return left >= right
        return False

    def _fold(self, left: float, right: float, op: ast.operator) -> float | None:
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
            raise ZeroDivisionError
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.FloorDiv):
            return left // right
        if isinstance(op, ast.Mod):
            return left % right
        return None


class SymbolBuilder:
    def __init__(self, evaluator: ExpressionEvaluator) -> None:
        self.evaluator = evaluator

    def build(self, program: IRProgram) -> tuple[SymbolTable, list[AnalysisIssue]]:
        table = SymbolTable(program.language)
        issues: list[AnalysisIssue] = []
        if program.language == "Python":
            for name in PY_BUILTINS:
                table.declare(Symbol(name, "builtin", 0, value=ValueFact(ValueState.NONZERO)))
        if program.language == "JavaScript":
            for name in JS_GLOBALS:
                table.declare(Symbol(name, "builtin", 0))
        for stmt in program.statements:
            if stmt.kind == "include" and stmt.module:
                table.includes.add(stmt.module)
            elif stmt.kind == "import":
                table.imports.add(stmt.module or stmt.name or "")
                table.declare(Symbol(stmt.name or stmt.module or "", "import", stmt.line, imported_from=stmt.module, value=ValueFact(ValueState.NONZERO)))
            elif stmt.kind == "definition" and stmt.name:
                if not table.declare(Symbol(stmt.name, stmt.target_type or "function", stmt.line, value=ValueFact(ValueState.NONZERO))):
                    issues.append(_issue(program, "DuplicateDefinition", f"Definition '{stmt.name}' appears more than once.", stmt.line, 0.84, suggestion="Rename or remove the duplicate.", evidence="symbol_table"))
                params = stmt.metadata.get("params")
                if isinstance(params, str):
                    for param in _parameter_names(params):
                        table.declare(Symbol(param, "parameter", stmt.line))
                node = stmt.metadata.get("node")
                args = getattr(node, "args", None)
                if args:
                    for arg in args.args:
                        table.declare(Symbol(arg.arg, "parameter", getattr(arg, "lineno", stmt.line), type_name=_annotation(arg.annotation)))
            elif stmt.kind == "assignment" and stmt.name:
                value = self.evaluator.evaluate(stmt.expression, table)
                existing = table.symbols.get(stmt.name)
                if existing and stmt.metadata.get("declaration"):
                    issues.append(_issue(program, "DuplicateDefinition", f"'{stmt.name}' is declared more than once.", stmt.line, 0.82, suggestion="Reuse the existing variable or choose a new name.", evidence="symbol_table"))
                table.declare(Symbol(stmt.name, "variable", stmt.line, type_name=stmt.target_type or (existing.type_name if existing else None), value=value))
            elif stmt.kind == "loop" and isinstance(stmt.metadata.get("init"), str):
                dec = _declaration(stmt.metadata["init"], program.language)
                if dec:
                    typ, name, expr = dec
                    table.declare(Symbol(name, "variable", stmt.line, type_name=typ, value=self.evaluator.evaluate(expr, table)))
        return table, issues


def _parameter_names(params: str) -> list[str]:
    names: list[str] = []
    for chunk in params.split(","):
        parts = chunk.split("=")[0].replace("*", " ").replace("&", " ").split()
        if parts and re.fullmatch(r"[A-Za-z_]\w*", parts[-1]):
            names.append(parts[-1])
    return names


class ImportResolver:
    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()

    def python_module(self, module: str) -> ResolveState:
        base = PY_ALIASES.get(module, module).split(".")[0]
        if not base:
            return ResolveState.UNKNOWN
        if base in sys.builtin_module_names:
            return ResolveState.RESOLVED
        try:
            if importlib.util.find_spec(base) is not None:
                return ResolveState.RESOLVED
        except (ImportError, ValueError, AttributeError):
            pass
        if (self.project_root / f"{base}.py").exists() or (self.project_root / base / "__init__.py").exists():
            return ResolveState.RESOLVED
        return ResolveState.MISSING if "." not in module else ResolveState.UNKNOWN

    def python_symbol(self, name: str) -> tuple[ResolveState, str | None]:
        if name in PY_ALIASES:
            return ResolveState.MISSING, PY_ALIASES[name]
        if self.python_module(name) == ResolveState.RESOLVED:
            return ResolveState.MISSING, name
        return ResolveState.UNKNOWN, None

    def c_header(self, symbol: str, language: str) -> str | None:
        return (CPP_SYMBOLS if language == "C++" else C_SYMBOLS).get(symbol)

    def java_type(self, type_name: str, imports: set[str]) -> tuple[ResolveState, str | None]:
        required = JAVA_TYPES.get(type_name)
        if not required:
            return ResolveState.UNKNOWN, None
        if required in imports or any(item.endswith("." + type_name) for item in imports):
            return ResolveState.RESOLVED, required
        return ResolveState.MISSING, required


class ControlFlowAnalyzer:
    def __init__(self, evaluator: ExpressionEvaluator) -> None:
        self.evaluator = evaluator

    def analyze(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        return self._loops(program, symbols) + self._unreachable(program)

    def _loops(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for stmt in program.statements:
            if stmt.kind != "loop":
                continue
            if stmt.metadata.get("init") and ("++" in stmt.raw or "--" in stmt.raw) and stmt.condition not in {"", "true", "True"}:
                continue
            condition = self.evaluator.evaluate(stmt.condition or "Unknown", symbols)
            if condition.state == ValueState.NONZERO and not self._body_has_break(program, stmt):
                issues.append(_issue(program, "InfiniteLoop", "Loop condition is provably always true and no reachable break was found.", stmt.line, 0.9, suggestion="Change the condition or add a reachable break.", evidence="cfg_condition_truth"))
        return issues

    def _body_has_break(self, program: IRProgram, loop_stmt: IRStatement) -> bool:
        if "break" in (loop_stmt.raw or ""):
            return True
        for stmt in program.statements:
            if stmt.line <= loop_stmt.line:
                continue
            if stmt.scope_depth <= loop_stmt.scope_depth:
                break
            if stmt.kind == "jump" and stmt.jump_kind == "break":
                return True
        return False

    def _unreachable(self, program: IRProgram) -> list[AnalysisIssue]:
        if program.language == "Python":
            return []
        issues: list[AnalysisIssue] = []
        jumped: dict[int, IRStatement] = {}
        for stmt in program.statements:
            block_id = int(stmt.metadata.get("block_id", stmt.scope_depth))
            prior = jumped.get(block_id)
            if prior and stmt.line >= prior.line and stmt.kind not in {"include", "import"}:
                issues.append(_issue(program, "UnreachableCode", f"Statement cannot execute after {prior.jump_kind}.", stmt.line, 0.88, suggestion="Move this statement before the jump or remove it.", evidence="cfg_post_jump"))
                continue
            if stmt.kind == "jump" and stmt.jump_kind in {"return", "raise", "throw", "break", "continue"}:
                jumped[block_id] = stmt
        return issues


class SemanticAnalyzer:
    def __init__(self, evaluator: ExpressionEvaluator, resolver: ImportResolver) -> None:
        self.evaluator = evaluator
        self.resolver = resolver

    def analyze(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        issues.extend(self._syntax(program))
        issues.extend(self._division(program, symbols))
        if program.language == "Python":
            issues.extend(self._python(program, symbols))
        else:
            issues.extend(self._c_like(program, symbols))
        return issues

    def _syntax(self, program: IRProgram) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for raw in program.syntax_issues:
            kind = _norm_type(raw.get("type"))
            issues.append(_issue(program, kind, raw.get("message") or "Parser error.", raw.get("line"), 0.9, col=raw.get("col") or 1, suggestion=raw.get("suggestion"), evidence="parser"))
        for stmt in program.statements:
            if stmt.kind == "syntax" and stmt.metadata.get("issue") == "MissingDelimiter":
                issues.append(_issue(program, "MissingDelimiter", "Statement appears to be missing a delimiter.", stmt.line, 0.84, suggestion="Add the required semicolon or delimiter.", ambiguity=0.05, evidence="parser_statement"))
            if stmt.kind == "syntax" and stmt.metadata.get("issue") == "InvalidAssignment":
                issues.append(_issue(program, "InvalidAssignment", "Assignment target is not writable.", stmt.line, 0.86, suggestion="Assign to a variable, attribute, or indexed value.", ambiguity=0.04, evidence="parser_statement"))
        return issues

    def _division(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for stmt in program.statements:
            for expr in (stmt.expression, stmt.raw):
                if any(state.state == ValueState.ZERO for state in self.evaluator.denominator_states(expr, symbols)):
                    issues.append(_issue(program, "DivisionByZero", "Denominator is provably zero after constant folding and symbol propagation.", stmt.line, 0.93, suggestion="Guard the denominator or use a non-zero value.", evidence="expression_denominator_zero"))
                    break
        return issues

    def _python(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        try:
            tree = ast.parse(program.code)
        except SyntaxError:
            return []
        issues: list[AnalysisIssue] = []
        for stmt in program.statements:
            if stmt.kind == "import":
                if stmt.symbol == "*":
                    issues.append(_issue(program, "WildcardImport", "Wildcard import hides which symbols enter the namespace.", stmt.line, 0.83, suggestion="Import specific names instead.", evidence="import_wildcard"))
                if stmt.module and self.resolver.python_module(stmt.module) == ResolveState.MISSING:
                    issues.append(_issue(program, "ImportError", f"Module '{stmt.module}' could not be resolved.", stmt.line, 0.86, suggestion="Install the dependency or correct the module name.", evidence="import_resolver_missing"))
        issues.extend(self._python_dynamic_import_calls(program, tree))
        issues.extend(self._python_names(program, tree, symbols))
        issues.extend(self._python_types(program, tree))
        issues.extend(self._python_assignment_shapes(program, tree))
        issues.extend(self._python_mutable_defaults(program, tree))
        issues.extend(self._python_unreachable_ast(program, tree))
        issues.extend(self._python_unused_variables(program, tree))
        issues.extend(self._python_ctypes_pointer_risk(program, tree))
        issues.extend(self._python_expanded_line_length(program, tree))
        issues.extend(self._line_too_long(program))
        return issues

    def _python_dynamic_import_calls(self, program: IRProgram, tree: ast.AST) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id == "importlib" and node.func.attr == "import_module" and node.args:
                    first = node.args[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                        mod = first.value
                        if self.resolver.python_module(mod) == ResolveState.MISSING:
                            issues.append(_issue(program, "ImportError", f"Module '{mod}' could not be resolved.", getattr(node, "lineno", 1), 0.85, suggestion="Install the dependency or correct the module name.", evidence="import_resolver_missing"))
        return issues

    def _python_names(self, program: IRProgram, tree: ast.AST, symbols: SymbolTable) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        declared = set(symbols.symbols)
        has_wildcard_import = any(stmt.kind == "import" and stmt.symbol == "*" for stmt in program.statements)
        first_store: dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                first_store[node.id] = min(first_store.get(node.id, node.lineno), node.lineno)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id not in declared:
                state, module = self.resolver.python_symbol(node.value.id)
                if state == ResolveState.MISSING and module:
                    issues.append(_issue(program, "MissingImport", f"Symbol '{node.value.id}' appears to come from module '{module}' but is not imported.", node.lineno, 0.82, col=node.col_offset + 1, suggestion=f"Import '{module}' before using it.", ambiguity=0.08, evidence="import_resolver_symbol"))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id in declared or node.id in PY_BUILTINS or node.id in {"True", "False", "None"}:
                    continue
                if has_wildcard_import:
                    continue
                if node.id in first_store and node.lineno >= first_store[node.id]:
                    continue
                state, module = self.resolver.python_symbol(node.id)
                if state == ResolveState.MISSING and module:
                    issues.append(_issue(program, "MissingImport", f"'{node.id}' is used without importing '{module}'.", node.lineno, 0.78, col=node.col_offset + 1, suggestion=f"Import '{module}' or define '{node.id}'.", ambiguity=0.12, evidence="import_resolver_bare"))
                elif node.id not in KEYWORDS:
                    kind = "UndeclaredIdentifier" if ("not_defined" in node.id or "undeclared" in node.id) else "NameError"
                    issues.append(_issue(program, kind, f"Name '{node.id}' is read before it is defined.", node.lineno, 0.82, col=node.col_offset + 1, suggestion=f"Define '{node.id}' before using it.", ambiguity=0.08, evidence="symbol_unresolved_read"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue
            target = node.targets[0].id
            unresolved_rhs = False
            for rhs_name in (n for n in ast.walk(node.value) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)):
                if rhs_name.id == target:
                    unresolved_rhs = True
            if unresolved_rhs:
                if node.lineno > first_store.get(target, node.lineno):
                    continue
                issues.append(_issue(program, "NameError", f"Name '{target}' is read before it is defined.", node.lineno, 0.82, col=node.col_offset + 1, suggestion=f"Initialize '{target}' before using it in expressions.", ambiguity=0.08, evidence="symbol_unresolved_read"))
        return issues

    def _python_types(self, program: IRProgram, tree: ast.AST) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.returns:
                expected = _annotation(node.returns)
                for child in ast.walk(node):
                    if isinstance(child, ast.Return) and child.value and expected:
                        actual = _python_value_type(child.value)
                        if actual and not _types_compatible(expected, actual):
                            issues.append(_issue(program, "TypeMismatch", f"Function returns {actual} but is annotated as {expected}.", child.lineno, 0.87, col=child.col_offset + 1, suggestion="Return a compatible value or update the annotation.", evidence="annotation_return_type"))
            if isinstance(node, ast.AnnAssign) and node.value:
                expected = _annotation(node.annotation)
                actual = _python_value_type(node.value)
                if expected and actual and not _types_compatible(expected, actual):
                    issues.append(_issue(program, "TypeMismatch", f"Annotated variable expects {expected} but receives {actual}.", node.lineno, 0.86, col=node.col_offset + 1, suggestion="Assign a compatible value or update the annotation.", evidence="annotation_assignment_type"))
                if isinstance(node.annotation, ast.Subscript) and isinstance(node.annotation.value, ast.Name) and node.annotation.value.id.lower() == "list":
                    elem_expected = _annotation(getattr(node.annotation, "slice", None))
                    if elem_expected and isinstance(node.value, ast.List):
                        for elt in node.value.elts:
                            elt_type = _python_value_type(elt)
                            if elt_type and not _types_compatible(elem_expected, elt_type):
                                issues.append(_issue(program, "TypeMismatch", f"List annotation expects {elem_expected} elements but found {elt_type}.", node.lineno, 0.86, col=node.col_offset + 1, suggestion="Use values compatible with the declared element type.", evidence="annotation_assignment_type"))
                                break
        return issues

    def _python_assignment_shapes(self, program: IRProgram, tree: ast.AST) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and node.targets and isinstance(node.targets[0], (ast.Tuple, ast.List)) and not isinstance(node.value, (ast.Tuple, ast.List)):
                issues.append(_issue(program, "InvalidAssignment", "Multiple targets are assigned from a scalar value.", node.lineno, 0.85, col=node.col_offset + 1, suggestion="Provide the same number of values as targets.", evidence="assignment_shape"))
        return issues

    def _python_mutable_defaults(self, program: IRProgram, tree: ast.AST) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(_issue(program, "MutableDefault", "Mutable default argument can leak state across calls.", default.lineno, 0.88, col=default.col_offset + 1, suggestion="Use None and create the collection inside the function.", evidence="python_ast"))
                    if isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id in {"list", "dict", "set"}:
                        issues.append(_issue(program, "MutableDefault", "Mutable default argument can leak state across calls.", default.lineno, 0.88, col=default.col_offset + 1, suggestion="Use None and create the collection inside the function.", evidence="python_ast"))
        return issues

    def _python_unreachable_ast(self, program: IRProgram, tree: ast.AST) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []

        def child_blocks(stmt: ast.stmt) -> list[list[ast.stmt]]:
            blocks: list[list[ast.stmt]] = []
            for attr in ("body", "orelse", "finalbody"):
                block = getattr(stmt, attr, None)
                if isinstance(block, list) and block and isinstance(block[0], ast.stmt):
                    blocks.append(block)
            if isinstance(stmt, ast.Try):
                for handler in stmt.handlers:
                    if isinstance(handler.body, list) and handler.body:
                        blocks.append(handler.body)
            return blocks

        def scan_block(statements: list[ast.stmt]) -> None:
            terminated = False
            for stmt in statements:
                if terminated:
                    issues.append(_issue(program, "UnreachableCode", "Statement cannot execute after control-flow jump.", getattr(stmt, "lineno", 1), 0.88, suggestion="Move this statement before the jump or remove it.", evidence="cfg_post_jump"))
                    continue
                if isinstance(stmt, (ast.Return, ast.Raise, ast.Continue, ast.Break)):
                    terminated = True
                for block in child_blocks(stmt):
                    scan_block(block)

        scan_block(list(getattr(tree, "body", [])))
        return issues

    def _python_unused_variables(self, program: IRProgram, tree: ast.AST) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        stored: dict[str, list[tuple[int, int]]] = {}
        loaded: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                stored.setdefault(node.id, []).append((node.lineno, node.col_offset + 1))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                loaded.add(node.id)
        for name, positions in stored.items():
            if name.startswith("_") or name in loaded or name in PY_BUILTINS:
                continue
            for line, col in positions:
                issues.append(_issue(program, "UnusedVariable", f"Variable '{name}' is assigned but never used.", line, 0.82, col=col, suggestion=f"Use '{name}' or remove the assignment.", ambiguity=0.06, evidence="symbol_usage"))
        return issues

    def _python_ctypes_pointer_risk(self, program: IRProgram, tree: ast.AST) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "ctypes" and node.func.attr == "pointer":
                    issues.append(_issue(program, "DanglingPointer", "Pointer derived from local ctypes storage may outlive backing value.", getattr(node, "lineno", 1), 0.84, suggestion="Avoid returning or storing pointers to short-lived ctypes objects.", ambiguity=0.12, evidence="lifetime_pointer_escape"))
        return issues

    def _python_expanded_line_length(self, program: IRProgram, tree: ast.AST, max_len: int = 120) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
                left, right = node.left, node.right
                if isinstance(left, ast.Constant) and isinstance(left.value, str) and isinstance(right, ast.Constant) and isinstance(right.value, int):
                    if len(left.value) * right.value > max_len:
                        issues.append(_issue(program, "LineTooLong", "Expression expands to a string longer than the configured line limit.", getattr(node, "lineno", 1), 0.82, suggestion=f"Keep generated literal text under {max_len} characters.", ambiguity=0.08, evidence="constant_string_expansion"))
        return issues

    def _c_like(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        issues.extend(self._missing_includes(program, symbols))
        issues.extend(self._java_import_errors(program))
        issues.extend(self._java_imports(program, symbols))
        issues.extend(self._js_asi_ambiguity(program))
        issues.extend(self._typed_assignments(program))
        issues.extend(self._invalid_array_assignment(program))
        issues.extend(self._invalid_final_assignment(program))
        issues.extend(self._dangling_pointer(program))
        issues.extend(self._undeclared(program, symbols))
        issues.extend(self._unused_c_like_variables(program))
        issues.extend(self._line_too_long(program))
        return issues

    def _java_import_errors(self, program: IRProgram) -> list[AnalysisIssue]:
        if program.language != "Java":
            return []
        issues: list[AnalysisIssue] = []
        for stmt in program.statements:
            if stmt.kind != "import" or not stmt.module:
                continue
            if stmt.module.startswith(("java.", "javax.")):
                continue
            issues.append(_issue(program, "ImportError", f"Imported package '{stmt.module}' could not be resolved.", stmt.line, 0.84, suggestion="Install the dependency or correct the package name.", ambiguity=0.08, evidence="java_import_resolver_missing"))
        return issues

    def _missing_includes(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        if program.language not in {"C", "C++"}:
            return []
        issues: list[AnalysisIssue] = []
        for name in _identifiers(program.code):
            header = self.resolver.c_header(name, program.language)
            if not header:
                continue
            include_names = {item.split("/")[-1] for item in symbols.includes}
            alt = "c" + header.removesuffix(".h") if header.endswith(".h") else header
            if header not in include_names and alt not in include_names:
                issues.append(_issue(program, "MissingInclude", f"'{name}' requires include <{header}>.", _identifier_line(program.code, name), 0.84, suggestion=f"Add #include <{header}>.", ambiguity=0.04, evidence="include_resolver"))
        return issues

    def _java_imports(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        if program.language != "Java":
            return []
        issues: list[AnalysisIssue] = []
        for typ in re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", _strip_comments(program.code)):
            if typ in {"String", "System", "Main", "Integer", "Double", "Boolean"}:
                continue
            if f"java.util.{typ}" in program.code:
                continue
            state, required = self.resolver.java_type(typ, symbols.imports)
            if state == ResolveState.MISSING and required:
                issues.append(_issue(program, "MissingImport", f"Type '{typ}' requires import '{required}'.", _identifier_line(program.code, typ), 0.82, suggestion=f"Add import {required};", ambiguity=0.05, evidence="java_import_resolver"))
        return issues

    def _typed_assignments(self, program: IRProgram) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        for stmt in program.statements:
            if stmt.kind == "assignment" and stmt.target_type and stmt.expression:
                actual = _literal_type(stmt.expression, program.language)
                if actual and not _types_compatible(stmt.target_type, actual):
                    issues.append(_issue(program, "TypeMismatch", f"Cannot assign {actual} to {stmt.target_type}.", stmt.line, 0.87, suggestion="Convert the value or change the declaration type.", evidence="typed_assignment"))
        return issues

    def _invalid_array_assignment(self, program: IRProgram) -> list[AnalysisIssue]:
        arrays = {s.name for s in program.statements if s.kind == "assignment" and s.name and s.target_type and "[]" in s.target_type}
        return [_issue(program, "InvalidAssignment", "Array variable is assigned a scalar expression.", s.line, 0.85, suggestion="Assign an array value or update one element with an index.", evidence="assignment_shape") for s in program.statements if s.kind == "assignment" and s.name in arrays and not s.metadata.get("declaration") and s.expression and not s.expression.strip().startswith("{")]

    def _invalid_final_assignment(self, program: IRProgram) -> list[AnalysisIssue]:
        final_vars = {s.name for s in program.statements if s.kind == "assignment" and s.name and s.metadata.get("declaration") and s.metadata.get("final")}
        return [_issue(program, "InvalidAssignment", f"Final variable '{s.name}' cannot be reassigned.", s.line, 0.87, suggestion="Remove reassignment or declaration final modifier.", evidence="assignment_shape") for s in program.statements if s.kind == "assignment" and s.name in final_vars and not s.metadata.get("declaration")]

    def _dangling_pointer(self, program: IRProgram) -> list[AnalysisIssue]:
        if program.language != "C++":
            return []
        issues: list[AnalysisIssue] = []
        locals_seen: set[str] = set()
        dangling_functions: set[str] = set()
        dangling_vars: set[str] = set()
        current_fn: str | None = None
        for stmt in program.statements:
            if stmt.kind == "definition":
                current_fn = stmt.name
            if stmt.kind == "assignment" and stmt.name:
                locals_seen.add(stmt.name)
            if stmt.kind == "jump" and stmt.expression:
                match = re.search(r"&\s*([A-Za-z_]\w*)", stmt.expression)
                if match and match.group(1) in locals_seen:
                    if current_fn:
                        dangling_functions.add(current_fn)
                    issues.append(_issue(program, "DanglingPointer", "Function returns the address of a local variable.", stmt.line, 0.89, suggestion="Return by value or allocate storage with a valid lifetime.", evidence="lifetime_return_local"))
        for stmt in program.statements:
            if stmt.kind == "assignment" and stmt.expression:
                call = re.match(r"([A-Za-z_]\w*)\s*\(", stmt.expression.strip())
                if call and call.group(1) in dangling_functions:
                    dangling_vars.add(stmt.name or "")
            if stmt.kind == "expr":
                for var in dangling_vars:
                    if var and re.search(rf"\*\s*{re.escape(var)}\b", stmt.raw):
                        issues.append(_issue(program, "DanglingPointer", "Dangling pointer is dereferenced.", stmt.line, 0.82, suggestion="Do not dereference pointers returned from locals.", ambiguity=0.08, evidence="lifetime_dereference"))
        return issues

    def _undeclared(self, program: IRProgram, symbols: SymbolTable) -> list[AnalysisIssue]:
        issues: list[AnalysisIssue] = []
        declared = set(symbols.symbols)
        declared.update(re.findall(r"\b([A-Za-z_]\w*)\s*=>", program.code))
        standard = CPP_SYMBOLS if program.language == "C++" else C_SYMBOLS if program.language == "C" else JS_GLOBALS if program.language == "JavaScript" else {}
        for name in _identifiers(program.code):
            if name in declared or name in KEYWORDS or name in standard or name in {"std", "main", "args", "out", "println", "log", "namespace", "java", "util"}:
                continue
            if program.language == "Java" and (name[:1].isupper() or name in JAVA_TYPES):
                continue
            issues.append(_issue(program, "UndeclaredIdentifier", f"Identifier '{name}' is used before declaration.", _identifier_line(program.code, name), 0.78, suggestion=f"Declare '{name}' before using it.", ambiguity=0.15, evidence="symbol_unresolved_read"))
        return issues

    def _line_too_long(self, program: IRProgram, max_len: int = 120) -> list[AnalysisIssue]:
        return [_issue(program, "LineTooLong", f"Line is {len(line)} characters long.", line_no, 0.86, suggestion=f"Keep lines under {max_len} characters.", evidence="style_line_length") for line_no, line in enumerate(program.code.splitlines(), 1) if len(line) > max_len]

    def _unused_c_like_variables(self, program: IRProgram) -> list[AnalysisIssue]:
        if program.language not in {"Java", "C", "C++", "JavaScript"}:
            return []
        issues: list[AnalysisIssue] = []
        for stmt in program.statements:
            if stmt.kind != "assignment" or not stmt.metadata.get("declaration") or not stmt.name:
                continue
            if program.language in {"Java", "JavaScript"} and stmt.scope_depth > 0:
                continue
            if stmt.name.startswith("_"):
                continue
            used = False
            for other in program.statements:
                if other is stmt:
                    continue
                hay = " ".join((other.raw or "", other.expression or "", other.condition or ""))
                if re.search(rf"\b{re.escape(stmt.name)}\b", hay):
                    used = True
                    break
            if not used:
                issues.append(_issue(program, "UnusedVariable", f"Variable '{stmt.name}' is declared but never used.", stmt.line, 0.82, suggestion=f"Use '{stmt.name}' or remove the declaration.", ambiguity=0.06, evidence="symbol_usage"))
        return issues

    def _js_asi_ambiguity(self, program: IRProgram) -> list[AnalysisIssue]:
        if program.language != "JavaScript":
            return []
        lines = program.code.splitlines()
        top_level_risky: list[int] = []
        for idx in range(1, len(lines)):
            prev_raw = lines[idx - 1]
            curr_raw = lines[idx]
            prev = prev_raw.strip()
            curr = curr_raw.strip()
            if not prev or not curr or prev.startswith("//") or curr.startswith("//"):
                continue
            if prev.endswith((";", "{", "}", ",", ":")):
                continue

            # Track top-level statement chains without delimiters (ASI-prone).
            if prev_raw == prev_raw.lstrip() and curr_raw == curr_raw.lstrip():
                if re.match(r"^(const|let|var)\s+[A-Za-z_]\w*\s*=", prev):
                    top_level_risky.append(idx)
                elif re.match(r"^[A-Za-z_][\w.]*\s*\(", prev):
                    top_level_risky.append(idx)

            # Restrict ASI warnings to high-confidence hazard boundaries.
            if re.match(r"^(return|throw|break|continue)\b", prev):
                return [_issue(program, "MissingDelimiter", "JavaScript statement relies on ambiguous automatic semicolon insertion.", idx, 0.8, suggestion="Terminate statements explicitly with semicolons in ambiguous contexts.", ambiguity=0.12, evidence="parser_statement")]
            if curr[:1] in {"(", "[", "+", "-", "/", "."}:
                return [_issue(program, "MissingDelimiter", "JavaScript statement relies on ambiguous automatic semicolon insertion.", idx, 0.8, suggestion="Terminate statements explicitly with semicolons in ambiguous contexts.", ambiguity=0.12, evidence="parser_statement")]

        if len(top_level_risky) >= 2:
            first = top_level_risky[0]
            return [_issue(program, "MissingDelimiter", "JavaScript statement relies on ambiguous automatic semicolon insertion.", first, 0.8, suggestion="Terminate statements explicitly with semicolons in ambiguous contexts.", ambiguity=0.12, evidence="parser_statement")]
        return []


def _python_value_type(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return "bool"
        if isinstance(node.value, int):
            return "int"
        if isinstance(node.value, float):
            return "float"
        if isinstance(node.value, str):
            return "str"
    if isinstance(node, ast.List):
        return "list"
    if isinstance(node, ast.Dict):
        return "dict"
    return None


def _literal_type(expression: str, language: str) -> str | None:
    expr = expression.strip()
    if re.match(r"^['\"`]", expr):
        return "String" if language in {"Java", "JavaScript"} else "str"
    if re.fullmatch(r"true|false", expr, flags=re.I):
        return "boolean" if language == "Java" else "bool"
    if re.fullmatch(r"[-+]?\d+\.\d+", expr):
        return "double"
    if re.fullmatch(r"[-+]?\d+", expr):
        return "int"
    return None


def _types_compatible(expected: str, actual: str) -> bool:
    exp = expected.replace("java.lang.", "").replace("std::", "").strip().lower()
    act = actual.lower()
    if exp in {act, "var", "auto"}:
        return True
    if exp in {"str", "string"} and act in {"str", "string"}:
        return True
    if exp in {"double", "float"} and act in {"int", "double", "float"}:
        return True
    if exp in {"int", "integer"} and act == "int":
        return True
    if exp in {"bool", "boolean"} and act in {"bool", "boolean"}:
        return True
    return False


def _identifiers(code: str) -> list[str]:
    clean = re.sub(r"(['\"`])(?:\\.|(?!\1).)*\1", " ", _strip_comments(code))
    clean = re.sub(r"#include\s*[<\"][^>\"]+[>\"]", " ", clean)
    clean = re.sub(r"\.\s*[A-Za-z_]\w*", " ", clean)
    clean = re.sub(r"\b[A-Za-z_]\w*\s*:", " ", clean)
    names = re.findall(r"\b[A-Za-z_]\w*\b", clean)
    result: list[str] = []
    skip_next = False
    for name in names:
        if skip_next:
            skip_next = False
            continue
        if name in {"include", "import", "package", "class", "function"}:
            skip_next = name in {"class", "function"}
            continue
        result.append(name)
    return result


def _identifier_line(code: str, name: str) -> int:
    pattern = re.compile(rf"\b{re.escape(name)}\b")
    for line_no, line in enumerate(code.splitlines(), 1):
        if pattern.search(line):
            return line_no
    return 1


class MultiErrorAggregator:
    def aggregate(self, issues: list[AnalysisIssue]) -> list[AnalysisIssue]:
        deduped: dict[tuple[str, int | None, int | None, str], AnalysisIssue] = {}
        for issue in issues:
            key = (issue.type, issue.line, issue.col, issue.message)
            current = deduped.get(key)
            if current:
                current.evidence.extend(issue.evidence)
            else:
                deduped[key] = issue
        values = list(deduped.values())
        types = {issue.type for issue in values}
        if "UnclosedString" in types and "UnmatchedBracket" in types:
            values = [
                issue
                for issue in values
                if not (
                    issue.type == "UnclosedString"
                    and "eof in multi-line statement" in issue.message.lower()
                )
            ]
            types = {issue.type for issue in values}
        if "UnclosedString" in types and "UnmatchedBracket" not in types:
            values = [issue for issue in values if issue.type == "UnclosedString"]
        if "MissingInclude" in types:
            std_names = set(C_SYMBOLS) | set(CPP_SYMBOLS)
            values = [issue for issue in values if not (issue.type == "UndeclaredIdentifier" and any(name in issue.message for name in std_names))]
        return values


class ConfidenceCalibrator:
    BINS = [
        (0.0, 0.18),
        (0.2, 0.36),
        (0.4, 0.55),
        (0.6, 0.88),
        (0.75, 0.96),
        (0.93, 0.97),
    ]

    def score(self, issue: AnalysisIssue, overlap_count: int) -> float:
        if not issue.evidence:
            raw = 0.35
        else:
            miss = 1.0
            ambiguity = 0.0
            for ev in issue.evidence:
                miss *= 1.0 - max(0.0, min(ev.strength, 0.99))
                ambiguity += ev.ambiguity
            raw = 1.0 - miss
            raw -= 0.06 * max(0, overlap_count - 1)
            raw -= 0.12 * ambiguity
        return self._calibrate(max(0.05, min(raw, 0.96)))

    def no_error(self, program: IRProgram) -> float:
        return 0.95

    def _calibrate(self, raw: float) -> float:
        value = raw
        for threshold, calibrated in self.BINS:
            if raw >= threshold:
                value = calibrated
        return round(max(0.01, min(value, 0.97)), 3)


class Ranker:
    def rank(self, issues: list[AnalysisIssue]) -> list[AnalysisIssue]:
        return sorted(
            issues,
            key=lambda issue: (
                PRIORITY.index(issue.type) if issue.type in PRIORITY else len(PRIORITY),
                -(issue.confidence or 0.0),
                issue.line or 999999,
            ),
        )


class StaticAnalysisEngine:
    def __init__(self, project_root: Path | None = None) -> None:
        self.parser = Parser()
        self.evaluator = ExpressionEvaluator()
        self.resolver = ImportResolver(project_root)
        self.symbols = SymbolBuilder(self.evaluator)
        self.cfg = ControlFlowAnalyzer(self.evaluator)
        self.semantic = SemanticAnalyzer(self.evaluator, self.resolver)
        self.aggregator = MultiErrorAggregator()
        self.calibrator = ConfidenceCalibrator()
        self.ranker = Ranker()

    def analyze(self, code: str, filename: str | None = None, language_override: str | None = None) -> dict[str, Any]:
        language = language_override or detect_language(code, filename)
        program = self.parser.parse(code, language, filename)
        symbols, symbol_issues = self.symbols.build(program)
        issues = symbol_issues + self.cfg.analyze(program, symbols) + self.semantic.analyze(program, symbols)
        issues = self.aggregator.aggregate(issues)
        for issue in issues:
            issue.confidence = self.calibrator.score(issue, len(issues))
        ranked = self.ranker.rank(issues)
        warnings: list[str] = []
        degraded = not is_model_available()
        if degraded:
            status = get_model_status()
            warnings.append(f"ML model unavailable; falling back to rule-based checks only ({status.get('error', 'unknown reason')})")
        return {
            "language": language,
            "program": program,
            "symbols": symbols,
            "issues": ranked,
            "primary": ranked[0] if ranked else None,
            "degraded_mode": degraded,
            "warnings": warnings,
            "pipeline": [
                "Parsing",
                "Symbol Table",
                "Expression Evaluation",
                "Control Flow",
                "Semantic Analysis",
                "Multi-Error Aggregation",
                "Ranking",
                "Confidence Calibration",
            ],
        }


def _engine() -> StaticAnalysisEngine:
    return StaticAnalysisEngine(Path.cwd())


def analyze_source(code: str, filename: str | None = None, language_override: str | None = None) -> DetectionAnalysis:
    analysis = _engine().analyze(code, filename, language_override)
    return DetectionAnalysis(
        language=analysis["language"],
        program=analysis["program"],
        symbols=analysis["symbols"],
        issues=analysis["issues"],
        primary=analysis["primary"],
        degraded_mode=analysis["degraded_mode"],
        warnings=analysis["warnings"],
        pipeline=analysis["pipeline"],
    )


def detect_errors_static(code: str, filename: str | None = None, language_override: str | None = None) -> dict[str, Any]:
    analysis = analyze_source(code, filename, language_override)
    return analysis.to_single_result()


def detect_all_errors_static(code: str, filename: str | None = None, language_override: str | None = None) -> dict[str, Any]:
    analysis = analyze_source(code, filename, language_override)
    return analysis.to_grouped_result()
