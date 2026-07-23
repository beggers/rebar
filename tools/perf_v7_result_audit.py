#!/usr/bin/env python3
"""Independently verify a complete, frozen, five-engine version-7 run."""

from __future__ import annotations

import argparse
import array
import collections
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path

from tools.perf_v7 import (
    COHORTS,
    REGRESSION_SPEEDUP_THRESHOLD,
    ROOT,
    ROW_SCHEMA,
    SUMMARY_SCHEMA,
    frozen,
    is_runtime_regression,
    trial_order,
    valid_process_memory,
    verify_regression_boundaries,
)


SCHEMA = "rebar-performance-result-integrity-v7"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def finite_positive(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def matches_float(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-15)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def deterministic_archive(source: Path, destination: Path, expected_sha256: str) -> dict:
    """Write and independently read back a timestamp-free complete evidence archive."""
    source_digest = hashlib.sha256()
    if destination.exists():
        require(destination.is_file(), f"evidence archive is not a file: {destination}")
        with source.open("rb") as uncompressed:
            for chunk in iter(lambda: uncompressed.read(1024 * 1024), b""):
                source_digest.update(chunk)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as uncompressed, destination.open("xb") as compressed:
            with gzip.GzipFile(
                filename="", fileobj=compressed, mode="wb", compresslevel=9, mtime=0
            ) as archive:
                for chunk in iter(lambda: uncompressed.read(1024 * 1024), b""):
                    source_digest.update(chunk)
                    archive.write(chunk)
    require(source_digest.hexdigest() == expected_sha256, f"source changed while archiving {source}")
    restored_digest = hashlib.sha256()
    restored_bytes = 0
    with gzip.open(destination, "rb") as restored:
        for chunk in iter(lambda: restored.read(1024 * 1024), b""):
            restored_digest.update(chunk)
            restored_bytes += len(chunk)
    require(restored_digest.hexdigest() == expected_sha256, f"archive changed evidence {destination}")
    with destination.open("rb") as compressed:
        header = compressed.read(10)
    require(len(header) == 10, f"truncated gzip header {destination}")
    require(header[:2] == b"\x1f\x8b", f"invalid gzip header {destination}")
    require(header[3] & 0x08 == 0, f"non-deterministic gzip filename {destination}")
    require(header[4:8] == b"\0\0\0\0", f"non-deterministic gzip timestamp {destination}")
    return {
        "path": str(destination.resolve().relative_to(ROOT.resolve())),
        "sha256": file_sha256(destination),
        "bytes": destination.stat().st_size,
        "restored_sha256": restored_digest.hexdigest(),
        "restored_bytes": restored_bytes,
        "gzip_mtime": 0,
        "gzip_filename": "",
    }


def audit(raw_path: Path, summary_path: Path) -> dict:
    suite, cases, expected, manifest = frozen()
    modules = tuple(suite.MODULES)
    candidates = modules[1:]
    trials = suite.TRIALS
    module_indexes = {name: index for index, name in enumerate(modules)}
    candidate_indexes = {name: index for index, name in enumerate(candidates)}
    rows_per_case = len(modules) * trials
    required_rows = len(cases) * rows_per_case
    require(len(modules) == 5, "the five-engine denominator changed")
    require(len(candidates) == 4, "the four-candidate denominator changed")
    require(trials == 13, "the frozen trial count changed")
    require(suite.WARMUPS == 4, "the frozen warmup count changed")
    require(len(cases) == 20_624, "the frozen case denominator changed")
    require(required_rows == 1_340_560, "the frozen raw-row denominator changed")
    require(
        REGRESSION_SPEEDUP_THRESHOLD == 5.0 / 6.0,
        "the strict runtime regression threshold changed",
    )
    boundary_checks = verify_regression_boundaries()

    timings = array.array("d", [0.0]) * required_rows
    peaks = array.array("Q", [0]) * required_rows
    seen = bytearray(required_rows)
    raw_digest = hashlib.sha256()
    raw_counts: collections.Counter[tuple[str, str]] = collections.Counter()
    memory_missing: collections.Counter[str] = collections.Counter()
    process_samples: dict[tuple[str, str, str], array.array] = (
        collections.defaultdict(lambda: array.array("Q"))
    )
    row_count = 0
    with raw_path.open("rb") as source:
        for row_count, line in enumerate(source, 1):
            require(row_count <= required_rows, "extra raw timing row")
            raw_digest.update(line)
            try:
                row = json.loads(line)
            except (UnicodeError, json.JSONDecodeError) as error:
                raise RuntimeError(f"invalid raw row {row_count}") from error
            case_index = (row_count - 1) // rows_per_case
            case = cases[case_index]
            module_name = row.get("module")
            trial = row.get("trial")
            require(module_name in module_indexes, f"unknown engine at raw row {row_count}")
            require(
                isinstance(trial, int)
                and not isinstance(trial, bool)
                and 0 <= trial < trials,
                f"invalid trial at raw row {row_count}",
            )
            module_index = module_indexes[module_name]
            key = (case_index * len(modules) + module_index) * trials + trial
            require(not seen[key], f"duplicate engine or trial at raw row {row_count}")
            require(row.get("schema") == ROW_SCHEMA, f"wrong schema at raw row {row_count}")
            require(row.get("case") == case["id"], f"wrong case at raw row {row_count}")
            require(row.get("cohort") == case["cohort"], f"wrong cohort at raw row {row_count}")
            require(row.get("category") == case["category"], f"wrong family at raw row {row_count}")
            require(row.get("ops") == case["ops"], f"wrong operation count at raw row {row_count}")
            require(
                row.get("expected_sha256") == expected[case_index]["result_sha256"],
                f"wrong correctness digest at raw row {row_count}",
            )
            require(
                row.get("order") == trial_order(suite, case, trial).index(module_name),
                f"wrong seeded engine order at raw row {row_count}",
            )
            elapsed = row.get("elapsed_ns")
            per_operation = row.get("ns_per_op")
            peak = row.get("peak_traced_bytes")
            require(
                isinstance(elapsed, int) and not isinstance(elapsed, bool) and elapsed > 0,
                f"invalid elapsed time at raw row {row_count}",
            )
            require(
                finite_positive(per_operation) and per_operation == elapsed / case["ops"],
                f"invalid per-operation time at raw row {row_count}",
            )
            require(
                isinstance(peak, int) and not isinstance(peak, bool) and peak >= 0,
                f"invalid traced memory at raw row {row_count}",
            )
            require(valid_process_memory(row), f"invalid process memory at raw row {row_count}")
            for field in ("rss_before_kb", "rss_after_kb", "hwm_kb"):
                if row[field] is None:
                    memory_missing[field] += 1
                else:
                    process_samples[case["cohort"], module_name, field].append(row[field])
            timings[key] = per_operation
            peaks[key] = peak
            seen[key] = 1
            raw_counts[case["cohort"], module_name] += 1
    require(row_count == required_rows, "missing raw timing rows")
    require(all(seen), "missing candidate, baseline, or trial observations")
    for cohort in COHORTS:
        for name in modules:
            require(
                raw_counts[cohort, name] == suite.CASES_PER_COHORT * trials,
                f"wrong raw cohort denominator for {cohort} {name}",
            )

    summary_bytes = summary_path.read_bytes()
    try:
        summary = json.loads(summary_bytes)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("invalid performance summary") from error
    require(summary.get("schema") == SUMMARY_SCHEMA, "wrong performance summary schema")
    require(
        summary.get("expected_sha256") == manifest["expected_sha256"],
        "performance summary does not use the frozen fixture",
    )
    actual_raw_sha256 = raw_digest.hexdigest()
    require(summary.get("raw_sha256") == actual_raw_sha256, "performance raw digest changed")
    require(summary.get("rows") == required_rows, "performance summary dropped raw rows")
    case_results = summary.get("case_results")
    require(isinstance(case_results, list), "missing complete candidate case results")
    required_results = len(cases) * len(candidates)
    require(len(case_results) == required_results, "wrong candidate result denominator")
    case_indexes = {case["id"]: index for index, case in enumerate(cases)}
    result_seen = bytearray(required_results)
    result_counts: collections.Counter[tuple[str, str]] = collections.Counter()
    significant_counts: collections.Counter[tuple[str, str]] = collections.Counter()
    slowdown_counts: collections.Counter[tuple[str, str]] = collections.Counter()
    memory_ratios: dict[tuple[str, str], list[float]] = collections.defaultdict(list)
    expected_regressions: dict[tuple[str, str], dict] = {}
    for index, result in enumerate(case_results):
        require(isinstance(result, dict), f"invalid candidate result {index}")
        case_id = result.get("case")
        candidate_name = result.get("candidate")
        require(case_id in case_indexes, f"unknown candidate result case {index}")
        require(candidate_name in candidate_indexes, f"unknown candidate in result {index}")
        case_index = case_indexes[case_id]
        candidate_index = candidate_indexes[candidate_name]
        result_key = case_index * len(candidates) + candidate_index
        require(not result_seen[result_key], f"duplicate candidate result {case_id}")
        case = cases[case_index]
        require(result.get("cohort") == case["cohort"], f"wrong result cohort {case_id}")
        require(result.get("category") == case["category"], f"wrong result family {case_id}")
        require(result.get("weight") == case["weight"], f"wrong result weight {case_id}")
        for field in ("speedup", "ci95_low", "ci95_high"):
            require(finite_positive(result.get(field)), f"invalid {field} for {case_id}")
        require(
            result["ci95_low"] <= result["ci95_high"],
            f"inverted candidate confidence range {case_id}",
        )
        baseline_offset = case_index * len(modules) * trials
        source_offset = (
            case_index * len(modules) + module_indexes[candidate_name]
        ) * trials
        logs = tuple(
            math.log(timings[baseline_offset + trial] / timings[source_offset + trial])
            for trial in range(trials)
        )
        expected_speedup = math.exp(statistics.fmean(logs))
        require(
            matches_float(result["speedup"], expected_speedup),
            f"speedup does not reproduce raw paired trials: {case_id} {candidate_name}",
        )
        baseline_peak = statistics.median(peaks[baseline_offset : baseline_offset + trials])
        candidate_peak = statistics.median(peaks[source_offset : source_offset + trials])
        expected_memory_ratio = candidate_peak / max(1, baseline_peak)
        memory_ratio = result.get("peak_traced_ratio")
        require(
            isinstance(memory_ratio, (int, float))
            and not isinstance(memory_ratio, bool)
            and math.isfinite(memory_ratio)
            and memory_ratio >= 0
            and matches_float(memory_ratio, expected_memory_ratio),
            f"memory does not reproduce raw paired trials: {case_id} {candidate_name}",
        )
        statistically_faster = result["ci95_low"] > 1.0
        require(
            result.get("statistically_faster") is statistically_faster,
            f"wrong significant-win flag: {case_id} {candidate_name}",
        )
        slowdown = is_runtime_regression(expected_speedup)
        require(
            result.get("regression_gt_20pct") is slowdown,
            f"wrong strict 5/6 slowdown flag: {case_id} {candidate_name}",
        )
        key = case["cohort"], candidate_name
        result_counts[key] += 1
        significant_counts[key] += statistically_faster
        slowdown_counts[key] += slowdown
        memory_ratios[key].append(memory_ratio)
        if slowdown:
            expected_regressions[case_id, candidate_name] = result
        result_seen[result_key] = 1
    require(all(result_seen), "a complete candidate case result is missing")
    for cohort in COHORTS:
        for name in candidates:
            require(
                result_counts[cohort, name] == suite.CASES_PER_COHORT,
                f"wrong candidate case denominator for {cohort} {name}",
            )

    regressions = summary.get("regressions")
    require(isinstance(regressions, list), "missing complete slowdown results")
    require(len(regressions) == len(expected_regressions), "wrong strict slowdown denominator")
    seen_regressions: set[tuple[str, str]] = set()
    for regression in regressions:
        require(isinstance(regression, dict), "invalid recorded slowdown")
        key = regression.get("case"), regression.get("candidate")
        require(key in expected_regressions, f"unexplained or false slowdown {key}")
        require(key not in seen_regressions, f"duplicate slowdown {key}")
        require(regression == expected_regressions[key], f"changed recorded slowdown {key}")
        seen_regressions.add(key)
    require(
        seen_regressions == set(expected_regressions),
        "a greater-than-20-percent slowdown was omitted",
    )

    rankings = summary.get("rankings")
    require(isinstance(rankings, list), "missing complete candidate rankings")
    require(len(rankings) == len(candidates) * (len(COHORTS) + 1), "wrong ranking count")
    ranking_keys: set[tuple[str, str]] = set()
    for ranking in rankings:
        require(isinstance(ranking, dict), "invalid ranking")
        cohort, name = ranking.get("cohort"), ranking.get("candidate")
        require(cohort in (*COHORTS, "all"), "unknown ranking cohort")
        require(name in candidate_indexes, "unknown ranking candidate")
        key = cohort, name
        require(key not in ranking_keys, f"duplicate ranking {key}")
        ranking_keys.add(key)
        selected_cohorts = COHORTS if cohort == "all" else (cohort,)
        case_count = sum(result_counts[item, name] for item in selected_cohorts)
        require(ranking.get("cases") == case_count, f"wrong ranking denominator {key}")
        require(ranking.get("weight") == case_count, f"wrong ranking weights {key}")
        for field in ("geomean_speedup", "ci95_low", "ci95_high"):
            require(finite_positive(ranking.get(field)), f"invalid ranking {field} {key}")
        require(ranking["ci95_low"] <= ranking["ci95_high"], f"inverted ranking CI {key}")
        selected_results = (
            result
            for result in case_results
            if result["candidate"] == name and result["cohort"] in selected_cohorts
        )
        recomputed_speedup = math.exp(
            statistics.fmean(math.log(result["speedup"]) for result in selected_results)
        )
        require(
            matches_float(ranking["geomean_speedup"], recomputed_speedup),
            f"overall speedup does not reproduce every case {key}",
        )
        wins = sum(significant_counts[item, name] for item in selected_cohorts)
        losses = sum(slowdown_counts[item, name] for item in selected_cohorts)
        require(
            ranking.get("statistically_faster_cases") == wins,
            f"wrong significant-win count {key}",
        )
        require(
            ranking.get("regressions_gt_20pct") == losses,
            f"wrong strict slowdown count {key}",
        )
    require(
        ranking_keys == {(cohort, name) for cohort in (*COHORTS, "all") for name in candidates},
        "a complete cohort or candidate ranking is missing",
    )

    source_paths = (
        "GOAL.md",
        "performance/v7/manifest.json",
        "performance/v7/expected.jsonl",
        "performance/v7/suite.py",
        "tools/perf_v7.py",
        "tools/performance_v7_charts.py",
        "tools/perf_v7_result_audit.py",
        "candidates/rust/src/lib.rs",
        "candidates/rust/src/unicode_tables.rs",
        "candidates/rust/py_bridge.c",
        "candidates/rust_candidate.py",
        "candidates/_rust_engine.so",
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    )
    memory_medians = [
        {
            "candidate": name,
            "cohort": cohort,
            "cases": sum(
                result_counts[item, name]
                for item in (COHORTS if cohort == "all" else (cohort,))
            ),
            "median_peak_traced_ratio": statistics.median(
                value
                for item in (COHORTS if cohort == "all" else (cohort,))
                for value in memory_ratios[item, name]
            ),
        }
        for cohort in (*COHORTS, "all")
        for name in candidates
    ]
    process_memory_medians = []
    for cohort in COHORTS:
        baseline_after = statistics.median(process_samples[cohort, modules[0], "rss_after_kb"])
        for name in modules:
            medians = {}
            for field in ("rss_before_kb", "rss_after_kb", "hwm_kb"):
                observations = process_samples[cohort, name, field]
                require(
                    len(observations) == raw_counts[cohort, name],
                    f"missing process-memory observations for {cohort} {name} {field}",
                )
                medians[f"{field}_median"] = statistics.median(observations)
            medians["rss_after_ratio_to_python"] = (
                medians["rss_after_kb_median"] / max(1, baseline_after)
            )
            process_memory_medians.append(
                {"cohort": cohort, "engine": name, "rows": raw_counts[cohort, name], **medians}
            )
    return {
        "schema": SCHEMA,
        "python": manifest["python"],
        "expected_sha256": manifest["expected_sha256"],
        "raw_sha256": actual_raw_sha256,
        "summary_sha256": hashlib.sha256(summary_bytes).hexdigest(),
        "raw_bytes": raw_path.stat().st_size,
        "summary_bytes": len(summary_bytes),
        "cases": len(cases),
        "cases_per_cohort": suite.CASES_PER_COHORT,
        "engines": list(modules),
        "trials": trials,
        "warmups": suite.WARMUPS,
        "paired_raw_rows": required_rows,
        "candidate_case_results": required_results,
        "order_seed": suite.ORDER_SEED,
        "bootstrap_seed": suite.BOOTSTRAP_SEED,
        "bootstrap_samples": suite.BOOTSTRAPS,
        **boundary_checks,
        "raw_memory_observations": required_rows,
        "raw_process_memory_fields": required_rows * 3,
        "missing_process_memory_fields": dict(sorted(memory_missing.items())),
        "cohort_engine_rows": [
            {"cohort": cohort, "engine": name, "rows": raw_counts[cohort, name]}
            for cohort in COHORTS
            for name in modules
        ],
        "candidate_cohort_cases": [
            {"cohort": cohort, "candidate": name, "cases": result_counts[cohort, name]}
            for cohort in COHORTS
            for name in candidates
        ],
        "rankings": rankings,
        "peak_traced_memory_medians": memory_medians,
        "process_memory_medians": process_memory_medians,
        "strict_regressions": len(regressions),
        "source_sha256": {name: file_sha256(ROOT / name) for name in source_paths},
        "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--raw-archive", type=Path)
    parser.add_argument("--summary-archive", type=Path)
    args = parser.parse_args()
    result = audit(args.raw, args.summary)
    if args.raw_archive or args.summary_archive:
        require(
            args.raw_archive is not None and args.summary_archive is not None,
            "both complete deterministic evidence archives must be requested together",
        )
        result["archives"] = {
            "raw": deterministic_archive(args.raw, args.raw_archive, result["raw_sha256"]),
            "summary": deterministic_archive(
                args.summary, args.summary_archive, result["summary_sha256"]
            ),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
