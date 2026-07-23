#!/usr/bin/env python3
"""Measure from-scratch Rust against the complete frozen v7 Python baseline."""

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

from tools.perf_v5 import digest, operation, proc_memory, snapshot
from tools.perf_v6_analyze_fast import (
    helper as bootstrap_helper,
    pointer,
    self_test as bootstrap_self_test,
)
from tools.perf_v7 import (
    correctness_gate,
    frozen,
    is_runtime_regression,
    valid_process_memory,
    verify_bootstrap_seed,
    verify_regression_boundaries,
)


MODULES = ("re", "candidates.rust_candidate")
ROW_SCHEMA = "rebar-rust-performance-row-v7"


def trial_order(suite, case, trial):
    order = list(MODULES)
    random.Random(
        suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))
    ).shuffle(order)
    return order


def measure(output, *, limit=None):
    suite, cases, expected, manifest = frozen()
    if limit is not None and (
        not isinstance(limit, int) or isinstance(limit, bool) or limit < 1
    ):
        raise ValueError("the smoke-test task count must be a positive integer")
    selected = list(zip(cases, expected, strict=True))
    if limit is not None:
        selected = selected[:limit]
    modules = {name: importlib.import_module(name) for name in MODULES}
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    checks = 0
    with destination.open("w", encoding="utf-8") as stream:
        for case, want in selected:
            for trial in range(suite.TRIALS):
                for order, name in enumerate(trial_order(suite, case, trial)):
                    module = modules[name]
                    expected_digest = correctness_gate(module, case, want)
                    checks += 1
                    action = operation(module, case)
                    for _ in range(suite.WARMUPS):
                        action()
                    tracemalloc.start()
                    try:
                        action()
                        _, peak = tracemalloc.get_traced_memory()
                    finally:
                        tracemalloc.stop()
                    before = proc_memory()
                    restore_gc = gc.isenabled()
                    if restore_gc:
                        gc.disable()
                    try:
                        started = time.perf_counter_ns()
                        result = None
                        for _ in range(case["ops"]):
                            result = action()
                        elapsed = time.perf_counter_ns() - started
                    finally:
                        if restore_gc:
                            gc.enable()
                    after = proc_memory()
                    timed = snapshot(result)
                    if digest(timed) != expected_digest or timed != want["result"]:
                        raise RuntimeError(
                            f"post-timing correctness mismatch: {name} {case['id']}"
                        )
                    checks += 1
                    stream.write(
                        json.dumps(
                            {
                                "schema": ROW_SCHEMA,
                                "case": case["id"],
                                "cohort": case["cohort"],
                                "category": case["category"],
                                "module": name,
                                "trial": trial,
                                "order": order,
                                "ops": case["ops"],
                                "elapsed_ns": elapsed,
                                "ns_per_op": elapsed / case["ops"],
                                "peak_traced_bytes": peak,
                                "rss_before_kb": before["rss_kb"],
                                "rss_after_kb": after["rss_kb"],
                                "hwm_kb": after["hwm_kb"],
                                "expected_sha256": expected_digest,
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                        + "\n"
                    )
                    rows += 1
            print(f"measured {case['id']} ({suite.TRIALS} paired trials)", flush=True)
    required = len(selected) * len(MODULES) * suite.TRIALS
    if rows != required:
        raise RuntimeError(f"paired Rust raw row count changed: {rows} != {required}")
    result = {
        "schema": (
            "rebar-rust-performance-measurement-v7"
            if limit is None
            else "rebar-rust-performance-smoke-v7"
        ),
        "complete": limit is None,
        "rows": rows,
        "correctness_checks": checks,
        "cases": len(selected),
        "modules": list(MODULES),
        "trials": suite.TRIALS,
        "warmups": suite.WARMUPS,
        "output": str(destination),
        "expected_sha256": manifest["expected_sha256"],
    }
    print(json.dumps(result, sort_keys=True))
    return result


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
                raise RuntimeError(f"too many Rust paired rows: {row_count} > {required}")
            raw_hash.update(line)
            row = json.loads(line)
            case_index = (row_count - 1) // rows_per_case
            case = cases[case_index]
            trial = row.get("trial")
            module = row.get("module")
            if (
                not isinstance(trial, int)
                or isinstance(trial, bool)
                or not 0 <= trial < trials
                or module not in MODULES
            ):
                raise RuntimeError(f"Rust paired trial or engine changed at row {row_count}")
            key = (case_index * len(MODULES) + MODULES.index(module)) * trials + trial
            if seen[key]:
                raise RuntimeError(f"duplicate Rust paired row: {(case['id'], trial, module)}")
            elapsed = row.get("elapsed_ns")
            per_operation = row.get("ns_per_op")
            peak = row.get("peak_traced_bytes")
            if (
                row.get("schema") != ROW_SCHEMA
                or row.get("case") != case["id"]
                or row.get("cohort") != case["cohort"]
                or row.get("category") != case["category"]
                or row.get("ops") != case["ops"]
                or row.get("expected_sha256") != expected[case_index]["result_sha256"]
                or row.get("order") != trial_order(suite, case, trial).index(module)
                or not isinstance(elapsed, int)
                or isinstance(elapsed, bool)
                or elapsed <= 0
                or not isinstance(per_operation, (int, float))
                or isinstance(per_operation, bool)
                or not math.isfinite(per_operation)
                or per_operation != elapsed / case["ops"]
                or not isinstance(peak, int)
                or isinstance(peak, bool)
                or peak < 0
                or not valid_process_memory(row)
            ):
                raise RuntimeError(f"Rust paired timing or metadata changed at row {row_count}")
            seen[key] = 1
            times[key] = per_operation
            memory[key] = peak
    if row_count != required or not all(seen):
        raise RuntimeError(f"Rust paired raw row count changed: {row_count} != {required}")

    logs = array.array("d", (0 for _ in range(len(cases) * trials)))
    for case_index in range(len(cases)):
        baseline = case_index * len(MODULES) * trials
        for trial in range(trials):
            logs[case_index * trials + trial] = math.log(
                times[baseline + trial] / times[baseline + trials + trial]
            )

    native, _target = bootstrap_helper()
    native.rebar_bootstrap_seed(suite.BOOTSTRAP_SEED)
    lows = array.array("d", (0 for _ in range(len(cases))))
    highs = array.array("d", (0 for _ in range(len(cases))))
    if native.rebar_bootstrap_cases(
        pointer(logs, ctypes.c_double),
        len(cases),
        trials,
        suite.BOOTSTRAPS,
        pointer(lows, ctypes.c_double),
        pointer(highs, ctypes.c_double),
    ):
        raise RuntimeError("Rust paired case confidence-range calculation failed")

    results = []
    for case_index, case in enumerate(cases):
        offset = case_index * len(MODULES) * trials
        baseline_memory = memory[offset : offset + trials]
        candidate_memory = memory[offset + trials : offset + trials * 2]
        values = logs[case_index * trials : (case_index + 1) * trials]
        speed = math.exp(statistics.fmean(values))
        low = lows[case_index]
        results.append(
            {
                "case": case["id"],
                "cohort": case["cohort"],
                "category": case["category"],
                "candidate": MODULES[1],
                "weight": case["weight"],
                "speedup": speed,
                "ci95_low": low,
                "ci95_high": highs[case_index],
                "peak_traced_ratio": statistics.median(candidate_memory)
                / max(1, statistics.median(baseline_memory)),
                "statistically_faster": low > 1,
                "regression_gt_20pct": is_runtime_regression(speed),
            }
        )

    rankings = []
    for cohort in ("calibration", "holdout", "all"):
        selected_indexes = [
            index for index, case in enumerate(cases)
            if cohort == "all" or case["cohort"] == cohort
        ]
        denominator = sum(cases[index]["weight"] for index in selected_indexes)
        wanted = suite.CASES_PER_COHORT * (2 if cohort == "all" else 1)
        if denominator != wanted:
            raise RuntimeError(f"Rust paired ranking denominator changed: {cohort}")
        selected = array.array("I", selected_indexes)
        weights = array.array("d", (cases[index]["weight"] for index in selected_indexes))
        low = ctypes.c_double()
        high = ctypes.c_double()
        if native.rebar_bootstrap_overall(
            pointer(logs, ctypes.c_double),
            pointer(selected, ctypes.c_uint32),
            pointer(weights, ctypes.c_double),
            len(selected),
            1,
            0,
            trials,
            suite.BOOTSTRAPS,
            denominator,
            ctypes.byref(low),
            ctypes.byref(high),
        ):
            raise RuntimeError(f"Rust paired overall confidence range failed: {cohort}")
        relevant = [
            row for row in results if cohort == "all" or row["cohort"] == cohort
        ]
        point = math.exp(
            sum(
                statistics.fmean(logs[index * trials : (index + 1) * trials])
                * cases[index]["weight"]
                for index in selected_indexes
            )
            / denominator
        )
        rankings.append(
            {
                "cohort": cohort,
                "candidate": MODULES[1],
                "cases": len(selected_indexes),
                "weight": denominator,
                "geomean_speedup": point,
                "ci95_low": low.value,
                "ci95_high": high.value,
                "statistically_faster_cases": sum(
                    row["statistically_faster"] for row in relevant
                ),
                "regressions_gt_20pct": sum(
                    row["regression_gt_20pct"] for row in relevant
                ),
            }
        )
    summary = {
        "schema": "rebar-performance-summary-v7",
        "expected_sha256": manifest["expected_sha256"],
        "raw_sha256": raw_hash.hexdigest(),
        "rows": row_count,
        "rankings": rankings,
        "case_results": results,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = {
        "rows": row_count,
        "cases": len(cases),
        "results": len(results),
        "regressions": len(summary["regressions"]),
        "raw_sha256": summary["raw_sha256"],
        "output": str(destination),
    }
    print(json.dumps(result, sort_keys=True))
    return result


def self_test():
    bootstrap = bootstrap_self_test()
    suite, cases, expected, manifest = frozen()
    seeded_draws = verify_bootstrap_seed(suite)
    boundary_checks = verify_regression_boundaries()
    indexes = [0]
    for family in suite.FAMILIES:
        indexes.append(
            next(
                index for index, case in enumerate(cases)
                if case["category"] == f"broader-{family}"
                and case["cohort"] == "calibration"
                and case["id"].endswith(".00")
            )
        )
    checks = 0
    for name in MODULES:
        module = importlib.import_module(name)
        for index in indexes:
            correctness_gate(module, cases[index], expected[index])
            checks += 1
    result = {
        **bootstrap,
        **seeded_draws,
        **boundary_checks,
        "schema": "rebar-rust-performance-self-test-v7",
        "candidate": MODULES[1],
        "expected_sha256": manifest["expected_sha256"],
        "frozen_cases": len(cases),
        "frozen_holdout": suite.CASES_PER_COHORT,
        "frozen_trials": suite.TRIALS,
        "frozen_warmups": suite.WARMUPS,
        "frozen_bootstraps": suite.BOOTSTRAPS,
        "sample_correctness_checks": checks,
    }
    print(json.dumps(result, sort_keys=True))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    measure_parser = commands.add_parser("measure")
    measure_parser.add_argument("--output", required=True)
    measure_parser.set_defaults(function=lambda args: measure(args.output))
    analyze_parser = commands.add_parser("analyze")
    analyze_parser.add_argument("--input", required=True)
    analyze_parser.add_argument("--output", required=True)
    analyze_parser.set_defaults(
        function=lambda args: analyze(args.input, args.output)
    )
    smoke_parser = commands.add_parser("smoke")
    smoke_parser.add_argument("--output", required=True)
    smoke_parser.add_argument("--cases", type=int, default=2)
    smoke_parser.set_defaults(
        function=lambda args: measure(args.output, limit=args.cases)
    )
    test_parser = commands.add_parser("self-test")
    test_parser.set_defaults(function=lambda _args: self_test())
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
