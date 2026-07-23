#!/usr/bin/env python3
"""Preserve and verify the isolated, from-scratch Rust repeat experiments.

The archive contains previously recorded compatibility and calibration data.
It never runs a candidate, touches a frozen holdout, starts a benchmark, or
modifies the Rust engine.
"""

from __future__ import annotations

import argparse
import collections
import difflib
import gzip
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path


SCHEMA = "rebar-rust-v6-repeat-lab-v1"
ORACLE_PYTHON = "3.14.6"
REPEAT_SEED = 202607230541
REGRESSION_SPEEDUP_NUMERATOR = 5
REGRESSION_SPEEDUP_DENOMINATOR = 6
EXPECTED_PERFORMANCE = (
    "c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335"
)
DEFAULT_RESEARCH = Path("/tmp/rebar-rust-counter-research.XuFUZd")
DEFAULT_ARCHIVE = (
    Path(__file__).resolve().parents[1]
    / "candidates"
    / "evidence"
    / "rust-v6-repeat-lab.json.gz"
)

SOURCES = {
    "original_repeat_engine": "core-wide-baseline.rs",
    "corrected_isolated_repeat_engine": "lib.rs",
    "corrected_integrated_repeat_engine": "comparison-hybrid.rs",
    "counted_repeat_differential": "counter_probe.py",
    "original_search_primitive": "search.rs",
    "lazy_repeat_baseline_engine": "lazy/baseline.rs",
    "lazy_repeat_corrected_engine": "lazy/lib.rs",
    "qualified_tail_filter_candidate": "lazy/tail.rs",
    "qualified_tail_search_candidate": "lazy/search.rs",
    "qualified_tail_differential": "lazy/tail_probe.py",
}

PATCHES = {
    "corrected_isolated_counted_repeat": (
        "original_repeat_engine",
        "corrected_isolated_repeat_engine",
        "correctness-qualified; calibrated; final holdout NOT MEASURED",
    ),
    "corrected_integrated_counted_repeat": (
        "original_repeat_engine",
        "corrected_integrated_repeat_engine",
        "correctness-qualified; calibrated; final holdout NOT MEASURED",
    ),
    "corrected_linear_lazy_repeat": (
        "lazy_repeat_baseline_engine",
        "lazy_repeat_corrected_engine",
        "correctness-qualified; calibrated; final holdout NOT MEASURED",
    ),
    "qualified_lazy_tail_filter": (
        "lazy_repeat_corrected_engine",
        "qualified_tail_filter_candidate",
        "correctness-qualified; performance NOT MEASURED; not integrated",
    ),
    "qualified_lazy_tail_byte_search": (
        "original_search_primitive",
        "qualified_tail_search_candidate",
        "correctness-qualified; performance NOT MEASURED; not integrated",
    ),
}

GATES = {
    "original_rejected_repeat": "core-wide-counter-fuzz-baseline.json",
    "first_rejected_repeat_patch": "counter-fuzz-16384.json",
    "corrected_first_repeat_16384": "counter-fuzz-16384-fixed.json",
    "corrected_first_repeat_full": "counter-fuzz-65536-fixed.json",
    "corrected_hybrid_repeat_16384": "counter-hybrid-16384.json",
    "corrected_isolated_repeat": "counter-hybrid-65536.json",
    "corrected_first_oracle_v2": "counter-frozen-v2.json",
    "corrected_first_oracle_v3": "counter-frozen-v3.json",
    "corrected_first_performance_correctness_v6": "counter-frozen-v6.json",
    "corrected_first_official_cpython": "counter-official-upstream.json",
    "corrected_integrated_repeat": "core-integrated-counter-65536.json",
    "corrected_integrated_hidden_surface": "integrated-hidden-paths.json",
    "corrected_integrated_oracle_v2": "integrated-frozen-v2.json",
    "corrected_integrated_oracle_v3": "integrated-frozen-v3.json",
    "corrected_integrated_performance_correctness_v6": (
        "integrated-frozen-v6.json"
    ),
    "corrected_integrated_official_cpython": "integrated-official-upstream.json",
    "corrected_hybrid_oracle_v2": "hybrid-frozen-v2.json",
    "corrected_hybrid_oracle_v3": "hybrid-frozen-v3.json",
    "corrected_hybrid_performance_correctness_v6": "hybrid-frozen-v6.json",
    "corrected_hybrid_official_cpython": "hybrid-official-upstream.json",
    "linear_lazy_repeat_differential": "lazy/counter-65536.json",
    "linear_lazy_hidden_surface": "lazy/optimized-hidden-paths.json",
    "linear_lazy_oracle_v2": "lazy/optimized-frozen-v2.json",
    "linear_lazy_oracle_v3": "lazy/optimized-frozen-v3.json",
    "linear_lazy_performance_correctness_v6": "lazy/optimized-frozen-v6.json",
    "linear_lazy_official_cpython": "lazy/optimized-official-upstream.json",
    "exact_tail_repeat_smoke": "lazy/tail-counter-smoke.json",
    "exact_tail_repeat_differential": "lazy/tail-counter-65536.json",
    "exact_tail_manual_differential": "lazy/tail-focused-manual.json",
    "exact_tail_seeded_differential": "lazy/tail-focused-4096.json",
    "exact_tail_hidden_surface": "lazy/tail-hidden-paths.json",
    "exact_tail_oracle_v2": "lazy/tail-frozen-v2.json",
    "exact_tail_oracle_v3": "lazy/tail-frozen-v3.json",
    "exact_tail_performance_correctness_v6": "lazy/tail-frozen-v6.json",
    "exact_tail_official_cpython": "lazy/tail-official-upstream.json",
}

