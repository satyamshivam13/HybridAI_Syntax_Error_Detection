---
name: OmniSyntax Project Cleanup And Structure
description: "Find duplicate code, detect unused files/symbols, and restructure OmniSyntax safely while preserving degraded-mode reliability"
argument-hint: "Scope and constraints (for example: src and tests only, no file deletes without approval)"
agent: agent
---
Clean and reorganize OmniSyntax based on the request: $ARGUMENTS

## Project Context

**OmniSyntax** is a brownfield Python project that detects and explains code issues for students across Python, Java, C, C++, and JavaScript. The same analysis engine powers:
- FastAPI REST API (`api.py`, `start_api.py`)
- Streamlit web interface (`app.py`)
- CLI utility (`cli.py`)

**Core value:** Students must receive accurate, actionable code-error feedback even when the ML layer is unavailable (degraded mode).

**Working rules:**
- Treat degraded-mode correctness as a first-class requirement
- Add tests for every detection bug fix
- Prefer shared logic in `src/` over duplicating behavior in entry points
- Be especially careful in `src/error_engine.py` and `src/multi_error_detector.py` (high-impact modules)

Default scope for this repository:
- All folders and files in the workspace, including `src/`, `tests/`, root `*.py` files, `scripts/`, `docs/`, `artifacts/`, `results/`, and `models/`.
- Entry points: `api.py`, `app.py`, `cli.py`, `start_api.py`
- Engine core: `src/error_engine.py`, `src/multi_error_detector.py`
- Regression tests: `tests/` (currently 100% passing in v1.0)
- ML artifacts: `models/bundle_metadata.json`
- Treat this as a workspace-scoped cleanup policy aligned with brownfield reliability goals.

Goals:
1. Remove or consolidate duplicate code across entry points and shared modules.
2. Detect unused files, modules, and symbols without breaking API/CLI/Streamlit behavior.
3. Improve project structure and consistency while preserving degraded-mode reliability.
4. Preserve test coverage and maintain regression protection for C, Java, and JavaScript detection.
5. Identify opportunities to strengthen the `src/` layer so entry points share more logic safely.

Required workflow:
1. Inspect the repository and produce an action plan grouped by:
- Duplicate logic
- Dead/unused code and files
- Structural improvements (folders, naming, boundaries)
2. For each proposed removal or move, provide impact and confidence:
- Why it appears unused or duplicated
- What references were checked
- Confidence level (high, medium, low)
3. Ask for confirmation before deleting files or making low-confidence removals.
4. Implement approved changes in small, reviewable edits.
5. Update imports/paths/tests after each structural change.
6. Run available tests or smoke checks and report results.
7. Provide a final cleanup report with:
- Files changed
- Files removed
- Duplicates consolidated
- Risks or follow-ups

Safety constraints:
- Do not use destructive git commands.
- Include generated artifacts (`artifacts/`, `results/`) in analysis but flag them as non-source.
- Do not remove or weaken `src/error_engine.py` or `src/multi_error_detector.py` without explicit justification.
- Do not consolidate entry-point code (`api.py`, `app.py`, `cli.py`) without verifying behavior across all three interfaces.
- Test any changes against the full test suite: `python -m pytest tests/ -q`
- Run smoke checks: verify API, CLI, and Streamlit work in both healthy and degraded mode (`python scripts/test_false_positives.py`, `python cli.py tests/Test.java`)
- If uncertain whether a file is required, keep it and mark it as a candidate for post-cleanup review.
- Prefer reversible, minimal-risk refactors.
- Always ask before deleting any file, especially in `src/`, `tests/`, or `models/`.

Output format:
1. **Findings**: concise list with file references, grouped by duplicate logic / unused code / structural improvements.
2. **Proposed plan**: ordered steps with risk level (high/medium/low); cross-entry-point impact assessment; test strategy.
3. **Implemented changes**: what was done and why; entry point verification (API/CLI/Streamlit); degraded-mode testing.
4. **Verification**: 
   - Full test suite: `python -m pytest tests/ -q`
   - Smoke tests: `python scripts/test_false_positives.py`, `python cli.py tests/Test.java`
   - API health check: `python start_api.py` (verify startup)
   - Streamlit check: `python -m streamlit run app.py` (verify startup in --logger.level=debug mode)
5. **Remaining candidates**: items needing manual decision; low-confidence removals; post-cleanup review items.
