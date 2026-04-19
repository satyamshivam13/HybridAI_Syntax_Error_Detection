# Roadmap: OmniSyntax

## Milestones

- ✅ **v1.0 Cross-Language Reliability** — Phases 1–5 (shipped 2026-03-27) — [archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Reliability Refinement** — Phase 6 (completed 2026-04-11)
- 🟡 **v1.2 Production Hardening and Product Foundations** — Phases 7–13 (planned 2026-04-19)

## Phases

<details>
<summary>✅ v1.0 Cross-Language Reliability (Phases 1–5) — SHIPPED 2026-03-27</summary>

- [x] Phase 1: Detection Reliability (2/2 plans) — completed 2026-03-27
- [x] Phase 2: Diagnostics and Autofix Quality (2/2 plans) — completed 2026-03-27
- [x] Phase 3: Runtime Health and ML Recovery (3/3 plans) — completed 2026-03-27
- [x] Phase 4: QA Hardening and Release Readiness (2/2 plans) — completed 2026-03-27
- [x] Phase 5: Cross-Language Reliability Hardening (4/4 plans) — completed 2026-03-27

</details>

### v1.1 (Complete)

### Phase 6: Python and Java Reliability Refinement
**Goal**: Close the remaining Python and Java reliability gaps without regressing the shared API, CLI, and Streamlit contracts established in v1.0.
**Depends on**: Phase 5
**Plans**: 2 plans

Plans:
- [x] 06-01: Merge Python semantic ML into all-errors and stabilize Java mixed-error precedence
- [x] 06-02: Keep autofix guidance conservative while tightening location-aware messaging and regression coverage

**Outcome:** Python all-errors mode merges confident semantic ML findings as a separate grouped result. IndentationError and UnclosedString stay suggestion-only but gain exact location-aware guidance. Java suppresses the known mixed-case false positive only when context proves it.

### v1.2 (Planned)

### Phase 7: Security and API Hardening
**Goal**: Remove the most immediate production blockers at the API boundary: anonymous exposure, weak health semantics, loose contracts, and unvalidated fix success claims.
**Depends on**: Phase 6
**Plans**: 1 plan
**Requirements**: SEC-01, SEC-02, API-01, API-02, API-03

Success criteria:
1. API access control is explicit and configurable for non-local deployments.
2. Liveness, readiness, and capability/health semantics are distinct and documented.
3. `/check`, `/fix`, `/quality`, and `/check-and-fix` use strict typed contracts.
4. Fix endpoints only report success after shared-pipeline revalidation.

### Phase 8: Engine Consolidation and Shared Contracts
**Goal**: Make the static pipeline authoritative, reduce legacy detection debt, and stabilize internal contracts across API, CLI, and Streamlit.
**Depends on**: Phase 7
**Plans**: 1 plan
**Requirements**: ARCH-01, ARCH-02, ARCH-03

Success criteria:
1. Dead legacy branches are removed from `src/error_engine.py` and `src/multi_error_detector.py`.
2. Shared detection payloads are modeled with typed internal contracts.
3. Entry points use a shared orchestration path instead of duplicating result-shaping behavior.

### Phase 9: Detection Assurance and ML Verification
**Goal**: Raise fidelity and confidence for non-Python languages while proving healthy-mode ML readiness and measurable performance baselines.
**Depends on**: Phase 8
**Plans**: 1 plan
**Requirements**: REL-01, REL-02, REL-03

Success criteria:
1. Compiler/LSP adapter seams exist for Java, C, C++, and JavaScript with fallback preserved.
2. CI can prove ML healthy-mode load in a compatible environment.
3. Accuracy and latency baselines exist for the shared engine and are reusable in regressions.

### Phase 10: Delivery, CI, and Observability
**Goal**: Make the repo runnable and supportable across local, staging, and production environments with enforceable quality gates, operational visibility, and runtime scale readiness.
**Depends on**: Phase 7
**Plans**: 1 plan
**Requirements**: OPS-01, OPS-02, OPS-03, OPS-04, PERF-01, PERF-02, PERF-03

Success criteria:
1. Container and environment baselines exist for deployment and local verification.
2. CI enforces lint, type, tests, coverage, and dependency/security checks.
3. API and engine paths emit structured logs, tracing hooks, and alert-friendly signals.
4. Worker/isolation, prewarm/cache, and load/perf smoke paths are designed and validated.

### Phase 11: UX and Fix Workflow Upgrades
**Goal**: Improve student-facing trust and usability by reducing noisy recomputation, modernizing analysis quality signals, and making evidence, warnings, and fix previews clearer.
**Depends on**: Phase 8, Phase 10
**Plans**: 1 plan
**Requirements**: UX-01, UX-02, QUAL-01

Success criteria:
1. Streamlit avoids unnecessary full reruns for repeated analysis actions.
2. Confidence, evidence, and degraded-mode information are visible in the UI.
3. Fix previews are diffed and validated before being presented as safe to apply.
4. Quality scoring is language-aware enough to be credible for JavaScript and non-Python code.

### Phase 12: Product Foundations and Commercial Readiness
**Goal**: Add persistence and product scaffolding so OmniSyntax can evolve into a classroom or beta offering without redoing platform fundamentals later.
**Depends on**: Phase 10, Phase 11
**Plans**: 1 plan
**Requirements**: PROD-01, PROD-02

Success criteria:
1. Saved analyses and recent history have a persistence foundation.
2. Lightweight analytics events can be captured for reliability and retention work.
3. Tenant, quota, and billing readiness is documented and minimally scaffolded.

### Phase 13: Project-Mode and Educator Feedback Workflows
**Goal**: Extend OmniSyntax beyond single-snippet use with multi-file analysis, explicit feedback capture, and lightweight educator review workflows.
**Depends on**: Phase 12
**Plans**: 1 plan
**Requirements**: PROD-03, PROD-04, EDU-01

Success criteria:
1. Users can submit and analyze multi-file or project-mode inputs.
2. The product captures explicit user feedback on analysis quality and fix usefulness.
3. Educators can review saved analyses and attach rubric-style notes or feedback artifacts.
## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Detection Reliability | v1.0 | 2/2 | ✅ Complete | 2026-03-27 |
| 2. Diagnostics and Autofix Quality | v1.0 | 2/2 | ✅ Complete | 2026-03-27 |
| 3. Runtime Health and ML Recovery | v1.0 | 3/3 | ✅ Complete | 2026-03-27 |
| 4. QA Hardening and Release Readiness | v1.0 | 2/2 | ✅ Complete | 2026-03-27 |
| 5. Cross-Language Reliability Hardening | v1.0 | 4/4 | ✅ Complete | 2026-03-27 |
| 6. Python and Java Reliability Refinement | v1.1 | 2/2 | Complete | 2026-04-11 |
| 7. Security and API Hardening | v1.2 | 0/1 | Planned | - |
| 8. Engine Consolidation and Shared Contracts | v1.2 | 0/1 | Planned | - |
| 9. Detection Assurance and ML Verification | v1.2 | 0/1 | Planned | - |
| 10. Delivery, CI, and Observability | v1.2 | 0/1 | Planned | - |
| 11. UX and Fix Workflow Upgrades | v1.2 | 0/1 | Planned | - |
| 12. Product Foundations and Commercial Readiness | v1.2 | 0/1 | Planned | - |
| 13. Project-Mode and Educator Feedback Workflows | v1.2 | 0/1 | Planned | - |


