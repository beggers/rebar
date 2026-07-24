#!/usr/bin/env python3
"""Run unchanged frozen correctness suites against independently rebuilt engines."""

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
import zlib


ROOT = Path(__file__).resolve().parent.parent
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-postfinal-current-build-proofs-v8"
SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v8.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V8.md"
REFRESH_PROTOCOL_SHA256 = (
    "76e66c091ae06ad56b8f4e22c76f4db44810cdb512b839201c9cc7cb83f4cfa0"
)
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
EDGE_SEED = 2026072329
EDGE_CHECKS = 223198
EDGE_CATEGORIES = 49
EDGE_SEEDED_CASES = 8
EDGE_UNICODE_STRIDE = 4099
EDGE_REFERENCE_SHA256 = (
    "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
)
EDGE_INDEPENDENT_SEEDS = {
    "edge_generation": 2026072329,
    "memory_safety": 5928217332825410871,
    "module_api": 35403857216905324734871187764,
    "object_contract": 5928217332825411394,
    "parser_grammar": 6518143889424763005106639421778,
    "repeat_stream": 23157159151883287,
}
DEEP_SCHEMA = "rebar-rust-v8-deep-public-contract-v1"
DEEP_SEED = 2026072347
DEEP_CHECKS = 393
DEEP_SEEDED_CASES = 64
DEEP_REFERENCE_SHA256 = (
    "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8"
)
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_CHILD_OUTPUT_BYTES = 2 * 1024 * 1024

# Only the actually generated, actually published all-family V8 reports may
# fill these pins. A guessed, historical, synthetic, or source-only digest is
# never sufficient to run a campaign-qualified correctness proof.
V8_SOURCE_AUDIT_SHA256 = (
    "14b8daeebfb620eafa778529f6bf11e1a4f48256dd010b25621f4e94666692c6"
)
V8_SOURCE_REPORT_SHA256: str | None = None
V8_STRICT_AUDIT_SHA256 = (
    "bb22b1983c11a896d3639077050dfaac746876ccbb9e4909518fb33d19987c01"
)
V8_STRICT_REPORT_SHA256: str | None = None

OWNERSHIP_PROTOCOL_RELATIVE = "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V8.md"
V8_SOURCE_AUDIT_RELATIVE = "tools/postfinal_from_scratch_audit_v8.py"
V8_SOURCE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V8.json"
V8_STRICT_AUDIT_RELATIVE = "tools/postfinal_no_delegation_audit_v8.py"
V8_STRICT_REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V8.json"

FROZEN_INPUTS = {
    "GOAL.md":
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    "tools/rust_v7_edge_oracle.py":
        "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca",
    "tools/rust_v8_deep_contract_oracle.py":
        "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978",
    "tools/rust_v8_multi_candidate_contract.py":
        "167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70",
    "tools/postfinal_current_build_proofs_v7.py":
        "9e25e5cbab24220b27ac279e17a5b02f48a5583f2dd27b93eb7d811ae6b827ff",
    V8_SOURCE_AUDIT_RELATIVE: V8_SOURCE_AUDIT_SHA256,
    V8_STRICT_AUDIT_RELATIVE: V8_STRICT_AUDIT_SHA256,
    OWNERSHIP_PROTOCOL_RELATIVE:
        "5c60e6ce63ff1e4c5593eaafe29971cb3557b1a0389dcd5cf41cfb00647bc399",
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V7.md":
        "781cf1e4c85a1de6d5d7d30ea8f451f0fd3417e0a81747ab8e1aa204b6478912",
    "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz":
        "db43cbf8be1d6891eb4f009b8ae92995a6434f9753b944fbf0a8ed0b44237192",
    "candidates/evidence/"
    "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json":
        "62aba93fa8bdd6df7be93199aea6f58be7b24c095750c520179e96b98084b75a",
}

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
        "module": "candidates.rust_candidate",
        "contract_name": "RUST",
        "sources": (
            "candidates/rust_candidate.py",
            "candidates/rust/py_bridge.c",
            "candidates/rust/src/lib.rs",
            "candidates/rust/src/search.rs",
            "candidates/rust/src/newline.rs",
            "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
        "native": {
            "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "engine": "candidates/_rust_engine.so",
        },
    },
    "vm": {
        "module": "candidates.vm_candidate",
        "contract_name": "C",
        "sources": ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
        "native": {
            "native": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        },
    },
    "zig": {
        "module": "candidates.zig_candidate",
        "contract_name": "ZIG",
        "sources": (
            "candidates/zig_candidate.py",
            "candidates/zig/py_bridge.c",
            "candidates/zig/mini_regex.zig",
        ),
        "native": {
            "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
            "engine": "candidates/_zig_probe.so",
        },
    },
}

REGEX_GUARDS = (
    ("re", "compile"), ("re", "search"), ("re", "match"),
    ("re", "fullmatch"), ("re", "findall"), ("re", "finditer"),
    ("re", "split"), ("re", "sub"), ("re", "subn"),
    ("re", "_compile"), ("_sre", "compile"),
    ("re._compiler", "compile"), ("re._parser", "parse"),
)


class ProofV8Error(AssertionError):
    """The unchanged frozen suite or a current native provenance check failed."""


class ProofV8Failure(ProofV8Error):
    def __init__(self, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ProofV8Error(message)


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, allow_nan=False,
                   sort_keys=True, indent=2)
        + "\n"
    ).encode("ascii")


def decode_json(payload: bytes, label: str) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            require(key not in result, label + " contains a duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value: str) -> Any:
        raise ProofV8Error(label + " contains non-finite JSON: " + value)

    try:
        document = json.loads(
            payload.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=reject_constant,
        )
    except (UnicodeError, ValueError, TypeError) as error:
        raise ProofV8Error(label + " is not complete strict JSON") from error
    require(isinstance(document, dict), label + " is not a JSON object")
    return document


def read_regular(path: Path, label: str) -> bytes:
    require(isinstance(path, Path) and path.is_absolute()
            and path.resolve() == path and not path.is_symlink(),
            label + " is not its exact regular, canonical path")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and 0 <= before.st_size <= MAX_FILE_BYTES,
                label + " is not a bounded regular file")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            payload = stream.read(MAX_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
        require(len(payload) == before.st_size and len(payload) <= MAX_FILE_BYTES,
                label + " changed size or exceeded the bounded reader")
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns),
                label + " changed while it was authenticated")
        return payload
    finally:
        if descriptor != -1:
            os.close(descriptor)


def checked_frozen(relative: str, expected: str) -> bytes:
    require(valid_sha256(expected), "a frozen input has no actual SHA-256")
    path = ROOT / relative
    payload = read_regular(path, "frozen V8 input: " + relative)
    require(hashlib.sha256(payload).hexdigest() == expected,
            "an immutable frozen correctness input changed: " + relative)
    return payload


def decode_archive(
    raw: bytes, label: str, *, compact: bool = False,
) -> tuple[dict[str, Any], bytes]:
    require(isinstance(raw, bytes) and 10 <= len(raw) <= MAX_FILE_BYTES,
            label + " is not bounded gzip evidence")
    require(raw[:2] == b"\x1f\x8b" and raw[2] == 8 and raw[3] == 0
            and raw[4:8] == b"\x00\x00\x00\x00",
            label + " has invalid or nondeterministic gzip metadata")
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        payload = decoder.decompress(raw, MAX_FILE_BYTES + 1)
        require(len(payload) <= MAX_FILE_BYTES and not decoder.unconsumed_tail,
                label + " exceeds the decompression boundary")
        payload += decoder.flush(MAX_FILE_BYTES + 1 - len(payload))
        require(len(payload) <= MAX_FILE_BYTES and decoder.eof
                and not decoder.unused_data,
                label + " is truncated, oversized, or has appended gzip data")
    except (ValueError, zlib.error) as error:
        raise ProofV8Error(label + " is not complete bounded gzip") from error
    document = decode_json(payload, label)
    expected = (
        json.dumps(document, ensure_ascii=True, allow_nan=False,
                   sort_keys=True, separators=(",", ":")).encode("ascii")
        if compact else canonical_json(document)
    )
    require(payload == expected,
            label + " is not the unchanged producer's full canonical JSON")
    return document, payload


def verify_runtime() -> None:
    require(platform.python_implementation() == "CPython"
            and sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and Path(sys.executable).resolve() == PINNED_EXECUTABLE.resolve()
            and sys.flags.isolated == 1,
            "V8 correctness proofs require the exact pinned CPython 3.14.6")
    require(unicodedata.unidata_version == "16.0.0",
            "V8 correctness proofs require frozen Unicode 16.0.0")
    require(sys.dont_write_bytecode
            and os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
            "V8 correctness proofs require -B and PYTHONDONTWRITEBYTECODE=1")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "the correctness controller must never import a production candidate")


def checked_family(name: str) -> dict[str, Any]:
    require(name in FAMILIES, "an unknown independent native family was requested")
    return FAMILIES[name]


def snapshot_family(name: str) -> dict[str, Any]:
    family = checked_family(name)
    sources: dict[str, str] = {}
    for relative in family["sources"]:
        payload = read_regular(ROOT / relative, "current owned source " + relative)
        sources[relative] = hashlib.sha256(payload).hexdigest()
    native: dict[str, str] = {}
    for relative in family["native"].values():
        payload = read_regular(ROOT / relative, "current owned native ELF " + relative)
        require(payload.startswith(b"\x7fELF"),
                "a purported independently rebuilt native engine is not ELF: "
                + relative)
        native[relative] = hashlib.sha256(payload).hexdigest()
    require(len(sources) == len(family["sources"])
            and len(native) == len(family["native"]),
            "the individual native source or ELF denominator changed")
    return {
        "family": name,
        "module": family["module"],
        "source_sha256_by_path": sources,
        "native_sha256_by_path": native,
    }


def source_audit_module(expected_sha256: str | None = None) -> tuple[Any, str]:
    payload = read_regular(ROOT / V8_SOURCE_AUDIT_RELATIVE,
                           "actual V8 individual native-owner controller")
    observed = hashlib.sha256(payload).hexdigest()
    if expected_sha256 is not None:
        require(observed == expected_sha256,
                "the individually authenticated V8 native controller changed")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    module = importlib.import_module("tools.postfinal_from_scratch_audit_v8")
    require(Path(module.__file__).resolve() == ROOT / V8_SOURCE_AUDIT_RELATIVE,
            "a different individual native-owner controller was substituted")
    require(tuple(module.CORE_FAMILIES) == tuple(FAMILIES),
            "the native-owner controller changed the three genuine families")
    for name, family in FAMILIES.items():
        require(tuple(module.OWNED_SOURCE_PATHS[name]) == family["sources"]
                and dict(module.OWNED_NATIVE_PATHS[name]) == family["native"],
                "the V8 native-owner controller changed an independently owned graph")
    return module, observed


