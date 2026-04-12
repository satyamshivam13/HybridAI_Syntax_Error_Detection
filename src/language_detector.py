import os


def detect_language(code: str, filename: str | None = None) -> str:
    """
    Detect the programming language of the given source code.

    Priority:
      1. Filename extension (most reliable)
      2. Score-based keyword matching (content fallback)

    Returns one of: "Python", "Java", "C++", "C", "JavaScript", "Unknown"
    """
    code_lower = code.lower()

    # -------------------------
    # 1. Filename-based (CLI)
    # -------------------------
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".py":
            return "Python"
        if ext == ".java":
            return "Java"
        if ext == ".c":
            return "C"
        if ext in (".cpp", ".cc", ".cxx", ".hpp"):
            return "C++"
        if ext in (".js", ".jsx", ".ts", ".tsx"):
            return "JavaScript"

    # -------------------------
    # 2. Score-based content detection
    # -------------------------
    # Each language gets points for specific keywords.
    # More-specific patterns score higher to avoid mis-classification
    # (e.g. C's printf matching Python's print).
    scores = {"Python": 0, "Java": 0, "C++": 0, "C": 0, "JavaScript": 0}

    # --- C indicators (check BEFORE Python to avoid printf→print false match) ---
    if "printf(" in code_lower or "fprintf(" in code_lower or "scanf(" in code_lower:
        scores["C"] += 2
    if "#include" in code_lower:
        scores["C"] += 1
        scores["C++"] += 1
        # C-specific headers tip the balance toward C
        import re
        if re.search(r'#include\s*<\w+\.h>', code_lower):
            scores["C"] += 1
    if "int main" in code_lower:
        scores["C"] += 1
        scores["C++"] += 1

    # --- C++ indicators ---
    if "cout <<" in code_lower or "cin >>" in code_lower:
        scores["C++"] += 2
    if "std::" in code_lower:
        scores["C++"] += 2
    if "using namespace" in code_lower:
        scores["C++"] += 2

    # --- Java indicators ---
    if "system.out.println" in code_lower or "system.out.print" in code_lower:
        scores["Java"] += 2
    if "public class" in code_lower or "public static void main" in code_lower:
        scores["Java"] += 2
    if "import java." in code_lower:
        scores["Java"] += 2

    # --- JavaScript indicators ---
    import re
    if "console.log" in code_lower or "document.getelementbyid" in code_lower:
        scores["JavaScript"] += 2
    if re.search(r'\b(let|const|function|var)\b', code_lower):
        scores["JavaScript"] += 1
    if "=>" in code_lower:
        scores["JavaScript"] += 1

    # --- Python indicators ---
    if "def " in code_lower:
        scores["Python"] += 2
    if "import " in code_lower and "#include" not in code_lower and "import java." not in code_lower:
        scores["Python"] += 1
    # Only award print( for Python if no C-style printf evidence
    if "print(" in code_lower and scores["C"] == 0 and scores["C++"] == 0:
        scores["Python"] += 1
    if "elif " in code_lower or "except " in code_lower:
        scores["Python"] += 2

    # Return language with highest score (ties broken by dict order: Python first)
    best = max(scores, key=scores.__getitem__)
    return best if scores[best] > 0 else "Unknown"
