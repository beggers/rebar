#!/usr/bin/env python3
"""Compose the immutable full P0 gate with real crash-safe native recovery.

The sole source-only mode is synthetic.  Actual candidate execution first
authenticates the corrected original activation validator and every durable
pre-replace promotion intent.  Frozen V1 and V2 sources are never modified.
"""
from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
from dataclasses import dataclass
import gc
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
import traceback
import types
from typing import Any, Callable, Iterator, Mapping, Sequence

ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_v4.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V4.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v4.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-v4"
PROTOCOL_SCHEMA = "rebar-frozen-python-re-p0-candidate-protocol-v4"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
P0_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
P0_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
P0_VERIFIER_RELATIVE = "tools/verify_p0_completeness_v1.py"
P0_VERIFIER_SHA256 = "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c"
V1_RELATIVE = "tools/run_frozen_p0_candidate_v1.py"
V1_SHA256 = "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8"
V2_RELATIVE = "tools/run_frozen_p0_candidate_v2.py"
V2_SHA256 = "6789f54668ab1a6b8401135a429c3a3cc9cbcb7c820fdf1df02811cdf7975ced"
V2_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V2.md"
V2_PROTOCOL_SHA256 = "fc670f502b43ce55f1ef326ea43edeee1fdf28c21726c1bd102468f50c7bbab6"
V2_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v2.json"
V2_DOCUMENT_SHA256 = "ce3b5c950ef61858af060109e9ac1050bc0851e6324625fed43343086d310c57"
V3_RELATIVE = "tools/run_frozen_p0_candidate_v3.py"
V3_SHA256 = "478d7d6d119c0f1b248890b1d4e27ffe1714688684b439ecb14bd4a83ecee557"
V3_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V3.md"
V3_PROTOCOL_SHA256 = "3587e71b91f15c7727749554d971c120ecf5dea2b3624298be19e5dd849adb84"
V3_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v3.json"
V3_DOCUMENT_SHA256 = "ebdbc2b9e6ada77a25d6c95d83078fc2af9fde5dd0c2887c5aab09748a67c8bc"
V3_FAILURE_ARCHIVE_RELATIVE = (
    "oracle/phase2/evidence/"
    "frozen-p0-candidate-v3-c-phase2-v3-failures.json.gz"
)
V3_FAILURE_ARCHIVE_SHA256 = (
    "3f7718b09080d0aa9612dabc7f97e8f41ea35958c8bbfeb7febbbf678d06028d"
)
V3_FAILURE_RECEIPT_RELATIVE = (
    "oracle/phase2/evidence/"
    "frozen-p0-candidate-v3-c-phase2-v3-failures-publication-receipt.json"
)
V3_FAILURE_RECEIPT_SHA256 = (
    "02996c09c8662c75eadadeccef2ac77895d942a56e06aca323e880f951a330a1"
)
V3_FAILURE_UNCOMPRESSED_SHA256 = (
    "5eb32867d926d709b216b1a153f7d2ad11bc9bbfe2261d90f0d4f4073757dc71"
)
V3_C_ACTIVATION_REPORT_SHA256 = (
    "15bf1d23d4753f6a6d51a7f66d3972c5b9f0c50feb82c08293960a2e1e0e2dc7"
)
V3_C_ACTIVATION_RECEIPT_SHA256 = (
    "b217874c748a8a9a67da70d000c2cfaa22b5a98ff7fdf5fef4564a05890f29fb"
)
V3_C_RECOVERY_JOURNAL_SHA256 = (
    "5ba9fb6539b373dacb2ba39f4cf6120a081709a39bc3ec3dacf68ca9fa1af82b"
)
V3_C_PROMOTION_INTENT_SHA256 = (
    "82b5206408aede2ea6cbfb5709755129951a5264a4d798feeb4949d2ab565748"
)
V3_C_RESTORATION_RECEIPT_SHA256 = (
    "f1682d947ce925a58322b4b27c7b26278b71cbbf9146d9f0724997ac0a9c942b"
)
ACTIVATION_RELATIVE = "tools/activate_verified_native_candidate_v1.py"
ACTIVATION_SHA256 = "ebc2427f6981e12c136b7f9371e5c72bccd89e1362930ad63245751d76fef164"
ACTIVATION_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V1.md"
ACTIVATION_PROTOCOL_SHA256 = "8f69bc751ac07e6d0a55fe9563c0038838976873991e45c5a0967f0d21a989d2"
ACTIVATION_SCHEMA = "rebar-phase2-verified-native-candidate-activation-v1"
BUILD_RELATIVE = "tools/reproduce_phase2_native_builds_v2.py"
BUILD_SHA256 = "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796"
BUILD_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md"
BUILD_PROTOCOL_SHA256 = "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603"
NESTED_V1_RELATIVE = "tools/run_owned_candidate_subinterpreters_v1.py"
NESTED_V1_SHA256 = "45e9b47c7c635fc30ebdb2cb4830d2d1fe382a5a7e4b663fb1a8e0112779e1a7"
NESTED_V1_DOCUMENT_RELATIVE = "oracle/phase2/candidate-subinterpreters-v1.json"
NESTED_V1_DOCUMENT_SHA256 = "7d282b559952df68b95b5ebd55634b99d922ffc27b7a640778822ec3eed6ebe2"
NESTED_V1_PROSE_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V1.md"
NESTED_V1_PROSE_SHA256 = "1dee7ebb7a98ccfec65cdb58f95378836a6747c1c9532ca676599cce62367332"
NESTED_V2_RELATIVE = "tools/run_owned_candidate_subinterpreters_v2.py"
NESTED_V2_DOCUMENT_RELATIVE = "oracle/phase2/candidate-subinterpreters-v2.json"
NESTED_V2_PROSE_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V2.md"
CASE_COUNT = 31_237
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_STREAM_BYTES = 512 * 1024 * 1024
MAX_NESTED_REPORT_BYTES = 48 * 1024 * 1024
MAX_LABEL_LENGTH = 48
TIMEOUT_SECONDS = 3_600
FAMILIES = ("rust", "c", "zig")
ROLES = {"rust": ("engine", "bridge"), "c": ("extension",),
         "zig": ("engine", "bridge")}
OWNER_IDENTITY_FIELDS = (
    "relative", "path", "sha256", "size_bytes", "device", "inode", "mode",
)
DURABLE_INTENT_FLAGS = (
    "exclusive_creation",
    "same_inode_readback_verified",
    "file_fsync_completed",
    "directory_fsync_completed",
)

SUITES = (
 ("original_bounded_v5",151,"tools/independent_original_cpython_suite_v5.py","8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce","93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240","b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"),
 ("public_v3",864,"tools/rust_public_practice_benchmark_v1.py","d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37","367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e","0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c"),
 ("scanner_v3",1024,"tools/rust_scanner_differential_v1.py","fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7","83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c","37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d"),
 ("buffer_v3",768,"tools/rust_memoryview_expand_differential_v1.py","226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6","b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60","8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75"),
 ("managed_v1",1024,"tools/independent_managed_buffer_lifetime_v1.py","cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489","28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976","80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df"),
 ("scanner_verbose_v1",2854,"tools/independent_scanner_verbose_comments_v1.py","5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d","01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b","d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012"),
 ("public_types_v1",6912,"tools/independent_public_type_identity_serialization_v1.py","7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20","c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123","0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"),
 ("substitution_v2",5120,"tools/independent_substitution_buffer_semantics_v2.py","e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573","26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54","2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b"),
 ("shape_v2",10240,"tools/independent_shape_changing_buffer_semantics_v2.py","0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c","10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8","58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c"),
 ("public_surface_v19",1376,"tools/python_re_public_surface_oracle_stage19.py","fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e","7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa","c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef"),
 ("subinterpreter_v2",128,"tools/python_re_subinterpreter_oracle_v2.py","54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8","edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3","450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8"),
 ("pep688_v4",264,"tools/python_re_buffer_exporter_oracle_v4.py","8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490","2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891","7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8"),
 ("threaded_pattern_v1",512,"tools/python_re_threaded_pattern_oracle_v1.py","05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276","a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b","928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81"),
)
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


class GateError(Exception):
    """Do not qualify a missing native proof, failed case, or lost intent."""


class WorkerFailure(GateError):
    """Preserve the complete actual output of a failed isolated worker."""

    def __init__(self, message: str, evidence: dict[str, Any]) -> None:
        super().__init__(message)
        self.evidence = evidence


class SourceOnlyEffect(GateError):
    """Synthetic controls may not perform an actual operation."""


def require(value: Any, message: str) -> None:
    if value is not True:
        raise GateError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise GateError("require complete finite canonical evidence") from error


def checked_hash(value: Any, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require an exact caller-pinned SHA-256: " + name)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "reject wrappers, external engines, and unfrozen candidates")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= MAX_LABEL_LENGTH
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(x in "abcdefghijklmnopqrstuvwxyz0123456789-" for x in value),
            "require a safe exclusively published candidate label")
    return value


def decode_document(raw: Any, name: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_STREAM_BYTES,
            "require complete bounded evidence: " + name)
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        actual: dict[str, Any] = {}
        for key, value in pairs:
            require(type(key) is str and key not in actual,
                    "reject concealed duplicate evidence keys")
            actual[key] = value
        return actual
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda x: (_ for _ in ()).throw(
                GateError("reject non-finite evidence: " + x)))
    except (ValueError, UnicodeError, TypeError, RecursionError) as error:
        raise GateError("malformed complete evidence: " + name) from error
    require(type(result) is dict, "require one exact evidence object: " + name)
    return result


def safe_relative(value: Any, allowed: frozenset[str]) -> tuple[str, ...]:
    require(type(value) is str and value in allowed and not value.startswith("/")
            and "\\" not in value and "\x00" not in value,
            "read only a caller-pinned frozen correctness owner")
    parts = tuple(value.split("/"))
    require(parts and all(x not in {"", ".", ".."} for x in parts)
            and not any(x in {"holdout", "hidden", "benchmark", "benchmarks",
                              "performance"} for x in parts),
            "hidden cases, benchmarks, traversals, and holdout are forbidden")
    return parts


