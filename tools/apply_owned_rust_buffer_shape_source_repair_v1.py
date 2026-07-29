#!/usr/bin/env python3
"""Freeze one first-party Rust buffer-lifecycle source repair without running it."""

from __future__ import annotations

import sys

_BOOT_MODULES = frozenset(sys.modules)
if "re" in _BOOT_MODULES or "_sre" in _BOOT_MODULES:
    raise SystemExit("Rust buffer-shape source freeze requires no re or _sre import")

import ast
import builtins
import hashlib
import os
import stat

ROOT = "/home/dev-user/src/rebar"
SOURCE = "tools/apply_owned_rust_buffer_shape_source_repair_v1.py"
PROTOCOL = "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-REPAIR-V1.md"
CONTRACT = "oracle/phase2/rust-buffer-shape-source-repair-v1.json"
VARIANT = "candidates/rust/variants/buffer_shape_v1/py_bridge.c"
SCHEMA = "rebar-phase2-owned-rust-buffer-shape-source-repair-v1-source-freeze"
STATUS = "SOURCE FROZEN; FIRST-PARTY RUST BUFFER-SHAPE VARIANT NOT BUILT OR RUN"
ACTUAL_BRIDGE_SHA256 = "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
ACTUAL_BRIDGE_BYTES = 176118
ACTUAL_ADAPTER_SHA256 = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ACTUAL_ADAPTER_BYTES = 31934
VARIANT_SHA256 = "29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3"
VARIANT_BYTES = 180436
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 64
MAX_OWNER_BYTES = 40 * 1024 * 1024

