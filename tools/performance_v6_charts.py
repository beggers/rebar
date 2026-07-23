#!/usr/bin/env python3
"""Draw clear, reproducible charts for the broader regex performance holdout."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from html import escape
from pathlib import Path


NAMES = {
    "candidates.ast_candidate": "Python engine",
    "candidates.vm_candidate": "Native C engine",
    "candidates.rust_candidate": "Rust engine",
    "candidates.zig_candidate": "Zig / rebar",
}
COLORS = {
    "candidates.ast_candidate": "#b45309",
    "candidates.vm_candidate": "#2563eb",
    "candidates.rust_candidate": "#7c3aed",
    "candidates.zig_candidate": "#059669",
}


def geometric(values):
    values = list(values)
    return math.exp(sum(map(math.log, values)) / len(values))


def fmt(value):
    if value >= 10:
        return f"{value:.1f}×"
    if value >= .1:
        return f"{value:.2f}×"
    return f"{value:.3f}×"


def label(category):
    return category.removeprefix("deeper-").replace("-", " ").title()


def page(width, height, title, subtitle):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:24px;font-weight:700}.sub{font-size:13px;fill:#52627a}.head{font-size:16px;font-weight:700}.label{font-size:12px}.small{font-size:11px;fill:#52627a}.value{font-size:12px;font-weight:700}.tick{font-size:11px;fill:#64748b}.grid{stroke:#dde5ed;stroke-width:1}.base{stroke:#64748b;stroke-width:1.4}</style>',
        f'<text x="24" y="38" class="title">{escape(title)}</text>',
        f'<text x="24" y="61" class="sub">{escape(subtitle)}</text>',
    ]


def save(path, body):
    Path(path).write_text("".join([*body, "</svg>\n"]), encoding="utf-8")
    print(f"wrote {path}")


def xlog(value, left, width, low, high):
    return left + (max(low, min(high, math.log10(max(value, 1e-12)))) - low) / (high - low) * width


def grid(body, left, right, top, bottom, low, high, ticks):
    for value, text in ticks:
        x = xlog(value, left, right - left, low, high)
        body.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" class="{"base" if value == 1 else "grid"}"/>')
        body.append(f'<text x="{x:.1f}" y="{top-6}" class="tick" text-anchor="middle">{text}</text>')


def ordered(summary):
    values = (row for row in summary["rankings"] if row["cohort"] == "holdout")
    return sorted(values, key=lambda row: row["geomean_speedup"], reverse=True)


def overall(summary, output):
    rows = ordered(summary)
    width, height, left, right = 1220, 150 + len(rows) * 64, 285, 815
    body = page(width, height, "How fast are the replacement engines?", f"{rows[0]['cases']:,} unseen tasks. 1× is Python re; farther right is faster. Lines show the measured 95% range.")
    grid(body, left, right, 100, height - 24, -2, 1, ((.01, ".01×"), (.03, ".03×"), (.1, ".1×"), (.3, ".3×"), (1, "1× Python re"), (3, "3×"), (10, "10×")))
    for index, row in enumerate(rows):
        y = 132 + index * 64
        color = COLORS[row["candidate"]]
        low = xlog(row["ci95_low"], left, right - left, -2, 1)
        point = xlog(row["geomean_speedup"], left, right - left, -2, 1)
        high = xlog(row["ci95_high"], left, right - left, -2, 1)
        body.extend((
            f'<text x="24" y="{y+5}" class="head">{escape(NAMES[row["candidate"]])}</text>',
            f'<line x1="{low:.1f}" y1="{y}" x2="{high:.1f}" y2="{y}" stroke="{color}" stroke-width="7" stroke-linecap="round"/>',
            f'<circle cx="{point:.1f}" cy="{y}" r="6" fill="{color}" stroke="#fff" stroke-width="1.5"/>',
            f'<text x="845" y="{y-4}" class="head">{fmt(row["geomean_speedup"])} as fast overall</text>',
            f'<text x="845" y="{y+16}" class="small">{row["statistically_faster_cases"]:,}/{row["cases"]:,} clearly faster · {row["regressions_gt_20pct"]:,} large slowdowns</text>',
        ))
    save(output, body)


def groups(summary, new_only=True):
    values = defaultdict(list)
    for row in summary["case_results"]:
        if row["cohort"] != "holdout":
            continue
        category = row["category"]
        if new_only and not category.startswith("deeper-"):
            continue
        if not new_only and not category.startswith("deeper-"):
            category = "Earlier workloads"
        values[(category, row["candidate"])].append(row)
    categories = sorted({key[0] for key in values}, key=lambda value: (value != "Earlier workloads", value))
    candidates = [row["candidate"] for row in ordered(summary)]
    return values, categories, candidates


def family_speed(summary, output):
    values, categories, candidates = groups(summary)
    row_height, panel_gap = 24, 66
    panel = len(categories) * row_height + panel_gap
    width, height, left, right = 1280, 82 + len(candidates) * panel + 24, 260, 945
    body = page(width, height, "Speed across the 48 new kinds of task", "Each row combines 64 unseen variations. 1× is Python re; farther right is faster. The line combines each task's measured range.")
    for panel_index, candidate in enumerate(candidates):
        top = 100 + panel_index * panel
        bottom = top + 18 + len(categories) * row_height
        color = COLORS[candidate]
        body.extend((f'<rect x="16" y="{top-27}" width="1248" height="{panel-8}" rx="8" fill="#f8fafc" stroke="#e2e8f0"/>', f'<text x="28" y="{top-7}" class="head">{escape(NAMES[candidate])}</text>'))
        grid(body, left, right, top + 8, bottom, -3, 2, ((.001, ".001×"), (.01, ".01×"), (.1, ".1×"), (1, "1×"), (10, "10×"), (100, "100×")))
        for index, category in enumerate(categories):
            rows = values[(category, candidate)]
            point = geometric(row["speedup"] for row in rows)
            low = geometric(row["ci95_low"] for row in rows)
            high = geometric(row["ci95_high"] for row in rows)
            wins = sum(row["statistically_faster"] for row in rows)
            losses = sum(row["regression_gt_20pct"] for row in rows)
            y = top + 24 + index * row_height
            body.extend((
                f'<text x="28" y="{y+4}" class="label">{escape(label(category))}</text>',
                f'<line x1="{xlog(low,left,right-left,-3,2):.1f}" y1="{y}" x2="{xlog(high,left,right-left,-3,2):.1f}" y2="{y}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>',
                f'<circle cx="{xlog(point,left,right-left,-3,2):.1f}" cy="{y}" r="3.5" fill="{color}"/>',
                f'<text x="966" y="{y+4}" class="value">{fmt(point)}</text>',
                f'<text x="1040" y="{y+4}" class="small">{wins}/{len(rows)} faster · {losses} slow</text>',
            ))
    save(output, body)


def zig_speed(summary, output):
    values, categories, _ = groups(summary, new_only=False)
    candidate = "candidates.zig_candidate"
    row_height = 25
    width, height, left, right = 1220, 118 + len(categories) * row_height, 266, 878
    body = page(width, height, "Where Zig / rebar is fast and slow", "The first row combines all earlier tasks; every other row is one of the 48 new workload types. 1× is Python re; farther right is faster.")
    grid(body, left, right, 100, height - 14, -1, 2, ((.1, ".1×"), (.3, ".3×"), (1, "1× Python re"), (3, "3×"), (10, "10×"), (30, "30×"), (100, "100×")))
    for index, category in enumerate(categories):
        rows = values[(category, candidate)]
        point = geometric(row["speedup"] for row in rows)
        low = geometric(row["ci95_low"] for row in rows)
        high = geometric(row["ci95_high"] for row in rows)
        losses = sum(row["regression_gt_20pct"] for row in rows)
        color = "#dc2626" if losses else "#059669"
        y = 122 + index * row_height
        body.extend((
            f'<text x="24" y="{y+4}" class="label">{escape(label(category))}</text>',
            f'<line x1="{xlog(low,left,right-left,-1,2):.1f}" y1="{y}" x2="{xlog(high,left,right-left,-1,2):.1f}" y2="{y}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>',
            f'<circle cx="{xlog(point,left,right-left,-1,2):.1f}" cy="{y}" r="3.5" fill="{color}"/>',
            f'<text x="900" y="{y+4}" class="value">{fmt(point)}</text>',
            f'<text x="978" y="{y+4}" class="small">{sum(row["statistically_faster"] for row in rows)}/{len(rows)} faster · {losses} slow</text>',
        ))
    save(output, body)


def memory(summary, output):
    values, categories, candidates = groups(summary)
    row_height, panel_gap = 24, 66
    panel = len(categories) * row_height + panel_gap
    width, height, left, right = 1240, 82 + len(candidates) * panel + 24, 260, 944
    body = page(width, height, "Temporary Python memory across the 48 new kinds of task", "Each row combines 64 unseen variations. 1× is Python re; farther left uses less traced Python memory. Native allocations are reported separately in the raw data.")
    for panel_index, candidate in enumerate(candidates):
        top = 100 + panel_index * panel
        bottom = top + 18 + len(categories) * row_height
        color = COLORS[candidate]
        body.extend((f'<rect x="16" y="{top-27}" width="1208" height="{panel-8}" rx="8" fill="#f8fafc" stroke="#e2e8f0"/>', f'<text x="28" y="{top-7}" class="head">{escape(NAMES[candidate])}</text>'))
        grid(body, left, right, top + 8, bottom, -2, 4, ((.01, ".01×"), (.1, ".1×"), (1, "1× Python re"), (10, "10×"), (100, "100×"), (1000, "1,000×"), (10000, "10,000×")))
        for index, category in enumerate(categories):
            rows = values[(category, candidate)]
            ratio = geometric(max(row["peak_traced_ratio"], 1e-12) for row in rows)
            y = top + 24 + index * row_height
            body.extend((f'<text x="28" y="{y+4}" class="label">{escape(label(category))}</text>', f'<circle cx="{xlog(ratio,left,right-left,-2,4):.1f}" cy="{y}" r="3.5" fill="{color}"/>', f'<text x="970" y="{y+4}" class="value">{fmt(ratio)}</text>'))
    save(output, body)


def win_loss(summary, output):
    values, categories, candidates = groups(summary, new_only=False)
    row_height, cell = 25, 244
    width, height, left = 1260, 116 + len(categories) * row_height, 268
    body = page(width, height, "Which workloads are faster, and where are the large slowdowns?", "Every holdout task is counted. Green means a majority is clearly faster; red means at least one task is more than 20% slower.")
    for index, candidate in enumerate(candidates):
        body.append(f'<text x="{left+index*cell+8}" y="95" class="head">{escape(NAMES[candidate])}</text>')
    for row_index, category in enumerate(categories):
        y = 105 + row_index * row_height
        body.append(f'<text x="24" y="{y+16}" class="label">{escape(label(category))}</text>')
        for candidate_index, candidate in enumerate(candidates):
            rows = values[(category, candidate)]
            wins = sum(row["statistically_faster"] for row in rows)
            losses = sum(row["regression_gt_20pct"] for row in rows)
            fill = "#b91c1c" if losses else "#15803d" if wins > len(rows) / 2 else "#64748b"
            x = left + candidate_index * cell
            body.extend((f'<rect x="{x}" y="{y}" width="{cell-7}" height="21" rx="4" fill="{fill}"/>', f'<text x="{x+7}" y="{y+14}" class="value" style="fill:#fff">{fmt(geometric(row["speedup"] for row in rows))} · {wins}/{len(rows)} faster · {losses} slow</text>'))
    save(output, body)


def rankings(summary, output):
    candidates = [row["candidate"] for row in ordered(summary)]
    cohorts = (("calibration", "Practice tasks"), ("holdout", "Holdout tasks"), ("all", "All tasks"))
    by = {(row["cohort"], row["candidate"]): row for row in summary["rankings"]}
    width, height, left, right = 1220, 145 + len(candidates) * len(cohorts) * 54, 268, 812
    body = page(width, height, "Overall results across all test sets", "1× is Python re; farther right is faster. Each row shows overall speed, measured 95% range, clearly faster tasks, and large slowdowns.")
    grid(body, left, right, 100, height - 18, -2, 1, ((.01, ".01×"), (.03, ".03×"), (.1, ".1×"), (.3, ".3×"), (1, "1× Python re"), (3, "3×"), (10, "10×")))
    index = 0
    for cohort, cohort_label in cohorts:
        for candidate in candidates:
            row = by[(cohort, candidate)]
            y = 129 + index * 54
            index += 1
            color = COLORS[candidate]
            body.extend((
                f'<text x="24" y="{y-4}" class="small">{cohort_label}</text>',
                f'<text x="24" y="{y+14}" class="value">{escape(NAMES[candidate])}</text>',
                f'<line x1="{xlog(row["ci95_low"],left,right-left,-2,1):.1f}" y1="{y+2}" x2="{xlog(row["ci95_high"],left,right-left,-2,1):.1f}" y2="{y+2}" stroke="{color}" stroke-width="6" stroke-linecap="round"/>',
                f'<circle cx="{xlog(row["geomean_speedup"],left,right-left,-2,1):.1f}" cy="{y+2}" r="5" fill="{color}"/>',
                f'<text x="842" y="{y}" class="head">{fmt(row["geomean_speedup"])} overall</text>',
                f'<text x="842" y="{y+17}" class="small">{row["statistically_faster_cases"]:,}/{row["cases"]:,} clearly faster · {row["regressions_gt_20pct"]:,} large slowdowns</text>',
            ))
    save(output, body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    overall(summary, args.prefix + "-overall.svg")
    zig_speed(summary, args.prefix + "-zig-speed.svg")
    family_speed(summary, args.prefix + "-family-speed.svg")
    memory(summary, args.prefix + "-memory.svg")
    win_loss(summary, args.prefix + "-win-loss.svg")
    rankings(summary, args.prefix + "-rankings.svg")


if __name__ == "__main__":
    main()