PILOTS = {
    "first_corrected_counted_repeat_calibration": {
        "before_summary": "core-wide-calibration-pilot.json",
        "before_raw": "core-wide-calibration-pilot-raw.jsonl",
        "after_summary": "counter-calibration-pilot.json",
        "after_raw": "counter-calibration-pilot-raw.jsonl",
    },
    "counted_repeat_broad_calibration": {
        "before_summary": "core-wide-calibration-pilot.json",
        "before_raw": "core-wide-calibration-pilot-raw.jsonl",
        "after_summary": "hybrid-calibration-pilot.json",
        "after_raw": "hybrid-calibration-pilot-raw.jsonl",
    },
    "linear_lazy_broad_calibration": {
        "before_summary": "lazy/baseline-calibration.json",
        "before_raw": "lazy/baseline-calibration-raw.jsonl",
        "after_summary": "lazy/optimized-calibration.json",
        "after_raw": "lazy/optimized-calibration-raw.jsonl",
    },
    "linear_lazy_size_scaling_calibration": {
        "before_summary": "lazy/baseline-lazy-scale.json",
        "before_raw": "lazy/baseline-lazy-scale-raw.jsonl",
        "after_summary": "lazy/optimized-lazy-scale.json",
        "after_raw": "lazy/optimized-lazy-scale-raw.jsonl",
    },
}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_source(root: Path, relative: str) -> dict:
    raw = (root / relative).read_bytes()
    return {
        "path": relative,
        "sha256": sha256(raw),
        "bytes": len(raw),
        "text": raw.decode("utf-8"),
    }


def load_json(root: Path, relative: str) -> dict:
    raw = (root / relative).read_bytes()
    return {
        "path": relative,
        "sha256": sha256(raw),
        "bytes": len(raw),
        "text": raw.decode("utf-8"),
        "result": json.loads(raw),
    }


def source_patch(sources: dict, original: str, corrected: str, status: str) -> dict:
    previous = sources[original]
    current = sources[corrected]
    patch = "".join(
        difflib.unified_diff(
            previous["text"].splitlines(keepends=True),
            current["text"].splitlines(keepends=True),
            fromfile=previous["path"],
            tofile=current["path"],
        )
    )
    encoded = patch.encode("utf-8")
    return {
        "original_source": original,
        "corrected_source": corrected,
        "original_sha256": previous["sha256"],
        "corrected_sha256": current["sha256"],
        "status": status,
        "patch_sha256": sha256(encoded),
        "patch_bytes": len(encoded),
        "unified_diff": patch,
    }


def load_raw(root: Path, relative: str, summary: dict) -> dict:
    raw = (root / relative).read_bytes()
    digest = sha256(raw)
    if digest != summary["raw_sha256"]:
        raise ValueError(f"paired raw timing hash differs: {relative}")

    text = raw.decode("utf-8")
    rows = [json.loads(line) for line in text.splitlines()]
    if len(rows) != summary["rows"]:
        raise ValueError(f"paired raw timing row count differs: {relative}")
    if any(row["cohort"] != "calibration" for row in rows):
        raise ValueError(f"non-calibration timing row: {relative}")
    return {
        "path": relative,
        "sha256": digest,
        "bytes": len(raw),
        "rows": len(rows),
        "jsonl": text,
    }


