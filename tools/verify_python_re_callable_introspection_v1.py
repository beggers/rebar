#!/usr/bin/env python3
"""Freeze additive Python regex callable introspection without running engines."""

from __future__ import annotations

import argparse
import builtins
import copy
import ctypes
from dataclasses import dataclass
import fcntl
import gc
import gzip
import hashlib
import importlib
import inspect
import io
import json
import locale
import os
from pathlib import Path, PurePosixPath
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Mapping, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-python-re-callable-introspection-v1"
SOURCE_RELATIVE = "tools/verify_python_re_callable_introspection_v1.py"
PROTOCOL_RELATIVE = "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md"
CONTRACT_RELATIVE = "oracle/phase1/p0-callable-introspection-v1.json"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
MAX_OWNER_BYTES = 4 * 1024 * 1024
MAX_WORKER_BYTES = 4 * 1024 * 1024
ORIGINAL_CASE_COUNT = 31_237
ORIGINAL_SUITE_COUNT = 13
ORIGINAL_PRIVATE_WAIVER_COUNT = 13
ADDITIVE_CASE_COUNT = 50
PLANNED_HOLDOUT_CASE_COUNT = 4_194_304
V30_EVIDENCE_OWNER_COUNT = 149
V30_HISTORY_REFERENCE_COUNT = 154
PUBLISHED_EVIDENCE_OWNER_COUNT = 151
PUBLISHED_HISTORY_REFERENCE_COUNT = 156


@dataclass(frozen=True, slots=True)
class Owner:
    path: str
    sha256: str
    size: int | None = None


