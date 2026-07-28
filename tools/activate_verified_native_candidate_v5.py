#!/usr/bin/env python3
"""Freeze and, only when separately requested, reversibly activate V8 C."""

from __future__ import annotations

import ast
import builtins
import copy
import ctypes
import gzip
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
import types
import zlib
from typing import Any


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SCHEMA = "rebar-phase2-verified-native-activation-v5"
SELF = "tools/activate_verified_native_candidate_v5.py"
PROTOCOL = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V5.md"
CONTRACT = "oracle/phase2/verified-native-activation-v5.json"
FAMILY = "c"
EXTENSION = "_vm_native.cpython-314-x86_64-linux-gnu.so"
TARGET = "candidates/" + EXTENSION
ACTIVATION_PREFIX = "rebar-phase2-native-activation-v5-c-"
BUILD_PREFIX = "rebar-phase2-native-build-v8-c-"
EVIDENCE = "oracle/phase2/evidence"
MAX_SOURCE = 8 * 1024 * 1024
MAX_BINARY = 256 * 1024 * 1024
MAX_REPORT = 48 * 1024 * 1024
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_LABEL = 48
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols", "extension_sections",
    "extension_notes",
)
SUITES = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)
MANIFEST = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
V8 = {
    "source": (
        "tools/reproduce_owned_native_source_build_v8.py",
        "afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4",
        63656,
    ),
    "protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILD-V8.md",
        "376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2",
        4498,
    ),
    "contract": (
        "oracle/phase2/native-source-build-v8.json",
        "7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b",
        6207,
    ),
}
REPAIR = {
    "source": (
        "tools/apply_owned_first_party_source_repair_v1.py",
        "c04bbc8e7bc45bdbe1fb9eb93942286f5b32b39aef554db15b8b1acd9cc8cd99",
        45783,
    ),
    "protocol": (
        "oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md",
        "1a2e83caaca5cb43fc82445c2a4fc3097bc3d51bdfc568783b8815797b8c63f5",
        4308,
    ),
    "contract": (
        "oracle/phase2/first-party-source-repair-v1.json",
        "8f1a5676bbef5f2ef560d03fef910bf4ed3a4df029ecc0c638e3fa971206dab5",
        5650,
    ),
}
ORIGINAL = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218185,
)
ADAPTER = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60707,
)
DERIVED_SHA256 = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
DERIVED_BYTES = 218308
V19 = {
    "overview_renderer": (
        "tools/render_candidate_current_overview_v19.py",
        "8144272f7c91e3821306a4d3963c8e201c68b275cecacf80d5000dd98c502494",
        38801,
    ),
    "overview_inputs": (
        "docs/evidence/candidate-current-overview-v19.inputs.json",
        "8f1eb51ff477f0b59934ee503d9bf795f472fd6674180e2af244c7ad4504560c",
        2264,
    ),
    "overview_summary": (
        "docs/evidence/candidate-current-overview-v19.json",
        "504de87d091c555eb53d664fbfaaa70660ff4dd2f9abc22803246f8a5e18287f",
        64819,
    ),
}
BOUNDARY = {
    "actual_v5_activations": "NOT RUN",
    "actual_v8_builds": "NOT RUN",
    "candidate_correctness": "NOT MEASURED",
    "candidate_imports": 0,
    "candidate_processes_started": 0,
    "canonical_promotions": 0,
    "clock_samples": 0,
    "compiler_processes_started": 0,
    "final_comparison_cases_generated": False,
    "final_comparison_planned_case_count": 4194304,
    "final_holdout_authorized": False,
    "hidden_cases_read": 0,
    "holdout": "NOT OPENED",
    "holdout_opened": False,
    "memory": "NOT MEASURED",
    "native_builds_started": 0,
    "native_libraries_loaded": 0,
    "network_requests": 0,
    "performance": "NOT MEASURED",
    "performance_files_read": 0,
    "qualified_candidate_count": 0,
    "recovery_roots_created": 0,
    "source_apply_count": 0,
    "timing_trials_run": 0,
    "undefined_behavior": "NOT MEASURED",
    "winner_selected": False,
}


class ActivationError(Exception):
    """Reject changed, incomplete, non-owned, or unsafe activation evidence."""


class SourceOnlyEffect(ActivationError):
    """A synthetic-only gate attempted to perform a real external effect."""


def require(condition: Any, reason: str) -> None:
    if condition is not True:
        raise ActivationError(reason)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete, genuine byte evidence")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False,
            ).encode("ascii") + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise ActivationError("require a complete finite canonical JSON document") from error


def machine_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, sort_keys=True, indent=2,
                ensure_ascii=True, allow_nan=False,
            ).encode("ascii") + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise ActivationError("require one exact deterministic machine contract") from error


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require an exact lowercase SHA-256 for " + label,
    )
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512, "invalid owner path")
    path = PurePosixPath(value)
    require(
        not path.is_absolute() and str(path) == value
        and all(part not in ("", ".", "..") for part in path.parts)
        and len(path.parts) <= 12,
        "reject an absolute, traversing, ambiguous, or substituted owner",
    )
    return value


def owner(specification: tuple[str, str, int]) -> dict[str, Any]:
    return {
        "bytes": specification[2],
        "path": specification[0],
        "sha256": specification[1],
    }


def expected_contract() -> dict[str, Any]:
    return {
        "activation_policy": {
            "accepted_family": "c",
            "actual_v8_build_required": True,
            "adjacent_backup": "SAME-DIRECTORY ORIGINAL INODE; NEVER A BYTE COPY",
            "canonical_target": TARGET,
            "candidate_source_mutation": "FORBIDDEN",
            "completed_report_requirement": (
                "TWO ACTUAL INDEPENDENT PRIVATE PHASES AND A DISTINCT DURABLE RECEIPT"
            ),
            "external_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "group_atomic": False,
            "hardlinks": "FORBIDDEN FOR ORIGINAL, BACKUP, STAGE, AND PROMOTED TARGET",
            "native_output": "COMPLETE BYTE-IDENTICAL AUTHENTICATED C ELF",
            "network": "FORBIDDEN",
            "original_inode_restoration": "EXACT DEVICE, INODE, MODE, CONTENT, AND OWNER",
            "private_directory_mode": "0700",
            "private_native_file_mode": "0700",
            "private_root_prefix": "/tmp/" + ACTIVATION_PREFIX,
            "private_source_and_evidence_file_mode": "0600",
            "promotion": "INDIVIDUALLY ATOMIC; NEVER GROUP-ATOMIC",
            "recovery": "DURABLE JOURNAL AND EACH PRE-OPERATION INTENTION",
            "recovery_without_activation_report": True,
            "stdlib_regex_engine": "FORBIDDEN",
            "v8_compiler_process_count": 14,
            "v8_independent_source_phase_count": 2,
        },
        "family": FAMILY,
        "first_party_source_repair": {
            "adapter": owner(ADAPTER),
            "derived_c_source": {
                "bytes": DERIVED_BYTES,
                "materialized_during_activation_freeze": False,
                "path": ORIGINAL[0],
                "sha256": DERIVED_SHA256,
            },
            "original_c_source": owner(ORIGINAL),
            "owners": {key: owner(value) for key, value in REPAIR.items()},
        },
        "frozen_v8_source_build": {
            key: owner(value) for key, value in V8.items()
        },
        "historical_v19": {
            "actual_activation_count": 3,
            "actual_candidate_and_native_evidence_owner_count": 71,
            "authenticated_digest_addressed_history_paths": 76,
            "cpp_inclusive_evidence_owner_count": 55,
            "current_active_target_count": 0,
            "go_full_campaign_infrastructure_failure_count": 4,
            "go_full_campaign_semantic_mismatch_count": 4518,
            "go_full_campaign_status": "FAIL",
            "go_restoration_status": "PASS",
            "original_source_owner_count": 25,
            **{key: owner(value) for key, value in V19.items()},
            "qualified_candidate_count": 0,
        },
        "oracle": {
            "case_execution_count": 31237,
            "implementation": "CPython",
            "manifest": owner(MANIFEST),
            "private_waiver_count": 13,
            "python": {"path": PYTHON, "sha256": PYTHON_SHA256},
            "suite_count": 13,
            "suite_ids": list(SUITES),
            "version": "3.14.6",
        },
        "phase": "ACTIVATION FREEZE; NO V8 BUILD, CANDIDATE RUN, OR PROMOTION",
        "phase_boundary": copy.deepcopy(BOUNDARY),
        "schema": SCHEMA + "-source-freeze",
        "version": 5,
    }


