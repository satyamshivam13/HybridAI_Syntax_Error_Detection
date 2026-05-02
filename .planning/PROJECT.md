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

- v1.2 production hardening and product foundations is now active (kickoff 2026-04-19).
- Secure public deployment path before any broad external exposure.
- Make the static pipeline authoritative and reduce legacy engine surface area.
- Add delivery, observability, and product foundations without weakening degraded-mode correctness.
- Latest verified local run (2026-05-02): 193 passed, 1 skipped, 1 xfailed.

## Current Milestone: v1.2 Production Hardening and Product Foundations

**Goal:** Make OmniSyntax deployable, secure, observable, and extensible for classroom and beta usage while preserving the reliability gains already delivered in v1.0 and v1.1.

**Target features:**
- Secure and typed API contracts with production-safe access control, rate limiting, and health semantics.
- Consolidated shared engine contracts with dead legacy branches removed, package boundaries clarified, and entry-point parity preserved.
- Delivery baseline: containers, CI quality gates, structured logging, tracing/alert hooks, and operational metrics.
- Runtime scale readiness through worker/isolation options, prewarm/cache strategy, and measurable load/perf gates.
- Student-facing diffed fix previews, clearer evidence/confidence surfacing, better code-quality scoring, and persistence foundations for saved analysis history.
- Project-mode multi-file analysis plus lightweight educator feedback workflows after the platform hardening layers are in place.

### Out of Scope

- New language support beyond Python, Java, C, C++, and JavaScript — reliability in existing languages is the priority.
- Full compiler replacement — the hybrid engine approach is the chosen strategy.
- Hosted SaaS, user accounts, or classroom management — outside the current repo scope.

## Context

OmniSyntax v1.0 shipped a hardened hybrid analysis pipeline for educational use across Python, Java, C, C++, and JavaScript. The engine exposes detection through FastAPI, a Streamlit UI, and a CLI. Key improvements in v1.0:

- **ML compatibility**: scikit-learn==1.7.2 bundle with metadata-aware health contract; `/health` reflects true model state.
- **Rule-based coverage**: 11+ patterns for C/Java/JavaScript covering syntax, semantic, and runtime error classes.
- **Entry-point parity**: CLI, API, and Streamlit now share warning payloads and consistent label/column output.
- **Test coverage**: 153 automated tests at v1.0; current regression suite is 193 passed, 1 skipped, 1 xfailed.

v1.1 tightened the remaining Python and Java reliability gaps while preserving entry-point parity.

v1.2 shifts from reliability repair into platform hardening. The April 19, 2026 audit found that the codebase is functionally healthy but still carries major production debt in API security, legacy engine complexity, deployability, observability, and product readiness. The current milestone turns those findings into ordered execution phases instead of leaving them as one-off audit notes.

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
| Prioritize API security and operational hardening before monetization or hosted product work | The audit showed internet exposure and delivery maturity are the real blockers, not feature count | ✓ Good |
| Keep a modular monolith and strengthen boundaries before considering microservices | Current scale does not justify distributed complexity; internal contracts need cleanup first | ✓ Good |
| Treat compiler/LSP integration as an adapter seam, not a one-shot rewrite | Improves fidelity for C-like languages without destabilizing the existing fallback path | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-02 after verification refresh*
