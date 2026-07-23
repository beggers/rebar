#!/usr/bin/env python3
"""Preserve the frozen five-engine results while updating measured Rust."""

from __future__ import annotations

import argparse
import gzip
import json
import math
from pathlib import Path

from tools.perf_v6 import frozen


RUST = "candidates.rust_candidate"
ZIG = "candidates.zig_candidate"
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    target = Path(path)
    opener = gzip.open if target.suffix == ".gz" else open
    with opener(target, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def validate_summary(summary, *, label, suite, cases, manifest, candidates):
    if summary.get("schema") not in {
        "rebar-performance-summary-v6",
        "rebar-performance-combined-v6",
    }:
        raise RuntimeError(f"{label} is not a frozen v6 summary")
    if summary.get("expected_sha256") != manifest["expected_sha256"]:
        raise RuntimeError(f"{label} changed the frozen performance fixture")

    wanted_cases = {
        case["id"]: (case["cohort"], case["category"], case["weight"])
        for case in cases
    }
    wanted_candidates = set(candidates)
    grouped = {candidate: {} for candidate in wanted_candidates}
    for row in summary.get("case_results", ()):
        candidate = row.get("candidate")
        case_id = row.get("case")
        if candidate not in wanted_candidates or case_id not in wanted_cases:
            raise RuntimeError(f"{label} contains an unexpected engine or task")
        if case_id in grouped[candidate]:
            raise RuntimeError(
                f"{label} contains duplicate task {case_id!r} for {candidate}"
            )
        metadata = (row.get("cohort"), row.get("category"), row.get("weight"))
        if metadata != wanted_cases[case_id]:
            raise RuntimeError(f"{label} changed frozen task metadata: {case_id}")

        speed = row.get("speedup")
        low = row.get("ci95_low")
        high = row.get("ci95_high")
        memory = row.get("peak_traced_ratio")
        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            for value in (speed, low, high, memory)
        ):
            raise RuntimeError(f"{label} contains invalid measurements: {case_id}")
        if speed <= 0 or low <= 0 or high < low or memory < 0:
            raise RuntimeError(f"{label} contains invalid ranges: {case_id}")
        if (
            row.get("statistically_faster") is not (low > 1)
            or row.get("regression_gt_20pct") is not (speed < 0.8)
        ):
            raise RuntimeError(f"{label} changed win/loss rules: {case_id}")
        grouped[candidate][case_id] = row

    for candidate, rows in grouped.items():
        if rows.keys() != wanted_cases.keys():
            raise RuntimeError(
                f"{label} changed the full frozen task set for {candidate}"
            )

    rankings = {}
    for row in summary.get("rankings", ()):
        candidate = row.get("candidate")
        cohort = row.get("cohort")
        key = (candidate, cohort)
        if candidate not in wanted_candidates or cohort not in {
            "calibration",
            "holdout",
            "all",
        }:
            raise RuntimeError(f"{label} contains an unexpected ranking")
        if key in rankings:
            raise RuntimeError(f"{label} contains duplicate ranking {key}")

        relevant = [
            item
            for item in grouped[candidate].values()
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
            raise RuntimeError(f"{label} changed ranking denominators: {key}")

        point = math.exp(
            sum(math.log(item["speedup"]) * item["weight"] for item in relevant)
            / denominator
        )
        if not math.isclose(
            row.get("geomean_speedup", math.nan),
            point,
            rel_tol=2e-12,
            abs_tol=0,
        ):
            raise RuntimeError(f"{label} changed the ranking calculation: {key}")
        low = row.get("ci95_low")
        high = row.get("ci95_high")
        if (
            not isinstance(low, (int, float))
            or not isinstance(high, (int, float))
            or not math.isfinite(low)
            or not math.isfinite(high)
            or low <= 0
            or high < low
        ):
            raise RuntimeError(f"{label} contains invalid ranking ranges: {key}")
        rankings[key] = row

    wanted_rankings = {
        (candidate, cohort)
        for candidate in wanted_candidates
        for cohort in ("calibration", "holdout", "all")
    }
    if rankings.keys() != wanted_rankings:
        raise RuntimeError(f"{label} changed its complete ranking set")

    actual_regressions = {
        (row["candidate"], row["case"])
        for row in summary.get("regressions", ())
    }
    expected_regressions = {
        (candidate, case_id)
        for candidate, rows in grouped.items()
        for case_id, row in rows.items()
        if row["regression_gt_20pct"]
    }
    if (
        len(actual_regressions) != len(summary.get("regressions", ()))
        or actual_regressions != expected_regressions
    ):
        raise RuntimeError(f"{label} omitted or changed measured slowdowns")

    return grouped


def combine(initial, latest, *, suite, cases, manifest):
    candidates = tuple(suite.MODULES[1:])
    validate_summary(
        initial,
        label="preserved five-engine comparison",
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=candidates,
    )
    validate_summary(
        latest,
        label="latest paired Rust run",
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=(RUST,),
    )

    required_rust_rows = len(cases) * 2 * suite.TRIALS
    if latest.get("rows") != required_rust_rows:
        raise RuntimeError(
            "latest Rust run has an incomplete or changed raw-row count: "
            f"{latest.get('rows')} != {required_rust_rows}"
        )

    rust_raw_hash = latest.get("raw_sha256")
    if (
        not isinstance(rust_raw_hash, str)
        or len(rust_raw_hash) != 64
        or any(char not in "0123456789abcdef" for char in rust_raw_hash)
    ):
        raise RuntimeError("latest Rust run does not have a raw SHA-256 digest")

    initial_raw_hash = initial.get("initial_raw_sha256", initial.get("raw_sha256"))
    if (
        not isinstance(initial_raw_hash, str)
        or len(initial_raw_hash) != 64
        or any(char not in "0123456789abcdef" for char in initial_raw_hash)
    ):
        raise RuntimeError("the original five-engine raw digest was not preserved")

    lineage = [f"initial={initial_raw_hash}"]
    zig_raw_hash = initial.get("zig_raw_sha256")
    if zig_raw_hash is not None:
        if (
            not isinstance(zig_raw_hash, str)
            or len(zig_raw_hash) != 64
            or any(char not in "0123456789abcdef" for char in zig_raw_hash)
        ):
            raise RuntimeError("the preserved Zig raw digest is invalid")
        lineage.append(f"zig={zig_raw_hash}")

    previous_rust_raw_hash = initial.get("rust_raw_sha256")
    if previous_rust_raw_hash is not None:
        if (
            not isinstance(previous_rust_raw_hash, str)
            or len(previous_rust_raw_hash) != 64
            or any(char not in "0123456789abcdef" for char in previous_rust_raw_hash)
        ):
            raise RuntimeError("the previous Rust raw digest is invalid")
        lineage.append(f"previous-rust={previous_rust_raw_hash}")
    lineage.append(f"rust={rust_raw_hash}")

    results = [
        row for row in initial["case_results"] if row["candidate"] != RUST
    ] + latest["case_results"]
    rankings = [
        row for row in initial["rankings"] if row["candidate"] != RUST
    ] + latest["rankings"]
    summary = {
        "schema": "rebar-performance-combined-v6",
        "expected_sha256": manifest["expected_sha256"],
        "initial_raw_sha256": initial_raw_hash,
        "source_raw_sha256": initial["raw_sha256"],
        "rust_raw_sha256": rust_raw_hash,
        "raw_sha256": "; ".join(lineage),
        "rows": initial["rows"] + latest["rows"],
        "rankings": rankings,
        "case_results": results,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
    }
    if zig_raw_hash is not None:
        summary["zig_raw_sha256"] = zig_raw_hash
    if previous_rust_raw_hash is not None:
        summary["previous_rust_raw_sha256"] = previous_rust_raw_hash

    validate_summary(
        summary,
        label="merged five-engine result",
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=candidates,
    )
    return summary


def self_test():
    suite, cases, _expected, manifest = frozen()
    initial = read(ROOT / "candidates/evidence/zig-v6-combined-summary.json.gz")
    rust_results = [
        row for row in initial["case_results"] if row["candidate"] == RUST
    ]
    rust_rankings = [
        row for row in initial["rankings"] if row["candidate"] == RUST
    ]
    latest = {
        "schema": "rebar-performance-summary-v6",
        "expected_sha256": manifest["expected_sha256"],
        "raw_sha256": "0" * 64,
        "rows": len(cases) * 2 * suite.TRIALS,
        "case_results": rust_results,
        "rankings": rust_rankings,
        "regressions": [
            row for row in rust_results if row["regression_gt_20pct"]
        ],
    }
    merged = combine(initial, latest, suite=suite, cases=cases, manifest=manifest)
    preserved = [
        row for row in initial["case_results"] if row["candidate"] != RUST
    ]
    if (
        merged["case_results"][: len(preserved)] != preserved
        or merged["case_results"][len(preserved) :] != rust_results
        or merged.get("zig_raw_sha256") != initial.get("zig_raw_sha256")
        or merged["rust_raw_sha256"] != "0" * 64
    ):
        raise RuntimeError("merge failed to preserve all independent engines")

    rejected = 0
    corruptions = (
        {**latest, "expected_sha256": "f" * 64},
        {**latest, "rows": latest["rows"] - 1},
        {**latest, "case_results": rust_results[:-1]},
        {**latest, "rankings": rust_rankings[:-1]},
        {**latest, "regressions": latest["regressions"][:-1]},
        {**latest, "raw_sha256": "not-a-sha256"},
    )
    for corrupt in corruptions:
        try:
            combine(initial, corrupt, suite=suite, cases=cases, manifest=manifest)
        except (KeyError, RuntimeError, TypeError, ValueError):
            rejected += 1
        else:
            raise RuntimeError("merge accepted corrupted or incomplete evidence")

    result = {
        "passed": True,
        "expected_sha256": manifest["expected_sha256"],
        "frozen_cases": len(cases),
        "engines": len(suite.MODULES) - 1,
        "preserved_non_rust_results": len(preserved),
        "rust_results": len(rust_results),
        "rankings": len(merged["rankings"]),
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
            parser.error("--self-test cannot be combined with merge inputs")
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
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
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
                "zig_raw_sha256": summary.get("zig_raw_sha256"),
                "rust_raw_sha256": summary["rust_raw_sha256"],
                "output": str(target),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