def read_owned(relative: str, expected: str, *, allowed: frozenset[str],
               maximum: int = MAX_SOURCE_BYTES) -> bytes:
    checked_hash(expected, relative)
    parts = safe_relative(relative, allowed)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory)
        opened.append(current)
        for part in parts[:-1]:
            current = os.open(part, directory, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a genuine frozen owner parent was redirected")
        fd = os.open(parts[-1], flags, dir_fd=current)
        opened.append(fd)
        before = os.fstat(fd)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < before.st_size <= maximum,
                "reject a symlinked, incomplete, or oversized frozen owner")
        chunks: list[bytes] = []
        remain = before.st_size
        while remain:
            chunk = os.read(fd, min(remain, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "a complete frozen owner was truncated")
            chunks.append(chunk)
            remain -= len(chunk)
        require(os.read(fd, 1) == b"", "reject a concealed frozen-owner suffix")
        after = os.fstat(fd)
        final = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (final.st_dev, final.st_ino, final.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "a genuine frozen owner changed during authentication")
        raw = b"".join(chunks)
        require(hashlib.sha256(raw).hexdigest() == expected,
                "an original source or evidence hash changed: " + relative)
        return raw
    finally:
        for fd in reversed(opened):
            os.close(fd)


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and not any(x == "candidates" or x.startswith("candidates.")
                        for x in sys.modules),
            "use exact isolated CPython with no imported production candidate")


def synthetic_protocol() -> dict[str, Any]:
    mode = "mandatory-exact-caller-pinned-published-source-bytes"
    rows = [{"id": x[0], "case_count": x[1], "source_path": x[2],
             "source_sha256": x[3], "matrix_sha256": x[4],
             "reference_records_sha256": x[5]}
            for x in SUITES]
    return {"schema": PROTOCOL_SCHEMA, "version": 4,
        "phase": "CANDIDATES", "status": "SOURCE FROZEN; V4 CANDIDATES NOT RUN",
        "goal_sha256": GOAL_SHA256,
        "phase1": {"inventory_path": P0_RELATIVE,
            "inventory_sha256": P0_SHA256,
            "verifier_path": P0_VERIFIER_RELATIVE,
            "verifier_sha256": P0_VERIFIER_SHA256,
            "python_path": PYTHON, "python_sha256": PYTHON_SHA256,
            "suite_count": 13, "case_execution_denominator": CASE_COUNT,
            "public_obligation_count": 73, "named_private_waiver_count": 13,
            "runnable_original_public_methods": 151,
            "complete_original_public_records": 152,
            "genuine_original_debug_skips": 1},
        "runner": {"path": SOURCE_RELATIVE, "source_sha256_mode": mode},
        "preserved_aggregate_v2": {"source_path": V2_RELATIVE,
            "source_sha256": V2_SHA256,
            "protocol_path": V2_PROTOCOL_RELATIVE,
            "protocol_sha256": V2_PROTOCOL_SHA256,
            "inventory_path": V2_DOCUMENT_RELATIVE,
            "inventory_sha256": V2_DOCUMENT_SHA256,
            "all_original_suite_routes_changed": False,
            "actual_required_case_execution_denominator": CASE_COUNT},
        "preserved_aggregate_v3": {
            "source_path": V3_RELATIVE,
            "source_sha256": V3_SHA256,
            "protocol_path": V3_PROTOCOL_RELATIVE,
            "protocol_sha256": V3_PROTOCOL_SHA256,
            "inventory_path": V3_DOCUMENT_RELATIVE,
            "inventory_sha256": V3_DOCUMENT_SHA256,
            "all_original_suite_routes_changed": False,
            "actual_required_case_execution_denominator": CASE_COUNT,
            "prior_source_modified": False},
        "preserved_candidate_v1": {"source_path": V1_RELATIVE,
            "source_sha256": V1_SHA256, "changed": False},
        "corrected_canonical_activation": {
            "source_path": ACTIVATION_RELATIVE,
            "source_sha256": ACTIVATION_SHA256,
            "protocol_path": ACTIVATION_PROTOCOL_RELATIVE,
            "protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
            "schema": ACTIVATION_SCHEMA,
            "receipt_schema": ACTIVATION_SCHEMA + "-durable-publication-receipt",
            "journal_schema": ACTIVATION_SCHEMA + "-recovery-journal",
            "intent_schema": ACTIVATION_SCHEMA + "-durable-promotion-intent",
            "promotion_mode": "recoverable-canonical-promotion",
            "candidate_import_root": str(ROOT),
            "report_sha256_mode": mode, "receipt_sha256_mode": mode,
            "recovery_journal_sha256_mode": mode,
            "activation_root_mode": "0700", "promotion_intent_mode": "0600",
            "all_role_intents_verified_before_each_candidate_invocation": True,
            "original_guard_root_rebinding_allowed": False,
            "original_guard_copy_allowed": False,
            "journal_only_crash_recovery_required": True,
            "actual_read_owner_identity_fields": list(OWNER_IDENTITY_FIELDS),
            "publication_only_durability_flags": list(DURABLE_INTENT_FLAGS),
            "publication_write_calls_positive": True,
            "actual_read_owner_has_publication_metadata": False,
            "canonical_native_original_mode_preserved": True},
        "native_source_build_v2": {
            "source_path": BUILD_RELATIVE,
            "source_sha256": BUILD_SHA256,
            "protocol_path": BUILD_PROTOCOL_RELATIVE,
            "protocol_sha256": BUILD_PROTOCOL_SHA256,
            "independent_fresh_phase_count": 2,
            "version_one_artifact_authorized": False,
            "archive_sha256_mode": mode,
            "receipt_sha256_mode": mode},
        "preserved_subinterpreter_v1": {"source_path": NESTED_V1_RELATIVE,
            "source_sha256": NESTED_V1_SHA256,
            "inventory_path": NESTED_V1_DOCUMENT_RELATIVE,
            "inventory_sha256": NESTED_V1_DOCUMENT_SHA256,
            "protocol_path": NESTED_V1_PROSE_RELATIVE,
            "protocol_sha256": NESTED_V1_PROSE_SHA256,
            "original_v2_suite_case_count": 128,
            "promotion_intents_independently_preverified": True},
        "supplemental_subinterpreter_v2": {
            "source_path": NESTED_V2_RELATIVE,
            "inventory_path": NESTED_V2_DOCUMENT_RELATIVE,
            "protocol_path": NESTED_V2_PROSE_RELATIVE,
            "source_sha256_mode": mode, "inventory_sha256_mode": mode,
            "protocol_sha256_mode": mode,
            "supplemental_case_count": 128,
            "counted_in_original_case_denominator": False,
            "actual_case_interpreter_exec_calls": 394,
            "actual_interpreters_created": 11,
            "actual_interpreters_destroyed": 11,
            "actual_initialization_interpreter_exec_calls": 11,
            "actual_guard_cleanup_interpreter_exec_calls": 11,
            "real_corrected_candidate_worker_required": True},
        "candidate_families": list(FAMILIES), "suites": rows,
        "publication": {"directory": "oracle/phase2/evidence",
            "pass_archive_template": "frozen-p0-candidate-v4-FAMILY-LABEL.json.gz",
            "pass_receipt_template": "frozen-p0-candidate-v4-FAMILY-LABEL-publication-receipt.json",
            "failure_archive_template": "frozen-p0-candidate-v4-FAMILY-LABEL-failures.json.gz",
            "failure_receipt_template": "frozen-p0-candidate-v4-FAMILY-LABEL-failures-publication-receipt.json",
            "exclusive_creation": True, "no_follow": True,
            "complete_failure_and_process_streams_required": True,
            "same_inode_readback_required": True,
            "file_and_directory_fsync_required": True},
        "historical_interop_failure": {
            "source_path": NESTED_V1_RELATIVE,
            "source_sha256": NESTED_V1_SHA256,
            "classification": "published-manual-validator-omits-corrected-durable-promotion-intents",
            "candidate_executed": False, "candidate_pass_claimed": False,
            "prior_source_modified": False,
            "resolution": "authenticate corrected source-owned activation journal and every 0600 intent before unchanged V2 and separately corrected nested V2"},
        "historical_v3_live_owner_failure": {
            "source_path": V3_RELATIVE,
            "source_sha256": V3_SHA256,
            "protocol_path": V3_PROTOCOL_RELATIVE,
            "protocol_sha256": V3_PROTOCOL_SHA256,
            "inventory_path": V3_DOCUMENT_RELATIVE,
            "inventory_sha256": V3_DOCUMENT_SHA256,
            "failure_archive_path": V3_FAILURE_ARCHIVE_RELATIVE,
            "failure_archive_sha256": V3_FAILURE_ARCHIVE_SHA256,
            "failure_receipt_path": V3_FAILURE_RECEIPT_RELATIVE,
            "failure_receipt_sha256": V3_FAILURE_RECEIPT_SHA256,
            "failure_uncompressed_sha256": V3_FAILURE_UNCOMPRESSED_SHA256,
            "candidate_family": "c",
            "label": "phase2-v3",
            "failed_stage": "authenticate all actual canonical promotion intentions",
            "failure_type": "GateError",
            "failure_message": "a mode-0600 pre-replace promotion intention was lost",
            "classification": "genuine-seven-field-read-owner-compared-to-rich-durable-publication-owner",
            "qualified_candidate_case_executions": 0,
            "supplemental_subinterpreter_case_count": 0,
            "actual_reference_workers_started": 0,
            "candidate_pass_claimed": False,
            "prior_source_modified": False,
            "native_activation_occurred": True,
            "activation_report_sha256": V3_C_ACTIVATION_REPORT_SHA256,
            "activation_receipt_sha256": V3_C_ACTIVATION_RECEIPT_SHA256,
            "recovery_journal_sha256": V3_C_RECOVERY_JOURNAL_SHA256,
            "promotion_intent_sha256": V3_C_PROMOTION_INTENT_SHA256,
            "canonical_original_restored": True,
            "restoration_receipt_sha256": V3_C_RESTORATION_RECEIPT_SHA256,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "resolution": (
                "compare all seven immutable actual owner-identity fields; "
                "require original exclusive-publication durability and write "
                "provenance on the separately announced publication owner")},
        "boundaries": {"reference_workers_started": 0,
            "stdlib_candidate_delegation_allowed": False,
            "cross_candidate_delegation_allowed": False,
            "external_regex_package_allowed": False,
            "original_guard_root_rebinding_allowed": False,
            "timing_allowed": False, "hidden_case_access_allowed": False,
            "final_holdout_authorized": False,
            "final_holdout_opened": False,
            "final_winner_selected": False, "performance": "NOT MEASURED"},
        "candidate_results": "NOT MEASURED"}


