#!/usr/bin/env python3
"""Compare frozen, drift-checked Rust native-allocation measurements."""

from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import math
import random
import statistics
from pathlib import Path


SCHEMA = "rebar-rust-readonly-native-allocator-profile-v6"
DIAGNOSTIC_NOTICE = (
    "Confidence intervals describe only the explicitly sampled frozen cases. "
    "They are not full-holdout rankings and do not replace the 6,216-case "
    "performance oracle."
)


def geometric_mean(values):
    values = list(values)
    if not values:
        return None
    if any(value <= 0 for value in values):
        raise RuntimeError("geometric comparison requires positive measurements")
    return math.exp(statistics.fmean(math.log(value) for value in values))


def native_totals(row):
    native = row["native_heap"]["rust"]
    return {
        "allocation_calls": sum(
            native[name] for name in ("malloc_calls", "calloc_calls", "realloc_calls")
        ),
        "allocation_bytes": sum(
            native[name] for name in ("malloc_bytes", "calloc_bytes", "realloc_bytes")
        ),
        "failed_calls": native["failed_calls"],
    }


def validate_profile(result, path):
    if result.get("schema") != SCHEMA:
        raise RuntimeError(f"unexpected allocator-profile schema: {path}")
    if result.get("artifact_drift"):
        raise RuntimeError(f"native binary changed during profile: {path}")
    if result.get("measured_cases") != result.get("requested_cases"):
        raise RuntimeError(f"native allocation profile is incomplete: {path}")
    if result.get("measured_cases") != len(result.get("rows", ())):
        raise RuntimeError(f"native allocation profile row count changed: {path}")
    cases = [row["case"] for row in result["rows"]]
    if len(cases) != len(set(cases)):
        raise RuntimeError(f"duplicate case IDs in native allocation profile: {path}")
    return result


def load_profile(value):
    path = Path(value).resolve()
    if not path.is_relative_to(Path("/tmp")):
        raise RuntimeError("native-allocation comparison accepts only /tmp artifacts")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    with path.open(encoding="utf-8") as stream:
        result = json.load(stream)
    validate_profile(result, path)
    return result, {"path": str(path), "sha256": digest}


