---
phase: 07-security-and-api-hardening
reviewed: 2026-04-19T15:11:46+05:30
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
  warning: 4
  info: 0
  total: 4
status: issues
---

# Phase 07: Advisory Code Review Gate (Plan 07-01)

**Reviewed:** 2026-04-19T15:11:46+05:30  
**Depth:** standard  
**Scope:** api.py, src/config.py, src/auto_fix.py, tests/test_api_and_regressions.py, .env.template, docs/API_DOCUMENTATION.md  
**Status:** issues

## Summary

The phase improves API hardening and introduces clearer health/auth/rate-limit contracts, but there are still contract/correctness gaps that can cause misleading fix verification, fail-open rate-limit behavior under misconfiguration, and reduced regression-test signal. No direct critical vulnerabilities were found in this scope.

## Warnings

### WR-01: /fix verification trusts client-provided error type instead of actual baseline

**File:** `api.py:604` (baseline assignment path starts in `_verify_fix_result` at `api.py:248`)  
**Issue:** `/fix` passes `expected_original_error=request.error_type.value`, so verification compares post-fix results against the user-requested label rather than the actual pre-fix detector result. This can produce false positives (for example, reporting `verified_removed` when no such original error existed), weakening the API contract for `verified`/`success`.

**Fix:** Derive baseline from detector output, not request input. Either:

```python
# Option A: remove expected_original_error for /fix
verification = _verify_fix_result(
    original_code=request.code,
    fixed_code=fixed_code,
    language=language,
    filename=None,
)
```

or:

```python
# Option B: precompute true baseline explicitly and pass it
baseline = detect_errors(request.code, None, language)["predicted_error"]
verification = _verify_fix_result(
    original_code=request.code,
    fixed_code=fixed_code,
    language=language,
    filename=None,
    expected_original_error=baseline,
)
```

Also add a regression test where requested `error_type` differs from detected baseline and assert `verification.original_error` reflects detector output.

### WR-02: Unknown RATE_LIMIT_BACKEND silently falls back to memory (fail-open config)

**File:** `api.py:201-208`, `src/config.py:56-57`  
**Issue:** `get_rate_limit_backend()` accepts any string and `_build_rate_limiter()` defaults to memory unless backend equals `redis`. A typo like `RATE_LIMIT_BACKEND=redsi` quietly disables intended shared-store enforcement in multi-worker deployments.

**Fix:** Validate backend strictly and fail closed:

```python
# src/config.py

def get_rate_limit_backend() -> str:
    backend = os.getenv("RATE_LIMIT_BACKEND", "memory").strip().lower() or "memory"
    if backend not in {"memory", "redis"}:
        raise ValueError("RATE_LIMIT_BACKEND must be 'memory' or 'redis'")
    return backend
```

Then surface this via readiness/config validation so misconfiguration yields `not_ready` instead of implicit fallback.

### WR-03: Regression test always xfails without asserting behavior

**File:** `tests/test_api_and_regressions.py:391-399`  
**Issue:** `test_java_import_error_false_negative_regression` computes a result but immediately calls `pytest.xfail(...)` with no assertions. This test currently cannot detect regressions or improvements and can mask contract drift.

**Fix:** Convert to conditional `xfail` with an explicit assertion target. Example:

```python
if not ml.model_loaded:
    pytest.xfail("Model unavailable in this environment")

assert result["predicted_error"] in {"MissingImport", "NoError"}
# Or pin exact expected behavior for current policy.
```

If behavior is intentionally unresolved, mark with `@pytest.mark.xfail(strict=False, reason=...)` and still assert a bounded outcome.

### WR-04: API docs request-limit section omits /check-and-fix despite enforcement

**File:** `docs/API_DOCUMENTATION.md:42-44`, `api.py:663-667`  
**Issue:** Documentation says `/check`, `/fix`, and `/quality` enforce `MAX_CODE_SIZE`, but `/check-and-fix` also enforces `_validate_code_payload`. This is a contract/documentation mismatch that may surprise API consumers.

**Fix:** Update docs request-limit section to include `/check-and-fix` and add a parity test covering 413 behavior for `/check-and-fix` in `test_payload_limit_parity`.

## Residual Risks

- Redis backend readiness is handled, but configuration strictness is still permissive until WR-02 is addressed.
- Verification semantics can still be misinterpreted by clients until WR-01 is fixed and regression-tested.
- Documentation and test parity for `/check-and-fix` limits should be aligned to prevent client-side contract assumptions.

---

_Reviewed: 2026-04-19T15:11:46+05:30_  
_Reviewer: GitHub Copilot (GPT-5.3-Codex)_  
_Depth: standard_
