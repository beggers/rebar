#!/usr/bin/env python3
"""Immutable successor for authenticated, public-only Rust profiling.

The original first-party driver remains frozen and is executed only after its
source, documentation, manifest, and preserved failed run are authenticated.
Strict source modes execute no candidate, profiler, clock, subprocess, or write.
Actual profiling remains restricted to an explicitly selected fresh V2 session.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import types
from typing import Any


ROOT = Path("/home/dev-user/src/rebar")
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SOURCE_RELATIVE = "tools/rust_public_profile_v2.py"
PROTOCOL_RELATIVE = "oracle/phase3/RUST-PUBLIC-PROFILE-V2.md"
MANIFEST_RELATIVE = "oracle/phase3/rust-public-profile-v2.json"
APPROVED_OUTPUT_PREFIX = "experiments/rust_public_profile_v2"
SCHEMA = "rebar-rust-fresh-public-profile-v2"
MAX_OWNED_FILE_BYTES = 2 * 1024 * 1024
MAX_TARGET_PID = 2_147_483_647

V1_SOURCE_RELATIVE = "tools/rust_public_profile_v1.py"
V1_PROTOCOL_RELATIVE = "oracle/phase3/RUST-PUBLIC-PROFILE-V1.md"
V1_MANIFEST_RELATIVE = "oracle/phase3/rust-public-profile-v1.json"
V1_SOURCE_SHA256 = (
    "ada1e9cfc8684ecb4fcf9294057347018b6058fc1619ae9de6a8b31097aa1562"
)
V1_PROTOCOL_SHA256 = (
    "6664f17ddd65c1953782f43b7fe1fa01427f1f510adfbad86fe8efdb135829ba"
)
V1_MANIFEST_SHA256 = (
    "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5"
)

FAILED_ROOT_RELATIVE = "experiments/rust_public_profile_v1/public-run-001"
FAILED_ROOT_DEVICE = 2064
FAILED_ROOT_INODE = 526004
FAILED_ROOT_MODE = 0o700
FAILED_STDOUT_RELATIVE = FAILED_ROOT_RELATIVE + "/stdlib.collector.stdout.json"
FAILED_STDOUT_SHA256 = (
    "057d2eb19a2c24e11688fa0419047e50f6720cbafd41b7ec3bd7ee763691aff0"
)
FAILED_STDOUT_BYTES = 2200
FAILED_STDOUT_INODE = 526025
FAILED_NORMALIZED_SHA256 = (
    "8471fcd2497eba55c4ff69c72475c15ff8c55162f75e9ac240b558720f1602ba"
)
FAILED_NORMALIZED_BYTES = 2139
FAILED_BANNER_PID = 91
FAILED_PAIRED_RELATIVE = FAILED_ROOT_RELATIVE + "/paired-timing.raw.json"
FAILED_PAIRED_SHA256 = (
    "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85"
)
FAILED_PAIRED_BYTES = 504907
FAILED_PAIRED_INODE = 526015
FAILED_PAIRED_ROWS = 1664
FAILED_PAIRED_ROWS_SHA256 = (
    "ce5ddb143be0d58588d2b18540c0db1b716eebb138cfe32a04690a0efe62c378"
)
FAILED_EXPECTED_RECORDS_SHA256 = (
    "41f83dc761a93ea8e3203f46cedbba1e10918cf053194c20b37b8c209e992242"
)

ALLOWED_OWNED_READS = frozenset({
    SOURCE_RELATIVE,
    PROTOCOL_RELATIVE,
    MANIFEST_RELATIVE,
    V1_SOURCE_RELATIVE,
    V1_PROTOCOL_RELATIVE,
    V1_MANIFEST_RELATIVE,
    FAILED_STDOUT_RELATIVE,
    FAILED_PAIRED_RELATIVE,
})


class PublicProfileSuccessorError(Exception):
    """Reject substituted source, failed-run evidence, or collector output."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublicProfileSuccessorError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def _directory_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    )


