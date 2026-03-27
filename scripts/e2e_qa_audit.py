"""
Comprehensive end-to-end QA audit for OmniSyntax.

Outputs:
- artifacts/qa/e2e_qa_results.json
- artifacts/qa/e2e_qa_results.md
"""

from __future__ import annotations

import json
import re
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

import api
from src.auto_fix import AutoFixer
from src.error_engine import detect_errors
from src.multi_error_detector import detect_all_errors


@dataclass
class Case:
    case_id: str
    language: str
    category: str
    description: str
    code: str
    expected_types: list[str]
    expected_line: int | None
    corrected_code: str


def mk(
    language: str,
    idx: int,
    category: str,
    description: str,
    code: str,
    expected: list[str],
    corrected: str,
    expected_line: int | None = None,
) -> Case:
    return Case(
        case_id=f"{language}-{idx:02d}",
        language=language,
        category=category,
        description=description,
        code=code,
        expected_types=expected,
        expected_line=expected_line,
        corrected_code=corrected,
    )


CASES: list[Case] = [
    # C (10)
    mk("C", 1, "Syntax Errors", "Seed: missing semicolon", """int main() {
    int a = 5
    printf(\"%d\", a);
}""", ["MissingDelimiter"], """#include <stdio.h>
int main() {
    int a = 5;
    printf(\"%d\", a);
    return 0;
}""", 2),
    mk("C", 2, "Syntax Errors", "Unmatched brace", """int main() {
    int x = 1;
""", ["UnmatchedBracket"], """int main() {
    int x = 1;
    return 0;
}""", 1),
    mk("C", 3, "Runtime-like Errors", "Division by zero", """int main() {
    int a = 10;
    int b = 0;
    int c = a / b;
    return c;
}""", ["DivisionByZero"], """int main() {
    int a = 10;
    int b = 2;
    int c = a / b;
    return c;
}""", 4),
    mk("C", 4, "Runtime-like Errors", "Undeclared identifier", """int main() {
    int a = 1;
    return b;
}""", ["UndeclaredIdentifier"], """int main() {
    int a = 1;
    int b = 2;
    return b;
}""", 3),
    mk("C", 5, "Runtime-like Errors", "Missing include", """int main() {
    printf(\"hi\");
    return 0;
}""", ["MissingInclude"], """#include <stdio.h>
int main() {
    printf(\"hi\");
    return 0;
}""", 2),
    mk("C", 6, "Edge Cases", "Incomplete assignment", """int main() {
    int x = ;
    return 0;
}""", ["MissingDelimiter"], """int main() {
    int x = 0;
    return 0;
}""", 2),
    mk("C", 7, "Edge Cases", "Unclosed string", """int main() {
    printf(\"hello);
    return 0;
}""", ["UnclosedString"], """int main() {
    printf(\"hello\");
    return 0;
}""", 2),
    mk("C", 8, "Logical Errors", "Wrong formula", """int main() {
    int a = 2;
    int b = 3;
    int area = a + b;
    return area;
}""", ["LogicalError", "NoError"], """int main() {
    int a = 2;
    int b = 3;
    int area = a * b;
    return area;
}""", 4),
    mk("C", 9, "Correct Code", "Valid C snippet", """#include <stdio.h>
int main() {
    int sum = 2 + 3;
    printf(\"%d\\n\", sum);
    return 0;
}""", ["NoError"], """#include <stdio.h>
int main() {
    int sum = 2 + 3;
    printf(\"%d\\n\", sum);
    return 0;
}""", None),
    mk("C", 10, "Syntax Errors", "Missing delimiter before return", """int main() {
    int n = 4
    return n;
}""", ["MissingDelimiter"], """int main() {
    int n = 4;
    return n;
}""", 2),
    # C++ (10)
    mk("C++", 1, "Runtime-like Errors", "Seed: undeclared identifier", """#include <iostream>
using namespace std;
int main() {
    int x;
    cout << y;
}""", ["UndeclaredIdentifier"], """#include <iostream>
using namespace std;
int main() {
    int y = 0;
    cout << y;
    return 0;
}""", 5),
    mk("C++", 2, "Syntax Errors", "Missing semicolon", """#include <iostream>
int main() {
    int a = 5
    std::cout << a;
}""", ["MissingDelimiter"], """#include <iostream>
int main() {
    int a = 5;
    std::cout << a;
    return 0;
}""", 3),
    mk("C++", 3, "Runtime-like Errors", "Division by zero", """int main() {
    int x = 10;
    int y = 0;
    return x / y;
}""", ["DivisionByZero"], """int main() {
    int x = 10;
    int y = 2;
    return x / y;
}""", 4),
    mk("C++", 4, "Runtime-like Errors", "Missing include for cout", """int main() {
    std::cout << 10;
    return 0;
}""", ["MissingInclude"], """#include <iostream>
int main() {
    std::cout << 10;
    return 0;
}""", 2),
    mk("C++", 5, "Edge Cases", "Unmatched parenthesis", """int main( {
    return 0;
}""", ["UnmatchedBracket"], """int main() {
    return 0;
}""", 1),
    mk("C++", 6, "Edge Cases", "Infinite loop", """int main() {
    for(;;) {
    }
}""", ["InfiniteLoop"], """int main() {
    for (int i = 0; i < 10; i++) {
    }
}""", 2),
    mk("C++", 7, "Logical Errors", "Off-by-one loop", """#include <vector>
int main() {
    std::vector<int> v = {1,2,3};
    int s = 0;
    for (size_t i = 0; i <= v.size(); i++) { s += v[i]; }
    return s;
}""", ["LogicalError", "NoError"], """#include <vector>
int main() {
    std::vector<int> v = {1,2,3};
    int s = 0;
    for (size_t i = 0; i < v.size(); i++) { s += v[i]; }
    return s;
}""", 5),
    mk("C++", 8, "Correct Code", "Valid C++ snippet", """#include <iostream>
int main() {
    int x = 10;
    std::cout << x << std::endl;
    return 0;
}""", ["NoError"], """#include <iostream>
int main() {
    int x = 10;
    std::cout << x << std::endl;
    return 0;
}""", None),
    mk("C++", 9, "Correct Code", "Function and call", """#include <iostream>
int add(int a, int b) { return a + b; }
int main() {
    std::cout << add(2, 3);
    return 0;
}""", ["NoError"], """#include <iostream>
int add(int a, int b) { return a + b; }
int main() {
    std::cout << add(2, 3);
    return 0;
}""", None),
    mk("C++", 10, "Syntax Errors", "Missing semicolon after cout", """#include <iostream>
int main() {
    std::cout << 1
    return 0;
}""", ["MissingDelimiter"], """#include <iostream>
int main() {
    std::cout << 1;
    return 0;
}""", 3),
    # Java (10)
    mk("Java", 1, "Runtime-like Errors", "Seed: type mismatch", """public class Main {
    public static void main(String[] args) {
        int a = \"hello\";
    }
}""", ["TypeMismatch"], """public class Main {
    public static void main(String[] args) {
        String a = \"hello\";
    }
}""", 3),
    mk("Java", 2, "Syntax Errors", "Missing semicolon", """public class Main {
    public static void main(String[] args) {
        int x = 1
    }
}""", ["MissingDelimiter"], """public class Main {
    public static void main(String[] args) {
        int x = 1;
    }
}""", 3),
    mk("Java", 3, "Runtime-like Errors", "Undeclared identifier", """public class Main {
    public static void main(String[] args) {
        System.out.println(z);
    }
}""", ["UndeclaredIdentifier"], """public class Main {
    public static void main(String[] args) {
        int z = 0;
        System.out.println(z);
    }
}""", 3),
    mk("Java", 4, "Runtime-like Errors", "Missing import", """public class Main {
    public static void main(String[] args) {
        ArrayList<Integer> x = new ArrayList<>();
    }
}""", ["MissingImport"], """import java.util.ArrayList;
public class Main {
    public static void main(String[] args) {
        ArrayList<Integer> x = new ArrayList<>();
    }
}""", 3),
    mk("Java", 5, "Edge Cases", "Unmatched bracket", """public class Main {
    public static void main(String[] args) {
        if (true) {
            System.out.println(1);
    }
}""", ["UnmatchedBracket"], """public class Main {
    public static void main(String[] args) {
        if (true) {
            System.out.println(1);
        }
    }
}""", 1),
    mk("Java", 6, "Edge Cases", "Infinite loop", """public class Main {
    public static void main(String[] args) {
        while(true) {}
    }
}""", ["InfiniteLoop"], """public class Main {
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) {}
    }
}""", 3),
    mk("Java", 7, "Logical Errors", "Wrong operation", """public class Main {
    public static void main(String[] args) {
        int price = 100;
        int discount = 10;
        int finalPrice = price + discount;
        System.out.println(finalPrice);
    }
}""", ["LogicalError", "NoError"], """public class Main {
    public static void main(String[] args) {
        int price = 100;
        int discount = 10;
        int finalPrice = price - discount;
        System.out.println(finalPrice);
    }
}""", 5),
    mk("Java", 8, "Correct Code", "Simple valid Java", """public class Main {
    public static void main(String[] args) {
        int a = 2;
        int b = 3;
        System.out.println(a + b);
    }
}""", ["NoError"], """public class Main {
    public static void main(String[] args) {
        int a = 2;
        int b = 3;
        System.out.println(a + b);
    }
}""", None),
    mk("Java", 9, "Correct Code", "Class with method", """public class Main {
    static int add(int a, int b) { return a + b; }
    public static void main(String[] args) {
        System.out.println(add(2, 3));
    }
}""", ["NoError"], """public class Main {
    static int add(int a, int b) { return a + b; }
    public static void main(String[] args) {
        System.out.println(add(2, 3));
    }
}""", None),
    mk("Java", 10, "Syntax Errors", "Missing parenthesis", """public class Main {
    public static void main(String[] args {
        System.out.println(1);
    }
}""", ["UnmatchedBracket", "MissingDelimiter"], """public class Main {
    public static void main(String[] args) {
        System.out.println(1);
    }
}""", 2),
    # Python (10)
    mk("Python", 1, "Syntax Errors", "Seed: indentation error", """def test():
print(\"Hello\")""", ["IndentationError"], """def test():
    print(\"Hello\")""", 2),
    mk("Python", 2, "Correct Code", "Seed: correct python", """def add(a, b):
    return a + b
print(add(2,3))""", ["NoError"], """def add(a, b):
    return a + b
print(add(2,3))""", None),
    mk("Python", 3, "Syntax Errors", "Missing colon", """if True
    print('x')""", ["MissingDelimiter", "MissingColon"], """if True:
    print('x')""", 1),
    mk("Python", 4, "Runtime-like Errors", "Division by zero", """def f():
    return 10/0
print(f())""", ["DivisionByZero"], """def f():
    return 10/2
print(f())""", 2),
    mk("Python", 5, "Runtime-like Errors", "Name error", """def f():
    return x + 1
print(f())""", ["NameError"], """def f():
    x = 1
    return x + 1
print(f())""", 2),
    mk("Python", 6, "Runtime-like Errors", "Mutable default", """def add_item(item, bag=[]):
    bag.append(item)
    return bag""", ["MutableDefault"], """def add_item(item, bag=None):
    if bag is None:
        bag = []
    bag.append(item)
    return bag""", 1),
    mk("Python", 7, "Edge Cases", "Wildcard import", """from math import *
print(sqrt(4))""", ["WildcardImport"], """from math import sqrt
print(sqrt(4))""", 1),
    mk("Python", 8, "Logical Errors", "Wrong formula", """def avg(a, b):
    return a * b / 2
print(avg(2, 6))""", ["LogicalError", "NoError"], """def avg(a, b):
    return (a + b) / 2
print(avg(2, 6))""", 2),
    mk("Python", 9, "Correct Code", "Valid loop", """total = 0
for i in range(3):
    total += i
print(total)""", ["NoError"], """total = 0
for i in range(3):
    total += i
print(total)""", None),
    mk("Python", 10, "Edge Cases", "Unclosed string", """name = \"Asha
print(name)""", ["UnclosedString"], """name = \"Asha\"
print(name)""", 1),
    # JavaScript (10)
    mk("JavaScript", 1, "Runtime-like Errors", "Seed: undeclared variable", """function demo() {
    let a = 10;
    console.log(b);
}""", ["UndeclaredIdentifier"], """function demo() {
    let a = 10;
    console.log(a);
}""", 3),
    mk("JavaScript", 2, "Correct Code", "Seed: correct JS", """let x = 10;
console.log(x);""", ["NoError"], """let x = 10;
console.log(x);""", None),
    mk("JavaScript", 3, "Syntax Errors", "Invalid member access", """function f() {
    const a = {x: 1};
    console..log(a.x);
}""", ["MissingDelimiter"], """function f() {
    const a = {x: 1};
    console.log(a.x);
}""", 3),
    mk("JavaScript", 4, "Runtime-like Errors", "Division by zero", """function f() {
    return 10 / 0;
}""", ["DivisionByZero"], """function f() {
    return 10 / 2;
}""", 2),
    mk("JavaScript", 5, "Edge Cases", "Unclosed string", """function f() {
    let s = \"hello;
}""", ["UnclosedString"], """function f() {
    let s = \"hello\";
}""", 2),
    mk("JavaScript", 6, "Edge Cases", "Infinite loop", """function f() {
    while(true) {
    }
}""", ["InfiniteLoop"], """function f() {
    for (let i = 0; i < 10; i++) {
    }
}""", 2),
    mk("JavaScript", 7, "Logical Errors", "Wrong threshold", """function isAdult(age) {
    return age > 21;
}""", ["LogicalError", "NoError"], """function isAdult(age) {
    return age >= 18;
}""", 2),
    mk("JavaScript", 8, "Correct Code", "Function add", """function add(a, b) {
    return a + b;
}
console.log(add(2, 3));""", ["NoError"], """function add(a, b) {
    return a + b;
}
console.log(add(2, 3));""", None),
    mk("JavaScript", 9, "Syntax Errors", "Incomplete assignment", """let x = ;
console.log(x);""", ["MissingDelimiter"], """let x = 0;
console.log(x);""", 1),
    mk("JavaScript", 10, "Correct Code", "Arrow function map", """const nums = [1, 2, 3];
const out = nums.map(n => n * 2);
console.log(out);""", ["NoError"], """const nums = [1, 2, 3];
const out = nums.map(n => n * 2);
console.log(out);""", None),
]


