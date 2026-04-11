# Phase 06: python-and-java-reliability-refinement - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Close the remaining reliability gaps in Python and Java without regressing the shared API, CLI, and Streamlit contracts established in v1.0.

</domain>

<decisions>
## Implementation Decisions

### Python all-errors semantics
- **D-01:** Merge confident semantic ML findings into Python all-errors output even when rule-based issues already exist.
- **D-02:** Surface the ML result as its own grouped error entry in `errors` / `errors_by_type`, with confidence metadata preserved for downstream use.

### Autofix precision
- **D-03:** Keep `IndentationError` fixes suggestion-only for v1.1 rather than rewriting code automatically.
- **D-04:** Keep `UnclosedString` fixes suggestion-only for v1.1 rather than rewriting code automatically.
- **D-05:** Precision still matters for these fixes: the guidance should carry exact line/column context plus clearer wording.

### Java mixed-error precedence
- **D-06:** Suppress `UndeclaredIdentifier` only when declaration/type context proves it is a false positive; do not broad-suppress every mixed `TypeMismatch` case.

### Regression coverage
- **D-07:** Lock the repaired Python and Java scenarios with unit tests, API/CLI regressions, and Streamlit parity coverage.

### the agent's Discretion
- Exact phase wave breakdown and task ordering.
- Whether the new tests live in existing regression files or a dedicated phase-specific test module.
- Internal helper boundaries for the semantic merge and mixed-error suppression logic.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and milestone planning
- `.planning/PROJECT.md` — milestone goal, active requirements, and project-level constraints.
- `.planning/REQUIREMENTS.md` — v1.1 requirements, out-of-scope items, and traceability.
- `.planning/STATE.md` — current milestone status and session continuity.
- `.planning/ROADMAP.md` — planned Phase 06 scope and milestone placement.

### Codebase architecture and testing
- `.planning/codebase/ARCHITECTURE.md` — shared engine layers, entry-point flow, and integration points.
- `.planning/codebase/TESTING.md` — pytest patterns, smoke coverage, and current coverage gaps.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/multi_error_detector.py` — already groups multi-error output and exposes `degraded_mode` / `warnings`.
- `src/auto_fix.py` — already contains `fix_indentation()` and `fix_unclosed_quotes()` hooks that can be refined.
- `src/error_engine.py` — centralizes Python and Java detection, tutor messaging, and semantic precedence logic.
- `src/tutor_explainer.py` — already provides the user-facing explanations for the repaired error types.

### Established Patterns
- Regression tests assert exact `predicted_error`, issue counts, warning payloads, and degraded-mode flags.
- Streamlit parity is already tested with `streamlit.testing.v1.AppTest`, so the UI surface can be locked without adding a browser harness.
- Existing tests favor concrete snippets over abstract fixtures, which suits these reliability regressions.

### Integration Points
- `src/error_engine.py` — Python semantic merge behavior and Java false-positive suppression.
- `src/multi_error_detector.py` — grouped all-errors result shape for Python semantic findings.
- `src/auto_fix.py` — precision and message quality for `IndentationError` and `UnclosedString`.
- `tests/test_api_and_regressions.py`, `tests/test_c_java_js_regressions.py`, `tests/test_streamlit_parity.py`, `tests/test_multi_error_detector.py` — regression surfaces for the repaired cases.

</code_context>

<specifics>
## Specific Ideas

- The user wants the fixes to stay within the existing API, CLI, and Streamlit parity contract rather than introducing new behavior.
- For the autofix items, the emphasis is on clearer, location-aware guidance rather than aggressive automatic rewrites.
- Streamlit parity is in scope for the repaired cases, not just backend detection.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-python-and-java-reliability-refinement*
*Context gathered: 2026-04-11*
