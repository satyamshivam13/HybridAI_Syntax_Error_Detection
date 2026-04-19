# Phase 12: product-foundations-and-commercial-readiness - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Add the persistence and product scaffolding needed for saved analysis history, lightweight analytics, and future quota or billing work without prematurely building a full SaaS platform.

</domain>

<decisions>
## Implementation Decisions

### Persistence foundation
- **D-01:** The product needs a small persistence layer for saved analyses, recent history, and analytics events.
- **D-02:** The storage approach should work locally with a lightweight default and leave a clean path to a production database.

### Commercial-readiness scaffolding
- **D-03:** Tenant, quota, and billing readiness should be documented and minimally scaffolded, not fully productized.
- **D-04:** Product instrumentation should support retention and reliability learning before monetization is attempted.

### Scope discipline
- **D-05:** This phase is about foundations, not a full classroom SaaS launch.

### the agent's Discretion
- Exact storage technology and schema, as long as it is simple locally and production-aware.
- Whether quota and billing readiness lives in code, docs, or both, provided it is concrete enough to build on.

</decisions>

<canonical_refs>
## Canonical References

### Planning
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/phases/12-product-foundations-and-commercial-readiness/12-CONTEXT.md`

### Product and runtime surfaces
- `api.py`
- `app.py`
- `cli.py`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONCERNS.md`

</canonical_refs>

<specifics>
## Specific Ideas

- Start with persistence that supports saved analyses and recent history rather than inventing a broad domain model too early.
- Analytics should support learning and reliability, not surveillance theater.
- Billing readiness means boundary design and hooks, not payment UI.

</specifics>

<deferred>
## Deferred Ideas

- Full account system and self-serve subscriptions.
- Rich teacher dashboards or multi-role collaboration flows.

</deferred>

---

*Phase: 12-product-foundations-and-commercial-readiness*
*Context gathered: 2026-04-19*
