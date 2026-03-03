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
    python retrain_model.py --dataset dataset/merged/all_errors_v2.csv
    python retrain_model.py --preview          # show dataset stats only, no train
    python retrain_model.py --compare          # compare old vs new model accuracy
"""

import os
import sys
import csv
import pickle
import argparse
import warnings
import time
from collections import Counter

import numpy as np
from scipy.sparse import hstack

warnings.filterwarnings('ignore')

# Import shared feature extraction (single source of truth)
try:
    from src.feature_utils import extract_numerical_features, NUMERICAL_FEATURE_NAMES
    _SHARED_FEATURES_AVAILABLE = True
except ImportError:
    _SHARED_FEATURES_AVAILABLE = False

# ─── Colour helpers ──────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
def green(s):  return f"{GREEN}{s}{RESET}"
def red(s):    return f"{RED}{s}{RESET}"
def yellow(s): return f"{YELLOW}{s}{RESET}"
def bold(s):   return f"{BOLD}{s}{RESET}"
def cyan(s):   return f"{CYAN}{s}{RESET}"

# ─── Paths ────────────────────────────────────────────────────────────────────
DATASET_PATHS = [
    "dataset/merged/all_errors_v2.csv",
    "dataset/merged/all_errors.csv",
    "all_errors_v2.csv",
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


# ─── Feature extraction ───────────────────────────────────────────────────────
NUMERICAL_FEATURE_NAMES = [
    'code_length', 'num_lines', 'has_division', 'has_type_conv',
    'missing_colon', 'missing_semicolon', 'compares_zero',
    'has_string_ops', 'has_type_decl', 'bracket_diff'
]

def extract_numerical_features(code: str) -> list:
    """
    Extract the same 10 numerical features as the original model.
    Must match EXACTLY what the original training used.
    """
    lines = code.split('\n')
    non_empty = [l.strip() for l in lines if l.strip()]

    return [
        len(code),                                                   # code_length
        len(lines),                                                  # num_lines
        int('/' in code and '0' in code),                           # has_division
        int(any(t in code for t in ['int(', 'float(', 'str(', 'bool('])),  # has_type_conv
        int(':' not in code and any(kw in code for kw in ['def ', 'if ', 'for ', 'while ', 'class '])),  # missing_colon
        int(';' not in code and any(kw in code for kw in ['printf', 'cout', 'System.out', 'fprintf'])),  # missing_semicolon
        int('== 0' in code or '!= 0' in code or '/0' in code or '/ 0' in code),  # compares_zero
        int(any(op in code for op in ['.upper()', '.lower()', '.split()', '.join(', '.strip()'])),  # has_string_ops
        int(any(t in code for t in ['int ', 'float ', 'double ', 'String ', 'char ', 'bool '])),  # has_type_decl
        code.count('(') - code.count(')'),                          # bracket_diff
    ]


def build_features(codes, tfidf, fit_tfidf=False):
    """Build combined TF-IDF + numerical feature matrix."""
    if fit_tfidf:
        tfidf_matrix = tfidf.fit_transform(codes)
    else:
        tfidf_matrix = tfidf.transform(codes)

    num_matrix = np.array([extract_numerical_features(c) for c in codes])
    return hstack([tfidf_matrix, num_matrix])


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
    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]
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

                old_codes_test = [codes[i] for i in test_idx]
                old_tfidf_test = old_tfidf.transform(old_codes_test)
                if os.path.exists(old_num_path):
                    old_num_test = np.array([extract_numerical_features(c) for c in old_codes_test])
                    old_X_test = hstack([old_tfidf_test, old_num_test])
                else:
                    old_X_test = old_tfidf_test

                old_pred = old_model.predict(old_X_test)
                old_pred_labels = old_le.inverse_transform(old_pred)
                y_test_labels = le.inverse_transform(y_test[:len(old_pred_labels)])
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
    report = classification_report(
        y_test, y_pred,
        target_names=le.classes_,
        output_dict=True,
        zero_division=0
    )

    print(f"\n  {'Error Type':<25} {'Prec':>6} {'Recall':>7} {'F1':>6} {'Support':>8}")
    print(f"  {'─'*25} {'─'*6} {'─'*7} {'─'*6} {'─'*8}")
    for cls in le.classes_:
        m = report.get(cls, {})
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
    }

    pickle.dump(clf,   open(paths["model"],    'wb'))
    pickle.dump(le,    open(paths["encoder"],  'wb'))
    pickle.dump(tfidf, open(paths["tfidf"],    'wb'))
    pickle.dump(NUMERICAL_FEATURE_NAMES, open(paths["num_feats"], 'wb'))

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
    parser = argparse.ArgumentParser(description="Retrain the syntax error detection model")
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
    print(bold(cyan(f"  Model Retraining — Syntax Error Detection System")))
    print(bold(cyan(f"{'='*60}")))

    # Find dataset
    dataset_path = find_dataset(args.dataset)
    if not dataset_path:
        print(red("\n❌ No dataset found. Tried:"))
        for p in DATASET_PATHS:
            print(f"   {p}")
        print(f"\nRun: python augment_dataset.py  first to generate all_errors_v2.csv")
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
