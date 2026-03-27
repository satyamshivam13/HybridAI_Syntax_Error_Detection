# Coding Conventions

**Analysis Date:** 2026-03-27

## Naming Patterns

**Files:**
- `snake_case.py` for source modules under `src/`
- `test_*.py` for pytest files under `tests/`
- Root entry scripts use short descriptive names such as `api.py`, `app.py`, and `cli.py`

**Functions:**
- `snake_case` for functions and helpers
- Private/internal helpers commonly use a leading underscore such as `_parse_cors_origins`
- Async behavior is uncommon; no special async naming convention is used

**Variables:**
- `snake_case` for locals and parameters
- `UPPER_SNAKE_CASE` for module constants such as `SUPPORTED_LANGUAGES`
- Type aliases are minimal; dict-based payloads are common

**Types:**
- `PascalCase` for classes and Pydantic models such as `CodeCheckRequest`
- Built-in generics and modern annotations are used in newer files

## Code Style

**Formatting:**
- No committed formatter config was found
- Files generally follow PEP 8 style with 4-space indentation
- Double quotes are common in current source files
- Semicolons are not used in Python code

**Linting:**
- No dedicated linter config was found in the repo
- New code should stay close to existing style and keep imports readable

## Import Organization

**Order:**
1. Standard library imports
2. Third-party packages
3. Local `src` imports

**Grouping:**
- Blank lines separate import groups in representative files like `api.py`
- Relative imports are common inside `src/`

**Path Aliases:**
- None; imports use package-relative or direct module paths

## Error Handling

**Patterns:**
- API boundary raises structured `HTTPException` values
- Runtime modules return dict-shaped results instead of throwing for normal detection outcomes
- ML failures are represented with explicit exceptions and degraded-mode status

**Error Types:**
- Throw or raise at the boundary when input is invalid or runtime health blocks a requested behavior
- Return structured result payloads for expected detection outcomes
- Include warnings when behavior is partial rather than silently failing

## Logging

**Framework:**
- Standard library `logging`
- Mostly configured in `api.py`

**Patterns:**
- Log infrastructure concerns at the API/runtime boundary
- Keep lower-level analysis modules mostly pure and return values instead of logging each step

## Comments

**When to Comment:**
- Explain rule-engine edge cases, compatibility constraints, or non-obvious heuristics
- Avoid trivial comments for straightforward assignments
- Module docstrings are already used in core files like `src/error_engine.py`

**Docstrings:**
- Module docstrings are common for core modules
- Function docstrings are selective rather than universal

**TODO Comments:**
- Not strongly standardized in the current repo
- Prefer concise, actionable TODOs if new ones are needed

## Function Design

**Size:**
- Small helpers are preferred for parsing and normalization
- Some legacy functions are longer; isolate new logic into helpers where possible

**Parameters:**
- Functions usually take a few explicit arguments rather than large option objects
- Filename and language context are often passed alongside code strings

**Return Values:**
- Detection and autofix code often returns dictionaries with stable keys
- Guard clauses and early returns are common in validation-heavy paths

## Module Design

**Exports:**
- Modules export plain functions and lightweight classes
- Central runtime behavior is imported directly from `src/` modules rather than through barrel files

**Boundaries:**
- Entry points should orchestrate, not reimplement detection logic
- Shared detection logic belongs in `src/`, with tests in `tests/`

## Guidance for New Code

- Prefer reusable helpers in `src/` over duplicating logic in `api.py`, `app.py`, or `cli.py`
- Preserve the dict-based result shapes expected by tests and entry points
- Add regression tests for every bug fix in C, Java, or JavaScript detection
- Favor explicit degraded-mode behavior over silent fallback

---
*Convention analysis: 2026-03-27*
*Update when patterns change*
