"""Edge-case stress tests for the static pipeline — validates hardening fixes."""
import sys, io, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.static_pipeline import detect_errors_static, detect_all_errors_static

passed = 0
failed = 0

def run(label, code, expect_error=None, expect_no_crash=True, **kwargs):
    global passed, failed
    try:
        r = detect_errors_static(code, **kwargs)
        error = r['predicted_error']
        if expect_error is not None and error != expect_error:
            print(f"  FAIL  {label}: expected={expect_error}, got={error}")
            failed += 1
        else:
            print(f"  PASS  {label}: error={error}, conf={r['confidence']}")
            passed += 1
    except Exception as e:
        if expect_no_crash:
            print(f"  FAIL  {label}: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
        else:
            print(f"  PASS  {label}: Expected crash caught: {type(e).__name__}")
            passed += 1

print("=" * 60)
print("EDGE CASE & REGRESSION TESTS")
print("=" * 60)

# ==================== C1 REGRESSION: Null bytes ====================
print("\n--- C1: Null byte handling ---")
run("Null bytes (was crash)", "\x00\x00\x00", expect_error="NoError")
run("Null in valid code", "x = 1\x00 + 2", expect_error="NoError")
run("Null in Python def", "def foo():\x00\n    pass")

# ==================== H1 REGRESSION: Comment false positives ====================
print("\n--- H1: Comment-only Python ---")
run("Python comments only", "# just a comment\n# another comment", expect_error="NoError")
run("Python comment + code", "# setup\nx = 42")
run("C include not stripped", '#include <stdio.h>\nint main() { printf("hi"); return 0; }')

# ==================== General edge cases ====================
print("\n--- General edge cases ---")
run("Empty string", "", expect_error="NoError")
run("Whitespace only", "   \n\n\t\t  ", expect_error="NoError")
run("Very long single line", "x = 1 + " * 5000 + "1")
run("Deep brackets", "(" * 200 + ")" * 200)
run("Unicode RTL", 'x = "' + '\u202e' * 50 + '"')
run("Mixed indent", "def foo():\n\t    print('hi')\n    print('bye')")
run("Long var name", "a" * 10000 + " = 42")
run("Mixed line endings", "def foo():\r\n    pass\n    return 1\r\n")
run("Only comments", "# just a comment\n# another comment", expect_error="NoError")
run("Single char", "x")
run("Just number", "42", expect_error="NoError")
run("JS template literal", "const x = `hello ${name}`;\nconsole.log(x);")
run("C preprocessor", '#include <stdio.h>\n#define MAX 100\nint main() { printf("%d", MAX); return 0; }')
run("Java generics", 'import java.util.ArrayList;\npublic class Test {\n  public static void main(String[] args) {\n    ArrayList<String> list = new ArrayList<>();\n  }\n}')
run("Code injection attempt", 'x = "__import__(\'os\').system(\'rm -rf /\')"', expect_error="NoError")
run("Division by zero", "result = 10 / 0")

# ==================== Multi-error path ====================
print("\n--- Multi-error detection ---")
try:
    r = detect_all_errors_static("")
    print(f"  PASS  Empty multi-error: errors={r.get('total_errors', 'N/A')}")
    passed += 1
except Exception as e:
    print(f"  FAIL  Empty multi-error: {type(e).__name__}: {e}")
    failed += 1

try:
    r = detect_all_errors_static("def foo(\n    pass")
    print(f"  PASS  Broken Python multi: errors={r.get('total_errors', 'N/A')}")
    passed += 1
except Exception as e:
    print(f"  FAIL  Broken Python multi: {type(e).__name__}: {e}")
    failed += 1

try:
    r = detect_all_errors_static("\x00\x00\x00")
    print(f"  PASS  Null bytes multi: errors={r.get('total_errors', 'N/A')}")
    passed += 1
except Exception as e:
    print(f"  FAIL  Null bytes multi: {type(e).__name__}: {e}")
    failed += 1

print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 60)

if failed > 0:
    sys.exit(1)
