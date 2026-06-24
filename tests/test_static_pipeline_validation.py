from __future__ import annotations

import ast

from scripts.production_validation import run
from src.auto_fix import AutoFixer
from src.error_engine import detect_errors
from src.static_pipeline import ExpressionEvaluator, SymbolTable, analyze_source


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


def test_mixed_type_loop_condition_detects_type_mismatch():
    # A String compared with an int in a loop condition used to (a) crash the CFG
    # loop analysis and later (b) return NoError. It must now report TypeMismatch.
    code = 'String input = "10";\nwhile (input > 0) { input--; }'

    result = detect_errors(code, "A.java")

    assert isinstance(result, dict)
    assert result["language"] == "Java"
    assert result["degraded_mode"] is False
    assert result["predicted_error"] == "TypeMismatch"
    assert any(i.get("type") == "TypeMismatch" for i in result["rule_based_issues"])


def test_string_numeric_use_site_type_mismatch_variants():
    flagged = [
        'public class T { void m(){ String s = "3"; if (s < 5) {} } }',     # relational
        'public class T { void m(){ String s = "3"; if (0 < s) {} } }',     # literal on left
        'public class T { void m(){ String s = "3"; int y = s - 1; } }',    # arithmetic
    ]
    for code in flagged:
        res = detect_errors(code, "T.java")
        assert res["predicted_error"] == "TypeMismatch", code


def test_string_numeric_detector_avoids_false_positives():
    clean = [
        'public class T { void m(){ String s = "3"; String r = s + 1; } }',       # concatenation
        'public class T { void m(){ String s = "3"; if (s.length() > 0) {} } }',  # method call, int result
        'public class T { void m(){ String a = "x"; String b = "y"; if (a == b) {} } }',  # String compare
        'public class T { void m(){ String input = "input > 0"; } }',            # pattern only inside a literal
        'public class T { void m(){ int i = 5; if (i > 0) {} } }',               # genuinely numeric variable
    ]
    for code in clean:
        res = detect_errors(code, "T.java")
        issues = res["rule_based_issues"]
        assert not any(i.get("type") == "TypeMismatch" for i in issues), code


def test_expression_evaluator_guards_unorderable_operands():
    evaluator = ExpressionEvaluator()
    symbols = SymbolTable("Java")

    # str-vs-int ordering is not statically decidable -> UNKNOWN, never a raise.
    fact = evaluator.evaluate('"10" > 0', symbols)
    assert fact.state.name == "UNKNOWN"

    # Direct contract: ordering ops on unorderable operands return None (the sentinel),
    # while equality stays decidable and numeric ordering still folds.
    assert evaluator._compare("10", 0, ast.Gt()) is None
    assert evaluator._compare("10", 0, ast.Eq()) is False
    assert evaluator._compare(3, 1, ast.Gt()) is True
