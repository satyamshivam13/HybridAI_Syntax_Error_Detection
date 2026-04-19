---
phase: 07-security-and-api-hardening
reviewed: 2026-04-19T15:19:29+05:30
depth: standard
files_reviewed: 6
files_reviewed_list:
  - api.py
  - src/config.py
  - src/auto_fix.py
  - tests/test_api_and_regressions.py
  - .env.template
  - docs/API_DOCUMENTATION.md
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues
---

# Phase 07: Advisory Code Review Gate (Plan 07-01)

**Reviewed:** 2026-04-19T15:19:29+05:30  
**Depth:** standard  
**Scope:** api.py, src/config.py, src/auto_fix.py, tests/test_api_and_regressions.py, .env.template, docs/API_DOCUMENTATION.md  
**Status:** issues

## Summary

Re-review confirms that previously reported contract mismatches in API docs and rate-limit backend handling are resolved in current code. One test reliability issue remains: a regression test is currently unconditional `xfail` and provides no assertion signal.

## Warnings

### WR-01: Regression test is unconditional xfail and never asserts behavior

**File:** `tests/test_api_and_regressions.py:399`  
**Issue:** `test_java_import_error_false_negative_regression` calls `pytest.xfail(...)` unconditionally after computing a result. This prevents the test from detecting both regressions and improvements, reducing confidence in API/model behavior.

**Fix:** Convert to conditional xfail (only under explicit environment conditions) and keep at least one bounded assertion. Example:

```python
if not ml.model_loaded:
    pytest.xfail("Model unavailable in this environment")

assert result["predicted_error"] in {"MissingImport", "NoError"}
```

If this case is intentionally unresolved, use `@pytest.mark.xfail(strict=False, reason=...)` with an assertion that still validates response shape or bounded outcomes.

## Resolved Since Prior Review

- `/fix` verification no longer trusts client-supplied error type and now passes `expected_original_error=None` (baseline derived from detector).
- Rate-limit backend now has explicit validity checks via `is_rate_limit_backend_valid()` and readiness integration.
- API docs now include `/check-and-fix` in request-size enforcement contract.

---

_Reviewed: 2026-04-19T15:19:29+05:30_  
_Reviewer: GitHub Copilot (GPT-5.3-Codex)_  
_Depth: standard_
