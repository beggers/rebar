#!/usr/bin/env python3
"""Bounded Rust-only provenance gate for the independently frozen native heap."""

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
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import audit_from_scratch as shared
from tools import audit_rust_from_scratch as scanner
from tools import audit_rust_variants_from_scratch as variants


DEFAULT_EDGE = (
    ROOT / "candidates" / "evidence" / "rust-v8-edge-oracle-rust-native-heap-final.json.gz"
)
DEFAULT_DEEP = (
    ROOT / "candidates" / "audits" / "RUST-V8-DEEP-CONTRACT-NATIVE-HEAP-FINAL.json.gz"
)
AUTHORIZED_OUTPUT = (
    ROOT / "candidates" / "audits" / "RUST-V8-NATIVE-HEAP-FROM-SCRATCH.json"
)
MAX_COMPRESSED_BYTES = 16 * 1024 * 1024
MAX_JSON_BYTES = 32 * 1024 * 1024
EDGE_CHECK_COUNT = 223198
EDGE_CATEGORY_COUNT = 49
DEEP_CHECK_COUNT = 393
DEEP_GUARD_COUNT = 13
DEEP_FAMILY_COUNT = 21
EXPECTED_VARIANT_CONTROL_COUNT = 104
EXPECTED_VARIANT_NEGATIVE_COUNT = 99
EXPECTED_SCANNER_CONTROL_COUNT = 49
EXPECTED_UPSTREAM_CONTROL_COUNT = 76
MINIMUM_NATIVE_HEAP_NEGATIVE_CONTROLS = 49

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
    "native-bridge": "840497035864542caf33bdc80a7c1cf5f1a31414a8bd28699536927b3a4732c8",
    "native-engine": "890f9e34e966244067a3dc173c2276043ae15d4830a05228fb37ec2571aa17cd",
    "native-source": "a2fa04912bb1f6957f833560446f4d3d1c5d13df8b5efac992fa63e28803668b",
    "bridge-source": "6fc3b6f52a9e7beebfb099160f19565e8c5fb663fab899478bdc00ce9aac8ec7",
}

EDGE_PINS = scanner.EdgePins(
    compressed_sha256="0c8748f78809e0f29f4bbacaad48296d4f51ca14445a4f9e8938376b37d85a21",
    result_sha256="b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526",
    script_sha256="fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca",
    component_sha256={
        "candidate_artifacts": "463076b18c1ca413259d700224c60ff9d990e3379e10516438141b80200c9359",
        "categories": "99a76d581e3fd8b68239867722a032e6f67701524896ec75684e11184f721ca8",
        "embedded_frozen_oracles": "7ba1fe99e4fd8389e1a4116c85c611ad847dcb41478d367c6ca059f24b57d4bc",
        "independent_source_seeds": "10b94594042987a1e9229b782bcdc9ce5d7d0543e91a203df18fef5733416bb0",
        "json_normalization": "62c42c6358643a3f99ff9cf4721059c8425965c59aec25c49b4efbd0219b4544",
        "membership_partitions": "785157a16916365ec6d9c6516a0c13499dca10c50ef4d2a988f2d145e69a9855",
    },
)


@dataclass(frozen=True)
class DeepPins:
    compressed_sha256: str
    document_sha256: str
    observation_sha256: str
    fixture_sha256: str
    suite_sha256: str
    component_sha256: dict[str, str]


DEEP_PINS = DeepPins(
    compressed_sha256="f31ec92ffa7975406267ee9cdb29e2a3e0314d436d643ccfb34862f09956c2c5",
    document_sha256="841191fb4704f12b07e31231de5d20663d069f2eacb77d90927a3cc0ff42381b",
    observation_sha256="b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8",
    fixture_sha256="c72a5e47f15c94ce13ce34d4918c05ef81eea5b010ac119b255264e60939ef16",
    suite_sha256="ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978",
    component_sha256={
        "candidate": "f08224f9b6d494921a08887466a0aa66481353d5a0cb706406f9a6dfc6ceaaa4",
        "differential_poison_self_tests": "f23f83fb8ce0e57fcf8a10b9470413b6c3d990812579eaaa906cd11259e692b5",
        "edge_oracle": "da79e3f9ba08486d55267e0df30d21176af6c058bbfb84b531081928a29f16be",
        "frozen_failure_evidence": "e04bc22376c1b340716606f328fd2159ef12eb25aaf04a3604fc09d8e63a7246",
        "guard_observations": "475b0d1c0feca44e158cdf050a63da17c27c852db93ca0d9e0387463a0f99f5c",
        "implementation_private_gc_topology_differences": "55754ce8c8cb8665fe4ad5212511882e97e0e8503c49eeb63045ae4ab2a2d652",
        "native_artifacts": "302105309470f31a63806e56aa8dada3dac57171bceb21dee7ec8ad42d6ac3ec",
        "native_under_poison": "5994d57987f56611abf5212d8d1dfb4951947bd3221214b82e5fd335a66ca50d",
        "public_mismatch_family_counts": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        "public_mismatches": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "reference": "6e1ea37bf3cd3907da4b3a1679bd81a79f9218c31ac192dbea56cff2902ad88a",
        "reference_independent_repeat": "9693fb77da9ff4fa6c1e0c4be8353a1cc735bfab14c825bc5dcd6f8ce3e5757f",
        "stdlib_vs_stdlib_mismatches": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "variant_runner": "0f1b451354cbd69315e5d765cc5fa10cdf78bdfa312ed932358b8ade4c48f754",
    },
)

PRIOR_STAGE_CERTIFICATES = {
    "scanner-auditor": (
        ROOT / "tools" / "audit_rust_from_scratch.py",
        "31e8db794c36b083b4ab0a75b96d0ac6e73eb13c0d0b601a42dcbbed28ce1475",
    ),
    "scanner-report": (
        ROOT / "candidates" / "audits" / "RUST-V8-SCANNER-FROM-SCRATCH.json",
        "d761686c7a4cb2f5b65ddae37272bd5f644894eb157fb9b56735e6747685f70b",
    ),
    "cmethod-auditor": (
        ROOT / "tools" / "audit_rust_variants_from_scratch.py",
        "fca9cd90cf7a74a3bebc4e30c8d05a77a0a42f27d4b7836e73c1f9822fd78998",
    ),
    "cmethod-report": (
        ROOT / "candidates" / "audits" / "RUST-V8-CMETHOD-FROM-SCRATCH.json",
        "2c18f7797d91fcb507043bff13fa166deb952ad9abf1c82455ac8712fe70390a",
    ),
}


def observe_artifacts() -> tuple[dict[str, dict[str, Any]], list[str]]:
    observed: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for role, path in ARTIFACT_PATHS.items():
        try:
            data = scanner.bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            issues.append(f"unreadable native-heap Rust {role}: {error}")
            continue
        actual = hashlib.sha256(data).hexdigest()
        expected = PINNED_ARTIFACT_HASHES[role]
        matches = actual == expected
        if not matches:
            issues.append(f"native-heap Rust {role} differs from its frozen artifact")
        observed[role] = {
            "role": role,
            "path": scanner.relative(path),
            "sha256": actual,
            "expected_sha256": expected,
            "matches_frozen_edge": matches,
        }
    if set(observed) != set(ARTIFACT_PATHS):
        issues.append("the native-heap Rust variant must expose exactly five artifacts")
    return observed, issues


def check_artifact_rows(
    rows: Any,
    observed: dict[str, dict[str, Any]],
    label: str,
) -> tuple[set[str], list[str]]:
    issues: list[str] = []
    roles: set[str] = set()
    if not isinstance(rows, list) or len(rows) != len(ARTIFACT_PATHS):
        return roles, [f"{label} must contain exactly five frozen Rust artifacts"]
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
        expected_sha256 = PINNED_ARTIFACT_HASHES[role]
        if item["path"] != expected_path:
            issues.append(f"{label} frozen {role} artifact path changed")
        if item["sha256"] != expected_sha256:
            issues.append(f"{label} frozen {role} artifact digest changed")
        live = observed.get(role)
        if (
            not isinstance(live, dict)
            or live.get("path") != expected_path
            or live.get("sha256") != expected_sha256
            or live.get("matches_frozen_edge") is not True
        ):
            issues.append(f"{label} live {role} differs from its frozen artifact")
    if roles != set(ARTIFACT_PATHS):
        issues.append(f"{label} Rust artifact roles are incomplete")
    return roles, issues


