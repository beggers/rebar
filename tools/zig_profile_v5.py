#!/usr/bin/env python3
"""Collect correctness-gated Zig executor counters for the frozen performance matrix."""

from __future__ import annotations

import argparse
import ctypes
import json
import statistics
from pathlib import Path

from candidates import zig_candidate as zig
from tools.perf_v5 import correctness_gate, frozen, operation, snapshot


FIELDS = ("bytecode_calls", "capture_calls", "search_starts", "steps", "splits", "class_checks", "collections")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    _, cases, expected, manifest = frozen()
    library = zig._NATIVE.library
    try:
        reset = library.rebar_zig_profile_reset
        get = library.rebar_zig_profile_get
    except AttributeError as error:
        raise RuntimeError("build the temporary instrumented Zig matcher before profiling") from error
    reset.argtypes = []
    get.argtypes = [ctypes.c_size_t]
    get.restype = ctypes.c_uint64
    rows = []
    for index, (case, want) in enumerate(zip(cases, expected, strict=True)):
        if index % 512 == 0:
            print(f"profiling {index}/{len(cases)}", flush=True)
        correctness_gate(zig, case, want)
        action = operation(zig, case)
        reset()
        result = action()
        if snapshot(result) != want["result"]:
            raise RuntimeError(f"post-profile mismatch: {case['id']}")
        row = {"case": case["id"], "cohort": case["cohort"], "category": case["category"], "api": case["api"], "pattern_length": len(case["pattern"]), "subject_length": len(case.get("string") or "")}
        row.update((field, get(offset)) for offset, field in enumerate(FIELDS))
        rows.append(row)
    families = []
    for cohort in ("calibration", "holdout", "all"):
        selected = [row for row in rows if cohort == "all" or row["cohort"] == cohort]
        for category in sorted({row["category"] for row in selected}):
            members = [row for row in selected if row["category"] == category]
            family = {"cohort": cohort, "category": category, "cases": len(members)}
            for field in FIELDS:
                values = [row[field] for row in members]
                family[field + "_median"] = round(statistics.median(values))
                family[field + "_maximum"] = max(values)
            families.append(family)
    result = {"schema": "rebar-zig-profile-v5", "expected_sha256": manifest["expected_sha256"], "cases": len(rows), "correctness_checks": len(rows) * 2, "fields": list(FIELDS), "families": families, "rows": rows}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in {"families", "rows"}}, sort_keys=True))


if __name__ == "__main__":
    main()
