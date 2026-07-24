#!/usr/bin/env python3
"""Run unchanged frozen suites only through cache-hardened genuine V10 owners."""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import collections
import contextlib
import copy
import gzip
import hashlib
import importlib
import io
import json
import multiprocessing
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Callable, Iterator, Mapping
import unicodedata


ROOT = Path(__file__).resolve().parent.parent
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-postfinal-current-build-proofs-v10"
SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v10.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V10.md"
REFRESH_PROTOCOL_SHA256 = (
    "2eb5b5c0828059b1d02d306e9cf6f05e90d30575e3a386c20f83582456de1ae0"
)
V10_BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v10.py"
V10_BASE_SOURCE_SHA256 = (
    "0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505"
)
V10_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v10.py"
V10_STRICT_SOURCE_SHA256 = (
    "885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95"
)
V10_OWNERSHIP_PROTOCOL_RELATIVE = "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md"
V10_OWNERSHIP_PROTOCOL_SHA256 = (
    "902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6"
)
V10_BASE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10.json"
V10_STRICT_REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10.json"
V8_PROOF_RELATIVE = "tools/postfinal_current_build_proofs_v8.py"
V8_PROOF_SHA256 = (
    "0f9e12847855797669206ea89de94948da66c29742d64820a625ce5a6570b313"
)
V9_PROOF_RELATIVE = "tools/postfinal_current_build_proofs_v9.py"
V9_PROOF_SHA256 = (
    "5604c513efef32a352336506e23b855ee7fb6010722dc3dae2b97c9601ad4c86"
)
V9_REFRESH_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V9.md"
)
V9_REFRESH_PROTOCOL_SHA256 = (
    "986f29f6a31981f8bf5155bd1b04f5d3ba569ba80a49652ed638c99f01e92680"
)
STAGE07_RELATIVE = "tools/python_re_universal_public_oracle_stage07.py"
STAGE07_SHA256 = (
    "150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25"
)
EDGE_SOURCE_RELATIVE = "tools/rust_v7_edge_oracle.py"
EDGE_SOURCE_SHA256 = (
    "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
)
EDGE_SEED = 2026072329
EDGE_CHECKS = 223198
EDGE_CATEGORIES = 49
EDGE_SEEDED_CASES = 8
EDGE_UNICODE_STRIDE = 4099
EDGE_REFERENCE_SHA256 = (
    "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
)
DEEP_SOURCE_RELATIVE = "tools/rust_v8_deep_contract_oracle.py"
DEEP_SOURCE_SHA256 = (
    "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978"
)
DEEP_RUNNER_RELATIVE = "tools/rust_v8_multi_candidate_contract.py"
DEEP_RUNNER_SHA256 = (
    "167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70"
)
DEEP_SEED = 2026072347
DEEP_CHECKS = 393
DEEP_SEEDED_CASES = 64
DEEP_REFERENCE_SHA256 = (
    "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8"
)
BASELINE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json"
)
BASELINE_SHA256 = (
    "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916"
)
OFFICIAL_V5_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v5.py"
OFFICIAL_V5_SOURCE_SHA256 = (
    "9a4f2ac53617fb91e498ae2935bde622417921415af255e390668f69ba908730"
)
OFFICIAL_V5_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V5.md"
OFFICIAL_V5_PROTOCOL_SHA256 = (
    "1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840"
)
V8_GENUINE_FAILURE_RELATIVE = (
    "candidates/evidence/"
    "rust-v7-edge-oracle-rust-postfinal-current-build-v8-"
    "diagnostic-native-owner-failure.json.gz"
)
V8_GENUINE_FAILURE_SHA256 = (
    "2f8bfcba726d729865cb8411a25ef1c3e0633e80c70af8895e5875a71f15ed7b"
)
V9_GENUINE_FAILURE_RELATIVE = (
    "candidates/evidence/"
    "rust-v7-edge-oracle-rust-postfinal-current-build-v9-"
    "diagnostic-native-owner-failure.json.gz"
)
V9_GENUINE_FAILURE_SHA256 = (
    "04e52f831534458e9af50ad3ab962d78ad43e6a8725cbfccfee37bf9c234f07c"
)
HISTORICAL_EDGE_FAILURES = {
    "rust": (
        "candidates/evidence/"
        "rust-v7-edge-oracle-rust-postfinal-locale-v7-first-failure.json.gz",
        "3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8",
        16,
    ),
    "vm": (
        "candidates/evidence/"
        "rust-v7-edge-oracle-vm-postfinal-locale-v7-first-failure.json.gz",
        "2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c",
        33,
    ),
    "zig": (
        "candidates/evidence/"
        "rust-v7-edge-oracle-zig-postfinal-locale-v7-first-failure.json.gz",
        "5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a",
        16,
    ),
}
FAMILIES = {
    "rust": {
        "module": "candidates.rust_candidate", "contract_name": "RUST",
        "sources": (
            "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
            "candidates/rust/src/lib.rs", "candidates/rust/src/search.rs",
            "candidates/rust/src/newline.rs", "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
        "native": {
            "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "engine": "candidates/_rust_engine.so",
        },
    },
    "vm": {
        "module": "candidates.vm_candidate", "contract_name": "C",
        "sources": ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
        "native": {
            "native": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        },
    },
    "zig": {
        "module": "candidates.zig_candidate", "contract_name": "ZIG",
        "sources": (
            "candidates/zig_candidate.py", "candidates/zig/py_bridge.c",
            "candidates/zig/mini_regex.zig",
        ),
        "native": {
            "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
            "engine": "candidates/_zig_probe.so",
        },
    },
}
SENTINEL_TRUE_FIELDS = (
    "sentinel_type_exact", "sys_modules_sentinel_identity",
    "imported_sentinel_identity", "before_matching_verified",
    "after_matching_verified", "fresh_sentinel_rejected",
    "subclass_sentinel_rejected", "same_name_forged_sentinel_rejected",
    "live_module_rejected",
)
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_CHILD_OUTPUT_BYTES = 2 * 1024 * 1024
FROZEN_INPUTS = {
    "GOAL.md":
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    EDGE_SOURCE_RELATIVE: EDGE_SOURCE_SHA256,
    DEEP_SOURCE_RELATIVE: DEEP_SOURCE_SHA256,
    DEEP_RUNNER_RELATIVE: DEEP_RUNNER_SHA256,
    STAGE07_RELATIVE: STAGE07_SHA256,
    V8_PROOF_RELATIVE: V8_PROOF_SHA256,
    V9_PROOF_RELATIVE: V9_PROOF_SHA256,
    V9_REFRESH_PROTOCOL_RELATIVE: V9_REFRESH_PROTOCOL_SHA256,
    OFFICIAL_V5_SOURCE_RELATIVE: OFFICIAL_V5_SOURCE_SHA256,
    OFFICIAL_V5_PROTOCOL_RELATIVE: OFFICIAL_V5_PROTOCOL_SHA256,
    BASELINE_RELATIVE: BASELINE_SHA256,
    V8_GENUINE_FAILURE_RELATIVE: V8_GENUINE_FAILURE_SHA256,
    V9_GENUINE_FAILURE_RELATIVE: V9_GENUINE_FAILURE_SHA256,
}


class ProofV10Error(AssertionError):
    """Corrected genuine ownership or frozen original correctness failed."""


class ProofV10Failure(ProofV10Error):
    def __init__(self, message: str, evidence: Mapping[str, Any]):
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ProofV10Error(message)


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        item in "0123456789abcdef" for item in value
    )


def canonical(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, allow_nan=False,
                   sort_keys=True, indent=2)
        + "\n"
    ).encode("ascii")


def decode_json(payload: bytes, label: str) -> dict[str, Any]:
    def unique(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in rows:
            require(key not in result, label + " repeats a JSON key")
            result[key] = value
        return result

    def reject_constant(value: str) -> Any:
        raise ProofV10Error(label + " contains non-finite JSON: " + value)

    try:
        result = json.loads(payload.decode("utf-8"),
                            object_pairs_hook=unique,
                            parse_constant=reject_constant)
    except (UnicodeError, ValueError, TypeError) as error:
        raise ProofV10Error(label + " is not complete strict JSON") from error
    require(isinstance(result, dict), label + " is not a JSON object")
    return result


def read_regular(path: Path, label: str) -> bytes:
    require(isinstance(path, Path) and path.is_absolute()
            and path.resolve() == path and not path.is_symlink(),
            label + " is not its exact canonical regular path")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and 0 < before.st_size <= MAX_FILE_BYTES,
                label + " is not a complete bounded regular file")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            raw = stream.read(MAX_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
        require(len(raw) == before.st_size and len(raw) <= MAX_FILE_BYTES,
                label + " changed its complete size")
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns),
                label + " changed while its bytes were authenticated")
        return raw
    finally:
        if descriptor != -1:
            os.close(descriptor)


def authenticate_frozen(relative: str, digest: str) -> bytes:
    require(valid_sha256(digest),
            "a corrected immutable V10 source or protocol has not been published")
    raw = read_regular(ROOT / relative, "frozen V10 correctness input " + relative)
    require(hashlib.sha256(raw).hexdigest() == digest,
            "an immutable V10 correctness input changed: " + relative)
    return raw


def verify_runtime() -> None:
    require(platform.python_implementation() == "CPython"
            and sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and Path(sys.executable).resolve() == PINNED_EXECUTABLE.resolve()
            and sys.flags.isolated == 1 and sys.dont_write_bytecode,
            "V10 correctness requires the exact pinned isolated CPython 3.14.6")
    require(unicodedata.unidata_version == "16.0.0",
            "V10 correctness requires exact frozen Unicode 16")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "the V10 correctness controller must never import a candidate")


def checked_family(name: str) -> dict[str, Any]:
    require(name in FAMILIES, "an unknown independently owned V10 family was requested")
    return FAMILIES[name]


def snapshot_family(name: str) -> dict[str, Any]:
    family = checked_family(name)
    sources: dict[str, str] = {}
    for relative in family["sources"]:
        raw = read_regular(ROOT / relative, "exact rebuilt V10 source " + relative)
        sources[relative] = hashlib.sha256(raw).hexdigest()
    native: dict[str, str] = {}
    for relative in family["native"].values():
        raw = read_regular(ROOT / relative, "exact owned V10 ELF " + relative)
        require(raw.startswith(b"\x7fELF"),
                "a current independent V10 matching engine is not real ELF")
        native[relative] = hashlib.sha256(raw).hexdigest()
    require(len(sources) == len(family["sources"])
            and len(native) == len(family["native"]),
            "the corrected genuine V10 owner source/native denominator changed")
    return {
        "family": name, "module": family["module"],
        "source_sha256_by_path": sources,
        "native_sha256_by_path": native,
    }


def validated_report_pins(
    qualified: bool, base_digest: Any, strict_digest: Any,
    *, synthetic_sources: Mapping[str, str] | None = None,
) -> dict[str, str] | None:
    if not qualified:
        require(base_digest is None and strict_digest is None,
                "a diagnostic must not represent unvalidated all-family report pins")
        return None
    source = V10_BASE_SOURCE_SHA256
    strict = V10_STRICT_SOURCE_SHA256
    if synthetic_sources is not None:
        require(isinstance(synthetic_sources, Mapping)
                and set(synthetic_sources) == {"base_source", "strict_source"},
                "a source-only synthetic V10 proof changed its source denominator")
        source = synthetic_sources["base_source"]
        strict = synthetic_sources["strict_source"]
    for label, digest in (
        ("base_source", source), ("strict_source", strict),
        ("base_report", base_digest), ("strict_report", strict_digest),
    ):
        require(valid_sha256(digest),
                "the actual frozen all-family V10 " + label
                + " was not independently published")
    values = {
        "base_source": str(source), "strict_source": str(strict),
        "base_report": str(base_digest), "strict_report": str(strict_digest),
    }
    require(len(set(values.values())) == len(values),
            "an actual V10 source, base report, or strict report was repeated")
    return values


def import_frozen(name: str, relative: str, digest: str) -> Any:
    authenticate_frozen(relative, digest)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    module = importlib.import_module(name)
    require(Path(module.__file__).resolve() == ROOT / relative,
            "a frozen corrected V10 module was substituted: " + name)
    authenticate_frozen(relative, digest)
    verify_runtime()
    return module


def validate_sentinel(record: Any, family: str) -> None:
    require(isinstance(record, dict)
            and record.get("stage07_source_sha256") == STAGE07_SHA256
            and all(record.get(key) is True for key in SENTINEL_TRUE_FIELDS),
            "the " + family
            + " owner did not prove exact stage07 cached sentinel identity "
              "before and after genuine native matching")


