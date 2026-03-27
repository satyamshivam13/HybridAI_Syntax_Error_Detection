# OmniSyntax

## What This Is

OmniSyntax is a brownfield Python project that detects and explains code issues for students working in Python, Java, C, C++, and JavaScript. It exposes the same analysis engine through a FastAPI API, a Streamlit interface, and a CLI so learners can submit code, receive error guidance, and get fix suggestions.

## Core Value

Students should get accurate, actionable code-error feedback even when the ML layer is unavailable.

## Requirements

### Validated

- ✓ Multi-language code checking is available through the API, CLI, and Streamlit app. — v1.0
- ✓ The system explains detected errors and suggests fixes for supported scenarios. — v1.0
- ✓ The runtime exposes degraded mode explicitly when ML artifacts cannot load. — v1.0
- ✓ Automated tests and CI protect core detection, API behavior, and smoke scripts. — v1.0
- ✓ Improved syntax and semantic error detection accuracy for C, Java, and JavaScript. — v1.0
- ✓ Reduced false negatives in degraded mode via 11+ rule-based patterns. — v1.0
- ✓ Line and column localization for all rule-based C/Java/JavaScript findings. — v1.0
- ✓ Improved tutor explanations with actionable next-step guidance. — v1.0
- ✓ API, CLI, and Streamlit degrade consistently with shared warning payloads. — v1.0
- ✓ Expanded QA coverage: 153 automated tests + regression suites for C/Java/JavaScript. — v1.0

### Active

*No active requirements yet — define via `$gsd-new-milestone` for v1.1.*

### Out of Scope

- New language support beyond Python, Java, C, C++, and JavaScript — reliability in existing languages is the priority.
- Full compiler replacement — the hybrid engine approach is the chosen strategy.
- Hosted SaaS, user accounts, or classroom management — outside the current repo scope.

## Context

OmniSyntax v1.0 shipped a hardened hybrid analysis pipeline for educational use across Python, Java, C, C++, and JavaScript. The engine exposes detection through FastAPI, a Streamlit UI, and a CLI. Key improvements in v1.0:

- **ML compatibility**: scikit-learn==1.7.2 bundle with metadata-aware health contract; `/health` reflects true model state.
- **Rule-based coverage**: 11+ patterns for C/Java/JavaScript covering syntax, semantic, and runtime error classes.
- **Entry-point parity**: CLI, API, and Streamlit now share warning payloads and consistent label/column output.
- **Test coverage**: 153 automated tests including API regressions, C/Java/JavaScript-specific regressions, and 13 smoke tests.

**Known gaps at v1.0:**
- `--all-errors` mode skips ML for Python semantic errors
- IndentationError and UnclosedString auto-fixes are imprecise
- Occasional false-positive UndeclaredIdentifier alongside TypeMismatch in Java

**Stack:** Python, FastAPI, Streamlit, scikit-learn 1.7.2, pytest

## Constraints

- **Tech stack**: Existing Python codebase with FastAPI, Streamlit, and scikit-learn artifacts - improvements need to fit the current architecture rather than rewrite it.
- **Compatibility**: Runtime compatibility is driven by `models/bundle_metadata.json` and the active `scikit-learn==1.7.2` environment contract; incompatible environments must still produce useful degraded-mode results.
- **Quality**: Student-facing diagnostics need exact locations and understandable explanations - vague or misleading feedback is not acceptable.
- **Reliability**: API, CLI, and Streamlit flows must behave consistently in healthy and degraded mode - regressions across entry points are high impact.
- **QA**: Production-grade regression coverage is required for C, Java, and JavaScript - known false negatives must stay fixed once addressed.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep the brownfield Python architecture | Stable entry points and tests made focused improvements lower risk than a rewrite | ✓ Good |
| Treat degraded-mode correctness as a first-class requirement | ML compatibility is fragile; fallback must still be trustworthy | ✓ Good |
| Organize work around detection reliability → feedback quality → ML recovery → QA hardening | Maps directly to observed failures and user goals; all phases delivered | ✓ Good |
| Use `.planning/codebase/` maps before deeper phase planning | Reliable repo context reduced rediscovery overhead across phases | ✓ Good |
| Pin scikit-learn==1.7.2 to match the bundle metadata contract | Prevents silent model incompatibility; degraded mode handles drift | ✓ Good |
| Accept auto-fix imprecision for IndentationError and UnclosedString | Precise rewriting is high-risk; suggestion-based fix is safer and still useful | ⚠️ Revisit |

---
*Last updated: 2026-03-27 after v1.0 milestone*