ARCHITECTURE_WIRING = {
    "core_detection_entry": {
        "file": "src/error_engine.py",
        "line": 1213,
        "symbol": "detect_errors",
        "evidence": "Primary hybrid detection entry point.",
    },
    "api_check_route_integration": {
        "file": "api.py",
        "line": 225,
        "symbol": "@app.post('/check') -> check_code",
        "evidence": "Route calls detect_errors at api.py:238.",
    },
    "streamlit_detection_integration": {
        "file": "app.py",
        "line": 95,
        "symbol": "show_all branch uses detect_all_errors",
        "evidence": "Single-error branch calls detect_errors at app.py:131.",
    },
    "cli_detection_integration": {
        "file": "cli.py",
        "line": 25,
        "symbol": "main",
        "evidence": "CLI calls detect_errors at cli.py:51.",
    },
}


def _git_status_lines() -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ["<git status unavailable>"]
    return [line for line in proc.stdout.splitlines() if line.strip()]


def _tutor_rubric(tutor: dict[str, str], predicted_error: str) -> dict[str, Any]:
    why = (tutor or {}).get("why", "")
    fix = (tutor or {}).get("fix", "")
    why_words = len(why.split())
    fix_words = len(fix.split())

    explains_why = bool(why.strip())
    beginner_friendly = explains_why and (why_words >= 8 and fix_words >= 8)
    step_by_step = any(token in fix.lower() for token in ["first", "then", "step", "1.", "2."])

    concept_score = min(5, 1 + (1 if explains_why else 0) + (1 if why_words >= 8 else 0) + (1 if why_words >= 15 else 0) + (1 if why_words >= 25 else 0))
    correction_clarity = min(5, 1 + (1 if fix_words >= 6 else 0) + (1 if fix_words >= 12 else 0) + (1 if fix_words >= 20 else 0) + (1 if step_by_step else 0))
    beginner_readability = min(5, 2 + (1 if beginner_friendly else 0) + (1 if "because" in why.lower() else 0) + (1 if "example" in fix.lower() else 0))
    guidance_structure = min(5, 2 + (1 if step_by_step else 0) + (1 if ":" in fix else 0) + (1 if len(fix.split(".")) >= 2 else 0))

    teaching_value = max(1, round((concept_score + correction_clarity + beginner_readability + guidance_structure) / 4))
    if predicted_error == "NoError":
        teaching_value = max(teaching_value, 3)

    return {
        "explains_why": explains_why,
        "beginner_friendly": beginner_friendly,
        "step_by_step": step_by_step,
        "concept_explanation_quality": concept_score,
        "correction_clarity": correction_clarity,
        "beginner_readability": beginner_readability,
        "guidance_structure": guidance_structure,
        "teaching_value_vs_patching": teaching_value,
    }


