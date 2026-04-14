# Phase 05: Cross-Language Reliability Hardening - Research

**Researched:** 2026-03-27
**Domain:** Cross-language reliability hardening for the shared detection engine, ML bundle health, and entry-point parity
**Confidence:** HIGH

> Historical snapshot note (added 2026-04-14): This is a pre-execution research artifact. Any unchecked actions here reflect planning-time state and were later resolved during execution and milestone completion.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Restore and preserve ML bundle compatibility using the current metadata-aware bundle approach already landed in the repo.
- Keep strong rule-based fallback for non-Python languages even when ML is healthy.
- Focus language-specific reliability work on `C`, `Java`, and `JavaScript`.
- Improve exact line and column localization for non-Python findings.
- Improve tutor/explainer output so detected issues are more actionable for students.
- Expand automated regression coverage for the bugs already found during QA.
- Verify API, CLI, and Streamlit behavior in both degraded and healthy modes.
- Use the resolved ML debug session and the QA report as source-of-truth evidence for planning.

### Claude's Discretion
- How many plans are needed and how they should be grouped into execution waves.
- Whether parser-grade work in this phase is limited to heuristics/refactors or includes deeper parser integration groundwork.
- Whether phase work should include roadmap/requirements cleanup for earlier overlapping phases.
- Exact test grouping and verification command breakdown.

### Deferred Ideas (OUT OF SCOPE)
- New language support outside the current supported set
- Full compiler replacement or full parser-backed architecture for every language
- Hosted SaaS or classroom-management features
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DET-02 | User receives useful C, Java, and JavaScript issue detection even when ML models are unavailable. | Preserve `_collect_c_like_rule_based_issues()` as the authoritative fallback path and extend it via targeted helpers, not entry-point logic. |
| DET-03 | User can see multiple issues for a snippet when the code contains more than one detectable problem. | Keep `src/multi_error_detector.py` as a projection over the shared rule engine; add ordering/dedupe regressions as behavior expands. |
| DET-04 | User does not receive bracket or delimiter false positives caused only by characters inside string literals. | Reuse the existing comment/string stripping and cascading-noise suppression helpers; add more negative tests before heuristic edits. |
| DIAG-01 | User receives exact line information for detected errors whenever the engine can localize the issue. | Continue emitting normalized `line` metadata from rule-based issues and keep single-result and multi-result payloads aligned. |
| DIAG-02 | User receives column information for rule-based C, Java, and JavaScript findings when available. | Treat `col` as part of the rule-issue contract and add regression assertions anywhere a new rule is introduced. |
| DIAG-03 | User receives an explanation that states what is wrong and what to fix next. | Expand `src/tutor_explainer.py` coverage and keep explanations keyed by normalized error type. |
| DIAG-04 | User sees degraded-mode warnings when semantic ML analysis is unavailable. | Standardize on `src.ml_engine.get_model_status()` plus `warnings`/`degraded_mode` metadata from `detect_errors()`. |
| FIX-02 | User gets consistent issue labels and wording across API, CLI, and Streamlit entry points. | Push wording and labeling into shared payloads from `src/`; keep entry points as renderers only. |
| OPS-01 | API `/health` accurately reports healthy versus degraded runtime state. | `/health` already maps directly to `get_model_status()`; Phase 05 should preserve this contract and add parity checks around status-dependent UX. |
| OPS-03 | CLI, API, and Streamlit startup paths work on a clean local environment with documented setup. | Verify the existing startup commands in healthy and degraded mode, and document the current sklearn/bundle expectations explicitly. |
| QA-01 | Automated tests cover known false negatives and regressions for C, Java, and JavaScript. | Build on `tests/test_c_java_js_regressions.py` and add requirement-oriented cases for localization, explanations, and parity. |
| QA-02 | Smoke scripts fail gracefully when ML artifacts are unavailable instead of crashing. | Keep `tests/test_script_smoke.py` in scope and add healthy/degraded smoke coverage where current scripts only prove happy-path execution. |
| QA-03 | Documentation and reports clearly describe current limitations, fixes, and verification evidence. | Reconcile stale planning docs with the verified healthy runtime and keep QA/debug artifacts as canonical evidence. |
</phase_requirements>

## Summary

