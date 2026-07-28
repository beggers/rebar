#!/usr/bin/env python3
"""Qualify a genuinely source-built engine against the frozen Python P0.

The self-test is entirely synthetic.  A real run is forbidden until the caller
pins this source, the complete protocol, an independently reproduced version-2
native build, a reversible canonical native activation, and the separately
frozen real-subinterpreter producer.  No matcher guard is copied or rebound.
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
import locale
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
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V2.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v2.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-v2"
PROTOCOL_SCHEMA = "rebar-frozen-python-re-p0-candidate-protocol-v2"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
P0_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
P0_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
P0_EXPLANATION_RELATIVE = "oracle/phase1/P0-COMPLETENESS-V1.md"
P0_EXPLANATION_SHA256 = "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798"
P0_VERIFIER_RELATIVE = "tools/verify_p0_completeness_v1.py"
P0_VERIFIER_SHA256 = "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c"
V1_RELATIVE = "tools/run_frozen_p0_candidate_v1.py"
V1_SHA256 = "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8"
V1_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v1.json"
V1_DOCUMENT_SHA256 = "7ca70c9d4ae7491ae2b9b9a660c8c72efcee629708103ac7654f31353fa7cd0c"
V1_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V1.md"
V1_PROTOCOL_SHA256 = "e73c8a9a1b1edeb847d23c3d27d594d19bdfc514bee9e89790cd4d18fc9d3844"
BUILD_RELATIVE = "tools/reproduce_phase2_native_builds_v2.py"
BUILD_SHA256 = "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796"
BUILD_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md"
BUILD_PROTOCOL_SHA256 = "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603"
BUILD_SCHEMA = "rebar-phase2-independent-native-source-build-v2"
ACTIVATION_RELATIVE = "tools/activate_verified_native_candidate_v1.py"
ACTIVATION_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V1.md"
ACTIVATION_SCHEMA = "rebar-phase2-verified-native-candidate-activation-v1"
ACTIVATION_RECEIPT_SCHEMA = ACTIVATION_SCHEMA + "-durable-publication-receipt"
ACTIVATION_JOURNAL_SCHEMA = ACTIVATION_SCHEMA + "-recovery-journal"
ACTIVATION_PREFIX = "/tmp/rebar-phase2-verified-native-activation-v1-"
SUBINTERPRETER_RELATIVE = "tools/run_owned_candidate_subinterpreters_v1.py"
SUBINTERPRETER_DOCUMENT_RELATIVE = "oracle/phase2/candidate-subinterpreters-v1.json"
SUBINTERPRETER_EXPLANATION_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V1.md"
SUBINTERPRETER_SCHEMA = "rebar-owned-candidate-subinterpreters-v1"
AUDIT_RELATIVE = "tools/audit_candidate_independence_v1.py"
AUDIT_SHA256 = "f18d9b99a3f11fdf20c47d6cb43cb353532c894ababbdaeb7088c14e397ae3b5"
AUDIT_PROTOCOL_RELATIVE = "oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md"
AUDIT_PROTOCOL_SHA256 = "a7ee45f0ea76ee7fedacc564c3122b7f37272d918ef28f1c527c9e8adf351292"
CORE_RELATIVE = "tools/independent_public_contract_v3.py"
CORE_SHA256 = "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3"
RECORDING_AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
RECORDING_AUDIT_SHA256 = "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
V19_VALIDATOR_RELATIVE = "tools/python_re_public_surface_oracle_stage27.py"
V19_VALIDATOR_SHA256 = "fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
CASE_DENOMINATOR = 31_237
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_STREAM_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_LABEL_LENGTH = 48
PROCESS_TIMEOUT_SECONDS = 3_600


class CandidateGateError(Exception):
    """A mandatory frozen correctness or native-ownership obligation failed."""


class SourceOnlyEffect(CandidateGateError):
    """A source-only self-test attempted a real external effect."""


@dataclass(frozen=True, slots=True)
class SuiteSpec:
    name: str
    case_count: int
    source_relative: str
    source_sha256: str
    matrix_sha256: str
    reference_sha256: str
    route: str
    recorder_relative: str | None = None
    recorder_sha256: str | None = None
    baseline_label: str | None = None


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    audit_name: str
    module: str
    adapter: str
    bridge_module: str
    engine: str
    bridge: str
    sources: tuple[str, ...]


FROZEN_SUITES = (
    SuiteSpec("original_bounded_v5", 151,
        "tools/independent_original_cpython_suite_v5.py",
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
        "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240",
        "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276",
        "unchanged-original-v5-isolated-candidate-worker"),
    SuiteSpec("public_v3", 864, "tools/rust_public_practice_benchmark_v1.py",
        "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
        "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
        "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
        "unchanged-public-v3-isolated-candidate-worker", CORE_RELATIVE, CORE_SHA256),
    SuiteSpec("scanner_v3", 1024, "tools/rust_scanner_differential_v1.py",
        "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
        "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
        "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
        "unchanged-scanner-v3-isolated-candidate-worker", CORE_RELATIVE, CORE_SHA256),
    SuiteSpec("buffer_v3", 768, "tools/rust_memoryview_expand_differential_v1.py",
        "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
        "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
        "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
        "unchanged-buffer-v3-isolated-candidate-worker", CORE_RELATIVE, CORE_SHA256),
    SuiteSpec("managed_v1", 1024,
        "tools/independent_managed_buffer_lifetime_v1.py",
        "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489",
        "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976",
        "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df",
        "unchanged-managed-candidate-recorder-with-signed-baseline",
        "tools/record_independent_managed_buffer_candidates_v1.py",
        "d7f9fdeb9979eaeaa5ffdcea5a655be31c070356d93d293289b9b90de876877a",
        "shared-suite-v1"),
    SuiteSpec("scanner_verbose_v1", 2854,
        "tools/independent_scanner_verbose_comments_v1.py",
        "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d",
        "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b",
        "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012",
        "unchanged-verbose-candidate-recorder-with-signed-baseline",
        "tools/record_independent_scanner_verbose_comments_v1.py",
        "d75934bef992e01ad5c1131a8abef997d3b540f8b150518822ad7e55c39c9191",
        "shared-suite-v1"),
    SuiteSpec("public_types_v1", 6912,
        "tools/independent_public_type_identity_serialization_v1.py",
        "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
        "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123",
        "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
        "unchanged-public-types-candidate-recorder-with-signed-baseline",
        "tools/record_independent_public_type_identity_serialization_v1.py",
        "ee3e6fc00991758fee93b710a63dad9094f881f1ea57777cae2415397f752eae",
        "shared-suite-v1"),
    SuiteSpec("substitution_v2", 5120,
        "tools/independent_substitution_buffer_semantics_v2.py",
        "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
        "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54",
        "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b",
        "unchanged-substitution-v3-recorder-with-signed-v2-baseline",
        "tools/record_independent_substitution_buffer_semantics_v3.py",
        "1e6bd77cea22c511ca3ee0ccdd4c02b12b4aa22c4fb79cb0df74d2894280807c",
        "shared-suite-v2"),
    SuiteSpec("shape_v2", 10240,
        "tools/independent_shape_changing_buffer_semantics_v2.py",
        "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
        "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8",
        "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c",
        "unchanged-shape-v2-recorder-with-signed-baseline",
        "tools/record_independent_shape_changing_buffer_semantics_v2.py",
        "0ddcb154378807ce6d3b8c5726f37e72ed9fcf921fe348d7640e1a6f1a898cc9",
        "shared-suite-v2"),
    SuiteSpec("public_surface_v19", 1376,
        "tools/python_re_public_surface_oracle_stage19.py",
        "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e",
        "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa",
        "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
        "unchanged-v17-evaluator-v19-normalizer-real-private-locales",
        V19_VALIDATOR_RELATIVE, V19_VALIDATOR_SHA256),
    SuiteSpec("subinterpreter_v2", 128,
        "tools/python_re_subinterpreter_oracle_v2.py",
        "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8",
        "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3",
        "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8",
        "separately-frozen-real-owned-candidate-subinterpreter-recorder",
        SUBINTERPRETER_RELATIVE),
    SuiteSpec("pep688_v4", 264, "tools/python_re_buffer_exporter_oracle_v4.py",
        "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490",
        "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891",
        "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8",
        "unchanged-real-pep688-buffer-exporter-candidate-worker"),
    SuiteSpec("threaded_pattern_v1", 512,
        "tools/python_re_threaded_pattern_oracle_v1.py",
        "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276",
        "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b",
        "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81",
        "unchanged-real-simultaneous-shared-pattern-thread-cohorts"),
)

FAMILY_SPECS = {
    "rust": FamilySpec("rust", "rust", "candidates.rust_candidate",
        "candidates/rust_candidate.py", "candidates._rust_bridge",
        "candidates/_rust_engine.so", "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        ("candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
         "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
         "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
         "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
         "candidates/rust/src/unicode_tables.rs")),
    "c": FamilySpec("c", "c_vm", "candidates.vm_candidate",
        "candidates/vm_candidate.py", "candidates._vm_native",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c")),
    "zig": FamilySpec("zig", "zig", "candidates.zig_candidate",
        "candidates/zig_candidate.py", "candidates._zig_bridge",
        "candidates/_zig_probe.so", "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        ("candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
         "candidates/zig/py_bridge.c")),
}

REFERENCE_ONLY_FIELDS = frozenset({"candidate_imports", "stdlib_origin_verified"})
SUBINTERPRETER_FIELDS = frozenset({"actual_exec", "case_id", "cohort",
    "locale_unchanged", "observation", "ordinal", "pinned_executable_verified",
    "seed", "status", "variant"})
OBSERVATION_RENAMES = types.MappingProxyType({
    "actual_stdlib_reimport": "actual_engine_reimport",
    "match_is_stdlib_match": "match_is_engine_match",
    "module_identity": "engine_sysmodules_identity_verified",
    "pattern_is_stdlib_pattern": "pattern_is_engine_pattern",
    "reimported_origin_verified": "engine_reimported_origin_verified",
    "stdlib_owner": "engine_sysmodules_owner_verified",
    "stdlib_re_module": "engine_module_name_verified",
})
PROJECTED_REFERENCE_SHA256 = "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021"
THREAD_WARNING_SHA256 = "f28af6781328eacabdbe96460e8c54cba1e7802f6a052cefb4a7c59f30ce4413"

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CandidateGateError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=True, allow_nan=False,
                          sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise CandidateGateError("complete canonical ASCII evidence is mandatory") from error


def valid_sha256(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require an exact lowercase SHA-256: " + label)
    return value


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "duplicate or non-string complete evidence keys are forbidden")
        result[key] = value
    return result


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_STREAM_BYTES,
            "require bounded complete evidence: " + label)
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
            parse_constant=lambda item: (_ for _ in ()).throw(
                CandidateGateError("non-finite evidence is forbidden: " + item)))
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise CandidateGateError("reject malformed complete evidence: " + label) from error
    require(type(result) is dict, "require a complete evidence object: " + label)
    return result


def verify_runtime(*, candidate_allowed: bool = False) -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and sys.path and sys.path[0] == str(ROOT),
            "use exact isolated no-bytecode CPython 3.14.6 and canonical ROOT")
    if not candidate_allowed:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "a native candidate was imported before authenticated activation")


def suite_spec(value: Any) -> SuiteSpec:
    require(type(value) is str, "select one exact frozen P0 suite")
    found = [suite for suite in FROZEN_SUITES if suite.name == value]
    require(len(found) == 1, "reject an omitted, foreign, or holdout suite")
    return found[0]


def family_spec(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILY_SPECS,
            "select one genuinely independent frozen Rust, C, or Zig engine")
    return FAMILY_SPECS[value]


def checked_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= MAX_LABEL_LENGTH
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-" for item in value),
            "require an exact safe lowercase evidence label")
    return value


def parse_source_owners(values: Any, spec: FamilySpec) -> dict[str, str]:
    require(isinstance(values, (list, tuple)),
            "explicitly pin the complete independent engine source closure")
    owners: dict[str, str] = {}
    for item in values:
        require(type(item) is str and item.count("=") == 1,
                "each genuine source owner requires one relative=SHA-256 pin")
        relative, owner = item.split("=", 1)
        require(relative in spec.sources and relative not in owners,
                "reject missing, duplicate, sibling, or external source owners")
        owners[relative] = valid_sha256(owner, relative)
    require(set(owners) == set(spec.sources),
            "authenticate every source of the independently owned candidate")
    return dict(sorted(owners.items()))


def safe_relative(relative: Any, allowed: frozenset[str]) -> tuple[str, ...]:
    require(type(relative) is str and relative in allowed
            and not relative.startswith("/") and "\\" not in relative
            and "\x00" not in relative,
            "read only a specifically pinned correctness owner")
    parts = tuple(relative.split("/"))
    require(parts and all(item not in {"", ".", ".."} for item in parts)
            and not any(item in {"holdout", "hidden", "benchmark",
                                 "benchmarks", "performance"} for item in parts),
            "holdout, performance, traversal, and hidden reads are forbidden")
    return parts


def read_owned(relative: str, expected: str, *, allowed: frozenset[str],
               maximum: int = MAX_SOURCE_BYTES) -> bytes:
    valid_sha256(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_STREAM_BYTES,
            "require an exact bounded frozen correctness file")
    parts = safe_relative(relative, allowed)
    regular = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = regular | getattr(os, "O_DIRECTORY", 0)
    descriptors: list[int] = []
    try:
        parent = os.open(str(ROOT), directory)
        descriptors.append(parent)
        for item in parts[:-1]:
            parent = os.open(item, directory, dir_fd=parent)
            descriptors.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "a pinned correctness parent was replaced")
        descriptor = os.open(parts[-1], regular, dir_fd=parent)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum,
                "reject symlinked, unbounded, or substituted correctness evidence")
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1_048_576))
            require(type(piece) is bytes and bool(piece),
                    "a complete pinned correctness owner was truncated")
            pieces.append(piece)
            remaining -= len(piece)
        require(os.read(descriptor, 1) == b"", "reject a hidden owner suffix")
        after = os.fstat(descriptor)
        final = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (final.st_dev, final.st_ino, final.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "an authenticated owner changed while it was being read")
        result = b"".join(pieces)
        require(hashlib.sha256(result).hexdigest() == expected,
                "exact source or evidence SHA-256 mismatch: " + relative)
        return result
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def synthetic_protocol() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for suite in FROZEN_SUITES:
        row: dict[str, Any] = {
            "id": suite.name, "case_count": suite.case_count,
            "source_path": suite.source_relative,
            "source_sha256": suite.source_sha256,
            "matrix_sha256": suite.matrix_sha256,
            "reference_records_sha256": suite.reference_sha256,
            "route": suite.route,
            "projection": ("original-152-public-records-151-runnable-one-debug-skip"
                if suite.name == "original_bounded_v5" else
                "explicit-lossless-reference-only-owner-identity-v1"
                if suite.name == "subinterpreter_v2" else
                "exact-complete-source-ordered-reference-record"),
        }
        if suite.recorder_relative is not None:
            row["candidate_recorder_path"] = suite.recorder_relative
            if suite.recorder_sha256 is not None:
                row["candidate_recorder_sha256"] = suite.recorder_sha256
            else:
                row["candidate_recorder_sha256_mode"] = (
                    "mandatory-exact-caller-pinned-separately-published-source")
        if suite.baseline_label is not None:
            row["baseline_label"] = suite.baseline_label
        if suite.name == "original_bounded_v5":
            row.update(actual_public_record_count=152,
                       runnable_public_record_count=151,
                       genuine_debug_skip_count=1, named_private_waiver_count=13)
        elif suite.name == "public_surface_v19":
            row.update(actual_real_locale_case_count=64,
                       actual_real_locale_transition_count=192)
        elif suite.name == "subinterpreter_v2":
            row.update(projected_reference_records_sha256=PROJECTED_REFERENCE_SHA256,
                projected_reference_only_top_level_fields=sorted(REFERENCE_ONLY_FIELDS),
                lossless_observation_field_renames=dict(OBSERVATION_RENAMES),
                actual_interpreters_created=11, actual_interpreters_destroyed=11,
                actual_case_interpreter_exec_calls=394,
                actual_initialization_interpreter_exec_calls=11,
                actual_guard_cleanup_interpreter_exec_calls=11,
                actual_repeated_fresh_interpreter_cases=8)
        elif suite.name == "threaded_pattern_v1":
            row.update(actual_thread_starts=32, actual_thread_joins=32,
                actual_thread_case_executions=1024, actual_regex_api_calls=2176,
                warning_records_sha256=THREAD_WARNING_SHA256)
        rows.append(row)
    caller_mode = "mandatory-exact-caller-pinned-published-source-bytes"
    return {
        "schema": PROTOCOL_SCHEMA, "version": 2, "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; CANDIDATES NOT RUN",
        "goal_sha256": GOAL_SHA256,
        "phase1": {
            "inventory_path": P0_RELATIVE, "inventory_sha256": P0_SHA256,
            "explanation_path": P0_EXPLANATION_RELATIVE,
            "explanation_sha256": P0_EXPLANATION_SHA256,
            "verifier_path": P0_VERIFIER_RELATIVE,
            "verifier_sha256": P0_VERIFIER_SHA256,
            "python_path": PINNED_PYTHON, "python_sha256": PINNED_PYTHON_SHA256,
            "python_version": "3.14.6", "suite_count": 13,
            "case_execution_denominator": CASE_DENOMINATOR,
            "public_obligation_count": 73, "named_private_waiver_count": 13,
            "genuine_public_debug_skip_count": 1},
        "preserved_v1": {
            "source_path": V1_RELATIVE, "source_sha256": V1_SHA256,
            "protocol_path": V1_PROTOCOL_RELATIVE,
            "protocol_sha256": V1_PROTOCOL_SHA256,
            "inventory_path": V1_DOCUMENT_RELATIVE,
            "inventory_sha256": V1_DOCUMENT_SHA256,
            "modified": False},
        "candidate_families": ["rust", "c", "zig"],
        "runner": {"path": SOURCE_RELATIVE, "source_sha256_mode": caller_mode},
        "native_source_build_v2": {
            "schema": BUILD_SCHEMA, "source_path": BUILD_RELATIVE,
            "source_sha256": BUILD_SHA256,
            "protocol_path": BUILD_PROTOCOL_RELATIVE,
            "protocol_sha256": BUILD_PROTOCOL_SHA256,
            "independent_fresh_source_build_phase_count": 2,
            "version_one_build_authorized": False,
            "preexisting_binary_authorized": False,
            "archive_sha256_mode": caller_mode,
            "receipt_sha256_mode": caller_mode},
        "canonical_activation": {
            "schema": ACTIVATION_SCHEMA,
            "receipt_schema": ACTIVATION_RECEIPT_SCHEMA,
            "recovery_journal_schema": ACTIVATION_JOURNAL_SCHEMA,
            "source_path": ACTIVATION_RELATIVE,
            "protocol_path": ACTIVATION_PROTOCOL_RELATIVE,
            "source_sha256_mode": caller_mode,
            "protocol_sha256_mode": caller_mode,
            "report_sha256_mode": caller_mode,
            "receipt_sha256_mode": caller_mode,
            "activation_root_prefix": ACTIVATION_PREFIX,
            "activation_root_mode": "0700",
            "promotion_mode": "recoverable-canonical-promotion",
            "candidate_import_root": str(ROOT),
            "exact_preexisting_native_backup_required": True,
            "complete_recovery_journal_required": True,
            "atomic_native_replacement_required": True,
            "rollback_required": True,
            "copied_matcher_guard_allowed": False,
            "matcher_guard_root_rebinding_allowed": False},
        "subinterpreter_controller": {
            "schema": SUBINTERPRETER_SCHEMA,
            "source_path": SUBINTERPRETER_RELATIVE,
            "protocol_path": SUBINTERPRETER_DOCUMENT_RELATIVE,
            "explanation_path": SUBINTERPRETER_EXPLANATION_RELATIVE,
            "source_sha256_mode": caller_mode,
            "protocol_sha256_mode": caller_mode,
            "explanation_sha256_mode": caller_mode,
            "actual_candidate_recorder_required": True,
            "main_interpreter_replay_allowed": False},
        "independence_audit": {
            "source_path": AUDIT_RELATIVE, "source_sha256": AUDIT_SHA256,
            "protocol_path": AUDIT_PROTOCOL_RELATIVE,
            "protocol_sha256": AUDIT_PROTOCOL_SHA256,
            "runtime_no_delegation_proved_by_static_audit": False,
            "unchanged_continuous_v5_runtime_guard_required": True},
        "common_category_controller": {
            "path": CORE_RELATIVE, "sha256": CORE_SHA256,
            "families": ["rust", "c", "zig"],
            "categories": ["public", "scanner", "buffer"]},
        "specialized_recorder_ownership_audit": {
            "path": RECORDING_AUDIT_RELATIVE,
            "sha256": RECORDING_AUDIT_SHA256,
            "managed_recorder_uses_its_own_frozen_legacy_audit": True},
        "suites": rows,
        "publication": {
            "directory": "oracle/phase2/evidence",
            "pass_archive_template": "frozen-p0-candidate-v2-FAMILY-LABEL.json.gz",
            "pass_receipt_template": "frozen-p0-candidate-v2-FAMILY-LABEL-publication-receipt.json",
            "failure_archive_template": "frozen-p0-candidate-v2-FAMILY-LABEL-failures.json.gz",
            "failure_receipt_template": "frozen-p0-candidate-v2-FAMILY-LABEL-failures-publication-receipt.json",
            "exclusive_creation": True, "no_follow": True,
            "deterministic_gzip_mtime": 0,
            "complete_stdout_and_stderr_required": True,
            "same_inode_readback_required": True,
            "file_and_directory_fsync_required": True,
            "all_mismatches_crashes_timeouts_and_signals_preserved": True},
        "boundaries": {
            "archive_receipts_required": True,
            "candidate_workers_isolated": True,
            "continuous_original_matcher_quarantine_required": True,
            "cross_candidate_delegation_allowed": False,
            "external_regex_package_allowed": False,
            "stdlib_candidate_delegation_allowed": False,
            "copied_or_rebound_original_matcher_guards_allowed": False,
            "unverified_canonical_native_binary_allowed": False,
            "reference_workers_started": 0,
            "hidden_case_access_allowed": False, "timing_allowed": False,
            "final_holdout_authorized": False, "final_holdout_opened": False,
            "final_winner_selected": False, "performance": "NOT MEASURED"},
        "candidate_results": "NOT MEASURED",
    }


def validate_protocol_document(document: Any) -> dict[str, Any]:
    require(type(document) is dict
            and canonical(document) == canonical(synthetic_protocol()),
            "the complete frozen V2 protocol, obligation, producer, or boundary changed")
    return document


def validate_phase1_document(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and type(value.get("goal")) is dict
            and value["goal"].get("sha256") == GOAL_SHA256,
            "the immutable original complete Python correctness inventory changed")
    gate = value.get("phase_gate")
    require(type(gate) is dict and gate.get("status") == "PASS"
            and gate.get("phase") == "CORRECTNESS ORACLE"
            and gate.get("all_obligations_mapped") is True
            and gate.get("final_holdout_authorized") is False,
            "the complete passing phase-one oracle is mandatory")
    obligations = value.get("obligations")
    require(type(obligations) is dict
            and obligations.get("inherited_count") == 45
            and obligations.get("additional_named_count") == 28
            and obligations.get("crosswalk_count") == 34
            and type(obligations.get("inherited")) is list
            and len(obligations["inherited"]) == 45
            and type(obligations.get("additional")) is list
            and len(obligations["additional"]) == 28
            and type(obligations.get("crosswalk")) is list
            and len(obligations["crosswalk"]) == 34,
            "preserve all 73 public obligations and all 34 original crosswalks")
    original = value.get("original_upstream")
    require(type(original) is dict
            and original.get("private_waiver_count") == 13
            and type(original.get("private_waivers")) is list
            and len(original["private_waivers"]) == 13
            and original.get("source_method_count") == 165
            and original.get("public_method_count") == 152
            and original.get("runnable_public_method_count") == 151
            and type(original.get("public_debug_skip")) is dict
            and original["public_debug_skip"].get("method")
            == "ReTests.test_memory_leaks"
            and original["public_debug_skip"].get("counted_as_runnable_case") is False,
            "never conceal the real original debug skip or any named private waiver")
    denominator = value.get("denominator")
    require(type(denominator) is dict
            and denominator.get("final_required_case_execution_denominator")
            == CASE_DENOMINATOR
            and denominator.get("available_frozen_vector_case_executions")
            == CASE_DENOMINATOR
            and denominator.get("counted_suite_ids")
            == [item.name for item in FROZEN_SUITES],
            "all 13 original suites and 31,237 counted executions are mandatory")
    rows = value.get("suites")
    require(type(rows) is list and len(rows) == len(FROZEN_SUITES),
            "never omit or add a frozen correctness suite")
    for actual, expected in zip(rows, FROZEN_SUITES, strict=True):
        require(type(actual) is dict and actual.get("id") == expected.name
                and actual.get("case_execution_count") == expected.case_count
                and actual.get("matrix_sha256") == expected.matrix_sha256
                and actual.get("baseline_records_sha256") == expected.reference_sha256
                and type(actual.get("source")) is dict
                and actual["source"].get("path") == expected.source_relative
                and actual["source"].get("sha256") == expected.source_sha256,
                "an original producer, case ID, order, or reference was changed")
        if actual.get("recorder") is not None and expected.name != "managed_v1":
            recorder = actual["recorder"]
            if expected.recorder_relative not in {None, CORE_RELATIVE,
                                                 V19_VALIDATOR_RELATIVE,
                                                 SUBINTERPRETER_RELATIVE}:
                require(type(recorder) is dict
                        and recorder.get("path") == expected.recorder_relative
                        and recorder.get("sha256") == expected.recorder_sha256,
                        "an exact suite-owned actual candidate recorder changed")
    return value


def project_subinterpreter_reference(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and set(value) == SUBINTERPRETER_FIELDS | REFERENCE_ONLY_FIELDS
            and value.get("candidate_imports") == 0
            and value.get("stdlib_origin_verified") is True
            and value.get("actual_exec") is True
            and value.get("locale_unchanged") is True
            and value.get("pinned_executable_verified") is True
            and value.get("status") == "PASS"
            and type(value.get("observation")) is dict,
            "preserve every genuine original subinterpreter observation")
    require(len(OBSERVATION_RENAMES) == 7
            and len(set(OBSERVATION_RENAMES.values())) == 7
            and set(OBSERVATION_RENAMES).isdisjoint(OBSERVATION_RENAMES.values()),
            "all seven lossless observation renames must be exact and injective")
    observation = dict(value["observation"])
    for old, new in OBSERVATION_RENAMES.items():
        if old in observation:
            require(new not in observation,
                    "reject a collided genuine engine-ownership observation")
            observation[new] = observation.pop(old)
    result = {name: item for name, item in value.items()
              if name not in REFERENCE_ONLY_FIELDS}
    result["observation"] = observation
    require(set(result) == SUBINTERPRETER_FIELDS,
            "a genuine frozen semantic field was dropped")
    return result


def validate_subinterpreter_case(record: Any, reference: Mapping[str, Any],
                                 spec: FamilySpec,
                                 pins: Mapping[str, str]) -> dict[str, Any]:
    extras = {"candidate_family", "candidate_module", "candidate_source_sha256",
              "candidate_engine_sha256", "candidate_bridge_sha256",
              "candidate_origin_verified", "candidate_import_count",
              "original_matcher_calls", "external_engine_imports",
              "cross_candidate_imports", "foreign_native_loads"}
    require(type(record) is dict
            and set(record) == SUBINTERPRETER_FIELDS | extras
            and record.get("candidate_family") == spec.name
            and record.get("candidate_module") == spec.module
            and record.get("candidate_origin_verified") is True
            and type(record.get("candidate_import_count")) is int
            and record["candidate_import_count"] >= 1,
            "an actual in-interpreter engine or its full observation was forged")
    for actual, expected in (("candidate_source_sha256", "source"),
                              ("candidate_engine_sha256", "native_engine"),
                              ("candidate_bridge_sha256", "native_bridge")):
        require(record.get(actual) == valid_sha256(pins.get(expected), expected),
                "a genuine activated in-interpreter native owner was substituted")
    require((record["candidate_engine_sha256"]
             == record["candidate_bridge_sha256"]) is (spec.name == "c")
            and all(type(record.get(name)) is int and record[name] == 0
                    for name in ("original_matcher_calls",
                                 "external_engine_imports",
                                 "cross_candidate_imports", "foreign_native_loads")),
            "an original matcher, sibling engine, or foreign native escaped")
    projected = {name: record[name] for name in SUBINTERPRETER_FIELDS}
    require(canonical(projected) == canonical(project_subinterpreter_reference(reference)),
            "an actual candidate differs from a full frozen interpreter observation")
    return projected


def validate_thread_evidence(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("actual_thread_starts") == 32
            and value.get("actual_thread_joins") == 32
            and value.get("actual_thread_case_executions") == 1024
            and value.get("actual_regex_api_calls") == 2176
            and value.get("metadata_case_count") == 32
            and value.get("metadata_cases_are_threaded_subset") is True
            and value.get("all_barriers_verified") is True
            and value.get("all_thread_joins_verified") is True
            and value.get("orphan_threads") == 0
            and value.get("thread_failures") == [],
            "all genuine frozen simultaneous thread calls and joins are mandatory")
    lifecycle = value.get("thread_lifecycle")
    events = value.get("thread_events")
    require(type(lifecycle) is list and len(lifecycle) == 32
            and all(type(row) is dict and row.get("started") is True
                    and row.get("joined") is True
                    and row.get("alive_after_join") is False for row in lifecycle),
            "reject fabricated, missing, or leaked real thread lifecycles")
    require(type(events) is list and len(events) == 1024
            and all(type(row) is dict and row.get("status") == "PASS"
                    and row.get("start_barrier_passed") is True
                    and row.get("completion_barrier_arrived") is True
                    for row in events),
            "reject missing simultaneous thread barrier executions")
    if "warning_records_sha256" in value:
        require(value["warning_records_sha256"] == THREAD_WARNING_SHA256,
                "all 16 frozen threaded warning observations are mandatory")
    return value


def capture_stream(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_STREAM_BYTES,
            "retain a complete bounded genuine candidate process stream")
    return {"encoding": "base64", "data": base64.b64encode(raw).decode("ascii"),
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "complete": True}


def restore_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"encoding", "data", "bytes", "sha256", "complete"}
            and value.get("encoding") == "base64" and value.get("complete") is True
            and type(value.get("data")) is str
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_STREAM_BYTES,
            "retain exact complete worker standard output and error: " + label)
    valid_sha256(value.get("sha256"), label)
    try:
        raw = base64.b64decode(value["data"], validate=True)
    except (TypeError, ValueError) as error:
        raise CandidateGateError("invalid exact process stream: " + label) from error
    require(len(raw) == value["bytes"]
            and hashlib.sha256(raw).hexdigest() == value["sha256"],
            "a genuine complete candidate process stream was changed")
    return raw


def synthetic_reference() -> dict[str, Any]:
    return {"actual_exec": True, "candidate_imports": 0,
        "case_id": "frozen-subinterpreter:00", "cohort": "fresh-interpreter",
        "locale_unchanged": True, "observation": {
            **{key: True for key in OBSERVATION_RENAMES},
            "actual_interpreter_exec": True, "owner_state_intact": True},
        "ordinal": 0, "pinned_executable_verified": True,
        "seed": 13339223064461967305, "status": "PASS",
        "stdlib_origin_verified": True, "variant": 0}


def synthetic_candidate(spec: FamilySpec | None = None) -> tuple[dict[str, Any], dict[str, str]]:
    family = family_spec("rust") if spec is None else spec
    pins = {"source": "1" * 64, "native_engine": "2" * 64,
            "native_bridge": "2" * 64 if family.name == "c" else "3" * 64}
    result = {**project_subinterpreter_reference(synthetic_reference()),
        "candidate_family": family.name, "candidate_module": family.module,
        "candidate_source_sha256": pins["source"],
        "candidate_engine_sha256": pins["native_engine"],
        "candidate_bridge_sha256": pins["native_bridge"],
        "candidate_origin_verified": True, "candidate_import_count": 1,
        "original_matcher_calls": 0, "external_engine_imports": 0,
        "cross_candidate_imports": 0, "foreign_native_loads": 0}
    return result, pins


def synthetic_threads() -> dict[str, Any]:
    return {"actual_thread_starts": 32, "actual_thread_joins": 32,
        "actual_thread_case_executions": 1024, "actual_regex_api_calls": 2176,
        "metadata_case_count": 32, "metadata_cases_are_threaded_subset": True,
        "all_barriers_verified": True, "all_thread_joins_verified": True,
        "orphan_threads": 0, "thread_failures": [],
        "warning_records_sha256": THREAD_WARNING_SHA256,
        "thread_lifecycle": [{"started": True, "joined": True,
                               "alive_after_join": False} for _ in range(32)],
        "thread_events": [{"status": "PASS", "start_barrier_passed": True,
                           "completion_barrier_arrived": True}
                          for _ in range(1024)]}


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {name: 0 for name in (
        "file_reads", "file_writes", "candidate_imports", "reference_workers",
        "candidate_workers", "thread_starts", "interpreter_creations",
        "gc_collections", "clock_samples", "hidden_cases_read",
        "performance_files_read", "build_processes", "native_libraries_loaded",
        "native_promotions", "guard_root_rebindings", "blocked_reads",
        "blocked_writes", "blocked_imports", "blocked_processes",
        "blocked_threads", "blocked_clocks", "blocked_gc_collections",
        "blocked_promotions")}
    installed: list[tuple[Any, str, Any]] = []

    def deny(field: str, reason: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[field] += 1
            raise SourceOnlyEffect(reason)
        return blocked

    def install(owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    try:
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                            (os, "read"), (os, "stat"), (os, "lstat"),
                            (Path, "open"), (Path, "read_bytes"),
                            (Path, "read_text")):
            install(owner, name, deny("blocked_reads", "source-only real file read"))
        for owner, name in ((os, "write"), (os, "unlink"), (os, "remove"),
                            (os, "rename"), (os, "mkdir"), (os, "rmdir"),
                            (os, "fsync"), (Path, "write_bytes"),
                            (Path, "write_text"), (Path, "mkdir"), (Path, "unlink")):
            install(owner, name, deny("blocked_writes", "source-only real file write"))
        install(os, "replace", deny("blocked_promotions",
                                     "source-only real canonical native promotion"))
        install(importlib, "import_module", deny("blocked_imports",
                                                  "source-only real candidate import"))
        install(subprocess, "Popen", deny("blocked_processes",
                                           "source-only real candidate or reference process"))
        install(subprocess, "run", deny("blocked_processes",
                                         "source-only real build or process"))
        install(threading.Thread, "start", deny("blocked_threads",
                                                 "source-only real thread"))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "thread_time"):
            install(time, name, deny("blocked_clocks",
                                     "source-only real wall clock or benchmark"))
        install(gc, "collect", deny("blocked_gc_collections",
                                     "source-only real garbage collection"))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(label: str, operation: Callable[[], Any]) -> Any:
        try:
            result = operation()
        except Exception as error:
            raise CandidateGateError("a required synthetic positive failed: " + label) from error
        accepted.append(label)
        return result

    def reject(label: str, operation: Callable[[], Any]) -> None:
        try:
            operation()
        except (CandidateGateError, SourceOnlyEffect, ValueError, TypeError,
                KeyError, OverflowError, UnicodeError, RecursionError):
            rejected.append(label)
            return
        raise CandidateGateError("a mandatory hostile control escaped: " + label)

    with source_only_boundary() as effects:
        document = accept("accept-exact-13-suite-31,237-case-v2-protocol",
                          lambda: validate_protocol_document(synthetic_protocol()))
        accept("retain-unchanged-v1-and-three-independent-native-families",
               lambda: require(tuple(FAMILY_SPECS) == ("rust", "c", "zig")
                   and sum(item.case_count for item in FROZEN_SUITES) == CASE_DENOMINATOR,
                   "never change candidate families or original case denominator"))
        accept("reject-private-guard-relocation-and-root-rebinding-by-protocol",
               lambda: require(document["canonical_activation"]["copied_matcher_guard_allowed"]
                   is False and document["canonical_activation"]["matcher_guard_root_rebinding_allowed"]
                   is False and document["canonical_activation"]["candidate_import_root"]
                   == str(ROOT), "the frozen matcher guard must remain unchanged"))
        for suite in FROZEN_SUITES:
            accept("resolve-exact-producer-" + suite.name,
                   lambda suite=suite: suite_spec(suite.name))
            row = next(item for item in document["suites"] if item["id"] == suite.name)
            for field in tuple(row):
                def changed_suite(suite: SuiteSpec = suite, field: str = field) -> Any:
                    forged = synthetic_protocol()
                    selected = next(item for item in forged["suites"]
                                    if item["id"] == suite.name)
                    value = selected[field]
                    if type(value) is bool:
                        selected[field] = not value
                    elif type(value) is int:
                        selected[field] = value + 1
                    elif type(value) is str:
                        selected[field] = ("0" * 64 if field.endswith("sha256")
                                           else value + "-forged")
                    elif type(value) is list:
                        selected[field] = value[:-1]
                    elif type(value) is dict:
                        selected[field] = {**value, "forged": True}
                    else:
                        selected[field] = None
                    return validate_protocol_document(forged)
                reject("reject-suite-" + suite.name + "-" + field, changed_suite)
        for index, suite in enumerate(FROZEN_SUITES):
            def omitted(index: int = index) -> Any:
                forged = synthetic_protocol()
                del forged["suites"][index]
                return validate_protocol_document(forged)
            reject("reject-omitted-frozen-suite-" + suite.name, omitted)
            if index + 1 < len(FROZEN_SUITES):
                def reordered(index: int = index) -> Any:
                    forged = synthetic_protocol()
                    forged["suites"][index:index + 2] = reversed(
                        forged["suites"][index:index + 2])
                    return validate_protocol_document(forged)
                reject("reject-reordered-frozen-suite-" + suite.name, reordered)
        for section in ("phase1", "preserved_v1", "native_source_build_v2",
                        "canonical_activation", "subinterpreter_controller",
                        "independence_audit", "common_category_controller",
                        "specialized_recorder_ownership_audit", "publication",
                        "boundaries"):
            for field in document[section]:
                def changed_section(section: str = section, field: str = field) -> Any:
                    forged = synthetic_protocol()
                    value = forged[section][field]
                    forged[section][field] = (
                        not value if type(value) is bool else
                        value + 1 if type(value) is int else
                        value + "-forged" if type(value) is str else
                        value[:-1] if type(value) is list else None)
                    return validate_protocol_document(forged)
                reject("reject-" + section + "-" + field, changed_section)
        for family in FAMILY_SPECS.values():
            accept("resolve-owned-engine-" + family.name,
                   lambda family=family: family_spec(family.name))
            entries = [relative + "=" + hashlib.sha256(
                relative.encode("ascii")).hexdigest() for relative in family.sources]
            accept("accept-complete-source-closure-" + family.name,
                   lambda family=family, entries=entries:
                   parse_source_owners(entries, family))
            reject("reject-missing-engine-source-" + family.name,
                   lambda family=family, entries=entries:
                   parse_source_owners(entries[:-1], family))
            reject("reject-duplicate-engine-source-" + family.name,
                   lambda family=family, entries=entries:
                   parse_source_owners([*entries, entries[0]], family))
            reject("reject-external-engine-source-" + family.name,
                   lambda family=family, entries=entries:
                   parse_source_owners([*entries[:-1],
                       "candidates/external.py=" + "a" * 64], family))
            candidate, pins = synthetic_candidate(family)
            accept("verify-real-interpreter-owner-" + family.name,
                   lambda candidate=candidate, family=family, pins=pins:
                   validate_subinterpreter_case(candidate, synthetic_reference(),
                                                family, pins))
            for field in ("candidate_family", "candidate_module",
                          "candidate_source_sha256", "candidate_engine_sha256",
                          "candidate_bridge_sha256", "candidate_origin_verified",
                          "candidate_import_count", "original_matcher_calls",
                          "external_engine_imports", "cross_candidate_imports",
                          "foreign_native_loads"):
                def forged_owner(field: str = field, family: FamilySpec = family) -> Any:
                    changed, actual_pins = synthetic_candidate(family)
                    old = changed[field]
                    changed[field] = (not old if type(old) is bool else
                        0 if field == "candidate_import_count" else
                        old + 1 if type(old) is int else "forged-external-engine")
                    return validate_subinterpreter_case(changed, synthetic_reference(),
                                                       family, actual_pins)
                reject("reject-forged-interpreter-" + family.name + "-" + field,
                       forged_owner)
        reference = synthetic_reference()
        accept("preserve-seven-injective-lossless-observation-renames",
               lambda: project_subinterpreter_reference(reference))
        for field in sorted(SUBINTERPRETER_FIELDS):
            def drop_reference(field: str = field) -> Any:
                changed = synthetic_reference()
                changed.pop(field)
                return project_subinterpreter_reference(changed)
            reject("reject-dropped-interpreter-reference-" + field, drop_reference)
            def drop_candidate(field: str = field) -> Any:
                actual, pins = synthetic_candidate()
                actual.pop(field)
                return validate_subinterpreter_case(actual, synthetic_reference(),
                                                   family_spec("rust"), pins)
            reject("reject-dropped-interpreter-candidate-" + field, drop_candidate)
        for original, renamed in OBSERVATION_RENAMES.items():
            def collision(original: str = original, renamed: str = renamed) -> Any:
                changed = synthetic_reference()
                changed["observation"] = dict(changed["observation"])
                changed["observation"][renamed] = True
                return project_subinterpreter_reference(changed)
            reject("reject-collided-interpreter-observation-" + original, collision)
            def weakened(original: str = original, renamed: str = renamed) -> Any:
                changed, pins = synthetic_candidate()
                changed["observation"] = dict(changed["observation"])
                changed["observation"][renamed] = False
                return validate_subinterpreter_case(changed, synthetic_reference(),
                                                   family_spec("rust"), pins)
            reject("reject-weakened-interpreter-observation-" + original, weakened)
        for field in sorted(REFERENCE_ONLY_FIELDS):
            def launder(field: str = field) -> Any:
                changed, pins = synthetic_candidate()
                changed[field] = reference[field]
                return validate_subinterpreter_case(changed, reference,
                                                   family_spec("rust"), pins)
            reject("reject-reference-owner-laundering-" + field, launder)
        accept("verify-32-real-threads-and-1024-simultaneous-events",
               lambda: validate_thread_evidence(synthetic_threads()))
        for field in ("actual_thread_starts", "actual_thread_joins",
                      "actual_thread_case_executions", "actual_regex_api_calls",
                      "metadata_case_count", "metadata_cases_are_threaded_subset",
                      "all_barriers_verified", "all_thread_joins_verified",
                      "orphan_threads", "thread_failures", "warning_records_sha256"):
            def altered_threads(field: str = field) -> Any:
                forged = synthetic_threads()
                old = forged[field]
                forged[field] = (not old if type(old) is bool else
                    old + 1 if type(old) is int else
                    [{"failure": "concealed"}] if type(old) is list else
                    "0" * 64)
                return validate_thread_evidence(forged)
            reject("reject-fabricated-thread-" + field, altered_threads)
        for field in ("started", "joined", "alive_after_join"):
            def changed_lifecycle(field: str = field) -> Any:
                forged = synthetic_threads()
                forged["thread_lifecycle"][0][field] = (
                    not forged["thread_lifecycle"][0][field])
                return validate_thread_evidence(forged)
            reject("reject-forged-thread-lifecycle-" + field, changed_lifecycle)
        for field in ("status", "start_barrier_passed", "completion_barrier_arrived"):
            def changed_barrier(field: str = field) -> Any:
                forged = synthetic_threads()
                forged["thread_events"][0][field] = (
                    "FAIL" if field == "status" else False)
                return validate_thread_evidence(forged)
            reject("reject-forged-real-thread-barrier-" + field, changed_barrier)
        stream = accept("capture-full-synthetic-candidate-stream",
                        lambda: capture_stream(b"complete genuine synthetic stream\n"))
        accept("restore-full-synthetic-candidate-stream",
               lambda: require(restore_stream(stream, "synthetic")
                   == b"complete genuine synthetic stream\n", "retain full process bytes"))
        for field in ("encoding", "data", "bytes", "sha256", "complete"):
            def forged_stream(field: str = field) -> Any:
                changed = dict(stream)
                old = changed[field]
                changed[field] = (not old if type(old) is bool else
                    old + 1 if type(old) is int else
                    "invalid-base64!" if field == "data" else "forged")
                return restore_stream(changed, field)
            reject("reject-forged-complete-stream-" + field, forged_stream)
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}',
                    b'{"x":-Infinity}', b"[]", b"null", b"", b"{", b"\xff"):
            reject("reject-malformed-nonfinite-or-duplicate-json-" + repr(raw),
                   lambda raw=raw: decode_document(raw, "synthetic"))
        accept("preserve-genuine-escaped-lone-surrogate",
               lambda: require(decode_document(b'{"x":"\\ud800"}', "synthetic")["x"]
                   == "\ud800", "never alter a genuine original public surrogate"))
        allowed = frozenset({P0_RELATIVE})
        accept("accept-only-exact-frozen-inventory-path",
               lambda: safe_relative(P0_RELATIVE, allowed))
        for unsafe in ("/etc/passwd", "../GOAL.md", "oracle/../GOAL.md",
                       "holdout/cases.json", "hidden/cases.json",
                       "benchmarks/final.json", "performance/results.json",
                       "candidates/_rust_engine.so", "", None, 3,
                       "oracle\\phase1\\p0.json", "oracle/phase1/\x00.json"):
            reject("reject-hidden-or-unsafe-correctness-path-" + repr(unsafe),
                   lambda unsafe=unsafe: safe_relative(unsafe, allowed))
        for value in ("p0-v2", "rust-1", "c", "zig-42"):
            accept("accept-safe-publication-label-" + value,
                   lambda value=value: checked_label(value))
        for value in (None, "", "../outside", "/tmp/outside", "RUST",
                      "with spaces", "a/b", "a" * 49, 1):
            reject("reject-unsafe-publication-label-" + repr(value),
                   lambda value=value: checked_label(value))
        for forged in (None, "", "go", "stdlib", "_sre", "regex", "re2",
                       "rust_candidate", "all", 0, [], {}):
            reject("reject-unfrozen-or-delegating-family-" + repr(forged),
                   lambda forged=forged: family_spec(forged))
        for action, operation in (
            ("actual-file-read", lambda: builtins.open(str(ROOT / "GOAL.md"), "rb")),
            ("actual-directory-read", lambda: os.open(str(ROOT), os.O_RDONLY)),
            ("actual-file-write", lambda: Path("forbidden").write_text("forbidden")),
            ("actual-candidate-import", lambda: importlib.import_module(
                "candidates.rust_candidate")),
            ("actual-reference-process", lambda: subprocess.Popen([PINNED_PYTHON])),
            ("actual-candidate-process", lambda: subprocess.run([PINNED_PYTHON])),
            ("actual-thread", lambda: threading.Thread(target=lambda: None).start()),
            ("actual-performance-clock", lambda: time.perf_counter()),
            ("actual-wall-clock", lambda: time.time()),
            ("actual-garbage-collection", lambda: gc.collect()),
            ("actual-canonical-native-promotion", lambda: os.replace(
                "forbidden-source", "forbidden-target")),
        ):
            reject("block-source-only-" + action, operation)
        require(len(accepted) >= 25 and len(rejected) >= 300,
                "the source-only P0 V2 positive and hostile controls are incomplete")
        require(effects["blocked_reads"] >= 2
                and effects["blocked_writes"] >= 1
                and effects["blocked_imports"] >= 1
                and effects["blocked_processes"] >= 2
                and effects["blocked_threads"] >= 1
                and effects["blocked_clocks"] >= 2
                and effects["blocked_gc_collections"] >= 1
                and effects["blocked_promotions"] >= 1,
                "exercise every genuine zero-effect source-only boundary")
        snapshot = dict(effects)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a source-only self-test cannot actually import a candidate")
    return {"schema": SCHEMA + "-source-only-self-test", "status": "PASS",
        "source_only": True, "python": "3.14.6", "goal_sha256": GOAL_SHA256,
        "phase1_inventory_sha256": P0_SHA256,
        "phase1_verifier_sha256": P0_VERIFIER_SHA256,
        "preserved_v1_source_sha256": V1_SHA256,
        "suite_count": len(FROZEN_SUITES),
        "case_execution_denominator": CASE_DENOMINATOR,
        "candidate_families": list(FAMILY_SPECS),
        "synthetic_positive_control_count": len(accepted),
        "synthetic_rejection_control_count": len(rejected),
        "positive_controls": accepted, "rejection_controls": rejected,
        "source_only_effects": snapshot, "actual_reference_workers": 0,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_thread_starts": 0, "actual_interpreter_creations": 0,
        "actual_source_builds": 0, "actual_native_promotions": 0,
        "actual_guard_root_rebindings": 0, "native_libraries_loaded": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED", "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False}


def authenticate_module(relative: str, expected: str,
                        allowed: frozenset[str]) -> types.ModuleType:
    read_owned(relative, expected, allowed=allowed)
    name = relative.removesuffix(".py").replace("/", ".")
    module = importlib.import_module(name)
    require(type(module) is types.ModuleType
            and module.__name__ == name
            and os.path.abspath(module.__file__) == str(ROOT / relative),
            "only a frozen unchanged canonical-root owner may be imported: " + relative)
    read_owned(relative, expected, allowed=allowed)
    return module


def authenticate_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    dynamic = {
        SOURCE_RELATIVE: valid_sha256(options.source_sha256, "V2 runner"),
        PROTOCOL_RELATIVE: valid_sha256(options.protocol_sha256, "V2 prose"),
        DOCUMENT_RELATIVE: valid_sha256(options.document_sha256, "V2 inventory"),
        SUBINTERPRETER_RELATIVE: valid_sha256(
            options.subinterpreter_source_sha256, "separately frozen interpreter source"),
        SUBINTERPRETER_DOCUMENT_RELATIVE: valid_sha256(
            options.subinterpreter_protocol_sha256, "separately frozen interpreter protocol"),
        SUBINTERPRETER_EXPLANATION_RELATIVE: valid_sha256(
            options.subinterpreter_explanation_sha256, "separately frozen interpreter prose"),
        ACTIVATION_RELATIVE: valid_sha256(
            options.activation_source_sha256, "separately frozen canonical activator"),
        ACTIVATION_PROTOCOL_RELATIVE: valid_sha256(
            options.activation_protocol_sha256, "separately frozen canonical activation"),
    }
    fixed = {"GOAL.md": GOAL_SHA256, P0_RELATIVE: P0_SHA256,
        P0_EXPLANATION_RELATIVE: P0_EXPLANATION_SHA256,
        P0_VERIFIER_RELATIVE: P0_VERIFIER_SHA256,
        V1_RELATIVE: V1_SHA256, V1_DOCUMENT_RELATIVE: V1_DOCUMENT_SHA256,
        V1_PROTOCOL_RELATIVE: V1_PROTOCOL_SHA256,
        BUILD_RELATIVE: BUILD_SHA256,
        BUILD_PROTOCOL_RELATIVE: BUILD_PROTOCOL_SHA256,
        AUDIT_RELATIVE: AUDIT_SHA256,
        AUDIT_PROTOCOL_RELATIVE: AUDIT_PROTOCOL_SHA256,
        CORE_RELATIVE: CORE_SHA256,
        RECORDING_AUDIT_RELATIVE: RECORDING_AUDIT_SHA256,
        V19_VALIDATOR_RELATIVE: V19_VALIDATOR_SHA256}
    for suite in FROZEN_SUITES:
        fixed[suite.source_relative] = suite.source_sha256
        if suite.recorder_relative is not None and suite.recorder_sha256 is not None:
            fixed[suite.recorder_relative] = suite.recorder_sha256
    allowed = frozenset({*fixed, *dynamic})
    raw: dict[str, bytes] = {}
    for relative, expected in {**fixed, **dynamic}.items():
        raw[relative] = read_owned(relative, expected, allowed=allowed)
    document = validate_protocol_document(decode_document(
        raw[DOCUMENT_RELATIVE], "exact V2 candidate protocol"))
    phase1 = validate_phase1_document(decode_document(raw[P0_RELATIVE],
                                                       "complete frozen phase one"))
    v1 = authenticate_module(V1_RELATIVE, V1_SHA256, allowed)
    require(v1.validate_protocol_document(decode_document(
        raw[V1_DOCUMENT_RELATIVE], "unchanged frozen V1 protocol")),
            "preserve the entire published V1 candidate freeze")
    inventory, verified = v1.authenticate_phase1()
    require(canonical(inventory) == canonical(phase1)
            and type(verified) is dict and verified.get("status") == "PASS"
            and verified.get("suite_count") == 13
            and verified.get("case_execution_denominator") == CASE_DENOMINATOR
            and verified.get("new_candidate_workers") == 0
            and verified.get("hidden_cases_read") == 0
            and verified.get("performance_files_read") == 0
            and verified.get("clock_samples") == 0,
            "authenticate the full real two-reference Phase 1 without starting a reference")
    nested = authenticate_module(SUBINTERPRETER_RELATIVE,
                                 options.subinterpreter_source_sha256, allowed)
    require(getattr(nested, "SCHEMA", None) == SUBINTERPRETER_SCHEMA,
            "the separately frozen actual interpreter controller changed")
    return {"phase1": phase1, "phase1_verification": verified,
            "protocol": document, "v1": v1, "subinterpreter": nested,
            "allowed_paths": allowed}


def make_nested_arguments(options: argparse.Namespace, *, label: str) -> list[str]:
    arguments = ["--record-candidate", "--family", options.candidate,
        "--label", checked_label(label),
        "--source-sha256", valid_sha256(options.subinterpreter_source_sha256,
                                         "real subinterpreter runner"),
        "--protocol-sha256", valid_sha256(options.subinterpreter_protocol_sha256,
                                           "real subinterpreter protocol"),
        "--explanation-sha256", valid_sha256(options.subinterpreter_explanation_sha256,
                                              "real subinterpreter prose"),
        "--build-label", checked_label(options.build_label),
        "--build-archive-sha256", valid_sha256(options.build_archive_sha256,
                                                "actual V2 native build archive"),
        "--build-receipt-sha256", valid_sha256(options.build_receipt_sha256,
                                                "actual V2 native build receipt"),
        "--build-source-sha256", BUILD_SHA256,
        "--build-protocol-sha256", BUILD_PROTOCOL_SHA256,
        "--activation-root", options.activation_root,
        "--activation-source-sha256", valid_sha256(options.activation_source_sha256,
                                                     "canonical activator"),
        "--activation-protocol-sha256", valid_sha256(options.activation_protocol_sha256,
                                                       "canonical activation protocol"),
        "--activation-report-sha256", valid_sha256(options.activation_report_sha256,
                                                     "actual canonical promotion report"),
        "--activation-receipt-sha256", valid_sha256(options.activation_receipt_sha256,
                                                      "actual canonical promotion receipt"),
        "--candidate-source-sha256", valid_sha256(options.candidate_source_sha256,
                                                   "selected candidate adapter"),
        "--native-engine-sha256", valid_sha256(options.native_engine_sha256,
                                                "actual source-built native engine"),
        "--native-bridge-sha256", valid_sha256(options.native_bridge_sha256,
                                                "actual source-built native bridge")]
    family = family_spec(options.candidate)
    for relative, owner in parse_source_owners(
            options.owned_source_sha256, family).items():
        arguments.extend(("--owned-source-sha256", relative + "=" + owner))
    return arguments


def authenticate_canonical_activation(options: argparse.Namespace,
                                      context: Mapping[str, Any]) -> dict[str, Any]:
    family = family_spec(options.candidate)
    owners = parse_source_owners(options.owned_source_sha256, family)
    pins = {"source": valid_sha256(options.candidate_source_sha256, "adapter"),
            "native_engine": valid_sha256(options.native_engine_sha256, "engine"),
            "native_bridge": valid_sha256(options.native_bridge_sha256, "bridge")}
    require(owners.get(family.adapter) == pins["source"]
            and (pins["native_engine"] == pins["native_bridge"])
            is (family.name == "c"),
            "reject crossed family ownership or an unaudited native bridge")
    root = options.activation_root
    require(type(root) is str and root.isascii()
            and root.startswith(ACTIVATION_PREFIX + family.name + "-")
            and root.count("/") == 2 and os.path.normpath(root) == root,
            "require the exact owner-only canonical promotion recovery root")
    nested = context["subinterpreter"]
    arguments = nested.parse_arguments(make_nested_arguments(
        options, label=checked_label(options.label)))
    prerequisite = nested.authenticate_prerequisites(arguments)
    require(type(prerequisite) is dict,
            "require a genuinely authenticated V2 build and canonical activation")
    build = prerequisite.get("source_build_v2")
    require(type(build) is dict and build.get("schema") == BUILD_SCHEMA
            and build.get("status") == "PASS"
            and build.get("family") == family.name
            and build.get("source_sha256") == BUILD_SHA256
            and build.get("protocol_sha256") == BUILD_PROTOCOL_SHA256
            and build.get("archive_sha256") == options.build_archive_sha256
            and build.get("receipt_sha256") == options.build_receipt_sha256
            and build.get("independent_fresh_phase_count") == 2,
            "never authorize historical or unproved native binary bytes")
    activation = prerequisite.get("canonical_activation")
    require(type(activation) is dict and activation.get("schema") == ACTIVATION_SCHEMA
            and activation.get("status") == "PASS"
            and activation.get("family") == family.name
            and activation.get("promotion_mode") == "recoverable-canonical-promotion"
            and activation.get("candidate_import_root") == str(ROOT)
            and activation.get("backup_root") == root
            and type(activation.get("recovery_journal")) is dict
            and type(activation.get("backup_entries")) is dict
            and type(activation.get("native_owners")) is dict
            and type(activation.get("guard_owners")) is dict,
            "fail closed until recoverable unchanged-root V2 promotion is independently proved")
    require(prerequisite.get("pins") == pins
            and prerequisite.get("source_owners") == owners,
            "the authenticated canonical activation changed candidate source owners")
    canonical_pins = context["v1"].validate_owners(
        context["v1"].family_spec(family.name),
        adapter=pins["source"], engine=pins["native_engine"],
        bridge=pins["native_bridge"], source_entries=options.owned_source_sha256)
    require(canonical_pins == pins,
            "never import a stale or unproved canonical repository native binary")
    return {"family": family, "pins": pins, "owners": owners,
            "build": build, "activation": activation,
            "nested_arguments": arguments, "canonical_pins": canonical_pins}


def encoded_process(command: Sequence[str]) -> dict[str, Any]:
    require(type(command) in (tuple, list)
            and command[:3] == [PINNED_PYTHON, "-I", "-B"]
            and all(type(item) is str for item in command),
            "run only an exact isolated pinned actual candidate producer")
    environment = {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                   "LC_ALL": "C", "PATH": "/usr/bin:/bin"}
    process = subprocess.Popen(list(command), shell=False, cwd=str(ROOT),
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=environment)
    try:
        stdout, stderr = process.communicate(timeout=PROCESS_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        process.kill()
        stdout, stderr = process.communicate()
        return {"status": "FAIL", "timed_out": True, "pid": process.pid,
                "returncode": process.returncode,
                "timeout_type": type(error).__name__,
                "stdout": capture_stream(stdout), "stderr": capture_stream(stderr)}
    return {"status": "OBSERVED", "timed_out": False,
            "pid": process.pid, "returncode": process.returncode,
            "signal": -process.returncode if process.returncode < 0 else None,
            "stdout": capture_stream(stdout), "stderr": capture_stream(stderr)}


def direct_worker(options: argparse.Namespace) -> dict[str, Any]:
    context = authenticate_frozen_context(options)
    approval = authenticate_canonical_activation(options, context)
    suite = suite_spec(options.suite)
    family = approval["family"]
    v1 = context["v1"]
    require(suite.name in {"public_surface_v19", "pep688_v4",
                            "threaded_pattern_v1"},
            "direct observation is allowed only for three genuine source-owned suites")
    if suite.name == "public_surface_v19":
        harness_relative = "tools/rust_original_cpython_suite_v1.py"
        harness_sha256 = "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"
        harness = authenticate_module(harness_relative, harness_sha256,
                                     frozenset({harness_relative}))
        original_locale = locale.setlocale(locale.LC_CTYPE)
        original_path = os.environ.get("LOCPATH")
        with harness.authentic_private_locales() as evidence:
            result = v1.run_direct_candidate_worker(
                v1.suite_spec(suite.name), v1.family_spec(family.name),
                approval["pins"], locale_names={"iso8859_1": "en_US.iso88591",
                                                 "utf8": "en_US.utf8"})
        require(locale.setlocale(locale.LC_CTYPE) == original_locale
                and os.environ.get("LOCPATH") == original_path
                and evidence.get("actual_localedef_workers") == 2
                and evidence.get("iso_8859_1_verified") is True
                and evidence.get("utf_8_verified") is True
                and evidence.get("temporary_directory_removed") is True,
                "genuinely provision and clean both differently encoded localedef locales")
        result["resource_evidence"]["actual_private_locale_provision"] = evidence
    else:
        result = v1.run_direct_candidate_worker(v1.suite_spec(suite.name),
            v1.family_spec(family.name), approval["pins"])
    require(type(result) is dict and result.get("status") == "OBSERVED"
            and result.get("suite") == suite.name
            and result.get("candidate_family") == family.name
            and result.get("actual_candidate_cases") == suite.case_count
            and result.get("matrix_sha256") == suite.matrix_sha256
            and result.get("reference_records_sha256") == suite.reference_sha256,
            "retain every actual frozen source-owned P0 candidate observation")
    if suite.name == "threaded_pattern_v1":
        validate_thread_evidence(result.get("resource_evidence"))
    if suite.name == "public_surface_v19":
        evidence = result.get("resource_evidence")
        require(type(evidence) is dict
                and evidence.get("real_locale_case_count") == 64
                and evidence.get("real_locale_transition_count") == 192
                and evidence.get("used_original_v17_evaluator") is True
                and evidence.get("used_original_v19_cycle_safe_normalizer") is True,
                "never approximate the original genuine real-locale public oracle")
    return result


def frozen_owner_arguments(options: argparse.Namespace) -> list[str]:
    pairs = (("source", options.source_sha256),
             ("protocol", options.protocol_sha256),
             ("document", options.document_sha256),
             ("subinterpreter-source", options.subinterpreter_source_sha256),
             ("subinterpreter-protocol", options.subinterpreter_protocol_sha256),
             ("subinterpreter-explanation", options.subinterpreter_explanation_sha256),
             ("build-archive", options.build_archive_sha256),
             ("build-receipt", options.build_receipt_sha256),
             ("activation-source", options.activation_source_sha256),
             ("activation-protocol", options.activation_protocol_sha256),
             ("activation-report", options.activation_report_sha256),
             ("activation-receipt", options.activation_receipt_sha256),
             ("candidate-source", options.candidate_source_sha256),
             ("native-engine", options.native_engine_sha256),
             ("native-bridge", options.native_bridge_sha256))
    result: list[str] = []
    for name, value in pairs:
        result.extend(("--" + name + "-sha256", valid_sha256(value, name)))
    result.extend(("--candidate", options.candidate,
                   "--label", checked_label(options.label),
                   "--build-label", checked_label(options.build_label),
                   "--activation-root", options.activation_root))
    for owner in options.owned_source_sha256:
        result.extend(("--owned-source-sha256", owner))
    return result


def producer_command(suite: SuiteSpec, options: argparse.Namespace,
                     phase1_row: Mapping[str, Any]) -> list[str]:
    family = family_spec(options.candidate)
    executable = [PINNED_PYTHON, "-I", "-B"]
    pins = ["--candidate-source-sha256", options.candidate_source_sha256,
            "--native-engine-sha256", options.native_engine_sha256,
            "--native-bridge-sha256", options.native_bridge_sha256]
    owned: list[str] = []
    for entry in options.owned_source_sha256:
        owned.extend(("--owned-source-sha256", entry))
    if suite.name == "original_bounded_v5":
        return [*executable, str(ROOT / suite.source_relative),
                "--internal-worker", "--family", family.name,
                "--oracle-source-sha256", suite.source_sha256,
                "--matrix-sha256", suite.matrix_sha256, *pins]
    if suite.name in {"public_v3", "scanner_v3", "buffer_v3"}:
        category = {"public_v3": "public", "scanner_v3": "scanner",
                    "buffer_v3": "buffer"}[suite.name]
        return [*executable, str(ROOT / CORE_RELATIVE), "--internal-worker",
                "--category", category, "--family", family.name,
                "--role", "candidate-" + family.name,
                "--oracle-source-sha256", CORE_SHA256,
                "--matrix-sha256", suite.matrix_sha256, *pins, *owned]
    if suite.name in {"managed_v1", "scanner_verbose_v1", "public_types_v1",
                      "substitution_v2", "shape_v2"}:
        require(suite.recorder_relative is not None
                and suite.recorder_sha256 is not None,
                "only the exact frozen owner may record this candidate")
        baseline = phase1_row.get("baseline")
        require(type(baseline) is dict and baseline.get("status") == "PASS"
                and type(baseline.get("compressed_report")) is dict
                and type(baseline.get("publication_receipt")) is dict,
                "the exact recorder-owned archived baseline and receipt are mandatory")
        suffix = {"managed_v1": "managed", "scanner_verbose_v1": "verbose",
                  "public_types_v1": "types", "substitution_v2": "substitution",
                  "shape_v2": "shape"}[suite.name]
        label = checked_label(options.label + "-" + suffix)
        command = [*executable, str(ROOT / suite.recorder_relative),
            "--record-candidate", "--candidate", family.name, "--label", label,
            "--recorder-source-sha256", suite.recorder_sha256,
            "--oracle-source-sha256", suite.source_sha256,
            "--matrix-sha256", suite.matrix_sha256,
            "--baseline-receipt-sha256", valid_sha256(
                baseline["publication_receipt"].get("sha256"),
                suite.name + " original baseline receipt"),
            "--baseline-archive-sha256", valid_sha256(
                baseline["compressed_report"].get("sha256"),
                suite.name + " original compressed baseline"),
            "--baseline-records-sha256", suite.reference_sha256,
            *pins, *owned]
        if suite.name != "managed_v1":
            command.extend(("--ownership-audit-source-sha256",
                            RECORDING_AUDIT_SHA256,
                            "--baseline-label", suite.baseline_label))
        if suite.name == "public_types_v1":
            command.extend(("--native-artifact-sha256",
                family.engine + "=" + options.native_engine_sha256))
            if family.bridge != family.engine:
                command.extend(("--native-artifact-sha256",
                    family.bridge + "=" + options.native_bridge_sha256))
        return command
    if suite.name == "subinterpreter_v2":
        return [*executable, str(ROOT / SUBINTERPRETER_RELATIVE),
                *make_nested_arguments(options,
                    label=checked_label(options.label + "-subinterpreters"))]
    if suite.name in {"public_surface_v19", "pep688_v4",
                      "threaded_pattern_v1"}:
        return [*executable, str(ROOT / SOURCE_RELATIVE),
                "--internal-candidate-worker", "--suite", suite.name,
                *frozen_owner_arguments(options)]
    raise CandidateGateError("reject any unimplemented original producer route")


def publication_owner(value: Any, *, suite: str,
                      maximum: int) -> dict[str, Any]:
    require(type(value) is dict, "a genuine suite publication is mandatory: " + suite)
    relative = value.get("path", value.get("relative"))
    expected = value.get("sha256")
    raw = read_owned(relative, valid_sha256(expected, suite + " publication"),
                     allowed=frozenset({relative}), maximum=maximum)
    claimed = value.get("bytes", value.get("size_bytes"))
    require(type(claimed) is int and claimed == len(raw),
            "a complete durable suite publication was truncated: " + suite)
    return {"path": relative, "sha256": expected, "bytes": len(raw)}


def validate_specialized_result(value: Any, suite: SuiteSpec,
                                options: argparse.Namespace) -> dict[str, Any]:
    require(type(value) is dict and value.get("candidate_family") == options.candidate
            and value.get("status") == "PASS"
            and value.get("publication_status") == "PASS"
            and value.get("matrix_sha256") == suite.matrix_sha256
            and value.get("baseline_records_sha256") == suite.reference_sha256
            and value.get("validated_baseline_record_count") == suite.case_count
            and value.get("validated_candidate_record_count") == suite.case_count
            and value.get("mismatch_count") == 0
            and value.get("actual_candidate_process_invocations") == 1
            and value.get("clock_samples") == 0
            and value.get("timing_trials_run") == 0
            and value.get("benchmark_files_read") == 0
            and value.get("hidden_cases_read") == 0
            and value.get("performance") == "NOT MEASURED"
            and value.get("candidate_qualified_for_hidden_benchmark") is False
            and value.get("final_winner_selected") is False,
            "an original recorder concealed an actual mismatch or failed case: " + suite.name)
    archive = publication_owner(value.get("report_publication"),
                                suite=suite.name + " complete candidate archive",
                                maximum=MAX_ARCHIVE_BYTES)
    receipt = publication_owner(value.get("receipt_publication"),
                                suite=suite.name + " complete publication receipt",
                                maximum=MAX_SOURCE_BYTES)
    return {"actual_candidate_case_count": suite.case_count,
            "candidate_records_location": archive,
            "candidate_publication_receipt": receipt,
            "mismatch_count": 0, "all_failure_reasons": [],
            "source_owned_recorder_result": value}


def validate_original_result(value: Any, suite: SuiteSpec,
                             options: argparse.Namespace) -> dict[str, Any]:
    require(type(value) is dict and value.get("status") == "PASS"
            and value.get("candidate_family") == options.candidate
            and value.get("matrix_sha256") == suite.matrix_sha256
            and value.get("records_sha256") == suite.reference_sha256
            and value.get("actual_public_method_count") == 152
            and value.get("private_waiver_count") == 13
            and value.get("pass_count") == 151
            and value.get("skip_count") == 1
            and value.get("failure_count") == 0
            and type(value.get("private_waivers")) is list
            and len(value["private_waivers"]) == 13
            and type(value.get("records")) is list
            and len(value["records"]) == 152
            and value.get("actual_candidate_workers") == 1,
            "preserve all 152 upstream records, 151 runnable cases, and 13 named waivers")
    skipped = [row for row in value["records"] if row.get("status") == "SKIP"]
    require(len(skipped) == 1 and skipped[0].get("test")
            == "ReTests.test_memory_leaks"
            and skipped[0].get("skip_reasons") == ["requires debug build"],
            "the only original public debug skip cannot be hidden or changed")
    return {"actual_candidate_case_count": 151,
            "actual_public_record_count": 152,
            "actual_debug_skip_count": 1,
            "actual_named_private_waiver_count": 13,
            "candidate_records": value["records"],
            "candidate_records_sha256": value["records_sha256"],
            "native_provenance": value.get("native_provenance"),
            "matcher_guard": value.get("matcher_guard")}


def validate_category_result(value: Any, suite: SuiteSpec,
                             options: argparse.Namespace) -> dict[str, Any]:
    category = {"public_v3": "public", "scanner_v3": "scanner",
                "buffer_v3": "buffer"}[suite.name]
    require(type(value) is dict and value.get("status") == "OBSERVED"
            and value.get("category") == category
            and value.get("role") == "candidate-" + options.candidate
            and value.get("candidate_family") == options.candidate
            and value.get("controller_source_sha256") == CORE_SHA256
            and value.get("category_source_sha256") == suite.source_sha256
            and value.get("matrix_sha256") == suite.matrix_sha256
            and value.get("frozen_baseline_records_sha256") == suite.reference_sha256
            and value.get("case_count") == suite.case_count
            and type(value.get("records")) is list
            and len(value["records"]) == suite.case_count
            and value.get("records_sha256") == suite.reference_sha256
            and value.get("actual_candidate_workers") == 1
            and value.get("clock_samples") == 0
            and value.get("hidden_cases_read") == 0,
            "all authentic common-controller candidate cases must equal frozen Python")
    return {"actual_candidate_case_count": suite.case_count,
            "candidate_records": value["records"],
            "candidate_records_sha256": value["records_sha256"],
            "native_provenance": value.get("native_provenance"),
            "matcher_guard": value.get("matcher_guard")}


def validate_direct_result(value: Any, suite: SuiteSpec,
                           options: argparse.Namespace) -> dict[str, Any]:
    require(type(value) is dict and value.get("status") == "OBSERVED"
            and value.get("suite") == suite.name
            and value.get("candidate_family") == options.candidate
            and value.get("matrix_sha256") == suite.matrix_sha256
            and value.get("actual_candidate_cases") == suite.case_count
            and type(value.get("candidate_records")) is list
            and len(value["candidate_records"]) == suite.case_count
            and value.get("candidate_records_sha256") == suite.reference_sha256
            and value.get("reference_records_sha256") == suite.reference_sha256
            and value.get("actual_candidate_workers") == 1
            and value.get("clock_samples") == 0
            and value.get("benchmark_files_read") == 0
            and value.get("hidden_cases_read") == 0,
            "a genuine source-owned P0 candidate vector differs from frozen Python")
    metadata = value.get("resource_evidence")
    if suite.name == "threaded_pattern_v1":
        validate_thread_evidence(metadata)
    elif suite.name == "public_surface_v19":
        require(type(metadata) is dict
                and metadata.get("real_locale_case_count") == 64
                and metadata.get("real_locale_transition_count") == 192
                and metadata.get("used_original_v17_evaluator") is True
                and metadata.get("used_original_v19_cycle_safe_normalizer") is True,
                "retain all original real locales and normalization")
    return {"actual_candidate_case_count": suite.case_count,
            "candidate_records": value["candidate_records"],
            "candidate_records_sha256": value["candidate_records_sha256"],
            "native_provenance": value.get("native_provenance"),
            "matcher_guard": value.get("matcher_guard"),
            "resource_evidence": metadata}


def validate_subinterpreter_result(value: Any, suite: SuiteSpec,
                                   options: argparse.Namespace,
                                   nested: types.ModuleType) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("schema") == SUBINTERPRETER_SCHEMA + "-published-candidate-result"
            and value.get("status") == "PASS"
            and value.get("candidate_family") == options.candidate
            and value.get("failure_preserved") is False
            and value.get("directory_fsync") is True
            and value.get("performance") == "NOT MEASURED"
            and value.get("holdout") == "NOT OPENED",
            "only a genuinely successful published real-subinterpreter run qualifies")
    archive = publication_owner(value.get("archive"),
                                suite="actual subinterpreter full archive",
                                maximum=MAX_ARCHIVE_BYTES)
    receipt = publication_owner(value.get("receipt"),
                                suite="actual subinterpreter durable receipt",
                                maximum=MAX_SOURCE_BYTES)
    compressed = read_owned(archive["path"], archive["sha256"],
                            allowed=frozenset({archive["path"]}),
                            maximum=MAX_ARCHIVE_BYTES)
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as stream:
            plain = stream.read(MAX_STREAM_BYTES + 1)
    except (OSError, EOFError, gzip.BadGzipFile) as error:
        raise CandidateGateError("the genuine complete interpreter archive is invalid") from error
    require(0 < len(plain) <= MAX_STREAM_BYTES,
            "the genuine candidate interpreter archive exceeds its frozen bound")
    report = decode_document(plain, "full published real interpreter candidate")
    require(report.get("status") == "PASS"
            and report.get("candidate_family") == options.candidate
            and type(report.get("worker")) is dict,
            "the actual interpreter worker was omitted from its durable archive")
    worker = report["worker"]
    require(worker.get("case_count") == suite.case_count
            and worker.get("actual_case_interpreter_exec_calls") == 394
            and worker.get("actual_initialization_interpreter_exec_calls") == 11
            and worker.get("actual_guard_cleanup_interpreter_exec_calls") == 11
            and worker.get("actual_interpreters_created") == 11
            and worker.get("actual_interpreters_destroyed") == 11
            and worker.get("fresh_interpreter_case_count") == 8
            and worker.get("reference_records_sha256") == suite.reference_sha256
            and worker.get("projected_reference_records_sha256")
            == PROJECTED_REFERENCE_SHA256
            and all(worker.get(name) is True for name in (
                "all_real_pipes_read_to_eof", "all_real_pipe_descriptors_closed",
                "interpreter_live_set_restored", "locale_restored",
                "simultaneous_interpreters_verified",
                "b_closed_before_a_reexecution", "fresh_c_verified",
                "persistent_original_v5_per_interpreter")),
            "require all 394 actual guarded A/B/A/fresh interpreter observations")
    reference = nested.load_original_baseline()
    exact = nested.validate_worker_document(
        worker, spec=nested.checked_family(options.candidate),
        pins={"source": options.candidate_source_sha256,
              "native_engine": options.native_engine_sha256,
              "native_bridge": options.native_bridge_sha256},
        original=reference, expected_pid=worker.get("pid"))
    require(exact is worker or canonical(exact) == canonical(worker),
            "revalidate every original reference against every real interpreter case")
    return {"actual_candidate_case_count": suite.case_count,
            "candidate_records_location": archive,
            "candidate_publication_receipt": receipt,
            "candidate_records": worker["records"],
            "peer_candidate_records": worker["peer_records"],
            "repeated_a_candidate_records": worker["repeated_a_records"],
            "projected_reference_records_sha256": PROJECTED_REFERENCE_SHA256,
            "actual_interpreter_ids": worker["actual_interpreter_ids"],
            "actual_case_interpreter_exec_calls": 394,
            "actual_interpreters_created": 11,
            "actual_interpreters_destroyed": 11}


def observe_actual_suite(suite: SuiteSpec, options: argparse.Namespace,
                         context: Mapping[str, Any],
                         approval: Mapping[str, Any]) -> dict[str, Any]:
    phase1 = next(item for item in context["phase1"]["suites"]
                  if item["id"] == suite.name)
    current = context["v1"].validate_owners(
        context["v1"].family_spec(options.candidate),
        adapter=options.candidate_source_sha256,
        engine=options.native_engine_sha256,
        bridge=options.native_bridge_sha256,
        source_entries=options.owned_source_sha256)
    require(current == approval["pins"],
            "the canonically activated native binary changed before a real suite")
    process = encoded_process(producer_command(suite, options, phase1))
    evidence: dict[str, Any] = {
        "suite": suite.name, "candidate_family": options.candidate,
        "case_execution_denominator": suite.case_count,
        "matrix_sha256": suite.matrix_sha256,
        "reference_records_sha256": suite.reference_sha256,
        "producer_source_path": suite.source_relative,
        "producer_source_sha256": suite.source_sha256,
        "actual_process": process,
        "status": "FAIL", "failure": None}
    try:
        require(process.get("timed_out") is False
                and process.get("returncode") in (0, 1),
                "retain a genuine candidate crash, timeout, or fatal signal")
        stdout = restore_stream(process.get("stdout"), suite.name + " complete stdout")
        stderr = restore_stream(process.get("stderr"), suite.name + " complete stderr")
        require(stderr == b"", "a genuine candidate process emitted failure stderr")
        actual = decode_document(stdout, suite.name + " genuine producer result")
        require(process["returncode"] == 0,
                "a source-owned candidate reported a genuine failed P0 case")
        if suite.name == "original_bounded_v5":
            outcome = validate_original_result(actual, suite, options)
        elif suite.name in {"public_v3", "scanner_v3", "buffer_v3"}:
            outcome = validate_category_result(actual, suite, options)
        elif suite.name in {"managed_v1", "scanner_verbose_v1",
                            "public_types_v1", "substitution_v2", "shape_v2"}:
            outcome = validate_specialized_result(actual, suite, options)
        elif suite.name == "subinterpreter_v2":
            outcome = validate_subinterpreter_result(actual, suite, options,
                                                     context["subinterpreter"])
        else:
            outcome = validate_direct_result(actual, suite, options)
        require(outcome.get("actual_candidate_case_count") == suite.case_count,
                "the complete actual source-ordered denominator changed")
        evidence.update(status="PASS", **outcome)
    except (CandidateGateError, OSError, ValueError, TypeError, KeyError,
            OverflowError, UnicodeError, RecursionError) as error:
        evidence["failure"] = {"type": type(error).__qualname__,
            "message": str(error),
            "traceback": traceback.format_exception(type(error), error,
                                                    error.__traceback__)}
    final = context["v1"].validate_owners(
        context["v1"].family_spec(options.candidate),
        adapter=options.candidate_source_sha256,
        engine=options.native_engine_sha256,
        bridge=options.native_bridge_sha256,
        source_entries=options.owned_source_sha256)
    require(final == approval["pins"],
            "the canonically activated native binary changed during a frozen suite")
    return evidence


def write_fresh_evidence(directory: int, basename: str,
                         content: bytes) -> dict[str, Any]:
    require(type(directory) is int and directory >= 0
            and type(basename) is str and "/" not in basename
            and basename not in {"", ".", ".."}
            and type(content) is bytes and 0 < len(content) <= MAX_STREAM_BYTES,
            "publish one exact bounded fresh candidate evidence file")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(basename, flags, 0o644, dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode), "the evidence owner is not regular")
        position = 0
        while position < len(content):
            written = os.write(descriptor, content[position:])
            require(type(written) is int and written > 0,
                    "a complete candidate evidence file was truncated")
            position += written
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((after.st_dev, after.st_ino, after.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and (before.st_dev, before.st_ino)
                == (after.st_dev, after.st_ino)
                and after.st_size == len(content),
                "a durable evidence file or same inode was changed")
        return {"relative": "oracle/phase2/evidence/" + basename,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content), "device": after.st_dev,
                "inode": after.st_ino, "exclusive_creation": True,
                "file_fsync_completed": True,
                "same_inode_readback_verified": True}
    finally:
        os.close(descriptor)


def publish_actual_report(report: dict[str, Any], family: FamilySpec,
                          label: str) -> dict[str, Any]:
    failure = report.get("status") != "PASS"
    stem = "frozen-p0-candidate-v2-" + family.name + "-" + checked_label(label)
    if failure:
        stem += "-failures"
    plain = canonical(report)
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(len(archive) <= MAX_ARCHIVE_BYTES,
            "the complete P0 candidate archive exceeds its frozen bound")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0))
    directory = os.open(str(ROOT / "oracle/phase2/evidence"), flags)
    try:
        compressed = write_fresh_evidence(directory, stem + ".json.gz", archive)
        os.fsync(directory)
        receipt_document = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS", "candidate_status": report["status"],
            "candidate_family": family.name, "label": label,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "document_sha256": report["document_sha256"],
            "archive": compressed, "uncompressed_sha256":
            hashlib.sha256(plain).hexdigest(),
            "uncompressed_bytes": len(plain),
            "archive_directory_fsync_completed": True,
            "failure_preserved": failure,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False}
        receipt = write_fresh_evidence(directory,
            stem + "-publication-receipt.json", canonical(receipt_document))
        os.fsync(directory)
    finally:
        os.close(directory)
    return {"schema": SCHEMA + "-published-complete-candidate",
            "status": report["status"], "candidate_family": family.name,
            "label": label, "suite_count": len(FROZEN_SUITES),
            "case_execution_denominator": CASE_DENOMINATOR,
            "completed_candidate_suite_count": report["completed_candidate_suite_count"],
            "qualified_candidate_case_executions":
                report["qualified_candidate_case_executions"],
            "candidate_qualified": report["candidate_qualified"],
            "complete_archive": compressed,
            "complete_publication_receipt": receipt,
            "all_mismatches_crashes_and_timeouts_preserved": True,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False}


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Qualify a genuinely V2-built native engine against all frozen Python re tests")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--internal-candidate-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--candidate", choices=tuple(FAMILY_SPECS))
    parser.add_argument("--suite", choices=tuple(item.name for item in FROZEN_SUITES))
    parser.add_argument("--label")
    for option in ("source", "protocol", "document", "subinterpreter-source",
                   "subinterpreter-protocol", "subinterpreter-explanation",
                   "build-archive", "build-receipt", "activation-source",
                   "activation-protocol", "activation-report", "activation-receipt",
                   "candidate-source", "native-engine", "native-bridge"):
        parser.add_argument("--" + option + "-sha256")
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    return parser.parse_args(arguments)


def require_complete_real_options(options: argparse.Namespace,
                                  *, worker: bool) -> None:
    family_spec(options.candidate)
    checked_label(options.label)
    checked_label(options.build_label)
    for name in ("source_sha256", "protocol_sha256", "document_sha256",
                 "subinterpreter_source_sha256", "subinterpreter_protocol_sha256",
                 "subinterpreter_explanation_sha256", "build_archive_sha256",
                 "build_receipt_sha256", "activation_source_sha256",
                 "activation_protocol_sha256", "activation_report_sha256",
                 "activation_receipt_sha256", "candidate_source_sha256",
                 "native_engine_sha256", "native_bridge_sha256"):
        valid_sha256(getattr(options, name), name)
    require(type(options.activation_root) is str,
            "a genuinely published reversible canonical activation is mandatory")
    parse_source_owners(options.owned_source_sha256, family_spec(options.candidate))
    if worker:
        require(options.suite in {"public_surface_v19", "pep688_v4",
                                  "threaded_pattern_v1"},
                "an internal worker can execute only its authentic owned route")
    else:
        require(options.suite is None,
                "never omit or select a subset of the 13 frozen P0 suites")


def fail_closed_candidate_run(options: argparse.Namespace) -> dict[str, Any]:
    """Authenticate every published prerequisite before authorizing a worker.

    The corrected canonical activator and corrected real-interpreter producer
    are independently frozen chunks.  Their exact source and evidence bytes
    must be supplied by the caller; an unpublished private-root prototype can
    never qualify a candidate.
    """
    require_complete_real_options(options, worker=False)
    context = authenticate_frozen_context(options)
    approval = authenticate_canonical_activation(options, context)
    require(type(approval["activation"].get("native_owners")) is dict,
            "the promoted canonical native targets were not actually authenticated")
    suites: list[dict[str, Any]] = []
    for suite in FROZEN_SUITES:
        suites.append(observe_actual_suite(suite, options, context, approval))
    passed = [row for row in suites if row.get("status") == "PASS"]
    passed_cases = sum(row["actual_candidate_case_count"] for row in passed)
    qualified = len(passed) == len(FROZEN_SUITES) and passed_cases == CASE_DENOMINATOR
    report = {"schema": SCHEMA + "-complete-candidate-evaluation",
        "status": "PASS" if qualified else "FAIL",
        "candidate_family": approval["family"].name,
        "label": checked_label(options.label),
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "document_sha256": options.document_sha256,
        "goal_sha256": GOAL_SHA256, "phase1_inventory_sha256": P0_SHA256,
        "phase1_verification": context["phase1_verification"],
        "source_build_v2": approval["build"],
        "canonical_activation": approval["activation"],
        "complete_owned_source_sha256": approval["owners"],
        "suite_count": len(FROZEN_SUITES),
        "case_execution_denominator": CASE_DENOMINATOR,
        "completed_candidate_suite_count": len(passed),
        "qualified_candidate_case_executions": passed_cases,
        "all_required_suites_executed": len(suites) == len(FROZEN_SUITES),
        "all_required_suites_passed": qualified,
        "candidate_qualified": qualified,
        "all_suites": suites,
        "all_failure_reasons": [row["failure"] for row in suites
                                if row.get("status") != "PASS"],
        "actual_reference_workers_started": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED", "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False}
    return publish_actual_report(report, approval["family"], options.label)


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(options.candidate is None and options.suite is None
                and options.label is None and options.build_label is None
                and options.activation_root is None
                and not options.owned_source_sha256
                and all(getattr(options, item) is None for item in (
                    "source_sha256", "protocol_sha256", "document_sha256",
                    "subinterpreter_source_sha256", "subinterpreter_protocol_sha256",
                    "subinterpreter_explanation_sha256", "build_archive_sha256",
                    "build_receipt_sha256", "activation_source_sha256",
                    "activation_protocol_sha256", "activation_report_sha256",
                    "activation_receipt_sha256", "candidate_source_sha256",
                    "native_engine_sha256", "native_bridge_sha256")),
                "synthetic self-tests cannot authorize actual owners or activation")
        result = source_self_test()
    elif options.internal_candidate_worker:
        require_complete_real_options(options, worker=True)
        result = direct_worker(options)
    else:
        result = fail_closed_candidate_run(options)
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") in {"PASS", "OBSERVED"} else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CandidateGateError, OSError, ValueError, TypeError, KeyError,
            OverflowError, UnicodeError, RecursionError,
            subprocess.SubprocessError) as error:
        result = {"schema": SCHEMA + "-complete-gate-failure", "status": "FAIL",
            "error_type": type(error).__qualname__, "message": str(error),
            "traceback": traceback.format_exception(type(error), error,
                                                    error.__traceback__),
            "clock_samples": 0, "timing_trials_run": 0,
            "actual_reference_workers": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False}
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        raise SystemExit(1)
