#!/usr/bin/env python3
"""Independently replay a complete, sealed Rust calibration measurement."""

from __future__ import annotations

import argparse
import collections
import dataclasses
import gzip
import hashlib
import importlib
import json
import math
import platform
import statistics
from pathlib import Path

from tools.rust_v7_calibration_pilot import (
    BASELINE,
    DEFAULT_CASES,
    DEFAULT_FIXTURE,
    DEFAULT_FIXTURE_MANIFEST,
    DEFAULT_PLAN,
    DEFAULT_TRIALS,
    EDGE_SCHEMA,
    MAX_OPERATIONS,
    PRACTICE,
    REPORT_SCHEMA,
    ROOT,
    ROW_SCHEMA,
    RUST,
    density,
    edge_document,
    file_sha256,
    is_runtime_regression,
    load_calibration_fixture,
    make_plan,
    source_kind,
    summarize_measurements,
    trial_order,
    valid_process_memory,
    verify_edge_source_hash,
    verify_regression_boundaries,
    verify_reported_artifacts,
)


SCHEMA = "rebar-rust-sealed-calibration-result-integrity-v7"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SLOT = "corrected-v4-production-baseline-fc30cf7b"
RAW_PATH = ROOT / "performance/v7/evidence/rust-v7-calibration-corrected-v4-baseline-raw.jsonl.gz"
SUMMARY_PATH = ROOT / "performance/v7/evidence/rust-v7-calibration-corrected-v4-baseline-summary.json"
OUTPUT_PATH = ROOT / "performance/v7/evidence/rust-v7-calibration-corrected-v4-baseline-integrity.json"
EDGE_PATH = ROOT / "candidates/evidence/rust-v7-edge-oracle-rust-corrected-v4.json.gz"
STDLIB_EDGE_PATH = ROOT / "candidates/evidence/rust-v7-edge-oracle-stdlib-baseline.json.gz"
EDGE_SOURCE = ROOT / "tools/rust_v7_edge_oracle.py"
EXPECTED_EDGE_SOURCE_SHA256 = "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
EXPECTED_ANSWER_SHA256 = "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
EXPECTED_MODULES = (BASELINE, RUST)
EXPECTED_CASES = 624
EXPECTED_CATEGORIES = 260
EXPECTED_APIS = 12
EXPECTED_TRIALS = 7
EXPECTED_WARMUPS = 4
EXPECTED_BOOTSTRAPS = 499
EXPECTED_ROWS = 8_736
EXPECTED_CORRECTNESS_CHECKS = 26_208
EXPECTED_REGRESSIONS = 175
EXPECTED_EDGE_CHECKS = 223_198


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


def display_path(path: Path) -> str:
    actual = path.resolve()
    root = ROOT.resolve()
    return str(actual.relative_to(root)) if actual.is_relative_to(root) else str(actual)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclasses.dataclass(frozen=True)
class Context:
    suite: object
    entries: list[tuple[int, dict, dict, tuple[str, ...]]]
    parent_manifest: dict
    plan: dict
    fixture_manifest: dict
    cases: dict[str, tuple[dict, dict, tuple[str, ...]]]


