#!/usr/bin/env python3
"""Rank Rust optimization opportunities using only frozen practice workloads."""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path

from tools.perf_v5 import digest, source_kind
from tools.perf_v7 import (
    REGRESSION_SPEEDUP_THRESHOLD,
    ROOT,
    is_runtime_regression,
    verify_regression_boundaries,
)
from tools.rust_v7_calibration_pilot import (
    DEFAULT_FIXTURE,
    DEFAULT_FIXTURE_MANIFEST,
    decode_calibration_expected,
    load_calibration_fixture,
)


SCHEMA = "rebar-rust-practice-priorities-v7"
PRACTICE = "calibration"
RUST = "candidates.rust_candidate"
ZIG = "candidates.zig_candidate"
C_ENGINE = "candidates.vm_candidate"
PYTHON_ENGINE = "candidates.ast_candidate"
DEFAULT_SUMMARY = DEFAULT_FIXTURE
DEFAULT_OUTPUT = ROOT / "candidates/evidence/rust-v7-calibration-priorities.json.gz"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def positive_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def practice_index(
    summary: dict,
    practice_cases: dict[str, dict],
    candidates: tuple[str, ...],
) -> dict[tuple[str, str], dict]:
    """Read only practice results; do not derive any hidden-case information."""
    rows = summary.get("case_results")
    require(isinstance(rows, list), "complete candidate performance results are missing")
    indexed: dict[tuple[str, str], dict] = {}
    for row in rows:
        require(isinstance(row, dict), "a candidate performance result is not an object")
        require(row.get("cohort") == PRACTICE, "mixed-cohort candidate results are forbidden")
        case_id = row.get("case")
        candidate = row.get("candidate")
        case = practice_cases.get(case_id)
        require(case is not None, f"unfrozen practice workload: {case_id!r}")
        require(candidate in candidates, f"unknown practice candidate: {candidate!r}")
        key = (case_id, candidate)
        require(key not in indexed, f"duplicate practice result: {key}")
        require(row.get("category") == case["category"], f"changed practice workload: {key}")
        require(row.get("weight") == case["weight"], f"changed practice weight: {key}")
        speedup = row.get("speedup")
        require(positive_number(speedup), f"invalid practice speed: {key}")
        for field in ("ci95_low", "ci95_high"):
            require(positive_number(row.get(field)), f"invalid practice confidence interval: {key}")
        require(row["ci95_low"] <= row["ci95_high"], f"inverted practice interval: {key}")
        require(
            row.get("statistically_faster") is (row["ci95_low"] > 1.0),
            f"changed practice confidence flag: {key}",
        )
        require(
            row.get("regression_gt_20pct") is is_runtime_regression(speedup),
            f"changed strictly-more-than-20% practice flag: {key}",
        )
        memory = row.get("peak_traced_ratio")
        require(
            isinstance(memory, (int, float))
            and not isinstance(memory, bool)
            and math.isfinite(memory)
            and memory >= 0,
            f"invalid practice memory: {key}",
        )
        indexed[key] = row
    expected = len(practice_cases) * len(candidates)
    require(
        len(indexed) == expected,
        f"incomplete practice-only candidate results: {len(indexed)} != {expected}",
    )
    for case_id in practice_cases:
        for candidate in candidates:
            require((case_id, candidate) in indexed, f"missing practice result: {(case_id, candidate)}")
    return indexed


def group_name(length: int) -> str:
    if length <= 16:
        return "0–16"
    if length <= 64:
        return "17–64"
    if length <= 256:
        return "65–256"
    if length <= 1024:
        return "257–1,024"
    if length <= 4096:
        return "1,025–4,096"
    if length <= 16384:
        return "4,097–16,384"
    if length <= 65536:
        return "16,385–65,536"
    return "65,537+"


def cardinality(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, (list, tuple)):
        return len(value)
    return 1


def count_bucket(value: int) -> str:
    if value == 0:
        return "no result"
    if value == 1:
        return "one result"
    if value <= 4:
        return "2–4 results"
    if value <= 16:
        return "5–16 results"
    if value <= 64:
        return "17–64 results"
    return "65+ results"


def geometric(values: list[float]) -> float:
    require(bool(values), "cannot calculate an empty practice group")
    require(all(positive_number(value) for value in values), "practice geometric mean contains invalid speed")
    return math.exp(statistics.fmean(math.log(value) for value in values))


