#!/usr/bin/env python3
"""Measure only correctness-qualified frozen performance cases for the evolving Zig engine."""

import argparse
import gc
import importlib
import json
import math
import random
import statistics
import time
from html import escape
from pathlib import Path

from tools.perf_v3 import correctness_gate, frozen, operation, snapshot


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, math.floor(fraction * (len(ordered) - 1))))]


def confidence(values, rng, samples):
    means = [statistics.fmean(values[rng.randrange(len(values))] for _ in values) for _ in range(samples)]
    return math.exp(percentile(means, .025)), math.exp(percentile(means, .975))


def make_chart(result, output):
    values = sorted(result["case_results"], key=lambda item: item["speedup"], reverse=True)
    width, top, row_height = 1180, 145, 21
    height = top + len(values) * row_height + 30
    center, half = 914, 240
    max_log = max(1.0, max(abs(math.log2(value["speedup"])) for value in values))
    rankings = {item["cohort"]: item for item in result["rankings"]}
    holdout = rankings["holdout"]
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#fff"/>', '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:22px;font-weight:700}.sub{font-size:13px;fill:#536179}.head{font-size:11px;font-weight:700;fill:#41506a}.label{font-size:11px}.num{font-size:11px;text-anchor:end;font-variant-numeric:tabular-nums}.gain{font-size:10px;text-anchor:end;font-weight:700}.grid{stroke:#dbe1eb;stroke-width:1}</style>', '<text x="24" y="36" class="title">Zig public-engine pilot: speed on correctness-qualified tasks</text>', f'<text x="24" y="60" class="sub">{len(values)}/144 tasks qualify · holdout {holdout["geomean_speedup"]:.3f}× of Python re ({holdout["ci95_low"]:.3f}–{holdout["ci95_high"]:.3f}×) · every timed result checked</text>', '<text x="24" y="82" class="sub">Green is clearly faster, red is more than 20% slower, and grey is close or uncertain. Ten unsupported Unicode tasks are listed in the report and excluded visibly.</text>', '<text x="24" y="122" class="head">TASK</text><text x="544" y="122" class="head" text-anchor="end">PYTHON re (µs)</text><text x="640" y="122" class="head" text-anchor="end">ZIG (µs)</text><text x="896" y="122" class="head" text-anchor="end">SPEED · 95% RANGE</text><text x="914" y="122" class="head">SLOWER ← · → FASTER</text>', f'<line x1="{center}" y1="{top-12}" x2="{center}" y2="{height-16}" stroke="#8391a7" stroke-width="1.2"/>']
    for index, value in enumerate(values):
        speed = value["speedup"]
        case = value["case"]
        baseline = value["baseline_ns"] / 1000
        candidate = value["candidate_ns"] / 1000
        y = top + index * row_height
        delta = math.log2(speed) / max_log * half
        color = "#238b64" if value["statistically_faster"] else "#c84c4c" if speed < .8 else "#8995a7"
        if index % 2 == 0:
            lines.append(f'<rect x="16" y="{y-14}" width="{width-32}" height="{row_height}" fill="#f5f7fb"/>')
        lines.extend((f'<line x1="16" y1="{y+7}" x2="{width-16}" y2="{y+7}" class="grid"/>', f'<text x="24" y="{y}" class="label">{escape(case.replace(".", " / ").replace("-", " "))}</text>', f'<text x="544" y="{y}" class="num">{baseline:.2f}</text>', f'<text x="640" y="{y}" class="num">{candidate:.2f}</text>', f'<text x="896" y="{y}" class="gain" fill="{color}">{speed:.3f}× · {value["ci95_low"]:.3f}–{value["ci95_high"]:.3f}×</text>', f'<rect x="{center if delta >= 0 else center + delta:.1f}" y="{y-9}" width="{abs(delta):.1f}" height="10" rx="2" fill="{color}"/>'))
    lines.append("</svg>\n")
    Path(output).write_text("".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--chart")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--max-ops", type=int, default=8)
    parser.add_argument("--bootstraps", type=int, default=5000)
    args = parser.parse_args()
    if args.trials < 1 or args.max_ops < 1 or args.bootstraps < 1:
        raise ValueError("--trials, --max-ops, and --bootstraps must be positive")
    suite, cases, expected, manifest = frozen()
    candidate = importlib.import_module("candidates.zig_candidate")
    baseline = importlib.import_module("re")
    qualified = []
    failures = []
    checks = 0
    for case, want in zip(cases, expected, strict=True):
        try:
            correctness_gate(candidate, case, want)
            correctness_gate(baseline, case, want)
            checks += 2
            qualified.append((case, want))
        except BaseException as error:
            failures.append({"case": case["id"], "cohort": case["cohort"], "type": type(error).__name__, "message": str(error)})
    rows = []
    for case, want in qualified:
        actions = {"re": operation(baseline, case), "candidates.zig_candidate": operation(candidate, case)}
        operations = min(case["ops"], args.max_ops)
        for trial in range(args.trials):
            order = ["re", "candidates.zig_candidate"]
            random.Random(suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))).shuffle(order)
            for order_index, name in enumerate(order):
                action = actions[name]
                action()
                was_enabled = gc.isenabled()
                if was_enabled:
                    gc.disable()
                try:
                    started = time.perf_counter_ns()
                    for _ in range(operations):
                        value = action()
                    elapsed = time.perf_counter_ns() - started
                finally:
                    if was_enabled:
                        gc.enable()
                if snapshot(value) != want["result"]:
                    raise RuntimeError(f"post-timing Zig mismatch: {case['id']}")
                checks += 1
                rows.append({"case": case["id"], "cohort": case["cohort"], "module": name, "trial": trial, "order": order_index, "operations": operations, "elapsed_ns": elapsed, "per_operation_ns": elapsed / operations})
    grouped = {(row["case"], row["trial"], row["module"]): row for row in rows}
    rng = random.Random(suite.BOOTSTRAP_SEED)
    paired_logs = {}
    case_results = []
    for case, _ in qualified:
        logs = [math.log(grouped[(case["id"], trial, "re")]["per_operation_ns"] / grouped[(case["id"], trial, "candidates.zig_candidate")]["per_operation_ns"]) for trial in range(args.trials)]
        paired_logs[case["id"]] = logs
        low, high = confidence(logs, rng, args.bootstraps)
        baseline = statistics.median(grouped[(case["id"], trial, "re")]["per_operation_ns"] for trial in range(args.trials))
        candidate_time = statistics.median(grouped[(case["id"], trial, "candidates.zig_candidate")]["per_operation_ns"] for trial in range(args.trials))
        case_results.append({"case": case["id"], "cohort": case["cohort"], "speedup": math.exp(statistics.fmean(logs)), "ci95_low": low, "ci95_high": high, "statistically_faster": low > 1, "regression_gt_20pct": math.exp(statistics.fmean(logs)) < .8, "baseline_ns": baseline, "candidate_ns": candidate_time})

    rankings = []
    for cohort in ("calibration", "holdout", "all"):
        cohort_cases = [case for case, _ in qualified if cohort == "all" or case["cohort"] == cohort]
        relevant = [item for item in case_results if cohort == "all" or item["cohort"] == cohort]
        point = math.exp(statistics.fmean(statistics.fmean(paired_logs[case["id"]]) for case in cohort_cases))
        boot = [statistics.fmean(statistics.fmean(paired_logs[case["id"]][rng.randrange(args.trials)] for _ in range(args.trials)) for case in cohort_cases) for _ in range(args.bootstraps)]
        rankings.append({"cohort": cohort, "qualified": len(cohort_cases), "total": len(cases) if cohort == "all" else suite.CASES_PER_COHORT, "geomean_speedup": point, "ci95_low": math.exp(percentile(boot, .025)), "ci95_high": math.exp(percentile(boot, .975)), "faster_cases": sum(item["statistically_faster"] for item in relevant), "slowdowns_gt_20pct": sum(item["regression_gt_20pct"] for item in relevant)})
    result = {"schema": "rebar-zig-holdout-pilot-v2", "expected_sha256": manifest["expected_sha256"], "trials": args.trials, "max_operations": args.max_ops, "bootstraps": args.bootstraps, "correctness_checks": checks, "qualified": len(qualified), "total": len(cases), "qualified_cases": [case["id"] for case, _ in qualified], "unsupported_cases": failures, "rankings": rankings, "case_results": case_results, "rows": rows}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.chart:
        make_chart(result, args.chart)
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
