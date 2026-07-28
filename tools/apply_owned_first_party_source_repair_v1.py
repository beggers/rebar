#!/usr/bin/env python3
"""Freeze one private, first-party C repair without changing a candidate."""

from __future__ import annotations

import argparse
import builtins
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
SCHEMA = "rebar-phase2-owned-first-party-source-repair-v1"
MAX_OWNER_BYTES = 64 * 1024 * 1024
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
    "tools/reproduce_owned_native_source_build_v7.py": "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
    "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md": "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313",
    "oracle/phase2/native-source-build-v7.json": "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
    "tools/render_candidate_current_overview_v19.py": "8144272f7c91e3821306a4d3963c8e201c68b275cecacf80d5000dd98c502494",
    "docs/evidence/candidate-current-overview-v19.inputs.json": "8f1eb51ff477f0b59934ee503d9bf795f472fd6674180e2af244c7ad4504560c",
    "docs/evidence/candidate-current-overview-v19.json": "504de87d091c555eb53d664fbfaaa70660ff4dd2f9abc22803246f8a5e18287f",
    "docs/evidence/candidate-current-overview-v19.svg": "7dea68622d7c360f9d2af83f97d76210889b2aeda6662e06178009a1127cf3d6",
}
ORIGINAL_PATH = "candidates/_vm_native.c"
ORIGINAL_SHA256 = "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55"
ORIGINAL_BYTES = 218185
ADAPTER_PATH = "candidates/vm_candidate.py"
ADAPTER_SHA256 = "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
ADAPTER_BYTES = 60707
DERIVED_SHA256 = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
DERIVED_BYTES = 218308
OLD_BLOCK = b"""    Subject subject;
    if (!pattern_subject(pattern,string,&subject)) return NULL;
    PyObject *result=NULL;
    PyObject *template_parts=NULL;
    if (PyCallable_Check(replacement)) {
        result=substitute_callable(pattern,&subject,replacement,limit,
                                  return_count);
        goto done;
    }

    int template_byte_mode=0,literal_replacement=0;
    template_parts=substitution_template(
        pattern,replacement,&template_byte_mode,&literal_replacement);
    if (!template_parts) goto done;
"""
NEW_BLOCK = b"""    Subject subject={0};
    PyObject *result=NULL;
    PyObject *template_parts=NULL;
    int template_byte_mode=0,literal_replacement=0;
    int callable=PyCallable_Check(replacement);
    if (!callable) {
        template_parts=substitution_template(
            pattern,replacement,&template_byte_mode,&literal_replacement);
        if (!template_parts) return NULL;
    }
    if (!pattern_subject(pattern,string,&subject)) {
        Py_XDECREF(template_parts);
        return NULL;
    }
    if (callable) {
        result=substitute_callable(pattern,&subject,replacement,limit,
                                  return_count);
        goto done;
    }
"""
FUNCTION_ANCHOR = b"static PyObject *pattern_substitute("
NEXT_FUNCTION_ANCHOR = b"static PyObject *pattern_sub("
DONE_BLOCK = b"done:\n    Py_XDECREF(template_parts);\n    subject_clear(&subject);\n    return result;\n}"
BOUND_BLOCK = (
    b"    if (!pattern_bind_arguments(args,nargsf,kwnames,method,names,3,2,\n"
    b"                                values)) return NULL;\n"
    b"    PyObject *replacement=values[0],*string=values[1],*limit_value=values[2];\n"
    b"    Py_ssize_t limit=0;\n"
)


