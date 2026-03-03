# Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install & Setup
```bash
# Clone repository
git clone https://github.com/satyamshivam13/HybridAI_Syntax_Error_Detection.git
cd Hybrid_AI-Based_Multi-Language_Syntax_Error_Detection_System

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
**Time**: ~5-10 minutes  
**Output**: Models saved to `models/` folder  
**Note**: Pre-trained models are already included in `models/`

### 3. Test with Samples
```bash
# Test with provided samples
python cli.py samples/missing_colon.py
python cli.py samples/indentation_error.py
```

### 4. Launch Web Interface
```bash
python -m streamlit run app.py
```
Open browser: `http://localhost:8501`

### 5. Launch REST API
```bash
python start_api.py
```
Open docs: `http://localhost:8000/docs`

### 6. Deploy to Streamlit Cloud (Free Hosting)
You can deploy your main `app.py` for free in minutes.
1. Push this entire repository to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in.
3. Click **"New app"**, select your repository, set the main file path to `app.py`.
4. Click **Deploy**. The app will build using `requirements.txt`.

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

# Run all tests (46/46 passing)
pytest tests/ -v

# Train/optimize model
python scripts/optimize_model.py

# Retrain model on current dataset
python retrain_model.py

# Augment training data
python augment_dataset.py
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

### Java - Missing Semicolon
```java
// File: Test.java
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello")
    }
}
```

---

## 🐛 Troubleshooting

### Issue: Models not found
**Solution**: Run `python scripts/optimize_model.py` to train models

### Issue: ModuleNotFoundError
**Solution**: Activate virtual environment and reinstall:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Dataset not found
**Solution**: Ensure `dataset/merged/all_errors_v2.csv` exists

### Issue: Streamlit not loading
**Solution**: Check if port 8501 is available

---

## 📊 Understanding Output

### CLI Output Example
```
============================================================
🧠 Multi-Language Syntax Error Checker (CLI)
============================================================
📂 File        : test_colon.py
🗂 Language    : Python
🤖 ML Error    : MissingDelimiter

⚠️ Rule-Based Issues:
  1. Missing colon after function definition

🔧 AUTO-FIX SUGGESTION
✅ Automatic fix available!

📊 CODE QUALITY ANALYSIS
Quality Score  : 45/100
```

---

## 🎯 Project Structure Quick Reference

```
Key Files:
├── app.py              → Web UI entry point
├── cli.py              → Command-line entry point
├── api.py              → REST API
├── src/error_engine.py → Main detection logic
└── requirements.txt    → Dependencies

Key Folders:
├── dataset/merged/     → Training data (all_errors_v2.csv)
├── models/             → Trained ML models
├── results/            → Evaluation outputs
└── samples/            → Test cases
```

---

**Need help?** Check the main [README.md](../README.md) for detailed documentation.