def validate_contract(document: Any) -> dict[str, Any]:
    require(
        type(document) is dict
        and canonical(document) == canonical(expected_contract()),
        "reject a weakened, incomplete, cross-family, or altered V5 C-only contract",
    )
    return document


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result, "reject a duplicate JSON key")
        result[key] = value
    return result


def strict_document(raw: bytes, label: str, *, canonical_required: bool) -> dict[str, Any]:
    require(type(raw) is bytes and bool(raw), "require a complete " + label)
    try:
        document = json.loads(
            raw,
            object_pairs_hook=unique_pairs,
            parse_constant=lambda _value: (_ for _ in ()).throw(
                ActivationError("reject a nonfinite " + label),
            ),
        )
    except (UnicodeError, ValueError, TypeError, RecursionError) as error:
        raise ActivationError("reject invalid " + label + " JSON") from error
    require(type(document) is dict, "require a JSON object for " + label)
    if canonical_required:
        require(canonical(document) == raw, "reject noncanonical " + label)
    return document


def directory_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )


def validate_private_file_mode(mode: Any, *, native: bool) -> int:
    require(type(native) is bool, "explicitly distinguish private source from native ELF")
    expected = 0o700 if native else 0o600
    require(
        type(mode) is int and mode == expected,
        "require an exact owner-only "
        + ("0700 compiler-produced native ELF" if native else "0600 private source or evidence"),
    )
    return mode


def read_owned(
    root: str,
    relative: str,
    expected: str | None,
    *,
    maximum: int,
    exact_size: int | None = None,
    private: bool = False,
    native: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    if expected is not None:
        checked_digest(expected, relative)
    require(
        type(maximum) is int and 0 < maximum <= MAX_BINARY
        and type(private) is bool and type(native) is bool
        and (not native or private)
        and (exact_size is None or type(exact_size) is int and 0 <= exact_size <= maximum),
        "bound complete authenticated V5 source, evidence, and native bytes",
    )
    opened: list[int] = []
    try:
        parent = os.open(root, directory_flags())
        opened.append(parent)
        root_info = os.fstat(parent)
        require(stat.S_ISDIR(root_info.st_mode), "reject an aliased owner root")
        if private:
            require(
                root_info.st_uid == os.geteuid()
                and stat.S_IMODE(root_info.st_mode) == 0o700,
                "reject a non-private, foreign, or substituted source-build root",
            )
        parts = PurePosixPath(relative).parts
        for component in parts[:-1]:
            parent = os.open(component, directory_flags(), dir_fd=parent)
            opened.append(parent)
            info = os.fstat(parent)
            require(stat.S_ISDIR(info.st_mode), "reject a redirected owner parent")
            if private:
                require(
                    info.st_uid == os.geteuid()
                    and stat.S_IMODE(info.st_mode) == 0o700,
                    "reject a non-private or cross-phase source directory",
                )
        descriptor = os.open(
            parts[-1],
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent,
        )
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
            and before.st_nlink == 1 and named.st_nlink == 1
            and before.st_uid == os.geteuid()
            and (before.st_dev, before.st_ino) == (named.st_dev, named.st_ino)
            and 0 < before.st_size <= maximum
            and (exact_size is None or before.st_size == exact_size),
            "reject a symlink, hardlink, foreign, incomplete, or replaced " + relative,
        )
        if private:
            validate_private_file_mode(stat.S_IMODE(before.st_mode), native=native)
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(chunk), "reject truncated complete owner bytes")
            pieces.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "reject concealed extra owner bytes")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        require(
            (
                before.st_dev, before.st_ino, before.st_size,
                before.st_mtime_ns, before.st_ctime_ns, before.st_nlink,
            ) == (
                after.st_dev, after.st_ino, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns, after.st_nlink,
            )
            and (expected is None or sha256(raw) == expected),
            "reject a concurrently changed or misidentified " + relative,
        )
        return raw, {
            "bytes": len(raw),
            "device": before.st_dev,
            "inode": before.st_ino,
            "mode": stat.S_IMODE(before.st_mode),
            "nlink": before.st_nlink,
            "path": root.rstrip("/") + "/" + relative,
            "relative": relative,
            "sha256": sha256(raw),
            "uid": before.st_uid,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def load_frozen_module(name: str, specification: tuple[str, str, int]) -> types.ModuleType:
    raw, _ = read_owned(
        ROOT, specification[0], specification[1],
        maximum=MAX_SOURCE, exact_size=specification[2],
    )
    require(name not in sys.modules, "reject a preloaded or substituted source-only kernel")
    module = types.ModuleType(name)
    module.__dict__["__file__"] = ROOT + "/" + specification[0]
    module.__dict__["__package__"] = None
    exec(compile(raw, module.__dict__["__file__"], "exec"), module.__dict__)
    return module


def verify_runtime() -> None:
    require(
        sys.executable == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and sys.version_info[:3] == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
        "use only isolated, bytecode-free, pinned stable CPython 3.14.6",
    )


def validate_adapter(raw: bytes) -> None:
    try:
        document = ast.parse(raw.decode("utf-8", "strict"), filename=ADAPTER[0])
    except (SyntaxError, UnicodeError) as error:
        raise ActivationError("reject an invalid independent C adapter") from error
    own_import = False
    forbidden = {"re", "_sre", "sre_compile", "sre_parse", "regex", "re2", "pcre"}
    for node in ast.walk(document):
        if isinstance(node, ast.Import):
            for alias in node.names:
                require(alias.name.split(".", 1)[0] not in forbidden, "reject an external regex engine")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            require(module.split(".", 1)[0] not in forbidden, "reject indirect stdlib regex delegation")
            if module == "candidates":
                for alias in node.names:
                    require(alias.name == "_vm_native", "reject cross-family native delegation")
                    own_import = True
            elif module.startswith("candidates."):
                raise ActivationError("reject another candidate's parser, compiler, or executor")
        elif isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name):
                require(function.id not in {"__import__", "eval", "exec"}, "reject computed engine delegation")
            elif isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name):
                require(
                    (function.value.id, function.attr) not in {
                        ("importlib", "import_module"), ("ctypes", "CDLL"),
                        ("ctypes", "PyDLL"), ("os", "system"),
                        ("os", "popen"), ("subprocess", "run"),
                        ("subprocess", "Popen"),
                    },
                    "reject dynamic, external, or process-based matcher delegation",
                )
    require(own_import, "the original adapter must import only its original C extension")