def validate_protocol(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and canonical(value) == canonical(synthetic_protocol()),
            "reject any changed frozen original suite, crash proof, or V4 boundary")
    return value


def synthetic_promotion(family: str) -> dict[str, Any]:
    checked_family(family)
    journal = hashlib.sha256(("journal-" + family).encode()).hexdigest()
    root = "/tmp/rebar-phase2-verified-native-activation-v1-" + family + "-synthetic"
    targets: dict[str, dict[str, Any]] = {}
    intents: dict[str, dict[str, Any]] = {}
    for index, role in enumerate(ROLES[family]):
        filename = role + "-" + family + ".so"
        native_owner = {
            "relative": "candidates/" + filename,
            "path": str(ROOT / "candidates" / filename),
            "sha256": hashlib.sha256(filename.encode()).hexdigest(),
            "size_bytes": 100 + index,
            "device": 10,
            "inode": 1000 + index,
            "mode": 0o755,
            "atomic_replace_completed": True,
            "adjacent_exclusive_stage_verified": True,
            "candidate_directory_fsync_completed": True,
        }
        announced = {
            "relative": "promotion-intent-" + role + ".json",
            "path": root + "/promotion-intent-" + role + ".json",
            "sha256": hashlib.sha256(
                ("intent-" + family + "-" + role).encode()
            ).hexdigest(),
            "size_bytes": 200 + index,
            "device": 22,
            "inode": 2000 + index,
            "mode": 0o600,
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "write_calls": 1,
        }
        actual_owner = {
            key: announced[key] for key in OWNER_IDENTITY_FIELDS
        }
        actual_target = {
            key: native_owner[key] for key in OWNER_IDENTITY_FIELDS
        }
        targets[role] = {
            **native_owner,
            "promotion_intent": dict(announced),
        }
        intents[role] = {
            "intent": actual_owner,
            "target": actual_target,
        }
    return {
        "family": family,
        "root": root,
        "journal_sha256": journal,
        "promotion_mode": "recoverable-canonical-promotion",
        "candidate_import_root": str(ROOT),
        "canonical_targets": targets,
        "promotion_intents": intents,
    }


def validate_intent_snapshot(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict,
        "a complete genuine promotion snapshot is mandatory",
    )
    family = checked_family(value.get("family"))
    root = value.get("root")
    require(
        type(root) is str
        and root.startswith(
            "/tmp/rebar-phase2-verified-native-activation-v1-"
            + family
            + "-"
        )
        and root.count("/") == 2
        and value.get("promotion_mode") == "recoverable-canonical-promotion"
        and value.get("candidate_import_root") == str(ROOT),
        "reject copied guards or an unjournaled noncanonical native promotion",
    )
    checked_hash(value.get("journal_sha256"), "actual durable recovery journal")
    targets = value.get("canonical_targets")
    intentions = value.get("promotion_intents")
    roles = set(ROLES[family])
    require(
        type(targets) is dict
        and set(targets) == roles
        and type(intentions) is dict
        and set(intentions) == roles,
        "require every actual canonical native target and staged intention",
    )
    identity_fields = set(OWNER_IDENTITY_FIELDS)
    publication_fields = identity_fields | set(DURABLE_INTENT_FLAGS) | {
        "write_calls"
    }
    for role in sorted(roles):
        target = targets[role]
        proof = intentions[role]
        require(
            type(target) is dict
            and type(proof) is dict
            and type(proof.get("intent")) is dict
            and type(proof.get("target")) is dict,
            "reject an absent or substituted durable native promotion role",
        )
        actual = proof["intent"]
        announced = target.get("promotion_intent")
        expected_relative = "promotion-intent-" + role + ".json"
        expected_path = root + "/" + expected_relative
        require(
            set(actual) == identity_fields
            and type(announced) is dict
            and set(announced) == publication_fields
            and all(
                type(actual.get(field)) is type(announced.get(field))
                and actual[field] == announced[field]
                for field in OWNER_IDENTITY_FIELDS
            )
            and actual["relative"] == expected_relative
            and actual["path"] == expected_path
            and type(actual["mode"]) is int
            and actual["mode"] == 0o600,
            "the actual mode-0600 intention is not the exact announced inode",
        )
        checked_hash(
            actual["sha256"],
            role + " actual durable read-owner intention",
        )
        require(
            all(
                type(actual[field]) is int and actual[field] > 0
                for field in ("size_bytes", "device", "inode")
            ),
            "a durable source-built intention lost its exact read-owner inode",
        )
        require(
            all(announced.get(flag) is True for flag in DURABLE_INTENT_FLAGS)
            and type(announced.get("write_calls")) is int
            and announced["write_calls"] > 0,
            "the original announced intent lost exclusive durable publication",
        )
        observed = proof["target"]
        require(
            set(observed) == identity_fields
            and all(
                type(target.get(field)) is type(observed.get(field))
                and target.get(field) == observed.get(field)
                for field in OWNER_IDENTITY_FIELDS
            )
            and type(target.get("relative")) is str
            and target.get("path") == str(ROOT / target["relative"])
            and type(target.get("mode")) is int
            and 0 <= target["mode"] <= 0o777
            and all(
                target.get(field) is True
                for field in (
                    "atomic_replace_completed",
                    "adjacent_exclusive_stage_verified",
                    "candidate_directory_fsync_completed",
                )
            ),
            "the promoted native inode differs from its pre-replace intention",
        )
        checked_hash(target["sha256"], role + " genuine native artifact")
        require(
            all(
                type(target.get(field)) is int and target[field] > 0
                for field in ("size_bytes", "device", "inode")
            ),
            "the source-built canonical target lost its real native identity",
        )
    return value