Phase 05 should be planned as a consolidation phase over code that already contains most of the core technical primitives: a shared rule engine for C/Java/JavaScript in `src/error_engine.py`, a grouped projection in `src/multi_error_detector.py`, metadata-aware ML bundle health in `src/ml_engine.py`, and regression suites covering the main QA-discovered failures. The phase is not starting from a blank slate.

The most important planning fact is that the live repo state is healthier than some project docs imply. Direct runtime verification on 2026-03-27 shows `src.ml_engine.get_model_status()` returning `loaded=true` with bundle metadata for `scikit-learn 1.7.2`, while older project docs and `requirements.txt` still describe or pin the pre-fix `1.1.3` world. Planning must treat the code, the regenerated bundle, and the resolved debug record as authoritative, then schedule documentation/dependency reconciliation early so future work does not reintroduce stale degraded-mode assumptions.

Phase 05 work should stay centered in shared `src/` logic, not entry-point forks. API, CLI, and Streamlit mostly render shared results today; the hardening work is therefore about tightening the shared contracts for issue typing, line/column data, tutor explanations, degraded-mode warnings, and regression coverage, then verifying those contracts surface consistently everywhere.

**Primary recommendation:** Plan Phase 05 around the existing shared rule-engine plus metadata-aware ML health contract, and make sklearn/doc/runtime reconciliation the first task so healthy and degraded verification targets are based on the real repo state.

## Project Constraints (from AGENTS.md)

- Treat degraded-mode correctness as a first-class requirement.
- Add tests for every detection bug fix.
- Prefer shared logic in `src/` over duplicating behavior in entry points.
- Be careful in `src/error_engine.py` and `src/multi_error_detector.py`; both are high-impact modules.

## Standard Stack

Version verification in this research is based on the local workspace and direct import checks, not external package registries.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.10.0 | Runtime for API, CLI, Streamlit, tests, and scripts | Verified local runtime; all repo commands use `python` directly |
| pytest | 8.4.0 | Automated regression and smoke testing | Existing repo standard for all verification |
| FastAPI | 0.110.0 | HTTP API surface in `api.py` | Current shared API framework already covered by tests |
| Streamlit | 1.45.1 | Browser UI in `app.py` | Existing UI surface; Phase 05 needs parity verification, not replacement |
| scikit-learn | 1.7.2 runtime / bundle metadata | ML classifier runtime and bundle compatibility contract | Verified healthy locally; matches `models/bundle_metadata.json` and `get_model_status()` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic | 2.11.5 | Request/response schemas in API | Use for API contracts only; keep detection payload normalization in `src/` |
| uvicorn | 0.27.1 | API server runtime | Use for local API startup and smoke verification |
| joblib | 1.2.0 | Model artifact loading | Use through `src/ml_engine.py`; do not bypass loader semantics |
| numpy | 1.26.4 | Feature arrays and ML helpers | Use inside ML/retraining scripts only |
| pandas | requirements only (`>=1.5.0,<3.0.0`) | Evaluation/reporting scripts | Use for scripts; not part of the shared request path |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Shared heuristic/rule hardening in `src/` | New parser stack immediately | Out of scope for this phase; groundwork is acceptable, full replacement is deferred |
| Shared ML health via `get_model_status()` | Entry-point-specific health probes | Creates drift and inconsistent degraded-mode behavior |
| Existing single-result + grouped multi-result split | Separate implementations per entry point | Faster to write short-term, but high regression risk and violates project constraints |

**Installation:**
```bash
python -m pip install -r requirements.txt
```

**Version verification used for this research:**
```bash
python --version
python -m pytest --version
python -c "import fastapi, streamlit, sklearn, pydantic, joblib, numpy, uvicorn; ..."
python -c "from src.ml_engine import get_model_status; import json; print(json.dumps(get_model_status(), indent=2))"
```

**Critical note:** `requirements.txt` still pins `scikit-learn==1.1.3`, but the verified local runtime and bundle metadata are `1.7.2`. Phase 05 planning should treat this mismatch as real work, not background noise.

## Architecture Patterns