def verify_frozen_context(arguments: dict[str, Any]) -> dict[str, Any]:
    verify_runtime()
    observed: dict[str, dict[str, Any]] = {}
    for key, relative in (("source", SELF), ("protocol", PROTOCOL), ("contract", CONTRACT)):
        digest = checked_digest(arguments.get("activation_" + key + "_sha256"), "V5 " + key)
        raw, current = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE)
        observed[key] = current
        if key == "contract":
            document = strict_document(raw, "V5 machine contract", canonical_required=False)
            validate_contract(document)
            require(raw == machine_bytes(document), "reject nondeterministic V5 contract formatting")
    for key, specification in V8.items():
        require(
            checked_digest(arguments.get("build_" + key + "_sha256"), "V8 " + key)
            == specification[1],
            "independently caller-pin the exact frozen V8 " + key,
        )
    v8 = load_frozen_module("_rebar_phase2_exact_v5_activation_v8", V8["source"])
    context = v8.verify_context({
        "source_sha256": V8["source"][1],
        "protocol_sha256": V8["protocol"][1],
        "contract_sha256": V8["contract"][1],
    })
    require(
        type(context) is dict and context.get("status") == "PASS"
        and context.get("family") == FAMILY
        and context.get("source_family_count") == 6
        and context.get("original_source_owner_count") == 25
        and context.get("authenticated_digest_addressed_history_paths") == 76
        and context.get("authoritative_counted_evidence_owner_count") == 71
        and context.get("go_full_campaign_status") == "FAIL"
        and context.get("go_full_campaign_semantic_mismatch_count") == 4518
        and context.get("go_full_campaign_infrastructure_failure_count") == 4
        and context.get("go_restoration_status") == "PASS"
        and context.get("qualified_candidate_count") == 0
        and context.get("holdout") == "NOT OPENED"
        and context.get("clock_samples") == 0
        and context.get("candidate_processes_started") == 0
        and context.get("compiler_processes_started") == 0,
        "reject a changed V8 source freeze, full owner closure, or original failed history",
    )
    summary_raw, summary_owner = read_owned(
        ROOT, V19["overview_summary"][0], V19["overview_summary"][1],
        maximum=MAX_SOURCE, exact_size=V19["overview_summary"][2],
    )
    summary = strict_document(summary_raw, "original V19 overview", canonical_required=True)
    snapshot = summary.get("snapshot")
    require(
        type(snapshot) is dict
        and snapshot.get("preserved_v18_verified_activation_v4_actual_activation_count") == 2
        and snapshot.get("verified_activation_v4_actual_activation_count") == 3
        and snapshot.get("verified_activation_v4_current_active_target_count") == 0
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 71
        and snapshot.get("all_actual_candidate_and_cpp_evidence_owner_count") == 55
        and snapshot.get("current_source_owner_count") == 25
        and snapshot.get("qualified_candidate_count") == 0,
        "preserve all three actual restored V4 activations; never reset history to zero",
    )
    adapter, _ = read_owned(
        ROOT, ADAPTER[0], ADAPTER[1], maximum=MAX_SOURCE, exact_size=ADAPTER[2],
    )
    validate_adapter(adapter)
    return {
        "schema": SCHEMA + "-read-only-context",
        "status": "PASS",
        "version": 5,
        "family": FAMILY,
        "activation_source": observed["source"],
        "activation_protocol": observed["protocol"],
        "activation_contract": observed["contract"],
        "v8_source_context": context,
        "v19_overview": summary_owner,
        "historical_actual_v4_activation_count": 3,
        "historical_current_active_target_count": 0,
        "original_source_owner_count": 25,
        "authoritative_counted_evidence_owner_count": 71,
        "authenticated_digest_addressed_history_paths": 76,
        "read_only": True,
        **copy.deepcopy(BOUNDARY),
    }


def checked_label(value: Any) -> str:
    require(
        type(value) is str and 0 < len(value) <= MAX_LABEL
        and all(character.isascii() and (character.isalnum() or character in "-_") for character in value),
        "require one exact bounded genuine V8 evidence label",
    )
    return value


def checked_private_root(value: Any, prefix: str) -> str:
    require(
        type(value) is str and value.startswith("/tmp/" + prefix)
        and len(value) <= 512 and value == value.rstrip("/")
        and len(value.split("/")) == 3
        and all(
            character.isascii() and (character.isalnum() or character in "-_")
            for character in value.rsplit("/", 1)[1]
        ),
        "reject a foreign, traversing, cross-family, or incorrect-version private root",
    )
    return value


def checked_native_size(value: Any) -> int:
    require(
        type(value) is str and value.isascii() and value.isdecimal()
        and value == str(int(value)) and 0 < int(value) <= MAX_BINARY,
        "caller-pin an exact bounded complete native C ELF byte count",
    )
    return int(value)


def parse_arguments(arguments: Any) -> dict[str, Any]:
    require(
        type(arguments) is list and all(type(value) is str for value in arguments),
        "require one complete explicit source-only, activation, or recovery command",
    )
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(
        bool(arguments)
        and arguments[0] in {"--verify-frozen-context", "--activate", "--recover", "--restore"},
        "explicitly select only a frozen gate, C activation, or journal recovery",
    )
    mode = arguments[0][2:]
    common = {
        "--activation-source-sha256": "activation_source_sha256",
        "--activation-protocol-sha256": "activation_protocol_sha256",
        "--activation-contract-sha256": "activation_contract_sha256",
        "--build-source-sha256": "build_source_sha256",
        "--build-protocol-sha256": "build_protocol_sha256",
        "--build-contract-sha256": "build_contract_sha256",
    }
    mapping = dict(common)
    if mode == "activate":
        mapping.update({
            "--family": "family", "--build-label": "build_label",
            "--build-root": "build_root",
            "--build-report-sha256": "build_report_sha256",
            "--build-receipt-sha256": "build_receipt_sha256",
            "--native-sha256": "native_sha256",
            "--native-bytes": "native_bytes",
        })
    elif mode in {"recover", "restore"}:
        mapping.update({
            "--family": "family", "--activation-root": "activation_root",
            "--recovery-journal-sha256": "recovery_journal_sha256",
        })
    result: dict[str, Any] = {"mode": mode}
    if mode == "activate":
        result["owned_source_sha256"] = []
    position = 1
    while position < len(arguments):
        require(position + 1 < len(arguments), "reject a missing independently pinned flag value")
        flag, value = arguments[position], arguments[position + 1]
        if flag == "--owned-source-sha256" and mode == "activate":
            result["owned_source_sha256"].append(value)
        else:
            require(flag in mapping and mapping[flag] not in result, "reject a repeated or foreign activation flag")
            result[mapping[flag]] = value
        position += 2
    expected = {"mode", *mapping.values()}
    if mode == "activate":
        expected.add("owned_source_sha256")
    require(set(result) == expected, "independently caller-pin every complete V5 and V8 owner")
    for key, value in result.items():
        if key.endswith("_sha256") and key != "owned_source_sha256":
            checked_digest(value, key)
    if mode == "activate":
        require(result["family"] == FAMILY, "activate only the first-party C family")
        checked_label(result["build_label"])
        checked_private_root(result["build_root"], BUILD_PREFIX)
        require(
            len(result["owned_source_sha256"]) == 2
            and set(result["owned_source_sha256"]) == {
                ORIGINAL[0] + "=" + ORIGINAL[1],
                ADAPTER[0] + "=" + ADAPTER[1],
            },
            "caller-pin both complete unchanged original first-party C source owners",
        )
        result["native_size"] = checked_native_size(result["native_bytes"])
    elif mode in {"recover", "restore"}:
        require(result["family"] == FAMILY, "recover only the approved C target")
        checked_private_root(result["activation_root"], ACTIVATION_PREFIX)
    return result


def decompress_report(raw: bytes) -> bytes:
    require(
        type(raw) is bytes and 10 <= len(raw) <= MAX_ARCHIVE
        and raw[:3] == b"\x1f\x8b\x08" and raw[4:8] == b"\x00\x00\x00\x00",
        "require exactly one deterministic, bounded V8 gzip archive",
    )
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        plain = decoder.decompress(raw, MAX_REPORT + 1)
        require(
            decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
            and 0 < len(plain) <= MAX_REPORT,
            "reject concatenated, truncated, oversized, or trailing V8 gzip members",
        )
    except (zlib.error, EOFError, ValueError) as error:
        raise ActivationError("reject an invalid or incomplete V8 build archive") from error
    require(
        gzip.compress(plain, compresslevel=9, mtime=0) == raw,
        "reject changed deterministic complete V8 archive bytes",
    )
    return plain


def exact_owner_pair(actual: dict[str, Any], recorded: Any) -> bool:
    return (
        type(recorded) is dict
        and actual["device"] == recorded.get("device")
        and actual["inode"] == recorded.get("inode")
        and actual["sha256"] == recorded.get("sha256")
        and actual["bytes"] == (
            recorded.get("bytes")
            if type(recorded.get("bytes")) is int
            else recorded.get("size_bytes")
        )
    )


def validate_report_boundary(document: dict[str, Any], *, receipt: bool) -> None:
    for key, expected in (
        ("candidate_correctness", "NOT MEASURED"),
        ("candidate_processes_started", 0), ("candidate_imports", 0),
        ("native_libraries_loaded", 0), ("hidden_cases_read", 0),
        ("clock_samples", 0), ("timing_trials_run", 0),
        ("performance", "NOT MEASURED"), ("memory", "NOT MEASURED"),
        ("holdout", "NOT OPENED"), ("winner_selected", False),
    ):
        require(
            type(document.get(key)) is type(expected) and document.get(key) == expected,
            "the actual V8 " + ("receipt" if receipt else "report") + " crossed the frozen " + key + " boundary",
        )


