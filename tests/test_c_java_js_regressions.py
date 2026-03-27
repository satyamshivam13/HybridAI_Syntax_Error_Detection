from src.error_engine import detect_errors
from src.multi_error_detector import detect_all_errors


def test_c_division_by_zero_reports_location():
    code = (
        "#include <stdio.h>\n"
        "int main() {\n"
        "    int x = 5 / 0;\n"
        "    return 0;\n"
        "}\n"
    )
    result = detect_errors(code, "main.c")
    assert result["predicted_error"] == "DivisionByZero"
    assert result["rule_based_issues"][0]["line"] == 3


def test_c_missing_include_detected_without_ml():
    code = (
        "int main() {\n"
        "    printf(\"hi\");\n"
        "    return 0;\n"
        "}\n"
    )
    result = detect_errors(code, "main.c")
    assert result["predicted_error"] == "MissingInclude"
    assert result["rule_based_issues"][0]["line"] == 2


def test_java_combo_keeps_primary_syntax_and_secondary_type_issue():
    code = (
        "public class Test {\n"
        "    public static void main(String[] args) {\n"
        "        int x = \"10\";\n"
        "        System.out.println(x)\n"
        "    }\n"
        "}\n"
    )
    result = detect_errors(code, "Test.java")
    assert result["predicted_error"] == "MissingDelimiter"
    issue_types = {issue["type"] for issue in result["rule_based_issues"]}
    assert "TypeMismatch" in issue_types
    assert "MissingDelimiter" in issue_types


def test_java_missing_import_detected_rule_based():
    code = (
        "public class Test {\n"
        "    public static void main(String[] args) {\n"
        "        ArrayList<Integer> x = new ArrayList<>();\n"
        "    }\n"
        "}\n"
    )
    result = detect_errors(code, "Test.java")
    assert result["predicted_error"] == "MissingImport"


def test_javascript_undeclared_identifier_detected():
    code = (
        "function test() {\n"
        "    console.log(y);\n"
        "}\n"
        "test();\n"
    )
    result = detect_errors(code, "test.js")
    assert result["predicted_error"] == "UndeclaredIdentifier"
    assert result["rule_based_issues"][0]["line"] == 2


def test_javascript_valid_without_semicolons_is_not_false_positive():
    code = (
        "function test() {\n"
        "    const x = 1\n"
        "    console.log(x)\n"
        "}\n"
        "test()\n"
    )
    result = detect_errors(code, "test.js")
    assert result["predicted_error"] == "NoError"


def test_javascript_duplicate_definition_detected():
    code = (
        "function test() {\n"
        "    let x = 1;\n"
        "    let x = 2;\n"
        "}\n"
        "test();\n"
    )
    result = detect_errors(code, "test.js")
    assert result["predicted_error"] == "DuplicateDefinition"


def test_multi_error_detector_reports_multiple_java_issues():
    code = (
        "public class Test {\n"
        "    public static void main(String[] args) {\n"
        "        int x = \"10\";\n"
        "        System.out.println(x)\n"
        "    }\n"
        "}\n"
    )
    result = detect_all_errors(code, "Test.java")
    error_types = {error["type"] for error in result["errors"]}
    assert "MissingDelimiter" in error_types
    assert "TypeMismatch" in error_types


def test_unclosed_string_suppresses_cascading_bracket_noise_in_detector():
    code = (
        "function test() {\n"
        "    console.log(\"Hello);\n"
        "}\n"
    )
    result = detect_errors(code, "test.js")
    assert result["predicted_error"] == "UnclosedString"
    issue_types = {issue["type"] for issue in result["rule_based_issues"]}
    assert issue_types == {"UnclosedString"}


def test_multi_error_detector_keeps_primary_unclosed_string_without_bracket_noise():
    code = (
        "public class Test {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"Hi);\n"
        "    }\n"
        "}\n"
    )
    result = detect_all_errors(code, "Test.java")
    error_types = {error["type"] for error in result["errors"]}
    assert "UnclosedString" in error_types
    assert "UnmatchedBracket" not in error_types


def test_cpp_pointer_declarations_are_not_undeclared_identifiers():
    code = (
        "#include <iostream>\n"
        "using namespace std;\n"
        "\n"
        "int* getValue() {\n"
        "    int x = 10;\n"
        "    return &x;\n"
        "}\n"
        "\n"
        "int main() {\n"
        "    int* ptr = getValue();\n"
        "    cout << *ptr << endl;\n"
        "}\n"
    )
    result = detect_errors(code, "main.cpp")
    issue_types = {issue["type"] for issue in result["rule_based_issues"]}
    assert "UndeclaredIdentifier" not in issue_types
