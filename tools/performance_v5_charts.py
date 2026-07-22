#!/usr/bin/env python3
"""Generate readable headline and all-case charts for the expanded performance holdout."""

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape


NAMES = {"candidates.ast_candidate": "Python engine", "candidates.vm_candidate": "Native C engine", "candidates.rust_candidate": "Rust engine", "candidates.zig_candidate": "Zig engine", "rebar": "rebar"}
COLORS = {"candidates.ast_candidate": "#7c3aed", "candidates.vm_candidate": "#0284c7", "candidates.rust_candidate": "#d97706", "candidates.zig_candidate": "#0f766e", "rebar": "#15803d"}


def name(value):
    return NAMES.get(value, value.rsplit(".", 1)[-1].replace("_candidate", ""))


def family(value):
    if value.startswith("expanded-"):
        return "new:" + value.removeprefix("expanded-")
    if value.startswith("large-"):
        return "v4:" + value.removeprefix("large-")
    return "earlier-72"


def family_name(value):
    if value == "earlier-72":
        return "Earlier 72 holdout tasks"
    if value.startswith("new:"):
        return "New · " + value.removeprefix("new:").replace("-", " ").title()
    return "V4 · " + value.removeprefix("v4:").replace("-", " ").title()


def fmt(value):
    if value >= 10:
        return f"{value:.1f}×"
    if value >= 0.1:
        return f"{value:.2f}×"
    if value >= 0.01:
        return f"{value:.3f}×"
    return f"{value:.4f}×"


def page(width, height, title, subtitle):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">', '<rect width="100%" height="100%" fill="#f8fafc"/>', '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:13px;fill:#526076}.head{font-size:15px;font-weight:700}.label{font-size:12px}.small{font-size:11px;fill:#526076}.value{font-size:12px;font-weight:700}</style>', f'<text x="28" y="38" class="title">{escape(title)}</text>', f'<text x="28" y="61" class="sub">{escape(subtitle)}</text>']


def save(path, body):
    Path(path).write_text("".join([*body, "</svg>\n"]), encoding="utf-8")
    print(f"wrote {path}")


def xlog(value, left, width, low, high):
    position = max(low, min(high, math.log10(max(value, 1e-12))))
    return left + round((position - low) * width / (high - low))


def ylog(value, top, height, low, high):
    position = max(low, min(high, math.log10(max(value, 1e-12))))
    return top + height - round((position - low) * height / (high - low))