def validate_matcher_descendants(record: Any, family: str) -> None:
    require(isinstance(record, dict),
            "the " + family + " owner omitted the actual cached stage07 descendants")
    required = ["re._compiler", "re._parser"]
    discovered = record.get("discovered_descendants")
    require(record.get("stage07_source_sha256") == STAGE07_SHA256
            and record.get("required_descendants") == required
            and isinstance(discovered, list)
            and all(isinstance(name, str) and name.startswith("re.")
                    for name in discovered)
            and discovered == sorted(set(discovered))
            and all(name in discovered for name in required),
            "the " + family + " owner omitted a genuine cached re descendant")
    require(type(record.get("cached_alias_count")) is int
            and record["cached_alias_count"] >= 0
            and type(record.get("helper_alias_replacement_count")) is int
            and record["helper_alias_replacement_count"]
            == record["cached_alias_count"]
            and record.get("all_cached_aliases_same_sentinel") is True
            and record.get("before_matching_verified") is True
            and record.get("after_matching_verified") is True,
            "the " + family + " owner did not use the real stage07 alias helper")
    observed: dict[str, list[dict[str, Any]]] = {}
    for phase in ("observations_before", "observations_after"):
        rows = record.get(phase)
        require(isinstance(rows, list) and len(rows) == len(discovered),
                "the " + family + " owner omitted a " + phase + " cached alias")
        names: list[str] = []
        for row in rows:
            require(isinstance(row, dict)
                    and isinstance(row.get("module"), str)
                    and row.get("blocked") is True
                    and row.get("sentinel_identity") is True
                    and row.get("cache_identity") is True
                    and row.get("sentinel_type_exact") is True,
                    "the " + family + " owner retained or forged a live "
                    + phase + " stage07 descendant")
            names.append(row["module"])
        require(names == discovered,
                "the " + family + " owner replaced or reordered a "
                + phase + " genuine cached descendant")
        observed[phase] = rows
    require(observed["observations_before"] == observed["observations_after"],
            "the " + family + " stage07 cached alias changed after matching")


def validate_owner(owner: Any, record: Any, family: str,
                   expected_native: Mapping[str, str]) -> dict[str, Any]:
    require(family in FAMILIES and isinstance(record, dict)
            and isinstance(expected_native, Mapping) and bool(expected_native),
            "a corrected isolated V10 owner record is missing")
    validated = owner.validate_worker(record, family, dict(expected_native))
    require(validated is record or validated == record,
            "the corrected V10 validator substituted real native observations")
    for key, value in {
        "status": "PASS", "result": "PASS", "passed": True,
        "family": family,
        "candidate_module": FAMILIES[family]["module"],
        "standard_pickle_check_count": 16,
        "standard_pickle_failure_count": 0,
        "regex_guard_count": 13,
        "native_loader_guard_count": 5,
        "persistent_cross_engine_guard": True,
        "genuine_matching_executed": True,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }.items():
        require(record.get(key) == value,
                "a corrected genuine V10 native owner changed: " + family + ":" + key)
    validate_sentinel(record.get("stage07_guard_sentinel"), family)
    validate_matcher_descendants(
        record.get("stage07_matcher_descendant_guards"), family,
    )
    require(record.get("native_binary_sha256") == dict(expected_native),
            "the corrected V10 worker used a foreign or stale mapped native ELF")
    require(record.get("regex_guard_observations_after")
            == record.get("regex_guard_observations")
            and record.get("foreign_engine_guard_observations_after")
            == record.get("foreign_engine_guard_observations")
            and record.get("native_loader_guard_observations_after")
            == record.get("native_loader_guard_observations"),
            "the corrected native owner changed a genuine poison after matching")
    checks = record.get("standard_pickle_checks")
    require(isinstance(checks, list) and len(checks) == 16
            and all(isinstance(row, dict) and row.get("passed") is True
                    for row in checks),
            "the corrected V10 owner omitted a genuine ordinary pickle observation")
    return record


def validate_official_baseline(document: Any) -> None:
    require(isinstance(document, dict),
            "the actual frozen two-reference CPython baseline is not an object")
    for key, value in {
        "schema": "rebar-postfinal-cpython-full-public-locale-v5-self-oracle",
        "status": "PASS", "synthetic": False, "python": "3.14.6",
        "source_sha256":
            "9a4f2ac53617fb91e498ae2935bde622417921415af255e390668f69ba908730",
        "protocol_sha256":
            "1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840",
        "public_method_matrix_sha256":
            "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a",
        "actual_independent_reference_count": 2,
        "old_v7_campaign_prerequisite": False,
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }.items():
        require(document.get(key) == value,
                "the real independently frozen CPython baseline changed: " + key)
    roles = document.get("roles")
    require(isinstance(roles, dict) and set(roles) == {"reference_a", "reference_b"},
            "the genuine official self-oracle omitted a real independent CPython role")
    for name, role in roles.items():
        require(isinstance(role, dict) and role.get("status") == "PASS"
                and role.get("methods") == 152
                and role.get("applicable") == 151
                and role.get("passed") == 151
                and role.get("skipped") == 1
                and role.get("named_private_debug_skips") == 1
                and role.get("unexplained_skips") == 0,
                "the genuine full official CPython baseline changed: " + name)


def edge_target(family: str, qualified: bool, passed: bool) -> Path:
    checked_family(family)
    scope = "qualified" if qualified else "diagnostic"
    result = "pass" if passed else "failures"
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v10-" + scope + "-" + result + ".json.gz"
    )


def owner_failure_target(family: str, qualified: bool) -> Path:
    checked_family(family)
    scope = "qualified" if qualified else "diagnostic"
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v10-" + scope
        + "-native-owner-failure.json.gz"
    )


def producer_failure_target(family: str, qualified: bool, deep: bool) -> Path:
    metadata = checked_family(family)
    if deep:
        require(qualified, "an unqualified diagnostic cannot start a deep producer")
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V10-PRODUCER-CRASH.json.gz"
        )
    scope = "qualified" if qualified else "diagnostic"
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v10-" + scope + "-producer-crash.json.gz"
    )


def invalidated_target(family: str, qualified: bool, deep: bool) -> Path:
    metadata = checked_family(family)
    if deep:
        require(qualified, "a diagnostic cannot publish a deep result")
        return ROOT / "candidates/audits" / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V10-INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
        )
    scope = "qualified" if qualified else "diagnostic"
    return ROOT / "candidates/evidence" / (
        "rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v10-" + scope
        + "-invalidated-after-owner-failure.json.gz"
    )


def deep_target(family: str, passed: bool) -> Path:
    metadata = checked_family(family)
    suffix = "PASS" if passed else "FAILURES"
    return ROOT / "candidates/audits" / (
        "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V10-" + suffix + ".json.gz"
    )


def fresh_target(path: Path, parent: Path) -> Path:
    require(path.is_absolute() and path.parent == parent
            and path.resolve() == path,
            "a V10 evidence target escaped its exact authorized family directory")
    require(parent.is_dir() and not parent.is_symlink(),
            "an exact authorized V10 evidence directory is missing or unsafe")
    require(not path.exists() and not path.is_symlink(),
            "refusing to rerun a worker or overwrite an existing V10 result")
    return path


