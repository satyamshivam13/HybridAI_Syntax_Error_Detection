# OmniSyntax — Hybrid Syntax Error Detection

> **94.18% accuracy · Cohen's κ 0.79 · ~1ms median inference · Python · Java · C · C++ · JS · FastAPI + CLI + Streamlit**

[![Accuracy](https://img.shields.io/badge/Accuracy-94.18%25-brightgreen)](artifacts/accuracy_final/metrics_overall_available.csv)
[![Cohen's Kappa](https://img.shields.io/badge/Cohen's_%CE%BA-0.79-green)](#metrics-verified)
[![Latency](https://img.shields.io/badge/Inference-~1ms_median-009688)](#metrics-verified)
[![Languages](https://img.shields.io/badge/Languages-Py_Java_C_C%2B%2B_JS-informational)]()
[![Tests](https://img.shields.io/badge/Tests-193_passed-success)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Hybrid syntax and code-quality assistant for Python, Java, C, C++, and JavaScript.
It pairs deterministic rule-based checks with an ML-assisted classifier (TF-IDF +
gradient boosting) and degrades gracefully to rule-based analysis when ML models
are unavailable.

<a id="metrics-verified"></a>
### Metrics (verified)
Measured on this repository's own evaluation artifacts and engine — not estimates.

| Metric | Value | How it was measured |
|---|---|---|
| Overall accuracy | **94.18%** | 61,580-sample exhaustive corpus ([`metrics_overall_available.csv`](artifacts/accuracy_final/metrics_overall_available.csv)) |
| Cohen's Kappa | **0.79** | Computed from [`predictions_available.csv`](artifacts/accuracy_final/predictions_available.csv) (expected vs. predicted label) |
| Per-language accuracy | C 94.4% · C++ 91.7% · Java 94.2% · JS 97.1% · Py 93.6% | [`per_language_metrics_available.csv`](artifacts/accuracy_final/per_language_metrics_available.csv) |
| Inference latency | **0.99 ms median, 1.46 ms mean, 4.06 ms p95** | 999 real corpus files, all 5 languages, healthy mode (sklearn 1.7.2) |
| NoError false-positive rate | 0.0% | quality gates ([`quality_gates_available.json`](artifacts/accuracy_final/quality_gates_available.json)) |

**Honest caveats:** the project's own release gate reports `NO-GO` because the
critical label `MissingDelimiter` has 0.82 recall (below the 0.95 threshold), so
this is a strong research prototype rather than a production-certified release. A
small fraction of inputs (~0.1% in the latency sample) can still raise an
unhandled exception in the static evaluator. Reproduce all numbers with
`python scripts/evaluate_exhaustive_accuracy.py`.

A working draft of the accompanying paper is in [`docs/PAPER_ABSTRACT.md`](docs/PAPER_ABSTRACT.md) (not yet submitted to a venue).

## Current state
- Latest local verification (2026-05-02): `python -m pytest tests/ -q` => 193 passed, 1 skipped, 1 xfailed.
- API, CLI, and Streamlit entrypoints are available.
- ML-backed classification is enabled with metadata-aware model compatibility control.
- System reports degraded mode explicitly when ML models cannot load or are incompatible.
- Graceful degradation: all entry points continue to provide rule-based analysis in degraded mode.

## Repository layout
- `src/`: core detection, auto-fix, quality, and language modules.
- `api.py`: FastAPI server.
- `app.py`: Streamlit UI.
- `cli.py`: command-line interface.
- `scripts/`: training, evaluation, and maintenance scripts.
- `tests/`: automated tests.
- `docs/`: project and API documentation.

## Setup

**Requires Python 3.11 or 3.12.** `requirements.txt` pins `numpy<2.0`, which has
no wheels for Python 3.13 — installing under 3.13 will fail. The serialized models
also expect `scikit-learn==1.7.2`. Create the environment with an explicit version
so you don't accidentally pick up 3.13:

```powershell
# Windows (PowerShell) — use the launcher to pin the version
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

```bash
# macOS / Linux
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verify the environment is healthy (ML models load):

```bash
python -c "import src.ml_engine as m; print(m.get_model_status()['loaded'])"   # -> True
```

> If `.venv` ever stops working after a Python upgrade/uninstall, a virtualenv is
> **not** relocatable — its `pyvenv.cfg` hard-codes the base interpreter path.
> Delete and recreate it: `rm -rf .venv` (PowerShell: `Remove-Item -Recurse -Force .venv`)
> then repeat the steps above. Use `.venv` only — older `.venvNNN` directories are not used.

## Run

### Healthy mode (with ML model)
When the environment is compatible with `scikit-learn==1.7.2` and model artifacts are present:

```bash
# API (healthy mode)
python start_api.py
# Expect: FastAPI server starts on http://localhost:8000/health showing "healthy": true

# Web UI (healthy mode)
python -m streamlit run app.py
# Expect: Streamlit interface loads with ML-assisted classification active

# CLI (healthy mode)
python cli.py tests/Test.java
# Expect: Structured output with "Detected X issue(s)" plus optional ML classification labels
```

### Degraded mode (fallback, rule-based only)
If ML models are unavailable or incompatible:

```bash
# API (degraded mode)
python start_api.py
# Expect: /health endpoint shows "healthy": false with error message
# /check responses include "degraded_mode": true and warnings

# Web UI (degraded mode)
python -m streamlit run app.py
# Expect: Interface displays warnings but continues using rule-based detection

# CLI (degraded mode)
python cli.py tests/Test.java
# Expect: Output includes "degraded" warning but still returns Detected issue(s)
```

## Test

### Smoke / Startup verification
```bash
python -m pytest tests/test_script_smoke.py -q
# Verifies: API import, Streamlit import, CLI execution, graceful degradation signals
```

### Full test suite
```bash
python -m pytest tests/ -q
python scripts/production_validation.py
python scripts/adversarial_validation.py
python scripts/check_links.py
```

### Optional evaluation scripts
```bash
python scripts/test_accuracy.py --samples 100 --skip-pipeline
python scripts/test_false_positives.py --lang Python
python scripts/generate_results.py --smoke
python scripts/advanced_metrics.py --smoke
```

## Model compatibility
The active model bundle is metadata-aware via `models/bundle_metadata.json` and currently targets scikit-learn 1.7.x.
`requirements.txt` is pinned to match the current bundle contract. If your environment becomes incompatible:
- `/health` reports `"healthy": false` with descriptive error message.
- `/check` responses include `degraded_mode: true` and explanatory warnings.
- Semantic ML classification is skipped safely while rule-based checks continue.

## API notes
- `POST /check` and `POST /check-and-fix` support `language` override.
- `POST /check`, `POST /fix`, `POST /quality` enforce the same payload limit.
- Error responses use structured `detail`:
  - `error_code`
  - `message`

## Documentation
- [Quick Start](docs/QUICKSTART.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Project Summary](docs/PROJECT_SUMMARY.md)
- [Comprehensive Test Report](docs/COMPREHENSIVE_TEST_REPORT.md)
- [Paper Abstract](docs/PAPER_ABSTRACT.md)
- [Project Structure](PROJECT_STRUCTURE.md)
- [Project Status](PROJECT_STATUS.md)

Documentation maintenance note:
- `python scripts/check_links.py` runs in CI and validates local markdown links.
- Keep these linked files present and update links if files are moved or renamed.

## Notes on sample inputs
The [`samples/`](samples/) directory contains ready-to-run examples for Python, Java, C, and C++ —
one clean file plus several that each trigger a specific detector. Every sample's expected
output is verified against the engine and documented in [`samples/README.md`](samples/README.md).

```bash
python cli.py samples/java/TypeMismatch.java      # -> Detected: TypeMismatch (Line 3)
python cli.py samples/python/valid.py             # -> No syntax errors
```



