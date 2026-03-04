import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def _run(command: list[str], encoding: str = "utf-8", timeout: int = 180):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = encoding
    env["PYTHONUTF8"] = "0"
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