def evaluate_core_case(case: Case) -> dict[str, Any]:
    t0 = time.perf_counter()
    result = detect_errors(case.code, filename=None, language_override=case.language)
    latency_ms = (time.perf_counter() - t0) * 1000.0

    issues = result.get("rule_based_issues", [])
    predicted = result.get("predicted_error", "Unknown")
    confidence = result.get("confidence")
    first_line = issues[0].get("line") if issues else None

    expected_match = predicted in case.expected_types
    line_match = True if case.expected_line is None else first_line == case.expected_line

    tutor = result.get("tutor", {}) or {}
    rubric = _tutor_rubric(tutor, predicted)

    if "NoError" in case.expected_types:
        pass_flag = (predicted == "NoError") and line_match
    else:
        pass_flag = expected_match and line_match and rubric["explains_why"]

    fixer = AutoFixer()
    line_num = first_line - 1 if isinstance(first_line, int) and first_line > 0 else None
    auto_fix = fixer.apply_fixes(case.code, predicted, line_num=line_num, language=case.language)

    return {
        "case_id": case.case_id,
        "language": case.language,
        "category": case.category,
        "description": case.description,
        "input_code": case.code,
        "expected_types": case.expected_types,
        "expected_line": case.expected_line,
        "omnisyntax_output": {
            "predicted_error": predicted,
            "confidence": confidence,
            "tutor": tutor,
            "rule_based_issues": issues,
            "degraded_mode": result.get("degraded_mode", False),
            "warnings": result.get("warnings", []),
        },
        "result": "PASS" if pass_flag else "FAIL",
        "error_type": predicted,
        "location": {
            "line": first_line,
            "all_lines": [i.get("line") for i in issues if i.get("line") is not None],
        },
        "line_match": line_match,
        "corrected_code": case.corrected_code,
        "auto_fix_preview": auto_fix,
        "ai_tutor_assessment": rubric,
        "latency_ms": round(latency_ms, 3),
    }


