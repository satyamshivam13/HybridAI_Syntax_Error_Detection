# Quick Start

## 1) Setup
Requires **Python 3.11 or 3.12** (`numpy<2.0` has no 3.13 wheels; models need `scikit-learn==1.7.2`).
```powershell
py -3.11 -m venv .venv          # macOS/Linux: python3.11 -m venv .venv
.venv\Scripts\Activate.ps1      # macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2) Run interfaces
```bash
# API
python start_api.py

# Web
python -m streamlit run app.py

# CLI
python cli.py tests/Test.java
```

## 3) Run tests
```bash
python -m pytest tests/ -v -p no:cacheprovider
python scripts/check_links.py
```

## 4) Script smoke checks
```bash
python scripts/test_accuracy.py --samples 100 --skip-pipeline
python scripts/test_false_positives.py --lang Python
python scripts/generate_results.py --smoke
python scripts/advanced_metrics.py --smoke
```

## 5) Retraining and dataset utilities
```bash
python scripts/augment_dataset.py --preview
python scripts/retrain_model.py --preview
```

## Notes
- `samples/` may be empty in some repository snapshots.
- If `/health` reports `degraded`, install a compatible sklearn runtime and restart.
