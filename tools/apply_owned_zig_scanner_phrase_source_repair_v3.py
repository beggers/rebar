#!/usr/bin/env python3
"""Freeze one first-party Zig Scanner construction correction, without running it."""

from __future__ import annotations

import __future__
import argparse
import ast
import builtins
import collections
import ctypes
import fcntl
import gzip
import hashlib
import importlib
import importlib.machinery
import io
import json
import os
from pathlib import Path, PurePosixPath
import random
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any
import zlib


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SCHEMA = "rebar-owned-zig-scanner-phrase-source-repair-v3"
SOURCE_PATH = "tools/apply_owned_zig_scanner_phrase_source_repair_v3.py"
PROTOCOL_PATH = "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V3.md"
CONTRACT_PATH = "oracle/phase2/zig-scanner-phrase-source-repair-v3.json"
MAX_OWNER_BYTES = 2 * 1024 * 1024
MATRIX_SHA256 = "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c"
PRIVATE_ROOT_PREFIX = "rebar-phase2-zig-scanner-phrase-source-build-v3-"
CORRECTED_ADAPTER_SHA256 = (
    "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b"
)
CORRECTED_REFERENCE_RECORDS_SHA256 = (
    "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
)
CORRECTED_REFERENCE_CACHE_SHA256 = (
    "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
)
PUBLIC_MATRIX_SHA256 = (
    "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
)
CORRECTED_PRODUCER_STATUS = "SOURCE FROZEN; CANDIDATES NOT RUN"
CORRECTED_ENGINE_RUNNER_STATUS = "NOT FROZEN"
V4_BLOCK_REASON = (
    "The corrected V4 case producer is frozen. Candidate workers V7/V9 and "
    "the Rust V5 campaign still use the obsolete baseline; freeze, commit, "
    "and push corrected V8/V10/V6 before any candidate run."
)

OWNERS: dict[str, tuple[str, int]] = {
    "GOAL.md": (
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756,
    ),
    "oracle/phase1/p0-completeness-v1.json": (
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632,
    ),
    "tools/run_owned_six_family_original_p0_producer_v3.py": (
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c", 195555,
    ),
    "tools/run_owned_six_family_original_p0_producer_v4.py": (
        "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782,
    ),
    "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md": (
        "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5", 5981,
    ),
    "oracle/phase2/six-family-p0-producer-v4.json": (
        "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867,
    ),
    "tools/verify_owned_public_type_reference_context_v1.py": (
        "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc", 102474,
    ),
    "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md": (
        "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018", 10691,
    ),
    "oracle/phase1/p0-public-type-reference-context-v1.json": (
        "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b", 13965,
    ),
    "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json": (
        "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670", 3892,
    ),
    (
        "oracle/phase1/evidence/"
        "public-type-reference-context-v1-cpython-3-14-6-"
        "candidate-context-p0-publication-receipt.json"
    ): (
        "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966", 2509,
    ),
    "tools/rust_scanner_differential_v1.py": (
        "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7", 39826,
    ),
    "tools/independent_scanner_verbose_comments_v1.py": (
        "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d", 88737,
    ),
    "candidates/zig_candidate.py": (
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422,
    ),
    "candidates/zig/mini_regex.zig": (
        "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915,
    ),
    "candidates/zig/py_bridge.c": (
        "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026,
    ),
    (
        "oracle/phase2/evidence/"
        "repaired-zig-original-campaign-v3-zig-phase2-v12-"
        "zig-scanner-v2-original-p0-failures-publication-receipt.json"
    ): (
        "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96", 4111,
    ),
    (
        "oracle/phase1/evidence/"
        "callable-introspection-reference-v2-cpython-3.14.6-"
        "publication-receipt.json"
    ): (
        "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334", 3533,
    ),
    "tools/render_candidate_current_overview_v38.py": (
        "8d6b83cd31cdb8d1b02d94946a4f4583e818fb649010a38f35e02ff9c66eac37", 98509,
    ),
    "docs/evidence/candidate-current-overview-v38.inputs.json": (
        "754dca58a8423255fb00eb6869894b2bb79017afb59e36081b6d62b88d00ff89", 165534,
    ),
    "docs/evidence/candidate-current-overview-v38.json": (
        "c8b1c018a018e4e3e26fb35c0901179945cf363d868019283f31689a8d5d411c", 496340,
    ),
    "docs/evidence/candidate-current-overview-v38.svg": (
        "7559d6ab328420d0b59741d38e003aafc4348bf7d3932c6e51b945c3069d7eaf", 11483,
    ),
    "tools/render_candidate_current_overview_v39.py": (
        "8adb7202644da2d19a4d2f50fe191de8d84007ce9b654a427a61fb4ea883c6b5", 115526,
    ),
    "docs/evidence/candidate-current-overview-v39.inputs.json": (
        "22e740d2f7a22e4bd485c5d6e83204bfd2c529f1b87dd041d4ed604849b69d6b", 198039,
    ),
    "docs/evidence/candidate-current-overview-v39.json": (
        "d25c486e36d82069c718f82a1f6281295d539606dcd72a0a6c2c295f5a4e4ca6", 561943,
    ),
    "docs/evidence/candidate-current-overview-v39.svg": (
        "eecc366a7e14e3bee67a801cbf4b07e848af3659a82cc0715a90525c05652a9a", 11485,
    ),
}

ORIGINAL_BLOCK = (
    b"        if not branches:\n"
    b"            raise RuntimeError(\"invalid SRE code\")\n"
    b"        group_count = len(branches)\n"
)
CORRECTED_BLOCK = (
    b"        group_count = len(branches)\n"
    b"        if not group_count or any(\n"
    b"            local_groups > group_count\n"
    b"            for _body, local_groups in branches\n"
    b"        ):\n"
    b"            raise RuntimeError(\"invalid SRE code\")\n"
)
EXPECTED_HISTOGRAM = {
    "nested-captures": 32,
    "numbered-captures": 16,
    "named-captures": 16,
}


class GateError(Exception):
    """An authentic source-only construction-correction gate failed."""


def require(value: Any, message: str) -> None:
    if value is not True:
        raise GateError(message)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact source-owned bytes")
    return hashlib.sha256(raw).hexdigest()


def valid_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "require a complete lowercase SHA-256 for " + label,
    )
    return value


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("ascii") + b"\n"
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as error:
        raise GateError("reject a noncanonical source-freeze document") from error


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        require(type(name) is str and name not in result,
                "reject a repeated or non-string JSON field")
        result[name] = value
    return result


def decode_document(raw: bytes, label: str) -> dict[str, Any]:
    try:
        result = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                GateError("reject a nonfinite " + label + ": " + value)
            ),
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise GateError("reject an invalid complete document: " + label) from error
    require(type(result) is dict, "require one exact document: " + label)
    return result


def safe_parts(relative: str) -> tuple[str, ...]:
    require(type(relative) is str and 0 < len(relative) <= 512,
            "require one bounded project-relative owner")
    parsed = PurePosixPath(relative)
    require(
        not parsed.is_absolute()
        and str(parsed) == relative
        and 0 < len(parsed.parts) <= 12
        and all(part not in ("", ".", "..") for part in parsed.parts)
        and not relative.endswith((".gz", ".so", ".dll", ".dylib"))
        and "holdout" not in relative.casefold()
        and "benchmark" not in relative.casefold(),
        "reject archives, native libraries, holdouts, or unsafe source paths",
    )
    return parsed.parts


