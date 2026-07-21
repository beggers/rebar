#!/usr/bin/env python3
"""Draw clear, reproducible benchmark charts from a committed performance summary."""

import argparse
import json
import math
from pathlib import Path


COLORS = {
    "candidates.ast_candidate": "#7c3aed",
    "candidates.vm_candidate": "#0284c7",
    "candidates.rust_candidate": "#d97706",
    "rebar": "#15803d",
}

NAMES = {
    "candidates.ast_candidate": "Python backtracker",
    "candidates.vm_candidate": "Native C engine",
    "candidates.rust_candidate": "Rust engine",
    "rebar": "rebar",
}

CASES = {
    "search.literal.hit": "Find a word (present)",
    "search.literal.miss": "Find a word (absent)",
    "search.long-boundary": "Find the ending in long text",
    "search.class-anchor": "Find a formatted line",
    "match.prefix": "Check a formatted prefix",
    "fullmatch.structured": "Check the whole string",
    "search.look-capture": "Find and capture nearby text",
    "findall.tokens": "Find all text tokens",
    "finditer.groups": "Iterate over captured pairs",
    "split.capture": "Split and keep separators",
    "sub.template": "Reorder captured text",
    "subn.callable": "Replace with a Python function",
    "bytes.tokens": "Find tokens in bytes",
    "unicode.words": "Find Unicode words/numbers",
    "cold.compile-search": "Compile, then search (cold)",
    "module.warm": "Search through the module API",
}


def candidate_name(value):
    return NAMES.get(value, value.rsplit(".", 1)[-1].replace("_candidate", ""))


def case_name(value):
    key = value.split(".", 1)[1] if "." in value else value
    return CASES.get(key, key.replace(".", " ").replace("-", " ").title())


def fmt(value):
    if value >= 10:
        return f"{value:.1f}×"
    if value >= 0.1:
        return f"{value:.2f}×"
    if value >= 0.01:
        return f"{value:.3f}×"
    return f"{value:.4f}×"


def head(width, height, title, subtitle):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        f'<text x="28" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#0f172a">{title}</text>',
        f'<text x="28" y="58" font-family="Arial, sans-serif" font-size="13" fill="#475569">{subtitle}</text>',
    ]


def save(path, body):
    Path(path).write_text("\n".join([*body, "</svg>\n"]), encoding="utf-8")
    print(f"wrote {path}")


def log_position(value, left, plot, minimum, maximum):
    logged = max(minimum, min(maximum, math.log10(max(value, 1e-12))))
    return left + round(plot * (logged - minimum) / (maximum - minimum))


def log_grid(body, left, top, bottom, plot, minimum, maximum, labels):
    for exponent, label in labels:
        x = left + round(plot * (exponent - minimum) / (maximum - minimum))
        baseline = exponent == 0
        body.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" stroke="{"#334155" if baseline else "#cbd5e1"}" stroke-width="{2 if baseline else 1}"/>')
        body.append(f'<text x="{x}" y="{top-8}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="{700 if baseline else 400}" fill="{"#0f172a" if baseline else "#64748b"}">{label}</text>')


def overall(summary, path):
    rows = [row for row in summary["rankings"] if row["cohort"] == "holdout"]
    rows.sort(key=lambda row: row["geomean_speedup"], reverse=True)
    width, left, plot, row_height = 1140, 262, 590, 66
    height = 142 + len(rows) * row_height
    body = head(width, height, "Overall speed compared with Python re", "Holdout results. 1× is the built-in re module; farther right is faster. Lines show the measured 95% range.")
    top, bottom = 98, height - 22
    log_grid(body, left, top, bottom, plot, -4, 2, [(-4, "0.0001×"), (-3, "0.001×"), (-2, "0.01×"), (-1, "0.1×"), (0, "1× baseline"), (1, "10×"), (2, "100×")])
    for index, row in enumerate(rows):
        y = 126 + index * row_height
        color = COLORS.get(row["candidate"], "#475569")
        body.append(f'<text x="28" y="{y+5}" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#0f172a">{candidate_name(row["candidate"])}</text>')
        x1 = log_position(row["ci95_low"], left, plot, -4, 2)
        x = log_position(row["geomean_speedup"], left, plot, -4, 2)
        x2 = log_position(row["ci95_high"], left, plot, -4, 2)
        body.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="5" stroke-linecap="round"/>')
        body.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
        faster = row["statistically_faster_cases"]
        total = row["cases"]
        losses = row["regressions_gt_20pct"]
        body.append(f'<text x="878" y="{y-3}" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#0f172a">{fmt(row["geomean_speedup"])} as fast overall</text>')
        body.append(f'<text x="878" y="{y+16}" font-family="Arial, sans-serif" font-size="12" fill="#475569">{faster}/{total} clearly faster · {losses}/{total} large slowdowns</text>')
    save(path, body)