def practice_rows(
    cases: dict[str, dict],
    expected: dict[str, dict],
    index: dict[tuple[str, str], dict],
) -> list[dict]:
    result = []
    for case_id, case in sorted(cases.items()):
        rust = index[case_id, RUST]
        zig = index[case_id, ZIG]
        c_engine = index[case_id, C_ENGINE]
        python_engine = index[case_id, PYTHON_ENGINE]
        value = case.get("string")
        if value is None:
            value = case.get("pattern")
        length = len(value) if isinstance(value, (str, bytes, bytearray, memoryview)) else 0
        output_count = cardinality(expected[case_id]["result"])
        rust_speed = rust["speedup"]
        zig_speed = zig["speedup"]
        result.append(
            {
                "case": case_id,
                "cohort": PRACTICE,
                "category": case["category"],
                "api": case["api"],
                "lifecycle": case["lifecycle"],
                "input_kind": source_kind(case),
                "input_length": length,
                "input_length_bucket": group_name(length),
                "result_count": output_count,
                "result_count_bucket": count_bucket(output_count),
                "operations_per_trial": case["ops"],
                "ignore_case": "I" in case["flags"],
                "bounded_window": "pos" in case or "endpos" in case,
                "rust_speedup": rust_speed,
                "rust_ci95_low": rust["ci95_low"],
                "rust_ci95_high": rust["ci95_high"],
                "rust_statistically_faster": rust["statistically_faster"],
                "rust_regression_gt_20pct": rust["regression_gt_20pct"],
                "rust_peak_traced_ratio": rust["peak_traced_ratio"],
                "zig_speedup": zig_speed,
                "c_engine_speedup": c_engine["speedup"],
                "python_engine_speedup": python_engine["speedup"],
                "rust_relative_to_zig": rust_speed / zig_speed,
                "rust_relative_to_c_engine": rust_speed / c_engine["speedup"],
                "baseline_log_opportunity": max(0.0, -math.log(rust_speed)),
                "zig_log_opportunity": max(0.0, math.log(zig_speed / rust_speed)),
                "expected_result_sha256": expected[case_id]["result_sha256"],
            }
        )
    require(len(result) == len(cases), "a practice optimization workload was omitted")
    require(all(row["cohort"] == PRACTICE for row in result), "non-practice workload leaked")
    return result


def summarize(rows: list[dict], fields: tuple[str, ...]) -> list[dict]:
    values: dict[tuple[object, ...], list[dict]] = collections.defaultdict(list)
    for row in rows:
        values[tuple(row[field] for field in fields)].append(row)

    result = []
    for key, members in values.items():
        baseline_score = math.fsum(row["baseline_log_opportunity"] for row in members)
        zig_score = math.fsum(row["zig_log_opportunity"] for row in members)
        result.append(
            {
                **dict(zip(fields, key, strict=True)),
                "cases": len(members),
                "rust_geomean_speedup": geometric([row["rust_speedup"] for row in members]),
                "zig_geomean_speedup": geometric([row["zig_speedup"] for row in members]),
                "c_engine_geomean_speedup": geometric(
                    [row["c_engine_speedup"] for row in members]
                ),
                "rust_relative_to_zig_geomean": geometric(
                    [row["rust_relative_to_zig"] for row in members]
                ),
                "rust_relative_to_c_engine_geomean": geometric(
                    [row["rust_relative_to_c_engine"] for row in members]
                ),
                "rust_significantly_faster_cases": sum(
                    row["rust_statistically_faster"] for row in members
                ),
                "rust_regressions_gt_20pct": sum(
                    row["rust_regression_gt_20pct"] for row in members
                ),
                "rust_median_peak_traced_ratio": statistics.median(
                    row["rust_peak_traced_ratio"] for row in members
                ),
                "baseline_log_opportunity": baseline_score,
                "zig_log_opportunity": zig_score,
                "median_input_length": statistics.median(
                    row["input_length"] for row in members
                ),
                "median_result_count": statistics.median(
                    row["result_count"] for row in members
                ),
            }
        )
    result.sort(
        key=lambda row: (
            -row["baseline_log_opportunity"],
            -row["zig_log_opportunity"],
            tuple(str(row[field]) for field in fields),
        )
    )
    require(sum(row["cases"] for row in result) == len(rows), f"incomplete {fields} grouping")
    require(
        math.isclose(
            math.fsum(row["baseline_log_opportunity"] for row in result),
            math.fsum(row["baseline_log_opportunity"] for row in rows),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ),
        f"changed baseline opportunity denominator: {fields}",
    )
    require(
        math.isclose(
            math.fsum(row["zig_log_opportunity"] for row in result),
            math.fsum(row["zig_log_opportunity"] for row in rows),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ),
        f"changed Zig opportunity denominator: {fields}",
    )
    return result


