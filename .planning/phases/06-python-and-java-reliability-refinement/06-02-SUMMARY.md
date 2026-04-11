---
phase: 06-python-and-java-reliability-refinement
plan: 02
status: complete
---

# Plan 06-02 Summary

Implemented suggestion-only autofix behavior for `IndentationError` and `UnclosedString`, and tightened guidance wording to be location-aware.

## What Changed

- Updated `src/auto_fix.py`:
  - Added `suggest_indentation_fix(...)` and `suggest_unclosed_string_fix(...)` helper paths.
  - Switched `apply_fixes(...)` branches for `IndentationError` and `UnclosedString`/`UnclosedQuotes` to suggestion-only behavior (no source mutation).
  - Guidance now references the reported line number when available.
- Updated `src/tutor_explainer.py`:
  - Refined `IndentationError` and `UnclosedString` explanations to be clearer and action-oriented.
- Added regression tests:
  - `tests/test_detection.py` now asserts suggestion-only behavior and location-aware messages for both error types.
  - `tests/test_error_and_repair_matrix.py` now asserts autofix preserves original snippets for both locked cases.

## Verification

- `pytest tests/test_detection.py tests/test_error_and_repair_matrix.py -q`

## Result

Plan 06-02 is complete and locked with regression tests:
- Indentation and unclosed-string fixes remain conservative (suggestion-only).
- Guidance is more precise and line-aware.
