#!/usr/bin/env python3
"""Paired, correctness-gated actual-hit control for Match-result workloads."""

from __future__ import annotations

import argparse
import gc
import json
import math
import random
import re
import time
from pathlib import Path

import rebar
from performance.v5.suite import cases
from tools.perf_v5 import operation, snapshot


SEED = 2026073111


def geomean(values):
    return math.exp(sum(math.log(value) for value in values) / len(values))


def interval(values, seed, samples):
    generator = random.Random(seed)
    draws = sorted(geomean([values[generator.randrange(len(values))] for _ in values]) for _ in range(samples))
    return draws[int(.025 * samples)], draws[min(samples - 1, int(.975 * samples))]


def timed(function, operations):
    start = time.perf_counter_ns()
    for _ in range(operations):
        function()
    return (time.perf_counter_ns() - start) / operations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--trials", type=int, default=13)
    parser.add_argument("--warmups", type=int, default=4)
    parser.add_argument("--bootstraps", type=int, default=2000)
    args = parser.parse_args()
    selected = [dict(case) for case in cases() if case["category"] == "expanded-match-surface"]
    raw_rows = []
    results = []
    checks = 0
    failures = []
    for number, case in enumerate(selected):
        original = case["string"]
        case["string"] = re.sub(r"_[0-9]+-", "_-", original, count=1)
        case["id"] = case["id"].replace("match-surface", "match-surface-hit")
        oracle = operation(re, case)
        candidate = operation(rebar, case)
        expected = snapshot(oracle())
        actual = snapshot(candidate())
        checks += 1
        if expected is None or expected != actual:
            failures.append({"case": case["id"], "expected": expected, "actual": actual})
            continue
        for _ in range(args.warmups):
            oracle()
            candidate()
        baseline = []
        zig = []
        generator = random.Random(SEED + number)
        for trial in range(args.trials):
            gc.disable()
            if generator.randrange(2):
                first = timed(oracle, case["ops"])
                second = timed(candidate, case["ops"])
            else:
                second = timed(candidate, case["ops"])
                first = timed(oracle, case["ops"])
            gc.enable()
            baseline.append(first)
            zig.append(second)
            raw_rows.append({"case": case["id"], "cohort": case["cohort"], "trial": trial, "operations": case["ops"], "baseline_ns": first, "zig_ns": second})
        checks += 1
        after = snapshot(candidate())
        if after != expected:
            failures.append({"case": case["id"], "expected": expected, "actual": after, "phase": "post"})
            continue
        ratios = [left / right for left, right in zip(baseline, zig)]
        low, high = interval(ratios, SEED + number, args.bootstraps)
        results.append({"case": case["id"], "cohort": case["cohort"], "operations": case["ops"], "baseline_ns": sorted(baseline)[len(baseline) // 2], "zig_ns": sorted(zig)[len(zig) // 2], "speedup": geomean(ratios), "ci95_low": low, "ci95_high": high, "statistically_faster": low > 1, "regression_gt_20pct": geomean(ratios) < .8})
    Path(args.raw).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in raw_rows), encoding="utf-8")
    rankings = []
    for cohort in ("calibration", "holdout", "all"):
        members = [row for row in results if cohort == "all" or row["cohort"] == cohort]
        values = [row["speedup"] for row in members]
        low, high = interval(values, SEED + len(rankings), args.bootstraps)
        rankings.append({"cohort": cohort, "cases": len(members), "speedup": geomean(values), "ci95_low": low, "ci95_high": high, "faster_cases": sum(row["statistically_faster"] for row in members), "slowdowns_gt_20pct": sum(row["regression_gt_20pct"] for row in members)})
    report = {"schema": "rebar-zig-match-surface-hit-v1", "seed": SEED, "trials": args.trials, "warmups": args.warmups, "bootstraps": args.bootstraps, "cases": len(selected), "correctness_checks": checks, "failed": len(failures), "failures": failures, "rows": len(raw_rows), "rankings": rankings, "case_results": results}
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, default=repr) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in ("failures", "case_results")}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
