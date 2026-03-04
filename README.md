# OmniSyntax

Hybrid syntax and code-quality assistant for Python, Java, C, C++, and JavaScript.

## Current state
- Core unit tests pass locally (`pytest tests/ -v`).
- API, CLI, and Streamlit entrypoints are available.
- ML-backed classification depends on serialized model compatibility.
- If models cannot load, the system now reports degraded mode explicitly.

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
```bash
# API
python start_api.py

# Web UI
python -m streamlit run app.py

# CLI
python cli.py path/to/file.py
```

## Test
```bash
python -m pytest tests/ -v -p no:cacheprovider
python scripts/test_accuracy.py --samples 100 --skip-pipeline
python scripts/test_false_positives.py --lang Python
python scripts/generate_results.py --smoke
python scripts/advanced_metrics.py --smoke
python scripts/check_links.py
```

## Model compatibility
Serialized models in `models/*.pkl` were trained with scikit-learn 1.1.x.
`requirements.txt` is pinned accordingly. If your environment is incompatible:
- `/health` reports `degraded`.
- `/check` responses include `degraded_mode` and warnings.
- semantic ML classification is skipped safely.

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
