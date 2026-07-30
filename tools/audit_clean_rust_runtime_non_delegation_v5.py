#!/usr/bin/env python3
"""Authenticate the exact clean, independently rebuilt first-party Rust engine."""

from __future__ import annotations

import ast
import builtins
import hashlib
import importlib
import io
import json
import os
import socket
import stat
import struct
import subprocess
import sys
import threading
import time
import tomllib


ROOT = "/home/dev-user/src/rebar"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/audit_clean_rust_runtime_non_delegation_v5.py"
PROTOCOL = "oracle/phase2/RUST-CLEAN-NON-DELEGATION-V5.md"
CONTRACT = "oracle/phase2/rust-clean-non-delegation-v5.json"
SCHEMA = "rebar-phase2-clean-first-party-rust-non-delegation-v5"
HEX = frozenset("0123456789abcdef")
MAX_SOURCE = 8 * 1024 * 1024
MAX_BINARY = 16 * 1024 * 1024
READ_CHUNK = 65536

V4_OWNERS = {
    "tools/audit_candidate_runtime_non_delegation_v4.py":
        "597f2f1156d773a42e32103ef7370e8552a416756910c013cdcd0cfc34d39b02",
    "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md":
        "6c3bd6b2ccabe3ab240771d743afce5b32f1de17a510bedd835e867c5cea7826",
    "oracle/phase2/runtime-non-delegation-v4.json":
        "edc3ac8866da7afb5934b56fbcbff38a908e5109f7975f998753b479aa7bc672",
}
V4_FAILURE_PATH = "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json"
V4_FAILURE = {
    "sha256": "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19",
    "bytes": 20985, "device": 2064, "inode": 526140, "mode": "0600",
}
V30_OWNERS = {
    "tools/reproduce_owned_rust_complete_semantic_source_build_v30.py":
        "dd0ed268775537b985a060e5f608c6bc2730f86922ad20ee78cff19e4c387a1d",
    "oracle/phase2/RUST-COMPLETE-SEMANTIC-SOURCE-BUILD-V30.md":
        "9f508fd651fa544ecea82487cb05bc94cce6aa1049ec676d257eb62fc73b3c61",
    "oracle/phase2/rust-complete-semantic-source-build-v30.json":
        "38e0a8f44cf1e3f68abb643b004f7f47350e743f5c3f1994d101b02e5ebc1956",
}
V30_PUBLICATION_PATH = (
    "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-"
    "complete-semantic-source-root-provenance-publication-receipt.json"
)
V30_PUBLICATION = {
    "sha256": "c29361f0436f73ada037ba497a0eb008eeadac6ebb41c50019521c0212448abd",
    "bytes": 3438, "device": 2064, "inode": 524977, "mode": "0600",
}
V30_ROOT_PATH = (
    "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-"
    "complete-semantic-source-root-provenance-root-provenance-receipt.json"
)
V30_ROOT = {
    "sha256": "26445b833ac0e846538a1f648059a1c8a224e4e2f1acd58f82e9458dcc142404",
    "bytes": 77160, "device": 2064, "inode": 524978, "mode": "0600",
}
PUBLIC_VARIANTS = {
    "candidates/rust/variants/complete_semantic_correction_v2/py_bridge.c":
        ("254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55", 178270),
    "candidates/rust/variants/combined_search_compiler_fastpath_v2/lib.rs":
        ("c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee", 189423),
    "candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs":
        ("4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7", 24305),
}
EXPECTED_PRIVATE_SOURCES = {
    "candidates/rust/Cargo.lock":
        ("267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, "lock"),
    "candidates/rust/Cargo.toml":
        ("2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, "manifest"),
    "candidates/rust/py_bridge.c":
        ("254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55", 178270, "c"),
    "candidates/rust/src/lib.rs":
        ("c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee", 189423, "rust"),
    "candidates/rust/src/newline.rs":
        ("13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416, "rust"),
    "candidates/rust/src/search.rs":
        ("4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7", 24305, "rust"),
    "candidates/rust/src/stack.rs":
        ("5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269, "rust"),
    "candidates/rust/src/unicode_tables.rs":
        ("f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989, "rust"),
    "candidates/rust_candidate.py":
        ("d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e", 31934, "python"),
}
PUBLIC_PROJECT = {
    "pyproject.toml": "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825",
    "uv.lock": "1f8402bb3fdda2c1ba57b5cfdcb1f8b835a4528784d553fe1219ca157f0750f2",
}
EXPECTED_NATIVE = {
    "engine": {
        "name": "_rust_engine.so",
        "sha256": "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237",
        "bytes": 672424, "mode": "0600",
    },
    "bridge": {
        "name": "_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256",
        "bytes": 148672, "mode": "0700",
    },
}
FORBIDDEN_ROOTS = frozenset({
    "_sre", "ahocorasick", "cffi", "ctypes", "hyperscan", "importlib", "inspect",
    "onig", "oniguruma", "pcre", "pcre2", "pyre2", "re", "re2", "regex",
    "regex_automata", "regex_lite", "regex_syntax", "regexp", "rure",
    "sre_compile", "sre_constants", "sre_parse", "tokenize",
})
SAFE_PYTHON_ROOTS = frozenset({
    "__future__", "copyreg", "enum", "operator", "os", "struct", "sys",
    "types", "unicodedata", "warnings",
})
SAFE_NATIVE_PYTHON_IMPORTS = frozenset({"copyreg", "functools", "unicodedata"})
SAFE_RUST_ROOTS = frozenset({
    "alloc", "core", "crate", "newline", "search", "self", "stack", "std",
    "super", "unicode_tables",
})
SAFE_HEADERS = frozenset({"Python.h", "stddef.h", "stdint.h", "string.h"})
SAFE_SYSTEM_LIBRARIES = frozenset({
    "libc.so.6", "libgcc_s.so.1", "libm.so.6", "ld-linux-x86-64.so.2",
})
FORBIDDEN_NATIVE = frozenset({
    "PyImport_AddModule", "PyImport_ExecCodeModule", "PyImport_GetModule",
    "PyImport_GetModuleDict", "PyImport_Import", "PyImport_ImportModuleLevel",
    "PyImport_ImportModuleLevelObject", "PyRun_AnyFile", "PyRun_SimpleString",
    "PyRun_String", "PyRun_StringFlags", "PyEval_EvalCode", "Py_CompileString",
    "Py_CompileStringExFlags", "GetProcAddress", "LoadLibrary", "LoadLibraryA",
    "LoadLibraryW", "dlopen", "dlmopen", "dlsym", "dlvsym", "execve", "fork",
    "popen", "posix_spawn", "posix_spawnp", "regcomp", "regexec", "system",
})
FORBIDDEN_PREFIXES = ("pcre", "onig", "re2_", "hs_", "hyperscan", "rure_", "tre_")
FOREIGN_FAMILY_PREFIXES = (
    "vm_", "rebar_zig_", "rebar_cpp_", "rebar_go_", "rebar_fortran_",
    "PyInit__vm_native", "PyInit__zig_bridge", "PyInit__cpp_bridge",
    "PyInit__go_bridge", "PyInit__fortran_bridge",
)
_OPEN, _READ, _FSTAT, _CLOSE = os.open, os.read, os.fstat, os.close


class AuditError(Exception):
    """An exact frozen owner, first-party boundary, or effect gate failed."""


def require(value: object, message: str) -> None:
    if not value:
        raise AuditError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("ascii")


def exact_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64 and frozenset(value) <= HEX,
            label + ": expected exactly 64 lowercase SHA-256 digits")
    return value


def strict_json(raw: bytes, label: str) -> dict[str, object]:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        answer: dict[str, object] = {}
        for key, value in pairs:
            require(type(key) is str and key not in answer, label + ": duplicate JSON object key")
            answer[key] = value
        return answer

    try:
        answer = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                            parse_constant=lambda token: (_ for _ in ()).throw(
                                AuditError(label + ": non-finite JSON constant " + token)))
    except (ValueError, UnicodeError, TypeError) as error:
        raise AuditError(label + ": invalid strict JSON") from error
    require(type(answer) is dict, label + ": expected one JSON object")
    return answer


def effects_template() -> dict[str, int]:
    return {name: 0 for name in (
        "approved_owner_reads", "historical_v4_owner_reads", "historical_failure_reads",
        "public_build_owner_reads", "public_build_receipt_reads", "public_variant_reads",
        "project_owner_reads", "private_root_opens", "private_phase_opens",
        "private_source_reads", "private_binary_reads", "candidate_imports",
        "candidate_executions", "candidate_workers", "native_library_loads",
        "compiler_processes", "subprocesses", "archive_reads", "archive_decompressions",
        "holdout_reads", "hidden_case_reads", "benchmark_reads", "network_requests",
        "threads_started", "clock_samples", "workspace_mutations", "git_reads",
        "blocked_reads", "blocked_writes", "blocked_imports", "blocked_processes",
        "blocked_network", "blocked_threads", "blocked_clocks", "blocked_native_loads",
        "blocked_audit_hooks",
    )}


class EffectWall:
    def __init__(self) -> None:
        self.effects = effects_template()
        self.originals: list[tuple[object, str, object]] = []

    def block(self, owner: object, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def denied(*args: object, **kwargs: object) -> object:
            self.effects[category] += 1
            raise AuditError("effect wall rejected " + name)

        self.originals.append((owner, name, previous))
        setattr(owner, name, denied)

    def __enter__(self) -> EffectWall:
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                            (os, "read"), (os, "stat"), (os, "lstat"), (os, "fstat"),
                            (os, "listdir"), (os, "scandir"), (os, "walk")):
            self.block(owner, name, "blocked_reads")
        for name in ("write", "unlink", "remove", "mkdir", "makedirs", "rename", "replace",
                     "rmdir", "chmod", "chown", "link", "symlink", "truncate", "utime", "fsync"):
            self.block(os, name, "blocked_writes")
        self.block(builtins, "__import__", "blocked_imports")
        self.block(importlib, "import_module", "blocked_imports")
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            self.block(subprocess, name, "blocked_processes")
        for name in ("system", "popen", "fork", "posix_spawn", "posix_spawnp"):
            self.block(os, name, "blocked_processes")
        self.block(threading.Thread, "start", "blocked_threads")
        self.block(socket, "create_connection", "blocked_network")
        self.block(socket.socket, "connect", "blocked_network")
        self.block(sys, "addaudithook", "blocked_audit_hooks")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
                     "thread_time_ns", "sleep"):
            self.block(time, name, "blocked_clocks")
        for module_name in ("ctypes", "_ctypes"):
            module = sys.modules.get(module_name)
            if module is not None:
                for name in ("CDLL", "PyDLL", "WinDLL", "OleDLL", "dlopen", "_dlopen"):
                    self.block(module, name, "blocked_native_loads")
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        for owner, name, value in reversed(self.originals):
            setattr(owner, name, value)


def checked_parts(path: str, *, allow_evidence: bool = False,
                  allow_candidate: bool = False) -> tuple[str, ...]:
    require(type(path) is str and bool(path) and "\x00" not in path and "\\" not in path
            and not path.startswith("/"), "owner path must be an exact relative path")
    pieces = path.split("/")
    require(all(part not in {"", ".", "..", ".git", ".agents", ".codex", "__pycache__"}
                for part in pieces), "owner path contains traversal, metadata, or caches")
    for item in pieces:
        lowered = item.casefold()
        require(not any(fragment in lowered for fragment in
                        ("holdout", "hidden", "benchmark", "postfinal", "archive")),
                "owner path attempts to reach private final cases or archives")
        require(lowered != "performance", "owner path attempts to enter performance data")
        if lowered == "evidence":
            require(allow_evidence and path in {
                V4_FAILURE_PATH, V30_PUBLICATION_PATH, V30_ROOT_PATH,
            }, "only the three exact public, historical/provenance receipts are allowed")
        if lowered == "candidates":
            require(allow_candidate, "source-only mode cannot open candidate-owned source")
    return tuple(pieces)


def read_under(directory: int, parts: tuple[str, ...], label: str, wall: EffectWall,
               category: str, maximum: int = MAX_SOURCE,
               expected: dict[str, object] | None = None) -> tuple[bytes, dict[str, object]]:
    require(bool(parts), "an owner requires a nonempty descriptor-relative path")
    handles: list[int] = []
    try:
        parent = directory
        for part in parts[:-1]:
            require(part not in {"", ".", ".."} and "/" not in part,
                    "descriptor path contains traversal")
            child = _OPEN(part, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                          dir_fd=parent)
            handles.append(child)
            parent = child
        descriptor = _OPEN(parts[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                           dir_fd=parent)
        handles.append(descriptor)
        before = _FSTAT(descriptor)
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum
                and before.st_nlink == 1 and before.st_uid == os.getuid(),
                label + ": require a bounded owner-only regular, single-link file")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            piece = _READ(descriptor, min(remaining, READ_CHUNK))
            require(bool(piece), label + ": owner was truncated during authentication")
            chunks.append(piece)
            remaining -= len(piece)
        require(not _READ(descriptor, 1), label + ": owner grew during authentication")
        after = _FSTAT(descriptor)
        identity = lambda item: (item.st_dev, item.st_ino, item.st_size,
                                 item.st_mtime_ns, item.st_ctime_ns, item.st_nlink)
        require(identity(before) == identity(after), label + ": owner changed while authenticated")
        raw = b"".join(chunks)
        owner = {
            "path": label, "sha256": digest(raw), "bytes": len(raw),
            "device": before.st_dev, "inode": before.st_ino,
            "mode": format(stat.S_IMODE(before.st_mode), "04o"),
            "uid": before.st_uid, "nlink": before.st_nlink,
        }
        if expected is not None:
            for key, value in expected.items():
                require(owner.get(key) == value, label + ": pinned " + key + " changed")
        wall.effects["approved_owner_reads"] += 1
        if category != "approved_owner_reads":
            wall.effects[category] += 1
        return raw, owner
    finally:
        for descriptor in reversed(handles):
            _CLOSE(descriptor)


def read_public(path: str, wall: EffectWall, category: str,
                *, expected: dict[str, object] | None = None,
                allow_candidate: bool = False, maximum: int = MAX_SOURCE
                ) -> tuple[bytes, dict[str, object]]:
    pieces = checked_parts(path, allow_evidence=(category in {
        "historical_failure_reads", "public_build_receipt_reads",
    }), allow_candidate=allow_candidate)
    descriptor = _OPEN(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        return read_under(descriptor, pieces, path, wall, category, maximum, expected)
    finally:
        _CLOSE(descriptor)


def verify_runtime_pins() -> None:
    require(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE,
            "use only isolated, bytecode-disabled, pinned CPython 3.14.6")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules), "candidate modules were imported before the effect wall")


def verify_history(wall: EffectWall) -> tuple[dict[str, object], dict[str, object]]:
    v4_owners: dict[str, dict[str, object]] = {}
    for path, expected_sha in V4_OWNERS.items():
        _, owner = read_public(path, wall, "historical_v4_owner_reads",
                               expected={"sha256": expected_sha, "mode": "0600"})
        v4_owners[path] = owner
    failure_raw, failure_owner = read_public(V4_FAILURE_PATH, wall,
                                            "historical_failure_reads", expected=V4_FAILURE)
    failure = strict_json(failure_raw, V4_FAILURE_PATH)
    findings = failure.get("findings")
    previous_effects = failure.get("effects")
    require(failure.get("schema") ==
            "rebar-phase2-first-party-runtime-non-delegation-v4-root-static-audit"
            and failure.get("status") == "FAIL" and failure.get("finding_count") == 1
            and failure.get("candidate_family_count") == 6
            and type(findings) is list and len(findings) == 1
            and type(findings[0]) is dict
            and findings[0].get("family") == "rust"
            and findings[0].get("path") == "candidates/rust/py_bridge.c"
            and findings[0].get("line") == 4403
            and findings[0].get("code") == "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE"
            and failure.get("candidate_qualified") is False
            and failure.get("runtime_non_delegation") ==
            "NOT ESTABLISHED; CANDIDATES NEVER EXECUTED"
            and type(previous_effects) is dict
            and all(previous_effects.get(name) == 0 for name in (
                "candidate_imports", "candidate_executions", "candidate_workers",
                "native_library_loads", "compiler_processes", "archive_reads",
                "archive_decompressions", "holdout_reads", "workspace_mutations",
            )), "the genuine V4 FAIL-one history was replaced, hidden, or overstated")

    v30_owners: dict[str, dict[str, object]] = {}
    for path, expected_sha in V30_OWNERS.items():
        _, owner = read_public(path, wall, "public_build_owner_reads",
                               expected={"sha256": expected_sha, "mode": "0600"})
        v30_owners[path] = owner
    publication_raw, publication_owner = read_public(
        V30_PUBLICATION_PATH, wall, "public_build_receipt_reads", expected=V30_PUBLICATION)
    provenance_raw, provenance_owner = read_public(
        V30_ROOT_PATH, wall, "public_build_receipt_reads", expected=V30_ROOT)
    publication = strict_json(publication_raw, V30_PUBLICATION_PATH)
    provenance = strict_json(provenance_raw, V30_ROOT_PATH)
    validate_build_receipts(publication, provenance)
    return ({"owners": v4_owners, "actual_failure_receipt": failure_owner,
             "status": "FAIL", "finding_count": 1,
             "finding_code": "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
             "finding_path": "candidates/rust/py_bridge.c",
             "historical_failure_preserved": True},
            {"owners": v30_owners, "publication_owner": publication_owner,
             "root_provenance_owner": provenance_owner,
             "publication": publication, "provenance": provenance})


def validate_build_receipts(publication: dict[str, object],
                            provenance: dict[str, object]) -> None:
    require(publication.get("schema") ==
            "rebar-phase2-owned-rust-complete-semantic-source-build-v30-durable-publication-receipt"
            and publication.get("status") == "PASS"
            and publication.get("actual_completed_phase_count") == 2
            and publication.get("actual_compiler_process_count") == 28
            and publication.get("external_cargo_dependency_count") == 0
            and publication.get("candidate_matching") == "NOT RUN"
            and publication.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and publication.get("candidate_qualified") is False
            and publication.get("hidden_cases_generated") == 0,
            "the real V30 two-phase, 28-process, dependency-free publication changed")
    require(provenance.get("schema") ==
            "rebar-phase2-owned-rust-complete-semantic-source-build-v30-durable-root-provenance-receipt"
            and provenance.get("status") == "PASS"
            and provenance.get("actual_source_phase_count") == 2
            and provenance.get("actual_compiler_process_count") == 28
            and provenance.get("distinct_private_source_identity_count") == 18
            and provenance.get("total_private_source_overlay_apply_count") == 8
            and provenance.get("cross_phase_complete_bridge_elf_byte_identical") is True
            and provenance.get("cross_phase_complete_engine_elf_byte_identical") is True
            and provenance.get("all_original_runtime_target_identities_restored") is True
            and provenance.get("all_original_source_identities_restored") is True
            and provenance.get("candidate_matching") == "NOT RUN"
            and provenance.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and provenance.get("candidate_qualified") is False
            and provenance.get("hidden_cases_generated") == 0,
            "authentic V30 root provenance no longer records two safe independent phases")
    for field, expected in (
        ("source_sha256", V30_OWNERS["tools/reproduce_owned_rust_complete_semantic_source_build_v30.py"]),
        ("protocol_sha256", V30_OWNERS["oracle/phase2/RUST-COMPLETE-SEMANTIC-SOURCE-BUILD-V30.md"]),
        ("contract_sha256", V30_OWNERS["oracle/phase2/rust-complete-semantic-source-build-v30.json"]),
        ("combined_engine_source_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust/src/lib.rs"][0]),
        ("combined_search_source_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust/src/search.rs"][0]),
        ("materialized_complete_bridge_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust/py_bridge.c"][0]),
        ("safe_no_external_introspection_bridge_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust/py_bridge.c"][0]),
        ("corrected_public_adapter_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust_candidate.py"][0]),
    ):
        require(publication.get(field) == expected and provenance.get(field) == expected,
                "V30 publication/root disagree on first-party frozen owner " + field)
    for field, expected in (
        ("combined_engine_source_bytes", 189423), ("combined_search_source_bytes", 24305),
        ("materialized_complete_bridge_bytes", 178270),
        ("corrected_public_adapter_bytes", 31934),
    ):
        require(publication.get(field) == expected and provenance.get(field) == expected,
                "V30 publication/root disagree on frozen source byte count " + field)
    require(provenance.get("canonical_build_receipt_sha256") == V30_PUBLICATION["sha256"]
            and provenance.get("canonical_build_receipt_bytes") == V30_PUBLICATION["bytes"]
            and provenance.get("canonical_build_receipt_device") == V30_PUBLICATION["device"]
            and provenance.get("canonical_build_receipt_inode") == V30_PUBLICATION["inode"]
            and provenance.get("canonical_build_receipt_relative") == V30_PUBLICATION_PATH,
            "V30 root provenance is not bound to the exact independently published receipt")
    root = provenance.get("root")
    phases = provenance.get("phase_native_outputs")
    private = provenance.get("actual_private_source_owners")
    require(type(root) is dict and root.get("prefix") == "/tmp/rebar-phase2-native-build-v9-rust-"
            and type(root.get("path")) is str and root["path"].startswith(root["prefix"])
            and root.get("mode") == "0700" and root.get("uid") == os.getuid()
            and root.get("phase_count") == 2 and root.get("directory_scanned") is False
            and type(phases) is list and type(private) is list
            and len(phases) == 2 and len(private) == 2,
            "V30 private build roots are no longer exactly two owned non-enumerated phases")
    native_identities: set[tuple[int, int]] = set()
    source_identities: set[tuple[int, int]] = set()
    for index, name in enumerate(("reference-a", "reference-b")):
        phase, source = phases[index], private[index]
        require(type(phase) is dict and phase.get("name") == name
                and type(source) is dict and source.get("phase") == name
                and phase.get("uid") == os.getuid() and phase.get("mode") == "0700"
                and type(phase.get("native_outputs")) is list
                and len(phase["native_outputs"]) == 2
                and type(source.get("owners")) is dict
                and set(source["owners"]) == set(EXPECTED_PRIVATE_SOURCES),
                name + ": private source/native inventory changed")
        for path, (expected_sha, expected_bytes, _) in EXPECTED_PRIVATE_SOURCES.items():
            item = source["owners"][path]
            require(type(item) is dict and item.get("sha256") == expected_sha
                    and item.get("bytes") == expected_bytes
                    and item.get("device") == root.get("device")
                    and type(item.get("inode")) is int and item["inode"] > 0
                    and item.get("same_inode_readback_verified") is True,
                    name + ": untrusted private source provenance for " + path)
            source_identities.add((item["device"], item["inode"]))
        for item in phase["native_outputs"]:
            require(type(item) is dict and item.get("role") in EXPECTED_NATIVE,
                    name + ": unknown native artifact")
            expected = EXPECTED_NATIVE[item["role"]]
            require(item.get("file_name") == expected["name"]
                    and item.get("sha256") == expected["sha256"]
                    and item.get("bytes") == expected["bytes"]
                    and item.get("mode") == expected["mode"]
                    and item.get("device") == root.get("device")
                    and item.get("nlink") == 1 and item.get("uid") == os.getuid()
                    and item.get("native_loaded") is False,
                    name + ": native artifact no longer has its exact first-party identity")
            native_identities.add((item["device"], item["inode"]))
    require(len(source_identities) == 18 and len(native_identities) == 4,
            "independent private Rust phases no longer have 18 source / four native identities")
    outputs = provenance.get("actual_reproduced_native_outputs")
    require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
            "V30 root provenance omits exact first-party native engine/bridge proofs")
    for role, expected in EXPECTED_NATIVE.items():
        item = outputs[role]
        audit = item.get("audit") if type(item) is dict else None
        require(type(item) is dict and item.get("sha256") == expected["sha256"]
                and item.get("size_bytes") == expected["bytes"]
                and item.get("file_name") == expected["name"]
                and item.get("fresh_independent_inode_count") == 2
                and item.get("reproduced_in_two_fresh_directories") is True
                and type(audit) is dict and audit.get("role") == role
                and audit.get("external_regex_dependency_count") == 0
                and audit.get("cross_family_dependency_count") == 0,
                "V30 root provenance no longer proves zero foreign ELF dependencies: " + role)


