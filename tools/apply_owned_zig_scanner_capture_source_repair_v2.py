#!/usr/bin/env python3
"""Freeze the evidence-backed correction to one first-party Zig scanner block."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import importlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SCHEMA = "rebar-phase2-owned-zig-scanner-capture-source-repair-v2"
SOURCE_PATH = "tools/apply_owned_zig_scanner_capture_source_repair_v2.py"
PROTOCOL_PATH = "oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V2.md"
CONTRACT_PATH = "oracle/phase2/zig-scanner-capture-source-repair-v2.json"
MAX_OWNER_BYTES = 8 * 1024 * 1024
PRIVATE_ROOT_PREFIX = "rebar-phase2-zig-scanner-capture-source-build-v2-"
ORIGINAL_PATH = "candidates/zig/py_bridge.c"
ORIGINAL_SHA256 = "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
ORIGINAL_BYTES = 173026
ENGINE_PATH = "candidates/zig/mini_regex.zig"
ENGINE_SHA256 = "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"
ENGINE_BYTES = 186915
ADAPTER_PATH = "candidates/zig_candidate.py"
ADAPTER_SHA256 = "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862"
ADAPTER_BYTES = 68422
DEFECTIVE_SHA256 = "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148"
DEFECTIVE_BYTES = 173082
CORRECTED_SHA256 = ORIGINAL_SHA256
CORRECTED_BYTES = ORIGINAL_BYTES
V1_SCHEMA = "rebar-phase2-owned-zig-scanner-capture-source-repair-v1"
ZIG_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-"
    "original-p0-failures-publication-receipt.json"
)
RUST_BUILD_ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz"
)
RUST_BUILD_ARCHIVE_SHA256 = (
    "840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d"
)
RUST_BUILD_ARCHIVE_BYTES = 108325
RUST_BUILD_ARCHIVE_DEVICE = 2064
RUST_BUILD_ARCHIVE_INODE = 524643
RUST_BUILD_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v12-rust-phase2-v12-rust-flag-original-p0-"
    "publication-receipt.json"
)
RUST_BUILD_RECEIPT_SHA256 = (
    "1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f"
)
RUST_BUILD_RECEIPT_BYTES = 2109
CASE_ID = "rust-public-practice.v1.0031"
SUITE_IDS = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)
SUPPORT = {
    "GOAL.md": "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    "oracle/phase1/p0-completeness-v1.json": "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    "oracle/phase1/P0-COMPLETENESS-V1.md": "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
    "tools/verify_p0_completeness_v1.py": "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
    "tools/render_candidate_current_overview_v30.py": "a8c2bb2e0ccfab0b76b5387437fe48279e01ca1034739a67967f543f1930c507",
    "docs/evidence/candidate-current-overview-v30.inputs.json": "ea2ea381a22a9a23344ff40505d975aba8d25704d2ad90e03b58018fda44ca0f",
    "docs/evidence/candidate-current-overview-v30.json": "b04db4e93dc74bb9200c13133c0a33bd33961b5f35e5810e74de65b29fcab534",
    "docs/evidence/candidate-current-overview-v30.svg": "a3dbbb69c5140d15588463e0e3579d5bea5d95587f1abf444b6679cd3361d4c6",
    "tools/run_owned_six_family_original_p0_producer_v3.py": "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
    "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md": "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
    "oracle/phase2/six-family-p0-producer-v3.json": "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
    "toolchains/zig-0.16.0.lock.json": "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
    "tools/apply_owned_zig_scanner_capture_source_repair_v1.py": "963f306373753b9fef84c9a9784668f42067cb905b84347a0bcc99e1e8692515",
    "oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md": "7a40b58bcc69744fc6b749368ec307be7d05d742de3d921410fd2753a4f5c8d0",
    "oracle/phase2/zig-scanner-capture-source-repair-v1.json": "c48fcd9cb40cbe15442c2dd197627d7f4ccc341b3edfbbe0c645405015c8ea87",
    "oracle/phase2/repaired-zig-original-campaign-v2.json": "0112748e8dbca769625ea2643643fad81ced069e20ed87a458bebe0a922d2851",
    ZIG_RECEIPT: "40dd3afa5f99dc51b30af48fe407ece84337a2a41fb3536b214845d0dda00fba",
    RUST_BUILD_ARCHIVE: RUST_BUILD_ARCHIVE_SHA256,
    RUST_BUILD_RECEIPT: RUST_BUILD_RECEIPT_SHA256,
}

FUNCTION_ANCHOR = b"static int zig_scanner_project_match("
NEXT_FUNCTION_ANCHOR = b"static ZigMatch *zig_iterator_record("
LOCAL_PROJECTION = b"""    for (size_t logical = 1; logical <= iterator->groups; logical++) {
        if (logical > iterator->native_groups - outer) break;
        size_t actual = outer + logical;
        if (actual >= next_outer) break;
        if (begins[actual] < 0) continue;
        if (ends[actual] < begins[actual]) {
            PyErr_SetString(PyExc_RuntimeError,
                            "invalid owned Zig scanner local capture");
            return 0;
        }
        match->spans[logical] = begins[actual];
        match->spans[exposed_stride + logical] = ends[actual];
    }
"""
CORRECT_BLOCK = b"""    size_t branch_group = active + 1;
    match->spans[branch_group] = begins[0];
    match->spans[exposed_stride + branch_group] = ends[0];
    match->lastindex = (Py_ssize_t)branch_group;
"""
DEFECTIVE_BLOCK = b"""    size_t branch_group = active + 1;
    if (match->spans[branch_group] < 0) {
        match->spans[branch_group] = begins[0];
        match->spans[exposed_stride + branch_group] = ends[0];
    }
    match->lastindex = (Py_ssize_t)branch_group;
"""
CORRECT_BLOCK_SHA256 = "42009e889c83ee06194f14223b629bb221326ce7a3ebf3efe09f5d1a76344978"
DEFECTIVE_BLOCK_SHA256 = "7a7fa3a9a16d9dae07e74845984bbd36d17309c1f06ddb091d6d3986b4e27177"


class GateError(Exception):
    """A frozen, source-only Zig scanner-capture obligation was not met."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise GateError(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError) as error:
        raise GateError("require one finite canonical source-freeze document") from error


def valid_digest(value: object, label: str) -> str:
    require(isinstance(value, str) and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            f"invalid {label} SHA-256")
    return value


def relative_parts(value: object, *, allow_build_archive: bool = False) -> tuple[str, ...]:
    require(isinstance(allow_build_archive, bool),
            "reject an invalid frozen compressed-build access policy")
    require(isinstance(value, str) and 0 < len(value) <= 512,
            "require a bounded, canonical relative source owner")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value
            and 0 < len(parsed.parts) <= 12
            and all(part not in ("", ".", "..") for part in parsed.parts)
            and not value.endswith((".so", ".dylib", ".dll"))
            and (not value.endswith(".gz")
                 or (allow_build_archive and value == RUST_BUILD_ARCHIVE))
            and (not allow_build_archive or value == RUST_BUILD_ARCHIVE)
            and "holdout" not in value.casefold()
            and "benchmark" not in value.casefold(),
            "reject archives, native binaries, hidden cases, or unsafe source owners")
    return parsed.parts