def speed(summary, path):
    rows = [row for row in summary["case_results"] if row["cohort"] == "holdout"]
    cases = sorted({row["case"] for row in rows})
    candidates = sorted({row["candidate"] for row in rows}, key=lambda value: candidate_name(value))
    by = {(row["case"], row["candidate"]): row for row in rows}
    width, left, plot, row_height = 1140, 280, 700, 25
    panel = 58 + len(cases) * row_height
    height = 95 + len(candidates) * panel
    body = head(width, height, "Speed on every holdout test", "Each dot compares one replacement with Python re. Right of the dark 1× line is faster; bars show the measured 95% range.")
    for panel_index, candidate in enumerate(candidates):
        top = 102 + panel_index * panel
        bottom = top + len(cases) * row_height + 2
        color = COLORS.get(candidate, "#475569")
        body.append(f'<rect x="18" y="{top-25}" width="1104" height="{panel-8}" rx="8" fill="#fff" stroke="#e2e8f0"/>')
        body.append(f'<text x="28" y="{top-6}" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="{color}">{candidate_name(candidate)}</text>')
        log_grid(body, left, top + 10, bottom, plot, -4, 2, [(-4, "0.0001×"), (-3, "0.001×"), (-2, "0.01×"), (-1, "0.1×"), (0, "1×"), (1, "10×"), (2, "100×")])
        for index, case in enumerate(cases):
            row = by[(case, candidate)]
            y = top + 29 + index * row_height
            body.append(f'<text x="30" y="{y+3}" font-family="Arial, sans-serif" font-size="12" fill="#334155">{case_name(case)}</text>')
            x1 = log_position(row["ci95_low"], left, plot, -4, 2)
            x = log_position(row["speedup"], left, plot, -4, 2)
            x2 = log_position(row["ci95_high"], left, plot, -4, 2)
            body.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
            body.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
            body.append(f'<text x="996" y="{y+4}" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#0f172a">{fmt(row["speedup"])}</text>')
    save(path, body)


def memory(summary, path):
    rows = [row for row in summary["case_results"] if row["cohort"] == "holdout"]
    cases = sorted({row["case"] for row in rows})
    candidates = sorted({row["candidate"] for row in rows}, key=lambda value: candidate_name(value))
    by = {(row["case"], row["candidate"]): row for row in rows}
    width, left, plot, row_height = 1140, 280, 700, 25
    panel = 58 + len(cases) * row_height
    height = 95 + len(candidates) * panel
    body = head(width, height, "Extra memory used during each holdout test", "Compared with Python re. Left of the dark 1× line uses less traced Python memory; right uses more.")
    for panel_index, candidate in enumerate(candidates):
        top = 102 + panel_index * panel
        bottom = top + len(cases) * row_height + 2
        color = COLORS.get(candidate, "#475569")
        body.append(f'<rect x="18" y="{top-25}" width="1104" height="{panel-8}" rx="8" fill="#fff" stroke="#e2e8f0"/>')
        body.append(f'<text x="28" y="{top-6}" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="{color}">{candidate_name(candidate)}</text>')
        log_grid(body, left, top + 10, bottom, plot, -2, 5, [(-2, "0.01×"), (-1, "0.1×"), (0, "1×"), (1, "10×"), (2, "100×"), (3, "1,000×"), (4, "10,000×"), (5, "100,000×")])
        for index, case in enumerate(cases):
            row = by[(case, candidate)]
            y = top + 29 + index * row_height
            value = row["peak_traced_ratio"]
            x = log_position(value, left, plot, -2, 5)
            body.append(f'<text x="30" y="{y+3}" font-family="Arial, sans-serif" font-size="12" fill="#334155">{case_name(case)}</text>')
            body.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
            body.append(f'<text x="996" y="{y+4}" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#0f172a">{fmt(value)}</text>')
    save(path, body)


