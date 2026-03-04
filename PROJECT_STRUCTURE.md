# Project Structure

```
OmniSyntax/
├── api.py
├── app.py
├── cli.py
├── start_api.py
├── README.md
├── PROJECT_STATUS.md
├── PROJECT_STRUCTURE.md
├── requirements.txt
├── requirements-dev.txt
├── .env.template
├── src/
│   ├── __init__.py
│   ├── auto_fix.py
│   ├── error_engine.py
│   ├── feature_utils.py
│   ├── language_detector.py
│   ├── ml_engine.py
│   ├── multi_error_detector.py
│   ├── quality_analyzer.py
│   ├── syntax_checker.py
│   └── tutor_explainer.py
├── scripts/
│   ├── advanced_metrics.py
│   ├── augment_dataset.py
│   ├── check_links.py
│   ├── evaluate_results_visualization.py
│   ├── generate_results.py
│   ├── retrain_model.py
│   ├── test_accuracy.py
│   ├── test_false_positives.py
│   └── utils/
│       ├── __init__.py
│       └── data_utils.py
├── tests/
│   ├── Test.java
│   ├── test_api_and_regressions.py
│   ├── test_detection.py
│   └── test_script_smoke.py
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── COMPREHENSIVE_TEST_REPORT.md
│   ├── CONTRIBUTING.md
│   ├── PAPER_ABSTRACT.md
│   ├── PROJECT_SUMMARY.md
│   └── QUICKSTART.md
├── dataset/
├── models/
└── results/
```

## Notes
- `samples/` may be empty depending on snapshot; this is expected.
- CI workflow is in `.github/workflows/ci.yml`.
