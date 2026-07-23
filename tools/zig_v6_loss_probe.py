#!/usr/bin/env python3
"""Correctness-gated paired timing for the Zig workloads exposed by v6."""

from __future__ import annotations

import argparse
import gc
import importlib
import json
import math
import random
import statistics
import time
from collections import defaultdict
from pathlib import Path

from tools.perf_v6 import correctness_gate, frozen, operation, snapshot


BASELINE = "re"
CANDIDATE = "candidates.zig_candidate"
DEFAULT = (
    "deeper-file-names",
    "deeper-shared-prefix-alternatives",
    "deeper-dense-literal-findall",
    "deeper-unicode-word-lines",
    "deeper-money-units",
    "expanded-backreference",
    "expanded-branch-alternatives",
)


def interval(values, rng, samples):
    means = sorted(statistics.fmean(values[rng.randrange(len(values))] for _ in values) for _ in range(samples))
    return math.exp(means[math.floor(.025 * (samples - 1))]), math.exp(means[math.floor(.975 * (samples - 1))])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--raw", required=True)
    parser.add_argument("--trials", type=int, default=7)
    parser.add_argument("--max-ops", type=int, default=32)
    parser.add_argument("--bootstraps", type=int, default=1000)
    parser.add_argument("--category", action="append")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.trials < 1 or args.max_ops < 1 or args.bootstraps < 1:
        raise ValueError("trial, operation, and bootstrap counts must be positive")
    suite, cases, expected, manifest = frozen()
    if args.all and args.category:
        raise ValueError("--all cannot be combined with --category")
    wanted = {case["category"] for case in cases} if args.all else set(args.category or DEFAULT)
    selected = [(case, want) for case, want in zip(cases, expected, strict=True) if case["category"] in wanted]
    found = {case["category"] for case, _ in selected}
    if found != wanted:
        raise RuntimeError(f"unknown workload categories: {sorted(wanted - found)}")
    modules = {name: importlib.import_module(name) for name in (BASELINE, CANDIDATE)}
    rows = []
    checks = 0
    raw = Path(args.raw)
    raw.parent.mkdir(parents=True, exist_ok=True)
    with raw.open("w", encoding="utf-8") as stream:
        for index, (case, want) in enumerate(selected):
            actions = {}
            for name, module in modules.items():
                correctness_gate(module, case, want)
                actions[name] = operation(module, case)
                checks += 1
            operations = min(case["ops"], args.max_ops)
            for trial in range(args.trials):
                order = [BASELINE, CANDIDATE]
                random.Random(suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))).shuffle(order)
                for order_index, name in enumerate(order):
                    action = actions[name]
                    for _ in range(suite.WARMUPS):
                        action()
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
                    row = {"case": case["id"], "cohort": case["cohort"], "category": case["category"], "module": name, "trial": trial, "order": order_index, "operations": operations, "elapsed_ns": elapsed, "ns_per_op": elapsed / operations, "expected_sha256": want["result_sha256"]}
                    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
                    rows.append(row)
            if index and index % 128 == 0:
                print(f"measured {index}/{len(selected)}", flush=True)
    grouped = {(row["case"], row["trial"], row["module"]): row for row in rows}
    if len(grouped) != len(selected) * args.trials * 2:
        raise RuntimeError("duplicate or missing raw timing rows")
    rng = random.Random(suite.BOOTSTRAP_SEED)
    results = []
    for case, _ in selected:
        logs = [math.log(grouped[(case["id"], trial, BASELINE)]["ns_per_op"] / grouped[(case["id"], trial, CANDIDATE)]["ns_per_op"]) for trial in range(args.trials)]
        low, high = interval(logs, rng, args.bootstraps)
        speed = math.exp(statistics.fmean(logs))
        results.append({"case": case["id"], "cohort": case["cohort"], "category": case["category"], "speedup": speed, "ci95_low": low, "ci95_high": high, "baseline_ns": statistics.median(grouped[(case["id"], trial, BASELINE)]["ns_per_op"] for trial in range(args.trials)), "zig_ns": statistics.median(grouped[(case["id"], trial, CANDIDATE)]["ns_per_op"] for trial in range(args.trials)), "statistically_faster": low > 1, "regression_gt_20pct": speed < .8})
    families = []
    family_rows = defaultdict(list)
    for row in results:
        family_rows[(row["cohort"], row["category"])].append(row)
    for (cohort, category), members in sorted(family_rows.items()):
        logs = [math.log(row["speedup"]) for row in members]
        low, high = interval(logs, rng, args.bootstraps)
        families.append({"cohort": cohort, "category": category, "cases": len(members), "speedup": math.exp(statistics.fmean(logs)), "ci95_low": low, "ci95_high": high, "faster": sum(row["statistically_faster"] for row in members), "slow": sum(row["regression_gt_20pct"] for row in members)})
    summary = {"schema": "rebar-zig-v6-loss-probe-v1", "expected_sha256": manifest["expected_sha256"], "categories": sorted(wanted), "cases": len(selected), "trials": args.trials, "max_operations": args.max_ops, "bootstraps": args.bootstraps, "rows": len(rows), "correctness_checks": checks, "families": families, "case_results": results}
    Path(args.output).write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for row in families:
        if row["cohort"] == "holdout":
            print(f"{row['category']:<40} {row['speedup']:.3f}× {row['ci95_low']:.3f}–{row['ci95_high']:.3f} faster={row['faster']}/{row['cases']} slow={row['slow']}")
    print(json.dumps({key: value for key, value in summary.items() if key not in {"families", "case_results"}}, sort_keys=True))


if __name__ == "__main__":
    main()
