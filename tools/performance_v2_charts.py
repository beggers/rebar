#!/usr/bin/env python3
"""Generate readable, baseline-relative performance charts from a frozen summary."""

import argparse
import html
import json
import math
from pathlib import Path

COLORS = {"candidates.ast_candidate": "#7c3aed", "candidates.vm_candidate": "#0284c7", "candidates.rust_candidate": "#d97706", "rebar": "#15803d"}
NAMES = {"candidates.ast_candidate": "Python engine", "candidates.vm_candidate": "Native C engine", "candidates.rust_candidate": "Rust engine", "rebar": "rebar"}
LABELS = {
    "search.literal.hit": "Find a word (present)", "search.literal.miss": "Find a word (absent)", "search.long-boundary": "Find the ending in long text", "search.class-anchor": "Find a formatted line", "match.prefix": "Check a formatted prefix", "fullmatch.structured": "Check the whole string", "search.look-capture": "Find and capture nearby text", "findall.tokens": "Find all text tokens", "finditer.groups": "Iterate over captured pairs", "split.capture": "Split and keep separators", "sub.template": "Reorder captured text", "subn.callable": "Replace using a Python function", "bytes.tokens": "Find tokens in bytes", "unicode.words": "Find Unicode words or numbers", "cold.compile-search": "Compile and search from cold", "module.warm": "Search through the module API", "empty.finditer": "Find empty-position matches", "backref.fullmatch": "Check repeated captured text", "conditional.match": "Check an optional wrapper", "atomic.search": "Search with controlled branches", "byteslike.findall": "Find in a byte array or view", "unicode-name.search": "Find a named Unicode character", "ignorecase.findall": "Find text ignoring case", "many.split": "Split many small pieces", "escape.text": "Escape special text characters", "escape.bytes": "Escape special byte characters", "compile.only": "Compile a new pattern", "scanner.search": "Scan repeated matches", "match.surface": "Read groups and expand a match",
    "real.log": "Read request lines from a log", "real.url": "Find a web or file address", "real.email": "Find email-like addresses", "real.datetime": "Find dates and times", "real.version": "Check a version string", "real.uuid": "Find a request identifier", "real.ip": "Find network-like addresses", "real.path": "Find file paths", "real.config": "Read configuration lines", "real.comments": "Find line comments", "real.whitespace": "Clean up extra whitespace", "real.lines": "Clean up blank lines", "real.markup": "Find simple markup tags", "real.quotes": "Find quoted values", "real.csv": "Split comma-separated fields",
    "branch.prefix": "Check one of many prefixes", "branch.miss": "Search for one of many words (absent)", "repeat.nested": "Check a structured repeated path", "lines.records": "Read repeated line records", "block.dotall": "Find a multi-line block", "pattern.verbose": "Find a readable formatted field", "mode.ascii": "Find ASCII-only words", "mode.casefold": "Find text ignoring Unicode case", "mode.astral": "Find extended Unicode characters", "look.negative-ahead": "Skip excluded word prefixes", "look.negative-behind": "Find unescaped tagged words",
    "bytes.replace": "Replace repeated byte values", "bytes.scan": "Scan repeated byte pairs", "compile.complex": "Compile a complex pattern", "module.replace": "Replace through the module API", "zero.boundary": "Find word and separator positions", "dense.iter": "Iterate over many small matches", "capture.optional": "Find optional captured fields", "split.limited": "Split a few mixed separators", "replace.limited": "Replace a few captured fields", "bytes.view-long": "Find values in a long byte view", "window.search": "Search inside part of a string", "window.findall": "Find all values in a text window", "window.scanner": "Scan values in a text window", "window.match": "Check a prefix in a text window", "literal.replace": "Replace literal text", "template.repeat": "Reorder repeated captured fields", "match.miss": "Quickly reject a short prefix", "fullmatch.miss": "Quickly reject a whole string",
}


def esc(value):
    return html.escape(str(value), quote=True)


def candidate_name(value):
    return NAMES.get(value, value.rsplit(".", 1)[-1].replace("_candidate", "").replace("_", " ").title())


def case_name(value):
    key = value.split(".", 1)[1] if "." in value else value
    return LABELS.get(key, key.replace(".", " ").replace("-", " ").title())


def ratio(value):
    if value >= 10:
        return f"{value:.1f}×"
    if value >= 0.1:
        return f"{value:.2f}×"
    if value >= 0.01:
        return f"{value:.3f}×"
    return f"{value:.4f}×"


def head(width, height, title, subtitle):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">', '<rect width="100%" height="100%" fill="#f8fafc"/>', f'<text x="28" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#0f172a">{esc(title)}</text>', f'<text x="28" y="59" font-family="Arial, sans-serif" font-size="13" fill="#475569">{esc(subtitle)}</text>']


