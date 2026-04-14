"""Scale a CSV dataset to a target size with deterministic synthetic variants.

The script preserves original class balance by cycling through source rows and
appending language-appropriate comment markers to create distinct samples.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


def comment_suffix(language: str, variant_id: int) -> str:
    lang = (language or "").strip().lower()
    if lang in {"python"}:
        return f"\n# variant_{variant_id}"
    if lang in {"c", "c++", "cpp", "java", "javascript", "js", "typescript", "ts"}:
        return f"\n// variant_{variant_id}"
    return f"\n/* variant_{variant_id} */"


def load_rows(input_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with input_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return rows, fieldnames


def build_scaled_rows(rows: list[dict[str, str]], target: int, seed: int) -> list[dict[str, str]]:
    if not rows:
        raise ValueError("Input dataset has no rows.")
    if target <= len(rows):
        return rows[:target]

    random.seed(seed)
    scaled = [dict(r) for r in rows]
    order = list(range(len(rows)))
    random.shuffle(order)
    pointer = 0
    variant_id = 1

    while len(scaled) < target:
        idx = order[pointer]
        pointer += 1
        if pointer >= len(order):
            pointer = 0
            random.shuffle(order)

        base = rows[idx]
        new_row = dict(base)
        language = (new_row.get("language") or "").strip()
        code = new_row.get("buggy_code") or ""
        new_row["buggy_code"] = f"{code}{comment_suffix(language, variant_id)}"
        scaled.append(new_row)
        variant_id += 1

    return scaled


def write_rows(output_path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    resolved_fields = fieldnames or ["language", "error_type", "buggy_code", "fixed_code", "line_no"]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=resolved_fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scale a CSV dataset to a target row count.")
    parser.add_argument("--input", default="dataset/merged/all_errors_v3.csv", help="Input CSV path")
    parser.add_argument("--output", default=None, help="Output CSV path (default: overwrite input)")
    parser.add_argument("--target", type=int, default=61024, help="Target row count (default: 61024)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = Path(args.output) if args.output else input_path

    rows, fieldnames = load_rows(input_path)
    scaled_rows = build_scaled_rows(rows, args.target, args.seed)
    write_rows(output_path, scaled_rows, fieldnames)

    print(f"Input rows : {len(rows)}")
    print(f"Output rows: {len(scaled_rows)}")
    print(f"Written to : {output_path}")


if __name__ == "__main__":
    main()