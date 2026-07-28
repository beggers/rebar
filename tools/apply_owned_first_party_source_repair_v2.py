#!/usr/bin/env python3
"""Freeze one evidence-backed, first-party legacy C Match pickle repair."""

from __future__ import annotations

import argparse
import builtins
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
from typing import Any


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SCHEMA = "rebar-phase2-owned-first-party-source-repair-v2"
SELF = "tools/apply_owned_first_party_source_repair_v2.py"
PROTOCOL = "oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V2.md"
CONTRACT = "oracle/phase2/first-party-source-repair-v2.json"
MAX_OWNER_BYTES = 64 * 1024 * 1024
MAX_EXPANDED_BYTES = 24 * 1024 * 1024
SUITES = (
    ("original_bounded_v5", 151, 0),
    ("public_v3", 864, 0),
    ("scanner_v3", 1024, 0),
    ("buffer_v3", 768, 0),
    ("managed_v1", 1024, 0),
    ("scanner_verbose_v1", 2854, 0),
    ("public_types_v1", 6912, 248),
    ("substitution_v2", 5120, 224),
    ("shape_v2", 10240, 672),
    ("public_surface_v19", 1376, 114),
    ("subinterpreter_v2", 128, 0),
    ("pep688_v4", 264, 4),
    ("threaded_pattern_v1", 512, 0),
)
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
V7_MANIFEST = (
    "oracle/phase2/native-source-build-v7.json",
    "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
    28924,
)
ORIGINAL_SOURCE = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218185,
)
ADAPTER = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60707,
)
V1 = {
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
V1_DERIVED_SHA256 = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
V1_DERIVED_BYTES = 218308
GRAPH = {
    "source": (
        "tools/render_candidate_current_overview_v25.py",
        "9b1eabba4a3bd991c4359af4ab1482fe6f1ce848bb9e5df6fdd9e8bdafb21204",
        98948,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v25.inputs.json",
        "123210219fac109506c03c2f76f89fda33aa5e08b0628fef43b9236d05bc1abe",
        37281,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v25.json",
        "8e4101c896e316190928d0710ca4442488c925ee5ef421507ba4dd08ff10a6d9",
        144980,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v25.svg",
        "db2f1a11e49fd58701ad89111aa422e619431eb9834d3fb5ae66deffcd75f0bb",
        13188,
    ),
}
ORIGINAL_PRODUCER = (
    "tools/run_owned_six_family_original_p0_producer_v3.py",
    "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
    195555,
)
PUBLIC_ORACLE = (
    "tools/independent_public_type_identity_serialization_v1.py",
    "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
    150015,
)
PUBLIC_ARCHIVE = (
    "oracle/phase2/evidence/"
    "frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-public_types_v1.json.gz",
    "bd0f8ed8691785c33c0fdb4d0a506808c959d1e412d655d742d5a4ea46808ce4",
    206151,
)
PUBLIC_RECEIPT = (
    "oracle/phase2/evidence/"
    "frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-"
    "public_types_v1-publication-receipt.json",
    "5548f27728cfb8e9d941aa9a3d6c4220d889d82707384d73f41f5a2ec92e3964",
    1471,
)
PUBLIC_EXPANDED_SHA256 = "2485d6159feb2ab32628355a33d5f2b5552c6e40d48317557849e5cf3fb1b532"
PUBLIC_EXPANDED_BYTES = 15960736
PUBLIC_MATRIX_SHA256 = "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
PUBLIC_REFERENCE_SHA256 = "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
PUBLIC_CANDIDATE_SHA256 = "894552a71ec54f4012bf64e7202c656d915ef2b097e6ca257116359e3352ac7c"
CAMPAIGN_LABEL = "phase2-v10-live-original-p0"
PICKLE_OLD = (
    b'static PyObject *match_reduce(MatchObject *match, PyObject *ignored) '
    b'{ (void)match; (void)ignored; PyErr_SetString(PyExc_TypeError,'
    b'"cannot pickle \'re.Match\' object"); return NULL; }'
)
PICKLE_NEW = b'''static PyObject *match_reduce(MatchObject *match, PyObject *ignored) {
    (void)ignored;
    VMModuleState *state=vm_type_state(Py_TYPE(match));
    if (!state) return NULL;
    if (!state->scanner_reconstructor || !state->match_type) {
        PyErr_SetString(PyExc_RuntimeError,
                        "native match reconstruction is not configured");
        return NULL;
    }
    PyObject *arguments=PyTuple_Pack(3,state->match_type,
                                     (PyObject *)&PyBaseObject_Type,Py_None);
    if (!arguments) return NULL;
    PyObject *result=PyTuple_Pack(2,state->scanner_reconstructor,arguments);
    Py_DECREF(arguments);
    return result;
}

static PyObject *match_reduce_ex(MatchObject *match, PyObject *protocol) {
    PyObject *index=PyNumber_Index(protocol);
    if (!index) return NULL;
    Py_ssize_t version=PyLong_AsSsize_t(index);
    Py_DECREF(index);
    if (version == -1 && PyErr_Occurred()) return NULL;
    if (version < 2) return match_reduce(match,NULL);
    PyErr_SetString(PyExc_TypeError,"cannot pickle 're.Match' object");
    return NULL;
}'''
METHOD_OLD = (
    b'    {"__reduce_ex__",(PyCFunction)match_reduce,METH_O,'
    b'"Matches cannot be pickled."},\n'
)
METHOD_NEW = (
    b'    {"__reduce_ex__",(PyCFunction)match_reduce_ex,METH_O,'
    b'"Matches cannot be pickled."},\n'
)
MATCH_START = b"static PyObject *match_copy("
MATCH_END = b"static PyObject *match_class_getitem("
METHOD_START = b"static PyMethodDef MatchMethods[]={"
METHOD_END = b"static PyGetSetDef MatchGetSet[]={"
EXPECTED_COHORTS = {
    "cache-pattern-type-separation": 96,
    "flags-unknown-bit-retention": 12,
    "module-public-error-alias": 96,
    "pattern-and-match-representation": 12,
    "pickle-match-rejection": 32,
}


class RepairError(Exception):
    """The immutable source freeze or an explicit effect boundary failed."""


def require(value: Any, message: str) -> None:
    if value is not True:
        raise RepairError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact first-party source bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(value, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise RepairError("reject a noncanonical C pickle repair contract") from error


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require an exact lowercase SHA-256: " + label)
    return value


def relative_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one bounded canonical relative owner")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value
            and 0 < len(path.parts) <= 16
            and all(part not in ("", ".", "..") for part in path.parts),
            "reject a linked, escaped, or noncanonical owner")
    return path.parts


def read_owner(relative: str, fingerprint: str,
               expected_bytes: int | None = None) -> bytes:
    parts = relative_parts(relative)
    checked_digest(fingerprint, relative)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    parent = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=parent)
            os.close(parent)
            parent = following
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and 0 <= before.st_size <= MAX_OWNER_BYTES,
                    "require an unchanged bounded regular source owner")
            if expected_bytes is not None:
                require(before.st_size == expected_bytes,
                        "reject substituted exact source-owner bytes")
            blocks: list[bytes] = []
            remaining = before.st_size
            while remaining:
                block = os.read(descriptor, min(remaining, 1024 * 1024))
                require(bool(block), "reject a truncated authenticated source owner")
                blocks.append(block)
                remaining -= len(block)
            require(os.read(descriptor, 1) == b"",
                    "reject concealed bytes in a frozen source owner")
            after = os.fstat(descriptor)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns),
                    "reject a source owner changed while it was read")
            raw = b"".join(blocks)
            require(len(raw) == before.st_size and digest(raw) == fingerprint,
                    "authenticate every original byte: " + relative)
            return raw
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)


