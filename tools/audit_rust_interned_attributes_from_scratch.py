#!/usr/bin/env python3
"""Fail-closed Rust-only provenance gate for native interned attribute names."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import audit_from_scratch as shared
from tools import audit_rust_from_scratch as scanner
from tools import audit_rust_native_heap_from_scratch as heap
from tools import audit_rust_variants_from_scratch as variants


DEFAULT_EDGE = (
    ROOT / "candidates" / "evidence"
    / "rust-v7-edge-oracle-rust-native-interned-attributes.json.gz"
)
DEFAULT_DEEP = (
    ROOT / "candidates" / "audits"
    / "RUST-V8-DEEP-CONTRACT-RUST-INTERNED-ATTRIBUTES.json.gz"
)
DEFAULT_OBSERVABILITY = (
    ROOT / "candidates" / "evidence"
    / "rust-v8-observability-rust-qualified-interned-attributes.json.gz"
)
AUTHORIZED_OUTPUT = (
    ROOT / "candidates" / "audits"
    / "RUST-V8-INTERNED-ATTRIBUTES-FROM-SCRATCH.json"
)
EDGE_CHECK_COUNT = 223198
EDGE_CATEGORY_COUNT = 49
DEEP_CHECK_COUNT = 393
DEEP_FAMILY_COUNT = 21
OBSERVABILITY_CHECK_COUNT = 479
OBSERVABILITY_FAMILY_COUNT = 11
FORBIDDEN_REGEX_GUARD_COUNT = 13
CROSS_ENGINE_GUARD_COUNT = 10
PRIVATE_BINDER_CHECK_COUNT = 34
EXPECTED_HEAP_CONTROL_COUNT = 115
EXPECTED_HEAP_NEGATIVE_COUNT = 108
EXPECTED_VARIANT_CONTROL_COUNT = 104
EXPECTED_SCANNER_CONTROL_COUNT = 49
EXPECTED_UPSTREAM_CONTROL_COUNT = 76
MINIMUM_INTERNED_NEGATIVE_CONTROLS = 49

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
    "public-python": "80812459261edb9585bdf703f137af3e0e788638af2ad7183d00b6d357e8a926",
    "native-bridge": "59da375e0e1e47274be58fc8a88440ee09f641b0ec05c34611f5d96bb3aaa716",
    "native-engine": "890f9e34e966244067a3dc173c2276043ae15d4830a05228fb37ec2571aa17cd",
    "native-source": "a2fa04912bb1f6957f833560446f4d3d1c5d13df8b5efac992fa63e28803668b",
    "bridge-source": "c5e01dd02ab4ac1bd530c3244eec146ffceb24a25db7901ed855d66b0665be03",
}
EDGE_PINS = scanner.EdgePins(
    compressed_sha256="02f2d9164d184720e3723b8f90061232b6a2e0c77ca71890c91c1b366f6a5508",
    result_sha256="b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526",
    script_sha256="fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca",
    component_sha256={
        "candidate_artifacts": "39ac22b9d0d4e1b4449f0b3e77408f588772cc7a4caadd880b172f087bffb147",
        "categories": "99a76d581e3fd8b68239867722a032e6f67701524896ec75684e11184f721ca8",
        "embedded_frozen_oracles": "7ba1fe99e4fd8389e1a4116c85c611ad847dcb41478d367c6ca059f24b57d4bc",
        "independent_source_seeds": "10b94594042987a1e9229b782bcdc9ce5d7d0543e91a203df18fef5733416bb0",
        "json_normalization": "62c42c6358643a3f99ff9cf4721059c8425965c59aec25c49b4efbd0219b4544",
        "membership_partitions": "785157a16916365ec6d9c6516a0c13499dca10c50ef4d2a988f2d145e69a9855",
    },
)
DEEP_PINS = heap.DeepPins(
    compressed_sha256="27f421d7d86885efa1121514ac83f06d51f3fbc7ebd1db8ff0206495d0295bf2",
    document_sha256="1bfd4319fb7be1434585ecbf67cc9d42e16b80cf002946f82cec16bc96301a52",
    observation_sha256="b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8",
    fixture_sha256="c72a5e47f15c94ce13ce34d4918c05ef81eea5b010ac119b255264e60939ef16",
    suite_sha256="ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978",
    component_sha256={
        "candidate": "7b4fe4f35951b758fcfe57c726ed96b8109bce8885c0a0764c2ca94237037147",
        "cross_engine_guard_observations": "cc475a7622f2e395896759f3b6128e675da57997462167b9b40acc44f1e29143",
        "differential_poison_self_tests": "f23f83fb8ce0e57fcf8a10b9470413b6c3d990812579eaaa906cd11259e692b5",
        "edge_oracle": "b4a613875b0f5a42cca0ef1862aa824a74f66162eff8b70855510d11dde902eb",
        "frozen_failure_evidence": "e04bc22376c1b340716606f328fd2159ef12eb25aaf04a3604fc09d8e63a7246",
        "guard_observations": "475b0d1c0feca44e158cdf050a63da17c27c852db93ca0d9e0387463a0f99f5c",
        "implementation_private_gc_topology_differences": "55754ce8c8cb8665fe4ad5212511882e97e0e8503c49eeb63045ae4ab2a2d652",
        "multifamily_runner": "0ad9194d38e366a6ebc6c89d55c31b2eb297e655b0fdf676579f53b47a6ab02e",
        "native_artifacts": "873c5da9dcc49264c00644efe6c9b2265e5607835caf52101f2a12e4c0bbbc72",
        "native_under_poison": "5994d57987f56611abf5212d8d1dfb4951947bd3221214b82e5fd335a66ca50d",
        "public_mismatch_family_counts": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        "public_mismatches": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "reference": "6e1ea37bf3cd3907da4b3a1679bd81a79f9218c31ac192dbea56cff2902ad88a",
        "reference_independent_repeat": "9693fb77da9ff4fa6c1e0c4be8353a1cc735bfab14c825bc5dcd6f8ce3e5757f",
        "stdlib_vs_stdlib_mismatches": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    },
)


@dataclass(frozen=True)
class ObservabilityPins:
    compressed_sha256: str
    document_sha256: str
    observation_sha256: str
    fixture_sha256: str
    binder_sha256: str
    component_sha256: dict[str, str]


OBSERVABILITY_PINS = ObservabilityPins(
    compressed_sha256="9345999533d3255af13c289a0cd942ec2a629473f2551bd9b9ed44c954e1cdbe",
    document_sha256="42f2eb861881af67d7a83f60f5d37047c8656a1559a87aa1bf5d4fa3bb64be47",
    observation_sha256="6e3593b963036e2381569475cac390ccbb7bc6dbc8358acda578fcbcb7e0642e",
    fixture_sha256="1d5a84b9fe2213289d96126dab740d103958bd593b811b262238bfc57a4a5403",
    binder_sha256="3254670410ef2bc93fd9b47f515e03471ed47ac1147a55dbdd73f5cc6195e301",
    component_sha256={
        "candidate": "ba52935385324c9e41952a95a04f9a7c5ba664dfab8ae424abd512bdc0bd7ed0",
        "candidate_failures_by_family": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        "cross_engine_guard_observations": "04528db5c930b8fed6c10305ba5214268175f26afdf7401a3c7ae0f40423b60e",
        "deep_proof": "eb116ba299a5d3db4773408cfcb852ae9de317016009c8f7ec99c806f34329b5",
        "edge_oracle": "b4a613875b0f5a42cca0ef1862aa824a74f66162eff8b70855510d11dde902eb",
        "failures": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "family_counts": "ed7fdd7dd37f1c5c767c99476ef16b37776ef4e34b97a6f6e6ddf2a844fbfe8e",
        "forbidden_regex_guard_observations": "de6f5cc9f8be019c8836ba6c64f3b03c0d05155390c24a1c46be3833e5aab65c",
        "immutable_frozen_observability": "5e8c7a03e0ebc5569f485fdbede3a3bae771225896d08cd62e0cc5ccacba6a8e",
        "multi_candidate_deep_runner": "0ad9194d38e366a6ebc6c89d55c31b2eb297e655b0fdf676579f53b47a6ab02e",
        "native_artifacts": "873c5da9dcc49264c00644efe6c9b2265e5607835caf52101f2a12e4c0bbbc72",
        "poison": "0a2d9690430f5e92a7b38963207d3f12b8b73cb89695baf9b60b410c3f2f36b5",
        "private_binder_failures": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "private_binder_observations": "3254670410ef2bc93fd9b47f515e03471ed47ac1147a55dbdd73f5cc6195e301",
        "public_iterator_controls": "a032e55a9735f7eef4b6ab40c0dea7deaeb34f3cc03ca89cf22b08718f6f4010",
        "reference": "66860c44536f7694ab98a106a695370c84611a4fd192979b343ccca61d4383d1",
        "reference_independent_repeat": "7d1c4401412041e801808d87f9f02b0680856188b23593cb33d7cafb80b635d3",
        "runner": "1f2e63102fa4027028f7a7343d29270a22bb599ec23b3fd927f2f77cd7752bb0",
    },
)
PRIOR_STAGE_CERTIFICATES = {
    **heap.PRIOR_STAGE_CERTIFICATES,
    "native-heap-auditor": (
        ROOT / "tools" / "audit_rust_native_heap_from_scratch.py",
        "78b717a3d6ef0623c6196781417e8fcd8533ebdefeb119310c22ed33a26e6e80",
    ),
    "native-heap-report": (
        ROOT / "candidates" / "audits" / "RUST-V8-NATIVE-HEAP-FROM-SCRATCH.json",
        "40079825f4b213bdbb585628c2fc6ec2e499cde566a4989d2d16e7c6d3877762",
    ),
}


def observe_artifacts() -> tuple[dict[str, dict[str, Any]], list[str]]:
    observed: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for role, path in ARTIFACT_PATHS.items():
        try:
            data = scanner.bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            issues.append(f"unreadable interned-attribute Rust {role}: {error}")
            continue
        actual = hashlib.sha256(data).hexdigest()
        expected = PINNED_ARTIFACT_HASHES[role]
        matches = actual == expected
        if not matches:
            issues.append(f"interned-attribute Rust {role} differs from its frozen artifact")
        observed[role] = {
            "role": role, "path": scanner.relative(path), "sha256": actual,
            "expected_sha256": expected, "matches_frozen_edge": matches,
        }
    if set(observed) != set(ARTIFACT_PATHS):
        issues.append("exactly five independently frozen Rust artifacts are required")
    return observed, issues


def check_artifact_rows(
    rows: Any, observed: dict[str, dict[str, Any]], label: str
) -> tuple[set[str], list[str]]:
    roles: set[str] = set()
    issues: list[str] = []
    if not isinstance(rows, list) or len(rows) != len(ARTIFACT_PATHS):
        return roles, [f"{label} must contain exactly five Rust artifacts"]
    for item in rows:
        if not isinstance(item, dict) or set(item) != {"path", "role", "sha256"}:
            issues.append(f"{label} contains a malformed Rust artifact")
            continue
        role = item["role"]
        if role not in ARTIFACT_PATHS or role in roles:
            issues.append(f"{label} contains a duplicated or unapproved Rust artifact")
            continue
        roles.add(role)
        expected_path = scanner.relative(ARTIFACT_PATHS[role])
        expected_digest = PINNED_ARTIFACT_HASHES[role]
        if item["path"] != expected_path:
            issues.append(f"{label} frozen {role} artifact path changed")
        if item["sha256"] != expected_digest:
            issues.append(f"{label} frozen {role} artifact digest changed")
        live = observed.get(role)
        if (not isinstance(live, dict) or live.get("path") != expected_path
                or live.get("sha256") != expected_digest
                or live.get("matches_frozen_edge") is not True):
            issues.append(f"{label} live {role} does not match its frozen artifact")
    if roles != set(ARTIFACT_PATHS):
        issues.append(f"{label} frozen Rust artifact roles are incomplete")
    return roles, issues


def check_required_fields(
    document: dict[str, Any], required: dict[str, Any], label: str
) -> list[str]:
    issues: list[str] = []
    for name, expected in required.items():
        actual = document.get(name)
        if type(actual) is not type(expected) or actual != expected:
            issues.append(f"{label} field {name!r} changed")
    return issues


def check_canonical_components(
    document: dict[str, Any], expected: dict[str, str], label: str
) -> tuple[dict[str, str], list[str]]:
    actual: dict[str, str] = {}
    issues: list[str] = []
    for name, digest in expected.items():
        if name not in document:
            issues.append(f"{label} component {name!r} is missing")
            continue
        try:
            found = scanner.canonical_sha256(document[name])
        except (TypeError, ValueError, UnicodeError) as error:
            issues.append(f"{label} component {name!r} is invalid: {error}")
            continue
        actual[name] = found
        if found != digest:
            issues.append(f"{label} component {name!r} digest changed")
    return actual, issues


def validate_edge_document(
    document: Any, archive_sha256: str,
    observed: dict[str, dict[str, Any]],
    pins: scanner.EdgePins = EDGE_PINS,
) -> dict[str, Any]:
    issues: list[str] = []
    if archive_sha256 != pins.compressed_sha256:
        issues.append("the frozen interned-attribute edge archive SHA-256 changed")
    if not isinstance(document, dict):
        return {"passed": False, "issues": issues + ["edge JSON must be an object"],
                "archive_sha256": archive_sha256, "correctness_checks": None,
                "artifact_count": 0}
    issues.extend(check_required_fields(document, {
        "schema": "rebar-v7-independent-edge-oracle-v1",
        "module": "candidates.rust_candidate", "python": "3.14.6",
        "correctness_checks": EDGE_CHECK_COUNT, "failed": 0,
        "expected_sha256": pins.result_sha256,
        "actual_sha256": pins.result_sha256,
        "script_sha256": pins.script_sha256,
        "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
    }, "interned-attribute edge"))
    if document.get("failures") != []:
        issues.append("interned-attribute edge failure rows must be present and empty")
    categories = document.get("categories")
    if not isinstance(categories, dict) or len(categories) != EDGE_CATEGORY_COUNT:
        issues.append("interned-attribute edge requires exactly 49 categories")
    elif any(type(count) is not int or count < 0 for count in categories.values()):
        issues.append("an interned-attribute edge category count is malformed")
    elif sum(categories.values()) != EDGE_CHECK_COUNT:
        issues.append("interned-attribute edge categories must sum to 223198")
    components, component_issues = check_canonical_components(
        document, pins.component_sha256, "interned-attribute edge"
    )
    issues.extend(component_issues)
    roles, row_issues = check_artifact_rows(
        document.get("candidate_artifacts"), observed, "interned-attribute edge"
    )
    issues.extend(row_issues)
    partitions = document.get("membership_partitions")
    if not isinstance(partitions, list) or len(partitions) != 4:
        issues.append("interned-attribute edge requires exactly four partitions")
    else:
        for row in partitions:
            if (not isinstance(row, dict) or row.get("stride") != 4099
                    or row.get("actual_sha256") != row.get("expected_sha256")):
                issues.append("interned-attribute edge partition evidence is invalid")
    return {
        "passed": not issues, "issues": issues,
        "file": scanner.relative(DEFAULT_EDGE), "archive_sha256": archive_sha256,
        "expected_archive_sha256": pins.compressed_sha256,
        "schema": document.get("schema"), "module": document.get("module"),
        "correctness_checks": document.get("correctness_checks"),
        "failed": document.get("failed"),
        "expected_sha256": document.get("expected_sha256"),
        "actual_sha256": document.get("actual_sha256"),
        "script_sha256": document.get("script_sha256"),
        "category_count": len(categories) if isinstance(categories, dict) else 0,
        "category_check_sum": (
            sum(categories.values())
            if isinstance(categories, dict)
            and all(type(value) is int for value in categories.values())
            else None
        ),
        "artifact_count": len(roles),
        "canonical_component_sha256": components,
        "holdout": document.get("holdout"),
        "performance": document.get("performance"),
    }


def validate_observation_snapshots(
    document: dict[str, Any], *, label: str, schema: str,
    check_count: int, family_count: int, observation_sha256: str,
    fixture_sha256: str, seed: int, observed: dict[str, dict[str, Any]],
    observability: bool,
) -> tuple[list[list[Any]], list[str]]:
    issues: list[str] = []
    snapshots: list[list[Any]] = []
    for key, expected_role in (
        ("candidate", "candidate"),
        ("reference", "stdlib-a"),
        ("reference_independent_repeat", "stdlib-b"),
    ):
        snapshot = document.get(key)
        if not isinstance(snapshot, dict):
            issues.append(f"{label} {key} snapshot is missing")
            continue
        required: dict[str, Any] = {
            "schema": schema, "python": "3.14.6", "role": expected_role,
            "checks": check_count, "fixture_sha256": fixture_sha256,
            "observation_sha256": observation_sha256,
            "seed": seed, "holdout": "NOT ACCESSED",
            "performance": "NOT MEASURED",
        }
        if key == "candidate":
            required.update({
                "candidate_family": "RUST",
                "candidate_module": "candidates.rust_candidate",
                "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
            })
        if observability:
            required["monitoring_available"] = True
            required["forbidden_regex_guards"] = (
                FORBIDDEN_REGEX_GUARD_COUNT if key == "candidate" else 0
            )
            required["private_binder_checks"] = (
                PRIVATE_BINDER_CHECK_COUNT if key == "candidate" else 0
            )
        else:
            required["guard_count"] = (
                FORBIDDEN_REGEX_GUARD_COUNT if key == "candidate" else 0
            )
        issues.extend(check_required_fields(snapshot, required, f"{label} {key}"))
        rows = snapshot.get("observations")
        if not isinstance(rows, list) or len(rows) != check_count:
            issues.append(f"{label} {key} observation rows are incomplete")
        else:
            ids: set[str] = set()
            for row in rows:
                if (not isinstance(row, dict)
                        or set(row) != {"family", "id", "observation", "sha256"}
                        or not isinstance(row.get("id"), str)
                        or row["id"] in ids):
                    issues.append(f"{label} {key} observation row is malformed or duplicated")
                    break
                ids.add(row["id"])
                if row["sha256"] != scanner.canonical_sha256(row["observation"]):
                    issues.append(f"{label} {key} observation row digest changed")
                    break
            if scanner.canonical_sha256(rows) != observation_sha256:
                issues.append(f"{label} {key} complete observation digest changed")
            snapshots.append(rows)
        counts = snapshot.get("family_counts")
        if (not isinstance(counts, dict) or len(counts) != family_count
                or any(type(value) is not int or value < 0 for value in counts.values())
                or sum(counts.values()) != check_count):
            issues.append(f"{label} {key} complete family counts are invalid")
        guard_key = (
            "forbidden_regex_guard_observations" if observability
            else "guard_observations"
        )
        guard_rows = snapshot.get(guard_key)
        expected_guards = FORBIDDEN_REGEX_GUARD_COUNT if key == "candidate" else 0
        if not isinstance(guard_rows, list) or len(guard_rows) != expected_guards:
            issues.append(f"{label} {key} forbidden-engine guards are incomplete")
        cross_key = (
            "cross_engine_guard_observations" if observability else "cross_engine_guards"
        )
        if key == "candidate":
            cross_rows = snapshot.get(cross_key)
            if not isinstance(cross_rows, list) or len(cross_rows) != CROSS_ENGINE_GUARD_COUNT:
                issues.append(f"{label} candidate cross-family guards are incomplete")
            _, row_issues = check_artifact_rows(
                snapshot.get("native_artifacts"), observed,
                f"{label} candidate snapshot"
            )
            issues.extend(row_issues)
            if snapshot.get("native_artifacts") != document.get("native_artifacts"):
                issues.append(f"{label} candidate artifacts do not bind to the proof")
        elif snapshot.get("native_artifacts") != []:
            issues.append(f"{label} independent stdlib references must have no native artifacts")
        if observability:
            binders = snapshot.get("private_binder_observations")
            expected_binders = PRIVATE_BINDER_CHECK_COUNT if key == "candidate" else 0
            if not isinstance(binders, list) or len(binders) != expected_binders:
                issues.append(f"{label} {key} private binder controls are incomplete")
            if snapshot.get("private_binder_failures") != []:
                issues.append(f"{label} {key} private binder failures are nonempty")
    if len(snapshots) != 3 or not (snapshots[0] == snapshots[1] == snapshots[2]):
        issues.append(f"{label} requires three complete identical observation snapshots")
    return snapshots, issues


def validate_edge_binding(
    binding: Any, observed: dict[str, dict[str, Any]],
    edge: dict[str, Any], label: str,
) -> list[str]:
    if not isinstance(binding, dict):
        return [f"{label} immutable edge binding is missing"]
    issues = check_required_fields(binding, {
        "schema": "rebar-v7-independent-edge-oracle-v1",
        "family": "RUST", "module": "candidates.rust_candidate",
        "path": str(DEFAULT_EDGE),
        "archive_sha256": EDGE_PINS.compressed_sha256,
        "checks": EDGE_CHECK_COUNT, "failed": 0,
        "category_count": EDGE_CATEGORY_COUNT,
        "candidate_sha256": EDGE_PINS.result_sha256,
        "reference_sha256": EDGE_PINS.result_sha256,
        "script_sha256": EDGE_PINS.script_sha256,
    }, f"{label} edge binding")
    if not edge.get("passed") or edge.get("archive_sha256") != EDGE_PINS.compressed_sha256:
        issues.append(f"{label} binds to an invalid or stale live edge")
    for name in ("candidate_artifacts", "production_artifacts"):
        _, row_issues = check_artifact_rows(binding.get(name), observed,
                                             f"{label} edge {name}")
        issues.extend(row_issues)
    if binding.get("candidate_artifacts") != binding.get("production_artifacts"):
        issues.append(f"{label} edge candidate and production artifact rows differ")
    return issues


def validate_deep_document(
    document: Any, archive_sha256: str,
    observed: dict[str, dict[str, Any]], edge: dict[str, Any],
    pins: heap.DeepPins = DEEP_PINS,
) -> dict[str, Any]:
    issues: list[str] = []
    if archive_sha256 != pins.compressed_sha256:
        issues.append("the complete interned-attribute deep archive SHA-256 changed")
    if not isinstance(document, dict):
        return {"passed": False, "issues": issues + ["deep JSON must be an object"],
                "archive_sha256": archive_sha256, "checks": None,
                "public_mismatch_count": None, "artifact_count": 0}
    issues.extend(check_required_fields(document, {
        "schema": "rebar-rust-v8-deep-public-contract-v1",
        "python": "3.14.6", "status": "PASS",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "checks": DEEP_CHECK_COUNT, "public_mismatch_count": 0,
        "candidate_sha256": pins.observation_sha256,
        "reference_a_sha256": pins.observation_sha256,
        "reference_b_sha256": pins.observation_sha256,
        "fixture_sha256": pins.fixture_sha256,
        "suite_sha256": pins.suite_sha256,
        "forbidden_regex_guards": FORBIDDEN_REGEX_GUARD_COUNT,
        "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
        "seed": 2026072347, "seeded_case_count": 64,
        "implementation_private_gc_topology_difference_count": 36,
        "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
    }, "complete interned-attribute deep proof"))
    try:
        canonical = scanner.canonical_sha256(document)
    except (TypeError, ValueError, UnicodeError) as error:
        canonical = None
        issues.append(f"complete interned-attribute deep canonical JSON is invalid: {error}")
    if canonical != pins.document_sha256:
        issues.append("the complete 393-row deep canonical digest changed")
    components, component_issues = check_canonical_components(
        document, pins.component_sha256, "complete interned-attribute deep proof"
    )
    issues.extend(component_issues)
    if document.get("public_mismatches") != []:
        issues.append("complete deep public mismatch rows must be empty")
    if document.get("stdlib_vs_stdlib_mismatches") != []:
        issues.append("complete deep independent-reference mismatch rows must be empty")
    if document.get("public_mismatch_family_counts") != {}:
        issues.append("complete deep mismatch family counts must be empty")
    for name, count in (
        ("guard_observations", FORBIDDEN_REGEX_GUARD_COUNT),
        ("cross_engine_guard_observations", CROSS_ENGINE_GUARD_COUNT),
        ("implementation_private_gc_topology_differences", 36),
    ):
        rows = document.get(name)
        if not isinstance(rows, list) or len(rows) != count:
            issues.append(f"complete deep {name} rows are incomplete")
    roles, artifact_issues = check_artifact_rows(
        document.get("native_artifacts"), observed, "complete interned-attribute deep proof"
    )
    issues.extend(artifact_issues)
    snapshots, snapshot_issues = validate_observation_snapshots(
        document, label="complete 393-check deep proof",
        schema="rebar-rust-v8-deep-public-contract-v1",
        check_count=DEEP_CHECK_COUNT, family_count=DEEP_FAMILY_COUNT,
        observation_sha256=pins.observation_sha256,
        fixture_sha256=pins.fixture_sha256, seed=2026072347,
        observed=observed, observability=False,
    )
    issues.extend(snapshot_issues)
    issues.extend(validate_edge_binding(
        document.get("edge_oracle"), observed, edge, "complete 393-check deep proof"
    ))
    differential = document.get("differential_poison_self_tests")
    if (not isinstance(differential, dict)
            or set(differential) != {
                "changed_observation_poison", "identical_reference",
                "missing_observation_poison"
            }
            or any(value != "PASS" for value in differential.values())):
        issues.append("the complete deep differential poison controls failed")
    return {
        "passed": not issues, "issues": issues,
        "file": scanner.relative(DEFAULT_DEEP),
        "archive_sha256": archive_sha256,
        "expected_archive_sha256": pins.compressed_sha256,
        "canonical_sha256": canonical,
        "expected_canonical_sha256": pins.document_sha256,
        "schema": document.get("schema"), "status": document.get("status"),
        "candidate_family": document.get("candidate_family"),
        "candidate_module": document.get("candidate_module"),
        "checks": document.get("checks"),
        "public_mismatch_count": document.get("public_mismatch_count"),
        "forbidden_regex_guards": document.get("forbidden_regex_guards"),
        "cross_engine_guard_count": document.get("cross_engine_guard_count"),
        "artifact_count": len(roles),
        "reference_snapshot_count": len(snapshots),
        "complete_observation_rows_per_snapshot": [len(rows) for rows in snapshots],
        "canonical_component_sha256": components,
        "edge_archive_sha256": (
            document.get("edge_oracle", {}).get("archive_sha256")
            if isinstance(document.get("edge_oracle"), dict) else None
        ),
        "holdout": document.get("holdout"),
        "performance": document.get("performance"),
    }


def validate_deep_binding(
    binding: Any, observed: dict[str, dict[str, Any]],
    deep: dict[str, Any], label: str,
) -> list[str]:
    if not isinstance(binding, dict):
        return [f"{label} complete 393-check deep binding is missing"]
    issues = check_required_fields(binding, {
        "schema": "rebar-rust-v8-deep-public-contract-v1",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "path": str(DEFAULT_DEEP),
        "archive_sha256": DEEP_PINS.compressed_sha256,
        "checks": DEEP_CHECK_COUNT, "status": "PASS",
        "candidate_sha256": DEEP_PINS.observation_sha256,
        "reference_sha256": DEEP_PINS.observation_sha256,
        "fixture_sha256": DEEP_PINS.fixture_sha256,
        "edge_archive_sha256": EDGE_PINS.compressed_sha256,
        "seed": 2026072347,
    }, f"{label} complete deep binding")
    if not deep.get("passed") or deep.get("archive_sha256") != DEEP_PINS.compressed_sha256:
        issues.append(f"{label} binds to a stale or incomplete 393-check deep proof")
    _, artifact_issues = check_artifact_rows(
        binding.get("native_artifacts"), observed, f"{label} complete deep binding"
    )
    return issues + artifact_issues


def validate_observability_document(
    document: Any, archive_sha256: str,
    observed: dict[str, dict[str, Any]], edge: dict[str, Any],
    deep: dict[str, Any], pins: ObservabilityPins = OBSERVABILITY_PINS,
) -> dict[str, Any]:
    issues: list[str] = []
    if archive_sha256 != pins.compressed_sha256:
        issues.append("the complete 479-check observability archive SHA-256 changed")
    if not isinstance(document, dict):
        return {"passed": False, "issues": issues + ["observability JSON must be an object"],
                "archive_sha256": archive_sha256, "checks": None,
                "candidate_failures": None, "artifact_count": 0}
    issues.extend(check_required_fields(document, {
        "schema": "rebar-v8-multi-candidate-observability-v1",
        "python": "3.14.6", "status": "PASS",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "checks": OBSERVABILITY_CHECK_COUNT,
        "candidate_checks": OBSERVABILITY_CHECK_COUNT,
        "self_oracle_checks": OBSERVABILITY_CHECK_COUNT,
        "candidate_failures": 0, "self_oracle_failures": 0,
        "expected_observation_sha256": pins.observation_sha256,
        "actual_observation_sha256": pins.observation_sha256,
        "fixture_sha256": pins.fixture_sha256,
        "forbidden_regex_guards": FORBIDDEN_REGEX_GUARD_COUNT,
        "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
        "private_binder_checks": PRIVATE_BINDER_CHECK_COUNT,
        "private_binder_observation_sha256": pins.binder_sha256,
        "monitoring_available": True,
        "seed": 2026072343, "seeded_cases": 64,
        "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
    }, "complete 479-check interned-attribute observability"))
    try:
        canonical = scanner.canonical_sha256(document)
    except (TypeError, ValueError, UnicodeError) as error:
        canonical = None
        issues.append(f"complete 479-check canonical JSON is invalid: {error}")
    if canonical != pins.document_sha256:
        issues.append("the complete 479-check observability canonical digest changed")
    components, component_issues = check_canonical_components(
        document, pins.component_sha256, "complete 479-check observability"
    )
    issues.extend(component_issues)
    if document.get("failures") != []:
        issues.append("all 479 public observability failure rows must be empty")
    if document.get("candidate_failures_by_family") != {}:
        issues.append("all 479 observability family failure counts must be empty")
    if document.get("private_binder_failures") != []:
        issues.append("all 34 native private binder controls must pass")
    for name, count in (
        ("forbidden_regex_guard_observations", FORBIDDEN_REGEX_GUARD_COUNT),
        ("cross_engine_guard_observations", CROSS_ENGINE_GUARD_COUNT),
        ("private_binder_observations", PRIVATE_BINDER_CHECK_COUNT),
    ):
        rows = document.get(name)
        if not isinstance(rows, list) or len(rows) != count:
            issues.append(f"complete 479-check {name} rows are incomplete")
    binders = document.get("private_binder_observations")
    if isinstance(binders, list) and scanner.canonical_sha256(binders) != pins.binder_sha256:
        issues.append("all 34 native private binder row digests must be preserved")
    counts = document.get("family_counts")
    if (not isinstance(counts, dict) or len(counts) != OBSERVABILITY_FAMILY_COUNT
            or any(type(value) is not int or value < 0 for value in counts.values())
            or sum(counts.values()) != OBSERVABILITY_CHECK_COUNT):
        issues.append("all 479 observability family counts must be preserved")
    roles, artifact_issues = check_artifact_rows(
        document.get("native_artifacts"), observed, "complete 479-check observability"
    )
    issues.extend(artifact_issues)
    snapshots, snapshot_issues = validate_observation_snapshots(
        document, label="complete 479-check observability",
        schema="rebar-rust-v7-public-observability-v2",
        check_count=OBSERVABILITY_CHECK_COUNT,
        family_count=OBSERVABILITY_FAMILY_COUNT,
        observation_sha256=pins.observation_sha256,
        fixture_sha256=pins.fixture_sha256,
        seed=2026072343, observed=observed, observability=True,
    )
    issues.extend(snapshot_issues)
    issues.extend(validate_edge_binding(
        document.get("edge_oracle"), observed, edge,
        "complete 479-check observability"
    ))
    issues.extend(validate_deep_binding(
        document.get("deep_proof"), observed, deep,
        "complete 479-check observability"
    ))
    candidate = document.get("candidate")
    if isinstance(candidate, dict):
        issues.extend(validate_edge_binding(
            candidate.get("edge_oracle"), observed, edge,
            "complete 479-check candidate snapshot"
        ))
        issues.extend(validate_deep_binding(
            candidate.get("deep_proof"), observed, deep,
            "complete 479-check candidate snapshot"
        ))
    controls = document.get("public_iterator_controls")
    if (not isinstance(controls, dict) or controls.get("checks") != 2
            or controls.get("failures") != []
            or not isinstance(controls.get("observations"), list)
            or len(controls["observations"]) != 2):
        issues.append("both public iterator poison controls must remain complete")
    poison = document.get("poison")
    if not isinstance(poison, dict):
        issues.append("the full observability poison proof is missing")
    else:
        issues.extend(check_required_fields(poison, {
            "schema": "rebar-v8-multi-candidate-observability-v1",
            "role": "poison", "python": "3.14.6",
            "candidate_family": "RUST",
            "candidate_module": "candidates.rust_candidate",
            "checks": OBSERVABILITY_CHECK_COUNT,
            "fixture_sha256": pins.fixture_sha256,
            "forbidden_regex_guards": FORBIDDEN_REGEX_GUARD_COUNT,
            "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
            "seed": 2026072343,
            "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
        }, "complete 479-check poison"))
    return {
        "passed": not issues, "issues": issues,
        "file": scanner.relative(DEFAULT_OBSERVABILITY),
        "archive_sha256": archive_sha256,
        "expected_archive_sha256": pins.compressed_sha256,
        "canonical_sha256": canonical,
        "expected_canonical_sha256": pins.document_sha256,
        "schema": document.get("schema"), "status": document.get("status"),
        "candidate_family": document.get("candidate_family"),
        "candidate_module": document.get("candidate_module"),
        "checks": document.get("checks"),
        "candidate_failures": document.get("candidate_failures"),
        "forbidden_regex_guards": document.get("forbidden_regex_guards"),
        "cross_engine_guard_count": document.get("cross_engine_guard_count"),
        "private_binder_checks": document.get("private_binder_checks"),
        "artifact_count": len(roles),
        "reference_snapshot_count": len(snapshots),
        "complete_observation_rows_per_snapshot": [len(rows) for rows in snapshots],
        "canonical_component_sha256": components,
        "holdout": document.get("holdout"),
        "performance": document.get("performance"),
    }


def load_proof(path: Path, authorized: Path, digest: str, label: str) -> tuple[Any, str, list[str]]:
    if not scanner.authorized_path(path, authorized):
        return None, "", [f"only the expressly authorized {label} may be read"]
    try:
        compressed = scanner.bounded_binary(authorized, heap.MAX_COMPRESSED_BYTES)
    except (OSError, ValueError) as error:
        return None, "", [f"the authorized {label} cannot be read: {error}"]
    return heap.decode_pinned_gzip(compressed, digest, label)


def load_edge(path: Path, observed: dict[str, dict[str, Any]]) -> dict[str, Any]:
    document, digest, issues = load_proof(
        path, DEFAULT_EDGE, EDGE_PINS.compressed_sha256, "interned-attribute edge"
    )
    if issues:
        return {"passed": False, "issues": issues, "archive_sha256": digest,
                "correctness_checks": None, "artifact_count": 0}
    return validate_edge_document(document, digest, observed)


def load_deep(
    path: Path, observed: dict[str, dict[str, Any]], edge: dict[str, Any]
) -> dict[str, Any]:
    document, digest, issues = load_proof(
        path, DEFAULT_DEEP, DEEP_PINS.compressed_sha256,
        "complete interned-attribute 393-check deep proof"
    )
    if issues:
        return {"passed": False, "issues": issues, "archive_sha256": digest,
                "checks": None, "public_mismatch_count": None,
                "artifact_count": 0}
    return validate_deep_document(document, digest, observed, edge)


def load_observability(
    path: Path, observed: dict[str, dict[str, Any]],
    edge: dict[str, Any], deep: dict[str, Any],
) -> dict[str, Any]:
    document, digest, issues = load_proof(
        path, DEFAULT_OBSERVABILITY, OBSERVABILITY_PINS.compressed_sha256,
        "complete interned-attribute 479-check qualified observability proof"
    )
    if issues:
        return {"passed": False, "issues": issues, "archive_sha256": digest,
                "checks": None, "candidate_failures": None,
                "artifact_count": 0}
    return validate_observability_document(document, digest, observed, edge, deep)


def validate_prior_certificates() -> dict[str, Any]:
    issues: list[str] = []
    artifacts: list[dict[str, Any]] = []
    for role, (path, expected) in PRIOR_STAGE_CERTIFICATES.items():
        try:
            data = scanner.bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            issues.append(f"immutable prior {role} is unreadable: {error}")
            continue
        actual = hashlib.sha256(data).hexdigest()
        matches = actual == expected
        if not matches:
            issues.append(f"immutable prior {role} was modified")
        artifacts.append({
            "role": role, "path": scanner.relative(path),
            "sha256": actual, "expected_sha256": expected,
            "matches": matches,
        })
    if len(artifacts) != len(PRIOR_STAGE_CERTIFICATES):
        issues.append("all six scanner, cmethod, and native-heap certificates are required")
    return {"passed": not issues, "issues": issues,
            "expected_count": len(PRIOR_STAGE_CERTIFICATES),
            "observed_count": len(artifacts), "artifacts": artifacts}


def inherited_heap_issues(report: Any) -> list[str]:
    if not isinstance(report, dict):
        return ["the independently inherited 115 native-heap controls are missing"]
    issues: list[str] = []
    checks = report.get("checks")
    if (report.get("passed") is not True or report.get("failed") != []
            or report.get("fixture_storage") != "in-memory only"
            or not isinstance(checks, list)
            or len(checks) != EXPECTED_HEAP_CONTROL_COUNT
            or report.get("check_count") != EXPECTED_HEAP_CONTROL_COUNT
            or report.get("negative_control_count") != EXPECTED_HEAP_NEGATIVE_COUNT):
        issues.append("the exact 115 native-heap poison controls did not pass")
    names: set[str] = set()
    if isinstance(checks, list):
        for item in checks:
            if (not isinstance(item, dict) or set(item) != {"name", "passed"}
                    or not isinstance(item.get("name"), str)
                    or item.get("passed") is not True or item["name"] in names):
                issues.append("an inherited native-heap poison control is invalid")
                break
            names.add(item["name"])
        if sum(name.startswith("reject_") for name in names) != EXPECTED_HEAP_NEGATIVE_COUNT:
            issues.append("the exact inherited 108 native-heap negatives changed")
    issues.extend(heap.inherited_variant_issues(report.get("inherited_variant_controls")))
    issues.extend(scanner.validate_control_report(report.get("upstream_controls")))
    if report.get("inherited_variant_control_issues") != []:
        issues.append("the inherited 104 cmethod controls contain failures")
    if report.get("upstream_control_issues") != []:
        issues.append("the inherited 76 isolated shared controls contain failures")
    return issues


def synthetic_proofs() -> tuple[
    dict[str, Any], scanner.EdgePins, dict[str, dict[str, Any]],
    dict[str, Any], heap.DeepPins, dict[str, Any],
    dict[str, Any], ObservabilityPins, dict[str, Any],
]:
    artifacts = [{"role": role, "path": scanner.relative(path),
                  "sha256": PINNED_ARTIFACT_HASHES[role]}
                 for role, path in ARTIFACT_PATHS.items()]
    observed = {row["role"]: {**row, "expected_sha256": row["sha256"],
                               "matches_frozen_edge": True}
                for row in artifacts}
    categories = {f"synthetic-{index:02d}": 1 for index in range(48)}
    categories["synthetic-48"] = EDGE_CHECK_COUNT - 48
    partitions = [{"partition": str(index), "stride": 4099,
                   "expected_sha256": hashlib.sha256(str(index).encode()).hexdigest(),
                   "actual_sha256": hashlib.sha256(str(index).encode()).hexdigest()}
                  for index in range(4)]
    edge_doc: dict[str, Any] = {
        "schema": "rebar-v7-independent-edge-oracle-v1",
        "module": "candidates.rust_candidate", "python": "3.14.6",
        "correctness_checks": EDGE_CHECK_COUNT, "failed": 0, "failures": [],
        "expected_sha256": EDGE_PINS.result_sha256,
        "actual_sha256": EDGE_PINS.result_sha256,
        "script_sha256": EDGE_PINS.script_sha256,
        "candidate_artifacts": copy.deepcopy(artifacts),
        "categories": categories,
        "embedded_frozen_oracles": [{"name": "interned-synthetic"}],
        "independent_source_seeds": {"interned-synthetic": 1},
        "json_normalization": {"interned-synthetic": "canonical"},
        "membership_partitions": partitions,
        "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
    }
    compressed_edge = gzip.compress(
        json.dumps(edge_doc, sort_keys=True, separators=(",", ":")).encode(), mtime=0
    )
    edge_pins = scanner.EdgePins(
        compressed_sha256=hashlib.sha256(compressed_edge).hexdigest(),
        result_sha256=EDGE_PINS.result_sha256,
        script_sha256=EDGE_PINS.script_sha256,
        component_sha256={name: scanner.canonical_sha256(edge_doc[name])
                          for name in EDGE_PINS.component_sha256},
    )
    clean_edge = validate_edge_document(edge_doc, edge_pins.compressed_sha256,
                                        observed, edge_pins)
    bound_edge = dict(clean_edge)
    bound_edge["archive_sha256"] = EDGE_PINS.compressed_sha256

    def make_rows(count: int, family_count: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
        rows = []
        for index in range(count):
            observation = {"synthetic_index": index}
            rows.append({
                "family": f"synthetic-{index % family_count:02d}",
                "id": f"interned-{count}-{index:04d}",
                "observation": observation,
                "sha256": scanner.canonical_sha256(observation),
            })
        counts = {
            f"synthetic-{index:02d}": sum(
                item["family"] == f"synthetic-{index:02d}" for item in rows
            )
            for index in range(family_count)
        }
        return rows, counts

    deep_rows, deep_families = make_rows(DEEP_CHECK_COUNT, DEEP_FAMILY_COUNT)
    deep_digest = scanner.canonical_sha256(deep_rows)
    forbidden = [{"id": f"forbidden-{index}"}
                 for index in range(FORBIDDEN_REGEX_GUARD_COUNT)]
    cross = [{"id": f"cross-{index}"} for index in range(CROSS_ENGINE_GUARD_COUNT)]

    def edge_binding() -> dict[str, Any]:
        return {
            "schema": "rebar-v7-independent-edge-oracle-v1",
            "family": "RUST", "module": "candidates.rust_candidate",
            "path": str(DEFAULT_EDGE),
            "archive_sha256": EDGE_PINS.compressed_sha256,
            "checks": EDGE_CHECK_COUNT, "failed": 0,
            "category_count": EDGE_CATEGORY_COUNT,
            "candidate_sha256": EDGE_PINS.result_sha256,
            "reference_sha256": EDGE_PINS.result_sha256,
            "script_sha256": EDGE_PINS.script_sha256,
            "candidate_artifacts": copy.deepcopy(artifacts),
            "production_artifacts": copy.deepcopy(artifacts),
        }

    def deep_snapshot(role: str) -> dict[str, Any]:
        candidate = role == "candidate"
        result: dict[str, Any] = {
            "schema": "rebar-rust-v8-deep-public-contract-v1",
            "python": "3.14.6", "role": role,
            "checks": DEEP_CHECK_COUNT,
            "fixture_sha256": DEEP_PINS.fixture_sha256,
            "observation_sha256": deep_digest,
            "observations": copy.deepcopy(deep_rows),
            "family_counts": copy.deepcopy(deep_families),
            "guard_count": FORBIDDEN_REGEX_GUARD_COUNT if candidate else 0,
            "guard_observations": copy.deepcopy(forbidden) if candidate else [],
            "native_artifacts": copy.deepcopy(artifacts) if candidate else [],
            "implementation_private_gc_diagnostics": [
                {"index": index} for index in range(64)
            ],
            "seed": 2026072347,
            "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
        }
        if candidate:
            result.update({
                "candidate_family": "RUST",
                "candidate_module": "candidates.rust_candidate",
                "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
                "cross_engine_guards": copy.deepcopy(cross),
            })
        return result

    deep_doc: dict[str, Any] = {
        "schema": "rebar-rust-v8-deep-public-contract-v1",
        "python": "3.14.6", "status": "PASS",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "checks": DEEP_CHECK_COUNT, "public_mismatch_count": 0,
        "candidate_sha256": deep_digest,
        "reference_a_sha256": deep_digest,
        "reference_b_sha256": deep_digest,
        "fixture_sha256": DEEP_PINS.fixture_sha256,
        "suite_sha256": DEEP_PINS.suite_sha256,
        "forbidden_regex_guards": FORBIDDEN_REGEX_GUARD_COUNT,
        "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
        "cross_engine_guard_observations": copy.deepcopy(cross),
        "guard_observations": copy.deepcopy(forbidden),
        "seed": 2026072347, "seeded_case_count": 64,
        "implementation_private_gc_topology_difference_count": 36,
        "implementation_private_gc_topology_differences": [
            {"index": index} for index in range(36)
        ],
        "native_artifacts": copy.deepcopy(artifacts),
        "candidate": deep_snapshot("candidate"),
        "reference": deep_snapshot("stdlib-a"),
        "reference_independent_repeat": deep_snapshot("stdlib-b"),
        "public_mismatch_family_counts": {}, "public_mismatches": [],
        "stdlib_vs_stdlib_mismatches": [],
        "differential_poison_self_tests": {
            "changed_observation_poison": "PASS",
            "identical_reference": "PASS",
            "missing_observation_poison": "PASS",
        },
        "frozen_failure_evidence": {"status": "FAIL", "public_mismatch_count": 104},
        "native_under_poison": {"search": {"status": "value"}},
        "multifamily_runner": {"path": "synthetic", "sha256": "b" * 64},
        "edge_oracle": edge_binding(),
        "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
    }
    compressed_deep = gzip.compress(
        json.dumps(deep_doc, sort_keys=True, separators=(",", ":")).encode(), mtime=0
    )
    deep_pins = heap.DeepPins(
        compressed_sha256=hashlib.sha256(compressed_deep).hexdigest(),
        document_sha256=scanner.canonical_sha256(deep_doc),
        observation_sha256=deep_digest,
        fixture_sha256=DEEP_PINS.fixture_sha256,
        suite_sha256=DEEP_PINS.suite_sha256,
        component_sha256={name: scanner.canonical_sha256(deep_doc[name])
                          for name in DEEP_PINS.component_sha256},
    )
    clean_deep = validate_deep_document(
        deep_doc, deep_pins.compressed_sha256, observed, bound_edge, deep_pins
    )
    bound_deep = dict(clean_deep)
    bound_deep["archive_sha256"] = DEEP_PINS.compressed_sha256

    observation_rows, observation_families = make_rows(
        OBSERVABILITY_CHECK_COUNT, OBSERVABILITY_FAMILY_COUNT
    )
    observation_digest = scanner.canonical_sha256(observation_rows)
    binders = [{"id": f"binder-{index}", "passed": True}
               for index in range(PRIVATE_BINDER_CHECK_COUNT)]
    binder_digest = scanner.canonical_sha256(binders)

    def deep_binding() -> dict[str, Any]:
        return {
            "schema": "rebar-rust-v8-deep-public-contract-v1",
            "candidate_family": "RUST",
            "candidate_module": "candidates.rust_candidate",
            "path": str(DEFAULT_DEEP),
            "archive_sha256": DEEP_PINS.compressed_sha256,
            "checks": DEEP_CHECK_COUNT, "status": "PASS",
            "candidate_sha256": DEEP_PINS.observation_sha256,
            "reference_sha256": DEEP_PINS.observation_sha256,
            "fixture_sha256": DEEP_PINS.fixture_sha256,
            "edge_archive_sha256": EDGE_PINS.compressed_sha256,
            "seed": 2026072347,
            "native_artifacts": copy.deepcopy(artifacts),
        }

    def observability_snapshot(role: str) -> dict[str, Any]:
        candidate = role == "candidate"
        result: dict[str, Any] = {
            "schema": "rebar-rust-v7-public-observability-v2",
            "python": "3.14.6", "role": role,
            "checks": OBSERVABILITY_CHECK_COUNT,
            "fixture_sha256": OBSERVABILITY_PINS.fixture_sha256,
            "observation_sha256": observation_digest,
            "observations": copy.deepcopy(observation_rows),
            "family_counts": copy.deepcopy(observation_families),
            "forbidden_regex_guards": FORBIDDEN_REGEX_GUARD_COUNT if candidate else 0,
            "forbidden_regex_guard_observations": (
                copy.deepcopy(forbidden) if candidate else []
            ),
            "native_artifacts": copy.deepcopy(artifacts) if candidate else [],
            "private_binder_checks": PRIVATE_BINDER_CHECK_COUNT if candidate else 0,
            "private_binder_observations": copy.deepcopy(binders) if candidate else [],
            "private_binder_failures": [], "monitoring_available": True,
            "seed": 2026072343,
            "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
        }
        if candidate:
            result.update({
                "candidate_family": "RUST",
                "candidate_module": "candidates.rust_candidate",
                "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
                "cross_engine_guard_observations": copy.deepcopy(cross),
                "private_binder_observation_sha256": binder_digest,
                "edge_oracle": edge_binding(), "deep_proof": deep_binding(),
            })
        return result

    observability_doc: dict[str, Any] = {
        "schema": "rebar-v8-multi-candidate-observability-v1",
        "python": "3.14.6", "status": "PASS",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "checks": OBSERVABILITY_CHECK_COUNT,
        "candidate_checks": OBSERVABILITY_CHECK_COUNT,
        "self_oracle_checks": OBSERVABILITY_CHECK_COUNT,
        "candidate_failures": 0, "self_oracle_failures": 0,
        "expected_observation_sha256": observation_digest,
        "actual_observation_sha256": observation_digest,
        "fixture_sha256": OBSERVABILITY_PINS.fixture_sha256,
        "forbidden_regex_guards": FORBIDDEN_REGEX_GUARD_COUNT,
        "forbidden_regex_guard_observations": copy.deepcopy(forbidden),
        "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
        "cross_engine_guard_observations": copy.deepcopy(cross),
        "private_binder_checks": PRIVATE_BINDER_CHECK_COUNT,
        "private_binder_observation_sha256": binder_digest,
        "private_binder_observations": copy.deepcopy(binders),
        "private_binder_failures": [],
        "monitoring_available": True,
        "seed": 2026072343, "seeded_cases": 64,
        "family_counts": copy.deepcopy(observation_families),
        "candidate_failures_by_family": {}, "failures": [],
        "native_artifacts": copy.deepcopy(artifacts),
        "candidate": observability_snapshot("candidate"),
        "reference": observability_snapshot("stdlib-a"),
        "reference_independent_repeat": observability_snapshot("stdlib-b"),
        "deep_proof": deep_binding(), "edge_oracle": edge_binding(),
        "public_iterator_controls": {
            "checks": 2, "failures": [],
            "observations": [{"index": 0}, {"index": 1}],
        },
        "immutable_frozen_observability": {"sha256": "c" * 64},
        "multi_candidate_deep_runner": {"sha256": "d" * 64},
        "runner": {"sha256": "e" * 64},
        "poison": {
            "schema": "rebar-v8-multi-candidate-observability-v1",
            "role": "poison", "python": "3.14.6",
            "candidate_family": "RUST",
            "candidate_module": "candidates.rust_candidate",
            "checks": OBSERVABILITY_CHECK_COUNT,
            "fixture_sha256": OBSERVABILITY_PINS.fixture_sha256,
            "forbidden_regex_guards": FORBIDDEN_REGEX_GUARD_COUNT,
            "cross_engine_guard_count": CROSS_ENGINE_GUARD_COUNT,
            "seed": 2026072343,
            "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
        },
        "holdout": "NOT ACCESSED", "performance": "NOT MEASURED",
    }
    compressed_observability = gzip.compress(
        json.dumps(observability_doc, sort_keys=True, separators=(",", ":")).encode(),
        mtime=0,
    )
    observation_pins = ObservabilityPins(
        compressed_sha256=hashlib.sha256(compressed_observability).hexdigest(),
        document_sha256=scanner.canonical_sha256(observability_doc),
        observation_sha256=observation_digest,
        fixture_sha256=OBSERVABILITY_PINS.fixture_sha256,
        binder_sha256=binder_digest,
        component_sha256={
            name: scanner.canonical_sha256(observability_doc[name])
            for name in OBSERVABILITY_PINS.component_sha256
        },
    )
    return (edge_doc, edge_pins, observed, deep_doc, deep_pins, bound_edge,
            observability_doc, observation_pins, bound_deep)


def interned_self_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    inherited = heap.native_heap_self_test()
    heap_issues = inherited_heap_issues(inherited)
    controls = inherited.get("upstream_controls")
    upstream_issues = scanner.validate_control_report(controls)
    record("preserve_all_115_native_heap_controls", not heap_issues)
    record("preserve_all_104_cmethod_controls",
           not heap.inherited_variant_issues(inherited.get("inherited_variant_controls")))
    inherited_variant = inherited.get("inherited_variant_controls")
    scanner_report = (
        inherited_variant.get("inherited_scanner_controls")
        if isinstance(inherited_variant, dict) else None
    )
    record("preserve_all_49_original_scanner_controls",
           not variants.scanner_control_issues(scanner_report))
    record("preserve_all_76_isolated_shared_controls", not upstream_issues)

    (edge_doc, edge_pins, observed, deep_doc, deep_pins, bound_edge,
     observability_doc, observation_pins, bound_deep) = synthetic_proofs()
    record("accept_complete_synthetic_interned_edge",
           validate_edge_document(edge_doc, edge_pins.compressed_sha256,
                                  observed, edge_pins)["passed"])
    record("accept_complete_synthetic_multifamily_393_proof",
           validate_deep_document(deep_doc, deep_pins.compressed_sha256,
                                  observed, bound_edge, deep_pins)["passed"])
    record("accept_complete_synthetic_multifamily_479_proof",
           validate_observability_document(
               observability_doc, observation_pins.compressed_sha256,
               observed, bound_edge, bound_deep, observation_pins
           )["passed"])

    def reject_edge(name: str, mutate: Callable[[dict[str, Any]], Any], marker: str) -> None:
        altered = copy.deepcopy(edge_doc)
        mutate(altered)
        result = validate_edge_document(altered, edge_pins.compressed_sha256,
                                         observed, edge_pins)
        record(name, not result["passed"]
               and any(marker in issue for issue in result["issues"]))

    edge_mutations: tuple[tuple[str, Callable[[dict[str, Any]], Any], str], ...] = (
        ("reject_interned_cross_candidate_edge", lambda x: x.__setitem__("module", "candidates.zig_candidate"), "module"),
        ("reject_interned_invalid_edge_schema", lambda x: x.__setitem__("schema", "foreign"), "schema"),
        ("reject_interned_wrong_edge_python", lambda x: x.__setitem__("python", "3.13.0"), "python"),
        ("reject_interned_nonzero_edge_failures", lambda x: x.__setitem__("failed", 1), "failed"),
        ("reject_interned_missing_edge_failure_rows", lambda x: x.pop("failures"), "failure"),
        ("reject_interned_nonempty_edge_failure_rows", lambda x: x.__setitem__("failures", [{"bad": True}]), "failure"),
        ("reject_interned_incomplete_223198_edge", lambda x: x.__setitem__("correctness_checks", 43), "correctness_checks"),
        ("reject_interned_boolean_edge_count", lambda x: x.__setitem__("correctness_checks", True), "correctness_checks"),
        ("reject_interned_edge_actual_digest", lambda x: x.__setitem__("actual_sha256", "0" * 64), "actual_sha256"),
        ("reject_interned_edge_expected_digest", lambda x: x.__setitem__("expected_sha256", "0" * 64), "expected_sha256"),
        ("reject_interned_edge_script_digest", lambda x: x.__setitem__("script_sha256", "0" * 64), "script_sha256"),
        ("reject_interned_edge_category_drift", lambda x: x["categories"].__setitem__("synthetic-00", 2), "categories"),
        ("reject_interned_missing_edge_category", lambda x: x["categories"].pop("synthetic-00"), "categories"),
        ("reject_interned_edge_seed_component", lambda x: x["independent_source_seeds"].__setitem__("foreign", 1), "independent_source_seeds"),
        ("reject_interned_edge_oracle_component", lambda x: x["embedded_frozen_oracles"].append({"name": "foreign"}), "embedded_frozen_oracles"),
        ("reject_interned_missing_edge_partition", lambda x: x["membership_partitions"].pop(), "partition"),
        ("reject_interned_missing_edge_artifact", lambda x: x["candidate_artifacts"].pop(), "exactly five"),
        ("reject_interned_duplicate_edge_artifact", lambda x: x["candidate_artifacts"].__setitem__(1, copy.deepcopy(x["candidate_artifacts"][0])), "duplicated"),
        ("reject_interned_changed_edge_artifact_path", lambda x: x["candidate_artifacts"][0].__setitem__("path", "candidates/foreign.py"), "path"),
        ("reject_interned_changed_edge_artifact_digest", lambda x: x["candidate_artifacts"][0].__setitem__("sha256", "0" * 64), "digest"),
        ("reject_interned_edge_holdout_access", lambda x: x.__setitem__("holdout", "ACCESSED"), "holdout"),
        ("reject_interned_edge_timing_access", lambda x: x.__setitem__("performance", "MEASURED"), "performance"),
    )
    for name, mutate, marker in edge_mutations:
        reject_edge(name, mutate, marker)

    def reject_deep(name: str, mutate: Callable[[dict[str, Any]], Any], marker: str) -> None:
        altered = copy.deepcopy(deep_doc)
        mutate(altered)
        result = validate_deep_document(
            altered, deep_pins.compressed_sha256, observed, bound_edge, deep_pins
        )
        record(name, not result["passed"]
               and any(marker in issue for issue in result["issues"]))

    deep_mutations: tuple[tuple[str, Callable[[dict[str, Any]], Any], str], ...] = (
        ("reject_interned_wrong_multifamily_deep_family", lambda x: x.__setitem__("candidate_family", "ZIG"), "candidate_family"),
        ("reject_interned_wrong_multifamily_deep_module", lambda x: x.__setitem__("candidate_module", "candidates.zig_candidate"), "candidate_module"),
        ("reject_interned_stale_43_check_deep", lambda x: x.__setitem__("checks", 43), "checks"),
        ("reject_interned_stale_32_check_deep", lambda x: x.__setitem__("checks", 32), "checks"),
        ("reject_interned_partial_392_check_deep", lambda x: x.__setitem__("checks", 392), "checks"),
        ("reject_interned_failed_deep_status", lambda x: x.__setitem__("status", "FAIL"), "status"),
        ("reject_interned_nonzero_deep_mismatch", lambda x: x.__setitem__("public_mismatch_count", 1), "public_mismatch_count"),
        ("reject_interned_missing_deep_rows", lambda x: x.pop("public_mismatches"), "mismatch"),
        ("reject_interned_deep_candidate_digest", lambda x: x.__setitem__("candidate_sha256", "0" * 64), "candidate_sha256"),
        ("reject_interned_deep_reference_digest", lambda x: x.__setitem__("reference_a_sha256", "0" * 64), "reference_a_sha256"),
        ("reject_interned_deep_missing_candidate_snapshot", lambda x: x.pop("candidate"), "candidate"),
        ("reject_interned_deep_missing_reference_snapshot", lambda x: x.pop("reference"), "reference"),
        ("reject_interned_deep_missing_independent_repeat", lambda x: x.pop("reference_independent_repeat"), "reference_independent_repeat"),
        ("reject_interned_incomplete_deep_candidate_rows", lambda x: x["candidate"]["observations"].pop(), "candidate observation rows"),
        ("reject_interned_incomplete_deep_reference_rows", lambda x: x["reference"]["observations"].pop(), "reference observation rows"),
        ("reject_interned_incomplete_deep_repeat_rows", lambda x: x["reference_independent_repeat"]["observations"].pop(), "reference_independent_repeat observation rows"),
        ("reject_interned_changed_deep_row", lambda x: x["candidate"]["observations"][0]["observation"].__setitem__("synthetic_index", -1), "row digest"),
        ("reject_interned_duplicated_deep_row", lambda x: x["candidate"]["observations"].__setitem__(1, copy.deepcopy(x["candidate"]["observations"][0])), "duplicated"),
        ("reject_interned_missing_deep_cross_family_guard", lambda x: x["cross_engine_guard_observations"].pop(), "cross_engine_guard_observations"),
        ("reject_interned_wrong_deep_cross_guard_count", lambda x: x.__setitem__("cross_engine_guard_count", 9), "cross_engine_guard_count"),
        ("reject_interned_missing_deep_candidate_cross_guard", lambda x: x["candidate"]["cross_engine_guards"].pop(), "cross-family guards"),
        ("reject_interned_missing_deep_forbidden_guard", lambda x: x["guard_observations"].pop(), "guard_observations"),
        ("reject_interned_missing_deep_candidate_guard", lambda x: x["candidate"]["guard_observations"].pop(), "forbidden-engine guards"),
        ("reject_interned_incomplete_deep_family_counts", lambda x: x["candidate"]["family_counts"].pop("synthetic-00"), "family counts"),
        ("reject_interned_missing_deep_live_artifact", lambda x: x["native_artifacts"].pop(), "exactly five"),
        ("reject_interned_missing_deep_edge", lambda x: x.pop("edge_oracle"), "edge"),
        ("reject_interned_deep_stale_edge", lambda x: x["edge_oracle"].__setitem__("archive_sha256", heap.EDGE_PINS.compressed_sha256), "archive_sha256"),
        ("reject_interned_missing_deep_private_gc", lambda x: x["implementation_private_gc_topology_differences"].pop(), "topology"),
        ("reject_interned_failed_deep_differential_poison", lambda x: x["differential_poison_self_tests"].__setitem__("missing_observation_poison", "FAIL"), "differential poison"),
    )
    for name, mutate, marker in deep_mutations:
        reject_deep(name, mutate, marker)

    def reject_observability(
        name: str, mutate: Callable[[dict[str, Any]], Any], marker: str
    ) -> None:
        altered = copy.deepcopy(observability_doc)
        mutate(altered)
        result = validate_observability_document(
            altered, observation_pins.compressed_sha256,
            observed, bound_edge, bound_deep, observation_pins
        )
        record(name, not result["passed"]
               and any(marker in issue for issue in result["issues"]))

    observation_mutations: tuple[tuple[str, Callable[[dict[str, Any]], Any], str], ...] = (
        ("reject_interned_479_wrong_candidate_family", lambda x: x.__setitem__("candidate_family", "VM"), "candidate_family"),
        ("reject_interned_479_wrong_candidate_module", lambda x: x.__setitem__("candidate_module", "candidates.vm_candidate"), "candidate_module"),
        ("reject_interned_partial_478_observability", lambda x: x.__setitem__("checks", 478), "checks"),
        ("reject_interned_stale_43_observability", lambda x: x.__setitem__("checks", 43), "checks"),
        ("reject_interned_failed_479_status", lambda x: x.__setitem__("status", "FAIL"), "status"),
        ("reject_interned_479_public_failures", lambda x: x.__setitem__("candidate_failures", 1), "candidate_failures"),
        ("reject_interned_479_nonempty_failure_rows", lambda x: x.__setitem__("failures", [{"bad": True}]), "failure"),
        ("reject_interned_479_missing_candidate_snapshot", lambda x: x.pop("candidate"), "candidate"),
        ("reject_interned_479_missing_reference_snapshot", lambda x: x.pop("reference"), "reference"),
        ("reject_interned_479_missing_independent_repeat", lambda x: x.pop("reference_independent_repeat"), "reference_independent_repeat"),
        ("reject_interned_479_partial_candidate_rows", lambda x: x["candidate"]["observations"].pop(), "candidate observation rows"),
        ("reject_interned_479_partial_reference_rows", lambda x: x["reference"]["observations"].pop(), "reference observation rows"),
        ("reject_interned_479_partial_repeat_rows", lambda x: x["reference_independent_repeat"]["observations"].pop(), "reference_independent_repeat observation rows"),
        ("reject_interned_479_changed_candidate_row", lambda x: x["candidate"]["observations"][0]["observation"].__setitem__("synthetic_index", -1), "row digest"),
        ("reject_interned_479_missing_cross_guard", lambda x: x["cross_engine_guard_observations"].pop(), "cross_engine_guard_observations"),
        ("reject_interned_479_wrong_cross_guard_count", lambda x: x.__setitem__("cross_engine_guard_count", 9), "cross_engine_guard_count"),
        ("reject_interned_479_missing_candidate_cross_guard", lambda x: x["candidate"]["cross_engine_guard_observations"].pop(), "cross-family guards"),
        ("reject_interned_479_missing_forbidden_guard", lambda x: x["forbidden_regex_guard_observations"].pop(), "forbidden_regex_guard_observations"),
        ("reject_interned_479_missing_candidate_guard", lambda x: x["candidate"]["forbidden_regex_guard_observations"].pop(), "forbidden-engine guards"),
        ("reject_interned_479_missing_private_binder", lambda x: x["private_binder_observations"].pop(), "private_binder_observations"),
        ("reject_interned_479_missing_candidate_private_binder", lambda x: x["candidate"]["private_binder_observations"].pop(), "private binder"),
        ("reject_interned_479_failed_private_binder", lambda x: x["private_binder_failures"].append({"bad": True}), "binder"),
        ("reject_interned_479_binder_digest", lambda x: x.__setitem__("private_binder_observation_sha256", "0" * 64), "private_binder_observation_sha256"),
        ("reject_interned_479_missing_native_artifact", lambda x: x["native_artifacts"].pop(), "exactly five"),
        ("reject_interned_479_missing_edge_binding", lambda x: x.pop("edge_oracle"), "edge"),
        ("reject_interned_479_stale_edge_binding", lambda x: x["edge_oracle"].__setitem__("archive_sha256", heap.EDGE_PINS.compressed_sha256), "archive_sha256"),
        ("reject_interned_479_missing_deep_binding", lambda x: x.pop("deep_proof"), "deep"),
        ("reject_interned_479_stale_deep_binding", lambda x: x["deep_proof"].__setitem__("archive_sha256", heap.DEEP_PINS.compressed_sha256), "archive_sha256"),
        ("reject_interned_479_missing_iterator_poison", lambda x: x.pop("public_iterator_controls"), "iterator"),
        ("reject_interned_479_failed_iterator_poison", lambda x: x["public_iterator_controls"]["failures"].append({"bad": True}), "iterator"),
        ("reject_interned_479_missing_poison_snapshot", lambda x: x.pop("poison"), "poison"),
        ("reject_interned_479_monitoring_bypass", lambda x: x.__setitem__("monitoring_available", False), "monitoring_available"),
        ("reject_interned_479_incomplete_family_counts", lambda x: x["family_counts"].pop("synthetic-00"), "family counts"),
    )
    for name, mutate, marker in observation_mutations:
        reject_observability(name, mutate, marker)

    for role in ARTIFACT_PATHS:
        stale = copy.deepcopy(observed)
        stale[role]["sha256"] = "0" * 64
        stale[role]["matches_frozen_edge"] = False
        one = validate_edge_document(edge_doc, edge_pins.compressed_sha256,
                                     stale, edge_pins)
        two = validate_deep_document(deep_doc, deep_pins.compressed_sha256,
                                     stale, bound_edge, deep_pins)
        three = validate_observability_document(
            observability_doc, observation_pins.compressed_sha256,
            stale, bound_edge, bound_deep, observation_pins
        )
        record("reject_interned_stale_live_" + role.replace("-", "_"),
               not one["passed"] and not two["passed"] and not three["passed"]
               and any(role in issue for issue in one["issues"]))

    for index, (role, digest) in enumerate((
        ("native-bridge", "840497035864542caf33bdc80a7c1cf5f1a31414a8bd28699536927b3a4732c8"),
        ("bridge-source", "6fc3b6f52a9e7beebfb099160f19565e8c5fb663fab899478bdc00ce9aac8ec7"),
        ("native-bridge", "4499d74edf4b3910008d7131c140c0fdf19fabe5a832fe5250b92084cb570543"),
        ("bridge-source", "f30d80b013152251481e103def2fb7ce0b7dd527a9b7c00013e61d25dc54ff04"),
        ("native-bridge", "8ca1d493f957c493c97785531b27d3356ce21cf4ed2ae3bde2713f9869f67327"),
        ("bridge-source", "8dba6d2c3b6d8c0d3c044c91a62b6e4a2664dde0df3d3d974044917c96d6a713"),
    )):
        stale = copy.deepcopy(observed)
        stale[role]["sha256"] = digest
        stale[role]["matches_frozen_edge"] = False
        result = validate_edge_document(edge_doc, edge_pins.compressed_sha256,
                                        stale, edge_pins)
        record(f"reject_interned_previous_stage_{index}_{role.replace('-', '_')}",
               digest != PINNED_ARTIFACT_HASHES[role]
               and not result["passed"]
               and any(role in issue for issue in result["issues"]))

    record("reject_interned_previous_edge_path",
           not scanner.authorized_path(heap.DEFAULT_EDGE, DEFAULT_EDGE))
    record("reject_interned_previous_deep_path",
           not scanner.authorized_path(heap.DEFAULT_DEEP, DEFAULT_DEEP))
    record("reject_interned_previous_output_path",
           not scanner.authorized_path(heap.AUTHORIZED_OUTPUT, AUTHORIZED_OUTPUT))
    record("reject_interned_wrong_interpreter",
           bool(scanner.pinned_interpreter_issues((3, 13, 0), scanner.PINNED_INTERPRETER)))

    for name, source in (
        ("reject_interned_stdlib_regex", "import re\n"),
        ("reject_interned_cpython_sre", "import _sre\n"),
        ("reject_interned_external_regex", "import regex\n"),
        ("reject_interned_cross_candidate", "from candidates import zig_candidate\n"),
        ("reject_interned_obfuscated_import", "__import__(chr(114)+chr(101))\n"),
        ("reject_interned_environment_dispatch", "import os\nos.getenv('REGEX_ENGINE')\n"),
        ("reject_interned_external_process", "import subprocess\nsubprocess.run(['engine'])\n"),
        ("reject_interned_foreign_native_loader", "import ctypes\nctypes.CDLL('foreign.so')\n"),
    ):
        record(name, not shared.analyze_python(
            source, "rust", f"<interned-synthetic:{name}>"
        )["passed"])
    for name, source, path in (
        ("reject_interned_native_pcre", "pcre2_match(p,t);", "candidates/rust/py_bridge.c"),
        ("reject_interned_native_dynamic_loader", 'dlopen("foreign.so",1);', "candidates/rust/py_bridge.c"),
        ("reject_interned_native_cpython_regex", 'PyImport_ImportModule("re");', "candidates/rust/py_bridge.c"),
        ("reject_interned_unowned_native_extern", "extern int foreign_engine(void);", "candidates/rust/py_bridge.c"),
        ("reject_interned_external_rust_crate", "extern crate regex;", "candidates/rust/src/lib.rs"),
    ):
        record(name, not shared.analyze_native(source, path, "rust")["passed"])

    clean_engine = shared.synthetic_elf(
        exported=tuple(sorted(shared.RUST_REQUIRED_EXPORTS)), needed=("libc.so.6",)
    )
    clean_bridge = shared.synthetic_elf(
        undefined=("rebar_compile", "rebar_match"),
        exported=("PyInit__rust_bridge",),
        needed=("_rust_engine.so",), runpaths=("$ORIGIN",),
    )
    record("accept_interned_owned_synthetic_elf",
           shared.analyze_rust_binaries({"engine": clean_engine,
                                         "bridge": clean_bridge})["passed"])
    for name, bridge, marker in (
        ("reject_interned_elf_compiler_bypass",
         shared.synthetic_elf(undefined=("rebar_match",),
                              exported=("PyInit__rust_bridge",),
                              needed=("_rust_engine.so",)),
         "bridge_bypasses_owned_compiler"),
        ("reject_interned_elf_executor_bypass",
         shared.synthetic_elf(undefined=("rebar_compile",),
                              exported=("PyInit__rust_bridge",),
                              needed=("_rust_engine.so",)),
         "bridge_bypasses_owned_executor"),
        ("reject_interned_cross_family_elf",
         shared.synthetic_elf(undefined=("rebar_compile", "rebar_match"),
                              exported=("PyInit__rust_bridge",),
                              needed=("_zig_probe.so",)),
         "cross_candidate_native_dependency"),
        ("reject_interned_external_regex_elf",
         shared.synthetic_elf(undefined=("rebar_compile", "rebar_match"),
                              exported=("PyInit__rust_bridge",),
                              needed=("_rust_engine.so", "libpcre2-8.so.0")),
         "external_regex_native_dependency"),
        ("reject_interned_untrusted_elf_runpath",
         shared.synthetic_elf(undefined=("rebar_compile", "rebar_match"),
                              exported=("PyInit__rust_bridge",),
                              needed=("_rust_engine.so",),
                              runpaths=("/tmp/foreign",)),
         "untrusted_native_runpath"),
    ):
        result = shared.analyze_rust_binaries({"engine": clean_engine, "bridge": bridge})
        record(name, not result["passed"]
               and any(issue.get("code") == marker for issue in result["issues"]))

    def mapping(path: Path | str) -> str:
        return f"00400000-00401000 r-xp 00000000 00:00 0 {path}\n"

    own = (mapping(shared.NATIVE_BINARIES["rust"]["engine"])
           + mapping(shared.NATIVE_BINARIES["rust"]["bridge"]))
    record("accept_interned_exact_owned_synthetic_mappings",
           shared.classify_mapping_snapshot(own, "rust")["passed"])
    for name, text in (
        ("reject_interned_cross_family_mapping",
         own + mapping(ROOT / "candidates" / "_zig_probe.so")),
        ("reject_interned_external_regex_mapping",
         own + mapping("/usr/lib/libpcre2-8.so.0")),
        ("reject_interned_unapproved_mapping",
         own + mapping(ROOT / "candidates" / "_foreign.so")),
        ("reject_interned_deleted_engine_mapping",
         mapping(str(shared.NATIVE_BINARIES["rust"]["engine"]) + " (deleted)")
         + mapping(shared.NATIVE_BINARIES["rust"]["bridge"])),
        ("reject_interned_missing_bridge_mapping",
         mapping(shared.NATIVE_BINARIES["rust"]["engine"])),
    ):
        record(name, not shared.classify_mapping_snapshot(text, "rust")["passed"])

    if not upstream_issues and isinstance(controls, dict):
        for name, mutate in (
            ("reject_interned_corrupted_76_control_count",
             lambda x: x.__setitem__("check_count", 75)),
            ("reject_interned_bypassed_shared_control",
             lambda x: x["checks"][0].__setitem__("passed", False)),
            ("reject_interned_unisolated_shared_controls",
             lambda x: x["execution"].__setitem__("isolated_subprocess", False)),
        ):
            altered = copy.deepcopy(controls)
            mutate(altered)
            record(name, bool(scanner.validate_control_report(altered)))
    else:
        for name in ("reject_interned_corrupted_76_control_count",
                     "reject_interned_bypassed_shared_control",
                     "reject_interned_unisolated_shared_controls"):
            record(name, False)

    names = [item["name"] for item in checks]
    negative = sum(name.startswith("reject_") for name in names)
    failed = [item["name"] for item in checks if not item["passed"]]
    if len(names) != len(set(names)):
        failed.append("duplicate_interned_self_test_name")
    if negative < MINIMUM_INTERNED_NEGATIVE_CONTROLS:
        failed.append("insufficient_interned_negative_controls")
    return {
        "passed": not failed, "checks": checks, "check_count": len(checks),
        "negative_control_count": negative,
        "minimum_negative_control_count": MINIMUM_INTERNED_NEGATIVE_CONTROLS,
        "failed": failed, "fixture_storage": "in-memory only",
        "inherited_heap_controls": inherited,
        "inherited_heap_control_issues": heap_issues,
        "upstream_controls": controls,
        "upstream_control_issues": upstream_issues,
    }


def isolated_interned_self_test() -> dict[str, Any]:
    command = [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--self-test"]

    def reject(reason: str) -> dict[str, Any]:
        return {
            "passed": False, "checks": [], "check_count": 0,
            "negative_control_count": 0,
            "minimum_negative_control_count": MINIMUM_INTERNED_NEGATIVE_CONTROLS,
            "failed": [reason], "fixture_storage": "in-memory only",
            "inherited_heap_controls": {"passed": False, "check_count": 0},
            "inherited_heap_control_issues": [reason],
            "upstream_controls": {"passed": False, "check_count": 0},
            "upstream_control_issues": [reason],
            "execution": {"isolated_subprocess": True, "validated": False},
        }

    try:
        process = subprocess.run(command, capture_output=True, text=True,
                                 check=False, timeout=30)
    except (OSError, subprocess.SubprocessError) as error:
        return reject(f"isolated interned-attribute controls failed: {error}")
    size = len(process.stdout.encode("utf-8"))
    if (size > shared.MAX_WORKER_RESPONSE_BYTES
            or len(process.stderr.encode("utf-8")) > shared.MAX_WORKER_RESPONSE_BYTES):
        return reject("isolated interned control output exceeds its hard bound")
    if process.returncode or process.stderr:
        return reject("isolated interned-attribute controls did not terminate cleanly")
    lines = process.stdout.splitlines()
    if len(lines) != 1:
        return reject("isolated interned controls must emit exactly one JSON line")
    try:
        result = json.loads(lines[0])
    except (TypeError, json.JSONDecodeError) as error:
        return reject(f"invalid isolated interned control JSON: {error}")
    if not isinstance(result, dict):
        return reject("isolated interned controls returned a non-object")
    checks = result.get("checks")
    if (result.get("passed") is not True or result.get("failed") != []
            or result.get("fixture_storage") != "in-memory only"
            or not isinstance(checks, list)
            or result.get("check_count") != len(checks)
            or result.get("negative_control_count", 0)
            < MINIMUM_INTERNED_NEGATIVE_CONTROLS
            or result.get("minimum_negative_control_count")
            != MINIMUM_INTERNED_NEGATIVE_CONTROLS):
        return reject("isolated interned controls failed or have an invalid schema")
    names: set[str] = set()
    for item in checks:
        if (not isinstance(item, dict) or set(item) != {"name", "passed"}
                or not isinstance(item.get("name"), str)
                or item.get("passed") is not True or item["name"] in names):
            return reject("an isolated interned control is malformed or duplicated")
        names.add(item["name"])
    if sum(name.startswith("reject_") for name in names) != result.get("negative_control_count"):
        return reject("isolated interned negative-control count is invalid")
    if inherited_heap_issues(result.get("inherited_heap_controls")):
        return reject("isolated interned audit did not preserve all 115 heap controls")
    if result.get("inherited_heap_control_issues") != []:
        return reject("isolated interned audit reports inherited heap failures")
    if scanner.validate_control_report(result.get("upstream_controls")):
        return reject("isolated interned audit did not preserve all 76 shared controls")
    if result.get("upstream_control_issues") != []:
        return reject("isolated interned audit reports shared control failures")
    result["execution"] = {
        "isolated_subprocess": True, "interpreter": sys.executable,
        "exit_code": process.returncode, "response_bytes": size,
        "maximum_response_bytes": shared.MAX_WORKER_RESPONSE_BYTES,
        "validated": True,
    }
    return result


def run_interned_audit(
    edge_path: Path, deep_path: Path, observability_path: Path
) -> dict[str, Any]:
    interpreter_issues = scanner.pinned_interpreter_issues()
    tests = isolated_interned_self_test()
    prior = validate_prior_certificates()
    observed, artifact_issues = observe_artifacts()
    edge = load_edge(edge_path, observed)
    deep = load_deep(deep_path, observed, edge)
    observability = load_observability(observability_path, observed, edge, deep)
    source_issues: list[str] = []
    python_path = shared.PYTHON_SOURCES["rust"]
    try:
        source = python_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        source = ""
        source_issues.append(f"owned Rust Python source is unreadable: {error}")
    python_result = shared.analyze_python(source, "rust", scanner.relative(python_path))
    tree = python_result.pop("tree", None)

    native: dict[str, str] = {}
    native_results: list[dict[str, Any]] = []
    for path in shared.NATIVE_SOURCES["rust"]:
        relative = scanner.relative(path)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            source_issues.append(f"owned Rust source {relative} is unreadable: {error}")
            native_results.append({"passed": False, "file": relative,
                                   "issues": [str(error)]})
            continue
        native[relative] = text
        checked = shared.analyze_native(text, relative, "rust")
        checked["file"] = relative
        checked["sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        native_results.append(checked)
    pipeline = (
        shared.verify_pipeline("rust", tree, native)
        if tree is not None and all(scanner.relative(path) in native
                                    for path in shared.NATIVE_SOURCES["rust"])
        else {"passed": False, "issues": ["the owned Rust compiler pipeline is incomplete"]}
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
        else {"passed": False, "issues": ["owned zero-dependency manifests are incomplete"]}
    )
    binaries: dict[str, bytes] = {}
    for role, path in shared.NATIVE_BINARIES["rust"].items():
        try:
            binaries[role] = scanner.bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            source_issues.append(f"owned Rust {role} ELF is unreadable: {error}")
    elf = shared.analyze_rust_binaries(binaries)
    runtime = (
        shared.isolated_probe("rust", elf["files"])
        if elf["passed"] and python_result["passed"] and pipeline["passed"]
        else {"passed": False, "skipped": "owned Rust source, compiler, or ELF failed"}
    )
    mappings = runtime.get("native_mapping_provenance", {})
    heap_issues = inherited_heap_issues(tests.get("inherited_heap_controls"))
    upstream_issues = scanner.validate_control_report(tests.get("upstream_controls"))
    passed = (
        not interpreter_issues and tests["passed"] and not heap_issues
        and not upstream_issues and prior["passed"] and not artifact_issues
        and edge["passed"] and deep["passed"] and observability["passed"]
        and not source_issues and python_result["passed"]
        and len(native_results) == len(shared.NATIVE_SOURCES["rust"])
        and all(item["passed"] for item in native_results)
        and pipeline["passed"] and manifests["passed"] and elf["passed"]
        and runtime["passed"] and mappings.get("passed") is True
        and mappings.get("expected_owned_mapping_count") == 2
        and mappings.get("observed_owned_mapping_count") == 2
    )
    return {
        "schema_version": 1,
        "audit": "rust-v8-interned-attributes-from-scratch-provenance",
        "module": "candidates.rust_candidate",
        "passed": bool(passed), "result": "PASS" if passed else "FAIL",
        "pinned_interpreter": {
            "expected_version": list(scanner.PINNED_VERSION),
            "actual_version": list(sys.version_info[:3]),
            "expected_executable": str(scanner.PINNED_INTERPRETER),
            "actual_executable": sys.executable,
            "passed": not interpreter_issues, "issues": interpreter_issues,
        },
        "edge_oracle": edge,
        "deep_contract_proof": deep,
        "qualified_observability_proof": observability,
        "frozen_live_artifacts": {
            "passed": not artifact_issues,
            "expected_count": len(ARTIFACT_PATHS),
            "observed_count": len(observed),
            "artifacts": [observed[name] for name in sorted(observed)],
            "issues": artifact_issues,
        },
        "prior_stage_certificates": prior,
        "python_source": {
            "file": scanner.relative(python_path),
            "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            **python_result,
        },
        "native_sources": native_results,
        "owned_pipeline": pipeline,
        "manifest_provenance": manifests,
        "rust_native_elf_provenance": elf,
        "isolated_runtime": runtime,
        "runtime_native_mapping_provenance": mappings,
        "self_test": tests,
        "inherited_native_heap_poison_controls": {
            "passed": not heap_issues,
            "expected_count": EXPECTED_HEAP_CONTROL_COUNT,
            "expected_negative_count": EXPECTED_HEAP_NEGATIVE_COUNT,
            "validated_count": tests.get("inherited_heap_controls", {}).get("check_count", 0),
            "issues": heap_issues,
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
            "variant": "native-interned-attribute-names",
            "other_candidate_production_sources_read": False,
            "other_candidate_native_binaries_read": False,
            "native_elf_paths": [scanner.relative(path)
                                 for path in shared.NATIVE_BINARIES["rust"].values()],
            "immutable_edge_oracle": scanner.relative(DEFAULT_EDGE),
            "immutable_multifamily_deep_proof": scanner.relative(DEFAULT_DEEP),
            "immutable_qualified_observability_proof": scanner.relative(DEFAULT_OBSERVABILITY),
            "benchmark_or_timing_executed": False,
            "holdout_accessed": False,
            "full_campaign_evidence_accessed": False,
            "synthetic_malicious_fixtures": "in-memory only",
            "minimum_interned_negative_controls": MINIMUM_INTERNED_NEGATIVE_CONTROLS,
            "maximum_compressed_evidence_bytes": heap.MAX_COMPRESSED_BYTES,
            "maximum_decompressed_evidence_bytes": heap.MAX_JSON_BYTES,
        },
        "limitations": [
            "The pinned 223198-case edge, three complete 393-row multifamily contract snapshots, and three complete 479-row qualified-observability snapshots are independently validated but not rerun.",
            "All 13 forbidden-engine guards and all 10 cross-family guards are mandatory in both complete current Rust deep and observability proofs.",
            "The certificate binds the five current Rust artifacts, all six owned Rust native sources, zero-external-dependency manifests, and two independently hashed actually mapped Rust ELF binaries.",
            "All original scanner, cmethod, and native-heap auditors and reports remain independently hash-pinned and immutable.",
            "The 22-family campaign digest is not independently certified because no campaign artifact path is authorized or accessed by this Rust-only gate.",
            "Static source and isolated mapped-runtime evidence do not prove unexercised future execution paths.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="run exclusively isolated in-memory interned poison controls")
    parser.add_argument("--edge-oracle", type=Path, default=DEFAULT_EDGE,
                        help="the single frozen interned-attribute Rust edge")
    parser.add_argument("--deep-proof", type=Path, default=DEFAULT_DEEP,
                        help="the complete frozen 393-check multifamily Rust deep proof")
    parser.add_argument("--observability-proof", type=Path, default=DEFAULT_OBSERVABILITY,
                        help="the complete frozen 479-check qualified Rust proof")
    parser.add_argument("--output", type=Path, default=AUTHORIZED_OUTPUT,
                        help="the unique authorized additive interned-attribute report")
    args = parser.parse_args(argv)
    interpreter_issues = scanner.pinned_interpreter_issues()
    if interpreter_issues:
        print(json.dumps({"passed": False, "result": "FAIL", "issues": interpreter_issues},
                         sort_keys=True))
        return 1
    if not scanner.authorized_path(args.output, AUTHORIZED_OUTPUT):
        parser.error("only candidates/audits/RUST-V8-INTERNED-ATTRIBUTES-FROM-SCRATCH.json is authorized")
    if not scanner.authorized_path(args.edge_oracle, DEFAULT_EDGE):
        parser.error("only the exact interned-attribute Rust edge archive is authorized")
    if not scanner.authorized_path(args.deep_proof, DEFAULT_DEEP):
        parser.error("only the exact complete interned-attribute multifamily deep proof is authorized")
    if not scanner.authorized_path(args.observability_proof, DEFAULT_OBSERVABILITY):
        parser.error("only the exact complete interned-attribute qualified 479 proof is authorized")
    if args.self_test:
        report = interned_self_test()
        print(json.dumps(report, sort_keys=True))
        return 0 if report["passed"] else 1
    report = run_interned_audit(args.edge_oracle, args.deep_proof,
                                 args.observability_proof)
    if report["passed"]:
        AUTHORIZED_OUTPUT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    summary: dict[str, Any] = {
        "passed": report["passed"], "result": report["result"],
        "module": report["module"],
        "correctness_checks": report["edge_oracle"].get("correctness_checks"),
        "edge_failed": report["edge_oracle"].get("failed"),
        "edge_oracle_passed": report["edge_oracle"]["passed"],
        "deep_checks": report["deep_contract_proof"].get("checks"),
        "deep_public_mismatches": report["deep_contract_proof"].get("public_mismatch_count"),
        "deep_contract_passed": report["deep_contract_proof"]["passed"],
        "deep_complete_rows": report["deep_contract_proof"].get(
            "complete_observation_rows_per_snapshot", []
        ),
        "observability_checks": report["qualified_observability_proof"].get("checks"),
        "observability_failures": report["qualified_observability_proof"].get("candidate_failures"),
        "observability_passed": report["qualified_observability_proof"]["passed"],
        "observability_complete_rows": report["qualified_observability_proof"].get(
            "complete_observation_rows_per_snapshot", []
        ),
        "cross_engine_guards": report["deep_contract_proof"].get("cross_engine_guard_count"),
        "forbidden_regex_guards": report["deep_contract_proof"].get("forbidden_regex_guards"),
        "artifact_count": report["frozen_live_artifacts"]["observed_count"],
        "artifacts_passed": report["frozen_live_artifacts"]["passed"],
        "prior_stage_artifacts_passed": report["prior_stage_certificates"]["passed"],
        "source_passed": report["python_source"]["passed"],
        "native_sources_passed": all(x["passed"] for x in report["native_sources"]),
        "pipeline_passed": report["owned_pipeline"]["passed"],
        "manifest_passed": report["manifest_provenance"]["passed"],
        "rust_native_elf_passed": report["rust_native_elf_provenance"]["passed"],
        "rust_actual_mappings_passed": report["runtime_native_mapping_provenance"].get("passed", False),
        "isolated_runtime_passed": report["isolated_runtime"]["passed"],
        "interned_self_test_checks": report["self_test"]["check_count"],
        "interned_negative_controls": report["self_test"]["negative_control_count"],
        "inherited_native_heap_controls": report[
            "inherited_native_heap_poison_controls"
        ]["validated_count"],
        "upstream_poison_controls": report["upstream_poison_controls"]["validated_count"],
        "report": scanner.relative(AUTHORIZED_OUTPUT),
    }
    if not report["passed"]:
        summary["issues"] = (
            report["pinned_interpreter"]["issues"]
            + report["edge_oracle"]["issues"]
            + report["deep_contract_proof"]["issues"]
            + report["qualified_observability_proof"]["issues"]
            + report["frozen_live_artifacts"]["issues"]
            + report["prior_stage_certificates"]["issues"]
            + report["inherited_native_heap_poison_controls"]["issues"]
            + report["upstream_poison_controls"]["issues"]
            + report["input_issues"]
            + report["self_test"].get("failed", [])
        )
    print(json.dumps(summary, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
