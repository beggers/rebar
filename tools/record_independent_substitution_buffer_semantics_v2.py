#!/usr/bin/env python3
"""Durably record all 5,120 frozen substitution and buffer checks.

Source-only controls never inspect files, execute an engine, start a worker,
sample a clock, or publish evidence. A separately recorded baseline runs
exactly two genuinely isolated, source-pinned CPython reference workers. A
candidate runs only under the frozen from-scratch ownership audit and the
continuous native matcher and warning guards.

Every return value, exception, callback, nested buffer acquisition and
release, warning, worker stream, mismatch, and failure is preserved in
deterministic lossless evidence. Publication and correctness have separate
statuses.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
from dataclasses import dataclass
import gc
import gzip
import hashlib
import importlib
import importlib.machinery
import io
import json
import os
import random
import stat
import subprocess
import sys
import threading
import time
import types
import warnings
from collections.abc import Callable, Iterator, Mapping
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/record_independent_substitution_buffer_semantics_v2.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-substitution-buffer-semantics-recorder-v2"
ORACLE_RELATIVE = "tools/independent_substitution_buffer_semantics_v1.py"
ORACLE_MODULE = "tools.independent_substitution_buffer_semantics_v1"
ORACLE_SCHEMA = "rebar-independent-substitution-buffer-semantics-v1"
ORACLE_SHA256 = (
    "a325528aa62f107969b9dfdf5dea2ae8f9426607887a317fe20fcf9a1b7fd445"
)
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_MODULE = "tools.independent_original_cpython_suite_v5"
V5_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
AUDIT_MODULE = "tools.independent_from_scratch_audit_v3"
AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
PREVIOUS_RECORDER_RELATIVE = (
    "tools/record_independent_substitution_buffer_semantics_v1.py"
)
PREVIOUS_RECORDER_SHA256 = (
    "1dbb45e8950a0eceb966a56adcbe2f9d1da35ec04883458a780b6f08f5a4735d"
)
PRESERVED_PREVIOUS_FAILURE_RELATIVE = (
    "experiments/rust_public_practice_v1/"
    "substitution-buffer-semantics-v1-shared-suite-v1-"
    "controller-failure-v1.json"
)
PRESERVED_PREVIOUS_FAILURE_SHA256 = (
    "a80316f3d1fe87808c8f16cb651393d275132d408633303da16a5142f55ba807"
)
MATRIX_SHA256 = (
    "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54"
)
PUBLISHED_SEED = 0x5355_4253_4255_4631
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
TRUSTED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
VARIANTS_PER_COHORT = 80
COHORTS = (
    "text-literal",
    "text-escaped",
    "text-callback",
    "text-callback-error",
    "text-named-captures",
    "text-numeric-captures",
    "text-missing-capture",
    "text-invalid-escape",
    "text-zero-width-lookahead",
    "text-zero-width-empty",
    "text-count-limit",
    "text-window-pos-endpos",
    "text-lone-surrogate",
    "text-combining-mark",
    "text-precomposed-unicode",
    "text-cross-domain-bytes-template",
    "bytes-literal",
    "bytes-escaped",
    "bytes-callback",
    "bytes-callback-error",
    "bytes-named-captures",
    "bytes-numeric-captures",
    "bytes-missing-capture",
    "bytes-invalid-escape",
    "bytes-zero-width-lookahead",
    "bytes-zero-width-empty",
    "bytes-count-limit",
    "bytes-window-pos-endpos",
    "bytearray-subject-literal",
    "bytearray-subject-escaped",
    "bytearray-replacement-literal",
    "bytearray-replacement-escaped",
    "readonly-subject-memoryview",
    "writable-subject-memoryview",
    "readonly-strided-subject-memoryview",
    "writable-strided-subject-memoryview",
    "released-readonly-subject-memoryview",
    "released-writable-subject-memoryview",
    "readonly-template-memoryview",
    "writable-template-memoryview",
    "readonly-strided-template-memoryview",
    "writable-strided-template-memoryview",
    "released-readonly-template-memoryview",
    "released-writable-template-memoryview",
    "pep688-stable-subject",
    "pep688-mutating-subject",
    "pep688-failing-subject",
    "pep688-fixed-hash-subject",
    "pep688-unhashable-subject",
    "pep688-stable-template",
    "pep688-mutating-template",
    "pep688-failing-template",
    "pep688-fixed-hash-template",
    "pep688-unhashable-template",
    "pep688-failing-hash-template",
    "pep688-wrapped-readonly-subject",
    "pep688-wrapped-writable-subject",
    "nested-stable-subject-and-template",
    "nested-mutating-subject-and-template",
    "nested-stable-fixed-hash-template",
    "nested-mutating-unhashable-template",
    "nested-failing-template-after-subject",
    "match-expand-buffer-retention",
    "callback-capture-and-buffer-order",
)
CASE_COUNT = len(COHORTS) * VARIANTS_PER_COHORT
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_ARCHIVE_BYTES = 384 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 320 * 1024 * 1024
MAX_COMPACT_REPORT_METADATA_BYTES = 32 * 1024 * 1024
MAX_ENCODED_PROCESS_STREAM_BYTES = ((MAX_PROCESS_BYTES + 2) // 3) * 4
MAX_COMPACT_REPORT_BYTES = (
    2 * MAX_ENCODED_PROCESS_STREAM_BYTES
    + MAX_COMPACT_REPORT_METADATA_BYTES
)
PROCESS_TIMEOUT_SECONDS = 900
SIMPLE_BUFFER_FLAG = 0
FULL_READONLY_BUFFER_FLAG = 284
APIS = (
    "module.sub", "module.subn", "pattern.sub", "pattern.subn", "match.expand",
)
FLAGS = (0, 2, 256, 258)
COUNTS = (0, 1, 2, 7)
WINDOW_STARTS = (-4, -1, 0, 1, 2, 5, 99, 2_147_483_647)
WINDOW_ENDS = (0, 1, 3, 8, 16, 64, None, 2_147_483_647)
SUBJECT_KINDS = frozenset({
    "str", "bytes", "bytearray", "readonly-memoryview",
    "writable-memoryview", "readonly-strided-memoryview",
    "writable-strided-memoryview", "released-readonly-memoryview",
    "released-writable-memoryview", "pep688-stable", "pep688-mutating",
    "pep688-failing", "pep688-fixed-hash", "pep688-unhashable",
    "pep688-wrapped-readonly", "pep688-wrapped-writable",
})
REPLACEMENT_KINDS = frozenset({
    "str", "bytes", "bytearray", "readonly-memoryview",
    "writable-memoryview", "readonly-strided-memoryview",
    "writable-strided-memoryview", "released-readonly-memoryview",
    "released-writable-memoryview", "pep688-stable", "pep688-mutating",
    "pep688-failing", "pep688-fixed-hash", "pep688-unhashable",
    "pep688-failing-hash", "callable",
})
REPLACEMENT_STYLES = frozenset({
    "literal", "escaped-named", "escaped-numeric", "missing-capture",
    "invalid-escape", "callable", "callable-error",
})
BUFFER_BEHAVIORS = frozenset({"none", "stable", "mutate", "fail"})
HASH_BEHAVIORS = frozenset({"none", "fixed", "unhashable", "fail"})

GUARD_TRUE_FIELDS = (
    "original_matchers_blocked", "adapter_import_quarantined",
    "native_sre_blocked", "builtins_import_guarded",
    "importlib_import_guarded", "actual_object_identity_guarded",
    "warning_registry_introspection_safe",
    "warning_registry_exactly_absent", "cross_family_imports_blocked",
    "external_regex_imports_blocked",
)
GUARD_COUNTER_FIELDS = (
    "cached_original_matcher_descendant_count",
    "cached_original_holder_count",
    "owned_ctypes_load_count", "owned_ctypes_symbol_count",
)


class RecorderError(Exception):
    """A complete frozen observation, owner, or publication was changed."""


class SourceOnlyError(RecorderError):
    """A synthetic-only control attempted a genuine external effect."""


class ObservationFailure(RecorderError):
    """Retain truthful evidence after a real worker has already started."""

    def __init__(
        self,
        message: str,
        *,
        mode: str,
        process: Mapping[str, Any],
        report: Mapping[str, Any] | None,
        report_publication: Mapping[str, Any] | None = None,
        receipt_publication: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.mode = mode
        self.process = dict(process)
        self.report = dict(report) if report is not None else None
        self.report_publication = (
            dict(report_publication)
            if report_publication is not None else None
        )
        self.receipt_publication = (
            dict(receipt_publication)
            if receipt_publication is not None else None
        )


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    adapter_module: str
    adapter_relative: str
    engine_relative: str
    bridge_module: str
    bridge_relative: str
    owned_ctypes: bool
    owned_source_relatives: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BaselinePins:
    label: str
    receipt: str
    archive: str
    records: str


@dataclass(frozen=True, slots=True)
class OwnerPins:
    family: str
    recorder: str
    adapter: str
    engine: str
    bridge: str
    owned_sources: tuple[tuple[str, str], ...]
    baseline: BaselinePins


FAMILIES = types.MappingProxyType({
    "rust": FamilySpec(
        "rust", "candidates.rust_candidate", "candidates/rust_candidate.py",
        "candidates/_rust_engine.so", "candidates._rust_bridge",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX, False,
        (
            "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
    ),
    "c": FamilySpec(
        "c", "candidates.vm_candidate", "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates._vm_native", "candidates/_vm_native" + EXTENSION_SUFFIX,
        False, ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    ),
    "zig": FamilySpec(
        "zig", "candidates.zig_candidate", "candidates/zig_candidate.py",
        "candidates/_zig_probe.so", "candidates._zig_bridge",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX, True,
        (
            "candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
    ),
})

if not sys.path or sys.path[0] != ROOT:
    sys.path.insert(0, ROOT)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RecorderError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise RecorderError("full evidence is not canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64 and len(set(value)) > 1
        and all(item in "0123456789abcdef" for item in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "a complete evidence field was duplicated")
        result[key] = value
    return result


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_UNCOMPRESSED_BYTES,
            "complete bounded canonical evidence is mandatory: " + label)

    def reject_constant(_: str) -> Any:
        raise RecorderError("nonfinite evidence is forbidden")

    try:
        result = json.loads(
            raw, object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (RecorderError, TypeError, ValueError, UnicodeError,
            json.JSONDecodeError) as error:
        raise RecorderError("invalid complete evidence: " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "complete canonical evidence was truncated or substituted: " + label)
    return result


def validate_label(value: Any) -> str:
    require(
        type(value) is str and 1 <= len(value) <= 64
        and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-"
                for item in value)
        and "--" not in value,
        "an exact bounded lowercase nonescaping run label is mandatory",
    )
    return value


def safe_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and bool(value)
            and "\\" not in value and "\x00" not in value,
            "an exact no-follow relative path is mandatory")
    parts = tuple(value.split("/"))
    require(all(part not in {"", ".", ".."} for part in parts)
            and "/".join(parts) == value,
            "an owner or publication escaped the approved project root")
    return parts


def family_spec(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independently owned Rust, C, or Zig family")
    spec = FAMILIES[value]
    require(
        isinstance(spec, FamilySpec) and spec.name == value
        and spec.adapter_module.startswith("candidates.")
        and spec.bridge_module.startswith("candidates.")
        and spec.adapter_module != spec.bridge_module
        and spec.owned_ctypes is (value == "zig")
        and (spec.engine_relative == spec.bridge_relative) is (value == "c")
        and len(set(spec.owned_source_relatives))
        == len(spec.owned_source_relatives)
        and spec.adapter_relative in spec.owned_source_relatives
        and all(safe_parts(path)[0] == "candidates"
                for path in spec.owned_source_relatives),
        "a sibling, external, or incompletely owned engine was selected",
    )
    return spec


def parse_owned_source(value: Any) -> tuple[str, str]:
    require(type(value) is str and value.count("=") == 1,
            "pin every owned source as exact/path=sha256")
    relative, expected = value.split("=", 1)
    require(safe_parts(relative)[0] == "candidates",
            "a candidate source escaped its independently owned closure")
    return relative, validate_digest(expected, relative)


def make_baseline_pins(
    label: Any, receipt: Any, archive: Any, records: Any,
) -> BaselinePins:
    return BaselinePins(
        validate_label(label),
        validate_digest(receipt, "published baseline receipt"),
        validate_digest(archive, "published lossless baseline archive"),
        validate_digest(records, "all 5,120 frozen reference observations"),
    )


def make_owner_pins(
    family: Any, recorder: Any, adapter: Any, engine: Any, bridge: Any,
    sources: Any, baseline: BaselinePins,
) -> OwnerPins:
    spec = family_spec(family)
    require(isinstance(baseline, BaselinePins),
            "an exact previously published baseline is mandatory")
    validate_digest(recorder, "frozen substitution recorder")
    validate_digest(adapter, "owned candidate adapter")
    validate_digest(engine, "owned native regex engine")
    validate_digest(bridge, "owned native Python bridge")
    require(type(sources) is list,
            "explicitly pin every independently owned candidate source")
    parsed = tuple(parse_owned_source(item) for item in sources)
    require(len(parsed) == len(spec.owned_source_relatives)
            and len({path for path, _ in parsed}) == len(parsed)
            and {path for path, _ in parsed}
            == set(spec.owned_source_relatives),
            "pin every owned parser, compiler, engine, bridge, and lockfile")
    mapped = dict(parsed)
    require(mapped[spec.adapter_relative] == adapter,
            "the native adapter escaped its exact source closure")
    require((engine == bridge) is (spec.name == "c"),
            "only the combined C engine and bridge may alias")
    return OwnerPins(
        spec.name, recorder, adapter, engine, bridge,
        tuple((path, mapped[path]) for path in spec.owned_source_relatives),
        baseline,
    )


def encode_bytes(value: bytes) -> dict[str, str]:
    require(type(value) is bytes, "an exact bytes payload is mandatory")
    return {"kind": "bytes", "hex": value.hex()}


def encode_text(value: str) -> dict[str, str]:
    require(type(value) is str, "an exact Unicode payload is mandatory")
    return {"kind": "str", "value": value}


def validate_payload(value: Any) -> dict[str, str]:
    require(type(value) is dict, "an exact typed payload is mandatory")
    if value.get("kind") == "str":
        require(
            set(value) == {"kind", "value"} and type(value.get("value")) is str,
            "an original Unicode payload was forged",
        )
        return value
    require(
        set(value) == {"kind", "hex"}
        and value.get("kind") == "bytes"
        and type(value.get("hex")) is str,
        "an original bytes payload was forged",
    )
    try:
        raw = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise RecorderError("a substitution payload has invalid hexadecimal") from error
    require(raw.hex() == value["hex"], "a substitution payload is noncanonical")
    return value


def make_carrier(
    kind: str,
    payload: bytes | str,
    *,
    role: str,
) -> dict[str, Any]:
    approved = SUBJECT_KINDS if role == "subject" else REPLACEMENT_KINDS
    require(role in {"subject", "replacement"} and kind in approved, "an unfrozen carrier was selected")
    if type(payload) is str:
        require(kind in {"str", "callable"}, "a Unicode payload entered a binary carrier")
        encoded = encode_text(payload)
        length = len(payload)
    else:
        require(type(payload) is bytes and kind != "str", "an exact binary carrier is mandatory")
        encoded = encode_bytes(payload)
        length = len(payload)
    readonly = kind.startswith("readonly-") or kind.startswith("released-readonly-")
    if kind == "pep688-wrapped-readonly":
        readonly = True
    step = 2 if "strided" in kind else 1
    released = kind.startswith("released-")
    if kind.startswith("pep688-"):
        if "mutating" in kind:
            behavior = "mutate"
        elif kind == "pep688-failing":
            behavior = "fail"
        else:
            behavior = "stable"
        hash_behavior = (
            "fixed" if "fixed-hash" in kind
            else "unhashable" if "unhashable" in kind
            else "fail" if "failing-hash" in kind
            else "none"
        )
    else:
        behavior = "none"
        hash_behavior = "none"
    return {
        "kind": kind,
        "payload": encoded,
        "start": 0,
        "stop": length,
        "step": step,
        "readonly": readonly,
        "released": released,
        "behavior": behavior,
        "hash_behavior": hash_behavior,
        "wrapped": kind.startswith("pep688-wrapped-"),
    }


def validate_carrier(value: Any, *, role: str) -> dict[str, Any]:
    approved = SUBJECT_KINDS if role == "subject" else REPLACEMENT_KINDS
    require(
        role in {"subject", "replacement"}
        and type(value) is dict
        and set(value) == {
            "kind", "payload", "start", "stop", "step", "readonly",
            "released", "behavior", "hash_behavior", "wrapped",
        }
        and value.get("kind") in approved
        and type(value.get("start")) is int
        and type(value.get("stop")) is int
        and type(value.get("step")) is int
        and value["step"] in (1, 2)
        and type(value.get("readonly")) is bool
        and type(value.get("released")) is bool
        and type(value.get("wrapped")) is bool
        and value.get("behavior") in BUFFER_BEHAVIORS
        and value.get("hash_behavior") in HASH_BEHAVIORS,
        "a complete original carrier, exporter, shape, or ownership was forged: " + role,
    )
    payload = validate_payload(value["payload"])
    length = len(payload["value"]) if payload["kind"] == "str" else len(bytes.fromhex(payload["hex"]))
    require(
        0 <= value["start"] <= value["stop"] <= length,
        "a frozen carrier escaped its actual original storage bounds",
    )
    kind = value["kind"]
    require(
        (value["step"] == 2) is ("strided" in kind),
        "a real memoryview stride was concealed",
    )
    require(
        value["released"] is kind.startswith("released-"),
        "a real released memoryview was substituted",
    )
    require(
        value["wrapped"] is kind.startswith("pep688-wrapped-"),
        "a nested PEP-688 memoryview wrapper was substituted",
    )
    if kind.startswith("pep688-"):
        expected_behavior = (
            "mutate" if "mutating" in kind
            else "fail" if kind == "pep688-failing"
            else "stable"
        )
        expected_hash = (
            "fixed" if "fixed-hash" in kind
            else "unhashable" if "unhashable" in kind
            else "fail" if "failing-hash" in kind
            else "none"
        )
        require(
            value["behavior"] == expected_behavior
            and value["hash_behavior"] == expected_hash,
            "a genuine tracked exporter, buffer failure, or custom hash was forged",
        )
    else:
        require(
            value["behavior"] == "none" and value["hash_behavior"] == "none",
            "an ordinary carrier impersonated a tracked buffer exporter",
        )
    if kind == "str":
        require(payload["kind"] == "str", "a Unicode subject lost its exact string domain")
    elif kind != "callable":
        require(payload["kind"] == "bytes", "a binary carrier lost its exact bytes domain")
    return value


def build_frozen_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and seed == PUBLISHED_SEED, "the exact prospectively frozen published 64-bit seed is required")
    seeded = random.Random(seed)
    cases: list[dict[str, Any]] = []
    for cohort in COHORTS:
        for variant in range(VARIANTS_PER_COHORT):
            suffix = "".join(seeded.choice("abcdef0123456789") for _ in range(12))
            text_domain = cohort.startswith("text-")
            if text_domain:
                source_text = "caf\u00e942 beta7 e\u0301 \ud800 delta3 " + suffix
                payload: bytes | str = source_text
                pattern: bytes | str = r"(?P<word>\w+?)(?P<number>[0-9]+)"
                literal: bytes | str = "X"
                named: bytes | str = r"<\g<word>:\g<number>>"
                numbered: bytes | str = r"<\1:\2>"
            else:
                payload = ("alpha42 beta7 gamma3 " + suffix).encode("ascii")
                pattern = rb"(?P<word>[A-Za-z]+)(?P<number>[0-9]*)"
                literal = b"X"
                named = rb"<\g<word>:\g<number>>"
                numbered = rb"<\1:\2>"

            subject_kind = "str" if text_domain else "bytes"
            replacement_kind = "str" if text_domain else "bytes"
            style = ("literal", "escaped-named", "escaped-numeric", "callable")[variant % 4]
            if "literal" in cohort:
                style = "literal"
            elif "callback-error" in cohort:
                style = "callable-error"
            elif "callback" in cohort:
                style = "callable"
            elif "missing-capture" in cohort:
                style = "missing-capture"
            elif "invalid-escape" in cohort:
                style = "invalid-escape"
            elif "numeric-captures" in cohort:
                style = "escaped-numeric"
            elif "escaped" in cohort or "named-captures" in cohort:
                style = "escaped-named"

            if "zero-width-lookahead" in cohort:
                pattern = r"(?=\w)" if text_domain else rb"(?=[A-Za-z])"
            elif "zero-width-empty" in cohort:
                pattern = r"" if text_domain else rb""
            elif "lone-surrogate" in cohort:
                pattern = "\ud800"
            elif "combining-mark" in cohort:
                pattern = "e\u0301"
            elif "precomposed-unicode" in cohort:
                pattern = "\u00e9"

            if cohort.startswith("bytearray-subject-"):
                subject_kind = "bytearray"
            elif cohort.startswith("bytearray-replacement-"):
                replacement_kind = "bytearray"
            elif "subject-memoryview" in cohort:
                subject_kind = cohort.removesuffix("-subject-memoryview") + "-memoryview"
            elif "template-memoryview" in cohort:
                replacement_kind = cohort.removesuffix("-template-memoryview") + "-memoryview"
            elif cohort.startswith("pep688-") and cohort.endswith("-subject"):
                subject_kind = cohort.removesuffix("-subject")
            elif cohort.startswith("pep688-") and cohort.endswith("-template"):
                replacement_kind = cohort.removesuffix("-template")

            if cohort == "nested-stable-subject-and-template":
                subject_kind, replacement_kind = "pep688-stable", "pep688-stable"
            elif cohort == "nested-mutating-subject-and-template":
                subject_kind, replacement_kind = "pep688-mutating", "pep688-mutating"
            elif cohort == "nested-stable-fixed-hash-template":
                subject_kind, replacement_kind = "pep688-stable", "pep688-fixed-hash"
            elif cohort == "nested-mutating-unhashable-template":
                subject_kind, replacement_kind = "pep688-mutating", "pep688-unhashable"
            elif cohort == "nested-failing-template-after-subject":
                subject_kind, replacement_kind = "pep688-stable", "pep688-failing"
            elif cohort == "match-expand-buffer-retention":
                subject_kind, replacement_kind = "writable-memoryview", "readonly-memoryview"
            elif cohort == "callback-capture-and-buffer-order":
                subject_kind, replacement_kind = "pep688-stable", "callable"
                style = "callable"

            if cohort == "text-cross-domain-bytes-template":
                replacement_kind = "bytes"
                replacement_payload: bytes | str = b"X"
            elif style == "literal":
                replacement_payload = literal
            elif style == "escaped-named":
                replacement_payload = named
            elif style == "escaped-numeric":
                replacement_payload = numbered
            elif style == "missing-capture":
                replacement_payload = r"\g<absent>" if text_domain else rb"\g<absent>"
            elif style == "invalid-escape":
                replacement_payload = r"\q" if text_domain else rb"\q"
            else:
                replacement_payload = literal

            if replacement_kind == "callable" or style.startswith("callable"):
                replacement_kind = "callable"
            api = APIS[variant % len(APIS)]
            if cohort == "match-expand-buffer-retention":
                api = "match.expand"
            replacement = make_carrier(
                replacement_kind,
                replacement_payload,
                role="replacement",
            )
            subject = make_carrier(subject_kind, payload, role="subject")
            case = {
                "case": "substitution-buffer-semantics.v1." + format(len(cases), "05d"),
                "cohort": cohort,
                "variant": variant,
                "seed": seed,
                "api": api,
                "flags": FLAGS[variant % len(FLAGS)],
                "count": COUNTS[(variant // len(APIS)) % len(COUNTS)],
                "pos": WINDOW_STARTS[variant % len(WINDOW_STARTS)],
                "endpos": WINDOW_ENDS[(variant // len(WINDOW_STARTS)) % len(WINDOW_ENDS)],
                "pattern": encode_text(pattern) if type(pattern) is str else encode_bytes(pattern),
                "subject": subject,
                "replacement": replacement,
                "replacement_style": style,
                "callback_raises": style == "callable-error",
            }
            cases.append(case)
    return cases


def validate_matrix(
    matrix: Any, expected_sha256: str = MATRIX_SHA256,
) -> str:
    validate_digest(expected_sha256, "prospectively frozen substitution case matrix")
    require(
        len(COHORTS) == 64
        and len(set(COHORTS)) == 64
        and VARIANTS_PER_COHORT == 80
        and CASE_COUNT == 5_120,
        "the balanced original substitution obligation denominator silently changed",
    )
    require(
        type(matrix) is list and len(matrix) == CASE_COUNT,
        "all 5,120 independently frozen replacement-buffer cases are mandatory",
    )
    actual = build_frozen_matrix()
    require(
        matrix == actual and digest(matrix) == expected_sha256,
        "the exact substitution seed, ordered case rows, or matrix digest changed",
    )
    coverage: dict[str, int] = {name: 0 for name in COHORTS}
    identifiers: set[str] = set()
    for index, row in enumerate(matrix):
        require(
            type(row) is dict
            and set(row) == {
                "case", "cohort", "variant", "seed", "api", "flags", "count",
                "pos", "endpos", "pattern", "subject", "replacement",
                "replacement_style", "callback_raises",
            }
            and row.get("case") == "substitution-buffer-semantics.v1." + format(index, "05d")
            and row["case"] not in identifiers
            and row.get("cohort") == COHORTS[index // VARIANTS_PER_COHORT]
            and type(row.get("variant")) is int
            and row["variant"] == index % VARIANTS_PER_COHORT
            and type(row.get("seed")) is int
            and row["seed"] == PUBLISHED_SEED
            and row.get("api") in APIS
            and type(row.get("flags")) is int
            and row["flags"] in FLAGS
            and type(row.get("count")) is int
            and row["count"] in COUNTS
            and type(row.get("pos")) is int
            and row["pos"] in WINDOW_STARTS
            and (row.get("endpos") is None or type(row.get("endpos")) is int)
            and row["endpos"] in WINDOW_ENDS
            and row.get("replacement_style") in REPLACEMENT_STYLES
            and type(row.get("callback_raises")) is bool,
            "a complete original replacement case was removed, reordered, or forged",
        )
        validate_payload(row["pattern"])
        validate_carrier(row["subject"], role="subject")
        validate_carrier(row["replacement"], role="replacement")
        require(
            row["callback_raises"] is (row["replacement_style"] == "callable-error"),
            "a genuine failing replacement callback was concealed",
        )
        identifiers.add(row["case"])
        coverage[row["cohort"]] += 1
    require(
        all(count == VARIANTS_PER_COHORT for count in coverage.values()),
        "an entire replacement-buffer cohort silently changed weight",
    )
    return matrix

def directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


def regular_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0))


@contextlib.contextmanager
def open_owned_descriptor(relative: str) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_parts(relative)
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact frozen repository root was replaced")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an exact frozen owner parent became a symlink")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino)
                == (named.st_dev, named.st_ino),
                "an exact frozen source or archive was replaced")
        yield descriptor, before
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "an exact frozen owner changed while being authenticated")
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_owned_regular(
    relative: str, expected: str, maximum: int, *, retain: bool = False,
) -> tuple[dict[str, Any], bytes | None]:
    validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_ARCHIVE_BYTES,
            "an exact bounded source, native owner, or archive is mandatory")
    with open_owned_descriptor(relative) as (descriptor, before):
        require(0 < before.st_size <= maximum,
                "an exact pinned source or archive exceeds its safe bound")
        hasher = hashlib.sha256()
        remaining = before.st_size
        pieces: list[bytes] = []
        while remaining:
            raw = os.read(descriptor, min(remaining, 1_048_576))
            require(type(raw) is bytes and bool(raw),
                    "an independently owned source or archive was truncated")
            hasher.update(raw)
            if retain:
                pieces.append(raw)
            remaining -= len(raw)
        require(os.read(descriptor, 1) == b""
                and hasher.hexdigest() == expected,
                "an exact pinned source or archive was substituted")
        owner = {
            "relative": relative, "sha256": expected,
            "bytes": before.st_size, "device": before.st_dev,
            "inode": before.st_ino,
        }
        return owner, b"".join(pieces) if retain else None


def validate_owner(value: Any, relative: str, expected: str) -> dict[str, Any]:
    require(type(value) is dict
            and set(value) == {"relative", "sha256", "bytes", "device", "inode"}
            and value.get("relative") == relative
            and value.get("sha256") == expected
            and type(value.get("bytes")) is int and value["bytes"] > 0
            and type(value.get("device")) is int and value["device"] >= 0
            and type(value.get("inode")) is int and value["inode"] > 0,
            "an exact complete native or frozen source owner changed")
    return value


def validate_preserved_previous_failure(value: Any) -> dict[str, Any]:
    expected = {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-v1-"
            "controller-failure-preserved-v1"
        ),
        "status": "FAIL",
        "python": "3.14.6",
        "label": "shared-suite-v1",
        "recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "recorder_source_sha256": PREVIOUS_RECORDER_SHA256,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "actual_baseline_controller_invocations": 1,
        "actual_reference_worker_count": "UNKNOWN",
        "reported_reference_worker_count_is_reliable": False,
        "actual_candidate_workers": 0,
        "reference_outcomes_status": "NOT MEASURED",
        "baseline_result_status": "NOT MEASURED",
        "report_publication_status": "NOT PUBLISHED",
        "receipt_publication_status": "NOT PUBLISHED",
        "controller_exit_code": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }
    additional = {
        "complete_controller_failure_stdout",
        "failure_explanation",
    }
    require(
        type(value) is dict and set(value) == set(expected) | additional,
        "the complete genuinely observed V1 publication failure was omitted",
    )
    for field, original in expected.items():
        require(
            value.get(field) == original
            and type(value.get(field)) is type(original),
            "the genuinely preserved V1 failure changed: " + field,
        )
    require(
        type(value.get("failure_explanation")) is str
        and "268435456" in value["failure_explanation"]
        and "not reliable" in value["failure_explanation"],
        "the genuine V1 bound and unreliable worker count were concealed",
    )
    nested = {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-"
            "recorder-v1-failure"
        ),
        "status": "FAIL",
        "error_type": "RecorderError",
        "error": "a complete substitution report exceeds its bound",
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(
        value["complete_controller_failure_stdout"] == nested,
        "the actual V1 controller failure or its false-zero envelope changed",
    )
    return value


def validate_frozen_source_owners(
    value: Any,
    recorder_pin: str,
) -> dict[str, Any]:
    owners = (
        ("recorder", SOURCE_RELATIVE, recorder_pin),
        (
            "previous_recorder",
            PREVIOUS_RECORDER_RELATIVE,
            PREVIOUS_RECORDER_SHA256,
        ),
        (
            "preserved_previous_failure",
            PRESERVED_PREVIOUS_FAILURE_RELATIVE,
            PRESERVED_PREVIOUS_FAILURE_SHA256,
        ),
        ("substitution_oracle", ORACLE_RELATIVE, ORACLE_SHA256),
        ("original_v5", V5_RELATIVE, V5_SHA256),
        ("from_scratch_audit_v3", AUDIT_RELATIVE, AUDIT_SHA256),
    )
    require(
        type(value) is dict
        and set(value) == {name for name, _, _ in owners},
        "a frozen source or the actually preserved V1 failure was omitted",
    )
    for name, relative, expected in owners:
        validate_owner(value[name], relative, expected)
    return value


def verify_runtime(*, candidate_loaded: bool = False) -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == ROOT
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == SOURCE_ABSOLUTE
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
            "use only exact isolated pinned stable CPython and this recorder")
    if not candidate_loaded:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "a candidate escaped into reference-only authentication")


def authenticate_module(
    module_name: str, relative: str, expected: str,
) -> tuple[types.ModuleType, dict[str, Any]]:
    before, _ = read_owned_regular(relative, expected, MAX_SOURCE_BYTES)
    module = importlib.import_module(module_name)
    absolute = ROOT + "/" + relative
    module_spec = getattr(module, "__spec__", None)
    loader = getattr(module_spec, "loader", None)
    require(type(module) is types.ModuleType
            and module.__name__ == module_name
            and getattr(module, "__file__", None) == absolute
            and os.path.realpath(absolute) == absolute
            and module_spec is not None
            and getattr(module_spec, "name", None) == module_name
            and getattr(module_spec, "origin", None) == absolute
            and isinstance(loader, importlib.machinery.SourceFileLoader)
            and getattr(loader, "name", None) == module_name
            and getattr(loader, "path", None) == absolute,
            "a frozen genuine source module or loader was substituted")
    after, _ = read_owned_regular(relative, expected, MAX_SOURCE_BYTES)
    require(before == after,
            "an authenticated frozen source changed during import")
    return module, before


def authenticate_frozen_tools(
    recorder_pin: str,
) -> tuple[Any, Any, Any, list[dict[str, Any]], dict[str, Any]]:
    verify_runtime()
    recorder_owner, _ = read_owned_regular(
        SOURCE_RELATIVE, recorder_pin, MAX_SOURCE_BYTES,
    )
    previous_owner, _ = read_owned_regular(
        PREVIOUS_RECORDER_RELATIVE,
        PREVIOUS_RECORDER_SHA256,
        MAX_SOURCE_BYTES,
    )
    preserved_failure_owner, preserved_failure_raw = read_owned_regular(
        PRESERVED_PREVIOUS_FAILURE_RELATIVE,
        PRESERVED_PREVIOUS_FAILURE_SHA256,
        MAX_SOURCE_BYTES,
        retain=True,
    )
    require(
        preserved_failure_raw is not None,
        "retain the complete genuinely observed V1 publication failure",
    )
    validate_preserved_previous_failure(
        decode_document(
            preserved_failure_raw,
            "complete preserved genuine V1 controller failure",
        )
    )
    oracle, oracle_owner = authenticate_module(
        ORACLE_MODULE, ORACLE_RELATIVE, ORACLE_SHA256,
    )
    v5, v5_owner = authenticate_module(V5_MODULE, V5_RELATIVE, V5_SHA256)
    audit, audit_owner = authenticate_module(
        AUDIT_MODULE, AUDIT_RELATIVE, AUDIT_SHA256,
    )
    require(
        getattr(oracle, "SCHEMA", None) == ORACLE_SCHEMA
        and getattr(oracle, "MATRIX_SHA256", None) == MATRIX_SHA256
        and getattr(oracle, "PUBLISHED_SEED", None) == PUBLISHED_SEED
        and getattr(oracle, "CASE_COUNT", None) == CASE_COUNT
        and tuple(getattr(oracle, "COHORTS", ())) == COHORTS
        and getattr(oracle, "VARIANTS_PER_COHORT", None)
        == VARIANTS_PER_COHORT
        and tuple(getattr(oracle, "APIS", ())) == APIS
        and getattr(oracle, "SIMPLE_BUFFER_FLAG", None)
        == SIMPLE_BUFFER_FLAG
        and getattr(oracle, "FULL_READONLY_BUFFER_FLAG", None)
        == FULL_READONLY_BUFFER_FLAG
        and getattr(oracle, "V5_GUARD_SHA256", None) == V5_SHA256
        and getattr(oracle, "OWNERSHIP_AUDIT_SHA256", None) == AUDIT_SHA256
        and getattr(v5, "SOURCE_RELATIVE", None) == V5_RELATIVE
        and v5.current_source_sha256() == V5_SHA256
        and getattr(audit, "SOURCE_RELATIVE", None) == AUDIT_RELATIVE,
        "the frozen substitution oracle or V3/V5 ownership policy changed",
    )
    validate_compact_bounds()
    matrix = validate_matrix(build_frozen_matrix())
    require(
        oracle.build_matrix() == matrix
        and oracle.validate_matrix(matrix, MATRIX_SHA256) == MATRIX_SHA256,
        "the independently frozen 5,120-case substitution matrix changed",
    )
    return oracle, v5, audit, matrix, validate_frozen_source_owners(
        {
            "recorder": recorder_owner,
            "previous_recorder": previous_owner,
            "preserved_previous_failure": preserved_failure_owner,
            "substitution_oracle": oracle_owner,
            "original_v5": v5_owner,
            "from_scratch_audit_v3": audit_owner,
        },
        recorder_pin,
    )




def approved_paths(
    kind: str, label: str, family: str | None = None,
) -> tuple[str, str]:
    validate_label(label)
    require(kind in {"baseline", "candidate"},
            "select only one reference or owned-candidate evidence class")
    if kind == "baseline":
        require(family is None, "a baseline cannot select a candidate")
        slug = "substitution-buffer-semantics-v1-" + label
    else:
        spec = family_spec(family)
        slug = spec.name + "-substitution-buffer-semantics-v1-" + label
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json.gz",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


def require_directory_identity(a: Any, b: Any, c: Any) -> None:
    require(type(a) is tuple and type(b) is tuple and type(c) is tuple
            and len(a) == len(b) == len(c) == 2
            and all(type(item) is int and item >= 0
                    for pair in (a, b, c) for item in pair)
            and a == b == c,
            "the retained no-follow evidence directory was replaced")


def verify_retained_directory(value: Mapping[str, Any]) -> int:
    descriptor = value.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "retain exactly the approved no-follow evidence directory")
    retained = os.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode),
            "the retained substitution evidence directory was replaced")
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "the exact approved evidence path became a symlink")
        actual = os.fstat(current)
        require_directory_identity(
            (retained.st_dev, retained.st_ino),
            (value.get("directory_device"), value.get("directory_inode")),
            (actual.st_dev, actual.st_ino),
        )
    finally:
        for current in reversed(opened):
            os.close(current)
    return descriptor


@contextlib.contextmanager
def preflight_fresh_outputs(
    kind: str, label: str, family: str | None = None,
) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(kind, label, family)
    report_parts, receipt_parts = safe_parts(report), safe_parts(receipt)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "select exactly one lossless report and publication receipt")
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        for component in report_parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "the approved evidence parent became a symlink")
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError(
                "refusing to overwrite frozen substitution evidence: " + basename
            )
        actual = os.fstat(current)
        result = {
            "report_relative": report, "receipt_relative": receipt,
            "report_basename": report_parts[-1],
            "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": actual.st_dev,
            "directory_inode": actual.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_observation": True,
        }
        verify_retained_directory(result)
        yield result
    finally:
        for current in reversed(opened):
            os.close(current)


def iter_canonical(value: Mapping[str, Any]) -> Iterator[bytes]:
    encoder = json.JSONEncoder(
        ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    )
    for part in encoder.iterencode(dict(value)):
        require(type(part) is str,
                "a complete evidence encoder produced invalid data")
        yield part.encode("ascii")
    yield b"\n"


def readback_archive(
    preflight: Mapping[str, Any], basename: str,
    expected_archive: str, expected_plain: str,
    archive_bytes: int, plain_bytes: int,
) -> None:
    directory = verify_retained_directory(preflight)
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        owner = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(owner.st_mode)
                and (owner.st_dev, owner.st_ino)
                == (named.st_dev, named.st_ino)
                and owner.st_size == archive_bytes,
                "a complete lossless substitution report was replaced")
        archive_hasher = hashlib.sha256()
        remaining = archive_bytes
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "a published lossless substitution report was truncated")
            archive_hasher.update(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b""
                and archive_hasher.hexdigest() == expected_archive,
                "a published substitution archive gained or lost evidence")
        os.lseek(descriptor, 0, os.SEEK_SET)
        plain_hasher = hashlib.sha256()
        count = 0
        with io.FileIO(descriptor, "rb", closefd=False) as source:
            with gzip.GzipFile(fileobj=source, mode="rb") as compressed:
                while True:
                    block = compressed.read(131_072)
                    require(type(block) is bytes,
                            "lossless substitution evidence produced invalid bytes")
                    if not block:
                        break
                    count += len(block)
                    require(count <= MAX_COMPACT_REPORT_BYTES,
                            "lossless substitution evidence exceeds its safe bound")
                    plain_hasher.update(block)
        require(count == plain_bytes
                and plain_hasher.hexdigest() == expected_plain,
                "lossless substitution evidence differs from its original report")
    finally:
        os.close(descriptor)
    verify_retained_directory(preflight)


def publish_document(
    preflight: Mapping[str, Any], document: Mapping[str, Any],
    *, compressed: bool,
) -> dict[str, Any]:
    kind = "report" if compressed else "receipt"
    predicted_plain_bytes = (
        validate_compact_report_document(document)["complete_report_bytes"]
        if compressed else None
    )
    basename = preflight[kind + "_basename"]
    directory = verify_retained_directory(preflight)
    temporary = (
        ".rebar-substitution-buffer-recorder-v2-" + basename
        + "-" + str(os.getpid())
    )
    safe_parts(temporary)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    identity: tuple[int, int] | None = None
    linked = False
    plain_hasher = hashlib.sha256()
    plain_bytes = 0
    write_calls = 0
    try:
        original = os.fstat(descriptor)
        require(stat.S_ISREG(original.st_mode),
                "a fresh substitution evidence temporary is not regular")
        identity = (original.st_dev, original.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "a fresh substitution evidence temporary was substituted")
        if compressed:
            with io.FileIO(descriptor, "wb", closefd=False) as output:
                with gzip.GzipFile(
                    filename="", fileobj=output, mode="wb",
                    compresslevel=9, mtime=0,
                ) as archive:
                    for piece in iter_canonical(document):
                        plain_bytes += len(piece)
                        require(plain_bytes <= MAX_COMPACT_REPORT_BYTES,
                                "a complete substitution report exceeds its bound")
                        plain_hasher.update(piece)
                        archive.write(piece)
                        write_calls += 1
        else:
            for piece in iter_canonical(document):
                plain_bytes += len(piece)
                require(plain_bytes <= MAX_SOURCE_BYTES,
                        "a substitution publication receipt exceeds its bound")
                plain_hasher.update(piece)
                offset = 0
                while offset < len(piece):
                    actual = os.write(descriptor, piece[offset:])
                    require(type(actual) is int and actual > 0,
                            "a complete substitution receipt was truncated")
                    offset += actual
                    write_calls += 1
        os.fsync(descriptor)
        if compressed:
            require(
                plain_bytes == predicted_plain_bytes,
                "the single-stream evidence differs from its proven exact size",
            )
        actual = os.fstat(descriptor)
        require(0 < actual.st_size <= MAX_ARCHIVE_BYTES,
                "a complete compressed report or receipt exceeds its bound")
        verify_retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "substitution evidence changed before its no-clobber publication")
        reader = os.open(temporary, regular_flags(), dir_fd=directory)
        try:
            archive_hasher = hashlib.sha256()
            remaining = actual.st_size
            while remaining:
                block = os.read(reader, min(remaining, 1_048_576))
                require(type(block) is bytes and bool(block),
                        "an authenticated substitution temporary was truncated")
                archive_hasher.update(block)
                remaining -= len(block)
            require(os.read(reader, 1) == b"",
                    "an authenticated substitution temporary gained a suffix")
        finally:
            os.close(reader)
        os.link(temporary, basename, src_dir_fd=directory,
                dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        os.fsync(directory)
        verify_retained_directory(preflight)
        destination = os.stat(basename, dir_fd=directory,
                              follow_symlinks=False)
        require((destination.st_dev, destination.st_ino) == identity,
                "an atomically published substitution report was substituted")
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "refusing to remove a substituted owned temporary")
        os.unlink(temporary, dir_fd=directory)
        os.fsync(directory)
    except BaseException:
        if not linked and identity is not None:
            try:
                named = os.stat(temporary, dir_fd=directory,
                                follow_symlinks=False)
                if (named.st_dev, named.st_ino) == identity:
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
            except (OSError, RecorderError):
                pass
        raise
    finally:
        os.close(descriptor)
    result = {
        "path": preflight[kind + "_relative"],
        "bytes": actual.st_size,
        "sha256": archive_hasher.hexdigest(),
        "uncompressed_bytes": plain_bytes,
        "uncompressed_sha256": plain_hasher.hexdigest(),
        "compression": "gzip-mtime-zero-level-9" if compressed else "none",
        "actual_write_calls": write_calls,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True,
        "owned_temporary_removed": True,
        "complete_readback_verified": True,
    }
    if compressed:
        readback_archive(
            preflight, basename, result["sha256"],
            result["uncompressed_sha256"], result["bytes"],
            result["uncompressed_bytes"],
        )
    else:
        require(result["bytes"] == result["uncompressed_bytes"]
                and result["sha256"] == result["uncompressed_sha256"],
                "a substitution receipt was compressed or substituted")
        directory = verify_retained_directory(preflight)
        reader = os.open(basename, regular_flags(), dir_fd=directory)
        try:
            parts: list[bytes] = []
            remaining = result["bytes"]
            while remaining:
                raw = os.read(reader, min(remaining, 1_048_576))
                require(bool(raw), "a durable substitution receipt was truncated")
                parts.append(raw)
                remaining -= len(raw)
            require(os.read(reader, 1) == b""
                    and b"".join(parts) == canonical(dict(document)),
                    "a durable substitution receipt differs from its exact source")
        finally:
            os.close(reader)
    verify_retained_directory(preflight)
    return result


def validate_stream_byte_count(value: Any, label: str) -> int:
    require(
        type(value) is int and 0 <= value <= MAX_PROCESS_BYTES,
        "a complete worker stream exceeds its proven 96 MiB bound: " + label,
    )
    return value


def encoded_stream_byte_count(value: Any, label: str) -> int:
    size = validate_stream_byte_count(value, label)
    encoded = ((size + 2) // 3) * 4
    require(
        0 <= encoded <= MAX_ENCODED_PROCESS_STREAM_BYTES,
        "a complete reversible process base64 stream exceeds 128 MiB",
    )
    return encoded


def validate_compact_metadata_byte_count(value: Any) -> int:
    require(
        type(value) is int
        and 0 < value <= MAX_COMPACT_REPORT_METADATA_BYTES,
        "complete compact evidence metadata exceeds its frozen 32 MiB bound",
    )
    return value


def validate_compact_bounds() -> dict[str, int]:
    require(
        MAX_PROCESS_BYTES == 96 * 1024 * 1024
        and MAX_ENCODED_PROCESS_STREAM_BYTES == 128 * 1024 * 1024
        and MAX_COMPACT_REPORT_METADATA_BYTES == 32 * 1024 * 1024
        and MAX_COMPACT_REPORT_BYTES == 288 * 1024 * 1024
        and MAX_UNCOMPRESSED_BYTES == 320 * 1024 * 1024
        and MAX_ARCHIVE_BYTES == 384 * 1024 * 1024
        and MAX_COMPACT_REPORT_BYTES < MAX_UNCOMPRESSED_BYTES
        and MAX_UNCOMPRESSED_BYTES < MAX_ARCHIVE_BYTES,
        "the prospectively frozen lossless two-stream budget was weakened",
    )
    return {
        "maximum_raw_process_stream_bytes": MAX_PROCESS_BYTES,
        "maximum_encoded_process_stream_bytes": (
            MAX_ENCODED_PROCESS_STREAM_BYTES
        ),
        "maximum_process_stream_count": 2,
        "maximum_compact_report_metadata_bytes": (
            MAX_COMPACT_REPORT_METADATA_BYTES
        ),
        "maximum_compact_report_bytes": MAX_COMPACT_REPORT_BYTES,
        "maximum_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "maximum_archive_bytes": MAX_ARCHIVE_BYTES,
    }


def capture_stream(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is bytes,
            "retain complete genuine bounded worker process bytes: " + label)
    validate_stream_byte_count(len(value), label)
    result = {
        "base64": base64.b64encode(value).decode("ascii"),
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": True,
    }
    require(
        len(result["base64"])
        == encoded_stream_byte_count(len(value), label),
        "the complete base64 process stream changed its proven byte bound",
    )
    return result



def decode_stream(value: Any, label: str) -> bytes:
    require(
        type(value) is dict
        and set(value) == {"base64", "bytes", "sha256", "complete"}
        and type(value.get("base64")) is str
        and type(value.get("bytes")) is int
        and value.get("complete") is True,
        "a complete reversible substitution worker stream was concealed: "
        + label,
    )
    validate_stream_byte_count(value["bytes"], label)
    validate_digest(value["sha256"], label)
    require(
        len(value["base64"])
        == encoded_stream_byte_count(value["bytes"], label),
        "a full isolated process stream lost its exact base64 length",
    )
    try:
        original = base64.b64decode(
            value["base64"].encode("ascii"), validate=True,
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise RecorderError(
            "a complete native process stream is not canonical base64: "
            + label
        ) from error
    require(
        len(original) == value["bytes"]
        and hashlib.sha256(original).hexdigest() == value["sha256"]
        and base64.b64encode(original).decode("ascii") == value["base64"],
        "a complete native worker stream was truncated or substituted",
    )
    return original


def validate_compact_report_document(
    document: Any,
) -> dict[str, int]:
    validate_compact_bounds()
    require(
        type(document) is dict
        and document.get("schema") in {
            SCHEMA + "-complete-baseline-report",
            SCHEMA + "-complete-candidate-report",
        },
        "only one exact bounded substitution evidence report can be published",
    )
    kind = (
        "baseline"
        if document["schema"] == SCHEMA + "-complete-baseline-report"
        else "candidate"
    )
    forbidden_duplicates = {
        "complete_decoded_baseline_process",
        "complete_baseline_result",
        "reference_a_records",
        "reference_b_records",
        "reference_a_process",
        "reference_b_process",
        "complete_decoded_candidate_process",
        "complete_candidate_result",
        "baseline_records",
        "candidate_records",
    }
    require(
        not (set(document) & forbidden_duplicates),
        "a complete canonical process or frozen vector was duplicated",
    )
    stdout_field = "complete_" + kind + "_process_stdout"
    stderr_field = "complete_" + kind + "_process_stderr"
    require(
        stdout_field in document and stderr_field in document,
        "retain each original isolated process stdout and stderr exactly once",
    )
    metadata = dict(document)
    encoded_bytes = 0
    for field in (stdout_field, stderr_field):
        stream = document[field]
        original = decode_stream(stream, field)
        require(
            len(original) == stream["bytes"],
            "a compact report substituted its complete raw process evidence",
        )
        encoded_bytes += len(stream["base64"])
        metadata[field] = {**stream, "base64": ""}
    require(
        encoded_bytes <= 2 * MAX_ENCODED_PROCESS_STREAM_BYTES,
        "two complete process streams exceed their exact base64 ceiling",
    )
    metadata_bytes = validate_compact_metadata_byte_count(
        len(canonical(metadata))
    )
    actual_bytes = metadata_bytes + encoded_bytes
    require(
        0 < actual_bytes <= MAX_COMPACT_REPORT_BYTES
        and actual_bytes < MAX_UNCOMPRESSED_BYTES,
        "a complete two-stream report exceeds its prospectively proven bound",
    )
    return {
        "metadata_bytes": metadata_bytes,
        "encoded_process_stream_bytes": encoded_bytes,
        "complete_report_bytes": actual_bytes,
    }



def run_one_process(arguments: list[str]) -> dict[str, Any]:
    require(type(arguments) is list and bool(arguments)
            and arguments[0] == PINNED_PYTHON
            and all(type(item) is str for item in arguments),
            "only an exactly pinned isolated CPython worker is permitted")
    try:
        process = subprocess.Popen(
            arguments, cwd=ROOT, shell=False,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=False,
            env={
                "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                "LC_ALL": "C", "PATH": "/usr/bin:/bin",
            },
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {
            "started": False, "pid": None, "returncode": None,
            "signal": None, "timed_out": False,
            "spawn_error": str(error), "stdout": b"", "stderr": b"",
        }
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=PROCESS_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes
            and type(process.returncode) is int,
            "a genuine isolated worker lost its complete process streams")
    return {
        "started": True, "pid": process.pid,
        "returncode": process.returncode,
        "signal": -process.returncode if process.returncode < 0 else None,
        "timed_out": timed_out, "spawn_error": None,
        "stdout": stdout, "stderr": stderr,
    }


def validate_baseline_result(
    value: Any, oracle: Any, matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    expected = {
        "schema": ORACLE_SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(
        type(value) is dict
        and set(value) == set(expected) | {
            "baseline_records_sha256", "source_owners", "reference_a",
            "reference_b", "reference_a_process", "reference_b_process",
        },
        "a complete two-worker frozen substitution baseline was forged",
    )
    for name, original in expected.items():
        require(
            value.get(name) == original
            and type(value.get(name)) is type(original),
            "a genuine two-reference substitution field changed: " + name,
        )
    validate_digest(
        value["baseline_records_sha256"],
        "all source-ordered substitution reference observations",
    )
    try:
        oracle.validate_source_owners(
            value["source_owners"], ORACLE_SHA256,
        )
        observed_hash = oracle.validate_reference_pair(
            value["reference_a"],
            value["reference_b"],
            value["reference_a_process"],
            value["reference_b_process"],
            source_pin=ORACLE_SHA256,
            matrix=matrix,
        )
    except Exception as error:
        raise RecorderError(
            "the frozen substitution oracle rejected its complete "
            "independent reference workers"
        ) from error
    require(
        observed_hash == value["baseline_records_sha256"]
        and value["source_owners"]
        == value["reference_a"]["source_owners"]
        == value["reference_b"]["source_owners"],
        "two genuinely isolated substitution reference workers disagree",
    )
    return value



def validate_oracle_failure(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("schema") == ORACLE_SCHEMA + "-failure"
            and value.get("status") == "FAIL"
            and type(value.get("error_type")) is str
            and type(value.get("error")) is str
            and value.get("actual_candidate_workers") == 0
            and value.get("actual_candidate_imports") == 0
            and value.get("clock_samples") == 0
            and value.get("timing_trials_run") == 0
            and value.get("workspace_files_written") == 0
            and value.get("evidence_files_created") == 0
            and value.get("benchmark_files_read") == 0
            and value.get("hidden_cases_read") == 0
            and value.get("performance") == "NOT MEASURED",
            "a genuine complete reference-worker failure was forged")
    nested = value.get("complete_reference_worker_failure")
    if nested is not None:
        require(type(nested) is dict,
                "a complete failed reference process was concealed")
        if "stdout" in nested:
            decode_stream(nested["stdout"], "failed reference stdout")
        if "stderr" in nested:
            decode_stream(nested["stderr"], "failed reference stderr")
    return value


def baseline_source_fields(
    recorder_pin: str, label: str,
) -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "label": validate_label(label),
        "recorder_relative": SOURCE_RELATIVE,
        "recorder_source_sha256": recorder_pin,
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "cohorts": list(COHORTS),
        "apis": list(APIS),
        "simple_buffer_flag": SIMPLE_BUFFER_FLAG,
        "full_readonly_buffer_flag": FULL_READONLY_BUFFER_FLAG,
        **validate_compact_bounds(),
    }




def build_baseline_report(
    recorder_pin: str,
    label: str,
    process: Mapping[str, Any],
    oracle: Any,
    matrix: list[dict[str, Any]],
    before: Mapping[str, Any],
    after: Mapping[str, Any] | None,
    *,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    validate_frozen_source_owners(before, recorder_pin)
    if after is not None:
        validate_frozen_source_owners(after, recorder_pin)
    failures: list[str] = []
    raw_stdout = process.get("stdout")
    raw_stderr = process.get("stderr")
    stdout = capture_stream(
        raw_stdout,
        "complete baseline controller stdout",
    )
    stderr = capture_stream(
        raw_stderr,
        "complete baseline controller stderr",
    )
    result: dict[str, Any] | None = None
    structured_failure: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append(
            "the pinned baseline could not start: "
            + str(process.get("spawn_error"))
        )
    if process.get("timed_out") is True:
        failures.append(
            "the genuinely isolated reference controller exceeded its timeout"
        )
    if raw_stdout:
        try:
            decoded = decode_document(
                raw_stdout,
                "complete genuine reference controller",
            )
            if decoded.get("schema") == (
                ORACLE_SCHEMA + "-two-reference-baseline"
            ):
                result = validate_baseline_result(
                    decoded,
                    oracle,
                    matrix,
                )
            elif decoded.get("schema") == ORACLE_SCHEMA + "-failure":
                structured_failure = validate_oracle_failure(decoded)
                failures.append(
                    "the frozen baseline reported: "
                    + structured_failure["error"]
                )
            else:
                raise RecorderError(
                    "an unrecognized genuine reference schema was emitted"
                )
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append(
                "invalid complete baseline observation: " + str(error)
            )
    if result is None:
        failures.append(
            "agreement on all 5,120 reference cases remains unknown"
        )
    if raw_stderr:
        failures.append(
            "the genuine reference controller emitted complete stderr"
        )
    expected_exit = 0 if result is not None and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        failures.append(
            "the isolated reference controller crashed or returned a wrong exit"
        )
    if post_run_error is not None:
        failures.append(
            "post-run frozen source authentication failed: "
            + post_run_error
        )
    if before != after:
        failures.append(
            "a frozen original source changed during baseline observation"
        )
    first = result.get("reference_a") if result is not None else None
    second = result.get("reference_b") if result is not None else None
    actual_references: int | str = (
        2 if result is not None
        else "UNKNOWN" if process.get("started") is True
        else 0
    )
    document = {
        "schema": SCHEMA + "-complete-baseline-report",
        "status": "FAIL" if failures else "PASS",
        **baseline_source_fields(recorder_pin, label),
        "source_closure_before": dict(before),
        "source_closure_after": (
            dict(after) if after is not None else None
        ),
        "source_closure_unchanged": before == after,
        "complete_baseline_process_stdout": stdout,
        "complete_baseline_process_stderr": stderr,
        "complete_process_representation": (
            "single-canonical-controller-stream"
        ),
        "baseline_result_reconstruction": (
            "decode-and-validate-complete-baseline-process-stdout"
        ),
        "baseline_result_sha256": (
            digest(result) if result is not None else None
        ),
        "baseline_failure_schema": (
            structured_failure.get("schema")
            if structured_failure is not None else None
        ),
        "validated_reference_a_case_count": (
            len(first["records"]) if first is not None else None
        ),
        "validated_reference_b_case_count": (
            len(second["records"]) if second is not None else None
        ),
        "baseline_records_sha256": (
            result["baseline_records_sha256"]
            if result is not None else None
        ),
        "baseline_reference_pids": (
            [first["pid"], second["pid"]]
            if result is not None else None
        ),
        "actual_reference_workers": actual_references,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": int(
            process.get("started") is True
        ),
        "actual_baseline_controller_pid": process.get("pid"),
        "actual_baseline_process_returncode": process.get("returncode"),
        "actual_baseline_process_signal": process.get("signal"),
        "actual_baseline_process_timed_out": (
            process.get("timed_out") is True
        ),
        "actual_baseline_process_spawn_error": (
            process.get("spawn_error")
        ),
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    validate_compact_report_document(document)
    return document



def make_baseline_receipt(
    recorder_pin: str, label: str, report: Mapping[str, Any],
    publication: Mapping[str, Any], preflight: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-durable-baseline-publication-receipt",
        "status": "PASS", "baseline_result_status": report["status"],
        **baseline_source_fields(recorder_pin, label),
        "baseline_records_sha256": report["baseline_records_sha256"],
        "validated_reference_a_case_count": (
            report["validated_reference_a_case_count"]
        ),
        "validated_reference_b_case_count": (
            report["validated_reference_b_case_count"]
        ),
        "baseline_reference_pids": report["baseline_reference_pids"],
        "actual_reference_workers": report["actual_reference_workers"],
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": (
            report["actual_baseline_controller_invocations"]
        ),
        "source_closure_before": report["source_closure_before"],
        "source_closure_after": report["source_closure_after"],
        "source_closure_unchanged": report["source_closure_unchanged"],
        "report_relative": publication["path"],
        "report_sha256": publication["sha256"],
        "report_bytes": publication["bytes"],
        "report_uncompressed_sha256": publication["uncompressed_sha256"],
        "report_uncompressed_bytes": publication["uncompressed_bytes"],
        "report_compression": publication["compression"],
        "report_file_fsync_completed": publication["file_fsync_completed"],
        "report_directory_fsync_completed": (
            publication["directory_fsync_completed"]
        ),
        "report_atomic_no_overwrite_link": publication["atomic_no_overwrite_link"],
        "report_complete_readback_verified": (
            publication["complete_readback_verified"]
        ),
        "receipt_relative": preflight["receipt_relative"],
        "approved_fresh_path_count": preflight["approved_fresh_path_count"],
        "fresh_paths_checked_before_baseline": (
            preflight["fresh_paths_checked_before_observation"]
        ),
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def record_baseline(
    recorder_pin: str,
    oracle_pin: str,
    matrix_pin: str,
    label: str,
) -> dict[str, Any]:
    verify_runtime()
    validate_digest(
        recorder_pin,
        "explicitly frozen compact substitution recorder",
    )
    require(
        validate_digest(
            oracle_pin,
            "frozen substitution oracle",
        ) == ORACLE_SHA256
        and validate_digest(
            matrix_pin,
            "frozen substitution matrix",
        ) == MATRIX_SHA256,
        "pin the exact independently frozen substitution oracle and matrix",
    )
    oracle, _, _, matrix, before = authenticate_frozen_tools(
        recorder_pin,
    )
    process: dict[str, Any] | None = None
    report: dict[str, Any] | None = None
    report_publication: dict[str, Any] | None = None
    receipt_publication: dict[str, Any] | None = None
    try:
        with preflight_fresh_outputs(
            "baseline",
            label,
        ) as preflight:
            arguments = [
                PINNED_PYTHON,
                "-I",
                "-B",
                ROOT + "/" + ORACLE_RELATIVE,
                "--baseline",
                "--oracle-source-sha256",
                ORACLE_SHA256,
                "--matrix-sha256",
                MATRIX_SHA256,
            ]
            process = run_one_process(arguments)
            verify_retained_directory(preflight)
            after: dict[str, Any] | None = None
            post_error: str | None = None
            try:
                after = authenticate_frozen_tools(
                    recorder_pin,
                )[4]
            except (OSError, RecorderError) as error:
                post_error = str(error)
            report = build_baseline_report(
                recorder_pin,
                label,
                process,
                oracle,
                matrix,
                before,
                after,
                post_run_error=post_error,
            )
            report_publication = publish_document(
                preflight,
                report,
                compressed=True,
            )
            receipt = make_baseline_receipt(
                recorder_pin,
                label,
                report,
                report_publication,
                preflight,
            )
            receipt_publication = publish_document(
                preflight,
                receipt,
                compressed=False,
            )
            verify_runtime()
            require(
                report is not None
                and report_publication is not None
                and receipt_publication is not None,
                "a compact baseline publication concealed its complete evidence",
            )
    except (
        RecorderError, OSError, ValueError, TypeError,
        KeyError, EOFError, gzip.BadGzipFile,
    ) as error:
        if process is not None and process.get("started") is True:
            raise ObservationFailure(
                "post-invocation standard baseline failure: " + str(error),
                mode="baseline",
                process=process,
                report=report,
                report_publication=report_publication,
                receipt_publication=receipt_publication,
            ) from error
        raise
    return {
        "schema": SCHEMA + "-recorded-baseline",
        "status": report["status"],
        "publication_status": "PASS",
        **baseline_source_fields(recorder_pin, label),
        "baseline_records_sha256": report["baseline_records_sha256"],
        "validated_reference_a_case_count": (
            report["validated_reference_a_case_count"]
        ),
        "validated_reference_b_case_count": (
            report["validated_reference_b_case_count"]
        ),
        "baseline_reference_pids": report["baseline_reference_pids"],
        "actual_reference_workers": report["actual_reference_workers"],
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": (
            report["actual_baseline_controller_invocations"]
        ),
        "report_publication": report_publication,
        "receipt_publication": receipt_publication,
        "all_failure_reasons": report["all_failure_reasons"],
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }



def validate_baseline_receipt(
    value: Any, pins: OwnerPins,
) -> dict[str, Any]:
    baseline = pins.baseline
    report_relative, receipt_relative = approved_paths(
        "baseline", baseline.label,
    )
    expected = {
        "schema": SCHEMA + "-durable-baseline-publication-receipt",
        "status": "PASS", "baseline_result_status": "PASS",
        **baseline_source_fields(pins.recorder, baseline.label),
        "baseline_records_sha256": baseline.records,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "source_closure_unchanged": True,
        "report_relative": report_relative,
        "report_sha256": baseline.archive,
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_relative,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_baseline": True,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    extras = {
        "baseline_reference_pids", "source_closure_before",
        "source_closure_after", "report_bytes",
        "report_uncompressed_sha256", "report_uncompressed_bytes",
    }
    require(type(value) is dict and set(value) == set(expected) | extras,
            "the complete prior two-reference baseline receipt was forged")
    for field, original in expected.items():
        require(value.get(field) == original,
                "the frozen prior reference receipt changed: " + field)
    pids = value["baseline_reference_pids"]
    require(type(pids) is list and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1],
            "the two independent frozen reference PIDs were forged")
    require(type(value["report_bytes"]) is int
            and 0 < value["report_bytes"] <= MAX_ARCHIVE_BYTES
            and type(value["report_uncompressed_bytes"]) is int
            and 0 < value["report_uncompressed_bytes"]
            <= MAX_COMPACT_REPORT_BYTES,
            "the complete lossless baseline archive bounds were forged")
    validate_digest(value["report_uncompressed_sha256"],
                    "lossless uncompressed baseline")
    require(value["source_closure_before"] == value["source_closure_after"],
            "a frozen baseline tool owner changed during observation")
    validate_frozen_source_owners(
        value["source_closure_before"],
        pins.recorder,
    )
    validate_frozen_source_owners(
        value["source_closure_after"],
        pins.recorder,
    )
    return value


def authenticate_baseline_receipt(
    pins: OwnerPins,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _, receipt_relative = approved_paths("baseline", pins.baseline.label)
    owner, raw = read_owned_regular(
        receipt_relative, pins.baseline.receipt,
        MAX_SOURCE_BYTES, retain=True,
    )
    require(raw is not None, "retain the complete pinned baseline receipt")
    value = validate_baseline_receipt(
        decode_document(raw, "published baseline receipt"), pins,
    )
    return value, owner


def validate_archived_baseline(
    value: Any,
    pins: OwnerPins,
    oracle: Any,
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        type(value) is dict
        and value.get("schema") == SCHEMA + "-complete-baseline-report"
        and value.get("status") == "PASS",
        "the signed two-reference substitution baseline did not pass",
    )
    require(
        len(canonical(value)) == receipt["report_uncompressed_bytes"]
        and digest(value) == receipt["report_uncompressed_sha256"],
        "the complete compact baseline differs from its signed receipt",
    )
    for field, expected in baseline_source_fields(
        pins.recorder,
        pins.baseline.label,
    ).items():
        require(
            value.get(field) == expected
            and type(value.get(field)) is type(expected),
            "the lossless baseline changed a frozen source field: " + field,
        )
    require(
        value.get("source_closure_unchanged") is True
        and value.get("source_closure_before")
        == value.get("source_closure_after")
        == receipt["source_closure_before"]
        and value.get("complete_process_representation")
        == "single-canonical-controller-stream"
        and value.get("baseline_result_reconstruction")
        == "decode-and-validate-complete-baseline-process-stdout"
        and value.get("validated_reference_a_case_count") == CASE_COUNT
        and value.get("validated_reference_b_case_count") == CASE_COUNT
        and value.get("baseline_records_sha256") == pins.baseline.records
        and value.get("baseline_reference_pids")
        == receipt["baseline_reference_pids"]
        and value.get("actual_reference_workers") == 2
        and value.get("actual_candidate_workers") == 0
        and value.get("actual_candidate_imports") == 0
        and value.get("actual_baseline_controller_invocations") == 1
        and value.get("all_failure_reasons") == []
        and value.get("failure_count") == 0
        and value.get("clock_samples") == 0
        and value.get("timing_trials_run") == 0
        and value.get("benchmark_files_read") == 0
        and value.get("hidden_cases_read") == 0
        and value.get("performance") == "NOT MEASURED"
        and value.get("candidate_qualified_for_hidden_benchmark") is False
        and value.get("final_winner_selected") is False,
        "the complete published baseline was changed or did not pass",
    )
    validate_compact_report_document(value)
    raw_stdout = decode_stream(
        value["complete_baseline_process_stdout"],
        "published complete genuine baseline controller stdout",
    )
    require(
        decode_stream(
            value["complete_baseline_process_stderr"],
            "published complete genuine baseline controller stderr",
        ) == b"",
        "the signed successful reference emitted concealed stderr",
    )
    result = validate_baseline_result(
        decode_document(raw_stdout, "published canonical baseline controller"),
        oracle,
        matrix,
    )
    require(
        digest(result) == value.get("baseline_result_sha256")
        and result["baseline_records_sha256"] == pins.baseline.records
        and [
            result["reference_a"]["pid"],
            result["reference_b"]["pid"],
        ] == value["baseline_reference_pids"],
        "the losslessly reconstructed complete reference pair was substituted",
    )
    return {
        **value,
        "complete_baseline_result": result,
        "reference_a_records": result["reference_a"]["records"],
        "reference_b_records": result["reference_b"]["records"],
        "reference_a_process": result["reference_a_process"],
        "reference_b_process": result["reference_b_process"],
    }


def revalidate_derived_baseline(
    value: Any,
    pins: OwnerPins,
    oracle: Any,
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    derived_fields = frozenset({
        "complete_baseline_result",
        "reference_a_records",
        "reference_b_records",
        "reference_a_process",
        "reference_b_process",
    })
    require(
        type(value) is dict and derived_fields <= set(value),
        "retain every in-memory reference derived from the signed baseline",
    )
    compact = {
        field: original
        for field, original in value.items()
        if field not in derived_fields
    }
    validated = validate_archived_baseline(
        compact,
        pins,
        oracle,
        matrix,
        receipt,
    )
    for field in derived_fields:
        require(
            type(value[field]) is type(validated[field])
            and value[field] == validated[field],
            "an in-memory derived reference differs from its signed "
            "canonical baseline: " + field,
        )
    return validated



def stream_baseline_archive(
    pins: OwnerPins, oracle: Any, matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    archive_relative, _ = approved_paths("baseline", pins.baseline.label)
    archive_owner, _ = read_owned_regular(
        archive_relative, pins.baseline.archive, MAX_ARCHIVE_BYTES,
    )
    require(archive_owner["bytes"] == receipt["report_bytes"],
            "the exact published baseline gzip size changed")
    with open_owned_descriptor(archive_relative) as (descriptor, original):
        require((original.st_dev, original.st_ino)
                == (archive_owner["device"], archive_owner["inode"]),
                "the lossless baseline gzip inode changed")
        plain_hasher = hashlib.sha256()
        pieces: list[bytes] = []
        plain_bytes = 0
        try:
            with io.FileIO(descriptor, "rb", closefd=False) as source:
                with gzip.GzipFile(fileobj=source, mode="rb") as compressed:
                    while True:
                        block = compressed.read(131_072)
                        require(type(block) is bytes,
                                "lossless baseline gzip returned invalid bytes")
                        if not block:
                            break
                        plain_bytes += len(block)
                        require(plain_bytes <= MAX_COMPACT_REPORT_BYTES,
                                "lossless baseline exceeded its exact safe bound")
                        plain_hasher.update(block)
                        pieces.append(block)
        except (OSError, EOFError, gzip.BadGzipFile) as error:
            raise RecorderError(
                "the authenticated substitution baseline gzip is not lossless"
            ) from error
    require(plain_bytes == receipt["report_uncompressed_bytes"]
            and plain_hasher.hexdigest()
            == receipt["report_uncompressed_sha256"],
            "the signed complete substitution baseline was truncated or substituted")
    report = decode_document(b"".join(pieces), "complete frozen baseline")
    return (
        validate_archived_baseline(report, pins, oracle, matrix, receipt),
        archive_owner,
    )


def make_audit_manifest(pins: OwnerPins, audit: Any) -> dict[str, Any]:
    spec = family_spec(pins.family)
    native = {spec.engine_relative: pins.engine}
    if spec.bridge_relative != spec.engine_relative:
        native[spec.bridge_relative] = pins.bridge
    try:
        manifest = audit.validate_family_pins(
            spec.name, pins.adapter, pins.engine, pins.bridge,
            [path + "=" + source for path, source in pins.owned_sources],
            [path + "=" + source for path, source in native.items()],
        )
        audit.validate_manifest(manifest, spec.name)
    except Exception as error:
        raise RecorderError(
            "the frozen V3 from-scratch ownership policy rejected this family"
        ) from error
    return manifest


def native_pins(pins: OwnerPins) -> dict[str, str]:
    family_spec(pins.family)
    return {
        "source": validate_digest(pins.adapter, "owned Python adapter"),
        "native_engine": validate_digest(pins.engine, "owned native engine"),
        "native_bridge": validate_digest(pins.bridge, "owned native bridge"),
    }


def authenticate_family_closure(
    pins: OwnerPins, v5: Any, audit: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    spec = family_spec(pins.family)
    frozen = v5.family_spec(spec.name)
    require(frozen.adapter_module == spec.adapter_module
            and frozen.adapter_relative == spec.adapter_relative
            and frozen.engine_relative == spec.engine_relative
            and frozen.bridge_module == spec.bridge_module
            and frozen.bridge_relative == spec.bridge_relative
            and frozen.owned_ctypes is spec.owned_ctypes
            and v5.validate_pins(native_pins(pins), frozen)
            == native_pins(pins),
            "the exact frozen V5 family and native alias policy changed")
    manifest = make_audit_manifest(pins, audit)
    try:
        full = audit.authenticate_closure(spec.name, manifest, AUDIT_SHA256)
        serializable = audit.serializable_owners(full)
        audit.validate_serializable_owners(
            serializable, spec.name, manifest, AUDIT_SHA256,
        )
    except Exception as error:
        raise RecorderError(
            "the frozen V3 audit rejected an owned source or native closure"
        ) from error
    return serializable, manifest


def validate_guard(value: Any, spec: FamilySpec) -> dict[str, Any]:
    require(type(value) is dict, "a continuous V5 ownership guard is mandatory")
    for name in GUARD_TRUE_FIELDS:
        require(value.get(name) is True,
                "a native no-delegation guard was omitted: " + name)
    require(value.get("public_type_names_used_for_ownership") is False,
            "an independently owned compatible public type was misclassified")
    for name in ("actual_method_guard_checks",
                 "actual_warning_registry_guard_checks"):
        require(type(value.get(name)) is int
                and value[name] == 2 * CASE_COUNT,
                "a before-and-after ownership or warning guard was omitted")
    require(value.get("owned_native_ffi_allowed") is spec.owned_ctypes,
            "the independently owned Zig-only FFI policy changed")
    for name in (
        "trusted_stdlib_ctypes_preloaded",
        "trusted_stdlib_ctypes_builtin_verified",
        "trusted_stdlib_ctypes_pythonapi_initialized",
    ):
        require(value.get(name) is spec.owned_ctypes,
                "the frozen genuine native FFI policy changed: " + name)
    require(value.get("trusted_stdlib_ctypes_source_sha256")
            == (TRUSTED_CTYPES_SHA256 if spec.owned_ctypes else None),
            "the genuinely owned Zig-only standard FFI was substituted")
    for name in GUARD_COUNTER_FIELDS:
        require(type(value.get(name)) is int and value[name] >= 0,
                "a genuine continuous native guard counter was concealed")
    if spec.owned_ctypes:
        require(value["owned_ctypes_load_count"] >= 1
                and value["owned_ctypes_symbol_count"] >= 1,
                "the independently owned Zig engine and symbols never loaded")
    else:
        require(value["owned_ctypes_load_count"] == 0
                and value["owned_ctypes_symbol_count"] == 0,
                "an unowned external native engine was dynamically loaded")
    return value


def snapshot_guard(active: Mapping[str, Any], spec: FamilySpec) -> dict[str, Any]:
    result = {name: active.get(name) for name in GUARD_TRUE_FIELDS}
    result.update({
        "public_type_names_used_for_ownership": (
            active.get("public_type_names_used_for_ownership")
        ),
        "actual_method_guard_checks": active.get("actual_method_guard_checks"),
        "actual_warning_registry_guard_checks": (
            active.get("actual_warning_registry_guard_checks")
        ),
        "owned_native_ffi_allowed": active.get("owned_native_ffi_allowed"),
        "trusted_stdlib_ctypes_preloaded": (
            active.get("trusted_stdlib_ctypes_preloaded")
        ),
        "trusted_stdlib_ctypes_builtin_verified": (
            active.get("trusted_stdlib_ctypes_builtin_verified")
        ),
        "trusted_stdlib_ctypes_pythonapi_initialized": (
            active.get("trusted_stdlib_ctypes_pythonapi_initialized")
        ),
        "trusted_stdlib_ctypes_source_sha256": (
            active.get("trusted_stdlib_ctypes_source_sha256")
        ),
    })
    result.update({name: active.get(name) for name in GUARD_COUNTER_FIELDS})
    return validate_guard(result, spec)


def validate_local_callback_match(value: Any) -> dict[str, Any]:
    fields = {
        "pattern_is_expected", "string_is_subject", "string", "group",
        "groups", "groupdict", "regs", "lastindex", "lastgroup",
        "pos", "endpos",
    }
    require(
        type(value) is dict and set(value) == fields
        and value.get("pattern_is_expected") is True
        and value.get("string_is_subject") is True
        and all(
            type(value.get(name)) is dict
            for name in fields - {"pattern_is_expected", "string_is_subject"}
        ),
        "a replacement callback borrowed or concealed its native Match",
    )
    canonical(value)
    return value


def validate_substitution_events(
    events: Any,
    *,
    require_balanced: bool = False,
    expected_acquisition_flags: tuple[int, ...] | None = None,
) -> list[dict[str, Any]]:
    require(
        type(events) is list,
        "a complete ordered PEP-688 substitution ledger is mandatory",
    )
    active = {"subject": 0, "replacement": 0}
    ownership_stack: list[str] = []
    acquisition_flags: list[int] = []
    for record in events:
        require(
            type(record) is dict and type(record.get("event")) is str,
            "a genuine acquisition, callback, hash, or release was concealed",
        )
        kind = record["event"]
        if kind == "phase":
            require(
                set(record) == {"event", "name"}
                and type(record.get("name")) is str
                and bool(record["name"]),
                "a real substitution operation phase was forged",
            )
            continue
        if kind == "callback":
            require(
                set(record) == {"event", "index", "match", "raises"}
                and type(record.get("index")) is int
                and record["index"] >= 0
                and type(record.get("raises")) is bool,
                "an ordered replacement callback or exception was concealed",
            )
            validate_local_callback_match(record["match"])
            continue
        required = {
            "event", "role", "flags", "active_before", "active_after",
            "backing_before_hex", "backing_after_hex", "behavior",
        }
        actual_keys = required | ({"hash_result"} if kind == "hash" else set())
        require(
            kind in {
                "acquire", "acquire-error", "release", "hash", "hash-error",
            }
            and set(record) == actual_keys
            and record.get("role") in active
            and type(record.get("active_before")) is int
            and type(record.get("active_after")) is int
            and record["active_before"] >= 0
            and record["active_after"] >= 0
            and type(record.get("backing_before_hex")) is str
            and type(record.get("backing_after_hex")) is str
            and record.get("behavior") in {"stable", "mutate", "fail"},
            "a genuine nested owner, buffer flag, backing, or hash was forged",
        )
        for field in ("backing_before_hex", "backing_after_hex"):
            try:
                original = bytes.fromhex(record[field])
            except ValueError as error:
                raise RecorderError(
                    "a genuine PEP-688 buffer event contains invalid hex"
                ) from error
            require(
                original.hex() == record[field],
                "a genuine substitution backing is not canonical hex",
            )
        role = record["role"]
        require(
            record["active_before"] == active[role],
            "a real nested PEP-688 acquisition was reordered",
        )
        if kind == "acquire":
            require(
                type(record["flags"]) is int
                and record["flags"] in {
                    SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG,
                }
                and record["behavior"] != "fail"
                and record["active_after"] == active[role] + 1
                and record["backing_after_hex"]
                == record["backing_before_hex"],
                "a real SIMPLE or FULL-READONLY acquisition was forged",
            )
            ownership_stack.append(role)
            acquisition_flags.append(record["flags"])
            active[role] += 1
        elif kind == "acquire-error":
            require(
                type(record["flags"]) is int
                and record["flags"] in {
                    SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG,
                }
                and record["behavior"] == "fail"
                and record["active_after"] == active[role]
                and record["backing_after_hex"]
                == record["backing_before_hex"],
                "a genuine failing buffer export was concealed",
            )
        elif kind == "release":
            require(
                record["flags"] is None
                and active[role] > 0
                and record["active_after"] == active[role] - 1
                and bool(ownership_stack)
                and ownership_stack[-1] == role,
                "a real nested buffer release was leaked or reordered",
            )
            if record["behavior"] == "mutate":
                original = bytes.fromhex(record["backing_before_hex"])
                require(
                    record["backing_after_hex"]
                    == (b"!" * len(original)).hex(),
                    "an on-release exporter mutation was concealed",
                )
            else:
                require(
                    record["backing_after_hex"]
                    == record["backing_before_hex"],
                    "a stable exporter silently mutated its backing",
                )
            ownership_stack.pop()
            active[role] -= 1
        elif kind == "hash":
            require(
                record["flags"] is None
                and record["active_after"] == active[role]
                and type(record.get("hash_result")) is int
                and record["hash_result"] == 1729,
                "a genuine deterministic replacement hash was forged",
            )
        else:
            require(
                record["flags"] is None
                and record["active_after"] == active[role],
                "a genuine custom replacement-hash failure was concealed",
            )
    require(
        type(require_balanced) is bool,
        "an exact buffer acquisition-balance policy is mandatory",
    )
    if expected_acquisition_flags is not None:
        require(
            type(expected_acquisition_flags) is tuple
            and all(type(flag) is int for flag in expected_acquisition_flags)
            and tuple(acquisition_flags) == expected_acquisition_flags,
            "the actual nested SIMPLE, SIMPLE, FULL-READONLY order changed",
        )
    if require_balanced:
        require(
            all(count == 0 for count in active.values())
            and not ownership_stack,
            "a genuine nested exporter acquisition or release was omitted",
        )
    return events


def validate_candidate_outcome(
    value: Any, oracle: Any | None = None,
) -> dict[str, Any]:
    fields = {
        "status", "stage", "value", "exception", "events", "callbacks",
        "warnings", "subject_after", "replacement_after",
        "subject_active_exports", "replacement_active_exports",
        "count_requested", "pos_requested", "endpos_requested",
    }
    require(
        type(value) is dict
        and set(value) == fields
        and value.get("status") in {"return", "raise"}
        and type(value.get("stage")) is str
        and type(value.get("events")) is list
        and type(value.get("callbacks")) is list
        and type(value.get("warnings")) is list
        and type(value.get("subject_active_exports")) is int
        and value["subject_active_exports"] >= 0
        and type(value.get("replacement_active_exports")) is int
        and value["replacement_active_exports"] >= 0
        and type(value.get("count_requested")) is int
        and type(value.get("pos_requested")) is int
        and (
            value.get("endpos_requested") is None
            or type(value["endpos_requested"]) is int
        ),
        "a complete substitution result, exception, callback, buffer event, "
        "or window was concealed",
    )
    require(
        type(value["subject_after"]) is dict
        and type(value["replacement_after"]) is dict,
        "the exact final subject and replacement storage were concealed",
    )
    validate_substitution_events(value["events"])
    for role, field in (
        ("subject", "subject_active_exports"),
        ("replacement", "replacement_active_exports"),
    ):
        acquisitions = sum(
            event.get("event") == "acquire"
            and event.get("role") == role
            for event in value["events"]
        )
        releases = sum(
            event.get("event") == "release"
            and event.get("role") == role
            for event in value["events"]
        )
        require(
            value[field] == acquisitions - releases,
            "a real nested exporter was leaked or concealed: " + role,
        )
    if value["status"] == "return":
        require(
            value["exception"] is None and type(value["value"]) is dict,
            "a successful substitution concealed a value or exception",
        )
    else:
        require(
            value["value"] is None and type(value["exception"]) is dict,
            "a failing substitution concealed its exact Python exception",
        )
    require(
        [
            event for event in value["events"]
            if event.get("event") == "callback"
        ] == value["callbacks"],
        "a replacement callback was removed from its buffer-event position",
    )
    for event in value["callbacks"]:
        validate_local_callback_match(event["match"])
    for warning in value["warnings"]:
        require(
            type(warning) is dict
            and set(warning) == {"category_module", "category", "message"}
            and all(type(warning.get(name)) is str for name in warning),
            "a genuine original replacement warning was omitted",
        )
    if oracle is not None:
        try:
            oracle.validate_outcome(value)
        except Exception as error:
            raise RecorderError(
                "the frozen oracle rejected a complete substitution outcome"
            ) from error
    canonical(value)
    return value



def validate_candidate_records(
    matrix: list[dict[str, Any]], records: Any, expected: Any,
    oracle: Any | None = None,
) -> list[dict[str, Any]]:
    validate_digest(expected, "all source-ordered substitution outcomes")
    require(
        type(records) is list and len(records) == CASE_COUNT,
        "all 5,120 actual source-ordered substitution outcomes are mandatory",
    )
    for case, record in zip(matrix, records, strict=True):
        require(
            type(record) is dict
            and set(record) == {"case", "cohort", "api", "outcome"}
            and record.get("case") == case["case"]
            and record.get("cohort") == case["cohort"]
            and record.get("api") == case["api"],
            "a genuine substitution case, cohort, or API was concealed",
        )
        validate_candidate_outcome(record["outcome"], oracle)
    require(
        digest(records) == expected,
        "a complete native substitution observation vector changed",
    )
    if oracle is not None:
        try:
            oracle.validate_records(matrix, records, expected)
        except Exception as error:
            raise RecorderError(
                "the frozen substitution oracle rejected complete candidate records"
            ) from error
    return records


def observe_candidate_case(
    case: Mapping[str, Any], candidate: Any, oracle: Any,
) -> dict[str, Any]:
    try:
        outcome = oracle.execute_case(case, candidate)
    except Exception as error:
        raise RecorderError(
            "the frozen substitution oracle could not retain an exact "
            "candidate outcome: " + str(error)
        ) from error
    return validate_candidate_outcome(outcome, oracle)



def validate_native_provenance(
    value: Any, pins: OwnerPins,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    require(type(value) is dict
            and set(value) == {"source", "native_engine", "native_bridge"},
            "the complete genuinely guarded native provenance is mandatory")
    for name, relative, expected in (
        ("source", spec.adapter_relative, pins.adapter),
        ("native_engine", spec.engine_relative, pins.engine),
        ("native_bridge", spec.bridge_relative, pins.bridge),
    ):
        validate_owner(value.get(name), relative, expected)
    require((value["native_engine"] == value["native_bridge"])
            is (spec.name == "c"),
            "an independently owned engine or native bridge was aliased")
    return value


def execute_candidate_worker(pins: OwnerPins) -> dict[str, Any]:
    verify_runtime()
    spec = family_spec(pins.family)
    oracle, v5, audit, matrix, sources = authenticate_frozen_tools(
        pins.recorder,
    )
    receipt, receipt_owner = authenticate_baseline_receipt(pins)
    reference, archive_owner = stream_baseline_archive(
        pins, oracle, matrix, receipt,
    )
    before, manifest = authenticate_family_closure(pins, v5, audit)
    warning, identity, _, _ = v5.load_frozen_oracles()
    original = importlib.import_module("re")
    require(
        type(original) is types.ModuleType and original.__name__ == "re",
        "the genuine original CPython matcher guard was substituted",
    )
    selected = v5.family_spec(spec.name)
    records: list[dict[str, Any]] = []
    guard: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    with warning.installed_warning_safe_guard(identity):
        with v5.chosen_original_guard(
            original, native_pins(pins), selected, identity, warning,
        ) as active:
            candidate = active.get("candidate")
            require(
                type(candidate) is types.ModuleType
                and candidate.__name__ == spec.adapter_module,
                "a sibling, standard, or external substitution engine escaped",
            )
            require(
                active.get("actual_method_guard_checks") == 0
                and active.get("actual_warning_registry_guard_checks") == 0,
                "continuous native ownership guards did not start at zero",
            )
            for row in matrix:
                active["verify"]()
                active["actual_method_guard_checks"] += 1
                try:
                    outcome = observe_candidate_case(row, candidate, oracle)
                finally:
                    active["verify"]()
                    active["actual_method_guard_checks"] += 1
                records.append({
                    "case": row["case"],
                    "cohort": row["cohort"],
                    "api": row["api"],
                    "outcome": outcome,
                })
            guard = snapshot_guard(active, spec)
            actual = active.get("native_provenance")
            require(
                v5.validate_owners(actual, selected, native_pins(pins)),
                "the continuously guarded native substitution engine changed",
            )
            provenance = validate_native_provenance(actual, pins)
    require(
        guard is not None and provenance is not None,
        "complete continuously guarded substitution ownership is mandatory",
    )
    records_sha256 = digest(records)
    validate_candidate_records(matrix, records, records_sha256, oracle)
    after, final_manifest = authenticate_family_closure(pins, v5, audit)
    require(
        before == after and manifest == final_manifest,
        "an independently owned source or native engine changed",
    )
    return {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "role": "candidate-" + spec.name,
        "pid": os.getpid(),
        "candidate_family": spec.name,
        **baseline_source_fields(pins.recorder, pins.baseline.label),
        "baseline_receipt_relative": approved_paths(
            "baseline", pins.baseline.label,
        )[1],
        "baseline_receipt_sha256": pins.baseline.receipt,
        "baseline_archive_relative": approved_paths(
            "baseline", pins.baseline.label,
        )[0],
        "baseline_archive_sha256": pins.baseline.archive,
        "baseline_records_sha256": pins.baseline.records,
        "baseline_reference_pids": receipt["baseline_reference_pids"],
        "baseline_receipt_owner": receipt_owner,
        "baseline_archive_owner": archive_owner,
        "source_provenance": sources,
        "audit_manifest": manifest,
        "owned_source_closure": after,
        "native_provenance": provenance,
        "matcher_guard": guard,
        "records_sha256": records_sha256,
        "records": records,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": sum(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }



def validate_candidate_worker(
    value: Any, pins: OwnerPins, matrix: list[dict[str, Any]],
    *, expected_pid: int, oracle: Any, audit: Any,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    require(
        type(expected_pid) is int and expected_pid > 0,
        "an independently isolated substitution worker PID is mandatory",
    )
    expected = {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "role": "candidate-" + spec.name,
        "pid": expected_pid,
        "candidate_family": spec.name,
        **baseline_source_fields(pins.recorder, pins.baseline.label),
        "baseline_receipt_relative": approved_paths(
            "baseline", pins.baseline.label,
        )[1],
        "baseline_receipt_sha256": pins.baseline.receipt,
        "baseline_archive_relative": approved_paths(
            "baseline", pins.baseline.label,
        )[0],
        "baseline_archive_sha256": pins.baseline.archive,
        "baseline_records_sha256": pins.baseline.records,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    additional = {
        "baseline_reference_pids",
        "baseline_receipt_owner",
        "baseline_archive_owner",
        "source_provenance",
        "audit_manifest",
        "owned_source_closure",
        "native_provenance",
        "matcher_guard",
        "records_sha256",
        "records",
        "actual_candidate_imports",
    }
    require(
        type(value) is dict and set(value) == set(expected) | additional,
        "a complete guarded substitution worker was forged",
    )
    for field, original in expected.items():
        require(
            value.get(field) == original
            and type(value.get(field)) is type(original),
            "a frozen isolated substitution observation changed: " + field,
        )
    pids = value["baseline_reference_pids"]
    require(
        type(pids) is list and len(pids) == 2
        and all(type(item) is int and item > 0 for item in pids)
        and pids[0] != pids[1] and expected_pid not in pids,
        "a native worker was aliased to an independent reference process",
    )
    require(
        type(value["actual_candidate_imports"]) is int
        and value["actual_candidate_imports"] >= 2,
        "a genuinely owned native adapter or bridge was not imported",
    )
    validate_owner(
        value["baseline_receipt_owner"],
        approved_paths("baseline", pins.baseline.label)[1],
        pins.baseline.receipt,
    )
    validate_owner(
        value["baseline_archive_owner"],
        approved_paths("baseline", pins.baseline.label)[0],
        pins.baseline.archive,
    )
    validate_frozen_source_owners(
        value["source_provenance"],
        pins.recorder,
    )
    manifest = make_audit_manifest(pins, audit)
    require(
        value["audit_manifest"] == manifest,
        "the complete V3 native ownership manifest was substituted",
    )
    try:
        audit.validate_serializable_owners(
            value["owned_source_closure"], spec.name, manifest, AUDIT_SHA256,
        )
    except Exception as error:
        raise RecorderError(
            "the frozen V3 policy rejected a complete native source owner"
        ) from error
    validate_native_provenance(value["native_provenance"], pins)
    validate_guard(value["matcher_guard"], spec)
    validate_candidate_records(
        matrix, value["records"], value["records_sha256"], oracle,
    )
    return value



def run_candidate_process(pins: OwnerPins) -> dict[str, Any]:
    arguments = [
        PINNED_PYTHON, "-I", "-B", SOURCE_ABSOLUTE,
        "--internal-candidate-worker", "--candidate", pins.family,
        "--recorder-source-sha256", pins.recorder,
        "--oracle-source-sha256", ORACLE_SHA256,
        "--matrix-sha256", MATRIX_SHA256,
        "--ownership-audit-source-sha256", AUDIT_SHA256,
        "--baseline-label", pins.baseline.label,
        "--baseline-receipt-sha256", pins.baseline.receipt,
        "--baseline-archive-sha256", pins.baseline.archive,
        "--baseline-records-sha256", pins.baseline.records,
        "--candidate-source-sha256", pins.adapter,
        "--native-engine-sha256", pins.engine,
        "--native-bridge-sha256", pins.bridge,
    ]
    for path, source in pins.owned_sources:
        arguments.extend(("--owned-source-sha256", path + "=" + source))
    return run_one_process(arguments)


def reconstruct_mismatch_evidence(
    matrix: list[dict[str, Any]],
    baseline_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    dict[str, int],
    dict[str, int],
]:
    require(
        type(matrix) is list
        and type(baseline_records) is list
        and type(candidate_records) is list
        and len(matrix) == len(baseline_records)
        == len(candidate_records) == CASE_COUNT,
        "reconstruct every source-ordered frozen comparison case",
    )
    mismatches: list[dict[str, Any]] = []
    by_cohort = {name: 0 for name in COHORTS}
    by_api = {name: 0 for name in APIS}
    for index, (row, original, actual) in enumerate(zip(
        matrix,
        baseline_records,
        candidate_records,
        strict=True,
    )):
        require(
            type(row) is dict
            and type(original) is dict
            and type(actual) is dict
            and row["case"] == original.get("case") == actual.get("case")
            and row["cohort"]
            == original.get("cohort") == actual.get("cohort")
            and row["api"] == original.get("api") == actual.get("api")
            and row["cohort"] in by_cohort
            and row["api"] in by_api,
            "a frozen input, baseline, or candidate vector was reordered",
        )
        if original["outcome"] != actual["outcome"]:
            by_cohort[row["cohort"]] += 1
            by_api[row["api"]] += 1
            mismatches.append({
                "index": index,
                "case": row["case"],
                "cohort": row["cohort"],
                "api": row["api"],
                "baseline_outcome_sha256": digest(
                    original["outcome"],
                ),
                "candidate_outcome_sha256": digest(
                    actual["outcome"],
                ),
            })
    require(
        sum(by_cohort.values())
        == sum(by_api.values())
        == len(mismatches)
        and len(mismatches) <= CASE_COUNT,
        "a complete source-ordered substitution mismatch was omitted",
    )
    return mismatches, by_cohort, by_api


def validate_mismatch_evidence(
    evidence: Any,
    matrix: list[dict[str, Any]],
    baseline_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
    expected_digest: str,
) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int]]:
    validate_digest(expected_digest, "lossless substitution mismatch ledger")
    expected, by_cohort, by_api = reconstruct_mismatch_evidence(
        matrix,
        baseline_records,
        candidate_records,
    )
    require(
        type(evidence) is list
        and evidence == expected
        and digest(evidence) == expected_digest,
        "a source-ordered substitution mismatch was hidden, reordered, "
        "or disconnected from its complete original outcomes",
    )
    return expected, by_cohort, by_api


def build_candidate_report(
    pins: OwnerPins,
    label: str,
    process: Mapping[str, Any],
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
    reference: Mapping[str, Any],
    before: Mapping[str, Any],
    after: Mapping[str, Any] | None,
    oracle: Any,
    audit: Any,
    *,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    validate_label(label)
    validate_matrix(matrix)
    validate_baseline_receipt(receipt, pins)
    restored_reference = revalidate_derived_baseline(
        reference,
        pins,
        oracle,
        matrix,
        receipt,
    )
    raw_stdout = process.get("stdout")
    raw_stderr = process.get("stderr")
    stdout = capture_stream(
        raw_stdout,
        "complete native candidate stdout",
    )
    stderr = capture_stream(
        raw_stderr,
        "complete native candidate stderr",
    )
    failures: list[str] = []
    candidate: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append(
            "the independent substitution candidate could not start: "
            + str(process.get("spawn_error"))
        )
    if process.get("timed_out") is True:
        failures.append(
            "the native substitution candidate exceeded its timeout"
        )
    if raw_stdout:
        try:
            candidate = validate_candidate_worker(
                decode_document(
                    raw_stdout,
                    "complete canonical isolated native candidate",
                ),
                pins,
                matrix,
                expected_pid=process.get("pid"),
                oracle=oracle,
                audit=audit,
            )
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append(
                "invalid complete candidate observation: " + str(error)
            )
    if candidate is None:
        failures.append(
            "all 5,120 genuine candidate outcomes remain unknown"
        )
    if raw_stderr:
        failures.append(
            "the isolated native candidate emitted complete stderr"
        )
    expected_exit = 0 if candidate is not None and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        failures.append(
            "the native substitution candidate crashed "
            "or returned a wrong exit"
        )
    if post_run_error is not None:
        failures.append(
            "post-run native ownership authentication failed: "
            + post_run_error
        )
    if before != after:
        failures.append(
            "the complete independently owned source closure changed"
        )
    mismatches: list[dict[str, Any]] | None = None
    by_cohort: dict[str, int] | None = None
    by_api: dict[str, int] | None = None
    mismatch_hash: str | None = None
    if candidate is not None:
        mismatches, by_cohort, by_api = reconstruct_mismatch_evidence(
            matrix,
            restored_reference["reference_a_records"],
            candidate["records"],
        )
        mismatch_hash = digest(mismatches)
        validate_mismatch_evidence(
            mismatches,
            matrix,
            restored_reference["reference_a_records"],
            candidate["records"],
            mismatch_hash,
        )
        if mismatches:
            failures.append(
                "the independent candidate differs on "
                + str(len(mismatches))
                + " frozen substitution and buffer cases"
            )
    actual_candidates: int | str = (
        1 if candidate is not None
        else "UNKNOWN" if process.get("started") is True
        else 0
    )
    document = {
        "schema": SCHEMA + "-complete-candidate-report",
        "status": "FAIL" if failures else "PASS",
        "python": "3.14.6",
        "label": label,
        "candidate_family": spec.name,
        "candidate_source_sha256": pins.adapter,
        "native_engine_sha256": pins.engine,
        "native_bridge_sha256": pins.bridge,
        "baseline_label": pins.baseline.label,
        "recorder_relative": SOURCE_RELATIVE,
        "recorder_source_sha256": pins.recorder,
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "cohorts": list(COHORTS),
        "apis": list(APIS),
        "simple_buffer_flag": SIMPLE_BUFFER_FLAG,
        "full_readonly_buffer_flag": FULL_READONLY_BUFFER_FLAG,
        **validate_compact_bounds(),
        "baseline_receipt_relative": approved_paths(
            "baseline",
            pins.baseline.label,
        )[1],
        "baseline_receipt_sha256": pins.baseline.receipt,
        "baseline_archive_relative": approved_paths(
            "baseline",
            pins.baseline.label,
        )[0],
        "baseline_archive_sha256": pins.baseline.archive,
        "baseline_records_sha256": pins.baseline.records,
        "baseline_reference_pids": receipt["baseline_reference_pids"],
        "candidate_owner_before": dict(before),
        "candidate_owner_after": (
            dict(after) if after is not None else None
        ),
        "candidate_owner_unchanged": before == after,
        "complete_candidate_process_stdout": stdout,
        "complete_candidate_process_stderr": stderr,
        "complete_process_representation": (
            "single-canonical-candidate-stream"
        ),
        "candidate_records_reconstruction": (
            "decode-and-validate-complete-candidate-process-stdout"
        ),
        "baseline_records_reconstruction": (
            "decode-and-validate-pinned-complete-baseline-archive"
        ),
        "mismatch_outcome_reconstruction": (
            "frozen-matrix-plus-pinned-baseline-plus-candidate-stdout"
        ),
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": (
            len(candidate["records"])
            if candidate is not None else None
        ),
        "candidate_records_sha256": (
            candidate["records_sha256"]
            if candidate is not None else None
        ),
        "mismatch_count": (
            len(mismatches) if mismatches is not None else None
        ),
        "all_mismatches": mismatches,
        "mismatch_evidence_sha256": mismatch_hash,
        "mismatches_by_cohort": by_cohort,
        "mismatches_by_api": by_api,
        "all_mismatches_preserved": (
            True if mismatches is not None else None
        ),
        "actual_method_guard_checks": (
            candidate["matcher_guard"]["actual_method_guard_checks"]
            if candidate is not None else None
        ),
        "actual_warning_registry_guard_checks": (
            candidate["matcher_guard"][
                "actual_warning_registry_guard_checks"
            ]
            if candidate is not None else None
        ),
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": actual_candidates,
        "actual_candidate_imports": (
            candidate["actual_candidate_imports"]
            if candidate is not None else "UNKNOWN"
            if process.get("started") is True else 0
        ),
        "actual_candidate_process_invocations": int(
            process.get("started") is True
        ),
        "actual_candidate_pid": process.get("pid"),
        "actual_candidate_process_returncode": (
            process.get("returncode")
        ),
        "actual_candidate_process_signal": process.get("signal"),
        "actual_candidate_process_timed_out": (
            process.get("timed_out") is True
        ),
        "actual_candidate_process_spawn_error": (
            process.get("spawn_error")
        ),
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    validate_compact_report_document(document)
    return document




def make_candidate_receipt(
    pins: OwnerPins,
    label: str,
    report: Mapping[str, Any],
    publication: Mapping[str, Any],
    preflight: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-durable-candidate-publication-receipt",
        "status": "PASS",
        "candidate_result_status": report["status"],
        "python": "3.14.6",
        "label": label,
        "candidate_family": pins.family,
        "candidate_source_sha256": pins.adapter,
        "native_engine_sha256": pins.engine,
        "native_bridge_sha256": pins.bridge,
        "baseline_label": pins.baseline.label,
        "recorder_source_sha256": pins.recorder,
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "cohorts": list(COHORTS),
        "apis": list(APIS),
        "simple_buffer_flag": SIMPLE_BUFFER_FLAG,
        "full_readonly_buffer_flag": FULL_READONLY_BUFFER_FLAG,
        **validate_compact_bounds(),
        "baseline_receipt_relative": approved_paths(
            "baseline",
            pins.baseline.label,
        )[1],
        "baseline_receipt_sha256": pins.baseline.receipt,
        "baseline_archive_relative": approved_paths(
            "baseline",
            pins.baseline.label,
        )[0],
        "baseline_archive_sha256": pins.baseline.archive,
        "baseline_records_sha256": pins.baseline.records,
        "baseline_reference_pids": report["baseline_reference_pids"],
        "validated_baseline_record_count": (
            report["validated_baseline_record_count"]
        ),
        "validated_candidate_record_count": (
            report["validated_candidate_record_count"]
        ),
        "candidate_records_sha256": report["candidate_records_sha256"],
        "mismatch_count": report["mismatch_count"],
        "mismatch_evidence_sha256": (
            report["mismatch_evidence_sha256"]
        ),
        "mismatches_by_cohort": report["mismatches_by_cohort"],
        "mismatches_by_api": report["mismatches_by_api"],
        "all_mismatches_preserved": report["all_mismatches_preserved"],
        "actual_method_guard_checks": (
            report["actual_method_guard_checks"]
        ),
        "actual_warning_registry_guard_checks": (
            report["actual_warning_registry_guard_checks"]
        ),
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": (
            report["actual_candidate_workers"]
        ),
        "actual_candidate_imports": (
            report["actual_candidate_imports"]
        ),
        "actual_candidate_process_invocations": (
            report["actual_candidate_process_invocations"]
        ),
        "candidate_owner_before": report["candidate_owner_before"],
        "candidate_owner_after": report["candidate_owner_after"],
        "candidate_owner_unchanged": report["candidate_owner_unchanged"],
        "report_relative": publication["path"],
        "report_sha256": publication["sha256"],
        "report_bytes": publication["bytes"],
        "report_uncompressed_sha256": (
            publication["uncompressed_sha256"]
        ),
        "report_uncompressed_bytes": (
            publication["uncompressed_bytes"]
        ),
        "report_compression": publication["compression"],
        "report_file_fsync_completed": (
            publication["file_fsync_completed"]
        ),
        "report_directory_fsync_completed": (
            publication["directory_fsync_completed"]
        ),
        "report_atomic_no_overwrite_link": (
            publication["atomic_no_overwrite_link"]
        ),
        "report_complete_readback_verified": (
            publication["complete_readback_verified"]
        ),
        "receipt_relative": preflight["receipt_relative"],
        "approved_fresh_path_count": (
            preflight["approved_fresh_path_count"]
        ),
        "fresh_paths_checked_before_candidate": (
            preflight["fresh_paths_checked_before_observation"]
        ),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }




def record_candidate(
    pins: OwnerPins,
    label: str,
) -> dict[str, Any]:
    verify_runtime()
    spec = family_spec(pins.family)
    validate_label(label)
    oracle, v5, audit, matrix, _ = authenticate_frozen_tools(
        pins.recorder,
    )
    receipt, _ = authenticate_baseline_receipt(pins)
    reference, _ = stream_baseline_archive(
        pins,
        oracle,
        matrix,
        receipt,
    )
    before, _ = authenticate_family_closure(
        pins,
        v5,
        audit,
    )
    process: dict[str, Any] | None = None
    report: dict[str, Any] | None = None
    publication: dict[str, Any] | None = None
    receipt_publication: dict[str, Any] | None = None
    try:
        with preflight_fresh_outputs(
            "candidate",
            label,
            spec.name,
        ) as preflight:
            process = run_candidate_process(pins)
            verify_retained_directory(preflight)
            after: dict[str, Any] | None = None
            post_error: str | None = None
            try:
                after = authenticate_family_closure(
                    pins,
                    v5,
                    audit,
                )[0]
                authenticate_frozen_tools(pins.recorder)
            except (OSError, RecorderError) as error:
                post_error = str(error)
            report = build_candidate_report(
                pins,
                label,
                process,
                matrix,
                receipt,
                reference,
                before,
                after,
                oracle,
                audit,
                post_run_error=post_error,
            )
            publication = publish_document(
                preflight,
                report,
                compressed=True,
            )
            receipt_document = make_candidate_receipt(
                pins,
                label,
                report,
                publication,
                preflight,
            )
            receipt_publication = publish_document(
                preflight,
                receipt_document,
                compressed=False,
            )
            verify_runtime()
            require(
                report is not None
                and publication is not None
                and receipt_publication is not None,
                "a compact native publication concealed its complete evidence",
            )
    except (
        RecorderError, OSError, ValueError, TypeError,
        KeyError, EOFError, gzip.BadGzipFile,
    ) as error:
        if process is not None and process.get("started") is True:
            raise ObservationFailure(
                "post-invocation native candidate failure: " + str(error),
                mode="candidate",
                process=process,
                report=report,
                report_publication=publication,
                receipt_publication=receipt_publication,
            ) from error
        raise
    return {
        "schema": SCHEMA + "-recorded-candidate",
        "status": report["status"],
        "publication_status": "PASS",
        "python": "3.14.6",
        "candidate_family": spec.name,
        "label": label,
        "recorder_source_sha256": pins.recorder,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_source_sha256": ORACLE_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        **validate_compact_bounds(),
        "baseline_records_sha256": pins.baseline.records,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": (
            report["validated_candidate_record_count"]
        ),
        "mismatch_count": report["mismatch_count"],
        "mismatch_evidence_sha256": (
            report["mismatch_evidence_sha256"]
        ),
        "actual_candidate_process_invocations": (
            report["actual_candidate_process_invocations"]
        ),
        "actual_candidate_workers": (
            report["actual_candidate_workers"]
        ),
        "report_publication": publication,
        "receipt_publication": receipt_publication,
        "all_failure_reasons": report["all_failure_reasons"],
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def capture_failure_stream(
    value: Any,
    label: str,
) -> dict[str, Any]:
    require(
        type(value) is bytes,
        "a genuine post-invocation failure concealed process bytes: " + label,
    )
    if len(value) <= MAX_PROCESS_BYTES:
        return capture_stream(value, label)
    return {
        "base64": None,
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": False,
        "maximum_complete_stream_bytes": MAX_PROCESS_BYTES,
        "size_limit_exceeded": True,
    }


def validate_failure_stream(
    value: Any,
    label: str,
) -> dict[str, Any]:
    require(
        type(value) is dict,
        "a post-invocation native failure concealed raw process evidence",
    )
    if value.get("complete") is True:
        decode_stream(value, label)
        return value
    require(
        set(value) == {
            "base64", "bytes", "sha256", "complete",
            "maximum_complete_stream_bytes", "size_limit_exceeded",
        }
        and value.get("base64") is None
        and type(value.get("bytes")) is int
        and value["bytes"] > MAX_PROCESS_BYTES
        and value.get("complete") is False
        and value.get("maximum_complete_stream_bytes")
        == MAX_PROCESS_BYTES
        and value.get("size_limit_exceeded") is True,
        "an oversized native stream was omitted without explicit disclosure",
    )
    validate_digest(value["sha256"], label)
    return value


def validate_observation_failure_document(
    value: Any,
) -> dict[str, Any]:
    expected = {
        "schema": SCHEMA + "-post-invocation-failure",
        "status": "FAIL",
        "publication_status": "FAIL",
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        **validate_compact_bounds(),
        "actual_process_invocations": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    additional = {
        "mode",
        "error_type",
        "error",
        "actual_process_pid",
        "actual_process_returncode",
        "actual_process_signal",
        "actual_process_timed_out",
        "actual_process_spawn_error",
        "complete_actual_process_stdout",
        "complete_actual_process_stderr",
        "actual_reference_workers",
        "actual_candidate_workers",
        "actual_candidate_imports",
        "actual_baseline_controller_invocations",
        "actual_candidate_process_invocations",
        "validated_reference_a_case_count",
        "validated_reference_b_case_count",
        "validated_candidate_record_count",
        "baseline_reference_pids",
        "published_report",
        "published_receipt",
        "published_evidence_file_count",
        "workspace_files_written",
        "evidence_files_created",
        "reference_outcomes_known",
        "candidate_outcomes_known",
    }
    require(
        type(value) is dict and set(value) == set(expected) | additional,
        "a complete post-invocation failure field was hidden",
    )
    for field, original in expected.items():
        require(
            value.get(field) == original
            and type(value.get(field)) is type(original),
            "a truthful post-invocation failure changed: " + field,
        )
    mode = value["mode"]
    require(
        mode in {"baseline", "candidate"}
        and type(value.get("error_type")) is str
        and type(value.get("error")) is str
        and type(value.get("actual_process_pid")) is int
        and value["actual_process_pid"] > 0
        and (
            value.get("actual_process_returncode") is None
            or type(value["actual_process_returncode"]) is int
        )
        and (
            value.get("actual_process_signal") is None
            or type(value["actual_process_signal"]) is int
        )
        and type(value.get("actual_process_timed_out")) is bool
        and (
            value.get("actual_process_spawn_error") is None
            or type(value["actual_process_spawn_error"]) is str
        ),
        "a failed real process, PID, timeout, or exit was fabricated",
    )
    validate_failure_stream(
        value["complete_actual_process_stdout"],
        "complete failed process stdout",
    )
    validate_failure_stream(
        value["complete_actual_process_stderr"],
        "complete failed process stderr",
    )
    if mode == "baseline":
        require(
            value["actual_baseline_controller_invocations"] == 1
            and value["actual_candidate_process_invocations"] == 0
            and value["actual_candidate_workers"] == 0
            and value["actual_candidate_imports"] == 0
            and value["actual_reference_workers"] in {2, "UNKNOWN"},
            "an already started standard reference was falsely called unrun",
        )
    else:
        require(
            value["actual_baseline_controller_invocations"] == 0
            and value["actual_candidate_process_invocations"] == 1
            and value["actual_reference_workers"] == 0
            and value["actual_candidate_workers"] in {1, "UNKNOWN"}
            and (
                value["actual_candidate_imports"] == "UNKNOWN"
                or type(value["actual_candidate_imports"]) is int
                and value["actual_candidate_imports"] >= 2
            ),
            "an already started independent candidate was falsely called unrun",
        )
    require(
        value["reference_outcomes_known"]
        is (value["actual_reference_workers"] == 2)
        and value["candidate_outcomes_known"]
        is (value["actual_candidate_workers"] == 1),
        "UNKNOWN reference or candidate outcomes were silently asserted",
    )
    published = (
        int(value["published_report"] is not None)
        + int(value["published_receipt"] is not None)
    )
    require(
        value["published_evidence_file_count"] == published
        and value["workspace_files_written"] == published
        and value["evidence_files_created"] == published
        and (
            value["published_receipt"] is None
            or value["published_report"] is not None
        ),
        "a partially completed evidence publication was concealed",
    )
    if value["actual_reference_workers"] == 2:
        pids = value["baseline_reference_pids"]
        require(
            type(pids) is list
            and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1]
            and value["validated_reference_a_case_count"] == CASE_COUNT
            and value["validated_reference_b_case_count"] == CASE_COUNT,
            "a fully validated reference process or denominator was forged",
        )
    else:
        require(
            value["validated_reference_a_case_count"] is None
            and value["validated_reference_b_case_count"] is None
            and (
                value["baseline_reference_pids"] is None
                or mode == "candidate"
            ),
            "UNKNOWN standard-reference results were misrepresented",
        )
    if value["actual_candidate_workers"] == 1:
        require(
            value["validated_candidate_record_count"] == CASE_COUNT,
            "a fully validated candidate denominator was forged",
        )
    else:
        require(
            value["validated_candidate_record_count"] is None,
            "UNKNOWN candidate outcomes were misrepresented",
        )
    return value


def observation_failure_document(
    error: ObservationFailure,
) -> dict[str, Any]:
    require(
        isinstance(error, ObservationFailure)
        and error.mode in {"baseline", "candidate"}
        and type(error.process) is dict
        and error.process.get("started") is True
        and type(error.process.get("pid")) is int
        and error.process["pid"] > 0,
        "post-invocation failure evidence requires a real independent process",
    )
    stdout = capture_failure_stream(
        error.process.get("stdout"),
        "complete failed isolated stdout",
    )
    stderr = capture_failure_stream(
        error.process.get("stderr"),
        "complete failed isolated stderr",
    )
    report = error.report
    reference_workers: int | str = (
        report.get("actual_reference_workers")
        if report is not None
        else "UNKNOWN" if error.mode == "baseline"
        else 0
    )
    if reference_workers is None:
        reference_workers = "UNKNOWN"
    candidate_workers: int | str = (
        report.get("actual_candidate_workers")
        if report is not None
        else "UNKNOWN" if error.mode == "candidate"
        else 0
    )
    if candidate_workers is None:
        candidate_workers = "UNKNOWN"
    published = (
        int(error.report_publication is not None)
        + int(error.receipt_publication is not None)
    )
    document = {
        "schema": SCHEMA + "-post-invocation-failure",
        "status": "FAIL",
        "publication_status": "FAIL",
        "mode": error.mode,
        "error_type": type(error).__qualname__,
        "error": str(error),
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        **validate_compact_bounds(),
        "actual_process_invocations": 1,
        "actual_process_pid": error.process["pid"],
        "actual_process_returncode": error.process.get("returncode"),
        "actual_process_signal": error.process.get("signal"),
        "actual_process_timed_out": (
            error.process.get("timed_out") is True
        ),
        "actual_process_spawn_error": error.process.get("spawn_error"),
        "complete_actual_process_stdout": stdout,
        "complete_actual_process_stderr": stderr,
        "actual_reference_workers": reference_workers,
        "actual_candidate_workers": candidate_workers,
        "actual_candidate_imports": (
            0 if error.mode == "baseline"
            else report.get("actual_candidate_imports", "UNKNOWN")
            if report is not None else "UNKNOWN"
        ),
        "actual_baseline_controller_invocations": (
            1 if error.mode == "baseline" else 0
        ),
        "actual_candidate_process_invocations": (
            1 if error.mode == "candidate" else 0
        ),
        "validated_reference_a_case_count": (
            report.get("validated_reference_a_case_count")
            if report is not None else None
        ),
        "validated_reference_b_case_count": (
            report.get("validated_reference_b_case_count")
            if report is not None else None
        ),
        "validated_candidate_record_count": (
            report.get("validated_candidate_record_count")
            if report is not None else None
        ),
        "baseline_reference_pids": (
            report.get("baseline_reference_pids")
            if report is not None else None
        ),
        "published_report": error.report_publication,
        "published_receipt": error.receipt_publication,
        "published_evidence_file_count": published,
        "workspace_files_written": published,
        "evidence_files_created": published,
        "reference_outcomes_known": reference_workers == 2,
        "candidate_outcomes_known": candidate_workers == 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return validate_observation_failure_document(document)




class SourceOnlyBoundary:
    """Make actual files, clocks, imports, workers, and writes impossible."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "file_reads": 0, "file_writes": 0, "processes": 0,
            "candidate_imports": 0, "dynamic_imports": 0,
            "clock_samples": 0, "threads": 0,
            "garbage_collections": 0, "directory_syncs": 0,
            "randomness": 0,
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        self.originals.append((owner, name, getattr(owner, name)))

        def denied(*args: Any, **kwargs: Any) -> Any:
            selected = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if type(mode) is str and any(item in mode for item in "wax+"):
                    selected = "file_writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT
                    | os.O_TRUNC | os.O_APPEND
                ):
                    selected = "file_writes"
            elif category == "dynamic_imports" and args:
                target = args[0]
                if type(target) is str and (
                    target == "candidates" or target.startswith("candidates.")
                ):
                    selected = "candidate_imports"
            self.blocked[selected] += 1
            raise SourceOnlyError(
                "source-only substitution controls cannot perform " + selected
            )

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        for owner, name, category in (
            (builtins, "open", "file_reads"),
            (io, "open", "file_reads"),
            (os, "open", "file_reads"),
            (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"),
            (os, "scandir", "file_reads"),
            (os, "listdir", "file_reads"),
            (os, "readlink", "file_reads"),
            (os, "replace", "file_writes"),
            (os, "rename", "file_writes"),
            (os, "remove", "file_writes"),
            (os, "link", "file_writes"),
            (os, "unlink", "file_writes"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (os, "fsync", "directory_syncs"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (os, "system", "processes"),
            (os, "fork", "processes"),
            (os, "posix_spawn", "processes"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clock_samples"),
            (time, "time_ns", "clock_samples"),
            (time, "monotonic", "clock_samples"),
            (time, "monotonic_ns", "clock_samples"),
            (time, "perf_counter", "clock_samples"),
            (time, "perf_counter_ns", "clock_samples"),
            (gc, "collect", "garbage_collections"),
            (os, "urandom", "randomness"),
            (importlib, "import_module", "dynamic_imports"),
            (builtins, "__import__", "dynamic_imports"),
        ):
            self.install(owner, name, category)
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False


def synthetic_owner(relative: str, source: str, number: int) -> dict[str, Any]:
    return {
        "relative": relative, "sha256": source,
        "bytes": 4096 + number, "device": 7, "inode": 80_000 + number,
    }


def synthetic_frozen_source_owners(recorder_pin: str) -> dict[str, Any]:
    return validate_frozen_source_owners(
        {
            "recorder": synthetic_owner(SOURCE_RELATIVE, recorder_pin, 1),
            "previous_recorder": synthetic_owner(
                PREVIOUS_RECORDER_RELATIVE,
                PREVIOUS_RECORDER_SHA256,
                5,
            ),
            "preserved_previous_failure": synthetic_owner(
                PRESERVED_PREVIOUS_FAILURE_RELATIVE,
                PRESERVED_PREVIOUS_FAILURE_SHA256,
                6,
            ),
            "substitution_oracle": synthetic_owner(
                ORACLE_RELATIVE,
                ORACLE_SHA256,
                2,
            ),
            "original_v5": synthetic_owner(V5_RELATIVE, V5_SHA256, 3),
            "from_scratch_audit_v3": synthetic_owner(
                AUDIT_RELATIVE,
                AUDIT_SHA256,
                4,
            ),
        },
        recorder_pin,
    )


def synthetic_preserved_previous_failure() -> dict[str, Any]:
    nested = {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-"
            "recorder-v1-failure"
        ),
        "status": "FAIL",
        "error_type": "RecorderError",
        "error": "a complete substitution report exceeds its bound",
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return {
        "schema": (
            "rebar-independent-substitution-buffer-semantics-v1-"
            "controller-failure-preserved-v1"
        ),
        "status": "FAIL",
        "python": "3.14.6",
        "label": "shared-suite-v1",
        "recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "recorder_source_sha256": PREVIOUS_RECORDER_SHA256,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "actual_baseline_controller_invocations": 1,
        "actual_reference_worker_count": "UNKNOWN",
        "reported_reference_worker_count_is_reliable": False,
        "actual_candidate_workers": 0,
        "reference_outcomes_status": "NOT MEASURED",
        "baseline_result_status": "NOT MEASURED",
        "report_publication_status": "NOT PUBLISHED",
        "receipt_publication_status": "NOT PUBLISHED",
        "controller_exit_code": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
        "complete_controller_failure_stdout": nested,
        "failure_explanation": (
            "The version-one recorder started the baseline controller "
            "before its complete lossless report exceeded the 268435456-byte "
            "uncompressed safety bound. Its outer exception envelope reports "
            "zero reference workers after losing the already-executed process "
            "context; that counter is not reliable and is preserved as "
            "observed rather than reported as fact."
        ),
    }


class SyntheticSubstitutionOracle:
    """Strict in-memory reference fixture; never imports a real matcher."""

    def validate_source_owners(
        self,
        value: Any,
        source_pin: str,
    ) -> dict[str, Any]:
        expected = {
            "substitution_oracle": synthetic_owner(
                ORACLE_RELATIVE,
                source_pin,
                20,
            ),
        }
        require(
            type(value) is dict and value == expected,
            "an in-memory-only reference source fixture was substituted",
        )
        return value

    def validate_outcome(self, value: Any) -> dict[str, Any]:
        return validate_candidate_outcome(value)

    def validate_records(
        self,
        matrix: list[dict[str, Any]],
        records: Any,
        expected: str,
    ) -> list[dict[str, Any]]:
        return validate_candidate_records(matrix, records, expected)

    def validate_reference_pair(
        self,
        first: Any,
        second: Any,
        first_process: Any,
        second_process: Any,
        *,
        source_pin: str,
        matrix: list[dict[str, Any]],
    ) -> str:
        for role, worker, process in (
            ("reference_a", first, first_process),
            ("reference_b", second, second_process),
        ):
            require(
                type(worker) is dict
                and worker.get("schema")
                == ORACLE_SCHEMA + "-isolated-reference-worker"
                and worker.get("status") == "OBSERVED"
                and worker.get("role") == role
                and type(worker.get("pid")) is int
                and worker["pid"] > 0
                and worker.get("oracle_source_sha256") == source_pin
                and worker.get("matrix_sha256") == MATRIX_SHA256
                and worker.get("published_seed") == PUBLISHED_SEED
                and worker.get("case_count") == CASE_COUNT
                and worker.get("actual_reference_workers") == 1
                and worker.get("actual_candidate_workers") == 0
                and worker.get("actual_candidate_imports") == 0,
                "an exact in-memory reference fixture was substituted",
            )
            self.validate_source_owners(worker["source_owners"], source_pin)
            self.validate_records(
                matrix,
                worker["records"],
                worker["records_sha256"],
            )
            require(
                type(process) is dict
                and process.get("role") == role
                and process.get("pid") == worker["pid"]
                and process.get("returncode") == 0
                and decode_stream(
                    process["stdout"],
                    "complete synthetic-only reference worker",
                ) == canonical(worker)
                and decode_stream(
                    process["stderr"],
                    "complete synthetic-only reference stderr",
                ) == b"",
                "an in-memory canonical reference process was substituted",
            )
        require(
            first["pid"] != second["pid"]
            and first["source_owners"] == second["source_owners"]
            and first["records_sha256"] == second["records_sha256"]
            and first["records"] == second["records"],
            "the two complete synthetic-only reference vectors disagree",
        )
        return first["records_sha256"]


class SyntheticFromScratchAudit:
    """Validate real-shaped owned-family fixtures without any file access."""

    immutable_policies = {
        "tools/independent_from_scratch_audit_v2.py": (
            "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
        ),
        V5_RELATIVE: V5_SHA256,
    }

    def validate_family_pins(
        self,
        family: Any,
        adapter: Any,
        engine: Any,
        bridge: Any,
        source_entries: Any,
        native_entries: Any,
    ) -> dict[str, Any]:
        spec = family_spec(family)
        require(
            type(source_entries) is list and type(native_entries) is list,
            "retain every synthetic-only owned source and native entry",
        )
        parsed_sources = dict(
            parse_owned_source(value) for value in source_entries
        )
        parsed_native = dict(
            parse_owned_source(value) for value in native_entries
        )
        require(
            len(parsed_sources) == len(source_entries)
            and set(parsed_sources) == set(spec.owned_source_relatives)
            and parsed_sources.get(spec.adapter_relative) == adapter
            and len(parsed_native) == len(native_entries)
            and set(parsed_native)
            == {spec.engine_relative, spec.bridge_relative}
            and parsed_native.get(spec.engine_relative) == engine
            and parsed_native.get(spec.bridge_relative) == bridge
            and (engine == bridge) is (family == "c")
            and len(set(parsed_sources.values())) == len(parsed_sources)
            and len(set(parsed_native.values())) == len(parsed_native),
            "an in-memory exact native ownership manifest was forged",
        )
        return {
            "family": family,
            "candidate_source_sha256": adapter,
            "native_engine_sha256": engine,
            "native_bridge_sha256": bridge,
            "source_sha256": dict(sorted(parsed_sources.items())),
            "native_sha256": dict(sorted(parsed_native.items())),
            "immutable_policy_sha256": dict(self.immutable_policies),
        }

    def validate_manifest(
        self,
        value: Any,
        family: str,
    ) -> dict[str, Any]:
        require(
            type(value) is dict
            and set(value) == {
                "family",
                "candidate_source_sha256",
                "native_engine_sha256",
                "native_bridge_sha256",
                "source_sha256",
                "native_sha256",
                "immutable_policy_sha256",
            }
            and value.get("family") == family
            and type(value.get("source_sha256")) is dict
            and type(value.get("native_sha256")) is dict
            and value.get("immutable_policy_sha256")
            == self.immutable_policies,
            "a complete synthetic-only family manifest was substituted",
        )
        expected = self.validate_family_pins(
            family,
            value["candidate_source_sha256"],
            value["native_engine_sha256"],
            value["native_bridge_sha256"],
            [
                path + "=" + source
                for path, source in value["source_sha256"].items()
            ],
            [
                path + "=" + source
                for path, source in value["native_sha256"].items()
            ],
        )
        require(
            value == expected,
            "an in-memory source, native artifact, or policy was replaced",
        )
        return value

    def validate_serializable_owners(
        self,
        value: Any,
        family: str,
        manifest: Mapping[str, Any],
        source_pin: str,
    ) -> dict[str, Any]:
        require(
            type(value) is dict
            and set(value) == {
                "family",
                "manifest",
                "source_owners",
                "native_owners",
                "policy_owners",
                "oracle_owner",
                "python_owner",
            }
            and value.get("family") == family
            and value.get("manifest") == manifest,
            "a complete synthetic-only owned source closure was omitted",
        )
        self.validate_manifest(value["manifest"], family)
        for section, expected in (
            ("source_owners", manifest["source_sha256"]),
            ("native_owners", manifest["native_sha256"]),
            ("policy_owners", self.immutable_policies),
        ):
            observed = value[section]
            require(
                type(observed) is dict and set(observed) == set(expected),
                "a synthetic-only family owner or policy was omitted",
            )
            for relative, pinned in expected.items():
                validate_owner(observed[relative], relative, pinned)
        validate_owner(value["oracle_owner"], AUDIT_RELATIVE, source_pin)
        python = value["python_owner"]
        require(
            type(python) is dict
            and set(python) == {
                "path",
                "sha256",
                "bytes",
                "device",
                "inode",
            }
            and python.get("path") == PINNED_PYTHON
            and python.get("sha256") == PINNED_PYTHON_SHA256
            and type(python.get("bytes")) is int
            and python["bytes"] > 0
            and type(python.get("device")) is int
            and python["device"] >= 0
            and type(python.get("inode")) is int
            and python["inode"] > 0,
            "a synthetic-only pinned standard interpreter was substituted",
        )
        return value


def synthetic_baseline_pins() -> BaselinePins:
    return make_baseline_pins(
        "shared-suite-v1", "12" * 32, "34" * 32, "56" * 32,
    )


def synthetic_owner_pins(family: str) -> OwnerPins:
    spec = family_spec(family)
    adapter, engine = "78" * 32, "9a" * 32
    bridge = engine if family == "c" else "bc" * 32
    sources = [
        path + "=" + (
            adapter if path == spec.adapter_relative
            else hashlib.sha256(path.encode("ascii")).hexdigest()
        )
        for path in spec.owned_source_relatives
    ]
    return make_owner_pins(
        family, "de" * 32, adapter, engine, bridge,
        sources, synthetic_baseline_pins(),
    )


def synthetic_guard(spec: FamilySpec) -> dict[str, Any]:
    result = {name: True for name in GUARD_TRUE_FIELDS}
    result.update({
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "owned_native_ffi_allowed": spec.owned_ctypes,
        "trusted_stdlib_ctypes_preloaded": spec.owned_ctypes,
        "trusted_stdlib_ctypes_builtin_verified": spec.owned_ctypes,
        "trusted_stdlib_ctypes_pythonapi_initialized": spec.owned_ctypes,
        "trusted_stdlib_ctypes_source_sha256": (
            TRUSTED_CTYPES_SHA256 if spec.owned_ctypes else None
        ),
        "cached_original_matcher_descendant_count": 0,
        "cached_original_holder_count": 0,
        "owned_ctypes_load_count": 1 if spec.owned_ctypes else 0,
        "owned_ctypes_symbol_count": 3 if spec.owned_ctypes else 0,
    })
    return result


def synthetic_buffer_event(
    kind: str,
    role: str,
    flags: int | None,
    before: int,
    after: int,
    *,
    behavior: str = "stable",
    backing: bytes = b"alpha42",
) -> dict[str, Any]:
    require(
        kind in {"acquire", "acquire-error", "release", "hash", "hash-error"}
        and role in {"subject", "replacement"}
        and behavior in {"stable", "mutate", "fail"},
        "an exact in-memory synthetic exporter event is mandatory",
    )
    after_backing = (
        b"!" * len(backing)
        if kind == "release" and behavior == "mutate"
        else backing
    )
    event: dict[str, Any] = {
        "event": kind,
        "role": role,
        "flags": flags,
        "active_before": before,
        "active_after": after,
        "backing_before_hex": backing.hex(),
        "backing_after_hex": after_backing.hex(),
        "behavior": behavior,
    }
    if kind == "hash":
        event["hash_result"] = 1729
    return event


def synthetic_nested_events() -> list[dict[str, Any]]:
    return [
        {"event": "phase", "name": "synthetic-materialize"},
        synthetic_buffer_event(
            "acquire", "subject", SIMPLE_BUFFER_FLAG, 0, 1,
        ),
        synthetic_buffer_event(
            "acquire", "replacement", SIMPLE_BUFFER_FLAG, 0, 1,
        ),
        synthetic_buffer_event(
            "acquire", "replacement", FULL_READONLY_BUFFER_FLAG, 1, 2,
        ),
        synthetic_buffer_event("release", "replacement", None, 2, 1),
        synthetic_buffer_event("release", "replacement", None, 1, 0),
        synthetic_buffer_event("release", "subject", None, 1, 0),
        {"event": "phase", "name": "synthetic-cleanup"},
    ]


def synthetic_outcome(row: Mapping[str, Any]) -> dict[str, Any]:
    empty = {"kind": "none"}
    return {
        "status": "return",
        "stage": row["api"],
        "value": dict(empty),
        "exception": None,
        "events": [
            {"event": "phase", "name": "synthetic-operation"},
            {"event": "phase", "name": "synthetic-cleanup"},
        ],
        "callbacks": [],
        "warnings": [],
        "subject_after": dict(empty),
        "replacement_after": dict(empty),
        "subject_active_exports": 0,
        "replacement_active_exports": 0,
        "count_requested": row["count"],
        "pos_requested": row["pos"],
        "endpos_requested": row["endpos"],
    }


def synthetic_records(
    matrix: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "case": row["case"],
            "cohort": row["cohort"],
            "api": row["api"],
            "outcome": synthetic_outcome(row),
        }
        for row in matrix
    ]


def synthetic_baseline_receipt(
    pins: OwnerPins,
) -> dict[str, Any]:
    before = {
        "recorder": synthetic_owner(
            SOURCE_RELATIVE, pins.recorder, 1,
        ),
        "previous_recorder": synthetic_owner(
            PREVIOUS_RECORDER_RELATIVE,
            PREVIOUS_RECORDER_SHA256,
            5,
        ),
        "preserved_previous_failure": synthetic_owner(
            PRESERVED_PREVIOUS_FAILURE_RELATIVE,
            PRESERVED_PREVIOUS_FAILURE_SHA256,
            6,
        ),
        "substitution_oracle": synthetic_owner(
            ORACLE_RELATIVE, ORACLE_SHA256, 2,
        ),
        "original_v5": synthetic_owner(
            V5_RELATIVE, V5_SHA256, 3,
        ),
        "from_scratch_audit_v3": synthetic_owner(
            AUDIT_RELATIVE, AUDIT_SHA256, 4,
        ),
    }
    report: dict[str, Any] = {
        "status": "PASS",
        "baseline_records_sha256": pins.baseline.records,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_reference_pids": [82_001, 82_002],
        "actual_reference_workers": 2,
        "actual_baseline_controller_invocations": 1,
        "source_closure_before": before,
        "source_closure_after": before,
        "source_closure_unchanged": True,
    }
    report_relative, receipt_relative = approved_paths(
        "baseline", pins.baseline.label,
    )
    publication = {
        "path": report_relative,
        "sha256": pins.baseline.archive,
        "bytes": 12_345,
        "uncompressed_sha256": "ab" * 32,
        "uncompressed_bytes": 67_890,
        "compression": "gzip-mtime-zero-level-9",
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True,
        "complete_readback_verified": True,
    }
    preflight = {
        "receipt_relative": receipt_relative,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_observation": True,
    }
    return make_baseline_receipt(
        pins.recorder,
        pins.baseline.label,
        report,
        publication,
        preflight,
    )


def synthetic_complete_baseline(
    matrix: list[dict[str, Any]],
    records: list[dict[str, Any]],
    recorder_pin: str,
    oracle: SyntheticSubstitutionOracle,
) -> tuple[dict[str, Any], dict[str, Any]]:
    records_pin = digest(records)
    source_owners = {
        "substitution_oracle": synthetic_owner(
            ORACLE_RELATIVE,
            ORACLE_SHA256,
            20,
        ),
    }
    references: dict[str, dict[str, Any]] = {}
    processes: dict[str, dict[str, Any]] = {}
    for role, pid in (("reference_a", 82_001), ("reference_b", 82_002)):
        worker = {
            "schema": ORACLE_SCHEMA + "-isolated-reference-worker",
            "status": "OBSERVED",
            "python": "3.14.6",
            "role": role,
            "pid": pid,
            "oracle_source_sha256": ORACLE_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
            "cohort_count": len(COHORTS),
            "variants_per_cohort": VARIANTS_PER_COHORT,
            "case_count": CASE_COUNT,
            "records_sha256": records_pin,
            "records": records,
            "source_owners": source_owners,
            "reference_guard": {"source_only_synthetic_reference": True},
            "actual_reference_workers": 1,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        references[role] = worker
        processes[role] = {
            "role": role,
            "pid": pid,
            "returncode": 0,
            "stdout": capture_stream(
                canonical(worker),
                "synthetic-only complete reference stdout",
            ),
            "stderr": capture_stream(
                b"",
                "synthetic-only complete reference stderr",
            ),
        }
    result = {
        "schema": ORACLE_SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "baseline_records_sha256": records_pin,
        "source_owners": source_owners,
        "reference_a": references["reference_a"],
        "reference_b": references["reference_b"],
        "reference_a_process": processes["reference_a"],
        "reference_b_process": processes["reference_b"],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    owners = synthetic_frozen_source_owners(recorder_pin)
    process = {
        "started": True,
        "pid": 83_001,
        "returncode": 0,
        "signal": None,
        "timed_out": False,
        "spawn_error": None,
        "stdout": canonical(result),
        "stderr": b"",
    }
    report = build_baseline_report(
        recorder_pin,
        "shared-suite-v1",
        process,
        oracle,
        matrix,
        owners,
        owners,
    )
    require(
        report["status"] == "PASS"
        and report["actual_reference_workers"] == 2
        and report["baseline_records_sha256"] == records_pin,
        "a complete synthetic-only two-reference baseline was not retained",
    )
    return report, owners


def synthetic_complete_receipt(
    pins: OwnerPins,
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    report_relative, receipt_relative = approved_paths(
        "baseline",
        pins.baseline.label,
    )
    publication = {
        "path": report_relative,
        "sha256": pins.baseline.archive,
        "bytes": 12_345,
        "uncompressed_sha256": digest(baseline),
        "uncompressed_bytes": len(canonical(baseline)),
        "compression": "gzip-mtime-zero-level-9",
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True,
        "complete_readback_verified": True,
    }
    preflight = {
        "receipt_relative": receipt_relative,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_observation": True,
    }
    receipt = make_baseline_receipt(
        pins.recorder,
        pins.baseline.label,
        baseline,
        publication,
        preflight,
    )
    return validate_baseline_receipt(receipt, pins)


def synthetic_complete_candidate_worker(
    pins: OwnerPins,
    matrix: list[dict[str, Any]],
    records: list[dict[str, Any]],
    receipt: Mapping[str, Any],
    oracle: SyntheticSubstitutionOracle,
    audit: SyntheticFromScratchAudit,
    *,
    pid: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    spec = family_spec(pins.family)
    manifest = make_audit_manifest(pins, audit)
    source_owners = {
        relative: synthetic_owner(relative, pinned, 100 + index)
        for index, (relative, pinned) in enumerate(
            manifest["source_sha256"].items()
        )
    }
    native_owners = {
        relative: synthetic_owner(relative, pinned, 200 + index)
        for index, (relative, pinned) in enumerate(
            manifest["native_sha256"].items()
        )
    }
    policy_owners = {
        relative: synthetic_owner(relative, pinned, 300 + index)
        for index, (relative, pinned) in enumerate(
            audit.immutable_policies.items()
        )
    }
    closure = {
        "family": spec.name,
        "manifest": manifest,
        "source_owners": source_owners,
        "native_owners": native_owners,
        "policy_owners": policy_owners,
        "oracle_owner": synthetic_owner(AUDIT_RELATIVE, AUDIT_SHA256, 401),
        "python_owner": {
            "path": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
            "bytes": 8_192,
            "device": 7,
            "inode": 80_402,
        },
    }
    audit.validate_serializable_owners(
        closure,
        spec.name,
        manifest,
        AUDIT_SHA256,
    )
    worker = {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "role": "candidate-" + spec.name,
        "pid": pid,
        "candidate_family": spec.name,
        **baseline_source_fields(pins.recorder, pins.baseline.label),
        "baseline_receipt_relative": approved_paths(
            "baseline",
            pins.baseline.label,
        )[1],
        "baseline_receipt_sha256": pins.baseline.receipt,
        "baseline_archive_relative": approved_paths(
            "baseline",
            pins.baseline.label,
        )[0],
        "baseline_archive_sha256": pins.baseline.archive,
        "baseline_records_sha256": pins.baseline.records,
        "baseline_reference_pids": receipt["baseline_reference_pids"],
        "baseline_receipt_owner": synthetic_owner(
            approved_paths("baseline", pins.baseline.label)[1],
            pins.baseline.receipt,
            501,
        ),
        "baseline_archive_owner": synthetic_owner(
            approved_paths("baseline", pins.baseline.label)[0],
            pins.baseline.archive,
            502,
        ),
        "source_provenance": synthetic_frozen_source_owners(
            pins.recorder,
        ),
        "audit_manifest": manifest,
        "owned_source_closure": closure,
        "native_provenance": {
            "source": source_owners[spec.adapter_relative],
            "native_engine": native_owners[spec.engine_relative],
            "native_bridge": native_owners[spec.bridge_relative],
        },
        "matcher_guard": synthetic_guard(spec),
        "records_sha256": digest(records),
        "records": records,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": 2,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return (
        validate_candidate_worker(
            worker,
            pins,
            matrix,
            expected_pid=pid,
            oracle=oracle,
            audit=audit,
        ),
        closure,
    )



def expect_rejection(
    name: str, operation: Callable[[], Any], rejected: list[str],
) -> None:
    require(type(name) is str and name not in rejected and callable(operation),
            "a synthetic poison control was duplicated")
    try:
        operation()
    except (RecorderError, OSError, TypeError, ValueError, KeyError,
            OverflowError, UnicodeError, EOFError, gzip.BadGzipFile):
        rejected.append(name)
        return
    raise RecorderError("a forged substitution control was accepted: " + name)


def source_self_test() -> dict[str, Any]:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "run synthetic-only controls under clean isolated pinned CPython",
    )
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, actual: Any) -> None:
        require(
            type(name) is str and name not in accepted and bool(actual),
            "a distinct synthetic substitution control failed: " + name,
        )
        accepted.append(name)

    def reject(name: str, operation: Callable[[], Any]) -> None:
        expect_rejection(name, operation, rejected)

    with SourceOnlyBoundary() as blocked:
        matrix = validate_matrix(build_frozen_matrix())
        accept(
            "pin-unchanged-frozen-v1-recorder-and-preserved-real-failure",
            PREVIOUS_RECORDER_RELATIVE
            == "tools/record_independent_substitution_buffer_semantics_v1.py"
            and PREVIOUS_RECORDER_SHA256
            == "1dbb45e8950a0eceb966a56adcbe2f9d1da35ec04883458a780b6f08f5a4735d"
            and PRESERVED_PREVIOUS_FAILURE_RELATIVE
            == (
                "experiments/rust_public_practice_v1/"
                "substitution-buffer-semantics-v1-shared-suite-v1-"
                "controller-failure-v1.json"
            )
            and PRESERVED_PREVIOUS_FAILURE_SHA256
            == "a80316f3d1fe87808c8f16cb651393d275132d408633303da16a5142f55ba807",
        )
        preserved_failure = synthetic_preserved_previous_failure()
        accept(
            "authenticate-complete-genuine-v1-failure-with-exact-a803-digest",
            validate_preserved_previous_failure(preserved_failure)
            == preserved_failure
            and digest(preserved_failure)
            == PRESERVED_PREVIOUS_FAILURE_SHA256,
        )
        for field, poison in (
            ("recorder_source_sha256", "ef" * 32),
            ("oracle_source_sha256", "ef" * 32),
            ("matrix_sha256", "ef" * 32),
            ("published_seed_decimal", str(PUBLISHED_SEED - 1)),
            ("actual_reference_worker_count", 0),
            ("reported_reference_worker_count_is_reliable", True),
            ("actual_baseline_controller_invocations", 0),
            ("report_publication_status", "PUBLISHED"),
            ("hidden_cases_read", 1),
        ):
            reject(
                "reject-preserved-real-v1-failure-forgery-" + field,
                lambda field=field, poison=poison:
                validate_preserved_previous_failure({
                    **preserved_failure,
                    field: poison,
                }),
            )
        reject(
            "reject-omitted-genuine-v1-failure-envelope",
            lambda: validate_preserved_previous_failure({
                field: value
                for field, value in preserved_failure.items()
                if field != "complete_controller_failure_stdout"
            }),
        )
        reject(
            "reject-forged-genuine-v1-failure-false-zero-envelope",
            lambda: validate_preserved_previous_failure({
                **preserved_failure,
                "complete_controller_failure_stdout": {
                    **preserved_failure[
                        "complete_controller_failure_stdout"
                    ],
                    "actual_reference_workers": 2,
                },
            }),
        )
        bounds = validate_compact_bounds()
        accept(
            "prove-exact-96-mib-raw-and-128-mib-base64-stream-ceilings",
            encoded_stream_byte_count(
                96 * 1024 * 1024,
                "synthetic maximum",
            ) == 128 * 1024 * 1024
            and bounds["maximum_raw_process_stream_bytes"]
            == 96 * 1024 * 1024,
        )
        accept(
            "prove-two-full-streams-plus-32-mib-fit-288-mib-compact-report",
            bounds["maximum_process_stream_count"] == 2
            and 2 * bounds["maximum_encoded_process_stream_bytes"]
            + bounds["maximum_compact_report_metadata_bytes"]
            == bounds["maximum_compact_report_bytes"]
            == 288 * 1024 * 1024
            and bounds["maximum_compact_report_bytes"]
            < bounds["maximum_uncompressed_bytes"]
            < bounds["maximum_archive_bytes"],
        )
        accept(
            "reproduce-all-5120-source-ordered-frozen-substitution-cases",
            len(matrix) == 5_120 and digest(matrix) == MATRIX_SHA256,
        )
        accept(
            "preserve-exact-64-bit-substitution-seed-without-json-rounding",
            PUBLISHED_SEED == 6_004_778_603_531_028_017
            and PUBLISHED_SEED > 2 ** 53
            and str(PUBLISHED_SEED) == "6004778603531028017"
            and all(row["seed"] == PUBLISHED_SEED for row in matrix),
        )
        accept(
            "retain-all-64-equally-weighted-80-variant-cohorts",
            len(COHORTS) == 64
            and all(
                sum(row["cohort"] == cohort for row in matrix)
                == VARIANTS_PER_COHORT
                for cohort in COHORTS
            ),
        )
        accept(
            "retain-all-five-module-compiled-and-expand-apis",
            {row["api"] for row in matrix} == set(APIS)
            and len(APIS) == 5,
        )
        accept(
            "retain-exact-simple-and-full-readonly-buffer-flags",
            SIMPLE_BUFFER_FLAG == 0 and FULL_READONLY_BUFFER_FLAG == 284,
        )
        accept(
            "retain-all-subject-template-and-pep688-carriers",
            any(
                row["subject"]["kind"].startswith("pep688-")
                for row in matrix
            )
            and any(
                row["replacement"]["kind"].startswith("pep688-")
                for row in matrix
            )
            and any(
                row["replacement"]["kind"].startswith("released-")
                for row in matrix
            )
            and any(
                "strided" in row["subject"]["kind"]
                or "strided" in row["replacement"]["kind"]
                for row in matrix
            ),
        )
        accept(
            "retain-real-failing-replacement-callback-cases",
            any(row["callback_raises"] for row in matrix),
        )
        nested = synthetic_nested_events()
        accept(
            "preserve-nested-simple-simple-full-readonly-acquisition-order",
            validate_substitution_events(
                nested,
                require_balanced=True,
                expected_acquisition_flags=(0, 0, 284),
            ) == nested,
        )
        mutation = [
            synthetic_buffer_event(
                "acquire", "subject", 0, 0, 1, behavior="mutate",
            ),
            synthetic_buffer_event(
                "release", "subject", None, 1, 0, behavior="mutate",
            ),
        ]
        accept(
            "preserve-authentic-on-release-backing-mutation",
            validate_substitution_events(
                mutation,
                require_balanced=True,
                expected_acquisition_flags=(0,),
            ) == mutation,
        )
        hash_event = synthetic_buffer_event(
            "hash", "replacement", None, 0, 0,
        )
        accept(
            "preserve-exact-deterministic-custom-exporter-hash",
            validate_substitution_events([hash_event]) == [hash_event],
        )
        fail_event = synthetic_buffer_event(
            "acquire-error",
            "replacement",
            FULL_READONLY_BUFFER_FLAG,
            0,
            0,
            behavior="fail",
        )
        accept(
            "preserve-genuine-failing-full-readonly-buffer-export",
            validate_substitution_events([fail_event]) == [fail_event],
        )
        records = synthetic_records(matrix)
        records_sha256 = digest(records)
        accept(
            "preserve-all-5120-complete-ordered-synthetic-outcomes",
            validate_candidate_records(
                matrix, records, records_sha256,
            ) == records,
        )
        accept(
            "retain-every-result-event-window-and-live-export-counter",
            all(
                record["outcome"]["count_requested"] == row["count"]
                and record["outcome"]["pos_requested"] == row["pos"]
                and record["outcome"]["endpos_requested"] == row["endpos"]
                for row, record in zip(matrix, records, strict=True)
            ),
        )
        altered = list(records)
        altered[0] = {
            **records[0],
            "outcome": {
                **records[0]["outcome"],
                "stage": records[0]["outcome"]["stage"]
                + "-synthetic-mismatch",
            },
        }
        altered[1] = {
            **records[1],
            "outcome": {
                **records[1]["outcome"],
                "stage": records[1]["outcome"]["stage"]
                + "-synthetic-mismatch",
            },
        }
        mismatch, mismatch_cohorts, mismatch_apis = (
            reconstruct_mismatch_evidence(
                matrix,
                records,
                altered,
            )
        )
        mismatch_sha256 = digest(mismatch)
        accept(
            "reconstruct-every-source-ordered-mismatch-from-exact-outcomes",
            len(mismatch) == 2
            and [entry["index"] for entry in mismatch] == [0, 1]
            and sum(mismatch_cohorts.values()) == 2
            and sum(mismatch_apis.values()) == 2
            and validate_mismatch_evidence(
                mismatch,
                matrix,
                records,
                altered,
                mismatch_sha256,
            )[0] == mismatch,
        )
        for name, poisoned in (
            ("omitted", mismatch[1:]),
            ("reordered", list(reversed(mismatch))),
            ("duplicated", [mismatch[0], mismatch[0]]),
            (
                "forged-baseline-digest",
                [
                    {
                        **mismatch[0],
                        "baseline_outcome_sha256": "ef" * 32,
                    },
                    mismatch[1],
                ],
            ),
            (
                "forged-candidate-digest",
                [
                    {
                        **mismatch[0],
                        "candidate_outcome_sha256": "ef" * 32,
                    },
                    mismatch[1],
                ],
            ),
        ):
            reject(
                "reject-" + name + "-lossless-mismatch-evidence",
                lambda poisoned=poisoned: validate_mismatch_evidence(
                    poisoned,
                    matrix,
                    records,
                    altered,
                    mismatch_sha256,
                ),
            )
        fixture = canonical({
            "surrogate": "\ud800",
            "accent": "e\u0301",
            "emoji": "😀",
            "seed": PUBLISHED_SEED,
            "seed_decimal": str(PUBLISHED_SEED),
            "nested": [True, None, {"x": [1, 2]}],
        })
        decoded_fixture = decode_document(fixture, "synthetic-only")
        accept(
            "preserve-lone-surrogates-and-exact-large-integer-json",
            decoded_fixture["seed"] == PUBLISHED_SEED
            and decoded_fixture["seed_decimal"] == "6004778603531028017",
        )
        accept(
            "stream-exact-canonical-evidence-without-files",
            b"".join(iter_canonical(decoded_fixture)) == fixture,
        )
        compressed = gzip.compress(fixture, compresslevel=9, mtime=0)
        accept(
            "produce-deterministic-lossless-zero-mtime-gzip",
            compressed == gzip.compress(fixture, compresslevel=9, mtime=0)
            and gzip.decompress(compressed) == fixture,
        )
        stream = capture_stream(fixture, "synthetic-only")
        accept(
            "preserve-complete-reversible-isolated-worker-streams",
            decode_stream(stream, "synthetic-only") == fixture,
        )
        stress = bytes(range(256)) * 4_096
        stress_stream = capture_stream(stress, "synthetic one-mebibyte")
        accept(
            "losslessly-reverse-a-genuine-one-mib-worker-stream",
            len(stress) == 1_048_576
            and decode_stream(
                stress_stream,
                "synthetic one-mebibyte",
            ) == stress
            and len(stress_stream["base64"])
            == encoded_stream_byte_count(
                len(stress),
                "synthetic one-mebibyte",
            ),
        )
        stress_archive = gzip.compress(
            stress,
            compresslevel=9,
            mtime=0,
        )
        accept(
            "stream-deterministic-lossless-one-mib-gzip-in-memory",
            stress_archive
            == gzip.compress(stress, compresslevel=9, mtime=0)
            and gzip.decompress(stress_archive) == stress,
        )
        compact_document = {
            "schema": SCHEMA + "-complete-baseline-report",
            "complete_baseline_process_stdout": stress_stream,
            "complete_baseline_process_stderr": capture_stream(
                b"",
                "synthetic empty stderr",
            ),
            "synthetic_marker": "no reference engine was executed",
        }
        compact_budget = validate_compact_report_document(
            compact_document,
        )
        accept(
            "prove-exact-reversible-single-stream-report-size",
            compact_budget["complete_report_bytes"]
            == len(canonical(compact_document))
            and compact_budget["metadata_bytes"]
            <= MAX_COMPACT_REPORT_METADATA_BYTES
            and compact_budget["encoded_process_stream_bytes"]
            == len(stress_stream["base64"]),
        )
        for name, excess in (
            ("negative", -1),
            ("bool", True),
            ("one-byte-over-96-mib", MAX_PROCESS_BYTES + 1),
        ):
            reject(
                "reject-" + name + "-genuine-process-stream-size",
                lambda excess=excess: validate_stream_byte_count(
                    excess,
                    "synthetic-boundary",
                ),
            )
        reject(
            "reject-one-byte-over-32-mib-compact-metadata",
            lambda: validate_compact_metadata_byte_count(
                MAX_COMPACT_REPORT_METADATA_BYTES + 1,
            ),
        )
        for duplicated in (
            "complete_baseline_result",
            "complete_decoded_baseline_process",
            "reference_a_records",
            "reference_b_records",
            "reference_a_process",
            "reference_b_process",
            "complete_decoded_candidate_process",
            "complete_candidate_result",
            "candidate_records",
            "baseline_records",
        ):
            reject(
                "reject-duplicated-compact-payload-" + duplicated,
                lambda duplicated=duplicated:
                validate_compact_report_document({
                    **compact_document,
                    duplicated: [],
                }),
            )
        failed_process = {
            "started": True,
            "pid": 83_001,
            "returncode": 1,
            "signal": None,
            "timed_out": False,
            "spawn_error": None,
            "stdout": b"partial reference controller evidence\n",
            "stderr": b"bounded source-only synthetic traceback\n",
        }
        unknown_baseline = observation_failure_document(
            ObservationFailure(
                "synthetic previous oversized-publication failure",
                mode="baseline",
                process=failed_process,
                report=None,
            )
        )
        accept(
            "preserve-started-baseline-pid-and-never-forge-unknown-workers",
            unknown_baseline["actual_baseline_controller_invocations"] == 1
            and unknown_baseline["actual_process_pid"] == 83_001
            and unknown_baseline["actual_reference_workers"] == "UNKNOWN"
            and unknown_baseline["reference_outcomes_known"] is False
            and decode_stream(
                unknown_baseline["complete_actual_process_stdout"],
                "synthetic failed stdout",
            ) == failed_process["stdout"]
            and decode_stream(
                unknown_baseline["complete_actual_process_stderr"],
                "synthetic failed stderr",
            ) == failed_process["stderr"]
            and unknown_baseline["preserved_previous_failure_sha256"]
            == PRESERVED_PREVIOUS_FAILURE_SHA256,
        )
        unknown_candidate = observation_failure_document(
            ObservationFailure(
                "synthetic native post-invocation failure",
                mode="candidate",
                process={**failed_process, "pid": 83_002},
                report=None,
            )
        )
        accept(
            "preserve-started-candidate-with-truthful-unknown-outcomes",
            unknown_candidate["actual_candidate_process_invocations"] == 1
            and unknown_candidate["actual_process_pid"] == 83_002
            and unknown_candidate["actual_candidate_workers"] == "UNKNOWN"
            and unknown_candidate["candidate_outcomes_known"] is False,
        )
        for name, poisoned in (
            (
                "zero-baseline-worker-after-invocation",
                {
                    **unknown_baseline,
                    "actual_reference_workers": 0,
                },
            ),
            (
                "zero-candidate-after-invocation",
                {
                    **unknown_candidate,
                    "actual_candidate_workers": 0,
                },
            ),
            (
                "hidden-process-invocation",
                {
                    **unknown_baseline,
                    "actual_process_invocations": 0,
                },
            ),
            (
                "forged-known-reference-outcome",
                {
                    **unknown_baseline,
                    "reference_outcomes_known": True,
                },
            ),
            (
                "forged-known-candidate-outcome",
                {
                    **unknown_candidate,
                    "candidate_outcomes_known": True,
                },
            ),
            (
                "hidden-partial-publication",
                {
                    **unknown_baseline,
                    "published_evidence_file_count": 1,
                },
            ),
            (
                "substituted-preserved-v1-failure",
                {
                    **unknown_baseline,
                    "preserved_previous_failure_sha256": "ef" * 32,
                },
            ),
        ):
            reject(
                "reject-" + name,
                lambda poisoned=poisoned:
                validate_observation_failure_document(poisoned),
            )
        source_oracle = SyntheticSubstitutionOracle()
        source_audit = SyntheticFromScratchAudit()
        compact_baseline, frozen_owners = synthetic_complete_baseline(
            matrix,
            records,
            "de" * 32,
            source_oracle,
        )
        compact_baseline_budget = validate_compact_report_document(
            compact_baseline,
        )
        accept(
            "retain-complete-5120-case-six-owner-single-stream-baseline",
            compact_baseline["actual_reference_workers"] == 2
            and compact_baseline["validated_reference_a_case_count"]
            == CASE_COUNT
            and compact_baseline["validated_reference_b_case_count"]
            == CASE_COUNT
            and compact_baseline["source_closure_before"]
            == frozen_owners
            and len(frozen_owners) == 6
            and compact_baseline_budget["complete_report_bytes"]
            == len(canonical(compact_baseline))
            and "complete_baseline_result" not in compact_baseline
            and "reference_a_records" not in compact_baseline
            and "reference_b_records" not in compact_baseline,
        )
        accept(
            "freeze-three-complete-independently-owned-native-families",
            all(family_spec(name).name == name for name in FAMILIES),
        )
        accept(
            "permit-only-c-own-engine-and-bridge-alias",
            all(
                (
                    family_spec(name).engine_relative
                    == family_spec(name).bridge_relative
                ) is (name == "c")
                for name in FAMILIES
            ),
        )
        for family in FAMILIES:
            pins = synthetic_owner_pins(family)
            spec = family_spec(family)
            integration_pins = make_owner_pins(
                family,
                pins.recorder,
                pins.adapter,
                pins.engine,
                pins.bridge,
                [
                    relative + "=" + pinned
                    for relative, pinned in pins.owned_sources
                ],
                make_baseline_pins(
                    pins.baseline.label,
                    pins.baseline.receipt,
                    pins.baseline.archive,
                    records_sha256,
                ),
            )
            integration_receipt = synthetic_complete_receipt(
                integration_pins,
                compact_baseline,
            )
            derived_reference = validate_archived_baseline(
                compact_baseline,
                integration_pins,
                source_oracle,
                matrix,
                integration_receipt,
            )
            accept(
                "rederive-" + family
                + "-complete-signed-baseline-without-payload-duplication",
                revalidate_derived_baseline(
                    derived_reference,
                    integration_pins,
                    source_oracle,
                    matrix,
                    integration_receipt,
                ) == derived_reference
                and "complete_baseline_result" in derived_reference
                and "complete_baseline_result" not in compact_baseline
                and derived_reference["reference_a_records"] == records
                and derived_reference["reference_b_records"] == records,
            )
            if family == "rust":
                for field in (
                    "complete_baseline_result",
                    "reference_a_records",
                    "reference_b_records",
                    "reference_a_process",
                    "reference_b_process",
                ):
                    reject(
                        "reject-omitted-signed-derived-baseline-" + field,
                        lambda field=field:
                        revalidate_derived_baseline(
                            {
                                key: original
                                for key, original
                                in derived_reference.items()
                                if key != field
                            },
                            integration_pins,
                            source_oracle,
                            matrix,
                            integration_receipt,
                        ),
                    )
                    original = derived_reference[field]
                    forged = (
                        {**original, "synthetic_forgery": True}
                        if type(original) is dict
                        else list(reversed(original))
                    )
                    reject(
                        "reject-forged-signed-derived-baseline-" + field,
                        lambda field=field, forged=forged:
                        revalidate_derived_baseline(
                            {**derived_reference, field: forged},
                            integration_pins,
                            source_oracle,
                            matrix,
                            integration_receipt,
                        ),
                    )
                reject(
                    "reject-enriched-in-memory-reference-as-compact-archive",
                    lambda: validate_archived_baseline(
                        derived_reference,
                        integration_pins,
                        source_oracle,
                        matrix,
                        integration_receipt,
                    ),
                )
                reject(
                    "reject-extra-unsigned-compact-baseline-field",
                    lambda: validate_archived_baseline(
                        {
                            **compact_baseline,
                            "synthetic_unsigned_forgery": True,
                        },
                        integration_pins,
                        source_oracle,
                        matrix,
                        integration_receipt,
                    ),
                )
                reject(
                    "reject-omitted-authenticated-a803-failure-source-owner",
                    lambda: validate_frozen_source_owners(
                        {
                            key: original
                            for key, original in frozen_owners.items()
                            if key != "preserved_previous_failure"
                        },
                        integration_pins.recorder,
                    ),
                )
                reject(
                    "reject-forged-authenticated-a803-failure-source-owner",
                    lambda: validate_frozen_source_owners(
                        {
                            **frozen_owners,
                            "preserved_previous_failure": {
                                **frozen_owners[
                                    "preserved_previous_failure"
                                ],
                                "sha256": "ef" * 32,
                            },
                        },
                        integration_pins.recorder,
                    ),
                )
            worker, owned_closure = synthetic_complete_candidate_worker(
                integration_pins,
                matrix,
                records,
                integration_receipt,
                source_oracle,
                source_audit,
                pid=84_001 + tuple(FAMILIES).index(family),
            )
            candidate_process = {
                "started": True,
                "pid": worker["pid"],
                "returncode": 0,
                "signal": None,
                "timed_out": False,
                "spawn_error": None,
                "stdout": canonical(worker),
                "stderr": b"",
            }
            candidate_report = build_candidate_report(
                integration_pins,
                "trial-v1",
                candidate_process,
                matrix,
                integration_receipt,
                derived_reference,
                owned_closure,
                owned_closure,
                source_oracle,
                source_audit,
            )
            candidate_budget = validate_compact_report_document(
                candidate_report,
            )
            accept(
                "pass-complete-" + family
                + "-5120-case-signed-baseline-to-native-report",
                candidate_report["status"] == "PASS"
                and candidate_report["validated_baseline_record_count"]
                == CASE_COUNT
                and candidate_report["validated_candidate_record_count"]
                == CASE_COUNT
                and candidate_report["mismatch_count"] == 0
                and candidate_report["actual_candidate_workers"] == 1
                and candidate_report["actual_method_guard_checks"]
                == 2 * CASE_COUNT
                and candidate_report[
                    "actual_warning_registry_guard_checks"
                ] == 2 * CASE_COUNT
                and len(worker["source_provenance"]) == 6
                and candidate_budget["complete_report_bytes"]
                == len(canonical(candidate_report))
                and "candidate_records" not in candidate_report
                and "reference_a_records" not in candidate_report,
            )
            mismatch_worker, _ = synthetic_complete_candidate_worker(
                integration_pins,
                matrix,
                altered,
                integration_receipt,
                source_oracle,
                source_audit,
                pid=85_001 + tuple(FAMILIES).index(family),
            )
            mismatch_report = build_candidate_report(
                integration_pins,
                "trial-v1",
                {
                    **candidate_process,
                    "pid": mismatch_worker["pid"],
                    "stdout": canonical(mismatch_worker),
                },
                matrix,
                integration_receipt,
                derived_reference,
                owned_closure,
                owned_closure,
                source_oracle,
                source_audit,
            )
            accept(
                "retain-every-" + family
                + "-real-shaped-5120-case-substitution-mismatch",
                mismatch_report["status"] == "FAIL"
                and mismatch_report["mismatch_count"] == 2
                and mismatch_report["all_mismatches"] == mismatch
                and mismatch_report["mismatch_evidence_sha256"]
                == mismatch_sha256
                and mismatch_report["all_mismatches_preserved"] is True
                and mismatch_report["validated_candidate_record_count"]
                == CASE_COUNT,
            )
            accept(
                "pin-all-" + family + "-source-native-and-lockfile-owners",
                isinstance(pins, OwnerPins),
            )
            accept(
                "enforce-all-" + family + "-native-no-delegation-guards",
                validate_guard(synthetic_guard(spec), spec),
            )
            receipt = synthetic_baseline_receipt(pins)
            accept(
                "authenticate-complete-" + family
                + "-two-reference-baseline-receipt",
                validate_baseline_receipt(receipt, pins) == receipt,
            )
            report, receipt_path = approved_paths(
                "candidate", "trial-v1", family,
            )
            accept(
                "isolate-" + family + "-lossless-report-and-receipt-paths",
                report.endswith(".json.gz")
                and receipt_path.endswith("-publication-receipt.json")
                and "/" + family + "-substitution-buffer-semantics-v1-"
                in report,
            )
            raw = [
                path + "=" + source
                for path, source in pins.owned_sources
            ]
            reject(
                "reject-" + family + "-omitted-owned-source",
                lambda pins=pins, raw=raw: make_owner_pins(
                    pins.family,
                    pins.recorder,
                    pins.adapter,
                    pins.engine,
                    pins.bridge,
                    raw[:-1],
                    pins.baseline,
                ),
            )
            reject(
                "reject-" + family + "-duplicate-owned-source",
                lambda pins=pins, raw=raw: make_owner_pins(
                    pins.family,
                    pins.recorder,
                    pins.adapter,
                    pins.engine,
                    pins.bridge,
                    [*raw, raw[0]],
                    pins.baseline,
                ),
            )
            reject(
                "reject-" + family + "-substituted-adapter",
                lambda pins=pins, raw=raw: make_owner_pins(
                    pins.family,
                    pins.recorder,
                    "ef" * 32,
                    pins.engine,
                    pins.bridge,
                    raw,
                    pins.baseline,
                ),
            )
            wrong_bridge = (
                pins.engine if family != "c" else "ef" * 32
            )
            reject(
                "reject-" + family + "-cross-family-native-alias",
                lambda pins=pins, raw=raw, wrong_bridge=wrong_bridge:
                make_owner_pins(
                    pins.family,
                    pins.recorder,
                    pins.adapter,
                    pins.engine,
                    wrong_bridge,
                    raw,
                    pins.baseline,
                ),
            )
            guard = synthetic_guard(spec)
            for field in GUARD_TRUE_FIELDS:
                reject(
                    "reject-" + family + "-lost-" + field,
                    lambda guard=guard, field=field, spec=spec:
                    validate_guard({**guard, field: False}, spec),
                )
            for field in (
                "actual_method_guard_checks",
                "actual_warning_registry_guard_checks",
            ):
                reject(
                    "reject-" + family + "-short-" + field,
                    lambda guard=guard, field=field, spec=spec:
                    validate_guard(
                        {**guard, field: 2 * CASE_COUNT - 1},
                        spec,
                    ),
                )
            reject(
                "reject-" + family + "-foreign-ffi-policy",
                lambda guard=guard, spec=spec: validate_guard(
                    {
                        **guard,
                        "owned_native_ffi_allowed": not spec.owned_ctypes,
                    },
                    spec,
                ),
            )
            reject(
                "reject-" + family + "-substituted-trusted-ffi-source",
                lambda guard=guard, spec=spec: validate_guard(
                    {
                        **guard,
                        "trusted_stdlib_ctypes_source_sha256": "ef" * 32,
                    },
                    spec,
                ),
            )
            poisons = (
                ("status", "FAIL"),
                ("baseline_result_status", "FAIL"),
                ("previous_recorder_sha256", "ef" * 32),
                ("preserved_previous_failure_sha256", "ef" * 32),
                ("published_seed", PUBLISHED_SEED - 1),
                ("published_seed_decimal", str(PUBLISHED_SEED - 1)),
                ("case_count", CASE_COUNT - 1),
                ("cohort_count", len(COHORTS) - 1),
                ("variants_per_cohort", VARIANTS_PER_COHORT - 1),
                ("cohorts", list(COHORTS[:-1])),
                ("apis", list(APIS[:-1])),
                ("simple_buffer_flag", 1),
                ("full_readonly_buffer_flag", 0),
                (
                    "maximum_raw_process_stream_bytes",
                    MAX_PROCESS_BYTES + 1,
                ),
                (
                    "maximum_encoded_process_stream_bytes",
                    MAX_ENCODED_PROCESS_STREAM_BYTES + 1,
                ),
                (
                    "maximum_compact_report_metadata_bytes",
                    MAX_COMPACT_REPORT_METADATA_BYTES + 1,
                ),
                (
                    "maximum_compact_report_bytes",
                    MAX_COMPACT_REPORT_BYTES + 1,
                ),
                ("baseline_records_sha256", "ef" * 32),
                ("report_sha256", "ef" * 32),
                ("report_relative", "experiments/foreign.json.gz"),
                ("baseline_reference_pids", [82_001, 82_001]),
                ("actual_reference_workers", 1),
                ("actual_candidate_workers", 1),
                ("actual_candidate_imports", 1),
                ("actual_baseline_controller_invocations", 2),
                ("source_closure_unchanged", False),
                ("report_compression", "none"),
                ("report_file_fsync_completed", False),
                ("report_directory_fsync_completed", False),
                ("report_atomic_no_overwrite_link", False),
                ("report_complete_readback_verified", False),
                ("approved_fresh_path_count", 1),
                ("fresh_paths_checked_before_baseline", False),
                ("clock_samples", 1),
                ("timing_trials_run", 1),
                ("benchmark_files_read", 1),
                ("hidden_cases_read", 1),
                ("performance", "MEASURED"),
                ("candidate_qualified_for_hidden_benchmark", True),
                ("final_winner_selected", True),
            )
            for field, poison in poisons:
                reject(
                    "reject-" + family + "-baseline-receipt-" + field,
                    lambda receipt=receipt, field=field,
                    poison=poison, pins=pins: validate_baseline_receipt(
                        {**receipt, field: poison},
                        pins,
                    ),
                )

        for name, value in (
            ("empty", ""),
            ("uppercase", "ABC"),
            ("escaping", "../x"),
            ("slash", "a/b"),
            ("backslash", "a\\b"),
            ("double-dash", "a--b"),
            ("leading-dash", "-a"),
            ("trailing-dash", "a-"),
            ("dot", "a.b"),
            ("nul", "a\x00b"),
            ("bool", True),
            ("oversize", "a" * 65),
        ):
            reject(
                "reject-" + name + "-run-label",
                lambda value=value: validate_label(value),
            )
        for name, value in (
            ("empty", ""),
            ("dot", "."),
            ("parent", "../x"),
            ("absolute", "/tmp/x"),
            ("double-slash", "a//b"),
            ("backslash", "a\\b"),
            ("nul", "a\x00b"),
        ):
            reject(
                "reject-" + name + "-owner-path",
                lambda value=value: safe_parts(value),
            )
        for name, value in (
            ("short", "ab"),
            ("uppercase", "AB" * 32),
            ("constant", "0" * 64),
            ("nonhex", "g1" * 32),
            ("bool", True),
            ("none", None),
        ):
            reject(
                "reject-" + name + "-owner-digest",
                lambda value=value: validate_digest(value, "synthetic"),
            )
        for name, mutation in (
            ("truncated-first", lambda xs: xs[1:]),
            ("truncated-last", lambda xs: xs[:-1]),
            ("reordered", lambda xs: list(reversed(xs))),
            ("duplicate", lambda xs: [xs[0], *xs[1:-1], xs[0]]),
        ):
            reject(
                "reject-" + name + "-frozen-substitution-matrix",
                lambda mutation=mutation: validate_matrix(mutation(matrix)),
            )
        for field, poison in (
            ("case", "forged.case"),
            ("cohort", "forged-cohort"),
            ("variant", -1),
            ("seed", PUBLISHED_SEED - 1),
            ("api", "re.search"),
            ("flags", 512),
            ("count", -1),
            ("pos", 11),
            ("endpos", -1),
            ("replacement_style", "foreign"),
            ("callback_raises", "yes"),
        ):
            def poison_matrix(
                field: str = field,
                poison: Any = poison,
            ) -> list[dict[str, Any]]:
                altered = list(matrix)
                altered[0] = {**matrix[0], field: poison}
                return validate_matrix(altered)
            reject(
                "reject-forged-matrix-" + field,
                poison_matrix,
            )
        reject(
            "reject-rounded-53-bit-json-substitution-seed",
            lambda: build_frozen_matrix(int(float(PUBLISHED_SEED))),
        )
        reject(
            "reject-float-64-bit-substitution-seed",
            lambda: build_frozen_matrix(float(PUBLISHED_SEED)),
        )
        for name, mutation in (
            ("truncate", lambda xs: xs[:-1]),
            ("reorder", lambda xs: list(reversed(xs))),
            ("duplicate", lambda xs: [xs[0], *xs[1:-1], xs[0]]),
        ):
            reject(
                "reject-" + name + "-complete-candidate-records",
                lambda mutation=mutation: validate_candidate_records(
                    matrix,
                    mutation(records),
                    records_sha256,
                ),
            )
        for field, poison in (
            ("case", "forged"),
            ("cohort", "forged"),
            ("api", "foreign.api"),
        ):
            def poison_record(
                field: str = field,
                poison: Any = poison,
            ) -> list[dict[str, Any]]:
                altered = list(records)
                altered[0] = {**records[0], field: poison}
                return validate_candidate_records(
                    matrix,
                    altered,
                    records_sha256,
                )
            reject(
                "reject-forged-candidate-record-" + field,
                poison_record,
            )
        sample = records[0]["outcome"]
        for field in (
            "status",
            "stage",
            "value",
            "exception",
            "events",
            "callbacks",
            "warnings",
            "subject_after",
            "replacement_after",
            "subject_active_exports",
            "replacement_active_exports",
            "count_requested",
            "pos_requested",
            "endpos_requested",
        ):
            def omit_outcome(
                field: str = field,
            ) -> dict[str, Any]:
                forged = dict(sample)
                forged.pop(field)
                return validate_candidate_outcome(forged)
            reject(
                "reject-hidden-substitution-outcome-" + field,
                omit_outcome,
            )
        for name, poisoned in (
            (
                "reordered-nested-release",
                [
                    *nested[:4],
                    nested[6],
                    nested[5],
                    nested[4],
                    *nested[7:],
                ],
            ),
            ("truncated-nested-release", nested[:-2]),
            (
                "substituted-full-readonly-flag",
                [
                    *nested[:3],
                    {**nested[3], "flags": SIMPLE_BUFFER_FLAG},
                    *nested[4:],
                ],
            ),
            (
                "invalid-buffer-backing-hex",
                [
                    nested[0],
                    {
                        **nested[1],
                        "backing_before_hex": "GG",
                    },
                    *nested[2:],
                ],
            ),
            (
                "duplicate-nested-release",
                [
                    *nested[:-1],
                    synthetic_buffer_event(
                        "release", "subject", None, 0, 0,
                    ),
                    nested[-1],
                ],
            ),
        ):
            reject(
                "reject-" + name,
                lambda poisoned=poisoned: validate_substitution_events(
                    poisoned,
                    require_balanced=True,
                    expected_acquisition_flags=(0, 0, 284),
                ),
            )
        reject(
            "reject-forged-mutation-backing",
            lambda: validate_substitution_events(
                [
                    mutation[0],
                    {
                        **mutation[1],
                        "backing_after_hex": mutation[1]["backing_before_hex"],
                    },
                ],
                require_balanced=True,
            ),
        )
        reject(
            "reject-forged-exporter-custom-hash",
            lambda: validate_substitution_events(
                [{**hash_event, "hash_result": 1728}],
            ),
        )
        reject(
            "reject-hidden-failing-exporter",
            lambda: validate_substitution_events(
                [{**fail_event, "behavior": "stable"}],
            ),
        )
        for name, raw in (
            ("duplicate-json-key", b'{"a":1,"a":2}\n'),
            ("nan", b'{"a":NaN}\n'),
            ("positive-infinity", b'{"a":Infinity}\n'),
            ("negative-infinity", b'{"a":-Infinity}\n'),
            ("noncanonical-spacing", b'{"a": 1}\n'),
            ("missing-newline", b'{"a":1}'),
            ("trailing-document", b'{"a":1}\n{}\n'),
        ):
            reject(
                "reject-" + name + "-process-document",
                lambda raw=raw: decode_document(raw, "synthetic"),
            )
        for field, poison in (
            ("base64", "!!!"),
            ("bytes", len(fixture) + 1),
            ("sha256", "ef" * 32),
            ("complete", False),
        ):
            reject(
                "reject-forged-worker-stream-" + field,
                lambda field=field, poison=poison: decode_stream(
                    {**stream, field: poison},
                    "synthetic",
                ),
            )
        for family in ("python", "re", "regex", "pcre2", "other", None):
            reject(
                "reject-foreign-engine-family-" + str(family),
                lambda family=family: family_spec(family),
            )
        for mode, family in (
            ("baseline", "c"),
            ("candidate", "regex"),
            ("other", None),
        ):
            reject(
                "reject-foreign-evidence-mode-"
                + str(mode)
                + "-"
                + str(family),
                lambda mode=mode, family=family: approved_paths(
                    mode,
                    "trial-v1",
                    family,
                ),
            )

        def poison_gzip() -> bytes:
            corrupted = compressed[:-8] + bytes(
                (compressed[-8] ^ 1,)
            ) + compressed[-7:]
            return gzip.decompress(corrupted)

        reject("reject-corrupt-in-memory-gzip-crc", poison_gzip)
        reject(
            "block-real-file-read",
            lambda: builtins.open(SOURCE_ABSOLUTE, "rb"),
        )
        reject(
            "block-real-file-write",
            lambda: builtins.open("synthetic-forbidden", "wb"),
        )
        reject(
            "block-real-process",
            lambda: subprocess.Popen([PINNED_PYTHON]),
        )
        reject(
            "block-real-background-thread",
            lambda: threading.Thread(target=lambda: None).start(),
        )
        reject(
            "block-real-candidate-import",
            lambda: importlib.import_module("candidates.rust_candidate"),
        )
        reject(
            "block-real-dynamic-import",
            lambda: importlib.import_module("json"),
        )
        reject("block-real-clock", lambda: time.perf_counter_ns())
        reject("block-real-randomness", lambda: os.urandom(1))
        reject("block-real-garbage-collection", lambda: gc.collect())
        reject("block-real-directory-fsync", lambda: os.fsync(1))
        counts = dict(blocked.blocked)

    require(
        all(type(value) is int and value >= 0 for value in counts.values())
        and counts["file_reads"] == 1
        and counts["file_writes"] == 1
        and counts["processes"] == 1
        and counts["candidate_imports"] == 1
        and counts["dynamic_imports"] == 1
        and counts["clock_samples"] == 1
        and counts["garbage_collections"] == 1
        and counts["directory_syncs"] == 1
        and counts["randomness"] == 1
        and counts["threads"] == 1,
        "the source-only substitution effect boundary was bypassed",
    )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "a real candidate escaped synthetic substitution-only controls",
    )
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "previous_recorder_relative": PREVIOUS_RECORDER_RELATIVE,
        "previous_recorder_sha256": PREVIOUS_RECORDER_SHA256,
        "preserved_previous_failure_relative": (
            PRESERVED_PREVIOUS_FAILURE_RELATIVE
        ),
        "preserved_previous_failure_sha256": (
            PRESERVED_PREVIOUS_FAILURE_SHA256
        ),
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "cohorts": list(COHORTS),
        "apis": list(APIS),
        "simple_buffer_flag": SIMPLE_BUFFER_FLAG,
        "full_readonly_buffer_flag": FULL_READONLY_BUFFER_FLAG,
        **validate_compact_bounds(),
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_poison_count": len(rejected),
        "rejected_poisons": rejected,
        "source_only_boundary": counts,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }



def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Durably record frozen original substitution compatibility",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run only effect-blocked in-memory controls")
    modes.add_argument("--record-baseline", action="store_true",
                       help="publish exactly two isolated standard references")
    modes.add_argument("--record-candidate", action="store_true",
                       help="publish one guarded from-scratch candidate")
    modes.add_argument("--internal-candidate-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--label")
    parser.add_argument("--candidate", choices=tuple(FAMILIES))
    parser.add_argument("--recorder-source-sha256")
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--ownership-audit-source-sha256")
    parser.add_argument("--baseline-label")
    parser.add_argument("--baseline-receipt-sha256")
    parser.add_argument("--baseline-archive-sha256")
    parser.add_argument("--baseline-records-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    return parser.parse_args(arguments)


def make_cli_pins(options: argparse.Namespace) -> OwnerPins:
    require(validate_digest(options.oracle_source_sha256, "frozen substitution oracle")
            == ORACLE_SHA256
            and validate_digest(options.matrix_sha256, "frozen substitution matrix")
            == MATRIX_SHA256
            and validate_digest(options.ownership_audit_source_sha256,
                                "frozen V3 no-delegation audit") == AUDIT_SHA256,
            "explicitly pin the unchanged substitution oracle, matrix, and V3 audit")
    baseline = make_baseline_pins(
        options.baseline_label, options.baseline_receipt_sha256,
        options.baseline_archive_sha256, options.baseline_records_sha256,
    )
    return make_owner_pins(
        options.candidate, options.recorder_source_sha256,
        options.candidate_source_sha256, options.native_engine_sha256,
        options.native_bridge_sha256, options.owned_source_sha256,
        baseline,
    )


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(options.label is None and options.candidate is None
                    and options.recorder_source_sha256 is None
                    and options.oracle_source_sha256 is None
                    and options.matrix_sha256 is None
                    and options.ownership_audit_source_sha256 is None
                    and options.baseline_label is None
                    and options.baseline_receipt_sha256 is None
                    and options.baseline_archive_sha256 is None
                    and options.baseline_records_sha256 is None
                    and options.candidate_source_sha256 is None
                    and options.native_engine_sha256 is None
                    and options.native_bridge_sha256 is None
                    and options.owned_source_sha256 == [],
                    "source-only controls cannot select files or an engine")
            result = source_self_test()
        elif options.record_baseline:
            require(options.candidate is None
                    and options.ownership_audit_source_sha256 is None
                    and options.baseline_label is None
                    and options.baseline_receipt_sha256 is None
                    and options.baseline_archive_sha256 is None
                    and options.baseline_records_sha256 is None
                    and options.candidate_source_sha256 is None
                    and options.native_engine_sha256 is None
                    and options.native_bridge_sha256 is None
                    and options.owned_source_sha256 == [],
                    "a genuine standard baseline cannot select any candidate")
            result = record_baseline(
                options.recorder_source_sha256,
                options.oracle_source_sha256,
                options.matrix_sha256, options.label,
            )
        else:
            pins = make_cli_pins(options)
            if options.internal_candidate_worker:
                require(options.label is None,
                        "an isolated candidate worker cannot publish evidence")
                result = execute_candidate_worker(pins)
            else:
                result = record_candidate(pins, options.label)
        sys.stdout.buffer.write(canonical(result))
        if result.get("status") in {"PASS", "OBSERVED"}:
            return 0
        return 1
    except ObservationFailure as error:
        sys.stdout.buffer.write(
            canonical(observation_failure_document(error))
        )
        return 1
    except (RecorderError, OSError, ValueError, TypeError,
            KeyError, OverflowError, EOFError, gzip.BadGzipFile) as error:
        failure = {
            "schema": SCHEMA + "-failure", "status": "FAIL",
            "error_type": type(error).__qualname__, "error": str(error),
            "actual_reference_workers": 0,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "workspace_files_written": 0, "evidence_files_created": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(failure))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
