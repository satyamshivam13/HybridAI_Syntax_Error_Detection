"""
Code Quality Analyzer Module
Provides metrics and suggestions for code improvement beyond syntax errors
"""

import re
from typing import Dict, List


class CodeQualityAnalyzer:
    """
    Analyzes code quality metrics including:
    - Code complexity
    - Naming conventions
    - Code length
    - Comment density
    """

    def __init__(self, code: str, language: str):
        self.code = code
        self.language = language.lower()  # Normalize: "Python" → "python", "C++" → "c++"
        self.lines = code.split('\n')
        self.metrics = {}

    def count_lines(self) -> Dict[str, int]:
        """Count total, code, and comment lines"""
        total_lines = len(self.lines)
        code_lines = 0
        comment_lines = 0
        blank_lines = 0

        for line in self.lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif self._is_comment(stripped):
                comment_lines += 1
            else:
                code_lines += 1

        return {
            'total': total_lines,
            'code': code_lines,
            'comments': comment_lines,
            'blank': blank_lines
        }

    def _is_comment(self, line: str) -> bool:
        """Check if line is a comment"""
        if self.language == "python":
            return line.startswith('#')
        elif self.language in ["java", "c", "c++"]:
            return line.startswith('//') or line.startswith('/*') or line.startswith('*')
        return False

    def _strip_strings_and_comments(self, code: str) -> str:
        """
        Remove string literals and comments before counting keywords.
        This prevents words inside strings/comments from inflating complexity.
        """
        # Remove single-line strings (both quote types), non-greedy
        code = re.sub(r'"[^"\n]*"', '""', code)
        code = re.sub(r"'[^'\n]*'", "''", code)

        if self.language == "python":
            # Remove Python single-line comments
            code = re.sub(r'#[^\n]*', '', code)
        elif self.language in ["java", "c", "c++"]:
            # Remove C-style block comments
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            # Remove C-style single-line comments
            code = re.sub(r'//[^\n]*', '', code)

        return code

    def calculate_complexity(self) -> int:
        """
        Calculate cyclomatic complexity (simplified).
        Counts decision points: if, for, while, case, catch, etc.
        Strings and comments are stripped first to avoid false matches.
        """
        complexity = 1  # Base complexity

        # Strip strings and comments before scanning for keywords
        clean_code = self._strip_strings_and_comments(self.code)

        keyword_patterns = [
            r"\bif\b",
            r"\belif\b",
            r"\belse\b",
            r"\bfor\b",
            r"\bwhile\b",
            r"\bcase\b",
            r"\bcatch\b",
            r"\bexcept\b",
            r"&&",
            r"\|\|",
        ]

        for pattern in keyword_patterns:
            matches = re.findall(pattern, clean_code)
            complexity += len(matches)

        return complexity

    def check_naming_conventions(self) -> Dict[str, List[str]]:
        """
        Check if naming follows conventions
        """
        issues = {
            'snake_case_violations': [],
            'camel_case_violations': [],
            'constant_violations': []
        }

        if self.language == "python":
            # Find function/variable names
            func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            functions = re.findall(func_pattern, self.code)
            for func in functions:
                if not func.islower() and '_' not in func:
                    issues['snake_case_violations'].append(func)

        elif self.language == "java":
            # Check camelCase for methods
            method_pattern = r'(public|private|protected)?\s+\w+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            methods = re.findall(method_pattern, self.code)
            for _, method in methods:
                if method[0].isupper():
                    issues['camel_case_violations'].append(method)

        return issues

    def calculate_avg_line_length(self) -> float:
        """Calculate average line length"""
        non_blank = [line for line in self.lines if line.strip()]
        if not non_blank:
            return 0
        return sum(len(line) for line in non_blank) / len(non_blank)

    def check_long_functions(self, max_lines: int = 50) -> List[str]:
        """Identify functions longer than max_lines"""
        long_functions = []

        if self.language == "python":
            pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        elif self.language == "java":
            pattern = r'(public|private|protected)?\s+\w+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        else:
            return long_functions

        # Simple heuristic: count lines between function definitions
        func_matches = list(re.finditer(pattern, self.code))

        for i, match in enumerate(func_matches):
            func_name = match.group(1) if self.language == "python" else match.group(2)
            start_line = self.code[:match.start()].count('\n')

            if i + 1 < len(func_matches):
                end_line = self.code[:func_matches[i + 1].start()].count('\n')
            else:
                end_line = len(self.lines)

            func_length = end_line - start_line

            if func_length > max_lines:
                long_functions.append(f"{func_name} ({func_length} lines)")

        return long_functions

    def analyze(self) -> Dict:
        """
        Run complete quality analysis

        Returns:
            Dict containing all metrics and suggestions
        """
        line_counts = self.count_lines()
        complexity = self.calculate_complexity()
        naming_issues = self.check_naming_conventions()
        avg_line_length = self.calculate_avg_line_length()
        long_functions = self.check_long_functions()

        # Calculate comment ratio
        comment_ratio = (line_counts['comments'] / line_counts['total'] * 100) if line_counts['total'] > 0 else 0

        # Generate suggestions
        suggestions = []

        if complexity > 10:
            suggestions.append(f"⚠️ High complexity ({complexity}). Consider refactoring.")

        if comment_ratio < 10:
            suggestions.append(f"📝 Low comment ratio ({comment_ratio:.1f}%). Add more documentation.")

        if avg_line_length > 100:
            suggestions.append(f"📏 Long lines (avg {avg_line_length:.0f} chars). Keep under 80-100 chars.")

        if long_functions:
            suggestions.append(f"🔨 Long functions detected: {', '.join(long_functions)}")

        if any(naming_issues.values()):
            suggestions.append("🏷️ Naming convention violations detected.")

        return {
            'line_counts': line_counts,
            'complexity': complexity,
            'comment_ratio': round(comment_ratio, 2),
            'avg_line_length': round(avg_line_length, 2),
            'naming_issues': naming_issues,
            'long_functions': long_functions,
            'suggestions': suggestions,
            'quality_score': self._calculate_quality_score(
                complexity, comment_ratio, avg_line_length, len(long_functions)
            )
        }

    def _calculate_quality_score(self, complexity: int, comment_ratio: float,
                                  avg_line_length: float, long_func_count: int) -> float:
        """
        Calculate overall quality score (0-100)
        """
        score = 100

        # Deduct for high complexity
        if complexity > 10:
            score -= min((complexity - 10) * 2, 30)

        # Deduct for low comments
        if comment_ratio < 10:
            score -= (10 - comment_ratio)

        # Deduct for long lines
        if avg_line_length > 100:
            score -= min((avg_line_length - 100) / 5, 20)

        # Deduct for long functions
        score -= long_func_count * 5

        return max(score, 0)


def analyze_code_quality(code: str, language: str) -> Dict:
    """
    Convenience function for quality analysis

    Args:
        code: Source code to analyze
        language: Programming language (python, java, c, cpp)

    Returns:
        Dict with quality metrics and suggestions
    """
    analyzer = CodeQualityAnalyzer(code, language)
    return analyzer.analyze()


if __name__ == "__main__":
    # Test case
    test_code = """
def calculateSum(numbers):
    total = 0
    for num in numbers:
        if num > 0:
            total += num
    return total

def process():
    data = [1, 2, 3, 4, 5]
    result = calculateSum(data)
    print(result)
"""

    result = analyze_code_quality(test_code, "python")
    print("Quality Analysis:")
    print(f"Complexity: {result['complexity']}")
    print(f"Comment Ratio: {result['comment_ratio']}%")
    print(f"Quality Score: {result['quality_score']}/100")
    print(f"\nSuggestions:")
    for suggestion in result['suggestions']:
        print(f"  {suggestion}")
