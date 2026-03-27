import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.error_engine import detect_errors


TEST_CASES = [
    # C (provided + 5 additional)
    {
        "id": "C-01",
        "language": "C",
        "category": "Syntax",
        "title": "Missing semicolon after declaration (provided)",
        "expected_type": "MissingDelimiter",
        "code": "#include <stdio.h>\nint main() {\n    int a = 10\n    printf(\"%d\", a);\n    return 0;\n}\n",
        "fixed_code": "#include <stdio.h>\nint main() {\n    int a = 10;\n    printf(\"%d\", a);\n    return 0;\n}\n",
    },
    {
        "id": "C-02",
        "language": "C",
        "category": "Syntax",
        "title": "Missing closing brace",
        "expected_type": "UnmatchedBracket",
        "code": "#include <stdio.h>\nint main() {\n    printf(\"Hello\");\n",
        "fixed_code": "#include <stdio.h>\nint main() {\n    printf(\"Hello\");\n}\n",
    },
    {
        "id": "C-03",
        "language": "C",
        "category": "Runtime",
        "title": "Division by zero",
        "expected_type": "DivisionByZero",
        "code": "#include <stdio.h>\nint main() {\n    int x = 10 / 0;\n    printf(\"%d\", x);\n    return 0;\n}\n",
        "fixed_code": "#include <stdio.h>\nint main() {\n    int d = 2;\n    int x = 10 / d;\n    printf(\"%d\", x);\n    return 0;\n}\n",
    },
    {
        "id": "C-04",
        "language": "C",
        "category": "Semantic",
        "title": "Use stdio symbol without include",
        "expected_type": "MissingInclude",
        "code": "int main() {\n    printf(\"Hi\");\n    return 0;\n}\n",
        "fixed_code": "#include <stdio.h>\nint main() {\n    printf(\"Hi\");\n    return 0;\n}\n",
    },
    {
        "id": "C-05",
        "language": "C",
        "category": "Edge",
        "title": "Undeclared identifier",
        "expected_type": "UndeclaredIdentifier",
        "code": "#include <stdio.h>\nint main() {\n    result = 42;\n    return 0;\n}\n",
        "fixed_code": "#include <stdio.h>\nint main() {\n    int result = 42;\n    return 0;\n}\n",
    },
    {
        "id": "C-06",
        "language": "C",
        "category": "Semantic",
        "title": "Type mismatch int assigned string",
        "expected_type": "TypeMismatch",
        "code": "#include <stdio.h>\nint main() {\n    int n = \"42\";\n    return 0;\n}\n",
        "fixed_code": "#include <stdio.h>\nint main() {\n    int n = 42;\n    return 0;\n}\n",
    },

    # Java (provided + 5 additional)
    {
        "id": "J-01",
        "language": "Java",
        "category": "Syntax+Semantic",
        "title": "Type mismatch and missing semicolon (provided)",
        "expected_type": "TypeMismatch",
        "code": "public class Test {\n    public static void main(String[] args) {\n        int x = \"10\";\n        System.out.println(x)\n    }\n}\n",
        "fixed_code": "public class Test {\n    public static void main(String[] args) {\n        int x = 10;\n        System.out.println(x);\n    }\n}\n",
    },
    {
        "id": "J-02",
        "language": "Java",
        "category": "Syntax",
        "title": "Missing closing brace",
        "expected_type": "UnmatchedBracket",
        "code": "public class T {\n    public static void main(String[] args) {\n        System.out.println(1);\n}\n",
        "fixed_code": "public class T {\n    public static void main(String[] args) {\n        System.out.println(1);\n    }\n}\n",
    },
    {
        "id": "J-03",
        "language": "Java",
        "category": "Semantic",
        "title": "Missing import for ArrayList",
        "expected_type": "MissingImport",
        "code": "public class T {\n    public static void main(String[] args) {\n        ArrayList<Integer> nums = new ArrayList<>();\n        System.out.println(nums.size());\n    }\n}\n",
        "fixed_code": "import java.util.ArrayList;\npublic class T {\n    public static void main(String[] args) {\n        ArrayList<Integer> nums = new ArrayList<>();\n        System.out.println(nums.size());\n    }\n}\n",
    },
    {
        "id": "J-04",
        "language": "Java",
        "category": "Edge",
        "title": "Undeclared variable use",
        "expected_type": "UndeclaredIdentifier",
        "code": "public class T {\n    public static void main(String[] args) {\n        int x = y + 1;\n        System.out.println(x);\n    }\n}\n",
        "fixed_code": "public class T {\n    public static void main(String[] args) {\n        int y = 2;\n        int x = y + 1;\n        System.out.println(x);\n    }\n}\n",
    },
    {
        "id": "J-05",
        "language": "Java",
        "category": "Runtime",
        "title": "Division by zero",
        "expected_type": "DivisionByZero",
        "code": "public class T {\n    public static void main(String[] args) {\n        int z = 5 / 0;\n        System.out.println(z);\n    }\n}\n",
        "fixed_code": "public class T {\n    public static void main(String[] args) {\n        int d = 1;\n        int z = 5 / d;\n        System.out.println(z);\n    }\n}\n",
    },
    {
        "id": "J-06",
        "language": "Java",
        "category": "Logical",
        "title": "Potentially unreachable statement after return",
        "expected_type": "UnreachableCode",
        "code": "public class T {\n    static int f() {\n        return 1;\n        int x = 2;\n    }\n}\n",
        "fixed_code": "public class T {\n    static int f() {\n        int x = 2;\n        return x;\n    }\n}\n",
    },

    # JavaScript (provided + edge + 5 additional)
    {
        "id": "JS-01",
        "language": "JavaScript",
        "category": "Syntax+Runtime",
        "title": "Undefined variable and broken function call (provided)",
        "expected_type": "UndeclaredIdentifier",
        "code": "function test() {\n    let x = 10;\n    console.log(y);\n}\ntest(\n",
        "fixed_code": "function test() {\n    let x = 10;\n    console.log(x);\n}\ntest();\n",
    },
    {
        "id": "JS-02",
        "language": "JavaScript",
        "category": "Syntax",
        "title": "Missing parenthesis in if condition (provided edge)",
        "expected_type": "UnmatchedBracket",
        "code": "if (true {\n    console.log(\"Hello\");\n}\n",
        "fixed_code": "if (true) {\n    console.log(\"Hello\");\n}\n",
    },
    {
        "id": "JS-03",
        "language": "JavaScript",
        "category": "Edge",
        "title": "Duplicate let declaration",
        "expected_type": "DuplicateDefinition",
        "code": "let a = 1;\nlet a = 2;\nconsole.log(a);\n",
        "fixed_code": "let a = 1;\na = 2;\nconsole.log(a);\n",
    },
    {
        "id": "JS-04",
        "language": "JavaScript",
        "category": "Runtime",
        "title": "Division by zero",
        "expected_type": "DivisionByZero",
        "code": "function f() {\n    const z = 10 / 0;\n    return z;\n}\n",
        "fixed_code": "function f() {\n    const d = 2;\n    const z = 10 / d;\n    return z;\n}\n",
    },
    {
        "id": "JS-05",
        "language": "JavaScript",
        "category": "Syntax",
        "title": "Unclosed string literal",
        "expected_type": "UnclosedString",
        "code": "function greet() {\n    const s = \"hello;\n    return s;\n}\n",
        "fixed_code": "function greet() {\n    const s = \"hello\";\n    return s;\n}\n",
    },
    {
        "id": "JS-06",
        "language": "JavaScript",
        "category": "Logical",
        "title": "Unreachable code after return",
        "expected_type": "UnreachableCode",
        "code": "function f() {\n    return 1;\n    console.log(\"never\");\n}\n",
        "fixed_code": "function f() {\n    console.log(\"runs\");\n    return 1;\n}\n",
    },
    {
        "id": "JS-07",
        "language": "JavaScript",
        "category": "Edge",
        "title": "Undeclared identifier usage",
        "expected_type": "UndeclaredIdentifier",
        "code": "function add() {\n    return total + 1;\n}\n",
        "fixed_code": "function add() {\n    const total = 0;\n    return total + 1;\n}\n",
    },
]


