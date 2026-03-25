---
name: Project Analysis And Improvement
description: "Analyze what this project does, what technologies it uses, why choices were made, current bugs/risks, and prioritized improvements"
argument-hint: "Optional focus (for example: API only, model accuracy, test quality, release readiness, docs quality)"
agent: agent
---
Run a full, evidence-based analysis of this repository using: $ARGUMENTS

Objective:
- Explain what the project is doing.
- Explain what tools, libraries, and architecture are being used.
- Explain the core logic, decision paths, and algorithmic flow inside critical modules.
- Explain why those choices make sense (or where they do not).
- Identify bugs, quality issues, and regression risks.
- Provide a practical, prioritized improvement plan.

Default scope (override with `$ARGUMENTS`):
- Entire workspace, with focus on `src/`, `tests/`, `scripts/`, root app/API entry points, and key docs.

Primary sources to inspect first:
- [README](../../README.md)
- [Project Summary](../../docs/PROJECT_SUMMARY.md)
- [API Documentation](../../docs/API_DOCUMENTATION.md)
- [Comprehensive Test Report](../../docs/COMPREHENSIVE_TEST_REPORT.md)
- `app.py`, `api.py`, `cli.py`, `start_api.py`
- `src/`
- `tests/`
- `requirements.txt`, `requirements-dev.txt`
- `PROJECT_STATUS.md`, `PROJECT_STRUCTURE.md`

Rules:
- Ground every major claim in repository evidence.
- Do not invent behavior, metrics, or bug impact.
- If evidence is missing, explicitly mark it as `UNKNOWN` and request the minimum data needed.
- Prioritize correctness, safety, and maintainability over style-only comments.
- Keep recommendations actionable and scoped.

Output format:
1. Executive Summary
- What the system does in 5-8 bullets.
- Current overall health (green/yellow/red) with one-line rationale.

2. System Understanding
- Main flows: input -> processing -> output.
- Component map with responsibilities and boundaries.

3. Logic And Architecture Deep Dive
- End-to-end architecture view (entry points, service/core modules, data/control flow).
- Core logic walk-through for the most critical execution paths.
- Decision points and branching behavior (including fallback/error paths).
- Key algorithms/rules/model-routing logic and why they exist.
- Coupling and cohesion analysis across modules.
- Architecture weaknesses (complexity hotspots, hidden dependencies, brittle interfaces).

4. Technology Stack And Usage
- Runtime/frameworks/libraries in use.
- Where each key dependency is used (file references).
- Build/run/test workflow currently implied by the repo.

5. Design Rationale (Why)
- Likely reasons behind current architecture/tool choices.
- Trade-offs: what is gained and what is constrained.

6. Bugs And Risks (Findings First)
- Ordered by severity: critical, high, medium, low.
- For each finding include:
  - Symptom
  - Evidence (file path and short quote/behavior)
  - Impact
  - Probable root cause
  - Suggested fix
  - Confidence (high/medium/low)

7. Improvement Plan
- Top 10 improvements, prioritized.
- For each item include:
  - Priority (P0/P1/P2)
  - Effort (S/M/L)
  - Expected impact
  - Dependencies or blockers
  - Suggested owner area (API/core/tests/docs/devops)

8. Verification Strategy
- Specific checks/tests to run to validate each P0/P1 change.
- Mention any missing tests and propose exact new test cases.

9. Clarifications Needed
- List up to 5 high-value questions only if ambiguity blocks accurate conclusions.

Quality bar:
- Be direct, specific, and evidence-backed.
- Avoid generic advice that is not tied to this repository.
- Emphasize bug prevention and measurable improvement steps.
