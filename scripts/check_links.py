"""
Validate local markdown links across repository documentation.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "#"))


def _collect_markdown_files(root: Path) -> list[Path]:
    return sorted([*root.glob("*.md"), *root.glob("docs/*.md")])


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local markdown links")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    failures: list[str] = []

    for md_file in _collect_markdown_files(root):
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        for raw_target in LINK_PATTERN.findall(text):
            target = raw_target.strip()
            if not target or _is_external(target):
                continue
            target_path = target.split("#", 1)[0]
            resolved = (md_file.parent / target_path).resolve()
            if not resolved.exists():
                failures.append(f"{md_file.relative_to(root)} -> {target}")

    if failures:
        print("Broken markdown links found:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("Markdown link check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