### Recommended Project Structure
```text
src/
+-- error_engine.py          # Authoritative single-result detection and warning payloads
+-- multi_error_detector.py  # Grouped multi-issue projection over shared rules
+-- ml_engine.py             # Model loading, compatibility, and health status
+-- tutor_explainer.py       # Shared explanation templates by normalized error type
+-- auto_fix.py              # Fix application driven by shared issue metadata
+-- quality_analyzer.py      # Secondary analysis used by API/CLI/Streamlit

api.py                       # FastAPI renderer and health endpoint
cli.py                       # Terminal renderer over shared engine
app.py                       # Streamlit renderer over shared engine
tests/
+-- test_c_java_js_regressions.py
+-- test_api_and_regressions.py
+-- test_script_smoke.py
```

### Pattern 1: Shared-Core Detection Is Authoritative
**What:** `detect_errors()` in `src/error_engine.py` owns language routing, degraded-mode warnings, rule issue normalization, and ML fallback decisions.
**When to use:** Any change that affects issue type, localization, degraded-mode semantics, or tutor wording.
**Example:**
```python
# Source: src/error_engine.py
rule_based_issues = _collect_c_like_rule_based_issues(code, language)
syntax_issues = [issue for issue in rule_based_issues if issue.get("type") in RULE_BASED_TYPES]
semantic_issues = [issue for issue in rule_based_issues if issue.get("type") in SEMANTIC_ERROR_TYPES]

if syntax_issues:
    primary_issue = _pick_primary_issue(syntax_issues)
    return _attach_metadata({...}, warnings)

if semantic_issues:
    primary_issue = _pick_primary_issue(semantic_issues)
    return _attach_metadata({...}, warnings)
```

### Pattern 2: Multi-Error Output Should Be a Projection, Not a Fork
**What:** `src/multi_error_detector.py` reuses `_collect_c_like_rule_based_issues()` and groups normalized issues by type.
**When to use:** Any change to issue grouping, ordering, or location surfacing.
**Example:**
```python
# Source: src/multi_error_detector.py
if language in ["Java", "C", "C++", "JavaScript"]:
    rule_based_issues = _collect_c_like_rule_based_issues(code, language)
    if rule_based_issues:
        all_errors.extend(_group_issues(rule_based_issues))
```

### Pattern 3: Healthy/Degraded Mode Must Flow from ML Metadata
**What:** `src/ml_engine.py` loads bundle metadata, exposes compatibility details, and powers `/health`.
**When to use:** Any work touching model availability, startup UX, or degraded-mode warnings.
**Example:**
```python
# Source: src/ml_engine.py
status = {"loaded": model_loaded, "error": model_error}
status["bundle_metadata_present"] = bool(bundle_metadata)
status["bundle_sklearn_version"] = bundle_metadata.get("sklearn_version")
status["expected_sklearn_major_minor"] = _expected_sklearn_major_minor()
status["sklearn_compatible"] = sklearn.__version__.startswith(expected_major_minor)
```

### Pattern 4: Tutor Copy Should Stay Type-Keyed and Shared
**What:** `src/tutor_explainer.py` maps normalized error types to `why`/`fix` text.
**When to use:** Any improvement to student-facing explanation quality.
**Example:**
```python
# Source: src/tutor_explainer.py
def explain_error(error_type: str) -> dict[str, str]:
    return EXPLANATIONS.get(
        error_type,
        {"why": "The code contains a structural or syntactic issue.",
         "fix": "Review the code structure and correct the error."}
    )
```

### Anti-Patterns to Avoid
- **Entry-point heuristics:** Do not add detection or label logic directly in `api.py`, `cli.py`, or `app.py`; they should render shared results.
- **Silent ML assumptions:** Do not assume degraded mode from stale docs; check `get_model_status()` and bundle metadata.
- **Extending dead legacy branches:** `src/error_engine.py` still contains unreachable old C-like logic after an earlier `return`; do not build new behavior there.
- **Localization drift:** Do not add rules without explicit `line`/`col` assertions in tests.
- **One-surface fixes:** Do not fix API output without verifying CLI and Streamlit presentation of the same shared fields.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-surface health reporting | Separate degraded/healthy status logic in API, CLI, and Streamlit | `src.ml_engine.get_model_status()` plus `detect_errors()` metadata | Prevents contradictory state reporting |
| Per-surface issue classification | Ad hoc regexes in `api.py`, `cli.py`, or `app.py` | `_collect_c_like_rule_based_issues()` and `detect_errors()` | Keeps C/Java/JS behavior aligned |
| Multi-error aggregation | A second C/Java/JS detector | `src.multi_error_detector._group_issues()` over normalized rule issues | Avoids ordering, dedupe, and label drift |
| Tutor text in entry points | Hard-coded UI/API explanation strings | `src.tutor_explainer.explain_error()` | One source of truth for student-facing copy |
| ML compatibility checks in scripts | Script-local sklearn version heuristics | Metadata-aware bundle contract in `src/ml_engine.py` and `scripts/retrain_model.py` | The repo already has the compatibility mechanism |

