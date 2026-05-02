---
description: "Run a compact release-gate audit for OmniSyntax and decide whether it is safe to ship"
name: "Project Completeness Release Gate"
argument-hint: "Optional focus (quick | standard | deep, plus any area like API, tests, docs, ML, UI)"
agent: "agent"
---
Run a release-gate audit of OmniSyntax using: $ARGUMENTS

Objective:
- Decide whether the project is safe to ship.
- Identify any blocking gaps in functionality, tests, docs, or runtime behavior.
- Produce a concise go/no-go judgment backed by evidence.

Primary sources to inspect first:
- `README.md`
- `api.py`, `app.py`, `cli.py`, `start_api.py`
- `src/`
- `tests/`
- `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`
- Any relevant QA or validation artifacts under `.planning/` and `artifacts/`

Workflow:
1. Map the main runtime paths and project goals.
2. Check the most important user-facing flows.
3. Review current tests and recent validation evidence.
4. Search for unfinished code, TODOs, placeholders, and stale claims.
5. Make a release decision.

Audit focus:
- Core detection correctness
- API/CLI/Streamlit parity
- ML degraded-mode safety
- Test coverage for critical flows
- Documentation and roadmap alignment
- Remaining risks that would block release

Required output format:
1. Decision
- One of: `GO`, `NO-GO`, `GO WITH RISKS`
- One-sentence rationale

2. Blocking Issues
- Only issues that would block release.
- Each issue must include file evidence, root cause, and impact.

3. Non-Blocking Risks
- Short list of important but non-blocking concerns.

4. Evidence Summary
- Tests or checks reviewed or run.
- What was verified directly.
- What remains unverified.

5. Recommendation
- Clear next action if the answer is not `GO`.
- If `GO`, state the main residual risk to monitor.

Quality bar:
- Keep it short and strict.
- Do not over-explain.
- Only include evidence-backed claims.
- Treat unverified areas as risks, not as complete.
