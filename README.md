# 🧠 OmniSyntax: A Hybrid AI Code Tutor

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.18%2B-FF4B4B.svg)](https://streamlit.io/)
[![Accuracy](https://img.shields.io/badge/Accuracy-98.12%25-success.svg)](docs/PROJECT_SUMMARY.md)
[![Tests](https://img.shields.io/badge/Tests-47%2F47%20Passing-success.svg)](tests/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](PROJECT_STRUCTURE.md)

**Quick Links:** [🚀 Quick Start](docs/QUICKSTART.md) | [📁 Structure](PROJECT_STRUCTURE.md) | [🤝 Contributing](docs/CONTRIBUTING.md) | [📊 Results](results/01_confusion_matrix.png) | [📖 Documentation](docs/)

---

## 📁 Project Structure

```
Hybrid_AI-Based_Multi-Language_Syntax_Error_Detection_System/
├── 🚀 Entry Points
│   ├── app.py                      # Streamlit web interface
│   ├── cli.py                      # Command-line interface
│   ├── api.py                      # FastAPI REST API
│   └── start_api.py                # API server launcher
├── 📚 src/                         # Core engine modules
│   ├── error_engine.py            # Main detection orchestrator
│   ├── ml_engine.py               # ML model (98.12% accuracy)
│   ├── syntax_checker.py          # Rule-based AST parser
│   ├── language_detector.py       # Multi-language detection (score-based)
│   ├── tutor_explainer.py         # Error explanations
│   ├── auto_fix.py                # Automatic code fixes
│   ├── quality_analyzer.py        # Code quality metrics
│   ├── multi_error_detector.py    # Multi-error detection
│   └── feature_utils.py           # Shared ML feature extraction
├── 🤖 models/                      # Trained ML models (98.12%)
│   ├── syntax_error_model.pkl     # Gradient Boosting classifier
│   ├── tfidf_vectorizer.pkl       # TF-IDF vectorizer
│   ├── label_encoder.pkl          # Label encoder
│   └── numerical_features.pkl     # Feature names
├── 📊 dataset/                     # Training data (4,351 unique samples, 18 error types)
│   ├── active/                    # Current datasets by language
│   │   └── noerror_samples.csv    # No-error code samples (multi-language)
│   ├── merged/all_errors_v2.csv    # Combined dataset (4,351 unique samples)
│   └── archieve/                  # Historical datasets
├── 🔬 scripts/                     # Training & utilities
│   ├── retrain_model.py           # ✅ Model training pipeline
│   ├── advanced_metrics.py        # Performance metrics
│   ├── evaluate_results_visualization.py # Headless chart generator
│   └── evaluate_results_visualization.ipynb
├── 🧪 tests/                       # Unit tests (47/47 passing)
├── 📝 samples/                     # Example error files
├── 📈 results/                     # High-res Data Visualizations
├── 📖 docs/                        # Complete documentation
│   ├── QUICKSTART.md              # Quick start guide
│   ├── PROJECT_SUMMARY.md         # Technical overview
│   ├── PAPER_ABSTRACT.md          # Academic Paper Guide
│   └── ... (6 docs total)
├── PROJECT_STRUCTURE.md            # Detailed structure guide
├── README.md                       # This file
├── requirements.txt                # Production dependencies
└── requirements-dev.txt            # Development dependencies
```

**📋 See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete file structure**

---

## 📌 Overview

This project implements a hybrid AI-based system for detecting and explaining syntax errors in source code written in multiple programming languages.
The system is designed primarily for programming education, helping beginners understand why syntax errors occur and how to fix them, instead of only showing compiler messages.

The system combines:

**Rule-based static analysis** (deterministic, high confidence)

**Machine learning–based classification** (flexible, multi-language, **98.12% accuracy**)

This hybrid approach improves accuracy, interpretability, and learning effectiveness.

---

## 📚 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Technical architecture overview
- **[Optimization Details](docs/OPTIMIZATION_SUMMARY.md)** - How we achieved 98.12% accuracy
- **[Integration Guide](docs/INTEGRATION_SUMMARY.md)** - Auto-fix & quality analyzer features
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Research Abstract](docs/PAPER_ABSTRACT.md)** - Academic paper outline
- **[Development Checklist](docs/CHECKLIST.md)** - Project completion status
- **[Results & Metrics](results/)** - Model performance and evaluation data

---

## 🎯 Key Features

✅ **Multi-language Support**: Python, Java, C, C++, **JavaScript**

✅ **Automatic language detection**

✅ **Rule-based syntax detection** for Python (AST + token analysis)

✅ **ML-based error classification** using Gradient Boosting + TF-IDF (98.12% accuracy)

✅ **Multi-Error Detection** - Find ALL errors in code (not just first one)

✅ **REST API** - FastAPI-based API for CI/CD and external integrations

✅ **Automatic error fixing** - Language-aware code corrections (12 error types)

✅ **Code quality analysis** - Complexity metrics and improvement suggestions

✅ **Beginner-friendly error explanations** - 100% coverage for 19 error types

✅ **Streamlit web interface** with live preview and multi-error mode

✅ **Command-line interface (CLI)** for batch processing

✅ **Dataset-driven evaluation** with advanced metrics

---

## 🏗️ High-Level Architecture

```
Code Input
   ↓
Language Detection
   ↓
Rule-Based Analysis (Python)
   ↓
ML-Based Classification (Gradient Boosting + TF-IDF)
   ↓
Error Explanation (Tutor Module)
   ↓
Auto-Fix Suggestions (Language-aware)
   ↓
Code Quality Analysis (Metrics & Suggestions)
   ↓
Results Display (Web UI / CLI)
```



---

## 🎯 Error Types Detected

| Error Type | Python | Java | C/C++ | Detection Method |
|------------|--------|------|-------|------------------|
| **Missing Colon** | ✅ | ❌ | ❌ | Rule-based (AST) |
| **Missing Semicolon** | ❌ | ✅ | ✅ | ML + Pattern |
| **Indentation Errors** | ✅ | ❌ | ❌ | Rule-based (Token) |
| **Unmatched Brackets** | ✅ | ✅ | ✅ | Rule-based (Stack) |
| **Unclosed Quotes** | ✅ | ✅ | ✅ | Rule-based (String) |
| **Division by Zero** | ✅ | ✅ | ✅ | Static Analysis |
| **Undeclared Variables** | ⚠️ | ⚠️ | ⚠️ | ML-based (Limited) |

**Legend:**  
✅ Full Support | ⚠️ Partial/ML-based | ❌ Not Applicable

### Detection Coverage
- **Total Error Types**: 18 categories
- **Multi-language Support**: 5 languages (Python, Java, C, C++, JavaScript)
- **Hybrid Detection**: Rule-based (Symbolic AI) + ML-based (Gradient Boosting)

---

## 🤖 Machine Learning Details

**Model Architecture:**
- **Vectorization**: TF-IDF (5,000 char-level subword n-grams)
- **Classifier**: Gradient Boosting (100 estimators, max_depth=5)
- **Training Data**: 4,351 unique deduplicated samples across 5 languages
- **Features**: TF-IDF vectors + 10 deterministic numerical AST features

**Enhanced Numerical Features:**
1. Code length (characters)
2. Line count
3. Division operators detection
4. Type conversions
5. Missing colon patterns
6. Missing semicolon patterns
7. Zero comparison checks
8. String operations
9. Type declarations
10. Bracket balance score

**Training Split:**
- Training Set: 80%
- Test Set: 20%

**Performance Metrics:**
- **Overall Accuracy**: **98.12%**
- **Weighted Precision**: 98.13%
- **Weighted Recall**: 98.12%
- **Weighted F1-Score**: 98.11%
- **Per-Language Accuracy**: JavaScript (99.90%), C++ (98.59%), C (98.39%), Java (97.56%), Python (96.71%)

**Model Optimization Journey:**
- Initial: 87.8% (Logistic Regression)
- First optimization: 98.82% (Random Forest, but suffered from duplicate leakage)
- Overhaul: Merged duplicate error types, standardized on Gradient Boosting
- Final Benchmark: **98.12% genuine accuracy** on completely unique deduplicated data

**Role of ML:**
- Handles all languages with high accuracy
- Generalizes to unseen code patterns
- Works alongside rule-based detection
- Provides confidence scores for predictions

---

## 📊 Evaluation

The system is evaluated using:

- **Accuracy**: Overall correctness of predictions
- **Precision**: Ratio of correct positive predictions
- **Recall**: Ability to find all actual errors
- **F1-score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Visualization of prediction patterns
- **Per-error accuracy**: Performance breakdown by error type
- **Language-wise performance**: Accuracy across Python/Java/C/C++
- **Rule-based vs ML contribution**: Hybrid approach analysis

### 📈 Key Results

Based on evaluation results ([results.json](results/results.json)):

| Error Type | Recall | Precision | F1-Score |
|------------|--------|-----------|----------|
| MissingColon | 100% | 100% | 1.00 |
| UnmatchedBracket | 100% | 100% | 1.00 |
| IndentationError | 100% | 100% | 1.00 |
| UnclosedQuotes | 100% | 47.3% | 0.64 |

**Overall Recall**: 100% (No errors missed)

---

## 🎯 **Performance Metrics** (Optimized Model)

### 🏆 **Breakthrough Achievement: 98.12% Accuracy**

After targeted augmentation (+670 total samples) and model optimization with Gradient Boosting + enhanced feature engineering:

| Metric | Score | Improvement |
|--------|-------|-------------|
| **Overall Accuracy** | **98.12%** | +12.0% |
| Weighted Precision | 1.00 | +0.09 |
| Weighted Recall | 1.00 | +0.13 |
| Weighted F1-Score | 1.00 | +0.13 |
| Cohen's Kappa | 0.9996 | +0.16 |

### 🌍 **Language-Specific Performance**

| Language | Accuracy | Samples | Improvement |
|----------|----------|---------|-------------|
| **Python** | 99.91% | 1,161 | +5.91% |
| **C++** | 100% | 354 | +15.0% 🏆 |
| **C** | 100% | 535 | +22.0% ⭐ |
| **Java** | 100% | 501 | +19.0% 🏆 |

### 📈 **Top 10 Perfect Error Detections** (100% F1-Score)

1. ImportError
2. WildcardImport  
3. LineTooLong
4. UnreachableCode
5. UndeclaredIdentifier
6. MissingImport
7. MutableDefault
8. NameError
9. InfiniteLoop
10. IndentationError

### 🔍 **Key Optimizations**

1. **Enhanced Feature Engineering**: Added 10 numerical features (code length, bracket balance, delimiter detection)
2. **Advanced TF-IDF**: Character-level trigrams with 8,000 features (vs 5,000)
3. **Algorithm Upgrade**: Gradient Boosting (100 estimators) vs Random Forest
4. **Targeted Augmentation Phase 1**: +240 samples (TypeMismatch, DivisionByZero, MissingDelimiter)
5. **Targeted Augmentation Phase 2**: +430 samples for weak precision/recall errors
6. **Balanced Classes**: Class weights for minority error types

### 📊 Visualization

Detailed evaluation and visualizations are available in:
- **Jupyter Notebook**: [scripts/evaluate_results_visualization.ipynb](scripts/evaluate_results_visualization.ipynb)
- **Results Files**: [results/optimized_results.csv](results/optimized_results.csv), [results/advanced_metrics.txt](results/advanced_metrics.txt)
- **Training Scripts**: [scripts/optimize_model.py](scripts/optimize_model.py), [scripts/advanced_metrics.py](scripts/advanced_metrics.py)

Run the notebook to generate:
- Confusion matrices (98.12% accuracy)
- Per-language accuracy charts
- Error distribution plots
- Precision-recall curves
- Advanced metrics (Cohen's Kappa 0.9996, Matthews 0.9996)

---

## ▶️ How to Run the Project

### Prerequisites
- **Python**: 3.10 or higher
- **pip**: Package installer for Python
- **Git**: For cloning the repository

### 1️⃣ Create Virtual Environment (Required)
```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\Activate.ps1       # Windows PowerShell
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `streamlit==1.50.0` - Web interface
- `pandas` - Data manipulation
- `scikit-learn==1.7.2` - Machine learning (exact version required)
- `matplotlib`, `seaborn` - Visualization
- `joblib` - Model serialization

### 3️⃣ Pre-trained Models Ready!
✅ **No training needed!** The repository includes optimized models:
- `models/syntax_error_model.pkl` (Gradient Boosting, 98.12% accuracy)
- `models/tfidf_vectorizer.pkl` (8K features)
- `models/label_encoder.pkl`
- `models/numerical_features.pkl`

**Optional: Retrain models** (only if you modify the dataset)
```bash
python scripts/optimize_model.py
```

### 4️⃣ Run Web Application
```bash
# Make sure virtual environment is activated!
.venv\Scripts\Activate.ps1       # Windows
python -m streamlit run app.py
```

Access at: `http://localhost:8501`

**Features:**
- Live error detection
- Multi-Error Detection mode (🔍 Show All Errors checkbox)
- Auto-fix suggestions with preview
- Code quality analysis dashboard
- Multi-language support

### 5️⃣ Run REST API Server (NEW!)
```bash
python start_api.py
# or
python api.py
```

Access at: `http://localhost:8000`

**API Documentation:**
- Interactive Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Full Documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

**Available Endpoints:**
- `GET /health` - API status check
- `POST /check` - Detect errors in code
- `POST /fix` - Auto-fix syntax errors
- `POST /quality` - Analyze code quality
- `POST /check-and-fix` - Combined detection & fixing

### 6️⃣ Run CLI Tool
```bash
python cli.py <path_to_code_file>
```

**Examples:**
```bash
python cli.py samples/missing_colon.py
python cli.py tests/Test.java
python cli.py samples/unmatched_paren.py
```

**CLI Output includes:**
- Error detection (ML + Rule-based)
- Auto-fix suggestions
- Quality analysis with metrics
- Improvement suggestions

### 6️⃣ Run Tests
```bash
python -m pytest tests/test_detection.py -v
```

**Expected:** 46 tests passing (language detection, syntax checker, error engine, auto-fix, quality analyzer, multi-error detector, feature utils)

### 7️⃣ View Evaluation Notebook
Open `scripts/evaluate_results_visualization.ipynb` in Jupyter or VS Code to see:
- Confusion matrices (98.12% accuracy)
- Performance charts
- Language-wise analysis
- Advanced metrics visualization

---

## 🎓 Intended Use

- **Programming education** - CS1/CS2 courses and tutorials
- **Beginner debugging assistance** - Help students understand errors
- **Academic demonstrations** - Teaching tool for instructors
- **Final-year engineering project** - Capstone project showcase
- **Research experimentation** - Hybrid AI systems research

⚠️ **Note**: This system is not a compiler replacement. It is a learning-oriented diagnostic tool.

---

## 🚀 Future Enhancements

### Planned Features
- [ ] **Additional Language Support**
  - JavaScript/TypeScript
  - Go
  - Rust
  - PHP

- [x] **Multi-Error Detection** _(Completed)_
  - Detect multiple errors in single code snippet
  - Grouped by error type with tutor explanations

- [x] **REST API** _(Completed)_
  - FastAPI-based API with Swagger docs
  - Endpoints: `/check`, `/fix`, `/quality`, `/check-and-fix`
  - Configurable CORS, optional rate limiting

- [ ] **Improved Auto-correction**
  - Context-aware fixes
  - Multiple fix suggestions with confidence scores

- [ ] **IDE Plugin Integration**
  - VS Code extension
  - PyCharm plugin
  - Real-time error highlighting

- [ ] **Enhanced ML Models**
  - Transformer-based models (BERT, CodeBERT)
  - Fine-tuned LLMs for better context understanding
  - Optimized inference for faster detection

- [ ] **Educational Features**
  - Interactive tutorials
  - Gamified learning paths
  - Progress tracking for students

---

## 📚 Academic Note

All system claims are supported by implementation and evaluation.
The project follows standard software engineering and machine learning practices, making it suitable for:

- **Internal reviews**: Complete documentation and code structure
- **Final submissions**: Meets academic project requirements
- **IEEE-style research papers**: Reproducible methodology and results
- **Educational demonstrations**: Clear architecture and explanations

### 📊 Dataset Information
- **Total Samples**: 3,178 unique samples across 18 error types and 5 languages
- **Language Distribution**: Python (1,229), Java (698), C (682), C++ (569)
- **Error Categories**: 18 distinct types with cross-language balance, plus explicit NoError class
- **Cross-Language Errors**: 12 error types present in all applicable languages
- **Language-Specific Errors**: 8 error types (Python: 5, C/C++: 2, Java: 1)
- **Data Quality**: All samples genuinely unique — randomized variable names, code patterns, and structures
- **Source**: Custom-generated + real-world student code + targeted optimization + curated NoError samples

### 🛠️ Technical Stack
- **Backend**: Python 3.10+
- **ML Framework**: scikit-learn
- **Web Framework**: Streamlit
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **Version Control**: Git

### 🏆 Project Highlights
✅ **End-to-end ML pipeline** (data → training → deployment)
✅ **Hybrid architecture** (combines symbolic AI + statistical ML)
✅ **Production-ready** (Web UI + CLI + REST API)
✅ **Evaluation-driven** (Comprehensive metrics and visualizations)
✅ **Extensible design** (Easy to add new languages/error types)
✅ **Explicit NoError class** (robust detection of error-free code)

---

## 👨‍💻 Authors

**Team Members:**
- Satyam Shivam
- Dilip Kumar Anjana
- Kartik Arora
- Manan Shah

**Academic Year**: 2025-2026  
**Project Type**: Final Year Engineering Project  
**Domain**: Artificial Intelligence, Software Engineering, Programming Education

---

📄 **License**: [MIT License](LICENSE)  
🌟 **Contributions**: Welcome! See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines  
📧 **Contact**: Open an issue on GitHub for questions or support

---

**Recent Updates:**
- Fixed language detection: score-based approach prevents `printf` misclassification as Python
- Centralized ML feature extraction into `src/feature_utils.py` (eliminates code duplication)
- Expanded test suite from 13 to **46 tests** (auto-fix, quality, multi-error, edge cases)
- Refactored `multi_error_detector.py` to reuse `error_engine` validators
- Cleaned `requirements.txt`, separated dev dependencies into `requirements-dev.txt`
- Made CORS configurable via `CORS_ORIGINS` env var in API
- Added `dataset/active/noerror_samples.csv` (multi-language, error-free code)
- Merged NoError samples into `dataset/merged/all_errors_v2.csv`
- Updated scripts and models for improved NoError detection

---

*This project demonstrates the practical application of hybrid AI systems in educational technology, combining rule-based deterministic approaches with machine learning for robust multi-language syntax error detection.*
