#!/usr/bin/env python3
"""Correctness-gated, paired holdout pilot for iterating on individual engines."""

import argparse
import gc
import importlib
import json
import math
import random
import statistics
import time
from pathlib import Path

from tools.perf_v3 import correctness_gate, frozen, operation, snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--module", action="append", required=True)
    parser.add_argument("--cohort", choices=("calibration", "holdout", "all"), default="holdout")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--max-ops", type=int, default=8)
    args = parser.parse_args()
    if args.trials < 1 or args.max_ops < 1:
        raise ValueError("--trials and --max-ops must be positive")

    suite, cases, expected, manifest = frozen()
    selected = [(case, want) for case, want in zip(cases, expected, strict=True) if args.cohort == "all" or case["cohort"] == args.cohort]
    names = ["re", *args.module]
    if len(names) != len(set(names)):
        raise ValueError("duplicate module")
    modules = {name: importlib.import_module(name) for name in names}
    rows = []
    checks = 0
    for case, want in selected:
        actions = {}
        for name, module in modules.items():
            correctness_gate(module, case, want)
            checks += 1
            actions[name] = operation(module, case)
        operations = min(case["ops"], args.max_ops)
        for trial in range(args.trials):
            order = list(names)
            random.Random(suite.ORDER_SEED + trial * 1009 + sum(ord(char) for char in case["id"])).shuffle(order)
            for order_index, name in enumerate(order):
                action = actions[name]
                action()
                was_enabled = gc.isenabled()
                if was_enabled:
                    gc.disable()
                try:
                    begin = time.perf_counter_ns()
                    for _ in range(operations):
                        value = action()
                    elapsed = time.perf_counter_ns() - begin
                finally:
                    if was_enabled:
                        gc.enable()
                if snapshot(value) != want["result"]:
                    raise RuntimeError(f"post-timing correctness mismatch: {name} {case['id']}")
                checks += 1
                rows.append({"case": case["id"], "cohort": case["cohort"], "module": name, "trial": trial, "order": order_index, "operations": operations, "elapsed_ns": elapsed, "per_operation_ns": elapsed / operations})

    rankings = []
    for name in args.module:
        speedups = []
        faster = 0
        slow = 0
        for case, _ in selected:
            baseline = statistics.median(row["per_operation_ns"] for row in rows if row["case"] == case["id"] and row["module"] == "re")
            candidate = statistics.median(row["per_operation_ns"] for row in rows if row["case"] == case["id"] and row["module"] == name)
            speed = baseline / candidate
            speedups.append(speed)
            faster += speed > 1
            slow += speed < .8
        rankings.append({"module": name, "cases": len(selected), "geomean_speedup": math.exp(statistics.fmean(math.log(value) for value in speedups)), "faster_cases": faster, "slowdowns_gt_20pct": slow})

    result = {"schema": "rebar-engine-pilot-v1", "cohort": args.cohort, "cases": len(selected), "trials": args.trials, "max_operations": args.max_ops, "modules": names, "correctness_checks": checks, "expected_sha256": manifest["expected_sha256"], "rows": rows, "rankings": rankings}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
