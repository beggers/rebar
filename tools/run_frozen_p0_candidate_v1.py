#!/usr/bin/env python3
"""Fail-closed, prospectively frozen CPython 3.14.6 P0 candidate runner.

``--self-test`` is synthetic and has no external effects.  A real candidate
run is possible only after this source and both phase-two protocol documents
have been independently frozen and explicitly pinned by the caller.  A frozen
suite without a genuine guarded candidate route fails; it is never counted as
passed.
"""

from __future__ import annotations

import argparse
import ast
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
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V1.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v1.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-v1"
PROTOCOL_SCHEMA = "rebar-frozen-python-re-p0-candidate-protocol-v1"
GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
P0_DOCUMENT_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
P0_DOCUMENT_SHA256 = (
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
)
P0_EXPLANATION_RELATIVE = "oracle/phase1/P0-COMPLETENESS-V1.md"
P0_EXPLANATION_SHA256 = (
    "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798"
)
P0_VERIFIER_RELATIVE = "tools/verify_p0_completeness_v1.py"
P0_VERIFIER_SHA256 = (
    "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c"
)
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
CORE_RELATIVE = "tools/independent_public_contract_v3.py"
CORE_SHA256 = (
    "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3"
)
V19_VALIDATOR_RELATIVE = "tools/python_re_public_surface_oracle_stage27.py"
V19_VALIDATOR_SHA256 = (
    "fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b"
)
V19_VALIDATOR_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md"
)
V19_VALIDATOR_PROTOCOL_SHA256 = (
    "c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f"
)
INDEPENDENCE_AUDIT_RELATIVE = "tools/audit_candidate_independence_v1.py"
INDEPENDENCE_AUDIT_SHA256 = (
    "f18d9b99a3f11fdf20c47d6cb43cb353532c894ababbdaeb7088c14e397ae3b5"
)
INDEPENDENCE_PROTOCOL_RELATIVE = (
    "oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md"
)
INDEPENDENCE_PROTOCOL_SHA256 = (
    "a7ee45f0ea76ee7fedacc564c3122b7f37272d918ef28f1c527c9e8adf351292"
)
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
CASE_DENOMINATOR = 31_237
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_COMPRESSED_BYTES = 64 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 192 * 1024 * 1024
MAX_RECEIPT_BYTES = 8 * 1024 * 1024
MAX_LABEL_LENGTH = 80
PROCESS_TIMEOUT_SECONDS = 3_600


class CandidateGateError(Exception):
    """A frozen correctness obligation did not actually pass."""


class SourceOnlyEffect(CandidateGateError):
    """A synthetic test attempted a real-world effect."""


