"""Production validation gates for the semantic OmniSyntax engine.

The original benchmark is intentionally not used as the proof of readiness here.
It remains a regression replay; these suites stress mutation robustness,
messy code, multi-error recall, cross-language consistency, and confidence
calibration.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.error_engine import detect_errors
from src.multi_error_detector import detect_all_errors


@dataclass(frozen=True)
class Case:
    language: str
    expected: str
    code: str
    filename: str


@dataclass(frozen=True)
class MultiCase:
    language: str
    expected_types: tuple[str, ...]
    code: str
    filename: str


def _strict_cases() -> list[Case]:
    return [
        Case("Python", "DivisionByZero", "def f():\n    return 10 / (2-2)\n", "x.py"),
        Case("Python", "InfiniteLoop", "while (2 > 1):\n    pass\n", "x.py"),
        Case("Python", "UnreachableCode", "def f():\n    return 1\n    x = 2\n", "x.py"),
        Case("Python", "MissingImport", "def f():\n    return statistics.mean([1,2,3])\n", "x.py"),
        Case("Java", "DivisionByZero", "public class T { static int f(){ int d=2-2; return 10/d; } }", "T.java"),
        Case("Java", "UnreachableCode", "public class T { static int f(){ return 1; int x=2; } }", "T.java"),
        Case("Java", "MissingImport", "public class T { void f(){ LinkedList<Integer> q = new LinkedList<>(); } }", "T.java"),
        Case("C", "DivisionByZero", "int main(){ int d = 2-2; return 5/d; }", "x.c"),
        Case("C", "MissingInclude", "int main(){ fprintf(stdout, \"x\"); return 0; }", "x.c"),
        Case("C++", "DanglingPointer", "int* bad(){ int x=1; return &x; } int main(){ int* p = bad(); return *p; }", "x.cpp"),
        Case("JavaScript", "DivisionByZero", "const d = 2-2; const z = 9 / d;", "x.js"),
        Case("JavaScript", "UnreachableCode", "function f(){ return 1; console.log(2); }", "x.js"),
    ]


def _messy_cases() -> list[Case]:
    return [
        Case("Python", "NoError", "# comment\n\ndef add(a:int,b:int)->int:\n    return a+b\n", "x.py"),
        Case("Java", "NoError", "public class T { public static void main(String[] a){ int x=1; System.out.println(x); } }", "T.java"),
        Case("C", "NoError", "#include <stdio.h>\nint main(){ printf(\"ok\"); return 0; }", "x.c"),
        Case("C++", "NoError", "#include <iostream>\nint main(){ int x=1; std::cout << x; return 0; }", "x.cpp"),
        Case("JavaScript", "NoError", "function add(a,b){ return a+b }\nconsole.log(add(1,2))\n", "x.js"),
        Case("JavaScript", "UndeclaredIdentifier", "function f(){ return missing_symbol_qa + 1 }", "x.js"),
        Case("Python", "ImportError", "import vendor_pkg_alpha\nprint('x')\n", "x.py"),
        Case("Java", "TypeMismatch", "public class T { void f(){ int x = \"7\"; } }", "T.java"),
        Case("C", "UnreachableCode", "int main(){ return 0; int x = 1; }", "x.c"),
        Case("C++", "DivisionByZero", "int main(){ int d = 2-2; return 10/d; }", "x.cpp"),
    ]


def _multi_cases() -> list[MultiCase]:
    return [
        MultiCase("Java", ("MissingImport", "TypeMismatch", "UnreachableCode"), "public class T { static int f(){ ArrayList<Integer> xs = new ArrayList<>(); int n = \"7\"; return 1; int z=2; } }", "T.java"),
        MultiCase("C", ("DivisionByZero", "UnreachableCode"), "int main(){ int z = 5/0; return z; int x = 2; }", "x.c"),
        MultiCase("C++", ("DanglingPointer", "UndeclaredIdentifier"), "int* bad(){ int x=1; return &x; } int main(){ int* p = bad(); return *q; }", "x.cpp"),
        MultiCase("JavaScript", ("DuplicateDefinition", "UnreachableCode"), "function f(){ let x=1; let x=2; return x; console.log(x); }", "x.js"),
        MultiCase("Python", ("MissingImport", "TypeMismatch"), "def f() -> int:\n    data = np.array([1,2,3])\n    return 'x'\n", "x.py"),
    ]


def _family_cases() -> dict[str, list[Case]]:
    return {
        "division_expr_zero": [
            Case("Python", "DivisionByZero", "def f():\n    return 10 / (2-2)\n", "x.py"),
            Case("Java", "DivisionByZero", "public class T { static int f(){ int d=2-2; return 10/d; } }", "T.java"),
            Case("C++", "DivisionByZero", "int main(){ int d=2-2; return 10/d; }", "x.cpp"),
            Case("JavaScript", "DivisionByZero", "const d = 2-2; const z = 10 / d;", "x.js"),
        ],
        "infinite_condition_expr": [
            Case("Python", "InfiniteLoop", "while (2 > 1):\n    pass\n", "x.py"),
            Case("Java", "InfiniteLoop", "public class T { static void f(){ while((2>1)){} } }", "T.java"),
            Case("C++", "InfiniteLoop", "int main(){ while((2>1)){} }", "x.cpp"),
            Case("JavaScript", "InfiniteLoop", "while((2>1)){}", "x.js"),
        ],
        "unreachable_after_jump": [
            Case("Python", "UnreachableCode", "def f():\n    return 1\n    x = 2\n", "x.py"),
            Case("Java", "UnreachableCode", "public class T { static int f(){ return 1; int x=2; } }", "T.java"),
            Case("C++", "UnreachableCode", "int main(){ return 1; int x=2; }", "x.cpp"),
            Case("JavaScript", "UnreachableCode", "function f(){ return 1; console.log(2); }", "x.js"),
        ],
    }


def _score_cases(cases: list[Case]) -> tuple[float, list[dict]]:
    rows = []
    for case in cases:
        result = detect_errors(case.code, case.filename, case.language)
        predicted = result["predicted_error"]
        rows.append({
            "language": case.language,
            "expected": case.expected,
            "predicted": predicted,
            "confidence": result.get("confidence", 0.0),
            "correct": predicted == case.expected,
        })
    return mean(1.0 if row["correct"] else 0.0 for row in rows), rows


def _multi_recall(cases: list[MultiCase]) -> tuple[float, list[dict]]:
    rows = []
    for case in cases:
        result = detect_all_errors(case.code, case.filename)
        found = {item["type"] for item in result.get("errors", [])}
        expected = set(case.expected_types)
        recall = len(found & expected) / len(expected)
        rows.append({"language": case.language, "expected": sorted(expected), "found": sorted(found), "recall": recall, "full_match": expected.issubset(found)})
    return mean(row["recall"] for row in rows), rows


def _ece(rows: list[dict], bins: int = 10) -> float:
    total = len(rows)
    if not total:
        return 0.0
    ece = 0.0
    for idx in range(bins):
        low = idx / bins
        high = (idx + 1) / bins
        bucket = [row for row in rows if low <= min(float(row["confidence"]), 0.999999) < high]
        if not bucket:
            continue
        avg_conf = mean(float(row["confidence"]) for row in bucket)
        avg_acc = mean(1.0 if row["correct"] else 0.0 for row in bucket)
        ece += (len(bucket) / total) * abs(avg_conf - avg_acc)
    return ece


def run() -> dict:
    mutation_score, mutation_rows = _score_cases(_strict_cases())
    messy_score, messy_rows = _score_cases(_messy_cases())
    multi_score, multi_rows = _multi_recall(_multi_cases())
    family_rows = []
    family_scores = {}
    for family, cases in _family_cases().items():
        score, rows = _score_cases(cases)
        family_scores[family] = score
        family_rows.extend({"family": family, **row} for row in rows)
    confidence_rows = mutation_rows + messy_rows + family_rows
    confidences = [round(float(row["confidence"]), 3) for row in confidence_rows]
    payload = {
        "metrics": {
            "mutation_robustness": round(mutation_score, 3),
            "real_world_messy_accuracy": round(messy_score, 3),
            "multi_error_recall": round(multi_score, 3),
            "cross_language_consistency": round(mean(family_scores.values()), 3),
            "confidence_ece": round(_ece(confidence_rows), 4),
            "confidence_constant": len(set(confidences)) <= 1,
        },
        "thresholds": {
            "mutation_robustness": 0.95,
            "real_world_messy_accuracy": 0.90,
            "multi_error_recall": 0.85,
            "cross_language_consistency": 0.80,
            "confidence_ece": 0.05,
            "confidence_constant": False,
        },
        "details": {
            "mutation": mutation_rows,
            "messy": messy_rows,
            "multi": multi_rows,
            "families": family_scores,
        },
    }
    metrics = payload["metrics"]
    payload["passed"] = (
        metrics["mutation_robustness"] >= 0.95
        and metrics["real_world_messy_accuracy"] >= 0.90
        and metrics["multi_error_recall"] >= 0.85
        and metrics["cross_language_consistency"] >= 0.80
        and metrics["confidence_ece"] < 0.05
        and metrics["confidence_constant"] is False
    )
    return payload


def main() -> None:
    payload = run()
    output = REPO_ROOT / "artifacts" / "qa" / "production-validation-current.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["metrics"], indent=2))
    print(f"Wrote: {output}")
    raise SystemExit(0 if payload["passed"] else 1)


if __name__ == "__main__":
    main()