def authenticate_v8_evidence(arguments: dict[str, Any]) -> dict[str, Any]:
    context = verify_frozen_context(arguments)
    label = checked_label(arguments["build_label"])
    root = checked_private_root(arguments["build_root"], BUILD_PREFIX)
    base = EVIDENCE + "/native-source-build-v8-c-" + label
    archive, archive_owner = read_owned(
        ROOT, base + ".json.gz", arguments["build_report_sha256"],
        maximum=MAX_ARCHIVE,
    )
    receipt_raw, receipt_owner = read_owned(
        ROOT, base + "-publication-receipt.json", arguments["build_receipt_sha256"],
        maximum=MAX_SOURCE,
    )
    require(
        archive_owner["mode"] == 0o600 and receipt_owner["mode"] == 0o600
        and (archive_owner["device"], archive_owner["inode"])
        != (receipt_owner["device"], receipt_owner["inode"]),
        "require two distinct, owner-only, unlinked actual V8 evidence files",
    )
    plain = decompress_report(archive)
    report = strict_document(plain, "actual passing V8 build report", canonical_required=True)
    receipt = strict_document(receipt_raw, "durable V8 publication receipt", canonical_required=True)
    require(
        report.get("schema") == "rebar-phase2-owned-native-source-build-v8"
        and report.get("version") == 8 and report.get("status") == "PASS"
        and report.get("family") == FAMILY and report.get("label") == label,
        "reject an absent, failed, synthetic, wrong-family, or non-V8 actual build",
    )
    require(
        receipt.get("schema") == "rebar-phase2-owned-native-source-build-v8-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == FAMILY and receipt.get("label") == label,
        "a successful publication receipt cannot turn an absent or failed build into a pass",
    )
    for key, specification in V8.items():
        require(
            report.get(key + "_sha256") == specification[1]
            and receipt.get(key + "_sha256") == specification[1]
            and arguments["build_" + key + "_sha256"] == specification[1],
            "bind actual report, receipt, and caller to the exact V8 " + key,
        )
    require(
        receipt.get("phase1_manifest_sha256") == MANIFEST[1]
        and receipt.get("archive_relative") == base + ".json.gz"
        and receipt.get("archive_sha256") == archive_owner["sha256"]
        and receipt.get("archive_bytes") == archive_owner["bytes"]
        and receipt.get("uncompressed_sha256") == sha256(plain)
        and receipt.get("uncompressed_bytes") == len(plain)
        and exact_owner_pair(archive_owner, receipt.get("archive_publication")),
        "bind the durable V8 receipt to the exact independently authenticated complete archive",
    )
    publication = receipt["archive_publication"]
    directory_sync = receipt.get("archive_directory_fsync")
    require(
        publication.get("exclusive_creation") is True
        and publication.get("same_inode_readback_verified") is True
        and publication.get("file_fsync_completed") is True
        and type(directory_sync) is dict and directory_sync.get("completed") is True
        and receipt.get("receipt_self_publication") == "NOT CLAIMED",
        "require actual exclusive, same-inode, file- and directory-synchronized V8 evidence",
    )
    for document in (report, receipt):
        require(
            document.get("original_source_sha256") == ORIGINAL[1]
            and document.get("derived_source_sha256") == DERIVED_SHA256
            and document.get("derived_source_apply_count") == 2
            and document.get("expected_v8_compiler_process_count") == 14
            and document.get("actual_v8_compiler_process_count") == 14,
            "require both genuine frozen private repaired-source phases and all 14 actual processes",
        )
        validate_report_boundary(document, receipt=document is receipt)
    frozen_context = report.get("frozen_context")
    require(
        type(frozen_context) is dict
        and frozen_context.get("status") == "PASS"
        and frozen_context.get("original_source_owner_count") == 25
        and frozen_context.get("authenticated_digest_addressed_history_paths") == 76
        and frozen_context.get("authoritative_counted_evidence_owner_count") == 71
        and frozen_context.get("derived_source_sha256") == DERIVED_SHA256
        and frozen_context.get("derived_source_bytes") == DERIVED_BYTES,
        "bind the actual build to the separately reverified complete frozen source context",
    )
    phases = report.get("phases")
    steps = report.get("compiler_processes")
    require(
        type(phases) is list and len(phases) == 2
        and [phase.get("name") if type(phase) is dict else None for phase in phases] == list(PHASES)
        and report.get("phase_count") == 2
        and type(steps) is list and len(steps) == 14,
        "require exactly two complete distinct actual V8 phases and 14 compiler processes",
    )
    pids: set[int] = set()
    for index, step in enumerate(steps):
        require(
            type(step) is dict
            and step.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
            and type(step.get("pid")) is int and step["pid"] > 0
            and step["pid"] not in pids and step.get("exit_status") == 0,
            "reject missing, failed, fake, reordered, or repeated actual V8 compiler processes",
        )
        if "phase" in step:
            require(step["phase"] == PHASES[index // len(PROCESS_NAMES)], "reject a cross-phase actual process")
        pids.add(step["pid"])
    v8 = load_frozen_module("_rebar_phase2_exact_v5_activation_elf_v8", V8["source"])
    v7 = v8.load_frozen_module("_rebar_phase2_exact_v5_activation_elf_v7", v8.V7_OWNERS["source"])
    actual_elf: list[bytes] = []
    phase_owners: set[tuple[int, int]] = set()
    outputs: list[dict[str, Any]] = []
    for index, phase in enumerate(phases):
        recorded_sources = phase.get("fresh_source_owners")
        require(
            type(recorded_sources) is dict and set(recorded_sources) == {ORIGINAL[0], ADAPTER[0]},
            "require both independently owned complete C and adapter snapshots",
        )
        for relative, digest, size in (
            (ORIGINAL[0], DERIVED_SHA256, DERIVED_BYTES),
            (ADAPTER[0], ADAPTER[1], ADAPTER[2]),
        ):
            raw, actual = read_owned(
                root, PHASES[index] + "/source/" + relative,
                digest, maximum=MAX_SOURCE, exact_size=size, private=True,
            )
            recorded = recorded_sources.get(relative)
            require(exact_owner_pair(actual, recorded), "bind every real private source snapshot to its report inode")
            identity = (actual["device"], actual["inode"])
            require(identity not in phase_owners, "reject a reused or cross-linked private source owner")
            phase_owners.add(identity)
            if relative == ORIGINAL[0]:
                overlay = recorded.get("source_overlay")
                require(
                    type(overlay) is dict and overlay.get("status") == "PASS"
                    and overlay.get("phase") == PHASES[index]
                    and overlay.get("source_apply_count") == 1
                    and overlay.get("derived_sha256") == DERIVED_SHA256
                    and overlay.get("derived_bytes") == DERIVED_BYTES,
                    "require exactly one frozen first-party repair in each actual private phase",
                )
            else:
                validate_adapter(raw)
        outputs_record = phase.get("native_outputs")
        require(type(outputs_record) is dict, "require an independently audited actual C output")
        output = outputs_record.get("extension")
        require(
            type(output) is dict and output.get("file_name") == EXTENSION
            and output.get("sha256") == arguments["native_sha256"]
            and output.get("size_bytes") == arguments["native_size"],
            "caller-pin one exact real independently built C extension",
        )
        raw, actual = read_owned(
            root, PHASES[index] + "/native/" + EXTENSION,
            arguments["native_sha256"], maximum=MAX_BINARY,
            exact_size=arguments["native_size"], private=True, native=True,
        )
        require(exact_owner_pair(actual, output), "reject a substituted real V8 native output inode")
        identity = (actual["device"], actual["inode"])
        require(identity not in phase_owners, "reject a hardlinked, reused, or cross-phase C binary")
        phase_owners.add(identity)
        forensics = phase.get("native_forensics")
        require(
            type(forensics) is dict and type(forensics.get("extension")) is dict
            and v7.parse_owned_elf64(raw) == forensics["extension"].get("raw_elf64"),
            "authenticate and independently reparse every complete actual C ELF byte",
        )
        for role in ("sections", "notes"):
            forensic = forensics["extension"].get(role)
            expected_step = steps[index * len(PROCESS_NAMES) + PROCESS_NAMES.index("extension_" + role)]
            require(
                type(forensic) is dict and forensic.get("command") == "extension_" + role
                and forensic.get("process_pid") == expected_step["pid"]
                and type(forensic.get("stdout_sha256")) is str
                and type(forensic.get("stdout_bytes")) is int,
                "bind each actual ELF forensic record to its distinct real process",
            )
            checked_digest(forensic["stdout_sha256"], "actual " + role + " stream")
        outputs.append(output)
        actual_elf.append(raw)
    reproduction = report.get("reproducibility")
    require(
        type(reproduction) is dict and reproduction.get("independent_fresh_phase_count") == 2
        and reproduction.get("derived_source_apply_count") == 2
        and reproduction.get("derived_source_sha256") == DERIVED_SHA256
        and reproduction.get("derived_source_bytes") == DERIVED_BYTES
        and reproduction.get("original_source_modified") is False
        and reproduction.get("byte_identical") is True
        and reproduction.get("unique_process_count") == 14
        and reproduction.get("prebuilt_artifact_count") == 0
        and reproduction.get("native_libraries_loaded") == 0
        and actual_elf[0] == actual_elf[1]
        and outputs[0].get("audit") == outputs[1].get("audit")
        and type(outputs[0].get("audit")) is dict,
        "require genuine first-party, reproducible, independently audited full ELF bytes",
    )
    compared = v7.compare_owned_elf64(actual_elf[0], actual_elf[1])
    require(
        type(compared) is dict and compared.get("byte_identical") is True
        and compared == reproduction.get("raw_elf_comparison"),
        "independently reproduce the original full-ELF comparison",
    )
    reproduced_output = reproduction.get("native_outputs")
    require(
        type(reproduced_output) is dict
        and type(reproduced_output.get("extension")) is dict
        and reproduced_output["extension"].get("file_name") == EXTENSION
        and reproduced_output["extension"].get("sha256") == arguments["native_sha256"]
        and reproduced_output["extension"].get("size_bytes") == arguments["native_size"]
        and reproduced_output["extension"].get("fresh_independent_inode_count") == 2
        and reproduced_output["extension"].get("reproduced_in_two_fresh_directories") is True
        and reproduced_output["extension"].get("audit") == outputs[0]["audit"],
        "bind complete native bytes to both actual reproducibility phases and audits",
    )
    return {
        "context": context,
        "report": report,
        "receipt": receipt,
        "archive_owner": archive_owner,
        "receipt_owner": receipt_owner,
        "native_bytes": actual_elf[0],
        "native_sha256": arguments["native_sha256"],
        "native_size": arguments["native_size"],
    }


def candidate_directory() -> tuple[int, int]:
    root = os.open(ROOT, directory_flags())
    try:
        directory = os.open("candidates", directory_flags(), dir_fd=root)
        info = os.fstat(directory)
        require(
            stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid(),
            "promote only inside the actual owner-controlled candidates directory",
        )
        return root, directory
    except BaseException:
        os.close(root)
        raise


def current_target() -> tuple[bytes, dict[str, Any]] | None:
    root, directory = candidate_directory()
    try:
        try:
            info = os.stat(EXTENSION, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            return None
        require(
            stat.S_ISREG(info.st_mode) and info.st_nlink == 1
            and info.st_uid == os.geteuid(),
            "never overwrite a user-owned, hardlinked, dangling, directory, or symlink target",
        )
        return read_owned(ROOT, TARGET, None, maximum=MAX_BINARY)
    finally:
        os.close(directory)
        os.close(root)


def same_owner(first: Any, second: Any) -> bool:
    return (
        type(first) is dict and type(second) is dict
        and all(first.get(key) == second.get(key) for key in (
            "device", "inode", "mode", "nlink", "uid", "bytes", "sha256",
        ))
    )


def synchronize_root(root: str) -> dict[str, Any]:
    descriptor = os.open(root, directory_flags())
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISDIR(before.st_mode) and before.st_uid == os.geteuid()
            and stat.S_IMODE(before.st_mode) == 0o700,
            "synchronize only the independently owned private V5 recovery root",
        )
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino),
            "reject a swapped private recovery directory",
        )
        return {"completed": True, "device": after.st_dev, "inode": after.st_ino}
    finally:
        os.close(descriptor)