@contextlib.contextmanager
def source_boundary() -> Iterator[dict[str, int]]:
    counts = {key: 0 for key in ("file_reads", "file_writes", "candidate_imports",
        "reference_workers", "candidate_workers", "source_builds",
        "native_promotions", "guard_root_rebindings", "thread_starts",
        "interpreter_creations", "gc_collections", "clock_samples",
        "hidden_cases_read", "performance_files_read", "blocked_reads",
        "blocked_writes", "blocked_imports", "blocked_processes",
        "blocked_promotions", "blocked_threads", "blocked_clocks",
        "blocked_gc_collections")}
    installed: list[tuple[Any, str, Any]] = []
    def deny(field: str, reason: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            counts[field] += 1
            raise SourceOnlyEffect(reason)
        return blocked
    def install(owner: Any, name: str, field: str) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, deny(field, "source-only " + field))
    try:
        for owner, name in ((builtins,"open"),(io,"open"),(os,"open"),
                            (os,"read"),(os,"stat"),(os,"lstat"),
                            (Path,"open"),(Path,"read_bytes"),(Path,"read_text")):
            install(owner,name,"blocked_reads")
        for owner,name in ((os,"write"),(os,"unlink"),(os,"rename"),(os,"mkdir"),
                           (os,"fsync"),(Path,"write_bytes"),(Path,"write_text")):
            install(owner,name,"blocked_writes")
        install(os,"replace","blocked_promotions")
        install(importlib,"import_module","blocked_imports")
        install(subprocess,"Popen","blocked_processes")
        install(subprocess,"run","blocked_processes")
        install(threading.Thread,"start","blocked_threads")
        for name in ("time","time_ns","monotonic","monotonic_ns",
                     "perf_counter","perf_counter_ns"):
            install(time,name,"blocked_clocks")
        install(gc,"collect","blocked_gc_collections")
        yield counts
    finally:
        for owner,name,original in reversed(installed):
            setattr(owner,name,original)


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    positive: list[str] = []
    negative: list[str] = []
    def accept(label: str, callback: Callable[[], Any]) -> Any:
        try:
            result = callback()
        except Exception as error:
            raise GateError("a required synthetic positive failed: " + label) from error
        positive.append(label)
        return result
    def reject(label: str, callback: Callable[[], Any]) -> None:
        try:
            callback()
        except (GateError, SourceOnlyEffect, ValueError, TypeError, KeyError,
                OverflowError, UnicodeError, RecursionError):
            negative.append(label)
            return
        raise GateError("a mandatory hostile V4 control escaped: " + label)
    with source_boundary() as effects:
        protocol = accept("preserve-all-13-original-suites-and-31237-cases",
                          lambda: validate_protocol(synthetic_protocol()))
        accept("do-not-count-supplemental-128-cases-twice",
               lambda: require(sum(x[1] for x in SUITES) == CASE_COUNT
                   and protocol["supplemental_subinterpreter_v2"]
                       ["counted_in_original_case_denominator"] is False,
                   "never change the original 31,237 denominator"))
        for index, suite in enumerate(SUITES):
            accept("retain-original-source-owner-" + suite[0],
                   lambda suite=suite: checked_hash(suite[3], suite[0]))
            for key in ("id","case_count","source_path","source_sha256",
                        "matrix_sha256","reference_records_sha256"):
                def alter(index: int=index,key: str=key) -> Any:
                    forged=synthetic_protocol()
                    old=forged["suites"][index][key]
                    forged["suites"][index][key]=(old+1 if type(old) is int
                        else "0"*64 if key.endswith("sha256") else old+"-forged")
                    return validate_protocol(forged)
                reject("reject-suite-"+suite[0]+"-"+key,alter)
            def omit(index: int=index) -> Any:
                forged=synthetic_protocol();del forged["suites"][index]
                return validate_protocol(forged)
            reject("reject-omitted-original-suite-"+suite[0],omit)
            if index+1<len(SUITES):
                def reorder(index: int=index) -> Any:
                    forged=synthetic_protocol()
                    forged["suites"][index:index+2]=reversed(forged["suites"][index:index+2])
                    return validate_protocol(forged)
                reject("reject-reordered-original-suite-"+suite[0],reorder)
        for name in ("phase1","preserved_aggregate_v2","preserved_aggregate_v3",
                     "preserved_candidate_v1",
                     "corrected_canonical_activation","native_source_build_v2",
                     "preserved_subinterpreter_v1",
                     "supplemental_subinterpreter_v2","publication",
                     "historical_interop_failure",
                     "historical_v3_live_owner_failure","boundaries"):
            for key in protocol[name]:
                def replace(name: str=name,key: str=key) -> Any:
                    forged=synthetic_protocol();old=forged[name][key]
                    forged[name][key]=(not old if type(old) is bool else
                        old+1 if type(old) is int else
                        old+"-forged" if type(old) is str else None)
                    return validate_protocol(forged)
                reject("reject-"+name+"-"+key,replace)
        for family in FAMILIES:
            fixture=synthetic_promotion(family)
            accept(
                "verify-all-genuine-lean-and-durable-owners-" + family,
                lambda fixture=fixture: validate_intent_snapshot(fixture),
            )
            accept(
                "preserve-original-native-owner-mode-" + family,
                lambda fixture=fixture: require(
                    all(
                        entry["mode"] == 0o755
                        for entry in fixture["canonical_targets"].values()
                    ),
                    "never invent mode 0600 for a genuine canonical native target",
                ),
            )
            accept(
                "distinguish-actual-seven-field-read-owner-" + family,
                lambda fixture=fixture: require(
                    all(
                        set(fixture["promotion_intents"][role]["intent"])
                        == set(OWNER_IDENTITY_FIELDS)
                        and fixture["promotion_intents"][role]["intent"]
                        != fixture["canonical_targets"][role]["promotion_intent"]
                        and all(
                            fixture["promotion_intents"][role]["intent"][field]
                            == fixture["canonical_targets"][role]
                               ["promotion_intent"][field]
                            for field in OWNER_IDENTITY_FIELDS
                        )
                        for role in ROLES[family]
                    ),
                    "model the exact real read owner separately from publication",
                ),
            )
            accept(
                "retain-all-original-durable-publication-flags-" + family,
                lambda fixture=fixture: require(
                    all(
                        all(
                            fixture["canonical_targets"][role]
                            ["promotion_intent"].get(flag) is True
                            for flag in DURABLE_INTENT_FLAGS
                        )
                        and type(
                            fixture["canonical_targets"][role]
                            ["promotion_intent"].get("write_calls")
                        ) is int
                        and fixture["canonical_targets"][role]
                            ["promotion_intent"]["write_calls"] > 0
                        for role in ROLES[family]
                    ),
                    "preserve original genuine exclusive publication evidence",
                ),
            )
            for field in ("family","root","journal_sha256","promotion_mode",
                          "candidate_import_root","canonical_targets",
                          "promotion_intents"):
                def forge_root(field: str=field,family: str=family) -> Any:
                    actual=synthetic_promotion(family);old=actual[field]
                    actual[field]=(old+"-forged" if type(old) is str else {})
                    return validate_intent_snapshot(actual)
                reject("reject-"+family+"-activation-"+field,forge_root)
            for role in sorted(ROLES[family]):
                for field in ("relative","path","sha256","size_bytes","device",
                              "inode","mode","atomic_replace_completed",
                              "adjacent_exclusive_stage_verified",
                              "candidate_directory_fsync_completed"):
                    def forge_target(family: str=family,role: str=role,
                                     field: str=field) -> Any:
                        actual=synthetic_promotion(family)
                        old=actual["canonical_targets"][role][field]
                        actual["canonical_targets"][role][field]=(
                            not old if type(old) is bool else old+1
                            if type(old) is int else old+"-forged")
                        return validate_intent_snapshot(actual)
                    reject("reject-"+family+"-"+role+"-target-"+field,forge_target)
                for field in OWNER_IDENTITY_FIELDS:
                    def forge_actual_owner(
                        family: str = family,
                        role: str = role,
                        field: str = field,
                    ) -> Any:
                        actual = synthetic_promotion(family)
                        owner = actual["promotion_intents"][role]["intent"]
                        old = owner[field]
                        owner[field] = (
                            old + 1 if type(old) is int else old + "-forged"
                        )
                        return validate_intent_snapshot(actual)
                    reject(
                        "reject-" + family + "-" + role
                        + "-actual-read-owner-" + field,
                        forge_actual_owner,
                    )

                    def omit_actual_owner(
                        family: str = family,
                        role: str = role,
                        field: str = field,
                    ) -> Any:
                        actual = synthetic_promotion(family)
                        del actual["promotion_intents"][role]["intent"][field]
                        return validate_intent_snapshot(actual)
                    reject(
                        "reject-" + family + "-" + role
                        + "-missing-actual-read-owner-" + field,
                        omit_actual_owner,
                    )

                    def forge_announced_owner(
                        family: str = family,
                        role: str = role,
                        field: str = field,
                    ) -> Any:
                        actual = synthetic_promotion(family)
                        owner = actual["canonical_targets"][role][
                            "promotion_intent"
                        ]
                        old = owner[field]
                        owner[field] = (
                            old + 1 if type(old) is int else old + "-forged"
                        )
                        return validate_intent_snapshot(actual)
                    reject(
                        "reject-" + family + "-" + role
                        + "-announced-publication-owner-" + field,
                        forge_announced_owner,
                    )

                    def omit_announced_owner(
                        family: str = family,
                        role: str = role,
                        field: str = field,
                    ) -> Any:
                        actual = synthetic_promotion(family)
                        del actual["canonical_targets"][role][
                            "promotion_intent"
                        ][field]
                        return validate_intent_snapshot(actual)
                    reject(
                        "reject-" + family + "-" + role
                        + "-missing-announced-owner-" + field,
                        omit_announced_owner,
                    )

                    def forge_observed_native(
                        family: str = family,
                        role: str = role,
                        field: str = field,
                    ) -> Any:
                        actual = synthetic_promotion(family)
                        owner = actual["promotion_intents"][role]["target"]
                        old = owner[field]
                        owner[field] = (
                            old + 1 if type(old) is int else old + "-forged"
                        )
                        return validate_intent_snapshot(actual)
                    reject(
                        "reject-" + family + "-" + role
                        + "-actual-canonical-native-owner-" + field,
                        forge_observed_native,
                    )

                for flag in DURABLE_INTENT_FLAGS:
                    for poison_name, poison in (
                        ("false", False),
                        ("zero", 0),
                        ("one", 1),
                        ("none", None),
                    ):
                        def forge_publication_flag(
                            family: str = family,
                            role: str = role,
                            flag: str = flag,
                            poison: Any = poison,
                        ) -> Any:
                            actual = synthetic_promotion(family)
                            actual["canonical_targets"][role][
                                "promotion_intent"
                            ][flag] = poison
                            return validate_intent_snapshot(actual)
                        reject(
                            "reject-" + family + "-" + role
                            + "-announced-" + flag + "-" + poison_name,
                            forge_publication_flag,
                        )

                    def omit_publication_flag(
                        family: str = family,
                        role: str = role,
                        flag: str = flag,
                    ) -> Any:
                        actual = synthetic_promotion(family)
                        del actual["canonical_targets"][role][
                            "promotion_intent"
                        ][flag]
                        return validate_intent_snapshot(actual)
                    reject(
                        "reject-" + family + "-" + role
                        + "-missing-announced-" + flag,
                        omit_publication_flag,
                    )

                    def forge_lean_with_publication_flag(
                        family: str = family,
                        role: str = role,
                        flag: str = flag,
                    ) -> Any:
                        actual = synthetic_promotion(family)
                        actual["promotion_intents"][role][
                            "intent"
                        ][flag] = True
                        return validate_intent_snapshot(actual)
                    reject(
                        "reject-" + family + "-" + role
                        + "-publication-flag-in-actual-read-owner-" + flag,
                        forge_lean_with_publication_flag,
                    )

                for poison_name, poison in (
                    ("false", False),
                    ("zero", 0),
                    ("negative", -1),
                    ("none", None),
                    ("string", "1"),
                ):
                    def forge_write_calls(
                        family: str = family,
                        role: str = role,
                        poison: Any = poison,
                    ) -> Any:
                        actual = synthetic_promotion(family)
                        actual["canonical_targets"][role][
                            "promotion_intent"
                        ]["write_calls"] = poison
                        return validate_intent_snapshot(actual)
                    reject(
                        "reject-" + family + "-" + role
                        + "-announced-write-calls-" + poison_name,
                        forge_write_calls,
                    )

                def omit_write_calls(
                    family: str = family,
                    role: str = role,
                ) -> Any:
                    actual = synthetic_promotion(family)
                    del actual["canonical_targets"][role][
                        "promotion_intent"
                    ]["write_calls"]
                    return validate_intent_snapshot(actual)
                reject(
                    "reject-" + family + "-" + role
                    + "-missing-announced-write-calls",
                    omit_write_calls,
                )

                def copy_publication_owner_into_read_owner(
                    family: str = family,
                    role: str = role,
                ) -> Any:
                    actual = synthetic_promotion(family)
                    actual["promotion_intents"][role]["intent"] = dict(
                        actual["canonical_targets"][role]["promotion_intent"]
                    )
                    return validate_intent_snapshot(actual)
                reject(
                    "reject-" + family + "-" + role
                    + "-copying-durable-publication-into-actual-read-owner",
                    copy_publication_owner_into_read_owner,
                )

                def omit_intent(family: str=family,role: str=role) -> Any:
                    actual=synthetic_promotion(family)
                    del actual["promotion_intents"][role]
                    return validate_intent_snapshot(actual)
                reject("reject-"+family+"-omitted-pre-replace-intent-"+role,
                       omit_intent)
        for value in (None,"","stdlib","_sre","regex","go","all",0,[],{}):
            reject("reject-foreign-candidate-"+repr(value),
                   lambda value=value:checked_family(value))
        for raw in (b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',
                    b'{"x":-Infinity}',b"[]",b"null",b"",b"{",b"\xff"):
            reject("reject-invalid-complete-json-"+repr(raw),
                   lambda raw=raw:decode_document(raw,"synthetic"))
        accept("preserve-escaped-original-unicode-surrogates",
               lambda:require(decode_document(b'{"x":"\\ud800"}',"synthetic")["x"]
                   =="\ud800","preserve exact frozen Python observations"))
        allowed=frozenset({P0_RELATIVE})
        accept("retain-exact-frozen-inventory-safe-path",
               lambda:safe_relative(P0_RELATIVE,allowed))
        for path in ("../GOAL.md","/etc/passwd","holdout/cases.json",
                     "hidden/cases.json","benchmarks/final.json",
                     "performance/results.json","candidates/engine.so","",None,0):
            reject("reject-hidden-or-unsafe-path-"+repr(path),
                   lambda path=path:safe_relative(path,allowed))
        for label in ("v4","rust-v4","c-1","zig-42"):
            accept("accept-safe-evidence-label-"+label,
                   lambda label=label:checked_label(label))
        for label in (None,"","../outside","/tmp/x","UPPER","white space",1,"x"*49):
            reject("reject-unsafe-evidence-label-"+repr(label),
                   lambda label=label:checked_label(label))
        for name,action in (
            ("file-read",lambda:builtins.open(str(ROOT/"GOAL.md"),"rb")),
            ("directory-read",lambda:os.open(str(ROOT),os.O_RDONLY)),
            ("file-write",lambda:Path("forbidden").write_text("forbidden")),
            ("candidate-import",lambda:importlib.import_module("candidates.rust_candidate")),
            ("reference-process",lambda:subprocess.Popen([PYTHON])),
            ("candidate-process",lambda:subprocess.run([PYTHON])),
            ("native-promotion",lambda:os.replace("forbidden-a","forbidden-b")),
            ("real-thread",lambda:threading.Thread(target=lambda:None).start()),
            ("wall-clock",lambda:time.time()),
            ("performance-clock",lambda:time.perf_counter()),
            ("garbage-collection",lambda:gc.collect())):
            reject("block-source-only-"+name,action)
        require(len(positive)>=30 and len(negative)>=450,
                "require complete independent promotion-intent attack controls")
        require(effects["blocked_reads"]>=2 and effects["blocked_writes"]>=1
                and effects["blocked_imports"]>=1 and effects["blocked_processes"]>=2
                and effects["blocked_promotions"]>=1 and effects["blocked_threads"]>=1
                and effects["blocked_clocks"]>=2
                and effects["blocked_gc_collections"]>=1,
                "exercise every actual zero-effect source-only boundary")
        captured=dict(effects)
    return {"schema":SCHEMA+"-source-only-self-test","status":"PASS",
        "python":"3.14.6","source_only":True,"goal_sha256":GOAL_SHA256,
        "phase1_inventory_sha256":P0_SHA256,
        "preserved_aggregate_v2_sha256":V2_SHA256,
        "preserved_aggregate_v3_sha256":V3_SHA256,
        "preserved_v3_failure_archive_sha256":V3_FAILURE_ARCHIVE_SHA256,
        "preserved_v3_failure_receipt_sha256":V3_FAILURE_RECEIPT_SHA256,
        "actual_read_owner_identity_field_count":len(OWNER_IDENTITY_FIELDS),
        "original_durable_publication_flag_count":len(DURABLE_INTENT_FLAGS),
        "canonical_native_mode_forced_to_0600":False,
        "corrected_activation_sha256":ACTIVATION_SHA256,
        "suite_count":len(SUITES),"case_execution_denominator":CASE_COUNT,
        "supplemental_interpreter_cases_not_double_counted":128,
        "candidate_families":list(FAMILIES),
        "synthetic_positive_control_count":len(positive),
        "synthetic_rejection_control_count":len(negative),
        "positive_controls":positive,"rejection_controls":negative,
        "source_only_effects":captured,
        "actual_reference_workers":0,"actual_candidate_workers":0,
        "actual_candidate_imports":0,"actual_source_builds":0,
        "actual_native_promotions":0,"actual_guard_root_rebindings":0,
        "actual_interpreter_creations":0,"actual_thread_starts":0,
        "clock_samples":0,"timing_trials_run":0,
        "benchmark_files_read":0,"hidden_cases_read":0,
        "performance":"NOT MEASURED","final_holdout_authorized":False,
        "candidate_qualified_for_hidden_benchmark":False,
        "final_winner_selected":False}


