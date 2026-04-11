"""
Advanced stress testing for OmniSyntax detector stability and prioritization.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.error_engine import C_LIKE_ISSUE_PRIORITY, detect_errors


@dataclass(frozen=True)
class StressCase:
    case_id: str
    language: str
    category: str
    code: str
    expected_any: tuple[str, ...]


STRESS_CASES: list[StressCase] = [
    StressCase(
        case_id="py-overlap-missingimport-typemismatch",
        language="Python",
        category="multi_error_overlap",
        code=(
            "def build() -> int:\n"
            "    arr = np.array([1, 2, 3])\n"
            "    return 'x'\n"
        ),
        expected_any=("MissingImport", "TypeMismatch"),
    ),
    StressCase(
        case_id="py-nested-unreachable",
        language="Python",
        category="nested_edge",
        code=(
            "def f(flag):\n"
            "    if flag:\n"
            "        return 1\n"
            "        x = 2\n"
            "    return 0\n"
        ),
        expected_any=("UnreachableCode",),
    ),
    StressCase(
        case_id="py-large-line-and-unused",
        language="Python",
        category="large_snippet",
        code=(
            "def render():\n"
            "    payload = '" + ("x" * 140) + "'\n"
            "    return 1\n"
        ),
        expected_any=("LineTooLong",),
    ),
    StressCase(
        case_id="java-overlap-import-typemismatch",
        language="Java",
        category="multi_error_overlap",
        code=(
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        ArrayList<Integer> xs = new ArrayList<>();\n"
            "        int n = \"7\";\n"
            "    }\n"
            "}\n"
        ),
        expected_any=("TypeMismatch", "MissingImport"),
    ),
    StressCase(
        case_id="java-overlap-unreachable-infinite",
        language="Java",
        category="multi_error_overlap",
        code=(
            "public class Main {\n"
            "    static void f() {\n"
            "        while (true) {\n"
            "            continue;\n"
            "            int y = 1;\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        expected_any=("UnreachableCode",),
    ),
    StressCase(
        case_id="java-large-line",
        language="Java",
        category="large_snippet",
        code=(
            "public class Main { public static void main(String[] args) { "
            "String s = \"" + ("y" * 130) + "\"; System.out.println(s); } }\n"
        ),
        expected_any=("LineTooLong",),
    ),
    StressCase(
        case_id="c-overlap-unreachable-infinite",
        language="C",
        category="multi_error_overlap",
        code=(
            "int main() {\n"
            "    while (1) {\n"
            "        break;\n"
            "        int y = 2;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_any=("UnreachableCode",),
    ),
    StressCase(
        case_id="cpp-overlap-include-undeclared",
        language="C++",
        category="multi_error_overlap",
        code=(
            "#include <cstdio>\n"
            "int main() {\n"
            "    printf(\"%d\", value);\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_any=("UndeclaredIdentifier",),
    ),
    StressCase(
        case_id="cpp-nested-dangling",
        language="C++",
        category="nested_edge",
        code=(
            "int* bad() {\n"
            "    int local = 3;\n"
            "    return &local;\n"
            "}\n"
            "int main() {\n"
            "    int *p = bad();\n"
            "    if (p) return *p;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_any=("DanglingPointer",),
    ),
    StressCase(
        case_id="js-overlap-unreachable-undeclared",
        language="JavaScript",
        category="multi_error_overlap",
        code=(
            "function g() {\n"
            "  throw new Error('x');\n"
            "  console.log(missing_name);\n"
            "}\n"
        ),
        expected_any=("UnreachableCode", "UndeclaredIdentifier"),
    ),
    StressCase(
        case_id="js-overlap-dup-unreachable",
        language="JavaScript",
        category="multi_error_overlap",
        code=(
            "function f() {\n"
            "  let x = 1;\n"
            "  let x = 2;\n"
            "  return x;\n"
            "  console.log(x);\n"
            "}\n"
        ),
        expected_any=("DuplicateDefinition", "UnreachableCode"),
    ),
    StressCase(
        case_id="js-large-line",
        language="JavaScript",
        category="large_snippet",
        code=("const payload = '" + ("z" * 135) + "';\n"),
        expected_any=("LineTooLong", "NoError"),
    ),
]


def _variants(code: str) -> list[str]:
    return [
        code,
        code + "\n",
        code.replace("    ", "  "),
    ]


def run() -> dict:
    rows: list[dict] = []
    stability_failures = 0
    priority_mismatches = 0

    for case in STRESS_CASES:
        result = detect_errors(case.code, language_override=case.language)
        predicted = str(result.get("predicted_error", "NoError"))
        pass_expected = predicted in case.expected_any

        variant_preds = []
        for variant in _variants(case.code):
            variant_result = detect_errors(variant, language_override=case.language)
            variant_preds.append(str(variant_result.get("predicted_error", "NoError")))
        stable = len(set(variant_preds)) == 1
        if not stable:
            stability_failures += 1

        rule_issues = result.get("rule_based_issues", [])
        issue_types = [str(issue.get("type")) for issue in rule_issues if issue.get("type")]
        priority_ok = True
        if len(issue_types) > 1 and case.language in {"Java", "C", "C++", "JavaScript"}:
            ranked = sorted(
                issue_types,
                key=lambda t: (
                    C_LIKE_ISSUE_PRIORITY.index(t) if t in C_LIKE_ISSUE_PRIORITY else len(C_LIKE_ISSUE_PRIORITY),
                ),
            )
            priority_ok = (predicted == ranked[0])
            if not priority_ok:
                priority_mismatches += 1

        rows.append(
            {
                "case_id": case.case_id,
                "language": case.language,
                "category": case.category,
                "expected_any": list(case.expected_any),
                "predicted": predicted,
                "pass_expected": pass_expected,
                "stable_prediction": stable,
                "variant_predictions": variant_preds,
                "priority_consistent": priority_ok,
                "rule_types": issue_types,
                "confidence": result.get("confidence"),
            }
        )

    total = len(rows)
    pass_count = sum(1 for row in rows if row["pass_expected"])
    summary = {
        "total_cases": total,
        "pass_cases": pass_count,
        "fail_cases": total - pass_count,
        "stability_failures": stability_failures,
        "priority_mismatches": priority_mismatches,
    }
    return {"summary": summary, "cases": rows}


def main() -> None:
    payload = run()
    out = Path("artifacts/qa/stress-replay-batch4.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