def geomean(values) -> float:
    values = list(values)
    if not values or any(value <= 0 for value in values):
        raise ValueError("geometric comparison requires positive measurements")
    return math.exp(statistics.fmean(map(math.log, values)))


def elapsed_regression_gt_20_percent(
    reference_nanoseconds: float, candidate_nanoseconds: float
) -> bool:
    if reference_nanoseconds <= 0 or candidate_nanoseconds <= 0:
        raise ValueError("regression comparison requires positive elapsed time")
    return (
        candidate_nanoseconds * REGRESSION_SPEEDUP_NUMERATOR
        > reference_nanoseconds * REGRESSION_SPEEDUP_DENOMINATOR
    )


def speedup_regression_gt_20_percent(speedup: float) -> bool:
    if speedup <= 0:
        raise ValueError("regression comparison requires a positive speedup")
    return speedup < (
        REGRESSION_SPEEDUP_NUMERATOR / REGRESSION_SPEEDUP_DENOMINATOR
    )


def validate_regression_boundary() -> None:
    if elapsed_regression_gt_20_percent(100, 120):
        raise ValueError("exactly 20% slower must not count as more than 20%")
    if not elapsed_regression_gt_20_percent(100, math.nextafter(120.0, math.inf)):
        raise ValueError("the first elapsed value above 20% must be included")

    boundary = REGRESSION_SPEEDUP_NUMERATOR / REGRESSION_SPEEDUP_DENOMINATOR
    if speedup_regression_gt_20_percent(boundary):
        raise ValueError("the exact 5/6 speedup boundary must be excluded")
    if not speedup_regression_gt_20_percent(math.nextafter(boundary, -math.inf)):
        raise ValueError("the first speedup below 5/6 must be included")
    if not speedup_regression_gt_20_percent(0.81):
        raise ValueError("a speedup between 0.8 and 5/6 is over 20% slower")
    if speedup_regression_gt_20_percent(0.84):
        raise ValueError("a speedup over 5/6 is not over 20% slower")


def corrected_rankings(summary: dict) -> list[dict]:
    result = []
    for ranking in summary["rankings"]:
        rows = [
            row
            for row in summary["case_results"]
            if ranking["cohort"] == "all" or row["cohort"] == ranking["cohort"]
        ]
        if len(rows) != ranking["cases"]:
            raise ValueError("pilot ranking changed its case denominator")
        corrected = dict(ranking)
        corrected["legacy_speedup_below_0_8_cases"] = ranking.get("slow")
        corrected["slow"] = sum(
            speedup_regression_gt_20_percent(row["speedup"]) for row in rows
        )
        corrected["slow_definition"] = "candidate elapsed time > reference × 1.2"
        corrected["slow_speedup_boundary"] = "strictly below 5/6"
        result.append(corrected)
    return result