def import_frozen(relative: str, expected: str,
                  allowed: frozenset[str]) -> types.ModuleType:
    read_owned(relative,expected,allowed=allowed)
    name=relative.removesuffix(".py").replace("/",".")
    module=importlib.import_module(name)
    require(type(module) is types.ModuleType and module.__name__==name
            and os.path.abspath(module.__file__)==str(ROOT/relative),
            "reject a rebound, copied, or replaced canonical source owner")
    read_owned(relative,expected,allowed=allowed)
    return module


def verify_all_promotion_intents(options: argparse.Namespace,
                                 activation: types.ModuleType) -> dict[str, Any]:
    family=checked_family(options.candidate)
    root=activation.checked_private_root(options.activation_root,family,build=False)
    arguments={"family":family,"activation_root":root,
        "activation_source_sha256":ACTIVATION_SHA256,
        "activation_protocol_sha256":ACTIVATION_PROTOCOL_SHA256,
        "activation_report_sha256":checked_hash(options.activation_report_sha256,"activation report"),
        "activation_receipt_sha256":checked_hash(options.activation_receipt_sha256,"activation receipt")}
    report_raw,report_owner=activation.read_owned(root,"activation-report.json",
        arguments["activation_report_sha256"],maximum=MAX_SOURCE_BYTES,private=True)
    receipt_raw,receipt_owner=activation.read_owned(root,"activation-receipt.json",
        arguments["activation_receipt_sha256"],maximum=MAX_SOURCE_BYTES,private=True)
    journal_hash=checked_hash(options.recovery_journal_sha256,
                              "actual mode-0600 recovery journal")
    journal_raw,journal_owner=activation.read_owned(root,"recovery-journal.json",
        journal_hash,maximum=MAX_SOURCE_BYTES,private=True)
    require(report_owner.get("mode")==0o600
            and receipt_owner.get("mode")==0o600
            and journal_owner.get("mode")==0o600,
            "all actual canonical crash-proof files must be owner-only mode 0600")
    report=activation.decode_document(report_raw,"corrected canonical report")
    receipt=activation.decode_document(receipt_raw,"corrected durable receipt")
    journal=activation.decode_document(journal_raw,"pinned pre-promotion journal")
    proved=activation.validate_activation_documents(report,receipt,journal,
                                                    arguments=arguments)
    require(type(proved) is dict and proved.get("status")=="PASS"
            and proved.get("family")==family
            and proved.get("candidate_import_root")==str(ROOT),
            "the actual corrected activation owner rejected its full evidence")
    announced_journal=report.get("recovery_journal")
    require(type(announced_journal) is dict
            and activation.same_owner(announced_journal,journal_owner),
            "the caller-pinned mode-0600 recovery journal changed its actual inode")
    intents=activation.authenticate_promotion_intents(root,journal,journal_hash)
    snapshot={"family":family,"root":root,"journal_sha256":journal_hash,
              "promotion_mode":"recoverable-canonical-promotion",
              "candidate_import_root":str(ROOT),
              "canonical_targets":proved["canonical_targets"],
              "promotion_intents":intents}
    validate_intent_snapshot(snapshot)
    provenance=proved.get("source_build_v2")
    require(type(provenance) is dict
            and provenance.get("archive_sha256")==options.build_archive_sha256
            and provenance.get("receipt_sha256")==options.build_receipt_sha256
            and provenance.get("independent_fresh_phase_count")==2,
            "require the caller-pinned two-phase source-built actual native engine")
    build_root=activation.checked_private_root(provenance.get("build_root"),
                                                family,build=True)
    for role in sorted(ROLES[family]):
        target=proved["canonical_targets"][role]
        intention=intents[role]
        require(activation.same_owner(intention["intent"],
                                      target["promotion_intent"])
                and activation.same_owner(intention["target"],target),
                "the actual durable intent does not own the promoted target inode")
        current=activation.current_canonical(target["relative"])
        require(type(current) is tuple and len(current)==2
                and activation.same_owner(current[1],target),
                "the actual canonical native inode changed since promotion")
        phases=target.get("source_build_phases")
        require(type(phases) is list and len(phases)==2,
                "both actual distinct source-build phase native files are mandatory")
        actual_phases=[]
        for number,phase in enumerate(phases):
            expected_prefix=("reference-a","reference-b")[number]+"/native/"
            require(type(phase) is dict
                    and type(phase.get("relative")) is str
                    and phase["relative"].startswith(expected_prefix),
                    "read only the exact source-built frozen phase-native owner")
            _,actual_phase=activation.read_owned(
                build_root,phase["relative"],target["sha256"],
                maximum=activation.MAX_BINARY_BYTES,
                exact_size=target["size_bytes"],private=True)
            require(activation.same_owner(actual_phase,phase),
                    "a genuinely source-built phase file changed its exact inode")
            actual_phases.append(actual_phase)
        require((actual_phases[0]["device"],actual_phases[0]["inode"])
                !=(actual_phases[1]["device"],actual_phases[1]["inode"]),
                "never count one native build inode as two fresh source phases")
    for relative,record in proved["original_guard_sources"].items():
        require(type(record) is dict,
                "every original matcher guard must remain unchanged")
        _,original=activation.read_owned(str(ROOT),relative,record["sha256"],
                                         maximum=MAX_SOURCE_BYTES,private=False)
        require(activation.same_owner(original,record),
                "an immutable original matcher guard was replaced or rebound")
    source_records=report.get("source_owners")
    require(type(source_records) is dict and bool(source_records),
            "the complete actual original candidate source closure is mandatory")
    for relative,record in source_records.items():
        require(type(record) is dict,
                "a genuine source-built candidate source owner was concealed")
        _,actual=activation.read_owned(str(ROOT),relative,record["sha256"],
                                       maximum=MAX_SOURCE_BYTES,private=False)
        require(activation.same_owner(actual,record),
                "a complete native family source changed after source building")
    return {"schema":SCHEMA+"-independently-verified-durable-promotion-intents",
        "status":"PASS","family":family,
        "activation_report":report_owner,"activation_receipt":receipt_owner,
        "recovery_journal":journal_owner,"source_build_v2":provenance,
        "canonical_targets":proved["canonical_targets"],
        "backup_entries":proved["backup_entries"],
        "original_guard_sources":proved["original_guard_sources"],
        "promotion_intents":intents,"all_native_roles_intent_verified":True,
        "candidate_import_root":str(ROOT)}


