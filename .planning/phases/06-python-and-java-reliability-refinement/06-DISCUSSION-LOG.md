# Phase 06: python-and-java-reliability-refinement - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-11
**Phase:** 06-python-and-java-reliability-refinement
**Areas discussed:** Python all-errors semantics, IndentationError fix shape, UnclosedString fix shape, Java mixed-error precedence, Regression surface, Autofix evidence, Java guard strictness, Python semantic result shape, Streamlit parity coverage

---

## Python all-errors semantics

| Option | Description | Selected |
|--------|-------------|----------|
| AST-valid only | Run ML only after valid Python parses cleanly; merge confident semantic hits into all-errors. |  |
| Always run ML | Run ML for every Python snippet and merge semantic hits whenever confidence clears the bar. | ✓ |
| Rules first, ML later | Keep rule-based errors primary and only add ML when no rule-based issue is present. |  |

**User's choice:** Always run ML
**Notes:** Follow-up clarified that confident semantic ML findings should still merge into all-errors even when rule-based issues exist.

## IndentationError fix shape

| Option | Description | Selected |
|--------|-------------|----------|
| Suggestion only | Keep the conservative model: explain the fix, but do not rewrite indentation automatically. | ✓ |
| Targeted line rewrite | Adjust indentation on the failing line or block, instead of standardizing the whole file. |  |
| Normalize whole block | Reflow the surrounding block to a consistent indentation style. |  |

**User's choice:** Suggestion only
**Notes:** The user preferred to keep this fix conservative rather than automatically rewriting code.

## UnclosedString fix shape

| Option | Description | Selected |
|--------|-------------|----------|
| Append at EOF | Keep the current conservative repair: close the quote at the end of the snippet. |  |
| Insert at source line | Place the closing quote near the opening string so the fix stays local and easier to review. |  |
| Suggestion only | Do not rewrite code; explain where the missing quote should go. | ✓ |

**User's choice:** Suggestion only
**Notes:** The user preferred location-aware guidance without automatic rewriting.

## Java mixed-error precedence

| Option | Description | Selected |
|--------|-------------|----------|
| Suppress UndeclaredIdentifier | Treat TypeMismatch as the primary issue and drop the secondary false-positive in mixed cases. |  |
| Keep both with priority | Keep both issues but clearly mark TypeMismatch as primary in the response. |  |
| Contextual suppression | Suppress only when the identifier is clearly declared and typed elsewhere in the snippet. | ✓ |

**User's choice:** Contextual suppression
**Notes:** Follow-up clarified that suppression should be strict and evidence-based, not broad across every mixed case.

## Regression surface

| Option | Description | Selected |
|--------|-------------|----------|
| Unit tests only | Lock behavior with focused detector/autofix tests and stop there. |  |
| Unit + API/CLI | Add regression coverage through the shared API and CLI surfaces too. | ✓ |
| All entry points | Cover unit tests plus API, CLI, and Streamlit parity for the repaired cases. |  |

**User's choice:** Unit + API/CLI
**Notes:** The initial decision was later refined to include Streamlit parity as well.

## Autofix evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Exact line/column + wording | Lock the fix with location-aware guidance and clearer tutor text. | ✓ |
| Wording only | Improve the explanation text, but do not require location-specific guidance. |  |
| Location only | Require precise location metadata, but keep the wording mostly as-is. |  |

**User's choice:** Exact line/column + wording
**Notes:** The user wanted precision to mean both better location context and better language.

## Java guard strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Strict context-only | Suppress UndeclaredIdentifier only when declaration/type context proves it is false positive. | ✓ |
| Broad mixed-case | Suppress whenever TypeMismatch and UndeclaredIdentifier appear together in the same snippet. |  |

**User's choice:** Strict context-only
**Notes:** This keeps suppression narrow and evidence-based.

## Python semantic result shape

| Option | Description | Selected |
|--------|-------------|----------|
| Separate error group | Emit it as its own entry in errors/errors_by_type alongside rule-based findings. | ✓ |
| Primary only | Keep it only as the primary predicted_error and do not surface it in grouped all-errors output. |  |
| Hybrid | Surface it in errors, but keep it out of errors_by_type or treat it specially. |  |

**User's choice:** Hybrid
**Notes:** Follow-up clarified that the hybrid shape should still be a separate grouped error entry with confidence metadata.

## Streamlit parity coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, include Streamlit | Add UI parity coverage through AppTest in addition to unit and API/CLI assertions. | ✓ |
| No, unit + API/CLI | Keep the phase's automated lock to unit tests plus API/CLI regressions only. |  |

**User's choice:** Yes, include Streamlit
**Notes:** Streamlit parity remains in scope for the repaired cases.

## the agent's Discretion

- Exact test module placement and grouping.
- How to split the work into planning waves.
- Internal helper boundaries for the semantic merge and Java suppression logic.

## Deferred Ideas

None - discussion stayed within phase scope.
