from .language_detector import detect_language
from .ml_engine import detect_error_ml
from .syntax_checker import detect_all
from .tutor_explainer import explain_error

CONFIDENCE_THRESHOLD = 0.65


def detect_errors(code: str, filename: str | None = None):
    # 🔑 language detection WITH filename
    language = detect_language(code, filename)

    # ------------------------------------------------
    # 1. Python: Rule-based detection is FINAL
    # ------------------------------------------------
    rule_based_issues = []

    if language == "Python":
        rule_based_issues = detect_all(code)

        if not rule_based_issues:
            return {
                "language": language,
                "predicted_error": "NoError",
                "confidence": 1.0,
                "tutor": {
                    "why": "The Python code follows correct syntax rules.",
                    "fix": "No changes are required."
                },
                "rule_based_issues": []
            }
        
        # If issues found, return the first detected error type
        primary_error = rule_based_issues[0].get('type', 'SyntaxError')
        tutor_help = explain_error(primary_error)
        return {
            "language": language,
            "predicted_error": primary_error,
            "confidence": 1.0,
            "tutor": tutor_help,
            "rule_based_issues": rule_based_issues
        }

    # ------------------------------------------------
    # 2. ML-based prediction
    # ------------------------------------------------
    ml_error, confidence = detect_error_ml(code)

    # ------------------------------------------------
    # 3. HARD RULES: Java / C / C++
    # ------------------------------------------------
    if language in ["Java", "C", "C++"]:
        lines = [l.strip() for l in code.splitlines() if l.strip()]

        # More sophisticated semicolon check
        semicolon_required_lines = []
        import re
        # Patterns for simple statements that require semicolons
        simple_statements = [
            r'^return\s+.+$',                # return statements
            r'^cout\s*<<.*$',                # C++ cout
            r'^cin\s*>>.*$',                 # C++ cin
            r'^printf\s*\(.*\)$',          # C printf
            r'^fprintf\s*\(.*\)$',         # C fprintf
            r'^puts\s*\(.*\)$',            # C puts
            r'^std::cout\s*<<.*$',           # C++ std::cout
            r'^std::cin\s*>>.*$',            # C++ std::cin
        ]
        for l in lines:
            # Skip comments, preprocessor directives, and control structures
            if (l.startswith('//') or l.startswith('/*') or l.startswith('*') or 
                l.startswith('#') or l.endswith('{') or l.endswith('}') or
                l.startswith('import') or l.startswith('package') or
                l.startswith('using') or l.startswith('namespace') or
                l.startswith('public class') or l.startswith('class ') or
                l.startswith('private class') or l.startswith('protected class')):
                continue
            # Check if line looks like it needs a semicolon but doesn't have one
            is_control = any(keyword in l for keyword in [
                'if (', 'if(', 'for (', 'for(', 'while (', 'while(', 'else', 'try', 'catch', 
                'switch (', 'switch(', 'case ', 'default:', 'do ', 'do{'
            ])
            if not is_control and not l.endswith(';') and not l.endswith('{') and not l.endswith('}'):
                # Check for simple statement patterns
                if any(re.match(pat, l) for pat in simple_statements):
                    semicolon_required_lines.append(l)
                # Also check for assignment or function call
                elif ('=' in l or ('(' in l and ')' in l)) and not l.startswith('}'):
                    semicolon_required_lines.append(l)

        # ❌ Missing semicolon is ALWAYS an error
        if semicolon_required_lines:
            tutor_help = explain_error("MissingDelimiter")
            return {
                "language": language,
                "predicted_error": "MissingDelimiter",
                "confidence": 1.0,
                "tutor": tutor_help,
                "rule_based_issues": []
            }

        # ✅ Semicolons OK → Code is valid (rule-based check passed)
        # For Java/C/C++, rule-based check is authoritative for semicolons
        return {
            "language": language,
            "predicted_error": "NoError",
            "confidence": 1.0,
            "tutor": {
                "why": "The code follows valid syntax rules for this language.",
                "fix": "No changes are required."
            },
            "rule_based_issues": []
        }

    # ------------------------------------------------
    # 4. Fallback (non-Java languages only)
    # ------------------------------------------------
    if language not in ["Java", "C", "C++"] and confidence < CONFIDENCE_THRESHOLD:
        return {
            "language": language,
            "predicted_error": "NoError",
            "confidence": confidence,
            "tutor": {
                "why": "The code structure appears syntactically correct.",
                "fix": "No changes are required."
            },
            "rule_based_issues": []
        }

    # ------------------------------------------------
    # 5. ERROR CASE
    # ------------------------------------------------
    tutor_help = explain_error(ml_error)

    return {
        "language": language,
        "predicted_error": ml_error,
        "confidence": confidence,
        "tutor": tutor_help,
        "rule_based_issues": rule_based_issues
    }
