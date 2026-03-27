# AGENTS

## Project Summary

OmniSyntax is a brownfield Python project for multi-language code-error detection in programming education. The same shared engine powers a FastAPI API, a Streamlit app, and a CLI.

## Where To Start

- Read `.planning/PROJECT.md` for product context and current priorities
- Read `.planning/ROADMAP.md` for the active phase plan
- Read `.planning/STATE.md` for current execution status
- Read `.planning/codebase/` for architecture, structure, testing, and concern maps

## Current Focus

- Improve C, Java, and JavaScript reliability in degraded mode
- Restore or redesign ML compatibility safely
- Keep API, CLI, and Streamlit behavior aligned
- Preserve and expand regression coverage

## Working Rules

- Treat degraded-mode correctness as a first-class requirement
- Add tests for every detection bug fix
- Prefer shared logic in `src/` over duplicating behavior in entry points
- Be careful in `src/error_engine.py` and `src/multi_error_detector.py`; both are high-impact modules

## Useful Commands

```bash
python -m pytest tests/ -q
python scripts/check_links.py
python start_api.py
python -m streamlit run app.py
python cli.py tests/Test.java
```
