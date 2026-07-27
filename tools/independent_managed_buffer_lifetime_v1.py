#!/usr/bin/env python3
"""Frozen, untimed CPython buffer, scanner, and Unicode property cases.

``--self-test`` is synthetic and cannot read a project file, start a worker,
load a candidate, sample a clock, or write evidence.  ``--baseline`` is a
separate, explicitly pinned operation that starts exactly two genuine CPython
reference workers.  This source intentionally has no candidate-running mode.
A future candidate controller must install the independently frozen V5
ownership guard and supply a complete, explicitly authenticated native closure.
"""

from __future__ import annotations

import argparse
import base64
import builtins
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
from collections.abc import Callable, Mapping
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/independent_managed_buffer_lifetime_v1.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-managed-buffer-lifetime-v1"
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
OWNERSHIP_AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
OWNERSHIP_AUDIT_SHA256 = (
    "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
)
PUBLISHED_SEED = 0x4D424C4946455631
VARIANTS_PER_GROUP = 32
GROUPS = (
    "direct-bytes-control",
    "direct-bytearray-control",
    "readonly-contiguous-view",
    "writable-contiguous-view",
    "readonly-sliced-contiguous-view",
    "writable-sliced-contiguous-view",
    "readonly-strided-view",
    "writable-strided-view",
    "released-before-operation",
    "released-after-match-before-group",
    "released-after-match-before-expand",
    "backing-mutated-after-match",
    "bytearray-resize-during-live-iterator",
    "bytearray-resize-after-iterator-teardown",
    "pep688-subject-acquire-release",
    "pep688-subject-overwrite-on-release",
    "pep688-subject-exporter-error",
    "pep688-template-exporter-error",
    "readonly-template-memoryview",
    "writable-template-memoryview",
    "strided-template-memoryview",
    "released-template-memoryview",
    "match-group-retained-lifetime",
    "iterator-create-and-advance-lifetime",
    "iterator-exhaust-release",
    "iterator-delete-and-gc-release",
    "native-scanner-search-lifetime",
    "native-scanner-match-lifetime",
    "public-scanner-branch-and-callback-identity",
    "public-scanner-lexicon-mutation-and-flags",
    "bytes-vs-unicode-type-separation",
    "unicode-surrogate-and-normalization-boundaries",
)
FAMILIES = GROUPS
VARIANTS_PER_FAMILY = VARIANTS_PER_GROUP
CASE_COUNT = len(GROUPS) * VARIANTS_PER_GROUP
MATRIX_SHA256 = (
    "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976"
)
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
IGNORECASE = 2
ASCII = 256
FLAGS = (0, IGNORECASE, ASCII, IGNORECASE | ASCII)
BASIC_APIS = (
    "search", "match", "fullmatch", "findall", "split", "sub", "subn",
    "finditer",
)
ALL_APIS = BASIC_APIS + (
    "match.group", "match.groups", "match.expand",
    "compiled.scanner.search", "compiled.scanner.match",
    "public.scanner.scan",
)
CARRIER_KINDS = frozenset({
    "bytes", "bytearray", "readonly-memoryview", "mutable-memoryview",
    "tracked-exporter", "failing-exporter",
})
BEHAVIORS = frozenset({"none", "stable", "overwrite", "error"})
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "_regex", "fancy_regex", "google_re2", "hyperscan", "onig",
    "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class ManagedBufferOracleError(Exception):
    """A frozen case, genuine reference, or complete observation was forged."""


class SourceOnlyError(ManagedBufferOracleError):
    """A synthetic source self-test attempted a real external effect."""


