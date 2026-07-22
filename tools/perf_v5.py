#!/usr/bin/env python3
"""Freeze, correctness-gate, measure, and analyze the expanded performance holdout."""

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


ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "performance" / "v5" / "suite.py"
EXPECTED = ROOT / "performance" / "v5" / "expected.jsonl"
MANIFEST = ROOT / "performance" / "v5" / "manifest.json"
PARENT_SUITE = ROOT / "performance" / "v4" / "suite.py"
PARENT_EXPECTED = ROOT / "performance" / "v4" / "expected.jsonl"
PARENT_MANIFEST = ROOT / "performance" / "v4" / "manifest.json"
CORRECTNESS = ROOT / "oracle" / "v3" / "manifest.json"
GOAL_HASH = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"


def suite_module():
    spec = importlib.util.spec_from_file_location("rebar_performance_v5", SUITE_PATH)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def jsonable(value):
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"bytes_hex": bytes(value).hex()}
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    return value


def flags(module, names):
    result = 0
    for name in names:
        result |= int(getattr(module, name))
    return result


def materialize(value, kind):
    if kind in (None, "bytes", "text"):
        return value
    if kind == "bytearray":
        return bytearray(value)
    if kind == "memoryview":
        return memoryview(value)
    raise RuntimeError(f"unknown input kind: {kind}")


def replacement(case):
    value = case.get("repl")
    if not isinstance(value, dict):
        return materialize(value, case.get("replacement_kind"))
    if value["callable"] == "upper_bracket":
        return lambda match: "[" + match.group(0).upper() + "]"
    if value["callable"] == "lower_bracket":
        return lambda match: "[" + match.group(0).lower() + "]"
    raise RuntimeError(f"unknown callable replacement: {value['callable']}")


def snapshot(value):
    if value is None:
        return None
    if hasattr(value, "group") and hasattr(value, "span"):
        return {"span": jsonable(value.span()), "groups": jsonable(value.groups()), "groupdict": jsonable(value.groupdict()), "lastindex": value.lastindex, "lastgroup": value.lastgroup}
    if hasattr(value, "pattern") and hasattr(value, "findall"):
        return {"pattern": jsonable(value.pattern), "flags": value.flags, "groups": value.groups, "groupindex": jsonable(dict(value.groupindex))}
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
    pattern = case["pattern"]
    subject = materialize(case.get("string"), case.get("subject_kind"))
    repl = replacement(case)
    if api == "escape":
        return lambda: module.escape(pattern)
    if api == "compile":
        if lifecycle != "cold":
            raise RuntimeError("compile benchmark must be cold")

        def cold_compile():
            module.purge()
            return module.compile(pattern, flag_value)

        return cold_compile
    if api in {"scanner", "match-surface"}:
        compiled = module.compile(pattern, flag_value)
        if api == "scanner":

            def scan():
                if "pos" in case or "endpos" in case:
                    scanner = compiled.scanner(subject, case.get("pos", 0), case.get("endpos", sys.maxsize))
                else:
                    scanner = compiled.scanner(subject)
                result = []
                while True:
                    item = scanner.search()
                    if item is None:
                        return result
                    result.append(item)

            return scan

        def surface():
            item = compiled.search(subject)
            if item is None:
                return None
            return (item.group(0), item.groups(), item.groupdict(), item.regs, item.lastgroup, item.expand(case["expand"]))

        return surface
    kwargs = {}
    if api in {"sub", "subn"}:
        kwargs["count"] = case.get("count", 0)
    if api == "split":
        kwargs["maxsplit"] = case.get("maxsplit", 0)
    if api in {"search", "match", "fullmatch", "findall", "finditer"} and lifecycle == "compiled":
        if "pos" in case:
            kwargs["pos"] = case["pos"]
        if "endpos" in case:
            kwargs["endpos"] = case["endpos"]
    if lifecycle == "compiled":
        function = getattr(module.compile(pattern, flag_value), api)
        if api in {"sub", "subn"}:
            return lambda: function(repl, subject, **kwargs)
        if api == "finditer":
            return lambda: list(function(subject, **kwargs))
        return lambda: function(subject, **kwargs)
    function = getattr(module, api)
    if lifecycle == "module":
        if api in {"sub", "subn"}:
            return lambda: function(pattern, repl, subject, flags=flag_value, **kwargs)
        if api == "finditer":
            return lambda: list(function(pattern, subject, flags=flag_value, **kwargs))
        return lambda: function(pattern, subject, flags=flag_value, **kwargs)
    if lifecycle == "cold":

        def cold():
            module.purge()
            if api in {"sub", "subn"}:
                return function(pattern, repl, subject, flags=flag_value, **kwargs)
            if api == "finditer":
                return list(function(pattern, subject, flags=flag_value, **kwargs))
            return function(pattern, subject, flags=flag_value, **kwargs)

        return cold
    raise RuntimeError(f"unknown lifecycle: {lifecycle}")


def runtime():
    if platform.python_implementation() != "CPython" or sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError(f"performance oracle requires CPython 3.14.6, got {platform.python_implementation()} {sys.version.split()[0]}")