def compare_pilot(before: dict, after: dict) -> dict:
    validate_regression_boundary()
    for name, summary in (("before", before), ("after", after)):
        if summary["schema"] != "rebar-rust-v6-loss-probe-v1":
            raise ValueError(f"unexpected {name} pilot schema")
        if summary["cohort_selection"] != "calibration":
            raise ValueError(f"{name} pilot is not calibration-only")
        if summary["expected_sha256"] != EXPECTED_PERFORMANCE:
            raise ValueError(f"{name} pilot changed the frozen v6 fixture")
        if "not a full frozen-holdout result" not in summary["measurement"]:
            raise ValueError(f"{name} pilot lost its holdout disclaimer")

    old = {row["case"]: row for row in before["case_results"]}
    new = {row["case"]: row for row in after["case_results"]}
    if set(old) != set(new):
        raise ValueError("before and after pilots do not use identical cases")
    if before["trials"] != after["trials"]:
        raise ValueError("before and after pilots use different trial counts")
    confidence_fields = (
        "interval_method",
        "bootstrap_seed",
        "bootstraps",
        "frozen_bootstraps",
        "frozen_trials",
        "order_seed",
        "trials",
        "warmups",
    )
    for field in confidence_fields:
        if before[field] != after[field]:
            raise ValueError(f"paired confidence metadata changed: {field}")

    cases = []
    for case in sorted(old):
        previous = old[case]
        current = new[case]
        if previous["category"] != current["category"]:
            raise ValueError(f"paired category changed: {case}")
        if previous["cohort"] != "calibration" or current["cohort"] != "calibration":
            raise ValueError(f"non-calibration case in paired pilot: {case}")

        direct = previous["rust_ns"] / current["rust_ns"]
        slowdown = current["rust_ns"] / previous["rust_ns"] - 1
        direct_regression = elapsed_regression_gt_20_percent(
            previous["rust_ns"], current["rust_ns"]
        )
        previous_stdlib_regression = speedup_regression_gt_20_percent(
            previous["speedup"]
        )
        corrected_stdlib_regression = speedup_regression_gt_20_percent(
            current["speedup"]
        )
        cases.append(
            {
                "case": case,
                "category": previous["category"],
                "previous_rust_ns_per_operation": previous["rust_ns"],
                "corrected_rust_ns_per_operation": current["rust_ns"],
                "previous_stdlib_ns_per_operation": previous["baseline_ns"],
                "corrected_stdlib_ns_per_operation": current["baseline_ns"],
                "previous_speedup_against_stdlib": previous["speedup"],
                "corrected_speedup_against_stdlib": current["speedup"],
                "previous_stdlib_ci95_low": previous["ci95_low"],
                "previous_stdlib_ci95_high": previous["ci95_high"],
                "corrected_stdlib_ci95_low": current["ci95_low"],
                "corrected_stdlib_ci95_high": current["ci95_high"],
                "direct_rust_speedup": direct,
                "direct_rust_elapsed_regression_fraction": max(0.0, slowdown),
                "direct_rust_elapsed_regression_gt_20_percent": direct_regression,
                "previous_stdlib_regression_gt_20_percent": previous_stdlib_regression,
                "corrected_stdlib_regression_gt_20_percent": corrected_stdlib_regression,
                "legacy_previous_stdlib_speedup_below_0_8": previous[
                    "regression_gt_20pct"
                ],
                "legacy_corrected_stdlib_speedup_below_0_8": current[
                    "regression_gt_20pct"
                ],
            }
        )

    grouped: dict[str, list[dict]] = collections.defaultdict(list)
    for row in cases:
        grouped[row["category"]].append(row)
    old_families = {row["category"]: row for row in before["families"]}
    new_families = {row["category"]: row for row in after["families"]}
    families = []
    for category, rows in sorted(grouped.items()):
        families.append(
            {
                "category": category,
                "cases": len(rows),
                "direct_rust_geomean_speedup": geomean(
                    row["direct_rust_speedup"] for row in rows
                ),
                "previous_stdlib_geomean_speedup": old_families[category][
                    "speedup"
                ],
                "previous_stdlib_ci95_low": old_families[category][
                    "ci95_low"
                ],
                "previous_stdlib_ci95_high": old_families[category][
                    "ci95_high"
                ],
                "corrected_stdlib_geomean_speedup": new_families[category][
                    "speedup"
                ],
                "corrected_stdlib_ci95_low": new_families[category][
                    "ci95_low"
                ],
                "corrected_stdlib_ci95_high": new_families[category][
                    "ci95_high"
                ],
                "direct_rust_elapsed_regressions_gt_20_percent": sum(
                    row["direct_rust_elapsed_regression_gt_20_percent"]
                    for row in rows
                ),
                "previous_stdlib_regressions_gt_20_percent": sum(
                    row["previous_stdlib_regression_gt_20_percent"]
                    for row in rows
                ),
                "corrected_stdlib_regressions_gt_20_percent": sum(
                    row["corrected_stdlib_regression_gt_20_percent"]
                    for row in rows
                ),
            }
        )

    return {
        "measurement": "diagnostic pilot; not a full frozen-holdout result",
        "cohort": "calibration",
        "frozen_expected_sha256": EXPECTED_PERFORMANCE,
        "regression_definition": "candidate elapsed time > reference × 1.2",
        "regression_speedup_boundary": "strictly below 5/6",
        "cases": len(cases),
        "trials_per_case": before["trials"],
        "confidence_interval_metadata": {
            "level": 0.95,
            "method": before["interval_method"],
            "bootstrap_samples": before["bootstraps"],
            "bootstrap_seed": before["bootstrap_seed"],
            "paired_order_seed": before["order_seed"],
            "paired_trials_per_case": before["trials"],
            "frozen_bootstrap_samples": before["frozen_bootstraps"],
            "frozen_trials": before["frozen_trials"],
            "warmups": before["warmups"],
        },
        "previous_correctness_checks": before["correctness_checks"],
        "corrected_correctness_checks": after["correctness_checks"],
        "direct_rust_geomean_speedup": geomean(
            row["direct_rust_speedup"] for row in cases
        ),
        "previous_stdlib_ranking": corrected_rankings(before),
        "corrected_stdlib_ranking": corrected_rankings(after),
        "families": families,
        "case_results": cases,
        "direct_rust_elapsed_regressions_gt_20_percent": [
            row
            for row in cases
            if row["direct_rust_elapsed_regression_gt_20_percent"]
        ],
        "corrected_stdlib_regressions_gt_20_percent": [
            row for row in cases if row["corrected_stdlib_regression_gt_20_percent"]
        ],
        "previous_stdlib_regressions_gt_20_percent": [
            row for row in cases if row["previous_stdlib_regression_gt_20_percent"]
        ],
    }


