#!/usr/bin/env python3
"""Independently verify frozen Rust observability across additive scanner builds."""

from __future__ import annotations

import argparse
import collections
import gzip
import io
import json
from dataclasses import dataclass
from pathlib import Path

from tools import rust_v7_observability_oracle as frozen
from tools import rust_v7_observability_variant as original
from tools import rust_v8_deep_contract_oracle as deep


SCHEMA = "rebar-rust-v8-scanner-variant-observability-v1"
ORIGINAL_TOOL_SHA256 = (
    "f12af342c8f8d1b0a24dc8a2e80e7a82fe3b80ffe9d94f1242cb2ac8f0293f30"
)
ORIGINAL_ARCHIVE_SHA256 = (
    "9a228416d4de30190180c62ce2ee9b6fd932602317b1403e4d99f590c16e6231"
)
CMETHOD_EDGE_SHA256 = (
    "4006d192d61e7827bc46e298c598f570bef1baba3c05e03bcae66453fc1e0eba"
)
CMETHOD_DEEP_SHA256 = (
    "d34ad5d340f8185a92650fb916535536e1f6325a4761c0f97e638e20bffc0e4d"
)
DEEP_SOURCE_SHA256 = (
    "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978"
)
DEEP_RUNNER_SHA256 = (
    "4999fbf5314c55c6d26c2d9a005460fbd7bb820841d27c95f06f335772f68835"
)
DEEP_FAILURE_SHA256 = (
    "db43cbf8be1d6891eb4f009b8ae92995a6434f9753b944fbf0a8ed0b44237192"
)
DEEP_FIXTURE_SHA256 = (
    "c72a5e47f15c94ce13ce34d4918c05ef81eea5b010ac119b255264e60939ef16"
)


@dataclass(frozen=True)
class ScannerVariant:
    name: str
    edge_name: str
    edge_sha256: str
    archive_name: str


VARIANTS = {
    "scanner-lifetimes": ScannerVariant(
        "scanner-lifetimes",
        "rust-v8-edge-oracle-rust-scanner-lifetimes.json.gz",
        original.SCANNER_EDGE_SHA256,
        "rust-v8-observability-scanner-lifetimes.json.gz",
    ),
    "scanner-cmethod": ScannerVariant(
        "scanner-cmethod",
        "rust-v8-edge-oracle-rust-scanner-cmethod.json.gz",
        CMETHOD_EDGE_SHA256,
        "rust-v8-observability-scanner-cmethod.json.gz",
    ),
}
DEEP_ARCHIVE = (
    frozen.ROOT / "candidates/audits/RUST-V8-DEEP-CONTRACT-SCANNER-CMETHOD.json.gz"
)
DEEP_FAILURE = frozen.ROOT / "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def current_source() -> dict:
    source = Path(__file__).resolve()
    return {
        "path": source.relative_to(frozen.ROOT).as_posix(),
        "sha256": frozen.path_digest(source),
    }


def infer_variant(edge_path: Path) -> ScannerVariant:
    requested = Path(edge_path)
    require(not requested.is_symlink(), "the canonical edge must not be a symlink")
    resolved = requested.resolve()
    for variant in VARIANTS.values():
        canonical = (frozen.EVIDENCE / variant.edge_name).resolve()
        if resolved == canonical:
            require(
                frozen.path_digest(canonical) == variant.edge_sha256,
                f"the frozen {variant.name} edge archive changed",
            )
            return variant
    raise AssertionError("only an explicitly frozen canonical scanner edge is authorized")


def canonical_archive(value: dict) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(
        filename="", fileobj=output, mode="wb", compresslevel=9, mtime=0
    ) as stream:
        stream.write(frozen.canonical(value))
    return output.getvalue()


