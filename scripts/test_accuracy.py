"""
test_accuracy.py
================
Comprehensive accuracy test for OmniSyntax: A Hybrid AI Code Tutor.

Tests three layers:
  1. ML Engine alone        — raw model predictions vs ground truth
  2. Full Pipeline          — detect_errors() end-to-end accuracy
  3. Rule-Based (Python)    — syntax_checker accuracy on Python samples

Usage:
    python test_accuracy.py
    python test_accuracy.py --samples 500   # test on a random subset
    python test_accuracy.py --lang Python   # test one language only
    python test_accuracy.py --verbose       # show every wrong prediction
"""

import sys
import os
import csv
import time
import argparse
import random
import io
from collections import defaultdict, Counter

# Prevent cp1252 crashes for Unicode output on Windows terminals.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath('.'))

# ─── Colour helpers (works on Windows with ANSI enabled) ──────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def green(s):  return f"{GREEN}{s}{RESET}"
def red(s):    return f"{RED}{s}{RESET}"
def yellow(s): return f"{YELLOW}{s}{RESET}"
def cyan(s):   return f"{CYAN}{s}{RESET}"
def bold(s):   return f"{BOLD}{s}{RESET}"

BAR_WIDTH = 30

def pct_bar(pct):
    filled = int(BAR_WIDTH * pct / 100)
    bar = "█" * filled + "░" * (BAR_WIDTH - filled)
    colour = GREEN if pct >= 90 else YELLOW if pct >= 70 else RED
    return f"{colour}[{bar}]{RESET} {pct:.2f}%"


# ─── Load dataset ─────────────────────────────────────────────────────────────
DATASET_PATHS = [
    "dataset/merged/all_errors_v2.csv",
    "all_errors_v2.csv",
]

def load_dataset(lang_filter=None, max_samples=None):
    for path in DATASET_PATHS:
        if os.path.exists(path):
            break
    else:
        print(red("❌ Dataset not found. Tried:"))
        for p in DATASET_PATHS:
            print(f"   {p}")
        sys.exit(1)

    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if lang_filter and row['language'].lower() != lang_filter.lower():
                continue
            rows.append(row)

    if max_samples and max_samples < len(rows):
        random.seed(42)
        rows = random.sample(rows, max_samples)

    return rows, path


# ─── Imports ──────────────────────────────────────────────────────────────────
def import_modules():
    try:
        from src.ml_engine import detect_error_ml, model_loaded
        from src.error_engine import detect_errors
        from src.syntax_checker import detect_all
        return detect_error_ml, model_loaded, detect_errors, detect_all
    except Exception as e:
        print(red(f"❌ Failed to import src modules: {e}"))
        sys.exit(1)


# ─── Test 1: ML Engine ────────────────────────────────────────────────────────
def test_ml_engine(rows, detect_error_ml, model_loaded, verbose=False):
    print(bold(f"\n{'='*60}"))
    print(bold("  TEST 1: ML Engine Accuracy"))
    print(bold(f"{'='*60}"))

    if not model_loaded:
        print(yellow("  ⚠️  ML model not loaded — skipping ML engine test."))
        return None

    correct = 0
    total = 0
    wrong = []
    by_lang = defaultdict(lambda: [0, 0])    # lang -> [correct, total]
    by_type = defaultdict(lambda: [0, 0])    # error_type -> [correct, total]
    confidences = []

    start = time.time()
    for row in rows:
        code       = row['buggy_code']
        true_label = row['error_type']
        language   = row['language']

        pred_label, confidence = detect_error_ml(code)
        confidences.append(confidence)

        by_lang[language][1] += 1
        by_type[true_label][1] += 1
        total += 1

        if pred_label == true_label:
            correct += 1
            by_lang[language][0] += 1
            by_type[true_label][0] += 1
        else:
            wrong.append((language, true_label, pred_label, confidence, code[:60]))

    elapsed = time.time() - start
    accuracy = correct / total * 100 if total else 0
    avg_conf = sum(confidences) / len(confidences) * 100 if confidences else 0

    print(f"\n  Samples tested : {total}")
    print(f"  Correct        : {correct}")
    print(f"  Wrong          : {total - correct}")
    print(f"  Accuracy       : {pct_bar(accuracy)}")
    print(f"  Avg Confidence : {avg_conf:.2f}%")
    print(f"  Time taken     : {elapsed:.2f}s  ({elapsed/total*1000:.1f}ms/sample)")

    # Per-language breakdown
    print(f"\n  {bold('Per-Language Breakdown:')}")
    for lang in sorted(by_lang):
        c, t = by_lang[lang]
        p = c / t * 100 if t else 0
        print(f"    {lang:<8} {pct_bar(p)}  ({c}/{t})")

    # Per-error-type breakdown
    print(f"\n  {bold('Per-Error-Type Breakdown:')}")
    for etype in sorted(by_type):
        c, t = by_type[etype]
        p = c / t * 100 if t else 0
        status = green("✓") if p >= 95 else yellow("~") if p >= 80 else red("✗")
        print(f"    {status} {etype:<25} {p:6.2f}%  ({c}/{t})")

    # Worst predictions
    if wrong and verbose:
        print(f"\n  {bold('Wrong Predictions (verbose):')}")
        for lang, true, pred, conf, snippet in wrong[:20]:
            print(f"    [{lang}] True={true} | Pred={red(pred)} | Conf={conf:.2f}")
            print(f"           Code: {snippet!r}")

    return accuracy


