---
description: "Audit project documentation for accuracy against the current codebase and dependencies"
name: "Documentation Up-to-Date Check"
argument-hint: "Scope or focus (optional), e.g. API docs only, quick check, deep check"
agent: "agent"
---
You are auditing whether this repository's documentation is up to date.

Use the user's prompt argument as scope guidance.

Argument behavior:
- If no scope is provided, run a full-repo documentation audit.
- If the argument includes "quick", prioritize high-impact docs first (README.md, setup/start commands, API and CLI usage).
- If the argument includes "deep", exhaustively verify all markdown documentation in scope.
- If the argument includes "report-only", do not edit files; only report findings and fixes.
- If the argument includes "api only" or "cli only", constrain checks accordingly.
- Treat generated outputs under `artifacts/` and `results/` as out of scope unless explicitly requested.

Audit targets:
- Top-level docs: README.md, PROJECT_STATUS.md, PROJECT_STRUCTURE.md
- docs/*.md files
- CLI/API usage and startup instructions
- Dependencies and setup instructions
- File paths, command examples, and stated capabilities

Validation method:
1. Read docs and extract claims (commands, paths, features, API behavior, outputs, metrics, and workflow steps).
2. Verify each claim against the real codebase and config files (for example: app/api entrypoints, src modules, scripts, tests, requirements files).
3. Mark each claim as:
   - Accurate
   - Needs update
   - Unverifiable
4. For each "Needs update" or "Unverifiable" item, provide concrete evidence from the codebase and propose corrected text.
5. If not in report-only mode and the fix is safe and straightforward, apply minimal documentation fixes directly.

Output format:
- Summary: pass/fail and confidence
- Findings:
  - Severity: High/Medium/Low
  - Doc location (path and line when available)
  - Problem
  - Evidence (path and line in code/config/test)
  - Recommended fix (exact replacement text when possible)
- Applied changes:
  - List files updated and what changed
- Remaining ambiguities:
  - Questions that need maintainer confirmation

Rules:
- Prefer precise evidence over assumptions.
- Do not invent features or endpoints.
- Keep edits minimal and preserve existing writing style unless clarity requires rewrite.
- If evidence is insufficient, mark as Unverifiable instead of guessing.
- If no issues are found, explicitly state that docs appear current and list what was checked.
