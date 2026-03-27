# Architecture

**Analysis Date:** 2026-03-27

## Pattern Overview

**Overall:** Layered Python application with shared analysis core and three user-facing entry points

**Key Characteristics:**
- One detection engine is reused by API, CLI, and Streamlit
- Hybrid analysis combines structural rules, rule-based heuristics, and optional ML classification
- Runtime is mostly stateless per request, with local filesystem dependencies for models and datasets

## Layers

**Entry Layer:**
- Purpose: Accept user input and present results
- Contains: `api.py`, `cli.py`, `app.py`, `start_api.py`
- Depends on: detection, autofix, quality, and model-status modules
- Used by: end users and test harnesses

**Detection Layer:**
- Purpose: Determine language, detect issues, and aggregate findings
- Contains: `src/error_engine.py`, `src/syntax_checker.py`, `src/multi_error_detector.py`, `src/language_detector.py`
- Depends on: ML layer, tutor explanations, and rule helpers
- Used by: API, CLI, Streamlit, and tests

**ML and Feature Layer:**
- Purpose: Load serialized artifacts and run feature-based error classification when available
- Contains: `src/ml_engine.py`, `src/feature_utils.py`
- Depends on: `models/*.pkl`, `joblib`, `scikit-learn`, `pandas`, `numpy`
- Used by: detection flow and evaluation scripts

**Feedback Layer:**
- Purpose: Explain issues, propose fixes, and analyze code quality
- Contains: `src/tutor_explainer.py`, `src/auto_fix.py`, `src/quality_analyzer.py`
- Depends on: detection outputs and language context
- Used by: API, CLI, Streamlit

**Evaluation Layer:**
- Purpose: Train, score, and report on model and rule behavior
- Contains: `scripts/`, `dataset/`, `artifacts/`, `results/`
- Depends on: core modules and local data artifacts
- Used by: QA workflows and maintainers

## Data Flow

**HTTP Request Flow:**

1. Client sends code to `/check`, `/quality`, `/fix`, or `/check-and-fix` in `api.py`
2. FastAPI validates payloads and enforces size/rate safeguards
3. The API calls shared analysis modules in `src/`
4. Detection returns structured issue data, warnings, and status details
5. API serializes the result back to JSON

**CLI Flow:**

1. User runs `python cli.py <path>`
2. `cli.py` reads the file and calls shared detection logic
3. CLI formats results, locations, and warnings for terminal output

**Streamlit Flow:**

1. User enters or uploads code in `app.py`
2. Streamlit triggers detection, autofix, or quality analysis
3. Results are rendered in a browser session

**State Management:**
- Request analysis is stateless
- ML availability is effectively process-global because model artifacts are loaded once
- API rate limiting keeps a small in-memory request log

## Key Abstractions

**Detection Result:**
- Purpose: Standard shape returned by the engine
- Examples: `predicted_error`, `line_number`, `column_number`, `explanation`, `degraded_mode`
- Pattern: dictionary-based result object rather than typed domain classes

**Rule-Based Issue:**
- Purpose: Represent localized issues for non-Python languages and multi-error reporting
- Examples: `type`, `message`, `line`, `col`, `snippet`, `suggestion`
- Pattern: normalized issue dicts aggregated by `src/error_engine.py` and `src/multi_error_detector.py`

**Model Status:**
- Purpose: Separate healthy versus degraded runtime behavior
- Examples: `get_model_status()`, `ModelUnavailableError`, `ModelInferenceError`
- Pattern: explicit health/status check before semantic ML use

## Entry Points

**API Server:**
- Location: `api.py`
- Triggers: HTTP requests, FastAPI startup
- Responsibilities: validation, rate limiting, health reporting, orchestration

**CLI:**
- Location: `cli.py`
- Triggers: terminal invocation
- Responsibilities: file loading, analysis execution, terminal formatting

**Streamlit UI:**
- Location: `app.py`
- Triggers: browser session through Streamlit
- Responsibilities: interactive analysis and quality views

**Server Bootstrap:**
- Location: `start_api.py`
- Triggers: local startup convenience command
- Responsibilities: load env and launch uvicorn

## Error Handling

**Strategy:** Fail safely at the boundaries and expose degraded mode when full ML behavior is not available

**Patterns:**
- API uses structured `HTTPException` payloads via `_raise_api_error`
- ML layer raises explicit unavailable/inference exceptions
- Detection paths fall back to rules when semantic ML cannot be trusted
- Tests encode regression expectations for fragile cases

## Cross-Cutting Concerns

**Logging:**
- Standard library logging in `api.py`
- Most other modules return structured values instead of logging heavily

**Validation:**
- FastAPI and Pydantic validate API inputs
- Detection modules perform language-specific sanity checks

**Compatibility:**
- Model artifact loading depends on pinned library versions and file presence
- Degraded mode is a core runtime concern across API, CLI, scripts, and UI

---
*Architecture analysis: 2026-03-27*
*Update when major patterns change*
