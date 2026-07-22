#!/usr/bin/env python3
"""Draw a plain-language coverage chart for the broader performance holdout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FAMILY_NAMES = (
    ("request-logs", "Read web request logs"), ("error-stack", "Read error stack lines"), ("http-headers", "Read HTTP headers"),
    ("html-attributes", "Read markup attributes"), ("markdown-code", "Read Markdown and code"), ("sql-tokens", "Scan SQL-like text"),
    ("config-lines", "Read configuration lines"), ("shell-vars", "Replace shell variables"), ("source-comments", "Remove source comments"),
    ("uuid-hash", "Find IDs and hashes"), ("version-tags", "Check version tags"), ("money-units", "Find money and units"),
    ("dates-zones", "Find dates and time zones"), ("file-names", "Find common file names"), ("path-mixed-bytes", "Find paths in byte buffers"),
    ("csv-split-even", "Split quoted CSV-like text"), ("quote-captures", "Find quoted values"), ("email-mixed", "Find email addresses"),
    ("unicode-word-lines", "Read multilingual lines"), ("unicode-casefold", "Find Unicode without case"), ("combining-wide", "Find accents, emoji, and CJK"),
    ("byte-highbit", "Read non-ASCII bytes"), ("buffer-tokenize", "Scan mutable byte buffers"), ("dense-literal-findall", "Find many repeated words"),
    ("dense-class-finditer", "Iterate over many tokens"), ("boundary-positions", "Find word and separator edges"), ("nullable-positions", "Handle empty matches safely"),
    ("lookahead-chain", "Check several following values"), ("lookbehind-chain", "Check several preceding values"), ("backref-named", "Match repeated captured text"),
    ("conditionals-nested", "Match conditional endings"), ("atomic-alternatives", "Use controlled alternatives"), ("bounded-repeats", "Match bounded repeated fields"),
    ("shared-prefix-alternatives", "Choose words with shared prefixes"), ("negative-class", "Read fields with excluded text"), ("multiline-anchors", "Read anchored multi-line fields"),
    ("inline-modes", "Use local matching modes"), ("search-long-hit", "Find a phrase in long text"), ("search-long-miss", "Search long text for an absent phrase"),
    ("match-short", "Check a short prefix"), ("fullmatch-structured", "Check a complete structured value"), ("module-warm-search", "Repeat a module-level search"),
    ("module-warm-sub", "Repeat a module-level replacement"), ("cold-compile", "Compile a new expression"), ("escape-mixed", "Escape mixed text and bytes"),
    ("windowed-collect", "Collect values in an input slice"), ("scanner-window", "Scan inside an input slice"), ("match-access", "Read complete match details"),
)


def line(x, y, text, css, anchor=None):
    return f'<text x="{x}" y="{y}" class="{css}"' + (f' text-anchor="{anchor}"' if anchor else "") + f'>{text}</text>'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="performance/v6/manifest.json")
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    if len(FAMILY_NAMES) != manifest["expanded_families"]:
        raise RuntimeError("broader family labels drifted from the frozen suite")
    apis = list(manifest["api_counts"].items())
    width = 1180
    top = 134
    row = 22
    api_top = top + ((len(FAMILY_NAMES) + 1) // 2) * row + 52
    api_row = 23
    footer = api_top + len(apis) * api_row + 64
    height = footer + 76
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Broader Python re performance holdout coverage and correctness status">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:24px;font-weight:700}.sub{font-size:13px;fill:#526076}.head{font-size:16px;font-weight:700}.label{font-size:12px}.value{font-size:12px;font-weight:700}.note{font-size:12px;fill:#526076}.track{fill:#e2e8f0}</style>',
        line(28, 40, "Broader Python re performance holdout", "title"),
        line(28, 63, f'{manifest["cohorts"]["holdout"]:,} holdout tasks · {manifest["cohorts"]["calibration"]:,} practice tasks · {manifest["cases"]:,} total · CPython {manifest["python"]}', "sub"),
        line(28, 86, f'{manifest["expanded_families"]} new workload families × {manifest["variants_per_family"]} variations in each set · all {manifest["parent_cases"]:,} earlier tasks preserved', "sub"),
        line(28, 118, "What is in the new holdout?", "head"),
    ]
    for index, (_, label) in enumerate(FAMILY_NAMES):
        column, item = index % 2, index // 2
        x, y = 28 + column * 572, top + item * row
        pieces.extend((line(x, y + 14, label, "label"), f'<rect x="{x+355}" y="{y+2}" width="128" height="15" rx="3" class="track"/>', f'<rect x="{x+355}" y="{y+2}" width="128" height="15" rx="3" fill="#4f7fb8"/>', line(x + 555, y + 14, f'{manifest["variants_per_family"]} tasks', "value", "end")))
    pieces.extend((line(28, api_top - 24, "Which Python re calls are exercised?", "head"), line(28, api_top - 3, "Counts include earlier tasks. Text, bytes, bytearray, memoryview, compiled, module-level, and fresh-compilation paths are included.", "note")))
    largest = max(count for _, count in apis)
    for index, (name, count) in enumerate(apis):
        y = api_top + index * api_row
        bar = round(680 * count / largest)
        pieces.extend((line(28, y + 14, name.replace("match-surface", "match details"), "label"), f'<rect x="205" y="{y+2}" width="680" height="16" rx="3" class="track"/>', f'<rect x="205" y="{y+2}" width="{bar}" height="16" rx="3" fill="#60966f"/>', line(925, y + 14, f"{count:,} tasks", "value")))
    failures = result["failed"]
    checks = result["checks"]
    byte_tasks = sum(manifest["input_counts"].get(name, 0) for name in ("bytes", "bytearray", "memoryview"))
    pieces.extend((f'<rect x="24" y="{footer-25}" width="1132" height="76" rx="8" fill="#fff" stroke="#cbd5e1"/>', line(42, footer, "Pre-timing correctness check", "head"), line(42, footer + 20, f'{checks-failures:,}/{checks:,} comparisons match frozen CPython results · {failures:,} failed', "value"), line(42, footer + 40, f'{manifest["trials"]} paired trials · {manifest["warmups"]} warmups · {manifest["bootstraps"]:,} confidence samples · equal weights · {byte_tasks:,} byte/buffer tasks', "note"), f'<circle cx="1127" cy="{footer+11}" r="10" fill="{"#238b64" if failures == 0 else "#c84c4c"}"/>', '</svg>\n'))
    Path(args.output).write_text("".join(pieces), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
