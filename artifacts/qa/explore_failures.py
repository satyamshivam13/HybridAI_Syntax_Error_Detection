import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.error_engine import detect_errors

CASES = [
    ("C", "C-F1", "int main(){\n int x = 1.5;\n return 0;\n}\n"),
    ("C", "C-F2", "#include <stdio.h>\nint main(){\n int x;\n printf(\"%d\", y);\n}\n"),
    ("C", "C-F3", "#include <stdio.h>\nint main(){\n int a = 0;\n if (a = 5) { printf(\"x\"); }\n return 0;\n}\n"),
    ("Java", "J-F1", "public class T{\n public static void main(String[] args){\n int x = 1.5;\n }\n}\n"),
    ("Java", "J-F2", "public class T{\n public static void main(String[] args){\n String s = true;\n }\n}\n"),
    ("Java", "J-F3", "public class T{\n public static void main(String[] args){\n int[] a = new int[2]\n a[2]=3;\n }\n}\n"),
    ("Java", "J-F4", "public class T{\n public static void main(String[] args){\n System.out.println(\"x\")\n int y = 2;\n }\n}\n"),
    ("JavaScript", "JS-F1", "function x(){\n  const a = ;\n}\n"),
    ("JavaScript", "JS-F2", "function x(){\n  let a = 1\n  [1,2].forEach(n => console.log(n));\n}\n"),
    ("JavaScript", "JS-F3", "function x(){\n  if (true)\n    console.log('ok')\n  elsee\n    console.log('bad')\n}\n"),
    ("JavaScript", "JS-F4", "const obj = {a:1};\nconsole.log(obj..a);\n"),
    ("JavaScript", "JS-F5", "function x(){\n  return\n  5 + undeclared;\n}\n"),
]

for lang, cid, code in CASES:
    r = detect_errors(code, filename=f"{cid}.txt", language_override=lang)
    print("="*70)
    print(cid, lang)
    print("predicted:", r.get("predicted_error"), "degraded:", r.get("degraded_mode"))
    print("issues:", [i.get("type") for i in r.get("rule_based_issues", [])])
    if r.get("rule_based_issues"):
        i = r["rule_based_issues"][0]
        print("first issue:", i.get("line"), i.get("message"))