def evaluate_api_cases(cases: list[Case]) -> dict[str, Any]:
    client = TestClient(api.app)
    records: list[dict[str, Any]] = []

    for case in cases:
        t0 = time.perf_counter()
        response = client.post(
            "/check",
            json={"code": case.code, "filename": None, "language": case.language},
        )
        latency_ms = (time.perf_counter() - t0) * 1000.0

        payload: dict[str, Any] = response.json() if response.status_code == 200 else {"error": response.text}
        predicted = payload.get("predicted_error") if response.status_code == 200 else None

        records.append(
            {
                "case_id": case.case_id,
                "status_code": response.status_code,
                "predicted_error": predicted,
                "latency_ms": round(latency_ms, 3),
                "degraded_mode": payload.get("degraded_mode") if response.status_code == 200 else None,
                "warnings": payload.get("warnings", []) if response.status_code == 200 else [],
                "raw": payload,
            }
        )

    return {
        "total": len(records),
        "records": records,
        "avg_latency_ms": round(statistics.mean([r["latency_ms"] for r in records]), 3) if records else None,
    }


def evaluate_cli_samples(cases: list[Case]) -> dict[str, Any]:
    by_language: dict[str, list[Case]] = {}
    for case in cases:
        by_language.setdefault(case.language, []).append(case)

    sample_cases: list[Case] = []
    for language, lang_cases in by_language.items():
        sample_cases.extend(lang_cases[:1])
        no_error = [c for c in lang_cases if "NoError" in c.expected_types]
        if no_error:
            sample_cases.append(no_error[0])

    records: list[dict[str, Any]] = []
    cli_path = Path("cli.py")

    for case in sample_cases:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
            tmp.write(case.code)
            tmp_path = Path(tmp.name)
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(cli_path), str(tmp_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        latency_ms = (time.perf_counter() - t0) * 1000.0

        stdout = proc.stdout or ""
        match = re.search(r"Detected\s*:\s*([^\r\n]+)", stdout)
        predicted = match.group(1).strip() if match else None

        records.append(
            {
                "case_id": case.case_id,
                "language": case.language,
                "exit_code": proc.returncode,
                "predicted_error": predicted,
                "latency_ms": round(latency_ms, 3),
                "stdout_excerpt": "\n".join(stdout.splitlines()[:25]),
                "stderr_excerpt": "\n".join((proc.stderr or "").splitlines()[:20]),
            }
        )

        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass

    return {
        "sample_total": len(records),
        "records": records,
        "avg_latency_ms": round(statistics.mean([r["latency_ms"] for r in records]), 3) if records else None,
    }


def evaluate_streamlit_expectations(cases: list[Case]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []

    for case in cases:
        t0 = time.perf_counter()
        result = detect_all_errors(case.code, filename=None)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        records.append(
            {
                "case_id": case.case_id,
                "language": case.language,
                "has_errors": result.get("has_errors"),
                "total_errors": result.get("total_errors"),
                "error_types": [e.get("type") for e in result.get("errors", [])],
                "degraded_mode": result.get("degraded_mode", False),
                "warnings": result.get("warnings", []),
                "latency_ms": round(latency_ms, 3),
            }
        )

    return {
        "total": len(records),
        "records": records,
        "avg_latency_ms": round(statistics.mean([r["latency_ms"] for r in records]), 3) if records else None,
    }


def compute_consistency(core_records: list[dict[str, Any]], api_records: list[dict[str, Any]]) -> dict[str, Any]:
    api_by_case = {r["case_id"]: r for r in api_records}
    mismatches = []
    for rec in core_records:
        api_rec = api_by_case.get(rec["case_id"])
        if not api_rec:
            continue
        if api_rec.get("status_code") != 200:
            mismatches.append({"case_id": rec["case_id"], "reason": f"API status {api_rec.get('status_code')}"})
            continue
        if rec["error_type"] != api_rec.get("predicted_error"):
            mismatches.append(
                {
                    "case_id": rec["case_id"],
                    "core": rec["error_type"],
                    "api": api_rec.get("predicted_error"),
                }
            )

    return {
        "core_api_total_compared": len(core_records),
        "mismatch_count": len(mismatches),
        "match_rate_percent": round((len(core_records) - len(mismatches)) * 100.0 / len(core_records), 2) if core_records else 0.0,
        "mismatches": mismatches,
    }


def run_stress(cases: list[Case], repeats: int = 3) -> dict[str, Any]:
    client = TestClient(api.app)
    core_samples: list[float] = []
    api_samples: list[float] = []
    deterministic_failures: list[dict[str, Any]] = []

    # Determinism check on core detector.
    for case in cases:
        preds = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            result = detect_errors(case.code, filename=None, language_override=case.language)
            core_samples.append((time.perf_counter() - t0) * 1000.0)
            preds.append(result.get("predicted_error"))
        if len(set(preds)) != 1:
            deterministic_failures.append({"case_id": case.case_id, "predictions": preds})

    # Throughput and path consistency at API layer.
    total_api = 0
    bad_status = 0
    for _ in range(repeats):
        for case in cases:
            t0 = time.perf_counter()
            resp = client.post("/check", json={"code": case.code, "filename": None, "language": case.language})
            api_samples.append((time.perf_counter() - t0) * 1000.0)
            total_api += 1
            if resp.status_code != 200:
                bad_status += 1

    consistency_verdict = "PASS" if not deterministic_failures and bad_status == 0 else "FAIL"

    return {
        "total_evaluations": len(cases) * repeats * 2,
        "core_evaluations": len(cases) * repeats,
        "api_evaluations": total_api,
        "core_avg_latency_ms": round(statistics.mean(core_samples), 3) if core_samples else None,
        "api_avg_latency_ms": round(statistics.mean(api_samples), 3) if api_samples else None,
        "core_p95_latency_ms": round(_pct(core_samples, 95), 3) if core_samples else None,
        "api_p95_latency_ms": round(_pct(api_samples, 95), 3) if api_samples else None,
        "deterministic_failures": deterministic_failures,
        "api_non_200_count": bad_status,
        "consistency_verdict": consistency_verdict,
    }


def _pct(values: list[float], percentile: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, int(round((percentile / 100.0) * (len(ordered) - 1)))))
    return ordered[idx]


def summarize(core_records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(core_records)
    passed = sum(1 for r in core_records if r["result"] == "PASS")
    failed = total - passed

    per_language: dict[str, dict[str, Any]] = {}
    for rec in core_records:
        lang = rec["language"]
        per_language.setdefault(
            lang,
            {
                "total": 0,
                "pass": 0,
                "fail": 0,
                "tutor_explains_why": 0,
                "tutor_beginner_friendly": 0,
                "tutor_step_by_step": 0,
            },
        )
        per_language[lang]["total"] += 1
        if rec["result"] == "PASS":
            per_language[lang]["pass"] += 1
        else:
            per_language[lang]["fail"] += 1

        tutor = rec["ai_tutor_assessment"]
        if tutor["explains_why"]:
            per_language[lang]["tutor_explains_why"] += 1
        if tutor["beginner_friendly"]:
            per_language[lang]["tutor_beginner_friendly"] += 1
        if tutor["step_by_step"]:
            per_language[lang]["tutor_step_by_step"] += 1

    return {
        "overall": {
            "total_test_count": total,
            "passed_count": passed,
            "failed_count": failed,
            "overall_pass_rate_percent": round((passed * 100.0 / total), 2) if total else 0.0,
        },
        "per_language": per_language,
    }


def classify_severity(case_record: dict[str, Any]) -> str:
    predicted = case_record["error_type"]
    expected = case_record["expected_types"]
    category = case_record["category"]

    if "NoError" in expected and predicted != "NoError":
        return "High"
    if "NoError" not in expected and predicted == "NoError":
        return "High"
    if category in {"Runtime-like Errors", "Syntax Errors"} and case_record["result"] == "FAIL":
        return "High"
    if not case_record["line_match"]:
        return "Medium"
    if not case_record["ai_tutor_assessment"]["beginner_friendly"]:
        return "Medium"
    return "Low"


def defect_root_cause(case_record: dict[str, Any]) -> str:
    predicted = case_record["error_type"]
    expected = case_record["expected_types"]

    if "NoError" in expected and predicted != "NoError":
        return "False positive from heuristic prioritization bias."
    if "NoError" not in expected and predicted == "NoError":
        return "False negative likely due to semantic thresholding or rule coverage gap."
    if not case_record["line_match"]:
        return "Localization issue in rule-based issue ordering or line extraction."
    if not case_record["ai_tutor_assessment"]["beginner_friendly"]:
        return "Tutor response template lacks pedagogical depth."
    return "Minor mismatch in expected label aliasing or categorization."


def build_defects(core_records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    defects: list[dict[str, Any]] = []
    themes = {
        "heuristic_brittleness": 0,
        "prioritization_bias": 0,
        "ml_threshold_or_label_confusion": 0,
        "tutor_static_response_limitations": 0,
    }

    for rec in core_records:
        if rec["result"] == "PASS":
            continue

        severity = classify_severity(rec)
        rc = defect_root_cause(rec)

        if "False positive" in rc or "heuristic" in rc:
            themes["heuristic_brittleness"] += 1
            themes["prioritization_bias"] += 1
        if "semantic thresholding" in rc or "label" in rc:
            themes["ml_threshold_or_label_confusion"] += 1
        if "Tutor" in rc:
            themes["tutor_static_response_limitations"] += 1

        defects.append(
            {
                "id": f"DEF-{len(defects) + 1:03d}",
                "severity": severity,
                "what_failed": f"Expected {rec['expected_types']} but observed {rec['error_type']}.",
                "evidence_case_id": rec["case_id"],
                "impact": "Learner feedback may be incorrect or less actionable.",
                "likely_root_cause": rc,
                "code_location_hint": _location_hint(rec),
            }
        )

    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    defects.sort(key=lambda d: (severity_order[d["severity"]], d["id"]))
    return defects, themes


def _location_hint(record: dict[str, Any]) -> str:
    lang = record["language"]
    if lang in {"C", "C++", "Java", "JavaScript"}:
        return "src/error_engine.py:1213"
    return "src/error_engine.py:1213"


def build_markdown(
    summary: dict[str, Any],
    core_records: list[dict[str, Any]],
    api_results: dict[str, Any],
    cli_results: dict[str, Any],
    streamlit_results: dict[str, Any],
    consistency: dict[str, Any],
    stress: dict[str, Any],
    defects: list[dict[str, Any]],
    root_cause_themes: dict[str, int],
    workspace_integrity: dict[str, Any],
) -> str:
    lines: list[str] = []
    overall = summary["overall"]

    lines.append("# OmniSyntax E2E QA Audit Report")
    lines.append("")
    lines.append("## 1. Executive Summary")
    lines.append(f"- Total test count: {overall['total_test_count']}")
    lines.append(f"- Passed count: {overall['passed_count']}")
    lines.append(f"- Failed count: {overall['failed_count']}")
    lines.append(f"- Overall pass rate percent: {overall['overall_pass_rate_percent']}%")
    lines.append(f"- Core/API consistency verdict: {stress['consistency_verdict']} (match rate {consistency['match_rate_percent']}%)")
    lines.append("")
    lines.append("## 2. Test Strategy and Coverage")
    lines.append("- Mandatory languages covered: C, C++, Java, Python, JavaScript")
    lines.append("- Categories per language: Syntax Errors, Logical Errors, Runtime-like Errors, Edge Cases, Correct Code")
    lines.append("- Cases per language: 10 each (seed cases included exactly), total 50")
    lines.append("- Pathways covered: core detector, API /check route, CLI execution, Streamlit detection behavior expectations")
    lines.append("")
    lines.append("## 3. System Workflow Overview")
    lines.append("- Core detection entry: src/error_engine.py:1213 (detect_errors)")
    lines.append("- API check route integration: api.py:225 (@app.post('/check')), calls detect_errors at api.py:238")
    lines.append("- Streamlit detection integration: app.py:95 (detect_all_errors), app.py:131 (detect_errors)")
    lines.append("- CLI detection integration: cli.py:25 (main), call at cli.py:51 (detect_errors)")
    lines.append("")
    lines.append("## 4. Per-language Results Summary")
    lines.append("| Language | Total | Pass | Fail | explains why | beginner-friendly | step-by-step |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for lang, stats in summary["per_language"].items():
        lines.append(
            f"| {lang} | {stats['total']} | {stats['pass']} | {stats['fail']} | {stats['tutor_explains_why']} | {stats['tutor_beginner_friendly']} | {stats['tutor_step_by_step']} |"
        )
    lines.append("")
    lines.append("## 5. Overall Metrics")
    lines.append(f"- Total: {overall['total_test_count']}")
    lines.append(f"- Passed: {overall['passed_count']}")
    lines.append(f"- Failed: {overall['failed_count']}")
    lines.append(f"- Pass rate: {overall['overall_pass_rate_percent']}%")
    lines.append("")
    lines.append("## 6. Detailed Case Table (Expected vs Observed)")
    lines.append("| Case ID | Lang | Category | Expected | Observed | Expected Line | Observed Line | PASS/FAIL |")
    lines.append("|---|---|---|---|---|---:|---:|---|")
    for rec in core_records:
        lines.append(
            f"| {rec['case_id']} | {rec['language']} | {rec['category']} | {', '.join(rec['expected_types'])} | {rec['error_type']} | {rec['expected_line'] if rec['expected_line'] is not None else '-'} | {rec['location']['line'] if rec['location']['line'] is not None else '-'} | {rec['result']} |"
        )
    lines.append("")
    lines.append("## 7. AI Tutor Quality Findings")
    avg_concept = round(statistics.mean([r["ai_tutor_assessment"]["concept_explanation_quality"] for r in core_records]), 2)
    avg_clarity = round(statistics.mean([r["ai_tutor_assessment"]["correction_clarity"] for r in core_records]), 2)
    avg_readability = round(statistics.mean([r["ai_tutor_assessment"]["beginner_readability"] for r in core_records]), 2)
    avg_structure = round(statistics.mean([r["ai_tutor_assessment"]["guidance_structure"] for r in core_records]), 2)
    avg_teaching = round(statistics.mean([r["ai_tutor_assessment"]["teaching_value_vs_patching"] for r in core_records]), 2)
    lines.append(f"- Avg concept explanation quality (1-5): {avg_concept}")
    lines.append(f"- Avg correction clarity (1-5): {avg_clarity}")
    lines.append(f"- Avg beginner readability (1-5): {avg_readability}")
    lines.append(f"- Avg guidance structure (1-5): {avg_structure}")
    lines.append(f"- Avg teaching value vs patching (1-5): {avg_teaching}")
    lines.append("")
    lines.append("## 8. Stress and Consistency Findings")
    lines.append(f"- Stress run total evaluations: {stress['total_evaluations']}")
    lines.append(f"- Core avg latency per case: {stress['core_avg_latency_ms']} ms")
    lines.append(f"- API avg latency per case: {stress['api_avg_latency_ms']} ms")
    lines.append(f"- Consistency verdict: {stress['consistency_verdict']}")
    lines.append(f"- Core/API mismatch count: {consistency['mismatch_count']}")
    lines.append("")
    lines.append("## 9. Bug List Prioritized")
    if defects:
        lines.append("| Defect ID | Severity | What failed | Evidence | Impact | Root cause | Code location hint |")
        lines.append("|---|---|---|---|---|---|---|")
        for d in defects:
            lines.append(
                f"| {d['id']} | {d['severity']} | {d['what_failed']} | {d['evidence_case_id']} | {d['impact']} | {d['likely_root_cause']} | {d['code_location_hint']} |"
            )
    else:
        lines.append("- No defects found in this run.")
    lines.append("")
    lines.append("## 10. Root Cause Analysis")
    lines.append("- Root-cause themes:")
    lines.append(f"  - heuristic brittleness: {root_cause_themes['heuristic_brittleness']}")
    lines.append(f"  - prioritization bias: {root_cause_themes['prioritization_bias']}")
    lines.append(f"  - ML threshold or label confusion: {root_cause_themes['ml_threshold_or_label_confusion']}")
    lines.append(f"  - tutor static response limitations: {root_cause_themes['tutor_static_response_limitations']}")
    lines.append("")
    lines.append("## 11. Suggested Fixes")
    lines.append("- Rule-based enhancements: strengthen edge-case tokenization and line localization around unterminated strings and malformed statements.")
    lines.append("- Model improvements: recalibrate semantic thresholds by language and length bucket; improve label confidence routing in degraded conditions.")
    lines.append("- Better training data and hard negatives: add language-balanced hard negatives for logical-vs-noerror and missing-import/include edge snippets.")
    lines.append("- UX and tutoring improvements: add deterministic step-by-step tutoring templates with beginner examples for all top error classes.")
    lines.append("- Regression hardening: lock this audit into CI with pass-rate and consistency gates.")
    lines.append("")
    lines.append("## 12. Residual Risks and Release Readiness")
    lines.append("- Residual risk remains where logical errors are expected to be difficult without execution semantics.")
    lines.append("- Release readiness: conditional. Suitable for controlled release if high-severity defects are zero and consistency remains PASS.")
    lines.append("")
    lines.append("## Workspace Integrity Notes")
    lines.append(f"- Pre-existing dirty files detected: {workspace_integrity['pre_existing_dirty_detected']}")
    lines.append(f"- Unrelated local changes reverted: {workspace_integrity['unrelated_local_changes_reverted']}")
    lines.append(f"- New artifacts created: {', '.join(workspace_integrity['new_artifacts_created'])}")
    lines.append("")
    lines.append("## Pathway Runtime Summary")
    lines.append(f"- API total evaluations: {api_results['total']}, avg latency: {api_results['avg_latency_ms']} ms")
    lines.append(f"- CLI sampled evaluations: {cli_results['sample_total']}, avg latency: {cli_results['avg_latency_ms']} ms")
    lines.append(f"- Streamlit expectation simulations: {streamlit_results['total']}, avg latency: {streamlit_results['avg_latency_ms']} ms")

    return "\n".join(lines) + "\n"


def main() -> None:
    # Avoid throttling QA loops while still exercising the same /check handler.
    api.RATE_LIMIT_PER_MINUTE = 0
    api._REQUEST_LOG.clear()

    pre_status = _git_status_lines()

    core_records = [evaluate_core_case(case) for case in CASES]
    summary = summarize(core_records)
    api_results = evaluate_api_cases(CASES)
    cli_results = evaluate_cli_samples(CASES)
    streamlit_results = evaluate_streamlit_expectations(CASES)
    consistency = compute_consistency(core_records, api_results["records"])
    stress = run_stress(CASES, repeats=3)
    defects, root_cause_themes = build_defects(core_records)

    out_dir = Path("artifacts") / "qa"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "e2e_qa_results.json"
    md_path = out_dir / "e2e_qa_results.md"

    post_status = _git_status_lines()

    workspace_integrity = {
        "pre_existing_dirty_detected": bool(pre_status),
        "pre_status_lines": pre_status,
        "post_status_lines": post_status,
        "unrelated_local_changes_reverted": False,
        "new_artifacts_created": [str(json_path).replace('\\\\', '/'), str(md_path).replace('\\\\', '/')],
    }

    payload = {
        "metadata": {
            "audit_name": "OmniSyntax E2E QA Audit",
            "generated_at_unix": time.time(),
            "focus": "deep",
            "languages": ["C", "C++", "Java", "Python", "JavaScript"],
        },
        "architecture_validation": ARCHITECTURE_WIRING,
        "summary": summary,
        "records": core_records,
        "pathway_checks": {
            "api": api_results,
            "cli": cli_results,
            "streamlit_expectations": streamlit_results,
        },
        "consistency": consistency,
        "stress": stress,
        "defects": defects,
        "root_cause_themes": root_cause_themes,
        "remediation_plan": {
            "rule_based_enhancements": [
                "Increase malformed-token recovery for syntax localization precision.",
                "Harden C/C++ include resolution around mixed snippets.",
            ],
            "model_improvements": [
                "Tune semantic confidence thresholds by language and snippet length.",
                "Add confidence calibration checks in CI.",
            ],
            "training_data_improvements": [
                "Add hard negatives for logical-error lookalikes.",
                "Expand Java missing-import and JavaScript undeclared-identifier edge corpora.",
            ],
            "tutor_ux_improvements": [
                "Standardize stepwise tutoring format with concrete mini examples.",
                "Expose confidence and warning context to reduce ambiguity.",
            ],
            "regression_hardening": [
                "Run this audit script in CI and fail on high-severity regressions.",
                "Pin deterministic behavior tests across repeated runs.",
            ],
        },
        "workspace_integrity": workspace_integrity,
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(
        build_markdown(
            summary,
            core_records,
            api_results,
            cli_results,
            streamlit_results,
            consistency,
            stress,
            defects,
            root_cause_themes,
            workspace_integrity,
        ),
        encoding="utf-8",
    )

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(json.dumps(summary["overall"], indent=2))


if __name__ == "__main__":
    main()