def read_canonical_archive(path: Path, expected_sha256: str | None = None) -> dict:
    requested = Path(path)
    require(not requested.is_symlink(), "frozen evidence must not be a symlink")
    require(requested.is_file(), "frozen evidence is missing")
    if expected_sha256 is not None:
        require(
            frozen.path_digest(requested) == expected_sha256,
            "frozen evidence archive fingerprint changed",
        )
    raw = requested.read_bytes()
    require(len(raw) >= 10 and raw[:2] == b"\x1f\x8b", "evidence is not gzip")
    require(
        not raw[3] & 0x08 and raw[4:8] == b"\x00\x00\x00\x00",
        "frozen evidence gzip is nondeterministic",
    )
    try:
        payload = gzip.decompress(raw)
        report = json.loads(payload)
    except (OSError, EOFError, ValueError, json.JSONDecodeError) as error:
        raise AssertionError("frozen gzip evidence cannot be decoded") from error
    require(isinstance(report, dict), "frozen evidence report is not an object")
    require(frozen.canonical(report) == payload, "frozen evidence JSON is not canonical")
    require(canonical_archive(report) == raw, "frozen archive cannot be reproduced")
    return report


def validate_archived_first_scanner(history: dict) -> dict:
    first_source = Path(original.__file__).resolve()
    require(
        first_source == (frozen.ROOT / "tools/rust_v7_observability_variant.py").resolve(),
        "the first scanner verification source was replaced",
    )
    require(
        frozen.path_digest(first_source) == ORIGINAL_TOOL_SHA256,
        "the first scanner verification source changed",
    )
    first_path = frozen.EVIDENCE / VARIANTS["scanner-lifetimes"].archive_name
    first = read_canonical_archive(first_path, ORIGINAL_ARCHIVE_SHA256)
    require(first.get("schema") == original.SCHEMA, "the first scanner schema changed")
    require(first.get("status") == "PASS", "the first scanner evidence no longer passes")
    require(
        first.get("checks") == 479
        and first.get("self_oracle_checks") == 479
        and first.get("candidate_checks") == 479,
        "the first scanner lost a frozen observation",
    )
    require(
        first.get("self_oracle_failures") == []
        and first.get("candidate_failures") == [],
        "the first scanner hides public mismatches",
    )
    require(
        first.get("script")
        == {
            "path": "tools/rust_v7_observability_variant.py",
            "sha256": ORIGINAL_TOOL_SHA256,
        },
        "the first scanner source self-reference changed",
    )
    require(
        first.get("immutable_frozen_baseline") == history,
        "the first scanner historical baseline changed",
    )
    standard_a = first.get("standard_library_a")
    standard_b = first.get("standard_library_b")
    candidate = first.get("candidate")
    original.validate_worker(standard_a, "stdlib-a")
    original.validate_worker(standard_b, "stdlib-b")
    original.validate_worker(candidate, "candidate")
    require(
        not frozen.mismatch_records(
            standard_a["observations"], standard_b["observations"]
        ),
        "the original scanner standard-library self-control changed",
    )
    require(
        not frozen.mismatch_records(
            standard_a["observations"], candidate["observations"]
        ),
        "the original scanner public observations changed",
    )
    require(
        original.classify_resolved_iterators(standard_a, candidate)
        == first.get("resolved_iterator_controls"),
        "the first scanner iterator evidence changed",
    )
    require(
        first.get("private_binder_checks") == 34
        and first.get("private_binder_failures") == []
        and len(candidate.get("private_binder_observations", [])) == 34
        and all(item.get("passed") for item in candidate["private_binder_observations"]),
        "the first scanner private binder evidence changed",
    )
    guards = candidate.get("forbidden_regex_guard_observations", [])
    require(
        first.get("forbidden_regex_guards") == 13
        and len(guards) == 13
        and all(item.get("passed") for item in guards),
        "the first scanner regex-delegation evidence changed",
    )
    controls = first.get("negative_controls", [])
    require(
        len(controls) == 16 and all(item.get("passed") for item in controls),
        "the first scanner malicious negative controls changed",
    )

    old_config = VARIANTS["scanner-lifetimes"]
    old_edge_path = frozen.EVIDENCE / old_config.edge_name
    require(
        frozen.path_digest(old_edge_path) == old_config.edge_sha256,
        "the preserved first scanner edge archive changed",
    )
    _, old_edge_document = frozen.read_edge_archive(old_edge_path)
    old_artifacts = frozen.validate_edge_document(
        old_edge_document,
        frozen.frozen_edge_baseline(),
        check_live_files=False,
    )
    expected_artifacts = [
        {
            "role": role,
            "path": path.relative_to(frozen.ROOT).as_posix(),
            "sha256": digest,
        }
        for role, (path, digest) in sorted(old_artifacts.items())
    ]
    require(
        candidate.get("native_artifacts") == expected_artifacts
        and first.get("native_artifacts") == expected_artifacts,
        "the first scanner original five artifact fingerprints changed",
    )
    first_edge = first.get("edge_oracle", {})
    require(
        first_edge.get("path")
        == old_edge_path.relative_to(frozen.ROOT).as_posix()
        and first_edge.get("sha256") == old_config.edge_sha256
        and first_edge.get("checks") == frozen.EDGE_CHECKS
        and first_edge.get("artifacts") == expected_artifacts,
        "the first scanner edge authorization changed",
    )
    require(
        first.get("holdout") == "NOT ACCESSED"
        and first.get("performance") == "NOT MEASURED",
        "the first scanner archive accessed a benchmark",
    )
    return {
        "source": first["script"],
        "archive": {
            "path": first_path.relative_to(frozen.ROOT).as_posix(),
            "sha256": ORIGINAL_ARCHIVE_SHA256,
        },
        "edge": first_edge,
        "checks": 479,
        "private_binder_checks": 34,
        "forbidden_regex_guards": 13,
        "negative_controls": 16,
        "report": first,
    }