def sealed_context() -> Context:
    fixture_suite, fixture_rows, parent, _history, fixture_manifest = (
        load_calibration_fixture(DEFAULT_FIXTURE, DEFAULT_FIXTURE_MANIFEST)
    )
    require(fixture_suite.CASES_PER_COHORT == 10_312, "sealed fixture changed its practice denominator")
    require(len(fixture_rows) == 10_312, "sealed fixture omitted a practice workload")
    suite, entries, manifest, plan = make_plan(DEFAULT_CASES)
    require(len(entries) == EXPECTED_CASES, "frozen practice plan changed its denominator")
    require(manifest == parent, "sealed practice fixture changed its parent manifest")
    require(plan.get("cases") == EXPECTED_CASES, "frozen practice plan has the wrong case count")
    require(
        plan.get("all_bounded_workload_categories") == EXPECTED_CATEGORIES,
        "frozen practice plan dropped a workload category",
    )
    require(len(plan.get("public_operations", {})) == EXPECTED_APIS, "frozen practice plan dropped a public API")
    require(plan.get("cohort") == PRACTICE, "frozen practice plan is not calibration-only")
    require(plan.get("holdout_accessed") is False, "frozen practice plan exposes held-out data")
    with DEFAULT_PLAN.open("rb") as source:
        try:
            frozen_plan = json.load(source)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise RuntimeError("invalid committed frozen calibration plan") from error
    require(isinstance(frozen_plan, dict), "committed calibration plan is not an object")
    require(
        {key: value for key, value in frozen_plan.items() if key != "self_test"} == plan,
        "committed 624-case calibration selection changed",
    )
    cases = {
        case["id"]: (case, expected, reasons)
        for _position, case, expected, reasons in entries
    }
    require(len(cases) == EXPECTED_CASES, "duplicate frozen calibration workload")
    require(
        all(case.get("cohort") == PRACTICE for case, _expected, _reasons in cases.values()),
        "held-out workload entered the 624-case plan",
    )
    return Context(suite, entries, manifest, plan, fixture_manifest, cases)


def read_summary(path: Path, context: Context) -> dict:
    require(path.is_file(), "sealed calibration summary is missing")
    with path.open("rb") as source:
        try:
            summary = json.load(source)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise RuntimeError("invalid sealed calibration summary") from error
    require(isinstance(summary, dict), "sealed calibration summary is not an object")
    validate_summary_header(summary, context)
    return summary


def validate_summary_header(summary: dict, context: Context) -> None:
    require(summary.get("schema") == REPORT_SCHEMA, "incorrect sealed calibration summary schema")
    require(summary.get("cohort") == PRACTICE, "hidden cohort entered the calibration summary")
    require(summary.get("holdout_accessed") is False, "calibration summary admits holdout access")
    require(summary.get("failed") == 0, "calibration summary reports a correctness failure")
    require(summary.get("exclusive_slot") == SLOT, "calibration ran in an unapproved exclusive slot")
    require(summary.get("modules") == list(EXPECTED_MODULES), "paired Python and Rust engines changed")
    require(summary.get("cases") == EXPECTED_CASES, "calibration summary dropped cases")
    require(
        summary.get("all_bounded_workload_categories") == EXPECTED_CATEGORIES,
        "calibration summary dropped workload categories",
    )
    require(summary.get("public_operations") == context.plan["public_operations"], "calibration changed API weights")
    require(summary.get("lifetimes") == context.plan["lifetimes"], "calibration changed pattern lifetimes")
    require(summary.get("inputs") == context.plan["inputs"], "calibration changed input representations")
    require(summary.get("result_densities") == context.plan["result_densities"], "calibration changed result densities")
    require(summary.get("api_lifetimes") == context.plan["api_lifetimes"], "calibration changed API/lifetime groups")
    require(summary.get("expected_sha256") == context.parent_manifest["expected_sha256"], "calibration changed the frozen correctness answers")
    require(summary.get("selection_seed") == context.plan["selection_seed"], "calibration changed its workload seed")
    require(summary.get("order_seed") == context.suite.ORDER_SEED, "calibration changed its pairing seed")
    require(summary.get("bootstrap_seed") == context.suite.BOOTSTRAP_SEED, "calibration changed its confidence seed")
    require(summary.get("trials") == EXPECTED_TRIALS == DEFAULT_TRIALS, "calibration changed its paired-trial count")
    require(summary.get("warmups") == EXPECTED_WARMUPS == context.suite.WARMUPS, "calibration changed its warmup count")
    require(summary.get("bootstrap_samples") == EXPECTED_BOOTSTRAPS, "calibration changed its confidence protocol")
    require(summary.get("maximum_operations_per_trial") == MAX_OPERATIONS, "calibration changed its timing bound")
    require(summary.get("paired_raw_rows") == EXPECTED_ROWS, "calibration changed its raw-row denominator")
    require(
        summary.get("correctness_checks") == EXPECTED_CORRECTNESS_CHECKS,
        "calibration omitted a pre-timing, memory, or post-timing correctness gate",
    )
    require(
        summary.get("strict_regression_speedup_threshold") == 5.0 / 6.0,
        "calibration changed the strict more-than-20-percent regression boundary",
    )
    require(summary.get("raw_path") == str(RAW_PATH.resolve()), "calibration summary identifies a different raw file")