OWNERS = (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756),
    ("original_p0_matrix", "oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632),
    ("original_p0_protocol", "oracle/phase1/P0-COMPLETENESS-V1.md", "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798", 10392),
    ("large_input_supplement", "oracle/phase1/p0-large-input-indexing-v1.json", "23601fe4947c70979081d8248ee9891287e3fa618b554b97a8ee56024823bacf", 17322),
    ("public_entrypoint_supplement", "oracle/phase1/p0-public-entrypoint-import-v1.json", "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47", 9823),
    ("callable_introspection_supplement", "oracle/phase1/p0-callable-introspection-v1.json", "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349", 14749),
    ("first_party_family_inventory", "oracle/phase2/candidate-independence-v2.json", "89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659", 8798),
    ("original_six_family_producer", "tools/run_owned_six_family_original_p0_producer_v4.py", "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782),
    ("original_six_family_protocol", "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md", "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5", 5981),
    ("original_six_family_contract", "oracle/phase2/six-family-p0-producer-v4.json", "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867),
    ("historical_rust_bridge_derivation", "tools/apply_owned_rust_source_repair_v1.py", "1d5d9b5e3fecb278fdcb97ef21dadff9134cdd779cb6751c42d4931096796851", 59388),
    ("historical_rust_bridge_protocol", "oracle/phase2/RUST-SOURCE-REPAIR-V1.md", "df9ce744660a4328a2b83151a3320aca64a7ad1606e14a4509f50f638a4afc7b", 5496),
    ("historical_rust_bridge_contract", "oracle/phase2/rust-source-repair-v1.json", "1ef69922310cb40166896685c75004c9f423a78e5bb96341a545d4dc75a1cf9b", 8306),
    ("historical_rust_adapter_derivation", "tools/apply_owned_rust_public_contract_source_repair_v3.py", "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060),
    ("historical_rust_adapter_protocol", "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md", "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405),
    ("historical_rust_adapter_contract", "oracle/phase2/rust-public-contract-source-repair-v3.json", "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817),
    ("actual_v13_build_source", "tools/reproduce_owned_rust_pattern_repr_source_build_v13.py", "2ec050c9902cbb3a239ed3a2dce3258344300b40546e37aea374cf18a9c8b797", 133023),
    ("actual_v13_build_protocol", "oracle/phase2/RUST-PATTERN-REPR-SOURCE-BUILD-V13.md", "3c486fdb63041b4f6060a6147186dd93c8339cbdff5f8060f597ab156ff05701", 5894),
    ("actual_v13_build_contract", "oracle/phase2/rust-pattern-repr-source-build-v13.json", "15023a0a484715f2d97ae5ea9649bb16fe3d30781d601635bda40c246c5906aa", 20519),
    ("actual_v7_campaign_source", "tools/run_owned_repaired_rust_original_campaign_v7.py", "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104", 505616),
    ("actual_v7_campaign_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md", "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840", 8433),
    ("actual_v7_campaign_contract", "oracle/phase2/repaired-rust-original-campaign-v7.json", "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5", 46385),
    ("actual_v7_small_plaintext_receipt", "oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures-publication-receipt.json", "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943", 8450),
    ("actual_v13_small_plaintext_build_receipt", "oracle/phase2/evidence/native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0-publication-receipt.json", "4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805", 2437),
    ("canonical_rust_bridge", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
    ("canonical_rust_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
    ("first_party_rust_manifest", "candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    ("first_party_rust_lock", "candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    ("first_party_rust_engine", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    ("first_party_rust_newline", "candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    ("first_party_rust_search", "candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    ("first_party_rust_stack", "candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    ("first_party_rust_unicode", "candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    ("current_v48_renderer", "tools/render_candidate_current_overview_v48.py", "29604bd560dcba08f95ca8bcc792bf277c43a4680d94a82990fd341a1b0f6394", 89718),
    ("current_v48_inputs", "docs/evidence/candidate-current-overview-v48.inputs.json", "d1bc5998012a8f174788a4c28fad7fa1116078a3cbb859b0f952eb65777e33da", 523944),
    ("current_v48_summary", "docs/evidence/candidate-current-overview-v48.json", "bfd591aebf6aea805c8f6a4b5665d87ceca6b2574513bb5cdfb8331b36176305", 1428930),
    ("current_v48_chart", "docs/evidence/candidate-current-overview-v48.svg", "cf8955199d714854faeea4d5c0cabf4431010949a7b7d5ed81d5b65f14b74903", 20331),
    ("pinned_cpython_3146", "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14", "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016", 32387816),
)

HELPER_ANCHOR = b"static int rust_replacement_cache(PyObject *pattern, PyObject *templates, PyObject *replacement, PyObject *subject, Py_ssize_t length, PyObject **raw, PyObject **tokens) {\n"
HELPER = b"static int rust_restore_original_template_error(PyObject *replacement) {\n    PyObject *raised = PyErr_GetRaisedException();\n    if (raised == NULL) {\n        PyErr_SetString(PyExc_RuntimeError, \"Rust template lost its original exception\");\n        return -1;\n    }\n\n    PyObject *message = PyObject_GetAttrString(raised, \"msg\");\n    if (message == NULL) {\n        PyErr_Clear();\n        PyErr_SetRaisedException(raised);\n        return -1;\n    }\n\n    PyObject *position = PyObject_GetAttrString(raised, \"pos\");\n    if (position == NULL) {\n        PyErr_Clear();\n        Py_DECREF(message);\n        PyErr_SetRaisedException(raised);\n        return -1;\n    }\n\n    if (position == Py_None || !PyUnicode_Check(message)) {\n        Py_DECREF(position);\n        Py_DECREF(message);\n        PyErr_SetRaisedException(raised);\n        return -1;\n    }\n\n    if (\n        PyUnicode_CompareWithASCIIString(\n            message, \"bad escape (end of pattern)\"\n        ) == 0\n    ) {\n        Py_ssize_t original_length = PyObject_Length(replacement);\n        if (original_length < 0) {\n            Py_DECREF(position);\n            Py_DECREF(message);\n            Py_DECREF(raised);\n            return -1;\n        }\n        PyObject *original_position = PyLong_FromSsize_t(original_length - 1);\n        if (original_position == NULL) {\n            Py_DECREF(position);\n            Py_DECREF(message);\n            Py_DECREF(raised);\n            return -1;\n        }\n        Py_SETREF(position, original_position);\n    }\n\n    PyObject *restored = PyObject_CallFunctionObjArgs(\n        (PyObject *)Py_TYPE(raised), message, replacement, position, NULL\n    );\n    Py_DECREF(position);\n    Py_DECREF(message);\n    Py_DECREF(raised);\n    if (restored != NULL) {\n        PyErr_SetRaisedException(restored);\n    }\n    return -1;\n}\n\n"
OLD_CACHE_DECLARATION = b"    PyObject *normalized = NULL;\n    int escaped = 0;\n\n    if (PyUnicode_Check(replacement)) {\n"
NEW_CACHE_DECLARATION = b"    PyObject *normalized = NULL;\n    int escaped = 0;\n    int original_hash_checked = 0;\n\n    if (PyUnicode_Check(replacement)) {\n"
OLD_BUFFER_MATERIALIZATION = b"        if (PyObject_GetBuffer(replacement, &buffer, PyBUF_SIMPLE) == 0) {\n            escaped = buffer.len != 0 && memchr(buffer.buf, '\\\\', (size_t)buffer.len) != NULL;\n            PyBuffer_Release(&buffer);\n            if (escaped) {\n                if (PyObject_GetBuffer(replacement, &buffer, PyBUF_SIMPLE) != 0) return -1;\n                normalized = PyBytes_FromStringAndSize(buffer.buf, buffer.len);\n                PyBuffer_Release(&buffer);\n                if (normalized == NULL) return -1;\n            }\n        } else {\n"
NEW_BUFFER_MATERIALIZATION = b"        if (PyObject_GetBuffer(replacement, &buffer, PyBUF_SIMPLE) == 0) {\n            escaped = buffer.len != 0 && memchr(buffer.buf, '\\\\', (size_t)buffer.len) != NULL;\n            PyBuffer_Release(&buffer);\n            if (escaped) {\n                int materialization_flags = PyBUF_SIMPLE;\n                Py_hash_t original_hash = PyObject_Hash(replacement);\n                original_hash_checked = 1;\n                if (original_hash == -1) {\n                    if (!PyErr_ExceptionMatches(PyExc_TypeError)) return -1;\n                    PyErr_Clear();\n                    materialization_flags = PyBUF_FULL_RO;\n                }\n                if (\n                    PyObject_GetBuffer(\n                        replacement, &buffer, materialization_flags\n                    ) != 0\n                ) {\n                    return -1;\n                }\n                normalized = PyBytes_FromStringAndSize(\n                    (const char *)buffer.buf, buffer.len\n                );\n                PyBuffer_Release(&buffer);\n                if (normalized == NULL) return -1;\n            }\n        } else {\n"
OLD_HASH = b"    if (!PyUnicode_CheckExact(replacement) && !PyBytes_CheckExact(replacement)) {\n        Py_hash_t fingerprint = PyObject_Hash(replacement);\n"
NEW_HASH = b"    if (\n        !original_hash_checked\n        && !PyUnicode_CheckExact(replacement)\n        && !PyBytes_CheckExact(replacement)\n    ) {\n        Py_hash_t fingerprint = PyObject_Hash(replacement);\n"
OLD_TEMPLATE_FAILURE = b"    Py_DECREF(normalized);\n    if (loaded == NULL) {\n        if (((PyUnicode_Check(replacement) && !PyUnicode_CheckExact(replacement))\n"
NEW_TEMPLATE_FAILURE = b"    Py_DECREF(normalized);\n    if (loaded == NULL) {\n        if (\n            !PyUnicode_Check(replacement)\n            && !PyBytes_Check(replacement)\n            && PyObject_CheckBuffer(replacement)\n        ) {\n            return rust_restore_original_template_error(replacement);\n        }\n        if (((PyUnicode_Check(replacement) && !PyUnicode_CheckExact(replacement))\n"
OLD_EXPANSION_FAILURE = b"            PyObject *result = rust_match_expand_fallback(match, normalized);\n            Py_DECREF(normalized);\n            return result;\n"
NEW_EXPANSION_FAILURE = b"            PyObject *result = rust_match_expand_fallback(match, normalized);\n            Py_DECREF(normalized);\n            if (result == NULL) {\n                (void)rust_restore_original_template_error(template);\n            }\n            return result;\n"
OLD_CAPTURE = b"    if (!rust_subject_open(&capture, NULL, subject->object, 0)) {\n        return -1;\n    }\n    int result = rust_output_subject(writer, &capture, begin, end);\n"
NEW_CAPTURE = b"    if (!rust_subject_open(&capture, NULL, subject->object, 0)) {\n        return -1;\n    }\n    if (end > capture.length) {\n        rust_subject_release(&capture);\n        PyErr_SetString(\n            PyExc_BufferError,\n            \"Rust captured buffer changed size during replacement\"\n        );\n        return -1;\n    }\n    int result = rust_output_subject(writer, &capture, begin, end);\n"
SUBSTITUTION_START = b"static PyObject *rust_substitute_core("
SUBSTITUTION_END = b"static PyObject *rust_bound_substitute("
SNAPSHOT_ANCHOR = b"    size_t stride = groups + 1;\n"
SNAPSHOT_INSERTION = b"    if (!callback && subject.view.obj != NULL) {\n        if (subject.length > (size_t)PY_SSIZE_T_MAX) {\n            Py_XDECREF(raw);\n            Py_XDECREF(tokens);\n            rust_subject_release(&subject);\n            return PyErr_NoMemory();\n        }\n        subject_snapshot = PyBytes_FromStringAndSize(\n            (const char *)subject.data, (Py_ssize_t)subject.length\n        );\n        if (subject_snapshot == NULL) {\n            Py_XDECREF(raw);\n            Py_XDECREF(tokens);\n            rust_subject_release(&subject);\n            return NULL;\n        }\n        rust_subject_release(&subject);\n        if (!rust_subject_open(&subject, pattern_value, subject_snapshot, 1)) {\n            Py_XDECREF(raw);\n            Py_XDECREF(tokens);\n            rust_subject_release(&subject);\n            Py_DECREF(subject_snapshot);\n            return NULL;\n        }\n    }\n\n"
UNSAFE_CONTIGUOUS_COPY = b"                normalized = PyBytes_FromStringAndSize(\n                    (const char *)buffer.buf, buffer.len\n                );\n"
SAFE_CONTIGUOUS_COPY = b"                normalized = PyBytes_FromStringAndSize(NULL, buffer.len);\n                if (\n                    normalized != NULL\n                    && buffer.len != 0\n                    && PyBuffer_ToContiguous(\n                        PyBytes_AS_STRING(normalized), &buffer, buffer.len, 'C'\n                    ) < 0\n                ) {\n                    Py_CLEAR(normalized);\n                }\n"
OLD_SUBJECT_ORDER = b"    if (!callback) {\n        Py_ssize_t validation_length = 0;\n        if (PyUnicode_Check(value)) {\n            validation_length = PyUnicode_GET_LENGTH(value);\n        } else if (PyBytes_Check(value)) {\n            validation_length = PyBytes_GET_SIZE(value);\n        } else if (PyByteArray_Check(value)) {\n            validation_length = PyByteArray_GET_SIZE(value);\n        }\n        if (rust_replacement_cache(pattern, templates, replacement, value, validation_length, &raw, &tokens) < 0) {\n            Py_XDECREF(raw);\n            Py_XDECREF(tokens);\n            return NULL;\n        }\n    }\n    if (!rust_subject_open(&subject, pattern_value, value, 1)) {\n        Py_XDECREF(raw);\n        Py_XDECREF(tokens);\n        return NULL;\n    }\n    int deferred = callback || (tokens == Py_None && !PyUnicode_Check(raw) && !PyBytes_Check(raw));\n    if (limit < 0) {\n        PyObject *unchanged = rust_sub_unchanged(&subject);\n        Py_XDECREF(raw);\n        Py_XDECREF(tokens);\n        rust_subject_release(&subject);\n        Py_XDECREF(subject_snapshot);\n        return rust_sub_result(unchanged, 0, want_count);\n    }\n    if (!callback && subject.view.obj != NULL) {\n        if (subject.length > (size_t)PY_SSIZE_T_MAX) {\n            Py_XDECREF(raw);\n            Py_XDECREF(tokens);\n            rust_subject_release(&subject);\n            return PyErr_NoMemory();\n        }\n        subject_snapshot = PyBytes_FromStringAndSize(\n            (const char *)subject.data, (Py_ssize_t)subject.length\n        );\n        if (subject_snapshot == NULL) {\n            Py_XDECREF(raw);\n            Py_XDECREF(tokens);\n            rust_subject_release(&subject);\n            return NULL;\n        }\n        rust_subject_release(&subject);\n        if (!rust_subject_open(&subject, pattern_value, subject_snapshot, 1)) {\n            Py_XDECREF(raw);\n            Py_XDECREF(tokens);\n            rust_subject_release(&subject);\n            Py_DECREF(subject_snapshot);\n            return NULL;\n        }\n    }\n\n"
SAFE_SUBJECT_ORDER = b"    if (!rust_subject_open(&subject, pattern_value, value, 1)) {\n        return NULL;\n    }\n    if (!callback && subject.view.obj != NULL) {\n        if (subject.length > (size_t)PY_SSIZE_T_MAX) {\n            rust_subject_release(&subject);\n            return PyErr_NoMemory();\n        }\n        subject_snapshot = PyBytes_FromStringAndSize(\n            (const char *)subject.data, (Py_ssize_t)subject.length\n        );\n        if (subject_snapshot == NULL) {\n            rust_subject_release(&subject);\n            return NULL;\n        }\n        rust_subject_release(&subject);\n        if (!rust_subject_open(&subject, pattern_value, subject_snapshot, 1)) {\n            rust_subject_release(&subject);\n            Py_DECREF(subject_snapshot);\n            return NULL;\n        }\n    }\n    if (!callback) {\n        if (subject.length > (size_t)PY_SSIZE_T_MAX) {\n            rust_subject_release(&subject);\n            Py_XDECREF(subject_snapshot);\n            return PyErr_NoMemory();\n        }\n        Py_ssize_t validation_length = (Py_ssize_t)subject.length;\n        if (\n            rust_replacement_cache(\n                pattern, templates, replacement, value,\n                validation_length, &raw, &tokens\n            ) < 0\n        ) {\n            Py_XDECREF(raw);\n            Py_XDECREF(tokens);\n            rust_subject_release(&subject);\n            Py_XDECREF(subject_snapshot);\n            return NULL;\n        }\n    }\n    int deferred = callback || (\n        tokens == Py_None && !PyUnicode_Check(raw) && !PyBytes_Check(raw)\n    );\n    if (limit < 0) {\n        PyObject *unchanged = rust_sub_unchanged(&subject);\n        Py_XDECREF(raw);\n        Py_XDECREF(tokens);\n        rust_subject_release(&subject);\n        Py_XDECREF(subject_snapshot);\n        return rust_sub_result(unchanged, 0, want_count);\n    }\n\n"


class FreezeError(Exception):
    """The independently pinned, source-only Rust repair failed closed."""


_AUDIT_INSTALLED = False
_BLOCKED_AUDIT_EVENTS: dict[str, int] = {}


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def no_engine_imports() -> None:
    require("re" not in sys.modules and "_sre" not in sys.modules,
            "the source verifier imported a Python regex engine")
    require(not any(name == "rebar" or name.startswith("rebar.") or
                    name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "the source verifier imported an entrypoint or candidate")


def source_paths() -> frozenset[str]:
    result = {ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
              ROOT + "/" + CONTRACT, ROOT + "/" + VARIANT}
    for _name, path, _sha256, _size in OWNERS:
        result.add(path if path.startswith("/") else ROOT + "/" + path)
    return frozenset(result)


def block(event: str, reason: str) -> None:
    _BLOCKED_AUDIT_EVENTS[event] = _BLOCKED_AUDIT_EVENTS.get(event, 0) + 1
    raise FreezeError("Rust buffer-shape source-only wall blocked " + event +
                      ": " + reason)


def source_audit_hook(event: str, arguments: tuple[object, ...]) -> None:
    if event == "open":
        path = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        if type(path) is not str or path not in source_paths():
            block(event, "reads are restricted to exact frozen plaintext owners")
        if path.endswith(".gz"):
            block(event, "compressed archives are never opened")
        if type(flags) is not int:
            block(event, "only exact descriptor-backed read-only opens are allowed")
        forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC |
                     os.O_APPEND | getattr(os, "O_TMPFILE", 0))
        if flags & forbidden:
            block(event, "source-freeze writes are forbidden")
        return
    if event == "compile":
        raw = arguments[0] if arguments else None
        label = arguments[1] if len(arguments) > 1 else None
        if (label not in {
            "tools/apply_owned_rust_source_repair_v1.py",
            "tools/apply_owned_rust_public_contract_source_repair_v3.py",
            "<rust-buffer-shape-self-test>",
        } or type(raw) not in (str, bytes) or len(raw) > MAX_JSON_BYTES):
            block(event, "only bounded, authenticated historical Python AST is allowed")
        return
    if event == "import":
        block(event, "imports are forbidden after the clean bootstrap")
    if (event == "exec" or event.startswith("ctypes.") or
            event.startswith("subprocess.") or event.startswith("socket.") or
            event.startswith("multiprocessing.") or event.startswith("threading.") or
            event.startswith("time.") or event in {
                "os.system", "os.fork", "os.forkpty", "os.posix_spawn",
                "os.spawn", "os.exec", "os.chdir", "os.putenv", "os.unsetenv",
                "os.remove", "os.rename", "os.replace", "os.mkdir", "os.rmdir",
                "os.symlink", "os.link", "os.chmod", "os.chown", "os.truncate",
                "os.utime", "code.__new__", "function.__new__", "marshal.loads",
            }):
        block(event, "execution, native loading, processes, clocks and mutation are forbidden")


def install_audit_wall() -> None:
    global _AUDIT_INSTALLED
    require(not _AUDIT_INSTALLED, "the physical source wall was installed twice")
    no_engine_imports()
    sys.addaudithook(source_audit_hook)
    _AUDIT_INSTALLED = True
    no_engine_imports()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def quote(value: str) -> str:
    require(type(value) is str, "canonical JSON requires string object keys")
    escaped = {'"': '\\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for char in value:
        point = ord(char)
        if char in escaped:
            result.append(escaped[char])
        elif point < 0x20:
            result.append("\\u" + format(point, "04x"))
        else:
            require(not 0xD800 <= point <= 0xDFFF,
                    "canonical JSON rejects unpaired Unicode surrogates")
            result.append(char)
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "canonical JSON exceeded its depth limit")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quote(value)
    if type(value) is int:
        return str(value)
    if type(value) is float:
        require(value == value and abs(value) != float("inf"),
                "canonical JSON rejects nonfinite numbers")
        return repr(value)
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1)
                               for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value),
                "canonical JSON rejects non-string object keys")
        return "{" + ",".join(quote(key) + ":" +
                               canonical(value[key], depth + 1)
                               for key in sorted(value)) + "}"
    raise FreezeError("unsupported canonical JSON value")


class StrictJSON:
    """Bounded, duplicate-key-free JSON without importing json or re."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_JSON_BYTES,
                "JSON exceeds the bounded plaintext allowance")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("JSON must be strictly valid UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"',
                "a quoted JSON string is required")
        self.index += 1
        result: list[str] = []
        short = {'"': '"', "\\": "\\", "/": "/", "b": "\b",
                 "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(result)
            if char != "\\":
                require(ord(char) >= 0x20 and
                        not 0xD800 <= ord(char) <= 0xDFFF,
                        "a raw JSON control character or surrogate is forbidden")
                result.append(char)
                continue
            require(self.index < len(self.text), "incomplete JSON string escape")
            char = self.text[self.index]
            self.index += 1
            if char != "u":
                require(char in short, "unknown JSON string escape")
                result.append(short[char])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and all(
                item in "0123456789abcdefABCDEF" for item in digits),
                "invalid JSON Unicode escape")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "an unpaired JSON high surrogate is forbidden")
                low_digits = self.text[self.index + 2:self.index + 6]
                require(len(low_digits) == 4 and all(
                    item in "0123456789abcdefABCDEF" for item in low_digits),
                    "invalid JSON low surrogate")
                low = int(low_digits, 16)
                require(0xDC00 <= low <= 0xDFFF,
                        "an unpaired JSON high surrogate is forbidden")
                self.index += 6
                result.append(chr(0x10000 + ((point - 0xD800) << 10) +
                                  low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF,
                        "an unpaired JSON low surrogate is forbidden")
                result.append(chr(point))
        raise FreezeError("unterminated JSON string")

    def number(self) -> int | float:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text) or
                    self.text[self.index] not in "0123456789",
                    "JSON numbers cannot have leading zeroes")
        else:
            require(self.text[self.index] in "123456789", "invalid JSON number")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        floating = False
        if self.text[self.index:self.index + 1] == ".":
            floating = True
            self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "incomplete JSON fraction")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            floating = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "incomplete JSON exponent")
        token = self.text[start:self.index]
        require(len(token) <= 128, "JSON number exceeds the frozen bound")
        if not floating:
            return int(token)
        result = float(token)
        require(result == result and abs(result) != float("inf"),
                "nonfinite JSON number")
        return result

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "JSON exceeds its nesting limit")
        self.whitespace()
        require(self.index < len(self.text), "missing JSON value")
        char = self.text[self.index]
        if char == '"':
            return self.string()
        if char == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "duplicate JSON object key: " + key)
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "missing JSON member colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "invalid JSON object separator")
        if char == "[":
            self.index += 1
            result_list: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result_list
            while True:
                result_list.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result_list
                require(separator == ",", "invalid JSON array separator")
        if char == "-" or char in "0123456789":
            return self.number()
        for literal, result in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return result
        raise FreezeError("unrecognized JSON literal")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "trailing JSON document")
        return result


def read_exact(path: str, expected_hash: str, expected_size: int) -> bytes:
    require(type(path) is str and type(expected_size) is int and
            0 < expected_size <= MAX_OWNER_BYTES,
            "a bounded exact source owner was substituted")
    absolute = path if path.startswith("/") else ROOT + "/" + path
    require(absolute in source_paths() and not absolute.endswith(".gz"),
            "archive and unlisted owner reads are forbidden")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise FreezeError("cannot read exact plaintext owner: " + path) from error
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_size == expected_size,
                "plaintext owner identity or size changed: " + path)
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1048576, expected_size + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            require(total <= expected_size, "plaintext owner grew: " + path)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    require(total == expected_size and
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
            "plaintext owner changed while authenticated: " + path)
    raw = b"".join(chunks)
    require(digest(raw) == expected_hash, "plaintext owner digest changed: " + path)
    return raw


def read_dynamic(path: str, expected_hash: str) -> bytes:
    absolute = ROOT + "/" + path
    require(absolute in source_paths() and not absolute.endswith(".gz"),
            "dynamic owner must be frozen uncompressed source")
    try:
        info = os.stat(absolute, follow_symlinks=False)
    except OSError as error:
        raise FreezeError("required source-freeze owner is missing: " + path) from error
    require(stat.S_ISREG(info.st_mode), "source-freeze owner must be a regular file")
    return read_exact(path, expected_hash, info.st_size)


def replace_once(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    require(type(raw) is bytes and type(old) is bytes and type(new) is bytes,
            "source repair accepts bytes only")
    require(old != new and raw.count(old) == 1,
            "source repair requires one authentic anchor: " + label)
    return raw.replace(old, new, 1)


def byte_assignments(raw: bytes, path: str,
                     required: tuple[str, ...]) -> dict[str, bytes]:
    try:
        tree = ast.parse(raw, filename=path)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise FreezeError("historical source cannot be parsed as bounded AST") from error
    pending: list[ast.AST] = [tree]
    seen = 0
    while pending:
        node = pending.pop()
        seen += 1
        require(seen <= 50000, "historical source exceeded its AST allowance")
        pending.extend(ast.iter_child_nodes(node))
    found: dict[str, bytes] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in required:
                require(target.id not in found and
                        isinstance(node.value, ast.Constant) and
                        type(node.value.value) is bytes,
                        "historical repair must expose one literal byte anchor")
                found[target.id] = node.value.value
    require(set(found) == set(required),
            "historical repair byte-literal anchors are incomplete")
    return found


def corrected_bridge(source: bytes, repair_source: bytes) -> bytes:
    names = byte_assignments(
        repair_source, "tools/apply_owned_rust_source_repair_v1.py",
        ("OLD_BLOCK", "NEW_BLOCK"),
    )
    fixed = replace_once(source, names["OLD_BLOCK"], names["NEW_BLOCK"],
                         "actual-v13-historical-first-party-bridge")
    require(len(fixed) == ACTUAL_BRIDGE_BYTES and
            digest(fixed) == ACTUAL_BRIDGE_SHA256,
            "the actual V13 corrected Rust bridge did not reproduce")
    return fixed


def corrected_adapter(source: bytes, repair_source: bytes) -> bytes:
    names = byte_assignments(
        repair_source, "tools/apply_owned_rust_public_contract_source_repair_v3.py",
        ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "OLD_ERROR_BLOCK",
         "V2_ERROR_BLOCK", "OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK",
         "V3_PATTERN_BLOCK"),
    )
    fixed = source
    for old, new, label in (
        ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "first-party-V2-flags"),
        ("OLD_ERROR_BLOCK", "V2_ERROR_BLOCK", "first-party-V2-pattern-error"),
        ("OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK", "first-party-V2-pattern-value"),
        ("V2_PATTERN_BLOCK", "V3_PATTERN_BLOCK", "actual-V13-first-party-adapter"),
    ):
        fixed = replace_once(fixed, names[old], names[new], label)
    require(len(fixed) == ACTUAL_ADAPTER_BYTES and
            digest(fixed) == ACTUAL_ADAPTER_SHA256,
            "the actual V13 corrected Rust public adapter did not reproduce")
    return fixed


def derive_variant(actual: bytes) -> bytes:
    require(len(actual) == ACTUAL_BRIDGE_BYTES and
            digest(actual) == ACTUAL_BRIDGE_SHA256,
            "buffer repair must start from the actually tested V13 bridge")
    fixed = replace_once(actual, HELPER_ANCHOR,
                         HELPER + HELPER_ANCHOR, "owned original-error restoration")
    for old, new, label in (
        (OLD_CACHE_DECLARATION, NEW_CACHE_DECLARATION, "single observed original hash"),
        (OLD_BUFFER_MATERIALIZATION, NEW_BUFFER_MATERIALIZATION,
         "observable buffer acquisition and hash order"),
        (OLD_HASH, NEW_HASH, "do not repeat original replacement hashing"),
        (OLD_TEMPLATE_FAILURE, NEW_TEMPLATE_FAILURE,
         "restore replacement error from original exporter"),
        (OLD_EXPANSION_FAILURE, NEW_EXPANSION_FAILURE,
         "restore original match-expansion template error"),
        (OLD_CAPTURE, NEW_CAPTURE, "check fresh capture buffer bounds"),
    ):
        fixed = replace_once(fixed, old, new, label)
    start = fixed.find(SUBSTITUTION_START)
    require(start >= 0 and fixed.count(SUBSTITUTION_START) == 1,
            "the first-party substitution implementation must be unique")
    stop = fixed.find(SUBSTITUTION_END, start + len(SUBSTITUTION_START))
    require(stop > start and fixed.count(SUBSTITUTION_END) == 1,
            "the first-party substitution boundary must be unique")
    function = fixed[start:stop]
    old_local = b"    PyObject *raw = NULL;\n    PyObject *tokens = NULL;\n"
    new_local = old_local + b"    PyObject *subject_snapshot = NULL;\n"
    function = replace_once(function, old_local, new_local,
                            "one owned substitution subject snapshot")
    lines: list[bytes] = []
    released = 0
    for line in function.splitlines(keepends=True):
        body = line.lstrip(b" \t")
        if body == b"rust_subject_release(&subject);\n":
            prefix = line[:len(line) - len(body)]
            lines.append(line)
            lines.append(prefix + b"Py_XDECREF(subject_snapshot);\n")
            released += 1
        else:
            lines.append(line)
    require(released == 6, "all six existing subject cleanups must remain balanced")
    function = b"".join(lines)
    function = replace_once(function, SNAPSHOT_ANCHOR,
                            SNAPSHOT_INSERTION + SNAPSHOT_ANCHOR,
                            "snapshot a live, owned noncallback subject")
    fixed = fixed[:start] + function + fixed[stop:]
    fixed = replace_once(fixed, UNSAFE_CONTIGUOUS_COPY, SAFE_CONTIGUOUS_COPY,
                         "copy possibly strided FULL_RO buffers safely")
    fixed = replace_once(fixed, OLD_SUBJECT_ORDER, SAFE_SUBJECT_ORDER,
                         "acquire and snapshot the subject before hashing replacement")
    require(len(fixed) == VARIANT_BYTES and digest(fixed) == VARIANT_SHA256,
            "the complete reviewed buffer-shape source variant did not reproduce")
    require(fixed.count(b"rust_restore_original_template_error(") == 3 and
            fixed.count(b"PyBuffer_ToContiguous(") >= 1 and
            fixed.count(b"PyBUF_FULL_RO") >= 1,
            "general original-error and strided-buffer protections are missing")
    for marker in (b"__reduce__", b"__reduce_ex__"):
        require(fixed.count(marker) == actual.count(marker),
                "the separate match-pickling source feature must remain untouched")
    for forbidden in (
        b"import re\n", b"from re import", b"import _sre", b"from _sre",
        b"regex.compile", b"pcre", b"oniguruma", b"candidates.vm_candidate",
        b"candidates.zig_candidate", b"candidates.cpp_candidate",
        b"candidates.go_candidate", b"candidates.fortran_candidate",
    ):
        require(fixed.count(forbidden) == actual.count(forbidden),
                "a delegated or cross-family regex engine was introduced")
    return fixed


def owner_mapping() -> dict[str, dict[str, object]]:
    return {name: {"path": path, "sha256": sha256, "bytes": size}
            for name, path, sha256, size in OWNERS}


def validate_overview(value: object, label: str) -> None:
    require(type(value) is dict, "V48 overview must be a JSON object: " + label)
    expected = {
        "version": 48, "full_case_denominator": 31237,
        "suite_count": 13, "private_waiver_count": 13,
        "authenticated_evidence_owner_lower_bound": 168,
        "authenticated_history_reference_lower_bound": 173,
        "first_party_source_inventory_family_count": 6,
        "frozen_corrected_runner_source_family_count": 3,
        "qualified_candidate_count": 0,
        "actual_rust_semantic_mismatch_count": 928,
        "actual_rust_candidate_workers": 13,
        "actual_rust_distinct_worker_process_id_count": 13,
        "actual_rust_completed_suite_count": 13,
        "actual_rust_publication_receipt_sha256":
            "b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943",
    }
    for key, expected_value in expected.items():
        require(value.get(key) == expected_value,
                "actual V48 evidence changed: " + label + "." + key)
    campaign = value.get("actual_complete_rust_v7_campaign")
    require(type(campaign) is dict, "actual Rust V7 campaign is missing")
    for key, expected_value in {
        "status": "FAIL", "candidate_status": "FAIL",
        "semantic_mismatch_count": 928, "verified_passing_case_count": 8965,
        "verified_passing_cases_derived_by_subtraction": False,
        "case_execution_denominator": 31237, "completed_suite_count": 13,
        "distinct_worker_process_id_count": 13, "infrastructure_failure_count": 0,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "winner_selected": False, "candidate_qualified": False,
        "corrected_bridge_source_sha256": ACTUAL_BRIDGE_SHA256,
        "corrected_public_adapter_sha256": ACTUAL_ADAPTER_SHA256,
    }.items():
        require(campaign.get(key) == expected_value,
                "actual Rust V7 evidence changed: " + key)
    archive = campaign.get("archive")
    require(type(archive) is dict and all(
        archive.get(key) is False for key in (
            "content_opened_by_graph", "content_read_by_graph",
            "content_sha256_recomputed_by_graph", "archive_inflated_by_graph",
        )), "V48 must not open, read, inflate, or hash a failure archive")


def validate_context() -> tuple[bytes, bytes]:
    observed: dict[str, bytes] = {}
    for name, path, sha256, size in OWNERS:
        observed[name] = read_exact(path, sha256, size)
    matrix = StrictJSON(observed["original_p0_matrix"]).decode()
    require(type(matrix) is dict and matrix.get("schema") ==
            "rebar-cpython-re-p0-completeness-v1" and
            type(matrix.get("denominator")) is dict and
            matrix["denominator"].get("final_required_case_execution_denominator") == 31237 and
            type(matrix.get("suites")) is list and len(matrix["suites"]) == 13 and
            type(matrix.get("phase_gate")) is dict and
            matrix["phase_gate"].get("status") == "PASS",
            "the original frozen 31,237-case correctness oracle changed")
    family = StrictJSON(observed["first_party_family_inventory"]).decode()
    require(type(family) is dict and family.get("family_count") == 6 and
            type(family.get("families")) is list and len(family["families"]) == 6,
            "the independent first-party family inventory changed")
    large = StrictJSON(observed["large_input_supplement"]).decode()
    public = StrictJSON(observed["public_entrypoint_supplement"]).decode()
    callable_matrix = StrictJSON(observed["callable_introspection_supplement"]).decode()
    require(type(large) is dict and type(large.get("case_matrix")) is list and
            len(large["case_matrix"]) == 32 and
            type(large.get("actual_candidate_large_input")) is dict and
            large["actual_candidate_large_input"].get("full_resource_large_search") == "NOT RUN" and
            large["actual_candidate_large_input"].get("full_resource_large_subn") == "NOT RUN",
            "the 32 separate full-resource large-input obligations changed")
    require(type(public) is dict and type(public.get("case_matrix")) is list and
            len(public["case_matrix"]) == 32 and
            type(public.get("boundaries")) is dict and
            public["boundaries"].get("observed_public_entrypoint_status") == "FAIL",
            "the 32 separate public-import observations changed")
    require(type(callable_matrix) is dict and
            type(callable_matrix.get("additional_obligation")) is dict and
            callable_matrix["additional_obligation"].get("case_count") == 50 and
            callable_matrix["additional_obligation"].get(
                "included_in_original_31237_denominator") is False,
            "the 50 separate callable-introspection obligations changed")
    receipt = StrictJSON(observed["actual_v7_small_plaintext_receipt"]).decode()
    require(type(receipt) is dict, "the small genuine V7 receipt must be an object")
    for key, expected in {
        "schema": "rebar-owned-repaired-rust-original-campaign-v7-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS", "candidate_status": "FAIL",
        "semantic_mismatch_count": 928, "verified_passing_case_count": 8965,
        "case_execution_denominator": 31237, "suite_count": 13,
        "completed_suite_count": 13, "actual_candidate_workers": 13,
        "distinct_worker_process_id_count": 13, "infrastructure_failure_count": 0,
        "corrected_bridge_source_sha256": ACTUAL_BRIDGE_SHA256,
        "corrected_public_adapter_sha256": ACTUAL_ADAPTER_SHA256,
        "actual_v13_build_receipt_sha256":
            "4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805",
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "winner_selected": False, "candidate_qualified": False,
    }.items():
        require(receipt.get(key) == expected,
                "the durable actual Rust failure receipt changed: " + key)
    require(type(receipt.get("actual_worker_process_ids")) is list and
            len(receipt["actual_worker_process_ids"]) == 13 and
            len(set(receipt["actual_worker_process_ids"])) == 13,
            "the actual 13 distinct Rust worker identities changed")
    build = StrictJSON(observed["actual_v13_small_plaintext_build_receipt"]).decode()
    require(type(build) is dict, "the small V13 build receipt must be an object")
    for key, expected in {
        "schema": "rebar-phase2-owned-rust-pattern-repr-source-build-v13-durable-publication-receipt",
        "status": "PASS", "build_status": "PASS",
        "label": "phase2-v13-rust-pattern-repr-original-p0",
        "bridge_derived_sha256": ACTUAL_BRIDGE_SHA256,
        "public_derived_sha256": ACTUAL_ADAPTER_SHA256,
        "candidate_correctness": "NOT MEASURED", "candidate_processes_started": 0,
        "candidate_imports": 0, "candidate_qualified": False,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "winner_selected": False,
    }.items():
        require(build.get(key) == expected,
                "the actual V13 build provenance changed: " + key)
    for key in ("current_v48_inputs", "current_v48_summary"):
        validate_overview(StrictJSON(observed[key]).decode(), key)
    actual = corrected_bridge(observed["canonical_rust_bridge"],
                              observed["historical_rust_bridge_derivation"])
    adapter = corrected_adapter(observed["canonical_rust_adapter"],
                                observed["historical_rust_adapter_derivation"])
    fixed = derive_variant(actual)
    variant = read_exact(VARIANT, VARIANT_SHA256, VARIANT_BYTES)
    require(fixed == variant, "complete append-only variant differs from exact source derivation")
    require(adapter != observed["canonical_rust_adapter"],
            "historically corrected adapter must remain an in-memory derivation")
    no_engine_imports()
    return actual, fixed


def phase_boundary() -> dict[str, object]:
    return {
        "actual_reference_workers_started": 0,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_public_entrypoint_imports": 0,
        "actual_stdlib_regex_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "actual_clock_samples": 0,
        "actual_holdout_cases_read": 0,
        "actual_hidden_cases_read": 0,
        "workspace_files_written": 0,
        "source_variant_materialized": True,
        "source_variant_built": False,
        "source_variant_candidate_matching": "NOT RUN",
        "source_variant_candidate_correctness": "NOT MEASURED",
        "source_variant_native_undefined_behavior": "NOT MEASURED",
        "source_variant_native_memory": "NOT MEASURED",
        "source_variant_runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "holdout_generated": False,
        "holdout_planned_case_count": 4194304,
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "physical_audit_hook_required": True,
        "physical_audit_denies_unlisted_reads": True,
        "physical_audit_denies_all_archive_reads": True,
        "physical_audit_denies_module_imports": True,
        "physical_audit_denies_native_loading": True,
        "physical_audit_denies_execution_and_processes": True,
        "physical_audit_denies_network_and_writes": True,
    }


def contract_document(source_sha256: str,
                      protocol_sha256: str) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 1,
        "phase": "CANDIDATES",
        "status": STATUS,
        "family": "rust",
        "source": {"path": SOURCE, "sha256": source_sha256},
        "protocol": {"path": PROTOCOL, "sha256": protocol_sha256},
        "candidate_variant": {
            "path": VARIANT, "sha256": VARIANT_SHA256, "bytes": VARIANT_BYTES,
            "same_existing_rust_family": True,
            "adds_candidate_family": False,
            "materialized": True,
            "built": False,
            "candidate_matching": "NOT RUN",
            "correctness": "NOT MEASURED",
            "runtime_no_delegation": "NOT ESTABLISHED",
            "actual_corrected_bridge_sha256": ACTUAL_BRIDGE_SHA256,
        },
        "historical_v13_source_derivation": {
            "actual_corrected_bridge_sha256": ACTUAL_BRIDGE_SHA256,
            "actual_corrected_bridge_bytes": ACTUAL_BRIDGE_BYTES,
            "method": "BOUNDED AST OF HASH-PINNED FIRST-PARTY REPAIR SOURCES ONLY",
            "archive_opened": False,
            "archive_decompressed": False,
            "private_snapshot_required": False,
        },
        "preserved_public_adapter": {
            "actual_corrected_adapter_sha256": ACTUAL_ADAPTER_SHA256,
            "actual_corrected_adapter_bytes": ACTUAL_ADAPTER_BYTES,
            "derived_only_in_memory": True,
            "canonical_adapter_modified": False,
            "runtime_adapter_activated": False,
        },
        "preserved_rust_owners": owner_mapping(),
        "actual_v7_failure": {
            "source": "HASH-PINNED SMALL PLAINTEXT DURABLE RECEIPT",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 928,
            "verified_passing_case_count": 8965,
            "verified_passing_cases_derived_by_subtraction": False,
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "distinct_worker_process_id_count": 13,
            "infrastructure_failure_count": 0,
            "new_matching_run": False,
        },
        "current_v48_overview": {
            "version": 48,
            "authenticated_evidence_owner_lower_bound": 168,
            "authenticated_history_reference_lower_bound": 173,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 3,
            "qualified_candidate_count": 0,
        },
        "original_oracle": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "large_input_supplement_cases": 32,
            "public_import_supplement_cases": 32,
            "callable_introspection_supplement_cases": 50,
            "supplements_added_to_original_denominator": False,
        },
        "historically_reported_buffer_shape_diagnosis": {
            "source": "HISTORICALLY COMMITTED V48 EXPERIMENT LOG; NOT DERIVED FROM THE SMALL DURABLE RECEIPT",
            "historical_committed_log_path": "docs/EXPERIMENT-LOG.md",
            "historical_committed_log_sha256": "bfec908f1689bf940e479688e51b209b6182eed29f50996792507fb2668362db",
            "historical_committed_log_bytes": 1206058,
            "mutable_live_log_read": False,
            "separate_match_serialization_case_count": 32,
            "historical_replacement_and_buffer_order_case_count": 224,
            "historical_match_expansion_and_replacement_shape_case_count": 672,
            "targeted_historically_reported_case_count": 896,
            "case_histogram_rederived_by_this_source_freeze": False,
            "repair_effect": "NOT MEASURED",
            "repairs_verified": "NOT MEASURED",
            "separate_match_serialization_modified": False,
        },
        "phase_boundary": phase_boundary(),
        "future_private_build": {
            "authorized_by_source_freeze": False,
            "candidate_processes_started": 0,
            "build_status": "NOT RUN",
            "correctness": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
        },
    }


def parse_cli() -> tuple[str, dict[str, str]]:
    args = sys.argv[1:]
    require(len(args) >= 1, "exactly one explicit source-only mode is required")
    mode = args[0]
    require(mode in {"--render-contract", "--self-test", "--verify-frozen-context"},
            "unknown source-only mode")
    expected_names = ("--source-sha256", "--protocol-sha256")
    if mode != "--render-contract":
        expected_names += ("--contract-sha256",)
    require(len(args) == 1 + 2 * len(expected_names),
            "all independent owner pins are required exactly once")
    parsed: dict[str, str] = {}
    for offset in range(1, len(args), 2):
        name, value = args[offset], args[offset + 1]
        require(name in expected_names and name not in parsed,
                "an owner pin was unknown or repeated")
        require(len(value) == 64 and all(
            character in "0123456789abcdef" for character in value),
            "owner pins must be exact lowercase SHA-256 values")
        parsed[name] = value
    require(set(parsed) == set(expected_names), "an independent owner pin is missing")
    return mode, parsed


def verify_contract(pins: dict[str, str]) -> dict[str, object]:
    read_dynamic(SOURCE, pins["--source-sha256"])
    read_dynamic(PROTOCOL, pins["--protocol-sha256"])
    expected = contract_document(pins["--source-sha256"],
                                 pins["--protocol-sha256"])
    encoded = (canonical(expected) + "\n").encode("utf-8")
    raw = read_dynamic(CONTRACT, pins["--contract-sha256"])
    require(raw == encoded and StrictJSON(raw).decode() == expected,
            "the exact independently pinned canonical source contract changed")
    return expected


def expect_rejection(label: str, operation: object) -> None:
    try:
        operation()
    except FreezeError:
        return
    raise FreezeError("hostile source-only control was accepted: " + label)


def run_self_tests(actual: bytes, fixed: bytes,
                   expected: dict[str, object]) -> int:
    count = 0
    for old, new, label in (
        (HELPER_ANCHOR, HELPER + HELPER_ANCHOR, "error helper"),
        (OLD_CACHE_DECLARATION, NEW_CACHE_DECLARATION, "hash state"),
        (OLD_BUFFER_MATERIALIZATION, NEW_BUFFER_MATERIALIZATION, "buffer ordering"),
        (OLD_HASH, NEW_HASH, "duplicate original hash"),
        (OLD_TEMPLATE_FAILURE, NEW_TEMPLATE_FAILURE, "replacement error"),
        (OLD_EXPANSION_FAILURE, NEW_EXPANSION_FAILURE, "expansion error"),
        (OLD_CAPTURE, NEW_CAPTURE, "capture bounds"),
    ):
        for mutation, suffix in (
            (actual.replace(old, b"", 1), "missing"),
            (actual.replace(old, old + old, 1), "duplicate"),
        ):
            expect_rejection(label + "/" + suffix,
                             lambda value=mutation: derive_variant(value))
            count += 1
    for marker, replacement, label in (
        (b"PyBuffer_ToContiguous(", b"PyBuffer_ToRawPointer(", "unsafe strided copy"),
        (b"PyBUF_FULL_RO", b"PyBUF_SIMPLE", "lost FULL_RO fallback"),
        (b"rust_restore_original_template_error(",
         b"rust_ignore_original_template_error(", "lost original template error"),
        (b"PyObject_Length(replacement)", b"PyObject_SizeIgnoringReplacement(replacement)",
         "lost observable original template length"),
        (b"Py_XDECREF(subject_snapshot);", b"/* snapshot reference leaked */",
         "lost snapshot cleanup"),
        (b"if (end > capture.length)", b"if (end > SIZE_MAX)",
         "lost fresh capture bound"),
        (b"if (!callback && subject.view.obj != NULL)",
         b"if (callback && subject.view.obj != NULL)",
         "snapshotted the callback subject"),
    ):
        hostile = fixed.replace(marker, replacement, 1)
        require(hostile != fixed, "a hostile source control marker vanished: " + label)
        expect_rejection(label, lambda value=hostile:
                         require(value == derive_variant(actual), label))
        count += 1
    for key, wrong in (
        ("case_execution_denominator", 31236),
        ("case_execution_denominator", 31238),
        ("semantic_mismatch_count", 0),
        ("semantic_mismatch_count", 896),
        ("verified_passing_case_count", 31237 - 928),
        ("candidate_status", "PASS"),
        ("winner_selected", True),
        ("candidate_qualified", True),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
    ):
        campaign = dict(expected["actual_v7_failure"])
        if key in campaign:
            campaign[key] = wrong
            hostile = dict(expected)
            hostile["actual_v7_failure"] = campaign
        else:
            boundary = dict(expected["phase_boundary"])
            boundary[key] = wrong
            hostile = dict(expected)
            hostile["phase_boundary"] = boundary
        expect_rejection("fabricated evidence/" + key,
                         lambda value=hostile: require(value == expected,
                                                       "fabricated source evidence"))
        count += 1
    malformed = (
        b'{"x":1,"x":2}', b'{"x":01}', b'{"x":NaN}',
        b'{"x":"\\uD800"}', b'{"x":"\\uDC00"}',
        b'{"x":1}{"x":2}', b'{"x":1,}', b'["x",]',
    )
    for raw in malformed:
        expect_rejection("strict JSON", lambda value=raw: StrictJSON(value).decode())
        count += 1
    physical = (
        ("unlisted read", lambda: builtins.open("/etc/hosts", "r")),
        ("compressed failure archive", lambda: builtins.open(
            ROOT + "/oracle/phase2/evidence/"
            "repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-"
            "original-p0-failures.json.gz", "rb")),
        ("holdout read", lambda: builtins.open(ROOT + "/benchmarks/holdout.json", "rb")),
        ("candidate import", lambda: sys.audit("import", "candidates.rust_candidate",
                                                None, None, None, None)),
        ("stdlib engine import", lambda: sys.audit("import", "_sre",
                                                   None, None, None, None)),
        ("native load", lambda: sys.audit("ctypes.dlopen", "forbidden-native.so")),
        ("subprocess", lambda: sys.audit("subprocess.Popen", "rustc", (), None, None)),
        ("network", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("code execution", lambda: sys.audit("exec", "forbidden-code")),
        ("workspace rename", lambda: sys.audit("os.rename", "a", "b", -1, -1)),
        ("clock", lambda: sys.audit("time.monotonic",)),
        ("source write", lambda: builtins.open(ROOT + "/" + SOURCE, "w")),
    )
    for label, operation in physical:
        expect_rejection("physical audit/" + label, operation)
        count += 1
    require(sum(_BLOCKED_AUDIT_EVENTS.values()) >= len(physical),
            "physical hostile controls were not denied by the irrevocable audit wall")
    no_engine_imports()
    return count


def main() -> int:
    mode, pins = parse_cli()
    install_audit_wall()
    read_dynamic(SOURCE, pins["--source-sha256"])
    read_dynamic(PROTOCOL, pins["--protocol-sha256"])
    if mode == "--render-contract":
        result = canonical(contract_document(pins["--source-sha256"],
                                             pins["--protocol-sha256"]))
        sys.stdout.write(result + "\n")
        no_engine_imports()
        return 0
    expected = verify_contract(pins)
    actual, fixed = validate_context()
    if mode == "--self-test":
        controls = run_self_tests(actual, fixed, expected)
        result = {"status": "PASS", "mode": "self-test",
                  "source_only_controls": controls,
                  "physical_audit_controls": 12,
                  "variant_sha256": VARIANT_SHA256,
                  "candidate_matching": "NOT RUN",
                  "performance": "NOT MEASURED", "holdout": "NOT OPENED"}
    else:
        no_engine_imports()
        result = {"status": "PASS", "mode": "verify-frozen-context",
                  "authenticated_plaintext_owner_count": len(OWNERS) + 4,
                  "variant_sha256": VARIANT_SHA256,
                  "actual_rust_status": "FAIL",
                  "actual_rust_semantic_mismatch_count": 928,
                  "actual_rust_verified_passing_case_count": 8965,
                  "full_case_denominator": 31237,
                  "suite_count": 13,
                  "candidate_matching": "NOT RUN",
                  "performance": "NOT MEASURED", "holdout": "NOT OPENED"}
    sys.stdout.write(canonical(result) + "\n")
    no_engine_imports()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, RecursionError,
            OverflowError) as error:
        sys.stderr.write("FAIL: " + str(error) + "\n")
        raise SystemExit(1)
