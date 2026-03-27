# Project Structure

This file is a high-level map of the OmniSyntax repository.

## Top-level layout
- `src/`: shared detection, analysis, and orchestration logic
- `tests/`: regression and behavior tests
- `docs/`: user and contributor documentation
- `scripts/`: evaluation, QA, and maintenance utilities
- `models/`: model bundle metadata and related assets
- `artifacts/`: generated evaluation and QA outputs
- `dataset/`: active, merged, and archived datasets
- `results/`: result snapshots and summaries

## Key runtime entry points
- `api.py`: FastAPI app surface
- `start_api.py`: API launcher
- `app.py`: Streamlit app
- `cli.py`: command-line runner

## Core engine modules
- `src/error_engine.py`: central detection orchestration
- `src/multi_error_detector.py`: multi-error detection flow
- `src/syntax_checker.py`: syntax checks
- `src/quality_analyzer.py`: quality checks
- `src/ml_engine.py`: ML route integration and compatibility handling
- `src/language_detector.py`: language detection helpers

## CI/quality controls
- `.github/workflows/ci.yml`: test and docs-link validation
- `scripts/check_links.py`: local markdown link validator used by CI