def validate_raw_row(
    row: object,
    context: Context,
    seen: set[tuple[str, int, str]],
) -> tuple[str, int, str]:
    require(isinstance(row, dict), "calibration raw record is not an object")
    require(row.get("schema") == ROW_SCHEMA, "calibration raw record changed schema")
    require(row.get("cohort") == PRACTICE, "held-out record entered raw calibration evidence")
    identifier = row.get("case")
    require(isinstance(identifier, str) and identifier in context.cases, "unknown frozen calibration case")
    case, expected, reasons = context.cases[identifier]
    module = row.get("module")
    require(module in EXPECTED_MODULES, "unknown paired calibration engine")
    trial = row.get("trial")
    require(
        isinstance(trial, int) and not isinstance(trial, bool) and 0 <= trial < EXPECTED_TRIALS,
        "invalid paired calibration trial",
    )
    key = (identifier, trial, module)
    require(key not in seen, "duplicate frozen workload, paired engine, or trial")
    require(row.get("category") == case["category"], "raw calibration changed a workload category")
    require(row.get("api") == case["api"], "raw calibration changed a public operation")
    require(row.get("lifecycle") == case["lifecycle"], "raw calibration changed a pattern lifetime")
    require(row.get("input") == source_kind(case), "raw calibration changed an input representation")
    require(row.get("result_density") == density(expected["result"]), "raw calibration changed result density")
    require(row.get("selection_reasons") == list(reasons), "raw calibration changed case selection")
    require(row.get("expected_sha256") == expected["result_sha256"], "raw calibration changed its correctness answer")
    require(row.get("frozen_operations") == case["ops"], "raw calibration changed frozen operations")
    operations = row.get("operations")
    require(
        isinstance(operations, int)
        and not isinstance(operations, bool)
        and operations == min(case["ops"], MAX_OPERATIONS),
        "raw calibration changed its per-trial operation bound",
    )
    order = trial_order(EXPECTED_MODULES, identifier, trial, context.suite.ORDER_SEED)
    require(row.get("order") == order.index(module), "raw calibration changed randomized paired order")
    elapsed = row.get("elapsed_ns")
    require(isinstance(elapsed, int) and not isinstance(elapsed, bool) and elapsed > 0, "invalid calibrated elapsed time")
    require(
        finite_positive(row.get("ns_per_op")) and row["ns_per_op"] == elapsed / operations,
        "invalid calibrated per-operation time",
    )
    peak = row.get("peak_traced_bytes")
    require(isinstance(peak, int) and not isinstance(peak, bool) and peak >= 0, "invalid calibrated Python memory observation")
    require(valid_process_memory(row), "invalid calibrated process memory observation")
    return key


def validate_observed_denominator(
    observed: dict[tuple[str, int, str], dict],
    context: Context,
) -> collections.Counter[str]:
    require(len(observed) == EXPECTED_ROWS, "calibration raw evidence dropped or added paired rows")
    counts: collections.Counter[str] = collections.Counter()
    for identifier, (_case, _expected, _reasons) in context.cases.items():
        for module in EXPECTED_MODULES:
            for trial in range(EXPECTED_TRIALS):
                key = (identifier, trial, module)
                require(key in observed, f"missing calibrated case, engine, or trial: {key}")
                counts[module] += 1
    require(
        counts == collections.Counter({BASELINE: 4_368, RUST: 4_368}),
        "baseline and Rust paired-trial weights are not equal",
    )
    return counts


