#!/usr/bin/env python3
"""Freeze one first-party C subject-buffer ownership source without running it."""

from __future__ import annotations

import _imp
import _io
import _thread
import argparse
import builtins
import hashlib
import importlib
import io
import json
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
from typing import Any

ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
PYTHON_BYTES = 32_387_816
SCHEMA = "rebar-phase2-owned-c-subject-buffer-ownership-v1"
SELF = "tools/apply_owned_c_subject_buffer_ownership_v1.py"
PROTOCOL = "oracle/phase2/C-SUBJECT-BUFFER-OWNERSHIP-V1.md"
CONTRACT = "oracle/phase2/c-subject-buffer-ownership-v1.json"
VARIANT = "candidates/c/variants/subject_buffer_ownership_v1/vm_native.c"
MAX_OWNER_BYTES = 4 * 1024 * 1024
Owner = tuple[str, str, int]

GOAL: Owner = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3_756,
)
P0_READINESS: dict[str, Owner] = {
    "source": (
        "tools/verify_owned_p0_completeness_v4.py",
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        29_094,
    ),
    "protocol": (
        "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4_261,
    ),
    "contract": (
        "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34_875,
    ),
}
PHASE_ONE: Owner = P0_READINESS["contract"]

ORIGINAL_C: Owner = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218_185,
)
ORIGINAL_ADAPTER: Owner = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60_707,
)
FIRST_REPAIR: Owner = (
    "tools/apply_owned_first_party_source_repair_v1.py",
    "c04bbc8e7bc45bdbe1fb9eb93942286f5b32b39aef554db15b8b1acd9cc8cd99",
    45_783,
)
PICKLE_REPAIR: Owner = (
    "tools/apply_owned_first_party_source_repair_v2.py",
    "1bb4f21cca20928b1c8993b3646825ac04ad46a231633105e5cb2469fd8434c0",
    65_872,
)
PRODUCER: dict[str, Owner] = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v4.py",
        "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
        230_782,
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md",
        "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5",
        5_981,
    ),
    "contract": (
        "oracle/phase2/six-family-p0-producer-v4.json",
        "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5",
        30_867,
    ),
}
C_RUNNER: dict[str, Owner] = {
    "worker": (
        "tools/run_frozen_p0_candidate_worker_v8.py",
        "78634bbcb5f55c560ea4b38c81ca395f4d4d5385c285bd0a3c25b395e3dd5ee1",
        95_361,
    ),
    "runner": (
        "tools/run_frozen_p0_candidate_v10.py",
        "c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a",
        91_132,
    ),
    "protocol": (
        "oracle/phase2/P0-CANDIDATE-PROTOCOL-V10.md",
        "2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae",
        6_792,
    ),
    "contract": (
        "oracle/phase2/p0-candidate-protocol-v10.json",
        "8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737",
        21_238,
    ),
}
V64: dict[str, Owner] = {
    "source": (
        "tools/render_candidate_current_overview_v64.py",
        "6e8364972fe69c4e6074df14ce69369d962773de64bedf576515744cf44e488f",
        120_686,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v64.inputs.json",
        "6566c57fe58b501b54b056aae528d1e1087bec279718e5d175d99baca703cd76",
        1_004_674,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v64.json",
        "feaf43cb6eeeb0d61f60ede20925d559cdafb66d8110f9607192dac542f51ae0",
        2_775_659,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v64.svg",
        "1106fa228c5cf9ed3df94be344c58acf8513ac3be4b01b9c1a0bf058f76bb95f",
        14_807,
    ),
}

C_FAILURE_RECEIPT: Owner = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-"
    "original-p0-failures-publication-receipt.json",
    "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9",
    3_482,
)
C15_BUILD_RECEIPT: Owner = (
    "oracle/phase2/evidence/"
    "native-source-build-v15-c-phase2-v15-c-pickle-original-p0-"
    "publication-receipt.json",
    "ad196290f8f08b1547ffefc02bd1cdaff52557f792b8a32ea93c67f6ee857643",
    4_052,
)
RUST_V7_RECEIPT: Owner = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v7-rust-phase2-v13-rust-"
    "pattern-repr-original-p0-failures-publication-receipt.json",
    "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943",
    8_450,
)
RUST_V10_RECEIPT: Owner = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-"
    "original-p0-v10-failures-publication-receipt.json",
    "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2",
    6_708,
)
HISTORICAL_V48_LOG: Owner = (
    "docs/EXPERIMENT-LOG.md",
    "bfec908f1689bf940e479688e51b209b6182eed29f50996792507fb2668362db",
    1_206_058,
)
FIRST_DERIVED_SHA256 = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
FIRST_DERIVED_BYTES = 218_308
C15_SOURCE_SHA256 = "8b35fba5b565ae18c5b9c180bec1dfbfb46b75bf3db7421626da4a73cdda2b94"
C15_SOURCE_BYTES = 219_227
VARIANT_SHA256 = "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962"
VARIANT_BYTES = 222_212
SUITES: tuple[tuple[str, int], ...] = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1_024),
    ("buffer_v3", 768),
    ("managed_v1", 1_024),
    ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912),
    ("substitution_v2", 5_120),
    ("shape_v2", 10_240),
    ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)

class RepairError(Exception):
    """Reject changed provenance, unsafe source, or a real source-phase effect."""

def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise RepairError(message)

def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete and exact source bytes")
    return hashlib.sha256(raw).hexdigest()

def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require one complete lower-case SHA-256: " + label,
    )
    return value

def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("ascii")
            + b"\n"
        )
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError) as error:
        raise RepairError("reject noncanonical C buffer source evidence") from error

def strict_document(raw: bytes, label: str) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            require(type(key) is str and key not in result, "reject repeated JSON: " + label)
            result[key] = value
        return result
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique,
            parse_constant=lambda item: (_ for _ in ()).throw(
                RepairError("reject nonfinite JSON: " + item)
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise RepairError("reject incomplete JSON: " + label) from error
    require(type(value) is dict and canonical(value) == raw, "reject noncanonical " + label)
    return value

def owner_pin(owner: Owner) -> dict[str, Any]:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}

def owner_group(group: dict[str, Owner]) -> dict[str, Any]:
    return {role: owner_pin(owner) for role, owner in sorted(group.items())}

def checked_parts(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and 0 < len(relative) <= 512, "reject an invalid owner path")
    path = PurePosixPath(relative)
    require(
        not path.is_absolute()
        and str(path) == relative
        and 0 < len(path.parts) <= 16
        and all(part not in ("", ".", "..") for part in path.parts),
        "reject an escaped, absolute or noncanonical owner",
    )
    lowered = relative.lower()
    require(
        ".gz" not in lowered
        and not lowered.endswith(".so")
        and "holdout" not in lowered
        and "benchmark" not in lowered
        and "/phase3/" not in lowered
        and "/performance/" not in lowered,
        "never open an archive, native, holdout or benchmark owner",
    )
    return path.parts

def read_owner(owner: Owner) -> bytes:
    relative, fingerprint, expected_size = owner
    parts = checked_parts(relative)
    checked_digest(fingerprint, relative)
    require(
        type(expected_size) is int and 0 < expected_size <= MAX_OWNER_BYTES,
        "reject an unbounded immutable source owner",
    )
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            require(
                stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and before.st_size == expected_size,
                "reject a linked, foreign or substituted owner: " + relative,
            )
            blocks: list[bytes] = []
            consumed = 0
            while consumed < expected_size:
                block = os.read(descriptor, min(1_048_576, expected_size - consumed))
                require(bool(block), "reject a truncated owner: " + relative)
                consumed += len(block)
                blocks.append(block)
            require(os.read(descriptor, 1) == b"", "reject extra owner bytes: " + relative)
            after = os.fstat(descriptor)
            require(
                (
                    before.st_dev, before.st_ino, before.st_size,
                    before.st_mtime_ns, before.st_ctime_ns,
                )
                == (
                    after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns,
                ),
                "reject an owner modified while being authenticated",
            )
            raw = b"".join(blocks)
            require(
                len(raw) == expected_size and sha256(raw) == fingerprint,
                "reject an incorrect owner hash: " + relative,
            )
            return raw
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)