def checked_read(relative: str, expected: str, size: int) -> bytes:
    parts = safe_parts(relative)
    valid_digest(expected, relative)
    require(type(size) is int and 0 < size <= MAX_OWNER_BYTES,
            "bound every complete source-owned input")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    descriptor: int | None = None
    try:
        for component in parts[:-1]:
            following = os.open(component, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode) and first.st_size == size,
                "reject an unowned or resized source: " + relative)
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            block = os.read(descriptor, min(65536, remaining))
            require(bool(block), "reject a truncated source: " + relative)
            pieces.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject a hidden source suffix: " + relative)
        raw = b"".join(pieces)
        final = os.fstat(descriptor)
        require(
            (first.st_dev, first.st_ino, first.st_size,
             first.st_mtime_ns, first.st_ctime_ns)
            == (final.st_dev, final.st_ino, final.st_size,
                final.st_mtime_ns, final.st_ctime_ns)
            and sha256(raw) == expected,
            "reject changed source identity or content: " + relative,
        )
        return raw
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def extract_matrix(raw: bytes) -> list[dict[str, Any]]:
    """Evaluate only the frozen pure matrix builder; never import its module."""
    try:
        tree = ast.parse(raw, filename="frozen original Scanner matrix", mode="exec")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise GateError("reject a malformed frozen Scanner matrix source") from error
    constants = {
        "PUBLISHED_SEED", "VARIANTS_PER_FAMILY", "FAMILIES",
        "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "UNICODE",
        "VERBOSE", "ASCII",
    }
    functions = {"require", "encode_subject", "encode_phrase", "_typed_phrase", "build_matrix"}
    selected: list[ast.stmt] = []
    found_constants: set[str] = set()
    found_functions: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [item.id for item in node.targets if isinstance(item, ast.Name)]
            if len(names) == 1 and names[0] in constants:
                try:
                    ast.literal_eval(node.value)
                except (ValueError, TypeError, RecursionError) as error:
                    raise GateError("reject a nonliteral original matrix constant") from error
                selected.append(node)
                found_constants.add(names[0])
        elif isinstance(node, ast.FunctionDef) and node.name in functions:
            require(node.name not in found_functions,
                    "reject a duplicate original pure matrix function")
            selected.append(node)
            found_functions.add(node.name)
    require(found_constants == constants and found_functions == functions,
            "preserve every exact frozen pure Scanner matrix dependency")
    namespace: dict[str, Any] = {
        "__builtins__": builtins.__dict__,
        "random": random,
        "ScannerOracleError": GateError,
    }
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(
        compile(
            module,
            "<frozen-original-scanner-matrix>",
            "exec",
            flags=__future__.annotations.compiler_flag,
            dont_inherit=True,
        ),
        namespace,
    )
    matrix = namespace["build_matrix"]()
    require(
        type(matrix) is list
        and len(matrix) == 1024
        and len(namespace["FAMILIES"]) == 32
        and namespace["VARIANTS_PER_FAMILY"] == 32
        and sha256(canonical(matrix)) == MATRIX_SHA256,
        "require the complete authentic 1,024-case original Scanner matrix",
    )
    return matrix


def count_phrase_captures(value: str | bytes) -> int:
    require(type(value) in (str, bytes), "reject a substituted Scanner phrase")
    phrase = value.decode("latin1") if type(value) is bytes else value
    captures = 0
    position = 0
    in_class = False
    while position < len(phrase):
        character = phrase[position]
        if character == "\\":
            position += 2
            continue
        if in_class:
            if character == "]":
                in_class = False
            position += 1
            continue
        if character == "[":
            in_class = True
            position += 1
            continue
        if character != "(":
            position += 1
            continue
        if phrase.startswith("(?#", position):
            close = phrase.find(")", position + 3)
            position = len(phrase) if close == -1 else close + 1
            continue
        if phrase.startswith("(?P<", position):
            captures += 1
        elif not phrase.startswith("(?", position):
            captures += 1
        position += 1
    return captures


