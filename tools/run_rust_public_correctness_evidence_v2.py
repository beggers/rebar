#!/usr/bin/env python3
"""Preserve exactly one complete, frozen Rust public-practice v2 comparison.

The immutable v2 benchmark intentionally writes nothing in correctness-only
mode.  This independently frozen controller captures its *entire* canonical
stdout, including every mismatch on FAIL, and publishes that unchanged stdout
plus an independently durable provenance receipt.  The benchmark exposes full
10,434-case vector digests, not individual passing outcomes; this controller
never invents or claims to retain unavailable passing records.

Only an explicitly root-authorized ``--run`` may inspect candidate/native
owners, create a subprocess, or publish evidence.  Source-only modes install a
physical audit/clock wall and read only six named, owned public source files.
"""

from __future__ import annotations

import argparse
import hashlib
from importlib.machinery import EXTENSION_SUFFIXES
import json
import os
import stat
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/run_rust_public_correctness_evidence_v2.py"
PROTOCOL = "oracle/phase3/RUST-PUBLIC-CORRECTNESS-EVIDENCE-V2.md"
MANIFEST = "oracle/phase3/rust-public-correctness-evidence-v2.json"
BENCHMARK_SOURCE = "tools/rust_public_practice_benchmark_v2.py"
BENCHMARK_PROTOCOL = "oracle/phase3/RUST-PUBLIC-PRACTICE-BENCHMARK-V2.md"
BENCHMARK_MANIFEST = "oracle/phase3/rust-public-practice-benchmark-v2.json"
BENCHMARK_SOURCE_SHA256 = (
    "a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6"
)
BENCHMARK_PROTOCOL_SHA256 = (
    "4040c458119a6d347c1eb876e1120a4400f76b8f16611d21de15371b50508586"
)
BENCHMARK_MANIFEST_SHA256 = (
    "7c4120c549a006cc162abb545032e1808637cf3c088f4a21023d5c99fb351e4a"
)
MATRIX_SHA256 = (
    "0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d"
)
SCHEMA = "rebar-rust-public-correctness-evidence-v2"
BENCHMARK_SCHEMA = "rebar-rust-independent-public-practice-v2"
LABEL = "PUBLIC DEVELOPMENT/PRACTICE ONLY; NOT A SEALED, HIDDEN, OR FINAL HOLDOUT"
PUBLISHED_SEED = 5928217332825411634
CASE_COUNT = 10434
DOMAIN_CASE_COUNT = 5217
DATASET_COUNT = 94
OPERATIONS_PER_DATASET = 111
ADAPTER = "candidates/rust_candidate.py"
NATIVE_ENGINE = "candidates/_rust_engine.so"
APPROVED_DIRECTORIES = (
    "oracle/phase3/evidence",
    "experiments/rust_public_practice_v2",
)
PUBLIC_OWNERS = (SOURCE, PROTOCOL, MANIFEST, BENCHMARK_SOURCE,
                 BENCHMARK_PROTOCOL, BENCHMARK_MANIFEST)
MAX_PUBLIC_BYTES = 4 * 1024 * 1024
MAX_NATIVE_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 256 * 1024 * 1024
MAX_RECEIPT_BYTES = 512 * 1024 * 1024

_SOURCE_WALL_ACTIVE = False
_SOURCE_WALL_INSTALLED = False
_SOURCE_BLOCKED: dict[str, int] = {
    "candidate": 0,
    "process": 0,
    "clock": 0,
    "mutation": 0,
    "archive_holdout_fixture": 0,
    "native": 0,
    "foreign_read": 0,
}
_CLOCK_NAMES = tuple(
    name for name in (
        "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
        "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
        "thread_time_ns", "clock_gettime", "clock_gettime_ns", "sleep",
    ) if hasattr(time, name)
)