def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON,
        "use only pinned, isolated, bytecode-free CPython 3.14.6",
    )
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptor = os.open(PYTHON, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and before.st_size == PYTHON_BYTES,
            "reject the wrong stable CPython baseline executable",
        )
        digest = hashlib.sha256()
        consumed = 0
        while consumed < PYTHON_BYTES:
            block = os.read(descriptor, min(1_048_576, PYTHON_BYTES - consumed))
            require(bool(block), "reject truncated stable CPython")
            consumed += len(block)
            digest.update(block)
        require(os.read(descriptor, 1) == b"", "reject oversized stable CPython")
        after = os.fstat(descriptor)
        require(
            consumed == PYTHON_BYTES
            and digest.hexdigest() == PYTHON_SHA256
            and (
                before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
            )
            == (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
            ),
            "authenticate every byte of the pinned CPython baseline",
        )
    finally:
        os.close(descriptor)

FIRST_OLD = b"""    Subject subject;
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
FIRST_NEW = b"""    Subject subject={0};
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
PICKLE_OLD = (
    b"static PyObject *match_reduce(MatchObject *match, PyObject *ignored) "
    b"{ (void)match; (void)ignored; PyErr_SetString(PyExc_TypeError,"
    b"\"cannot pickle 're.Match' object\"); return NULL; }"
)
PICKLE_NEW = b"""static PyObject *match_reduce(MatchObject *match, PyObject *ignored) {
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
}"""
METHOD_OLD = (
    b"    {\"__reduce_ex__\",(PyCFunction)match_reduce,METH_O,"
    b"\"Matches cannot be pickled.\"},\n"
)
METHOD_NEW = (
    b"    {\"__reduce_ex__\",(PyCFunction)match_reduce_ex,METH_O,"
    b"\"Matches cannot be pickled.\"},\n"
)

MATCH_EXPAND_START = (
    b"static PyObject *match_expand(MatchObject *match, PyObject *template) {\n"
)
BUFFER_COPY_START = (
    b"static PyObject *substitution_buffer_copy(PyObject *replacement) {\n"
)
TEMPLATE_START = (
    b"static PyObject *substitution_template(PatternObject *pattern,\n"
)
MATCH_COPY_START = b"static PyObject *match_copy(MatchObject *match,"
SUBSTITUTE_START = b"static PyObject *pattern_substitute(PatternObject *pattern,"
SUBSTITUTE_END = b"static PyObject *pattern_sub(PatternObject *pattern,"

ORIGINAL_TEMPLATE_ERROR_HELPER = b"""static PyObject *substitution_original_template_error(PyObject *replacement) {
    PyObject *raised=PyErr_GetRaisedException();
    if (!raised) {
        PyErr_SetString(PyExc_RuntimeError,
                        "owned replacement compiler lost its exception");
        return NULL;
    }
    PyObject *message=PyObject_GetAttrString(raised,"msg");
    if (!message) {
        PyErr_Clear();
        PyErr_SetRaisedException(raised);
        return NULL;
    }
    PyObject *position=PyObject_GetAttrString(raised,"pos");
    if (!position) {
        PyErr_Clear();
        Py_DECREF(message);
        PyErr_SetRaisedException(raised);
        return NULL;
    }
    if (position==Py_None || !PyUnicode_Check(message)) {
        Py_DECREF(position);
        Py_DECREF(message);
        PyErr_SetRaisedException(raised);
        return NULL;
    }
    if (PyUnicode_CompareWithASCIIString(
            message,"bad escape (end of pattern)")==0) {
        Py_ssize_t original_length=PyObject_Length(replacement);
        if (original_length<0) {
            Py_DECREF(position);
            Py_DECREF(message);
            Py_DECREF(raised);
            return NULL;
        }
        PyObject *original_position=PyLong_FromSsize_t(original_length-1);
        if (!original_position) {
            Py_DECREF(position);
            Py_DECREF(message);
            Py_DECREF(raised);
            return NULL;
        }
        Py_SETREF(position,original_position);
    }
    PyObject *rebuilt=PyObject_CallFunctionObjArgs(
        (PyObject *)Py_TYPE(raised),message,replacement,position,NULL);
    Py_DECREF(position);
    Py_DECREF(message);
    Py_DECREF(raised);
    if (rebuilt) PyErr_SetRaisedException(rebuilt);
    return NULL;
}

"""
MATCH_TEMPLATE_CALL_OLD = b"""        parts=PyObject_CallFunctionObjArgs(state->template_compiler,template_key,(PyObject *)match->pattern,byte_value,NULL);
        if (!parts) { Py_XDECREF(owned_key); return NULL; }
"""
MATCH_TEMPLATE_CALL_NEW = b"""        parts=PyObject_CallFunctionObjArgs(state->template_compiler,template_key,(PyObject *)match->pattern,byte_value,NULL);
        if (!parts) {
            Py_XDECREF(owned_key);
            if (buffer_template && !PyBytes_Check(template))
                return substitution_original_template_error(template);
            return NULL;
        }
"""
BUFFER_COPY_OLD = b"""static PyObject *substitution_buffer_copy(PyObject *replacement) {
    Py_buffer view;
    if (PyObject_GetBuffer(replacement,&view,PyBUF_SIMPLE)<0) {
        if (!PyMemoryView_Check(replacement)) return NULL;
        PyErr_Clear();
        return PyBytes_FromObject(replacement);
    }
    PyObject *result=PyBytes_FromStringAndSize(
        (const char *)view.buf,view.len);
    PyBuffer_Release(&view);
    return result;
}
"""
BUFFER_COPY_NEW = b"""static PyObject *substitution_buffer_copy_flags(PyObject *replacement,
                                                  int flags) {
    Py_buffer view;
    if (PyObject_GetBuffer(replacement,&view,flags)<0) {
        if (!PyMemoryView_Check(replacement)) return NULL;
        PyErr_Clear();
        return PyBytes_FromObject(replacement);
    }
    PyObject *result=PyBytes_FromStringAndSize(NULL,view.len);
    if (result && view.len &&
        PyBuffer_ToContiguous(PyBytes_AS_STRING(result),
                              &view,view.len,'C')<0) {
        Py_DECREF(result);
        result=NULL;
    }
    PyBuffer_Release(&view);
    return result;
}

static PyObject *substitution_buffer_copy(PyObject *replacement) {
    return substitution_buffer_copy_flags(replacement,PyBUF_SIMPLE);
}
"""
TEMPLATE_HASH_OLD = b"""    int has_observable_hash=
        (PyUnicode_Check(replacement) &&
         !PyUnicode_CheckExact(replacement)) ||
        (PyBytes_Check(replacement) && !PyBytes_CheckExact(replacement)) ||
        PyMemoryView_Check(replacement);
"""
TEMPLATE_HASH_NEW = b"""    int has_observable_hash=
        (PyUnicode_Check(replacement) &&
         !PyUnicode_CheckExact(replacement)) ||
        (PyBytes_Check(replacement) && !PyBytes_CheckExact(replacement)) ||
        PyMemoryView_Check(replacement) || is_buffer;
"""
TEMPLATE_KEY_OLD = b"""    if (is_buffer) {
        owned_key=substitution_buffer_copy(replacement);
"""
TEMPLATE_KEY_NEW = b"""    if (is_buffer) {
        owned_key=substitution_buffer_copy_flags(
            replacement,hash_unusable ? PyBUF_FULL_RO : PyBUF_SIMPLE);
"""
TEMPLATE_CALL_OLD = b"""    PyObject *parts=PyObject_CallFunctionObjArgs(
        state->template_compiler,key,(PyObject *)pattern,flag,NULL);
    if (!parts) {
        Py_XDECREF(owned_key);
        return NULL;
    }
"""
TEMPLATE_CALL_NEW = b"""    PyObject *parts=PyObject_CallFunctionObjArgs(
        state->template_compiler,key,(PyObject *)pattern,flag,NULL);
    if (!parts) {
        Py_XDECREF(owned_key);
        if (is_buffer)
            return substitution_original_template_error(replacement);
        return NULL;
    }
"""
SUBSTITUTE_LOCALS_OLD = b"""    PyObject *result=NULL;
    PyObject *template_parts=NULL;
    int template_byte_mode=0,literal_replacement=0;
"""
SUBSTITUTE_LOCALS_NEW = b"""    PyObject *result=NULL;
    PyObject *template_parts=NULL;
    PyObject *subject_snapshot=NULL;
    int template_byte_mode=0,literal_replacement=0;
"""
SUBSTITUTE_CALLABLE_OLD = b"""    if (callable) {
        result=substitute_callable(pattern,&subject,replacement,limit,
                                  return_count);
        goto done;
    }
"""
SUBSTITUTE_CALLABLE_NEW = b"""    if (callable) {
        result=substitute_callable(pattern,&subject,replacement,limit,
                                  return_count);
        goto done;
    }
    if (subject.has_view) {
        subject_snapshot=PyBytes_FromStringAndSize(
            NULL,subject.view.len);
        if (!subject_snapshot) goto done;
        if (subject.view.len &&
            PyBuffer_ToContiguous(PyBytes_AS_STRING(subject_snapshot),
                                  &subject.view,subject.view.len,'C')<0) {
            goto done;
        }
        subject_clear(&subject);
        if (!subject_init(&subject,subject_snapshot)) goto done;
    }
"""
SUBSTITUTE_DONE_OLD = b"""done:
    Py_XDECREF(template_parts);
    subject_clear(&subject);
    return result;
}
"""
SUBSTITUTE_DONE_NEW = b"""done:
    Py_XDECREF(template_parts);
    subject_clear(&subject);
    Py_XDECREF(subject_snapshot);
    return result;
}
"""
MATCH_PAIRS = ((MATCH_TEMPLATE_CALL_OLD, MATCH_TEMPLATE_CALL_NEW),)
TEMPLATE_PAIRS = (
    (TEMPLATE_HASH_OLD, TEMPLATE_HASH_NEW),
    (TEMPLATE_KEY_OLD, TEMPLATE_KEY_NEW),
    (TEMPLATE_CALL_OLD, TEMPLATE_CALL_NEW),
)
SUBSTITUTE_PAIRS = (
    (SUBSTITUTE_LOCALS_OLD, SUBSTITUTE_LOCALS_NEW),
    (SUBSTITUTE_CALLABLE_OLD, SUBSTITUTE_CALLABLE_NEW),
    (SUBSTITUTE_DONE_OLD, SUBSTITUTE_DONE_NEW),
)
FORBIDDEN_DELEGATION = (
    b"PyImport_ImportModule",
    b"PyImport_Import",
    b"dlopen(",
    b"dlsym(",
    b"candidates.rust",
    b"candidates.zig",
    b"candidates.cpp",
    b"candidates.go",
    b"candidates.fortran",
    b"regex.compile",
    b"re.compile(",
)

