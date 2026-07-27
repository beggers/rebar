#!/usr/bin/env python3
"""Freeze complete, deterministic CPython replacement and buffer semantics.

The 64 equally weighted cohorts preserve module and compiled ``sub``/``subn``,
``Match.expand``, text, bytes, bytearrays, contiguous and strided memoryviews,
released replacements, real nested PEP-688 exporters, custom hashes, callbacks,
capture groups, zero-width matches, windows, exact exceptions, and every
ordered acquisition and release.  ``--self-test`` is synthetic and cannot run
an engine, read or write a file, start a process, sample a clock, or inspect a
benchmark.  Only an explicitly pinned later ``--baseline`` may start two
genuine isolated standard-CPython reference workers.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import copy
import gc
import hashlib
import importlib
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
from collections.abc import Callable, Mapping, Sequence
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/independent_substitution_buffer_semantics_v1.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-substitution-buffer-semantics-v1"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/"
)
PINNED_STDLIB_SOURCES = types.MappingProxyType({
    "re": (
        "__init__.py",
        "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
    ),
    "re._compiler": (
        "_compiler.py",
        "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91",
    ),
    "re._parser": (
        "_parser.py",
        "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4",
    ),
    "re._constants": (
        "_constants.py",
        "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b",
    ),
})
V5_GUARD_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_GUARD_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
OWNERSHIP_AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
OWNERSHIP_AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
PUBLISHED_SEED = 0x5355_4253_4255_4631
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
MATRIX_SHA256 = (
    "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54"
)
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
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
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "_regex", "candidates", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "regex", "rebar",
    "rust_regex", "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class SubstitutionOracleError(Exception):
    """A complete frozen substitution obligation or reference was forged."""


class SourceOnlyError(SubstitutionOracleError):
    """A synthetic control attempted an external effect."""


class ReferenceWorkerFailure(SubstitutionOracleError):
    """Preserve a complete failing genuinely isolated reference worker."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