def validate_preserved_deep(edge: dict) -> dict:
    require(
        frozen.path_digest(Path(deep.__file__).resolve()) == DEEP_SOURCE_SHA256,
        "the frozen 393-case deep-contract source changed",
    )
    runner = frozen.ROOT / "tools/rust_v8_deep_contract_variant.py"
    require(
        frozen.path_digest(runner) == DEEP_RUNNER_SHA256,
        "the frozen deep-contract variant runner changed",
    )
    require(
        frozen.path_digest(DEEP_FAILURE) == DEEP_FAILURE_SHA256,
        "the original 104-failure deep-contract archive changed",
    )
    report = read_canonical_archive(DEEP_ARCHIVE, CMETHOD_DEEP_SHA256)
    require(report.get("schema") == deep.SCHEMA, "deep-contract schema changed")
    require(report.get("python") == "3.14.6", "deep-contract Python changed")
    require(report.get("seed") == deep.SEED, "deep-contract seed changed")
    require(report.get("checks") == 393, "deep-contract denominator changed")
    require(
        report.get("fixture_sha256") == DEEP_FIXTURE_SHA256
        and deep.digest(deep.build_cases()) == DEEP_FIXTURE_SHA256,
        "deep-contract fixture changed",
    )
    require(
        report.get("status") == "FAIL"
        and report.get("public_mismatch_count") == 43,
        "the 43 remaining genuine deep-contract mismatches were hidden",
    )
    require(
        report.get("suite_path") == "tools/rust_v8_deep_contract_oracle.py"
        and report.get("suite_sha256") == DEEP_SOURCE_SHA256,
        "deep-contract suite provenance changed",
    )
    require(
        report.get("variant_runner")
        == {
            "path": "tools/rust_v8_deep_contract_variant.py",
            "sha256": DEEP_RUNNER_SHA256,
        },
        "deep-contract variant provenance changed",
    )
    reference = report.get("reference")
    repeat = report.get("reference_independent_repeat")
    candidate = report.get("candidate")
    expected_ids = [case["id"] for case in deep.build_cases()]
    for role, worker in (
        ("stdlib-a", reference),
        ("stdlib-b", repeat),
        ("candidate", candidate),
    ):
        require(isinstance(worker, dict), f"deep-contract {role} results are missing")
        observations = worker.get("observations")
        require(
            worker.get("checks") == 393
            and isinstance(observations, list)
            and len(observations) == 393,
            f"deep-contract {role} does not preserve all 393 results",
        )
        require(
            [row.get("id") for row in observations] == expected_ids,
            f"deep-contract {role} changed a frozen case identity",
        )
        require(
            deep.digest(observations) == worker.get("observation_sha256"),
            f"deep-contract {role} result digest changed",
        )
        for row in observations:
            require(
                deep.digest(row.get("observation")) == row.get("sha256"),
                f"deep-contract {role} case digest changed: {row.get('id')}",
            )
    require(
        report.get("stdlib_vs_stdlib_mismatches") == []
        and deep.mismatches(reference["observations"], repeat["observations"]) == [],
        "the deep-contract independent Python references disagree",
    )
    mismatches = deep.mismatches(reference["observations"], candidate["observations"])
    require(
        len(mismatches) == 43 and mismatches == report.get("public_mismatches"),
        "the deep-contract mismatch rows were altered or omitted",
    )
    expected_families = dict(
        sorted(collections.Counter(row["family"] for row in mismatches).items())
    )
    require(
        report.get("public_mismatch_family_counts") == expected_families,
        "the remaining deep-contract mismatch family counts changed",
    )
    require(
        not any("scanner" in row.get("family", "") for row in mismatches),
        "a remaining scanner mismatch was hidden",
    )
    require(
        report.get("forbidden_regex_guards") == 13
        and len(report.get("guard_observations", [])) == 13
        and all(
            row.get("type") == "GuardSignal"
            for row in report["guard_observations"]
        ),
        "deep-contract regex delegation controls changed",
    )
    require(
        report.get("native_artifacts") == edge.get("artifacts"),
        "deep-contract artifacts do not identify the current scanner build",
    )
    deep_edge = report.get("edge_oracle", {})
    require(
        deep_edge.get("archive_sha256") == edge.get("sha256")
        and deep_edge.get("checks") == frozen.EDGE_CHECKS
        and deep_edge.get("failed") == 0,
        "deep-contract edge provenance differs from the current build",
    )
    previous_failure = report.get("frozen_failure_evidence", {})
    require(
        previous_failure.get("archive_sha256") == DEEP_FAILURE_SHA256
        and previous_failure.get("public_mismatch_count") == 104
        and previous_failure.get("status") == "FAIL",
        "the original 104 deep-contract failures were hidden",
    )
    require(
        report.get("holdout") == "NOT ACCESSED"
        and report.get("performance") == "NOT MEASURED",
        "deep-contract evidence used a holdout or benchmark",
    )
    return {
        "archive": {
            "path": DEEP_ARCHIVE.relative_to(frozen.ROOT).as_posix(),
            "sha256": CMETHOD_DEEP_SHA256,
        },
        "checks": 393,
        "public_mismatch_count": 43,
        "scanner_mismatch_count": 0,
        "original_public_mismatch_count": 104,
        "report": report,
    }


