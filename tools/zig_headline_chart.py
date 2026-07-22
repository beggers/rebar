#!/usr/bin/env python3
"""Draw the latest, plain-language engine comparison for the expanded holdout."""

from __future__ import annotations

import argparse
import json
import math
from html import escape
from pathlib import Path


NAMES = {
    "candidates.ast_candidate": "Python engine",
    "candidates.vm_candidate": "Native C / rebar",
    "candidates.rust_candidate": "Rust engine",
    "candidates.zig_candidate": "Zig engine (latest)",
}
COLORS = {
    "candidates.ast_candidate": "#b45309",
    "candidates.vm_candidate": "#2563eb",
    "candidates.rust_candidate": "#7c3aed",
    "candidates.zig_candidate": "#059669",
}


def scale(value, left, width):
    return left + (math.log10(max(value, .01)) + 2) / 3 * width


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial", required=True)
    parser.add_argument("--zig", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    initial = json.loads(Path(args.initial).read_text(encoding="utf-8"))
    latest = json.loads(Path(args.zig).read_text(encoding="utf-8"))
    rows = []
    for value in initial["rankings"]:
        if value["cohort"] == "holdout" and value["candidate"] != "candidates.zig_candidate":
            rows.append({"candidate": value["candidate"], "speed": value["geomean_speedup"], "low": value["ci95_low"], "high": value["ci95_high"], "faster": value["statistically_faster_cases"], "losses": value["regressions_gt_20pct"], "cases": value["cases"]})
    value = next(item for item in latest["rankings"] if item["cohort"] == "holdout")
    rows.append({"candidate": "candidates.zig_candidate", "speed": value["speedup"], "low": value["ci95_low"], "high": value["ci95_high"], "faster": value["faster_cases"], "losses": value["slowdowns_gt_20pct"], "cases": value["cases"]})
    rows.sort(key=lambda item: item["speed"], reverse=True)
    cases = rows[0]["cases"]
    width, height = 1180, 404
    left, plot = 300, 500
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:24px;font-weight:700}.sub{font-size:14px;fill:#52627a}.head{font-size:16px;font-weight:700}.small{font-size:13px;fill:#52627a}.tick{font-size:12px;fill:#64748b}.grid{stroke:#dbe2ea;stroke-width:1}.base{stroke:#64748b;stroke-width:1.4}</style>',
        '<text x="24" y="38" class="title">How fast are the replacement engines?</text>',
        f'<text x="24" y="64" class="sub">{cases:,} unseen tasks. 1× is Python re; farther right is faster. Lines show the measured 95% range.</text>',
        '<text x="24" y="86" class="sub">Zig is the latest paired rerun; the other engines use the identical frozen protocol and their preserved paired results.</text>',
    ]
    for number, label in ((.01, ".01×"), (.03, ".03×"), (.1, ".1×"), (.3, ".3×"), (1, "1× Python re"), (3, "3×"), (10, "10×")):
        x = scale(number, left, plot)
        body.append(f'<line x1="{x:.1f}" y1="116" x2="{x:.1f}" y2="{height-24}" class="{"base" if number == 1 else "grid"}"/>')
        body.append(f'<text x="{x:.1f}" y="108" class="tick" text-anchor="middle">{label}</text>')
    for index, row in enumerate(rows):
        y = 155 + index * 62
        color = COLORS[row["candidate"]]
        low = scale(row["low"], left, plot)
        point = scale(row["speed"], left, plot)
        high = scale(row["high"], left, plot)
        body.extend((
            f'<text x="24" y="{y+5}" class="head">{escape(NAMES[row["candidate"]])}</text>',
            f'<line x1="{low:.1f}" y1="{y}" x2="{high:.1f}" y2="{y}" stroke="{color}" stroke-width="7" stroke-linecap="round"/>',
            f'<circle cx="{point:.1f}" cy="{y}" r="6" fill="{color}" stroke="#fff" stroke-width="1.5"/>',
            f'<text x="830" y="{y-4}" class="head">{row["speed"]:.3f}× as fast overall</text>',
            f'<text x="830" y="{y+17}" class="small">{row["faster"]:,}/{row["cases"]:,} clearly faster · {row["losses"]:,} large slowdowns</text>',
        ))
    body.append("</svg>\n")
    Path(args.output).write_text("".join(body), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
