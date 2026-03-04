"""
Comprehensive Unit Tests for OmniSyntax
Covers: language detection, syntax checker, error engine, auto-fix,
        quality analyzer, multi-error detector, and feature utils.
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.language_detector import detect_language
from src.syntax_checker import detect_all, try_ast_parse
from src.error_engine import detect_errors
from src.auto_fix import AutoFixer
from src.quality_analyzer import CodeQualityAnalyzer
from src.multi_error_detector import detect_all_errors
from src.feature_utils import extract_numerical_features, NUMERICAL_FEATURE_NAMES


# ==============================================================
# 1. Language Detection Tests
# ==============================================================
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
        code = '#include <iostream>\nusing namespace std;\nint main() { cout << "test"; }'
        self.assertEqual(detect_language(code), "C++")

    def test_javascript_detection(self):
        code = "const hello = () => { console.log('Hi'); }"
        self.assertEqual(detect_language(code), "JavaScript")

class TestLanguageDetectorEdgeCases(unittest.TestCase):
    """Tests for the printf-vs-print bug fix and other edge cases."""

    def test_c_printf_not_python(self):
        """printf() should be detected as C, NOT Python."""
        code = '#include <stdio.h>\nint main() { printf("hello"); return 0; }'
        self.assertEqual(detect_language(code), "C")

    def test_c_printf_without_include(self):
        """Even without #include, printf should suggest C."""
        code = 'int main() { printf("hello"); return 0; }'
        self.assertEqual(detect_language(code), "C")

    def test_filename_overrides_content(self):
        """Filename extension should take priority over content heuristics."""
        code = "def hello():\n    print('Hi')"  # Python-like content
        self.assertEqual(detect_language(code, "test.java"), "Java")

    def test_filename_py(self):
        self.assertEqual(detect_language("anything", "script.py"), "Python")

    def test_filename_c(self):
        self.assertEqual(detect_language("anything", "main.c"), "C")

    def test_filename_cpp(self):
        self.assertEqual(detect_language("anything", "main.cpp"), "C++")

    def test_unknown_language(self):
        code = "42"
        self.assertEqual(detect_language(code), "Unknown")

    def test_java_system_out(self):
        code = 'System.out.println("hello");'
        self.assertEqual(detect_language(code), "Java")

    def test_cpp_cout(self):
        code = 'cout << "hello" << endl;'
        self.assertEqual(detect_language(code), "C++")

    def test_python_elif(self):
        """elif is Python-specific."""
        code = "if x:\n    pass\nelif y:\n    pass"
        self.assertEqual(detect_language(code), "Python")


# ==============================================================
# 2. Syntax Checker Tests
# ==============================================================
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


# ==============================================================
# 3. Error Engine Tests
# ==============================================================
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


class TestErrorEngineJavaCCpp(unittest.TestCase):
    """Tests for Java/C/C++ error detection paths."""

    def test_java_valid_code(self):
        code = 'public class T { public static void main(String[] a) { System.out.println("hi"); } }'
        result = detect_errors(code, "T.java")
        self.assertEqual(result['predicted_error'], "NoError")
        self.assertEqual(result['language'], "Java")

    def test_java_missing_semicolon(self):
        """Missing semicolon on a standalone statement line should be caught."""
        code = 'public class T {\n  public static void main(String[] a) {\n    int x = 5\n  }\n}'
        result = detect_errors(code, "T.java")
        self.assertIn(result['predicted_error'], ["MissingDelimiter", "UnmatchedBracket"])

    def test_c_valid_code(self):
        code = '#include <stdio.h>\nint main() { printf("hello"); return 0; }'
        result = detect_errors(code, "test.c")
        self.assertEqual(result['predicted_error'], "NoError")

    def test_c_unmatched_bracket(self):
        code = '#include <stdio.h>\nint main() { printf("hello"); return 0; '
        result = detect_errors(code, "test.c")
        self.assertEqual(result['predicted_error'], "UnmatchedBracket")

    def test_python_unclosed_string(self):
        code = "x = 'hello"
        result = detect_errors(code, "test.py")
        self.assertIn(result['predicted_error'], ["UnclosedString", "UnclosedQuotes"])

    def test_python_indentation_error(self):
        code = "def test():\npass"
        result = detect_errors(code, "test.py")
        self.assertEqual(result['predicted_error'], "IndentationError")

    def test_python_unmatched_bracket(self):
        code = "print((1+2)"
        result = detect_errors(code, "test.py")
        self.assertNotEqual(result['predicted_error'], "NoError")

    def test_result_has_tutor(self):
        """Every error result should include a tutor explanation."""
        code = "def test()\n    pass"
        result = detect_errors(code, "test.py")
        self.assertIn('tutor', result)
        self.assertIn('why', result['tutor'])
        self.assertIn('fix', result['tutor'])