def document(raw: bytes, label: str) -> dict[str, Any]:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "reject a repeated JSON key: " + label)
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda item: (_ for _ in ()).throw(
                RepairError("reject a nonfinite JSON value: " + item)),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise RepairError("reject incomplete frozen JSON: " + label) from error
    require(type(value) is dict and canonical(value) == raw,
            "require canonical complete JSON: " + label)
    return value


def load_module(owner: tuple[str, str, int], name: str) -> types.ModuleType:
    raw = read_owner(*owner)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / owner[0])
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module


def owned_repair(previous: bytes, *, frozen: bool = True) -> bytes:
    require(type(previous) is bytes, "repair only complete first-party C bytes")
    if frozen:
        require(len(previous) == V1_DERIVED_BYTES
                and digest(previous) == V1_DERIVED_SHA256,
                "layer exclusively on the already successful V1 buffer repair")
    for block, label in (
        (MATCH_START, "match section"), (MATCH_END, "next match operation"),
        (METHOD_START, "Match method table"), (METHOD_END, "next Match table"),
        (PICKLE_OLD, "old Match reduction"), (METHOD_OLD, "old protocol entry"),
    ):
        require(previous.count(block) == 1,
                "require exactly one first-party " + label)
    require(previous.count(PICKLE_NEW) == 0 and previous.count(METHOD_NEW) == 0,
            "reject an already applied or nonunique Match reduction")
    function_start = previous.index(MATCH_START)
    function_end = previous.index(MATCH_END, function_start + len(MATCH_START))
    old_at = previous.index(PICKLE_OLD)
    require(function_start < old_at < function_end,
            "keep the legacy reduction inside the genuine Match section")
    table_start = previous.index(METHOD_START)
    table_end = previous.index(METHOD_END, table_start + len(METHOD_START))
    method_at = previous.index(METHOD_OLD)
    require(table_start < method_at < table_end,
            "change only the genuine Match protocol method entry")
    first = previous.replace(PICKLE_OLD, PICKLE_NEW, 1)
    derived = first.replace(METHOD_OLD, METHOD_NEW, 1)
    require(derived.count(PICKLE_OLD) == 0
            and derived.count(PICKLE_NEW) == 1
            and derived.count(METHOD_OLD) == 0
            and derived.count(METHOD_NEW) == 1,
            "require exactly the two anchored parts of one pickle feature")
    reconstructed = derived.replace(METHOD_NEW, METHOD_OLD, 1).replace(
        PICKLE_NEW, PICKLE_OLD, 1,
    )
    require(reconstructed == previous,
            "forbid any change outside the exact original Match reduction")
    require(b"state->scanner_reconstructor" in PICKLE_NEW
            and b"state->match_type" in PICKLE_NEW
            and b"PyObject *)&PyBaseObject_Type,Py_None" in PICKLE_NEW
            and b"if (version < 2) return match_reduce(match,NULL);" in PICKLE_NEW
            and b'PyErr_SetString(PyExc_TypeError,"cannot pickle \'re.Match\' object");'
            in PICKLE_NEW
            and b"PyNumber_Index(protocol)" in PICKLE_NEW
            and b"Py_DECREF(index);" in PICKLE_NEW
            and b"Py_DECREF(arguments);" in PICKLE_NEW,
            "preserve genuine owned copyreg reduction and protocol >= 2 rejection")
    for forbidden in (
        b"import re", b"from re ", b"import _sre", b"PyImport_ImportModule",
        b"dlopen(", b"ctypes", b"subprocess", b"candidates.rust",
        b"candidates.zig", b"candidates.cpp", b"candidates.go",
        b"candidates.fortran", b"PyBUF_SIMPLE", b"substitute_callable(",
        b"static PyObject *scanner_reduce(",
        b"static PyObject *scanner_reduce_ex(",
    ):
        require(derived.count(forbidden) == previous.count(forbidden),
                "preserve first-party engine ownership and previous repairs")
    return derived


class SourceOnlyWall:
    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = 0

    def install(self, owner: Any, name: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked += 1
            raise RepairError("source-only effect rejected: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open",)),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir",
                  "makedirs", "remove", "unlink", "replace", "rename",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "resolve", "mkdir",
                    "unlink", "rename", "replace")),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "thread_time", "thread_time_ns", "sleep")),
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_source() -> bytes:
    return (
        b"/* synthetic owned C: no compiler, candidate, or filesystem */\n"
        + MATCH_START + b"MatchObject *match, PyObject *ignored) { return NULL; }\n"
        + PICKLE_OLD + b"\n"
        + MATCH_END + b"PyObject *type, PyObject *item) { return NULL; }\n"
        + METHOD_START + b"\n" + METHOD_OLD + b"    {NULL,NULL,0,NULL}\n};\n"
        + METHOD_END + b"\n    {NULL,NULL,NULL,NULL,NULL}\n};\n"
        + b"/* PyBUF_SIMPLE substitute_callable( */\n"
        + b"static PyObject *scanner_reduce(Scanner *x, PyObject *y);\n"
        + b"static PyObject *scanner_reduce_ex(Scanner *x, PyObject *y);\n"
    )


