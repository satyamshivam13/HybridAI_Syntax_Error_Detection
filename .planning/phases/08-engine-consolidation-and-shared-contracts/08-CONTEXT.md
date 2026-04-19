# Phase 08: engine-consolidation-and-shared-contracts - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the shared analysis path easier to reason about by removing dead legacy branches, introducing typed result contracts, and reducing entry-point duplication.

</domain>

<decisions>
## Implementation Decisions

### Authoritative engine
- **D-01:** `src/static_pipeline.py` is the authoritative shared analysis path for current and future work.
- **D-02:** `src/error_engine.py` and `src/multi_error_detector.py` should stop carrying unreachable legacy logic once parity is proven.

### Shared contracts
- **D-03:** Replace dict soup at internal boundaries with typed contracts while preserving the current external JSON surface where needed.
- **D-04:** API, CLI, and Streamlit should depend on one shared orchestration layer instead of each shaping results independently.

### Safety rails
- **D-05:** Legacy cleanup is only acceptable if parity tests lock the repaired behavior before and after extraction.

### the agent's Discretion
- Whether typed contracts are dataclasses, TypedDicts, or Pydantic internal models.
- Where the shared orchestration layer lives as long as it clearly reduces boundary duplication.

</decisions>

<canonical_refs>
## Canonical References

### Planning
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/08-engine-consolidation-and-shared-contracts/08-CONTEXT.md`

### Engine and parity surfaces
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONCERNS.md`
- `src/static_pipeline.py`
- `src/error_engine.py`
- `src/multi_error_detector.py`
- `api.py`
- `cli.py`
- `app.py`
- `tests/test_api_and_regressions.py`
- `tests/test_streamlit_parity.py`

</canonical_refs>

<specifics>
## Specific Ideas

- Remove dead code after parity is locked, not before.
- Keep the repo as a modular monolith; the work is boundary cleanup, not service decomposition.
- Use typed contracts to reduce mutation-heavy bugs and drift between entry points.

</specifics>

<deferred>
## Deferred Ideas

- Splitting the API, UI, and engine into separate services.
- Full compiler replacement inside this phase.

</deferred>

---

*Phase: 08-engine-consolidation-and-shared-contracts*
*Context gathered: 2026-04-19*