**Key insight:** Phase 05 risk comes from divergence between shared contracts and the surfaces that render them, not from missing primitives. The repo already has the primitives.

## Common Pitfalls

### Pitfall 1: Planning Against Stale ML Assumptions
**What goes wrong:** Work is scoped as if the product is still permanently degraded.
**Why it happens:** `PROJECT.md`, `STATE.md`, and `requirements.txt` lag behind the resolved debug record and live runtime.
**How to avoid:** Treat direct `get_model_status()` output, `models/bundle_metadata.json`, and the resolved debug note as the runtime source of truth.
**Warning signs:** Docs say `scikit-learn==1.1.3` is required while `/health` and bundle metadata say `1.7.2`.

### Pitfall 2: Reintroducing False Positives by Skipping String/Comment Masking
**What goes wrong:** Bracket or delimiter checks fire on characters inside strings or comments.
**Why it happens:** Heuristic edits bypass `_strip_c_like_comments_and_strings()` or remove cascading-noise suppression.
**How to avoid:** Keep masking and `_suppress_cascading_syntax_noise()` on the hot path and add negative tests before touching those helpers.
**Warning signs:** Regressions like `print(')')` or unclosed-string snippets start producing `UnmatchedBracket`.

### Pitfall 3: Single-Result and Multi-Result Paths Drift Apart
**What goes wrong:** `detect_errors()` and `detect_all_errors()` disagree on issue types, counts, ordering, or localization.
**Why it happens:** A new rule is added to one path but not the other.
**How to avoid:** Make all new C/Java/JS rules originate in shared rule collection, then project them into both outputs.
**Warning signs:** API/CLI show one primary error while Streamlit multi-error mode omits or renames it.

### Pitfall 4: Healthy Mode Breaks Quietly After Bundle or Dependency Drift
**What goes wrong:** Rule-based tests keep passing while semantic ML silently falls back again.
**Why it happens:** Bundle artifacts and sklearn/runtime expectations are version-coupled.
**How to avoid:** Add explicit healthy-mode checks around `get_model_status()` and document the expected bundle metadata.
**Warning signs:** `/health` becomes `degraded`, or `model_loaded` flips false without test failures in cross-language regressions.

### Pitfall 5: Fixing Detection Without Fixing Presentation Parity
**What goes wrong:** Shared payloads improve, but CLI or Streamlit still show stale wording or omit warnings.
**Why it happens:** Entry-point rendering is lightly tested compared with backend logic.
**How to avoid:** Include API, CLI, and Streamlit parity checks in the same plan wave as payload changes.
**Warning signs:** API returns `warnings`/`degraded_mode`, but CLI or UI output never surfaces them.

## Code Examples

Verified patterns from repo sources:

### Authoritative C/Java/JavaScript Rule Selection
```python
# Source: src/error_engine.py
if syntax_issues:
    primary_issue = _pick_primary_issue(syntax_issues)
    primary_type = primary_issue["type"] if primary_issue else "SyntaxError"
    return _attach_metadata({
        "language": language,
        "predicted_error": primary_type,
        "confidence": 1.0,
        "tutor": explain_error(primary_type),
        "rule_based_issues": rule_based_issues
    }, warnings)
```

### API Health Delegates to Shared ML Status
```python
# Source: api.py
status = get_model_status()
loaded = bool(status.get("loaded"))
health_status = "healthy" if loaded else "degraded"
degraded_reason = None if loaded else (status.get("error") or "ML model unavailable")
```

### Multi-Error Grouping Preserves Locations and Suggestions
```python
# Source: src/multi_error_detector.py
grouped[error_type]["locations"].append({
    "line": issue.get("line"),
    "col": issue.get("col"),
    "message": issue.get("message"),
    "suggestion": issue.get("suggestion"),
    "snippet": issue.get("snippet"),
})
```

