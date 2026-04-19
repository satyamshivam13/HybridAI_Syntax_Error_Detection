# Phase 07: security-and-api-hardening - Context

**Gathered:** 2026-04-19
**Status:** Discussed and decision-locked
**Source:** Deep production audit converted into v1.2 execution scope and refined via discuss-phase on 2026-04-19

<domain>
## Phase Boundary

Remove the highest-risk production blockers at the API boundary without widening the product into a full hosted SaaS account system.

</domain>

<decisions>
## Implementation Decisions

### API access and safety
- **D-01:** Public deployment must require an explicit access-control layer; local development may keep a bypass.
- **D-02:** Rate limiting must support the current in-memory mode for local use and a shared-store-ready production path.
- **D-06:** Interactive API docs should be disableable by default in production-facing configurations.
- **D-07:** Phase 07 will implement a gateway-friendly API key model rather than full JWT/OAuth. Local development may run with auth disabled, but non-local deployment must require an API-key-style gate unless an explicit unsafe override is set.
- **D-08:** Rate limiting will be introduced behind a provider abstraction with an in-memory default and a Redis-capable adapter seam for production deployments.

### Health and contract semantics
- **D-03:** Liveness, readiness, and capability/health semantics must be distinct so operators can tell "process up" from "ML healthy" from "service degraded but usable."
- **D-04:** Endpoint contracts must become strict and typed, including enum validation and a declared response model for `/check-and-fix`.
- **D-09:** `/health/live`, `/health/ready`, and `/health/capabilities` will be added. The existing `/health` endpoint should remain as a backward-compatible aggregate response and be documented as legacy-compatible.
- **D-10:** Unsupported languages and fix/error types must be rejected at the API boundary with explicit 4xx validation errors rather than silently accepted or normalized.

### Fix trustworthiness
- **D-05:** `/fix` and `/check-and-fix` may only claim success after the proposed output has been revalidated through the shared engine.
- **D-11:** Revalidation responses should default to a compact verification summary that states whether the original issue was removed, improved, unchanged, or worsened, with room to include optional detailed analysis later.
- **D-12:** Production-facing configurations should disable Swagger/ReDoc by default and allow enablement only through explicit configuration intended for trusted environments.

### the agent's Discretion
- Naming of configuration flags and DTO types, as long as they make the deployment contract obvious.
- Whether `/fix` and `/check-and-fix` share one verification summary model or use closely related typed models.
- Whether the legacy `/health` aggregate is marked deprecated in docs only or also returns an explicit compatibility note.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning and requirements
- `.planning/PROJECT.md` - current milestone goal and constraints.
- `.planning/REQUIREMENTS.md` - v1.2 requirement set and phase traceability.
- `.planning/ROADMAP.md` - milestone ordering and dependencies.
- `.planning/STATE.md` - current execution focus.

### Architecture and concerns
- `.planning/codebase/ARCHITECTURE.md` - entry-point and detection-layer boundaries.
- `.planning/codebase/CONCERNS.md` - production blockers already identified in the repo maps.
- `api.py` - current API surface, rate limiting, and health endpoint behavior.
- `src/auto_fix.py` - current fix behavior and success contract.
- `tests/test_api_and_regressions.py` - existing API regression patterns.

</canonical_refs>

<specifics>
## Specific Ideas

- Prefer a modest, explicit API key or middleware-based gate over a half-built auth system.
- Prefer a gateway-friendly API key model and Redis-capable throttling path over pretending in-memory host-based limits are enough.
- Preserve degraded-mode behavior and warning propagation while improving operator-facing health semantics.
- Keep the API public contract stable where possible, but do not preserve unsafe behavior just for backward compatibility.
- Reject invalid API inputs early and loudly; do not let permissive contracts hide client bugs.
- Treat "generated a suggestion" and "verified improvement" as different states in the fix workflow.

</specifics>

<deferred>
## Deferred Ideas

- Full end-user auth, classroom accounts, and organization management.
- Billing and tenant management beyond scaffold-level planning.

</deferred>

---

*Phase: 07-security-and-api-hardening*
*Context gathered: 2026-04-19*
