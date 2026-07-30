#!/usr/bin/env python3
"""Freeze independently owned Zig replacement lifetime and error provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/apply_owned_zig_replacement_event_semantics_v1.py"
PROTOCOL = "oracle/phase2/ZIG-REPLACEMENT-EVENT-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/zig-replacement-event-semantics-v1.json"
TARGET = "candidates/zig/variants/replacement_event_semantics_v1/py_bridge.c"

BRIDGE = "candidates/zig/py_bridge.c"
BRIDGE_SHA256 = "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
BRIDGE_BYTES = 173026
ENGINE = "candidates/zig/mini_regex.zig"
ENGINE_SHA256 = "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"
ENGINE_BYTES = 186915

SCANNER_SOURCE = "tools/apply_owned_zig_scanner_capture_semantics_v1.py"
SCANNER_SOURCE_SHA256 = "155183987fbc30f716b315d41ddfc9dddf0356c065177de4661198bdc60b85ad"
SCANNER_PROTOCOL = "oracle/phase2/ZIG-SCANNER-CAPTURE-SEMANTICS-V1.md"
SCANNER_PROTOCOL_SHA256 = "48de77e626818bc75ff451e225e1c895445d9ca29b91b59778543c9847032947"
SCANNER_CONTRACT = "oracle/phase2/zig-scanner-capture-semantics-v1.json"
SCANNER_CONTRACT_SHA256 = "fe43d924d74c2bfe1dac5d7e1f936a1975bb53461a7bb73394841e8934ecb27c"
SCANNER_BRIDGE_SHA256 = "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148"
SCANNER_BRIDGE_BYTES = 173082

PICKLE_SOURCE = "tools/apply_owned_zig_match_pickle_semantics_v1.py"
PICKLE_SOURCE_SHA256 = "a389ec3e113014450d2a42ca9deebbf0543c17eba4226a1dc3f7dfa512d4b313"
PICKLE_PROTOCOL = "oracle/phase2/ZIG-MATCH-PICKLE-SEMANTICS-V1.md"
PICKLE_PROTOCOL_SHA256 = "a885bcf346b3e999827188282c0370b7d27c590f33a610d8077ade2b11e97fa9"
PICKLE_CONTRACT = "oracle/phase2/zig-match-pickle-semantics-v1.json"
PICKLE_CONTRACT_SHA256 = "ee975e920ba56968c239953b4414b8da4f85192d9a742d6256bed5f08b8af862"
PICKLE_BRIDGE_SHA256 = "b2866780c627035d596eb4190247446efa46e91235152dac1d92fb333d53e915"
PICKLE_BRIDGE_BYTES = 174024

ADAPTER_SOURCE = "tools/apply_owned_zig_public_adapter_semantics_v1.py"
ADAPTER_SOURCE_SHA256 = "14ffb1f8a8fc611a64ad307e4e5c86c17a635d2dc0b509c1a0c2eb60d3a75782"
ADAPTER_PROTOCOL = "oracle/phase2/ZIG-PUBLIC-ADAPTER-SEMANTICS-V1.md"
ADAPTER_PROTOCOL_SHA256 = "db81ccb98ccc018f8bec21f6e37ed33f3829be92ce435ba0f5198db28e655226"
ADAPTER_CONTRACT = "oracle/phase2/zig-public-adapter-semantics-v1.json"
ADAPTER_CONTRACT_SHA256 = "26a48a86a9d6d99d138d7e4f44bec5e2ba70c9dd36249305d4733fa9370ee765"

SUBSTITUTION_ORACLE = "tools/independent_substitution_buffer_semantics_v2.py"
SUBSTITUTION_ORACLE_SHA256 = "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573"
SUBSTITUTION_ORACLE_BYTES = 317541
SHAPE_ORACLE = "tools/independent_shape_changing_buffer_semantics_v2.py"
SHAPE_ORACLE_SHA256 = "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c"
SHAPE_ORACLE_BYTES = 137527
REFERENCE_PARSER = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/_parser.py"
)
REFERENCE_PARSER_SHA256 = "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4"
REFERENCE_PARSER_BYTES = 40353

RECEIPT = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v13-"
    "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13-"
    "failures-publication-receipt.json"
)
RECEIPT_SHA256 = "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca"

OLD_CAPTURE = (
    "    size_t branch_group = active + 1;\n"
    "    match->spans[branch_group] = begins[0];\n"
    "    match->spans[exposed_stride + branch_group] = ends[0];\n"
    "    match->lastindex = (Py_ssize_t)branch_group;\n"
)
NEW_CAPTURE = (
    "    size_t branch_group = active + 1;\n"
    "    if (match->spans[branch_group] < 0) {\n"
    "        match->spans[branch_group] = begins[0];\n"
    "        match->spans[exposed_stride + branch_group] = ends[0];\n"
    "    }\n"
    "    match->lastindex = (Py_ssize_t)branch_group;\n"
)
OLD_REDUCER = (
    "static PyObject *zig_match_reduce(ZigMatch *match, PyObject *ignored) "
    "{ (void)match; (void)ignored; PyErr_SetString(PyExc_TypeError, "
    "\"cannot pickle 're.Match' object\"); return NULL; }\n"
)
NEW_REDUCER = OLD_REDUCER + (
    "static PyObject *zig_match_reduce_ex(ZigMatch *match, PyObject *protocol) {\n"
    "    Py_ssize_t version = PyLong_AsSsize_t(protocol);\n"
    "    if (version == -1 && PyErr_Occurred()) return NULL;\n"
    "    if (version < 0 || version >= 2) {\n"
    "        return zig_match_reduce(match, NULL);\n"
    "    }\n"
    "    PyObject *registry = PyImport_ImportModule(\"copyreg\");\n"
    "    if (registry == NULL) return NULL;\n"
    "    PyObject *reconstructor = PyObject_GetAttrString(\n"
    "        registry, \"_reconstructor\");\n"
    "    Py_DECREF(registry);\n"
    "    if (reconstructor == NULL) return NULL;\n"
    "    PyObject *arguments = PyTuple_Pack(\n"
    "        3, (PyObject *)Py_TYPE(match),\n"
    "        (PyObject *)&PyBaseObject_Type, Py_None);\n"
    "    if (arguments == NULL) {\n"
    "        Py_DECREF(reconstructor);\n"
    "        return NULL;\n"
    "    }\n"
    "    PyObject *reduction = PyTuple_Pack(2, reconstructor, arguments);\n"
    "    Py_DECREF(reconstructor);\n"
    "    Py_DECREF(arguments);\n"
    "    return reduction;\n"
    "}\n"
)
OLD_REDUCER_METHOD = (
    "    {\"__reduce_ex__\", (PyCFunction)zig_match_reduce, METH_O, "
    "\"Matches cannot be pickled.\"},\n"
)
NEW_REDUCER_METHOD = (
    "    {\"__reduce_ex__\", (PyCFunction)zig_match_reduce_ex, METH_O, "
    "\"Return the Python-compatible protocol-specific match reduction.\"},\n"
)

OLD_EXPAND_ANCHOR = "static PyObject *zig_match_expand(ZigMatch *match, PyObject *value) {\n"
ERROR_HELPER = (
    "static void zig_restore_template_error(PyObject *original) {\n"
    "    if (original == NULL || !PyErr_Occurred() ||\n"
    "        PyBytes_Check(original) || PyUnicode_Check(original) ||\n"
    "        PyByteArray_Check(original) || PyMemoryView_Check(original) ||\n"
    "        !PyObject_CheckBuffer(original)) return;\n"
    "\n"
    "    PyObject *failure = PyErr_GetRaisedException();\n"
    "    if (failure == NULL) return;\n"
    "    PyObject *message = PyObject_GetAttrString(failure, \"msg\");\n"
    "    PyObject *position = message == NULL ? NULL\n"
    "        : PyObject_GetAttrString(failure, \"pos\");\n"
    "    PyObject *pattern = position == NULL ? NULL\n"
    "        : PyObject_GetAttrString(failure, \"pattern\");\n"
    "    if (message == NULL || position == NULL || pattern == NULL ||\n"
    "        !PyUnicode_Check(message) || !PyLong_Check(position)) {\n"
    "        PyErr_Clear();\n"
    "        Py_XDECREF(message);\n"
    "        Py_XDECREF(position);\n"
    "        Py_XDECREF(pattern);\n"
    "        PyErr_SetRaisedException(failure);\n"
    "        return;\n"
    "    }\n"
    "    Py_DECREF(pattern);\n"
    "\n"
    "    if (PyUnicode_CompareWithASCIIString(\n"
    "            message, \"bad escape (end of pattern)\") == 0) {\n"
    "        Py_ssize_t length = PyObject_Size(original);\n"
    "        if (length < 0) {\n"
    "            Py_DECREF(message);\n"
    "            Py_DECREF(position);\n"
    "            Py_DECREF(failure);\n"
    "            return;\n"
    "        }\n"
    "        PyObject *observed = PyLong_FromSsize_t(length - 1);\n"
    "        if (observed == NULL) {\n"
    "            Py_DECREF(message);\n"
    "            Py_DECREF(position);\n"
    "            Py_DECREF(failure);\n"
    "            return;\n"
    "        }\n"
    "        Py_SETREF(position, observed);\n"
    "    }\n"
    "\n"
    "    PyObject *restored = PyObject_CallFunctionObjArgs(\n"
    "        (PyObject *)Py_TYPE(failure), message, original, position, NULL);\n"
    "    Py_DECREF(message);\n"
    "    Py_DECREF(position);\n"
    "    Py_DECREF(failure);\n"
    "    if (restored != NULL) PyErr_SetRaisedException(restored);\n"
    "}\n\n"
)
NEW_EXPAND_ANCHOR = ERROR_HELPER + OLD_EXPAND_ANCHOR

OLD_EXPAND_FAILURE = (
    "        PyObject *result = PyObject_CallMethod(\n"
    "            match->pattern, \"_expand\", \"OO\", raw, (PyObject *)match);\n"
    "        Py_DECREF(templates);\n"
    "        Py_XDECREF(owned);\n"
    "        return result;\n"
)
NEW_EXPAND_FAILURE = (
    "        PyObject *result = PyObject_CallMethod(\n"
    "            match->pattern, \"_expand\", \"OO\", raw, (PyObject *)match);\n"
    "        if (result == NULL) zig_restore_template_error(value);\n"
    "        Py_DECREF(templates);\n"
    "        Py_XDECREF(owned);\n"
    "        return result;\n"
)

OLD_CACHE_FAILURE = (
    "            created = PyObject_CallMethod(\n"
    "                args[0], \"_cache_template\", \"OO\", template, subject\n"
    "            );\n"
    "            if (created == NULL) goto bound_substitute_done;\n"
    "            tokens = created;\n"
)
NEW_CACHE_FAILURE = (
    "            created = PyObject_CallMethod(\n"
    "                args[0], \"_cache_template\", \"OO\", template, subject\n"
    "            );\n"
    "            if (created == NULL) {\n"
    "                zig_restore_template_error(replacement);\n"
    "                goto bound_substitute_done;\n"
    "            }\n"
    "            tokens = created;\n"
)

OLD_GENERIC_EXPORTER = (
    "    if (!text_mode && !PyBytes_Check(subject) &&\n"
    "        !PyByteArray_Check(subject) && !PyMemoryView_Check(subject)) {\n"
    "        PyObject *result = zig_live_exporter_subn(\n"
    "            handle, subject, data, length, kind, groups, replacement, limit,\n"
    "            template_mode);\n"
    "        if (view.obj != NULL) PyBuffer_Release(&view);\n"
    "        return result;\n"
    "    }\n"
)
NEW_GENERIC_EXPORTER = (
    "    if (!text_mode && !PyBytes_Check(subject) &&\n"
    "        !PyByteArray_Check(subject) && !PyMemoryView_Check(subject)) {\n"
    "        if (!template_mode && PyObject_CheckBuffer(replacement) &&\n"
    "            !PyBytes_Check(replacement) &&\n"
    "            !PyByteArray_Check(replacement) &&\n"
    "            !PyMemoryView_Check(replacement)) {\n"
    "            PyObject *snapshot = PyBytes_FromStringAndSize(\n"
    "                (const char *)data, (Py_ssize_t)length);\n"
    "            if (snapshot == NULL) {\n"
    "                PyBuffer_Release(&view);\n"
    "                return NULL;\n"
    "            }\n"
    "            PyBuffer_Release(&view);\n"
    "            PyObject *result = zig_live_exporter_subn(\n"
    "                handle, subject,\n"
    "                (const uint8_t *)PyBytes_AS_STRING(snapshot), length,\n"
    "                kind, groups, replacement, limit, template_mode);\n"
    "            Py_DECREF(snapshot);\n"
    "            return result;\n"
    "        }\n"
    "        PyObject *result = zig_live_exporter_subn(\n"
    "            handle, subject, data, length, kind, groups, replacement, limit,\n"
    "            template_mode);\n"
    "        if (view.obj != NULL) PyBuffer_Release(&view);\n"
    "        return result;\n"
    "    }\n"
)

ZERO_EFFECTS = (
    "candidate_imports", "candidate_processes", "candidate_matching_calls",
    "native_library_loads", "native_builds", "archive_opens", "holdout_opens",
    "benchmark_opens", "seed_opens", "private_root_opens", "files_written",
    "canonical_targets_changed", "subinterpreters_created", "reference_workers",
    "compiler_processes", "clock_samples", "production_stdlib_engine_imports",
)


class FreezeError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def absolute(relative: str) -> str:
    if relative == REFERENCE_PARSER:
        return REFERENCE_PARSER
    require(type(relative) is str and relative and not relative.startswith("/")
            and ".." not in relative.split("/"),
            "reject unowned or traversing Zig replacement input")
    return os.path.join(ROOT, relative)


class SourceWall:
    def __init__(self, owners: set[str]):
        self.owners = {absolute(owner) for owner in owners}
        self.active = False

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if not self.active:
            return
        if event == "open":
            require(len(arguments) == 3 and type(arguments[0]) is str
                    and arguments[0] in self.owners
                    and arguments[1] in (None, "r", "rb")
                    and type(arguments[2]) is int
                    and arguments[2] & os.O_ACCMODE == os.O_RDONLY
                    and arguments[2] & (os.O_CREAT | os.O_APPEND | os.O_TRUNC) == 0,
                    "replacement source wall rejected unowned or mutable open")
            return
        if event == "import":
            name = arguments[0] if arguments else ""
            banned = ("candidates", "re", "_sre", "regex", "ctypes", "inspect")
            require(not any(name == item or name.startswith(item + ".")
                            for item in banned),
                    "replacement source wall rejected matching engine import")
            return
        banned_events = (
            "subprocess.", "socket.", "ctypes.", "_posixsubprocess.",
            "os.mkdir", "os.rmdir", "os.remove", "os.rename", "os.replace",
            "os.unlink", "os.chmod", "os.chown", "os.system", "os.putenv",
            "os.posix_spawn", "os.fork", "os.exec", "threading.",
        )
        require(not event.startswith(banned_events),
                "replacement source wall rejected external action " + event)

    def __enter__(self) -> "SourceWall":
        sys.addaudithook(self.audit)
        self.active = True
        return self

    def __exit__(self, kind: object, value: object, traceback: object) -> None:
        self.active = False


def read_owner(path: str, identity: str | None = None,
               length: int | None = None) -> bytes:
    descriptor = os.open(absolute(path), os.O_RDONLY
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1
                and metadata.st_uid == os.getuid()
                and metadata.st_size <= 1024 * 1024,
                "reject nonowned frozen Zig replacement input " + path)
        if length is not None:
            require(metadata.st_size == length,
                    "reject frozen Zig replacement input length " + path)
        chunks = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    value = b"".join(chunks)
    if identity is not None:
        require(digest(value) == identity,
                "reject frozen Zig replacement input digest " + path)
    return value


def replace_once(value: bytes, old: str, new: str, label: str) -> bytes:
    before = old.encode()
    after = new.encode()
    require(value.count(before) == 1,
            "reject missing or duplicated first-party source block " + label)
    return value.replace(before, after, 1)


def derive(original: bytes) -> tuple[bytes, bytes, bytes]:
    require(len(original) == BRIDGE_BYTES and digest(original) == BRIDGE_SHA256,
            "reject original independently owned Zig binding")
    scanner = replace_once(original, OLD_CAPTURE, NEW_CAPTURE, "scanner capture")
    require(len(scanner) == SCANNER_BRIDGE_BYTES
            and digest(scanner) == SCANNER_BRIDGE_SHA256,
            "reject independently frozen scanner bridge")
    legacy = replace_once(scanner, OLD_REDUCER, NEW_REDUCER,
                          "legacy match serialization")
    legacy = replace_once(legacy, OLD_REDUCER_METHOD, NEW_REDUCER_METHOD,
                          "legacy match method registration")
    require(len(legacy) == PICKLE_BRIDGE_BYTES
            and digest(legacy) == PICKLE_BRIDGE_SHA256,
            "reject independently frozen scanner and pickle bridge")
    corrected = replace_once(legacy, OLD_EXPAND_ANCHOR, NEW_EXPAND_ANCHOR,
                             "owned exporter error restoration")
    corrected = replace_once(corrected, OLD_EXPAND_FAILURE, NEW_EXPAND_FAILURE,
                             "match expansion original template")
    corrected = replace_once(corrected, OLD_CACHE_FAILURE, NEW_CACHE_FAILURE,
                             "pattern replacement original template")
    corrected = replace_once(corrected, OLD_GENERIC_EXPORTER, NEW_GENERIC_EXPORTER,
                             "literal custom-exporter safe lifetime")
    rollback = corrected.replace(NEW_GENERIC_EXPORTER.encode(),
                                 OLD_GENERIC_EXPORTER.encode(), 1)
    rollback = rollback.replace(NEW_CACHE_FAILURE.encode(),
                               OLD_CACHE_FAILURE.encode(), 1)
    rollback = rollback.replace(NEW_EXPAND_FAILURE.encode(),
                               OLD_EXPAND_FAILURE.encode(), 1)
    rollback = rollback.replace(NEW_EXPAND_ANCHOR.encode(),
                               OLD_EXPAND_ANCHOR.encode(), 1)
    require(rollback == legacy,
            "reject unrelated native Zig replacement changes")
    require(corrected.count(b"zig_restore_template_error(") == 3,
            "reject absent, duplicate, or unconnected exporter error restoration")
    require(corrected.count(b"PyObject *snapshot = PyBytes_FromStringAndSize(") == 1,
            "reject duplicate or missing safe exporter snapshot")
    require(corrected.count(NEW_CAPTURE.encode()) == 1
            and corrected.count(NEW_REDUCER_METHOD.encode()) == 1,
            "reject discarded independently frozen scanner or pickle semantics")
    for forbidden in (
        b"PyImport_ImportModule(\"re\")",
        b"PyImport_ImportModule(\"_sre\")",
        b"PyImport_ImportModule(\"regex\")",
        b"PyImport_ImportModule(\"candidates.",
    ):
        require(forbidden not in corrected,
                "reject borrowed Python or candidate regular-expression engine")
    return scanner, legacy, corrected


class SyntheticPatternError(Exception):
    def __init__(self, message: str, pattern: object, position: int):
        self.msg = message
        self.pattern = pattern
        self.pos = position
        pattern.count("\n", 0, position)
        super().__init__(message)


class SyntheticExporter:
    def __init__(self, role: str, payload: bytes,
                 events: list[tuple[str, str, bytes | int]],
                 *, mutate: bool = False):
        self.role = role
        self.backing = bytearray(payload)
        self.events = events
        self.mutate = mutate

    def __buffer__(self, flags: int) -> memoryview:
        self.events.append(("acquire", self.role, bytes(self.backing)))
        return memoryview(self.backing)

    def __release_buffer__(self, view: memoryview) -> None:
        if self.mutate:
            self.backing[:] = b"!" * len(self.backing)
        self.events.append(("release", self.role, bytes(self.backing)))

    def __len__(self) -> int:
        self.events.append(("length-probe", self.role, len(self.backing)))
        return len(self.backing)


class CountableExporter(SyntheticExporter):
    def count(self, value: str, start: int, end: int) -> int:
        return 0


def restore_synthetic(failure: Exception, original: object) -> Exception:
    if not isinstance(failure, SyntheticPatternError) or isinstance(
            original, (bytes, str, bytearray, memoryview)):
        return failure
    position = failure.pos
    if failure.msg == "bad escape (end of pattern)":
        position = len(original) - 1
    try:
        return type(failure)(failure.msg, original, position)
    except Exception as actual:
        return actual


def synthetic_failure(message: str, pattern: object, position: int) -> Exception:
    failure = Exception.__new__(SyntheticPatternError)
    failure.msg = message
    failure.pattern = pattern
    failure.pos = position
    return failure


def self_test(original: bytes, scanner: bytes, legacy: bytes,
              corrected: bytes, parser: bytes) -> int:
    controls = 0
    for mutate in (False, True):
        events: list[tuple[str, str, bytes | int]] = []
        subject = SyntheticExporter("subject", b"alpha", events, mutate=mutate)
        replacement = SyntheticExporter("replacement", b"X", events)
        view = memoryview(subject)
        snapshot = bytes(view)
        view.release()
        replacement_view = memoryview(replacement)
        replacement_view.release()
        require(snapshot == b"alpha"
                and [event[:2] for event in events] == [
                    ("acquire", "subject"), ("release", "subject"),
                    ("acquire", "replacement"), ("release", "replacement"),
                ], "reject safe snapshot or exact subject-before-template lifetime")
        controls += 1
        require(bytes(subject.backing) == (b"!!!!!" if mutate else b"alpha"),
                "reject observable custom-exporter release mutation")
        controls += 1

    for message, dangling in (
            ("bad escape (end of pattern)", True),
            ("bad escape \\q", False),
            ("missing <", False),
            ("invalid group reference 9", False)):
        events = []
        exporter = SyntheticExporter("template", b"\\", events)
        failure = synthetic_failure(message, b"\\", 1)
        actual = restore_synthetic(failure, exporter)
        require(isinstance(actual, AttributeError)
                and str(actual) == "'SyntheticExporter' object has no attribute 'count'",
                "reject original exporter PatternError construction")
        require(events == ([
            ("length-probe", "template", 1)
        ] if dangling else []), "reject exact dangling-escape length-probe order")
        controls += 2

    counted_events: list[tuple[str, str, bytes | int]] = []
    counted = CountableExporter("template", b"xxx", counted_events)
    counted_error = restore_synthetic(
        synthetic_failure("bad escape (end of pattern)", b"x\\", 1), counted)
    require(isinstance(counted_error, SyntheticPatternError)
            and counted_error.pattern is counted and counted_error.pos == 2
            and counted_events == [("length-probe", "template", 3)],
            "reject a lawful exporter with working count and original position")
    controls += 1

    other = IndexError("unknown group name 'missing'")
    require(restore_synthetic(other, counted) is other,
            "reject rewritten unrelated missing-group exception")
    controls += 1
    for plain in (b"bad", "bad", bytearray(b"bad"), memoryview(b"bad")):
        error = synthetic_failure("missing <", b"bad", 0)
        require(restore_synthetic(error, plain) is error,
                "reject changed built-in replacement carrier")
        controls += 1

    for altered in (
        original + b"\n",
        original.replace(OLD_CAPTURE.encode(), b"", 1),
        original.replace(OLD_REDUCER.encode(), b"", 1),
        original.replace(OLD_EXPAND_ANCHOR.encode(), b"", 1),
        original.replace(OLD_EXPAND_FAILURE.encode(), b"", 1),
        original.replace(OLD_CACHE_FAILURE.encode(), b"", 1),
        original.replace(OLD_GENERIC_EXPORTER.encode(), b"", 1),
    ):
        try:
            derive(altered)
        except FreezeError:
            controls += 1
        else:
            raise FreezeError("accepted poisoned first-party replacement binding")

    require(b"class Tokenizer:" in parser
            and b"self.string = string" in parser
            and b"self.string, len(self.string) - 1" in parser
            and b"return error(msg, self.string," in parser,
            "reject pinned reference-only original replacement provenance")
    controls += 1
    require(corrected.count(b"#include") == legacy.count(b"#include")
            and corrected.count(b"extern ") == legacy.count(b"extern "),
            "reject imported package, foreign engine, or delegated regex entry")
    controls += 1
    require(scanner.count(NEW_CAPTURE.encode()) == 1
            and legacy.count(NEW_CAPTURE.encode()) == 1
            and corrected.count(NEW_CAPTURE.encode()) == 1,
            "reject independently frozen scanner composition")
    controls += 1
    require(legacy.count(NEW_REDUCER_METHOD.encode()) == 1
            and corrected.count(NEW_REDUCER_METHOD.encode()) == 1,
            "reject independently frozen protocol-specific pickle composition")
    controls += 1
    require(NEW_GENERIC_EXPORTER.count("!template_mode") == 1
            and "PyObject_CheckBuffer(replacement)" in NEW_GENERIC_EXPORTER
            and "PyBuffer_Release(&view);\n            PyObject *result" in
                NEW_GENERIC_EXPORTER,
            "reject unsafe broadening to escaped or native replacement paths")
    controls += 1
    require(OLD_GENERIC_EXPORTER.encode() not in corrected
            and corrected.count(NEW_GENERIC_EXPORTER.encode()) == 1,
            "reject stale custom-exporter lifetime")
    controls += 1
    return controls


def verify_history(receipt: bytes, scanner_contract: bytes,
                   adapter_contract: bytes, pickle_contract: bytes) -> None:
    observed = json.loads(receipt)
    require(observed.get("candidate_status") == "FAIL"
            and observed.get("case_execution_denominator") == 31237
            and observed.get("actual_candidate_workers") == 13
            and observed.get("verified_passing_case_count") == 4607
            and observed.get("observed_semantic_mismatch_lower_bound") == 1700
            and observed.get("semantic_mismatch_count") == "NOT MEASURED",
            "reject measured original independent Zig campaign")
    rows = observed.get("original_suite_diagnostics")
    require(isinstance(rows, list) and len(rows) == 13,
            "reject original Zig complete suite denominator")
    for name, denominator, mismatches in (
            ("substitution_v2", 5120, 64),
            ("shape_v2", 10240, 672)):
        row = next((item for item in rows if item.get("suite") == name), None)
        require(row is not None
                and row.get("case_execution_denominator") == denominator
                and row.get("observed_semantic_mismatch_count") == mismatches,
                "reject actual original Zig replacement failures " + name)
    scanner = json.loads(scanner_contract)
    require(scanner.get("source_modeled_scanner_corrections") == 620
            and scanner.get("prospective_variant", {}).get("sha256")
                   == SCANNER_BRIDGE_SHA256,
            "reject independently frozen Zig scanner source")
    adapter = json.loads(adapter_contract)
    require(adapter.get("source_modeled_corrected_case_count") == 312,
            "reject independently frozen Zig public-adapter source")
    legacy = json.loads(pickle_contract)
    require(legacy.get("source_modeled_combined_public_adapter_corrections") == 964
            and legacy.get("source_modeled_combined_remaining_measured_failures") == 736
            and legacy.get("prospective_variant", {}).get("sha256")
                   == PICKLE_BRIDGE_SHA256,
            "reject independently frozen composed match-pickle source")


def owners(options: argparse.Namespace) -> set[str]:
    result = {
        SELF, PROTOCOL, BRIDGE, ENGINE, RECEIPT, REFERENCE_PARSER,
        SUBSTITUTION_ORACLE, SHAPE_ORACLE,
        SCANNER_SOURCE, SCANNER_PROTOCOL, SCANNER_CONTRACT,
        PICKLE_SOURCE, PICKLE_PROTOCOL, PICKLE_CONTRACT,
        ADAPTER_SOURCE, ADAPTER_PROTOCOL, ADAPTER_CONTRACT,
    }
    if options.contract_sha256:
        result.add(CONTRACT)
    return result


def build(options: argparse.Namespace, *, run_self_test: bool) -> dict[str, object]:
    with SourceWall(owners(options)):
        source = read_owner(SELF, options.source_sha256, options.source_bytes)
        protocol = read_owner(PROTOCOL, options.protocol_sha256)
        original = read_owner(BRIDGE, options.bridge_sha256, options.bridge_bytes)
        engine = read_owner(ENGINE, options.engine_sha256, options.engine_bytes)
        receipt = read_owner(RECEIPT, options.receipt_sha256)
        parser = read_owner(REFERENCE_PARSER, options.reference_parser_sha256,
                            options.reference_parser_bytes)
        substitution = read_owner(SUBSTITUTION_ORACLE,
                                  options.substitution_oracle_sha256,
                                  options.substitution_oracle_bytes)
        shape = read_owner(SHAPE_ORACLE, options.shape_oracle_sha256,
                           options.shape_oracle_bytes)
        scanner_source = read_owner(SCANNER_SOURCE, options.scanner_source_sha256)
        scanner_protocol = read_owner(SCANNER_PROTOCOL,
                                      options.scanner_protocol_sha256)
        scanner_contract = read_owner(SCANNER_CONTRACT,
                                      options.scanner_contract_sha256)
        pickle_source = read_owner(PICKLE_SOURCE, options.pickle_source_sha256)
        pickle_protocol = read_owner(PICKLE_PROTOCOL,
                                     options.pickle_protocol_sha256)
        pickle_contract = read_owner(PICKLE_CONTRACT,
                                     options.pickle_contract_sha256)
        adapter_source = read_owner(ADAPTER_SOURCE, options.adapter_source_sha256)
        adapter_protocol = read_owner(ADAPTER_PROTOCOL,
                                      options.adapter_protocol_sha256)
        adapter_contract = read_owner(ADAPTER_CONTRACT,
                                      options.adapter_contract_sha256)
        verify_history(receipt, scanner_contract, adapter_contract, pickle_contract)
        scanner, legacy, corrected = derive(original)
        if options.variant_sha256 is not None:
            require(digest(corrected) == options.variant_sha256,
                    "reject pinned composed Zig replacement binding")
        if options.variant_bytes is not None:
            require(len(corrected) == options.variant_bytes,
                    "reject pinned composed Zig replacement binding size")
        require(not os.path.lexists(absolute(TARGET)),
                "reject materialized Zig replacement-event correction")
        controls = self_test(original, scanner, legacy, corrected, parser)
        result = {
            "schema": "rebar-owned-zig-replacement-event-semantics-v1-source-freeze",
            "status": "SOURCE FROZEN; NATIVE BUILD AND CANDIDATE NOT RUN",
            "family": "zig",
            "source": {"path": SELF, "sha256": digest(source), "bytes": len(source)},
            "protocol": {"path": PROTOCOL, "sha256": digest(protocol),
                         "bytes": len(protocol)},
            "original_bridge": {"path": BRIDGE, "sha256": digest(original),
                                "bytes": len(original)},
            "independent_zig_engine": {"path": ENGINE, "sha256": digest(engine),
                                       "bytes": len(engine)},
            "independently_derived_scanner_bridge": {
                "sha256": digest(scanner), "bytes": len(scanner),
                "physical_target_opened": False,
                "source_modeled_scanner_corrections": 620,
            },
            "independently_derived_match_pickle_bridge": {
                "sha256": digest(legacy), "bytes": len(legacy),
                "physical_target_opened": False,
                "source_modeled_scanner_and_pickle_corrections": 652,
            },
            "prospective_variant": {"path": TARGET, "sha256": digest(corrected),
                                    "bytes": len(corrected),
                                    "physical_status": "NOT MATERIALIZED"},
            "replacement_event_corrections": {
                "observed_substitution_exporter_order_failures": 64,
                "observed_shape_exporter_order_failures": 112,
                "observed_original_template_attribute_failures": 560,
                "observed_dangling_escape_length_probe_failures": 88,
                "shape_total_observed_failures": 672,
                "replacement_total_observed_failures": 736,
                "snapshot_copied_before_release": True,
                "subject_released_before_replacement_join": True,
                "snapshot_owned_for_entire_independent_match": True,
                "narrow_literal_custom_exporter_guard": True,
                "escaped_template_paths_unchanged": True,
                "match_expand_preserves_original_template": True,
                "pattern_sub_preserves_original_template": True,
                "original_exporter_length_probe_preserved": True,
                "ordinary_attribute_error_is_not_forged": True,
                "other_error_types_preserved": True,
            },
            "original_oracle": {
                "case_execution_denominator": 31237,
                "suite_count": 13,
                "historical_verified_passing_cases": 4607,
                "historical_measured_mismatches": 1700,
                "historical_complete_mismatch_count": "NOT MEASURED",
                "unfinished_subinterpreter_cases": 128,
                "substitution_suite_case_execution_denominator": 5120,
                "shape_suite_case_execution_denominator": 10240,
            },
            "source_modeled_combined_public_adapter_corrections": 1700,
            "source_modeled_combined_remaining_measured_failures": 0,
            "complete_candidate_mismatches": "NOT MEASURED",
            "modeled_results_are_actual_runs": False,
            "candidate_correctness": "NOT RUN",
            "candidate_qualified": False,
            "native_engine_changed": False,
            "native_bridge_built": False,
            "cross_candidate_engine_used": False,
            "stdlib_regex_engine_used": False,
            "external_regex_package_used": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "source_only_effects": {name: 0 for name in ZERO_EFFECTS},
            "source_only_self_test_control_count": controls,
            "frozen_authority": {
                "v13_failure_receipt": digest(receipt),
                "substitution_oracle_source": digest(substitution),
                "shape_oracle_source": digest(shape),
                "official_cpython_reference_parser": digest(parser),
                "reference_parser_used_in_production": False,
                "scanner_source": digest(scanner_source),
                "scanner_protocol": digest(scanner_protocol),
                "scanner_contract": digest(scanner_contract),
                "match_pickle_source": digest(pickle_source),
                "match_pickle_protocol": digest(pickle_protocol),
                "match_pickle_contract": digest(pickle_contract),
                "public_adapter_source": digest(adapter_source),
                "public_adapter_protocol": digest(adapter_protocol),
                "public_adapter_contract": digest(adapter_contract),
            },
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        if options.contract_sha256:
            require(read_owner(CONTRACT, options.contract_sha256) == canonical(result),
                    "reject complete Zig replacement-event contract")
        if run_self_test:
            require(self_test(original, scanner, legacy, corrected, parser) == controls,
                    "reject unstable owned replacement-event synthetic controls")
    result["_candidate_bytes"] = corrected
    return result


def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", type=int, required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--bridge-sha256", required=True)
    parser.add_argument("--bridge-bytes", type=int, required=True)
    parser.add_argument("--engine-sha256", required=True)
    parser.add_argument("--engine-bytes", type=int, required=True)
    parser.add_argument("--receipt-sha256", required=True)
    parser.add_argument("--reference-parser-sha256", required=True)
    parser.add_argument("--reference-parser-bytes", type=int, required=True)
    parser.add_argument("--substitution-oracle-sha256", required=True)
    parser.add_argument("--substitution-oracle-bytes", type=int, required=True)
    parser.add_argument("--shape-oracle-sha256", required=True)
    parser.add_argument("--shape-oracle-bytes", type=int, required=True)
    parser.add_argument("--scanner-source-sha256", required=True)
    parser.add_argument("--scanner-protocol-sha256", required=True)
    parser.add_argument("--scanner-contract-sha256", required=True)
    parser.add_argument("--pickle-source-sha256", required=True)
    parser.add_argument("--pickle-protocol-sha256", required=True)
    parser.add_argument("--pickle-contract-sha256", required=True)
    parser.add_argument("--adapter-source-sha256", required=True)
    parser.add_argument("--adapter-protocol-sha256", required=True)
    parser.add_argument("--adapter-contract-sha256", required=True)
    parser.add_argument("--variant-sha256")
    parser.add_argument("--variant-bytes", type=int)
    options = parser.parse_args()
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == absolute(SELF),
            "use pinned isolated bytecode-disabled CPython 3.14.6 only")
    require(options.bridge_sha256 == BRIDGE_SHA256
            and options.bridge_bytes == BRIDGE_BYTES
            and options.engine_sha256 == ENGINE_SHA256
            and options.engine_bytes == ENGINE_BYTES
            and options.receipt_sha256 == RECEIPT_SHA256
            and options.reference_parser_sha256 == REFERENCE_PARSER_SHA256
            and options.reference_parser_bytes == REFERENCE_PARSER_BYTES
            and options.substitution_oracle_sha256 == SUBSTITUTION_ORACLE_SHA256
            and options.substitution_oracle_bytes == SUBSTITUTION_ORACLE_BYTES
            and options.shape_oracle_sha256 == SHAPE_ORACLE_SHA256
            and options.shape_oracle_bytes == SHAPE_ORACLE_BYTES
            and options.scanner_source_sha256 == SCANNER_SOURCE_SHA256
            and options.scanner_protocol_sha256 == SCANNER_PROTOCOL_SHA256
            and options.scanner_contract_sha256 == SCANNER_CONTRACT_SHA256
            and options.pickle_source_sha256 == PICKLE_SOURCE_SHA256
            and options.pickle_protocol_sha256 == PICKLE_PROTOCOL_SHA256
            and options.pickle_contract_sha256 == PICKLE_CONTRACT_SHA256
            and options.adapter_source_sha256 == ADAPTER_SOURCE_SHA256
            and options.adapter_protocol_sha256 == ADAPTER_PROTOCOL_SHA256
            and options.adapter_contract_sha256 == ADAPTER_CONTRACT_SHA256,
            "reject incomplete independently frozen replacement-event authority")
    if not options.render_contract:
        require(options.contract_sha256 is not None
                and options.variant_sha256 is not None
                and options.variant_bytes is not None,
                "reject incomplete composed Zig replacement-event pins")
    return options


def publish(options: argparse.Namespace, corrected: bytes) -> dict[str, object]:
    require(options.apply, "reject unrequested Zig replacement source publication")
    destination = absolute(TARGET)
    directory = os.path.dirname(destination)
    parent = os.path.dirname(directory)
    parent_owner = os.lstat(parent)
    require(stat.S_ISDIR(parent_owner.st_mode)
            and not stat.S_ISLNK(parent_owner.st_mode)
            and not os.path.lexists(directory)
            and not os.path.lexists(destination),
            "reject foreign or existing Zig replacement-event destination")
    os.mkdir(directory, 0o700)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        offset = 0
        while offset < len(corrected):
            count = os.write(descriptor, corrected[offset:])
            require(count > 0, "reject interrupted native-source publication")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    owner = os.open(directory, os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_CLOEXEC", 0))
    try:
        os.fsync(owner)
    finally:
        os.close(owner)
    require(read_owner(TARGET, options.variant_sha256, options.variant_bytes)
            == corrected, "reject changed materialized Zig replacement binding")
    return {
        "schema": "rebar-owned-zig-replacement-event-semantics-v1-application",
        "status": "PASS; NATIVE SOURCE MATERIALIZED ONLY",
        "family": "zig",
        "target": TARGET,
        "source_sha256": digest(corrected),
        "source_bytes": len(corrected),
        "original_case_execution_denominator": 31237,
        "historical_measured_mismatches": 1700,
        "source_modeled_combined_remaining_measured_failures": 0,
        "complete_candidate_mismatches": "NOT MEASURED",
        "native_build": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def main() -> int:
    try:
        options = parse()
        contract = build(options, run_self_test=options.self_test)
        candidate = contract.pop("_candidate_bytes")
        if options.apply:
            result = publish(options, candidate)
        elif options.render_contract:
            result = contract
        else:
            result = {
                "status": "PASS",
                "mode": "self-test" if options.self_test else "verify-frozen-context",
                "source_sha256": options.source_sha256,
                "contract_sha256": options.contract_sha256,
                "prospective_variant_sha256": digest(candidate),
                "prospective_variant_bytes": len(candidate),
                "synthetic_control_count": contract["source_only_self_test_control_count"],
                "source_only_effects": {key: 0 for key in ZERO_EFFECTS},
                "native_build": "NOT RUN",
                "candidate_matching": "NOT RUN",
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
            }
        print(canonical(result).decode(), end="")
        return 0
    except (FreezeError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("first-party Zig replacement-event correction rejected: "
              + type(error).__name__ + ": " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