def validate_practice_rankings(
    summary: dict,
    rows: list[dict],
    candidates: tuple[str, ...],
) -> list[dict]:
    rankings = summary.get("rankings")
    require(isinstance(rankings, list), "frozen candidate rankings are missing")
    selected = {}
    for row in rankings:
        require(isinstance(row, dict), "a frozen ranking is not an object")
        if row.get("cohort") != PRACTICE:
            continue
        candidate = row.get("candidate")
        require(candidate in candidates, f"unexpected practice ranking: {candidate}")
        require(candidate not in selected, f"duplicate practice ranking: {candidate}")
        require(row.get("cases") == len(rows), f"changed practice ranking denominator: {candidate}")
        require(row.get("weight") == len(rows), f"changed practice ranking weight: {candidate}")
        selected[candidate] = row
    require(set(selected) == set(candidates), "an independent practice ranking is missing")
    rust = selected[RUST]
    recomputed = geometric([row["rust_speedup"] for row in rows])
    require(
        math.isclose(rust["geomean_speedup"], recomputed, rel_tol=1e-12, abs_tol=1e-15),
        "the complete Rust practice speed does not reproduce individual practice cases",
    )
    require(
        rust["statistically_faster_cases"]
        == sum(row["rust_statistically_faster"] for row in rows),
        "the complete Rust practice confidence count changed",
    )
    require(
        rust["regressions_gt_20pct"]
        == sum(row["rust_regression_gt_20pct"] for row in rows),
        "the complete Rust practice slowdown denominator changed",
    )
    return sorted(selected.values(), key=lambda row: (-row["geomean_speedup"], row["candidate"]))


