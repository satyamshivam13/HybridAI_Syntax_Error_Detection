# Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install & Setup
```bash
# Clone repository (if not done)
git clone <repository-url>
cd LLM_Syntax_Error_Checker

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Train Models (Optional - Pre-trained models included)
```bash
# Use the optimized training script
python scripts/optimize_model.py
```
**Time**: ~2-3 minutes  
**Output**: Models saved to `models/` folder with 99.80% accuracy  
**Note**: Pre-trained models are already included in `models/`

### 3. Test with Samples
```bash
# Test with provided samples
python cli.py samples/missing_colon.py
python cli.py samples/indentation_error.py
```

### 4. Launch Web Interface
```bash
streamlit run app.py
```
Open browser: `http://localhost:8501`

---

## 📝 Common Commands

```bash
# Run CLI on custom file
python cli.py path/to/your/code.py

# Start REST API server
python start_api.py
# Access at: http://localhost:8000/docs

# Launch Streamlit web UI
python -m streamlit run app.py

# Run all tests
pytest tests/ -v

# Train/optimize model
python scripts/optimize_model.py

# Augment training data
python scripts/augment_data.py

# Generate evaluation results
python scripts/generate_results.py

# View results in Jupyter
jupyter notebook evaluate_results_visualization.ipynb
```

---

## 🔍 Testing Different Error Types

### Python - Missing Colon
```python
# File: test_colon.py
def hello()
    print("Missing colon!")
```
```bash
python cli.py test_colon.py
```

### Python - Indentation Error
```python
# File: test_indent.py
def calculate():
print("Wrong indentation")
    return 5
```

### Python - Unmatched Brackets
```python
# File: test_bracket.py
result = (1 + 2 * 3
print(result)
```

---

## 🐛 Troubleshooting

### Issue: Models not found
**Solution**: Run `python evaluate.py` to train models

### Issue: ModuleNotFoundError
**Solution**: Activate virtual environment and reinstall:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Streamlit not loading
**Solution**: Check if port 8501 is available:
```bash
netstat -an | findstr :8501  # Windows
lsof -i :8501  # Linux/Mac
```

### Issue: Dataset not found
**Solution**: Ensure `dataset/merged/all_errors.csv` exists

---

## 📊 Understanding Output

### CLI Output Example
```
Language Detected: Python
Error Type: MissingColon
Confidence: 95%
Line: 2

Explanation:
Python functions require a colon (:) after the function definition.

Suggested Fix:
def hello():
    print("Fixed!")
```

### Web UI Features
- ✅ Paste code directly
- ✅ Upload file
- ✅ See explanations
- ✅ View suggested fixes
- ✅ Download corrected code

---

## 📈 Next Steps

1. **Customize Dataset**: Add your own error samples to `dataset/active/`
2. **Retrain Model**: Run `python evaluate.py` after adding data
3. **Extend Languages**: Add new language detection patterns
4. **Improve Explanations**: Edit `tutor_explainer.py`
5. **Add Error Types**: Update `syntax_checker.py` and `ml_engine.py`

---

## 💡 Tips

- **Use samples folder**: Pre-made test cases for quick validation
- **Check results.json**: See model performance metrics
- **Run notebook**: Visual analysis of model performance
- **Try different languages**: Test with Java, C, C++ files

---

## 🎯 Project Structure Quick Reference

```
Key Files:
├── app.py              → Web UI entry point
├── cli.py              → Command-line entry point
├── error_engine.py     → Main detection logic
├── evaluate.py         → Model training script
└── requirements.txt    → Dependencies

Key Folders:
├── dataset/merged/     → Training data
├── models/             → Trained ML models
├── results/            → Evaluation outputs
└── samples/            → Test cases
```

---

**Need help?** Check the main [README.md](README.md) for detailed documentation.
