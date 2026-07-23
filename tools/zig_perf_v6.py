#!/usr/bin/env python3
"""Measure and exactly summarize the frozen v6 holdout for Python re versus Zig."""

from __future__ import annotations

import argparse
import array
import ctypes
import gc
import hashlib
import importlib
import json
import math
import random
import statistics
import time
import tracemalloc
from pathlib import Path

from tools.perf_v5 import digest, proc_memory, snapshot
from tools.perf_v6 import correctness_gate, frozen, operation
from tools.perf_v6_analyze_fast import helper, pointer, self_test


MODULES = ("re", "candidates.zig_candidate")


def measure(output):
    suite, cases, expected, manifest = frozen()
    modules = {name: importlib.import_module(name) for name in MODULES}
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    checks = 0
    with target.open("w", encoding="utf-8") as stream:
        for case, want in zip(cases, expected, strict=True):
            for trial in range(suite.TRIALS):
                order = list(MODULES)
                random.Random(suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))).shuffle(order)
                for order_index, name in enumerate(order):
                    module = modules[name]
                    expected_digest = correctness_gate(module, case, want)
                    checks += 1
                    action = operation(module, case)
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
                        result = None
                        for _ in range(case["ops"]):
                            result = action()
                        elapsed = time.perf_counter_ns() - started
                    finally:
                        if enabled:
                            gc.enable()
                    after = proc_memory()
                    timed = snapshot(result)
                    if digest(timed) != expected_digest or timed != want["result"]:
                        raise RuntimeError(f"post-timing correctness mismatch: {name} {case['id']}")
                    checks += 1
                    row = {"schema": "rebar-zig-performance-row-v6", "case": case["id"], "cohort": case["cohort"], "category": case["category"], "module": name, "trial": trial, "order": order_index, "ops": case["ops"], "elapsed_ns": elapsed, "ns_per_op": elapsed / case["ops"], "peak_traced_bytes": peak, "rss_before_kb": before["rss_kb"], "rss_after_kb": after["rss_kb"], "hwm_kb": after["hwm_kb"], "expected_sha256": expected_digest}
                    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
                    rows += 1
            print(f"measured {case['id']} ({case['ops']} operations × {suite.TRIALS} paired trials)", flush=True)
    required = len(cases) * len(MODULES) * suite.TRIALS
    if rows != required:
        raise RuntimeError(f"raw row count drift: {rows} != {required}")
    print(json.dumps({"rows": rows, "correctness_checks": checks, "cases": len(cases), "modules": list(MODULES), "trials": suite.TRIALS, "output": str(target), "manifest": manifest["expected_sha256"]}, sort_keys=True))