def raw_evidence(
    path: Path,
    context: Context,
    summary: dict,
) -> tuple[dict[tuple[str, int, str], dict], collections.Counter[str], str]:
    require(path.is_file(), "sealed calibration raw evidence is missing")
    with path.open("rb") as source:
        header = source.read(10)
    require(len(header) == 10 and header[:2] == b"\x1f\x8b", "invalid practice evidence gzip header")
    require(header[3] & 0x08 == 0, "practice evidence contains a nondeterministic gzip filename")
    require(header[4:8] == b"\0\0\0\0", "practice evidence contains a nondeterministic gzip timestamp")
    observed: dict[tuple[str, int, str], dict] = {}
    seen: set[tuple[str, int, str]] = set()
    raw_digest = hashlib.sha256()
    with gzip.open(path, "rb") as source:
        for line_number, raw in enumerate(source, 1):
            require(line_number <= EXPECTED_ROWS, "calibration raw evidence contains extra rows")
            raw_digest.update(raw)
            try:
                row = json.loads(raw)
            except (UnicodeError, json.JSONDecodeError) as error:
                raise RuntimeError(f"invalid practice raw JSON at row {line_number}") from error
            key = validate_raw_row(row, context, seen)
            seen.add(key)
            observed[key] = row
    counts = validate_observed_denominator(observed, context)
    require(raw_digest.hexdigest() == summary.get("raw_sha256"), "raw practice evidence uncompressed hash changed")
    require(file_sha256(path) == summary.get("compressed_raw_sha256"), "raw practice evidence compressed hash changed")
    return observed, counts, raw_digest.hexdigest()


def validate_summary_results(
    summary: dict,
    expected_results: list[dict],
    expected_rankings: list[dict],
) -> None:
    reported = summary.get("case_results")
    require(isinstance(reported, list) and len(reported) == EXPECTED_CASES, "calibration summary omitted case results")
    require(reported == expected_results, "calibration summary speed, memory, case interval, or paired result changed")
    require(summary.get("rankings") == expected_rankings, "calibration summary changed the recomputed overall ranking or interval")
    regressions = [row for row in expected_results if is_runtime_regression(row["speedup"])]
    require(len(regressions) == EXPECTED_REGRESSIONS, "calibration changed its recorded strict slowdown denominator")
    require(summary.get("regressions") == regressions, "calibration concealed, added, or changed a slowdown")
    require(
        all(row["regression_gt_20pct"] is is_runtime_regression(row["speedup"]) for row in reported),
        "calibration changed a case's strict slowdown classification",
    )
    require(
        all(row["statistically_faster"] is (row["ci95_low"] > 1.0) for row in reported),
        "calibration changed a case's confidence classification",
    )
    require(
        all(
            finite_positive(row["speedup"])
            and finite_positive(row["ci95_low"])
            and finite_positive(row["ci95_high"])
            and row["ci95_low"] <= row["ci95_high"]
            for row in reported
        ),
        "calibration contains an invalid paired speed or confidence interval",
    )
    require(len(expected_rankings) == 1, "calibration changed its candidate denominator")
    ranking = expected_rankings[0]
    require(ranking["candidate"] == RUST and ranking["cases"] == EXPECTED_CASES, "calibration ranking lost the Rust candidate")
    require(ranking["regressions_gt_20pct"] == EXPECTED_REGRESSIONS, "calibration ranking concealed a slowdown")
    require(
        ranking["statistically_faster_cases"]
        == sum(row["statistically_faster"] for row in reported),
        "calibration ranking changed its significant-win count",
    )


