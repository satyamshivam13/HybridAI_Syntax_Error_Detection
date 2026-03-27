# Project Status

Last updated: 2026-03-27

## Overall
- Active development in a brownfield codebase
- Core tests and startup smoke checks are available
- API, CLI, and Streamlit entry points are present and aligned around shared `src/` logic

## Reliability focus
- Improve degraded-mode correctness for C, Java, and JavaScript
- Preserve regression behavior across API/CLI/UI surfaces
- Keep ML compatibility safe and explicit

## Quality posture
- Automated tests in `tests/`
- CI runs full test suite plus markdown link validation
- Additional QA and evaluation outputs are tracked under `artifacts/` and `results/`

## Recommended verification commands
```bash
python -m pytest tests/ -q
python scripts/check_links.py
python start_api.py
python -m streamlit run app.py
python cli.py tests/Test.java
```
