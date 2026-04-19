# OmniSyntax v1.2 Requirements

## Milestone Goal

Turn OmniSyntax from a reliable academic prototype into a deployable, secure, observable platform for classroom and beta usage without regressing degraded-mode correctness.

## Requirements

### Security and API Hardening
- [ ] **SEC-01**: Public API deployments require an explicit access-control layer so the service is not anonymously exposed on the open internet.
- [ ] **SEC-02**: Rate limiting and request safeguards work in both local single-process mode and a shared-store production mode.
- [ ] **API-01**: The API exposes distinct liveness, readiness, and capability/health semantics so operators can tell whether the service is up, ready, and fully ML-capable.
- [ ] **API-02**: Request and response contracts are strict and typed across `/check`, `/fix`, `/quality`, and `/check-and-fix`, including enum validation and a declared response model for combined flows.
- [ ] **API-03**: Fix-related endpoints only report success when the suggested output has been revalidated by the shared analysis pipeline.

### Architecture and Contracts
- [ ] **ARCH-01**: `src/static_pipeline.py` becomes the authoritative shared analysis path, with dead legacy branches removed from `src/error_engine.py` and `src/multi_error_detector.py`.
- [ ] **ARCH-02**: Shared detection results use typed internal contracts instead of ad hoc dict mutation across API, CLI, and Streamlit boundaries.
- [ ] **ARCH-03**: Entry points call a shared orchestration layer so API, CLI, and Streamlit stay behaviorally aligned as the engine evolves.

### Detection Assurance and ML Health
- [ ] **REL-01**: Java, C, C++, and JavaScript analysis gains a compiler/LSP adapter seam so OmniSyntax can evolve beyond handwritten heuristics without a rewrite.
- [ ] **REL-02**: CI proves the healthy-mode ML bundle can load in a compatible environment instead of only exercising degraded mode.
- [ ] **REL-03**: Accuracy and latency baselines are captured for the shared engine so future reliability work has measurable guardrails.

### Delivery and Observability
- [ ] **OPS-01**: The project ships a production-friendly container and environment baseline for local, staging, and production startup.
- [ ] **OPS-02**: CI enforces linting, typing, tests, coverage, and dependency/security checks across supported Python versions.
- [ ] **OPS-03**: API and engine flows emit structured logs and baseline operational metrics suitable for alerting and incident review.
- [ ] **OPS-04**: Tracing and alerting hooks exist for API failures, degraded-mode spikes, and runtime regressions.

### Performance and Scale Readiness
- [ ] **PERF-01**: CPU-heavy analysis can run through a configurable worker or isolated execution path instead of only inline request-thread execution.
- [ ] **PERF-02**: The engine supports prewarm and cache strategies that reduce cold-start and repeat-analysis overhead.
- [ ] **PERF-03**: Load and performance smoke checks exist alongside accuracy/latency benchmarks so scale regressions are measurable.

### UX and Analysis Quality
- [ ] **UX-01**: Streamlit avoids unnecessary full recomputation and surfaces confidence, evidence, and degraded-mode signals clearly.
- [ ] **UX-02**: Users see validated fix previews with diffs instead of opaque "automatic fix applied" messaging.
- [ ] **QUAL-01**: The quality analyzer becomes language-aware enough to produce credible JavaScript and non-Python scoring, including comment handling, complexity rules, and long-function detection.

### Product Foundations
- [ ] **PROD-01**: The product gains a persistence foundation for saved analyses, recent history, and lightweight analytics events.
- [ ] **PROD-02**: Multi-tenant, quota, and billing-readiness scaffolding is documented and minimally wired so commercial follow-on work does not require a restart from scratch.
- [ ] **PROD-03**: Users can analyze multi-file or project-mode inputs instead of being limited to a single snippet.
- [ ] **PROD-04**: The product captures explicit user feedback on analysis quality and fix usefulness so reliability work can use real signals.

### Educator Workflows
- [ ] **EDU-01**: Educators can review saved analyses and attach rubric-style notes or feedback artifacts without needing a full dashboard product.

## Future Requirements

- Rich classroom-management workflows, grading, and teacher dashboards.
- Full hosted SaaS account system with self-serve signup, organization management, and subscription billing.
- New language support beyond Python, Java, C, C++, and JavaScript.

## Out of Scope

- Immediate microservice decomposition of the entire product.
- Replacing the whole hybrid detection system in one milestone.
- Full commercial rollout, payment processing, or a complete auth/identity platform in this cycle.

## Traceability

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| SEC-01 | Phase 7 | Complete (2026-04-19) |
| SEC-02 | Phase 7 | Complete (2026-04-19) |
| API-01 | Phase 7 | Complete (2026-04-19) |
| API-02 | Phase 7 | Complete (2026-04-19) |
| API-03 | Phase 7 | Complete (2026-04-19) |
| ARCH-01 | Phase 8 | Planned |
| ARCH-02 | Phase 8 | Planned |
| ARCH-03 | Phase 8 | Planned |
| REL-01 | Phase 9 | Planned |
| REL-02 | Phase 9 | Planned |
| REL-03 | Phase 9 | Planned |
| OPS-01 | Phase 10 | Planned |
| OPS-02 | Phase 10 | Planned |
| OPS-03 | Phase 10 | Planned |
| OPS-04 | Phase 10 | Planned |
| PERF-01 | Phase 10 | Planned |
| PERF-02 | Phase 10 | Planned |
| PERF-03 | Phase 10 | Planned |
| UX-01 | Phase 11 | Planned |
| UX-02 | Phase 11 | Planned |
| QUAL-01 | Phase 11 | Planned |
| PROD-01 | Phase 12 | Planned |
| PROD-02 | Phase 12 | Planned |
| PROD-03 | Phase 13 | Planned |
| PROD-04 | Phase 13 | Planned |
| EDU-01 | Phase 13 | Planned |

## Planning Notes

- The phase order is intentionally risk-first: security, contract hardening, and architecture cleanup come before product expansion.
- Commercial-readiness work is limited to foundations until the platform is secure, observable, and stable.
- Every major finding from the April 19, 2026 audit is now mapped either to an active v1.2 phase or an explicit future requirement; nothing is left as an untracked concern.
