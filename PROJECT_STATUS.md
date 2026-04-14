# Project Status

Last updated: 2026-04-14

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

## Latest verification snapshot
- `python -m pytest tests/ -q` => 179 passed, 1 skipped, 1 xfailed
- `python scripts/production_validation.py` => all production gates passing, confidence_ece 0.0391
- `python scripts/adversarial_validation.py` => mutation_accuracy 97.08, real_world_accuracy 97.3, verdict PRODUCTION_READY
- `node "$HOME/.copilot/get-shit-done/bin/gsd-tools.cjs" audit-uat --raw` => 0 outstanding UAT/verification items (all clear)

## Recommended verification commands
```bash
python -m pytest tests/ -q
python scripts/check_links.py
python start_api.py
python -m streamlit run app.py
python cli.py tests/Test.java
```