def checked_read(relative: str, expected: str,
                 expected_bytes: int | None = None,
                 *, allow_build_archive: bool = False) -> bytes:
    parts = relative_parts(relative, allow_build_archive=allow_build_archive)
    valid_digest(expected, relative)
    if allow_build_archive:
        require(relative == RUST_BUILD_ARCHIVE
                and expected == RUST_BUILD_ARCHIVE_SHA256
                and expected_bytes == RUST_BUILD_ARCHIVE_BYTES,
                "permit raw bytes only from the sole pinned Rust build archive")
    require(expected_bytes is None
            or (isinstance(expected_bytes, int)
                and 0 <= expected_bytes <= MAX_OWNER_BYTES),
            "reject an invalid or excessive authenticated owner size")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and 0 <= before.st_size <= MAX_OWNER_BYTES
                    and (expected_bytes is None or before.st_size == expected_bytes)
                    and (not allow_build_archive
                         or (before.st_dev == RUST_BUILD_ARCHIVE_DEVICE
                             and before.st_ino == RUST_BUILD_ARCHIVE_INODE
                             and before.st_uid == os.geteuid()
                             and before.st_nlink == 1
                             and stat.S_IMODE(before.st_mode) == 0o600)),
                    "reject a nonregular, excessive, or incorrectly sized owner")
            chunks: list[bytes] = []
            total = 0
            while True:
                piece = os.read(descriptor, min(1024 * 1024,
                                                MAX_OWNER_BYTES + 1 - total))
                if not piece:
                    break
                total += len(piece)
                require(total <= MAX_OWNER_BYTES,
                        "the authenticated source owner exceeds its hard bound")
                chunks.append(piece)
            after = os.fstat(descriptor)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns),
                    "the authenticated source owner changed during its read")
            raw = b"".join(chunks)
            require(len(raw) == before.st_size and sha256(raw) == expected,
                    f"the authenticated source owner changed: {relative}")
            if allow_build_archive:
                require(raw[:3] == b"\x1f\x8b\x08"
                        and len(raw) == RUST_BUILD_ARCHIVE_BYTES
                        and int.from_bytes(raw[-4:], "little") == 757826,
                        "authenticate only compressed Rust build bytes, never inflate")
            return raw
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def strict_json(raw: bytes, label: str, *, require_canonical: bool = False) -> dict:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        value: dict[str, object] = {}
        for key, item in pairs:
            require(key not in value, f"duplicate JSON key in {label}")
            value[key] = item
        return value

    def reject_constant(_value: str) -> object:
        raise GateError(f"nonfinite JSON number in {label}")

    try:
        value = json.loads(raw.decode("utf-8", "strict"),
                           object_pairs_hook=unique,
                           parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise GateError(f"invalid authenticated JSON: {label}") from error
    require(isinstance(value, dict),
            f"require an exact JSON object: {label}")
    if require_canonical:
        require(canonical(value) == raw,
                f"require an exact canonical JSON object: {label}")
    return value


def anchored_block(source: bytes, block: bytes, other: bytes) -> int:
    require(source.count(FUNCTION_ANCHOR) == 1
            and source.count(NEXT_FUNCTION_ANCHOR) == 1
            and source.count(block) == 1 and source.count(other) == 0,
            "require one unambiguous, unmodified scanner projection block")
    start = source.index(FUNCTION_ANCHOR)
    finish = source.index(NEXT_FUNCTION_ANCHOR, start + len(FUNCTION_ANCHOR))
    position = source.index(block)
    require(start < position < finish,
            "reject a scanner correction outside its owned function")
    function = source[start:finish]
    require(function.count(LOCAL_PROJECTION) == 1
            and function.index(LOCAL_PROJECTION) < function.index(block)
            and function.count(b"match->lastindex = (Py_ssize_t)branch_group;") == 1,
            "preserve the nested-capture projection and the branch lastindex")
    return position


def historical_source(original: bytes, original_digest: str,
                      original_size: int, *, frozen: bool = True) -> bytes:
    require(isinstance(original, bytes) and len(original) == original_size
            and sha256(original) == original_digest,
            "reject an altered original first-party Zig bridge")
    require(len(CORRECT_BLOCK) == 190
            and sha256(CORRECT_BLOCK) == CORRECT_BLOCK_SHA256
            and len(DEFECTIVE_BLOCK) == 246
            and sha256(DEFECTIVE_BLOCK) == DEFECTIVE_BLOCK_SHA256,
            "the two exact scanner branch blocks changed")
    position = anchored_block(original, CORRECT_BLOCK, DEFECTIVE_BLOCK)
    result = (original[:position] + DEFECTIVE_BLOCK
              + original[position + len(CORRECT_BLOCK):])
    require(anchored_block(result, DEFECTIVE_BLOCK, CORRECT_BLOCK) == position,
            "the historical conditional block is not uniquely reconstructed")
    if frozen:
        require(original_digest == ORIGINAL_SHA256
                and original_size == ORIGINAL_BYTES
                and len(result) == DEFECTIVE_BYTES
                and sha256(result) == DEFECTIVE_SHA256,
                "reject any invented or substituted historical V1 bridge")
    return result


def repaired_source(defective: bytes, defective_digest: str,
                    defective_size: int, *, frozen: bool = True) -> bytes:
    require(isinstance(defective, bytes) and len(defective) == defective_size
            and sha256(defective) == defective_digest,
            "reject an altered historical conditional Zig bridge")
    require(len(CORRECT_BLOCK) == 190
            and sha256(CORRECT_BLOCK) == CORRECT_BLOCK_SHA256
            and len(DEFECTIVE_BLOCK) == 246
            and sha256(DEFECTIVE_BLOCK) == DEFECTIVE_BLOCK_SHA256,
            "the exact corrective scanner-block fingerprints changed")
    position = anchored_block(defective, DEFECTIVE_BLOCK, CORRECT_BLOCK)
    result = (defective[:position] + CORRECT_BLOCK
              + defective[position + len(DEFECTIVE_BLOCK):])
    require(anchored_block(result, CORRECT_BLOCK, DEFECTIVE_BLOCK) == position
            and result[:position] == defective[:position]
            and result[position + len(CORRECT_BLOCK):]
            == defective[position + len(DEFECTIVE_BLOCK):],
            "reject any change outside the sole historical scanner block")
    for marker in (
        b"PyObject_GetBuffer(", b"PyBuffer_Release(", b"PyBUF_SIMPLE",
        b"PyCallable_Check(", b"zig_prepare_expand_template(",
        b"zig_match_expand(", b"zig_live_exporter_subn(",
        b"bridge_generic_subn(", b"PyImport_ImportModule",
        b"import re", b"from re ", b"import _sre", b"dlopen(",
        b"pcre", b"oniguruma", b"hyperscan", b"candidates.rust",
        b"candidates.vm_candidate", b"candidates.cpp", b"candidates.go",
        b"candidates.fortran",
    ):
        require(defective.count(marker) == result.count(marker),
                "reject changed matching ownership, buffers, or regex delegation")
    if frozen:
        require(defective_digest == DEFECTIVE_SHA256
                and defective_size == DEFECTIVE_BYTES
                and len(result) == CORRECTED_BYTES
                and sha256(result) == CORRECTED_SHA256,
                "the corrected scanner must reproduce the exact canonical bridge")
    return result


def project_witness(*, conditional: bool, active: int,
                    local_spans: tuple[tuple[int, int], ...],
                    whole: tuple[int, int]) -> tuple[tuple[tuple[int, int], ...], int]:
    require(isinstance(conditional, bool) and isinstance(active, int)
            and active >= 0 and isinstance(local_spans, tuple)
            and len(local_spans) > active
            and isinstance(whole, tuple) and len(whole) == 2
            and all(isinstance(part, int) for part in whole)
            and 0 <= whole[0] <= whole[1],
            "reject an invalid synthetic scanner capture")
    for item in local_spans:
        require(isinstance(item, tuple) and len(item) == 2
                and all(isinstance(part, int) for part in item)
                and ((item[0] == -1 and item[1] == -1)
                     or (0 <= item[0] <= item[1] <= whole[1])),
                "reject a forged synthetic nested-capture span")
    spans = [whole, *local_spans]
    branch_group = active + 1
    if not conditional or spans[branch_group][0] < 0:
        spans[branch_group] = whole
    return tuple(spans), branch_group


class SourceOnlyBoundary:
    """Make all real source, process, import, archive, and clock probes fail."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, owner: object, name: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GateError(f"source-only Zig V2 boundary: {name}")

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyBoundary:
        groups = (
            (builtins, ("open",)),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "remove", "unlink", "replace", "rename",
                  "system", "fork", "posix_spawn", "fsync")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "mkdir", "unlink", "rename", "replace",
                    "stat", "lstat", "resolve")),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (threading.Thread, ("start",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (importlib, ("import_module",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "thread_time", "sleep")),
        )
        for owner, names in groups:
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: object, _value: object,
                 _traceback: object) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def private_parts(value: object) -> tuple[str, ...]:
    require(isinstance(value, str) and 0 < len(value) <= 512,
            "require a bounded, absolute private Zig source snapshot")
    parsed = PurePosixPath(value)
    require(parsed.is_absolute() and str(parsed) == value,
            "reject a noncanonical or relative private source snapshot")
    parts = parsed.parts
    require(len(parts) == 5 and parts[1] == "tmp"
            and parts[2].startswith(PRIVATE_ROOT_PREFIX)
            and len(parts[2]) > len(PRIVATE_ROOT_PREFIX)
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in parts[2])
            and parts[3] in ("reference-a", "reference-b")
            and parts[4] == "source",
            "reject workspace, cross-family, linked, or reused private phase roots")
    return parts


def discover_evidence(value: object, output: dict[str, str]) -> None:
    if isinstance(value, dict):
        path = value.get("path")
        digest = value.get("sha256")
        if (isinstance(path, str) and isinstance(digest, str)
                and path.startswith(("oracle/phase2/evidence/",
                                     "experiments/rust_public_practice_v1/"))):
            valid_digest(digest, "digest-addressed evidence reference")
            require(isinstance(PurePosixPath(path), PurePosixPath)
                    and not PurePosixPath(path).is_absolute()
                    and str(PurePosixPath(path)) == path
                    and ".." not in PurePosixPath(path).parts,
                    "reject an escaping authenticated historical evidence reference")
            require(path not in output or output[path] == digest,
                    "reject conflicting hashes for one historical evidence owner")
            output[path] = digest
        for item in value.values():
            discover_evidence(item, output)
    elif isinstance(value, list):
        for item in value:
            discover_evidence(item, output)


def load_history(inputs: dict, summary: dict) -> dict[str, str]:
    evidence: dict[str, str] = {}
    current_inputs, current_summary = inputs, summary
    for version in range(30, 18, -1):
        require(current_inputs.get("schema")
                == f"rebar-candidate-current-overview-v{version}-inputs"
                and current_summary.get("schema")
                == f"rebar-candidate-current-overview-v{version}-summary"
                and current_summary.get("status") == "PASS",
                "reject a substituted or missing committed historical overview")
        discover_evidence(current_inputs, evidence)
        discover_evidence(current_summary, evidence)
        if version == 19:
            break
        previous = current_inputs.get("previous_overview")
        require(isinstance(previous, dict),
                "require the digest-addressed previous-overview chain")
        loaded: dict[str, dict] = {}
        for role, suffix in (("inputs", ".inputs.json"),
                             ("summary", ".json")):
            owner = previous.get(role)
            path = f"docs/evidence/candidate-current-overview-v{version - 1}{suffix}"
            require(isinstance(owner, dict) and owner.get("path") == path,
                    "reject an invented or skipped historical overview owner")
            expected = valid_digest(owner.get("sha256"), path)
            size = owner.get("bytes")
            require(size is None or isinstance(size, int),
                    "reject an invalid historical overview owner size")
            loaded[role] = strict_json(checked_read(path, expected, size), path)
        current_inputs, current_summary = loaded["inputs"], loaded["summary"]
    require(len(evidence) == 154
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in evidence) == 124
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in evidence) == 30,
            "retain exactly 154 historical references without opening an archive")
    return evidence


def validate_rust_build_receipt(receipt: dict) -> None:
    require(isinstance(receipt, dict)
            and receipt.get("schema")
            == "rebar-phase2-owned-rust-flag-source-build-v12-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == "rust"
            and receipt.get("label") == "phase2-v12-rust-flag-original-p0"
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("candidate_qualified") is False
            and receipt.get("historical_evidence_owner_count") == 149
            and receipt.get("historical_authenticated_reference_count") == 154
            and receipt.get("new_actual_evidence_owner_count") == 2
            and receipt.get("repository_evidence_owner_count_after_publication") == 151
            and receipt.get("authenticated_history_reference_count_after_publication") == 156
            and receipt.get("archive_relative") == RUST_BUILD_ARCHIVE
            and receipt.get("archive_sha256") == RUST_BUILD_ARCHIVE_SHA256
            and receipt.get("archive_bytes") == RUST_BUILD_ARCHIVE_BYTES
            and receipt.get("uncompressed_bytes") == 757826
            and receipt.get("uncompressed_sha256")
            == "a69fe5a873891c3aee51cf8e711877125b06c079057b04daeb86720bbd2dc75f"
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("expected_actual_compiler_process_count") == 28
            and receipt.get("corrected_public_overlay_apply_count") == 2
            and receipt.get("bridge_overlay_apply_count") == 2
            and receipt.get("public_derived_sha256")
            == "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
            and receipt.get("bridge_derived_sha256")
            == "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257",
            "derive 151 current owners and 156 references only from the real Rust build")
    publication = receipt.get("archive_publication")
    require(isinstance(publication, dict)
            and publication.get("path") == str(ROOT / RUST_BUILD_ARCHIVE)
            and publication.get("sha256") == RUST_BUILD_ARCHIVE_SHA256
            and publication.get("bytes") == RUST_BUILD_ARCHIVE_BYTES
            and publication.get("device") == RUST_BUILD_ARCHIVE_DEVICE
            and publication.get("inode") == RUST_BUILD_ARCHIVE_INODE
            and publication.get("exclusive_creation") is True
            and publication.get("file_fsync_completed") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("write_calls") == 1,
            "bind the exact distinct published Rust compressed-build inode")
    directory = receipt.get("archive_directory_fsync")
    require(isinstance(directory, dict)
            and directory.get("completed") is True
            and directory.get("device") == RUST_BUILD_ARCHIVE_DEVICE,
            "preserve genuine durable publication of the Rust build archive")
    require(receipt.get("candidate_imports") == 0
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("winner_selected") is False,
            "a Rust source-build PASS cannot become matching, timing, or a winner")


def extend_current_evidence(history: dict[str, str],
                            receipt: dict) -> dict[str, str]:
    require(isinstance(history, dict) and len(history) == 154
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in history) == 124
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "preserve the complete 149-owner, 154-reference V30 signed history")
    for path, fingerprint in history.items():
        require(isinstance(path, str), "reject a nonstring historical evidence owner")
        valid_digest(fingerprint, "historical evidence owner")
    validate_rust_build_receipt(receipt)
    added = {
        RUST_BUILD_ARCHIVE: RUST_BUILD_ARCHIVE_SHA256,
        RUST_BUILD_RECEIPT: RUST_BUILD_RECEIPT_SHA256,
    }
    require(len(added) == 2 and not (set(added) & set(history)),
            "reject duplicate, preexisting, missing, or invented Rust build owners")
    current = dict(history)
    current.update(added)
    require(len(current) == 156
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in current) == 126
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in current) == 30
            and receipt["historical_evidence_owner_count"] + len(added) == 151
            and receipt["historical_authenticated_reference_count"] + len(added) == 156,
            "derive current 151/156 from exactly two real, distinct new evidence owners")
    return current


def validate_overview(inputs: dict, summary: dict, receipt: dict) -> None:
    require(inputs.get("schema") == "rebar-candidate-current-overview-v30-inputs"
            and inputs.get("version") == 30
            and inputs.get("repository_evidence_owner_count") == 149
            and inputs.get("all_digest_addressed_history_path_count") == 154
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("suite_count") == 13
            and inputs.get("full_case_denominator") == 31237
            and inputs.get("private_waiver_count") == 13
            and inputs.get("actual_zig_candidate_workers") == 13
            and inputs.get("actual_zig_semantic_mismatch_count") == 2172
            and inputs.get("actual_rust_candidate_workers") == 13
            and inputs.get("actual_rust_semantic_mismatch_count") == 1087
            and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230,
            "preserve all V30 evidence counts and all actual failing candidates")
    require(summary.get("schema") == "rebar-candidate-current-overview-v30-summary"
            and summary.get("status") == "PASS"
            and summary.get("repository_evidence_owner_count") == 149
            and summary.get("authenticated_digest_addressed_history_paths") == 154
            and summary.get("qualified_candidate_count") == 0
            and summary.get("suite_count") == 13
            and summary.get("full_case_denominator") == 31237
            and summary.get("private_waiver_count") == 13
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
            and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
            and summary.get("zig_original_campaign_candidate_worker_count") == 13
            and summary.get("zig_original_campaign_completed_suite_count") == 13
            and summary.get("zig_original_campaign_infrastructure_failure_count") == 0
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1087
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1230,
            "never represent a published failure receipt as a passed candidate")
    snapshot = summary.get("snapshot")
    require(isinstance(snapshot, dict)
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 149
            and snapshot.get("all_digest_addressed_history_path_count") == 154
            and snapshot.get("current_source_owner_count") == 25
            and snapshot.get("frozen_independent_engine_family_count") == 6
            and snapshot.get("qualified_candidate_count") == 0
            and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS
            and snapshot.get("zig_v2_original_campaign_status") == "FAIL"
            and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count") == 2172
            and snapshot.get("zig_v2_original_campaign_verified_passing_case_count") == 2847
            and snapshot.get("zig_v2_original_campaign_actual_candidate_workers") == 13
            and snapshot.get("zig_v2_original_campaign_completed_suite_count") == 13
            and snapshot.get("zig_v2_original_campaign_infrastructure_failure_count") == 0
            and snapshot.get("rust_v3_original_campaign_semantic_mismatch_count") == 1087,
            "reject missing engine ownership or invented full matching results")
    early = snapshot.get("zig_original_campaign_preflight_failure")
    require(isinstance(early, dict) and early.get("status") == "FAIL"
            and early.get("actual_candidate_workers") == 0
            and early.get("actual_matching_case_execution_count") == 0,
            "retain the real zero-worker Zig setup failure")
    require(receipt.get("schema")
            == "rebar-owned-repaired-zig-original-campaign-v2-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("family") == "zig"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("candidate_qualified") is False
            and receipt.get("semantic_mismatch_count") == 2172
            and receipt.get("verified_passing_case_count") == 2847
            and receipt.get("actual_candidate_workers") == 13
            and receipt.get("suite_count") == 13
            and receipt.get("completed_suite_count") == 13
            and receipt.get("case_execution_denominator") == 31237
            and receipt.get("named_private_waiver_count") == 13
            and receipt.get("infrastructure_failure_count") == 0
            and receipt.get("actual_first_v1_attempt_status") == "FAIL"
            and receipt.get("actual_first_v1_candidate_workers") == 0
            and receipt.get("actual_first_v1_matching_case_execution_count") == 0
            and receipt.get("all_original_suite_streams_retained") is True
            and receipt.get("original_native_restored") is True,
            "preserve the exact actual matching failure and zero-worker preflight")
    for document in (inputs, summary, snapshot):
        require(document.get("final_holdout_opened") is False
                and document.get("final_comparison_cases_generated") is False
                and document.get("final_comparison_planned_case_count") == 4194304
                and document.get("performance") == "NOT MEASURED"
                and document.get("memory") == "NOT MEASURED",
                "reject a generated holdout, benchmark, speed, or memory claim")
    require(summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("winner_selected") is False
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("benchmark_files_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("winner_selected") is False,
            "reject hidden cases, clocks, ranking, or an early winner")


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None) -> tuple[dict, bytes]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "use only isolated pinned stable CPython 3.14.6")
    checked_read(SOURCE_PATH, valid_digest(source_pin, "Zig V2 source"))
    checked_read(PROTOCOL_PATH, valid_digest(protocol_pin, "Zig V2 protocol"))
    protected: dict[str, bytes] = {}
    for path, fingerprint in SUPPORT.items():
        is_build_archive = path == RUST_BUILD_ARCHIVE
        size = (RUST_BUILD_ARCHIVE_BYTES if is_build_archive
                else RUST_BUILD_RECEIPT_BYTES if path == RUST_BUILD_RECEIPT
                else None)
        protected[path] = checked_read(
            path, fingerprint, size, allow_build_archive=is_build_archive,
        )
    original = checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
    checked_read(ENGINE_PATH, ENGINE_SHA256, ENGINE_BYTES)
    checked_read(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
    defective = historical_source(original, ORIGINAL_SHA256, ORIGINAL_BYTES)
    corrected = repaired_source(defective, DEFECTIVE_SHA256, DEFECTIVE_BYTES)
    require(corrected == original,
            "the private correction must reproduce every original bridge byte")

    p0 = strict_json(protected["oracle/phase1/p0-completeness-v1.json"],
                     "frozen CPython correctness oracle")
    denominator, runtime = p0.get("denominator"), p0.get("runtime")
    phase_gate = p0.get("phase_gate")
    require(p0.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and p0.get("version") == 1
            and isinstance(denominator, dict)
            and tuple(denominator.get("counted_suite_ids", ())) == SUITE_IDS
            and denominator.get("final_required_case_execution_denominator") == 31237
            and denominator.get("private_upstream_methods_outside_public_denominator") == 13
            and isinstance(runtime, dict)
            and runtime.get("python_implementation") == "CPython"
            and runtime.get("python_version") == "3.14.6"
            and isinstance(runtime.get("executable"), dict)
            and runtime["executable"].get("path") == PYTHON
            and runtime["executable"].get("sha256") == PYTHON_SHA256
            and isinstance(phase_gate, dict)
            and phase_gate.get("status") == "PASS"
            and phase_gate.get("all_obligations_mapped") is True
            and phase_gate.get("final_holdout_authorized") is False,
            "preserve the complete frozen original 31,237-case correctness oracle")

    v1 = strict_json(
        protected["oracle/phase2/zig-scanner-capture-source-repair-v1.json"],
        "historical first-party Zig scanner V1 contract",
    )
    repair = v1.get("repair")
    require(v1.get("schema") == V1_SCHEMA and v1.get("version") == 1
            and isinstance(repair, dict)
            and repair.get("function") == "zig_scanner_project_match"
            and isinstance(repair.get("original_source"), dict)
            and repair["original_source"].get("sha256") == ORIGINAL_SHA256
            and repair["original_source"].get("bytes") == ORIGINAL_BYTES
            and isinstance(repair.get("derived_source"), dict)
            and repair["derived_source"].get("sha256") == DEFECTIVE_SHA256
            and repair["derived_source"].get("bytes") == DEFECTIVE_BYTES
            and isinstance(repair.get("old_block"), dict)
            and repair["old_block"].get("sha256") == CORRECT_BLOCK_SHA256
            and repair["old_block"].get("bytes") == len(CORRECT_BLOCK)
            and isinstance(repair.get("new_block"), dict)
            and repair["new_block"].get("sha256") == DEFECTIVE_BLOCK_SHA256
            and repair["new_block"].get("bytes") == len(DEFECTIVE_BLOCK),
            "bind the correction to the exact genuinely published V1 mistake")

    freeze = strict_json(protected["oracle/phase2/six-family-p0-producer-v3.json"],
                         "frozen six-family first-party ownership proof")
    require(freeze.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and freeze.get("version") == 3
            and freeze.get("status")
            == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
            and freeze.get("family_count") == 6
            and freeze.get("source_owner_count") == 25
            and freeze.get("pairwise_shared_semantic_source_count") == 0
            and freeze.get("suite_count") == 13
            and freeze.get("case_execution_denominator") == 31237
            and freeze.get("goal_sha256") == SUPPORT["GOAL.md"],
            "preserve six separate from-scratch regex implementations")
    families = freeze.get("families")
    require(isinstance(families, list) and len(families) == 6,
            "require all independently owned first-party engine families")
    identifiers: set[str] = set()
    owners: set[str] = set()
    zig: dict | None = None
    for family in families:
        require(isinstance(family, dict)
                and isinstance(family.get("family"), str)
                and family["family"] not in identifiers,
                "reject missing, duplicated, or forged engine families")
        identifiers.add(family["family"])
        sources = family.get("sources")
        require(isinstance(sources, list)
                and len(sources) == family.get("owned_source_count")
                and len(sources) > 0,
                "reject incomplete first-party matching ownership")
        for owner in sources:
            require(isinstance(owner, dict)
                    and isinstance(owner.get("relative"), str)
                    and owner["relative"] not in owners
                    and isinstance(owner.get("size_bytes"), int),
                    "reject duplicate or cross-family semantic source ownership")
            checked_read(owner["relative"],
                         valid_digest(owner.get("sha256"), "engine source"),
                         owner["size_bytes"])
            owners.add(owner["relative"])
        if family["family"] == "zig":
            zig = family
    require(identifiers == {"c", "rust", "zig", "cpp", "go", "fortran"}
            and len(owners) == 25 and isinstance(zig, dict)
            and zig.get("owned_source_count") == 3
            and zig.get("bridge_module") == "candidates._zig_bridge"
            and zig.get("adapter_relative") == ADAPTER_PATH
            and {ORIGINAL_PATH, ENGINE_PATH, ADAPTER_PATH}.issubset(owners),
            "retain exactly one independent three-source Zig implementation")
    effects = freeze.get("verification_effects")
    require(isinstance(effects, dict)
            and effects.get("actual_candidate_imports") == 0
            and effects.get("actual_candidate_workers") == 0
            and effects.get("actual_source_builds") == 0
            and effects.get("actual_native_activations") == 0
            and effects.get("actual_network_requests") == 0
            and effects.get("actual_subprocesses_started") == 0
            and effects.get("clock_samples") == 0
            and effects.get("hidden_cases_read") == 0
            and effects.get("candidate_qualified_count") == 0
            and effects.get("holdout") == "NOT OPENED"
            and effects.get("performance") == "NOT MEASURED",
            "a source freeze cannot run an engine or open a holdout")

    lock = strict_json(protected["toolchains/zig-0.16.0.lock.json"],
                       "locked stable Zig toolchain")
    require(lock.get("schema") == "rebar-official-language-toolchain-v1"
            and lock.get("language") == "Zig"
            and lock.get("version") == "0.16.0"
            and lock.get("release_channel") == "stable"
            and lock.get("compiler_sha256")
            == "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
            and lock.get("compiler_relative_path")
            == "zig-x86_64-linux-0.16.0/zig",
            "retain the exact stable Zig lock without opening or running a compiler")

    inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v30.inputs.json"],
        "published V30 graph inputs",
    )
    summary = strict_json(
        protected["docs/evidence/candidate-current-overview-v30.json"],
        "published V30 graph summary",
    )
    receipt = strict_json(protected[ZIG_RECEIPT],
                          "actual complete Zig matching publication receipt")
    rust_build_receipt = strict_json(
        protected[RUST_BUILD_RECEIPT],
        "actual distinct Rust V12 source-build publication receipt",
    )
    validate_overview(inputs, summary, receipt)
    evidence = load_history(inputs, summary)
    require(evidence.get(ZIG_RECEIPT) == SUPPORT[ZIG_RECEIPT],
            "bind the exact small Zig failure receipt to frozen V30 history")
    current = extend_current_evidence(evidence, rust_build_receipt)
    require(current.get(RUST_BUILD_ARCHIVE) == RUST_BUILD_ARCHIVE_SHA256
            and current.get(RUST_BUILD_RECEIPT) == RUST_BUILD_RECEIPT_SHA256
            and current.get(ZIG_RECEIPT) == SUPPORT[ZIG_RECEIPT],
            "retain historical failed Zig while authenticating both new Rust owners")
    contract = contract_document(source_pin, protocol_pin)
    if contract_pin is not None:
        raw = checked_read(CONTRACT_PATH,
                           valid_digest(contract_pin, "Zig V2 contract"))
        require(raw == canonical(contract),
                "reject a substituted or noncanonical exact V2 contract")
    return contract, corrected


def contract_document(source_pin: str, protocol_pin: str) -> dict:
    return {
        "schema": SCHEMA,
        "version": 2,
        "phase": "EVIDENCE-BACKED ZIG SCANNER SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "tool": {"path": SOURCE_PATH, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin},
        "oracle": {
            "implementation": "CPython", "version": "3.14.6",
            "manifest_path": "oracle/phase1/p0-completeness-v1.json",
            "manifest_sha256": SUPPORT["oracle/phase1/p0-completeness-v1.json"],
            "suite_count": 13, "suite_ids": list(SUITE_IDS),
            "case_execution_count": 31237, "private_waiver_count": 13,
        },
        "observed_failure": {
            "case_id": CASE_ID,
            "suite_id": "public_v3",
            "api": "Scanner",
            "whole_match": "alpha42",
            "expected_branch_group": "alpha42",
            "expected_branch_span": [0, 7],
            "historical_actual_branch_group": "alpha",
            "historical_actual_branch_span": [0, 5],
            "nested_capture_must_be_retained_when_not_the_branch_group": True,
            "evidence_origin": "BOUNDED READ OF THE PUBLISHED FULL ORIGINAL ZIG FAILURE; ARCHIVE NOT OPENED BY V2",
            "corrected_native_case_executed": False,
            "corrected_candidate_correctness": "NOT MEASURED",
        },
        "zig_ownership": {
            "independent_family_count": 6,
            "first_party_source_owner_count": 25,
            "zig_source_owner_count": 3,
            "cross_family_semantic_source_count": 0,
            "engine": {"path": ENGINE_PATH, "sha256": ENGINE_SHA256,
                       "bytes": ENGINE_BYTES, "modified": False},
            "adapter": {"path": ADAPTER_PATH, "sha256": ADAPTER_SHA256,
                        "bytes": ADAPTER_BYTES, "modified": False},
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_delegation": "FORBIDDEN",
            "candidate_family": "zig", "candidate_family_added": False,
        },
        "historical_v1": {
            "source_path": "tools/apply_owned_zig_scanner_capture_source_repair_v1.py",
            "source_sha256": SUPPORT["tools/apply_owned_zig_scanner_capture_source_repair_v1.py"],
            "protocol_path": "oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md",
            "protocol_sha256": SUPPORT["oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md"],
            "contract_path": "oracle/phase2/zig-scanner-capture-source-repair-v1.json",
            "contract_sha256": SUPPORT["oracle/phase2/zig-scanner-capture-source-repair-v1.json"],
            "conditional_source_sha256": DEFECTIVE_SHA256,
            "conditional_source_bytes": DEFECTIVE_BYTES,
            "historical_files_modified": False,
        },
        "repair": {
            "function": "zig_scanner_project_match",
            "canonical_original_source": {
                "path": ORIGINAL_PATH, "sha256": ORIGINAL_SHA256,
                "bytes": ORIGINAL_BYTES, "modified": False,
            },
            "defective_historical_block": {
                "sha256": DEFECTIVE_BLOCK_SHA256,
                "bytes": len(DEFECTIVE_BLOCK),
                "occurrence_count_before": 1,
                "occurrence_count_after": 0,
            },
            "corrected_whole_branch_block": {
                "sha256": CORRECT_BLOCK_SHA256,
                "bytes": len(CORRECT_BLOCK),
                "occurrence_count_before": 0,
                "occurrence_count_after": 1,
            },
            "derived_source": {
                "sha256": CORRECTED_SHA256, "bytes": CORRECTED_BYTES,
                "byte_identical_to_original": True,
                "materialized": False,
            },
            "branch_group": "WHOLE MATCH, INCLUDING WHEN A NESTED CAPTURE OCCUPIES ITS SLOT",
            "noncolliding_nested_captures": "PRESERVED",
            "branch_lastindex": "UNCHANGED",
            "range_checks": "UNCHANGED",
            "branch_identification": "UNCHANGED",
            "native_last_handling": "UNCHANGED",
            "match_expand": "UNCHANGED",
            "substitution": "UNCHANGED",
            "buffer_acquisition": "UNCHANGED",
            "source_bytes_outside_exact_block": "UNCHANGED",
            "corrected_native_case_executed": False,
            "corrected_candidate_correctness": "NOT MEASURED",
        },
        "official_compiler": {
            "version": "0.16.0",
            "path": "/tmp/zig-x86_64-linux-0.16.0/zig",
            "sha256": "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
            "lock_path": "toolchains/zig-0.16.0.lock.json",
            "lock_sha256": SUPPORT["toolchains/zig-0.16.0.lock.json"],
            "compiler_binary_read": False,
            "compiler_executed": False,
        },
        "published_history": {
            "historical_overview_version": 30,
            "overview_inputs_path": "docs/evidence/candidate-current-overview-v30.inputs.json",
            "overview_inputs_sha256": SUPPORT["docs/evidence/candidate-current-overview-v30.inputs.json"],
            "overview_path": "docs/evidence/candidate-current-overview-v30.json",
            "overview_sha256": SUPPORT["docs/evidence/candidate-current-overview-v30.json"],
            "historical_counted_evidence_owner_count": 149,
            "historical_authenticated_reference_count": 154,
            "historical_oracle_evidence_reference_count": 124,
            "new_actual_rust_build_evidence_owner_count": 2,
            "authoritative_counted_evidence_owner_count": 151,
            "authenticated_digest_addressed_history_paths": 156,
            "oracle_evidence_reference_count": 126,
            "experiment_evidence_reference_count": 30,
            "history_overview_version_start": 19,
            "history_overview_version_end": 30,
            "compressed_build_archive_files_opened": 1,
            "compressed_matching_failure_archive_files_opened": 0,
            "gzip_inflation_count": 0,
            "native_binary_files_opened": 0,
            "qualified_candidate_count": 0,
        },
        "current_rust_v12_source_build": {
            "family": "rust",
            "label": "phase2-v12-rust-flag-original-p0",
            "publication_status": "PASS",
            "build_status": "PASS",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "actual_compiler_process_count": 28,
            "historical_evidence_owner_count": 149,
            "historical_authenticated_reference_count": 154,
            "new_actual_evidence_owner_count": 2,
            "repository_evidence_owner_count_after_publication": 151,
            "authenticated_reference_count_after_publication": 156,
            "archive": {
                "path": RUST_BUILD_ARCHIVE,
                "sha256": RUST_BUILD_ARCHIVE_SHA256,
                "bytes": RUST_BUILD_ARCHIVE_BYTES,
                "device": RUST_BUILD_ARCHIVE_DEVICE,
                "inode": RUST_BUILD_ARCHIVE_INODE,
                "compressed_bytes_read": RUST_BUILD_ARCHIVE_BYTES,
                "decompressed_bytes_read": 0,
                "gzip_inflation_count": 0,
            },
            "receipt": {
                "path": RUST_BUILD_RECEIPT,
                "sha256": RUST_BUILD_RECEIPT_SHA256,
                "bytes": RUST_BUILD_RECEIPT_BYTES,
            },
            "publication_pass_means": "DURABLE SOURCE BUILD ONLY; MATCHING NOT MEASURED",
            "historical_rust_matching_semantic_mismatch_count": 1087,
        },
        "preserved_results": {
            "zig_candidate_status": "FAIL; NOT QUALIFIED",
            "zig_semantic_mismatch_count": 2172,
            "zig_verified_passing_case_count": 2847,
            "zig_actual_candidate_workers": 13,
            "zig_completed_suite_count": 13,
            "zig_infrastructure_failure_count": 0,
            "historical_first_zig_candidate_workers": 0,
            "historical_first_zig_matching_case_executions": 0,
            "rust_semantic_mismatch_count": 1087,
            "c_semantic_mismatch_count": 1230,
            "receipt_path": ZIG_RECEIPT,
            "receipt_sha256": SUPPORT[ZIG_RECEIPT],
            "receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
            "corrected_candidate_correctness": "NOT MEASURED",
        },
        "apply_policy": {
            "explicit_apply_required": True,
            "workspace_destination": "FORBIDDEN",
            "candidate_source_mutation": "FORBIDDEN",
            "existing_destination": "FORBIDDEN",
            "external_owner": "FORBIDDEN",
            "private_root_parent": "/tmp",
            "private_root_prefix": PRIVATE_ROOT_PREFIX,
            "phase_names": ["reference-a", "reference-b"],
            "relative_destination": ORIGINAL_PATH,
            "private_directory_mode": "0700",
            "private_file_mode": "0600",
            "mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "file_fsync_required": True,
            "directory_fsync_required": True,
            "same_inode_readback_required": True,
            "holdout": "NOT OPENED",
        },
        "phase_boundary": {
            "source_apply_count": 0,
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "native_binary_files_opened": 0,
            "compressed_archive_files_opened": 1,
            "compressed_build_archive_files_opened": 1,
            "compressed_matching_failure_archive_files_opened": 0,
            "gzip_inflation_count": 0,
            "network_requests": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "qualified_candidate_count": 0,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "holdout": "NOT OPENED",
            "holdout_opened": False,
            "winner_selected": False,
        },
        "pinned_support": [
            {"path": path, "sha256": fingerprint}
            for path, fingerprint in sorted(SUPPORT.items())
        ],
    }


def synthetic_original() -> bytes:
    return (b"/* synthetic, first-party scanner projection */\n"
            + FUNCTION_ANCHOR + b"void) {\n" + LOCAL_PROJECTION
            + CORRECT_BLOCK + b"    return 1;\n}\n"
            + NEXT_FUNCTION_ANCHOR + b"void) { return NULL; }\n")


def synthetic_overview() -> tuple[dict, dict, dict]:
    boundary = {
        "final_holdout_opened": False,
        "final_comparison_cases_generated": False,
        "final_comparison_planned_case_count": 4194304,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
    }
    inputs = {
        **boundary,
        "schema": "rebar-candidate-current-overview-v30-inputs",
        "version": 30,
        "repository_evidence_owner_count": 149,
        "all_digest_addressed_history_path_count": 154,
        "candidate_qualified_count": 0,
        "suite_count": 13,
        "full_case_denominator": 31237,
        "private_waiver_count": 13,
        "actual_zig_candidate_workers": 13,
        "actual_zig_semantic_mismatch_count": 2172,
        "actual_rust_candidate_workers": 13,
        "actual_rust_semantic_mismatch_count": 1087,
        "c_original_campaign_semantic_mismatch_count": 1230,
    }
    snapshot = {
        **boundary,
        "all_actual_candidate_and_native_evidence_owner_count": 149,
        "all_digest_addressed_history_path_count": 154,
        "current_source_owner_count": 25,
        "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "suite_ids": list(SUITE_IDS),
        "zig_v2_original_campaign_status": "FAIL",
        "zig_v2_original_campaign_semantic_mismatch_count": 2172,
        "zig_v2_original_campaign_verified_passing_case_count": 2847,
        "zig_v2_original_campaign_actual_candidate_workers": 13,
        "zig_v2_original_campaign_completed_suite_count": 13,
        "zig_v2_original_campaign_infrastructure_failure_count": 0,
        "rust_v3_original_campaign_semantic_mismatch_count": 1087,
        "zig_original_campaign_preflight_failure": {
            "status": "FAIL",
            "actual_candidate_workers": 0,
            "actual_matching_case_execution_count": 0,
        },
    }
    summary = {
        **boundary,
        "schema": "rebar-candidate-current-overview-v30-summary",
        "status": "PASS",
        "repository_evidence_owner_count": 149,
        "authenticated_digest_addressed_history_paths": 154,
        "qualified_candidate_count": 0,
        "suite_count": 13,
        "full_case_denominator": 31237,
        "private_waiver_count": 13,
        "zig_original_campaign_status": "FAIL",
        "zig_original_campaign_semantic_mismatch_count": 2172,
        "zig_original_campaign_verified_passing_case_count": 2847,
        "zig_original_campaign_candidate_worker_count": 13,
        "zig_original_campaign_completed_suite_count": 13,
        "zig_original_campaign_infrastructure_failure_count": 0,
        "rust_original_campaign_semantic_mismatch_count": 1087,
        "c_original_campaign_semantic_mismatch_count": 1230,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "winner_selected": False,
        "snapshot": snapshot,
    }
    receipt = {
        "schema": "rebar-owned-repaired-zig-original-campaign-v2-durable-publication-receipt",
        "status": "PASS",
        "family": "zig",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "semantic_mismatch_count": 2172,
        "verified_passing_case_count": 2847,
        "actual_candidate_workers": 13,
        "suite_count": 13,
        "completed_suite_count": 13,
        "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "infrastructure_failure_count": 0,
        "actual_first_v1_attempt_status": "FAIL",
        "actual_first_v1_candidate_workers": 0,
        "actual_first_v1_matching_case_execution_count": 0,
        "all_original_suite_streams_retained": True,
        "original_native_restored": True,
        "holdout": "NOT OPENED",
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "winner_selected": False,
    }
    return inputs, summary, receipt


def synthetic_current_build() -> tuple[dict[str, str], dict]:
    history = {
        f"oracle/phase2/evidence/zig-v2-synthetic-history-{index:03d}.json":
        "a" * 64
        for index in range(124)
    }
    history.update({
        ("experiments/rust_public_practice_v1/"
         f"zig-v2-synthetic-history-{index:03d}.json"): "b" * 64
        for index in range(30)
    })
    receipt = {
        "schema": "rebar-phase2-owned-rust-flag-source-build-v12-durable-publication-receipt",
        "status": "PASS",
        "build_status": "PASS",
        "family": "rust",
        "label": "phase2-v12-rust-flag-original-p0",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "historical_evidence_owner_count": 149,
        "historical_authenticated_reference_count": 154,
        "new_actual_evidence_owner_count": 2,
        "repository_evidence_owner_count_after_publication": 151,
        "authenticated_history_reference_count_after_publication": 156,
        "archive_relative": RUST_BUILD_ARCHIVE,
        "archive_sha256": RUST_BUILD_ARCHIVE_SHA256,
        "archive_bytes": RUST_BUILD_ARCHIVE_BYTES,
        "uncompressed_bytes": 757826,
        "uncompressed_sha256":
            "a69fe5a873891c3aee51cf8e711877125b06c079057b04daeb86720bbd2dc75f",
        "actual_compiler_process_count": 28,
        "expected_actual_compiler_process_count": 28,
        "corrected_public_overlay_apply_count": 2,
        "bridge_overlay_apply_count": 2,
        "public_derived_sha256":
            "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5",
        "bridge_derived_sha256":
            "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257",
        "archive_publication": {
            "path": str(ROOT / RUST_BUILD_ARCHIVE),
            "sha256": RUST_BUILD_ARCHIVE_SHA256,
            "bytes": RUST_BUILD_ARCHIVE_BYTES,
            "device": RUST_BUILD_ARCHIVE_DEVICE,
            "inode": RUST_BUILD_ARCHIVE_INODE,
            "exclusive_creation": True,
            "file_fsync_completed": True,
            "same_inode_readback_verified": True,
            "write_calls": 1,
        },
        "archive_directory_fsync": {
            "completed": True, "device": RUST_BUILD_ARCHIVE_DEVICE,
        },
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return history, receipt


def self_test() -> dict:
    accepted = rejected = 0
    original = synthetic_original()
    with SourceOnlyBoundary() as boundary:
        defective = historical_source(original, sha256(original),
                                      len(original), frozen=False)
        corrected = repaired_source(defective, sha256(defective),
                                   len(defective), frozen=False)
        broken, broken_last = project_witness(
            conditional=True, active=0,
            local_spans=((0, 5),), whole=(0, 7),
        )
        fixed, fixed_last = project_witness(
            conditional=False, active=0,
            local_spans=((0, 5),), whole=(0, 7),
        )
        preserved, preserved_last = project_witness(
            conditional=False, active=1,
            local_spans=((0, 5), (-1, -1)), whole=(0, 7),
        )
        synthetic_inputs, synthetic_summary, synthetic_receipt = synthetic_overview()
        validate_overview(synthetic_inputs, synthetic_summary, synthetic_receipt)
        synthetic_history, synthetic_rust_build = synthetic_current_build()
        synthetic_current = extend_current_evidence(
            synthetic_history, synthetic_rust_build,
        )
        controls = (
            (corrected == original, "restore every original synthetic bridge byte"),
            (sha256(CORRECT_BLOCK) == CORRECT_BLOCK_SHA256, "correct exact block hash"),
            (len(CORRECT_BLOCK) == 190, "correct exact block size"),
            (sha256(DEFECTIVE_BLOCK) == DEFECTIVE_BLOCK_SHA256,
             "historical conditional block hash"),
            (len(DEFECTIVE_BLOCK) == 246, "historical conditional block size"),
            (defective.count(DEFECTIVE_BLOCK) == 1,
             "reconstruct exactly one historical block"),
            (defective.count(CORRECT_BLOCK) == 0,
             "do not leave a second historical whole-branch block"),
            (corrected.count(CORRECT_BLOCK) == 1,
             "restore exactly one original whole-branch block"),
            (corrected.count(DEFECTIVE_BLOCK) == 0,
             "remove the exact historical conditional block"),
            (corrected.count(LOCAL_PROJECTION) == 1,
             "preserve all nested-capture range checks"),
            (corrected.index(LOCAL_PROJECTION) < corrected.index(CORRECT_BLOCK),
             "preserve capture projection before whole-branch assignment"),
            (broken[1] == (0, 5) and broken_last == 1,
             "reproduce the actual historical alpha scanner witness"),
            (fixed[1] == (0, 7) and fixed_last == 1,
             "restore the actual required alpha42 whole-branch span"),
            (preserved[1] == (0, 5), "retain a noncolliding nested alpha span"),
            (preserved[2] == (0, 7) and preserved_last == 2,
             "retain a distinct full branch and correct lastindex"),
            (private_parts("/tmp/" + PRIVATE_ROOT_PREFIX
                           + "synthetic/reference-a/source")[3] == "reference-a",
             "accept only the first distinct owner-only phase"),
            (private_parts("/tmp/" + PRIVATE_ROOT_PREFIX
                           + "synthetic/reference-b/source")[3] == "reference-b",
             "accept only the second distinct owner-only phase"),
            (CORRECTED_SHA256 == ORIGINAL_SHA256
             and CORRECTED_BYTES == ORIGINAL_BYTES,
             "the frozen corrected bridge is byte-identical to canonical"),
            (synthetic_summary["repository_evidence_owner_count"] == 149
             and synthetic_summary["authenticated_digest_addressed_history_paths"] == 154,
             "accept the exact historical V30 evidence-owner and reference counts"),
            (len(synthetic_history) == 154 and len(synthetic_current) == 156,
             "derive exactly two additional authentic Rust V12 evidence references"),
            (synthetic_rust_build["historical_evidence_owner_count"] == 149
             and synthetic_rust_build["repository_evidence_owner_count_after_publication"]
             == 151,
             "derive current 151 actual evidence owners from historical 149"),
            (synthetic_rust_build["historical_authenticated_reference_count"] == 154
             and synthetic_rust_build[
                 "authenticated_history_reference_count_after_publication"] == 156,
             "derive current 156 references from historical 154"),
            (synthetic_rust_build["build_status"] == "PASS"
             and synthetic_rust_build["candidate_correctness"] == "NOT MEASURED",
             "never count successful Rust building as successful Rust matching"),
            (relative_parts(RUST_BUILD_ARCHIVE, allow_build_archive=True)
             == PurePosixPath(RUST_BUILD_ARCHIVE).parts,
             "permit raw bytes only from the independently pinned Rust build owner"),
            (synthetic_receipt["status"] == "PASS"
             and synthetic_receipt["candidate_status"] == "FAIL",
             "distinguish successful publication from failed candidate matching"),
        )
        for condition, label in controls:
            require(condition, "failed synthetic V2 scanner control: " + label)
            accepted += 1

        def reject(action: object, label: str) -> None:
            nonlocal rejected
            try:
                action()  # type: ignore[operator]
            except (GateError, OSError, TypeError, ValueError,
                    OverflowError, UnicodeError, RecursionError):
                rejected += 1
            else:
                raise GateError("accepted hostile Zig V2 control: " + label)

        changes = {
            "wrong historical digest": (defective, "0" * 64, len(defective)),
            "wrong historical size": (defective, sha256(defective), len(defective) + 1),
            "missing conditional":
                (defective.replace(DEFECTIVE_BLOCK, b"/* removed */\n"), None, None),
            "duplicate conditional":
                (defective.replace(DEFECTIVE_BLOCK,
                                   DEFECTIVE_BLOCK + DEFECTIVE_BLOCK), None, None),
            "already corrected": (original, sha256(original), len(original)),
            "missing function":
                (defective.replace(FUNCTION_ANCHOR, b"unowned_projection("), None, None),
            "duplicate function": (FUNCTION_ANCHOR + defective, None, None),
            "missing following function":
                (defective.replace(NEXT_FUNCTION_ANCHOR, b"unowned_match("), None, None),
            "duplicate following function":
                (defective + NEXT_FUNCTION_ANCHOR, None, None),
            "missing nested projection":
                (defective.replace(LOCAL_PROJECTION, b"/* removed */\n"), None, None),
            "duplicate nested projection":
                (defective.replace(LOCAL_PROJECTION,
                                   LOCAL_PROJECTION + LOCAL_PROJECTION), None, None),
            "conditional outside owned function":
                (DEFECTIVE_BLOCK
                 + defective.replace(DEFECTIVE_BLOCK, b"/* moved */\n"), None, None),
            "falsely frozen synthetic owner":
                (defective, sha256(defective), len(defective)),
        }
        for label, (raw, fingerprint, size) in changes.items():
            actual = sha256(raw) if fingerprint is None else fingerprint
            count = len(raw) if size is None else size
            reject(lambda item=raw, digest=actual, length=count,
                   frozen=label == "falsely frozen synthetic owner":
                   repaired_source(item, digest, length, frozen=frozen), label)
        reject(lambda: historical_source(original, "0" * 64, len(original),
                                        frozen=False), "substituted canonical source")
        reject(lambda: historical_source(original, sha256(original), len(original),
                                        frozen=True), "falsely frozen synthetic canonical")

        for path in (
            "", "/", "../owner", "a/../owner", "a/./owner", "a//owner",
            "./owner", "a/", "x" * 513,
            "/home/dev-user/src/rebar/candidates/zig/py_bridge.c",
            "oracle/phase2/evidence/hidden.json.gz",
            RUST_BUILD_ARCHIVE,
            "candidates/_zig_probe.so", "secret/holdout/case.json",
            "benchmarks/final.json",
        ):
            reject(lambda value=path: relative_parts(value),
                   "unsafe, native, archive, benchmark, or holdout path")
        for path in (
            "", "/", "/tmp", "/home/dev-user/src/rebar",
            "/tmp/" + PRIVATE_ROOT_PREFIX,
            "/tmp/" + PRIVATE_ROOT_PREFIX + "x/reference-c/source",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "x/reference-a/native",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "x/../source",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "x/reference-a/source/",
            "/tmp/rebar-phase2-zig-scanner-capture-source-build-v1-x/reference-a/source",
            "/tmp/rebar-phase2-rust-source-build-v1-x/reference-a/source",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "x/reference-a/source/extra",
        ):
            reject(lambda value=path: private_parts(value),
                   "unsafe, reused, or cross-family private phase")
        for fingerprint in ("", "0" * 63, "0" * 65, "F" * 64, "g" * 64):
            reject(lambda value=fingerprint: valid_digest(value, "synthetic"),
                   "invalid or substituted owner fingerprint")
        for raw in (b'{"x":1,"x":2}\n', b'{"x":NaN}\n', b"[]\n",
                    b'{"x": 1}\n', b'{"x":1}'):
            reject(lambda value=raw: strict_json(value, "synthetic",
                                                require_canonical=True),
                   "duplicate, nonfinite, nonobject, or noncanonical JSON")
        references: dict[str, str] = {}
        discover_evidence({"path": "oracle/phase2/evidence/synthetic.json",
                           "sha256": "0" * 64}, references)
        reject(lambda: discover_evidence(
            {"path": "oracle/phase2/evidence/synthetic.json",
             "sha256": "1" * 64}, references),
            "conflicting digest-addressed evidence owner")
        overview_controls = (
            (0, ("repository_evidence_owner_count",), 148),
            (0, ("all_digest_addressed_history_path_count",), 153),
            (0, ("candidate_qualified_count",), 1),
            (0, ("suite_count",), 12),
            (0, ("full_case_denominator",), 31236),
            (0, ("private_waiver_count",), 12),
            (0, ("actual_zig_candidate_workers",), 0),
            (0, ("actual_zig_semantic_mismatch_count",), 0),
            (0, ("actual_rust_semantic_mismatch_count",), 0),
            (0, ("c_original_campaign_semantic_mismatch_count",), 0),
            (0, ("final_holdout_opened",), True),
            (0, ("performance",), "FASTER"),
            (1, ("repository_evidence_owner_count",), 148),
            (1, ("authenticated_digest_addressed_history_paths",), 153),
            (1, ("qualified_candidate_count",), 1),
            (1, ("zig_original_campaign_status",), "PASS"),
            (1, ("zig_original_campaign_semantic_mismatch_count",), 0),
            (1, ("zig_original_campaign_verified_passing_case_count",), 31237),
            (1, ("zig_original_campaign_candidate_worker_count",), 0),
            (1, ("rust_original_campaign_semantic_mismatch_count",), 0),
            (1, ("c_original_campaign_semantic_mismatch_count",), 0),
            (1, ("hidden_cases_read",), 1),
            (1, ("clock_samples",), 1),
            (1, ("timing_trials_run",), 1),
            (1, ("winner_selected",), True),
            (1, ("snapshot", "all_actual_candidate_and_native_evidence_owner_count"), 148),
            (1, ("snapshot", "all_digest_addressed_history_path_count"), 153),
            (1, ("snapshot", "current_source_owner_count"), 24),
            (1, ("snapshot", "frozen_independent_engine_family_count"), 5),
            (1, ("snapshot", "qualified_candidate_count"), 1),
            (1, ("snapshot", "zig_v2_original_campaign_status"), "PASS"),
            (1, ("snapshot", "zig_v2_original_campaign_semantic_mismatch_count"), 0),
            (1, ("snapshot", "zig_v2_original_campaign_actual_candidate_workers"), 0),
            (1, ("snapshot", "zig_original_campaign_preflight_failure",
                 "actual_candidate_workers"), 1),
            (1, ("snapshot", "final_comparison_cases_generated"), True),
            (2, ("candidate_status",), "PASS"),
            (2, ("candidate_qualified",), True),
            (2, ("semantic_mismatch_count",), 0),
            (2, ("verified_passing_case_count",), 31237),
            (2, ("actual_candidate_workers",), 0),
            (2, ("actual_first_v1_candidate_workers",), 1),
            (2, ("infrastructure_failure_count",), 1),
            (2, ("holdout",), "OPENED"),
            (2, ("clock_samples",), 1),
            (2, ("performance",), "FASTER"),
            (2, ("winner_selected",), True),
        )
        for index, route, forged in overview_controls:
            documents = copy.deepcopy((synthetic_inputs, synthetic_summary,
                                      synthetic_receipt))
            target = documents[index]
            for key in route[:-1]:
                target = target[key]
            target[route[-1]] = forged
            reject(lambda items=documents: validate_overview(*items),
                   "forged matching, owner count, winner, or phase boundary")
        build_controls = (
            (("status",), "FAIL"),
            (("build_status",), "FAIL"),
            (("family",), "zig"),
            (("label",), "phase2-v11-rust-original-p0"),
            (("candidate_correctness",), "PASS"),
            (("candidate_qualified",), True),
            (("historical_evidence_owner_count",), 151),
            (("historical_authenticated_reference_count",), 156),
            (("new_actual_evidence_owner_count",), 1),
            (("repository_evidence_owner_count_after_publication",), 149),
            (("authenticated_history_reference_count_after_publication",), 154),
            (("archive_relative",), "oracle/phase2/evidence/forged.json.gz"),
            (("archive_sha256",), "0" * 64),
            (("archive_bytes",), RUST_BUILD_ARCHIVE_BYTES - 1),
            (("uncompressed_bytes",), 757825),
            (("uncompressed_sha256",), "0" * 64),
            (("actual_compiler_process_count",), 27),
            (("expected_actual_compiler_process_count",), 27),
            (("corrected_public_overlay_apply_count",), 1),
            (("bridge_overlay_apply_count",), 1),
            (("public_derived_sha256",), "0" * 64),
            (("bridge_derived_sha256",), "0" * 64),
            (("archive_publication", "path"), "/tmp/forged-rust-v12.gz"),
            (("archive_publication", "sha256"), "0" * 64),
            (("archive_publication", "bytes"), RUST_BUILD_ARCHIVE_BYTES - 1),
            (("archive_publication", "device"), 0),
            (("archive_publication", "inode"), 0),
            (("archive_publication", "exclusive_creation"), False),
            (("archive_publication", "file_fsync_completed"), False),
            (("archive_publication", "same_inode_readback_verified"), False),
            (("archive_publication", "write_calls"), 0),
            (("archive_directory_fsync", "completed"), False),
            (("candidate_imports",), 1),
            (("candidate_processes_started",), 1),
            (("native_libraries_loaded",), 1),
            (("hidden_cases_read",), 1),
            (("clock_samples",), 1),
            (("timing_trials_run",), 1),
            (("performance",), "FASTER"),
            (("memory",), "FREE"),
            (("holdout",), "OPENED"),
            (("winner_selected",), True),
        )
        for route, forged in build_controls:
            changed_build = copy.deepcopy(synthetic_rust_build)
            node = changed_build
            for key in route[:-1]:
                node = node[key]
            node[route[-1]] = forged
            reject(lambda value=changed_build: extend_current_evidence(
                synthetic_history, value),
                "stale current counts, forged Rust build, or invented matching")
        for duplicate_path, duplicate_digest in (
            (RUST_BUILD_ARCHIVE, RUST_BUILD_ARCHIVE_SHA256),
            (RUST_BUILD_RECEIPT, RUST_BUILD_RECEIPT_SHA256),
        ):
            duplicated = dict(synthetic_history)
            duplicated.pop("oracle/phase2/evidence/zig-v2-synthetic-history-000.json")
            duplicated[duplicate_path] = duplicate_digest
            reject(lambda value=duplicated: extend_current_evidence(
                value, synthetic_rust_build),
                "reuse or double-count a supposedly new Rust build owner")
        reject(lambda: relative_parts(
            "oracle/phase2/evidence/forged.json.gz", allow_build_archive=True),
            "allow arbitrary compressed archives under a build-only exception")
        reject(lambda: relative_parts(
            RUST_BUILD_ARCHIVE, allow_build_archive=1),
            "substitute a nonboolean compressed-build access policy")
        for kwargs in (
            {"conditional": True, "active": -1,
             "local_spans": ((0, 5),), "whole": (0, 7)},
            {"conditional": True, "active": 1,
             "local_spans": ((0, 5),), "whole": (0, 7)},
            {"conditional": True, "active": 0,
             "local_spans": ((0, 8),), "whole": (0, 7)},
            {"conditional": True, "active": 0,
             "local_spans": ((-1, 0),), "whole": (0, 7)},
            {"conditional": True, "active": 0,
             "local_spans": ((0, 5),), "whole": (7, 0)},
        ):
            reject(lambda item=kwargs: project_witness(**item),
                   "forged nested-capture range, branch, or whole span")

        probes = (
            (lambda: builtins.open("/tmp/forbidden-zig-v2"), "builtin source read"),
            (lambda: io.open("/tmp/forbidden-zig-v2"), "I/O source read"),
            (lambda: os.open("/tmp/forbidden-zig-v2", os.O_RDONLY), "owner open"),
            (lambda: os.read(0, 1), "source descriptor read"),
            (lambda: os.write(1, b"forbidden"), "source descriptor write"),
            (lambda: os.stat("/tmp"), "source stat"),
            (lambda: os.lstat("/tmp"), "symlink stat"),
            (lambda: os.mkdir("/tmp/forbidden-zig-v2"), "phase creation"),
            (lambda: os.unlink("/tmp/forbidden-zig-v2"), "owner deletion"),
            (lambda: os.replace("/tmp/zig-v2-a", "/tmp/zig-v2-b"),
             "owner replacement"),
            (lambda: Path("/tmp/forbidden-zig-v2").read_bytes(), "path read"),
            (lambda: Path("/tmp/forbidden-zig-v2").write_bytes(b"x"), "path write"),
            (lambda: Path("/tmp").resolve(), "symlink resolution"),
            (lambda: builtins.open("oracle/phase2/evidence/forbidden.json.gz"),
             "compressed failure archive"),
            (lambda: builtins.open("candidates/_zig_probe.so"),
             "native matching library"),
            (lambda: builtins.open("benchmarks/holdout.json"), "hidden holdout"),
            (lambda: subprocess.run(("zig", "build")), "compiler process"),
            (lambda: subprocess.Popen((PYTHON, "-V")), "candidate process"),
            (lambda: socket.socket(), "network socket"),
            (lambda: tempfile.mkdtemp(), "temporary phase creation"),
            (lambda: tempfile.mkstemp(), "temporary source creation"),
            (lambda: importlib.import_module("candidates.zig_candidate"),
             "Zig candidate import"),
            (lambda: importlib.import_module("candidates.rust_candidate"),
             "cross-family candidate import"),
            (lambda: importlib.import_module("re"), "standard regex delegation"),
            (lambda: importlib.import_module("_sre"), "CPython regex delegation"),
            (lambda: threading.Thread().start(), "matching worker"),
            (lambda: time.perf_counter(), "performance clock"),
            (lambda: time.perf_counter_ns(), "performance nanoclock"),
            (lambda: time.monotonic(), "monotonic clock"),
            (lambda: time.time(), "wall clock"),
            (lambda: time.sleep(0), "waiting"),
        )
        for action, label in probes:
            reject(action, label)
        blocked = boundary.blocked
    require(blocked == len(probes),
            "every synthetic archive, native, compiler, import, or clock was blocked")
    return {
        "schema": SCHEMA, "status": "PASS",
        "mode": "SOURCE-ONLY SELF-TEST",
        "accepted_source_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_controls": blocked,
        "historical_evidence_owner_count": 149,
        "historical_authenticated_reference_count": 154,
        "new_actual_rust_build_evidence_owner_count": 2,
        "authoritative_counted_evidence_owner_count": 151,
        "authenticated_digest_addressed_history_paths": 156,
        "current_rust_build_status": "PASS",
        "current_rust_build_candidate_correctness": "NOT MEASURED",
        "historical_witness_case_id": CASE_ID,
        "historical_synthetic_branch_span": [0, 5],
        "corrected_synthetic_branch_span": [0, 7],
        "noncolliding_synthetic_nested_span": [0, 5],
        "candidate_imports": 0, "candidate_processes_started": 0,
        "compiler_processes_started": 0, "native_libraries_loaded": 0,
        "native_binary_files_opened": 0, "compressed_archive_files_opened": 0,
        "clock_samples": 0, "network_requests": 0,
        "holdout_opened": False, "workspace_mutations": 0,
        "corrected_candidate_correctness": "NOT MEASURED",
    }


def checked_private_directory(parent: int, component: str) -> int:
    require(isinstance(parent, int) and parent >= 0
            and isinstance(component, str) and component not in ("", ".", "..")
            and "/" not in component and "\\" not in component,
            "reject an invalid private phase component")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(component, flags, dir_fd=parent)
    try:
        owner = os.fstat(descriptor)
        require(stat.S_ISDIR(owner.st_mode)
                and stat.S_IMODE(owner.st_mode) == 0o700
                and owner.st_uid == os.geteuid(),
                "require an owner-only, real mode-0700 phase directory")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def apply_private(snapshot_root: str, corrected: bytes) -> dict:
    parts = private_parts(snapshot_root)
    require(len(corrected) == CORRECTED_BYTES
            and sha256(corrected) == CORRECTED_SHA256,
            "only the exact corrected private bridge may be materialized")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    tmp = os.open("/tmp", flags)
    root = phase = sibling = source = candidates = zig = destination = None
    try:
        root = checked_private_directory(tmp, parts[2])
        phase = checked_private_directory(root, parts[3])
        sibling_name = "reference-b" if parts[3] == "reference-a" else "reference-a"
        sibling = checked_private_directory(root, sibling_name)
        left, right = os.fstat(phase), os.fstat(sibling)
        require((left.st_dev, left.st_ino) != (right.st_dev, right.st_ino),
                "the two private reference phases must be genuinely distinct")
        source = checked_private_directory(phase, "source")
        candidates = checked_private_directory(source, "candidates")
        zig = checked_private_directory(candidates, "zig")
        original = checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
        historical = historical_source(original, ORIGINAL_SHA256, ORIGINAL_BYTES)
        require(repaired_source(historical, DEFECTIVE_SHA256, DEFECTIVE_BYTES)
                == corrected == original,
                "derive private bytes from the exact immutable canonical source")
        destination = os.open(
            "py_bridge.c",
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600, dir_fd=zig,
        )
        before = os.fstat(destination)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "create only one fresh owner-only private source inode")
        offset = 0
        while offset < len(corrected):
            count = os.write(destination, corrected[offset:])
            require(isinstance(count, int) and count > 0,
                    "reject an incomplete exclusive private scanner write")
            offset += count
        os.fsync(destination)
        after = os.fstat(destination)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == CORRECTED_BYTES,
                "reject replacement of the exclusive private source inode")
        os.close(destination)
        destination = None
        verify = os.open("py_bridge.c",
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                         dir_fd=zig)
        try:
            visible = os.fstat(verify)
            require((visible.st_dev, visible.st_ino, visible.st_size)
                    == (after.st_dev, after.st_ino, after.st_size),
                    "reject substitution before private same-inode readback")
            digest = hashlib.sha256()
            total = 0
            while True:
                piece = os.read(verify, 1024 * 1024)
                if not piece:
                    break
                total += len(piece)
                digest.update(piece)
            require(total == CORRECTED_BYTES
                    and digest.hexdigest() == CORRECTED_SHA256,
                    "reject an incomplete or altered corrected private bridge")
        finally:
            os.close(verify)
        os.fsync(zig)
        checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
        checked_read(ENGINE_PATH, ENGINE_SHA256, ENGINE_BYTES)
        checked_read(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
        return {
            "schema": SCHEMA, "status": "PASS",
            "mode": "EXCLUSIVE PRIVATE ZIG V2 SCANNER SNAPSHOT APPLY",
            "phase": parts[3], "snapshot_root": snapshot_root,
            "derived_source_sha256": CORRECTED_SHA256,
            "derived_source_bytes": CORRECTED_BYTES,
            "byte_identical_to_original": True,
            "candidate_original_modified": False,
            "source_apply_count": 1,
            "candidate_correctness": "NOT MEASURED",
        }
    finally:
        if destination is not None:
            os.close(destination)
        for descriptor in (zig, candidates, source, sibling, phase, root, tmp):
            if descriptor is not None:
                os.close(descriptor)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--snapshot-root")
    options = parser.parse_args()
    try:
        require(sys.implementation.name == "cpython"
                and tuple(sys.version_info[:3]) == (3, 14, 6)
                and sys.executable == PYTHON
                and sys.flags.isolated == 1
                and sys.dont_write_bytecode is True,
                "use only isolated stable CPython 3.14.6")
        valid_digest(options.source_sha256, "Zig V2 source")
        valid_digest(options.protocol_sha256, "Zig V2 protocol")
        if options.contract_sha256 is not None:
            valid_digest(options.contract_sha256, "Zig V2 contract")
        if options.self_test:
            require(options.contract_sha256 is not None
                    and options.snapshot_root is None,
                    "fully pin source, protocol, and contract for synthetic self-test")
            result = self_test()
        elif options.render_contract:
            require(options.snapshot_root is None
                    and options.contract_sha256 is None,
                    "contract rendering cannot apply or accept a preexisting contract")
            result, _corrected = verify_context(
                options.source_sha256, options.protocol_sha256,
            )
        else:
            require(options.contract_sha256 is not None,
                    "independently caller-pin the exact V2 source contract")
            contract, corrected = verify_context(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256,
            )
            if options.verify_frozen_context:
                require(options.snapshot_root is None,
                        "read-only verification cannot create a private source")
                result = {
                    "schema": contract["schema"], "status": "PASS",
                    "mode": "READ-ONLY FROZEN CONTEXT",
                    "historical_overview_version": 30,
                    "historical_evidence_owner_count": 149,
                    "historical_authenticated_reference_count": 154,
                    "new_actual_rust_build_evidence_owner_count": 2,
                    "authoritative_counted_evidence_owner_count": 151,
                    "authenticated_digest_addressed_history_paths": 156,
                    "historical_oracle_evidence_reference_count": 124,
                    "oracle_evidence_reference_count": 126,
                    "experiment_evidence_reference_count": 30,
                    "current_rust_build_status": "PASS",
                    "current_rust_build_candidate_correctness": "NOT MEASURED",
                    "current_rust_build_candidate_qualified": False,
                    "current_rust_build_actual_compiler_process_count": 28,
                    "current_rust_build_archive_sha256": RUST_BUILD_ARCHIVE_SHA256,
                    "current_rust_build_archive_bytes": RUST_BUILD_ARCHIVE_BYTES,
                    "current_rust_build_receipt_sha256": RUST_BUILD_RECEIPT_SHA256,
                    "current_rust_build_receipt_bytes": RUST_BUILD_RECEIPT_BYTES,
                    "frozen_case_execution_count": 31237,
                    "frozen_suite_count": 13,
                    "frozen_private_waiver_count": 13,
                    "frozen_independent_family_count": 6,
                    "frozen_source_owner_count": 25,
                    "frozen_zig_source_owner_count": 3,
                    "historical_witness_case_id": CASE_ID,
                    "historical_zig_semantic_mismatch_count": 2172,
                    "historical_zig_verified_passing_case_count": 2847,
                    "historical_zig_candidate_worker_count": 13,
                    "historical_first_zig_candidate_worker_count": 0,
                    "historical_rust_semantic_mismatch_count": 1087,
                    "historical_c_semantic_mismatch_count": 1230,
                    "derived_source_sha256": CORRECTED_SHA256,
                    "derived_source_bytes": CORRECTED_BYTES,
                    "derived_source_byte_identical_to_original": True,
                    "derived_source_materialized": False,
                    "source_apply_count": 0,
                    "candidate_imports": 0,
                    "candidate_processes_started": 0,
                    "compiler_processes_started": 0,
                    "native_libraries_loaded": 0,
                    "native_binary_files_opened": 0,
                    "compressed_archive_files_opened": 1,
                    "compressed_build_archive_files_opened": 1,
                    "compressed_matching_failure_archive_files_opened": 0,
                    "decompressed_archive_bytes_read": 0,
                    "gzip_inflation_count": 0,
                    "network_requests": 0, "clock_samples": 0,
                    "workspace_mutations": 0,
                    "qualified_candidate_count": 0,
                    "corrected_candidate_correctness": "NOT MEASURED",
                    "performance": "NOT MEASURED",
                    "memory": "NOT MEASURED",
                    "undefined_behavior": "NOT MEASURED",
                    "final_comparison_planned_case_count": 4194304,
                    "holdout_opened": False,
                    "winner_selected": False,
                }
            else:
                require(options.snapshot_root is not None,
                        "private source application requires an explicit snapshot")
                result = apply_private(options.snapshot_root, corrected)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GateError, OSError, TypeError, ValueError,
            OverflowError, UnicodeError, RecursionError) as error:
        sys.stderr.write(f"OWNED ZIG SCANNER SOURCE FREEZE V2: FAIL: {error}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