def validate_contract(payload: dict[str, object]) -> None:
    freeze = payload.get("source_freeze")
    lineage = payload.get("immutable_v4")
    build = payload.get("authenticated_v30")
    boundary = payload.get("boundaries")
    require(payload.get("schema") == SCHEMA and payload.get("version") == 5
            and type(freeze) is dict and type(lineage) is dict and type(build) is dict
            and type(boundary) is dict and freeze.get("source_path") == SOURCE
            and freeze.get("protocol_path") == PROTOCOL and freeze.get("contract_path") == CONTRACT
            and freeze.get("sole_owned_file_count") == 3
            and lineage.get("failure_receipt_sha256") == V4_FAILURE["sha256"]
            and lineage.get("historical_status") == "FAIL"
            and lineage.get("historical_finding_count") == 1
            and build.get("publication_receipt_sha256") == V30_PUBLICATION["sha256"]
            and build.get("root_receipt_sha256") == V30_ROOT["sha256"]
            and build.get("exact_phase_count") == 2
            and build.get("exact_source_owner_count") == 18
            and build.get("exact_native_owner_count") == 4
            and build.get("actual_compiler_process_count") == 28
            and build.get("external_cargo_dependencies") == 0
            and boundary.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and boundary.get("root_only_static_audit") is True
            and boundary.get("candidate_qualified") is False
            and boundary.get("final_cases_generated") == 0
            and boundary.get("performance") == "NOT MEASURED",
            "V5 contract weakens frozen candidate, predecessor, or effect boundaries")
    for key, expected in (("clean_bridge_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust/py_bridge.c"][0]),
                          ("engine_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust/src/lib.rs"][0]),
                          ("search_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust/src/search.rs"][0]),
                          ("adapter_sha256", EXPECTED_PRIVATE_SOURCES["candidates/rust_candidate.py"][0])):
        require(build.get(key) == expected, "V5 contract changed the exact first-party source " + key)


