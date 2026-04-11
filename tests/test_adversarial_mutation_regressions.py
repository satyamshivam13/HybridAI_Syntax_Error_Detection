from __future__ import annotations

from src.error_engine import detect_errors


def test_python_noise_unmatched_bracket_not_unclosed_string():
    code = """# adversarial-noise-header
items = [1, 2, 3
# trailing-noise
"""
    result = detect_errors(code, "x.py")
    assert result["predicted_error"] == "UnmatchedBracket"


def test_python_mutable_default_call_detected():
    code = """def tags(x, s=set()):
    s.add(x)
    return s
"""
    result = detect_errors(code, "x.py")
    assert result["predicted_error"] == "MutableDefault"


def test_python_self_reference_assignment_is_name_error():
    code = "missing_symbol_qa = missing_symbol_qa + missing_symbol_qa\n"
    result = detect_errors(code, "x.py")
    assert result["predicted_error"] == "NameError"


def test_python_dynamic_import_error_detected():
    code = """import importlib
mod = importlib.import_module('vendor_pkg_beta')
"""
    result = detect_errors(code, "x.py")
    assert result["predicted_error"] == "ImportError"


def test_python_list_annotation_type_mismatch_detected():
    code = "items: list[int] = ['a']\n"
    result = detect_errors(code, "x.py")
    assert result["predicted_error"] == "TypeMismatch"


def test_python_ctypes_pointer_pattern_detected_as_dangling():
    code = """import ctypes

def bad_ptr():
    value = ctypes.c_int(10)
    return ctypes.pointer(value)
"""
    result = detect_errors(code, "x.py")
    assert result["predicted_error"] == "DanglingPointer"


def test_java_throw_followed_by_statement_is_unreachable():
    code = """public class Main {
    static void f() {
        throw new RuntimeException();
        System.out.println(1);
    }
}
"""
    result = detect_errors(code, "Main.java")
    assert result["predicted_error"] == "UnreachableCode"


def test_java_final_reassignment_is_invalid_assignment():
    code = """public class Main {
    public static void main(String[] args) {
        final int x = 1;
        x = 2;
    }
}
"""
    result = detect_errors(code, "Main.java")
    assert result["predicted_error"] == "InvalidAssignment"


def test_cpp_missing_delimiter_stream_line_detected():
    code = """#include <iostream>
int main() {
    std::cout << 1
    return 0;
}
"""
    result = detect_errors(code, "x.cpp")
    assert result["predicted_error"] == "MissingDelimiter"


def test_js_throw_new_error_not_duplicate_definition():
    code = """function g() {
  throw new Error('x');
  let y = 1;
}
"""
    result = detect_errors(code, "x.js")
    assert result["predicted_error"] == "UnreachableCode"


def test_js_asi_ambiguity_missing_delimiter_detected():
    code = """const a = 1
const b = 2
console.log(a+b)
"""
    result = detect_errors(code, "x.js")
    assert result["predicted_error"] == "MissingDelimiter"
