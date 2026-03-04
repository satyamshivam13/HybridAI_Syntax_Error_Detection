# Paper Abstract (Draft)

## Title
Hybrid Rule-Based and ML-Assisted Multi-Language Syntax Diagnostics for Programming Education

## Abstract
This work presents OmniSyntax, a hybrid educational code-analysis system that combines deterministic syntax checks with ML-assisted error classification. The platform exposes API, CLI, and web interfaces and targets Python, Java, C, C++, and JavaScript workflows. Recent hardening work focuses on production safety: explicit degraded-mode behavior when ML artifacts are unavailable, consistent API payload limits, structured error contracts, and expanded regression testing across runtime, API, and script surfaces. The implementation demonstrates a practical pattern for educational tools that must remain usable under partial dependency failure while preserving contract clarity and testability.

## Implementation references
- Core engine: `src/error_engine.py`
- ML runtime: `src/ml_engine.py`
- API contract: `api.py`
- Tests: `tests/`