def matrix_witness(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    require(
        type(matrix) is list
        and len(matrix) == 1024
        and sha256(canonical(matrix)) == MATRIX_SHA256,
        "reject an omitted, duplicated, reordered, or substituted Scanner case",
    )
    reject_counts: collections.Counter[str] = collections.Counter()
    rejected_ids: list[str] = []
    for index, row in enumerate(matrix):
        require(
            type(row) is dict
            and row.get("case") == "scanner-differential.v1." + format(index, "04d")
            and type(row.get("family")) is str
            and type(row.get("variant")) is int
            and type(row.get("lexicon")) is list,
            "reject a hidden or reordered original Scanner stimulus",
        )
        phrase_counts: list[int] = []
        for entry in row["lexicon"]:
            require(type(entry) is dict and type(entry.get("phrase")) is dict,
                    "retain every source-owned Scanner lexicon phrase")
            encoded = entry["phrase"]
            if encoded.get("type") == "str":
                require(set(encoded) == {"type", "value"}
                        and type(encoded.get("value")) is str,
                        "reject a changed original text Scanner phrase")
                phrase = encoded["value"]
            else:
                require(set(encoded) == {"type", "hex"}
                        and encoded.get("type") == "bytes"
                        and type(encoded.get("hex")) is str,
                        "reject a changed original bytes Scanner phrase")
                try:
                    phrase = bytes.fromhex(encoded["hex"])
                except ValueError as error:
                    raise GateError("reject an invalid original bytes phrase") from error
                require(phrase.hex() == encoded["hex"],
                        "reject noncanonical original Scanner phrase bytes")
            phrase_counts.append(count_phrase_captures(phrase))
        if any(count > len(row["lexicon"]) for count in phrase_counts):
            reject_counts[row["family"]] += 1
            rejected_ids.append(row["case"])
    require(dict(reject_counts) == EXPECTED_HISTOGRAM
            and len(rejected_ids) == 64
            and len(set(rejected_ids)) == 64
            and rejected_ids[0] == "scanner-differential.v1.0160",
            "derive exactly 32 nested, 16 numbered, and 16 named capture overflows")
    return {
        "matrix_sha256": MATRIX_SHA256,
        "matrix_case_count": 1024,
        "family_count": 32,
        "variants_per_family": 32,
        "overflow_case_count": 64,
        "overflow_family_case_counts": dict(reject_counts),
        "first_overflow_case": rejected_ids[0],
        "last_overflow_case": rejected_ids[-1],
        "overflow_case_ids_sha256": sha256(canonical(rejected_ids)),
        "preserved_nonoverflow_case_count": 960,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "candidate_imports": 0,
        "native_activations": 0,
    }


def derive_source(original: bytes) -> bytes:
    require(sha256(original) == OWNERS["candidates/zig_candidate.py"][0]
            and len(original) == OWNERS["candidates/zig_candidate.py"][1],
            "derive only from the exact actual first-party Zig adapter")
    require(original.count(ORIGINAL_BLOCK) == 1,
            "require one exact original Scanner construction block")
    require(original.count(CORRECTED_BLOCK) == 0,
            "reject an already applied or ambiguous Scanner correction")
    scanner = original.index(b"\nclass Scanner:\n")
    scan = original.index(b"\n    def scan(self, string):\n", scanner)
    offset = original.index(ORIGINAL_BLOCK)
    require(scanner < offset < scan,
            "limit the correction to the original owned Scanner constructor")
    corrected = original.replace(ORIGINAL_BLOCK, CORRECTED_BLOCK, 1)
    require(
        corrected.count(ORIGINAL_BLOCK) == 0
        and corrected.count(CORRECTED_BLOCK) == 1
        and corrected.replace(CORRECTED_BLOCK, ORIGINAL_BLOCK, 1) == original,
        "preserve every first-party adapter byte outside one exact correction",
    )
    require(
        len(corrected) == 68530
        and sha256(corrected) == CORRECTED_ADAPTER_SHA256,
        "derive only the exact independently witnessed, unapplied Zig overlay",
    )
    try:
        ast.parse(corrected, filename="private Zig Scanner phrase overlay")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise GateError("reject a syntactically invalid private Zig overlay") from error
    return corrected


class SourceOnlyBoundary:
    """Physically deny files, workers, imports, engines, timing, and archives."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = 0
        self.blocked_effects_by_kind = {
            kind: 0
            for kind in (
                "filesystem", "write", "process", "import", "network",
                "thread", "clock", "native", "lock", "signal", "decompression",
            )
        }

    def deny(self, name: str, kind: str) -> Any:
        def reject(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked += 1
            self.blocked_effects_by_kind[kind] += 1
            raise GateError("blocked source-only external effect: " + name)
        return reject

    def __enter__(self) -> "SourceOnlyBoundary":
        targets: list[tuple[Any, tuple[str, ...], str]] = [
            (builtins, ("open",), "filesystem"),
            (builtins, ("__import__",), "import"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir", "listdir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat", "resolve", "iterdir"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove",
                  "rename", "replace", "fsync", "symlink", "link"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink",
                    "rename", "replace", "touch"), "write"),
            (tempfile, ("mkdtemp", "mkstemp", "TemporaryFile",
                        "NamedTemporaryFile"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call",
                          "check_output", "_fork_exec"), "process"),
            (os, ("fork", "system", "posix_spawn", "posix_spawnp",
                  "execv", "execve", "execl", "execle", "execlp",
                  "execlpe", "execvp", "execvpe", "spawnv",
                  "spawnve", "spawnvp", "spawnvpe"), "process"),
            (importlib, ("import_module",), "import"),
            (importlib.machinery.SourceFileLoader,
             ("create_module", "exec_module", "load_module"), "import"),
            (importlib.machinery.SourcelessFileLoader,
             ("create_module", "exec_module", "load_module"), "import"),
            (importlib.machinery.ExtensionFileLoader,
             ("create_module", "exec_module", "load_module"), "native"),
            (importlib.machinery.BuiltinImporter,
             ("create_module", "exec_module", "load_module"), "native"),
            (importlib.machinery.FrozenImporter,
             ("create_module", "exec_module", "load_module"), "import"),
            (socket, ("socket", "create_connection", "getaddrinfo"), "network"),
            (threading, ("_start_joinable_thread", "_start_new_thread"), "thread"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "thread_time"), "clock"),
            (ctypes, ("CDLL", "PyDLL", "_dlopen"), "native"),
            (fcntl, ("flock", "lockf"), "lock"),
            (signal, ("signal", "pthread_sigmask", "raise_signal"), "signal"),
            (gzip, ("open", "decompress", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
        ]
        native_targets = (
            ("_io", ("open",), "filesystem"),
            ("posix", ("open", "read", "stat", "lstat",
                       "scandir", "listdir"), "filesystem"),
            ("posix", ("write", "mkdir", "unlink", "remove",
                       "rename", "replace", "fsync", "symlink", "link"),
             "write"),
            ("posix", ("fork", "posix_spawn", "posix_spawnp",
                       "execv", "execve", "spawnv", "spawnve"), "process"),
            ("_posixsubprocess", ("fork_exec",), "process"),
            ("_ctypes", ("dlopen",), "native"),
            ("_imp", ("create_dynamic", "exec_dynamic", "create_builtin",
                      "exec_builtin", "init_frozen"), "native"),
            ("_socket", ("socket", "getaddrinfo"), "network"),
            ("_thread", ("start_new_thread", "start_joinable_thread"), "thread"),
        )
        for module_name, names, kind in native_targets:
            module = sys.modules.get(module_name)
            if module is not None:
                targets.append((module, names, kind))
        for owner, names, kind in targets:
            for name in names:
                if hasattr(owner, name):
                    current = getattr(owner, name)
                    self.saved.append((owner, name, current))
                    setattr(owner, name, self.deny(name, kind))
        return self

    def __exit__(self, *_error: Any) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def validate_receipt(value: dict[str, Any]) -> None:
    expected: dict[str, Any] = {
        "schema": "rebar-owned-repaired-zig-original-campaign-v3-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": "zig", "candidate_status": "FAIL",
        "candidate_qualified": False, "case_execution_denominator": 31237,
        "suite_count": 13, "completed_suite_count": 13,
        "actual_candidate_workers": 13, "semantic_mismatch_count": 1764,
        "verified_passing_case_count": 3711, "infrastructure_failure_count": 0,
        "historical_zig_semantic_mismatch_count": 2172,
        "named_private_waiver_count": 13, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "winner_selected": False,
        "canonical_corrected_bridge_source_sha256":
            OWNERS["candidates/zig/py_bridge.c"][0],
    }
    for key, exact in expected.items():
        require(value.get(key) == exact, "preserve actual Zig publication field: " + key)
    archive = value.get("archive")
    require(
        type(archive) is dict
        and archive.get("sha256")
        == "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b"
        and archive.get("size_bytes") == 3722337
        and archive.get("device") == 2064
        and archive.get("inode") == 524695
        and archive.get("mode") == 384
        and value.get("uncompressed_bytes") == 5367720
        and value.get("uncompressed_sha256")
        == "5f33a22258baee31c972a13bbcb1f4be30c486982284a3c1f3cd6085ca1cd3f0",
        "bind the current matching history without opening its gzip archive",
    )


def validate_reference(value: dict[str, Any]) -> None:
    for key, exact in {
        "schema": "rebar-owned-callable-introspection-reference-v2-durable-publication-receipt",
        "status": "PASS", "reference_status": "PASS",
        "reference_failure_count": 0, "additional_case_count": 50,
        "actual_distinct_process_ids": [81, 82],
        "actual_reference_processes_started": 2,
        "additional_cases_included_in_original_denominator": False,
        "original_case_denominator": 31237, "original_suite_count": 13,
        "original_private_waiver_count": 13, "candidate_processes_started": 0,
        "candidate_introspection": "NOT MEASURED", "holdout": "NOT OPENED",
        "holdout_cases_read": 0, "matching_archives_opened": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED",
    }.items():
        require(value.get(key) == exact,
                "retain the real, separate 50-case Python reference: " + key)


def validate_public_falsification(value: dict[str, Any]) -> None:
    require(
        value.get("schema") == "rebar-public-type-candidate-context-falsification-v1"
        and value.get("version") == 1
        and value.get("status") == "FALSIFIED"
        and value.get("candidate_facing_self_oracle_status") == "FAIL",
        "preserve the actually recorded historical V37 public-reference failure",
    )
    original = value.get("original_oracle")
    require(
        type(original) is dict
        and original.get("case_execution_denominator") == 31237
        and original.get("suite_count") == 13
        and original.get("named_private_waiver_count") == 13
        and original.get("affected_suite") == "public_types_v1"
        and original.get("affected_suite_case_count") == 6912
        and original.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
        and original.get("original_cases_removed") == 0
        and original.get("additional_private_waivers") == 0
        and original.get("case_denominator_changed") is False,
        "never silently weaken the original 31,237-case public oracle",
    )
    replay = value.get("actual_replay")
    require(
        type(replay) is dict
        and replay.get("python_version") == "3.14.6"
        and replay.get("python_sha256") == PYTHON_SHA256
        and replay.get("isolated_python_process_id") == 80
        and replay.get("candidate_import_count") == 0
        and replay.get("candidate_workers_started") == 0
        and replay.get("reference_subprocesses_started") == 0
        and replay.get("matching_archives_opened") == 0
        and replay.get("holdout_opened") is False,
        "retain the exact genuine standard-only historical falsification",
    )
    cases = value.get("falsifying_cases")
    require(
        type(cases) is dict
        and cases.get("cohort") == "cache-pattern-type-separation"
        and cases.get("case_count") == 96
        and cases.get("text_subclass_case_count") == 48
        and cases.get("bytes_subclass_case_count") == 48
        and cases.get("case_ids_sha256")
        == "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
        and cases.get("exact_case_matrix_sha256")
        == "09b5d7cb665af227b8d6c733c795d68f9a1e22c62956b9d64105a9234af6abca"
        and cases.get("actual_named_context_stdlib_records_sha256")
        == CORRECTED_REFERENCE_CACHE_SHA256
        and cases.get("sole_normalized_difference_path")
        == "outcome.value.items[2].module"
        and cases.get("actual_candidate_facing_module")
        == "tools.independent_public_type_identity_serialization_v1"
        and cases.get("published_script_context_module") == "__main__",
        "preserve every actual historical public-type falsifying case",
    )
    meaning = value.get("interpretation")
    require(
        type(meaning) is dict
        and meaning.get("candidate_facing_python_against_python_agrees") is False
        and meaning.get("historical_rust_records_recomputed_or_deleted") is False
        and meaning.get("c_pattern_equality_failure_waived") is False
        and meaning.get("zig_pattern_equality_failure_waived") is False
        and meaning.get("all_candidate_matching_blocked") is True
        and meaning.get("same_context_reference_correction_status") == "NOT RUN"
        and meaning.get("separate_50_case_reference_status") == "PASS"
        and meaning.get("separate_50_case_candidate_status") == "NOT RUN"
        and meaning.get("final_holdout_opened") is False,
        "retain the V37 historical falsification without inventing a candidate run",
    )


def validate_corrected_public_reference(value: dict[str, Any]) -> None:
    expected: dict[str, Any] = {
        "schema": "rebar-phase1-owned-public-type-reference-context-v1-durable-publication-receipt",
        "version": 1,
        "status": "PASS",
        "publication_status": "PASS",
        "reference_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "source_sha256": OWNERS["tools/verify_owned_public_type_reference_context_v1.py"][0],
        "protocol_sha256": OWNERS["oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md"][0],
        "contract_sha256": OWNERS["oracle/phase1/p0-public-type-reference-context-v1.json"][0],
        "matrix_sha256": PUBLIC_MATRIX_SHA256,
        "public_case_count_per_reference": 6912,
        "original_case_execution_denominator": 31237,
        "attempted_reference_worker_count": 2,
        "actual_reference_worker_count": 2,
        "actual_started_reference_worker_count": 2,
        "completed_reference_worker_count": 2,
        "validated_reference_worker_count": 2,
        "actual_distinct_reference_process_ids": [81, 82],
        "full_reference_records_sha256": CORRECTED_REFERENCE_RECORDS_SHA256,
        "cache_records_sha256": CORRECTED_REFERENCE_CACHE_SHA256,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "uncompressed_bytes": 73371145,
        "uncompressed_sha256": (
            "bc6c0fc9b4e3ff57faecd7e6dda982c1099d170e09dd8ce5641c48872479bebd"
        ),
    }
    for key, exact in expected.items():
        require(value.get(key) == exact,
                "authenticate the actual corrected Python reference: " + key)
    archive = value.get("archive")
    require(
        type(archive) is dict
        and archive.get("path")
        == (
            "oracle/phase1/evidence/"
            "public-type-reference-context-v1-cpython-3-14-6-"
            "candidate-context-p0.json.gz"
        )
        and archive.get("sha256")
        == "c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05"
        and archive.get("bytes") == 1374913
        and archive.get("mode") == 384
        and archive.get("nlink") == 1
        and archive.get("file_fsync_completed") is True
        and archive.get("directory_fsync_completed") is True,
        "bind actual reference evidence through its receipt without opening its archive",
    )


def validate_v38_history(value: dict[str, Any]) -> None:
    for key, exact in {
        "schema": "rebar-candidate-current-overview-v38-summary",
        "status": "PASS", "full_case_denominator": 31237,
        "suite_count": 13, "private_waiver_count": 13,
        "qualified_candidate_count": 0,
        "authenticated_evidence_owner_lower_bound": 164,
        "authenticated_history_reference_lower_bound": 169,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "phase_one_reference_gate_status": "PASS",
        "same_context_reference_correction_status": "PASS",
        "candidate_facing_self_oracle_status": "PASS",
        "corrected_reference_status": "PASS",
        "corrected_reference_publication_status": "PASS",
        "corrected_reference_actual_worker_count": 2,
        "corrected_reference_process_ids": [81, 82],
        "corrected_reference_case_count_per_worker": 6912,
        "corrected_reference_cache_cases_per_worker": 96,
        "corrected_reference_full_records_sha256": CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256": CORRECTED_REFERENCE_CACHE_SHA256,
        "historical_reference_context_falsifying_case_count": 96,
        "reference_context_falsifying_case_count": 0,
        "all_candidate_matching_blocked": True,
        "candidate_case_producer_status": "STALE; CORRECTED V4 NOT FROZEN",
        "candidate_case_producer_corrected_v4_status": "NOT FROZEN",
        "candidate_case_producer_source_sha256":
            OWNERS["tools/run_owned_six_family_original_p0_producer_v3.py"][0],
        "rust_original_campaign_semantic_mismatch_count": 1036,
        "c_original_campaign_semantic_mismatch_count": 1230,
        "zig_original_campaign_semantic_mismatch_count": 1764,
        "zig_original_campaign_verified_passing_case_count": 3711,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": [81, 82],
        "additional_signature_candidate_status": "NOT RUN",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "reference_archive_gzip_inflation_count": 1,
        "candidate_matching_archives_opened_by_graph": 0,
        "final_holdout_opened": False,
        "final_comparison_planned_case_count": 4194304,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "winner_selected": False,
    }.items():
        require(value.get(key) == exact,
                "retain the actual corrected and fail-closed V38 result: " + key)
    require(value.get("zig_individual_suite_mismatches")
            == "NOT PRESENT IN DURABLE RECEIPT",
            "do not invent suite-level counts from the small durable receipt")


def validate_v39_renderer(raw: bytes) -> None:
    name = "tools/render_candidate_current_overview_v39.py"
    require(
        type(raw) is bytes
        and len(raw) == OWNERS[name][1]
        and sha256(raw) == OWNERS[name][0]
        and raw.endswith(b"\n")
        and not raw.endswith(b"\n\n"),
        "require the final whitespace-clean V39 renderer, not its withdrawn owner",
    )


def validate_overview(value: dict[str, Any]) -> None:
    for key, exact in {
        "schema": "rebar-candidate-current-overview-v39-summary",
        "status": "PASS",
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "qualified_candidate_count": 0,
        "authenticated_evidence_owner_lower_bound": 164,
        "authenticated_history_reference_lower_bound": 169,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "phase_one_reference_gate_status": "PASS",
        "same_context_reference_correction_status": "PASS",
        "candidate_facing_self_oracle_status": "PASS",
        "corrected_reference_status": "PASS",
        "corrected_reference_publication_status": "PASS",
        "corrected_reference_actual_worker_count": 2,
        "corrected_reference_process_ids": [81, 82],
        "corrected_reference_case_count_per_worker": 6912,
        "corrected_reference_cache_cases_per_worker": 96,
        "corrected_reference_full_records_sha256": CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256": CORRECTED_REFERENCE_CACHE_SHA256,
        "historical_reference_context_falsifying_case_count": 96,
        "reference_context_falsifying_case_count": 0,
        "all_candidate_matching_blocked": True,
        "candidate_case_producer_status": "FROZEN; CANDIDATE WORKERS STILL STALE",
        "candidate_case_producer_corrected_v4_status": CORRECTED_PRODUCER_STATUS,
        "candidate_case_producer_source_sha256":
            OWNERS["tools/run_owned_six_family_original_p0_producer_v4.py"][0],
        "candidate_case_producer_protocol_sha256":
            OWNERS["oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md"][0],
        "candidate_case_producer_contract_sha256":
            OWNERS["oracle/phase2/six-family-p0-producer-v4.json"][0],
        "candidate_matching_block_reason": V4_BLOCK_REASON,
        "rust_original_campaign_semantic_mismatch_count": 1036,
        "c_original_campaign_semantic_mismatch_count": 1230,
        "zig_original_campaign_semantic_mismatch_count": 1764,
        "zig_original_campaign_verified_passing_case_count": 3711,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": [81, 82],
        "additional_signature_candidate_status": "NOT RUN",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "reference_archive_gzip_inflation_count": 1,
        "candidate_matching_archives_opened_by_graph": 0,
        "final_holdout_opened": False,
        "final_comparison_planned_case_count": 4194304,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "winner_selected": False,
    }.items():
        require(
            value.get(key) == exact,
            "retain the actually frozen and runner-blocked V39 result: " + key,
        )
    require(
        value.get("zig_individual_suite_mismatches")
        == "NOT PRESENT IN DURABLE RECEIPT",
        "do not invent original Zig scanner suite results from a small receipt",
    )


def validate_corrected_v4_producer(value: dict[str, Any]) -> None:
    for key, exact in {
        "schema": "rebar-owned-six-family-original-p0-producer-v4-source-freeze",
        "version": 4,
        "status": "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        "phase": "CANDIDATES",
        "goal_sha256": OWNERS["GOAL.md"][0],
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "family_count": 6,
        "source_owner_count": 25,
        "pairwise_shared_semantic_source_count": 0,
    }.items():
        require(
            value.get(key) == exact,
            "authenticate the actually frozen independent V4 producer: " + key,
        )
    families = value.get("families")
    require(
        type(families) is list
        and [family.get("family") for family in families]
        == ["rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve all six actually distinct first-party candidate families",
    )
    phase = value.get("phase_one")
    require(
        type(phase) is dict
        and phase.get("case_execution_denominator") == 31237
        and phase.get("suite_count") == 13
        and phase.get("named_private_waiver_count") == 13
        and phase.get("inventory_sha256")
        == OWNERS["oracle/phase1/p0-completeness-v1.json"][0]
        and phase.get("supplemental_cases_added") is False,
        "preserve every original P0 obligation in the corrected V4 producer",
    )
    reference = value.get("corrected_candidate_context_public_type_reference")
    require(
        type(reference) is dict
        and reference.get("status") == "PASS"
        and reference.get("reference_status") == "PASS"
        and reference.get("publication_status") == "PASS"
        and reference.get("case_count") == 6912
        and reference.get("actual_reference_worker_count") == 2
        and reference.get("validated_reference_worker_count") == 2
        and reference.get("reference_pids") == [81, 82]
        and reference.get("records_sha256") == CORRECTED_REFERENCE_RECORDS_SHA256
        and reference.get("cache_case_count") == 96
        and reference.get("cache_records_sha256") == CORRECTED_REFERENCE_CACHE_SHA256
        and reference.get("candidate_run_starts_reference_processes") is False
        and reference.get("source_context_inflates_reference_archive") is False
        and reference.get("source_context_reads_reference_archive") is False,
        "bind the corrected V4 producer to both complete real Python references",
    )
    reference_owners = reference.get("owners")
    require(type(reference_owners) is dict,
            "retain every actual corrected V4 reference owner")
    for name, path in (
        ("source", "tools/verify_owned_public_type_reference_context_v1.py"),
        ("protocol", "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md"),
        ("contract", "oracle/phase1/p0-public-type-reference-context-v1.json"),
        (
            "receipt",
            "oracle/phase1/evidence/"
            "public-type-reference-context-v1-cpython-3-14-6-"
            "candidate-context-p0-publication-receipt.json",
        ),
        (
            "falsification",
            "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json",
        ),
    ):
        owner = reference_owners.get(name)
        require(
            type(owner) is dict
            and owner.get("relative") == path
            and owner.get("sha256") == OWNERS[path][0]
            and owner.get("size_bytes") == OWNERS[path][1],
            "preserve the actual corrected V4 reference owner: " + name,
        )
    effects = value.get("verification_effects")
    require(
        type(effects) is dict
        and effects.get("actual_candidate_imports") == 0
        and effects.get("actual_candidate_workers") == 0
        and effects.get("actual_native_libraries_loaded") == 0
        and effects.get("actual_source_builds") == 0
        and effects.get("actual_reference_workers") == 0
        and effects.get("actual_subprocesses_started") == 0
        and effects.get("candidate_qualified_count") == 0
        and effects.get("holdout") == "NOT OPENED"
        and effects.get("performance") == "NOT MEASURED"
        and effects.get("memory") == "NOT MEASURED"
        and effects.get("winner_selected") is False,
        "a frozen V4 producer is not an applied repair, candidate run, or winner",
    )


def load_context(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PYTHON,
        "use only the frozen isolated CPython 3.14.6 source verifier",
    )
    source = checked_read(SOURCE_PATH, valid_digest(source_pin, "repair source"),
                          os.stat(ROOT / SOURCE_PATH, follow_symlinks=False).st_size)
    protocol = checked_read(PROTOCOL_PATH, valid_digest(protocol_pin, "repair protocol"),
                            os.stat(ROOT / PROTOCOL_PATH, follow_symlinks=False).st_size)
    require(sha256(source) == source_pin and sha256(protocol) == protocol_pin,
            "independently pin both source-freeze instruction owners")
    loaded = {
        relative: checked_read(relative, fingerprint, size)
        for relative, (fingerprint, size) in OWNERS.items()
    }
    phase = decode_document(loaded["oracle/phase1/p0-completeness-v1.json"], "P0")
    denominator = phase.get("denominator")
    suites = phase.get("suites")
    require(
        type(denominator) is dict
        and denominator.get("final_required_case_execution_denominator") == 31237
        and denominator.get("available_frozen_vector_case_executions") == 31237
        and denominator.get("private_upstream_methods_outside_public_denominator") == 13
        and type(suites) is list and len(suites) == 13
        and sum(row["case_execution_count"] for row in suites) == 31237
        and [(row["id"], row["case_execution_count"]) for row in suites
             if row["id"] in ("scanner_v3", "scanner_verbose_v1")]
        == [("scanner_v3", 1024), ("scanner_verbose_v1", 2854)]
        and phase.get("phase_gate", {}).get("status") == "PASS",
        "preserve all 31,237 frozen cases, 13 groups, and both original scanner matrices",
    )
    receipt_name = next(name for name in OWNERS if name.endswith(
        "zig-scanner-v2-original-p0-failures-publication-receipt.json"))
    reference_name = next(name for name in OWNERS if name.endswith(
        "callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json"))
    corrected_reference_name = next(name for name in OWNERS if name.endswith(
        "candidate-context-p0-publication-receipt.json"))
    falsification_name = (
        "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json"
    )
    validate_receipt(decode_document(loaded[receipt_name], "actual Zig failure receipt"))
    validate_reference(decode_document(loaded[reference_name], "50-case Python receipt"))
    validate_public_falsification(decode_document(
        loaded[falsification_name], "actual preserved V37 public falsification",
    ))
    validate_corrected_public_reference(decode_document(
        loaded[corrected_reference_name],
        "actual corrected same-context Python reference receipt",
    ))
    frozen_reference = decode_document(
        loaded["oracle/phase1/p0-public-type-reference-context-v1.json"],
        "frozen corrected Python reference source contract",
    )
    require(
        frozen_reference.get("schema")
        == "rebar-phase1-owned-public-type-reference-context-v1-frozen-contract"
        and frozen_reference.get("phase") == "CORRECTNESS ORACLE"
        and frozen_reference.get("status")
        == "SOURCE FROZEN; CORRECTED TWO-REFERENCE BASELINE NOT RUN"
        and frozen_reference.get("source", {}).get("sha256")
        == OWNERS["tools/verify_owned_public_type_reference_context_v1.py"][0]
        and frozen_reference.get("protocol", {}).get("sha256")
        == OWNERS["oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md"][0]
        and frozen_reference.get("original_p0", {}).get(
            "case_execution_denominator"
        ) == 31237
        and frozen_reference.get("original_p0", {}).get("suite_count") == 13
        and frozen_reference.get("original_p0", {}).get(
            "named_private_waiver_count"
        ) == 13
        and frozen_reference.get("original_public_suite", {}).get("case_count")
        == 6912
        and frozen_reference.get("independently_reproduced_self_oracle_failure", {}).get(
            "case_count"
        ) == 96,
        "bind the pushed phase-one source freeze without relabeling its historical status",
    )
    validate_v38_history(decode_document(
        loaded["docs/evidence/candidate-current-overview-v38.json"],
        "actual preserved V38 overview",
    ))
    validate_v39_renderer(loaded["tools/render_candidate_current_overview_v39.py"])
    validate_corrected_v4_producer(decode_document(
        loaded["oracle/phase2/six-family-p0-producer-v4.json"],
        "actual corrected six-family V4 producer contract",
    ))
    validate_overview(decode_document(
        loaded["docs/evidence/candidate-current-overview-v39.json"],
        "actual current V39 overview",
    ))
    return {
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "owners": loaded,
        "corrected": derive_source(loaded["candidates/zig_candidate.py"]),
    }


def contract_document(context: dict[str, Any], witness: dict[str, Any]) -> dict[str, Any]:
    corrected = context["corrected"]
    return {
        "schema": SCHEMA,
        "version": 3,
        "status": "SOURCE FROZEN; CORRECTED CANDIDATE NOT RUN",
        "source": {"path": SOURCE_PATH, "sha256": context["source_sha256"]},
        "protocol": {"path": PROTOCOL_PATH, "sha256": context["protocol_sha256"]},
        "pinned_cpython": {"path": PYTHON, "sha256": PYTHON_SHA256, "version": "3.14.6"},
        "original_oracle": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "scanner_matrix_sha256": MATRIX_SHA256,
            "scanner_case_count": 1024,
            "verbose_scanner_case_count": 2854,
        },
        "actual_previous_matching": {
            "candidate_status": "FAIL",
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "case_execution_denominator": 31237,
            "candidate_workers": 13,
            "semantic_mismatch_count": 1764,
            "verified_passing_case_count": 3711,
            "infrastructure_failure_count": 0,
            "archive_sha256": "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b",
            "archive_compressed_bytes": 3722337,
            "archive_uncompressed_sha256": "5f33a22258baee31c972a13bbcb1f4be30c486982284a3c1f3cd6085ca1cd3f0",
            "archive_uncompressed_bytes": 5367720,
            "archive_opened_by_source_freeze": False,
            "historical_mismatch_count": 2172,
            "matching_receipt_sha256": OWNERS[next(
                name for name in OWNERS if name.endswith(
                    "zig-scanner-v2-original-p0-failures-publication-receipt.json"))][0],
        },
        "construction_repair": {
            "function": "candidates.zig_candidate.Scanner.__init__",
            "semantics": "reject a phrase with more capture groups than there are Scanner branches",
            "error_type": "RuntimeError",
            "error_message": "invalid SRE code",
            "first_source_ordered_case": "scanner-differential.v1.0160",
            "complete_original_scanner_matrix": witness,
            "original_adapter": {
                "path": "candidates/zig_candidate.py",
                "sha256": OWNERS["candidates/zig_candidate.py"][0],
                "bytes": OWNERS["candidates/zig_candidate.py"][1],
                "modified": False,
            },
            "original_block": {
                "sha256": sha256(ORIGINAL_BLOCK), "bytes": len(ORIGINAL_BLOCK),
                "occurrence_count": 1,
            },
            "corrected_block": {
                "sha256": sha256(CORRECTED_BLOCK), "bytes": len(CORRECTED_BLOCK),
                "occurrence_count": 1,
            },
            "corrected_private_adapter": {
                "sha256": sha256(corrected), "bytes": len(corrected),
                "materialized": False, "outside_block_unchanged": True,
            },
            "original_engine_modified": False,
            "original_bridge_modified": False,
            "corrected_candidate_matching": "NOT RUN",
            "verbose_scanner_620_mismatches": "NOT REPAIRED; CORRECTED CANDIDATE NOT RUN",
            "other_published_mismatches": "PRESERVED; CORRECTED CANDIDATE NOT RUN",
            "candidate_qualified": False,
        },
        "additional_callable_reference": {
            "case_count": 50, "reference_status": "PASS",
            "reference_failure_count": 0, "actual_reference_process_ids": [81, 82],
            "included_in_original_denominator": False,
            "candidate_status": "NOT RUN",
        },
        "actual_corrected_same_context_reference": {
            "reference_status": "PASS",
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "actual_reference_process_ids": [81, 82],
            "actual_reference_worker_count": 2,
            "case_count_per_reference": 6912,
            "full_reference_records_sha256": CORRECTED_REFERENCE_RECORDS_SHA256,
            "retained_public_type_case_count_per_reference": 96,
            "retained_public_type_records_sha256": CORRECTED_REFERENCE_CACHE_SHA256,
            "case_execution_denominator": 31237,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "archive_opened_by_source_freeze": False,
            "reference_receipt": {
                "path": next(
                    name for name in OWNERS
                    if name.endswith("candidate-context-p0-publication-receipt.json")
                ),
                "sha256": OWNERS[next(
                    name for name in OWNERS
                    if name.endswith("candidate-context-p0-publication-receipt.json")
                )][0],
            },
        },
        "preserved_v37_public_falsification": {
            "status": "FALSIFIED",
            "isolated_standard_reference_process_id": 80,
            "public_type_case_count": 96,
            "text_subclass_case_count": 48,
            "bytes_subclass_case_count": 48,
            "evidence": {
                "path": (
                    "oracle/phase1/evidence/"
                    "public-type-candidate-context-falsification-v1.json"
                ),
                "sha256": OWNERS[
                    "oracle/phase1/evidence/"
                    "public-type-candidate-context-falsification-v1.json"
                ][0],
            },
            "historical_candidate_failure_waived": False,
            "historical_result_removed": False,
        },
        "shared_candidate_producer_gate": {
            "current_producer": {
                "path": "tools/run_owned_six_family_original_p0_producer_v4.py",
                "sha256": OWNERS[
                    "tools/run_owned_six_family_original_p0_producer_v4.py"
                ][0],
                "protocol_sha256": OWNERS[
                    "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md"
                ][0],
                "contract_sha256": OWNERS[
                    "oracle/phase2/six-family-p0-producer-v4.json"
                ][0],
                "status": "FROZEN; CANDIDATE WORKERS STILL STALE",
            },
            "corrected_v4_status": CORRECTED_PRODUCER_STATUS,
            "corrected_v4_source_sha256": OWNERS[
                "tools/run_owned_six_family_original_p0_producer_v4.py"
            ][0],
            "historical_v3_producer": {
                "path": "tools/run_owned_six_family_original_p0_producer_v3.py",
                "sha256": OWNERS[
                    "tools/run_owned_six_family_original_p0_producer_v3.py"
                ][0],
                "status": "STALE; PRESERVED",
            },
            "corrected_engine_runner_status": CORRECTED_ENGINE_RUNNER_STATUS,
            "required_corrected_engine_runners": ["V6", "V8", "V10"],
            "all_candidate_matching_blocked": True,
            "source_apply": "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
            "native_build": "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
            "candidate_matching": "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
            "reason": V4_BLOCK_REASON,
        },
        "authenticated_historical_lower_bounds": {
            "overview": "V39",
            "repository_evidence_owner_count": 164,
            "authenticated_reference_count": 169,
            "whole_repository_census_claimed": False,
        },
        "from_scratch_policy": {
            "stdlib_matching_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "another_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "source_only_effects": {
            "candidate_imports": 0, "candidate_workers_started": 0,
            "reference_workers_started": 0, "native_libraries_loaded": 0,
            "native_builds_started": 0, "matching_archives_opened": 0,
            "matching_archives_inflated": 0, "reference_archives_opened": 0,
            "benchmark_files_opened": 0, "holdout_files_opened": 0,
            "clock_samples": 0, "files_written": 0,
        },
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
        "frozen_owners": [
            {"path": path, "sha256": pin, "bytes": size}
            for path, (pin, size) in OWNERS.items()
        ],
    }


def hostile_controls(matrix: list[dict[str, Any]], context: dict[str, Any]) -> int:
    rejected = 0

    def reject(operation: Any, label: str) -> None:
        nonlocal rejected
        try:
            operation()
        except (GateError, TypeError, ValueError, OSError, SyntaxError, RecursionError):
            rejected += 1
        else:
            raise GateError("accepted hostile source-only control: " + label)

    reject(lambda: matrix_witness(matrix[:-1]), "dropped frozen scanner case")
    modified = [dict(item) for item in matrix]
    modified[160] = dict(modified[160], case="scanner-differential.v1.0161")
    reject(lambda: matrix_witness(modified), "reordered first genuine capture failure")
    for index in range(0, len(matrix), 16):
        changed = list(matrix)
        changed[index] = dict(
            changed[index],
            case="scanner-differential.v1." + format((index + 1) % len(matrix), "04d"),
        )
        reject(
            lambda rows=changed: matrix_witness(rows),
            "changed original scanner case " + format(index, "04d"),
        )
    for forged in (b"", context["owners"]["candidates/zig_candidate.py"][:-1],
                   context["corrected"], ORIGINAL_BLOCK):
        reject(lambda value=forged: derive_source(value), "wrong immutable adapter")
    for phrase, expected in (
        (r"((a)(b(c)?))", 4), (r"(a)(b)(c)?", 3),
        (r"(?P<first>a)(?P<second>b)(?P<third>c)?", 3),
        (r"(?:a)(?=b)(?!c)", 0), (r"\(a\)", 0),
        (r"[(](a)[)]", 1), (r"(?#hidden (a))(b)", 1),
        (r"(?P=word)", 0), (b"(a)(b)", 2),
    ):
        require(count_phrase_captures(phrase) == expected,
                "preserve source-owned phrase capture semantics")
    original = context["owners"]["candidates/zig_candidate.py"]
    reject(lambda: derive_source(original.replace(ORIGINAL_BLOCK, ORIGINAL_BLOCK + b" ", 1)),
           "out-of-block source tampering")
    receipt_name = next(name for name in OWNERS if name.endswith(
        "zig-scanner-v2-original-p0-failures-publication-receipt.json"))
    receipt = decode_document(context["owners"][receipt_name], "actual receipt")
    for key, value in (
        ("candidate_status", "PASS"), ("semantic_mismatch_count", 1700),
        ("verified_passing_case_count", 29473), ("suite_count", 12),
        ("actual_candidate_workers", 12), ("infrastructure_failure_count", 1),
        ("case_execution_denominator", 31301), ("holdout", "OPENED"),
        ("performance", "1.5x"), ("winner_selected", True),
    ):
        reject(lambda k=key, v=value: validate_receipt(dict(receipt, **{k: v})),
               "forged actual matching field " + key)
    reference_name = next(name for name in OWNERS if name.endswith(
        "callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json"))
    reference = decode_document(context["owners"][reference_name], "actual reference")
    for key, value in (
        ("reference_status", "FAIL"), ("reference_failure_count", 1),
        ("additional_case_count", 49), ("actual_distinct_process_ids", [81, 81]),
        ("additional_cases_included_in_original_denominator", True),
        ("candidate_introspection", "PASS"), ("holdout", "OPENED"),
    ):
        reject(lambda k=key, v=value: validate_reference(dict(reference, **{k: v})),
               "forged independent 50-case reference " + key)
    corrected_name = next(
        name for name in OWNERS
        if name.endswith("candidate-context-p0-publication-receipt.json")
    )
    corrected_reference = decode_document(
        context["owners"][corrected_name], "actual corrected public reference"
    )
    for key, value in (
        ("status", "FAIL"),
        ("publication_status", "FAIL"),
        ("reference_status", "FAIL"),
        ("publication_pass_means", "REFERENCE PASSES"),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("contract_sha256", "0" * 64),
        ("matrix_sha256", "0" * 64),
        ("public_case_count_per_reference", 6911),
        ("original_case_execution_denominator", 31236),
        ("attempted_reference_worker_count", 1),
        ("actual_reference_worker_count", 1),
        ("actual_started_reference_worker_count", 1),
        ("completed_reference_worker_count", 1),
        ("validated_reference_worker_count", 1),
        ("actual_distinct_reference_process_ids", [81, 81]),
        ("full_reference_records_sha256", "0" * 64),
        ("cache_records_sha256", "0" * 64),
        ("candidate_imports", 1),
        ("candidate_workers_started", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("uncompressed_bytes", 73371144),
        ("uncompressed_sha256", "0" * 64),
    ):
        reject(
            lambda k=key, v=value: validate_corrected_public_reference(
                dict(corrected_reference, **{k: v})
            ),
            "forged actual corrected 6,912-case reference " + key,
        )
    falsification_path = (
        "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json"
    )
    falsification = decode_document(
        context["owners"][falsification_path],
        "actual preserved 96-case historical falsification",
    )
    for key, value in (
        ("status", "PASS"),
        ("candidate_facing_self_oracle_status", "PASS"),
        ("schema", "substituted-public-falsification"),
        ("version", 2),
    ):
        reject(
            lambda k=key, v=value: validate_public_falsification(
                dict(falsification, **{k: v})
            ),
            "forged actual historical public falsification " + key,
        )
    for section, key, value in (
        ("original_oracle", "case_execution_denominator", 31236),
        ("original_oracle", "suite_count", 12),
        ("original_oracle", "named_private_waiver_count", 14),
        ("original_oracle", "affected_suite_case_count", 6911),
        ("actual_replay", "isolated_python_process_id", 81),
        ("actual_replay", "candidate_workers_started", 1),
        ("actual_replay", "matching_archives_opened", 1),
        ("falsifying_cases", "case_count", 95),
        ("falsifying_cases", "text_subclass_case_count", 47),
        ("falsifying_cases", "bytes_subclass_case_count", 47),
        ("falsifying_cases", "actual_named_context_stdlib_records_sha256", "0" * 64),
        ("interpretation", "zig_pattern_equality_failure_waived", True),
        ("interpretation", "all_candidate_matching_blocked", False),
    ):
        nested = dict(falsification[section])
        nested[key] = value
        reject(
            lambda name=section, changed=nested: validate_public_falsification(
                dict(falsification, **{name: changed})
            ),
            "forged historical falsification " + section + "." + key,
        )
    history = decode_document(
        context["owners"]["docs/evidence/candidate-current-overview-v38.json"],
        "actual V38 history",
    )
    for key, value in (
        ("corrected_reference_status", "NOT RUN"),
        ("corrected_reference_process_ids", [81, 81]),
        ("candidate_case_producer_corrected_v4_status", "FROZEN"),
        ("all_candidate_matching_blocked", False),
        ("historical_reference_context_falsifying_case_count", 0),
        ("zig_original_campaign_semantic_mismatch_count", 1763),
        ("final_holdout_opened", True),
    ):
        reject(
            lambda k=key, v=value: validate_v38_history(dict(history, **{k: v})),
            "forged independently preserved V38 history " + key,
        )
    current_renderer = context["owners"][
        "tools/render_candidate_current_overview_v39.py"
    ]
    reject(
        lambda: validate_v39_renderer(current_renderer + b"\n"),
        "reject the withdrawn V39 renderer trailing-blank defect",
    )
    reject(
        lambda: validate_v39_renderer(current_renderer[:-1]),
        "reject a truncated or non-newline-terminated V39 renderer",
    )
    frozen_v4 = decode_document(
        context["owners"]["oracle/phase2/six-family-p0-producer-v4.json"],
        "actual corrected V4 producer",
    )
    for key, value in (
        ("status", "NOT FROZEN"),
        ("phase", "CORRECTNESS ORACLE"),
        ("goal_sha256", "0" * 64),
        ("case_execution_denominator", 31236),
        ("suite_count", 12),
        ("family_count", 5),
        ("source_owner_count", 24),
        ("pairwise_shared_semantic_source_count", 1),
    ):
        reject(
            lambda k=key, v=value: validate_corrected_v4_producer(
                dict(frozen_v4, **{k: v})
            ),
            "forged genuinely frozen six-family V4 producer " + key,
        )
    for section, key, value in (
        ("corrected_candidate_context_public_type_reference", "status", "FAIL"),
        ("corrected_candidate_context_public_type_reference",
         "actual_reference_worker_count", 1),
        ("corrected_candidate_context_public_type_reference",
         "reference_pids", [81, 81]),
        ("corrected_candidate_context_public_type_reference",
         "records_sha256", "0" * 64),
        ("corrected_candidate_context_public_type_reference",
         "cache_case_count", 95),
        ("verification_effects", "actual_candidate_workers", 1),
        ("verification_effects", "actual_source_builds", 1),
        ("verification_effects", "holdout", "OPENED"),
    ):
        changed_section = dict(frozen_v4[section])
        changed_section[key] = value
        reject(
            lambda name=section, changed=changed_section:
                validate_corrected_v4_producer(
                    dict(frozen_v4, **{name: changed})
                ),
            "forged actual V4 " + section + "." + key,
        )
    overview = decode_document(
        context["owners"]["docs/evidence/candidate-current-overview-v39.json"], "V39")
    for key, value in (
        ("status", "FAIL"),
        ("full_case_denominator", 31236),
        ("suite_count", 12),
        ("private_waiver_count", 14),
        ("qualified_candidate_count", 1),
        ("authenticated_evidence_owner_lower_bound", 163),
        ("authenticated_history_reference_lower_bound", 168),
        ("evidence_owner_count_is_authenticated_lower_bound", False),
        ("history_reference_count_is_authenticated_lower_bound", False),
        ("phase_one_reference_gate_status", "FAIL"),
        ("same_context_reference_correction_status", "NOT RUN"),
        ("candidate_facing_self_oracle_status", "FAIL"),
        ("corrected_reference_status", "NOT RUN"),
        ("corrected_reference_publication_status", "FAIL"),
        ("corrected_reference_actual_worker_count", 1),
        ("corrected_reference_process_ids", [81, 81]),
        ("corrected_reference_case_count_per_worker", 6911),
        ("corrected_reference_cache_cases_per_worker", 95),
        ("corrected_reference_full_records_sha256", "0" * 64),
        ("corrected_reference_cache_records_sha256", "0" * 64),
        ("historical_reference_context_falsifying_case_count", 95),
        ("reference_context_falsifying_case_count", 96),
        ("all_candidate_matching_blocked", False),
        ("candidate_case_producer_status", "STALE; CORRECTED V4 NOT FROZEN"),
        ("candidate_case_producer_corrected_v4_status", "NOT FROZEN"),
        ("candidate_case_producer_source_sha256", "0" * 64),
        ("zig_original_campaign_semantic_mismatch_count", 1700),
        ("zig_original_campaign_verified_passing_case_count", 4000),
        ("runtime_no_delegation", "VERIFIED"),
        ("production_runtime_delegation_audit", "VERIFIED"),
        ("additional_signature_reference_status", "NOT RUN"),
        ("additional_signature_candidate_status", "PASS"),
        ("reference_archive_gzip_inflation_count", 0),
        ("candidate_matching_archives_opened_by_graph", 1),
        ("final_holdout_opened", True),
        ("final_comparison_planned_case_count", 4194303),
        ("performance", "1.5x"),
        ("memory", "1 MiB"),
        ("winner_selected", True),
        ("zig_individual_suite_mismatches", {"scanner_v3": 64}),
    ):
        reject(lambda k=key, v=value: validate_overview(dict(overview, **{k: v})),
               "forged current overview " + key)
    source_arguments = [
        "--source-sha256", context["source_sha256"],
        "--protocol-sha256", context["protocol_sha256"],
        "--contract-sha256", "0" * 64,
    ]
    for forbidden in (
        "--apply", "--build", "--compile", "--match", "--run",
        "--run-candidate", "--record-reference", "--benchmark",
        "--holdout", "--install", "--apply-source", "--run-matching",
    ):
        reject(
            lambda mode=forbidden: parse_arguments([
                "--self-test", mode, *source_arguments,
            ]),
            "refuse actual operation while corrected V6/V8/V10 is not frozen: "
            + forbidden,
        )
    reject(
        lambda: parse_arguments([
            "--self-test", "--verify-frozen-context", *source_arguments,
        ]),
        "reject conflicting source-only and actual authorization modes",
    )
    for unsafe in (
        "../GOAL.md", "/tmp/holdout", "oracle/phase2/evidence/result.json.gz",
        "candidates/_zig_probe.so", "performance/benchmark.json",
        "docs/evidence/holdout.json", "candidates/../zig_candidate.py",
        "oracle/phase1/evidence/public-reference.json.gz",
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    ):
        reject(lambda value=unsafe: safe_parts(value), "unsafe source owner " + unsafe)
    require(rejected >= 150,
            "exercise complete original cases, real references, and fail-closed V4 controls")
    return rejected


def source_only_result(context: dict[str, Any], *, run_hostile: bool) -> dict[str, Any]:
    existing = frozenset(name for name in sys.modules
                         if name == "candidates" or name.startswith("candidates."))
    with SourceOnlyBoundary() as boundary:
        matrix = extract_matrix(context["owners"]["tools/rust_scanner_differential_v1.py"])
        witness = matrix_witness(matrix)
        blocked_before = boundary.blocked
        if run_hostile:
            blocked_operations: list[tuple[str, Any, str]] = [
                ("filesystem", lambda: builtins.open("GOAL.md"), "file opening"),
                ("filesystem", lambda: os.open("GOAL.md", os.O_RDONLY), "native file opening"),
                ("filesystem", lambda: io.open("GOAL.md"), "alternate file opening"),
                ("import", lambda: importlib.import_module(
                    "candidates.zig_candidate"
                ), "candidate import"),
                ("import", lambda: builtins.__import__(
                    "candidates.zig_candidate"
                ), "direct candidate import"),
                ("import", lambda: importlib.import_module("re"), "stdlib matching import"),
                ("native", lambda: ctypes.CDLL("libregex.so"), "native matcher load"),
                ("native", lambda: ctypes._dlopen("libregex.so"), "direct native matcher load"),
                ("process", lambda: subprocess.run([PYTHON]), "worker creation"),
                ("process", lambda: os.execv("/forbidden-zig-worker", []), "direct exec"),
                ("network", lambda: socket.socket(), "network"),
                ("thread", lambda: threading.Thread().start(), "thread creation"),
                ("decompression", lambda: gzip.open("matching.json.gz"), "matching gzip"),
                ("decompression", lambda: gzip.decompress(b""), "archive inflation"),
                ("clock", lambda: time.time(), "timing sample"),
                ("write", lambda: os.remove("GOAL.md"), "source deletion"),
                ("write", lambda: os.replace("a", "b"), "source overwrite"),
                ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX), "native file lock"),
                ("signal", lambda: signal.signal(
                    signal.SIGINT, signal.SIG_DFL
                ), "process signal"),
                ("native", lambda: importlib.machinery.ExtensionFileLoader.create_module(
                    None, None
                ), "native extension create_module"),
                ("native", lambda: importlib.machinery.ExtensionFileLoader.exec_module(
                    None, None
                ), "native extension exec_module"),
                ("import", lambda: importlib.machinery.SourceFileLoader.create_module(
                    None, None
                ), "source loader create_module"),
                ("import", lambda: importlib.machinery.SourceFileLoader.exec_module(
                    None, None
                ), "source loader exec_module"),
            ]
            for module_name, attribute, kind, arguments in (
                ("_io", "open", "filesystem", ("forbidden-zig-source",)),
                ("posix", "open", "filesystem", ("forbidden-zig-source", 0)),
                ("posix", "execv", "process", ("/forbidden-zig-process", [])),
                ("_posixsubprocess", "fork_exec", "process", ()),
                ("_ctypes", "dlopen", "native", ("forbidden-zig-engine.so",)),
                ("_imp", "create_dynamic", "native", (None,)),
                ("_imp", "exec_dynamic", "native", (None,)),
                ("_imp", "create_builtin", "native", (None,)),
                ("_imp", "exec_builtin", "native", (None,)),
                ("_socket", "socket", "network", ()),
                ("_thread", "start_new_thread", "thread", (lambda: None, ())),
                ("_thread", "start_joinable_thread", "thread", (lambda: None,)),
            ):
                native_module = sys.modules.get(module_name)
                if native_module is not None and hasattr(native_module, attribute):
                    blocked_operations.append((
                        kind,
                        lambda owner=native_module, name=attribute, args=arguments:
                            getattr(owner, name)(*args),
                        "direct native module " + module_name + "." + attribute,
                    ))
            for attribute in (
                "execv", "execve", "execl", "execle", "execlp", "execlpe",
                "execvp", "execvpe", "spawnv", "spawnve", "spawnvp",
                "spawnvpe", "posix_spawn", "posix_spawnp", "fork",
            ):
                if hasattr(os, attribute):
                    blocked_operations.append((
                        "process",
                        lambda name=attribute: getattr(os, name)(),
                        "direct process entry " + attribute,
                    ))
            if hasattr(subprocess, "_fork_exec"):
                blocked_operations.append((
                    "process", lambda: subprocess._fork_exec(),
                    "direct subprocess native fork",
                ))
            if hasattr(threading, "_start_joinable_thread"):
                blocked_operations.append((
                    "thread",
                    lambda: threading._start_joinable_thread(lambda: None),
                    "direct native thread launch",
                ))
            for kind, operation, label in blocked_operations:
                previous = boundary.blocked_effects_by_kind[kind]
                try:
                    operation()
                except GateError:
                    require(
                        boundary.blocked_effects_by_kind[kind] == previous + 1,
                        "prove the actual source-only barrier stopped " + label,
                    )
                else:
                    raise GateError("source-only boundary allowed " + label)
            require(
                all(value > 0 for value in boundary.blocked_effects_by_kind.values()),
                "exercise every first-party Zig source-only physical effect boundary",
            )
        blocked = boundary.blocked - blocked_before
        blocked_by_kind = dict(boundary.blocked_effects_by_kind)
        require(
            frozenset(name for name in sys.modules
                      if name == "candidates" or name.startswith("candidates.")) == existing,
            "a candidate was imported by a source-only gate",
        )
    rejects = hostile_controls(matrix, context) if run_hostile else 0
    return {
        "schema": SCHEMA + "-source-only-result",
        "status": "PASS",
        "mode": "SELF-TEST" if run_hostile else "FROZEN CONTEXT",
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "named_private_waiver_count": 13,
        "matrix": witness,
        "historical_zig_mismatches": 1764,
        "historical_zig_verified_passing_cases": 3711,
        "corrected_reference_status": "PASS",
        "corrected_reference_process_ids": [81, 82],
        "corrected_reference_case_count_per_worker": 6912,
        "corrected_reference_full_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_retained_public_type_cases": 96,
        "corrected_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_SHA256,
        "historical_public_reference_falsification_status": "FALSIFIED",
        "historical_public_reference_falsifying_case_count": 96,
        "current_overview": "V39",
        "authenticated_evidence_owner_lower_bound": 164,
        "authenticated_history_reference_lower_bound": 169,
        "candidate_case_producer_status": "FROZEN; CANDIDATE WORKERS STILL STALE",
        "candidate_case_producer_corrected_v4_status": CORRECTED_PRODUCER_STATUS,
        "candidate_case_producer_corrected_v4_source_sha256": OWNERS[
            "tools/run_owned_six_family_original_p0_producer_v4.py"
        ][0],
        "candidate_engine_runner_corrected_status": CORRECTED_ENGINE_RUNNER_STATUS,
        "required_corrected_engine_runners": ["V6", "V8", "V10"],
        "all_candidate_matching_blocked": True,
        "source_apply_status": "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
        "native_build_status": "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
        "corrected_candidate_matching":
            "NOT RUN; BLOCKED UNTIL CORRECTED V6/V8/V10 IS FROZEN",
        "candidate_matching_block_reason": V4_BLOCK_REASON,
        "verbose_scanner_620_mismatches": "NOT REPAIRED; CORRECTED CANDIDATE NOT RUN",
        "additional_callable_reference_status": "PASS",
        "additional_callable_case_count": 50,
        "additional_callable_candidate_status": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "derived_adapter_sha256": sha256(context["corrected"]),
        "derived_adapter_bytes": len(context["corrected"]),
        "derived_adapter_materialized": False,
        "hostile_controls_rejected": rejects,
        "external_effect_controls_blocked": blocked,
        "blocked_effects_by_kind": blocked_by_kind,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "native_libraries_loaded": 0,
        "matching_archives_opened": 0,
        "matching_archives_inflated": 0,
        "holdout_files_opened": 0,
        "benchmark_files_opened": 0,
        "clock_samples": 0,
        "files_written": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


class SourceOnlyArgumentParser(argparse.ArgumentParser):
    """Reject unauthorized repair actions without exiting the source verifier."""

    def error(self, message: str) -> None:
        raise GateError("reject unauthorized Zig source-freeze arguments: " + message)


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    options_seen = [item for item in values if item.startswith("--")]
    require(
        len(options_seen) == len(set(options_seen)),
        "reject repeated or ambiguous Zig source-freeze authorizations",
    )
    parser = SourceOnlyArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    return parser.parse_args(values)


def main() -> int:
    try:
        options = parse_arguments()
        context = load_context(options.source_sha256, options.protocol_sha256)
        result = source_only_result(context, run_hostile=options.self_test)
        expected = contract_document(context, result["matrix"])
        if options.render_contract:
            require(options.contract_sha256 is None,
                    "do not invent a hash for the contract being rendered")
            sys.stdout.buffer.write(canonical(expected))
            return 0
        require(options.contract_sha256 is not None,
                "independently pin the complete source, protocol, and contract")
        contract_size = os.stat(ROOT / CONTRACT_PATH, follow_symlinks=False).st_size
        raw_contract = checked_read(
            CONTRACT_PATH, valid_digest(options.contract_sha256, "repair contract"),
            contract_size,
        )
        contract = decode_document(raw_contract, "V3 construction repair contract")
        require(canonical(contract) == raw_contract,
                "require one canonical, complete V3 construction repair contract")
        require(contract == expected,
                "bind the exact V3 contract to all actual owners and the complete matrix")
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GateError, OSError, ValueError, TypeError, KeyError, IndexError,
            json.JSONDecodeError, RecursionError) as error:
        sys.stderr.write("zig-scanner-phrase-v3: " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
