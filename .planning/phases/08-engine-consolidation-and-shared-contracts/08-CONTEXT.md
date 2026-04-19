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
- **D-03:** Keep the internal typed detection contract close to `src/static_pipeline.py` using the existing dataclass model, rather than introducing a separate public-facing contract layer for this phase.
- **D-04:** Preserve the current external JSON surface while replacing internal dict mutation with typed internal objects and a thin boundary adapter.
- **D-05:** API, CLI, and Streamlit should depend on one shared orchestration helper so result shaping stays aligned instead of drifting independently.

### Safety rails
- **D-06:** Legacy cleanup is only acceptable after parity tests lock the repaired behavior before and after extraction.
- **D-07:** Dead code should be removed aggressively once parity is proven; keep only minimal compatibility shims where tests or external behavior still require them.

### the agent's Discretion
- Exact module name and location for the shared orchestration helper, as long as all three entry points use it.
- Whether the helper lives beside `static_pipeline.py` or as a small adjacent adapter module.

</decisions>

<specifics>
## Specific Ideas

- Remove dead code after parity is locked, not before.
- Keep the repo as a modular monolith; the work is boundary cleanup, not service decomposition.
- Use typed contracts to reduce mutation-heavy bugs and drift between entry points.

</specifics>

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
- `.planning/codebase/TESTING.md`
- `src/static_pipeline.py`
- `src/error_engine.py`
- `src/multi_error_detector.py`
- `src/__init__.py`
- `api.py`
- `cli.py`
- `app.py`
- `tests/test_api_and_regressions.py`
- `tests/test_streamlit_parity.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `IRProgram`, `IRStatement`, `SymbolTable`, `AnalysisIssue`, and related dataclasses in `src/static_pipeline.py`: already provide a typed internal model that can be reused instead of inventing a separate contract.
- `detect_errors` and `detect_all_errors`: existing cross-entry analysis functions that can anchor the shared orchestration helper.
- `tests/test_api_and_regressions.py` and `tests/test_streamlit_parity.py`: existing parity/regression surfaces that can lock contract changes.

### Established Patterns
- `src/static_pipeline.py` already uses typed dataclasses for the analysis core, which fits the plan to keep the authoritative engine and internal contract together.
- `api.py`, `cli.py`, and `app.py` currently each shape results at the edge, so a shared helper is the cleanest way to reduce drift.
- `src/error_engine.py` and `src/multi_error_detector.py` still contain compatibility logic, so cleanup must remain parity-gated.

### Integration Points
- `src/static_pipeline.py` for the authoritative engine and typed internal result model.
- `src/error_engine.py` and `src/multi_error_detector.py` for legacy-path pruning.
- `api.py`, `cli.py`, and `app.py` for shared orchestration and final presentation.
- `src/__init__.py` for any export changes needed to keep entry points stable.

</code_context>

<deferred>
## Deferred Ideas

- Splitting the API, UI, and engine into separate services.
- Full compiler replacement inside this phase.

</deferred>

---

*Phase: 08-engine-consolidation-and-shared-contracts*
*Context gathered: 2026-04-19*
