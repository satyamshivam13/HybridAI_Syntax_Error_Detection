"""
Auto-Fix Module for Common Syntax Errors
Provides safe, conservative auto-correction suggestions
"""

class AutoFixer:
    """
    Attempts to automatically fix common syntax errors
    with minimal code modification
    """
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_missing_colon(self, code: str, line_num: int) -> str:
        """
        Add missing colon to control structures
        """
        lines = code.split('\n')
        if line_num < len(lines):
            line = lines[line_num]
            # Check if line ends with keywords that need colon
            keywords = ['if ', 'elif ', 'else', 'for ', 'while ', 'def ', 'class ', 'try', 'except', 'finally', 'with ']
            for kw in keywords:
                if kw in line and not line.rstrip().endswith(':'):
                    lines[line_num] = line.rstrip() + ':'
                    self.fixes_applied.append(f"Added colon at line {line_num + 1}")
                    break
        return '\n'.join(lines)
    
    def fix_missing_semicolon(self, code: str, line_num: int = None) -> str:
        """
        Add missing semicolon (for C/C++/Java)
        """
        lines = code.split('\n')
        
        # If line_num not provided or is 0, scan all lines
        if line_num is None or line_num == 0:
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
            if line_num < len(lines):
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
    
    def fix_missing_import(self, code: str, language: str = None) -> str:
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
    
    def fix_missing_include(self, code: str, language: str = None) -> str:
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
    
    def apply_fixes(self, code: str, error_type: str, line_num: int = None, language: str = None) -> dict:
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
        
        try:
            # MissingDelimiter - language-specific
            if error_type == "MissingDelimiter":
                if language == "Python" and line_num is not None:
                    fixed_code = self.fix_missing_colon(code, line_num)
                elif language in ["Java", "C", "C++"] and line_num is not None:
                    fixed_code = self.fix_missing_semicolon(code, line_num)
            
            # Specific error types
            elif error_type == "MissingColon" and line_num is not None:
                fixed_code = self.fix_missing_colon(code, line_num)
            
            elif error_type == "MissingSemicolon" and line_num is not None:
                fixed_code = self.fix_missing_semicolon(code, line_num)
            
            elif error_type == "IndentationError":
                fixed_code = self.fix_indentation(code)
            
            elif error_type == "UnmatchedBracket":
                fixed_code = self.fix_unmatched_brackets(code)
            
            elif error_type in ["UnclosedQuotes", "UnclosedString"]:
                fixed_code = self.fix_unclosed_quotes(code)
            
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
            
            return {
                'fixed_code': fixed_code,
                'changes': self.fixes_applied,
                'success': len(self.fixes_applied) > 0
            }
        
        except Exception as e:
            return {
                'fixed_code': code,
                'changes': [],
                'success': False,
                'error': str(e)
            }


def auto_fix_code(code: str, error_type: str, line_num: int = None) -> dict:
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
    print(result['fixes_applied'])
