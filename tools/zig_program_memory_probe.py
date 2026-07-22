#!/usr/bin/env python3
"""Measure real Zig compiled-program allocation on every frozen performance task."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from candidates import zig_candidate as zig
from tools.perf_v5 import flags, frozen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    _, cases, _, manifest = frozen()
    library = zig._NATIVE.library
    rows = []
    for index, case in enumerate(cases):
        if index % 512 == 0:
            print(f"checking program memory {index}/{len(cases)}", flush=True)
        zig.purge()
        compiled = zig.compile(case["pattern"], flags(zig, case["flags"]))
        rows.append({"case": case["id"], "cohort": case["cohort"], "category": case["category"], "pattern_length": len(case["pattern"]), "groups": compiled.groups, "program_bytes": library.rebar_zig_program_memory(compiled._handle)})
    zig.purge()
    families = []
    for cohort in ("calibration", "holdout", "all"):
        selected = [row for row in rows if cohort == "all" or row["cohort"] == cohort]
        for category in sorted({row["category"] for row in selected}):
            values = [row["program_bytes"] for row in selected if row["category"] == category]
            families.append({"cohort": cohort, "category": category, "cases": len(values), "minimum_bytes": min(values), "median_bytes": round(statistics.median(values)), "maximum_bytes": max(values)})
    values = [row["program_bytes"] for row in rows]
    result = {"schema": "rebar-zig-program-memory-v1", "expected_sha256": manifest["expected_sha256"], "cases": len(rows), "header_bytes": library.rebar_zig_program_size(), "minimum_bytes": min(values), "median_bytes": round(statistics.median(values)), "maximum_bytes": max(values), "families": families, "rows": rows}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in {"families", "rows"}}, sort_keys=True))


if __name__ == "__main__":
    main()