def save(path, body):
    Path(path).write_text("\n".join([*body, "</svg>\n"]), encoding="utf-8")
    print(f"wrote {path}")


def position(value, left, width):
    return left + round(width * (max(-4, min(2, math.log10(max(value, 1e-12)))) + 4) / 6)


def overall(data, path):
    rows = sorted((row for row in data["rankings"] if row["cohort"] == "holdout"), key=lambda row: row["geomean_speedup"], reverse=True)
    width, left, plot, row_height = 1240, 270, 520, 82
    height = 124 + len(rows) * row_height
    body = head(width, height, "At a glance: speed compared with Python re", "New holdout tasks. 1× is the built-in re module; higher is faster. The line shows the measured range.")
    top, bottom = 91, height - 24
    for exponent, label in ((-4, "0.0001×"), (-3, "0.001×"), (-2, "0.01×"), (-1, "0.1×"), (0, "1× Python re"), (1, "10×"), (2, "100×")):
        x = left + round(plot * (exponent + 4) / 6)
        body.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" stroke="{"#334155" if exponent == 0 else "#cbd5e1"}" stroke-width="{2 if exponent == 0 else 1}"/>')
        body.append(f'<text x="{x}" y="{top-8}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="{700 if exponent == 0 else 400}" fill="{"#0f172a" if exponent == 0 else "#64748b"}">{label}</text>')
    for index, row in enumerate(rows):
        y = 125 + index * row_height
        color = COLORS.get(row["candidate"], "#475569")
        low, mid, high = (position(row[key], left, plot) for key in ("ci95_low", "geomean_speedup", "ci95_high"))
        body.extend([f'<text x="28" y="{y+4}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#0f172a">{esc(candidate_name(row["candidate"]))}</text>', f'<line x1="{low}" y1="{y}" x2="{high}" y2="{y}" stroke="{color}" stroke-width="6" stroke-linecap="round"/>', f'<circle cx="{mid}" cy="{y}" r="7" fill="{color}" stroke="#fff" stroke-width="1.5"/>', f'<text x="820" y="{y-5}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#0f172a">{ratio(row["geomean_speedup"])} as fast overall</text>', f'<text x="820" y="{y+16}" font-family="Arial, sans-serif" font-size="12" fill="#475569">{row["statistically_faster_cases"]}/{row["cases"]} clearly faster · {row["regressions_gt_20pct"]}/{row["cases"]} large slowdowns · range {ratio(row["ci95_low"])}–{ratio(row["ci95_high"])}</text>'])
    save(path, body)


def candidates_for(rows):
    return sorted({row["candidate"] for row in rows}, key=lambda value: (-sum(row.get("statistically_faster", False) for row in rows if row["candidate"] == value), candidate_name(value)))


def cell_color(row, memory=False):
    if memory:
        value = row["peak_traced_ratio"]
        return ("#dcfce7", "#166534") if value <= 1 else (("#fee2e2", "#991b1b") if value > 2 else ("#f1f5f9", "#334155"))
    if row["regression_gt_20pct"]:
        return "#fee2e2", "#991b1b"
    if row["statistically_faster"]:
        return "#dcfce7", "#166534"
    return "#f1f5f9", "#334155"


def matrix(data, path, *, memory=False):
    rows = [row for row in data["case_results"] if row["cohort"] == "holdout"]
    cases = sorted({row["case"] for row in rows})
    candidates = candidates_for(rows)
    lookup = {(row["case"], row["candidate"]): row for row in rows}
    label_width, cell, row_height = 296, 304, 30
    width, height = label_width + cell * len(candidates) + 38, 129 + row_height * len(cases)
    title = "Memory used on each holdout task" if memory else "Speed on each holdout task"
    subtitle = "Compared with Python re. Green uses no more traced Python memory; red uses over twice as much." if memory else "Compared with Python re. Green is clearly faster, red is more than 20% slower, and each cell includes the measured range."
    body = head(width, height, title, subtitle)
    for index, candidate in enumerate(candidates):
        x = label_width + cell * index
        body.append(f'<text x="{x+10}" y="96" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="{COLORS.get(candidate, "#475569")}">{esc(candidate_name(candidate))}</text>')
    for index, case in enumerate(cases):
        y = 106 + row_height * index
        if index % 2 == 0:
            body.append(f'<rect x="18" y="{y}" width="{width-36}" height="{row_height}" fill="#fff"/>')
        body.append(f'<text x="28" y="{y+20}" font-family="Arial, sans-serif" font-size="12" fill="#334155">{esc(case_name(case))}</text>')
        for offset, candidate in enumerate(candidates):
            row = lookup[(case, candidate)]
            fill, ink = cell_color(row, memory)
            x = label_width + cell * offset
            text = ratio(row["peak_traced_ratio"]) if memory else f'{ratio(row["speedup"])} · {ratio(row["ci95_low"])}–{ratio(row["ci95_high"])}'
            detail = f'{candidate_name(candidate)} / {case_name(case)}: {text}'
            body.extend([f'<rect x="{x}" y="{y+3}" width="{cell-9}" height="{row_height-6}" rx="4" fill="{fill}"><title>{esc(detail)}</title></rect>', f'<text x="{x+9}" y="{y+19}" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="{ink}">{esc(text)}</text>'])
    save(path, body)


