---
description: "Audit whether the whole project is complete, identify unfinished work, and report any remaining gaps with evidence"
name: "Project Completeness Audit"
argument-hint: "Optional focus (quick | standard | deep, plus any area like API, tests, docs, ML, UI)"
agent: "agent"
---
Run a full completeness audit of OmniSyntax using: $ARGUMENTS

Objective:
- Check whether the repository is functionally complete.
- Identify unfinished work, missing coverage, broken flows, and residual risks.
- Distinguish between implemented, partially implemented, and missing features.
- Produce a clear verdict on what is complete and what is still left.

Primary sources to inspect first:
- `README.md`
- `docs/`
- `api.py`, `app.py`, `cli.py`, `start_api.py`
- `src/`
- `tests/`
- `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`
- Any existing QA, audit, or summary artifacts under `.planning/` and `artifacts/`

Workflow:
1. Understand the project goals and current roadmap.
2. Map the major entry points and critical runtime flows.
3. Check the repo for missing pieces, partial implementations, and dead or stale code paths.
4. Run or review tests and validation artifacts where available.
5. Search for TODOs, placeholders, fallback stubs, outdated docs, and unverified claims.
6. Report exactly what is done, what is incomplete, and what remains risky.

Audit areas:
- Core detection and analysis logic
- API, CLI, and Streamlit entry points
- ML compatibility and degraded-mode behavior
- Regression test coverage
- Documentation and roadmap alignment
- Performance or reliability gaps
- Unfinished code, TODOs, placeholders, or stale artifacts

Required output:
1. Completion Verdict
- One of: complete, mostly complete, partially complete, incomplete
- One-line rationale

2. What Is Complete
- List the major finished capabilities with evidence.

3. What Is Not Complete
- List missing, partial, or brittle areas with file evidence.

4. Gaps and Risks
- Prioritized issues ordered by severity.
- For each issue include file, symptom, root cause, and impact.

5. Validation Summary
- Tests or checks reviewed or executed.
- Any unverified claims or missing evidence.

6. Next Steps
- Concrete remaining work, if any, grouped by priority.

Quality bar:
- Be evidence-based and specific.
- Do not claim completion without checking tests, roadmap state, and unfinished-code signals.
- Mark anything uncertain as unknown.
- Focus on whether the project is actually done, not just whether it builds.
