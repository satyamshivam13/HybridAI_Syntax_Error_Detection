from __future__ import annotations

from scripts.production_validation import run
from src.error_engine import detect_errors


def test_confidence_outputs_are_calibrated_and_not_constant():
    payload = run()
    metrics = payload["metrics"]

    assert metrics["confidence_constant"] is False
    assert metrics["confidence_ece"] < 0.05


def test_static_pipeline_exposes_required_stage_names():
    result = detect_errors("def f():\n    return 1 / (2-2)\n", "x.py")

    assert result["analysis_pipeline"] == [
        "Parsing",
        "Symbol Table",
        "Expression Evaluation",
        "Control Flow",
        "Semantic Analysis",
        "Multi-Error Aggregation",
        "Ranking",
        "Confidence Calibration",
    ]
    assert result["confidence_model"]["constant_output"] is False
    assert "Zero" in result["confidence_model"]["value_states"]
