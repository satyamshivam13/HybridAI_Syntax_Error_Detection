# OmniSyntax

Hybrid syntax and code-quality assistant for Python, Java, C, C++, and JavaScript.

## Current state
- Core unit tests pass locally (`pytest tests/ -v`).
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
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

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
python -m pytest tests/ -v -p no:cacheprovider
python scripts/test_accuracy.py --samples 100 --skip-pipeline
python scripts/test_false_positives.py --lang Python
python scripts/generate_results.py --smoke
python scripts/advanced_metrics.py --smoke
python scripts/check_links.py
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

## Notes on sample inputs
The `samples/` directory may be empty in some snapshots. Use `tests/Test.java` or your own snippets with `cli.py`.



