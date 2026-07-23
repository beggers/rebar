#!/usr/bin/env python3
"""Merge a complete frozen-v7 Rust rerun without hiding any other candidate."""

from __future__ import annotations

import argparse
import gzip
import json
import math
from pathlib import Path

from tools.perf_v7 import (
    frozen,
    is_runtime_regression,
    verify_regression_boundaries,
)


RUST = "candidates.rust_candidate"
ZIG = "candidates.zig_candidate"


def read(path):
    target = Path(path)
    opener = gzip.open if target.suffix == ".gz" else open
    with opener(target, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def valid_digest(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_summary(summary, *, label, suite, cases, manifest, candidates):
    if summary.get("schema") not in {
        "rebar-performance-summary-v7",
        "rebar-performance-combined-v7",
    }:
        raise RuntimeError(f"{label} is not a complete frozen v7 summary")
    if summary.get("expected_sha256") != manifest["expected_sha256"]:
        raise RuntimeError(f"{label} changed the frozen broader fixture")

    wanted = {
        case["id"]: (case["cohort"], case["category"], case["weight"])
        for case in cases
    }
    names = set(candidates)
    grouped = {candidate: {} for candidate in names}
    for row in summary.get("case_results", ()):
        candidate = row.get("candidate")
        case_id = row.get("case")
        if candidate not in names or case_id not in wanted:
            raise RuntimeError(f"{label} added or changed a candidate or task")
        if case_id in grouped[candidate]:
            raise RuntimeError(f"{label} duplicated task {case_id!r}")
        if (row.get("cohort"), row.get("category"), row.get("weight")) != wanted[case_id]:
            raise RuntimeError(f"{label} changed frozen task metadata: {case_id}")
        values = (
            row.get("speedup"),
            row.get("ci95_low"),
            row.get("ci95_high"),
            row.get("peak_traced_ratio"),
        )
        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            for value in values
        ):
            raise RuntimeError(f"{label} has an invalid task measurement: {case_id}")
        speed, low, high, memory = values
        if speed <= 0 or low <= 0 or high < low or memory < 0:
            raise RuntimeError(f"{label} has an invalid measured range: {case_id}")
        if (
            row.get("statistically_faster") is not (low > 1)
            or row.get("regression_gt_20pct") is not is_runtime_regression(speed)
        ):
            raise RuntimeError(f"{label} changed the frozen win or slowdown rule")
        grouped[candidate][case_id] = row

    for candidate, results in grouped.items():
        if results.keys() != wanted.keys():
            raise RuntimeError(f"{label} omitted a frozen task for {candidate}")

    rankings = {}
    for row in summary.get("rankings", ()):
        candidate = row.get("candidate")
        cohort = row.get("cohort")
        key = (candidate, cohort)
        if candidate not in names or cohort not in {"calibration", "holdout", "all"}:
            raise RuntimeError(f"{label} added an invalid candidate ranking")
        if key in rankings:
            raise RuntimeError(f"{label} duplicated ranking {key}")
        relevant = [
            item for item in grouped[candidate].values()
            if cohort == "all" or item["cohort"] == cohort
        ]
        denominator = suite.CASES_PER_COHORT * (2 if cohort == "all" else 1)
        if (
            row.get("cases") != len(relevant)
            or row.get("weight") != denominator
            or sum(item["weight"] for item in relevant) != denominator
            or row.get("statistically_faster_cases")
            != sum(item["statistically_faster"] for item in relevant)
            or row.get("regressions_gt_20pct")
            != sum(item["regression_gt_20pct"] for item in relevant)
        ):
            raise RuntimeError(f"{label} changed a ranking denominator: {key}")
        point = math.exp(
            sum(math.log(item["speedup"]) * item["weight"] for item in relevant)
            / denominator
        )
        if not math.isclose(
            row.get("geomean_speedup", math.nan),
            point,
            rel_tol=2e-12,
        ):
            raise RuntimeError(f"{label} changed an overall speed calculation: {key}")
        low = row.get("ci95_low")
        high = row.get("ci95_high")
        if (
            not isinstance(low, (int, float))
            or isinstance(low, bool)
            or not isinstance(high, (int, float))
            or isinstance(high, bool)
            or not math.isfinite(low)
            or not math.isfinite(high)
            or low <= 0
            or high < low
        ):
            raise RuntimeError(f"{label} changed an overall measured range: {key}")
        rankings[key] = row

    wanted_rankings = {
        (candidate, cohort)
        for candidate in names
        for cohort in ("calibration", "holdout", "all")
    }
    if rankings.keys() != wanted_rankings:
        raise RuntimeError(f"{label} omitted a full candidate ranking")

    actual = {
        (row.get("candidate"), row.get("case"))
        for row in summary.get("regressions", ())
    }
    expected = {
        (candidate, case_id)
        for candidate, values in grouped.items()
        for case_id, row in values.items()
        if row["regression_gt_20pct"]
    }
    if len(actual) != len(summary.get("regressions", ())) or actual != expected:
        raise RuntimeError(f"{label} omitted or duplicated a measured slowdown")
    return grouped


def combine(initial, latest, *, suite, cases, manifest):
    candidates = tuple(suite.MODULES[1:])
    validate_summary(
        initial,
        label="preserved complete candidate comparison",
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=candidates,
    )
    validate_summary(
        latest,
        label="latest complete paired Rust comparison",
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=(RUST,),
    )
    expected_initial = len(cases) * len(suite.MODULES) * suite.TRIALS
    initial_rows = initial.get("rows")
    if (
        not isinstance(initial_rows, int)
        or isinstance(initial_rows, bool)
        or initial_rows < expected_initial
        or (
            initial.get("schema") == "rebar-performance-summary-v7"
            and initial_rows != expected_initial
        )
    ):
        raise RuntimeError("the preserved all-candidate raw evidence is incomplete")
    expected_latest = len(cases) * 2 * suite.TRIALS
    if latest.get("rows") != expected_latest:
        raise RuntimeError(
            f"the paired Rust raw evidence is incomplete: "
            f"{latest.get('rows')} != {expected_latest}"
        )
    rust_hash = latest.get("raw_sha256")
    if not valid_digest(rust_hash):
        raise RuntimeError("the paired Rust measurement has no valid raw digest")
    initial_hash = initial.get("initial_raw_sha256", initial.get("raw_sha256"))
    if not valid_digest(initial_hash):
        raise RuntimeError("the all-candidate original raw digest was not preserved")
    lineage = [f"initial={initial_hash}"]
    zig_hash = initial.get("zig_raw_sha256")
    if zig_hash is not None:
        if not valid_digest(zig_hash):
            raise RuntimeError("the preserved Zig evidence has an invalid digest")
        lineage.append(f"zig={zig_hash}")
    previous_rust = initial.get("rust_raw_sha256")
    if previous_rust is not None:
        if not valid_digest(previous_rust):
            raise RuntimeError("the previous Rust evidence has an invalid digest")
        lineage.append(f"previous-rust={previous_rust}")
    lineage.append(f"rust={rust_hash}")

    preserved_results = [
        row for row in initial["case_results"] if row["candidate"] != RUST
    ]
    results = preserved_results + latest["case_results"]
    rankings = [
        row for row in initial["rankings"] if row["candidate"] != RUST
    ] + latest["rankings"]
    merged = {
        "schema": "rebar-performance-combined-v7",
        "expected_sha256": manifest["expected_sha256"],
        "initial_raw_sha256": initial_hash,
        "source_raw_sha256": initial.get("raw_sha256"),
        "rust_raw_sha256": rust_hash,
        "raw_sha256": "; ".join(lineage),
        "rows": initial_rows + latest["rows"],
        "rankings": rankings,
        "case_results": results,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
    }
    if zig_hash is not None:
        merged["zig_raw_sha256"] = zig_hash
    if previous_rust is not None:
        merged["previous_rust_raw_sha256"] = previous_rust
    validate_summary(
        merged,
        label="merged complete candidate comparison",
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=candidates,
    )
    if merged["case_results"][: len(preserved_results)] != preserved_results:
        raise RuntimeError("merging changed a previously measured candidate")
    return merged


def synthetic_summary(*, suite, cases, manifest, candidates, speeds, raw_hash):
    """Make clearly synthetic self-test data; it is never reported as evidence."""
    results = []
    for candidate in candidates:
        speed = speeds[candidate]
        low = speed * 0.99
        high = speed * 1.01
        for case in cases:
            results.append(
                {
                    "case": case["id"],
                    "cohort": case["cohort"],
                    "category": case["category"],
                    "candidate": candidate,
                    "weight": case["weight"],
                    "speedup": speed,
                    "ci95_low": low,
                    "ci95_high": high,
                    "peak_traced_ratio": 1.0,
                    "statistically_faster": low > 1,
                    "regression_gt_20pct": is_runtime_regression(speed),
                }
            )
    rankings = []
    for candidate in candidates:
        speed = speeds[candidate]
        for cohort in ("calibration", "holdout", "all"):
            relevant = [
                row for row in results
                if row["candidate"] == candidate
                and (cohort == "all" or row["cohort"] == cohort)
            ]
            rankings.append(
                {
                    "cohort": cohort,
                    "candidate": candidate,
                    "cases": len(relevant),
                    "weight": sum(row["weight"] for row in relevant),
                    "geomean_speedup": speed,
                    "ci95_low": speed * 0.99,
                    "ci95_high": speed * 1.01,
                    "statistically_faster_cases": sum(
                        row["statistically_faster"] for row in relevant
                    ),
                    "regressions_gt_20pct": sum(
                        row["regression_gt_20pct"] for row in relevant
                    ),
                }
            )
    module_count = len(suite.MODULES) if len(candidates) > 1 else 2
    return {
        "schema": "rebar-performance-summary-v7",
        "expected_sha256": manifest["expected_sha256"],
        "raw_sha256": raw_hash,
        "rows": len(cases) * module_count * suite.TRIALS,
        "rankings": rankings,
        "case_results": results,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
    }


def self_test():
    suite, cases, _expected, manifest = frozen()
    boundary_checks = verify_regression_boundaries()
    candidates = tuple(suite.MODULES[1:])
    initial_speeds = {
        name: value
        for name, value in zip(candidates, (0.82, 1.19, 0.91, 1.56), strict=True)
    }
    initial = synthetic_summary(
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=candidates,
        speeds=initial_speeds,
        raw_hash="a" * 64,
    )
    latest = synthetic_summary(
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=(RUST,),
        speeds={RUST: 1.37},
        raw_hash="b" * 64,
    )
    merged = combine(initial, latest, suite=suite, cases=cases, manifest=manifest)
    preserved = [row for row in initial["case_results"] if row["candidate"] != RUST]
    if (
        merged["case_results"][: len(preserved)] != preserved
        or merged["case_results"][len(preserved) :] != latest["case_results"]
        or merged["rust_raw_sha256"] != "b" * 64
    ):
        raise RuntimeError("v7 merging did not preserve every non-Rust result")

    rust_rows = latest["case_results"]
    rust_rankings = latest["rankings"]
    slowdowns = latest["regressions"]
    corrupted_case = {**rust_rows[0], "weight": 2}
    corrupted_speed = {**rust_rows[0], "statistically_faster": False}
    corrupted_range = {**rust_rows[0], "ci95_low": -1.0}
    corrupted_ranking = {**rust_rankings[0], "weight": 1}
    corruptions = (
        {**latest, "expected_sha256": "f" * 64},
        {**latest, "rows": latest["rows"] - 1},
        {**latest, "case_results": rust_rows[:-1]},
        {**latest, "case_results": [rust_rows[0], *rust_rows]},
        {**latest, "case_results": [corrupted_case, *rust_rows[1:]]},
        {**latest, "case_results": [corrupted_speed, *rust_rows[1:]]},
        {**latest, "case_results": [corrupted_range, *rust_rows[1:]]},
        {**latest, "rankings": rust_rankings[:-1]},
        {**latest, "rankings": [corrupted_ranking, *rust_rankings[1:]]},
        {**latest, "raw_sha256": "not-a-digest"},
        {**latest, "regressions": [rust_rows[0], *slowdowns]},
    )
    rejected = 0
    for damaged in corruptions:
        try:
            combine(initial, damaged, suite=suite, cases=cases, manifest=manifest)
        except (KeyError, RuntimeError, TypeError, ValueError):
            rejected += 1
        else:
            raise RuntimeError("v7 merging accepted incomplete or corrupted evidence")

    boundary_case = initial["case_results"][0]
    if (
        boundary_case["speedup"] != 0.82
        or boundary_case["regression_gt_20pct"] is not True
    ):
        raise RuntimeError("the merge self-test omitted a real 20–25% slowdown")
    concealed = {
        **initial,
        "case_results": [
            {**boundary_case, "regression_gt_20pct": False},
            *initial["case_results"][1:],
        ],
        "regressions": [
            row
            for row in initial["regressions"]
            if (row["candidate"], row["case"])
            != (boundary_case["candidate"], boundary_case["case"])
        ],
    }
    try:
        combine(concealed, latest, suite=suite, cases=cases, manifest=manifest)
    except (KeyError, RuntimeError, TypeError, ValueError):
        rejected += 1
    else:
        raise RuntimeError("v7 merging concealed a 20–25% elapsed-time regression")
    result = {
        **boundary_checks,
        "schema": "rebar-performance-merge-self-test-v7",
        "passed": True,
        "synthetic_only": True,
        "expected_sha256": manifest["expected_sha256"],
        "frozen_cases": len(cases),
        "preserved_non_rust_results": len(preserved),
        "rust_results": len(rust_rows),
        "candidate_rankings": len(merged["rankings"]),
        "rejected_corruptions": rejected,
    }
    print(json.dumps(result, sort_keys=True))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial")
    parser.add_argument("--rust")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        if args.initial or args.rust or args.output:
            parser.error("--self-test cannot be combined with measurement inputs")
        self_test()
        return
    if not args.initial or not args.rust or not args.output:
        parser.error("--initial, --rust, and --output are required")
    suite, cases, _expected, manifest = frozen()
    summary = combine(
        read(args.initial),
        read(args.rust),
        suite=suite,
        cases=cases,
        manifest=manifest,
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "rows": summary["rows"],
                "results": len(summary["case_results"]),
                "rankings": len(summary["rankings"]),
                "regressions": len(summary["regressions"]),
                "expected_sha256": summary["expected_sha256"],
                "initial_raw_sha256": summary["initial_raw_sha256"],
                "rust_raw_sha256": summary["rust_raw_sha256"],
                "output": str(destination),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