def _verify_runtime(*, permit_candidate: bool = False) -> None:
    expected_source = str(ROOT / SOURCE_RELATIVE)
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.realpath(sys.executable) == str(PINNED_PYTHON)
        and os.path.realpath(str(ROOT)) == str(ROOT)
        and os.path.abspath(__file__) == expected_source
        and os.path.realpath(__file__) == expected_source,
        "use exactly the pinned isolated CPython and no-symlink V2 source",
    )
    if not permit_candidate:
        require(
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
            "a candidate escaped into strictly candidate-free V2 source mode",
        )


def _read_allowed(relative: str) -> bytes:
    require(
        type(relative) is str and relative in ALLOWED_OWNED_READS,
        "only eight exact first-party V2 source/history components may be read",
    )
    parts = PurePosixPath(relative).parts
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), _directory_flags())
        opened.append(current)
        root_details = os.fstat(current)
        require(
            stat.S_ISDIR(root_details.st_mode),
            "the frozen first-party workspace is not a no-follow directory",
        )
        for index, component in enumerate(parts[:-1]):
            current = os.open(component, _directory_flags(), dir_fd=current)
            opened.append(current)
            details = os.fstat(current)
            require(
                stat.S_ISDIR(details.st_mode),
                "a frozen first-party component is not a no-follow directory",
            )
            if parts[: index + 1] == PurePosixPath(FAILED_ROOT_RELATIVE).parts:
                require(
                    details.st_dev == FAILED_ROOT_DEVICE
                    and details.st_ino == FAILED_ROOT_INODE
                    and stat.S_IMODE(details.st_mode) == FAILED_ROOT_MODE,
                    "the preserved V1 failed-run root identity was substituted",
                )
        descriptor = os.open(
            parts[-1],
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_CLOEXEC", 0),
            dir_fd=current,
        )
        opened.append(descriptor)
        details = os.fstat(descriptor)
        require(
            stat.S_ISREG(details.st_mode),
            "an authenticated first-party source/evidence owner is not regular",
        )
        if relative == FAILED_STDOUT_RELATIVE:
            require(
                details.st_ino == FAILED_STDOUT_INODE
                and details.st_dev == FAILED_ROOT_DEVICE
                and stat.S_IMODE(details.st_mode) == 0o600
                and details.st_size == FAILED_STDOUT_BYTES,
                "the exclusively preserved V1 collector stream identity changed",
            )
        elif relative == FAILED_PAIRED_RELATIVE:
            require(
                details.st_ino == FAILED_PAIRED_INODE
                and details.st_dev == FAILED_ROOT_DEVICE
                and stat.S_IMODE(details.st_mode) == 0o600
                and details.st_size == FAILED_PAIRED_BYTES,
                "the exclusively preserved V1 paired evidence identity changed",
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, 128 * 1024)
            if not chunk:
                break
            total += len(chunk)
            require(
                total <= MAX_OWNED_FILE_BYTES,
                "an authenticated first-party V2 component exceeded its bound",
            )
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def _load_authenticated_v1() -> tuple[types.ModuleType, dict[str, Any]]:
    _verify_runtime()
    source = _read_allowed(V1_SOURCE_RELATIVE)
    protocol = _read_allowed(V1_PROTOCOL_RELATIVE)
    manifest = _read_allowed(V1_MANIFEST_RELATIVE)
    failed_stdout = _read_allowed(FAILED_STDOUT_RELATIVE)
    failed_pairs = _read_allowed(FAILED_PAIRED_RELATIVE)
    require(
        hashlib.sha256(source).hexdigest() == V1_SOURCE_SHA256
        and hashlib.sha256(protocol).hexdigest() == V1_PROTOCOL_SHA256
        and hashlib.sha256(manifest).hexdigest() == V1_MANIFEST_SHA256
        and hashlib.sha256(failed_stdout).hexdigest() == FAILED_STDOUT_SHA256
        and hashlib.sha256(failed_pairs).hexdigest() == FAILED_PAIRED_SHA256,
        "frozen V1 first-party sources or preserved failure evidence changed",
    )
    module = types.ModuleType("rebar_authenticated_public_profile_v1")
    module.__file__ = str(ROOT / V1_SOURCE_RELATIVE)
    module.__package__ = None
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    require(
        module.ROOT == ROOT
        and module.PINNED_PYTHON == PINNED_PYTHON
        and module.MATRIX_SHA256
        == "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
        and module.PUBLIC_LABEL
        == "FRESH PUBLIC PRACTICE ONLY; NOT A HOLDOUT OR FINAL BENCHMARK",
        "the authenticated first-party V1 implementation identity changed",
    )
    return module, {
        "previous_source_sha256": V1_SOURCE_SHA256,
        "previous_protocol_sha256": V1_PROTOCOL_SHA256,
        "previous_manifest_sha256": V1_MANIFEST_SHA256,
        "failed_collector_stdout_sha256": FAILED_STDOUT_SHA256,
        "failed_paired_timing_sha256": FAILED_PAIRED_SHA256,
        "failed_root_device": FAILED_ROOT_DEVICE,
        "failed_root_inode": FAILED_ROOT_INODE,
    }


