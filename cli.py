# cli.py - simple command line tester
from syntax_checker import detect_all
import sys, json

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <file.py>")
        return
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    issues = detect_all(code)
    if not issues:
        print("No issues found.")
    else:
        for i, iss in enumerate(issues, start=1):
            print(f"{i}. {iss['type']} - line {iss.get('line')}")
            print("   Message:", iss['message'])
            if iss.get('suggestion'):
                print("   Suggestion:", iss['suggestion'])
            print()
if __name__ == "__main__":
    main()