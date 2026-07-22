#!/usr/bin/env python3
"""Draw a compact, plain-language coverage chart for the expanded performance holdout."""

import argparse
import json
from pathlib import Path


FAMILY_NAMES = {
    "long-literal": "Find a phrase in long text",
    "line-records": "Read log and status lines",
    "json-fields": "Find JSON-like fields",
    "html-tags": "Find markup tags and attributes",
    "markdown-links": "Find Markdown links",
    "source-tokens": "Read source-code tokens",
    "comment-strip": "Remove code and config comments",
    "url-extract": "Find web and file addresses",
    "email-extract": "Find email addresses",
    "ip-version": "Find IP and version numbers",
    "dates-numbers": "Find dates, times, and numbers",
    "phone-postcode": "Find phones and postcodes",
    "path-text": "Find text file paths",
    "path-bytes": "Find byte-buffer paths",
    "csv-fields": "Read quoted CSV fields",
    "quoted-escapes": "Find quoted and escaped text",
    "whitespace-clean": "Clean line spacing",
    "newline-normalize": "Normalize line endings",
    "split-delimiters": "Split common separators",
    "split-captures": "Split and keep separators",
    "replace-redact": "Hide secrets and tokens",
    "replace-template": "Reorder captured text",
    "replace-callback": "Replace with a Python function",
    "unicode-words": "Find multilingual words",
    "unicode-case": "Case-insensitive Unicode",
    "combining-emoji": "Find accents and emoji",
    "ascii-boundary": "Use ASCII-only boundaries",
    "byte-buffer": "Read bytes and mutable buffers",
    "lookaround": "Find text using nearby context",
    "backreference": "Match repeated captured text",
    "conditionals": "Match optional delimiters",
    "atomic-possessive": "Use controlled repeats",
    "nullable-empty": "Handle empty matches safely",
    "branch-alternatives": "Choose among many words",
    "class-heavy": "Match mixed character sets",
    "windowed": "Work inside an input slice",
    "scanner": "Scan text and bytes incrementally",
    "cold-compile": "Compile a new expression",
    "cold-module": "Compile and use once",
    "match-surface": "Read full match details",
}
API_NAMES = {"compile": "compile", "escape": "escape", "findall": "findall", "finditer": "finditer", "fullmatch": "fullmatch", "match": "match", "match-surface": "match details", "scanner": "scanner", "search": "search", "split": "split", "sub": "sub", "subn": "subn"}


def text_line(x, y, value, css, anchor=None):
    extra = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" class="{css}"{extra}>{value}</text>'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="performance/v5/manifest.json")
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    families = list(FAMILY_NAMES.items())
    if len(families) != manifest["expanded_families"]:
        raise RuntimeError("expanded family labels drifted from the frozen suite")
    apis = list(manifest["api_counts"].items())
    width = 1080
    family_top = 132
    family_row = 22
    api_top = family_top + ((len(families) + 1) // 2) * family_row + 50
    api_row = 23
    footer = api_top + len(apis) * api_row + 50
    height = footer + 92
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Expanded performance holdout coverage and correctness status">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:24px;font-weight:700}.sub{font-size:13px;fill:#526076}.head{font-size:16px;font-weight:700}.label{font-size:12px}.value{font-size:12px;font-weight:700}.note{font-size:12px;fill:#526076}.track{fill:#e2e8f0}</style>',
        text_line(28, 40, "Expanded Python re performance holdout", "title"),
        text_line(28, 63, f'{manifest["cohorts"]["holdout"]:,} holdout tasks · {manifest["cohorts"]["calibration"]:,} practice tasks · {manifest["cases"]:,} total · CPython {manifest["python"]}', "sub"),
        text_line(28, 86, f'{manifest["expanded_families"]} new everyday workload families × {manifest["variants_per_family"]} variations in each set · all {manifest["parent_cases"]:,} earlier tasks preserved', "sub"),
        text_line(28, 116, "What is in the expanded holdout?", "head"),
    ]
    for index, (_, label) in enumerate(families):
        column = index % 2
        row = index // 2
        x = 28 + column * 530
        y = family_top + row * family_row
        lines.extend((text_line(x, y + 14, label, "label"), f'<rect x="{x+320}" y="{y+2}" width="128" height="15" rx="3" class="track"/>', f'<rect x="{x+320}" y="{y+2}" width="128" height="15" rx="3" fill="#4f7fb8"/>', text_line(x + 506, y + 14, f'{manifest["variants_per_family"]} tasks', "value", "end")))
    lines.extend((text_line(28, api_top - 22, "Which Python re calls are exercised?", "head"), text_line(28, api_top - 2, "Counts include earlier tasks. Text, bytes, bytearray, memoryview, compiled, module-level, and fresh-compilation paths are included.", "note")))
    largest = max(value for _, value in apis)
    for index, (name, count) in enumerate(apis):
        y = api_top + 15 + index * api_row
        bar = round(640 * count / largest)
        lines.extend((text_line(28, y + 14, API_NAMES.get(name, name), "label"), f'<rect x="190" y="{y+2}" width="640" height="16" rx="3" class="track"/>', f'<rect x="190" y="{y+2}" width="{bar}" height="16" rx="3" fill="#60966f"/>', text_line(858, y + 14, f"{count:,} tasks", "value")))
    footer = api_top + 15 + len(apis) * api_row + 44
    failures = result["failed"]
    checks = result["checks"]
    color = "#238b64" if failures == 0 else "#c84c4c"
    byte_tasks = sum(manifest["input_counts"].get(name, 0) for name in ("bytes", "bytearray", "memoryview"))
    lines.extend((f'<rect x="24" y="{footer-28}" width="1032" height="84" rx="8" fill="#fff" stroke="#cbd5e1"/>', text_line(42, footer - 2, "Pre-timing correctness check", "head"), text_line(42, footer + 20, f'{checks-failures:,}/{checks:,} comparisons match frozen CPython results · {failures:,} failed', "value"), text_line(42, footer + 40, f'{manifest["trials"]} paired trials · {manifest["warmups"]} warmups · {manifest["bootstraps"]:,} confidence samples · equal weights · {byte_tasks:,} byte/buffer tasks', "note"), f'<circle cx="1023" cy="{footer+8}" r="10" fill="{color}"/>', '</svg>\n'))
    Path(args.output).write_text("".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