def audit_edge_provenance(summary: dict) -> dict:
    references = summary.get("verified_edge_oracles")
    require(isinstance(references, list) and len(references) == 1, "calibration changed its candidate oracle denominator")
    reference = references[0]
    require(isinstance(reference, dict) and reference.get("module") == RUST, "calibration did not gate the production Rust candidate")
    require(Path(reference.get("path", "")).resolve() == EDGE_PATH.resolve(), "calibration used an unexpected Rust correctness report")
    source_hash = file_sha256(EDGE_SOURCE)
    require(source_hash == EXPECTED_EDGE_SOURCE_SHA256, "frozen independent edge-oracle source changed")
    verify_edge_source_hash(reference, source_hash, RUST)
    report, payload = edge_document(EDGE_PATH)
    require(report.get("schema") == EDGE_SCHEMA, "calibration used the wrong edge-oracle schema")
    require(report.get("module") == RUST, "edge report verifies a different candidate")
    require(report.get("correctness_checks") == EXPECTED_EDGE_CHECKS, "edge report dropped frozen compatibility checks")
    require(report.get("failed") == 0, "edge report contains unexplained compatibility failures")
    verify_edge_source_hash(report, source_hash, RUST)
    require(
        report.get("expected_sha256") == report.get("actual_sha256") == EXPECTED_ANSWER_SHA256,
        "edge report does not reproduce the complete Python answer digest",
    )
    require(report.get("performance") == "NOT MEASURED", "edge oracle contains performance data")
    require(report.get("holdout") == "NOT ACCESSED", "edge oracle accessed held-out data")
    categories = report.get("categories")
    require(isinstance(categories, dict) and len(categories) == 49, "edge oracle changed frozen correctness families")
    require(sum(categories.values()) == EXPECTED_EDGE_CHECKS, "edge oracle changed correctness-family denominators")
    require(hashlib.sha256(payload).hexdigest() == reference.get("report_sha256"), "edge correctness report changed after measurement")
    artifacts = verify_reported_artifacts(RUST, report.get("candidate_artifacts"))
    require(artifacts == reference.get("candidate_artifacts"), "edge proof and measured native artifacts disagree")

    baseline, baseline_payload = edge_document(STDLIB_EDGE_PATH)
    require(baseline.get("module") == BASELINE, "paired baseline oracle does not verify Python re")
    require(baseline.get("failed") == 0, "paired baseline oracle contains failures")
    require(baseline.get("correctness_checks") == EXPECTED_EDGE_CHECKS, "paired baseline lost edge cases")
    verify_edge_source_hash(baseline, source_hash, BASELINE)
    require(baseline.get("categories") == categories, "paired baseline changed frozen edge families")
    require(
        baseline.get("expected_sha256") == baseline.get("actual_sha256") == EXPECTED_ANSWER_SHA256,
        "paired baseline changed Python edge answers",
    )
    require(
        hashlib.sha256(baseline_payload).hexdigest() == reference.get("stdlib_baseline_sha256"),
        "paired Python baseline proof changed",
    )

    before = summary.get("candidate_binary_sha256_before")
    after = summary.get("candidate_binary_sha256_after")
    require(isinstance(before, dict) and before == after, "candidate or baseline changed during timing")
    roles = {
        "public-python": "module",
        "native-bridge": "native-bridge",
        "native-engine": "native-engine",
        "native-source": "native-source",
        "bridge-source": "bridge-source",
    }
    require(set(artifacts) == set(roles), "edge report did not prove all five native roles")
    for role, suffix in roles.items():
        key = f"{RUST}:{suffix}"
        require(before.get(key) == artifacts[role]["sha256"], f"measured Rust {role} differs from its compatibility proof")
    stdlib = importlib.import_module("re")
    require(
        before.get(f"{BASELINE}:module") == file_sha256(Path(stdlib.__file__)),
        "paired standard-library implementation changed",
    )
    return {
        "source_sha256": source_hash,
        "python_answer_sha256": EXPECTED_ANSWER_SHA256,
        "correctness_checks": EXPECTED_EDGE_CHECKS,
        "correctness_categories": len(categories),
        "report": display_path(EDGE_PATH),
        "report_sha256": reference["report_sha256"],
        "stdlib_report": display_path(STDLIB_EDGE_PATH),
        "stdlib_payload_sha256": reference["stdlib_baseline_sha256"],
        "artifacts": artifacts,
        "candidate_fingerprints_before": before,
        "candidate_fingerprints_after": after,
        "audit_imported_rust_candidate": False,
    }