def exclusive_publish(path: Path, raw: bytes, *, deep: bool) -> str:
    parent = ROOT / "candidates" / ("audits" if deep else "evidence")
    fresh_target(path, parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor != -1:
            os.close(descriptor)
    require(read_regular(path, "exclusively published complete V10 evidence") == raw,
            "exclusive V10 publication changed the actual complete producer bytes")
    return hashlib.sha256(raw).hexdigest()


def validate_v8_failure(document: Any) -> None:
    require(isinstance(document, dict),
            "the real frozen V8 pre-import owner failure is malformed")
    for key, value in {
        "schema": "rebar-postfinal-current-build-proofs-v8-native-owner-failure",
        "status": "FAIL", "result": "FAIL", "mode": "diagnostic",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "stage": "before-original-edge",
        "native_worker_crashed": True,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "original_edge_worker_started": False,
        "original_deep_worker_started": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }.items():
        require(document.get(key) == value,
                "the genuine pre-import stage07 owner failure changed: " + key)
    actual = document.get("complete_actual_native_worker")
    require(isinstance(actual, dict) and actual.get("status") == "FAIL"
            and actual.get("family") == "rust"
            and actual.get("candidate_module") == "candidates.rust_candidate"
            and actual.get("actual_returncode") == 1
            and actual.get("signal") is None
            and actual.get("timed_out") is False
            and actual.get("stdout_bytes") == 0
            and actual.get("stderr_bytes") == 216
            and actual.get("stdout_sha256")
            == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            and actual.get("stderr_sha256")
            == "020e506be39aab54cc62c7fc5f5ce15a2e8a505e6585df6089298c833e42ba2c"
            and actual.get("production_observations_invented") is False
            and actual.get("qualifies_current_engine") is False,
            "the actual V8 pre-import guard failure was hidden or relabeled")


def validate_v9_failure(document: Any) -> None:
    require(isinstance(document, dict),
            "the real frozen V9 cached-compiler owner failure is malformed")
    for key, value in {
        "schema": "rebar-postfinal-current-build-proofs-v9-native-owner-failure",
        "status": "FAIL", "result": "FAIL", "mode": "diagnostic",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "stage": "before-original-edge",
        "native_worker_crashed": True,
        "refresh_protocol_path": V9_REFRESH_PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": V9_REFRESH_PROTOCOL_SHA256,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "original_edge_worker_started": False,
        "original_deep_worker_started": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }.items():
        require(document.get(key) == value,
                "the genuine V9 cached-compiler failure changed: " + key)
    actual = document.get("complete_actual_native_worker")
    require(isinstance(actual, dict)
            and actual.get("schema")
            == "rebar-postfinal-from-scratch-audit-v9-native-owner-worker-failure"
            and actual.get("status") == "FAIL"
            and actual.get("family") == "rust"
            and actual.get("candidate_module") == "candidates.rust_candidate"
            and actual.get("actual_returncode") == 1
            and actual.get("signal") is None
            and actual.get("timed_out") is False
            and actual.get("stdout_bytes") == 0
            and actual.get("stderr_bytes") == 203
            and actual.get("stdout_sha256")
            == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            and actual.get("stderr_sha256")
            == "7cfcf842efd492372ee01c330db0fc632aac9182c5f5b45870c5286a3e841097"
            and actual.get("production_observations_invented") is False
            and actual.get("qualifies_current_engine") is False,
            "the actual 203-byte V9 cached-compiler failure was hidden or forged")


def validate_v9_failure_summary(record: Any, label: str) -> None:
    require(isinstance(record, dict),
            label + " omitted the complete actual V9 cached-compiler failure")
    for key, value in {
        "path": V9_GENUINE_FAILURE_RELATIVE,
        "sha256": V9_GENUINE_FAILURE_SHA256,
        "status": "FAIL",
        "stage": "before-original-edge",
        "candidate_module": "candidates.rust_candidate",
        "actual_returncode": 1,
        "stdout_bytes": 0,
        "stderr_bytes": 203,
        "stdout_sha256":
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stderr_sha256":
            "7cfcf842efd492372ee01c330db0fc632aac9182c5f5b45870c5286a3e841097",
        "original_edge_worker_started": False,
        "qualifies_current_engine": False,
    }.items():
        require(record.get(key) == value,
                label + " replaced the actual V9 cached-compiler failure: " + key)


def authenticate_history(v8: Any, owner: Any) -> dict[str, Any]:
    incident_raw = authenticate_frozen(
        V8_GENUINE_FAILURE_RELATIVE, V8_GENUINE_FAILURE_SHA256,
    )
    incident, _ = v8.decode_archive(
        incident_raw, "actual immutable V8 pre-import native guard failure",
    )
    validate_v8_failure(incident)
    original_incident = owner.validate_v8_owner_failure(incident)
    require(original_incident.get("sha256") == V8_GENUINE_FAILURE_SHA256
            and original_incident.get("status") == "FAIL"
            and original_incident.get("actual_returncode") == 1
            and original_incident.get("stdout_bytes") == 0
            and original_incident.get("stderr_bytes") == 216,
            "the corrected V10 owner rejected the exact real V8 cached-sentinel failure")
    v9_incident_raw = authenticate_frozen(
        V9_GENUINE_FAILURE_RELATIVE, V9_GENUINE_FAILURE_SHA256,
    )
    v9_incident, _ = v8.decode_archive(
        v9_incident_raw, "actual immutable V9 cached-compiler guard failure",
    )
    validate_v9_failure(v9_incident)
    original_v9_incident = owner.validate_v9_owner_failure(v9_incident)
    validate_v9_failure_summary(
        original_v9_incident, "the genuine frozen V10 native owner",
    )
    baseline_raw = authenticate_frozen(BASELINE_RELATIVE, BASELINE_SHA256)
    baseline = decode_json(baseline_raw, "real independent two-reference V5 oracle")
    validate_official_baseline(baseline)
    official = import_frozen(
        "tools.postfinal_cpython_locale_oracle_v5",
        OFFICIAL_V5_SOURCE_RELATIVE, OFFICIAL_V5_SOURCE_SHA256,
    )
    provenance = official.authenticate_reference_prerequisites(
        OFFICIAL_V5_SOURCE_SHA256, OFFICIAL_V5_PROTOCOL_SHA256,
    )
    official._validate_reference(baseline, provenance)
    previous: dict[str, dict[str, Any]] = {}
    for family, (relative, digest, failed) in HISTORICAL_EDGE_FAILURES.items():
        raw = authenticate_frozen(relative, digest)
        document, _ = v8.decode_archive(
            raw, "real preserved historical edge failure " + family,
        )
        require(document.get("schema") == "rebar-v7-independent-edge-oracle-v1"
                and document.get("module") == FAMILIES[family]["module"]
                and document.get("seed") == EDGE_SEED
                and document.get("correctness_checks") == EDGE_CHECKS
                and document.get("expected_sha256") == EDGE_REFERENCE_SHA256
                and document.get("failed") == failed
                and isinstance(document.get("failures"), list)
                and len(document["failures"]) == failed
                and isinstance(document.get("categories"), dict)
                and len(document["categories"]) == EDGE_CATEGORIES
                and sum(document["categories"].values()) == EDGE_CHECKS,
                "a real original full edge failure was hidden: " + family)
        previous[family] = {
            "status": "FAIL", "qualifies_current_engine": False,
            "archive_sha256": digest, "failed": failed,
            "checks": EDGE_CHECKS, "category_count": EDGE_CATEGORIES,
        }
    return {
        "historical_current_build_edge_failures": previous,
        "genuine_v8_preimport_owner_failure": {
            "path": V8_GENUINE_FAILURE_RELATIVE,
            "sha256": V8_GENUINE_FAILURE_SHA256,
            "status": "FAIL", "original_edge_worker_started": False,
        },
        "genuine_v9_cached_compiler_owner_failure": {
            **original_v9_incident,
            "actual_stderr_sha256":
                "7cfcf842efd492372ee01c330db0fc632aac9182c5f5b45870c5286a3e841097",
            "actual_stdout_sha256":
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        },
        "genuine_official_cpython_baseline": {
            "path": BASELINE_RELATIVE, "sha256": BASELINE_SHA256,
            "status": "PASS", "actual_independent_reference_count": 2,
            "public_method_count": 152, "applicable_public_method_count": 151,
        },
    }


def decode_report(relative: str, digest: str) -> dict[str, Any]:
    raw = authenticate_frozen(relative, digest)
    result = decode_json(raw, "complete actual passing V10 audit report " + relative)
    compact = json.dumps(result, ensure_ascii=True, allow_nan=False,
                         sort_keys=True, separators=(",", ":")).encode("ascii")
    require(raw in {compact, compact + b"\n"},
            "an actual V10 audit report is not exact canonical frozen JSON")
    return result


def audit_v10_reports(owner: Any, strict: Any,
                     pins: Mapping[str, str]) -> dict[str, Any]:
    base = decode_report(V10_BASE_REPORT_RELATIVE, pins["base_report"])
    report = decode_report(V10_STRICT_REPORT_RELATIVE, pins["strict_report"])
    validate_v9_failure_summary(
        base.get("actual_v9_native_owner_failure"),
        "the actual full all-family V10 base report",
    )
    validate_v9_failure_summary(
        report.get("actual_v9_native_owner_failure"),
        "the actual full all-family V10 strict report",
    )
    require(base.get("historical_v9_owner_failure_qualifies_current_build") is False,
            "the V10 base report qualified the genuine cached-compiler failure")
    graph = strict.validate_base_report(base, {
        "base_source": pins["base_source"],
        "base_report": pins["base_report"],
    })
    require(isinstance(graph, dict) and graph.get("source_count") == 12
            and graph.get("native_binary_count") == 5,
            "the actual passing V10 source graph lost its 12 sources or five ELFs")
    base_workers = base.get("actual_native_owner_workers")
    require(isinstance(base_workers, dict) and set(base_workers) == set(FAMILIES),
            "the passing V10 base audit omitted a corrected native owner")
    for family in FAMILIES:
        validate_owner(owner, base_workers[family], family,
                       graph["native_sha256_by_family"][family])
    for key, value in {
        "schema": "rebar-postfinal-no-delegation-audit-v10",
        "postfinal_schema": "rebar-postfinal-no-delegation-audit-v10",
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": V10_STRICT_SOURCE_RELATIVE,
        "audit_source_sha256": pins["strict_source"],
        "base_audit_postfinal_schema": "rebar-postfinal-from-scratch-audit-v10",
        "base_audit_source_path": V10_BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": pins["base_source"],
        "base_audit_report_path": V10_BASE_REPORT_RELATIVE,
        "base_audit_report_sha256": pins["base_report"],
        "native_ownership_protocol_path": V10_OWNERSHIP_PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
        "stage07_source_path": STAGE07_RELATIVE,
        "stage07_source_sha256": STAGE07_SHA256,
        "native_owner_worker_sha256": owner.NATIVE_OWNER_WORKER_SHA256,
        "v5_reference_path": BASELINE_RELATIVE,
        "v5_reference_sha256": BASELINE_SHA256,
        "historical_v8_owner_failure_qualifies_current_build": False,
        "historical_v9_owner_failure_qualifies_current_build": False,
        "historical_v7_results_qualify_current_build": False,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "verified_match_repr_checks": 6,
        "verified_standard_pickle_count": 48,
        "standard_pickle_failure_count": 0,
        "completed_native_owner_worker_count": 3,
        "actual_native_owner_worker_failure": None,
    }.items():
        require(report.get(key) == value,
                "the actually passing corrected V10 strict audit changed: " + key)
    require(report.get("verified_candidate_source_paths") == graph["source_paths"]
            and report.get("native_sha256_by_family")
            == graph["native_sha256_by_family"],
            "the passing strict V10 audit changed its complete source/native graph")
    workers = report.get("actual_native_owner_workers")
    require(isinstance(workers, dict) and set(workers) == set(FAMILIES),
            "the passing strict V10 audit omitted an actual corrected native owner")
    for family in FAMILIES:
        validate_owner(owner, workers[family], family,
                       graph["native_sha256_by_family"][family])
    require(report.get("independent_base_native_owner_workers") == base_workers,
            "the strict corrected audit replaced its original independently passing owners")
    incident = report.get("actual_v8_native_owner_failure")
    require(isinstance(incident, dict)
            and incident.get("path") == V8_GENUINE_FAILURE_RELATIVE
            and incident.get("sha256") == V8_GENUINE_FAILURE_SHA256
            and incident.get("status") == "FAIL"
            and incident.get("stage") == "before-original-edge"
            and incident.get("actual_returncode") == 1
            and incident.get("stdout_bytes") == 0
            and incident.get("stderr_bytes") == 216
            and incident.get("original_edge_worker_started") is False
            and incident.get("qualifies_current_engine") is False,
            "the corrected strict V10 report concealed the real V8 guard incident")
    history = report.get("historical_current_build_edge_failures")
    require(isinstance(history, dict) and set(history) == set(FAMILIES),
            "the corrected strict V10 audit omitted a historical native edge failure")
    for family, (_, digest, failed) in HISTORICAL_EDGE_FAILURES.items():
        previous = history[family]
        require(isinstance(previous, dict)
                and previous.get("status") == "FAIL"
                and previous.get("qualifies_current_engine") is False
                and previous.get("archive_sha256") == digest
                and previous.get("failed") == failed
                and previous.get("failure_rows_preserved") == failed
                and previous.get("checks") == EDGE_CHECKS
                and previous.get("category_count") == EDGE_CATEGORIES,
                "a corrected strict audit concealed a real native edge failure: "
                + family)
    scope = report.get("postfinal_scope")
    require(isinstance(scope, dict)
            and scope.get("append_only") is True
            and scope.get("exclusive_report_path") == V10_STRICT_REPORT_RELATIVE
            and scope.get("separate_pass_and_failure_destinations") is True
            and scope.get("independently_pinned_fresh_v10_base") is True
            and scope.get("base_report_hash_supplied_externally") is True
            and scope.get("previous_v8_owner_failure_preserved") is True
            and scope.get("previous_v9_owner_failure_preserved") is True
            and scope.get("historical_v8_owner_failure_qualifies_current_build") is False
            and scope.get("historical_v9_owner_failure_qualifies_current_build") is False
            and scope.get("historical_v7_reports_qualify_current_build") is False
            and scope.get("actual_edge_failures_preserved") is True
            and scope.get("actual_current_native_binary_count") == 5
            and scope.get("exact_current_owned_candidate_source_count") == 12
            and scope.get("independently_executed_native_owner_workers") == 3
            and scope.get("genuine_public_pickle_checks") == 48
            and scope.get("genuine_match_repr_checks") == 6
            and scope.get("actual_python_matching_guards_per_family") == 13
            and scope.get("actual_native_loader_guards_per_family") == 5
            and scope.get("exact_stage07_sentinel_checked_before_and_after") is True
            and scope.get(
                "all_cached_matcher_descendants_poisoned_before_and_after"
            ) is True
            and scope.get("original_stage07_cached_alias_helper_used") is True
            and scope.get("persistent_cross_family_import_and_loader_guards") is True
            and scope.get("native_identity_is_independent_of_public_module") is True
            and scope.get("mapped_binaries_hashed_against_static_elf") is True
            and scope.get("benchmark_or_timing_executed") is False
            and scope.get("holdout_or_case_fixture_access") is False,
            "the corrected genuine V10 strict source or poison scope was weakened")
    controls = report.get("postfinal_wrapper_self_test")
    require(isinstance(controls, dict)
            and controls.get("passed") is True
            and controls.get("candidate_imports") == 0
            and controls.get("subprocesses") == 0
            and controls.get("file_reads") == 0
            and controls.get("file_writes") == 0
            and controls.get("clock_samples") == 0,
            "the corrected strict V10 candidate-free proof boundary was weakened")
    return {"base": base, "strict": report, "graph": graph, "pins": dict(pins)}


def preflight(family: str, qualified: bool,
              base_digest: Any = None, strict_digest: Any = None) -> dict[str, Any]:
    verify_runtime()
    metadata = checked_family(family)
    pins = validated_report_pins(qualified, base_digest, strict_digest)
    require(valid_sha256(REFRESH_PROTOCOL_SHA256),
            "the exact independently frozen V10 refresh protocol is not published")
    authenticate_frozen(PROTOCOL_RELATIVE, str(REFRESH_PROTOCOL_SHA256))
    require(valid_sha256(V10_BASE_SOURCE_SHA256)
            and valid_sha256(V10_STRICT_SOURCE_SHA256)
            and valid_sha256(V10_OWNERSHIP_PROTOCOL_SHA256),
            "an exact independently frozen V10 native audit source is not published")
    for relative, digest in FROZEN_INPUTS.items():
        if relative.startswith("candidates/") or "/evidence/" in relative:
            continue
        authenticate_frozen(relative, digest)
    authenticate_frozen(V10_OWNERSHIP_PROTOCOL_RELATIVE,
                        str(V10_OWNERSHIP_PROTOCOL_SHA256))
    v8 = import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        V8_PROOF_RELATIVE, V8_PROOF_SHA256,
    )
    owner = import_frozen(
        "tools.postfinal_from_scratch_audit_v10",
        V10_BASE_SOURCE_RELATIVE, str(V10_BASE_SOURCE_SHA256),
    )
    strict = import_frozen(
        "tools.postfinal_no_delegation_audit_v10",
        V10_STRICT_SOURCE_RELATIVE, str(V10_STRICT_SOURCE_SHA256),
    )
    require(tuple(owner.CORE_FAMILIES) == tuple(FAMILIES)
            and strict.independent is owner
            and owner.PROTOCOL_RELATIVE == V10_OWNERSHIP_PROTOCOL_RELATIVE
            and owner.PROTOCOL_SHA256 == V10_OWNERSHIP_PROTOCOL_SHA256,
            "the corrected genuine V10 native-owner dependency graph changed")
    for name in FAMILIES:
        require(tuple(owner.OWNED_SOURCE_PATHS[name]) == FAMILIES[name]["sources"]
                and dict(owner.OWNED_NATIVE_PATHS[name]) == FAMILIES[name]["native"],
                "the corrected V10 owner omitted a genuine family source or ELF")
    audits = audit_v10_reports(owner, strict, pins) if pins is not None else None
    history = authenticate_history(v8, owner)
    snapshot = snapshot_family(family)
    if audits is not None:
        require(snapshot["native_sha256_by_path"]
                == audits["graph"]["native_sha256_by_family"][family]
                and set(snapshot["source_sha256_by_path"])
                <= set(audits["graph"]["source_paths"]),
                "the independently proven V10 candidate changed after both audits")
    require(metadata["module"] not in sys.modules,
            "a corrected V10 candidate leaked into the proof controller")
    return {
        "owner": owner, "strict": strict, "v8": v8,
        "history": history, "snapshot": snapshot, "audits": audits,
    }


