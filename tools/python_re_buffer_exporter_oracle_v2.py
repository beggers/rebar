#!/usr/bin/env python3
"""Candidate-free, phase-exact PEP 688 regex lifetime and V1 failure oracle.

Source controls are standalone and perform no production imports or I/O.
Only a separately authorized actual self-oracle may import the immutable V1
reference authenticators and start two genuine standard-library workers.
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
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SCHEMA = "rebar-python-re-pep688-buffer-exporter-v2"
SOURCE_RELATIVE = "tools/python_re_buffer_exporter_oracle_v2.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V2.md"
PROTOCOL_SHA256 = (
    "a34f68399982b6ecf45a443664d290132a463dd6824d2bf797e8a470eb0c3458"
)
V1_SOURCE_RELATIVE = "tools/python_re_buffer_exporter_oracle_v1.py"
V1_SOURCE_SHA256 = (
    "1f60401fa24717c502e147509d1aa625c05bd1cc3aa27b0d1f6ce84783309af7"
)
V1_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V1.md"
V1_PROTOCOL_SHA256 = (
    "30587b78d2752f9e9a1eeeaa4cef89e09ad75ccd39989bd5eb2d84f136c99dad"
)
V1_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v1-self-oracle-failures.json"
)
V1_FAILURE_SHA256 = (
    "f38c8b3dd1faaaa6197a1cf4698a51f830398a3d26c3527302607ed0136fb5ae"
)
V1_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v1-self-oracle-failure-publication-receipt.json"
)
V1_RECEIPT_SHA256 = (
    "f68612336528f5660805d2bec5a5c2316f891651cdef3a4ee4d3253960c80f82"
)
V1_STDERR_SHA256 = (
    "4f395284262fb5264a734336016e8acfa18d7860ecb55433fa0e0dd670d14f73"
)
V1_STDERR_BYTES = 1_657
EMPTY_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
V6_REFERENCE_SHA256 = (
    "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
)
V27_SOURCE_SHA256 = (
    "fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b"
)
V27_PROTOCOL_SHA256 = (
    "c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f"
)
PUBLIC_REFERENCE_SHA256 = (
    "a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8"
)
PUBLIC_RECORD_SHA256 = (
    "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef"
)
MATRIX_SHA256 = (
    "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891"
)
REFERENCE_LABELS = ("reference_a", "reference_b")
ORIGINAL_METHOD_COUNT = 165
PUBLIC_METHOD_COUNT = 152
PRIVATE_WAIVER_COUNT = 13
PUBLIC_CASE_COUNT = 1_376
PUBLIC_COHORT_COUNT = 43
BUFFER_CASE_COUNT = 264
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_REFERENCE_BYTES = 32 * 1024 * 1024
MAX_WORKER_BYTES = 16 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 120
PRIVATE_METHOD_NAMES = (
    "DebugTests.test_debug_flag", "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one", "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable", "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness",
    "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules",
    "ImplementationTest.test_case_helpers", "ImplementationTest.test_dealloc",
    "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
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
    "module.sub", "module.subn", "pattern.sub", "pattern.subn", "scanner.scan",
)
RETAINED_OPERATIONS = (
    "module.finditer", "pattern.finditer", "pattern.scanner", "match.group",
)
SUCCESS_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-buffer-exporter-v2-self-oracle.json"
)
FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v2-self-oracle-failures.json"
)
SUCCESS_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v2-self-oracle-publication-receipt.json"
)
FAILURE_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-buffer-exporter-v2-self-oracle-failure-publication-receipt.json"
)
APPROVED_OUTPUTS = frozenset({
    SUCCESS_RELATIVE, FAILURE_RELATIVE,
    SUCCESS_RECEIPT_RELATIVE, FAILURE_RECEIPT_RELATIVE,
})


class BufferExporterOracleError(Exception):
    """Reject a forged case, unsafe lifetime, or actual provenance mismatch."""


class SourceOnlyBoundaryError(BufferExporterOracleError):
    """An actual outside effect was correctly intercepted."""


class CallbackProbeError(Exception):
    """A real, deliberately observed replacement or scanner failure."""


class ActualReferenceWorkerFailure(BufferExporterOracleError):
    """Retain actual completed case prefixes and genuine worker streams."""

    def __init__(self, message: str, details: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.details = dict(details)


class ActualPublicationFailure(BufferExporterOracleError):
    """Keep first and all real publication/cleanup errors and pending calls."""

    def __init__(self, message: str, details: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BufferExporterOracleError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_sha256(value: Any) -> bool:
    return type(value) is str and len(value) == 64 and len(set(value)) > 1 \
        and all(character in "0123456789abcdef" for character in value)


def build_matrix() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    def add(scenario: str, operation: str, carrier: tuple[str, bool, bool]) -> None:
        result.append({
            "case": "buffer-exporter.v1." + format(len(result), "03d"),
            "scenario": scenario, "operation": operation,
            "carrier": carrier[0], "wrapped": carrier[1],
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
    return result


def validate_matrix(rows: Any) -> str:
    require(type(rows) is list and len(rows) == BUFFER_CASE_COUNT
            and rows == build_matrix()
            and digest(rows) == MATRIX_SHA256
            and len({row["case"] for row in rows}) == BUFFER_CASE_COUNT,
            "all 264 exact immutable V1 exporter identities are mandatory")
    return MATRIX_SHA256


def safe_relative(relative: Any, *, output: bool = False) -> Path:
    require(type(relative) is str, "an exact repository-relative path is required")
    pure = PurePosixPath(relative)
    require(not pure.is_absolute() and ".." not in pure.parts
            and "\\" not in relative and "\x00" not in relative
            and pure.as_posix() == relative,
            "an escaping, substituted, or noncanonical path is forbidden")
    require(not output or relative in APPROVED_OUTPUTS,
            "only the four fresh V2 evidence paths are permitted")
    return ROOT.joinpath(*pure.parts)


def _read_regular(relative: str, expected: str, maximum: int) -> bytes:
    require(valid_sha256(expected) and type(maximum) is int and maximum > 0,
            "an independently frozen digest and bounded read are mandatory")
    descriptor = os.open(
        safe_relative(relative),
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode) and 0 < info.st_size <= maximum,
                "an actual frozen prerequisite is not a bounded regular file")
        chunks: list[bytes] = []
        remaining = info.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(chunk), "an actual frozen prerequisite was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(not os.read(descriptor, 1),
                "an actual frozen prerequisite grew during authentication")
    finally:
        os.close(descriptor)
    actual = b"".join(chunks)
    require(hashlib.sha256(actual).hexdigest() == expected,
            "actual immutable prerequisite bytes changed: " + relative)
    return actual


def _unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    actual: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in actual,
                "duplicate JSON keys cannot hide a genuine original failure")
        actual[key] = value
    return actual


def decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and bool(raw),
            "complete actual surrogate-safe JSON is required: " + label)
    try:
        actual = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                BufferExporterOracleError("nonfinite JSON is forbidden"),
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise BufferExporterOracleError(
            "invalid strict canonical actual Python evidence: " + label,
        ) from error
    require(type(actual) is dict and canonical(actual) == raw,
            "actual complete canonical Python evidence changed: " + label)
    return actual


def capture_stream(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_WORKER_BYTES,
            "complete bounded actual worker output is required: " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def restore_stream(record: Any, label: str) -> bytes:
    require(type(record) is dict
            and set(record) == {"base64", "bytes", "sha256", "complete"}
            and type(record.get("base64")) is str
            and type(record.get("bytes")) is int
            and 0 <= record["bytes"] <= MAX_WORKER_BYTES
            and valid_sha256(record.get("sha256"))
            and record.get("complete") is True,
            "an actual complete reference-worker stream was forged: " + label)
    try:
        actual = base64.b64decode(record["base64"], validate=True)
    except (ValueError, base64.binascii.Error) as error:
        raise BufferExporterOracleError(
            "invalid complete reference-worker encoding: " + label,
        ) from error
    require(len(actual) == record["bytes"]
            and hashlib.sha256(actual).hexdigest() == record["sha256"]
            and capture_stream(actual, label) == record,
            "actual complete reference-worker bytes changed: " + label)
    return actual


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "use exactly isolated pinned no-bytecode CPython 3.14.6")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a matching candidate escaped into original-only authentication")


def validate_pins(pins: Any) -> dict[str, str]:
    require(type(pins) is dict and set(pins) == {
        "source", "protocol", "v1_source", "v1_protocol",
        "v1_failure", "v1_receipt", "v6_reference", "stage27_source",
        "stage27_protocol", "public_reference",
    }, "supply all exact V2 and genuine immutable failed-history pins")
    require(all(valid_sha256(value) for value in pins.values()),
            "every actual externally supplied canonical SHA-256 is required")
    expected = {
        "protocol": PROTOCOL_SHA256,
        "v1_source": V1_SOURCE_SHA256,
        "v1_protocol": V1_PROTOCOL_SHA256,
        "v1_failure": V1_FAILURE_SHA256,
        "v1_receipt": V1_RECEIPT_SHA256,
        "v6_reference": V6_REFERENCE_SHA256,
        "stage27_source": V27_SOURCE_SHA256,
        "stage27_protocol": V27_PROTOCOL_SHA256,
        "public_reference": PUBLIC_REFERENCE_SHA256,
    }
    for name, expected_hash in expected.items():
        require(pins[name] == expected_hash,
                "an exact independently frozen V2 prerequisite changed: " + name)
    return dict(pins)


def validate_v1_failure(
    failure: Any, receipt: Any, *, report_bytes: bytes,
) -> dict[str, Any]:
    require(type(failure) is dict and type(receipt) is dict,
            "the complete real first failure and durable receipt are mandatory")
    expected_failure = {
        "schema": "rebar-python-re-pep688-buffer-exporter-v1-actual-self-oracle-failure",
        "status": "FAIL", "python": "3.14.6",
        "source_sha256": V1_SOURCE_SHA256,
        "protocol_sha256": V1_PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": BUFFER_CASE_COUNT,
        "actual_completed_reference_count": 0,
        "failure_type": "ActualReferenceWorkerFailure",
        "failure_message": "the genuine Python buffer-reference worker did not pass",
        "actual_candidate_workers": 0,
        "holdout_cases_read": 0, "performance_fixtures_read": 0,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "synthetic": False,
    }
    for key, value in expected_failure.items():
        require(failure.get(key) == value,
                "the genuine first V1 failure was altered: " + key)
    require(failure.get("actual_completed_reference_roles") == {}
            and failure.get("actual_completed_reference_processes") == {},
            "the first genuine V1 failure published no complete case vector")
    worker = failure.get("actual_failed_worker")
    require(type(worker) is dict
            and set(worker) == {"role", "pid", "returncode", "stdout", "stderr"}
            and worker.get("role") == "reference_a"
            and type(worker.get("pid")) is int and worker["pid"] > 0
            and worker.get("returncode") == 1,
            "the exact genuine first failed V1 reference process was substituted")
    stdout = restore_stream(worker.get("stdout"), "actual first V1 stdout")
    stderr = restore_stream(worker.get("stderr"), "actual first V1 stderr")
    require(stdout == b"" and len(stderr) == V1_STDERR_BYTES
            and hashlib.sha256(stderr).hexdigest() == V1_STDERR_SHA256
            and b"_validate_event_ledger" in stderr
            and b"acquired buffer was dereferenced, leaked, or miscounted"
            in stderr,
            "the complete genuine 1,657-byte first traceback was changed")
    expected_receipt = {
        "schema": "rebar-python-re-pep688-buffer-exporter-v1-actual-exclusive-publication-receipt",
        "status": "PASS", "path": V1_FAILURE_RELATIVE,
        "sha256": V1_FAILURE_SHA256,
        "bytes": len(report_bytes),
        "actual_write_calls": 1,
        "actual_bytes_written": len(report_bytes),
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "exact_canonical_readback_verified": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "synthetic": False,
    }
    for key, value in expected_receipt.items():
        require(receipt.get(key) == value,
                "the genuine separately durable V1 receipt changed: " + key)
    require(hashlib.sha256(report_bytes).hexdigest() == receipt["sha256"],
            "the real durable first receipt is unbound from its exact failure")
    return {
        "failure_sha256": V1_FAILURE_SHA256,
        "failure_bytes": len(report_bytes),
        "receipt_sha256": V1_RECEIPT_SHA256,
        "actual_failed_role": "reference_a",
        "actual_failed_returncode": 1,
        "actual_stdout_bytes": 0,
        "actual_stderr_bytes": V1_STDERR_BYTES,
        "actual_stderr_sha256": V1_STDERR_SHA256,
        "actual_completed_reference_count": 0,
        "failed_case_identity": "NOT CAPTURED",
        "failure_qualifies_candidate": False,
        "failure_qualifies_reference": False,
    }


def authenticate_prerequisites(pins: dict[str, str]) -> dict[str, Any]:
    verify_runtime()
    supplied = validate_pins(pins)
    for relative, expected in (
        (SOURCE_RELATIVE, supplied["source"]),
        (PROTOCOL_RELATIVE, PROTOCOL_SHA256),
        (V1_SOURCE_RELATIVE, V1_SOURCE_SHA256),
        (V1_PROTOCOL_RELATIVE, V1_PROTOCOL_SHA256),
    ):
        _read_regular(relative, expected, MAX_SOURCE_BYTES)
    failed_raw = _read_regular(
        V1_FAILURE_RELATIVE, V1_FAILURE_SHA256, MAX_REFERENCE_BYTES,
    )
    receipt_raw = _read_regular(
        V1_RECEIPT_RELATIVE, V1_RECEIPT_SHA256, MAX_REFERENCE_BYTES,
    )
    preserved = validate_v1_failure(
        decode_canonical(failed_raw, "complete real first V1 failure"),
        decode_canonical(receipt_raw, "complete separately durable V1 receipt"),
        report_bytes=failed_raw,
    )
    frozen = importlib.import_module("tools.python_re_buffer_exporter_oracle_v1")
    require(os.path.abspath(frozen.__file__) == str(ROOT / V1_SOURCE_RELATIVE)
            and frozen.PROTOCOL_SHA256 == V1_PROTOCOL_SHA256
            and frozen.MATRIX_SHA256 == MATRIX_SHA256
            and frozen.build_matrix() == build_matrix(),
            "the immutable original V1 case graph was substituted")
    legacy = frozen.authenticate_reference_prerequisites({
        "source": V1_SOURCE_SHA256,
        "protocol": V1_PROTOCOL_SHA256,
        "v6_reference": V6_REFERENCE_SHA256,
        "stage27_source": V27_SOURCE_SHA256,
        "stage27_protocol": V27_PROTOCOL_SHA256,
        "public_reference": PUBLIC_REFERENCE_SHA256,
    })
    require(type(legacy) is dict
            and legacy.get("original_method_count") == ORIGINAL_METHOD_COUNT
            and legacy.get("original_public_method_count") == PUBLIC_METHOD_COUNT
            and legacy.get("original_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and tuple(legacy.get("original_private_method_names", ()))
            == PRIVATE_METHOD_NAMES
            and legacy.get("original_v6_reference_sha256") == V6_REFERENCE_SHA256
            and legacy.get("stage27_source_sha256") == V27_SOURCE_SHA256
            and legacy.get("stage27_protocol_sha256") == V27_PROTOCOL_SHA256
            and legacy.get("public_reference_sha256") == PUBLIC_REFERENCE_SHA256
            and legacy.get("public_reference_record_sha256") == PUBLIC_RECORD_SHA256
            and legacy.get("unchanged_public_cases") == PUBLIC_CASE_COUNT
            and legacy.get("unchanged_public_cohorts") == PUBLIC_COHORT_COUNT
            and legacy.get("public_reference_workers") == 2
            and legacy.get("public_reference_locale_cases_per_worker") == 64
            and legacy.get("public_reference_locale_transitions_per_worker") == 192
            and legacy.get("buffer_exporter_cases") == BUFFER_CASE_COUNT
            and legacy.get("buffer_exporter_matrix_sha256") == MATRIX_SHA256,
            "the actual complete immutable V6/V27/V19 original references changed")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate escaped into genuine original reference validation")
    return {
        "source_sha256": supplied["source"],
        "protocol_sha256": PROTOCOL_SHA256,
        "preserved_v1_failure": preserved,
        "authenticated_original_reference": legacy,
        "original_method_count": ORIGINAL_METHOD_COUNT,
        "original_public_method_count": PUBLIC_METHOD_COUNT,
        "original_private_method_names": list(PRIVATE_METHOD_NAMES),
        "public_case_count": PUBLIC_CASE_COUNT,
        "public_cohort_count": PUBLIC_COHORT_COUNT,
        "matrix_sha256": MATRIX_SHA256,
        "buffer_case_count": BUFFER_CASE_COUNT,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


class PoisonOnReleaseExporter:
    """A real Python-owned exporter that poisons only still-owned storage."""

    def __init__(self, payload: bytes, readonly: bool) -> None:
        require(type(payload) is bytes and type(readonly) is bool,
                "an actual immutable Python exporter configuration is required")
        self.storage = bytearray(payload)
        self.readonly = readonly
        self.events: list[list[Any]] = []
        self.acquisitions = 0
        self.releases = 0

    def __buffer__(self, flags: int) -> memoryview:
        require(type(flags) is int and flags >= 0,
                "CPython must supply genuine nonnegative buffer flags")
        self.acquisitions += 1
        self.events.append([
            "acquire", self.acquisitions, flags,
            self.readonly, bytes(self.storage).hex(),
        ])
        view = memoryview(self.storage)
        return view.toreadonly() if self.readonly else view

    def __release_buffer__(self, view: memoryview) -> None:
        require(isinstance(view, memoryview),
                "CPython must deliver its genuine acquired exporter view")
        self.releases += 1
        before = bytes(self.storage).hex()
        for index in range(len(self.storage)):
            self.storage[index] = 0x21
        self.events.append([
            "release", self.releases, before, bytes(self.storage).hex(),
        ])


def observe_value(value: Any, regex: Any) -> Any:
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
            "kind": "match", "group": observe_value(value.group(), regex),
            "span": list(value.span()),
            "groups": [observe_value(group, regex) for group in value.groups()],
            "lastindex": value.lastindex, "lastgroup": value.lastgroup,
            "pos": value.pos, "endpos": value.endpos,
        }
    if isinstance(value, (list, tuple)):
        return {
            "kind": "list" if isinstance(value, list) else "tuple",
            "items": [observe_value(item, regex) for item in value],
        }
    if isinstance(value, dict):
        return {
            "kind": "mapping",
            "items": [
                [str(key), observe_value(item, regex)]
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            ],
        }
    raise BufferExporterOracleError(
        "a real reference returned an unrepresentable object: "
        + type(value).__qualname__,
    )


def observe_exception(error: Exception, regex: Any) -> dict[str, Any]:
    return {
        "module": type(error).__module__,
        "type": type(error).__qualname__,
        "args": observe_value(error.args, regex),
    }


def create_callback(
    events: list[list[Any]], *, fail: bool,
) -> Callable[..., bytes]:
    def callback(*arguments: Any) -> bytes:
        token = arguments[-1]
        if hasattr(token, "group"):
            token = token.group()
        events.append([
            "callback",
            bytes(token).hex()
            if isinstance(token, (bytes, bytearray, memoryview)) else None,
            fail,
        ])
        if fail:
            raise CallbackProbeError("genuine buffer exporter callback failure")
        return b"X"

    return callback


def dispatch_operation(
    regex: Any, operation: str, subject: Any,
    events: list[list[Any]], *, callback_error: bool,
) -> Any:
    expression = b"a+"
    compiled = regex.compile(expression)
    callback = create_callback(events, fail=callback_error)
    if operation.startswith("module."):
        name = operation.split(".", 1)[1]
        method = getattr(regex, name)
        result = (
            method(expression, callback if callback_error else b"X", subject)
            if name in ("sub", "subn") else method(expression, subject)
        )
        return list(result) if name == "finditer" else result
    if operation.startswith("pattern."):
        name = operation.split(".", 1)[1]
        if name == "scanner":
            scanner = compiled.scanner(subject)
            return {"first": scanner.search(), "second": scanner.search()}
        method = getattr(compiled, name)
        result = (
            method(callback if callback_error else b"X", subject)
            if name in ("sub", "subn") else method(subject)
        )
        return list(result) if name == "finditer" else result
    if operation == "match.group":
        match = compiled.search(subject)
        if match is None:
            return None
        return {"group": match.group(), "span": match.span(),
                "groups": match.groups()}
    if operation == "scanner.scan":
        scanner = regex.Scanner([
            (rb"a+", lambda scanner, token: callback(scanner, token)),
            (rb".", None),
        ])
        return scanner.scan(subject)
    raise BufferExporterOracleError("an unfrozen original operation was injected")


def capture_operation(
    regex: Any, operation: str, subject: Any,
    events: list[list[Any]], *, callback_error: bool,
) -> dict[str, Any]:
    events.append(["call-start", operation])
    try:
        result = dispatch_operation(
            regex, operation, subject, events, callback_error=callback_error,
        )
        events.append(["result-live", operation])
        observed = observe_value(result, regex)
        events.append(["result-materialized", operation])
        del result
        events.append(["result-dropped", operation])
    except BufferExporterOracleError:
        raise
    except Exception as error:
        events.append(["call-raise", operation, type(error).__qualname__])
        return {"status": "raise", "exception": observe_exception(error, regex)}
    events.append(["call-return", operation])
    return {"status": "return", "value": observed}


def retained_holder(regex: Any, operation: str, subject: Any) -> Any:
    compiled = regex.compile(b"a+")
    if operation == "module.finditer":
        return regex.finditer(b"a+", subject)
    if operation == "pattern.finditer":
        return compiled.finditer(subject)
    if operation == "pattern.scanner":
        return compiled.scanner(subject)
    if operation == "match.group":
        return compiled.search(subject)
    raise BufferExporterOracleError("an unfrozen live native holder was injected")


def consume_holder(regex: Any, operation: str, holder: Any) -> Any:
    if operation in ("module.finditer", "pattern.finditer"):
        return list(holder)
    if operation == "pattern.scanner":
        return {"first": holder.search(), "second": holder.search()}
    if operation == "match.group":
        return holder
    raise BufferExporterOracleError("an unfrozen live holder was consumed")


def buffer_observation(payload: bytes, events: list[list[Any]]) -> dict[str, Any]:
    acquisitions = [row for row in events if row and row[0] == "acquire"]
    releases = [row for row in events if row and row[0] == "release"]
    return {
        "initial_hex": payload.hex(),
        "final_hex": releases[-1][3] if releases else payload.hex(),
        "byte_length": len(payload),
        "acquisitions": len(acquisitions), "releases": len(releases),
    }


def execute_case(case: Mapping[str, Any], regex: Any) -> dict[str, Any]:
    scenario = case["scenario"]
    payload = b"zzz" if scenario == "no-match" else b"aaa"
    owner = PoisonOnReleaseExporter(payload, case["readonly"])
    events = owner.events
    wrapped = memoryview(owner) if case["wrapped"] else None
    subject: Any = wrapped if wrapped is not None else owner
    results: list[dict[str, Any]] = []
    lifetime: dict[str, Any] = {}

    if scenario == "retained":
        events.append(["retained-create", case["operation"]])
        try:
            holder = retained_holder(regex, case["operation"], subject)
        except BufferExporterOracleError:
            raise
        except Exception as error:
            events.append(["retained-create-raise", type(error).__qualname__])
            results.append({
                "status": "raise", "exception": observe_exception(error, regex),
            })
            lifetime = {
                "holder_created": False,
                "owner_alive_while_holder_live": None,
                "carrier_supports_weakref": None,
                "carrier_alive_while_holder_live": None,
                "owner_alive_after_cyclic_gc": None,
                "carrier_alive_after_cyclic_gc": None,
            }
        else:
            owner.cyclic_holder = holder
            owner_ref = weakref.ref(owner)
            try:
                carrier_ref: weakref.ReferenceType[Any] | None = weakref.ref(subject)
            except TypeError:
                carrier_ref = None
            wrapped = None
            del subject
            del owner
            gc.collect()
            lifetime = {
                "holder_created": True,
                "owner_alive_while_holder_live": owner_ref() is not None,
                "carrier_supports_weakref": carrier_ref is not None,
                "carrier_alive_while_holder_live": (
                    carrier_ref() is not None if carrier_ref is not None else None
                ),
            }
            events.append([
                "retained-gc-while-live",
                lifetime["owner_alive_while_holder_live"],
                lifetime["carrier_alive_while_holder_live"],
            ])
            try:
                actual = consume_holder(regex, case["operation"], holder)
                events.append(["holder-result-live", case["operation"]])
                observed = observe_value(actual, regex)
                events.append(["holder-result-materialized", case["operation"]])
                del actual
                events.append(["holder-result-dropped", case["operation"]])
                results.append({"status": "return", "value": observed})
            except BufferExporterOracleError:
                raise
            except Exception as error:
                results.append({
                    "status": "raise", "exception": observe_exception(error, regex),
                })
            events.append(["cleanup-start"])
            del holder
            gc.collect()
            lifetime["owner_alive_after_cyclic_gc"] = owner_ref() is not None
            lifetime["carrier_alive_after_cyclic_gc"] = (
                carrier_ref() is not None if carrier_ref is not None else None
            )
            events.append([
                "retained-gc-after-drop",
                lifetime["owner_alive_after_cyclic_gc"],
                lifetime["carrier_alive_after_cyclic_gc"],
            ])
            events.append(["cleanup-complete"])
            events.append(["case-finish", buffer_observation(payload, events)["final_hex"]])
            return {
                **dict(case), "results": results, "events": copy.deepcopy(events),
                "lifetime": lifetime, "buffer": buffer_observation(payload, events),
            }

    if scenario != "retained":
        for _ in range(2 if scenario == "repeat" else 1):
            results.append(capture_operation(
                regex, case["operation"], subject, events,
                callback_error=scenario == "callback-error",
            ))
    events.append(["cleanup-start"])
    if wrapped is not None:
        events.append(["wrapped-release-start"])
        wrapped.release()
        events.append(["wrapped-release-finish"])
    gc.collect()
    events.append(["cleanup-complete"])
    events.append(["case-finish", bytes(owner.storage).hex()])
    return {
        **dict(case), "results": results, "events": copy.deepcopy(events),
        "lifetime": lifetime, "buffer": buffer_observation(payload, events),
    }


def valid_hex(value: Any, size: int) -> bool:
    if type(value) is not str or len(value) != 2 * size:
        return False
    try:
        return bytes.fromhex(value).hex() == value
    except ValueError:
        return False


def validate_event_ledger(
    events: Any, expected: Mapping[str, Any], observed_buffer: Any,
    outcomes: Any, lifetime: Any,
) -> None:
    require(type(events) is list and bool(events),
            "a real exporter cannot have an empty or hidden event ledger")
    require(type(observed_buffer) is dict
            and set(observed_buffer) == {
                "initial_hex", "final_hex", "byte_length",
                "acquisitions", "releases",
            }, "the complete original exporter storage evidence was lost")
    payload = b"zzz" if expected["scenario"] == "no-match" else b"aaa"
    require(observed_buffer.get("initial_hex") == payload.hex()
            and observed_buffer.get("byte_length") == len(payload),
            "the actual original payload or exact buffer length changed")
    current = payload.hex()
    acquisitions = 0
    releases = 0
    active = False
    result_live = False
    result_materialized = False
    result_dropped = False
    call_count = 0
    call_finishes = 0
    callback_count = 0
    cleanup_started = False
    cleanup_finished = False
    terminal = False
    wrapped_started = False
    wrapped_finished = False
    retained_created = False
    retained_failed = False
    retained_live = False
    retained_dropped = False
    retained_live_values: tuple[Any, Any] | None = None
    retained_drop_values: tuple[Any, Any] | None = None
    for index, event in enumerate(events):
        require(type(event) is list and bool(event) and type(event[0]) is str,
                "every actual buffer event must retain its exact typed arity")
        kind = event[0]
        if kind == "acquire":
            require(len(event) == 5 and type(event[1]) is int
                    and event[1] == acquisitions + 1
                    and type(event[2]) is int and event[2] >= 0
                    and type(event[3]) is bool
                    and event[3] is expected["readonly"]
                    and event[4] == current
                    and (active or expected["wrapped"] or retained_created),
                    "a real PEP 688 acquisition was forged or reordered")
            acquisitions += 1
        elif kind == "release":
            require(len(event) == 4 and type(event[1]) is int
                    and event[1] == releases + 1
                    and event[1] <= acquisitions and event[2] == current
                    and event[3] == (b"!" * len(payload)).hex(),
                    "a real in-place release or exact poison was forged")
            releases += 1
            current = event[3]
        elif kind == "call-start":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and not active and not cleanup_started,
                    "a real regex operation was omitted or reordered")
            call_count += 1
            active = True
            result_live = result_materialized = result_dropped = False
        elif kind == "result-live":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and active and not result_live,
                    "the actual returned holder was not genuinely retained")
            result_live = True
        elif kind == "result-materialized":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and active and result_live and not result_materialized,
                    "the actual result was inspected after being discarded")
            result_materialized = True
        elif kind == "result-dropped":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and active and result_materialized and not result_dropped,
                    "the actual result was dropped before full materialization")
            result_dropped = True
        elif kind == "call-return":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and active and result_live and result_materialized
                    and result_dropped,
                    "a successful regex call concealed its real result lifetime")
            active = False
            call_finishes += 1
        elif kind == "call-raise":
            require(len(event) == 3 and event[1] == expected["operation"]
                    and type(event[2]) is str and active,
                    "a genuine Python regex error was forged")
            active = False
            call_finishes += 1
        elif kind == "callback":
            require(len(event) == 3 and type(event[2]) is bool
                    and event[2] is (expected["scenario"] == "callback-error")
                    and (event[1] is None or (
                        type(event[1]) is str
                        and valid_hex(event[1], len(event[1]) // 2)
                    )), "an actual scanner or replacement callback was forged")
            callback_count += 1
        elif kind == "retained-create":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and expected["scenario"] == "retained"
                    and not retained_created,
                    "an actual iterator, scanner, or match was replaced")
            retained_created = True
        elif kind == "retained-create-raise":
            require(len(event) == 2 and type(event[1]) is str
                    and retained_created and not retained_failed,
                    "a genuine unsupported retained carrier error was forged")
            retained_failed = True
        elif kind == "retained-gc-while-live":
            require(len(event) == 3 and type(event[1]) is bool
                    and (event[2] is None or type(event[2]) is bool)
                    and retained_created and not retained_failed
                    and not retained_live,
                    "a genuine live cyclic holder observation was removed")
            retained_live = True
            retained_live_values = (event[1], event[2])
        elif kind == "holder-result-live":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and retained_live and not result_live,
                    "a real cyclic holder result was not kept alive")
            result_live = True
        elif kind == "holder-result-materialized":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and retained_live and result_live
                    and not result_materialized,
                    "a cyclic result was read after holder destruction")
            result_materialized = True
        elif kind == "holder-result-dropped":
            require(len(event) == 2 and event[1] == expected["operation"]
                    and result_materialized and not result_dropped,
                    "a cyclic result was dropped before serialization")
            result_dropped = True
        elif kind == "retained-gc-after-drop":
            require(len(event) == 3 and type(event[1]) is bool
                    and (event[2] is None or type(event[2]) is bool)
                    and cleanup_started and retained_live
                    and not retained_dropped,
                    "actual cyclic collection after holder cleanup was omitted")
            retained_dropped = True
            retained_drop_values = (event[1], event[2])
        elif kind == "cleanup-start":
            require(len(event) == 1 and not active and not cleanup_started,
                    "real final reference cleanup was forged")
            cleanup_started = True
        elif kind == "wrapped-release-start":
            require(len(event) == 1 and expected["wrapped"] is True
                    and cleanup_started and not wrapped_started,
                    "actual memoryview cleanup was injected or reordered")
            wrapped_started = True
        elif kind == "wrapped-release-finish":
            require(len(event) == 1 and wrapped_started and not wrapped_finished,
                    "actual memoryview release completion was lost")
            wrapped_finished = True
        elif kind == "cleanup-complete":
            require(len(event) == 1 and cleanup_started and not cleanup_finished
                    and not active,
                    "the real final cleanup completion was hidden")
            cleanup_finished = True
        elif kind == "case-finish":
            require(len(event) == 2 and event[1] == current
                    and cleanup_finished and not terminal
                    and index == len(events) - 1,
                    "the exact last actual buffer-lifetime event was forged")
            terminal = True
        else:
            raise BufferExporterOracleError(
                "an unfrozen actual buffer phase was introduced: " + kind,
            )
    require(cleanup_started and cleanup_finished and terminal
            and not active and acquisitions == releases
            and observed_buffer.get("acquisitions") == acquisitions
            and observed_buffer.get("releases") == releases
            and observed_buffer.get("final_hex") == current
            and valid_hex(current, len(payload)),
            "a real buffer remained live or changed after final reference cleanup")
    require(type(outcomes) is list
            and len(outcomes) == (2 if expected["scenario"] == "repeat" else 1),
            "a genuine result, failure, or repeated acquisition was skipped")
    if acquisitions == 0:
        require(expected["wrapped"] is False
                and all(type(value) is dict
                        and value.get("status") == "raise"
                        and type(value.get("exception")) is dict
                        and value["exception"].get("module") == "builtins"
                        and value["exception"].get("type") == "TypeError"
                        for value in outcomes)
                and callback_count == 0,
                "zero acquisitions are legal only for a genuine direct TypeError")
    if expected["scenario"] == "retained":
        require(retained_created and call_count == call_finishes == 0
                and type(lifetime) is dict
                and set(lifetime) == {
                    "holder_created", "owner_alive_while_holder_live",
                    "carrier_supports_weakref", "carrier_alive_while_holder_live",
                    "owner_alive_after_cyclic_gc", "carrier_alive_after_cyclic_gc",
                }, "a genuine retained scanner or match was removed")
        if retained_failed:
            require(lifetime["holder_created"] is False and acquisitions == 0
                    and not retained_live and not retained_dropped
                    and all(lifetime[key] is None for key in (
                        "owner_alive_while_holder_live",
                        "carrier_supports_weakref",
                        "carrier_alive_while_holder_live",
                        "owner_alive_after_cyclic_gc",
                        "carrier_alive_after_cyclic_gc",
                    )),
                    "a real retained carrier failure was misclassified")
        else:
            require(retained_live and retained_dropped
                    and lifetime["holder_created"] is True
                    and lifetime["owner_alive_while_holder_live"] is True
                    and lifetime["owner_alive_after_cyclic_gc"] is False
                    and type(lifetime["carrier_supports_weakref"]) is bool
                    and retained_live_values is not None
                    and retained_drop_values is not None
                    and retained_live_values[0]
                    is lifetime["owner_alive_while_holder_live"]
                    and retained_drop_values[0]
                    is lifetime["owner_alive_after_cyclic_gc"]
                    and retained_live_values[1]
                    is lifetime["carrier_alive_while_holder_live"]
                    and retained_drop_values[1]
                    is lifetime["carrier_alive_after_cyclic_gc"]
                    and (
                        (
                            lifetime["carrier_supports_weakref"] is True
                            and lifetime["carrier_alive_while_holder_live"] is True
                            and lifetime["carrier_alive_after_cyclic_gc"] is False
                        ) or (
                            lifetime["carrier_supports_weakref"] is False
                            and lifetime["carrier_alive_while_holder_live"] is None
                            and lifetime["carrier_alive_after_cyclic_gc"] is None
                        )
                    )
                    and (
                        expected["wrapped"] is True
                        or (
                            lifetime["carrier_supports_weakref"] is True
                            and lifetime["carrier_alive_while_holder_live"]
                            is lifetime["owner_alive_while_holder_live"]
                            and lifetime["carrier_alive_after_cyclic_gc"]
                            is lifetime["owner_alive_after_cyclic_gc"]
                        )
                    ),
                    "a real cyclic native holder was never observed")
    else:
        require(call_count == call_finishes == len(outcomes)
                and lifetime == {},
                "a genuine ordinary regex call or lifetime was forged")
        require(wrapped_started is expected["wrapped"]
                and wrapped_finished is expected["wrapped"],
                "an actual wrapped Python memoryview was not finally released")
    if expected["scenario"] == "callback-error" and acquisitions:
        require(callback_count > 0
                and any(value.get("status") == "raise"
                        and value.get("exception", {}).get("type")
                        == "CallbackProbeError"
                        for value in outcomes),
                "an actually failing scanner or replacement callback was hidden")


def validate_case_record(record: Any, expected: Mapping[str, Any]) -> None:
    require(type(record) is dict
            and set(record) == set(expected) | {
                "results", "events", "lifetime", "buffer",
            }
            and all(record.get(key) == value for key, value in expected.items()),
            "a complete immutable original buffer case was forged")
    results = record.get("results")
    require(type(results) is list,
            "all exact returned values and original exceptions are mandatory")
    for value in results:
        require(type(value) is dict and value.get("status") in ("return", "raise")
                and set(value) == (
                    {"status", "value"} if value.get("status") == "return"
                    else {"status", "exception"}
                ), "a genuine exact original Python case outcome was forged")
        if value.get("status") == "raise":
            error = value["exception"]
            require(type(error) is dict
                    and set(error) == {"module", "type", "args"}
                    and type(error["module"]) is str
                    and type(error["type"]) is str,
                    "an authentic Python exception identity was concealed")
    validate_event_ledger(
        record.get("events"), expected, record.get("buffer"),
        results, record.get("lifetime"),
    )


def validate_current_failed_case_identity(
    observed: Any, expected: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(observed) is dict and type(expected) in (dict,)
            and all(key in observed and observed[key] == value
                    for key, value in expected.items()),
            "a previous, omitted, or cross-case record cannot identify this failure")
    return dict(observed)


def validate_completed_case_prefix(
    records: Any, matrix: Any, failed_index: Any,
) -> list[dict[str, Any]]:
    require(type(records) is list and type(matrix) is list
            and type(failed_index) is int
            and 0 <= failed_index <= len(matrix)
            and len(records) == failed_index,
            "the actual completed original case prefix was forged or skipped")
    for expected, observed in zip(matrix[:failed_index], records, strict=True):
        validate_case_record(observed, expected)
    return list(records)


def run_reference_worker(role: str, pins: dict[str, str]) -> dict[str, Any]:
    require(role in REFERENCE_LABELS,
            "only independently isolated genuine standard-library roles are allowed")
    provenance = authenticate_prerequisites(pins)
    regex = importlib.import_module("re")
    require(regex.__name__ == "re" and type(regex.__file__) is str
            and os.path.abspath(regex.__file__).startswith(
                str(PINNED_PYTHON.parent.parent) + os.sep,
            )
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "the genuine original reference loaded a candidate or foreign engine")
    matrix = build_matrix()
    validate_matrix(matrix)
    records: list[dict[str, Any]] = []
    for index, case in enumerate(matrix):
        actual: dict[str, Any] | None = None
        try:
            actual = execute_case(case, regex)
            validate_case_record(actual, case)
        except Exception as error:
            details: dict[str, Any] = {
                "role": role, "first_failed_case_index": index,
                "first_failed_case_id": case["case"],
                "first_failed_case": dict(case),
                "completed_count": len(records),
                "completed_records": validate_completed_case_prefix(
                    records, matrix, index,
                ),
                "exception_module": type(error).__module__,
                "exception_type": type(error).__qualname__,
                "exception_message": str(error),
                "matrix_sha256": MATRIX_SHA256,
            }
            if actual is not None:
                try:
                    details["actual_failed_case_record"] = (
                        validate_current_failed_case_identity(actual, case)
                    )
                except BufferExporterOracleError:
                    details["actual_invalid_case_record"] = actual
            raise ActualReferenceWorkerFailure(
                "the actual first original buffer case failed: " + case["case"],
                details,
            ) from error
        records.append(actual)
    require(len(records) == BUFFER_CASE_COUNT,
            "one or more actual mandatory buffer cases were omitted")
    return {
        "schema": SCHEMA + "-actual-reference-worker",
        "status": "PASS", "python": "3.14.6", "role": role,
        "source_sha256": provenance["source_sha256"],
        "protocol_sha256": PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": BUFFER_CASE_COUNT,
        "records_sha256": digest(records), "records": records,
        "actual_candidate_workers": 0, "candidate_imports": 0,
        "holdout_cases_read": 0, "performance_fixtures_read": 0,
        "preserved_v1_failure_sha256": V1_FAILURE_SHA256,
        "preserved_v1_receipt_sha256": V1_RECEIPT_SHA256,
        "preserved_v1_failed_case_identity": "NOT CAPTURED",
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "synthetic": False,
    }


def validate_worker_document(
    document: Any, *, role: str, pins: Mapping[str, str],
) -> dict[str, Any]:
    require(type(document) is dict,
            "the complete authentic original V2 reference is mandatory")
    checks = {
        "schema": SCHEMA + "-actual-reference-worker",
        "status": "PASS", "python": "3.14.6", "role": role,
        "source_sha256": pins["source"],
        "protocol_sha256": PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": BUFFER_CASE_COUNT,
        "actual_candidate_workers": 0, "candidate_imports": 0,
        "holdout_cases_read": 0, "performance_fixtures_read": 0,
        "preserved_v1_failure_sha256": V1_FAILURE_SHA256,
        "preserved_v1_receipt_sha256": V1_RECEIPT_SHA256,
        "preserved_v1_failed_case_identity": "NOT CAPTURED",
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "synthetic": False,
    }
    for key, expected in checks.items():
        require(document.get(key) == expected,
                "an actual reference worker field was forged: " + key)
    rows = document.get("records")
    require(type(rows) is list and len(rows) == BUFFER_CASE_COUNT
            and document.get("records_sha256") == digest(rows),
            "all 264 actual original reference observations are required")
    for expected, observed in zip(build_matrix(), rows, strict=True):
        validate_case_record(observed, expected)
    return dict(document)


def validate_worker_process(
    process: Any, *, role: str, expected: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(process) is dict
            and set(process) == {"role", "pid", "returncode", "stdout", "stderr"}
            and process.get("role") == role
            and type(process.get("pid")) is int and process["pid"] > 0
            and type(process.get("returncode")) is int
            and process["returncode"] == 0,
            "the actual separately isolated worker process was substituted")
    stdout = restore_stream(process.get("stdout"), role + " actual stdout")
    stderr = restore_stream(process.get("stderr"), role + " actual stderr")
    require(stderr == b""
            and decode_canonical(stdout, role + " actual complete stdout")
            == dict(expected),
            "actual passing Python worker output changed or hid stderr")
    return dict(process)


def validate_child_worker_failure(
    document: Any, *, role: str, pins: Mapping[str, str],
) -> dict[str, Any]:
    require(type(document) is dict,
            "the actual failed child must emit complete canonical evidence")
    for key, expected in {
        "schema": SCHEMA + "-actual-reference-worker-failure",
        "status": "FAIL", "python": "3.14.6", "role": role,
        "source_sha256": pins["source"],
        "protocol_sha256": PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "error_type": "ActualReferenceWorkerFailure",
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "synthetic": False,
    }.items():
        require(document.get(key) == expected,
                "an actual failed child field was forged: " + key)
    details = document.get("details")
    require(type(details) is dict and details.get("role") == role
            and type(details.get("first_failed_case_index")) is int
            and 0 <= details["first_failed_case_index"] < BUFFER_CASE_COUNT,
            "the actual first failed original case was not identified")
    matrix = build_matrix()
    actual_case = matrix[details["first_failed_case_index"]]
    require(details.get("first_failed_case_id") == actual_case["case"]
            and details.get("first_failed_case") == actual_case
            and details.get("completed_count")
            == details["first_failed_case_index"]
            and details.get("matrix_sha256") == MATRIX_SHA256
            and type(details.get("exception_module")) is str
            and type(details.get("exception_type")) is str
            and type(details.get("exception_message")) is str,
            "the exact failed original case, exception, or prefix was forged")
    validate_completed_case_prefix(
        details.get("completed_records"), matrix,
        details["first_failed_case_index"],
    )
    if "actual_failed_case_record" in details:
        validate_current_failed_case_identity(
            details["actual_failed_case_record"], actual_case,
        )
    return dict(document)


def worker_arguments(role: str, pins: Mapping[str, str]) -> list[str]:
    arguments = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--worker-role", role,
    ]
    for flag, key in (
        ("--source-sha256", "source"),
        ("--protocol-sha256", "protocol"),
        ("--v1-source-sha256", "v1_source"),
        ("--v1-protocol-sha256", "v1_protocol"),
        ("--v1-failure-sha256", "v1_failure"),
        ("--v1-receipt-sha256", "v1_receipt"),
        ("--v6-reference-sha256", "v6_reference"),
        ("--stage27-source-sha256", "stage27_source"),
        ("--stage27-protocol-sha256", "stage27_protocol"),
        ("--public-reference-sha256", "public_reference"),
    ):
        arguments.extend((flag, pins[key]))
    return arguments


def run_isolated_reference(
    role: str, pins: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in REFERENCE_LABELS,
            "an unapproved original reference process cannot start")
    process = subprocess.Popen(
        worker_arguments(role, pins), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(ROOT), shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "LC_ALL": "C", "PATH": "/usr/bin:/bin",
        },
    )
    try:
        stdout, stderr = process.communicate(timeout=WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        process.kill()
        stdout, stderr = process.communicate()
        raise ActualReferenceWorkerFailure(
            "the actual original isolated buffer worker timed out",
            {
                "role": role, "pid": process.pid,
                "returncode": process.returncode,
                "stdout": capture_stream(stdout or b"", role + " stdout"),
                "stderr": capture_stream(stderr or b"", role + " stderr"),
            },
        ) from error
    observed = {
        "role": role, "pid": process.pid, "returncode": process.returncode,
        "stdout": capture_stream(stdout, role + " stdout"),
        "stderr": capture_stream(stderr, role + " stderr"),
    }
    if process.returncode != 0 or stderr:
        actual_failure: dict[str, Any] = dict(observed)
        if stdout:
            try:
                actual_failure["complete_worker_failure"] = (
                    validate_child_worker_failure(
                        decode_canonical(
                            stdout, role + " complete original failure",
                        ), role=role, pins=pins,
                    )
                )
            except BufferExporterOracleError as error:
                actual_failure["actual_child_failure_validation"] = {
                    "status": "FAIL",
                    "exception_module": type(error).__module__,
                    "exception_type": type(error).__qualname__,
                    "exception_message": str(error),
                    "failed_case_identity": "NOT AUTHENTICATED",
                }
        raise ActualReferenceWorkerFailure(
            "the actual genuine original V2 worker failed", actual_failure,
        )
    try:
        document = validate_worker_document(
            decode_canonical(stdout, role + " complete original stdout"),
            role=role, pins=pins,
        )
        validate_worker_process(observed, role=role, expected=document)
    except BufferExporterOracleError as error:
        raise ActualReferenceWorkerFailure(
            "the complete actual original V2 worker vector failed validation",
            {**observed, "actual_validation_failure": str(error)},
        ) from error
    return document, observed


def _record_syscall(
    ledger: list[dict[str, Any]], operation: str, target: str,
    call: Callable[..., Any], *arguments: Any,
    expected_kind: str | None = None,
    allow_empty_read: bool = False,
    validator: Callable[[Any], None] | None = None,
    **keywords: Any,
) -> Any:
    require(type(ledger) is list and type(operation) is str
            and type(target) is str,
            "every real publication operation needs an exact pending record")
    kind = expected_kind
    if kind is None:
        if operation.startswith("write-"):
            kind = "write"
        elif operation.startswith("read-"):
            kind = "read"
        elif operation.startswith("open-"):
            kind = "open"
        elif operation.startswith("fstat-") or operation.startswith("stat-"):
            kind = "stat"
        elif operation.startswith("fsync-"):
            kind = "fsync"
        elif operation.startswith("close-"):
            kind = "close"
        elif operation.startswith("unlink-"):
            kind = "unlink"
    entry: dict[str, Any] = {
        "operation": operation, "target": target,
        "status": "PENDING", "pending_recorded_before_syscall": True,
    }
    if type(keywords.get("dir_fd")) is int:
        entry["directory_descriptor"] = keywords["dir_fd"]
    if arguments and type(arguments[0]) is int and kind != "open":
        entry["descriptor"] = arguments[0]
    if kind == "write":
        require(len(arguments) >= 2 and type(arguments[1]) is bytes,
                "a real publication write needs complete immutable bytes")
        entry["requested_bytes"] = len(arguments[1])
        entry["requested_sha256"] = hashlib.sha256(arguments[1]).hexdigest()
    elif kind == "read":
        require(len(arguments) >= 2 and type(arguments[1]) is int
                and arguments[1] >= 0,
                "a real descriptor read needs an exact nonnegative byte count")
        entry["requested_bytes"] = arguments[1]
    ledger.append(entry)
    try:
        actual = call(*arguments, **keywords)
        if kind == "open":
            require(type(actual) is int and actual >= 0,
                    "a real opened descriptor must be a nonnegative exact int")
            entry["returned_descriptor"] = actual
        elif kind == "write":
            require(type(actual) is int,
                    "a real write count cannot be bool or a forged object")
            entry["returned_bytes"] = actual
            require(0 <= actual <= entry["requested_bytes"]
                    and actual == entry["requested_bytes"],
                    "a real write was zero, short, negative, or oversized")
        elif kind == "read":
            require(type(actual) is bytes,
                    "a real descriptor read must return exact bytes")
            entry["returned_bytes"] = len(actual)
            entry["returned_sha256"] = hashlib.sha256(actual).hexdigest()
            require(len(actual) <= entry["requested_bytes"]
                    and (allow_empty_read or (
                        bool(actual)
                        and len(actual) == entry["requested_bytes"]
                    )),
                    "a real descriptor read was zero, short, or oversized")
        elif kind == "stat":
            require(type(getattr(actual, "st_dev", None)) is int
                    and type(getattr(actual, "st_ino", None)) is int
                    and type(getattr(actual, "st_mode", None)) is int,
                    "an actual parent or report inode was not captured")
            entry["device"] = actual.st_dev
            entry["inode"] = actual.st_ino
            entry["mode"] = actual.st_mode
        elif kind in ("fsync", "close", "unlink"):
            require(actual is None,
                    "a real descriptor cleanup returned a forged success value")
        if validator is not None:
            validator(actual)
    except Exception as error:
        entry.update({
            "status": "FAIL", "error_type": type(error).__qualname__,
            "error_module": type(error).__module__,
            "errno": getattr(error, "errno", None),
            "message": str(error),
        })
        raise
    entry["status"] = "PASS"
    return actual


def _open_evidence_parent(
    relative: str, ledger: list[dict[str, Any]], owned: list[tuple[int, str]],
) -> tuple[int, str]:
    path = safe_relative(relative, output=True)
    parts = PurePosixPath(relative).parts
    require(parts[:-1] == ("oracle", "cpython-3.14.6", "evidence"),
            "only the exact component-owned evidence directory is permitted")
    flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    current = _record_syscall(
        ledger, "open-root-directory", str(ROOT), os.open, str(ROOT), flags,
    )
    owned.append((current, str(ROOT)))
    information = _record_syscall(
        ledger, "fstat-root-directory", str(ROOT), os.fstat, current,
        validator=lambda info: require(
            stat.S_ISDIR(info.st_mode),
            "the authentic repository root is not an actual directory",
        ),
    )
    prefix = str(ROOT)
    for name in parts[:-1]:
        prefix += "/" + name
        next_descriptor = _record_syscall(
            ledger, "open-relative-evidence-component", prefix,
            os.open, name, flags, dir_fd=current,
        )
        owned.append((next_descriptor, prefix))
        information = _record_syscall(
            ledger, "fstat-relative-evidence-component", prefix,
            os.fstat, next_descriptor,
            validator=lambda info: require(
                stat.S_ISDIR(info.st_mode),
                "an actual evidence component is not a no-follow directory",
            ),
        )
        current = next_descriptor
    require(path.name == parts[-1], "the exact safe evidence basename changed")
    return current, path.name


def _close_owned_descriptors(
    ledger: list[dict[str, Any]], owned: list[tuple[int, str]],
    *, closer: Callable[[int], Any] | None = None,
) -> list[dict[str, Any]]:
    actual_close = os.close if closer is None else closer
    require(callable(actual_close), "a genuine owned-descriptor closer is required")
    errors: list[dict[str, Any]] = []
    for descriptor, name in reversed(owned):
        try:
            _record_syscall(
                ledger, "close-owned-descriptor", name,
                actual_close, descriptor, expected_kind="close",
            )
        except Exception as error:
            errors.append({
                "operation": "close-owned-descriptor", "target": name,
                "error_type": type(error).__qualname__,
                "error_module": type(error).__module__,
                "errno": getattr(error, "errno", None),
                "message": str(error),
            })
    return errors


def _cleanup_error(operation: str, error: Exception) -> dict[str, Any]:
    return {
        "operation": operation,
        "error_type": type(error).__qualname__,
        "error_module": type(error).__module__,
        "errno": getattr(error, "errno", None),
        "message": str(error),
    }


def cleanup_created_partial(
    *, relative: str, directory: int, basename: str,
    writer: int, original_info: Any,
    ledger: list[dict[str, Any]],
    operations: Mapping[str, Callable[..., Any]] | None = None,
) -> dict[str, Any]:
    require(type(directory) is int and directory >= 0
            and type(writer) is int and writer >= 0
            and type(basename) is str and safe_relative(relative, output=True).name
            == basename,
            "only this actual newly created report can be cleaned up")
    actual_operations: Mapping[str, Callable[..., Any]] = (
        {"fstat": os.fstat, "stat": os.stat,
         "unlink": os.unlink, "fsync": os.fsync}
        if operations is None else operations
    )
    require(set(actual_operations) == {"fstat", "stat", "unlink", "fsync"}
            and all(callable(item) for item in actual_operations.values()),
            "an actual inode-proven cleanup operation was replaced")
    cleanup_errors: list[dict[str, Any]] = []
    info = original_info
    inode_proven = False
    unlinked = False
    directory_synced = False
    try:
        if info is None:
            info = _record_syscall(
                ledger, "fstat-partial-exclusive-writer", relative,
                actual_operations["fstat"], writer,
                expected_kind="stat",
                validator=lambda value: require(
                    stat.S_ISREG(value.st_mode),
                    "the actually created partial writer is not a regular file",
                ),
            )

        def same_original_inode(value: Any) -> None:
            require(stat.S_ISREG(value.st_mode)
                    and value.st_dev == info.st_dev
                    and value.st_ino == info.st_ino,
                    "refusing to remove a substituted or non-owned report inode")

        _record_syscall(
            ledger, "stat-created-partial-before-removal", relative,
            actual_operations["stat"], basename,
            dir_fd=directory, follow_symlinks=False,
            expected_kind="stat", validator=same_original_inode,
        )
        inode_proven = True
        _record_syscall(
            ledger, "unlink-inode-proven-exclusive-partial", relative,
            actual_operations["unlink"], basename,
            dir_fd=directory, expected_kind="unlink",
        )
        unlinked = True
    except Exception as error:
        cleanup_errors.append(_cleanup_error("remove-owned-partial", error))
    try:
        _record_syscall(
            ledger, "fsync-owned-parent-after-partial-cleanup", relative,
            actual_operations["fsync"], directory,
            expected_kind="fsync",
        )
        directory_synced = True
    except Exception as error:
        cleanup_errors.append(_cleanup_error("fsync-after-partial-cleanup", error))
    return {
        "attempted": True,
        "inode_proven": inode_proven,
        "removed_only_created_inode": unlinked,
        "directory_fsync_completed": directory_synced,
        "errors": cleanup_errors,
    }


def should_remove_created_partial(
    *, failed: bool, created: bool, publication_complete: bool,
) -> bool:
    require(type(failed) is bool and type(created) is bool
            and type(publication_complete) is bool,
            "actual publication and cleanup phases must be genuine booleans")
    require(not publication_complete or created,
            "a complete durable publication must own its created report")
    return failed and created and not publication_complete


def preflight_fresh_outputs() -> None:
    for relative in sorted(APPROVED_OUTPUTS):
        ledger: list[dict[str, Any]] = []
        owned: list[tuple[int, str]] = []
        first: BaseException | None = None
        try:
            directory, basename = _open_evidence_parent(relative, ledger, owned)
            try:
                _record_syscall(
                    ledger, "stat-approved-fresh-basename", relative,
                    os.stat, basename, dir_fd=directory, follow_symlinks=False,
                )
            except FileNotFoundError:
                pass
            else:
                raise BufferExporterOracleError(
                    "refusing to reuse a genuine V2 first-result path: " + relative,
                )
        except BaseException as error:
            first = error
        finally:
            cleanup = _close_owned_descriptors(ledger, owned)
        if first is not None or cleanup:
            raise ActualPublicationFailure(
                "actual secure V2 output preflight failed",
                {
                    "path": relative, "syscalls": ledger,
                    "first_error": (
                        {"type": type(first).__qualname__, "message": str(first)}
                        if first is not None else cleanup[0]
                    ),
                    "cleanup_errors": cleanup,
                },
            )


def write_exclusive(relative: str, payload: bytes) -> dict[str, Any]:
    require(type(payload) is bytes and 0 < len(payload) <= MAX_REFERENCE_BYTES,
            "one complete genuine canonical bounded write is mandatory")
    ledger: list[dict[str, Any]] = []
    owned: list[tuple[int, str]] = []
    result: dict[str, Any] | None = None
    first: Exception | None = None
    directory: int | None = None
    basename: str | None = None
    writer: int | None = None
    actual_file: Any = None
    created = False
    publication_complete = False
    partial_cleanup: dict[str, Any] | None = None
    try:
        directory, basename = _open_evidence_parent(relative, ledger, owned)
        flags = (
            os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        )
        writer = _record_syscall(
            ledger, "open-exclusive-report", relative,
            os.open, basename, flags, 0o644, dir_fd=directory,
        )
        owned.append((writer, relative + ":writer"))
        created = True
        actual_file = _record_syscall(
            ledger, "fstat-exclusive-report", relative, os.fstat, writer,
            validator=lambda info: require(
                stat.S_ISREG(info.st_mode),
                "the actual exclusively created report is not an ordinary file",
            ),
        )
        written = _record_syscall(
            ledger, "write-exclusive-report-once", relative,
            os.write, writer, payload,
        )
        require(type(written) is int and written == len(payload),
                "the actual single report write was incomplete")
        _record_syscall(ledger, "fsync-exclusive-report", relative, os.fsync, writer)
        read_flags = (
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        reader = _record_syscall(
            ledger, "open-same-directory-report-readback", relative,
            os.open, basename, read_flags, dir_fd=directory,
        )
        owned.append((reader, relative + ":reader"))
        read_info = _record_syscall(
            ledger, "fstat-same-inode-readback", relative,
            os.fstat, reader,
            validator=lambda info: require(
                stat.S_ISREG(info.st_mode)
                and info.st_dev == actual_file.st_dev
                and info.st_ino == actual_file.st_ino
                and info.st_size == len(payload),
                "an exclusively created report changed inode or byte count",
            ),
        )
        remaining = len(payload)
        chunks: list[bytes] = []
        while remaining:
            part = _record_syscall(
                ledger, "read-same-inode-report", relative,
                os.read, reader, min(remaining, 1024 * 1024),
            )
            require(type(part) is bytes and bool(part),
                    "the actual same-inode report readback was truncated")
            chunks.append(part)
            remaining -= len(part)
        trailer = _record_syscall(
            ledger, "read-same-inode-report-eof", relative,
            os.read, reader, 1,
            allow_empty_read=True,
        )
        require(trailer == b"" and b"".join(chunks) == payload,
                "actual original report bytes changed during secure readback")
        _record_syscall(
            ledger, "fsync-owned-evidence-directory", relative,
            os.fsync, directory,
        )
        publication_complete = True
        for descriptor, name in (
            (reader, relative + ":reader"),
            (writer, relative + ":writer"),
        ):
            _record_syscall(
                ledger, "close-verified-report-descriptor", name,
                os.close, descriptor, expected_kind="close",
            )
            owned.remove((descriptor, name))
        result = {
            "path": relative, "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload), "actual_write_calls": 1,
            "actual_bytes_written": written,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "exact_same_inode_readback_verified": True,
            "syscalls": ledger,
            "cleanup_errors": [],
        }
    except Exception as error:
        first = error
    finally:
        cleanup: list[dict[str, Any]] = []
        if should_remove_created_partial(
            failed=first is not None,
            created=created,
            publication_complete=publication_complete,
        ) and directory is not None \
                and basename is not None and writer is not None:
            try:
                partial_cleanup = cleanup_created_partial(
                    relative=relative, directory=directory,
                    basename=basename, writer=writer,
                    original_info=actual_file, ledger=ledger,
                )
                cleanup.extend(partial_cleanup["errors"])
            except Exception as error:
                cleanup.append(_cleanup_error("inode-proven-partial-cleanup", error))
        cleanup.extend(_close_owned_descriptors(ledger, owned))
    if first is not None or cleanup or result is None:
        raise ActualPublicationFailure(
            "the actual secure durable V2 publication failed",
            {
                "path": relative, "syscalls": ledger,
                "first_error": (
                    {"type": type(first).__qualname__, "message": str(first)}
                    if first is not None else cleanup[0] if cleanup else None
                ),
                "cleanup_errors": cleanup,
                "partial_cleanup": partial_cleanup,
                "publication_complete": publication_complete,
                "complete_published_report_retained": publication_complete,
            },
        )
    result["syscalls"] = ledger
    return result


def publish_exclusive(
    document: Mapping[str, Any], relative: str, receipt_relative: str,
) -> dict[str, Any]:
    require(relative in (SUCCESS_RELATIVE, FAILURE_RELATIVE)
            and receipt_relative == (
                SUCCESS_RECEIPT_RELATIVE if relative == SUCCESS_RELATIVE
                else FAILURE_RECEIPT_RELATIVE
            ), "a genuine V2 success/failure report and receipt were interchanged")
    report = write_exclusive(relative, canonical(dict(document)))
    receipt_document = {
        "schema": SCHEMA + "-actual-exclusive-publication-receipt",
        "status": "PASS", **report,
        "preserved_v1_failure_sha256": V1_FAILURE_SHA256,
        "preserved_v1_receipt_sha256": V1_RECEIPT_SHA256,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "synthetic": False,
    }
    receipt = write_exclusive(receipt_relative, canonical(receipt_document))
    return {"report": report, "receipt": receipt}


def run_self_oracle(pins: dict[str, str]) -> dict[str, Any]:
    provenance = authenticate_prerequisites(pins)
    validate_matrix(build_matrix())
    preflight_fresh_outputs()
    roles: dict[str, dict[str, Any]] = {}
    processes: dict[str, dict[str, Any]] = {}
    try:
        for role in REFERENCE_LABELS:
            actual, process = run_isolated_reference(role, pins)
            roles[role] = actual
            processes[role] = process
        require(processes["reference_a"]["pid"]
                != processes["reference_b"]["pid"],
                "the real two original worker processes are not independent")
        first = roles["reference_a"]["records"]
        require(first == roles["reference_b"]["records"]
                and roles["reference_a"]["records_sha256"]
                == roles["reference_b"]["records_sha256"] == digest(first),
                "the two actual full V2 Python buffer vectors disagree")
        document = {
            "schema": SCHEMA + "-self-oracle", "status": "PASS",
            "python": "3.14.6", "source_sha256": pins["source"],
            "protocol_sha256": PROTOCOL_SHA256,
            "matrix_sha256": MATRIX_SHA256, "case_count": BUFFER_CASE_COUNT,
            "actual_independent_reference_count": 2,
            "actual_reference_process_count": 2,
            "actual_case_executions": 2 * BUFFER_CASE_COUNT,
            "reference_vector_sha256": digest(first),
            "reference_worker_reports": roles,
            "reference_worker_processes": processes,
            "frozen_prerequisites": provenance,
            "actual_candidate_workers": 0, "candidate_imports": 0,
            "holdout_cases_read": 0, "performance_fixtures_read": 0,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            "synthetic": False,
        }
        published = publish_exclusive(
            document, SUCCESS_RELATIVE, SUCCESS_RECEIPT_RELATIVE,
        )
        return {
            "schema": SCHEMA + "-published-reference-summary",
            "status": "PASS", "actual_independent_reference_count": 2,
            "case_count": BUFFER_CASE_COUNT,
            "matrix_sha256": MATRIX_SHA256,
            "reference_vector_sha256": digest(first),
            "publication": published,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }
    except (BufferExporterOracleError, OSError, subprocess.SubprocessError) as error:
        details = error.details if isinstance(
            error, (ActualReferenceWorkerFailure, ActualPublicationFailure),
        ) else {}
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
            "actual_failed_worker_or_publication": details,
            "frozen_prerequisites": provenance,
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
            "status": "FAIL", "actual_completed_reference_count": len(roles),
            "actual_failed_reference_role": details.get("role"),
            "actual_first_failed_case_id": (
                details.get("first_failed_case_id")
                or details.get("complete_worker_failure", {})
                .get("details", {}).get("first_failed_case_id")
            ),
            "publication": publication,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0, "file_writes": 0,
        "candidate_imports": 0, "production_imports": 0,
        "reference_workers": 0, "candidate_workers": 0, "native_workers": 0,
        "threads_started": 0, "clock_samples": 0,
        "regex_matching_calls": 0, "directory_inspections": 0,
        "locale_changes": 0, "buffer_exporter_constructions": 0,
        "buffer_case_executions": 0, "gc_collections": 0,
        "blocked_reads": 0, "blocked_writes": 0,
        "blocked_imports": 0, "blocked_workers": 0,
        "blocked_threads": 0, "blocked_clocks": 0,
        "blocked_regex_matching": 0, "blocked_directories": 0,
        "blocked_locale_changes": 0,
        "blocked_buffer_exporter_constructions": 0,
        "blocked_buffer_case_executions": 0, "blocked_gc_collections": 0,
    }
    installed: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    def deny(name: str, explanation: str) -> Callable[..., Any]:
        def blocked(*arguments: Any, **keywords: Any) -> Any:
            effects[name] += 1
            raise SourceOnlyBoundaryError(explanation)

        return blocked

    def blocked_open(*arguments: Any, **keywords: Any) -> Any:
        mode = keywords.get("mode", arguments[1] if len(arguments) > 1 else "r")
        writing = (
            bool(mode & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))
            if isinstance(mode, int)
            else any(marker in str(mode) for marker in ("w", "a", "x", "+"))
        )
        effects["blocked_writes" if writing else "blocked_reads"] += 1
        raise SourceOnlyBoundaryError("source controls cannot open actual evidence")

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (Path, "open"),
        ):
            install(owner, name, blocked_open)
        for name in ("read_bytes", "read_text"):
            install(Path, name, deny("blocked_reads", "actual reading is forbidden"))
        for name in ("write_bytes", "write_text", "touch", "mkdir", "unlink"):
            install(Path, name, deny("blocked_writes", "actual writing is forbidden"))
        for name in ("unlink", "remove", "rename", "replace", "write"):
            install(os, name, deny(
                "blocked_writes",
                "source controls cannot remove, replace, rename, or write files",
            ))
        for name in ("listdir", "scandir", "walk"):
            install(os, name, deny("blocked_directories", "directory scans are forbidden"))
        for name in ("iterdir", "glob", "rglob"):
            install(Path, name, deny("blocked_directories", "directory scans are forbidden"))
        install(importlib, "import_module", deny(
            "blocked_imports", "no actual candidate or reference may be imported",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "no actual production module may be imported",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny("blocked_workers", "no worker may start"))
        for name in ("fork", "posix_spawn", "posix_spawnp", "system"):
            install(os, name, deny("blocked_workers", "no process may start"))
        install(threading.Thread, "start", deny(
            "blocked_threads", "no actual background thread may start",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "process_time_ns", "thread_time", "thread_time_ns",
        ):
            install(time, name, deny("blocked_clocks", "clock sampling is forbidden"))
        install(locale, "setlocale", deny(
            "blocked_locale_changes", "locale changes are forbidden",
        ))
        install(PoisonOnReleaseExporter, "__init__", deny(
            "blocked_buffer_exporter_constructions",
            "source controls cannot create an actual PEP 688 exporter",
        ))
        install(sys.modules[__name__], "execute_case", deny(
            "blocked_buffer_case_executions",
            "source controls cannot execute a real PEP 688 case",
        ))
        install(gc, "collect", deny(
            "blocked_gc_collections", "source controls cannot collect real cycles",
        ))
        preloaded_regex = sys.modules.get("re")
        if preloaded_regex is not None:
            for name in (
                "compile", "search", "match", "fullmatch", "findall",
                "finditer", "split", "sub", "subn",
            ):
                install(preloaded_regex, name, deny(
                    "blocked_regex_matching", "real matching is forbidden",
                ))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    regex = sys.modules.get("re")
    previous_search = getattr(regex, "search", None) if regex else None
    previous_open = builtins.open
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and bool(condition) and name not in accepted,
                "a genuine V2 source-only positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected,
                "a real V2 poison control was duplicated: " + name)
        try:
            action()
        except (BufferExporterOracleError, OSError, ValueError, TypeError):
            rejected.append(name)
            return
        raise BufferExporterOracleError(
            "a genuine V2 adversarial control was accepted: " + name,
        )

    with source_only_boundary() as effects:
        matrix = build_matrix()
        accept("retain-all-264-exact-original-v1-buffer-cases",
               validate_matrix(matrix) == MATRIX_SHA256)
        accept("retain-four-exact-direct-and-memoryview-carriers", len(CARRIERS) == 4)
        accept("retain-19-exact-real-module-pattern-and-scanner-operations",
               len(OPERATIONS) == 19)
        for scenario, amount in (
            ("success", 76), ("no-match", 76), ("repeat", 76),
            ("callback-error", 20), ("retained", 16),
        ):
            accept("retain-exact-original-scenario-" + scenario,
                   sum(row["scenario"] == scenario for row in matrix) == amount)
        for operation in OPERATIONS:
            accept("retain-original-buffer-operation-" + operation,
                   any(row["operation"] == operation for row in matrix))
        for name, wrapped, readonly in CARRIERS:
            accept("retain-original-buffer-carrier-" + name,
                   all(row["wrapped"] is wrapped and row["readonly"] is readonly
                       for row in matrix if row["carrier"] == name))
        accept("retain-165-original-152-public-and-13-exact-private-methods",
               ORIGINAL_METHOD_COUNT == PUBLIC_METHOD_COUNT + PRIVATE_WAIVER_COUNT
               and len(PRIVATE_METHOD_NAMES) == PRIVATE_WAIVER_COUNT
               and len(set(PRIVATE_METHOD_NAMES)) == PRIVATE_WAIVER_COUNT)
        accept("retain-unchanged-1376-public-cases-and-43-cohorts",
               PUBLIC_CASE_COUNT == 1_376 and PUBLIC_COHORT_COUNT == 43)
        accept("preserve-complete-genuine-v1-failure-and-separate-receipt-pins",
               valid_sha256(V1_FAILURE_SHA256) and valid_sha256(V1_RECEIPT_SHA256)
               and valid_sha256(V1_STDERR_SHA256) and V1_STDERR_BYTES == 1_657)
        accept("retain-root-pinned-v1-source-and-protocol",
               valid_sha256(V1_SOURCE_SHA256) and valid_sha256(V1_PROTOCOL_SHA256))
        accept("retain-root-pinned-v2-protocol-and-matrix",
               valid_sha256(PROTOCOL_SHA256) and valid_sha256(MATRIX_SHA256))
        fake_pins = {
            "source": "12" * 32, "protocol": PROTOCOL_SHA256,
            "v1_source": V1_SOURCE_SHA256, "v1_protocol": V1_PROTOCOL_SHA256,
            "v1_failure": V1_FAILURE_SHA256, "v1_receipt": V1_RECEIPT_SHA256,
            "v6_reference": V6_REFERENCE_SHA256,
            "stage27_source": V27_SOURCE_SHA256,
            "stage27_protocol": V27_PROTOCOL_SHA256,
            "public_reference": PUBLIC_REFERENCE_SHA256,
        }
        accept("accept-only-in-memory-exact-complete-v2-pins",
               validate_pins(fake_pins) == fake_pins)
        for key in tuple(fake_pins):
            missing = dict(fake_pins)
            missing.pop(key)
            reject("reject-missing-immutable-v2-prerequisite-" + key,
                   lambda missing=missing: validate_pins(missing))
            if key != "source":
                wrong = dict(fake_pins)
                wrong[key] = "34" * 32
                reject("reject-substituted-immutable-v2-prerequisite-" + key,
                       lambda wrong=wrong: validate_pins(wrong))

        for index in range(44):
            omitted = copy.deepcopy(matrix)
            omitted.pop(index)
            reject("reject-missing-genuine-original-case-" + format(index, "03d"),
                   lambda omitted=omitted: validate_matrix(omitted))
            replaced = copy.deepcopy(matrix)
            replaced[index]["operation"] = "candidates.foreign.match"
            reject("reject-substituted-genuine-operation-" + format(index, "03d"),
                   lambda replaced=replaced: validate_matrix(replaced))
            wrong_carrier = copy.deepcopy(matrix)
            wrong_carrier[index]["wrapped"] = not wrong_carrier[index]["wrapped"]
            reject("reject-substituted-genuine-carrier-" + format(index, "03d"),
                   lambda wrong_carrier=wrong_carrier: validate_matrix(wrong_carrier))
        swapped = copy.deepcopy(matrix)
        swapped[0], swapped[1] = swapped[1], swapped[0]
        reject("reject-reordered-authentic-original-case-matrix",
               lambda: validate_matrix(swapped))
        duplicate = copy.deepcopy(matrix)
        duplicate[-1] = copy.deepcopy(duplicate[0])
        reject("reject-duplicated-authentic-original-case-matrix",
               lambda: validate_matrix(duplicate))

        row = matrix[0]
        real_events = [
            ["call-start", row["operation"]],
            ["acquire", 1, 0, False, "616161"],
            ["release", 1, "616161", "212121"],
            ["result-live", row["operation"]],
            ["result-materialized", row["operation"]],
            ["result-dropped", row["operation"]],
            ["call-return", row["operation"]],
            ["cleanup-start"], ["cleanup-complete"],
            ["case-finish", "212121"],
        ]
        positive = {
            **row, "results": [{"status": "return", "value": None}],
            "events": real_events, "lifetime": {},
            "buffer": {
                "initial_hex": "616161", "final_hex": "212121",
                "byte_length": 3, "acquisitions": 1, "releases": 1,
            },
        }
        validate_case_record(positive, row)
        accept("accept-only-explicitly-synthetic-phase-exact-memory-control", True)

        retained_row = matrix[248]
        accept("retain-genuine-first-cyclic-exporter-matrix-row",
               retained_row["scenario"] == "retained"
               and retained_row["wrapped"] is False
               and retained_row["readonly"] is False)
        retained_events = [
            ["retained-create", retained_row["operation"]],
            ["acquire", 1, 0, False, "616161"],
            ["retained-gc-while-live", True, True],
            ["holder-result-live", retained_row["operation"]],
            ["holder-result-materialized", retained_row["operation"]],
            ["holder-result-dropped", retained_row["operation"]],
            ["cleanup-start"],
            ["release", 1, "616161", "212121"],
            ["retained-gc-after-drop", False, False],
            ["cleanup-complete"],
            ["case-finish", "212121"],
        ]
        retained_positive = {
            **retained_row,
            "results": [{"status": "return", "value": None}],
            "events": retained_events,
            "buffer": {
                "initial_hex": "616161", "final_hex": "212121",
                "byte_length": 3, "acquisitions": 1, "releases": 1,
            },
            "lifetime": {
                "holder_created": True,
                "owner_alive_while_holder_live": True,
                "carrier_supports_weakref": True,
                "carrier_alive_while_holder_live": True,
                "owner_alive_after_cyclic_gc": False,
                "carrier_alive_after_cyclic_gc": False,
            },
        }
        validate_case_record(retained_positive, retained_row)
        accept("validate-only-synthetic-genuine-live-and-collected-weakrefs", True)
        for key, forged_value in (
            ("holder_created", False),
            ("owner_alive_while_holder_live", False),
            ("owner_alive_after_cyclic_gc", True),
            ("carrier_supports_weakref", False),
            ("carrier_alive_while_holder_live", False),
            ("carrier_alive_after_cyclic_gc", True),
        ):
            forged_retention = copy.deepcopy(retained_positive)
            forged_retention["lifetime"][key] = forged_value
            reject("reject-forged-actual-retained-weakref-" + key,
                   lambda forged_retention=forged_retention: (
                       validate_case_record(forged_retention, retained_row)
                   ))
        for event_index, value_index in ((2, 1), (2, 2), (8, 1), (8, 2)):
            forged_event = copy.deepcopy(retained_positive)
            forged_event["events"][event_index][value_index] = (
                not forged_event["events"][event_index][value_index]
            )
            reject("reject-forged-live-gc-event-"
                   + str(event_index) + "-" + str(value_index),
                   lambda forged_event=forged_event: validate_case_record(
                       forged_event, retained_row,
                   ))

        fake_payload = b"abc"
        fake_journal: list[dict[str, Any]] = []

        def genuine_synthetic_write(descriptor: int, payload: bytes) -> int:
            require(fake_journal[-1]["status"] == "PENDING"
                    and fake_journal[-1]["descriptor"] == descriptor
                    and fake_journal[-1]["requested_bytes"] == len(payload)
                    and fake_journal[-1]["requested_sha256"]
                    == hashlib.sha256(payload).hexdigest(),
                    "the actual synthetic pending journal was not appended first")
            return len(payload)

        written = _record_syscall(
            fake_journal, "write-synthetic-pending-proof", "synthetic-only",
            genuine_synthetic_write, 17, fake_payload,
            expected_kind="write",
        )
        accept("record-exactly-one-real-pending-then-successful-fake-write",
               written == len(fake_payload) and len(fake_journal) == 1
               and fake_journal[0]["status"] == "PASS"
               and fake_journal[0]["pending_recorded_before_syscall"] is True
               and fake_journal[0]["descriptor"] == 17
               and fake_journal[0]["returned_bytes"] == len(fake_payload))
        reused = _record_syscall(
            fake_journal, "write-synthetic-legally-reused-descriptor",
            "synthetic-only", lambda descriptor, payload: len(payload),
            17, fake_payload, expected_kind="write",
        )
        accept("permit-genuine-descriptor-number-reuse-with-new-journal-event",
               reused == len(fake_payload) and len(fake_journal) == 2
               and fake_journal[0]["descriptor"]
               == fake_journal[1]["descriptor"] == 17
               and fake_journal[1]["status"] == "PASS")
        for label, returned in (
            ("zero", 0), ("short", 1), ("boolean", True),
            ("negative", -1), ("oversized", len(fake_payload) + 1),
        ):
            forged_journal: list[dict[str, Any]] = []
            reject("reject-injected-actual-" + label + "-write",
                   lambda returned=returned, forged_journal=forged_journal: (
                       _record_syscall(
                           forged_journal, "write-injected-" + label,
                           "synthetic-only",
                           lambda descriptor, payload: returned,
                           17, fake_payload, expected_kind="write",
                       )
                   ))
            accept("preserve-single-failed-real-pending-" + label + "-write",
                   len(forged_journal) == 1
                   and forged_journal[0]["status"] == "FAIL"
                   and forged_journal[0]["pending_recorded_before_syscall"] is True
                   and forged_journal[0]["descriptor"] == 17)
        for label, returned in (
            ("zero", b""), ("short", b"a"),
            ("oversized", b"abcd"), ("boolean", True),
        ):
            forged_journal = []
            reject("reject-injected-actual-" + label + "-read",
                   lambda returned=returned, forged_journal=forged_journal: (
                       _record_syscall(
                           forged_journal, "read-injected-" + label,
                           "synthetic-only",
                           lambda descriptor, requested: returned,
                           17, 3, expected_kind="read",
                       )
                   ))
            accept("preserve-single-failed-real-pending-" + label + "-read",
                   len(forged_journal) == 1
                   and forged_journal[0]["status"] == "FAIL"
                   and forged_journal[0]["descriptor"] == 17)
        fake_info = os.stat_result((stat.S_IFREG | 0o600, 73, 42, 1, 0, 0,
                                    3, 0, 0, 0))
        alien_info = os.stat_result((stat.S_IFREG | 0o600, 74, 42, 1, 0, 0,
                                     3, 0, 0, 0))
        fake_side_effects = {"unlink": 0, "fsync": 0}

        def fake_unlink(name: str, *, dir_fd: int) -> None:
            require(dir_fd == 17 and name == safe_relative(
                SUCCESS_RELATIVE, output=True,
            ).name, "a synthetic unlink targeted an unowned basename")
            fake_side_effects["unlink"] += 1

        def fake_fsync(descriptor: int) -> None:
            require(descriptor == 17, "a synthetic parent descriptor was forged")
            fake_side_effects["fsync"] += 1

        simulated_cleanup_ledger: list[dict[str, Any]] = []
        successful_cleanup = cleanup_created_partial(
            relative=SUCCESS_RELATIVE, directory=17,
            basename=safe_relative(SUCCESS_RELATIVE, output=True).name,
            writer=18, original_info=fake_info,
            ledger=simulated_cleanup_ledger,
            operations={
                "fstat": lambda descriptor: fake_info,
                "stat": lambda name, **keywords: fake_info,
                "unlink": fake_unlink, "fsync": fake_fsync,
            },
        )
        accept("prove-in-memory-inode-owned-partial-unlink-and-parent-sync",
               successful_cleanup["inode_proven"] is True
               and successful_cleanup["removed_only_created_inode"] is True
               and successful_cleanup["directory_fsync_completed"] is True
               and successful_cleanup["errors"] == []
               and fake_side_effects == {"unlink": 1, "fsync": 1}
               and all(event["status"] == "PASS"
                       and event["pending_recorded_before_syscall"] is True
                       for event in simulated_cleanup_ledger))
        foreign_side_effects = {"unlink": 0, "fsync": 0}

        def never_unlink(name: str, *, dir_fd: int) -> None:
            foreign_side_effects["unlink"] += 1

        def sync_foreign(descriptor: int) -> None:
            foreign_side_effects["fsync"] += 1

        foreign_cleanup = cleanup_created_partial(
            relative=SUCCESS_RELATIVE, directory=17,
            basename=safe_relative(SUCCESS_RELATIVE, output=True).name,
            writer=18, original_info=fake_info, ledger=[],
            operations={
                "fstat": lambda descriptor: fake_info,
                "stat": lambda name, **keywords: alien_info,
                "unlink": never_unlink, "fsync": sync_foreign,
            },
        )
        accept("refuse-in-memory-partial-removal-of-foreign-report-inode",
               foreign_cleanup["inode_proven"] is False
               and foreign_cleanup["removed_only_created_inode"] is False
               and foreign_cleanup["directory_fsync_completed"] is True
               and len(foreign_cleanup["errors"]) == 1
               and foreign_side_effects == {"unlink": 0, "fsync": 1})

        def failed_unlink(name: str, *, dir_fd: int) -> None:
            raise OSError(5, "synthetic-only inode-proven unlink failure")

        def failed_fsync(descriptor: int) -> None:
            raise OSError(5, "synthetic-only post-cleanup directory sync failure")

        multi_failure_journal: list[dict[str, Any]] = []
        multiple_cleanup = cleanup_created_partial(
            relative=SUCCESS_RELATIVE, directory=17,
            basename=safe_relative(SUCCESS_RELATIVE, output=True).name,
            writer=18, original_info=fake_info,
            ledger=multi_failure_journal,
            operations={
                "fstat": lambda descriptor: fake_info,
                "stat": lambda name, **keywords: fake_info,
                "unlink": failed_unlink, "fsync": failed_fsync,
            },
        )
        accept("preserve-first-and-all-real-injected-partial-cleanup-failures",
               multiple_cleanup["inode_proven"] is True
               and multiple_cleanup["removed_only_created_inode"] is False
               and multiple_cleanup["directory_fsync_completed"] is False
               and len(multiple_cleanup["errors"]) == 2
               and multiple_cleanup["errors"][0]["operation"]
               == "remove-owned-partial"
               and multiple_cleanup["errors"][1]["operation"]
               == "fsync-after-partial-cleanup"
               and sum(event["status"] == "FAIL"
                       for event in multi_failure_journal) == 2
               and all(event["pending_recorded_before_syscall"] is True
                       for event in multi_failure_journal))

        fake_close_journal: list[dict[str, Any]] = []
        closed_descriptors: list[int] = []

        def synthetic_close(descriptor: int) -> None:
            closed_descriptors.append(descriptor)

        no_close_errors = _close_owned_descriptors(
            fake_close_journal,
            [(17, "first-synthetic-descriptor"),
             (17, "legally-reused-synthetic-descriptor")],
            closer=synthetic_close,
        )
        accept("preserve-legal-reused-descriptor-close-provenance",
               no_close_errors == [] and closed_descriptors == [17, 17]
               and len(fake_close_journal) == 2
               and all(event["descriptor"] == 17
                       and event["status"] == "PASS"
                       and event["pending_recorded_before_syscall"] is True
                       for event in fake_close_journal))

        def failing_close(descriptor: int) -> None:
            raise OSError(5, "synthetic-only owned-descriptor close failure")

        failed_close_journal: list[dict[str, Any]] = []
        all_close_errors = _close_owned_descriptors(
            failed_close_journal,
            [(17, "first-failed-synthetic-descriptor"),
             (18, "second-failed-synthetic-descriptor")],
            closer=failing_close,
        )
        accept("preserve-first-and-all-genuine-injected-close-failures",
               len(all_close_errors) == 2
               and all_close_errors[0]["target"]
               == "second-failed-synthetic-descriptor"
               and all_close_errors[1]["target"]
               == "first-failed-synthetic-descriptor"
               and len(failed_close_journal) == 2
               and all(event["status"] == "FAIL"
                       and event["pending_recorded_before_syscall"] is True
                       for event in failed_close_journal))
        accept("remove-only-a-genuinely-created-incomplete-report",
               should_remove_created_partial(
                   failed=True, created=True, publication_complete=False,
               ) is True)
        accept("never-delete-verified-durable-report-after-close-failure",
               should_remove_created_partial(
                   failed=True, created=True, publication_complete=True,
               ) is False
               and len(all_close_errors) == 2
               and all(event["status"] == "FAIL"
                       for event in failed_close_journal))
        accept("never-delete-uncreated-failed-report-path",
               should_remove_created_partial(
                   failed=True, created=False, publication_complete=False,
               ) is False)
        reject("reject-impossible-durable-report-without-exclusive-creation",
               lambda: should_remove_created_partial(
                   failed=True, created=False, publication_complete=True,
               ))
        reject("reject-forged-nonboolean-durable-publication-phase",
               lambda: should_remove_created_partial(
                   failed=True, created=True, publication_complete=1,
               ))
        accept("accept-only-current-exact-source-only-failed-case-identity",
               validate_current_failed_case_identity(positive, row) == positive)
        accept("accept-only-source-ordered-complete-original-case-prefix",
               validate_completed_case_prefix([positive], matrix, 1) == [positive])
        reject("reject-missing-current-failure-record",
               lambda: validate_current_failed_case_identity(None, row))
        reject("reject-stale-previous-success-as-new-failed-case",
               lambda: validate_current_failed_case_identity(positive, matrix[1]))
        for key in ("case", "scenario", "operation", "carrier", "wrapped", "readonly"):
            stale = copy.deepcopy(positive)
            stale[key] = (
                not stale[key] if type(stale[key]) is bool
                else "substituted-previous-case"
            )
            reject("reject-forged-failed-case-identity-" + key,
                   lambda stale=stale: validate_current_failed_case_identity(
                       stale, row,
                   ))
        reject("reject-invented-completed-prefix-count",
               lambda: validate_completed_case_prefix([positive], matrix, 0))
        reject("reject-omitted-completed-first-case",
               lambda: validate_completed_case_prefix([], matrix, 1))
        reject("reject-duplicated-completed-original-case",
               lambda: validate_completed_case_prefix(
                   [positive, copy.deepcopy(positive)], matrix, 2,
               ))
        actual_failed_case = matrix[1]
        synthetic_child_failure = {
            "schema": SCHEMA + "-actual-reference-worker-failure",
            "status": "FAIL", "python": "3.14.6", "role": "reference_a",
            "source_sha256": fake_pins["source"],
            "protocol_sha256": PROTOCOL_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "error_type": "ActualReferenceWorkerFailure",
            "error_message": "synthetic in-memory failed-child poison control",
            "details": {
                "role": "reference_a",
                "first_failed_case_index": 1,
                "first_failed_case_id": actual_failed_case["case"],
                "first_failed_case": dict(actual_failed_case),
                "completed_count": 1,
                "completed_records": [copy.deepcopy(positive)],
                "exception_module": "builtins",
                "exception_type": "RuntimeError",
                "exception_message": "synthetic source-only exception",
                "matrix_sha256": MATRIX_SHA256,
            },
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            "synthetic": False,
        }
        accept("validate-only-synthetic-in-memory-first-failed-child-contract",
               validate_child_worker_failure(
                   synthetic_child_failure, role="reference_a", pins=fake_pins,
               ) == synthetic_child_failure)
        for key in ("schema", "status", "role", "source_sha256",
                    "protocol_sha256", "matrix_sha256", "error_type"):
            forged_child = copy.deepcopy(synthetic_child_failure)
            forged_child[key] = "FORGED"
            reject("reject-forged-complete-failed-child-" + key,
                   lambda forged_child=forged_child: validate_child_worker_failure(
                       forged_child, role="reference_a", pins=fake_pins,
                   ))
        for key in ("first_failed_case_index", "first_failed_case_id",
                    "first_failed_case", "completed_count", "completed_records",
                    "exception_module", "exception_type", "exception_message",
                    "matrix_sha256"):
            forged_child = copy.deepcopy(synthetic_child_failure)
            forged_child["details"].pop(key)
            reject("reject-omitted-real-failed-child-detail-" + key,
                   lambda forged_child=forged_child: validate_child_worker_failure(
                       forged_child, role="reference_a", pins=fake_pins,
                   ))
        previous_child = copy.deepcopy(synthetic_child_failure)
        previous_child["details"]["actual_failed_case_record"] = (
            copy.deepcopy(positive)
        )
        reject("reject-stale-prior-success-as-actual-failed-child",
               lambda: validate_child_worker_failure(
                   previous_child, role="reference_a", pins=fake_pins,
               ))
        for index in range(len(real_events)):
            lost = copy.deepcopy(positive)
            lost["events"].pop(index)
            reject("reject-missing-genuine-cleanup-phase-" + format(index, "02d"),
                   lambda lost=lost: validate_case_record(lost, row))
        for index in (0, 1, 3, 4, 5, 6, 7, 8):
            reordered = copy.deepcopy(positive)
            reordered["events"][index], reordered["events"][index + 1] = (
                reordered["events"][index + 1], reordered["events"][index],
            )
            reject("reject-reordered-genuine-lifetime-phase-" + format(index, "02d"),
                   lambda reordered=reordered: validate_case_record(reordered, row))
        for key in ("initial_hex", "final_hex", "byte_length", "acquisitions", "releases"):
            forged = copy.deepcopy(positive)
            forged["buffer"].pop(key)
            reject("reject-missing-genuine-buffer-observation-" + key,
                   lambda forged=forged: validate_case_record(forged, row))
        fake_zero = copy.deepcopy(positive)
        fake_zero["events"] = [
            ["call-start", row["operation"]],
            ["result-live", row["operation"]],
            ["result-materialized", row["operation"]],
            ["result-dropped", row["operation"]],
            ["call-return", row["operation"]],
            ["cleanup-start"], ["cleanup-complete"],
            ["case-finish", "616161"],
        ]
        fake_zero["buffer"] = {
            "initial_hex": "616161", "final_hex": "616161",
            "byte_length": 3, "acquisitions": 0, "releases": 0,
        }
        reject("reject-fake-success-with-no-real-buffer-acquisition",
               lambda: validate_case_record(fake_zero, row))
        for relative in (
            "/tmp/false-buffer-v2.json", "../false-buffer-v2.json",
            "oracle/cpython-3.14.6/evidence/unapproved-buffer-v2.json",
            V1_FAILURE_RELATIVE, V1_RECEIPT_RELATIVE,
        ):
            reject("reject-historical-or-escaping-buffer-output-" + relative,
                   lambda relative=relative: safe_relative(relative, output=True))
        for name in (
            "candidates.rust_candidate", "candidates.vm_candidate",
            "candidates.zig_candidate",
            "tools.python_re_buffer_exporter_oracle_v1",
            "tools.postfinal_cpython_locale_oracle_v6",
            "tools.python_re_public_surface_oracle_stage27",
        ):
            reject("block-actual-source-only-production-import-" + name,
                   lambda name=name: importlib.import_module(name))
        reject("block-actual-source-only-builtin-import",
               lambda: builtins.__import__("candidates.rust_candidate"))
        reject("block-actual-source-only-first-failure-read",
               lambda: builtins.open(V1_FAILURE_RELATIVE, "rb"))
        reject("block-actual-source-only-receipt-read",
               lambda: io.open(V1_RECEIPT_RELATIVE, "rb"))
        reject("block-actual-source-only-raw-reference-read",
               lambda: os.open(V1_FAILURE_RELATIVE, os.O_RDONLY))
        reject("block-actual-source-only-path-reference-read",
               lambda: (ROOT / V1_RECEIPT_RELATIVE).read_bytes())
        reject("block-actual-source-only-v2-evidence-write",
               lambda: builtins.open(SUCCESS_RELATIVE, "wb"))
        reject("block-actual-source-only-raw-evidence-write",
               lambda: os.write(1, b"forbidden-source-only-write"))
        reject("block-actual-source-only-descriptor-relative-evidence-unlink",
               lambda: os.unlink(SUCCESS_RELATIVE))
        reject("block-actual-source-only-evidence-remove",
               lambda: os.remove(SUCCESS_RELATIVE))
        reject("block-actual-source-only-evidence-rename",
               lambda: os.rename(SUCCESS_RELATIVE, FAILURE_RELATIVE))
        reject("block-actual-source-only-evidence-replacement",
               lambda: os.replace(SUCCESS_RELATIVE, FAILURE_RELATIVE))
        reject("block-actual-source-only-directory-inspection",
               lambda: os.listdir(str(ROOT / "oracle")))
        reject("block-actual-source-only-reference-process",
               lambda: subprocess.Popen([str(PINNED_PYTHON)]))
        reject("block-actual-source-only-reference-run",
               lambda: subprocess.run([str(PINNED_PYTHON)]))
        reject("block-actual-source-only-background-thread",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-actual-source-only-wall-clock", lambda: time.time())
        reject("block-actual-source-only-performance-clock",
               lambda: time.perf_counter())
        reject("block-actual-source-only-locale-mutation",
               lambda: locale.setlocale(locale.LC_CTYPE))
        reject("block-actual-source-only-buffer-exporter-construction",
               lambda: PoisonOnReleaseExporter(b"aaa", False))
        reject("block-actual-source-only-genuine-buffer-case",
               lambda: execute_case(row, None))
        reject("block-actual-source-only-cyclic-collection", lambda: gc.collect())
        if regex is not None:
            reject("block-actual-source-only-stdlib-matching",
                   lambda: regex.search("a", "a"))
        accept("load-no-candidate-or-reference-controller",
               not any(name == "candidates" or name.startswith("candidates.")
                       or name == "tools.python_re_buffer_exporter_oracle_v1"
                       or name == "tools.postfinal_cpython_locale_oracle_v6"
                       or name == "tools.python_re_public_surface_oracle_stage27"
                       for name in sys.modules))
        actual_effect_keys = (
            "file_reads", "file_writes", "candidate_imports",
            "production_imports", "reference_workers", "candidate_workers",
            "native_workers", "threads_started", "clock_samples",
            "regex_matching_calls", "directory_inspections", "locale_changes",
            "buffer_exporter_constructions", "buffer_case_executions",
            "gc_collections",
        )
        accept("prove-zero-actual-source-only-effects",
               all(effects[name] == 0 for name in actual_effect_keys))
        accept("require-at-least-150-distinct-real-adversarial-rejections",
               len(rejected) >= 150)
    accept("restore-exact-original-filesystem-opener",
           builtins.open is previous_open)
    accept("restore-exact-preloaded-stdlib-regex-function",
           regex is None or getattr(regex, "search", None) is previous_search)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "protocol_sha256": PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "buffer_case_count": BUFFER_CASE_COUNT,
        "carrier_count": len(CARRIERS), "operation_count": len(OPERATIONS),
        "original_method_count": ORIGINAL_METHOD_COUNT,
        "original_public_method_count": PUBLIC_METHOD_COUNT,
        "original_private_method_count": PRIVATE_WAIVER_COUNT,
        "original_private_methods_status": "WAIVED; NOT RUN; NOT QUALIFIED",
        "unchanged_public_case_count": PUBLIC_CASE_COUNT,
        "unchanged_public_cohort_count": PUBLIC_COHORT_COUNT,
        "preserved_v1_failure_sha256": V1_FAILURE_SHA256,
        "preserved_v1_receipt_sha256": V1_RECEIPT_SHA256,
        "preserved_v1_failure_status": "FAIL; NOT QUALIFIED",
        "preserved_v1_failed_case_identity": "NOT CAPTURED",
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted, "rejected_controls": rejected,
        "effects": effects,
        "preloaded_stdlib_regex_present": regex is not None,
        "actual_reference_workers": 0, "actual_candidate_workers": 0,
        "actual_buffer_case_executions": 0,
        "reference_qualified": False, "candidate_qualified": False,
        "synthetic": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Authenticate genuine phase-exact original regex exporter lifetimes",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--worker-role", choices=REFERENCE_LABELS)
    for name in (
        "source", "protocol", "v1-source", "v1-protocol",
        "v1-failure", "v1-receipt", "v6-reference",
        "stage27-source", "stage27-protocol", "public-reference",
    ):
        parser.add_argument("--" + name + "-sha256")
    return parser.parse_args(arguments)


def options_to_pins(options: argparse.Namespace) -> dict[str, str]:
    return validate_pins({
        "source": options.source_sha256,
        "protocol": options.protocol_sha256,
        "v1_source": options.v1_source_sha256,
        "v1_protocol": options.v1_protocol_sha256,
        "v1_failure": options.v1_failure_sha256,
        "v1_receipt": options.v1_receipt_sha256,
        "v6_reference": options.v6_reference_sha256,
        "stage27_source": options.stage27_source_sha256,
        "stage27_protocol": options.stage27_protocol_sha256,
        "public_reference": options.public_reference_sha256,
    })


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "source_sha256", "protocol_sha256", "v1_source_sha256",
            "v1_protocol_sha256", "v1_failure_sha256", "v1_receipt_sha256",
            "v6_reference_sha256", "stage27_source_sha256",
            "stage27_protocol_sha256", "public_reference_sha256",
        )), "source-only tests cannot consume any genuine production pins")
        observed = source_self_test()
    elif options.self_oracle:
        observed = run_self_oracle(options_to_pins(options))
    else:
        try:
            observed = run_reference_worker(
                options.worker_role, options_to_pins(options),
            )
        except ActualReferenceWorkerFailure as error:
            observed = {
                "schema": SCHEMA + "-actual-reference-worker-failure",
                "status": "FAIL", "python": "3.14.6",
                "role": options.worker_role,
                "source_sha256": options.source_sha256,
                "protocol_sha256": PROTOCOL_SHA256,
                "matrix_sha256": MATRIX_SHA256,
                "error_type": type(error).__qualname__,
                "error_message": str(error),
                "details": error.details,
                "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
                "synthetic": False,
            }
    sys.stdout.buffer.write(canonical(observed))
    sys.stdout.buffer.flush()
    return 0 if observed.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