def replay(
    raw_path: Path,
    summary_path: Path,
) -> tuple[Context, dict, dict[tuple[str, int, str], dict], list[dict], list[dict], dict, collections.Counter[str], str]:
    context = sealed_context()
    summary = read_summary(summary_path, context)
    observed, counts, raw_digest = raw_evidence(raw_path, context, summary)
    results, rankings = summarize_measurements(
        context.suite,
        context.entries,
        EXPECTED_MODULES,
        observed,
        EXPECTED_TRIALS,
        EXPECTED_BOOTSTRAPS,
    )
    validate_summary_results(summary, results, rankings)
    proof = audit_edge_provenance(summary)
    return context, summary, observed, results, rankings, proof, counts, raw_digest


def audit(raw_path: Path = RAW_PATH, summary_path: Path = SUMMARY_PATH) -> dict:
    context, summary, observed, results, rankings, proof, counts, raw_digest = replay(
        raw_path, summary_path
    )
    category_cases: collections.Counter[str] = collections.Counter()
    category_regressions: collections.Counter[str] = collections.Counter()
    for row in results:
        category_cases[row["category"]] += 1
        if row["regression_gt_20pct"]:
            category_regressions[row["category"]] += 1
    require(len(category_cases) == EXPECTED_CATEGORIES, "calibration audit dropped a workload category")
    categories = [
        {
            "category": name,
            "cases": count,
            "regressions_gt_20pct": category_regressions[name],
        }
        for name, count in sorted(category_cases.items())
    ]
    regressions = [
        {
            "case": row["case"],
            "category": row["category"],
            "api": row["api"],
            "lifecycle": row["lifecycle"],
            "speedup": row["speedup"],
            "ci95_low": row["ci95_low"],
            "ci95_high": row["ci95_high"],
            "runtime_slowdown_factor": 1.0 / row["speedup"],
            "statistically_faster": row["statistically_faster"],
        }
        for row in results
        if row["regression_gt_20pct"]
    ]
    require(len(regressions) == EXPECTED_REGRESSIONS, "calibration audit concealed a strict slowdown")
    boundaries = verify_regression_boundaries()
    ranking = rankings[0]
    return {
        "schema": SCHEMA,
        "python": platform.python_version(),
        "cohort": PRACTICE,
        "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent verification of an existing practice run; no timing or holdout",
        "exclusive_slot": summary["exclusive_slot"],
        "source_sha256": file_sha256(Path(__file__)),
        "sealed_fixture": {
            "path": display_path(DEFAULT_FIXTURE),
            "manifest_path": display_path(DEFAULT_FIXTURE_MANIFEST),
            "sha256": context.fixture_manifest["fixture_sha256"],
            "manifest_sha256": file_sha256(DEFAULT_FIXTURE_MANIFEST),
            "cases": context.fixture_manifest["cases"],
            "held_out_cases_generated": 0,
            "held_out_records_deserialized": 0,
        },
        "frozen_plan": {
            "path": display_path(DEFAULT_PLAN),
            "sha256": file_sha256(DEFAULT_PLAN),
            "cases": len(context.entries),
            "categories": len(categories),
            "public_operations": context.plan["public_operations"],
            "selection_seed": context.plan["selection_seed"],
        },
        "raw": {
            "path": display_path(raw_path),
            "sha256": file_sha256(raw_path),
            "uncompressed_sha256": raw_digest,
            "rows": len(observed),
            "candidate_rows": dict(sorted(counts.items())),
            "trials": EXPECTED_TRIALS,
            "warmups": EXPECTED_WARMUPS,
            "operations_per_trial_limit": MAX_OPERATIONS,
            "gzip_mtime": 0,
            "gzip_filename": "",
        },
        "summary": {
            "path": display_path(summary_path),
            "sha256": file_sha256(summary_path),
            "case_results": len(results),
            "case_results_sha256": canonical_sha256(results),
            "rankings_sha256": canonical_sha256(rankings),
            "confidence_intervals_recalculated": len(results) + len(rankings),
            "bootstrap_samples": EXPECTED_BOOTSTRAPS,
            "bootstrap_seed": context.suite.BOOTSTRAP_SEED,
        },
        "correctness_checks": summary["correctness_checks"],
        "correctness_checks_per_raw_row": 3,
        "native_provenance": proof,
        "regression_rule": {
            **boundaries,
            "slowdown_factor_exclusive": 1.2,
            "interpretation": "candidate elapsed time strictly more than 20 percent greater",
        },
        "ranking": ranking,
        "workload_categories": categories,
        "regressions_gt_20pct": regressions,
        "regression_count": len(regressions),
        "failed": 0,
    }


