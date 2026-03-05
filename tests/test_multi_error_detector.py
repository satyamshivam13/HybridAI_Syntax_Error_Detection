import pytest
from src.multi_error_detector import detect_all_errors
from src.ml_engine import ModelUnavailableError, ModelInferenceError

# --- Test Data & Mocks ---

def mock_detect_language(code, filename):
    return "Python" # Simplify for tests unless overridden

# --- Python Tests ---

def test_python_valid_code_skips_ml():
    """Test that valid Python code does not fall through to the ML scanner, preventing hallucinations."""
    # This code is syntactically purely valid
    code = "def foo():\n    print('hello world')"
    result = detect_all_errors(code, "test.py")
    
    assert result['language'] == 'Python'
    assert result['has_errors'] is False
    assert result['total_errors'] == 0
    assert len(result['errors']) == 0

def test_python_invalid_code_triggers_rules_and_ml(monkeypatch):
    """Test that invalid Python code triggers rule-based checks and correctly falls back to ML."""
    
    # 1. Mock the rule scanner to simulate missing an error
    def mock_detect_all(code):
        return [] # Rule scanner found nothing!
    
    monkeypatch.setattr("src.multi_error_detector.detect_all", mock_detect_all)
    
    # 2. Mock the ML scanner to catch it
    def mock_ml_detect(code):
        return ("MissingColon", 0.95) # ML caught it!
        
    monkeypatch.setattr("src.multi_error_detector.detect_error_ml", mock_ml_detect)
    
    code = "def foo()\n    print('hello')" # Invalid Python
    result = detect_all_errors(code, "test.py")
    
    assert result['language'] == 'Python'
    assert result['has_errors'] is True
    assert result['total_errors'] == 1
    assert result['errors'][0]['type'] == 'MissingColon'
    assert result['errors'][0]['locations'][0]['ml_detected'] is True

def test_python_rules_override_ml_duplication(monkeypatch):
    """Test that if the rule scanner finds an error, the ML scanner doesn't add a duplicate."""
    
    # 1. Mock rule scanner to find the error
    def mock_detect_all(code):
        return [{'type': 'MissingColon', 'line': 1, 'message': 'Missing colon', 'snippet': 'def foo()'}]
    
    monkeypatch.setattr("src.multi_error_detector.detect_all", mock_detect_all)
    
    # 2. Mock the ML scanner to find the EXACT SAME error
    def mock_ml_detect(code):
        return ("MissingColon", 0.95)
        
    monkeypatch.setattr("src.multi_error_detector.detect_error_ml", mock_ml_detect)
    
    code = "def foo()\n    print('hello')"
    result = detect_all_errors(code, "test.py")
    
    assert result['has_errors'] is True
    assert result['total_errors'] == 1
    assert len(result['errors']) == 1
    # Check that it's NOT the ML version (evaluating the dict structure)
    assert 'ml_detected' not in result['errors'][0]['locations'][0]
    assert result['errors'][0]['locations'][0]['line'] == 1


# --- Java / C / C++ Tests ---

@pytest.mark.parametrize("language, code, expected_error", [
    ("Java", "class Main { public static void main(String[] args) ", "UnmatchedBracket"),
    ("C", 'int main() { int x = 1 printf("hello"); }', "MissingDelimiter"),
    ("C++", 'int main() { printf("hello ); return 0; }', "UnclosedString"),
])
def test_compiled_languages_structural_rules(monkeypatch, language, code, expected_error):
    """Test that structural rules (braces, semicolons, quotes) work for compiled languages."""
    
    # Mock language detection
    monkeypatch.setattr("src.multi_error_detector.detect_language", lambda c, f: language)
    
    # Mock ML to return nothing to isolate structural rule testing
    monkeypatch.setattr("src.multi_error_detector.detect_error_ml", lambda c: ("NoError", 0.0))
    
    result = detect_all_errors(code, f"test.{language.lower()}")
    
    assert result['has_errors'] is True
    
    error_types = [err['type'] for err in result['errors']]
    assert expected_error in error_types


# --- Edge Cases & ML Mocks ---

def test_ml_low_confidence_is_ignored(monkeypatch):
    """Test that low confidence ML predictions are discarded."""
    monkeypatch.setattr("src.multi_error_detector.detect_language", lambda c, f: "Java")
    monkeypatch.setattr("src.multi_error_detector.detect_error_ml", lambda c: ("MissingColon", 0.60)) # Below 0.65 threshold
    
    code = "class Main {}" # Valid code
    result = detect_all_errors(code, "test.java")
    
    assert result['has_errors'] is False
    assert result['total_errors'] == 0


def test_ml_unavailable_error_is_handled_gracefully(monkeypatch):
    """Test that ModelUnavailableError doesn't crash the pipeline."""
    monkeypatch.setattr("src.multi_error_detector.detect_language", lambda c, f: "JavaScript") # Unsupported language to bypass rules
    
    def raise_error(code):
        raise ModelUnavailableError("Model offline")
        
    monkeypatch.setattr("src.multi_error_detector.detect_error_ml", raise_error)
    
    code = "console.log('hello');"
    result = detect_all_errors(code, "test.js")
    
    assert result['language'] == 'JavaScript'
    assert result['has_errors'] is False # Gracefully degraded to no errors instead of crashing
