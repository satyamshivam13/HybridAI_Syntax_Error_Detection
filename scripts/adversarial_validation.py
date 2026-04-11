"""
Adversarial validation for OmniSyntax production-readiness claims.

Goals:
1) Detect overfitting vs internal 240-case benchmark
2) Stress real-world messy/partial/mixed snippets
3) Audit multi-error handling and priority behavior
4) Audit confidence score integrity
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.error_engine import C_LIKE_ISSUE_PRIORITY, detect_errors
from src.multi_error_detector import detect_all_errors


@dataclass(frozen=True)
class StrictCase:
    case_id: str
    language: str
    expected: str
    code: str
    category: str
    root_cause_hint: str
    filename: str | None = None
    use_override: bool = True


@dataclass(frozen=True)
class MultiCase:
    case_id: str
    language: str
    expected_types: tuple[str, ...]
    expected_primary: str
    code: str
    category: str


@dataclass(frozen=True)
class FamilyCase:
    family: str
    language: str
    expected: str
    code: str


COMMENT_PREFIX = {
    "Python": "#",
    "Java": "//",
    "C": "//",
    "C++": "//",
    "JavaScript": "//",
}

FILE_EXT = {
    "Python": ".py",
    "Java": ".java",
    "C": ".c",
    "C++": ".cpp",
    "JavaScript": ".js",
}


def _baseline_records() -> list[dict]:
    path = REPO_ROOT / "artifacts" / "qa" / "mapping_audit_2026-04-11.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["records"]


def _inject_noise(code: str, language: str) -> str:
    comment = COMMENT_PREFIX[language]
    lines = code.splitlines()
    noisy: list[str] = [f"{comment} adversarial-noise-header"]
    for line in lines:
        if line.strip():
            noisy.append(line + "  ")
        else:
            noisy.append(line)
    noisy.append(f"{comment} trailing-noise")
    return "\n".join(noisy) + ("\n" if code.endswith("\n") else "")


def _mutate_preserve_intent(record: dict) -> tuple[str, str]:
    """
    Return mutated_code, mutation_tag.
    Designed to keep semantic intent while changing shape/surface features.
    """
    language = record["language"]
    expected = record["expected"]
    code = str(record["code"])
    mutated = _inject_noise(code, language)
    tag = "noise_only"

    if expected in {"NameError", "UndeclaredIdentifier"}:
        mutated = re.sub(r"\b(total|price|tax|missing_value|user_name|value2|missingVar|y|z)\b", "missing_symbol_qa", mutated)
        tag = "identifier_rename"

    elif expected == "DivisionByZero":
        new = re.sub(r"/\s*0(\.0+)?\b", "/ (2-2)", mutated, count=1)
        new = re.sub(r"%\s*0(\.0+)?\b", "% (3-3)", new, count=1)
        if new != mutated:
            mutated = new
            tag = "nonliteral_zero"

    elif expected == "InfiniteLoop":
        repl = {
            "Python": (r"\bwhile\s+(True|1)\s*:", "while (1 == 1):"),
            "Java": (r"\bwhile\s*\(\s*true\s*\)", "while ((2 > 1))"),
            "C": (r"\bwhile\s*\(\s*1\s*\)", "while ((2 > 1))"),
            "C++": (r"\bwhile\s*\(\s*1\s*\)", "while ((2 > 1))"),
            "JavaScript": (r"\bwhile\s*\(\s*true\s*\)", "while ((2 > 1))"),
        }
        pattern, replacement = repl[language]
        new = re.sub(pattern, replacement, mutated, flags=re.IGNORECASE)
        if new != mutated:
            mutated = new
            tag = "equivalent_loop_condition"

    elif expected == "MissingImport" and language == "Python":
        new = mutated.replace("math.sqrt", "statistics.mean")
        new = new.replace("datetime.datetime.now()", "zoneinfo.ZoneInfo('UTC')")
        new = new.replace("np.array", "numpy.array")
        if new != mutated:
            mutated = new
            tag = "unknown_import_symbol_set"

    elif expected == "ImportError":
        new = mutated.replace("does_not_exist", "vendor_pkg_alpha")
        new = new.replace("imaginary_pkg_123", "vendor_pkg_beta")
        new = new.replace("ghostlib", "vendor_pkg_gamma")
        if new != mutated:
            mutated = new
            tag = "importerror_nonplaceholder_name"

    elif expected == "LineTooLong":
        # Keep long line intent but change structure to concatenation.
        if language == "Python":
            new = re.sub(r"('([^']{120,})')", r"'X'*130", mutated, count=1)
            if new != mutated:
                mutated = new
                tag = "line_long_via_expression"
        elif language == "Java":
            new = mutated.replace("//", "/*noise*/ //")
            mutated = new
            tag = "line_long_with_comment_noise"

    elif expected == "InvalidAssignment":
        if language == "Python":
            mutated = mutated.replace("(x, y) = 1", "(left, right) = 1")
            tag = "tuple_unpack_scalar"
        elif language == "Java":
            mutated = mutated.replace("arr = 3;", "arr = (1 + 2);")
            tag = "array_scalar_assignment_expr"

    return mutated, tag


def _evaluate_strict_case(case: StrictCase) -> dict:
    kwargs = {}
    if case.use_override:
        kwargs["language_override"] = case.language
    filename = case.filename or f"snippet{FILE_EXT[case.language]}"
    result = detect_errors(case.code, filename=filename, **kwargs)
    predicted = str(result.get("predicted_error", "NoError"))
    confidence = float(result.get("confidence", 0.0) or 0.0)
    return {
        "case_id": case.case_id,
        "language": case.language,
        "expected": case.expected,
        "predicted": predicted,
        "correct": predicted == case.expected,
        "confidence": confidence,
        "category": case.category,
        "root_cause_hint": case.root_cause_hint,
        "rule_types": [i.get("type") for i in result.get("rule_based_issues", []) if i.get("type")],
    }


def _ece(records: list[dict], bins: int = 10) -> float:
    if not records:
        return 0.0
    bin_totals = [0] * bins
    bin_conf = [0.0] * bins
    bin_acc = [0.0] * bins
    for row in records:
        conf = max(0.0, min(1.0, float(row["confidence"])))
        b = min(bins - 1, int(conf * bins))
        bin_totals[b] += 1
        bin_conf[b] += conf
        bin_acc[b] += 1.0 if row["correct"] else 0.0
    total = len(records)
    ece = 0.0
    for i in range(bins):
        if bin_totals[i] == 0:
            continue
        avg_conf = bin_conf[i] / bin_totals[i]
        avg_acc = bin_acc[i] / bin_totals[i]
        ece += (bin_totals[i] / total) * abs(avg_conf - avg_acc)
    return ece


def _confidence_reliability_score(records: list[dict]) -> float:
    if not records:
        return 0.0
    one_rate = sum(1 for r in records if r["confidence"] >= 0.999) / len(records)
    ece = _ece(records)
    penalty = 0.7 * ece + 0.3 * max(0.0, one_rate - 0.85)
    return round(max(0.0, 10.0 * (1.0 - penalty)), 2)


def _strict_metrics(records: list[dict]) -> dict:
    total = len(records)
    correct = sum(1 for r in records if r["correct"])
    accuracy = correct / total if total else 0.0
    by_type = defaultdict(lambda: {"ok": 0, "total": 0})
    for r in records:
        key = (r["language"], r["expected"])
        by_type[key]["total"] += 1
        if r["correct"]:
            by_type[key]["ok"] += 1
    covered = sum(1 for v in by_type.values() if v["ok"] == v["total"])
    weak = sum(1 for v in by_type.values() if 0 < v["ok"] < v["total"])
    missing = sum(1 for v in by_type.values() if v["ok"] == 0)
    robustness = max(0.0, 1.0 - ((1.5 * (total - correct)) / max(total, 1)))
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy * 100, 2),
        "coverage": {
            "covered": covered,
            "weak": weak,
            "missing": missing,
        },
        "robustness": round(robustness * 100, 2),
        "confidence_reliability": _confidence_reliability_score(records),
        "ece": round(_ece(records), 4),
        "confidence_one_rate": round(
            (sum(1 for r in records if r["confidence"] >= 0.999) / total) if total else 0.0, 4
        ),
    }


def _real_world_cases() -> list[StrictCase]:
    return [
        # Python
        StrictCase("rw-py-01", "Python", "MissingImport", "def run():\n    return statistics.mean([1,2,3])\n", "real_world", "static_import_dictionary_gap"),
        StrictCase("rw-py-02", "Python", "DivisionByZero", "def f(n):\n    return n / (2-2)\n", "real_world", "literal_only_zero_detector"),
        StrictCase("rw-py-03", "Python", "InfiniteLoop", "while (2 > 1):\n    pass\n", "real_world", "rigid_loop_pattern"),
        StrictCase("rw-py-04", "Python", "UnreachableCode", "def g():\n    return 1\n    x = 2\n", "real_world", "nested_unreachable"),
        StrictCase("rw-py-05", "Python", "TypeMismatch", "def h() -> int:\n    return '7'\n", "real_world", "annotation_semantics"),
        StrictCase("rw-py-06", "Python", "UndeclaredIdentifier", "def h():\n    return missing_symbol_qa\n", "real_world", "name_vs_undeclared_bias"),
        StrictCase("rw-py-07", "Python", "ImportError", "import vendor_pkg_alpha\nprint('x')\n", "real_world", "importerror_nonplaceholder_name"),
        StrictCase("rw-py-08", "Python", "NoError", "def clean(a:int,b:int)->int:\n    return a+b\n", "real_world", "clean_reference"),
        # Java
        StrictCase("rw-java-01", "Java", "MissingImport", "public class Main { public static void main(String[] args){ LinkedList<Integer> q = new LinkedList<>(); } }", "real_world", "java_import_symbol_gap"),
        StrictCase("rw-java-02", "Java", "DivisionByZero", "public class Main { static int f(){ int d = 2-2; return 9/d; } }", "real_world", "literal_only_zero_detector"),
        StrictCase("rw-java-03", "Java", "UnreachableCode", "public class Main { static void f(){ return; int x = 2; } }", "real_world", "post_jump_statement"),
        StrictCase("rw-java-04", "Java", "InvalidAssignment", "public class Main { static void f(){ int[] arr = {1,2}; arr = (1+2); } }", "real_world", "array_scalar_assignment_expr"),
        StrictCase("rw-java-05", "Java", "ImportError", "import vendor.pkg.Alpha;\npublic class Main { public static void main(String[] args){} }", "real_world", "importerror_nonplaceholder_name"),
        StrictCase("rw-java-06", "Java", "LineTooLong", "public class Main { public static void main(String[] args) { String s = \"" + ("Q" * 130) + "\"; } }", "real_world", "style_long_line"),
        StrictCase("rw-java-07", "Java", "NoError", "public class Main { public static void main(String[] args){ int x=1; System.out.println(x); } }", "real_world", "clean_reference"),
        # C
        StrictCase("rw-c-01", "C", "DivisionByZero", "int main(){ int d = 2-2; return 5/d; }", "real_world", "literal_only_zero_detector"),
        StrictCase("rw-c-02", "C", "InfiniteLoop", "int main(){ while(2>1){ } }", "real_world", "rigid_loop_pattern"),
        StrictCase("rw-c-03", "C", "UnreachableCode", "int main(){ return 0; int x = 1; }", "real_world", "post_jump_statement"),
        StrictCase("rw-c-04", "C", "MissingInclude", "int main(){ fprintf(stdout, \"x\"); return 0; }", "real_world", "include_symbol_mapping"),
        StrictCase("rw-c-05", "C", "NoError", "#include <stdio.h>\nint main(){ printf(\"ok\"); return 0; }", "real_world", "clean_reference"),
        # C++
        StrictCase("rw-cpp-01", "C++", "UndeclaredIdentifier", "#include <cstdio>\nint main(){ printf(\"%d\", value); return 0; }", "real_world", "priority_include_vs_identifier"),
        StrictCase("rw-cpp-02", "C++", "DivisionByZero", "int main(){ int d = 2-2; return 10/d; }", "real_world", "literal_only_zero_detector"),
        StrictCase("rw-cpp-03", "C++", "InfiniteLoop", "int main(){ while(2>1){ } }", "real_world", "rigid_loop_pattern"),
        StrictCase("rw-cpp-04", "C++", "DanglingPointer", "int* bad(){ int x=1; return &x; } int main(){ int* p = bad(); return *p; }", "real_world", "lifetime_static_pattern"),
        StrictCase("rw-cpp-05", "C++", "NoError", "#include <iostream>\nint main(){ int x=1; std::cout << x; return 0; }", "real_world", "clean_reference"),
        # JavaScript
        StrictCase("rw-js-01", "JavaScript", "UndeclaredIdentifier", "function f(){ return missing_symbol_qa + 1; }", "real_world", "identifier_resolution"),
        StrictCase("rw-js-02", "JavaScript", "InfiniteLoop", "while((2>1)){ }", "real_world", "rigid_loop_pattern"),
        StrictCase("rw-js-03", "JavaScript", "UnreachableCode", "function g(){ throw new Error('x'); console.log('never'); }", "real_world", "post_jump_statement"),
        StrictCase("rw-js-04", "JavaScript", "DivisionByZero", "const d = 2-2; const z = 9 / d;", "real_world", "literal_only_zero_detector"),
        StrictCase("rw-js-05", "JavaScript", "NoError", "function add(a,b){ return a+b; } console.log(add(1,2));", "real_world", "clean_reference"),
    ]


def _mixed_and_partial_cases() -> list[StrictCase]:
    # Auto language mode intentionally (no override) to probe detector leakage.
    return [
        StrictCase(
            "mx-01", "JavaScript", "UndeclaredIdentifier",
            "/* copied from issue */\nfunction f(){\n  int x = 1;\n  console.log(y)\n}\n",
            "mixed_language", "language_bias_leak", filename="snippet.js", use_override=False
        ),
        StrictCase(
            "mx-02", "C++", "MissingInclude",
            "std::cout << 1 << std::endl;\n",
            "partial_snippet", "partial_file_header_missing", filename="sample.cpp", use_override=False
        ),
        StrictCase(
            "mx-03", "Python", "MissingDelimiter",
            "def parse(x)\n    if x:\n        return x\n",
            "partial_snippet", "partial_function_fragment", filename="frag.py", use_override=False
        ),
        StrictCase(
            "mx-04", "Java", "UnmatchedBracket",
            "public class Main {\n  public static void main(String[] args) {\n    if (true) {\n      System.out.println(1);\n",
            "partial_snippet", "truncated_file", filename="Main.java", use_override=False
        ),
        StrictCase(
            "mx-05", "C", "UnclosedString",
            "int main(){ printf(\"oops); }\n",
            "partial_snippet", "unterminated_literal", filename="x.c", use_override=False
        ),
        StrictCase(
            "mx-06", "JavaScript", "MissingDelimiter",
            "const a = 1\nconst b = 2\nconsole.log(a+b)\n",
            "messy_style", "asi_ambiguity", filename="x.js", use_override=False
        ),
        StrictCase(
            "mx-07", "Python", "NoError",
            "# notebook-ish\nx=1\ny=2\nx+y\n",
            "messy_style", "script_expression_ok", filename="nb.py", use_override=False
        ),
    ]


def _multi_error_cases() -> list[MultiCase]:
    return [
        MultiCase(
            "me-java-01",
            "Java",
            ("MissingImport", "TypeMismatch", "UnreachableCode"),
            "TypeMismatch",
            "public class Main { static int f(){ ArrayList<Integer> xs = new ArrayList<>(); int n = \"7\"; return 1; int z=2; } }",
            "overlap",
        ),
        MultiCase(
            "me-cpp-01",
            "C++",
            ("DanglingPointer", "UndeclaredIdentifier"),
            "UndeclaredIdentifier",
            "int* bad(){ int x=1; return &x; } int main(){ int* p = bad(); return *q; }",
            "overlap",
        ),
        MultiCase(
            "me-c-01",
            "C",
            ("DivisionByZero", "UnreachableCode"),
            "DivisionByZero",
            "int main(){ int z = 5/0; return z; int x = 2; }",
            "overlap",
        ),
        MultiCase(
            "me-js-01",
            "JavaScript",
            ("DuplicateDefinition", "UnreachableCode"),
            "DuplicateDefinition",
            "function f(){ let x=1; let x=2; return x; console.log(x); }",
            "overlap",
        ),
        MultiCase(
            "me-py-01",
            "Python",
            ("MissingImport", "TypeMismatch"),
            "TypeMismatch",
            "def f() -> int:\n    data = np.array([1,2,3])\n    return 'x'\n",
            "overlap",
        ),
    ]


def _cross_language_families() -> list[FamilyCase]:
    return [
        FamilyCase("division_expr_zero", "Python", "DivisionByZero", "def f():\n    return 10 / (2-2)\n"),
        FamilyCase("division_expr_zero", "Java", "DivisionByZero", "public class Main { static int f(){ int d=2-2; return 10/d; } }"),
        FamilyCase("division_expr_zero", "C++", "DivisionByZero", "int main(){ int d=2-2; return 10/d; }"),
        FamilyCase("division_expr_zero", "JavaScript", "DivisionByZero", "const d = 2-2; const z = 10 / d;"),
        FamilyCase("infinite_condition_expr", "Python", "InfiniteLoop", "while (2 > 1):\n    pass\n"),
        FamilyCase("infinite_condition_expr", "Java", "InfiniteLoop", "public class Main { static void f(){ while((2>1)){} } }"),
        FamilyCase("infinite_condition_expr", "C++", "InfiniteLoop", "int main(){ while((2>1)){} }"),
        FamilyCase("infinite_condition_expr", "JavaScript", "InfiniteLoop", "while((2>1)){}"),
        FamilyCase("unreachable_after_jump", "Python", "UnreachableCode", "def f():\n    return 1\n    x = 2\n"),
        FamilyCase("unreachable_after_jump", "Java", "UnreachableCode", "public class Main { static int f(){ return 1; int x=2; } }"),
        FamilyCase("unreachable_after_jump", "C++", "UnreachableCode", "int main(){ return 1; int x=2; }"),
        FamilyCase("unreachable_after_jump", "JavaScript", "UnreachableCode", "function f(){ return 1; console.log(2); }"),
    ]


def _evaluate_multi(case: MultiCase) -> dict:
    single = detect_errors(case.code, language_override=case.language)
    all_res = detect_all_errors(case.code, filename=f"tmp{FILE_EXT[case.language]}")
    detected_all = sorted({str(item.get("type")) for item in all_res.get("errors", []) if item.get("type")})
    expected_set = set(case.expected_types)
    detected_set = set(detected_all)
    recall = len(expected_set & detected_set) / len(expected_set) if expected_set else 1.0
    single_pred = str(single.get("predicted_error", "NoError"))
    return {
        "case_id": case.case_id,
        "language": case.language,
        "expected_types": list(case.expected_types),
        "expected_primary": case.expected_primary,
        "single_predicted": single_pred,
        "single_confidence": float(single.get("confidence", 0.0) or 0.0),
        "all_detected_types": detected_all,
        "all_recall": round(recall, 3),
        "full_multi_match": expected_set.issubset(detected_set),
        "primary_correct": single_pred == case.expected_primary,
        "single_only_failure": (len(expected_set) > 1 and len(detected_set) < len(expected_set)),
        "category": case.category,
    }


def _evaluate_family(case: FamilyCase) -> dict:
    result = detect_errors(case.code, filename=f"family{FILE_EXT[case.language]}", language_override=case.language)
    predicted = str(result.get("predicted_error", "NoError"))
    return {
        "family": case.family,
        "language": case.language,
        "expected": case.expected,
        "predicted": predicted,
        "correct": predicted == case.expected,
    }


def _build_failure_clusters(records: list[dict]) -> dict:
    by_lang = Counter()
    by_type = Counter()
    by_root = Counter()
    for row in records:
        if row["correct"]:
            continue
        by_lang[row["language"]] += 1
        by_type[(row["language"], row["expected"], row["predicted"])] += 1
        by_root[row.get("root_cause_hint", "unknown")] += 1
    return {
        "by_language": dict(by_lang),
        "by_expected_vs_predicted": {f"{k[0]}::{k[1]}->{k[2]}": v for k, v in by_type.items()},
        "by_root_cause": dict(by_root),
    }


def run() -> dict:
    baseline = json.loads((REPO_ROOT / "artifacts" / "qa" / "replay-batch4.json").read_text(encoding="utf-8"))

    # Phase 1: overfitting check via mutated versions of the same logical suite.
    mutation_cases: list[StrictCase] = []
    for idx, record in enumerate(_baseline_records(), start=1):
        mutated, tag = _mutate_preserve_intent(record)
        mutation_cases.append(
            StrictCase(
                case_id=f"mut-{idx:03d}",
                language=record["language"],
                expected=record["expected"],
                code=mutated,
                category="mutation",
                root_cause_hint=tag,
            )
        )
    mutation_results = [_evaluate_strict_case(case) for case in mutation_cases]
    mutation_metrics = _strict_metrics(mutation_results)

    # Phase 2 + 6: real-world and noisy/partial simulation.
    real_world_cases = _real_world_cases() + _mixed_and_partial_cases()
    real_world_results = [_evaluate_strict_case(case) for case in real_world_cases]
    real_world_metrics = _strict_metrics(real_world_results)

    # Phase 3: multi-error handling.
    multi_results = [_evaluate_multi(case) for case in _multi_error_cases()]
    multi_metrics = {
        "cases": len(multi_results),
        "primary_correct_rate": round(mean(1.0 if r["primary_correct"] else 0.0 for r in multi_results), 3),
        "full_multi_match_rate": round(mean(1.0 if r["full_multi_match"] else 0.0 for r in multi_results), 3),
        "avg_multi_recall": round(mean(r["all_recall"] for r in multi_results), 3),
        "single_only_failures": sum(1 for r in multi_results if r["single_only_failure"]),
    }

    # Phase 4: confidence integrity over unseen strict sets.
    unseen_for_conf = mutation_results + real_world_results
    confidence_audit = {
        "confidence_reliability_score": _confidence_reliability_score(unseen_for_conf),
        "ece": round(_ece(unseen_for_conf), 4),
        "confidence_one_rate": round(
            sum(1 for r in unseen_for_conf if r["confidence"] >= 0.999) / max(len(unseen_for_conf), 1),
            4,
        ),
        "mean_confidence_correct": round(
            mean(r["confidence"] for r in unseen_for_conf if r["correct"]) if any(r["correct"] for r in unseen_for_conf) else 0.0,
            4,
        ),
        "mean_confidence_incorrect": round(
            mean(r["confidence"] for r in unseen_for_conf if not r["correct"]) if any(not r["correct"] for r in unseen_for_conf) else 0.0,
            4,
        ),
    }

    # Phase 5: cross-language consistency.
    family_results = [_evaluate_family(case) for case in _cross_language_families()]
    fam_group = defaultdict(list)
    for row in family_results:
        fam_group[row["family"]].append(row)
    family_consistency = {
        family: round(mean(1.0 if r["correct"] else 0.0 for r in rows), 3)
        for family, rows in fam_group.items()
    }
    cross_metrics = {
        "overall_consistency": round(mean(family_consistency.values()), 3),
        "families": family_consistency,
    }

    # Overfitting indicator.
    baseline_acc = baseline["summary"]["total_pass"] / baseline["summary"]["total_cases"]
    mutation_acc = mutation_metrics["correct"] / max(mutation_metrics["total"], 1)
    overfitting_drop = round((baseline_acc - mutation_acc) * 100, 2)
    overfit = mutation_acc < baseline_acc

    combined_failure_clusters = _build_failure_clusters(mutation_results + real_world_results)

    # Brutal verdict rule.
    # Must choose exactly one:
    # - production-ready if no significant drop, robust multi-error, confidence reliable
    # - conditionally ready for moderate drop
    # - overfitted/unsafe for large drop or confidence/multi issues
    if (
        overfitting_drop >= 15.0
        or real_world_metrics["accuracy"] < 75.0
        or confidence_audit["confidence_reliability_score"] < 6.5
        or multi_metrics["full_multi_match_rate"] < 0.7
    ):
        verdict = "OVERFITTED_UNSAFE"
    elif (
        overfitting_drop >= 5.0
        or real_world_metrics["accuracy"] < 90.0
        or confidence_audit["confidence_reliability_score"] < 8.0
        or multi_metrics["full_multi_match_rate"] < 0.9
    ):
        verdict = "CONDITIONALLY_READY"
    else:
        verdict = "PRODUCTION_READY"

    payload = {
        "baseline_summary": baseline["summary"],
        "mutation_metrics": mutation_metrics,
        "real_world_metrics": real_world_metrics,
        "multi_error_metrics": multi_metrics,
        "confidence_audit": confidence_audit,
        "cross_language_metrics": cross_metrics,
        "overfitting": {
            "baseline_accuracy_pct": round(baseline_acc * 100, 2),
            "mutation_accuracy_pct": round(mutation_acc * 100, 2),
            "accuracy_drop_pct": overfitting_drop,
            "performance_drop_detected": overfit,
        },
        "failure_clusters": combined_failure_clusters,
        "verdict": verdict,
        "details": {
            "mutation_results": mutation_results,
            "real_world_results": real_world_results,
            "multi_error_results": multi_results,
            "family_results": family_results,
        },
    }
    return payload


def _write_markdown(payload: dict) -> str:
    lines = []
    lines.append("# Adversarial Validation Report")
    lines.append("")
    lines.append("## New Metrics (Unseen Dataset)")
    lines.append(f"- Mutation Accuracy: **{payload['mutation_metrics']['accuracy']}%**")
    lines.append(f"- Real-world Accuracy: **{payload['real_world_metrics']['accuracy']}%**")
    lines.append(f"- Real-world Robustness: **{payload['real_world_metrics']['robustness']}%**")
    lines.append(f"- Confidence Reliability Score: **{payload['confidence_audit']['confidence_reliability_score']}/10**")
    lines.append("")
    lines.append("## Overfitting Indicators")
    lines.append(
        f"- Baseline benchmark accuracy: **{payload['overfitting']['baseline_accuracy_pct']}%**"
    )
    lines.append(
        f"- Mutated unseen accuracy: **{payload['overfitting']['mutation_accuracy_pct']}%**"
    )
    lines.append(
        f"- Accuracy drop: **{payload['overfitting']['accuracy_drop_pct']}%**"
    )
    lines.append(
        f"- Performance drop outside benchmark: **{'YES' if payload['overfitting']['performance_drop_detected'] else 'NO'}**"
    )
    lines.append("")
    lines.append("## Failure Clusters")
    lines.append(f"- By language: `{payload['failure_clusters']['by_language']}`")
    lines.append(f"- By root cause: `{payload['failure_clusters']['by_root_cause']}`")
    lines.append("")
    lines.append("## Multi-error Handling")
    lines.append(f"- Primary correctness rate: **{payload['multi_error_metrics']['primary_correct_rate']}**")
    lines.append(f"- Full multi-error match rate: **{payload['multi_error_metrics']['full_multi_match_rate']}**")
    lines.append(f"- Avg multi-error recall: **{payload['multi_error_metrics']['avg_multi_recall']}**")
    lines.append(f"- Single-only failures: **{payload['multi_error_metrics']['single_only_failures']}**")
    lines.append("")
    lines.append("## Confidence Integrity")
    lines.append(f"- ECE: **{payload['confidence_audit']['ece']}**")
    lines.append(f"- Confidence=1.0 rate: **{payload['confidence_audit']['confidence_one_rate']}**")
    lines.append(
        f"- Mean confidence (correct vs incorrect): **{payload['confidence_audit']['mean_confidence_correct']} / {payload['confidence_audit']['mean_confidence_incorrect']}**"
    )
    lines.append("")
    lines.append("## Cross-language Edge Consistency")
    lines.append(
        f"- Overall family consistency: **{payload['cross_language_metrics']['overall_consistency']}**"
    )
    lines.append(f"- Family breakdown: `{payload['cross_language_metrics']['families']}`")
    lines.append("")
    lines.append("## Final Verdict")
    verdict_map = {
        "PRODUCTION_READY": "✅ Production-ready (real-world safe)",
        "CONDITIONALLY_READY": "⚠️ Conditionally ready (limited scope)",
        "OVERFITTED_UNSAFE": "❌ Overfitted / unsafe",
    }
    lines.append(f"- **{verdict_map[payload['verdict']]}**")
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = run()
    out_json = REPO_ROOT / "artifacts" / "qa" / "adversarial-validation-2026-04-11.json"
    out_md = REPO_ROOT / "artifacts" / "qa" / "adversarial-validation-2026-04-11.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(_write_markdown(payload), encoding="utf-8")
    print(json.dumps(
        {
            "mutation_accuracy": payload["mutation_metrics"]["accuracy"],
            "real_world_accuracy": payload["real_world_metrics"]["accuracy"],
            "confidence_reliability": payload["confidence_audit"]["confidence_reliability_score"],
            "accuracy_drop_pct": payload["overfitting"]["accuracy_drop_pct"],
            "verdict": payload["verdict"],
        },
        indent=2,
    ))
    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_md}")


if __name__ == "__main__":
    main()
