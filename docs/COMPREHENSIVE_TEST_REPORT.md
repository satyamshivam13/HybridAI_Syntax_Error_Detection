# Comprehensive Test Report

Last updated: 2026-04-11

Latest verified local run (`python -m pytest tests/ -q`): 179 passed, 1 skipped, 1 xfailed.

Latest validation gates:
- `python scripts/production_validation.py` => mutation_robustness 1.0, real_world_messy_accuracy 1.0, multi_error_recall 1.0, cross_language_consistency 1.0, confidence_ece 0.0391.
- `python scripts/adversarial_validation.py` => mutation_accuracy 97.08, real_world_accuracy 97.3, confidence_reliability 9.9, verdict PRODUCTION_READY.

## Scope
- Unit tests (`tests/test_detection.py`)
- API and regression tests (`tests/test_api_and_regressions.py`)
- Script smoke tests (`tests/test_script_smoke.py`)
- Markdown link validation (`scripts/check_links.py`)

## Current quality gates
1. `python -m pytest tests/ -q`
2. `python scripts/check_links.py`
3. `python scripts/production_validation.py`
4. `python scripts/adversarial_validation.py`

## Key regressions now covered
- Model-unavailable path is explicit (no silent ML fallback).
- Complexity baseline (`x=1`) remains deterministic.
- Multi-error detector ignores bracket-like characters inside valid strings.
- Auto-fix does not append colons based on string literals.
- API payload limit parity across `/check`, `/fix`, and `/quality`.
- API rate-limit path returns `429`.
- API health shows `degraded` when ML is unavailable.
- Script execution under UTF-8 and cp1252 environments.

## Release note
Model availability remains environment-dependent; `/health` must be checked in deployment before marking a release as production-ready.
