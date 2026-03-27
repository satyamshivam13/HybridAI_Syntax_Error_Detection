# GSD Debug Knowledge Base

Resolved debug sessions. Used by `gsd-debugger` to surface known-pattern hypotheses at the start of new investigations.

---

## ml-model-bundle-load-failure — ML bundle failed to load after sklearn/runtime drift
- **Date:** 2026-03-27
- **Error patterns:** degraded, semantic ML classification skipped, sklearn version mismatch, missing fallback model file, sklearn.ensemble._gb_losses, tfidf.pkl, error_classifier.pkl
- **Root cause:** The checked-in `models/` bundle was serialized against scikit-learn 1.1.3, but the current environment runs 1.7.2, so unpickling `syntax_error_model.pkl` fails on the removed `sklearn.ensemble._gb_losses` module; the loader’s legacy fallback cannot recover because `models/tfidf.pkl` and `models/error_classifier.pkl` are not present.
- **Fix:** Added metadata-aware compatibility reporting in `src/ml_engine.py`, hardened `scripts/retrain_model.py` so bundle regeneration works without manual UTF-8 shell setup and without importing `ml_engine` as a side effect, added a regression test for bundle metadata handling, and regenerated the `models/` primary bundle plus `models/bundle_metadata.json` under scikit-learn 1.7.2.
- **Files changed:** src/ml_engine.py, scripts/retrain_model.py, tests/test_api_and_regressions.py, models/syntax_error_model.pkl, models/tfidf_vectorizer.pkl, models/label_encoder.pkl, models/numerical_features.pkl, models/bundle_metadata.json
---