GOAL = Owner(
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
)
ORIGINAL_INVENTORY = Owner(
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
ORIGINAL_PROTOCOL = Owner(
    "oracle/phase1/P0-COMPLETENESS-V1.md",
    "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
    10392,
)
ORIGINAL_VERIFIER = Owner(
    "tools/verify_p0_completeness_v1.py",
    "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
    118040,
)
UPSTREAM_TEST = Owner(
    "oracle/cpython-3.14.6/test_re.py",
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
    150895,
)
INSTALLED_RE = Owner(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
    "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
    17876,
)
OVERVIEW = (
    Owner(
        "tools/render_candidate_current_overview_v30.py",
        "a8c2bb2e0ccfab0b76b5387437fe48279e01ca1034739a67967f543f1930c507",
        60771,
    ),
    Owner(
        "docs/evidence/candidate-current-overview-v30.inputs.json",
        "ea2ea381a22a9a23344ff40505d975aba8d25704d2ad90e03b58018fda44ca0f",
        65902,
    ),
    Owner(
        "docs/evidence/candidate-current-overview-v30.json",
        "b04db4e93dc74bb9200c13133c0a33bd33961b5f35e5810e74de65b29fcab534",
        293980,
    ),
    Owner(
        "docs/evidence/candidate-current-overview-v30.svg",
        "a3dbbb69c5140d15588463e0e3579d5bea5d95587f1abf444b6679cd3361d4c6",
        12987,
    ),
)
RUST_V12_SOURCE_BUILD = (
    Owner(
        "oracle/phase2/evidence/"
        "native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz",
        "840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d",
        108325,
    ),
    Owner(
        "oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-"
        "rust-flag-original-p0-publication-receipt.json",
        "1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f",
        2109,
    ),
)
SIX_FAMILY_PRODUCER = Owner(
    "tools/run_owned_six_family_original_p0_producer_v1.py",
    "36451c10221857cca8c77fad7533382f4e3969a20a5cdf73c055beea1d315d33",
    149599,
)
FAMILY_MODULES = {
    "rust": "candidates.rust_candidate",
    "c": "candidates.vm_candidate",
    "zig": "candidates.zig_candidate",
    "cpp": "candidates.cpp_candidate",
    "go": "candidates.go_candidate",
    "fortran": "candidates.fortran_candidate",
}
MODULE_FUNCTIONS = (
    "match", "fullmatch", "search", "sub", "subn", "split",
    "findall", "finditer", "compile", "purge", "escape",
)
PATTERN_METHODS = (
    "search", "match", "fullmatch", "split", "findall", "finditer",
    "sub", "subn", "scanner",
)
MATCH_METHODS = (
    "group", "groups", "groupdict", "start", "end", "span", "expand",
)
SCANNER_CASES = (
    ("Scanner", "unbound", "__init__"),
    ("Scanner", "unbound", "scan"),
    ("Scanner", "bound", "scan"),
    ("compiled-scanner", "unbound", "match"),
    ("compiled-scanner", "bound", "match"),
    ("compiled-scanner", "unbound", "search"),
    ("compiled-scanner", "bound", "search"),
)
ORIGINAL_SUITES = (
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
FORBIDDEN_EXTERNAL_ROOTS = frozenset({
    "_regex", "cffi", "fancy_regex", "google_re2", "hyperscan", "onig",
    "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class IntrospectionError(Exception):
    """An additive oracle owner, boundary, reference, or worker is invalid."""


class ForbiddenEffect(IntrospectionError):
    """A real source-only side effect was physically prevented."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise IntrospectionError(message)


def sha256(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only the complete original byte stream")
    return hashlib.sha256(raw).hexdigest()


def checked_sha256(value: object, label: str) -> str:
    need(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "require an independently pinned canonical SHA-256: " + label,
    )
    return value


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                separators=(",", ":"),
            ) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise IntrospectionError("reject noncanonical oracle observations") from exc


def decode_json(raw: bytes, label: str, *, exact: bool = False) -> dict[str, Any]:
    need(
        type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
        "reject empty, oversized, or truncated JSON: " + label,
    )

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            need(type(key) is str and key not in result,
                 "reject duplicate JSON keys: " + label)
            result[key] = value
        return result

    def reject_constant(value: str) -> Any:
        raise IntrospectionError("reject a nonfinite JSON constant: " + value)

    try:
        document = json.loads(
            raw.decode("utf-8", "strict"), object_pairs_hook=unique,
            parse_constant=reject_constant,
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise IntrospectionError("reject malformed oracle JSON: " + label) from exc
    need(type(document) is dict, "require a JSON object: " + label)
    if exact:
        need(canonical(document) == raw,
             "reject a noncanonical frozen oracle owner: " + label)
    return document


def checked_relative(value: object) -> tuple[str, ...]:
    need(
        type(value) is str and 0 < len(value) <= 512
        and "\\" not in value and "\x00" not in value,
        "reject an escaped or ambiguous oracle path",
    )
    parsed = PurePosixPath(value)
    need(
        not parsed.is_absolute() and str(parsed) == value
        and 0 < len(parsed.parts) <= 12
        and all(part not in ("", ".", "..") for part in parsed.parts),
        "reject an absolute, normalized, or parent-escaping oracle path",
    )
    need(
        not any(
            "holdout" in part.lower() or "hidden" in part.lower()
            or part == "candidates" or part == "performance"
            for part in parsed.parts
        ),
        "never open a candidate, final case, performance result, or holdout",
    )
    return parsed.parts


def owner_document(owner: Owner) -> dict[str, Any]:
    result: dict[str, Any] = {"path": owner.path, "sha256": owner.sha256}
    if owner.size is not None:
        result["bytes"] = owner.size
    return result


def read_owner(owner: Owner, *, external: bool = False) -> bytes:
    checked_sha256(owner.sha256, owner.path)
    need(
        owner.size is None
        or (type(owner.size) is int and 0 < owner.size <= MAX_OWNER_BYTES),
        "reject an unbounded or oversized frozen owner: " + owner.path,
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    directories: list[int] = []
    handle: int | None = None
    try:
        if external:
            need(owner == INSTALLED_RE,
                 "never inspect an unapproved external Python owner")
            handle = os.open(owner.path, flags)
            visible = os.stat(owner.path, follow_symlinks=False)
        else:
            pieces = checked_relative(owner.path)
            directory = os.open(
                str(ROOT), flags | getattr(os, "O_DIRECTORY", 0),
            )
            directories.append(directory)
            for piece in pieces[:-1]:
                directory = os.open(
                    piece, flags | getattr(os, "O_DIRECTORY", 0),
                    dir_fd=directory,
                )
                directories.append(directory)
            handle = os.open(pieces[-1], flags, dir_fd=directory)
            visible = os.stat(
                pieces[-1], dir_fd=directory, follow_symlinks=False,
            )
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and 0 < before.st_size <= MAX_OWNER_BYTES
            and (owner.size is None or before.st_size == owner.size)
            and (before.st_dev, before.st_ino, before.st_size,
                 before.st_uid, before.st_nlink)
            == (visible.st_dev, visible.st_ino, visible.st_size,
                visible.st_uid, visible.st_nlink),
            "reject a linked, foreign, substituted, or truncated owner: "
            + owner.path,
        )
        remaining = before.st_size
        parts: list[bytes] = []
        while remaining:
            part = os.read(handle, min(remaining, 1024 * 1024))
            need(type(part) is bytes and bool(part),
                 "reject a truncated descriptor-bound source")
            parts.append(part)
            remaining -= len(part)
        need(os.read(handle, 1) == b"", "reject appended owner bytes")
        raw = b"".join(parts)
        after = os.fstat(handle)
        need(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_uid, before.st_nlink, before.st_mtime_ns,
             before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_uid, after.st_nlink, after.st_mtime_ns,
                after.st_ctime_ns)
            and sha256(raw) == owner.sha256,
            "reject bytes changed during owner verification: " + owner.path,
        )
        return raw
    finally:
        if handle is not None:
            os.close(handle)
        for directory in reversed(directories):
            os.close(directory)


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "require the pinned, isolated, bytecode-free CPython 3.14.6 oracle",
    )
    need(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "a source freeze or reference may never import a candidate",
    )


def case_matrix() -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for index, member in enumerate(MODULE_FUNCTIONS):
        matrix.append({
            "id": f"callable-introspection.v1.module.{index:02d}.{member}",
            "category": "module", "owner": "module",
            "binding": "module", "member": member,
        })
    for category, members in (("pattern", PATTERN_METHODS),
                              ("match", MATCH_METHODS)):
        for member_index, member in enumerate(members):
            for binding_index, binding in enumerate(("unbound", "bound")):
                number = member_index * 2 + binding_index
                matrix.append({
                    "id": (
                        f"callable-introspection.v1.{category}."
                        f"{number:02d}.{binding}.{member}"
                    ),
                    "category": category, "owner": category,
                    "binding": binding, "member": member,
                })
    for index, (owner, binding, member) in enumerate(SCANNER_CASES):
        matrix.append({
            "id": (
                f"callable-introspection.v1.scanner.{index:02d}."
                f"{binding}.{owner}.{member}"
            ),
            "category": "scanner", "owner": owner,
            "binding": binding, "member": member,
        })
    return matrix


def validate_matrix(value: object) -> str:
    expected = case_matrix()
    need(
        type(value) is list and len(value) == ADDITIVE_CASE_COUNT
        and value == expected,
        "reject missing, reordered, repeated, invented, or altered "
        "additive introspection cases",
    )
    ids = [case["id"] for case in value]
    need(len(set(ids)) == ADDITIVE_CASE_COUNT,
         "reject a duplicate callable-introspection case")
    counts = {
        category: sum(case["category"] == category for case in value)
        for category in ("module", "pattern", "match", "scanner")
    }
    need(counts == {"module": 11, "pattern": 18,
                    "match": 14, "scanner": 7},
         "reject a changed additive introspection category denominator")
    return sha256(canonical(value))


def current_history() -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "original_suite_count": ORIGINAL_SUITE_COUNT,
        "original_case_denominator": ORIGINAL_CASE_COUNT,
        "additional_introspection_case_count": ADDITIVE_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "original_private_waiver_count": ORIGINAL_PRIVATE_WAIVER_COUNT,
        "historical_v30_repository_evidence_owner_count": (
            V30_EVIDENCE_OWNER_COUNT
        ),
        "historical_v30_authenticated_history_reference_count": (
            V30_HISTORY_REFERENCE_COUNT
        ),
        "repository_evidence_owner_count": PUBLISHED_EVIDENCE_OWNER_COUNT,
        "authenticated_history_reference_count": (
            PUBLISHED_HISTORY_REFERENCE_COUNT
        ),
        "published_rust_v12_additional_evidence_owner_count": 2,
        "qualified_candidate_count": 0,
        "rust_semantic_mismatch_count": 1087,
        "c_semantic_mismatch_count": 1230,
        "zig_semantic_mismatch_count": 2172,
        "candidate_introspection": "NOT MEASURED",
        "introspection_reference": "NOT RUN",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "final_holdout_opened": False,
        "final_comparison_cases_generated": False,
        "final_comparison_planned_case_count": PLANNED_HOLDOUT_CASE_COUNT,
        "winner_selected": False,
    }


def validate_current_history(value: object) -> None:
    need(type(value) is dict and value == current_history(),
         "reject a false result, denominator, candidate, or holdout history")


def boundaries(*, authenticated_build_archive_count: int = 0
               ) -> dict[str, Any]:
    return {
        "actual_reference_roles_started": 0,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_native_loads": 0,
        "actual_source_builds": 0,
        "actual_files_written": 0,
        "actual_clock_samples": 0,
        "actual_network_requests": 0,
        "actual_threads_started": 0,
        "actual_compressed_source_build_archives_authenticated": (
            authenticated_build_archive_count
        ),
        "actual_source_build_archives_decompressed": 0,
        "actual_source_build_archive_uncompressed_bytes_read": 0,
        "actual_candidate_matching_archives_opened": 0,
        "actual_final_cases_read": 0,
        "actual_holdout_cases_read": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "candidate_introspection": "NOT MEASURED",
        "introspection_reference": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_sha256(source_pin, "additive introspection source")
    checked_sha256(protocol_pin, "additive introspection protocol")
    matrix = case_matrix()
    matrix_sha256 = validate_matrix(matrix)
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 1,
        "status": "SOURCE FREEZE ONLY; REFERENCE AND CANDIDATES NOT RUN",
        "phase": "ADDITIVE CORRECTNESS ORACLE; NO BENCHMARK",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "goal": owner_document(GOAL),
        "pinned_runtime": {
            "implementation": "CPython", "version": "3.14.6",
            "executable": PINNED_PYTHON,
            "executable_sha256": PINNED_PYTHON_SHA256,
            "isolated": True, "bytecode_writes": False,
            "installed_re": owner_document(INSTALLED_RE),
            "original_upstream_test": owner_document(UPSTREAM_TEST),
        },
        "original_correctness": {
            "inventory": owner_document(ORIGINAL_INVENTORY),
            "protocol": owner_document(ORIGINAL_PROTOCOL),
            "verifier": owner_document(ORIGINAL_VERIFIER),
            "source_ordered_suites": [
                {"id": suite, "case_count": count}
                for suite, count in ORIGINAL_SUITES
            ],
            "suite_count": ORIGINAL_SUITE_COUNT,
            "case_execution_denominator": ORIGINAL_CASE_COUNT,
            "private_waiver_count": ORIGINAL_PRIVATE_WAIVER_COUNT,
            "denominator_modified": False,
            "full_resource_candidate_2g_search": "NOT RUN",
            "full_resource_candidate_2g_subn": "NOT RUN",
            "candidate_facing_large_input_maximum": 5147,
            "full_resource_reference_bytes": 2147483648,
            "full_resource_reference_allowance_bytes": 42949672960,
        },
        "additional_obligation": {
            "id": "API-PUBLIC-CALLABLE-INTROSPECTION",
            "status": "FROZEN; TWO INDEPENDENT REFERENCES NOT RUN",
            "included_in_original_31237_denominator": False,
            "case_count": ADDITIVE_CASE_COUNT,
            "matrix_sha256": matrix_sha256,
            "categories": [
                {"id": "module", "case_count": 11},
                {"id": "pattern", "case_count": 18},
                {"id": "match", "case_count": 14},
                {"id": "scanner", "case_count": 7},
            ],
            "case_matrix": matrix,
            "signature_fields": [
                "status", "parameters", "parameter_name",
                "parameter_kind", "normalized_default",
                "return_annotation", "text_signature_present",
                "raw_text_signature", "signature_error_class",
            ],
            "sys_maxsize_normalization": "sys.maxsize",
            "uninspectable_match_group": "ValueError",
            "hardcoded_candidate_observations_allowed": False,
            "candidate_module_name_equality_required": False,
        },
        "future_reference_policy": {
            "explicit_mode": "--run-reference",
            "reference_roles": ["reference-a", "reference-b"],
            "independent_isolated_worker_process_count": 2,
            "different_actual_process_ids_required": True,
            "exact_complete_case_vectors_required": True,
            "complete_stdout_and_stderr_required": True,
            "executed_in_source_freeze": False,
        },
        "future_candidate_policy": {
            "explicit_mode": "--run-candidate",
            "families": [
                {"id": name, "module": module}
                for name, module in FAMILY_MODULES.items()
            ],
            "independently_pinned_reference_report_required": True,
            "independently_pinned_original_31237_pass_required": True,
            "independently_pinned_no_delegation_proof_required": True,
            "source_owned_six_family_producer": owner_document(
                SIX_FAMILY_PRODUCER,
            ),
            "external_regex_engines_allowed": False,
            "stdlib_regex_delegation_allowed": False,
            "cross_candidate_delegation_allowed": False,
            "fallback_allowed": False,
            "executed_in_source_freeze": False,
        },
        "preserved_historical_v30_overview": {
            "version": 30,
            "owners": [owner_document(item) for item in OVERVIEW],
            "historical_repository_evidence_owner_count": (
                V30_EVIDENCE_OWNER_COUNT
            ),
            "historical_authenticated_history_reference_count": (
                V30_HISTORY_REFERENCE_COUNT
            ),
        },
        "actual_published_rust_v12_source_build": {
            "owners": [owner_document(item) for item in RUST_V12_SOURCE_BUILD],
            "actual_compiler_process_count": 28,
            "actual_new_evidence_owner_count": 2,
            "repository_evidence_owner_count_after_publication": (
                PUBLISHED_EVIDENCE_OWNER_COUNT
            ),
            "authenticated_history_reference_count_after_publication": (
                PUBLISHED_HISTORY_REFERENCE_COUNT
            ),
            "build_status": "PASS",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "compressed_source_build_archive_decompression_required": False,
            "matching_archive_access_required": False,
        },
        "actual_published_history": {
            "actual_history": current_history(),
        },
        "phase_boundary": boundaries(),
    }


def normalize_annotation(value: Any) -> dict[str, Any]:
    if value is inspect.Signature.empty:
        return {"kind": "empty"}
    if value is None:
        return {"kind": "none"}
    if type(value) in (str, bool, int):
        return {"kind": type(value).__name__, "value": value}
    return {"kind": "type", "name": getattr(value, "__qualname__",
                                                type(value).__qualname__)}


def normalize_default(value: Any) -> dict[str, Any]:
    if value is inspect.Signature.empty:
        return {"kind": "empty"}
    if value is None:
        return {"kind": "none"}
    if type(value) is int and value == sys.maxsize:
        return {"kind": "sys.maxsize"}
    if type(value) in (str, bool, int):
        return {"kind": type(value).__name__, "value": value}
    return {"kind": "type", "name": type(value).__qualname__}


def observe_callable(value: Any) -> dict[str, Any]:
    text_present = hasattr(value, "__text_signature__")
    text = getattr(value, "__text_signature__", None)
    need(text is None or type(text) is str,
         "reject non-string public callable text-signature metadata")
    result: dict[str, Any] = {
        "text_signature_present": text_present,
        "raw_text_signature": text,
    }
    try:
        signature = inspect.signature(value)
    except (TypeError, ValueError) as exc:
        result.update({
            "status": "UNINSPECTABLE",
            "signature_error_class": type(exc).__name__,
        })
        return result
    result.update({
        "status": "INSPECTABLE",
        "parameters": [
            {
                "parameter_name": parameter.name,
                "parameter_kind": parameter.kind.name,
                "normalized_default": normalize_default(parameter.default),
                "annotation": normalize_annotation(parameter.annotation),
            }
            for parameter in signature.parameters.values()
        ],
        "return_annotation": normalize_annotation(
            signature.return_annotation,
        ),
    })
    return result


def observe_engine(engine: Any) -> list[dict[str, Any]]:
    pattern = engine.compile("(?P<word>[A-Za-z]+)")
    matched = pattern.match("Alpha42")
    need(matched is not None,
         "never invent an introspection match or use a fallback engine")
    compiled_scanner = pattern.scanner("Alpha42")
    lexical_scanner = engine.Scanner([("[A-Za-z]+", None)])
    records: list[dict[str, Any]] = []
    for case in case_matrix():
        owner = case["owner"]
        binding = case["binding"]
        member = case["member"]
        if owner == "module":
            value = getattr(engine, member)
        elif owner == "pattern":
            value = getattr(
                engine.Pattern if binding == "unbound" else pattern,
                member,
            )
        elif owner == "match":
            value = getattr(
                engine.Match if binding == "unbound" else matched,
                member,
            )
        elif owner == "Scanner":
            value = getattr(
                engine.Scanner if binding == "unbound" else lexical_scanner,
                member,
            )
        else:
            need(owner == "compiled-scanner",
                 "reject an unknown scanner owner")
            value = getattr(
                type(compiled_scanner)
                if binding == "unbound" else compiled_scanner,
                member,
            )
        records.append({**case, "observation": observe_callable(value)})
    validate_observations(records)
    return records


def validate_observations(records: object) -> str:
    need(type(records) is list and len(records) == ADDITIVE_CASE_COUNT,
         "require all 50 original callable observations")
    expected = case_matrix()
    for index, (case, item) in enumerate(zip(expected, records, strict=True)):
        need(
            type(item) is dict and set(item) == set(case) | {"observation"}
            and all(item[key] == value for key, value in case.items())
            and type(item["observation"]) is dict,
            "reject an omitted, reordered, forged, or partial callable case "
            + str(index),
        )
        observation = item["observation"]
        need(
            type(observation.get("text_signature_present")) is bool
            and (observation.get("raw_text_signature") is None
                 or type(observation["raw_text_signature"]) is str),
            "reject invalid original callable metadata",
        )
        if observation.get("status") == "INSPECTABLE":
            need(
                set(observation) == {
                    "status", "parameters", "return_annotation",
                    "text_signature_present", "raw_text_signature",
                }
                and type(observation["parameters"]) is list
                and type(observation["return_annotation"]) is dict,
                "reject partial inspectable callable metadata",
            )
            for parameter in observation["parameters"]:
                need(
                    type(parameter) is dict
                    and set(parameter) == {
                        "parameter_name", "parameter_kind",
                        "normalized_default", "annotation",
                    }
                    and type(parameter["parameter_name"]) is str
                    and parameter["parameter_kind"] in {
                        "POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD",
                        "VAR_POSITIONAL", "KEYWORD_ONLY", "VAR_KEYWORD",
                    }
                    and type(parameter["normalized_default"]) is dict
                    and type(parameter["annotation"]) is dict,
                    "reject hidden positional-only or default metadata",
                )
        else:
            need(
                observation.get("status") == "UNINSPECTABLE"
                and set(observation) == {
                    "status", "signature_error_class",
                    "text_signature_present", "raw_text_signature",
                }
                and observation.get("signature_error_class")
                in {"TypeError", "ValueError"},
                "reject an invented uninspectable-signature result",
            )
    return sha256(canonical(records))


class SourceWall:
    """Physically intercept the effects forbidden in source-only controls."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = {
            item: 0 for item in (
                "filesystem", "write", "process", "import", "network",
                "thread", "clock", "native", "lock", "signal", "archive",
                "garbage_collection", "locale", "regex_matching",
            )
        }

    def deny(self, owner: Any, name: str, category: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise ForbiddenEffect(
                "physically blocked source-only " + category + ": " + name,
            )

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceWall:
        groups: list[tuple[Any, tuple[str, ...], str]] = [
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "stat", "lstat", "scandir", "listdir"),
             "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "stat", "lstat",
                    "resolve"), "filesystem"),
            (os, ("write", "mkdir", "makedirs", "unlink", "remove",
                  "rename", "replace", "fsync", "urandom"), "write"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink",
                    "rename", "replace", "touch"), "write"),
            (tempfile, ("mkdtemp", "mkstemp"), "write"),
            (subprocess, ("Popen", "run", "call", "check_call",
                          "check_output"), "process"),
            (importlib, ("import_module",), "import"),
            (socket, ("socket", "create_connection"), "network"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "clock_gettime", "sleep"), "clock"),
            (ctypes, ("CDLL", "PyDLL"), "native"),
            (fcntl, ("flock",), "lock"),
            (signal, ("signal", "pthread_sigmask"), "signal"),
            (gzip, ("open", "decompress"), "archive"),
            (zlib, ("decompress", "decompressobj"), "archive"),
            (gc, ("collect",), "garbage_collection"),
            (locale, ("setlocale",), "locale"),
        ]
        original_re = sys.modules.get("re")
        if original_re is not None:
            groups.append((
                original_re,
                ("compile", "match", "fullmatch", "search", "sub", "subn",
                 "split", "findall", "finditer"),
                "regex_matching",
            ))
        for owner, names, category in groups:
            for name in names:
                self.deny(owner, name, category)
        return self

    def __exit__(self, *_args: Any) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def validate_reference_worker(document: object, role: str) -> str:
    need(type(document) is dict, "reject a non-object reference worker")
    need(
        document.get("schema") == SCHEMA + "-reference-worker"
        and document.get("status") == "PASS"
        and document.get("role") == role
        and type(document.get("actual_process_id")) is int
        and document["actual_process_id"] > 0
        and document.get("original_case_denominator") == ORIGINAL_CASE_COUNT
        and document.get("additional_case_count") == ADDITIVE_CASE_COUNT
        and document.get("candidate_imports") == 0
        and document.get("hidden_cases_read") == 0
        and document.get("performance") == "NOT MEASURED",
        "reject a forged, incomplete, candidate-tainted reference worker",
    )
    actual = validate_observations(document.get("records"))
    need(document.get("record_vector_sha256") == actual,
         "reject a reference worker with invented vector fingerprints")
    return actual