BASE, AUTHENTICATED_HISTORY = _load_authenticated_v1()
BASE.ROOT = ROOT
BASE.PINNED_PYTHON = PINNED_PYTHON
BASE.SOURCE_RELATIVE = SOURCE_RELATIVE
BASE.MANIFEST_RELATIVE = MANIFEST_RELATIVE
BASE.APPROVED_OUTPUT_PREFIX = APPROVED_OUTPUT_PREFIX
BASE.SCHEMA = SCHEMA
BASE.__file__ = str(ROOT / SOURCE_RELATIVE)


def _parse_collector_output(
    payload: bytes, engine: str,
) -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    require(engine in ("stdlib", "rust"), "an unknown collector engine is forbidden")
    require(
        type(payload) is bytes and 0 < len(payload) <= BASE.MAX_PROCESS_BYTES,
        "one bounded complete collector stream is mandatory",
    )
    require(
        payload.count(b"\n") == 2
        and b"\r" not in payload
        and b"\x00" not in payload
        and all(value < 128 for value in payload),
        "exactly one ASCII collector banner and canonical JSON are mandatory",
    )
    line, separator, document_payload = payload.partition(b"\n")
    require(separator == b"\n", "the sole collector banner was omitted")
    require(
        bool(line) and all(0x20 <= value <= 0x7E for value in line),
        "collector banners cannot contain control characters",
    )
    prefix = (
        b"Creating experiment directory " + engine.encode("ascii")
        + b".er (Process ID: "
    )
    suffix = b") ..."
    require(
        line.startswith(prefix) and line.endswith(suffix),
        "the collector engine, experiment path, or fixed ASCII banner changed",
    )
    digits = line[len(prefix): -len(suffix)]
    require(
        1 <= len(digits) <= 10
        and all(0x30 <= value <= 0x39 for value in digits)
        and digits[0] != 0x30,
        "the collector banner must contain one positive canonical decimal PID",
    )
    target_pid = int(digits.decode("ascii"))
    require(
        0 < target_pid <= MAX_TARGET_PID,
        "the collector target PID is outside its exact positive bound",
    )
    document = BASE.decode_document(
        document_payload,
        engine + " authenticated canonical profiled worker stdout",
    )
    require(
        type(document.get("pid")) is int and document["pid"] == target_pid,
        "the collector target PID does not match the canonical worker document",
    )
    return document, document_payload, {
        "engine": engine,
        "experiment": engine + ".er",
        "target_pid": target_pid,
        "banner_sha256": hashlib.sha256(line + b"\n").hexdigest(),
        "normalized_stdout_sha256": hashlib.sha256(document_payload).hexdigest(),
        "normalized_stdout_bytes": len(document_payload),
    }


