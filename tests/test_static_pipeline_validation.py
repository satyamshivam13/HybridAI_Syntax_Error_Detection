from __future__ import annotations

from scripts.production_validation import run
from src.auto_fix import AutoFixer
from src.error_engine import detect_errors
from src.static_pipeline import analyze_source


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


def test_python_live_tutor_sample_reports_multiple_localized_issues():
    code = '''def calculate():
    numbers = [1, 2 3, 4]  # MissingDelimiter

    if len(numbers) > 3   # MissingColon
        print("Valid list")

    total = 0
    for i in numbers:
    total += i  # IndentationError

    text = "This is a broken string  # UnclosedString

    print(math.sqrt(total))  # MissingImport

    if (total > 10:  # UnmatchedBracket
        print("Large")'''

    grouped = analyze_source(code, language_override="Python").to_grouped_result()
    by_type = grouped["errors_by_type"]

    assert grouped["total_errors"] >= 6
    assert set(by_type) >= {
        "MissingDelimiter",
        "IndentationError",
        "UnclosedString",
        "MissingImport",
        "UnmatchedBracket",
    }
    assert {issue["line"] for issue in by_type["MissingDelimiter"]} >= {2, 4}
    assert by_type["IndentationError"][0]["line"] == 9
    assert by_type["MissingImport"][0]["line"] == 13


def test_python_live_tutor_sample_has_patch_preview():
    code = '''def calculate():
    numbers = [1, 2 3, 4]  # MissingDelimiter

    if len(numbers) > 3   # MissingColon
        print("Valid list")

    total = 0
    for i in numbers:
    total += i  # IndentationError

    text = "This is a broken string  # UnclosedString

    print(math.sqrt(total))  # MissingImport

    if (total > 10:  # UnmatchedBracket
        print("Large")'''

    issues = analyze_source(code, language_override="Python").to_single_result()["rule_based_issues"]
    preview = AutoFixer.format_patch_preview(AutoFixer.patch_preview(code, issues, "Python"))

    assert "Line 1 + import math" in preview
    assert any("Line 2 ->     numbers = [1, 2, 3, 4]" in line for line in preview)
    assert any("Line 4 ->     if len(numbers) > 3:" in line for line in preview)
    assert any("Line 9 ->         total += i" in line for line in preview)
    assert any('Line 11 ->     text = "This is a broken string"' in line for line in preview)


def test_suggestion_only_fix_targets_primary_issue_line():
    code = '''def calculate():
    numbers = [1, 2 3, 4]

    text = "This is a broken string
'''
    result = analyze_source(code, language_override="Python").to_single_result()
    line_num = AutoFixer.line_for_error(result["rule_based_issues"], result["predicted_error"])

    fix_result = AutoFixer().apply_fixes(code, result["predicted_error"], line_num, result["language"])

    assert result["predicted_error"] == "UnclosedString"
    assert fix_result["success"] is False
    assert fix_result["fixed_code"] == code
    assert any("line 4" in change for change in fix_result["changes"])
