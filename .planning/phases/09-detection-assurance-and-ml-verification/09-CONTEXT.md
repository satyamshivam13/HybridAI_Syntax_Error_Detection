# Phase 09: detection-assurance-and-ml-verification - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Improve confidence in OmniSyntax's C-like language detection path and ML health by adding adapter seams, healthy-mode verification, and measurable performance baselines.

</domain>

<decisions>
## Implementation Decisions

### Fidelity path
- **D-01:** Java, C, C++, and JavaScript need an adapter seam for compiler/LSP-backed validation; the existing heuristic path remains the fallback.
- **D-02:** The adapter work should be staged so the repo can adopt real validation incrementally instead of blocking on full integration for every language at once.

### ML assurance
- **D-03:** Healthy-mode ML verification must run automatically in CI or a deterministic verification job, not just on a maintainer machine.
- **D-04:** Model artifact reproducibility and version compatibility should be explicit, testable, and benchmarked.

### Measurement
- **D-05:** Accuracy and latency baselines should be recorded for the shared engine so future regressions are measurable.

### the agent's Discretion
- Which language adapters are implemented first as long as Java, C, C++, and JavaScript all have a clear path.
- Whether benchmarks live in pytest, scripts, or a dedicated validation harness.

</decisions>

<canonical_refs>
## Canonical References

### Planning and requirements
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/phases/09-detection-assurance-and-ml-verification/09-CONTEXT.md`

### Engine, ML, and validation surfaces
- `.planning/codebase/CONCERNS.md`
- `.planning/codebase/TESTING.md`
- `src/static_pipeline.py`
- `src/ml_engine.py`
- `models/bundle_metadata.json`
- `scripts/retrain_model.py`
- `scripts/production_validation.py`
- `tests/test_static_pipeline_validation.py`

</canonical_refs>

<specifics>
## Specific Ideas

- Keep degraded-mode correctness sacred while adding stronger healthy-mode proof.
- Start with adapter interfaces and one or two concrete integrations if full coverage is too large for a single pass.
- Record baseline latency before later UI and product work stacks more demand onto the engine.

</specifics>

<deferred>
## Deferred Ideas

- Replacing all heuristics with full compiler execution in one milestone.
- Large-scale ML architecture replacement.

</deferred>

---

*Phase: 09-detection-assurance-and-ml-verification*
*Context gathered: 2026-04-19*
