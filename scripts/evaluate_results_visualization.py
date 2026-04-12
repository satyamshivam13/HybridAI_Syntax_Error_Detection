"""
Evaluation & Visualization Script
OmniSyntax: A Hybrid AI Code Tutor

Generates:
  results/01_confusion_matrix.png
  results/02_per_error_accuracy.png
  results/03_language_accuracy.png
  results/04_detection_source_pie.png
  results/05_class_f1_scores.png

Updated: March 2026
Supports: Python, Java, C, C++, JavaScript (5 languages)
Error Types: 18 categories
"""

import os, sys, warnings
from typing import Any, cast
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # headless � no display required
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
from scripts.utils.ml_utils import load_model_bundle

# -- Paths -------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA  = os.path.join(ROOT, "dataset", "merged", "all_errors_v3.csv")
MODELS = os.path.join(ROOT, "models")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(RESULTS, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")

print("=" * 70)
print("  EVALUATION & VISUALIZATION � OmniSyntax: A Hybrid AI Code Tutor")
print("  5 Languages | 18 Error Types | March 2026")
print("=" * 70)

# -- 1. Load dataset & model --------------------------------------------------
df = pd.read_csv(DATA)
print(f"\n  Dataset loaded: {len(df):,} samples, {df['error_type'].nunique()} error types")
print(f"  Languages: {sorted(df['language'].unique())}")

model, vec, le, load_err = load_model_bundle(MODELS)
if load_err:
    print(f"  ?? Model loading issue: {load_err}")
    sys.exit(1)
if model is None or vec is None or le is None:
    print("  ?? Model bundle is incomplete (model/vectorizer/label encoder missing)")
    sys.exit(1)

# Import feature extractor
sys.path.insert(0, ROOT)
from src.feature_utils import extract_numerical_features, NUMERICAL_FEATURE_NAMES

# -- 2. Build prediction dataframe ---------------------------------------------
print("\n  Running predictions on the full dataset �")
texts = df["buggy_code"].fillna("").tolist()

num_feats = pd.DataFrame(
    [extract_numerical_features(c) for c in texts],
    columns=NUMERICAL_FEATURE_NAMES
)
from scipy.sparse import hstack
X = hstack([vec.transform(texts), num_feats.values])

y_true_enc = le.transform(df["error_type"])
y_pred_enc = model.predict(X)
y_true = le.inverse_transform(y_true_enc)
y_pred = le.inverse_transform(y_pred_enc)
df["predicted_error"] = y_pred

# -- 3. Overall metrics --------------------------------------------------------
acc  = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
rec  = recall_score(y_true, y_pred, average="weighted", zero_division=0)
f1   = f1_score(y_true, y_pred, average="weighted", zero_division=0)

print(f"\n  Overall Accuracy  : {acc*100:.2f}%")
print(f"  Weighted Precision: {prec*100:.2f}%")
print(f"  Weighted Recall   : {rec*100:.2f}%")
print(f"  Weighted F1-Score : {f1*100:.2f}%")
report_text = cast(str, classification_report(y_true, y_pred, zero_division=0, output_dict=False))
print("\n" + report_text)

# -- 4. Plot 1: Confusion Matrix -----------------------------------------------
labels = sorted(set(y_true) | set(y_pred))
cm = confusion_matrix(y_true, y_pred, labels=labels)
fig, ax = plt.subplots(figsize=(14, 12))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=labels, yticklabels=labels,
            linewidths=0.4, ax=ax)
ax.set_xlabel("Predicted", fontsize=12)
ax.set_ylabel("True", fontsize=12)
ax.set_title(f"Confusion Matrix � 18 Error Categories\n(Accuracy: {acc*100:.2f}%)", fontsize=14, fontweight="bold")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
path1 = os.path.join(RESULTS, "01_confusion_matrix.png")
plt.savefig(path1, dpi=150, bbox_inches="tight")
plt.close()
print(f"  [OK] Saved: {path1}")

# -- 5. Plot 2: Per-Error Accuracy ---------------------------------------------
per_error = {}
for err in sorted(df["error_type"].unique()):
    sub = df[df["error_type"] == err]
    per_error[err] = accuracy_score(sub["error_type"], sub["predicted_error"]) * 100

pe_series = pd.Series(per_error).sort_values(ascending=False)
pe_vals = np.asarray(pe_series.values, dtype=float)
fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar(pe_series.index.tolist(), pe_vals,
              color=[plt.get_cmap("RdYlGn")(float(v) / 100.0) for v in pe_vals])
ax.axhline(float(acc * 100), color="navy", linestyle="--", linewidth=1.2, label=f"Overall ({acc*100:.1f}%)")
ax.set_xlabel("Error Type", fontsize=12)
ax.set_ylabel("Accuracy (%)", fontsize=12)
ax.set_title("Per-Error-Type Accuracy � 18 Categories", fontsize=14, fontweight="bold")
ax.set_ylim(0, 110)
plt.xticks(rotation=45, ha="right", fontsize=9)
ax.legend(fontsize=10)
for bar, val in zip(bars, pe_vals):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f"{val:.0f}%", ha="center", va="bottom", fontsize=7.5)
plt.tight_layout()
path2 = os.path.join(RESULTS, "02_per_error_accuracy.png")
plt.savefig(path2, dpi=150, bbox_inches="tight")
plt.close()
print(f"  [OK] Saved: {path2}")

