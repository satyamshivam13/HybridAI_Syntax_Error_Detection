# OmniSyntax QA Report (FAANG-Style)
Date: 2026-03-27
Tester Role: Senior QA / Compiler Tooling Validation
Scope: C, Java, JavaScript detection quality in real-world degraded and rule-driven paths

## 1) Test Context
- Environment: Windows, Python virtual environment at `.venv`
- Core detector under test: `src/error_engine.py`
- Verification artifacts:
  - `artifacts/qa/multilang_qa_matrix_results.json`
  - `artifacts/qa/explore_failures_output.txt`
- Commands executed:
  - `python artifacts/qa/run_multilang_qa_matrix.py`
  - `python artifacts/qa/explore_failures.py`
  - `python -m pytest tests/test_c_java_js_regressions.py -q`
  - `python -m pytest tests/ -q`

## 2) Task Coverage
- Baseline matrix executed: 19 cases total
  - C: 6 cases
  - Java: 6 cases
  - JavaScript: 7 cases
- Adversarial matrix executed: 12 extra stress cases
  - C: 3 cases
  - Java: 4 cases
  - JavaScript: 5 cases
- Error families covered:
  - Syntax: missing delimiter, unmatched bracket, unclosed string, malformed member access
  - Semantic/logical: type mismatch, undeclared identifier, duplicate definition, missing include/import, unreachable code
  - Runtime-risk: division by zero

## 3) Instruction Compliance Results
### Baseline matrix outcomes (provided + additional per language)
- C: 6/6 detected
- Java: 6/6 detected
- JavaScript: 7/7 detected

### Detection quality notes
- In multi-defect snippets, OmniSyntax prioritizes syntax-level blockers as primary `predicted_error` and keeps semantic items in `rule_based_issues`.
- This behavior is mostly correct for tutoring workflows, but explanation ordering can hide secondary defects if consumers only read the top label.

## 4) Data and Findings
### A) Sample detailed outcomes (selected)
1. C-01 (provided): Missing semicolon
- Input code:
```c
#include <stdio.h>
int main() {
    int a = 10
    printf("%d", a);
    return 0;
}
```
- Detected: YES
- Primary type: `MissingDelimiter`
- Error location: line 3
- Fixed code:
```c
#include <stdio.h>
int main() {
    int a = 10;
    printf("%d", a);
    return 0;
}
```

2. J-01 (provided): Type mismatch + missing semicolon
- Input code:
```java
public class Test {
    public static void main(String[] args) {
        int x = "10";
        System.out.println(x)
    }
}
```
- Detected: YES
- Primary type: `MissingDelimiter`
- Secondary type present: `TypeMismatch`
- Error location: line 3 and line 4 level issues present
- Fixed code:
```java
public class Test {
    public static void main(String[] args) {
        int x = 10;
        System.out.println(x);
    }
}
```

3. JS-01 (provided): undefined variable + broken call
- Input code:
```javascript
function test() {
    let x = 10;
    console.log(y);
}
test(
```
- Detected: YES
- Primary type: `UnmatchedBracket`
- Secondary type present: `UndeclaredIdentifier`
- Error location: line 5 primary, line 3 secondary
- Fixed code:
```javascript
function test() {
    let x = 10;
    console.log(x);
}
test();
```

### B) Confirmed failure cases (after fixes)
1. FAILURE CASE: C-F3 logical assignment in condition not detected
- Input code:
```c
#include <stdio.h>
int main(){
 int a = 0;
 if (a = 5) { printf("x"); }
 return 0;
}
```
- OmniSyntax result: `NoError`
- Expected QA result: logical bug warning (suspicious assignment in conditional)
- Root cause:
  - No explicit rule for assignment-vs-comparison misuse in C/Java/JS condition expressions.
  - Current semantic checks focus on a defined subset (division by zero, unreachable, includes/imports, type mismatch patterns).
- Proposed fix:
  - Add rule detector for `if|while` condition patterns using assignment operators where comparison is likely intended.
  - Suggest quick-fix conversion from `=` to `==` where safe.
- Corrected code:
```c
#include <stdio.h>
int main(){
 int a = 0;
 if (a == 5) { printf("x"); }
 return 0;
}
```

### C) Additional gaps (quality, not hard miss)
1. Multi-defect prioritization can down-rank semantic context
- Example: J-01, JS-01
- Impact: UX may feel incomplete if consumer only reads `predicted_error`
- Recommendation: include `primary_error` + `secondary_errors` explicitly in response schema and UI.

## Priority Bug List
### High
1. Missing logical-pattern detector for assignment inside conditions (C/Java/JS)
- Status: OPEN
- Impact: real classroom bug escapes detection
- Repro: C-F3 from adversarial matrix

### Medium
1. Multi-defect explanation sequencing can obscure secondary actionable issues
- Status: OPEN (design-level)
- Impact: partial guidance in first-pass tutoring
- Repro: J-01 and JS-01 mixed-fault snippets

### Low
1. Semantic strictness for language-specific narrowing/implicit conversion remains heuristic-based
- Status: PARTIALLY MITIGATED
- Impact: edge-case false negatives still possible for advanced type systems

## Implemented Fixes During This QA Cycle
- Java type mismatch coverage broadened (narrowing numeric, String/boolean mismatch)
- JavaScript incomplete assignment syntax detection added (`const a = ;`)
- JavaScript invalid member access detection added (`obj..a`)
- JavaScript undeclared identifier false positives reduced:
  - object literal keys excluded
  - arrow-function parameters recognized as declared

Changed files:
- `src/error_engine.py`
- `tests/test_c_java_js_regressions.py`

## Verification After Fixes
- Targeted regressions: 17 passed
- Full test suite: 103 passed, 1 skipped, 1 xfailed
- Baseline matrix: 19/19 detected

## Architecture and Algorithm Recommendations
1. Introduce language-aware lightweight parsers (tree-sitter or equivalent) per C/Java/JavaScript to reduce regex-only ambiguity.
2. Split detection output into explicit channels:
   - `syntax_errors[]`
   - `semantic_errors[]`
   - `logic_warnings[]`
   - `primary_error`
3. Add confidence and severity at issue-level, not only global prediction.
4. Add mutation-based QA fuzz tests for delimiter and expression-edge corruption.
5. Add rule telemetry: track which detector rule fired to improve explainability and model-retraining feedback loops.