def enforce_zero_effects(effects: dict[str, int], *, verify: bool = False,
                         audit: bool = False) -> None:
    permitted = {"approved_owner_reads"}
    if verify or audit:
        permitted |= {"historical_v4_owner_reads", "historical_failure_reads",
                      "public_build_owner_reads", "public_build_receipt_reads"}
    if audit:
        permitted |= {"public_variant_reads", "project_owner_reads", "private_root_opens",
                      "private_phase_opens", "private_source_reads", "private_binary_reads"}
    for key, value in effects.items():
        if key not in permitted:
            require(value == 0, "audit escaped its frozen read-only boundary: " + key)
    if verify:
        require(effects["approved_owner_reads"] == 12
                and effects["historical_v4_owner_reads"] == 3
                and effects["historical_failure_reads"] == 1
                and effects["public_build_owner_reads"] == 3
                and effects["public_build_receipt_reads"] == 2,
                "source-only verification opened an unapproved owner")
    if audit:
        require(effects["approved_owner_reads"] == 38
                and effects["historical_v4_owner_reads"] == 3
                and effects["historical_failure_reads"] == 1
                and effects["public_build_owner_reads"] == 3
                and effects["public_build_receipt_reads"] == 2
                and effects["public_variant_reads"] == 3
                and effects["project_owner_reads"] == 2
                and effects["private_root_opens"] == 1
                and effects["private_phase_opens"] == 2
                and effects["private_source_reads"] == 18
                and effects["private_binary_reads"] == 4,
                "root audit opened owners outside its exact first-party source/native inventory")