def self_test() -> dict:
    boundary = verify_regression_boundaries()
    require(REGRESSION_SPEEDUP_THRESHOLD == 5.0 / 6.0, "strict 20% runtime rule changed")
    fake_cases = {
        "cal.one": {"category": "one", "weight": 1},
        "cal.two": {"category": "two", "weight": 1},
    }
    fake_candidates = ("rust", "zig")

    def measured(case: str, candidate: str, speed: float) -> dict:
        return {
            "case": case,
            "cohort": PRACTICE,
            "category": fake_cases[case]["category"],
            "candidate": candidate,
            "weight": 1,
            "speedup": speed,
            "ci95_low": speed,
            "ci95_high": speed,
            "statistically_faster": speed > 1.0,
            "regression_gt_20pct": is_runtime_regression(speed),
            "peak_traced_ratio": 1.0,
        }

    base = [
        measured("cal.one", "rust", 0.81),
        measured("cal.one", "zig", 1.7),
        measured("cal.two", "rust", 1.2),
        measured("cal.two", "zig", 1.4),
    ]
    clean = {"case_results": base}
    baseline = practice_index(clean, fake_cases, fake_candidates)
    hidden_variants = (
        {"cohort": "holdout", "case": "hold.secret", "candidate": "rust", "speedup": 0.001},
        {"cohort": "holdout", "case": "hold.secret", "candidate": "zig", "speedup": 900.0},
        {"cohort": "holdout", "case": "totally different", "candidate": "not a candidate"},
    )
    rejected_hidden = 0
    for variant in hidden_variants:
        mutated = {"case_results": [*base, variant]}
        try:
            practice_index(mutated, fake_cases, fake_candidates)
        except RuntimeError:
            rejected_hidden += 1
        else:
            raise RuntimeError("mixed-cohort optimization evidence was accepted")

    safe_case = {"id": "cal.poison", "cohort": PRACTICE, "category": "one"}
    safe_result = {
        "id": safe_case["id"],
        "cohort": PRACTICE,
        "category": safe_case["category"],
        "result": ["practice", 1],
    }
    safe_result["result_sha256"] = digest(safe_result["result"])
    safe_line = (
        json.dumps(safe_result, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    poison = (
        b'{"category":"hidden","cohort":"holdout","id":"hold.poison",'
        b'"result":MUST_NEVER_BE_DESERIALIZED}\n'
    )
    decoded: list[bytes] = []

    def reject_hidden_decode(raw: bytes) -> dict:
        require(b'"cohort":"holdout"' not in raw, "a hidden result reached the practice JSON decoder")
        decoded.append(raw)
        return json.loads(raw)

    require(
        decode_calibration_expected(
            (poison, safe_line, poison),
            {safe_case["id"]: safe_case},
            decoder=reject_hidden_decode,
        ) == {safe_case["id"]: safe_result},
        "opaque hidden bytes changed practice-only priorities",
    )
    require(decoded == [safe_line], "a hidden result was decoded for practice-only priorities")

    rejected = 0
    corrupted = (
        {"case_results": base[:-1]},
        {"case_results": [*base, base[0]]},
        {
            "case_results": [
                {**row, "regression_gt_20pct": False} if index == 0 else row
                for index, row in enumerate(base)
            ]
        },
        {
            "case_results": [
                {**row, "ci95_low": 2.0, "ci95_high": 1.0} if index == 0 else row
                for index, row in enumerate(base)
            ]
        },
    )
    for mutation in corrupted:
        try:
            practice_index(mutation, fake_cases, fake_candidates)
        except RuntimeError:
            rejected += 1
        else:
            raise RuntimeError("practice-only optimizer accepted corrupted calibration evidence")

    return {
        "schema": f"{SCHEMA}-self-test",
        **boundary,
        "hidden_case_noninterference_checks": len(hidden_variants),
        "mixed_cohort_rejections": rejected_hidden,
        "held_out_records_deserialized": 0,
        "poisoned_record_decoder_checks": 2,
        "rejected_corruptions": rejected,
        "holdout_accessed": False,
        "failed": 0,
    }


def historical_candidate_index(
    cases: dict[str, dict],
    history: dict[str, dict],
    candidates: tuple[str, ...],
) -> dict[tuple[str, str], dict]:
    fields = {
        RUST: "rust_speedup",
        ZIG: "zig_speedup",
        C_ENGINE: "c_engine_speedup",
        PYTHON_ENGINE: "python_engine_speedup",
    }
    rows = []
    for identifier, case in cases.items():
        previous = history.get(identifier)
        require(isinstance(previous, dict), f"missing sealed practice history: {identifier}")
        require(previous.get("cohort") == PRACTICE, "hidden row entered sealed practice history")
        for candidate in candidates:
            speed = previous.get(fields[candidate])
            require(positive_number(speed), f"invalid sealed practice speed: {(identifier, candidate)}")
            low = previous.get("rust_ci95_low") if candidate == RUST else speed
            high = previous.get("rust_ci95_high") if candidate == RUST else speed
            rows.append({
                "case": identifier,
                "cohort": PRACTICE,
                "category": case["category"],
                "candidate": candidate,
                "weight": case["weight"],
                "speedup": speed,
                "ci95_low": low,
                "ci95_high": high,
                "statistically_faster": (
                    previous.get("rust_statistically_faster")
                    if candidate == RUST else low > 1.0
                ),
                "regression_gt_20pct": (
                    previous.get("rust_regression_gt_20pct")
                    if candidate == RUST else is_runtime_regression(speed)
                ),
                "peak_traced_ratio": (
                    previous.get("rust_peak_traced_ratio") if candidate == RUST else 1.0
                ),
            })
    return practice_index({"case_results": rows}, cases, candidates)


def prioritize(
    summary_path: Path,
    manifest_path: Path = DEFAULT_FIXTURE_MANIFEST,
) -> dict:
    controls = self_test()
    suite, pairs, manifest, history, fixture_manifest = load_calibration_fixture(
        summary_path, manifest_path
    )
    candidates = tuple(suite.MODULES[1:])
    require(
        set(candidates) == {RUST, ZIG, C_ENGINE, PYTHON_ENGINE},
        "an independent Rust comparison candidate changed",
    )
    cases = {case["id"]: case for _position, case, _expected in pairs}
    want = {case["id"]: expected for _position, case, expected in pairs}
    require(len(cases) == suite.CASES_PER_COHORT == 10_312, "practice workload denominator changed")
    require(set(cases) == set(want), "practice correctness fixtures are incomplete")
    require(set(history) == set(cases), "sealed practice history changed the frozen workload set")
    indexed = historical_candidate_index(cases, history, candidates)
    rows = practice_rows(cases, want, indexed)
    require(
        rows == [history[identifier] for identifier in sorted(cases)],
        "sealed practice rankings do not reproduce every original practice case",
    )
    summary = {"rankings": fixture_manifest["historical_practice_rankings"]}
    rankings = validate_practice_rankings(summary, rows, candidates)

    dimensions = {
        "workload": ("category",),
        "public_operation": ("api",),
        "pattern_lifetime": ("lifecycle",),
        "input_kind": ("input_kind",),
        "input_size": ("input_length_bucket",),
        "result_count": ("result_count_bucket",),
        "case_folding": ("ignore_case",),
        "bounded_window": ("bounded_window",),
        "operation_and_lifetime": ("api", "lifecycle"),
        "operation_and_input": ("api", "input_kind"),
        "workload_and_operation": ("category", "api", "lifecycle"),
    }
    groups = {label: summarize(rows, fields) for label, fields in dimensions.items()}
    return {
        "schema": SCHEMA,
        "python": manifest["python"],
        "cohort": PRACTICE,
        "holdout_accessed": False,
        "timing_performed": False,
        "production_files_modified": False,
        "cases": len(rows),
        "candidate_case_results": len(indexed),
        "engines": ["re", *candidates],
        "expected_sha256": manifest["expected_sha256"],
        "summary_sha256": fixture_manifest["historical_summary_sha256"],
        "raw_sha256": fixture_manifest["historical_raw_sha256"],
        "practice_fixture_sha256": fixture_manifest["fixture_sha256"],
        "practice_fixture_manifest_sha256": file_digest(manifest_path),
        "strict_regression_speedup_threshold": REGRESSION_SPEEDUP_THRESHOLD,
        "ranking_metric": (
            "Sum of positive natural-log Rust slowdowns against unchanged Python "
            "across all frozen practice cases; Zig-gap scores are recorded separately."
        ),
        "confidence_caveat": (
            "Existing case intervals are preserved; category aggregates are descriptive "
            "practice diagnostics, not independently bootstrapped confidence intervals."
        ),
        "practice_rankings": rankings,
        "groups": groups,
        "practice_cases": rows,
        "self_test": controls,
        "failed": 0,
    }


def write_archive(document: dict, destination: Path) -> dict:
    payload = (
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    if destination.exists():
        require(destination.is_file(), f"practice evidence target is not a file: {destination}")
        with gzip.open(destination, "rb") as archive:
            require(
                archive.read() == payload,
                f"refusing to overwrite changed practice evidence: {destination}",
            )
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            with gzip.GzipFile(
                filename="", fileobj=stream, mode="wb", compresslevel=9, mtime=0
            ) as archive:
                archive.write(payload)
    with gzip.open(destination, "rb") as archive:
        require(archive.read() == payload, "practice evidence did not survive gzip round trip")
    with destination.open("rb") as archive:
        header = archive.read(10)
    require(len(header) == 10 and header[:2] == b"\x1f\x8b", "invalid practice gzip")
    require(header[3] & 0x08 == 0, "practice gzip contains a nondeterministic filename")
    require(header[4:8] == b"\0\0\0\0", "practice gzip contains a nondeterministic timestamp")
    resolved = destination.resolve()
    location = (
        str(resolved.relative_to(ROOT.resolve()))
        if resolved.is_relative_to(ROOT.resolve())
        else str(resolved)
    )
    return {
        "path": location,
        "sha256": file_digest(destination),
        "bytes": destination.stat().st_size,
        "restored_sha256": hashlib.sha256(payload).hexdigest(),
        "restored_bytes": len(payload),
        "gzip_mtime": 0,
        "gzip_filename": "",
    }


def headline(group: list[dict], limit: int = 12) -> list[dict]:
    return group[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--summary", "--fixture", dest="summary", type=Path, default=DEFAULT_SUMMARY,
        help="the sealed single-cohort practice fixture; mixed-cohort summaries are rejected",
    )
    parser.add_argument("--fixture-manifest", type=Path, default=DEFAULT_FIXTURE_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return
    document = prioritize(args.summary, args.fixture_manifest)
    archive = write_archive(document, args.output)
    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "cases": document["cases"],
                "candidate_case_results": document["candidate_case_results"],
                "cohort": PRACTICE,
                "holdout_accessed": False,
                "timing_performed": False,
                "practice_rankings": document["practice_rankings"],
                "priority_operations": headline(document["groups"]["public_operation"]),
                "priority_lifetimes": headline(document["groups"]["pattern_lifetime"]),
                "priority_workloads": headline(document["groups"]["workload"]),
                "priority_input_kinds": headline(document["groups"]["input_kind"]),
                "archive": archive,
                "failed": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
