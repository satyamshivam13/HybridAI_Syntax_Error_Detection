# Contributing

## Development setup
Requires **Python 3.11 or 3.12** (`numpy<2.0` has no 3.13 wheels; models need `scikit-learn==1.7.2`).
Use `.venv` only — a virtualenv is not relocatable, so if a Python upgrade breaks it,
delete and recreate rather than editing it.
```powershell
py -3.11 -m venv .venv          # macOS/Linux: python3.11 -m venv .venv
.venv\Scripts\Activate.ps1      # macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Before opening a PR
```bash
pytest tests/ -v -p no:cacheprovider
python scripts/check_links.py
python scripts/test_accuracy.py --samples 100 --skip-pipeline
```

## Code standards
- Keep behavior changes covered by tests.
- Prefer explicit errors over silent fallbacks.
- Keep API contracts backward compatible when feasible.
- Update docs for any command, path, or response-shape change.

## Typical workflows
```bash
# Retrain model
python scripts/retrain_model.py --compare

# Regenerate metrics
python scripts/advanced_metrics.py

# Generate prediction file
python scripts/generate_results.py
```

## Notes
- `samples/` can be empty in some snapshots; use `tests/Test.java` or custom snippets for manual checks.
