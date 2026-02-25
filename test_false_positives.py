"""
test_false_positives.py
=======================
Tests valid (correct) code across Python, Java, C, C++ to find cases
where the system wrongly reports an error on perfectly good code.

Usage:
    python test_false_positives.py
    python test_false_positives.py --verbose    # show all results, not just failures
    python test_false_positives.py --lang Python
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath('.'))

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def green(s):  return f"{GREEN}{s}{RESET}"
def red(s):    return f"{RED}{s}{RESET}"
def yellow(s): return f"{YELLOW}{s}{RESET}"
def bold(s):   return f"{BOLD}{s}{RESET}"


# ─── Valid Python test cases ───────────────────────────────────────────────────
VALID_PYTHON = [
    # Basic statements
    ("single print",            "print('HELLO')",                                         ".py"),
    ("print double quotes",     'print("HELLO")',                                          ".py"),
    ("variable assignment",     "x = 10",                                                  ".py"),
    ("arithmetic",              "x = 1 + 2 * 3",                                           ".py"),
    ("string variable",         "name = 'Alice'",                                          ".py"),
    ("multi-assign",            "x, y = 1, 2",                                             ".py"),
    ("augmented assign",        "x = 0\nx += 1",                                           ".py"),

    # Functions
    ("simple function",         "def hello():\n    print('hi')",                           ".py"),
    ("function with args",      "def add(a, b):\n    return a + b",                        ".py"),
    ("function with default",   "def greet(name='World'):\n    print(f'Hello {name}')",   ".py"),
    ("lambda",                  "f = lambda x: x * 2",                                    ".py"),
    ("nested function",         "def outer():\n    def inner():\n        pass\n    inner()", ".py"),
    ("function call",           "def foo():\n    pass\nfoo()",                             ".py"),
    ("return value",            "def square(n):\n    return n * n",                        ".py"),

    # Classes
    ("simple class",            "class Dog:\n    pass",                                    ".py"),
    ("class with init",         "class Dog:\n    def __init__(self, name):\n        self.name = name", ".py"),
    ("class with method",       "class Dog:\n    def bark(self):\n        print('Woof')", ".py"),
    ("class inheritance",       "class Animal:\n    pass\nclass Dog(Animal):\n    pass",  ".py"),

    # Control flow
    ("if statement",            "x = 5\nif x > 0:\n    print('positive')",                ".py"),
    ("if-else",                 "x = 5\nif x > 0:\n    print('pos')\nelse:\n    print('neg')", ".py"),
    ("if-elif-else",            "x = 5\nif x > 0:\n    pass\nelif x == 0:\n    pass\nelse:\n    pass", ".py"),
    ("for loop",                "for i in range(10):\n    print(i)",                       ".py"),
    ("for with list",           "for x in [1, 2, 3]:\n    print(x)",                      ".py"),
    ("while loop",              "x = 0\nwhile x < 5:\n    x += 1",                        ".py"),
    ("break continue",          "for i in range(10):\n    if i == 5:\n        break",      ".py"),

    # Data structures
    ("list",                    "nums = [1, 2, 3, 4, 5]",                                  ".py"),
    ("dict",                    "d = {'a': 1, 'b': 2}",                                    ".py"),
    ("set",                     "s = {1, 2, 3}",                                           ".py"),
    ("tuple",                   "t = (1, 2, 3)",                                           ".py"),
    ("list comprehension",      "squares = [x**2 for x in range(10)]",                    ".py"),
    ("dict comprehension",      "d = {k: v for k, v in zip('abc', [1,2,3])}",             ".py"),
    ("nested list",             "matrix = [[1, 2], [3, 4], [5, 6]]",                       ".py"),

    # Imports
    ("import os",               "import os",                                               ".py"),
    ("import math",             "import math\nprint(math.pi)",                             ".py"),
    ("from import",             "from os import path",                                     ".py"),

    # Exception handling
    ("try-except",              "try:\n    x = 1/1\nexcept ZeroDivisionError:\n    pass",  ".py"),
    ("try-except-finally",      "try:\n    pass\nexcept Exception:\n    pass\nfinally:\n    pass", ".py"),
    ("raise",                   "def check(x):\n    if x < 0:\n        raise ValueError('negative')", ".py"),

    # String operations
    ("f-string",                "name = 'Alice'\nprint(f'Hello {name}')",                  ".py"),
    ("multiline string",        "s = '''\nhello\nworld\n'''",                              ".py"),
    ("string methods",          "s = 'hello'\nprint(s.upper())",                           ".py"),
    ("string concat",           "a = 'hello' + ' ' + 'world'",                            ".py"),

    # File operations pattern
    ("with statement",          "with open('test.txt', 'w') as f:\n    f.write('hi')",    ".py"),

    # Decorators
    ("decorator",               "def my_dec(f):\n    return f\n\n@my_dec\ndef foo():\n    pass", ".py"),

    # Type hints
    ("type hint",               "def add(a: int, b: int) -> int:\n    return a + b",       ".py"),

    # Walrus operator
    ("walrus operator",         "data = [1, 2, 3]\nif n := len(data):\n    print(n)",      ".py"),

    # Division (should NOT flag DivisionByZero — that's a runtime issue)
    ("safe division",           "x = 10\ny = 2\nresult = x / y\nprint(result)",           ".py"),
    ("division by var",         "def divide(a, b):\n    return a / b",                    ".py"),

    # Multiline valid code
    ("full script",             "import os\n\ndef main():\n    name = 'World'\n    print(f'Hello {name}')\n\nif __name__ == '__main__':\n    main()", ".py"),
]


# ─── Valid Java test cases ─────────────────────────────────────────────────────
VALID_JAVA = [
    ("hello world",
     'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello");\n    }\n}',
     ".java"),

    ("variable declaration",
     'public class Main {\n    public static void main(String[] args) {\n        int x = 10;\n        int y = 20;\n        System.out.println(x + y);\n    }\n}',
     ".java"),

    ("if statement",
     'public class Main {\n    public static void main(String[] args) {\n        int x = 5;\n        if (x > 0) {\n            System.out.println("positive");\n        }\n    }\n}',
     ".java"),

    ("for loop",
     'public class Main {\n    public static void main(String[] args) {\n        for (int i = 0; i < 10; i++) {\n            System.out.println(i);\n        }\n    }\n}',
     ".java"),

    ("method definition",
     'public class Main {\n    public static int add(int a, int b) {\n        return a + b;\n    }\n    public static void main(String[] args) {\n        System.out.println(add(2, 3));\n    }\n}',
     ".java"),

    ("string operations",
     'public class Main {\n    public static void main(String[] args) {\n        String name = "Alice";\n        System.out.println("Hello " + name);\n    }\n}',
     ".java"),
]


# ─── Valid C test cases ────────────────────────────────────────────────────────
VALID_C = [
    ("hello world",
     '#include <stdio.h>\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}',
     ".c"),

    ("variables",
     '#include <stdio.h>\nint main() {\n    int x = 10;\n    int y = 20;\n    printf("%d\\n", x + y);\n    return 0;\n}',
     ".c"),

    ("for loop",
     '#include <stdio.h>\nint main() {\n    for (int i = 0; i < 10; i++) {\n        printf("%d\\n", i);\n    }\n    return 0;\n}',
     ".c"),

    ("function",
     '#include <stdio.h>\nint add(int a, int b) {\n    return a + b;\n}\nint main() {\n    printf("%d\\n", add(2, 3));\n    return 0;\n}',
     ".c"),

    ("if-else",
     '#include <stdio.h>\nint main() {\n    int x = 5;\n    if (x > 0) {\n        printf("positive\\n");\n    } else {\n        printf("non-positive\\n");\n    }\n    return 0;\n}',
     ".c"),
]


# ─── Valid C++ test cases ──────────────────────────────────────────────────────
VALID_CPP = [
    ("hello world",
     '#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}',
     ".cpp"),

    ("variables",
     '#include <iostream>\nusing namespace std;\nint main() {\n    int x = 10;\n    int y = 20;\n    cout << x + y << endl;\n    return 0;\n}',
     ".cpp"),

    ("for loop",
     '#include <iostream>\nusing namespace std;\nint main() {\n    for (int i = 0; i < 10; i++) {\n        cout << i << endl;\n    }\n    return 0;\n}',
     ".cpp"),

    ("class",
     '#include <iostream>\nusing namespace std;\nclass Dog {\npublic:\n    void bark() {\n        cout << "Woof!" << endl;\n    }\n};\nint main() {\n    Dog d;\n    d.bark();\n    return 0;\n}',
     ".cpp"),

    ("vector",
     '#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    vector<int> v = {1, 2, 3};\n    for (int x : v) cout << x << endl;\n    return 0;\n}',
     ".cpp"),
]


# ─── Runner ───────────────────────────────────────────────────────────────────
def run_tests(cases, detect_errors, lang_filter=None, verbose=False):
    failures = []
    passes = 0

    for name, code, ext in cases:
        lang = ext.lstrip('.')
        if lang_filter and lang.lower() != lang_filter.lower() and ext.lstrip('.') != lang_filter.lower():
            continue

        try:
            result = detect_errors(code, f"test{ext}")
            predicted = result['predicted_error']
        except Exception as e:
            predicted = f"EXCEPTION: {e}"

        is_pass = predicted == "NoError"

        if is_pass:
            passes += 1
            if verbose:
                print(f"  {green('✅')} [{lang.upper():4}] {name}")
        else:
            failures.append((lang, name, predicted, code))
            print(f"  {red('❌')} [{lang.upper():4}] {name}")
            print(f"         → Wrongly reported: {red(predicted)}")
            if verbose:
                print(f"         Code: {code[:80].replace(chr(10), ' | ')!r}")

    return passes, failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--lang', type=str, default=None,
                        help='Filter: Python, Java, C, cpp')
    args = parser.parse_args()

    from src.error_engine import detect_errors

    all_cases = VALID_PYTHON + VALID_JAVA + VALID_C + VALID_CPP

    print(bold(f"\n{'='*60}"))
    print(bold("  False Positive Test — Valid Code Should Return NoError"))
    print(bold(f"{'='*60}\n"))

    # Group by language
    groups = [
        ("Python", VALID_PYTHON),
        ("Java",   VALID_JAVA),
        ("C",      VALID_C),
        ("C++",    VALID_CPP),
    ]

    total_pass = 0
    total_fail = 0
    all_failures = []

    for lang, cases in groups:
        if args.lang and args.lang.lower() not in lang.lower():
            continue

        print(bold(f"  ── {lang} ({len(cases)} cases) " + "─"*30))
        p, failures = run_tests(cases, detect_errors, verbose=args.verbose)
        total_pass += p
        total_fail += len(failures)
        all_failures.extend(failures)
        if not failures:
            print(f"  {green('✅ All passed!')}")
        print()

    # Summary
    total = total_pass + total_fail
    print(bold(f"{'='*60}"))
    print(bold(f"  SUMMARY"))
    print(bold(f"{'='*60}"))
    print(f"\n  Total cases : {total}")
    print(f"  Passed      : {green(str(total_pass))}")
    print(f"  Failed      : {red(str(total_fail)) if total_fail else green('0')}")
    pct = total_pass / total * 100 if total else 0
    bar_filled = int(30 * pct / 100)
    bar = "█" * bar_filled + "░" * (30 - bar_filled)
    colour = GREEN if pct == 100 else YELLOW if pct >= 90 else RED
    print(f"  Accuracy    : {colour}[{bar}]{RESET} {pct:.1f}%")

    if all_failures:
        print(f"\n  {bold('False Positives to Fix:')}")
        for lang, name, predicted, code in all_failures:
            print(f"\n  [{lang.upper()}] {bold(name)}")
            print(f"    Wrongly flagged as: {red(predicted)}")
            print(f"    Code snippet: {code[:100].replace(chr(10), ' | ')!r}")
    else:
        print(f"\n  {green('🎉 Zero false positives! All valid code correctly returns NoError.')}")
    print()


if __name__ == '__main__':
    main()