class GateError(Exception):
    """A frozen gate or a forbidden effect failed."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise GateError(reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def valid_digest(value: str, name: str) -> str:
    require(isinstance(value, str) and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            f"invalid {name} SHA-256")
    return value


def relative_parts(value: str) -> tuple[str, ...]:
    require(isinstance(value, str) and 0 < len(value) <= 512,
            "invalid owner path")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value,
            "owner must be a canonical relative path")
    require(0 < len(parsed.parts) <= 12
            and all(part not in ("", ".", "..") for part in parsed.parts),
            "invalid owner path component")
    return parsed.parts


def checked_read(relative: str, expected: str, expected_bytes: int | None = None,
                 *, base: str = str(ROOT)) -> bytes:
    """Read a pinned regular file through no-follow, directory-owned FDs."""
    parts = relative_parts(relative)
    valid_digest(expected, "owner")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(base, flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        fd = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode), "owner is not a regular file")
            require(before.st_size <= MAX_OWNER_BYTES, "owner exceeds byte bound")
            if expected_bytes is not None:
                require(before.st_size == expected_bytes, "owner byte count changed")
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = os.read(fd, min(1024 * 1024, MAX_OWNER_BYTES + 1 - total))
                if not chunk:
                    break
                total += len(chunk)
                require(total <= MAX_OWNER_BYTES, "owner exceeds read bound")
                chunks.append(chunk)
            after = os.fstat(fd)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns),
                    "owner changed during authenticated read")
            data = b"".join(chunks)
            require(len(data) == before.st_size, "owner was incompletely read")
            require(sha256(data) == expected, f"owner digest changed: {relative}")
            return data
        finally:
            os.close(fd)
    finally:
        os.close(directory)


def strict_json(data: bytes, name: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        result: dict[str, object] = {}
        for key, value in items:
            require(key not in result, f"duplicate key in {name}")
            result[key] = value
        return result

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(
                               GateError(f"non-finite value in {name}")))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise GateError(f"invalid JSON in {name}: {error}") from error
    require(isinstance(value, dict), f"{name} must be a JSON object")
    return value


def repaired_source(source: bytes, baseline_digest: str,
                    baseline_bytes: int, *, frozen: bool = True) -> bytes:
    require(len(source) == baseline_bytes, "original source byte count changed")
    require(sha256(source) == baseline_digest, "original source digest changed")
    require(source.count(FUNCTION_ANCHOR) == 1, "substitution function is not unique")
    require(source.count(NEXT_FUNCTION_ANCHOR) == 1, "function end is not unique")
    require(source.count(OLD_BLOCK) == 1, "original repair block is not unique")
    require(source.count(NEW_BLOCK) == 0, "derived repair block already exists")
    start = source.index(FUNCTION_ANCHOR)
    finish = source.index(NEXT_FUNCTION_ANCHOR, start + len(FUNCTION_ANCHOR))
    at = source.index(OLD_BLOCK)
    require(start < at < finish, "repair block escapes substitution function")
    function = source[start:finish]
    require(function.count(DONE_BLOCK) == 1, "substitution cleanup is not unique")
    require(function.count(BOUND_BLOCK) == 1, "argument binding precedence changed")
    require(function.index(BOUND_BLOCK) < function.index(OLD_BLOCK),
            "repair would move argument binding or count conversion")
    derived = source[:at] + NEW_BLOCK + source[at + len(OLD_BLOCK):]
    require(derived[:at] == source[:at]
            and derived[at + len(NEW_BLOCK):] == source[at + len(OLD_BLOCK):],
            "repair changes bytes outside the one anchored block")
    require(derived.count(OLD_BLOCK) == 0 and derived.count(NEW_BLOCK) == 1,
            "derived source does not contain exactly one repair")
    require(derived.count(FUNCTION_ANCHOR) == 1
            and derived.count(NEXT_FUNCTION_ANCHOR) == 1,
            "repair changed function ownership")
    require(derived.count(b"PyBUF_SIMPLE") == source.count(b"PyBUF_SIMPLE"),
            "repair changed buffer acquisition flags")
    require(derived.count(b"substitute_callable(")
            == source.count(b"substitute_callable("),
            "repair changed callable replacement dispatch")
    for forbidden in (b"import re", b"from re ", b"import _sre",
                      b"PyImport_ImportModule", b"dlopen(", b"ctypes",
                      b"subprocess", b"candidates.rust", b"candidates.zig",
                      b"candidates.cpp", b"candidates.go", b"candidates.fortran"):
        require(derived.count(forbidden) == source.count(forbidden),
                "repair introduced delegation or a foreign candidate")
    derived_function = derived[start:derived.index(NEXT_FUNCTION_ANCHOR, start)]
    require(derived_function.count(DONE_BLOCK) == 1,
            "repair changed the successful-subject cleanup")
    require(derived_function.index(BOUND_BLOCK) < derived_function.index(NEW_BLOCK),
            "repair changed argument-validation precedence")
    if frozen:
        require(baseline_digest == ORIGINAL_SHA256
                and baseline_bytes == ORIGINAL_BYTES,
                "repair is not based on the frozen first-party owner")
        require(sha256(derived) == DERIVED_SHA256
                and len(derived) == DERIVED_BYTES,
                "derived source is not the exact frozen repair")
        require(source.count(b"PyBUF_SIMPLE") == 4
                and source.count(b"substitute_callable(") == 2,
                "original buffer or callback witness changed")
    return derived


class SourceOnlyBoundary:
    """Make source-only self-tests fail before any real side effect."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, owner: object, name: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def forbidden(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise GateError(f"source-only boundary: {name}")

        self.saved.append((owner, name, original))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyBoundary:
        for owner, names in (
            (builtins, ("open",)),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "remove", "unlink", "replace", "rename",
                  "system", "fork", "posix_spawn")),
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
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: object, _value: object, _traceback: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def sample_source() -> bytes:
    return (
        b"/* independent synthetic first-party C fixture */\n"
        + FUNCTION_ANCHOR
        + b"PatternObject *pattern) {\n"
        + BOUND_BLOCK
        + OLD_BLOCK
        + b"    if (PyBUF_SIMPLE) substitute_callable(pattern);\n"
        + DONE_BLOCK + b"\n"
        + NEXT_FUNCTION_ANCHOR + b"PatternObject *pattern) { return NULL; }\n"
    )


