---
status: investigating
trigger: "Investigate issue: ml-model-bundle-load-failure"
created: 2026-03-27T14:54:14.8730286+05:30
updated: 2026-03-27T14:54:14.8730286+05:30
---

## Current Focus

hypothesis: Model bundle loading fails because the checked-in artifacts do not match the current runtime contract.
test: Check for prior matched debug knowledge, inspect the `models/` contents, confirm the installed scikit-learn version, and reproduce `src.ml_engine` load behavior directly.
expecting: If true, the failure will show a concrete mismatch between loader expectations, artifact filenames, or serialized estimator compatibility.
next_action: Read `.planning/debug/knowledge-base.md` if present and gather initial runtime evidence from the local environment.

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

## Resolution

root_cause:
fix:
verification:
files_changed: []