def replace_exact(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    require(type(raw) is bytes, "replace only first-party bytes")
    require(old != new and raw.count(old) == 1, "require exactly one " + label)
    require(raw.count(new) == 0, "reject an already-applied " + label)
    return raw.replace(old, new, 1)

def replace_region(
    raw: bytes,
    start: bytes,
    end: bytes,
    pairs: tuple[tuple[bytes, bytes], ...],
    label: str,
) -> bytes:
    require(raw.count(start) == 1 and raw.count(end) == 1, "reject duplicate " + label)
    begin = raw.index(start)
    finish = raw.index(end, begin + len(start))
    region = raw[begin:finish]
    for old, new in pairs:
        require(
            old != new and region.count(old) == 1,
            "require exactly one reversible " + label,
        )
        region = region.replace(old, new, 1)
    return raw[:begin] + region + raw[finish:]

def reconstructed_c15(original: bytes) -> bytes:
    require(
        len(original) == ORIGINAL_C[2] and sha256(original) == ORIGINAL_C[1],
        "start from the exact immutable canonical first-party C",
    )
    first = replace_exact(original, FIRST_OLD, FIRST_NEW, "first owned buffer-order repair")
    require(
        len(first) == FIRST_DERIVED_BYTES and sha256(first) == FIRST_DERIVED_SHA256,
        "independently reconstruct the exact first C repair",
    )
    second = replace_exact(first, PICKLE_OLD, PICKLE_NEW, "owned legacy Match reduction")
    second = replace_exact(second, METHOD_OLD, METHOD_NEW, "owned Match protocol method")
    require(
        len(second) == C15_SOURCE_BYTES and sha256(second) == C15_SOURCE_SHA256,
        "independently reconstruct the exact historical C15 C source",
    )
    return second

def repaired_c_variant(previous: bytes, *, frozen: bool = True) -> bytes:
    require(type(previous) is bytes, "derive only complete first-party C source")
    if frozen:
        require(
            len(previous) == C15_SOURCE_BYTES and sha256(previous) == C15_SOURCE_SHA256,
            "repair only the byte-authenticated C15 first-party combined engine",
        )
    for anchor, name in (
        (MATCH_EXPAND_START, "Match.expand"),
        (BUFFER_COPY_START, "replacement buffer copy"),
        (TEMPLATE_START, "replacement template"),
        (MATCH_COPY_START, "Match method boundary"),
        (SUBSTITUTE_START, "Pattern.sub and Pattern.subn"),
        (SUBSTITUTE_END, "next public Pattern method"),
    ):
        require(previous.count(anchor) == 1, "require one independent C " + name)
    require(
        previous.count(ORIGINAL_TEMPLATE_ERROR_HELPER) == 0
        and previous.count(BUFFER_COPY_NEW) == 0,
        "reject a repaired or ambiguous combined C source",
    )
    for _old, new in (*MATCH_PAIRS, *TEMPLATE_PAIRS, *SUBSTITUTE_PAIRS):
        require(previous.count(new) == 0, "reject a pre-applied shape or buffer repair")
    derived = previous.replace(
        MATCH_EXPAND_START, ORIGINAL_TEMPLATE_ERROR_HELPER + MATCH_EXPAND_START, 1,
    )
    derived = replace_region(
        derived, MATCH_EXPAND_START, BUFFER_COPY_START, MATCH_PAIRS, "C Match.expand",
    )
    derived = replace_exact(
        derived, BUFFER_COPY_OLD, BUFFER_COPY_NEW, "general C replacement flags",
    )
    derived = replace_region(
        derived, TEMPLATE_START, MATCH_COPY_START, TEMPLATE_PAIRS, "C replacement hash",
    )
    derived = replace_region(
        derived, SUBSTITUTE_START, SUBSTITUTE_END, SUBSTITUTE_PAIRS, "C buffer lifetime",
    )
    inverse = replace_region(
        derived,
        SUBSTITUTE_START,
        SUBSTITUTE_END,
        tuple((new, old) for old, new in reversed(SUBSTITUTE_PAIRS)),
        "inverse C subject lifetime",
    )
    inverse = replace_region(
        inverse,
        TEMPLATE_START,
        MATCH_COPY_START,
        tuple((new, old) for old, new in reversed(TEMPLATE_PAIRS)),
        "inverse C template hash",
    )
    inverse = replace_exact(inverse, BUFFER_COPY_NEW, BUFFER_COPY_OLD, "inverse C copy")
    inverse = replace_region(
        inverse,
        MATCH_EXPAND_START,
        BUFFER_COPY_START,
        tuple((new, old) for old, new in reversed(MATCH_PAIRS)),
        "inverse C expansion",
    )
    combined_helper = ORIGINAL_TEMPLATE_ERROR_HELPER + MATCH_EXPAND_START
    require(
        inverse.count(combined_helper) == 1,
        "require one reversible original-exporter exception helper",
    )
    inverse = inverse.replace(combined_helper, MATCH_EXPAND_START, 1)
    require(inverse == previous, "forbid unrelated C engine or bridge changes")
    for needle in FORBIDDEN_DELEGATION:
        require(
            derived.count(needle) == previous.count(needle),
            "reject Python, external-package or cross-candidate delegation",
        )
    require(
        derived.count(b"PyBUF_FULL_RO") == previous.count(b"PyBUF_FULL_RO") + 1
        and derived.count(b"substitution_original_template_error(") == 3
        and b"PyObject_Length(replacement)" in derived
        and b"subject_snapshot=PyBytes_FromStringAndSize(" in derived
        and b"Py_XDECREF(subject_snapshot);" in derived
        and derived.count(b"PyBuffer_ToContiguous(")
        == previous.count(b"PyBuffer_ToContiguous(") + 2
        and b"PyBytes_FromStringAndSize(NULL,view.len)" in derived
        and b"NULL,subject.view.len" in derived
        and b"if (version < 2) return match_reduce(match,NULL);" in derived,
        "preserve general original-exporter, hash, release, shape and pickle semantics",
    )
    if frozen:
        require(
            len(derived) == VARIANT_BYTES and sha256(derived) == VARIANT_SHA256,
            "derive the exact complete independent C buffer-and-shape variant",
        )
    return derived

def source_effects() -> dict[str, Any]:
    return {
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "actual_candidate_workers": 0,
        "reference_processes_started": 0,
        "actual_reference_workers": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "native_builds_started": 0,
        "native_activations_started": 0,
        "original_source_targets_modified": 0,
        "original_native_targets_read": 0,
        "matching_archive_bytes_read": 0,
        "matching_archives_opened": 0,
        "matching_archives_inflated": 0,
        "reference_archive_bytes_read": 0,
        "reference_archives_opened": 0,
        "reference_archives_inflated": 0,
        "build_archive_bytes_read": 0,
        "build_archives_opened": 0,
        "build_archives_inflated": 0,
        "recovery_roots_opened": 0,
        "workspace_mutations": 0,
        "network_requests": 0,
        "threads_started": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "large_subject_allocations": 0,
        "qualified_candidate_count": 0,
        "candidate_correctness": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "undefined_behavior": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }

class SourceWall:
    """Physically deny I/O, matching, native loading, archives and clocks."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.installed: set[tuple[int, str]] = set()
        self.blocked = 0

    def deny(self, *_args: Any, **_kwargs: Any) -> Any:
        self.blocked += 1
        raise RepairError("physically rejected a C source-only side effect")

    def install(self, owner: Any, name: str) -> None:
        if owner is None:
            return
        key = (id(owner), name)
        if key in self.installed or not hasattr(owner, name):
            return
        original = getattr(owner, name)
        try:
            setattr(owner, name, self.deny)
        except (TypeError, AttributeError):
            return
        self.saved.append((owner, name, original))
        self.installed.add(key)

    def __enter__(self) -> "SourceWall":
        for owner, names in (
            (builtins, ("open", "__import__")),
            (_io, ("open",)),
            (io, ("open",)),
            (
                os,
                (
                    "open", "read", "write", "stat", "lstat", "listdir",
                    "scandir", "mkdir", "makedirs", "unlink", "remove",
                    "replace", "rename", "link", "symlink", "fsync",
                    "system", "fork", "forkpty", "posix_spawn",
                    "posix_spawnp", "execv", "execve", "popen",
                ),
            ),
            (
                Path,
                (
                    "open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "mkdir", "unlink",
                    "rename", "replace", "resolve", "touch", "glob",
                ),
            ),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (threading.Thread, ("start",)),
            (_thread, ("start_new_thread", "start_joinable_thread")),
            (_imp, ("create_dynamic", "exec_dynamic", "create_builtin")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (signal, ("signal", "raise_signal", "pthread_kill")),
            (
                time,
                (
                    "time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "thread_time", "thread_time_ns",
                    "sleep",
                ),
            ),
        ):
            for name in names:
                self.install(owner, name)
        for name in (
            "gzip", "zlib", "ctypes", "_ctypes", "fcntl", "_posixsubprocess",
        ):
            module = sys.modules.get(name)
            for attribute in (
                "open", "decompress", "decompressobj", "GzipFile",
                "CDLL", "PyDLL", "_dlopen", "dlopen", "flock", "fork_exec",
            ):
                self.install(module, attribute)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)

def validate_v64_summary(summary: dict[str, Any]) -> dict[str, Any]:
    require(type(summary) is dict, "reject a missing published V64 summary")
    expected_scalars: tuple[tuple[str, Any], ...] = (
        ("version", 64),
        ("status", "PASS"),
        ("authenticated_evidence_owner_lower_bound", 216),
        ("authenticated_history_reference_lower_bound", 221),
        ("actually_runnable_candidate_family_count", 0),
        ("qualified_candidate_count", 0),
        ("actual_candidate_workers_started_by_graph", 0),
        ("actual_reference_workers_started_by_graph", 0),
        ("actual_compiler_processes_started_by_graph", 0),
        ("final_holdout_opened", False),
        ("hidden_cases_read", 0),
        ("clock_samples", 0),
        ("timing_trials_run", 0),
        ("performance", "NOT MEASURED"),
        ("memory", "NOT MEASURED"),
        ("undefined_behavior", "NOT MEASURED"),
        ("winner_selected", False),
        ("large_input_source_case_matrix_count", 32),
        ("large_input_actual_candidate_search_status", "NOT RUN"),
        ("large_input_actual_candidate_subn_status", "NOT RUN"),
        ("large_input_actual_large_subject_allocations_by_graph", 0),
        ("large_input_actual_candidate_maximum_subject_bytes", 5_147),
        ("phase1_v4_oracle_readiness_status", "PASS"),
        ("phase1_v4_candidate_qualification_status", "BLOCKED"),
        ("phase1_v4_candidate_testing_authorized", True),
        ("first_party_source_inventory_family_count", 6),
    )
    for name, value in expected_scalars:
        require(
            type(summary.get(name)) is type(value) and summary.get(name) == value,
            "reject changed V64 evidence: " + name,
        )
    require(
        summary.get("required_corrected_candidate_runner_versions") == []
        and summary.get("actually_runnable_candidate_families") == [],
        "never present a source runner or variant as an actually runnable candidate",
    )
    families = summary.get("families")
    require(type(families) is list, "require every independent V64 source family")
    names = [entry.get("family") for entry in families]
    require(
        set(names) == {"python", "rust", "c", "zig", "cpp", "go", "fortran"}
        and len(names) == 7,
        "preserve Python and all six independently owned candidate source families",
    )
    require(
        summary.get("large_input_source_case_status_counts")
        == {
            "FAIL": 1,
            "NOT ESTABLISHED": 2,
            "NOT MEASURED": 3,
            "NOT OPENED": 1,
            "NOT RUN": 3,
            "PASS": 22,
        },
        "preserve every genuine giant-input matrix outcome",
    )
    rust = summary.get("actual_complete_rust_v7_campaign")
    require(
        type(rust) is dict
        and rust.get("status") == "FAIL"
        and rust.get("candidate_status") == "FAIL"
        and rust.get("semantic_mismatch_count") == 928
        and rust.get("case_execution_denominator") == 31_237
        and rust.get("actual_candidate_workers") == 13
        and rust.get("completed_suite_count") == 13
        and rust.get("infrastructure_failure_count") == 0,
        "preserve the real independent Rust failure without sharing its engine",
    )
    require(
        summary.get("individual_rust_suite_mismatches")
        == "NOT PRESENT IN DURABLE RECEIPT",
        "never invent a Rust cohort histogram from the small durable receipt",
    )
    current_rust = summary.get("actual_complete_rust_campaign")
    require(
        type(current_rust) is dict
        and current_rust.get("status") == "FAIL"
        and current_rust.get("candidate_status") == "FAIL"
        and current_rust.get("semantic_mismatch_count") == 1_440
        and current_rust.get("verified_passing_case_count") == 14_853
        and current_rust.get("case_execution_denominator") == 31_237
        and current_rust.get("actual_candidate_workers") == 13
        and current_rust.get("completed_suite_count") == 13
        and current_rust.get("infrastructure_failure_count") == 0,
        "preserve the actual latest complete Rust V10 result",
    )
    old_c = summary.get("actual_c_v4_original_campaign")
    require(
        type(old_c) is dict
        and old_c.get("status") == "FAIL"
        and old_c.get("semantic_mismatch_count") == 1_230
        and old_c.get("case_execution_denominator") == 31_237
        and old_c.get("actual_candidate_workers") == 13
        and old_c.get("verified_passing_case_count") == 7_325,
        "preserve every genuine old-C loss and explicitly verified pass",
    )
    return summary

def validate_rust_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    require(
        receipt.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v7-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_qualified") is False
        and receipt.get("case_execution_denominator") == 31_237
        and receipt.get("suite_count") == 13
        and receipt.get("completed_suite_count") == 13
        and receipt.get("actual_candidate_workers") == 13
        and receipt.get("semantic_mismatch_count") == 928
        and receipt.get("infrastructure_failure_count") == 0
        and receipt.get("all_original_observation_vectors_complete") is True
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("performance") == "NOT MEASURED",
        "authenticate genuine Rust failure publication, never a successful candidate",
    )
    require(
        all(
            key not in receipt
            for key in (
                "individual_suite_mismatches",
                "suite_mismatches",
                "semantic_mismatch_histogram",
                "mismatch_histogram",
            )
        ),
        "never attribute the logged Rust histogram to its small receipt",
    )
    archive = receipt.get("archive")
    require(
        type(archive) is dict
        and archive.get("sha256")
        == "4112b4e6372f4f94d59eece2e514bda21001f0828d686162e18b631911fc2c99"
        and archive.get("size_bytes") == 3_668_825
        and type(archive.get("relative")) is str
        and archive["relative"].endswith(".json.gz"),
        "authenticate only Rust failure-archive metadata supplied by its receipt",
    )
    return receipt

def validate_current_rust_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    require(
        receipt.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v10-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("family") == "rust"
        and receipt.get("candidate_qualified") is False
        and receipt.get("case_execution_denominator") == 31_237
        and receipt.get("suite_count") == 13
        and receipt.get("completed_suite_count") == 13
        and receipt.get("actual_candidate_workers") == 13
        and receipt.get("semantic_mismatch_count") == 1_440
        and receipt.get("verified_passing_case_count") == 14_853
        and receipt.get("infrastructure_failure_count") == 0
        and receipt.get("holdout") == "NOT OPENED",
        "preserve the latest complete Rust V10 failure; never claim V7 is current",
    )
    return receipt

def validate_c_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    require(
        receipt.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v4-durable-publication-receipt"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_qualified") is False
        and receipt.get("case_execution_denominator") == 31_237
        and receipt.get("suite_count") == 13
        and receipt.get("completed_suite_count") == 13
        and receipt.get("actual_candidate_workers") == 13
        and receipt.get("semantic_mismatch_count") == 1_230
        and receipt.get("verified_passing_case_count") == 7_325
        and receipt.get("infrastructure_failure_count") == 0,
        "authenticate the old first-party C failure, not a repaired candidate",
    )
    return receipt

def synthetic_source() -> bytes:
    return (
        b"/* synthetic independent combined C engine and Python bridge */\n"
        + MATCH_EXPAND_START
        + MATCH_TEMPLATE_CALL_OLD
        + b"}\n"
        + BUFFER_COPY_OLD
        + TEMPLATE_START
        + b"                                       PyObject *replacement) {\n"
        + TEMPLATE_HASH_OLD
        + TEMPLATE_KEY_OLD
        + b"    }\n"
        + TEMPLATE_CALL_OLD
        + b"}\n"
        + MATCH_COPY_START
        + b" PyObject *ignored) { return NULL; }\n"
        + SUBSTITUTE_START
        + b" PyObject *args) {\n"
        + SUBSTITUTE_LOCALS_OLD
        + SUBSTITUTE_CALLABLE_OLD
        + SUBSTITUTE_DONE_OLD
        + SUBSTITUTE_END
        + b" PyObject *args) { return NULL; }\n"
        + b"/* if (version < 2) return match_reduce(match,NULL); */\n"
    )

def synthetic_v64() -> dict[str, Any]:
    return {
        "version": 64,
        "status": "PASS",
        "authenticated_evidence_owner_lower_bound": 216,
        "authenticated_history_reference_lower_bound": 221,
        "actually_runnable_candidate_family_count": 0,
        "actually_runnable_candidate_families": [],
        "required_corrected_candidate_runner_versions": [],
        "qualified_candidate_count": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "final_holdout_opened": False,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
        "large_input_source_case_matrix_count": 32,
        "large_input_actual_candidate_search_status": "NOT RUN",
        "large_input_actual_candidate_subn_status": "NOT RUN",
        "large_input_actual_large_subject_allocations_by_graph": 0,
        "large_input_actual_candidate_maximum_subject_bytes": 5_147,
        "phase1_v4_oracle_readiness_status": "PASS",
        "phase1_v4_candidate_qualification_status": "BLOCKED",
        "phase1_v4_candidate_testing_authorized": True,
        "first_party_source_inventory_family_count": 6,
        "large_input_source_case_status_counts": {
            "FAIL": 1,
            "NOT ESTABLISHED": 2,
            "NOT MEASURED": 3,
            "NOT OPENED": 1,
            "NOT RUN": 3,
            "PASS": 22,
        },
        "families": [
            {"family": family}
            for family in ("python", "rust", "c", "zig", "cpp", "go", "fortran")
        ],
        "individual_rust_suite_mismatches": "NOT PRESENT IN DURABLE RECEIPT",
        "actual_complete_rust_v7_campaign": {
            "status": "FAIL",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 928,
            "case_execution_denominator": 31_237,
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "infrastructure_failure_count": 0,
        },
        "actual_complete_rust_campaign": {
            "status": "FAIL",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1_440,
            "verified_passing_case_count": 14_853,
            "case_execution_denominator": 31_237,
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "infrastructure_failure_count": 0,
        },
        "actual_c_v4_original_campaign": {
            "status": "FAIL",
            "semantic_mismatch_count": 1_230,
            "case_execution_denominator": 31_237,
            "actual_candidate_workers": 13,
            "verified_passing_case_count": 7_325,
        },
    }

def self_test() -> dict[str, Any]:
    positives = 0
    rejected = 0

    def accept(condition: Any, description: str) -> None:
        nonlocal positives
        require(condition is True, "positive C source control failed: " + description)
        positives += 1

    def reject(action: Any, description: str) -> None:
        nonlocal rejected
        try:
            action()
        except (RepairError, OSError, ValueError, TypeError, RuntimeError, KeyError):
            rejected += 1
        else:
            raise RepairError("hostile source control escaped: " + description)

    with SourceWall() as wall:
        previous = synthetic_source()
        derived = repaired_c_variant(previous, frozen=False)
        accept(type(derived) is bytes, "complete synthetic C source")
        accept(derived != previous, "nonidentity native repair")
        accept(derived.count(ORIGINAL_TEMPLATE_ERROR_HELPER) == 1, "one error owner")
        accept(derived.count(b"substitution_original_template_error(") == 3, "error dispatch")
        accept(derived.count(BUFFER_COPY_NEW) == 1, "one full-readonly copy")
        accept(derived.count(b"PyBuffer_ToContiguous(")
               == previous.count(b"PyBuffer_ToContiguous(") + 2,
               "two bounded C-order owned-buffer copies")
        accept(b"PyBytes_FromStringAndSize(NULL,view.len)" in derived,
               "one checked replacement-sized allocation")
        accept(b"NULL,subject.view.len" in derived,
               "one checked subject-sized allocation")
        accept(derived.count(b"PyBUF_FULL_RO") == previous.count(b"PyBUF_FULL_RO") + 1,
               "one general full-readonly buffer flag")
        accept(derived.count(MATCH_TEMPLATE_CALL_NEW) == 1, "matching expansion owner")
        accept(derived.count(TEMPLATE_HASH_NEW) == 1, "original replacement hash")
        accept(derived.count(TEMPLATE_KEY_NEW) == 1, "replacement flag selection")
        accept(derived.count(TEMPLATE_CALL_NEW) == 1, "original template exception")
        accept(derived.count(SUBSTITUTE_LOCALS_NEW) == 1, "one subject snapshot")
        accept(derived.count(SUBSTITUTE_CALLABLE_NEW) == 1, "callable remains independent")
        accept(derived.count(SUBSTITUTE_DONE_NEW) == 1, "balanced cleanup")
        accept(b"PyObject_Length(replacement)" in derived, "terminal owner length")
        accept(b"Py_XDECREF(subject_snapshot);" in derived, "snapshot cleanup")
        accept(b"if (version < 2) return match_reduce(match,NULL);" in derived,
               "legacy Match pickle preserved")
        for needle in FORBIDDEN_DELEGATION:
            accept(
                derived.count(needle) == previous.count(needle),
                "no new delegated matching: " + needle.decode("ascii"),
            )
        graph = synthetic_v64()
        accept(validate_v64_summary(graph) is graph, "exact V64 graph")
        accept(sum(count for _, count in SUITES) == 31_237, "original case denominator")
        accept(len(SUITES) == 13, "original suite denominator")
        accept(len(graph["families"]) == 7, "Python plus six first-party families")
        accept(
            graph["large_input_source_case_status_counts"]["NOT RUN"] == 3,
            "giant candidate operations remain unrun",
        )
        accept(
            graph["individual_rust_suite_mismatches"]
            == "NOT PRESENT IN DURABLE RECEIPT",
            "never invent receipt cohort evidence",
        )
        accept(
            source_effects()["qualified_candidate_count"] == 0,
            "source freeze cannot qualify a candidate",
        )
        accept(source_effects()["matching_archives_opened"] == 0, "no matching archive")
        accept(source_effects()["build_archives_inflated"] == 0, "no build archive")
        accept(source_effects()["clock_samples"] == 0, "no performance measurements")
        accept(source_effects()["holdout"] == "NOT OPENED", "preserve final holdout")

        for name in (
            "version", "status", "authenticated_evidence_owner_lower_bound",
            "authenticated_history_reference_lower_bound",
            "actually_runnable_candidate_family_count", "qualified_candidate_count",
            "actual_candidate_workers_started_by_graph",
            "actual_reference_workers_started_by_graph",
            "actual_compiler_processes_started_by_graph", "final_holdout_opened",
            "hidden_cases_read", "clock_samples", "timing_trials_run",
            "performance", "memory", "undefined_behavior", "winner_selected",
            "large_input_source_case_matrix_count",
            "large_input_actual_candidate_search_status",
            "large_input_actual_candidate_subn_status",
            "large_input_actual_large_subject_allocations_by_graph",
            "large_input_actual_candidate_maximum_subject_bytes",
            "individual_rust_suite_mismatches",
        ):
            mutated = dict(graph)
            value = mutated[name]
            if type(value) is bool:
                mutated[name] = not value
            elif type(value) is int:
                mutated[name] = value + 1
            else:
                mutated[name] = "FORGED"
            reject(
                lambda value=mutated: validate_v64_summary(value),
                "substituted V64 graph " + name,
            )
        for name in ("public_types_v1", "substitution_v2", "shape_v2"):
            reject(
                lambda name=name: checked_parts("holdout/" + name),
                "no private holdout access",
            )
        for relative in (
            "../candidates/_vm_native.c",
            "/tmp/foreign.c",
            "candidates/../rust/src/lib.rs",
            "evidence/failure.json.gz",
            "oracle/phase3/holdout.json",
            "benchmarks/timing.json",
            "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        ):
            reject(lambda relative=relative: checked_parts(relative), "unsafe owner " + relative)
        for old, _new, label in (
            (MATCH_TEMPLATE_CALL_OLD, MATCH_TEMPLATE_CALL_NEW, "Match expansion"),
            (BUFFER_COPY_OLD, BUFFER_COPY_NEW, "buffer copy"),
            (TEMPLATE_HASH_OLD, TEMPLATE_HASH_NEW, "template hash"),
            (TEMPLATE_KEY_OLD, TEMPLATE_KEY_NEW, "replacement flags"),
            (TEMPLATE_CALL_OLD, TEMPLATE_CALL_NEW, "template error"),
            (SUBSTITUTE_LOCALS_OLD, SUBSTITUTE_LOCALS_NEW, "snapshot locals"),
            (SUBSTITUTE_CALLABLE_OLD, SUBSTITUTE_CALLABLE_NEW, "callable dispatch"),
            (SUBSTITUTE_DONE_OLD, SUBSTITUTE_DONE_NEW, "release ownership"),
        ):
            mutated = previous.replace(old, b"/* removed owned repair */\n", 1)
            reject(
                lambda value=mutated: repaired_c_variant(value, frozen=False),
                "missing first-party " + label,
            )
        for anchor, label in (
            (MATCH_EXPAND_START, "Match.expand"),
            (BUFFER_COPY_START, "buffer copy"),
            (TEMPLATE_START, "template"),
            (MATCH_COPY_START, "Match boundary"),
            (SUBSTITUTE_START, "substitution"),
            (SUBSTITUTE_END, "next method"),
        ):
            mutated = previous + anchor
            reject(
                lambda value=mutated: repaired_c_variant(value, frozen=False),
                "duplicate C ownership " + label,
            )
        reject(lambda: repaired_c_variant(previous, frozen=True), "synthetic C15 owner")
        reject(lambda: repaired_c_variant(derived, frozen=False), "double C repair")
        for action, label in (
            (lambda: builtins.open("archive.json.gz", "rb"), "built-in archive open"),
            (lambda: _io.open("archive.json.gz", "rb"), "low-level archive open"),
            (lambda: io.open("archive.json.gz", "rb"), "I/O archive open"),
            (lambda: os.open("source", os.O_RDONLY), "descriptor owner open"),
            (lambda: os.read(0, 1), "descriptor source read"),
            (lambda: os.write(1, b"x"), "descriptor output"),
            (lambda: os.stat("source"), "source metadata"),
            (lambda: os.listdir("."), "source enumeration"),
            (lambda: os.mkdir("forbidden"), "source creation"),
            (lambda: os.unlink("forbidden"), "source deletion"),
            (lambda: Path("archive.json.gz").read_bytes(), "Path archive read"),
            (lambda: Path("forbidden").write_text("x"), "Path source mutation"),
            (lambda: subprocess.Popen(("true",)), "candidate process"),
            (lambda: subprocess.run(("true",)), "candidate runner"),
            (lambda: socket.socket(), "network socket"),
            (lambda: socket.create_connection(("localhost", 1)), "network connection"),
            (lambda: threading.Thread(target=lambda: None).start(), "thread launch"),
            (lambda: _thread.start_new_thread(lambda: None, ()), "low-level thread"),
            (lambda: _imp.create_dynamic(None), "native library creation"),
            (lambda: _imp.exec_dynamic(None), "native library execution"),
            (lambda: importlib.import_module("candidates.vm_candidate"), "candidate import"),
            (lambda: __import__("re"), "standard regular-expression import"),
            (lambda: tempfile.mkdtemp(), "private recovery root"),
            (lambda: signal.raise_signal(signal.SIGINT), "signal escape"),
            (lambda: time.time(), "wall clock"),
            (lambda: time.monotonic(), "monotonic clock"),
            (lambda: time.perf_counter(), "benchmark clock"),
            (lambda: time.process_time(), "CPU clock"),
            (lambda: time.sleep(0), "sleep"),
        ):
            reject(action, label)
        accept(wall.blocked >= 25, "physical source-only side-effect probes")
    require(positives >= 35, "require independent positive source controls")
    require(rejected >= 65, "require complete hostile source controls")
    return {
        "status": "PASS",
        "positive_controls": positives,
        "hostile_controls": rejected,
        "physically_blocked_effects": wall.blocked,
        "source_only_effects": source_effects(),
    }

def authenticate_source(relative: str, fingerprint: str) -> bytes:
    checked_digest(fingerprint, relative)
    checked_parts(relative)
    visible = os.stat(ROOT / relative, follow_symlinks=False)
    require(stat.S_ISREG(visible.st_mode), "require one immutable source owner")
    return read_owner((relative, fingerprint, visible.st_size))

def verified_frozen_context(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str | None = None,
    *,
    require_variant: bool = True,
) -> tuple[dict[str, Any], bytes]:
    verify_runtime()
    checked_digest(source_pin, "C subject-buffer V1 source")
    checked_digest(protocol_pin, "C subject-buffer V1 protocol")
    if contract_pin is not None:
        checked_digest(contract_pin, "C subject-buffer V1 contract")
    require(
        not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules),
        "refuse candidate code imported into the source verifier",
    )
    source_raw = authenticate_source(SELF, source_pin)
    protocol_raw = authenticate_source(PROTOCOL, protocol_pin)
    require(source_raw.startswith(b"#!/usr/bin/env python3\n"), "require complete source")
    require(protocol_raw.startswith(b"# "), "require the plain-language source protocol")
    goal = read_owner(GOAL)
    require(goal.startswith(b"/goal "), "preserve the immutable goal")
    for owner in P0_READINESS.values():
        read_owner(owner)
    phase_one = strict_document(read_owner(PHASE_ONE), "corrected P0 V4 Python readiness")
    original_oracle = phase_one.get("original_oracle")
    reference = phase_one.get("actual_supplemental_two_reference")
    phase_gate = phase_one.get("phase_gate")
    qualification = phase_one.get("candidate_qualification_gate")
    require(
        phase_one.get("schema") == "rebar-cpython-re-p0-completeness-v4"
        and phase_one.get("version") == 4
        and phase_one.get("status") == "PASS"
        and phase_one.get("original_case_execution_denominator") == 31_237
        and phase_one.get("original_suite_count") == 13
        and phase_one.get("original_named_private_waiver_count") == 13
        and phase_one.get("first_party_candidate_family_count") == 6
        and phase_one.get("qualified_candidate_count") == 0
        and type(original_oracle) is dict
        and original_oracle.get("case_execution_denominator") == 31_237
        and original_oracle.get("suite_count") == 13
        and original_oracle.get("named_private_waiver_count") == 13
        and [entry.get("id") for entry in original_oracle.get("suites", [])]
        == [name for name, _ in SUITES]
        and [entry.get("case_execution_count") for entry in original_oracle.get("suites", [])]
        == [count for _, count in SUITES]
        and type(reference) is dict
        and reference.get("actual_reference_worker_count") == 2
        and reference.get("case_count_per_worker") == [8_244, 8_244]
        and reference.get("failed_per_worker") == [0, 0]
        and reference.get("worker_exit_codes") == [0, 0]
        and type(phase_gate) is dict
        and phase_gate.get("status") == "PASS"
        and phase_gate.get("candidate_evaluation_authorized") is True
        and phase_gate.get("performance_oracle_authorized") is False
        and phase_gate.get("final_holdout_authorized") is False
        and type(qualification) is dict
        and qualification.get("status") == "BLOCKED"
        and qualification.get("qualified_candidate_count") == 0,
        "preserve the corrected 31,237-case P0 V4 and actual 8,244-case references",
    )
    raw_original = read_owner(ORIGINAL_C)
    read_owner(ORIGINAL_ADAPTER)
    for owner in (FIRST_REPAIR, PICKLE_REPAIR):
        owner_raw = read_owner(owner)
        if owner[0].endswith(".py"):
            compile(owner_raw.decode("utf-8"), owner[0], "exec", dont_inherit=True)
    for owner in PRODUCER.values():
        read_owner(owner)
    producer = strict_document(read_owner(PRODUCER["contract"]), "corrected V4 producer")
    require(
        producer.get("schema") == "rebar-owned-six-family-original-p0-producer-v4-source-freeze"
        and producer.get("version") == 4
        and producer.get("case_execution_denominator") == 31_237
        and producer.get("suite_count") == 13,
        "require the corrected complete V4 original-case producer",
    )
    for owner in C_RUNNER.values():
        read_owner(owner)
    c_runner = strict_document(read_owner(C_RUNNER["contract"]), "frozen C-only V10 runner")
    require(
        c_runner.get("schema") == "rebar-frozen-python-re-p0-candidate-protocol-v10"
        and c_runner.get("version") == 10
        and c_runner.get("case_execution_denominator") == 31_237
        and c_runner.get("suite_count") == 13
        and c_runner.get("named_private_waiver_count") == 13
        and c_runner.get("source_inventory_family_count") == 6
        and c_runner.get("source_inventory_owner_count") == 25
        and c_runner.get("runnable_candidate_families") == ["c"]
        and c_runner.get("runnable_candidate_family_count") == 1,
        "preserve one C-only source dispatch, never invent a live candidate",
    )
    runner_boundary = c_runner.get("phase_boundary")
    require(
        type(runner_boundary) is dict
        and runner_boundary.get("actual_candidate_workers") == 0
        and runner_boundary.get("actual_reference_workers") == 0
        and runner_boundary.get("candidate_qualified_count") == 0
        and runner_boundary.get("candidate_correctness") == "NOT MEASURED"
        and runner_boundary.get("holdout") == "NOT OPENED",
        "preserve the frozen runner's genuine source-only boundary",
    )
    for role, owner in V64.items():
        owner_raw = read_owner(owner)
        if role == "source":
            compile(owner_raw.decode("utf-8"), owner[0], "exec", dont_inherit=True)
    graph = validate_v64_summary(
        strict_document(read_owner(V64["summary"]), "published immutable V64 graph")
    )
    inputs = strict_document(read_owner(V64["inputs"]), "immutable V64 graph inputs")
    require(inputs.get("version") == 64, "reject substituted V64 graph inputs")
    rust_receipt = validate_rust_receipt(
        strict_document(read_owner(RUST_V7_RECEIPT), "small Rust V7 loss receipt")
    )
    current_rust_receipt = validate_current_rust_receipt(
        strict_document(read_owner(RUST_V10_RECEIPT), "small current Rust V10 loss receipt")
    )
    c_receipt = validate_c_receipt(
        strict_document(read_owner(C_FAILURE_RECEIPT), "small historical C loss receipt")
    )
    c_build_receipt = strict_document(read_owner(C15_BUILD_RECEIPT), "small historical C15 receipt")
    require(
        c_build_receipt.get("schema")
        == "rebar-phase2-owned-c-pickle-source-build-v15-durable-publication-receipt"
        and c_build_receipt.get("status") == "PASS"
        and c_build_receipt.get("label") == "phase2-v15-c-pickle-original-p0"
        and c_build_receipt.get("actual_compiler_process_count") == 14
        and c_build_receipt.get("candidate_correctness") == "NOT MEASURED"
        and c_build_receipt.get("holdout") == "NOT OPENED",
        "preserve the old C15 build; never claim it compiled the V2 variant",
    )
    c15 = reconstructed_c15(raw_original)
    derived = repaired_c_variant(c15)
    if require_variant:
        variant = read_owner((VARIANT, VARIANT_SHA256, VARIANT_BYTES))
        require(variant == derived, "authenticate every byte of the full combined C variant")
    context = {
        "graph": graph,
        "rust_receipt": rust_receipt,
        "current_rust_receipt": current_rust_receipt,
        "c_receipt": c_receipt,
        "producer": producer,
        "runner": c_runner,
        "variant_authenticated": require_variant,
    }
    if contract_pin is not None:
        contract_raw = authenticate_source(CONTRACT, contract_pin)
        supplied = strict_document(contract_raw, "frozen C subject-buffer V1 contract")
        expected = contract_document(source_pin, protocol_pin)
        require(supplied == expected, "reject a changed complete C subject-buffer V1 contract")
    return context, derived

def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "frozen C subject-buffer V1 source")
    checked_digest(protocol_pin, "frozen C subject-buffer V1 protocol")
    return {
        "schema": SCHEMA,
        "version": 1,
        "phase": "SOURCE FREEZE; FIRST-PARTY C SUBJECT BUFFER VARIANT NOT BUILT OR RUN",
        "family": "c",
        "goal": owner_pin(GOAL),
        "pinned_cpython": {
            "implementation": "CPython",
            "version": "3.14.6",
            "executable": PYTHON,
            "sha256": PYTHON_SHA256,
            "bytes": PYTHON_BYTES,
            "isolated": True,
            "bytecode": False,
        },
        "source": {"path": SELF, "sha256": source_pin},
        "protocol": {"path": PROTOCOL, "sha256": protocol_pin},
        "corrected_p0_v4_readiness": {
            "owners": owner_group(P0_READINESS),
            "status": "PASS",
            "scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
            "supplemental_cases_per_reference": 8_244,
            "supplemental_reference_workers": 2,
            "supplemental_cases_added_to_original_denominator": False,
            "candidate_qualification_status": "BLOCKED",
        },
        "phase_one": {
            "owner": owner_pin(PHASE_ONE),
            "case_execution_denominator": 31_237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "suites": [{"id": name, "case_execution_count": count} for name, count in SUITES],
            "cases_removed": 0,
            "waivers_added": 0,
        },
        "published_v64": {
            "version": 64,
            "owners": owner_group(V64),
            "authenticated_evidence_owner_lower_bound": 216,
            "authenticated_history_reference_lower_bound": 221,
            "lower_bounds_are_not_whole_repository_counts": True,
            "required_corrected_candidate_runner_versions": [],
            "actually_runnable_candidate_families": [],
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            "future_overview_versions_do_not_invalidate_this_immutable_predecessor": True,
        },
        "corrected_original_v4_producer": owner_group(PRODUCER),
        "corrected_c_only_v10_runner": {
            "owners": owner_group(C_RUNNER),
            "source_dispatch_families": ["c"],
            "source_dispatch_is_not_live_candidate_runnability": True,
            "case_execution_denominator": 31_237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "source_inventory_family_count": 6,
            "source_inventory_owner_count": 25,
            "matching_started": False,
        },
        "original_first_party_c_owners": {
            "combined_native_engine_and_python_bridge": owner_pin(ORIGINAL_C),
            "unchanged_public_python_adapter": owner_pin(ORIGINAL_ADAPTER),
            "canonical_engine_modified": False,
            "canonical_adapter_modified": False,
            "canonical_native_loaded": False,
        },
        "pure_first_party_derivation": {
            "historical_first_repair_source": owner_pin(FIRST_REPAIR),
            "historical_pickle_repair_source": owner_pin(PICKLE_REPAIR),
            "first_reconstructed_source": {
                "bytes": FIRST_DERIVED_BYTES,
                "sha256": FIRST_DERIVED_SHA256,
            },
            "historical_c15_source": {
                "bytes": C15_SOURCE_BYTES,
                "sha256": C15_SOURCE_SHA256,
                "reconstructed_from_immutable_canonical_source": True,
                "private_build_root_opened": False,
            },
            "historical_c15_build_receipt": owner_pin(C15_BUILD_RECEIPT),
            "historical_c15_build_is_not_this_variant_build": True,
        },
        "historical_c_observation": {
            "publication_receipt": owner_pin(C_FAILURE_RECEIPT),
            "historical_c_case_execution_denominator": 31_237,
            "historical_c_worker_count": 13,
            "historical_c_semantic_mismatch_count": 1_230,
            "explicitly_verified_historical_c_passing_cases": 7_325,
            "historically_reported_shape_targets": 672,
            "historically_reported_substitution_targets": 224,
            "historically_reported_combined_targets": 896,
            "individual_c_histogram_provenance": (
                "Previously reported historical failure cohorts; not present in "
                "the small C receipt and not independently recomputed by this "
                "archive-free source verifier."
            ),
            "obsolete_v40_source_freeze_required": False,
            "untracked_historical_owner_required": False,
            "targeted_mismatches_repaired": "NOT MEASURED",
            "historical_archive_read_by_v2": False,
        },
        "independent_rust_history": {
            "publication_receipt": owner_pin(RUST_V7_RECEIPT),
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 928,
            "case_execution_denominator": 31_237,
            "completed_suite_count": 13,
            "actual_candidate_workers": 13,
            "receipt_contains_individual_suite_histogram": False,
            "historical_root_log_owner": owner_pin(HISTORICAL_V48_LOG),
            "historical_root_log_opened_by_v2": False,
            "historically_reported_suite_mismatches": {
                "public_types_v1": 32,
                "substitution_v2": 224,
                "shape_v2": 672,
            },
            "histogram_provenance": (
                "Historical root-observed, complete archived report recorded in the "
                "pushed V64 experiment log; not present in the Rust small receipt; "
                "log and archive are never opened by this verifier."
            ),
            "rust_parser_compiler_executor_or_engine_reused": False,
        },
        "current_rust_v10_history": {
            "publication_receipt": owner_pin(RUST_V10_RECEIPT),
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1_440,
            "verified_passing_case_count": 14_853,
            "case_execution_denominator": 31_237,
            "completed_suite_count": 13,
            "actual_candidate_workers": 13,
            "rust_parser_compiler_executor_or_engine_reused": False,
        },
        "complete_first_party_c_variant": {
            "owner": owner_pin((VARIANT, VARIANT_SHA256, VARIANT_BYTES)),
            "language": "C",
            "layout": "owned Python parser and first-party C bytecode engine and CPython bridge",
            "append_only_new_variant": True,
            "independent_parser_compiler_executor_and_engine": True,
            "original_exporter_error_context_preserved": True,
            "original_replacement_hash_observed": True,
            "replacement_full_readonly_buffer_flags": "PyBUF_FULL_RO",
            "normal_replacement_buffer_flags": "PyBUF_SIMPLE",
            "replacement_subject_released_before_materialization": True,
            "safe_contiguous_copy_order": "C",
            "checked_exact_buffer_allocation": True,
            "indirect_and_strided_buffer_safe_by_construction": True,
            "subject_buffer_released_exactly_once": True,
            "preserves_zero_length_buffer": True,
            "callable_replacement_path_preserved": True,
            "previous_match_pickle_repair_preserved": True,
            "all_native_changes_reversibly_anchored": True,
            "shape_and_pep688_result": "NOT MEASURED",
            "actual_build": "NOT RUN",
            "actual_activation": "NOT RUN",
            "actual_candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
        },
        "large_input_history": {
            "case_matrix_count": 32,
            "source_case_status_counts": {
                "FAIL": 1,
                "NOT ESTABLISHED": 2,
                "NOT MEASURED": 3,
                "NOT OPENED": 1,
                "NOT RUN": 3,
                "PASS": 22,
            },
            "actual_candidate_search": "NOT RUN",
            "actual_candidate_subn": "NOT RUN",
            "actual_giant_subject_allocations": 0,
            "maximum_actual_candidate_subject_bytes": 5_147,
            "two_billion_character_candidate_tests": "NOT RUN",
            "native_large_allocation_arithmetic": "NOT VERIFIED",
            "native_undefined_behavior": "NOT MEASURED",
            "large_cases_added_to_original_denominator": False,
        },
        "delegation_policy": {
            "stdlib_re": "FORBIDDEN",
            "stdlib__sre": "FORBIDDEN",
            "cpython_regular_expression_engine": "FORBIDDEN",
            "external_regular_expression_packages": "FORBIDDEN",
            "other_candidate_parser_compiler_executor_or_engine": "FORBIDDEN",
            "hardcoded_oracle_answers": "FORBIDDEN",
            "case_ids_in_native_variant": "FORBIDDEN",
            "candidate_fallback": "FORBIDDEN",
            "candidate_or_reference_execution": "FORBIDDEN",
            "native_build_or_loading": "FORBIDDEN",
            "historical_archive_open_or_inflation": "FORBIDDEN",
            "benchmark_or_holdout": "FORBIDDEN",
            "clock_or_network": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "source_only_effects": source_effects(),
    }

def verify_report(source_pin: str, protocol_pin: str, contract_pin: str) -> dict[str, Any]:
    context, derived = verified_frozen_context(source_pin, protocol_pin, contract_pin)
    return {
        "schema": SCHEMA + "-verification",
        "status": "PASS",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "published_overview_version": 64,
        "published_overview_sha256": V64["summary"][1],
        "authenticated_evidence_owner_lower_bound": 216,
        "authenticated_history_reference_lower_bound": 221,
        "case_execution_denominator": 31_237,
        "suite_count": 13,
        "named_private_waiver_count": 13,
        "source_inventory_family_count": 6,
        "live_runnable_candidate_count": 0,
        "qualified_candidate_count": 0,
        "combined_native_variant": owner_pin((VARIANT, VARIANT_SHA256, VARIANT_BYTES)),
        "derived_variant_sha256": sha256(derived),
        "derived_variant_bytes": len(derived),
        "historical_c_mismatches": context["c_receipt"]["semantic_mismatch_count"],
        "historical_c_buffer_shape_targets": 896,
        "historical_rust_mismatches": context["rust_receipt"]["semantic_mismatch_count"],
        "current_rust_mismatches": context["current_rust_receipt"]["semantic_mismatch_count"],
        "current_rust_verified_passing_cases": context["current_rust_receipt"]["verified_passing_case_count"],
        "corrected_p0_v4_readiness_status": "PASS",
        "supplemental_reference_cases_per_worker": 8_244,
        "historical_rust_histogram_reported_only_in_root_log": True,
        "historical_v48_log_read_by_v2": False,
        "source_only_effects": source_effects(),
    }

def parse_arguments(values: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze and authenticate one independent first-party C variant."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--render-variant", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--variant-part", type=int)
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "independently supplied source")
    checked_digest(options.protocol_sha256, "independently supplied protocol")
    if options.self_test or options.verify_frozen_context:
        checked_digest(options.contract_sha256, "independently supplied contract")
        require(options.variant_part is None, "reject variant selection for a source gate")
    else:
        require(options.contract_sha256 is None, "never predict a self-referential contract")
    if options.render_variant:
        require(
            options.variant_part is None
            or type(options.variant_part) is int and 1 <= options.variant_part <= 6,
            "select one of exactly six read-only C source slices",
        )
    else:
        require(options.variant_part is None, "reject unexpected C variant output")
    return options

def main(values: list[str] | None = None) -> int:
    try:
        options = parse_arguments(values)
        if options.render_variant:
            _context, derived = verified_frozen_context(
                options.source_sha256,
                options.protocol_sha256,
                None,
                require_variant=False,
            )
            if options.variant_part is not None:
                part = options.variant_part
                begin = len(derived) * (part - 1) // 6
                finish = len(derived) * part // 6
                derived = derived[begin:finish]
            written = sys.stdout.buffer.write(derived)
            require(written == len(derived), "refuse truncated C variant output")
            sys.stdout.buffer.flush()
            return 0
        if options.render_contract:
            verified_frozen_context(
                options.source_sha256, options.protocol_sha256, None,
            )
            result = contract_document(options.source_sha256, options.protocol_sha256)
        elif options.verify_frozen_context:
            result = verify_report(
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
        else:
            verified_frozen_context(
                options.source_sha256,
                options.protocol_sha256,
                options.contract_sha256,
            )
            result = self_test()
            result.update(
                {
                    "schema": SCHEMA + "-self-test",
                    "source_sha256": options.source_sha256,
                    "protocol_sha256": options.protocol_sha256,
                    "contract_sha256": options.contract_sha256,
                    "published_overview_version": 64,
                    "derived_variant_sha256": VARIANT_SHA256,
                    "derived_variant_bytes": VARIANT_BYTES,
                }
            )
        encoded = canonical(result)
        written = sys.stdout.buffer.write(encoded)
        require(written == len(encoded), "refuse truncated C source-gate output")
        sys.stdout.buffer.flush()
        return 0
    except (RepairError, OSError, ValueError, TypeError, UnicodeError, RecursionError) as error:
        sys.stderr.write("FIRST-PARTY C SUBJECT-BUFFER V1: FAIL: " + str(error) + "\n")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
