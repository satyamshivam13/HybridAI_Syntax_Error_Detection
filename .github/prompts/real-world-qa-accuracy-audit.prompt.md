---
description: "Run a real-world QA and accuracy audit for OmniSyntax, covering detection correctness, tutor quality, stress behavior, and project-wide risks"
name: "Real-World QA Accuracy Audit"
argument-hint: "Optional focus (quick | standard | deep, plus any language/module priority)"
agent: "agent"
---
Run a full, evidence-based audit of OmniSyntax using: $ARGUMENTS

Objective:
- Evaluate how accurately the project responds to real-world user inputs.
- Check whether the detector, explanations, fixes, and fallback behavior are correct, clear, and consistent.
- Identify bugs, brittle logic, runtime risks, and misleading tutor responses.
- Produce a prioritized remediation plan backed by repository evidence.

Default scope (override with `$ARGUMENTS`):
- Entire workspace, with emphasis on `src/`, `tests/`, root entry points, QA scripts, and key docs.

Primary sources to inspect first:
- `README.md`
- `docs/`
- `api.py`, `app.py`, `cli.py`, `start_api.py`
- `src/`
- `tests/`
- `requirements.txt`, `requirements-dev.txt`
- `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`

Workflow:
1. Understand the system end to end before judging accuracy.
2. Trace the main execution paths used by real users.
3. Validate the project with realistic positive and negative code samples.
4. Stress the detection flow with malformed, incomplete, noisy, and repeated inputs.
5. Compare behavior across API, CLI, Streamlit, and core engine paths.
6. Report findings with direct evidence and concrete fixes.

Mandatory evaluation areas:
- Detection accuracy on correct and incorrect code
- Tutor explanation quality and usefulness
- Confidence and degraded-mode behavior
- Cross-entry-point consistency
- Edge-case handling and crash resistance
- Performance and redundant work
- Regression risk in critical shared modules

Suggested test matrix:
- Python, Java, C, C++, JavaScript
- Syntax errors, semantic errors, and no-error cases
- Unclosed strings, missing delimiters, unmatched brackets, undeclared identifiers, type mismatch, divide-by-zero, missing import/include
- Empty input, whitespace, partial code, malformed code, large input, repeated calls
- Known-good snippets that must return no error

Required reporting:
- What the project is supposed to do
- What actually happens across major paths
- Accuracy assessment with concrete examples
- Bugs found, ordered by severity
- Root cause analysis
- Suggested code fixes
- Residual risks and what remains unverified

Output format:
1. Executive Summary
2. System Understanding
3. Execution Flow Breakdown
4. Accuracy and Response Quality Findings
5. Issues Found
6. Fix Recommendations
7. Residual Risks
8. Validation Performed

Quality bar:
- Be specific and evidence-backed.
- Do not invent metrics or behavior.
- Mark unknowns clearly when evidence is missing.
- Focus on user-facing correctness, not style-only comments.
- Prioritize real-world accuracy over theoretical completeness.
