#!/usr/bin/env python3
"""Collect correctness-checked native execution counters for a expanded holdout family."""

import argparse
import json
import re
from pathlib import Path

import candidates._vm_native as native
import candidates.vm_candidate as candidate
from tools.perf_v5 import operation, snapshot, suite_module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    parser.add_argument("--operations", type=int, default=128)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.operations < 1:
        raise ValueError("--operations must be positive")
    selected = [case for case in suite_module().cases() if case["cohort"] == "holdout" and case["category"] == args.family]
    if not selected:
        raise ValueError(f"holdout family not found: {args.family}")
    results = []
    for case in selected:
        expected = snapshot(operation(re, case)())
        action = operation(candidate, case)
        actual = snapshot(action())
        if actual != expected:
            raise RuntimeError(f"correctness mismatch before profiling: {case['id']}")
        native.profile(True)
        value = None
        for _ in range(args.operations):
            value = action()
        if snapshot(value) != expected:
            raise RuntimeError(f"correctness mismatch after profiling: {case['id']}")
        counts = native.profile(True)
        results.append({"case": case["id"], "api": case["api"], "operations": args.operations, "counts": counts, "per_operation": {key: value / args.operations for key, value in counts.items()}})
    payload = {"schema": "rebar-native-expanded-profile-v1", "family": args.family, "correctness_checked_cases": len(results), "operations_per_case": args.operations, "results": results}
    Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"family": args.family, "correctness_checked_cases": len(results), "operations_per_case": args.operations, "output": args.output}, sort_keys=True))
    print("case | api | general | clones | starts | classes | repeats | steps")
    for item in sorted(results, key=lambda row: (row["per_operation"]["class_checks"], row["per_operation"]["general_calls"], row["per_operation"]["steps"]), reverse=True):
        row = item["per_operation"]
        print(f"{item['case']} | {item['api']} | {row['general_calls']:.1f} | {row['state_clone']:.1f} | {row['starts']:.1f} | {row['class_checks']:.1f} | {row['repeat_chars']:.1f} | {row['steps']:.1f}")


if __name__ == "__main__":
    main()
