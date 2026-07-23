#!/usr/bin/env python3
"""Combine the frozen five-engine comparison with the latest paired Zig rerun."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path


ZIG = "candidates.zig_candidate"


def read(path):
    target = Path(path)
    opener = gzip.open if target.suffix == ".gz" else open
    with opener(target, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial", required=True)
    parser.add_argument("--zig", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    initial = read(args.initial)
    latest = read(args.zig)
    if initial["expected_sha256"] != latest["expected_sha256"]:
        raise RuntimeError("performance fixtures differ")
    if {row["candidate"] for row in latest["case_results"]} != {ZIG} or {row["candidate"] for row in latest["rankings"]} != {ZIG}:
        raise RuntimeError("latest run is not a Zig-only paired result")
    old_ids = {(row["cohort"], row["case"]) for row in initial["case_results"] if row["candidate"] == ZIG}
    new_ids = {(row["cohort"], row["case"]) for row in latest["case_results"]}
    if old_ids != new_ids:
        raise RuntimeError("latest Zig result changed the task set")
    results = [row for row in initial["case_results"] if row["candidate"] != ZIG] + latest["case_results"]
    rankings = [row for row in initial["rankings"] if row["candidate"] != ZIG] + latest["rankings"]
    summary = {
        "schema": "rebar-performance-combined-v6",
        "expected_sha256": initial["expected_sha256"],
        "initial_raw_sha256": initial["raw_sha256"],
        "zig_raw_sha256": latest["raw_sha256"],
        "raw_sha256": f"initial={initial['raw_sha256']}; zig={latest['raw_sha256']}",
        "rows": initial["rows"] + latest["rows"],
        "rankings": rankings,
        "case_results": results,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
    }
    Path(args.output).write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": summary["rows"], "results": len(results), "regressions": len(summary["regressions"]), "expected_sha256": summary["expected_sha256"], "initial_raw_sha256": summary["initial_raw_sha256"], "zig_raw_sha256": summary["zig_raw_sha256"], "output": args.output}, sort_keys=True))


if __name__ == "__main__":
    main()
