"""
Auto-Fix Module for Common Syntax Errors
Provides safe, conservative auto-correction suggestions
"""

import re

from src.config import get_supported_fix_error_types


def _normalized_error_type(error_type: str | None) -> str:
    aliases = {
        "MissingColon": "MissingDelimiter",
        "MissingSemicolon": "MissingDelimiter",
        "UnclosedQuotes": "UnclosedString",
    }
    return aliases.get(error_type or "", error_type or "")


def _split_inline_comment(line: str, language: str | None) -> tuple[str, str]:
    markers = ["//"] if language in {"C", "C++", "Java", "JavaScript"} else ["#"]
    for marker in markers:
        idx = line.find(marker)
        if idx >= 0:
            return line[:idx].rstrip(), line[idx:]
    return line.rstrip(), ""


def _join_code_comment(code_part: str, comment: str) -> str:
    return f"{code_part}  {comment}" if comment else code_part


def _add_before_comment(line: str, token: str, language: str | None) -> str:
    code_part, comment = _split_inline_comment(line, language)
    return _join_code_comment(f"{code_part.rstrip()}{token}", comment)


class AutoFixer:
    """
    Attempts to automatically fix common syntax errors
    with minimal code modification
    """
    
    def __init__(self):
        self.fixes_applied = []

    @staticmethod
    def supported_error_types() -> list[str]:
        return get_supported_fix_error_types()

    @staticmethod
    def line_for_error(issues: list[dict], error_type: str) -> int | None:
        """Return the 0-indexed line for the matching issue type, if known."""
        target = _normalized_error_type(error_type)
        for issue in issues:
            if _normalized_error_type(issue.get("type")) == target and issue.get("line"):
                return issue["line"] - 1
        for issue in issues:
            if issue.get("line"):
                return issue["line"] - 1
        return None

    @staticmethod
    def patch_preview(code: str, issues: list[dict], language: str | None = None) -> list[dict]:
        """Build localized line-replacement previews for conservative tutor display."""
        lines = code.splitlines()
        replacements: dict[int, str] = {}
        insertions: list[dict] = []

        for issue in issues:
            if _normalized_error_type(issue.get("type")) == "MissingImport":
                imported = AutoFixer._preview_import_line(issue)
                if imported:
                    insertions.append({"line": 1, "replacement": imported, "kind": "insert"})
                continue

            line_no = issue.get("line")
            if not line_no or line_no < 1 or line_no > len(lines):
                continue

            current = replacements.get(line_no, lines[line_no - 1])
            if _normalized_error_type(issue.get("type")) == "IndentationError":
                replacement = AutoFixer._preview_indentation(lines, line_no)
            else:
                replacement = AutoFixer._preview_line_fix(current, issue, language)
            if replacement and replacement != current:
                replacements[line_no] = replacement

        preview: list[dict] = []
        for item in insertions:
            preview.append(item)
        for line_no in sorted(replacements):
            preview.append({
                "line": line_no,
                "original": lines[line_no - 1],
                "replacement": replacements[line_no],
                "kind": "replace",
            })
        return preview

    @staticmethod
    def format_patch_preview(preview: list[dict]) -> list[str]:
        formatted = []
        for item in preview:
            prefix = f"Line {item['line']}"
            if item.get("kind") == "insert":
                formatted.append(f"{prefix} + {item['replacement']}")
            else:
                formatted.append(f"{prefix} -> {item['replacement']}")
        return formatted

    @staticmethod
    def _preview_line_fix(line: str, issue: dict, language: str | None) -> str | None:
        issue_type = _normalized_error_type(issue.get("type"))
        message = (issue.get("message") or "").lower()
        suggestion = (issue.get("suggestion") or "").lower()

        if issue_type == "MissingDelimiter":
            if "comma" in message or "comma" in suggestion or "adjacent" in message:
                return AutoFixer._preview_missing_comma(line, language)
            if language == "Python" or re.search(r"\bcolon\b|':'", f"{message} {suggestion}"):
                return AutoFixer._preview_missing_colon(line, language)
            return AutoFixer._preview_missing_semicolon(line, language)

        if issue_type == "UnclosedString":
            return AutoFixer._preview_unclosed_string(line, language)

        if issue_type == "UnmatchedBracket":
            return AutoFixer._preview_unmatched_bracket(line)

        if issue_type == "IndentationError":
            return None

        if issue_type == "MissingImport":
            return None

        return None

    @staticmethod
    def _preview_missing_comma(line: str, language: str | None) -> str | None:
        code_part, comment = _split_inline_comment(line, language)
        fixed = re.sub(
            r"(?<![\w.])(\d+(?:\.\d*)?|\.\d+)\s+(\d+(?:\.\d*)?|\.\d+)(?![\w.])",
            r"\1, \2",
            code_part,
            count=1,
        )
        return _join_code_comment(fixed, comment) if fixed != code_part else None

    @staticmethod
    def _preview_missing_colon(line: str, language: str | None) -> str | None:
        code_part, comment = _split_inline_comment(line, language)
        if code_part.rstrip().endswith(":"):
            return None
        return _join_code_comment(code_part.rstrip() + ":", comment)

    @staticmethod
    def _preview_missing_semicolon(line: str, language: str | None) -> str | None:
        code_part, comment = _split_inline_comment(line, language)
        stripped = code_part.rstrip()
        if not stripped or stripped.endswith((";", "{", "}")):
            return None
        return _join_code_comment(stripped + ";", comment)

    @staticmethod
    def _preview_unclosed_string(line: str, language: str | None) -> str | None:
        code_part, comment = _split_inline_comment(line, language)
        stripped = code_part.rstrip()
        quote = AutoFixer._unmatched_quote(stripped)
        if not quote:
            return None
        insertion_at = len(stripped)
        if stripped.endswith(")"):
            insertion_at = stripped.rfind(")")
        elif stripped.endswith(";"):
            insertion_at = stripped.rfind(";")
        fixed = stripped[:insertion_at] + quote + stripped[insertion_at:]
        if language in {"C", "C++", "Java", "JavaScript"} and fixed.rstrip().endswith(")"):
            fixed = fixed.rstrip() + ";"
        return _join_code_comment(fixed, comment)

    @staticmethod
    def _unmatched_quote(text: str) -> str | None:
        active = None
        escaped = False
        for char in text:
            if escaped:
                escaped = False
                continue
            if char == "\\" and active:
                escaped = True
                continue
            if char in {"'", '"'}:
                if active == char:
                    active = None
                elif not active:
                    active = char
        return active

    @staticmethod
    def _preview_indentation(lines: list[str], line_no: int) -> str | None:
        index = line_no - 1
        if index < 1 or index >= len(lines):
            return None
        current = lines[index]
        for prev_index in range(index - 1, -1, -1):
            prev = lines[prev_index]
            if not prev.strip():
                continue
            if prev.split("#", 1)[0].rstrip().endswith(":"):
                parent_indent = len(prev) - len(prev.lstrip(" \t"))
                return " " * (parent_indent + 4) + current.lstrip()
            break
        return "    " + current.lstrip()

    @staticmethod
    def _preview_unmatched_bracket(line: str) -> str | None:
        if "{" in line and line.count("(") > line.count(")"):
            idx = line.find("{")
            return line[:idx].rstrip() + ") " + line[idx:].lstrip()
        if ":" in line and line.count("(") > line.count(")"):
            idx = line.find(":")
            return line[:idx].rstrip() + ")" + line[idx:]
        return None

    @staticmethod
    def _preview_import_line(issue: dict) -> str | None:
        suggestion = issue.get("suggestion") or ""
        match = re.search(r"(?:Add\s+import|Import)\s+'?([A-Za-z_][\w.]*)'?", suggestion)
        if match:
            return f"import {match.group(1).rstrip('.;')}"
        return None
    
    def fix_missing_colon(self, code: str, line_num: int) -> str:
        """
        Add missing colon to control structures
        """
        lines = code.split('\n')
        if 0 <= line_num < len(lines):
            line = lines[line_num]
            code_part = line.split('#', 1)[0].rstrip()
            keyword_pattern = r"^\s*(if|elif|else|for|while|def|class|try|except|finally|with)\b"
            if re.match(keyword_pattern, code_part) and not code_part.endswith(':'):
                lines[line_num] = line.rstrip() + ':'
                self.fixes_applied.append(f"Added colon at line {line_num + 1}")
        return '\n'.join(lines)
    
    def fix_missing_semicolon(self, code: str, line_num: int | None = None) -> str:
        """
        Add missing semicolon (for C/C++/Java/JavaScript)
        """
        lines = code.split('\n')
        
        # If line_num not provided, scan all lines
        if line_num is None:
            for i, line in enumerate(lines):
                line_stripped = line.rstrip()
                # Skip control structures, braces, and comments
                if not any(x in line for x in ['{', '}', '//', '/*', '*/', 'if ', 'for ', 'while ', 'else', 'class ', 'public ', 'private']):
                    if line_stripped and not line_stripped.endswith(';') and not line_stripped.endswith(':'):
                        # Check if it looks like a statement
                        if any(keyword in line for keyword in ['int ', 'float ', 'double ', 'String ', 'char ', 'boolean ', '=']):
                            lines[i] = line_stripped + ';'
                            self.fixes_applied.append(f"Added semicolon at line {i + 1}")
        else:
            # Fix specific line
            if 0 <= line_num < len(lines):
                line = lines[line_num].rstrip()
                # Don't add to control structures or comments
                if not any(x in line for x in ['{', '}', '//', '/*', '*/','if ', 'for ', 'while ']):
                    if not line.endswith(';') and line:
                        lines[line_num] = line + ';'
                        self.fixes_applied.append(f"Added semicolon at line {line_num + 1}")
        
        return '\n'.join(lines)
    
    def fix_indentation(self, code: str) -> str:
        """
        Standardize indentation (Python)
        """
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Convert tabs to 4 spaces
            fixed_line = line.replace('\t', '    ')
            fixed_lines.append(fixed_line)
        
        self.fixes_applied.append("Standardized indentation to 4 spaces")
        return '\n'.join(fixed_lines)
    
    def suggest_indentation_fix(self, line_num: int | None = None) -> None:
        """
        Keep indentation fixes suggestion-only to avoid accidental block rewrites.
        """
        location = f"line {line_num + 1}" if line_num is not None and line_num >= 0 else "the reported line"
        self.fixes_applied.append(
            f"Suggestion-only: check indentation at {location}; align with the parent block using 4 spaces (no tabs)."
        )

    def suggest_unclosed_string_fix(self, line_num: int | None = None) -> None:
        """
        Keep unclosed-string fixes suggestion-only to avoid inserting the wrong quote.
        """
        location = f"line {line_num + 1}" if line_num is not None and line_num >= 0 else "the reported line"
        self.fixes_applied.append(
            f"Suggestion-only: close the string literal at {location} by adding the matching quote before end-of-line."
        )

    def fix_unmatched_brackets(self, code: str) -> str:
        """
        Balance brackets/parentheses/braces
        """
        stack = []
        brackets = {'(': ')', '[': ']', '{': '}'}
        
        for char in code:
            if char in brackets.keys():
                stack.append(char)
            elif char in brackets.values():
                if stack and brackets[stack[-1]] == char:
                    stack.pop()
        
        # Add missing closing brackets
        while stack:
            opening = stack.pop()
            code += brackets[opening]
            self.fixes_applied.append(f"Added missing closing bracket: {brackets[opening]}")
        
        return code
    
    def fix_unclosed_quotes(self, code: str) -> str:
        """
        Close unclosed string quotes
        """
        single_quotes = code.count("'")
        double_quotes = code.count('"')
        
        # If odd number of quotes, add closing quote at end
        if single_quotes % 2 != 0:
            code += "'"
            self.fixes_applied.append("Closed unclosed single quote")
        
        if double_quotes % 2 != 0:
            code += '"'
            self.fixes_applied.append("Closed unclosed double quote")
        
        return code
    
    def fix_missing_import(self, code: str, language: str | None = None) -> str:
        """
        Suggest common missing imports based on code content
        """
        suggestions = []
        
        if language == "Python":
            # Check for common modules
            if 'np.' in code or 'numpy' in code.lower():
                suggestions.append("import numpy as np")
            if 'pd.' in code or 'pandas' in code.lower():
                suggestions.append("import pandas as pd")
            if 'plt.' in code or 'pyplot' in code.lower():
                suggestions.append("import matplotlib.pyplot as plt")
            if 'math.' in code:
                suggestions.append("import math")
            if 'os.' in code:
                suggestions.append("import os")
            if 'sys.' in code:
                suggestions.append("import sys")
                
        elif language == "Java":
            if 'Scanner' in code:
                suggestions.append("import java.util.Scanner;")
            if 'ArrayList' in code or 'List' in code:
                suggestions.append("import java.util.ArrayList;")
            if 'HashMap' in code or 'Map' in code:
                suggestions.append("import java.util.HashMap;")
        
        if suggestions:
            imports = '\n'.join(suggestions)
            code = imports + '\n\n' + code
            self.fixes_applied.append(f"Added suggested imports: {', '.join(suggestions)}")
        
        return code
    
    def fix_missing_include(self, code: str, language: str | None = None) -> str:
        """
        Suggest common missing includes for C/C++
        """
        suggestions = []
        
        if language in ["C", "C++"]:
            if 'printf' in code or 'scanf' in code:
                suggestions.append("#include <stdio.h>")
            if 'malloc' in code or 'free' in code:
                suggestions.append("#include <stdlib.h>")
            if 'strlen' in code or 'strcpy' in code:
                suggestions.append("#include <string.h>")
            if 'cout' in code or 'cin' in code:
                suggestions.append("#include <iostream>")
            if 'vector' in code:
                suggestions.append("#include <vector>")
            if 'string' in code and language == "C++":
                suggestions.append("#include <string>")
        
        if suggestions:
            includes = '\n'.join(suggestions)
            code = includes + '\n\n' + code
            self.fixes_applied.append(f"Added suggested includes: {', '.join(suggestions)}")
        
        return code
    
    def fix_unused_variable(self, code: str) -> str:
        """
        Add comment suggesting variable removal (conservative approach)
        """
        self.fixes_applied.append("Suggestion: Remove unused variables to clean up code")
        return code  # Don't auto-remove, just suggest
    
    def fix_unreachable_code(self, code: str) -> str:
        """
        Add comment about unreachable code (conservative approach)
        """
        self.fixes_applied.append("Suggestion: Remove unreachable code after return/break statements")
        return code  # Don't auto-remove, just suggest
    
    def fix_wildcard_import(self, code: str) -> str:
        """
        Suggest replacing wildcard imports
        """
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'from' in line and 'import *' in line:
                # Extract module name
                parts = line.split()
                if len(parts) >= 4 and parts[0] == 'from' and parts[2] == 'import':
                    module = parts[1]
                    lines[i] = f"# TODO: Replace with specific imports from {module}"
                    self.fixes_applied.append(f"Marked wildcard import for replacement: {module}")
        
        return '\n'.join(lines)
    
    def fix_duplicate_definition(self, code: str) -> str:
        """
        Detect and comment duplicate definitions
        """
        self.fixes_applied.append("Suggestion: Rename or remove duplicate definitions")
        return code  # Detection only, manual fix required
    
    def fix_invalid_assignment(self, code: str) -> str:
        """
        Suggest fixing invalid assignments
        """
        self.fixes_applied.append("Suggestion: Ensure you're assigning to valid variables, not literals or constants")
        return code  # Manual fix required
        
    def fix_infinite_loop(self, code: str) -> str:
        """ Suggest an exit condition for infinite loops """
        self.fixes_applied.append("Suggestion: Add a break condition or modify the loop expression to prevent an infinite loop")
        return code
        
    def fix_type_mismatch(self, code: str) -> str:
        """ Suggest fixing type mismatches """
        self.fixes_applied.append("Suggestion: Ensure assigned values match their declared variable types or cast appropriately")
        return code
        
    def fix_name_error(self, code: str) -> str:
        """ Suggest fixing undeclared variables """
        self.fixes_applied.append("Suggestion: Declare the variable before using it, or check for typos in the variable name")
        return code
        
    def fix_division_by_zero(self, code: str) -> str:
        """ Suggest fixing division by zero """
        self.fixes_applied.append("Suggestion: Avoid dividing by zero or wrap the division in a condition checking if denominator != 0")
        return code
        
    def fix_mutable_default(self, code: str) -> str:
        """ Suggest fixing mutable default arguments (Python) """
        self.fixes_applied.append("Suggestion: Use None as default value and initialize the mutable object (e.g. lists/dicts) inside the function")
        return code
        
    def fix_line_too_long(self, code: str) -> str:
        """ Suggest formatting for long lines """
        self.fixes_applied.append("Suggestion: Break long lines into multiple lines for better readability and PEP8 compliance")
        return code
    
    def apply_fixes(self, code: str, error_type: str, line_num: int | None = None, language: str | None = None) -> dict:
        """
        Apply appropriate fix based on error type and language
        
        Args:
            code: Source code with error
            error_type: Type of error detected
            line_num: Line number (0-indexed)
            language: Programming language (Python, Java, C, C++)
        
        Returns:
            dict: {
                'fixed_code': str,
                'changes': list,
                'success': bool
            }
        """
        self.fixes_applied = []
        fixed_code = code

        if error_type not in self.supported_error_types():
            return {
                'fixed_code': code,
                'changes': [],
                'success': False,
                'error': f"Unsupported error_type: {error_type}"
            }
        
        try:
            # MissingDelimiter - language-specific
            if error_type == "MissingDelimiter":
                if language == "Python" and line_num is not None:
                    fixed_code = self.fix_missing_colon(code, line_num)
                elif language in ["Java", "C", "C++", "JavaScript"]:
                    fixed_code = self.fix_missing_semicolon(code, line_num)
            
            # Specific error types
            elif error_type == "MissingColon" and line_num is not None:
                fixed_code = self.fix_missing_colon(code, line_num)
            
            elif error_type == "MissingSemicolon":
                fixed_code = self.fix_missing_semicolon(code, line_num)
            
            elif error_type == "IndentationError":
                self.suggest_indentation_fix(line_num)
            
            elif error_type == "UnmatchedBracket":
                fixed_code = self.fix_unmatched_brackets(code)
            
            elif error_type in ["UnclosedQuotes", "UnclosedString"]:
                self.suggest_unclosed_string_fix(line_num)
            
            # New auto-fix support
            elif error_type == "MissingImport":
                fixed_code = self.fix_missing_import(code, language)
            
            elif error_type == "MissingInclude":
                fixed_code = self.fix_missing_include(code, language)
            
            elif error_type == "UnusedVariable":
                fixed_code = self.fix_unused_variable(code)
            
            elif error_type == "UnreachableCode":
                fixed_code = self.fix_unreachable_code(code)
            
            elif error_type == "WildcardImport":
                fixed_code = self.fix_wildcard_import(code)
            
            elif error_type == "DuplicateDefinition":
                fixed_code = self.fix_duplicate_definition(code)
            
            elif error_type == "InvalidAssignment":
                fixed_code = self.fix_invalid_assignment(code)
                
            elif error_type == "InfiniteLoop":
                fixed_code = self.fix_infinite_loop(code)
                
            elif error_type == "TypeMismatch":
                fixed_code = self.fix_type_mismatch(code)
                
            elif error_type in ["NameError", "UndeclaredIdentifier"]:
                fixed_code = self.fix_name_error(code)
                
            elif error_type == "DivisionByZero":
                fixed_code = self.fix_division_by_zero(code)
                
            elif error_type == "MutableDefault":
                fixed_code = self.fix_mutable_default(code)
                
            elif error_type == "LineTooLong":
                fixed_code = self.fix_line_too_long(code)
            
            return {
                'fixed_code': fixed_code,
                'changes': self.fixes_applied,
                'success': fixed_code != code
            }
        
        except Exception as e:
            return {
                'fixed_code': code,
                'changes': [],
                'success': False,
                'error': str(e)
            }


def auto_fix_code(code: str, error_type: str, line_num: int | None = None) -> dict:
    """
    Convenience function for auto-fixing
    
    Args:
        code: Source code with error
        error_type: Type of syntax error detected
        line_num: Line number where error occurs (0-indexed)
    
    Returns:
        dict with fixed code and metadata
    """
    fixer = AutoFixer()
    return fixer.apply_fixes(code, error_type, line_num)


if __name__ == "__main__":
    # Test cases
    test_code_colon = """def hello()
    print('Hi')"""
    
    result = auto_fix_code(test_code_colon, "MissingColon", 0)
    print("Fixed Code:")
    print(result['fixed_code'])
    print("\nFixes Applied:")
    print(result['changes'])
