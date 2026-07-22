#!/usr/bin/env python3
"""Collect correctness-checked native execution counters for the frozen holdout."""

import argparse
import json
import re
from pathlib import Path

import candidates._vm_native as native
import candidates.vm_candidate as candidate
from tools.perf_v3 import operation, snapshot, suite_module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--operations", type=int, default=96)
    args = parser.parse_args()
    if args.operations < 1:
        raise ValueError("--operations must be positive")
    results = []
    for case in suite_module().CASES:
        if case["cohort"] != "holdout":
            continue
        expected = snapshot(operation(re, case)())
        function = operation(candidate, case)
        actual = snapshot(function())
        if actual != expected:
            raise RuntimeError(f"correctness mismatch before profiling: {case['id']}")
        native.profile(True)
        for _ in range(args.operations):
            value = function()
        if snapshot(value) != expected:
            raise RuntimeError(f"correctness mismatch after profiling: {case['id']}")
        counts = native.profile(True)
        results.append({"case": case["id"], "api": case["api"], "operations": args.operations, "counts": counts, "per_operation": {key: value / args.operations for key, value in counts.items()}})
    result = {"schema": "rebar-native-profile-v1", "correctness_checked_cases": len(results), "operations_per_case": args.operations, "results": results}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"correctness_checked_cases": len(results), "operations_per_case": args.operations, "output": args.output}, sort_keys=True))
    print("case | general | clones | look | starts | rejected | steps")
    for item in sorted(results, key=lambda row: (row["per_operation"]["state_clone"], row["per_operation"]["general_calls"], row["per_operation"]["steps"]), reverse=True):
        row = item["per_operation"]
        print(f"{item['case']} | {row['general_calls']:.1f} | {row['state_clone']:.1f} | {row['look_calls']:.1f} | {row['starts']:.1f} | {row['start_rejected'] + row['pair_rejected']:.1f} | {row['steps']:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
