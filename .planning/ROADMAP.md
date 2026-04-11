# Roadmap: OmniSyntax

## Milestones

- ✅ **v1.0 Cross-Language Reliability** — Phases 1–5 (shipped 2026-03-27) — [archive](milestones/v1.0-ROADMAP.md)
- 📋 **v1.1 Reliability Refinement** — Planned

## Phases

<details>
<summary>✅ v1.0 Cross-Language Reliability (Phases 1–5) — SHIPPED 2026-03-27</summary>

- [x] Phase 1: Detection Reliability (2/2 plans) — completed 2026-03-27
- [x] Phase 2: Diagnostics and Autofix Quality (2/2 plans) — completed 2026-03-27
- [x] Phase 3: Runtime Health and ML Recovery (3/3 plans) — completed 2026-03-27
- [x] Phase 4: QA Hardening and Release Readiness (2/2 plans) — completed 2026-03-27
- [x] Phase 5: Cross-Language Reliability Hardening (4/4 plans) — completed 2026-03-27

</details>

### v1.1 (Planned)

### Phase 6: Python and Java Reliability Refinement
**Goal**: Close the remaining Python and Java reliability gaps without regressing the shared API, CLI, and Streamlit contracts established in v1.0.
**Depends on**: Phase 5
**Plans**: 2 plans

Plans:
- [x] 06-01: Merge Python semantic ML into all-errors and stabilize Java mixed-error precedence
- [x] 06-02: Keep autofix guidance conservative while tightening location-aware messaging and regression coverage

**Outcome:** Python all-errors mode merges confident semantic ML findings as a separate grouped result. IndentationError and UnclosedString stay suggestion-only but gain exact location-aware guidance. Java suppresses the known mixed-case false positive only when context proves it.
## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Detection Reliability | v1.0 | 2/2 | ✅ Complete | 2026-03-27 |
| 2. Diagnostics and Autofix Quality | v1.0 | 2/2 | ✅ Complete | 2026-03-27 |
| 3. Runtime Health and ML Recovery | v1.0 | 3/3 | ✅ Complete | 2026-03-27 |
| 4. QA Hardening and Release Readiness | v1.0 | 2/2 | ✅ Complete | 2026-03-27 |
| 5. Cross-Language Reliability Hardening | v1.0 | 4/4 | ✅ Complete | 2026-03-27 |
| 6. Python and Java Reliability Refinement | v1.1 | 2/2 | Complete | 2026-04-11 |