def expect_rejection(label: str, action: object) -> str:
    try:
        action()
    except RuntimeError:
        return label
    raise RuntimeError(f"calibration integrity self-test accepted corruption: {label}")


def self_test() -> dict:
    context, summary, observed, results, rankings, proof, _counts, _raw = replay(
        RAW_PATH, SUMMARY_PATH
    )
    first_key = next(iter(observed))
    first_row = observed[first_key]
    rejected: list[str] = []
    rejected.append(expect_rejection(
        "dropped-paired-raw-row",
        lambda: validate_observed_denominator(
            {key: value for key, value in observed.items() if key != first_key}, context
        ),
    ))
    rejected.append(expect_rejection(
        "duplicate-paired-raw-row",
        lambda: validate_raw_row(first_row, context, {first_key}),
    ))
    rejected.append(expect_rejection(
        "changed-correctness-digest",
        lambda: validate_raw_row({**first_row, "expected_sha256": "0" * 64}, context, set()),
    ))
    rejected.append(expect_rejection(
        "held-out-raw-cohort",
        lambda: validate_raw_row({**first_row, "cohort": "holdout"}, context, set()),
    ))
    rejected.append(expect_rejection(
        "changed-seeded-trial-order",
        lambda: validate_raw_row({**first_row, "order": 1 - first_row["order"]}, context, set()),
    ))
    rejected.append(expect_rejection(
        "changed-paired-elapsed-time",
        lambda: validate_raw_row({**first_row, "elapsed_ns": first_row["elapsed_ns"] + 1}, context, set()),
    ))
    rejected.append(expect_rejection(
        "dropped-case-result",
        lambda: validate_summary_results({**summary, "case_results": summary["case_results"][:-1]}, results, rankings),
    ))
    rejected.append(expect_rejection(
        "hidden-more-than-20-percent-regression",
        lambda: validate_summary_results({**summary, "regressions": summary["regressions"][1:]}, results, rankings),
    ))
    rejected.append(expect_rejection(
        "changed-case-confidence-interval",
        lambda: validate_summary_results(
            {
                **summary,
                "case_results": [
                    {**row, "ci95_low": row["ci95_low"] * 1.01} if index == 0 else row
                    for index, row in enumerate(summary["case_results"])
                ],
            },
            results,
            rankings,
        ),
    ))
    rejected.append(expect_rejection(
        "changed-strict-regression-boundary",
        lambda: validate_summary_header({**summary, "strict_regression_speedup_threshold": 0.8}, context),
    ))
    rejected.append(expect_rejection(
        "hidden-summary-cohort",
        lambda: validate_summary_header({**summary, "cohort": "holdout"}, context),
    ))
    rejected.append(expect_rejection(
        "stale-edge-oracle-source",
        lambda: verify_edge_source_hash(
            {"script_sha256": "0" * 64}, EXPECTED_EDGE_SOURCE_SHA256, "synthetic"
        ),
    ))

    original, _payload = edge_document(EDGE_PATH)
    artifacts = original["candidate_artifacts"]
    rejected.append(expect_rejection(
        "missing-native-artifact-role",
        lambda: verify_reported_artifacts(RUST, artifacts[:-1]),
    ))
    rejected.append(expect_rejection(
        "duplicate-native-artifact-role",
        lambda: verify_reported_artifacts(RUST, [*artifacts, dict(artifacts[0])]),
    ))
    by_role = {item["role"]: item for item in artifacts}
    swapped = [
        {
            **item,
            "path": by_role["native-bridge"]["path"],
            "sha256": by_role["native-bridge"]["sha256"],
        }
        if item["role"] == "native-engine"
        else item
        for item in artifacts
    ]
    rejected.append(expect_rejection(
        "swapped-native-engine-and-bridge",
        lambda: verify_reported_artifacts(RUST, swapped),
    ))
    changed_source = [
        {**item, "sha256": "0" * 64} if item["role"] == "native-source" else item
        for item in artifacts
    ]
    rejected.append(expect_rejection(
        "changed-native-source-digest",
        lambda: verify_reported_artifacts(RUST, changed_source),
    ))
    changed_before = dict(summary["candidate_binary_sha256_before"])
    changed_before[f"{RUST}:native-engine"] = "0" * 64
    rejected.append(expect_rejection(
        "measured-engine-differs-from-qualified-engine",
        lambda: audit_edge_provenance({**summary, "candidate_binary_sha256_before": changed_before}),
    ))
    return {
        "schema": SELF_TEST_SCHEMA,
        "cases": len(context.entries),
        "raw_rows": len(observed),
        "categories": EXPECTED_CATEGORIES,
        "public_operations": EXPECTED_APIS,
        "edge_checks": proof["correctness_checks"],
        "native_artifact_roles": len(proof["artifacts"]),
        "rejected_corruption_count": len(rejected),
        "rejected_corruptions": rejected,
        "holdout_accessed": False,
        "timing_performed": False,
        "failed": 0,
    }


