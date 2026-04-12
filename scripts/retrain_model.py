"""
retrain_model.py
================
Retrains the Gradient Boosting model on the augmented dataset.

Preserves the EXACT same feature pipeline as the original model:
  - TF-IDF vectorizer (text features from code)
  - 10 numerical features (code_length, num_lines, etc.)
  - GradientBoostingClassifier

Overwrites the existing model files so the app immediately uses new model.

Usage:
    python retrain_model.py                    # full retrain, auto-find dataset
    python retrain_model.py --dataset dataset/merged/all_errors_v3.csv
    python retrain_model.py --preview          # show dataset stats only, no train
    python retrain_model.py --compare          # compare old vs new model accuracy
"""

import os
import sys
import csv
import json
import pickle
import argparse
import warnings
import time
from collections import Counter
from typing import Any, cast

import numpy as np
from scipy.sparse import hstack

warnings.filterwarnings('ignore')

# ─── Ensure project root is on sys.path so `src` package is importable ─────
_here = os.path.abspath(__file__)               # e.g. .../scripts/retrain_model.py
_project_root = os.path.dirname(os.path.dirname(_here))  # .../project_root
_src_root = os.path.join(_project_root, "src")
for _p in (_src_root, _project_root, os.getcwd()):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from src.feature_utils import extract_numerical_features, NUMERICAL_FEATURE_NAMES

# ─── Colour helpers ──────────────────────────────────────────────────────────
from src.utils.cli_colors import GREEN, RED, YELLOW, CYAN, BOLD, RESET, green, red, yellow, bold, cyan

# ─── Paths ────────────────────────────────────────────────────────────────────
DATASET_PATHS = [
    "dataset/merged/all_errors_v3.csv",
    "dataset/merged/all_errors.csv",
    "all_errors_v3.csv",
    "all_errors.csv",
]

MODEL_DIR_CANDIDATES = [
    "models",
    "model",
    "src/models",
    ".",
]

MODEL_FILES = {
    "model":      "syntax_error_model.pkl",
    "encoder":    "label_encoder.pkl",
    "tfidf":      "tfidf_vectorizer.pkl",
    "num_feats":  "numerical_features.pkl",
}
MODEL_BUNDLE_METADATA = "bundle_metadata.json"


def configure_console_output():
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def get_bundle_metadata():
    import sklearn

    version = sklearn.__version__
    major_minor = ".".join(version.split(".")[:2])
    return {
        "sklearn_version": version,
        "sklearn_major_minor": major_minor,
        "artifact_format": "tfidf+numerical+gradient_boosting",
    }


def find_dataset(override=None):
    if override and os.path.exists(override):
        return override
    for p in DATASET_PATHS:
        if os.path.exists(p):
            return p
    return None


def find_model_dir():
    """Find directory containing existing model files."""
    for d in MODEL_DIR_CANDIDATES:
        if os.path.exists(os.path.join(d, MODEL_FILES["model"])):
            return d
    return None




def build_features(codes, tfidf, fit_tfidf=False):
    """Build combined TF-IDF + numerical feature matrix."""
    if fit_tfidf:
        tfidf_matrix = tfidf.fit_transform(codes)
    else:
        tfidf_matrix = tfidf.transform(codes)

    num_matrix = np.array([extract_numerical_features(c) for c in codes])
    return hstack([tfidf_matrix, num_matrix]).tocsr()


# ─── Load dataset ────────────────────────────────────────────────────────────
def load_dataset(path):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('buggy_code', '').strip() and row.get('error_type', '').strip():
                rows.append(row)
    return rows