def write_private(root: str, filename: str, raw: bytes) -> dict[str, Any]:
    checked_relative(filename)
    require("/" not in filename and type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE, "bound exact V5 private evidence")
    directory = os.open(root, directory_flags())
    descriptor: int | None = None
    try:
        info = os.fstat(directory)
        require(
            stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
            and stat.S_IMODE(info.st_mode) == 0o700,
            "publish only inside a real owner-only recovery directory",
        )
        descriptor = os.open(
            filename,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
            and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600,
            "require an exclusive, unlinked, owner-only durable journal inode",
        )
        offset = 0
        while offset < len(raw):
            amount = os.write(descriptor, raw[offset:])
            require(type(amount) is int and amount > 0, "reject partial recovery evidence")
            offset += amount
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_nlink)
            and after.st_size == len(raw),
            "reject a replaced or incomplete synchronized journal",
        )
        os.close(descriptor)
        descriptor = None
        os.fsync(directory)
        _, recorded = read_owned(
            root, filename, sha256(raw), maximum=MAX_SOURCE,
            exact_size=len(raw), private=True,
        )
        require(
            (recorded["device"], recorded["inode"]) == (after.st_dev, after.st_ino),
            "reject journal evidence replaced after file and directory synchronization",
        )
        return {
            **recorded,
            "exclusive_creation": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "same_inode_readback_verified": True,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def adjacent_name(token: str, kind: str) -> str:
    require(
        type(token) is str and len(token) == 36
        and all(character in "0123456789abcdef" for character in token)
        and kind in {"original", "stage"},
        "require one exact, unpredictable, same-directory C-only recovery name",
    )
    result = ".rebar-v5-" + kind + "-" + token + "-" + EXTENSION
    require(len(result) < 240 and "/" not in result, "bound adjacent canonical recovery names")
    return result


def require_absent(directory: int, filename: str) -> None:
    try:
        os.stat(filename, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise ActivationError("never replace a pre-existing, symlinked, or dangling adjacent recovery path")


def stage_native(directory: int, filename: str, content: bytes, mode: int) -> dict[str, Any]:
    require(
        type(content) is bytes and 0 < len(content) <= MAX_BINARY
        and type(mode) is int and 0 <= mode <= 0o777,
        "stage only complete exact source-built C bytes and original permissions",
    )
    descriptor = os.open(
        filename,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        0o600,
        dir_fd=directory,
    )
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and before.st_nlink == 1
            and before.st_uid == os.geteuid(),
            "reject a linked, redirected, or foreign adjacent C staging inode",
        )
        offset = 0
        while offset < len(content):
            amount = os.write(descriptor, content[offset:])
            require(type(amount) is int and amount > 0, "never stage partial native ELF bytes")
            offset += amount
        if mode != 0o600:
            os.fchmod(descriptor, mode)
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_nlink)
            == (after.st_dev, after.st_ino, after.st_nlink)
            and after.st_size == len(content)
            and stat.S_IMODE(after.st_mode) == mode,
            "preserve one complete, fsynced, unlinked adjacent native stage",
        )
    finally:
        os.close(descriptor)
    _, recorded = read_owned(
        ROOT, "candidates/" + filename, sha256(content),
        maximum=MAX_BINARY, exact_size=len(content),
    )
    require(
        (recorded["device"], recorded["inode"]) == (after.st_dev, after.st_ino)
        and recorded["nlink"] == 1 and recorded["mode"] == mode,
        "reject a swapped adjacent stage before canonical promotion",
    )
    os.fsync(directory)
    return recorded


