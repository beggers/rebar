#!/usr/bin/env python3
"""Independently verify a sealed, practice-only Rust architecture comparison.

The original production-baseline auditor and its evidence remain immutable.
No benchmark is executed: every result is reconstructed from recorded,
correctness-gated practice observations and independently qualified binaries.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import gzip
import hashlib
import importlib
import json
import locale
import math
import platform
import sys
import unicodedata
from pathlib import Path

from tools import rust_v7_calibration_result_audit as original
from tools.rust_v7_calibration_pilot import (
    BASELINE,
    DEFAULT_BOOTSTRAPS,
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
    RUST,
    edge_document,
    file_sha256,
    is_runtime_regression,
    match_reported_fingerprints,
    module_fingerprints,
    required_edge_artifact_roles,
    summarize_measurements,
    verify_edge_source_hash,
    verify_regression_boundaries,
    verify_reported_artifacts,
)


SCHEMA = "rebar-rust-sealed-calibration-variant-integrity-v7"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
ORIGINAL_AUDITOR_SHA256 = "d89e49e2f2708e0765089d6798f04bf44eb275e3e196d0b24b20e7a09d3c4d55"
ORIGINAL_INTEGRITY_SHA256 = "699ba77aafdcd210ee53eeb0ae858e012a284ccd68a065a9d7efe4ce2dd9db8a"
ORIGINAL_SUMMARY_SHA256 = "78d8417e93e88637ab39e2632f4170e75dcfe3ec1cf0db74bc6f2c45a406b161"
ORIGINAL_RAW_SHA256 = "c0157b492495f6a72a600a5e4a3654bfb37af85086cb96ed1a21957d51385f76"
ORIGINAL_RAW_UNCOMPRESSED_SHA256 = "60b453d09efdf9ab10a991b456b77fbf43926f3a48eea38cbae0b117d4280ab8"
ORIGINAL_PLAN_SHA256 = "8e3da72df3c69ad68c181574ad62ed6bf77e2e9cd9987111aa7accbec6901744"
ORIGINAL_FIXTURE_SHA256 = "c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5"
ORIGINAL_FIXTURE_MANIFEST_SHA256 = "2ff780cd43ab4948a2af2f37e3d5dd3bbb69b9dd924385de1f2f3fc924dd276a"
ORIGINAL_CASE_RESULTS_SHA256 = "46955f2f97f6d661d6353c58c2d008f3dd53bc31b8e86e7f93c297e0e533b726"
ORIGINAL_RANKINGS_SHA256 = "eb8a21bf021c669011a2c009307fda8da506b9cb484a6d7828f0e29995750398"
ORIGINAL_CANDIDATE_EDGE_PAYLOAD_SHA256 = "b6f93fc99e650f07be1f11f4b9803a62ae69f98cfe117820f47b6a8394ed9d06"
STDLIB_EDGE_PAYLOAD_SHA256 = "38d5cdcce6a2f6d8baaa194d4866ebd582400a6b425387ae951ca65f2d0ea40a"
EXPECTED_CASES = 624
EXPECTED_CATEGORIES = 260
EXPECTED_APIS = 12
EXPECTED_TRIALS = 7
EXPECTED_WARMUPS = 4
EXPECTED_BOOTSTRAPS = 499
EXPECTED_ROWS = 8_736
EXPECTED_CORRECTNESS_CHECKS = 26_208
EXPECTED_BASELINE_REGRESSIONS = 175
EXPECTED_EDGE_CHECKS = 223_198
EXPECTED_EDGE_CATEGORIES = 49
EXPECTED_MODULES = (BASELINE, RUST)
CONTROL_OUTPUT = (
    ROOT / "performance/v7/evidence/rust-v7-calibration-baseline-variant-control-integrity.json"
)


require = original.require
canonical_sha256 = original.canonical_sha256
display_path = original.display_path


@dataclasses.dataclass(frozen=True)
class Configuration:
    raw: Path
    summary: Path
    edge: Path
    exclusive_slot: str
    output: Path
    baseline_integrity: Path


@dataclasses.dataclass(frozen=True)
class BaselineEvidence:
    integrity: dict
    summary: dict
    observations: dict
    results: list[dict]
    rankings: list[dict]
    raw_digest: str
    candidate_edge: dict
    candidate_edge_payload: bytes
    stdlib_edge: dict
    stdlib_edge_payload: bytes


@dataclasses.dataclass(frozen=True)
class VariantEvidence:
    summary: dict
    observations: dict
    results: list[dict]
    rankings: list[dict]
    raw_digest: str
    counts: collections.Counter[str]
    edge_report: dict
    edge_payload: bytes
    live_fingerprints: dict[str, str]
    native_provenance: dict


def load_json(path: Path, description: str) -> dict:
    require(path.is_file(), f"{description} is missing")
    try:
        with path.open("rb") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid {description}") from error
    require(isinstance(document, dict), f"{description} is not an object")
    return document


def validate_environment() -> None:
    require(platform.python_implementation() == "CPython", "requires pinned CPython")
    require(tuple(sys.version_info[:3]) == (3, 14, 6), "requires pinned CPython 3.14.6")
    require(unicodedata.unidata_version == "16.0.0", "requires pinned Unicode 16.0.0")
    locale.setlocale(locale.LC_CTYPE, "C")
    require(locale.setlocale(locale.LC_CTYPE) == "C", "requires the frozen C locale")


def validate_configuration(config: Configuration) -> bool:
    performance_root = (ROOT / "performance/v7/evidence").resolve()
    edge_root = (ROOT / "candidates/evidence").resolve()
    require(config.raw.parent == performance_root, "raw observations escaped sealed practice evidence")
    require(config.summary.parent == performance_root, "practice summary escaped sealed evidence")
    require(config.output.parent == performance_root, "integrity output escaped sealed practice evidence")
    require(config.edge.parent == edge_root, "candidate correctness proof escaped candidate evidence")
    require(config.baseline_integrity == original.OUTPUT_PATH.resolve(), "immutable original baseline reference changed")
    require(config.output not in {config.raw, config.summary, config.edge, config.baseline_integrity}, "integrity output overwrites frozen evidence")
    require(bool(config.exclusive_slot.strip()), "an exact authorized exclusive slot is required")

    original_raw = original.RAW_PATH.resolve()
    original_summary = original.SUMMARY_PATH.resolve()
    original_edge = original.EDGE_PATH.resolve()
    control = config.raw == original_raw
    if control:
        require(config.summary == original_summary, "baseline control was paired with a variant summary")
        require(config.edge == original_edge, "baseline control was paired with a variant edge proof")
        require(config.exclusive_slot == original.SLOT, "baseline control changed its authorized slot")
        require(config.output == CONTROL_OUTPUT.resolve(), "baseline control must use its independent reserved output")
    else:
        require(config.summary != original_summary, "variant reused the original baseline summary")
        require(config.edge != original_edge, "variant reused the original baseline correctness proof")
        require(config.exclusive_slot != original.SLOT, "variant reused the original baseline timing slot")
        raw_suffix = "-raw.jsonl.gz"
        summary_suffix = "-summary.json"
        require(config.raw.name.endswith(raw_suffix), "variant raw observation name is invalid")
        stem = config.raw.name[: -len(raw_suffix)]
        require(config.summary.name == stem + summary_suffix, "variant raw and summary experiment names disagree")
        require(config.output.name == stem + "-integrity.json", "variant integrity experiment name disagrees")
        require(
            config.edge.name.startswith("rust-v7-edge-oracle-rust-")
            and config.edge.name.endswith(".json.gz"),
            "variant candidate edge proof has an unexpected identity",
        )
    return control


def validate_gzip_rows(
    path: Path,
    context: original.Context,
    summary: dict,
) -> tuple[dict, collections.Counter[str], str]:
    require(path.is_file(), "sealed practice observations are missing")
    with path.open("rb") as stream:
        header = stream.read(10)
    require(len(header) == 10 and header[:2] == b"\x1f\x8b", "practice observations have no gzip header")
    require(header[3] & 0x08 == 0, "practice observations expose a nondeterministic filename")
    require(header[4:8] == b"\0\0\0\0", "practice observations expose a nondeterministic timestamp")
    observations: dict[tuple[str, int, str], dict] = {}
    seen: set[tuple[str, int, str]] = set()
    uncompressed = hashlib.sha256()
    try:
        with gzip.open(path, "rb") as stream:
            for number, encoded in enumerate(stream, 1):
                require(number <= EXPECTED_ROWS, "practice observations contain extra records")
                uncompressed.update(encoded)
                try:
                    row = json.loads(encoded)
                except (UnicodeError, json.JSONDecodeError) as error:
                    raise RuntimeError(f"invalid frozen practice record {number}") from error
                key = original.validate_raw_row(row, context, seen)
                seen.add(key)
                observations[key] = row
    except (OSError, EOFError) as error:
        raise RuntimeError("truncated or corrupt frozen practice observations") from error
    counts = original.validate_observed_denominator(observations, context)
    digest = uncompressed.hexdigest()
    require(digest == summary.get("raw_sha256"), "uncompressed practice observation digest changed")
    require(file_sha256(path) == summary.get("compressed_raw_sha256"), "compressed practice observation digest changed")
    return observations, counts, digest


def compact_regression(row: dict) -> dict:
    return {
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


def historical_roles(report: dict) -> dict[str, dict[str, str]]:
    recorded = report.get("candidate_artifacts")
    require(isinstance(recorded, list), "historical candidate role proof is missing")
    required = required_edge_artifact_roles(RUST)
    resolved: dict[str, dict[str, str]] = {}
    for artifact in recorded:
        require(isinstance(artifact, dict), "invalid historical candidate role")
        require(set(artifact) == {"role", "path", "sha256"}, "historical role fields changed")
        role = artifact.get("role")
        require(role in required and role not in resolved, "historical candidate role is missing or duplicated")
        location = artifact.get("path")
        digest = artifact.get("sha256")
        require(isinstance(location, str) and not Path(location).is_absolute(), "historical candidate role escaped production")
        require(
            isinstance(digest, str)
            and len(digest) == 64
            and all(char in "0123456789abcdef" for char in digest),
            "historical candidate role digest is invalid",
        )
        resolved[role] = {"path": location, "sha256": digest}
    require(set(resolved) == required, "historical candidate proof omitted a native role")
    return {role: resolved[role] for role in sorted(resolved)}


def validate_original_document(
    document: dict,
    summary: dict,
    observations: dict,
    results: list[dict],
    rankings: list[dict],
    raw_digest: str,
    candidate_edge: dict,
    candidate_payload: bytes,
    stdlib_edge: dict,
    stdlib_payload: bytes,
) -> None:
    require(document.get("schema") == original.SCHEMA, "immutable baseline integrity schema changed")
    require(document.get("cohort") == PRACTICE, "immutable baseline cohort changed")
    require(document.get("holdout_accessed") is False, "immutable baseline accessed hidden workloads")
    require(document.get("timing_performed") is False, "immutable baseline integrity executed timing")
    require(document.get("failed") == 0, "immutable baseline integrity contains failures")
    require(document.get("source_sha256") == ORIGINAL_AUDITOR_SHA256, "immutable baseline auditor reference changed")
    require(document.get("exclusive_slot") == original.SLOT, "immutable baseline slot changed")
    plan = document.get("frozen_plan")
    require(isinstance(plan, dict), "immutable baseline plan proof is missing")
    require(plan.get("sha256") == ORIGINAL_PLAN_SHA256, "immutable baseline plan digest changed")
    require(plan.get("cases") == EXPECTED_CASES, "immutable baseline dropped frozen cases")
    require(plan.get("categories") == EXPECTED_CATEGORIES, "immutable baseline dropped workload categories")
    require(isinstance(plan.get("public_operations"), dict) and len(plan["public_operations"]) == EXPECTED_APIS, "immutable baseline dropped public operations")

    raw = document.get("raw")
    require(isinstance(raw, dict), "immutable baseline raw proof is missing")
    require(raw.get("sha256") == ORIGINAL_RAW_SHA256, "immutable baseline raw archive digest changed")
    require(raw.get("uncompressed_sha256") == ORIGINAL_RAW_UNCOMPRESSED_SHA256 == raw_digest, "immutable baseline raw stream digest changed")
    require(raw.get("rows") == EXPECTED_ROWS == len(observations), "immutable baseline raw denominator changed")
    require(raw.get("trials") == EXPECTED_TRIALS and raw.get("warmups") == EXPECTED_WARMUPS, "immutable baseline trial protocol changed")
    require(raw.get("candidate_rows") == {BASELINE: 4_368, RUST: 4_368}, "immutable baseline candidate weights changed")

    recorded_summary = document.get("summary")
    require(isinstance(recorded_summary, dict), "immutable baseline summary proof is missing")
    require(recorded_summary.get("sha256") == ORIGINAL_SUMMARY_SHA256, "immutable baseline summary digest changed")
    require(recorded_summary.get("case_results") == EXPECTED_CASES, "immutable baseline case-result count changed")
    require(recorded_summary.get("case_results_sha256") == ORIGINAL_CASE_RESULTS_SHA256 == canonical_sha256(results), "immutable baseline case results changed")
    require(recorded_summary.get("rankings_sha256") == ORIGINAL_RANKINGS_SHA256 == canonical_sha256(rankings), "immutable baseline ranking changed")
    require(recorded_summary.get("confidence_intervals_recalculated") == EXPECTED_CASES + 1, "immutable baseline confidence intervals were omitted")
    require(recorded_summary.get("bootstrap_samples") == EXPECTED_BOOTSTRAPS, "immutable baseline bootstrap count changed")
    original.validate_summary_results(summary, results, rankings)
    require(document.get("ranking") == rankings[0], "immutable baseline reported ranking differs from recorded trials")
    losses = [compact_regression(row) for row in results if is_runtime_regression(row["speedup"])]
    require(len(losses) == EXPECTED_BASELINE_REGRESSIONS, "immutable baseline no longer contains all 175 losses")
    require(document.get("regression_count") == EXPECTED_BASELINE_REGRESSIONS, "immutable baseline loss denominator changed")
    require(document.get("regressions_gt_20pct") == losses, "immutable baseline concealed or changed a recorded slowdown")
    require(document.get("correctness_checks") == EXPECTED_CORRECTNESS_CHECKS, "immutable baseline omitted correctness gates")

    reference = document.get("native_provenance")
    require(isinstance(reference, dict), "immutable baseline native proof is missing")
    require(reference.get("source_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, "immutable baseline edge source changed")
    require(reference.get("python_answer_sha256") == original.EXPECTED_ANSWER_SHA256, "immutable baseline Python answers changed")
    require(reference.get("correctness_checks") == EXPECTED_EDGE_CHECKS, "immutable baseline edge check denominator changed")
    require(reference.get("correctness_categories") == EXPECTED_EDGE_CATEGORIES, "immutable baseline edge categories changed")
    require(hashlib.sha256(candidate_payload).hexdigest() == ORIGINAL_CANDIDATE_EDGE_PAYLOAD_SHA256, "immutable baseline native proof payload changed")
    require(reference.get("report_sha256") == ORIGINAL_CANDIDATE_EDGE_PAYLOAD_SHA256, "immutable baseline native report reference changed")
    require(hashlib.sha256(stdlib_payload).hexdigest() == STDLIB_EDGE_PAYLOAD_SHA256, "immutable baseline Python edge proof changed")
    require(reference.get("stdlib_payload_sha256") == STDLIB_EDGE_PAYLOAD_SHA256, "immutable baseline Python edge reference changed")
    require(candidate_edge.get("module") == RUST and stdlib_edge.get("module") == BASELINE, "immutable baseline edge candidate identity changed")
    require(candidate_edge.get("correctness_checks") == EXPECTED_EDGE_CHECKS, "immutable baseline candidate edge checks changed")
    require(stdlib_edge.get("correctness_checks") == EXPECTED_EDGE_CHECKS, "immutable baseline Python edge checks changed")
    require(candidate_edge.get("failed") == 0 and stdlib_edge.get("failed") == 0, "immutable baseline edge proof failed")
    require(candidate_edge.get("categories") == stdlib_edge.get("categories"), "immutable baseline edge categories changed")
    require(isinstance(candidate_edge.get("categories"), dict) and len(candidate_edge["categories"]) == EXPECTED_EDGE_CATEGORIES, "immutable baseline edge category denominator changed")
    require(sum(candidate_edge["categories"].values()) == EXPECTED_EDGE_CHECKS, "immutable baseline edge category weights changed")
    require(
        candidate_edge.get("expected_sha256")
        == candidate_edge.get("actual_sha256")
        == stdlib_edge.get("expected_sha256")
        == stdlib_edge.get("actual_sha256")
        == original.EXPECTED_ANSWER_SHA256,
        "immutable baseline edge oracle answers changed",
    )
    require(reference.get("artifacts") == historical_roles(candidate_edge), "immutable baseline five historical native roles changed")
    require(summary.get("candidate_binary_sha256_before") == summary.get("candidate_binary_sha256_after"), "immutable baseline binaries changed during original timing")
    require(reference.get("candidate_fingerprints_before") == summary.get("candidate_binary_sha256_before"), "immutable baseline pre-timing native evidence changed")
    require(reference.get("candidate_fingerprints_after") == summary.get("candidate_binary_sha256_after"), "immutable baseline post-timing native evidence changed")
    controls = document.get("self_test")
    require(isinstance(controls, dict) and controls.get("failed") == 0, "immutable baseline corruption controls failed")
    require(controls.get("rejected_corruption_count", 0) >= 17, "immutable baseline corruption controls were omitted")


def load_original_baseline(config: Configuration, context: original.Context) -> BaselineEvidence:
    require(file_sha256(Path(original.__file__).resolve()) == ORIGINAL_AUDITOR_SHA256, "immutable baseline auditor source was modified")
    require(file_sha256(config.baseline_integrity) == ORIGINAL_INTEGRITY_SHA256, "immutable baseline integrity was modified")
    require(file_sha256(original.SUMMARY_PATH) == ORIGINAL_SUMMARY_SHA256, "immutable baseline summary was modified")
    require(file_sha256(original.RAW_PATH) == ORIGINAL_RAW_SHA256, "immutable baseline raw archive was modified")
    require(file_sha256(DEFAULT_PLAN) == ORIGINAL_PLAN_SHA256, "immutable sealed 624-case plan was modified")
    require(file_sha256(DEFAULT_FIXTURE) == ORIGINAL_FIXTURE_SHA256, "immutable calibration-only fixture was modified")
    require(file_sha256(DEFAULT_FIXTURE_MANIFEST) == ORIGINAL_FIXTURE_MANIFEST_SHA256, "immutable calibration-only fixture manifest was modified")
    require(file_sha256(original.EDGE_SOURCE) == original.EXPECTED_EDGE_SOURCE_SHA256, "committed independent edge oracle source was modified")
    integrity = load_json(config.baseline_integrity, "immutable baseline integrity")
    summary = load_json(original.SUMMARY_PATH, "immutable baseline summary")
    original.validate_summary_header(summary, context)
    observations, _counts, digest = validate_gzip_rows(original.RAW_PATH, context, summary)
    results, rankings = summarize_measurements(
        context.suite,
        context.entries,
        EXPECTED_MODULES,
        observations,
        EXPECTED_TRIALS,
        EXPECTED_BOOTSTRAPS,
    )
    candidate_edge, candidate_payload = edge_document(original.EDGE_PATH)
    stdlib_edge, stdlib_payload = edge_document(original.STDLIB_EDGE_PATH)
    verify_edge_source_hash(candidate_edge, original.EXPECTED_EDGE_SOURCE_SHA256, RUST)
    verify_edge_source_hash(stdlib_edge, original.EXPECTED_EDGE_SOURCE_SHA256, BASELINE)
    validate_original_document(
        integrity,
        summary,
        observations,
        results,
        rankings,
        digest,
        candidate_edge,
        candidate_payload,
        stdlib_edge,
        stdlib_payload,
    )
    return BaselineEvidence(
        integrity,
        summary,
        observations,
        results,
        rankings,
        digest,
        candidate_edge,
        candidate_payload,
        stdlib_edge,
        stdlib_payload,
    )


def validate_variant_header(summary: dict, context: original.Context, config: Configuration) -> None:
    require(summary.get("schema") == REPORT_SCHEMA, "variant practice summary schema changed")
    require(summary.get("cohort") == PRACTICE, "variant selected a hidden or mixed cohort")
    require(summary.get("holdout_accessed") is False, "variant accessed hidden workloads")
    require(summary.get("failed") == 0, "variant reports failed correctness gates")
    require(summary.get("exclusive_slot") == config.exclusive_slot, "variant was measured in a different exclusive slot")
    require(summary.get("modules") == list(EXPECTED_MODULES), "variant changed the canonical paired production candidates")
    require(summary.get("cases") == EXPECTED_CASES == DEFAULT_CASES, "variant changed the frozen case denominator")
    require(summary.get("all_bounded_workload_categories") == EXPECTED_CATEGORIES, "variant changed the frozen workload categories")
    require(summary.get("public_operations") == context.plan["public_operations"], "variant changed public-operation weights")
    require(len(summary["public_operations"]) == EXPECTED_APIS, "variant dropped a public operation")
    require(summary.get("lifetimes") == context.plan["lifetimes"], "variant changed pattern-lifetime weights")
    require(summary.get("inputs") == context.plan["inputs"], "variant changed input-representation weights")
    require(summary.get("result_densities") == context.plan["result_densities"], "variant changed result-density weights")
    require(summary.get("api_lifetimes") == context.plan["api_lifetimes"], "variant changed operation/lifetime weights")
    require(summary.get("expected_sha256") == context.parent_manifest["expected_sha256"], "variant changed frozen correctness answers")
    require(summary.get("selection_seed") == context.plan["selection_seed"], "variant changed frozen case-selection seed")
    require(summary.get("order_seed") == context.suite.ORDER_SEED, "variant changed randomized pairing seed")
    require(summary.get("bootstrap_seed") == context.suite.BOOTSTRAP_SEED, "variant changed confidence seed")
    require(summary.get("trials") == EXPECTED_TRIALS == DEFAULT_TRIALS, "variant must retain exactly seven practice trials")
    require(summary.get("warmups") == EXPECTED_WARMUPS == context.suite.WARMUPS, "variant must retain exactly four practice warmups")
    require(summary.get("bootstrap_samples") == EXPECTED_BOOTSTRAPS == DEFAULT_BOOTSTRAPS, "variant must retain exactly 499 practice bootstrap draws")
    require(summary.get("maximum_operations_per_trial") == MAX_OPERATIONS, "variant changed the bounded operation cap")
    require(summary.get("paired_raw_rows") == EXPECTED_ROWS, "variant changed paired observation weights")
    require(summary.get("correctness_checks") == EXPECTED_CORRECTNESS_CHECKS, "variant omitted pre-, memory-, or post-timing correctness gates")
    require(summary.get("strict_regression_speedup_threshold") == 5.0 / 6.0, "variant changed the strict 20-percent slowdown boundary")
    require(summary.get("raw_path") == str(config.raw), "variant summary identifies a different raw archive")


def validate_variant_results(summary: dict, results: list[dict], rankings: list[dict]) -> list[dict]:
    recorded = summary.get("case_results")
    require(isinstance(recorded, list) and len(recorded) == EXPECTED_CASES, "variant omitted a frozen case result")
    require(recorded == results, "variant changed recorded speed, memory, correctness, or confidence intervals")
    require(summary.get("rankings") == rankings, "variant changed its independently reconstructed overall confidence interval")
    require(len(rankings) == 1, "variant changed its candidate ranking denominator")
    ranking = rankings[0]
    require(ranking.get("candidate") == RUST and ranking.get("cases") == EXPECTED_CASES, "variant ranking is not the canonical Rust candidate")
    losses = [row for row in results if is_runtime_regression(row["speedup"])]
    require(summary.get("regressions") == losses, "variant concealed, invented, or altered a strict slowdown")
    require(ranking.get("regressions_gt_20pct") == len(losses), "variant ranking concealed a strict slowdown")
    require(
        ranking.get("statistically_faster_cases")
        == sum(row["statistically_faster"] for row in recorded),
        "variant ranking changed its statistically faster case count",
    )
    for row in recorded:
        require(row.get("cohort") == PRACTICE, "variant case result accessed the hidden cohort")
        require(row.get("candidate") == RUST, "variant case result changed production candidate")
        require(row.get("regression_gt_20pct") is is_runtime_regression(row["speedup"]), "variant falsified strict slowdown classification")
        require(row.get("statistically_faster") is (row["ci95_low"] > 1.0), "variant falsified case confidence classification")
        require(
            original.finite_positive(row["speedup"])
            and original.finite_positive(row["ci95_low"])
            and original.finite_positive(row["ci95_high"])
            and row["ci95_low"] <= row["ci95_high"],
            "variant reports an invalid speed or confidence interval",
        )
    require(
        original.finite_positive(ranking["geomean_speedup"])
        and original.finite_positive(ranking["ci95_low"])
        and original.finite_positive(ranking["ci95_high"])
        and ranking["ci95_low"] <= ranking["ci95_high"],
        "variant reports an invalid overall confidence interval",
    )
    return losses


def validate_variant_edge(
    summary: dict,
    config: Configuration,
    report: dict,
    payload: bytes,
    stdlib_report: dict,
    stdlib_payload: bytes,
    fingerprints: dict[str, str],
) -> dict:
    references = summary.get("verified_edge_oracles")
    require(isinstance(references, list) and len(references) == 1, "variant changed its independently qualified candidate denominator")
    reference = references[0]
    require(isinstance(reference, dict) and reference.get("module") == RUST, "variant edge proof names a different candidate")
    location = reference.get("path")
    require(isinstance(location, str) and Path(location).resolve() == config.edge, "variant summary points at a swapped or stale edge proof")
    source_hash = file_sha256(original.EDGE_SOURCE)
    require(source_hash == original.EXPECTED_EDGE_SOURCE_SHA256, "frozen edge-oracle source has changed")
    verify_edge_source_hash(reference, source_hash, RUST)
    verify_edge_source_hash(report, source_hash, RUST)
    verify_edge_source_hash(stdlib_report, source_hash, BASELINE)
    require(report.get("schema") == EDGE_SCHEMA, "variant edge schema changed")
    require(report.get("module") == RUST, "variant edge proves a different candidate")
    require(stdlib_report.get("module") == BASELINE, "variant edge baseline is not pinned Python re")
    require(report.get("failed") == 0 and stdlib_report.get("failed") == 0, "variant edge correctness proof failed")
    require(report.get("correctness_checks") == EXPECTED_EDGE_CHECKS, "variant omitted independent edge correctness checks")
    require(stdlib_report.get("correctness_checks") == EXPECTED_EDGE_CHECKS, "variant baseline omitted independent edge correctness checks")
    require(reference.get("correctness_checks") == EXPECTED_EDGE_CHECKS, "variant summary changed edge correctness check count")
    categories = report.get("categories")
    require(isinstance(categories, dict) and len(categories) == EXPECTED_EDGE_CATEGORIES, "variant omitted an edge correctness category")
    require(categories == stdlib_report.get("categories"), "variant changed frozen edge correctness families")
    require(sum(categories.values()) == EXPECTED_EDGE_CHECKS, "variant changed edge correctness-family weights")
    for key in ("python", "unicode", "locale", "seed", "seeded_cases", "unicode_stride"):
        require(report.get(key) == stdlib_report.get(key), f"variant changed independent edge setting: {key}")
    require(report.get("python") == "3.14.6", "variant edge changed the pinned Python version")
    require(report.get("unicode") == "16.0.0", "variant edge changed the pinned Unicode version")
    require(report.get("locale") == "C", "variant edge changed the pinned character locale")
    require(
        report.get("expected_sha256")
        == report.get("actual_sha256")
        == stdlib_report.get("expected_sha256")
        == stdlib_report.get("actual_sha256")
        == original.EXPECTED_ANSWER_SHA256,
        "variant does not match every frozen CPython edge answer",
    )
    require(reference.get("actual_sha256") == original.EXPECTED_ANSWER_SHA256, "variant summary changed the exact edge answer")
    require(report.get("performance") == "NOT MEASURED", "variant edge proof includes timing")
    require(report.get("holdout") == "NOT ACCESSED", "variant edge proof accessed hidden workloads")
    require(stdlib_report.get("performance") == "NOT MEASURED", "Python edge proof includes timing")
    require(stdlib_report.get("holdout") == "NOT ACCESSED", "Python edge proof accessed hidden workloads")
    payload_hash = hashlib.sha256(payload).hexdigest()
    require(payload_hash == reference.get("report_sha256"), "variant edge report changed after timing")
    stdlib_hash = hashlib.sha256(stdlib_payload).hexdigest()
    require(stdlib_hash == STDLIB_EDGE_PAYLOAD_SHA256, "frozen standard-library edge proof changed")
    require(stdlib_hash == reference.get("stdlib_baseline_sha256"), "variant uses a different standard-library edge proof")
    artifacts = verify_reported_artifacts(RUST, report.get("candidate_artifacts"))
    require(set(artifacts) == required_edge_artifact_roles(RUST), "variant omitted one of five required native roles")
    require(artifacts == reference.get("candidate_artifacts"), "variant measured artifacts do not match its edge-qualified artifacts")
    before = summary.get("candidate_binary_sha256_before")
    after = summary.get("candidate_binary_sha256_after")
    require(isinstance(before, dict) and before == after, "variant binaries changed during the exclusive timing slot")
    require(before == fingerprints, "variant measured fingerprints are not the native binaries actually mapped in this auditor")
    match_reported_fingerprints([reference], fingerprints)
    return {
        "source_sha256": source_hash,
        "python_answer_sha256": original.EXPECTED_ANSWER_SHA256,
        "correctness_checks": EXPECTED_EDGE_CHECKS,
        "correctness_categories": EXPECTED_EDGE_CATEGORIES,
        "report": display_path(config.edge),
        "report_sha256": payload_hash,
        "stdlib_report": display_path(original.STDLIB_EDGE_PATH),
        "stdlib_payload_sha256": stdlib_hash,
        "artifacts": artifacts,
        "candidate_fingerprints_before": before,
        "candidate_fingerprints_after": after,
        "current_loaded_fingerprints": fingerprints,
        "native_mappings_verified": True,
        "native_mapping_source": "/proc/self/maps",
        "audit_imported_rust_candidate_for_fingerprint_only": True,
        "audit_executed_rust_candidate": False,
    }


def load_variant(
    config: Configuration,
    context: original.Context,
    baseline: BaselineEvidence,
) -> VariantEvidence:
    summary = load_json(config.summary, "variant frozen practice summary")
    validate_variant_header(summary, context, config)
    observations, counts, digest = validate_gzip_rows(config.raw, context, summary)
    results, rankings = summarize_measurements(
        context.suite,
        context.entries,
        EXPECTED_MODULES,
        observations,
        EXPECTED_TRIALS,
        EXPECTED_BOOTSTRAPS,
    )
    validate_variant_results(summary, results, rankings)
    report, payload = edge_document(config.edge)
    modules = {
        BASELINE: importlib.import_module(BASELINE),
        RUST: importlib.import_module(RUST),
    }
    fingerprints = module_fingerprints(modules)
    provenance = validate_variant_edge(
        summary,
        config,
        report,
        payload,
        baseline.stdlib_edge,
        baseline.stdlib_edge_payload,
        fingerprints,
    )
    return VariantEvidence(
        summary,
        observations,
        results,
        rankings,
        digest,
        counts,
        report,
        payload,
        fingerprints,
        provenance,
    )


def case_deltas(baseline: BaselineEvidence, variant: VariantEvidence) -> list[dict]:
    original_cases = {row["case"]: row for row in baseline.results}
    candidate_cases = {row["case"]: row for row in variant.results}
    require(len(original_cases) == EXPECTED_CASES, "immutable baseline contains duplicate case results")
    require(len(candidate_cases) == EXPECTED_CASES, "variant contains duplicate case results")
    require(set(original_cases) == set(candidate_cases), "variant changed the immutable comparison workload set")
    changes = []
    for previous in baseline.results:
        current = candidate_cases[previous["case"]]
        for key in ("case", "cohort", "category", "api", "lifecycle", "input", "result_density", "weight", "candidate"):
            require(current.get(key) == previous.get(key), f"variant changed frozen case metadata: {key}")
        changes.append({
            "case": previous["case"],
            "category": previous["category"],
            "api": previous["api"],
            "lifecycle": previous["lifecycle"],
            "baseline_speedup_vs_python": previous["speedup"],
            "baseline_ci95_low_vs_python": previous["ci95_low"],
            "baseline_ci95_high_vs_python": previous["ci95_high"],
            "variant_speedup_vs_python": current["speedup"],
            "variant_ci95_low_vs_python": current["ci95_low"],
            "variant_ci95_high_vs_python": current["ci95_high"],
            "descriptive_relative_speedup_vs_baseline": current["speedup"] / previous["speedup"],
            "baseline_candidate_median_ns": previous["candidate_ns"],
            "variant_candidate_median_ns": current["candidate_ns"],
            "baseline_peak_traced_ratio": previous["peak_traced_ratio"],
            "variant_peak_traced_ratio": current["peak_traced_ratio"],
            "baseline_regression_gt_20pct": previous["regression_gt_20pct"],
            "variant_regression_gt_20pct": current["regression_gt_20pct"],
        })
    require(len(changes) == EXPECTED_CASES, "variant omitted a case-by-case comparison")
    require(
        sum(row["baseline_regression_gt_20pct"] for row in changes)
        == EXPECTED_BASELINE_REGRESSIONS,
        "variant comparison concealed an immutable baseline slowdown",
    )
    return changes


def validate_deltas(changes: list[dict], baseline: BaselineEvidence, variant: VariantEvidence) -> None:
    require(changes == case_deltas(baseline, variant), "variant concealed or altered a case-by-case baseline comparison")


def expect_rejection(name: str, action: object) -> str:
    try:
        action()
    except (RuntimeError, OSError, ValueError, TypeError):
        return name
    raise RuntimeError(f"variant integrity accepted synthetic corruption: {name}")


def self_test(
    config: Configuration,
    context: original.Context,
    baseline: BaselineEvidence,
    variant: VariantEvidence,
    changes: list[dict],
) -> dict:
    first_key = next(iter(variant.observations))
    first = variant.observations[first_key]
    full_losses = [row for row in variant.results if is_runtime_regression(row["speedup"])]
    controls: list[str] = []

    def reject(name: str, action: object) -> None:
        controls.append(expect_rejection(name, action))

    reject("dropped-paired-raw-row", lambda: original.validate_observed_denominator(
        {key: value for key, value in variant.observations.items() if key != first_key}, context
    ))
    reject("duplicate-paired-raw-row", lambda: original.validate_raw_row(first, context, {first_key}))
    reject("held-out-raw-cohort", lambda: original.validate_raw_row({**first, "cohort": "holdout"}, context, set()))
    reject("changed-correctness-digest", lambda: original.validate_raw_row({**first, "expected_sha256": "0" * 64}, context, set()))
    reject("unknown-paired-candidate", lambda: original.validate_raw_row({**first, "module": "candidates.fake_candidate"}, context, set()))
    reject("changed-randomized-trial-order", lambda: original.validate_raw_row({**first, "order": 1 - first["order"]}, context, set()))
    reject("changed-recorded-elapsed-time", lambda: original.validate_raw_row({**first, "elapsed_ns": first["elapsed_ns"] + 1}, context, set()))
    reject("changed-frozen-operation-cap", lambda: original.validate_raw_row({**first, "operations": first["operations"] + 1}, context, set()))
    reject("hidden-summary-cohort", lambda: validate_variant_header({**variant.summary, "cohort": "holdout"}, context, config))
    reject("claimed-held-out-access", lambda: validate_variant_header({**variant.summary, "holdout_accessed": True}, context, config))
    reject("wrong-authorized-exclusive-slot", lambda: validate_variant_header({**variant.summary, "exclusive_slot": "unauthorized-synthetic-slot"}, context, config))
    reject("wrong-practice-case-denominator", lambda: validate_variant_header({**variant.summary, "cases": EXPECTED_CASES - 1}, context, config))
    reject("wrong-public-operation-denominator", lambda: validate_variant_header({**variant.summary, "public_operations": {}}, context, config))
    reject("wrong-practice-trial-denominator", lambda: validate_variant_header({**variant.summary, "trials": 13}, context, config))
    reject("wrong-practice-warmup-denominator", lambda: validate_variant_header({**variant.summary, "warmups": EXPECTED_WARMUPS + 1}, context, config))
    reject("wrong-practice-bootstrap-denominator", lambda: validate_variant_header({**variant.summary, "bootstrap_samples": 2_000}, context, config))
    reject("wrong-strict-slowdown-boundary", lambda: validate_variant_header({**variant.summary, "strict_regression_speedup_threshold": 0.8}, context, config))
    reject("changed-recorded-raw-path", lambda: validate_variant_header({**variant.summary, "raw_path": "/tmp/swapped-frozen-raw.jsonl.gz"}, context, config))
    reject("dropped-candidate-case-result", lambda: validate_variant_results(
        {**variant.summary, "case_results": variant.summary["case_results"][:-1]},
        variant.results,
        variant.rankings,
    ))
    altered_cases = [dict(row) for row in variant.summary["case_results"]]
    altered_cases[0]["ci95_low"] *= 1.01
    reject("changed-case-confidence-interval", lambda: validate_variant_results(
        {**variant.summary, "case_results": altered_cases}, variant.results, variant.rankings
    ))
    altered_rankings = [dict(row) for row in variant.summary["rankings"]]
    altered_rankings[0]["ci95_high"] *= 1.01
    reject("changed-overall-confidence-interval", lambda: validate_variant_results(
        {**variant.summary, "rankings": altered_rankings}, variant.results, variant.rankings
    ))
    if full_losses:
        reject("hidden-variant-more-than-20-percent-regression", lambda: validate_variant_results(
            {**variant.summary, "regressions": full_losses[1:]}, variant.results, variant.rankings
        ))
    else:
        reject("invented-variant-more-than-20-percent-regression", lambda: validate_variant_results(
            {**variant.summary, "regressions": [variant.results[0]]}, variant.results, variant.rankings
        ))

    def check_original(document: dict) -> None:
        validate_original_document(
            document,
            baseline.summary,
            baseline.observations,
            baseline.results,
            baseline.rankings,
            baseline.raw_digest,
            baseline.candidate_edge,
            baseline.candidate_edge_payload,
            baseline.stdlib_edge,
            baseline.stdlib_edge_payload,
        )

    reject("changed-immutable-baseline-source-digest", lambda: check_original({
        **baseline.integrity, "source_sha256": "0" * 64
    }))
    reject("changed-immutable-baseline-raw-digest", lambda: check_original({
        **baseline.integrity, "raw": {**baseline.integrity["raw"], "sha256": "0" * 64}
    }))
    reject("changed-immutable-baseline-summary-digest", lambda: check_original({
        **baseline.integrity,
        "summary": {**baseline.integrity["summary"], "sha256": "0" * 64},
    }))
    reject("hidden-immutable-baseline-regression", lambda: check_original({
        **baseline.integrity,
        "regressions_gt_20pct": baseline.integrity["regressions_gt_20pct"][1:],
    }))
    reject("changed-immutable-baseline-regression-denominator", lambda: check_original({
        **baseline.integrity, "regression_count": EXPECTED_BASELINE_REGRESSIONS - 1
    }))
    reject("dropped-case-by-case-baseline-comparison", lambda: validate_deltas(
        changes[:-1], baseline, variant
    ))
    modified_changes = [dict(row) for row in changes]
    modified_changes[0]["variant_speedup_vs_python"] *= 1.01
    reject("changed-case-by-case-baseline-comparison", lambda: validate_deltas(
        modified_changes, baseline, variant
    ))

    candidate_artifacts = variant.edge_report["candidate_artifacts"]
    reject("missing-current-native-artifact-role", lambda: verify_reported_artifacts(
        RUST, candidate_artifacts[:-1]
    ))
    reject("duplicated-current-native-artifact-role", lambda: verify_reported_artifacts(
        RUST, [*candidate_artifacts, dict(candidate_artifacts[0])]
    ))
    by_role = {artifact["role"]: artifact for artifact in candidate_artifacts}
    swapped = [
        {
            **artifact,
            "path": by_role["native-bridge"]["path"],
            "sha256": by_role["native-bridge"]["sha256"],
        }
        if artifact["role"] == "native-engine"
        else artifact
        for artifact in candidate_artifacts
    ]
    reject("swapped-current-native-engine-and-bridge", lambda: verify_reported_artifacts(RUST, swapped))
    stale_source = [
        {**artifact, "sha256": "0" * 64}
        if artifact["role"] == "native-source"
        else artifact
        for artifact in candidate_artifacts
    ]
    reject("stale-current-native-source", lambda: verify_reported_artifacts(RUST, stale_source))
    reject("stale-frozen-edge-source", lambda: verify_edge_source_hash(
        {"script_sha256": "0" * 64}, original.EXPECTED_EDGE_SOURCE_SHA256, RUST
    ))

    def edge_check(summary: dict, live: dict[str, str]) -> None:
        validate_variant_edge(
            summary,
            config,
            variant.edge_report,
            variant.edge_payload,
            baseline.stdlib_edge,
            baseline.stdlib_edge_payload,
            live,
        )

    first_reference = variant.summary["verified_edge_oracles"][0]
    reject("swapped-candidate-edge-report", lambda: edge_check({
        **variant.summary,
        "verified_edge_oracles": [{**first_reference, "path": "/tmp/swapped-edge-proof.json.gz"}],
    }, variant.live_fingerprints))
    reject("stale-candidate-edge-payload", lambda: edge_check({
        **variant.summary,
        "verified_edge_oracles": [{**first_reference, "report_sha256": "0" * 64}],
    }, variant.live_fingerprints))
    stale_live = dict(variant.live_fingerprints)
    stale_live[f"{RUST}:native-engine"] = "0" * 64
    reject("mapped-native-engine-differs-from-qualified-engine", lambda: edge_check(
        variant.summary, stale_live
    ))
    stale_before = dict(variant.summary["candidate_binary_sha256_before"])
    stale_before[f"{RUST}:native-engine"] = "0" * 64
    reject("native-engine-changed-during-exclusive-slot", lambda: edge_check({
        **variant.summary, "candidate_binary_sha256_before": stale_before
    }, variant.live_fingerprints))
    reject("baseline-and-variant-summary-cross-contamination", lambda: validate_configuration(
        dataclasses.replace(config, summary=ROOT / "performance/v7/evidence/swapped-summary.json")
    ))

    require(len(controls) >= 20, "variant integrity omitted required synthetic corruption controls")
    return {
        "schema": SELF_TEST_SCHEMA,
        "cases": EXPECTED_CASES,
        "categories": EXPECTED_CATEGORIES,
        "public_operations": EXPECTED_APIS,
        "raw_rows": EXPECTED_ROWS,
        "trials": EXPECTED_TRIALS,
        "warmups": EXPECTED_WARMUPS,
        "bootstrap_samples": EXPECTED_BOOTSTRAPS,
        "correctness_checks": EXPECTED_CORRECTNESS_CHECKS,
        "edge_checks": EXPECTED_EDGE_CHECKS,
        "edge_categories": EXPECTED_EDGE_CATEGORIES,
        "native_artifact_roles": len(variant.native_provenance["artifacts"]),
        "native_mappings_verified": True,
        "baseline_regressions": EXPECTED_BASELINE_REGRESSIONS,
        "variant_regressions": len(full_losses),
        "rejected_corruption_count": len(controls),
        "rejected_corruptions": controls,
        "holdout_accessed": False,
        "timing_performed": False,
        "failed": 0,
    }


def build_integrity(
    config: Configuration,
    control: bool,
    context: original.Context,
    baseline: BaselineEvidence,
    variant: VariantEvidence,
    changes: list[dict],
    controls: dict,
) -> dict:
    losses = [compact_regression(row) for row in variant.results if is_runtime_regression(row["speedup"])]
    category_counts: collections.Counter[str] = collections.Counter()
    category_losses: collections.Counter[str] = collections.Counter()
    for row in variant.results:
        category_counts[row["category"]] += 1
        if row["regression_gt_20pct"]:
            category_losses[row["category"]] += 1
    require(len(category_counts) == EXPECTED_CATEGORIES, "variant integrity omitted a frozen workload category")
    categories = [
        {"category": category, "cases": count, "regressions_gt_20pct": category_losses[category]}
        for category, count in sorted(category_counts.items())
    ]
    transitions = {
        "original_regressions": EXPECTED_BASELINE_REGRESSIONS,
        "variant_regressions": len(losses),
        "resolved_regressions": sum(
            row["baseline_regression_gt_20pct"] and not row["variant_regression_gt_20pct"]
            for row in changes
        ),
        "retained_regressions": sum(
            row["baseline_regression_gt_20pct"] and row["variant_regression_gt_20pct"]
            for row in changes
        ),
        "introduced_regressions": sum(
            not row["baseline_regression_gt_20pct"] and row["variant_regression_gt_20pct"]
            for row in changes
        ),
        "descriptively_faster_cases": sum(
            row["variant_speedup_vs_python"] > row["baseline_speedup_vs_python"]
            for row in changes
        ),
        "descriptively_slower_cases": sum(
            row["variant_speedup_vs_python"] < row["baseline_speedup_vs_python"]
            for row in changes
        ),
        "unchanged_cases": sum(
            row["variant_speedup_vs_python"] == row["baseline_speedup_vs_python"]
            for row in changes
        ),
        "architecture_runs_independently_paired_to_python": True,
        "baseline_and_variant_directly_paired_to_each_other": False,
        "direct_architecture_comparison_confidence_interval": "NOT MEASURED",
    }
    require(
        transitions["resolved_regressions"] + transitions["retained_regressions"]
        == EXPECTED_BASELINE_REGRESSIONS,
        "variant transition proof concealed an original slowdown",
    )
    require(
        transitions["retained_regressions"] + transitions["introduced_regressions"]
        == len(losses),
        "variant transition proof concealed a new slowdown",
    )
    require(
        transitions["descriptively_faster_cases"]
        + transitions["descriptively_slower_cases"]
        + transitions["unchanged_cases"]
        == EXPECTED_CASES,
        "variant transition proof changed the frozen case denominator",
    )
    if control:
        require(all(row["descriptive_relative_speedup_vs_baseline"] == 1.0 for row in changes), "baseline control is not byte-for-byte identical to itself")
        require(transitions["resolved_regressions"] == 0 and transitions["introduced_regressions"] == 0, "baseline control changed recorded slowdowns")
    return {
        "schema": SCHEMA,
        "python": platform.python_version(),
        "cohort": PRACTICE,
        "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of recorded sealed-practice observations; no timing and no holdout",
        "baseline_control": control,
        "exclusive_slot": config.exclusive_slot,
        "source_sha256": file_sha256(Path(__file__).resolve()),
        "sealed_fixture": {
            "path": display_path(DEFAULT_FIXTURE),
            "manifest_path": display_path(DEFAULT_FIXTURE_MANIFEST),
            "sha256": ORIGINAL_FIXTURE_SHA256,
            "manifest_sha256": ORIGINAL_FIXTURE_MANIFEST_SHA256,
            "cases": context.fixture_manifest["cases"],
            "held_out_cases_generated": 0,
            "held_out_records_deserialized": 0,
        },
        "frozen_plan": {
            "path": display_path(DEFAULT_PLAN),
            "sha256": ORIGINAL_PLAN_SHA256,
            "cases": EXPECTED_CASES,
            "categories": EXPECTED_CATEGORIES,
            "public_operations": context.plan["public_operations"],
            "selection_seed": context.plan["selection_seed"],
        },
        "immutable_baseline": {
            "auditor": display_path(Path(original.__file__).resolve()),
            "auditor_sha256": ORIGINAL_AUDITOR_SHA256,
            "integrity": display_path(config.baseline_integrity),
            "integrity_sha256": ORIGINAL_INTEGRITY_SHA256,
            "summary": display_path(original.SUMMARY_PATH),
            "summary_sha256": ORIGINAL_SUMMARY_SHA256,
            "raw": display_path(original.RAW_PATH),
            "raw_sha256": ORIGINAL_RAW_SHA256,
            "uncompressed_raw_sha256": ORIGINAL_RAW_UNCOMPRESSED_SHA256,
            "case_results_sha256": ORIGINAL_CASE_RESULTS_SHA256,
            "rankings_sha256": ORIGINAL_RANKINGS_SHA256,
            "cases": EXPECTED_CASES,
            "regressions_gt_20pct": EXPECTED_BASELINE_REGRESSIONS,
            "regression_records_sha256": canonical_sha256(baseline.integrity["regressions_gt_20pct"]),
            "ranking": baseline.rankings[0],
            "historical_native_artifacts": baseline.integrity["native_provenance"]["artifacts"],
            "historical_native_artifacts_are_not_claimed_current": not control,
        },
        "raw": {
            "path": display_path(config.raw),
            "sha256": file_sha256(config.raw),
            "uncompressed_sha256": variant.raw_digest,
            "rows": len(variant.observations),
            "candidate_rows": dict(sorted(variant.counts.items())),
            "trials": EXPECTED_TRIALS,
            "warmups": EXPECTED_WARMUPS,
            "operations_per_trial_limit": MAX_OPERATIONS,
            "gzip_mtime": 0,
            "gzip_filename": "",
        },
        "summary": {
            "path": display_path(config.summary),
            "sha256": file_sha256(config.summary),
            "case_results": len(variant.results),
            "case_results_sha256": canonical_sha256(variant.results),
            "rankings_sha256": canonical_sha256(variant.rankings),
            "confidence_intervals_recalculated": len(variant.results) + len(variant.rankings),
            "bootstrap_samples": EXPECTED_BOOTSTRAPS,
            "bootstrap_seed": context.suite.BOOTSTRAP_SEED,
        },
        "correctness_checks": EXPECTED_CORRECTNESS_CHECKS,
        "correctness_checks_per_raw_row": 3,
        "native_provenance": variant.native_provenance,
        "regression_rule": {
            **verify_regression_boundaries(),
            "slowdown_factor_exclusive": 1.2,
            "interpretation": "candidate elapsed time strictly more than 20 percent greater",
        },
        "ranking": variant.rankings[0],
        "workload_categories": categories,
        "regressions_gt_20pct": losses,
        "regression_count": len(losses),
        "baseline_delta_interpretation": (
            "Each architecture was independently paired against pinned Python on the same frozen "
            "practice cases. Baseline-to-variant ratios are descriptive, not directly paired "
            "measurements and not architecture-to-architecture confidence intervals."
        ),
        "baseline_delta": transitions,
        "case_deltas": changes,
        "self_test": controls,
        "failed": 0,
    }


def resolve_configuration(args: argparse.Namespace) -> Configuration:
    return Configuration(
        raw=args.raw.resolve(),
        summary=args.summary.resolve(),
        edge=args.edge.resolve(),
        exclusive_slot=args.exclusive_slot,
        output=args.output.resolve(),
        baseline_integrity=args.baseline_integrity.resolve(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=original.RAW_PATH)
    parser.add_argument("--summary", type=Path, default=original.SUMMARY_PATH)
    parser.add_argument("--edge", type=Path, default=original.EDGE_PATH)
    parser.add_argument("--exclusive-slot", default=original.SLOT)
    parser.add_argument("--output", type=Path, default=CONTROL_OUTPUT)
    parser.add_argument("--baseline-integrity", type=Path, default=original.OUTPUT_PATH)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    config = resolve_configuration(args)
    validate_environment()
    control = validate_configuration(config)
    context = original.sealed_context()
    baseline = load_original_baseline(config, context)
    variant = load_variant(config, context, baseline)
    changes = case_deltas(baseline, variant)
    validate_deltas(changes, baseline, variant)
    controls = self_test(config, context, baseline, variant, changes)
    if args.self_test:
        print(json.dumps({**controls, "baseline_control": control}, sort_keys=True))
        return
    document = build_integrity(config, control, context, baseline, variant, changes, controls)
    evidence_hash = original.persist(config.output, document)
    print(json.dumps({
        "schema": SCHEMA,
        "baseline_control": control,
        "cohort": PRACTICE,
        "holdout_accessed": False,
        "timing_performed": False,
        "cases": EXPECTED_CASES,
        "categories": EXPECTED_CATEGORIES,
        "public_operations": EXPECTED_APIS,
        "trials": EXPECTED_TRIALS,
        "warmups": EXPECTED_WARMUPS,
        "bootstrap_samples": EXPECTED_BOOTSTRAPS,
        "paired_raw_rows": EXPECTED_ROWS,
        "correctness_checks": EXPECTED_CORRECTNESS_CHECKS,
        "edge_checks": EXPECTED_EDGE_CHECKS,
        "edge_categories": EXPECTED_EDGE_CATEGORIES,
        "native_artifact_roles": len(variant.native_provenance["artifacts"]),
        "native_mappings_verified": True,
        "confidence_intervals_recalculated": EXPECTED_CASES + 1,
        "baseline_regressions": EXPECTED_BASELINE_REGRESSIONS,
        "variant_regressions": document["regression_count"],
        "case_deltas": len(changes),
        "rejected_corruptions": controls["rejected_corruption_count"],
        "output": display_path(config.output),
        "sha256": evidence_hash,
        "failed": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