def _preserved_failure_document() -> dict[str, Any]:
    failed_stdout = _read_allowed(FAILED_STDOUT_RELATIVE)
    failed_pairs = _read_allowed(FAILED_PAIRED_RELATIVE)
    document, normalized, banner = _parse_collector_output(
        failed_stdout, "stdlib",
    )
    pairs = BASE.decode_document(failed_pairs, "preserved V1 paired public rows")
    require(
        hashlib.sha256(normalized).hexdigest() == FAILED_NORMALIZED_SHA256
        and len(normalized) == FAILED_NORMALIZED_BYTES
        and banner["target_pid"] == FAILED_BANNER_PID
        and document.get("engine") == "stdlib"
        and document.get("status") == "PASS"
        and document.get("case_count") == 416
        and document.get("public_case_executions") == 1248
        and document.get("profile_passes") == 3
        and document.get("expected_records_sha256")
        == FAILED_EXPECTED_RECORDS_SHA256
        and document.get("holdout_files_read") == 0
        and document.get("archive_files_read") == 0
        and document.get("files_written") == 0
        and pairs.get("schema")
        == "rebar-rust-fresh-public-profile-v1-paired-timing-rows"
        and pairs.get("matrix_sha256") == BASE.MATRIX_SHA256
        and pairs.get("rows_sha256") == FAILED_PAIRED_ROWS_SHA256
        and type(pairs.get("rows")) is list
        and len(pairs["rows"]) == FAILED_PAIRED_ROWS
        and BASE.digest(pairs["rows"]) == FAILED_PAIRED_ROWS_SHA256,
        "the complete preserved V1 profile failure or paired evidence changed",
    )
    return {
        "directory": FAILED_ROOT_RELATIVE,
        "directory_device": FAILED_ROOT_DEVICE,
        "directory_inode": FAILED_ROOT_INODE,
        "directory_mode": "0700",
        "collector_stdout": FAILED_STDOUT_RELATIVE,
        "collector_stdout_sha256": FAILED_STDOUT_SHA256,
        "collector_stdout_bytes": FAILED_STDOUT_BYTES,
        "normalized_stdout_sha256": FAILED_NORMALIZED_SHA256,
        "normalized_stdout_bytes": FAILED_NORMALIZED_BYTES,
        "collector_target_pid": FAILED_BANNER_PID,
        "paired_timing": FAILED_PAIRED_RELATIVE,
        "paired_timing_sha256": FAILED_PAIRED_SHA256,
        "paired_timing_bytes": FAILED_PAIRED_BYTES,
        "paired_rows": FAILED_PAIRED_ROWS,
        "paired_rows_sha256": FAILED_PAIRED_ROWS_SHA256,
        "expected_records_sha256": FAILED_EXPECTED_RECORDS_SHA256,
    }


def _expected_previous_manifest() -> dict[str, str]:
    return {
        "source": V1_SOURCE_RELATIVE,
        "source_sha256": V1_SOURCE_SHA256,
        "protocol": V1_PROTOCOL_RELATIVE,
        "protocol_sha256": V1_PROTOCOL_SHA256,
        "manifest": V1_MANIFEST_RELATIVE,
        "manifest_sha256": V1_MANIFEST_SHA256,
    }