def audited_graph_provenance(state: Mapping[str, Any]) -> dict[str, Any]:
    audits = state["audits"]
    if audits is None:
        return {"all_family_audit_qualified": False,
                "all_family_source_sha256_by_path": None,
                "all_family_native_elf_sha256_by_path": None}
    sources: dict[str, str] = {}
    for family in FAMILIES:
        detail = audits["base"]["families"][family]
        public = detail["python_source"]
        sources[public["file"]] = public["sha256"]
        for source in detail["native_sources"]:
            sources[source["file"]] = source["sha256"]
    native: dict[str, str] = {}
    for family in FAMILIES:
        native.update(audits["graph"]["native_sha256_by_family"][family])
    require(len(sources) == 12 and len(native) == 5,
            "the real passing V10 audits omitted an owned source or native ELF")
    return {"all_family_audit_qualified": True,
            "all_family_source_sha256_by_path": sources,
            "all_family_native_elf_sha256_by_path": native}


def frozen_provenance(state: Mapping[str, Any]) -> dict[str, Any]:
    audits = state["audits"]
    return {
        "refresh_protocol_path": PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": REFRESH_PROTOCOL_SHA256,
        "v10_native_owner_source_path": V10_BASE_SOURCE_RELATIVE,
        "v10_native_owner_source_sha256": V10_BASE_SOURCE_SHA256,
        "v10_no_delegation_source_path": V10_STRICT_SOURCE_RELATIVE,
        "v10_no_delegation_source_sha256": V10_STRICT_SOURCE_SHA256,
        "v10_native_ownership_protocol_path": V10_OWNERSHIP_PROTOCOL_RELATIVE,
        "v10_native_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
        "stage07_source_path": STAGE07_RELATIVE,
        "stage07_source_sha256": STAGE07_SHA256,
        "actual_v10_base_report_sha256":
            audits["pins"]["base_report"] if audits is not None else None,
        "actual_v10_strict_report_sha256":
            audits["pins"]["strict_report"] if audits is not None else None,
    }


def retain_invalidated_original(
    family: str, qualified: bool, deep: bool,
    raw: bytes, passed: bool | None,
) -> tuple[str, str, str]:
    require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_FILE_BYTES
            and (passed is None or type(passed) is bool),
            "a real V10 original result lost its bounded complete original bytes")
    target = invalidated_target(family, qualified, deep)
    digest = exclusive_publish(target, raw, deep=deep)
    actual = "NOT VALIDATED" if passed is None else "PASS" if passed else "FAIL"
    return target.relative_to(ROOT).as_posix(), digest, actual


def preserve_owner_failure(
    family: str, state: Mapping[str, Any], *, qualified: bool,
    stage: str, actual: Mapping[str, Any], crashed: bool,
    completed_original: tuple[bytes, bool] | None = None,
) -> None:
    allowed_stages = {"before-original-edge", "after-original-edge",
                      "before-original-deep", "after-original-deep"}
    require(stage in allowed_stages and isinstance(actual, Mapping)
            and actual.get("status") == "FAIL",
            "refusing to invent a real corrected V10 native-owner failure")
    deep = "deep" in stage
    require((completed_original is not None) == stage.startswith("after-"),
            "a corrected failed owner concealed the actual complete original result")
    invalidated_path = invalidated_digest = invalidated_status = None
    if completed_original is not None:
        raw, passed = completed_original
        invalidated_path, invalidated_digest, invalidated_status = (
            retain_invalidated_original(family, qualified, deep, raw, passed)
        )
    metadata = checked_family(family)
    target = owner_failure_target(family, qualified)
    document = {
        "schema": SCHEMA + "-native-owner-failure",
        "status": "FAIL", "result": "FAIL",
        "mode": "qualified" if qualified else "diagnostic",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "stage": stage, "native_worker_crashed": crashed,
        "complete_actual_native_worker": dict(actual),
        "actual_native_worker_failure_count":
            actual.get("standard_pickle_failure_count"),
        "actual_native_worker_pickle_check_count":
            actual.get("standard_pickle_check_count"),
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "all_family_audited_provenance": audited_graph_provenance(state),
        "preserved_immutable_history": state["history"],
        "original_edge_worker_started": stage == "after-original-edge",
        "original_deep_worker_started": stage == "after-original-deep",
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_digest,
        "invalidated_complete_original_actual_status": invalidated_status,
        "passing_evidence_published": False,
        "campaign_qualified": False, "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        **frozen_provenance(state),
    }
    payload = canonical(document)
    require(len(payload) <= MAX_FILE_BYTES,
            "a complete real V10 owner failure exceeds its bounded archive")
    raw = gzip.compress(payload, compresslevel=9, mtime=0)
    decoded, preserved = state["v8"].decode_archive(
        raw, "complete exclusively retained V10 native-owner failure",
    )
    require(decoded == document and preserved == payload,
            "exclusive V10 native-owner failure lost actual observations")
    digest = exclusive_publish(target, raw, deep=False)
    raise ProofV10Failure(
        "the corrected isolated V10 native owner failed before qualification",
        {"status": "FAIL", "candidate_family": metadata["contract_name"],
         "candidate_module": metadata["module"], "stage": stage,
         "native_worker_crashed": crashed,
         "failure_evidence_path": target.relative_to(ROOT).as_posix(),
         "failure_evidence_sha256": digest,
         "invalidated_complete_original_evidence_path": invalidated_path,
         "invalidated_complete_original_evidence_sha256": invalidated_digest,
         "invalidated_complete_original_actual_status": invalidated_status,
         "passing_evidence_published": False,
         "campaign_qualified": False,
         "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
         **frozen_provenance(state)},
    )


def observe_owner(
    family: str, state: Mapping[str, Any], *, qualified: bool,
    stage: str, completed_original: tuple[bytes, bool] | None = None,
) -> dict[str, Any]:
    owner = state["owner"]
    expected = dict(state["snapshot"]["native_sha256_by_path"])
    try:
        record = owner.run_native_worker(family, expected)
    except owner.NativeWorkerFailure as error:
        preserve_owner_failure(
            family, state, qualified=qualified, stage=stage,
            actual=error.evidence, crashed=True,
            completed_original=completed_original,
        )
        raise AssertionError("a completely retained genuine V10 owner crash returned")
    try:
        return validate_owner(owner, record, family, expected)
    except (AssertionError, TypeError, ValueError, KeyError) as error:
        require(isinstance(record, Mapping),
                "the genuine corrected V10 owner did not return actual observations")
        failure = {
            "status": "FAIL", "result": "FAIL", "passed": False,
            "family": family,
            "candidate_module": FAMILIES[family]["module"],
            "actual_validation_error_type": type(error).__name__,
            "actual_validation_error_message": str(error),
            "actual_owner_record_status": record.get("status"),
            "complete_actual_native_owner_record": dict(record),
            "standard_pickle_check_count": record.get("standard_pickle_check_count"),
            "standard_pickle_failure_count":
                record.get("standard_pickle_failure_count"),
            "qualifies_current_engine": False,
            "production_observations_invented": False,
        }
        preserve_owner_failure(
            family, state, qualified=qualified, stage=stage,
            actual=failure, crashed=False,
            completed_original=completed_original,
        )
        raise AssertionError("a completely preserved genuine V10 owner rejection returned")


def observed_stream(value: bytes | str | None, complete: bool) -> dict[str, Any]:
    if value is None:
        raw = b""
    elif isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8", "surrogatepass")
    else:
        raise ProofV10Error("an actual V10 worker stream is not bytes")
    preview = raw[:MAX_CHILD_OUTPUT_BYTES]
    return {
        "observed_bytes": len(raw),
        "observed_sha256": hashlib.sha256(raw).hexdigest(),
        "observed_stream_complete": complete,
        "preview_bytes": len(preview),
        "preview_complete": len(raw) == len(preview),
        "preview_base64": base64.b64encode(preview).decode("ascii"),
    }


def preserve_producer_failure(
    family: str, state: Mapping[str, Any], *, qualified: bool, deep: bool,
    reason: str, returncode: int | None, stdout: bytes | str | None,
    stderr: bytes | str | None, timed_out: bool,
    owner_before: Mapping[str, Any],
    completed_original: tuple[bytes, bool | None] | None = None,
    integrity_error: BaseException | None = None,
) -> None:
    require(reason in {
        "crash-without-complete-archive", "timeout",
        "stdout-limit-exceeded", "stderr-limit-exceeded",
        "post-original-integrity-failure",
    }, "a genuine original V10 producer failure was invented")
    require(isinstance(owner_before, Mapping)
            and owner_before.get("status") == "PASS"
            and owner_before.get("standard_pickle_failure_count") == 0,
            "the original producer started without a corrected passing V10 owner")
    require(completed_original is None
            or reason == "post-original-integrity-failure",
            "a timed-out or crashed V10 producer fabricated completed observations")
    metadata = checked_family(family)
    target = producer_failure_target(family, qualified, deep)
    invalidated_path = invalidated_digest = invalidated_status = None
    if completed_original is not None:
        raw, passed = completed_original
        invalidated_path, invalidated_digest, invalidated_status = (
            retain_invalidated_original(family, qualified, deep, raw, passed)
        )
    document = {
        "schema": SCHEMA + "-original-producer-failure",
        "status": "FAIL", "result": "FAIL",
        "mode": ("qualified-deep" if deep
                 else "qualified-edge" if qualified else "edge-diagnostic"),
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "actual_failure_reason": reason,
        "actual_child_exit_code": returncode,
        "actual_child_signal":
            -returncode if isinstance(returncode, int) and returncode < 0 else None,
        "timed_out": timed_out,
        "timeout_seconds": 1800 if timed_out else None,
        "actual_integrity_error_type":
            type(integrity_error).__name__ if integrity_error is not None else None,
        "actual_integrity_error_message":
            str(integrity_error) if integrity_error is not None else None,
        "stdout": observed_stream(stdout, not timed_out),
        "stderr": observed_stream(stderr, not timed_out),
        "native_owner_before": dict(owner_before),
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "all_family_audited_provenance": audited_graph_provenance(state),
        "preserved_immutable_history": state["history"],
        "complete_original_observation_archive": completed_original is not None,
        "original_correctness_observations":
            "INVALIDATED" if completed_original is not None else "NOT COMPLETED",
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_digest,
        "invalidated_complete_original_actual_status": invalidated_status,
        "production_observations_invented": False,
        "passing_evidence_published": False,
        "campaign_qualified": False, "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        **frozen_provenance(state),
    }
    payload = canonical(document)
    require(len(payload) <= MAX_FILE_BYTES,
            "the complete real V10 producer failure exceeded its bounded size")
    raw = gzip.compress(payload, compresslevel=9, mtime=0)
    decoded, preserved = state["v8"].decode_archive(
        raw, "complete exclusive genuine V10 producer failure",
    )
    require(decoded == document and preserved == payload,
            "the real original producer failure lost bounded actual output")
    digest = exclusive_publish(target, raw, deep=deep)
    raise ProofV10Failure(
        "the unchanged original correctness producer did not finish safely",
        {"status": "FAIL", "candidate_family": metadata["contract_name"],
         "candidate_module": metadata["module"],
         "actual_failure_reason": reason,
         "actual_child_exit_code": returncode,
         "failure_evidence_path": target.relative_to(ROOT).as_posix(),
         "failure_evidence_sha256": digest,
         "stdout_observed_sha256": document["stdout"]["observed_sha256"],
         "stderr_observed_sha256": document["stderr"]["observed_sha256"],
         "invalidated_complete_original_evidence_path": invalidated_path,
         "invalidated_complete_original_evidence_sha256": invalidated_digest,
         "passing_evidence_published": False, "campaign_qualified": False,
         "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
         **frozen_provenance(state)},
    )