class ReplacementCallbackError(Exception):
    """A deterministic public replacement callback raised intentionally."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise SubstitutionOracleError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise SubstitutionOracleError("substitution evidence is not complete canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value)
    )


def checked_digest(value: Any, label: str) -> str:
    require(valid_digest(value), "an exact prospectively frozen SHA-256 is required: " + label)
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result, "duplicate JSON fields hide a mismatch")
        result[key] = value
    return result


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
        "a complete bounded reference stream is mandatory: " + label,
    )

    def reject_constant(_: str) -> Any:
        raise SubstitutionOracleError("nonfinite substitution evidence is forbidden")

    try:
        result = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (SubstitutionOracleError, TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise SubstitutionOracleError("invalid complete reference evidence: " + label) from error
    require(
        type(result) is dict and canonical(result) == raw,
        "reference evidence was truncated, reordered, extended, or substituted",
    )
    return result


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
        raise SubstitutionOracleError("a substitution payload has invalid hexadecimal") from error
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


def build_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and 0 <= seed < 1 << 64, "a genuine published 64-bit seed is required")
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
    checked_digest(expected_sha256, "prospectively frozen substitution case matrix")
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
    actual = build_matrix()
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
    return expected_sha256


class TrackedExporter:
    """A PEP-688 exporter retaining exact nested acquisition and release order."""

    __slots__ = ("backing", "behavior", "events", "role", "active")

    def __init__(
        self,
        payload: bytes,
        behavior: str,
        events: list[dict[str, Any]],
        role: str,
    ) -> None:
        require(
            type(payload) is bytes
            and behavior in {"stable", "mutate", "fail"}
            and type(events) is list
            and role in {"subject", "replacement"},
            "a genuine PEP-688 replacement exporter was forged",
        )
        self.backing = bytearray(payload)
        self.behavior = behavior
        self.events = events
        self.role = role
        self.active = 0

    def __buffer__(self, flags: int) -> memoryview:
        require(
            type(flags) is int and flags >= 0,
            "a genuine exact CPython PEP-688 acquisition flag is mandatory",
        )
        before = bytes(self.backing).hex()
        if self.behavior == "fail":
            self.events.append({
                "event": "acquire-error",
                "role": self.role,
                "flags": flags,
                "active_before": self.active,
                "active_after": self.active,
                "backing_before_hex": before,
                "backing_after_hex": before,
                "behavior": self.behavior,
            })
            raise BufferError("frozen substitution " + self.role + " exporter failure")
        previous = self.active
        self.active += 1
        self.events.append({
            "event": "acquire",
            "role": self.role,
            "flags": flags,
            "active_before": previous,
            "active_after": self.active,
            "backing_before_hex": before,
            "backing_after_hex": before,
            "behavior": self.behavior,
        })
        return memoryview(self.backing)

    def __release_buffer__(self, view: memoryview) -> None:
        require(
            type(view) is memoryview and self.active > 0,
            "a PEP-688 export was released without its exact original view",
        )
        before = bytes(self.backing).hex()
        if self.behavior == "mutate":
            replacement = b"!" * len(self.backing)
            require(len(replacement) == len(self.backing), "release must not resize live storage")
            self.backing[:] = replacement
        previous = self.active
        self.active -= 1
        self.events.append({
            "event": "release",
            "role": self.role,
            "flags": None,
            "active_before": previous,
            "active_after": self.active,
            "backing_before_hex": before,
            "backing_after_hex": bytes(self.backing).hex(),
            "behavior": self.behavior,
        })


class FixedHashExporter(TrackedExporter):
    __slots__ = ()

    def __hash__(self) -> int:
        self.events.append({
            "event": "hash",
            "role": self.role,
            "flags": None,
            "active_before": self.active,
            "active_after": self.active,
            "backing_before_hex": bytes(self.backing).hex(),
            "backing_after_hex": bytes(self.backing).hex(),
            "behavior": self.behavior,
            "hash_result": 1729,
        })
        return 1729


class UnhashableExporter(TrackedExporter):
    __slots__ = ()
    __hash__ = None


class FailingHashExporter(TrackedExporter):
    __slots__ = ()

    def __hash__(self) -> int:
        self.events.append({
            "event": "hash-error",
            "role": self.role,
            "flags": None,
            "active_before": self.active,
            "active_after": self.active,
            "backing_before_hex": bytes(self.backing).hex(),
            "backing_after_hex": bytes(self.backing).hex(),
            "behavior": self.behavior,
        })
        raise TypeError("frozen substitution replacement exporter hash failure")


def decode_payload(value: Mapping[str, Any]) -> str | bytes:
    validate_payload(value)
    if value["kind"] == "str":
        return value["value"]
    return bytes.fromhex(value["hex"])


def decode_carrier(
    value: Mapping[str, Any],
    events: list[dict[str, Any]],
    *,
    role: str,
) -> tuple[Any, TrackedExporter | None, list[memoryview]]:
    validate_carrier(value, role=role)
    payload = decode_payload(value["payload"])
    kind = value["kind"]
    if kind == "str":
        return payload, None, []
    if kind == "callable":
        return payload, None, []
    require(type(payload) is bytes, "a binary replacement carrier was substituted")
    start, stop, step = value["start"], value["stop"], value["step"]
    if kind == "bytes":
        return payload[start:stop:step], None, []
    if kind == "bytearray":
        return bytearray(payload[start:stop:step]), None, []
    if "memoryview" in kind:
        backing: bytes | bytearray = payload if value["readonly"] else bytearray(payload)
        actual = memoryview(backing)[start:stop:step]
        if value["released"]:
            actual.release()
        return actual, None, [actual]
    if value["hash_behavior"] == "fixed":
        exporter: TrackedExporter = FixedHashExporter(payload, value["behavior"], events, role)
    elif value["hash_behavior"] == "unhashable":
        exporter = UnhashableExporter(payload, value["behavior"], events, role)
    elif value["hash_behavior"] == "fail":
        exporter = FailingHashExporter(payload, value["behavior"], events, role)
    else:
        exporter = TrackedExporter(payload, value["behavior"], events, role)
    if value["wrapped"]:
        actual = memoryview(exporter)
        if value["readonly"]:
            readonly = actual.toreadonly()
            actual.release()
            actual = readonly
        return actual, exporter, [actual]
    return exporter, exporter, []


def normalize_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {"type": "none"}
    if type(value) is bool:
        return {"type": "bool", "value": value}
    if type(value) is int:
        return {"type": "int", "value": value}
    if type(value) is str:
        return {"type": "str", "value": value}
    if type(value) is bytes:
        return {"type": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"type": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        try:
            return {
                "type": "memoryview",
                "hex": value.tobytes().hex(),
                "readonly": value.readonly,
                "format": value.format,
                "itemsize": value.itemsize,
                "ndim": value.ndim,
                "shape": list(value.shape) if value.shape is not None else None,
                "strides": list(value.strides) if value.strides is not None else None,
                "contiguous": value.contiguous,
                "c_contiguous": value.c_contiguous,
                "f_contiguous": value.f_contiguous,
            }
        except ValueError as error:
            return {
                "type": "released-memoryview",
                "exception_module": type(error).__module__,
                "exception_type": type(error).__qualname__,
                "exception_args": normalize_value(error.args),
            }
    if isinstance(value, TrackedExporter):
        return {
            "type": "pep688-exporter",
            "role": value.role,
            "behavior": value.behavior,
            "backing_hex": bytes(value.backing).hex(),
            "active_exports": value.active,
            "hash_kind": (
                "fixed" if isinstance(value, FixedHashExporter)
                else "unhashable" if isinstance(value, UnhashableExporter)
                else "fail" if isinstance(value, FailingHashExporter)
                else "identity"
            ),
        }
    if type(value) in (tuple, list):
        return {
            "type": "tuple" if type(value) is tuple else "list",
            "items": [normalize_value(item) for item in value],
        }
    if type(value) is dict:
        pairs = [[normalize_value(key), normalize_value(item)] for key, item in value.items()]
        pairs.sort(key=lambda pair: canonical(pair[0]))
        return {"type": "dict", "items": pairs}
    raise SubstitutionOracleError(
        "a complete replacement-buffer value was omitted: " + type(value).__qualname__
    )


def validate_normalized_value(value: Any) -> None:
    require(type(value) is dict and type(value.get("type")) is str, "a strictly typed value is required")
    kind = value["type"]
    if kind == "none":
        require(set(value) == {"type"}, "a null substitution result was forged")
    elif kind in {"bool", "int", "str"}:
        exact = {"bool": bool, "int": int, "str": str}[kind]
        require(
            set(value) == {"type", "value"} and type(value.get("value")) is exact,
            "a substitution scalar lost its exact Python type",
        )
    elif kind in {"bytes", "bytearray"}:
        require(
            set(value) == {"type", "hex"} and type(value.get("hex")) is str,
            "a bytes replacement lost its original carrier type",
        )
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise SubstitutionOracleError("a substitution result hex is invalid") from error
        require(actual.hex() == value["hex"], "a substitution result hex is noncanonical")
    elif kind in {"tuple", "list"}:
        require(
            set(value) == {"type", "items"} and type(value.get("items")) is list,
            "a regex result lost its exact tuple/list type",
        )
        for item in value["items"]:
            validate_normalized_value(item)
    elif kind == "dict":
        require(
            set(value) == {"type", "items"} and type(value.get("items")) is list,
            "a substitution mapping was forged",
        )
        previous: bytes | None = None
        for pair in value["items"]:
            require(type(pair) is list and len(pair) == 2, "a mapping entry was omitted")
            validate_normalized_value(pair[0])
            validate_normalized_value(pair[1])
            current = canonical(pair[0])
            require(previous is None or previous < current, "a mapping key was repeated or reordered")
            previous = current
    elif kind == "memoryview":
        require(
            set(value) == {
                "type", "hex", "readonly", "format", "itemsize", "ndim",
                "shape", "strides", "contiguous", "c_contiguous", "f_contiguous",
            }
            and type(value.get("readonly")) is bool
            and type(value.get("format")) is str
            and type(value.get("itemsize")) is int
            and type(value.get("ndim")) is int
            and all(type(value.get(name)) is bool for name in (
                "contiguous", "c_contiguous", "f_contiguous",
            )),
            "a real memoryview shape, flags, or mutability was hidden",
        )
        require(type(value.get("hex")) is str, "a memoryview payload is mandatory")
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise SubstitutionOracleError("memoryview observation hex is invalid") from error
        require(actual.hex() == value["hex"], "memoryview observation hex is noncanonical")
        for name in ("shape", "strides"):
            current = value[name]
            require(
                current is None
                or (type(current) is list and all(type(part) is int for part in current)),
                "a genuine memoryview dimension was replaced",
            )
    elif kind == "released-memoryview":
        require(
            set(value) == {"type", "exception_module", "exception_type", "exception_args"}
            and type(value.get("exception_module")) is str
            and type(value.get("exception_type")) is str,
            "the exact genuine released-memoryview error was hidden",
        )
        validate_normalized_value(value["exception_args"])
    elif kind == "pep688-exporter":
        require(
            set(value) == {
                "type", "role", "behavior", "backing_hex", "active_exports", "hash_kind",
            }
            and value.get("role") in {"subject", "replacement"}
            and value.get("behavior") in {"stable", "mutate", "fail"}
            and value.get("hash_kind") in {"identity", "fixed", "unhashable", "fail"}
            and type(value.get("backing_hex")) is str
            and type(value.get("active_exports")) is int
            and value["active_exports"] >= 0,
            "a tracked substitution exporter was forged or leaked",
        )
        try:
            actual = bytes.fromhex(value["backing_hex"])
        except ValueError as error:
            raise SubstitutionOracleError("a tracked exporter payload is invalid") from error
        require(actual.hex() == value["backing_hex"], "a tracked exporter payload is noncanonical")
    else:
        raise SubstitutionOracleError("an unfrozen substitution result type was injected")


def normalize_error(error: BaseException, engine: Any) -> dict[str, Any]:
    public = getattr(engine, "error", None)
    if isinstance(public, type) and isinstance(error, public):
        return {
            "kind": "public-regex-error",
            "type": type(error).__qualname__,
            "args": normalize_value(error.args),
            "message": normalize_value(getattr(error, "msg", None)),
            "pattern": normalize_value(getattr(error, "pattern", None)),
            "position": normalize_value(getattr(error, "pos", None)),
            "line": normalize_value(getattr(error, "lineno", None)),
            "column": normalize_value(getattr(error, "colno", None)),
        }
    return {
        "kind": "ordinary-python-error",
        "module": type(error).__module__,
        "type": type(error).__qualname__,
        "message": str(error),
        "args": normalize_value(error.args),
    }


def validate_error(value: Any) -> None:
    require(type(value) is dict, "an exact public replacement exception is mandatory")
    if value.get("kind") == "ordinary-python-error":
        require(
            set(value) == {"kind", "module", "type", "message", "args"}
            and type(value.get("module")) is str
            and type(value.get("type")) is str
            and type(value.get("message")) is str,
            "a genuine Python exception class or module was concealed",
        )
        validate_normalized_value(value["args"])
        return
    require(
        value.get("kind") == "public-regex-error"
        and set(value) == {
            "kind", "type", "args", "message", "pattern", "position", "line", "column",
        }
        and type(value.get("type")) is str,
        "a genuine Python PatternError and exact position were concealed",
    )
    for key in ("args", "message", "pattern", "position", "line", "column"):
        validate_normalized_value(value[key])


def normalize_match(match: Any, subject: Any, pattern: Any) -> dict[str, Any]:
    return {
        "pattern_is_expected": match.re is pattern,
        "string_is_subject": match.string is subject,
        "string": normalize_value(match.string),
        "group": normalize_value(match.group()),
        "groups": normalize_value(match.groups()),
        "groupdict": normalize_value(match.groupdict()),
        "regs": normalize_value(match.regs),
        "lastindex": normalize_value(match.lastindex),
        "lastgroup": normalize_value(match.lastgroup),
        "pos": normalize_value(match.pos),
        "endpos": normalize_value(match.endpos),
    }


def validate_match(value: Any) -> None:
    require(
        type(value) is dict
        and set(value) == {
            "pattern_is_expected", "string_is_subject", "string", "group", "groups",
            "groupdict", "regs", "lastindex", "lastgroup", "pos", "endpos",
        }
        and value.get("pattern_is_expected") is True
        and value.get("string_is_subject") is True,
        "a callback or retained match borrowed a foreign regex object",
    )
    for key in (
        "string", "group", "groups", "groupdict", "regs", "lastindex",
        "lastgroup", "pos", "endpos",
    ):
        validate_normalized_value(value[key])


def normalize_warnings(observed: Sequence[Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for item in observed:
        require(
            isinstance(item.category, type)
            and isinstance(item.message, item.category),
            "a genuine original Python warning was substituted",
        )
        result.append({
            "category_module": item.category.__module__,
            "category": item.category.__qualname__,
            "message": str(item.message),
        })
    return result


def validate_events(
    events: Any,
    *,
    require_balanced: bool = False,
    expected_acquisition_flags: tuple[int, ...] | None = None,
) -> list[dict[str, Any]]:
    require(type(events) is list, "a complete ordered PEP-688 event ledger is mandatory")
    active = {"subject": 0, "replacement": 0}
    ownership_stack: list[str] = []
    acquisition_flags: list[int] = []
    for record in events:
        require(
            type(record) is dict and type(record.get("event")) is str,
            "an exact ordered buffer acquisition event was hidden",
        )
        kind = record["event"]
        if kind == "phase":
            require(
                set(record) == {"event", "name"}
                and type(record.get("name")) is str
                and bool(record["name"]),
                "a genuine substitution phase was forged",
            )
            continue
        if kind == "callback":
            require(
                set(record) == {"event", "index", "match", "raises"}
                and type(record.get("index")) is int
                and record["index"] >= 0
                and type(record.get("raises")) is bool,
                "a genuine replacement callback and ordering was forged",
            )
            validate_match(record["match"])
            continue
        required = {
            "event", "role", "flags", "active_before", "active_after",
            "backing_before_hex", "backing_after_hex", "behavior",
        }
        expected_keys = required | ({"hash_result"} if kind == "hash" else set())
        require(
            kind in {"acquire", "acquire-error", "release", "hash", "hash-error"}
            and set(record) == expected_keys
            and record.get("role") in active
            and type(record.get("active_before")) is int
            and type(record.get("active_after")) is int
            and record["active_before"] >= 0
            and record["active_after"] >= 0
            and type(record.get("backing_before_hex")) is str
            and type(record.get("backing_after_hex")) is str
            and record.get("behavior") in {"stable", "mutate", "fail"},
            "a nested buffer flag, hash, storage, or exporter owner was forged",
        )
        for key in ("backing_before_hex", "backing_after_hex"):
            try:
                actual = bytes.fromhex(record[key])
            except ValueError as error:
                raise SubstitutionOracleError("a genuine buffer event contains invalid hex") from error
            require(actual.hex() == record[key], "a genuine buffer event hex is noncanonical")
        role = record["role"]
        require(record["active_before"] == active[role], "a nested exporter acquisition was reordered")
        if kind == "acquire":
            require(
                type(record.get("flags")) is int
                and record["flags"] in {SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG}
                and record["behavior"] != "fail"
                and record["active_after"] == active[role] + 1
                and record["backing_after_hex"] == record["backing_before_hex"],
                "a genuine SIMPLE or FULL buffer acquisition was forged",
            )
            ownership_stack.append(role)
            acquisition_flags.append(record["flags"])
            active[role] += 1
        elif kind == "acquire-error":
            require(
                type(record.get("flags")) is int
                and record["flags"] in {SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG}
                and record["behavior"] == "fail"
                and record["active_after"] == active[role]
                and record["backing_after_hex"] == record["backing_before_hex"],
                "a genuine failing PEP-688 acquisition was hidden",
            )
        elif kind == "release":
            require(
                record.get("flags") is None
                and active[role] > 0
                and record["active_after"] == active[role] - 1
                and bool(ownership_stack)
                and ownership_stack[-1] == role,
                "a nested buffer release was leaked, repeated, or reordered",
            )
            if record["behavior"] == "mutate":
                previous = bytes.fromhex(record["backing_before_hex"])
                require(
                    record["backing_after_hex"] == (b"!" * len(previous)).hex(),
                    "a mutating exporter did not preserve exact equal-length storage",
                )
            else:
                require(
                    record["backing_after_hex"] == record["backing_before_hex"],
                    "a stable exporter silently mutated original storage",
                )
            ownership_stack.pop()
            active[role] -= 1
        elif kind == "hash":
            require(
                record.get("flags") is None
                and record["active_after"] == active[role]
                and type(record.get("hash_result")) is int
                and record["hash_result"] == 1729,
                "an exact deterministic custom exporter hash was forged",
            )
        else:
            require(
                record.get("flags") is None
                and record["active_after"] == active[role],
                "a genuine custom hash exception was hidden",
            )
    require(type(require_balanced) is bool, "an exact buffer-balance policy is mandatory")
    if expected_acquisition_flags is not None:
        require(
            type(expected_acquisition_flags) is tuple
            and all(type(flag) is int for flag in expected_acquisition_flags)
            and tuple(acquisition_flags) == expected_acquisition_flags,
            "the exact nested SIMPLE, SIMPLE, FULL-READONLY acquisition flags changed",
        )
    if require_balanced:
        require(
            all(count == 0 for count in active.values()) and not ownership_stack,
            "a complete nested PEP-688 acquisition or release was omitted",
        )
    return events


def execute_case(case: Mapping[str, Any], engine: Any) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    callbacks: list[dict[str, Any]] = []
    views: list[memoryview] = []
    subject: Any = None
    replacement: Any = None
    subject_tracker: TrackedExporter | None = None
    replacement_tracker: TrackedExporter | None = None
    stage = "materialize"
    status = "raise"
    observed_value: dict[str, Any] | None = None
    observed_error: dict[str, Any] | None = None
    warning_results: list[dict[str, str]] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            events.append({"event": "phase", "name": "materialize-start"})
            pattern = decode_payload(case["pattern"])
            subject, subject_tracker, subject_views = decode_carrier(
                case["subject"], events, role="subject",
            )
            views.extend(subject_views)
            replacement, replacement_tracker, template_views = decode_carrier(
                case["replacement"], events, role="replacement",
            )
            views.extend(template_views)
            events.append({"event": "phase", "name": "materialize-complete"})
            stage = "compile"
            compiled = engine.compile(pattern, case["flags"])

            def callback(match: Any) -> Any:
                observed = normalize_match(match, subject, compiled)
                entry = {
                    "event": "callback",
                    "index": len(callbacks),
                    "match": observed,
                    "raises": case["callback_raises"],
                }
                events.append(entry)
                callbacks.append(copy.deepcopy(entry))
                if case["callback_raises"]:
                    raise ReplacementCallbackError("frozen substitution callback failure")
                value = decode_payload(case["replacement"]["payload"])
                return value

            selected = callback if case["replacement_style"] in {"callable", "callable-error"} else replacement
            stage = case["api"]
            events.append({"event": "phase", "name": "operation-start"})
            if stage == "module.sub":
                actual = engine.sub(
                    pattern, selected, subject,
                    count=case["count"], flags=case["flags"],
                )
            elif stage == "module.subn":
                actual = engine.subn(
                    pattern, selected, subject,
                    count=case["count"], flags=case["flags"],
                )
            elif stage == "pattern.sub":
                actual = compiled.sub(selected, subject, count=case["count"])
            elif stage == "pattern.subn":
                actual = compiled.subn(selected, subject, count=case["count"])
            elif stage == "match.expand":
                if case["endpos"] is None:
                    match = compiled.search(subject, case["pos"])
                else:
                    match = compiled.search(subject, case["pos"], case["endpos"])
                actual = None if match is None else match.expand(selected)
            else:
                raise SubstitutionOracleError("an unfrozen substitution API was injected")
            observed_value = normalize_value(actual)
            status = "return"
            events.append({"event": "phase", "name": "operation-return"})
        except SubstitutionOracleError:
            raise
        except Exception as error:
            observed_error = normalize_error(error, engine)
            events.append({"event": "phase", "name": "operation-raise"})
        finally:
            for view in reversed(views):
                try:
                    view.release()
                except ValueError:
                    pass
            events.append({"event": "phase", "name": "cleanup-complete"})
            warning_results = normalize_warnings(caught)
    result = {
        "status": status,
        "stage": stage,
        "value": observed_value,
        "exception": observed_error,
        "events": copy.deepcopy(events),
        "callbacks": copy.deepcopy(callbacks),
        "warnings": warning_results,
        "subject_after": normalize_value(subject),
        "replacement_after": normalize_value(replacement),
        "subject_active_exports": subject_tracker.active if subject_tracker is not None else 0,
        "replacement_active_exports": replacement_tracker.active if replacement_tracker is not None else 0,
        "count_requested": case["count"],
        "pos_requested": case["pos"],
        "endpos_requested": case["endpos"],
    }
    validate_outcome(result)
    return result


def validate_outcome(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {
            "status", "stage", "value", "exception", "events", "callbacks",
            "warnings", "subject_after", "replacement_after",
            "subject_active_exports", "replacement_active_exports",
            "count_requested", "pos_requested", "endpos_requested",
        }
        and value.get("status") in {"return", "raise"}
        and type(value.get("stage")) is str
        and type(value.get("callbacks")) is list
        and type(value.get("warnings")) is list
        and type(value.get("subject_active_exports")) is int
        and value["subject_active_exports"] >= 0
        and type(value.get("replacement_active_exports")) is int
        and value["replacement_active_exports"] >= 0
        and type(value.get("count_requested")) is int
        and type(value.get("pos_requested")) is int
        and (value.get("endpos_requested") is None or type(value.get("endpos_requested")) is int),
        "a complete substitution value, error, buffer ledger, or boundary was omitted",
    )
    validate_events(value["events"])
    for role, key in (
        ("subject", "subject_active_exports"),
        ("replacement", "replacement_active_exports"),
    ):
        acquisitions = sum(
            1 for event in value["events"]
            if event.get("event") == "acquire" and event.get("role") == role
        )
        releases = sum(
            1 for event in value["events"]
            if event.get("event") == "release" and event.get("role") == role
        )
        require(
            value[key] == acquisitions - releases,
            "a live or released nested exporter was omitted: " + role,
        )
    validate_normalized_value(value["subject_after"])
    validate_normalized_value(value["replacement_after"])
    if value["status"] == "return":
        require(value["exception"] is None, "a successful replacement hides an exception")
        validate_normalized_value(value["value"])
    else:
        require(value["value"] is None, "a failed replacement hides a return value")
        validate_error(value["exception"])
    for callback in value["callbacks"]:
        require(
            type(callback) is dict
            and set(callback) == {"event", "index", "match", "raises"}
            and callback.get("event") == "callback"
            and type(callback.get("index")) is int
            and callback["index"] >= 0
            and type(callback.get("raises")) is bool,
            "a complete callback result or exception was omitted",
        )
        validate_match(callback["match"])
    require(
        [event for event in value["events"] if event.get("event") == "callback"]
        == value["callbacks"],
        "a replacement callback was removed from its exact buffer-event ordering",
    )
    for warning in value["warnings"]:
        require(
            type(warning) is dict
            and set(warning) == {"category_module", "category", "message"}
            and all(type(warning.get(key)) is str for key in warning),
            "a genuine substitution warning was omitted",
        )
    return value


def verify_runtime(*, synthetic: bool = False) -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == SOURCE_ABSOLUTE,
        "use only the exact isolated pinned CPython substitution oracle",
    )
    if not synthetic:
        require(
            os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
            "the frozen replacement oracle or Python executable is a symlink",
        )


def read_pinned_file(
    absolute: str,
    expected: str,
    *,
    maximum: int,
    label: str,
) -> dict[str, Any]:
    checked_digest(expected, label)
    require(
        type(absolute) is str
        and os.path.isabs(absolute)
        and os.path.abspath(absolute) == absolute
        and os.path.realpath(absolute) == absolute
        and type(maximum) is int
        and 0 < maximum <= MAX_BINARY_BYTES,
        "an exact genuine pinned owner is mandatory: " + label,
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
            "a genuine standard source is not an owned bounded regular file: " + label,
        )
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk), "a pinned reference source was truncated")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "a pinned reference source has a hidden suffix")
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and hasher.hexdigest() == expected,
            "a frozen original regex source or policy changed: " + label,
        )
        return {
            "path": absolute,
            "sha256": expected,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        os.close(descriptor)


def verify_standard_modules(modules: Mapping[str, Any] | None = None) -> None:
    actual = sys.modules if modules is None else modules
    require(isinstance(actual, Mapping), "the actual reference module graph is mandatory")
    for name in actual:
        require(
            type(name) is str and name.partition(".")[0] not in FORBIDDEN_ENGINE_ROOTS,
            "a candidate, sibling, or external regex entered the standard-only reference",
        )


def authenticate_standard_reference(
    source_pin: str,
) -> tuple[Any, dict[str, dict[str, Any]]]:
    verify_runtime()
    owners = {
        "oracle": read_pinned_file(
            SOURCE_ABSOLUTE,
            source_pin,
            maximum=MAX_SOURCE_BYTES,
            label="frozen replacement-buffer oracle",
        ),
        "python": read_pinned_file(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            maximum=MAX_BINARY_BYTES,
            label="pinned stable CPython executable",
        ),
        "v5_guard": read_pinned_file(
            ROOT + "/" + V5_GUARD_RELATIVE,
            V5_GUARD_SHA256,
            maximum=MAX_SOURCE_BYTES,
            label="frozen original CPython V5 policy",
        ),
        "ownership_audit": read_pinned_file(
            ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
            maximum=MAX_SOURCE_BYTES,
            label="frozen no-delegation V3 ownership audit",
        ),
    }
    engine = importlib.import_module("re")
    for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items():
        absolute = PINNED_STDLIB_DIRECTORY + filename
        module = importlib.import_module(name)
        require(
            isinstance(module, types.ModuleType)
            and module.__name__ == name
            and getattr(module, "__file__", None) == absolute
            and os.path.realpath(absolute) == absolute,
            "a genuine standard CPython regex module was substituted: " + name,
        )
        owners[name] = read_pinned_file(
            absolute,
            source_hash,
            maximum=MAX_SOURCE_BYTES,
            label=name,
        )
    builtin = sys.modules.get("_sre")
    require(
        isinstance(builtin, types.ModuleType)
        and getattr(getattr(builtin, "__spec__", None), "origin", None) == "built-in"
        and engine.__name__ == "re"
        and getattr(engine.compile, "__module__", None) == "re",
        "the isolated genuine standard CPython regex engine was substituted",
    )
    verify_standard_modules()
    return engine, owners


def validate_source_owners(value: Any, source_pin: str) -> dict[str, dict[str, Any]]:
    expected: dict[str, tuple[str, str]] = {
        "oracle": (SOURCE_ABSOLUTE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "v5_guard": (ROOT + "/" + V5_GUARD_RELATIVE, V5_GUARD_SHA256),
        "ownership_audit": (
            ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
        ),
    }
    expected.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, source_hash)
        for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items()
    })
    require(
        type(value) is dict and set(value) == set(expected),
        "the complete stable CPython, regex, original-suite, and V3 ownership closure is mandatory",
    )
    for name, (path, source_hash) in expected.items():
        owner = value[name]
        require(
            type(owner) is dict
            and set(owner) == {"path", "sha256", "bytes", "device", "inode"}
            and owner.get("path") == path
            and owner.get("sha256") == source_hash
            and type(owner.get("bytes")) is int
            and owner["bytes"] > 0
            and type(owner.get("device")) is int
            and owner["device"] >= 0
            and type(owner.get("inode")) is int
            and owner["inode"] > 0,
            "a genuine pinned substitution reference owner was forged: " + name,
        )
    return value


def make_reference_guard(checks: int) -> dict[str, Any]:
    return {
        "candidate_import_count": 0,
        "external_regex_import_count": 0,
        "actual_method_guard_checks": checks,
        "required_method_guard_checks": 2 * CASE_COUNT,
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "future_candidate_guard_installed": False,
    }


def validate_reference_guard(value: Any) -> dict[str, Any]:
    expected = make_reference_guard(2 * CASE_COUNT)
    require(
        type(value) is dict and value == expected,
        "a complete no-delegation substitution reference guard was forged",
    )
    return value


def validate_records(
    matrix: list[dict[str, Any]],
    records: Any,
    records_pin: str,
) -> list[dict[str, Any]]:
    checked_digest(records_pin, "complete replacement-buffer observation vector")
    require(
        type(records) is list and len(records) == CASE_COUNT,
        "all 5,120 original replacement and nested-buffer outcomes are mandatory",
    )
    for case, row in zip(matrix, records, strict=True):
        require(
            type(row) is dict
            and set(row) == {"case", "cohort", "api", "outcome"}
            and row.get("case") == case["case"]
            and row.get("cohort") == case["cohort"]
            and row.get("api") == case["api"],
            "an ordered original substitution outcome was omitted or relabeled",
        )
        validate_outcome(row["outcome"])
    require(
        digest(records) == records_pin,
        "a complete original replacement observation vector was substituted",
    )
    return records


def observe_reference_worker(role: str, source_pin: str) -> dict[str, Any]:
    require(role in {"reference_a", "reference_b"}, "only genuine isolated references may run")
    checked_digest(source_pin, "prospectively frozen substitution oracle source")
    matrix = build_matrix()
    validate_matrix(matrix)
    engine, before = authenticate_standard_reference(source_pin)
    records: list[dict[str, Any]] = []
    checks = 0
    for case in matrix:
        verify_standard_modules()
        checks += 1
        try:
            outcome = execute_case(case, engine)
        finally:
            verify_standard_modules()
            checks += 1
        records.append({
            "case": case["case"],
            "cohort": case["cohort"],
            "api": case["api"],
            "outcome": outcome,
        })
    records_sha256 = digest(records)
    validate_records(matrix, records, records_sha256)
    after = authenticate_standard_reference(source_pin)[1]
    require(before == after, "a genuine reference owner changed during observation")
    document = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": os.getpid(),
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "case_count": CASE_COUNT,
        "records_sha256": records_sha256,
        "records": records,
        "source_owners": before,
        "reference_guard": make_reference_guard(checks),
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
    return validate_reference_worker(
        document,
        role=role,
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=document["pid"],
    )


def validate_reference_worker(
    value: Any,
    *,
    role: str,
    source_pin: str,
    matrix: list[dict[str, Any]],
    expected_pid: int,
) -> dict[str, Any]:
    require(
        role in {"reference_a", "reference_b"}
        and type(expected_pid) is int
        and expected_pid > 0,
        "a genuine independent substitution-reference role and PID are mandatory",
    )
    expected = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": expected_pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "case_count": CASE_COUNT,
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
    require(
        type(value) is dict
        and set(value) == set(expected) | {
            "records_sha256", "records", "source_owners", "reference_guard",
        },
        "a complete genuine substitution-reference worker was forged",
    )
    for field, original in expected.items():
        require(
            value.get(field) == original and type(value.get(field)) is type(original),
            "a genuine original substitution worker field changed: " + field,
        )
    validate_source_owners(value["source_owners"], source_pin)
    validate_reference_guard(value["reference_guard"])
    validate_records(matrix, value["records"], value["records_sha256"])
    return value


def encode_stream(value: Any) -> dict[str, Any]:
    require(
        type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
        "a complete bounded substitution-reference stream is mandatory",
    )
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": True,
    }


def decode_stream(value: Any, label: str) -> bytes:
    require(
        type(value) is dict
        and set(value) == {"base64", "bytes", "sha256", "complete"}
        and type(value.get("base64")) is str
        and type(value.get("bytes")) is int
        and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
        and valid_digest(value.get("sha256"))
        and value.get("complete") is True,
        "a complete reversible substitution-reference stream was hidden: " + label,
    )
    try:
        actual = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (TypeError, ValueError, UnicodeError) as error:
        raise SubstitutionOracleError("an isolated reference stream is invalid: " + label) from error
    require(
        len(actual) == value["bytes"]
        and hashlib.sha256(actual).hexdigest() == value["sha256"]
        and base64.b64encode(actual).decode("ascii") == value["base64"],
        "a complete isolated reference stream was truncated or substituted",
    )
    return actual


def validate_process_evidence(
    value: Any,
    worker: Mapping[str, Any],
    *,
    role: str,
) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {"role", "pid", "returncode", "stdout", "stderr"}
        and value.get("role") == role
        and type(value.get("pid")) is int
        and value["pid"] > 0
        and value["pid"] == worker.get("pid")
        and type(value.get("returncode")) is int
        and value["returncode"] == 0,
        "a genuine isolated original substitution-reference process was forged",
    )
    stdout = decode_stream(value["stdout"], role + " stdout")
    stderr = decode_stream(value["stderr"], role + " stderr")
    require(
        stdout == canonical(dict(worker)) and stderr == b"",
        "a reference process stream differs from its complete original worker",
    )
    return value


def run_isolated_reference(
    role: str,
    source_pin: str,
    matrix: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in {"reference_a", "reference_b"}, "only an exact isolated standard reference may run")
    arguments = [
        PINNED_PYTHON,
        "-I",
        "-B",
        SOURCE_ABSOLUTE,
        "--internal-reference-worker",
        "--role",
        role,
        "--oracle-source-sha256",
        source_pin,
        "--matrix-sha256",
        MATRIX_SHA256,
    ]
    try:
        process = subprocess.Popen(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            cwd=ROOT,
            env={
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            },
        )
        stdout, stderr = process.communicate()
    except (OSError, subprocess.SubprocessError) as error:
        raise ReferenceWorkerFailure(
            "a genuine isolated pinned CPython substitution reference could not start",
            {"role": role, "error_type": type(error).__qualname__, "error": str(error)},
        ) from error
    evidence = {
        "role": role,
        "pid": process.pid,
        "returncode": process.returncode,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    if process.returncode != 0 or stderr:
        raise ReferenceWorkerFailure(
            "a genuine isolated original substitution reference failed",
            evidence,
        )
    try:
        worker = validate_reference_worker(
            decode_canonical(stdout, role),
            role=role,
            source_pin=source_pin,
            matrix=matrix,
            expected_pid=process.pid,
        )
        validate_process_evidence(evidence, worker, role=role)
    except (SubstitutionOracleError, TypeError, ValueError, KeyError) as error:
        evidence["validation_error"] = {
            "type": type(error).__qualname__,
            "message": str(error),
        }
        raise ReferenceWorkerFailure(
            "complete original substitution-reference evidence was rejected",
            evidence,
        ) from error
    return worker, evidence


def validate_reference_pair(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    first_process: Mapping[str, Any],
    second_process: Mapping[str, Any],
    *,
    source_pin: str,
    matrix: list[dict[str, Any]],
) -> str:
    validate_reference_worker(
        first,
        role="reference_a",
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=first.get("pid"),
    )
    validate_reference_worker(
        second,
        role="reference_b",
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=second.get("pid"),
    )
    validate_process_evidence(first_process, first, role="reference_a")
    validate_process_evidence(second_process, second, role="reference_b")
    require(
        first["pid"] != second["pid"]
        and first["source_owners"] == second["source_owners"]
        and first["records_sha256"] == second["records_sha256"]
        and first["records"] == second["records"],
        "two genuinely independent standard substitution references disagree",
    )
    return first["records_sha256"]


def run_baseline(source_pin: str, matrix_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "prospectively frozen substitution oracle source")
    checked_digest(matrix_pin, "prospectively frozen substitution case matrix")
    require(matrix_pin == MATRIX_SHA256, "the frozen replacement matrix was substituted")
    matrix = build_matrix()
    validate_matrix(matrix, matrix_pin)
    _, before = authenticate_standard_reference(source_pin)
    first, first_process = run_isolated_reference("reference_a", source_pin, matrix)
    second, second_process = run_isolated_reference("reference_b", source_pin, matrix)
    records_sha256 = validate_reference_pair(
        first,
        second,
        first_process,
        second_process,
        source_pin=source_pin,
        matrix=matrix,
    )
    after = authenticate_standard_reference(source_pin)[1]
    require(
        before == after == first["source_owners"],
        "an exact original reference owner changed around substitution observation",
    )
    return {
        "schema": SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "baseline_records_sha256": records_sha256,
        "source_owners": before,
        "reference_a": dict(first),
        "reference_b": dict(second),
        "reference_a_process": dict(first_process),
        "reference_b_process": dict(second_process),
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


class SourceOnlyBoundary:
    """Reject actual filesystem, engines, workers, clocks, and randomness."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "file_reads": 0,
            "file_writes": 0,
            "processes": 0,
            "candidate_imports": 0,
            "dynamic_imports": 0,
            "clock_samples": 0,
            "threads": 0,
            "garbage_collections": 0,
            "randomness": 0,
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)
        self.originals.append((owner, name, original))

        def denied(*args: Any, **kwargs: Any) -> Any:
            selected = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if type(mode) is str and any(flag in mode for flag in "wax+"):
                    selected = "file_writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
                ):
                    selected = "file_writes"
            elif category == "dynamic_imports" and args:
                module = args[0]
                if type(module) is str and (
                    module == "candidates"
                    or module.startswith("candidates.")
                    or module.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS
                ):
                    selected = "candidate_imports"
            self.blocked[selected] += 1
            raise SourceOnlyError("synthetic substitution controls cannot perform " + selected)

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        protections = (
            (builtins, "open", "file_reads"),
            (io, "open", "file_reads"),
            (os, "open", "file_reads"),
            (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"),
            (os, "fstat", "file_reads"),
            (os, "scandir", "file_reads"),
            (os, "listdir", "file_reads"),
            (os, "readlink", "file_reads"),
            (os, "write", "file_writes"),
            (os, "replace", "file_writes"),
            (os, "rename", "file_writes"),
            (os, "remove", "file_writes"),
            (os, "unlink", "file_writes"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (os, "fsync", "file_writes"),
            (os, "link", "file_writes"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (subprocess, "call", "processes"),
            (subprocess, "check_call", "processes"),
            (subprocess, "check_output", "processes"),
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
            (time, "process_time", "clock_samples"),
            (gc, "collect", "garbage_collections"),
            (os, "urandom", "randomness"),
            (importlib, "import_module", "dynamic_imports"),
            (builtins, "__import__", "dynamic_imports"),
        )
        for owner, name, category in protections:
            self.install(owner, name, category)
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False


def synthetic_source_owners(source_pin: str) -> dict[str, dict[str, Any]]:
    values: dict[str, tuple[str, str]] = {
        "oracle": (SOURCE_ABSOLUTE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "v5_guard": (ROOT + "/" + V5_GUARD_RELATIVE, V5_GUARD_SHA256),
        "ownership_audit": (
            ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
        ),
    }
    values.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, source_hash)
        for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items()
    })
    return {
        name: {
            "path": path,
            "sha256": pinned,
            "bytes": 4096 + index,
            "device": 7,
            "inode": 1000 + index,
        }
        for index, (name, (path, pinned)) in enumerate(values.items())
    }


def synthetic_event(
    event: str,
    role: str,
    *,
    flags: int | None,
    before: int,
    after: int,
    payload: bytes,
    behavior: str = "stable",
) -> dict[str, Any]:
    next_payload = (
        b"!" * len(payload)
        if event == "release" and behavior == "mutate"
        else payload
    )
    result: dict[str, Any] = {
        "event": event,
        "role": role,
        "flags": flags,
        "active_before": before,
        "active_after": after,
        "backing_before_hex": payload.hex(),
        "backing_after_hex": next_payload.hex(),
        "behavior": behavior,
    }
    if event == "hash":
        result["hash_result"] = 1729
    return result


def synthetic_outcome(case: Mapping[str, Any]) -> dict[str, Any]:
    events = [
        {"event": "phase", "name": "materialize-start"},
        {"event": "phase", "name": "materialize-complete"},
        {"event": "phase", "name": "operation-start"},
        {"event": "phase", "name": "operation-return"},
        {"event": "phase", "name": "cleanup-complete"},
    ]
    result = {
        "status": "return",
        "stage": case["api"],
        "value": normalize_value(None),
        "exception": None,
        "events": events,
        "callbacks": [],
        "warnings": [],
        "subject_after": normalize_value(None),
        "replacement_after": normalize_value(None),
        "subject_active_exports": 0,
        "replacement_active_exports": 0,
        "count_requested": case["count"],
        "pos_requested": case["pos"],
        "endpos_requested": case["endpos"],
    }
    return validate_outcome(result)


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "case": case["case"],
            "cohort": case["cohort"],
            "api": case["api"],
            "outcome": synthetic_outcome(case),
        }
        for case in matrix
    ]