def load_pilot(root: Path, paths: dict) -> dict:
    before = load_json(root, paths["before_summary"])
    after = load_json(root, paths["after_summary"])
    before_raw = load_raw(root, paths["before_raw"], before["result"])
    after_raw = load_raw(root, paths["after_raw"], after["result"])
    return {
        "before_summary": before,
        "before_raw": before_raw,
        "after_summary": after,
        "after_raw": after_raw,
        "comparison": compare_pilot(before["result"], after["result"]),
    }


def validate_gate_results(gates: dict) -> None:
    original = gates["original_rejected_repeat"]["result"]
    rejected = gates["first_rejected_repeat_patch"]["result"]
    if original["failed"] != 24 or len(original["failures"]) != 24:
        raise ValueError("the original 24 repeat failures were not retained")
    if rejected["failed"] != 8 or len(rejected["failures"]) != 8:
        raise ValueError("the rejected patch's eight repeat failures were not retained")

    for name in (
        "corrected_first_repeat_full",
        "corrected_isolated_repeat",
        "corrected_integrated_repeat",
        "linear_lazy_repeat_differential",
        "exact_tail_repeat_differential",
    ):
        report = gates[name]["result"]
        if (
            report["failed"] != 0
            or report["correctness_checks"] != 343436
            or report["seeded_cases"] != 65536
            or report["seed"] != REPEAT_SEED
            or report["python"] != ORACLE_PYTHON
        ):
            raise ValueError(f"incomplete pinned 343,436-check repeat gate: {name}")

    focused = gates["exact_tail_seeded_differential"]["result"]
    if (
        focused["failed"] != 0
        or focused["correctness_checks"] != 219587
        or focused["seeded_cases"] != 4096
        or focused["extended_window_checks"] != 11186
        or focused["python"] != ORACLE_PYTHON
    ):
        raise ValueError("incomplete focused 219,587-check lazy-tail gate")

    for name, entry in gates.items():
        if name in ("original_rejected_repeat", "first_rejected_repeat_patch"):
            continue
        result = entry["result"]
        if result.get("failed") != 0:
            raise ValueError(f"preserved correctness gate failed: {name}")
        if "official_cpython" in name and (
            result["passed"] != 144
            or result["skipped"] != 2
            or result["crashes"] != 0
            or result["timeouts"] != 0
        ):
            raise ValueError(f"official pinned CPython test result drift: {name}")


def validate_json_record(name: str, record: dict) -> None:
    payload = record["text"].encode("utf-8")
    if sha256(payload) != record["sha256"] or len(payload) != record["bytes"]:
        raise ValueError(f"preserved exact JSON hash drift: {name}")
    if json.loads(payload) != record["result"]:
        raise ValueError(f"preserved exact JSON content drift: {name}")


