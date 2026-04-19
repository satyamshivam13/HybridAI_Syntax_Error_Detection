# Phase 07 Discussion Log

**Date:** 2026-04-19
**Mode:** `gsd-discuss-phase`
**Outcome:** Recommended defaults accepted by user (`7`)

## Locked Decisions

1. **Access control model**
   - Use a gateway-friendly API key model in Phase 07.
   - Do not expand Phase 07 into JWT, OAuth, accounts, or tenant identity.
   - Preserve local-development ergonomics with an explicit bypass mode.

2. **Rate limiting strategy**
   - Introduce a rate-limiter abstraction.
   - Keep in-memory behavior for local/single-process runs.
   - Add a Redis-capable production seam instead of baking in process-local throttling as the only story.

3. **Health contract**
   - Add distinct liveness, readiness, and capabilities endpoints.
   - Keep `/health` as a backward-compatible aggregate surface.
   - Report degraded-but-usable capability separately from process/readiness truth.

4. **API validation**
   - Reject unsupported languages and fix/error types at the API boundary.
   - Replace permissive free-string contracts with explicit typed enums or equivalent strict validation.

5. **Fix verification**
   - Revalidate generated fixes through the shared engine before reporting success.
   - Return a compact verification summary by default rather than a giant repeated detection payload.

6. **Docs exposure**
   - Disable Swagger/ReDoc by default in production-facing configurations.
   - Enable docs only through explicit configuration for trusted environments.

## Why These Defaults

- They close the biggest production lies without dragging the phase into a full platform rewrite.
- They preserve degraded-mode and local-dev usability.
- They make later phases cleaner: Phase 08 gets firmer contracts, Phase 10 gets clearer operator signals, and Phase 11 gets trustworthy fix UX.
