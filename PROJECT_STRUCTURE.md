# Project Structure

```
Hybrid_AI-Based_Multi-Language_Syntax_Error_Detection_System/
│
├── 📄 Core Files (Root)
│   ├── README.md                    # Main project documentation
│   ├── LICENSE                      # MIT License
│   ├── requirements.txt             # Python dependencies
│   ├── requirements-dev.txt         # Dev/test dependencies
│   ├── PROJECT_STATUS.md            # Current project status
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── .env                         # Environment variables (not in git)
│   └── .gitignore                   # Git ignore rules
│
├── 🚀 Application Entry Points
│   ├── api.py                       # FastAPI REST API (6 endpoints)
│   ├── start_api.py                 # API server launcher
│   ├── app.py                       # Streamlit web UI
│   └── cli.py                       # Command-line interface
│
├── 📚 src/ - Core Source Code (10 modules)
│   ├── __init__.py                  # Package exports
│   ├── error_engine.py              # Main error detection engine
│   ├── ml_engine.py                 # ML classifier (Gradient Boosting)
│   ├── language_detector.py         # Programming language detection
│   ├── syntax_checker.py            # Rule-based syntax checking
│   ├── auto_fix.py                  # Automatic error fixing
│   ├── tutor_explainer.py           # AI tutor explanations
│   ├── quality_analyzer.py          # Code quality analysis
│   ├── multi_error_detector.py      # Multi-error detection
│   └── feature_utils.py             # Centralized feature extraction
│
├── 🔬 scripts/ - Training & Utilities
│   ├── optimize_model.py            # Model training pipeline
│   ├── augment_data.py              # Data augmentation
│   ├── generate_results.py          # Results generation
│   ├── advanced_metrics.py          # Advanced evaluation metrics
│   ├── test_accuracy.py             # Accuracy testing script
│   ├── test_false_positives.py      # False positive testing
│   ├── evaluate_results_visualization.ipynb  # Results analysis notebook
│   └── utils/
│       ├── __init__.py
│       └── data_utils.py            # Shared data utilities
│
├── 🧪 tests/ - Unit Tests (46/46 passing)
│   ├── test_detection.py            # Comprehensive test suite
│   └── Test.java                    # Java test sample
│
├── 🤖 models/ - Trained ML Models
│   ├── syntax_error_model.pkl       # Gradient Boosting (87.26% accuracy)
│   ├── tfidf_vectorizer.pkl         # TF-IDF vectorizer (8K features)
│   ├── label_encoder.pkl            # Label encoder (18 classes)
│   └── numerical_features.pkl       # Feature names
│
├── 📊 dataset/ - Training Data (3,178 unique samples)
│   ├── active/
│   │   ├── python_errors.csv        # Python error seeds
│   │   ├── java_errors.csv          # Java error seeds
│   │   ├── c_errors.csv             # C error seeds
│   │   ├── cpp_errors.csv           # C++ error seeds
│   │   └── noerror_samples.csv      # Correct code samples
│   ├── merged/
│   │   └── all_errors_v2.csv        # Combined dataset (3,178 samples)
│   └── archieve/
│       ├── comprehensive_errors.jsonl
│       └── expanded_new_error_types_100_each.xlsx
│
├── 📈 results/ - Evaluation Results
│   ├── results.csv                  # Main results
│   ├── results.json                 # JSON format results
│   ├── optimized_results.csv        # Latest model results
│   └── advanced_metrics.txt         # Advanced metrics
│
├── 📝 samples/ - Test Code Samples
│   ├── missing_colon.py
│   ├── indentation_error.py
│   ├── unclosed_quote.py
│   ├── unmatched_paren.py
│   ├── test_division.py
│   └── test_error.py
│
└── 📖 docs/ - Documentation (12 files)
    ├── API_DOCUMENTATION.md         # API reference
    ├── QUICKSTART.md                # Quick start guide
    ├── CONTRIBUTING.md              # Contribution guidelines
    ├── PROJECT_SUMMARY.md           # Project overview
    ├── COMPREHENSIVE_TEST_REPORT.md # Test results
    ├── IMPROVEMENTS_SUMMARY.md      # Recent improvements
    ├── OPTIMIZATION_SUMMARY.md      # Model optimization details
    ├── INTEGRATION_SUMMARY.md       # Integration guide
    ├── ORGANIZATION.md              # Project organization
    ├── PAPER_ABSTRACT.md            # Research paper abstract
    ├── CHECKLIST.md                 # Development checklist
    └── SUGGESTIONS.md               # Feature suggestions
```

## 🎯 Quick Reference

### Run the Application
```bash
# Web UI (Streamlit)
python -m streamlit run app.py

# REST API
python start_api.py

# Command Line
python cli.py <file_path>
```

### Train/Evaluate Models
```bash
# Train optimized model
python scripts/optimize_model.py

# Retrain on current dataset
python retrain_model.py

# Augment training data
python augment_dataset.py
```

### Run Tests
```bash
# All tests (46/46 passing)
pytest tests/ -v

# Specific test
pytest tests/test_detection.py -v
```

## 📦 Package Information

- **Main Package**: `src/` (importable as `from src import ...`)
- **Scripts**: Standalone training/utility scripts in `scripts/`
- **Entry Points**: API, CLI, and Web UI at root level

## 🔒 Ignored Files (.gitignore)

- Virtual environments (`.venv/`, `venv/`)
- Cache directories (`__pycache__/`, `.pytest_cache/`)
- Environment files (`.env`)
- Debug models (`models/FAILED_*.pkl`)
- Backup files (`*.bak`, `*_old.*`)

## ✅ Project Health

- **Model Accuracy**: 87.26% (Gradient Boosting, genuine on unique data)
- **Test Coverage**: 46/46 tests passing
- **Supported Languages**: Python, Java, C, C++, JavaScript
- **Error Types**: 20
- **Documentation**: Complete (15 files)
- **Production Ready**: Yes

---

**Last Updated**: February 27, 2026  
**Status**: ✅ Clean, organized, production-ready
