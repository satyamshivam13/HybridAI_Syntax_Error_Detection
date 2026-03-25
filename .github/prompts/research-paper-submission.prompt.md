---
name: Research Paper Submission Draft
description: "Generate an evidence-grounded, submission-ready research paper draft for OmniSyntax using repository artifacts"
argument-hint: "Optional overrides (for example: specific venue template, max pages, mandatory sections)"
agent: agent
---
Write a research-paper draft for this repository using: $ARGUMENTS

Default assumptions (override with `$ARGUMENTS` when needed):
- Target format: generic journal-style manuscript
- Citation style: IEEE numeric
- Length: no strict page limit (optimize for completeness and submission-readiness)
- Include optional deliverables: cover letter and 5-slide talk outline

Task:
- Produce a publication-quality manuscript draft for OmniSyntax that is close to submission-ready.
- Use only verifiable repository evidence for implementation and results claims.
- Where evidence is missing, explicitly mark placeholders as `TBD` and list what data is needed.

Primary sources to inspect first:
- [README](../../README.md)
- [Project Summary](../../docs/PROJECT_SUMMARY.md)
- [Paper Abstract](../../docs/PAPER_ABSTRACT.md)
- [Comprehensive Test Report](../../docs/COMPREHENSIVE_TEST_REPORT.md)
- [API Documentation](../../docs/API_DOCUMENTATION.md)
- [results](../../results/results.json)
- [advanced metrics](../../results/advanced_metrics.txt)
- [accuracy artifacts](../../artifacts/accuracy_final/)
- Core modules: `src/error_engine.py`, `src/ml_engine.py`, `src/syntax_checker.py`, `src/quality_analyzer.py`, `src/language_detector.py`
- Tests: `tests/`

Requirements:
- Do not invent experiments, benchmark numbers, datasets, baselines, or citations.
- Align claims with available artifacts and code behavior.
- Keep the tone academic and concise.
- Include reproducibility details (environment, commands, test/eval scripts).
- Include limitations and threat-to-validity statements.

Output format:
1. Paper Metadata
- Candidate title (3 alternatives)
- One-line contribution summary
- Suggested keywords

2. Abstract
- 150-250 words, evidence-grounded

3. Full Paper Draft
- Introduction
- Related Work (only if supported; otherwise include a TODO block)
- System Design / Method
- Implementation Details
- Experimental Setup
- Results
- Error Analysis / Ablations (if evidence exists)
- Discussion
- Limitations and Threats to Validity
- Conclusion

4. References
- Use only citations explicitly provided or inferable from repository docs.
- If external citations are needed but not available, add `TODO_CITATION` entries.

5. Submission Checklist
- Venue formatting assumptions used
- Claims-to-evidence trace table:
  - Claim
  - Evidence file path
  - Confidence (high/medium/low)
  - Gap to resolve before submission
- Missing assets blocking submission

6. Optional Deliverables (include by default)
- Cover letter to program chair/editor (short)
- 5-slide talk outline

Quality bar:
- Prioritize factual correctness over fluency.
- Surface weak evidence explicitly.
- Produce text that can be directly edited into a final submission package.