def make_intention(
    root: str, name: str, journal_owner: dict[str, Any],
    operation: str, details: dict[str, Any],
) -> dict[str, Any]:
    return write_private(root, name, canonical({
        "schema": SCHEMA + "-pre-operation-intention",
        "status": "PREPARED",
        "family": FAMILY,
        "operation": operation,
        "activation_root": root,
        "recovery_journal_sha256": journal_owner["sha256"],
        "target": TARGET,
        "details": details,
        "group_atomic": False,
    }))


def validate_intention(
    root: str, filename: str, journal_digest: str, operation: str,
) -> dict[str, Any] | None:
    try:
        raw, _ = read_owned(root, filename, None, maximum=MAX_SOURCE, private=True)
    except FileNotFoundError:
        return None
    document = strict_document(raw, "durable " + operation + " intention", canonical_required=True)
    require(
        document.get("schema") == SCHEMA + "-pre-operation-intention"
        and document.get("status") == "PREPARED"
        and document.get("family") == FAMILY
        and document.get("operation") == operation
        and document.get("activation_root") == root
        and document.get("recovery_journal_sha256") == journal_digest
        and document.get("target") == TARGET
        and document.get("group_atomic") is False
        and type(document.get("details")) is dict,
        "reject an incomplete, cross-root, foreign, or substituted durable pre-operation intention",
    )
    return document


