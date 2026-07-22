#!/usr/bin/env python3
"""Correctness-gated allocation and end-to-end timing probe for the Zig engine."""

import argparse
import gc
import json
import math
import random
import re
import statistics
import time
import tracemalloc
from pathlib import Path

import candidates.zig_candidate as zig


CASES = [
    ("short-findall-miss", "findall", r"missing", "ordinary short text", {}),
    ("long-findall-miss", "findall", r"missing", "ordinary text " * 4096, {}),
    ("long-findall-sparse", "findall", r"TOKEN_[0-9]+", "x" * 16384 + " TOKEN_17 " + "x" * 16384, {}),
    ("long-findall-dense", "findall", r"[A-Za-z]+|[0-9]+", "alpha17 beta29 gamma41 " * 256, {}),
    ("long-findall-captures", "findall", r"([A-Za-z]+)=([0-9]+)", "alpha=17 beta=29 gamma=41 " * 192, {}),
    ("long-finditer-sparse", "finditer", r"TOKEN_[0-9]+", "x" * 16384 + " TOKEN_17 " + "x" * 16384, {}),
    ("long-finditer-captures", "finditer", r"(?P<key>[A-Za-z]+)=(?P<num>[0-9]+)", "alpha=17 beta=29 gamma=41 " * 96, {}),
    ("long-split-miss", "split", r"[,;]", "ordinary text " * 4096, {}),
    ("long-split-sparse", "split", r"([,;])", "x" * 16384 + "," + "x" * 16384, {}),
    ("long-split-dense", "split", r"([,;])", "alpha,beta;gamma," * 256, {}),
    ("long-split-limited", "split", r"([,;])", "alpha,beta;gamma," * 256, {"maxsplit": 8}),
    ("long-sub-miss", "subn", r"missing", "ordinary text " * 4096, {"repl": "X"}),
    ("long-sub-sparse", "subn", r"TOKEN_([0-9]+)", "x" * 16384 + " TOKEN_17 " + "x" * 16384, {"repl": r"<\1>"}),
    ("long-sub-dense", "subn", r"([A-Za-z]+)=([0-9]+)", "alpha=17 beta=29 gamma=41 " * 160, {"repl": r"\2:\1"}),
    ("long-sub-limited", "subn", r"([A-Za-z]+)=([0-9]+)", "alpha=17 beta=29 gamma=41 " * 160, {"repl": r"\2:\1", "count": 8}),
    ("bytes-findall-sparse", "findall", rb"TOKEN_[0-9]+", b"x" * 16384 + b" TOKEN_17 " + b"x" * 16384, {}),
    ("bytes-findall-captures", "findall", rb"([A-Za-z]+)=([0-9]+)", b"alpha=17 beta=29 gamma=41 " * 192, {}),
    ("bytes-split-sparse", "split", rb"([,;])", b"x" * 16384 + b"," + b"x" * 16384, {}),
    ("bytes-sub-sparse", "subn", rb"TOKEN_([0-9]+)", b"x" * 16384 + b" TOKEN_17 " + b"x" * 16384, {"repl": rb"<\1>"}),
    ("empty-dense", "findall", r"|a", "a" * 512, {}),
]


def action(module, api, pattern, string, values):
    compiled = module.compile(pattern)
    if api == "finditer":
        return lambda: [(match.span(), match.groups(), match.lastindex) for match in compiled.finditer(string)]
    if api == "findall":
        return lambda: compiled.findall(string)
    if api == "split":
        return lambda: compiled.split(string, values.get("maxsplit", 0))
    if api == "subn":
        return lambda: compiled.subn(values["repl"], string, values.get("count", 0))
    raise ValueError(api)


def timed(function, operations):
    enabled = gc.isenabled()
    if enabled:
        gc.disable()
    try:
        started = time.perf_counter_ns()
        value = None
        for _ in range(operations):
            value = function()
        elapsed = time.perf_counter_ns() - started
    finally:
        if enabled:
            gc.enable()
    return elapsed / operations, value


def peak(function):
    tracemalloc.start()
    value = function()
    _, result = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--trials", type=int, default=7)
    parser.add_argument("--operations", type=int, default=24)
    args = parser.parse_args()
    if args.trials < 1 or args.operations < 1:
        raise ValueError("--trials and --operations must be positive")
    seed = 2026073017
    results = []
    checks = 0
    for index, (case, api, pattern, string, values) in enumerate(CASES):
        baseline = action(re, api, pattern, string, values)
        candidate = action(zig, api, pattern, string, values)
        expected = baseline()
        actual = candidate()
        checks += 1
        if actual != expected:
            raise RuntimeError(f"correctness mismatch before timing: {case}")
        memory = {}
        for label, function in (("re", baseline), ("zig", candidate)):
            memory[label], value = peak(function)
            checks += 1
            if value != expected:
                raise RuntimeError(f"correctness mismatch while tracing memory: {label} {case}")
        rows = []
        for trial in range(args.trials):
            order = ["re", "zig"]
            random.Random(seed + index * 1009 + trial).shuffle(order)
            row = {}
            for label in order:
                function = baseline if label == "re" else candidate
                function()
                elapsed, value = timed(function, args.operations)
                checks += 1
                if value != expected:
                    raise RuntimeError(f"correctness mismatch after timing: {label} {case}")
                row[label] = elapsed
            rows.append(row)
        speedups = [row["re"] / row["zig"] for row in rows]
        result = {"case": case, "api": api, "length": len(string), "operations": args.operations, "baseline_ns_median": statistics.median(row["re"] for row in rows), "zig_ns_median": statistics.median(row["zig"] for row in rows), "speedup": math.exp(statistics.fmean(math.log(value) for value in speedups)), "baseline_peak_bytes": memory["re"], "zig_peak_bytes": memory["zig"], "peak_ratio": memory["zig"] / max(1, memory["re"]), "rows": rows}
        results.append(result)
        print(f"{case}: {result['speedup']:.3f}×, peak {memory['zig']:,} vs {memory['re']:,} bytes ({result['peak_ratio']:.2f}×)")
    payload = {"schema": "rebar-zig-allocation-probe-v1", "seed": seed, "trials": args.trials, "operations": args.operations, "correctness_checks": checks, "failed": 0, "cases": len(results), "geomean_speedup": math.exp(statistics.fmean(math.log(item["speedup"]) for item in results)), "results": results}
    Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "results"}, sort_keys=True))


if __name__ == "__main__":
    main()