def validated_edge(edge_path: Path) -> tuple[ScannerVariant, dict]:
    variant = infer_variant(edge_path)
    require(variant.name == "scanner-cmethod", "only the current scanner variant may be rebuilt")
    expected_path = frozen.EVIDENCE / variant.edge_name
    provenance, _ = frozen.validate_edge_oracle(expected_path)
    require(
        provenance.get("sha256") == variant.edge_sha256
        and provenance.get("checks") == frozen.EDGE_CHECKS
        and provenance.get("categories") == frozen.EDGE_CATEGORIES
        and provenance.get("failed") == 0
        and len(provenance.get("artifacts", [])) == 5,
        "the current scanner edge correctness or native provenance is incomplete",
    )
    return variant, provenance


def additional_controls(
    standard_a: dict,
    standard_b: dict,
    candidate: dict,
    edge: dict,
    deep_reference: dict,
) -> list[dict]:
    controls = original.collect_negative_controls(
        standard_a, standard_b, candidate, edge
    )

    def reject_candidate(label, mutate):
        changed = original.clone(candidate)
        mutate(changed)
        return original.expect_rejection(
            label,
            lambda: original.validate_live_reports(
                standard_a, standard_b, changed, edge
            ),
        )

    def duplicate_observation(report):
        report["observations"][1] = original.clone(report["observations"][0])
        report["observation_sha256"] = frozen.value_digest(report["observations"])

    def reorder_observations(report):
        rows = report["observations"]
        rows[0], rows[1] = rows[1], rows[0]
        report["observation_sha256"] = frozen.value_digest(rows)

    def duplicate_guard(report):
        report["forbidden_regex_guard_observations"][1] = original.clone(
            report["forbidden_regex_guard_observations"][0]
        )

    def omit_private(report):
        report["private_binder_observations"].pop()

    def stale_edge_path(report):
        report["edge_oracle"]["path"] = (
            "candidates/evidence/rust-v8-edge-oracle-rust-scanner-lifetimes.json.gz"
        )

    def stale_edge_hash(report):
        report["edge_oracle"]["sha256"] = original.SCANNER_EDGE_SHA256

    def poison_edge_source(report):
        report["edge_oracle"]["script_sha256"] = "0" * 64

    def poison_edge_reference(report):
        report["edge_oracle"]["reference_sha256"] = "0" * 64

    def wrong_role(report):
        report["role"] = "stdlib-a"

    def access_holdout(report):
        report["holdout"] = "ACCESSED"

    def measure_performance(report):
        report["performance"] = "MEASURED"

    mutations = (
        ("duplicate-frozen-public-observation", duplicate_observation),
        ("reordered-frozen-public-observations", reorder_observations),
        ("duplicated-regex-delegation-guard", duplicate_guard),
        ("missing-private-native-binder", omit_private),
        ("stale-first-scanner-edge-path", stale_edge_path),
        ("stale-first-scanner-edge-hash", stale_edge_hash),
        ("poisoned-current-edge-source", poison_edge_source),
        ("poisoned-current-edge-reference", poison_edge_reference),
        ("swapped-candidate-worker-role", wrong_role),
        ("forbidden-holdout-access", access_holdout),
        ("forbidden-performance-measurement", measure_performance),
    )
    controls.extend(reject_candidate(label, mutation) for label, mutation in mutations)

    def poisoned_deep(label, mutate):
        changed = original.clone(deep_reference)
        mutate(changed)
        return original.expect_rejection(
            label, lambda: validate_deep_document(changed, edge)
        )

    controls.extend(
        (
            poisoned_deep(
                "hidden-deep-contract-mismatch",
                lambda item: item.update(public_mismatch_count=0),
            ),
            poisoned_deep(
                "truncated-deep-contract-reference",
                lambda item: item["reference"]["observations"].pop(),
            ),
            poisoned_deep(
                "truncated-deep-contract-candidate",
                lambda item: item["candidate"]["observations"].pop(),
            ),
            poisoned_deep(
                "stale-deep-contract-edge",
                lambda item: item["edge_oracle"].update(
                    archive_sha256=original.SCANNER_EDGE_SHA256
                ),
            ),
        )
    )
    require(len(controls) == 31, "generalized scanner poison-control count changed")
    require(
        len({row.get("id") for row in controls}) == 31
        and all(row.get("passed") is True for row in controls),
        "a generalized scanner stale-artifact or observation poison was accepted",
    )
    return controls