def process_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw)<=MAX_STREAM_BYTES,
            "retain complete actual candidate process output")
    return {"encoding":"base64","data":base64.b64encode(raw).decode("ascii"),
            "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
            "complete":True}


def invoke(command: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    require(type(command) is list and command[:3]==[PYTHON,"-I","-B"],
            "launch only one frozen isolated canonical candidate gate")
    process=subprocess.Popen(command,stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=str(ROOT),shell=False,
        env={"PYTHONDONTWRITEBYTECODE":"1","PYTHONHASHSEED":"0",
             "LC_ALL":"C","PATH":"/usr/bin:/bin"})
    try:
        out,err=process.communicate(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        process.kill();out,err=process.communicate()
        evidence={"pid":process.pid,"returncode":process.returncode,
            "stdout":process_stream(out),"stderr":process_stream(err),
            "timed_out":True,"signal":-process.returncode
            if process.returncode is not None and process.returncode<0 else None}
        raise WorkerFailure("an actual frozen candidate worker timed out",
                            evidence) from error
    evidence={"pid":process.pid,"returncode":process.returncode,
              "stdout":process_stream(out),"stderr":process_stream(err),
              "timed_out":False,"signal":-process.returncode
              if process.returncode<0 else None}
    if err!=b"" or process.returncode!=0:
        raise WorkerFailure(
            "retain and reject a failed actual isolated native correctness worker",
            evidence)
    return decode_document(out,"complete frozen actual candidate output"),evidence


def v2_command(options: argparse.Namespace) -> list[str]:
    result=[PYTHON,"-I","-B",str(ROOT/V2_RELATIVE),"--run",
        "--candidate",checked_family(options.candidate),
        "--label",checked_label(options.label),
        "--source-sha256",V2_SHA256,
        "--protocol-sha256",V2_PROTOCOL_SHA256,
        "--document-sha256",V2_DOCUMENT_SHA256,
        "--subinterpreter-source-sha256",NESTED_V1_SHA256,
        "--subinterpreter-protocol-sha256",NESTED_V1_DOCUMENT_SHA256,
        "--subinterpreter-explanation-sha256",NESTED_V1_PROSE_SHA256,
        "--build-label",checked_label(options.build_label),
        "--build-archive-sha256",checked_hash(options.build_archive_sha256,"V2 archive"),
        "--build-receipt-sha256",checked_hash(options.build_receipt_sha256,"V2 receipt"),
        "--activation-root",options.activation_root,
        "--activation-source-sha256",ACTIVATION_SHA256,
        "--activation-protocol-sha256",ACTIVATION_PROTOCOL_SHA256,
        "--activation-report-sha256",options.activation_report_sha256,
        "--activation-receipt-sha256",options.activation_receipt_sha256,
        "--candidate-source-sha256",options.candidate_source_sha256,
        "--native-engine-sha256",options.native_engine_sha256,
        "--native-bridge-sha256",options.native_bridge_sha256]
    for item in options.owned_source_sha256:
        result.extend(("--owned-source-sha256",item))
    return result


def nested_v2_command(options: argparse.Namespace) -> list[str]:
    label=checked_label(options.label+"-subinterp-v2")
    result=[PYTHON,"-I","-B",str(ROOT/NESTED_V2_RELATIVE),
        "--record-candidate","--family",checked_family(options.candidate),
        "--label",label,
        "--source-sha256",checked_hash(options.nested_v2_source_sha256,"nested V2 source"),
        "--protocol-sha256",checked_hash(options.nested_v2_protocol_sha256,"nested V2 inventory"),
        "--explanation-sha256",checked_hash(options.nested_v2_explanation_sha256,"nested V2 protocol"),
        "--v1-source-sha256",NESTED_V1_SHA256,
        "--v1-protocol-sha256",NESTED_V1_DOCUMENT_SHA256,
        "--v1-explanation-sha256",NESTED_V1_PROSE_SHA256,
        "--build-label",checked_label(options.build_label),
        "--build-source-sha256",BUILD_SHA256,
        "--build-protocol-sha256",BUILD_PROTOCOL_SHA256,
        "--build-archive-sha256",options.build_archive_sha256,
        "--build-receipt-sha256",options.build_receipt_sha256,
        "--activation-root",options.activation_root,
        "--activation-source-sha256",ACTIVATION_SHA256,
        "--activation-protocol-sha256",ACTIVATION_PROTOCOL_SHA256,
        "--activation-report-sha256",options.activation_report_sha256,
        "--activation-receipt-sha256",options.activation_receipt_sha256,
        "--candidate-source-sha256",options.candidate_source_sha256,
        "--native-engine-sha256",options.native_engine_sha256,
        "--native-bridge-sha256",options.native_bridge_sha256]
    for item in options.owned_source_sha256:
        result.extend(("--owned-source-sha256",item))
    return result


def published_archive(value: Any,name: str) -> dict[str, Any]:
    require(type(value) is dict,"require the complete durable actual "+name)
    relative=value.get("relative",value.get("path"))
    expected=checked_hash(value.get("sha256"),name)
    raw=read_owned(relative,expected,allowed=frozenset({relative}),
                   maximum=MAX_ARCHIVE_BYTES)
    claimed=value.get("bytes",value.get("size_bytes"))
    require(type(claimed) is int and claimed==len(raw),
            "the independently published full candidate result was truncated")
    return {"relative":relative,"sha256":expected,"bytes":len(raw)}


def validate_supplemental_result(result: dict[str, Any],
                                 options: argparse.Namespace) -> dict[str, Any]:
    nested_schema="rebar-owned-candidate-subinterpreters-v2"
    label=checked_label(options.label+"-subinterp-v2")
    require(type(result) is dict
            and result.get("schema")==nested_schema+"-published-candidate-result"
            and result.get("status")=="PASS"
            and result.get("candidate_family")==options.candidate
            and result.get("label")==label
            and result.get("failure_preserved") is False
            and result.get("directory_fsync") is True
            and result.get("performance")=="NOT MEASURED"
            and result.get("holdout")=="NOT OPENED",
            "require the genuine corrected complete supplemental publication")
    archive=published_archive(result.get("archive"),
                              "supplemental corrected interpreter archive")
    receipt=published_archive(result.get("receipt"),
                              "supplemental corrected interpreter receipt")
    compressed=read_owned(archive["relative"],archive["sha256"],
                          allowed=frozenset({archive["relative"]}),
                          maximum=MAX_ARCHIVE_BYTES)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed),mode="rb") as source:
        plain=source.read(MAX_NESTED_REPORT_BYTES+1)
    require(0<len(plain)<=MAX_NESTED_REPORT_BYTES,
            "fully retain and bound the genuine supplemental interpreter report")
    report=decode_document(plain,"complete corrected supplemental report")
    require(canonical(report)==plain
            and report.get("schema")==nested_schema+"-candidate-evaluation"
            and report.get("status")=="PASS"
            and report.get("candidate_family")==options.candidate
            and report.get("label")==label
            and report.get("source_sha256")==options.nested_v2_source_sha256
            and report.get("protocol_sha256")==options.nested_v2_protocol_sha256
            and report.get("explanation_sha256")==options.nested_v2_explanation_sha256
            and report.get("v1_source_sha256")==NESTED_V1_SHA256
            and report.get("v1_protocol_sha256")==NESTED_V1_DOCUMENT_SHA256
            and report.get("activation_report_sha256")==options.activation_report_sha256
            and report.get("activation_receipt_sha256")==options.activation_receipt_sha256
            and type(report.get("supplemental_case_count")) is int
            and report["supplemental_case_count"]==128
            and report.get("phase1_case_execution_denominator")==CASE_COUNT
            and report.get("supplemental_cases_added_to_phase1_denominator") is False
            and report.get("failure") is None
            and report.get("performance")=="NOT MEASURED"
            and report.get("holdout")=="NOT OPENED",
            "authenticate the exact complete caller-pinned 128-case nested report")
    worker=report.get("worker")
    process=report.get("worker_process")
    corrected=report.get("corrected_activation")
    audit=report.get("static_independence_audit")
    require(type(worker) is dict and type(process) is dict
            and type(corrected) is dict and type(audit) is dict
            and worker.get("schema")==nested_schema+"-actual-worker"
            and worker.get("status")=="PASS"
            and type(worker.get("pid")) is int and worker["pid"]>0
            and process.get("pid")==worker["pid"]
            and process.get("returncode")==0
            and process.get("signal") is None
            and process.get("timed_out") is False
            and process.get("process_reaped") is True
            and canonical(worker.get("corrected_promotion"))==canonical(corrected)
            and worker.get("previous_original_source_sha256")==NESTED_V1_SHA256
            and worker.get("previous_original_protocol_sha256")
                ==NESTED_V1_DOCUMENT_SHA256
            and type(audit.get("report")) is dict
            and audit["report"].get("static_independence")=="PASS",
            "require one real corrected native worker and its complete static audit")
    for key,expected in (
        ("case_count",128),
        ("actual_case_interpreter_exec_calls",394),
        ("actual_initialization_interpreter_exec_calls",11),
        ("actual_guard_cleanup_interpreter_exec_calls",11),
        ("actual_interpreters_created",11),
        ("actual_interpreters_destroyed",11),
    ):
        require(type(worker.get(key)) is int and worker[key]==expected,
                "require every complete actual supplemental lifecycle: "+key)
    records=worker.get("records")
    require(type(records) is list and len(records)==128
            and canonical(records)==canonical(worker.get("peer_records"))
            and canonical(records)==canonical(worker.get("repeated_a_records")),
            "retain every genuine supplemental A/B/A interpreter observation")
    receipt_raw=read_owned(receipt["relative"],receipt["sha256"],
                           allowed=frozenset({receipt["relative"]}),
                           maximum=MAX_SOURCE_BYTES)
    document=decode_document(receipt_raw,"complete nested durable receipt")
    require(canonical(document)==receipt_raw
            and document.get("schema")==nested_schema+"-publication-receipt"
            and document.get("status")=="PASS"
            and document.get("result_status")=="PASS"
            and document.get("candidate_family")==options.candidate
            and document.get("label")==label
            and document.get("source_sha256")==options.nested_v2_source_sha256
            and document.get("protocol_sha256")==options.nested_v2_protocol_sha256
            and document.get("explanation_sha256")==options.nested_v2_explanation_sha256
            and document.get("v1_source_sha256")==NESTED_V1_SHA256
            and document.get("v1_protocol_sha256")==NESTED_V1_DOCUMENT_SHA256
            and document.get("activation_source_sha256")==ACTIVATION_SHA256
            and document.get("activation_protocol_sha256")==ACTIVATION_PROTOCOL_SHA256
            and document.get("activation_report_sha256")==options.activation_report_sha256
            and document.get("activation_receipt_sha256")==options.activation_receipt_sha256
            and document.get("archive_relative")==archive["relative"]
            and document.get("archive_sha256")==archive["sha256"]
            and document.get("archive_bytes")==archive["bytes"]
            and document.get("uncompressed_sha256")==hashlib.sha256(plain).hexdigest()
            and document.get("uncompressed_bytes")==len(plain)
            and document.get("archive_directory_fsync") is True
            and document.get("performance")=="NOT MEASURED"
            and document.get("holdout")=="NOT OPENED",
            "authenticate the genuine corrected nested receipt and archive bytes")
    return {"archive":archive,"receipt":receipt,
        "actual_supplemental_case_count":128,
        "actual_case_interpreter_exec_calls":394,
        "actual_initialization_interpreter_exec_calls":11,
        "actual_guard_cleanup_interpreter_exec_calls":11,
        "actual_interpreters_created":11,
        "actual_interpreters_destroyed":11,
        "all_complete_a_b_a_records_verified":True,
        "counted_in_original_case_denominator":False}