# -- 6. Plot 3: Language-wise Accuracy ----------------------------------------
if "language" in df.columns:
    lang_acc = (
        df.groupby("language")
          .apply(lambda x: accuracy_score(x["error_type"], x["predicted_error"]) * 100)
          .sort_values(ascending=False)
    )
    lang_vals = np.asarray(lang_acc.values, dtype=float)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336"]
    bars = ax.bar(lang_acc.index.tolist(), lang_vals,
                  color=colors[:len(lang_acc)], width=0.5)
    ax.axhline(float(acc * 100), color="navy", linestyle="--", linewidth=1.2, label=f"Overall ({acc*100:.1f}%)")
    ax.set_xlabel("Programming Language", fontsize=12)
    ax.set_ylabel("Accuracy (%)", fontsize=12)
    ax.set_title("Language-wise Accuracy � 5 Languages", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 110)
    ax.legend(fontsize=10)
    for bar, val in zip(bars, lang_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")
    plt.tight_layout()
    path3 = os.path.join(RESULTS, "03_language_accuracy.png")
    plt.savefig(path3, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [OK] Saved: {path3}")
    print(f"\n  Language Accuracy:")
    for lang, a in lang_acc.items():
        print(f"    {lang:12s}: {a:.2f}%")

# -- 7. Plot 4: Rule-Based vs ML Pie ------------------------------------------
rule_based = {"MissingColon", "IndentationError", "UnmatchedBracket",
              "UnclosedString", "MissingDelimiter"}
df["source"] = df["error_type"].apply(
    lambda e: "Rule-Based" if e in rule_based else "ML-Based"
)
source_counts = df["source"].value_counts()
fig, ax = plt.subplots(figsize=(6, 6))
pie_result = ax.pie(
    np.asarray(source_counts.values, dtype=float),
    labels=source_counts.index.astype(str).tolist(),
    autopct="%1.1f%%",
    startangle=90,
    colors=["#42A5F5", "#EF5350"],
    shadow=True
)
autotexts = pie_result[2] if len(pie_result) > 2 else []
for t in autotexts:
    t.set_fontsize(12)
    t.set_fontweight("bold")
ax.set_title("Rule-Based vs ML-Based Detection\nDistribution by Error Category", fontsize=13, fontweight="bold")
plt.tight_layout()
path4 = os.path.join(RESULTS, "04_detection_source_pie.png")
plt.savefig(path4, dpi=150, bbox_inches="tight")
plt.close()
print(f"  [OK] Saved: {path4}")

# -- 8. Plot 5: Per-class F1 Scores -------------------------------------------
report_dict = cast(dict[str, Any], classification_report(y_true, y_pred, zero_division=0, output_dict=True))
f1_scores = {
    k: float(v.get("f1-score", 0.0))
    for k, v in report_dict.items()
    if k not in ("accuracy", "macro avg", "weighted avg") and isinstance(v, dict)
}
f1_series = pd.Series(f1_scores).sort_values(ascending=True)
f1_vals = np.asarray(f1_series.values, dtype=float)
fig, ax = plt.subplots(figsize=(8, 10))
colors_f1 = [plt.get_cmap("RdYlGn")(float(v)) for v in f1_vals]
ax.barh(f1_series.index.tolist(), f1_vals * 100.0, color=colors_f1)
ax.axvline(float(f1 * 100), color="navy", linestyle="--", linewidth=1.2, label=f"Weighted F1 ({f1*100:.1f}%)")
ax.set_xlabel("F1-Score (%)", fontsize=12)
ax.set_title("Per-Class F1-Scores � 18 Error Types", fontsize=14, fontweight="bold")
ax.set_xlim(0, 115)
ax.legend(fontsize=10)
for i, v in enumerate(f1_vals):
    ax.text(v * 100 + 1, i, f"{v*100:.1f}%", va="center", fontsize=8.5)
plt.tight_layout()
path5 = os.path.join(RESULTS, "05_class_f1_scores.png")
plt.savefig(path5, dpi=150, bbox_inches="tight")
plt.close()
print(f"  [OK] Saved: {path5}")

# -- 9. Summary ---------------------------------------------------------------
print("\n" + "=" * 70)
print("  SUMMARY")
print("=" * 70)
print(f"  Model            : Gradient Boosting (100 estimators)")
print(f"  Languages        : Python, Java, C, C++, JavaScript (5)")
print(f"  Error Types      : 18 categories")
print(f"  Dataset Size     : {len(df):,} samples")
print(f"  Overall Accuracy : {acc*100:.2f}%")
print(f"  Weighted F1      : {f1*100:.2f}%")
print(f"  Output Dir       : {RESULTS}")
print(f"  Charts Saved     : 5 charts (01_�05_*.png)")
print("=" * 70)