def validate_reference_pair(first: object, second: object) -> str:
    left = validate_reference_worker(first, "reference-a")
    right = validate_reference_worker(second, "reference-b")
    need(type(first) is dict and type(second) is dict,
         "require both independently executed references")
    need(
        first["actual_process_id"] != second["actual_process_id"]
        and left == right and first["records"] == second["records"],
        "reject reused process IDs or mismatching full reference vectors",
    )
    return left


def validate_family(family: object, module: object) -> None:
    need(
        type(family) is str and family in FAMILY_MODULES
        and type(module) is str and module == FAMILY_MODULES[family],
        "reject an unknown family, cross-family module, or fallback engine",
    )


def validate_independence_proof(proof: object, family: str) -> None:
    need(type(proof) is dict, "reject a missing independence proof")
    validate_family(family, proof.get("candidate_module"))
    need(
        proof.get("status") == "PASS"
        and proof.get("family") == family
        and proof.get("external_regex_dependency_count") == 0
        and proof.get("cross_family_dependency_count") == 0
        and proof.get("stdlib_regex_delegation") is False
        and proof.get("fallback_allowed") is False
        and proof.get("candidate_source_verified") is True,
        "reject unproven native ownership or delegated candidate matching",
    )


def synthetic_reference(role: str, process: int) -> dict[str, Any]:
    records = [
        {
            **case,
            "observation": {
                "status": "INSPECTABLE",
                "parameters": [],
                "return_annotation": {"kind": "empty"},
                "text_signature_present": False,
                "raw_text_signature": None,
            },
        }
        for case in case_matrix()
    ]
    return {
        "schema": SCHEMA + "-reference-worker", "status": "PASS",
        "role": role, "actual_process_id": process,
        "original_case_denominator": ORIGINAL_CASE_COUNT,
        "additional_case_count": ADDITIVE_CASE_COUNT,
        "record_vector_sha256": validate_observations(records),
        "records": records, "candidate_imports": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
    }


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    expected = contract_document(source_pin, protocol_pin)
    need(
        sha256(canonical(expected))
        == checked_sha256(contract_pin, "frozen additive machine contract"),
        "reject a stale or substituted independently pinned contract",
    )
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, value: bool) -> None:
        need(value, "reject a required source-only control: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (
            IntrospectionError, OSError, TypeError, ValueError,
            UnicodeError, RecursionError, OverflowError,
        ):
            rejected.append(name)
            return
        raise IntrospectionError("accept hostile source-only control: " + name)

    with SourceWall() as wall:
        matrix = case_matrix()
        accept("freeze all 50 additional cases", len(matrix) == 50)
        accept("freeze 11 module cases",
               sum(row["category"] == "module" for row in matrix) == 11)
        accept("freeze 18 bound and unbound pattern cases",
               sum(row["category"] == "pattern" for row in matrix) == 18)
        accept("freeze 14 bound and unbound match cases",
               sum(row["category"] == "match" for row in matrix) == 14)
        accept("freeze seven scanner cases",
               sum(row["category"] == "scanner" for row in matrix) == 7)
        accept("preserve the immutable original denominator",
               len(ORIGINAL_SUITES) == 13
               and sum(count for _, count in ORIGINAL_SUITES) == 31237)
        accept("keep all six independent candidate families visible",
               tuple(FAMILY_MODULES)
               == ("rust", "c", "zig", "cpp", "go", "fortran"))
        accept("retain a separately counted introspection category",
               expected["additional_obligation"]
               ["included_in_original_31237_denominator"] is False)
        accept("require two actual distinct reference roles",
               expected["future_reference_policy"]
               ["different_actual_process_ids_required"] is True)
        accept("retain all actual current compatibility failures",
               current_history()["rust_semantic_mismatch_count"] == 1087
               and current_history()["c_semantic_mismatch_count"] == 1230
               and current_history()["zig_semantic_mismatch_count"] == 2172)
        accept("preserve 149 historical V30 owners and 154 references",
               current_history()
               ["historical_v30_repository_evidence_owner_count"] == 149
               and current_history()
               ["historical_v30_authenticated_history_reference_count"]
               == 154)
        accept("preserve 151 released owners and 156 released references",
               current_history()["repository_evidence_owner_count"] == 151
               and current_history()
               ["authenticated_history_reference_count"] == 156)
        accept("preserve exactly two released Rust V12 build owners",
               current_history()
               ["published_rust_v12_additional_evidence_owner_count"] == 2
               and len(RUST_V12_SOURCE_BUILD) == 2)
        accept("normalize the actual sys.maxsize sentinel",
               normalize_default(sys.maxsize) == {"kind": "sys.maxsize"})
        accept("distinguish absent and None defaults",
               normalize_default(inspect.Signature.empty)
               != normalize_default(None))
        accept("retain Match.group ValueError as an observed class",
               expected["additional_obligation"]
               ["uninspectable_match_group"] == "ValueError")
        validate_current_history(current_history())
        accept("validate every frozen deterministic matrix identity",
               validate_matrix(matrix)
               == expected["additional_obligation"]["matrix_sha256"])

        for index in range(ADDITIVE_CASE_COUNT):
            hostile = matrix[:index] + matrix[index + 1:]
            reject("reject omitted exact case " + matrix[index]["id"],
                   lambda value=hostile: validate_matrix(value))
        duplicate = copy.deepcopy(matrix)
        duplicate[-1] = copy.deepcopy(duplicate[0])
        reject("reject a duplicated original case",
               lambda: validate_matrix(duplicate))
        swapped = copy.deepcopy(matrix)
        swapped[0], swapped[1] = swapped[1], swapped[0]
        reject("reject silently reordered original cases",
               lambda: validate_matrix(swapped))
        for field, value in (
            ("id", "callable-introspection.v1.forged"),
            ("owner", "candidates.rust_candidate"),
            ("binding", "delegated"),
            ("member", "fallback"),
            ("category", "holdout"),
        ):
            changed = copy.deepcopy(matrix)
            changed[0][field] = value
            reject("reject forged matrix " + field,
                   lambda document=changed: validate_matrix(document))
        reject("reject an invented 51st case",
               lambda: validate_matrix(matrix + [copy.deepcopy(matrix[0])]))

        reference_a = synthetic_reference("reference-a", 101)
        reference_b = synthetic_reference("reference-b", 202)
        accept("accept only two complete synthetic independent role vectors",
               bool(validate_reference_pair(reference_a, reference_b)))
        for field, value in (
            ("schema", "forged"),
            ("status", "FAIL"),
            ("role", "reference-b"),
            ("actual_process_id", 0),
            ("original_case_denominator", 31287),
            ("additional_case_count", 49),
            ("record_vector_sha256", "0" * 64),
            ("candidate_imports", 1),
            ("hidden_cases_read", 1),
            ("performance", "FASTER"),
        ):
            hostile_reference = copy.deepcopy(reference_a)
            hostile_reference[field] = value
            reject("reject forged source-only reference " + field,
                   lambda document=hostile_reference:
                   validate_reference_worker(document, "reference-a"))
        same_process = copy.deepcopy(reference_b)
        same_process["actual_process_id"] = 101
        reject("reject reused independent-reference process identity",
               lambda: validate_reference_pair(reference_a, same_process))
        changed_vector = copy.deepcopy(reference_b)
        changed_vector["records"][0]["observation"]
        changed_vector["records"][0]["observation"][
            "text_signature_present"
        ] = True
        changed_vector["record_vector_sha256"] = validate_observations(
            changed_vector["records"],
        )
        reject("reject divergent complete independent reference vectors",
               lambda: validate_reference_pair(reference_a, changed_vector))

        for name, module in FAMILY_MODULES.items():
            validate_family(name, module)
            accept("retain exact independently owned family " + name, True)
            reject("reject cross-family fallback for " + name,
                   lambda family=name: validate_family(
                       family, "candidates.vm_candidate"
                       if family != "c" else "candidates.rust_candidate",
                   ))
        for hostile in ("regex", "re2", "_sre", "re", "ast", "",
                        "candidates", "../rust"):
            reject("reject external or unowned family " + hostile,
                   lambda family=hostile: validate_family(
                       family, "candidates.rust_candidate",
                   ))
        proof = {
            "status": "PASS", "family": "rust",
            "candidate_module": FAMILY_MODULES["rust"],
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
            "stdlib_regex_delegation": False,
            "fallback_allowed": False,
            "candidate_source_verified": True,
        }
        validate_independence_proof(proof, "rust")
        accept("require a genuine independent no-delegation proof", True)
        for field, value in (
            ("status", "FAIL"), ("family", "zig"),
            ("candidate_module", "candidates.zig_candidate"),
            ("external_regex_dependency_count", 1),
            ("cross_family_dependency_count", 1),
            ("stdlib_regex_delegation", True),
            ("fallback_allowed", True),
            ("candidate_source_verified", False),
        ):
            hostile_proof = copy.deepcopy(proof)
            hostile_proof[field] = value
            reject("reject delegated or stale candidate proof " + field,
                   lambda value=hostile_proof:
                   validate_independence_proof(value, "rust"))

        for field, value in (
            ("original_case_denominator", 31287),
            ("additional_introspection_case_count", 49),
            ("additional_cases_included_in_original_denominator", True),
            ("original_suite_count", 12),
            ("original_private_waiver_count", 12),
            ("historical_v30_repository_evidence_owner_count", 151),
            ("historical_v30_authenticated_history_reference_count", 156),
            ("repository_evidence_owner_count", 149),
            ("authenticated_history_reference_count", 154),
            ("published_rust_v12_additional_evidence_owner_count", 0),
            ("qualified_candidate_count", 1),
            ("rust_semantic_mismatch_count", 0),
            ("c_semantic_mismatch_count", 1262),
            ("zig_semantic_mismatch_count", 0),
            ("candidate_introspection", "PASS"),
            ("introspection_reference", "PASS"),
            ("performance", "FASTER"),
            ("memory", "PASS"),
            ("undefined_behavior", "PASS"),
            ("confidence_intervals", "PASS"),
            ("holdout", "OPENED"),
            ("final_holdout_opened", True),
            ("final_comparison_cases_generated", True),
            ("final_comparison_planned_case_count", 4194303),
            ("winner_selected", True),
        ):
            forged_history = current_history()
            forged_history[field] = value
            reject("reject altered real project history " + field,
                   lambda document=forged_history:
                   validate_current_history(document))

        for fingerprint in ("", "0" * 63, "0" * 65, "A" * 64,
                            "z" * 64, None, 0, True):
            reject("reject malformed independent digest",
                   lambda value=fingerprint: checked_sha256(value, "hostile"))
        for path in ("", "/tmp/escaped", "../escape", "a/../b", "a//b",
                     "a/./b", "./a", "a/", "a\\b", "candidates/x",
                     "performance/x", "holdout/x", "HOLDOUT/x",
                     "hidden/x", "x" * 513):
            reject("reject unsafe source-only path " + repr(path),
                   lambda value=path: checked_relative(value))
        for raw in (b'{"x":1,"x":2}\n', b'{"x":NaN}\n',
                    b'{"x":Infinity}\n', b"[]\n", b"", b"null\n"):
            reject("reject noncanonical hostile JSON",
                   lambda value=raw: decode_json(value, "hostile"))

        original_re = sys.modules.get("re")
        probes: list[tuple[str, Any]] = [
            ("filesystem", lambda: builtins.open("/tmp/rebar-forbidden", "rb")),
            ("filesystem", lambda: io.open("/tmp/rebar-forbidden", "rb")),
            ("filesystem", lambda: os.open("/tmp/rebar-forbidden", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("/tmp/rebar-forbidden")),
            ("filesystem", lambda: Path("/tmp/rebar-forbidden").read_bytes()),
            ("write", lambda: os.write(-1, b"forbidden")),
            ("write", lambda: tempfile.mkdtemp()),
            ("process", lambda: subprocess.run(("rebar-forbidden",))),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("import", lambda: importlib.import_module("re")),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter()),
            ("native", lambda: ctypes.CDLL("rebar-forbidden")),
            ("lock", lambda: fcntl.flock(-1, fcntl.LOCK_EX)),
            ("signal", lambda: signal.signal(signal.SIGTERM, signal.SIG_DFL)),
            ("archive", lambda: gzip.decompress(b"forbidden")),
            ("archive", lambda: zlib.decompress(b"forbidden")),
            ("garbage_collection", lambda: gc.collect()),
            ("locale", lambda: locale.setlocale(locale.LC_CTYPE)),
        ]
        if original_re is not None:
            probes.append(("regex_matching",
                           lambda: original_re.search("a", "a")))
        for category, action in probes:
            before = wall.blocked[category]
            reject("physically intercept source-only " + category, action)
            need(wall.blocked[category] == before + 1,
                 "prove the real source-only effect was physically blocked")
        blocked = dict(wall.blocked)

    need(len(rejected) >= 120,
         "require exhaustive hostile source and reference controls")
    need(all(count > 0 for count in blocked.values()),
         "require an independently intercepted probe for every effect family")
    return {
        "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "blocked_effects_by_kind": blocked,
        "original_case_denominator": ORIGINAL_CASE_COUNT,
        "additional_case_count": ADDITIVE_CASE_COUNT,
        "category_counts": {"module": 11, "pattern": 18,
                            "match": 14, "scanner": 7},
        "matrix_sha256": validate_matrix(case_matrix()),
        "historical_v30_repository_evidence_owner_count": (
            V30_EVIDENCE_OWNER_COUNT
        ),
        "historical_v30_authenticated_history_reference_count": (
            V30_HISTORY_REFERENCE_COUNT
        ),
        "repository_evidence_owner_count": PUBLISHED_EVIDENCE_OWNER_COUNT,
        "authenticated_history_reference_count": (
            PUBLISHED_HISTORY_REFERENCE_COUNT
        ),
        "current_rust_mismatches": 1087,
        "current_c_mismatches": 1230,
        "current_zig_mismatches": 2172,
        **boundaries(),
    }


