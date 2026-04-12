"""Generate thesis-ready figures from verified OmniSyntax evaluation artifacts.

This script reads the checked-in evaluation outputs under artifacts/accuracy_final
and writes publication-style PNG figures under docs/figures.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "accuracy_final"
FIGURES = ROOT / "docs" / "figures"

FIGURES.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="paper")
plt.rcParams.update(
    {
        "figure.dpi": 160,
        "savefig.dpi": 220,
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
    }
)


def _save(fig: plt.Figure, filename: str) -> None:
    path = FIGURES / filename
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {path.relative_to(ROOT)}")


def confusion_matrix_figure() -> None:
    cm = pd.read_csv(ARTIFACTS / "confusion_matrix_available.csv", index_col=0)
    fig, ax = plt.subplots(figsize=(14, 11))
    sns.heatmap(
        cm,
        cmap="Blues",
        annot=False,
        linewidths=0.25,
        linecolor="white",
        cbar_kws={"label": "Count"},
        ax=ax,
    )
    ax.set_title("Figure 1. Confusion Matrix for the Available Model")
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    _save(fig, "figure_1_confusion_matrix.png")


def per_label_performance_figure() -> None:
    metrics = pd.read_csv(ARTIFACTS / "per_label_metrics_available.csv")
    metrics = metrics[metrics["label"] != "SyntaxError"].copy()
    metrics = metrics.sort_values("f1", ascending=True)
    fig, ax = plt.subplots(figsize=(13, 9))
    x = range(len(metrics))
    width = 0.24
    ax.barh([i - width for i in x], metrics["precision"], height=width, label="Precision", color="#4C78A8")
    ax.barh(x, metrics["recall"], height=width, label="Recall", color="#F58518")
    ax.barh([i + width for i in x], metrics["f1"], height=width, label="F1-score", color="#54A24B")
    ax.set_yticks(list(x))
    ax.set_yticklabels(metrics["label"])
    ax.set_xlim(0, 1.05)
    ax.set_title("Figure 2. Per-label Precision, Recall, and F1-score")
    ax.set_xlabel("Score")
    ax.legend(loc="lower right")
    _save(fig, "figure_2_per_label_performance.png")


def per_language_accuracy_figure() -> None:
    language = pd.read_csv(ARTIFACTS / "per_language_metrics_available.csv").sort_values("accuracy")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(language["language"], language["accuracy"], color=["#72B7B2", "#4C78A8", "#F58518", "#E45756", "#54A24B"])
    ax.set_ylim(0, 1.05)
    ax.set_title("Figure 3. Per-language Accuracy")
    ax.set_ylabel("Accuracy")
    ax.set_xlabel("Language")
    for bar, value in zip(bars, language["accuracy"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.015, f"{value:.3f}", ha="center", va="bottom", fontsize=9)
    _save(fig, "figure_3_per_language_accuracy.png")


def model_comparison_figure() -> None:
    comparison = json.loads((ARTIFACTS / "model_availability_comparison.json").read_text(encoding="utf-8"))
    labels = ["Available model", "Forced unavailable"]
    values = [comparison["accuracy_available_subset"], comparison["accuracy_forced_unavailable_subset"]]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    bars = ax.bar(labels, values, color=["#54A24B", "#E45756"])
    ax.set_ylim(0, 1.05)
    ax.set_title("Figure 4. Model Availability Comparison on Shared Subset")
    ax.set_ylabel("Accuracy")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.4f}", ha="center", va="bottom")
    _save(fig, "figure_4_model_availability_comparison.png")


def overall_metrics_figure() -> None:
    overall = pd.read_csv(ARTIFACTS / "metrics_overall_available.csv")
    row = overall.iloc[0]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    labels = ["Overall accuracy", "NoError FPR"]
    values = [row["overall_accuracy"], row["noerror_false_positive_rate"]]
    bars = ax.bar(labels, values, color=["#4C78A8", "#F58518"])
    ax.set_ylim(0, max(values) * 1.25 if max(values) else 1.0)
    ax.set_title("Figure 5. Overall Runtime Evaluation Summary")
    ax.set_ylabel("Value")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + (0.01 if value else 0.001), f"{value:.4f}", ha="center", va="bottom")
    _save(fig, "figure_5_overall_metrics.png")


if __name__ == "__main__":
    confusion_matrix_figure()
    per_label_performance_figure()
    per_language_accuracy_figure()
    model_comparison_figure()
    overall_metrics_figure()
