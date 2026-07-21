#!/usr/bin/env python3
"""Freeze, correctness-gate, measure, and analyze the versioned performance oracle."""

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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "performance" / "v1" / "suite.py"
EXPECTED = ROOT / "performance" / "v1" / "expected.jsonl"
MANIFEST = ROOT / "performance" / "v1" / "manifest.json"
CORRECTNESS = ROOT / "oracle" / "v1" / "manifest.json"
GOAL_HASH = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"


def suite_module():
    spec = importlib.util.spec_from_file_location("rebar_performance_v1", SUITE_PATH)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def jsonable(value):
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in sorted(value.items(), key=lambda x: str(x[0]))}
    return value


def flags(module, names):
    value = 0
    for name in names:
        value |= int(getattr(module, name))
    return value


def replacement(case):
    value = case.get("repl")
    if not isinstance(value, dict):
        return value
    if value["callable"] == "upper_bracket":
        return lambda match: "[" + match.group(0).upper() + "]"
    if value["callable"] == "lower_bracket":
        return lambda match: "[" + match.group(0).lower() + "]"
    raise RuntimeError(f"unknown callable replacement {value['callable']}")


def snapshot(value):
    if value is None:
        return None
    if hasattr(value, "group") and hasattr(value, "span"):
        return {"span": jsonable(value.span()), "groups": jsonable(value.groups()), "groupdict": jsonable(value.groupdict()), "lastindex": value.lastindex, "lastgroup": value.lastgroup}
    if isinstance(value, list):
        return [snapshot(item) for item in value]
    if isinstance(value, tuple):
        return [snapshot(item) for item in value]
    if hasattr(value, "__next__"):
        return [snapshot(item) for item in value]
    return jsonable(value)


def operation(module, case):
    flag_value = flags(module, case["flags"])
    api = case["api"]
    lifecycle = case["lifecycle"]
    repl = replacement(case)
    kwargs = {}
    if api in {"sub", "subn"}:
        kwargs["count"] = case.get("count", 0)
    if api == "split":
        kwargs["maxsplit"] = case.get("maxsplit", 0)
    if lifecycle == "compiled":
        function = getattr(module.compile(case["pattern"], flag_value), api)
        if api in {"sub", "subn"}:
            return lambda: function(repl, case["string"], **kwargs)
        if api == "finditer":
            return lambda: list(function(case["string"], **kwargs))
        return lambda: function(case["string"], **kwargs)
    function = getattr(module, api)
    if lifecycle == "module":
        if api in {"sub", "subn"}:
            return lambda: function(case["pattern"], repl, case["string"], flags=flag_value, **kwargs)
        if api == "finditer":
            return lambda: list(function(case["pattern"], case["string"], flags=flag_value, **kwargs))
        return lambda: function(case["pattern"], case["string"], flags=flag_value, **kwargs)
    if lifecycle == "cold":
        def cold():
            module.purge()
            if api in {"sub", "subn"}:
                return function(case["pattern"], repl, case["string"], flags=flag_value, **kwargs)
            if api == "finditer":
                return list(function(case["pattern"], case["string"], flags=flag_value, **kwargs))
            return function(case["pattern"], case["string"], flags=flag_value, **kwargs)
        return cold
    raise RuntimeError(f"unknown lifecycle {lifecycle}")


def validate_suite(cases):
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate performance case IDs")
    cohorts = {name: [case for case in cases if case["cohort"] == name] for name in ("calibration", "holdout")}
    if any(len(values) != 16 for values in cohorts.values()):
        raise RuntimeError(f"performance cohort count drift: {[(name, len(values)) for name, values in cohorts.items()]}")
    if any(sum(case["weight"] for case in values) != 16 for values in cohorts.values()):
        raise RuntimeError("performance cohort weight drift")
    if {case["category"] for case in cohorts["calibration"]} != {case["category"] for case in cohorts["holdout"]}:
        raise RuntimeError("calibration and holdout categories differ")
    if any(case["ops"] <= 0 or case["weight"] <= 0 for case in cases):
        raise RuntimeError("non-positive operation count or weight")
    if hashlib.sha256((ROOT / "GOAL.md").read_bytes()).hexdigest() != GOAL_HASH:
        raise RuntimeError("GOAL.md hash changed")
    correctness = json.loads(CORRECTNESS.read_text(encoding="utf-8"))
    if correctness["schema"] != "rebar-correctness-v1.1" or correctness["cases"] != 2048 or correctness["mapped_obligations"] != 38:
        raise RuntimeError("correctness oracle is not the frozen qualified v1.1")
    return correctness


def runtime():
    if platform.python_implementation() != "CPython" or sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError(f"performance oracle requires CPython 3.14.6, got {platform.python_implementation()} {sys.version.split()[0]}")