def source_verify(options: dict[str, object]) -> dict[str, object]:
    verify_runtime_pins()
    pins = {SOURCE: exact_sha(options.get("source_sha256"), "V5 source"),
            PROTOCOL: exact_sha(options.get("protocol_sha256"), "V5 protocol"),
            CONTRACT: exact_sha(options.get("contract_sha256"), "V5 contract")}
    require(len(set(pins.values())) == 3, "three independent exact V5 owner pins are required")
    with EffectWall() as wall:
        owners: dict[str, dict[str, object]] = {}
        raw: dict[str, bytes] = {}
        for path in (SOURCE, PROTOCOL, CONTRACT):
            content, owner = read_public(path, wall, "approved_owner_reads",
                                         expected={"sha256": pins[path], "mode": "0600"})
            owners[path], raw[path] = owner, content
        contract = strict_json(raw[CONTRACT], CONTRACT)
        validate_contract(contract)
        freeze = contract["source_freeze"]
        require(type(freeze) is dict and freeze.get("source_sha256") == pins[SOURCE]
                and freeze.get("protocol_sha256") == pins[PROTOCOL],
                "V5 contract no longer binds the independently supplied source/protocol pins")
        historical, build = verify_history(wall)
        counts = dict(wall.effects)
        enforce_zero_effects(counts, verify=True)
    return {
        "schema": SCHEMA + "-source-verification", "status": "PASS",
        "phase": "SOURCE ONLY; CANDIDATE AND PRIVATE BUILD OWNERS NOT OPENED",
        "owners": owners, "immutable_v4": historical,
        "authenticated_v30": {"publication_owner": build["publication_owner"],
                              "root_provenance_owner": build["root_provenance_owner"],
                              "actual_compiler_process_count": 28,
                              "external_cargo_dependencies": 0,
                              "private_root_opened": False},
        "effects": counts, "candidate_source_audit": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED", "candidate_qualified": False,
        "final_cases_generated": 0, "performance": "NOT MEASURED", "winner_selected": False,
    }


def folded(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and type(node.value) is str:
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = folded(node.left), folded(node.right)
        return left + right if left is not None and right is not None else None
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "chr" and len(node.args) == 1 and not node.keywords
            and isinstance(node.args[0], ast.Constant)
            and type(node.args[0].value) is int and 0 <= node.args[0].value <= 0x10FFFF):
        return chr(node.args[0].value)
    return None


def ast_chain(node: ast.AST) -> tuple[str, ...] | None:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        head = ast_chain(node.value)
        return head + (node.attr,) if head is not None else None
    return None


class RustPythonInspector(ast.NodeVisitor):
    def __init__(self, label: str) -> None:
        self.label = label
        self.imports: set[str] = set()
        self.owned_bridge_count = 0
        self.aliases: dict[str, tuple[str, ...]] = {}
        self.descriptor_calls = 0
        self.bind_calls = 0

    def fail(self, node: ast.AST, message: str) -> None:
        raise AuditError(f"{self.label}:{getattr(node, 'lineno', 0)}: {message}")

    def chain(self, node: ast.AST) -> tuple[str, ...] | None:
        value = ast_chain(node)
        return self.aliases.get(value[0], (value[0],)) + value[1:] if value else None

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            module, root = item.name, item.name.split(".", 1)[0]
            if root in FORBIDDEN_ROOTS or root not in SAFE_PYTHON_ROOTS:
                self.fail(node, "forbidden or external candidate-owned module " + module)
            self.imports.add(module)
            self.aliases[item.asname or root] = tuple(module.split("."))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level:
            self.fail(node, "relative or computed candidate-owned imports are forbidden")
        module = node.module or ""
        if module == "candidates":
            if len(node.names) != 1 or node.names[0].name != "_rust_bridge" \
                    or node.names[0].asname is not None:
                self.fail(node, "Rust may import only its exact first-party bridge")
            self.owned_bridge_count += 1
            self.aliases["_rust_bridge"] = ("candidates", "_rust_bridge")
            return
        root = module.split(".", 1)[0]
        if root in FORBIDDEN_ROOTS or root not in SAFE_PYTHON_ROOTS:
            self.fail(node, "forbidden or external candidate-owned module " + module)
        self.imports.add(module)
        for item in node.names:
            if item.name == "*":
                self.fail(node, "unbounded candidate-owned star imports are forbidden")
            self.aliases[item.asname or item.name] = tuple(module.split(".")) + (item.name,)

    def visit_Assign(self, node: ast.Assign) -> None:
        chain = self.chain(node.value)
        if chain is not None:
            for item in node.targets:
                if isinstance(item, ast.Name):
                    self.aliases[item.id] = chain
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        chain = self.chain(node.func)
        if chain:
            tail = chain[-1]
            if tail in {"__import__", "import_module", "module_from_spec", "spec_from_file_location",
                        "exec_module", "CDLL", "PyDLL", "WinDLL", "OleDLL", "LoadLibrary",
                        "dlopen", "dlsym", "CFUNCTYPE", "eval", "exec", "system", "popen",
                        "Popen", "posix_spawn"}:
                self.fail(node, "computed import, external engine, loader, or process dispatch " + tail)
            if chain in {("candidates", "_rust_bridge", "pattern_descriptors"),
                         ("_rust_bridge", "pattern_descriptors")}:
                self.descriptor_calls += 1
            if chain in {("candidates", "_rust_bridge", "bind"), ("_rust_bridge", "bind"),
                         ("_NATIVE_BIND",)}:
                self.bind_calls += 1
                self.fail(node, "the private native bind capability cannot execute production matching")
        if chain == ("getattr",) and len(node.args) >= 2:
            receiver, key = self.chain(node.args[0]), folded(node.args[1])
            if receiver and (receiver[0] in FORBIDDEN_ROOTS or receiver[0] in {"sys", "builtins"}) \
                    and (key is None or key in {"__import__", "modules", "__dict__", "CDLL", "dlopen"}):
                self.fail(node, "computed access to a hidden engine or dynamic loader")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        chain, key = self.chain(node.value), folded(node.slice)
        if chain == ("sys", "modules") and (key is None or key.split(".", 1)[0] in FORBIDDEN_ROOTS):
            self.fail(node, "hidden candidate-owned engine access through sys.modules")
        self.generic_visit(node)


def inspect_python(source: str, label: str, *, require_descriptor: bool = True) -> dict[str, object]:
    try:
        tree = ast.parse(source, filename=label)
    except (SyntaxError, RecursionError, ValueError) as error:
        raise AuditError(label + ": invalid first-party Python adapter source") from error
    visitor = RustPythonInspector(label)
    visitor.visit(tree)
    require(visitor.owned_bridge_count == 1,
            label + ": candidate must import exactly one same-family first-party bridge")
    if require_descriptor:
        require(visitor.descriptor_calls >= 1 and visitor.bind_calls == 0,
                label + ": public methods must use direct native descriptors only")
    return {"kind": "python", "imports": sorted(visitor.imports),
            "owned_bridge_import_count": visitor.owned_bridge_count,
            "public_native_descriptor_calls": visitor.descriptor_calls,
            "private_bind_calls": visitor.bind_calls,
            "external_regex_packages": 0, "source_parsed_not_executed": True}


def identifier_start(value: str) -> bool:
    return bool(value) and (value == "_" or value.isalpha())


def identifier_part(value: str) -> bool:
    return bool(value) and (value == "_" or value.isalnum())


