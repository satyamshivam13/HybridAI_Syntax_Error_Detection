import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.error_engine import detect_errors


SAMPLES = {
    "C_missing_delimiter": {
        "filename": "test.c",
        "expected": "MissingDelimiter",
        "code": """#include <stdio.h>\nint main() {\n    int a = 5\n    return a;\n}\n""",
    },
    "CPP_dangling_pointer": {
        "filename": "test.cpp",
        "expected": "DanglingPointer",
        "code": """int* get_value() {\n    int x = 10;\n    return &x;\n}\n""",
    },
    "Java_missing_import": {
        "filename": "Test.java",
        "expected": "MissingImport",
        "code": """public class Test {\n    public static void main(String[] args) {\n        ArrayList<Integer> xs = new ArrayList<>();\n    }\n}\n""",
    },
    "Python_mutable_default": {
        "filename": "test.py",
        "expected": "MutableDefault",
        "code": """def add_item(x, acc=[]):\n    acc.append(x)\n    return acc\nprint(add_item(1)); print(add_item(2))\n""",
    },
    "JavaScript_undeclared_identifier": {
        "filename": "test.js",
        "expected": "UndeclaredIdentifier",
        "code": """function run() {\n  console.log(x);\n}\nrun();\n""",
    },
}


def main() -> int:
    failures = 0

    print("OmniSyntax smoke test: reliable cross-language samples")
    print("-" * 65)

    for name, sample in SAMPLES.items():
        result = detect_errors(sample["code"], sample["filename"])
        predicted = result.get("predicted_error")
        language = result.get("language")
        confidence = result.get("confidence")
        expected = sample["expected"]

        ok = predicted == expected
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1

        print(
            f"{status:4} | {name:34} | expected={expected:20} | predicted={predicted:20} "
            f"| lang={language:10} | conf={confidence}"
        )

    print("-" * 65)
    if failures == 0:
        print("All smoke samples matched expected errors.")
        return 0

    print(f"{failures} sample(s) did not match expected errors.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