def synthetic_reference(
    role: str,
    pid: int,
    source_pin: str,
    matrix: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "case_count": CASE_COUNT,
        "records_sha256": digest(records),
        "records": records,
        "source_owners": synthetic_source_owners(source_pin),
        "reference_guard": make_reference_guard(2 * CASE_COUNT),
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


def synthetic_process(worker: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "role": worker["role"],
        "pid": worker["pid"],
        "returncode": 0,
        "stdout": encode_stream(canonical(dict(worker))),
        "stderr": encode_stream(b""),
    }


def validate_future_candidate_pins(value: Any) -> dict[str, str]:
    require(
        type(value) is dict
        and set(value) == {
            "family", "adapter_relative", "adapter_sha256", "engine_relative",
            "engine_sha256", "bridge_relative", "bridge_sha256",
            "v5_guard_relative", "v5_guard_sha256", "ownership_audit_relative",
            "ownership_audit_sha256",
        }
        and value.get("family") in {"rust", "c", "zig"},
        "a future independently owned candidate manifest was forged",
    )
    family = value["family"]
    adapters = {
        "rust": "candidates/rust_candidate.py",
        "c": "candidates/vm_candidate.py",
        "zig": "candidates/zig_candidate.py",
    }
    engines = {
        "rust": "candidates/_rust_engine.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_probe.so",
    }
    bridges = {
        "rust": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }
    require(
        value["adapter_relative"] == adapters[family]
        and value["engine_relative"] == engines[family]
        and value["bridge_relative"] == bridges[family]
        and value["v5_guard_relative"] == V5_GUARD_RELATIVE
        and value["v5_guard_sha256"] == V5_GUARD_SHA256
        and value["ownership_audit_relative"] == OWNERSHIP_AUDIT_RELATIVE
        and value["ownership_audit_sha256"] == OWNERSHIP_AUDIT_SHA256,
        "a sibling, external matcher, or stale ownership policy was substituted",
    )
    for key in ("adapter_sha256", "engine_sha256", "bridge_sha256"):
        checked_digest(value[key], "future independently owned candidate " + key)
    require(
        (value["engine_relative"] == value["bridge_relative"]) is (family == "c")
        and (value["engine_sha256"] == value["bridge_sha256"]) is (family == "c"),
        "only the owned C engine and bridge can share a native implementation",
    )
    return value


def synthetic_candidate_pins(family: str) -> dict[str, str]:
    adapters = {
        "rust": "candidates/rust_candidate.py",
        "c": "candidates/vm_candidate.py",
        "zig": "candidates/zig_candidate.py",
    }
    engines = {
        "rust": "candidates/_rust_engine.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_probe.so",
    }
    bridges = {
        "rust": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }
    require(family in adapters, "a genuine future candidate family is mandatory")
    result = {
        "family": family,
        "adapter_relative": adapters[family],
        "adapter_sha256": "12" * 32,
        "engine_relative": engines[family],
        "engine_sha256": "34" * 32,
        "bridge_relative": bridges[family],
        "bridge_sha256": "34" * 32 if family == "c" else "56" * 32,
        "v5_guard_relative": V5_GUARD_RELATIVE,
        "v5_guard_sha256": V5_GUARD_SHA256,
        "ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
    }
    return validate_future_candidate_pins(result)


def source_self_test() -> dict[str, Any]:
    verify_runtime(synthetic=True)
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceOnlyBoundary() as boundary:

        def accept(label: str, condition: Any) -> None:
            require(condition, "synthetic replacement positive control failed: " + label)
            accepted.append(label)

        def reject(label: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (SubstitutionOracleError, OSError, TypeError, ValueError, KeyError, IndexError):
                rejected.append(label)
                return
            raise SubstitutionOracleError("synthetic forged substitution evidence was accepted: " + label)

        matrix = build_matrix()
        validate_matrix(matrix)
        accept("freeze-all-5120-complete-substitution-buffer-cases", len(matrix) == 5120)
        accept("freeze-exact-64-balanced-cohorts", len(COHORTS) == 64)
        accept("freeze-exact-80-variants-per-cohort", all(
            sum(row["cohort"] == cohort for row in matrix) == VARIANTS_PER_COHORT
            for cohort in COHORTS
        ))
        accept("freeze-original-unsigned-64-bit-seed", 0 <= PUBLISHED_SEED < 1 << 64)
        accept("freeze-canonical-ordered-matrix-digest", digest(matrix) == MATRIX_SHA256)
        accept("include-all-module-and-compiled-substitution-apis", {
            "module.sub", "module.subn", "pattern.sub", "pattern.subn",
        }.issubset({row["api"] for row in matrix}))
        accept("include-genuine-match-expand-windows", any(
            row["api"] == "match.expand"
            and (row["pos"] != 0 or row["endpos"] is not None)
            for row in matrix
        ))
        accept("include-literal-and-all-original-replacement-escapes", {
            "literal", "escaped-named", "escaped-numeric", "missing-capture", "invalid-escape",
        }.issubset({row["replacement_style"] for row in matrix}))
        accept("include-returning-and-failing-user-callbacks", {
            "callable", "callable-error",
        }.issubset({row["replacement_style"] for row in matrix}))
        accept("include-text-bytes-bytearray", {
            "str", "bytes", "bytearray",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-contiguous-and-strided-subject-views", {
            "readonly-memoryview", "writable-memoryview",
            "readonly-strided-memoryview", "writable-strided-memoryview",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-readonly-writable-released-subject-views", {
            "released-readonly-memoryview", "released-writable-memoryview",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-contiguous-strided-released-replacement-views", {
            "readonly-memoryview", "writable-memoryview",
            "readonly-strided-memoryview", "writable-strided-memoryview",
            "released-readonly-memoryview", "released-writable-memoryview",
        }.issubset({row["replacement"]["kind"] for row in matrix}))
        accept("include-stable-mutating-failing-subject-exporters", {
            "pep688-stable", "pep688-mutating", "pep688-failing",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-stable-mutating-failing-replacement-exporters", {
            "pep688-stable", "pep688-mutating", "pep688-failing",
        }.issubset({row["replacement"]["kind"] for row in matrix}))
        accept("include-deterministic-fixed-and-unhashable-subjects", {
            "pep688-fixed-hash", "pep688-unhashable",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-fixed-unhashable-and-failing-replacement-hashes", {
            "pep688-fixed-hash", "pep688-unhashable", "pep688-failing-hash",
        }.issubset({row["replacement"]["kind"] for row in matrix}))
        accept("include-nested-owned-pep688-memoryview-wrappers", {
            "pep688-wrapped-readonly", "pep688-wrapped-writable",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-zero-width-lookahead-and-empty-patterns", {
            "text-zero-width-lookahead", "text-zero-width-empty",
            "bytes-zero-width-lookahead", "bytes-zero-width-empty",
        }.issubset(COHORTS))
        accept("include-exact-count-and-window-boundaries", {
            "text-count-limit", "text-window-pos-endpos",
            "bytes-count-limit", "bytes-window-pos-endpos",
        }.issubset(COHORTS))
        accept("preserve-lone-surrogate-and-unicode-normalization", {
            "text-lone-surrogate", "text-combining-mark", "text-precomposed-unicode",
        }.issubset(COHORTS))
        accept("freeze-owned-v3-no-delegation-policy", OWNERSHIP_AUDIT_SHA256 == (
            "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
        ))

        nested_events = [
            synthetic_event("acquire", "subject", flags=0, before=0, after=1, payload=b"alpha"),
            synthetic_event("acquire", "subject", flags=0, before=1, after=2, payload=b"alpha"),
            synthetic_event("acquire", "replacement", flags=284, before=0, after=1, payload=b"X"),
            synthetic_event("release", "replacement", flags=None, before=1, after=0, payload=b"X"),
            synthetic_event("release", "subject", flags=None, before=2, after=1, payload=b"alpha"),
            synthetic_event("release", "subject", flags=None, before=1, after=0, payload=b"alpha"),
        ]
        accept("preserve-exact-nested-buffer-flags-0-0-284", [
            item["flags"] for item in nested_events if item["event"] == "acquire"
        ] == [0, 0, 284])
        accept(
            "preserve-exact-nested-lifo-acquisition-release",
            validate_events(
                nested_events,
                require_balanced=True,
                expected_acquisition_flags=(
                    SIMPLE_BUFFER_FLAG,
                    SIMPLE_BUFFER_FLAG,
                    FULL_READONLY_BUFFER_FLAG,
                ),
            ) is nested_events,
        )
        hash_events = [synthetic_event(
            "hash", "replacement", flags=None, before=0, after=0, payload=b"X",
        )]
        accept("preserve-exact-deterministic-custom-hash-event", validate_events(hash_events) is hash_events)
        mutating_events = [
            synthetic_event("acquire", "subject", flags=0, before=0, after=1, payload=b"alpha", behavior="mutate"),
            synthetic_event("release", "subject", flags=None, before=1, after=0, payload=b"alpha", behavior="mutate"),
        ]
        accept("preserve-exact-equal-length-poison-on-release", validate_events(mutating_events) is mutating_events)
        synthetic_error_engine = types.SimpleNamespace(error=None)
        for title, error, message in (
            (
                "released-subject-memoryview-type-error",
                TypeError("expected string or bytes-like object, got 'memoryview'"),
                "expected string or bytes-like object, got 'memoryview'",
            ),
            (
                "released-replacement-memoryview-value-error",
                ValueError("operation forbidden on released memoryview object"),
                "operation forbidden on released memoryview object",
            ),
            (
                "writable-replacement-memoryview-hash-error",
                ValueError("cannot hash writable memoryview object"),
                "cannot hash writable memoryview object",
            ),
            (
                "pep688-replacement-buffer-failure",
                BufferError("frozen substitution replacement exporter failure"),
                "frozen substitution replacement exporter failure",
            ),
            (
                "deterministic-failing-replacement-hash",
                TypeError("frozen substitution replacement exporter hash failure"),
                "frozen substitution replacement exporter hash failure",
            ),
            (
                "deterministic-failing-user-callback",
                ReplacementCallbackError("frozen substitution callback failure"),
                "frozen substitution callback failure",
            ),
        ):
            observed_error = normalize_error(error, synthetic_error_engine)
            accept(
                "preserve-exact-" + title,
                observed_error["message"] == message
                and observed_error["type"] == type(error).__qualname__
                and validate_error(observed_error) is None,
            )

        for item in (
            None,
            True,
            False,
            0,
            1,
            "\ud800",
            "e\u0301",
            "\u00e9",
            b"\x00\xff",
            bytearray(b"ab"),
            (),
            ("a", 1),
            [],
            ["a", b"b"],
            {"a": 1, "b": b"x"},
        ):
            observed = normalize_value(item)
            accept("preserve-type-tagged-original-value-" + str(len(accepted)), validate_normalized_value(observed) is None)

        source_pin = hashlib.sha256(b"synthetic-substitution-oracle-source-v1").hexdigest()
        owners = synthetic_source_owners(source_pin)
        accept("authenticate-complete-synthetic-standard-source-closure", validate_source_owners(owners, source_pin) is owners)
        records = synthetic_records(matrix)
        records_sha256 = digest(records)
        accept("retain-every-complete-synthetic-outcome", validate_records(matrix, records, records_sha256) is records)
        first = synthetic_reference("reference_a", 7001, source_pin, matrix, records)
        second = synthetic_reference("reference_b", 7002, source_pin, matrix, records)
        first_process = synthetic_process(first)
        second_process = synthetic_process(second)
        accept("authenticate-synthetic-reference-a", validate_reference_worker(
            first, role="reference_a", source_pin=source_pin, matrix=matrix, expected_pid=7001,
        ) is first)
        accept("authenticate-synthetic-reference-b", validate_reference_worker(
            second, role="reference_b", source_pin=source_pin, matrix=matrix, expected_pid=7002,
        ) is second)
        accept("preserve-two-genuinely-distinct-synthetic-reference-pids", first["pid"] != second["pid"])
        accept("preserve-complete-reversible-reference-stdout", decode_stream(
            first_process["stdout"], "reference_a",
        ) == canonical(first))
        accept("preserve-complete-empty-reference-stderr", decode_stream(
            first_process["stderr"], "reference_a",
        ) == b"")
        accept("require-two-identical-independent-reference-vectors", validate_reference_pair(
            first, second, first_process, second_process, source_pin=source_pin, matrix=matrix,
        ) == records_sha256)

        for family in ("rust", "c", "zig"):
            future = synthetic_candidate_pins(family)
            accept(
                "preserve-future-independent-" + family + "-owned-engine",
                validate_future_candidate_pins(future) is future,
            )
            for field in (
                "family", "adapter_relative", "adapter_sha256", "engine_relative",
                "engine_sha256", "bridge_relative", "bridge_sha256",
                "v5_guard_relative", "v5_guard_sha256", "ownership_audit_relative",
                "ownership_audit_sha256",
            ):
                forged = dict(future)
                if field == "family":
                    forged[field] = "foreign"
                elif field in {"adapter_sha256", "engine_sha256", "bridge_sha256"}:
                    forged[field] = "0" * 64
                elif field.endswith("sha256"):
                    forged[field] = hashlib.sha256(("foreign:" + field).encode("ascii")).hexdigest()
                else:
                    forged[field] = "candidates/foreign-regex.so"
                reject(
                    "reject-" + family + "-foreign-" + field,
                    lambda forged=forged: validate_future_candidate_pins(forged),
                )

        for field in (
            "case", "cohort", "variant", "seed", "api", "flags", "count",
            "pos", "endpos", "pattern", "subject", "replacement",
            "replacement_style", "callback_raises",
        ):
            forged = list(matrix)
            row = dict(forged[0])
            del row[field]
            forged[0] = row
            reject(
                "reject-missing-frozen-case-" + field,
                lambda forged=forged: validate_matrix(forged),
            )
        for title, transform in (
            ("missing-first", lambda values: values.pop(0)),
            ("missing-last", lambda values: values.pop()),
            ("duplicate-case", lambda values: values.__setitem__(1, values[0])),
            ("reordered-case", lambda values: values.__setitem__(slice(0, 2), [values[1], values[0]])),
            ("added-case", lambda values: values.append(values[0])),
        ):
            forged = list(matrix)
            transform(forged)
            reject(
                "reject-" + title + "-complete-matrix",
                lambda forged=forged: validate_matrix(forged),
            )

        for field in (
            "schema", "status", "python", "role", "pid", "oracle_source_sha256",
            "matrix_sha256", "published_seed", "cohort_count", "variants_per_cohort",
            "case_count", "records_sha256", "records", "source_owners",
            "reference_guard", "actual_reference_workers", "actual_candidate_workers",
            "actual_candidate_imports", "clock_samples", "timing_trials_run",
            "workspace_files_written", "evidence_files_created", "benchmark_files_read",
            "hidden_cases_read", "performance", "candidate_qualified_for_hidden_benchmark",
            "final_winner_selected",
        ):
            forged = dict(first)
            del forged[field]
            reject(
                "reject-missing-reference-worker-" + field,
                lambda forged=forged: validate_reference_worker(
                    forged,
                    role="reference_a",
                    source_pin=source_pin,
                    matrix=matrix,
                    expected_pid=7001,
                ),
            )
        for field in first["reference_guard"]:
            forged = dict(first["reference_guard"])
            if type(forged[field]) is bool:
                forged[field] = not forged[field]
            elif type(forged[field]) is int:
                forged[field] += 1
            else:
                forged[field] = "foreign"
            reject(
                "reject-forged-reference-guard-" + field,
                lambda forged=forged: validate_reference_guard(forged),
            )
        for field in ("base64", "bytes", "sha256", "complete"):
            forged = dict(first_process["stdout"])
            if field == "base64":
                forged[field] = "e30="
            elif field == "bytes":
                forged[field] += 1
            elif field == "sha256":
                forged[field] = hashlib.sha256(b"forged").hexdigest()
            else:
                forged[field] = False
            reject(
                "reject-incomplete-process-" + field,
                lambda forged=forged: decode_stream(forged, "forged"),
            )
        for title, forged in (
            ("duplicate-fields", b'{"role":"a","role":"b"}\n'),
            ("nonfinite", b'{"value":NaN}\n'),
            ("truncated", b'{"role":"a"'),
            ("extra-suffix", b'{}\n{}\n'),
            ("noncanonical", b'{ "role": "a" }\n'),
        ):
            reject(
                "reject-" + title + "-worker-json",
                lambda forged=forged: decode_canonical(forged, title),
            )
        poisoned = list(nested_events)
        poisoned[0] = {**poisoned[0], "flags": True}
        reject("reject-boolean-simple-acquisition-flag", lambda: validate_events(poisoned))
        reordered = list(nested_events)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        reject("reject-reordered-nested-simple-acquisitions", lambda: validate_events(reordered))
        missing_release = list(nested_events)
        missing_release.pop(3)
        reject(
            "reject-omitted-nested-template-release",
            lambda: validate_events(
                missing_release,
                require_balanced=True,
                expected_acquisition_flags=(
                    SIMPLE_BUFFER_FLAG,
                    SIMPLE_BUFFER_FLAG,
                    FULL_READONLY_BUFFER_FLAG,
                ),
            ),
        )
        forged_full_flag = copy.deepcopy(nested_events)
        forged_full_flag[2]["flags"] = SIMPLE_BUFFER_FLAG
        reject(
            "reject-substituted-exact-284-full-readonly-buffer-flag",
            lambda: validate_events(
                forged_full_flag,
                require_balanced=True,
                expected_acquisition_flags=(
                    SIMPLE_BUFFER_FLAG,
                    SIMPLE_BUFFER_FLAG,
                    FULL_READONLY_BUFFER_FLAG,
                ),
            ),
        )
        wrong_release_order = copy.deepcopy(nested_events)
        wrong_release_order[3], wrong_release_order[4] = (
            wrong_release_order[4],
            wrong_release_order[3],
        )
        reject(
            "reject-reordered-nested-subject-and-replacement-releases",
            lambda: validate_events(
                wrong_release_order,
                require_balanced=True,
                expected_acquisition_flags=(
                    SIMPLE_BUFFER_FLAG,
                    SIMPLE_BUFFER_FLAG,
                    FULL_READONLY_BUFFER_FLAG,
                ),
            ),
        )
        broken_mutation = copy.deepcopy(mutating_events)
        broken_mutation[1]["backing_after_hex"] = b"?".hex()
        reject("reject-resized-poison-on-release", lambda: validate_events(broken_mutation))

        for title, action in (
            ("file-read", lambda: builtins.open("synthetic-reference")),
            ("descriptor-read", lambda: os.open("synthetic-reference", os.O_RDONLY)),
            ("file-write", lambda: os.write(1, b"synthetic")),
            ("candidate-import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("external-regex-import", lambda: builtins.__import__("regex")),
            ("dynamic-standard-import", lambda: importlib.import_module("math")),
            ("reference-worker", lambda: subprocess.Popen(["synthetic"])),
            ("process-delegation", lambda: os.system("synthetic")),
            ("background-thread", lambda: threading.Thread().start()),
            ("wall-clock", lambda: time.time()),
            ("monotonic-clock", lambda: time.monotonic()),
            ("performance-clock", lambda: time.perf_counter()),
            ("system-randomness", lambda: os.urandom(8)),
            ("garbage-collection", lambda: gc.collect()),
        ):
            reject("block-real-" + title, action)
        accept(
            "exercise-every-real-source-only-side-effect-guard",
            all(count > 0 for count in boundary.blocked.values()),
        )
        accept(
            "load-zero-native-candidates-or-external-regex",
            not any(
                name == "candidates" or name.startswith("candidates.")
                or name.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS
                for name in sys.modules
            ),
        )

    verify_runtime(synthetic=True)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "positive_control_count": len(accepted),
        "positive_controls": accepted,
        "negative_control_count": len(rejected),
        "negative_controls": rejected,
        "source_only_blocked_operations": dict(boundary.blocked),
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
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze independently owned replacement and PEP-688 semantics",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--baseline", action="store_true")
    modes.add_argument("--internal-reference-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--role", choices=("reference_a", "reference_b"))
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            verify_runtime(synthetic=True)
            require(
                options.role is None
                and options.oracle_source_sha256 is None
                and options.matrix_sha256 is None,
                "a source-only control cannot select, pin, or run an actual reference",
            )
            result = source_self_test()
        else:
            verify_runtime()
            checked_digest(options.oracle_source_sha256, "explicitly frozen substitution oracle")
            checked_digest(options.matrix_sha256, "explicitly frozen substitution matrix")
            require(options.matrix_sha256 == MATRIX_SHA256, "the frozen substitution matrix changed")
            if options.internal_reference_worker:
                require(options.role in {"reference_a", "reference_b"}, "an exact reference role is mandatory")
                result = observe_reference_worker(options.role, options.oracle_source_sha256)
            else:
                require(options.baseline and options.role is None, "only an explicitly authorized two-reference baseline may run")
                result = run_baseline(options.oracle_source_sha256, options.matrix_sha256)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except ReferenceWorkerFailure as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "complete_reference_worker_failure": error.evidence,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1
    except (SubstitutionOracleError, OSError, TypeError, ValueError) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
