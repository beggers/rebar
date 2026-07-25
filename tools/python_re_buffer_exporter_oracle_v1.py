#!/usr/bin/env python3
"""Frozen, candidate-free CPython 3.14.6 PEP 688 regex lifetime oracle.

The source-only self-test never runs an original reference, imports a
candidate, reads evidence, writes a report, starts a worker, or times code.
Only an explicitly root-invoked self-oracle may run two fresh independently
isolated standard-library reference workers.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
import gc
import hashlib
import importlib
import io
import json
import locale
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Iterator, Mapping
import weakref


ROOT = Path(os.path.abspath(__file__)).parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-python-re-pep688-buffer-exporter-v1"
SOURCE_RELATIVE = "tools/python_re_buffer_exporter_oracle_v1.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V1.md"
PROTOCOL_SHA256 = (
    "30587b78d2752f9e9a1eeeaa4cef89e09ad75ccd39989bd5eb2d84f136c99dad"
)
ORIGINAL_TEST_RELATIVE = "oracle/cpython-3.14.6/test_re.py"
ORIGINAL_TEST_SHA256 = (
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
)
V6_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v6.py"
V6_SOURCE_SHA256 = (
    "b1522b55b37de2e004b029c128e2e75c3020cda34165bcf0de07cb5ebb3136cb"
)
V6_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V6.md"
V6_PROTOCOL_SHA256 = (
    "8e43ceaa61f6e70e2e1193de71bde8583c101cdbe40bc78d862ae789531aff57"
)
V6_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
)
V6_REFERENCE_SHA256 = (
    "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
)
V27_SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage27.py"
V27_SOURCE_SHA256 = (
    "fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b"
)
V27_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md"
V27_PROTOCOL_SHA256 = (
    "c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f"
)
PUBLIC_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v19-self-oracle.json"
)
PUBLIC_REFERENCE_SHA256 = (
    "a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8"
)
PUBLIC_RECORD_SHA256 = (
    "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef"
)
ORIGINAL_MATRIX_SHA256 = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
MATRIX_SHA256 = (
    "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891"
)
REFERENCE_LABELS = ("reference_a", "reference_b")
ORIGINAL_METHOD_COUNT = 165
PUBLIC_METHOD_COUNT = 152
PRIVATE_WAIVER_COUNT = 13
PRIVATE_METHOD_NAMES = (
    "DebugTests.test_debug_flag",
    "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one",
    "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable",
    "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness",
    "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules",
    "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc",
    "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
AUTHENTIC_PRIVATE_CLASS_WAIVERS = {
    "DebugTests": {
        "methods": 4,
        "reason": "CPython-only textual disassembly of private matching opcodes",
    },
    "ImplementationTest": {
        "methods": 9,
        "reason": (
            "private CPython regex compiler, _sre, type internals, "
            "and deprecated private implementation modules"
        ),
    },
}
PUBLIC_CASE_COUNT = 1_376
PUBLIC_COHORT_COUNT = 43
BUFFER_CASE_COUNT = 264
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_REFERENCE_BYTES = 32 * 1024 * 1024
MAX_WORKER_BYTES = 16 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 120

CARRIERS = (
    ("direct-mutable", False, False),
    ("direct-readonly", False, True),
    ("wrapped-mutable", True, False),
    ("wrapped-readonly", True, True),
)
OPERATIONS = (
    "module.search", "module.match", "module.fullmatch", "module.findall",
    "module.finditer", "module.split", "module.sub", "module.subn",
    "pattern.search", "pattern.match", "pattern.fullmatch", "pattern.findall",
    "pattern.finditer", "pattern.split", "pattern.sub", "pattern.subn",
    "pattern.scanner", "match.group", "scanner.scan",
)
CALLBACK_OPERATIONS = (
    "module.sub", "module.subn", "pattern.sub", "pattern.subn",
    "scanner.scan",
)
RETAINED_OPERATIONS = (
    "module.finditer", "pattern.finditer", "pattern.scanner", "match.group",
)
SUCCESS_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v1-self-oracle.json"
)
FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v1-self-oracle-failures.json"
)
SUCCESS_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v1-self-oracle-publication-receipt.json"
)
FAILURE_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v1-self-oracle-failure-publication-receipt.json"
)
APPROVED_OUTPUTS = frozenset({
    SUCCESS_RELATIVE, FAILURE_RELATIVE,
    SUCCESS_RECEIPT_RELATIVE, FAILURE_RECEIPT_RELATIVE,
})


class BufferExporterOracleError(Exception):
    """Fail closed without concealing an actual reference observation."""


class SourceOnlyBoundaryError(BufferExporterOracleError):
    """A source-only test attempted an actual external effect."""


class CallbackProbeError(Exception):
    """Genuine, deliberately observed replacement/scanner callback error."""


class ActualReferenceWorkerFailure(BufferExporterOracleError):
    """Retain real subprocess streams and only genuinely completed roles."""

    def __init__(self, message: str, details: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BufferExporterOracleError(message)


def canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("ascii") + b"\n"
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_sha256(value: Any) -> bool:
    return (
        type(value) is str and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
        and len(set(value)) > 1
    )


def build_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(scenario: str, operation: str, carrier: tuple[str, bool, bool]) -> None:
        rows.append({
            "case": "buffer-exporter.v1." + format(len(rows), "03d"),
            "scenario": scenario,
            "operation": operation,
            "carrier": carrier[0],
            "wrapped": carrier[1],
            "readonly": carrier[2],
        })

    for scenario in ("success", "no-match", "repeat"):
        for operation in OPERATIONS:
            for carrier in CARRIERS:
                add(scenario, operation, carrier)
    for operation in CALLBACK_OPERATIONS:
        for carrier in CARRIERS:
            add("callback-error", operation, carrier)
    for operation in RETAINED_OPERATIONS:
        for carrier in CARRIERS:
            add("retained", operation, carrier)
    return rows


def validate_matrix(rows: Any) -> str:
    require(type(rows) is list and len(rows) == BUFFER_CASE_COUNT,
            "all 264 original PEP 688 cases are mandatory")
    require(rows == build_matrix(),
            "a PEP 688 operation, carrier, scenario, or source order changed")
    require(digest(rows) == MATRIX_SHA256,
            "the frozen 264-case buffer-exporter matrix changed")
    require(len({row["case"] for row in rows}) == BUFFER_CASE_COUNT,
            "a real exporter case was duplicated")
    return MATRIX_SHA256


class PoisonOnReleaseExporter:
    """Only overwrite still-owned storage; never resize or release memory."""

    def __init__(self, payload: bytes, readonly: bool) -> None:
        require(type(payload) is bytes and type(readonly) is bool,
                "an actual immutable exporter setup is required")
        self.storage = bytearray(payload)
        self.readonly = readonly
        self.events: list[list[Any]] = []
        self.acquisitions = 0
        self.releases = 0

    def __buffer__(self, flags: int) -> memoryview:
        require(type(flags) is int,
                "Python must supply the actual integer buffer-request flags")
        self.acquisitions += 1
        self.events.append([
            "acquire", self.acquisitions, flags,
            self.readonly, bytes(self.storage).hex(),
        ])
        result = memoryview(self.storage)
        return result.toreadonly() if self.readonly else result

    def __release_buffer__(self, view: memoryview) -> None:
        require(isinstance(view, memoryview),
                "Python must deliver the actual acquired buffer view")
        self.releases += 1
        before = bytes(self.storage).hex()
        for index in range(len(self.storage)):
            self.storage[index] = 0x21
        self.events.append([
            "release", self.releases, before, bytes(self.storage).hex(),
        ])


def safe_relative(relative: Any, *, output: bool = False) -> Path:
    require(type(relative) is str, "an exact repository-relative path is required")
    pure = PurePosixPath(relative)
    require(not pure.is_absolute() and ".." not in pure.parts
            and "\\" not in relative and "\x00" not in relative
            and pure.as_posix() == relative,
            "refusing an escaping, rewritten, or noncanonical path")
    require(not output or relative in APPROVED_OUTPUTS,
            "refusing an unapproved buffer-oracle output")
    return ROOT.joinpath(*pure.parts)


def _read_regular(relative: str, expected: str, maximum: int) -> bytes:
    require(valid_sha256(expected) and type(maximum) is int and maximum > 0,
            "an actual frozen digest and bounded byte count are required")
    path = safe_relative(relative)
    descriptor = os.open(
        path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        information = os.fstat(descriptor)
        require(stat.S_ISREG(information.st_mode)
                and 0 < information.st_size <= maximum,
                "a frozen prerequisite is not a bounded ordinary file")
        pieces: list[bytes] = []
        remaining = information.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(piece), "a frozen prerequisite ended prematurely")
            pieces.append(piece)
            remaining -= len(piece)
        require(not os.read(descriptor, 1),
                "a frozen prerequisite grew while being authenticated")
        actual = b"".join(pieces)
    finally:
        os.close(descriptor)
    require(hashlib.sha256(actual).hexdigest() == expected,
            "actual frozen prerequisite bytes changed: " + relative)
    return actual


def _unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "duplicate JSON keys cannot conceal reference observations")
        result[key] = value
    return result


def decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and bool(raw),
            "the complete actual reference bytes are required: " + label)
    try:
        decoded = json.loads(
            raw, object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                BufferExporterOracleError("nonfinite JSON is forbidden"),
            ),
        )
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError) as error:
        raise BufferExporterOracleError(
            "the actual frozen Python reference is not strict JSON: " + label,
        ) from error
    require(type(decoded) is dict and canonical(decoded) == raw,
            "actual canonical surrogate-safe reference bytes changed: " + label)
    return decoded


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "use only the isolated, pinned, no-bytecode CPython 3.14.6")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate cannot enter a standard-library-only reference")


def validate_reference_pins(pins: Any) -> dict[str, str]:
    require(type(pins) is dict and set(pins) == {
        "source", "protocol", "v6_reference", "stage27_source",
        "stage27_protocol", "public_reference",
    }, "supply all independently frozen source, protocol, and baseline pins")
    expected = {
        "protocol": PROTOCOL_SHA256,
        "v6_reference": V6_REFERENCE_SHA256,
        "stage27_source": V27_SOURCE_SHA256,
        "stage27_protocol": V27_PROTOCOL_SHA256,
        "public_reference": PUBLIC_REFERENCE_SHA256,
    }
    require(all(valid_sha256(value) for value in pins.values()),
            "every actual externally supplied reference pin is mandatory")
    for key, actual in expected.items():
        require(pins[key] == actual,
                "a frozen independently reviewed prerequisite changed: " + key)
    return dict(pins)


def authenticate_reference_prerequisites(pins: dict[str, str]) -> dict[str, Any]:
    verify_runtime()
    supplied = validate_reference_pins(pins)
    frozen = (
        (SOURCE_RELATIVE, supplied["source"], MAX_SOURCE_BYTES),
        (PROTOCOL_RELATIVE, PROTOCOL_SHA256, MAX_SOURCE_BYTES),
        (ORIGINAL_TEST_RELATIVE, ORIGINAL_TEST_SHA256, MAX_SOURCE_BYTES),
        (V6_SOURCE_RELATIVE, V6_SOURCE_SHA256, MAX_SOURCE_BYTES),
        (V6_PROTOCOL_RELATIVE, V6_PROTOCOL_SHA256, MAX_SOURCE_BYTES),
        (V27_SOURCE_RELATIVE, V27_SOURCE_SHA256, MAX_SOURCE_BYTES),
        (V27_PROTOCOL_RELATIVE, V27_PROTOCOL_SHA256, MAX_SOURCE_BYTES),
    )
    for relative, expected, maximum in frozen:
        _read_regular(relative, expected, maximum)
    original = decode_canonical(
        _read_regular(V6_REFERENCE_RELATIVE, V6_REFERENCE_SHA256,
                      MAX_REFERENCE_BYTES),
        "actual independent two-process V6 original reference",
    )
    require(all(original.get(key) == value for key, value in {
        "schema": "rebar-postfinal-cpython-full-public-locale-v6-self-oracle",
        "status": "PASS", "python": "3.14.6",
        "source_sha256": V6_SOURCE_SHA256,
        "protocol_sha256": V6_PROTOCOL_SHA256,
        "public_method_matrix_sha256": ORIGINAL_MATRIX_SHA256,
        "actual_independent_reference_count": 2,
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }.items()), "the authentic complete original V6 reference was weakened")
    roles = original.get("roles")
    require(type(roles) is dict and tuple(roles) == REFERENCE_LABELS,
            "both independently executed original Python references are required")
    for role in REFERENCE_LABELS:
        actual = roles.get(role)
        require(type(actual) is dict and actual.get("status") == "PASS"
                and actual.get("record_count") == PUBLIC_METHOD_COUNT
                and actual.get("passed") == PUBLIC_METHOD_COUNT - 1
                and actual.get("named_private_debug_skips") == 1
                and type(actual.get("records")) is list
                and len(actual["records"]) == PUBLIC_METHOD_COUNT,
                "an actual original public role or genuine debug skip changed")
    public = decode_canonical(
        _read_regular(PUBLIC_REFERENCE_RELATIVE, PUBLIC_REFERENCE_SHA256,
                      MAX_REFERENCE_BYTES),
        "actual independent surrogate-safe public Python reference",
    )
    require(all(public.get(key) == value for key, value in {
        "schema": "rebar-python-re-cycle-safe-guarded-public-surface-v19-self-oracle",
        "status": "PASS", "python": "3.14.6",
        "cases": PUBLIC_CASE_COUNT, "cohorts": PUBLIC_COHORT_COUNT,
        "actual_independent_reference_count": 2,
        "record_sha256": PUBLIC_RECORD_SHA256,
        "original_public_methods": PUBLIC_METHOD_COUNT,
        "original_applicable_passes": PUBLIC_METHOD_COUNT - 1,
        "original_named_private_debug_skips": 1,
        "original_public_method_waivers": 0,
        "candidate_imports": 0, "candidate_audits_read": 0,
        "candidate_proofs_read": 0, "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
    }.items()), "the genuine frozen 1,376-case public reference was weakened")
    public_roles = public.get("reference_worker_reports")
    require(type(public_roles) is dict and tuple(public_roles) == REFERENCE_LABELS,
            "both genuine complete public-reference workers are mandatory")
    first: list[dict[str, Any]] | None = None
    for role in REFERENCE_LABELS:
        current = public_roles[role]
        records = current.get("records") if isinstance(current, dict) else None
        require(type(records) is list and len(records) == PUBLIC_CASE_COUNT,
                "an original public compatibility observation was omitted")
        require(current.get("status") == "PASS"
                and current.get("record_sha256") == PUBLIC_RECORD_SHA256,
                "a genuine public-reference role no longer passes")
        if first is None:
            first = records
        else:
            require(records == first,
                    "the two authentic public-reference outcome vectors disagree")

    v6 = importlib.import_module("tools.postfinal_cpython_locale_oracle_v6")
    require(os.path.abspath(v6.__file__) == str(ROOT / V6_SOURCE_RELATIVE),
            "the actual frozen original V6 authenticator was substituted")
    original_provenance = v6._original_reference_prerequisites()
    actual_path, actual_original_roles = v6._read_reference(
        V6_REFERENCE_SHA256, original_provenance, V6_SOURCE_SHA256,
    )
    official = original_provenance.get("official", {})
    require(actual_path == V6_REFERENCE_RELATIVE
            and type(actual_original_roles) is dict
            and tuple(actual_original_roles) == REFERENCE_LABELS
            and actual_original_roles == roles
            and official.get("all_original_methods") == ORIGINAL_METHOD_COUNT
            and official.get("public_original_methods") == PUBLIC_METHOD_COUNT
            and official.get("private_original_methods") == PRIVATE_WAIVER_COUNT
            and official.get("named_private_class_waivers")
            == AUTHENTIC_PRIVATE_CLASS_WAIVERS
            and official.get("public_method_waivers") == []
            and type(official.get("public_method_matrix")) is list
            and len(official["public_method_matrix"]) == PUBLIC_METHOD_COUNT
            and type(official.get("original_method_records")) is list
            and len(official["original_method_records"]) == ORIGINAL_METHOD_COUNT
            and tuple(
                record["test"]
                for record in official["original_method_records"]
                if record.get("scope") == "named-private-class-waiver"
            ) == PRIVATE_METHOD_NAMES,
            "the genuine V6 method matrix or 13 named private waivers changed")

    surface = importlib.import_module(
        "tools.python_re_public_surface_oracle_stage27",
    )
    require(os.path.abspath(surface.__file__) == str(ROOT / V27_SOURCE_RELATIVE),
            "the actual frozen public V27 authenticator was substituted")
    authenticated_surface = surface.authenticate_reference(
        V27_SOURCE_SHA256, V27_PROTOCOL_SHA256,
    )
    require(type(authenticated_surface) is dict
            and authenticated_surface.get("v19_reference_sha256")
            == PUBLIC_REFERENCE_SHA256
            and authenticated_surface.get("v19_reference_record_sha256")
            == PUBLIC_RECORD_SHA256
            and authenticated_surface.get("actual_independent_reference_count") == 2
            and authenticated_surface.get("cases") == PUBLIC_CASE_COUNT
            and authenticated_surface.get("baseline_records") == first,
            "the actual full original 1,376-case public reference changed")
    public_processes = public.get("reference_worker_processes")
    require(type(public_processes) is dict
            and tuple(public_processes) == REFERENCE_LABELS,
            "the two actual complete original public worker streams are required")
    for role in REFERENCE_LABELS:
        surface.validate_process_streams(
            public_processes[role], role=role,
            expected_document=public_roles[role],
        )
        require(surface.validate_public_records(public_roles[role]["records"])
                == PUBLIC_RECORD_SHA256
                and public_roles[role].get("successful_real_locale_cases") == 64
                and public_roles[role].get("real_locale_transition_count") == 192,
                "an actual public reference record, stream, or locale changed")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate escaped into immutable reference authentication")
    return {
        "source_sha256": supplied["source"],
        "protocol_sha256": PROTOCOL_SHA256,
        "original_test_sha256": ORIGINAL_TEST_SHA256,
        "original_v6_reference_sha256": V6_REFERENCE_SHA256,
        "original_method_count": ORIGINAL_METHOD_COUNT,
        "original_public_method_count": PUBLIC_METHOD_COUNT,
        "original_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "original_private_method_names": list(PRIVATE_METHOD_NAMES),
        "named_private_class_waivers": copy.deepcopy(
            AUTHENTIC_PRIVATE_CLASS_WAIVERS,
        ),
        "original_applicable_passes": PUBLIC_METHOD_COUNT - 1,
        "original_named_private_debug_skips": 1,
        "stage27_source_sha256": V27_SOURCE_SHA256,
        "stage27_protocol_sha256": V27_PROTOCOL_SHA256,
        "public_reference_sha256": PUBLIC_REFERENCE_SHA256,
        "public_reference_record_sha256": PUBLIC_RECORD_SHA256,
        "unchanged_public_cases": PUBLIC_CASE_COUNT,
        "unchanged_public_cohorts": PUBLIC_COHORT_COUNT,
        "public_reference_workers": 2,
        "public_reference_locale_cases_per_worker": 64,
        "public_reference_locale_transitions_per_worker": 192,
        "buffer_exporter_cases": BUFFER_CASE_COUNT,
        "buffer_exporter_matrix_sha256": MATRIX_SHA256,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _observe_value(value: Any, regex: Any) -> Any:
    if value is None or type(value) in (bool, int, str):
        return value
    if isinstance(value, bytes):
        return {"kind": "bytes", "hex": value.hex()}
    if isinstance(value, bytearray):
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if isinstance(value, memoryview):
        return {
            "kind": "memoryview", "readonly": value.readonly,
            "format": value.format,
            "shape": list(value.shape) if value.shape is not None else None,
            "strides": list(value.strides) if value.strides is not None else None,
            "contiguous": value.contiguous,
            "hex": value.tobytes().hex(),
        }
    if isinstance(value, regex.Match):
        return {
            "kind": "match",
            "group": _observe_value(value.group(), regex),
            "span": list(value.span()),
            "groups": [_observe_value(item, regex) for item in value.groups()],
            "lastindex": value.lastindex,
            "lastgroup": value.lastgroup,
            "pos": value.pos,
            "endpos": value.endpos,
        }
    if isinstance(value, tuple):
        return {
            "kind": "tuple",
            "items": [_observe_value(item, regex) for item in value],
        }
    if isinstance(value, list):
        return {
            "kind": "list",
            "items": [_observe_value(item, regex) for item in value],
        }
    if isinstance(value, dict):
        return {
            "kind": "mapping",
            "items": [
                [str(key), _observe_value(item, regex)]
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            ],
        }
    raise BufferExporterOracleError(
        "the actual buffer worker returned an unfrozen object type: "
        + type(value).__name__,
    )


def _observe_exception(error: Exception, regex: Any) -> dict[str, Any]:
    return {
        "module": type(error).__module__,
        "type": type(error).__qualname__,
        "args": _observe_value(error.args, regex),
    }


def _callback(events: list[list[Any]], *, fail: bool) -> Callable[..., Any]:
    def actual(*arguments: Any) -> bytes:
        token = arguments[-1]
        if hasattr(token, "group"):
            token = token.group()
        events.append([
            "callback",
            bytes(token).hex()
            if isinstance(token, (bytes, bytearray, memoryview)) else None,
            bool(fail),
        ])
        if fail:
            raise CallbackProbeError("genuine buffer exporter callback failure")
        return b"X"

    return actual


def _dispatch(
    regex: Any, operation: str, subject: Any,
    events: list[list[Any]], *, callback_error: bool,
) -> Any:
    expression = b"a+"
    compiled = regex.compile(expression)
    callback = _callback(events, fail=callback_error)
    if operation.startswith("module."):
        method = getattr(regex, operation.split(".", 1)[1])
        if operation in ("module.sub", "module.subn"):
            result = method(expression, callback if callback_error else b"X", subject)
        else:
            result = method(expression, subject)
        return list(result) if operation == "module.finditer" else result
    if operation.startswith("pattern."):
        member = operation.split(".", 1)[1]
        if member == "scanner":
            scanner = compiled.scanner(subject)
            return {"first": scanner.search(), "second": scanner.search()}
        method = getattr(compiled, member)
        if member in ("sub", "subn"):
            result = method(callback if callback_error else b"X", subject)
        else:
            result = method(subject)
        return list(result) if member == "finditer" else result
    if operation == "match.group":
        match = compiled.search(subject)
        if match is None:
            return None
        return {
            "group": match.group(),
            "span": match.span(),
            "groups": match.groups(),
        }
    if operation == "scanner.scan":
        scanner = regex.Scanner([
            (rb"a+", lambda scanner, token: callback(scanner, token)),
            (rb".", None),
        ])
        return scanner.scan(subject)
    raise BufferExporterOracleError("an unfrozen regex operation was selected")


def _capture_call(
    regex: Any, operation: str, subject: Any,
    events: list[list[Any]], *, callback_error: bool,
) -> dict[str, Any]:
    events.append(["call-start", operation])
    try:
        actual = _dispatch(
            regex, operation, subject, events, callback_error=callback_error,
        )
        observed = _observe_value(actual, regex)
    except BufferExporterOracleError:
        raise
    except Exception as error:
        events.append(["call-raise", operation, type(error).__qualname__])
        return {"status": "raise", "exception": _observe_exception(error, regex)}
    events.append(["call-return", operation])
    return {"status": "return", "value": observed}


def _retain_holder(regex: Any, operation: str, subject: Any) -> Any:
    compiled = regex.compile(b"a+")
    if operation == "module.finditer":
        return regex.finditer(b"a+", subject)
    if operation == "pattern.finditer":
        return compiled.finditer(subject)
    if operation == "pattern.scanner":
        return compiled.scanner(subject)
    if operation == "match.group":
        return compiled.search(subject)
    raise BufferExporterOracleError("an unfrozen strong-reference holder escaped")


def _consume_holder(regex: Any, operation: str, holder: Any) -> Any:
    if operation in ("module.finditer", "pattern.finditer"):
        return list(holder)
    if operation == "pattern.scanner":
        return {"first": holder.search(), "second": holder.search()}
    if operation == "match.group":
        return holder
    raise BufferExporterOracleError("an unfrozen live regex holder was consumed")


def _buffer_observation(payload: bytes, events: list[list[Any]]) -> dict[str, Any]:
    acquisitions = [event for event in events if event and event[0] == "acquire"]
    releases = [event for event in events if event and event[0] == "release"]
    final = releases[-1][3] if releases else payload.hex()
    return {
        "initial_hex": payload.hex(),
        "final_hex": final,
        "byte_length": len(payload),
        "acquisitions": len(acquisitions),
        "releases": len(releases),
    }


def execute_case(case: Mapping[str, Any], regex: Any) -> dict[str, Any]:
    scenario = case["scenario"]
    payload = b"zzz" if scenario == "no-match" else b"aaa"
    exporter = PoisonOnReleaseExporter(payload, case["readonly"])
    events = exporter.events
    wrapped = memoryview(exporter) if case["wrapped"] else None
    subject: Any = wrapped if wrapped is not None else exporter
    results: list[dict[str, Any]] = []
    lifetime: dict[str, Any] = {}

    if scenario == "retained":
        events.append(["retained-create", case["operation"]])
        try:
            holder = _retain_holder(regex, case["operation"], subject)
        except BufferExporterOracleError:
            raise
        except Exception as error:
            results.append({
                "status": "raise", "exception": _observe_exception(error, regex),
            })
            events.append(["retained-create-raise", type(error).__qualname__])
        else:
            exporter.cyclic_holder = holder
            owner_reference = weakref.ref(exporter)
            try:
                carrier_reference: weakref.ReferenceType[Any] | None = (
                    weakref.ref(subject)
                )
            except TypeError:
                carrier_reference = None
            wrapped = None
            del subject
            del exporter
            gc.collect()
            lifetime["owner_alive_while_holder_live"] = owner_reference() is not None
            lifetime["carrier_supports_weakref"] = carrier_reference is not None
            lifetime["carrier_alive_while_holder_live"] = (
                carrier_reference() is not None if carrier_reference else None
            )
            events.append([
                "retained-gc-while-live",
                lifetime["owner_alive_while_holder_live"],
                lifetime["carrier_alive_while_holder_live"],
            ])
            try:
                observed = _observe_value(
                    _consume_holder(regex, case["operation"], holder), regex,
                )
                results.append({"status": "return", "value": observed})
            except BufferExporterOracleError:
                raise
            except Exception as error:
                results.append({
                    "status": "raise",
                    "exception": _observe_exception(error, regex),
                })
            del holder
            gc.collect()
            lifetime["owner_alive_after_cyclic_gc"] = owner_reference() is not None
            lifetime["carrier_alive_after_cyclic_gc"] = (
                carrier_reference() is not None if carrier_reference else None
            )
            events.append([
                "retained-gc-after-drop",
                lifetime["owner_alive_after_cyclic_gc"],
                lifetime["carrier_alive_after_cyclic_gc"],
            ])
            return {
                **dict(case), "results": results,
                "events": copy.deepcopy(events), "lifetime": lifetime,
                "buffer": _buffer_observation(payload, events),
            }

    if scenario != "retained":
        calls = 2 if scenario == "repeat" else 1
        for _ in range(calls):
            results.append(_capture_call(
                regex, case["operation"], subject, events,
                callback_error=scenario == "callback-error",
            ))
    if wrapped is not None:
        events.append(["wrapped-release-start"])
        wrapped.release()
        events.append(["wrapped-release-finish"])
    events.append(["case-finish", bytes(exporter.storage).hex()])
    return {
        **dict(case), "results": results,
        "events": copy.deepcopy(events), "lifetime": lifetime,
        "buffer": _buffer_observation(payload, events),
    }


def _valid_payload_hex(value: Any, length: int) -> bool:
    if type(value) is not str or len(value) != 2 * length:
        return False
    try:
        return bytes.fromhex(value).hex() == value
    except ValueError:
        return False


def _validate_event_ledger(
    events: Any, expected: Mapping[str, Any], observed_buffer: Any,
) -> None:
    require(type(events) is list and bool(events),
            "an empty or fabricated exporter event ledger is forbidden")
    require(type(observed_buffer) is dict
            and set(observed_buffer) == {
                "initial_hex", "final_hex", "byte_length",
                "acquisitions", "releases",
            }, "the actual exporter storage and acquisition counts were lost")
    payload = b"zzz" if expected["scenario"] == "no-match" else b"aaa"
    length = len(payload)
    require(observed_buffer.get("initial_hex") == payload.hex()
            and observed_buffer.get("byte_length") == length,
            "the actual original exporter bytes were replaced")
    storage = payload.hex()
    acquisitions = 0
    releases = 0
    callbacks = 0
    starts = 0
    finishes = 0
    case_finishes = 0
    active = False
    wrapped_started = False
    wrapped_finished = False
    retained_started = False
    retained_live = False
    retained_dropped = False
    for event_index, event in enumerate(events):
        require(type(event) is list and bool(event) and type(event[0]) is str,
                "every actual exporter event must retain its exact typed schema")
        kind = event[0]
        if kind == "acquire":
            require(len(event) == 5 and type(event[1]) is int
                    and event[1] == acquisitions + 1
                    and type(event[2]) is int and event[2] >= 0
                    and type(event[3]) is bool
                    and event[3] is expected["readonly"]
                    and event[4] == storage,
                    "an exporter acquisition was reordered or fabricated")
            acquisitions += 1
        elif kind == "release":
            require(len(event) == 4 and type(event[1]) is int
                    and event[1] == releases + 1
                    and event[1] <= acquisitions
                    and event[2] == storage
                    and event[3] == (b"!" * length).hex(),
                    "an actual in-place safe release was lost or forged")
            releases += 1
            storage = event[3]
        elif kind == "call-start":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and not active,
                    "a genuine regex operation was reordered or nested")
            starts += 1
            active = True
        elif kind == "call-return":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and active,
                    "a genuine regex return was invented or reordered")
            finishes += 1
            active = False
        elif kind == "call-raise":
            require(len(event) == 3 and event[1] == expected["operation"]
                    and type(event[2]) is str and active,
                    "a genuine regex exception event was substituted")
            finishes += 1
            active = False
        elif kind == "callback":
            require(len(event) == 3
                    and (event[1] is None
                         or _valid_payload_hex(event[1], len(event[1]) // 2))
                    and type(event[2]) is bool
                    and event[2] is (expected["scenario"] == "callback-error"),
                    "an actual replacement or scanner callback was forged")
            callbacks += 1
        elif kind == "wrapped-release-start":
            require(len(event) == 1 and expected["wrapped"] is True
                    and not wrapped_started and not active,
                    "an original wrapped exporter release was substituted")
            wrapped_started = True
        elif kind == "wrapped-release-finish":
            require(len(event) == 1 and wrapped_started and not wrapped_finished,
                    "the actual wrapped exporter release order changed")
            wrapped_finished = True
        elif kind == "case-finish":
            require(len(event) == 2 and event[1] == storage and not active
                    and expected["scenario"] != "retained"
                    and case_finishes == 0 and event_index == len(events) - 1,
                    "the complete final exporter bytes were changed")
            case_finishes += 1
        elif kind == "retained-create":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and expected["scenario"] == "retained"
                    and not retained_started,
                    "a genuine cyclic scanner or iterator was substituted")
            retained_started = True
        elif kind == "retained-create-raise":
            require(len(event) == 2 and type(event[1]) is str
                    and retained_started,
                    "an actual retained-holder exception was invented")
        elif kind == "retained-gc-while-live":
            require(len(event) == 3 and type(event[1]) is bool
                    and (event[2] is None or type(event[2]) is bool)
                    and retained_started and not retained_live,
                    "an actual live strong-reference GC check was forged")
            retained_live = True
        elif kind == "retained-gc-after-drop":
            require(len(event) == 3 and type(event[1]) is bool
                    and (event[2] is None or type(event[2]) is bool)
                    and retained_live and not retained_dropped,
                    "an actual cyclic exporter cleanup check was forged")
            retained_dropped = True
        else:
            raise BufferExporterOracleError(
                "an unfrozen exporter event was injected: " + kind,
            )
    require(not active and acquisitions > 0
            and acquisitions == releases
            and observed_buffer.get("acquisitions") == acquisitions
            and observed_buffer.get("releases") == releases
            and observed_buffer.get("final_hex") == storage
            and _valid_payload_hex(storage, length),
            "an acquired buffer was dereferenced, leaked, or miscounted")
    if expected["scenario"] == "retained":
        require(retained_started and retained_live and retained_dropped
                and not starts and not finishes and case_finishes == 0,
                "actual live-holder or cyclic GC observations were removed")
    else:
        required_calls = 2 if expected["scenario"] == "repeat" else 1
        require(starts == finishes == required_calls,
                "an actual original or repeated exporter call was omitted")
        require(case_finishes == 1,
                "the exact terminal exporter event was omitted or duplicated")
        require(wrapped_started is expected["wrapped"]
                and wrapped_finished is expected["wrapped"],
                "a wrapped memoryview was not genuinely acquired and released")
    if expected["scenario"] == "callback-error":
        require(callbacks > 0,
                "an actual failing replacement or scanner callback was removed")


def validate_case_record(record: Any, expected: Mapping[str, Any]) -> None:
    require(type(record) is dict
            and set(record) == set(expected) | {
                "results", "events", "lifetime", "buffer",
            },
            "an actual exporter record omitted or invented a field")
    require(all(record.get(key) == value for key, value in expected.items()),
            "a real exporter record changed its frozen case identity")
    require(type(record.get("results")) is list
            and len(record["results"]) == (
                2 if expected["scenario"] == "repeat" else 1
            )
            and type(record.get("events")) is list
            and type(record.get("lifetime")) is dict,
            "a genuine buffer event, repeat, or lifetime was concealed")
    _validate_event_ledger(
        record["events"], expected, record.get("buffer"),
    )
    for observed in record["results"]:
        require(type(observed) is dict
                and observed.get("status") in ("return", "raise")
                and set(observed) == (
                    {"status", "value"}
                    if observed.get("status") == "return"
                    else {"status", "exception"}
                ), "a genuine Python return or exception was forged")
        if observed["status"] == "raise":
            exception = observed["exception"]
            require(type(exception) is dict
                    and set(exception) == {"module", "type", "args"}
                    and type(exception["module"]) is str
                    and type(exception["type"]) is str,
                    "an actual buffer exception identity was discarded")
    if expected["scenario"] == "callback-error":
        require(record["results"][0]["status"] == "raise"
                and record["results"][0]["exception"]["type"]
                == "CallbackProbeError",
                "a genuine callback failure was swallowed or substituted")
    if expected["scenario"] == "retained":
        require(set(record["lifetime"]) == {
            "owner_alive_while_holder_live", "carrier_supports_weakref",
            "carrier_alive_while_holder_live", "owner_alive_after_cyclic_gc",
            "carrier_alive_after_cyclic_gc",
        }, "a real scanner, iterator, match, or cyclic lifetime was omitted")
        lifetime = record["lifetime"]
        require(type(lifetime["owner_alive_while_holder_live"]) is bool
                and type(lifetime["carrier_supports_weakref"]) is bool
                and type(lifetime["owner_alive_after_cyclic_gc"]) is bool
                and all(lifetime[key] is None or type(lifetime[key]) is bool
                        for key in (
                            "carrier_alive_while_holder_live",
                            "carrier_alive_after_cyclic_gc",
                        )),
                "an actual typed exporter or scanner weak-reference was forged")
        while_live = [
            event for event in record["events"]
            if event and event[0] == "retained-gc-while-live"
        ]
        after_drop = [
            event for event in record["events"]
            if event and event[0] == "retained-gc-after-drop"
        ]
        require(len(while_live) == len(after_drop) == 1
                and while_live[0][1]
                is lifetime["owner_alive_while_holder_live"]
                and while_live[0][2]
                is lifetime["carrier_alive_while_holder_live"]
                and after_drop[0][1]
                is lifetime["owner_alive_after_cyclic_gc"]
                and after_drop[0][2]
                is lifetime["carrier_alive_after_cyclic_gc"]
                and lifetime["carrier_supports_weakref"]
                is (while_live[0][2] is not None),
                "actual live and finalized cyclic weakrefs contradict their events")
    else:
        require(record["lifetime"] == {},
                "a nonretained regex case invented lifetime observations")


def run_reference_worker(role: str, pins: dict[str, str]) -> dict[str, Any]:
    require(role in REFERENCE_LABELS,
            "only two actual standard-library-only reference roles are allowed")
    provenance = authenticate_reference_prerequisites(pins)
    regex = importlib.import_module("re")
    require(regex.__name__ == "re" and type(regex.__file__) is str
            and os.path.abspath(regex.__file__).startswith(
                str(PINNED_PYTHON.parent.parent) + os.sep,
            )
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "the buffer reference imported a nonstandard matching engine")
    matrix = build_matrix()
    validate_matrix(matrix)
    records = []
    for case in matrix:
        actual = execute_case(case, regex)
        validate_case_record(actual, case)
        records.append(actual)
    require(len(records) == BUFFER_CASE_COUNT,
            "a genuine Python exporter observation was skipped")
    return {
        "schema": SCHEMA + "-actual-reference-worker",
        "status": "PASS", "role": role, "python": "3.14.6",
        "source_sha256": provenance["source_sha256"],
        "protocol_sha256": PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": BUFFER_CASE_COUNT,
        "records_sha256": digest(records),
        "records": records,
        "candidate_imports": 0,
        "candidate_workers": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "synthetic": False,
    }


def _capture_stream(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_WORKER_BYTES,
            "the complete actual bounded worker stream was lost: " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def restore_stream(observed: Any, label: str) -> bytes:
    require(type(observed) is dict
            and set(observed) == {"base64", "bytes", "sha256", "complete"}
            and type(observed.get("base64")) is str
            and type(observed.get("bytes")) is int
            and 0 <= observed["bytes"] <= MAX_WORKER_BYTES
            and valid_sha256(observed.get("sha256"))
            and observed.get("complete") is True,
            "the complete actual buffer-worker stream was forged: " + label)
    try:
        raw = base64.b64decode(observed["base64"], validate=True)
    except (ValueError, base64.binascii.Error) as error:
        raise BufferExporterOracleError(
            "invalid complete buffer-worker capture: " + label,
        ) from error
    require(len(raw) == observed["bytes"]
            and hashlib.sha256(raw).hexdigest() == observed["sha256"]
            and _capture_stream(raw, label) == observed,
            "actual buffer-worker stream bytes changed: " + label)
    return raw


def validate_worker_document(
    observed: Any, *, role: str, pins: Mapping[str, str],
) -> dict[str, Any]:
    require(type(observed) is dict,
            "a complete genuine isolated reference document is mandatory")
    for key, expected in {
        "schema": SCHEMA + "-actual-reference-worker",
        "status": "PASS", "role": role, "python": "3.14.6",
        "source_sha256": pins["source"],
        "protocol_sha256": PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": BUFFER_CASE_COUNT,
        "candidate_imports": 0,
        "candidate_workers": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED", "synthetic": False,
    }.items():
        require(observed.get(key) == expected,
                "an actual Python worker observation changed: " + key)
    records = observed.get("records")
    matrix = build_matrix()
    require(type(records) is list and len(records) == BUFFER_CASE_COUNT
            and observed.get("records_sha256") == digest(records),
            "the complete ordered actual 264-case outcome vector was lost")
    for expected, record in zip(matrix, records, strict=True):
        validate_case_record(record, expected)
    return dict(observed)


def validate_worker_process(
    observed: Any, *, role: str, expected: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(observed) is dict
            and set(observed) == {"role", "pid", "returncode", "stdout", "stderr"}
            and observed.get("role") == role
            and type(observed.get("pid")) is int and observed["pid"] > 0
            and type(observed.get("returncode")) is int
            and observed["returncode"] == 0,
            "the actual isolated Python reference process was forged")
    stdout = restore_stream(observed["stdout"], role + " stdout")
    stderr = restore_stream(observed["stderr"], role + " stderr")
    require(stderr == b"", "a passing reference worker concealed actual stderr")
    require(decode_canonical(stdout, role + " complete original stdout")
            == dict(expected),
            "actual complete worker stdout does not equal its reference report")
    return dict(observed)


def _worker_arguments(role: str, pins: Mapping[str, str]) -> list[str]:
    return [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--worker-role", role,
        "--source-sha256", pins["source"],
        "--protocol-sha256", pins["protocol"],
        "--v6-reference-sha256", pins["v6_reference"],
        "--stage27-source-sha256", pins["stage27_source"],
        "--stage27-protocol-sha256", pins["stage27_protocol"],
        "--public-reference-sha256", pins["public_reference"],
    ]


def run_isolated_reference(
    role: str, pins: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in REFERENCE_LABELS,
            "an unapproved reference process cannot be started")
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }
    process = subprocess.Popen(
        _worker_arguments(role, pins),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(ROOT), env=environment,
        shell=False,
    )
    try:
        stdout, stderr = process.communicate(timeout=WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        process.kill()
        stdout, stderr = process.communicate()
        raise ActualReferenceWorkerFailure(
            "the genuine isolated Python buffer-reference worker timed out",
            {
                "role": role, "pid": process.pid,
                "returncode": process.returncode,
                "stdout": _capture_stream(stdout or b"", role + " stdout"),
                "stderr": _capture_stream(stderr or b"", role + " stderr"),
            },
        ) from error
    captured = {
        "role": role, "pid": process.pid, "returncode": process.returncode,
        "stdout": _capture_stream(stdout, role + " stdout"),
        "stderr": _capture_stream(stderr, role + " stderr"),
    }
    if process.returncode != 0 or stderr:
        raise ActualReferenceWorkerFailure(
            "the genuine Python buffer-reference worker did not pass",
            captured,
        )
    try:
        document = validate_worker_document(
            decode_canonical(stdout, role + " actual complete worker stdout"),
            role=role, pins=pins,
        )
        validate_worker_process(captured, role=role, expected=document)
    except BufferExporterOracleError as error:
        raise ActualReferenceWorkerFailure(
            "the actual Python buffer-reference vector was invalid: " + str(error),
            captured,
        ) from error
    return document, captured


def preflight_fresh_outputs() -> None:
    for relative in sorted(APPROVED_OUTPUTS):
        path = safe_relative(relative, output=True)
        directory = os.open(
            path.parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            require(stat.S_ISDIR(os.fstat(directory).st_mode),
                    "the exact approved evidence parent is not a real directory")
            try:
                os.stat(path.name, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise BufferExporterOracleError(
                "refusing to overwrite an actual first buffer result: " + relative,
            )
        finally:
            os.close(directory)


def _write_exclusive(relative: str, payload: bytes) -> dict[str, Any]:
    path = safe_relative(relative, output=True)
    require(type(payload) is bytes and 0 < len(payload) <= MAX_REFERENCE_BYTES,
            "one complete canonical bounded publication is mandatory")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    directory = os.open(
        path.parent,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    written = 0
    file_synced = False
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the actual approved publication parent is not a real directory")
        descriptor = os.open(path.name, flags, 0o644, dir_fd=directory)
        try:
            information = os.fstat(descriptor)
            require(stat.S_ISREG(information.st_mode),
                    "the exclusively created report is not an ordinary file")
            written = os.write(descriptor, payload)
            require(type(written) is int and written == len(payload),
                    "the actual single publication write was short")
            os.fsync(descriptor)
            file_synced = True
        finally:
            os.close(descriptor)
        reader = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory,
        )
        try:
            actual_info = os.fstat(reader)
            require(stat.S_ISREG(actual_info.st_mode)
                    and actual_info.st_dev == information.st_dev
                    and actual_info.st_ino == information.st_ino
                    and actual_info.st_size == len(payload),
                    "the report changed its actual descriptor or file identity")
            parts: list[bytes] = []
            remaining = len(payload)
            while remaining:
                piece = os.read(reader, min(remaining, 1024 * 1024))
                require(bool(piece), "the actual report readback was truncated")
                parts.append(piece)
                remaining -= len(piece)
            require(not os.read(reader, 1),
                    "the actual report grew during descriptor-local readback")
            require(b"".join(parts) == payload,
                    "actual exclusively published bytes changed during readback")
        finally:
            os.close(reader)
        os.fsync(directory)
    finally:
        os.close(directory)
    expected = hashlib.sha256(payload).hexdigest()
    return {
        "path": relative,
        "sha256": expected,
        "bytes": len(payload),
        "actual_write_calls": 1,
        "actual_bytes_written": written,
        "file_fsync_completed": file_synced,
        "directory_fsync_completed": True,
        "exact_canonical_readback_verified": True,
    }


def publish_exclusive(
    document: Mapping[str, Any], relative: str, receipt_relative: str,
) -> dict[str, Any]:
    require(relative in (SUCCESS_RELATIVE, FAILURE_RELATIVE)
            and receipt_relative == (
                SUCCESS_RECEIPT_RELATIVE
                if relative == SUCCESS_RELATIVE
                else FAILURE_RECEIPT_RELATIVE
            ), "a failure, success, or receipt path was interchanged")
    observed = _write_exclusive(relative, canonical(dict(document)))
    receipt = {
        "schema": SCHEMA + "-actual-exclusive-publication-receipt",
        "status": "PASS",
        **observed,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "synthetic": False,
    }
    sidecar = _write_exclusive(receipt_relative, canonical(receipt))
    require(sidecar["actual_write_calls"] == 1
            and sidecar["exact_canonical_readback_verified"] is True,
            "the actual exclusive receipt was not durably published")
    return {"report": observed, "receipt": sidecar}


def run_self_oracle(pins: dict[str, str]) -> dict[str, Any]:
    prerequisites = authenticate_reference_prerequisites(pins)
    validate_matrix(build_matrix())
    preflight_fresh_outputs()
    roles: dict[str, dict[str, Any]] = {}
    processes: dict[str, dict[str, Any]] = {}
    try:
        for role in REFERENCE_LABELS:
            document, process = run_isolated_reference(role, pins)
            roles[role] = document
            processes[role] = process
        require(processes["reference_a"]["pid"]
                != processes["reference_b"]["pid"],
                "the two real buffer-reference workers must be distinct processes")
        first = roles["reference_a"]["records"]
        second = roles["reference_b"]["records"]
        require(first == second,
                "the two actual PEP 688 Python outcome vectors disagree")
        require(roles["reference_a"]["records_sha256"]
                == roles["reference_b"]["records_sha256"] == digest(first),
                "the two actual buffer-reference outcome digests differ")
        result = {
            "schema": SCHEMA + "-self-oracle",
            "status": "PASS", "python": "3.14.6",
            "source_sha256": pins["source"],
            "protocol_sha256": PROTOCOL_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "case_count": BUFFER_CASE_COUNT,
            "actual_independent_reference_count": 2,
            "actual_reference_process_count": 2,
            "actual_case_executions": 2 * BUFFER_CASE_COUNT,
            "reference_vector_sha256": digest(first),
            "reference_worker_reports": roles,
            "reference_worker_processes": processes,
            "frozen_prerequisites": prerequisites,
            "actual_candidate_workers": 0,
            "candidate_imports": 0,
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            "synthetic": False,
        }
        publication = publish_exclusive(
            result, SUCCESS_RELATIVE, SUCCESS_RECEIPT_RELATIVE,
        )
        return {
            "schema": SCHEMA + "-published-reference-summary",
            "status": "PASS",
            "actual_independent_reference_count": 2,
            "case_count": BUFFER_CASE_COUNT,
            "matrix_sha256": MATRIX_SHA256,
            "reference_vector_sha256": digest(first),
            "publication": publication,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }
    except (BufferExporterOracleError, OSError, subprocess.SubprocessError) as error:
        failure = {
            "schema": SCHEMA + "-actual-self-oracle-failure",
            "status": "FAIL", "python": "3.14.6",
            "source_sha256": pins["source"],
            "protocol_sha256": PROTOCOL_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "case_count": BUFFER_CASE_COUNT,
            "actual_completed_reference_count": len(roles),
            "actual_completed_reference_roles": roles,
            "actual_completed_reference_processes": processes,
            "failure_type": type(error).__qualname__,
            "failure_message": str(error),
            "actual_failed_worker": (
                error.details if isinstance(error, ActualReferenceWorkerFailure)
                else None
            ),
            "frozen_prerequisites": prerequisites,
            "actual_candidate_workers": 0,
            "holdout_cases_read": 0, "performance_fixtures_read": 0,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            "synthetic": False,
        }
        publication = publish_exclusive(
            failure, FAILURE_RELATIVE, FAILURE_RECEIPT_RELATIVE,
        )
        return {
            "schema": SCHEMA + "-published-reference-failure-summary",
            "status": "FAIL",
            "actual_completed_reference_count": len(roles),
            "actual_failed_reference_role": (
                error.details.get("role")
                if isinstance(error, ActualReferenceWorkerFailure) else None
            ),
            "publication": publication,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0, "file_writes": 0, "candidate_imports": 0,
        "production_imports": 0, "reference_workers": 0,
        "candidate_workers": 0, "native_workers": 0,
        "threads_started": 0, "clock_samples": 0,
        "regex_matching_calls": 0, "directory_inspections": 0,
        "locale_changes": 0,
        "buffer_exporter_constructions": 0,
        "buffer_case_executions": 0, "gc_collections": 0,
        "blocked_reads": 0, "blocked_writes": 0,
        "blocked_imports": 0, "blocked_workers": 0,
        "blocked_threads": 0, "blocked_clocks": 0,
        "blocked_regex_matching": 0, "blocked_directories": 0,
        "blocked_locale_changes": 0,
        "blocked_buffer_exporter_constructions": 0,
        "blocked_buffer_case_executions": 0,
        "blocked_gc_collections": 0,
    }
    changes: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            changes.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    def deny(counter: str, message: str) -> Callable[..., Any]:
        def blocked(*arguments: Any, **keywords: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyBoundaryError(message)

        return blocked

    def denied_open(*arguments: Any, **keywords: Any) -> Any:
        mode = keywords.get("mode", arguments[1] if len(arguments) > 1 else "r")
        if isinstance(mode, int):
            writing = bool(mode & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))
        else:
            writing = any(marker in str(mode) for marker in ("w", "a", "x", "+"))
        effects["blocked_writes" if writing else "blocked_reads"] += 1
        raise SourceOnlyBoundaryError("source-only controls cannot open a file")

    try:
        install(builtins, "open", denied_open)
        install(io, "open", denied_open)
        install(os, "open", denied_open)
        install(Path, "open", denied_open)
        for name in ("read_bytes", "read_text"):
            install(Path, name, deny(
                "blocked_reads", "source-only controls cannot read evidence",
            ))
        for name in ("write_bytes", "write_text", "touch", "mkdir", "unlink"):
            install(Path, name, deny(
                "blocked_writes", "source-only controls cannot write a file",
            ))
        for name in ("listdir", "scandir", "walk"):
            install(os, name, deny(
                "blocked_directories", "source-only controls cannot inspect data",
            ))
        for name in ("iterdir", "glob", "rglob"):
            install(Path, name, deny(
                "blocked_directories", "source-only controls cannot inspect paths",
            ))
        install(importlib, "import_module", deny(
            "blocked_imports", "source-only controls cannot import production code",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "source-only controls cannot import modules",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny(
                "blocked_workers", "source-only controls cannot start a worker",
            ))
        for name in ("fork", "posix_spawn", "posix_spawnp", "system"):
            install(os, name, deny(
                "blocked_workers", "source-only controls cannot start a process",
            ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "source-only controls cannot start a thread",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
            "perf_counter_ns", "process_time", "process_time_ns",
            "thread_time", "thread_time_ns",
        ):
            install(time, name, deny(
                "blocked_clocks", "source-only controls cannot sample a clock",
            ))
        install(locale, "setlocale", deny(
            "blocked_locale_changes", "source-only controls cannot change locale",
        ))
        install(PoisonOnReleaseExporter, "__init__", deny(
            "blocked_buffer_exporter_constructions",
            "source-only controls cannot construct an actual PEP 688 exporter",
        ))
        install(sys.modules[__name__], "execute_case", deny(
            "blocked_buffer_case_executions",
            "source-only controls cannot execute a real buffer-exporter case",
        ))
        install(gc, "collect", deny(
            "blocked_gc_collections",
            "source-only controls cannot perform production cyclic collection",
        ))
        loaded_regex = sys.modules.get("re")
        if loaded_regex is not None:
            for name in (
                "compile", "search", "match", "fullmatch", "findall", "finditer",
                "split", "sub", "subn",
            ):
                install(loaded_regex, name, deny(
                    "blocked_regex_matching",
                    "source-only controls cannot perform Python regex matching",
                ))
        yield effects
    finally:
        for owner, name, previous in reversed(changes):
            setattr(owner, name, previous)


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    preloaded_regex = sys.modules.get("re")
    original_regex_search = (
        getattr(preloaded_regex, "search", None)
        if preloaded_regex is not None else None
    )
    original_open = builtins.open
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and bool(condition),
                "an authentic source-only positive control failed: " + name)
        require(name not in accepted,
                "an authentic source-only positive control was duplicated")
        accepted.append(name)

    def reject(name: str, exercise: Callable[[], Any]) -> None:
        require(name not in rejected,
                "an authentic source-only rejection control was duplicated")
        try:
            exercise()
        except (BufferExporterOracleError, ValueError, TypeError, OSError):
            rejected.append(name)
            return
        raise BufferExporterOracleError(
            "a genuine source-only poison control unexpectedly passed: " + name,
        )

    with source_only_boundary() as effects:
        matrix = build_matrix()
        accept("freeze-exact-264-genuine-buffer-cases",
               validate_matrix(matrix) == MATRIX_SHA256)
        accept("freeze-exact-four-original-pep688-carriers", len(CARRIERS) == 4)
        accept("freeze-exact-19-original-module-and-pattern-operations",
               len(OPERATIONS) == 19)
        accept("freeze-20-genuine-failing-callback-cases",
               sum(row["scenario"] == "callback-error" for row in matrix) == 20)
        accept("freeze-16-genuine-strong-reference-and-cyclic-cases",
               sum(row["scenario"] == "retained" for row in matrix) == 16)
        for scenario in ("success", "no-match", "repeat"):
            accept("freeze-76-exact-" + scenario + "-cases",
                   sum(row["scenario"] == scenario for row in matrix) == 76)
        for carrier, wrapped, readonly in CARRIERS:
            accept("retain-genuine-carrier-" + carrier,
                   all(row["wrapped"] is wrapped
                       and row["readonly"] is readonly
                       for row in matrix if row["carrier"] == carrier))
        for operation in OPERATIONS:
            accept("retain-genuine-buffer-operation-" + operation,
                   any(row["operation"] == operation for row in matrix))
        accept("truthfully-preserve-165-original-152-public-13-private",
               ORIGINAL_METHOD_COUNT == PUBLIC_METHOD_COUNT + PRIVATE_WAIVER_COUNT
               and len(PRIVATE_METHOD_NAMES) == PRIVATE_WAIVER_COUNT
               and len(set(PRIVATE_METHOD_NAMES)) == PRIVATE_WAIVER_COUNT
               and sum(value["methods"] for value in
                       AUTHENTIC_PRIVATE_CLASS_WAIVERS.values())
               == PRIVATE_WAIVER_COUNT)
        accept("truthfully-preserve-frozen-1376-public-cases-and-43-cohorts",
               PUBLIC_CASE_COUNT == 1_376 and PUBLIC_COHORT_COUNT == 43)
        accept("keep-complete-pinned-surrogate-safe-original-reference",
               valid_sha256(V6_REFERENCE_SHA256)
               and valid_sha256(PUBLIC_REFERENCE_SHA256)
               and valid_sha256(PUBLIC_RECORD_SHA256))
        accept("bind-exact-final-v27-source-and-protocol",
               valid_sha256(V27_SOURCE_SHA256)
               and valid_sha256(V27_PROTOCOL_SHA256))
        accept("bind-exact-complete-exporter-protocol",
               valid_sha256(PROTOCOL_SHA256))
        fake_pins = {
            "source": "12" * 32, "protocol": PROTOCOL_SHA256,
            "v6_reference": V6_REFERENCE_SHA256,
            "stage27_source": V27_SOURCE_SHA256,
            "stage27_protocol": V27_PROTOCOL_SHA256,
            "public_reference": PUBLIC_REFERENCE_SHA256,
        }
        accept("validate-only-in-memory-source-reference-pin-shape",
               validate_reference_pins(fake_pins) == fake_pins)
        for name in tuple(fake_pins):
            removed = dict(fake_pins)
            removed.pop(name)
            reject("reject-missing-source-only-frozen-pin-" + name,
                   lambda removed=removed: validate_reference_pins(removed))
            changed = dict(fake_pins)
            changed[name] = "34" * 32
            if name != "source":
                reject("reject-replaced-source-only-frozen-pin-" + name,
                       lambda changed=changed: validate_reference_pins(changed))
        for index in (0, len(matrix) // 2, len(matrix) - 1):
            missing = copy.deepcopy(matrix)
            missing.pop(index)
            reject("reject-omitted-real-buffer-case-" + str(index),
                   lambda missing=missing: validate_matrix(missing))
            replaced = copy.deepcopy(matrix)
            replaced[index]["operation"] = "candidates.foreign.match"
            reject("reject-foreign-real-buffer-case-" + str(index),
                   lambda replaced=replaced: validate_matrix(replaced))
            forged = copy.deepcopy(matrix)
            forged[index]["readonly"] = 1
            reject("reject-forged-real-buffer-type-" + str(index),
                   lambda forged=forged: validate_matrix(forged))
        swapped = copy.deepcopy(matrix)
        swapped[0], swapped[1] = swapped[1], swapped[0]
        reject("reject-reordered-real-buffer-cases",
               lambda: validate_matrix(swapped))
        duplicated = copy.deepcopy(matrix)
        duplicated[-1] = copy.deepcopy(duplicated[0])
        reject("reject-duplicated-real-buffer-cases",
               lambda: validate_matrix(duplicated))

        sample = matrix[0]
        safe_events = [
            ["call-start", sample["operation"]],
            ["acquire", 1, 0, False, "616161"],
            ["release", 1, "616161", "212121"],
            ["call-return", sample["operation"]],
            ["case-finish", "212121"],
        ]
        synthetic_record = {
            **sample,
            "results": [{"status": "return", "value": None}],
            "events": safe_events,
            "lifetime": {},
            "buffer": {
                "initial_hex": "616161", "final_hex": "212121",
                "byte_length": 3, "acquisitions": 1, "releases": 1,
            },
        }
        validate_case_record(synthetic_record, sample)
        accept("accept-only-explicitly-synthetic-in-memory-event-control", True)
        for key in ("results", "events", "lifetime", "buffer"):
            forged = copy.deepcopy(synthetic_record)
            forged.pop(key)
            reject("reject-missing-authenticated-exporter-" + key,
                   lambda forged=forged: validate_case_record(forged, sample))
        for key in ("initial_hex", "final_hex", "byte_length", "acquisitions", "releases"):
            forged = copy.deepcopy(synthetic_record)
            forged["buffer"].pop(key)
            reject("reject-missing-actual-exporter-buffer-" + key,
                   lambda forged=forged: validate_case_record(forged, sample))
        empty_events = copy.deepcopy(synthetic_record)
        empty_events["events"] = []
        reject("reject-empty-fabricated-buffer-event-ledger",
               lambda: validate_case_record(empty_events, sample))
        inverted_events = copy.deepcopy(synthetic_record)
        inverted_events["events"][1], inverted_events["events"][2] = (
            inverted_events["events"][2], inverted_events["events"][1],
        )
        reject("reject-release-before-real-buffer-acquisition",
               lambda: validate_case_record(inverted_events, sample))
        no_release = copy.deepcopy(synthetic_record)
        no_release["events"].pop(2)
        reject("reject-concealed-real-buffer-release",
               lambda: validate_case_record(no_release, sample))
        fake_count = copy.deepcopy(synthetic_record)
        fake_count["buffer"]["releases"] = 2
        reject("reject-fabricated-buffer-release-count",
               lambda: validate_case_record(fake_count, sample))
        bad_poison = copy.deepcopy(synthetic_record)
        bad_poison["events"][2][3] = "212122"
        reject("reject-resized-or-nongenuine-buffer-poison",
               lambda: validate_case_record(bad_poison, sample))
        no_finish = copy.deepcopy(synthetic_record)
        no_finish["events"].pop()
        reject("reject-missing-terminal-exporter-event",
               lambda: validate_case_record(no_finish, sample))
        extra_finish = copy.deepcopy(synthetic_record)
        extra_finish["events"].append(["case-finish", "212121"])
        reject("reject-duplicate-terminal-exporter-event",
               lambda: validate_case_record(extra_finish, sample))
        early_finish = copy.deepcopy(synthetic_record)
        early_finish["events"][3], early_finish["events"][4] = (
            early_finish["events"][4], early_finish["events"][3],
        )
        reject("reject-reordered-terminal-exporter-event",
               lambda: validate_case_record(early_finish, sample))
        for relative in (
            "/tmp/escaping-buffer.json", "../escaping-buffer.json",
            "oracle/cpython-3.14.6/evidence/not-approved.json",
        ):
            reject("reject-unapproved-source-only-output-" + relative,
                   lambda relative=relative: safe_relative(relative, output=True))
        for name in ("candidates.rust_candidate", "candidates.vm_candidate",
                     "candidates.zig_candidate",
                     "tools.postfinal_cpython_locale_oracle_v6",
                     "tools.python_re_public_surface_oracle_stage27"):
            reject("block-actual-source-only-production-import-" + name,
                   lambda name=name: importlib.import_module(name))
        reject("block-actual-source-only-builtin-production-import",
               lambda: builtins.__import__("candidates.rust_candidate"))
        reject("block-actual-source-only-builtin-evidence-read",
               lambda: builtins.open(V6_REFERENCE_RELATIVE, "rb"))
        reject("block-actual-source-only-io-evidence-read",
               lambda: io.open(PUBLIC_REFERENCE_RELATIVE, "rb"))
        reject("block-actual-source-only-raw-evidence-read",
               lambda: os.open(V6_REFERENCE_RELATIVE, os.O_RDONLY))
        reject("block-actual-source-only-path-evidence-read",
               lambda: (ROOT / PUBLIC_REFERENCE_RELATIVE).read_bytes())
        reject("block-actual-source-only-evidence-write",
               lambda: builtins.open(SUCCESS_RELATIVE, "wb"))
        reject("block-actual-source-only-authenticated-reference-reading",
               lambda: authenticate_reference_prerequisites(fake_pins))
        reject("block-actual-source-only-secure-output-preflight",
               lambda: preflight_fresh_outputs())
        reject("block-actual-source-only-exclusive-report-publication",
               lambda: _write_exclusive(SUCCESS_RELATIVE, b"{}\n"))
        reject("block-actual-source-only-proof-directory-inspection",
               lambda: os.listdir(str(ROOT / "oracle")))
        reject("block-actual-source-only-background-thread",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-actual-source-only-reference-worker",
               lambda: subprocess.Popen([str(PINNED_PYTHON)]))
        reject("block-actual-source-only-reference-run",
               lambda: subprocess.run([str(PINNED_PYTHON)]))
        reject("block-actual-source-only-wall-clock",
               lambda: time.time())
        reject("block-actual-source-only-performance-clock",
               lambda: time.perf_counter())
        reject("block-actual-source-only-locale-mutation",
               lambda: locale.setlocale(locale.LC_CTYPE))
        reject("block-actual-source-only-buffer-exporter-construction",
               lambda: PoisonOnReleaseExporter(b"aaa", False))
        reject("block-actual-source-only-real-buffer-case-execution",
               lambda: execute_case(sample, None))
        reject("block-actual-source-only-cyclic-garbage-collection",
               lambda: gc.collect())
        loaded_regex = sys.modules.get("re")
        if loaded_regex is not None:
            reject("block-actual-source-only-stdlib-regex-matching",
                   lambda: loaded_regex.search("a", "a"))
        class ContractPoison:
            def compile(self, expression: Any) -> Any:
                raise BufferExporterOracleError("actual source-only contract poison")

        reject("reject-harness-errors-as-fake-regex-outcomes",
               lambda: _capture_call(
                   ContractPoison(), "module.search", b"aaa", [],
                   callback_error=False,
               ))
        accept("never-load-a-candidate-or-production-oracle",
               not any(name == "candidates" or name.startswith("candidates.")
                       or name == "tools.postfinal_cpython_locale_oracle_v6"
                       or name == "tools.python_re_public_surface_oracle_stage27"
                       for name in sys.modules))
        accept("preserve-zero-real-source-only-side-effects",
               all(effects[name] == 0 for name in (
                   "file_reads", "file_writes", "candidate_imports",
                   "production_imports", "reference_workers", "candidate_workers",
                   "native_workers", "threads_started", "clock_samples",
                   "regex_matching_calls", "directory_inspections", "locale_changes",
                   "buffer_exporter_constructions", "buffer_case_executions",
                   "gc_collections",
               )))

    accept("restore-exact-original-open-after-reversible-source-boundary",
           builtins.open is original_open)
    accept("restore-exact-preloaded-stdlib-matcher-after-source-boundary",
           preloaded_regex is None
           or getattr(preloaded_regex, "search", None) is original_regex_search)

    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "protocol_sha256": PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "buffer_case_count": BUFFER_CASE_COUNT,
        "carrier_count": len(CARRIERS),
        "operation_count": len(OPERATIONS),
        "original_method_count": ORIGINAL_METHOD_COUNT,
        "original_public_method_count": PUBLIC_METHOD_COUNT,
        "original_private_method_count": PRIVATE_WAIVER_COUNT,
        "original_private_methods_status": "WAIVED; NOT RUN; NOT QUALIFIED",
        "unchanged_public_case_count": PUBLIC_CASE_COUNT,
        "unchanged_public_cohort_count": PUBLIC_COHORT_COUNT,
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "effects": effects,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_buffer_case_executions": 0,
        "preloaded_stdlib_regex_present": preloaded_regex is not None,
        "candidate_qualified": False,
        "reference_qualified": False,
        "synthetic": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze and compare safe original Python PEP 688 exporter events",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--worker-role", choices=REFERENCE_LABELS)
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--v6-reference-sha256")
    parser.add_argument("--stage27-source-sha256")
    parser.add_argument("--stage27-protocol-sha256")
    parser.add_argument("--public-reference-sha256")
    return parser.parse_args(arguments)


def _option_pins(options: argparse.Namespace) -> dict[str, str]:
    return validate_reference_pins({
        "source": options.source_sha256,
        "protocol": options.protocol_sha256,
        "v6_reference": options.v6_reference_sha256,
        "stage27_source": options.stage27_source_sha256,
        "stage27_protocol": options.stage27_protocol_sha256,
        "public_reference": options.public_reference_sha256,
    })


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "source_sha256", "protocol_sha256", "v6_reference_sha256",
            "stage27_source_sha256", "stage27_protocol_sha256",
            "public_reference_sha256",
        )), "a source-only test cannot consume reference or production pins")
        observed = source_self_test()
    elif options.self_oracle:
        observed = run_self_oracle(_option_pins(options))
    else:
        observed = run_reference_worker(options.worker_role, _option_pins(options))
    sys.stdout.buffer.write(canonical(observed))
    sys.stdout.buffer.flush()
    return 0 if observed.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