def grid_x(body, left, top, bottom, width, low, high, labels):
    for exponent, label in labels:
        x = left + round((exponent - low) * width / (high - low))
        color = "#334155" if exponent == 0 else "#cbd5e1"
        stroke = 2 if exponent == 0 else 1
        body.extend((f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" stroke="{color}" stroke-width="{stroke}"/>', f'<text x="{x}" y="{top-8}" class="small" text-anchor="middle">{label}</text>'))


def grid_y(body, left, right, top, height, low, high, labels):
    for exponent, label in labels:
        y = top + height - round((exponent - low) * height / (high - low))
        color = "#334155" if exponent == 0 else "#cbd5e1"
        stroke = 2 if exponent == 0 else 1
        body.extend((f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" stroke="{color}" stroke-width="{stroke}"/>', f'<text x="{left-8}" y="{y+4}" class="small" text-anchor="end">{label}</text>'))


def holdout_rows(summary):
    return [row for row in summary["case_results"] if row["cohort"] == "holdout"]


def ordered_candidates(summary):
    ranking = [row for row in summary["rankings"] if row["cohort"] == "holdout"]
    return [row["candidate"] for row in sorted(ranking, key=lambda row: row["geomean_speedup"], reverse=True)]


def ordered_cases(summary):
    rows = holdout_rows(summary)
    values = {}
    for row in rows:
        values[row["case"]] = family(row["category"])
    return sorted(values, key=lambda value: (0 if values[value] == "earlier-72" else 1 if values[value].startswith("v4:") else 2, values[value], value)), values


def overall(summary, path):
    rows = sorted((row for row in summary["rankings"] if row["cohort"] == "holdout"), key=lambda row: row["geomean_speedup"], reverse=True)
    width, left, plot, row_height = 1140, 270, 560, 66
    height = 144 + len(rows) * row_height
    cases = rows[0]["cases"] if rows else 0
    body = page(width, height, "Overall speed compared with Python re", f"{cases:,} holdout tasks. 1× is the built-in re module; farther right is faster. Lines show the measured 95% range.")
    grid_x(body, left, 104, height - 24, plot, -4, 2, [(-4, "0.0001×"), (-3, "0.001×"), (-2, "0.01×"), (-1, "0.1×"), (0, "1× baseline"), (1, "10×"), (2, "100×")])
    for index, row in enumerate(rows):
        y = 134 + index * row_height
        color = COLORS.get(row["candidate"], "#475569")
        first = xlog(row["ci95_low"], left, plot, -4, 2)
        point = xlog(row["geomean_speedup"], left, plot, -4, 2)
        last = xlog(row["ci95_high"], left, plot, -4, 2)
        body.extend((f'<text x="28" y="{y+5}" class="head">{escape(name(row["candidate"]))}</text>', f'<line x1="{first}" y1="{y}" x2="{last}" y2="{y}" stroke="{color}" stroke-width="6" stroke-linecap="round"/>', f'<circle cx="{point}" cy="{y}" r="6" fill="{color}" stroke="#fff" stroke-width="1.5"/>', f'<text x="856" y="{y-4}" class="head">{fmt(row["geomean_speedup"])} as fast overall</text>', f'<text x="856" y="{y+16}" class="small">{row["statistically_faster_cases"]:,}/{row["cases"]:,} clearly faster · {row["regressions_gt_20pct"]:,}/{row["cases"]:,} large slowdowns</text>'))
    save(path, body)


def grouped(summary):
    groups = defaultdict(list)
    for row in holdout_rows(summary):
        groups[(family(row["category"]), row["candidate"])].append(row)
    families = sorted({key[0] for key in groups}, key=lambda value: (0 if value == "earlier-72" else 1 if value.startswith("v4:") else 2, value))
    return groups, families


def family_speed(summary, path):
    groups, families = grouped(summary)
    candidates = ordered_candidates(summary)
    row_height = 27
    panel = 66 + len(families) * row_height
    height = 104 + len(candidates) * panel
    width, left, plot = 1140, 292, 660
    body = page(width, height, "Speed by kind of holdout task", "Each row combines every variation in a workload family. 1× is Python re; farther right is faster. Lines combine the per-task measured ranges.")
    for panel_index, candidate in enumerate(candidates):
        top = 111 + panel_index * panel
        bottom = top + 24 + len(families) * row_height
        color = COLORS.get(candidate, "#475569")
        body.extend((f'<rect x="18" y="{top-25}" width="1104" height="{panel-8}" rx="8" fill="#fff" stroke="#e2e8f0"/>', f'<text x="28" y="{top-4}" class="head" fill="{color}">{escape(name(candidate))}</text>'))
        grid_x(body, left, top + 10, bottom, plot, -4, 2, [(-4, "0.0001×"), (-3, "0.001×"), (-2, "0.01×"), (-1, "0.1×"), (0, "1×"), (1, "10×"), (2, "100×")])
        for index, item in enumerate(families):
            rows = groups[(item, candidate)]
            point = math.exp(statistics_fmean(math.log(row["speedup"]) for row in rows))
            first = math.exp(statistics_fmean(math.log(row["ci95_low"]) for row in rows))
            last = math.exp(statistics_fmean(math.log(row["ci95_high"]) for row in rows))
            y = top + 29 + index * row_height
            faster = sum(row["statistically_faster"] for row in rows)
            losses = sum(row["regression_gt_20pct"] for row in rows)
            body.extend((f'<text x="30" y="{y+4}" class="label">{escape(family_name(item))}</text>', f'<line x1="{xlog(first,left,plot,-4,2)}" y1="{y}" x2="{xlog(last,left,plot,-4,2)}" y2="{y}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>', f'<circle cx="{xlog(point,left,plot,-4,2)}" cy="{y}" r="4" fill="{color}"/>', f'<text x="966" y="{y+4}" class="value">{fmt(point)}</text>', f'<text x="1026" y="{y+4}" class="small">{faster}/{len(rows)} win · {losses} loss</text>'))
    save(path, body)


def statistics_fmean(values):
    values = list(values)
    return sum(values) / len(values)


def cloud(summary, path, *, memory):
    rows = holdout_rows(summary)
    cases, case_family = ordered_cases(summary)
    candidates = ordered_candidates(summary)
    by = {(row["case"], row["candidate"]): row for row in rows}
    width, left, plot, panel_height = 1260, 82, 1148, 226
    panel_gap = 60
    height = 102 + len(candidates) * (panel_height + panel_gap) + 36
    title = "Memory on every holdout task" if memory else "Speed and confidence on every holdout task"
    subtitle = "Every dot is one task. Lower uses less traced Python memory; the dark line is Python re." if memory else "Every dot is one task and every vertical line is its measured 95% range. Above the dark 1× line is faster."
    body = page(width, height, title, subtitle)
    low, high = (-2, 5) if memory else (-4, 2)
    labels = [(-2, "0.01×"), (-1, "0.1×"), (0, "1×"), (1, "10×"), (2, "100×"), (3, "1,000×"), (4, "10,000×"), (5, "100,000×")] if memory else [(-4, "0.0001×"), (-3, "0.001×"), (-2, "0.01×"), (-1, "0.1×"), (0, "1×"), (1, "10×"), (2, "100×")]
    boundaries = []
    previous = None
    for index, case in enumerate(cases):
        current = case_family[case]
        if current != previous:
            boundaries.append((index, current))
            previous = current
    for panel_index, candidate in enumerate(candidates):
        top = 104 + panel_index * (panel_height + panel_gap)
        right = left + plot
        color = COLORS.get(candidate, "#475569")
        body.extend((f'<rect x="20" y="{top-24}" width="1222" height="{panel_height+46}" rx="8" fill="#fff" stroke="#e2e8f0"/>', f'<text x="30" y="{top-4}" class="head" fill="{color}">{escape(name(candidate))}</text>'))
        grid_y(body, left, right, top + 8, panel_height - 16, low, high, labels)
        if not memory:
            slow = ylog(0.8, top + 8, panel_height - 16, low, high)
            body.append(f'<line x1="{left}" y1="{slow}" x2="{right}" y2="{slow}" stroke="#dc2626" stroke-dasharray="3 3"/>')
        for index, case in enumerate(cases):
            row = by[(case, candidate)]
            x = left + round(index * (plot - 1) / max(1, len(cases) - 1))
            if memory:
                y = ylog(row["peak_traced_ratio"], top + 8, panel_height - 16, low, high)
                fill = color
            else:
                first = ylog(row["ci95_low"], top + 8, panel_height - 16, low, high)
                last = ylog(row["ci95_high"], top + 8, panel_height - 16, low, high)
                body.append(f'<line x1="{x}" y1="{first}" x2="{x}" y2="{last}" stroke="{color}" stroke-opacity="0.55" stroke-width="0.9"/>')
                y = ylog(row["speedup"], top + 8, panel_height - 16, low, high)
                fill = "#dc2626" if row["regression_gt_20pct"] else "#15803d" if row["statistically_faster"] else color
            body.append(f'<circle cx="{x}" cy="{y}" r="1.45" fill="{fill}"/>')
        for index, item in boundaries:
            x = left + round(index * (plot - 1) / max(1, len(cases) - 1))
            body.append(f'<line x1="{x}" y1="{top+panel_height-7}" x2="{x}" y2="{top+panel_height-1}" stroke="#64748b"/>')
        body.append(f'<text x="{left}" y="{top+panel_height+15}" class="small">Earlier tasks</text>')
        body.append(f'<text x="{right}" y="{top+panel_height+15}" class="small" text-anchor="end">40 new workload families →</text>')
    save(path, body)


def regressions(summary, path):
    groups, families = grouped(summary)
    candidates = ordered_candidates(summary)
    width, left, cell, row_height = 1418, 295, 276, 27
    height = 146 + len(families) * row_height
    body = page(width, height, "Where each engine wins and loses", "All holdout tasks are counted. Green means most are clearly faster; red shows a family with large slowdowns; every count and family remains visible.")
    for index, candidate in enumerate(candidates):
        body.append(f'<text x="{left+index*cell+8}" y="103" class="head" fill="{COLORS.get(candidate,"#475569")}">{escape(name(candidate))}</text>')
    for index, item in enumerate(families):
        y = 114 + index * row_height
        body.append(f'<text x="28" y="{y+17}" class="label">{escape(family_name(item))}</text>')
        for offset, candidate in enumerate(candidates):
            rows = groups[(item, candidate)]
            faster = sum(row["statistically_faster"] for row in rows)
            losses = sum(row["regression_gt_20pct"] for row in rows)
            speed = math.exp(statistics_fmean(math.log(row["speedup"]) for row in rows))
            fill = "#b91c1c" if losses else "#15803d" if faster > len(rows) / 2 else "#64748b"
            x = left + offset * cell
            body.extend((f'<rect x="{x}" y="{y}" width="{cell-8}" height="22" rx="4" fill="{fill}"/>', f'<text x="{x+8}" y="{y+15}" class="value" style="fill:#fff">{fmt(speed)} · {faster}/{len(rows)} win · {losses} loss</text>'))
    save(path, body)


def rankings(summary, path):
    candidates = ordered_candidates(summary)
    cohorts = (("calibration", "Practice tasks"), ("holdout", "Holdout tasks"), ("all", "All tasks"))
    by = {(row["cohort"], row["candidate"]): row for row in summary["rankings"]}
    width, left, plot, row_height = 1140, 266, 558, 56
    height = 150 + len(candidates) * len(cohorts) * row_height
    body = page(width, height, "Overall results across the test sets", "1× is Python re. Each row shows overall speed, the measured 95% range, clearly faster tasks, and large slowdowns.")
    grid_x(body, left, 105, height - 22, plot, -4, 2, [(-4, "0.0001×"), (-3, "0.001×"), (-2, "0.01×"), (-1, "0.1×"), (0, "1× baseline"), (1, "10×"), (2, "100×")])
    index = 0
    for cohort, label in cohorts:
        for candidate in candidates:
            row = by[(cohort, candidate)]
            y = 139 + index * row_height
            index += 1
            color = COLORS.get(candidate, "#475569")
            body.extend((f'<text x="28" y="{y-4}" class="small">{label}</text>', f'<text x="28" y="{y+14}" class="value" fill="{color}">{escape(name(candidate))}</text>', f'<line x1="{xlog(row["ci95_low"],left,plot,-4,2)}" y1="{y+3}" x2="{xlog(row["ci95_high"],left,plot,-4,2)}" y2="{y+3}" stroke="{color}" stroke-width="5" stroke-linecap="round"/>', f'<circle cx="{xlog(row["geomean_speedup"],left,plot,-4,2)}" cy="{y+3}" r="5" fill="{color}"/>', f'<text x="850" y="{y}" class="head">{fmt(row["geomean_speedup"])} overall</text>', f'<text x="850" y="{y+17}" class="small">{row["statistically_faster_cases"]:,}/{row["cases"]:,} clearly faster · {row["regressions_gt_20pct"]:,} large slowdowns</text>'))
    save(path, body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    overall(summary, args.prefix + "-overall.svg")
    family_speed(summary, args.prefix + "-family-speed.svg")
    cloud(summary, args.prefix + "-speed-cloud.svg", memory=False)
    cloud(summary, args.prefix + "-memory-cloud.svg", memory=True)
    regressions(summary, args.prefix + "-regressions.svg")
    rankings(summary, args.prefix + "-rankings.svg")


if __name__ == "__main__":
    main()
