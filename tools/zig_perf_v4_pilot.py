#!/usr/bin/env python3
"""Correctness-gated, paired Zig/stdlib timing on the frozen large performance holdout."""

from __future__ import annotations

import argparse
import gc
import importlib
import json
import math
import random
import statistics
import time
import tracemalloc
from html import escape
from pathlib import Path

from tools.perf_v4 import correctness_gate, frozen, operation, proc_memory, snapshot


BASELINE = "re"
CANDIDATE = "candidates.zig_candidate"


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, math.floor(fraction * (len(ordered) - 1))))]


def interval(logs, rng, samples):
    means = [statistics.fmean(logs[rng.randrange(len(logs))] for _ in logs) for _ in range(samples)]
    return math.exp(percentile(means, .025)), math.exp(percentile(means, .975))


def chart(summary, output):
    holdout = next(value for value in summary["rankings"] if value["cohort"] == "holdout")
    families = [value for value in summary["families"] if value["cohort"] == "holdout" and value["category"].startswith("large-")]
    families.sort(key=lambda value: value["speedup"], reverse=True)
    width, top, row = 1180, 164, 25
    height = top + len(families) * row + 38
    center, half = 866, 276
    max_log = max(1, *(abs(math.log2(value["speedup"])) for value in families))
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:14px;fill:#52627a}.head{font-size:11px;font-weight:700;fill:#41506a}.label{font-size:12px}.number{font-size:12px;text-anchor:end;font-variant-numeric:tabular-nums}.strong{font-size:12px;text-anchor:end;font-weight:700}.grid{stroke:#dbe1eb;stroke-width:1}</style>',
        '<text x="24" y="38" class="title">How the Zig experiment compares with Python re</text>',
        f'<text x="24" y="64" class="sub">Overall on {holdout["cases"]:,} unseen tasks: {holdout["speedup"]:.3f}× as fast ({holdout["ci95_low"]:.3f}–{holdout["ci95_high"]:.3f}× measured range) · {holdout["faster_cases"]:,} clearly faster · {holdout["slowdowns_gt_20pct"]:,} large slowdowns</text>',
        '<text x="24" y="87" class="sub">Rows show the 36 balanced task families (1,152 tasks); the other 72 varied tasks are retained in the detailed graphs and raw results. Every timed result was checked.</text>',
        '<text x="24" y="121" class="head">KIND OF TASK</text><text x="610" y="121" class="head" text-anchor="end">TASKS</text><text x="735" y="121" class="head" text-anchor="end">SPEED · 95% RANGE</text><text x="866" y="121" class="head" text-anchor="middle">SLOWER ← 1× → FASTER</text>',
        f'<line x1="{center}" y1="{top-25}" x2="{center}" y2="{height-22}" stroke="#7f8fa7" stroke-width="1.3"/>',
    ]
    for index, value in enumerate(families):
        y = top + index * row
        speed = value["speedup"]
        delta = math.log2(speed) / max_log * half
        color = "#238b64" if value["ci95_low"] > 1 else "#c84c4c" if speed < .8 else "#8995a7"
        if index % 2 == 0:
            lines.append(f'<rect x="16" y="{y-16}" width="{width-32}" height="{row}" fill="#f5f7fb"/>')
        lines.extend((
            f'<line x1="16" y1="{y+9}" x2="{width-16}" y2="{y+9}" class="grid"/>',
            f'<text x="24" y="{y}" class="label">{escape(value["label"])}</text>',
            f'<text x="610" y="{y}" class="number">{value["cases"]:,}</text>',
            f'<text x="735" y="{y}" class="strong" fill="{color}">{speed:.3f}× · {value["ci95_low"]:.3f}–{value["ci95_high"]:.3f}×</text>',
            f'<rect x="{center if delta >= 0 else center + delta:.1f}" y="{y-11}" width="{abs(delta):.1f}" height="12" rx="2.5" fill="{color}"/>',
        ))
    lines.append("</svg>\n")
    Path(output).write_text("".join(lines), encoding="utf-8")


