# Codebase Concerns

**Analysis Date:** 2026-05-02

## Tech Debt

**ML artifact compatibility in `src/ml_engine.py`:**
- Issue: Runtime health depends on serialized pickle artifacts that are version-sensitive
- Why: The project ships trained artifacts instead of rebuilding or versioning them more robustly
- Impact: Semantic ML classification may be unavailable when the installed environment drifts away from the bundle metadata contract
- Fix approach: Keep bundle metadata authoritative, verify healthy-mode loading in CI, and treat degraded mode as the safe fallback

**Legacy logic still present in `src/error_engine.py`:**
- Issue: The file carries legacy/non-authoritative branches and long heuristic sections
- Why: Detection behavior evolved incrementally around existing bugs
- Impact: The module is harder to reason about and easier to regress
- Fix approach: Continue extracting helpers and remove dead paths once parity is proven by tests

## Known Bugs

**ML runtime may remain degraded on otherwise working installs:**
- Symptoms: `/health` returns `degraded`, semantic detection is skipped, evaluation scripts fall back or skip
- Trigger: Model bundle is incompatible with the installed environment or fallback files are incomplete
- Workaround: Use rule-based mode and pinned dependencies
- Root cause: Tight coupling between pickle artifacts and library versions
- Blocked by: Artifact refresh or compatibility redesign

**Explanation quality can still be generic for some non-Python issues:**
- Symptoms: Error type is correct but the explanation is shallow
- Trigger: Rule-based detection finds an issue with limited tutor-specific copy
- Workaround: Manual interpretation or code reading
- Root cause: Explanation templates do not yet cover every rule-based case

## Security Considerations

**Open API deployment:**
- Risk: Public deployments could be abused without an explicit access-control layer
- Current mitigation: payload-size checks, in-memory rate limiting, and configurable API key mode
- Recommendations: Keep auth or gateway controls enabled before exposing this service broadly

**User-submitted code handling:**
- Risk: Future execution-based analysis could become dangerous if code is ever run directly
- Current mitigation: Current detection is static analysis only
- Recommendations: Preserve static-only behavior unless sandboxing is added intentionally

## Performance Bottlenecks

**Cold model loading:**
- Problem: ML availability depends on loading multiple local artifacts at startup or on first use
- Measurement: Not benchmarked in-repo
- Cause: File I/O and deserialization overhead
- Improvement path: Preflight health checks, lazy loading with cached status, or model packaging improvements

**Evaluation scripts on large datasets:**
- Problem: Dataset and visualization scripts can become slow as artifact sizes grow
- Measurement: Not benchmarked in-repo
- Cause: pandas-heavy processing and filesystem-bound reporting
- Improvement path: Add sampling defaults and performance notes to scripts

## Fragile Areas

**`src/error_engine.py`:**
- Why fragile: It blends language routing, heuristics, ML gating, normalization, and explanation wiring
- Common failures: False positives, inconsistent locations, regressions after small heuristic edits
- Safe modification: Add or update regression tests first, then change one rule cluster at a time
- Test coverage: Good regression coverage exists, but edge-case heuristics still need expansion

**`src/multi_error_detector.py`:**
- Why fragile: Multi-issue reporting must stay consistent with the single-result engine
- Common failures: Duplicate issues, ordering drift, or mismatch between CLI/API expectations
- Safe modification: Keep shared normalization behavior aligned with `src/error_engine.py`
- Test coverage: Good targeted coverage, but future expansions should include ordering and dedupe checks

## Scaling Limits

**API rate limiting:**
- Current capacity: per-process in-memory throttle only
- Limit: Not suitable for distributed or multi-worker deployments
- Symptoms at limit: Inconsistent enforcement across workers
- Scaling path: Move rate limiting to a shared store or edge gateway if the service becomes multi-instance

## Dependencies at Risk

**`scikit-learn==1.7.2`:**
- Risk: Model compatibility is still tied to a versioned artifact contract
- Impact: Upgrades or environment drift can silently disable semantic ML behavior if the bundle metadata and runtime diverge
- Migration plan: Keep re-exporting models with the verified toolchain and preserve the bundle metadata contract

## Missing Critical Features

**Healthy-mode verification path:**
- Problem: The repo verifies degraded mode well, but healthy ML mode is harder to validate automatically
- Current workaround: Manual local environment alignment
- Blocks: Confident release of ML-assisted improvements
- Implementation complexity: Medium

## Test Coverage Gaps

**Model artifact regeneration and healthy-mode loading:**
- What's not tested: Rebuild and load path for a fresh compatible model bundle
- Risk: ML can stay broken while fallback tests continue passing
- Priority: High
- Difficulty to test: Requires deterministic artifact generation or checked-in fixtures

**Streamlit UI interaction flows:**
- What's not tested: User interactions inside the browser UI
- Risk: UI regressions may slip past backend-focused tests
- Priority: Medium
- Difficulty to test: Needs browser or UI automation tooling

---
*Concerns audit: 2026-03-27*
*Update as issues are fixed or new ones discovered*