def run_original(
    command: list[str], family: str, state: Mapping[str, Any],
    *, qualified: bool, deep: bool, owner_before: Mapping[str, Any],
) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            command, cwd=str(ROOT),
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "PYTHONPATH": str(ROOT), "LC_ALL": "C",
                 "PATH": "/usr/bin:/bin"},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=1800,
        )
    except subprocess.TimeoutExpired as error:
        preserve_producer_failure(
            family, state, qualified=qualified, deep=deep, reason="timeout",
            returncode=None, stdout=error.stdout, stderr=error.stderr,
            timed_out=True, owner_before=owner_before,
        )
        raise AssertionError("an exclusively preserved original timeout returned")
    for value, label in ((result.stdout, "stdout-limit-exceeded"),
                         (result.stderr, "stderr-limit-exceeded")):
        if len(value) > MAX_CHILD_OUTPUT_BYTES:
            preserve_producer_failure(
                family, state, qualified=qualified, deep=deep, reason=label,
                returncode=result.returncode, stdout=result.stdout,
                stderr=result.stderr, timed_out=False,
                owner_before=owner_before,
            )
            raise AssertionError("an exclusively preserved oversized stream returned")
    return result


def preflight_targets(family: str, qualified: bool, deep: bool) -> None:
    if deep:
        require(qualified, "an unqualified mode cannot run the genuine deep suite")
        for path in (deep_target(family, True), deep_target(family, False),
                     producer_failure_target(family, True, True),
                     invalidated_target(family, True, True)):
            fresh_target(path, ROOT / "candidates/audits")
        fresh_target(owner_failure_target(family, True),
                     ROOT / "candidates/evidence")
        return
    for path in (
        edge_target(family, qualified, True),
        edge_target(family, qualified, False),
        owner_failure_target(family, qualified),
        producer_failure_target(family, qualified, False),
        invalidated_target(family, qualified, False),
    ):
        fresh_target(path, ROOT / "candidates/evidence")


def refresh_edge(
    family: str, *, qualified: bool,
    base_digest: str | None = None, strict_digest: str | None = None,
) -> dict[str, Any]:
    state = preflight(family, qualified, base_digest, strict_digest)
    preflight_targets(family, qualified, False)
    metadata = checked_family(family)
    v8 = state["v8"]
    contract = v8.load_contract()
    before = observe_owner(
        family, state, qualified=qualified, stage="before-original-edge",
    )
    require(snapshot_family(family) == state["snapshot"],
            "the corrected genuine V10 native owner changed before the original edge")
    with tempfile.TemporaryDirectory(
        prefix="rebar-v10-original-edge-" + family + "-", dir="/tmp",
    ) as directory:
        private = Path(directory).resolve()
        require(private.parent == Path("/tmp").resolve(),
                "the unchanged original V10 edge escaped its direct /tmp root")
        temporary = private / "original-full-edge.json.gz"
        result = run_original(
            [str(PINNED_EXECUTABLE), "-I", "-B", str(ROOT / EDGE_SOURCE_RELATIVE),
             "--module", metadata["module"], "--seed", str(EDGE_SEED),
             "--seeded-cases", str(EDGE_SEEDED_CASES),
             "--unicode-stride", str(EDGE_UNICODE_STRIDE),
             "--output", str(temporary)],
            family, state, qualified=qualified, deep=False,
            owner_before=before,
        )
        if not temporary.exists() or temporary.is_symlink():
            preserve_producer_failure(
                family, state, qualified=qualified, deep=False,
                reason="crash-without-complete-archive",
                returncode=result.returncode,
                stdout=result.stdout, stderr=result.stderr,
                timed_out=False, owner_before=before,
            )
            raise AssertionError("an exclusively preserved original edge crash returned")
        raw = read_regular(temporary, "complete unchanged actual V10 original edge")
        passed: bool | None = None
        try:
            report, _, passed = v8.validate_original_edge(
                raw, temporary, family, state["snapshot"], contract,
            )
            require(result.returncode == int(not passed),
                    "the unchanged V10 original edge concealed an actual mismatch")
            after_owner = observe_owner(
                family, state, qualified=qualified,
                stage="after-original-edge", completed_original=(raw, passed),
            )
            after = preflight(family, qualified, base_digest, strict_digest)
            require(after["snapshot"] == state["snapshot"]
                    and after["history"] == state["history"]
                    and (not qualified or (
                        after["audits"]["pins"] == state["audits"]["pins"]
                        and after["audits"]["graph"] == state["audits"]["graph"]
                    )),
                    "a real V10 native source, sentinel audit, or failure history drifted")
            target = edge_target(family, qualified, passed)
            preflight_targets(family, qualified, False)
            archive_sha256 = exclusive_publish(target, raw, deep=False)
        except ProofV10Failure:
            raise
        except (AssertionError, OSError, ValueError, TypeError,
                KeyError, UnicodeError) as error:
            preserve_producer_failure(
                family, state, qualified=qualified, deep=False,
                reason="post-original-integrity-failure",
                returncode=result.returncode,
                stdout=result.stdout, stderr=result.stderr,
                timed_out=False, owner_before=before,
                completed_original=(raw, passed),
                integrity_error=error,
            )
            raise AssertionError("an invalidated unchanged original edge returned")
    preserved = read_regular(target, "actual exclusively published V10 original edge")
    final, proof, published_pass = v8.validate_original_edge(
        preserved, target, family, state["snapshot"], contract,
    )
    require(preserved == raw and final == report and published_pass == passed
            and proof["archive_sha256"] == archive_sha256,
            "exclusive publication changed the real complete original V10 edge")
    result = {
        "schema": SCHEMA + ("-qualified-edge" if qualified else "-edge-diagnostic"),
        "status": "PASS" if passed else "FAIL",
        "mode": "qualified-edge" if qualified else "edge-diagnostic",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "campaign_qualified": bool(qualified and passed),
        "seed": EDGE_SEED, "checks": EDGE_CHECKS,
        "category_count": EDGE_CATEGORIES,
        "failure_count": final["failed"],
        "complete_failure_row_count": len(final["failures"]),
        "reference_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": final["actual_sha256"],
        "evidence_path": target.relative_to(ROOT).as_posix(),
        "evidence_sha256": archive_sha256,
        "complete_original_producer_bytes_preserved": True,
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "corrected_v10_native_owner_before": before,
        "corrected_v10_native_owner_after": after_owner,
        "actual_v10_base_report_sha256": base_digest if qualified else None,
        "actual_v10_strict_report_sha256": strict_digest if qualified else None,
        "preserved_immutable_history": state["history"],
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        **frozen_provenance(state),
    }
    if not passed:
        result["first_failures"] = final["failures"][:5]
    return result


DEEP_LAUNCHER = (
    "import json,sys;from pathlib import Path;"
    "sys.path.insert(0,sys.argv[1]);"
    "from tools import rust_v8_multi_candidate_contract as c;"
    "s=c.SPECS[sys.argv[2]];"
    "r,v,e=c.run_gate(s,Path(sys.argv[3]),Path(sys.argv[4]),"
    "Path(sys.argv[5]));"
    "print(json.dumps(v,ensure_ascii=True,allow_nan=False,sort_keys=True));"
    "raise SystemExit(e)"
)


