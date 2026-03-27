# Milestones

## v1.0 — Cross-Language Reliability

**Shipped:** 2026-03-27
**Phases:** 1–5 | **Plans:** 10 | **Timeline:** 2026-01-23 → 2026-03-27 (63 days)
**Files changed:** 156 | **Net LOC:** +27,487 / -86,909

### Key Accomplishments

1. Rule engine expanded with 11+ patterns for C, Java, and JavaScript in degraded mode — students get actionable output without ML
2. Line and column localization added to all C/Java/JavaScript rule-based findings
3. ML bundle restored with metadata-aware scikit-learn==1.7.2 compatibility contract; `/health` endpoint reflects true state
4. Degraded-mode warnings propagated uniformly across API, CLI, and Streamlit
5. Smoke suite expanded to 13 tests covering graceful degradation across all entry points
6. Full test suite: 153 passed, 1 skipped, 1 xfailed

### Known Gaps at Ship

- CLI `--all-errors` mode does not invoke ML classifier for Python semantic errors (DivisionByZero etc.)
- IndentationError auto-fix suggests rather than rewrites
- UnclosedString auto-fix appends quote at EOF instead of the original line
- Occasional false-positive UndeclaredIdentifier alongside TypeMismatch in Java

### Archive

- Roadmap: `.planning/milestones/v1.0-ROADMAP.md`
- Requirements: `.planning/milestones/v1.0-REQUIREMENTS.md`
- Phases: `.planning/milestones/v1.0-phases/`
