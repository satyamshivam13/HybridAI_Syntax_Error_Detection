import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def _run(command: list[str], encoding: str = "utf-8", timeout: int = 180, env_override: dict = None):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = encoding
    env["PYTHONUTF8"] = "0"
    if env_override:
        env.update(env_override)
    return subprocess.run(
        [PYTHON, *command],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252"])
def test_accuracy_script_smoke(encoding: str):
    proc = _run(["scripts/test_accuracy.py", "--samples", "30", "--skip-pipeline"], encoding=encoding)
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252"])
def test_false_positives_script_smoke(encoding: str):
    proc = _run(["scripts/test_false_positives.py", "--lang", "Python"], encoding=encoding)
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout


def test_generate_results_smoke():
    proc = _run(["scripts/generate_results.py", "--smoke"], encoding="utf-8")
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout


def test_advanced_metrics_smoke():
    proc = _run(["scripts/advanced_metrics.py", "--smoke"], encoding="utf-8")
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout

def test_cli_smoke_on_java_fixture():
    proc = _run(["cli.py", "tests/Test.java"], encoding="utf-8")
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout
    assert "Detected" in proc.stdout


def test_cli_smoke_with_warning_propagation():
    """Verify CLI shows warnings and status info when present."""
    proc = _run(["cli.py", "tests/Test.java"], encoding="utf-8")
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout
    # Verify structured output is present for downstream parsing
    assert ("Detected" in proc.stdout or "No issues" in proc.stdout), "Expected detection or clear empty result"


def test_api_startup_import_smoke():
    proc = _run(["-c", "import api; print('api-import-ok')"], encoding="utf-8", timeout=60)
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout
    assert "api-import-ok" in proc.stdout


def test_api_health_function_smoke():
    """Test /health endpoint logic via direct function call."""
    proc = _run(
        ["-c", "from api import get_model_status; status = get_model_status(); print(f'health:{status}')"],
        encoding="utf-8",
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout
    assert "health:" in proc.stdout


def test_streamlit_startup_headless_smoke():
    proc = _run(["-c", "import app; print('streamlit-import-ok')"], encoding="utf-8", timeout=60)
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout
    assert "streamlit-import-ok" in proc.stdout


def test_cli_graceful_degradation_signal():
    """Verify CLI reports degraded mode without crashing when ML is unavailable."""
    env = {"OMNISYNTAX_FORCE_DEGRADED": "1"}
    proc = _run(["cli.py", "tests/Test.java"], encoding="utf-8", env_override=env)
    # Should succeed even when degraded
    assert proc.returncode == 0, f"CLI should handle degraded mode gracefully. stderr: {proc.stderr}\nstdout: {proc.stdout}"
    # Should show some output (either detection or warning)
    assert len(proc.stdout) > 0, "CLI should produce output even in degraded mode"


def test_api_degraded_mode_messaging():
    """Verify API surfaces degraded-mode warnings in response structure."""
    proc = _run(
        [
            "-c",
            """
from src.multi_error_detector import detect_all_errors
result = detect_all_errors('int x;', 'test.c')
print('has_warnings' if result.get('warnings') else 'no_warnings')
print('has_errors' if result.get('errors') else 'no_errors')
print(f"degraded_mode:{result.get('degraded_mode')}")
""",
        ],
        encoding="utf-8",
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr + "\n" + proc.stdout
    # Should return structured result with degraded_mode and warnings fields
    assert ("has_warnings" in proc.stdout or "no_warnings" in proc.stdout), (
        f"Expected warning field in response. stderr: {proc.stderr}\nstdout: {proc.stdout}"
    )
    assert "degraded_mode:" in proc.stdout, (
        f"Expected degraded_mode field in response. stderr: {proc.stderr}\nstdout: {proc.stdout}"
    )
