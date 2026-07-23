#!/usr/bin/env python3
"""Collect correctness-gated Zig executor counters for selected v6 workloads."""

from __future__ import annotations

import argparse
import ctypes
import json
import statistics
from collections import defaultdict
from pathlib import Path

from candidates import zig_candidate as zig
from tools.perf_v6 import correctness_gate, frozen, operation, snapshot


FIELDS = ("bytecode_calls", "capture_calls", "search_starts", "steps", "splits", "class_checks", "collections", "equal_checks", "cached_class_checks", "runs", "cached_class_runs", "uncached_class_runs")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--category", action="append", required=True)
    args = parser.parse_args()
    _, cases, expected, manifest = frozen()
    wanted = set(args.category)
    selected = [(case, want) for case, want in zip(cases, expected, strict=True) if case["category"] in wanted]
    found = {case["category"] for case, _ in selected}
    if found != wanted:
        raise RuntimeError(f"unknown workload categories: {sorted(wanted - found)}")
    library = zig._NATIVE.library
    reset = library.rebar_zig_profile_reset
    reset.argtypes = []
    get = library.rebar_zig_profile_get
    get.argtypes = [ctypes.c_size_t]
    get.restype = ctypes.c_uint64
    rows = []
    for index, (case, want) in enumerate(selected):
        correctness_gate(zig, case, want)
        action = operation(zig, case)
        reset()
        result = action()
        if snapshot(result) != want["result"]:
            raise RuntimeError(f"post-profile mismatch: {case['id']}")
        row = {"case": case["id"], "cohort": case["cohort"], "category": case["category"], "api": case["api"], "flags": case.get("flags", []), "pattern_length": len(case["pattern"]), "subject_length": len(case.get("string") or "")}
        row.update((field, get(offset)) for offset, field in enumerate(FIELDS))
        rows.append(row)
        if index and index % 128 == 0:
            print(f"profiled {index}/{len(selected)}", flush=True)
    groups = defaultdict(list)
    for row in rows:
        groups[(row["cohort"], row["category"], "I" in row["flags"])].append(row)
    families = []
    for (cohort, category, ignore_case), members in sorted(groups.items()):
        value = {"cohort": cohort, "category": category, "ignore_case": ignore_case, "cases": len(members)}
        for field in FIELDS:
            values = [row[field] for row in members]
            value[field + "_median"] = round(statistics.median(values))
            value[field + "_maximum"] = max(values)
        families.append(value)
        if cohort == "holdout":
            print(f"{category:<40} I={str(ignore_case):<5} calls={value['bytecode_calls_median']}/{value['capture_calls_median']} starts={value['search_starts_median']} steps={value['steps_median']} splits={value['splits_median']} classes={value['class_checks_median']}/{value['cached_class_checks_median']} equal={value['equal_checks_median']} runs={value['runs_median']} cached/slow={value['cached_class_runs_median']}/{value['uncached_class_runs_median']} collect={value['collections_median']}")
    result = {"schema": "rebar-zig-profile-v6", "expected_sha256": manifest["expected_sha256"], "categories": sorted(wanted), "cases": len(rows), "correctness_checks": len(rows) * 2, "fields": list(FIELDS), "families": families, "rows": rows}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in {"families", "rows"}}, sort_keys=True))


if __name__ == "__main__":
    main()
