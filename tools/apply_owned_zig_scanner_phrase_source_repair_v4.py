#!/usr/bin/env python3
"""Freeze the materialized, first-party Zig Scanner correction without matching."""

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
from pathlib import Path
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
SCHEMA = "rebar-owned-zig-scanner-phrase-source-repair-v4"
VERSION = 4
SOURCE_PATH = "tools/apply_owned_zig_scanner_phrase_source_repair_v4.py"
PROTOCOL_PATH = "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md"
CONTRACT_PATH = "oracle/phase2/zig-scanner-phrase-source-repair-v4.json"
VARIANT_PATH = "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"
MAX_OWNER_BYTES = 8 * 1024 * 1024
MATRIX_SHA256 = "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c"
OVERFLOW_SHA256 = "e1b75493de4be5ea1583e30077737405112b22fdb072cd8b0e38e2770a2959e6"
VARIANT_SHA256 = "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b"
GRAPH_VERSION = 72
EVIDENCE_LOWER_BOUND = 239
HISTORY_LOWER_BOUND = 244
ORIGINAL_BLOCK = (
    b"        if not branches:\n"
    b'            raise RuntimeError("invalid SRE code")\n'
    b"        group_count = len(branches)\n"
)
CORRECTED_BLOCK = (
    b"        group_count = len(branches)\n"
    b"        if not group_count or any(\n"
    b"            local_groups > group_count\n"
    b"            for _body, local_groups in branches\n"
    b"        ):\n"
    b'            raise RuntimeError("invalid SRE code")\n'
)
EXPECTED_HISTOGRAM = {
    "nested-captures": 32,
    "numbered-captures": 16,
    "named-captures": 16,
}
SUITE_CASES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
OWNERS: dict[str, tuple[str, int]] = {
    "GOAL.md": (
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756,
    ),
    "oracle/phase1/p0-completeness-v1.json": (
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632,
    ),
    "tools/verify_owned_p0_completeness_v4.py": (
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d", 29094,
    ),
    "oracle/phase1/P0-COMPLETENESS-V4.md": (
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2", 4261,
    ),
    "oracle/phase1/p0-completeness-v4.json": (
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875,
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
    "tools/rust_scanner_differential_v1.py": (
        "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7", 39826,
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
    "tools/apply_owned_zig_scanner_phrase_source_repair_v3.py": (
        "9b5cf55b9d66729b84b91470f8ba5906208ccee09312b43c329acaab2ff34010", 84556,
    ),
    "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V3.md": (
        "78fccd7fffd33e5ecd9a9033d8225c294d82ee07f391eb46ccd621a08e0d38e1", 6205,
    ),
    "oracle/phase2/zig-scanner-phrase-source-repair-v3.json": (
        "4eee672b4fe6f25f7481c34a34928f00d34a45a9e0675e024238a8ee5576fade", 11117,
    ),
    (
        "oracle/phase2/evidence/"
        "repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-"
        "original-p0-failures-publication-receipt.json"
    ): (
        "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96", 4111,
    ),
    (
        "oracle/phase1/evidence/"
        "differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/"
        "two-independent-reference-result.json"
    ): (
        "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096", 3658,
    ),
    "tools/render_candidate_current_overview_v72.py": (
        "b279901481d2f4f6bc1adeae542d5aacf2453dedbcff88a944a79ce5c8478753", 37922,
    ),
    "docs/evidence/candidate-current-overview-v72.inputs.json": (
        "28f235f8bbb7e49de25a1194fa0693e9764d3e5b0ef7a3e5a4da8e273f22eaef", 1134228,
    ),
    "docs/evidence/candidate-current-overview-v72.json": (
        "2b5dba28961c0842fc15df1afdca49eeb20613df05b31c1bd4a16491f7f9c25b", 3179471,
    ),
    "docs/evidence/candidate-current-overview-v72.svg": (
        "eb2708426467a85a6d7ee592c4dde21fc08b57f8a17822a0b60732f44f22e804", 4734,
    ),
    VARIANT_PATH: (VARIANT_SHA256, 68530),
}
GRAPH_PATHS = (
    "tools/render_candidate_current_overview_v72.py",
    "docs/evidence/candidate-current-overview-v72.inputs.json",
    "docs/evidence/candidate-current-overview-v72.json",
    "docs/evidence/candidate-current-overview-v72.svg",
)


class GateError(Exception):
    """Reject substituted source, candidate execution, or guessed correctness."""


def require(condition: Any, reason: str) -> None:
    if condition is not True:
        raise GateError(reason)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact independently bounded source bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "reject invalid caller-pinned " + label,
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
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError) as error:
        raise GateError("require complete finite canonical evidence") from error


def strict_document(raw: bytes, label: str) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            require(type(key) is str and key not in result,
                    "reject duplicate " + label + " field")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw, object_pairs_hook=unique,
            parse_constant=lambda _value: (_ for _ in ()).throw(
                GateError("reject nonfinite " + label)
            ),
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise GateError("reject malformed complete " + label) from error
    require(type(value) is dict, "require an object for " + label)
    require(canonical(value) == raw, "require canonical complete " + label)
    return value


def safe_parts(relative: str) -> tuple[str, ...]:
    require(type(relative) is str and relative != "",
            "require one relative source-only owner")
    parts = tuple(relative.split("/"))
    require(
        not relative.startswith("/")
        and all(part not in ("", ".", "..") for part in parts)
        and not relative.endswith((".gz", ".so", ".pyc", ".zip", ".tar"))
        and all(part not in ("performance", "benchmarks", "holdout", ".git")
                for part in parts),
        "reject archive, native, benchmark, holdout, or unsafe source owner",
    )
    return parts


def read_owned(
    relative: str, expected_sha256: str, expected_bytes: int,
) -> tuple[bytes, dict[str, Any]]:
    require(
        type(expected_bytes) is int and 0 < expected_bytes <= MAX_OWNER_BYTES,
        "reject missing or oversized source-only owner " + relative,
    )
    parts = safe_parts(relative)
    descriptor: int | None = None
    directory = os.open(str(ROOT), os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for part in parts[:-1]:
            following = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                dir_fd=directory,
            )
            os.close(directory)
            directory = following
        descriptor = os.open(
            parts[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
            dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_size == expected_bytes
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) in (0o600, 0o644, 0o755),
            "reject changed or linked source-only owner " + relative,
        )
        pieces: list[bytes] = []
        remaining = expected_bytes
        while remaining:
            block = os.read(descriptor, min(65536, remaining))
            require(bool(block), "reject truncated source-only owner " + relative)
            pieces.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject hidden source-only suffix " + relative)
        content = b"".join(pieces)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns)
            and digest(content) == checked_digest(expected_sha256, relative),
            "reject substituted or changing source-only owner " + relative,
        )
        return content, {
            "path": relative,
            "sha256": expected_sha256,
            "bytes": expected_bytes,
            "device": before.st_dev,
            "inode": before.st_ino,
            "mode": format(stat.S_IMODE(before.st_mode), "04o"),
            "nlink": before.st_nlink,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def count_phrase_captures(value: str | bytes) -> int:
    require(type(value) in (str, bytes), "reject changed Scanner phrase type")
    phrase = value.decode("latin1") if type(value) is bytes else value
    count = 0
    offset = 0
    in_class = False
    while offset < len(phrase):
        current = phrase[offset]
        if current == "\\":
            offset += 2
            continue
        if in_class:
            if current == "]":
                in_class = False
            offset += 1
            continue
        if current == "[":
            in_class = True
            offset += 1
            continue
        if current != "(":
            offset += 1
            continue
        if phrase.startswith("(?#", offset):
            close = phrase.find(")", offset + 3)
            offset = len(phrase) if close == -1 else close + 1
            continue
        if phrase.startswith("(?P<", offset):
            count += 1
        elif not phrase.startswith("(?", offset):
            count += 1
        offset += 1
    return count


def extract_matrix(raw: bytes) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(raw, filename="frozen original Scanner matrix", mode="exec")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise GateError("reject malformed frozen original Scanner source") from error
    wanted_constants = {
        "PUBLISHED_SEED", "VARIANTS_PER_FAMILY", "FAMILIES", "IGNORECASE",
        "LOCALE", "MULTILINE", "DOTALL", "UNICODE", "VERBOSE", "ASCII",
    }
    wanted_functions = {
        "require", "encode_subject", "encode_phrase", "_typed_phrase", "build_matrix",
    }
    nodes: list[ast.stmt] = []
    found_constants: set[str] = set()
    found_functions: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [item.id for item in node.targets if isinstance(item, ast.Name)]
            if len(names) == 1 and names[0] in wanted_constants:
                require(names[0] not in found_constants,
                        "reject duplicate pure original matrix constant")
                try:
                    ast.literal_eval(node.value)
                except (ValueError, TypeError, RecursionError) as error:
                    raise GateError("reject nonliteral original Scanner constant") from error
                found_constants.add(names[0])
                nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in wanted_functions:
            require(node.name not in found_functions,
                    "reject duplicate pure original Scanner builder")
            found_functions.add(node.name)
            nodes.append(node)
    require(found_constants == wanted_constants
            and found_functions == wanted_functions,
            "preserve all independently frozen pure Scanner-builder dependencies")
    namespace: dict[str, Any] = {
        "__builtins__": builtins.__dict__,
        "random": random,
        "ScannerOracleError": GateError,
    }
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(
        compile(
            module, "<frozen-source-only-scanner-matrix>", "exec",
            flags=__future__.annotations.compiler_flag, dont_inherit=True,
        ),
        namespace,
    )
    matrix = namespace["build_matrix"]()
    require(
        type(matrix) is list and len(matrix) == 1024
        and len(namespace["FAMILIES"]) == 32
        and namespace["VARIANTS_PER_FAMILY"] == 32
        and digest(canonical(matrix)) == MATRIX_SHA256,
        "reject incomplete or changed original 1,024-case Scanner matrix",
    )
    return matrix


def matrix_witness(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    require(type(matrix) is list and len(matrix) == 1024
            and digest(canonical(matrix)) == MATRIX_SHA256,
            "reject changed, omitted, or reordered Scanner matrix")
    histogram: collections.Counter[str] = collections.Counter()
    ids: list[str] = []
    for index, row in enumerate(matrix):
        require(
            type(row) is dict
            and row.get("case") == "scanner-differential.v1." + format(index, "04d")
            and type(row.get("family")) is str
            and type(row.get("variant")) is int
            and type(row.get("lexicon")) is list,
            "reject substituted original Scanner stimulus",
        )
        captures: list[int] = []
        for entry in row["lexicon"]:
            require(type(entry) is dict and type(entry.get("phrase")) is dict,
                    "reject substituted original Scanner lexicon")
            encoded = entry["phrase"]
            if encoded.get("type") == "str":
                require(set(encoded) == {"type", "value"}
                        and type(encoded.get("value")) is str,
                        "preserve exact original text Scanner phrase")
                phrase = encoded["value"]
            else:
                require(set(encoded) == {"type", "hex"}
                        and encoded.get("type") == "bytes"
                        and type(encoded.get("hex")) is str,
                        "preserve exact original bytes Scanner phrase")
                try:
                    phrase = bytes.fromhex(encoded["hex"])
                except ValueError as error:
                    raise GateError("reject noncanonical bytes Scanner phrase") from error
                require(phrase.hex() == encoded["hex"],
                        "reject changed original bytes Scanner phrase")
            captures.append(count_phrase_captures(phrase))
        if any(count > len(row["lexicon"]) for count in captures):
            histogram[row["family"]] += 1
            ids.append(row["case"])
    require(
        dict(histogram) == EXPECTED_HISTOGRAM
        and len(ids) == 64 and len(set(ids)) == 64
        and ids[0] == "scanner-differential.v1.0160"
        and ids[-1] == "scanner-differential.v1.0254"
        and digest(canonical(ids)) == OVERFLOW_SHA256,
        "require all 64 authentic nested, numbered, and named overflow witnesses",
    )
    return {
        "matrix_sha256": MATRIX_SHA256,
        "matrix_case_count": 1024,
        "family_count": 32,
        "variants_per_family": 32,
        "overflow_case_count": 64,
        "overflow_family_case_counts": dict(histogram),
        "first_overflow_case": ids[0],
        "last_overflow_case": ids[-1],
        "overflow_case_ids_sha256": OVERFLOW_SHA256,
        "preserved_nonoverflow_case_count": 960,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "native_activations": 0,
    }


def derive_variant(original: bytes) -> bytes:
    expected = OWNERS["candidates/zig_candidate.py"]
    require(len(original) == expected[1] and digest(original) == expected[0],
            "derive only from the unchanged complete first-party Zig adapter")
    require(original.count(ORIGINAL_BLOCK) == 1
            and original.count(CORRECTED_BLOCK) == 0,
            "require one exact unapplied owned Scanner-construction correction")
    scanner = original.index(b"\nclass Scanner:\n")
    scanner_end = original.index(b"\n    def scan(self, string):\n", scanner)
    changed_at = original.index(ORIGINAL_BLOCK)
    require(scanner < changed_at < scanner_end,
            "restrict the correction to the owned Scanner constructor")
    corrected = original.replace(ORIGINAL_BLOCK, CORRECTED_BLOCK, 1)
    require(
        len(corrected) == 68530
        and digest(corrected) == VARIANT_SHA256
        and corrected.count(CORRECTED_BLOCK) == 1
        and corrected.count(ORIGINAL_BLOCK) == 0
        and corrected.replace(CORRECTED_BLOCK, ORIGINAL_BLOCK, 1) == original,
        "reject any change outside the exact first-party Scanner correction",
    )
    try:
        ast.parse(corrected, filename=VARIANT_PATH, mode="exec")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise GateError("reject malformed complete first-party Zig variant") from error
    return corrected


def validate_p0(value: dict[str, Any]) -> None:
    denominator = value.get("denominator")
    suites = value.get("suites")
    require(
        value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and type(denominator) is dict
        and denominator.get("final_required_case_execution_denominator") == 31237
        and denominator.get("available_frozen_vector_case_executions") == 31237
        and denominator.get("private_upstream_methods_outside_public_denominator") == 13
        and type(suites) is list
        and tuple((row.get("id"), row.get("case_execution_count"))
                  for row in suites) == SUITE_CASES
        and sum(count for _, count in SUITE_CASES) == 31237
        and value.get("phase_gate", {}).get("status") == "PASS",
        "preserve all 31,237 original cases, 13 ordered suites, and 13 waivers",
    )


def validate_readiness(value: dict[str, Any]) -> None:
    phase = value.get("phase_gate")
    candidate = value.get("candidate_qualification_gate")
    supplemental = value.get("actual_supplemental_two_reference")
    require(
        value.get("schema") == "rebar-cpython-re-p0-completeness-v4"
        and value.get("version") == 4 and value.get("status") == "PASS"
        and value.get("original_case_execution_denominator") == 31237
        and value.get("original_suite_count") == 13
        and value.get("original_named_private_waiver_count") == 13
        and value.get("original_obligation_count") == 73
        and value.get("original_crosswalk_count") == 34
        and value.get("first_party_candidate_family_count") == 6
        and type(phase) is dict
        and phase.get("status") == "PASS"
        and phase.get("status_scope") == "PHASE 1 PYTHON-ORACLE READINESS ONLY"
        and phase.get("candidate_evaluation_authorized") is True
        and phase.get("final_holdout_authorized") is False
        and phase.get("performance_oracle_authorized") is False
        and phase.get("qualified_candidate_count") == 0
        and type(candidate) is dict
        and candidate.get("status") == "BLOCKED"
        and candidate.get("qualified_candidate_count") == 0
        and candidate.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and type(supplemental) is dict
        and supplemental.get("actual_reference_worker_count") == 2
        and supplemental.get("actual_reference_worker_process_ids") == [81, 82]
        and supplemental.get("case_count_per_worker") == [8244, 8244]
        and supplemental.get("failed_per_worker") == [0, 0]
        and supplemental.get("case_denominator_included_in_original_31237") is False
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("qualified_candidate_count") == 0
        and value.get("winner_selected") is False,
        "require actual passing phase-one V4 readiness without candidate qualification",
    )


def validate_supplement(value: dict[str, Any]) -> None:
    require(
        value.get("schema") == "rebar-owned-differential-fuzz-reference-v3-actual-reference"
        and value.get("status") == "PASS"
        and value.get("actual_reference_worker_count") == 2
        and value.get("actual_reference_worker_process_ids") == [81, 82]
        and value.get("actual_candidate_worker_count") == 0
        and value.get("candidate_status") == "NOT RUN"
        and value.get("candidate_qualified") is False
        and value.get("case_denominator_included_in_original_31237") is False
        and value.get("original_case_execution_denominator") == 31237
        and value.get("supplemental_case_count") == 8244
        and value.get("mapped_obligation_count") == 45
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("qualified_candidate_count") == 0
        and value.get("winner_selected") is False,
        "preserve all 8,244 independently referenced supplemental checks separately",
    )


def validate_previous_zig(value: dict[str, Any]) -> None:
    require(
        value.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v3-durable-publication-receipt"
        and value.get("status") == "PASS"
        and value.get("publication_status") == "PASS"
        and value.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and value.get("family") == "zig"
        and value.get("candidate_status") == "FAIL"
        and value.get("candidate_qualified") is False
        and value.get("case_execution_denominator") == 31237
        and value.get("suite_count") == 13
        and value.get("completed_suite_count") == 13
        and value.get("actual_candidate_workers") == 13
        and value.get("semantic_mismatch_count") == 1764
        and value.get("verified_passing_case_count") == 3711
        and value.get("infrastructure_failure_count") == 0
        and value.get("named_private_waiver_count") == 13
        and value.get("native_engine_sha256")
        == "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071"
        and value.get("native_bridge_sha256")
        == "e5809566a166f469e7f95fc1a43e814a3beeeffa2a6e848c00a3a48215ee6726"
        and value.get("canonical_corrected_bridge_source_sha256")
        == OWNERS["candidates/zig/py_bridge.c"][0]
        and value.get("all_original_native_targets_restored") is True
        and value.get("restoration_verified_before_publication") is True
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("timing_trials_run") == 0
        and value.get("hidden_cases_read") == 0
        and value.get("winner_selected") is False,
        "retain genuine complete Zig failure; publication PASS is not compatibility",
    )


def validate_previous_feature(value: dict[str, Any]) -> None:
    repair = value.get("construction_repair")
    matrix = repair.get("complete_original_scanner_matrix") if type(repair) is dict else None
    require(
        value.get("schema") == "rebar-owned-zig-scanner-phrase-source-repair-v3"
        and value.get("version") == 3
        and value.get("status") == "SOURCE FROZEN; CORRECTED CANDIDATE NOT RUN"
        and type(repair) is dict
        and repair.get("function") == "candidates.zig_candidate.Scanner.__init__"
        and repair.get("error_type") == "RuntimeError"
        and repair.get("error_message") == "invalid SRE code"
        and repair.get("corrected_candidate_matching") == "NOT RUN"
        and repair.get("corrected_private_adapter", {}).get("sha256") == VARIANT_SHA256
        and repair.get("corrected_private_adapter", {}).get("bytes") == 68530
        and repair.get("corrected_private_adapter", {}).get("materialized") is False
        and type(matrix) is dict
        and matrix.get("matrix_sha256") == MATRIX_SHA256
        and matrix.get("matrix_case_count") == 1024
        and matrix.get("overflow_case_count") == 64
        and matrix.get("overflow_case_ids_sha256") == OVERFLOW_SHA256
        and matrix.get("overflow_family_case_counts") == EXPECTED_HISTOGRAM
        and matrix.get("preserved_nonoverflow_case_count") == 960
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("winner_selected") is False,
        "preserve the authentic historical, unmaterialized scanner source experiment",
    )


def validate_graph(value: dict[str, Any], *, input_graph: bool = False) -> None:
    require(
        value.get("version") == GRAPH_VERSION
        and value.get("phase1_v4_oracle_readiness_status") == "PASS"
        and value.get("phase1_v4_candidate_testing_authorized") is True
        and value.get("first_party_source_inventory_family_count") == 6
        and value.get("qualified_candidate_count") == 0
        and value.get("zig_original_campaign_status") == "FAIL"
        and value.get("zig_original_campaign_semantic_mismatch_count") == 1764
        and value.get("rust_native_build_v19_status") == "PASS"
        and value.get("rust_native_build_v19_actual_compiler_process_count") == 28
        and value.get("rust_native_build_v19_compiler_process_count") == 28
        and value.get("rust_native_build_v19_planned_compiler_process_count") == 28
        and value.get("rust_native_build_v19_independent_phase_count") == 2
        and value.get("rust_native_build_v19_private_root_provenance") == "PASS"
        and value.get("rust_native_build_v19_matching_status") == "NOT RUN"
        and value.get("rust_native_build_v19_candidate_correctness") == "NOT MEASURED"
        and value.get("rust_native_build_v19_candidate_qualified") is False
        and value.get("rust_v11_original_campaign_execution_status")
        == "BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT"
        and value.get("rust_v11_original_campaign_matching_status") == "NOT RUN"
        and value.get("rust_v11_original_campaign_actual_worker_count") == 0
        and value.get("rust_v11_original_campaign_private_root_provenance")
        == "NOT ESTABLISHED"
        and value.get("rust_original_campaign_status") == "FAIL"
        and value.get("rust_original_campaign_semantic_mismatch_count") == 1440
        and value.get("rust_original_campaign_verified_passing_case_count") == 14853
        and value.get("c_native_build_v16_status") == "PASS"
        and value.get("c_native_build_v16_compiler_process_count") == 14
        and value.get("c_native_build_v16_expected_compiler_process_count") == 14
        and value.get("c_native_build_v16_matching_status") == "NOT RUN"
        and value.get("c_native_build_v16_activation_status") == "NOT RUN"
        and value.get("c_native_build_v16_candidate_workers_started") == 0
        and value.get("c_native_build_v16_candidate_correctness") == "NOT MEASURED"
        and value.get("c_native_build_v16_candidate_qualified") is False
        and value.get("c_original_campaign_status") == "FAIL"
        and value.get("c_original_campaign_semantic_mismatch_count") == 1230
        and value.get("c_original_campaign_verified_passing_case_count") == 7325
        and value.get("actual_c_v4_original_campaign_status") == "FAIL"
        and value.get("actual_c_v4_original_campaign_semantic_mismatch_count") == 1230
        and value.get("actual_c_v4_original_campaign_verified_passing_case_count") == 7325
        and value.get("final_holdout_opened") is False
        and value.get("performance") == "NOT MEASURED",
        "require the exact genuine current V72 graph and preserve every candidate result",
    )
    if not input_graph:
        require(
            value.get("authenticated_evidence_owner_lower_bound") == EVIDENCE_LOWER_BOUND
            and value.get("authenticated_history_reference_lower_bound") == HISTORY_LOWER_BOUND
            and value.get("phase1_differential_fuzz_reference_v3_reference_case_count") == 8244
            and value.get("phase1_differential_fuzz_reference_v3_execution_status") == "PASS"
            and value.get("phase1_differential_fuzz_reference_v3_actual_worker_case_counts")
            == [8244, 8244]
            and value.get("phase1_differential_fuzz_reference_v3_actual_worker_failure_counts")
            == [0, 0]
            and value.get("zig_original_campaign_verified_passing_case_count") == 3711
            and value.get("zig_original_campaign_candidate_worker_count") == 13
            and value.get("zig_original_campaign_case_execution_denominator") == 31237
            and value.get("zig_original_campaign_completed_suite_count") == 13
            and value.get("zig_original_campaign_private_waiver_count") == 13
            and value.get("runtime_no_delegation") == "NOT ESTABLISHED"
            and value.get("winner_selected") is False,
            "reject stale graph, forged current lower bounds, or invented Zig result",
        )


class SourceOnlyBoundary:
    """Physically deny source-only candidate, archive, clock, and native effects."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = 0
        self.counts = {
            kind: 0 for kind in (
                "filesystem", "write", "process", "import", "native",
                "network", "thread", "clock", "decompression", "lock", "signal",
            )
        }

    def deny(self, name: str, kind: str) -> Any:
        def reject(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked += 1
            self.counts[kind] += 1
            raise GateError("blocked source-only external effect: " + name)
        return reject

    def __enter__(self) -> SourceOnlyBoundary:
        targets: list[tuple[Any, tuple[str, ...], str]] = [
            (builtins, ("open", "__import__"), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir", "listdir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat", "iterdir"),
             "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove", "rename",
                  "replace", "fsync", "symlink", "link"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink", "rename",
                    "replace", "touch"), "write"),
            (tempfile, ("mkdtemp", "mkstemp", "TemporaryFile",
                        "NamedTemporaryFile"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call",
                          "check_output", "_fork_exec"), "process"),
            (os, ("fork", "system", "posix_spawn", "posix_spawnp",
                  "execv", "execve", "execl", "execle", "execvp",
                  "spawnv", "spawnve", "spawnvp", "spawnvpe"), "process"),
            (importlib, ("import_module",), "import"),
            (importlib.machinery.SourceFileLoader,
             ("create_module", "exec_module", "load_module"), "import"),
            (importlib.machinery.ExtensionFileLoader,
             ("create_module", "exec_module", "load_module"), "native"),
            (ctypes, ("CDLL", "PyDLL", "_dlopen"), "native"),
            (socket, ("socket", "create_connection", "getaddrinfo"), "network"),
            (threading, ("_start_joinable_thread", "_start_new_thread"), "thread"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "thread_time"), "clock"),
            (gzip, ("open", "decompress", "GzipFile"), "decompression"),
            (zlib, ("decompress", "decompressobj"), "decompression"),
            (fcntl, ("flock", "lockf"), "lock"),
            (signal, ("signal", "pthread_sigmask", "raise_signal"), "signal"),
        ]
        native_modules = (
            ("_io", ("open",), "filesystem"),
            ("posix", ("open", "read", "stat", "lstat", "scandir", "listdir"),
             "filesystem"),
            ("posix", ("write", "mkdir", "unlink", "remove", "rename", "replace",
                       "fsync", "symlink", "link"), "write"),
            ("posix", ("fork", "posix_spawn", "posix_spawnp", "execv", "execve"),
             "process"),
            ("_posixsubprocess", ("fork_exec",), "process"),
            ("_ctypes", ("dlopen",), "native"),
            ("_imp", ("create_dynamic", "exec_dynamic", "create_builtin",
                      "exec_builtin", "init_frozen"), "native"),
            ("_socket", ("socket", "getaddrinfo"), "network"),
            ("_thread", ("start_new_thread", "start_joinable_thread"), "thread"),
        )
        for module_name, names, kind in native_modules:
            module = sys.modules.get(module_name)
            if module is not None:
                targets.append((module, names, kind))
        seen: set[tuple[int, str]] = set()
        for owner, names, kind in targets:
            for name in names:
                if hasattr(owner, name) and (id(owner), name) not in seen:
                    seen.add((id(owner), name))
                    original = getattr(owner, name)
                    self.saved.append((owner, name, original))
                    setattr(owner, name, self.deny(name, kind))
        return self

    def __exit__(self, *_error: Any) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def graph_options(options: argparse.Namespace) -> None:
    actual = (
        options.graph_source_sha256,
        options.graph_inputs_sha256,
        options.graph_summary_sha256,
        options.graph_svg_sha256,
    )
    expected = tuple(OWNERS[path][0] for path in GRAPH_PATHS)
    require(
        tuple(checked_digest(value, "current graph owner") for value in actual)
        == expected,
        "independently caller-pin all four actually pushed V72 graph owners",
    )


def load_context(options: argparse.Namespace) -> dict[str, Any]:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PYTHON,
        "use only pinned isolated CPython 3.14.6 for source verification",
    )
    graph_options(options)
    source_size = os.stat(ROOT / SOURCE_PATH, follow_symlinks=False).st_size
    source, source_owner = read_owned(
        SOURCE_PATH, checked_digest(options.source_sha256, "V4 verifier source"),
        source_size,
    )
    protocol_size = os.stat(ROOT / PROTOCOL_PATH, follow_symlinks=False).st_size
    protocol, protocol_owner = read_owned(
        PROTOCOL_PATH, checked_digest(options.protocol_sha256, "V4 protocol"),
        protocol_size,
    )
    loaded: dict[str, bytes] = {}
    owners: dict[str, dict[str, Any]] = {}
    for relative, (fingerprint, size) in OWNERS.items():
        content, owner = read_owned(relative, fingerprint, size)
        loaded[relative] = content
        owners[relative] = owner
    validate_p0(strict_document(
        loaded["oracle/phase1/p0-completeness-v1.json"], "original P0",
    ))
    readiness = strict_document(
        loaded["oracle/phase1/p0-completeness-v4.json"], "P0 V4 readiness",
    )
    validate_readiness(readiness)
    supplement_path = next(
        path for path in OWNERS if path.endswith("two-independent-reference-result.json")
    )
    validate_supplement(strict_document(loaded[supplement_path],
                                        "actual two-reference supplement"))
    receipt_path = next(
        path for path in OWNERS if path.endswith(
            "zig-scanner-v2-original-p0-failures-publication-receipt.json"
        )
    )
    validate_previous_zig(strict_document(loaded[receipt_path],
                                         "actual small Zig failure receipt"))
    validate_previous_feature(strict_document(
        loaded["oracle/phase2/zig-scanner-phrase-source-repair-v3.json"],
        "historical unmaterialized Scanner repair",
    ))
    validate_graph(strict_document(
        loaded["docs/evidence/candidate-current-overview-v72.inputs.json"],
        "pushed V72 graph inputs",
    ), input_graph=True)
    graph = strict_document(
        loaded["docs/evidence/candidate-current-overview-v72.json"],
        "pushed V72 graph summary",
    )
    validate_graph(graph)
    producer = strict_document(
        loaded["oracle/phase2/six-family-p0-producer-v4.json"],
        "corrected six-family original producer",
    )
    require(
        producer.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v4-source-freeze"
        and producer.get("version") == 4
        and producer.get("case_execution_denominator") == 31237
        and producer.get("suite_count") == 13
        and producer.get("status")
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        "preserve the exact corrected six-family original-case producer",
    )
    corrected = derive_variant(loaded["candidates/zig_candidate.py"])
    require(
        loaded[VARIANT_PATH] == corrected
        and loaded[VARIANT_PATH].replace(CORRECTED_BLOCK, ORIGINAL_BLOCK, 1)
        == loaded["candidates/zig_candidate.py"],
        "authenticate the complete independently owned materialized V4 variant",
    )
    require(b"from candidates import _zig_bridge\n" in corrected,
            "preserve the independently owned Zig CPython bridge")
    return {
        "source": source,
        "source_owner": source_owner,
        "protocol": protocol,
        "protocol_owner": protocol_owner,
        "loaded": loaded,
        "owners": owners,
        "graph": graph,
        "readiness": readiness,
        "corrected": corrected,
    }


def contract_document(context: dict[str, Any],
                      witness: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "SOURCE FROZEN; FIRST-PARTY ZIG VARIANT NOT BUILT OR TESTED",
        "phase": "PHASE 2 FIRST-PARTY ZIG SOURCE FEATURE",
        "source": context["source_owner"],
        "protocol": context["protocol_owner"],
        "original_oracle": {
            "phase1_readiness_status": "PASS",
            "original_case_execution_denominator": 31237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "mapped_obligation_count": 73,
            "crosswalk_count": 34,
            "candidate_family_count": 6,
            "additional_independently_referenced_case_count": 8244,
            "additional_reference_worker_count": 2,
            "additional_candidate_case_count": 0,
            "additional_cases_included_in_original_denominator": False,
        },
        "current_graph": {
            "version": GRAPH_VERSION,
            "owners": [context["owners"][path] for path in GRAPH_PATHS],
            "authenticated_evidence_owner_lower_bound": EVIDENCE_LOWER_BOUND,
            "authenticated_history_reference_lower_bound": HISTORY_LOWER_BOUND,
            "lower_bounds_are_whole_repository_census": False,
            "source_freeze_new_evidence_owner_count": 0,
        },
        "previous_actual_zig_matching": {
            "status": "FAIL",
            "semantic_mismatch_count": 1764,
            "verified_passing_case_count": 3711,
            "infrastructure_failure_count": 0,
            "actual_candidate_worker_count": 13,
            "completed_suite_count": 13,
            "case_execution_denominator": 31237,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "receipt": context["owners"][next(
                path for path in OWNERS if path.endswith(
                    "zig-scanner-v2-original-p0-failures-publication-receipt.json"
                )
            )],
            "matching_archive_read": False,
            "per_suite_mismatches_inferred": False,
        },
        "preserved_current_graph_history": {
            "rust_v19_native_build": {
                "status": context["graph"]["rust_native_build_v19_status"],
                "actual_compiler_process_count": context["graph"][
                    "rust_native_build_v19_actual_compiler_process_count"
                ],
                "independent_phase_count": context["graph"][
                    "rust_native_build_v19_independent_phase_count"
                ],
                "private_root_provenance": context["graph"][
                    "rust_native_build_v19_private_root_provenance"
                ],
                "matching_status": context["graph"][
                    "rust_native_build_v19_matching_status"
                ],
                "candidate_correctness": context["graph"][
                    "rust_native_build_v19_candidate_correctness"
                ],
                "candidate_qualified": context["graph"][
                    "rust_native_build_v19_candidate_qualified"
                ],
            },
            "rust_v11_original_campaign": {
                "execution_status": context["graph"][
                    "rust_v11_original_campaign_execution_status"
                ],
                "matching_status": context["graph"][
                    "rust_v11_original_campaign_matching_status"
                ],
                "actual_worker_count": context["graph"][
                    "rust_v11_original_campaign_actual_worker_count"
                ],
                "private_root_provenance": context["graph"][
                    "rust_v11_original_campaign_private_root_provenance"
                ],
            },
            "rust_original_matching": {
                "status": context["graph"]["rust_original_campaign_status"],
                "semantic_mismatch_count": context["graph"][
                    "rust_original_campaign_semantic_mismatch_count"
                ],
                "verified_passing_case_count": context["graph"][
                    "rust_original_campaign_verified_passing_case_count"
                ],
            },
            "c_v16_native_build": {
                "status": context["graph"]["c_native_build_v16_status"],
                "compiler_process_count": context["graph"][
                    "c_native_build_v16_compiler_process_count"
                ],
                "matching_status": context["graph"][
                    "c_native_build_v16_matching_status"
                ],
                "activation_status": context["graph"][
                    "c_native_build_v16_activation_status"
                ],
                "candidate_workers_started": context["graph"][
                    "c_native_build_v16_candidate_workers_started"
                ],
                "candidate_correctness": context["graph"][
                    "c_native_build_v16_candidate_correctness"
                ],
                "candidate_qualified": context["graph"][
                    "c_native_build_v16_candidate_qualified"
                ],
            },
            "c_original_matching": {
                "status": context["graph"]["c_original_campaign_status"],
                "semantic_mismatch_count": context["graph"][
                    "c_original_campaign_semantic_mismatch_count"
                ],
                "verified_passing_case_count": context["graph"][
                    "c_original_campaign_verified_passing_case_count"
                ],
            },
        },
        "first_party_source_feature": {
            "family": "zig",
            "semantic_owner_count": 1,
            "new_independent_candidate_family_count": 0,
            "canonical_adapter": context["owners"]["candidates/zig_candidate.py"],
            "independent_engine": context["owners"]["candidates/zig/mini_regex.zig"],
            "independent_cpython_bridge": context["owners"]["candidates/zig/py_bridge.c"],
            "complete_materialized_variant": context["owners"][VARIANT_PATH],
            "variant_materialized": True,
            "outside_feature_block_unchanged": True,
            "original_block": {
                "bytes": len(ORIGINAL_BLOCK),
                "sha256": digest(ORIGINAL_BLOCK),
                "occurrence_count": 1,
            },
            "corrected_block": {
                "bytes": len(CORRECTED_BLOCK),
                "sha256": digest(CORRECTED_BLOCK),
                "occurrence_count": 1,
            },
            "function": "candidates.zig_candidate.Scanner.__init__",
            "error_type": "RuntimeError",
            "error_message": "invalid SRE code",
            "capture_check_occurs_before_native_compile": True,
            "empty_lexicon_error_preserved": True,
            "original_canonical_adapter_modified": False,
            "original_engine_modified": False,
            "original_bridge_modified": False,
            "duplicate_loader_repair_included": False,
            "scanner_matrix": witness,
            "unrepaired_verbose_scanner_mismatches": 620,
            "corrected_candidate_build": "NOT RUN",
            "corrected_candidate_matching": "NOT RUN",
            "corrected_candidate_qualified": False,
        },
        "from_scratch_policy": {
            "stdlib_re_engine": "FORBIDDEN",
            "stdlib_sre_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "another_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "hardcoded_oracle_answers": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "source_only_effects": {
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "reference_workers_started": 0,
            "native_libraries_loaded": 0,
            "native_activations": 0,
            "compiler_processes_started": 0,
            "native_builds_started": 0,
            "matching_archives_opened": 0,
            "matching_archives_inflated": 0,
            "reference_archives_opened": 0,
            "benchmark_files_opened": 0,
            "holdout_files_opened": 0,
            "clock_samples": 0,
            "files_written": 0,
        },
        "frozen_source_owners": [
            context["owners"][path] for path in OWNERS
        ],
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def hostile_controls(matrix: list[dict[str, Any]],
                     context: dict[str, Any]) -> int:
    rejected = 0

    def reject(action: Any, label: str) -> None:
        nonlocal rejected
        try:
            action()
        except (GateError, TypeError, ValueError, OSError,
                SyntaxError, RecursionError):
            rejected += 1
        else:
            raise GateError("accepted hostile source-only control: " + label)

    reject(lambda: matrix_witness(matrix[:-1]), "dropped original scanner case")
    reject(lambda: matrix_witness(matrix + [matrix[0]]),
           "duplicated original scanner case")
    for index in range(0, len(matrix), 8):
        changed = list(matrix)
        changed[index] = dict(
            changed[index],
            case="scanner-differential.v1." + format((index + 1) % len(matrix), "04d"),
        )
        reject(lambda rows=changed: matrix_witness(rows),
               "substituted original scanner case " + format(index, "04d"))
    original = context["loaded"]["candidates/zig_candidate.py"]
    variant = context["loaded"][VARIANT_PATH]
    for forged in (b"", original[:-1], variant, ORIGINAL_BLOCK,
                   original.replace(ORIGINAL_BLOCK, ORIGINAL_BLOCK + b" ", 1)):
        reject(lambda value=forged: derive_variant(value),
               "forged immutable first-party scanner adapter")
    for phrase, expected in (
        (r"((a)(b(c)?))", 4),
        (r"(a)(b)(c)?", 3),
        (r"(?P<first>a)(?P<second>b)(?P<third>c)?", 3),
        (r"(?:a)(?=b)(?!c)", 0),
        (r"\(a\)", 0),
        (r"[(](a)[)]", 1),
        (r"(?#hidden (a))(b)", 1),
        (r"(?P=word)", 0),
        (b"(a)(b)", 2),
    ):
        require(count_phrase_captures(phrase) == expected,
                "retain exact original Scanner capture semantics")
    receipt_path = next(
        path for path in OWNERS if path.endswith(
            "zig-scanner-v2-original-p0-failures-publication-receipt.json"
        )
    )
    receipt = strict_document(context["loaded"][receipt_path],
                              "authentic actual small Zig receipt")
    for key, value in (
        ("candidate_status", "PASS"),
        ("semantic_mismatch_count", 1700),
        ("verified_passing_case_count", 29473),
        ("suite_count", 12),
        ("completed_suite_count", 12),
        ("actual_candidate_workers", 12),
        ("infrastructure_failure_count", 1),
        ("case_execution_denominator", 31301),
        ("named_private_waiver_count", 14),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("winner_selected", True),
    ):
        reject(lambda k=key, v=value: validate_previous_zig(dict(receipt, **{k: v})),
               "forged actual Zig matching field " + key)
    readiness = context["readiness"]
    for key, value in (
        ("status", "FAIL"),
        ("version", 3),
        ("original_case_execution_denominator", 31236),
        ("original_suite_count", 12),
        ("original_named_private_waiver_count", 14),
        ("original_obligation_count", 72),
        ("first_party_candidate_family_count", 5),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("qualified_candidate_count", 1),
        ("winner_selected", True),
    ):
        reject(lambda k=key, v=value: validate_readiness(dict(readiness, **{k: v})),
               "forged passing P0 V4 readiness " + key)
    graph = context["graph"]
    for key, value in (
        ("version", 71),
        ("phase1_v4_oracle_readiness_status", "FAIL"),
        ("phase1_v4_candidate_testing_authorized", False),
        ("first_party_source_inventory_family_count", 5),
        ("qualified_candidate_count", 1),
        ("zig_original_campaign_status", "PASS"),
        ("zig_original_campaign_semantic_mismatch_count", 0),
        ("zig_original_campaign_verified_passing_case_count", 31237),
        ("zig_original_campaign_candidate_worker_count", 12),
        ("zig_original_campaign_case_execution_denominator", 31301),
        ("zig_original_campaign_completed_suite_count", 12),
        ("zig_original_campaign_private_waiver_count", 14),
        ("rust_native_build_v19_status", "FAIL"),
        ("rust_native_build_v19_actual_compiler_process_count", 27),
        ("rust_native_build_v19_compiler_process_count", 27),
        ("rust_native_build_v19_planned_compiler_process_count", 27),
        ("rust_native_build_v19_independent_phase_count", 1),
        ("rust_native_build_v19_private_root_provenance", "NOT ESTABLISHED"),
        ("rust_native_build_v19_matching_status", "PASS"),
        ("rust_native_build_v19_candidate_correctness", "PASS"),
        ("rust_native_build_v19_candidate_qualified", True),
        ("rust_v11_original_campaign_execution_status", "PASS"),
        ("rust_v11_original_campaign_matching_status", "PASS"),
        ("rust_v11_original_campaign_actual_worker_count", 1),
        ("rust_v11_original_campaign_private_root_provenance", "PASS"),
        ("rust_original_campaign_status", "PASS"),
        ("rust_original_campaign_semantic_mismatch_count", 0),
        ("rust_original_campaign_verified_passing_case_count", 31237),
        ("c_native_build_v16_status", "FAIL"),
        ("c_native_build_v16_compiler_process_count", 13),
        ("c_native_build_v16_expected_compiler_process_count", 13),
        ("c_native_build_v16_matching_status", "PASS"),
        ("c_native_build_v16_activation_status", "PASS"),
        ("c_native_build_v16_candidate_workers_started", 1),
        ("c_native_build_v16_candidate_correctness", "PASS"),
        ("c_native_build_v16_candidate_qualified", True),
        ("c_original_campaign_status", "PASS"),
        ("c_original_campaign_semantic_mismatch_count", 0),
        ("c_original_campaign_verified_passing_case_count", 31237),
        ("actual_c_v4_original_campaign_status", "PASS"),
        ("actual_c_v4_original_campaign_semantic_mismatch_count", 0),
        ("actual_c_v4_original_campaign_verified_passing_case_count", 31237),
        ("authenticated_evidence_owner_lower_bound", EVIDENCE_LOWER_BOUND - 1),
        ("authenticated_history_reference_lower_bound", HISTORY_LOWER_BOUND - 1),
        ("phase1_differential_fuzz_reference_v3_reference_case_count", 8243),
        ("final_holdout_opened", True),
        ("performance", "1.5x"),
        ("runtime_no_delegation", "ESTABLISHED"),
        ("winner_selected", True),
    ):
        reject(lambda k=key, v=value: validate_graph(dict(graph, **{k: v})),
               "forged actual V72 graph field " + key)
    supplemental_path = next(
        path for path in OWNERS if path.endswith("two-independent-reference-result.json")
    )
    supplemental = strict_document(
        context["loaded"][supplemental_path], "authentic supplemental reference",
    )
    for key, value in (
        ("status", "FAIL"),
        ("actual_reference_worker_count", 1),
        ("actual_reference_worker_process_ids", [81, 81]),
        ("actual_candidate_worker_count", 1),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("case_denominator_included_in_original_31237", True),
        ("original_case_execution_denominator", 39481),
        ("supplemental_case_count", 8243),
        ("mapped_obligation_count", 44),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("qualified_candidate_count", 1),
        ("winner_selected", True),
    ):
        reject(lambda k=key, v=value: validate_supplement(dict(supplemental, **{k: v})),
               "forged two-reference supplement " + key)
    for unsafe in (
        "", "/tmp/zig", "../GOAL.md", "oracle/../GOAL.md",
        "oracle/phase2/evidence/failure.json.gz",
        "candidates/_zig_probe.so", "performance/secret.json",
        "holdout/secret.json", ".git/config",
    ):
        reject(lambda path=unsafe: safe_parts(path),
               "unsafe source-only owner " + repr(unsafe))
    require(rejected >= 170,
            "exercise all original cases, current graph, readiness and actual failures")
    return rejected


def source_only_result(context: dict[str, Any], *,
                       run_hostile: bool) -> dict[str, Any]:
    existing = frozenset(
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
        or name in ("re", "_sre", "regex")
    )
    with SourceOnlyBoundary() as boundary:
        matrix = extract_matrix(
            context["loaded"]["tools/rust_scanner_differential_v1.py"],
        )
        witness = matrix_witness(matrix)
        before = boundary.blocked
        if run_hostile:
            probes: list[tuple[str, Any, str]] = [
                ("filesystem", lambda: builtins.open("GOAL.md"), "Python file open"),
                ("filesystem", lambda: os.open("GOAL.md", os.O_RDONLY),
                 "native source file open"),
                ("filesystem", lambda: io.open("GOAL.md"), "alternate file open"),
                ("import", lambda: importlib.import_module("candidates.zig_candidate"),
                 "candidate import"),
                ("import", lambda: importlib.import_module("re"),
                 "stdlib regular-expression import"),
                ("native", lambda: ctypes.CDLL("forbidden-regex.so"),
                 "external native matcher"),
                ("native", lambda: ctypes._dlopen("forbidden-regex.so"),
                 "direct native dynamic load"),
                ("process", lambda: subprocess.run([PYTHON]), "candidate worker"),
                ("process", lambda: os.execv("/forbidden-worker", []),
                 "native worker execution"),
                ("write", lambda: os.remove("GOAL.md"), "workspace deletion"),
                ("write", lambda: tempfile.mkdtemp(), "temporary source mutation"),
                ("network", lambda: socket.socket(), "network connection"),
                ("thread", lambda: threading.Thread().start(), "thread creation"),
                ("clock", lambda: time.perf_counter(), "performance measurement"),
                ("decompression", lambda: gzip.open("forbidden.json.gz"),
                 "compressed matching archive"),
                ("decompression", lambda: zlib.decompress(b""),
                 "compressed archive inflation"),
                ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX), "filesystem lock"),
                ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL),
                 "signal mutation"),
            ]
            for kind, action, label in probes:
                previous = boundary.counts[kind]
                try:
                    action()
                except GateError:
                    require(
                        boundary.counts[kind] == previous + 1,
                        "prove source-only wall physically blocks " + label,
                    )
                else:
                    raise GateError("source-only wall allowed " + label)
            require(all(value > 0 for value in boundary.counts.values()),
                    "exercise all independent source-only effect boundaries")
        blocked = boundary.blocked - before
        blocked_counts = dict(boundary.counts)
        require(
            frozenset(
                name for name in sys.modules
                if name == "candidates" or name.startswith("candidates.")
                or name in ("re", "_sre", "regex")
            ) == existing,
            "source-only gate imported a candidate or regex matcher",
        )
    rejected = hostile_controls(matrix, context) if run_hostile else 0
    return {
        "schema": SCHEMA + "-source-only-result",
        "version": VERSION,
        "status": "PASS",
        "mode": "SELF-TEST" if run_hostile else "FROZEN CONTEXT",
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "named_private_waiver_count": 13,
        "mapped_original_obligation_count": 73,
        "supplemental_reference_case_count": 8244,
        "supplemental_candidate_status": "NOT RUN",
        "supplemental_cases_included_in_original_denominator": False,
        "phase1_oracle_readiness_status": "PASS",
        "phase1_candidate_testing_authorized": True,
        "first_party_source_inventory_family_count": 6,
        "current_graph_version": GRAPH_VERSION,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_LOWER_BOUND,
        "authenticated_history_reference_lower_bound": HISTORY_LOWER_BOUND,
        "historical_zig_candidate_status": "FAIL",
        "historical_zig_semantic_mismatch_count": 1764,
        "historical_zig_verified_passing_case_count": 3711,
        "historical_zig_actual_worker_count": 13,
        "historical_matching_archive_opened": False,
        "scanner_matrix": witness,
        "complete_variant_materialized": True,
        "complete_variant_sha256": VARIANT_SHA256,
        "complete_variant_bytes": 68530,
        "original_adapter_modified": False,
        "original_engine_modified": False,
        "original_bridge_modified": False,
        "duplicate_loader_repair_included": False,
        "unrepaired_verbose_scanner_mismatches": 620,
        "corrected_candidate_build": "NOT RUN",
        "corrected_candidate_matching": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "hostile_controls_rejected": rejected,
        "external_effect_controls_blocked": blocked,
        "blocked_effects_by_kind": blocked_counts,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "native_activations": 0,
        "matching_archives_opened": 0,
        "matching_archives_inflated": 0,
        "reference_archives_opened": 0,
        "holdout_files_opened": 0,
        "benchmark_files_opened": 0,
        "clock_samples": 0,
        "files_written": 0,
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise GateError("reject unauthorized Zig V4 source action: " + message)


def parse_arguments() -> argparse.Namespace:
    arguments = sys.argv[1:]
    flags = [item for item in arguments if item.startswith("--")]
    require(len(flags) == len(set(flags)),
            "reject repeated source authorization or caller pins")
    parser = SafeArgumentParser(description=__doc__, allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--verify-frozen-context", action="store_true")
    group.add_argument("--render-contract", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--graph-source-sha256", required=True)
    parser.add_argument("--graph-inputs-sha256", required=True)
    parser.add_argument("--graph-summary-sha256", required=True)
    parser.add_argument("--graph-svg-sha256", required=True)
    return parser.parse_args(arguments)


def main() -> int:
    try:
        options = parse_arguments()
        context = load_context(options)
        result = source_only_result(context, run_hostile=options.self_test)
        expected = contract_document(context, result["scanner_matrix"])
        if options.render_contract:
            require(options.contract_sha256 is None,
                    "do not invent a hash for the contract being rendered")
            sys.stdout.buffer.write(canonical(expected))
            return 0
        require(options.contract_sha256 is not None,
                "independently caller-pin the complete V4 machine contract")
        size = os.stat(ROOT / CONTRACT_PATH, follow_symlinks=False).st_size
        raw, _owner = read_owned(
            CONTRACT_PATH, checked_digest(options.contract_sha256, "V4 contract"), size,
        )
        require(
            strict_document(raw, "canonical Zig V4 machine contract") == expected,
            "bind complete V4 feature to every actual owner and original Scanner case",
        )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (
        GateError, OSError, ValueError, TypeError, KeyError,
        IndexError, json.JSONDecodeError, RecursionError,
    ) as error:
        sys.stderr.write("zig-scanner-phrase-v4: " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
