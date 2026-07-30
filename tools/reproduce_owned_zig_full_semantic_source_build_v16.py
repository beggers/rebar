#!/usr/bin/env python3
"""Freeze and, only after root authorization, reproduce a complete Zig build."""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import copy
import ctypes
import errno
import fcntl
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import signal
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import threading
import time
import types
from typing import Any
import zlib


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/reproduce_owned_zig_full_semantic_source_build_v16.py"
PROTOCOL = "oracle/phase2/ZIG-FULL-SEMANTIC-SOURCE-BUILD-V16.md"
CONTRACT = "oracle/phase2/zig-full-semantic-source-build-v16.json"
SCHEMA = "rebar-owned-zig-full-semantic-source-build-v16"
VERSION = 16
ROOT_PREFIX = "rebar-phase2-zig-full-semantic-source-build-v16-"
LABEL_PREFIX = "zig-full-semantic-source-build-v16-"
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3_756,
)
LEGACY = {
    "source": (
        "tools/reproduce_owned_zig_scanner_phrase_source_build_v13.py",
        "673cb1a5a1b2b70d36e77032e01312fda2887828a8898900f1c91378fde8687e",
        123_672,
    ),
    "protocol": (
        "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-BUILD-V13.md",
        "b8c3622d64041386c6202f0d980632c9e03a8c90c08455d1c38a50260ae68a40",
        8_765,
    ),
    "contract": (
        "oracle/phase2/zig-scanner-phrase-source-build-v13.json",
        "6b0b918da55d55144c1384d915027f9ba360048c910a4225568abce6fd3efd15",
        21_331,
    ),
}
CAMPAIGN = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v13.py",
        "fa46d4029f5590adceb22bfe4e612248da5f7f90ed6362d58faa5b631fee7ff8",
        246_570,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V13.md",
        "6b42893161e37baec1695aefb414fb7179b778f2164018b024bd68b3c9bb5c2c",
        9_553,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v13.json",
        "327b14096e36c7a2e4cab977a452fc2477fbf148396f50433cbf1dc8aba31a3f",
        106_084,
    ),
}
GUARD = {
    "source": (
        "tools/verify_owned_candidate_runtime_independence_v4.py",
        "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3",
        48_687,
    ),
    "protocol": (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md",
        "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16",
        4_492,
    ),
    "contract": (
        "oracle/phase2/candidate-runtime-independence-v4.json",
        "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2",
        9_352,
    ),
}
ENGINE = (
    "candidates/zig/mini_regex.zig",
    "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
    186_915,
)
ADAPTER = (
    "candidates/zig/variants/public_adapter_semantics_v1/zig_candidate.py",
    "7129c63bdfd3c265a44541500238c26a8a5511f8932140de7d06bb49c13f588d",
    67_735,
)
BRIDGE = (
    "candidates/zig/variants/replacement_event_semantics_v1/py_bridge.c",
    "07337863f6b4a0e749a8d60b2e5704bb961e43dc09bfa85c238f0efa40d3583c",
    176_765,
)
LOCK = (
    "toolchains/zig-0.16.0.lock.json",
    "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
    628,
)
FAILURE = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v12-"
    "phase2-v13-zig-guard-clean-v1-original-p0-v12-failures-"
    "publication-receipt.json",
    "ce7605be25bbb71e1b06b65b9aa3f79cfd09b39f0ce5f076ed9d986f15ee8de9",
    77_604,
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1_024), ("buffer_v3", 768),
    ("managed_v1", 1_024), ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912), ("substitution_v2", 5_120),
    ("shape_v2", 10_240), ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
LEGACY_ADAPTER_KEY = "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"
LEGACY_BRIDGE_KEY = "candidates/zig/py_bridge.c"
LEGACY_CANONICAL_ADAPTER_KEY = "candidates/zig_candidate.py"
EXPECTED_COMPILER_SHA = (
    "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
)
COPYREG_LITERAL = b'PyImport_ImportModule("copyreg")'