def self_test() -> dict:
    accepted = 0
    rejected = 0
    sample = sample_source()
    sample_digest = sha256(sample)
    with SourceOnlyBoundary() as boundary:
        result = repaired_source(sample, sample_digest, len(sample), frozen=False)
        require(result.count(NEW_BLOCK) == 1, "synthetic positive did not repair")
        accepted += 1
        require(result.count(b"PyBUF_SIMPLE") == 1, "synthetic buffer flags changed")
        accepted += 1
        require(result.count(b"substitute_callable(") == 2,
                "synthetic callback changed")
        accepted += 1
        require(result.count(DONE_BLOCK) == 1, "synthetic cleanup changed")
        accepted += 1
        require(NEW_BLOCK.index(b"substitution_template(")
                < NEW_BLOCK.index(b"pattern_subject("),
                "template must be acquired before subject")
        accepted += 1
        require(NEW_BLOCK.index(b"if (!template_parts) return NULL;")
                < NEW_BLOCK.index(b"pattern_subject("),
                "template failure must not acquire a subject")
        accepted += 1
        failed_subject = (
            b"if (!pattern_subject(pattern,string,&subject)) {\n"
            b"        Py_XDECREF(template_parts);\n"
            b"        return NULL;\n    }"
        )
        require(NEW_BLOCK.count(failed_subject) == 1,
                "subject failure must release its template exactly once")
        accepted += 1
        require(b"subject_clear(" not in failed_subject,
                "failed subject must not be released twice")
        accepted += 1
        require(NEW_BLOCK.index(b"if (callable)")
                > NEW_BLOCK.index(b"pattern_subject("),
                "callable replacement must remain subject-first")
        accepted += 1
        require(result[:result.index(NEW_BLOCK)]
                == sample[:sample.index(OLD_BLOCK)], "prefix changed")
        accepted += 1
        require(result[result.index(NEW_BLOCK) + len(NEW_BLOCK):]
                == sample[sample.index(OLD_BLOCK) + len(OLD_BLOCK):],
                "suffix changed")
        accepted += 1
        require(sha256(OLD_BLOCK)
                == "7e27dd70cd152e2bf4848f34c9b309d89acd44468991d336dd22b6250d72e178",
                "old block pin changed")
        accepted += 1
        require(sha256(NEW_BLOCK)
                == "82bb19944c11d0aba8d0d0e5e5f76a4b77127f44006d8326e3c86d93e34a32d3",
                "new block pin changed")
        accepted += 1

        def reject(call: object, label: str) -> None:
            nonlocal rejected
            try:
                call()  # type: ignore[operator]
            except (GateError, OSError, ValueError, TypeError):
                rejected += 1
            else:
                raise GateError(f"hostile control was accepted: {label}")

        mutations = {
            "wrong original digest": (sample, "0" * 64, len(sample)),
            "wrong original byte count": (sample, sample_digest, len(sample) + 1),
            "missing repair block":
                (sample.replace(OLD_BLOCK, b"/* absent */\n"), None, None),
            "duplicate repair block":
                (sample.replace(OLD_BLOCK, OLD_BLOCK + OLD_BLOCK), None, None),
            "already-repaired source":
                (sample.replace(OLD_BLOCK, NEW_BLOCK), None, None),
            "duplicate function owner":
                (FUNCTION_ANCHOR + b"fake\n" + sample, None, None),
            "missing function owner":
                (sample.replace(FUNCTION_ANCHOR, b"not_the_owner("), None, None),
            "duplicate next function":
                (sample + NEXT_FUNCTION_ANCHOR, None, None),
            "missing next function":
                (sample.replace(NEXT_FUNCTION_ANCHOR, b"not_the_next("), None, None),
            "duplicate cleanup":
                (sample.replace(DONE_BLOCK, DONE_BLOCK + DONE_BLOCK), None, None),
            "missing cleanup":
                (sample.replace(DONE_BLOCK, b"return result;\n}"), None, None),
            "missing argument binding":
                (sample.replace(BOUND_BLOCK, b"/* bypass binding */\n"), None, None),
            "duplicate argument binding":
                (sample.replace(BOUND_BLOCK, BOUND_BLOCK + BOUND_BLOCK), None, None),
            "block outside owner":
                (OLD_BLOCK + sample.replace(OLD_BLOCK, b"/* moved */\n"), None, None),
            "frozen synthetic owner": (sample, sample_digest, len(sample)),
        }
        for name, (mutated, expected, size) in mutations.items():
            expected = sha256(mutated) if expected is None else expected
            size = len(mutated) if size is None else size
            frozen = name == "frozen synthetic owner"
            reject(lambda data=mutated, digest=expected, count=size, exact=frozen:
                   repaired_source(data, digest, count, frozen=exact), name)

        invalid_paths = ("", "/tmp/escape", "../escape", "a/../escape",
                         "a/./escape", "a//escape", "./owner", "a/",
                         "a" * 513, "/home/dev-user/src/rebar/candidates/_vm_native.c")
        for value in invalid_paths:
            reject(lambda item=value: relative_parts(item), f"hostile path {value!r}")
        for value in ("", "0" * 63, "0" * 65, "F" * 64,
                      "g" * 64, "../" + "0" * 61):
            reject(lambda item=value: valid_digest(item, "hostile"),
                   "hostile digest")
        reject(lambda: strict_json(b'{"a":1,"a":2}', "hostile"),
               "duplicate JSON key")
        reject(lambda: strict_json(b'{"a":NaN}', "hostile"), "non-finite JSON")
        reject(lambda: strict_json(b"[]", "hostile"), "non-object JSON")

        effect_probes = (
            (lambda: builtins.open("/tmp/forbidden"), "builtins open"),
            (lambda: io.open("/tmp/forbidden"), "io open"),
            (lambda: os.open("/tmp/forbidden", os.O_RDONLY), "os open"),
            (lambda: os.read(0, 1), "file read"),
            (lambda: os.write(1, b"x"), "file write"),
            (lambda: os.stat("/tmp"), "path stat"),
            (lambda: os.lstat("/tmp"), "symlink stat"),
            (lambda: os.mkdir("/tmp/forbidden"), "directory creation"),
            (lambda: os.unlink("/tmp/forbidden"), "owner deletion"),
            (lambda: os.replace("/tmp/a", "/tmp/b"), "owner replacement"),
            (lambda: Path("/tmp/forbidden").read_bytes(), "Path read"),
            (lambda: Path("/tmp/forbidden").write_bytes(b"x"), "Path write"),
            (lambda: Path("/tmp").resolve(), "path resolution"),
            (lambda: subprocess.run(("true",)), "subprocess"),
            (lambda: subprocess.Popen(("true",)), "candidate or compiler"),
            (lambda: socket.socket(), "network"),
            (lambda: tempfile.mkdtemp(), "private root creation"),
            (lambda: tempfile.mkstemp(), "temporary owner creation"),
            (lambda: importlib.import_module("candidates.vm_candidate"),
             "candidate import"),
            (lambda: importlib.import_module("re"), "stdlib oracle import"),
            (lambda: threading.Thread().start(), "thread"),
            (lambda: time.perf_counter(), "performance clock"),
            (lambda: time.perf_counter_ns(), "performance nanoclock"),
            (lambda: time.monotonic(), "monotonic clock"),
            (lambda: time.time(), "wall clock"),
            (lambda: time.sleep(0), "wait"),
        )
        for probe, label in effect_probes:
            reject(probe, label)
        blocked = boundary.blocked
    require(blocked == len(effect_probes), "effect-boundary accounting changed")
    return {
        "accepted_source_controls": accepted,
        "blocked_effect_controls": blocked,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "clock_samples": 0,
        "compiler_processes_started": 0,
        "holdout_opened": False,
        "mode": "SOURCE-ONLY SELF-TEST",
        "network_requests": 0,
        "rejected_hostile_controls": rejected,
        "schema": SCHEMA,
        "status": "PASS",
        "workspace_mutations": 0,
    }


