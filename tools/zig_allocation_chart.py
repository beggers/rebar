#!/usr/bin/env python3
"""Draw readable before/after allocation and speed results for the Zig engine."""

import argparse
import json
import math
from pathlib import Path


def label(value):
    return value.replace("-", " ").title()


def xlog(value, left, width, low, high):
    point = max(low, min(high, math.log10(max(value, 1e-12))))
    return left + round((point - low) * width / (high - low))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))
    previous = {row["case"]: row for row in before["results"]}
    rows = after["results"]
    if set(previous) != {row["case"] for row in rows}:
        raise ValueError("before/after cases differ")
    width, left, plot, row_height = 1160, 270, 600, 28
    speed_top = 122
    memory_top = speed_top + len(rows) * row_height + 88
    height = memory_top + len(rows) * row_height + 55
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Zig allocation before and after">', '<rect width="100%" height="100%" fill="#f8fafc"/>', '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:13px;fill:#526076}.head{font-size:16px;font-weight:700}.label{font-size:12px}.small{font-size:11px;fill:#526076}.value{font-size:12px;font-weight:700}</style>', '<text x="28" y="38" class="title">Zig collection allocation: before and after</text>', f'<text x="28" y="61" class="sub">{after["cases"]} correctness-gated cases · {after["correctness_checks"]} checks · stack-backed, resumable capture records replace worst-case input-sized buffers</text>', '<text x="28" y="96" class="head">End-to-end speed compared with Python re</text>']
    for exponent, value in ((-1, "0.1×"), (0, "1× baseline"), (1, "10×")):
        x = xlog(10**exponent, left, plot, -1, 1)
        lines.extend((f'<line x1="{x}" y1="{speed_top-12}" x2="{x}" y2="{speed_top+len(rows)*row_height}" stroke="{"#334155" if exponent==0 else "#cbd5e1"}" stroke-width="{2 if exponent==0 else 1}"/>', f'<text x="{x}" y="{speed_top-18}" class="small" text-anchor="middle">{value}</text>'))
    for index, row in enumerate(rows):
        old = previous[row["case"]]
        y = speed_top + index * row_height
        first = xlog(old["speedup"], left, plot, -1, 1)
        second = xlog(row["speedup"], left, plot, -1, 1)
        lines.extend((f'<text x="28" y="{y+5}" class="label">{label(row["case"])}</text>', f'<line x1="{first}" y1="{y}" x2="{second}" y2="{y}" stroke="#94a3b8" stroke-width="2"/>', f'<circle cx="{first}" cy="{y}" r="4" fill="#94a3b8"/>', f'<circle cx="{second}" cy="{y}" r="4.5" fill="#2563eb"/>', f'<text x="894" y="{y+5}" class="value">{old["speedup"]:.2f}× → {row["speedup"]:.2f}×</text>'))
    lines.extend((f'<text x="28" y="{memory_top-30}" class="head">Peak traced Python memory used by Zig</text>', f'<text x="28" y="{memory_top-11}" class="small">Grey is the input-sized buffer used before; blue is the new growing capture stream. Lower is better.</text>'))
    for exponent, value in ((1, "10 B"), (2, "100 B"), (3, "1 KB"), (4, "10 KB"), (5, "100 KB"), (6, "1 MB"), (7, "10 MB")):
        x = xlog(10**exponent, left, plot, 1, 7)
        lines.extend((f'<line x1="{x}" y1="{memory_top+5}" x2="{x}" y2="{memory_top+len(rows)*row_height+12}" stroke="#cbd5e1"/>', f'<text x="{x}" y="{memory_top-1}" class="small" text-anchor="middle">{value}</text>'))
    for index, row in enumerate(rows):
        old = previous[row["case"]]
        y = memory_top + 24 + index * row_height
        first = xlog(old["zig_peak_bytes"], left, plot, 1, 7)
        second = xlog(row["zig_peak_bytes"], left, plot, 1, 7)
        lines.extend((f'<text x="28" y="{y+5}" class="label">{label(row["case"])}</text>', f'<line x1="{first}" y1="{y}" x2="{second}" y2="{y}" stroke="#94a3b8" stroke-width="2"/>', f'<circle cx="{first}" cy="{y}" r="4" fill="#94a3b8"/>', f'<circle cx="{second}" cy="{y}" r="4.5" fill="#2563eb"/>', f'<text x="894" y="{y+5}" class="value">{old["zig_peak_bytes"]:,} → {row["zig_peak_bytes"]:,} B</text>'))
    lines.append("</svg>\n")
    Path(args.output).write_text("".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