def validate_deep_document(report: dict, edge: dict) -> None:
    require(report.get("schema") == deep.SCHEMA, "deep-contract schema changed")
    require(
        report.get("checks") == 393 and report.get("public_mismatch_count") == 43,
        "deep-contract results or honest remaining failures changed",
    )
    expected_ids = [case["id"] for case in deep.build_cases()]
    for role in ("reference", "reference_independent_repeat", "candidate"):
        worker = report.get(role)
        require(isinstance(worker, dict), f"deep-contract {role} is missing")
        rows = worker.get("observations")
        require(
            isinstance(rows, list)
            and len(rows) == 393
            and worker.get("checks") == 393,
            f"deep-contract {role} omitted frozen results",
        )
        require(
            [row.get("id") for row in rows] == expected_ids,
            f"deep-contract {role} changed frozen case identities",
        )
        require(
            deep.digest(rows) == worker.get("observation_sha256"),
            f"deep-contract {role} observation fingerprint changed",
        )
        require(
            all(
                deep.digest(row.get("observation")) == row.get("sha256")
                for row in rows
            ),
            f"deep-contract {role} contains a poisoned observation",
        )
    reference = report["reference"]["observations"]
    candidate = report["candidate"]["observations"]
    require(
        deep.mismatches(reference, report["reference_independent_repeat"]["observations"])
        == [],
        "the deep-contract independent reference was poisoned",
    )
    actual = deep.mismatches(reference, candidate)
    require(
        len(actual) == 43 and actual == report.get("public_mismatches"),
        "the 43 remaining deep-contract failures were hidden",
    )
    require(
        not any("scanner" in item.get("family", "") for item in actual),
        "a scanner-family deep-contract mismatch was omitted",
    )
    require(
        report.get("native_artifacts") == edge.get("artifacts")
        and report.get("edge_oracle", {}).get("archive_sha256")
        == edge.get("sha256"),
        "the deep-contract report belongs to a stale scanner build",
    )


