import importlib
import os
import sys

import pytest
from fastapi.testclient import TestClient

from src.auto_fix import AutoFixer
from src.ml_engine import ModelUnavailableError, detect_error_ml, model_loaded
from src.multi_error_detector import detect_all_errors
from src.quality_analyzer import CodeQualityAnalyzer


def _load_api(monkeypatch: pytest.MonkeyPatch, rate_limit: str = "100"):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", rate_limit)
    monkeypatch.setenv("MAX_CODE_SIZE", "100000")
    if "api" in sys.modules:
        del sys.modules["api"]
    import api

    return importlib.reload(api)


def test_model_unavailable_is_explicit():
    if model_loaded:
        pytest.skip("Model is available in this environment")
    with pytest.raises(ModelUnavailableError):
        detect_error_ml("x = 1")


def test_quality_complexity_baseline():
    analyzer = CodeQualityAnalyzer("x=1", "python")
    assert analyzer.calculate_complexity() == 1


def test_multi_error_ignores_brackets_inside_strings():
    result = detect_all_errors("print(')')", "a.py")
    assert result["has_errors"] is False
    assert result["total_errors"] == 0


def test_autofix_missing_colon_does_not_mutate_literals():
    fixer = AutoFixer()
    original = "print('if this works')"
    result = fixer.apply_fixes(original, "MissingColon", 0, "Python")
    assert result["success"] is False
    assert result["fixed_code"] == original


def test_autofix_semicolon_line_targeting():
    fixer = AutoFixer()
    original = "int a = 1\nint b = 2"
    result = fixer.apply_fixes(original, "MissingSemicolon", 0, "Java")
    assert result["success"] is True
    assert result["fixed_code"].splitlines()[0].endswith(";")
    assert not result["fixed_code"].splitlines()[1].endswith(";")


def test_health_reflects_model_state(monkeypatch: pytest.MonkeyPatch):
    api = _load_api(monkeypatch, rate_limit="100")
    client = TestClient(api.app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert "JavaScript" in payload["supported_languages"]
    if payload["ml_model_loaded"]:
        assert payload["status"] == "healthy"
    else:
        assert payload["status"] == "degraded"
        assert payload.get("degraded_reason")


def test_language_override_is_honored(monkeypatch: pytest.MonkeyPatch):
    api = _load_api(monkeypatch, rate_limit="100")
    client = TestClient(api.app)
    response = client.post(
        "/check",
        json={"code": "console.log(1);", "filename": "x.py", "language": "JavaScript"},
    )
    assert response.status_code == 200
    assert response.json()["language"] == "JavaScript"


@pytest.mark.parametrize("endpoint,payload_builder", [
    ("/check", lambda code: {"code": code, "filename": "x.py"}),
    ("/fix", lambda code: {"code": code, "error_type": "MissingColon", "language": "Python", "line_num": 0}),
    ("/quality", lambda code: {"code": code, "language": "python"}),
])
def test_payload_limit_parity(monkeypatch: pytest.MonkeyPatch, endpoint, payload_builder):
    api = _load_api(monkeypatch, rate_limit="100")
    client = TestClient(api.app)
    exact = "a" * 100000
    over = "a" * 100001

    ok_resp = client.post(endpoint, json=payload_builder(exact))
    assert ok_resp.status_code != 413

    over_resp = client.post(endpoint, json=payload_builder(over))
    assert over_resp.status_code == 413
    detail = over_resp.json()["detail"]
    assert detail["error_code"] == "PAYLOAD_TOO_LARGE"


def test_rate_limit_returns_429(monkeypatch: pytest.MonkeyPatch):
    api = _load_api(monkeypatch, rate_limit="3")
    client = TestClient(api.app)
    statuses = []
    for _ in range(4):
        response = client.post("/check", json={"code": "x=1", "filename": "x.py"})
        statuses.append(response.status_code)
    assert statuses[-1] == 429