### Retraining Writes Bundle Metadata with the Artifacts
```python
# Source: scripts/retrain_model.py
with open(paths["metadata"], "w", encoding="utf-8") as metadata_file:
    json.dump(get_bundle_metadata(), metadata_file, indent=2, sort_keys=True)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Shallow non-Python structural checks plus optional ML | Rich shared C/Java/JS rule engine with normalized issues, localization, and multi-error reuse | QA/debug work on 2026-03-27 | Degraded mode is materially more useful and testable |
| Hard-coded sklearn major/minor expectation without bundle metadata as the main planning story | Metadata-aware bundle verification with `bundle_metadata.json` and status reporting | Resolved ML debug session on 2026-03-27 | Healthy mode can be verified explicitly and regenerated in-place |
| Planning docs assuming degraded ML as the default current state | Live runtime verified healthy on 2026-03-27 | Repo/runtime verification during this research | Phase plans must separate stale docs from actual runtime behavior |

**Deprecated/outdated:**
- Treating `requirements.txt` `scikit-learn==1.1.3` as the authoritative runtime contract is outdated in this workspace.
- Treating all Phase 05 work as "restore ML from degraded mode" is outdated; the bundle is already healthy locally.
- Extending the old dead C-like branch below the early return in `src/error_engine.py` would be an outdated implementation path.

## Open Questions

1. **Should Phase 05 explicitly clean up stale planning/docs and the sklearn pin before reliability work continues?**
   - What we know: runtime is healthy at `1.7.2`, but planning docs and `requirements.txt` still encode the older degraded assumptions.
   - What's unclear: whether doc/dependency reconciliation belongs inside this phase or should be a prerequisite patch.
   - Recommendation: include it in the first plan wave because later verification depends on it.

2. **How much parser groundwork belongs in this phase?**
   - What we know: full parser replacement is deferred, but the context leaves room for parser-grade groundwork.
   - What's unclear: whether Phase 05 should only refine heuristics or also add interfaces/seams for future parser-backed detectors.
   - Recommendation: allow groundwork only where it reduces heuristic fragility without changing the shared contracts.

3. **How far should entry-point verification go for Streamlit?**
   - What we know: backend and script tests exist; no dedicated browser/UI automation exists yet.
   - What's unclear: whether manual smoke is sufficient for Phase 05 or whether lightweight automated coverage is needed.
   - Recommendation: at minimum add deterministic smoke guidance; add automation only if shared-output changes are substantial.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All phase work | yes | 3.10.0 | none |
| pytest | Regression and smoke validation | yes | 8.4.0 | none |
| FastAPI | API parity and `/health` checks | yes | 0.110.0 | none |
| Streamlit | UI parity verification | yes | 1.45.1 | Manual verification if no UI automation is added |
| uvicorn | API startup smoke | yes | 0.27.1 | `python api.py` local run path |
| scikit-learn | ML health and retraining | yes | 1.7.2 | Degraded-mode fallback exists, but healthy-mode tasks are blocked without sklearn |
| Model bundle metadata | Healthy-mode verification | yes | `models/bundle_metadata.json` present | Degraded mode only |
| Training dataset | Model regeneration workflow | yes | `dataset/merged/all_errors_v3.csv` present | None for retrain work |

**Missing dependencies with no fallback:**
- None identified for current Phase 05 scope.

**Missing dependencies with fallback:**
- Streamlit browser automation tooling is not present in repo tests; manual smoke remains the fallback.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.4.0 |
| Config file | none - tests rely on `tests/` layout and direct commands |
| Quick run command | `python -m pytest tests/test_c_java_js_regressions.py -q` |
| Full suite command | `python -m pytest tests/ -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DET-02 | C/Java/JS fallback detection works without ML | unit/regression | `python -m pytest tests/test_c_java_js_regressions.py -q` | yes |
| DET-03 | Multi-error reporting returns multiple grouped findings | unit/regression | `python -m pytest tests/test_c_java_js_regressions.py -q` | yes |
| DET-04 | Strings/comments do not trigger bracket noise | unit/regression | `python -m pytest tests/test_api_and_regressions.py -q` | yes |
| DIAG-01 | Localized line metadata is returned | unit/regression | `python -m pytest tests/test_c_java_js_regressions.py -q` | yes |
| DIAG-02 | Column metadata is preserved where available | unit/regression | `python -m pytest tests/test_c_java_js_regressions.py -q` | yes |
| DIAG-03 | Tutor explanations are actionable and type-aligned | unit/regression | `python -m pytest tests/test_api_and_regressions.py -q` | yes |
| DIAG-04 | Degraded-mode warnings appear when ML is unavailable | integration | `python -m pytest tests/test_api_and_regressions.py -q` | yes |
| FIX-02 | API, CLI, and Streamlit show consistent labels/warnings | integration/manual-smoke | `python -m pytest tests/test_api_and_regressions.py -q` | yes, partial |
| OPS-01 | `/health` reflects healthy vs degraded | integration | `python -m pytest tests/test_api_and_regressions.py -q` | yes |
| OPS-03 | Startup paths work locally | smoke/manual | `python -m pytest tests/test_script_smoke.py -q` | yes, partial |
| QA-01 | Known C/Java/JS regressions stay fixed | regression | `python -m pytest tests/test_c_java_js_regressions.py -q` | yes |
| QA-02 | Scripts degrade gracefully instead of crashing | smoke | `python -m pytest tests/test_script_smoke.py -q` | yes |
| QA-03 | QA/debug documentation matches verified state | manual/doc review | none - document check | Wave 0 gap |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_c_java_js_regressions.py -q`
- **Per wave merge:** `python -m pytest tests/test_api_and_regressions.py -q` and `python -m pytest tests/test_script_smoke.py -q`
- **Phase gate:** `python -m pytest tests/ -q`

### Wave 0 Gaps
- [ ] Add explicit column assertions for every new C/Java/JS rule case; current regression coverage is strong but not exhaustive.
- [ ] Add targeted explanation-quality tests so DIAG-03 is not inferred only from generic payload presence.
- [ ] Add CLI parity smoke coverage; current automated checks are API-heavy.
- [ ] Add at least one Streamlit verification path or a documented manual checklist for Phase 05 sign-off.
- [ ] Reconcile documentation/tests around healthy-mode expectations so QA-03 is automatable or at least reviewable.

## Sources

### Primary (HIGH confidence)
- `/.planning/phases/05-cross-language-reliability-hardening/05-CONTEXT.md` - locked decisions, discretion boundaries, canonical references
- `/.planning/REQUIREMENTS.md` - requirement IDs and descriptions
- `/.planning/ROADMAP.md` - roadmap position and prior phase overlap
- `/.planning/STATE.md` - current planning-state drift to account for
- `/.planning/codebase/ARCHITECTURE.md` - shared-engine architecture and entry points
- `/.planning/codebase/CONCERNS.md` - fragility and verification gaps
- `/.planning/codebase/TESTING.md` - existing test conventions and commands
- `/docs/QA_REPORT_2026-03-27.md` - QA-derived bug list, risk ranking, and implemented fixes
- `/.planning/debug/resolved/ml-model-bundle-load-failure.md` - resolved ML recovery and verification evidence
- `/src/error_engine.py` - authoritative single-result detection path
- `/src/multi_error_detector.py` - multi-error grouping contract
- `/src/ml_engine.py` - metadata-aware ML status contract
- `/src/tutor_explainer.py` - explanation mapping
- `/api.py` - API health and parity surface
- `/cli.py` - CLI rendering behavior
- `/app.py` - Streamlit rendering behavior
- `/tests/test_c_java_js_regressions.py` - cross-language regressions
- `/tests/test_api_and_regressions.py` - API/health/regression coverage
- `/tests/test_script_smoke.py` - script smoke coverage
- `/scripts/retrain_model.py` - model regeneration and metadata write path
- Direct runtime checks on 2026-03-27:
  - `python -c "from src.ml_engine import get_model_status; ..."` => healthy, metadata present, sklearn 1.7.2
  - `python -m pytest tests/test_c_java_js_regressions.py -q` => `10 passed`
  - `python -m pytest tests/test_api_and_regressions.py -q` => `16 passed, 1 skipped, 1 xfailed`
  - `python -m pytest tests/test_script_smoke.py -q` => `6 passed`

### Secondary (MEDIUM confidence)
- None needed; all key claims were verified from local repo artifacts or direct runtime commands.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - verified from local imports, requirements file, and live runtime status
- Architecture: HIGH - confirmed from code and codebase maps
- Pitfalls: HIGH - derived from QA report, resolved debug notes, and direct code inspection

**Research date:** 2026-03-27
**Valid until:** 2026-04-03