def regressions(data, path):
    rows = data["case_results"]
    candidates = candidates_for(rows)
    lookup = {(row["case"], row["candidate"]): row for row in rows}
    groups = [("Practice tasks", sorted({row["case"] for row in rows if row["cohort"] == "calibration"})), ("Holdout tasks", sorted({row["case"] for row in rows if row["cohort"] == "holdout"}))]
    label_width, cell, row_height = 298, 182, 25
    width = label_width + cell * len(candidates) + 36
    height = 146 + sum(len(cases) * row_height + 32 for _, cases in groups)
    body = head(width, height, "Where each engine is faster or slower", "Every task is shown. Green is clearly faster; red is more than 20% slower; grey is close or uncertain.")
    for index, candidate in enumerate(candidates):
        body.append(f'<text x="{label_width+cell*index+7}" y="95" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="{COLORS.get(candidate, "#475569")}">{esc(candidate_name(candidate))}</text>')
    y = 109
    for heading, cases in groups:
        body.append(f'<text x="28" y="{y+15}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#0f172a">{heading}</text>')
        y += 24
        for index, case in enumerate(cases):
            row_y = y + index * row_height
            body.append(f'<text x="28" y="{row_y+17}" font-family="Arial, sans-serif" font-size="11" fill="#334155">{esc(case_name(case))}</text>')
            for offset, candidate in enumerate(candidates):
                row = lookup[(case, candidate)]
                fill = "#b91c1c" if row["regression_gt_20pct"] else ("#15803d" if row["statistically_faster"] else "#64748b")
                x = label_width + cell * offset
                body.extend([f'<rect x="{x}" y="{row_y+1}" width="{cell-7}" height="20" rx="4" fill="{fill}"/>', f'<text x="{x+8}" y="{row_y+15}" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#fff">{ratio(row["speedup"])}</text>'])
        y += len(cases) * row_height + 8
    save(path, body)


def rankings(data, path):
    groups = [("Practice tasks", "calibration"), ("Holdout tasks", "holdout"), ("All tasks", "all")]
    rows = data["rankings"]
    candidates = sorted({row["candidate"] for row in rows}, key=lambda value: (-next(row["geomean_speedup"] for row in rows if row["candidate"] == value and row["cohort"] == "holdout"), candidate_name(value)))
    lookup = {(row["cohort"], row["candidate"]): row for row in rows}
    width, label_width, cell, row_height = 1236, 220, 328, 70
    height = 122 + len(groups) * row_height
    body = head(width, height, "Overall results across all task sets", "1× is Python re. Each card shows overall speed, the measured range, clearly faster tasks, and large slowdowns.")
    for index, candidate in enumerate(candidates):
        body.append(f'<text x="{label_width+cell*index+10}" y="96" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="{COLORS.get(candidate, "#475569")}">{esc(candidate_name(candidate))}</text>')
    for index, (heading, cohort) in enumerate(groups):
        y = 106 + index * row_height
        body.append(f'<text x="28" y="{y+28}" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#0f172a">{heading}</text>')
        for offset, candidate in enumerate(candidates):
            row = lookup[(cohort, candidate)]
            x = label_width + cell * offset
            fill = "#dcfce7" if row["ci95_low"] > 1 else ("#fee2e2" if row["geomean_speedup"] < 0.8 else "#f1f5f9")
            body.extend([f'<rect x="{x}" y="{y}" width="{cell-10}" height="58" rx="6" fill="{fill}"/>', f'<text x="{x+10}" y="{y+22}" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#0f172a">{ratio(row["geomean_speedup"])} overall · {ratio(row["ci95_low"])}–{ratio(row["ci95_high"])}</text>', f'<text x="{x+10}" y="{y+42}" font-family="Arial, sans-serif" font-size="11" fill="#475569">{row["statistically_faster_cases"]}/{row["cases"]} clearly faster · {row["regressions_gt_20pct"]} large slowdowns</text>'])
    save(path, body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    overall(data, args.prefix + "-overall.svg")
    matrix(data, args.prefix + "-speed.svg")
    matrix(data, args.prefix + "-memory.svg", memory=True)
    regressions(data, args.prefix + "-regressions.svg")
    rankings(data, args.prefix + "-rankings.svg")


if __name__ == "__main__":
    main()