def authenticate_freeze(source_pin: str, protocol_pin: str,
                        contract_pin: str | None) -> dict[str, Any] | None:
    read_owner(Owner(SOURCE_RELATIVE, source_pin))
    read_owner(Owner(PROTOCOL_RELATIVE, protocol_pin))
    if contract_pin is None:
        return None
    raw = read_owner(Owner(CONTRACT_RELATIVE, contract_pin))
    observed = decode_json(raw, "additive source-freeze contract", exact=True)
    need(observed == contract_document(source_pin, protocol_pin),
         "reject a substituted, stale, or incomplete additive contract")
    return observed


def validate_original_inventory(document: Mapping[str, Any]) -> None:
    need(
        document.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and document.get("version") == 1,
        "reject a changed original Python correctness inventory",
    )
    denominator = document.get("denominator")
    need(type(denominator) is dict
         and denominator.get("final_required_case_execution_denominator")
         == ORIGINAL_CASE_COUNT,
         "never add 50 examples to the immutable 31,237-case denominator")
    suites = document.get("suites")
    need(type(suites) is list and len(suites) == ORIGINAL_SUITE_COUNT,
         "retain all 13 original correctness suites")
    for row, (name, count) in zip(suites, ORIGINAL_SUITES, strict=True):
        need(type(row) is dict and row.get("id") == name
             and row.get("case_execution_count") == count
             and type(row.get("baseline")) is dict
             and row["baseline"].get("status") == "PASS",
             "reject a changed original source-ordered suite: " + name)
    upstream = document.get("original_upstream")
    need(type(upstream) is dict
         and upstream.get("private_waiver_count")
         == ORIGINAL_PRIVATE_WAIVER_COUNT,
         "retain all 13 exact named private waivers")
    obligations = document.get("obligations")
    need(type(obligations) is dict
         and obligations.get("inherited_count") == 45
         and obligations.get("additional_named_count") == 28,
         "retain all 73 previously frozen public obligations")
    old_ids = {
        item.get("id")
        for key in ("inherited", "additional")
        for item in obligations.get(key, [])
        if type(item) is dict
    }
    need("API-PUBLIC-CALLABLE-INTROSPECTION" not in old_ids,
         "never pretend the new introspection obligation already passed")


