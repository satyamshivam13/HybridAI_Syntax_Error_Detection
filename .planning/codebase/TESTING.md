# Testing Patterns

**Analysis Date:** 2026-03-27

## Test Framework

**Runner:**
- pytest
- CI runs `pytest tests/ -v -p no:cacheprovider`

**Assertion Library:**
- pytest built-in assertions
- Matchers are plain Python `assert` statements plus `pytest.raises`, `pytest.mark.parametrize`, and `xfail`

**Run Commands:**
```bash
python -m pytest tests/ -q
python -m pytest tests/ -v -p no:cacheprovider
python scripts/check_links.py
python scripts/generate_results.py --smoke
python scripts/advanced_metrics.py --smoke
```

## Test File Organization

**Location:**
- Tests live in a dedicated `tests/` directory
- Smoke and regression checks share the same tree

**Naming:**
- `test_*.py` for all automated tests
- Fixture-like sample files may live alongside tests, for example `tests/Test.java`

**Structure:**
```text
tests/
  conftest.py
  test_api_and_regressions.py
  test_c_java_js_regressions.py
  test_detection.py
  test_multi_error_detector.py
  test_script_smoke.py
  Test.java
```

## Test Structure

**Suite Organization:**
```python
def test_example():
    result = function_under_test(...)
    assert result["has_errors"] is False

@pytest.mark.parametrize("filename,code", [...])
def test_parameterized_example(filename, code):
    ...
```

**Patterns:**
- Small focused test functions are preferred over large class-based suites
- `pytest.mark.parametrize` is used heavily for language and fixture coverage
- Regression tests assert exact fields such as `predicted_error`, `status_code`, `degraded_mode`, and issue counts

## Mocking

**Framework:**
- pytest monkeypatch and direct module attribute overrides

**Patterns:**
```python
def test_health_reflects_model_state(monkeypatch):
    api = _load_api(monkeypatch, rate_limit="100")
    ...
```

**What to Mock:**
- Environment variables
- Model availability flags or ML state
- Reloaded modules when API config depends on env vars

**What NOT to Mock:**
- Core rule-based detection when writing regression tests
- Simple pure helpers that can be exercised directly

## Fixtures and Factories

**Test Data:**
- Most fixtures are inline code snippets
- Reusable helper functions live inside test modules when needed
- `tests/Test.java` acts as a file fixture for Java scenarios

**Location:**
- Shared pytest setup in `tests/conftest.py`
- Additional ad hoc helpers are kept near the tests that use them

## Coverage

**Requirements:**
- No explicit percentage target is documented
- Practical focus is regression protection for detection, API behavior, and script smoke paths

**Configuration:**
- `pytest-cov` is available in dependencies
- CI currently enforces test and link-check success rather than a hard coverage threshold

## Test Types

**Unit Tests:**
- Detection, autofix, and utility behavior in isolation

**Integration Tests:**
- FastAPI routes through `TestClient`
- End-to-end style checks across detection plus entry-point formatting

**Smoke Tests:**
- Scripts such as `generate_results.py` and `advanced_metrics.py`
- Startup checks for API and Streamlit behavior are suitable additions here

## Common Patterns

**Error Testing:**
```python
with pytest.raises(ModelUnavailableError):
    detect_error_ml("x = 1")
```

**Response Testing:**
```python
response = client.post("/check", json={"code": "x=1", "filename": "x.py"})
assert response.status_code == 200
```

**Regression Testing:**
- Use concrete snippets that previously failed
- Assert the exact issue type or degraded-mode behavior that must remain stable

## Current Gaps

- No dedicated browser automation for Streamlit
- Limited automated verification for retraining and model artifact regeneration
- Healthy-mode ML behavior is harder to exercise when the local artifact set is incompatible

---
*Testing analysis: 2026-03-27*
*Update when test patterns change*
