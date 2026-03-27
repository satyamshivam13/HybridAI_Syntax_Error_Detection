# Requirements: OmniSyntax

**Defined:** 2026-03-27
**Core Value:** Students should get accurate, actionable code-error feedback even when the ML layer is unavailable.

## v1 Requirements

### Detection

- [ ] **DET-01**: User can submit Python, Java, C, C++, or JavaScript code and receive a primary analysis result.
- [ ] **DET-02**: User receives useful C, Java, and JavaScript issue detection even when ML models are unavailable.
- [ ] **DET-03**: User can see multiple issues for a snippet when the code contains more than one detectable problem.
- [ ] **DET-04**: User does not receive bracket or delimiter false positives caused only by characters inside string literals.

### Diagnostics

- [ ] **DIAG-01**: User receives exact line information for detected errors whenever the engine can localize the issue.
- [ ] **DIAG-02**: User receives column information for rule-based C, Java, and JavaScript findings when available.
- [ ] **DIAG-03**: User receives an explanation that states what is wrong and what to fix next.
- [ ] **DIAG-04**: User sees degraded-mode warnings when semantic ML analysis is unavailable.

### Autofix and UX

- [ ] **FIX-01**: User can request an autofix for supported syntax issues without unrelated code mutation.
- [ ] **FIX-02**: User gets consistent issue labels and wording across API, CLI, and Streamlit entry points.
- [ ] **FIX-03**: User can override language selection when filename-based detection would be misleading.

### Reliability and Operations

- [ ] **OPS-01**: API `/health` accurately reports healthy versus degraded runtime state.
- [ ] **OPS-02**: API payload limits and rate limits are enforced consistently across endpoints.
- [ ] **OPS-03**: CLI, API, and Streamlit startup paths work on a clean local environment with documented setup.

### QA and Evaluation

- [ ] **QA-01**: Automated tests cover known false negatives and regressions for C, Java, and JavaScript.
- [ ] **QA-02**: Smoke scripts fail gracefully when ML artifacts are unavailable instead of crashing.
- [ ] **QA-03**: Documentation and reports clearly describe current limitations, fixes, and verification evidence.

## v2 Requirements

### Advanced Analysis

- **ADV-01**: User receives parser-grade diagnostics for all supported non-Python languages.
- **ADV-02**: User receives richer semantic tutoring backed by healthy ML or alternative models.
- **ADV-03**: Evaluations can compare rule-only versus ML-assisted accuracy automatically across datasets.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Support for new programming languages | Current work is about reliability in existing supported languages |
| Full IDE or LSP integration | Useful later, but not needed to stabilize the current product |
| User accounts, classrooms, or cloud collaboration | Not represented in the repo and outside the current QA-driven scope |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DET-01 | Phase 1 | Pending |
| DET-02 | Phase 1 | Pending |
| DET-03 | Phase 1 | Pending |
| DET-04 | Phase 1 | Pending |
| DIAG-01 | Phase 2 | Pending |
| DIAG-02 | Phase 2 | Pending |
| DIAG-03 | Phase 2 | Pending |
| DIAG-04 | Phase 2 | Pending |
| FIX-01 | Phase 2 | Pending |
| FIX-02 | Phase 2 | Pending |
| FIX-03 | Phase 2 | Pending |
| OPS-01 | Phase 3 | Pending |
| OPS-02 | Phase 3 | Pending |
| OPS-03 | Phase 3 | Pending |
| QA-01 | Phase 4 | Pending |
| QA-02 | Phase 4 | Pending |
| QA-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-27*
*Last updated: 2026-03-27 after initial definition*