def publish_actual_report(report: dict[str, Any], options: argparse.Namespace,
                          v2: types.ModuleType) -> dict[str, Any]:
    require(type(report) is dict
            and report.get("schema")==SCHEMA+"-actual-complete-candidate"
            and report.get("status") in ("PASS","FAIL"),
            "publish only one complete genuine actual V4 candidate report")
    family=checked_family(options.candidate)
    label=checked_label(options.label)
    require(report.get("candidate_family")==family
            and report.get("label")==label
            and callable(getattr(v2,"write_fresh_evidence",None)),
            "use only the frozen verified exclusive V2 evidence writer")
    failure=report["status"]!="PASS"
    stem="frozen-p0-candidate-v4-"+family+"-"+label
    if failure:
        stem+="-failures"
    plain=canonical(report)
    archive=gzip.compress(plain,compresslevel=9,mtime=0)
    require(0<len(archive)<=MAX_ARCHIVE_BYTES,
            "retain the complete bounded V4 candidate failure or result")
    flags=(os.O_RDONLY|getattr(os,"O_DIRECTORY",0)
           |getattr(os,"O_NOFOLLOW",0)|getattr(os,"O_CLOEXEC",0))
    directory=os.open(str(ROOT/"oracle/phase2/evidence"),flags)
    try:
        compressed=v2.write_fresh_evidence(directory,stem+".json.gz",archive)
        os.fsync(directory)
        compressed_record=published_archive(compressed,"V4 full result archive")
        receipt_document={
            "schema":SCHEMA+"-durable-publication-receipt",
            "status":"PASS","candidate_status":report["status"],
            "candidate_family":family,"label":label,
            "source_sha256":checked_hash(options.source_sha256,"V4 source"),
            "protocol_sha256":checked_hash(options.protocol_sha256,"V4 protocol"),
            "document_sha256":checked_hash(options.document_sha256,"V4 inventory"),
            "archive":compressed,
            "uncompressed_sha256":hashlib.sha256(plain).hexdigest(),
            "uncompressed_bytes":len(plain),
            "archive_directory_fsync_completed":True,
            "failure_preserved":failure,
            "all_actual_process_streams_preserved":True,
            "hidden_cases_read":0,"benchmark_files_read":0,
            "clock_samples":0,"timing_trials_run":0,
            "performance":"NOT MEASURED","final_holdout_authorized":False,
            "candidate_qualified_for_hidden_benchmark":False,
            "final_winner_selected":False}
        receipt=v2.write_fresh_evidence(directory,
            stem+"-publication-receipt.json",canonical(receipt_document))
        os.fsync(directory)
        receipt_record=published_archive(receipt,"V4 durable result receipt")
    finally:
        os.close(directory)
    return {"schema":SCHEMA+"-published-complete-candidate",
        "status":report["status"],"candidate_family":family,"label":label,
        "suite_count":13,"case_execution_denominator":CASE_COUNT,
        "qualified_candidate_case_executions":
            report["qualified_candidate_case_executions"],
        "supplemental_subinterpreter_case_count":
            report["supplemental_subinterpreter_case_count"],
        "supplemental_cases_added_to_original_denominator":False,
        "candidate_qualified":report["candidate_qualified"],
        "complete_archive":compressed,"complete_publication_receipt":receipt,
        "independently_reverified_archive":compressed_record,
        "independently_reverified_receipt":receipt_record,
        "all_mismatches_crashes_timeouts_and_process_streams_preserved":True,
        "failure_preserved":failure,"actual_reference_workers_started":0,
        "clock_samples":0,"timing_trials_run":0,"benchmark_files_read":0,
        "hidden_cases_read":0,"performance":"NOT MEASURED",
        "final_holdout_authorized":False,
        "candidate_qualified_for_hidden_benchmark":False,
        "final_winner_selected":False}


def validate_preserved_v3_failure(
    archive_raw: bytes,
    receipt_raw: bytes,
) -> dict[str, Any]:
    require(
        type(archive_raw) is bytes
        and 0 < len(archive_raw) <= MAX_ARCHIVE_BYTES
        and hashlib.sha256(archive_raw).hexdigest() == V3_FAILURE_ARCHIVE_SHA256,
        "preserve the exact published actual version-three failure archive",
    )
    plain = gzip.decompress(archive_raw)
    require(
        0 < len(plain) <= MAX_ARCHIVE_BYTES
        and hashlib.sha256(plain).hexdigest()
        == V3_FAILURE_UNCOMPRESSED_SHA256
        and gzip.compress(plain, compresslevel=9, mtime=0) == archive_raw,
        "authenticate every original actual version-three failure byte",
    )
    report = decode_document(plain, "preserved actual version-three failure")
    failure = report.get("failure")
    require(
        report.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v3-actual-complete-candidate"
        and report.get("status") == "FAIL"
        and report.get("candidate_family") == "c"
        and report.get("label") == "phase2-v3"
        and report.get("source_sha256") == V3_SHA256
        and report.get("protocol_sha256") == V3_PROTOCOL_SHA256
        and report.get("document_sha256") == V3_DOCUMENT_SHA256
        and report.get("failed_stage")
        == "authenticate all actual canonical promotion intentions"
        and type(failure) is dict
        and failure.get("type") == "GateError"
        and failure.get("message")
        == "a mode-0600 pre-replace promotion intention was lost"
        and report.get("suite_count") == 13
        and report.get("case_execution_denominator") == CASE_COUNT
        and report.get("qualified_candidate_case_executions") == 0
        and report.get("supplemental_subinterpreter_case_count") == 0
        and report.get("supplemental_cases_added_to_original_denominator")
        is False
        and report.get("candidate_qualified") is False
        and report.get("actual_reference_workers_started") == 0
        and report.get("hidden_cases_read") == 0
        and report.get("benchmark_files_read") == 0
        and report.get("clock_samples") == 0
        and report.get("timing_trials_run") == 0
        and report.get("performance") == "NOT MEASURED"
        and report.get("final_holdout_authorized") is False
        and report.get("candidate_qualified_for_hidden_benchmark") is False
        and report.get("final_winner_selected") is False,
        "never conceal or alter the genuine pre-worker version-three failure",
    )
    require(
        type(receipt_raw) is bytes
        and hashlib.sha256(receipt_raw).hexdigest()
        == V3_FAILURE_RECEIPT_SHA256,
        "preserve the exact durable actual version-three failure receipt",
    )
    receipt = decode_document(
        receipt_raw,
        "preserved actual version-three failure receipt",
    )
    owner = receipt.get("archive")
    require(
        canonical(receipt) == receipt_raw
        and receipt.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v3-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_family") == "c"
        and receipt.get("label") == "phase2-v3"
        and receipt.get("source_sha256") == V3_SHA256
        and receipt.get("protocol_sha256") == V3_PROTOCOL_SHA256
        and receipt.get("document_sha256") == V3_DOCUMENT_SHA256
        and receipt.get("failure_preserved") is True
        and receipt.get("all_actual_process_streams_preserved") is True
        and receipt.get("archive_directory_fsync_completed") is True
        and receipt.get("uncompressed_sha256")
        == V3_FAILURE_UNCOMPRESSED_SHA256
        and receipt.get("uncompressed_bytes") == len(plain)
        and type(owner) is dict
        and owner.get("relative") == V3_FAILURE_ARCHIVE_RELATIVE
        and owner.get("sha256") == V3_FAILURE_ARCHIVE_SHA256
        and owner.get("bytes") == len(archive_raw)
        and all(
            owner.get(key) is True
            for key in (
                "exclusive_creation",
                "same_inode_readback_verified",
                "file_fsync_completed",
            )
        )
        and type(owner.get("device")) is int
        and owner["device"] > 0
        and type(owner.get("inode")) is int
        and owner["inode"] > 0
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("benchmark_files_read") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("final_holdout_authorized") is False,
        "the original durable failure receipt no longer owns its exact archive",
    )
    return {
        "schema": SCHEMA + "-independently-verified-preserved-v3-failure",
        "status": "PASS",
        "version_three_source_sha256": V3_SHA256,
        "version_three_protocol_sha256": V3_PROTOCOL_SHA256,
        "version_three_document_sha256": V3_DOCUMENT_SHA256,
        "failure_archive_sha256": V3_FAILURE_ARCHIVE_SHA256,
        "failure_receipt_sha256": V3_FAILURE_RECEIPT_SHA256,
        "failure_uncompressed_sha256": V3_FAILURE_UNCOMPRESSED_SHA256,
        "actual_candidate_cases_executed": 0,
        "failure_preserved": True,
        "candidate_was_qualified": False,
        "holdout_opened": False,
        "performance": "NOT MEASURED",
    }


