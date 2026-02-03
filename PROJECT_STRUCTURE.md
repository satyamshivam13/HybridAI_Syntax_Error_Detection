# Project Structure

```
Hybrid_AI-Based_Multi-Language_Syntax_Error_Detection_System/
│
├── 📄 Core Files (Root)
│   ├── README.md                    # Main project documentation
│   ├── LICENSE                      # License file
│   ├── requirements.txt             # Python dependencies
│   ├── .env                         # Environment variables (not in git)
│   └── .gitignore                   # Git ignore rules
│
├── 🚀 Application Entry Points
│   ├── api.py                       # FastAPI REST API implementation
│   ├── start_api.py                 # API server launcher
│   ├── app.py                       # Streamlit web UI
│   └── cli.py                       # Command-line interface
│
├── 📚 src/ - Core Source Code
│   ├── __init__.py
│   ├── error_engine.py              # Main error detection engine
│   ├── ml_engine.py                 # Machine learning classifier
│   ├── language_detector.py         # Programming language detection
│   ├── syntax_checker.py            # Rule-based syntax checking
│   ├── auto_fix.py                  # Automatic error fixing
│   ├── tutor_explainer.py           # AI tutor explanations
│   ├── quality_analyzer.py          # Code quality analysis
│   └── multi_error_detector.py      # Multi-error detection
│
├── 🔬 scripts/ - Training & Utilities
│   ├── optimize_model.py            # ✅ PRIMARY: Model training (99.8% accuracy)
│   ├── augment_data.py              # Data augmentation with deduplication
│   ├── generate_results.py          # Results generation
│   ├── advanced_metrics.py          # Advanced evaluation metrics
│   ├── evaluate_results_visualization.ipynb  # Results analysis notebook
│   └── utils/
│       ├── __init__.py
│       └── data_utils.py            # Shared data utilities
│
├── 🧪 tests/ - Unit Tests
│   ├── test_detection.py            # Error detection tests
│   ├── test_division.py             # Division error tests
│   ├── test_error.py                # General error tests
│   └── Test.java                    # Java test sample
│
├── 🤖 models/ - Trained ML Models
│   ├── syntax_error_model.pkl       # ✅ Gradient Boosting (99.8% accuracy)
│   ├── tfidf_vectorizer.pkl         # TF-IDF vectorizer
│   ├── label_encoder.pkl            # Label encoder
│   └── numerical_features.pkl       # Feature names
│
├── 📊 dataset/ - Training Data
│   ├── active/
│   │   ├── python_errors.csv
│   │   ├── java_errors.csv
│   │   ├── c_errors.csv
│   │   └── cpp_errors.csv
│   ├── merged/
│   │   └── all_errors.csv           # Combined dataset (2551 samples)
│   └── archieve/
│       └── comprehensive_errors.jsonl
│
├── 📈 results/ - Evaluation Results
│   ├── results.csv                  # Main results
│   ├── results.json                 # JSON format results
│   ├── optimized_results.csv        # Optimized model results
│   └── advanced_metrics.txt         # Advanced metrics
│
├── 💾 data/ - Runtime Data
│   └── results.csv                  # Runtime results
│
├── 🖼️ screenshots/ - UI Screenshots
│   └── (interface screenshots)
│
├── 📝 samples/ - Test Code Samples
│   ├── missing_colon.py
│   ├── indentation_error.py
│   ├── unclosed_quote.py
│   └── unmatched_paren.py
│
├── 📖 docs/ - Documentation
│   ├── API_DOCUMENTATION.md         # API reference
│   ├── QUICKSTART.md                # Quick start guide
│   ├── CONTRIBUTING.md              # Contribution guidelines
│   ├── PROJECT_SUMMARY.md           # Project overview
│   ├── COMPREHENSIVE_TEST_REPORT.md # Test results
│   ├── IMPROVEMENTS_SUMMARY.md      # Recent improvements
│   ├── OPTIMIZATION_SUMMARY.md      # Model optimization details
│   ├── INTEGRATION_SUMMARY.md       # Integration guide
│   ├── ORGANIZATION.md              # Project organization
│   ├── PAPER_ABSTRACT.md            # Research paper abstract
│   ├── CHECKLIST.md                 # Development checklist
│   └── SUGGESTIONS.md               # Feature suggestions
│
└── 🔧 experiments/ - Experiment Tracking
    └── (empty - ready for MLflow/W&B logs)

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
# Train optimized model (recommended)
python scripts/optimize_model.py

# Augment training data
python scripts/augment_data.py

# View results in notebook
jupyter notebook scripts/evaluate_results_visualization.ipynb
```

### Run Tests
```bash
# All tests
pytest tests/

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
- Experiment tracking (`mlruns/`, `wandb/`)
- Backup files (`*.bak`, `*_old.*`)

## ✅ Project Health

- **Model Accuracy**: 99.80% (Gradient Boosting)
- **Test Coverage**: 13/13 tests passing
- **Supported Languages**: Python, Java, C, C++
- **Documentation**: Complete
- **Production Ready**: Yes

---

**Last Updated**: February 3, 2026  
**Status**: ✅ Clean, organized, production-ready
