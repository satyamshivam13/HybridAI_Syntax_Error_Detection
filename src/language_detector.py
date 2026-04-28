import os
import re

_PREPROCESSOR_PREFIXES = (
    '#include',
    '#define',
    '#if',
    '#ifdef',
    '#ifndef',
    '#elif',
    '#else',
    '#endif',
    '#pragma',
    '#error',
    '#line',
)


def _strip_inline_comments(raw_line: str, allow_hash_comment: bool) -> str:
    cleaned: list[str] = []
    quote: str | None = None
    escaped = False
    index = 0

    while index < len(raw_line):
        ch = raw_line[index]

        if escaped:
            cleaned.append(ch)
            escaped = False
            index += 1
            continue

        if quote:
            cleaned.append(ch)
            if ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
            index += 1
            continue

        if ch in {'"', "'", '`'}:
            quote = ch
            cleaned.append(ch)
            index += 1
            continue

        if allow_hash_comment and ch == '#':
            break
        if ch == '/' and index + 1 < len(raw_line):
            next_ch = raw_line[index + 1]
            if next_ch == '/':
                break
            if next_ch == '*':
                end = raw_line.find('*/', index + 2)
                if end == -1:
                    return ''.join(cleaned).rstrip()
                index = end + 2
                continue

        cleaned.append(ch)
        index += 1

    return ''.join(cleaned).rstrip()


def _strip_comment_noise(code: str) -> str:
    cleaned_lines: list[str] = []
    in_block_comment = False

    for raw_line in code.splitlines():
        working = raw_line

        while True:
            if in_block_comment:
                end = working.find('*/')
                if end == -1:
                    working = ''
                    break
                working = working[end + 2 :]
                in_block_comment = False
                continue

            stripped = working.lstrip()
            if not stripped:
                working = ''
                break

            if stripped.startswith('/*'):
                end = stripped.find('*/', 2)
                if end == -1:
                    in_block_comment = True
                    working = ''
                    break
                working = stripped[end + 2 :]
                continue

            break

        if not working.strip():
            continue

        stripped = working.lstrip()
        if stripped.startswith('//'):
            continue
        if stripped.startswith('#') and not stripped.startswith(_PREPROCESSOR_PREFIXES):
            continue

        allow_hash_comment = not stripped.startswith(_PREPROCESSOR_PREFIXES)
        cleaned_line = _strip_inline_comments(working, allow_hash_comment=allow_hash_comment)
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)


def detect_language(code: str | None, filename: str | None = None) -> str:
    """
    Detect the programming language of the given source code.

    Priority:
      1. Filename extension (most reliable)
      2. Score-based keyword matching (content fallback)

    Returns one of: "Python", "Java", "C++", "C", "JavaScript", "Unknown"
    """
    if not isinstance(code, str):
        return 'Unknown'

    code = _strip_comment_noise(code)
    code_lower = code.lower()

    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.py':
            return 'Python'
        if ext == '.java':
            return 'Java'
        if ext == '.c':
            return 'C'
        if ext in ('.cpp', '.cc', '.cxx', '.hpp'):
            return 'C++'
        if ext in ('.js', '.jsx', '.ts', '.tsx'):
            return 'JavaScript'

    scores = {'Python': 0, 'Java': 0, 'C++': 0, 'C': 0, 'JavaScript': 0}
    line_count = sum(1 for line in code.splitlines() if line.strip())

    if 'printf(' in code_lower or 'fprintf(' in code_lower or 'scanf(' in code_lower:
        scores['C'] += 2
    if '#include' in code_lower:
        scores['C'] += 1
        scores['C++'] += 1
        if re.search(r'#include\s*<\w+\.h>', code_lower):
            scores['C'] += 1
    if 'int main' in code_lower:
        scores['C'] += 1
        scores['C++'] += 1

    if 'cout <<' in code_lower or 'cin >>' in code_lower:
        scores['C++'] += 2
    if 'std::' in code_lower:
        scores['C++'] += 2
    if 'using namespace' in code_lower:
        scores['C++'] += 2

    if 'system.out.println' in code_lower or 'system.out.print' in code_lower:
        scores['Java'] += 2
    if 'public class' in code_lower or 'public static void main' in code_lower:
        scores['Java'] += 2
    if 'import java.' in code_lower:
        scores['Java'] += 2

    if 'console.log' in code_lower or 'document.getelementbyid' in code_lower:
        scores['JavaScript'] += 2
    if re.search(r'\b(let|const|function|var)\b', code_lower):
        scores['JavaScript'] += 1
    if '=>' in code_lower:
        scores['JavaScript'] += 1

    if 'def ' in code_lower:
        scores['Python'] += 2
    if 'import ' in code_lower and '#include' not in code_lower and 'import java.' not in code_lower:
        scores['Python'] += 1
    if 'print(' in code_lower and scores['C'] == 0 and scores['C++'] == 0:
        scores['Python'] += 1
    if 'elif ' in code_lower or 'except ' in code_lower:
        scores['Python'] += 2

    best = max(scores, key=scores.__getitem__)
    best_score = scores[best]
    if best_score == 0:
        return 'Unknown'
    if line_count <= 2 and best_score < 2:
        return 'Unknown'
    return best


