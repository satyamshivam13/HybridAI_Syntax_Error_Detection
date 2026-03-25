import sys
import os
import io

# Fix Unicode on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath('.'))
from src.error_engine import detect_errors
from src.auto_fix import AutoFixer

TEST_CASES = [
    {
        "name": "JavaScript Infinite Loop (authoritative)",
        "code": "function run() {\n  while(true) {\n    console.log('spinning');\n  }\n}",
        "lang": "JavaScript",
        "expected": "InfiniteLoop"
    },
    {
        "name": "Java Infinite Loop (authoritative)",
        "code": "public class Test {\n  public static void main(String[] args) {\n    while(1) { System.out.println(\"loop\"); }\n  }\n}",
        "lang": "Java",
        "expected": "InfiniteLoop"
    },
    {
        "name": "C++ Infinite Loop (authoritative)",
        "code": "int main() {\n  for(;;) { /* loop */ }\n  return 0;\n}",
        "lang": "C++",
        "expected": "InfiniteLoop"
    },
    {
        "name": "Python Mutable Default (Semantic)",
        "code": "def process(items=[]):\n    items.append(1)\n    return items",
        "lang": "Python",
        "expected": "MutableDefault"
    },
    {
        "name": "Python Division By Zero (Heuristic)",
        "code": "x = 10 / 0",
        "lang": "Python",
        "expected": "DivisionByZero"
    },
    {
        "name": "C++ Missing Semicolon (ML + AutoFix)",
        "code": "#include <iostream>\nint main() {\n    std::cout << \"Hello\" << std::endl\n    return 0;\n}",
        "lang": "C++",
        "expected": "MissingDelimiter"
    }
]

def run_demo():
    print("=" * 60)
    print("🧪 OmniSyntax Optimization Verification — Live Demo")
    print("=" * 60)
    
    passed = 0
    fixer = AutoFixer()

    for test in TEST_CASES:
        print(f"\n▶ Test: {test['name']} ({test['lang']})")
        res = detect_errors(test['code'], filename=f"test.{test['lang'].lower()}")
        
        predicted = res['predicted_error']
        conf = res['confidence']
        
        print(f"  Prediction : {predicted} (Confidence: {conf:.2f})")
        
        if predicted == test['expected'] or (test['expected'] == "MissingDelimiter" and predicted == "MissingSemicolon"):
            print("  ✅ Match!")
            passed += 1
        else:
            print(f"  ❌ Mismatch! Expected: {test['expected']}")

        # Test AutoFix
        if predicted != "NoError":
            fix = fixer.apply_fixes(test['code'], predicted, 0, test['lang'])
            if fix['success']:
                print(f"  🔧 Auto-Fix: Available ({len(fix['changes'])} changes)")
            else:
                print("  ℹ️  Auto-Fix: Not available for this specific snippet")

    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{len(TEST_CASES)} passed")
    print("=" * 60)

if __name__ == "__main__":
    run_demo()
