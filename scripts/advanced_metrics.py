"""
Compute advanced evaluation metrics for the trained model.
"""

import argparse
import os
import sys
from typing import cast

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    matthews_corrcoef,
    precision_recall_fscore_support,
)

sys.path.insert(0, os.path.abspath("."))

from src.feature_utils import extract_numerical_features


from scripts.utils.ml_utils import load_model_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Advanced model metrics")
    parser.add_argument("--dataset", default="dataset/merged/all_errors_v3.csv")
    parser.add_argument("--models-dir", default="models")
    parser.add_argument("--output", default="results/advanced_metrics.txt")
    parser.add_argument("--smoke", action="store_true", help="Quick metrics check")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Dataset not found: {args.dataset}")
        return 1

    model, vectorizer, label_encoder, err = load_model_bundle(args.models_dir)
    if err:
        print(f"Skipping advanced metrics: model unavailable ({err})")
        return 0
    if model is None or vectorizer is None or label_encoder is None:
        print("Skipping advanced metrics: incomplete model bundle")
        return 0

    df = pd.read_csv(args.dataset)
    if "buggy_code" not in df.columns or "error_type" not in df.columns:
        print("Dataset must contain buggy_code and error_type columns")
        return 1

    texts = df["buggy_code"].fillna("").astype(str)
    classes = np.asarray(label_encoder.classes_)
    y_true = label_encoder.transform(df["error_type"])
    x_text = vectorizer.transform(texts)
    try:
        from scipy.sparse import hstack

        x_num = np.array([extract_numerical_features(code) for code in texts])
        x = hstack([x_text, x_num])
    except Exception:
        x = x_text

    y_pred = model.predict(x)
    accuracy = accuracy_score(y_true, y_pred)
    kappa = cohen_kappa_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)
    metric_tuple = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(len(classes))), zero_division=0
    )
    precision = np.atleast_1d(metric_tuple[0])
    recall = np.atleast_1d(metric_tuple[1])
    f1 = np.atleast_1d(metric_tuple[2])
    support_raw = metric_tuple[3]
    support = np.atleast_1d(support_raw) if support_raw is not None else np.zeros(len(classes), dtype=int)

    if args.smoke:
        print(f"Smoke OK: accuracy={accuracy:.4f}, classes={len(classes)}")
        return 0

    rows = []
    for idx, label in enumerate(classes):
        label_str = cast(str, label)
        rows.append(
            f"{label_str:24s} prec={float(precision[idx]):.3f} rec={float(recall[idx]):.3f} "
            f"f1={float(f1[idx]):.3f} support={int(support[idx])}"
        )

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write("ADVANCED EVALUATION METRICS\n")
        handle.write("=" * 60 + "\n")
        handle.write(f"Accuracy: {accuracy:.4f}\n")
        handle.write(f"Cohen Kappa: {kappa:.4f}\n")
        handle.write(f"Matthews Corrcoef: {mcc:.4f}\n\n")
        handle.write("Per-class metrics:\n")
        handle.write("\n".join(rows))
        handle.write("\n")

    print(f"Advanced metrics written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
