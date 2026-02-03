"""
Unit Tests for Syntax Error Detection System
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.language_detector import detect_language
from src.syntax_checker import detect_all, try_ast_parse
from src.error_engine import detect_errors

class TestLanguageDetector(unittest.TestCase):
    def test_python_detection(self):
        code = "def hello():\n    print('Hi')"
        self.assertEqual(detect_language(code), "Python")
    
    def test_java_detection(self):
        code = "public class Main { public static void main(String[] args) {} }"
        self.assertEqual(detect_language(code), "Java")
    
    def test_c_detection(self):
        code = "#include <stdio.h>\nint main() { return 0; }"
        self.assertEqual(detect_language(code), "C")
    
    def test_cpp_detection(self):
        code = "#include <iostream>\nusing namespace std;\nint main() { cout << \"test\"; }"
        self.assertEqual(detect_language(code), "C++")

class TestSyntaxChecker(unittest.TestCase):
    def test_valid_python_code(self):
        code = "def test():\n    pass"
        errors = detect_all(code)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_python_code(self):
        code = "def test()\n    pass"  # Missing colon
        errors = detect_all(code)
        self.assertTrue(len(errors) > 0)
    
    def test_ast_parse_valid(self):
        code = "x = 42"
        success, error = try_ast_parse(code)
        self.assertTrue(success)
    
    def test_ast_parse_invalid(self):
        code = "def test()"  # Incomplete
        success, error = try_ast_parse(code)
        self.assertFalse(success)

class TestErrorEngine(unittest.TestCase):
    def test_python_error_detection(self):
        code = "def test()\n    pass"  # Missing colon
        result = detect_errors(code, "test.py")
        self.assertIsNotNone(result)
        self.assertEqual(result['language'], "Python")
    
    def test_valid_code_detection(self):
        code = "def test():\n    pass"
        result = detect_errors(code, "test.py")
        self.assertEqual(result['predicted_error'], "NoError")
    
    def test_language_detection_with_filename(self):
        code = "// some code"
        result = detect_errors(code, "Test.java")
        self.assertEqual(result['language'], "Java")


# Pytest-style tests
import pytest
from src.error_engine import detect_errors as src_detect_errors

def test_missing_colon_python():
    code = "def test()\n    pass"
    result = src_detect_errors(code)
    assert result["predicted_error"] == "MissingColon"

def test_no_error_python():
    code = "def test():\n    pass"
    result = src_detect_errors(code)
    assert result["predicted_error"] == "NoError"

if __name__ == '__main__':
    unittest.main()