def verify_frozen_source() -> dict[str, Any]:
    _verify_runtime()
    source = _read_allowed(SOURCE_RELATIVE)
    protocol = _read_allowed(PROTOCOL_RELATIVE)
    manifest_payload = _read_allowed(MANIFEST_RELATIVE)
    manifest = BASE.decode_document(
        manifest_payload,
        "frozen first-party V2 public profile source manifest",
        canonical_required=False,
    )
    matrix = BASE.build_public_matrix()
    BASE.validate_public_matrix(matrix)
    source_sha256 = hashlib.sha256(source).hexdigest()
    protocol_sha256 = hashlib.sha256(protocol).hexdigest()
    failure = _preserved_failure_document()
    expected = {
        "schema": SCHEMA + "-source-freeze",
        "source": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha256,
        "previous": _expected_previous_manifest(),
        "preserved_failure": failure,
        "published_seed": BASE.PUBLISHED_SEED,
        "matrix_sha256": BASE.MATRIX_SHA256,
        "dataset_count": 16,
        "case_count": len(matrix),
        "operation_count": len(BASE.OPERATIONS),
        "pinned_python": str(PINNED_PYTHON),
        "pinned_cpython": "3.14.6",
        "approved_output_prefix": APPROVED_OUTPUT_PREFIX,
        "profiler": {
            "command": str(BASE.GPROFNG),
            "binaries": BASE._expected_profiler_manifest(),
            "archive_policy": "off",
            "descendant_policy": "off",
            "heap_tracing": "on",
            "clock_sampling": "hi",
        },
        "profile_configuration": {
            "paired_rounds": BASE.DEFAULT_PAIRED_ROUNDS,
            "batch_iterations": BASE.DEFAULT_BATCH_ITERATIONS,
            "warmup_iterations": BASE.DEFAULT_WARMUP_ITERATIONS,
            "profile_passes": BASE.DEFAULT_PROFILE_PASSES,
            "reports": sorted(BASE.PROFILE_REPORTS),
        },
        "collector_output_policy": {
            "ascii_banner_count": 1,
            "canonical_json_document_count": 1,
            "banner_engine_matches_expected_engine": True,
            "banner_experiment_matches_expected_engine": True,
            "banner_positive_decimal_pid_matches_worker_pid": True,
            "preserve_complete_raw_stdout": True,
            "preserve_separate_canonical_worker_json": True,
            "forbid_extra_output_control_bytes_and_trailing_data": True,
        },
        "provenance": {
            "data": "fresh embedded public literals only",
            "candidate_imports_in_source_modes": 0,
            "fixture_files_read": 0,
            "holdout_files_read": 0,
            "archive_files_read": 0,
            "source_mode_clock_samples": 0,
            "source_mode_workspace_mutations": 0,
            "preserved_public_failed_runs_mutated": 0,
        },
    }
    require(
        manifest == expected,
        "the exact V2 source, protocol, history, or public manifest changed",
    )
    return {
        "schema": SCHEMA + "-source-verification",
        "status": "PASS",
        "label": BASE.PUBLIC_LABEL,
        "source": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "published_seed": BASE.PUBLISHED_SEED,
        "matrix_sha256": BASE.MATRIX_SHA256,
        "case_count": len(matrix),
        "operation_count": len(BASE.OPERATIONS),
        "authenticated_previous": _expected_previous_manifest(),
        "authenticated_failure": failure,
        "candidate_import_count": 0,
        "processes_started": 0,
        "clock_samples": 0,
        "profiler_runs": 0,
        "workspace_mutations": 0,
        "files_written": 0,
        "fixture_files_read": 0,
        "holdout_files_read": 0,
        "archive_files_read": 0,
    }