def authenticate_history(owner: Any) -> dict[str, dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    for name, (relative, expected, failures) in HISTORICAL_EDGE_FAILURES.items():
        raw = checked_frozen(relative, expected)
        document, _ = decode_archive(raw, "preserved original " + name + " edge failure")
        record = owner.validate_historical_edge(document, name, expected)
        require(record.get("status") == "FAIL"
                and record.get("qualifies_current_engine") is False
                and record.get("failed") == failures
                and record.get("checks") == EDGE_CHECKS
                and record.get("category_count") == EDGE_CATEGORIES
                and record.get("archive_sha256") == expected,
                "a genuine historical edge failure was changed or concealed: " + name)
        observed[name] = record
    require(set(observed) == set(FAMILIES),
            "the complete three-family historical failure record was weakened")
    return observed


def required_campaign_pins(
    synthetic: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    values: Mapping[str, Any] = {
        "source_audit": V8_SOURCE_AUDIT_SHA256,
        "source_report": V8_SOURCE_REPORT_SHA256,
        "strict_audit": V8_STRICT_AUDIT_SHA256,
        "strict_report": V8_STRICT_REPORT_SHA256,
    }
    if synthetic is not None:
        require(isinstance(synthetic, Mapping) and set(synthetic) == set(values),
                "a source-only campaign-pin control changed its four denominators")
        values = synthetic
    for label, digest in values.items():
        require(valid_sha256(digest),
                "the actually frozen, passing all-three-family V8 " + label
                + " has not been independently published")
    require(len(set(values.values())) == len(values),
            "independent actual V8 source and report digests cannot be duplicated")
    return {key: str(value) for key, value in values.items()}


def load_contract() -> Any:
    relative = "tools/rust_v8_multi_candidate_contract.py"
    checked_frozen(relative, FROZEN_INPUTS[relative])
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    contract = importlib.import_module("tools.rust_v8_multi_candidate_contract")
    require(Path(contract.RUNNER).resolve() == ROOT / relative,
            "the unchanged frozen multi-candidate contract was substituted")
    for key, value in {
        "EDGE_SCRIPT_SHA256": FROZEN_INPUTS["tools/rust_v7_edge_oracle.py"],
        "EDGE_SEED": EDGE_SEED,
        "EDGE_CHECKS": EDGE_CHECKS,
        "EDGE_CATEGORIES": EDGE_CATEGORIES,
        "EDGE_REFERENCE_SHA256": EDGE_REFERENCE_SHA256,
        "EDGE_INDEPENDENT_SEEDS": EDGE_INDEPENDENT_SEEDS,
        "FROZEN_SCHEMA": DEEP_SCHEMA,
        "FROZEN_SUITE_SHA256": FROZEN_INPUTS[
            "tools/rust_v8_deep_contract_oracle.py"
        ],
        "FROZEN_FAILURE_SHA256": FROZEN_INPUTS[
            "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
        ],
        "FROZEN_SEED": DEEP_SEED,
        "FROZEN_CASES": DEEP_CHECKS,
        "FROZEN_SEEDED_CASES": DEEP_SEEDED_CASES,
        "FROZEN_REFERENCE_SHA256": DEEP_REFERENCE_SHA256,
    }.items():
        require(getattr(contract, key, None) == value,
                "the unchanged frozen proof producer was altered: " + key)
    for name, family in FAMILIES.items():
        spec = contract.SPECS.get(family["module"])
        require(spec is not None and spec.module == family["module"]
                and spec.family == family["contract_name"]
                and spec.public_path == family["sources"][0],
                "the unchanged original producer substituted a native family: " + name)
    return contract


def authenticate_v8_audits(owner: Any, pins: Mapping[str, str]) -> dict[str, Any]:
    checked_frozen(V8_SOURCE_AUDIT_RELATIVE, pins["source_audit"])
    checked_frozen(V8_STRICT_AUDIT_RELATIVE, pins["strict_audit"])
    base_raw = checked_frozen(V8_SOURCE_REPORT_RELATIVE, pins["source_report"])
    strict_raw = checked_frozen(V8_STRICT_REPORT_RELATIVE, pins["strict_report"])
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    strict = importlib.import_module("tools.postfinal_no_delegation_audit_v8")
    require(Path(strict.__file__).resolve() == ROOT / V8_STRICT_AUDIT_RELATIVE,
            "the actual V8 strict source controller was substituted")
    strict_pins = {
        "base_source": pins["source_audit"],
        "base_report": pins["source_report"],
    }
    base = decode_json(base_raw, "actual all-family V8 source audit")
    graph = strict.validate_base_report(base, strict_pins)
    report = decode_json(strict_raw, "actual all-family V8 no-delegation audit")
    for key, value in {
        "schema": "rebar-postfinal-no-delegation-audit-v8",
        "postfinal_schema": "rebar-postfinal-no-delegation-audit-v8",
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": V8_STRICT_AUDIT_RELATIVE,
        "audit_source_sha256": pins["strict_audit"],
        "base_audit_postfinal_schema": "rebar-postfinal-from-scratch-audit-v8",
        "base_audit_source_path": V8_SOURCE_AUDIT_RELATIVE,
        "base_audit_source_sha256": pins["source_audit"],
        "base_audit_report_path": V8_SOURCE_REPORT_RELATIVE,
        "base_audit_report_sha256": pins["source_report"],
        "native_ownership_protocol_path": OWNERSHIP_PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": owner.PROTOCOL_SHA256,
        "historical_v7_results_qualify_current_build": False,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "verified_match_repr_checks": 6,
        "verified_standard_pickle_count": 48,
        "standard_pickle_failure_count": 0,
    }.items():
        require(report.get(key) == value,
                "the passing all-family V8 no-delegation audit changed: " + key)
    require(report.get("verified_candidate_source_paths") == graph["source_paths"]
            and report.get("native_sha256_by_family")
            == graph["native_sha256_by_family"],
            "the qualified strict audit changed the current all-family source graph")
    workers = report.get("actual_native_owner_workers")
    base_workers = report.get("independent_base_native_owner_workers")
    require(isinstance(workers, dict) and set(workers) == set(FAMILIES)
            and base_workers == base.get("actual_native_owner_workers"),
            "the strict V8 report omitted an independently executed native owner")
    for name in FAMILIES:
        owner.validate_worker(workers[name], name,
                              graph["native_sha256_by_family"][name])
    historical = report.get("historical_current_build_edge_failures")
    require(isinstance(historical, dict) and set(historical) == set(FAMILIES),
            "the strict V8 report concealed an actual historical native failure")
    for name, (_, digest, count) in HISTORICAL_EDGE_FAILURES.items():
        item = historical[name]
        require(isinstance(item, dict) and item.get("status") == "FAIL"
                and item.get("archive_sha256") == digest
                and item.get("failed") == count,
                "the strict V8 audit changed a real historical failure: " + name)
    scope = report.get("postfinal_scope")
    require(isinstance(scope, dict)
            and scope.get("append_only") is True
            and scope.get("exclusive_report_path") == V8_STRICT_REPORT_RELATIVE
            and scope.get("independently_pinned_fresh_v8_base") is True
            and scope.get("historical_v7_reports_qualify_current_build") is False
            and scope.get("actual_edge_failures_preserved") is True
            and scope.get("actual_current_native_binary_count") == 5
            and scope.get("exact_current_owned_candidate_source_count") == 12
            and scope.get("independently_executed_native_owner_workers") == 3
            and scope.get("genuine_public_pickle_checks") == 48
            and scope.get("genuine_match_repr_checks") == 6
            and scope.get("actual_python_matching_guards_per_family") == 13
            and scope.get("persistent_cross_family_import_and_loader_guards") is True
            and scope.get("native_identity_is_independent_of_public_module") is True
            and scope.get("mapped_binaries_hashed_against_static_elf") is True
            and scope.get("benchmark_or_timing_executed") is False
            and scope.get("holdout_or_case_fixture_access") is False,
            "the passing all-family strict V8 ownership boundary was weakened")
    controls = report.get("postfinal_wrapper_self_test")
    require(isinstance(controls, dict) and controls.get("passed") is True
            and controls.get("candidate_imports") == 0
            and controls.get("subprocesses") == 0
            and controls.get("file_reads") == 0
            and controls.get("file_writes") == 0
            and controls.get("clock_samples") == 0,
            "the passing strict V8 source-only protections were weakened")
    return {"graph": graph, "base": base, "strict": report, "pins": dict(pins)}


def edge_target(name: str, qualified: bool, passed: bool) -> Path:
    checked_family(name)
    mode = "qualified" if qualified else "diagnostic"
    status = "pass" if passed else "failures"
    return ROOT / "candidates" / "evidence" / (
        "rust-v7-edge-oracle-" + name
        + "-postfinal-current-build-v8-" + mode + "-" + status + ".json.gz"
    )


def native_owner_failure_target(name: str, qualified: bool) -> Path:
    checked_family(name)
    mode = "qualified" if qualified else "diagnostic"
    return ROOT / "candidates" / "evidence" / (
        "rust-v7-edge-oracle-" + name
        + "-postfinal-current-build-v8-" + mode
        + "-native-owner-failure.json.gz"
    )


def producer_failure_target(name: str, qualified: bool, *, deep: bool) -> Path:
    family = checked_family(name)
    if deep:
        require(qualified, "an unqualified diagnostic cannot start the deep producer")
        return ROOT / "candidates" / "audits" / (
            "RUST-V8-DEEP-CONTRACT-" + family["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V8-PRODUCER-CRASH.json.gz"
        )
    mode = "qualified" if qualified else "diagnostic"
    return ROOT / "candidates" / "evidence" / (
        "rust-v7-edge-oracle-" + name
        + "-postfinal-current-build-v8-" + mode + "-producer-crash.json.gz"
    )


def invalidated_original_target(name: str, qualified: bool, *, deep: bool) -> Path:
    family = checked_family(name)
    if deep:
        require(qualified, "a diagnostic cannot produce a genuine deep archive")
        return ROOT / "candidates" / "audits" / (
            "RUST-V8-DEEP-CONTRACT-" + family["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V8-INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
        )
    mode = "qualified" if qualified else "diagnostic"
    return ROOT / "candidates" / "evidence" / (
        "rust-v7-edge-oracle-" + name
        + "-postfinal-current-build-v8-" + mode
        + "-invalidated-after-owner-failure.json.gz"
    )


def deep_target(name: str, passed: bool) -> Path:
    family = checked_family(name)
    status = "PASS" if passed else "FAILURES"
    return ROOT / "candidates" / "audits" / (
        "RUST-V8-DEEP-CONTRACT-" + family["contract_name"]
        + "-POSTFINAL-CURRENT-BUILD-V8-" + status + ".json.gz"
    )


def fresh_target(path: Path, parent: Path, expected_name: str) -> Path:
    require(path.is_absolute() and path.parent == parent
            and path.name == expected_name and path.resolve() == path,
            "a V8 correctness destination escaped its exact family and directory")
    require(parent.is_dir() and not parent.is_symlink(),
            "an authorized V8 correctness destination parent is unavailable")
    require(not path.exists() and not path.is_symlink(),
            "refusing to overwrite or retry existing V8 correctness evidence")
    return path


def exclusive_publish(path: Path, raw: bytes, *, deep: bool) -> str:
    parent = ROOT / "candidates" / ("audits" if deep else "evidence")
    fresh_target(path, parent, path.name)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
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
    require(read_regular(path, "exclusive frozen V8 correctness archive") == raw,
            "exclusive V8 publication changed the original producer bytes")
    return hashlib.sha256(raw).hexdigest()


def validate_edge_shape(
    document: Any, name: str, snapshot: Mapping[str, Any],
) -> tuple[bool, int]:
    family = checked_family(name)
    require(isinstance(document, dict), "original V8 edge evidence is not an object")
    for key, value in {
        "schema": EDGE_SCHEMA,
        "script_sha256": FROZEN_INPUTS["tools/rust_v7_edge_oracle.py"],
        "oracle": "CPython standard-library re",
        "python": "3.14.6", "unicode": "16.0.0", "locale": "C",
        "module": family["module"],
        "seed": EDGE_SEED,
        "seeded_cases": EDGE_SEEDED_CASES,
        "unicode_stride": EDGE_UNICODE_STRIDE,
        "independent_source_seeds": EDGE_INDEPENDENT_SEEDS,
        "correctness_checks": EDGE_CHECKS,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "json_normalization": {"lone_surrogates": "surrogatepass_utf8_hex"},
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }.items():
        require(document.get(key) == value,
                "the unchanged complete edge producer changed: " + key)
    categories = document.get("categories")
    require(isinstance(categories, dict) and len(categories) == EDGE_CATEGORIES
            and all(isinstance(key, str) and key
                    and type(value) is int and value > 0
                    for key, value in categories.items())
            and sum(categories.values()) == EDGE_CHECKS,
            "the original edge suite lost its complete 223,198/49 denominator")
    failed = document.get("failed")
    failures = document.get("failures")
    actual = document.get("actual_sha256")
    require(type(failed) is int and failed >= 0 and isinstance(failures, list)
            and len(failures) == failed
            and all(isinstance(row, dict) for row in failures)
            and valid_sha256(actual),
            "the original edge suite concealed actual failures or observations")
    require((failed == 0) == (actual == EDGE_REFERENCE_SHA256),
            "the original edge suite relabeled actual differential observations")
    artifacts = document.get("candidate_artifacts")
    require(isinstance(artifacts, list) and all(isinstance(item, dict)
                                                 for item in artifacts),
            "the original edge suite omitted current native artifact provenance")
    expected = {
        "public-python": family["sources"][0],
    }
    for role, relative in family["native"].items():
        expected["native-bridge" if role in {"bridge", "native"}
                 else "native-engine"] = relative
    if name == "rust":
        expected.update({
            "bridge-source": "candidates/rust/py_bridge.c",
            "native-source": "candidates/rust/src/lib.rs",
        })
    fingerprints = dict(snapshot["source_sha256_by_path"])
    fingerprints.update(snapshot["native_sha256_by_path"])
    require(len(artifacts) == len(expected),
            "the complete original edge omitted or repeated an owned native role")
    seen: set[str] = set()
    for item in artifacts:
        require(set(item) == {"role", "path", "sha256"}
                and item["role"] in expected
                and item["role"] not in seen
                and expected[item["role"]] == item["path"]
                and fingerprints.get(item["path"]) == item["sha256"],
                "the complete edge substituted, omitted, repeated, or changed "
                "an exact owned source/native ELF role")
        seen.add(item["role"])
    require(seen == set(expected),
            "the unchanged frozen edge omitted a current native artifact role")
    return failed == 0, failed


def validate_failed_edge_provenance(
    document: Mapping[str, Any], raw: bytes, path: Path, name: str,
    snapshot: Mapping[str, Any], contract: Any,
) -> dict[str, Any]:
    family = checked_family(name)
    passed, count = validate_edge_shape(document, name, snapshot)
    require(not passed and count > 0,
            "only complete genuine failed observations use a failed-edge validator")
    spec = contract.SPECS[family["module"]]
    expected_embedded = contract.frozen_embedded_oracles()
    embedded = document.get("embedded_frozen_oracles")
    require(isinstance(embedded, list) and len(embedded) == len(expected_embedded),
            "a genuine complete edge failure lost a frozen embedded sub-oracle")
    found: set[str] = set()
    for item in embedded:
        require(isinstance(item, dict),
                "a genuine failing embedded frozen sub-oracle is malformed")
        label = item.get("name")
        require(label in expected_embedded and label not in found,
                "a genuine failing edge omitted or repeated a frozen sub-oracle")
        for key, value in expected_embedded[label].items():
            require(item.get(key) == value,
                    "a genuine failing edge changed a frozen sub-oracle: "
                    + label + ":" + key)
        require(isinstance(item.get("schema"), str) and bool(item["schema"]),
                "a genuine failing frozen sub-oracle lost its schema")
        if label == "independent-parser-grammar":
            families = item.get("families")
            require(isinstance(families, list) and len(families) == 16
                    and all(isinstance(value, str) for value in families)
                    and len(set(families)) == len(families),
                    "a genuine failing frozen grammar lost its 16 case families")
        found.add(label)
    actual_paths = {
        item["role"]: (item["path"], item["sha256"])
        for item in document["candidate_artifacts"]
    }
    require(set(actual_paths) == set(contract.expected_edge_paths(spec))
            and all(actual_paths[role][0] == relative
                    for role, relative in contract.expected_edge_paths(spec).items()),
            "the genuine failing edge changed the original native artifact graph")
    complete = dict(actual_paths)
    fingerprints = dict(snapshot["source_sha256_by_path"])
    fingerprints.update(snapshot["native_sha256_by_path"])
    for role, relative in spec.source_paths:
        require(relative in fingerprints,
                "a genuine failing edge omitted a current owned native source")
        current = (relative, fingerprints[relative])
        require(role not in complete or complete[role] == current,
                "a genuine failing edge substituted a current native source role")
        complete[role] = current
    production = [
        {"role": role, "path": relative, "sha256": digest}
        for role, (relative, digest) in sorted(complete.items())
    ]
    return {
        "schema": SCHEMA + "-complete-failed-edge-provenance",
        "path": str(path.resolve()),
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "script_sha256": FROZEN_INPUTS["tools/rust_v7_edge_oracle.py"],
        "seed": EDGE_SEED,
        "checks": EDGE_CHECKS,
        "category_count": EDGE_CATEGORIES,
        "reference_sha256": EDGE_REFERENCE_SHA256,
        "candidate_sha256": document["actual_sha256"],
        "failed": count,
        "module": family["module"],
        "family": family["contract_name"],
        "candidate_artifacts": [
            {"role": role, "path": relative, "sha256": digest}
            for role, (relative, digest) in sorted(actual_paths.items())
        ],
        "production_artifacts": production,
        "campaign_qualified": False,
    }


def validate_original_edge(
    raw: bytes, path: Path, name: str, snapshot: Mapping[str, Any], contract: Any,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    family = checked_family(name)
    document, _ = decode_archive(raw, "complete original " + name + " V8 edge proof")
    passed, _ = validate_edge_shape(document, name, snapshot)
    if passed:
        complete, proof = contract.validate_edge_document(
            document, contract.SPECS[family["module"]],
            hashlib.sha256(raw).hexdigest(), path,
        )
        expected_all = dict(snapshot["source_sha256_by_path"])
        expected_all.update(snapshot["native_sha256_by_path"])
        for relative, actual in complete.values():
            require(expected_all.get(relative) == actual,
                    "the frozen passing edge is not bound to current owned sources/ELFs")
    else:
        proof = validate_failed_edge_provenance(
            document, raw, path, name, snapshot, contract,
        )
    require(proof.get("checks") == EDGE_CHECKS
            and proof.get("category_count") == EDGE_CATEGORIES,
            "the frozen original edge contract changed its full denominator")
    return document, proof, passed


def preflight(name: str, *, qualified: bool) -> dict[str, Any]:
    verify_runtime()
    family = checked_family(name)
    pins = required_campaign_pins() if qualified else None
    frozen = {
        relative: hashlib.sha256(checked_frozen(relative, digest)).hexdigest()
        for relative, digest in FROZEN_INPUTS.items()
    }
    protocol_payload = read_regular(ROOT / PROTOCOL_RELATIVE,
                                   "V8 proof protocol documented before production")
    require(hashlib.sha256(protocol_payload).hexdigest() == REFRESH_PROTOCOL_SHA256,
            "the independently frozen V8 correctness proof protocol was changed")
    ownership_payload = read_regular(
        ROOT / OWNERSHIP_PROTOCOL_RELATIVE,
        "V8 independently owned native-engine protocol",
    )
    owner, owner_sha256 = source_audit_module(
        pins["source_audit"] if pins is not None else V8_SOURCE_AUDIT_SHA256
    )
    require(owner.PROTOCOL_RELATIVE == OWNERSHIP_PROTOCOL_RELATIVE
            and hashlib.sha256(ownership_payload).hexdigest()
            == owner.PROTOCOL_SHA256,
            "the independently authored V8 native-ownership protocol changed")
    historical = authenticate_history(owner)
    audit = authenticate_v8_audits(owner, pins) if pins is not None else None
    snapshot = snapshot_family(name)
    if audit is not None:
        graph = audit["graph"]
        require(snapshot["native_sha256_by_path"]
                == graph["native_sha256_by_family"][name],
                "the individual current ELF changed after both passing V8 audits")
        source_paths = set(graph["source_paths"])
        require(set(snapshot["source_sha256_by_path"]) <= source_paths,
                "the independently audited source graph omitted the chosen family")
    require(family["module"] not in sys.modules,
            "the production candidate leaked into the parent correctness controller")
    return {
        "owner": owner,
        "owner_source_sha256": owner_sha256,
        "protocol_sha256": hashlib.sha256(protocol_payload).hexdigest(),
        "ownership_protocol_sha256": hashlib.sha256(ownership_payload).hexdigest(),
        "frozen_input_sha256": frozen,
        "historical_failures": historical,
        "snapshot": snapshot,
        "audit": audit,
    }


def audited_graph_provenance(state: Mapping[str, Any]) -> dict[str, Any]:
    audit = state["audit"]
    if audit is None:
        return {
            "all_family_audit_qualified": False,
            "all_family_source_sha256_by_path": None,
            "all_family_native_elf_sha256_by_path": None,
        }
    sources: dict[str, str] = {}
    for name in FAMILIES:
        audited = audit["base"]["families"][name]
        public = audited["python_source"]
        sources[public["file"]] = public["sha256"]
        for source in audited["native_sources"]:
            sources[source["file"]] = source["sha256"]
    native: dict[str, str] = {}
    for name in FAMILIES:
        native.update(audit["graph"]["native_sha256_by_family"][name])
    require(len(sources) == 12 and len(native) == 5,
            "a preserved all-family failure lost its 12-source, five-ELF graph")
    return {
        "all_family_audit_qualified": True,
        "all_family_source_sha256_by_path": sources,
        "all_family_native_elf_sha256_by_path": native,
    }


def retain_invalidated_original(
    name: str, *, qualified: bool, deep: bool,
    raw: bytes, passed: bool | None,
) -> tuple[str, str, str]:
    require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_FILE_BYTES
            and (passed is None or type(passed) is bool),
            "a real invalidated original suite lost its bounded actual bytes")
    target = invalidated_original_target(name, qualified, deep=deep)
    parent = ROOT / "candidates" / ("audits" if deep else "evidence")
    fresh_target(target, parent, target.name)
    digest = exclusive_publish(target, raw, deep=deep)
    actual = "NOT VALIDATED" if passed is None else "PASS" if passed else "FAIL"
    return target.relative_to(ROOT).as_posix(), digest, actual


def preserve_native_owner_failure(
    name: str, state: Mapping[str, Any], *, qualified: bool, stage: str,
    actual: Mapping[str, Any], crashed: bool,
    completed_original: tuple[bytes, bool] | None = None,
) -> None:
    require(stage in {
        "before-original-edge", "after-original-edge",
        "before-original-deep", "after-original-deep",
    }, "a genuine isolated native owner changed its exact production stage")
    require(isinstance(actual, Mapping) and actual.get("status") == "FAIL",
            "refusing to invent or relabel a real isolated native-owner failure")
    family = checked_family(name)
    target = native_owner_failure_target(name, qualified)
    fresh_target(target, ROOT / "candidates/evidence", target.name)
    deep = stage in {"before-original-deep", "after-original-deep"}
    is_after = stage in {"after-original-edge", "after-original-deep"}
    require((completed_original is not None) == is_after,
            "a real post-owner failure concealed completed original observations")
    invalidated_path: str | None = None
    invalidated_sha256: str | None = None
    invalidated_original_status: str | None = None
    if completed_original is not None:
        original_raw, original_passed = completed_original
        require(isinstance(original_raw, bytes) and type(original_passed) is bool,
                "a completed original suite lost its real bytes or true status")
        invalidated_path, invalidated_sha256, invalidated_original_status = (
            retain_invalidated_original(
                name, qualified=qualified, deep=deep,
                raw=original_raw, passed=original_passed,
            )
        )
    document = {
        "schema": SCHEMA + "-native-owner-failure",
        "status": "FAIL", "result": "FAIL",
        "mode": "qualified" if qualified else "diagnostic",
        "candidate_family": family["contract_name"],
        "candidate_module": family["module"],
        "stage": stage,
        "native_worker_crashed": crashed,
        "refresh_protocol_path": PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": REFRESH_PROTOCOL_SHA256,
        "complete_actual_native_worker": dict(actual),
        "actual_native_worker_failure_count":
            actual.get("standard_pickle_failure_count"),
        "actual_native_worker_pickle_check_count":
            actual.get("standard_pickle_check_count"),
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "historical_current_build_edge_failures": state["historical_failures"],
        "all_family_audited_provenance": audited_graph_provenance(state),
        "actual_v8_source_audit_report_sha256":
            state["audit"]["pins"]["source_report"] if qualified else None,
        "actual_v8_no_delegation_report_sha256":
            state["audit"]["pins"]["strict_report"] if qualified else None,
        "original_edge_worker_started": stage == "after-original-edge",
        "original_deep_worker_started": stage == "after-original-deep",
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_sha256,
        "invalidated_complete_original_actual_status": invalidated_original_status,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    payload = canonical_json(document)
    require(len(payload) <= MAX_FILE_BYTES,
            "a real bounded native-owner failure exceeded its complete archive limit")
    raw = gzip.compress(payload, compresslevel=9, mtime=0)
    observed, preserved = decode_archive(raw, "complete actual native-owner failure")
    require(observed == document and preserved == payload,
            "the actual isolated native-owner failure lost its complete observations")
    archive_sha256 = exclusive_publish(target, raw, deep=False)
    raise ProofV8Failure(
        "the genuine isolated native owner failed before a qualifying producer",
        {
            "status": "FAIL",
            "candidate_family": family["contract_name"],
            "candidate_module": family["module"],
            "stage": stage,
            "native_worker_crashed": crashed,
            "failure_evidence_path": target.relative_to(ROOT).as_posix(),
            "failure_evidence_sha256": archive_sha256,
            "actual_native_worker_failure_count":
                actual.get("standard_pickle_failure_count"),
            "actual_native_worker_pickle_check_count":
                actual.get("standard_pickle_check_count"),
            "original_edge_worker_started": stage == "after-original-edge",
            "original_deep_worker_started": stage == "after-original-deep",
            "invalidated_complete_original_evidence_path": invalidated_path,
            "invalidated_complete_original_evidence_sha256": invalidated_sha256,
            "invalidated_complete_original_actual_status": invalidated_original_status,
            "passing_evidence_published": False,
            "failure_evidence_exclusively_preserved": True,
            "campaign_qualified": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        },
    )


def native_owner_observation(
    name: str, state: Mapping[str, Any], *, qualified: bool, stage: str,
    completed_original: tuple[bytes, bool] | None = None,
) -> dict[str, Any]:
    owner = state["owner"]
    native = dict(state["snapshot"]["native_sha256_by_path"])
    try:
        report = owner.run_native_worker(name, native)
    except owner.NativeWorkerFailure as error:
        preserve_native_owner_failure(
            name, state, qualified=qualified, stage=stage,
            actual=error.evidence, crashed=True,
            completed_original=completed_original,
        )
        raise AssertionError("an exclusively preserved owner crash unexpectedly returned")
    owner.validate_worker(report, name, native, allow_failure=True)
    require(report.get("genuine_matching_executed") is True
            and report.get("regex_guard_count") == len(REGEX_GUARDS)
            and report.get("persistent_cross_engine_guard") is True
            and report.get("benchmark_or_timing_executed") is False
            and report.get("holdout_or_case_fixture_access") is False,
            "the chosen candidate did not actually match under persistent poison")
    if (report.get("status") != "PASS"
            or report.get("result") != "PASS"
            or report.get("passed") is not True
            or report.get("standard_pickle_failure_count") != 0
            or report.get("standard_pickle_check_count") != 16):
        preserve_native_owner_failure(
            name, state, qualified=qualified, stage=stage,
            actual=report, crashed=False,
            completed_original=completed_original,
        )
        raise AssertionError("an exclusively preserved owner failure unexpectedly returned")
    return report


def child_environment() -> dict[str, str]:
    return {
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT), "LC_ALL": "C", "PATH": "/usr/bin:/bin",
    }


def observed_stream(value: bytes | str | None, *, complete: bool) -> dict[str, Any]:
    if value is None:
        raw = b""
    elif isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8", "surrogatepass")
    else:
        raise ProofV8Error("an actual failed producer returned a non-byte stream")
    preview = raw[:MAX_CHILD_OUTPUT_BYTES]
    return {
        "observed_bytes": len(raw),
        "observed_sha256": hashlib.sha256(raw).hexdigest(),
        "observed_stream_complete": complete,
        "preview_bytes": len(preview),
        "preview_base64": base64.b64encode(preview).decode("ascii"),
        "preview_complete": len(preview) == len(raw),
    }


def preserve_original_producer_failure(
    name: str, state: Mapping[str, Any], *, qualified: bool, deep: bool,
    reason: str, returncode: int | None, stdout: bytes | str | None,
    stderr: bytes | str | None, timed_out: bool,
    owner_before: Mapping[str, Any],
    completed_original: tuple[bytes, bool | None] | None = None,
    integrity_error: BaseException | None = None,
) -> None:
    family = checked_family(name)
    require(reason in {"crash-without-complete-archive", "timeout",
                       "stdout-limit-exceeded", "stderr-limit-exceeded",
                       "post-original-integrity-failure"},
            "an original frozen producer failure changed its exact real cause")
    require(isinstance(owner_before, Mapping)
            and owner_before.get("status") == "PASS"
            and owner_before.get("standard_pickle_failure_count") == 0,
            "an original frozen producer started without a genuinely passing owner")
    target = producer_failure_target(name, qualified, deep=deep)
    parent = ROOT / "candidates" / ("audits" if deep else "evidence")
    fresh_target(target, parent, target.name)
    invalidated_path: str | None = None
    invalidated_sha256: str | None = None
    invalidated_status: str | None = None
    if completed_original is not None:
        require(reason == "post-original-integrity-failure",
                "a crashed producer cannot invent completed original observations")
        original_raw, original_passed = completed_original
        invalidated_path, invalidated_sha256, invalidated_status = (
            retain_invalidated_original(
                name, qualified=qualified, deep=deep,
                raw=original_raw, passed=original_passed,
            )
        )
    document = {
        "schema": SCHEMA + "-original-producer-failure",
        "status": "FAIL", "result": "FAIL",
        "mode": ("qualified-deep" if deep
                 else "qualified-edge" if qualified else "edge-diagnostic"),
        "candidate_family": family["contract_name"],
        "candidate_module": family["module"],
        "actual_failure_reason": reason,
        "refresh_protocol_path": PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": REFRESH_PROTOCOL_SHA256,
        "actual_child_exit_code": returncode,
        "actual_child_signal":
            -returncode if isinstance(returncode, int) and returncode < 0 else None,
        "timed_out": timed_out,
        "timeout_seconds": 1800 if timed_out else None,
        "actual_integrity_error_type":
            type(integrity_error).__name__ if integrity_error is not None else None,
        "actual_integrity_error_message":
            str(integrity_error) if integrity_error is not None else None,
        "stdout": observed_stream(stdout, complete=not timed_out),
        "stderr": observed_stream(stderr, complete=not timed_out),
        "native_owner_before": dict(owner_before),
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "all_family_audited_provenance": audited_graph_provenance(state),
        "historical_current_build_edge_failures": state["historical_failures"],
        "complete_original_observation_archive": completed_original is not None,
        "original_correctness_observations":
            "INVALIDATED" if completed_original is not None else "NOT COMPLETED",
        "invalidated_complete_original_evidence_path": invalidated_path,
        "invalidated_complete_original_evidence_sha256": invalidated_sha256,
        "invalidated_complete_original_actual_status": invalidated_status,
        "production_observations_invented": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    payload = canonical_json(document)
    require(len(payload) <= MAX_FILE_BYTES,
            "the bounded genuine producer crash exceeded its archive size")
    raw = gzip.compress(payload, compresslevel=9, mtime=0)
    checked, preserved = decode_archive(raw, "complete actual producer-crash evidence")
    require(checked == document and preserved == payload,
            "the deterministic genuine crash archive changed its actual streams")
    digest = exclusive_publish(target, raw, deep=deep)
    raise ProofV8Failure(
        "the unchanged frozen producer did not finish its complete observations",
        {
            "status": "FAIL",
            "candidate_family": family["contract_name"],
            "candidate_module": family["module"],
            "actual_failure_reason": reason,
            "actual_child_exit_code": returncode,
            "actual_child_signal": document["actual_child_signal"],
            "timed_out": timed_out,
            "failure_evidence_path": target.relative_to(ROOT).as_posix(),
            "failure_evidence_sha256": digest,
            "stdout_observed_bytes": document["stdout"]["observed_bytes"],
            "stdout_observed_sha256": document["stdout"]["observed_sha256"],
            "stderr_observed_bytes": document["stderr"]["observed_bytes"],
            "stderr_observed_sha256": document["stderr"]["observed_sha256"],
            "complete_original_observation_archive":
                completed_original is not None,
            "invalidated_complete_original_evidence_path": invalidated_path,
            "invalidated_complete_original_evidence_sha256": invalidated_sha256,
            "invalidated_complete_original_actual_status": invalidated_status,
            "production_observations_invented": False,
            "passing_evidence_published": False,
            "failure_evidence_exclusively_preserved": True,
            "campaign_qualified": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        },
    )


def bounded_child(
    command: list[str], name: str, state: Mapping[str, Any],
    *, qualified: bool, deep: bool, owner_before: Mapping[str, Any],
) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            command, cwd=str(ROOT), env=child_environment(),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False, timeout=1800,
        )
    except subprocess.TimeoutExpired as error:
        preserve_original_producer_failure(
            name, state, qualified=qualified, deep=deep,
            reason="timeout", returncode=None,
            stdout=error.stdout, stderr=error.stderr, timed_out=True,
            owner_before=owner_before,
        )
        raise AssertionError("an exclusively preserved producer timeout returned")
    if len(result.stdout) > MAX_CHILD_OUTPUT_BYTES:
        preserve_original_producer_failure(
            name, state, qualified=qualified, deep=deep,
            reason="stdout-limit-exceeded", returncode=result.returncode,
            stdout=result.stdout, stderr=result.stderr, timed_out=False,
            owner_before=owner_before,
        )
        raise AssertionError("an exclusively preserved oversized stdout returned")
    if len(result.stderr) > MAX_CHILD_OUTPUT_BYTES:
        preserve_original_producer_failure(
            name, state, qualified=qualified, deep=deep,
            reason="stderr-limit-exceeded", returncode=result.returncode,
            stdout=result.stdout, stderr=result.stderr, timed_out=False,
            owner_before=owner_before,
        )
        raise AssertionError("an exclusively preserved oversized stderr returned")
    return result


def original_edge_command(name: str, output: Path) -> list[str]:
    family = checked_family(name)
    return [
        str(PINNED_EXECUTABLE), "-I", "-B",
        str(ROOT / "tools/rust_v7_edge_oracle.py"),
        "--module", family["module"],
        "--seed", str(EDGE_SEED),
        "--seeded-cases", str(EDGE_SEEDED_CASES),
        "--unicode-stride", str(EDGE_UNICODE_STRIDE),
        "--output", str(output),
    ]


def refresh_edge(name: str, *, qualified: bool) -> dict[str, Any]:
    state = preflight(name, qualified=qualified)
    family = checked_family(name)
    pass_path = edge_target(name, qualified, True)
    fail_path = edge_target(name, qualified, False)
    owner_fail_path = native_owner_failure_target(name, qualified)
    producer_fail_path = producer_failure_target(name, qualified, deep=False)
    invalidated_path = invalidated_original_target(name, qualified, deep=False)
    for path in (pass_path, fail_path, owner_fail_path,
                 producer_fail_path, invalidated_path):
        fresh_target(path, ROOT / "candidates/evidence", path.name)
    contract = load_contract()
    before_owner = native_owner_observation(
        name, state, qualified=qualified, stage="before-original-edge",
    )
    require(snapshot_family(name) == state["snapshot"],
            "the individually rebuilt native owner changed before the frozen edge")
    with tempfile.TemporaryDirectory(
        prefix="rebar-v8-frozen-edge-" + name + "-", dir="/tmp"
    ) as temporary:
        private = Path(temporary).resolve()
        require(private.parent == Path("/tmp").resolve(),
                "the unchanged original edge escaped its private direct /tmp root")
        temporary_path = private / "original-full-edge.json.gz"
        result = bounded_child(
            original_edge_command(name, temporary_path), name, state,
            qualified=qualified, deep=False, owner_before=before_owner,
        )
        if not temporary_path.exists() or temporary_path.is_symlink():
            preserve_original_producer_failure(
                name, state, qualified=qualified, deep=False,
                reason="crash-without-complete-archive",
                returncode=result.returncode,
                stdout=result.stdout, stderr=result.stderr, timed_out=False,
                owner_before=before_owner,
            )
            raise AssertionError("an exclusively preserved original edge crash returned")
        raw = read_regular(temporary_path, "private unchanged complete V8 edge result")
        passed: bool | None = None
        try:
            document, _, passed = validate_original_edge(
                raw, temporary_path, name, state["snapshot"], contract,
            )
            require(result.returncode == int(not passed),
                    "the frozen edge process exit disagrees with its real failures")
            after_owner = native_owner_observation(
                name, state, qualified=qualified, stage="after-original-edge",
                completed_original=(raw, passed),
            )
            after = preflight(name, qualified=qualified)
            require(after["snapshot"] == state["snapshot"]
                    and after["owner_source_sha256"] == state["owner_source_sha256"]
                    and after["protocol_sha256"] == state["protocol_sha256"]
                    and after["ownership_protocol_sha256"]
                    == state["ownership_protocol_sha256"]
                    and after["historical_failures"] == state["historical_failures"],
                    "the actual individual owner, protocol, or history changed mid-proof")
            if qualified:
                require(after["audit"]["pins"] == state["audit"]["pins"]
                        and after["audit"]["graph"] == state["audit"]["graph"],
                        "an actual all-family campaign audit changed mid-proof")
            target = pass_path if passed else fail_path
            for path in (pass_path, fail_path):
                fresh_target(path, ROOT / "candidates/evidence", path.name)
            archive_sha256 = exclusive_publish(target, raw, deep=False)
        except ProofV8Failure:
            raise
        except (AssertionError, OSError, ValueError, TypeError,
                KeyError, UnicodeError, zlib.error) as error:
            preserve_original_producer_failure(
                name, state, qualified=qualified, deep=False,
                reason="post-original-integrity-failure",
                returncode=result.returncode, stdout=result.stdout,
                stderr=result.stderr, timed_out=False,
                owner_before=before_owner,
                completed_original=(raw, passed),
                integrity_error=error,
            )
            raise AssertionError("an exclusively invalidated edge unexpectedly returned")
    published = read_regular(target, "exclusively preserved V8 frozen edge result")
    final, proof, published_pass = validate_original_edge(
        published, target, name, state["snapshot"], contract,
    )
    require(final == document and published == raw and published_pass == passed
            and proof["archive_sha256"] == archive_sha256,
            "exclusive publication changed the actual complete original edge")
    native_passed = (
        before_owner.get("status") == "PASS"
        and before_owner.get("passed") is True
        and before_owner.get("standard_pickle_failure_count") == 0
        and after_owner.get("status") == "PASS"
        and after_owner.get("passed") is True
        and after_owner.get("standard_pickle_failure_count") == 0
    )
    result = {
        "schema": SCHEMA + ("-qualified-edge" if qualified else "-edge-diagnostic"),
        "status": "PASS" if passed and native_passed else "FAIL",
        "complete_original_edge_status": "PASS" if passed else "FAIL",
        "genuine_native_owner_status": "PASS" if native_passed else "FAIL",
        "mode": "qualified-edge" if qualified else "edge-diagnostic",
        "refresh_protocol_path": PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": REFRESH_PROTOCOL_SHA256,
        "candidate_family": family["contract_name"],
        "candidate_module": family["module"],
        "campaign_qualified": bool(qualified and passed and native_passed),
        "scope": (
            "all-three-family-source-and-no-delegation-audit-qualified"
            if qualified else "one-current-native-family-diagnostic-only"
        ),
        "seed": EDGE_SEED, "checks": EDGE_CHECKS,
        "category_count": EDGE_CATEGORIES,
        "failure_count": final["failed"],
        "complete_failure_row_count": len(final["failures"]),
        "reference_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": final["actual_sha256"],
        "frozen_original_producer_sha256": FROZEN_INPUTS[
            "tools/rust_v7_edge_oracle.py"
        ],
        "evidence_path": target.relative_to(ROOT).as_posix(),
        "evidence_sha256": archive_sha256,
        "complete_original_producer_bytes_preserved": True,
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "native_owner_before": before_owner,
        "native_owner_after": after_owner,
        "historical_current_build_edge_failures": state["historical_failures"],
        "actual_v8_source_audit_report_sha256":
            state["audit"]["pins"]["source_report"] if qualified else None,
        "actual_v8_no_delegation_report_sha256":
            state["audit"]["pins"]["strict_report"] if qualified else None,
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    if not passed:
        result["first_failures"] = final["failures"][:5]
    return result


def expected_cross_guards(name: str, contract: Any) -> list[dict[str, str]]:
    family = checked_family(name)
    names = {module for module in contract.SPECS if module != family["module"]}
    names.update(
        spec.native_module for spec in contract.SPECS.values()
        if spec.native_module is not None and spec.module != family["module"]
    )
    names.update({"regex", "_regex", "pcre2", "re2", "hyperscan"})
    return [
        {"module": module, "type": "GuardSignal",
         "message":
             "production reached a forbidden independent or external engine: "
             + module}
        for module in sorted(names)
    ]


def validate_deep(
    raw: bytes, name: str, edge: dict[str, Any],
    snapshot: Mapping[str, Any], contract: Any,
) -> tuple[dict[str, Any], bool]:
    family = checked_family(name)
    report, payload = decode_archive(
        raw, "complete unchanged V8 deep proof", compact=True,
    )
    suite = contract.load_frozen_suite()
    contract.original_failure(suite)
    require(suite.canonical(report) == payload,
            "the 393-case proof is not the unchanged original canonical report")
    for key, value in {
        "schema": DEEP_SCHEMA,
        "python": "3.14.6", "seed": DEEP_SEED,
        "seeded_case_count": DEEP_SEEDED_CASES,
        "checks": DEEP_CHECKS,
        "fixture_sha256": contract.FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": FROZEN_INPUTS[
            "tools/rust_v8_deep_contract_oracle.py"
        ],
        "reference_a_sha256": DEEP_REFERENCE_SHA256,
        "reference_b_sha256": DEEP_REFERENCE_SHA256,
        "candidate_module": family["module"],
        "candidate_family": family["contract_name"],
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }.items():
        require(report.get(key) == value,
                "the unchanged complete 393-case contract changed: " + key)
    require(report.get("edge_oracle") == edge,
            "the 393-case proof is not bound to its fresh qualified edge archive")
    require(report.get("stdlib_vs_stdlib_mismatches") == [],
            "the independently isolated CPython references disagree")
    guards = report.get("guard_observations")
    require(isinstance(guards, list) and len(guards) == len(REGEX_GUARDS)
            and {(row.get("module"), row.get("name"))
                 for row in guards if isinstance(row, dict)
                 and row.get("type") == "GuardSignal"} == set(REGEX_GUARDS)
            and report.get("forbidden_regex_guards") == len(REGEX_GUARDS),
            "the real deep candidate lost an active frozen Python regex guard")
    cross = expected_cross_guards(name, contract)
    require(report.get("cross_engine_guard_observations") == cross
            and report.get("cross_engine_guard_count") == len(cross),
            "the real deep candidate lost a cross-family or external engine guard")
    for field, role in (
        ("reference", "stdlib-a"),
        ("reference_independent_repeat", "stdlib-b"),
        ("candidate", "candidate"),
    ):
        worker = report.get(field)
        require(isinstance(worker, dict), "a genuine isolated deep worker is missing")
        contract.verify_worker_report(
            suite, worker, role, edge if role == "candidate" else None,
        )
        diagnostics = worker.get("implementation_private_gc_diagnostics")
        require(isinstance(diagnostics, list) and len(diagnostics) == DEEP_SEEDED_CASES,
                "a genuine deep worker changed its full seeded-case denominator")
    require(report["candidate"].get("cross_engine_guards") == cross
            and report.get("candidate_sha256")
            == report["candidate"].get("observation_sha256"),
            "the deep native guard or actual candidate observations were substituted")
    references = report["reference"]["observations"]
    repeat = report["reference_independent_repeat"]["observations"]
    observations = report["candidate"]["observations"]
    require(suite.mismatches(references, repeat) == [],
            "the two independently isolated original references disagree")
    mismatches = suite.mismatches(references, observations)
    require(report.get("public_mismatches") == mismatches
            and report.get("public_mismatch_count") == len(mismatches),
            "the complete genuine deep contract concealed a public mismatch")
    expected_counts = dict(sorted(collections.Counter(
        row.get("family", "missing") for row in mismatches
    ).items()))
    require(report.get("public_mismatch_family_counts") == expected_counts,
            "the genuine deep contract concealed an actual failure category")
    passed = not mismatches
    require(report.get("status") == ("PASS" if passed else "FAIL"),
            "the unchanged deep producer relabeled its real 393 observations")
    if passed:
        require(report.get("candidate_sha256") == DEEP_REFERENCE_SHA256,
                "a passing deep label does not match the frozen public reference")
    expected = dict(snapshot["source_sha256_by_path"])
    expected.update(snapshot["native_sha256_by_path"])
    artifacts = report.get("native_artifacts")
    require(isinstance(artifacts, list) and all(
        isinstance(row, dict) and expected.get(row.get("path")) == row.get("sha256")
        for row in artifacts
    ) and artifacts == edge["production_artifacts"],
            "the deep producer loaded an unproven, stale, or foreign native role")
    require(report.get("differential_poison_self_tests") == {
        "changed_observation_poison": "PASS",
        "identical_reference": "PASS",
        "missing_observation_poison": "PASS",
    }, "the unchanged deep contract lost a genuine differential poison control")
    require(report.get("frozen_failure_evidence") == {
        "path": "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz",
        "archive_sha256": FROZEN_INPUTS[
            "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
        ],
        "status": "FAIL", "public_mismatch_count": 104,
    }, "the unchanged deep contract concealed its original 104 genuine failures")
    require(report.get("multifamily_runner") == {
        "path": "tools/rust_v8_multi_candidate_contract.py",
        "sha256": FROZEN_INPUTS["tools/rust_v8_multi_candidate_contract.py"],
    }, "the unchanged deep producer's frozen source was substituted")
    return report, passed


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


def refresh_deep(name: str) -> dict[str, Any]:
    state = preflight(name, qualified=True)
    family = checked_family(name)
    contract = load_contract()
    edge_path = edge_target(name, True, True)
    raw_edge = read_regular(edge_path, "required audit-qualified passing V8 edge")
    _, edge, edge_passed = validate_original_edge(
        raw_edge, edge_path, name, state["snapshot"], contract,
    )
    require(edge_passed and edge_path == edge_target(name, True, True),
            "a diagnostic or failed edge cannot qualify a genuine deep campaign")
    pass_path = deep_target(name, True)
    fail_path = deep_target(name, False)
    for path in (pass_path, fail_path):
        fresh_target(path, ROOT / "candidates/audits", path.name)
    owner_fail_path = native_owner_failure_target(name, True)
    fresh_target(owner_fail_path, ROOT / "candidates/evidence", owner_fail_path.name)
    for path in (producer_failure_target(name, True, deep=True),
                 invalidated_original_target(name, True, deep=True)):
        fresh_target(path, ROOT / "candidates/audits", path.name)
    before_owner = native_owner_observation(
        name, state, qualified=True, stage="before-original-deep",
    )
    with tempfile.TemporaryDirectory(
        prefix="rebar-v8-frozen-deep-" + name + "-", dir="/tmp"
    ) as temporary:
        private = Path(temporary).resolve()
        require(private.parent == Path("/tmp").resolve(),
                "the unchanged deep producer escaped its private direct /tmp root")
        temporary_path = private / (
            "RUST-V8-DEEP-CONTRACT-" + family["contract_name"]
            + "-POSTFINAL-CURRENT-BUILD-V8-PRIVATE.json.gz"
        )
        command = [
            str(PINNED_EXECUTABLE), "-I", "-B", "-c", DEEP_LAUNCHER,
            str(ROOT), family["module"], str(edge_path),
            str(temporary_path), str(private),
        ]
        result = bounded_child(
            command, name, state, qualified=True, deep=True,
            owner_before=before_owner,
        )
        if not temporary_path.exists() or temporary_path.is_symlink():
            preserve_original_producer_failure(
                name, state, qualified=True, deep=True,
                reason="crash-without-complete-archive",
                returncode=result.returncode,
                stdout=result.stdout, stderr=result.stderr, timed_out=False,
                owner_before=before_owner,
            )
            raise AssertionError("an exclusively preserved original deep crash returned")
        raw = read_regular(temporary_path, "private unchanged complete V8 deep proof")
        passed: bool | None = None
        try:
            report, passed = validate_deep(
                raw, name, edge, state["snapshot"], contract,
            )
            require(result.returncode == int(not passed),
                    "the unchanged deep exit disagrees with genuine mismatches")
            after_owner = native_owner_observation(
                name, state, qualified=True, stage="after-original-deep",
                completed_original=(raw, passed),
            )
            after = preflight(name, qualified=True)
            require(after["snapshot"] == state["snapshot"]
                    and after["audit"]["pins"] == state["audit"]["pins"]
                    and after["audit"]["graph"] == state["audit"]["graph"]
                    and after["historical_failures"] == state["historical_failures"]
                    and read_regular(edge_path, "rechecked qualifying V8 edge")
                    == raw_edge,
                    "the all-family audits, native build, or qualified edge changed")
            target = pass_path if passed else fail_path
            for path in (pass_path, fail_path):
                fresh_target(path, ROOT / "candidates/audits", path.name)
            archive_sha256 = exclusive_publish(target, raw, deep=True)
        except ProofV8Failure:
            raise
        except (AssertionError, OSError, ValueError, TypeError,
                KeyError, UnicodeError, zlib.error) as error:
            preserve_original_producer_failure(
                name, state, qualified=True, deep=True,
                reason="post-original-integrity-failure",
                returncode=result.returncode, stdout=result.stdout,
                stderr=result.stderr, timed_out=False,
                owner_before=before_owner,
                completed_original=(raw, passed),
                integrity_error=error,
            )
            raise AssertionError("an exclusively invalidated deep proof returned")
    preserved = read_regular(target, "exclusively preserved genuine V8 deep proof")
    final, final_passed = validate_deep(
        preserved, name, edge, state["snapshot"], contract,
    )
    require(preserved == raw and final == report and final_passed == passed,
            "exclusive publication changed the actual complete deep observations")
    result = {
        "schema": SCHEMA + "-qualified-deep",
        "status": "PASS" if passed else "FAIL",
        "mode": "qualified-deep",
        "refresh_protocol_path": PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": REFRESH_PROTOCOL_SHA256,
        "candidate_family": family["contract_name"],
        "candidate_module": family["module"],
        "campaign_qualified": passed,
        "seed": DEEP_SEED, "checks": DEEP_CHECKS,
        "seeded_case_count": DEEP_SEEDED_CASES,
        "public_mismatch_count": final["public_mismatch_count"],
        "public_mismatch_family_counts": final["public_mismatch_family_counts"],
        "reference_sha256": DEEP_REFERENCE_SHA256,
        "actual_sha256": final["candidate_sha256"],
        "evidence_path": target.relative_to(ROOT).as_posix(),
        "evidence_sha256": archive_sha256,
        "qualified_edge_path": edge_path.relative_to(ROOT).as_posix(),
        "qualified_edge_sha256": edge["archive_sha256"],
        "complete_original_producer_bytes_preserved": True,
        "full_current_family_source_sha256":
            state["snapshot"]["source_sha256_by_path"],
        "full_current_family_native_elf_sha256":
            state["snapshot"]["native_sha256_by_path"],
        "native_owner_before": before_owner,
        "native_owner_after": after_owner,
        "historical_current_build_edge_failures": state["historical_failures"],
        "actual_v8_source_audit_report_sha256":
            state["audit"]["pins"]["source_report"],
        "actual_v8_no_delegation_report_sha256":
            state["audit"]["pins"]["strict_report"],
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    if not passed:
        result["first_failures"] = final["public_mismatches"][:5]
    return result


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    """Permit only frozen source reads; make every production effect impossible."""
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
    }
    allowed.update({(ROOT / SOURCE_RELATIVE).resolve(),
                    (ROOT / PROTOCOL_RELATIVE).resolve()})

    def replace(target: Any, name: str, value: Any) -> None:
        if hasattr(target, name):
            originals.append((target, name, getattr(target, name)))
            setattr(target, name, value)

    def blocked(kind: str, label: str) -> Callable[..., Any]:
        def reject(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            counts[kind] += 1
            raise ProofV8Error("the candidate-free V8 source self-test forbids " + label)

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
                    and any(part in {"candidates", "performance", "holdout"}
                            for part in Path(os.fsdecode(path)).parts)
                    else "unauthorized_read_attempts_blocked")
            return blocked(kind, "evidence, candidate, or unapproved file reads")()
        return original_os_open(path, flags, *args, **kwargs)

    original_builtin_open = builtins.open

    def guarded_open(file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if any(character in mode for character in "wax+"):
            return blocked("write_attempts_blocked", "filesystem writes")()
        if isinstance(file, int):
            return original_builtin_open(file, mode, *args, **kwargs)
        if not authorized(file):
            kind = ("evidence_read_attempts_blocked"
                    if isinstance(file, (str, bytes, os.PathLike))
                    and any(part in {"candidates", "performance", "holdout"}
                            for part in Path(os.fsdecode(file)).parts)
                    else "unauthorized_read_attempts_blocked")
            return blocked(kind, "evidence, candidate, or unapproved file reads")()
        return original_builtin_open(file, mode, *args, **kwargs)

    original_import = builtins.__import__
    original_import_module = importlib.import_module
    forbidden_roots = {
        "candidates", "regex", "_regex", "re2", "pcre", "pcre2",
        "rure", "hyperscan", "onig", "oniguruma",
    }

    def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
        root = name.partition(".")[0]
        if root in forbidden_roots:
            return blocked("candidate_import_attempts_blocked",
                           "candidate or external-engine imports")()
        return original_import(name, *args, **kwargs)

    def guarded_import_module(name: str, package: str | None = None) -> Any:
        if isinstance(name, str) and name.partition(".")[0] in forbidden_roots:
            return blocked("candidate_import_attempts_blocked",
                           "importlib candidate or external-engine imports")()
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
    for target, name in ((subprocess, "run"), (subprocess, "Popen"),
                         (threading.Thread, "start"),
                         (multiprocessing.Process, "start"),
                         (tempfile, "mkdtemp"),
                         (tempfile, "TemporaryDirectory")):
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
    except (ProofV8Error, AssertionError, OSError, ValueError, TypeError,
            KeyError, json.JSONDecodeError, zlib.error):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def synthetic_snapshot(name: str) -> dict[str, Any]:
    family = checked_family(name)
    def digest(relative: str) -> str:
        return hashlib.sha256(("v8-source-only:" + relative).encode("ascii")).hexdigest()

    return {
        "family": name, "module": family["module"],
        "source_sha256_by_path": {
            relative: digest(relative) for relative in family["sources"]
        },
        "native_sha256_by_path": {
            relative: digest(relative) for relative in family["native"].values()
        },
    }


def synthetic_edge(name: str, *, failed: bool = False) -> dict[str, Any]:
    family = checked_family(name)
    snapshot = synthetic_snapshot(name)
    categories = {"source-only-category-" + str(index): 1
                  for index in range(EDGE_CATEGORIES)}
    categories["source-only-category-0"] = EDGE_CHECKS - EDGE_CATEGORIES + 1
    artifacts = [{
        "role": "public-python", "path": family["sources"][0],
        "sha256": snapshot["source_sha256_by_path"][family["sources"][0]],
    }]
    for role, relative in family["native"].items():
        artifacts.append({
            "role": "native-bridge" if role in {"bridge", "native"}
                    else "native-engine",
            "path": relative,
            "sha256": snapshot["native_sha256_by_path"][relative],
        })
    if name == "rust":
        for role, relative in (
            ("native-source", "candidates/rust/src/lib.rs"),
            ("bridge-source", "candidates/rust/py_bridge.c"),
        ):
            artifacts.append({
                "role": role, "path": relative,
                "sha256": snapshot["source_sha256_by_path"][relative],
            })
    return {
        "schema": EDGE_SCHEMA,
        "script_sha256": FROZEN_INPUTS["tools/rust_v7_edge_oracle.py"],
        "oracle": "CPython standard-library re",
        "python": "3.14.6", "unicode": "16.0.0", "locale": "C",
        "module": family["module"],
        "seed": EDGE_SEED, "seeded_cases": EDGE_SEEDED_CASES,
        "unicode_stride": EDGE_UNICODE_STRIDE,
        "independent_source_seeds": copy.deepcopy(EDGE_INDEPENDENT_SEEDS),
        "json_normalization": {"lone_surrogates": "surrogatepass_utf8_hex"},
        "correctness_checks": EDGE_CHECKS,
        "categories": categories,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": "0" * 64 if failed else EDGE_REFERENCE_SHA256,
        "failed": int(failed),
        "failures": ([{"category": "source-only-control",
                        "label": "synthetic-control-never-production"}]
                     if failed else []),
        "candidate_artifacts": artifacts,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime()
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    with source_only_boundary() as effects:
        for relative, expected in FROZEN_INPUTS.items():
            if relative.startswith("candidates/"):
                accept("preserve-evidence-fingerprint-without-reading:" + relative,
                       valid_sha256(expected))
                continue
            raw = checked_frozen(relative, expected)
            accept("authenticate-unchanged-frozen-source:" + relative,
                   hashlib.sha256(raw).hexdigest() == expected)
            if relative.endswith(".py"):
                tree = ast.parse(raw.decode("utf-8"), filename=relative)
                accept("parse-frozen-source-without-executing:" + relative,
                       isinstance(tree, ast.Module))
        own_source = read_regular(ROOT / SOURCE_RELATIVE,
                                  "candidate-free V8 correctness controller")
        own_tree = ast.parse(own_source.decode("utf-8"), filename=SOURCE_RELATIVE)
        accept("parse-current-controller-without-executing-a-candidate",
               isinstance(own_tree, ast.Module))
        import_nodes = (node for node in ast.walk(own_tree)
                        if isinstance(node, (ast.Import, ast.ImportFrom)))
        accept("reject-top-level-production-and-external-engine-imports", all(
            not ((node.module or "").startswith("candidates")
                 if isinstance(node, ast.ImportFrom)
                 else any(alias.name.split(".", 1)[0] in {
                     "candidates", "regex", "_regex", "pcre2", "re2",
                     "hyperscan", "rure", "onig", "oniguruma",
                 } for alias in node.names))
            for node in import_nodes
        ))
        real_edge_function = next(
            (node for node in own_tree.body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
             and node.name == "validate_original_edge"),
            None,
        )
        require(isinstance(real_edge_function, ast.FunctionDef),
                "the unchanged original-edge validator was omitted")
        protected = {"failed", "failures", "actual_sha256"}
        protected_writes = [
            target
            for node in ast.walk(real_edge_function)
            for target in (
                list(node.targets) if isinstance(node, ast.Assign)
                else [node.target] if isinstance(node, (ast.AnnAssign, ast.AugAssign))
                else []
            )
            if isinstance(target, ast.Subscript)
            and isinstance(target.slice, ast.Constant)
            and target.slice.value in protected
        ]
        accept("never-rewrite-real-original-failed-observations-to-a-pass",
               not protected_writes)
        pass_validator_calls = [
            node for node in ast.walk(real_edge_function)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "validate_edge_document"
        ]
        accept("pass-only-original-validator-receives-only-real-archive-document",
               len(pass_validator_calls) == 1
               and bool(pass_validator_calls[0].args)
               and isinstance(pass_validator_calls[0].args[0], ast.Name)
               and pass_validator_calls[0].args[0].id == "document")
        protocol = read_regular(ROOT / PROTOCOL_RELATIVE,
                                "candidate-free V8 correctness protocol")
        accept("authenticate-independently-frozen-v8-proof-protocol",
               hashlib.sha256(protocol).hexdigest() == REFRESH_PROTOCOL_SHA256)
        for token in (
            b"223,198", b"49", b"393", b"64", b"diagnostic",
            b"campaign_qualified", b"native-owner-failure",
            b"V5", b"NOT MEASURED", b"NOT ACCESSED",
        ):
            accept("protocol-preserves:" + token.decode("ascii"), token in protocol)
        accept("preserve-exact-three-independent-native-families",
               tuple(FAMILIES) == ("rust", "vm", "zig"))
        accept("preserve-all-twelve-independently-owned-source-files",
               sum(len(row["sources"]) for row in FAMILIES.values()) == 12)
        accept("preserve-all-five-independently-owned-real-native-roles",
               sum(len(row["native"]) for row in FAMILIES.values()) == 5)
        accept("preserve-all-thirteen-no-delegation-poison-guards",
               len(REGEX_GUARDS) == 13)
        accept("preserve-exact-original-223198-observation-edge-denominator",
               EDGE_CHECKS == 223198 and EDGE_CATEGORIES == 49)
        accept("preserve-exact-original-393-observation-deep-denominator",
               DEEP_CHECKS == 393 and DEEP_SEEDED_CASES == 64)
        accept("preserve-all-real-original-family-failures-without-evidence-access",
               set(HISTORICAL_EDGE_FAILURES) == set(FAMILIES)
               and {
                   name: (values[1], values[2])
                   for name, values in HISTORICAL_EDGE_FAILURES.items()
               } == {
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
        accept("preserve-exact-six-independent-original-edge-seeds",
               len(EDGE_INDEPENDENT_SEEDS) == 6
               and EDGE_INDEPENDENT_SEEDS["edge_generation"] == EDGE_SEED)
        accept("refuse-unpublished-all-family-campaign-pins",
               rejected("missing-actual-campaign-pins",
                        required_campaign_pins)["passed"])
        complete_pins = {
            name: hashlib.sha256(("source-only:" + name).encode("ascii")).hexdigest()
            for name in ("source_audit", "source_report",
                         "strict_audit", "strict_report")
        }
        accept("accept-four-distinct-synthetic-pin-controls-only-in-memory",
               required_campaign_pins(complete_pins) == complete_pins)
        for key in complete_pins:
            missing = dict(complete_pins)
            missing[key] = None
            checks.append(rejected("reject-unpublished-campaign-pin:" + key,
                                   lambda value=missing: required_campaign_pins(value)))
        repeated = dict(complete_pins)
        repeated["strict_report"] = repeated["source_report"]
        checks.append(rejected("reject-reused-source-or-report-campaign-digest",
                               lambda: required_campaign_pins(repeated)))
        for name in FAMILIES:
            snapshot = synthetic_snapshot(name)
            passing = synthetic_edge(name)
            failing = synthetic_edge(name, failed=True)
            accept("accept-complete-synthetic-edge-denominator:" + name,
                   validate_edge_shape(passing, name, snapshot) == (True, 0))
            accept("retain-complete-synthetic-failure-without-qualification:" + name,
                   validate_edge_shape(failing, name, snapshot) == (False, 1))
            checks.append(rejected(
                "reject-complete-edge-with-zero-native-provenance:" + name,
                lambda role=name, snap=snapshot: validate_edge_shape(
                    {**synthetic_edge(role), "candidate_artifacts": []}, role, snap,
                ),
            ))
            for omitted in range(len(passing["candidate_artifacts"])):
                incomplete = copy.deepcopy(passing)
                removed = incomplete["candidate_artifacts"].pop(omitted)
                checks.append(rejected(
                    "reject-missing-original-native-owner-role:"
                    + name + ":" + removed["role"],
                    lambda doc=incomplete, role=name, snap=snapshot:
                        validate_edge_shape(doc, role, snap),
                ))
            duplicated = copy.deepcopy(passing)
            duplicated["candidate_artifacts"][-1] = copy.deepcopy(
                duplicated["candidate_artifacts"][0]
            )
            checks.append(rejected(
                "reject-duplicate-original-native-owner-role:" + name,
                lambda doc=duplicated, role=name, snap=snapshot:
                    validate_edge_shape(doc, role, snap),
            ))
            for key, replacement in (
                ("schema", "substituted-schema"),
                ("module", "candidates.foreign_candidate"),
                ("seed", EDGE_SEED + 1),
                ("correctness_checks", EDGE_CHECKS - 1),
                ("expected_sha256", "0" * 64),
                ("independent_source_seeds", {}),
                ("performance", "secretly measured"),
                ("holdout", "secretly accessed"),
            ):
                poisoned = copy.deepcopy(passing)
                poisoned[key] = replacement
                checks.append(rejected(
                    "reject-original-edge-poison:" + name + ":" + key,
                    lambda doc=poisoned, role=name, snap=snapshot:
                        validate_edge_shape(doc, role, snap),
                ))
            for key, replacement in (
                ("categories", {"reduced-suite": EDGE_CHECKS}),
                ("failed", 1),
                ("failures", [{"hidden": True}]),
                ("actual_sha256", "0" * 64),
                ("candidate_artifacts", [{"role": "foreign", "path":
                                          "candidates/foreign.so", "sha256":
                                          "0" * 64}]),
            ):
                poisoned = copy.deepcopy(passing)
                poisoned[key] = replacement
                checks.append(rejected(
                    "reject-complete-edge-denominator-or-owner-poison:"
                    + name + ":" + key,
                    lambda doc=poisoned, role=name, snap=snapshot:
                        validate_edge_shape(doc, role, snap),
                ))
            encoded = canonical_json(passing)
            archive = gzip.compress(encoded, compresslevel=9, mtime=0)
            decoded, preserved = decode_archive(archive, "in-memory source-only edge")
            accept("accept-complete-deterministic-in-memory-gzip:" + name,
                   decoded == passing and preserved == encoded)
            checks.append(rejected(
                "reject-truncated-original-gzip:" + name,
                lambda value=archive[:-4]: decode_archive(value, "truncated control"),
            ))
            checks.append(rejected(
                "reject-appended-original-gzip-member:" + name,
                lambda value=archive + archive: decode_archive(value, "trailing control"),
            ))
            changed_time = bytearray(archive)
            changed_time[4] = 1
            checks.append(rejected(
                "reject-nondeterministic-original-gzip-timestamp:" + name,
                lambda value=bytes(changed_time): decode_archive(
                    value, "nondeterministic control"
                ),
            ))
            deep_control = {
                "schema": DEEP_SCHEMA, "status": "PASS",
                "candidate_module": FAMILIES[name]["module"],
                "seed": DEEP_SEED, "checks": DEEP_CHECKS,
                "seeded_case_count": DEEP_SEEDED_CASES,
                "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            }
            compact = json.dumps(
                deep_control, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("ascii")
            deep_archive = gzip.compress(compact, compresslevel=9, mtime=0)
            deep_document, deep_payload = decode_archive(
                deep_archive, "source-only unchanged deep canonical control",
                compact=True,
            )
            accept("preserve-original-compact-deep-canonical-gzip:" + name,
                   deep_document == deep_control and deep_payload == compact)
            checks.append(rejected(
                "reject-pretty-edge-canonical-as-original-compact-deep:" + name,
                lambda value=archive: decode_archive(
                    value, "source-only compact deep poison", compact=True,
                ),
            ))
            checks.append(rejected(
                "reject-compact-deep-canonical-as-original-pretty-edge:" + name,
                lambda value=deep_archive: decode_archive(
                    value, "source-only pretty edge poison",
                ),
            ))
            for qualified in (False, True):
                for passed in (False, True):
                    path = edge_target(name, qualified, passed)
                    expected_mode = "qualified" if qualified else "diagnostic"
                    expected_result = "pass" if passed else "failures"
                    accept("preserve-exclusive-edge-destination:"
                           + name + ":" + expected_mode + ":" + expected_result,
                           path.parent == ROOT / "candidates/evidence"
                           and expected_mode in path.name
                           and expected_result in path.name)
                failure = native_owner_failure_target(name, qualified)
                expected_mode = "qualified" if qualified else "diagnostic"
                accept("preserve-exclusive-genuine-owner-failure-destination:"
                       + name + ":" + expected_mode,
                       failure.parent == ROOT / "candidates/evidence"
                       and expected_mode in failure.name
                       and failure.name.endswith("-native-owner-failure.json.gz")
                       and failure != edge_target(name, qualified, True)
                       and failure != edge_target(name, qualified, False))
                crash = producer_failure_target(name, qualified, deep=False)
                invalidated = invalidated_original_target(
                    name, qualified, deep=False,
                )
                accept("preserve-exclusive-original-edge-crash-destination:"
                       + name + ":" + expected_mode,
                       crash.parent == ROOT / "candidates/evidence"
                       and expected_mode in crash.name
                       and crash.name.endswith("-producer-crash.json.gz")
                       and crash not in {
                           failure, invalidated,
                           edge_target(name, qualified, True),
                           edge_target(name, qualified, False),
                       })
                accept("retain-full-invalidated-original-edge-after-owner-failure:"
                       + name + ":" + expected_mode,
                       invalidated.parent == ROOT / "candidates/evidence"
                       and expected_mode in invalidated.name
                       and invalidated.name.endswith(
                           "-invalidated-after-owner-failure.json.gz"
                       )
                       and invalidated not in {
                           failure, crash,
                           edge_target(name, qualified, True),
                           edge_target(name, qualified, False),
                       })
            accept("keep-diagnostic-and-campaign-proof-paths-distinct:" + name,
                   edge_target(name, False, True) != edge_target(name, True, True)
                   and edge_target(name, False, False)
                   != edge_target(name, True, False))
            accept("never-share-diagnostic-and-qualified-native-owner-failures:"
                   + name,
                   native_owner_failure_target(name, False)
                   != native_owner_failure_target(name, True))
            accept("keep-deep-pass-and-complete-failure-paths-distinct:" + name,
                   deep_target(name, True) != deep_target(name, False))
            deep_crash = producer_failure_target(name, True, deep=True)
            deep_invalidated = invalidated_original_target(name, True, deep=True)
            accept("preserve-exclusive-complete-original-deep-crash:" + name,
                   deep_crash.parent == ROOT / "candidates/audits"
                   and deep_crash.name.endswith("-PRODUCER-CRASH.json.gz")
                   and deep_crash not in {
                       deep_target(name, True), deep_target(name, False),
                       deep_invalidated,
                   })
            accept("retain-complete-invalidated-original-deep-observations:" + name,
                   deep_invalidated.parent == ROOT / "candidates/audits"
                   and deep_invalidated.name.endswith(
                       "-INVALIDATED-AFTER-OWNER-FAILURE.json.gz"
                   )
                   and deep_invalidated not in {
                       deep_target(name, True), deep_target(name, False),
                       deep_crash,
                   })
        for label, action in (
            ("candidate-import", lambda: builtins.__import__("candidates")),
            ("importlib-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("external-package-import", lambda: builtins.__import__("regex")),
            ("importlib-external-package-import",
             lambda: importlib.import_module("regex")),
            ("candidate-evidence-read",
             lambda: read_regular(ROOT / HISTORICAL_EDGE_FAILURES["rust"][0],
                                  "forbidden evidence")),
            ("performance-or-holdout-read",
             lambda: builtins.open(ROOT / "performance" / "holdout.json", "rb")),
            ("clock", lambda: time.perf_counter()),
            ("worker", lambda: subprocess.run(["forbidden"])),
            ("filesystem-write",
             lambda: builtins.open(ROOT / "forbidden-v8-self-test-write", "wb")),
            ("direct-path-write",
             lambda: (ROOT / "forbidden-v8-path-write").write_bytes(b"blocked")),
            ("direct-file-removal",
             lambda: os.unlink(str(ROOT / "forbidden-v8-removal"))),
            ("direct-file-replacement",
             lambda: os.replace("forbidden-v8-source", "forbidden-v8-target")),
            ("unapproved-source-read",
             lambda: builtins.open(ROOT / "README.md", "rb")),
            ("temporary-worker-root", lambda: tempfile.mkdtemp()),
        ):
            checks.append(rejected("enforce-source-only-effect-boundary:" + label,
                                   action))
        accept("candidate-remains-unimported-after-all-source-controls",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
        accept("block-builtin-and-importlib-candidate-and-external-imports",
               effects["candidate_import_attempts_blocked"] >= 4)
        require(all(item["passed"] for item in checks),
                "an original-source, denominator, qualification, or effect control failed")
        snapshot = dict(effects)
    verify_runtime()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS", "result": "PASS", "passed": True,
        "refresh_protocol_path": PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": REFRESH_PROTOCOL_SHA256,
        "check_count": len(checks),
        "checks": checks,
        "candidate_imports": 0,
        "subprocesses": 0,
        "file_writes": 0,
        "clock_samples": 0,
        "historical_evidence_reads": 0,
        "original_edge_checks": EDGE_CHECKS,
        "original_edge_categories": EDGE_CATEGORIES,
        "original_deep_checks": DEEP_CHECKS,
        "original_deep_seeded_cases": DEEP_SEEDED_CASES,
        "historical_failure_counts": {
            name: values[2] for name, values in HISTORICAL_EDGE_FAILURES.items()
        },
        "campaign_qualification_without_actual_v8_audits": False,
        "blocked_effect_attempts": snapshot,
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
        family["module"] for family in FAMILIES.values()
    ))
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    if options.self_test:
        require(options.module is None,
                "the source-only proof self-test may not select a candidate")
        report = candidate_free_self_test()
    else:
        require(options.module is not None,
                "real correctness proofs require exactly one explicit owned family")
        family = next(name for name, row in FAMILIES.items()
                      if row["module"] == options.module)
        if options.diagnostic_edge:
            report = refresh_edge(family, qualified=False)
        elif options.qualified_edge:
            report = refresh_edge(family, qualified=True)
        else:
            report = refresh_deep(family)
    print(json.dumps(report, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")), flush=True)
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofV8Failure as error:
        print(json.dumps({
            "schema": SCHEMA + "-producer-failure",
            "status": "FAIL", "message": str(error),
            "details": error.details,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")),
            file=sys.stderr, flush=True)
        raise SystemExit(1) from error
