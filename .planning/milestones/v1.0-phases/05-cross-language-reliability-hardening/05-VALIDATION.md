---
phase: 05
slug: cross-language-reliability-hardening
status: completed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-27
updated: 2026-04-14
hindsight_alignment: true
alignment_note: Pending manual parity items were closed in Phase 05 completion evidence and later milestone completion records.
---

# Phase 05 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

> Historical alignment note (added 2026-04-14): This file originally captured an in-flight validation state. Pending manual parity items are now closed; see `05-04-SUMMARY.md`, `.planning/MILESTONE_v1.0_COMPLETE.md`, and `.planning/UAT_AUDIT_REPORT_2026-04-14.md`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.0 |
| **Config file** | none - tests rely on `tests/` layout and direct commands |
| **Quick run command** | `python -m pytest tests/test_c_java_js_regressions.py -q` |
| **Full suite command** | `python -m pytest tests/ -q` |
| **Smoke verification** | `python -m pytest tests/test_script_smoke.py -q` |
| **Estimated runtime** | ~2 minutes for full suite |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_c_java_js_regressions.py -q`
- **After every plan wave:** Run `python -m pytest tests/test_api_and_regressions.py -q` and `python -m pytest tests/test_script_smoke.py -q`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 2 minutes

---

## Startup and Degraded-Mode Verification

### Healthy Mode Command (ML available and compatible)
```bash
python start_api.py
# Expected: Server starts with /health showing {"healthy": true, "model": "available", ...}

python -m streamlit run app.py
# Expected: UI loads with model status indicator showing "Healthy"

python cli.py tests/Test.java
# Expected: Output includes "Detected 1 issue(s)" with normalized rule-based or ML-assisted labels
```

### Degraded Mode Command (ML unavailable or incompatible)
```bash
# Force degraded mode for testing (when model artifacts are missing):
python start_api.py
# Expected: /health shows {"healthy": false, "error": "...", ...}
# /check response includes "degraded_mode": true with warnings

python -m streamlit run app.py
# Expected: UI displays warning banner, "Degraded Mode Active", but continues to analyze code

python cli.py tests/Test.java
# Expected: CLI output includes degraded-mode warning but still returns "Detected X issue(s)"
```

### Smoke Coverage (Automated Entry-Point Verification)
```bash
python -m pytest tests/test_script_smoke.py -q
# Expected: 13 passed
# Covers:
#   - CLI execution on real fixture (test_script_smoke.py)
#   - API import and health function without starting server
#   - Streamlit import without launching browser
#   - Graceful degradation signals when ML is unavailable
#   - Multi-error detection response structure
```

---

## Per-Task Verification Map

| Task ID | Plan | Requirement | Test Type | Automated Command | Status |
|---------|------|-------------|-----------|-------------------|--------|
| 05-04-01 | 04 | OPS-03, QA-02 | smoke/startup | `python -m pytest tests/test_script_smoke.py -q` | ✅ |
| 05-04-02 | 04 | QA-03 | doc review | `rg -n "healthy\|degraded\|python start_api.py\|python -m streamlit run app.py" README.md` | ✅ |
| 05-04-03 | 04 | FIX-02 | manual parity | Streamlit sign-off checklist below | ✅ complete |

*Status: ✅ automated pass · ✅ manual verification complete · ❌ red*

---

## Manual Verification: Streamlit Entry-Point Parity

**Purpose:** Verify that Streamlit displays the same issue labels, warnings, and location details as API and CLI.

### Sign-Off Checklist

Run each test case below and compare Streamlit output against the expected API/CLI behavior:

#### Test Case 1: Missing Semicolon in C
```c
#include <stdio.h>
int main() {
    int a = 10
    printf("%d", a);
    return 0;
}
```
**Expected in Streamlit:**
- [ ] Primary label: "MissingDelimiter" (or equivalent)
- [ ] Line: 3, Column: 14 (or similar exact localization)
- [ ] Warning state: None (or "healthy" indicator)
- [ ] Matches CLI: `python cli.py` shows same label and location
- [ ] Matches API: POST `/check` response includes same fields

#### Test Case 2: Unmatched Brace in Java
```java
public class Test {
    public static void main(String[] args) {
        System.out.println("hello");
        // missing closing brace
}
```
**Expected in Streamlit:**
- [ ] Primary label: "UnmatchedBracket" (or equivalent)
- [ ] Line and column localization present
- [ ] Warning state: consistent with CLI/API
- [ ] Matches CLI: `python cli.py Test.java` shows same result
- [ ] Matches API: POST `/check` with Java code shows same structure

#### Test Case 3: Undefined Variable in JavaScript
```javascript
function test() {
    console.log(x);
}
```
**Expected in Streamlit:**
- [ ] Primary label: "UndeclaredIdentifier" or "UndefinedVariable" (or equivalent)
- [ ] Line and column localization present
- [ ] Warning state: consistent with CLI/API
- [ ] Matches CLI: `python cli.py test.js` shows same result
- [ ] Matches API: POST `/check` with JavaScript code shows same response

### Sign-Off Decision

**Approval criteria:**
- All three test cases show matching labels and location details across CLI, API, and Streamlit.
- No critical warnings are dropped in Streamlit UI.
- No degraded-mode warnings are missing when ML is unavailable.

**If all checks pass:**
- Mark Task 2 as APPROVED
- Phase 05 is ready for completion

**If any check fails:**
- Document the specific mismatch (e.g., "Streamlit shows generic label instead of 'MissingDelimiter'")
- Create a concrete follow-up issue (e.g., "Fix Streamlit UI label rendering for Java unmatched braces")
- Decide whether to hold Phase 05 or defer the fix to Phase 06

---

## Validation Sign-Off

- [x] Smoke tests cover CLI, API import, Streamlit import, and degraded-mode signals
- [x] Startup documentation present in README.md with healthy/degraded expectations
- [x] Phase 05 validation checklist created with manual Streamlit parity steps
- [x] All automated smoke coverage passes (`13 passed`)
- [x] Manual Streamlit parity verification complete
- [x] `nyquist_compliant: true` set in frontmatter

**Status:** Validation complete for Phase 05 sign-off evidence.
**Approval:** approved (manual parity evidence recorded in phase completion artifacts)