def validate_edge_document(
    document: Any,
    archive_sha256: str,
    observed: dict[str, dict[str, Any]],
    pins: scanner.EdgePins = EDGE_PINS,
) -> dict[str, Any]:
    issues: list[str] = []
    if archive_sha256 != pins.compressed_sha256:
        issues.append("the frozen native-heap edge archive SHA-256 changed")
    if not isinstance(document, dict):
        return {"passed": False, "issues": issues + ["edge JSON is not an object"],
                "archive_sha256": archive_sha256, "correctness_checks": None,
                "artifact_count": 0}
    expected: dict[str, Any] = {
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
    for name, value in expected.items():
        actual = document.get(name)
        if type(actual) is not type(value) or actual != value:
            issues.append(f"the frozen native-heap edge field {name!r} changed")
    if document.get("failures") != []:
        issues.append("native-heap edge failures must be present and empty")
    categories = document.get("categories")
    if not isinstance(categories, dict) or len(categories) != EDGE_CATEGORY_COUNT:
        issues.append("the native-heap edge requires exactly 49 categories")
    elif any(type(count) is not int or count < 0 for count in categories.values()):
        issues.append("a native-heap edge category count is malformed")
    elif sum(categories.values()) != EDGE_CHECK_COUNT:
        issues.append("native-heap edge categories must sum to 223198")
    component_hashes: dict[str, str] = {}
    for name, expected_digest in pins.component_sha256.items():
        if name not in document:
            issues.append(f"native-heap edge component {name!r} is missing")
            continue
        try:
            actual = scanner.canonical_sha256(document[name])
        except (TypeError, ValueError, UnicodeError) as error:
            issues.append(f"native-heap edge component {name!r} is invalid: {error}")
            continue
        component_hashes[name] = actual
        if actual != expected_digest:
            issues.append(f"frozen native-heap edge component {name!r} changed")
    roles, artifact_issues = check_artifact_rows(
        document.get("candidate_artifacts"), observed, "native-heap edge"
    )
    issues.extend(artifact_issues)
    partitions = document.get("membership_partitions")
    if not isinstance(partitions, list) or len(partitions) != 4:
        issues.append("native-heap edge requires exactly four membership partitions")
    else:
        for item in partitions:
            if (
                not isinstance(item, dict)
                or item.get("actual_sha256") != item.get("expected_sha256")
                or item.get("stride") != 4099
            ):
                issues.append("native-heap edge membership evidence is mismatched")
    return {
        "passed": not issues,
        "issues": issues,
        "file": scanner.relative(DEFAULT_EDGE),
        "archive_sha256": archive_sha256,
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
            and all(type(x) is int for x in categories.values())
            else None
        ),
        "artifact_count": len(roles),
        "canonical_component_sha256": component_hashes,
        "holdout": document.get("holdout"),
        "performance": document.get("performance"),
    }


def validate_deep_document(
    document: Any,
    archive_sha256: str,
    observed: dict[str, dict[str, Any]],
    edge: dict[str, Any],
    pins: DeepPins = DEEP_PINS,
) -> dict[str, Any]:
    issues: list[str] = []
    if archive_sha256 != pins.compressed_sha256:
        issues.append("the frozen 393-check native-heap deep archive SHA-256 changed")
    if not isinstance(document, dict):
        return {"passed": False, "issues": issues + ["deep proof JSON is not an object"],
                "archive_sha256": archive_sha256, "checks": None,
                "public_mismatch_count": None, "artifact_count": 0}
    required: dict[str, Any] = {
        "schema": "rebar-rust-v8-deep-public-contract-v1",
        "python": "3.14.6",
        "status": "PASS",
        "checks": DEEP_CHECK_COUNT,
        "public_mismatch_count": 0,
        "candidate_sha256": pins.observation_sha256,
        "reference_a_sha256": pins.observation_sha256,
        "reference_b_sha256": pins.observation_sha256,
        "fixture_sha256": pins.fixture_sha256,
        "suite_sha256": pins.suite_sha256,
        "forbidden_regex_guards": DEEP_GUARD_COUNT,
        "seed": 2026072347,
        "seeded_case_count": 64,
        "implementation_private_gc_topology_difference_count": 36,
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }
    for name, expected in required.items():
        actual = document.get(name)
        if type(actual) is not type(expected) or actual != expected:
            issues.append(f"the frozen 393-check deep field {name!r} changed")
    try:
        canonical_digest = scanner.canonical_sha256(document)
    except (TypeError, ValueError, UnicodeError) as error:
        canonical_digest = None
        issues.append(f"the complete frozen 393-check deep proof is invalid: {error}")
    if canonical_digest != pins.document_sha256:
        issues.append("the complete frozen 393-check deep proof canonical digest changed")
    component_hashes: dict[str, str] = {}
    for name, expected in pins.component_sha256.items():
        if name not in document:
            issues.append(f"frozen 393-check deep component {name!r} is missing")
            continue
        try:
            digest = scanner.canonical_sha256(document[name])
        except (TypeError, ValueError, UnicodeError) as error:
            issues.append(f"frozen 393-check deep component {name!r} is invalid: {error}")
            continue
        component_hashes[name] = digest
        if digest != expected:
            issues.append(f"frozen 393-check deep component {name!r} changed")

    if document.get("public_mismatches") != []:
        issues.append("the 393-check deep public mismatch rows must be empty")
    if document.get("stdlib_vs_stdlib_mismatches") != []:
        issues.append("the independent reference mismatch rows must be empty")
    if document.get("public_mismatch_family_counts") != {}:
        issues.append("the 393-check deep mismatch family counts must be empty")
    guards = document.get("guard_observations")
    if not isinstance(guards, list) or len(guards) != DEEP_GUARD_COUNT:
        issues.append("the 393-check deep proof requires exactly 13 forbidden-engine guards")
    differences = document.get("implementation_private_gc_topology_differences")
    if not isinstance(differences, list) or len(differences) != 36:
        issues.append("all 36 private GC-topology diagnostics must be explicitly retained")

    roles, artifact_issues = check_artifact_rows(
        document.get("native_artifacts"), observed, "393-check deep proof"
    )
    issues.extend(artifact_issues)
    candidate = document.get("candidate")
    reference = document.get("reference")
    repeat = document.get("reference_independent_repeat")
    snapshots = (
        ("candidate", candidate, "candidate", DEEP_GUARD_COUNT),
        ("reference", reference, "stdlib-a", 0),
        ("reference_independent_repeat", repeat, "stdlib-b", 0),
    )
    observation_lists: list[list[Any]] = []
    for label, snapshot, expected_role, expected_guards in snapshots:
        if not isinstance(snapshot, dict):
            issues.append(f"the frozen 393-check {label} snapshot is missing")
            continue
        snapshot_required = {
            "schema": "rebar-rust-v8-deep-public-contract-v1",
            "python": "3.14.6",
            "role": expected_role,
            "checks": DEEP_CHECK_COUNT,
            "fixture_sha256": pins.fixture_sha256,
            "observation_sha256": pins.observation_sha256,
            "guard_count": expected_guards,
            "seed": 2026072347,
            "holdout": "NOT ACCESSED",
            "performance": "NOT MEASURED",
        }
        for name, expected in snapshot_required.items():
            actual = snapshot.get(name)
            if type(actual) is not type(expected) or actual != expected:
                issues.append(f"393-check {label} snapshot field {name!r} changed")
        rows = snapshot.get("observations")
        if not isinstance(rows, list) or len(rows) != DEEP_CHECK_COUNT:
            issues.append(f"393-check {label} observations are incomplete")
        else:
            observation_lists.append(rows)
            ids: set[str] = set()
            for row in rows:
                if (
                    not isinstance(row, dict)
                    or set(row) != {"family", "id", "observation", "sha256"}
                    or not isinstance(row.get("id"), str)
                    or row["id"] in ids
                ):
                    issues.append(f"393-check {label} observation row is malformed or duplicated")
                    break
                ids.add(row["id"])
                if row.get("sha256") != scanner.canonical_sha256(row.get("observation")):
                    issues.append(f"393-check {label} observation row digest changed")
                    break
            if scanner.canonical_sha256(rows) != pins.observation_sha256:
                issues.append(f"393-check {label} observation-list digest changed")
        counts = snapshot.get("family_counts")
        if (
            not isinstance(counts, dict)
            or len(counts) != DEEP_FAMILY_COUNT
            or any(type(value) is not int or value < 0 for value in counts.values())
            or sum(counts.values()) != DEEP_CHECK_COUNT
        ):
            issues.append(f"393-check {label} family counts are incomplete")
        snapshot_guards = snapshot.get("guard_observations")
        if not isinstance(snapshot_guards, list) or len(snapshot_guards) != expected_guards:
            issues.append(f"393-check {label} forbidden-engine guards are incomplete")
        if label == "candidate" and snapshot.get("native_artifacts") != document.get("native_artifacts"):
            issues.append("393-check candidate native artifacts do not bind to live Rust")
    if len(observation_lists) != 3 or not (
        observation_lists[0] == observation_lists[1] == observation_lists[2]
    ):
        issues.append("all three complete 393-row observation snapshots must agree")

    binding = document.get("edge_oracle")
    if not isinstance(binding, dict):
        issues.append("the deep proof does not contain an immutable edge binding")
    else:
        binding_expected = {
            "schema": "rebar-v7-independent-edge-oracle-v1",
            "path": str(DEFAULT_EDGE),
            "archive_sha256": EDGE_PINS.compressed_sha256,
            "checks": EDGE_CHECK_COUNT,
            "failed": 0,
            "category_count": EDGE_CATEGORY_COUNT,
            "candidate_sha256": EDGE_PINS.result_sha256,
            "reference_sha256": EDGE_PINS.result_sha256,
            "script_sha256": EDGE_PINS.script_sha256,
        }
        for name, expected in binding_expected.items():
            actual = binding.get(name)
            if type(actual) is not type(expected) or actual != expected:
                issues.append(f"393-check deep-to-edge binding field {name!r} changed")
        if not edge.get("passed"):
            issues.append("the independently validated bound edge did not pass")
        elif binding.get("archive_sha256") != edge.get("archive_sha256"):
            issues.append("the deep proof binds to a stale native-heap edge archive")
        _, bound_issues = check_artifact_rows(
            binding.get("candidate_artifacts"), observed, "393-check deep-to-edge binding"
        )
        issues.extend(bound_issues)
        if binding.get("candidate_artifacts") != document.get("native_artifacts"):
            issues.append("the 393-check deep and edge live-artifact bindings disagree")

    differential = document.get("differential_poison_self_tests")
    if (
        not isinstance(differential, dict)
        or set(differential) != {
            "changed_observation_poison", "identical_reference", "missing_observation_poison"
        }
        or any(value != "PASS" for value in differential.values())
    ):
        issues.append("the 393-check independent differential poison controls failed")

    return {
        "passed": not issues,
        "issues": issues,
        "file": scanner.relative(DEFAULT_DEEP),
        "archive_sha256": archive_sha256,
        "expected_archive_sha256": pins.compressed_sha256,
        "canonical_sha256": canonical_digest,
        "expected_canonical_sha256": pins.document_sha256,
        "schema": document.get("schema"),
        "status": document.get("status"),
        "checks": document.get("checks"),
        "public_mismatch_count": document.get("public_mismatch_count"),
        "guard_count": document.get("forbidden_regex_guards"),
        "artifact_count": len(roles),
        "reference_snapshot_count": len(observation_lists),
        "complete_observation_rows_per_snapshot": (
            [len(rows) for rows in observation_lists]
        ),
        "canonical_component_sha256": component_hashes,
        "edge_archive_sha256": (
            binding.get("archive_sha256") if isinstance(binding, dict) else None
        ),
        "holdout": document.get("holdout"),
        "performance": document.get("performance"),
    }


