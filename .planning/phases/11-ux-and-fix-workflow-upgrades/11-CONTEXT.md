# Phase 11: ux-and-fix-workflow-upgrades - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Improve student-facing trust and usability by reducing noisy recomputation, surfacing stronger evidence, and making fix previews clear and validated.

</domain>

<decisions>
## Implementation Decisions

### Analysis UX
- **D-01:** Streamlit should not recompute every expensive analysis path on every minor interaction when cached or staged results can be reused safely.
- **D-02:** Confidence, evidence, and degraded-mode signals should be visible in the UI, not buried in backend payloads alone.
- **D-05:** `src/quality_analyzer.py` needs language-aware scoring that is credible for JavaScript and non-Python code.

### Fix UX
- **D-03:** Users need diffed, validated fix previews instead of optimistic "automatic fix applied" language.
- **D-04:** Fix trust is downstream of the Phase 7 revalidation contract; the UI should present that distinction clearly.

### the agent's Discretion
- Exact caching and state-management approach as long as it fits Streamlit idioms and keeps behavior stable.
- How much evidence detail to show by default versus in expandable detail panels.

</decisions>

<canonical_refs>
## Canonical References

### Planning
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/phases/11-ux-and-fix-workflow-upgrades/11-CONTEXT.md`

### UX surfaces
- `app.py`
- `src/static_pipeline.py`
- `src/auto_fix.py`
- `tests/test_streamlit_parity.py`
- `.planning/codebase/TESTING.md`

</canonical_refs>

<specifics>
## Specific Ideas

- Treat degraded-mode messaging as a user-trust feature, not a side warning.
- Show evidence without turning the app into a debugging console.
- Use fix diffs to separate "suggestion" from "validated improvement."
- The quality score should stop looking like a toy metric before it is surfaced more prominently.

</specifics>

<deferred>
## Deferred Ideas

- Full frontend rewrite away from Streamlit.
- Teacher dashboards and deep collaboration workflows.

</deferred>

---

*Phase: 11-ux-and-fix-workflow-upgrades*
*Context gathered: 2026-04-19*