def memory_chart(summary, output):
    families = [value for value in summary["families"] if value["cohort"] == "holdout"]
    families.sort(key=lambda value: value["memory_ratio"])
    width, top, row = 1180, 145, 25
    height = top + len(families) * row + 38
    center, half = 858, 284
    max_log = max(1, *(abs(math.log2(value["memory_ratio"])) for value in families))
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:14px;fill:#52627a}.head{font-size:11px;font-weight:700;fill:#41506a}.label{font-size:12px}.number{font-size:12px;text-anchor:end;font-variant-numeric:tabular-nums}.grid{stroke:#dbe1eb;stroke-width:1}</style>',
        '<text x="24" y="38" class="title">Temporary memory used by the Zig experiment</text>',
        '<text x="24" y="64" class="sub">Each row combines matching holdout tasks. Values compare peak Python-traced memory per call with Python re: less than 1× uses less memory.</text>',
        '<text x="24" y="86" class="sub">This includes result construction and bridge allocations visible to Python; process-wide high-water marks remain in the raw data.</text>',
        '<text x="24" y="120" class="head">KIND OF TASK</text><text x="710" y="120" class="head" text-anchor="end">ZIG / PYTHON re</text><text x="858" y="120" class="head" text-anchor="middle">LESS ← 1× → MORE</text>',
        f'<line x1="{center}" y1="{top-22}" x2="{center}" y2="{height-22}" stroke="#7f8fa7" stroke-width="1.3"/>',
    ]
    for index, value in enumerate(families):
        y = top + index * row
        ratio = value["memory_ratio"]
        delta = math.log2(ratio) / max_log * half
        color = "#238b64" if ratio < .8 else "#c84c4c" if ratio > 1.2 else "#8995a7"
        if index % 2 == 0:
            lines.append(f'<rect x="16" y="{y-16}" width="{width-32}" height="{row}" fill="#f5f7fb"/>')
        lines.extend((
            f'<line x1="16" y1="{y+9}" x2="{width-16}" y2="{y+9}" class="grid"/>',
            f'<text x="24" y="{y}" class="label">{escape(value["label"])}</text>',
            f'<text x="710" y="{y}" class="number" fill="{color}">{ratio:.3f}× · {value["zig_peak_bytes"]:,} B / {value["baseline_peak_bytes"]:,} B</text>',
            f'<rect x="{center if delta >= 0 else center + delta:.1f}" y="{y-11}" width="{abs(delta):.1f}" height="12" rx="2.5" fill="{color}"/>',
        ))
    lines.append("</svg>\n")
    Path(output).write_text("".join(lines), encoding="utf-8")


def regression_chart(summary, output):
    families = [value for value in summary["families"] if value["cohort"] == "holdout"]
    families.sort(key=lambda value: (value["slowdowns_gt_20pct"] / value["cases"], -value["faster_cases"] / value["cases"]), reverse=True)
    width, top, row = 1180, 142, 25
    height = top + len(families) * row + 40
    bar_x, bar_width = 738, 414
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:14px;fill:#52627a}.head{font-size:11px;font-weight:700;fill:#41506a}.label{font-size:12px}.number{font-size:12px;text-anchor:end;font-variant-numeric:tabular-nums}.grid{stroke:#dbe1eb;stroke-width:1}</style>',
        '<text x="24" y="38" class="title">Where the Zig experiment wins and loses</text>',
        '<text x="24" y="64" class="sub">Every unseen holdout task is counted. Green is clearly faster, red is more than 20% slower, and grey is close or uncertain.</text>',
        '<text x="24" y="118" class="head">KIND OF TASK</text><text x="708" y="118" class="head" text-anchor="end">FASTER / CLOSE / SLOWER</text><text x="945" y="118" class="head" text-anchor="middle">SHARE OF TASKS</text>',
    ]
    for index, value in enumerate(families):
        y = top + index * row
        faster = value["faster_cases"]
        slower = value["slowdowns_gt_20pct"]
        close = value["cases"] - faster - slower
        widths = (bar_width * faster / value["cases"], bar_width * close / value["cases"], bar_width * slower / value["cases"])
        if index % 2 == 0:
            lines.append(f'<rect x="16" y="{y-16}" width="{width-32}" height="{row}" fill="#f5f7fb"/>')
        lines.extend((
            f'<line x1="16" y1="{y+9}" x2="{width-16}" y2="{y+9}" class="grid"/>',
            f'<text x="24" y="{y}" class="label">{escape(value["label"])}</text>',
            f'<text x="708" y="{y}" class="number">{faster:,} / {close:,} / {slower:,}</text>',
            f'<rect x="{bar_x}" y="{y-11}" width="{widths[0]:.1f}" height="12" fill="#238b64"/>',
            f'<rect x="{bar_x+widths[0]:.1f}" y="{y-11}" width="{widths[1]:.1f}" height="12" fill="#8995a7"/>',
            f'<rect x="{bar_x+widths[0]+widths[1]:.1f}" y="{y-11}" width="{widths[2]:.1f}" height="12" fill="#c84c4c"/>',
        ))
    lines.append("</svg>\n")
    Path(output).write_text("".join(lines), encoding="utf-8")


