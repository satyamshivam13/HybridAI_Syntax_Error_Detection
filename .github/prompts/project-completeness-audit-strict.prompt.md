---
description: "Run a strict project-completeness audit with pass/fail verdict, checklist output, and evidence for every claim"
name: "Project Completeness Audit Strict"
argument-hint: "Optional focus (quick | standard | deep, plus any area like API, tests, docs, ML, UI)"
agent: "agent"
---
Run a strict completeness audit of OmniSyntax using: $ARGUMENTS

Objective:
- Determine whether the project is actually complete.
- Produce a pass/fail verdict for major project areas.
- Identify any missing work, unfinished code, stale artifacts, or unverified claims.
- Back every conclusion with repository evidence.

Primary sources to inspect first:
- `README.md`
- `docs/`
- `api.py`, `app.py`, `cli.py`, `start_api.py`
- `src/`
- `tests/`
- `requirements.txt`, `requirements-dev.txt`
- `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`
- Any QA, validation, audit, or summary artifacts under `.planning/` and `artifacts/`

Required workflow:
1. Read the roadmap and current state first.
2. Map the real runtime entry points and shared core paths.
3. Check for TODOs, placeholders, dead code, missing tests, and stale docs.
4. Run or review the most relevant validation commands.
5. Score each major area as pass, warn, or fail.
6. Report only evidence-backed conclusions.

Audit categories:
- Core detection engine
- API behavior and error handling
- CLI behavior
- Streamlit behavior
- ML compatibility and degraded-mode behavior
- Regression coverage
- Documentation completeness
- Roadmap / implementation alignment
- Unfinished code or stale artifacts

Output rules:
- If evidence is missing, say `UNKNOWN`.
- Do not claim completion without checking tests and roadmap state.
- Every finding must include file evidence.
- Prefer concrete pass/fail checks over narrative summaries.

Required output format:
1. Verdict
- One of: `PASS`, `PARTIAL`, `FAIL`
- One-sentence rationale

2. Checklist
- [ ] Project goals mapped to runtime entry points
- [ ] Core detection paths reviewed
- [ ] API, CLI, and Streamlit paths reviewed
- [ ] Tests reviewed or run
- [ ] Docs and roadmap reviewed
- [ ] Unfinished work / TODOs searched
- [ ] Residual risks documented

3. Completed Areas
- Each item must include evidence and why it is considered complete.

4. Incomplete or Risky Areas
- Ordered by severity: critical, high, medium, low
- For each item include:
  - Symptom
  - File evidence
  - Root cause
  - Impact
  - Recommended fix

5. Validation Evidence
- Commands run or reviewed
- Pass/fail result for each
- Gaps not covered by validation

6. Final Judgment
- State clearly whether the project is complete, mostly complete, or still has meaningful unfinished work.
- If incomplete, list the minimum remaining work needed to reach completion.

Quality bar:
- Be strict, concise, and evidence-based.
- Treat unverified claims as not complete.
- Prioritize user-facing correctness and repository completeness over style concerns.