def _approved_session_parts(value: Any) -> tuple[str, ...]:
    require(
        type(value) is str and bool(value)
        and "\x00" not in value and "\\" not in value,
        "exactly one approved V2 public-profile summary path is mandatory",
    )
    if os.path.isabs(value):
        prefix = str(ROOT) + "/"
        require(
            value.startswith(prefix),
            "a V2 public-profile path outside the owned workspace is forbidden",
        )
        relative = value[len(prefix):]
    else:
        relative = value
    path = PurePosixPath(relative)
    require(
        not path.is_absolute()
        and path.as_posix() == relative
        and len(path.parts) == 4
        and path.parts[:2] == ("experiments", "rust_public_profile_v2")
        and path.parts[-1] == "summary.json",
        "use exactly experiments/rust_public_profile_v2/<session>/summary.json",
    )
    session = path.parts[2]
    require(
        1 <= len(session) <= 80
        and session[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(
            character in "abcdefghijklmnopqrstuvwxyz0123456789-"
            for character in session
        )
        and not any(token in session for token in BASE.FORBIDDEN_OUTPUT_TOKENS),
        "the V2 public-profile session has a hostile or unapproved component",
    )
    return path.parts


def _profile_engine(
    workspace: Any, engine: str, request: dict[str, Any],
) -> dict[str, Any]:
    role = "public-profile-" + engine
    command = BASE._collector_command(engine)
    code, stdout, stderr, collector_pid = BASE._run_process(
        command,
        payload=BASE.canonical(request),
        cwd=workspace.proc_path,
        descriptor=workspace.directory,
        timed=True,
    )
    artifacts = [
        workspace.write(engine + ".collector.stdout.raw.txt", stdout),
        workspace.write(engine + ".collector.stderr.txt", stderr),
    ]
    BASE.require(
        code == 0,
        "gprofng CPU/heap collection failed for " + engine + ": "
        + stderr[-2_000:].decode("utf-8", "replace"),
    )
    document, normalized, banner = _parse_collector_output(stdout, engine)
    artifacts.append(workspace.write(engine + ".collector.stdout.json", normalized))
    BASE._validate_worker(
        document,
        role=role,
        engine=engine,
        mode="profile",
        pid=banner["target_pid"],
    )
    BASE.require(
        document.get("expected_records_sha256")
        == request["expected_records_sha256"]
        and document.get("profile_passes") == request["profile_passes"]
        and document.get("public_case_executions")
        == 16 * len(BASE.OPERATIONS) * request["profile_passes"]
        and type(document.get("python_heap")) is dict,
        "the complete correctness-gated native profile worker was forged",
    )
    BASE.require(
        type(workspace.directory) is int,
        "the approved V2 profiler directory descriptor was lost",
    )
    experiment = os.open(
        engine + ".er",
        BASE._directory_open_flags(),
        dir_fd=workspace.directory,
    )
    try:
        BASE.require(
            stat.S_ISDIR(os.fstat(experiment).st_mode),
            "the approved native profiler experiment is not a real directory",
        )
    finally:
        os.close(experiment)
    reports: dict[str, bytes] = {}
    for kind, option in BASE.PROFILE_REPORTS.items():
        report_command = [
            str(BASE.GPROFNG), "display", "text", option, engine + ".er",
        ]
        report_code, report, diagnostics, _ = BASE._run_process(
            report_command,
            payload=None,
            cwd=workspace.proc_path,
            descriptor=workspace.directory,
            timed=True,
        )
        artifacts.append(workspace.write(engine + "." + kind + ".txt", report))
        artifacts.append(workspace.write(
            engine + "." + kind + ".stderr.txt", diagnostics,
        ))
        BASE.require(
            report_code == 0 and bool(report.strip()),
            "gprofng " + kind + " evidence failed for " + engine + ": "
            + diagnostics[-2_000:].decode("utf-8", "replace"),
        )
        reports[kind] = report
    return {
        "engine": engine,
        "collector_pid": collector_pid,
        "target_pid": document["pid"],
        "authenticated_collector_banner": banner,
        "experiment": workspace.relative_directory + "/" + engine + ".er",
        "archive_collection": "DISABLED (-a off)",
        "descendant_collection": "DISABLED (-F off)",
        "native_heap_tracing": "ENABLED (-H on)",
        "cpu_sampling": "ENABLED (-p hi)",
        "correctness_checks": document["public_case_executions"],
        "cohort_execution_counts": document["executions_by_cohort"],
        "python_heap": document["python_heap"],
        "native_ffi": BASE._profile_report_markers(reports),
        "engine_provenance": document["engine_provenance"],
        "artifacts": artifacts,
    }


def source_self_test() -> dict[str, Any]:
    verification = verify_frozen_source()
    matrix = BASE.build_public_matrix()
    BASE.validate_public_matrix(matrix)
    for case in matrix:
        for field in ("pattern", "subject", "replacement", "scanner_phrase"):
            require(
                BASE.encode_typed(BASE.decode_typed(case[field])) == case[field],
                "a fresh V2 public carrier failed an exact source-only round trip",
            )
    approved = _approved_session_parts(
        "experiments/rust_public_profile_v2/public-run-001/summary.json",
    )
    require(
        approved
        == (
            "experiments", "rust_public_profile_v2",
            "public-run-001", "summary.json",
        ),
        "the exact fresh V2 public output layout changed",
    )
    hostile_paths = (
        "/tmp/public-profile-escape/summary.json",
        "../experiments/rust_public_profile_v2/public-run/summary.json",
        "experiments/rust_public_profile_v1/public-run-001/summary.json",
        "experiments/rust_public_profile_v2/../escape/summary.json",
        "experiments/rust_public_profile_v2/public-run/../summary.json",
        "experiments/rust_public_profile_v2/public-run//summary.json",
        "experiments/rust_public_profile_v2/public-run/report.json",
        "experiments/rust_public_profile_v2/.public/summary.json",
        "experiments/rust_public_profile_v2/PUBLIC/summary.json",
        "experiments/rust_public_profile_v2/hidden-run/summary.json",
        "experiments/rust_public_profile_v2/legacy-run/summary.json",
        "experiments/rust_public_profile_v2/final-run/summary.json",
        "experiments/rust_public_profile_v2/fixture-run/summary.json",
        "experiments/rust_public_profile_v2/holdout-run/summary.json",
        "experiments/rust_public_profile_v2/archive-run/summary.json",
        "experiments/rust_public_profile_v2/public\\run/summary.json",
        "experiments/rust_public_profile_v2/public\x00run/summary.json",
    )
    rejected_paths = 0
    for value in hostile_paths:
        try:
            _approved_session_parts(value)
        except PublicProfileSuccessorError:
            rejected_paths += 1
        else:
            raise PublicProfileSuccessorError("a hostile V2 output path was accepted")
    for value in ("../rust.er", "/tmp/rust.er", ".rust", "hidden.txt"):
        try:
            BASE._approved_artifact_name(value)
        except BASE.PublicProfileError:
            rejected_paths += 1
        else:
            raise PublicProfileSuccessorError(
                "a hostile V2 profile artifact name was accepted",
            )
    actual_stream = _read_allowed(FAILED_STDOUT_RELATIVE)
    actual, normalized, banner = _parse_collector_output(actual_stream, "stdlib")
    require(
        banner["target_pid"] == FAILED_BANNER_PID
        and hashlib.sha256(normalized).hexdigest() == FAILED_NORMALIZED_SHA256
        and actual.get("engine") == "stdlib",
        "the frozen real collector failure is not exactly reproducible",
    )
    good_document = canonical({"engine": "stdlib", "pid": 91, "status": "PASS"})
    good_line = b"Creating experiment directory stdlib.er (Process ID: 91) ..."
    good_payload = good_line + b"\n" + good_document
    result, result_payload, result_banner = _parse_collector_output(
        good_payload, "stdlib",
    )
    require(
        result.get("engine") == "stdlib"
        and result_payload == good_document
        and result_banner["target_pid"] == 91,
        "a clean exact collector banner was rejected",
    )
    rust_document = canonical({"engine": "rust", "pid": 227, "status": "PASS"})
    rust_payload = (
        b"Creating experiment directory rust.er (Process ID: 227) ...\n"
        + rust_document
    )
    rust_result, rust_normalized, rust_banner = _parse_collector_output(
        rust_payload, "rust",
    )
    require(
        rust_result.get("engine") == "rust"
        and rust_normalized == rust_document
        and rust_banner["target_pid"] == 227,
        "the exact independent Rust collector banner was rejected",
    )
    hostile_streams: list[tuple[bytes, str]] = [
        (b"", "stdlib"),
        (good_document, "stdlib"),
        (good_payload, "rust"),
        (good_payload.replace(b"stdlib.er", b"rust.er"), "stdlib"),
        (good_payload.replace(b"stdlib.er", b"../stdlib.er"), "stdlib"),
        (good_payload.replace(b"stdlib.er", b"/tmp/stdlib.er"), "stdlib"),
        (good_payload.replace(b"Creating", b"creating"), "stdlib"),
        (good_payload.replace(b"directory ", b"directory  "), "stdlib"),
        (good_payload.replace(b"Process ID: ", b"Process ID:"), "stdlib"),
        (good_payload.replace(b"91) ...", b"0) ..."), "stdlib"),
        (good_payload.replace(b"91) ...", b"-91) ..."), "stdlib"),
        (good_payload.replace(b"91) ...", b"+91) ..."), "stdlib"),
        (good_payload.replace(b"91) ...", b"091) ..."), "stdlib"),
        (good_payload.replace(b"91) ...", b"91.0) ..."), "stdlib"),
        (good_payload.replace(b"91) ...", b"2147483648) ..."), "stdlib"),
        (good_payload.replace(b"91) ...", b"99999999999) ..."), "stdlib"),
        (good_payload.replace(b"91) ...", b"92) ..."), "stdlib"),
        (good_payload.replace(b"91) ...", b"91) ...."), "stdlib"),
        (good_payload.replace(b" ...\n", b" ...\r\n"), "stdlib"),
        (good_payload + b"\n", "stdlib"),
        (good_payload + b"trailing", "stdlib"),
        (b"noise\n" + good_payload, "stdlib"),
        (good_line + b"\n" + good_line + b"\n" + good_document, "stdlib"),
        (good_line + b"\n" + b" " + good_document, "stdlib"),
        (good_line + b"\n" + good_document[:-1] + b" \n", "stdlib"),
        (good_line + b"\n" + b"[]\n", "stdlib"),
        (good_line + b"\n" + b"null\n", "stdlib"),
        (good_line + b"\n" + b"{\"pid\":91,\"pid\":91}\n", "stdlib"),
        (good_line + b"\n" + b"{\"pid\":NaN}\n", "stdlib"),
        (good_line + b"\n" + b"{\"pid\":Infinity}\n", "stdlib"),
        (good_line + b"\n" + canonical({"pid": True}), "stdlib"),
        (good_line + b"\n" + canonical({"pid": "91"}), "stdlib"),
        (good_line + b"\n" + canonical({"pid": 92}), "stdlib"),
        (good_line + b"\n" + good_document.replace(b"PASS", b"P\xffSS"), "stdlib"),
    ]
    for value in range(1, 256):
        hostile_streams.append((
            good_line[:-5] + bytes((value,)) + good_line[-5:]
            + b"\n" + good_document,
            "stdlib",
        ))
    for index in range(len(good_line)):
        hostile_streams.append((
            good_line[:index] + bytes((good_line[index] ^ 1,))
            + good_line[index + 1:] + b"\n" + good_document,
            "stdlib",
        ))
    rejected_streams = 0
    for payload, engine in hostile_streams:
        try:
            _parse_collector_output(payload, engine)
        except (PublicProfileSuccessorError, BASE.PublicProfileError):
            rejected_streams += 1
        else:
            raise PublicProfileSuccessorError(
                "a hostile or ambiguous collector banner/JSON stream was accepted",
            )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "a candidate escaped into the strictly source-only V2 self-test",
    )
    verification.update({
        "schema": SCHEMA + "-source-self-test",
        "dataset_count": 16,
        "text_case_count": 8 * len(BASE.OPERATIONS),
        "bytes_case_count": 8 * len(BASE.OPERATIONS),
        "rejected_hostile_output_count": rejected_paths,
        "rejected_hostile_collector_stream_count": rejected_streams,
        "authenticated_real_v1_collector_failure": True,
        "approved_profiler_report_kinds": sorted(BASE.PROFILE_REPORTS),
        "candidate_owned_reference_import_policy": "DENY",
        "harness_warning_and_inspection_import_policy": "ALLOW",
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    })
    return verification


BASE.verify_frozen_source = verify_frozen_source
BASE._approved_session_parts = _approved_session_parts
BASE._profile_engine = _profile_engine
BASE.source_self_test = source_self_test


if __name__ == "__main__":
    try:
        raise SystemExit(BASE.main())
    except (PublicProfileSuccessorError, BASE.PublicProfileError, OSError) as error:
        print("fresh public profile V2 failed closed: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
