#!/usr/bin/env python3
"""Bounded, fail-closed provenance gate for the Rust scanner family only."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import audit_from_scratch as shared


PINNED_VERSION = (3, 14, 6)
PINNED_INTERPRETER = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
DEFAULT_EDGE = (
    ROOT / "candidates" / "evidence"
    / "rust-v8-edge-oracle-rust-scanner-lifetimes.json.gz"
)
AUTHORIZED_OUTPUT = (
    ROOT / "candidates" / "audits" / "RUST-V8-SCANNER-FROM-SCRATCH.json"
)
MAX_EDGE_COMPRESSED_BYTES = 16 * 1024 * 1024
MAX_EDGE_JSON_BYTES = 32 * 1024 * 1024
EDGE_CHECK_COUNT = 223198
EDGE_CATEGORY_COUNT = 49
EXPECTED_UPSTREAM_CONTROL_COUNT = 76
PINNED_UPSTREAM_CONTROL_NAMES = frozenset({
    "direct_stdlib_re",
    "direct_cpython_sre",
    "third_party_regex",
    "aliased_regex",
    "cross_candidate",
    "cross_candidate_dotted",
    "dynamic_import",
    "chr_obfuscated_import",
    "join_obfuscated_import",
    "importlib_indirection",
    "builtins_subscript",
    "getattr_indirection",
    "foreign_ctypes",
    "unowned_zig_library",
    "zig_owned_path_reassignment",
    "environment_dispatch",
    "environment_mapping",
    "external_process",
    "dynamic_eval",
    "dynamic_exec",
    "benchmark_clock",
    "holdout_path",
    "benchmark_file",
    "unowned_vm_configuration",
    "native_posix_regex",
    "native_pcre",
    "native_cpython_import",
    "native_copyreg_unowned_family",
    "native_copyreg_near_miss",
    "native_dynamic_loader",
    "native_hidden_header",
    "native_hidden_extern",
    "rust_external_crate",
    "rust_environment",
    "rust_hidden_extern",
    "zig_external_package",
    "zig_hidden_extern",
    "zig_c_import",
    "native_benchmark_clock",
    "ignore_native_comments_and_display_literals",
    "allow_owned_rust_generic_object_copy_protocol_only",
    "preserve_rust_lifetimes_and_owned_pipeline",
    "parse_in_memory_owned_elf",
    "reject_excessive_elf_section_count",
    "reject_excessive_elf_symbol_string",
    "reject_in_memory_external_elf_dependency",
    "reject_bridge_without_owned_elf_link",
    "reject_disguised_third_party_elf_dependency",
    "accept_five_owned_synthetic_elf_binaries_and_python_api_symbols",
    "reject_vm_disguised_external_engine",
    "reject_vm_external_regex_symbol",
    "reject_vm_cross_candidate_engine_symbol",
    "reject_vm_untrusted_runpath",
    "reject_vm_wrong_module_initializer",
    "reject_zig_engine_disguised_external_dependency",
    "reject_zig_bridge_disguised_external_dependency",
    "reject_zig_bridge_wrong_linked_rust_engine",
    "reject_zig_bridge_wrong_engine_cross_candidate",
    "reject_zig_bridge_compiler_bypass",
    "reject_zig_bridge_executor_bypass",
    "reject_zig_bridge_unresolved_owned_symbols",
    "reject_zig_engine_untrusted_runpath",
    "reject_zig_bridge_untrusted_runpath",
    "reject_zig_rust_cross_candidate_symbol",
    "reject_rust_zig_cross_candidate_symbol",
    "reject_rust_bridge_untrusted_runpath",
    "accept_exact_ast_owned_memory_mappings",
    "accept_exact_vm_owned_memory_mappings",
    "accept_exact_rust_owned_memory_mappings",
    "accept_exact_zig_owned_memory_mappings",
    "reject_cross_candidate_actual_memory_mapping",
    "reject_external_regex_actual_memory_mapping",
    "reject_unapproved_candidate_actual_memory_mapping",
    "reject_deleted_owned_native_memory_mapping",
    "reject_invalid_elf",
    "reject_renamed_and_transitive_cargo_dependency",
})

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
    "public-python": "1111a419d65d44775d1f4b0cb6a728dea8de44a592597341596533351c16018e",
    "native-bridge": "a1cf1384d20e20a8a744ead2a5952457d04c3a49d118ca87cd7977700d068073",
    "native-engine": "890f9e34e966244067a3dc173c2276043ae15d4830a05228fb37ec2571aa17cd",
    "native-source": "a2fa04912bb1f6957f833560446f4d3d1c5d13df8b5efac992fa63e28803668b",
    "bridge-source": "6aca53810d44cea6321f1e229b71fb41c60742a51da75ca2243604a60468134f",
}


@dataclass(frozen=True)
class EdgePins:
    compressed_sha256: str
    result_sha256: str
    script_sha256: str
    component_sha256: dict[str, str]


EDGE_PINS = EdgePins(
    compressed_sha256=(
        "113fd5cae48a4e808d782259bbc116b47a8eee68f22afa8b5cd74f77803dc288"
    ),
    result_sha256=(
        "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
    ),
    script_sha256=(
        "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
    ),
    component_sha256={
        "candidate_artifacts": (
            "6ebdbf3ff482da3fd2ca58981b8acfcc5d77d65ca249a2e5b33171378ea58fd5"
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


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def pinned_interpreter_issues(
    version: tuple[int, int, int] | None = None,
    executable: Path | None = None,
) -> list[str]:
    actual_version = version if version is not None else tuple(sys.version_info[:3])
    actual_executable = executable if executable is not None else Path(sys.executable)
    issues: list[str] = []
    if actual_version != PINNED_VERSION:
        issues.append(
            f"expected CPython {PINNED_VERSION!r}, received {actual_version!r}"
        )
    if actual_executable.resolve() != PINNED_INTERPRETER.resolve():
        issues.append("the current interpreter is not the exact pinned CPython executable")
    return issues


def authorized_path(path: Path, expected: Path) -> bool:
    try:
        return path.resolve() == expected.resolve()
    except (OSError, RuntimeError):
        return False


def validate_control_report(report: Any) -> list[str]:
    issues: list[str] = []
    if len(PINNED_UPSTREAM_CONTROL_NAMES) != EXPECTED_UPSTREAM_CONTROL_COUNT:
        return ["the Rust gate's independently pinned control manifest is inconsistent"]
    if (
        shared.EXPECTED_SELF_TEST_CHECKS != EXPECTED_UPSTREAM_CONTROL_COUNT
        or shared.EXPECTED_SELF_TEST_NAMES != PINNED_UPSTREAM_CONTROL_NAMES
    ):
        issues.append("the shared auditor's exact pinned poison-control manifest changed")
    if not isinstance(report, dict):
        return issues + ["the isolated poison-control report is not an object"]
    checks = report.get("checks")
    if report.get("passed") is not True:
        issues.append("the isolated poison-control report failed")
    if report.get("failed") != []:
        issues.append("the isolated poison-control report contains failures")
    if report.get("fixture_storage") != "in-memory only":
        issues.append("the poison controls are not certified as in-memory-only")
    if (
        not isinstance(checks, list)
        or report.get("check_count") != EXPECTED_UPSTREAM_CONTROL_COUNT
        or len(checks) != EXPECTED_UPSTREAM_CONTROL_COUNT
    ):
        return issues + ["the isolated report did not execute all 76 controls"]
    names: set[str] = set()
    for item in checks:
        if (
            not isinstance(item, dict)
            or set(item) != {"name", "passed"}
            or not isinstance(item.get("name"), str)
            or item.get("passed") is not True
            or item["name"] in names
        ):
            issues.append("an isolated poison control is malformed, duplicated, or failing")
            break
        names.add(item["name"])
    if names != PINNED_UPSTREAM_CONTROL_NAMES:
        issues.append("the exact set of 76 isolated poison-control names changed")
    execution = report.get("execution")
    if (
        not isinstance(execution, dict)
        or execution.get("isolated_subprocess") is not True
        or execution.get("validated") is not True
        or execution.get("validated_check_count") != EXPECTED_UPSTREAM_CONTROL_COUNT
        or execution.get("exit_code") != 0
    ):
        issues.append("the 76 controls were not independently validated in a clean subprocess")
    return issues


def bounded_binary(path: Path, limit: int) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"{relative(path)} exceeds its {limit}-byte audit limit")
    return data


def observe_artifacts() -> tuple[dict[str, dict[str, Any]], list[str]]:
    observed: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for role, path in ARTIFACT_PATHS.items():
        try:
            data = bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            issues.append(f"unreadable Rust {role}: {error}")
            continue
        actual = hashlib.sha256(data).hexdigest()
        expected = PINNED_ARTIFACT_HASHES[role]
        matches = actual == expected
        if not matches:
            issues.append(
                f"Rust {role} hash does not match the independently frozen edge artifact"
            )
        observed[role] = {
            "role": role,
            "path": relative(path),
            "sha256": actual,
            "expected_sha256": expected,
            "matches_frozen_edge": matches,
        }
    if set(observed) != set(ARTIFACT_PATHS):
        issues.append("the Rust family does not expose exactly five required edge artifacts")
    return observed, issues


def validate_edge_document(
    document: Any,
    compressed_sha256: str,
    observed_artifacts: dict[str, dict[str, Any]],
    pins: EdgePins = EDGE_PINS,
) -> dict[str, Any]:
    issues: list[str] = []
    if compressed_sha256 != pins.compressed_sha256:
        issues.append("the compressed immutable edge-oracle SHA-256 does not match")
    if not isinstance(document, dict):
        return {
            "passed": False,
            "issues": issues + ["the canonical edge-oracle JSON must be an object"],
            "archive_sha256": compressed_sha256,
            "correctness_checks": None,
            "artifact_count": 0,
        }
    required = {
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
            issues.append(f"canonical edge field {key!r} does not match its frozen value")
    if document.get("failures") != []:
        issues.append("the canonical edge oracle has nonempty or malformed failures")

    categories = document.get("categories")
    if not isinstance(categories, dict) or len(categories) != EDGE_CATEGORY_COUNT:
        issues.append("the canonical edge oracle does not contain exactly 49 categories")
    elif any(type(count) is not int or count < 0 for count in categories.values()):
        issues.append("a canonical edge category count is malformed")
    elif sum(categories.values()) != EDGE_CHECK_COUNT:
        issues.append("canonical edge category counts do not sum to 223198")

    component_hashes: dict[str, str] = {}
    for key, expected in pins.component_sha256.items():
        if key not in document:
            issues.append(f"the canonical edge component {key!r} is missing")
            continue
        try:
            actual = canonical_sha256(document[key])
        except (TypeError, ValueError, UnicodeError) as error:
            issues.append(f"the canonical edge component {key!r} is invalid: {error}")
            continue
        component_hashes[key] = actual
        if actual != expected:
            issues.append(f"the independently frozen {key!r} canonical digest changed")

    artifacts = document.get("candidate_artifacts")
    document_roles: set[str] = set()
    if not isinstance(artifacts, list) or len(artifacts) != len(ARTIFACT_PATHS):
        issues.append("the canonical edge must contain exactly five Rust artifacts")
    else:
        for item in artifacts:
            if not isinstance(item, dict) or set(item) != {"path", "role", "sha256"}:
                issues.append("a frozen Rust edge artifact has a malformed schema")
                continue
            role = item["role"]
            if role not in ARTIFACT_PATHS or role in document_roles:
                issues.append("a frozen Rust edge artifact role is unexpected or duplicated")
                continue
            document_roles.add(role)
            expected_path = relative(ARTIFACT_PATHS[role])
            expected_digest = PINNED_ARTIFACT_HASHES[role]
            if item["path"] != expected_path:
                issues.append(f"frozen Rust {role} artifact path changed")
            if item["sha256"] != expected_digest:
                issues.append(f"frozen Rust {role} artifact digest changed")
            observed = observed_artifacts.get(role)
            if (
                not isinstance(observed, dict)
                or observed.get("path") != expected_path
                or observed.get("sha256") != expected_digest
                or observed.get("matches_frozen_edge") is not True
            ):
                issues.append(f"live Rust {role} does not match the frozen edge artifact")
    if document_roles != set(ARTIFACT_PATHS):
        issues.append("the canonical edge artifact roles are incomplete")

    partitions = document.get("membership_partitions")
    if not isinstance(partitions, list) or len(partitions) != 4:
        issues.append("the canonical edge must contain exactly four membership partitions")
    else:
        for partition in partitions:
            if (
                not isinstance(partition, dict)
                or partition.get("actual_sha256") != partition.get("expected_sha256")
                or partition.get("stride") != 4099
            ):
                issues.append("a frozen membership partition has mismatched or malformed evidence")

    return {
        "passed": not issues,
        "issues": issues,
        "file": relative(DEFAULT_EDGE),
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
        "artifact_count": len(document_roles),
        "canonical_component_sha256": component_hashes,
        "holdout": document.get("holdout"),
        "performance": document.get("performance"),
    }


def validate_edge_bytes(
    compressed: bytes,
    observed_artifacts: dict[str, dict[str, Any]],
    pins: EdgePins = EDGE_PINS,
) -> dict[str, Any]:
    compressed_hash = hashlib.sha256(compressed).hexdigest()
    if len(compressed) > MAX_EDGE_COMPRESSED_BYTES:
        return {
            "passed": False,
            "issues": ["the compressed edge oracle exceeds its bounded audit limit"],
            "archive_sha256": compressed_hash,
            "correctness_checks": None,
            "artifact_count": 0,
        }
    if compressed_hash != pins.compressed_sha256:
        return {
            "passed": False,
            "issues": ["the compressed immutable edge-oracle SHA-256 does not match"],
            "archive_sha256": compressed_hash,
            "correctness_checks": None,
            "artifact_count": 0,
        }
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as archive:
            decoded = archive.read(MAX_EDGE_JSON_BYTES + 1)
        if len(decoded) > MAX_EDGE_JSON_BYTES:
            raise ValueError("the decompressed edge oracle exceeds its bounded audit limit")
        document = json.loads(decoded)
    except (EOFError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        return {
            "passed": False,
            "issues": [f"invalid bounded gzip or canonical edge JSON: {error}"],
            "archive_sha256": compressed_hash,
            "correctness_checks": None,
            "artifact_count": 0,
        }
    return validate_edge_document(document, compressed_hash, observed_artifacts, pins)


def load_edge_oracle(
    path: Path,
    observed_artifacts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if not authorized_path(path, DEFAULT_EDGE):
        return {
            "passed": False,
            "issues": ["only the explicitly authorized immutable Rust edge oracle may be read"],
            "correctness_checks": None,
            "artifact_count": 0,
        }
    try:
        compressed = bounded_binary(DEFAULT_EDGE, MAX_EDGE_COMPRESSED_BYTES)
    except (OSError, ValueError) as error:
        return {
            "passed": False,
            "issues": [f"the immutable Rust edge oracle is unreadable: {error}"],
            "correctness_checks": None,
            "artifact_count": 0,
        }
    return validate_edge_bytes(compressed, observed_artifacts)


def synthetic_edge() -> tuple[dict[str, Any], bytes, EdgePins, dict[str, dict[str, Any]]]:
    categories = {f"synthetic-{index:02d}": 1 for index in range(48)}
    categories["synthetic-48"] = EDGE_CHECK_COUNT - 48
    rows = [
        {
            "role": role,
            "path": relative(ARTIFACT_PATHS[role]),
            "sha256": PINNED_ARTIFACT_HASHES[role],
        }
        for role in ARTIFACT_PATHS
    ]
    observed = {
        item["role"]: {
            "role": item["role"],
            "path": item["path"],
            "sha256": item["sha256"],
            "expected_sha256": item["sha256"],
            "matches_frozen_edge": True,
        }
        for item in rows
    }
    partitions = [
        {
            "partition": f"synthetic-{index}",
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
        "embedded_frozen_oracles": [{"name": "synthetic-frozen"}],
        "membership_partitions": partitions,
        "independent_source_seeds": {"synthetic": 1},
        "json_normalization": {"synthetic": "canonical"},
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }
    compressed = gzip.compress(
        json.dumps(document, sort_keys=True, separators=(",", ":")).encode(),
        mtime=0,
    )
    pins = EdgePins(
        compressed_sha256=hashlib.sha256(compressed).hexdigest(),
        result_sha256="b" * 64,
        script_sha256="c" * 64,
        component_sha256={
            name: canonical_sha256(document[name])
            for name in EDGE_PINS.component_sha256
        },
    )
    return document, compressed, pins, observed


def rust_self_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    controls = shared.isolated_self_test()
    control_issues = validate_control_report(controls)
    record("all_76_isolated_shared_poison_controls", not control_issues)

    document, compressed, pins, observed = synthetic_edge()
    clean = validate_edge_bytes(compressed, observed, pins)
    record("accept_complete_in_memory_canonical_edge", clean["passed"])

    def reject_document(name: str, mutate: Any, marker: str) -> None:
        altered = copy.deepcopy(document)
        mutate(altered)
        result = validate_edge_document(altered, pins.compressed_sha256, observed, pins)
        record(name, not result["passed"] and any(marker in issue for issue in result["issues"]))

    reject_document(
        "reject_wrong_candidate_module",
        lambda item: item.__setitem__("module", "candidates.vm_candidate"),
        "module",
    )
    reject_document(
        "reject_wrong_canonical_edge_schema",
        lambda item: item.__setitem__("schema", "untrusted-edge"),
        "schema",
    )
    reject_document(
        "reject_nonzero_canonical_edge_failures",
        lambda item: item.__setitem__("failed", 1),
        "failed",
    )
    reject_document(
        "reject_missing_canonical_failure_list",
        lambda item: item.pop("failures"),
        "failures",
    )
    reject_document(
        "reject_malformed_canonical_check_count",
        lambda item: item.__setitem__("correctness_checks", True),
        "correctness_checks",
    )
    reject_document(
        "reject_missing_canonical_check_count",
        lambda item: item.pop("correctness_checks"),
        "correctness_checks",
    )
    reject_document(
        "reject_changed_canonical_check_count",
        lambda item: item.__setitem__("correctness_checks", EDGE_CHECK_COUNT - 1),
        "correctness_checks",
    )
    reject_document(
        "reject_changed_canonical_result_digest",
        lambda item: item.__setitem__("actual_sha256", "d" * 64),
        "actual_sha256",
    )
    reject_document(
        "reject_changed_canonical_expected_digest",
        lambda item: item.__setitem__("expected_sha256", "d" * 64),
        "expected_sha256",
    )
    reject_document(
        "reject_changed_frozen_edge_categories",
        lambda item: item["categories"].__setitem__("synthetic-00", 2),
        "categories",
    )
    reject_document(
        "reject_nonempty_edge_failure_list",
        lambda item: item.__setitem__("failures", [{"synthetic": True}]),
        "failures",
    )
    reject_document(
        "reject_changed_frozen_script_digest",
        lambda item: item.__setitem__("script_sha256", "d" * 64),
        "script_sha256",
    )
    reject_document(
        "reject_changed_frozen_oracle_component",
        lambda item: item["embedded_frozen_oracles"].append({"name": "foreign"}),
        "embedded_frozen_oracles",
    )
    reject_document(
        "reject_changed_membership_partition",
        lambda item: item["membership_partitions"][0].__setitem__("actual_sha256", "e" * 64),
        "membership",
    )
    reject_document(
        "reject_changed_holdout_declaration",
        lambda item: item.__setitem__("holdout", "ACCESSED"),
        "holdout",
    )
    reject_document(
        "reject_changed_no_timing_declaration",
        lambda item: item.__setitem__("performance", "MEASURED"),
        "performance",
    )

    stale_engine = copy.deepcopy(observed)
    stale_engine["native-engine"]["sha256"] = "0" * 64
    stale_engine["native-engine"]["matches_frozen_edge"] = False
    result = validate_edge_document(document, pins.compressed_sha256, stale_engine, pins)
    record(
        "reject_stale_native_engine",
        not result["passed"] and any("native-engine" in issue for issue in result["issues"]),
    )
    stale_bridge = copy.deepcopy(observed)
    stale_bridge["native-bridge"]["sha256"] = "0" * 64
    stale_bridge["native-bridge"]["matches_frozen_edge"] = False
    result = validate_edge_document(document, pins.compressed_sha256, stale_bridge, pins)
    record(
        "reject_stale_native_bridge",
        not result["passed"] and any("native-bridge" in issue for issue in result["issues"]),
    )
    stale_source = copy.deepcopy(observed)
    stale_source["bridge-source"]["sha256"] = "0" * 64
    stale_source["bridge-source"]["matches_frozen_edge"] = False
    result = validate_edge_document(document, pins.compressed_sha256, stale_source, pins)
    record(
        "reject_changed_live_bridge_source",
        not result["passed"] and any("bridge-source" in issue for issue in result["issues"]),
    )
    missing_artifact = copy.deepcopy(document)
    missing_artifact["candidate_artifacts"].pop()
    result = validate_edge_document(missing_artifact, pins.compressed_sha256, observed, pins)
    record("reject_missing_frozen_live_artifact", not result["passed"])
    duplicate_artifact = copy.deepcopy(document)
    duplicate_artifact["candidate_artifacts"][1] = copy.deepcopy(
        duplicate_artifact["candidate_artifacts"][0]
    )
    result = validate_edge_document(duplicate_artifact, pins.compressed_sha256, observed, pins)
    record("reject_duplicate_frozen_artifact_role", not result["passed"])

    altered_archive = bytearray(compressed)
    altered_archive[-1] ^= 1
    result = validate_edge_bytes(bytes(altered_archive), observed, pins)
    record("reject_changed_immutable_gzip_digest", not result["passed"])
    result = validate_edge_bytes(compressed[:-1], observed, pins)
    record("reject_truncated_immutable_gzip", not result["passed"])

    record(
        "reject_wrong_output_path",
        not authorized_path(ROOT / "candidates" / "audits" / "UNAUTHORIZED.json", AUTHORIZED_OUTPUT),
    )
    record(
        "reject_wrong_edge_oracle_path",
        not authorized_path(ROOT / "candidates" / "evidence" / "UNAUTHORIZED.json.gz", DEFAULT_EDGE),
    )
    record(
        "reject_wrong_python_version",
        bool(pinned_interpreter_issues((3, 13, 0), PINNED_INTERPRETER)),
    )

    python_fixtures = (
        ("reject_stdlib_re_import", "import re\n"),
        ("reject_cpython_sre_import", "import _sre\n"),
        ("reject_external_regex_package", "import regex\n"),
        ("reject_cross_candidate_module", "from candidates import vm_candidate\n"),
        ("reject_obfuscated_dynamic_import_bypass", "__import__(chr(114) + chr(101))\n"),
        ("reject_environment_engine_dispatch", "import os\nos.getenv('REGEX_ENGINE')\n"),
    )
    for name, source in python_fixtures:
        result = shared.analyze_python(source, "rust", f"<synthetic:{name}>")
        record(name, not result["passed"])

    native_fixtures = (
        ("reject_native_external_regex", "pcre2_match(pattern, text);"),
        ("reject_native_dynamic_engine", 'dlopen("libhidden_engine.so", 1);'),
        ("reject_native_cpython_engine", 'PyImport_ImportModule("re");'),
        ("reject_native_cross_engine_extern", "extern int innocent_engine_match(void);"),
    )
    for name, source in native_fixtures:
        result = shared.analyze_native(source, "candidates/rust/py_bridge.c", "rust")
        record(name, not result["passed"])

    malformed_manifests = {
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
    result = shared.analyze_manifests(malformed_manifests)
    record("reject_renamed_external_cargo_manifest", not result["passed"])

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
    record("accept_owned_in_memory_rust_elf_pipeline", clean_elf["passed"])
    bypass = shared.analyze_rust_binaries({
        "engine": clean_engine,
        "bridge": shared.synthetic_elf(
            undefined=("rebar_match",),
            exported=("PyInit__rust_bridge",),
            needed=("_rust_engine.so",),
        ),
    })
    record(
        "reject_native_bridge_compiler_bypass",
        not bypass["passed"] and any(
            issue["code"] == "bridge_bypasses_owned_compiler"
            for issue in bypass["issues"]
        ),
    )
    wrong_link = shared.analyze_rust_binaries({
        "engine": clean_engine,
        "bridge": shared.synthetic_elf(
            undefined=("rebar_compile", "rebar_match"),
            exported=("PyInit__rust_bridge",),
            needed=("_zig_probe.so",),
        ),
    })
    record(
        "reject_cross_family_native_bridge_link",
        not wrong_link["passed"] and any(
            issue["code"] == "cross_candidate_native_dependency"
            for issue in wrong_link["issues"]
        ),
    )

    def mapping(path: Path | str) -> str:
        return f"00400000-00401000 r-xp 00000000 00:00 0 {path}\n"

    correct_map = shared.classify_mapping_snapshot(
        mapping(shared.NATIVE_BINARIES["rust"]["engine"])
        + mapping(shared.NATIVE_BINARIES["rust"]["bridge"]),
        "rust",
    )
    record("accept_owned_in_memory_rust_mappings", correct_map["passed"])
    cross_map = shared.classify_mapping_snapshot(
        mapping(shared.NATIVE_BINARIES["rust"]["engine"])
        + mapping(shared.NATIVE_BINARIES["rust"]["bridge"])
        + mapping(shared.NATIVE_BINARIES["zig"]["engine"]),
        "rust",
    )
    record("reject_cross_family_native_memory_mapping", not cross_map["passed"])
    external_map = shared.classify_mapping_snapshot(
        mapping(shared.NATIVE_BINARIES["rust"]["engine"])
        + mapping(shared.NATIVE_BINARIES["rust"]["bridge"])
        + mapping("/usr/lib/libpcre2-8.so.0"),
        "rust",
    )
    record("reject_external_regex_memory_mapping", not external_map["passed"])

    if not control_issues:
        wrong_count = copy.deepcopy(controls)
        wrong_count["check_count"] -= 1
        record("reject_corrupted_upstream_poison_count", bool(validate_control_report(wrong_count)))
        wrong_names = copy.deepcopy(controls)
        wrong_names["checks"][0]["name"] = "untrusted-control"
        record("reject_corrupted_upstream_poison_names", bool(validate_control_report(wrong_names)))
        wrong_status = copy.deepcopy(controls)
        wrong_status["checks"][0]["passed"] = False
        record("reject_bypassed_upstream_poison_control", bool(validate_control_report(wrong_status)))
        wrong_execution = copy.deepcopy(controls)
        wrong_execution["execution"]["validated"] = False
        record("reject_unisolated_upstream_poison_execution", bool(validate_control_report(wrong_execution)))
    else:
        for name in (
            "reject_corrupted_upstream_poison_count",
            "reject_corrupted_upstream_poison_names",
            "reject_bypassed_upstream_poison_control",
            "reject_unisolated_upstream_poison_execution",
        ):
            record(name, False)

    failed = [item["name"] for item in checks if not item["passed"]]
    names = [item["name"] for item in checks]
    if len(names) != len(set(names)):
        failed.append("duplicate_rust_gate_self_test_name")
    return {
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "fixture_storage": "in-memory only",
        "upstream_controls": controls,
        "upstream_control_issues": control_issues,
    }


def isolated_rust_self_test() -> dict[str, Any]:
    command = [
        sys.executable,
        "-I",
        "-B",
        str(Path(__file__).resolve()),
        "--self-test",
    ]

    def rejected(reason: str) -> dict[str, Any]:
        return {
            "passed": False,
            "checks": [],
            "check_count": 0,
            "failed": [reason],
            "fixture_storage": "in-memory only",
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
        return rejected(f"isolated Rust self-test failed: {error}")
    if (
        len(process.stdout.encode("utf-8")) > shared.MAX_WORKER_RESPONSE_BYTES
        or len(process.stderr.encode("utf-8")) > shared.MAX_WORKER_RESPONSE_BYTES
    ):
        return rejected("the isolated Rust self-test exceeds its bounded output limit")
    if process.returncode != 0 or process.stderr:
        return rejected("the isolated Rust self-test did not complete cleanly")
    lines = process.stdout.splitlines()
    if len(lines) != 1:
        return rejected("the isolated Rust self-test must produce exactly one JSON line")
    try:
        result = json.loads(lines[0])
    except (TypeError, json.JSONDecodeError) as error:
        return rejected(f"invalid isolated Rust self-test JSON: {error}")
    if not isinstance(result, dict) or result.get("passed") is not True:
        return rejected("the isolated Rust poison controls failed")
    checks = result.get("checks")
    if (
        not isinstance(checks, list)
        or len(checks) != result.get("check_count")
        or not checks
        or result.get("failed") != []
        or result.get("fixture_storage") != "in-memory only"
    ):
        return rejected("the isolated Rust poison report has an invalid schema")
    names: set[str] = set()
    for item in checks:
        if (
            not isinstance(item, dict)
            or set(item) != {"name", "passed"}
            or not isinstance(item.get("name"), str)
            or item.get("passed") is not True
            or item["name"] in names
        ):
            return rejected("a Rust self-test is missing, duplicated, or failing")
        names.add(item["name"])
    control_issues = validate_control_report(result.get("upstream_controls"))
    if control_issues:
        return rejected("the isolated Rust self-test did not preserve all 76 shared controls")
    result["execution"] = {
        "isolated_subprocess": True,
        "interpreter": sys.executable,
        "exit_code": process.returncode,
        "response_bytes": len(process.stdout.encode("utf-8")),
        "maximum_response_bytes": shared.MAX_WORKER_RESPONSE_BYTES,
        "validated": True,
    }
    return result


def run_rust_audit(edge_path: Path) -> dict[str, Any]:
    interpreter_issues = pinned_interpreter_issues()
    tests = isolated_rust_self_test()
    observed, artifact_issues = observe_artifacts()
    edge = load_edge_oracle(edge_path, observed)

    python_path = shared.PYTHON_SOURCES["rust"]
    source_issues: list[str] = []
    try:
        python_source = python_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        python_source = ""
        source_issues.append(f"owned Rust Python source is unreadable: {error}")
    python_result = shared.analyze_python(
        python_source, "rust", relative(python_path)
    )
    tree = python_result.pop("tree", None)

    native_source: dict[str, str] = {}
    native_results: list[dict[str, Any]] = []
    for path in shared.NATIVE_SOURCES["rust"]:
        key = relative(path)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            source_issues.append(f"owned Rust native source {key} is unreadable: {error}")
            native_results.append({
                "passed": False,
                "file": key,
                "issues": [str(error)],
            })
            continue
        native_source[key] = source
        checked = shared.analyze_native(source, key, "rust")
        checked["file"] = key
        checked["sha256"] = hashlib.sha256(source.encode("utf-8")).hexdigest()
        native_results.append(checked)

    pipeline = (
        shared.verify_pipeline("rust", tree, native_source)
        if tree is not None
        and all(relative(path) in native_source for path in shared.NATIVE_SOURCES["rust"])
        else {
            "passed": False,
            "issues": ["owned Rust parser/compiler/executor pipeline is incomplete"],
        }
    )

    manifest_sources: dict[str, str] = {}
    for name, path in shared.MANIFESTS.items():
        try:
            manifest_sources[name] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            source_issues.append(f"owned manifest {relative(path)} is unreadable: {error}")
    manifests = (
        shared.analyze_manifests(manifest_sources)
        if set(manifest_sources) == set(shared.MANIFESTS)
        else {"passed": False, "issues": ["owned dependency manifests are incomplete"]}
    )

    binary_data: dict[str, bytes] = {}
    for role, path in shared.NATIVE_BINARIES["rust"].items():
        try:
            binary_data[role] = bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            source_issues.append(f"owned Rust {role} ELF is unreadable: {error}")
    elf = shared.analyze_rust_binaries(binary_data)
    runtime = (
        shared.isolated_probe("rust", elf["files"])
        if elf["passed"] and python_result["passed"] and pipeline["passed"]
        else {
            "passed": False,
            "skipped": "owned Rust source, pipeline, or ELF provenance failed",
        }
    )
    mappings = runtime.get("native_mapping_provenance", {})
    control_issues = validate_control_report(tests.get("upstream_controls"))
    passed = (
        not interpreter_issues
        and tests["passed"]
        and not control_issues
        and not artifact_issues
        and edge["passed"]
        and not source_issues
        and python_result["passed"]
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
        "audit": "rust-v8-scanner-from-scratch-provenance",
        "module": "candidates.rust_candidate",
        "passed": bool(passed),
        "result": "PASS" if passed else "FAIL",
        "pinned_interpreter": {
            "expected_version": list(PINNED_VERSION),
            "actual_version": list(sys.version_info[:3]),
            "expected_executable": str(PINNED_INTERPRETER),
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
            "file": relative(python_path),
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
        "upstream_poison_controls": {
            "passed": not control_issues,
            "expected_count": EXPECTED_UPSTREAM_CONTROL_COUNT,
            "validated_count": tests.get("upstream_controls", {}).get("check_count", 0),
            "issues": control_issues,
        },
        "input_issues": source_issues,
        "scope": {
            "family": "rust only",
            "other_candidate_production_sources_read": False,
            "other_candidate_native_binaries_read": False,
            "native_elf_paths": [
                relative(path)
                for path in shared.NATIVE_BINARIES["rust"].values()
            ],
            "immutable_edge_oracle": relative(DEFAULT_EDGE),
            "benchmark_or_timing_executed": False,
            "holdout_accessed": False,
            "synthetic_malicious_fixtures": "in-memory only",
            "maximum_compressed_edge_bytes": MAX_EDGE_COMPRESSED_BYTES,
            "maximum_decompressed_edge_bytes": MAX_EDGE_JSON_BYTES,
        },
        "limitations": [
            "The frozen 223198-check oracle is independently hash-validated; its cases are not regenerated or rerun by this provenance-only gate.",
            "The certificate applies only to the exact five frozen Rust artifacts and the additional explicitly enumerated owned Rust source graph.",
            "Static source, ELF and actual mapped runtime checks do not constitute a mathematical proof of unexercised future execution paths.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test", action="store_true",
        help="run only in-memory Rust-gate poison controls",
    )
    parser.add_argument(
        "--edge-oracle", type=Path, default=DEFAULT_EDGE,
        help="the single authorized frozen 223198-check Rust edge oracle",
    )
    parser.add_argument(
        "--output", type=Path, default=AUTHORIZED_OUTPUT,
        help="the single authorized Rust-only JSON report path",
    )
    args = parser.parse_args(argv)
    interpreter_issues = pinned_interpreter_issues()
    if interpreter_issues:
        print(json.dumps({
            "passed": False,
            "result": "FAIL",
            "issues": interpreter_issues,
        }, sort_keys=True))
        return 1
    if not authorized_path(args.output, AUTHORIZED_OUTPUT):
        parser.error("only candidates/audits/RUST-V8-SCANNER-FROM-SCRATCH.json is authorized")
    if not authorized_path(args.edge_oracle, DEFAULT_EDGE):
        parser.error("only the frozen Rust scanner-lifetimes edge oracle is authorized")
    if args.self_test:
        report = rust_self_test()
        print(json.dumps(report, sort_keys=True))
        return 0 if report["passed"] else 1

    report = run_rust_audit(args.edge_oracle)
    if report["passed"]:
        AUTHORIZED_OUTPUT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    summary = {
        "passed": report["passed"],
        "result": report["result"],
        "module": report["module"],
        "correctness_checks": report["edge_oracle"].get("correctness_checks"),
        "edge_failed": report["edge_oracle"].get("failed"),
        "edge_oracle_passed": report["edge_oracle"]["passed"],
        "artifact_count": report["frozen_live_artifacts"]["observed_count"],
        "artifacts_passed": report["frozen_live_artifacts"]["passed"],
        "source_passed": report["python_source"]["passed"],
        "native_sources_passed": all(item["passed"] for item in report["native_sources"]),
        "pipeline_passed": report["owned_pipeline"]["passed"],
        "manifest_passed": report["manifest_provenance"]["passed"],
        "rust_native_elf_passed": report["rust_native_elf_provenance"]["passed"],
        "rust_actual_mappings_passed": report["runtime_native_mapping_provenance"].get("passed", False),
        "isolated_runtime_passed": report["isolated_runtime"]["passed"],
        "rust_self_test_checks": report["self_test"]["check_count"],
        "upstream_poison_controls": report["upstream_poison_controls"]["validated_count"],
        "report": relative(AUTHORIZED_OUTPUT),
    }
    if not report["passed"]:
        summary["issues"] = (
            report["pinned_interpreter"]["issues"]
            + report["edge_oracle"]["issues"]
            + report["frozen_live_artifacts"]["issues"]
            + report["upstream_poison_controls"]["issues"]
            + report["input_issues"]
        )
    print(json.dumps(summary, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
