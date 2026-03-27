# Phase 05: Cross-Language Reliability Hardening - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** User-provided phase scope plus current roadmap, QA report, and resolved ML debug findings

<domain>
## Phase Boundary

Phase 5 hardens OmniSyntax reliability for `C`, `Java`, and `JavaScript` across the shared detection engine and all user-facing entry points. This phase should consolidate the already-started ML compatibility recovery work, strengthen rule/parser fallback behavior, improve line and column localization, improve tutoring explanations, expand regression coverage, and verify consistent healthy/degraded behavior across API, CLI, and Streamlit.

The phase should treat both healthy mode and degraded mode as first-class supported states. Work in this phase should close the gap between the placeholder roadmap entry and the concrete QA/debug findings already produced in the repo.

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- Restore and preserve ML bundle compatibility using the current metadata-aware bundle approach already landed in the repo.
- Keep strong rule-based fallback for non-Python languages even when ML is healthy.
- Focus language-specific reliability work on `C`, `Java`, and `JavaScript`.
- Improve exact line and column localization for non-Python findings.
- Improve tutor/explainer output so detected issues are more actionable for students.
- Expand automated regression coverage for the bugs already found during QA.
- Verify API, CLI, and Streamlit behavior in both degraded and healthy modes.
- Use the resolved ML debug session and the QA report as source-of-truth evidence for planning.

### The Agent's Discretion
- How many plans are needed and how they should be grouped into execution waves.
- Whether parser-grade work in this phase is limited to heuristics/refactors or includes deeper parser integration groundwork.
- Whether phase work should include roadmap/requirements cleanup for earlier overlapping phases.
- Exact test grouping and verification command breakdown.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product and Planning
- `.planning/PROJECT.md` - product context and current reliability priorities
- `.planning/ROADMAP.md` - current phase ordering and placeholder Phase 5 entry
- `.planning/STATE.md` - current project status and roadmap evolution
- `.planning/REQUIREMENTS.md` - current v1 requirements and traceability

### Codebase Maps
- `.planning/codebase/ARCHITECTURE.md` - shared engine architecture and entry points
- `.planning/codebase/CONCERNS.md` - known fragility, ML coupling, and test gaps
- `.planning/codebase/TESTING.md` - current test and smoke patterns

### QA and Debug Evidence
- `docs/QA_REPORT_2026-03-27.md` - detailed C/Java/JavaScript findings, fixes, and recommendations
- `.planning/debug/resolved/ml-model-bundle-load-failure.md` - resolved ML compatibility investigation and verification

### Runtime and Detection Code
- `src/error_engine.py` - primary hybrid detector and non-Python rule logic
- `src/multi_error_detector.py` - multi-issue aggregation path
- `src/ml_engine.py` - model status and compatibility handling
- `src/tutor_explainer.py` - explanation layer
- `api.py` - health and API orchestration
- `cli.py` - terminal UX
- `app.py` - Streamlit UX

### Verification Targets
- `tests/test_api_and_regressions.py` - API and ML-status regression coverage
- `tests/test_c_java_js_regressions.py` - cross-language regression coverage
- `tests/test_script_smoke.py` - smoke-script behavior

</canonical_refs>

<specifics>
## Specific Ideas

- Ensure healthy mode remains stable after the regenerated model bundle and `bundle_metadata.json`.
- Preserve the rule-engine gains already made for `MissingDelimiter`, `UnmatchedBracket`, `UnclosedString`, `DivisionByZero`, `MissingInclude`, `MissingImport`, `TypeMismatch`, `UndeclaredIdentifier`, `InfiniteLoop`, `UnreachableCode`, and `DuplicateDefinition`.
- Continue improving malformed-input suppression so primary issues stay prominent.
- Make user-facing outputs consistent in JSON responses, CLI formatting, and Streamlit displays.
- Use QA evidence to prioritize `C` first, then `JavaScript`, then `Java`.

</specifics>

<deferred>
## Deferred Ideas

- New language support outside the current supported set
- Full compiler replacement or full parser-backed architecture for every language
- Hosted SaaS or classroom-management features

</deferred>

---

*Phase: 05-cross-language-reliability-hardening*
*Context gathered: 2026-03-27 via explicit planning prompt*