def discover_evidence(value: object, output: dict[str, str]) -> None:
    if isinstance(value, dict):
        path = value.get("path")
        digest = value.get("sha256")
        if (isinstance(path, str) and isinstance(digest, str)
                and path.startswith(("oracle/phase2/evidence/",
                                     "experiments/rust_public_practice_v1/"))):
            valid_digest(digest, "historical evidence")
            relative_parts(path)
            require(path not in output or output[path] == digest,
                    "conflicting historical evidence pins")
            output[path] = digest
        for child in value.values():
            discover_evidence(child, output)
    elif isinstance(value, list):
        for child in value:
            discover_evidence(child, output)


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None) -> tuple[dict, bytes]:
    require(sys.version_info[:3] == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.executable == PYTHON, "unfrozen CPython runtime")
    valid_digest(source_pin, "repair tool")
    valid_digest(protocol_pin, "repair protocol")
    checked_read("tools/apply_owned_first_party_source_repair_v1.py", source_pin)
    checked_read("oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md", protocol_pin)
    protected = {path: checked_read(path, digest)
                 for path, digest in SUPPORT.items()}
    original = checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
    checked_read(ADAPTER_PATH, ADAPTER_SHA256, ADAPTER_BYTES)
    derived = repaired_source(original, ORIGINAL_SHA256, ORIGINAL_BYTES)

    p0 = strict_json(protected["oracle/phase1/p0-completeness-v1.json"], "P0")
    require(p0.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and p0.get("version") == 1, "original P0 oracle changed")
    denominator = p0.get("denominator")
    require(isinstance(denominator, dict)
            and tuple(denominator.get("counted_suite_ids", ())) == SUITE_IDS
            and denominator.get("final_required_case_execution_denominator") == 31237
            and denominator.get("private_upstream_methods_outside_public_denominator") == 13,
            "original 13-suite, 31,237-case, 13-waiver denominator changed")
    phase = p0.get("phase_gate")
    require(isinstance(phase, dict) and phase.get("status") == "PASS"
            and phase.get("all_obligations_mapped") is True
            and phase.get("final_holdout_authorized") is False,
            "original correctness oracle gate changed")
    runtime = p0.get("runtime")
    require(isinstance(runtime, dict) and runtime.get("python_version") == "3.14.6"
            and runtime.get("python_implementation") == "CPython",
            "original oracle runtime changed")
    executable = runtime.get("executable")
    require(isinstance(executable, dict) and executable.get("path") == PYTHON
            and executable.get("sha256") == PYTHON_SHA256,
            "original oracle interpreter pin changed")

    v7 = strict_json(protected["oracle/phase2/native-source-build-v7.json"], "V7")
    require(v7.get("schema") == "rebar-phase2-owned-native-source-build-v7-source-freeze"
            and v7.get("version") == 7 and v7.get("family_count") == 6
            and v7.get("source_owner_count") == 25
            and v7.get("qualified_candidate_count") == 0,
            "frozen six-family, 25-owner V7 source baseline changed")
    families = v7.get("families")
    require(isinstance(families, list) and len(families) == 6,
            "frozen source-family count changed")
    family_ids: list[str] = []
    owner_paths: set[str] = set()
    for family in families:
        require(isinstance(family, dict), "invalid first-party source family")
        identifier = family.get("id")
        require(isinstance(identifier, str) and identifier not in family_ids,
                "duplicate source-family owner")
        family_ids.append(identifier)
        owners = family.get("owners")
        require(isinstance(owners, list) and owners,
                "family has no independent source owners")
        for owner in owners:
            require(isinstance(owner, dict), "invalid source owner")
            path, digest, size = owner.get("path"), owner.get("sha256"), owner.get("bytes")
            require(isinstance(path, str) and path not in owner_paths
                    and isinstance(digest, str) and isinstance(size, int)
                    and size >= 0, "duplicate or invalid first-party source owner")
            checked_read(path, digest, size)
            owner_paths.add(path)
    require(tuple(family_ids) == ("c", "rust", "zig", "cpp", "go", "fortran")
            and len(owner_paths) == 25
            and ORIGINAL_PATH in owner_paths and ADAPTER_PATH in owner_paths,
            "first-party ownership closure changed")

    inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v19.inputs.json"],
        "V19 inputs")
    summary = strict_json(
        protected["docs/evidence/candidate-current-overview-v19.json"],
        "V19 summary")
    require(inputs.get("repository_evidence_owner_count") == 71
            and inputs.get("preserved_v18_repository_evidence_owner_count") == 69
            and inputs.get("new_go_result_repository_evidence_owner_count") == 2
            and inputs.get("full_case_denominator") == 31237
            and inputs.get("suite_count") == 13,
            "V19 historical evidence or P0 denominator changed")
    require(summary.get("schema") == "rebar-candidate-current-overview-v19-summary"
            and summary.get("status") == "PASS"
            and summary.get("repository_evidence_owner_count") == 71
            and summary.get("full_case_denominator") == 31237
            and summary.get("suite_count") == 13,
            "published V19 baseline changed")
    snapshot = summary.get("snapshot")
    require(isinstance(snapshot, dict)
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 71
            and snapshot.get("current_source_owner_count") == 25
            and snapshot.get("frozen_independent_engine_family_count") == 6
            and snapshot.get("current_tested_candidate_family_count") == 5
            and snapshot.get("qualified_candidate_count") == 0
            and snapshot.get("verified_activation_v4_current_active_target_count") == 0
            and snapshot.get("c_actual_semantic_mismatch_count") == 2094
            and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS,
            "current candidate, activation, or evidence truth changed")
    campaign = snapshot.get("go_v2_full_original_campaign")
    require(isinstance(campaign, dict) and campaign.get("status") == "FAIL"
            and campaign.get("completed_suite_count") == 13
            and campaign.get("semantic_mismatch_count") == 4518
            and campaign.get("infrastructure_failure_count") == 4
            and campaign.get("crash_count") == 0
            and campaign.get("timeout_count") == 0
            and campaign.get("restoration_status") == "PASS",
            "preserved 13-suite Go failure or restoration changed")
    for value in (inputs, summary, snapshot):
        require(value.get("final_holdout_opened") is False
                and value.get("final_comparison_cases_generated") is False
                and value.get("final_comparison_planned_case_count") == 4194304
                and value.get("performance") == "NOT MEASURED"
                and value.get("memory") == "NOT MEASURED"
                and value.get("confidence_intervals") == "NOT MEASURED",
                "holdout or unmeasured performance boundary changed")
    require(snapshot.get("hidden_cases_read") == 0
            and snapshot.get("performance_files_read") == 0
            and snapshot.get("clock_samples") == 0
            and snapshot.get("timing_trials_run") == 0
            and snapshot.get("final_holdout_authorized") is False
            and snapshot.get("winner_selected") is False
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0,
            "holdout, benchmark, clock, or winner boundary changed")

    history: dict[str, str] = {}
    discover_evidence(inputs, history)
    discover_evidence(summary, history)
    require(len(history) == 76, "digest-addressed V19 history closure changed")
    for path, digest in sorted(history.items()):
        checked_read(path, digest)
    require(sum(path.startswith("oracle/phase2/evidence/") for path in history) == 46
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "digest-addressed history roots changed")

    result = contract_document(source_pin, protocol_pin)
    if contract_pin is not None:
        valid_digest(contract_pin, "repair contract")
        actual = checked_read("oracle/phase2/first-party-source-repair-v1.json",
                              contract_pin)
        require(actual == canonical(result),
                "repair contract is not exactly canonical or has changed")
    return result, derived