def compare(before, after):
    for field, description in (
        ("expected_sha256", "frozen correctness/performance fixtures"),
        ("cohort", "performance cohorts"),
        ("variant_indexes", "selected case variants"),
        ("selection", "selected performance families"),
    ):
        if before[field] != after[field]:
            raise RuntimeError(f"native allocation profile {description} differ")
    before_rows = {row["case"]: row for row in before["rows"]}
    after_rows = {row["case"]: row for row in after["rows"]}
    if before_rows.keys() != after_rows.keys():
        missing = sorted(before_rows.keys() - after_rows.keys())
        added = sorted(after_rows.keys() - before_rows.keys())
        raise RuntimeError(f"case denominators changed; missing={missing}, added={added}")

    rows = []
    for case in sorted(before_rows):
        old = before_rows[case]
        new = after_rows[case]
        for field in ("category", "api", "lifecycle", "input", "subject_length", "result_count"):
            if old[field] != new[field]:
                raise RuntimeError(f"native allocation case metadata drift: {case} {field}")
        old_native = native_totals(old)
        new_native = native_totals(new)
        if old_native["failed_calls"] or new_native["failed_calls"]:
            raise RuntimeError(f"observed a failed native allocation in case {case}")
        old_wall = statistics.median(old["wall_ns_per_op"]["rust"])
        new_wall = statistics.median(new["wall_ns_per_op"]["rust"])
        old_cpu = statistics.median(old["thread_cpu_ns_per_op"]["rust"])
        new_cpu = statistics.median(new["thread_cpu_ns_per_op"]["rust"])
        if min(old_wall, new_wall, old_cpu, new_cpu) <= 0:
            raise RuntimeError(f"nonpositive timing in case {case}")
        if min(old["wall_speedup"], new["wall_speedup"]) <= 0:
            raise RuntimeError(f"nonpositive baseline-relative timing in case {case}")
        rows.append(
            {
                "case": case,
                "category": old["category"],
                "api": old["api"],
                "lifecycle": old["lifecycle"],
                "input": old["input"],
                "subject_length": old["subject_length"],
                "result_count": old["result_count"],
                "old_stdlib_relative_speedup": old["wall_speedup"],
                "new_stdlib_relative_speedup": new["wall_speedup"],
                "paired_stdlib_relative_improvement": new["wall_speedup"] / old["wall_speedup"],
                "old_rust_wall_ns_per_op": old_wall,
                "new_rust_wall_ns_per_op": new_wall,
                "raw_rust_wall_improvement": old_wall / new_wall,
                "old_rust_thread_cpu_ns_per_op": old_cpu,
                "new_rust_thread_cpu_ns_per_op": new_cpu,
                "raw_rust_thread_cpu_improvement": old_cpu / new_cpu,
                "old_rust_native_heap": old_native,
                "new_rust_native_heap": new_native,
                "native_allocation_calls_removed": (
                    old_native["allocation_calls"] - new_native["allocation_calls"]
                ),
                "native_allocation_bytes_removed": (
                    old_native["allocation_bytes"] - new_native["allocation_bytes"]
                ),
                "native_allocation_reduction": (
                    old_native["allocation_calls"] / new_native["allocation_calls"]
                    if new_native["allocation_calls"]
                    else None
                ),
                "native_allocation_bytes_reduction": (
                    old_native["allocation_bytes"] / new_native["allocation_bytes"]
                    if new_native["allocation_bytes"]
                    else None
                ),
                "old_rust_traced_peak_bytes": old["traced_peak_bytes"]["rust"],
                "new_rust_traced_peak_bytes": new["traced_peak_bytes"]["rust"],
            }
        )

    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)
    families = []
    for category, members in grouped.items():
        families.append(
            {
                "category": category,
                "cases": len(members),
                "old_stdlib_relative_speedup": geometric_mean(
                    row["old_stdlib_relative_speedup"] for row in members
                ),
                "new_stdlib_relative_speedup": geometric_mean(
                    row["new_stdlib_relative_speedup"] for row in members
                ),
                "paired_stdlib_relative_improvement": geometric_mean(
                    row["paired_stdlib_relative_improvement"] for row in members
                ),
                "raw_rust_thread_cpu_improvement": geometric_mean(
                    row["raw_rust_thread_cpu_improvement"] for row in members
                ),
                "old_median_native_allocations": statistics.median(
                    row["old_rust_native_heap"]["allocation_calls"] for row in members
                ),
                "new_median_native_allocations": statistics.median(
                    row["new_rust_native_heap"]["allocation_calls"] for row in members
                ),
                "old_median_native_allocation_bytes": statistics.median(
                    row["old_rust_native_heap"]["allocation_bytes"] for row in members
                ),
                "new_median_native_allocation_bytes": statistics.median(
                    row["new_rust_native_heap"]["allocation_bytes"] for row in members
                ),
            }
        )
    return rows, sorted(families, key=lambda row: row["old_stdlib_relative_speedup"])


def percentile(values, position):
    index = position * (len(values) - 1)
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return values[lower]
    fraction = index - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction


def trial_logs(old, new, clock):
    key = "wall_ns_per_op" if clock == "wall" else "thread_cpu_ns_per_op"
    old_stdlib = old[key]["stdlib"]
    old_rust = old[key]["rust"]
    new_stdlib = new[key]["stdlib"]
    new_rust = new[key]["rust"]
    if not (
        len(old_stdlib) == len(old_rust) == len(new_stdlib) == len(new_rust)
    ):
        raise RuntimeError(f"bootstrap trial denominator changed: {old['case']}")
    if not old_stdlib:
        raise RuntimeError(f"bootstrap trials are missing: {old['case']}")
    if any(
        value <= 0
        for trial in (old_stdlib, old_rust, new_stdlib, new_rust)
        for value in trial
    ):
        raise RuntimeError(f"bootstrap timing is not positive: {old['case']}")
    return (
        [
            math.log(baseline / candidate)
            for baseline, candidate in zip(old_stdlib, old_rust, strict=True)
        ],
        [
            math.log(baseline / candidate)
            for baseline, candidate in zip(new_stdlib, new_rust, strict=True)
        ],
    )