def native_tokens(source: str, label: str, rust: bool) -> list[tuple[str, str, int]]:
    result: list[tuple[str, str, int]] = []
    cursor, line, size = 0, 1, len(source)
    while cursor < size:
        char = source[cursor]
        if char.isspace():
            line += char == "\n"
            cursor += 1
            continue
        if source.startswith("//", cursor):
            stop = source.find("\n", cursor + 2)
            cursor = size if stop < 0 else stop
            continue
        if source.startswith("/*", cursor):
            origin, depth = line, 1
            cursor += 2
            while cursor < size and depth:
                if source.startswith("/*", cursor):
                    depth += 1
                    cursor += 2
                elif source.startswith("*/", cursor):
                    depth -= 1
                    cursor += 2
                else:
                    line += source[cursor] == "\n"
                    cursor += 1
            require(depth == 0, f"{label}:{origin}: unterminated nested source comment")
            continue
        if rust:
            prefix = next((value for value in ("br", "cr", "r")
                           if source.startswith(value, cursor)), "")
            if prefix:
                start = cursor + len(prefix)
                end = start
                while end < size and source[end] == "#":
                    end += 1
                if end < size and source[end] == '"':
                    hashes = end - start
                    require(hashes <= 255, f"{label}:{line}: excessive raw-string delimiter")
                    delimiter = '"' + "#" * hashes
                    finish = source.find(delimiter, end + 1)
                    require(finish >= 0, f"{label}:{line}: unterminated Rust raw string")
                    after = finish + len(delimiter)
                    require(after >= size or source[after] != "#",
                            f"{label}:{line}: inconsistent Rust raw-string delimiter")
                    value = source[end + 1:finish]
                    result.append(("string", value, line))
                    line += value.count("\n")
                    cursor = after
                    continue
            byte_character = source.startswith("b'", cursor)
            if char == "'" or byte_character:
                quote = cursor + int(byte_character)
                require(quote + 1 < size, f"{label}:{line}: incomplete Rust character or lifetime")
                first = quote + 1
                if source[first] == "\\":
                    at = first + 1
                    require(at < size, f"{label}:{line}: truncated Rust character escape")
                    marker = source[at]
                    if marker == "x":
                        digits = source[at + 1:at + 3]
                        require(len(digits) == 2 and all(item in "0123456789abcdefABCDEF"
                                                         for item in digits),
                                f"{label}:{line}: malformed Rust hexadecimal character escape")
                        at += 3
                    elif marker == "u":
                        require(not byte_character and at + 1 < size and source[at + 1] == "{",
                                f"{label}:{line}: malformed Rust Unicode character escape")
                        finish = source.find("}", at + 2)
                        digits = source[at + 2:finish] if finish >= 0 else ""
                        require(1 <= len(digits.replace("_", "")) <= 6
                                and all(item in "0123456789abcdefABCDEF_" for item in digits),
                                f"{label}:{line}: malformed Rust Unicode character escape")
                        at = finish + 1
                    else:
                        require(marker in {"n", "r", "t", "0", "\\", "'", '"'},
                                f"{label}:{line}: invalid Rust character escape")
                        at += 1
                    require(at < size and source[at] == "'",
                            f"{label}:{line}: unterminated Rust character literal")
                    result.append(("literal", source[cursor:at + 1], line))
                    cursor = at + 1
                    continue
                first_char = source[first]
                require(first_char not in {"\n", "\r", "'"},
                        f"{label}:{line}: malformed Rust character or lifetime")
                if identifier_start(first_char):
                    at = first + 1
                    while at < size and identifier_part(source[at]):
                        at += 1
                    if at < size and source[at] == "'":
                        require(at == first + 1 and (not byte_character or ord(first_char) < 128),
                                f"{label}:{line}: malformed Rust character literal")
                        result.append(("literal", source[cursor:at + 1], line))
                        cursor = at + 1
                    else:
                        require(not byte_character, f"{label}:{line}: byte literal is not a lifetime")
                        result.append(("lifetime", source[first:at], line))
                        cursor = at
                    continue
                require(first + 1 < size and source[first + 1] == "'"
                        and (not byte_character or ord(first_char) < 128),
                        f"{label}:{line}: malformed Rust literal")
                result.append(("literal", source[cursor:first + 2], line))
                cursor = first + 2
                continue
        prefixed = rust and (source.startswith('b"', cursor) or source.startswith('c"', cursor))
        if char == '"' or (not rust and char == "'") or prefixed:
            origin, start = line, cursor
            if prefixed:
                cursor += 1
            quote = source[cursor]
            cursor += 1
            while cursor < size and source[cursor] != quote:
                if source[cursor] == "\n":
                    require(rust, f"{label}:{origin}: unterminated native literal")
                    line += 1
                if source[cursor] == "\\":
                    cursor += 1
                    require(cursor < size, f"{label}:{origin}: truncated native escape")
                    line += source[cursor] == "\n"
                cursor += 1
            require(cursor < size, f"{label}:{origin}: unterminated native literal")
            text = source[start:cursor + 1]
            if quote == '"':
                if rust:
                    value = text[1 + int(prefixed):-1]
                else:
                    try:
                        value = ast.literal_eval(text)
                    except (SyntaxError, ValueError, TypeError) as error:
                        raise AuditError(f"{label}:{origin}: malformed C string") from error
                    require(type(value) is str, f"{label}:{origin}: C string is not text")
                result.append(("string", value, origin))
            else:
                result.append(("literal", text, origin))
            cursor += 1
            continue
        if char.isalpha() or char == "_":
            if rust and source.startswith("r#", cursor) and cursor + 2 < size \
                    and identifier_start(source[cursor + 2]):
                cursor += 2
            end = cursor + 1
            while end < size and (source[end].isalnum() or source[end] == "_"):
                end += 1
            result.append(("identifier", source[cursor:end], line))
            cursor = end
            continue
        result.append(("punctuation", char, line))
        cursor += 1
    return result


def inspect_native(source: str, label: str, kind: str) -> dict[str, object]:
    tokens = native_tokens(source, label, kind == "rust")
    modules: list[str] = []
    headers: list[str] = []
    for index, (token_kind, value, line) in enumerate(tokens):
        if token_kind != "identifier":
            continue
        lowered = value.casefold()
        require(value not in FORBIDDEN_NATIVE and not lowered.startswith(FORBIDDEN_PREFIXES)
                and not value.startswith(FOREIGN_FAMILY_PREFIXES),
                f"{label}:{line}: foreign regular-expression engine or dynamic dispatch {value}")
        if value in {"RE2", "libloading"}:
            raise AuditError(f"{label}:{line}: non-first-party regular-expression/native loader {value}")
        if value == "PyImport_ImportModule":
            require(index + 2 < len(tokens) and tokens[index + 1][1] == "("
                    and tokens[index + 2][0] == "string",
                    f"{label}:{line}: computed native Python import is forbidden")
            end, pieces = index + 2, []
            while end < len(tokens) and tokens[end][0] == "string":
                pieces.append(tokens[end][1])
                end += 1
            require(end < len(tokens) and tokens[end][1] == ")",
                    f"{label}:{line}: computed native Python import is forbidden")
            module = "".join(pieces)
            require(module in SAFE_NATIVE_PYTHON_IMPORTS,
                    f"{label}:{line}: native bridge imports forbidden Python module {module}")
            modules.append(module)
        if value == "define" and index and tokens[index - 1][1] == "#":
            tail = [part[1] for part in tokens[index + 1:min(len(tokens), index + 4)]]
            require("PyImport_ImportModule" not in tail,
                    f"{label}:{line}: aliasing native Python imports is forbidden")
        if value == "include" and index and tokens[index - 1][1] == "#":
            cursor = index + 1
            require(cursor < len(tokens), f"{label}:{line}: missing C include header")
            if tokens[cursor][0] == "string":
                header = tokens[cursor][1]
            else:
                require(tokens[cursor][1] == "<", f"{label}:{line}: computed C header")
                cursor += 1
                pieces: list[str] = []
                while cursor < len(tokens) and tokens[cursor][1] != ">":
                    pieces.append(tokens[cursor][1])
                    cursor += 1
                require(cursor < len(tokens), f"{label}:{line}: unterminated C header")
                header = "".join(pieces)
            require(header in SAFE_HEADERS, f"{label}:{line}: unapproved native header {header}")
            headers.append(header)
        if kind == "rust" and value == "use":
            require(index + 1 < len(tokens) and tokens[index + 1][0] == "identifier"
                    and tokens[index + 1][1] in SAFE_RUST_ROOTS,
                    f"{label}:{line}: Rust imports a foreign, computed, or external crate")
        if kind == "rust" and value == "extern" and index + 1 < len(tokens):
            require(tokens[index + 1][1] != "crate", f"{label}:{line}: external Rust crate")
        if kind == "rust" and value in {"concat", "concat_idents", "include", "include_bytes",
                                          "include_str", "macro_rules", "env", "option_env",
                                          "asm", "global_asm"}:
            require(index + 1 >= len(tokens) or tokens[index + 1][1] != "!",
                    f"{label}:{line}: computed Rust source, symbol, macro, or engine dispatch")
        if kind == "rust" and value in {"link", "link_name", "link_ordinal"}:
            previous = [item[1] for item in tokens[max(0, index - 3):index]]
            require("[" not in previous and "#" not in previous,
                    f"{label}:{line}: external native Rust link attribute")
        if kind == "rust" and value in {"Library", "Command"}:
            previous = [item[1] for item in tokens[max(0, index - 6):index]]
            require("libloading" not in previous and "process" not in previous,
                    f"{label}:{line}: dynamic external native engine/process")
    if kind == "c":
        require("rust_bound_get_signature" not in {item[1] for item in tokens
                                                    if item[0] == "identifier"},
                label + ": historical private inspect getter remains in candidate bridge")
        require("PyDescr_NewMethod" in {item[1] for item in tokens if item[0] == "identifier"},
                label + ": direct public native method descriptors disappeared")
    return {"kind": kind, "native_python_imports": modules, "native_headers": sorted(set(headers)),
            "token_count": len(tokens), "external_regex_packages": 0,
            "legacy_private_inspect_getter": False, "source_parsed_not_compiled": True}


def inspect_cargo(source: str, label: str, lock: bool) -> dict[str, object]:
    try:
        value = tomllib.loads(source)
    except (TypeError, ValueError, RecursionError) as error:
        raise AuditError(label + ": invalid Cargo TOML") from error
    if lock:
        packages = value.get("package")
        require(value.get("version") == 4 and type(packages) is list and len(packages) == 1
                and type(packages[0]) is dict
                and packages[0].get("name") == "rebar-rust-continuation"
                and packages[0].get("version") == "0.1.0"
                and set(packages[0]) == {"name", "version"}
                and set(value) == {"version", "package"},
                label + ": Cargo lock contains a foreign package, registry, or dependency")
        return {"kind": "lock", "package_count": 1, "external_cargo_dependencies": 0}
    package, library = value.get("package"), value.get("lib")
    require(type(package) is dict and package.get("name") == "rebar-rust-continuation"
            and package.get("publish") is False and type(library) is dict
            and library.get("crate-type") == ["cdylib"],
            label + ": Cargo manifest does not describe the exact first-party native engine")

    def recurse(item: object, trail: tuple[str, ...]) -> None:
        if type(item) is dict:
            for key, child in item.items():
                normalized = key.casefold().replace("_", "-")
                require(not normalized.endswith("dependencies") and normalized not in {
                    "patch", "replace", "build", "build-script", "links", "git", "path",
                }, label + ": Cargo foreign/build dependency at " + ".".join(trail + (key,)))
                recurse(child, trail + (key,))
        elif type(item) is list:
            for index, child in enumerate(item):
                recurse(child, trail + (str(index),))

    recurse(value, ())
    return {"kind": "manifest", "first_party_package_count": 1, "external_cargo_dependencies": 0}


def inspect_project(source: str, label: str) -> dict[str, object]:
    try:
        value = tomllib.loads(source)
    except (TypeError, ValueError, RecursionError) as error:
        raise AuditError(label + ": invalid project TOML") from error
    if label == "pyproject.toml":
        project = value.get("project")
        require(type(project) is dict and project.get("name") == "rebar-experiment"
                and project.get("dependencies") == []
                and "optional-dependencies" not in project,
                "Python production manifest contains an external package")
    else:
        packages = value.get("package")
        require(type(packages) is list and len(packages) == 1 and type(packages[0]) is dict
                and packages[0].get("name") == "rebar-experiment"
                and "dependencies" not in packages[0],
                "Python production lock contains an external package")
    return {"path": label, "external_python_packages": 0}


