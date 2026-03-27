---
status: resolved
trigger: "Investigate issue: ml-model-bundle-load-failure"
created: 2026-03-27T14:54:14.8730286+05:30
updated: 2026-03-27T15:31:03.3986168+05:30
---

## Current Focus

hypothesis: Confirmed and resolved. The failing bundle was incompatible with the runtime toolchain.
test: Final verification completed across direct model status checks, `/health`, retrain preview, and the automated test suite.
expecting: Healthy mode should remain active in the current environment unless the bundle and runtime drift again.
next_action: Session complete; archive this record and use it as a known-pattern reference for future ML bundle failures.

## Symptoms

expected: models load successfully when the environment is compatible; /health reports healthy; semantic ML classification runs again
actual: /health reports degraded; semantic ML classification is skipped; degraded mode is active
errors: sklearn version mismatch warnings/errors and missing fallback model file errors
reproduction: start the API or call model health, then hit /health or invoke detection that depends on semantic ML loading
started: known current issue in this repo; recent QA and verification work confirmed degraded mode rather than healthy mode

## Eliminated

## Evidence

- timestamp: 2026-03-27T14:54:14.8730286+05:30
  checked: requirements and ML loader source
  found: `requirements.txt` pins `scikit-learn==1.1.3`, while `src/ml_engine.py` hard-codes `REQUIRED_SKLEARN_MAJOR_MINOR = "1.1"` and expects either a primary bundle (`tfidf_vectorizer.pkl`, `syntax_error_model.pkl`, `label_encoder.pkl`, optional `numerical_features.pkl`) or a fallback bundle (`tfidf.pkl`, `error_classifier.pkl`, `label_encoder.pkl`).
  implication: Healthy mode depends on both version compatibility and the presence of one complete, correctly named artifact bundle.

- timestamp: 2026-03-27T14:55:07.7936042+05:30
  checked: local runtime and artifact directory
  found: The environment has `scikit-learn 1.7.2`; `models/` contains only the primary bundle files (`tfidf_vectorizer.pkl`, `syntax_error_model.pkl`, `label_encoder.pkl`, `numerical_features.pkl`) and no fallback `tfidf.pkl` or `error_classifier.pkl`.
  implication: The only shipped load path in this environment is the incompatible primary bundle; the fallback path is guaranteed to fail.

- timestamp: 2026-03-27T14:55:07.7936042+05:30
  checked: direct `src.ml_engine.get_model_status()` reproduction
  found: Model loading fails with `No module named 'sklearn.ensemble._gb_losses'` for `syntax_error_model.pkl`, plus a second fallback error for missing `models\\tfidf.pkl`; the status reports `loaded=False`, `sklearn_version='1.7.2'`, and `sklearn_compatible=False`.
  implication: The degraded `/health` result is caused by a concrete serialization/runtime mismatch, not by API wiring or detection logic.

- timestamp: 2026-03-27T14:55:53.4007212+05:30
  checked: local dataset and retrain preview path
  found: The training dataset exists at `dataset/merged/all_errors_v3.csv`, but `python scripts/retrain_model.py --preview` fails in the default Windows console with `UnicodeEncodeError` while printing box-drawing characters.
  implication: The repo has the data needed to rebuild artifacts, but the current recovery workflow is brittle on Windows unless UTF-8 output is enforced or the script stops emitting non-ASCII console glyphs.

- timestamp: 2026-03-27T15:11:53.8869186+05:30
  checked: retrain preview under UTF-8 and package import behavior
  found: `scripts/retrain_model.py --preview` succeeds when `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1` are set; `src/__init__.py` imports `ml_engine` transitively, which explains the degraded-model log emitted during retrain startup even though the script only needs `feature_utils`.
  implication: Rebuilding in the current environment is feasible, but the retrain path is unnecessarily coupled to runtime model loading and is not console-safe by default on Windows.

