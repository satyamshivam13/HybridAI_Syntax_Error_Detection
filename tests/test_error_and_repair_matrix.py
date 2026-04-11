from __future__ import annotations

import pytest

from src.auto_fix import AutoFixer
from src.error_engine import detect_errors


# Each case validates both:
# 1) the faulty snippet triggers the expected error type
# 2) the repaired snippet is classified as NoError
CASES = [
    # Python
    {
        "id": "py-missing-delimiter",
        "filename": "x.py",
        "bad": "def test()\n    pass\n",
        "expected_error": "MissingDelimiter",
        "repaired": "def test():\n    pass\n",
    },
    {
        "id": "py-indentation-error",
        "filename": "x.py",
        "bad": "def test():\nprint('x')\n",
        "expected_error": "IndentationError",
        "repaired": "def test():\n    print('x')\n",
    },
    {
        "id": "py-unclosed-string",
        "filename": "x.py",
        "bad": "name = \"Asha\nprint(name)\n",
        "expected_error": "UnclosedString",
        "repaired": "name = \"Asha\"\nprint(name)\n",
    },
    {
        "id": "py-wildcard-import",
        "filename": "x.py",
        "bad": "from math import *\nprint(sqrt(4))\n",
        "expected_error": "WildcardImport",
        "repaired": "from math import sqrt\nprint(sqrt(4))\n",
    },
    {
        "id": "py-mutable-default",
        "filename": "x.py",
        "bad": "def add_item(item, bag=[]):\n    bag.append(item)\n    return bag\n",
        "expected_error": "MutableDefault",
        "repaired": "def add_item(item, bag=None):\n    if bag is None:\n        bag = []\n    bag.append(item)\n    return bag\n",
    },

    # C
    {
        "id": "c-missing-delimiter",
        "filename": "x.c",
        "bad": "int main() {\n    int a = 5\n    return a;\n}\n",
        "expected_error": "MissingDelimiter",
        "repaired": "int main() {\n    int a = 5;\n    return a;\n}\n",
    },
    {
        "id": "c-missing-include",
        "filename": "x.c",
        "bad": "int main() {\n    printf(\"hi\");\n    return 0;\n}\n",
        "expected_error": "MissingInclude",
        "repaired": "#include <stdio.h>\nint main() {\n    printf(\"hi\");\n    return 0;\n}\n",
    },
    {
        "id": "c-division-by-zero",
        "filename": "x.c",
        "bad": "int main() {\n    int x = 5 / 0;\n    return x;\n}\n",
        "expected_error": "DivisionByZero",
        "repaired": "int main() {\n    int x = 5 / 1;\n    return x;\n}\n",
    },
    {
        "id": "c-unmatched-bracket",
        "filename": "x.c",
        "bad": "int main() {\n    return 0;\n",
        "expected_error": "UnmatchedBracket",
        "repaired": "int main() {\n    return 0;\n}\n",
    },

    # C++
    {
        "id": "cpp-undeclared-identifier",
        "filename": "x.cpp",
        "bad": "#include <iostream>\nusing namespace std;\nint main() {\n    cout << y;\n}\n",
        "expected_error": "UndeclaredIdentifier",
        "repaired": "#include <iostream>\nusing namespace std;\nint main() {\n    int y = 0;\n    cout << y;\n}\n",
    },
    {
        "id": "cpp-infinite-loop",
        "filename": "x.cpp",
        "bad": "int main() {\n    for(;;) {\n    }\n}\n",
        "expected_error": "InfiniteLoop",
        "repaired": "int main() {\n    for (int i = 0; i < 3; i++) {\n    }\n}\n",
    },
    {
        "id": "cpp-dangling-pointer",
        "filename": "x.cpp",
        "bad": "#include <iostream>\nusing namespace std;\n\nint* getValue() {\n    int x = 10;\n    return &x;\n}\n\nint main() {\n    int* ptr = getValue();\n    cout << *ptr << endl;\n}\n",
        "expected_error": "DanglingPointer",
        "repaired": "#include <iostream>\nusing namespace std;\n\nint getValue() {\n    int x = 10;\n    return x;\n}\n\nint main() {\n    int value = getValue();\n    cout << value << endl;\n}\n",
    },

    # Java
    {
        "id": "java-missing-delimiter",
        "filename": "Main.java",
        "bad": "public class Main {\n    public static void main(String[] args) {\n        int x = 1\n    }\n}\n",
        "expected_error": "MissingDelimiter",
        "repaired": "public class Main {\n    public static void main(String[] args) {\n        int x = 1;\n    }\n}\n",
    },
    {
        "id": "java-missing-import",
        "filename": "Main.java",
        "bad": "public class Main {\n    public static void main(String[] args) {\n        ArrayList<Integer> x = new ArrayList<>();\n    }\n}\n",
        "expected_error": "MissingImport",
        "repaired": "public class Main {\n    public static void main(String[] args) {\n        java.util.ArrayList<Integer> x = new java.util.ArrayList<>();\n    }\n}\n",
    },
    {
        "id": "java-type-mismatch",
        "filename": "Main.java",
        "bad": "public class Main {\n    public static void main(String[] args) {\n        int x = 1.5;\n    }\n}\n",
        "expected_error": "TypeMismatch",
        "repaired": "public class Main {\n    public static void main(String[] args) {\n        double x = 1.5;\n    }\n}\n",
    },

    # JavaScript
    {
        "id": "js-undeclared-identifier",
        "filename": "x.js",
        "bad": "function demo() {\n    let a = 10;\n    console.log(b);\n}\n",
        "expected_error": "UndeclaredIdentifier",
        "repaired": "function demo() {\n    let a = 10;\n    console.log(a);\n}\n",
    },
    {
        "id": "js-duplicate-definition",
        "filename": "x.js",
        "bad": "function test() {\n    let x = 1;\n    let x = 2;\n}\n",
        "expected_error": "DuplicateDefinition",
        "repaired": "function test() {\n    let x = 1;\n    x = 2;\n}\n",
    },
    {
        "id": "js-invalid-member-access",
        "filename": "x.js",
        "bad": "function f() {\n    const a = {x: 1};\n    console..log(a.x);\n}\n",
        "expected_error": "MissingDelimiter",
        "repaired": "function f() {\n    const a = {x: 1};\n    console.log(a.x);\n}\n",
    },
    {
        "id": "js-unclosed-string",
        "filename": "x.js",
        "bad": "function f() {\n    let s = \"hello;\n}\n",
        "expected_error": "UnclosedString",
        "repaired": "function f() {\n    let s = \"hello\";\n}\n",
    },
]


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_error_and_repair_matrix(case: dict[str, str]):
    bad_result = detect_errors(case["bad"], case["filename"])
    assert bad_result["predicted_error"] == case["expected_error"], (
        f"{case['id']} bad-code mismatch: expected {case['expected_error']}, "
        f"got {bad_result['predicted_error']}"
    )

    repaired_result = detect_errors(case["repaired"], case["filename"])
    assert repaired_result["predicted_error"] == "NoError", (
        f"{case['id']} repaired-code mismatch: expected NoError, "
        f"got {repaired_result['predicted_error']}"
    )



def test_suggestion_only_autofix_preserves_indentation_error_snippet():
    fixer = AutoFixer()
    code = "def test():\nprint('x')\n"
    result = fixer.apply_fixes(code, "IndentationError", 1, "Python")
    assert result["success"] is True
    assert result["fixed_code"] == code
    assert any("Suggestion-only" in change for change in result["changes"])


def test_suggestion_only_autofix_preserves_unclosed_string_snippet():
    fixer = AutoFixer()
    code = "name = \"Asha\nprint(name)\n"
    result = fixer.apply_fixes(code, "UnclosedString", 0, "Python")
    assert result["success"] is True
    assert result["fixed_code"] == code
    assert any("Suggestion-only" in change for change in result["changes"])