def build_archive(root: Path) -> dict:
    gates = {name: load_json(root, path) for name, path in GATES.items()}
    validate_gate_results(gates)
    sources = {name: load_source(root, path) for name, path in SOURCES.items()}
    return {
        "schema": SCHEMA,
        "oracle_python": ORACLE_PYTHON,
        "counted_repeat_seed": REPEAT_SEED,
        "holdout": "NOT MEASURED; all timing rows are frozen calibration only",
        "external_regex_delegation": "none; isolated Rust source is preserved",
        "tail_filter_status": (
            "correctness-qualified; not integrated; performance NOT MEASURED"
        ),
        "source_snapshots": sources,
        "source_patches": {
            name: source_patch(sources, original, corrected, status)
            for name, (original, corrected, status) in PATCHES.items()
        },
        "correctness_gates": gates,
        "calibration_pilots": {
            name: load_pilot(root, paths) for name, paths in PILOTS.items()
        },
    }


def encode_archive(bundle: dict) -> bytes:
    payload = (
        json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    return gzip.compress(payload, compresslevel=6, mtime=0)


def validate_archive(bundle: dict) -> dict:
    validate_regression_boundary()
    if bundle.get("schema") != SCHEMA:
        raise ValueError("unexpected repeat-lab archive schema")
    if bundle.get("oracle_python") != ORACLE_PYTHON:
        raise ValueError("repeat lab does not use pinned CPython 3.14.6")
    if set(bundle["source_snapshots"]) != set(SOURCES):
        raise ValueError("repeat-lab source snapshots were omitted or replaced")
    if set(bundle["correctness_gates"]) != set(GATES):
        raise ValueError("repeat-lab correctness gates were omitted or replaced")
    if set(bundle["calibration_pilots"]) != set(PILOTS):
        raise ValueError("repeat-lab calibration pilots were omitted or replaced")
    if set(bundle["source_patches"]) != set(PATCHES):
        raise ValueError("repeat-lab source patches were omitted or replaced")

    for name, source in bundle["source_snapshots"].items():
        raw = source["text"].encode("utf-8")
        if sha256(raw) != source["sha256"] or len(raw) != source["bytes"]:
            raise ValueError(f"preserved Rust source hash drift: {name}")

    for name, (original, corrected, status) in PATCHES.items():
        expected = source_patch(
            bundle["source_snapshots"], original, corrected, status
        )
        if expected != bundle["source_patches"][name]:
            raise ValueError(f"preserved exact Rust source patch drift: {name}")

    for name, gate in bundle["correctness_gates"].items():
        validate_json_record(name, gate)

    validate_gate_results(bundle["correctness_gates"])
    for name, pilot in bundle["calibration_pilots"].items():
        for label in ("before", "after"):
            validate_json_record(f"{name}/{label}", pilot[f"{label}_summary"])
            raw = pilot[f"{label}_raw"]
            payload = raw["jsonl"].encode("utf-8")
            if sha256(payload) != raw["sha256"]:
                raise ValueError(f"preserved pilot raw hash drift: {name}/{label}")
            if len(payload) != raw["bytes"]:
                raise ValueError(f"preserved pilot raw size drift: {name}/{label}")
            rows = [json.loads(line) for line in raw["jsonl"].splitlines()]
            if len(rows) != raw["rows"]:
                raise ValueError(f"preserved pilot raw row drift: {name}/{label}")
            if any(row["cohort"] != "calibration" for row in rows):
                raise ValueError(f"holdout row entered repeat lab: {name}/{label}")
        expected = compare_pilot(
            pilot["before_summary"]["result"],
            pilot["after_summary"]["result"],
        )
        if expected != pilot["comparison"]:
            raise ValueError(f"paired pilot comparison drift: {name}")

    return {
        "schema": SCHEMA,
        "valid": True,
        "oracle_python": ORACLE_PYTHON,
        "original_repeat_failures": 24,
        "rejected_patch_failures": 8,
        "corrected_seeded_checks": 343436,
        "corrected_seeded_failures": 0,
        "source_snapshots": len(bundle["source_snapshots"]),
        "source_patches": len(bundle["source_patches"]),
        "correctness_gates": len(bundle["correctness_gates"]),
        "calibration_pilots": len(bundle["calibration_pilots"]),
        "holdout": "NOT MEASURED",
        "regression_definition": "candidate elapsed time > reference × 1.2",
        "regression_speedup_boundary": "strictly below 5/6",
        "tail_filter": "correctness-qualified; performance NOT MEASURED",
        "pilots": {
            name: {
                "cases": pilot["comparison"]["cases"],
                "direct_rust_geomean_speedup": pilot["comparison"][
                    "direct_rust_geomean_speedup"
                ],
                "direct_rust_elapsed_regressions_gt_20_percent": len(
                    pilot["comparison"][
                        "direct_rust_elapsed_regressions_gt_20_percent"
                    ]
                ),
                "corrected_stdlib_regressions_gt_20_percent": len(
                    pilot["comparison"]["corrected_stdlib_regressions_gt_20_percent"]
                ),
                "previous_stdlib_regressions_gt_20_percent": len(
                    pilot["comparison"]["previous_stdlib_regressions_gt_20_percent"]
                ),
            }
            for name, pilot in bundle["calibration_pilots"].items()
        },
    }


def capture(args: argparse.Namespace) -> None:
    bundle = build_archive(args.research_dir)
    summary = validate_archive(bundle)
    encoded = encode_archive(bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                **summary,
                "archive": str(args.output),
                "archive_bytes": len(encoded),
                "archive_sha256": sha256(encoded),
            },
            sort_keys=True,
        )
    )


