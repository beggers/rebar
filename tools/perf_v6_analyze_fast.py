#!/usr/bin/env python3
"""Stream and summarize the large v6 performance run with exact paired draws."""

from __future__ import annotations

import argparse
import array
import ctypes
import hashlib
import json
import math
import random
import statistics
import subprocess
import tempfile
from pathlib import Path

from tools.perf_v6 import frozen
from tools.perf_v5 import percentile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "perf_v6_bootstrap.c"


def pointer(values, item_type):
    return (item_type * len(values)).from_buffer(values)


def helper():
    target = Path(tempfile.gettempdir()) / f"rebar-perf-v6-bootstrap-{hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:16]}.so"
    if not target.exists():
        subprocess.run(("cc", "-std=c11", "-O3", "-fPIC", "-shared", "-Wall", "-Wextra", "-Werror", str(SOURCE), "-lm", "-o", str(target)), check=True)
    result = ctypes.CDLL(str(target))
    result.rebar_bootstrap_seed.argtypes = (ctypes.c_uint32,)
    result.rebar_bootstrap_draws.argtypes = (ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t)
    result.rebar_bootstrap_cases.argtypes = (ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double))
    result.rebar_bootstrap_cases.restype = ctypes.c_int
    result.rebar_bootstrap_overall.argtypes = (ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_double, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double))
    result.rebar_bootstrap_overall.restype = ctypes.c_int
    return result, target