class FreezeError(ValueError):
    """The independently frozen source build or isolated source boundary changed."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require a complete independently supplied lowercase SHA-256: " + label)
    return value


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                   separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicate independently frozen JSON fields")
        result[key] = value
    return result


def parse(value: bytes, label: str, *, canonical_required: bool = True) -> dict:
    try:
        result = json.loads(
            value,
            object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                FreezeError("reject nonfinite frozen JSON")),
        )
    except (TypeError, ValueError, UnicodeError) as failure:
        raise FreezeError("reject malformed frozen source evidence: " + label) from failure
    require(type(result) is dict,
            "require an authenticated complete JSON object: " + label)
    if canonical_required:
        require(canonical(result) == value,
                "reject noncanonical source evidence: " + label)
    return result


def same(actual: object, expected: dict, label: str) -> None:
    require(type(actual) is dict,
            "require a complete independently frozen object: " + label)
    for key, value in expected.items():
        require(actual.get(key) == value,
                "frozen source evidence changed: " + label + ": " + key)


def reference(row: tuple[str, str, int]) -> dict:
    return {"path": row[0], "sha256": row[1], "bytes": row[2]}


def owner_rows() -> tuple[tuple[str, str, int], ...]:
    return (GOAL, *LEGACY.values(), *CAMPAIGN.values(),
            *GUARD.values(), ENGINE, ADAPTER, BRIDGE, LOCK, FAILURE)


class SourceOnlyWall:
    """Deny proposals, private roots, engines, candidate imports, and processes."""

    def __init__(self, contract_render: bool, source: tuple[str, str, int],
                 protocol: tuple[str, str, int], contract: tuple[str, str, int] | None):
        self.contract_render = contract_render
        approved = (*owner_rows(), source, protocol)
        if contract is not None:
            approved = (*approved, contract)
        self.approved = frozenset(os.path.join(ROOT, item[0]) for item in approved)
        self.contract_path = os.path.join(ROOT, CONTRACT)

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(path) is str,
                    "reject descriptor-only, relative, or candidate-native file access")
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                    | os.O_TRUNC | os.O_APPEND))
            if writing:
                mandatory = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.contract_render and path == self.contract_path
                        and flags & mandatory == mandatory,
                        "reject source-only mutation outside the exclusive V16 contract")
            else:
                require(path in self.approved and flags & os.O_NOFOLLOW != 0,
                        "reject candidate-native object, private root, archive, "
                        "holdout proposal, seed, hidden case, or unowned evidence")
            return
        if (event.startswith(("subprocess.", "socket.", "ctypes.",
                              "os.exec", "os.spawn"))
                or event in {
                    "os.system", "os.fork", "os.posix_spawn", "os.mkdir",
                    "os.remove", "os.rename", "os.rmdir", "os.chdir", "os.chmod",
                    "os.link", "os.symlink", "os.truncate", "os.putenv",
                    "time.time", "time.monotonic", "time.perf_counter",
                    "_thread.start_new_thread",
                }):
            raise FreezeError("reject compiler, native load, clock, process, "
                              "thread, network, or unsafe source-only mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and (
                name in {"re", "_sre", "regex", "re2", "pcre", "oniguruma"}
                or name.startswith(("candidates.", "rebar."))
            )), "reject candidate, CPython matching engine, or external regex import")


def read(row: tuple[str, str, int], approved: tuple[tuple[str, str, int], ...]
         ) -> tuple[dict, bytes]:
    require(row in approved, "read only an exact independently frozen source owner")
    path, expected, size = row
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_uid == os.getuid()
                and before.st_nlink == 1
                and before.st_size == size,
                "frozen source owner identity changed: " + path)
        blocks = []
        while True:
            piece = os.read(descriptor, 1_048_576)
            if not piece:
                break
            blocks.append(piece)
        raw = b"".join(blocks)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_size,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and digest(raw) == expected,
                "frozen source owner content changed: " + path)
        return ({"path": path, "sha256": expected, "bytes": size,
                 "device": after.st_dev, "inode": after.st_ino,
                 "uid": after.st_uid, "mode": format(stat.S_IMODE(after.st_mode), "04o"),
                 "nlink": after.st_nlink}, raw)
    finally:
        os.close(descriptor)


def validate_sources(context: dict) -> None:
    adapter, bridge, engine = (context["protected"][ADAPTER[0]],
                               context["protected"][BRIDGE[0]],
                               context["protected"][ENGINE[0]])
    tree = ast.parse(adapter, filename=ADAPTER[0], mode="exec")
    imported_bridge = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for entry in node.names:
                require(entry.name.split(".", 1)[0]
                        not in {"re", "_sre", "regex", "re2", "pcre", "inspect",
                                "subprocess", "ctypes"},
                        "a first-party Zig adapter cannot import a matching engine")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            require(module.split(".", 1)[0]
                    not in {"re", "_sre", "regex", "re2", "pcre", "inspect",
                            "subprocess", "ctypes"},
                    "a first-party Zig adapter cannot import another matching engine")
            if module == "candidates":
                require(len(node.names) == 1 and node.names[0].name == "_zig_bridge",
                        "only the independently owned first-party Zig bridge is allowed")
                imported_bridge = True
    require(imported_bridge,
            "the corrected adapter must use only its own first-party native bridge")
    require(digest(bridge) == BRIDGE[1]
            and bridge.count(COPYREG_LITERAL) == 1
            and bridge.count(b"PyImport_ImportModule(") == 1
            and bridge.count(b"PyImport_Import(") == 0
            and bridge.count(b"PyImport_ExecCodeModule(") == 0
            and b'PyImport_ImportModule("re")' not in bridge
            and b'PyImport_ImportModule("_sre")' not in bridge
            and b'PyImport_ImportModule("regex")' not in bridge,
            "allow exactly one digest-bound benign copyreg import and no regex import")
    require(b'@import("std")' in engine,
            "require the independently written first-party Zig parser/executor")


def validate_history(context: dict) -> None:
    legacy = context["legacy_contract"]
    same(legacy, {
        "schema": "rebar-owned-zig-scanner-phrase-source-build-v13-source-freeze",
        "version": 13,
        "status": "SOURCE FROZEN; CORRECTED ZIG BUILD NOT RUN",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }, "immutable historical V13 native-build source freeze")
    same(legacy.get("original_oracle"), {
        "python_implementation": "CPython",
        "python_version": "3.14.6",
        "original_case_execution_denominator": 31_237,
        "original_suite_count": 13,
        "original_named_private_waiver_count": 13,
        "mapped_original_obligation_count": 73,
        "original_crosswalk_count": 34,
        "supplemental_reference_case_count": 8_244,
        "supplemental_cases_added_to_original_denominator": False,
    }, "unchanged original CPython oracle")
    same(legacy.get("future_native_build"), {
        "status": "NOT RUN",
        "independent_phase_count": 2,
        "expected_process_count_per_phase": 13,
        "expected_process_count_only_after_both_phases": 26,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
    }, "inherit the actually implementable V13 two-phase build structure")
    toolchain = legacy.get("offline_toolchain")
    same(toolchain, {
        "zig_version": "0.16.0",
        "zig_exact_executable": "/tmp/zig-x86_64-linux-0.16.0/zig",
        "compiler_binaries_executed": 0,
        "network_requests": 0,
    }, "pinned offline official Zig toolchain")
    require(type(toolchain.get("owners")) is list and len(toolchain["owners"]) == 6,
            "preserve each independently authenticated offline compiler and header")
    zig_tools = [item for item in toolchain["owners"] if item.get("id") == "zig"]
    require(len(zig_tools) == 1 and zig_tools[0].get("sha256") == EXPECTED_COMPILER_SHA,
            "reject replacement of the official pinned Zig compiler")

    campaign = context["campaign_contract"]
    same(campaign, {
        "schema": "rebar-owned-repaired-zig-original-campaign-v13-guarded-lifetime-source-freeze",
        "version": 13,
        "status": "SOURCE FROZEN; V3-GUARDED LIFETIME ZIG MATCHING NOT RUN",
        "qualified_candidate_count": 0,
        "corrected_original_matching": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }, "preserve historical V13 campaign without executing its stale V3 guard")
    same(campaign.get("original_oracle"), {
        "case_execution_denominator": 31_237,
        "suite_count": 13,
        "named_private_waiver_count": 13,
        "obligation_count": 73,
        "crosswalk_count": 34,
        "supplemental_reference_case_count": 8_244,
        "supplemental_cases_added_to_original_denominator": False,
        "final_holdout_authorized": False,
        "performance_oracle_authorized": False,
    }, "preserve the complete 31,237-case original oracle")
    predecessor = campaign.get("pushed_v12_actual_predecessor")
    same(predecessor, {
        "source_freeze_version": 12,
        "source_freeze_schema":
            "rebar-owned-repaired-zig-original-campaign-v12-guard-clean-source-freeze",
    }, "preserve the exact V12 independently observed failure predecessor")
    old_owners = predecessor.get("owners")
    require(type(old_owners) is list
            and any(type(item) is dict and item.get("path") == FAILURE[0]
                    and item.get("sha256") == FAILURE[1]
                    for item in old_owners),
            "bind the V13 predecessor to the exact complete V12 failure receipt")

    failure = context["failure"]
    same(failure, {
        "schema": "rebar-owned-repaired-zig-original-campaign-v12-durable-publication-receipt",
        "status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "case_execution_denominator": 31_237,
        "suite_count": 13,
        "completed_suite_count": 12,
        "actual_candidate_workers": 13,
        "verified_passing_case_count": 4_607,
        "observed_semantic_mismatch_lower_bound": 1_700,
        "semantic_mismatch_count": "NOT MEASURED",
        "infrastructure_failure_count": 1,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }, "preserve all 1,700 known Zig losses and the incomplete interpreter suite")


def validate_guard(context: dict) -> None:
    guard = context["guard_contract"]
    same(guard, {
        "schema": "rebar-owned-candidate-runtime-independence-v4-source-freeze",
        "version": 4,
        "goal_sha256": GOAL[1],
        "status": "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }, "require exact strict V4 guard without running it")
    same(guard.get("phase_one"), {
        "original_case_execution_denominator": 31_237,
        "original_suite_count": 13,
        "original_obligation_count": 73,
        "named_private_waiver_count": 13,
        "separate_supplemental_case_count": 8_244,
        "supplemental_cases_counted_in_original_denominator": False,
        "status": "PASS",
    }, "strict V4 guard retains the original oracle")
    same(guard.get("runtime_isolation_policy"), {
        "guard_installed_before_candidate_import": True,
        "stdlib_re_engine": "FORBIDDEN",
        "stdlib_sre_engine": "FORBIDDEN",
        "external_regex_package": "FORBIDDEN",
        "cross_candidate_engine": "FORBIDDEN",
        "matching_fallback": "FORBIDDEN",
        "source_gate_interpreters": "NOT CREATED",
    }, "the corrected original campaign must use strict V4, never stale V3")
    same(guard.get("native_owner_policy"), {
        "required_field_count": 14,
        "native_loaded": False,
        "extra_or_missing_fields": "FORBIDDEN",
    }, "strict family-owned native identity and source-before-import")
    same(guard.get("subinterpreter_bootstrap"), {
        "suite": "subinterpreter_v2",
        "original_case_count": 128,
        "expected_interpreters_created": 11,
        "expected_interpreters_destroyed": 11,
        "expected_case_interpreter_exec_calls": 394,
        "expected_total_real_interpreter_exec_calls": 416,
        "actual_interpreters_created": 0,
        "actual_interpreters_destroyed": 0,
        "actual_case_interpreter_exec_calls": 0,
        "candidate_status": "NOT RUN",
    }, "no genuine child is invented during Zig V16 source-only verification")
    same(guard.get("provider_proof"), {
        "mode": "--prove-provider",
        "source_gate_invokes_proof": False,
        "status": "NOT RUN",
        "candidate_imports": 0,
        "candidate_native_libraries_loaded": 0,
        "compressed_archives_opened": 0,
    }, "source-only gates never execute the independently authorized provider proof")


def verify_context(context: dict) -> None:
    require(digest(context["raw"][GOAL[0]]) == GOAL[1],
            "the immutable user objective changed")
    for mapping in (LEGACY, CAMPAIGN, GUARD):
        for name, owner in mapping.items():
            require(digest(context["raw"][owner[0]]) == owner[1],
                    "immutable frozen predecessor owner changed: " + name)
    for owner in (ENGINE, ADAPTER, BRIDGE, LOCK, FAILURE):
        require(digest(context["raw"][owner[0]]) == owner[1],
                "immutable Zig source or public failure receipt changed: " + owner[0])
    for name, owner in (("legacy_contract", LEGACY["contract"]),
                        ("campaign_contract", CAMPAIGN["contract"]),
                        ("guard_contract", GUARD["contract"]),
                        ("failure", FAILURE)):
        require(digest(canonical(context[name])) == owner[1],
                "complete parsed predecessor evidence changed: " + name)
    validate_sources(context)
    validate_history(context)
    validate_guard(context)
    lock = context["lock"]
    same(lock, {
        "schema": "rebar-official-language-toolchain-v1",
        "language": "Zig",
        "version": "0.16.0",
        "release_channel": "stable",
        "platform": "x86_64-linux",
        "compiler_sha256": EXPECTED_COMPILER_SHA,
    }, "exact official stable offline Zig toolchain lock")
    require(sum(amount for _, amount in SUITES) == 31_237,
            "never silently change the original Python correctness denominator")


def context(options: argparse.Namespace, *, wall: bool) -> dict:
    source_owner = (SOURCE, sha(options.source_sha256, "V16 controller"),
                    options.source_bytes)
    protocol_owner = (PROTOCOL, sha(options.protocol_sha256, "V16 protocol"),
                      options.protocol_bytes)
    contract_owner = None
    if options.contract_sha256 is not None:
        contract_owner = (CONTRACT, sha(options.contract_sha256, "V16 contract"),
                          options.contract_bytes)
    require(type(options.source_bytes) is int and 1 <= options.source_bytes <= 1_048_576
            and type(options.protocol_bytes) is int
            and 1 <= options.protocol_bytes <= 131_072,
            "independently pin full V16 source and protocol bytes")
    if contract_owner is not None:
        require(type(options.contract_bytes) is int
                and 1 <= options.contract_bytes <= 1_048_576,
                "independently pin full V16 contract bytes")
    for prefix, mapping in (("legacy", LEGACY), ("campaign", CAMPAIGN),
                            ("guard", GUARD)):
        for name, owner in mapping.items():
            require(getattr(options, prefix + "_" + name + "_sha256") == owner[1],
                    "independently pin exact predecessor " + prefix + " " + name)
    require(options.engine_sha256 == ENGINE[1]
            and options.adapter_sha256 == ADAPTER[1]
            and options.bridge_sha256 == BRIDGE[1]
            and options.lock_sha256 == LOCK[1]
            and options.failure_sha256 == FAILURE[1],
            "independently pin all corrected first-party sources and actual Zig failure")
    source_wall = None
    if wall:
        source_wall = SourceOnlyWall(options.render_contract,
                                     source_owner, protocol_owner, contract_owner)
        sys.addaudithook(source_wall.check)
    approved = (*owner_rows(), source_owner, protocol_owner)
    if contract_owner is not None:
        approved = (*approved, contract_owner)
    metadata, raw = {}, {}
    for row in approved:
        identity, payload = read(row, approved)
        metadata[row[0]], raw[row[0]] = identity, payload
    result = {
        "options": options,
        "wall": source_wall,
        "owners": metadata,
        "raw": raw,
        "protected": raw,
        "source": raw[SOURCE],
        "source_owner": metadata[SOURCE],
        "protocol": raw[PROTOCOL],
        "protocol_owner": metadata[PROTOCOL],
        "legacy_contract": parse(raw[LEGACY["contract"][0]], "V13 builder contract"),
        "campaign_contract": parse(raw[CAMPAIGN["contract"][0]], "V13 campaign"),
        "guard_contract": parse(raw[GUARD["contract"][0]], "strict V4 guard"),
        "lock": parse(raw[LOCK[0]], "official Zig lock", canonical_required=False),
        "failure": parse(raw[FAILURE[0]], "actual Zig V12 original failure"),
    }
    verify_context(result)
    return result


def legacy_module(context: dict) -> types.ModuleType:
    module = types.ModuleType("_rebar_owned_zig_v16_authenticated_legacy")
    module.__file__ = os.path.join(ROOT, LEGACY["source"][0])
    exec(compile(context["raw"][LEGACY["source"][0]],
                 module.__file__, "exec", dont_inherit=True), module.__dict__)
    require(module.SCHEMA == "rebar-owned-zig-scanner-phrase-source-build-v13"
            and module.VERSION == 13
            and tuple(module.PHASE_NAMES) == ("reference-a", "reference-b")
            and len(module.PROCESS_ROLES) == 13
            and "PyImport_ImportModule" in module.FORBIDDEN_SYMBOLS
            and module.TOOLCHAINS["zig"][1] == EXPECTED_COMPILER_SHA,
            "load only the exact complete source-authenticated V13 build machinery")
    module.SCHEMA = SCHEMA
    module.VERSION = VERSION
    module.SOURCE_PATH = SOURCE
    module.PROTOCOL_PATH = PROTOCOL
    module.CONTRACT_PATH = CONTRACT
    module.PRIVATE_ROOT_PREFIX = ROOT_PREFIX
    module.CANONICAL_SOURCE_PREFIX = "/rebar-owned-zig-full-semantic-v16-source"
    module.OWNERS = {
        ENGINE[0]: (ENGINE[1], ENGINE[2]),
        LEGACY_BRIDGE_KEY: (BRIDGE[1], BRIDGE[2]),
        LEGACY_ADAPTER_KEY: (ADAPTER[1], ADAPTER[2]),
        LEGACY_CANONICAL_ADAPTER_KEY: (ADAPTER[1], ADAPTER[2]),
    }
    module.FORBIDDEN_SYMBOLS = frozenset(
        item for item in module.FORBIDDEN_SYMBOLS
        if item != "PyImport_ImportModule"
    )
    original_audit = module.audit_native

    def strict_audit(role: str, dynamic: bytes, symbols: bytes,
                     sections: bytes) -> dict:
        defined, undefined = module.dynamic_symbols(symbols)
        require("PyImport_Import" not in defined | undefined
                and "PyImport_ExecCodeModule" not in defined | undefined,
                "reject every general-purpose Python import and code-loader symbol")
        benign_copyreg = "PyImport_ImportModule" in undefined
        if role == "engine":
            require("PyImport_ImportModule" not in defined | undefined,
                    "the first-party Zig engine must never import Python modules")
        elif role == "bridge":
            require(benign_copyreg
                    and "PyImport_ImportModule" not in defined
                    and digest(context["raw"][BRIDGE[0]]) == BRIDGE[1]
                    and context["raw"][BRIDGE[0]].count(COPYREG_LITERAL) == 1
                    and context["raw"][BRIDGE[0]].count(
                        b"PyImport_ImportModule(") == 1,
                    "permit only the pinned bridge's sole literal copyreg helper")
        else:
            raise FreezeError("audit only first-party Zig engine and adjacent bridge")
        result = original_audit(role, dynamic, symbols, sections)
        result.update({
            "general_python_import_count": 0,
            "python_code_loader_count": 0,
            "benign_copyreg_import_count": int(benign_copyreg),
            "benign_copyreg_import": "copyreg" if benign_copyreg else None,
            "copyreg_import_requires_exact_complete_bridge_sha256": BRIDGE[1],
            "copyreg_import_is_matching_engine": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
        })
        return result

    module.audit_native = strict_audit

    def names(label: str) -> tuple[str, str]:
        checked = module.checked_label(label)
        prefix = LABEL_PREFIX + checked
        return prefix + "-private-root-receipt.json", prefix + "-build-receipt.json"

    module.evidence_names = names
    return module


def source_effects() -> dict:
    return {
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "runtime_guards_installed": 0,
        "subinterpreters_created": 0,
        "compiler_processes_started": 0,
        "compiler_binaries_executed": 0,
        "native_libraries_loaded": 0,
        "native_activations": 0,
        "private_roots_created": 0,
        "private_roots_opened": 0,
        "private_phase_directories_created": 0,
        "private_source_files_written": 0,
        "private_root_receipts_published": 0,
        "build_receipts_published": 0,
        "matching_archives_opened": 0,
        "matching_archives_inflated": 0,
        "reference_archives_opened": 0,
        "holdout_proposals_opened": 0,
        "holdout_proposals_statted": 0,
        "hidden_cases_read": 0,
        "final_seed_files_opened": 0,
        "benchmark_files_opened": 0,
        "network_requests": 0,
        "clock_samples": 0,
        "threads_started": 0,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
    }


def contract_document(context: dict, legacy: types.ModuleType) -> dict:
    old = context["campaign_contract"]
    actual = context["failure"]
    guard = context["guard_contract"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; FULL FIRST-PARTY ZIG NATIVE BUILD NOT RUN",
        "family": "zig",
        "goal_sha256": GOAL[1],
        "source": context["source_owner"],
        "protocol": context["protocol_owner"],
        "predecessor_native_build": {
            "source": context["owners"][LEGACY["source"][0]],
            "protocol": context["owners"][LEGACY["protocol"][0]],
            "contract": context["owners"][LEGACY["contract"][0]],
            "version": 13,
            "independent_phase_count": 2,
            "process_count_per_phase": 13,
            "implementation_reused": "SOURCE-AUTHENTICATED V13 BUILD PLUMBING ONLY",
            "obsolete_v13_context_reused": False,
            "obsolete_v13_guard_executed": False,
        },
        "previous_original_campaign": {
            "source": context["owners"][CAMPAIGN["source"][0]],
            "protocol": context["owners"][CAMPAIGN["protocol"][0]],
            "contract": context["owners"][CAMPAIGN["contract"][0]],
            "previous_version": 13,
            "source_executed": False,
            "legacy_v3_runtime_guard_reused": False,
            "v13_contract_prior_proposal_owners_opened": 0,
        },
        "original_oracle": {
            "case_execution_denominator": 31_237,
            "suite_count": 13,
            "suites": [{"id": name, "case_execution_count": count}
                       for name, count in SUITES],
            "named_private_waiver_count": 13,
            "obligation_count": 73,
            "crosswalk_count": 34,
            "supplemental_reference_case_count": 8_244,
            "supplemental_cases_counted_in_original_denominator": False,
            "final_holdout_authorized": False,
            "performance_oracle_authorized": False,
        },
        "previous_actual_zig_failure": {
            "receipt": context["owners"][FAILURE[0]],
            "candidate_status": actual["candidate_status"],
            "publication_pass_means": actual["publication_pass_means"],
            "case_execution_denominator": actual["case_execution_denominator"],
            "suite_count": actual["suite_count"],
            "completed_suite_count": actual["completed_suite_count"],
            "actual_candidate_workers": actual["actual_candidate_workers"],
            "verified_passing_case_count": actual["verified_passing_case_count"],
            "observed_semantic_mismatch_lower_bound":
                actual["observed_semantic_mismatch_lower_bound"],
            "complete_semantic_mismatch_count": actual["semantic_mismatch_count"],
            "infrastructure_failure_count": actual["infrastructure_failure_count"],
            "matching_archive_opened": False,
            "mismatches_hidden": False,
        },
        "complete_first_party_sources": {
            "engine": context["owners"][ENGINE[0]],
            "corrected_adapter": context["owners"][ADAPTER[0]],
            "corrected_bridge": context["owners"][BRIDGE[0]],
            "engine_authorship": "FIRST-PARTY ZIG PARSER, COMPILER, AND EXECUTOR",
            "bridge_authorship": "FIRST-PARTY CPYTHON C-API BRIDGE",
            "adapter_authorship": "FIRST-PARTY PYTHON PUBLIC COMPATIBILITY LAYER",
            "external_regex_engine_count": 0,
            "external_regex_package_count": 0,
            "cross_candidate_engine_count": 0,
            "matching_fallback_count": 0,
            "stdlib_re_engine_count": 0,
            "stdlib_sre_engine_count": 0,
        },
        "strict_v4_runtime_guard": {
            "source": context["owners"][GUARD["source"][0]],
            "protocol": context["owners"][GUARD["protocol"][0]],
            "contract": context["owners"][GUARD["contract"][0]],
            "version": 4,
            "guard_installed_before_future_candidate_import": True,
            "source_gate_invokes_provider_proof": False,
            "runtime_guard_executed_by_source_freeze": False,
            "expected_subinterpreter_case_count": 128,
            "expected_interpreters_created": 11,
            "expected_interpreters_destroyed": 11,
            "expected_case_interpreter_exec_calls": 394,
            "expected_total_real_interpreter_exec_calls": 416,
            "required_native_owner_field_count":
                guard["native_owner_policy"]["required_field_count"],
            "native_loaded": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "narrow_copyreg_compatibility_exception": {
            "allowed_only_for_role": "bridge",
            "allowed_symbol": "PyImport_ImportModule",
            "allowed_exact_literal_module": "copyreg",
            "allowed_exact_literal_count": 1,
            "required_complete_corrected_bridge_sha256": BRIDGE[1],
            "engine_may_import_symbol": False,
            "other_python_import_functions_permitted": False,
            "external_regex_import_permitted": False,
            "dynamic_loader_symbol_permitted": False,
            "runtime_non_delegation_established": False,
        },
        "official_offline_toolchain": {
            "lock": context["owners"][LOCK[0]],
            "zig_version": "0.16.0",
            "zig_executable": "/tmp/zig-x86_64-linux-0.16.0/zig",
            "zig_compiler_sha256": EXPECTED_COMPILER_SHA,
            "owners": context["legacy_contract"]["offline_toolchain"]["owners"],
            "compiler_processes_started": 0,
            "network_requests": 0,
        },
        "future_native_build": {
            "status": "NOT RUN",
            "authorization": "ROOT-AUTHORIZED COMMITTED AND PUSHED SOURCE ONLY",
            "private_root_prefix": "/tmp/" + ROOT_PREFIX,
            "private_root_mode": "0700",
            "private_source_mode": "0600",
            "phase_names": ["reference-a", "reference-b"],
            "independent_phase_count": 2,
            "source_snapshot_count_per_phase": 3,
            "expected_source_snapshot_count": 6,
            "native_roles_per_phase": ["engine", "bridge"],
            "process_roles_per_phase": list(legacy.PROCESS_ROLES),
            "expected_process_count_per_phase": 13,
            "expected_total_process_count": 26,
            "actual_process_count": 0,
            "candidate_workers_started": 0,
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
            "native_reproducibility": "NOT MEASURED",
            "private_root_receipt_schema": SCHEMA + "-private-root-receipt",
            "build_receipt_schema": SCHEMA + "-plaintext-build-receipt",
            "private_root_receipt_template":
                "oracle/phase2/evidence/" + LABEL_PREFIX
                + "<FRESH-LABEL>-private-root-receipt.json",
            "build_receipt_template":
                "oracle/phase2/evidence/" + LABEL_PREFIX
                + "<FRESH-LABEL>-build-receipt.json",
            "planned_commands": legacy.command_templates(),
            "success_root_retained": True,
            "failure_cleanup_limited_to_exact_owned_private_root": True,
        },
        "source_only_effects": source_effects(),
        "from_scratch_policy": {
            "stdlib_regex_engine": "FORBIDDEN",
            "stdlib_sre_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "external_regex_library": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "network_fetch": "FORBIDDEN",
            "copyreg_pickle_helper_only": "ALLOWED IF EXACT DIGEST-BOUND SOURCE",
        },
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def validate_machine_contract(options: argparse.Namespace, state: dict,
                              legacy: types.ModuleType) -> dict:
    require(options.contract_sha256 is not None
            and options.contract_bytes is not None,
            "independently pin the complete machine-readable V16 source freeze")
    raw = state["raw"][CONTRACT]
    actual = parse(raw, "independently frozen V16 source-build contract")
    require(actual == contract_document(state, legacy),
            "bind the complete V16 build plan to every independently frozen owner")
    return state["owners"][CONTRACT]


def strict_commit(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(letter in "0123456789abcdef" for letter in value),
            "require an exact pushed main-branch commit: " + label)
    return value


def build_authorized(options: argparse.Namespace) -> None:
    require(options.root_authorized is True
            and options.frozen_committed_pushed is True
            and strict_commit(options.frozen_commit, "frozen commit")
                == strict_commit(options.pushed_commit, "pushed commit"),
            "only root may run the committed and pushed complete Zig build")


def bind_legacy(state: dict, module: types.ModuleType) -> None:
    def authenticated(_options: argparse.Namespace) -> dict:
        fresh = context(_options, wall=False)
        verify_context(fresh)
        for name in module.TOOLCHAINS:
            module.read_external_owner(name)
        owners_map = {
            ENGINE[0]: fresh["owners"][ENGINE[0]],
            LEGACY_BRIDGE_KEY: fresh["owners"][BRIDGE[0]],
            LEGACY_ADAPTER_KEY: fresh["owners"][ADAPTER[0]],
            LEGACY_CANONICAL_ADAPTER_KEY: fresh["owners"][ADAPTER[0]],
        }
        protected = {
            ENGINE[0]: fresh["raw"][ENGINE[0]],
            LEGACY_BRIDGE_KEY: fresh["raw"][BRIDGE[0]],
            LEGACY_ADAPTER_KEY: fresh["raw"][ADAPTER[0]],
            LEGACY_CANONICAL_ADAPTER_KEY: fresh["raw"][ADAPTER[0]],
        }
        fresh["owners"] = owners_map
        fresh["protected"] = protected
        return fresh

    def machine(_options: argparse.Namespace, inherited: dict) -> dict:
        # The source contract was authenticated before any process could start.
        expected = contract_document(state, module)
        actual = parse(state["raw"][CONTRACT], "independently frozen V16 contract")
        require(actual == expected,
                "never run a build after its frozen source contract changed")
        return state["owners"][CONTRACT]

    module.authenticate_context = authenticated
    module.require_machine_contract = machine

    def root_receipt(_context: dict, options: argparse.Namespace,
                     report: dict) -> dict:
        return {
            "schema": SCHEMA + "-private-root-receipt",
            "version": VERSION,
            "status": report["status"],
            "family": "zig",
            "label": module.checked_label(options.label),
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "contract_sha256": options.contract_sha256,
            "frozen_commit": options.frozen_commit,
            "pushed_commit": options.pushed_commit,
            "private_root": report.get("private_root"),
            "private_root_retained": report["status"] == "PASS",
            "private_root_cleanup": report.get("failure_cleanup"),
            "phase_names": list(module.PHASE_NAMES),
            "phases": report.get("build_phases", []),
            "source_snapshots_per_completed_phase": 3,
            "actual_process_count": len(report["processes"]),
            "corrected_adapter_sha256": ADAPTER[1],
            "corrected_bridge_source_sha256": BRIDGE[1],
            "first_party_engine_source_sha256": ENGINE[1],
            "strict_runtime_guard_version": 4,
            "strict_runtime_guard_contract_sha256": GUARD["contract"][1],
            "historical_zig_failure_sha256": FAILURE[1],
            "historical_zig_observed_mismatch_lower_bound": 1_700,
            "candidate_workers_started": 0,
            "native_activations": 0,
            "runtime_guards_installed": 0,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        }

    module.root_receipt_document = root_receipt
    prior_publish = module.publish_plaintext_pair

    def publication(inherited: dict, options: argparse.Namespace,
                    report: dict) -> dict:
        report.pop("frozen_graph_version", None)
        report.pop("frozen_evidence_owner_lower_bound", None)
        report.pop("frozen_history_reference_lower_bound", None)
        originals = {
            state["owners"][ENGINE[0]]["path"]: state["owners"][ENGINE[0]],
            state["owners"][BRIDGE[0]]["path"]: state["owners"][BRIDGE[0]],
            state["owners"][ADAPTER[0]]["path"]: state["owners"][ADAPTER[0]],
        }
        report["owned_original_sources_before"] = originals
        if report["status"] == "PASS":
            report["owned_original_sources_after"] = originals
        report["frozen_commit"] = options.frozen_commit
        report["pushed_commit"] = options.pushed_commit
        report["corrected_adapter_sha256"] = ADAPTER[1]
        report["first_party_bridge_source_sha256"] = BRIDGE[1]
        report["first_party_engine_source_sha256"] = ENGINE[1]
        report["strict_runtime_guard_version"] = 4
        report["strict_runtime_guard_contract_sha256"] = GUARD["contract"][1]
        report["historical_zig_observed_mismatch_lower_bound"] = 1_700
        report["historical_zig_failure_receipt_sha256"] = FAILURE[1]
        report["copyreg_compatibility_exception"] = {
            "allowed_role": "bridge",
            "literal_module": "copyreg",
            "allowed_import_count": 1,
            "required_complete_bridge_sha256": BRIDGE[1],
            "engine_import_allowed": False,
            "other_python_module_import_allowed": False,
            "external_regex_engine_count": 0,
            "runtime_non_delegation_established": False,
        }
        result = prior_publish(inherited, options, report)
        result.update({
            "frozen_commit": options.frozen_commit,
            "pushed_commit": options.pushed_commit,
            "corrected_adapter_sha256": ADAPTER[1],
            "corrected_bridge_source_sha256": BRIDGE[1],
            "first_party_engine_source_sha256": ENGINE[1],
            "strict_runtime_guard_version": 4,
            "strict_runtime_guard_contract_sha256": GUARD["contract"][1],
            "historical_zig_observed_mismatch_lower_bound": 1_700,
            "external_regex_package_count": 0,
            "external_regex_engine_count": 0,
            "candidate_qualified": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        })
        return result

    module.publish_plaintext_pair = publication


def actual_build(options: argparse.Namespace) -> tuple[int, dict]:
    build_authorized(options)
    state = context(options, wall=False)
    module = legacy_module(state)
    validate_machine_contract(options, state, module)
    bind_legacy(state, module)
    code, result = module.run_build(options)
    require(result.get("status") in {"PASS", "FAIL"}
            and result.get("candidate_qualified") is False,
            "never turn native build publication into matching qualification")
    if result["status"] == "PASS":
        require(result.get("actual_compiler_process_count") == 26
                and result.get("actual_phase_count") == 2,
                "claim independent reproducibility only after 26 real processes")
    return code, result


def different(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " CHANGED"
    if type(value) is list:
        return value + ["CHANGED"]
    if type(value) is dict:
        return {**value, "__v16_hostile": True}
    if value is None:
        return "CHANGED"
    raise FreezeError("unsupported adversarial frozen source value")


def hostile_controls(state: dict, module: types.ModuleType) -> int:
    labels = []

    def reject(label: str, action: Any) -> None:
        try:
            action()
        except (FreezeError, module.FreezeError, OSError, TypeError, ValueError,
                KeyError, IndexError):
            labels.append(label)
            return
        raise FreezeError("an unsafe Zig V16 source-only control passed: " + label)

    for name in ("legacy_contract", "campaign_contract", "guard_contract", "failure"):
        document = state[name]
        for key in sorted(document):
            def changed(owner=name, field=key) -> None:
                altered = copy.deepcopy(state)
                altered[owner][field] = different(altered[owner][field])
                verify_context(altered)
            reject(name + " changed " + key, changed)
    for index in range(len(SUITES)):
        reject(
            f"original suite {index} omitted",
            lambda number=index: same(
                {"suite_count": len(SUITES) - 1},
                {"suite_count": len(SUITES)}, "altered original suite " + str(number)),
        )
    for value in (None, "", "A" * 64, "0" * 63, "0" * 65,
                  "z" * 64):
        reject("invalid complete caller digest", lambda item=value: sha(item, "hostile"))
    for value in (None, "", "../bad", "/tmp", "a/b", "holdout", "a--b",
                  "a_", "A", "a-", "x" * 65):
        reject("escaped private build label",
               lambda item=value: module.checked_label(item))
    for value in ("/", "/tmp", ROOT, ROOT + "/tmp", "/tmp/../tmp/bad",
                  "/tmp/rebar-phase2-zig-other-root", "/tmp/" + ROOT_PREFIX + "a"):
        reject("escaped private build root", lambda item=value: module.checked_root(item))
    bridge = state["raw"][BRIDGE[0]]
    for hostile in (
        bridge.replace(COPYREG_LITERAL, b'PyImport_ImportModule("re")', 1),
        bridge.replace(COPYREG_LITERAL,
                       COPYREG_LITERAL + b'; PyImport_ImportModule("re")', 1),
        bridge.replace(COPYREG_LITERAL,
                       b'PyImport_ImportModule("_sre")', 1),
        bridge.replace(COPYREG_LITERAL,
                       b'PyImport_ImportModule("regex")', 1),
        bridge.replace(COPYREG_LITERAL, b'PyImport_Import("copyreg")', 1),
    ):
        def altered(raw=hostile) -> None:
            changed = dict(state)
            changed["protected"] = dict(state["protected"])
            changed["protected"][BRIDGE[0]] = raw
            changed["raw"] = dict(state["raw"])
            changed["raw"][BRIDGE[0]] = raw
            validate_sources(changed)
        reject("forged broader Python import exception", altered)
    wall = state["wall"]
    require(wall is not None and wall.contract_render is False,
            "hostile source tests require an active deny-default source wall")
    for label, path in (
        ("installed Zig engine", ROOT + "/candidates/_zig_probe.so"),
        ("installed Zig bridge", ROOT + "/candidates/_zig_bridge.so"),
        ("holdout proposal", ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json"),
        ("holdout seed", ROOT + "/oracle/phase3/final.seed"),
        ("hidden cases", ROOT + "/oracle/phase3/final-hidden.json"),
        ("candidate raw archive", ROOT + "/oracle/phase2/evidence/zig.json.gz"),
        ("private build root", "/tmp/" + ROOT_PREFIX + "forbiddenroot"),
    ):
        reject(label, lambda target=path: wall.check(
            "open", (target, None, os.O_RDONLY | os.O_NOFOLLOW)))
    for label, event, values in (
        ("Zig compiler process", "subprocess.Popen", ("zig",)),
        ("candidate native loader", "ctypes.dlopen", ("_zig_probe.so",)),
        ("candidate import", "import", ("candidates.zig_candidate",)),
        ("stdlib regex import", "import", ("re",)),
        ("stdlib sre import", "import", ("_sre",)),
        ("external regex import", "import", ("regex",)),
        ("benchmark clock", "time.perf_counter", ()),
        ("network connection", "socket.connect", ("example.invalid",)),
        ("thread creation", "_thread.start_new_thread", ()),
        ("destructive rename", "os.rename", ("before", "after")),
    ):
        reject(label, lambda action=event, args=values: wall.check(action, args))
    templates = module.command_templates()
    require(len(templates) == 2
            and all(len(item["processes"]) == 13 for item in templates),
            "prove the complete independent 26-process build is implemented")
    require(len(labels) >= 90,
            "exercise comprehensive immutable source, guarded import, and boundary controls")
    return len(labels)


def source_result(state: dict, module: types.ModuleType,
                  *, hostile: bool) -> dict:
    validate_machine_contract(state["options"], state, module)
    controls = hostile_controls(state, module) if hostile else 0
    return {
        "schema": SCHEMA + "-source-only-result",
        "version": VERSION,
        "status": "PASS",
        "mode": "SELF-TEST" if hostile else "FROZEN CONTEXT",
        "source_sha256": state["options"].source_sha256,
        "protocol_sha256": state["options"].protocol_sha256,
        "contract_sha256": state["options"].contract_sha256,
        "corrected_adapter_sha256": ADAPTER[1],
        "corrected_adapter_bytes": ADAPTER[2],
        "corrected_bridge_source_sha256": BRIDGE[1],
        "corrected_bridge_source_bytes": BRIDGE[2],
        "first_party_engine_source_sha256": ENGINE[1],
        "first_party_engine_source_bytes": ENGINE[2],
        "strict_runtime_guard_version": 4,
        "strict_runtime_guard_source_sha256": GUARD["source"][1],
        "strict_runtime_guard_protocol_sha256": GUARD["protocol"][1],
        "strict_runtime_guard_contract_sha256": GUARD["contract"][1],
        "historical_zig_failure_receipt_sha256": FAILURE[1],
        "historical_zig_verified_passing_case_count": 4_607,
        "historical_zig_observed_semantic_mismatch_lower_bound": 1_700,
        "historical_zig_complete_semantic_mismatch_count": "NOT MEASURED",
        "original_case_execution_denominator": 31_237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "supplemental_reference_case_count": 8_244,
        "supplemental_counted_in_original_denominator": False,
        "future_independent_phase_count": 2,
        "future_processes_per_phase": 13,
        "future_total_processes": 26,
        "future_source_snapshots_per_phase": 3,
        "copyreg_helper_allowed_only_in_pinned_bridge": True,
        "copyreg_literal_occurrence_count": 1,
        "engine_python_module_import_allowed": False,
        "hostile_controls_rejected": controls,
        **source_effects(),
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def write_contract(result: dict) -> None:
    raw = canonical(result)
    descriptor = os.open(os.path.join(ROOT, CONTRACT),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(count > 0, "persist every exclusive V16 contract byte")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FreezeError("reject unauthorized V16 source-build action: " + message)


def arguments() -> argparse.Namespace:
    tokens = [item for item in sys.argv[1:] if item.startswith("--")]
    require(len(tokens) == len(set(tokens)),
            "reject duplicate V16 modes, pins, or root authorizations")
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--protocol-bytes", required=True, type=int)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--contract-bytes", type=int)
    for group in ("legacy", "campaign", "guard"):
        for name in ("source", "protocol", "contract"):
            parser.add_argument("--" + group + "-" + name + "-sha256", required=True)
    for name in ("engine", "adapter", "bridge", "lock", "failure"):
        parser.add_argument("--" + name + "-sha256", required=True)
    parser.add_argument("--label")
    parser.add_argument("--root-authorized", action="store_true")
    parser.add_argument("--frozen-committed-pushed", action="store_true")
    parser.add_argument("--frozen-commit")
    parser.add_argument("--pushed-commit")
    options = parser.parse_args()
    if options.render_contract:
        require(options.contract_sha256 is None and options.contract_bytes is None
                and options.label is None and options.root_authorized is False
                and options.frozen_committed_pushed is False
                and options.frozen_commit is None and options.pushed_commit is None,
                "render only the exclusive V16 contract without activating a build")
    elif options.build:
        require(options.contract_sha256 is not None
                and options.contract_bytes is not None and options.label is not None,
                "actual Zig builds require an independent frozen contract and label")
    else:
        require(options.contract_sha256 is not None
                and options.contract_bytes is not None and options.label is None
                and options.root_authorized is False
                and options.frozen_committed_pushed is False
                and options.frozen_commit is None and options.pushed_commit is None,
                "source gates cannot possess actual build authority or labels")
    return options


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1,
            "require exact isolated, no-site, bytecode-disabled stable CPython 3.14.6")
    if options.build:
        code, result = actual_build(options)
    else:
        state = context(options, wall=True)
        module = legacy_module(state)
        if options.render_contract:
            result = contract_document(state, module)
            write_contract(result)
            result = {
                "status": "PASS",
                "mode": "RENDER CONTRACT",
                "contract_sha256": digest(canonical(contract_document(state, module))),
                "contract_bytes": len(canonical(contract_document(state, module))),
                "candidate_workers_started": 0,
                "compiler_processes_started": 0,
                "holdout_proposals_opened": 0,
            }
        else:
            result = source_result(state, module, hostile=options.self_test)
        code = 0
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, TypeError, ValueError, KeyError, IndexError,
            struct.error, subprocess.SubprocessError, UnicodeError,
            RecursionError) as failure:
        sys.stderr.write("zig-full-semantic-source-build-v16: "
                         + type(failure).__name__ + ": " + str(failure) + "\n")
        raise SystemExit(1)
