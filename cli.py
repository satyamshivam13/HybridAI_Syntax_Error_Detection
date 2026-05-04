# ============================================================
# CLI Tool: Multi-Language Syntax Error Checker
# File: cli.py
# ============================================================

import sys
import io

# Fix Unicode encoding on Windows (emojis crash with cp1252)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src import static_pipeline
from src.auto_fix import AutoFixer
from src.quality_analyzer import CodeQualityAnalyzer


def print_usage():
    print("Usage:")
    print("  python cli.py <path_to_code_file> [OPTIONS]")
    print("\nOptions:")
    print("  --all-errors     Show all detected errors (default: first error only)")
    print("\nExample:")
    print("  python cli.py test.java")
    print("  python cli.py test.py --all-errors")


def main():
    # --------------------------------------------------------
    # 1. Argument Check
    # --------------------------------------------------------
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    file_path = sys.argv[1]
    show_all_errors = "--all-errors" in sys.argv
    
    # --------------------------------------------------------
    # 2. Read Code File
    # --------------------------------------------------------
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"âŒ File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"âŒ Error reading file: {e}")
        sys.exit(1)

    # --------------------------------------------------------
    # 3. Detect Errors (PASS FILENAME ðŸ”¥)
    # --------------------------------------------------------
    if show_all_errors:
        result = static_pipeline.analyze_source(code, file_path).to_grouped_result()
    else:
        result = static_pipeline.analyze_source(code, file_path).to_single_result()

    # --------------------------------------------------------
    # 4. Print Results
    # --------------------------------------------------------
    print("=" * 60)
    print("ðŸ§  Multi-Language Syntax Error Checker (CLI)")
    print("=" * 60)

    print(f"ðŸ“‚ File        : {file_path}")
    print(f"ðŸ—‚ Language    : {result['language']}")
    
    warnings = result.get("warnings", [])
    if warnings:
        print("Runtime Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
        print("-" * 60)
    
    # Handle both single-error and all-errors output
    if show_all_errors:
        # Multi-error output
        print(f"ðŸ¤– Total Errors : {result.get('total_errors', 0)}")
        print("-" * 60)
        
        if result.get('total_errors', 0) == 0:
            print("âœ… No syntax errors detected.")
        else:
            errors_by_type = result.get('errors_by_type', {})
            for error_type, errors in errors_by_type.items():
                print(f"\nâš ï¸ {error_type} ({len(errors)} found)")
                for i, error in enumerate(errors, start=1):
                    print(f"  {i}. Line {error.get('line')}: {error.get('message')}")
                    if error.get("suggestion"):
                        print(f"     Suggestion: {error.get('suggestion')}")
    else:
        # Single error output  
        print(f"ðŸ¤– Detected    : {result['predicted_error']}")
        print("-" * 60)

    # --------------------------------------------------------
    # 5. Rule-Based Issues
    # --------------------------------------------------------
    issues = result.get("rule_based_issues", [])

    if issues:
        print("âš ï¸ Rule-Based Issues:")
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
        print("âœ… No rule-based syntax issues detected.")
    
    # --------------------------------------------------------
    # 6. Auto-Fix Suggestion
    # --------------------------------------------------------
    if show_all_errors:
        primary_error = next(iter(result.get("errors_by_type", {})), "NoError")
    else:
        primary_error = result.get("predicted_error", "NoError")

    if primary_error != "NoError":
        print("\n" + "=" * 60)
        print("ðŸ”§ AUTO-FIX SUGGESTION")
        print("=" * 60)
        
        fixer = AutoFixer()
        patch_preview = AutoFixer.patch_preview(code, issues, result['language'])
        if patch_preview:
            print("Auto-Fix Patch:")
            for line in AutoFixer.format_patch_preview(patch_preview):
                print(f"  {line}")
            print()

        line_num = AutoFixer.line_for_error(issues, primary_error)
        
        fix_result = fixer.apply_fixes(code, primary_error, line_num, result['language'])
        
        if fix_result['success']:
            print("âœ… Automatic fix available!\n")
            print("Fixed Code:")
            print("-" * 60)
            print(fix_result['fixed_code'])
            print("-" * 60)
            print("\nChanges Applied:")
            for change in fix_result['changes']:
                print(f"  â€¢ {change}")
        elif patch_preview:
            print("â„¹ï¸ Review and apply the patch lines above; automatic rewriting remains conservative for this error type.")
        elif fix_result.get('changes'):
            print("â„¹ï¸ Manual correction recommended. Suggested next steps:")
            for change in fix_result['changes']:
                print(f"  â€¢ {change}")
        else:
            print("â„¹ï¸ Manual correction recommended for this error type.")
    
    # --------------------------------------------------------
    # 7. Code Quality Analysis
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("ðŸ“Š CODE QUALITY ANALYSIS")
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
            print("\nðŸ’¡ Quality Suggestions:")
            for i, suggestion in enumerate(quality_report['suggestions'], start=1):
                print(f"  {i}. {suggestion}")
        else:
            print("\nâœ… Code quality looks good!")
    
    except Exception as e:
        print("â„¹ï¸ Quality analysis unavailable for this code snippet.")

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


# ------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------

if __name__ == "__main__":
    main()


