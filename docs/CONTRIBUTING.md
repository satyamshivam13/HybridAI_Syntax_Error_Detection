# Contributing

## Development setup
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
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
