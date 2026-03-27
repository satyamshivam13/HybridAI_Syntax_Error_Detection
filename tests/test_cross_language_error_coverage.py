from __future__ import annotations

import pytest

from src.error_engine import detect_errors


@pytest.mark.parametrize(
    "case_id,filename,code,expected",
    [
        # Python coverage
        (
            "py-missing-delimiter",
            "x.py",
            "def test()\n    pass\n",
            "MissingDelimiter",
        ),
        (
            "py-indentation",
            "x.py",
            "def test():\nprint('x')\n",
            "IndentationError",
        ),
        (
            "py-unclosed-string",
            "x.py",
            "name = \"Asha\nprint(name)\n",
            "UnclosedString",
        ),
        (
            "py-correct",
            "x.py",
            "def add(a, b):\n    return a + b\n",
            "NoError",
        ),

        # C coverage
        (
            "c-missing-delimiter",
            "x.c",
            "int main() {\n    int a = 5\n    return a;\n}\n",
            "MissingDelimiter",
        ),
        (
            "c-missing-include",
            "x.c",
            "int main() {\n    printf(\"hi\");\n    return 0;\n}\n",
            "MissingInclude",
        ),
        (
            "c-division-by-zero",
            "x.c",
            "int main() {\n    int x = 5 / 0;\n    return x;\n}\n",
            "DivisionByZero",
        ),
        (
            "c-correct",
            "x.c",
            "#include <stdio.h>\nint main() {\n    printf(\"hi\");\n    return 0;\n}\n",
            "NoError",
        ),

        # C++ coverage
        (
            "cpp-undeclared-identifier",
            "x.cpp",
            "#include <iostream>\nusing namespace std;\nint main() {\n    cout << y;\n}\n",
            "UndeclaredIdentifier",
        ),
        (
            "cpp-infinite-loop",
            "x.cpp",
            "int main() {\n    for(;;) {\n    }\n}\n",
            "InfiniteLoop",
        ),
        (
            "cpp-dangling-pointer",
            "x.cpp",
            "#include <iostream>\nusing namespace std;\n\nint* getValue() {\n    int x = 10;\n    return &x;\n}\n\nint main() {\n    int* ptr = getValue();\n    cout << *ptr << endl;\n}\n",
            "DanglingPointer",
        ),
        (
            "cpp-correct",
            "x.cpp",
            "#include <iostream>\nint main() {\n    int x = 10;\n    std::cout << x << std::endl;\n    return 0;\n}\n",
            "NoError",
        ),

        # Java coverage
        (
            "java-missing-delimiter",
            "Main.java",
            "public class Main {\n    public static void main(String[] args) {\n        int x = 1\n    }\n}\n",
            "MissingDelimiter",
        ),
        (
            "java-missing-import",
            "Main.java",
            "public class Main {\n    public static void main(String[] args) {\n        ArrayList<Integer> x = new ArrayList<>();\n    }\n}\n",
            "MissingImport",
        ),
        (
            "java-type-mismatch",
            "Main.java",
            "public class Main {\n    public static void main(String[] args) {\n        int x = 1.5;\n    }\n}\n",
            "TypeMismatch",
        ),
        (
            "java-correct",
            "Main.java",
            "public class Main {\n    public static void main(String[] args) {\n        int a = 2;\n        int b = 3;\n        System.out.println(a + b);\n    }\n}\n",
            "NoError",
        ),

        # JavaScript coverage
        (
            "js-undeclared-identifier",
            "x.js",
            "function demo() {\n    let a = 10;\n    console.log(b);\n}\n",
            "UndeclaredIdentifier",
        ),
        (
            "js-duplicate-definition",
            "x.js",
            "function test() {\n    let x = 1;\n    let x = 2;\n}\n",
            "DuplicateDefinition",
        ),
        (
            "js-invalid-member-access",
            "x.js",
            "function f() {\n    const a = {x: 1};\n    console..log(a.x);\n}\n",
            "MissingDelimiter",
        ),
        (
            "js-unclosed-string",
            "x.js",
            "function f() {\n    let s = \"hello;\n}\n",
            "UnclosedString",
        ),
        (
            "js-correct",
            "x.js",
            "let x = 10;\nconsole.log(x);\n",
            "NoError",
        ),
    ],
)
def test_cross_language_error_coverage_matrix(case_id: str, filename: str, code: str, expected: str):
    result = detect_errors(code, filename)
    assert result["predicted_error"] == expected, f"{case_id}: expected {expected}, got {result['predicted_error']}"


def test_cpp_dangling_pointer_reports_origin_and_use_sites():
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
    result = detect_errors(code, "x.cpp")
    lines = {
        issue["line"]
        for issue in result.get("rule_based_issues", [])
        if issue.get("type") == "DanglingPointer"
    }
    assert lines == {6, 11}
