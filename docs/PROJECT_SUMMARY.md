# Project Summary

OmniSyntax is a hybrid analysis project for beginner-focused code diagnostics.

## Components
- Rule-based syntax analysis (`src/syntax_checker.py`, `src/error_engine.py`)
- ML-backed classification (`src/ml_engine.py`)
- Auto-fix engine (`src/auto_fix.py`)
- Code quality analyzer (`src/quality_analyzer.py`)
- Interfaces:
  - FastAPI (`api.py`)
  - Streamlit (`app.py`)
  - CLI (`cli.py`)

## Hardening updates (March 2026)
- Model-unavailable behavior is explicit through API degraded metadata.
- API input limits are consistent across `/check`, `/fix`, and `/quality`.
- Structured error responses now use `error_code` and `message`.
- In-memory request rate limiting is active.
- Language override is supported on `/check` and `/check-and-fix`.

## Operational caveat
- Pretrained artifacts in `models/` require compatible sklearn serialization runtime.
- Use `/health` to verify that ML is loaded before depending on semantic classifications.
