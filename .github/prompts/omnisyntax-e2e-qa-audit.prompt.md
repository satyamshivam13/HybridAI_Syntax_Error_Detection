---
description: "Run a full FAANG-level end-to-end QA audit for OmniSyntax across C, C++, Java, Python, and JavaScript, including AI tutor quality checks, stress testing, and a structured defect report."
name: "OmniSyntax E2E QA Audit"
argument-hint: "Optional focus: quick | standard | deep, plus any language or module priority"
agent: "agent"
---

Run a complete end-to-end QA and AI tutor validation for OmniSyntax from scratch.

If an argument is provided, use it only to control depth or emphasis. Do not skip any mandatory sections.

## Objective
Validate that OmniSyntax:
- Correctly detects issues across C, C++, Java, Python, and JavaScript
- Provides accurate and helpful fixes
- Behaves like a real AI tutor by teaching, not only patching
- Correctly handles both faulty code and correct code

## Scope and Workflow
1. Understand system workflow and architecture before testing.
2. Validate detector behavior in the same pathways users hit:
- Core engine
- API
- CLI
- Streamlit behavior expectations
3. Build and run an extensive multilingual test matrix.
4. Capture reproducible evidence for each case.
5. Produce prioritized defects, root causes, and actionable fixes.

## Required Architecture Validation Output
You must explicitly identify and report where workflow entry points are wired, including file paths and line references when available:
- Core detection entry
- API check route integration
- Streamlit detection integration
- CLI detection integration

## Mandatory Languages
- C
- C++
- Java
- Python
- JavaScript

## Mandatory Test Categories Per Language
- Syntax Errors: missing semicolon, brackets, delimiters, malformed statements
- Logical Errors: wrong result despite valid syntax
- Runtime-like Errors: undeclared identifiers, type mismatch, divide-by-zero, missing import/include
- Edge Cases: incomplete code, nested blocks, unusual formatting, unclosed strings
- Correct Code: valid snippets that must return no error and clear positive tutor feedback

## Minimum Test Volume
- At least 5 to 10 additional test cases per language
- Include both error and no-error cases
- Include provided base cases exactly as seed scenarios
- Recommended baseline target: about 9 or more cases per language for balanced coverage

## Seed Cases To Include

### Error Code Examples

C
int main() {
    int a = 5
    printf("%d", a);
}

C++
#include <iostream>
using namespace std;
int main() {
    int x;
    cout << y;
}

Java
public class Main {
    public static void main(String[] args) {
        int a = "hello";
    }
}

Python
def test():
print("Hello")

JavaScript
function demo() {
    let a = 10;
    console.log(b);
}

### Correct Code Examples

Python
def add(a, b):
    return a + b
print(add(2,3))

JavaScript
let x = 10;
console.log(x);

## Required Case-Level Evidence
For every test case, capture all of the following:
- Input code
- OmniSyntax output
- Result flag:
- PASS if detection and explanation are correct
- FAIL if error is missed, mislabeled, poorly explained, or response is missing
- Error type
- Exact location, including line number when available
- Corrected code
- Tutor-quality explanation that includes:
- Why the issue occurs
- How to fix it
- Whether explanation is beginner-friendly
- Whether guidance is step-by-step

Also include for each case where available:
- Confidence score
- Rule-based issue list
- Degraded mode status and warnings

## AI Tutor Evaluation Rubric
Score each case on these dimensions:
- Concept explanation quality
- Correction clarity
- Beginner readability
- Guidance structure, stepwise or not
- Teaching value versus direct patching

## Stress and Consistency Testing
- Run bulk evaluations across many mixed cases per language
- Verify deterministic behavior across repeated runs
- Measure throughput or latency at detector level when possible
- Check consistency across core detector and API responses

## Mandatory Quantitative Reporting
Report all of the following numeric outputs:
- Total test count
- Passed count
- Failed count
- Overall pass rate percent
- Per-language totals, pass, fail
- Tutor-quality counters per language:
- explains why
- beginner-friendly
- step-by-step
- Stress run totals:
- total evaluations
- average latency per case if measurable
- consistency verdict

## Required Final Report Structure
Produce a professional, detailed QA report with these sections:
1. Executive Summary
2. Test Strategy and Coverage
3. System Workflow Overview
4. Per-language Results Summary
5. Overall metrics: total, passed, failed, pass rate
6. Detailed case table with expected versus observed
7. AI Tutor Quality Findings
8. Stress and consistency findings
9. Bug list prioritized as High, Medium, Low
10. Root cause analysis per major defect
11. Suggested fixes:
- Model improvements
- Rule-based enhancements
- Better training data and hard negatives
- UX and tutoring improvements
12. Residual risks and release readiness

## Mandatory Defect Narrative Style
For each high and medium defect, include:
- What failed
- Evidence by case ID
- Impact
- Likely root cause
- Code location hint with file and line when possible

Include a separate root-cause-themes section with cross-cutting patterns, for example:
- heuristic brittleness
- prioritization bias
- ML threshold or label confusion
- tutor static response limitations

## Mandatory Remediation Plan Sections
Provide a concrete remediation plan grouped under:
- Rule-based enhancements
- Model improvements
- Training data improvements
- Tutor UX improvements
- Regression hardening

## Workspace Integrity Notes
Always include a note about workspace state:
- whether pre-existing dirty files were detected
- confirmation that unrelated local changes were not reverted
- which new artifacts were created during audit

## Output Artifacts
Always generate:
- A machine-readable results artifact, for example JSON
- A human-readable QA report artifact, for example Markdown
- A concise chat summary with top findings and next remediation steps

Recommended artifact names for consistency:
- artifacts/qa/e2e_qa_results.json
- artifacts/qa/e2e_qa_results.md

## Quality Bar
- Do not skip categories
- Do not skip correct-code scenarios
- Do not omit line-level evidence when available
- Keep findings reproducible and implementation-oriented
- Prioritize real defects and regression risk over generic commentary
- Do not provide generic tutoring judgments without rubric-backed evidence
- Do not claim release readiness without explicit residual risk statement

## Execution Notes
- Reuse existing project tests and scripts when useful
- Add a dedicated audit script if needed for reproducibility
- Preserve unrelated local changes
- If blocked by environment constraints, state exact blocker and provide the closest valid alternative
