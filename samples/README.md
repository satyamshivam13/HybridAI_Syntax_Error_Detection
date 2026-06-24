# OmniSyntax Sample Files

A curated set of **example inputs** for trying OmniSyntax across every supported
language. Each file is a minimal, self-contained snippet that triggers a specific
detector — or, for the `valid.*` files, passes cleanly.

> Every expected output in this document was produced by running the committed
> file through the actual detector (`detect_errors`) in healthy ML mode. The
> outputs are verified, not illustrative. See [Verification](#verification).

## Purpose

- Give first-time users runnable inputs without writing their own buggy code.
- Demonstrate each detector category the engine actually supports.
- Serve as fixtures for manual QA and demos (CLI, API, or Streamlit UI).

## Supported languages

| Language | Folder | Extensions |
|---|---|---|
| Python | [`python/`](python/) | `.py` |
| Java | [`java/`](java/) | `.java` |
| C | [`c/`](c/) | `.c` |
| C++ | [`cpp/`](cpp/) | `.cpp` |

> JavaScript is also supported by the engine, but no JavaScript samples are
> included here yet (the requested sample set covers Python, Java, C, and C++).

## Folder structure

```
samples/
├── python/   valid · missing parenthesis · missing colon · bracket mismatch · unclosed string · indentation
├── java/     valid · missing semicolon · bracket mismatch · type mismatch · missing parenthesis
├── c/        valid · missing semicolon · bracket mismatch · missing include · type mismatch
├── cpp/      valid · missing semicolon · bracket mismatch · type mismatch · unclosed string
└── README.md
```

## Usage

Run any sample through the CLI (first-error mode):

```bash
python cli.py samples/python/missing_colon.py
```

Show every detected error instead of just the first:

```bash
python cli.py samples/c/bracket_mismatch.c --all-errors
```

You can also paste the file contents into the Streamlit UI (`python -m streamlit run app.py`)
or POST them to the API (`POST /check`). All three surfaces use the same engine.

## Expected outputs

`Detected error type` is the engine's `predicted_error`; `Line` and `Message`
are the primary rule-based issue. `valid.*` files report no errors.

### Python (`samples/python/`)

| File | Detected error type | Line | Message |
|---|---|---|---|
| `valid.py` | NoError (clean) | — | — |
| `missing_parenthesis.py` | UnmatchedBracket | 2 | Bracket structure is not balanced. |
| `missing_colon.py` | MissingDelimiter | 1 | Probable missing ':' after statement starting with 'def' |
| `bracket_mismatch.py` | UnmatchedBracket | 1 | Bracket structure is not balanced. |
| `unclosed_string.py` | UnclosedString | 1 | unterminated string literal (detected at line 1) |
| `indentation_error.py` | IndentationError | 2 | Expected an indented block after this statement. |

### Java (`samples/java/`)

| File | Detected error type | Line | Message |
|---|---|---|---|
| `Valid.java` | NoError (clean) | — | — |
| `MissingSemicolon.java` | MissingDelimiter | 3 | Statement appears to be missing a delimiter. |
| `BracketMismatch.java` | UnmatchedBracket | 1 | Bracket structure is not balanced. |
| `TypeMismatch.java` | TypeMismatch | 3 | Cannot assign String to int. |
| `TypeMismatchUseSite.java` | TypeMismatch | 4 | String variable 'input' is used in a numeric operation. |
| `MissingParenthesis.java` | UnmatchedBracket | 4 | Bracket structure is not balanced. |

### C (`samples/c/`)

| File | Detected error type | Line | Message |
|---|---|---|---|
| `valid.c` | NoError (clean) | — | — |
| `missing_semicolon.c` | MissingDelimiter | 4 | Statement appears to be missing a delimiter. |
| `bracket_mismatch.c` | UnmatchedBracket | 3 | Bracket structure is not balanced. |
| `missing_include.c` | MissingInclude | 2 | 'printf' requires include <stdio.h>. |
| `type_mismatch.c` | TypeMismatch | 4 | Cannot assign str to int. |

### C++ (`samples/cpp/`)

| File | Detected error type | Line | Message |
|---|---|---|---|
| `valid.cpp` | NoError (clean) | — | — |
| `missing_semicolon.cpp` | MissingDelimiter | 4 | Statement appears to be missing a delimiter. |
| `bracket_mismatch.cpp` | UnmatchedBracket | 3 | Bracket structure is not balanced. |
| `type_mismatch.cpp` | TypeMismatch | 4 | Cannot assign str to int. |
| `unclosed_string.cpp` | UnclosedString | 4 | String literal is not closed. |

## Notes on coverage

- **Missing parenthesis** is reported as `UnmatchedBracket` — an unbalanced `(` is
  a bracket-balance issue, which is how the engine classifies it.
- **Missing colon / missing semicolon** both surface as `MissingDelimiter` (the
  engine's general "missing terminator" label), with a language-specific message.
- **Type-mismatch detection has two forms.** *Declaration-site* mismatches
  (`int x = "hello";`) are caught for Java, C, and C++. *Use-site* mismatches —
  a `String` variable used in a relational/arithmetic operation against a number
  (`while (input > 0)`) — are caught for Java (`TypeMismatchUseSite.java`).
- **No Python type-mismatch sample is included.** Python is dynamically typed and
  the engine does not statically flag `int`/`str` mismatches there (a `count + "3"`
  snippet is reported as `UnusedVariable`, not `TypeMismatch`). Per the project's
  "only sample supported detectors" rule, that example is intentionally omitted.

## Testing instructions

Re-verify every sample produces its documented output:

```bash
python cli.py samples/java/TypeMismatch.java      # -> Detected: TypeMismatch (Line 3)
python cli.py samples/python/valid.py             # -> No syntax errors
```

Or run the engine directly over the whole folder:

```python
import glob
from src.error_engine import detect_errors

for path in glob.glob("samples/**/*.*", recursive=True):
    if path.endswith(".md"):
        continue
    with open(path, encoding="utf-8") as f:
        res = detect_errors(f.read(), path.rsplit("/", 1)[-1])
    print(path, "->", res["predicted_error"])
```

## Verification

- Verified on: 2026-06-24, healthy ML mode (`scikit-learn 1.7.2`, model loaded).
- Method: each committed file was read from disk and passed to `detect_errors`.
- Result: all `valid.*` files → `NoError`; all error files → the detector listed
  above; no file required degraded mode. Invariant check
  (`valid → NoError`, `error → non-NoError`) passed for all 21 files.
