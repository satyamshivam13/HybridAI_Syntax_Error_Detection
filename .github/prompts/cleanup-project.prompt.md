---
name: Project Cleanup And Structure
description: "Find duplicate code, detect unused files/symbols, and restructure a Python project safely with verification"
argument-hint: "Scope and constraints (for example: src and tests only, no file deletes without approval)"
agent: agent
---
Clean and reorganize this project based on the request: $ARGUMENTS

Default scope for this repository:
- All folders and files in the workspace, including `src/`, `tests/`, root `*.py` files, `scripts/`, `docs/`, `artifacts/`, and `results/`.
- Treat this as a workspace-scoped cleanup policy.

Goals:
1. Remove or consolidate duplicate code.
2. Detect unused files, modules, and symbols.
3. Improve project structure and consistency.
4. Preserve behavior and avoid risky changes.

Required workflow:
1. Inspect the repository and produce an action plan grouped by:
- Duplicate logic
- Dead/unused code and files
- Structural improvements (folders, naming, boundaries)
2. For each proposed removal or move, provide impact and confidence:
- Why it appears unused or duplicated
- What references were checked
- Confidence level (high, medium, low)
3. Ask for confirmation before deleting files or making low-confidence removals.
4. Implement approved changes in small, reviewable edits.
5. Update imports/paths/tests after each structural change.
6. Run available tests or smoke checks and report results.
7. Provide a final cleanup report with:
- Files changed
- Files removed
- Duplicates consolidated
- Risks or follow-ups

Safety constraints:
- Do not use destructive git commands.
- Include generated artifacts (`artifacts/`, `results/`) in analysis and cleanup.
- If uncertain whether a file is required, keep it and mark it as a candidate.
- Prefer reversible, minimal-risk refactors.
- Always ask before deleting any file.

Output format:
1. Findings: concise list with file references.
2. Proposed plan: ordered steps with risk level.
3. Implemented changes: what was done and why.
4. Verification: test commands and outcomes.
5. Remaining candidates: items needing manual decision.