def bootstrap_interval(pairs, clock, seed, draws):
    logs = [trial_logs(old, new, clock) for old, new in pairs]
    if not logs:
        raise RuntimeError("cannot bootstrap an empty diagnostic case selection")
    point = math.exp(
        statistics.fmean(
            statistics.fmean(new) - statistics.fmean(old) for old, new in logs
        )
    )
    generator = random.Random(seed)
    values = []
    denominator = len(logs)
    for _ in range(draws):
        total = 0.0
        for _ in range(denominator):
            old, new = logs[generator.randrange(denominator)]
            total += new[generator.randrange(len(new))]
            total -= old[generator.randrange(len(old))]
        values.append(math.exp(total / denominator))
    values.sort()
    low = percentile(values, 0.025)
    high = percentile(values, 0.975)
    return {
        "cases": denominator,
        "trials_per_case": len(logs[0][0]),
        "point": point,
        "ci95_low": low,
        "ci95_high": high,
        "statistically_faster": low > 1.0,
    }


def diagnostic_intervals(before, after, seed, draws):
    if draws < 100:
        raise RuntimeError("diagnostic intervals require at least 100 bootstrap draws")
    old_rows = {row["case"]: row for row in before["rows"]}
    new_rows = {row["case"]: row for row in after["rows"]}
    if old_rows.keys() != new_rows.keys():
        raise RuntimeError("diagnostic interval case denominator changed")
    pairs = [(old_rows[case], new_rows[case]) for case in sorted(old_rows)]
    grouped = collections.defaultdict(list)
    for old, new in pairs:
        if old["category"] != new["category"]:
            raise RuntimeError(f"diagnostic interval family changed: {old['case']}")
        grouped[old["category"]].append((old, new))
    families = []
    for index, category in enumerate(sorted(grouped)):
        family_seed = seed + 1009 * (index + 1)
        families.append(
            {
                "category": category,
                "wall": bootstrap_interval(
                    grouped[category], "wall", family_seed, draws
                ),
                "thread_cpu": bootstrap_interval(
                    grouped[category], "thread_cpu", family_seed + 1, draws
                ),
            }
        )
    return {
        "warning": DIAGNOSTIC_NOTICE,
        "cases": len(pairs),
        "families": sorted(families, key=lambda row: row["wall"]["point"]),
        "bootstrap_samples": draws,
        "seed": seed,
        "overall": {
            "wall": bootstrap_interval(pairs, "wall", seed, draws),
            "thread_cpu": bootstrap_interval(pairs, "thread_cpu", seed + 1, draws),
        },
    }