def verify(args: argparse.Namespace) -> None:
    raw = args.input.read_bytes()
    bundle = json.loads(gzip.decompress(raw))
    print(
        json.dumps(
            {
                **validate_archive(bundle),
                "archive": str(args.input),
                "archive_bytes": len(raw),
                "archive_sha256": sha256(raw),
                "deterministic_gzip": encode_archive(bundle) == raw,
            },
            sort_keys=True,
        )
    )


def extract(args: argparse.Namespace) -> None:
    compressed = args.input.read_bytes()
    bundle = json.loads(gzip.decompress(compressed))
    validate_archive(bundle)

    files: dict[str, bytes] = {}

    def add(relative: str, text: str) -> None:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe archived output path: {relative}")
        payload = text.encode("utf-8")
        previous = files.get(relative)
        if previous is not None and previous != payload:
            raise ValueError(f"inconsistent archived duplicate: {relative}")
        files[relative] = payload

    for source in bundle["source_snapshots"].values():
        add(source["path"], source["text"])
    for gate in bundle["correctness_gates"].values():
        add(gate["path"], gate["text"])
    for pilot in bundle["calibration_pilots"].values():
        for label in ("before", "after"):
            summary = pilot[f"{label}_summary"]
            raw = pilot[f"{label}_raw"]
            add(summary["path"], summary["text"])
            add(raw["path"], raw["jsonl"])

    destinations = [args.directory / relative for relative in sorted(files)]
    existing = [str(path) for path in destinations if path.exists()]
    if existing:
        raise FileExistsError(
            "repeat-lab extraction refuses to overwrite: " + ", ".join(existing)
        )

    for path in destinations:
        path.parent.mkdir(parents=True, exist_ok=True)
        relative = str(path.relative_to(args.directory))
        path.write_bytes(files[relative])

    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "archive_sha256": sha256(compressed),
                "directory": str(args.directory),
                "files": len(files),
                "overwrites": 0,
                "holdout": "NOT MEASURED",
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    record = commands.add_parser(
        "capture", help="archive already-recorded isolated repeat results"
    )
    record.add_argument("--research-dir", type=Path, default=DEFAULT_RESEARCH)
    record.add_argument("--output", type=Path, default=DEFAULT_ARCHIVE)
    record.set_defaults(function=capture)

    inspect = commands.add_parser(
        "verify", help="check all archived hashes, failures and calibration rows"
    )
    inspect.add_argument("--input", type=Path, default=DEFAULT_ARCHIVE)
    inspect.set_defaults(function=verify)

    replay = commands.add_parser(
        "extract", help="recover exact source, gates and raw evidence without overwriting"
    )
    replay.add_argument("--input", type=Path, default=DEFAULT_ARCHIVE)
    replay.add_argument("--directory", type=Path, required=True)
    replay.set_defaults(function=extract)

    args = parser.parse_args()
    if sys.implementation.name != "cpython" or sys.version_info[:3] != (3, 14, 6):
        raise SystemExit("repeat-lab evidence requires pinned CPython 3.14.6")
    args.function(args)


if __name__ == "__main__":
    main()