class EvidenceError(Exception):
    """A frozen owner, physical source wall, full result, or publication failed."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise EvidenceError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, allow_nan=False, ensure_ascii=True, separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii") + b"\n"


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(letter in "0123456789abcdef" for letter in value)
            and len(set(value)) > 1,
            "an independently pinned lowercase SHA-256 is mandatory: " + label)
    return value


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    actual: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in actual,
                "a duplicate JSON object key concealed public correctness evidence")
        actual[key] = value
    return actual


def decode_json(raw: bytes, label: str, *, limit: int,
                exact_canonical: bool) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= limit,
            "one complete bounded public JSON document is mandatory: " + label)
    try:
        actual = json.loads(
            raw, object_pairs_hook=unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                EvidenceError("nonfinite public JSON is forbidden: " + label),
            ),
        )
    except (UnicodeError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise EvidenceError("invalid complete public JSON: " + label) from error
    require(type(actual) is dict
            and (not exact_canonical or canonical(actual) == raw),
            "truncated, concatenated, or noncanonical public JSON: " + label)
    return actual


def _block_source(kind: str, message: str) -> None:
    _SOURCE_BLOCKED[kind] += 1
    raise EvidenceError("the candidate-free source-only wall rejected " + message)


def source_audit_wall(event: str, arguments: tuple[Any, ...]) -> None:
    if not _SOURCE_WALL_ACTIVE:
        return
    if event == "open":
        path = arguments[0] if arguments else None
        mode = arguments[1] if len(arguments) > 1 else None
        flags = arguments[2] if len(arguments) > 2 else 0
        if type(mode) is str and any(letter in mode for letter in "wax+"):
            _block_source("mutation", "a file mutation")
        if type(flags) is int and (
            flags & os.O_ACCMODE != os.O_RDONLY
            or flags & (os.O_CREAT | os.O_TRUNC | os.O_APPEND | os.O_EXCL)
        ):
            _block_source("mutation", "a file-descriptor mutation")
        approved = frozenset(ROOT + "/" + relative for relative in PUBLIC_OWNERS)
        if type(path) is not str or path not in approved:
            spelling = path if type(path) is str else "nonpath-descriptor"
            lowered = spelling.lower()
            if any(token in lowered for token in
                   ("archive", "holdout", "sealed", "hidden", "fixture")):
                _block_source("archive_holdout_fixture", "a restricted case owner")
            if "candidates" in lowered:
                _block_source("candidate", "a candidate owner")
            if lowered.endswith((".so", ".dylib", ".dll")) or spelling == PYTHON:
                _block_source("native", "a native owner")
            _block_source("foreign_read", "an unapproved file owner")
    elif event == "import":
        name = arguments[0] if arguments else "unknown"
        if type(name) is str and (name == "candidates"
                                  or name.startswith("candidates.")):
            _block_source("candidate", "a candidate import")
        _block_source("native", "a late source-only module/native import")
    elif event.startswith(("subprocess.", "os.posix_spawn", "os.spawn",
                           "os.exec", "os.fork", "os.system")):
        _block_source("process", "a process launch")
    elif event.startswith(("ctypes.", "socket.", "os.dlopen")):
        _block_source("native", "native activation or external communication")
    elif event.startswith(("os.mkdir", "os.rmdir", "os.remove", "os.unlink",
                           "os.rename", "os.replace", "os.chmod", "os.chown",
                           "os.link", "os.symlink", "os.truncate", "shutil.")):
        _block_source("mutation", "a filesystem mutation")
    elif event in ("os.listdir", "os.scandir", "glob.glob"):
        _block_source("foreign_read", "directory, fixture, or archive enumeration")


def blocked_clock(*_arguments: Any, **_keywords: Any) -> Any:
    _block_source("clock", "a clock sample or timer")


def install_source_wall() -> None:
    global _SOURCE_WALL_ACTIVE, _SOURCE_WALL_INSTALLED
    require(_SOURCE_WALL_INSTALLED is False,
            "the one-way candidate-free source-only wall was installed twice")
    sys.addaudithook(source_audit_wall)
    _SOURCE_WALL_INSTALLED = True
    _SOURCE_WALL_ACTIVE = True
    for name in _CLOCK_NAMES:
        setattr(time, name, blocked_clock)


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE
            and os.path.realpath(__file__) == ROOT + "/" + SOURCE
            and os.path.realpath(ROOT) == ROOT,
            "require the exact owned source and isolated pinned CPython 3.14.6")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate escaped into the candidate-free evidence controller")


def read_regular(path: str, *, maximum: int,
                 expected_sha256: str) -> tuple[bytes, dict[str, Any]]:
    checked_digest(expected_sha256, path)
    require(type(path) is str and os.path.isabs(path)
            and os.path.abspath(path) == path and os.path.realpath(path) == path
            and type(maximum) is int and 0 < maximum <= MAX_NATIVE_BYTES,
            "an exact no-symlink bounded first-party owner is mandatory")
    descriptor = os.open(
        path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode) and first.st_nlink == 1
                and first.st_uid == os.geteuid()
                and 0 < first.st_size <= maximum,
                "a bounded uniquely owned regular source/native owner changed")
        remaining = first.st_size
        pieces: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "a complete independently pinned owner was truncated")
            pieces.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "a pinned owner concealed a trailing replacement")
        last = os.fstat(descriptor)
        require(all(getattr(first, field) == getattr(last, field) for field in (
            "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns",
            "st_nlink",
        )), "an independently pinned owner changed during authentication")
    finally:
        os.close(descriptor)
    raw = b"".join(pieces)
    fingerprint = hashlib.sha256(raw).hexdigest()
    require(fingerprint == expected_sha256,
            "the independently pinned complete owner changed: " + path)
    return raw, {
        "path": path, "sha256": fingerprint, "bytes": len(raw),
        "device": first.st_dev, "inode": first.st_ino,
    }


def validate_public_manifest(value: Any) -> dict[str, Any]:
    require(type(value) is dict,
            "the exact frozen preexisting v2 public manifest is mandatory")
    expected = {
        "schema": BENCHMARK_SCHEMA + "-public-protocol-commitment",
        "source": BENCHMARK_SOURCE,
        "documentation": BENCHMARK_PROTOCOL,
        "pinned_python": PYTHON,
        "python_version": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "canonical_matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "dataset_count": DATASET_COUNT,
        "text_dataset_count": 47,
        "bytes_dataset_count": 47,
        "text_case_count": DOMAIN_CASE_COUNT,
        "bytes_case_count": DOMAIN_CASE_COUNT,
        "operation_count": OPERATIONS_PER_DATASET,
        "root_agent_may_run_candidate_only_after_commit_and_push": True,
        "benchmark_files_read": 0,
        "fixture_files_read": 0,
        "sealed_cases_read": 0,
        "hidden_cases_read": 0,
        "archive_files_read": 0,
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False,
        "final_winner_selected": False,
        "actual_public_candidate_correctness_run": "NOT RUN",
        "actual_public_candidate_performance_run": "NOT RUN",
    }
    for key, actual in expected.items():
        require(value.get(key) == actual,
                "the exact frozen enlarged public commitment changed: " + key)
    text = value.get("public_text_datasets")
    binary = value.get("public_bytes_datasets")
    operations = value.get("public_operations")
    require(type(text) is list and len(text) == 47
            and type(binary) is list and len(binary) == 47
            and type(operations) is list and len(operations) == OPERATIONS_PER_DATASET
            and all(type(item) is str and item.startswith("text.") for item in text)
            and all(type(item) is str and item.startswith("bytes.") for item in binary)
            and all(type(item) is str and bool(item) for item in operations)
            and len(set(text + binary)) == DATASET_COUNT
            and len(set(operations)) == OPERATIONS_PER_DATASET,
            "the complete equal-domain public dataset/operation vector changed")
    return value


def validate_controller_manifest(value: Any) -> None:
    require(type(value) is dict,
            "the frozen independent correctness-evidence manifest is mandatory")
    expected = {
        "schema": SCHEMA + "-public-protocol-commitment",
        "controller_source": SOURCE,
        "controller_protocol": PROTOCOL,
        "controller_manifest": MANIFEST,
        "benchmark_source": BENCHMARK_SOURCE,
        "benchmark_source_sha256": BENCHMARK_SOURCE_SHA256,
        "benchmark_protocol": BENCHMARK_PROTOCOL,
        "benchmark_protocol_sha256": BENCHMARK_PROTOCOL_SHA256,
        "benchmark_manifest": BENCHMARK_MANIFEST,
        "benchmark_manifest_sha256": BENCHMARK_MANIFEST_SHA256,
        "pinned_python": PYTHON,
        "python_version": "3.14.6",
        "canonical_matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "text_case_count": DOMAIN_CASE_COUNT,
        "bytes_case_count": DOMAIN_CASE_COUNT,
        "canonical_stdout_preserved_byte_for_byte": True,
        "all_actual_mismatches_preserved_on_pass_or_fail": True,
        "individual_passing_outcomes_exposed_by_frozen_benchmark": False,
        "individual_passing_outcomes_fabricated": False,
        "correctness_only_invocations_per_authorized_run": 1,
        "candidate_workers_per_authorized_run": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "sealed_cases_read": 0,
        "hidden_cases_read": 0,
        "archive_files_read": 0,
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False,
        "final_winner_selected": False,
        "source_only_candidate_imports": 0,
        "source_only_processes_started": 0,
        "source_only_clock_samples": 0,
        "source_only_candidate_owners_read": 0,
        "source_only_native_owners_read": 0,
        "source_only_files_written": 0,
        "requires_root_authorization": True,
        "requires_committed_pushed_source_acknowledgment": True,
        "requires_safe_clamped_candidate_acknowledgment": True,
        "actual_public_candidate_correctness_run": "NOT RUN",
    }
    for key, actual in expected.items():
        require(value.get(key) == actual,
                "the independent root-only evidence commitment changed: " + key)
    require(value.get("approved_output_directories") == list(APPROVED_DIRECTORIES)
            and value.get("required_caller_pinned_candidate_owners")
            == [ADAPTER, NATIVE_ENGINE, "candidates/_rust_bridge.<official-extension-suffix>"]
            and value.get("source_only_modes") == ["--verify-source", "--self-test"]
            and value.get("root_only_mode") == "--run",
            "the frozen source-only, owner-pin, or exclusive-output policy changed")


def authenticate_public_sources(options: argparse.Namespace) -> dict[str, Any]:
    expected = {
        SOURCE: checked_digest(options.source_sha256, "evidence controller source"),
        PROTOCOL: checked_digest(options.protocol_sha256, "evidence controller protocol"),
        MANIFEST: checked_digest(options.manifest_sha256, "evidence controller manifest"),
        BENCHMARK_SOURCE: BENCHMARK_SOURCE_SHA256,
        BENCHMARK_PROTOCOL: BENCHMARK_PROTOCOL_SHA256,
        BENCHMARK_MANIFEST: BENCHMARK_MANIFEST_SHA256,
    }
    owners: dict[str, dict[str, Any]] = {}
    content: dict[str, bytes] = {}
    for relative in PUBLIC_OWNERS:
        raw, owner = read_regular(
            ROOT + "/" + relative, maximum=MAX_PUBLIC_BYTES,
            expected_sha256=expected[relative],
        )
        content[relative] = raw
        owner["relative"] = relative
        owners[relative] = owner
    controller_manifest = decode_json(
        content[MANIFEST], "frozen evidence manifest", limit=MAX_PUBLIC_BYTES,
        exact_canonical=False,
    )
    validate_controller_manifest(controller_manifest)
    benchmark_manifest = decode_json(
        content[BENCHMARK_MANIFEST], "frozen existing public manifest",
        limit=MAX_PUBLIC_BYTES, exact_canonical=False,
    )
    validate_public_manifest(benchmark_manifest)
    return {
        "owners": owners,
        "controller_manifest": controller_manifest,
        "benchmark_manifest": benchmark_manifest,
    }


def approved_paths(output: Any) -> tuple[str, str, tuple[str, ...]]:
    require(type(output) is str and 1 <= len(output) <= 240
            and "\\" not in output and "\x00" not in output,
            "one exact bounded approved public-evidence JSON path is mandatory")
    if os.path.isabs(output):
        require(output.startswith(ROOT + "/"),
                "an evidence path outside the owned repository is forbidden")
        relative = output[len(ROOT) + 1:]
    else:
        relative = output
    parts = tuple(relative.split("/"))
    require(all(component not in ("", ".", "..") for component in parts)
            and "/".join(parts) == relative,
            "an escaping, empty, or noncanonical public evidence path is forbidden")
    directory = "/".join(parts[:-1])
    name = parts[-1]
    stem = name[:-5] if name.endswith(".json") else ""
    require(directory in APPROVED_DIRECTORIES and 1 <= len(stem) <= 96
            and not stem.endswith("-publication-receipt")
            and stem[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and stem[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and "--" not in stem
            and all(letter in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for letter in stem),
            "publish only a strict named JSON inside either approved v2 directory")
    receipt = directory + "/" + stem + "-publication-receipt.json"
    require(receipt != relative,
            "the complete report and durable receipt must be distinct")
    return relative, receipt, parts


def typed_public_value(value: Any, *, domain: str,
                       permit_buffer: bool) -> int:
    require(type(value) is dict and type(value.get("type")) is str,
            "a complete original typed public case value is mandatory")
    kind = value["type"]
    if kind == "str":
        require(domain == "text" and set(value) == {"type", "value"}
                and type(value["value"]) is str,
                "a genuine original public text value was substituted")
        return len(value["value"])
    require(domain == "bytes"
            and kind in (("bytes", "bytearray", "memoryview")
                         if permit_buffer else ("bytes",)),
            "a genuine original byte/buffer case value was substituted")
    expected_keys = ({"type", "hex", "readonly", "format", "shape"}
                     if kind == "memoryview" else {"type", "hex"})
    require(set(value) == expected_keys and type(value.get("hex")) is str,
            "an exact original public byte encoding was substituted")
    try:
        decoded = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise EvidenceError("an original public byte encoding is invalid") from error
    require(decoded.hex() == value["hex"],
            "an original public byte encoding is not canonical")
    if kind == "memoryview":
        require(type(value.get("readonly")) is bool and value.get("format") == "B"
                and value.get("shape") == [len(decoded)],
                "the exact original public memoryview shape/mutability changed")
    return len(decoded)


def validate_outcome(value: Any) -> None:
    require(type(value) is dict and value.get("status") in ("return", "raise")
            and all(type(value.get(key)) is list
                    for key in ("callbacks", "buffer_events", "warnings")),
            "an exact baseline/Rust public outcome concealed calls, buffers, or warnings")


def validate_report(report: Any, protocol: Mapping[str, Any], *,
                    benchmark_pid: int, controller_pid: int) -> dict[str, Any]:
    require(type(report) is dict,
            "the unchanged complete v2 correctness document is mandatory")
    expected = {
        "schema": BENCHMARK_SCHEMA + "-actual-untimed-correctness",
        "label": LABEL,
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_denominator": CASE_COUNT,
        "actual_baseline_cases": CASE_COUNT,
        "actual_rust_cases": CASE_COUNT,
        "actual_candidate_workers": 1,
        "timing_trials_run": 0,
        "clock_samples": 0,
        "benchmark_files_read": 0,
        "fixture_files_read": 0,
        "sealed_cases_read": 0,
        "hidden_cases_read": 0,
        "archive_files_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False,
        "final_winner_selected": False,
    }
    required_keys = set(expected) | {
        "status", "baseline_records_sha256", "rust_records_sha256",
        "baseline_pid", "rust_pid", "mismatch_count", "first_mismatch",
        "all_mismatches",
    }
    require(set(report) == required_keys,
            "the unchanged complete v2 correctness schema gained or lost fields")
    for key, actual in expected.items():
        require(report.get(key) == actual,
                "the actual frozen untimed correctness evidence changed: " + key)
    baseline_hash = checked_digest(report.get("baseline_records_sha256"),
                                   "full 10,434-case baseline vector")
    rust_hash = checked_digest(report.get("rust_records_sha256"),
                               "full 10,434-case Rust vector")
    baseline_pid = report.get("baseline_pid")
    rust_pid = report.get("rust_pid")
    require(type(benchmark_pid) is int and benchmark_pid > 0
            and type(controller_pid) is int and controller_pid > 0
            and type(baseline_pid) is int and baseline_pid > 0
            and type(rust_pid) is int and rust_pid > 0
            and len({controller_pid, benchmark_pid, baseline_pid, rust_pid}) == 4,
            "the coordinator, isolated benchmark, stdlib, and Rust PIDs must differ")
    mismatches = report.get("all_mismatches")
    require(type(mismatches) is list and type(report.get("mismatch_count")) is int
            and 0 <= len(mismatches) <= CASE_COUNT
            and report["mismatch_count"] == len(mismatches)
            and report.get("first_mismatch") == (mismatches[0] if mismatches else None)
            and report.get("status") == ("FAIL" if mismatches else "PASS")
            and (baseline_hash != rust_hash if mismatches
                 else baseline_hash == rust_hash),
            "a failed outcome, first failure, full-vector digest, or case was hidden")
    datasets = protocol["public_text_datasets"] + protocol["public_bytes_datasets"]
    operations = protocol["public_operations"]
    expected_mismatch_keys = {
        "case", "dataset", "workload", "domain", "operation", "lifecycle",
        "flags", "pattern", "subject", "replacement", "limit", "pos",
        "endpos", "baseline_outcome", "rust_outcome",
    }
    previous = -1
    for item in mismatches:
        require(type(item) is dict and set(item) == expected_mismatch_keys,
                "an exact complete genuine public mismatch field was concealed")
        identifier = item.get("case")
        require(type(identifier) is str
                and identifier.startswith("rust-public-practice.v2."),
                "an actual complete public mismatch identifier was substituted")
        suffix = identifier[len("rust-public-practice.v2."):]
        require(len(suffix) == 5 and suffix.isascii() and suffix.isdecimal(),
                "a canonical frozen public case ordinal was substituted")
        position = int(suffix)
        require(previous < position < CASE_COUNT,
                "an actual mismatch was omitted, duplicated, reordered, or injected")
        dataset_index, operation_index = divmod(position, OPERATIONS_PER_DATASET)
        domain = "text" if dataset_index < 47 else "bytes"
        require(item.get("dataset") == datasets[dataset_index]
                and item.get("operation") == operations[operation_index]
                and item.get("domain") == domain
                and type(item.get("workload")) is str and bool(item["workload"])
                and type(item.get("lifecycle")) is str and bool(item["lifecycle"]),
                "the original public dataset, domain, workload, or operation changed")
        require(type(item.get("flags")) is int and item["flags"] >= 0
                and type(item.get("limit")) is int and item["limit"] > 0
                and type(item.get("pos")) is int
                and type(item.get("endpos")) is int,
                "an exact original mismatch flag, limit, or bounds disappeared")
        typed_public_value(item["pattern"], domain=domain, permit_buffer=False)
        subject_length = typed_public_value(
            item["subject"], domain=domain, permit_buffer=True,
        )
        typed_public_value(item["replacement"], domain=domain, permit_buffer=False)
        require(0 <= item["pos"] <= item["endpos"] <= subject_length,
                "an exact original mismatch bound escaped its complete subject")
        baseline = item["baseline_outcome"]
        rust = item["rust_outcome"]
        validate_outcome(baseline)
        validate_outcome(rust)
        require(baseline != rust,
                "an actual public mismatch was replaced by a passing outcome")
        previous = position
    return dict(report)


def authenticate_candidate_owners(options: argparse.Namespace) -> dict[str, Any]:
    adapter_pin = checked_digest(options.adapter_sha256, "canonical public Rust adapter")
    engine_pin = checked_digest(options.native_engine_sha256, "semantic Rust native engine")
    bridge_pin = checked_digest(options.native_bridge_sha256, "canonical Rust native bridge")
    python_pin = checked_digest(options.python_sha256, "exact pinned CPython executable")
    _, adapter = read_regular(ROOT + "/" + ADAPTER, maximum=MAX_PUBLIC_BYTES,
                              expected_sha256=adapter_pin)
    _, engine = read_regular(ROOT + "/" + NATIVE_ENGINE, maximum=MAX_NATIVE_BYTES,
                             expected_sha256=engine_pin)
    bridges: list[dict[str, Any]] = []
    for suffix in dict.fromkeys(EXTENSION_SUFFIXES):
        path = ROOT + "/candidates/_rust_bridge" + suffix
        try:
            _, bridge = read_regular(path, maximum=MAX_NATIVE_BYTES,
                                     expected_sha256=bridge_pin)
        except FileNotFoundError:
            continue
        bridges.append(bridge)
    require(len(bridges) == 1,
            "exactly one independently pinned official CPython Rust bridge is required")
    _, interpreter = read_regular(PYTHON, maximum=MAX_NATIVE_BYTES,
                                  expected_sha256=python_pin)
    adapter["relative"] = ADAPTER
    engine["relative"] = NATIVE_ENGINE
    bridges[0]["relative"] = bridges[0]["path"][len(ROOT) + 1:]
    return {"adapter": adapter, "native_engine": engine,
            "native_bridge": bridges[0], "pinned_python": interpreter}


def open_output_directory(parts: tuple[str, ...]) -> tuple[int, list[int], dict[str, Any]]:
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptors: list[int] = []
    try:
        current = os.open(ROOT, flags)
        descriptors.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the owned evidence root is not a no-follow real directory")
        for name in parts[:-1]:
            try:
                following = os.open(name, flags, dir_fd=current)
            except FileNotFoundError:
                os.mkdir(name, mode=0o700, dir_fd=current)
                os.fsync(current)
                following = os.open(name, flags, dir_fd=current)
            descriptors.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "an approved evidence component is not a no-follow directory")
            current = following
        info = os.fstat(current)
        return current, descriptors, {"device": info.st_dev, "inode": info.st_ino}
    except BaseException:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise


def verify_directory(directory: int, identity: Mapping[str, Any]) -> None:
    info = os.fstat(directory)
    require(stat.S_ISDIR(info.st_mode)
            and info.st_dev == identity.get("device")
            and info.st_ino == identity.get("inode"),
            "the retained no-follow approved output directory was substituted")


def assert_fresh(directory: int, name: str) -> None:
    try:
        os.stat(name, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise EvidenceError("refusing to overwrite an existing evidence owner: " + name)


def publish_exclusive(directory: int, name: str, raw: bytes,
                      identity: Mapping[str, Any]) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_RECEIPT_BYTES,
            "the complete immutable evidence document exceeds its frozen bound")
    verify_directory(directory, identity)
    descriptor = os.open(
        name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        0o600, dir_fd=directory,
    )
    owner = os.fstat(descriptor)
    completed = False
    write_calls = 0
    try:
        require(stat.S_ISREG(owner.st_mode) and owner.st_nlink == 1,
                "the exclusively created public evidence is not a unique file")
        view = memoryview(raw)
        offset = 0
        while offset < len(view):
            count = os.write(descriptor, view[offset:])
            require(type(count) is int and count > 0,
                    "the complete exclusive public evidence write was truncated")
            offset += count
            write_calls += 1
        os.fsync(descriptor)
        os.fsync(directory)
        completed = True
    finally:
        if not completed:
            try:
                current = os.stat(name, dir_fd=directory, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == (owner.st_dev, owner.st_ino):
                    os.unlink(name, dir_fd=directory)
                    os.fsync(directory)
            finally:
                os.close(descriptor)
        else:
            os.close(descriptor)
    read_descriptor = os.open(
        name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory,
    )
    try:
        actual_owner = os.fstat(read_descriptor)
        require((actual_owner.st_dev, actual_owner.st_ino, actual_owner.st_size)
                == (owner.st_dev, owner.st_ino, len(raw)),
                "the actual durable evidence inode or complete length changed")
        chunks: list[bytes] = []
        remaining = len(raw)
        while remaining:
            chunk = os.read(read_descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the actual complete durable evidence readback was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(read_descriptor, 1) == b"",
                "the actual durable evidence readback concealed trailing bytes")
    finally:
        os.close(read_descriptor)
    actual = b"".join(chunks)
    fingerprint = hashlib.sha256(raw).hexdigest()
    require(actual == raw and hashlib.sha256(actual).hexdigest() == fingerprint,
            "the complete exclusive evidence readback omitted its original bytes")
    return {
        "sha256": fingerprint, "bytes": len(raw), "write_calls": write_calls,
        "file_fsync_completed": True, "directory_fsync_completed": True,
        "complete_readback_verified": True,
    }


def validate_commit(value: Any) -> str:
    require(type(value) is str and len(value) == 40
            and all(letter in "0123456789abcdef" for letter in value)
            and len(set(value)) > 1,
            "the root coordinator must acknowledge one real published Git commit")
    return value


def validate_options(options: argparse.Namespace) -> None:
    source_only = options.verify_source or options.self_test
    run_fields = (
        options.adapter_sha256, options.native_engine_sha256,
        options.native_bridge_sha256, options.python_sha256,
        options.output, options.published_commit,
    )
    if source_only:
        require(all(value is None for value in run_fields)
                and options.root_authorized is False
                and options.frozen_committed_pushed is False
                and options.safe_clamped_candidate is False,
                "source-only verification cannot authorize, pin, inspect, or run a candidate")
    else:
        require(options.run is True and all(type(value) is str for value in run_fields)
                and options.root_authorized is True
                and options.frozen_committed_pushed is True
                and options.safe_clamped_candidate is True,
                "root-only correctness evidence requires published-source and safe-candidate authorization")
        validate_commit(options.published_commit)
        approved_paths(options.output)
        for value, label in (
            (options.adapter_sha256, "canonical public Rust adapter"),
            (options.native_engine_sha256, "semantic Rust native engine"),
            (options.native_bridge_sha256, "canonical Rust native bridge"),
            (options.python_sha256, "exact pinned CPython executable"),
        ):
            checked_digest(value, label)


def run_authorized(options: argparse.Namespace,
                   sources: Mapping[str, Any]) -> dict[str, Any]:
    output, receipt, parts = approved_paths(options.output)
    candidate = authenticate_candidate_owners(options)
    directory, descriptors, identity = open_output_directory(parts)
    try:
        report_name = parts[-1]
        receipt_name = receipt.rsplit("/", 1)[-1]
        assert_fresh(directory, report_name)
        assert_fresh(directory, receipt_name)
        verify_directory(directory, identity)

        # This is the sole controller-created process and the sole comparison.
        # FAIL exits 1 with complete canonical stdout; it remains genuine data.
        process = subprocess.Popen(
            [PYTHON, "-I", "-B", ROOT + "/" + BENCHMARK_SOURCE,
             "--correctness-only"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=ROOT, shell=False,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
        )
        stdout, stderr = process.communicate()
        require(stderr == b"" and process.returncode in (0, 1),
                "the sole exact frozen correctness process failed before complete evidence")
        report = decode_json(stdout, "complete frozen correctness stdout",
                             limit=MAX_PROCESS_BYTES, exact_canonical=True)
        complete = validate_report(
            report, sources["benchmark_manifest"],
            benchmark_pid=process.pid, controller_pid=os.getpid(),
        )
        require(process.returncode == (0 if complete["status"] == "PASS" else 1),
                "the actual complete FAIL/PASS process exit was concealed")
        verify_runtime()
        verify_directory(directory, identity)
        require(authenticate_candidate_owners(options) == candidate,
                "the caller-pinned adapter, native engine, bridge, or CPython changed")

        publication = publish_exclusive(directory, report_name, stdout, identity)
        receipt_document = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS",
            "correctness_status": complete["status"],
            "practice_label": LABEL,
            "published_commit": options.published_commit,
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "manifest_sha256": options.manifest_sha256,
            "benchmark_source_relative": BENCHMARK_SOURCE,
            "benchmark_source_sha256": BENCHMARK_SOURCE_SHA256,
            "benchmark_protocol_sha256": BENCHMARK_PROTOCOL_SHA256,
            "benchmark_manifest_sha256": BENCHMARK_MANIFEST_SHA256,
            "pinned_python": candidate["pinned_python"],
            "canonical_public_adapter": candidate["adapter"],
            "native_engine": candidate["native_engine"],
            "native_bridge": candidate["native_bridge"],
            "matrix_sha256": MATRIX_SHA256,
            "case_denominator": CASE_COUNT,
            "text_case_denominator": DOMAIN_CASE_COUNT,
            "bytes_case_denominator": DOMAIN_CASE_COUNT,
            "actual_baseline_cases": complete["actual_baseline_cases"],
            "actual_rust_cases": complete["actual_rust_cases"],
            "baseline_records_sha256": complete["baseline_records_sha256"],
            "rust_records_sha256": complete["rust_records_sha256"],
            "controller_pid": os.getpid(),
            "benchmark_pid": process.pid,
            "baseline_pid": complete["baseline_pid"],
            "rust_pid": complete["rust_pid"],
            "correctness_only_invocations": 1,
            "actual_candidate_workers": 1,
            "benchmark_exit_code": process.returncode,
            "mismatch_count": complete["mismatch_count"],
            "all_mismatches_sha256": hashlib.sha256(
                canonical(complete["all_mismatches"]),
            ).hexdigest(),
            "all_mismatches": complete["all_mismatches"],
            "all_mismatches_preserved": True,
            "individual_passing_outcomes_exposed": False,
            "individual_passing_outcomes_fabricated": False,
            "canonical_stdout_preserved_byte_for_byte": True,
            "report_relative": output,
            "report_sha256": publication["sha256"],
            "report_bytes": publication["bytes"],
            "report_publication": publication,
            "receipt_relative": receipt,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "fixture_files_read": 0,
            "sealed_cases_read": 0,
            "hidden_cases_read": 0,
            "archive_files_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_sealed_final_holdout": False,
            "sealed_final_holdout_opened": False,
            "final_winner_selected": False,
        }
        receipt_bytes = canonical(receipt_document)
        require(len(receipt_bytes) <= MAX_RECEIPT_BYTES,
                "the complete all-failure root receipt exceeds its frozen bound")
        receipt_publication = publish_exclusive(
            directory, receipt_name, receipt_bytes, identity,
        )
        return {
            "schema": SCHEMA + "-compact-result",
            "status": complete["status"],
            "practice_label": LABEL,
            "published_commit": options.published_commit,
            "matrix_sha256": MATRIX_SHA256,
            "case_denominator": CASE_COUNT,
            "text_case_denominator": DOMAIN_CASE_COUNT,
            "bytes_case_denominator": DOMAIN_CASE_COUNT,
            "baseline_records_sha256": complete["baseline_records_sha256"],
            "rust_records_sha256": complete["rust_records_sha256"],
            "mismatch_count": complete["mismatch_count"],
            "all_mismatches_sha256": receipt_document["all_mismatches_sha256"],
            "report_relative": output,
            "report_publication": publication,
            "receipt_relative": receipt,
            "receipt_publication": receipt_publication,
            "correctness_only_invocations": 1,
            "actual_candidate_workers": 1,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "fixture_files_read": 0,
            "sealed_cases_read": 0,
            "hidden_cases_read": 0,
            "archive_files_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_sealed_final_holdout": False,
            "sealed_final_holdout_opened": False,
            "final_winner_selected": False,
        }
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def synthetic_report(protocol: Mapping[str, Any], indices: tuple[int, ...]) -> dict[str, Any]:
    baseline_hash = "12" * 32
    rust_hash = "34" * 32 if indices else baseline_hash
    cases: list[dict[str, Any]] = []
    datasets = protocol["public_text_datasets"] + protocol["public_bytes_datasets"]
    operations = protocol["public_operations"]
    for position in indices:
        dataset_index, operation_index = divmod(position, OPERATIONS_PER_DATASET)
        domain = "text" if dataset_index < 47 else "bytes"
        if domain == "text":
            pattern = {"type": "str", "value": "a"}
            subject = {"type": "str", "value": "a"}
            replacement = {"type": "str", "value": "b"}
        else:
            pattern = {"type": "bytes", "hex": "61"}
            subject = {"type": "memoryview", "hex": "61", "readonly": True,
                       "format": "B", "shape": [1]}
            replacement = {"type": "bytes", "hex": "62"}
        baseline = {"status": "return", "callbacks": [], "buffer_events": [],
                    "warnings": [], "value": "baseline"}
        rust = {"status": "return", "callbacks": [], "buffer_events": [],
                "warnings": [], "value": "rust"}
        cases.append({
            "case": "rust-public-practice.v2." + format(position, "05d"),
            "dataset": datasets[dataset_index], "workload": "synthetic-only",
            "domain": domain, "operation": operations[operation_index],
            "lifecycle": "synthetic-only", "flags": 0, "pattern": pattern,
            "subject": subject, "replacement": replacement, "limit": 1,
            "pos": 0, "endpos": 1,
            "baseline_outcome": baseline, "rust_outcome": rust,
        })
    return {
        "schema": BENCHMARK_SCHEMA + "-actual-untimed-correctness",
        "status": "FAIL" if cases else "PASS", "label": LABEL,
        "python": "3.14.6", "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256, "case_denominator": CASE_COUNT,
        "actual_baseline_cases": CASE_COUNT, "actual_rust_cases": CASE_COUNT,
        "baseline_records_sha256": baseline_hash,
        "rust_records_sha256": rust_hash, "baseline_pid": 201, "rust_pid": 202,
        "mismatch_count": len(cases), "first_mismatch": cases[0] if cases else None,
        "all_mismatches": cases, "actual_candidate_workers": 1,
        "timing_trials_run": 0, "clock_samples": 0,
        "benchmark_files_read": 0, "fixture_files_read": 0,
        "sealed_cases_read": 0, "hidden_cases_read": 0,
        "archive_files_read": 0, "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False, "final_winner_selected": False,
    }


def source_self_test(options: argparse.Namespace,
                     sources: Mapping[str, Any]) -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and condition is True,
                "a candidate-free evidence positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        require(type(name) is str and name not in rejected and callable(operation),
                "a candidate-free hostile control was duplicated")
        try:
            operation()
        except (EvidenceError, ValueError, TypeError):
            rejected.append(name)
            return
        raise EvidenceError("a candidate-free hostile control was accepted: " + name)

    protocol = sources["benchmark_manifest"]
    passing = synthetic_report(protocol, ())
    failing = synthetic_report(protocol, (0, DOMAIN_CASE_COUNT, CASE_COUNT - 1))
    accept("preserve-complete-synthetic-pass-with-full-vector-digests",
           validate_report(passing, protocol, benchmark_pid=200,
                           controller_pid=100)["status"] == "PASS")
    accept("preserve-every-synthetic-text-and-bytes-failure",
           validate_report(failing, protocol, benchmark_pid=200,
                           controller_pid=100)["mismatch_count"] == 3)
    accept("accept-approved-phase3-evidence-path",
           approved_paths("oracle/phase3/evidence/v2-public.json")[0]
           == "oracle/phase3/evidence/v2-public.json")
    accept("accept-approved-public-practice-path",
           approved_paths("experiments/rust_public_practice_v2/v2-public.json")[0]
           == "experiments/rust_public_practice_v2/v2-public.json")
    accept("retain-exact-10434-case-balanced-public-denominator",
           len(protocol["public_text_datasets"])
           * len(protocol["public_operations"]) == DOMAIN_CASE_COUNT
           and len(protocol["public_bytes_datasets"])
           * len(protocol["public_operations"]) == DOMAIN_CASE_COUNT)

    for name, raw in (
        ("duplicate-keys", b'{"x":1,"x":2}\n'),
        ("nonfinite", b'{"x":NaN}\n'),
        ("truncated", b'{"x":1'),
        ("concatenated", b'{"x":1}\n{"y":2}\n'),
        ("noncanonical-space", b'{"x": 1}\n'),
        ("noncanonical-order", b'{"z":1,"a":2}\n'),
        ("empty", b""),
    ):
        reject("reject-" + name,
               lambda raw=raw: decode_json(
                   raw, "synthetic hostile JSON", limit=256, exact_canonical=True,
               ))

    mutations: list[tuple[str, Any]] = [
        ("omitted-mismatch", lambda value: value["all_mismatches"].pop()),
        ("hidden-fail-status", lambda value: value.update(status="PASS")),
        ("changed-case-denominator", lambda value: value.update(case_denominator=CASE_COUNT - 1)),
        ("changed-vector-digest", lambda value: value.update(rust_records_sha256=value["baseline_records_sha256"])),
        ("same-worker-pid", lambda value: value.update(rust_pid=value["baseline_pid"])),
        ("reused-benchmark-pid", lambda value: value.update(baseline_pid=200)),
        ("hidden-clock-sample", lambda value: value.update(clock_samples=1)),
        ("hidden-sealed-read", lambda value: value.update(sealed_cases_read=1)),
        ("hidden-case-read", lambda value: value.update(hidden_cases_read=1)),
        ("hidden-archive-read", lambda value: value.update(archive_files_read=1)),
        ("hidden-timing", lambda value: value.update(timing_trials_run=1)),
        ("extra-report-field", lambda value: value.update(injected="forbidden")),
        ("changed-mismatch-domain", lambda value: value["all_mismatches"][0].update(domain="bytes")),
        ("changed-mismatch-dataset", lambda value: value["all_mismatches"][0].update(dataset="text.foreign")),
        ("changed-mismatch-operation", lambda value: value["all_mismatches"][0].update(operation="module.foreign")),
        ("duplicate-mismatch", lambda value: value["all_mismatches"].insert(1, value["all_mismatches"][0])),
        ("omitted-mismatch-outcome", lambda value: value["all_mismatches"][0].pop("rust_outcome")),
        ("invalid-memoryview-shape", lambda value: value["all_mismatches"][1]["subject"].update(shape=[2])),
        ("uppercase-byte-encoding", lambda value: value["all_mismatches"][1]["pattern"].update(hex="AB")),
    ]
    for name, mutate in mutations:
        forged = json.loads(json.dumps(failing))
        mutate(forged)
        reject("reject-" + name,
               lambda forged=forged: validate_report(
                   forged, protocol, benchmark_pid=200, controller_pid=100,
               ))

    for index, output in enumerate((
        "/tmp/escape.json", "../escape.json", "oracle/phase3/escape.json",
        "oracle/phase3/evidence/../escape.json",
        "experiments/rust_public_practice_v2/.json",
        "experiments/rust_public_practice_v2/UPPER.json",
        "experiments/rust_public_practice_v2/already-publication-receipt.json",
        "experiments/rust_public_practice_v2/two--hyphens.json",
        "experiments\\rust_public_practice_v2\\escape.json",
        "experiments/rust_public_practice_v2/nested/escape.json",
    )):
        reject("reject-foreign-output-" + format(index, "02d"),
               lambda output=output: approved_paths(output))

    for name, operation in (
        ("actual-candidate-import", lambda: sys.audit(
            "import", "candidates.rust_candidate", None, None, None, None,
        )),
        ("actual-process-launch", lambda: sys.audit(
            "subprocess.Popen", PYTHON, [PYTHON], ROOT, {},
        )),
        ("actual-clock-sample", lambda: time.perf_counter()),
        ("actual-file-mutation", lambda: sys.audit(
            "open", ROOT + "/oracle/phase3/evidence/forbidden.json", "wb",
            os.O_WRONLY | os.O_CREAT,
        )),
        ("actual-holdout-open", lambda: sys.audit(
            "open", ROOT + "/oracle/phase3/sealed-holdout.json", "rb", os.O_RDONLY,
        )),
        ("actual-archive-open", lambda: sys.audit(
            "open", ROOT + "/oracle/phase3/private-archive.json", "rb", os.O_RDONLY,
        )),
        ("actual-native-owner-open", lambda: sys.audit(
            "open", PYTHON, "rb", os.O_RDONLY,
        )),
        ("actual-native-load", lambda: sys.audit(
            "ctypes.dlopen", ROOT + "/candidates/_rust_engine.so",
        )),
        ("actual-foreign-file-open", lambda: sys.audit(
            "open", "/tmp/foreign-v2-source.json", "rb", os.O_RDONLY,
        )),
    ):
        reject("wall-reject-" + name, operation)

    for name in ("candidate", "process", "clock", "mutation",
                 "archive_holdout_fixture", "native", "foreign_read"):
        accept("physically-block-" + name, _SOURCE_BLOCKED[name] > 0)
    verify_runtime()
    accept("never-import-candidate-or-start-correctness",
           not any(name == "candidates" or name.startswith("candidates.")
                   for name in sys.modules))
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "manifest_sha256": options.manifest_sha256,
        "benchmark_source_sha256": BENCHMARK_SOURCE_SHA256,
        "benchmark_protocol_sha256": BENCHMARK_PROTOCOL_SHA256,
        "benchmark_manifest_sha256": BENCHMARK_MANIFEST_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "case_denominator": CASE_COUNT,
        "text_case_denominator": DOMAIN_CASE_COUNT,
        "bytes_case_denominator": DOMAIN_CASE_COUNT,
        "accepted_source_controls": len(accepted),
        "rejected_hostile_controls": len(rejected),
        "physically_blocked_effects": dict(_SOURCE_BLOCKED),
        "candidate_imports": 0,
        "processes_started": 0,
        "candidate_owners_read": 0,
        "native_owners_read": 0,
        "clock_samples": 0,
        "files_written": 0,
        "fixture_files_read": 0,
        "sealed_cases_read": 0,
        "hidden_cases_read": 0,
        "archive_files_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preserve exactly one complete frozen public Rust v2 correctness result",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-source", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--adapter-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--python-sha256")
    parser.add_argument("--output")
    parser.add_argument("--published-commit")
    parser.add_argument("--root-authorized", action="store_true")
    parser.add_argument("--frozen-committed-pushed", action="store_true")
    parser.add_argument("--safe-clamped-candidate", action="store_true")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    validate_options(options)
    verify_runtime()
    if options.verify_source or options.self_test:
        install_source_wall()
    sources = authenticate_public_sources(options)
    if options.verify_source:
        document = {
            "schema": SCHEMA + "-verified-public-source",
            "status": "PASS",
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "manifest_sha256": options.manifest_sha256,
            "benchmark_source_sha256": BENCHMARK_SOURCE_SHA256,
            "benchmark_protocol_sha256": BENCHMARK_PROTOCOL_SHA256,
            "benchmark_manifest_sha256": BENCHMARK_MANIFEST_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "case_denominator": CASE_COUNT,
            "text_case_denominator": DOMAIN_CASE_COUNT,
            "bytes_case_denominator": DOMAIN_CASE_COUNT,
            "candidate_imports": 0,
            "processes_started": 0,
            "candidate_owners_read": 0,
            "native_owners_read": 0,
            "clock_samples": 0,
            "files_written": 0,
            "fixture_files_read": 0,
            "sealed_cases_read": 0,
            "hidden_cases_read": 0,
            "archive_files_read": 0,
            "candidate_qualified_for_sealed_final_holdout": False,
            "sealed_final_holdout_opened": False,
            "final_winner_selected": False,
        }
    elif options.self_test:
        document = source_self_test(options, sources)
    else:
        document = run_authorized(options, sources)
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (EvidenceError, OSError) as error:
        print("frozen Rust public v2 correctness evidence failed closed: " + str(error),
              file=sys.stderr)
        raise SystemExit(1) from error
