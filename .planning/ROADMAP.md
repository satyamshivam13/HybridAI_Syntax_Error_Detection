# Roadmap: OmniSyntax

## Overview

This roadmap focuses on stabilizing OmniSyntax as a dependable educational code-analysis tool in a brownfield codebase. The near-term path is to harden detection quality for C, Java, and JavaScript, improve diagnostic usefulness across all entry points, restore trustworthy ML-assisted behavior where possible, and then lock those gains in with stronger QA and release checks.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions if new reliability issues appear

- [ ] **Phase 1: Detection Reliability** - Strengthen fallback analysis and reduce false negatives for C, Java, and JavaScript.
- [ ] **Phase 2: Diagnostics and Autofix Quality** - Improve localization, explanations, and student-facing consistency.
- [ ] **Phase 3: Runtime Health and ML Recovery** - Make degraded mode safer and restore ML compatibility where feasible.
- [ ] **Phase 4: QA Hardening and Release Readiness** - Expand verification, docs, and repeatable evidence for future changes.
- [ ] **Phase 5: Cross-Language Reliability Hardening** - Consolidate ML recovery, fallback detection, diagnostics, explanations, and multi-entry-point verification.

## Phase Details

### Phase 1: Detection Reliability
**Goal**: Make non-Python detection accurate enough to be trustworthy when the ML path is unavailable.
**Depends on**: Nothing (first phase)
**Requirements**: [DET-01, DET-02, DET-03, DET-04]
**Success Criteria** (what must be TRUE):
  1. User can submit representative C, Java, and JavaScript failure cases and receive useful detection in degraded mode.
  2. False negatives already found during QA are covered by regressions and stay fixed.
  3. String-literal edge cases no longer generate misleading bracket or delimiter noise.
**Plans**: 2 plans

Plans:
- [ ] 01-01: Expand and normalize rule-based non-Python detection
- [ ] 01-02: Add regression tests for known C, Java, and JavaScript failures

### Phase 2: Diagnostics and Autofix Quality
**Goal**: Make reported issues easier for students to act on across API, CLI, and Streamlit.
**Depends on**: Phase 1
**Requirements**: [DIAG-01, DIAG-02, DIAG-03, DIAG-04, FIX-01, FIX-02, FIX-03]
**Success Criteria** (what must be TRUE):
  1. User can see exact line information, and column information where rule-based localization supports it.
  2. User receives explanations that identify the problem and the next correction step.
  3. CLI, API, and Streamlit present consistent labels, warnings, and fix guidance.
**Plans**: 2 plans

Plans:
- [ ] 02-01: Improve issue localization and explanation quality
- [ ] 02-02: Align autofix and presentation behavior across entry points

### Phase 3: Runtime Health and ML Recovery
**Goal**: Stabilize runtime behavior in both healthy and degraded mode, and recover ML compatibility where justified.
**Depends on**: Phase 2
**Requirements**: [OPS-01, OPS-02, OPS-03]
**Success Criteria** (what must be TRUE):
  1. User can rely on `/health` and runtime warnings to understand whether ML assistance is active.
  2. API, CLI, and Streamlit start cleanly with documented setup and graceful degraded-mode behavior.
  3. The model-loading path is either restored or replaced with a clearly supported compatibility strategy.
**Plans**: 3 plans

Plans:
- [ ] 03-01: Audit and repair model artifact compatibility or fallback loading
- [ ] 03-02: Harden startup, configuration, and degraded-mode messaging
- [ ] 03-03: Verify runtime behavior across API, CLI, Streamlit, and scripts

### Phase 4: QA Hardening and Release Readiness
**Goal**: Make OmniSyntax changes safer to ship by strengthening verification and project documentation.
**Depends on**: Phase 3
**Requirements**: [QA-01, QA-02, QA-03]
**Success Criteria** (what must be TRUE):
  1. User can run automated tests and smoke checks that cover the major failure modes found so far.
  2. Evaluation and reporting scripts either run successfully or degrade safely with clear diagnostics.
  3. Documentation captures open risks, verification evidence, and known limitations for future contributors.
**Plans**: 2 plans

Plans:
- [ ] 04-01: Expand automated verification and smoke coverage
- [ ] 04-02: Refresh QA reports, docs, and release checklists

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Detection Reliability | 0/2 | Not started | - |
| 2. Diagnostics and Autofix Quality | 0/2 | Not started | - |
| 3. Runtime Health and ML Recovery | 0/3 | Not started | - |
| 4. QA Hardening and Release Readiness | 0/2 | Not started | - |
| 5. Cross-Language Reliability Hardening | 0/4 | Not started | - |

### Phase 5: Cross-Language Reliability Hardening

**Goal:** Make C, Java, and JavaScript analysis trustworthy across healthy and degraded runtime states by hardening shared detection contracts, actionable explanations, and API/CLI/Streamlit parity.
**Requirements**: [DET-02, DET-03, DET-04, DIAG-01, DIAG-02, DIAG-03, DIAG-04, FIX-02, OPS-01, OPS-03, QA-01, QA-02, QA-03]
**Depends on:** Phase 4
**Plans:** 4 plans

Plans:
- [ ] 05-01-PLAN.md - Reconcile runtime and documentation assumptions with the verified ML health contract
- [ ] 05-02-PLAN.md - Harden shared C, Java, and JavaScript detection plus localization
- [ ] 05-03-PLAN.md - Align explanations, degraded warnings, and entry-point wording
- [ ] 05-04-PLAN.md - Expand startup and smoke verification, then collect sign-off evidence