def source_kind(case):
    value = case.get("string")
    if value is None:
        value = case["pattern"]
    if isinstance(value, bytes):
        return case.get("subject_kind", "bytes")
    return "text"


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
    expected_large = len(suite.FAMILIES) * suite.VARIANTS
    for cohort, values in cohorts.items():
        generated = [case for case in values if ".expanded." in case["id"]]
        counts = Counter(case["category"] for case in generated)
        if len(generated) != expected_large or set(counts) != {f"expanded-{name}" for name in suite.FAMILIES} or any(value != suite.VARIANTS for value in counts.values()):
            raise RuntimeError(f"expanded performance family count drift: {cohort} {dict(sorted(counts.items()))}")
    if hashlib.sha256((ROOT / "GOAL.md").read_bytes()).hexdigest() != GOAL_HASH:
        raise RuntimeError("GOAL.md hash changed")
    correctness = json.loads(CORRECTNESS.read_text(encoding="utf-8"))
    if correctness["schema"] != "rebar-correctness-v3" or correctness["cases"] != 44084 or correctness["mapped_obligations"] != 51:
        raise RuntimeError("large correctness oracle is not frozen and qualified")
    parent = json.loads(PARENT_MANIFEST.read_text(encoding="utf-8"))
    parent_checks = (("schema", parent["schema"], "rebar-performance-v4"), ("cases", parent["cases"], 2448), ("suite", hashlib.sha256(PARENT_SUITE.read_bytes()).hexdigest(), parent["suite_sha256"]), ("expected", hashlib.sha256(PARENT_EXPECTED.read_bytes()).hexdigest(), parent["expected_sha256"]))
    if any(got != want for _, got, want in parent_checks):
        raise RuntimeError(f"parent performance freeze drift: {parent_checks}")
    return correctness, parent


def digest(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def records_for(module, cases):
    for case in cases:
        result = snapshot(operation(module, case)())
        yield {"id": case["id"], "cohort": case["cohort"], "category": case["category"], "result": result, "result_sha256": digest(result)}


def encode(records):
    return "".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in records).encode("utf-8")


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
    parent_payload = PARENT_EXPECTED.read_bytes()
    if encode(first[: parent["cases"]]) != parent_payload:
        raise RuntimeError("expanded performance fixture does not preserve the frozen v4 prefix")
    EXPECTED.parent.mkdir(parents=True, exist_ok=True)
    EXPECTED.write_bytes(payload)
    manifest = {"schema": "rebar-performance-v5", "python": "3.14.6", "implementation": "CPython", "goal_sha256": GOAL_HASH, "correctness_expected_sha256": correctness["expected_sha256"], "parent_expected_sha256": parent["expected_sha256"], "parent_cases": parent["cases"], "suite_sha256": hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "expected_sha256": hashlib.sha256(payload).hexdigest(), "modules": suite.MODULES, "cases": len(cases), "cohorts": {"calibration": suite.CASES_PER_COHORT, "holdout": suite.CASES_PER_COHORT}, "weights": {"calibration": suite.CASES_PER_COHORT, "holdout": suite.CASES_PER_COHORT}, "expanded_families": len(suite.FAMILIES), "variants_per_family": suite.VARIANTS, "seeds": dict(sorted(suite.SEEDS.items())), "api_counts": dict(sorted(Counter(case["api"] for case in cases).items())), "lifecycle_counts": dict(sorted(Counter(case["lifecycle"] for case in cases).items())), "input_counts": dict(sorted(Counter(source_kind(case) for case in cases).items())), "trials": suite.TRIALS, "warmups": suite.WARMUPS, "order_seed": suite.ORDER_SEED, "bootstrap_seed": suite.BOOTSTRAP_SEED, "bootstraps": suite.BOOTSTRAPS}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