def label(category):
    value = category.removeprefix("large-").replace("-", " ")
    replacements = {
        "unicode words": "Find Unicode words and emoji",
        "unicode casefold": "Case-insensitive Unicode",
        "literal hit": "Find a present word",
        "literal miss": "Search for an absent word",
        "literal long": "Find a word in long text",
        "text tokens": "Find text tokens",
        "bytes tokens": "Find byte tokens",
        "bytes buffer": "Iterate over byte buffers",
        "cold compile": "Compile a new expression",
        "cold search": "Compile and search",
        "warm search": "Repeated module search",
        "warm sub": "Repeated module replacement",
        "match surface": "Read a match result",
        "split capture": "Split and keep separators",
        "split many": "Split many small pieces",
        "sub template": "Replace using captures",
        "sub callable": "Replace using a function",
        "empty iter": "Iterate over empty matches",
        "window scanner": "Scan a slice of the input",
        "window findall": "Find results in an input slice",
        "window search": "Search an input slice",
        "window match": "Match an input slice",
    }
    return replacements.get(value, value.capitalize())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--chart")
    parser.add_argument("--memory-chart")
    parser.add_argument("--regression-chart")
    parser.add_argument("--trials", type=int)
    parser.add_argument("--max-ops", type=int, default=0)
    parser.add_argument("--bootstraps", type=int)
    args = parser.parse_args()
    suite, cases, expected, manifest = frozen()
    trials = args.trials or suite.TRIALS
    bootstraps = args.bootstraps or suite.BOOTSTRAPS
    if trials < 1 or bootstraps < 1 or args.max_ops < 0:
        raise ValueError("invalid trial, operation, or bootstrap count")
    modules = {name: importlib.import_module(name) for name in (BASELINE, CANDIDATE)}
    raw_path = Path(args.raw)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    checks = 0
    with raw_path.open("w", encoding="utf-8") as stream:
        for case, want in zip(cases, expected, strict=True):
            actions = {}
            for name, module in modules.items():
                correctness_gate(module, case, want)
                actions[name] = operation(module, case)
                checks += 1
            operations = min(case["ops"], args.max_ops) if args.max_ops else case["ops"]
            for trial in range(trials):
                order = [BASELINE, CANDIDATE]
                random.Random(suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))).shuffle(order)
                for order_index, name in enumerate(order):
                    action = actions[name]
                    for _ in range(suite.WARMUPS):
                        action()
                    tracemalloc.start()
                    action()
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    before = proc_memory()
                    enabled = gc.isenabled()
                    if enabled:
                        gc.disable()
                    try:
                        started = time.perf_counter_ns()
                        for _ in range(operations):
                            result = action()
                        elapsed = time.perf_counter_ns() - started
                    finally:
                        if enabled:
                            gc.enable()
                    if snapshot(result) != want["result"]:
                        raise RuntimeError(f"post-timing mismatch: {name} {case['id']}")
                    checks += 1
                    after = proc_memory()
                    row = {"schema": "rebar-zig-performance-row-v4", "case": case["id"], "cohort": case["cohort"], "category": case["category"], "module": name, "trial": trial, "order": order_index, "operations": operations, "elapsed_ns": elapsed, "ns_per_op": elapsed / operations, "peak_traced_bytes": peak, "rss_before_kb": before["rss_kb"], "rss_after_kb": after["rss_kb"], "hwm_kb": after["hwm_kb"], "expected_sha256": want["result_sha256"]}
                    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
                    rows.append(row)
            print(f"measured {case['id']} ({operations} calls × {trials} paired trials)", flush=True)

    grouped = {(row["case"], row["trial"], row["module"]): row for row in rows}
    required = len(cases) * 2 * trials
    if len(grouped) != required:
        raise RuntimeError(f"raw row count drift: {len(grouped)} != {required}")
    rng = random.Random(suite.BOOTSTRAP_SEED)
    results = []
    logs_by_case = {}
    for case in cases:
        logs = [math.log(grouped[(case["id"], trial, BASELINE)]["ns_per_op"] / grouped[(case["id"], trial, CANDIDATE)]["ns_per_op"]) for trial in range(trials)]
        low, high = interval(logs, rng, bootstraps)
        speed = math.exp(statistics.fmean(logs))
        logs_by_case[case["id"]] = logs
        results.append({
            "case": case["id"],
            "cohort": case["cohort"],
            "category": case["category"],
            "speedup": speed,
            "ci95_low": low,
            "ci95_high": high,
            "statistically_faster": low > 1,
            "regression_gt_20pct": speed < .8,
            "baseline_ns": statistics.median(grouped[(case["id"], trial, BASELINE)]["ns_per_op"] for trial in range(trials)),
            "zig_ns": statistics.median(grouped[(case["id"], trial, CANDIDATE)]["ns_per_op"] for trial in range(trials)),
            "baseline_peak_bytes": statistics.median(grouped[(case["id"], trial, BASELINE)]["peak_traced_bytes"] for trial in range(trials)),
            "zig_peak_bytes": statistics.median(grouped[(case["id"], trial, CANDIDATE)]["peak_traced_bytes"] for trial in range(trials)),
        })

    rankings = []
    families = []
    for cohort in ("calibration", "holdout", "all"):
        selected = [case for case in cases if cohort == "all" or case["cohort"] == cohort]
        values = [item for item in results if cohort == "all" or item["cohort"] == cohort]
        point_logs = [statistics.fmean(logs_by_case[case["id"]]) for case in selected]
        low, high = interval(point_logs, rng, bootstraps)
        rankings.append({"cohort": cohort, "cases": len(selected), "speedup": math.exp(statistics.fmean(point_logs)), "ci95_low": low, "ci95_high": high, "faster_cases": sum(item["statistically_faster"] for item in values), "slowdowns_gt_20pct": sum(item["regression_gt_20pct"] for item in values)})
        for category in sorted({case["category"] for case in selected}):
            members = [item for item in values if item["category"] == category]
            member_logs = [math.log(item["speedup"]) for item in members]
            family_low, family_high = interval(member_logs, rng, bootstraps)
            memory_logs = [math.log((item["zig_peak_bytes"] + 1) / (item["baseline_peak_bytes"] + 1)) for item in members]
            families.append({"cohort": cohort, "category": category, "label": label(category), "cases": len(members), "speedup": math.exp(statistics.fmean(member_logs)), "ci95_low": family_low, "ci95_high": family_high, "faster_cases": sum(item["statistically_faster"] for item in members), "slowdowns_gt_20pct": sum(item["regression_gt_20pct"] for item in members), "memory_ratio": math.exp(statistics.fmean(memory_logs)), "baseline_peak_bytes": round(statistics.median(item["baseline_peak_bytes"] for item in members)), "zig_peak_bytes": round(statistics.median(item["zig_peak_bytes"] for item in members))})

    summary = {"schema": "rebar-zig-performance-v4", "expected_sha256": manifest["expected_sha256"], "trials": trials, "max_operations": args.max_ops or None, "bootstraps": bootstraps, "correctness_checks": checks, "rows": len(rows), "cases": len(cases), "rankings": rankings, "families": families, "case_results": results}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.chart:
        chart(summary, args.chart)
    if args.memory_chart:
        memory_chart(summary, args.memory_chart)
    if args.regression_chart:
        regression_chart(summary, args.regression_chart)
    print(json.dumps({key: value for key, value in summary.items() if key not in {"case_results", "families"}}, sort_keys=True))


if __name__ == "__main__":
    main()