def contract_document(source_pin: str, protocol_pin: str) -> dict:
    return {
        "schema": SCHEMA,
        "version": 1,
        "phase": "SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "tool": {
            "path": "tools/apply_owned_first_party_source_repair_v1.py",
            "sha256": source_pin,
        },
        "protocol": {
            "path": "oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md",
            "sha256": protocol_pin,
        },
        "oracle": {
            "case_execution_count": 31237,
            "implementation": "CPython",
            "manifest_path": "oracle/phase1/p0-completeness-v1.json",
            "manifest_sha256": SUPPORT["oracle/phase1/p0-completeness-v1.json"],
            "private_waiver_count": 13,
            "suite_count": 13,
            "suite_ids": list(SUITE_IDS),
            "version": "3.14.6",
        },
        "source_baseline": {
            "frozen_family_count": 6,
            "frozen_family_ids": ["c", "rust", "zig", "cpp", "go", "fortran"],
            "frozen_source_owner_count": 25,
            "manifest_path": "oracle/phase2/native-source-build-v7.json",
            "manifest_sha256": SUPPORT["oracle/phase2/native-source-build-v7.json"],
        },
        "repair": {
            "adapter": {
                "bytes": ADAPTER_BYTES,
                "path": ADAPTER_PATH,
                "sha256": ADAPTER_SHA256,
            },
            "callback_invocation_count_after": 2,
            "callback_invocation_count_before": 2,
            "derived_source": {
                "bytes": DERIVED_BYTES,
                "materialized": False,
                "sha256": DERIVED_SHA256,
            },
            "function": "pattern_substitute",
            "new_block": {
                "bytes": len(NEW_BLOCK),
                "occurrence_count_after": 1,
                "occurrence_count_before": 0,
                "sha256": sha256(NEW_BLOCK),
            },
            "old_block": {
                "bytes": len(OLD_BLOCK),
                "occurrence_count_after": 0,
                "occurrence_count_before": 1,
                "sha256": sha256(OLD_BLOCK),
            },
            "original_source": {
                "bytes": ORIGINAL_BYTES,
                "modified": False,
                "path": ORIGINAL_PATH,
                "sha256": ORIGINAL_SHA256,
            },
            "pybuf_simple_occurrence_count_after": 4,
            "pybuf_simple_occurrence_count_before": 4,
            "successful_subject_cleanup": "EXISTING SINGLE DONE LABEL; UNCHANGED",
            "subject_failure_cleanup": "ONE TEMPLATE DECREF; NO SECOND SUBJECT RELEASE",
            "template_failure_cleanup": "NO SUBJECT ACQUIRED",
            "transformation": "EXACTLY ONE ANCHORED FIRST-PARTY C SOURCE BLOCK",
        },
        "published_history": {
            "authenticated_digest_addressed_history_paths": 76,
            "authoritative_counted_evidence_owner_count": 71,
            "current_active_target_count": 0,
            "current_tested_candidate_family_count": 5,
            "experiment_history_path_count": 30,
            "go_full_campaign_infrastructure_failure_count": 4,
            "go_full_campaign_semantic_mismatch_count": 4518,
            "go_full_campaign_status": "FAIL",
            "go_full_campaign_suite_count": 13,
            "go_restoration_status": "PASS",
            "oracle_evidence_path_count": 46,
            "overview_inputs_path": "docs/evidence/candidate-current-overview-v19.inputs.json",
            "overview_inputs_sha256": SUPPORT[
                "docs/evidence/candidate-current-overview-v19.inputs.json"],
            "overview_path": "docs/evidence/candidate-current-overview-v19.json",
            "overview_sha256": SUPPORT["docs/evidence/candidate-current-overview-v19.json"],
            "qualified_candidate_count": 0,
        },
        "apply_policy": {
            "candidate_source_mutation": "FORBIDDEN",
            "explicit_apply_required": True,
            "existing_destination": "FORBIDDEN",
            "external_owner": "FORBIDDEN",
            "holdout": "NOT OPENED",
            "mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "phase_names": ["reference-a", "reference-b"],
            "private_directory_mode": "0700",
            "private_file_mode": "0600",
            "private_root_parent": "/tmp",
            "private_root_prefix": "rebar-phase2-native-build-v8-c-",
            "relative_destination": "candidates/_vm_native.c",
            "workspace_destination": "FORBIDDEN",
        },
        "phase_boundary": {
            "candidate_correctness": "NOT MEASURED",
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "clock_samples": 0,
            "compiler_processes_started": 0,
            "final_comparison_cases_generated": False,
            "final_comparison_planned_case_count": 4194304,
            "holdout": "NOT OPENED",
            "holdout_opened": False,
            "memory": "NOT MEASURED",
            "native_libraries_loaded": 0,
            "network_requests": 0,
            "performance": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "source_apply_count": 0,
            "timing_trials_run": 0,
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        },
        "pinned_support": [
            {"path": path, "sha256": digest}
            for path, digest in sorted(SUPPORT.items())
        ],
    }