def validate_overview(inputs: Mapping[str, Any],
                      summary: Mapping[str, Any]) -> None:
    need(
        inputs.get("schema") == "rebar-candidate-current-overview-v30-inputs"
        and inputs.get("version") == 30
        and summary.get("schema")
        == "rebar-candidate-current-overview-v30-summary"
        and summary.get("status") == "PASS",
        "reject the independently pinned historical V30 overview",
    )
    for document, history_name in (
        (inputs, "all_digest_addressed_history_path_count"),
        (summary, "authenticated_digest_addressed_history_paths"),
    ):
        need(
            document.get("python") == "3.14.6"
            and document.get("suite_count") == ORIGINAL_SUITE_COUNT
            and document.get("full_case_denominator") == ORIGINAL_CASE_COUNT
            and document.get("private_waiver_count")
            == ORIGINAL_PRIVATE_WAIVER_COUNT
            and document.get("repository_evidence_owner_count")
            == V30_EVIDENCE_OWNER_COUNT
            and document.get(history_name) == V30_HISTORY_REFERENCE_COUNT
            and document.get("performance") == "NOT MEASURED"
            and document.get("memory") == "NOT MEASURED"
            and document.get("undefined_behavior") == "NOT MEASURED"
            and document.get("confidence_intervals") == "NOT MEASURED"
            and document.get("final_holdout_opened") is False
            and document.get("final_comparison_cases_generated") is False
            and document.get("final_comparison_planned_case_count")
            == PLANNED_HOLDOUT_CASE_COUNT
            and document.get("winner_selected") is False,
            "reject forged historical V30 results, holdout, or performance",
        )
    need(
        inputs.get("candidate_qualified_count") == 0
        and summary.get("qualified_candidate_count") == 0
        and inputs.get("actual_rust_semantic_mismatch_count") == 1087
        and summary.get("rust_original_campaign_semantic_mismatch_count")
        == 1087
        and inputs.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_semantic_mismatch_count")
        == 1230
        and inputs.get("actual_zig_semantic_mismatch_count") == 2172
        and summary.get("zig_original_campaign_semantic_mismatch_count")
        == 2172,
        "never promote, improve, hide, or invent candidate matching results",
    )