def print_dataset_stats(rows, title="Dataset Statistics"):
    counts = Counter(r['error_type'] for r in rows)
    lang_counts = Counter(r['language'] for r in rows)
    target = 200

    print(f"\n  {bold(title)}")
    print(f"  {'─'*50}")
    print(f"  Total samples : {len(rows)}")
    print(f"  Error types   : {len(counts)}")
    print(f"  Languages     : {dict(lang_counts)}")
    print(f"\n  {'Error Type':<25} {'Count':>6}  {'Bar'}")
    print(f"  {'─'*25} {'─'*6}  {'─'*20}")
    for t, v in sorted(counts.items(), key=lambda x: x[1]):
        bar = '█' * min(20, v // 10)
        flag = green(" ✓") if v >= target else yellow(" ~") if v >= 100 else red(" ✗")
        print(f"  {t:<25} {v:>6}  {bar}{flag}")


# ─── Training ─────────────────────────────────────────────────────────────────
def train_model(rows, model_dir, compare_old=False):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    codes  = [r['buggy_code'] for r in rows]
    labels = [r['error_type'] for r in rows]

    print(f"\n  {bold('Step 1: Encoding labels...')}")
    le = LabelEncoder()
    y = le.fit_transform(labels)
    print(f"  Classes: {list(le.classes_)}")

    print(f"\n  {bold('Step 2: Building TF-IDF + numerical features...')}")
    tfidf = TfidfVectorizer(
        analyzer='char_wb',
        ngram_range=(2, 4),
        max_features=5000,
        sublinear_tf=True
    )
    X = build_features(codes, tfidf, fit_tfidf=True)
    print(f"  Feature matrix: {X.shape}")

    print(f"\n  {bold('Step 3: Train/test split (80/20)...')}")
    indices = np.arange(len(codes))
    train_idx, test_idx = train_test_split(
        indices, test_size=0.2, random_state=42, stratify=y
    )
    train_idx = np.asarray(train_idx, dtype=np.intp)
    test_idx = np.asarray(test_idx, dtype=np.intp)
    y_arr = np.asarray(y)
    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = y_arr[train_idx]
    y_test = y_arr[test_idx]
    print(f"  Train: {X_train.shape[0]}  |  Test: {X_test.shape[0]}")

    # Optional: evaluate old model on same test set
    old_acc = None
    if compare_old:
        old_model_path = os.path.join(model_dir, MODEL_FILES["model"])
        old_tfidf_path = os.path.join(model_dir, MODEL_FILES["tfidf"])
        old_le_path    = os.path.join(model_dir, MODEL_FILES["encoder"])
        old_num_path   = os.path.join(model_dir, MODEL_FILES["num_feats"])
        if all(os.path.exists(p) for p in [old_model_path, old_tfidf_path, old_le_path]):
            try:
                def _load_model_file(path):
                    try:
                        import joblib
                        return joblib.load(path)
                    except Exception:
                        with open(path, 'rb') as f:
                            return pickle.load(f)

                old_model = _load_model_file(old_model_path)
                old_tfidf = _load_model_file(old_tfidf_path)
                old_le    = _load_model_file(old_le_path)

                old_codes_test = [codes[int(i)] for i in test_idx]
                old_tfidf_test = old_tfidf.transform(old_codes_test)
                if os.path.exists(old_num_path):
                    old_num_test = np.array([extract_numerical_features(c) for c in old_codes_test])
                    old_X_test = hstack([old_tfidf_test, old_num_test])
                else:
                    old_X_test = old_tfidf_test

                old_pred = old_model.predict(old_X_test)
                old_pred_labels = old_le.inverse_transform(old_pred)
                y_test_labels = le.inverse_transform(np.asarray(y_test)[:len(old_pred_labels)])
                old_acc = accuracy_score(y_test_labels, old_pred_labels) * 100
                print(f"\n  Old model accuracy on test set: {old_acc:.2f}%")
            except Exception as e:
                print(f"\n  Could not load old model for comparison: {e}")

    print(f"\n  {bold('Step 4: Training GradientBoostingClassifier...')}")
    print(f"  (This takes 2-5 minutes...)")
    start = time.time()

    clf = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        subsample=0.8,
        min_samples_split=5,
        random_state=42,
        verbose=0
    )
    clf.fit(X_train, y_train)
    elapsed = time.time() - start
    print(f"  Training complete in {elapsed:.1f}s")

    print(f"\n  {bold('Step 5: Evaluating...')}")
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred) * 100
    print(f"  Test accuracy: {green(f'{acc:.4f}%')}")

    # Per-class metrics
    report = cast(
        dict[str, Any],
        classification_report(
            y_test,
            y_pred,
            target_names=le.classes_,
            output_dict=True,
            zero_division=0,
        ),
    )

    print(f"\n  {'Error Type':<25} {'Prec':>6} {'Recall':>7} {'F1':>6} {'Support':>8}")
    print(f"  {'─'*25} {'─'*6} {'─'*7} {'─'*6} {'─'*8}")
    for cls in le.classes_:
        m_raw = report.get(cls, {})
        if not isinstance(m_raw, dict):
            continue
        m = cast(dict[str, Any], m_raw)
        p  = m.get('precision', 0)
        r  = m.get('recall', 0)
        f1 = m.get('f1-score', 0)
        s  = int(m.get('support', 0))
        flag = green("✓") if f1 >= 0.95 else yellow("~") if f1 >= 0.80 else red("✗")
        print(f"  {flag} {cls:<23} {p:6.3f}  {r:6.3f}  {f1:6.3f}  {s:7d}")

    if compare_old and old_acc is not None:
        delta = acc - old_acc
        sign = "+" if delta >= 0 else ""
        print(f"\n  Old model: {old_acc:.4f}%  →  New model: {acc:.4f}%  ({sign}{delta:.4f}%)")

    return clf, le, tfidf, acc