def activate(arguments: dict[str, Any]) -> dict[str, Any]:
    verified = authenticate_v8_evidence(arguments)
    original = current_target()
    token = os.urandom(18).hex()
    backup = adjacent_name(token, "original")
    stage = adjacent_name(token, "stage")
    original_owner = None if original is None else original[1]
    mode = 0o700 if original_owner is None else original_owner["mode"]
    activation_root = tempfile.mkdtemp(prefix=ACTIVATION_PREFIX, dir="/tmp")
    checked_private_root(activation_root, ACTIVATION_PREFIX)
    synchronize_root(activation_root)
    journal = {
        "schema": SCHEMA + "-recovery-journal",
        "status": "PREPARED",
        "version": 5,
        "family": FAMILY,
        "activation_root": activation_root,
        "target": TARGET,
        "original": original_owner,
        "backup_name": backup,
        "stage_name": stage,
        "expected_promoted_sha256": verified["native_sha256"],
        "expected_promoted_bytes": verified["native_size"],
        "expected_promoted_mode": mode,
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "activation_contract_sha256": arguments["activation_contract_sha256"],
        "build_source_sha256": V8["source"][1],
        "build_protocol_sha256": V8["protocol"][1],
        "build_contract_sha256": V8["contract"][1],
        "build_archive_sha256": verified["archive_owner"]["sha256"],
        "build_receipt_sha256": verified["receipt_owner"]["sha256"],
        "original_device_inode_preserved": original_owner is not None,
        "group_atomic": False,
        "reportless_recovery": True,
    }
    journal_owner = write_private(activation_root, "recovery-journal.json", canonical(journal))
    make_intention(
        activation_root, "stage-intent.json", journal_owner, "create-adjacent-stage",
        {"name": stage, "sha256": verified["native_sha256"], "bytes": verified["native_size"], "mode": mode},
    )
    root, directory = candidate_directory()
    try:
        require_absent(directory, stage)
        require_absent(directory, backup)
        actual = current_target()
        require(
            (actual is None and original_owner is None)
            or (actual is not None and same_owner(actual[1], original_owner)),
            "never promote over an unexpectedly created or modified user target",
        )
        staged = stage_native(directory, stage, verified["native_bytes"], mode)
        make_intention(
            activation_root, "stage-observed.json", journal_owner, "authenticated-adjacent-stage",
            {"stage": staged},
        )
        if original_owner is not None:
            make_intention(
                activation_root, "backup-intent.json", journal_owner, "move-original-inode",
                {"original": original_owner, "backup_name": backup},
            )
            actual = current_target()
            require(actual is not None and same_owner(actual[1], original_owner), "the original user inode changed before backup")
            require_absent(directory, backup)
            os.replace(EXTENSION, backup, src_dir_fd=directory, dst_dir_fd=directory)
            os.fsync(directory)
            _, preserved = read_owned(
                ROOT, "candidates/" + backup, original_owner["sha256"],
                maximum=MAX_BINARY, exact_size=original_owner["bytes"],
            )
            require(same_owner(preserved, original_owner), "the exact original user inode was not durably preserved")
            require(current_target() is None, "the individually moved original must leave an absent canonical target")
        else:
            require(current_target() is None, "an originally absent user target unexpectedly appeared")
        make_intention(
            activation_root, "promotion-intent.json", journal_owner, "promote-authenticated-stage",
            {"stage": staged, "original": original_owner, "backup_name": backup},
        )
        _, actual_stage = read_owned(
            ROOT, "candidates/" + stage, verified["native_sha256"],
            maximum=MAX_BINARY, exact_size=verified["native_size"],
        )
        require(same_owner(actual_stage, staged), "the durable promoted stage inode changed")
        require(current_target() is None, "never individually promote over a new or modified user target")
        os.replace(stage, EXTENSION, src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)
        promoted = current_target()
        require(promoted is not None and same_owner(promoted[1], staged), "the individually promoted source-built inode changed")
    finally:
        os.close(directory)
        os.close(root)
    result = {
        "schema": SCHEMA + "-actual-activation",
        "status": "PASS",
        "version": 5,
        "family": FAMILY,
        "activation_root": activation_root,
        "recovery_journal": journal_owner,
        "target": promoted[1],
        "original": original_owner,
        "group_atomic": False,
        "candidate_qualified": False,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    report = write_private(activation_root, "activation-report.json", canonical(result))
    receipt = write_private(activation_root, "activation-receipt.json", canonical({
        "schema": SCHEMA + "-durable-activation-receipt",
        "status": "PASS",
        "activation_status": "PASS",
        "family": FAMILY,
        "activation_root": activation_root,
        "recovery_journal": journal_owner,
        "activation_report": report,
        "target": promoted[1],
        "group_atomic": False,
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }))
    return {**result, "activation_report": report, "activation_receipt": receipt}


def recover(arguments: dict[str, Any]) -> dict[str, Any]:
    verify_frozen_context(arguments)
    root = checked_private_root(arguments["activation_root"], ACTIVATION_PREFIX)
    raw, journal_owner = read_owned(
        root, "recovery-journal.json", arguments["recovery_journal_sha256"],
        maximum=MAX_SOURCE, private=True,
    )
    journal = strict_document(raw, "caller-pinned recovery journal", canonical_required=True)
    require(
        journal.get("schema") == SCHEMA + "-recovery-journal"
        and journal.get("status") == "PREPARED" and journal.get("version") == 5
        and journal.get("family") == FAMILY
        and journal.get("activation_root") == root
        and journal.get("target") == TARGET and journal.get("group_atomic") is False
        and journal.get("reportless_recovery") is True,
        "recover only an authenticated original V5 C-only owner-only journal",
    )
    for key in ("source", "protocol", "contract"):
        require(
            journal.get("activation_" + key + "_sha256") == arguments["activation_" + key + "_sha256"]
            and journal.get("build_" + key + "_sha256") == V8[key][1]
            and arguments["build_" + key + "_sha256"] == V8[key][1],
            "bind reportless recovery to both caller-pinned exact V5 and V8 freezes",
        )
    expected_hash = checked_digest(journal.get("expected_promoted_sha256"), "promoted C target")
    expected_size = journal.get("expected_promoted_bytes")
    expected_mode = journal.get("expected_promoted_mode")
    require(
        type(expected_size) is int and 0 < expected_size <= MAX_BINARY
        and type(expected_mode) is int and 0 <= expected_mode <= 0o777,
        "reject an unbounded or malformed reportless native recovery target",
    )
    original = journal.get("original")
    require(original is None or type(original) is dict and original.get("nlink") == 1, "reject a linked or fabricated original inode")
    backup = journal.get("backup_name")
    stage = journal.get("stage_name")
    require(
        type(backup) is str and type(stage) is str
        and backup.startswith(".rebar-v5-original-")
        and stage.startswith(".rebar-v5-stage-")
        and backup.endswith("-" + EXTENSION) and stage.endswith("-" + EXTENSION)
        and "/" not in backup and "/" not in stage,
        "reject a foreign, traversing, cross-target, or ambiguous adjacent recovery name",
    )
    stage_intent = validate_intention(root, "stage-intent.json", journal_owner["sha256"], "create-adjacent-stage")
    require(stage_intent is not None, "require a durable intention before any adjacent stage")
    details = stage_intent["details"]
    require(
        details.get("name") == stage and details.get("sha256") == expected_hash
        and details.get("bytes") == expected_size and details.get("mode") == expected_mode,
        "bind reportless staging recovery to exact expected bytes and names",
    )
    stage_observed = validate_intention(
        root, "stage-observed.json", journal_owner["sha256"], "authenticated-adjacent-stage",
    )
    backup_intent = validate_intention(
        root, "backup-intent.json", journal_owner["sha256"], "move-original-inode",
    )
    promotion_intent = validate_intention(
        root, "promotion-intent.json", journal_owner["sha256"], "promote-authenticated-stage",
    )
    if original is None:
        require(backup_intent is None, "an originally absent target never has an original backup")
    else:
        require(
            backup_intent is None
            or same_owner(backup_intent["details"].get("original"), original)
            and backup_intent["details"].get("backup_name") == backup,
            "reject a wrong-inode or unjournaled original backup",
        )
    recorded_stage = None if stage_observed is None else stage_observed["details"].get("stage")
    if promotion_intent is not None:
        require(
            recorded_stage is not None
            and same_owner(promotion_intent["details"].get("stage"), recorded_stage)
            and promotion_intent["details"].get("backup_name") == backup
            and (
                original is None and promotion_intent["details"].get("original") is None
                or original is not None and same_owner(promotion_intent["details"].get("original"), original)
            ),
            "reject a promotion without an exact independently durable staged inode",
        )
    repository, directory = candidate_directory()
    removed_promoted = False
    restored_original = False
    removed_stage = False
    try:
        target = current_target()
        try:
            backup_raw, backup_owner = read_owned(
                ROOT, "candidates/" + backup,
                None if original is None else original.get("sha256"),
                maximum=MAX_BINARY,
                exact_size=None if original is None else original.get("bytes"),
            )
        except FileNotFoundError:
            backup_raw, backup_owner = None, None
        if original is None:
            require(backup_owner is None, "never adopt a fabricated original backup")
        elif backup_owner is not None:
            require(
                backup_intent is not None and same_owner(backup_owner, original),
                "never restore a changed, linked, or substituted original user inode",
            )
        if target is not None:
            current = target[1]
            if original is not None and same_owner(current, original):
                require(backup_owner is None, "the same original inode cannot exist at two names")
                restored_original = True
            else:
                require(
                    promotion_intent is not None and recorded_stage is not None
                    and same_owner(current, recorded_stage)
                    and current["sha256"] == expected_hash
                    and current["bytes"] == expected_size
                    and current["mode"] == expected_mode,
                    "never remove or overwrite a changed or unrelated user canonical target",
                )
                if original is None:
                    os.unlink(EXTENSION, dir_fd=directory)
                    os.fsync(directory)
                    removed_promoted = True
                else:
                    require(backup_owner is not None, "never replace a promoted target without its exact original inode")
                    os.replace(backup, EXTENSION, src_dir_fd=directory, dst_dir_fd=directory)
                    os.fsync(directory)
                    restored = current_target()
                    require(restored is not None and same_owner(restored[1], original), "the original inode was not restored exactly")
                    restored_original = True
        elif original is not None and backup_owner is not None:
            os.replace(backup, EXTENSION, src_dir_fd=directory, dst_dir_fd=directory)
            os.fsync(directory)
            restored = current_target()
            require(restored is not None and same_owner(restored[1], original), "restore the exact original device, inode, and content")
            restored_original = True
        elif original is not None:
            raise ActivationError("refuse recovery when the original user inode and backup are both absent")
        try:
            stage_raw, stage_owner = read_owned(
                ROOT, "candidates/" + stage, expected_hash,
                maximum=MAX_BINARY, exact_size=expected_size,
            )
        except FileNotFoundError:
            stage_raw, stage_owner = None, None
        if stage_owner is not None:
            require(
                recorded_stage is not None and same_owner(stage_owner, recorded_stage),
                "never delete an unrecorded, changed, linked, or unrelated adjacent user file",
            )
            os.unlink(stage, dir_fd=directory)
            os.fsync(directory)
            removed_stage = True
        final = current_target()
        require(
            (original is None and final is None)
            or (original is not None and final is not None and same_owner(final[1], original)),
            "report success only after the exact original canonical state is restored",
        )
        require_absent(directory, backup)
        require_absent(directory, stage)
    finally:
        os.close(directory)
        os.close(repository)
    result = {
        "schema": SCHEMA + "-actual-restoration",
        "status": "PASS",
        "version": 5,
        "family": FAMILY,
        "route": "reportless-recovery" if arguments["mode"] == "recover" else "journal-backed-restore",
        "activation_root": root,
        "recovery_journal": journal_owner,
        "target": TARGET,
        "original": original,
        "original_inode_preserved": original is not None and restored_original,
        "originally_absent": original is None,
        "removed_only_authenticated_promoted_inode": removed_promoted,
        "removed_only_authenticated_stage_inode": removed_stage,
        "group_atomic": False,
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    restoration = write_private(root, "restoration-receipt.json", canonical(result))
    return {**result, "restoration_receipt": restoration}


class SourceOnlyWall:
    """Prove that synthetic controls cannot perform real external effects."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked = 0

    def denied(self, *_arguments: Any, **_keywords: Any) -> Any:
        self.blocked += 1
        raise SourceOnlyEffect("V5 synthetic controls cannot perform an external effect")

    def __enter__(self) -> "SourceOnlyWall":
        targets = (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "write"), (os, "stat"), (os, "lstat"), (os, "fstat"),
            (os, "listdir"), (os, "scandir"), (os, "mkdir"), (os, "makedirs"),
            (os, "unlink"), (os, "remove"), (os, "rename"), (os, "replace"),
            (os, "link"), (os, "symlink"), (os, "fsync"), (os, "fchmod"),
            (os, "urandom"), (os, "system"), (os, "popen"),
            (os, "putenv"), (os, "unsetenv"),
            (subprocess, "Popen"), (subprocess, "run"), (subprocess, "call"),
            (subprocess, "check_call"), (subprocess, "check_output"),
            (socket, "socket"), (socket, "create_connection"),
            (tempfile, "mkdtemp"), (tempfile, "mkstemp"),
            (threading.Thread, "start"), (ctypes, "CDLL"), (ctypes, "PyDLL"),
            (importlib, "import_module"),
            (time, "time"), (time, "time_ns"), (time, "monotonic"),
            (time, "monotonic_ns"), (time, "perf_counter"),
            (time, "perf_counter_ns"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "exists"), (Path, "is_file"), (Path, "is_dir"),
            (Path, "stat"), (Path, "lstat"), (Path, "mkdir"), (Path, "iterdir"),
        )
        for item, name in targets:
            if hasattr(item, name):
                self.previous.append((item, name, getattr(item, name)))
                setattr(item, name, self.denied)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> bool:
        for item, name, previous in reversed(self.previous):
            setattr(item, name, previous)
        return False


def expect_rejected(function: Any, *arguments: Any) -> None:
    try:
        function(*arguments)
    except (ActivationError, TypeError, ValueError, KeyError, IndexError, OSError):
        return
    raise ActivationError("a negative V5 C-only, owner, recovery, or effect control was accepted")


def synthetic_owner(seed: int) -> dict[str, Any]:
    return {
        "bytes": 128,
        "device": 1,
        "inode": seed,
        "mode": 0o700,
        "nlink": 1,
        "path": ROOT + "/" + TARGET,
        "relative": TARGET,
        "sha256": "a" * 64,
        "uid": 1000,
    }


def self_test() -> dict[str, Any]:
    verify_runtime()
    with SourceOnlyWall() as wall:
        frozen = validate_contract(expected_contract())
        controls = 0
        changes: list[tuple[tuple[str, ...], Any]] = [
            (("schema",), SCHEMA), (("version",), 4),
            (("family",), "rust"), (("phase",), "PASS"),
            (("activation_policy", "accepted_family"), "zig"),
            (("activation_policy", "actual_v8_build_required"), False),
            (("activation_policy", "adjacent_backup"), "BYTE COPY"),
            (("activation_policy", "canonical_target"), "candidates/_rust_bridge.so"),
            (("activation_policy", "candidate_source_mutation"), "ALLOWED"),
            (("activation_policy", "external_engine"), "ALLOWED"),
            (("activation_policy", "fallback"), "ALLOWED"),
            (("activation_policy", "group_atomic"), True),
            (("activation_policy", "hardlinks"), "ALLOWED"),
            (("activation_policy", "network"), "ALLOWED"),
            (("activation_policy", "original_inode_restoration"), "BYTE COPY"),
            (("activation_policy", "private_directory_mode"), "0755"),
            (("activation_policy", "private_native_file_mode"), "0600"),
            (("activation_policy", "private_source_and_evidence_file_mode"), "0700"),
            (("activation_policy", "recovery_without_activation_report"), False),
            (("activation_policy", "stdlib_regex_engine"), "ALLOWED"),
            (("activation_policy", "v8_compiler_process_count"), 13),
            (("activation_policy", "v8_independent_source_phase_count"), 1),
            (("first_party_source_repair", "derived_c_source", "sha256"), ORIGINAL[1]),
            (("first_party_source_repair", "derived_c_source", "bytes"), ORIGINAL[2]),
            (("first_party_source_repair", "derived_c_source", "materialized_during_activation_freeze"), True),
            (("historical_v19", "actual_activation_count"), 0),
            (("historical_v19", "current_active_target_count"), 1),
            (("historical_v19", "actual_candidate_and_native_evidence_owner_count"), 76),
            (("historical_v19", "authenticated_digest_addressed_history_paths"), 71),
            (("historical_v19", "cpp_inclusive_evidence_owner_count"), 54),
            (("historical_v19", "original_source_owner_count"), 24),
            (("historical_v19", "qualified_candidate_count"), 1),
            (("historical_v19", "go_full_campaign_status"), "PASS"),
            (("historical_v19", "go_full_campaign_semantic_mismatch_count"), 0),
            (("historical_v19", "go_full_campaign_infrastructure_failure_count"), 0),
            (("historical_v19", "go_restoration_status"), "FAIL"),
            (("oracle", "case_execution_count"), 31236),
            (("oracle", "private_waiver_count"), 12),
            (("oracle", "suite_count"), 12),
            (("oracle", "version"), "3.14.5"),
        ]
        for family in (V8, REPAIR, V19):
            for specification in family.values():
                checked_digest(specification[1], specification[0])
        for path, replacement in changes:
            changed = copy.deepcopy(frozen)
            position = changed
            for part in path[:-1]:
                position = position[part]
            position[path[-1]] = replacement
            expect_rejected(validate_contract, changed)
            controls += 1
        for key, original in BOUNDARY.items():
            if type(original) is bool:
                replacements = (not original, 1, None)
            elif type(original) is int:
                replacements = (original + 1, True, None)
            else:
                replacements = ("PASS", "MEASURED", None)
            for replacement in replacements:
                changed = copy.deepcopy(frozen)
                changed["phase_boundary"][key] = replacement
                expect_rejected(validate_contract, changed)
                controls += 1
        for hostile in ("", "/tmp/../unsafe", "/", "../candidates", "candidates//x", "candidates/../x"):
            expect_rejected(checked_relative, hostile)
            controls += 1
        for hostile in ("", "A" * 64, "g" * 64, "a" * 63, "a" * 65, None, 1):
            expect_rejected(checked_digest, hostile, "synthetic hostile pin")
            controls += 1
        for hostile in ("", "01", "0", "-1", "1.5", str(MAX_BINARY + 1), "١"):
            expect_rejected(checked_native_size, hostile)
            controls += 1
        for hostile in ("", "../x", "phase 2", "a" * (MAX_LABEL + 1), "é"):
            expect_rejected(checked_label, hostile)
            controls += 1
        for hostile in ("/tmp/rebar-phase2-native-build-v8-rust-x", "/tmp/../x", "/", ROOT):
            expect_rejected(checked_private_root, hostile, BUILD_PREFIX)
            controls += 1
        exact = synthetic_owner(10)
        require(same_owner(exact, copy.deepcopy(exact)), "accept only the exact original inode")
        for key, replacement in (
            ("device", 2), ("inode", 11), ("mode", 0o600),
            ("nlink", 2), ("uid", 1001), ("bytes", 127), ("sha256", "b" * 64),
        ):
            hostile = copy.deepcopy(exact)
            hostile[key] = replacement
            require(not same_owner(exact, hostile), "reject changed original " + key)
            controls += 1
        require(
            validate_private_file_mode(0o600, native=False) == 0o600,
            "accept genuine owner-only original source, adapter, and recovery evidence",
        )
        require(
            validate_private_file_mode(0o700, native=True) == 0o700,
            "accept the actual owner-only executable GNU-compiled native C ELF",
        )
        for mode, native in (
            (0o700, False), (0o644, False), (0o755, False),
            (0o600, True), (0o755, True), (0o770, True),
            (0o777, True), (True, True),
        ):
            expect_rejected(
                lambda mode=mode, native=native:
                    validate_private_file_mode(mode, native=native),
            )
            controls += 1
        require(
            parse_arguments(["--self-test"]) == {"mode": "self-test"},
            "accept exactly one zero-effect V5 synthetic selector",
        )
        for hostile in (
            [], ["--verify-frozen-context"], ["--activate"], ["--recover"],
            ["--restore"], ["--self-test", "--activate"],
            ["--benchmark"], ["--build"], ["--family", "rust"],
        ):
            expect_rejected(parse_arguments, hostile)
            controls += 1
        effects = (
            lambda: builtins.open("/tmp/rebar-v5-forbidden", "wb"),
            lambda: os.open("/tmp/rebar-v5-forbidden", os.O_RDONLY),
            lambda: os.replace("/tmp/rebar-v5-a", "/tmp/rebar-v5-b"),
            lambda: os.link("/tmp/rebar-v5-a", "/tmp/rebar-v5-b"),
            lambda: tempfile.mkdtemp(prefix=ACTIVATION_PREFIX),
            lambda: subprocess.run(["/usr/bin/true"]),
            lambda: socket.socket(),
            lambda: time.perf_counter_ns(),
            lambda: ctypes.CDLL("/tmp/rebar-v5-forbidden.so"),
            lambda: importlib.import_module("re"),
            lambda: os.urandom(18),
            lambda: Path("/tmp/rebar-v5-forbidden").read_bytes(),
        )
        for effect in effects:
            expect_rejected(effect)
            controls += 1
        require(wall.blocked == len(effects), "independently intercept every prohibited real effect")
        require(controls >= 145, "exercise the complete C-only source, history, recovery, and effect controls")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "status": "PASS",
            "version": 5,
            "family": FAMILY,
            "negative_controls": controls,
            "blocked_effect_attempts": wall.blocked,
            "actual_filesystem_reads": 0,
            "actual_filesystem_writes": 0,
            "actual_processes_started": 0,
            "actual_clock_samples": 0,
            "actual_network_requests": 0,
            "actual_candidate_imports": 0,
            "actual_native_libraries_loaded": 0,
            "actual_holdout_reads": 0,
            "actual_canonical_promotions": 0,
            "actual_recovery_roots_created": 0,
            "historical_actual_v4_activation_count": 3,
            "authoritative_counted_evidence_owner_count": 71,
            "authenticated_digest_addressed_history_paths": 76,
            "read_only": True,
            **copy.deepcopy(BOUNDARY),
        }


def main(arguments: list[str] | None = None) -> int:
    try:
        parsed = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if parsed["mode"] == "self-test":
            result = self_test()
        elif parsed["mode"] == "verify-frozen-context":
            result = verify_frozen_context(parsed)
        elif parsed["mode"] == "activate":
            result = activate(parsed)
        else:
            result = recover(parsed)
        sys.stdout.buffer.write(canonical(result))
        return 0 if result.get("status") == "PASS" else 1
    except (
        ActivationError, OSError, ValueError, UnicodeError,
        subprocess.SubprocessError, zlib.error,
    ) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-gate-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