def frozen():
    runtime()
    suite = suite_module()
    cases = suite.cases()
    correctness, parent = validate_suite(suite, cases)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload = EXPECTED.read_bytes()
    checks = (("suite", hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), manifest["suite_sha256"]), ("runner", hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), manifest["runner_sha256"]), ("expected", hashlib.sha256(payload).hexdigest(), manifest["expected_sha256"]), ("correctness", correctness["expected_sha256"], manifest["correctness_expected_sha256"]), ("parent", parent["expected_sha256"], manifest["parent_expected_sha256"]))
    if any(got != want for _, got, want in checks):
        raise RuntimeError(f"performance freeze drift: {checks}")
    expected = [json.loads(line) for line in payload.splitlines()]
    if len(expected) != len(cases) or manifest["cases"] != len(cases):
        raise RuntimeError("performance case count drift")
    if encode(expected[: parent["cases"]]) != PARENT_EXPECTED.read_bytes():
        raise RuntimeError("frozen v4 performance prefix changed")
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
        for case, want in zip(cases, expected, strict=True):
            try:
                correctness_gate(module, case, want)
            except BaseException as error:
                failures.append({"module": name, "case": case["id"], "type": type(error).__name__, "message": str(error)})
    result = {"schema": "rebar-performance-correctness-v5", "modules": names, "cases_per_module": len(cases), "checks": len(cases) * len(names), "failed": len(failures), "expected_sha256": manifest["expected_sha256"], "failures": failures}
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        for failure in failures[:30]:
            print(f"{failure['module']} {failure['case']}: {failure['type']}: {failure['message']}", file=sys.stderr)
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
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with target.open("w", encoding="utf-8") as stream:
        for case, want in zip(cases, expected, strict=True):
            for trial in range(suite.TRIALS):
                order = list(suite.MODULES)
                random.Random(suite.ORDER_SEED + trial * 1009 + sum(ord(char) for char in case["id"])).shuffle(order)
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
                    started = time.perf_counter_ns()
                    sink = None
                    for _ in range(case["ops"]):
                        sink = action()
                    elapsed = time.perf_counter_ns() - started
                    if enabled:
                        gc.enable()
                    after = proc_memory()
                    timed_result = snapshot(sink)
                    if digest(timed_result) != expected_digest or timed_result != want["result"]:
                        raise RuntimeError(f"post-timing correctness mismatch: {name} {case['id']}")
                    row = {"schema": "rebar-performance-row-v5", "case": case["id"], "cohort": case["cohort"], "category": case["category"], "module": name, "trial": trial, "order": order_index, "ops": case["ops"], "elapsed_ns": elapsed, "ns_per_op": elapsed / case["ops"], "peak_traced_bytes": peak, "rss_before_kb": before["rss_kb"], "rss_after_kb": after["rss_kb"], "hwm_kb": after["hwm_kb"], "expected_sha256": expected_digest}
                    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
                    rows += 1
            print(f"measured {case['id']} ({case['ops']} operations × {suite.TRIALS} paired trials)", flush=True)
    required = len(cases) * len(suite.MODULES) * suite.TRIALS
    if rows != required:
        raise RuntimeError(f"raw row count drift: {rows} != {required}")
    print(json.dumps({"rows": rows, "cases": len(cases), "modules": len(suite.MODULES), "trials": suite.TRIALS, "output": str(target), "manifest": manifest["expected_sha256"]}, sort_keys=True))


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
    case_by_id = {case["id"]: case for case in cases}
    expected_by_id = {item["id"]: item["result_sha256"] for item in expected}
    grouped = {}
    for row in rows:
        key = (row["case"], row["trial"], row["module"])
        if key in grouped:
            raise RuntimeError(f"duplicate raw row: {key}")
        case = case_by_id.get(row["case"])
        if case is None or row["module"] not in suite.MODULES or not 0 <= row["trial"] < suite.TRIALS or row["schema"] != "rebar-performance-row-v5" or row["cohort"] != case["cohort"] or row["category"] != case["category"] or row["ops"] != case["ops"] or row["expected_sha256"] != expected_by_id[row["case"]]:
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
            speedup = math.exp(statistics.fmean(values))
            memory_ratio = statistics.median(candidate_memory) / max(1, statistics.median(baseline_memory))
            row = {"case": case["id"], "cohort": case["cohort"], "category": case["category"], "candidate": name, "weight": case["weight"], "speedup": speedup, "ci95_low": low, "ci95_high": high, "peak_traced_ratio": memory_ratio, "statistically_faster": low > 1, "regression_gt_20pct": speedup < 0.8}
            results.append(row)
            logs[(case["id"], name)] = values
    rankings = []
    for cohort in ("calibration", "holdout", "all"):
        selected = [case for case in cases if cohort == "all" or case["cohort"] == cohort]
        denominator = sum(case["weight"] for case in selected)
        expected_weight = suite.CASES_PER_COHORT * (2 if cohort == "all" else 1)
        if denominator != expected_weight:
            raise RuntimeError(f"ranking denominator drift: {cohort} {denominator} != {expected_weight}")
        for name in candidates:
            point = math.exp(sum(statistics.fmean(logs[(case["id"], name)]) * case["weight"] for case in selected) / denominator)
            boot = []
            for _ in range(suite.BOOTSTRAPS):
                total = 0
                for case in selected:
                    values = logs[(case["id"], name)]
                    total += statistics.fmean(values[rng.randrange(len(values))] for _ in values) * case["weight"]
                boot.append(total / denominator)
            relevant = [row for row in results if row["candidate"] == name and (cohort == "all" or row["cohort"] == cohort)]
            faster = sum(row["statistically_faster"] for row in relevant)
            rankings.append({"cohort": cohort, "candidate": name, "cases": len(selected), "weight": denominator, "geomean_speedup": point, "ci95_low": math.exp(percentile(boot, 0.025)), "ci95_high": math.exp(percentile(boot, 0.975)), "statistically_faster_cases": faster, "statistically_faster_fraction": faster / len(relevant), "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in relevant)})
    result = {"schema": "rebar-performance-summary-v5", "raw_sha256": hashlib.sha256(payload).hexdigest(), "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), "expected_sha256": manifest["expected_sha256"], "rows": len(rows), "case_results": results, "rankings": rankings, "regressions": [row for row in results if row["regression_gt_20pct"]]}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "cases": len(results), "regressions": len(result["regressions"]), "output": args.output}, sort_keys=True))


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
