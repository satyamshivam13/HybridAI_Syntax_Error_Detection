# Technology Stack

**Analysis Date:** 2026-03-27

## Languages

**Primary:**
- Python 3.10 - All application code, scripts, tests, API, CLI, and Streamlit UI

**Secondary:**
- Markdown - Documentation and QA reports under `docs/`
- YAML - GitHub Actions workflow in `.github/workflows/ci.yml`

## Runtime

**Environment:**
- CPython 3.10 in CI and local virtual environments
- Local execution also assumes a browser for Streamlit and HTTP clients for FastAPI

**Package Manager:**
- `pip` with `requirements.txt` and `requirements-dev.txt`
- Lockfile: none committed

## Frameworks

**Core:**
- FastAPI - REST API in `api.py`
- Streamlit - Interactive UI in `app.py`
- scikit-learn 1.1.3 - Serialized model compatibility target in `src/ml_engine.py`

**Testing:**
- pytest - Unit, regression, and smoke tests under `tests/`
- httpx / FastAPI TestClient - API verification

**Build/Dev:**
- uvicorn - API server runtime
- python-dotenv - Environment loading from `.env` files

## Key Dependencies

**Critical:**
- `fastapi` - API routing, validation, and structured errors
- `streamlit` - Student-facing web UI
- `scikit-learn==1.1.3` - Required for current serialized ML artifacts
- `joblib` - Loading model artifacts from `models/`
- `pydantic` - API request and response models

**Infrastructure:**
- `pandas` and `numpy` - Feature extraction, evaluation, and dataset processing
- `uvicorn[standard]` - ASGI serving for the API
- `pytest-cov` - Coverage tooling for local verification

## Configuration

**Environment:**
- Configured through `.env` and `.env.template`
- Important variables: `API_HOST`, `API_PORT`, `PRODUCTION`, `MAX_CODE_SIZE`, `RATE_LIMIT_PER_MINUTE`, `CORS_ORIGINS`

**Build:**
- No separate build system; Python files run directly
- CI configuration lives in `.github/workflows/ci.yml`

## Platform Requirements

**Development:**
- Windows, macOS, or Linux with Python 3.10-compatible dependencies
- Virtual environment recommended

**Production:**
- ASGI-compatible Python runtime for the API
- Local filesystem access to `models/`, `dataset/`, `artifacts/`, and `results/`
- Compatibility with the serialized scikit-learn model bundle if ML mode is expected

---
*Stack analysis: 2026-03-27*
*Update after major dependency changes*