def validate_rust_v12_receipt(document: Mapping[str, Any]) -> None:
    archive, receipt = RUST_V12_SOURCE_BUILD
    need(
        document.get("schema")
        == "rebar-phase2-owned-rust-flag-source-build-v12-"
        "durable-publication-receipt"
        and document.get("status") == "PASS"
        and document.get("build_status") == "PASS"
        and document.get("family") == "rust"
        and document.get("actual_compiler_process_count") == 28
        and document.get("expected_actual_compiler_process_count") == 28
        and document.get("archive_relative") == archive.path
        and document.get("archive_sha256") == archive.sha256
        and document.get("archive_bytes") == archive.size
        and document.get("historical_evidence_owner_count")
        == V30_EVIDENCE_OWNER_COUNT
        and document.get("historical_authenticated_reference_count")
        == V30_HISTORY_REFERENCE_COUNT
        and document.get("new_actual_evidence_owner_count") == 2
        and document.get("repository_evidence_owner_count_after_publication")
        == PUBLISHED_EVIDENCE_OWNER_COUNT
        and document.get(
            "authenticated_history_reference_count_after_publication",
        ) == PUBLISHED_HISTORY_REFERENCE_COUNT
        and document.get("candidate_correctness") == "NOT MEASURED"
        and document.get("candidate_qualified") is False
        and document.get("candidate_imports") == 0
        and document.get("candidate_processes_started") == 0
        and document.get("native_libraries_loaded") == 0
        and document.get("hidden_cases_read") == 0
        and document.get("clock_samples") == 0
        and document.get("timing_trials_run") == 0
        and document.get("performance") == "NOT MEASURED"
        and document.get("memory") == "NOT MEASURED"
        and document.get("holdout") == "NOT OPENED"
        and document.get("winner_selected") is False,
        "reject a forged Rust V12 build or mistake a source build "
        "for matching qualification",
    )
    publication = document.get("archive_publication")
    need(
        type(publication) is dict
        and publication.get("path") == str(ROOT / archive.path)
        and publication.get("sha256") == archive.sha256
        and publication.get("bytes") == archive.size
        and publication.get("exclusive_creation") is True
        and publication.get("same_inode_readback_verified") is True
        and publication.get("file_fsync_completed") is True,
        "authenticate the actual compressed V12 build owner without "
        "decompressing it",
    )
    need(receipt.size == 2109,
         "reject the exact V12 durable publication receipt size")


