"""
Replay the OmniSyntax mapping audit from a stored baseline case file.

Usage:
  .\.venv\Scripts\python.exe scripts/replay_mapping_audit.py `
      --dataset artifacts/qa/mapping_audit_2026-04-11.json `
      --output artifacts/qa/replay-current.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

# Ensure repo root is on sys.path when running as a script.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.error_engine import detect_errors


@dataclass(frozen=True)
class ReplayCase:
    language: str
    error_type: str
    case_kind: str
    expected: str
    code: str


def _load_cases(dataset_path: Path) -> list[ReplayCase]:
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    cases: list[ReplayCase] = []
    for record in records:
        cases.append(
            ReplayCase(
                language=str(record["language"]),
                error_type=str(record["error_type"]),
                case_kind=str(record["case_kind"]),
                expected=str(record["expected"]),
                code=str(record["code"]),
            )
        )
    return cases


def _score_accuracy(total: int, passed: int) -> float:
    if total == 0:
        return 0.0
    return round((passed / total) * 10, 2)


def _score_coverage(coverage: list[dict]) -> float:
    total = len(coverage)
    if total == 0:
        return 0.0
    covered = sum(1 for item in coverage if item["status"] == "Covered")
    weak = sum(1 for item in coverage if item["status"] == "Weak")
    weighted = (covered + 0.5 * weak) / total
    return round(weighted * 10, 2)


def _score_robustness(total: int, false_negatives: int, misclassified: int) -> float:
    if total == 0:
        return 0.0
    fn_rate = false_negatives / total
    mis_rate = misclassified / total
    score = 10 - (fn_rate * 25 + mis_rate * 10)
    return round(max(0.0, min(10.0, score)), 2)


def _score_production_readiness(accuracy: float, coverage: float, robustness: float) -> float:
    return round((0.35 * accuracy) + (0.35 * coverage) + (0.30 * robustness), 2)


def replay_cases(cases: list[ReplayCase]) -> dict:
    records: list[dict] = []

    for case in cases:
        result = detect_errors(case.code, language_override=case.language)
        predicted = str(result.get("predicted_error", "NoError"))
        rule_types = sorted(
            {
                str(issue.get("type"))
                for issue in result.get("rule_based_issues", [])
                if issue.get("type")
            }
        )
        records.append(
            {
                "language": case.language,
                "error_type": case.error_type,
                "case_kind": case.case_kind,
                "expected": case.expected,
                "predicted": predicted,
                "pass": predicted == case.expected,
                "rule_types": rule_types,
                "degraded_mode": bool(result.get("degraded_mode", False)),
                "warnings": list(result.get("warnings", [])),
                "code": case.code,
            }
        )

    by_type = defaultdict(
        lambda: {"positive_total": 0, "positive_pass": 0, "negative_pass": 0, "fails": 0}
    )
    for row in records:
        key = (row["language"], row["error_type"])
        if row["case_kind"] == "negative":
            by_type[key]["negative_pass"] = 1 if row["pass"] else 0
        else:
            by_type[key]["positive_total"] += 1
            by_type[key]["positive_pass"] += 1 if row["pass"] else 0
        by_type[key]["fails"] += 0 if row["pass"] else 1

    coverage: list[dict] = []
    for language, error_type in sorted(by_type.keys()):
        stats = by_type[(language, error_type)]
        if stats["positive_pass"] == 3 and stats["negative_pass"] == 1:
            status = "Covered"
        elif stats["positive_pass"] == 0:
            status = "Missing"
        else:
            status = "Weak"
        coverage.append(
            {
                "language": language,
                "error_type": error_type,
                "status": status,
                **stats,
            }
        )

    false_positives = [r for r in records if r["expected"] == "NoError" and r["predicted"] != "NoError"]
    false_negatives = [r for r in records if r["expected"] != "NoError" and r["predicted"] == "NoError"]
    misclassified = [
        r
        for r in records
        if r["expected"] != "NoError" and r["predicted"] not in (r["expected"], "NoError")
    ]

    total = len(records)
    passed = sum(1 for r in records if r["pass"])
    failed = total - passed
    coverage_counts = Counter(item["status"] for item in coverage)

    accuracy = _score_accuracy(total, passed)
    coverage_score = _score_coverage(coverage)
    robustness = _score_robustness(total, len(false_negatives), len(misclassified))
    production_readiness = _score_production_readiness(accuracy, coverage_score, robustness)

    summary = {
        "total_cases": total,
        "total_pass": passed,
        "total_fail": failed,
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
        "misclassified": len(misclassified),
        "degraded_mode_cases": sum(1 for r in records if r["degraded_mode"]),
        "coverage_counts": {
            "Covered": coverage_counts.get("Covered", 0),
            "Weak": coverage_counts.get("Weak", 0),
            "Missing": coverage_counts.get("Missing", 0),
        },
        "scores": {
            "accuracy": accuracy,
            "coverage": coverage_score,
            "robustness": robustness,
            "production_readiness": production_readiness,
        },
    }

    return {
        "summary": summary,
        "coverage": coverage,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "misclassified": misclassified,
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay OmniSyntax mapping audit cases.")
    parser.add_argument(
        "--dataset",
        default="artifacts/qa/mapping_audit_2026-04-11.json",
        help="Path to baseline dataset json containing records.",
    )
    parser.add_argument(
        "--output",
        default="artifacts/qa/replay-current.json",
        help="Output path for replay results.",
    )
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cases = _load_cases(dataset_path)
    replay = replay_cases(cases)
    output_path.write_text(json.dumps(replay, indent=2), encoding="utf-8")
    print(json.dumps(replay["summary"], indent=2))
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
