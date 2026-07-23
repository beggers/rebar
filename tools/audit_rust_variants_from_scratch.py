#!/usr/bin/env python3
"""Fail-closed, additive provenance gate for the frozen Rust cmethod variant."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import audit_from_scratch as shared
from tools import audit_rust_from_scratch as scanner


DEFAULT_EDGE = (
    ROOT / "candidates" / "evidence"
    / "rust-v8-edge-oracle-rust-scanner-cmethod.json.gz"
)
AUTHORIZED_OUTPUT = (
    ROOT / "candidates" / "audits" / "RUST-V8-CMETHOD-FROM-SCRATCH.json"
)
MAX_EDGE_COMPRESSED_BYTES = 16 * 1024 * 1024
MAX_EDGE_JSON_BYTES = 32 * 1024 * 1024
EDGE_CHECK_COUNT = 223198
EDGE_CATEGORY_COUNT = 49
EXPECTED_SCANNER_CONTROL_COUNT = 49
EXPECTED_UPSTREAM_CONTROL_COUNT = 76
MINIMUM_VARIANT_NEGATIVE_CONTROLS = 49

ARTIFACT_PATHS: dict[str, Path] = {
    "public-python": ROOT / "candidates" / "rust_candidate.py",
    "native-bridge": (
        ROOT / "candidates" / "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
    ),
    "native-engine": ROOT / "candidates" / "_rust_engine.so",
    "native-source": ROOT / "candidates" / "rust" / "src" / "lib.rs",
    "bridge-source": ROOT / "candidates" / "rust" / "py_bridge.c",
}
PINNED_ARTIFACT_HASHES = {
    "public-python": (
        "1111a419d65d44775d1f4b0cb6a728dea8de44a592597341596533351c16018e"
    ),
    "native-bridge": (
        "8ca1d493f957c493c97785531b27d3356ce21cf4ed2ae3bde2713f9869f67327"
    ),
    "native-engine": (
        "890f9e34e966244067a3dc173c2276043ae15d4830a05228fb37ec2571aa17cd"
    ),
    "native-source": (
        "a2fa04912bb1f6957f833560446f4d3d1c5d13df8b5efac992fa63e28803668b"
    ),
    "bridge-source": (
        "8dba6d2c3b6d8c0d3c044c91a62b6e4a2664dde0df3d3d974044917c96d6a713"
    ),
}

EDGE_PINS = scanner.EdgePins(
    compressed_sha256=(
        "4006d192d61e7827bc46e298c598f570bef1baba3c05e03bcae66453fc1e0eba"
    ),
    result_sha256=(
        "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
    ),
    script_sha256=(
        "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
    ),
    component_sha256={
        "candidate_artifacts": (
            "789ca573ed03687c1a30468b571ed256e82e20cac895ae4bf8866d17cb393075"
        ),
        "categories": (
            "99a76d581e3fd8b68239867722a032e6f67701524896ec75684e11184f721ca8"
        ),
        "embedded_frozen_oracles": (
            "7ba1fe99e4fd8389e1a4116c85c611ad847dcb41478d367c6ca059f24b57d4bc"
        ),
        "independent_source_seeds": (
            "10b94594042987a1e9229b782bcdc9ce5d7d0543e91a203df18fef5733416bb0"
        ),
        "json_normalization": (
            "62c42c6358643a3f99ff9cf4721059c8425965c59aec25c49b4efbd0219b4544"
        ),
        "membership_partitions": (
            "785157a16916365ec6d9c6516a0c13499dca10c50ef4d2a988f2d145e69a9855"
        ),
    },
)

PINNED_SCANNER_CONTROL_NAMES = frozenset({
    "all_76_isolated_shared_poison_controls",
    "accept_complete_in_memory_canonical_edge",
    "reject_wrong_candidate_module",
    "reject_wrong_canonical_edge_schema",
    "reject_nonzero_canonical_edge_failures",
    "reject_missing_canonical_failure_list",
    "reject_malformed_canonical_check_count",
    "reject_missing_canonical_check_count",
    "reject_changed_canonical_check_count",
    "reject_changed_canonical_result_digest",
    "reject_changed_canonical_expected_digest",
    "reject_changed_frozen_edge_categories",
    "reject_nonempty_edge_failure_list",
    "reject_changed_frozen_script_digest",
    "reject_changed_frozen_oracle_component",
    "reject_changed_membership_partition",
    "reject_changed_holdout_declaration",
    "reject_changed_no_timing_declaration",
    "reject_stale_native_engine",
    "reject_stale_native_bridge",
    "reject_changed_live_bridge_source",
    "reject_missing_frozen_live_artifact",
    "reject_duplicate_frozen_artifact_role",
    "reject_changed_immutable_gzip_digest",
    "reject_truncated_immutable_gzip",
    "reject_wrong_output_path",
    "reject_wrong_edge_oracle_path",
    "reject_wrong_python_version",
    "reject_stdlib_re_import",
    "reject_cpython_sre_import",
    "reject_external_regex_package",
    "reject_cross_candidate_module",
    "reject_obfuscated_dynamic_import_bypass",
    "reject_environment_engine_dispatch",
    "reject_native_external_regex",
    "reject_native_dynamic_engine",
    "reject_native_cpython_engine",
    "reject_native_cross_engine_extern",
    "reject_renamed_external_cargo_manifest",
    "accept_owned_in_memory_rust_elf_pipeline",
    "reject_native_bridge_compiler_bypass",
    "reject_cross_family_native_bridge_link",
    "accept_owned_in_memory_rust_mappings",
    "reject_cross_family_native_memory_mapping",
    "reject_external_regex_memory_mapping",
    "reject_corrupted_upstream_poison_count",
    "reject_corrupted_upstream_poison_names",
    "reject_bypassed_upstream_poison_control",
    "reject_unisolated_upstream_poison_execution",
})


def observe_artifacts() -> tuple[dict[str, dict[str, Any]], list[str]]:
    observed: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for role, path in ARTIFACT_PATHS.items():
        try:
            data = scanner.bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            issues.append(f"unreadable Rust cmethod {role}: {error}")
            continue
        actual = hashlib.sha256(data).hexdigest()
        expected = PINNED_ARTIFACT_HASHES[role]
        matches = actual == expected
        if not matches:
            issues.append(
                f"Rust cmethod {role} does not match its independently frozen artifact"
            )
        observed[role] = {
            "role": role,
            "path": scanner.relative(path),
            "sha256": actual,
            "expected_sha256": expected,
            "matches_frozen_edge": matches,
        }
    if set(observed) != set(ARTIFACT_PATHS):
        issues.append("the Rust cmethod variant must expose exactly five frozen artifacts")
    return observed, issues


def validate_edge_document(
    document: Any,
    compressed_sha256: str,
    observed_artifacts: dict[str, dict[str, Any]],
    pins: scanner.EdgePins = EDGE_PINS,
) -> dict[str, Any]:
    issues: list[str] = []
    if compressed_sha256 != pins.compressed_sha256:
        issues.append("the compressed immutable cmethod edge-oracle SHA-256 changed")
    if not isinstance(document, dict):
        return {
            "passed": False,
            "issues": issues + ["the canonical cmethod edge JSON must be an object"],
            "archive_sha256": compressed_sha256,
            "correctness_checks": None,
            "artifact_count": 0,
        }

    required: dict[str, Any] = {
        "schema": "rebar-v7-independent-edge-oracle-v1",
        "module": "candidates.rust_candidate",
        "python": "3.14.6",
        "correctness_checks": EDGE_CHECK_COUNT,
        "failed": 0,
        "expected_sha256": pins.result_sha256,
        "actual_sha256": pins.result_sha256,
        "script_sha256": pins.script_sha256,
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }
    for key, expected in required.items():
        actual = document.get(key)
        if type(actual) is not type(expected) or actual != expected:
            issues.append(f"canonical cmethod edge field {key!r} changed")
    if document.get("failures") != []:
        issues.append("the canonical cmethod edge failures are missing or nonempty")

    categories = document.get("categories")
    if not isinstance(categories, dict) or len(categories) != EDGE_CATEGORY_COUNT:
        issues.append("the canonical cmethod edge must have exactly 49 categories")
    elif any(type(value) is not int or value < 0 for value in categories.values()):
        issues.append("a canonical cmethod category count is malformed")
    elif sum(categories.values()) != EDGE_CHECK_COUNT:
        issues.append("canonical cmethod category counts must sum to 223198")

    component_hashes: dict[str, str] = {}
    for key, expected in pins.component_sha256.items():
        if key not in document:
            issues.append(f"the canonical cmethod component {key!r} is missing")
            continue
        try:
            actual = scanner.canonical_sha256(document[key])
        except (TypeError, ValueError, UnicodeError) as error:
            issues.append(f"canonical cmethod component {key!r} is invalid: {error}")
            continue
        component_hashes[key] = actual
        if actual != expected:
            issues.append(f"the independently frozen cmethod {key!r} digest changed")

    artifacts = document.get("candidate_artifacts")
    roles: set[str] = set()
    if not isinstance(artifacts, list) or len(artifacts) != len(ARTIFACT_PATHS):
        issues.append("the canonical cmethod edge must contain exactly five artifacts")
    else:
        for item in artifacts:
            if not isinstance(item, dict) or set(item) != {"path", "role", "sha256"}:
                issues.append("a frozen cmethod artifact has a malformed schema")
                continue
            role = item["role"]
            if role not in ARTIFACT_PATHS or role in roles:
                issues.append("a frozen cmethod artifact role is unapproved or duplicated")
                continue
            roles.add(role)
            expected_path = scanner.relative(ARTIFACT_PATHS[role])
            expected_digest = PINNED_ARTIFACT_HASHES[role]
            if item["path"] != expected_path:
                issues.append(f"frozen cmethod {role} artifact path changed")
            if item["sha256"] != expected_digest:
                issues.append(f"frozen cmethod {role} artifact digest changed")
            observed = observed_artifacts.get(role)
            if (
                not isinstance(observed, dict)
                or observed.get("path") != expected_path
                or observed.get("sha256") != expected_digest
                or observed.get("matches_frozen_edge") is not True
            ):
                issues.append(f"live cmethod {role} differs from its frozen artifact")
    if roles != set(ARTIFACT_PATHS):
        issues.append("the canonical cmethod artifact-role manifest is incomplete")

    partitions = document.get("membership_partitions")
    if not isinstance(partitions, list) or len(partitions) != 4:
        issues.append("the canonical cmethod edge requires exactly four membership partitions")
    else:
        for item in partitions:
            if (
                not isinstance(item, dict)
                or item.get("actual_sha256") != item.get("expected_sha256")
                or item.get("stride") != 4099
            ):
                issues.append("a cmethod membership partition is malformed or mismatched")

    return {
        "passed": not issues,
        "issues": issues,
        "file": scanner.relative(DEFAULT_EDGE),
        "archive_sha256": compressed_sha256,
        "expected_archive_sha256": pins.compressed_sha256,
        "schema": document.get("schema"),
        "module": document.get("module"),
        "correctness_checks": document.get("correctness_checks"),
        "failed": document.get("failed"),
        "expected_sha256": document.get("expected_sha256"),
        "actual_sha256": document.get("actual_sha256"),
        "script_sha256": document.get("script_sha256"),
        "category_count": len(categories) if isinstance(categories, dict) else 0,
        "category_check_sum": (
            sum(categories.values())
            if isinstance(categories, dict)
            and all(type(item) is int for item in categories.values())
            else None
        ),
        "artifact_count": len(roles),
        "canonical_component_sha256": component_hashes,
        "holdout": document.get("holdout"),
        "performance": document.get("performance"),
    }


def validate_edge_bytes(
    compressed: bytes,
    observed_artifacts: dict[str, dict[str, Any]],
    pins: scanner.EdgePins = EDGE_PINS,
) -> dict[str, Any]:
    digest = hashlib.sha256(compressed).hexdigest()

    def reject(reason: str) -> dict[str, Any]:
        return {
            "passed": False,
            "issues": [reason],
            "archive_sha256": digest,
            "correctness_checks": None,
            "artifact_count": 0,
        }

    if len(compressed) > MAX_EDGE_COMPRESSED_BYTES:
        return reject("the compressed cmethod edge exceeds its bounded audit limit")
    if digest != pins.compressed_sha256:
        return reject("the compressed immutable cmethod edge-oracle SHA-256 changed")
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as archive:
            decoded = archive.read(MAX_EDGE_JSON_BYTES + 1)
        if len(decoded) > MAX_EDGE_JSON_BYTES:
            raise ValueError("the decompressed cmethod edge exceeds its bounded audit limit")
        document = json.loads(decoded)
    except (EOFError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        return reject(f"invalid bounded cmethod gzip or canonical edge JSON: {error}")
    return validate_edge_document(document, digest, observed_artifacts, pins)


def load_edge_oracle(
    path: Path,
    observed_artifacts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if not scanner.authorized_path(path, DEFAULT_EDGE):
        return {
            "passed": False,
            "issues": ["only the expressly authorized immutable cmethod edge may be read"],
            "correctness_checks": None,
            "artifact_count": 0,
        }
    try:
        compressed = scanner.bounded_binary(DEFAULT_EDGE, MAX_EDGE_COMPRESSED_BYTES)
    except (OSError, ValueError) as error:
        return {
            "passed": False,
            "issues": [f"the immutable cmethod edge cannot be read: {error}"],
            "correctness_checks": None,
            "artifact_count": 0,
        }
    return validate_edge_bytes(compressed, observed_artifacts)


def synthetic_edge() -> tuple[
    dict[str, Any], bytes, scanner.EdgePins, dict[str, dict[str, Any]]
]:
    categories = {f"cmethod-synthetic-{index:02d}": 1 for index in range(48)}
    categories["cmethod-synthetic-48"] = EDGE_CHECK_COUNT - 48
    rows = [
        {
            "role": role,
            "path": scanner.relative(ARTIFACT_PATHS[role]),
            "sha256": PINNED_ARTIFACT_HASHES[role],
        }
        for role in ARTIFACT_PATHS
    ]
    observed = {
        row["role"]: {
            "role": row["role"],
            "path": row["path"],
            "sha256": row["sha256"],
            "expected_sha256": row["sha256"],
            "matches_frozen_edge": True,
        }
        for row in rows
    }
    partitions = [
        {
            "partition": f"cmethod-synthetic-{index}",
            "expected_sha256": hashlib.sha256(str(index).encode()).hexdigest(),
            "actual_sha256": hashlib.sha256(str(index).encode()).hexdigest(),
            "stride": 4099,
        }
        for index in range(4)
    ]
    document: dict[str, Any] = {
        "schema": "rebar-v7-independent-edge-oracle-v1",
        "module": "candidates.rust_candidate",
        "python": "3.14.6",
        "correctness_checks": EDGE_CHECK_COUNT,
        "failed": 0,
        "failures": [],
        "expected_sha256": "b" * 64,
        "actual_sha256": "b" * 64,
        "script_sha256": "c" * 64,
        "categories": categories,
        "candidate_artifacts": rows,
        "embedded_frozen_oracles": [{"name": "cmethod-synthetic-frozen"}],
        "independent_source_seeds": {"cmethod-synthetic": 1},
        "json_normalization": {"cmethod-synthetic": "canonical"},
        "membership_partitions": partitions,
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }
    compressed = gzip.compress(
        json.dumps(document, sort_keys=True, separators=(",", ":")).encode(),
        mtime=0,
    )
    pins = scanner.EdgePins(
        compressed_sha256=hashlib.sha256(compressed).hexdigest(),
        result_sha256="b" * 64,
        script_sha256="c" * 64,
        component_sha256={
            name: scanner.canonical_sha256(document[name])
            for name in EDGE_PINS.component_sha256
        },
    )
    return document, compressed, pins, observed


def scanner_control_issues(report: Any) -> list[str]:
    issues: list[str] = []
    if len(PINNED_SCANNER_CONTROL_NAMES) != EXPECTED_SCANNER_CONTROL_COUNT:
        return ["the independently pinned 49-control scanner manifest is inconsistent"]
    if not isinstance(report, dict):
        return ["the inherited Rust scanner control result is not an object"]
    checks = report.get("checks")
    if (
        report.get("passed") is not True
        or report.get("failed") != []
        or report.get("fixture_storage") != "in-memory only"
        or not isinstance(checks, list)
        or report.get("check_count") != EXPECTED_SCANNER_CONTROL_COUNT
        or len(checks) != EXPECTED_SCANNER_CONTROL_COUNT
    ):
        issues.append("the inherited Rust scanner did not pass all 49 in-memory controls")
    names: set[str] = set()
    if isinstance(checks, list):
        for item in checks:
            if (
                not isinstance(item, dict)
                or set(item) != {"name", "passed"}
                or not isinstance(item.get("name"), str)
                or item.get("passed") is not True
                or item["name"] in names
            ):
                issues.append("an inherited Rust scanner control was malformed or failed")
                break
            names.add(item["name"])
    if names != PINNED_SCANNER_CONTROL_NAMES:
        issues.append("the exact independently pinned 49 scanner control names changed")
    if report.get("upstream_control_issues") != []:
        issues.append("the inherited scanner reports upstream poison-control failures")
    issues.extend(scanner.validate_control_report(report.get("upstream_controls")))
    return issues


def variant_self_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    inherited = scanner.rust_self_test()
    inherited_issues = scanner_control_issues(inherited)
    controls = inherited.get("upstream_controls")
    upstream_issues = scanner.validate_control_report(controls)
    record("preserve_all_49_scanner_negative_controls", not inherited_issues)
    record("preserve_all_76_independently_isolated_shared_controls", not upstream_issues)

    document, compressed, pins, observed = synthetic_edge()
    clean = validate_edge_bytes(compressed, observed, pins)
    record("accept_complete_cmethod_in_memory_canonical_edge", clean["passed"])

    def reject_document(
        name: str,
        mutate: Callable[[dict[str, Any]], Any],
        marker: str,
    ) -> None:
        altered = copy.deepcopy(document)
        mutate(altered)
        result = validate_edge_document(altered, pins.compressed_sha256, observed, pins)
        record(
            name,
            not result["passed"]
            and any(marker in issue for issue in result["issues"]),
        )

    mutations: tuple[tuple[str, Callable[[dict[str, Any]], Any], str], ...] = (
        ("reject_cmethod_wrong_candidate_module", lambda x: x.__setitem__("module", "candidates.vm_candidate"), "module"),
        ("reject_cmethod_wrong_edge_schema", lambda x: x.__setitem__("schema", "untrusted-edge"), "schema"),
        ("reject_cmethod_wrong_frozen_python_version", lambda x: x.__setitem__("python", "3.13.0"), "python"),
        ("reject_cmethod_nonzero_edge_failures", lambda x: x.__setitem__("failed", 1), "failed"),
        ("reject_cmethod_missing_failure_count", lambda x: x.pop("failed"), "failed"),
        ("reject_cmethod_boolean_failure_count", lambda x: x.__setitem__("failed", False), "failed"),
        ("reject_cmethod_missing_failure_list", lambda x: x.pop("failures"), "failures"),
        ("reject_cmethod_nonempty_failure_list", lambda x: x.__setitem__("failures", [{"injected": True}]), "failures"),
        ("reject_cmethod_boolean_correctness_count", lambda x: x.__setitem__("correctness_checks", True), "correctness_checks"),
        ("reject_cmethod_missing_correctness_count", lambda x: x.pop("correctness_checks"), "correctness_checks"),
        ("reject_cmethod_changed_correctness_count", lambda x: x.__setitem__("correctness_checks", EDGE_CHECK_COUNT - 1), "correctness_checks"),
        ("reject_cmethod_changed_actual_result_digest", lambda x: x.__setitem__("actual_sha256", "d" * 64), "actual_sha256"),
        ("reject_cmethod_changed_expected_result_digest", lambda x: x.__setitem__("expected_sha256", "d" * 64), "expected_sha256"),
        ("reject_cmethod_changed_script_digest", lambda x: x.__setitem__("script_sha256", "d" * 64), "script_sha256"),
        ("reject_cmethod_changed_category_component", lambda x: x["categories"].__setitem__("cmethod-synthetic-00", 2), "categories"),
        ("reject_cmethod_missing_category", lambda x: x["categories"].pop("cmethod-synthetic-00"), "categories"),
        ("reject_cmethod_boolean_category_count", lambda x: x["categories"].__setitem__("cmethod-synthetic-00", True), "category"),
        ("reject_cmethod_negative_category_count", lambda x: x["categories"].__setitem__("cmethod-synthetic-00", -1), "category"),
        ("reject_cmethod_changed_frozen_oracles", lambda x: x["embedded_frozen_oracles"].append({"name": "foreign"}), "embedded_frozen_oracles"),
        ("reject_cmethod_changed_independent_seeds", lambda x: x["independent_source_seeds"].__setitem__("foreign", 1), "independent_source_seeds"),
        ("reject_cmethod_changed_json_normalization", lambda x: x["json_normalization"].__setitem__("foreign", True), "json_normalization"),
        ("reject_cmethod_missing_frozen_oracle_component", lambda x: x.pop("embedded_frozen_oracles"), "embedded_frozen_oracles"),
        ("reject_cmethod_missing_independent_seed_component", lambda x: x.pop("independent_source_seeds"), "independent_source_seeds"),
        ("reject_cmethod_missing_normalization_component", lambda x: x.pop("json_normalization"), "json_normalization"),
        ("reject_cmethod_changed_membership_digest", lambda x: x["membership_partitions"][0].__setitem__("actual_sha256", "e" * 64), "membership"),
        ("reject_cmethod_changed_membership_stride", lambda x: x["membership_partitions"][0].__setitem__("stride", 4098), "membership"),
        ("reject_cmethod_missing_membership_partition", lambda x: x["membership_partitions"].pop(), "membership"),
        ("reject_cmethod_missing_membership_component", lambda x: x.pop("membership_partitions"), "membership"),
        ("reject_cmethod_changed_holdout_declaration", lambda x: x.__setitem__("holdout", "ACCESSED"), "holdout"),
        ("reject_cmethod_changed_no_timing_declaration", lambda x: x.__setitem__("performance", "MEASURED"), "performance"),
        ("reject_cmethod_changed_frozen_artifact_path", lambda x: x["candidate_artifacts"][0].__setitem__("path", "candidates/unowned.py"), "path"),
        ("reject_cmethod_changed_frozen_artifact_digest", lambda x: x["candidate_artifacts"][0].__setitem__("sha256", "0" * 64), "digest"),
        ("reject_cmethod_duplicate_frozen_artifact_role", lambda x: x["candidate_artifacts"].__setitem__(1, copy.deepcopy(x["candidate_artifacts"][0])), "duplicated"),
        ("reject_cmethod_unapproved_frozen_artifact_role", lambda x: x["candidate_artifacts"][0].__setitem__("role", "foreign-native-engine"), "unapproved"),
        ("reject_cmethod_missing_frozen_artifact", lambda x: x["candidate_artifacts"].pop(), "exactly five"),
        ("reject_cmethod_malformed_frozen_artifact", lambda x: x["candidate_artifacts"][0].__setitem__("unexpected", True), "malformed"),
    )
    for name, mutate, marker in mutations:
        reject_document(name, mutate, marker)

    for role in ARTIFACT_PATHS:
        stale = copy.deepcopy(observed)
        stale[role]["sha256"] = "0" * 64
        stale[role]["matches_frozen_edge"] = False
        result = validate_edge_document(document, pins.compressed_sha256, stale, pins)
        record(
            "reject_cmethod_stale_live_" + role.replace("-", "_"),
            not result["passed"] and any(role in issue for issue in result["issues"]),
        )

    for role, old_digest in (
        ("native-bridge", "a1cf1384d20e20a8a744ead2a5952457d04c3a49d118ca87cd7977700d068073"),
        ("bridge-source", "6aca53810d44cea6321f1e229b71fb41c60742a51da75ca2243604a60468134f"),
    ):
        stale = copy.deepcopy(observed)
        stale[role]["sha256"] = old_digest
        stale[role]["matches_frozen_edge"] = False
        result = validate_edge_document(document, pins.compressed_sha256, stale, pins)
        record(
            "reject_previous_scanner_" + role.replace("-", "_"),
            old_digest != PINNED_ARTIFACT_HASHES[role]
            and not result["passed"]
            and any(role in issue for issue in result["issues"]),
        )

    altered_archive = bytearray(compressed)
    altered_archive[-1] ^= 1
    record(
        "reject_cmethod_changed_compressed_archive",
        not validate_edge_bytes(bytes(altered_archive), observed, pins)["passed"],
    )
    record(
        "reject_cmethod_truncated_compressed_archive",
        not validate_edge_bytes(compressed[:-1], observed, pins)["passed"],
    )
    bad_gzip = b"this is not an approved gzip stream"
    bad_pins = scanner.EdgePins(
        compressed_sha256=hashlib.sha256(bad_gzip).hexdigest(),
        result_sha256=pins.result_sha256,
        script_sha256=pins.script_sha256,
        component_sha256=pins.component_sha256,
    )
    record(
        "reject_cmethod_hash_matching_invalid_gzip",
        not validate_edge_bytes(bad_gzip, observed, bad_pins)["passed"],
    )
    invalid_json = gzip.compress(b"{not valid json", mtime=0)
    invalid_json_pins = scanner.EdgePins(
        compressed_sha256=hashlib.sha256(invalid_json).hexdigest(),
        result_sha256=pins.result_sha256,
        script_sha256=pins.script_sha256,
        component_sha256=pins.component_sha256,
    )
    record(
        "reject_cmethod_hash_matching_invalid_json",
        not validate_edge_bytes(invalid_json, observed, invalid_json_pins)["passed"],
    )
    record(
        "reject_cmethod_wrong_output_path",
        not scanner.authorized_path(
            ROOT / "candidates" / "audits" / "UNAUTHORIZED-CMETHOD.json",
            AUTHORIZED_OUTPUT,
        ),
    )
    record(
        "reject_cmethod_wrong_edge_path",
        not scanner.authorized_path(
            ROOT / "candidates" / "evidence" / "UNAUTHORIZED-CMETHOD.json.gz",
            DEFAULT_EDGE,
        ),
    )
    record(
        "reject_cmethod_previous_scanner_edge_path",
        not scanner.authorized_path(scanner.DEFAULT_EDGE, DEFAULT_EDGE),
    )
    record(
        "reject_cmethod_previous_scanner_output_path",
        not scanner.authorized_path(scanner.AUTHORIZED_OUTPUT, AUTHORIZED_OUTPUT),
    )
    record(
        "reject_cmethod_wrong_interpreter_version",
        bool(scanner.pinned_interpreter_issues((3, 13, 0), scanner.PINNED_INTERPRETER)),
    )
    record(
        "reject_cmethod_wrong_interpreter_executable",
        bool(scanner.pinned_interpreter_issues(scanner.PINNED_VERSION, Path("/tmp/untrusted-cpython"))),
    )

    python_fixtures = (
        ("reject_cmethod_stdlib_regex_import", "import re\n"),
        ("reject_cmethod_cpython_sre_import", "import _sre\n"),
        ("reject_cmethod_external_regex_package", "import regex\n"),
        ("reject_cmethod_cross_candidate_import", "from candidates import vm_candidate\n"),
        ("reject_cmethod_obfuscated_dynamic_import", "__import__(chr(114) + chr(101))\n"),
        ("reject_cmethod_importlib_indirection", "import importlib\nimportlib.import_module('re')\n"),
        ("reject_cmethod_environment_dispatch", "import os\nos.getenv('REGEX_ENGINE')\n"),
        ("reject_cmethod_environment_mapping", "import os\nos.environ['REGEX_ENGINE']\n"),
        ("reject_cmethod_external_process", "import subprocess\nsubprocess.run(['engine'])\n"),
        ("reject_cmethod_dynamic_evaluation", "eval('unowned_engine')\n"),
        ("reject_cmethod_unowned_ctypes_loader", "import ctypes\nctypes.CDLL('libforeign.so')\n"),
        ("reject_cmethod_indirect_builtin_loader", "__builtins__['__import__']('re')\n"),
    )
    for name, source in python_fixtures:
        result = shared.analyze_python(source, "rust", f"<cmethod-synthetic:{name}>")
        record(name, not result["passed"])

    native_fixtures = (
        ("reject_cmethod_native_pcre_engine", "pcre2_match(pattern, text);", "candidates/rust/py_bridge.c"),
        ("reject_cmethod_native_dynamic_loader", 'dlopen("libhidden_engine.so", 1);', "candidates/rust/py_bridge.c"),
        ("reject_cmethod_native_cpython_regex", 'PyImport_ImportModule("re");', "candidates/rust/py_bridge.c"),
        ("reject_cmethod_native_unowned_extern", "extern int innocent_engine_match(void);", "candidates/rust/py_bridge.c"),
        ("reject_cmethod_native_hidden_header", '#include "foreign_engine.h"\n', "candidates/rust/py_bridge.c"),
        ("reject_cmethod_external_rust_crate", "extern crate regex;\n", "candidates/rust/src/lib.rs"),
        ("reject_cmethod_external_rust_use", "use regex::Regex;\n", "candidates/rust/src/lib.rs"),
        ("reject_cmethod_unowned_rust_extern", 'unsafe extern "C" { fn unowned_engine(); }\n', "candidates/rust/src/lib.rs"),
    )
    for name, source, source_path in native_fixtures:
        result = shared.analyze_native(source, source_path, "rust")
        record(name, not result["passed"])

    malicious_manifests = {
        "project": '[project]\nname="synthetic"\ndependencies=[]\n',
        "rust": (
            '[package]\nname="rebar-rust-continuation"\n'
            '[dependencies]\ninnocent={package="regex",version="1"}\n'
        ),
        "rust_lock": (
            'version=4\n[[package]]\nname="rebar-rust-continuation"\n'
            'dependencies=["regex"]\n[[package]]\nname="regex"\nversion="1"\n'
        ),
    }
    record(
        "reject_cmethod_renamed_transitive_cargo_engine",
        not shared.analyze_manifests(malicious_manifests)["passed"],
    )

    clean_engine = shared.synthetic_elf(
        exported=tuple(sorted(shared.RUST_REQUIRED_EXPORTS)),
        needed=("libc.so.6",),
    )
    clean_bridge = shared.synthetic_elf(
        undefined=("rebar_compile", "rebar_match"),
        exported=("PyInit__rust_bridge",),
        needed=("_rust_engine.so",),
        runpaths=("$ORIGIN",),
    )
    clean_elf = shared.analyze_rust_binaries(
        {"engine": clean_engine, "bridge": clean_bridge}
    )
    record("accept_cmethod_owned_in_memory_rust_elf", clean_elf["passed"])

    def reject_bridge(name: str, bridge: bytes, marker: str) -> None:
        result = shared.analyze_rust_binaries(
            {"engine": clean_engine, "bridge": bridge}
        )
        record(
            name,
            not result["passed"]
            and any(issue.get("code") == marker for issue in result["issues"]),
        )

    reject_bridge(
        "reject_cmethod_elf_compiler_bypass",
        shared.synthetic_elf(
            undefined=("rebar_match",),
            exported=("PyInit__rust_bridge",),
            needed=("_rust_engine.so",),
        ),
        "bridge_bypasses_owned_compiler",
    )
    reject_bridge(
        "reject_cmethod_elf_executor_bypass",
        shared.synthetic_elf(
            undefined=("rebar_compile",),
            exported=("PyInit__rust_bridge",),
            needed=("_rust_engine.so",),
        ),
        "bridge_bypasses_owned_executor",
    )
    reject_bridge(
        "reject_cmethod_elf_cross_candidate_link",
        shared.synthetic_elf(
            undefined=("rebar_compile", "rebar_match"),
            exported=("PyInit__rust_bridge",),
            needed=("_zig_probe.so",),
        ),
        "cross_candidate_native_dependency",
    )
    reject_bridge(
        "reject_cmethod_elf_external_regex_link",
        shared.synthetic_elf(
            undefined=("rebar_compile", "rebar_match"),
            exported=("PyInit__rust_bridge",),
            needed=("_rust_engine.so", "libpcre2-8.so.0"),
        ),
        "external_regex_native_dependency",
    )
    reject_bridge(
        "reject_cmethod_elf_untrusted_runpath",
        shared.synthetic_elf(
            undefined=("rebar_compile", "rebar_match"),
            exported=("PyInit__rust_bridge",),
            needed=("_rust_engine.so",),
            runpaths=("/tmp/untrusted-engine",),
        ),
        "untrusted_native_runpath",
    )
    reject_bridge(
        "reject_cmethod_elf_wrong_bridge_initializer",
        shared.synthetic_elf(
            undefined=("rebar_compile", "rebar_match"),
            exported=("PyInit__foreign_bridge",),
            needed=("_rust_engine.so",),
        ),
        "missing_rust_bridge_initializer",
    )
    reject_bridge(
        "reject_cmethod_elf_unresolved_owned_symbol",
        shared.synthetic_elf(
            undefined=("rebar_compile", "rebar_match", "rebar_unowned_symbol"),
            exported=("PyInit__rust_bridge",),
            needed=("_rust_engine.so",),
        ),
        "unresolved_owned_engine_symbols",
    )
    invalid_elf = shared.analyze_rust_binaries(
        {"engine": b"not an ELF", "bridge": clean_bridge}
    )
    record(
        "reject_cmethod_invalid_owned_engine_elf",
        not invalid_elf["passed"]
        and any(
            issue.get("code") == "invalid_or_unverifiable_elf"
            for issue in invalid_elf["issues"]
        ),
    )

    def mapping(path: Path | str) -> str:
        return f"00400000-00401000 r-xp 00000000 00:00 0 {path}\n"

    rust_mappings = (
        mapping(shared.NATIVE_BINARIES["rust"]["engine"])
        + mapping(shared.NATIVE_BINARIES["rust"]["bridge"])
    )
    record(
        "accept_cmethod_exact_owned_synthetic_mappings",
        shared.classify_mapping_snapshot(rust_mappings, "rust")["passed"],
    )
    mapping_fixtures = (
        (
            "reject_cmethod_cross_candidate_memory_mapping",
            rust_mappings + mapping(ROOT / "candidates" / "_zig_probe.so"),
        ),
        (
            "reject_cmethod_external_regex_memory_mapping",
            rust_mappings + mapping("/usr/lib/libpcre2-8.so.0"),
        ),
        (
            "reject_cmethod_unapproved_candidate_memory_mapping",
            rust_mappings + mapping(ROOT / "candidates" / "_foreign_engine.so"),
        ),
        (
            "reject_cmethod_deleted_engine_memory_mapping",
            mapping(str(shared.NATIVE_BINARIES["rust"]["engine"]) + " (deleted)")
            + mapping(shared.NATIVE_BINARIES["rust"]["bridge"]),
        ),
        (
            "reject_cmethod_missing_engine_memory_mapping",
            mapping(shared.NATIVE_BINARIES["rust"]["bridge"]),
        ),
        (
            "reject_cmethod_missing_bridge_memory_mapping",
            mapping(shared.NATIVE_BINARIES["rust"]["engine"]),
        ),
    )
    for name, maps_text in mapping_fixtures:
        record(name, not shared.classify_mapping_snapshot(maps_text, "rust")["passed"])

    if not upstream_issues and isinstance(controls, dict):
        control_mutations: tuple[
            tuple[str, Callable[[dict[str, Any]], Any]], ...
        ] = (
            ("reject_cmethod_corrupted_upstream_control_count", lambda x: x.__setitem__("check_count", EXPECTED_UPSTREAM_CONTROL_COUNT - 1)),
            ("reject_cmethod_corrupted_upstream_control_name", lambda x: x["checks"][0].__setitem__("name", "untrusted-control")),
            ("reject_cmethod_bypassed_upstream_control", lambda x: x["checks"][0].__setitem__("passed", False)),
            ("reject_cmethod_unisolated_upstream_controls", lambda x: x["execution"].__setitem__("isolated_subprocess", False)),
            ("reject_cmethod_unvalidated_upstream_controls", lambda x: x["execution"].__setitem__("validated", False)),
            ("reject_cmethod_nonmemory_upstream_fixtures", lambda x: x.__setitem__("fixture_storage", "disk")),
            ("reject_cmethod_failed_upstream_report", lambda x: x.__setitem__("passed", False)),
        )
        for name, mutate in control_mutations:
            altered = copy.deepcopy(controls)
            mutate(altered)
            record(name, bool(scanner.validate_control_report(altered)))
    else:
        for name in (
            "reject_cmethod_corrupted_upstream_control_count",
            "reject_cmethod_corrupted_upstream_control_name",
            "reject_cmethod_bypassed_upstream_control",
            "reject_cmethod_unisolated_upstream_controls",
            "reject_cmethod_unvalidated_upstream_controls",
            "reject_cmethod_nonmemory_upstream_fixtures",
            "reject_cmethod_failed_upstream_report",
        ):
            record(name, False)

    if not inherited_issues:
        inherited_mutations: tuple[
            tuple[str, Callable[[dict[str, Any]], Any]], ...
        ] = (
            ("reject_cmethod_corrupted_scanner_control_count", lambda x: x.__setitem__("check_count", EXPECTED_SCANNER_CONTROL_COUNT - 1)),
            ("reject_cmethod_corrupted_scanner_control_name", lambda x: x["checks"][0].__setitem__("name", "foreign-scanner-control")),
            ("reject_cmethod_bypassed_scanner_control", lambda x: x["checks"][0].__setitem__("passed", False)),
            ("reject_cmethod_nonmemory_scanner_fixtures", lambda x: x.__setitem__("fixture_storage", "disk")),
        )
        for name, mutate in inherited_mutations:
            altered = copy.deepcopy(inherited)
            mutate(altered)
            record(name, bool(scanner_control_issues(altered)))
    else:
        for name in (
            "reject_cmethod_corrupted_scanner_control_count",
            "reject_cmethod_corrupted_scanner_control_name",
            "reject_cmethod_bypassed_scanner_control",
            "reject_cmethod_nonmemory_scanner_fixtures",
        ):
            record(name, False)

    names = [item["name"] for item in checks]
    negative_count = sum(name.startswith("reject_") for name in names)
    failed = [item["name"] for item in checks if not item["passed"]]
    if len(names) != len(set(names)):
        failed.append("duplicate_cmethod_self_test_name")
    if negative_count < MINIMUM_VARIANT_NEGATIVE_CONTROLS:
        failed.append("insufficient_independent_cmethod_negative_controls")
    return {
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "negative_control_count": negative_count,
        "minimum_negative_control_count": MINIMUM_VARIANT_NEGATIVE_CONTROLS,
        "failed": failed,
        "fixture_storage": "in-memory only",
        "inherited_scanner_controls": inherited,
        "inherited_scanner_control_issues": inherited_issues,
        "upstream_controls": controls,
        "upstream_control_issues": upstream_issues,
    }


def isolated_variant_self_test() -> dict[str, Any]:
    command = [
        sys.executable,
        "-I",
        "-B",
        str(Path(__file__).resolve()),
        "--self-test",
    ]

    def reject(reason: str) -> dict[str, Any]:
        return {
            "passed": False,
            "checks": [],
            "check_count": 0,
            "negative_control_count": 0,
            "minimum_negative_control_count": MINIMUM_VARIANT_NEGATIVE_CONTROLS,
            "failed": [reason],
            "fixture_storage": "in-memory only",
            "inherited_scanner_controls": {"passed": False, "check_count": 0},
            "inherited_scanner_control_issues": [reason],
            "upstream_controls": {"passed": False, "check_count": 0},
            "upstream_control_issues": [reason],
            "execution": {"isolated_subprocess": True, "validated": False},
        }

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return reject(f"isolated cmethod controls could not execute: {error}")
    stdout_size = len(process.stdout.encode("utf-8"))
    stderr_size = len(process.stderr.encode("utf-8"))
    if (
        stdout_size > shared.MAX_WORKER_RESPONSE_BYTES
        or stderr_size > shared.MAX_WORKER_RESPONSE_BYTES
    ):
        return reject("the isolated cmethod control response exceeds its hard bound")
    if process.returncode != 0 or process.stderr:
        return reject("the isolated cmethod controls did not terminate cleanly")
    lines = process.stdout.splitlines()
    if len(lines) != 1:
        return reject("the isolated cmethod controls must emit exactly one JSON line")
    try:
        result = json.loads(lines[0])
    except (TypeError, json.JSONDecodeError) as error:
        return reject(f"invalid isolated cmethod control JSON: {error}")
    if not isinstance(result, dict):
        return reject("the isolated cmethod control response is not an object")
    checks = result.get("checks")
    if (
        result.get("passed") is not True
        or result.get("failed") != []
        or result.get("fixture_storage") != "in-memory only"
        or not isinstance(checks, list)
        or result.get("check_count") != len(checks)
        or result.get("negative_control_count", 0) < MINIMUM_VARIANT_NEGATIVE_CONTROLS
        or result.get("minimum_negative_control_count")
        != MINIMUM_VARIANT_NEGATIVE_CONTROLS
    ):
        return reject("isolated cmethod controls failed or their exact schema is invalid")
    names: set[str] = set()
    for item in checks:
        if (
            not isinstance(item, dict)
            or set(item) != {"name", "passed"}
            or not isinstance(item.get("name"), str)
            or item.get("passed") is not True
            or item["name"] in names
        ):
            return reject("an isolated cmethod negative control is invalid or duplicated")
        names.add(item["name"])
    actual_negative_count = sum(name.startswith("reject_") for name in names)
    if actual_negative_count != result.get("negative_control_count"):
        return reject("the isolated cmethod negative-control count was misreported")
    inherited_issues = scanner_control_issues(result.get("inherited_scanner_controls"))
    if inherited_issues or result.get("inherited_scanner_control_issues") != []:
        return reject("the isolated cmethod gate did not preserve all 49 scanner controls")
    upstream_issues = scanner.validate_control_report(result.get("upstream_controls"))
    if upstream_issues or result.get("upstream_control_issues") != []:
        return reject("the isolated cmethod gate did not preserve all 76 shared controls")
    result["execution"] = {
        "isolated_subprocess": True,
        "interpreter": sys.executable,
        "exit_code": process.returncode,
        "response_bytes": stdout_size,
        "maximum_response_bytes": shared.MAX_WORKER_RESPONSE_BYTES,
        "validated": True,
    }
    return result


def run_rust_variant_audit(edge_path: Path) -> dict[str, Any]:
    interpreter_issues = scanner.pinned_interpreter_issues()
    tests = isolated_variant_self_test()
    observed, artifact_issues = observe_artifacts()
    edge = load_edge_oracle(edge_path, observed)
    source_issues: list[str] = []

    python_path = shared.PYTHON_SOURCES["rust"]
    try:
        python_source = python_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        python_source = ""
        source_issues.append(f"owned Rust Python source is unreadable: {error}")
    python_result = shared.analyze_python(
        python_source, "rust", scanner.relative(python_path)
    )
    tree = python_result.pop("tree", None)

    native_source: dict[str, str] = {}
    native_results: list[dict[str, Any]] = []
    for path in shared.NATIVE_SOURCES["rust"]:
        key = scanner.relative(path)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            source_issues.append(f"owned Rust native source {key} is unreadable: {error}")
            native_results.append({"passed": False, "file": key, "issues": [str(error)]})
            continue
        native_source[key] = source
        result = shared.analyze_native(source, key, "rust")
        result["file"] = key
        result["sha256"] = hashlib.sha256(source.encode("utf-8")).hexdigest()
        native_results.append(result)

    pipeline = (
        shared.verify_pipeline("rust", tree, native_source)
        if tree is not None
        and all(
            scanner.relative(path) in native_source
            for path in shared.NATIVE_SOURCES["rust"]
        )
        else {
            "passed": False,
            "issues": ["the owned Rust parser, compiler, and executor are incomplete"],
        }
    )

    manifest_sources: dict[str, str] = {}
    for name, path in shared.MANIFESTS.items():
        try:
            manifest_sources[name] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            source_issues.append(f"owned manifest {scanner.relative(path)} is unreadable: {error}")
    manifests = (
        shared.analyze_manifests(manifest_sources)
        if set(manifest_sources) == set(shared.MANIFESTS)
        else {"passed": False, "issues": ["owned Rust manifests are incomplete"]}
    )

    binary_data: dict[str, bytes] = {}
    for role, path in shared.NATIVE_BINARIES["rust"].items():
        try:
            binary_data[role] = scanner.bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            source_issues.append(f"owned Rust {role} ELF is unreadable: {error}")
    elf = shared.analyze_rust_binaries(binary_data)
    runtime = (
        shared.isolated_probe("rust", elf["files"])
        if elf["passed"] and python_result["passed"] and pipeline["passed"]
        else {
            "passed": False,
            "skipped": "owned Rust source, compiler pipeline, or ELF provenance failed",
        }
    )
    mappings = runtime.get("native_mapping_provenance", {})
    inherited_issues = scanner_control_issues(tests.get("inherited_scanner_controls"))
    upstream_issues = scanner.validate_control_report(tests.get("upstream_controls"))

    passed = (
        not interpreter_issues
        and tests["passed"]
        and not inherited_issues
        and not upstream_issues
        and not artifact_issues
        and edge["passed"]
        and not source_issues
        and python_result["passed"]
        and len(native_results) == len(shared.NATIVE_SOURCES["rust"])
        and all(item["passed"] for item in native_results)
        and pipeline["passed"]
        and manifests["passed"]
        and elf["passed"]
        and runtime["passed"]
        and mappings.get("passed") is True
        and mappings.get("expected_owned_mapping_count") == 2
        and mappings.get("observed_owned_mapping_count") == 2
    )
    return {
        "schema_version": 1,
        "audit": "rust-v8-cmethod-from-scratch-provenance",
        "module": "candidates.rust_candidate",
        "passed": bool(passed),
        "result": "PASS" if passed else "FAIL",
        "pinned_interpreter": {
            "expected_version": list(scanner.PINNED_VERSION),
            "actual_version": list(sys.version_info[:3]),
            "expected_executable": str(scanner.PINNED_INTERPRETER),
            "actual_executable": sys.executable,
            "passed": not interpreter_issues,
            "issues": interpreter_issues,
        },
        "edge_oracle": edge,
        "frozen_live_artifacts": {
            "passed": not artifact_issues,
            "expected_count": len(ARTIFACT_PATHS),
            "observed_count": len(observed),
            "artifacts": [observed[key] for key in sorted(observed)],
            "issues": artifact_issues,
        },
        "python_source": {
            "file": scanner.relative(python_path),
            "sha256": hashlib.sha256(python_source.encode("utf-8")).hexdigest(),
            **python_result,
        },
        "native_sources": native_results,
        "owned_pipeline": pipeline,
        "manifest_provenance": manifests,
        "rust_native_elf_provenance": elf,
        "isolated_runtime": runtime,
        "runtime_native_mapping_provenance": mappings,
        "self_test": tests,
        "inherited_scanner_poison_controls": {
            "passed": not inherited_issues,
            "expected_count": EXPECTED_SCANNER_CONTROL_COUNT,
            "validated_count": tests.get(
                "inherited_scanner_controls", {}
            ).get("check_count", 0),
            "issues": inherited_issues,
        },
        "upstream_poison_controls": {
            "passed": not upstream_issues,
            "expected_count": EXPECTED_UPSTREAM_CONTROL_COUNT,
            "validated_count": tests.get("upstream_controls", {}).get("check_count", 0),
            "issues": upstream_issues,
        },
        "input_issues": source_issues,
        "scope": {
            "family": "rust only",
            "variant": "scanner-cmethod",
            "other_candidate_production_sources_read": False,
            "other_candidate_native_binaries_read": False,
            "native_elf_paths": [
                scanner.relative(path)
                for path in shared.NATIVE_BINARIES["rust"].values()
            ],
            "immutable_edge_oracle": scanner.relative(DEFAULT_EDGE),
            "benchmark_or_timing_executed": False,
            "holdout_accessed": False,
            "synthetic_malicious_fixtures": "in-memory only",
            "minimum_variant_negative_controls": MINIMUM_VARIANT_NEGATIVE_CONTROLS,
            "maximum_compressed_edge_bytes": MAX_EDGE_COMPRESSED_BYTES,
            "maximum_decompressed_edge_bytes": MAX_EDGE_JSON_BYTES,
        },
        "limitations": [
            "The immutable 223198-check cmethod edge is independently hash-validated; its cases are not regenerated or rerun by this provenance-only gate.",
            "The certificate applies only to the five independently pinned cmethod artifacts and the explicitly enumerated owned Rust source graph.",
            "The prior scanner-stage audit and report are imported or referenced read-only and are neither rewritten nor recertified against cmethod binaries.",
            "No additional deep-oracle result is certified without separately authorized immutable deep evidence.",
            "Static source, ELF, and actually mapped runtime provenance do not prove unexercised future execution paths.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run only isolated in-memory cmethod provenance poison controls",
    )
    parser.add_argument(
        "--edge-oracle",
        type=Path,
        default=DEFAULT_EDGE,
        help="the single independently frozen Rust cmethod edge oracle",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=AUTHORIZED_OUTPUT,
        help="the single authorized additive Rust cmethod provenance report",
    )
    args = parser.parse_args(argv)
    interpreter_issues = scanner.pinned_interpreter_issues()
    if interpreter_issues:
        print(json.dumps({
            "passed": False,
            "result": "FAIL",
            "issues": interpreter_issues,
        }, sort_keys=True))
        return 1
    if not scanner.authorized_path(args.output, AUTHORIZED_OUTPUT):
        parser.error("only candidates/audits/RUST-V8-CMETHOD-FROM-SCRATCH.json is authorized")
    if not scanner.authorized_path(args.edge_oracle, DEFAULT_EDGE):
        parser.error("only the frozen rust-scanner-cmethod edge oracle is authorized")
    if args.self_test:
        report = variant_self_test()
        print(json.dumps(report, sort_keys=True))
        return 0 if report["passed"] else 1

    report = run_rust_variant_audit(args.edge_oracle)
    if report["passed"]:
        AUTHORIZED_OUTPUT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    summary: dict[str, Any] = {
        "passed": report["passed"],
        "result": report["result"],
        "module": report["module"],
        "correctness_checks": report["edge_oracle"].get("correctness_checks"),
        "edge_failed": report["edge_oracle"].get("failed"),
        "edge_oracle_passed": report["edge_oracle"]["passed"],
        "artifact_count": report["frozen_live_artifacts"]["observed_count"],
        "artifacts_passed": report["frozen_live_artifacts"]["passed"],
        "source_passed": report["python_source"]["passed"],
        "native_sources_passed": all(
            item["passed"] for item in report["native_sources"]
        ),
        "pipeline_passed": report["owned_pipeline"]["passed"],
        "manifest_passed": report["manifest_provenance"]["passed"],
        "rust_native_elf_passed": report["rust_native_elf_provenance"]["passed"],
        "rust_actual_mappings_passed": report[
            "runtime_native_mapping_provenance"
        ].get("passed", False),
        "isolated_runtime_passed": report["isolated_runtime"]["passed"],
        "variant_self_test_checks": report["self_test"]["check_count"],
        "variant_negative_controls": report["self_test"]["negative_control_count"],
        "inherited_scanner_controls": report[
            "inherited_scanner_poison_controls"
        ]["validated_count"],
        "upstream_poison_controls": report[
            "upstream_poison_controls"
        ]["validated_count"],
        "report": scanner.relative(AUTHORIZED_OUTPUT),
    }
    if not report["passed"]:
        summary["issues"] = (
            report["pinned_interpreter"]["issues"]
            + report["edge_oracle"]["issues"]
            + report["frozen_live_artifacts"]["issues"]
            + report["inherited_scanner_poison_controls"]["issues"]
            + report["upstream_poison_controls"]["issues"]
            + report["input_issues"]
            + report["self_test"].get("failed", [])
        )
    print(json.dumps(summary, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
