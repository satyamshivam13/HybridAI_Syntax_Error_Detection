# Comprehensive Test Report

Last updated: 2026-03-27

Latest verified local run (`pytest tests/ -v -p no:cacheprovider`): 87 passed, 1 xfailed (see test results for full details).

## Scope
- Unit tests (`tests/test_detection.py`)
- API and regression tests (`tests/test_api_and_regressions.py`)
- Script smoke tests (`tests/test_script_smoke.py`)
- Markdown link validation (`scripts/check_links.py`)

## Current quality gates
1. `pytest tests/ -v -p no:cacheprovider`
2. `python scripts/check_links.py`

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
