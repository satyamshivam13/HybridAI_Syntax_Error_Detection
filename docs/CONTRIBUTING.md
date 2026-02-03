# Contributing to Hybrid AI-Based Multi-Language Syntax Error Detection System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

**Current Status**: Production Ready (99.80% accuracy, 13/13 tests passing)

## 🤝 How to Contribute

### 1. Report Bugs
- Use GitHub Issues to report bugs
- Include code samples that trigger the bug
- Specify your environment (OS, Python version)
- Describe expected vs actual behavior

### 2. Suggest Features
- Open a GitHub Issue with the "enhancement" label
- Describe the feature and its use case
- Explain how it fits the project's educational goals

### 3. Submit Code
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## 📝 Code Style Guidelines

### Python Code
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small (<50 lines)
- Add type hints where appropriate

```python
def detect_error(code: str, language: str) -> dict:
    """
    Detect syntax errors in code
    
    Args:
        code: Source code to analyze
        language: Programming language (python, java, c, cpp)
    
    Returns:
        dict: {
            'error_type': str,
            'confidence': float,
            'line': int
        }
    """
    pass
```

### Commit Messages
```
feat: Add support for JavaScript detection
fix: Correct indentation detection for tabs
docs: Update installation instructions
test: Add unit tests for bracket matching
refactor: Simplify error classification logic
```

## 🧪 Testing

### Before Submitting
1. **Run existing tests**
   ```bash
   python -m pytest tests/
   ```

2. **Test with samples**
   ```bash
   python cli.py samples/missing_colon.py
   python cli.py samples/indentation_error.py
   ```

3. **Test web UI**
   ```bash
   streamlit run app.py
   ```

4. **Verify model training**
   ```bash
   python evaluate.py
   ```

### Adding Tests
- Place tests in `tests/` directory
- Name test files: `test_<module>.py`
- Use descriptive test function names

```python
def test_missing_colon_detection():
    code = "def hello()\n    print('test')"
    result = detect_syntax_error(code, "python")
    assert result['error_type'] == 'MissingColon'
```

## 📦 Adding New Features

### Adding a New Error Type

1. **Update Dataset**
   - Add samples to `dataset/active/<language>_errors.csv`
   - Format: `buggy_code,error_type,language`

2. **Update Rule-based Detection** (if applicable)
   ```python
   # In syntax_checker.py
   def check_new_error(self, code: str) -> dict:
       # Implement detection logic
       pass
   ```

3. **Update Explanations**
   ```python
   # In tutor_explainer.py
   explanations = {
       'NewErrorType': {
           'description': 'Clear explanation',
           'example': 'Code example',
           'fix': 'How to fix it'
       }
   }
   ```

4. **Retrain Model**
   ```bash
   python evaluate.py
   ```

5. **Test Thoroughly**
   ```bash
   python cli.py test_cases/new_error.py
   ```

### Adding a New Language

1. **Update Language Detector**
   ```python
   # In language_detector.py
   def detect_language(code: str) -> str:
       # Add new language patterns
       if 'function' in code and code.count('{') > 2:
           return 'javascript'
   ```

2. **Create Dataset**
   - Add `dataset/active/newlang_errors.csv`

3. **Update Error Patterns**
   ```python
   # In syntax_checker.py or ml_engine.py
   # Add language-specific rules
   ```

4. **Update Documentation**
   - Add to README.md supported languages
   - Update error type table

## 🎨 UI/UX Contributions

### Streamlit Web Interface
- Keep interface simple and intuitive
- Follow existing color scheme
- Add helpful tooltips and explanations
- Test on different screen sizes

### CLI Interface
- Maintain consistent output format
- Use clear, colored output (if terminal supports)
- Provide progress indicators for long operations

## 📚 Documentation

### What to Document
- New features and APIs
- Configuration options
- Architecture changes
- Troubleshooting steps

### Where to Document
- **README.md**: Main project documentation
- **QUICKSTART.md**: Quick setup instructions
- **Code comments**: Explain complex logic
- **Docstrings**: All public functions/classes

## 🔍 Review Process

### Pull Request Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Screenshots included (for UI changes)

### Review Timeline
- Initial review: Within 2-3 days
- Follow-up reviews: Within 1-2 days
- Merge: After approval from maintainer

## 🚫 What NOT to Contribute

- **Unrelated features**: Keep focus on syntax error detection
- **Breaking changes**: Without discussion first
- **Large refactors**: Without prior approval
- **Proprietary code**: Only open-source contributions
- **Copied code**: Without proper attribution and license

## 💬 Communication

### Getting Help
- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Feature Ideas**: Open an Issue with "enhancement" label

### Code of Conduct
- Be respectful and constructive
- Welcome newcomers
- Focus on the idea, not the person
- Give credit where due

## 🎓 Academic Contributions

Since this is an academic project:
- Cite any research papers or algorithms used
- Document theoretical foundations
- Include references in comments
- Maintain academic integrity

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Credited in academic presentations (with permission)

---

Thank you for helping improve this educational tool! Your contributions help students worldwide learn programming more effectively.

**Questions?** Open an issue or discussion on GitHub.
