# Streamlit Deployment Audit — OmniSyntax

**Repository:** https://github.com/satyamshivam13/HybridAI_Syntax_Error_Detection
**Audit date:** 2026-06-24
**Auditor environment:** Python 3.11.9, scikit-learn 1.7.2, numpy 1.26.4, streamlit 1.58.0 (local, verified)
**Scope:** Audit + readiness + local functional verification. Actual cloud deployment must be performed by the repository owner (requires GitHub OAuth on the owner's Streamlit Community Cloud account). No live URL is asserted by this audit.

> Every claim below is backed by direct repository evidence. Items that could **not** be verified (the live cloud deployment) are explicitly marked as unverified.

---

## 1. Deployment Audit Report

### Phase 1 — Dependency Map

| Requirement | Value | Evidence |
|---|---|---|
| **Main Streamlit file** | `app.py` | Imports `streamlit` + `src.static_pipeline`, `src.auto_fix`, `src.quality_analyzer` (`app.py:6-11`) |
| **Required models** | `models/syntax_error_model.pkl`, `tfidf_vectorizer.pkl`, `label_encoder.pkl`, `numerical_features.pkl`, `bundle_metadata.json` | Loaded by `src/ml_engine.py:62-66` from `MODEL_DIR = "models"` |
| **Required datasets** | None at runtime | App analyzes user-pasted code; `dataset/` is training-only |
| **Required config files** | None mandatory; `.streamlit/config.toml` added by this audit | — |
| **Required environment variables** | **None** | `app.py` reads no env vars; `.env`/`.env.template` are **FastAPI-only** (`API_HOST`, `API_KEYS`, rate limits) and unused by the Streamlit app |
| **Required API keys** | **None** | No external API calls in `app.py` or its import chain |
| **Required Python version** | 3.10–3.12 (see §2); **3.11 verified healthy** | numpy `<2.0` pin has no Python 3.13 wheels |

**Runtime import chain (app path only):** `streamlit`, `scikit-learn` (unpickle), `joblib`, `numpy`. The remaining packages in `requirements.txt` (fastapi, uvicorn, pydantic, matplotlib, seaborn, plotly, pytest*) belong to the API/CLI/test surfaces, not the Streamlit app.

### Phase 2 — Deployment Readiness Check

| Check | Status | Detail |
|---|---|---|
| `requirements.txt` | ✅ Present, valid | Pins `scikit-learn==1.7.2`, `numpy>=1.23,<2.0`, `streamlit>=1.18,<2.0` |
| `packages.txt` | ➖ Not present | **Not needed** — no apt/system libraries required |
| `runtime.txt` | ➖ Not present | Streamlit Cloud selects Python via the deploy **Advanced settings** dropdown, not `runtime.txt`. Set it there. |
| `.python-version` | ➖ Not present | Not used by Streamlit Cloud |
| sklearn compatibility | ✅ Verified | Model bundle metadata requires `1.7` major.minor; requirements pin `==1.7.2`; `get_model_status()` → `sklearn_compatible: True` |
| Streamlit compatibility | ✅ Verified | App runs under streamlit 1.58.0 via `AppTest` with no exceptions |
| Python version compatibility | ⚠️ **Action required** | `numpy<2.0` (1.26.4) ships **no wheels for Python 3.13**. If Cloud defaults to 3.13 the build fails. **Select Python 3.11 (verified) or 3.12 at deploy.** |

### Phase 3 — Model Verification

| Artifact | Exists | Committed to git | Git-ignored | Loads OK |
|---|---|---|---|---|
| `models/syntax_error_model.pkl` (6.16 MB) | ✅ | ✅ tracked | ❌ no | ✅ |
| `models/tfidf_vectorizer.pkl` (147 KB) | ✅ | ✅ tracked | ❌ no | ✅ |
| `models/label_encoder.pkl` | ✅ | ✅ tracked | ❌ no | ✅ |
| `models/numerical_features.pkl` | ✅ | ✅ tracked | ❌ no | ✅ |
| `models/bundle_metadata.json` | ✅ | ✅ tracked | ❌ no | ✅ |

- **`git ls-files models/` lists all five files** → they ship with the clone the cloud builds from.
- In `.gitignore`, the `models/*.pkl` / `models/*.joblib` exclusions are **commented out** (lines 34-35); only `models/FAILED_*.pkl` and `models/*_debug.pkl` are ignored.
- No corruption: all artifacts unpickle and the engine reports `loaded: True`.
- **This directly refutes the stated risk "models/*.pkl may not be committed."** They are committed.

### Phase 5 — Validation Results (local, healthy environment)

Executed headlessly via `streamlit.testing.v1.AppTest` against `app.py`:

| Test | Result |
|---|---|
| `get_model_status()` | `loaded: True`, `sklearn_compatible: True` → **ML active** |
| Startup / render | No exception; initial prompt renders |
| Prediction (broken Python `def f(:`) | Detects `UnmatchedBracket` + `SyntaxError`, generates auto-fix preview |
| Clean code | "No syntax errors detected" |
| Java type-mismatch repro | No exception (post-fix regression guard holds in UI) |
| Degraded-mode signal | **Absent** → full ML mode, not rule-based-only |

**Functional classification (Python 3.11 + committed models): `FULLY FUNCTIONAL` (ML-assisted).**
On a Python 3.13 cloud runner where `numpy<2.0` fails to install, the deploy would instead **fail to build** (not silently degrade), because numpy is a hard import for the ML engine.

---

## 2. Dependency Issues Report

| Severity | Issue | Impact | Fix |
|---|---|---|---|
| 🔴 **Blocker (conditional)** | `numpy>=1.23,<2.0` has no Python 3.13 wheels | Build fails if Cloud uses Python 3.13 | Select **Python 3.11** (verified) or 3.12 in deploy Advanced settings |
| 🟡 Minor | `requirements.txt` installs API/viz deps unused by the app (fastapi, uvicorn, matplotlib, seaborn, plotly) | Slower builds, larger failure surface | Optional: a slim deploy requirements file (kept out of scope to avoid breaking API/CLI/tests) |
| 🟡 Minor | `MODEL_DIR = "models"` is relative to CWD (`src/ml_engine.py:14`) | Healthy only because Cloud CWD = repo root | Works as-is on Streamlit Cloud; consider `Path(__file__).parent.parent / "models"` for robustness |

## 3. Missing Assets Report

**None.** Entry point, all five model artifacts, and `requirements.txt` are present and committed. No secrets, datasets, or system packages are required at runtime.

## 4. Deployment Instructions

1. Merge the deploy-ready code to `main` (currently models + app are on `main`; this audit's `.streamlit/config.toml` and report are on a branch — merge them in).
2. Go to **share.streamlit.io** → sign in with the GitHub account that owns `satyamshivam13/HybridAI_Syntax_Error_Detection`.
3. **New app** → Repository: `satyamshivam13/HybridAI_Syntax_Error_Detection`, Branch: `main`, Main file path: `app.py`.
4. Open **Advanced settings** → set **Python version = 3.11** (do not accept the default if it is 3.13).
5. **Secrets:** leave empty — the app requires none.
6. Click **Deploy** and wait for the build (sklearn + numpy wheels download).
7. Record the resulting URL (e.g. `https://<app-name>.streamlit.app`).

### Secrets template
```toml
# .streamlit/secrets.toml — NOT REQUIRED for this app.
# The Streamlit UI reads no environment variables or API keys.
# (API keys in .env apply only to the separate FastAPI server, not app.py.)
```

## 5. Post-Deploy Verification Checklist (gates the badge)

Run these against the **live URL** before claiming a live demo:
- [ ] App loads without a Streamlit error screen.
- [ ] Paste `def f(:` → an error type is shown (not just a generic message).
- [ ] Paste valid code → "No syntax errors detected".
- [ ] **No "degraded mode" info banner appears** → confirms ML loaded on the cloud (proves it is not rule-based-only).
- [ ] Quality metrics panel renders.

## 6. Recommended README Changes

- **Do not add the Live Demo badge yet.** Add it **only after** the post-deploy checklist passes on the real URL.
- After verification, add under the badges:
  `**[🚀 Live Demo →](https://<app-name>.streamlit.app)**`
- If the live app shows the degraded-mode banner (ML failed to load on Cloud), advertise it as a **rule-based demo**, not "ML-assisted," to keep the README honest.

## 7. Go / No-Go Decision — Live Demo Badge

| Question | Verdict |
|---|---|
| Local functionality independently verified? | ✅ Yes — Fully Functional, ML active (Phase 5) |
| Cloud deployment performed & verified by this audit? | ❌ No — cannot deploy on owner's behalf |
| **Live Demo badge?** | **NO-GO (today).** Gated on the owner deploying with Python 3.11 and passing §5. The instruction forbids a badge without independent verification of the *deployment*, which does not yet exist. |
| Deployment production-ready? | **Conditionally yes** for a demo: ready to deploy with one required setting (Python 3.11/3.12). Not "production-grade" — the model's own release gate is `NO-GO` (MissingDelimiter recall 0.82). |

**Bottom line:** The repo is deployable and verified healthy locally; the only required action is pinning Python to 3.11/3.12 at deploy time. The Live Demo badge stays off until the live URL passes the §5 checklist — share the URL and it can be verified in minutes.