def bounded_unpack(fmt: str, raw: bytes, at: int, label: str) -> tuple[object, ...]:
    length = struct.calcsize(fmt)
    require(type(at) is int and at >= 0 and at <= len(raw) and length <= len(raw) - at,
            label + ": ELF field exceeds its authenticated bounds")
    return struct.unpack_from(fmt, raw, at)


def elf_name(table: bytes, at: int, label: str) -> str:
    require(type(at) is int and 0 <= at < len(table), label + ": invalid ELF string offset")
    end = table.find(b"\x00", at)
    require(end >= at and end - at <= 1024, label + ": unterminated ELF string")
    try:
        answer = table[at:end].decode("ascii")
    except UnicodeError as error:
        raise AuditError(label + ": non-ASCII ELF symbol or dependency") from error
    return answer


def inspect_elf(raw: bytes, role: str, label: str) -> dict[str, object]:
    require(role in {"engine", "bridge"} and 64 <= len(raw) <= MAX_BINARY
            and raw[:8] == b"\x7fELF\x02\x01\x01\x00",
            label + ": expected one first-party little-endian ELF64 shared object")
    header = bounded_unpack("<16sHHIQQQIHHHHHH", raw, 0, label)
    require(header[1] == 3 and header[2] == 62 and header[8] == 64
            and header[11] == 64 and 0 < header[12] <= 512 and header[13] < header[12],
            label + ": malformed first-party x86-64 ELF header")
    offset, count = int(header[6]), int(header[12])
    require(offset <= len(raw) and count <= (len(raw) - offset) // 64,
            label + ": ELF sections escape the authenticated binary")
    sections = [bounded_unpack("<IIQQQQIIQQ", raw, offset + index * 64, label)
                for index in range(count)]
    names = sections[int(header[13])]
    begin, length = int(names[4]), int(names[5])
    require(begin <= len(raw) and length <= len(raw) - begin,
            label + ": ELF section names exceed the authenticated binary")
    name_table = raw[begin:begin + length]
    by_name: dict[str, tuple[object, ...]] = {}
    for section in sections:
        name = elf_name(name_table, int(section[0]), label)
        require(name not in by_name, label + ": duplicate ELF section")
        at, size = int(section[4]), int(section[5])
        require(at <= len(raw) and (int(section[1]) == 8 or size <= len(raw) - at),
                label + ": ELF section escapes the authenticated binary")
        by_name[name] = section
    require({".dynstr", ".dynsym", ".dynamic"} <= by_name.keys(),
            label + ": missing complete dynamic symbol/dependency inventory")
    strings, symbols, dynamic = by_name[".dynstr"], by_name[".dynsym"], by_name[".dynamic"]
    dynstr = raw[int(strings[4]):int(strings[4]) + int(strings[5])]
    require(bool(dynstr) and dynstr[0] == 0 and int(symbols[1]) == 11
            and int(symbols[9]) == 24 and int(symbols[5]) % 24 == 0
            and int(dynamic[1]) == 6 and int(dynamic[9]) == 16
            and int(dynamic[5]) % 16 == 0,
            label + ": malformed dynamic symbols, strings, or links")
    imported: set[str] = set()
    exported: set[str] = set()
    for at in range(int(symbols[4]), int(symbols[4]) + int(symbols[5]), 24):
        symbol = bounded_unpack("<IBBHQQ", raw, at, label)
        name = elf_name(dynstr, int(symbol[0]), label)
        if name:
            (imported if int(symbol[3]) == 0 else exported).add(name.split("@", 1)[0])
    dependencies: list[str] = []
    runpaths: list[str] = []
    sonames: list[str] = []
    terminated = False
    for at in range(int(dynamic[4]), int(dynamic[4]) + int(dynamic[5]), 16):
        tag, value = bounded_unpack("<qQ", raw, at, label)
        if tag == 0:
            terminated = True
            break
        if tag in {1, 14, 15, 29}:
            item = elf_name(dynstr, int(value), label)
            if tag == 1:
                dependencies.append(item)
            elif tag == 14:
                sonames.append(item)
            else:
                runpaths.append(item)
    require(terminated, label + ": unterminated ELF dynamic owner table")
    allowed = SAFE_SYSTEM_LIBRARIES | ({"_rust_engine.so"} if role == "bridge" else set())
    require(all(name in allowed for name in dependencies),
            label + ": external package/regex dynamic library dependency")
    require(all(value in {"$ORIGIN", "$ORIGIN/"} for value in runpaths),
            label + ": shared-library lookup escaped its first-party native owner")
    for symbol in imported | exported:
        require(symbol not in FORBIDDEN_NATIVE
                and not symbol.casefold().startswith(FORBIDDEN_PREFIXES)
                and not symbol.startswith(FOREIGN_FAMILY_PREFIXES),
                label + ": foreign engine, candidate family, or dynamic loader symbol " + symbol)
    required = {"rebar_compile", "rebar_match"} if role == "engine" else {"PyInit__rust_bridge"}
    require(required <= exported, label + ": missing first-party Rust engine/native bridge exports")
    if role == "bridge":
        require("_rust_engine.so" in dependencies and runpaths == ["$ORIGIN"],
                label + ": native bridge no longer binds its exact colocated first-party Rust engine")
    return {"role": role, "needed_libraries": sorted(dependencies), "runpaths": runpaths,
            "sonames": sonames, "imported_symbol_count": len(imported),
            "exported_symbol_count": len(exported), "required_exports": sorted(required),
            "native_python_import_capability": "PyImport_ImportModule" in imported,
            "external_regex_dependencies": 0, "external_regex_symbols": 0,
            "cross_family_dependencies": 0, "binary_parsed_not_loaded": True}


