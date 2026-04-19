---
phase: 08-engine-consolidation-and-shared-contracts
plan: 01
subsystem: core
tags: [static-pipeline, dataclasses, shared-contract, fastapi, cli, streamlit, pytest]
requires:
  - phase: 07-security-and-api-hardening
    provides: production-safe API boundary controls, split health semantics, and verification-aware fix responses
provides:
  - authoritative typed `DetectionAnalysis` contract in `src/static_pipeline.py`
  - shared `analyze_source` orchestration helper reused by API, CLI, and Streamlit
  - compatibility-wrapper cleanup in `src/error_engine.py` and `src/multi_error_detector.py`
  - parity coverage proving the shared contract and entry-point routing stay aligned
affects: [09-detection-assurance-and-ml-verification, 10-delivery-ci-and-observability, 11-ux-and-fix-workflow-upgrades]
tech-stack:
  added: [dataclasses]
  patterns: [shared-analysis-contract, pipeline-adapter-methods, parity-gated-legacy-trim]
key-files:
  created:
    - .planning/phases/08-engine-consolidation-and-shared-contracts/08-01-SUMMARY.md
  modified:
    - src/static_pipeline.py
    - src/error_engine.py
    - src/multi_error_detector.py
    - src/__init__.py
    - api.py
    - cli.py
    - app.py
    - tests/test_api_and_regressions.py
    - tests/test_streamlit_parity.py
    - .planning/STATE.md
key-decisions:
  - "Keep src/static_pipeline.py authoritative and wrap it in a typed shared analysis contract instead of introducing a separate public contract layer."
  - "Expose a single shared orchestration helper and route API, CLI, and Streamlit through it."
  - "Remove dead legacy code only after parity tests confirm the cleaned behavior is stable."
  - "Preserve compatibility wrappers as thin adapters rather than removing them outright."
patterns-established:
  - "Analysis helpers now return a typed dataclass contract with adapter methods for single and grouped outputs."
  - "Entry points consume shared analysis state instead of reshaping independent dicts."
  - "Legacy wrapper cleanup is gated by parity tests before dead branches are removed."
requirements-completed: [ARCH-01, ARCH-02, ARCH-03]
duration: 44 min
completed: 2026-04-19
---

# Phase 08 Plan 01: Engine Consolidation and Shared Contracts Summary

**Typed static-pipeline analysis, shared orchestration, and parity-verified wrapper cleanup now keep API, CLI, and Streamlit aligned on one authoritative detection boundary.**

## Performance

- **Duration:** 44 min
- **Started:** 2026-04-19T15:15:00+05:30
- **Completed:** 2026-04-19T15:58:59+05:30
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- Introduced `DetectionAnalysis` in `src/static_pipeline.py` as the typed internal contract for shared detection results.
- Added `analyze_source(...)` and reused it through API, CLI, and Streamlit so entry points no longer shape detection payloads independently.
- Trimmed dead code from `src/error_engine.py` and `src/multi_error_detector.py` while preserving compatibility wrappers.
- Added regression coverage for exportability, grouped Streamlit output, degraded-mode warnings, and the legacy multi-error wrapper.

## Task Commits

Each task was committed atomically:

1. **Task 1: Make the static pipeline the explicit source of truth** - `69ddeef` (refactor)
2. **Task 2: Introduce typed detection result contracts** - `8f95001` (feat)

## Files Created/Modified
- `src/static_pipeline.py` - Added the shared `DetectionAnalysis` contract and `analyze_source` helper.
- `src/error_engine.py` - Removed unreachable legacy branches while keeping the compatibility wrapper.
- `src/multi_error_detector.py` - Removed unreachable legacy branches while keeping the compatibility wrapper.
- `src/__init__.py` - Re-exported the shared analysis contract and helper.
- `api.py` - Routed verification and response construction through the shared analysis helper.
- `cli.py` - Routed single-error and grouped output through the shared analysis helper.
- `app.py` - Routed live Streamlit analysis through the shared analysis helper.
- `tests/test_api_and_regressions.py` - Added a contract-export regression for `src` package exports.
- `tests/test_streamlit_parity.py` - Switched parity coverage to the shared pipeline helper and updated degraded-mode patching.
- `.planning/STATE.md` - Updated execution state for the completed phase.

## Decisions Made
- Keep `src/static_pipeline.py` authoritative and close the typed contract to that module.
- Use one shared orchestration helper for API, CLI, and Streamlit instead of parallel result-shaping paths.
- Remove dead legacy code only after parity tests pass.
- Preserve thin compatibility wrappers so legacy entry points remain stable.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- The new Streamlit parity test initially targeted the old multi-error wrapper; it was retargeted to the shared pipeline helper so the test matched the new execution path.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 08 is complete and the shared analysis boundary is stable enough for Phase 09 reliability and assurance work.
- The next phase can build on a single typed detection contract instead of reconciling entry-point-specific result shapes.

## Self-Check: PASSED

---
*Phase: 08-engine-consolidation-and-shared-contracts*
*Completed: 2026-04-19*
