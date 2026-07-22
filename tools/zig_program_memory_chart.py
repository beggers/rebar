#!/usr/bin/env python3
"""Generate a readable compiled-program memory chart for the expanded Zig holdout."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


PREVIOUS_BYTES = 423960


def label(category):
    return category.removeprefix("large-").removeprefix("expanded-").replace("-", " ").capitalize()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    families = [value for value in data["families"] if value["cohort"] == "holdout" and value["category"].startswith(("large-", "expanded-"))]
    families.sort(key=lambda value: value["median_bytes"], reverse=True)
    width, top, row = 1120, 148, 24
    height = top + len(families) * row + 36
    bar_x, bar_width = 748, 338
    maximum = max(value["maximum_bytes"] for value in families)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:14px;fill:#52627a}.head{font-size:11px;font-weight:700;fill:#41506a}.label{font-size:12px}.number{font-size:12px;text-anchor:end;font-variant-numeric:tabular-nums}.grid{stroke:#dbe1eb;stroke-width:1}</style>',
        '<text x="24" y="38" class="title">Memory used by each compiled Zig expression</text>',
        f'<text x="24" y="64" class="sub">The old fixed program used {PREVIOUS_BYTES:,} B for every expression. The new arena uses {data["minimum_bytes"]:,}–{data["maximum_bytes"]:,} B across all {data["cases"]:,} tasks; less is better.</text>',
        '<text x="24" y="86" class="sub">Rows show every balanced holdout family. Labels give the median and range; the bar shows the median on a shared linear scale.</text>',
        '<text x="24" y="124" class="head">KIND OF TASK</text><text x="724" y="124" class="head" text-anchor="end">MEDIAN · RANGE · SHARE OF OLD</text><text x="918" y="124" class="head" text-anchor="middle">COMPILED BYTES</text>',
    ]
    for index, value in enumerate(families):
        y = top + index * row
        median = value["median_bytes"]
        if index % 2 == 0:
            lines.append(f'<rect x="16" y="{y-16}" width="{width-32}" height="{row}" fill="#f5f7fb"/>')
        lines.extend((
            f'<line x1="16" y1="{y+8}" x2="{width-16}" y2="{y+8}" class="grid"/>',
            f'<text x="24" y="{y}" class="label">{escape(label(value["category"]))}</text>',
            f'<text x="724" y="{y}" class="number">{median:,} B · {value["minimum_bytes"]:,}–{value["maximum_bytes"]:,} · {median/PREVIOUS_BYTES:.1%}</text>',
            f'<rect x="{bar_x}" y="{y-11}" width="{bar_width*median/maximum:.1f}" height="11" rx="2.5" fill="#238b64"/>',
        ))
    lines.append("</svg>\n")
    Path(args.output).write_text("".join(lines), encoding="utf-8")
    print(json.dumps({"families": len(families), "cases": data["cases"], "previous_bytes": PREVIOUS_BYTES, "output": args.output}, sort_keys=True))


if __name__ == "__main__":
    main()
