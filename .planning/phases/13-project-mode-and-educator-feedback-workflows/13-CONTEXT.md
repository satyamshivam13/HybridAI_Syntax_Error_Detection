# Phase 13: project-mode-and-educator-feedback-workflows - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend OmniSyntax beyond single-snippet use by supporting multi-file project analysis, explicit user feedback capture, and lightweight educator review workflows.

</domain>

<decisions>
## Implementation Decisions

### Project-mode analysis
- **D-01:** Users need a project-mode or multi-file analysis path instead of being limited to one snippet at a time.
- **D-02:** The implementation should build on the persistence foundation from Phase 12 rather than inventing a separate storage model.

### Feedback capture
- **D-03:** Users should be able to record whether an analysis or fix was useful so reliability work can use real-world signals.

### Educator workflows
- **D-04:** Educators need a lightweight review path for saved analyses and rubric-style notes, but this phase does not promise a full teacher dashboard.

### the agent's Discretion
- Exact packaging or upload model for project-mode inputs.
- How rubric notes are stored and displayed, as long as they are tied to persisted analyses.

</decisions>

<canonical_refs>
## Canonical References

### Planning
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/13-project-mode-and-educator-feedback-workflows/13-CONTEXT.md`

### Product surfaces
- `api.py`
- `app.py`
- `cli.py`
- `.planning/phases/12-product-foundations-and-commercial-readiness/12-01-PLAN.md`
- `.planning/codebase/ARCHITECTURE.md`

</canonical_refs>

<specifics>
## Specific Ideas

- Project-mode should start pragmatic: a small set of files, not an IDE clone.
- Feedback capture should help model and rule improvement, not just generate vanity metrics.
- Educator workflows should be artifact-centric and lightweight before any dashboard ambitions.

</specifics>

<deferred>
## Deferred Ideas

- Full teacher dashboards, grading pipelines, and classroom management.
- Large-scale collaborative code review features.

</deferred>

---

*Phase: 13-project-mode-and-educator-feedback-workflows*
*Context gathered: 2026-04-19*