def verify_frozen_context(source_pin: str, protocol_pin: str,
                          contract_pin: str) -> dict[str, Any]:
    authenticate_freeze(source_pin, protocol_pin, contract_pin)
    for owner in (
        GOAL, ORIGINAL_PROTOCOL, ORIGINAL_VERIFIER, UPSTREAM_TEST,
        SIX_FAMILY_PRODUCER,
    ):
        read_owner(owner)
    original = decode_json(read_owner(ORIGINAL_INVENTORY),
                           "unchanged original Phase 1 inventory")
    validate_original_inventory(original)
    installed = read_owner(INSTALLED_RE, external=True)
    need(
        b"sub.__text_signature__" in installed
        and b"subn.__text_signature__" in installed
        and b"split.__text_signature__" in installed,
        "retain the actual installed CPython public introspection witnesses",
    )
    overview_raw = [read_owner(owner) for owner in OVERVIEW]
    validate_overview(
        decode_json(overview_raw[1], "historical V30 graph inputs"),
        decode_json(overview_raw[2], "historical V30 graph summary"),
    )
    read_owner(RUST_V12_SOURCE_BUILD[0])
    receipt = decode_json(
        read_owner(RUST_V12_SOURCE_BUILD[1]),
        "actual released Rust V12 source-build receipt",
    )
    validate_rust_v12_receipt(receipt)
    return {
        "schema": SCHEMA + "-actual-read-only-frozen-context",
        "status": "PASS", "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "original_case_denominator": ORIGINAL_CASE_COUNT,
        "original_suite_count": ORIGINAL_SUITE_COUNT,
        "original_private_waiver_count": ORIGINAL_PRIVATE_WAIVER_COUNT,
        "additional_case_count": ADDITIVE_CASE_COUNT,
        "additional_category_counts": {
            "module": 11, "pattern": 18, "match": 14, "scanner": 7,
        },
        "additional_matrix_sha256": validate_matrix(case_matrix()),
        "historical_v30_repository_evidence_owner_count": (
            V30_EVIDENCE_OWNER_COUNT
        ),
        "historical_v30_authenticated_history_reference_count": (
            V30_HISTORY_REFERENCE_COUNT
        ),
        "repository_evidence_owner_count": PUBLISHED_EVIDENCE_OWNER_COUNT,
        "authenticated_history_reference_count": (
            PUBLISHED_HISTORY_REFERENCE_COUNT
        ),
        "actual_rust_v12_source_build_owner_count": 2,
        "actual_rust_v12_source_build_status": "PASS",
        "actual_rust_v12_candidate_correctness": "NOT MEASURED",
        "actual_rust_v12_source_build_archive_sha256": (
            RUST_V12_SOURCE_BUILD[0].sha256
        ),
        "actual_rust_v12_source_build_receipt_sha256": (
            RUST_V12_SOURCE_BUILD[1].sha256
        ),
        "rust_semantic_mismatch_count": 1087,
        "c_semantic_mismatch_count": 1230,
        "zig_semantic_mismatch_count": 2172,
        "installed_cpython_re_sha256": INSTALLED_RE.sha256,
        "authenticated_frozen_context_owner_count": 13,
        "authenticated_source_freeze_owner_count": 3,
        **boundaries(authenticated_build_archive_count=1),
    }


def reference_worker(role: str, source_pin: str, protocol_pin: str,
                     contract_pin: str) -> dict[str, Any]:
    need(role in ("reference-a", "reference-b"),
         "require an exact independently named Python reference role")
    verify_frozen_context(source_pin, protocol_pin, contract_pin)
    reference = importlib.import_module("re")
    need(os.path.abspath(reference.__file__) == INSTALLED_RE.path,
         "never substitute another standard-library matching reference")
    records = observe_engine(reference)
    need(not any(name == "candidates" or name.startswith("candidates.")
                 for name in sys.modules),
         "never run candidate matching in a standard-library reference")
    document = {
        "schema": SCHEMA + "-reference-worker", "status": "PASS",
        "role": role, "actual_process_id": os.getpid(),
        "original_case_denominator": ORIGINAL_CASE_COUNT,
        "additional_case_count": ADDITIVE_CASE_COUNT,
        "record_vector_sha256": validate_observations(records),
        "records": records, "candidate_imports": 0,
        "hidden_cases_read": 0, "performance": "NOT MEASURED",
    }
    validate_reference_worker(document, role)
    return document


