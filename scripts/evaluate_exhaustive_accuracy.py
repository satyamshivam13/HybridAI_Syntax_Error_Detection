"""
Exhaustive accuracy evaluation for OmniSyntax.

Outputs reproducible artifacts under artifacts/accuracy by default.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib
import json
import logging
import os
import random
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import joblib
import pandas as pd
from fastapi.testclient import TestClient
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.error_engine import detect_errors
from src.quality_analyzer import CodeQualityAnalyzer

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


LANGUAGES = ["Python", "Java", "C", "C++", "JavaScript"]
EXT_MAP = {"Python": ".py", "Java": ".java", "C": ".c", "C++": ".cpp", "JavaScript": ".js"}
LABEL_ALIASES = {"MissingColon": "MissingDelimiter", "UnclosedQuotes": "UnclosedString"}
CORE_CRITICAL_LABELS = ["MissingDelimiter", "UnmatchedBracket", "UnclosedString", "IndentationError"]
DEFAULT_SEED = 20260305


@dataclass(frozen=True)
class Sample:
    sample_id: str
    language: str
    expected_label: str
    code: str
    filename: str
    source_path: str
    source_line: int | None
    corpus_type: str
    generator: str
    seed: int
    metadata: dict


def normalize_label(label: str) -> str:
    return LABEL_ALIASES.get(label, label)


def make_sample_id(language: str, expected_label: str, code: str, source_path: str, source_line: int | None) -> str:
    raw = f"{language}|{expected_label}|{source_path}|{source_line}|{code}"
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:20]


def mk_sample(
    language: str,
    expected_label: str,
    code: str,
    source_path: str,
    source_line: int | None,
    corpus_type: str,
    generator: str,
    seed: int,
    metadata: dict | None = None,
) -> Sample:
    code = code.replace("\r\n", "\n")
    filename = f"eval_{language.lower().replace('+', 'p')}{EXT_MAP[language]}"
    sample_id = make_sample_id(language, expected_label, code, source_path, source_line)
    return Sample(
        sample_id=sample_id,
        language=language,
        expected_label=normalize_label(expected_label),
        code=code,
        filename=filename,
        source_path=source_path,
        source_line=source_line,
        corpus_type=corpus_type,
        generator=generator,
        seed=seed,
        metadata=metadata or {},
    )


def load_supported_labels(dataset_path: Path, model_label_path: Path) -> list[str]:
    labels: set[str] = set()
    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        labels.update(normalize_label(v) for v in df["error_type"].dropna().astype(str).tolist())
    if model_label_path.exists():
        le = joblib.load(model_label_path)
        labels.update(normalize_label(v) for v in le.classes_.tolist())
    labels.update({"SyntaxError", "NoError"})
    return sorted(labels)


def load_dataset_samples(dataset_path: Path, seed: int) -> list[Sample]:
    df = pd.read_csv(dataset_path)
    out: list[Sample] = []
    for i, row in df.iterrows():
        language = str(row["language"])
        if language not in LANGUAGES:
            continue
        label = normalize_label(str(row["error_type"]))
        code = str(row["buggy_code"])
        out.append(
            mk_sample(
                language=language,
                expected_label=label,
                code=code,
                source_path=str(dataset_path),
                source_line=int(i + 2),
                corpus_type="dataset",
                generator="dataset/merged/all_errors_v3.csv",
                seed=seed,
                metadata={"dataset_index": int(i)},
            )
        )
    return out


def base_valid_templates() -> dict[str, list[str]]:
    return {
        "Python": [
            "x = 1\nprint(x)",
            "def add(a, b):\n    return a + b\nprint(add(1, 2))",
            "for i in range(3):\n    print(i)",
            "class A:\n    def m(self):\n        return 'ok'\nA().m()",
            "items = [1, 2, 3]\nvals = [x * 2 for x in items]\nprint(vals)",
        ],
        "Java": [
            "public class Main { public static void main(String[] args) { int x = 1; System.out.println(x); } }",
            "public class Main { static int add(int a,int b){ return a+b; } public static void main(String[] args){ System.out.println(add(1,2)); } }",
            "public class Main { public static void main(String[] args){ for(int i=0;i<3;i++){ System.out.println(i); } } }",
        ],
        "C": [
            "#include <stdio.h>\nint main(){ int x = 1; printf(\"%d\\n\", x); return 0; }",
            "#include <stdio.h>\nint add(int a,int b){ return a+b; }\nint main(){ printf(\"%d\\n\", add(1,2)); return 0; }",
            "#include <stdio.h>\nint main(){ for(int i=0;i<3;i++){ printf(\"%d\\n\", i); } return 0; }",
        ],
        "C++": [
            "#include <iostream>\nusing namespace std;\nint main(){ int x = 1; cout << x << endl; return 0; }",
            "#include <iostream>\nusing namespace std;\nint add(int a,int b){ return a+b; }\nint main(){ cout << add(1,2) << endl; return 0; }",
            "#include <iostream>\nusing namespace std;\nint main(){ for(int i=0;i<3;i++){ cout << i << endl; } return 0; }",
        ],
        "JavaScript": [
            "function add(a,b){ return a+b; }\nconsole.log(add(1,2));",
            "const arr = [1,2,3];\nfor (const x of arr) { console.log(x); }",
            "class A { m(){ return 1; } }\nconsole.log(new A().m());",
        ],
    }


def dedupe_samples(samples: Iterable[Sample]) -> list[Sample]:
    seen: set[str] = set()
    out: list[Sample] = []
    for smp in samples:
        if smp.sample_id in seen:
            continue
        seen.add(smp.sample_id)
        out.append(smp)
    return out


def generate_valid_grammar(language: str, count: int, seed: int) -> list[Sample]:
    rnd = random.Random(seed)
    out: list[Sample] = []
    for i in range(count):
        a = rnd.randint(1, 2000)
        b = rnd.randint(1, 2000)
        c = rnd.randint(1, 2000)
        name = f"v{i % 113}"
        if language == "Python":
            code = (
                f"def f_{i % 37}(x):\n"
                f"    total = x + {a}\n"
                f"    for j in range({i % 5 + 1}):\n"
                f"        total += j\n"
                "    return total\n"
                f"{name} = f_{i % 37}({b})\n"
                f"print({name} + {c})\n"
            )
        elif language == "Java":
            code = (
                "public class Main {\n"
                f"  static int f_{i % 37}(int x) {{\n"
                f"    int total = x + {a};\n"
                f"    for (int j = 0; j < {i % 5 + 1}; j++) {{\n"
                "      total += j;\n"
                "    }\n"
                "    return total;\n"
                "  }\n"
                "  public static void main(String[] args) {\n"
                f"    int {name} = f_{i % 37}({b});\n"
                f"    System.out.println({name} + {c});\n"
                "  }\n"
                "}\n"
            )
        elif language == "C":
            code = (
                "#include <stdio.h>\n"
                f"int f_{i % 37}(int x) {{\n"
                f"    int total = x + {a};\n"
                f"    for (int j = 0; j < {i % 5 + 1}; j++) {{\n"
                "        total += j;\n"
                "    }\n"
                "    return total;\n"
                "}\n"
                "int main() {\n"
                f"    int {name} = f_{i % 37}({b});\n"
                f"    printf(\"%d\\n\", {name} + {c});\n"
                "    return 0;\n"
                "}\n"
            )
        elif language == "C++":
            code = (
                "#include <iostream>\n"
                "using namespace std;\n"
                f"int f_{i % 37}(int x) {{\n"
                f"    int total = x + {a};\n"
                f"    for (int j = 0; j < {i % 5 + 1}; j++) {{\n"
                "        total += j;\n"
                "    }\n"
                "    return total;\n"
                "}\n"
                "int main() {\n"
                f"    int {name} = f_{i % 37}({b});\n"
                f"    cout << ({name} + {c}) << endl;\n"
                "    return 0;\n"
                "}\n"
            )
        else:
            code = (
                f"function f_{i % 37}(x) {{\n"
                f"  let total = x + {a};\n"
                f"  for (let j = 0; j < {i % 5 + 1}; j++) {{\n"
                "    total += j;\n"
                "  }\n"
                "  return total;\n"
                "}\n"
                f"const {name} = f_{i % 37}({b});\n"
                f"console.log({name} + {c});\n"
            )
        out.append(
            mk_sample(
                language=language,
                expected_label="NoError",
                code=code,
                source_path=f"generated://grammar/{language}",
                source_line=i + 1,
                corpus_type="grammar_valid",
                generator="grammar_v1",
                seed=seed,
                metadata={"index": i},
            )
        )
    return out


def mutate_code(language: str, code: str, mutation: str) -> tuple[str, str] | None:
    lines = code.splitlines()
    if mutation == "missing_colon" and language == "Python":
        for idx, ln in enumerate(lines):
            if ln.strip().startswith(("def ", "if ", "for ", "while ", "class ")) and ln.rstrip().endswith(":"):
                lines[idx] = ln.rstrip()[:-1]
                return "\n".join(lines), "MissingDelimiter"
    if mutation == "bracket_drift":
        return code + "\n)", "UnmatchedBracket"
    if mutation == "quote_break":
        if language == "Python":
            return code + "\ns = 'unterminated", "UnclosedString"
        if language in {"Java", "C", "C++", "JavaScript"}:
            if language in {"C", "C++"}:
                return code + '\nprintf("unterminated);', "UnclosedString"
            return code + '\nconsole.log("unterminated);', "UnclosedString"
    if mutation == "indentation_drift" and language == "Python":
        return "def bad():\nprint('x')\n", "IndentationError"
    if mutation == "semicolon_removal" and language in {"Java", "C", "C++", "JavaScript"}:
        for idx, ln in enumerate(lines):
            if ";" in ln and "for(" not in ln and "for (" not in ln:
                lines[idx] = ln.replace(";", "", 1)
                return "\n".join(lines), "MissingDelimiter"
    if mutation == "include_variant" and language in {"C", "C++"}:
        return "int main(){ printf(\"hi\"); return 0; }\n", "MissingInclude"
    if mutation == "import_variant":
        if language == "Python":
            return "print(json.dumps({'a':1}))\n", "ImportError"
        if language == "Java":
            return "public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n", "ImportError"
    return None


def generate_mutation_samples(valid_samples: list[Sample], per_language: int, seed: int) -> list[Sample]:
    rnd = random.Random(seed)
    by_lang: dict[str, list[Sample]] = defaultdict(list)
    for smp in valid_samples:
        by_lang[smp.language].append(smp)

    mutations = [
        "missing_colon",
        "bracket_drift",
        "quote_break",
        "indentation_drift",
        "semicolon_removal",
        "include_variant",
        "import_variant",
    ]
    out: list[Sample] = []
    for language, samples in by_lang.items():
        if not samples:
            continue
        for i in range(per_language):
            base = samples[rnd.randrange(len(samples))]
            mutation = mutations[rnd.randrange(len(mutations))]
            result = mutate_code(language, base.code, mutation)
            if result is None:
                continue
            mutated, label = result
            out.append(
                mk_sample(
                    language=language,
                    expected_label=label,
                    code=mutated,
                    source_path=f"generated://mutation/{language}/{mutation}",
                    source_line=i + 1,
                    corpus_type="mutation_invalid",
                    generator=f"mutation:{mutation}",
                    seed=seed,
                    metadata={"base_id": base.sample_id, "mutation": mutation, "index": i},
                )
            )
    return out


def adversarial_samples(seed: int) -> list[Sample]:
    out: list[Sample] = []
    cases = [
        ("Python", "print(') ] } in string')\n# comment with [ { ("),
        ("Java", "public class Main { public static void main(String[] args) { System.out.println(\") ] }\"); } }"),
        ("C", "#include <stdio.h>\nint main(){ printf(\") ] }\"); /* [ { ( */ return 0; }"),
        ("C++", "#include <iostream>\nusing namespace std;\nint main(){ cout << \") ] }\"; // [ { (\nreturn 0; }"),
        ("JavaScript", "function f(){ console.log(\") ] }\"); /* [ { ( */ }\nf();"),
        ("Python", "name = 'caf\\u00e9'\nprint(name)\n"),
        ("JavaScript", "const s = 'caf\\u00e9';\nconsole.log(s);\n"),
        ("Python", "x = 1\r\ny = 2\r\nprint(x + y)\r\n"),
        ("Java", "public class Main {\r\n  public static void main(String[] a){\r\n    int x=1;\r\n    System.out.println(x);\r\n  }\r\n}\r\n"),
        ("C", "#include <stdio.h>\nint main(){ printf(\"caf\\xE9\"); return 0; }"),
        ("Python", "line = '" + ("a" * 5000) + "'\nprint(len(line))"),
        ("JavaScript", "const x = `" + ("b" * 5000) + "`;\nconsole.log(x.length);"),
    ]
    for idx, (language, code) in enumerate(cases, start=1):
        out.append(
            mk_sample(
                language=language,
                expected_label="NoError",
                code=code,
                source_path="generated://adversarial/edge_cases",
                source_line=idx,
                corpus_type="adversarial",
                generator="edge_cases_v1",
                seed=seed,
                metadata={"index": idx},
            )
        )
    return out


def curated_invalid_per_label(seed: int) -> list[Sample]:
    out: list[Sample] = []
    rows = [
        ("Python", "DivisionByZero", "def f():\n    return 3/0\n"),
        ("Python", "DuplicateDefinition", "def f():\n    return 1\ndef f():\n    return 2\n"),
        ("Python", "ImportError", "print(json.dumps({'a':1}))\n"),
        ("Python", "IndentationError", "def f():\nprint('x')\n"),
        ("C", "InfiniteLoop", "int main(){ while(1){ } return 0; }\n"),
        ("Java", "InvalidAssignment", "public class Main { public static void main(String[] a){ 5 = x; } }\n"),
        ("Python", "LineTooLong", "x = '" + ("x" * 140) + "'\n"),
        ("C", "MissingInclude", "int main(){ printf(\"x\"); return 0; }\n"),
        ("Python", "MutableDefault", "def f(x, items=[]):\n    items.append(x)\n    return items\n"),
        ("Python", "NoError", "def f():\n    return 1\n"),
        ("Python", "TypeMismatch", "x = 'a' + 1\n"),
        ("Python", "UnclosedString", "s = 'abc\n"),
        ("Python", "UndeclaredIdentifier", "def f():\n    return not_defined + 1\n"),
        ("Python", "UnmatchedBracket", "print((1+2)\n"),
        ("Python", "UnreachableCode", "def f():\n    return 1\n    print('no')\n"),
        ("Python", "UnusedVariable", "def f():\n    x = 3\n    return 1\n"),
        ("Python", "WildcardImport", "from math import *\nprint(sin(1))\n"),
        ("Java", "MissingDelimiter", "public class Main { public static void main(String[] a) { int x = 1 } }"),
    ]
    for idx, (language, label, code) in enumerate(rows, start=1):
        out.append(
            mk_sample(
                language=language,
                expected_label=label,
                code=code,
                source_path="generated://curated/invalid_per_label",
                source_line=idx,
                corpus_type="curated_invalid",
                generator="curated_label_v1",
                seed=seed,
                metadata={"index": idx},
            )
        )
    return out


def setup_api_client(reload_api: bool = True) -> TestClient:
    os.environ["RATE_LIMIT_PER_MINUTE"] = "0"
    os.environ["MAX_CODE_SIZE"] = "200000"
    import api

    if reload_api:
        api = importlib.reload(api)
    return TestClient(api.app)


@contextlib.contextmanager
def forced_model_unavailable():
    import api as api_module
    import src.error_engine as ee

    old_is_model_available = ee.is_model_available
    old_safe_ml_prediction = ee._safe_ml_prediction
    old_api_get_model_status = api_module.get_model_status

    def fake_safe_ml(code: str, warnings: list[str]) -> tuple[str, float] | None:
        if all("forced unavailable mode" not in w for w in warnings):
            warnings.append("ML model unavailable; forced unavailable mode for evaluation")
        return None

    ee.is_model_available = lambda: False
    ee._safe_ml_prediction = fake_safe_ml
    api_module.get_model_status = lambda: {
        "loaded": False,
        "error": "forced unavailable mode for evaluation",
        "sklearn_version": "forced-unavailable",
        "expected_sklearn_major_minor": "1.1",
        "sklearn_compatible": False,
    }
    try:
        yield
    finally:
        ee.is_model_available = old_is_model_available
        ee._safe_ml_prediction = old_safe_ml_prediction
        api_module.get_model_status = old_api_get_model_status


def evaluate_samples(
    samples: list[Sample],
    mode: str,
    evaluate_quality_sample_size: int,
    evaluate_fix: bool,
    evaluate_fix_sample_size: int,
    reload_api: bool,
    seed: int,
) -> tuple[pd.DataFrame, dict]:
    rng = random.Random(seed)
    client = setup_api_client(reload_api=reload_api)
    health = client.get("/health").json()

    quality_indices = set()
    if evaluate_quality_sample_size > 0 and samples:
        idxs = list(range(len(samples)))
        rng.shuffle(idxs)
        quality_indices = set(idxs[: min(evaluate_quality_sample_size, len(idxs))])

    fix_indices = set()
    if evaluate_fix and evaluate_fix_sample_size > 0 and samples:
        error_candidates = [i for i, smp in enumerate(samples) if smp.expected_label != "NoError"]
        rng.shuffle(error_candidates)
        fix_indices.update(error_candidates[: min(evaluate_fix_sample_size, len(error_candidates))])

    rows: list[dict] = []
    for idx, smp in enumerate(samples):
        core = detect_errors(smp.code, smp.filename, smp.language)
        core_pred = normalize_label(str(core["predicted_error"]))
        core_conf = float(core.get("confidence", 0.0))
        core_warn = core.get("warnings", [])

        check_resp = client.post(
            "/check",
            json={"code": smp.code, "filename": smp.filename, "language": smp.language},
        )
        if check_resp.status_code == 200:
            check_payload = check_resp.json()
            api_pred = normalize_label(str(check_payload["predicted_error"]))
            api_conf = float(check_payload.get("confidence", 0.0))
            api_warn = check_payload.get("warnings", [])
        else:
            api_pred = "API_ERROR"
            api_conf = 0.0
            api_warn = [json.dumps(check_resp.json())]

        fix_status = None
        fix_success = None
        fix_changes = None
        if evaluate_fix and idx in fix_indices:
            err_for_fix = api_pred if api_pred != "API_ERROR" else core_pred
            line_num = None
            if core.get("rule_based_issues"):
                first = core["rule_based_issues"][0]
                if first.get("line") is not None:
                    line_num = int(first["line"]) - 1
            fix_resp = client.post(
                "/fix",
                json={
                    "code": smp.code,
                    "error_type": err_for_fix,
                    "language": smp.language,
                    "line_num": line_num,
                },
            )
            fix_status = int(fix_resp.status_code)
            if fix_resp.status_code == 200:
                fix_payload = fix_resp.json()
                fix_success = bool(fix_payload.get("success", False))
                fix_changes = len(fix_payload.get("changes", []))
            else:
                fix_success = False
                fix_changes = None

        quality_status = None
        quality_score = None
        quality_complexity = None
        quality_parity = None
        if idx in quality_indices:
            q_resp = client.post(
                "/quality",
                json={"code": smp.code, "language": smp.language.lower()},
            )
            quality_status = int(q_resp.status_code)
            if q_resp.status_code == 200:
                q_payload = q_resp.json()
                quality_score = float(q_payload.get("quality_score", 0.0))
                quality_complexity = int(q_payload.get("complexity", 0))
                local_quality = CodeQualityAnalyzer(smp.code, smp.language.lower()).analyze()
                quality_parity = (
                    abs(local_quality["quality_score"] - quality_score) < 1e-9
                    and int(local_quality["complexity"]) == quality_complexity
                )

        rows.append(
            {
                **asdict(smp),
                "mode": mode,
                "expected_label_norm": normalize_label(smp.expected_label),
                "core_predicted": core_pred,
                "core_confidence": core_conf,
                "core_degraded_mode": bool(core.get("degraded_mode", False)),
                "core_warning_count": len(core_warn),
                "api_status": int(check_resp.status_code),
                "api_predicted": api_pred,
                "api_confidence": api_conf,
                "api_warning_count": len(api_warn),
                "api_core_match": core_pred == api_pred,
                "fix_status": fix_status,
                "fix_success": fix_success,
                "fix_changes_count": fix_changes,
                "quality_status": quality_status,
                "quality_score": quality_score,
                "quality_complexity": quality_complexity,
                "quality_core_parity": quality_parity,
            }
        )

    df = pd.DataFrame(rows)
    route_summary = {
        "health": health,
        "check_status_counts": df["api_status"].value_counts(dropna=False).to_dict(),
        "fix_status_counts": df["fix_status"].value_counts(dropna=False).to_dict() if evaluate_fix else {},
        "quality_status_counts": df["quality_status"].value_counts(dropna=False).to_dict(),
    }
    return df, route_summary


def metrics_from_predictions(df: pd.DataFrame, labels: list[str]) -> dict[str, pd.DataFrame | dict]:
    y_true = df["expected_label_norm"].tolist()
    y_pred = df["core_predicted"].tolist()

    overall_acc = (df["expected_label_norm"] == df["core_predicted"]).mean() if len(df) else 0.0
    by_lang_rows = []
    for lang in sorted(df["language"].unique().tolist()):
        sub = df[df["language"] == lang]
        by_lang_rows.append(
            {
                "language": lang,
                "samples": int(len(sub)),
                "accuracy": float((sub["expected_label_norm"] == sub["core_predicted"]).mean() if len(sub) else 0.0),
            }
        )
    by_lang_df = pd.DataFrame(by_lang_rows)

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true=y_true,
        y_pred=y_pred,
        labels=labels,
        zero_division=0,
    )
    by_label_df = pd.DataFrame(
        {
            "label": labels,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    )

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)

    valid = df[df["expected_label_norm"] == "NoError"]
    fpr = float((valid["core_predicted"] != "NoError").mean() if len(valid) else 0.0)
    mismatch = df[df["api_core_match"] == False]  # noqa: E712

    return {
        "overall": {
            "samples": int(len(df)),
            "overall_accuracy": float(overall_acc),
            "valid_samples": int(len(valid)),
            "noerror_false_positive_rate": fpr,
            "api_core_mismatch_count": int(len(mismatch)),
            "api_core_mismatch_rate": float(len(mismatch) / len(df) if len(df) else 0.0),
        },
        "by_language": by_lang_df,
        "by_label": by_label_df,
        "confusion": cm_df,
        "mismatches": mismatch,
    }


def calibration_bins(df: pd.DataFrame, bins: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["bin", "count", "avg_confidence", "empirical_accuracy"])
    edges = [i / bins for i in range(bins + 1)]
    rows = []
    for i in range(bins):
        lo, hi = edges[i], edges[i + 1]
        if i == bins - 1:
            sub = df[(df["core_confidence"] >= lo) & (df["core_confidence"] <= hi)]
        else:
            sub = df[(df["core_confidence"] >= lo) & (df["core_confidence"] < hi)]
        if sub.empty:
            rows.append(
                {
                    "bin": f"[{lo:.1f},{hi:.1f}{']' if i == bins - 1 else ')'}",
                    "count": 0,
                    "avg_confidence": 0.0,
                    "empirical_accuracy": 0.0,
                }
            )
            continue
        acc = (sub["expected_label_norm"] == sub["core_predicted"]).mean()
        rows.append(
            {
                "bin": f"[{lo:.1f},{hi:.1f}{']' if i == bins - 1 else ')'}",
                "count": int(len(sub)),
                "avg_confidence": float(sub["core_confidence"].mean()),
                "empirical_accuracy": float(acc),
            }
        )
    return pd.DataFrame(rows)


def confusion_highlights(cm_df: pd.DataFrame, top_k: int = 20) -> pd.DataFrame:
    rows = []
    for true_label in cm_df.index:
        for pred_label in cm_df.columns:
            if true_label == pred_label:
                continue
            count = int(cm_df.loc[true_label, pred_label])
            if count <= 0:
                continue
            total_true = int(cm_df.loc[true_label].sum())
            rows.append(
                {
                    "true_label": true_label,
                    "predicted_label": pred_label,
                    "count": count,
                    "rate_within_true_label": float(count / total_true if total_true else 0.0),
                    "true_total": total_true,
                }
            )
    rows.sort(key=lambda x: (x["count"], x["rate_within_true_label"]), reverse=True)
    return pd.DataFrame(rows[:top_k])


def quality_gates(metrics: dict, by_label_df: pd.DataFrame) -> dict:
    fpr = metrics["overall"]["noerror_false_positive_rate"]
    gate1 = fpr <= 0.01

    critical_rows = by_label_df[by_label_df["label"].isin(CORE_CRITICAL_LABELS)]
    critical_failures = []
    for _, row in critical_rows.iterrows():
        if float(row["support"]) > 0 and float(row["recall"]) < 0.95:
            critical_failures.append(
                {"label": row["label"], "recall": float(row["recall"]), "support": int(row["support"])}
            )
    gate2 = len(critical_failures) == 0

    mismatches = int(metrics["overall"]["api_core_mismatch_count"])
    gate3 = mismatches == 0

    return {
        "gate_noerror_false_positive_rate_le_1pct": {"pass": gate1, "value": fpr, "threshold": 0.01},
        "gate_critical_label_recall_ge_95pct": {"pass": gate2, "failures": critical_failures, "threshold": 0.95},
        "gate_api_core_agreement": {"pass": gate3, "mismatch_count": mismatches},
        "release_recommendation": "GO" if gate1 and gate2 and gate3 else "NO-GO",
    }


def top_failures(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    wrong = df[df["expected_label_norm"] != df["core_predicted"]].copy()
    wrong["snippet"] = wrong["code"].str.slice(0, 220).str.replace("\n", "\\n")
    wrong = wrong.sort_values(by=["core_confidence"], ascending=False)
    return wrong[
        [
            "sample_id",
            "language",
            "expected_label_norm",
            "core_predicted",
            "core_confidence",
            "snippet",
            "source_path",
            "source_line",
            "corpus_type",
            "generator",
            "seed",
        ]
    ].head(top_n)


def write_jsonl(path: Path, records: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_report(
    out_dir: Path,
    mode: str,
    metrics: dict,
    gates: dict,
    route_summary: dict,
    compare_summary: dict,
    seed: int,
    command: str,
) -> Path:
    path = out_dir / f"evaluation_report_{mode}.md"
    by_lang = pd.read_csv(out_dir / f"per_language_metrics_{mode}.csv")
    by_label = pd.read_csv(out_dir / f"per_label_metrics_{mode}.csv")
    fail = pd.read_csv(out_dir / f"top_failures_{mode}.csv")
    high = pd.read_csv(out_dir / f"confusion_highlights_{mode}.csv")
    lines = []
    lines.append("# Exhaustive Accuracy Evaluation")
    lines.append("")
    lines.append(f"- Mode: `{mode}`")
    lines.append(f"- Seed: `{seed}`")
    lines.append(f"- Command: `{command}`")
    lines.append(f"- Samples: `{metrics['overall']['samples']}`")
    lines.append(f"- Overall accuracy: `{metrics['overall']['overall_accuracy']:.6f}`")
    lines.append(f"- NoError false-positive rate: `{metrics['overall']['noerror_false_positive_rate']:.6f}`")
    lines.append(f"- API/core mismatch count: `{metrics['overall']['api_core_mismatch_count']}`")
    lines.append(f"- Release recommendation: `{gates['release_recommendation']}`")
    lines.append("")
    lines.append("## Quality Gates")
    lines.append(f"- NoError FPR <= 1%: `{gates['gate_noerror_false_positive_rate_le_1pct']['pass']}`")
    lines.append(f"- Critical label recall >= 95%: `{gates['gate_critical_label_recall_ge_95pct']['pass']}`")
    lines.append(f"- API/core agreement: `{gates['gate_api_core_agreement']['pass']}`")
    lines.append("")
    lines.append("## API Routes")
    lines.append(f"- /health: `{json.dumps(route_summary['health'], ensure_ascii=False)}`")
    lines.append(f"- /check status counts: `{json.dumps(route_summary['check_status_counts'])}`")
    lines.append(f"- /fix status counts: `{json.dumps(route_summary['fix_status_counts'])}`")
    lines.append(f"- /quality status counts: `{json.dumps(route_summary['quality_status_counts'])}`")
    lines.append("")
    lines.append("## Model Availability Comparison")
    lines.append(f"- Comparison summary: `{json.dumps(compare_summary)}`")
    lines.append("")
    lines.append("## Per-language Metrics")
    lines.append(by_lang.to_string(index=False))
    lines.append("")
    lines.append("## Per-label Metrics")
    lines.append(by_label.to_string(index=False))
    lines.append("")
    if len(high):
        lines.append("## Confusion Highlights")
        lines.append(high.to_string(index=False))
        lines.append("")
    if len(fail):
        lines.append("## Top Failures")
        lines.append(fail.to_string(index=False))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Exhaustive OmniSyntax accuracy evaluation")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--grammar-per-language", type=int, default=10000)
    parser.add_argument("--mutation-per-language", type=int, default=2500)
    parser.add_argument("--quality-sample-size", type=int, default=5000)
    parser.add_argument("--fix-sample-size", type=int, default=5000)
    parser.add_argument("--compare-sample-size", type=int, default=5000)
    parser.add_argument("--output-dir", default="artifacts/accuracy")
    args = parser.parse_args()

    started = time.time()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = Path("dataset/merged/all_errors_v3.csv")
    model_label_path = Path("models/label_encoder.pkl")
    command = (
        f"python scripts/evaluate_exhaustive_accuracy.py --seed {args.seed} "
        f"--grammar-per-language {args.grammar_per_language} --mutation-per-language {args.mutation_per_language} "
        f"--quality-sample-size {args.quality_sample_size} --fix-sample-size {args.fix_sample_size} "
        f"--compare-sample-size {args.compare_sample_size}"
    )

    labels = load_supported_labels(dataset_path, model_label_path)
    corpus: list[Sample] = []
    corpus.extend(load_dataset_samples(dataset_path, args.seed))

    valid_seed = args.seed + 11
    valid_samples: list[Sample] = []
    for language in LANGUAGES:
        base_tpl = base_valid_templates()[language]
        for idx, code in enumerate(base_tpl, start=1):
            valid_samples.append(
                mk_sample(
                    language=language,
                    expected_label="NoError",
                    code=code,
                    source_path=f"generated://base_valid/{language}",
                    source_line=idx,
                    corpus_type="deterministic_valid",
                    generator="base_valid_templates",
                    seed=valid_seed,
                )
            )
        valid_samples.extend(generate_valid_grammar(language, args.grammar_per_language, valid_seed + LANGUAGES.index(language)))

    corpus.extend(valid_samples)
    corpus.extend(generate_mutation_samples(valid_samples, args.mutation_per_language, args.seed + 101))
    corpus.extend(adversarial_samples(args.seed + 707))
    corpus.extend(curated_invalid_per_label(args.seed + 909))
    corpus = dedupe_samples(corpus)

    write_jsonl(out_dir / "corpus.jsonl", (asdict(s) for s in corpus))

    available_df, available_routes = evaluate_samples(
        samples=corpus,
        mode="available",
        evaluate_quality_sample_size=args.quality_sample_size,
        evaluate_fix=True,
        evaluate_fix_sample_size=args.fix_sample_size,
        reload_api=True,
        seed=args.seed + 1000,
    )

    compare_subset = available_df.sample(
        n=min(args.compare_sample_size, len(available_df)),
        random_state=args.seed,
    )
    compare_samples = [
        mk_sample(
            language=row["language"],
            expected_label=row["expected_label_norm"],
            code=row["code"],
            source_path=row["source_path"],
            source_line=int(row["source_line"]) if pd.notna(row["source_line"]) else None,
            corpus_type=row["corpus_type"],
            generator=row["generator"],
            seed=int(row["seed"]),
            metadata=row["metadata"] if isinstance(row["metadata"], dict) else {},
        )
        for _, row in compare_subset.iterrows()
    ]

    with forced_model_unavailable():
        forced_df, forced_routes = evaluate_samples(
            samples=compare_samples,
            mode="forced_unavailable",
            evaluate_quality_sample_size=min(1500, args.quality_sample_size),
            evaluate_fix=True,
            evaluate_fix_sample_size=min(1500, args.fix_sample_size),
            reload_api=False,
            seed=args.seed + 2000,
        )

    available_metrics = metrics_from_predictions(available_df, labels=labels)
    available_calibration = calibration_bins(available_df, bins=10)
    available_highlights = confusion_highlights(available_metrics["confusion"], top_k=30)
    available_gates = quality_gates(available_metrics, available_metrics["by_label"])
    available_failures = top_failures(available_df, top_n=20)
    forced_metrics = metrics_from_predictions(forced_df, labels=labels)

    compare_summary = {
        "actual_available_model_loaded": bool(available_routes["health"].get("ml_model_loaded")),
        "forced_unavailable_model_loaded": bool(forced_routes["health"].get("ml_model_loaded")),
        "subset_size": int(len(forced_df)),
        "accuracy_available_subset": float(
            (compare_subset["expected_label_norm"] == compare_subset["core_predicted"]).mean()
            if len(compare_subset)
            else 0.0
        ),
        "accuracy_forced_unavailable_subset": float(forced_metrics["overall"]["overall_accuracy"]),
    }

    available_df.to_csv(out_dir / "predictions_available.csv", index=False)
    write_jsonl(out_dir / "predictions_available.jsonl", available_df.to_dict(orient="records"))
    forced_df.to_csv(out_dir / "predictions_forced_unavailable.csv", index=False)
    write_jsonl(out_dir / "predictions_forced_unavailable.jsonl", forced_df.to_dict(orient="records"))

    pd.DataFrame([available_metrics["overall"]]).to_csv(out_dir / "metrics_overall_available.csv", index=False)
    available_metrics["by_language"].to_csv(out_dir / "per_language_metrics_available.csv", index=False)
    available_metrics["by_label"].to_csv(out_dir / "per_label_metrics_available.csv", index=False)
    available_metrics["confusion"].to_csv(out_dir / "confusion_matrix_available.csv")
    available_highlights.to_csv(out_dir / "confusion_highlights_available.csv", index=False)
    available_calibration.to_csv(out_dir / "calibration_bins_available.csv", index=False)
    available_metrics["mismatches"].to_csv(out_dir / "api_core_mismatches_available.csv", index=False)
    available_failures.to_csv(out_dir / "top_failures_available.csv", index=False)

    (out_dir / "quality_gates_available.json").write_text(
        json.dumps(available_gates, indent=2),
        encoding="utf-8",
    )
    (out_dir / "route_summary_available.json").write_text(
        json.dumps(available_routes, indent=2),
        encoding="utf-8",
    )
    (out_dir / "route_summary_forced_unavailable.json").write_text(
        json.dumps(forced_routes, indent=2),
        encoding="utf-8",
    )
    (out_dir / "model_availability_comparison.json").write_text(
        json.dumps(compare_summary, indent=2),
        encoding="utf-8",
    )

    report_path = write_report(
        out_dir=out_dir,
        mode="available",
        metrics=available_metrics,
        gates=available_gates,
        route_summary=available_routes,
        compare_summary=compare_summary,
        seed=args.seed,
        command=command,
    )

    manifest = {
        "seed": args.seed,
        "grammar_per_language": args.grammar_per_language,
        "mutation_per_language": args.mutation_per_language,
        "quality_sample_size": args.quality_sample_size,
        "fix_sample_size": args.fix_sample_size,
        "compare_sample_size": args.compare_sample_size,
        "output_dir": str(out_dir),
        "total_corpus_samples": len(corpus),
        "labels": labels,
        "elapsed_seconds": time.time() - started,
        "command": command,
        "report_path": str(report_path),
        "critical_labels": CORE_CRITICAL_LABELS,
        "assumptions": [
            "Primary run uses the real model availability state of the environment.",
            "forced_unavailable mode monkeypatches engine and API model status to compare behavior when ML is unavailable.",
            "fix and quality endpoints are evaluated on deterministic subsets for runtime practicality.",
        ],
        "verification_steps": [
            "Run once in a real unavailable-model environment and compare against forced_unavailable for parity.",
            "Increase --quality-sample-size and --fix-sample-size to total corpus size to fully exhaust /quality and /fix routes.",
        ],
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "report": str(report_path),
                "samples": len(corpus),
                "elapsed_sec": time.time() - started,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