# ─── Test 2: Full Pipeline (detect_errors) ────────────────────────────────────
def test_full_pipeline(rows, detect_errors, verbose=False):
    print(bold(f"\n{'='*60}"))
    print(bold("  TEST 2: Full Pipeline Accuracy (detect_errors)"))
    print(bold(f"{'='*60}"))

    correct = 0
    total = 0
    wrong = []
    no_error_false = 0   # predicted NoError when there IS an error
    by_lang = defaultdict(lambda: [0, 0])
    by_type = defaultdict(lambda: [0, 0])

    # Build fake filenames for language detection
    ext_map = {'Python': '.py', 'Java': '.java', 'C': '.c', 'C++': '.cpp', 'JavaScript': '.js'}

    start = time.time()
    for row in rows:
        code       = row['buggy_code']
        true_label = row['error_type']
        language   = row['language']
        filename   = f"test{ext_map.get(language, '.py')}"

        try:
            result     = detect_errors(code, filename)
            pred_label = result['predicted_error']
        except Exception as e:
            pred_label = "ERROR"

        by_lang[language][1] += 1
        by_type[true_label][1] += 1
        total += 1

        if pred_label == true_label:
            correct += 1
            by_lang[language][0] += 1
            by_type[true_label][0] += 1
        else:
            if pred_label == "NoError":
                no_error_false += 1
            wrong.append((language, true_label, pred_label, code[:60]))

    elapsed = time.time() - start
    accuracy = correct / total * 100 if total else 0

    print(f"\n  Samples tested      : {total}")
    print(f"  Correct             : {correct}")
    print(f"  Wrong               : {total - correct}")
    print(f"  False 'NoError'     : {no_error_false}  (missed errors)")
    print(f"  Accuracy            : {pct_bar(accuracy)}")
    print(f"  Time taken          : {elapsed:.2f}s  ({elapsed/total*1000:.1f}ms/sample)")

    # Per-language breakdown
    print(f"\n  {bold('Per-Language Breakdown:')}")
    for lang in sorted(by_lang):
        c, t = by_lang[lang]
        p = c / t * 100 if t else 0
        print(f"    {lang:<8} {pct_bar(p)}  ({c}/{t})")

    # Per-error-type breakdown
    print(f"\n  {bold('Per-Error-Type Breakdown:')}")
    for etype in sorted(by_type):
        c, t = by_type[etype]
        p = c / t * 100 if t else 0
        status = green("✓") if p >= 95 else yellow("~") if p >= 80 else red("✗")
        print(f"    {status} {etype:<25} {p:6.2f}%  ({c}/{t})")

    # Most common misclassifications
    if wrong:
        confusion = Counter((true, pred) for _, true, pred, _ in wrong)
        print(f"\n  {bold('Top Misclassifications:')}")
        for (true, pred), count in confusion.most_common(8):
            print(f"    {count:3}x  {true:<25} → {red(pred)}")

    if wrong and verbose:
        print(f"\n  {bold('Wrong Predictions (verbose):')}")
        for lang, true, pred, snippet in wrong[:20]:
            print(f"    [{lang}] True={true} | Pred={red(pred)}")
            print(f"           Code: {snippet!r}")

    return accuracy


