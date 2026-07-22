#!/usr/bin/env python3
"""Draw a compact, plain-language coverage chart for the large performance holdout."""

import argparse
import json
from pathlib import Path


FAMILY_NAMES = {
    "literal-hit": "Find a short phrase (present)",
    "literal-miss": "Find a short phrase (absent)",
    "long-ending": "Find an ending in long text",
    "formatted-lines": "Find formatted lines",
    "prefix-check": "Check a formatted prefix",
    "whole-check": "Check a whole structured value",
    "nearby-capture": "Find and capture nearby text",
    "findall-tokens": "Find all tokens",
    "finditer-pairs": "Iterate over captured pairs",
    "split-keep": "Split and keep separators",
    "replace-groups": "Reorder captured text",
    "replace-callback": "Replace using a Python function",
    "bytes-tokens": "Find tokens in bytes",
    "bytes-buffer": "Iterate over byte buffers",
    "unicode-words": "Find Unicode words and emoji",
    "unicode-casefold": "Case-insensitive Unicode",
    "cold-compile": "Compile a new expression",
    "cold-search": "Compile, then search",
    "module-search": "Search through the module API",
    "module-replace": "Replace through the module API",
    "empty-iterator": "Iterate over empty matches",
    "references": "Match repeated captured text",
    "conditionals": "Conditional matching",
    "branch-control": "Controlled alternatives/repeats",
    "scanner-text": "Scan text incrementally",
    "scanner-bytes": "Scan bytes incrementally",
    "window-search": "Search inside a text window",
    "window-collection": "Collect inside a text window",
    "request-records": "Read request/log records",
    "everyday-address": "Find URLs, email, and dates",
    "structured-text": "Read config, paths, and quotes",
    "cleanup": "Clean and split everyday text",
    "escape": "Escape text and bytes",
    "bytes-replace": "Replace captured byte data",
    "ascii-mode": "ASCII-only word matching",
    "verbose-dotall": "Readable and multi-line patterns",
}

API_NAMES = {"compile": "compile", "escape": "escape", "findall": "findall", "finditer": "finditer", "fullmatch": "fullmatch", "match": "match", "match-surface": "match details", "scanner": "scanner", "search": "search", "split": "split", "sub": "sub", "subn": "subn"}


def text_line(x, y, value, css, anchor=None):
    extra = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" class="{css}"{extra}>{value}</text>'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="performance/v4/manifest.json")
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    families = list(FAMILY_NAMES.items())
    apis = list(manifest["api_counts"].items())
    width = 1080
    family_top = 132
    family_row = 22
    api_top = family_top + ((len(families) + 1) // 2) * family_row + 50
    api_row = 23
    footer = api_top + len(apis) * api_row + 50
    height = footer + 92
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Large performance holdout coverage and correctness status">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:24px;font-weight:700}.sub{font-size:13px;fill:#526076}.head{font-size:16px;font-weight:700}.label{font-size:12px}.value{font-size:12px;font-weight:700}.note{font-size:12px;fill:#526076}.track{fill:#e2e8f0}</style>',
        text_line(28, 40, "Large Python re performance holdout", "title"),
        text_line(28, 63, f'{manifest["cohorts"]["holdout"]:,} holdout tasks · {manifest["cohorts"]["calibration"]:,} matching practice tasks · {manifest["cases"]:,} total · CPython {manifest["python"]}', "sub"),
        text_line(28, 86, f'{manifest["large_families"]} new workload families × {manifest["variants_per_family"]} variations in each set · every earlier task preserved', "sub"),
        text_line(28, 116, "What is in the new holdout?", "head"),
    ]
    for index, (name, label) in enumerate(families):
        column = index % 2
        row = index // 2
        x = 28 + column * 530
        y = family_top + row * family_row
        lines.extend((text_line(x, y + 14, label, "label"), f'<rect x="{x+320}" y="{y+2}" width="128" height="15" rx="3" class="track"/>', f'<rect x="{x+320}" y="{y+2}" width="128" height="15" rx="3" fill="#4f7fb8"/>', text_line(x + 506, y + 14, f'{manifest["variants_per_family"]} tasks', "value", "end")))
    lines.extend((text_line(28, api_top - 22, "Which Python re calls are exercised?", "head"), text_line(28, api_top - 2, "Counts include the earlier tasks. Text, bytes, bytearray, memoryview, compiled, module-level, and fresh compilation paths are all included.", "note")))
    largest = max(value for _, value in apis)
    for index, (name, count) in enumerate(apis):
        y = api_top + 15 + index * api_row
        bar = round(640 * count / largest)
        lines.extend((text_line(28, y + 14, API_NAMES.get(name, name), "label"), f'<rect x="190" y="{y+2}" width="640" height="16" rx="3" class="track"/>', f'<rect x="190" y="{y+2}" width="{bar}" height="16" rx="3" fill="#60966f"/>', text_line(858, y + 14, f"{count:,} tasks", "value")))
    footer = api_top + 15 + len(apis) * api_row + 44
    failures = result["failed"]
    checks = result["checks"]
    color = "#238b64" if failures == 0 else "#c84c4c"
    lines.extend((f'<rect x="24" y="{footer-28}" width="1032" height="84" rx="8" fill="#fff" stroke="#cbd5e1"/>', text_line(42, footer - 2, "Pre-timing correctness check", "head"), text_line(42, footer + 20, f'{checks-failures:,}/{checks:,} comparisons match the frozen CPython results · {failures:,} failed', "value"), text_line(42, footer + 40, f'13 paired trials · 4 warmups · 2,000 confidence samples · equal task weights · {manifest["input_counts"].get("bytes",0)+manifest["input_counts"].get("bytearray",0)+manifest["input_counts"].get("memoryview",0):,} byte/buffer tasks', "note"), f'<circle cx="1023" cy="{footer+8}" r="10" fill="{color}"/>', '</svg>\n'))
    Path(args.output).write_text("".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