def refresh_deep(family: str, base_digest: str, strict_digest: str) -> dict[str, Any]:
    state = preflight(family, True, base_digest, strict_digest)
    preflight_targets(family, True, True)
    metadata = checked_family(family)
    v8 = state["v8"]
    contract = v8.load_contract()
    qualified_edge = edge_target(family, True, True)
    raw_edge = read_regular(qualified_edge, "exact required V10 passing qualified edge")
    _, edge, edge_passed = v8.validate_original_edge(
        raw_edge, qualified_edge, family, state["snapshot"], contract,
    )
    require(edge_passed and edge.get("failed") == 0
            and edge.get("checks") == EDGE_CHECKS
            and edge.get("category_count") == EDGE_CATEGORIES,
            "a diagnostic or incomplete edge cannot run genuine V10 deep correctness")
    before = observe_owner(
        family, state, qualified=True, stage="before-original-deep",
    )
    with tempfile.TemporaryDirectory(
        prefix="rebar-v10-original-deep-" + family + "-", dir="/tmp",
    ) as directory:
        private = Path(directory).resolve()
        require(private.parent == Path("/tmp").resolve(),
                "the original deep suite escaped its exact direct /tmp root")
        temporary = private / (
            "RUST-V8-DEEP-CONTRACT-" + metadata["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V10-PRIVATE.json.gz"
        )
        command = [str(PINNED_EXECUTABLE), "-I", "-B", "-c", DEEP_LAUNCHER,
                   str(ROOT), metadata["module"], str(qualified_edge),
                   str(temporary), str(private)]
        child = run_original(command, family, state,
                             qualified=True, deep=True, owner_before=before)
        if not temporary.exists() or temporary.is_symlink():
            preserve_producer_failure(
                family, state, qualified=True, deep=True,
                reason="crash-without-complete-archive",
                returncode=child.returncode,
                stdout=child.stdout, stderr=child.stderr,
                timed_out=False, owner_before=before,
            )
            raise AssertionError("an exclusively preserved original deep crash returned")
        raw = read_regular(temporary, "actual complete original V10 deep producer")
        passed: bool | None = None
        try:
            document, passed = v8.validate_deep(
                raw, family, edge, state["snapshot"], contract,
            )
            require(child.returncode == int(not passed),
                    "the genuine original V10 deep producer hid a public mismatch")
            after_owner = observe_owner(
                family, state, qualified=True,
                stage="after-original-deep", completed_original=(raw, passed),
            )
            after = preflight(family, True, base_digest, strict_digest)
            require(after["snapshot"] == state["snapshot"]
                    and after["history"] == state["history"]
                    and after["audits"]["pins"] == state["audits"]["pins"]
                    and after["audits"]["graph"] == state["audits"]["graph"]
                    and read_regular(qualified_edge,
                                     "rechecked exact V10 qualified edge") == raw_edge,
                    "a real V10 audit, corrected owner, or qualified edge changed")
            target = deep_target(family, passed)
            preflight_targets(family, True, True)
            archive_sha256 = exclusive_publish(target, raw, deep=True)
        except ProofV10Failure:
            raise
        except (AssertionError, OSError, ValueError, TypeError,
                KeyError, UnicodeError) as error:
            preserve_producer_failure(
                family, state, qualified=True, deep=True,
                reason="post-original-integrity-failure",
                returncode=child.returncode,
                stdout=child.stdout, stderr=child.stderr,
                timed_out=False, owner_before=before,
                completed_original=(raw, passed),
                integrity_error=error,
            )
            raise AssertionError("an invalidated complete original deep report returned")
    preserved = read_regular(target, "genuine exclusively published V10 deep report")
    final, final_passed = v8.validate_deep(
        preserved, family, edge, state["snapshot"], contract,
    )
    require(preserved == raw and final == document and final_passed == passed,
            "exclusive V10 publication changed the actual original deep cases")
    result = {
        "schema": SCHEMA + "-qualified-deep",
        "status": "PASS" if passed else "FAIL", "mode": "qualified-deep",
        "candidate_family": metadata["contract_name"],
        "candidate_module": metadata["module"],
        "campaign_qualified": bool(passed),
        "seed": DEEP_SEED, "checks": DEEP_CHECKS,
        "seeded_case_count": DEEP_SEEDED_CASES,
        "public_mismatch_count": final["public_mismatch_count"],
        "public_mismatch_family_counts": final["public_mismatch_family_counts"],
        "reference_sha256": DEEP_REFERENCE_SHA256,
        "actual_sha256": final["candidate_sha256"],
        "evidence_path": target.relative_to(ROOT).as_posix(),
        "evidence_sha256": archive_sha256,
        "qualified_edge_path": qualified_edge.relative_to(ROOT).as_posix(),
        "qualified_edge_sha256": edge["archive_sha256"],
        "complete_original_producer_bytes_preserved": True,
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "corrected_v10_native_owner_before": before,
        "corrected_v10_native_owner_after": after_owner,
        "actual_v10_base_report_sha256": base_digest,
        "actual_v10_strict_report_sha256": strict_digest,
        "preserved_immutable_history": state["history"],
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        **frozen_provenance(state),
    }
    if not passed:
        result["first_failures"] = final["public_mismatches"][:5]
    return result


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    counts = {
        "candidate_import_attempts_blocked": 0,
        "worker_attempts_blocked": 0,
        "clock_attempts_blocked": 0,
        "write_attempts_blocked": 0,
        "evidence_read_attempts_blocked": 0,
        "unauthorized_read_attempts_blocked": 0,
    }
    originals: list[tuple[Any, str, Any]] = []
    allowed = {
        (ROOT / relative).resolve()
        for relative in FROZEN_INPUTS
        if not relative.startswith("candidates/")
        and "/evidence/" not in relative
    }
    allowed.update({
        (ROOT / SOURCE_RELATIVE).resolve(),
        (ROOT / PROTOCOL_RELATIVE).resolve(),
        (ROOT / V10_BASE_SOURCE_RELATIVE).resolve(),
        (ROOT / V10_STRICT_SOURCE_RELATIVE).resolve(),
    })

    def replace(target: Any, name: str, value: Any) -> None:
        if hasattr(target, name):
            originals.append((target, name, getattr(target, name)))
            setattr(target, name, value)

    def blocked(kind: str, label: str) -> Callable[..., Any]:
        def reject(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            counts[kind] += 1
            raise ProofV10Error("a candidate-free V10 source control forbids " + label)

        return reject

    def authorized(path: Any) -> bool:
        try:
            return Path(os.fsdecode(path)).resolve() in allowed
        except (OSError, TypeError, ValueError):
            return False

    original_os_open = os.open

    def guarded_os_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        writes = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
        writes |= getattr(os, "O_APPEND", 0)
        if flags & writes:
            return blocked("write_attempts_blocked", "filesystem writes")()
        if isinstance(path, int) or not authorized(path):
            kind = ("evidence_read_attempts_blocked"
                    if not isinstance(path, int)
                    and ("evidence" in Path(os.fsdecode(path)).parts
                         or "candidates" in Path(os.fsdecode(path)).parts
                         or "performance" in Path(os.fsdecode(path)).parts)
                    else "unauthorized_read_attempts_blocked")
            return blocked(kind, "evidence, report, holdout, or unrelated reads")()
        return original_os_open(path, flags, *args, **kwargs)

    original_open = builtins.open

    def guarded_open(path: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if any(character in mode for character in "wax+"):
            return blocked("write_attempts_blocked", "filesystem writes")()
        if isinstance(path, int):
            return original_open(path, mode, *args, **kwargs)
        if not authorized(path):
            kind = ("evidence_read_attempts_blocked"
                    if isinstance(path, (str, bytes, os.PathLike))
                    and any(part in {"candidates", "evidence", "performance", "holdout"}
                            for part in Path(os.fsdecode(path)).parts)
                    else "unauthorized_read_attempts_blocked")
            return blocked(kind, "evidence, report, holdout, or unrelated reads")()
        return original_open(path, mode, *args, **kwargs)

    denied = {"candidates", "regex", "_regex", "pcre", "pcre2", "re2",
              "hyperscan", "rure", "onig", "oniguruma"}
    original_import = builtins.__import__
    original_import_module = importlib.import_module

    def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if isinstance(name, str) and name.partition(".")[0] in denied:
            return blocked("candidate_import_attempts_blocked",
                           "candidate or foreign-engine import")()
        return original_import(name, *args, **kwargs)

    def guarded_import_module(name: str, package: str | None = None) -> Any:
        if isinstance(name, str) and name.partition(".")[0] in denied:
            return blocked("candidate_import_attempts_blocked",
                           "importlib candidate or foreign-engine import")()
        return original_import_module(name, package)

    replace(os, "open", guarded_os_open)
    replace(builtins, "open", guarded_open)
    replace(io, "open", guarded_open)
    replace(builtins, "__import__", guarded_import)
    replace(importlib, "import_module", guarded_import_module)
    for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                 "perf_counter", "perf_counter_ns", "process_time",
                 "process_time_ns", "thread_time", "thread_time_ns",
                 "clock_gettime", "clock_gettime_ns"):
        replace(time, name, blocked("clock_attempts_blocked", "clock " + name))
    for target, name in (
        (subprocess, "run"), (subprocess, "Popen"),
        (threading.Thread, "start"),
        (multiprocessing.Process, "start"),
        (tempfile, "mkdtemp"), (tempfile, "TemporaryDirectory"),
    ):
        replace(target, name, blocked("worker_attempts_blocked", "worker " + name))
    for name in ("fork", "posix_spawn", "posix_spawnp", "system"):
        replace(os, name, blocked("worker_attempts_blocked", "process " + name))
    for name in ("unlink", "remove", "rename", "replace", "mkdir", "makedirs",
                 "rmdir", "removedirs", "chmod", "chown", "link", "symlink",
                 "truncate", "utime"):
        replace(os, name, blocked("write_attempts_blocked", "filesystem " + name))
    for name in ("write_bytes", "write_text", "touch", "mkdir", "unlink",
                 "rename", "replace", "rmdir", "chmod", "hardlink_to",
                 "symlink_to"):
        replace(Path, name, blocked("write_attempts_blocked", "path " + name))
    try:
        yield counts
    finally:
        for target, name, original in reversed(originals):
            setattr(target, name, original)


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (ProofV10Error, AssertionError, OSError, ValueError,
            TypeError, KeyError, UnicodeError):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def synthetic_digest(label: str) -> str:
    return hashlib.sha256(("v10-candidate-free-only:" + label).encode("ascii")).hexdigest()


def synthetic_owner(family: str) -> tuple[Any, dict[str, Any], dict[str, str]]:
    metadata = checked_family(family)
    native = {relative: synthetic_digest(relative)
              for relative in metadata["native"].values()}
    sentinel = {key: True for key in SENTINEL_TRUE_FIELDS}
    sentinel["stage07_source_sha256"] = STAGE07_SHA256
    guards = [{"module": "source-control", "name": str(index), "blocked": True}
              for index in range(13)]
    loaders = [{"alias": "source-only-loader-" + str(index), "blocked": True}
               for index in range(5)]
    checks = [{"origin": origin, "argument": argument,
               "protocol": protocol, "passed": True}
              for origin in ("Pattern", "Match")
              for argument in ("str", "bytes")
              for protocol in (0, 2, 4, 5)]
    descendant_names = ["re._compiler", "re._parser"]
    descendant_observations = [
        {"module": name, "blocked": True, "sentinel_identity": True,
         "cache_identity": True, "sentinel_type_exact": True}
        for name in descendant_names
    ]
    descendants = {
        "stage07_source_sha256": STAGE07_SHA256,
        "required_descendants": descendant_names,
        "discovered_descendants": list(descendant_names),
        "observations_before": copy.deepcopy(descendant_observations),
        "observations_after": copy.deepcopy(descendant_observations),
        "cached_alias_count": len(descendant_names),
        "helper_alias_replacement_count": len(descendant_names),
        "all_cached_aliases_same_sentinel": True,
        "before_matching_verified": True,
        "after_matching_verified": True,
    }
    record = {
        "status": "PASS", "result": "PASS", "passed": True,
        "family": family, "candidate_module": metadata["module"],
        "native_binary_sha256": native,
        "standard_pickle_check_count": 16,
        "standard_pickle_failure_count": 0,
        "standard_pickle_checks": checks,
        "regex_guard_count": 13,
        "regex_guard_observations": guards,
        "regex_guard_observations_after": copy.deepcopy(guards),
        "foreign_engine_guard_observations": [],
        "foreign_engine_guard_observations_after": [],
        "native_loader_guard_count": 5,
        "native_loader_guard_observations": loaders,
        "native_loader_guard_observations_after": copy.deepcopy(loaders),
        "persistent_cross_engine_guard": True,
        "genuine_matching_executed": True,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "stage07_guard_sentinel": sentinel,
        "stage07_matcher_descendant_guards": descendants,
    }

    class SourceOnlyOwner:
        @staticmethod
        def validate_worker(value: Any, role: str,
                            expected: Mapping[str, str]) -> dict[str, Any]:
            require(isinstance(value, dict) and value.get("family") == role
                    and value.get("native_binary_sha256") == dict(expected),
                    "the source-only owner substituted a native family")
            return value

    return SourceOnlyOwner(), record, native


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime()
    controls: list[dict[str, Any]] = []

    def accept(label: str, condition: Any) -> None:
        controls.append({"name": label, "passed": bool(condition)})

    with source_only_boundary() as effects:
        for relative, digest in FROZEN_INPUTS.items():
            if relative.startswith("candidates/") or "/evidence/" in relative:
                accept("retain-immutable-evidence-pin-without-reading:" + relative,
                       valid_sha256(digest))
                continue
            raw = authenticate_frozen(relative, digest)
            accept("authenticate-immutable-frozen-source:" + relative,
                   hashlib.sha256(raw).hexdigest() == digest)
            if relative.endswith(".py"):
                accept("parse-frozen-source-without-importing:" + relative,
                       isinstance(ast.parse(raw.decode("utf-8"), filename=relative),
                                  ast.Module))
        source = read_regular(ROOT / SOURCE_RELATIVE,
                              "candidate-free corrected V10 proof source")
        tree = ast.parse(source.decode("utf-8"), filename=SOURCE_RELATIVE)
        accept("parse-corrected-v10-source-without-production-execution",
               isinstance(tree, ast.Module))
        history_function = next((
            node for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "authenticate_history"
        ), None)
        accept("require-actual-original-full-v5-reference-validator",
               isinstance(history_function, ast.FunctionDef)
               and any(
                   isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Attribute)
                   and node.func.attr == "_validate_reference"
                   for node in ast.walk(history_function)
               ))
        accept("require-actual-frozen-v9-cached-compiler-failure-validation",
               isinstance(history_function, ast.FunctionDef)
               and any(
                   isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name)
                   and node.func.id == "validate_v9_failure"
                   for node in ast.walk(history_function)
               )
               and any(
                   isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Attribute)
                   and node.func.attr == "validate_v9_owner_failure"
                   for node in ast.walk(history_function)
               ))
        owner_function = next((
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "validate_owner"
        ), None)
        accept("require-independent-genuine-cached-stage07-worker-validation",
               isinstance(owner_function, ast.FunctionDef)
               and any(
                   isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name)
                   and node.func.id == "validate_matcher_descendants"
                   for node in ast.walk(owner_function)
               ))
        audit_function = next((
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "audit_v10_reports"
        ), None)
        if isinstance(audit_function, ast.FunctionDef):
            audit_assignments: dict[str, tuple[int, ast.AST]] = {}
            for index, statement in enumerate(audit_function.body):
                if isinstance(statement, ast.Assign):
                    for target in statement.targets:
                        if isinstance(target, ast.Name):
                            audit_assignments[target.id] = (index, statement.value)
            accept("authenticate-both-full-actual-v10-reports-before-any-validator",
                   "base" in audit_assignments
                   and "report" in audit_assignments
                   and "graph" in audit_assignments
                   and audit_assignments["base"][0]
                   < audit_assignments["graph"][0]
                   and audit_assignments["report"][0]
                   < audit_assignments["graph"][0]
                   and all(
                       isinstance(audit_assignments[name][1], ast.Call)
                       and isinstance(audit_assignments[name][1].func, ast.Name)
                       and audit_assignments[name][1].func.id == "decode_report"
                       for name in ("base", "report")
                   ))
            accept("require-real-v9-cache-failure-in-both-full-v10-reports",
                   sum(
                       isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Name)
                       and node.func.id == "validate_v9_failure_summary"
                       for node in ast.walk(audit_function)
                   ) >= 2)
        else:
            accept("authenticate-both-full-actual-v10-reports-before-any-validator",
                   False)
            accept("require-real-v9-cache-failure-in-both-full-v10-reports", False)
        preflight_function = next((
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "preflight"
        ), None)
        accept("require-independent-actual-report-authentication-preflight",
               isinstance(preflight_function, ast.FunctionDef))
        if isinstance(preflight_function, ast.FunctionDef):
            assignment_indexes: dict[str, int] = {}
            for index, statement in enumerate(preflight_function.body):
                if isinstance(statement, ast.Assign):
                    for target in statement.targets:
                        if isinstance(target, ast.Name):
                            assignment_indexes[target.id] = index
            accept("authenticate-actual-v10-reports-before-historical-evidence",
                   "audits" in assignment_indexes
                   and "history" in assignment_indexes
                   and assignment_indexes["audits"]
                   < assignment_indexes["history"])
        protocol = read_regular(ROOT / PROTOCOL_RELATIVE,
                               "candidate-free corrected V10 refresh protocol")
        accept("require-actually-published-v10-refresh-protocol-pin",
               valid_sha256(REFRESH_PROTOCOL_SHA256)
               and hashlib.sha256(protocol).hexdigest() == REFRESH_PROTOCOL_SHA256)
        accept("require-actually-published-v10-native-source-pins",
               valid_sha256(V10_BASE_SOURCE_SHA256)
               and valid_sha256(V10_STRICT_SOURCE_SHA256)
               and valid_sha256(V10_OWNERSHIP_PROTOCOL_SHA256))
        if valid_sha256(V10_BASE_SOURCE_SHA256):
            raw = authenticate_frozen(V10_BASE_SOURCE_RELATIVE,
                                      str(V10_BASE_SOURCE_SHA256))
            accept("authenticate-real-frozen-corrected-v10-native-owner-source",
                   isinstance(ast.parse(raw.decode("utf-8")), ast.Module))
        if valid_sha256(V10_STRICT_SOURCE_SHA256):
            raw = authenticate_frozen(V10_STRICT_SOURCE_RELATIVE,
                                      str(V10_STRICT_SOURCE_SHA256))
            accept("authenticate-real-frozen-corrected-v10-strict-audit-source",
                   isinstance(ast.parse(raw.decode("utf-8")), ast.Module))
        for token in (
            b"223,198", b"49", b"393", b"64", b"stage07_guard_sentinel",
            b"stage07_matcher_descendant_guards",
            b"re._compiler", b"re._parser",
            b"2f8bfcba726d729865cb8411a25ef1c3e0633e80c70af8895e5875a71f15ed7b",
            b"04e52f831534458e9af50ad3ab962d78ad43e6a8725cbfccfee37bf9c234f07c",
            b"3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916",
            b"campaign_qualified", b"NOT MEASURED", b"NOT ACCESSED",
        ):
            accept("preserve-frozen-corrected-v10-protocol:" + token.decode("ascii"),
                   token in protocol)
        accept("retain-all-twelve-owned-independent-native-source-files",
               sum(len(row["sources"]) for row in FAMILIES.values()) == 12)
        accept("retain-exact-five-owned-independent-native-elf-roles",
               sum(len(row["native"]) for row in FAMILIES.values()) == 5)
        accept("retain-exact-original-edge-223198-over-49",
               EDGE_CHECKS == 223198 and EDGE_CATEGORIES == 49)
        accept("retain-exact-original-deep-393-with-64-seeded",
               DEEP_CHECKS == 393 and DEEP_SEEDED_CASES == 64)
        accept("retain-exact-frozen-actual-v8-preimport-owner-failure",
               V8_GENUINE_FAILURE_RELATIVE.endswith(
                   "-v8-diagnostic-native-owner-failure.json.gz"
               )
               and V8_GENUINE_FAILURE_SHA256
               == "2f8bfcba726d729865cb8411a25ef1c3e0633e80c70af8895e5875a71f15ed7b")
        accept("retain-exact-frozen-actual-v9-cached-compiler-owner-failure",
               V9_GENUINE_FAILURE_RELATIVE.endswith(
                   "-v9-diagnostic-native-owner-failure.json.gz"
               ) and V9_GENUINE_FAILURE_SHA256
               == "04e52f831534458e9af50ad3ab962d78ad43e6a8725cbfccfee37bf9c234f07c")
        v9_actual = {
            "schema": "rebar-postfinal-from-scratch-audit-v9-native-owner-worker-failure",
            "status": "FAIL", "family": "rust",
            "candidate_module": "candidates.rust_candidate",
            "actual_returncode": 1, "signal": None, "timed_out": False,
            "stdout_bytes": 0, "stderr_bytes": 203,
            "stdout_sha256":
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "stderr_sha256":
                "7cfcf842efd492372ee01c330db0fc632aac9182c5f5b45870c5286a3e841097",
            "production_observations_invented": False,
            "qualifies_current_engine": False,
        }
        v9_failure = {
            "schema": "rebar-postfinal-current-build-proofs-v9-native-owner-failure",
            "status": "FAIL", "result": "FAIL", "mode": "diagnostic",
            "candidate_family": "RUST",
            "candidate_module": "candidates.rust_candidate",
            "stage": "before-original-edge", "native_worker_crashed": True,
            "refresh_protocol_path": V9_REFRESH_PROTOCOL_RELATIVE,
            "refresh_protocol_sha256": V9_REFRESH_PROTOCOL_SHA256,
            "passing_evidence_published": False, "campaign_qualified": False,
            "original_edge_worker_started": False,
            "original_deep_worker_started": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            "complete_actual_native_worker": copy.deepcopy(v9_actual),
        }
        accept("validate-real-v9-cached-compiler-failure-shape-in-memory",
               validate_v9_failure(copy.deepcopy(v9_failure)) is None)
        for field, forged in (
            ("schema", "rebar-postfinal-current-build-proofs-v10-native-owner-failure"),
            ("status", "PASS"), ("result", "PASS"), ("mode", "qualified"),
            ("candidate_family", "ZIG"),
            ("candidate_module", "candidates.zig_candidate"),
            ("stage", "after-original-edge"), ("native_worker_crashed", False),
            ("refresh_protocol_path", PROTOCOL_RELATIVE),
            ("refresh_protocol_sha256", REFRESH_PROTOCOL_SHA256),
            ("passing_evidence_published", True), ("campaign_qualified", True),
            ("original_edge_worker_started", True),
            ("original_deep_worker_started", True),
            ("performance", "MEASURED"), ("holdout", "ACCESSED"),
        ):
            changed = copy.deepcopy(v9_failure)
            changed[field] = forged
            controls.append(rejected(
                "reject-forged-genuine-v9-owner-failure:" + field,
                lambda document=changed: validate_v9_failure(document),
            ))
        for field, forged in (
            ("schema", "rebar-postfinal-from-scratch-audit-v10-native-owner-worker"),
            ("status", "PASS"), ("family", "zig"),
            ("candidate_module", "candidates.zig_candidate"),
            ("actual_returncode", 0), ("signal", 9), ("timed_out", True),
            ("stdout_bytes", 1), ("stderr_bytes", 202),
            ("stdout_sha256", "0" * 64), ("stderr_sha256", "0" * 64),
            ("production_observations_invented", True),
            ("qualifies_current_engine", True),
        ):
            changed = copy.deepcopy(v9_failure)
            changed["complete_actual_native_worker"][field] = forged
            controls.append(rejected(
                "reject-forged-genuine-v9-203-byte-worker-stream:" + field,
                lambda document=changed: validate_v9_failure(document),
            ))
        v9_summary = {
            "path": V9_GENUINE_FAILURE_RELATIVE,
            "sha256": V9_GENUINE_FAILURE_SHA256, "status": "FAIL",
            "stage": "before-original-edge",
            "candidate_module": "candidates.rust_candidate",
            "actual_returncode": 1, "stdout_bytes": 0, "stderr_bytes": 203,
            "stdout_sha256": v9_actual["stdout_sha256"],
            "stderr_sha256": v9_actual["stderr_sha256"],
            "original_edge_worker_started": False,
            "qualifies_current_engine": False,
        }
        accept("validate-genuine-v9-incident-before-any-historical-read",
               validate_v9_failure_summary(
                   copy.deepcopy(v9_summary), "source-only V10 incident",
               ) is None)
        for field, forged in (
            ("path", V8_GENUINE_FAILURE_RELATIVE),
            ("sha256", V8_GENUINE_FAILURE_SHA256), ("status", "PASS"),
            ("stage", "after-original-edge"),
            ("candidate_module", "candidates.zig_candidate"),
            ("actual_returncode", 0), ("stdout_bytes", 1),
            ("stderr_bytes", 202), ("stdout_sha256", "0" * 64),
            ("stderr_sha256", "0" * 64),
            ("original_edge_worker_started", True),
            ("qualifies_current_engine", True),
        ):
            changed = copy.deepcopy(v9_summary)
            changed[field] = forged
            controls.append(rejected(
                "reject-forged-genuine-v9-audit-incident:" + field,
                lambda document=changed: validate_v9_failure_summary(
                    document, "source-only V10 forged incident",
                ),
            ))
        accept("retain-exact-frozen-actual-two-reference-cpython-v5-baseline",
               BASELINE_SHA256
               == "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916")
        accept("retain-exact-real-original-rust-c-zig-failures",
               {name: (row[1], row[2])
                for name, row in HISTORICAL_EDGE_FAILURES.items()} == {
                   "rust": (
                       "3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8",
                       16,
                   ),
                   "vm": (
                       "2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c",
                       33,
                   ),
                   "zig": (
                       "5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a",
                       16,
                   ),
               })
        base_digest = synthetic_digest("actual-v10-source-report")
        strict_digest = synthetic_digest("actual-v10-strict-report")
        synthetic_sources = {
            "base_source": synthetic_digest("immutable-v10-source-audit"),
            "strict_source": synthetic_digest("immutable-v10-strict-audit"),
        }
        accept("require-explicit-two-actual-published-v10-reports-in-memory",
               validated_report_pins(
                   True, base_digest, strict_digest,
                   synthetic_sources=synthetic_sources,
               ) == {**synthetic_sources,
                     "base_report": base_digest, "strict_report": strict_digest})
        accept("diagnostic-never-claims-all-family-report-pins",
               validated_report_pins(False, None, None) is None)
        for bad in (None, "", "0", "A" * 64, "z" * 64,
                    synthetic_sources["base_source"],
                    synthetic_sources["strict_source"], strict_digest):
            controls.append(rejected(
                "reject-missing-fake-crossed-v10-base-report:" + repr(bad),
                lambda value=bad: validated_report_pins(
                    True, value, strict_digest,
                    synthetic_sources=synthetic_sources,
                ),
            ))
        for bad in (None, "", "0", "A" * 64, "z" * 64,
                    synthetic_sources["base_source"],
                    synthetic_sources["strict_source"], base_digest):
            controls.append(rejected(
                "reject-missing-fake-crossed-v10-strict-report:" + repr(bad),
                lambda value=bad: validated_report_pins(
                    True, base_digest, value,
                    synthetic_sources=synthetic_sources,
                ),
            ))
        for family in FAMILIES:
            owner, record, native = synthetic_owner(family)
            accept("accept-in-memory-exact-stage07-owner-control:" + family,
                   validate_owner(owner, copy.deepcopy(record), family, native)
                   == record)
            expanded = copy.deepcopy(record)
            expanded_guards = expanded["stage07_matcher_descendant_guards"]
            expanded_names = ["re._compiler", "re._genuinely_discovered", "re._parser"]
            expanded_rows = [
                {"module": name, "blocked": True, "sentinel_identity": True,
                 "cache_identity": True, "sentinel_type_exact": True}
                for name in expanded_names
            ]
            expanded_guards["discovered_descendants"] = expanded_names
            expanded_guards["observations_before"] = copy.deepcopy(expanded_rows)
            expanded_guards["observations_after"] = copy.deepcopy(expanded_rows)
            expanded_guards["cached_alias_count"] = len(expanded_names)
            expanded_guards["helper_alias_replacement_count"] = len(expanded_names)
            accept("retain-every-actual-additional-sorted-stage07-descendant:"
                   + family,
                   validate_owner(owner, copy.deepcopy(expanded), family, native)
                   == expanded)
            for genuine_alias_count in (0, 1):
                observed_aliases = copy.deepcopy(record)
                observed_alias_guards = observed_aliases[
                    "stage07_matcher_descendant_guards"
                ]
                observed_alias_guards["cached_alias_count"] = genuine_alias_count
                observed_alias_guards["helper_alias_replacement_count"] = (
                    genuine_alias_count
                )
                accept("accept-exact-real-stage07-retained-alias-count:"
                       + family + ":" + str(genuine_alias_count),
                       validate_owner(
                           owner, copy.deepcopy(observed_aliases), family, native,
                       ) == observed_aliases)
            for field, forged in (
                ("stage07_source_sha256", "0" * 64),
                ("required_descendants", ["re._compiler"]),
                ("required_descendants", ["re._parser"]),
                ("required_descendants", ["re._parser", "re._compiler"]),
                ("required_descendants", ["re._compiler", "re._parser", "re.fake"]),
                ("discovered_descendants", ["re._compiler"]),
                ("discovered_descendants", ["re._parser"]),
                ("discovered_descendants", ["re._parser", "re._compiler"]),
                ("discovered_descendants",
                 ["re._compiler", "re._compiler", "re._parser"]),
                ("discovered_descendants",
                 ["re._compiler", "re._foreign", "re._parser"]),
                ("cached_alias_count", -1),
                ("cached_alias_count", 0),
                ("cached_alias_count", 1),
                ("cached_alias_count", True),
                ("helper_alias_replacement_count", 0),
                ("helper_alias_replacement_count", -1),
                ("helper_alias_replacement_count", True),
                ("all_cached_aliases_same_sentinel", False),
                ("before_matching_verified", False),
                ("after_matching_verified", False),
                ("observations_before", []),
                ("observations_after", []),
            ):
                changed = copy.deepcopy(record)
                changed["stage07_matcher_descendant_guards"][field] = forged
                controls.append(rejected(
                    "reject-cached-compiler-parser-alias-forgery:"
                    + family + ":" + field + ":" + repr(forged),
                    lambda row=changed, role=family, expected=native:
                        validate_owner(owner, row, role, expected),
                ))
            for field in ("stage07_matcher_descendant_guards",
                          "stage07_guard_sentinel"):
                changed = copy.deepcopy(record)
                del changed[field]
                controls.append(rejected(
                    "reject-missing-genuine-stage07-guard-record:"
                    + family + ":" + field,
                    lambda row=changed, role=family, expected=native:
                        validate_owner(owner, row, role, expected),
                ))
            for phase in ("observations_before", "observations_after"):
                for index, module in enumerate(("re._compiler", "re._parser")):
                    for field, forged in (
                        ("module", "re._restored_live_compiler"),
                        ("blocked", False), ("sentinel_identity", False),
                        ("cache_identity", False), ("sentinel_type_exact", False),
                    ):
                        changed = copy.deepcopy(record)
                        changed["stage07_matcher_descendant_guards"][phase][index][field] = forged
                        controls.append(rejected(
                            "reject-live-or-forged-stage07-cached-descendant:"
                            + family + ":" + phase + ":" + module + ":" + field,
                            lambda row=changed, role=family, expected=native:
                                validate_owner(owner, row, role, expected),
                        ))
                changed = copy.deepcopy(record)
                changed["stage07_matcher_descendant_guards"][phase].pop()
                controls.append(rejected(
                    "reject-dropped-stage07-cached-descendant:"
                    + family + ":" + phase,
                    lambda row=changed, role=family, expected=native:
                        validate_owner(owner, row, role, expected),
                ))
                changed = copy.deepcopy(record)
                changed["stage07_matcher_descendant_guards"][phase].reverse()
                controls.append(rejected(
                    "reject-reordered-stage07-cached-descendants:"
                    + family + ":" + phase,
                    lambda row=changed, role=family, expected=native:
                        validate_owner(owner, row, role, expected),
                ))
                changed = copy.deepcopy(record)
                duplicated = changed["stage07_matcher_descendant_guards"][phase]
                duplicated.append(copy.deepcopy(duplicated[0]))
                controls.append(rejected(
                    "reject-duplicate-stage07-cached-descendant-observation:"
                    + family + ":" + phase,
                    lambda row=changed, role=family, expected=native:
                        validate_owner(owner, row, role, expected),
                ))
            for field in SENTINEL_TRUE_FIELDS:
                changed = copy.deepcopy(record)
                changed["stage07_guard_sentinel"][field] = False
                controls.append(rejected(
                    "reject-forged-cached-stage07-sentinel:"
                    + family + ":" + field,
                    lambda row=changed, role=family, expected=native:
                        validate_owner(owner, row, role, expected),
                ))
            changed = copy.deepcopy(record)
            changed["stage07_guard_sentinel"]["stage07_source_sha256"] = "0" * 64
            controls.append(rejected(
                "reject-unfrozen-stage07-source:" + family,
                lambda row=changed, role=family, expected=native:
                    validate_owner(owner, row, role, expected),
            ))
            for field, value in (
                ("status", "FAIL"), ("result", "FAIL"), ("passed", False),
                ("candidate_module", "candidates.foreign_candidate"),
                ("standard_pickle_check_count", 15),
                ("standard_pickle_failure_count", 1),
                ("regex_guard_count", 12),
                ("native_loader_guard_count", 4),
                ("persistent_cross_engine_guard", False),
                ("genuine_matching_executed", False),
                ("external_regex_packages", 1),
                ("benchmark_or_timing_executed", True),
                ("holdout_or_case_fixture_access", True),
                ("native_binary_sha256", {"candidates/foreign.so": "0" * 64}),
            ):
                changed = copy.deepcopy(record)
                changed[field] = value
                controls.append(rejected(
                    "reject-incomplete-or-foreign-corrected-native-owner:"
                    + family + ":" + field,
                    lambda row=changed, role=family, expected=native:
                        validate_owner(owner, row, role, expected),
                ))
            for field in ("regex_guard_observations_after",
                          "foreign_engine_guard_observations_after",
                          "native_loader_guard_observations_after"):
                changed = copy.deepcopy(record)
                changed[field] = [{"substituted": True}]
                controls.append(rejected(
                    "reject-after-matching-guard-identity-drift:"
                    + family + ":" + field,
                    lambda row=changed, role=family, expected=native:
                        validate_owner(owner, row, role, expected),
                ))
            dropped = copy.deepcopy(record)
            dropped["standard_pickle_checks"].pop()
            controls.append(rejected(
                "reject-missing-real-public-pickle-observation:" + family,
                lambda row=dropped, role=family, expected=native:
                    validate_owner(owner, row, role, expected),
            ))
            broken = copy.deepcopy(record)
            broken["standard_pickle_checks"][0]["passed"] = False
            controls.append(rejected(
                "reject-pass-shaped-real-failed-pickle-observation:" + family,
                lambda row=broken, role=family, expected=native:
                    validate_owner(owner, row, role, expected),
            ))
            for qualified in (False, True):
                scope = "qualified" if qualified else "diagnostic"
                passed = edge_target(family, qualified, True)
                failed = edge_target(family, qualified, False)
                owner_failure = owner_failure_target(family, qualified)
                crash = producer_failure_target(family, qualified, False)
                invalidated = invalidated_target(family, qualified, False)
                paths = (passed, failed, owner_failure, crash, invalidated)
                accept("preserve-five-distinct-exclusive-v10-edge-destinations:"
                       + family + ":" + scope,
                       len(set(paths)) == 5
                       and all(path.parent == ROOT / "candidates/evidence"
                               and "-v10-" in path.name
                               and scope in path.name for path in paths))
            accept("never-qualify-single-family-v10-diagnostic:" + family,
                   edge_target(family, False, True)
                   != edge_target(family, True, True))
            paths = (
                deep_target(family, True), deep_target(family, False),
                producer_failure_target(family, True, True),
                invalidated_target(family, True, True),
            )
            accept("preserve-four-distinct-exclusive-v10-deep-destinations:" + family,
                   len(set(paths)) == 4
                   and all(path.parent == ROOT / "candidates/audits"
                           and "-V10-" in path.name for path in paths))
        for name, action in (
            ("builtin-candidate-import", lambda: builtins.__import__("candidates")),
            ("importlib-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("builtin-external-engine", lambda: builtins.__import__("regex")),
            ("importlib-external-engine", lambda: importlib.import_module("regex")),
            ("genuine-v8-failure-evidence",
             lambda: read_regular(ROOT / V8_GENUINE_FAILURE_RELATIVE,
                                  "forbidden source-only V8 failure evidence")),
            ("genuine-v9-failure-evidence",
             lambda: read_regular(ROOT / V9_GENUINE_FAILURE_RELATIVE,
                                  "forbidden source-only V9 failure evidence")),
            ("genuine-v5-baseline-evidence",
             lambda: read_regular(ROOT / BASELINE_RELATIVE,
                                  "forbidden source-only V5 baseline evidence")),
            ("actual-v10-source-report",
             lambda: read_regular(ROOT / V10_BASE_REPORT_RELATIVE,
                                  "forbidden source-only V10 base evidence")),
            ("actual-v10-strict-report",
             lambda: read_regular(ROOT / V10_STRICT_REPORT_RELATIVE,
                                  "forbidden source-only V10 strict evidence")),
            ("performance-or-holdout",
             lambda: builtins.open(ROOT / "performance" / "holdout.json", "rb")),
            ("unrelated-read", lambda: builtins.open(ROOT / "README.md", "rb")),
            ("clock", lambda: time.perf_counter()),
            ("subprocess", lambda: subprocess.run(["forbidden"])),
            ("temporary-directory", lambda: tempfile.mkdtemp()),
            ("direct-path-write",
             lambda: (ROOT / "forbidden-v10-write").write_bytes(b"blocked")),
            ("file-removal", lambda: os.unlink(str(ROOT / "forbidden-v10-removal"))),
            ("file-replacement", lambda: os.replace("forbidden-v10-a", "forbidden-v10-b")),
            ("unpublished-qualified-edge-report-pins",
             lambda: main(["--qualified-edge", "--module",
                           "candidates.rust_candidate"])),
            ("unpublished-qualified-deep-report-pins",
             lambda: main(["--qualified-deep", "--module",
                           "candidates.rust_candidate"])),
        ):
            controls.append(rejected("enforce-genuine-v10-source-only-boundary:" + name,
                                     action))
        accept("block-builtin-and-importlib-candidate-and-foreign-engine-imports",
               effects["candidate_import_attempts_blocked"] >= 4)
        accept("never-load-a-candidate-during-corrected-v10-source-controls",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
        accept("enforce-at-least-150-distinct-corrected-source-poison-controls",
               len(controls) >= 150)
        require(len({row["name"] for row in controls}) == len(controls),
                "the corrected V10 source controls silently duplicated a case")
        require(all(row["passed"] for row in controls),
                "a real corrected sentinel, native owner, or source-only control failed")
        observed = dict(effects)
    verify_runtime()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS",
        "result": "PASS", "passed": True,
        "check_count": len(controls), "checks": controls,
        "candidate_imports": 0, "subprocesses": 0,
        "file_writes": 0, "clock_samples": 0,
        "historical_evidence_reads": 0,
        "actual_audit_report_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "original_edge_checks": EDGE_CHECKS,
        "original_edge_categories": EDGE_CATEGORIES,
        "original_deep_checks": DEEP_CHECKS,
        "original_deep_seeded_cases": DEEP_SEEDED_CASES,
        "actual_v8_guard_failure_sha256": V8_GENUINE_FAILURE_SHA256,
        "actual_v9_cached_compiler_failure_sha256": V9_GENUINE_FAILURE_SHA256,
        "actual_official_cpython_baseline_sha256": BASELINE_SHA256,
        "v10_refresh_protocol_sha256": REFRESH_PROTOCOL_SHA256,
        "v10_native_owner_source_sha256": V10_BASE_SOURCE_SHA256,
        "v10_no_delegation_source_sha256": V10_STRICT_SOURCE_SHA256,
        "v10_native_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
        "required_cached_regex_descendants": ["re._compiler", "re._parser"],
        "blocked_effect_attempts": observed,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--diagnostic-edge", action="store_true")
    modes.add_argument("--qualified-edge", action="store_true")
    modes.add_argument("--qualified-deep", action="store_true")
    parser.add_argument("--module", choices=tuple(
        row["module"] for row in FAMILIES.values()
    ))
    parser.add_argument("--base-report-sha256")
    parser.add_argument("--strict-report-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    if options.self_test:
        require(options.module is None and options.base_report_sha256 is None
                and options.strict_report_sha256 is None,
                "a candidate-free V10 proof cannot select a production role or evidence")
        report = candidate_free_self_test()
    else:
        require(options.module is not None,
                "a genuine V10 correctness run requires exactly one native family")
        family = next(name for name, row in FAMILIES.items()
                      if row["module"] == options.module)
        if options.diagnostic_edge:
            require(options.base_report_sha256 is None
                    and options.strict_report_sha256 is None,
                    "a V10 diagnostic cannot claim all-family audit qualification")
            report = refresh_edge(family, qualified=False)
        elif options.qualified_edge:
            validated_report_pins(True, options.base_report_sha256,
                                  options.strict_report_sha256)
            report = refresh_edge(
                family, qualified=True,
                base_digest=options.base_report_sha256,
                strict_digest=options.strict_report_sha256,
            )
        else:
            validated_report_pins(True, options.base_report_sha256,
                                  options.strict_report_sha256)
            report = refresh_deep(family, options.base_report_sha256,
                                  options.strict_report_sha256)
    print(json.dumps(report, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")), flush=True)
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofV10Failure as error:
        print(json.dumps({
            "schema": SCHEMA + "-preserved-failure", "status": "FAIL",
            "message": str(error), "evidence": error.evidence,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")),
            file=sys.stderr, flush=True)
        raise SystemExit(1) from error