# ─── Save model ───────────────────────────────────────────────────────────────
def save_model(clf, le, tfidf, model_dir):
    os.makedirs(model_dir, exist_ok=True)

    paths = {
        "model":     os.path.join(model_dir, MODEL_FILES["model"]),
        "encoder":   os.path.join(model_dir, MODEL_FILES["encoder"]),
        "tfidf":     os.path.join(model_dir, MODEL_FILES["tfidf"]),
        "num_feats": os.path.join(model_dir, MODEL_FILES["num_feats"]),
        "metadata":  os.path.join(model_dir, MODEL_BUNDLE_METADATA),
    }

    pickle.dump(clf,   open(paths["model"],    'wb'))
    pickle.dump(le,    open(paths["encoder"],  'wb'))
    pickle.dump(tfidf, open(paths["tfidf"],    'wb'))
    pickle.dump(NUMERICAL_FEATURE_NAMES, open(paths["num_feats"], 'wb'))
    with open(paths["metadata"], "w", encoding="utf-8") as metadata_file:
        json.dump(get_bundle_metadata(), metadata_file, indent=2, sort_keys=True)

    print(f"\n  {bold('Model files saved:')}")
    for k, p in paths.items():
        size = os.path.getsize(p) / 1024
        print(f"    {green('✓')} {p}  ({size:.1f} KB)")


# ─── Quick smoke test ─────────────────────────────────────────────────────────
def smoke_test(clf, le, tfidf):
    test_cases = [
        ("x = 1/0",                    "DivisionByZero"),
        ("def foo()\n    pass",         "MissingColon"),
        ("from os import *",            "WildcardImport"),
        ("print('Hello'",              "UnmatchedBracket"),
        ("def f():\n    return 1\n    dead_code()", "UnreachableCode"),
    ]

    print(f"\n  {bold('Smoke test:')}")
    all_pass = True
    for code, expected in test_cases:
        tfidf_vec = tfidf.transform([code])
        num_vec   = np.array([extract_numerical_features(code)])
        X = hstack([tfidf_vec, num_vec])
        pred = le.inverse_transform(clf.predict(X))[0]
        prob = clf.predict_proba(X).max()
        ok   = pred == expected
        if not ok:
            all_pass = False
        status = green("✓") if ok else red("✗")
        print(f"    {status} {expected:<25} → Predicted: {pred}  ({prob:.2%})")

    return all_pass


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    configure_console_output()
    parser = argparse.ArgumentParser(description="Retrain OmniSyntax model")
    parser.add_argument('--dataset', type=str, default=None,
                        help='Path to training CSV (default: auto-detect)')
    parser.add_argument('--model-dir', type=str, default=None,
                        help='Directory to save model files (default: auto-detect)')
    parser.add_argument('--preview', action='store_true',
                        help='Show dataset stats only, do not train')
    parser.add_argument('--compare', action='store_true',
                        help='Compare accuracy vs old model')
    args = parser.parse_args()

    print(bold(cyan(f"\n{'='*60}")))
    print(bold(cyan(f"  Model Retraining — OmniSyntax")))
    print(bold(cyan(f"{'='*60}")))

    # Find dataset
    dataset_path = find_dataset(args.dataset)
    if not dataset_path:
        print(red("\n❌ No dataset found. Tried:"))
        for p in DATASET_PATHS:
            print(f"   {p}")
        print(f"\nRun: python augment_dataset.py  first to generate all_errors_v3.csv")
        sys.exit(1)

    # Find model dir
    model_dir = args.model_dir or find_model_dir() or "models"
    print(f"\n  Dataset   : {dataset_path}")
    print(f"  Model dir : {model_dir}")

    # Load dataset
    rows = load_dataset(dataset_path)
    print_dataset_stats(rows, "Training Dataset")

    if args.preview:
        print(f"\n  (Preview only — no training performed)")
        return

    # Check sklearn is available
    try:
        from sklearn.ensemble import GradientBoostingClassifier
    except ImportError:
        print(red("\n❌ scikit-learn not found. Run: pip install scikit-learn"))
        sys.exit(1)

    # Train
    clf, le, tfidf, acc = train_model(rows, model_dir, compare_old=args.compare)

    # Save
    print(f"\n  {bold('Saving model files...')}")
    save_model(clf, le, tfidf, model_dir)

    # Smoke test
    passed = smoke_test(clf, le, tfidf)

    # Final summary
    print(bold(f"\n{'='*60}"))
    print(bold(f"  RETRAIN COMPLETE"))
    print(bold(f"{'='*60}"))
    print(f"\n  Training samples : {len(rows)}")
    print(f"  Test accuracy    : {green(f'{acc:.4f}%')}")
    print(f"  Smoke test       : {green('PASSED') if passed else yellow('PARTIAL')}")
    print(f"\n  Next steps:")
    print(f"    python test_accuracy.py          ← verify full pipeline")
    print(f"    python test_false_positives.py   ← verify no regressions")
    print(f"    python -m pytest tests/ -v       ← run unit tests")
    print()


if __name__ == '__main__':
    main()