def decode_pinned_gzip(
    compressed: bytes,
    expected_sha256: str,
    label: str,
) -> tuple[Any | None, str, list[str]]:
    digest = hashlib.sha256(compressed).hexdigest()
    if len(compressed) > MAX_COMPRESSED_BYTES:
        return None, digest, [f"the {label} archive exceeds the hard compressed bound"]
    if digest != expected_sha256:
        return None, digest, [f"the frozen {label} archive SHA-256 changed"]
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as archive:
            decoded = archive.read(MAX_JSON_BYTES + 1)
        if len(decoded) > MAX_JSON_BYTES:
            raise ValueError("decompressed JSON exceeds the hard bound")
        return json.loads(decoded), digest, []
    except (EOFError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        return None, digest, [f"invalid bounded {label} gzip or JSON: {error}"]


def load_edge(path: Path, observed: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if not scanner.authorized_path(path, DEFAULT_EDGE):
        return {"passed": False, "issues": ["only the authorized native-heap edge may be read"],
                "correctness_checks": None, "artifact_count": 0}
    try:
        compressed = scanner.bounded_binary(DEFAULT_EDGE, MAX_COMPRESSED_BYTES)
    except (OSError, ValueError) as error:
        return {"passed": False, "issues": [f"the native-heap edge is unreadable: {error}"],
                "correctness_checks": None, "artifact_count": 0}
    document, digest, issues = decode_pinned_gzip(
        compressed, EDGE_PINS.compressed_sha256, "native-heap edge"
    )
    if issues:
        return {"passed": False, "issues": issues, "archive_sha256": digest,
                "correctness_checks": None, "artifact_count": 0}
    return validate_edge_document(document, digest, observed)


def load_deep(
    path: Path,
    observed: dict[str, dict[str, Any]],
    edge: dict[str, Any],
) -> dict[str, Any]:
    if not scanner.authorized_path(path, DEFAULT_DEEP):
        return {"passed": False, "issues": ["only the authorized native-heap deep proof may be read"],
                "checks": None, "public_mismatch_count": None, "artifact_count": 0}
    try:
        compressed = scanner.bounded_binary(DEFAULT_DEEP, MAX_COMPRESSED_BYTES)
    except (OSError, ValueError) as error:
        return {"passed": False, "issues": [f"the native-heap deep proof is unreadable: {error}"],
                "checks": None, "public_mismatch_count": None, "artifact_count": 0}
    document, digest, issues = decode_pinned_gzip(
        compressed, DEEP_PINS.compressed_sha256, "393-check native-heap deep proof"
    )
    if issues:
        return {"passed": False, "issues": issues, "archive_sha256": digest,
                "checks": None, "public_mismatch_count": None, "artifact_count": 0}
    return validate_deep_document(document, digest, observed, edge)


def validate_prior_certificates() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    issues: list[str] = []
    for role, (path, expected) in PRIOR_STAGE_CERTIFICATES.items():
        try:
            data = scanner.bounded_binary(path, shared.MAX_ELF_BYTES)
        except (OSError, ValueError) as error:
            issues.append(f"the immutable prior {role} is unreadable: {error}")
            continue
        actual = hashlib.sha256(data).hexdigest()
        matches = actual == expected
        if not matches:
            issues.append(f"the immutable prior {role} was modified")
        rows.append({
            "role": role,
            "path": scanner.relative(path),
            "sha256": actual,
            "expected_sha256": expected,
            "matches": matches,
        })
    if len(rows) != len(PRIOR_STAGE_CERTIFICATES):
        issues.append("all four scanner and cmethod auditor/report certificates are required")
    return {"passed": not issues, "expected_count": len(PRIOR_STAGE_CERTIFICATES),
            "observed_count": len(rows), "artifacts": rows, "issues": issues}


def inherited_variant_issues(report: Any) -> list[str]:
    if not isinstance(report, dict):
        return ["the inherited cmethod control report is not an object"]
    checks = report.get("checks")
    issues: list[str] = []
    if (
        report.get("passed") is not True
        or report.get("failed") != []
        or report.get("fixture_storage") != "in-memory only"
        or not isinstance(checks, list)
        or len(checks) != EXPECTED_VARIANT_CONTROL_COUNT
        or report.get("check_count") != EXPECTED_VARIANT_CONTROL_COUNT
        or report.get("negative_control_count") != EXPECTED_VARIANT_NEGATIVE_COUNT
    ):
        issues.append("the complete inherited 104 cmethod controls did not pass")
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
                issues.append("an inherited cmethod control is malformed or failed")
                break
            names.add(item["name"])
        if sum(name.startswith("reject_") for name in names) != EXPECTED_VARIANT_NEGATIVE_COUNT:
            issues.append("the exact inherited 99 cmethod negative controls changed")
    issues.extend(variants.scanner_control_issues(report.get("inherited_scanner_controls")))
    issues.extend(scanner.validate_control_report(report.get("upstream_controls")))
    if report.get("inherited_scanner_control_issues") != []:
        issues.append("the inherited 49 scanner controls contain failures")
    if report.get("upstream_control_issues") != []:
        issues.append("the inherited 76 isolated shared controls contain failures")
    return issues


def synthetic_evidence() -> tuple[
    dict[str, Any], scanner.EdgePins, dict[str, dict[str, Any]],
    dict[str, Any], DeepPins, dict[str, Any]
]:
    artifacts = [
        {"role": role, "path": scanner.relative(path),
         "sha256": PINNED_ARTIFACT_HASHES[role]}
        for role, path in ARTIFACT_PATHS.items()
    ]
    observed = {
        row["role"]: {**row, "expected_sha256": row["sha256"],
                      "matches_frozen_edge": True}
        for row in artifacts
    }
    categories = {f"synthetic-{index:02d}": 1 for index in range(48)}
    categories["synthetic-48"] = EDGE_CHECK_COUNT - 48
    partitions = [
        {"partition": str(index), "stride": 4099,
         "actual_sha256": hashlib.sha256(str(index).encode()).hexdigest(),
         "expected_sha256": hashlib.sha256(str(index).encode()).hexdigest()}
        for index in range(4)
    ]
    edge_document: dict[str, Any] = {
        "schema": "rebar-v7-independent-edge-oracle-v1",
        "module": "candidates.rust_candidate",
        "python": "3.14.6",
        "correctness_checks": EDGE_CHECK_COUNT,
        "failed": 0,
        "failures": [],
        "expected_sha256": EDGE_PINS.result_sha256,
        "actual_sha256": EDGE_PINS.result_sha256,
        "script_sha256": EDGE_PINS.script_sha256,
        "candidate_artifacts": artifacts,
        "categories": categories,
        "embedded_frozen_oracles": [{"name": "synthetic"}],
        "independent_source_seeds": {"synthetic": 1},
        "json_normalization": {"synthetic": "canonical"},
        "membership_partitions": partitions,
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }
    edge_archive = gzip.compress(
        json.dumps(edge_document, sort_keys=True, separators=(",", ":")).encode(),
        mtime=0,
    )
    edge_pins = scanner.EdgePins(
        compressed_sha256=hashlib.sha256(edge_archive).hexdigest(),
        result_sha256=EDGE_PINS.result_sha256,
        script_sha256=EDGE_PINS.script_sha256,
        component_sha256={
            name: scanner.canonical_sha256(edge_document[name])
            for name in EDGE_PINS.component_sha256
        },
    )
    edge_result = validate_edge_document(
        edge_document, edge_pins.compressed_sha256, observed, edge_pins
    )

    observations = []
    for index in range(DEEP_CHECK_COUNT):
        observation = {"synthetic_index": index}
        observations.append({
            "family": f"synthetic-{index % DEEP_FAMILY_COUNT:02d}",
            "id": f"native-heap-{index:03d}",
            "observation": observation,
            "sha256": scanner.canonical_sha256(observation),
        })
    observation_digest = scanner.canonical_sha256(observations)
    family_counts = {
        f"synthetic-{index:02d}": sum(
            row["family"] == f"synthetic-{index:02d}" for row in observations
        )
        for index in range(DEEP_FAMILY_COUNT)
    }
    guard_rows = [{"name": f"guard-{index}"} for index in range(DEEP_GUARD_COUNT)]
    private_rows = [{"index": index} for index in range(64)]

    def snapshot(role: str, guards: list[dict[str, Any]], native: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "schema": "rebar-rust-v8-deep-public-contract-v1",
            "python": "3.14.6",
            "role": role,
            "checks": DEEP_CHECK_COUNT,
            "fixture_sha256": DEEP_PINS.fixture_sha256,
            "observation_sha256": observation_digest,
            "observations": copy.deepcopy(observations),
            "family_counts": copy.deepcopy(family_counts),
            "guard_count": len(guards),
            "guard_observations": copy.deepcopy(guards),
            "native_artifacts": copy.deepcopy(native),
            "implementation_private_gc_diagnostics": copy.deepcopy(private_rows),
            "seed": 2026072347,
            "holdout": "NOT ACCESSED",
            "performance": "NOT MEASURED",
        }

    deep_document: dict[str, Any] = {
        "schema": "rebar-rust-v8-deep-public-contract-v1",
        "python": "3.14.6",
        "status": "PASS",
        "checks": DEEP_CHECK_COUNT,
        "public_mismatch_count": 0,
        "candidate_sha256": observation_digest,
        "reference_a_sha256": observation_digest,
        "reference_b_sha256": observation_digest,
        "fixture_sha256": DEEP_PINS.fixture_sha256,
        "suite_sha256": DEEP_PINS.suite_sha256,
        "forbidden_regex_guards": DEEP_GUARD_COUNT,
        "seed": 2026072347,
        "seeded_case_count": 64,
        "implementation_private_gc_topology_difference_count": 36,
        "implementation_private_gc_topology_differences": [
            {"index": index, "classification": "private"} for index in range(36)
        ],
        "guard_observations": copy.deepcopy(guard_rows),
        "native_artifacts": copy.deepcopy(artifacts),
        "candidate": snapshot("candidate", guard_rows, artifacts),
        "reference": snapshot("stdlib-a", [], []),
        "reference_independent_repeat": snapshot("stdlib-b", [], []),
        "public_mismatch_family_counts": {},
        "public_mismatches": [],
        "stdlib_vs_stdlib_mismatches": [],
        "differential_poison_self_tests": {
            "changed_observation_poison": "PASS",
            "identical_reference": "PASS",
            "missing_observation_poison": "PASS",
        },
        "native_under_poison": {"search": {"status": "value"}, "sub": {"status": "value"}},
        "frozen_failure_evidence": {"status": "FAIL", "public_mismatch_count": 104},
        "variant_runner": {"path": "tools/synthetic-native-heap.py", "sha256": "a" * 64},
        "edge_oracle": {
            "schema": "rebar-v7-independent-edge-oracle-v1",
            "path": str(DEFAULT_EDGE),
            "archive_sha256": EDGE_PINS.compressed_sha256,
            "checks": EDGE_CHECK_COUNT,
            "failed": 0,
            "category_count": EDGE_CATEGORY_COUNT,
            "candidate_sha256": EDGE_PINS.result_sha256,
            "reference_sha256": EDGE_PINS.result_sha256,
            "script_sha256": EDGE_PINS.script_sha256,
            "candidate_artifacts": copy.deepcopy(artifacts),
        },
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }
    deep_archive = gzip.compress(
        json.dumps(deep_document, sort_keys=True, separators=(",", ":")).encode(),
        mtime=0,
    )
    deep_pins = DeepPins(
        compressed_sha256=hashlib.sha256(deep_archive).hexdigest(),
        document_sha256=scanner.canonical_sha256(deep_document),
        observation_sha256=observation_digest,
        fixture_sha256=DEEP_PINS.fixture_sha256,
        suite_sha256=DEEP_PINS.suite_sha256,
        component_sha256={
            name: scanner.canonical_sha256(deep_document[name])
            for name in DEEP_PINS.component_sha256
        },
    )
    bound_edge = dict(edge_result)
    bound_edge["archive_sha256"] = EDGE_PINS.compressed_sha256
    return edge_document, edge_pins, observed, deep_document, deep_pins, bound_edge


def native_heap_self_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    inherited = variants.variant_self_test()
    inherited_issues = inherited_variant_issues(inherited)
    controls = inherited.get("upstream_controls")
    upstream_issues = scanner.validate_control_report(controls)
    record("preserve_all_104_cmethod_variant_controls", not inherited_issues)
    record("preserve_all_49_original_scanner_controls",
           not variants.scanner_control_issues(inherited.get("inherited_scanner_controls")))
    record("preserve_all_76_isolated_shared_poison_controls", not upstream_issues)

    edge_doc, edge_pins, observed, deep_doc, deep_pins, bound_edge = synthetic_evidence()
    record(
        "accept_complete_synthetic_native_heap_edge",
        validate_edge_document(edge_doc, edge_pins.compressed_sha256, observed, edge_pins)["passed"],
    )
    record(
        "accept_complete_synthetic_393_row_native_heap_deep_proof",
        validate_deep_document(deep_doc, deep_pins.compressed_sha256, observed,
                               bound_edge, deep_pins)["passed"],
    )

    def reject_edge(name: str, mutate: Callable[[dict[str, Any]], Any], marker: str) -> None:
        altered = copy.deepcopy(edge_doc)
        mutate(altered)
        result = validate_edge_document(altered, edge_pins.compressed_sha256, observed, edge_pins)
        record(name, not result["passed"] and any(marker in x for x in result["issues"]))

    edge_mutations: tuple[tuple[str, Callable[[dict[str, Any]], Any], str], ...] = (
        ("reject_native_heap_wrong_edge_module", lambda x: x.__setitem__("module", "candidates.vm_candidate"), "module"),
        ("reject_native_heap_wrong_edge_schema", lambda x: x.__setitem__("schema", "untrusted"), "schema"),
        ("reject_native_heap_wrong_edge_python", lambda x: x.__setitem__("python", "3.13.0"), "python"),
        ("reject_native_heap_nonzero_edge_failures", lambda x: x.__setitem__("failed", 1), "failed"),
        ("reject_native_heap_boolean_edge_failure_count", lambda x: x.__setitem__("failed", False), "failed"),
        ("reject_native_heap_missing_edge_failure_rows", lambda x: x.pop("failures"), "failures"),
        ("reject_native_heap_nonempty_edge_failure_rows", lambda x: x.__setitem__("failures", [{"bad": True}]), "failures"),
        ("reject_native_heap_incomplete_edge_count", lambda x: x.__setitem__("correctness_checks", 43), "correctness_checks"),
        ("reject_native_heap_previous_32_edge_stage", lambda x: x.__setitem__("correctness_checks", 32), "correctness_checks"),
        ("reject_native_heap_boolean_edge_count", lambda x: x.__setitem__("correctness_checks", True), "correctness_checks"),
        ("reject_native_heap_edge_result_digest", lambda x: x.__setitem__("actual_sha256", "0" * 64), "actual_sha256"),
        ("reject_native_heap_edge_reference_digest", lambda x: x.__setitem__("expected_sha256", "0" * 64), "expected_sha256"),
        ("reject_native_heap_edge_script_digest", lambda x: x.__setitem__("script_sha256", "0" * 64), "script_sha256"),
        ("reject_native_heap_edge_category_drift", lambda x: x["categories"].__setitem__("synthetic-00", 2), "categories"),
        ("reject_native_heap_missing_edge_category", lambda x: x["categories"].pop("synthetic-00"), "categories"),
        ("reject_native_heap_edge_oracle_component", lambda x: x["embedded_frozen_oracles"].append({"name": "foreign"}), "embedded_frozen_oracles"),
        ("reject_native_heap_edge_seed_component", lambda x: x["independent_source_seeds"].__setitem__("foreign", 1), "independent_source_seeds"),
        ("reject_native_heap_edge_normalization", lambda x: x["json_normalization"].__setitem__("foreign", True), "json_normalization"),
        ("reject_native_heap_edge_membership_digest", lambda x: x["membership_partitions"][0].__setitem__("actual_sha256", "0" * 64), "membership"),
        ("reject_native_heap_missing_edge_partition", lambda x: x["membership_partitions"].pop(), "membership"),
        ("reject_native_heap_edge_holdout_access", lambda x: x.__setitem__("holdout", "ACCESSED"), "holdout"),
        ("reject_native_heap_edge_timing_access", lambda x: x.__setitem__("performance", "MEASURED"), "performance"),
        ("reject_native_heap_missing_edge_artifact", lambda x: x["candidate_artifacts"].pop(), "exactly five"),
        ("reject_native_heap_duplicate_edge_artifact", lambda x: x["candidate_artifacts"].__setitem__(1, copy.deepcopy(x["candidate_artifacts"][0])), "duplicated"),
        ("reject_native_heap_changed_edge_artifact_path", lambda x: x["candidate_artifacts"][0].__setitem__("path", "candidates/foreign.py"), "path"),
        ("reject_native_heap_changed_edge_artifact_digest", lambda x: x["candidate_artifacts"][0].__setitem__("sha256", "0" * 64), "digest"),
    )
    for name, mutate, marker in edge_mutations:
        reject_edge(name, mutate, marker)

    def reject_deep(name: str, mutate: Callable[[dict[str, Any]], Any], marker: str) -> None:
        altered = copy.deepcopy(deep_doc)
        mutate(altered)
        result = validate_deep_document(
            altered, deep_pins.compressed_sha256, observed, bound_edge, deep_pins
        )
        record(name, not result["passed"] and any(marker in x for x in result["issues"]))

    deep_mutations: tuple[tuple[str, Callable[[dict[str, Any]], Any], str], ...] = (
        ("reject_native_heap_previous_43_check_deep_proof", lambda x: x.__setitem__("checks", 43), "checks"),
        ("reject_native_heap_previous_32_check_deep_proof", lambda x: x.__setitem__("checks", 32), "checks"),
        ("reject_native_heap_previous_392_check_deep_proof", lambda x: x.__setitem__("checks", 392), "checks"),
        ("reject_native_heap_boolean_deep_check_count", lambda x: x.__setitem__("checks", True), "checks"),
        ("reject_native_heap_failed_deep_status", lambda x: x.__setitem__("status", "FAIL"), "status"),
        ("reject_native_heap_nonzero_public_mismatches", lambda x: x.__setitem__("public_mismatch_count", 1), "public_mismatch_count"),
        ("reject_native_heap_missing_deep_public_rows", lambda x: x.pop("public_mismatches"), "public mismatch"),
        ("reject_native_heap_nonempty_deep_public_rows", lambda x: x.__setitem__("public_mismatches", [{"bad": True}]), "public mismatch"),
        ("reject_native_heap_missing_stdlib_repeat_rows", lambda x: x.pop("stdlib_vs_stdlib_mismatches"), "reference mismatch"),
        ("reject_native_heap_deep_candidate_digest", lambda x: x.__setitem__("candidate_sha256", "0" * 64), "candidate_sha256"),
        ("reject_native_heap_deep_first_reference_digest", lambda x: x.__setitem__("reference_a_sha256", "0" * 64), "reference_a_sha256"),
        ("reject_native_heap_deep_repeat_reference_digest", lambda x: x.__setitem__("reference_b_sha256", "0" * 64), "reference_b_sha256"),
        ("reject_native_heap_deep_fixture_digest", lambda x: x.__setitem__("fixture_sha256", "0" * 64), "fixture_sha256"),
        ("reject_native_heap_deep_suite_digest", lambda x: x.__setitem__("suite_sha256", "0" * 64), "suite_sha256"),
        ("reject_native_heap_deep_missing_candidate_snapshot", lambda x: x.pop("candidate"), "candidate"),
        ("reject_native_heap_deep_missing_reference_snapshot", lambda x: x.pop("reference"), "reference"),
        ("reject_native_heap_deep_missing_independent_reference", lambda x: x.pop("reference_independent_repeat"), "reference_independent_repeat"),
        ("reject_native_heap_incomplete_candidate_393_rows", lambda x: x["candidate"]["observations"].pop(), "candidate observations"),
        ("reject_native_heap_incomplete_reference_393_rows", lambda x: x["reference"]["observations"].pop(), "reference observations"),
        ("reject_native_heap_incomplete_repeat_393_rows", lambda x: x["reference_independent_repeat"]["observations"].pop(), "reference_independent_repeat observations"),
        ("reject_native_heap_changed_candidate_observation", lambda x: x["candidate"]["observations"][0]["observation"].__setitem__("synthetic_index", -1), "observation row digest"),
        ("reject_native_heap_duplicate_candidate_observation", lambda x: x["candidate"]["observations"].__setitem__(1, copy.deepcopy(x["candidate"]["observations"][0])), "duplicated"),
        ("reject_native_heap_missing_candidate_observation_digest", lambda x: x["candidate"]["observations"][0].pop("sha256"), "malformed"),
        ("reject_native_heap_incomplete_family_counts", lambda x: x["candidate"]["family_counts"].pop("synthetic-00"), "family counts"),
        ("reject_native_heap_negative_family_counts", lambda x: x["candidate"]["family_counts"].__setitem__("synthetic-00", -1), "family counts"),
        ("reject_native_heap_missing_forbidden_engine_guard", lambda x: x["guard_observations"].pop(), "guards"),
        ("reject_native_heap_changed_guard_count", lambda x: x.__setitem__("forbidden_regex_guards", 12), "forbidden_regex_guards"),
        ("reject_native_heap_missing_candidate_guard", lambda x: x["candidate"]["guard_observations"].pop(), "candidate forbidden-engine guards"),
        ("reject_native_heap_missing_private_gc_diagnostics", lambda x: x["implementation_private_gc_topology_differences"].pop(), "GC-topology"),
        ("reject_native_heap_missing_deep_native_artifact", lambda x: x["native_artifacts"].pop(), "exactly five"),
        ("reject_native_heap_changed_deep_native_bridge", lambda x: x["native_artifacts"][1].__setitem__("sha256", "0" * 64), "native-bridge"),
        ("reject_native_heap_missing_deep_edge_binding", lambda x: x.pop("edge_oracle"), "edge"),
        ("reject_native_heap_stale_deep_edge_digest", lambda x: x["edge_oracle"].__setitem__("archive_sha256", variants.EDGE_PINS.compressed_sha256), "archive_sha256"),
        ("reject_native_heap_stale_deep_edge_count", lambda x: x["edge_oracle"].__setitem__("checks", 43), "checks"),
        ("reject_native_heap_incomplete_bound_edge_artifacts", lambda x: x["edge_oracle"]["candidate_artifacts"].pop(), "exactly five"),
        ("reject_native_heap_changed_differential_poison", lambda x: x["differential_poison_self_tests"].__setitem__("missing_observation_poison", "FAIL"), "differential poison"),
        ("reject_native_heap_missing_differential_poison", lambda x: x["differential_poison_self_tests"].pop("missing_observation_poison"), "differential poison"),
        ("reject_native_heap_deep_holdout_access", lambda x: x.__setitem__("holdout", "ACCESSED"), "holdout"),
        ("reject_native_heap_deep_timing_access", lambda x: x.__setitem__("performance", "MEASURED"), "performance"),
        ("reject_native_heap_changed_seed", lambda x: x.__setitem__("seed", 1), "seed"),
    )
    for name, mutate, marker in deep_mutations:
        reject_deep(name, mutate, marker)

    for role in ARTIFACT_PATHS:
        altered = copy.deepcopy(observed)
        altered[role]["sha256"] = "0" * 64
        altered[role]["matches_frozen_edge"] = False
        edge_result = validate_edge_document(
            edge_doc, edge_pins.compressed_sha256, altered, edge_pins
        )
        deep_result = validate_deep_document(
            deep_doc, deep_pins.compressed_sha256, altered, bound_edge, deep_pins
        )
        record(
            "reject_native_heap_stale_live_" + role.replace("-", "_"),
            not edge_result["passed"] and not deep_result["passed"]
            and any(role in issue for issue in edge_result["issues"]),
        )

    previous_artifacts = (
        ("public-python", "1111a419d65d44775d1f4b0cb6a728dea8de44a592597341596533351c16018e"),
        ("native-bridge", "8ca1d493f957c493c97785531b27d3356ce21cf4ed2ae3bde2713f9869f67327"),
        ("bridge-source", "8dba6d2c3b6d8c0d3c044c91a62b6e4a2664dde0df3d3d974044917c96d6a713"),
        ("native-bridge", "a1cf1384d20e20a8a744ead2a5952457d04c3a49d118ca87cd7977700d068073"),
        ("bridge-source", "6aca53810d44cea6321f1e229b71fb41c60742a51da75ca2243604a60468134f"),
        ("native-bridge", "4499d74edf4b3910008d7131c140c0fdf19fabe5a832fe5250b92084cb570543"),
        ("bridge-source", "f30d80b013152251481e103def2fb7ce0b7dd527a9b7c00013e61d25dc54ff04"),
    )
    for index, (role, old_digest) in enumerate(previous_artifacts):
        altered = copy.deepcopy(observed)
        altered[role]["sha256"] = old_digest
        altered[role]["matches_frozen_edge"] = False
        result = validate_edge_document(edge_doc, edge_pins.compressed_sha256,
                                        altered, edge_pins)
        record(
            f"reject_native_heap_prior_stage_{index}_{role.replace('-', '_')}",
            old_digest != PINNED_ARTIFACT_HASHES[role]
            and not result["passed"]
            and any(role in issue for issue in result["issues"]),
        )

    record("reject_native_heap_wrong_edge_path",
           not scanner.authorized_path(variants.DEFAULT_EDGE, DEFAULT_EDGE))
    record("reject_native_heap_wrong_deep_path",
           not scanner.authorized_path(
               ROOT / "candidates" / "audits" / "RUST-V8-DEEP-CONTRACT.json.gz",
               DEFAULT_DEEP,
           ))
    record("reject_native_heap_previous_output_path",
           not scanner.authorized_path(variants.AUTHORIZED_OUTPUT, AUTHORIZED_OUTPUT))
    record("reject_native_heap_wrong_interpreter",
           bool(scanner.pinned_interpreter_issues((3, 13, 0), scanner.PINNED_INTERPRETER)))

    python_fixtures = (
        ("reject_native_heap_stdlib_regex", "import re\n"),
        ("reject_native_heap_cpython_sre", "import _sre\n"),
        ("reject_native_heap_external_regex", "import regex\n"),
        ("reject_native_heap_cross_candidate", "from candidates import vm_candidate\n"),
        ("reject_native_heap_dynamic_import", "__import__(chr(114)+chr(101))\n"),
        ("reject_native_heap_environment_dispatch", "import os\nos.getenv('REGEX_ENGINE')\n"),
        ("reject_native_heap_external_process", "import subprocess\nsubprocess.run(['engine'])\n"),
        ("reject_native_heap_foreign_native_loader", "import ctypes\nctypes.CDLL('foreign.so')\n"),
    )
    for name, source in python_fixtures:
        record(name, not shared.analyze_python(
            source, "rust", f"<native-heap-synthetic:{name}>"
        )["passed"])
    native_fixtures = (
        ("reject_native_heap_native_pcre", "pcre2_match(pattern,text);", "candidates/rust/py_bridge.c"),
        ("reject_native_heap_native_dynamic_loader", 'dlopen("foreign.so",1);', "candidates/rust/py_bridge.c"),
        ("reject_native_heap_native_cpython_re", 'PyImport_ImportModule("re");', "candidates/rust/py_bridge.c"),
        ("reject_native_heap_unowned_native_extern", "extern int foreign_engine(void);", "candidates/rust/py_bridge.c"),
        ("reject_native_heap_external_rust_crate", "extern crate regex;", "candidates/rust/src/lib.rs"),
    )
    for name, source, source_path in native_fixtures:
        record(name, not shared.analyze_native(source, source_path, "rust")["passed"])

    clean_engine = shared.synthetic_elf(
        exported=tuple(sorted(shared.RUST_REQUIRED_EXPORTS)), needed=("libc.so.6",)
    )
    clean_bridge = shared.synthetic_elf(
        undefined=("rebar_compile", "rebar_match"),
        exported=("PyInit__rust_bridge",),
        needed=("_rust_engine.so",),
        runpaths=("$ORIGIN",),
    )
    record("accept_native_heap_owned_synthetic_elf",
           shared.analyze_rust_binaries({"engine": clean_engine,
                                         "bridge": clean_bridge})["passed"])
    for name, bridge, marker in (
        (
            "reject_native_heap_elf_compiler_bypass",
            shared.synthetic_elf(undefined=("rebar_match",),
                exported=("PyInit__rust_bridge",), needed=("_rust_engine.so",)),
            "bridge_bypasses_owned_compiler",
        ),
        (
            "reject_native_heap_elf_executor_bypass",
            shared.synthetic_elf(undefined=("rebar_compile",),
                exported=("PyInit__rust_bridge",), needed=("_rust_engine.so",)),
            "bridge_bypasses_owned_executor",
        ),
        (
            "reject_native_heap_cross_family_native_elf",
            shared.synthetic_elf(undefined=("rebar_compile", "rebar_match"),
                exported=("PyInit__rust_bridge",), needed=("_zig_probe.so",)),
            "cross_candidate_native_dependency",
        ),
        (
            "reject_native_heap_external_regex_elf",
            shared.synthetic_elf(undefined=("rebar_compile", "rebar_match"),
                exported=("PyInit__rust_bridge",),
                needed=("_rust_engine.so", "libpcre2-8.so.0")),
            "external_regex_native_dependency",
        ),
        (
            "reject_native_heap_untrusted_elf_runpath",
            shared.synthetic_elf(undefined=("rebar_compile", "rebar_match"),
                exported=("PyInit__rust_bridge",), needed=("_rust_engine.so",),
                runpaths=("/tmp/foreign",)),
            "untrusted_native_runpath",
        ),
    ):
        result = shared.analyze_rust_binaries({"engine": clean_engine, "bridge": bridge})
        record(name, not result["passed"]
               and any(issue.get("code") == marker for issue in result["issues"]))

    def mapping(path: Path | str) -> str:
        return f"00400000-00401000 r-xp 00000000 00:00 0 {path}\n"

    owned_maps = (mapping(shared.NATIVE_BINARIES["rust"]["engine"])
                  + mapping(shared.NATIVE_BINARIES["rust"]["bridge"]))
    record("accept_native_heap_exact_owned_synthetic_maps",
           shared.classify_mapping_snapshot(owned_maps, "rust")["passed"])
    for name, map_text in (
        ("reject_native_heap_cross_family_memory_mapping",
         owned_maps + mapping(ROOT / "candidates" / "_zig_probe.so")),
        ("reject_native_heap_external_regex_memory_mapping",
         owned_maps + mapping("/usr/lib/libpcre2-8.so.0")),
        ("reject_native_heap_unapproved_memory_mapping",
         owned_maps + mapping(ROOT / "candidates" / "_foreign_engine.so")),
        ("reject_native_heap_deleted_engine_memory_mapping",
         mapping(str(shared.NATIVE_BINARIES["rust"]["engine"]) + " (deleted)")
         + mapping(shared.NATIVE_BINARIES["rust"]["bridge"])),
        ("reject_native_heap_missing_bridge_memory_mapping",
         mapping(shared.NATIVE_BINARIES["rust"]["engine"])),
    ):
        record(name, not shared.classify_mapping_snapshot(map_text, "rust")["passed"])

    if not upstream_issues and isinstance(controls, dict):
        for name, mutate in (
            ("reject_native_heap_corrupted_76_control_count",
             lambda x: x.__setitem__("check_count", 75)),
            ("reject_native_heap_bypassed_shared_control",
             lambda x: x["checks"][0].__setitem__("passed", False)),
            ("reject_native_heap_unisolated_shared_controls",
             lambda x: x["execution"].__setitem__("isolated_subprocess", False)),
        ):
            altered = copy.deepcopy(controls)
            mutate(altered)
            record(name, bool(scanner.validate_control_report(altered)))
    else:
        for name in ("reject_native_heap_corrupted_76_control_count",
                     "reject_native_heap_bypassed_shared_control",
                     "reject_native_heap_unisolated_shared_controls"):
            record(name, False)

    names = [item["name"] for item in checks]
    negative_count = sum(name.startswith("reject_") for name in names)
    failures = [item["name"] for item in checks if not item["passed"]]
    if len(names) != len(set(names)):
        failures.append("duplicate_native_heap_self_test_name")
    if negative_count < MINIMUM_NATIVE_HEAP_NEGATIVE_CONTROLS:
        failures.append("insufficient_native_heap_negative_controls")
    return {
        "passed": not failures,
        "checks": checks,
        "check_count": len(checks),
        "negative_control_count": negative_count,
        "minimum_negative_control_count": MINIMUM_NATIVE_HEAP_NEGATIVE_CONTROLS,
        "failed": failures,
        "fixture_storage": "in-memory only",
        "inherited_variant_controls": inherited,
        "inherited_variant_control_issues": inherited_issues,
        "upstream_controls": controls,
        "upstream_control_issues": upstream_issues,
    }


def isolated_native_heap_self_test() -> dict[str, Any]:
    command = [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--self-test"]

    def reject(reason: str) -> dict[str, Any]:
        return {
            "passed": False, "checks": [], "check_count": 0,
            "negative_control_count": 0,
            "minimum_negative_control_count": MINIMUM_NATIVE_HEAP_NEGATIVE_CONTROLS,
            "failed": [reason], "fixture_storage": "in-memory only",
            "inherited_variant_controls": {"passed": False, "check_count": 0},
            "inherited_variant_control_issues": [reason],
            "upstream_controls": {"passed": False, "check_count": 0},
            "upstream_control_issues": [reason],
            "execution": {"isolated_subprocess": True, "validated": False},
        }

    try:
        process = subprocess.run(command, capture_output=True, text=True,
                                 check=False, timeout=30)
    except (OSError, subprocess.SubprocessError) as error:
        return reject(f"isolated native-heap control execution failed: {error}")
    stdout_size = len(process.stdout.encode("utf-8"))
    if (stdout_size > shared.MAX_WORKER_RESPONSE_BYTES
            or len(process.stderr.encode("utf-8")) > shared.MAX_WORKER_RESPONSE_BYTES):
        return reject("the isolated native-heap control response exceeds its hard bound")
    if process.returncode or process.stderr:
        return reject("the isolated native-heap controls did not finish cleanly")
    lines = process.stdout.splitlines()
    if len(lines) != 1:
        return reject("isolated native-heap controls must produce exactly one JSON line")
    try:
        result = json.loads(lines[0])
    except (TypeError, json.JSONDecodeError) as error:
        return reject(f"invalid isolated native-heap control JSON: {error}")
    if not isinstance(result, dict):
        return reject("the isolated native-heap controls returned a non-object")
    checks = result.get("checks")
    if (
        result.get("passed") is not True
        or result.get("failed") != []
        or result.get("fixture_storage") != "in-memory only"
        or not isinstance(checks, list)
        or result.get("check_count") != len(checks)
        or result.get("negative_control_count", 0) < MINIMUM_NATIVE_HEAP_NEGATIVE_CONTROLS
        or result.get("minimum_negative_control_count") != MINIMUM_NATIVE_HEAP_NEGATIVE_CONTROLS
    ):
        return reject("isolated native-heap controls failed or their schema is invalid")
    names: set[str] = set()
    for item in checks:
        if (not isinstance(item, dict) or set(item) != {"name", "passed"}
                or not isinstance(item.get("name"), str)
                or item.get("passed") is not True or item["name"] in names):
            return reject("an isolated native-heap control is invalid or duplicated")
        names.add(item["name"])
    if sum(name.startswith("reject_") for name in names) != result.get("negative_control_count"):
        return reject("the isolated native-heap negative-control count is invalid")
    if inherited_variant_issues(result.get("inherited_variant_controls")):
        return reject("the isolated native-heap gate did not retain all 104 prior controls")
    if result.get("inherited_variant_control_issues") != []:
        return reject("the inherited native-heap variant controls report failures")
    if scanner.validate_control_report(result.get("upstream_controls")):
        return reject("the isolated native-heap gate did not retain all 76 shared controls")
    if result.get("upstream_control_issues") != []:
        return reject("the native-heap upstream control report contains failures")
    result["execution"] = {
        "isolated_subprocess": True, "interpreter": sys.executable,
        "exit_code": process.returncode, "response_bytes": stdout_size,
        "maximum_response_bytes": shared.MAX_WORKER_RESPONSE_BYTES,
        "validated": True,
    }
    return result


def run_native_heap_audit(edge_path: Path, deep_path: Path) -> dict[str, Any]:
    interpreter_issues = scanner.pinned_interpreter_issues()
    tests = isolated_native_heap_self_test()
    prior = validate_prior_certificates()
    observed, artifact_issues = observe_artifacts()
    edge = load_edge(edge_path, observed)
    deep = load_deep(deep_path, observed, edge)
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
    native_sources: dict[str, str] = {}
    native_results: list[dict[str, Any]] = []
    for path in shared.NATIVE_SOURCES["rust"]:
        relative_path = scanner.relative(path)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            source_issues.append(f"owned Rust source {relative_path} is unreadable: {error}")
            native_results.append({"passed": False, "file": relative_path,
                                   "issues": [str(error)]})
            continue
        native_sources[relative_path] = source
        checked = shared.analyze_native(source, relative_path, "rust")
        checked["file"] = relative_path
        checked["sha256"] = hashlib.sha256(source.encode("utf-8")).hexdigest()
        native_results.append(checked)
    pipeline = (
        shared.verify_pipeline("rust", tree, native_sources)
        if tree is not None and all(
            scanner.relative(path) in native_sources
            for path in shared.NATIVE_SOURCES["rust"]
        ) else {"passed": False, "issues": ["owned Rust compiler pipeline is incomplete"]}
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
        else {"passed": False, "skipped": "Rust source, compiler, or ELF provenance failed"}
    )
    mappings = runtime.get("native_mapping_provenance", {})
    inherited_issues = inherited_variant_issues(tests.get("inherited_variant_controls"))
    upstream_issues = scanner.validate_control_report(tests.get("upstream_controls"))
    passed = (
        not interpreter_issues
        and tests["passed"]
        and not inherited_issues
        and not upstream_issues
        and prior["passed"]
        and not artifact_issues
        and edge["passed"]
        and deep["passed"]
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
        "audit": "rust-v8-native-heap-from-scratch-provenance",
        "module": "candidates.rust_candidate",
        "result": "PASS" if passed else "FAIL",
        "passed": bool(passed),
        "pinned_interpreter": {
            "expected_version": list(scanner.PINNED_VERSION),
            "actual_version": list(sys.version_info[:3]),
            "expected_executable": str(scanner.PINNED_INTERPRETER),
            "actual_executable": sys.executable,
            "passed": not interpreter_issues,
            "issues": interpreter_issues,
        },
        "edge_oracle": edge,
        "deep_contract_proof": deep,
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
        "inherited_variant_poison_controls": {
            "passed": not inherited_issues,
            "expected_count": EXPECTED_VARIANT_CONTROL_COUNT,
            "expected_negative_count": EXPECTED_VARIANT_NEGATIVE_COUNT,
            "validated_count": tests.get("inherited_variant_controls", {}).get("check_count", 0),
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
            "variant": "genuine-native-heap",
            "other_candidate_production_sources_read": False,
            "other_candidate_native_binaries_read": False,
            "native_elf_paths": [scanner.relative(path)
                                 for path in shared.NATIVE_BINARIES["rust"].values()],
            "immutable_edge_oracle": scanner.relative(DEFAULT_EDGE),
            "immutable_deep_contract_proof": scanner.relative(DEFAULT_DEEP),
            "prior_stage_artifacts": [scanner.relative(path)
                                      for path, _ in PRIOR_STAGE_CERTIFICATES.values()],
            "benchmark_or_timing_executed": False,
            "holdout_accessed": False,
            "synthetic_malicious_fixtures": "in-memory only",
            "minimum_native_heap_negative_controls": MINIMUM_NATIVE_HEAP_NEGATIVE_CONTROLS,
            "maximum_compressed_evidence_bytes": MAX_COMPRESSED_BYTES,
            "maximum_decompressed_evidence_bytes": MAX_JSON_BYTES,
        },
        "limitations": [
            "The frozen 223198-case edge and three complete, matching 393-row deep-contract snapshots are independently hash-validated; no correctness cases are rerun.",
            "The certificate binds precisely five final Rust artifacts, six owned Rust native sources, zero-external-dependency manifests, and two independently hashed actually mapped Rust ELF binaries.",
            "All four original scanner and cmethod auditors and reports are independently hash-verified read-only and remain immutable.",
            "All 36 implementation-private GC-topology differences are preserved; they are not represented as documented public-contract mismatches.",
            "Static and isolated mapped-runtime evidence does not prove unexercised future execution paths.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="run only in-memory native-heap poison controls")
    parser.add_argument("--edge-oracle", type=Path, default=DEFAULT_EDGE,
                        help="the only authorized frozen native-heap edge")
    parser.add_argument("--deep-proof", type=Path, default=DEFAULT_DEEP,
                        help="the only authorized frozen 393-check native-heap proof")
    parser.add_argument("--output", type=Path, default=AUTHORIZED_OUTPUT,
                        help="the only authorized additive native-heap audit report")
    args = parser.parse_args(argv)
    interpreter_issues = scanner.pinned_interpreter_issues()
    if interpreter_issues:
        print(json.dumps({"passed": False, "result": "FAIL", "issues": interpreter_issues},
                         sort_keys=True))
        return 1
    if not scanner.authorized_path(args.output, AUTHORIZED_OUTPUT):
        parser.error("only candidates/audits/RUST-V8-NATIVE-HEAP-FROM-SCRATCH.json is authorized")
    if not scanner.authorized_path(args.edge_oracle, DEFAULT_EDGE):
        parser.error("only the frozen rust-native-heap edge oracle is authorized")
    if not scanner.authorized_path(args.deep_proof, DEFAULT_DEEP):
        parser.error("only RUST-V8-DEEP-CONTRACT-NATIVE-HEAP-FINAL.json.gz is authorized")
    if args.self_test:
        report = native_heap_self_test()
        print(json.dumps(report, sort_keys=True))
        return 0 if report["passed"] else 1
    report = run_native_heap_audit(args.edge_oracle, args.deep_proof)
    if report["passed"]:
        AUTHORIZED_OUTPUT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    summary: dict[str, Any] = {
        "passed": report["passed"],
        "result": report["result"],
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
        "artifact_count": report["frozen_live_artifacts"]["observed_count"],
        "artifacts_passed": report["frozen_live_artifacts"]["passed"],
        "original_stage_artifacts_passed": report["prior_stage_certificates"]["passed"],
        "source_passed": report["python_source"]["passed"],
        "native_sources_passed": all(x["passed"] for x in report["native_sources"]),
        "pipeline_passed": report["owned_pipeline"]["passed"],
        "manifest_passed": report["manifest_provenance"]["passed"],
        "rust_native_elf_passed": report["rust_native_elf_provenance"]["passed"],
        "rust_actual_mappings_passed": report["runtime_native_mapping_provenance"].get("passed", False),
        "isolated_runtime_passed": report["isolated_runtime"]["passed"],
        "native_heap_self_test_checks": report["self_test"]["check_count"],
        "native_heap_negative_controls": report["self_test"]["negative_control_count"],
        "inherited_variant_controls": report["inherited_variant_poison_controls"]["validated_count"],
        "upstream_poison_controls": report["upstream_poison_controls"]["validated_count"],
        "report": scanner.relative(AUTHORIZED_OUTPUT),
    }
    if not report["passed"]:
        summary["issues"] = (
            report["pinned_interpreter"]["issues"]
            + report["edge_oracle"]["issues"]
            + report["deep_contract_proof"]["issues"]
            + report["frozen_live_artifacts"]["issues"]
            + report["prior_stage_certificates"]["issues"]
            + report["inherited_variant_poison_controls"]["issues"]
            + report["upstream_poison_controls"]["issues"]
            + report["input_issues"]
            + report["self_test"].get("failed", [])
        )
    print(json.dumps(summary, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