def records_for(module, cases):
    for case in cases:
        result = snapshot(operation(module, case)())
        encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        yield {"id": case["id"], "cohort": case["cohort"], "category": case["category"], "result": result, "result_sha256": hashlib.sha256(encoded).hexdigest()}


def freeze(_args):
    runtime()
    suite = suite_module()
    cases = suite.cases()
    correctness = validate_suite(cases)
    baseline = importlib.import_module("re")
    first = list(records_for(baseline, cases))
    baseline.purge()
    second = list(records_for(baseline, cases))
    if first != second:
        raise RuntimeError("non-deterministic stdlib performance fixture")
    payload = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in first).encode("utf-8")
    EXPECTED.parent.mkdir(parents=True, exist_ok=True)
    EXPECTED.write_bytes(payload)
    manifest = {"schema": "rebar-performance-v1", "python": "3.14.6", "implementation": "CPython", "goal_sha256": GOAL_HASH, "correctness_expected_sha256": correctness["expected_sha256"], "suite_sha256": hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "expected_sha256": hashlib.sha256(payload).hexdigest(), "modules": suite.MODULES, "cases": len(cases), "cohorts": {"calibration": 16, "holdout": 16}, "weights": {"calibration": 16, "holdout": 16}, "trials": suite.TRIALS, "warmups": suite.WARMUPS, "order_seed": suite.ORDER_SEED, "bootstrap_seed": suite.BOOTSTRAP_SEED, "bootstraps": suite.BOOTSTRAPS}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


def frozen():
    runtime()
    suite = suite_module()
    cases = suite.cases()
    correctness = validate_suite(cases)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload = EXPECTED.read_bytes()
    checks = [("suite", hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), manifest["suite_sha256"]), ("runner", hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), manifest["runner_sha256"]), ("expected", hashlib.sha256(payload).hexdigest(), manifest["expected_sha256"]), ("correctness", correctness["expected_sha256"], manifest["correctness_expected_sha256"])]
    if any(got != want for _, got, want in checks):
        raise RuntimeError(f"performance freeze drift: {checks}")
    expected = [json.loads(line) for line in payload.splitlines()]
    if len(expected) != len(cases) or manifest["cases"] != len(cases):
        raise RuntimeError("performance case count drift")
    return suite, cases, expected, manifest


def correctness_gate(module, case, expected):
    result = snapshot(operation(module, case)())
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    if digest != expected["result_sha256"] or result != expected["result"]:
        raise RuntimeError(f"performance correctness mismatch: {module.__name__} {case['id']}")
    return digest


def verify(args):
    suite, cases, expected, manifest = frozen()
    names = args.module or suite.MODULES
    failures = []
    for name in names:
        module = importlib.import_module(name)
        for case, want in zip(cases, expected, strict=True):
            try:
                correctness_gate(module, case, want)
            except BaseException as error:
                failures.append({"module": name, "case": case["id"], "type": type(error).__name__, "message": str(error)})
    result = {"schema": "rebar-performance-correctness-v1", "modules": names, "cases_per_module": len(cases), "checks": len(cases) * len(names), "failed": len(failures), "expected_sha256": manifest["expected_sha256"], "failures": failures}
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        raise SystemExit(1)


def proc_memory():
    result = {"rss_kb": None, "hwm_kb": None}
    try:
        for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                result["rss_kb"] = int(line.split()[1])
            if line.startswith("VmHWM:"):
                result["hwm_kb"] = int(line.split()[1])
    except OSError:
        pass
    return result


def measure(args):
    suite, cases, expected, manifest = frozen()
    modules = {name: importlib.import_module(name) for name in suite.MODULES}
    rows = []
    for case, want in zip(cases, expected, strict=True):
        for trial in range(suite.TRIALS):
            order = list(suite.MODULES)
            rng = random.Random(suite.ORDER_SEED + trial * 1009 + sum(ord(char) for char in case["id"]))
            rng.shuffle(order)
            for order_index, name in enumerate(order):
                module = modules[name]
                digest = correctness_gate(module, case, want)
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
                started = time.perf_counter_ns()
                sink = None
                for _ in range(case["ops"]):
                    sink = action()
                elapsed = time.perf_counter_ns() - started
                if enabled:
                    gc.enable()
                after = proc_memory()
                if sink is None and want["result"] is not None:
                    raise RuntimeError(f"timed result disappeared: {name} {case['id']}")
                rows.append({"schema": "rebar-performance-row-v1", "case": case["id"], "cohort": case["cohort"], "category": case["category"], "module": name, "trial": trial, "order": order_index, "ops": case["ops"], "elapsed_ns": elapsed, "ns_per_op": elapsed / case["ops"], "peak_traced_bytes": peak, "rss_before_kb": before["rss_kb"], "rss_after_kb": after["rss_kb"], "hwm_kb": after["hwm_kb"], "expected_sha256": digest})
        print(f"measured {case['id']} ({case['ops']} ops x {suite.TRIALS} paired trials)")
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")
    required = len(cases) * len(suite.MODULES) * suite.TRIALS
    if len(rows) != required:
        raise RuntimeError(f"raw row count drift: {len(rows)} != {required}")
    print(json.dumps({"rows": len(rows), "cases": len(cases), "modules": len(suite.MODULES), "trials": suite.TRIALS, "output": str(target), "manifest": manifest["expected_sha256"]}, sort_keys=True))


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, math.floor(fraction * (len(ordered) - 1))))]