def self_test() -> dict[str, Any]:
    accepted = 0
    rejected = 0
    sample = synthetic_source()
    with SourceOnlyWall() as wall:
        derived = owned_repair(sample, frozen=False)
        for condition, reason in (
            (derived.count(PICKLE_NEW) == 1, "one owned reduction"),
            (derived.count(METHOD_NEW) == 1, "one protocol method"),
            (derived.count(PICKLE_OLD) == 0, "old reduction removed"),
            (derived.count(METHOD_OLD) == 0, "old protocol method removed"),
            (derived.replace(METHOD_NEW, METHOD_OLD, 1).replace(
                PICKLE_NEW, PICKLE_OLD, 1) == sample, "all other bytes preserved"),
            (b"version < 2" in derived, "legacy-only successful reduction"),
            (b"cannot pickle 're.Match' object" in derived,
             "modern-protocol TypeError preserved"),
            (b"state->scanner_reconstructor" in derived,
             "already authenticated copyreg reconstructor"),
            (b"state->match_type" in derived, "owned native Match type"),
            (derived.count(b"PyBUF_SIMPLE") == sample.count(b"PyBUF_SIMPLE"),
             "original buffer ownership"),
            (derived.count(b"substitute_callable(")
             == sample.count(b"substitute_callable("), "V1 callable ownership"),
        ):
            require(condition, "synthetic positive failed: " + reason)
            accepted += 1

        def reject(call: Any, label: str) -> None:
            nonlocal rejected
            try:
                call()
            except (RepairError, OSError, ValueError, TypeError):
                rejected += 1
            else:
                raise RepairError("hostile control was accepted: " + label)

        for mutation, label in (
            (sample.replace(PICKLE_OLD, b"/* missing */"), "missing old reduction"),
            (sample.replace(PICKLE_OLD, PICKLE_OLD + PICKLE_OLD),
             "duplicate old reduction"),
            (sample.replace(METHOD_OLD, b"/* missing */\n"), "missing method entry"),
            (sample.replace(METHOD_OLD, METHOD_OLD + METHOD_OLD),
             "duplicate method entry"),
            (sample.replace(MATCH_START, b"foreign_match("), "foreign Match owner"),
            (sample.replace(MATCH_END, b"foreign_match_end("), "missing Match end"),
            (sample.replace(METHOD_START, b"static PyMethodDef Foreign[]={"),
             "foreign method table"),
            (sample.replace(METHOD_END, b"static PyGetSetDef Foreign[]={"),
             "foreign method end"),
            (sample.replace(PICKLE_OLD, PICKLE_NEW), "already changed reduction"),
            (sample.replace(METHOD_OLD, METHOD_NEW), "already changed method"),
            (PICKLE_OLD + b"\n" + sample.replace(PICKLE_OLD, b"/* moved */"),
             "reduction outside Match owner"),
            (METHOD_OLD + sample.replace(METHOD_OLD, b"/* moved */\n"),
             "method outside Match method table"),
        ):
            reject(lambda value=mutation: owned_repair(value, frozen=False), label)
        reject(lambda: owned_repair(sample), "synthetic source as frozen C")
        for value in ("", "/tmp/escape", "../escape", "a/../escape",
                      "a//escape", "./owner", "a/", "x" * 513):
            reject(lambda item=value: relative_parts(item), "unsafe relative owner")
        for value in ("", "0" * 63, "0" * 65, "G" * 64, "x" * 64):
            reject(lambda item=value: checked_digest(item, "synthetic"),
                   "invalid owner digest")
        for raw in (b'{"a":1,"a":2}\n', b'{"a":NaN}\n', b"[]\n",
                    b'{"a": 1}\n'):
            reject(lambda data=raw: document(data, "synthetic"),
                   "noncanonical or unsafe JSON")
        effects = (
            (lambda: builtins.open("/tmp/forbidden"), "builtin file"),
            (lambda: io.open("/tmp/forbidden"), "io file"),
            (lambda: os.open("/tmp/forbidden", os.O_RDONLY), "file descriptor"),
            (lambda: os.read(0, 1), "file read"),
            (lambda: os.write(1, b"x"), "file write"),
            (lambda: os.stat("/tmp"), "owner stat"),
            (lambda: os.lstat("/tmp"), "symlink stat"),
            (lambda: os.mkdir("/tmp/forbidden"), "private directory"),
            (lambda: os.unlink("/tmp/forbidden"), "destructive unlink"),
            (lambda: os.replace("/tmp/a", "/tmp/b"), "owner replacement"),
            (lambda: Path("/tmp/forbidden").read_bytes(), "Path read"),
            (lambda: Path("/tmp/forbidden").write_bytes(b"x"), "Path write"),
            (lambda: Path("/tmp").resolve(), "private path resolution"),
            (lambda: subprocess.run(("true",)), "compiler process"),
            (lambda: subprocess.Popen(("true",)), "candidate process"),
            (lambda: socket.socket(), "network"),
            (lambda: tempfile.mkdtemp(), "temporary build root"),
            (lambda: tempfile.mkstemp(), "temporary owner"),
            (lambda: importlib.import_module("candidates.vm_candidate"),
             "candidate import"),
            (lambda: importlib.import_module("re"), "stdlib engine import"),
            (lambda: threading.Thread().start(), "background thread"),
            (lambda: time.time(), "wall clock"),
            (lambda: time.monotonic(), "monotonic clock"),
            (lambda: time.perf_counter(), "performance clock"),
            (lambda: time.perf_counter_ns(), "nanosecond clock"),
            (lambda: time.sleep(0), "wait"),
        )
        for probe, label in effects:
            reject(probe, label)
        require(wall.blocked == len(effects),
                "independently account for every blocked source-only effect")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "version": 2, "family": "c",
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_controls": len(effects),
        "frozen_case_execution_denominator": 31237,
        "frozen_suite_count": 13, "frozen_private_waiver_count": 13,
        "historical_c_semantic_mismatch_count": 1262,
        "historical_match_pickle_mismatch_count": 32,
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0, "candidate_processes_started": 0,
        "compiler_processes_started": 0, "source_apply_count": 0,
        "workspace_mutations": 0, "network_requests": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PYTHON,
            "use only isolated, bytecode-free pinned CPython 3.14.6")


