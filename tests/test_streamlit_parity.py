from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def _run_app(code: str, show_all_errors: bool = False):
    app = AppTest.from_file(str(ROOT / "app.py"))
    app.run(timeout=20)
    app.text_area[0].set_value(code)
    if show_all_errors:
        app.checkbox[0].set_value(True)
    app.run(timeout=20)
    return app


def test_streamlit_parity_for_c_java_js_cases():
    cases = [
        (
            "#include <stdio.h>\nint main() {\n    int a = 10\n    printf(\"%d\", a);\n    return 0;\n}\n",
            "C",
            "MissingDelimiter",
            "[ERROR] 003:     int a = 10",
        ),
        (
            "public class Test {\n    public static void main(String[] args) {\n        System.out.println(\"hello\");\n        // missing closing brace\n}\n",
            "Java",
            "UnmatchedBracket",
            "[ERROR] 001: public class Test {",
        ),
        (
            "function test() {\n    console.log(x);\n}\n",
            "JavaScript",
            "UndeclaredIdentifier",
            "[ERROR] 002:     console.log(x);",
        ),
    ]

    for code, expected_language, expected_error, highlight_fragment in cases:
        app = _run_app(code)

        assert any(
            f"Detected Language: **{expected_language}**" in item.value
            for item in app.success
        )
        assert any(
            f"Detected Error Type: **{expected_error}**" in item.value
            for item in app.error
        )
        assert any("Line" in item.value for item in app.error)
        assert not app.warning

        highlighted_block = next(item.value for item in app.markdown if "[ERROR]" in item.value)
        assert highlight_fragment in highlighted_block


def test_streamlit_degraded_mode_shows_warning_banner():
    code = "int main() {\n    return 0;\n}\n"

    with patch("src.error_engine.is_model_available", return_value=False), patch(
        "src.error_engine.get_model_status", return_value={"error": "forced-unavailable"}
    ):
        app = _run_app(code)

    assert any("Runtime warnings" in item.value for item in app.warning)
    assert any("forced-unavailable" in item.value for item in app.warning)
    assert any(
        "Semantic classification is limited in degraded mode" in item.value
        for item in app.info
    )
    assert any("No syntax errors detected" in item.value for item in app.success)



def test_streamlit_all_errors_mode_displays_grouped_results():
    fake_result = {
        "language": "Python",
        "errors": [
            {"type": "MissingColon", "count": 1, "locations": [{"line": 1, "message": "Missing colon", "snippet": "def broken()"}], "tutor": {"why": "", "fix": ""}},
            {"type": "DivisionByZero", "count": 1, "locations": [{"line": 2, "message": "Division by zero", "snippet": "    return 10 / 0"}], "tutor": {"why": "", "fix": ""}},
        ],
        "errors_by_type": {
            "MissingColon": [{"line": 1, "message": "Missing colon", "snippet": "def broken()"}],
            "DivisionByZero": [{"line": 2, "message": "Division by zero", "snippet": "    return 10 / 0"}],
        },
        "total_errors": 2,
        "has_errors": True,
        "rule_based_issues": [],
        "degraded_mode": False,
        "warnings": [],
    }

    with patch("src.multi_error_detector.detect_all_errors", return_value=fake_result):
        app = _run_app("def broken()\n    return 10 / 0\n", show_all_errors=True)

    assert any("Detected Language: **Python**" in item.value for item in app.success)
    assert any("Found **2 errors** across **2 types**" in item.value for item in app.error)
    assert len(app.error) >= 3