def analyze(input_path, output_path):
    suite, cases, expected, manifest = frozen()
    trials = suite.TRIALS
    rows_per_case = len(MODULES) * trials
    required = len(cases) * rows_per_case
    times = array.array("d", (0 for _ in range(required)))
    memory = array.array("Q", (0 for _ in range(required)))
    seen = bytearray(required)
    raw_hash = hashlib.sha256()
    row_count = 0
    with Path(input_path).open("rb") as stream:
        for row_count, line in enumerate(stream, 1):
            if row_count > required:
                raise RuntimeError(f"too many raw rows: {row_count} > {required}")
            raw_hash.update(line)
            row = json.loads(line)
            case_index = (row_count - 1) // rows_per_case
            case = cases[case_index]
            trial = row.get("trial")
            module = row.get("module")
            if not isinstance(trial, int) or not 0 <= trial < trials or module not in MODULES:
                raise RuntimeError(f"raw trial/module drift at row {row_count}")
            key = (case_index * len(MODULES) + MODULES.index(module)) * trials + trial
            if seen[key]:
                raise RuntimeError(f"duplicate raw row: {(case['id'], trial, module)}")
            seen[key] = 1
            if row.get("schema") != "rebar-zig-performance-row-v6" or row.get("case") != case["id"] or row.get("cohort") != case["cohort"] or row.get("category") != case["category"] or row.get("ops") != case["ops"] or row.get("expected_sha256") != expected[case_index]["result_sha256"]:
                raise RuntimeError(f"raw correctness or metadata drift at row {row_count}: {(case['id'], trial, module)}")
            times[key] = row["ns_per_op"]
            memory[key] = row["peak_traced_bytes"]
    if row_count != required or not all(seen):
        raise RuntimeError(f"raw row count drift: {row_count} != {required}")
    logs = array.array("d", (0 for _ in range(len(cases) * trials)))
    for case_index in range(len(cases)):
        baseline = case_index * len(MODULES) * trials
        zig = baseline + trials
        target = case_index * trials
        for trial in range(trials):
            logs[target + trial] = math.log(times[baseline + trial] / times[zig + trial])
    native, _ = helper()
    native.rebar_bootstrap_seed(suite.BOOTSTRAP_SEED)
    lows = array.array("d", (0 for _ in range(len(cases))))
    highs = array.array("d", (0 for _ in range(len(cases))))
    if native.rebar_bootstrap_cases(pointer(logs, ctypes.c_double), len(cases), trials, suite.BOOTSTRAPS, pointer(lows, ctypes.c_double), pointer(highs, ctypes.c_double)) != 0:
        raise RuntimeError("native case bootstrap failed")
    results = []
    for case_index, case in enumerate(cases):
        offset = case_index * len(MODULES) * trials
        baseline_memory = memory[offset:offset + trials]
        zig_memory = memory[offset + trials:offset + trials * 2]
        speed = math.exp(statistics.fmean(logs[case_index * trials:(case_index + 1) * trials]))
        low = lows[case_index]
        results.append({"case": case["id"], "cohort": case["cohort"], "category": case["category"], "candidate": MODULES[1], "weight": case["weight"], "speedup": speed, "ci95_low": low, "ci95_high": highs[case_index], "peak_traced_ratio": statistics.median(zig_memory) / max(1, statistics.median(baseline_memory)), "statistically_faster": low > 1, "regression_gt_20pct": speed < .8})
    rankings = []
    for cohort in ("calibration", "holdout", "all"):
        selected_indexes = [index for index, case in enumerate(cases) if cohort == "all" or case["cohort"] == cohort]
        denominator = sum(cases[index]["weight"] for index in selected_indexes)
        wanted = suite.CASES_PER_COHORT * (2 if cohort == "all" else 1)
        if denominator != wanted:
            raise RuntimeError(f"ranking denominator drift: {cohort} {denominator} != {wanted}")
        selected = array.array("I", selected_indexes)
        weights = array.array("d", (cases[index]["weight"] for index in selected_indexes))
        low = ctypes.c_double()
        high = ctypes.c_double()
        if native.rebar_bootstrap_overall(pointer(logs, ctypes.c_double), pointer(selected, ctypes.c_uint32), pointer(weights, ctypes.c_double), len(selected), 1, 0, trials, suite.BOOTSTRAPS, denominator, ctypes.byref(low), ctypes.byref(high)) != 0:
            raise RuntimeError(f"native overall bootstrap failed: {cohort}")
        relevant = [row for row in results if cohort == "all" or row["cohort"] == cohort]
        point = math.exp(sum(statistics.fmean(logs[index * trials:(index + 1) * trials]) * cases[index]["weight"] for index in selected_indexes) / denominator)
        rankings.append({"cohort": cohort, "candidate": MODULES[1], "cases": len(selected), "weight": denominator, "geomean_speedup": point, "ci95_low": low.value, "ci95_high": high.value, "statistically_faster_cases": sum(row["statistically_faster"] for row in relevant), "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in relevant)})
    summary = {"schema": "rebar-performance-summary-v6", "expected_sha256": manifest["expected_sha256"], "raw_sha256": raw_hash.hexdigest(), "rows": row_count, "rankings": rankings, "case_results": results, "regressions": [row for row in results if row["regression_gt_20pct"]]}
    Path(output_path).write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": row_count, "cases": len(cases), "results": len(results), "regressions": len(summary["regressions"]), "raw_sha256": summary["raw_sha256"], "output": str(output_path)}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(required=True)
    measure_parser = commands.add_parser("measure")
    measure_parser.add_argument("--output", required=True)
    measure_parser.set_defaults(function=lambda args: measure(args.output))
    analyze_parser = commands.add_parser("analyze")
    analyze_parser.add_argument("--input", required=True)
    analyze_parser.add_argument("--output", required=True)
    analyze_parser.set_defaults(function=lambda args: analyze(args.input, args.output))
    test_parser = commands.add_parser("self-test")
    test_parser.set_defaults(function=lambda args: print(json.dumps(self_test(), sort_keys=True)))
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
