# Phase 07 Research: Security and API Hardening

**Date:** 2026-04-19
**Phase:** 07
**Source:** Local codebase research after discuss-phase decision lock

## Research Question

What do we need to know to plan Phase 07 well without widening scope into a full hosted identity platform?

## Current State

### API boundary
- `api.py` currently exposes a public FastAPI app with `docs_url="/docs"` and `redoc_url="/redoc"`.
- There is no auth dependency, API key check, or production guardrail before requests hit `/check`, `/fix`, `/quality`, or `/check-and-fix`.
- Rate limiting is implemented in-process with `_REQUEST_LOG`, `_REQUEST_LOCK`, and `request.client.host`, so multi-worker or multi-instance deployments will drift immediately.

### Health semantics
- `/health` currently collapses process health and ML availability into one `healthy|degraded` status.
- The service still functions in degraded mode, so current semantics are not good enough for readiness gates or orchestration.

### Request and response contracts
- `CodeCheckRequest` validates `language` manually, not at the type layer.
- `AutoFixRequest.error_type` and `QualityCheckRequest.language` are permissive free strings.
- `/check-and-fix` has no declared response model.
- Existing tests in `tests/test_api_and_regressions.py` already assert payload limits, `/health`, language override, and rate-limit behavior, so the phase has a good regression foothold.

### Auto-fix trust boundary
- `src/auto_fix.py` supports a bounded set of fixable error types in `AutoFixer.apply_fixes`.
- `api.py` currently returns fix success directly from the fixer without re-running shared detection on the proposed output.
- This means the API can claim a fix is available even when the returned code still has the original problem.

## Recommended Implementation Shape

### 1. Access control
- Use a simple API-key model for production-facing deployments.
- Keep local development ergonomic with an explicit bypass mode.
- Make unsafe deployment a conscious override rather than the default.

Recommended config contract:
- `PRODUCTION=true|false`
- `API_AUTH_MODE=disabled|api_key`
- `API_KEYS=key1,key2`
- `ALLOW_UNSAFE_PUBLIC_API=true|false` only for deliberate override scenarios

### 2. Rate limiting
- Introduce a rate-limiter abstraction in `api.py` or a small shared helper.
- Keep the existing in-memory behavior as the default implementation for local development and tests.
- Add a Redis-capable adapter seam and configuration surface rather than pretending host-local throttling is production-ready.

Recommended config contract:
- `RATE_LIMIT_PER_MINUTE`
- `RATE_LIMIT_BACKEND=memory|redis`
- `RATE_LIMIT_REDIS_URL`
- `RATE_LIMIT_KEY_HEADER` optional if gateway/API-key identity should override client-host bucketing

### 3. Health semantics
- Split health into:
  - `/health/live`: process is alive
  - `/health/ready`: process is ready to serve requests
  - `/health/capabilities`: ML loaded vs degraded but usable
- Keep `/health` as a backward-compatible aggregate response so existing clients and tests do not break all at once.

### 4. Strict contracts
- Use typed enums for supported languages and supported auto-fix error types.
- Normalize casing rules explicitly instead of accepting arbitrary strings.
- Add a declared response model for `/check-and-fix`.

Likely enum candidates:
- Languages: `Python`, `Java`, `C`, `C++`, `JavaScript`
- Auto-fix error types: bounded to branches already present in `AutoFixer.apply_fixes`

### 5. Fix verification
- Separate "generated a suggestion" from "verified improvement."
- After `AutoFixer.apply_fixes`, re-run `detect_errors` on the proposed code.
- Return a compact verification summary:
  - `status`: `verified_removed|verified_improved|unchanged|worsened|not_verified`
  - `original_error`
  - `result_error`
  - `verified`

## Risks

### Scope creep risk
- Full JWT/OAuth is out of scope and would slow the milestone down.
- Redis integration can balloon if the phase tries to solve distributed infrastructure end to end instead of defining a clean runtime seam.

### Compatibility risk
- Existing `/health` callers may assume the current shape.
- Existing tests load `api` via module reload and env mutation; config changes should stay reload-friendly.

### Behavior risk
- Hardening validation may break callers currently relying on permissive strings.
- Fix verification needs to avoid reporting false success without also turning suggestion-only fixes into blanket failures with no explanation.

## Planning Implications

1. Keep Phase 07 to one plan, but structure tasks around three distinct deliverables:
   - boundary controls and deployment-safe defaults
   - health plus strict API contracts
   - verified fix workflow
2. Keep implementation centered in `api.py`, `src/config.py`, `src/auto_fix.py`, `tests/test_api_and_regressions.py`, `.env.template`, and `docs/API_DOCUMENTATION.md`.
3. Preserve degraded-mode correctness and backward-compatible `/health` behavior while tightening deployment posture.

## Verification Strategy

- Focused regression: `python -m pytest tests/test_api_and_regressions.py -q`
- Broader confidence after implementation: `python -m pytest tests/ -q`
- Require new tests for:
  - unauthorized access in production-facing mode
  - docs exposure toggles
  - split health semantics
  - strict enum rejection
  - `/check-and-fix` response model behavior
  - revalidated fix success and non-improving fix paths

## Recommendation

Proceed with a refreshed single-plan Phase 07 that locks explicit config names, typed contracts, and a revalidation summary model. The codebase is ready for that level of hardening without requiring a rewrite.