def self_test(profile):
    loaded, stamp = load_profile(profile)
    rows, families = compare(loaded, loaded)
    if len(rows) != loaded["measured_cases"] or not families:
        raise RuntimeError("self-comparison changed the frozen denominator")
    for row in rows:
        if (
            row["paired_stdlib_relative_improvement"] != 1.0
            or row["raw_rust_wall_improvement"] != 1.0
            or row["raw_rust_thread_cpu_improvement"] != 1.0
            or row["native_allocation_calls_removed"] != 0
            or row["native_allocation_bytes_removed"] != 0
        ):
            raise RuntimeError(f"native allocation self-oracle failed: {row['case']}")

    def refuses(callback, description):
        try:
            callback()
        except RuntimeError:
            return
        raise RuntimeError(f"native comparison accepted {description}")

    changed_fixture = copy.deepcopy(loaded)
    changed_fixture["expected_sha256"] = "0" * 64
    refuses(lambda: compare(loaded, changed_fixture), "a changed frozen fixture")

    changed_variants = copy.deepcopy(loaded)
    changed_variants["variant_indexes"] = [0]
    refuses(lambda: compare(loaded, changed_variants), "a changed case selection")

    missing_case = copy.deepcopy(loaded)
    missing_case["rows"].pop()
    refuses(lambda: compare(loaded, missing_case), "a changed case denominator")

    changed_metadata = copy.deepcopy(loaded)
    changed_metadata["rows"][0]["subject_length"] += 1
    refuses(lambda: compare(loaded, changed_metadata), "changed case metadata")

    drifted_binary = copy.deepcopy(loaded)
    drifted_binary["artifact_drift"] = True
    refuses(
        lambda: validate_profile(drifted_binary, "self-test"),
        "a native binary changed during profiling",
    )

    duplicated_case = copy.deepcopy(loaded)
    duplicated_case["rows"][1]["case"] = duplicated_case["rows"][0]["case"]
    refuses(
        lambda: validate_profile(duplicated_case, "self-test"),
        "a duplicate native allocation case",
    )

    interval = diagnostic_intervals(loaded, loaded, 1985072202, 100)
    for clock in ("wall", "thread_cpu"):
        result = interval["overall"][clock]
        if result["point"] != 1.0 or not result["ci95_low"] <= 1.0 <= result["ci95_high"]:
            raise RuntimeError(f"diagnostic bootstrap self-oracle failed: {clock}")

    return {
        "schema": "rebar-rust-native-allocation-comparator-self-test-v6",
        "profile": stamp,
        "expected_sha256": loaded["expected_sha256"],
        "cases": len(rows),
        "families": len(families),
        "rejection_checks": 6,
        "confidence_self_test": True,
        "failed": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", default="/tmp/rebar-rust-readonly-allocator-v6.json")
    parser.add_argument("--after", default="/tmp/rebar-rust-readonly-allocator-optimized-v6.json")
    parser.add_argument("--output", default="/tmp/rebar-rust-readonly-allocator-comparison-v6.json")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--self-test-output")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=1985072202)
    args = parser.parse_args()
    if args.self_test_output and not args.self_test:
        parser.error("--self-test-output requires --self-test")
    if args.self_test:
        result = self_test(args.before)
        if args.self_test_output:
            target = Path(args.self_test_output).resolve()
            if not target.is_relative_to(Path("/tmp")):
                raise RuntimeError("native allocation self-tests write only inside /tmp")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(result, sort_keys=True), flush=True)
        return

    before, before_file = load_profile(args.before)
    after, after_file = load_profile(args.after)
    rows, families = compare(before, after)
    confidence = diagnostic_intervals(
        before, after, args.bootstrap_seed, args.bootstrap_samples
    )
    output = Path(args.output).resolve()
    if not output.is_relative_to(Path("/tmp")):
        raise RuntimeError("native allocation comparisons write only inside /tmp")
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "rebar-rust-readonly-allocator-comparison-v6",
        "expected_sha256": before["expected_sha256"],
        "cohort": before["cohort"],
        "cases": len(rows),
        "families_count": len(families),
        "before": before_file,
        "after": after_file,
        "before_engine": before["artifacts_before"]["engine"],
        "before_bridge": before["artifacts_before"]["bridge"],
        "after_engine": after["artifacts_before"]["engine"],
        "after_bridge": after["artifacts_before"]["bridge"],
        "paired_stdlib_relative_improvement": geometric_mean(
            row["paired_stdlib_relative_improvement"] for row in rows
        ),
        "raw_rust_thread_cpu_improvement": geometric_mean(
            row["raw_rust_thread_cpu_improvement"] for row in rows
        ),
        "rust_native_allocations_before": sum(
            row["old_rust_native_heap"]["allocation_calls"] for row in rows
        ),
        "rust_native_allocations_after": sum(
            row["new_rust_native_heap"]["allocation_calls"] for row in rows
        ),
        "rust_native_allocation_bytes_before": sum(
            row["old_rust_native_heap"]["allocation_bytes"] for row in rows
        ),
        "rust_native_allocation_bytes_after": sum(
            row["new_rust_native_heap"]["allocation_bytes"] for row in rows
        ),
        "diagnostic_confidence": confidence,
        "families": families,
        "rows": rows,
    }
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "family                                 before    after improve    alloc_before alloc_after",
        flush=True,
    )
    for row in families:
        print(
            f"{row['category']:<38} {row['old_stdlib_relative_speedup']:>7.3f} "
            f"{row['new_stdlib_relative_speedup']:>8.3f} "
            f"{row['paired_stdlib_relative_improvement']:>7.2f} "
            f"{row['old_median_native_allocations']:>14.0f} "
            f"{row['new_median_native_allocations']:>11.0f}",
            flush=True,
        )
    print(
        json.dumps(
            {
                "output": str(output),
                "cases": len(rows),
                "families": len(families),
                "paired_stdlib_relative_improvement": result[
                    "paired_stdlib_relative_improvement"
                ],
                "diagnostic_ci95_low": confidence["overall"]["wall"]["ci95_low"],
                "diagnostic_ci95_high": confidence["overall"]["wall"]["ci95_high"],
                "diagnostic_warning": DIAGNOSTIC_NOTICE,
                "raw_rust_thread_cpu_improvement": result["raw_rust_thread_cpu_improvement"],
                "rust_native_allocations_before": result["rust_native_allocations_before"],
                "rust_native_allocations_after": result["rust_native_allocations_after"],
                "rust_native_allocation_bytes_before": result[
                    "rust_native_allocation_bytes_before"
                ],
                "rust_native_allocation_bytes_after": result[
                    "rust_native_allocation_bytes_after"
                ],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