def private_root_open(provenance: dict[str, object], wall: EffectWall) -> int:
    root = provenance["root"]
    require(type(root) is dict and type(root.get("path")) is str,
            "private source root provenance is missing")
    path = root["path"]
    require(path.startswith("/tmp/rebar-phase2-native-build-v9-rust-")
            and "/" not in path[len("/tmp/rebar-phase2-native-build-v9-rust-"):]
            and not any(value in path.casefold() for value in ("holdout", "hidden", "benchmark")),
            "refuse any private root outside the exact authenticated build prefix")
    descriptor = _OPEN(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    identity = _FSTAT(descriptor)
    require(stat.S_ISDIR(identity.st_mode) and identity.st_dev == root.get("device")
            and identity.st_ino == root.get("inode")
            and identity.st_uid == os.getuid() and stat.S_IMODE(identity.st_mode) == 0o700,
            "private build root no longer has its authenticated owner/device/inode/mode")
    wall.effects["private_root_opens"] += 1
    return descriptor


def run_static_audit(options: dict[str, object]) -> dict[str, object]:
    verify_runtime_pins()
    require(options.get("root_authorized") is True,
            "candidate/private-source inspection is ROOT-AGENT-ONLY")
    pushed = exact_sha(options.get("pushed_source_sha256"), "independently pushed V5 source")
    with EffectWall() as wall:
        _, source_owner = read_public(SOURCE, wall, "approved_owner_reads",
                                      expected={"sha256": pushed, "mode": "0600"})
        contract_raw, _ = read_public(CONTRACT, wall, "approved_owner_reads")
        contract = strict_json(contract_raw, CONTRACT)
        validate_contract(contract)
        freeze = contract["source_freeze"]
        require(type(freeze) is dict and freeze.get("source_sha256") == pushed,
                "root audit is not bound to the already committed and pushed source")
        historical, build = verify_history(wall)
        variants = {}
        for path, (expected_sha, expected_bytes) in PUBLIC_VARIANTS.items():
            _, owner = read_public(path, wall, "public_variant_reads", allow_candidate=True,
                                   expected={"sha256": expected_sha, "bytes": expected_bytes,
                                             "mode": "0600"})
            variants[path] = owner
        project = {}
        for path, expected_sha in PUBLIC_PROJECT.items():
            raw, owner = read_public(path, wall, "project_owner_reads",
                                     expected={"sha256": expected_sha, "mode": "0600"})
            project[path] = {"owner": owner, "audit": inspect_project(raw.decode("utf-8"), path)}

        provenance = build["provenance"]
        require(type(provenance) is dict, "V30 private build provenance is missing")
        root_descriptor = private_root_open(provenance, wall)
        phase_results: list[dict[str, object]] = []
        try:
            for index, phase_name in enumerate(("reference-a", "reference-b")):
                phase = provenance["phase_native_outputs"][index]
                expected_private = provenance["actual_private_source_owners"][index]["owners"]
                phase_descriptor = _OPEN(phase_name,
                                         os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                                         dir_fd=root_descriptor)
                try:
                    identity = _FSTAT(phase_descriptor)
                    require(identity.st_dev == phase["device"] and identity.st_ino == phase["inode"]
                            and identity.st_uid == os.getuid()
                            and stat.S_IMODE(identity.st_mode) == 0o700,
                            phase_name + ": exact private phase directory identity changed")
                    wall.effects["private_phase_opens"] += 1
                    sources: dict[str, dict[str, object]] = {}
                    adapter_source = ""
                    bridge_source = ""
                    for relative, (sha, length, kind) in EXPECTED_PRIVATE_SOURCES.items():
                        pinned = expected_private[relative]
                        raw, owner = read_under(
                            phase_descriptor, ("source",) + tuple(relative.split("/")),
                            phase_name + "/source/" + relative, wall, "private_source_reads",
                            expected={"sha256": sha, "bytes": length,
                                      "device": pinned["device"], "inode": pinned["inode"],
                                      "mode": "0600"})
                        source = raw.decode("utf-8")
                        if kind == "python":
                            audit = inspect_python(source, relative)
                            adapter_source = source
                        elif kind in {"c", "rust"}:
                            audit = inspect_native(source, relative, kind)
                            if kind == "c":
                                bridge_source = source
                        else:
                            audit = inspect_cargo(source, relative, kind == "lock")
                        sources[relative] = {"owner": owner, "audit": audit}
                    require(bool(adapter_source) and bool(bridge_source)
                            and "rust_bound_get_signature" not in bridge_source
                            and 'PyImport_ImportModule("inspect")' not in bridge_source
                            and "PyDescr_NewMethod(" in bridge_source
                            and "_rust_bridge.pattern_descriptors(Pattern)" in adapter_source,
                            phase_name + ": clean first-party bridge/adapter reachability changed")

                    binaries: list[dict[str, object]] = []
                    for expected_item in phase["native_outputs"]:
                        role = expected_item["role"]
                        expected = EXPECTED_NATIVE[role]
                        raw, owner = read_under(
                            phase_descriptor, ("native", expected["name"]),
                            phase_name + "/native/" + expected["name"], wall,
                            "private_binary_reads", MAX_BINARY,
                            expected={"sha256": expected["sha256"], "bytes": expected["bytes"],
                                      "device": expected_item["device"],
                                      "inode": expected_item["inode"], "mode": expected["mode"]})
                        binaries.append({"owner": owner, "audit": inspect_elf(raw, role, owner["path"])})
                    phase_results.append({"name": phase_name, "sources": sources,
                                          "native_outputs": binaries,
                                          "private_source_owner_count": len(sources),
                                          "private_native_owner_count": len(binaries),
                                          "legacy_private_inspect_getter": False,
                                          "external_regex_packages": 0})
                finally:
                    _CLOSE(phase_descriptor)
        finally:
            _CLOSE(root_descriptor)
        counts = dict(wall.effects)
        enforce_zero_effects(counts, audit=True)
    return {
        "schema": SCHEMA + "-root-static-audit", "status": "PASS",
        "phase": "ROOT-AUTHORIZED READ-ONLY FIRST-PARTY SOURCE AND NATIVE ELF AUDIT",
        "root_authorized": True, "pushed_source_sha256": pushed,
        "source_owner": source_owner, "immutable_v4": historical,
        "historical_canonical_v4_status": "FAIL", "historical_canonical_v4_finding_count": 1,
        "historical_canonical_v4_failure_hidden": False,
        "authenticated_v30": {
            "publication_owner": build["publication_owner"],
            "root_provenance_owner": build["root_provenance_owner"],
            "actual_compiler_process_count": 28,
            "actual_completed_phase_count": 2,
            "external_cargo_dependencies": 0,
            "actual_private_source_owner_count": 18,
            "actual_private_native_owner_count": 4,
        },
        "public_frozen_variants": variants, "production_project_dependencies": project,
        "audited_family": "rust", "independent_family_count": 1,
        "all_existing_candidate_families_audited": False,
        "phases": phase_results, "finding_count": 0, "findings": [],
        "clean_candidate_source_static_non_delegation": "PASS",
        "clean_candidate_native_elf_static_non_delegation": "PASS",
        "external_regex_packages": 0, "external_regex_libraries": 0,
        "external_regex_symbols": 0, "cross_family_dependencies": 0,
        "legacy_private_inspect_getter": False,
        "candidate_executions": 0, "native_library_loads": 0,
        "runtime_non_delegation": "NOT ESTABLISHED; STATIC SOURCE AND ELF AUDIT ONLY",
        "candidate_correctness": "NOT MEASURED BY THIS AUDIT", "candidate_qualified": False,
        "final_cases_generated": 0, "performance": "NOT MEASURED", "winner_selected": False,
        "effects": counts,
    }


def synthetic_elf(needed: tuple[str, ...], imports: tuple[str, ...], exports: tuple[str, ...],
                  *, runpath: str | None = None) -> bytes:
    strings = bytearray(b"\x00")

    def put_string(value: str) -> int:
        offset = len(strings)
        strings.extend(value.encode("ascii") + b"\x00")
        return offset

    needed_offsets = [put_string(value) for value in needed]
    imported_offsets = [put_string(value) for value in imports]
    exported_offsets = [put_string(value) for value in exports]
    path_offset = put_string(runpath) if runpath is not None else None
    section_names = b"\x00.shstrtab\x00.dynstr\x00.dynsym\x00.dynamic\x00"
    names = {value: section_names.index(value.encode("ascii"))
             for value in (".shstrtab", ".dynstr", ".dynsym", ".dynamic")}
    symbols = bytearray(struct.pack("<IBBHQQ", 0, 0, 0, 0, 0, 0))
    for offset in imported_offsets:
        symbols.extend(struct.pack("<IBBHQQ", offset, 0x12, 0, 0, 0, 0))
    for offset in exported_offsets:
        symbols.extend(struct.pack("<IBBHQQ", offset, 0x12, 0, 1, 1, 1))
    dynamic = bytearray()
    for offset in needed_offsets:
        dynamic.extend(struct.pack("<qQ", 1, offset))
    if path_offset is not None:
        dynamic.extend(struct.pack("<qQ", 29, path_offset))
    dynamic.extend(struct.pack("<qQ", 0, 0))
    payload = bytearray(b"\x00" * 64)

    def append(value: bytes | bytearray) -> tuple[int, int]:
        while len(payload) % 8:
            payload.append(0)
        start = len(payload)
        payload.extend(value)
        return start, len(value)

    names_at, names_size = append(section_names)
    strings_at, strings_size = append(strings)
    symbols_at, symbols_size = append(symbols)
    dynamic_at, dynamic_size = append(dynamic)
    while len(payload) % 8:
        payload.append(0)
    records_at = len(payload)
    rows = [struct.pack("<IIQQQQIIQQ", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]
    rows.append(struct.pack("<IIQQQQIIQQ", names[".shstrtab"], 3, 0, 0,
                            names_at, names_size, 0, 0, 1, 0))
    rows.append(struct.pack("<IIQQQQIIQQ", names[".dynstr"], 3, 0, 0,
                            strings_at, strings_size, 0, 0, 1, 0))
    rows.append(struct.pack("<IIQQQQIIQQ", names[".dynsym"], 11, 0, 0,
                            symbols_at, symbols_size, 2, 1, 8, 24))
    rows.append(struct.pack("<IIQQQQIIQQ", names[".dynamic"], 6, 0, 0,
                            dynamic_at, dynamic_size, 2, 0, 8, 16))
    payload.extend(b"".join(rows))
    identifier = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8
    payload[:64] = struct.pack("<16sHHIQQQIHHHHHH", identifier, 3, 62, 1, 0, 0,
                               records_at, 0, 64, 0, 0, 64, len(rows), 1)
    return bytes(payload)


def self_test() -> dict[str, object]:
    verify_runtime_pins()
    positive, hostile = 0, 0

    def accept(function: object, *args: object, **kwargs: object) -> object:
        nonlocal positive
        value = function(*args, **kwargs)
        positive += 1
        return value

    def reject(function: object, *args: object, **kwargs: object) -> None:
        nonlocal hostile
        try:
            function(*args, **kwargs)
        except (AuditError, ValueError, TypeError, SyntaxError, UnicodeError, RecursionError):
            hostile += 1
            return
        raise AuditError("hostile control escaped " + getattr(function, "__name__", "unknown"))

    with EffectWall() as wall:
        adapter = ('import enum\nimport operator\nimport os\nimport types\n'
                   'import unicodedata\nimport warnings\nfrom candidates import _rust_bridge\n'
                   'class Pattern: pass\n_rust_bridge.pattern_descriptors(Pattern)\n')
        accept(inspect_python, adapter, "fixture.py")
        for module in sorted(FORBIDDEN_ROOTS):
            reject(inspect_python, adapter + "import " + module + "\n", "fixture.py")
        for payload in (
            'from candidates import _zig_bridge\n',
            'from candidates import _rust_bridge as hidden\n',
            'import candidates.zig_candidate\n',
            '__import__("re")\n',
            'getattr(sys, "modules")["re"]\n',
            'sys.modules["_sre"]\n',
            '_rust_bridge.bind(lambda: None, Pattern())\n',
            'eval("import re")\n',
            'exec("import regex")\n',
            'os.system("foreign-regex")\n',
        ):
            reject(inspect_python, adapter + payload, "fixture.py")
        reject(inspect_python, 'import enum\n', "fixture.py")

        clean_c = ('#include <Python.h>\n#include <stddef.h>\n'
                   'PyImport_ImportModule("copyreg");\nPyDescr_NewMethod(method);\n')
        accept(inspect_native, clean_c, "fixture.c", "c")
        accept(inspect_native,
               '// PyImport_ImportModule("re"); pcre2_match();\n'
               'const char *label="_sre.SRE_Scanner pcre2_match";\nPyDescr_NewMethod(x);\n',
               "fixture.c", "c")
        for module in ("re", "_sre", "inspect", "tokenize", "regex", "pcre2"):
            reject(inspect_native, clean_c + 'PyImport_ImportModule("' + module + '");\n',
                   "fixture.c", "c")
        for payload in (
            'PyImport_ImportModule("r" "e");\n',
            'PyImport_ImportModule(variable);\n',
            '#define ALIAS PyImport_ImportModule\nALIAS("re");\n',
            'dlopen("pcre2", 1);\n', 'dlsym(handle, "pcre2_match");\n',
            'regcomp(pattern, flags);\n', 'pcre2_match_8(pattern);\n',
            'onig_search_gpos(pattern);\n', 're2_match(pattern);\n',
            'rebar_zig_compile(pattern);\n', '#include <pcre2.h>\n',
            'rust_bound_get_signature();\n', '/* unterminated',
        ):
            reject(inspect_native, clean_c + payload, "fixture.c", "c")

        clean_rust = (
            "use std::slice;\n",
            "use stack::InlineStack;\n",
            "struct Borrowed<'a> { value: &'a str }\n",
            "'outer: loop { break 'outer; }\n",
            "let character='🦀'; let escaped='\\u{1F980}'; let byte=b'\\x7f';\n",
            'let message=r###"use regex::Regex; pcre2_match()"###;\n',
            'let message=br##"dlopen(\\"foreign\\")"##;\n',
            '/* outer /* nested pcre2_match */ */\nuse std::slice;\n',
            'unsafe extern "C" { fn Py_GetRecursionLimit() -> i32; }\n',
        )
        for fixture in clean_rust:
            accept(inspect_native, fixture, "fixture.rs", "rust")
        for payload in (
            'use regex::Regex;\n', 'extern crate regex;\n',
            'pcre2_match(pattern);\n', 'rebar_go_compile(pattern);\n',
            'concat!("reg", "ex");\n', 'include!("foreign.rs");\n',
            'include_bytes!("foreign.so");\n', 'macro_rules! hidden {}\n',
            'env!("FOREIGN_REGEX_ENGINE");\n', '#[link(name="pcre2")] extern "C" {}\n',
            'libloading::Library::new("foreign.so");\n',
            'std::process::Command::new("foreign-regex");\n',
            'let broken=r###"bad"##;\n', "let broken='ab';\n",
            "let broken=b'🦀';\n", '/* unclosed\n',
        ):
            reject(inspect_native, payload, "fixture.rs", "rust")

        manifest = ('[package]\nname="rebar-rust-continuation"\npublish=false\n'
                    '[lib]\ncrate-type=["cdylib"]\n')
        lock = 'version=4\n[[package]]\nname="rebar-rust-continuation"\nversion="0.1.0"\n'
        accept(inspect_cargo, manifest, "Cargo.toml", False)
        accept(inspect_cargo, lock, "Cargo.lock", True)
        for extra in ('[dependencies]\nregex="1"\n', '[dev-dependencies]\npcre="1"\n',
                      '[build-dependencies]\nre2="1"\n',
                      '[target."cfg(unix)".dependencies]\nregex="1"\n',
                      '[workspace.dependencies]\nonig="1"\n',
                      '[patch.crates-io]\nregex={git="https://outside.invalid/regex"}\n'):
            reject(inspect_cargo, manifest + extra, "Cargo.toml", False)
        for extra in ('dependencies=["regex"]\n',
                      '[[package]]\nname="regex"\nversion="1"\n',
                      'source="registry+https://outside.invalid"\n'):
            reject(inspect_cargo, lock + extra, "Cargo.lock", True)

        project = '[project]\nname="rebar-experiment"\ndependencies=[]\n'
        project_lock = 'version=1\n[[package]]\nname="rebar-experiment"\n'
        accept(inspect_project, project, "pyproject.toml")
        accept(inspect_project, project_lock, "uv.lock")
        reject(inspect_project, project.replace("dependencies=[]", 'dependencies=["regex"]'),
               "pyproject.toml")
        reject(inspect_project, project + '[project.optional-dependencies]\nfast=["re2"]\n',
               "pyproject.toml")
        reject(inspect_project, project_lock + 'dependencies=["pcre2"]\n', "uv.lock")

        engine = synthetic_elf(("libc.so.6",), ("malloc",), ("rebar_compile", "rebar_match"))
        bridge = synthetic_elf(("libc.so.6", "_rust_engine.so"),
                               ("PyImport_ImportModule", "rebar_compile"),
                               ("PyInit__rust_bridge",), runpath="$ORIGIN")
        accept(inspect_elf, engine, "engine", "fixture-engine.so")
        accept(inspect_elf, bridge, "bridge", "fixture-bridge.so")
        for fixture, role in (
            (synthetic_elf(("libpcre2-8.so.0",), (), ("rebar_compile", "rebar_match")), "engine"),
            (synthetic_elf(("libc.so.6",), ("pcre2_match",), ("rebar_compile", "rebar_match")), "engine"),
            (synthetic_elf(("libc.so.6",), ("dlopen",), ("rebar_compile", "rebar_match")), "engine"),
            (synthetic_elf(("libc.so.6",), ("rebar_zig_compile",),
                           ("rebar_compile", "rebar_match")), "engine"),
            (synthetic_elf(("libc.so.6",), (), ("rebar_compile",)), "engine"),
            (synthetic_elf(("libc.so.6", "_rust_engine.so"), (),
                           ("PyInit__rust_bridge",), runpath="/tmp/outside"), "bridge"),
            (synthetic_elf(("libc.so.6",), (), ("PyInit__rust_bridge",),
                           runpath="$ORIGIN"), "bridge"),
            (engine[:63], "engine"),
        ):
            reject(inspect_elf, fixture, role, "hostile.so")

        for attack in ("../outside", ".git/config", "oracle/holdout/cases.json",
                       "oracle/hidden/results.json", "performance/report.json",
                       "oracle/phase2/evidence/arbitrary.json",
                       "candidates/rust_candidate.py", "/tmp/private", "source/../native"):
            reject(checked_parts, attack)
        accept(checked_parts, SOURCE)
        accept(checked_parts, V4_FAILURE_PATH, allow_evidence=True)
        accept(checked_parts, V30_PUBLICATION_PATH, allow_evidence=True)
        accept(checked_parts, V30_ROOT_PATH, allow_evidence=True)
        require(positive >= 20 and hostile >= 80,
                f"first-party hostile/positive synthetic controls shrank: {positive}/{hostile}")
        counts = dict(wall.effects)
        enforce_zero_effects(counts)
    return {"schema": SCHEMA + "-self-test", "status": "PASS",
            "positive_controls": positive, "hostile_controls": hostile,
            "candidate_sources_read": 0, "private_build_roots_opened": 0,
            "candidate_executions": 0, "native_libraries_loaded": 0,
            "historical_v4_failure_is_never_hidden": True,
            "same_family_first_party_rust_bridge_is_allowed": True,
            "external_regex_wrappers_engines_and_crates_are_rejected": True,
            "cross_family_dispatch_is_rejected": True,
            "historical_private_inspect_getter_is_rejected": True,
            "rust_lifetimes_nested_comments_raw_strings_are_supported": True,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_qualified": False, "final_cases_generated": 0,
            "performance": "NOT MEASURED", "winner_selected": False, "effects": counts}


def parse_arguments(values: list[str]) -> dict[str, object]:
    require(bool(values), "choose --self-test, --verify-source, or root-only --audit")
    mode = values[0]
    require(mode in {"--self-test", "--verify-source", "--audit"},
            "unrecognized clean Rust source-audit mode")
    answer: dict[str, object] = {"mode": mode}
    mapping = {"--source-sha256": "source_sha256", "--protocol-sha256": "protocol_sha256",
               "--contract-sha256": "contract_sha256",
               "--pushed-source-sha256": "pushed_source_sha256"}
    position = 1
    while position < len(values):
        option = values[position]
        if option == "--root-authorized":
            require(mode == "--audit" and "root_authorized" not in answer,
                    "root authorization is valid exactly once for an actual candidate audit")
            answer["root_authorized"] = True
            position += 1
            continue
        require(option in mapping and position + 1 < len(values), "invalid audit argument " + option)
        key = mapping[option]
        require(key not in answer, "duplicate clean Rust audit option " + option)
        answer[key] = values[position + 1]
        position += 2
    if mode == "--self-test":
        require(set(answer) == {"mode"}, "source-only self-tests cannot authorize reads or candidates")
    elif mode == "--verify-source":
        require(set(answer) == {"mode", "source_sha256", "protocol_sha256", "contract_sha256"},
                "source-only verification requires exactly three independently supplied owner pins")
    else:
        require(set(answer) == {"mode", "root_authorized", "pushed_source_sha256"},
                "static candidate inspection requires root authorization and exact pushed source")
    return answer


def main(values: list[str] | None = None) -> int:
    try:
        options = parse_arguments(list(sys.argv[1:] if values is None else values))
        if options["mode"] == "--self-test":
            answer = self_test()
        elif options["mode"] == "--verify-source":
            answer = source_verify(options)
        else:
            answer = run_static_audit(options)
        sys.stdout.buffer.write(canonical(answer))
        sys.stdout.buffer.flush()
        return 0 if answer.get("status") == "PASS" else 1
    except (Exception, KeyboardInterrupt) as error:
        answer = {"schema": SCHEMA + "-entry-failure", "status": "FAIL",
                  "error_type": type(error).__name__, "message": str(error)[:2048],
                  "candidate_executions": 0, "native_library_loads": 0,
                  "runtime_non_delegation": "NOT ESTABLISHED", "candidate_qualified": False,
                  "final_cases_generated": 0, "performance": "NOT MEASURED",
                  "winner_selected": False}
        sys.stdout.buffer.write(canonical(answer))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
