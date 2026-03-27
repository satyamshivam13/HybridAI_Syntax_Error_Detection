# Codebase Structure

**Analysis Date:** 2026-03-27

## Directory Layout

```text
OmniSyntax/
|-- .github/             # CI workflows
|-- artifacts/           # Generated evaluation outputs
|-- dataset/             # Training and evaluation datasets
|-- docs/                # Project documentation and QA reports
|-- models/              # Serialized ML artifacts
|-- results/             # Generated result files
|-- scripts/             # Training, evaluation, and maintenance scripts
|-- src/                 # Core detection, autofix, and quality logic
|-- tests/               # Automated regression and smoke tests
|-- api.py               # FastAPI entry point
|-- app.py               # Streamlit entry point
|-- cli.py               # Command-line entry point
|-- start_api.py         # API bootstrap helper
|-- requirements.txt     # Runtime dependencies
|-- requirements-dev.txt # Development and test dependencies
|-- .env.template        # Environment configuration template
`-- README.md            # Main project overview
```

## Directory Purposes

**src/**
- Purpose: Core application logic
- Contains: detection modules, ML integration, auto-fix, quality analysis, tutor explanations
- Key files: `src/error_engine.py`, `src/ml_engine.py`, `src/multi_error_detector.py`
- Subdirectories: `src/utils/` for shared CLI helpers

**scripts/**
- Purpose: Evaluation, retraining, reporting, and maintenance tasks
- Contains: smoke scripts, dataset tools, model retraining helpers
- Key files: `scripts/generate_results.py`, `scripts/advanced_metrics.py`, `scripts/retrain_model.py`
- Subdirectories: `scripts/utils/` for shared ML script helpers

**tests/**
- Purpose: Automated verification
- Contains: API tests, engine regressions, smoke checks, sample fixtures
- Key files: `tests/test_api_and_regressions.py`, `tests/test_c_java_js_regressions.py`, `tests/test_script_smoke.py`
- Subdirectories: flat structure today

**docs/**
- Purpose: Human-readable product, API, and QA documentation
- Contains: setup docs, reports, summaries, and contribution guidance
- Key files: `docs/API_DOCUMENTATION.md`, `docs/QA_REPORT_2026-03-27.md`
- Subdirectories: flat structure today

**dataset/**, **models/**, **artifacts/**, **results/**
- Purpose: Data and generated files used by training, evaluation, and reporting
- Contains: CSV data, serialized models, measurement artifacts, and output reports
- Key files: local artifacts vary by environment
- Subdirectories: `dataset/active/`, `dataset/archive/`, `dataset/merged/`

## Key File Locations

**Entry Points:**
- `api.py` - FastAPI application
- `app.py` - Streamlit application
- `cli.py` - terminal interface
- `start_api.py` - API startup helper

**Configuration:**
- `requirements.txt` - runtime dependencies
- `requirements-dev.txt` - development and CI dependencies
- `.env.template` - expected environment variables
- `.github/workflows/ci.yml` - CI workflow

**Core Logic:**
- `src/error_engine.py` - primary hybrid detector
- `src/multi_error_detector.py` - multi-issue aggregation for C-like languages
- `src/ml_engine.py` - model loading and semantic classification
- `src/auto_fix.py` - fix suggestion application
- `src/quality_analyzer.py` - non-syntax quality metrics

**Testing:**
- `tests/` - automated test suite
- `tests/Test.java` - Java fixture used in tests and manual checks

**Documentation:**
- `README.md` - repo overview and commands
- `PROJECT_STATUS.md` - current project notes
- `PROJECT_STRUCTURE.md` - human summary of layout

## Naming Conventions

**Files:**
- `snake_case.py` for Python modules
- `test_*.py` for pytest files
- `UPPERCASE.md` or descriptive report filenames for major docs

**Directories:**
- lowercase directory names
- plural nouns for collections such as `docs/`, `tests/`, `scripts/`

**Special Patterns:**
- Root-level entry point scripts for user interfaces
- `src/` contains reusable logic imported by every interface

## Where to Add New Code

**New Detection Feature:**
- Primary code: `src/`
- Tests: `tests/`
- Docs if behavior changes: `docs/`

**New Script or Evaluation Job:**
- Implementation: `scripts/`
- Shared helpers: `scripts/utils/`
- Outputs: `artifacts/` or `results/`

**New Entry-Point Behavior:**
- API changes: `api.py`
- CLI changes: `cli.py`
- UI changes: `app.py`

**Utilities:**
- Shared runtime helpers: `src/utils/`
- Shared script helpers: `scripts/utils/`

## Special Directories

**models/**
- Purpose: Serialized ML artifacts loaded at runtime
- Source: training output and checked-in artifacts
- Committed: yes

**artifacts/** and **results/**
- Purpose: generated QA and evaluation outputs
- Source: reporting and metrics scripts
- Committed: mixed; treat as generated content

**.planning/**
- Purpose: GSD project memory, roadmap, and codebase maps
- Source: maintained by GSD workflows
- Committed: yes, if the team wants planning artifacts versioned

---
*Structure analysis: 2026-03-27*
*Update when directory structure changes*