- timestamp: 2026-03-27T15:11:53.8869186+05:30
  checked: operator-supplied local reproduction
  found: Independent local reproduction confirmed the same `get_model_status()` failure, the same four files present in `models/`, and that `scripts/retrain_model.py` appears capable of regenerating the primary bundle from `dataset/merged/all_errors_v3.csv`.
  implication: The investigation evidence is consistent across runs; the issue is not intermittent or machine-specific within the current environment.

- timestamp: 2026-03-27T15:12:30.7435512+05:30
  checked: post-timeout artifact state and active Python processes
  found: `models/` file timestamps are unchanged after the timed-out full retrain attempt, while two long-running Python 3.10 processes remain active from the retrain window.
  implication: The timeout did not reach the save step; a clean, controlled retrain run is still required and may need explicit process cleanup first.

- timestamp: 2026-03-27T15:13:50.3492172+05:30
  checked: Python process command lines and retrain import paths
  found: The lingering Python 3.10 processes are both `scripts/retrain_model.py`; the script imports `src.feature_utils` and `src.utils.cli_colors`, which executes `src/__init__.py` and pulls in `ml_engine` as a side effect.
  implication: The rebuild workflow can be made cleaner by importing helper modules directly from `src/` without executing the package-level eager imports.

- timestamp: 2026-03-27T15:31:03.3986168+05:30
  checked: regenerated model bundle and direct `src.ml_engine.get_model_status()` output
  found: `models/` was regenerated in the current environment, `models/bundle_metadata.json` was added, and model status now reports `loaded=True`, `bundle_metadata_present=True`, `bundle_sklearn_version='1.7.2'`, `sklearn_version='1.7.2'`, `expected_sklearn_major_minor='1.7'`, and `sklearn_compatible=True`.
  implication: The runtime can now deserialize and use the primary bundle successfully in the current environment.

- timestamp: 2026-03-27T15:31:03.3986168+05:30
  checked: API health and retrain preview behavior
  found: `/health` now returns `healthy` with `ml_model_loaded=true` and no degraded reason, and `python scripts/retrain_model.py --preview` succeeds without manually setting `PYTHONIOENCODING`.
  implication: Both runtime health reporting and the operator recovery workflow are restored.

- timestamp: 2026-03-27T15:31:03.3986168+05:30
  checked: automated verification
  found: `python -m pytest tests/test_api_and_regressions.py -q` passed with `16 passed, 1 skipped, 1 xfailed`; `python -m pytest tests/test_script_smoke.py -q` passed with `6 passed`; `python -m pytest tests -q` passed with `87 passed, 1 skipped, 1 xfailed`.
  implication: The fix restored healthy mode without regressing the covered API, script, or repo-wide test behaviors.

## Resolution

root_cause: The checked-in `models/` bundle was serialized against scikit-learn 1.1.3, but the current environment runs 1.7.2, so unpickling `syntax_error_model.pkl` fails on the removed `sklearn.ensemble._gb_losses` module; the loader’s legacy fallback cannot recover because `models/tfidf.pkl` and `models/error_classifier.pkl` are not present.
fix: Added metadata-aware compatibility reporting in `src/ml_engine.py`, hardened `scripts/retrain_model.py` so bundle regeneration works without manual UTF-8 shell setup and without importing `ml_engine` as a side effect, added a regression test for bundle metadata handling, and regenerated the `models/` primary bundle plus `models/bundle_metadata.json` under scikit-learn 1.7.2.
verification: Direct model-status verification now reports `loaded=True` and compatible sklearn metadata; `/health` now reports `healthy` with `ml_model_loaded=true`; `python scripts/retrain_model.py --preview` succeeds without manual encoding overrides; `python -m pytest tests/test_api_and_regressions.py -q` => `16 passed, 1 skipped, 1 xfailed`; `python -m pytest tests/test_script_smoke.py -q` => `6 passed`; `python -m pytest tests -q` => `87 passed, 1 skipped, 1 xfailed`.
files_changed: [src/ml_engine.py, scripts/retrain_model.py, tests/test_api_and_regressions.py, models/syntax_error_model.pkl, models/tfidf_vectorizer.pkl, models/label_encoder.pkl, models/numerical_features.pkl, models/bundle_metadata.json]