def run_reference(source_pin: str, protocol_pin: str,
                  contract_pin: str) -> dict[str, Any]:
    verify_frozen_context(source_pin, protocol_pin, contract_pin)
    workers: list[dict[str, Any]] = []
    streams: list[dict[str, Any]] = []
    for role in ("reference-a", "reference-b"):
        arguments = (
            PINNED_PYTHON, "-I", "-B", str(ROOT / SOURCE_RELATIVE),
            "--reference-worker", "--reference-role", role,
            "--source-sha256", source_pin,
            "--protocol-sha256", protocol_pin,
            "--contract-sha256", contract_pin,
        )
        process = subprocess.run(arguments, capture_output=True, check=False)
        need(
            type(process.stdout) is bytes and type(process.stderr) is bytes
            and len(process.stdout) <= MAX_WORKER_BYTES
            and len(process.stderr) <= MAX_WORKER_BYTES,
            "preserve bounded complete reference stdout and stderr",
        )
        need(process.returncode == 0,
             "the actual isolated Python reference failed: " + role)
        document = decode_json(process.stdout, role, exact=True)
        validate_reference_worker(document, role)
        workers.append(document)
        streams.append({
            "role": role, "exit_code": process.returncode,
            "stdout_sha256": sha256(process.stdout),
            "stdout_bytes": len(process.stdout),
            "stderr_sha256": sha256(process.stderr),
            "stderr_bytes": len(process.stderr),
            "stdout": process.stdout.decode("utf-8", "strict"),
            "stderr": process.stderr.decode("utf-8", "strict"),
        })
    vector = validate_reference_pair(workers[0], workers[1])
    return {
        "schema": SCHEMA + "-actual-two-reference-baseline",
        "status": "PASS", "python": "3.14.6",
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "original_case_denominator": ORIGINAL_CASE_COUNT,
        "additional_case_count": ADDITIVE_CASE_COUNT,
        "matrix_sha256": validate_matrix(case_matrix()),
        "reference_roles": ["reference-a", "reference-b"],
        "actual_distinct_process_ids": [
            workers[0]["actual_process_id"],
            workers[1]["actual_process_id"],
        ],
        "record_vector_sha256": vector,
        "reference_workers": workers,
        "complete_reference_streams": streams,
        "candidate_workers_started": 0,
        "candidate_imports": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def future_evidence_owner(path: str, digest: str) -> Owner:
    pieces = checked_relative(path)
    need(
        len(pieces) >= 4
        and pieces[:3] == ("oracle", "phase1", "evidence")
        and pieces[-1].endswith(".json")
        and not pieces[-1].endswith(".json.gz"),
        "accept only a separately published, canonical Phase-1 JSON owner",
    )
    return Owner(path, checked_sha256(digest, "future evidence owner"))


def validate_actual_reference(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    need(
        document.get("schema") == SCHEMA + "-actual-two-reference-baseline"
        and document.get("status") == "PASS"
        and document.get("original_case_denominator") == ORIGINAL_CASE_COUNT
        and document.get("additional_case_count") == ADDITIVE_CASE_COUNT
        and document.get("matrix_sha256") == validate_matrix(case_matrix())
        and document.get("candidate_workers_started") == 0
        and document.get("candidate_imports") == 0
        and document.get("hidden_cases_read") == 0
        and document.get("holdout") == "NOT OPENED",
        "reject an unpublished, candidate-tainted, or partial double reference",
    )
    workers = document.get("reference_workers")
    need(type(workers) is list and len(workers) == 2,
         "require both genuine original isolated Python reference workers")
    vector = validate_reference_pair(workers[0], workers[1])
    need(document.get("record_vector_sha256") == vector,
         "reject a substituted full 50-case reference vector")
    return workers[0]["records"]


def validate_core_qualification(value: Mapping[str, Any], family: str) -> None:
    need(
        value.get("status") == "PASS"
        and value.get("family") == family
        and value.get("suite_count") == ORIGINAL_SUITE_COUNT
        and value.get("case_execution_denominator") == ORIGINAL_CASE_COUNT
        and value.get("private_waiver_count")
        == ORIGINAL_PRIVATE_WAIVER_COUNT
        and value.get("semantic_mismatch_count") == 0
        and value.get("infrastructure_failure_count") == 0
        and value.get("candidate_qualified") is True,
        "never start supplementary matching for an unqualified "
        "31,237-case candidate",
    )


def run_candidate(options: argparse.Namespace) -> dict[str, Any]:
    verify_frozen_context(
        options.source_sha256, options.protocol_sha256,
        options.contract_sha256,
    )
    validate_family(options.family, FAMILY_MODULES.get(options.family))
    required = (
        (options.reference_report, options.reference_report_sha256,
         "two-reference baseline"),
        (options.core_report, options.core_report_sha256,
         "full original correctness"),
        (options.independence_report,
         options.independence_report_sha256, "candidate independence"),
    )
    for path, digest, label in required:
        need(type(path) is str and type(digest) is str,
             "require independently published " + label + " evidence")
    reference = decode_json(read_owner(future_evidence_owner(
        options.reference_report, options.reference_report_sha256,
    )), "published two-reference baseline", exact=True)
    expected = validate_actual_reference(reference)
    core = decode_json(read_owner(future_evidence_owner(
        options.core_report, options.core_report_sha256,
    )), "published full original correctness", exact=True)
    validate_core_qualification(core, options.family)
    proof = decode_json(read_owner(future_evidence_owner(
        options.independence_report, options.independence_report_sha256,
    )), "published independent candidate ownership", exact=True)
    validate_independence_proof(proof, options.family)
    need(not any(root in sys.modules for root in FORBIDDEN_EXTERNAL_ROOTS),
         "reject a preloaded external regular-expression engine")
    module = importlib.import_module(FAMILY_MODULES[options.family])
    need(not any(root in sys.modules for root in FORBIDDEN_EXTERNAL_ROOTS),
         "reject candidate delegation to an external regex engine")
    actual = observe_engine(module)
    failures = [
        {
            "id": observed["id"],
            "expected": baseline["observation"],
            "actual": observed["observation"],
        }
        for baseline, observed in zip(expected, actual, strict=True)
        if baseline["observation"] != observed["observation"]
    ]
    return {
        "schema": SCHEMA + "-actual-candidate-result",
        "status": "PASS" if not failures else "FAIL",
        "family": options.family,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "contract_sha256": options.contract_sha256,
        "original_case_denominator": ORIGINAL_CASE_COUNT,
        "additional_case_count": ADDITIVE_CASE_COUNT,
        "matrix_sha256": validate_matrix(case_matrix()),
        "reference_report_sha256": options.reference_report_sha256,
        "core_report_sha256": options.core_report_sha256,
        "independence_report_sha256": options.independence_report_sha256,
        "actual_record_vector_sha256": validate_observations(actual),
        "actual_candidate_case_count": len(actual),
        "semantic_mismatch_count": len(failures),
        "failures": failures,
        "fallback_used": False,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def parse_arguments(arguments: Sequence[str] | None = None
                    ) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    switches = [value for value in values if value.startswith("--")]
    need(len(switches) == len(set(switches)),
         "reject duplicated or ambiguous additive oracle authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run-reference", action="store_true")
    modes.add_argument("--reference-worker", action="store_true")
    modes.add_argument("--run-candidate", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--reference-role")
    parser.add_argument("--family")
    parser.add_argument("--reference-report")
    parser.add_argument("--reference-report-sha256")
    parser.add_argument("--core-report")
    parser.add_argument("--core-report-sha256")
    parser.add_argument("--independence-report")
    parser.add_argument("--independence-report-sha256")
    options = parser.parse_args(values)
    checked_sha256(options.source_sha256, "additive source")
    checked_sha256(options.protocol_sha256, "additive protocol")
    if options.emit_contract:
        need(options.contract_sha256 is None,
             "contract rendering cannot guess its own SHA-256")
    else:
        checked_sha256(options.contract_sha256, "additive contract")
    candidate_values = (
        options.family, options.reference_report,
        options.reference_report_sha256, options.core_report,
        options.core_report_sha256, options.independence_report,
        options.independence_report_sha256,
    )
    if options.run_candidate:
        need(all(value is not None for value in candidate_values),
             "candidate execution requires all independent proof pins")
        need(options.reference_role is None,
             "never mix a candidate and reference role")
    else:
        need(all(value is None for value in candidate_values),
             "source-only and reference modes never authorize candidates")
    if options.reference_worker:
        need(options.reference_role in ("reference-a", "reference-b"),
             "require one exact isolated original Python reference role")
    else:
        need(options.reference_role is None,
             "never pass a reference worker role to another mode")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        runtime()
        options = parse_arguments(arguments)
        authenticate_freeze(
            options.source_sha256, options.protocol_sha256,
            options.contract_sha256,
        )
        if options.emit_contract:
            result = contract_document(
                options.source_sha256, options.protocol_sha256,
            )
        elif options.self_test:
            result = self_test(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256,
            )
        elif options.verify_frozen_context:
            result = verify_frozen_context(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256,
            )
        elif options.reference_worker:
            result = reference_worker(
                options.reference_role, options.source_sha256,
                options.protocol_sha256, options.contract_sha256,
            )
        elif options.run_reference:
            result = run_reference(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256,
            )
        else:
            result = run_candidate(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0
    except (
        IntrospectionError, OSError, ValueError, TypeError, UnicodeError,
        RecursionError, OverflowError, AttributeError, KeyError,
        json.JSONDecodeError,
    ) as exc:
        sys.stderr.write(
            "Python regex callable introspection v1 rejected: "
            + str(exc) + "\n",
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