class ReferenceWorkerFailure(ManagedBufferOracleError):
    """Preserve the exact streams of a failed genuine reference worker."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ManagedBufferOracleError(message)


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
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise ManagedBufferOracleError(
            "a managed-buffer observation is not canonical JSON"
        ) from error


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
    require(valid_digest(value), "an exact SHA-256 is required: " + label)
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(
            type(key) is str and key not in result,
            "a managed-buffer JSON field was duplicated",
        )
        result[key] = value
    return result


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
        "complete bounded managed-buffer output is mandatory: " + label,
    )

    def reject_constant(_: str) -> Any:
        raise ManagedBufferOracleError("nonfinite JSON is forbidden")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (
        ManagedBufferOracleError, TypeError, ValueError, UnicodeError,
        json.JSONDecodeError,
    ) as error:
        raise ManagedBufferOracleError(
            "a managed-buffer worker emitted invalid JSON: " + label
        ) from error
    require(
        type(value) is dict and canonical(value) == raw,
        "a complete canonical managed-buffer worker was substituted: " + label,
    )
    return value


def encode_bytes(value: bytes) -> dict[str, str]:
    require(type(value) is bytes, "an exact byte payload is mandatory")
    return {"kind": "bytes", "hex": value.hex()}


def encode_text(value: str) -> dict[str, str]:
    require(type(value) is str, "an exact Unicode payload is mandatory")
    return {"kind": "str", "value": value}


def carrier_descriptor(
    kind: str,
    payload: bytes,
    *,
    start: int = 0,
    stop: int | None = None,
    step: int = 1,
    behavior: str = "none",
) -> dict[str, Any]:
    require(kind in CARRIER_KINDS, "an unfrozen subject carrier was selected")
    require(type(payload) is bytes, "the subject payload must be exact bytes")
    require(behavior in BEHAVIORS, "an unfrozen exporter behavior was selected")
    return {
        "kind": kind,
        "hex": payload.hex(),
        "start": start,
        "stop": len(payload) if stop is None else stop,
        "step": step,
        "behavior": behavior,
    }


def template_descriptor(
    kind: str,
    payload: bytes,
    *,
    readonly: bool = True,
    start: int = 0,
    stop: int | None = None,
    step: int = 1,
    released: bool = False,
    behavior: str = "none",
) -> dict[str, Any]:
    require(
        kind in ("bytes", "bytearray", "template-memoryview",
                 "tracked-exporter", "failing-exporter"),
        "an unfrozen replacement carrier was selected",
    )
    require(type(payload) is bytes, "an exact replacement payload is required")
    require(type(readonly) is bool and type(released) is bool,
            "a replacement mutability or release marker was forged")
    require(behavior in BEHAVIORS, "a replacement exporter behavior changed")
    return {
        "kind": kind,
        "hex": payload.hex(),
        "readonly": readonly,
        "start": start,
        "stop": len(payload) if stop is None else stop,
        "step": step,
        "released": released,
        "behavior": behavior,
    }


def build_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and seed >= 0, "a deterministic seed is mandatory")
    seeded = random.Random(seed)
    cases: list[dict[str, Any]] = []
    text_patterns = (
        r"(?P<word>\w+)(?P<number>\d*)",
        r"(?a:\w+)",
        "\ud800",
        "e\u0301",
        "\N{LATIN SMALL LETTER E WITH ACUTE}",
        r".",
        r"(?i:[a-z]+)",
        r"(?P<word>\w+)",
    )
    for group in GROUPS:
        for variant in range(VARIANTS_PER_GROUP):
            noise = "".join(
                seeded.choice("abcdef0123456789") for _ in range(8)
            ).encode("ascii")
            payload = b"alpha42 beta7 !" + noise
            replacement = rb"<\g<word>>"
            carrier: dict[str, Any] = carrier_descriptor("bytes", payload)
            pattern: dict[str, Any] = encode_bytes(
                rb"(?P<word>[A-Za-z]+)(?P<number>[0-9]*)"
            )
            template = template_descriptor("bytes", replacement)
            operation = BASIC_APIS[variant % len(BASIC_APIS)]
            action = "none"
            flags = FLAGS[variant % len(FLAGS)]

            if group == "direct-bytearray-control":
                carrier = carrier_descriptor("bytearray", payload)
            elif group == "readonly-contiguous-view":
                carrier = carrier_descriptor("readonly-memoryview", payload)
            elif group == "writable-contiguous-view":
                carrier = carrier_descriptor("mutable-memoryview", payload)
            elif group in (
                "readonly-sliced-contiguous-view",
                "writable-sliced-contiguous-view",
            ):
                padded = b"<<" + payload + b">>"
                kind = (
                    "readonly-memoryview"
                    if group == "readonly-sliced-contiguous-view"
                    else "mutable-memoryview"
                )
                carrier = carrier_descriptor(
                    kind, padded, start=2, stop=len(padded) - 2,
                )
            elif group in ("readonly-strided-view", "writable-strided-view"):
                interleaved = b"".join(bytes((item, 33)) for item in payload)
                kind = (
                    "readonly-memoryview" if group == "readonly-strided-view"
                    else "mutable-memoryview"
                )
                carrier = carrier_descriptor(kind, interleaved, step=2)
            elif group == "released-before-operation":
                kind = (
                    "readonly-memoryview" if variant % 2 == 0
                    else "mutable-memoryview"
                )
                carrier = carrier_descriptor(kind, payload)
                action = "release-before-operation"
            elif group == "released-after-match-before-group":
                kind = (
                    "readonly-memoryview" if variant % 2 == 0
                    else "mutable-memoryview"
                )
                carrier = carrier_descriptor(kind, payload)
                operation = "match.group" if variant % 2 == 0 else "match.groups"
                action = "release-after-match"
            elif group == "released-after-match-before-expand":
                kind = (
                    "readonly-memoryview" if variant % 2 == 0
                    else "mutable-memoryview"
                )
                carrier = carrier_descriptor(kind, payload)
                operation = "match.expand"
                action = "release-after-match"
            elif group == "backing-mutated-after-match":
                carrier = carrier_descriptor("mutable-memoryview", payload)
                operation = (
                    "match.group", "match.groups", "match.expand",
                )[variant % 3]
                action = "mutate-backing-after-match"
            elif group == "bytearray-resize-during-live-iterator":
                carrier = carrier_descriptor("bytearray", payload)
                operation = "finditer"
                action = "resize-during-live-iterator"
            elif group == "bytearray-resize-after-iterator-teardown":
                carrier = carrier_descriptor("bytearray", payload)
                operation = "finditer"
                action = "resize-after-iterator-teardown"
            elif group in (
                "pep688-subject-acquire-release",
                "pep688-subject-overwrite-on-release",
            ):
                behavior = (
                    "stable" if group == "pep688-subject-acquire-release"
                    else "overwrite"
                )
                carrier = carrier_descriptor(
                    "tracked-exporter", payload, behavior=behavior,
                )
            elif group == "pep688-subject-exporter-error":
                carrier = carrier_descriptor(
                    "failing-exporter", payload, behavior="error",
                )
            elif group == "pep688-template-exporter-error":
                template = template_descriptor(
                    "failing-exporter", replacement, behavior="error",
                )
                operation = ("match.expand", "sub", "subn")[variant % 3]
            elif group in (
                "readonly-template-memoryview",
                "writable-template-memoryview",
            ):
                template = template_descriptor(
                    "template-memoryview",
                    replacement,
                    readonly=group == "readonly-template-memoryview",
                )
                operation = ("match.expand", "sub", "subn")[variant % 3]
            elif group == "strided-template-memoryview":
                interleaved = b"".join(bytes((item, 33)) for item in replacement)
                template = template_descriptor(
                    "template-memoryview", interleaved,
                    readonly=variant % 2 == 0, step=2,
                )
                operation = ("match.expand", "sub", "subn")[variant % 3]
            elif group == "released-template-memoryview":
                template = template_descriptor(
                    "template-memoryview", replacement,
                    readonly=variant % 2 == 0, released=True,
                )
                operation = ("match.expand", "sub", "subn")[variant % 3]
            elif group == "match-group-retained-lifetime":
                carrier = carrier_descriptor(
                    "tracked-exporter", payload,
                    behavior="overwrite" if variant % 2 else "stable",
                )
                operation = (
                    "match.group", "match.groups", "match.expand",
                )[variant % 3]
                action = "observe-match-retained-lifetime"
            elif group in (
                "iterator-create-and-advance-lifetime",
                "iterator-exhaust-release",
                "iterator-delete-and-gc-release",
            ):
                carrier = carrier_descriptor(
                    "tracked-exporter", payload,
                    behavior="overwrite" if variant % 2 else "stable",
                )
                operation = "finditer"
                action = {
                    "iterator-create-and-advance-lifetime":
                        "observe-iterator-advance",
                    "iterator-exhaust-release": "observe-iterator-exhaust",
                    "iterator-delete-and-gc-release": "delete-iterator-and-gc",
                }[group]
            elif group in (
                "native-scanner-search-lifetime",
                "native-scanner-match-lifetime",
            ):
                carrier = carrier_descriptor(
                    "tracked-exporter", payload,
                    behavior="overwrite" if variant % 2 else "stable",
                )
                operation = (
                    "compiled.scanner.search"
                    if group == "native-scanner-search-lifetime"
                    else "compiled.scanner.match"
                )
                action = "observe-native-scanner-lifetime"
            elif group in (
                "public-scanner-branch-and-callback-identity",
                "public-scanner-lexicon-mutation-and-flags",
            ):
                operation = "public.scanner.scan"
                if variant % 4 == 1:
                    carrier = carrier_descriptor("bytearray", payload)
                elif variant % 4 == 2:
                    carrier = carrier_descriptor("readonly-memoryview", payload)
                elif variant % 4 == 3:
                    carrier = carrier_descriptor("mutable-memoryview", payload)
                action = (
                    "observe-public-scanner"
                    if group == "public-scanner-branch-and-callback-identity"
                    else "mutate-public-scanner-lexicon"
                )
            elif group == "bytes-vs-unicode-type-separation":
                unicode_payload = (
                    "café42 Δelta7 e\u0301 \ud800 😀 "
                    + noise.decode("ascii")
                )
                if variant % 2 == 0:
                    carrier = encode_text(unicode_payload)
                else:
                    pattern = encode_text(r"(?P<word>\w+)(?P<number>\d*)")
                operation = BASIC_APIS[variant % len(BASIC_APIS)]
            elif group == "unicode-surrogate-and-normalization-boundaries":
                carrier = encode_text(
                    "café42 Δelta7 e\u0301 \ud800 😀 "
                    + noise.decode("ascii")
                )
                pattern = encode_text(
                    text_patterns[variant % len(text_patterns)]
                )
                template = encode_text(
                    r"<\g<word>>" if variant % 2 == 0 else r"\g<0>"
                )
                operation = BASIC_APIS[variant % len(BASIC_APIS)]

            cases.append({
                "case": "managed-buffer-lifetime.v1."
                + format(len(cases), "04d"),
                "group": group,
                "variant": variant,
                "seed": seed,
                "flags": flags,
                "operation": operation,
                "action": action,
                "pattern": pattern,
                "subject": carrier,
                "template": template,
            })
    return cases


def validate_carrier_descriptor(value: Any, *, template: bool = False) -> None:
    require(type(value) is dict, "a complete carrier descriptor is mandatory")
    if value.get("kind") == "str":
        require(
            not template and set(value) == {"kind", "value"}
            and type(value.get("value")) is str,
            "a Unicode subject carrier was substituted",
        )
        return
    if template:
        require(
            set(value) == {
                "kind", "hex", "readonly", "start", "stop", "step",
                "released", "behavior",
            }
            and value.get("kind") in {
                "bytes", "bytearray", "template-memoryview",
                "tracked-exporter", "failing-exporter",
            }
            and type(value.get("readonly")) is bool
            and type(value.get("released")) is bool,
            "a replacement descriptor, mutability, or release was forged",
        )
    else:
        require(
            set(value) == {"kind", "hex", "start", "stop", "step", "behavior"}
            and value.get("kind") in CARRIER_KINDS,
            "a subject descriptor or exporter was forged",
        )
    require(
        type(value.get("hex")) is str
        and type(value.get("start")) is int
        and type(value.get("stop")) is int
        and type(value.get("step")) is int
        and value["step"] in (1, 2)
        and value.get("behavior") in BEHAVIORS,
        "a carrier byte sequence, shape, or behavior was forged",
    )
    try:
        payload = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise ManagedBufferOracleError("a carrier hex payload is invalid") from error
    require(
        payload.hex() == value["hex"]
        and 0 <= value["start"] <= value["stop"] <= len(payload),
        "a carrier payload is noncanonical or its bounds are invalid",
    )
    kind = value["kind"]
    if kind == "tracked-exporter":
        require(value["behavior"] in {"stable", "overwrite"},
                "a real tracked exporter behavior was omitted")
    elif kind == "failing-exporter":
        require(value["behavior"] == "error",
                "a real failing exporter was substituted")
    else:
        require(value["behavior"] == "none",
                "an ordinary carrier cannot impersonate a managed exporter")


def validate_pattern_descriptor(value: Any) -> None:
    require(type(value) is dict, "a complete pattern descriptor is mandatory")
    if value.get("kind") == "str":
        require(set(value) == {"kind", "value"}
                and type(value.get("value")) is str,
                "an exact Unicode pattern was forged")
        return
    require(set(value) == {"kind", "hex"} and value.get("kind") == "bytes"
            and type(value.get("hex")) is str,
            "an exact bytes pattern was forged")
    try:
        raw = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise ManagedBufferOracleError("a pattern hex payload is invalid") from error
    require(raw.hex() == value["hex"], "a pattern hex payload is noncanonical")


def validate_matrix(
    matrix: Any, expected_sha256: str = MATRIX_SHA256,
) -> str:
    checked_digest(expected_sha256, "prospectively frozen managed-buffer matrix")
    require(
        len(GROUPS) == 32 and VARIANTS_PER_GROUP == 32 and CASE_COUNT == 1024,
        "the managed-buffer obligation denominator silently changed",
    )
    require(
        type(matrix) is list and len(matrix) == CASE_COUNT,
        "all 1,024 independently frozen managed-buffer cases are mandatory",
    )
    exact = build_matrix()
    require(
        matrix == exact and digest(matrix) == expected_sha256,
        "the exact seed, ordered groups, case rows, or matrix digest changed",
    )
    observed_groups: dict[str, int] = {group: 0 for group in GROUPS}
    identifiers: set[str] = set()
    for index, row in enumerate(matrix):
        require(
            type(row) is dict
            and set(row) == {
                "case", "group", "variant", "seed", "flags", "operation",
                "action", "pattern", "subject", "template",
            }
            and row["case"]
            == "managed-buffer-lifetime.v1." + format(index, "04d")
            and row["case"] not in identifiers
            and row["group"] == GROUPS[index // VARIANTS_PER_GROUP]
            and type(row["variant"]) is int
            and row["variant"] == index % VARIANTS_PER_GROUP
            and type(row["seed"]) is int and row["seed"] == PUBLISHED_SEED
            and type(row["flags"]) is int and row["flags"] in FLAGS
            and row["operation"] in ALL_APIS
            and type(row["action"]) is str,
            "a complete managed-buffer case was omitted, reordered, or forged",
        )
        validate_pattern_descriptor(row["pattern"])
        validate_carrier_descriptor(row["subject"])
        if row["template"].get("kind") == "str":
            validate_pattern_descriptor(row["template"])
        else:
            validate_carrier_descriptor(row["template"], template=True)
        identifiers.add(row["case"])
        observed_groups[row["group"]] += 1
    require(
        all(count == VARIANTS_PER_GROUP for count in observed_groups.values()),
        "an entire managed-buffer property group silently changed",
    )
    return expected_sha256


class TrackedExporter:
    """A safe PEP-688 exporter; release only overwrites at identical length."""

    __slots__ = ("backing", "behavior", "events", "role", "active")

    def __init__(
        self, payload: bytes, behavior: str,
        events: list[dict[str, Any]], role: str,
    ) -> None:
        require(type(payload) is bytes, "a tracked exporter needs exact bytes")
        require(behavior in {"stable", "overwrite", "error"},
                "an unfrozen tracked exporter behavior was selected")
        require(role in {"subject", "template"},
                "a tracked exporter role was forged")
        self.backing = bytearray(payload)
        self.behavior = behavior
        self.events = events
        self.role = role
        self.active = 0

    def __buffer__(self, flags: int) -> memoryview:
        require(type(flags) is int, "an exact buffer-acquisition flag is required")
        before = bytes(self.backing).hex()
        if self.behavior == "error":
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
            raise BufferError("frozen managed-buffer " + self.role + " exporter failure")
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
        require(type(view) is memoryview,
                "the genuine PEP-688 release view was substituted")
        require(self.active > 0, "an exporter was released without ownership")
        before = bytes(self.backing).hex()
        if self.behavior == "overwrite":
            replacement = b"!" * len(self.backing)
            require(len(replacement) == len(self.backing),
                    "an exporter release must never resize storage")
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


def decode_pattern(value: Mapping[str, Any]) -> str | bytes:
    validate_pattern_descriptor(value)
    if value["kind"] == "str":
        return value["value"]
    return bytes.fromhex(value["hex"])


def decode_carrier(
    value: Mapping[str, Any], events: list[dict[str, Any]], *, role: str,
) -> tuple[Any, bytearray | None, TrackedExporter | None]:
    validate_carrier_descriptor(value)
    if value["kind"] == "str":
        return value["value"], None, None
    payload = bytes.fromhex(value["hex"])
    start, stop, step = value["start"], value["stop"], value["step"]
    kind = value["kind"]
    if kind == "bytes":
        return payload[start:stop:step], None, None
    if kind == "bytearray":
        actual = bytearray(payload)
        if start == 0 and stop == len(payload) and step == 1:
            return actual, actual, None
        result = actual[start:stop:step]
        return result, result, None
    if kind == "readonly-memoryview":
        return memoryview(payload)[start:stop:step], None, None
    if kind == "mutable-memoryview":
        backing = bytearray(payload)
        return memoryview(backing)[start:stop:step], backing, None
    exporter = TrackedExporter(payload, value["behavior"], events, role)
    return exporter, exporter.backing, exporter


def decode_template(
    value: Mapping[str, Any], events: list[dict[str, Any]],
) -> tuple[Any, TrackedExporter | None]:
    if value.get("kind") == "str":
        validate_pattern_descriptor(value)
        return value["value"], None
    validate_carrier_descriptor(value, template=True)
    payload = bytes.fromhex(value["hex"])
    start, stop, step = value["start"], value["stop"], value["step"]
    kind = value["kind"]
    if kind == "bytes":
        return payload[start:stop:step], None
    if kind == "bytearray":
        return bytearray(payload)[start:stop:step], None
    if kind == "template-memoryview":
        backing: bytes | bytearray = (
            payload if value["readonly"] else bytearray(payload)
        )
        result = memoryview(backing)[start:stop:step]
        if value["released"]:
            result.release()
        return result, None
    exporter = TrackedExporter(payload, value["behavior"], events, "template")
    return exporter, exporter


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
                "strides": (
                    list(value.strides) if value.strides is not None else None
                ),
                "contiguous": value.contiguous,
                "c_contiguous": value.c_contiguous,
                "f_contiguous": value.f_contiguous,
            }
        except ValueError as error:
            return {
                "type": "released-memoryview",
                "error_module": type(error).__module__,
                "error_type": type(error).__qualname__,
                "error_args": normalize_value(error.args),
            }
    if type(value) is TrackedExporter:
        return {
            "type": "managed-exporter",
            "role": value.role,
            "behavior": value.behavior,
            "backing_hex": bytes(value.backing).hex(),
            "active_exports": value.active,
        }
    if type(value) in (tuple, list):
        return {
            "type": "tuple" if type(value) is tuple else "list",
            "items": [normalize_value(item) for item in value],
        }
    if type(value) is dict:
        items: list[list[dict[str, Any]]] = []
        for key, item in value.items():
            items.append([normalize_value(key), normalize_value(item)])
        items.sort(key=lambda pair: canonical(pair[0]))
        return {"type": "dict", "items": items}
    raise ManagedBufferOracleError(
        "a managed-buffer observable was omitted: " + type(value).__qualname__
    )


def validate_normalized_value(value: Any) -> None:
    require(type(value) is dict and type(value.get("type")) is str,
            "a strictly type-tagged observable is mandatory")
    kind = value["type"]
    if kind == "none":
        require(set(value) == {"type"}, "a null observable was forged")
    elif kind in {"bool", "int", "str"}:
        expected = {"bool": bool, "int": int, "str": str}[kind]
        require(set(value) == {"type", "value"}
                and type(value.get("value")) is expected,
                "a scalar observable lost its exact Python type")
    elif kind in {"bytes", "bytearray"}:
        require(set(value) == {"type", "hex"}
                and type(value.get("hex")) is str,
                "a bytes observable lost its Python carrier type")
        try:
            decoded = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise ManagedBufferOracleError("an observable hex is invalid") from error
        require(decoded.hex() == value["hex"],
                "an observable hex payload is noncanonical")
    elif kind in {"tuple", "list"}:
        require(set(value) == {"type", "items"}
                and type(value.get("items")) is list,
                "a sequence observable lost its Python carrier type")
        for item in value["items"]:
            validate_normalized_value(item)
    elif kind == "dict":
        require(set(value) == {"type", "items"}
                and type(value.get("items")) is list,
                "a mapping observable was forged")
        previous: bytes | None = None
        for pair in value["items"]:
            require(type(pair) is list and len(pair) == 2,
                    "a canonical mapping entry was omitted")
            validate_normalized_value(pair[0])
            validate_normalized_value(pair[1])
            ordering = canonical(pair[0])
            require(previous is None or previous < ordering,
                    "a mapping key was duplicated or reordered")
            previous = ordering
    elif kind == "memoryview":
        require(
            set(value) == {
                "type", "hex", "readonly", "format", "itemsize", "ndim",
                "shape", "strides", "contiguous", "c_contiguous",
                "f_contiguous",
            }
            and type(value.get("hex")) is str
            and type(value.get("readonly")) is bool
            and type(value.get("format")) is str
            and type(value.get("itemsize")) is int
            and type(value.get("ndim")) is int
            and all(type(value.get(name)) is bool for name in (
                "contiguous", "c_contiguous", "f_contiguous",
            )),
            "a real memoryview shape, format, or mutability was hidden",
        )
        try:
            raw = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise ManagedBufferOracleError("memoryview hex is invalid") from error
        require(raw.hex() == value["hex"], "memoryview hex is noncanonical")
        for name in ("shape", "strides"):
            item = value[name]
            require(item is None or (
                type(item) is list and all(type(part) is int for part in item)
            ), "a real memoryview dimension was substituted")
    elif kind == "released-memoryview":
        require(set(value) == {
            "type", "error_module", "error_type", "error_args",
        } and type(value.get("error_module")) is str
            and type(value.get("error_type")) is str,
            "a released memoryview exception was hidden")
        validate_normalized_value(value["error_args"])
    elif kind == "managed-exporter":
        require(set(value) == {
            "type", "role", "behavior", "backing_hex", "active_exports",
        } and value.get("role") in {"subject", "template"}
            and value.get("behavior") in {"stable", "overwrite", "error"}
            and type(value.get("backing_hex")) is str
            and type(value.get("active_exports")) is int
            and value["active_exports"] >= 0,
            "a tracked buffer exporter was concealed")
        try:
            raw = bytes.fromhex(value["backing_hex"])
        except ValueError as error:
            raise ManagedBufferOracleError("exporter hex is invalid") from error
        require(raw.hex() == value["backing_hex"],
                "exporter storage was encoded noncanonically")
    else:
        raise ManagedBufferOracleError("an unknown observable type was injected")


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
        "args": normalize_value(error.args),
    }


def validate_normalized_error(value: Any) -> None:
    require(type(value) is dict, "an exact Python exception is mandatory")
    if value.get("kind") == "ordinary-python-error":
        require(set(value) == {"kind", "module", "type", "args"}
                and type(value.get("module")) is str
                and type(value.get("type")) is str,
                "an exact built-in exception type or module was hidden")
        validate_normalized_value(value["args"])
        return
    require(value.get("kind") == "public-regex-error"
            and set(value) == {
                "kind", "type", "args", "message", "pattern", "position",
                "line", "column",
            } and type(value.get("type")) is str,
            "a public regex exception or position was hidden")
    for name in ("args", "message", "pattern", "position", "line", "column"):
        validate_normalized_value(value[name])


def normalize_pattern(pattern: Any) -> dict[str, Any]:
    flags = pattern.flags
    groups = pattern.groups
    require(type(flags) is int and type(groups) is int and groups >= 0,
            "compiled pattern metadata was forged")
    index = dict(pattern.groupindex)
    return {
        "pattern": normalize_value(pattern.pattern),
        "flags": flags,
        "groups": groups,
        "groupindex": [
            [name, number] for name, number in sorted(index.items())
        ],
    }


def normalize_match(
    match: Any,
    *,
    subject: Any,
    pattern: Any,
) -> dict[str, Any]:
    actual = match.re
    return {
        "pattern": normalize_pattern(actual),
        "pattern_is_expected": actual is pattern,
        "string_is_subject": match.string is subject,
        "string": normalize_value(match.string),
        "group": normalize_value(match.group(0)),
        "groups": normalize_value(match.groups()),
        "groupdict": normalize_value(match.groupdict()),
        "regs": normalize_value(match.regs),
        "lastindex": normalize_value(match.lastindex),
        "lastgroup": normalize_value(match.lastgroup),
        "pos": normalize_value(match.pos),
        "endpos": normalize_value(match.endpos),
    }


def normalize_warnings(observed: list[Any]) -> list[dict[str, str]]:
    require(type(observed) is list, "a complete warning sequence is mandatory")
    result: list[dict[str, str]] = []
    for warning in observed:
        require(
            isinstance(warning.category, type)
            and isinstance(warning.message, warning.category),
            "a genuine Python warning was substituted",
        )
        result.append({
            "category_module": warning.category.__module__,
            "category": warning.category.__qualname__,
            "message": str(warning.message),
        })
    return result


def event_snapshot(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(event) for event in events]


def checkpoint(
    checkpoints: list[dict[str, Any]], label: str, subject: Any,
    backing: bytearray | None, events: list[dict[str, Any]],
    trackers: list[TrackedExporter],
) -> None:
    require(type(label) is str and bool(label),
            "a deterministic lifetime checkpoint is mandatory")
    checkpoints.append({
        "label": label,
        "subject": normalize_value(subject),
        "backing_hex": bytes(backing).hex() if backing is not None else None,
        "events": event_snapshot(events),
        "active_exports": [
            {"role": item.role, "count": item.active}
            for item in trackers
        ],
    })


def observe_attempt(action: Callable[[], Any], engine: Any) -> dict[str, Any]:
    try:
        value = action()
    except ManagedBufferOracleError:
        raise
    except Exception as error:
        return {
            "status": "raise",
            "value": None,
            "exception": normalize_error(error, engine),
        }
    return {
        "status": "return",
        "value": normalize_value(value),
        "exception": None,
    }


def run_public_scanner(
    case: Mapping[str, Any], engine: Any, subject: Any,
    callbacks: list[dict[str, Any]],
) -> dict[str, Any]:
    byte_mode = not isinstance(subject, str)
    first = rb"([A-Za-z]+)" if byte_mode else r"([A-Za-z]+)"
    second = rb"([0-9]+)" if byte_mode else r"([0-9]+)"
    whitespace = rb"\s+" if byte_mode else r"\s+"
    zero = b"" if byte_mode else ""
    variant = case["variant"]

    def primary(scanner: Any, token: Any) -> Any:
        actual = scanner.match
        callbacks.append({
            "action": "primary",
            "scanner_is_owner": scanner is scanner_owner[0],
            "match_is_scanner_match": actual is scanner.match,
            "match_pattern_is_combined": actual.re is scanner.scanner,
            "combined_pattern_is_none": scanner.scanner.pattern is None,
            "token": normalize_value(token),
            "lastindex": normalize_value(actual.lastindex),
            "position": normalize_value(actual.pos),
            "span": normalize_value(actual.span()),
            "match": normalize_match(
                actual, subject=subject, pattern=scanner.scanner,
            ),
        })
        if variant % 16 == 15:
            raise LookupError("frozen managed-buffer scanner callback failure")
        return ("word", token)

    def mutated(scanner: Any, token: Any) -> Any:
        actual = scanner.match
        callbacks.append({
            "action": "mutated",
            "scanner_is_owner": scanner is scanner_owner[0],
            "match_is_scanner_match": actual is scanner.match,
            "match_pattern_is_combined": actual.re is scanner.scanner,
            "combined_pattern_is_none": scanner.scanner.pattern is None,
            "token": normalize_value(token),
            "lastindex": normalize_value(actual.lastindex),
            "position": normalize_value(actual.pos),
            "span": normalize_value(actual.span()),
            "match": normalize_match(
                actual, subject=subject, pattern=scanner.scanner,
            ),
        })
        return ("mutated", token)

    def number(scanner: Any, token: Any) -> Any:
        actual = scanner.match
        callbacks.append({
            "action": "number",
            "scanner_is_owner": scanner is scanner_owner[0],
            "match_is_scanner_match": actual is scanner.match,
            "match_pattern_is_combined": actual.re is scanner.scanner,
            "combined_pattern_is_none": scanner.scanner.pattern is None,
            "token": normalize_value(token),
            "lastindex": normalize_value(actual.lastindex),
            "position": normalize_value(actual.pos),
            "span": normalize_value(actual.span()),
            "match": normalize_match(
                actual, subject=subject, pattern=scanner.scanner,
            ),
        })
        return ("number", token)

    lexicon: list[tuple[Any, Any]] = [
        (first, primary), (second, number), (whitespace, None),
    ]
    if variant % 11 == 10:
        lexicon.insert(0, (zero, primary))
    scanner_owner: list[Any] = [None]
    scanner = engine.Scanner(lexicon, case["flags"])
    scanner_owner[0] = scanner
    original_identity = scanner.lexicon is lexicon
    if case["action"] == "mutate-public-scanner-lexicon" and variant % 2:
        target = 1 if variant % 11 == 10 else 0
        lexicon[target] = (lexicon[target][0], mutated)
    result = scanner.scan(subject)
    return {
        "result": normalize_value(result),
        "lexicon_is_original": original_identity,
        "lexicon_remains_original": scanner.lexicon is lexicon,
        "combined_pattern": normalize_pattern(scanner.scanner),
        "callbacks": [dict(item) for item in callbacks],
        "has_match": hasattr(scanner, "match"),
        "final_match": (
            normalize_match(
                scanner.match, subject=subject, pattern=scanner.scanner,
            ) if hasattr(scanner, "match") else None
        ),
    }


def execute_case(case: Mapping[str, Any], engine: Any) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    callbacks: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    trackers: list[TrackedExporter] = []
    state: dict[str, Any] = {"stage": "materialize"}
    with warnings.catch_warnings(record=True) as observed_warnings:
        warnings.simplefilter("always")
        try:
            pattern = decode_pattern(case["pattern"])
            subject, backing, subject_tracker = decode_carrier(
                case["subject"], events, role="subject",
            )
            if subject_tracker is not None:
                trackers.append(subject_tracker)
            template, replacement_tracker = decode_template(
                case["template"], events,
            )
            if replacement_tracker is not None:
                trackers.append(replacement_tracker)
            checkpoint(
                checkpoints, "materialized", subject, backing, events, trackers,
            )
            if case["action"] == "release-before-operation":
                require(type(subject) is memoryview,
                        "only a genuine subject memoryview may be released")
                subject.release()
                checkpoint(
                    checkpoints, "subject-released-before-operation", subject,
                    backing, events, trackers,
                )

            if case["operation"] == "public.scanner.scan":
                state["stage"] = "public-scanner-scan"
                result = run_public_scanner(case, engine, subject, callbacks)
                checkpoint(
                    checkpoints, "public-scanner-finished", subject, backing,
                    events, trackers,
                )
            else:
                state["stage"] = "compile"
                compiled = engine.compile(pattern, case["flags"])
                checkpoint(
                    checkpoints, "compiled", subject, backing, events, trackers,
                )
                operation = case["operation"]
                action = case["action"]

                if operation in {"search", "match", "fullmatch"}:
                    state["stage"] = operation
                    match = getattr(compiled, operation)(subject)
                    result = (
                        None if match is None
                        else normalize_match(
                            match, subject=subject, pattern=compiled,
                        )
                    )
                elif operation == "findall":
                    state["stage"] = "findall"
                    result = normalize_value(compiled.findall(subject))
                elif operation == "split":
                    state["stage"] = "split"
                    result = normalize_value(
                        compiled.split(subject, case["variant"] % 4)
                    )
                elif operation in {"sub", "subn"}:
                    state["stage"] = operation
                    result = normalize_value(
                        getattr(compiled, operation)(
                            template, subject, case["variant"] % 4,
                        )
                    )
                elif operation in {"match.group", "match.groups", "match.expand"}:
                    state["stage"] = "search"
                    match = compiled.search(subject)
                    checkpoint(
                        checkpoints, "match-created", subject, backing,
                        events, trackers,
                    )
                    if match is None:
                        result = None
                    else:
                        if action == "release-after-match":
                            require(type(subject) is memoryview,
                                    "only a real matched memoryview can release")
                            subject.release()
                            checkpoint(
                                checkpoints, "subject-released-after-match",
                                subject, backing, events, trackers,
                            )
                        elif action == "mutate-backing-after-match":
                            require(type(backing) is bytearray and len(backing) > 0,
                                    "a real mutable subject backing is mandatory")
                            previous = backing[0]
                            backing[0] = 90 if previous != 90 else 81
                            checkpoint(
                                checkpoints, "backing-mutated-after-match",
                                subject, backing, events, trackers,
                            )
                        state["stage"] = operation
                        if operation == "match.group":
                            result = normalize_value(
                                match.group(case["variant"] % 3)
                            )
                        elif operation == "match.groups":
                            result = normalize_value(match.groups())
                        else:
                            result = normalize_value(match.expand(template))
                elif operation == "finditer":
                    state["stage"] = "finditer-create"
                    iterator = compiled.finditer(subject)
                    checkpoint(
                        checkpoints, "iterator-created", subject, backing,
                        events, trackers,
                    )
                    values: list[Any] = []
                    if action == "resize-during-live-iterator":
                        require(type(backing) is bytearray,
                                "the live resize control needs a bytearray")
                        attempt = observe_attempt(
                            lambda: backing.append(33), engine,
                        )
                        checkpoint(
                            checkpoints, "resize-attempted-with-live-iterator",
                            subject, backing, events, trackers,
                        )
                        state["stage"] = "finditer-next"
                        first = next(iterator, None)
                        if first is not None:
                            values.append(normalize_match(
                                first, subject=subject, pattern=compiled,
                            ))
                        result = {
                            "resize": attempt,
                            "matches": values,
                        }
                    elif action == "resize-after-iterator-teardown":
                        require(type(backing) is bytearray,
                                "the post-teardown resize needs a bytearray")
                        state["stage"] = "finditer-delete"
                        del iterator
                        gc.collect()
                        checkpoint(
                            checkpoints, "iterator-deleted-before-resize",
                            subject, backing, events, trackers,
                        )
                        result = {
                            "resize": observe_attempt(
                                lambda: backing.append(33), engine,
                            ),
                            "matches": values,
                        }
                    elif action == "delete-iterator-and-gc":
                        state["stage"] = "finditer-next"
                        first = next(iterator, None)
                        if first is not None:
                            values.append(normalize_match(
                                first, subject=subject, pattern=compiled,
                            ))
                        checkpoint(
                            checkpoints, "iterator-advanced-before-deletion",
                            subject, backing, events, trackers,
                        )
                        del first
                        del iterator
                        gc.collect()
                        checkpoint(
                            checkpoints, "iterator-deleted-and-collected",
                            subject, backing, events, trackers,
                        )
                        result = {"matches": values}
                    else:
                        state["stage"] = "finditer-next"
                        for match in iterator:
                            values.append(normalize_match(
                                match, subject=subject, pattern=compiled,
                            ))
                            if action == "observe-iterator-advance" and len(values) == 2:
                                checkpoint(
                                    checkpoints, "iterator-advanced-twice",
                                    subject, backing, events, trackers,
                                )
                                break
                        if action == "observe-iterator-exhaust":
                            checkpoint(
                                checkpoints, "iterator-exhausted", subject,
                                backing, events, trackers,
                            )
                        result = {"matches": values}
                elif operation in {
                    "compiled.scanner.search", "compiled.scanner.match",
                }:
                    state["stage"] = "scanner-create"
                    scanner = compiled.scanner(subject)
                    checkpoint(
                        checkpoints, "native-scanner-created", subject,
                        backing, events, trackers,
                    )
                    method = "search" if operation.endswith("search") else "match"
                    state["stage"] = "scanner-" + method
                    values = []
                    for _ in range(3):
                        item = getattr(scanner, method)()
                        if item is None:
                            values.append(None)
                            break
                        values.append(normalize_match(
                            item, subject=subject, pattern=compiled,
                        ))
                    checkpoint(
                        checkpoints, "native-scanner-advanced", subject,
                        backing, events, trackers,
                    )
                    del scanner
                    gc.collect()
                    checkpoint(
                        checkpoints, "native-scanner-deleted-and-collected",
                        subject, backing, events, trackers,
                    )
                    result = {"matches": values}
                else:
                    raise ManagedBufferOracleError(
                        "an unfrozen managed-buffer operation was selected"
                    )

            checkpoint(
                checkpoints, "operation-completed", subject, backing,
                events, trackers,
            )
            return {
                "status": "return",
                "stage": state["stage"],
                "value": result,
                "exception": None,
                "events": event_snapshot(events),
                "checkpoints": checkpoints,
                "callbacks": callbacks,
                "warnings": normalize_warnings(observed_warnings),
            }
        except ManagedBufferOracleError:
            raise
        except Exception as error:
            return {
                "status": "raise",
                "stage": state["stage"],
                "value": None,
                "exception": normalize_error(error, engine),
                "events": event_snapshot(events),
                "checkpoints": checkpoints,
                "callbacks": callbacks,
                "warnings": normalize_warnings(observed_warnings),
            }


def validate_events(events: Any) -> None:
    require(type(events) is list, "the entire buffer event sequence is mandatory")
    live: dict[str, int] = {"subject": 0, "template": 0}
    for event in events:
        require(
            type(event) is dict
            and set(event) == {
                "event", "role", "flags", "active_before", "active_after",
                "backing_before_hex", "backing_after_hex", "behavior",
            }
            and event.get("event") in {"acquire", "acquire-error", "release"}
            and event.get("role") in {"subject", "template"}
            and event.get("behavior") in {"stable", "overwrite", "error"}
            and type(event.get("active_before")) is int
            and type(event.get("active_after")) is int
            and event["active_before"] >= 0 and event["active_after"] >= 0
            and type(event.get("backing_before_hex")) is str
            and type(event.get("backing_after_hex")) is str,
            "a real PEP-688 acquire or release event was omitted",
        )
        for name in ("backing_before_hex", "backing_after_hex"):
            try:
                raw = bytes.fromhex(event[name])
            except ValueError as error:
                raise ManagedBufferOracleError(
                    "a managed exporter event contains invalid bytes"
                ) from error
            require(raw.hex() == event[name],
                    "a managed exporter event contains noncanonical bytes")
        role = event["role"]
        require(event["active_before"] == live[role],
                "a real exporter acquisition or release was reordered")
        if event["event"] == "acquire":
            require(type(event["flags"]) is int
                    and event["active_after"] == live[role] + 1
                    and event["backing_before_hex"] == event["backing_after_hex"],
                    "a real exporter acquisition or flags were forged")
            live[role] += 1
        elif event["event"] == "acquire-error":
            require(type(event["flags"]) is int
                    and event["behavior"] == "error"
                    and event["active_after"] == live[role]
                    and event["backing_before_hex"] == event["backing_after_hex"],
                    "a real exporter failure was omitted or reordered")
        else:
            require(event["flags"] is None and live[role] > 0
                    and event["active_after"] == live[role] - 1,
                    "a managed exporter was released without ownership")
            before = bytes.fromhex(event["backing_before_hex"])
            after = bytes.fromhex(event["backing_after_hex"])
            require(len(before) == len(after),
                    "an exporter release resized or freed its storage")
            if event["behavior"] == "overwrite":
                require(after == b"!" * len(before),
                        "the exact safe same-length release overwrite changed")
            else:
                require(before == after,
                        "a stable exporter unexpectedly changed its backing")
            live[role] -= 1


def validate_checkpoint(value: Any, prior_events: list[dict[str, Any]]) -> None:
    require(type(value) is dict
            and set(value) == {
                "label", "subject", "backing_hex", "events", "active_exports",
            }
            and type(value.get("label")) is str and bool(value["label"])
            and (value.get("backing_hex") is None
                 or type(value.get("backing_hex")) is str)
            and type(value.get("active_exports")) is list,
            "a full deterministic buffer-lifetime checkpoint was omitted")
    validate_normalized_value(value["subject"])
    validate_events(value["events"])
    require(len(value["events"]) >= len(prior_events)
            and value["events"][:len(prior_events)] == prior_events,
            "a checkpoint concealed or reordered prior buffer events")
    if value["backing_hex"] is not None:
        try:
            raw = bytes.fromhex(value["backing_hex"])
        except ValueError as error:
            raise ManagedBufferOracleError("a checkpoint backing is invalid") from error
        require(raw.hex() == value["backing_hex"],
                "a checkpoint backing was encoded noncanonically")
    roles: set[str] = set()
    for item in value["active_exports"]:
        require(type(item) is dict and set(item) == {"role", "count"}
                and item.get("role") in {"subject", "template"}
                and item["role"] not in roles
                and type(item.get("count")) is int and item["count"] >= 0,
                "a real live-export ownership count was hidden")
        roles.add(item["role"])


def validate_outcome(value: Any) -> None:
    require(type(value) is dict
            and set(value) == {
                "status", "stage", "value", "exception", "events",
                "checkpoints", "callbacks", "warnings",
            }
            and value.get("status") in {"return", "raise"}
            and type(value.get("stage")) is str
            and type(value.get("checkpoints")) is list
            and type(value.get("callbacks")) is list
            and type(value.get("warnings")) is list,
            "a complete managed-buffer outcome or lifecycle was omitted")
    if value["status"] == "return":
        require(value["exception"] is None,
                "a normal result contains a concealed Python exception")
        canonical(value["value"])
    else:
        require(value["value"] is None,
                "a raising result concealed a successful return")
        validate_normalized_error(value["exception"])
    validate_events(value["events"])
    previous: list[dict[str, Any]] = []
    for item in value["checkpoints"]:
        validate_checkpoint(item, previous)
        previous = item["events"]
    require(value["events"][:len(previous)] == previous,
            "a final outcome concealed checkpointed exporter events")
    for callback in value["callbacks"]:
        require(type(callback) is dict and set(callback) == {
            "action", "scanner_is_owner", "match_is_scanner_match",
            "match_pattern_is_combined", "combined_pattern_is_none", "token",
            "lastindex", "position", "span", "match",
        } and callback.get("action") in {"primary", "mutated", "number"}
            and all(type(callback.get(key)) is bool for key in (
                "scanner_is_owner", "match_is_scanner_match",
                "match_pattern_is_combined", "combined_pattern_is_none",
            )), "a complete public scanner callback identity was hidden")
        for name in ("token", "lastindex", "position", "span"):
            validate_normalized_value(callback[name])
        require(type(callback.get("match")) is dict,
                "a complete callback match was omitted")
    for warning in value["warnings"]:
        require(type(warning) is dict
                and set(warning) == {"category_module", "category", "message"}
                and all(type(warning.get(key)) is str for key in warning),
                "a genuine managed-buffer warning was omitted")


def validate_records(
    matrix: list[dict[str, Any]], records: Any, expected_sha256: str,
) -> list[dict[str, Any]]:
    checked_digest(expected_sha256, "complete managed-buffer observations")
    require(type(records) is list and len(records) == CASE_COUNT,
            "all 1,024 managed-buffer outcomes must be retained")
    for case, observed in zip(matrix, records, strict=True):
        require(type(observed) is dict
                and set(observed) == {"case", "group", "variant", "outcome"}
                and observed.get("case") == case["case"]
                and observed.get("group") == case["group"]
                and observed.get("variant") == case["variant"],
                "a managed-buffer outcome was omitted, reordered, or relabeled")
        validate_outcome(observed["outcome"])
    require(digest(records) == expected_sha256,
            "the complete managed-buffer outcome digest was substituted")
    return records


def validate_future_candidate_pins(value: Any) -> dict[str, str]:
    require(type(value) is dict and set(value) == {
        "family", "adapter_relative", "adapter_sha256", "engine_relative",
        "engine_sha256", "bridge_relative", "bridge_sha256",
        "v5_guard_relative", "v5_guard_sha256", "ownership_audit_relative",
        "ownership_audit_sha256",
    }, "a future V5-guarded candidate source closure is mandatory")
    family = value.get("family")
    require(family in {"rust", "c", "zig"},
            "an independently owned candidate family is mandatory")
    expected_adapters = {
        "rust": "candidates/rust_candidate.py",
        "c": "candidates/vm_candidate.py",
        "zig": "candidates/zig_candidate.py",
    }
    expected_engines = {
        "rust": "candidates/_rust_engine.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_probe.so",
    }
    expected_bridges = {
        "rust": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }
    require(value["adapter_relative"] == expected_adapters[family]
            and value["engine_relative"] == expected_engines[family]
            and value["bridge_relative"] == expected_bridges[family],
            "a sibling, foreign package, or native component was substituted")
    require(value["v5_guard_relative"] == V5_GUARD_RELATIVE
            and value["v5_guard_sha256"] == V5_GUARD_SHA256
            and value["ownership_audit_relative"] == OWNERSHIP_AUDIT_RELATIVE
            and value["ownership_audit_sha256"] == OWNERSHIP_AUDIT_SHA256,
            "the frozen Zig-safe V5 guard or ownership audit was substituted")
    for name in ("adapter_sha256", "engine_sha256", "bridge_sha256"):
        checked_digest(value[name], "future candidate " + name)
    require((value["engine_relative"] == value["bridge_relative"])
            == (family == "c"),
            "the combined C or distinct Rust/Zig native owner was substituted")
    require((value["engine_sha256"] == value["bridge_sha256"])
            == (family == "c"),
            "an independent native owner or bridge digest was substituted")
    return dict(value)


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == SOURCE_ABSOLUTE
        and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
        "use only the pinned isolated CPython 3.14.6 and exact frozen oracle",
    )


def read_pinned_file(
    absolute: str, expected_sha256: str, *, label: str,
) -> dict[str, Any]:
    checked_digest(expected_sha256, label)
    require(type(absolute) is str and os.path.isabs(absolute)
            and os.path.abspath(absolute) == absolute
            and os.path.realpath(absolute) == absolute,
            "an exact regular source path is mandatory: " + label)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise ManagedBufferOracleError(
            "an exact pinned file could not be opened: " + label
        ) from error
    try:
        before = os.fstat(descriptor)
        maximum = MAX_BINARY_BYTES if absolute == PINNED_PYTHON else MAX_SOURCE_BYTES
        require(stat.S_ISREG(before.st_mode)
                and 0 < before.st_size <= maximum,
                "a pinned file is not a bounded regular source or binary: "
                + label)
        actual = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(bool(part), "a pinned file was truncated: " + label)
            actual.update(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "a pinned file grew while being authenticated: " + label)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size)
                and actual.hexdigest() == expected_sha256,
                "a pinned source, binary, or owner changed: " + label)
        return {
            "path": absolute,
            "sha256": expected_sha256,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        os.close(descriptor)


def authenticate_standard_reference(
    source_pin: str,
) -> tuple[Any, dict[str, dict[str, Any]]]:
    verify_runtime()
    source = read_pinned_file(
        SOURCE_ABSOLUTE, source_pin, label="frozen managed-buffer oracle",
    )
    python = read_pinned_file(
        PINNED_PYTHON, PINNED_PYTHON_SHA256,
        label="pinned CPython 3.14.6 executable",
    )
    engine = importlib.import_module("re")
    owners: dict[str, dict[str, Any]] = {
        "oracle": source,
        "python": python,
    }
    for module_name, (filename, pinned) in PINNED_STDLIB_SOURCES.items():
        absolute = PINNED_STDLIB_DIRECTORY + filename
        module = importlib.import_module(module_name)
        require(isinstance(module, types.ModuleType)
                and module.__name__ == module_name
                and getattr(module, "__file__", None) == absolute
                and os.path.realpath(absolute) == absolute,
                "a genuine pinned CPython regex module was substituted: "
                + module_name)
        owners[module_name] = read_pinned_file(
            absolute, pinned, label="pinned standard " + module_name,
        )
    builtin = sys.modules.get("_sre")
    require(isinstance(builtin, types.ModuleType)
            and getattr(getattr(builtin, "__spec__", None), "origin", None)
            == "built-in"
            and engine.__name__ == "re"
            and getattr(engine.compile, "__module__", None) == "re"
            and getattr(engine.Scanner, "__module__", None) == "re",
            "the genuine built-in CPython baseline was substituted")
    verify_standard_modules()
    return engine, owners


def verify_standard_modules(modules: Mapping[str, Any] | None = None) -> None:
    observed = sys.modules if modules is None else modules
    require(isinstance(observed, Mapping),
            "an exact reference module table is mandatory")
    for name in observed:
        require(type(name) is str, "an invalid reference module was injected")
        root = name.partition(".")[0]
        require(root != "candidates" and root not in FORBIDDEN_ENGINE_ROOTS,
                "a native candidate or external regex entered a CPython worker")


def validate_source_owners(
    value: Any, source_pin: str,
) -> dict[str, dict[str, Any]]:
    require(type(value) is dict
            and set(value) == {"oracle", "python", *PINNED_STDLIB_SOURCES},
            "a complete pinned CPython source closure is mandatory")
    expected: dict[str, tuple[str, str]] = {
        "oracle": (SOURCE_ABSOLUTE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
    }
    for name, (filename, pinned) in PINNED_STDLIB_SOURCES.items():
        expected[name] = (PINNED_STDLIB_DIRECTORY + filename, pinned)
    for name, (path, pinned) in expected.items():
        owner = value.get(name)
        require(type(owner) is dict
                and set(owner) == {"path", "sha256", "bytes", "device", "inode"}
                and owner.get("path") == path
                and owner.get("sha256") == pinned
                and type(owner.get("bytes")) is int and owner["bytes"] > 0
                and type(owner.get("device")) is int and owner["device"] >= 0
                and type(owner.get("inode")) is int and owner["inode"] > 0,
                "a pinned genuine CPython source owner was forged: " + name)
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
    require(type(value) is dict
            and set(value) == {
                "candidate_import_count", "external_regex_import_count",
                "actual_method_guard_checks", "required_method_guard_checks",
                "future_candidate_guard_relative", "future_candidate_guard_sha256",
                "future_ownership_audit_relative", "future_ownership_audit_sha256",
                "future_candidate_guard_installed",
            }
            and value.get("candidate_import_count") == 0
            and value.get("external_regex_import_count") == 0
            and value.get("actual_method_guard_checks") == 2 * CASE_COUNT
            and value.get("required_method_guard_checks") == 2 * CASE_COUNT
            and value.get("future_candidate_guard_relative") == V5_GUARD_RELATIVE
            and value.get("future_candidate_guard_sha256") == V5_GUARD_SHA256
            and value.get("future_ownership_audit_relative")
            == OWNERSHIP_AUDIT_RELATIVE
            and value.get("future_ownership_audit_sha256")
            == OWNERSHIP_AUDIT_SHA256
            and value.get("future_candidate_guard_installed") is False,
            "a genuine reference or future Zig-safe V5 guard was forged")
    return value


def observe_reference_worker(role: str, source_pin: str) -> dict[str, Any]:
    require(role in {"reference_a", "reference_b"},
            "only one explicit genuine standard-reference role is permitted")
    checked_digest(source_pin, "frozen managed-buffer source")
    matrix = build_matrix()
    validate_matrix(matrix)
    engine, owners = authenticate_standard_reference(source_pin)
    checks = 0
    records: list[dict[str, Any]] = []
    for case in matrix:
        verify_standard_modules()
        checks += 1
        try:
            outcome = execute_case(case, engine)
        finally:
            verify_standard_modules()
            checks += 1
        validate_outcome(outcome)
        records.append({
            "case": case["case"],
            "group": case["group"],
            "variant": case["variant"],
            "outcome": outcome,
        })
    records_sha256 = digest(records)
    validate_records(matrix, records, records_sha256)
    owners_after = authenticate_standard_reference(source_pin)[1]
    require(owners == owners_after,
            "a pinned genuine CPython owner changed during observation")
    document = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": os.getpid(),
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": VARIANTS_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
        "records_sha256": records_sha256,
        "records": records,
        "source_owners": owners,
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
    validate_reference_worker(
        document, role=role, source_pin=source_pin, matrix=matrix,
        expected_pid=os.getpid(),
    )
    return document


def validate_reference_worker(
    value: Any,
    *,
    role: str,
    source_pin: str,
    matrix: list[dict[str, Any]],
    expected_pid: int,
) -> dict[str, Any]:
    require(role in {"reference_a", "reference_b"}
            and type(expected_pid) is int and expected_pid > 0,
            "an independent genuine worker role and PID are mandatory")
    require(type(value) is dict, "a complete genuine worker is mandatory")
    expected = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": expected_pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": VARIANTS_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
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
    require(set(value) == set(expected) | {
        "records_sha256", "records", "source_owners", "reference_guard",
    }, "a genuine worker omitted or added complete evidence fields")
    for name, actual in expected.items():
        require(value.get(name) == actual,
                "a frozen genuine reference worker changed: " + name)
    validate_source_owners(value.get("source_owners"), source_pin)
    validate_reference_guard(value.get("reference_guard"))
    validate_records(matrix, value.get("records"), value.get("records_sha256"))
    return value


def encode_stream(value: bytes) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
            "a complete bounded genuine reference stream is mandatory")
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": True,
    }


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"base64", "bytes", "sha256", "complete"}
            and type(value.get("base64")) is str
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and valid_digest(value.get("sha256"))
            and value.get("complete") is True,
            "a complete reversible process stream was omitted: " + label)
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise ManagedBufferOracleError(
            "a complete process stream is not valid base64: " + label
        ) from error
    require(len(raw) == value["bytes"]
            and hashlib.sha256(raw).hexdigest() == value["sha256"]
            and base64.b64encode(raw).decode("ascii") == value["base64"],
            "a complete genuine reference stream was forged: " + label)
    return raw


def validate_process_evidence(
    evidence: Any, worker: Mapping[str, Any], *, role: str,
) -> dict[str, Any]:
    require(type(evidence) is dict
            and set(evidence) == {"role", "pid", "returncode", "stdout", "stderr"}
            and evidence.get("role") == role
            and type(evidence.get("pid")) is int and evidence["pid"] > 0
            and evidence["pid"] == worker.get("pid")
            and evidence.get("returncode") == 0,
            "a real isolated reference process was substituted")
    stdout = decode_stream(evidence.get("stdout"), role + " stdout")
    stderr = decode_stream(evidence.get("stderr"), role + " stderr")
    require(stderr == b"" and stdout == canonical(dict(worker)),
            "a real reference stream is incomplete or differs from its record")
    return evidence


def run_isolated_reference(
    role: str, source_pin: str, matrix: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in {"reference_a", "reference_b"},
            "no candidate or other worker may enter the baseline phase")
    arguments = [
        PINNED_PYTHON, "-I", "-B", SOURCE_ABSOLUTE,
        "--internal-reference-worker", "--role", role,
        "--oracle-source-sha256", source_pin,
        "--matrix-sha256", MATRIX_SHA256,
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
            "a genuine pinned reference process could not start",
            {
                "role": role,
                "error_type": type(error).__qualname__,
                "error": str(error),
            },
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
            "a genuine pinned reference process failed", evidence,
        )
    try:
        result = validate_reference_worker(
            decode_canonical(stdout, role), role=role, source_pin=source_pin,
            matrix=matrix, expected_pid=process.pid,
        )
        validate_process_evidence(evidence, result, role=role)
    except (ManagedBufferOracleError, ValueError, TypeError, KeyError) as error:
        evidence["validation_error"] = {
            "type": type(error).__qualname__,
            "message": str(error),
        }
        raise ReferenceWorkerFailure(
            "the complete genuine reference process was rejected", evidence,
        ) from error
    return result, evidence


def validate_reference_pair(
    first: Mapping[str, Any], second: Mapping[str, Any],
    first_process: Mapping[str, Any], second_process: Mapping[str, Any],
    *,
    source_pin: str,
    matrix: list[dict[str, Any]],
) -> str:
    validate_reference_worker(
        first, role="reference_a", source_pin=source_pin,
        matrix=matrix, expected_pid=first.get("pid"),
    )
    validate_reference_worker(
        second, role="reference_b", source_pin=source_pin,
        matrix=matrix, expected_pid=second.get("pid"),
    )
    validate_process_evidence(first_process, first, role="reference_a")
    validate_process_evidence(second_process, second, role="reference_b")
    require(first["pid"] != second["pid"]
            and first["source_owners"] == second["source_owners"]
            and first["records_sha256"] == second["records_sha256"]
            and first["records"] == second["records"],
            "two genuine isolated CPython references did not exactly agree")
    return first["records_sha256"]


def run_baseline(source_pin: str, matrix_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "prospectively frozen managed-buffer source")
    checked_digest(matrix_pin, "prospectively frozen managed-buffer matrix")
    require(matrix_pin == MATRIX_SHA256,
            "the explicitly frozen managed-buffer matrix was substituted")
    matrix = build_matrix()
    validate_matrix(matrix, matrix_pin)
    engine, owners_before = authenticate_standard_reference(source_pin)
    require(engine.__name__ == "re",
            "the genuine baseline reference was substituted")
    first, first_process = run_isolated_reference(
        "reference_a", source_pin, matrix,
    )
    second, second_process = run_isolated_reference(
        "reference_b", source_pin, matrix,
    )
    records_sha256 = validate_reference_pair(
        first, second, first_process, second_process,
        source_pin=source_pin, matrix=matrix,
    )
    owners_after = authenticate_standard_reference(source_pin)[1]
    require(owners_before == owners_after == first["source_owners"],
            "a pinned genuine source changed around baseline observations")
    return {
        "schema": SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": VARIANTS_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
        "baseline_records_sha256": records_sha256,
        "source_owners": owners_before,
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
    """Deny real file, process, import, clock, and thread effects."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked: dict[str, int] = {
            "file_reads": 0,
            "file_writes": 0,
            "processes": 0,
            "candidate_imports": 0,
            "dynamic_imports": 0,
            "clock_samples": 0,
            "threads": 0,
            "garbage_collections": 0,
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
                if (type(mode) is str and any(letter in mode for letter in "wax+")):
                    selected = "file_writes"
                elif (type(mode) is int
                      and mode & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                  | os.O_TRUNC | os.O_APPEND)):
                    selected = "file_writes"
            if category == "dynamic_imports" and args:
                target = args[0]
                if type(target) is str and (
                    target == "candidates" or target.startswith("candidates.")
                ):
                    selected = "candidate_imports"
            self.blocked[selected] += 1
            raise SourceOnlyError(
                "synthetic managed-buffer controls may not perform " + selected
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
            (os, "unlink", "file_writes"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (os, "system", "processes"),
            (os, "posix_spawn", "processes"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clock_samples"),
            (time, "time_ns", "clock_samples"),
            (time, "monotonic", "clock_samples"),
            (time, "monotonic_ns", "clock_samples"),
            (time, "perf_counter", "clock_samples"),
            (time, "perf_counter_ns", "clock_samples"),
            (gc, "collect", "garbage_collections"),
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


def synthetic_owners(source_pin: str) -> dict[str, dict[str, Any]]:
    values: dict[str, tuple[str, str]] = {
        "oracle": (SOURCE_ABSOLUTE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
    }
    for name, (filename, pinned) in PINNED_STDLIB_SOURCES.items():
        values[name] = (PINNED_STDLIB_DIRECTORY + filename, pinned)
    return {
        name: {
            "path": path,
            "sha256": pinned,
            "bytes": 4096 + number,
            "device": 7,
            "inode": 1000 + number,
        }
        for number, (name, (path, pinned)) in enumerate(values.items())
    }


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in matrix:
        subject: dict[str, Any]
        if case["subject"]["kind"] == "str":
            subject = normalize_value(case["subject"]["value"])
        else:
            subject = normalize_value(bytes.fromhex(case["subject"]["hex"]))
        checkpoints = [{
            "label": "synthetic-materialized",
            "subject": subject,
            "backing_hex": None,
            "events": [],
            "active_exports": [],
        }]
        records.append({
            "case": case["case"],
            "group": case["group"],
            "variant": case["variant"],
            "outcome": {
                "status": "return",
                "stage": "synthetic-only",
                "value": normalize_value(None),
                "exception": None,
                "events": [],
                "checkpoints": checkpoints,
                "callbacks": [],
                "warnings": [],
            },
        })
    return records


def synthetic_reference(
    role: str, pid: int, source_pin: str,
    matrix: list[dict[str, Any]], records: list[dict[str, Any]],
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
        "group_count": len(GROUPS),
        "cases_per_group": VARIANTS_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
        "records_sha256": digest(records),
        "records": records,
        "source_owners": synthetic_owners(source_pin),
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


def synthetic_candidate_pins(family: str) -> dict[str, str]:
    require(family in {"rust", "c", "zig"},
            "a real synthetic candidate family is mandatory")
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
    return {
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


def source_self_test() -> dict[str, Any]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "run synthetic controls only on isolated pinned CPython 3.14.6")
    initial_candidate_modules = {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }
    require(not initial_candidate_modules,
            "a candidate entered the synthetic-only managed-buffer process")
    matrix = build_matrix()
    observed_matrix_sha256 = digest(matrix)
    if not valid_digest(MATRIX_SHA256):
        return {
            "schema": SCHEMA + "-synthetic-self-test",
            "status": "UNFROZEN",
            "python": "3.14.6",
            "published_seed": PUBLISHED_SEED,
            "group_count": len(GROUPS),
            "cases_per_group": VARIANTS_PER_GROUP,
            "case_count": CASE_COUNT,
            "observed_matrix_sha256": observed_matrix_sha256,
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
            "message": "pin the prospectively generated matrix before freezing",
        }

    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a synthetic managed-buffer positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a synthetic managed-buffer rejection was duplicated")
        try:
            action()
        except (
            ManagedBufferOracleError, TypeError, ValueError, KeyError,
            OSError, OverflowError,
        ):
            rejected.append(name)
            return
        raise ManagedBufferOracleError(
            "a forged managed-buffer synthetic control was accepted: " + name
        )

    with SourceOnlyBoundary() as boundary:
        accept("freeze-all-32-independent-groups-and-all-1024-cases",
               validate_matrix(matrix) == MATRIX_SHA256)
        accept("preserve-the-exact-public-deterministic-seed",
               PUBLISHED_SEED == 0x4D424C4946455631)
        accept("preserve-all-32-cases-in-every-property-group",
               all(sum(case["group"] == group for case in matrix)
                   == VARIANTS_PER_GROUP for group in GROUPS))
        accept("preserve-all-original-bytes-unicode-and-scanner-operations",
               set(ALL_APIS) == set(case["operation"] for case in matrix))
        accept("pin-the-corrected-zig-safe-v5-native-ownership-guard",
               valid_digest(V5_GUARD_SHA256)
               and valid_digest(OWNERSHIP_AUDIT_SHA256))
        accept("distinguish-bool-from-int", normalize_value(True)
               != normalize_value(1))
        accept("distinguish-bytes-from-bytearray",
               normalize_value(b"a") != normalize_value(bytearray(b"a")))
        accept("distinguish-tuple-from-list",
               normalize_value((1,)) != normalize_value([1]))
        accept("preserve-lone-unicode-surrogates-canonically",
               normalize_value("\ud800")["value"] == "\ud800"
               and b"\\ud800" in canonical(normalize_value("\ud800")))
        accept("preserve-combining-and-precomposed-unicode-independently",
               normalize_value("e\u0301") != normalize_value("é"))

        stable_events: list[dict[str, Any]] = []
        stable_exporter = TrackedExporter(
            b"abc", "stable", stable_events, "subject",
        )
        stable_view = stable_exporter.__buffer__(0)
        stable_exporter.__release_buffer__(stable_view)
        stable_view.release()
        accept("preserve-a-complete-stable-pep688-acquire-and-release",
               validate_events(stable_events) is None
               and bytes(stable_exporter.backing) == b"abc"
               and stable_exporter.active == 0)

        overwrite_events: list[dict[str, Any]] = []
        overwrite_exporter = TrackedExporter(
            b"abc", "overwrite", overwrite_events, "subject",
        )
        overwrite_view = overwrite_exporter.__buffer__(0)
        overwrite_exporter.__release_buffer__(overwrite_view)
        overwrite_view.release()
        accept("preserve-the-safe-equal-length-pep688-release-overwrite",
               validate_events(overwrite_events) is None
               and bytes(overwrite_exporter.backing) == b"!!!"
               and overwrite_exporter.active == 0)

        failure_events: list[dict[str, Any]] = []
        failing_exporter = TrackedExporter(
            b"abc", "error", failure_events, "template",
        )
        try:
            failing_exporter.__buffer__(0)
        except BufferError as actual:
            accept("preserve-a-real-safe-in-memory-failing-exporter",
                   actual.args == (
                       "frozen managed-buffer template exporter failure",
                   ) and validate_events(failure_events) is None
                   and failing_exporter.active == 0)
        else:
            raise ManagedBufferOracleError(
                "a synthetic failing exporter unexpectedly acquired storage"
            )

        records = synthetic_records(matrix)
        records_sha256 = digest(records)
        accept("validate-all-1024-complete-in-memory-synthetic-observations",
               validate_records(matrix, records, records_sha256) is records)
        source_pin = "ab" * 32
        first = synthetic_reference(
            "reference_a", 47001, source_pin, matrix, records,
        )
        second = synthetic_reference(
            "reference_b", 47002, source_pin, matrix, records,
        )
        first_process = synthetic_process(first)
        second_process = synthetic_process(second)
        accept("validate-two-distinct-synthetic-standard-reference-processes",
               validate_reference_pair(
                   first, second, first_process, second_process,
                   source_pin=source_pin, matrix=matrix,
               ) == records_sha256)
        accept("preserve-the-complete-reversible-first-reference-stream",
               validate_process_evidence(
                   first_process, first, role="reference_a",
               ) is first_process)
        accept("preserve-the-complete-reversible-second-reference-stream",
               validate_process_evidence(
                   second_process, second, role="reference_b",
               ) is second_process)

        for family in ("rust", "c", "zig"):
            pins = synthetic_candidate_pins(family)
            accept("validate-future-independent-" + family + "-native-closure",
                   validate_future_candidate_pins(pins) == pins)

        reject("reject-an-omitted-managed-buffer-case",
               lambda: validate_matrix(matrix[:-1]))
        reject("reject-an-extra-managed-buffer-case",
               lambda: validate_matrix(matrix + [matrix[0]]))
        reject("reject-reordered-managed-buffer-cases",
               lambda: validate_matrix(list(reversed(matrix))))
        reject("reject-a-forged-managed-buffer-matrix-hash",
               lambda: validate_matrix(matrix, "12" * 32))
        reject("reject-a-forged-managed-buffer-seed",
               lambda: validate_matrix(build_matrix(PUBLISHED_SEED + 1)))
        for field, replacement in (
            ("case", "managed-buffer-lifetime.v1.9999"),
            ("group", GROUPS[-1]),
            ("variant", 99),
            ("seed", PUBLISHED_SEED + 1),
            ("flags", -1),
            ("operation", "candidate.match"),
            ("action", "tampered"),
        ):
            poisoned = list(matrix)
            row = dict(poisoned[0])
            row[field] = replacement
            poisoned[0] = row
            reject("reject-forged-matrix-field-" + field,
                   lambda poisoned=poisoned: validate_matrix(poisoned))

        for index, carrier in enumerate((
            {"kind": "foreign"},
            carrier_descriptor("bytes", b"abc") | {"hex": "0A"},
            carrier_descriptor("bytes", b"abc") | {"start": -1},
            carrier_descriptor("bytes", b"abc") | {"stop": 4},
            carrier_descriptor("bytes", b"abc") | {"step": 0},
            carrier_descriptor("bytes", b"abc") | {"behavior": "overwrite"},
            carrier_descriptor("tracked-exporter", b"abc", behavior="stable")
            | {"behavior": "none"},
            carrier_descriptor("failing-exporter", b"abc", behavior="error")
            | {"behavior": "stable"},
        )):
            reject("reject-forged-subject-carrier-" + format(index, "02d"),
                   lambda carrier=carrier: validate_carrier_descriptor(carrier))

        for index, template in enumerate((
            template_descriptor("template-memoryview", b"abc")
            | {"readonly": 1},
            template_descriptor("template-memoryview", b"abc")
            | {"released": 0},
            template_descriptor("template-memoryview", b"abc")
            | {"step": 0},
            template_descriptor("template-memoryview", b"abc")
            | {"hex": "GG"},
            template_descriptor("failing-exporter", b"abc", behavior="error")
            | {"behavior": "none"},
        )):
            reject("reject-forged-replacement-carrier-" + format(index, "02d"),
                   lambda template=template:
                   validate_carrier_descriptor(template, template=True))

        for index, item in enumerate((
            {"type": "int", "value": True},
            {"type": "bool", "value": 1},
            {"type": "bytes", "hex": "0A"},
            {"type": "bytes", "hex": "GG"},
            {"type": "tuple", "items": "not-a-sequence"},
            {"type": "str", "value": b"a"},
            {"type": "none", "value": None},
            {"type": "foreign", "value": 1},
            {"type": "dict", "items": [
                [{"type": "str", "value": "x"}, {"type": "none"}],
                [{"type": "str", "value": "x"}, {"type": "none"}],
            ]},
        )):
            reject("reject-forged-exact-python-type-" + format(index, "02d"),
                   lambda item=item: validate_normalized_value(item))

        for index, poisoned_events in enumerate((
            [dict(stable_events[1])],
            [dict(stable_events[1]), dict(stable_events[0])],
            [dict(stable_events[0]) | {"flags": True}],
            [dict(stable_events[0]) | {"active_before": 1}],
            [dict(stable_events[0]) | {"active_after": 0}],
            [dict(stable_events[0]) | {"backing_after_hex": "0A"}],
            [dict(stable_events[0]),
             dict(stable_events[1]) | {"flags": 0}],
            [dict(stable_events[0]),
             dict(stable_events[1]) | {"active_before": 0}],
            [dict(stable_events[0]),
             dict(stable_events[1]) | {"backing_after_hex": "6162"}],
            [dict(stable_events[0]),
             dict(stable_events[1]) | {"backing_after_hex": "212121"}],
            [dict(overwrite_events[0]),
             dict(overwrite_events[1]) | {"backing_after_hex": "3f3f3f"}],
            [dict(failure_events[0]) | {"behavior": "stable"}],
            [dict(failure_events[0]) | {"active_after": 1}],
        )):
            reject("reject-forged-safe-buffer-lifecycle-" + format(index, "02d"),
                   lambda poisoned_events=poisoned_events:
                   validate_events(poisoned_events))

        reject("reject-an-omitted-complete-observation",
               lambda: validate_records(matrix, records[:-1], records_sha256))
        reject("reject-reordered-complete-observations",
               lambda: validate_records(
                   matrix, list(reversed(records)), records_sha256,
               ))
        reject("reject-a-forged-complete-observation-hash",
               lambda: validate_records(matrix, records, "cd" * 32))
        for field, replacement in (
            ("case", "managed-buffer-lifetime.v1.1000"),
            ("group", GROUPS[-1]),
            ("variant", 99),
        ):
            poisoned_records = list(records)
            row = dict(poisoned_records[0])
            row[field] = replacement
            poisoned_records[0] = row
            reject("reject-forged-observation-field-" + field,
                   lambda poisoned_records=poisoned_records:
                   validate_records(
                       matrix, poisoned_records, digest(poisoned_records),
                   ))

        synthetic_outcome = records[0]["outcome"]
        for field, replacement in (
            ("status", "concealed"),
            ("stage", 1),
            ("exception", {
                "kind": "ordinary-python-error", "module": "builtins",
                "type": "BufferError", "args": normalize_value(("hidden",)),
            }),
            ("events", [dict(stable_events[1])]),
            ("checkpoints", "hidden"),
            ("callbacks", "hidden"),
            ("warnings", "hidden"),
        ):
            outcome = dict(synthetic_outcome)
            outcome[field] = replacement
            reject("reject-forged-complete-outcome-" + field,
                   lambda outcome=outcome: validate_outcome(outcome))

        actual_error = {
            "kind": "ordinary-python-error",
            "module": "builtins",
            "type": "BufferError",
            "args": normalize_value(("exact exporter failure",)),
        }
        accept("preserve-an-exact-module-type-and-type-tagged-error",
               validate_normalized_error(actual_error) is None)
        for field, replacement in (
            ("kind", "concealed-error"),
            ("module", 7),
            ("type", None),
            ("args", {"type": "int", "value": True}),
        ):
            error = dict(actual_error)
            error[field] = replacement
            reject("reject-forged-exact-python-exception-" + field,
                   lambda error=error: validate_normalized_error(error))

        for field, replacement in (
            ("candidate_import_count", 1),
            ("external_regex_import_count", 1),
            ("actual_method_guard_checks", 2 * CASE_COUNT - 1),
            ("future_candidate_guard_relative",
             "tools/independent_original_cpython_suite_v4.py"),
            ("future_candidate_guard_sha256", "ef" * 32),
            ("future_ownership_audit_sha256", "12" * 32),
            ("future_candidate_guard_installed", True),
        ):
            guard = dict(first["reference_guard"])
            guard[field] = replacement
            reject("reject-forged-genuine-reference-guard-" + field,
                   lambda guard=guard: validate_reference_guard(guard))

        for field, replacement in (
            ("role", "candidate-rust"),
            ("pid", 0),
            ("oracle_source_sha256", "cd" * 32),
            ("matrix_sha256", "ef" * 32),
            ("published_seed", PUBLISHED_SEED + 1),
            ("case_count", CASE_COUNT - 1),
            ("actual_reference_workers", 2),
            ("actual_candidate_workers", 1),
            ("actual_candidate_imports", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("workspace_files_written", 1),
            ("evidence_files_created", 1),
            ("benchmark_files_read", 1),
            ("hidden_cases_read", 1),
            ("performance", "1.5x"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
        ):
            worker = dict(first)
            worker[field] = replacement
            reject("reject-forged-reference-worker-" + field,
                   lambda worker=worker: validate_reference_worker(
                       worker, role="reference_a", source_pin=source_pin,
                       matrix=matrix, expected_pid=47001,
                   ))

        for name in ("oracle", "python", "re", "re._compiler",
                     "re._parser", "re._constants"):
            owners = dict(first["source_owners"])
            forged = dict(owners[name])
            forged["sha256"] = "89" * 32
            owners[name] = forged
            reject("reject-forged-pinned-source-owner-" + name,
                   lambda owners=owners:
                   validate_source_owners(owners, source_pin))

        same_pid = dict(second)
        same_pid["pid"] = first["pid"]
        same_pid_process = synthetic_process(same_pid)
        reject("reject-reuse-of-one-reference-process-as-two",
               lambda: validate_reference_pair(
                   first, same_pid, first_process, same_pid_process,
                   source_pin=source_pin, matrix=matrix,
               ))

        for family in ("rust", "c", "zig"):
            for field, replacement in (
                ("family", "foreign"),
                ("adapter_relative", "candidates/../regex.py"),
                ("adapter_sha256", "invalid"),
                ("engine_relative", "candidates/external.so"),
                ("engine_sha256", "invalid"),
                ("bridge_relative", "candidates/external_bridge.so"),
                ("bridge_sha256", "invalid"),
                ("v5_guard_relative",
                 "tools/independent_original_cpython_suite_v4.py"),
                ("v5_guard_sha256", "89" * 32),
                ("ownership_audit_relative", "tools/foreign_audit.py"),
                ("ownership_audit_sha256", "89" * 32),
            ):
                pins = synthetic_candidate_pins(family)
                pins[field] = replacement
                reject(
                    "reject-forged-" + family + "-closure-" + field,
                    lambda pins=pins: validate_future_candidate_pins(pins),
                )

        for field, replacement in (
            ("role", "reference_b"),
            ("pid", 47002),
            ("returncode", 1),
            ("stderr", encode_stream(b"concealed reference failure")),
        ):
            process = dict(first_process)
            process[field] = replacement
            reject("reject-forged-reference-process-" + field,
                   lambda process=process: validate_process_evidence(
                       process, first, role="reference_a",
                   ))
        for field, replacement in (
            ("base64", "!"),
            ("bytes", first_process["stdout"]["bytes"] + 1),
            ("sha256", "12" * 32),
            ("complete", False),
        ):
            stream = dict(first_process["stdout"])
            stream[field] = replacement
            reject("reject-forged-complete-process-stream-" + field,
                   lambda stream=stream: decode_stream(stream, "synthetic"))

        reject("reject-duplicate-json-worker-fields",
               lambda: decode_canonical(b'{"value":1,"value":2}\n',
                                        "duplicate"))
        reject("reject-noncanonical-json-worker-fields",
               lambda: decode_canonical(b'{ "value": 1 }\n', "noncanonical"))
        reject("reject-nonfinite-json-worker-fields",
               lambda: decode_canonical(b'{"value":NaN}\n', "nonfinite"))
        reject("reject-a-candidate-contaminating-reference-modules",
               lambda: verify_standard_modules({"re": object(),
                                                 "candidates.vm_candidate": object()}))
        reject("reject-an-external-regex-contaminating-reference-modules",
               lambda: verify_standard_modules({"re": object(),
                                                 "regex": object()}))

        reject("block-all-workspace-and-evidence-file-opens",
               lambda: builtins.open("performance/held-out-cases.json", "rb"))
        reject("block-all-workspace-and-evidence-file-writes",
               lambda: builtins.open("synthetic-forbidden-evidence.json", "wb"))
        reject("block-all-workspace-directory-enumeration",
               lambda: os.scandir("experiments"))
        reject("block-all-workspace-file-status-reads",
               lambda: os.stat("performance"))
        reject("block-all-evidence-and-workspace-replacements",
               lambda: os.replace("synthetic-before", "synthetic-after"))
        reject("block-all-candidate-imports",
               lambda: importlib.import_module("candidates.vm_candidate"))
        reject("block-all-dynamic-standard-reference-imports",
               lambda: importlib.import_module("re"))
        reject("block-all-isolated-reference-processes",
               lambda: subprocess.Popen([PINNED_PYTHON, "-I", "-B"]))
        reject("block-all-background-worker-threads",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-all-performance-clock-samples", lambda: time.perf_counter())
        reject("block-all-wall-clock-samples", lambda: time.time())
        reject("block-all-synthetic-garbage-collection", lambda: gc.collect())

        require(len(accepted) >= 15 and len(rejected) >= 80,
                "at least 40 independently bounded attack controls are required")
        require(boundary.blocked["file_reads"] >= 3
                and boundary.blocked["file_writes"] >= 1
                and boundary.blocked["candidate_imports"] >= 1
                and boundary.blocked["dynamic_imports"] >= 1
                and boundary.blocked["processes"] >= 1
                and boundary.blocked["threads"] >= 1
                and boundary.blocked["clock_samples"] >= 2
                and boundary.blocked["garbage_collections"] >= 1,
                "a real-effect source-only boundary was not exercised")

    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a genuine candidate escaped from the synthetic-only controls")
    return {
        "schema": SCHEMA + "-synthetic-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "group_count": len(GROUPS),
        "cases_per_group": VARIANTS_PER_GROUP,
        "case_count": CASE_COUNT,
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "blocked_effect_attempts": dict(boundary.blocked),
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
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
        description="Prospectively frozen managed-buffer correctness only",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run in-memory, effect-blocked synthetic controls")
    modes.add_argument("--baseline", action="store_true",
                       help="explicitly observe exactly two genuine references")
    modes.add_argument("--internal-reference-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--role", choices=("reference_a", "reference_b"))
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(options.role is None and options.oracle_source_sha256 is None
                    and options.matrix_sha256 is None,
                    "synthetic controls cannot select a worker, source, or matrix")
            document = source_self_test()
            sys.stdout.buffer.write(canonical(document))
            return 0 if document["status"] == "PASS" else 2

        checked_digest(options.oracle_source_sha256,
                       "explicitly frozen managed-buffer oracle source")
        checked_digest(options.matrix_sha256,
                       "explicitly frozen managed-buffer case matrix")
        require(options.matrix_sha256 == MATRIX_SHA256,
                "the exact prospectively frozen case matrix was substituted")
        if options.internal_reference_worker:
            require(options.role in {"reference_a", "reference_b"},
                    "a genuine reference role is mandatory")
            document = observe_reference_worker(
                options.role, options.oracle_source_sha256,
            )
        else:
            require(options.baseline and options.role is None,
                    "only exactly two genuine baseline workers may be selected")
            document = run_baseline(
                options.oracle_source_sha256, options.matrix_sha256,
            )
        sys.stdout.buffer.write(canonical(document))
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
    except (ManagedBufferOracleError, OSError, ValueError, TypeError) as error:
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
