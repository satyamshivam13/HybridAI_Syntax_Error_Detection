# Phase 10: delivery-ci-and-observability - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Bring OmniSyntax up to a baseline level of delivery maturity with containers, enforceable CI quality gates, and operational visibility for the API and analysis engine.

</domain>

<decisions>
## Implementation Decisions

### Delivery baseline
- **D-01:** The repo needs a production-friendly container and environment baseline for local, staging, and production use.
- **D-02:** Startup and deployment behavior should be driven by clear environment configuration instead of ad hoc local scripts alone.
- **D-06:** Dependency hygiene and docs must match the live runtime contract, including the current scikit-learn bundle expectations.

### CI gates
- **D-03:** CI should enforce linting, typing, tests, coverage, and dependency/security checks across supported Python versions.
- **D-04:** Build and verification steps should reflect the real deployable artifact, not only source-level unit tests.

### Observability
- **D-05:** API and engine flows must emit structured logs and baseline metrics so incidents and regressions are observable.

### Performance and scale readiness
- **D-07:** CPU-heavy analysis needs a configurable worker or isolation seam instead of living forever on the main request thread only.
- **D-08:** Engine prewarm and cache strategy must reduce cold-start and repeat-analysis cost.
- **D-09:** Load and performance smoke checks should exist alongside functionality checks.

### the agent's Discretion
- Exact tooling for metrics and error reporting, as long as the baseline is pragmatic for the repo's scale.
- Whether staging and production manifests are Docker-only or include compose/make helpers.

</decisions>

<canonical_refs>
## Canonical References

### Planning
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/phases/10-delivery-ci-and-observability/10-CONTEXT.md`

### Delivery and operations surfaces
- `.planning/codebase/CONCERNS.md`
- `.github/workflows/ci.yml`
- `requirements.txt`
- `requirements-dev.txt`
- `start_api.py`
- `api.py`
- `README.md`
- `.env.template`

</canonical_refs>

<specifics>
## Specific Ideas

- Remove the current ambiguity where `requirements.txt` includes test-only packages.
- Treat CI as a release gate, not just a smoke signal.
- Structured logging must cover both API failures and engine degradation paths.
- Tracing, alert hooks, worker seams, and cache strategy are required to make "production-ready" mean anything.

</specifics>

<deferred>
## Deferred Ideas

- Full Kubernetes or cloud-specific deployment stacks.
- Complex SRE automation beyond baseline instrumentation and alerts.

</deferred>

---

*Phase: 10-delivery-ci-and-observability*
*Context gathered: 2026-04-19*