# ─── Test 3: Rule-Based Python Only ───────────────────────────────────────────
def test_rule_based(rows, detect_all, verbose=False):
    print(bold(f"\n{'='*60}"))
    print(bold("  TEST 3: Rule-Based Detector Accuracy (Python only)"))
    print(bold(f"{'='*60}"))

    python_rows = [r for r in rows if r['language'] == 'Python']
    if not python_rows:
        print(yellow("  ⚠️  No Python samples in current filter — skipping."))
        return None

    true_pos  = 0   # error correctly detected
    false_neg = 0   # error missed (returned nothing)
    wrong_type = 0  # detected something but wrong type
    total = len(python_rows)
    by_type = defaultdict(lambda: [0, 0])

    for row in python_rows:
        code       = row['buggy_code']
        true_label = row['error_type']

        issues = detect_all(code)
        detected_types = [i['type'] for i in issues]

        by_type[true_label][1] += 1

        if true_label in detected_types:
            true_pos += 1
            by_type[true_label][0] += 1
        elif detected_types:
            wrong_type += 1
        else:
            false_neg += 1

    recall = true_pos / total * 100 if total else 0

    print(f"\n  Python samples tested : {total}")
    print(f"  Correct type detected : {true_pos}")
    print(f"  Missed (no detection) : {false_neg}")
    print(f"  Wrong type detected   : {wrong_type}")
    print(f"  Recall                : {pct_bar(recall)}")
    print(f"\n  Note: Rule-based only covers MissingDelimiter, IndentationError,")
    print(f"        UnmatchedBracket, UnclosedQuotes. Other types fall")
    print(f"        through to ML — low recall here is expected.")

    print(f"\n  {bold('Per-Error-Type Recall:')}")
    for etype in sorted(by_type):
        c, t = by_type[etype]
        p = c / t * 100 if t else 0
        status = green("✓") if p >= 95 else yellow("~") if p >= 50 else red("✗")
        print(f"    {status} {etype:<25} {p:6.2f}%  ({c}/{t})")

    return recall


# ─── Summary ──────────────────────────────────────────────────────────────────
def print_summary(ml_acc, pipeline_acc, rule_recall, total_samples, elapsed_total):
    print(bold(f"\n{'='*60}"))
    print(bold("  FINAL SUMMARY"))
    print(bold(f"{'='*60}"))
    print(f"\n  Total samples tested : {total_samples}")
    print(f"  Total time           : {elapsed_total:.2f}s")
    print()

    target = 99.80
    if ml_acc is not None:
        gap = ml_acc - target
        indicator = green("✅") if ml_acc >= target else yellow("⚠️ ")
        print(f"  {indicator} ML Engine Accuracy   : {ml_acc:.2f}%  (target: {target}%,  gap: {gap:+.2f}%)")
    if pipeline_acc is not None:
        indicator = green("✅") if pipeline_acc >= 90 else yellow("⚠️ ")
        print(f"  {indicator} Full Pipeline Accuracy: {pipeline_acc:.2f}%")
    if rule_recall is not None:
        indicator = green("✅") if rule_recall >= 80 else yellow("⚠️ ")
        print(f"  {indicator} Rule-Based Recall     : {rule_recall:.2f}%  (Python syntax rules)")

    print()
    if ml_acc is not None and ml_acc >= target:
        print(green("  🎉 Model meets the 99.80% accuracy target!"))
    elif ml_acc is not None:
        print(yellow(f"  ⚠️  Model is {target - ml_acc:.2f}% below the 99.80% target."))
        print(yellow("     Consider retraining with: python scripts/optimize_model.py"))
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Accuracy test for OmniSyntax")
    parser.add_argument('--samples', type=int, default=None,
                        help='Number of random samples to test (default: all)')
    parser.add_argument('--lang', type=str, default=None,
                        help='Filter by language: Python, Java, C, C++')
    parser.add_argument('--verbose', action='store_true',
                        help='Show individual wrong predictions')
    parser.add_argument('--skip-pipeline', action='store_true',
                        help='Skip the full pipeline test (faster)')
    args = parser.parse_args()

    print(bold(cyan("\n" + "="*60)))
    print(bold(cyan("  Accuracy Test — OmniSyntax")))
    print(bold(cyan("="*60)))

    # Load dataset
    rows, path = load_dataset(args.lang, args.samples)
    print(f"\n  Dataset  : {path}")
    print(f"  Samples  : {len(rows)}")
    if args.lang:
        print(f"  Filter   : {args.lang} only")

    # Import modules
    detect_error_ml, model_loaded, detect_errors, detect_all = import_modules()

    total_start = time.time()

    # Run tests
    ml_acc       = test_ml_engine(rows, detect_error_ml, model_loaded, args.verbose)
    pipeline_acc = None
    if not args.skip_pipeline:
        pipeline_acc = test_full_pipeline(rows, detect_errors, args.verbose)
    rule_recall  = test_rule_based(rows, detect_all, args.verbose)

    elapsed_total = time.time() - total_start

    # Final summary
    print_summary(ml_acc, pipeline_acc, rule_recall, len(rows), elapsed_total)


if __name__ == '__main__':
    main()
