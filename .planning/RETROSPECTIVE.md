# OmniSyntax Retrospective

## Milestone: v1.0 — Cross-Language Reliability

**Shipped:** 2026-03-27
**Phases:** 5 | **Plans:** 10

### What Was Built

1. Expanded rule engine with 11+ C/Java/JavaScript patterns for degraded-mode detection
2. Line and column localization for all non-Python rule-based findings
3. ML bundle restored with metadata-aware scikit-learn==1.7.2 compatibility contract
4. Degraded-mode warnings propagated uniformly across API, CLI, and Streamlit
5. Smoke test suite expanded to 13 tests; full test suite at 153 passed

### What Worked

- **Brownfield-first approach**: Starting with codebase mapping before planning let each phase build on verified understanding rather than assumptions
- **Degraded-mode as first-class**: Treating fallback correctness as a real requirement forced complete rule coverage instead of "good enough" heuristics
- **Phase 05 consolidation**: The cross-cutting final phase caught inter-entry-point gaps that phase-by-phase work would have missed
- **Regression anchoring**: Writing regression tests immediately after finding false negatives prevented drift across later phases

### What Was Inefficient

- ROADMAP.md and REQUIREMENTS.md traceability tables were not updated live during execution — required reconciliation at milestone completion
- Some auto-fix improvements were scoped to "suggestion" rather than actual code rewriting due to time constraints; this created known debt immediately
- `--all-errors` path and single-error ML path diverged at the architecture level without a clear bridge plan

### Patterns Established

- Phase SUMMARY.md format: outcome → key changes → verification → self-check
- Smoke test conventions: test both healthy and degraded states for every entry point
- Health contract: `/health` endpoint state is the ground truth; all downstream tests respect it

### Key Lessons

1. **Document the healthy/degraded contract explicitly at project start** — retrofitting this into docs cost extra time in Phases 03 and 05
2. **Auto-fix precision requires dedicated scope** — bundling it into diagnostics phases produces "works sometimes" fixes; it needs a full phase or explicit acceptance of known gaps
3. **Multi-error and single-error paths should share a common result shape** — the CLI crash found in this session proves the cost of divergence

### Cost Observations

- Sessions: Multiple (brownfield init + 5 phases over 63 days)
- Notable: ML compatibility investigation (Phase 03) was the highest-uncertainty work; frontloading it reduced risk for all subsequent phases

---

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Phases | 5 |
| Plans | 10 |
| Tests at ship | 153 passed |
| Days | 63 |
| Known gaps at ship | 4 |