def pin(owner: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def verify_oracle() -> None:
    read_owner(*GOAL)
    p0 = document(read_owner(*PHASE_ONE), "immutable P0 completeness")
    denominator = p0.get("denominator")
    runtime = p0.get("runtime")
    require(p0.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and p0.get("version") == 1 and type(denominator) is dict
            and tuple(denominator.get("counted_suite_ids", ()))
            == tuple(name for name, _, _ in SUITES)
            and denominator.get("final_required_case_execution_denominator") == 31237
            and denominator.get("private_upstream_methods_outside_public_denominator") == 13
            and type(runtime) is dict
            and runtime.get("python_version") == "3.14.6"
            and runtime.get("python_implementation") == "CPython"
            and type(runtime.get("executable")) is dict
            and runtime["executable"].get("path") == PYTHON
            and runtime["executable"].get("sha256") == PYTHON_SHA256
            and p0.get("phase_gate", {}).get("status") == "PASS"
            and p0.get("phase_gate", {}).get("all_obligations_mapped") is True
            and p0.get("phase_gate", {}).get("final_holdout_authorized") is False,
            "preserve the exact complete original CPython correctness oracle")
    manifest = document(read_owner(*V7_MANIFEST), "immutable six-family source freeze")
    families = manifest.get("families")
    require(manifest.get("version") == 7 and manifest.get("family_count") == 6
            and manifest.get("source_owner_count") == 25
            and manifest.get("qualified_candidate_count") == 0
            and type(families) is list and len(families) == 6,
            "preserve all 25 original owners and six independent engine families")
    owners: dict[str, str] = {}
    for family in families:
        require(type(family) is dict and type(family.get("owners")) is list,
                "require the exact original source-family owners")
        for owner in family["owners"]:
            require(type(owner) is dict and type(owner.get("path")) is str
                    and type(owner.get("bytes")) is int,
                    "require a complete original semantic source owner")
            path = owner["path"]
            require(path not in owners, "reject shared candidate semantic sources")
            read_owner(path, owner.get("sha256"), owner["bytes"])
            owners[path] = owner["sha256"]
    require(len(owners) == 25 and owners.get(ORIGINAL_SOURCE[0]) == ORIGINAL_SOURCE[1]
            and owners.get(ADAPTER[0]) == ADAPTER[1],
            "authenticate every original first-party semantic source")


def verify_v1() -> tuple[types.ModuleType, bytes]:
    raw = read_owner(*V1["source"])
    read_owner(*V1["protocol"])
    recorded = document(read_owner(*V1["contract"]), "frozen V1 C source repair")
    original = read_owner(*ORIGINAL_SOURCE)
    read_owner(*ADAPTER)
    previous = types.ModuleType("_rebar_exact_owned_c_source_repair_v1_for_v2")
    previous.__file__ = str(ROOT / V1["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    require(previous.SCHEMA == "rebar-phase2-owned-first-party-source-repair-v1"
            and previous.ORIGINAL_PATH == ORIGINAL_SOURCE[0]
            and previous.ORIGINAL_SHA256 == ORIGINAL_SOURCE[1]
            and previous.ORIGINAL_BYTES == ORIGINAL_SOURCE[2]
            and previous.ADAPTER_PATH == ADAPTER[0]
            and previous.ADAPTER_SHA256 == ADAPTER[1]
            and previous.ADAPTER_BYTES == ADAPTER[2]
            and previous.DERIVED_SHA256 == V1_DERIVED_SHA256
            and previous.DERIVED_BYTES == V1_DERIVED_BYTES,
            "require the exact independently frozen V1 first-party transformation")
    expected = previous.contract_document(V1["source"][1], V1["protocol"][1])
    require(recorded == expected and canonical(expected) == read_owner(*V1["contract"]),
            "independently reproduce every byte of the V1 repair contract")
    derived = previous.repaired_source(original, ORIGINAL_SOURCE[1],
                                       ORIGINAL_SOURCE[2])
    require(type(derived) is bytes and digest(derived) == V1_DERIVED_SHA256
            and len(derived) == V1_DERIVED_BYTES
            and derived.count(previous.NEW_BLOCK) == 1
            and derived.count(previous.OLD_BLOCK) == 0,
            "reproduce the full genuine already repaired C bridge before layering V2")
    return previous, derived


def verify_graph() -> dict[str, Any]:
    raw = {role: read_owner(*owner) for role, owner in GRAPH.items()}
    inputs = document(raw["inputs"], "published V25 graph inputs")
    summary = document(raw["summary"], "published V25 graph summary")
    graph = types.ModuleType("_rebar_exact_published_v25_graph_for_c_pickle_v2")
    graph.__file__ = str(ROOT / GRAPH["source"][0])
    graph.__package__ = ""
    exec(compile(raw["source"], graph.__file__, "exec", dont_inherit=True),
         graph.__dict__)
    require(graph.SCHEMA == "rebar-candidate-current-overview-v25"
            and graph.SELF == GRAPH["source"][0]
            and graph.TOTAL_OWNERS == 139 and graph.TOTAL_REFERENCES == 144
            and tuple((name, count, mismatches)
                      for name, count, mismatches, _ in graph.SUITES) == SUITES,
            "authenticate the independent published V25 graph renderer")
    snapshot = summary.get("snapshot")
    require(type(snapshot) is dict, "require the complete real V25 snapshot")
    graph.validate_snapshot(snapshot)
    require(graph.make_svg(snapshot, GRAPH["source"][1], GRAPH["inputs"][1])
            == raw["svg"],
            "independently reproduce every byte of the current V25 chart")
    require(inputs.get("schema") == "rebar-candidate-current-overview-v25-inputs"
            and inputs.get("version") == 25
            and summary.get("schema") == "rebar-candidate-current-overview-v25-summary"
            and summary.get("status") == "PASS"
            and inputs.get("renderer")
            == {"path": GRAPH["source"][0], "sha256": GRAPH["source"][1]}
            and summary.get("source")
            == {"path": GRAPH["source"][0], "sha256": GRAPH["source"][1]}
            and summary.get("inputs")
            == {"path": GRAPH["inputs"][0], "sha256": GRAPH["inputs"][1]}
            and summary.get("svg")
            == {"path": GRAPH["svg"][0], "sha256": GRAPH["svg"][1]},
            "bind all four actual V25 graph owners independently")
    for value in (inputs, summary, snapshot):
        require(value.get("full_case_denominator") == 31237
                and value.get("suite_count") == 13
                and value.get("performance") == "NOT MEASURED"
                and value.get("memory") == "NOT MEASURED"
                and value.get("final_holdout_opened") is False
                and value.get("winner_selected") is False,
                "preserve the unopened holdout and all original case denominators")
    require(inputs.get("repository_evidence_owner_count") == 139
            and inputs.get("all_digest_addressed_history_path_count") == 144
            and inputs.get("private_waiver_count") == 13
            and inputs.get("candidate_qualified_count") == 0
            and summary.get("repository_evidence_owner_count") == 139
            and summary.get("authenticated_digest_addressed_history_paths") == 144
            and summary.get("private_waiver_count") == 13
            and summary.get("qualified_candidate_count") == 0
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 139
            and snapshot.get("all_digest_addressed_history_path_count") == 144,
            "preserve the genuine complete 139-owner, 144-reference history")
    campaign = inputs.get("current_complete_c_campaign")
    require(type(campaign) is dict
            and campaign == snapshot.get("c_v10_repaired_original_campaign")
            and campaign.get("status") == "FAIL"
            and campaign.get("failure_class") == "SEMANTIC MISMATCH"
            and campaign.get("family") == "c"
            and campaign.get("label") == CAMPAIGN_LABEL
            and campaign.get("completed_suite_count") == 13
            and campaign.get("suite_count") == 13
            and campaign.get("full_case_denominator") == 31237
            and campaign.get("observed_matching_case_count") == 31237
            and campaign.get("actual_candidate_workers") == 13
            and campaign.get("fully_passing_suite_count") == 8
            and campaign.get("verified_passing_case_count") == 7325
            and campaign.get("semantic_mismatch_count") == 1262
            and campaign.get("infrastructure_failure_count") == 0
            and campaign.get("new_repository_evidence_owner_count") == 30
            and campaign.get("all_original_suite_evidence_preserved") is True
            and campaign.get("original_canonical_native_restored") is True
            and campaign.get("qualified") is False,
            "preserve all 30 genuine C result owners and all 1,262 real failures")
    rows = campaign.get("suite_results")
    require(type(rows) is list and len(rows) == len(SUITES),
            "preserve all thirteen complete original C suite records")
    for actual, (name, count, mismatches) in zip(rows, SUITES, strict=True):
        require(type(actual) is dict and actual.get("suite") == name
                and actual.get("case_execution_denominator") == count
                and actual.get("mismatch_count") == mismatches
                and actual.get("status") == ("PASS" if mismatches == 0 else "FAIL")
                and actual.get("actual_worker_started") is True
                and actual.get("all_original_records_and_mismatches_preserved") is True,
                "preserve the actual complete original suite: " + name)
        for role in ("archive", "receipt"):
            owner = actual.get(role)
            require(type(owner) is dict and type(owner.get("bytes")) is int,
                    "require separately pinned C original-suite owners")
            read_owner(owner.get("path"), owner.get("sha256"), owner["bytes"])
    for role in ("archive", "receipt", "aggregate_archive", "aggregate_receipt"):
        owner = campaign.get(role)
        require(type(owner) is dict and type(owner.get("bytes")) is int,
                "preserve the separately signed outer and aggregate C evidence")
        read_owner(owner.get("path"), owner.get("sha256"), owner["bytes"])
    rust = inputs.get("current_repaired_rust_source_build")
    zig = inputs.get("current_repaired_zig_source_build")
    require(type(rust) is dict and rust.get("build_status") == "PASS"
            and rust.get("actual_build_process_count") == 28
            and rust.get("matching_test_status") == "NOT MEASURED"
            and rust.get("actual_candidate_workers") == 0
            and rust.get("candidate_qualified") is False
            and rust.get("holdout") == "NOT OPENED"
            and type(zig) is dict and zig.get("build_status") == "PASS"
            and zig.get("actual_build_process_count") == 26
            and zig.get("matching_test_status") == "NOT MEASURED"
            and zig.get("actual_candidate_workers") == 0
            and zig.get("candidate_qualified") is False
            and zig.get("holdout") == "NOT OPENED",
            "preserve real Rust/Zig builds without inspecting private artifacts")
    return {"graph": graph, "inputs": inputs, "summary": summary,
            "snapshot": snapshot, "campaign": campaign}


def expand_public_archive(raw: bytes) -> bytes:
    blocks: list[bytes] = []
    total = 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as archive:
            while True:
                piece = archive.read(min(1024 * 1024,
                                         MAX_EXPANDED_BYTES + 1 - total))
                if not piece:
                    break
                total += len(piece)
                require(total <= MAX_EXPANDED_BYTES,
                        "reject an oversized original public-type archive")
                blocks.append(piece)
    except (gzip.BadGzipFile, EOFError, OSError) as error:
        raise RepairError("reject an incomplete original public-type archive") from error
    result = b"".join(blocks)
    require(total == PUBLIC_EXPANDED_BYTES
            and digest(result) == PUBLIC_EXPANDED_SHA256,
            "authenticate all complete actual original public-type records")
    return result


def verify_pickle_evidence(campaign: dict[str, Any]) -> dict[str, Any]:
    read_owner(*ORIGINAL_PRODUCER)
    read_owner(*PUBLIC_ORACLE)
    compressed = read_owner(*PUBLIC_ARCHIVE)
    receipt = document(read_owner(*PUBLIC_RECEIPT),
                       "actual original public-type durable receipt")
    owner = receipt.get("archive")
    require(type(owner) is dict
            and owner.get("relative") == PUBLIC_ARCHIVE[0]
            and owner.get("sha256") == PUBLIC_ARCHIVE[1]
            and owner.get("size_bytes") == PUBLIC_ARCHIVE[2]
            and owner.get("exclusive_creation") is True
            and owner.get("file_fsync_completed") is True
            and owner.get("directory_fsync_completed") is True
            and owner.get("same_inode_readback_verified") is True
            and owner.get("mode") == 0o600,
            "authenticate the genuine exclusively published public-type archive")
    require(receipt.get("schema")
            == "rebar-frozen-python-re-p0-candidate-worker-v7-durable-suite-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("candidate_family") == "c"
            and receipt.get("label") == CAMPAIGN_LABEL
            and receipt.get("suite") == "public_types_v1"
            and receipt.get("case_execution_denominator") == 6912
            and receipt.get("phase_one_case_execution_denominator") == 31237
            and receipt.get("mismatch_count") == 248
            and receipt.get("genuine_original_suite") is True
            and receipt.get("all_original_records_and_mismatches_preserved") is True
            and receipt.get("original_producer_sha256") == ORIGINAL_PRODUCER[1]
            and receipt.get("original_c_source_sha256") == ORIGINAL_SOURCE[1]
            and receipt.get("derived_c_source_sha256") == V1_DERIVED_SHA256
            and receipt.get("uncompressed_sha256") == PUBLIC_EXPANDED_SHA256
            and receipt.get("uncompressed_bytes") == PUBLIC_EXPANDED_BYTES
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("candidate_qualified") is False
            and receipt.get("winner_selected") is False,
            "preserve all original public-type cases and the real failed result")
    actual = document(expand_public_archive(compressed),
                      "complete actual original 6,912-case public-type report")
    require(actual.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-actual-original-suite"
            and actual.get("status") == "FAIL"
            and actual.get("suite") == "public_types_v1"
            and actual.get("candidate_family") == "c"
            and actual.get("candidate_module") == "candidates.vm_candidate"
            and actual.get("case_execution_denominator") == 6912
            and actual.get("actual_candidate_case_count") == 6912
            and actual.get("source_relative") == PUBLIC_ORACLE[0]
            and actual.get("source_sha256") == PUBLIC_ORACLE[1]
            and actual.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and actual.get("reference_records_sha256") == PUBLIC_REFERENCE_SHA256
            and actual.get("candidate_records_sha256") == PUBLIC_CANDIDATE_SHA256
            and actual.get("mismatch_count") == 248
            and actual.get("actual_candidate_workers") == 1
            and actual.get("hidden_cases_read") == 0
            and actual.get("benchmark_files_read") == 0
            and actual.get("clock_samples") == 0
            and actual.get("timing_trials_run") == 0
            and actual.get("performance") == "NOT MEASURED"
            and actual.get("holdout") == "NOT OPENED"
            and actual.get("candidate_qualified") is False
            and actual.get("winner_selected") is False,
            "never substitute a synthetic or shortened public-type evaluator")
    records = actual.get("candidate_records")
    mismatches = actual.get("all_mismatches")
    require(type(records) is list and len(records) == 6912
            and type(mismatches) is list and len(mismatches) == 248,
            "preserve every public-type record and all 248 actual mismatches")
    cohorts: dict[str, int] = {}
    legacy: dict[int, int] = {0: 0, 1: 0}
    for difference in mismatches:
        require(type(difference) is dict
                and set(difference) == {"case", "expected_record", "actual_record"}
                and type(difference.get("expected_record")) is dict
                and type(difference.get("actual_record")) is dict,
                "preserve complete genuine expected and actual original records")
        expected = difference["expected_record"]
        observed = difference["actual_record"]
        cohort = expected.get("cohort")
        require(type(cohort) is str and observed.get("cohort") == cohort
                and expected.get("case") == observed.get("case")
                and difference.get("case") == expected.get("case"),
                "never recategorize or replace a real public-type failure")
        cohorts[cohort] = cohorts.get(cohort, 0) + 1
        if cohort == "pickle-match-rejection":
            protocol = expected.get("pickle_protocol")
            expected_outcome = expected.get("outcome")
            observed_outcome = observed.get("outcome")
            require(type(protocol) is int and protocol in legacy
                    and observed.get("pickle_protocol") == protocol
                    and type(expected_outcome) is dict
                    and expected_outcome.get("status") == "return"
                    and type(expected_outcome.get("value")) is dict
                    and expected_outcome["value"].get("kind") == "bytes"
                    and type(expected_outcome["value"].get("hex")) is str
                    and type(observed_outcome) is dict
                    and observed_outcome.get("status") == "raise"
                    and type(observed_outcome.get("exception")) is dict
                    and observed_outcome["exception"].get("message")
                    == "cannot pickle 're.Match' object"
                    and type(observed_outcome["exception"].get("type")) is dict
                    and observed_outcome["exception"]["type"].get("module")
                    == "builtins"
                    and observed_outcome["exception"]["type"].get("name")
                    == "TypeError",
                    "repair only the actual protocol-0/1 legacy pickle defect")
            legacy[protocol] += 1
    require(cohorts == EXPECTED_COHORTS and legacy == {0: 16, 1: 16},
            "preserve all five actual public-type cohorts and exactly 32 target cases")
    protocol_counts = {number: 0 for number in range(6)}
    for record in records:
        if type(record) is dict and record.get("cohort") == "pickle-match-rejection":
            protocol = record.get("pickle_protocol")
            outcome = record.get("outcome")
            require(type(protocol) is int and protocol in protocol_counts
                    and type(outcome) is dict and outcome.get("status") == "raise"
                    and type(outcome.get("exception")) is dict
                    and outcome["exception"].get("message")
                    == "cannot pickle 're.Match' object",
                    "preserve every observed original Match pickle protocol")
            protocol_counts[protocol] += 1
    require(protocol_counts == {number: 16 for number in range(6)},
            "retain all 96 original Match pickle records and modern rejection")
    public = next(row for row in campaign["suite_results"]
                  if row["suite"] == "public_types_v1")
    require(public["archive"] == {"path": PUBLIC_ARCHIVE[0],
                                  "sha256": PUBLIC_ARCHIVE[1],
                                  "bytes": PUBLIC_ARCHIVE[2]}
            and public["receipt"] == {"path": PUBLIC_RECEIPT[0],
                                      "sha256": PUBLIC_RECEIPT[1],
                                      "bytes": PUBLIC_RECEIPT[2]}
            and public.get("mismatch_count") == 248,
            "bind protocol evidence to the complete actual V25 C campaign")
    guard = actual.get("matcher_guard")
    require(type(guard) is dict
            and guard.get("selected_candidate") == "c"
            and guard.get("original_matchers_blocked") is True
            and guard.get("native_sre_blocked") is True
            and guard.get("cross_family_imports_blocked") is True
            and guard.get("external_regex_imports_blocked") is True
            and guard.get("original_matcher_calls") == 0
            and guard.get("external_engine_imports") == 0
            and guard.get("cross_candidate_imports") == 0
            and guard.get("foreign_native_loads") == 0
            and guard.get("owned_native_ffi_allowed") is False,
            "preserve the genuine first-party, zero-delegation C matching proof")
    return {
        "suite": "public_types_v1", "status": "FAIL",
        "case_execution_denominator": 6912,
        "observed_mismatch_count": 248,
        "complete_record_count": 6912,
        "pickle_record_count": 96,
        "legacy_pickle_mismatch_count": 32,
        "legacy_pickle_protocol_counts": {"0": 16, "1": 16},
        "preserved_modern_pickle_protocol_counts":
            {str(number): 16 for number in range(2, 6)},
        "cohort_mismatch_counts": dict(sorted(cohorts.items())),
        "archive": pin(PUBLIC_ARCHIVE), "receipt": pin(PUBLIC_RECEIPT),
        "uncompressed_sha256": PUBLIC_EXPANDED_SHA256,
        "uncompressed_bytes": PUBLIC_EXPANDED_BYTES,
        "source": pin(PUBLIC_ORACLE),
        "matrix_sha256": PUBLIC_MATRIX_SHA256,
        "reference_records_sha256": PUBLIC_REFERENCE_SHA256,
        "candidate_records_sha256": PUBLIC_CANDIDATE_SHA256,
    }


def contract_document(source_pin: str, protocol_pin: str,
                      derived: bytes, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA, "version": 2, "family": "c",
        "phase": "SOURCE FREEZE; NO BUILD OR CANDIDATE RUN",
        "tool": {"path": SELF, "sha256": checked_digest(source_pin, "C V2 source")},
        "protocol": {"path": PROTOCOL,
                     "sha256": checked_digest(protocol_pin, "C V2 protocol")},
        "oracle": {
            "implementation": "CPython", "version": "3.14.6",
            "python": {"path": PYTHON, "sha256": PYTHON_SHA256},
            "manifest": pin(PHASE_ONE), "suite_count": 13,
            "suite_ids": [name for name, _, _ in SUITES],
            "case_execution_denominator": 31237, "private_waiver_count": 13,
        },
        "current_history": {
            "published_graph_version": 25,
            "graph": {role: pin(owner) for role, owner in GRAPH.items()},
            "repository_evidence_owner_count": 139,
            "authenticated_digest_addressed_history_paths": 144,
            "source_family_count": 6, "source_owner_count": 25,
            "qualified_candidate_count": 0,
            "actual_c_campaign_status": "FAIL",
            "actual_c_campaign_evidence_owner_count": 30,
            "actual_c_candidate_worker_count": 13,
            "actual_c_completed_suite_count": 13,
            "actual_c_fully_passing_suite_count": 8,
            "actual_c_verified_passing_case_count": 7325,
            "actual_c_semantic_mismatch_count": 1262,
            "actual_c_infrastructure_failure_count": 0,
            "actual_c_original_native_restored": True,
            "actual_rust_build_process_count": 28,
            "actual_rust_matching": "NOT MEASURED",
            "actual_zig_build_process_count": 26,
            "actual_zig_matching": "NOT MEASURED",
        },
        "previous_repair": {
            "version": 1,
            "owners": {role: pin(owner) for role, owner in V1.items()},
            "original_source": pin(ORIGINAL_SOURCE),
            "unchanged_adapter": pin(ADAPTER),
            "derived_source": {"sha256": V1_DERIVED_SHA256,
                               "bytes": V1_DERIVED_BYTES},
            "buffer_and_substitution_repair_preserved": True,
        },
        "actual_public_type_evidence": evidence,
        "repair": {
            "feature": "MATCH PICKLING FOR LEGACY PROTOCOLS 0 AND 1 ONLY",
            "original_source": pin(ORIGINAL_SOURCE),
            "unchanged_adapter": pin(ADAPTER),
            "input_source": {"sha256": V1_DERIVED_SHA256,
                             "bytes": V1_DERIVED_BYTES},
            "derived_source": {"sha256": digest(derived),
                               "bytes": len(derived), "materialized": False},
            "old_reduction": {"sha256": digest(PICKLE_OLD),
                              "bytes": len(PICKLE_OLD),
                              "occurrence_count_before": 1,
                              "occurrence_count_after": 0},
            "new_reduction": {"sha256": digest(PICKLE_NEW),
                              "bytes": len(PICKLE_NEW),
                              "occurrence_count_before": 0,
                              "occurrence_count_after": 1},
            "old_protocol_entry": {"sha256": digest(METHOD_OLD),
                                   "bytes": len(METHOD_OLD),
                                   "occurrence_count_before": 1,
                                   "occurrence_count_after": 0},
            "new_protocol_entry": {"sha256": digest(METHOD_NEW),
                                   "bytes": len(METHOD_NEW),
                                   "occurrence_count_before": 0,
                                   "occurrence_count_after": 1},
            "targeted_original_mismatch_count": 32,
            "legacy_protocols": [0, 1],
            "modern_protocol_rejection_preserved": [2, 3, 4, 5],
            "owned_reconstructor": "VMModuleState.scanner_reconstructor",
            "owned_match_type": "VMModuleState.match_type",
            "base_object": "PyBaseObject_Type",
            "none_state": True,
            "source_original_modified": False,
            "adapter_original_modified": False,
            "candidate_correctness": "NOT MEASURED",
            "substitution_mismatches_repaired": "NOT MEASURED",
            "shape_mismatches_repaired": "NOT MEASURED",
            "public_surface_mismatches_repaired": "NOT MEASURED",
            "pep688_mismatches_repaired": "NOT MEASURED",
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
        },
        "apply_policy": {
            "explicit_apply_required": True,
            "candidate_source_mutation": "FORBIDDEN",
            "workspace_destination": "FORBIDDEN",
            "existing_destination": "FORBIDDEN",
            "external_owner": "FORBIDDEN",
            "private_root_parent": "/tmp",
            "private_root_prefix": "rebar-phase2-native-build-v8-c-",
            "phase_names": ["reference-a", "reference-b"],
            "private_directory_mode": "0700",
            "private_file_mode": "0600",
            "mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "relative_destination": "candidates/_vm_native.c",
            "same_root_as_v1_source_builder": True,
            "holdout": "NOT OPENED",
        },
        "phase_boundary": {
            "candidate_correctness": "NOT MEASURED",
            "candidate_imports": 0, "candidate_processes_started": 0,
            "compiler_processes_started": 0, "native_libraries_loaded": 0,
            "source_apply_count": 0, "workspace_mutations": 0,
            "network_requests": 0, "hidden_cases_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
            "holdout_opened": False,
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "qualified_candidate_count": 0, "winner_selected": False,
        },
    }


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None) -> tuple[dict[str, Any], bytes]:
    verify_runtime()
    before = frozenset(name for name in sys.modules
                       if name == "candidates" or name.startswith("candidates."))
    require(not before, "do not import a candidate during a C source freeze")
    read_owner(SELF, checked_digest(source_pin, "C V2 source"))
    read_owner(PROTOCOL, checked_digest(protocol_pin, "C V2 protocol"))
    verify_oracle()
    previous, original = verify_v1()
    derived = owned_repair(original)
    require(derived.count(previous.NEW_BLOCK) == 1
            and derived.count(previous.OLD_BLOCK) == 0,
            "preserve the complete previously qualified buffer-order source repair")
    graph = verify_graph()
    evidence = verify_pickle_evidence(graph["campaign"])
    expected = contract_document(source_pin, protocol_pin, derived, evidence)
    if contract_pin is not None:
        raw = read_owner(CONTRACT, checked_digest(contract_pin, "C V2 contract"))
        require(raw == canonical(expected)
                and document(raw, "canonical C V2 machine contract") == expected,
                "independently reproduce the exact complete C V2 source contract")
    after = frozenset(name for name in sys.modules
                      if name == "candidates" or name.startswith("candidates."))
    require(not after and after == before,
            "source-only authentication must never import any regex candidate")
    read_owner(*ORIGINAL_SOURCE)
    read_owner(*ADAPTER)
    return expected, derived


def checked_private_directory(parent: int, component: str) -> int:
    require(type(component) is str and component not in ("", ".", "..")
            and "/" not in component and "\\" not in component,
            "reject a substituted private directory component")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptor = os.open(component, flags, dir_fd=parent)
    try:
        owner = os.fstat(descriptor)
        require(stat.S_ISDIR(owner.st_mode)
                and stat.S_IMODE(owner.st_mode) == 0o700
                and owner.st_uid == os.geteuid(),
                "require a private, owner-only, no-follow source directory")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def apply_private(snapshot_root: str, derived: bytes) -> dict[str, Any]:
    require(type(snapshot_root) is str and len(snapshot_root) <= 512,
            "require one exact existing private C build source root")
    parsed = PurePosixPath(snapshot_root)
    require(parsed.is_absolute() and str(parsed) == snapshot_root,
            "reject a relative or noncanonical private application root")
    parts = parsed.parts
    require(len(parts) == 5 and parts[1] == "tmp"
            and parts[2].startswith("rebar-phase2-native-build-v8-c-")
            and len(parts[2]) > len("rebar-phase2-native-build-v8-c-")
            and all(item.isascii() and (item.isalnum() or item in "-_")
                    for item in parts[2])
            and parts[3] in ("reference-a", "reference-b")
            and parts[4] == "source",
            "reject a workspace, external, linked, or cross-family destination")
    _, previous = verify_v1()
    require(owned_repair(previous) == derived,
            "apply only the exact V1-layered immutable C V2 repair")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    temporary = os.open("/tmp", flags)
    root = phase = peer = source = candidates = destination = None
    try:
        root = checked_private_directory(temporary, parts[2])
        phase = checked_private_directory(root, parts[3])
        peer_name = "reference-b" if parts[3] == "reference-a" else "reference-a"
        peer = checked_private_directory(root, peer_name)
        first = os.fstat(phase)
        second = os.fstat(peer)
        require((first.st_dev, first.st_ino) != (second.st_dev, second.st_ino),
                "require distinct genuinely prepared source-build phases")
        source = checked_private_directory(phase, "source")
        candidates = checked_private_directory(source, "candidates")
        read_owner(*ORIGINAL_SOURCE)
        read_owner(*ADAPTER)
        create = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                  | os.O_NOFOLLOW | os.O_CLOEXEC)
        destination = os.open("_vm_native.c", create, 0o600, dir_fd=candidates)
        before = os.fstat(destination)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                and before.st_uid == os.geteuid()
                and stat.S_IMODE(before.st_mode) == 0o600,
                "create only one fresh private owner-only compiler input")
        offset = 0
        while offset < len(derived):
            wrote = os.write(destination, derived[offset:])
            require(wrote > 0, "reject a partial private source write")
            offset += wrote
        os.fsync(destination)
        after = os.fstat(destination)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == len(derived),
                "preserve the exact exclusive private V2 source owner")
        os.close(destination)
        destination = None
        verifier = os.open("_vm_native.c", os.O_RDONLY | os.O_CLOEXEC
                           | os.O_NOFOLLOW, dir_fd=candidates)
        try:
            verified = os.fstat(verifier)
            require((verified.st_dev, verified.st_ino, verified.st_size,
                     verified.st_uid, verified.st_nlink)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_uid, after.st_nlink),
                    "reject a substituted private V2 compiler input")
            pieces: list[bytes] = []
            while True:
                piece = os.read(verifier, min(1024 * 1024, len(derived) + 1))
                if not piece:
                    break
                pieces.append(piece)
            require(b"".join(pieces) == derived,
                    "authenticate every exact private V2 source byte")
        finally:
            os.close(verifier)
        os.fsync(candidates)
        read_owner(*ORIGINAL_SOURCE)
        read_owner(*ADAPTER)
        return {
            "schema": SCHEMA + "-private-snapshot-application",
            "status": "PASS", "version": 2, "family": "c",
            "snapshot_root": snapshot_root, "phase": parts[3],
            "source_apply_count": 1,
            "derived_source_sha256": digest(derived),
            "derived_source_bytes": len(derived),
            "original_candidate_modified": False,
            "original_adapter_modified": False,
            "candidate_correctness": "NOT MEASURED",
            "actual_candidate_workers": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False,
        }
    finally:
        if destination is not None:
            os.close(destination)
        for descriptor in (candidates, source, peer, phase, root, temporary):
            if descriptor is not None:
                os.close(descriptor)


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--snapshot-root")
    options = parser.parse_args(arguments)
    checked_digest(options.source_sha256, "frozen C V2 source")
    checked_digest(options.protocol_sha256, "frozen C V2 protocol")
    if options.contract_sha256 is not None:
        checked_digest(options.contract_sha256, "frozen C V2 machine contract")
    if options.self_test:
        require(options.contract_sha256 is None and options.snapshot_root is None,
                "synthetic C V2 tests cannot authorize evidence or application")
    elif options.render_contract:
        require(options.contract_sha256 is None and options.snapshot_root is None,
                "contract reproduction cannot apply or presume a frozen contract")
    elif options.verify_frozen_context:
        require(options.contract_sha256 is not None and options.snapshot_root is None,
                "read-only C V2 verification requires its exact machine contract")
    else:
        require(options.contract_sha256 is not None
                and options.snapshot_root is not None,
                "private application requires explicit contract and snapshot pins")
    return options