def regressions(summary, path):
    rows = summary["case_results"]
    cases = sorted({row["case"] for row in rows})
    candidates = sorted({row["candidate"] for row in rows}, key=lambda value: candidate_name(value))
    by = {(row["case"], row["candidate"]): row for row in rows}
    width, left, cell, row_height = 1140, 284, 275, 25
    height = 128 + len(cases) * row_height
    body = head(width, height, "Where each replacement wins and loses", "All tests are shown. Green is clearly faster; red is more than 20% slower; grey is close or uncertain.")
    for index, candidate in enumerate(candidates):
        body.append(f'<text x="{left+index*cell+8}" y="100" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="{COLORS.get(candidate, "#475569")}">{candidate_name(candidate)}</text>')
    for index, case in enumerate(cases):
        y = 108 + index * row_height
        cohort = "Practice" if case.startswith("cal.") else "Holdout"
        body.append(f'<text x="28" y="{y+16}" font-family="Arial, sans-serif" font-size="11" fill="#334155">{cohort}: {case_name(case)}</text>')
        for offset, candidate in enumerate(candidates):
            row = by[(case, candidate)]
            fill = "#b91c1c" if row["regression_gt_20pct"] else "#15803d" if row["statistically_faster"] else "#64748b"
            body.append(f'<rect x="{left+offset*cell}" y="{y}" width="{cell-8}" height="20" rx="4" fill="{fill}"/>')
            body.append(f'<text x="{left+offset*cell+9}" y="{y+14}" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#fff">{fmt(row["speedup"])}</text>')
    save(path, body)


def rankings(summary, path):
    cohorts = [("calibration", "Practice tests"), ("holdout", "Holdout tests"), ("all", "All tests")]
    candidates = sorted({row["candidate"] for row in summary["rankings"]}, key=lambda value: candidate_name(value))
    by = {(row["cohort"], row["candidate"]): row for row in summary["rankings"]}
    width, left, plot, row_height = 1140, 260, 590, 54
    height = 146 + len(cohorts) * len(candidates) * row_height
    body = head(width, height, "Overall results across the test sets", "1× is Python re. Each row shows overall speed, the measured 95% range, and how many tests were clearly faster.")
    log_grid(body, left, 104, height - 18, plot, -4, 2, [(-4, "0.0001×"), (-3, "0.001×"), (-2, "0.01×"), (-1, "0.1×"), (0, "1× baseline"), (1, "10×"), (2, "100×")])
    line = 0
    for cohort, cohort_label in cohorts:
        for candidate in candidates:
            row = by[(cohort, candidate)]
            y = 132 + line * row_height
            line += 1
            color = COLORS.get(candidate, "#475569")
            body.append(f'<text x="28" y="{y-3}" font-family="Arial, sans-serif" font-size="12" fill="#475569">{cohort_label}</text>')
            body.append(f'<text x="28" y="{y+15}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="{color}">{candidate_name(candidate)}</text>')
            x1 = log_position(row["ci95_low"], left, plot, -4, 2)
            x = log_position(row["geomean_speedup"], left, plot, -4, 2)
            x2 = log_position(row["ci95_high"], left, plot, -4, 2)
            body.append(f'<line x1="{x1}" y1="{y+3}" x2="{x2}" y2="{y+3}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
            body.append(f'<circle cx="{x}" cy="{y+3}" r="5" fill="{color}"/>')
            body.append(f'<text x="876" y="{y}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#0f172a">{fmt(row["geomean_speedup"])} overall</text>')
            body.append(f'<text x="876" y="{y+17}" font-family="Arial, sans-serif" font-size="11" fill="#475569">{row["statistically_faster_cases"]}/{row["cases"]} clearly faster · {row["regressions_gt_20pct"]} large slowdowns</text>')
    save(path, body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    overall(summary, args.prefix + "-overall.svg")
    speed(summary, args.prefix + "-speed.svg")
    memory(summary, args.prefix + "-memory.svg")
    regressions(summary, args.prefix + "-regressions.svg")
    rankings(summary, args.prefix + "-rankings.svg")


if __name__ == "__main__":
    main()