def checked_private_directory(parent: int, component: str) -> int:
    require(component not in ("", ".", "..") and "/" not in component,
            "invalid private directory component")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    fd = os.open(component, flags, dir_fd=parent)
    try:
        info = os.fstat(fd)
        require(stat.S_ISDIR(info.st_mode)
                and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.geteuid(),
                "private phase directory is not exclusive and owner-only")
        return fd
    except BaseException:
        os.close(fd)
        raise


def apply_private(snapshot_root: str, derived: bytes) -> dict:
    require(isinstance(snapshot_root, str) and len(snapshot_root) <= 512,
            "invalid private snapshot root")
    parsed = PurePosixPath(snapshot_root)
    require(parsed.is_absolute() and str(parsed) == snapshot_root,
            "snapshot root must be a canonical absolute path")
    parts = parsed.parts
    require(len(parts) == 5 and parts[1] == "tmp"
            and parts[2].startswith("rebar-phase2-native-build-v8-c-")
            and len(parts[2]) > len("rebar-phase2-native-build-v8-c-")
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in parts[2])
            and parts[3] in ("reference-a", "reference-b")
            and parts[4] == "source",
            "snapshot must be a fresh, two-phase, private V8 C source root")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    tmpfd = os.open("/tmp", flags)
    rootfd = phasefd = sourcefd = candidatefd = otherfd = None
    destination = None
    try:
        rootfd = checked_private_directory(tmpfd, parts[2])
        phasefd = checked_private_directory(rootfd, parts[3])
        other = "reference-b" if parts[3] == "reference-a" else "reference-a"
        otherfd = checked_private_directory(rootfd, other)
        require((os.fstat(phasefd).st_dev, os.fstat(phasefd).st_ino)
                != (os.fstat(otherfd).st_dev, os.fstat(otherfd).st_ino),
                "the two private build phases alias")
        sourcefd = checked_private_directory(phasefd, "source")
        candidatefd = checked_private_directory(sourcefd, "candidates")
        original_before = checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
        require(repaired_source(original_before, ORIGINAL_SHA256, ORIGINAL_BYTES)
                == derived, "derived snapshot no longer matches original source")
        file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
        destination = os.open("_vm_native.c", file_flags, 0o600,
                              dir_fd=candidatefd)
        info = os.fstat(destination)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1
                and info.st_uid == os.geteuid()
                and stat.S_IMODE(info.st_mode) == 0o600,
                "private derived source is not a unique, owner-only file")
        offset = 0
        while offset < len(derived):
            wrote = os.write(destination, derived[offset:])
            require(wrote > 0, "incomplete private source write")
            offset += wrote
        os.fsync(destination)
        after = os.fstat(destination)
        require((info.st_dev, info.st_ino, info.st_uid, info.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == DERIVED_BYTES,
                "private derived source identity changed during write")
        os.close(destination)
        destination = None
        verifyfd = os.open("_vm_native.c", os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                           dir_fd=candidatefd)
        try:
            verify = os.fstat(verifyfd)
            require((verify.st_dev, verify.st_ino, verify.st_uid, verify.st_nlink,
                     verify.st_size)
                    == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink,
                        after.st_size), "private source was substituted")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(verifyfd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            require(b"".join(chunks) == derived,
                    "private derived source bytes changed")
        finally:
            os.close(verifyfd)
        os.fsync(candidatefd)
        checked_read(ORIGINAL_PATH, ORIGINAL_SHA256, ORIGINAL_BYTES)
        return {
            "candidate_original_modified": False,
            "derived_bytes": DERIVED_BYTES,
            "derived_sha256": DERIVED_SHA256,
            "mode": "EXCLUSIVE PRIVATE SNAPSHOT APPLY",
            "phase": parts[3],
            "schema": SCHEMA,
            "snapshot_root": snapshot_root,
            "source_apply_count": 1,
            "status": "PASS",
        }
    finally:
        if destination is not None:
            os.close(destination)
        for fd in (candidatefd, sourcefd, otherfd, phasefd, rootfd, tmpfd):
            if fd is not None:
                os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
        valid_digest(options.source_sha256, "repair tool")
        valid_digest(options.protocol_sha256, "repair protocol")
        if options.contract_sha256 is not None:
            valid_digest(options.contract_sha256, "repair contract")
        if options.self_test:
            require(options.snapshot_root is None, "self-test cannot apply source")
            result = self_test()
        elif options.render_contract:
            require(options.snapshot_root is None
                    and options.contract_sha256 is None,
                    "contract rendering cannot apply or assume a contract")
            result, _derived = verify_context(options.source_sha256,
                                              options.protocol_sha256)
        else:
            require(options.contract_sha256 is not None,
                    "frozen verification requires an explicit contract SHA-256")
            contract, derived = verify_context(options.source_sha256,
                                               options.protocol_sha256,
                                               options.contract_sha256)
            if options.verify_frozen_context:
                require(options.snapshot_root is None,
                        "read-only verification cannot apply source")
                result = {
                    "authenticated_digest_addressed_history_paths": 76,
                    "authoritative_counted_evidence_owner_count": 71,
                    "candidate_imports": 0,
                    "candidate_processes_started": 0,
                    "clock_samples": 0,
                    "compiler_processes_started": 0,
                    "derived_source_bytes": DERIVED_BYTES,
                    "derived_source_materialized": False,
                    "derived_source_sha256": DERIVED_SHA256,
                    "final_comparison_planned_case_count": 4194304,
                    "frozen_case_execution_count": 31237,
                    "frozen_independent_family_count": 6,
                    "frozen_private_waiver_count": 13,
                    "frozen_source_owner_count": 25,
                    "frozen_suite_count": 13,
                    "holdout_opened": False,
                    "mode": "READ-ONLY FROZEN CONTEXT",
                    "network_requests": 0,
                    "qualified_candidate_count": 0,
                    "schema": contract["schema"],
                    "source_apply_count": 0,
                    "status": "PASS",
                    "workspace_mutations": 0,
                }
            else:
                require(options.snapshot_root is not None,
                        "source application requires an explicit snapshot root")
                result = apply_private(options.snapshot_root, derived)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (GateError, OSError, ValueError, TypeError) as error:
        sys.stderr.write(f"FIRST-PARTY SOURCE REPAIR V1: FAIL: {error}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