def interval(values, rng, samples):
    means = [statistics.fmean(values[rng.randrange(len(values))] for _ in values) for _ in range(samples)]
    return math.exp(percentile(means, 0.025)), math.exp(percentile(means, 0.975))


def analyze(args):
    suite, cases, expected, manifest = frozen()
    payload = Path(args.input).read_bytes()
    rows = [json.loads(line) for line in payload.splitlines()]
    required = len(cases) * len(suite.MODULES) * suite.TRIALS
    if len(rows) != required:
        raise RuntimeError(f"raw row count drift: {len(rows)} != {required}")
    grouped = {}
    for row in rows:
        key = (row["case"], row["trial"], row["module"])
        if key in grouped:
            raise RuntimeError(f"duplicate raw row {key}")
        grouped[key] = row
    if len(grouped) != required:
        raise RuntimeError("missing raw rows")
    expected_by_id = {item["id"]: item["result_sha256"] for item in expected}
    if any(row["expected_sha256"] != expected_by_id[row["case"]] for row in rows):
        raise RuntimeError("raw correctness digest drift")
    rng = random.Random(suite.BOOTSTRAP_SEED)
    candidates = suite.MODULES[1:]
    case_rows = []
    logs = {}
    for case in cases:
        for name in candidates:
            values = [math.log(grouped[(case["id"], trial, "re")]["ns_per_op"] / grouped[(case["id"], trial, name)]["ns_per_op"]) for trial in range(suite.TRIALS)]
            low, high = interval(values, rng, suite.BOOTSTRAPS)
            base_mem = [grouped[(case["id"], trial, "re")]["peak_traced_bytes"] for trial in range(suite.TRIALS)]
            cand_mem = [grouped[(case["id"], trial, name)]["peak_traced_bytes"] for trial in range(suite.TRIALS)]
            speedup = math.exp(statistics.fmean(values))
            case_rows.append({"case": case["id"], "cohort": case["cohort"], "category": case["category"], "candidate": name, "weight": case["weight"], "speedup": speedup, "ci95_low": low, "ci95_high": high, "statistically_faster": low > 1, "regression_gt_20pct": speedup < 0.8, "baseline_peak_traced_bytes_median": statistics.median(base_mem), "candidate_peak_traced_bytes_median": statistics.median(cand_mem), "peak_traced_ratio": statistics.median(cand_mem) / max(statistics.median(base_mem), 1)})
            logs[(case["id"], name)] = values
    rankings = []
    for cohort in ("calibration", "holdout", "all"):
        selected = [case for case in cases if cohort == "all" or case["cohort"] == cohort]
        denominator = sum(case["weight"] for case in selected)
        for name in candidates:
            point = math.exp(sum(statistics.fmean(logs[(case["id"], name)]) * case["weight"] for case in selected) / denominator)
            boot = []
            for _ in range(suite.BOOTSTRAPS):
                total = 0
                for case in selected:
                    values = logs[(case["id"], name)]
                    total += statistics.fmean(values[rng.randrange(len(values))] for _ in values) * case["weight"]
                boot.append(total / denominator)
            relevant = [row for row in case_rows if row["candidate"] == name and (cohort == "all" or row["cohort"] == cohort)]
            faster = sum(row["statistically_faster"] for row in relevant)
            rankings.append({"cohort": cohort, "candidate": name, "cases": len(selected), "weight": denominator, "geomean_speedup": point, "ci95_low": math.exp(percentile(boot, 0.025)), "ci95_high": math.exp(percentile(boot, 0.975)), "statistically_faster_cases": faster, "statistically_faster_fraction": faster / len(relevant), "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in relevant)})
    result = {"schema": "rebar-performance-summary-v1", "raw_sha256": hashlib.sha256(payload).hexdigest(), "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), "expected_sha256": manifest["expected_sha256"], "rows": len(rows), "case_results": case_rows, "rankings": rankings, "regressions": [row for row in case_rows if row["regression_gt_20pct"]]}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "cases": len(case_rows), "regressions": len(result["regressions"]), "output": args.output}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("freeze").set_defaults(function=freeze)
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
