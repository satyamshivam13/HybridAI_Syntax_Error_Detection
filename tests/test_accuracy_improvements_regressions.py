from __future__ import annotations

from src.error_engine import detect_errors


def test_c_division_by_zero_via_zero_variable():
    code = """int main() {
    int a = 10;
    int b = 0;
    int c = a / b;
    return c;
}"""
    result = detect_errors(code, "x.c")
    assert result["predicted_error"] == "DivisionByZero"


def test_cpp_division_by_zero_via_zero_variable():
    code = """int main() {
    int x = 10;
    int y = 0;
    return x / y;
}"""
    result = detect_errors(code, "x.cpp")
    assert result["predicted_error"] == "DivisionByZero"


def test_cpp_missing_iostream_include_for_cout():
    code = """int main() {
    std::cout << 10;
    return 0;
}"""
    result = detect_errors(code, "x.cpp")
    assert result["predicted_error"] == "MissingInclude"


def test_cpp_function_with_inline_return_is_not_unreachable():
    code = """#include <iostream>
int add(int a, int b) { return a + b; }
int main() {
    std::cout << add(2, 3);
    return 0;
}"""
    result = detect_errors(code, "x.cpp")
    assert result["predicted_error"] == "NoError"


def test_python_name_error_not_missing_import():
    code = """def f():
    return x + 1
print(f())"""
    result = detect_errors(code, "x.py")
    assert result["predicted_error"] == "NameError"


def test_python_wildcard_import_has_line_info():
    code = """from math import *
print(sqrt(4))"""
    result = detect_errors(code, "x.py")
    assert result["predicted_error"] == "WildcardImport"
    issues = [i for i in result.get("rule_based_issues", []) if i.get("type") == "WildcardImport"]
    assert issues and issues[0].get("line") == 1


def test_c_undeclared_identifier_is_detected():
    code = """int main() {
    int a = 1;
    return b;
}"""
    result = detect_errors(code, "x.c")
    assert result["predicted_error"] == "UndeclaredIdentifier"


def test_cpp_size_t_loop_does_not_trigger_undeclared_size_t():
    code = """#include <vector>
int main() {
    std::vector<int> v = {1,2,3};
    int s = 0;
    for (size_t i = 0; i <= v.size(); i++) { s += v[i]; }
    return s;
}"""
    result = detect_errors(code, "x.cpp")
    assert result["predicted_error"] != "UndeclaredIdentifier"
