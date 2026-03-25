"""
Generate prediction results CSV for downstream visualization.
"""

import argparse
import os
import sys

import joblib
import pandas as pd

sys.path.insert(0, os.path.abspath("."))

from src.feature_utils import extract_numerical_features


from scripts.utils.ml_utils import load_model_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate prediction results CSV")
    parser.add_argument("--dataset", default="dataset/merged/all_errors_v3.csv")
    parser.add_argument("--models-dir", default="models")
    parser.add_argument("--output", default="results/results_generated.csv")
    parser.add_argument("--smoke", action="store_true", help="Quick check without writing output")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Dataset not found: {args.dataset}")
        return 1

    model, vectorizer, label_encoder, load_error = load_model_bundle(args.models_dir)
    if load_error:
        print(f"Skipping generation: {load_error}")
        return 0

    df = pd.read_csv(args.dataset)
    if "buggy_code" not in df.columns:
        print("Dataset must contain 'buggy_code' column")
        return 1
    if "error_type" not in df.columns:
        print("Dataset must contain 'error_type' column")
        return 1

    texts = df["buggy_code"].fillna("").astype(str)
    x_text = vectorizer.transform(texts)

    # Try enhanced feature matrix first; fall back gracefully for legacy models.
    try:
        from scipy.sparse import hstack

        x_num = [extract_numerical_features(code) for code in texts]
        x = hstack([x_text, x_num])
    except Exception:
        x = x_text

    y_pred_encoded = model.predict(x)
    y_pred = label_encoder.inverse_transform(y_pred_encoded)

    if args.smoke:
        print(f"Smoke OK: generated predictions for {len(y_pred)} samples")
        return 0

    output_df = pd.DataFrame(
        {
            "code": texts.values,
            "language": df.get("language", pd.Series(["Unknown"] * len(df))).values,
            "error_type": df["error_type"].values,
            "predicted": y_pred,
        }
    )
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    output_df.to_csv(args.output, index=False)
    print(f"Generated {args.output} with {len(output_df)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