def self_test():
    native, target = helper()
    seed = 1985072202
    draws = array.array("I", (0 for _ in range(4096)))
    native.rebar_bootstrap_seed(seed)
    native.rebar_bootstrap_draws(pointer(draws, ctypes.c_uint32), len(draws))
    reference = random.Random(seed)
    expected_draws = [reference.randrange(13) for _ in draws]
    if list(draws) != expected_draws:
        first = next(index for index, (left, right) in enumerate(zip(draws, expected_draws, strict=True)) if left != right)
        raise RuntimeError(f"native bootstrap draw drift at {first}: {draws[first]} != {expected_draws[first]}")

    cases = 5
    candidates = 4
    trials = 13
    bootstraps = 41
    logs = array.array("d", (math.sin(index * .37) / 5 + index / 10000 for index in range(cases * candidates * trials)))
    lows = array.array("d", (0 for _ in range(cases * candidates)))
    highs = array.array("d", (0 for _ in range(cases * candidates)))
    native.rebar_bootstrap_seed(seed)
    if native.rebar_bootstrap_cases(pointer(logs, ctypes.c_double), len(lows), trials, bootstraps, pointer(lows, ctypes.c_double), pointer(highs, ctypes.c_double)) != 0:
        raise RuntimeError("native case bootstrap failed")

    reference = random.Random(seed)
    reference_lows = []
    reference_highs = []
    for result in range(cases * candidates):
        values = logs[result * trials:(result + 1) * trials]
        samples = [statistics.fmean(values[reference.randrange(trials)] for _ in values) for _ in range(bootstraps)]
        reference_lows.append(math.exp(percentile(samples, .025)))
        reference_highs.append(math.exp(percentile(samples, .975)))
    if any(abs(left - right) > 2e-15 for left, right in zip(lows, reference_lows, strict=True)) or any(abs(left - right) > 2e-15 for left, right in zip(highs, reference_highs, strict=True)):
        raise RuntimeError("native case intervals differ from the Python reference")

    selected = array.array("I", (0, 2, 4))
    weights = array.array("d", (1, 2, 1))
    native_lows = []
    native_highs = []
    reference_lows = []
    reference_highs = []
    for candidate in range(candidates):
        low = ctypes.c_double()
        high = ctypes.c_double()
        result = native.rebar_bootstrap_overall(pointer(logs, ctypes.c_double), pointer(selected, ctypes.c_uint32), pointer(weights, ctypes.c_double), len(selected), candidates, candidate, trials, bootstraps, sum(weights), ctypes.byref(low), ctypes.byref(high))
        if result != 0:
            raise RuntimeError("native overall bootstrap failed")
        native_lows.append(low.value)
        native_highs.append(high.value)
        samples = []
        for _ in range(bootstraps):
            total = 0
            for case, weight in zip(selected, weights, strict=True):
                values = logs[(case * candidates + candidate) * trials:(case * candidates + candidate + 1) * trials]
                total += statistics.fmean(values[reference.randrange(trials)] for _ in values) * weight
            samples.append(total / sum(weights))
        reference_lows.append(math.exp(percentile(samples, .025)))
        reference_highs.append(math.exp(percentile(samples, .975)))
    if any(abs(left - right) > 2e-15 for left, right in zip(native_lows, reference_lows, strict=True)) or any(abs(left - right) > 2e-15 for left, right in zip(native_highs, reference_highs, strict=True)):
        raise RuntimeError("native overall intervals differ from the Python reference")
    return {"draws": len(draws), "case_intervals": len(lows), "overall_intervals": len(native_lows), "helper": str(target), "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "passed": True}


def analyze(input_path, output_path):
    suite, cases, expected, manifest = frozen()
    modules = tuple(suite.MODULES)
    candidates = modules[1:]
    candidate_index = {name: index for index, name in enumerate(candidates)}
    trials = suite.TRIALS
    rows_per_case = len(modules) * trials
    required = len(cases) * rows_per_case
    times = array.array("d", (0 for _ in range(len(cases) * len(modules) * trials)))
    memory = array.array("Q", (0 for _ in range(len(cases) * len(modules) * trials)))
    seen = bytearray(required)
    digest = hashlib.sha256()
    row_count = 0
    with Path(input_path).open("rb") as stream:
        for row_count, line in enumerate(stream, 1):
            if row_count > required:
                raise RuntimeError(f"too many raw rows: {row_count} > {required}")
            digest.update(line)
            row = json.loads(line)
            case_index = (row_count - 1) // rows_per_case
            case = cases[case_index]
            trial = row.get("trial")
            module = row.get("module")
            if not isinstance(trial, int) or not 0 <= trial < trials or module not in modules:
                raise RuntimeError(f"raw trial/module drift at row {row_count}")
            module_index = modules.index(module)
            key = (case_index * len(modules) + module_index) * trials + trial
            if seen[key]:
                raise RuntimeError(f"duplicate raw row: {(case['id'], trial, module)}")
            seen[key] = 1
            if row.get("schema") != "rebar-performance-row-v6" or row.get("case") != case["id"] or row.get("cohort") != case["cohort"] or row.get("category") != case["category"] or row.get("ops") != case["ops"] or row.get("expected_sha256") != expected[case_index]["result_sha256"]:
                raise RuntimeError(f"raw correctness or metadata drift at row {row_count}: {(case['id'], trial, module)}")
            times[key] = row["ns_per_op"]
            memory[key] = row["peak_traced_bytes"]
    if row_count != required or not all(seen):
        raise RuntimeError(f"raw row count drift: {row_count} != {required}")

    logs = array.array("d", (0 for _ in range(len(cases) * len(candidates) * trials)))
    for case_index in range(len(cases)):
        baseline = case_index * len(modules) * trials
        for name, target_index in candidate_index.items():
            source = (case_index * len(modules) + modules.index(name)) * trials
            target = (case_index * len(candidates) + target_index) * trials
            for trial in range(trials):
                logs[target + trial] = math.log(times[baseline + trial] / times[source + trial])

    native, _ = helper()
    native.rebar_bootstrap_seed(suite.BOOTSTRAP_SEED)
    lows = array.array("d", (0 for _ in range(len(cases) * len(candidates))))
    highs = array.array("d", (0 for _ in range(len(cases) * len(candidates))))
    if native.rebar_bootstrap_cases(pointer(logs, ctypes.c_double), len(lows), trials, suite.BOOTSTRAPS, pointer(lows, ctypes.c_double), pointer(highs, ctypes.c_double)) != 0:
        raise RuntimeError("native case bootstrap failed")

    results = []
    for case_index, case in enumerate(cases):
        baseline_memory = memory[case_index * len(modules) * trials:(case_index * len(modules) + 1) * trials]
        for name, target_index in candidate_index.items():
            result_index = case_index * len(candidates) + target_index
            values = logs[result_index * trials:(result_index + 1) * trials]
            module_index = modules.index(name)
            candidate_memory = memory[(case_index * len(modules) + module_index) * trials:(case_index * len(modules) + module_index + 1) * trials]
            speed = math.exp(statistics.fmean(values))
            low = lows[result_index]
            results.append({"case": case["id"], "cohort": case["cohort"], "category": case["category"], "candidate": name, "weight": case["weight"], "speedup": speed, "ci95_low": low, "ci95_high": highs[result_index], "peak_traced_ratio": statistics.median(candidate_memory) / max(1, statistics.median(baseline_memory)), "statistically_faster": low > 1, "regression_gt_20pct": speed < .8})

    rankings = []
    for cohort in ("calibration", "holdout", "all"):
        selected_indexes = [index for index, case in enumerate(cases) if cohort == "all" or case["cohort"] == cohort]
        denominator = sum(cases[index]["weight"] for index in selected_indexes)
        wanted = suite.CASES_PER_COHORT * (2 if cohort == "all" else 1)
        if denominator != wanted:
            raise RuntimeError(f"ranking denominator drift: {cohort} {denominator} != {wanted}")
        selected = array.array("I", selected_indexes)
        weights = array.array("d", (cases[index]["weight"] for index in selected_indexes))
        for name, target_index in candidate_index.items():
            low = ctypes.c_double()
            high = ctypes.c_double()
            result = native.rebar_bootstrap_overall(pointer(logs, ctypes.c_double), pointer(selected, ctypes.c_uint32), pointer(weights, ctypes.c_double), len(selected), len(candidates), target_index, trials, suite.BOOTSTRAPS, denominator, ctypes.byref(low), ctypes.byref(high))
            if result != 0:
                raise RuntimeError(f"native overall bootstrap failed: {cohort} {name}")
            total = 0
            for case_index in selected_indexes:
                result_index = case_index * len(candidates) + target_index
                total += statistics.fmean(logs[result_index * trials:(result_index + 1) * trials]) * cases[case_index]["weight"]
            relevant = [row for row in results if row["candidate"] == name and (cohort == "all" or row["cohort"] == cohort)]
            rankings.append({"cohort": cohort, "candidate": name, "cases": len(selected), "weight": denominator, "geomean_speedup": math.exp(total / denominator), "ci95_low": low.value, "ci95_high": high.value, "statistically_faster_cases": sum(row["statistically_faster"] for row in relevant), "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in relevant)})
    summary = {"schema": "rebar-performance-summary-v6", "expected_sha256": manifest["expected_sha256"], "raw_sha256": digest.hexdigest(), "rows": row_count, "rankings": rankings, "case_results": results, "regressions": [row for row in results if row["regression_gt_20pct"]]}
    Path(output_path).write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"rows": row_count, "cases": len(cases), "results": len(results), "regressions": len(summary["regressions"]), "raw_sha256": summary["raw_sha256"], "output": str(output_path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return
    if not args.input or not args.output:
        parser.error("--input and --output are required unless --self-test is used")
    print(json.dumps(analyze(args.input, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