# ==============================================================
# 4. Auto-Fix Tests
# ==============================================================
class TestAutoFixer(unittest.TestCase):
    def setUp(self):
        self.fixer = AutoFixer()

    def test_fix_missing_colon(self):
        code = "def test()\n    pass"
        result = self.fixer.apply_fixes(code, "MissingDelimiter", 0, "Python")
        self.assertTrue(result['success'])
        self.assertIn(":", result['fixed_code'])
        self.assertTrue(len(result['changes']) > 0)

    def test_fix_indentation(self):
        code = "  print('hi')\n    print('bye')"
        result = self.fixer.apply_fixes(code, "IndentationError", None, "Python")
        self.assertTrue(result['success'])

    def test_fix_unmatched_brackets(self):
        code = "print((1+2)"
        result = self.fixer.apply_fixes(code, "UnmatchedBracket", None, "Python")
        self.assertTrue(result['success'])

    def test_fix_returns_dict(self):
        """Fix result always has fixed_code, changes, success keys."""
        code = "x = 1"
        result = self.fixer.apply_fixes(code, "UnknownType", None, "Python")
        self.assertIn('fixed_code', result)
        self.assertIn('changes', result)
        self.assertIn('success', result)


# ==============================================================
# 5. Quality Analyzer Tests
# ==============================================================
class TestQualityAnalyzer(unittest.TestCase):
    def test_basic_quality_score(self):
        code = "def test():\n    pass"
        qa = CodeQualityAnalyzer(code, "Python")
        report = qa.analyze()
        self.assertIn('quality_score', report)
        self.assertGreaterEqual(report['quality_score'], 0)
        self.assertLessEqual(report['quality_score'], 100)

    def test_complexity(self):
        code = "x = 1\ny = 2\nz = x + y"
        qa = CodeQualityAnalyzer(code, "Python")
        report = qa.analyze()
        self.assertIn('complexity', report)
        self.assertIsInstance(report['complexity'], int)

    def test_line_counts(self):
        code = "# comment\nx = 1\n\ny = 2"
        qa = CodeQualityAnalyzer(code, "Python")
        report = qa.analyze()
        self.assertIn('line_counts', report)
        self.assertIn('code', report['line_counts'])
        self.assertIn('comments', report['line_counts'])
        self.assertIn('blank', report['line_counts'])

    def test_suggestions_is_list(self):
        code = "x = 1"
        qa = CodeQualityAnalyzer(code, "Python")
        report = qa.analyze()
        self.assertIsInstance(report['suggestions'], list)


# ==============================================================
# 6. Multi-Error Detector Tests
# ==============================================================
class TestMultiErrorDetector(unittest.TestCase):
    def test_multi_error_python(self):
        """Code with multiple issues should report all of them."""
        code = "def test()\n    x = 'hello\nprint((1+2)"
        result = detect_all_errors(code)
        self.assertTrue(result['has_errors'])
        self.assertGreater(result['total_errors'], 0)
        self.assertEqual(result['language'], "Python")

    def test_no_error_python(self):
        code = "def test():\n    pass"
        result = detect_all_errors(code, "test.py")
        self.assertFalse(result['has_errors'])
        self.assertEqual(result['total_errors'], 0)

    def test_result_structure(self):
        code = "x = 1"
        result = detect_all_errors(code, "test.py")
        self.assertIn('language', result)
        self.assertIn('errors', result)
        self.assertIn('total_errors', result)
        self.assertIn('has_errors', result)


# ==============================================================
# 7. Feature Utils Tests
# ==============================================================
class TestFeatureUtils(unittest.TestCase):
    def test_feature_names_count(self):
        self.assertEqual(len(NUMERICAL_FEATURE_NAMES), 10)

    def test_extract_returns_10_features(self):
        code = "x = 1"
        features = extract_numerical_features(code)
        self.assertEqual(len(features), 10)

    def test_code_length_feature(self):
        code = "hello"
        features = extract_numerical_features(code)
        self.assertEqual(features[0], len(code))  # code_length

    def test_bracket_diff_feature(self):
        code = "print((1+2)"  # 2 opens, 1 close → diff = 1
        features = extract_numerical_features(code)
        self.assertEqual(features[9], 1)  # bracket_diff


# ==============================================================
# Pytest-style tests (backward compatibility)
# ==============================================================
import pytest
from src.error_engine import detect_errors as src_detect_errors

def test_missing_colon_python():
    code = "def test()\n    pass"
    result = src_detect_errors(code)
    assert result["predicted_error"] == "MissingDelimiter"

def test_no_error_python():
    code = "def test():\n    pass"
    result = src_detect_errors(code)
    assert result["predicted_error"] == "NoError"


if __name__ == '__main__':
    unittest.main()
