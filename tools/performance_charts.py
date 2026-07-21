#!/usr/bin/env python3
"""Generate reproducible speed, memory, regression, and ranking charts from a summary."""

import argparse
import json
import math
from pathlib import Path

COLORS = {"candidates.ast_candidate": "#7c3aed", "candidates.vm_candidate": "#0284c7", "candidates.rust_candidate": "#d97706", "rebar": "#15803d"}


def label(name):
    return name.rsplit(".", 1)[-1].replace("_candidate", "")


def svg_head(width, height, title, subtitle):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">', '<rect width="100%" height="100%" fill="#fff"/>', f'<text x="24" y="30" font-family="sans-serif" font-size="20" font-weight="700" fill="#172033">{title}</text>', f'<text x="24" y="52" font-family="sans-serif" font-size="12" fill="#42526e">{subtitle}</text>']


def write(path, body):
    Path(path).write_text("\n".join([*body, "</svg>\n"]), encoding="utf-8")
    print(f"wrote {path}")


def speed(summary, path):
    rows = [row for row in summary["case_results"] if row["cohort"] == "holdout"]
    cases = sorted({row["case"] for row in rows})
    candidates = sorted({row["candidate"] for row in rows})
    by = {(row["case"], row["candidate"]): row for row in rows}
    width, left, plot, row_height = 1040, 242, 744, 27
    height = 102 + len(cases) * row_height
    body = svg_head(width, height, "Holdout speed and 95% confidence — all cases", "Paired stdlib / candidate ratios on a log10 axis; right of 1.0 is faster.")
    for exponent in range(-4, 2):
        x = left + round(plot * (exponent + 4) / 5)
        body.append(f'<line x1="{x}" y1="65" x2="{x}" y2="{height-18}" stroke="#cbd5e1"/>')
        body.append(f'<text x="{x}" y="78" text-anchor="middle" font-family="monospace" font-size="10" fill="#64748b">1e{exponent}</text>')
    for index, case in enumerate(cases):
        y = 96 + index * row_height
        body.append(f'<text x="24" y="{y+4}" font-family="monospace" font-size="11" fill="#172033">{case}</text>')
        for offset, candidate in enumerate(candidates):
            row = by[(case, candidate)]
            center = max(-4, min(1, math.log10(row["speedup"])))
            low = max(-4, min(1, math.log10(row["ci95_low"])))
            high = max(-4, min(1, math.log10(row["ci95_high"])))
            cy = y - 6 + offset * 6
            x = left + round(plot * (center + 4) / 5)
            x1 = left + round(plot * (low + 4) / 5)
            x2 = left + round(plot * (high + 4) / 5)
            color = COLORS.get(candidate, "#475569")
            body.append(f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="{color}" stroke-width="2"/>')
            body.append(f'<circle cx="{x}" cy="{cy}" r="2.5" fill="{color}"/>')
    body.append(f'<text x="{left}" y="{height-5}" font-family="sans-serif" font-size="10" fill="#42526e">' + " · ".join(f'{label(name)}: {COLORS.get(name, "#475569")}' for name in candidates) + "</text>")
    write(path, body)


def memory(summary, path):
    rows = [row for row in summary["case_results"] if row["cohort"] == "holdout"]
    cases = sorted({row["case"] for row in rows})
    candidates = sorted({row["candidate"] for row in rows})
    by = {(row["case"], row["candidate"]): row for row in rows}
    width, left, plot, row_height = 1040, 242, 744, 24
    height = 98 + len(cases) * row_height
    body = svg_head(width, height, "Holdout memory — all cases", "Median tracemalloc peak ratio (candidate / stdlib) on a log10 axis; /proc RSS/HWM remains in raw data.")
    for exponent in range(-1, 5):
        x = left + round(plot * (exponent + 1) / 5)
        body.append(f'<line x1="{x}" y1="65" x2="{x}" y2="{height-18}" stroke="#cbd5e1"/>')
        body.append(f'<text x="{x}" y="78" text-anchor="middle" font-family="monospace" font-size="10" fill="#64748b">1e{exponent}</text>')
    for index, case in enumerate(cases):
        y = 94 + index * row_height
        body.append(f'<text x="24" y="{y+4}" font-family="monospace" font-size="11" fill="#172033">{case}</text>')
        for offset, candidate in enumerate(candidates):
            value = max(-1, min(4, math.log10(max(by[(case, candidate)]["peak_traced_ratio"], 1e-9))))
            x = left + round(plot * (value + 1) / 5)
            body.append(f'<circle cx="{x}" cy="{y-5+offset*5}" r="2.7" fill="{COLORS.get(candidate, "#475569")}"/>')
    write(path, body)


def regressions(summary, path):
    rows = summary["case_results"]
    cases = sorted({row["case"] for row in rows})
    candidates = sorted({row["candidate"] for row in rows})
    by = {(row["case"], row["candidate"]): row for row in rows}
    width, left, cell, row_height = 840, 246, 150, 20
    height = 100 + len(cases) * row_height
    body = svg_head(width, height, "Regression map — all cases and candidates", "Red: >20% slower (speedup <0.8); green: statistically faster; grey: neither.")
    for index, candidate in enumerate(candidates):
        body.append(f'<text x="{left+index*cell+4}" y="78" font-family="monospace" font-size="11" fill="#172033">{label(candidate)}</text>')
    for index, case in enumerate(cases):
        y = 88 + index * row_height
        body.append(f'<text x="24" y="{y+12}" font-family="monospace" font-size="10" fill="#172033">{case}</text>')
        for offset, candidate in enumerate(candidates):
            row = by[(case, candidate)]
            fill = "#b91c1c" if row["regression_gt_20pct"] else "#15803d" if row["statistically_faster"] else "#94a3b8"
            body.append(f'<rect x="{left+offset*cell}" y="{y}" width="{cell-5}" height="16" rx="2" fill="{fill}"/>')
            body.append(f'<text x="{left+offset*cell+6}" y="{y+11}" font-family="monospace" font-size="9" fill="#fff">{row["speedup"]:.4g}x</text>')
    write(path, body)


def rankings(summary, path):
    rows = summary["rankings"]
    cohorts = ["calibration", "holdout", "all"]
    candidates = sorted({row["candidate"] for row in rows})
    by = {(row["cohort"], row["candidate"]): row for row in rows}
    width, left, plot, row_height = 950, 170, 700, 32
    height = 105 + len(cohorts) * len(candidates) * row_height
    body = svg_head(width, height, "Candidate rankings and 95% confidence", "Weighted geometric-mean stdlib / candidate ratio; every cohort denominator is shown.")
    for exponent in range(-4, 2):
        x = left + round(plot * (exponent + 4) / 5)
        body.append(f'<line x1="{x}" y1="65" x2="{x}" y2="{height-8}" stroke="#cbd5e1"/>')
        body.append(f'<text x="{x}" y="78" text-anchor="middle" font-family="monospace" font-size="10" fill="#64748b">1e{exponent}</text>')
    line = 0
    for cohort in cohorts:
        for candidate in candidates:
            row = by[(cohort, candidate)]
            y = 98 + line * row_height
            line += 1
            body.append(f'<text x="24" y="{y+4}" font-family="monospace" font-size="10" fill="#172033">{cohort}/{label(candidate)}</text>')
            values = [max(-4, min(1, math.log10(row[key]))) for key in ("ci95_low", "geomean_speedup", "ci95_high")]
            x1, x, x2 = [left + round(plot * (value + 4) / 5) for value in values]
            color = COLORS.get(candidate, "#475569")
            body.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="3"/>')
            body.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
            body.append(f'<text x="{x+8}" y="{y+4}" font-family="monospace" font-size="10" fill="#172033">{row["geomean_speedup"]:.4g}x · {row["statistically_faster_cases"]}/{row["cases"]} faster</text>')
    write(path, body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    speed(summary, args.prefix + "-speed.svg")
    memory(summary, args.prefix + "-memory.svg")
    regressions(summary, args.prefix + "-regressions.svg")
    rankings(summary, args.prefix + "-rankings.svg")


if __name__ == "__main__":
    main()