def main(arguments: list[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            result = self_test()
        else:
            frozen, derived = verify_context(
                options.source_sha256, options.protocol_sha256,
                options.contract_sha256,
            )
            if options.render_contract:
                result = frozen
            elif options.verify_frozen_context:
                result = {
                    "schema": SCHEMA + "-read-only-frozen-context",
                    "status": "PASS", "version": 2, "family": "c",
                    "source_sha256": options.source_sha256,
                    "protocol_sha256": options.protocol_sha256,
                    "contract_sha256": options.contract_sha256,
                    "derived_source_sha256": digest(derived),
                    "derived_source_bytes": len(derived),
                    "v1_derived_source_sha256": V1_DERIVED_SHA256,
                    "v1_derived_source_bytes": V1_DERIVED_BYTES,
                    "published_graph_version": 25,
                    "published_graph_owner_count": 4,
                    "published_graph_reproduced": True,
                    "repository_evidence_owner_count": 139,
                    "authenticated_digest_addressed_history_paths": 144,
                    "actual_c_campaign_evidence_owner_count": 30,
                    "actual_c_candidate_workers": 13,
                    "actual_c_completed_suite_count": 13,
                    "actual_c_fully_passing_suite_count": 8,
                    "actual_c_verified_passing_case_count": 7325,
                    "actual_c_semantic_mismatch_count": 1262,
                    "actual_c_infrastructure_failure_count": 0,
                    "actual_public_type_case_count": 6912,
                    "actual_public_type_mismatch_count": 248,
                    "targeted_legacy_pickle_mismatch_count": 32,
                    "legacy_pickle_protocol_counts": {"0": 16, "1": 16},
                    "preserved_modern_pickle_protocol_counts":
                        {str(number): 16 for number in range(2, 6)},
                    "actual_rust_build_process_count": 28,
                    "actual_zig_build_process_count": 26,
                    "frozen_suite_count": 13,
                    "frozen_case_execution_denominator": 31237,
                    "frozen_private_waiver_count": 13,
                    "candidate_correctness": "NOT MEASURED",
                    "candidate_imports": 0,
                    "candidate_processes_started": 0,
                    "compiler_processes_started": 0,
                    "native_libraries_loaded": 0,
                    "source_apply_count": 0,
                    "workspace_mutations": 0,
                    "network_requests": 0,
                    "hidden_cases_read": 0,
                    "clock_samples": 0,
                    "timing_trials_run": 0,
                    "performance": "NOT MEASURED",
                    "memory": "NOT MEASURED",
                    "holdout": "NOT OPENED",
                    "winner_selected": False,
                }
            else:
                result = apply_private(options.snapshot_root, derived)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (RepairError, OSError, ValueError, TypeError, AttributeError,
            KeyError, EOFError, gzip.BadGzipFile) as error:
        sys.stderr.write("FIRST-PARTY C PICKLE SOURCE REPAIR V2: FAIL: "
                         + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