def make_report(edge_path: Path) -> dict:
    history = original.check_frozen_history()
    first_scanner = validate_archived_first_scanner(history)
    variant, edge = validated_edge(edge_path)
    deep_evidence = validate_preserved_deep(edge)
    standard_a = frozen.run_worker("stdlib-a")
    standard_b = frozen.run_worker("stdlib-b")
    candidate = frozen.run_worker(
        "candidate", edge_oracle=frozen.EVIDENCE / variant.edge_name
    )
    validation = original.validate_live_reports(
        standard_a, standard_b, candidate, edge
    )
    controls = additional_controls(
        standard_a, standard_b, candidate, edge, deep_evidence["report"]
    )
    return {
        "schema": SCHEMA,
        "role": "scanner-variant-observability",
        "variant": variant.name,
        "status": "PASS",
        "python": "3.14.6",
        "seed": frozen.SEED,
        "goal_sha256": original.GOAL_SHA256,
        "fixture_sha256": frozen.FROZEN_FIXTURE_SHA256,
        "checks": 479,
        "self_oracle_checks": 479,
        "self_oracle_failures": validation["self_oracle_failures"],
        "candidate_checks": 479,
        "candidate_failures": validation["candidate_failures"],
        "private_binder_checks": 34,
        "private_binder_failures": [],
        "forbidden_regex_guards": 13,
        "negative_controls": controls,
        "negative_control_failures": 0,
        "immutable_frozen_baseline": history,
        "preserved_first_scanner": first_scanner,
        "preserved_deep_contract": deep_evidence,
        "edge_oracle": edge,
        "standard_library_a": standard_a,
        "standard_library_b": standard_b,
        "candidate": candidate,
        "private_binder_report": validation["private_binder_report"],
        "resolved_iterator_controls": validation["resolved_iterator_controls"],
        "native_artifacts": candidate["native_artifacts"],
        "expected_observation_sha256": standard_a["observation_sha256"],
        "actual_observation_sha256": candidate["observation_sha256"],
        "script": current_source(),
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def validate_report(report: dict, edge_path: Path) -> None:
    require(isinstance(report, dict), "scanner variant evidence is not an object")
    require(report.get("schema") == SCHEMA, "scanner variant schema changed")
    require(
        report.get("role") == "scanner-variant-observability",
        "scanner variant evidence role changed",
    )
    require(report.get("status") == "PASS", "scanner variant evidence did not pass")
    require(report.get("python") == "3.14.6", "scanner Python version changed")
    require(report.get("seed") == frozen.SEED, "scanner variant seed changed")
    require(
        report.get("goal_sha256") == original.GOAL_SHA256
        and frozen.path_digest(frozen.ROOT / "GOAL.md") == original.GOAL_SHA256,
        "the immutable experiment objective changed",
    )
    require(
        report.get("fixture_sha256") == frozen.FROZEN_FIXTURE_SHA256,
        "the frozen 479-case fixture changed",
    )
    require(
        report.get("checks") == 479
        and report.get("self_oracle_checks") == 479
        and report.get("candidate_checks") == 479,
        "scanner variant omitted frozen observations",
    )
    require(
        report.get("self_oracle_failures") == []
        and report.get("candidate_failures") == [],
        "scanner variant concealed an observability failure",
    )
    require(
        report.get("private_binder_checks") == 34
        and report.get("private_binder_failures") == []
        and report.get("forbidden_regex_guards") == 13,
        "scanner variant weakened a native safety or poison control",
    )
    require(report.get("script") == current_source(), "scanner self-reference was poisoned")
    require(
        report.get("holdout") == "NOT ACCESSED"
        and report.get("performance") == "NOT MEASURED",
        "scanner variant accessed benchmark or holdout data",
    )

    history = original.check_frozen_history()
    require(
        report.get("immutable_frozen_baseline") == history,
        "scanner variant changed immutable historical evidence",
    )
    first = validate_archived_first_scanner(history)
    require(
        report.get("preserved_first_scanner") == first,
        "scanner variant changed first-scanner evidence",
    )
    variant, edge = validated_edge(edge_path)
    require(report.get("variant") == variant.name, "scanner variant identity changed")
    require(report.get("edge_oracle") == edge, "scanner variant edge proof changed")
    deep_evidence = validate_preserved_deep(edge)
    require(
        report.get("preserved_deep_contract") == deep_evidence,
        "scanner variant omitted or altered a deep-contract result",
    )
    standard_a = report.get("standard_library_a")
    standard_b = report.get("standard_library_b")
    candidate = report.get("candidate")
    result = original.validate_live_reports(standard_a, standard_b, candidate, edge)
    require(
        report.get("private_binder_report") == result["private_binder_report"]
        and report.get("resolved_iterator_controls")
        == result["resolved_iterator_controls"],
        "scanner private binder or genuine callable-iterator controls changed",
    )
    require(
        report.get("native_artifacts") == candidate.get("native_artifacts")
        and len(candidate.get("native_artifacts", [])) == 5,
        "scanner variant changed or omitted a native production artifact",
    )
    require(
        report.get("expected_observation_sha256")
        == standard_a.get("observation_sha256")
        and report.get("actual_observation_sha256")
        == candidate.get("observation_sha256"),
        "scanner variant full observation fingerprint changed",
    )
    controls = report.get("negative_controls")
    require(
        isinstance(controls, list)
        and len(controls) == 31
        and len({row.get("id") for row in controls}) == 31
        and all(row.get("passed") is True for row in controls)
        and report.get("negative_control_failures") == 0,
        "scanner variant accepted a stale, forged, or weakened control",
    )


def variant_archive(variant: ScannerVariant) -> Path:
    return frozen.EVIDENCE / variant.archive_name


def write_report(report: dict, edge_path: Path) -> str:
    variant, _ = validated_edge(edge_path)
    destination = variant_archive(variant)
    require(
        destination.resolve()
        == (frozen.EVIDENCE / "rust-v8-observability-scanner-cmethod.json.gz").resolve(),
        "refusing to overwrite an original scanner or frozen oracle archive",
    )
    validate_report(report, edge_path)
    require(not destination.is_symlink(), "scanner evidence must not be a symlink")
    require(not destination.exists(), "scanner evidence already exists; refusing to overwrite")
    payload = canonical_archive(report)
    require(payload == canonical_archive(report), "scanner evidence compression is nondeterministic")
    with destination.open("xb") as output:
        output.write(payload)
    persisted = read_canonical_archive(destination)
    require(persisted == report, "scanner evidence failed an exact round-trip")
    validate_report(persisted, edge_path)
    return frozen.path_digest(destination)


def self_reference_controls(report: dict, edge_path: Path) -> list[dict]:
    checks = []
    source = original.clone(report)
    source["script"]["sha256"] = "0" * 64
    checks.append(
        original.expect_rejection(
            "poisoned-variant-source-self-reference",
            lambda: validate_report(source, edge_path),
        )
    )
    history = original.clone(report)
    history["immutable_frozen_baseline"]["source"]["sha256"] = "0" * 64
    checks.append(
        original.expect_rejection(
            "poisoned-original-oracle-source-reference",
            lambda: validate_report(history, edge_path),
        )
    )
    prior = original.clone(report)
    prior["preserved_first_scanner"]["archive"]["sha256"] = "0" * 64
    checks.append(
        original.expect_rejection(
            "poisoned-first-scanner-archive-reference",
            lambda: validate_report(prior, edge_path),
        )
    )
    deep_report = original.clone(report)
    deep_report["preserved_deep_contract"]["archive"]["sha256"] = "0" * 64
    checks.append(
        original.expect_rejection(
            "poisoned-preserved-deep-archive-reference",
            lambda: validate_report(deep_report, edge_path),
        )
    )
    require(len(checks) == 4, "self-reference poison denominator changed")
    require(all(row["passed"] for row in checks), "a source or archive poison was accepted")
    return checks


def announce(report: dict, *, phase: str, archive_sha256: str | None = None) -> None:
    result = {
        "schema": SCHEMA,
        "phase": phase,
        "variant": report["variant"],
        "status": report["status"],
        "checks": report["checks"],
        "self_oracle_failures": len(report["self_oracle_failures"]),
        "candidate_failures": len(report["candidate_failures"]),
        "private_binder_checks": report["private_binder_checks"],
        "private_binder_failures": len(report["private_binder_failures"]),
        "forbidden_regex_guards": report["forbidden_regex_guards"],
        "native_artifacts": len(report["native_artifacts"]),
        "resolved_iterator_controls": report["resolved_iterator_controls"]["checks"],
        "negative_controls": len(report["negative_controls"]),
        "frozen_evidence_poison_controls": len(
            report["immutable_frozen_baseline"]["frozen_artifact_poison_controls"]
        ),
        "preserved_first_scanner_checks": report["preserved_first_scanner"]["checks"],
        "preserved_deep_checks": report["preserved_deep_contract"]["checks"],
        "preserved_deep_public_mismatches": report["preserved_deep_contract"][
            "public_mismatch_count"
        ],
        "preserved_deep_scanner_mismatches": report["preserved_deep_contract"][
            "scanner_mismatch_count"
        ],
        "edge_checks": report["edge_oracle"]["checks"],
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    if "self_reference_controls" in report:
        result["self_reference_controls"] = len(report["self_reference_controls"])
    if archive_sha256 is not None:
        variant = VARIANTS[report["variant"]]
        result["archive"] = variant_archive(variant).relative_to(frozen.ROOT).as_posix()
        result["archive_sha256"] = archive_sha256
    print(json.dumps(result, ensure_ascii=True, sort_keys=True), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("self-test", help="validate every frozen and poisoned reference")
    check.add_argument("--edge-oracle", type=Path, required=True)
    check.add_argument("--output", type=Path)
    candidate = commands.add_parser("candidate", help="verify the current canonical scanner")
    candidate.add_argument("--edge-oracle", type=Path, required=True)
    verify = commands.add_parser("verify", help="verify the immutable scanner variant archive")
    verify.add_argument("--edge-oracle", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "self-test":
        report = make_report(args.edge_oracle)
        validate_report(report, args.edge_oracle)
        report["self_reference_controls"] = self_reference_controls(
            report, args.edge_oracle
        )
        require(
            canonical_archive(report) == canonical_archive(report),
            "scanner self-reference gzip is nondeterministic",
        )
        if args.output is not None:
            original.write_self_test(args.output, report)
        announce(report, phase="self-test")
        return 0

    if args.command == "candidate":
        report = make_report(args.edge_oracle)
        report["self_reference_controls"] = self_reference_controls(
            report, args.edge_oracle
        )
        fingerprint = write_report(report, args.edge_oracle)
        announce(report, phase="candidate", archive_sha256=fingerprint)
        return 0

    variant, _ = validated_edge(args.edge_oracle)
    archive = variant_archive(variant)
    report = read_canonical_archive(archive)
    validate_report(report, args.edge_oracle)
    require(
        len(report.get("self_reference_controls", [])) == 4
        and all(row.get("passed") for row in report["self_reference_controls"]),
        "the archived scanner self-reference poison controls changed",
    )
    announce(report, phase="verify", archive_sha256=frozen.path_digest(archive))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
