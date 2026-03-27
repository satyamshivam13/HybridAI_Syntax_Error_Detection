# OmniSyntax

## What This Is

OmniSyntax is a brownfield Python project that detects and explains code issues for students working in Python, Java, C, C++, and JavaScript. It exposes the same analysis engine through a FastAPI API, a Streamlit interface, and a CLI so learners can submit code, receive error guidance, and get fix suggestions.

## Core Value

Students should get accurate, actionable code-error feedback even when the ML layer is unavailable.

## Requirements

### Validated

- ✓ Multi-language code checking is already available through the API, CLI, and Streamlit app.
- ✓ The system can explain detected errors and suggest fixes for supported scenarios.
- ✓ The runtime now exposes degraded mode explicitly when ML artifacts cannot load.
- ✓ Automated tests and CI already protect core detection, API behavior, and smoke scripts.

### Active

- [ ] Improve syntax and semantic error detection accuracy for C, Java, and JavaScript.
- [ ] Reduce false negatives when ML classification is unavailable or incompatible.
- [ ] Improve line and column localization for reported issues.
- [ ] Improve tutor explanations and autofix quality for student-facing feedback.
- [ ] Make API, CLI, and Streamlit behavior reliable and consistent in degraded mode.
- [ ] Expand QA coverage and regression protection for known OmniSyntax failure cases.

### Out of Scope

- New language support beyond Python, Java, C, C++, and JavaScript - current work is focused on reliability in existing languages.
- Full compiler replacement for every supported language - the current roadmap improves the hybrid engine rather than building full compiler frontends.
- Hosted SaaS, user accounts, or classroom management features - not part of the present repo and not needed for the current reliability push.

## Context

OmniSyntax already contains a hybrid analysis pipeline with rule-based detection, ML-backed classification, auto-fix helpers, quality analysis, and student-oriented explanations. The repo includes working FastAPI, CLI, and Streamlit entry points, plus evaluation and reporting scripts, but recent QA work found that non-Python detection quality depends heavily on fallback heuristics when the serialized scikit-learn model bundle is unavailable.

Recent verification confirmed that the test suite passes in degraded mode and that the public entry points still run, but the ML runtime remains incompatible in the current environment. This means the short-term roadmap should prioritize strong rule-based behavior, trustworthy diagnostics, and better verification around degraded-mode operation.

## Constraints

- **Tech stack**: Existing Python codebase with FastAPI, Streamlit, and scikit-learn artifacts - improvements need to fit the current architecture rather than rewrite it.
- **Compatibility**: Serialized ML models are tied to `scikit-learn==1.1.3` - incompatible environments must still produce useful results.
- **Quality**: Student-facing diagnostics need exact locations and understandable explanations - vague or misleading feedback is not acceptable.
- **Reliability**: API, CLI, and Streamlit flows must behave consistently in healthy and degraded mode - regressions across entry points are high impact.
- **QA**: Production-grade regression coverage is required for C, Java, and JavaScript - known false negatives must stay fixed once addressed.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep the brownfield Python architecture | The repo already has stable entry points and tests, so focused improvements are lower risk than a rewrite | ✓ Good |
| Treat degraded-mode correctness as a first-class requirement | ML compatibility is currently fragile, so fallback behavior must still be trustworthy | ✓ Good |
| Organize work around detection reliability, feedback quality, ML recovery, and QA hardening | These areas map directly to observed failures and user goals | - Pending |
| Use `.planning/codebase/` maps before deeper phase planning | Future GSD phases need reliable repo context instead of rediscovering structure each time | ✓ Good |

---
*Last updated: 2026-03-27 after GSD project initialization*
