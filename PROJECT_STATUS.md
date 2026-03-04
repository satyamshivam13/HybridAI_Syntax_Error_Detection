# Project Status

Last updated: 2026-03-04

## Summary
- Runtime hardening completed for model-unavailable behavior.
- API contract hardening completed for payload limits, structured errors, and rate limiting.
- Regression and integration tests expanded (API, scripts, and core edge cases).
- Documentation reconciled with current repository contents.

## Verified locally
- `pytest tests/ -v -p no:cacheprovider` passes.
- Script smoke tests run under UTF-8 and cp1252 console settings.
- Link checker validates markdown references.

## Known release blocker
- The bundled model artifacts in `models/*.pkl` require scikit-learn 1.1.x compatibility.
- If runtime uses an incompatible sklearn version, health reports `degraded` and ML semantics are skipped.

## Next operational step
- In release environments, install dependencies from `requirements.txt` exactly and verify `/health` returns `healthy`.