def run_actual(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    checked_family(options.candidate);checked_label(options.label)
    owners={"GOAL.md":GOAL_SHA256,P0_RELATIVE:P0_SHA256,
        P0_VERIFIER_RELATIVE:P0_VERIFIER_SHA256,V1_RELATIVE:V1_SHA256,
        V2_RELATIVE:V2_SHA256,V2_PROTOCOL_RELATIVE:V2_PROTOCOL_SHA256,
        V2_DOCUMENT_RELATIVE:V2_DOCUMENT_SHA256,
        V3_RELATIVE:V3_SHA256,
        V3_PROTOCOL_RELATIVE:V3_PROTOCOL_SHA256,
        V3_DOCUMENT_RELATIVE:V3_DOCUMENT_SHA256,
        V3_FAILURE_ARCHIVE_RELATIVE:V3_FAILURE_ARCHIVE_SHA256,
        V3_FAILURE_RECEIPT_RELATIVE:V3_FAILURE_RECEIPT_SHA256,
        ACTIVATION_RELATIVE:ACTIVATION_SHA256,
        ACTIVATION_PROTOCOL_RELATIVE:ACTIVATION_PROTOCOL_SHA256,
        BUILD_RELATIVE:BUILD_SHA256,
        BUILD_PROTOCOL_RELATIVE:BUILD_PROTOCOL_SHA256,
        NESTED_V1_RELATIVE:NESTED_V1_SHA256,
        NESTED_V1_DOCUMENT_RELATIVE:NESTED_V1_DOCUMENT_SHA256,
        NESTED_V1_PROSE_RELATIVE:NESTED_V1_PROSE_SHA256,
        SOURCE_RELATIVE:checked_hash(options.source_sha256,"V4 source"),
        PROTOCOL_RELATIVE:checked_hash(options.protocol_sha256,"V4 protocol"),
        DOCUMENT_RELATIVE:checked_hash(options.document_sha256,"V4 inventory"),
        NESTED_V2_RELATIVE:checked_hash(options.nested_v2_source_sha256,"nested V2 source"),
        NESTED_V2_DOCUMENT_RELATIVE:checked_hash(options.nested_v2_protocol_sha256,"nested V2 inventory"),
        NESTED_V2_PROSE_RELATIVE:checked_hash(options.nested_v2_explanation_sha256,"nested V2 explanation")}
    allowed=frozenset(owners)
    snapshots={relative:read_owned(relative,actual,allowed=allowed)
               for relative,actual in owners.items()}
    validate_protocol(decode_document(snapshots[DOCUMENT_RELATIVE],"frozen V4 protocol"))
    historical_v3_failure = validate_preserved_v3_failure(
        snapshots[V3_FAILURE_ARCHIVE_RELATIVE],
        snapshots[V3_FAILURE_RECEIPT_RELATIVE],
    )
    v2=import_frozen(V2_RELATIVE,V2_SHA256,allowed)
    v2.validate_protocol_document(decode_document(snapshots[V2_DOCUMENT_RELATIVE],
                                                  "unchanged complete V2 P0"))
    activation=import_frozen(ACTIVATION_RELATIVE,ACTIVATION_SHA256,allowed)
    require(getattr(activation,"SCHEMA",None)==ACTIVATION_SCHEMA
            and callable(getattr(activation,"validate_activation_documents",None))
            and callable(getattr(activation,"authenticate_promotion_intents",None))
            and callable(getattr(v2,"write_fresh_evidence",None)),
            "use only the corrected original crash-safe native activation owner")
    report={"schema":SCHEMA+"-actual-complete-candidate","status":"FAIL",
        "candidate_family":options.candidate,"label":options.label,
        "source_sha256":options.source_sha256,
        "protocol_sha256":options.protocol_sha256,
        "document_sha256":options.document_sha256,
        "goal_sha256":GOAL_SHA256,"phase1_inventory_sha256":P0_SHA256,
        "preserved_v3_actual_failure":historical_v3_failure,
        "suite_count":13,"case_execution_denominator":CASE_COUNT,
        "qualified_candidate_case_executions":0,
        "supplemental_subinterpreter_case_count":0,
        "supplemental_cases_added_to_original_denominator":False,
        "candidate_qualified":False,"actual_reference_workers_started":0,
        "clock_samples":0,"timing_trials_run":0,"benchmark_files_read":0,
        "hidden_cases_read":0,"performance":"NOT MEASURED",
        "final_holdout_authorized":False,
        "candidate_qualified_for_hidden_benchmark":False,
        "final_winner_selected":False}
    stage="authenticate all actual canonical promotion intentions"
    try:
        first=verify_all_promotion_intents(options,activation)
        report["corrected_promotion_before_full_p0"]=first
        stage="run every unchanged frozen V2 correctness case"
        full,full_process=invoke(v2_command(options))
        report.update(actual_full_p0_gate=full,
                      actual_full_p0_process=full_process)
        require(full.get("schema")=="rebar-frozen-python-re-p0-candidate-v2-published-complete-candidate"
                and full.get("status")=="PASS"
                and full.get("candidate_family")==options.candidate
                and full.get("suite_count")==13
                and full.get("case_execution_denominator")==CASE_COUNT
                and full.get("completed_candidate_suite_count")==13
                and full.get("qualified_candidate_case_executions")==CASE_COUNT
                and full.get("candidate_qualified") is True
                and full.get("performance")=="NOT MEASURED"
                and full.get("final_holdout_authorized") is False,
                "every one of the 31,237 original actual P0 cases must genuinely pass")
        report["qualified_candidate_case_executions"]=CASE_COUNT
        report["actual_full_p0_archive"]=published_archive(
            full.get("complete_archive"),"full V2 P0 archive")
        report["actual_full_p0_receipt"]=published_archive(
            full.get("complete_publication_receipt"),"full V2 durable receipt")
        stage="reauthenticate promotion intentions after full V2 P0"
        second=verify_all_promotion_intents(options,activation)
        report["corrected_promotion_before_supplemental_interpreter"]=second
        require(canonical(first["canonical_targets"])
                ==canonical(second["canonical_targets"])
                and canonical(first["promotion_intents"])
                ==canonical(second["promotion_intents"]),
                "the promoted artifact or durable crash intention changed during V2")
        stage="run the corrected supplemental interpreter gate"
        supplemental,supplemental_process=invoke(nested_v2_command(options))
        report.update(supplemental_subinterpreter_result=supplemental,
                      supplemental_subinterpreter_process=supplemental_process)
        verified_supplemental=validate_supplemental_result(supplemental,options)
        report["verified_supplemental_subinterpreter_evidence"]=(
            verified_supplemental)
        report["supplemental_subinterpreter_case_count"]=128
        report["supplemental_subinterpreter_archive"]=(
            verified_supplemental["archive"])
        report["supplemental_subinterpreter_receipt"]=(
            verified_supplemental["receipt"])
        stage="reauthenticate every intention after both genuine workers"
        third=verify_all_promotion_intents(options,activation)
        report["corrected_promotion_after_all_candidate_invocations"]=third
        require(canonical(first["canonical_targets"])
                ==canonical(third["canonical_targets"])
                and canonical(first["promotion_intents"])
                ==canonical(third["promotion_intents"]),
                "the promoted artifact or 0600 intention changed after the final candidate")
        report.update(status="PASS",candidate_qualified=True)
    except Exception as error:
        report["failed_stage"]=stage
        report["failure"]={"type":type(error).__qualname__,
            "message":str(error),
            "traceback":traceback.format_exception(type(error),error,
                                                   error.__traceback__)}
        if isinstance(error,WorkerFailure):
            report["failed_worker_process"]=error.evidence
    return publish_actual_report(report,options,v2)


def parse_arguments(arguments: Sequence[str]|None=None)->argparse.Namespace:
    parser=argparse.ArgumentParser(description="Verify full Python re P0 and durable native crash-recovery intentions")
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test",action="store_true")
    mode.add_argument("--run",action="store_true")
    parser.add_argument("--candidate",choices=FAMILIES)
    parser.add_argument("--label")
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    for name in ("source","protocol","document","nested-v2-source",
                 "nested-v2-protocol","nested-v2-explanation","build-archive",
                 "build-receipt","activation-report","activation-receipt",
                 "recovery-journal","candidate-source","native-engine",
                 "native-bridge"):
        parser.add_argument("--"+name+"-sha256")
    parser.add_argument("--owned-source-sha256",action="append",default=[])
    return parser.parse_args(arguments)


def main(arguments: Sequence[str]|None=None)->int:
    args=parse_arguments(arguments)
    if args.self_test:
        names=("source_sha256","protocol_sha256","document_sha256",
            "nested_v2_source_sha256","nested_v2_protocol_sha256",
            "nested_v2_explanation_sha256","build_archive_sha256",
            "build_receipt_sha256","activation_report_sha256",
            "activation_receipt_sha256","recovery_journal_sha256",
            "candidate_source_sha256","native_engine_sha256",
            "native_bridge_sha256")
        require(args.candidate is None and args.label is None
                and args.build_label is None and args.activation_root is None
                and not args.owned_source_sha256
                and all(getattr(args,name) is None for name in names),
                "synthetic controls can never authorize actual candidate or native evidence")
        result=source_self_test()
    else:
        result=run_actual(args)
    sys.stdout.buffer.write(canonical(result));sys.stdout.buffer.flush()
    return 0 if result.get("status")=="PASS" else 1


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (GateError,OSError,ValueError,TypeError,KeyError,OverflowError,
            UnicodeError,RecursionError,subprocess.SubprocessError) as error:
        result={"schema":SCHEMA+"-complete-gate-failure","status":"FAIL",
            "error_type":type(error).__qualname__,"message":str(error),
            "traceback":traceback.format_exception(type(error),error,error.__traceback__),
            "actual_reference_workers_started":0,"clock_samples":0,
            "timing_trials_run":0,"benchmark_files_read":0,
            "hidden_cases_read":0,"performance":"NOT MEASURED",
            "final_holdout_authorized":False,
            "candidate_qualified_for_hidden_benchmark":False,
            "final_winner_selected":False}
        sys.stdout.buffer.write(canonical(result));sys.stdout.buffer.flush()
        raise SystemExit(1)
