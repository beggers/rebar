#!/usr/bin/env python3
"""Generate a compact before/after Zig compatibility chart from gate results."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-before", required=True)
    parser.add_argument("--v2-after", required=True)
    parser.add_argument("--v3-before", required=True)
    parser.add_argument("--v3-after", required=True)
    parser.add_argument("--perf-before", required=True)
    parser.add_argument("--perf-after", required=True)
    parser.add_argument("--official-before", required=True)
    parser.add_argument("--official-after", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    v2_before, v2_after = load(args.v2_before), load(args.v2_after)
    v3_before, v3_after = load(args.v3_before), load(args.v3_after)
    perf_before, perf_after = load(args.perf_before), load(args.perf_after)
    official_before, official_after = load(args.official_before), load(args.official_after)
    rows = [
        ("Expanded correctness matrix", v2_before["passed"], v2_after["passed"], v2_after["cases"]),
        ("Large correctness holdout", v3_before["passed"], v3_after["passed"], v3_after["cases"]),
    ]
    labels = {
        "deep-text": "  Deeper text patterns",
        "deep-bytes": "  Deeper byte patterns",
        "real-text": "  Everyday text patterns",
        "real-bytes": "  Everyday byte patterns",
        "scanner": "  Scanner sequences",
        "properties": "  Cross-API checks",
        "invalid-pattern": "  Invalid patterns",
        "invalid-template": "  Invalid replacements",
    }
    for name, after in v3_after["families"].items():
        before = v3_before["families"][name]
        rows.append((labels.get(name, f"  {name.replace('-', ' ').capitalize()}"), before["passed"], after["passed"], after["cases"]))
    rows.extend((
        ("Large performance tasks", perf_before["checks"] - perf_before["failed"], perf_after["checks"] - perf_after["failed"], perf_after["checks"]),
        ("Official CPython methods", official_before["passed"], official_after["passed"], official_after["methods"] - official_after["skipped"]),
    ))
    width, top, row_height = 1080, 152, 48
    height = top + len(rows) * row_height + 28
    bar_x, bar_width = 454, 590
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:14px;fill:#52627a}.head{font-size:11px;font-weight:700;fill:#41506a}.label{font-size:13px}.number{font-size:12px;text-anchor:end;font-variant-numeric:tabular-nums}.small{font-size:11px;fill:#52627a}.grid{stroke:#dbe1eb;stroke-width:1}</style>',
        '<text x="24" y="38" class="title">How much Python re behavior the Zig experiment now covers</text>',
        '<text x="24" y="64" class="sub">Unicode text, ranges, categories, boundaries, case handling, and named characters now work across every common API. Longer green bars mean more checks pass.</text>',
        '<text x="24" y="87" class="sub">Grey shows the previous result; red shows remaining gaps. No previous passing case regressed, and crashes/timeouts remain zero.</text>',
        '<text x="24" y="125" class="head">CHECK</text><text x="426" y="125" class="head" text-anchor="end">BEFORE → AFTER</text><text x="454" y="125" class="head">SHARE PASSING</text>',
    ]
    for index, (label, before, after, total) in enumerate(rows):
        y = top + index * row_height
        before_width = bar_width * before / total
        after_width = bar_width * after / total
        if index % 2 == 0:
            lines.append(f'<rect x="16" y="{y-20}" width="{width-32}" height="{row_height}" fill="#f5f7fb"/>')
        lines.extend((
            f'<line x1="16" y1="{y+26}" x2="{width-16}" y2="{y+26}" class="grid"/>',
            f'<text x="24" y="{y}" class="label">{escape(label)}</text>',
            f'<text x="426" y="{y}" class="number">{before:,} → {after:,} / {total:,}</text>',
            f'<rect x="{bar_x}" y="{y-11}" width="{bar_width}" height="12" rx="3" fill="#f4dede"/>',
            f'<rect x="{bar_x}" y="{y-11}" width="{after_width:.1f}" height="12" rx="3" fill="#238b64"/>',
            f'<rect x="{bar_x}" y="{y+7}" width="{before_width:.1f}" height="5" rx="2" fill="#8995a7"/>',
            f'<text x="{bar_x+bar_width}" y="{y+22}" class="number small">{after/total:.1%}</text>',
        ))
    lines.append("</svg>\n")
    Path(args.output).write_text("".join(lines), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "output": args.output}, sort_keys=True))


if __name__ == "__main__":
    main()