def persist(path: Path, document: dict) -> str:
    payload = (
        json.dumps(document, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    if path.exists():
        require(path.is_file(), "calibration integrity output is not a file")
        require(path.read_bytes() == payload, "refusing to overwrite different calibration integrity evidence")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as destination:
            destination.write(payload)
    require(path.read_bytes() == payload, "calibration integrity output failed round-trip verification")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--raw", type=Path, default=RAW_PATH)
    parser.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return
    document = audit(args.raw.resolve(), args.summary.resolve())
    controls = self_test()
    document["self_test"] = controls
    integrity_sha256 = persist(args.output.resolve(), document)
    print(json.dumps({
        "schema": SCHEMA,
        "cases": document["frozen_plan"]["cases"],
        "categories": len(document["workload_categories"]),
        "public_operations": len(document["frozen_plan"]["public_operations"]),
        "paired_raw_rows": document["raw"]["rows"],
        "correctness_checks": document["correctness_checks"],
        "edge_checks": document["native_provenance"]["correctness_checks"],
        "native_artifact_roles": len(document["native_provenance"]["artifacts"]),
        "confidence_intervals_recalculated": document["summary"]["confidence_intervals_recalculated"],
        "strict_regressions": document["regression_count"],
        "rejected_corruptions": controls["rejected_corruption_count"],
        "holdout_accessed": False,
        "timing_performed": False,
        "output": display_path(args.output),
        "sha256": integrity_sha256,
        "failed": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