def evaluate_case(case):
    result = detect_errors(case["code"], filename=f"{case['id']}.txt", language_override=case["language"])
    predicted = result.get("predicted_error", "NoError")
    issue_types = [it.get("type") for it in result.get("rule_based_issues", [])]
    detected = predicted == case["expected_type"] or case["expected_type"] in issue_types
    first_issue = result.get("rule_based_issues", [{}])[0] if result.get("rule_based_issues") else {}
    return {
        "id": case["id"],
        "language": case["language"],
        "category": case["category"],
        "title": case["title"],
        "expected_type": case["expected_type"],
        "predicted_error": predicted,
        "rule_issue_types": issue_types,
        "detected": detected,
        "degraded_mode": bool(result.get("degraded_mode", False)),
        "warnings": result.get("warnings", []),
        "first_issue_line": first_issue.get("line"),
        "first_issue_message": first_issue.get("message"),
        "input_code": case["code"],
        "fixed_code": case["fixed_code"],
    }


def main():
    rows = [evaluate_case(case) for case in TEST_CASES]

    out_dir = Path("artifacts/qa")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "multilang_qa_matrix_results.json"
    out_file.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    summary = {}
    for row in rows:
        lang = row["language"]
        summary.setdefault(lang, {"total": 0, "pass": 0, "fail": 0})
        summary[lang]["total"] += 1
        if row["detected"]:
            summary[lang]["pass"] += 1
        else:
            summary[lang]["fail"] += 1

    print("QA matrix complete")
    print(json.dumps(summary, indent=2))
    print(f"Results written to: {out_file}")


if __name__ == "__main__":
    main()
