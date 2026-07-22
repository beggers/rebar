#!/usr/bin/env python3
"""Freeze, correctness-gate, measure, and analyze the broader performance holdout."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib
import importlib.util
import json
import math
import platform
import random
import statistics
import sys
import time
import tracemalloc
from collections import Counter
from pathlib import Path

from tools.perf_v5 import digest, encode, interval, operation, percentile, proc_memory, snapshot, source_kind


ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "performance" / "v6" / "suite.py"
EXPECTED = ROOT / "performance" / "v6" / "expected.jsonl"
MANIFEST = ROOT / "performance" / "v6" / "manifest.json"
PARENT_SUITE = ROOT / "performance" / "v5" / "suite.py"
PARENT_EXPECTED = ROOT / "performance" / "v5" / "expected.jsonl"
PARENT_MANIFEST = ROOT / "performance" / "v5" / "manifest.json"
CORRECTNESS = ROOT / "oracle" / "v3" / "manifest.json"
GOAL_HASH = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"


def runtime():
    if platform.python_implementation() != "CPython" or sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError(f"performance oracle requires CPython 3.14.6, got {platform.python_implementation()} {sys.version.split()[0]}")


def suite_module():
    spec = importlib.util.spec_from_file_location("rebar_performance_v6", SUITE_PATH)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def validate_suite(suite, cases):
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate performance case IDs")
    cohorts = {name: [case for case in cases if case["cohort"] == name] for name in ("calibration", "holdout")}
    if any(len(values) != suite.CASES_PER_COHORT for values in cohorts.values()):
        raise RuntimeError(f"performance cohort count drift: {[(name, len(values)) for name, values in cohorts.items()]}")
    if any(sum(case["weight"] for case in values) != suite.CASES_PER_COHORT for values in cohorts.values()):
        raise RuntimeError("performance cohort weight drift")
    if {case["category"] for case in cohorts["calibration"]} != {case["category"] for case in cohorts["holdout"]}:
        raise RuntimeError("calibration and holdout categories differ")
    if any(case["ops"] <= 0 or case["weight"] <= 0 for case in cases):
        raise RuntimeError("non-positive operation count or weight")
    wanted = len(suite.FAMILIES) * suite.VARIANTS
    for cohort, values in cohorts.items():
        generated = [case for case in values if ".deeper." in case["id"]]
        counts = Counter(case["category"] for case in generated)
        if len(generated) != wanted or set(counts) != {f"deeper-{name}" for name in suite.FAMILIES} or any(value != suite.VARIANTS for value in counts.values()):
            raise RuntimeError(f"deeper performance family count drift: {cohort} {dict(sorted(counts.items()))}")
    if hashlib.sha256((ROOT / "GOAL.md").read_bytes()).hexdigest() != GOAL_HASH:
        raise RuntimeError("GOAL.md hash changed")
    correctness = json.loads(CORRECTNESS.read_text(encoding="utf-8"))
    if correctness["schema"] != "rebar-correctness-v3" or correctness["cases"] != 44084 or correctness["mapped_obligations"] != 51:
        raise RuntimeError("large correctness oracle is not frozen and qualified")
    parent = json.loads(PARENT_MANIFEST.read_text(encoding="utf-8"))
    checks = (
        ("schema", parent["schema"], "rebar-performance-v5"),
        ("cases", parent["cases"], 6288),
        ("suite", hashlib.sha256(PARENT_SUITE.read_bytes()).hexdigest(), parent["suite_sha256"]),
        ("expected", hashlib.sha256(PARENT_EXPECTED.read_bytes()).hexdigest(), parent["expected_sha256"]),
    )
    if any(got != want for _, got, want in checks):
        raise RuntimeError(f"parent performance freeze drift: {checks}")
    return correctness, parent


def records_for(module, cases):
    for index, case in enumerate(cases):
        try:
            result = snapshot(operation(module, case)())
        except BaseException as error:
            raise RuntimeError(f"performance fixture failed: {case['id']}: {type(error).__name__}: {error}") from error
        if index and index % 1024 == 0:
            print(f"freezing {index}/{len(cases)}", flush=True)
        yield {"id": case["id"], "cohort": case["cohort"], "category": case["category"], "result": result, "result_sha256": digest(result)}


def freeze(_args):
    runtime()
    suite = suite_module()
    cases = suite.cases()
    correctness, parent = validate_suite(suite, cases)
    baseline = importlib.import_module("re")
    first = list(records_for(baseline, cases))
    baseline.purge()
    second = list(records_for(baseline, cases))
    if first != second:
        raise RuntimeError("non-deterministic stdlib performance fixture")
    payload = encode(first)
    if encode(first[:parent["cases"]]) != PARENT_EXPECTED.read_bytes():
        raise RuntimeError("broader performance fixture does not preserve the frozen v5 prefix")
    EXPECTED.parent.mkdir(parents=True, exist_ok=True)
    EXPECTED.write_bytes(payload)
    manifest = {
        "schema": "rebar-performance-v6", "python": "3.14.6", "implementation": "CPython", "goal_sha256": GOAL_HASH,
        "correctness_expected_sha256": correctness["expected_sha256"], "parent_expected_sha256": parent["expected_sha256"],
        "parent_cases": parent["cases"], "suite_sha256": hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "expected_sha256": hashlib.sha256(payload).hexdigest(),
        "modules": suite.MODULES, "cases": len(cases), "cohorts": {"calibration": suite.CASES_PER_COHORT, "holdout": suite.CASES_PER_COHORT},
        "weights": {"calibration": suite.CASES_PER_COHORT, "holdout": suite.CASES_PER_COHORT}, "expanded_families": len(suite.FAMILIES),
        "variants_per_family": suite.VARIANTS, "seeds": dict(sorted(suite.SEEDS.items())),
        "api_counts": dict(sorted(Counter(case["api"] for case in cases).items())),
        "lifecycle_counts": dict(sorted(Counter(case["lifecycle"] for case in cases).items())),
        "input_counts": dict(sorted(Counter(source_kind(case) for case in cases).items())), "trials": suite.TRIALS,
        "warmups": suite.WARMUPS, "order_seed": suite.ORDER_SEED, "bootstrap_seed": suite.BOOTSTRAP_SEED, "bootstraps": suite.BOOTSTRAPS,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


def frozen():
    runtime()
    suite = suite_module()
    cases = suite.cases()
    correctness, parent = validate_suite(suite, cases)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload = EXPECTED.read_bytes()
    checks = (
        ("suite", hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), manifest["suite_sha256"]),
        ("runner", hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), manifest["runner_sha256"]),
        ("expected", hashlib.sha256(payload).hexdigest(), manifest["expected_sha256"]),
        ("correctness", correctness["expected_sha256"], manifest["correctness_expected_sha256"]),
        ("parent", parent["expected_sha256"], manifest["parent_expected_sha256"]),
    )
    if any(got != want for _, got, want in checks):
        raise RuntimeError(f"performance freeze drift: {checks}")
    expected = [json.loads(line) for line in payload.splitlines()]
    if len(expected) != len(cases) or manifest["cases"] != len(cases):
        raise RuntimeError("performance case count drift")
    if encode(expected[:parent["cases"]]) != PARENT_EXPECTED.read_bytes():
        raise RuntimeError("frozen v5 performance prefix changed")
    return suite, cases, expected, manifest


def correctness_gate(module, case, expected):
    result = snapshot(operation(module, case)())
    actual = digest(result)
    if actual != expected["result_sha256"] or result != expected["result"]:
        raise RuntimeError(f"performance correctness mismatch: {module.__name__} {case['id']}")
    return actual


def verify(args):
    suite, cases, expected, manifest = frozen()
    names = args.module or suite.MODULES
    failures = []
    for name in names:
        module = importlib.import_module(name)
        for index, (case, want) in enumerate(zip(cases, expected, strict=True)):
            try:
                correctness_gate(module, case, want)
            except BaseException as error:
                failures.append({"module": name, "case": case["id"], "type": type(error).__name__, "message": str(error)})
            if index and index % 2048 == 0:
                print(f"checking {name} {index}/{len(cases)}", flush=True)
    result = {"schema": "rebar-performance-correctness-v6", "modules": names, "cases_per_module": len(cases), "checks": len(cases) * len(names), "failed": len(failures), "expected_sha256": manifest["expected_sha256"], "failures": failures}
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        for failure in failures[:40]:
            print(f"{failure['module']} {failure['case']}: {failure['type']}: {failure['message']}", file=sys.stderr)
        raise SystemExit(1)


def measure(args):
    suite, cases, expected, manifest = frozen()
    modules = {name: importlib.import_module(name) for name in suite.MODULES}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with target.open("w", encoding="utf-8") as stream:
        for case, want in zip(cases, expected, strict=True):
            for trial in range(suite.TRIALS):
                order = list(suite.MODULES)
                random.Random(suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))).shuffle(order)
                for order_index, name in enumerate(order):
                    module = modules[name]
                    expected_digest = correctness_gate(module, case, want)
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
                        sink = None
                        for _ in range(case["ops"]):
                            sink = action()
                        elapsed = time.perf_counter_ns() - started
                    finally:
                        if enabled:
                            gc.enable()
                    timed_result = snapshot(sink)
                    if digest(timed_result) != expected_digest or timed_result != want["result"]:
                        raise RuntimeError(f"post-timing correctness mismatch: {name} {case['id']}")
                    row = {"schema": "rebar-performance-row-v6", "case": case["id"], "cohort": case["cohort"], "category": case["category"], "module": name, "trial": trial, "order": order_index, "ops": case["ops"], "elapsed_ns": elapsed, "ns_per_op": elapsed / case["ops"], "peak_traced_bytes": peak, "rss_before_kb": before["rss_kb"], "rss_after_kb": after["rss_kb"], "hwm_kb": after["hwm_kb"], "expected_sha256": expected_digest}
                    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
                    rows += 1
            print(f"measured {case['id']} ({case['ops']} operations × {suite.TRIALS} paired trials)", flush=True)
    required = len(cases) * len(suite.MODULES) * suite.TRIALS
    if rows != required:
        raise RuntimeError(f"raw row count drift: {rows} != {required}")
    print(json.dumps({"rows": rows, "cases": len(cases), "modules": len(suite.MODULES), "trials": suite.TRIALS, "output": str(target), "manifest": manifest["expected_sha256"]}, sort_keys=True))


def analyze(args):
    suite, cases, expected, manifest = frozen()
    payload = Path(args.input).read_bytes()
    rows = [json.loads(line) for line in payload.splitlines()]
    required = len(cases) * len(suite.MODULES) * suite.TRIALS
    if len(rows) != required:
        raise RuntimeError(f"raw row count drift: {len(rows)} != {required}")
    case_by_id = {case["id"]: case for case in cases}
    expected_by_id = {item["id"]: item["result_sha256"] for item in expected}
    grouped = {}
    for row in rows:
        key = (row["case"], row["trial"], row["module"])
        if key in grouped:
            raise RuntimeError(f"duplicate raw row: {key}")
        case = case_by_id.get(row["case"])
        if case is None or row["module"] not in suite.MODULES or not 0 <= row["trial"] < suite.TRIALS or row["schema"] != "rebar-performance-row-v6" or row["cohort"] != case["cohort"] or row["category"] != case["category"] or row["ops"] != case["ops"] or row["expected_sha256"] != expected_by_id[row["case"]]:
            raise RuntimeError(f"raw correctness or metadata drift: {key}")
        grouped[key] = row
    if len(grouped) != required:
        raise RuntimeError("missing raw rows")
    rng = random.Random(suite.BOOTSTRAP_SEED)
    candidates = suite.MODULES[1:]
    results = []
    logs = {}
    for case in cases:
        for name in candidates:
            values = []
            baseline_memory = []
            candidate_memory = []
            for trial in range(suite.TRIALS):
                baseline = grouped[(case["id"], trial, "re")]
                candidate = grouped[(case["id"], trial, name)]
                values.append(math.log(baseline["ns_per_op"] / candidate["ns_per_op"]))
                baseline_memory.append(baseline["peak_traced_bytes"])
                candidate_memory.append(candidate["peak_traced_bytes"])
            low, high = interval(values, rng, suite.BOOTSTRAPS)
            speed = math.exp(statistics.fmean(values))
            results.append({"case": case["id"], "cohort": case["cohort"], "category": case["category"], "candidate": name, "weight": case["weight"], "speedup": speed, "ci95_low": low, "ci95_high": high, "peak_traced_ratio": statistics.median(candidate_memory) / max(1, statistics.median(baseline_memory)), "statistically_faster": low > 1, "regression_gt_20pct": speed < .8})
            logs[(case["id"], name)] = values
    rankings = []
    for cohort in ("calibration", "holdout", "all"):
        selected = [case for case in cases if cohort == "all" or case["cohort"] == cohort]
        denominator = sum(case["weight"] for case in selected)
        wanted = suite.CASES_PER_COHORT * (2 if cohort == "all" else 1)
        if denominator != wanted:
            raise RuntimeError(f"ranking denominator drift: {cohort} {denominator} != {wanted}")
        for name in candidates:
            point = math.exp(sum(statistics.fmean(logs[(case["id"], name)]) * case["weight"] for case in selected) / denominator)
            boots = []
            for _ in range(suite.BOOTSTRAPS):
                total = 0
                for case in selected:
                    values = logs[(case["id"], name)]
                    total += statistics.fmean(values[rng.randrange(len(values))] for _ in values) * case["weight"]
                boots.append(total / denominator)
            relevant = [row for row in results if row["candidate"] == name and (cohort == "all" or row["cohort"] == cohort)]
            rankings.append({"cohort": cohort, "candidate": name, "cases": len(selected), "weight": denominator, "geomean_speedup": point, "ci95_low": math.exp(percentile(boots, .025)), "ci95_high": math.exp(percentile(boots, .975)), "statistically_faster_cases": sum(row["statistically_faster"] for row in relevant), "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in relevant)})
    summary = {"schema": "rebar-performance-summary-v6", "expected_sha256": manifest["expected_sha256"], "raw_sha256": hashlib.sha256(payload).hexdigest(), "rows": len(rows), "rankings": rankings, "case_results": results, "regressions": [row for row in results if row["regression_gt_20pct"]]}
    Path(args.output).write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "cases": len(cases), "results": len(results), "regressions": len(summary["regressions"]), "output": args.output}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(required=True)
    freeze_parser = commands.add_parser("freeze")
    freeze_parser.set_defaults(function=freeze)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--module", action="append")
    verify_parser.add_argument("--output")
    verify_parser.set_defaults(function=verify)
    measure_parser = commands.add_parser("measure")
    measure_parser.add_argument("--output", required=True)
    measure_parser.set_defaults(function=measure)
    analyze_parser = commands.add_parser("analyze")
    analyze_parser.add_argument("--input", required=True)
    analyze_parser.add_argument("--output", required=True)
    analyze_parser.set_defaults(function=analyze)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
