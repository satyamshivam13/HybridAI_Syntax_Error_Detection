EXPLANATIONS = {
    "MissingColon": {
        "why": "In Python, control structures and function definitions must end with a colon ':'.",
        "fix": "Add a colon ':' at the end of the statement (e.g., 'def function():' or 'if condition:')."
    },
    "MissingDelimiter": {
        "why": "Statements in C, C++, and Java must end with a semicolon ';'.",
        "fix": "Add a semicolon ';' at the end of the statement."
    },
    "IndentationError": {
        "why": "Python uses indentation to define code blocks. Inconsistent indentation causes errors.",
        "fix": "Indent the statement correctly (use 4 spaces per indentation level). Avoid mixing tabs and spaces."
    },
    "UnclosedString": {
        "why": "A string literal was started but not properly closed with a matching quote.",
        "fix": "Add the missing closing quote (' or \") to properly terminate the string."
    },
    "UnclosedQuotes": {
        "why": "A string literal was started but not properly closed with a matching quote.",
        "fix": "Add the missing closing quote (' or \") to properly terminate the string."
    },
    "UnmatchedBracket": {
        "why": "Every opening bracket '{', '(', '[' must have a matching closing bracket '}', ')', ']'.",
        "fix": "Add or remove brackets so that all pairs match correctly. Check for missing closing brackets."
    },
    "SyntaxError": {
        "why": "The code contains a syntax error that violates the language's grammar rules.",
        "fix": "Review the error message and correct the syntax issue according to the language specification."
    },
    "DivisionByZero": {
        "why": "Division by zero is mathematically undefined and will cause a runtime error or crash.",
        "fix": "Add a condition to check that the denominator is not zero before performing division."
    },
    "UndeclaredIdentifier": {
        "why": "A variable, function, or identifier is used without being declared first (common in C, C++, Java).",
        "fix": "Declare the variable or import the required identifier before using it."
    },
    "MissingInclude": {
        "why": "The function or object requires a header file that has not been included (C/C++).",
        "fix": "Add the required #include statement at the top of the file (e.g., #include <stdio.h>)."
    },
    "MissingImport": {
        "why": "A module, class, or function is used without being imported (Python/Java).",
        "fix": "Add the required import statement at the top of the file (e.g., 'import module' or 'import java.util.Scanner;')."
    },
    "TypeMismatch": {
        "why": "A value of one data type is being assigned or passed to a variable/parameter of a different, incompatible type.",
        "fix": "Convert the value to the correct type using type casting or change the variable's declared type."
    },
    "ImportError": {
        "why": "Python cannot find or import the specified module or package.",
        "fix": "Ensure the module is installed (use pip install) and the module name is spelled correctly."
    },
    "NameError": {
        "why": "A variable or function name is used before it has been defined (Python).",
        "fix": "Define the variable or function before using it, or check for typos in the name."
    },
    "InvalidAssignment": {
        "why": "An invalid assignment is being made, such as assigning to a literal or constant.",
        "fix": "Assign to a valid variable name, not to literals, constants, or function calls."
    },
    "DuplicateDefinition": {
        "why": "A variable, function, or class is defined multiple times with the same name.",
        "fix": "Remove duplicate definitions or rename one to avoid conflicts."
    },
    "UnusedVariable": {
        "why": "A variable is declared but never used in the code (code quality issue).",
        "fix": "Remove the unused variable or use it in the code if it was intended to be used."
    },
    "UnreachableCode": {
        "why": "Code appears after a return statement or in a location that can never be executed.",
        "fix": "Remove the unreachable code or restructure the logic so all code can be reached."
    },
    "InfiniteLoop": {
        "why": "A loop has no exit condition or the condition is always true, causing it to run forever.",
        "fix": "Add a proper exit condition or ensure the loop variable changes to eventually break the loop."
    },
    "WildcardImport": {
        "why": "Using wildcard imports (e.g., 'from module import *') is discouraged as it pollutes the namespace.",
        "fix": "Import specific names instead (e.g., 'from module import SpecificClass') for better code clarity."
    },
    "MutableDefault": {
        "why": "Using a mutable object (like a list or dict) as a default function argument can cause unexpected behavior.",
        "fix": "Use None as the default and initialize the mutable object inside the function."
    },
    "LineTooLong": {
        "why": "The line exceeds the recommended maximum length (typically 79-120 characters), affecting readability.",
        "fix": "Break the line into multiple lines using proper continuation or refactor to simplify the code."
    }
}

def explain_error(error_type: str) -> dict[str, str]:
    return EXPLANATIONS.get(
        error_type,
        {
            "why": "The code contains a structural or syntactic issue.",
            "fix": "Review the code structure and correct the error."
        }
    )