class CandidateProcessFailure(CandidateGateError):
    """Retain a real candidate crash, timeout, signal, or complete failure."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


@dataclass(frozen=True, slots=True)
class SuiteSpec:
    name: str
    case_count: int
    source_relative: str
    source_sha256: str
    matrix_sha256: str
    reference_sha256: str
    route: str


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
    SuiteSpec(
        "original_bounded_v5", 151, V5_RELATIVE, V5_SHA256,
        "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240",
        "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276",
        "frozen-original-v5-authenticated-candidate-worker",
    ),
    SuiteSpec(
        "public_v3", 864, "tools/rust_public_practice_benchmark_v1.py",
        "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
        "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
        "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
        "frozen-public-v3-producer-observe-case",
    ),
    SuiteSpec(
        "scanner_v3", 1_024, "tools/rust_scanner_differential_v1.py",
        "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
        "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
        "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
        "frozen-scanner-v3-producer-observe-case",
    ),
    SuiteSpec(
        "buffer_v3", 768, "tools/rust_memoryview_expand_differential_v1.py",
        "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
        "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
        "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
        "frozen-buffer-v3-producer-observe-case",
    ),
    SuiteSpec(
        "managed_v1", 1_024,
        "tools/independent_managed_buffer_lifetime_v1.py",
        "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489",
        "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976",
        "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df",
        "frozen-managed-buffer-producer-execute-case",
    ),
    SuiteSpec(
        "scanner_verbose_v1", 2_854,
        "tools/independent_scanner_verbose_comments_v1.py",
        "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d",
        "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b",
        "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012",
        "frozen-verbose-scanner-producer-execute-case",
    ),
    SuiteSpec(
        "public_types_v1", 6_912,
        "tools/independent_public_type_identity_serialization_v1.py",
        "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
        "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123",
        "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
        "frozen-public-type-producer-observe-case",
    ),
    SuiteSpec(
        "substitution_v2", 5_120,
        "tools/independent_substitution_buffer_semantics_v2.py",
        "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
        "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54",
        "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b",
        "frozen-substitution-producer-execute-case",
    ),
    SuiteSpec(
        "shape_v2", 10_240,
        "tools/independent_shape_changing_buffer_semantics_v2.py",
        "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
        "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8",
        "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c",
        "frozen-shape-producer-execute-case",
    ),
    SuiteSpec(
        "public_surface_v19", 1_376,
        "tools/python_re_public_surface_oracle_stage19.py",
        "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e",
        "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa",
        "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
        "frozen-v17-real-locale-evaluator-under-v19-normalizer",
    ),
    SuiteSpec(
        "subinterpreter_v2", 128,
        "tools/python_re_subinterpreter_oracle_v2.py",
        "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8",
        "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3",
        "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8",
        "frozen-producer-program-inside-real-a-b-a-and-fresh-candidate-interpreters",
    ),
    SuiteSpec(
        "pep688_v4", 264, "tools/python_re_buffer_exporter_oracle_v4.py",
        "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490",
        "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891",
        "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8",
        "frozen-pep688-producer-execute-case-with-real-buffer-lifetimes",
    ),
    SuiteSpec(
        "threaded_pattern_v1", 512,
        "tools/python_re_threaded_pattern_oracle_v1.py",
        "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276",
        "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b",
        "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81",
        "frozen-thread-producer-run-thread-cohort",
    ),
)

FAMILY_SPECS = {
    "rust": FamilySpec(
        "rust", "rust", "candidates.rust_candidate",
        "candidates/rust_candidate.py", "candidates._rust_bridge",
        "candidates/_rust_engine.so",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
    ),
    "c": FamilySpec(
        "c", "c_vm", "candidates.vm_candidate", "candidates/vm_candidate.py",
        "candidates._vm_native", "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    ),
    "zig": FamilySpec(
        "zig", "zig", "candidates.zig_candidate", "candidates/zig_candidate.py",
        "candidates._zig_bridge", "candidates/_zig_probe.so",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
    ),
}

SUBINTERPRETER_REFERENCE_ONLY_FIELDS = frozenset({
    "candidate_imports", "stdlib_origin_verified",
})
SUBINTERPRETER_REQUIRED_FIELDS = frozenset({
    "actual_exec", "case_id", "cohort", "locale_unchanged", "observation",
    "ordinal", "pinned_executable_verified", "seed", "status", "variant",
})
SUBINTERPRETER_OBSERVATION_FIELD_RENAMES = types.MappingProxyType({
    "actual_stdlib_reimport": "actual_engine_reimport",
    "match_is_stdlib_match": "match_is_engine_match",
    "module_identity": "engine_sysmodules_identity_verified",
    "pattern_is_stdlib_pattern": "pattern_is_engine_pattern",
    "reimported_origin_verified": "engine_reimported_origin_verified",
    "stdlib_owner": "engine_sysmodules_owner_verified",
    "stdlib_re_module": "engine_module_name_verified",
})
SUBINTERPRETER_OWNER_NEUTRAL_FIELDS = frozenset(
    SUBINTERPRETER_OBSERVATION_FIELD_RENAMES,
)
SUBINTERPRETER_PROJECTED_REFERENCE_SHA256 = (
    "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021"
)

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CandidateGateError(message)


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("ascii") + b"\n"
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise CandidateGateError("complete canonical JSON evidence is mandatory") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_sha256(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(letter in "0123456789abcdef" for letter in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def unique_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in items:
        require(type(name) is str and name not in result,
                "a duplicate or non-string evidence key was concealed")
        result[name] = value
    return result


def decode_document(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_UNCOMPRESSED_BYTES,
            "a complete bounded evidence document is mandatory: " + label)
    try:
        result = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_pairs,
            parse_constant=lambda item: (_ for _ in ()).throw(
                CandidateGateError("a non-finite evidence number was hidden: " + item),
            ),
        )
    except (ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise CandidateGateError("invalid complete JSON evidence: " + label) from error
    require(type(result) is dict,
            "a complete JSON evidence object is mandatory: " + label)
    return result


def safe_relative(relative: Any, allowed: frozenset[str]) -> tuple[str, ...]:
    require(type(relative) is str and relative in allowed,
            "read only a specifically frozen correctness source or archive")
    require(not relative.startswith("/") and "\\" not in relative
            and "\x00" not in relative,
            "a frozen correctness owner escaped the exact repository root")
    parts = tuple(relative.split("/"))
    require(parts and all(part not in ("", ".", "..") for part in parts),
            "a frozen correctness owner has a noncanonical path")
    require(not any(part in {
        "holdout", "hidden", "benchmark", "benchmarks", "performance",
    } for part in parts),
            "performance, hidden, benchmark, and holdout files are forbidden")
    return parts


@contextlib.contextmanager
def owned_descriptor(
    relative: str, allowed: frozenset[str], maximum: int,
) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_relative(relative, allowed)
    require(type(maximum) is int and 0 < maximum <= MAX_UNCOMPRESSED_BYTES,
            "an exact safe regular-file bound is mandatory")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags)
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact repository root is not an owned directory")
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a frozen correctness parent is not an owned directory")
        descriptor = os.open(parts[-1], flags, dir_fd=current)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            stat.S_ISREG(first.st_mode) and stat.S_ISREG(named.st_mode)
            and (first.st_dev, first.st_ino) == (named.st_dev, named.st_ino)
            and 0 < first.st_size <= maximum,
            "the exact no-follow, bounded correctness file was substituted",
        )
        yield descriptor, first
        final = os.fstat(descriptor)
        named_final = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            (first.st_dev, first.st_ino, first.st_size)
            == (final.st_dev, final.st_ino, final.st_size)
            == (named_final.st_dev, named_final.st_ino, named_final.st_size),
            "a frozen correctness owner changed while being observed",
        )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_owned(
    relative: str, expected: str, *, maximum: int,
    allowed: frozenset[str],
) -> bytes:
    valid_sha256(expected, relative)
    chunks: list[bytes] = []
    with owned_descriptor(relative, allowed, maximum) as (descriptor, info):
        remaining = info.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "an exact frozen correctness file was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "a frozen correctness file has an unrecorded suffix")
    result = b"".join(chunks)
    require(hashlib.sha256(result).hexdigest() == expected,
            "a frozen correctness owner changed: " + relative)
    return result


def verify_runtime(*, allow_candidate: bool = False) -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
        and bool(sys.path) and sys.path[0] == str(ROOT),
        "run only under exact isolated, no-bytecode CPython 3.14.6",
    )
    if not allow_candidate:
        require(
            not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate was imported before its frozen isolated worker",
        )


def suite_spec(value: Any) -> SuiteSpec:
    require(type(value) is str,
            "an exact independently frozen suite name is mandatory")
    matches = [suite for suite in FROZEN_SUITES if suite.name == value]
    require(len(matches) == 1,
            "the selected correctness suite is not independently frozen")
    return matches[0]


def family_spec(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILY_SPECS,
            "select one genuine independently owned native family")
    return FAMILY_SPECS[value]


def parse_owner_entries(
    entries: Sequence[str] | None, family: FamilySpec,
) -> dict[str, str]:
    require(isinstance(entries, (tuple, list)),
            "explicitly pin the exact complete independently owned source set")
    result: dict[str, str] = {}
    for entry in entries:
        require(type(entry) is str and entry.count("=") == 1,
                "each source owner requires one exact path=SHA-256 pin")
        path, actual = entry.split("=", 1)
        require(path in family.sources and path not in result,
                "an independent source owner was repeated or escaped its family")
        result[path] = valid_sha256(actual, path)
    require(set(result) == set(family.sources),
            "every selected family source owner must be explicitly pinned")
    return result


def validate_protocol_document(document: Any) -> dict[str, Any]:
    require(type(document) is dict and document.get("schema") == PROTOCOL_SCHEMA
            and document.get("version") == 1
            and document.get("phase") == "CANDIDATES"
            and document.get("status") == "SOURCE FROZEN; CANDIDATES NOT RUN"
            and document.get("goal_sha256") == GOAL_SHA256,
            "the independently frozen candidate protocol was substituted")
    phase = document.get("phase1")
    require(type(phase) is dict
            and phase.get("inventory_path") == P0_DOCUMENT_RELATIVE
            and phase.get("inventory_sha256") == P0_DOCUMENT_SHA256
            and phase.get("explanation_path") == P0_EXPLANATION_RELATIVE
            and phase.get("explanation_sha256") == P0_EXPLANATION_SHA256
            and phase.get("verifier_path") == P0_VERIFIER_RELATIVE
            and phase.get("verifier_sha256") == P0_VERIFIER_SHA256
            and phase.get("python_path") == PINNED_PYTHON
            and phase.get("python_sha256") == PINNED_PYTHON_SHA256
            and phase.get("python_version") == "3.14.6"
            and phase.get("suite_count") == len(FROZEN_SUITES)
            and phase.get("case_execution_denominator") == CASE_DENOMINATOR
            and phase.get("public_obligation_count") == 73
            and phase.get("named_private_waiver_count") == 13
            and phase.get("genuine_public_debug_skip_count") == 1,
            "the complete published CPython correctness standard changed")
    require(document.get("candidate_families") == ["rust", "c", "zig"],
            "the three actually distinct frozen engine families were changed")
    runner = document.get("runner")
    require(type(runner) is dict
            and runner.get("path") == SOURCE_RELATIVE
            and runner.get("source_sha256_mode")
            == "mandatory-exact-caller-pinned-source-bytes",
            "the exact frozen candidate runner or its source-pin policy changed")
    audit = document.get("independence_audit")
    require(type(audit) is dict
            and audit.get("source_path") == INDEPENDENCE_AUDIT_RELATIVE
            and audit.get("source_sha256") == INDEPENDENCE_AUDIT_SHA256
            and audit.get("protocol_path") == INDEPENDENCE_PROTOCOL_RELATIVE
            and audit.get("protocol_sha256") == INDEPENDENCE_PROTOCOL_SHA256
            and audit.get("runtime_no_delegation_proved_by_static_audit") is False
            and audit.get("continuous_v5_runtime_guard_required") is True,
            "the frozen independent source audit or real runtime guard changed")
    common = document.get("common_category_controller")
    require(type(common) is dict and common.get("path") == CORE_RELATIVE
            and common.get("sha256") == CORE_SHA256
            and common.get("families") == ["rust", "c", "zig"]
            and common.get("categories") == ["public", "scanner", "buffer"],
            "the exact three-family frozen public category controller changed")
    rows = document.get("suites")
    require(type(rows) is list and len(rows) == len(FROZEN_SUITES),
            "all 13 source-ordered frozen correctness suites are mandatory")
    for position, (row, expected) in enumerate(zip(rows, FROZEN_SUITES, strict=True)):
        require(type(row) is dict
                and row.get("id") == expected.name
                and row.get("case_count") == expected.case_count
                and row.get("source_path") == expected.source_relative
                and row.get("source_sha256") == expected.source_sha256
                and row.get("matrix_sha256") == expected.matrix_sha256
                and row.get("reference_records_sha256") == expected.reference_sha256
                and row.get("route") == expected.route,
                "a frozen suite, case count, route, or reference changed at "
                + str(position))
        expected_projection = (
            "original-public-methods-with-one-genuine-debug-skip"
            if expected.name == "original_bounded_v5" else
            "explicit-lossless-reference-only-owner-identity-v1"
            if expected.name == "subinterpreter_v2" else
            "exact-complete-reference-record"
        )
        require(row.get("projection") == expected_projection,
                "an independently frozen suite comparison was weakened")
        if expected.name == "subinterpreter_v2":
            require(set(row.get("projected_reference_only_top_level_fields", []))
                    == SUBINTERPRETER_REFERENCE_ONLY_FIELDS
                    and set(row.get("preserved_owner_neutral_observation_fields", []))
                    == SUBINTERPRETER_OWNER_NEUTRAL_FIELDS
                    and row.get("actual_interpreters_created") == 11
                    and row.get("actual_interpreters_destroyed") == 11
                    and row.get("actual_interpreter_exec_calls") == 394
                    and row.get("actual_repeated_fresh_interpreter_cases") == 8
                    and row.get("projected_reference_records_sha256")
                    == SUBINTERPRETER_PROJECTED_REFERENCE_SHA256
                    and row.get("lossless_observation_field_renames")
                    == dict(SUBINTERPRETER_OBSERVATION_FIELD_RENAMES),
                    "a genuine subinterpreter case, provenance, or lifecycle was omitted")
        if expected.name == "public_surface_v19":
            require(row.get("actual_real_locale_case_count") == 64
                    and row.get("actual_real_locale_transition_count") == 192,
                    "the original public real-locale cases were weakened")
        if expected.name == "threaded_pattern_v1":
            require(row.get("actual_thread_starts") == 32
                    and row.get("actual_thread_joins") == 32
                    and row.get("actual_thread_case_executions") == 1_024
                    and row.get("actual_regex_api_calls") == 2_176
                    and row.get("warning_records_sha256")
                    == "f28af6781328eacabdbe96460e8c54cba1e7802f6a052cefb4a7c59f30ce4413",
                    "a genuine shared-pattern thread or warning was omitted")
    require(sum(row["case_count"] for row in rows) == CASE_DENOMINATOR,
            "the complete frozen 31,237-case denominator was changed")
    boundaries = document.get("boundaries")
    require(type(boundaries) is dict
            and boundaries.get("archive_receipts_required") is True
            and boundaries.get("candidate_workers_isolated") is True
            and boundaries.get("continuous_original_matcher_quarantine_required") is True
            and boundaries.get("cross_candidate_delegation_allowed") is False
            and boundaries.get("external_regex_package_allowed") is False
            and boundaries.get("stdlib_candidate_delegation_allowed") is False
            and boundaries.get("hidden_case_access_allowed") is False
            and boundaries.get("timing_allowed") is False
            and boundaries.get("final_holdout_authorized") is False
            and boundaries.get("final_holdout_opened") is False
            and boundaries.get("final_winner_selected") is False
            and boundaries.get("performance") == "NOT MEASURED"
            and document.get("candidate_results") == "NOT MEASURED",
            "the unopened holdout or no-delegation correctness boundary changed")
    return document


def validate_phase1_document(document: Any) -> dict[str, Any]:
    require(type(document) is dict
            and document.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and type(document.get("goal")) is dict
            and document["goal"].get("sha256") == GOAL_SHA256,
            "the immutable complete phase-one inventory was substituted")
    phase = document.get("phase_gate")
    require(type(phase) is dict and phase.get("status") == "PASS"
            and phase.get("phase") == "CORRECTNESS ORACLE"
            and phase.get("all_obligations_mapped") is True
            and phase.get("final_holdout_authorized") is False,
            "only the actually passing, holdout-sealed phase-one oracle may be used")
    denominator = document.get("denominator")
    require(type(denominator) is dict
            and denominator.get("final_required_case_execution_denominator")
            == CASE_DENOMINATOR
            and denominator.get("available_frozen_vector_case_executions")
            == CASE_DENOMINATOR
            and denominator.get("counted_suite_ids")
            == [suite.name for suite in FROZEN_SUITES],
            "the original suite count or case denominator changed")
    rows = document.get("suites")
    require(type(rows) is list and len(rows) == len(FROZEN_SUITES),
            "each original phase-one suite must remain present")
    for row, expected in zip(rows, FROZEN_SUITES, strict=True):
        require(type(row) is dict and row.get("id") == expected.name
                and row.get("case_execution_count") == expected.case_count
                and row.get("matrix_sha256") == expected.matrix_sha256
                and row.get("baseline_records_sha256") == expected.reference_sha256
                and type(row.get("source")) is dict
                and row["source"].get("path") == expected.source_relative
                and row["source"].get("sha256") == expected.source_sha256,
                "a genuine phase-one producer or original suite was substituted")
    return document


def project_subinterpreter_reference(record: Any) -> dict[str, Any]:
    require(type(record) is dict
            and set(record) == SUBINTERPRETER_REQUIRED_FIELDS
            | SUBINTERPRETER_REFERENCE_ONLY_FIELDS
            and record.get("candidate_imports") == 0
            and record.get("stdlib_origin_verified") is True
            and record.get("actual_exec") is True
            and record.get("locale_unchanged") is True
            and record.get("pinned_executable_verified") is True
            and record.get("status") == "PASS"
            and type(record.get("observation")) is dict,
            "a genuine complete subinterpreter reference record was changed")
    result = {key: value for key, value in record.items()
              if key not in SUBINTERPRETER_REFERENCE_ONLY_FIELDS}
    observation = dict(record["observation"])
    for original, replacement in SUBINTERPRETER_OBSERVATION_FIELD_RENAMES.items():
        if original in observation:
            require(replacement not in observation,
                    "a genuine owner-neutral observation name collided")
            observation[replacement] = observation.pop(original)
    result["observation"] = observation
    require(set(result) == SUBINTERPRETER_REQUIRED_FIELDS,
            "a genuine subinterpreter semantic observation was dropped")
    return result


def validate_subinterpreter_candidate_record(
    record: Any, baseline: Mapping[str, Any],
) -> dict[str, Any]:
    required = SUBINTERPRETER_REQUIRED_FIELDS | {
        "candidate_family", "candidate_module", "candidate_source_sha256",
        "candidate_engine_sha256", "candidate_bridge_sha256",
        "candidate_origin_verified", "candidate_import_count",
        "original_matcher_calls", "external_engine_imports",
        "cross_candidate_imports", "foreign_native_loads",
    }
    require(type(record) is dict and set(record) == required,
            "a genuine in-interpreter candidate or semantic field was omitted")
    require(record.get("candidate_family") in FAMILY_SPECS,
            "an exact genuine subinterpreter candidate family is mandatory")
    selected = family_spec(record["candidate_family"])
    require(record.get("candidate_module") == selected.module
            and record.get("candidate_origin_verified") is True
            and type(record.get("candidate_import_count")) is int
            and record["candidate_import_count"] >= 1
            and all(record.get(name) == 0 for name in (
                "original_matcher_calls", "external_engine_imports",
                "cross_candidate_imports", "foreign_native_loads",
            )), "the genuine in-interpreter independent engine was not authenticated")
    for field in (
        "candidate_source_sha256", "candidate_engine_sha256",
        "candidate_bridge_sha256",
    ):
        valid_sha256(record.get(field), field)
    require((record["candidate_engine_sha256"]
             == record["candidate_bridge_sha256"])
            is (selected.name == "c"),
            "a subinterpreter candidate crossed or forged native family ownership")
    actual = {key: record[key] for key in SUBINTERPRETER_REQUIRED_FIELDS}
    require(actual == project_subinterpreter_reference(baseline),
            "a genuine candidate subinterpreter semantic observation differs")
    return actual


def validate_thread_evidence(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("actual_thread_starts") == 32
            and value.get("actual_thread_joins") == 32
            and value.get("actual_thread_case_executions") == 1_024
            and value.get("actual_regex_api_calls") == 2_176
            and value.get("metadata_case_count") == 32
            and value.get("metadata_cases_are_threaded_subset") is True
            and value.get("all_barriers_verified") is True
            and value.get("all_thread_joins_verified") is True
            and value.get("orphan_threads") == 0
            and value.get("thread_failures") == [],
            "a genuine frozen shared-pattern thread or join was omitted")
    lifecycle = value.get("thread_lifecycle")
    require(type(lifecycle) is list and len(lifecycle) == 32
            and all(type(row) is dict and row.get("started") is True
                    and row.get("joined") is True
                    and row.get("alive_after_join") is False
                    for row in lifecycle),
            "the exact 32 genuine shared-pattern thread lifecycles are required")
    events = value.get("thread_events")
    require(type(events) is list and len(events) == 1_024
            and all(type(row) is dict and row.get("status") == "PASS"
                    and row.get("start_barrier_passed") is True
                    and row.get("completion_barrier_arrived") is True
                    for row in events),
            "all 1,024 actual barrier-bound thread executions are mandatory")
    return value


def capture_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "retain the complete bounded original candidate process stream")
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "complete": True,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def restore_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"base64", "bytes", "complete", "sha256"}
            and value.get("complete") is True
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and type(value.get("base64")) is str,
            "a complete bounded worker stream is mandatory: " + label)
    valid_sha256(value.get("sha256"), label)
    try:
        raw = base64.b64decode(value["base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise CandidateGateError("an exact worker stream is not valid base64") from error
    require(len(raw) == value["bytes"]
            and hashlib.sha256(raw).hexdigest() == value["sha256"],
            "a complete genuine worker stream was truncated: " + label)
    return raw


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= MAX_LABEL_LENGTH
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(letter in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for letter in value),
            "use one short, lowercase, explicitly safe evidence label")
    return value


def authenticate_phase1() -> tuple[dict[str, Any], dict[str, Any]]:
    allowed = frozenset({
        P0_DOCUMENT_RELATIVE, P0_EXPLANATION_RELATIVE,
        P0_VERIFIER_RELATIVE, "GOAL.md",
    })
    goal = read_owned("GOAL.md", GOAL_SHA256,
                      maximum=MAX_SOURCE_BYTES, allowed=allowed)
    require(hashlib.sha256(goal).hexdigest() == GOAL_SHA256,
            "the immutable original objective changed")
    raw = read_owned(P0_DOCUMENT_RELATIVE, P0_DOCUMENT_SHA256,
                     maximum=MAX_SOURCE_BYTES, allowed=allowed)
    document = validate_phase1_document(
        decode_document(raw, P0_DOCUMENT_RELATIVE),
    )
    read_owned(P0_EXPLANATION_RELATIVE, P0_EXPLANATION_SHA256,
               maximum=MAX_SOURCE_BYTES, allowed=allowed)
    read_owned(P0_VERIFIER_RELATIVE, P0_VERIFIER_SHA256,
               maximum=MAX_SOURCE_BYTES, allowed=allowed)
    verifier = importlib.import_module("tools.verify_p0_completeness_v1")
    require(type(verifier) is types.ModuleType
            and os.path.abspath(verifier.__file__)
            == str(ROOT / P0_VERIFIER_RELATIVE),
            "the genuine frozen phase-one verifier was substituted")
    result = verifier.verify_actual(
        source_sha256=P0_VERIFIER_SHA256,
        document_sha256=P0_DOCUMENT_SHA256,
        explanation_sha256=P0_EXPLANATION_SHA256,
    )
    require(type(result) is dict and result.get("status") == "PASS"
            and result.get("suite_count") == len(FROZEN_SUITES)
            and result.get("case_execution_denominator") == CASE_DENOMINATOR
            and result.get("new_candidate_workers") == 0
            and result.get("hidden_cases_read") == 0
            and result.get("performance_files_read") == 0
            and result.get("clock_samples") == 0,
            "the complete signed original correctness oracle did not pass")
    return document, result


def authenticate_protocol(
    *, source_sha256: str, protocol_sha256: str, document_sha256: str,
) -> dict[str, Any]:
    allowed = frozenset({SOURCE_RELATIVE, PROTOCOL_RELATIVE, DOCUMENT_RELATIVE})
    read_owned(SOURCE_RELATIVE, valid_sha256(source_sha256, "candidate runner"),
               maximum=MAX_SOURCE_BYTES, allowed=allowed)
    read_owned(PROTOCOL_RELATIVE, valid_sha256(protocol_sha256, "candidate protocol"),
               maximum=MAX_SOURCE_BYTES, allowed=allowed)
    raw = read_owned(
        DOCUMENT_RELATIVE, valid_sha256(document_sha256, "candidate protocol inventory"),
        maximum=MAX_SOURCE_BYTES, allowed=allowed,
    )
    return validate_protocol_document(decode_document(raw, DOCUMENT_RELATIVE))


def validate_owners(
    family: FamilySpec, *, adapter: str, engine: str, bridge: str,
    source_entries: Sequence[str] | None,
) -> dict[str, str]:
    actual = {
        "source": valid_sha256(adapter, "selected Python adapter"),
        "native_engine": valid_sha256(engine, "selected native engine"),
        "native_bridge": valid_sha256(bridge, "selected native bridge"),
    }
    require((actual["native_engine"] == actual["native_bridge"])
            is (family.name == "c"),
            "only the actual C family's engine and bridge may be one binary")
    sources = parse_owner_entries(source_entries, family)
    require(sources.get(family.adapter) == actual["source"],
            "the selected adapter was excluded from its genuine owner closure")
    allowed = frozenset(set(family.sources) | {family.engine, family.bridge})
    for path, expected in sources.items():
        read_owned(path, expected, maximum=MAX_SOURCE_BYTES, allowed=allowed)
    read_owned(family.engine, actual["native_engine"],
               maximum=MAX_PROCESS_BYTES, allowed=allowed)
    if family.bridge != family.engine:
        read_owned(family.bridge, actual["native_bridge"],
                   maximum=MAX_PROCESS_BYTES, allowed=allowed)
    return actual


def import_suite_source(spec: SuiteSpec) -> types.ModuleType:
    allowed = frozenset({spec.source_relative})
    read_owned(spec.source_relative, spec.source_sha256,
               maximum=MAX_SOURCE_BYTES, allowed=allowed)
    module_name = spec.source_relative.removesuffix(".py").replace("/", ".")
    module = importlib.import_module(module_name)
    require(type(module) is types.ModuleType
            and os.path.abspath(module.__file__) == str(ROOT / spec.source_relative),
            "the exact independently frozen producer module was replaced")
    read_owned(spec.source_relative, spec.source_sha256,
               maximum=MAX_SOURCE_BYTES, allowed=allowed)
    return module


def producer_matrix(source: Any, spec: SuiteSpec) -> list[dict[str, Any]]:
    build = getattr(source, "build_matrix", None)
    require(callable(build),
            "the actual frozen suite has no authentic producer matrix")
    rows = build()
    require(type(rows) is list and len(rows) == spec.case_count,
            "the complete original producer case denominator changed")
    if spec.name == "public_surface_v19":
        producer = getattr(source, "v17", None)
        validate = getattr(producer, "validate_matrix", None)
        require(callable(validate),
                "the authentic frozen V17 public matrix validator is mandatory")
        observed = validate(rows, expected_sha256=spec.matrix_sha256)
    else:
        validate = getattr(source, "validate_matrix", None)
        require(callable(validate),
                "the original producer matrix validator is mandatory")
        observed = validate(rows)
    require(observed == spec.matrix_sha256,
            "the authentic original producer matrix changed")
    return rows


def case_identity(row: Mapping[str, Any]) -> str:
    for field in ("case", "case_id", "id", "test"):
        value = row.get(field)
        if type(value) is str and value:
            return value
    raise CandidateGateError("an original source-ordered case has no stable identity")


def validate_case_vector(
    records: Any, baseline: Any, spec: SuiteSpec,
    *, producer_digest: Callable[[Any], str],
) -> list[dict[str, Any]]:
    require(type(records) is list and type(baseline) is list
            and len(records) == len(baseline) == spec.case_count,
            "all original suite cases and both complete vectors are mandatory")
    require(producer_digest(baseline) == spec.reference_sha256,
            "the producer-owned archived reference digest was substituted")
    seen: set[str] = set()
    for reference, actual in zip(baseline, records, strict=True):
        require(type(reference) is dict and type(actual) is dict,
                "a complete actual suite case record was concealed")
        identity = case_identity(reference)
        require(identity not in seen and identity == case_identity(actual),
                "an actual candidate case was omitted, duplicated, or reordered")
        seen.add(identity)
    return records


def extract_role_record(document: Mapping[str, Any], role: str) -> list[dict[str, Any]]:
    for container_name in (
        "reference_workers", "reference_worker_reports", "reference_roles",
    ):
        container = document.get(container_name)
        if type(container) is dict and role in container:
            entry = container[role]
            if type(entry) is dict:
                if type(entry.get("records")) is list:
                    return entry["records"]
                report = entry.get("report")
                if type(report) is dict and type(report.get("records")) is list:
                    return report["records"]
    direct = document.get(role + "_records")
    if type(direct) is list:
        return direct
    nested = document.get(role)
    if type(nested) is dict and type(nested.get("records")) is list:
        return nested["records"]
    for container_name in ("reference_processes", "isolated_reference_process_evidence"):
        processes = document.get(container_name)
        if type(processes) is list:
            for item in processes:
                if type(item) is not dict or item.get("role") != role:
                    continue
                report = item.get("report")
                if type(report) is dict and type(report.get("records")) is list:
                    return report["records"]
    raise CandidateGateError(
        "the authenticated complete original reference vector is absent: " + role,
    )


def decode_archived_document(
    suite: Mapping[str, Any], spec: SuiteSpec,
) -> dict[str, Any]:
    baseline = suite.get("baseline")
    require(type(baseline) is dict and baseline.get("status") == "PASS",
            "an original passing independently archived baseline is mandatory")
    archive = baseline.get("compressed_report")
    require(type(archive) is dict
            and type(archive.get("path")) is str,
            "a complete frozen lossless baseline archive is mandatory")
    expected = valid_sha256(archive.get("sha256"), "frozen compressed archive")
    allowed = frozenset({archive["path"]})
    compressed = read_owned(archive["path"], expected,
                            maximum=MAX_COMPRESSED_BYTES, allowed=allowed)
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as stream:
            pieces: list[bytes] = []
            size = 0
            while True:
                block = stream.read(131_072)
                if not block:
                    break
                size += len(block)
                require(size <= MAX_UNCOMPRESSED_BYTES,
                        "a complete producer archive exceeded its frozen bound")
                pieces.append(block)
    except (OSError, EOFError, gzip.BadGzipFile) as error:
        raise CandidateGateError(
            "an authenticated producer archive is truncated or invalid",
        ) from error
    raw = b"".join(pieces)
    original = baseline.get("uncompressed_report")
    require(type(original) is dict and original.get("bytes") == size
            and original.get("sha256") == hashlib.sha256(raw).hexdigest(),
            "the exact full original archive bytes or escaped surrogates changed")
    document = decode_document(raw, spec.name + " complete archived baseline")
    require(document.get("status") == "PASS",
            "a genuine archived two-reference producer did not pass")
    return document


def archived_vectors(
    phase1: Mapping[str, Any], spec: SuiteSpec,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    matches = [row for row in phase1["suites"] if row["id"] == spec.name]
    require(len(matches) == 1,
            "exactly one original suite archive must be authenticated")
    suite = matches[0]
    if spec.name == "public_surface_v19":
        allowed = frozenset({
            V19_VALIDATOR_RELATIVE, V19_VALIDATOR_PROTOCOL_RELATIVE,
        })
        read_owned(V19_VALIDATOR_RELATIVE, V19_VALIDATOR_SHA256,
                   maximum=MAX_SOURCE_BYTES, allowed=allowed)
        read_owned(V19_VALIDATOR_PROTOCOL_RELATIVE,
                   V19_VALIDATOR_PROTOCOL_SHA256,
                   maximum=MAX_SOURCE_BYTES, allowed=allowed)
        owner = importlib.import_module(
            "tools.python_re_public_surface_oracle_stage27",
        )
        reference = owner.authenticate_reference(
            V19_VALIDATOR_SHA256, V19_VALIDATOR_PROTOCOL_SHA256,
        )
        require(type(reference) is dict
                and reference.get("actual_independent_reference_count") == 2
                and reference.get("fresh_reference_workers_started") == 0
                and reference.get("v19_reference_record_sha256")
                == spec.reference_sha256
                and reference.get("cases") == spec.case_count
                and reference.get("candidate_imports") == 0
                and reference.get("holdout_cases_read") == 0
                and reference.get("performance_fixtures_read") == 0
                and reference.get("benchmark_or_timing_executed") is False,
                "both authentic surrogate-safe public reference roles are mandatory")
        records = reference.get("baseline_records")
        require(type(records) is list and len(records) == spec.case_count
                and owner.validate_public_records(records) == spec.reference_sha256,
                "the exact source-owned V19 baseline record vector was replaced")
        return records, records, {
            "actual_independent_reference_count": 2,
            "reference_decoder": V19_VALIDATOR_RELATIVE,
            "reference_decoder_sha256": V19_VALIDATOR_SHA256,
            "reference_roles_separately_authenticated": True,
            "duplicate_reference_vectors_in_memory": False,
        }
    document = decode_archived_document(suite, spec)
    try:
        first = extract_role_record(document, "reference_a")
        second = extract_role_record(document, "reference_b")
    except CandidateGateError:
        stream = document.get("complete_baseline_process_stdout")
        require(type(stream) is dict,
                "the signed compact archive has no complete producer-owned stream")
        raw = restore_stream(stream, spec.name + " exact original producer stdout")
        decoded = decode_document(raw, spec.name + " decoded producer stdout")
        first = extract_role_record(decoded, "reference_a")
        second = extract_role_record(decoded, "reference_b")
    require(type(first) is list and type(second) is list
            and len(first) == len(second) == spec.case_count
            and first == second,
            "both complete independently produced reference vectors must agree")
    source = import_suite_source(spec)
    producer_digest = getattr(source, "digest", None)
    require(callable(producer_digest)
            and producer_digest(first) == producer_digest(second)
            == spec.reference_sha256,
            "the authentic producer-specific canonical baseline digest changed")
    return first, second, {
        "actual_independent_reference_count": 2,
        "reference_roles_separately_authenticated": True,
        "reference_records_sha256": spec.reference_sha256,
        "reference_archive_sha256": suite["baseline"]["compressed_report"]["sha256"],
    }


def source_module_for_core(spec: SuiteSpec) -> tuple[Any, Any]:
    allowed = frozenset({CORE_RELATIVE})
    read_owned(CORE_RELATIVE, CORE_SHA256,
               maximum=MAX_SOURCE_BYTES, allowed=allowed)
    core = importlib.import_module("tools.independent_public_contract_v3")
    require(type(core) is types.ModuleType
            and os.path.abspath(core.__file__) == str(ROOT / CORE_RELATIVE),
            "the frozen three-category guarded producer was substituted")
    category_name = {
        "public_v3": "public",
        "scanner_v3": "scanner",
        "buffer_v3": "buffer",
    }.get(spec.name)
    require(category_name is not None,
            "only an authentic original public category is allowed")
    category = core.category_spec(category_name)
    require(category.case_count == spec.case_count
            and category.matrix_sha256 == spec.matrix_sha256
            and category.baseline_sha256 == spec.reference_sha256
            and category.source_relative == spec.source_relative
            and category.source_sha256 == spec.source_sha256,
            "an original category source, baseline, or matrix was changed")
    return core, category


def create_frozen_record(
    spec: SuiteSpec, source: Any, case: Mapping[str, Any],
    candidate: types.ModuleType, *, core: Any = None, category: Any = None,
    support: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if spec.name in {"public_v3", "scanner_v3", "buffer_v3"}:
        require(core is not None and category is not None,
                "the authentic frozen category owner was omitted")
        result = core.observe_case(category, source, case, candidate)
    elif spec.name == "managed_v1":
        result = {
            "case": case["case"], "group": case["group"],
            "variant": case["variant"],
            "outcome": source.execute_case(case, candidate),
        }
    elif spec.name == "scanner_verbose_v1":
        result = {
            "case": case["case"], "cohort": case["cohort"],
            "expected_kind": case["expected_kind"],
            "outcome": source.execute_case(case, candidate),
        }
    elif spec.name == "public_types_v1":
        require(type(support) is dict,
                "the actual public-type support owner was not preloaded")
        result = source.observe_case(case, candidate, support)
    elif spec.name == "substitution_v2":
        result = {
            "case": case["case"], "cohort": case["cohort"],
            "api": case["api"],
            "outcome": source.execute_case(case, candidate),
        }
    elif spec.name == "shape_v2":
        result = {
            "case": case["case"], "cohort": case["cohort"],
            "api": case["api"], "outer_size": case["outer_size"],
            "nested_size": case["nested_size"],
            "outcome": source.execute_case(case, candidate),
        }
    elif spec.name == "pep688_v4":
        result = source.execute_case(case, candidate)
        source.validate_case_record(result, case)
    else:
        raise CandidateGateError(
            "no genuine producer-owned direct case route is frozen: " + spec.name,
        )
    require(type(result) is dict and case_identity(result) == case_identity(case),
            "the actual candidate did not execute the exact frozen case")
    return result


def capture_guard(
    active: Mapping[str, Any], checks: int, family: FamilySpec,
) -> dict[str, Any]:
    truth = (
        "original_matchers_blocked", "adapter_import_quarantined",
        "native_sre_blocked", "builtins_import_guarded",
        "importlib_import_guarded", "actual_object_identity_guarded",
        "warning_registry_introspection_safe",
        "warning_registry_exactly_absent", "cross_family_imports_blocked",
        "external_regex_imports_blocked",
    )
    require(type(active) is dict and all(active.get(name) is True for name in truth),
            "the genuine continuous original-matcher quarantine was disabled")
    require(active.get("public_type_names_used_for_ownership") is False
            and active.get("owned_native_ffi_allowed") is (family.name == "zig"),
            "the exact native-family FFI ownership policy was substituted")
    return {
        **{name: True for name in truth},
        "public_type_names_used_for_ownership": False,
        "owned_native_ffi_allowed": family.name == "zig",
        "actual_case_guard_checks": checks,
        "selected_candidate": family.name,
        "original_matcher_calls": 0,
        "external_engine_imports": 0,
        "cross_candidate_imports": 0,
        "foreign_native_loads": 0,
    }


def observe_threaded_suite(
    source: Any, candidate: types.ModuleType,
    matrix: list[dict[str, Any]], active: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    lifecycle: list[dict[str, Any]] = []
    warnings_seen: list[dict[str, Any]] = []
    verify = active["verify"]
    for index, cohort in enumerate(source.COHORTS):
        rows = matrix[
            index * source.CASES_PER_COHORT:
            (index + 1) * source.CASES_PER_COHORT
        ]
        require(len(rows) == source.CASES_PER_COHORT
                and all(row["cohort"] == cohort for row in rows),
                "the genuine source-ordered shared-thread cohort changed")
        verify()
        completed = source._run_thread_cohort(candidate, rows, index)
        verify()
        records.extend(completed["records"])
        events.extend(completed["thread_events"])
        lifecycle.extend(completed["thread_lifecycle"])
        warnings_seen.append(completed["warning_record"])
    require(len(records) == 512 and len(events) == 1_024
            and len(lifecycle) == 32 and len(warnings_seen) == 16,
            "a genuine shared-pattern thread case or lifecycle was omitted")
    metadata = {
        "actual_thread_starts": len(lifecycle),
        "actual_thread_joins": sum(row["joined"] is True for row in lifecycle),
        "actual_thread_case_executions": len(events),
        "actual_regex_api_calls": sum(row["actual_regex_api_calls"] for row in records),
        "metadata_case_count": sum(row["metadata_case"] is True for row in records),
        "metadata_cases_are_threaded_subset": True,
        "all_barriers_verified": True,
        "all_thread_joins_verified": all(row["joined"] is True for row in lifecycle),
        "orphan_threads": sum(row["alive_after_join"] is True for row in lifecycle),
        "thread_failures": [],
        "thread_events": events,
        "thread_lifecycle": lifecycle,
        "warning_records": warnings_seen,
        "warning_records_sha256": source.digest(warnings_seen),
    }
    validate_thread_evidence(metadata)
    require(metadata["warning_records_sha256"]
            == "f28af6781328eacabdbe96460e8c54cba1e7802f6a052cefb4a7c59f30ce4413",
            "the complete original shared-thread warning vector changed")
    return records, metadata


def observe_public_surface(
    source: Any, candidate: types.ModuleType,
    matrix: list[dict[str, Any]], active: Mapping[str, Any],
    locale_names: Mapping[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    original_locale = locale.setlocale(locale.LC_CTYPE)
    original_locpath = os.environ.get("LOCPATH")
    rows: list[dict[str, Any]] = []
    real_locale_cases = 0
    verify = active["verify"]
    preflight: dict[str, Any] | None = None
    try:
        preflight = source.v17._preflight_real_locales(locale_names)
        source._validate_locale_preflight(preflight)
        with source.cycle_safe_normalization():
            for case in matrix:
                verify()
                row = source.v17.evaluate_case(
                    candidate, case, locale_names=locale_names,
                )
                if case.get("cohort") in {
                    "real-locale-switch-on-compiled-bytes",
                    "real-locale-invalid-flags-and-cache",
                }:
                    source.v17._validate_locale_case(row)
                    real_locale_cases += 1
                verify()
                rows.append(row)
    finally:
        require(locale.setlocale(locale.LC_CTYPE) == original_locale,
                "a frozen public locale was not genuinely restored")
        require(os.environ.get("LOCPATH") == original_locpath,
                "a frozen public candidate changed the locale search path")
    require(real_locale_cases == 64,
            "all 64 genuine ISO-8859-1 and UTF-8 locale cases are mandatory")
    require(source.validate_public_records(rows)
            == source.v17.digest(rows),
            "the complete V19 producer-owned public records are invalid")
    return rows, {
        "real_locale_case_count": real_locale_cases,
        "real_locale_transition_count": real_locale_cases * 3,
        "locale_preflight": preflight,
        "process_locale_restored": True,
        "locale_search_path_restored": True,
        "used_original_v17_evaluator": True,
        "used_original_v19_cycle_safe_normalizer": True,
        "used_blocked_historical_candidate_cli": False,
    }


def unavailable_subinterpreter_evidence(
    spec: SuiteSpec, family: FamilySpec,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-unavailable-genuine-suite-route",
        "status": "FAIL",
        "suite": spec.name,
        "candidate_family": family.name,
        "case_denominator": spec.case_count,
        "actual_candidate_case_count": 0,
        "matrix_sha256": spec.matrix_sha256,
        "reference_records_sha256": spec.reference_sha256,
        "reason": (
            "NOT IMPLEMENTED: the frozen Python-reference interpreter program "
            "asserts zero candidate imports and the genuine stdlib source. "
            "A separate, source-pinned candidate-owner program must actually "
            "load the owned native extension in all 11 real subinterpreters, "
            "execute all 394 real A/B/A and cleanup operations, and apply only "
            "the prospectively frozen two-field identity projection. A main-"
            "interpreter replay, reference-worker execution, imported stdlib "
            "regex, unsupported native extension, or fabricated matching "
            "record is not a candidate pass."
        ),
        "candidate_qualified": False,
        "actual_interpreters_created": 0,
        "actual_interpreters_destroyed": 0,
        "actual_interpreter_exec_calls": 0,
        "candidate_imports_falsely_labeled_zero": False,
        "stdlib_origin_falsely_labeled_candidate": False,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
    }


def run_direct_candidate_worker(
    spec: SuiteSpec, family: FamilySpec, pins: Mapping[str, str],
    *, locale_names: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    verify_runtime()
    require(spec.name not in {"original_bounded_v5", "subinterpreter_v2"},
            "this direct worker has no authentic original or interpreter route")
    source = import_suite_source(spec)
    core = category = None
    support: dict[str, Any] | None = None
    if spec.name in {"public_v3", "scanner_v3", "buffer_v3"}:
        core, category = source_module_for_core(spec)
        _, _, original, matrix, _, _ = core.load_prerequisites(category)
        require(original is source,
                "the frozen category owner differs from its actual producer")
    else:
        matrix = producer_matrix(source, spec)
        if spec.name == "public_types_v1":
            support = source.preload_support_modules()
            source.verify_support_modules(support)
    allowed = frozenset({V5_RELATIVE})
    read_owned(V5_RELATIVE, V5_SHA256,
               maximum=MAX_SOURCE_BYTES, allowed=allowed)
    v5 = importlib.import_module("tools.independent_original_cpython_suite_v5")
    require(type(v5) is types.ModuleType
            and os.path.abspath(v5.__file__) == str(ROOT / V5_RELATIVE),
            "the independently frozen identity-based native guard changed")
    warning, original_guard, _, _ = v5.load_frozen_oracles()
    original_re = sys.modules.get("re")
    require(type(original_re) is types.ModuleType
            and original_re.__name__ == "re",
            "preload the genuine original matcher before native quarantine")
    native_spec = v5.family_spec(family.name)
    require(native_spec.adapter_module == family.module
            and native_spec.adapter_relative == family.adapter
            and native_spec.bridge_module == family.bridge_module
            and native_spec.engine_relative == family.engine
            and native_spec.bridge_relative == family.bridge,
            "the selected independent V5 family was substituted")
    approved = v5.validate_pins(dict(pins), native_spec)
    rows: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {}
    checks = 0
    active_case: str | None = None
    try:
        with warning.installed_warning_safe_guard(original_guard):
            with v5.chosen_original_guard(
                original_re, approved, native_spec, original_guard, warning,
            ) as active:
                candidate = active.get("candidate")
                require(type(candidate) is types.ModuleType
                        and candidate.__name__ == family.module
                        and sys.modules.get(family.module) is candidate,
                        "the authenticated exact native candidate was not executed")
                if spec.name == "threaded_pattern_v1":
                    rows, metadata = observe_threaded_suite(
                        source, candidate, matrix, active,
                    )
                    checks = 2 * len(source.COHORTS)
                elif spec.name == "public_surface_v19":
                    require(type(locale_names) is dict,
                            "two real differently encoded public locales are mandatory")
                    rows, metadata = observe_public_surface(
                        source, candidate, matrix, active, locale_names,
                    )
                    checks = 2 * len(rows)
                else:
                    for case in matrix:
                        active_case = case_identity(case)
                        active["verify"]()
                        checks += 1
                        result = create_frozen_record(
                            spec, source, case, candidate,
                            core=core, category=category, support=support,
                        )
                        active["verify"]()
                        checks += 1
                        rows.append(result)
                        active_case = None
                guard_evidence = capture_guard(active, checks, family)
                native_provenance = active.get("native_provenance")
                require(type(native_provenance) is dict,
                        "complete actual authenticated native ownership is mandatory")
                active["verify"]()
    except BaseException as error:
        failure = {
            "schema": SCHEMA + "-complete-isolated-suite-failure",
            "status": "FAIL", "suite": spec.name,
            "candidate_family": family.name,
            "active_case": active_case,
            "completed_candidate_cases": len(rows),
            "completed_candidate_records": rows,
            "error_type": type(error).__qualname__,
            "message": str(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__,
            ),
            "actual_candidate_workers": 1,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "performance": "NOT MEASURED",
        }
        details = getattr(error, "details", None)
        if type(details) is dict:
            failure["complete_producer_failure_details"] = details
        raise CandidateProcessFailure(
            "a genuine frozen candidate suite failed: " + spec.name,
            failure,
        ) from error
    producer_digest = getattr(source, "digest", None)
    require(callable(producer_digest),
            "the authentic suite-specific canonical digest is mandatory")
    require(type(rows) is list and len(rows) == spec.case_count,
            "every actual frozen candidate case is mandatory")
    return {
        "schema": SCHEMA + "-actual-isolated-candidate-suite",
        "status": "OBSERVED",
        "suite": spec.name,
        "candidate_family": family.name,
        "candidate_pid": os.getpid(),
        "matrix_sha256": spec.matrix_sha256,
        "case_denominator": spec.case_count,
        "actual_candidate_cases": len(rows),
        "candidate_records": rows,
        "candidate_records_sha256": producer_digest(rows),
        "reference_records_sha256": spec.reference_sha256,
        "native_provenance": native_provenance,
        "matcher_guard": guard_evidence,
        "resource_evidence": metadata,
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    counts = {
        "file_reads": 0, "file_writes": 0, "candidate_imports": 0,
        "reference_workers": 0, "candidate_workers": 0,
        "thread_starts": 0, "interpreter_creations": 0,
        "gc_collections": 0, "clock_samples": 0,
        "hidden_cases_read": 0, "performance_files_read": 0,
        "blocked_reads": 0, "blocked_writes": 0,
        "blocked_imports": 0, "blocked_processes": 0,
        "blocked_threads": 0, "blocked_clocks": 0,
        "blocked_gc_collections": 0,
    }
    installed: list[tuple[Any, str, Any]] = []

    def deny(field: str, message: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            counts[field] += 1
            raise SourceOnlyEffect(message)

        return blocked

    def install(owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (Path, "open"),
            (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, deny("blocked_reads", "source-only file read"))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"),
            (os, "rename"), (os, "replace"), (os, "mkdir"),
            (os, "rmdir"), (os, "fsync"), (Path, "write_bytes"),
            (Path, "write_text"), (Path, "mkdir"), (Path, "unlink"),
        ):
            install(owner, name, deny("blocked_writes", "source-only file write"))
        install(importlib, "import_module",
                deny("blocked_imports", "source-only dynamic candidate import"))
        install(subprocess, "Popen",
                deny("blocked_processes", "source-only reference or candidate process"))
        install(subprocess, "run",
                deny("blocked_processes", "source-only reference or candidate process"))
        install(threading.Thread, "start",
                deny("blocked_threads", "source-only actual thread"))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "thread_time",
        ):
            install(time, name,
                    deny("blocked_clocks", "source-only timing or wall clock"))
        install(gc, "collect",
                deny("blocked_gc_collections", "source-only actual collection"))
        yield counts
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_protocol() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for suite in FROZEN_SUITES:
        record: dict[str, Any] = {
            "id": suite.name,
            "case_count": suite.case_count,
            "source_path": suite.source_relative,
            "source_sha256": suite.source_sha256,
            "matrix_sha256": suite.matrix_sha256,
            "reference_records_sha256": suite.reference_sha256,
            "route": suite.route,
            "projection": (
                "original-public-methods-with-one-genuine-debug-skip"
                if suite.name == "original_bounded_v5" else
                "explicit-lossless-reference-only-owner-identity-v1"
                if suite.name == "subinterpreter_v2" else
                "exact-complete-reference-record"
            ),
        }
        if suite.name == "public_surface_v19":
            record.update(actual_real_locale_case_count=64,
                          actual_real_locale_transition_count=192)
        elif suite.name == "subinterpreter_v2":
            record.update(
                projected_reference_only_top_level_fields=sorted(
                    SUBINTERPRETER_REFERENCE_ONLY_FIELDS,
                ),
                preserved_owner_neutral_observation_fields=sorted(
                    SUBINTERPRETER_OWNER_NEUTRAL_FIELDS,
                ),
                actual_interpreters_created=11,
                actual_interpreters_destroyed=11,
                actual_interpreter_exec_calls=394,
                actual_repeated_fresh_interpreter_cases=8,
                projected_reference_records_sha256=(
                    SUBINTERPRETER_PROJECTED_REFERENCE_SHA256
                ),
                lossless_observation_field_renames=dict(
                    SUBINTERPRETER_OBSERVATION_FIELD_RENAMES,
                ),
            )
        elif suite.name == "threaded_pattern_v1":
            record.update(
                actual_thread_starts=32, actual_thread_joins=32,
                actual_thread_case_executions=1_024,
                actual_regex_api_calls=2_176,
                warning_records_sha256=(
                    "f28af6781328eacabdbe96460e8c54cba1e7802f6a052cefb4a7c59f30ce4413"
                ),
            )
        rows.append(record)
    return {
        "schema": PROTOCOL_SCHEMA,
        "version": 1,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; CANDIDATES NOT RUN",
        "goal_sha256": GOAL_SHA256,
        "phase1": {
            "inventory_path": P0_DOCUMENT_RELATIVE,
            "inventory_sha256": P0_DOCUMENT_SHA256,
            "explanation_path": P0_EXPLANATION_RELATIVE,
            "explanation_sha256": P0_EXPLANATION_SHA256,
            "verifier_path": P0_VERIFIER_RELATIVE,
            "verifier_sha256": P0_VERIFIER_SHA256,
            "python_path": PINNED_PYTHON,
            "python_sha256": PINNED_PYTHON_SHA256,
            "python_version": "3.14.6",
            "suite_count": len(FROZEN_SUITES),
            "case_execution_denominator": CASE_DENOMINATOR,
            "public_obligation_count": 73,
            "named_private_waiver_count": 13,
            "genuine_public_debug_skip_count": 1,
        },
        "candidate_families": ["rust", "c", "zig"],
        "runner": {
            "path": SOURCE_RELATIVE,
            "source_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
        },
        "independence_audit": {
            "source_path": INDEPENDENCE_AUDIT_RELATIVE,
            "source_sha256": INDEPENDENCE_AUDIT_SHA256,
            "protocol_path": INDEPENDENCE_PROTOCOL_RELATIVE,
            "protocol_sha256": INDEPENDENCE_PROTOCOL_SHA256,
            "runtime_no_delegation_proved_by_static_audit": False,
            "continuous_v5_runtime_guard_required": True,
        },
        "common_category_controller": {
            "path": CORE_RELATIVE,
            "sha256": CORE_SHA256,
            "families": ["rust", "c", "zig"],
            "categories": ["public", "scanner", "buffer"],
        },
        "suites": rows,
        "boundaries": {
            "archive_receipts_required": True,
            "candidate_workers_isolated": True,
            "continuous_original_matcher_quarantine_required": True,
            "cross_candidate_delegation_allowed": False,
            "external_regex_package_allowed": False,
            "final_holdout_authorized": False,
            "final_holdout_opened": False,
            "final_winner_selected": False,
            "hidden_case_access_allowed": False,
            "performance": "NOT MEASURED",
            "stdlib_candidate_delegation_allowed": False,
            "timing_allowed": False,
        },
        "candidate_results": "NOT MEASURED",
    }


def synthetic_subinterpreter_reference() -> dict[str, Any]:
    return {
        "actual_exec": True,
        "candidate_imports": 0,
        "case_id": "frozen-subinterpreter:00",
        "cohort": "fresh-interpreter-creation-and-stdlib-import",
        "locale_unchanged": True,
        "observation": {
            "owner_state_intact": True,
            "actual_stdlib_reimport": True,
            "match_is_stdlib_match": True,
            "stdlib_re_module": True,
            "module_identity": True,
            "pattern_is_stdlib_pattern": True,
            "reimported_origin_verified": True,
            "stdlib_owner": True,
            "actual_interpreter_exec": True,
        },
        "ordinal": 0,
        "pinned_executable_verified": True,
        "seed": 13_339_223_064_461_967_305,
        "status": "PASS",
        "stdlib_origin_verified": True,
        "variant": 0,
    }


def synthetic_subinterpreter_candidate() -> dict[str, Any]:
    baseline = synthetic_subinterpreter_reference()
    return {
        **project_subinterpreter_reference(baseline),
        "candidate_family": "rust",
        "candidate_module": "candidates.rust_candidate",
        "candidate_source_sha256": "1" * 64,
        "candidate_engine_sha256": "2" * 64,
        "candidate_bridge_sha256": "3" * 64,
        "candidate_origin_verified": True,
        "candidate_import_count": 1,
        "original_matcher_calls": 0,
        "external_engine_imports": 0,
        "cross_candidate_imports": 0,
        "foreign_native_loads": 0,
    }


def synthetic_thread_evidence() -> dict[str, Any]:
    return {
        "actual_thread_starts": 32,
        "actual_thread_joins": 32,
        "actual_thread_case_executions": 1_024,
        "actual_regex_api_calls": 2_176,
        "metadata_case_count": 32,
        "metadata_cases_are_threaded_subset": True,
        "all_barriers_verified": True,
        "all_thread_joins_verified": True,
        "orphan_threads": 0,
        "thread_failures": [],
        "thread_lifecycle": [
            {"started": True, "joined": True, "alive_after_join": False}
            for _ in range(32)
        ],
        "thread_events": [
            {"status": "PASS", "start_barrier_passed": True,
             "completion_barrier_arrived": True}
            for _ in range(1_024)
        ],
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a source-only correctness test imported a real candidate")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(label: str, operation: Callable[[], Any]) -> Any:
        try:
            result = operation()
        except Exception as error:
            raise CandidateGateError(
                "a mandatory positive source-only control failed: " + label,
            ) from error
        accepted.append(label)
        return result

    def reject(label: str, operation: Callable[[], Any]) -> None:
        try:
            operation()
        except (CandidateGateError, SourceOnlyEffect, ValueError, TypeError,
                KeyError, OverflowError, json.JSONDecodeError):
            rejected.append(label)
            return
        raise CandidateGateError(
            "a mandatory hostile source-only control escaped: " + label,
        )

    with source_only_boundary() as effects:
        protocol = accept("accept-all-13-frozen-suite-routes",
                          lambda: validate_protocol_document(synthetic_protocol()))
        accept("retain-exact-31,237-case-denominator",
               lambda: require(sum(item.case_count for item in FROZEN_SUITES)
                               == CASE_DENOMINATOR, "the case denominator changed"))
        accept("retain-three-materially-independent-native-families",
               lambda: require(tuple(FAMILY_SPECS) == ("rust", "c", "zig"),
                               "the candidate family set changed"))
        for suite in FROZEN_SUITES:
            accept("resolve-frozen-suite-" + suite.name,
                   lambda suite=suite: suite_spec(suite.name))
            for field in ("id", "case_count", "source_path", "source_sha256", "matrix_sha256",
                          "reference_records_sha256", "route", "projection"):
                def altered_suite(suite: SuiteSpec = suite,
                                  field: str = field) -> dict[str, Any]:
                    altered = synthetic_protocol()
                    row = next(item for item in altered["suites"]
                               if item["id"] == suite.name)
                    value = row[field]
                    row[field] = (
                        value + 1 if type(value) is int else
                        "0" * 64 if field.endswith("sha256") else
                        str(value) + "-substituted"
                    )
                    return validate_protocol_document(altered)

                reject("reject-" + suite.name + "-" + field, altered_suite)
        for family in FAMILY_SPECS.values():
            accept("resolve-owned-family-" + family.name,
                   lambda family=family: family_spec(family.name))
            synthetic_entries = [
                path + "=" + hashlib.sha256(path.encode("ascii")).hexdigest()
                for path in family.sources
            ]
            accept("pin-complete-source-closure-" + family.name,
                   lambda family=family, values=synthetic_entries:
                   parse_owner_entries(values, family))
            reject("reject-missing-source-owner-" + family.name,
                   lambda family=family, values=synthetic_entries:
                   parse_owner_entries(values[:-1], family))
            reject("reject-duplicate-source-owner-" + family.name,
                   lambda family=family, values=synthetic_entries:
                   parse_owner_entries([*values, values[0]], family))
            reject("reject-cross-family-source-owner-" + family.name,
                   lambda family=family, values=synthetic_entries:
                   parse_owner_entries([
                       *values[:-1],
                       "candidates/external-regex.py=" + "a" * 64,
                   ], family))
        for forged in (None, "", "python", "stdlib", "_sre", "regex",
                       "rust_candidate", "candidates.rust_candidate",
                       "rust/../zig", "all", 0, [], {}):
            reject("reject-foreign-family-" + repr(forged),
                   lambda forged=forged: family_spec(forged))
        for forged in (None, "", "public", "all", "hidden", "holdout",
                       "performance", 0, [], {}, "scanner_v3/../buffer_v3"):
            reject("reject-unfrozen-suite-" + repr(forged),
                   lambda forged=forged: suite_spec(forged))
        for index in range(len(FROZEN_SUITES)):
            def omit_suite(index: int = index) -> dict[str, Any]:
                altered = synthetic_protocol()
                del altered["suites"][index]
                return validate_protocol_document(altered)

            reject("reject-omitted-suite-" + FROZEN_SUITES[index].name,
                   omit_suite)
        for index in range(len(FROZEN_SUITES) - 1):
            def reorder(index: int = index) -> dict[str, Any]:
                altered = synthetic_protocol()
                altered["suites"][index], altered["suites"][index + 1] = (
                    altered["suites"][index + 1], altered["suites"][index],
                )
                return validate_protocol_document(altered)

            reject("reject-reordered-suite-" + str(index), reorder)
        for field in (
            "suite_count", "case_execution_denominator", "public_obligation_count",
            "named_private_waiver_count", "genuine_public_debug_skip_count",
            "inventory_sha256", "explanation_sha256", "verifier_sha256",
            "python_sha256", "python_version",
        ):
            def mutate_phase(field: str = field) -> dict[str, Any]:
                altered = synthetic_protocol()
                actual = altered["phase1"][field]
                altered["phase1"][field] = (
                    actual + 1 if type(actual) is int else str(actual) + "x"
                )
                return validate_protocol_document(altered)

            reject("reject-phase-one-" + field, mutate_phase)
        for field in protocol["boundaries"]:
            def alter_boundary(field: str = field) -> dict[str, Any]:
                altered = synthetic_protocol()
                actual = altered["boundaries"][field]
                altered["boundaries"][field] = (
                    not actual if type(actual) is bool else "MEASURED"
                )
                return validate_protocol_document(altered)

            reject("reject-unsafe-boundary-" + field, alter_boundary)

        original = synthetic_subinterpreter_reference()
        candidate = synthetic_subinterpreter_candidate()
        accept("retain-every-subinterpreter-semantic-field",
               lambda: project_subinterpreter_reference(original))
        accept("verify-actual-candidate-specific-interpreter-ownership",
               lambda: validate_subinterpreter_candidate_record(candidate, original))
        for field in sorted(SUBINTERPRETER_REQUIRED_FIELDS):
            def drop_reference(field: str = field) -> dict[str, Any]:
                changed = dict(synthetic_subinterpreter_reference())
                changed.pop(field)
                return project_subinterpreter_reference(changed)

            reject("reject-dropped-reference-semantic-" + field, drop_reference)

            def drop_candidate(field: str = field) -> dict[str, Any]:
                changed = dict(synthetic_subinterpreter_candidate())
                changed.pop(field)
                return validate_subinterpreter_candidate_record(
                    changed, synthetic_subinterpreter_reference(),
                )

            reject("reject-dropped-candidate-semantic-" + field, drop_candidate)
        for field in (
            "candidate_family", "candidate_module", "candidate_source_sha256",
            "candidate_engine_sha256", "candidate_bridge_sha256",
            "candidate_origin_verified", "candidate_import_count",
            "original_matcher_calls", "external_engine_imports",
            "cross_candidate_imports", "foreign_native_loads",
        ):
            def forge_owner(field: str = field) -> dict[str, Any]:
                changed = dict(synthetic_subinterpreter_candidate())
                value = changed[field]
                changed[field] = (
                    False if value is True else
                    0 if field == "candidate_import_count" else
                    1 if type(value) is int else
                    "external-regex"
                )
                return validate_subinterpreter_candidate_record(
                    changed, synthetic_subinterpreter_reference(),
                )

            reject("reject-forged-interpreter-owner-" + field, forge_owner)
        for field in sorted(SUBINTERPRETER_REFERENCE_ONLY_FIELDS):
            def retain_forged_reference_field(field: str = field) -> dict[str, Any]:
                changed = dict(synthetic_subinterpreter_candidate())
                changed[field] = original[field]
                return validate_subinterpreter_candidate_record(changed, original)

            reject("reject-reference-identity-laundering-" + field,
                   retain_forged_reference_field)
        for field in sorted(SUBINTERPRETER_OWNER_NEUTRAL_FIELDS):
            def weaken_observation(field: str = field) -> dict[str, Any]:
                reference = synthetic_subinterpreter_reference()
                changed = synthetic_subinterpreter_candidate()
                changed["observation"] = dict(changed["observation"])
                changed["observation"][
                    SUBINTERPRETER_OBSERVATION_FIELD_RENAMES[field]
                ] = False
                return validate_subinterpreter_candidate_record(changed, reference)

            require(field in original["observation"],
                    "every one of seven lossless observation controls is mandatory")
            reject("reject-weakened-owner-neutral-observation-" + field,
                   weaken_observation)

            def collide_observation(field: str = field) -> dict[str, Any]:
                changed = synthetic_subinterpreter_reference()
                changed["observation"] = dict(changed["observation"])
                changed["observation"][
                    SUBINTERPRETER_OBSERVATION_FIELD_RENAMES[field]
                ] = True
                return project_subinterpreter_reference(changed)

            reject("reject-colliding-owner-neutral-observation-" + field,
                   collide_observation)

            def change_observation_mapping(field: str = field) -> dict[str, Any]:
                changed = synthetic_protocol()
                row = next(item for item in changed["suites"]
                           if item["id"] == "subinterpreter_v2")
                row["lossless_observation_field_renames"][field] = (
                    "concealed_or_foreign_engine_observation"
                )
                return validate_protocol_document(changed)

            reject("reject-substituted-owner-neutral-mapping-" + field,
                   change_observation_mapping)

        def change_projected_reference_digest() -> dict[str, Any]:
            changed = synthetic_protocol()
            row = next(item for item in changed["suites"]
                       if item["id"] == "subinterpreter_v2")
            row["projected_reference_records_sha256"] = "0" * 64
            return validate_protocol_document(changed)

        reject("reject-substituted-lossless-projected-reference-digest",
               change_projected_reference_digest)

        accept("retain-32-real-thread-starts-and-joins",
               lambda: validate_thread_evidence(synthetic_thread_evidence()))
        for field in (
            "actual_thread_starts", "actual_thread_joins",
            "actual_thread_case_executions", "actual_regex_api_calls",
            "metadata_case_count", "metadata_cases_are_threaded_subset",
            "all_barriers_verified", "all_thread_joins_verified",
            "orphan_threads", "thread_failures",
        ):
            def change_threads(field: str = field) -> dict[str, Any]:
                changed = synthetic_thread_evidence()
                value = changed[field]
                changed[field] = (
                    not value if type(value) is bool else
                    value + 1 if type(value) is int else
                    [{"type": "hidden-real-thread-failure"}]
                )
                return validate_thread_evidence(changed)

            reject("reject-missing-real-thread-" + field, change_threads)
        for field in ("started", "joined", "alive_after_join"):
            def mutate_lifecycle(field: str = field) -> dict[str, Any]:
                changed = synthetic_thread_evidence()
                changed["thread_lifecycle"][0][field] = (
                    not changed["thread_lifecycle"][0][field]
                )
                return validate_thread_evidence(changed)

            reject("reject-forged-thread-lifecycle-" + field, mutate_lifecycle)
        for field in ("status", "start_barrier_passed",
                      "completion_barrier_arrived"):
            def mutate_barrier(field: str = field) -> dict[str, Any]:
                changed = synthetic_thread_evidence()
                changed["thread_events"][0][field] = (
                    "FAIL" if field == "status" else False
                )
                return validate_thread_evidence(changed)

            reject("reject-forged-thread-barrier-" + field, mutate_barrier)

        for raw in (
            b'{"duplicate":1,"duplicate":2}',
            b'{"hidden":NaN}', b'{"hidden":Infinity}',
            b'{"hidden":-Infinity}', b"[]", b"null", b"",
            b'{"truncated":', b"\xff",
        ):
            reject("reject-invalid-or-duplicate-json-" + repr(raw),
                   lambda raw=raw: decode_document(raw, "synthetic"))
        accept("preserve-genuine-escaped-lone-surrogates",
               lambda: require(
                   decode_document(b'{"value":"\\ud800"}', "synthetic")["value"]
                   == "\ud800", "a genuine escaped lone surrogate was changed",
               ))
        stream = accept("capture-a-complete-synthetic-worker-stream",
                        lambda: capture_stream(b"complete synthetic worker\n"))
        accept("restore-a-complete-synthetic-worker-stream",
               lambda: require(
                   restore_stream(stream, "synthetic")
                   == b"complete synthetic worker\n",
                   "a complete synthetic worker stream changed",
               ))
        for field in ("base64", "bytes", "complete", "sha256"):
            def forge_stream(field: str = field) -> bytes:
                changed = dict(stream)
                actual = changed[field]
                changed[field] = (
                    not actual if type(actual) is bool else
                    actual + 1 if type(actual) is int else
                    "invalid-base64!" if field == "base64" else "0" * 64
                )
                return restore_stream(changed, "synthetic forged stream")

            reject("reject-forged-complete-stream-" + field, forge_stream)

        allowed = frozenset({"oracle/phase1/p0-completeness-v1.json"})
        accept("accept-exact-safelisted-frozen-path",
               lambda: safe_relative(
                   "oracle/phase1/p0-completeness-v1.json", allowed,
               ))
        for unsafe in (
            "/etc/passwd", "../GOAL.md", "oracle/../GOAL.md",
            "candidates/rust_candidate.py", "holdout/cases.json",
            "performance/results.json", "hidden/cases.json",
            "benchmarks/final.json", "oracle\\phase1\\manifest.json",
            "oracle/phase1/\x00.json", "", None, 1,
        ):
            reject("reject-unsafe-correctness-path-" + repr(unsafe),
                   lambda unsafe=unsafe: safe_relative(unsafe, allowed))
        for name in ("phase-two-source", "rust-v1", "c-v1", "zig-v1", "1"):
            accept("accept-safe-evidence-label-" + name,
                   lambda name=name: validate_label(name))
        for name in (None, "", "../outside", "/tmp/outside", "RUST",
                     "has spaces", "a/b", ".hidden", "a" * 81, 1, []):
            reject("reject-unsafe-evidence-label-" + repr(name),
                   lambda name=name: validate_label(name))

        unavailable = unavailable_subinterpreter_evidence(
            suite_spec("subinterpreter_v2"), family_spec("rust"),
        )
        accept("fail-closed-until-actual-subinterpreter-route-exists",
               lambda: require(
                   unavailable["status"] == "FAIL"
                   and unavailable["actual_candidate_case_count"] == 0
                   and unavailable["candidate_qualified"] is False
                   and unavailable["actual_interpreters_created"] == 0
                   and unavailable["actual_interpreter_exec_calls"] == 0
                   and "NOT IMPLEMENTED" in unavailable["reason"],
                   "an unimplemented interpreter route cannot count as a pass",
               ))

        reject("block-an-actual-source-only-file-read",
               lambda: builtins.open(str(ROOT / "GOAL.md"), "rb"))
        reject("block-an-actual-source-only-directory-open",
               lambda: os.open(str(ROOT), os.O_RDONLY))
        reject("block-an-actual-source-only-file-write",
               lambda: Path("synthetic").write_text("forbidden"))
        reject("block-an-actual-source-only-candidate-import",
               lambda: importlib.import_module("candidates.rust_candidate"))
        reject("block-an-actual-source-only-reference-process",
               lambda: subprocess.Popen([PINNED_PYTHON, "-I", "-B"]))
        reject("block-an-actual-source-only-candidate-process",
               lambda: subprocess.run([PINNED_PYTHON, "-I", "-B"]))
        reject("block-an-actual-source-only-thread",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-an-actual-source-only-performance-clock",
               lambda: time.perf_counter())
        reject("block-an-actual-source-only-wall-clock",
               lambda: time.time())
        reject("block-an-actual-source-only-garbage-collection",
               lambda: gc.collect())

        require(len(accepted) >= 25 and len(rejected) >= 180,
                "the independent source-only hostile controls are incomplete")
        require(effects["blocked_reads"] >= 2
                and effects["blocked_writes"] >= 1
                and effects["blocked_imports"] >= 1
                and effects["blocked_processes"] >= 2
                and effects["blocked_threads"] >= 1
                and effects["blocked_clocks"] >= 2
                and effects["blocked_gc_collections"] >= 1,
                "every actual source-only external-effect boundary must be exercised")
        snapshot = dict(effects)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a real candidate escaped the synthetic correctness self-test")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "source_only": True,
        "phase1_inventory_sha256": P0_DOCUMENT_SHA256,
        "phase1_verifier_sha256": P0_VERIFIER_SHA256,
        "goal_sha256": GOAL_SHA256,
        "suite_count": len(FROZEN_SUITES),
        "case_execution_denominator": CASE_DENOMINATOR,
        "candidate_families": list(FAMILY_SPECS),
        "synthetic_positive_control_count": len(accepted),
        "synthetic_rejection_control_count": len(rejected),
        "positive_controls": accepted,
        "rejection_controls": rejected,
        "source_only_effects": snapshot,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_thread_starts": 0,
        "actual_interpreter_creations": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify one independent native engine against frozen Python re",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--internal-candidate-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--candidate", choices=tuple(FAMILY_SPECS))
    parser.add_argument("--suite", choices=tuple(item.name for item in FROZEN_SUITES))
    parser.add_argument("--label")
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--document-sha256")
    parser.add_argument("--independence-audit-source-sha256")
    parser.add_argument("--independence-audit-protocol-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    parser.add_argument("--iso8859-1-locale", dest="iso8859_1_locale")
    parser.add_argument("--utf8-locale")
    return parser.parse_args(arguments)


def fail_closed_run(options: argparse.Namespace) -> dict[str, Any]:
    """Validate the freeze, then refuse to misclassify the missing real route.

    The genuinely transformed per-interpreter native worker has not yet been
    published.  Therefore *no* 31,237-case candidate can be qualified by this
    version.  A later separately frozen chunk must add the actual A/B/A native
    interpreter execution before candidate observations can start.
    """
    verify_runtime()
    require(options.suite is None,
            "a complete correctness run cannot select or omit a suite")
    family = family_spec(options.candidate)
    label = validate_label(options.label)
    protocol = authenticate_protocol(
        source_sha256=options.source_sha256,
        protocol_sha256=options.protocol_sha256,
        document_sha256=options.document_sha256,
    )
    phase1, verified = authenticate_phase1()
    require(len(phase1["suites"]) == len(protocol["suites"])
            == len(FROZEN_SUITES),
            "all 13 independently verified original suites are mandatory")
    valid_sha256(options.independence_audit_source_sha256,
                 "independent from-scratch audit")
    valid_sha256(options.independence_audit_protocol_sha256,
                 "independent from-scratch audit protocol")
    sources = parse_owner_entries(options.owned_source_sha256, family)
    valid_sha256(options.candidate_source_sha256, "actual candidate adapter")
    valid_sha256(options.native_engine_sha256, "actual owned native engine")
    valid_sha256(options.native_bridge_sha256, "actual owned native bridge")
    require(sources[family.adapter] == options.candidate_source_sha256,
            "the authenticated candidate adapter is absent from its source closure")
    unavailable = unavailable_subinterpreter_evidence(
        suite_spec("subinterpreter_v2"), family,
    )
    return {
        "schema": SCHEMA + "-complete-candidate-gate",
        "status": "FAIL",
        "label": label,
        "candidate_family": family.name,
        "phase1_verification": verified,
        "phase1_inventory_sha256": P0_DOCUMENT_SHA256,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "document_sha256": options.document_sha256,
        "suite_count": len(FROZEN_SUITES),
        "required_case_execution_denominator": CASE_DENOMINATOR,
        "actual_candidate_case_executions": 0,
        "qualified_candidate_case_executions": 0,
        "completed_candidate_suite_count": 0,
        "all_required_suites_executed": False,
        "candidate_qualified": False,
        "blockers": [unavailable],
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(options.candidate is None and options.suite is None
                and options.label is None and options.source_sha256 is None
                and options.protocol_sha256 is None
                and options.document_sha256 is None
                and options.independence_audit_source_sha256 is None
                and options.independence_audit_protocol_sha256 is None
                and options.candidate_source_sha256 is None
                and options.native_engine_sha256 is None
                and options.native_bridge_sha256 is None
                and not options.owned_source_sha256
                and options.iso8859_1_locale is None
                and options.utf8_locale is None,
                "a source-only test cannot select or authorize a real engine")
        document = source_self_test()
    elif options.run:
        document = fail_closed_run(options)
    else:
        raise CandidateGateError(
            "BLOCKED: no internal candidate may run before a separately "
            "published real subinterpreter route and complete ownership audit",
        )
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CandidateProcessFailure as error:
        result = {
            "schema": SCHEMA + "-real-worker-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "message": str(error),
            "complete_failure_evidence": error.evidence,
            "clock_samples": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
        }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        raise SystemExit(1)
    except (
        CandidateGateError, OSError, ValueError, TypeError,
        KeyError, OverflowError, EOFError, gzip.BadGzipFile,
        subprocess.SubprocessError,
    ) as error:
        result = {
            "schema": SCHEMA + "-gate-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "message": str(error),
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        raise SystemExit(1)
