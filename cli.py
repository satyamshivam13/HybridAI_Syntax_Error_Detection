# ============================================================
# CLI Tool: Multi-Language Syntax Error Checker
# File: cli.py
# ============================================================

import sys
import io

# Fix Unicode encoding on Windows (emojis crash with cp1252)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.error_engine import detect_errors
from src.auto_fix import AutoFixer
from src.quality_analyzer import CodeQualityAnalyzer


def print_usage():
    print("Usage:")
    print("  python cli.py <path_to_code_file>")
    print("Example:")
    print("  python cli.py test.java")


def main():
    # --------------------------------------------------------
    # 1. Argument Check
    # --------------------------------------------------------
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    file_path = sys.argv[1]

    # --------------------------------------------------------
    # 2. Read Code File
    # --------------------------------------------------------
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    # --------------------------------------------------------
    # 3. Detect Errors (PASS FILENAME 🔥)
    # --------------------------------------------------------
    result = detect_errors(code, filename=file_path)

    # --------------------------------------------------------
    # 4. Print Results
    # --------------------------------------------------------
    print("=" * 60)
    print("🧠 Multi-Language Syntax Error Checker (CLI)")
    print("=" * 60)

    print(f"📂 File        : {file_path}")
    print(f"🗂 Language    : {result['language']}")
    print(f"🤖 Detected    : {result['predicted_error']}")
    print("-" * 60)

    # --------------------------------------------------------
    # 5. Rule-Based Issues
    # --------------------------------------------------------
    issues = result.get("rule_based_issues", [])

    if issues:
        print("⚠️ Rule-Based Issues:")
        for i, issue in enumerate(issues, start=1):
            print(f"\n{i}. {issue.get('type')}")
            if issue.get("line"):
                print(f"   Line      : {issue.get('line')}")
            if issue.get("col"):
                print(f"   Column    : {issue.get('col')}")
            print(f"   Message   : {issue.get('message')}")
            if issue.get("suggestion"):
                print(f"   Suggestion: {issue.get('suggestion')}")
    else:
        print("✅ No rule-based syntax issues detected.")
    
    # --------------------------------------------------------
    # 6. Auto-Fix Suggestion
    # --------------------------------------------------------
    if result['predicted_error'] != "NoError":
        print("\n" + "=" * 60)
        print("🔧 AUTO-FIX SUGGESTION")
        print("=" * 60)
        
        fixer = AutoFixer()
        line_num = 0
        
        # Get line number from issues
        if issues:
            for issue in issues:
                if issue.get('line'):
                    line_num = issue['line'] - 1
                    break
        
        fix_result = fixer.apply_fixes(code, result['predicted_error'], line_num, result['language'])
        
        if fix_result['success']:
            print("✅ Automatic fix available!\n")
            print("Fixed Code:")
            print("-" * 60)
            print(fix_result['fixed_code'])
            print("-" * 60)
            print("\nChanges Applied:")
            for change in fix_result['changes']:
                print(f"  • {change}")
        else:
            print("ℹ️ Manual correction recommended for this error type.")
    
    # --------------------------------------------------------
    # 7. Code Quality Analysis
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("📊 CODE QUALITY ANALYSIS")
    print("=" * 60)
    
    try:
        quality = CodeQualityAnalyzer(code, result['language'])
        quality_report = quality.analyze()
        
        print(f"Quality Score  : {quality_report['quality_score']}/100")
        print(f"Code Lines     : {quality_report['line_counts']['code']}")
        print(f"Comment Lines  : {quality_report['line_counts']['comments']}")
        print(f"Blank Lines    : {quality_report['line_counts']['blank']}")
        
        complexity = quality_report.get('complexity', 'N/A')
        print(f"Complexity     : {complexity}")
        print(f"Comment Ratio  : {quality_report['comment_ratio']}%")
        
        if quality_report['suggestions']:
            print("\n💡 Quality Suggestions:")
            for i, suggestion in enumerate(quality_report['suggestions'], start=1):
                print(f"  {i}. {suggestion}")
        else:
            print("\n✅ Code quality looks good!")
    
    except Exception as e:
        print("ℹ️ Quality analysis unavailable for this code snippet.")

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


# ------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------

if __name__ == "__main__":
    main()
