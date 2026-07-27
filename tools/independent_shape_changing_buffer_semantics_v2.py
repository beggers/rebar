#!/usr/bin/env python3
"""Freeze legal, independently shape-changing Python replacement buffers.

V2 retains the exact, immutable V1 input matrix and every signed V1 loss.  It
corrects only the defining-module observation of its own exact
``ShapeCallbackError`` class.  Subclasses, same-name foreign classes, public
regex errors, ordinary user exceptions, every original case, and every
observable replacement and buffer event remain unmodified.

The frozen matrix equally covers all 64 independent outer/nested PEP-688
buffer pairs at lengths 0, 1, 2, 3, 5, 8, 13, and 19.  Each pair is crossed
exactly once with five substitution APIs, eight subject/template/callback
placements, and four stable, mutating, and failing exporter behaviors.  The
actual witnessed outer-13, nested-0/1/2/5/8 regression is explicitly
preserved.  Full original group offsets, empty visible storage, replacement
results, exceptions, callbacks, acquisition flags, storage, and complete
ownership/release events are preserved.

``--self-test`` is in-memory and cannot start an engine or worker, read or
write a file, measure time, inspect a candidate, or access hidden data.  Only
an explicitly frozen future ``--baseline`` may execute the two isolated
standard-CPython reference processes.
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
SOURCE_RELATIVE = "tools/independent_shape_changing_buffer_semantics_v2.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-shape-changing-buffer-semantics-v2"
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

ORACLE_CALLBACK_CANONICAL_MODULE = (
    "tools.independent_shape_changing_buffer_semantics_v2"
)
HISTORICAL_V1_STATUS = "FALSIFIED"
HISTORICAL_V1_ORACLE_RELATIVE = (
    "tools/independent_shape_changing_buffer_semantics_v1.py"
)
HISTORICAL_V1_ORACLE_SHA256 = (
    "866dbf7bf4a48a867b3aaacd05cfa4f1346c747931543fa386835e783f0073aa"
)
HISTORICAL_V1_RECORDER_RELATIVE = (
    "tools/record_independent_shape_changing_buffer_semantics_v1.py"
)
HISTORICAL_V1_RECORDER_SHA256 = (
    "047bcc25a3b033fa374576c434b0e6ebcc6c97cf99965e9cc9083c012249529c"
)
HISTORICAL_V1_PINNED_FILES = types.MappingProxyType({
    "v1_oracle": (
        HISTORICAL_V1_ORACLE_RELATIVE,
        HISTORICAL_V1_ORACLE_SHA256,
    ),
    "v1_recorder": (
        HISTORICAL_V1_RECORDER_RELATIVE,
        HISTORICAL_V1_RECORDER_SHA256,
    ),
    "v1_two_python_reference": (
        "experiments/rust_public_practice_v1/"
        "shape-changing-buffer-semantics-v1-shared-suite-v1.json.gz",
        "8bf48813d82966edbed05330ce26f6c8a3d80ee72c59a6dbfa104ff397906b5b",
    ),
    "v1_two_python_reference_receipt": (
        "experiments/rust_public_practice_v1/"
        "shape-changing-buffer-semantics-v1-shared-suite-v1-"
        "publication-receipt.json",
        "8744ebf8fb29924661d8c379b3fa1d7662e6dd44ebca49ecd7d37219f06ac7c9",
    ),
    "v1_c_inconclusive_process_collision": (
        "experiments/rust_public_practice_v1/"
        "c-shape-changing-buffer-semantics-v1-native-lifetime-repair-v1.json.gz",
        "1a58c7d155a9bdf76841d0df0927b8ecb6ad496b0d190e3b9a591737783e3e5a",
    ),
    "v1_c_inconclusive_process_collision_receipt": (
        "experiments/rust_public_practice_v1/"
        "c-shape-changing-buffer-semantics-v1-native-lifetime-repair-v1-"
        "publication-receipt.json",
        "1d4450c6081b4a462c14eac17a637f8c3a79490eb413fea9d796e2ec917d5df3",
    ),
    "v1_c_complete_candidate_report": (
        "experiments/rust_public_practice_v1/"
        "c-shape-changing-buffer-semantics-v1-native-lifetime-repair-"
        "pid-retry-v1.json.gz",
        "8660c07a379901e4163b6204199c5a903013c2e9efa051ac67560d89085542db",
    ),
    "v1_c_complete_candidate_receipt": (
        "experiments/rust_public_practice_v1/"
        "c-shape-changing-buffer-semantics-v1-native-lifetime-repair-"
        "pid-retry-v1-publication-receipt.json",
        "d4d7c6f184e3a0dbea06ab9bbf8cbe13a945dcb4914a567e17a7b25a9a74b1b2",
    ),
    "v1_graph_input_manifest": (
        "docs/evidence/shape-changing-buffer-overview-v1.inputs.json",
        "418e89b29487caf401bc96d9e9b7ee02adde53105f0983a2298c1b910e7451b1",
    ),
    "v1_graph_complete_summary": (
        "docs/evidence/shape-changing-buffer-overview-v1.json",
        "d438b3beb510440304c94eb4ad8feb1df44531bd0390d0cbb2f66fc29b64b808",
    ),
    "v1_historical_falsified_graph": (
        "docs/evidence/shape-changing-buffer-overview-v1.svg",
        "8a9d614ff111dde55ecc652502f1a92b62fd7356a4299af4d4cc97ad0c3dc3c2",
    ),
    "v1_historical_graph_renderer": (
        "tools/render_shape_changing_buffer_overview_v1.py",
        "53e76b2a99a8bfe2adc654fbcfa5be13026726227b5cc2345e2c41833116a1cb",
    ),
})
HISTORICAL_V1_REFERENCE_RECORDS_SHA256 = (
    "0aeddfa2835be5895bc6d88edae5ecc4945241c7ea456c0487497be4c47f8373"
)
HISTORICAL_V1_C_CANDIDATE_RECORDS_SHA256 = (
    "b54207667c3922e57fd1af0f209bf2e468a8f2cfb9906e83bf2ebd845e4b8295"
)
HISTORICAL_V1_C_MISMATCH_LEDGER_SHA256 = (
    "e98fc451e765f2c196ca8c4b8fceeefff1c909d2416b71ec0c4cdeeaf37589e3"
)
HISTORICAL_V1_FAILURE_COUNTS = types.MappingProxyType({"c": 1_888})
HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS = types.MappingProxyType({"c": 496})
HISTORICAL_V1_REAL_FAILURE_COUNTS = types.MappingProxyType({"c": 1_392})

PUBLISHED_SEED = 0x5348_4150_4542_4632
SHAPE_NAMES = (
    "zero", "one", "two", "short", "five", "equal", "thirteen", "long",
)
SHAPE_SIZES = types.MappingProxyType({
    "zero": 0,
    "one": 1,
    "two": 2,
    "short": 3,
    "five": 5,
    "equal": 8,
    "thirteen": 13,
    "long": 19,
})
WITNESSED_REGRESSION_OUTER_SHAPE = "thirteen"
WITNESSED_REGRESSION_NESTED_SHAPES = (
    "zero", "one", "two", "five", "equal",
)
WITNESSED_REGRESSION_OUTER_SIZE = 13
WITNESSED_REGRESSION_NESTED_SIZES = (0, 1, 2, 5, 8)
COHORTS = tuple(
    "outer-" + outer + "-nested-" + nested
    for outer in SHAPE_NAMES
    for nested in SHAPE_NAMES
)
APIS = (
    "module.sub", "module.subn", "pattern.sub", "pattern.subn", "match.expand",
)
TARGETS = (
    "subject-direct",
    "subject-wrapped",
    "template-direct",
    "template-wrapped",
    "both-direct",
    "both-wrapped",
    "callback-return",
    "callback-error",
)
BEHAVIORS = ("stable", "mutate", "fail-outer", "fail-nested")
PATTERN_KINDS = ("captures", "zero-lookahead", "empty", "optional-captures")
TEMPLATE_STYLES = ("literal", "named", "numeric", "invalid", "missing")
FLAGS = (0, 2, 256, 258)
COUNTS = (0, 1, 2, 7)
WINDOW_STARTS = (-4, -1, 0, 1, 2, 3, 5, 8, 13, 19, 32, 2_147_483_647)
WINDOW_ENDS = (0, 1, 2, 3, 5, 8, 13, 19, 32, None, 2_147_483_647)
VARIANTS_PER_COHORT = len(APIS) * len(TARGETS) * len(BEHAVIORS)
CASE_COUNT = len(COHORTS) * VARIANTS_PER_COHORT
MATRIX_SHA256 = (
    "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8"
)
SIMPLE_BUFFER_FLAG = 0
FULL_READONLY_BUFFER_FLAG = 284
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "_regex", "candidates", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "regex", "rebar",
    "rust_regex", "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class ShapeOracleError(Exception):
    """A legal shape-changing case, owner, or original result was forged."""


class SourceOnlyError(ShapeOracleError):
    """A synthetic shape-changing control attempted a real side effect."""


class ReferenceWorkerFailure(ShapeOracleError):
    """Retain the complete failure of a genuine isolated standard worker."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


class ShapeCallbackError(Exception):
    """A frozen public replacement callback failed intentionally."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ShapeOracleError(message)


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
        raise ShapeOracleError("shape-changing evidence is not complete canonical JSON") from error


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
    require(valid_digest(value), "an independently frozen exact SHA-256 is mandatory: " + label)
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result, "duplicate JSON fields hide a shape mismatch")
        result[key] = value
    return result


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
        "a complete bounded isolated shape worker is mandatory: " + label,
    )

    def reject_constant(_: str) -> Any:
        raise ShapeOracleError("nonfinite shape-changing evidence is forbidden")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (ShapeOracleError, TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise ShapeOracleError("an isolated shape-changing worker emitted invalid JSON") from error
    require(
        type(value) is dict and canonical(value) == raw,
        "complete shape-changing worker evidence was truncated or substituted",
    )
    return value


def exact_hex(raw: Any, *, label: str) -> str:
    require(type(raw) is str, "an exact hexadecimal payload is mandatory: " + label)
    try:
        value = bytes.fromhex(raw)
    except ValueError as error:
        raise ShapeOracleError("invalid original hexadecimal payload: " + label) from error
    require(value.hex() == raw, "a noncanonical shape payload was injected: " + label)
    return raw


def shaped_bytes(base: bytes, size: int, suffix: bytes) -> bytes:
    require(
        type(base) is bytes
        and bool(base)
        and type(size) is int
        and size >= 0
        and type(suffix) is bytes,
        "an exact independently sized visible or nested buffer is mandatory",
    )
    if size == 0:
        return b""
    material = base + suffix
    while len(material) < size:
        material += base
    return material[:size]


def exporter_descriptor(
    *,
    role: str,
    outer_shape: str,
    nested_shape: str,
    outer_payload: bytes,
    nested_payload: bytes,
    behavior: str,
    wrapped: bool,
) -> dict[str, Any]:
    require(
        role in {"subject", "template"}
        and outer_shape in SHAPE_SIZES
        and nested_shape in SHAPE_SIZES
        and type(outer_payload) is bytes
        and type(nested_payload) is bytes
        and len(outer_payload) == SHAPE_SIZES[outer_shape]
        and len(nested_payload) == SHAPE_SIZES[nested_shape]
        and behavior in BEHAVIORS
        and type(wrapped) is bool,
        "a legal independently sized PEP-688 shape exporter was forged",
    )
    return {
        "kind": "shape-exporter",
        "role": role,
        "outer_shape": outer_shape,
        "nested_shape": nested_shape,
        "outer_size": len(outer_payload),
        "nested_size": len(nested_payload),
        "outer_hex": outer_payload.hex(),
        "nested_hex": nested_payload.hex(),
        "behavior": behavior,
        "wrapped": wrapped,
    }


def bytes_descriptor(payload: bytes) -> dict[str, Any]:
    require(type(payload) is bytes, "an original bytes control is mandatory")
    return {"kind": "bytes", "hex": payload.hex()}


def callable_descriptor(payload: bytes, *, raises: bool) -> dict[str, Any]:
    require(
        type(payload) is bytes and type(raises) is bool,
        "a genuine shape-changing replacement callback is mandatory",
    )
    return {"kind": "callable", "hex": payload.hex(), "raises": raises}


def validate_carrier(value: Any, *, role: str) -> dict[str, Any]:
    require(
        role in {"subject", "template"} and type(value) is dict,
        "a complete original shape-changing carrier is mandatory",
    )
    if value.get("kind") == "bytes":
        require(
            set(value) == {"kind", "hex"},
            "a genuine bytes shape-control payload was forged",
        )
        exact_hex(value.get("hex"), label=role)
        return value
    if value.get("kind") == "callable":
        require(
            role == "template"
            and set(value) == {"kind", "hex", "raises"}
            and type(value.get("raises")) is bool,
            "a genuine returning or failing shape callback was substituted",
        )
        exact_hex(value.get("hex"), label="callback")
        return value
    require(
        set(value) == {
            "kind", "role", "outer_shape", "nested_shape", "outer_size",
            "nested_size", "outer_hex", "nested_hex", "behavior", "wrapped",
        }
        and value.get("kind") == "shape-exporter"
        and value.get("role") == role
        and value.get("outer_shape") in SHAPE_SIZES
        and value.get("nested_shape") in SHAPE_SIZES
        and type(value.get("outer_size")) is int
        and type(value.get("nested_size")) is int
        and value["outer_size"] == SHAPE_SIZES[value["outer_shape"]]
        and value["nested_size"] == SHAPE_SIZES[value["nested_shape"]]
        and value.get("behavior") in BEHAVIORS
        and type(value.get("wrapped")) is bool,
        "an independently sized legal PEP-688 outer/nested owner was forged",
    )
    outer = bytes.fromhex(exact_hex(value.get("outer_hex"), label="outer"))
    nested = bytes.fromhex(exact_hex(value.get("nested_hex"), label="nested"))
    require(
        len(outer) == value["outer_size"]
        and len(nested) == value["nested_size"],
        "a real zero, short, equal, or long nested buffer size was concealed",
    )
    return value


def build_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and 0 <= seed < 1 << 64, "an exact published 64-bit seed is mandatory")
    seeded = random.Random(seed)
    matrix: list[dict[str, Any]] = []
    for outer_shape in SHAPE_NAMES:
        for nested_shape in SHAPE_NAMES:
            cohort = "outer-" + outer_shape + "-nested-" + nested_shape
            for variant in range(VARIANTS_PER_COHORT):
                noise = "".join(seeded.choice("abcdef0123456789") for _ in range(12)).encode("ascii")
                api = APIS[variant % len(APIS)]
                target = TARGETS[(variant // len(APIS)) % len(TARGETS)]
                behavior = BEHAVIORS[(variant // (len(APIS) * len(TARGETS))) % len(BEHAVIORS)]
                outer_subject = shaped_bytes(b"OUTERalpha42", SHAPE_SIZES[outer_shape], noise)
                nested_subject = shaped_bytes(b"aa12bb34cc56dd78xyz", SHAPE_SIZES[nested_shape], noise)
                outer_template = shaped_bytes(b"OUTER-template", SHAPE_SIZES[outer_shape], noise)
                nested_template = shaped_bytes(rb"<\g<word>:\g<number>>", SHAPE_SIZES[nested_shape], noise)
                wrapped = target.endswith("-wrapped")

                subject = bytes_descriptor(nested_subject)
                template = bytes_descriptor(b"X")
                if target.startswith("subject-") or target.startswith("both-") or target.startswith("callback-"):
                    subject = exporter_descriptor(
                        role="subject",
                        outer_shape=outer_shape,
                        nested_shape=nested_shape,
                        outer_payload=outer_subject,
                        nested_payload=nested_subject,
                        behavior=behavior,
                        wrapped=wrapped,
                    )
                if target.startswith("template-") or target.startswith("both-"):
                    template = exporter_descriptor(
                        role="template",
                        outer_shape=outer_shape,
                        nested_shape=nested_shape,
                        outer_payload=outer_template,
                        nested_payload=nested_template,
                        behavior=behavior,
                        wrapped=wrapped,
                    )
                if target == "callback-return":
                    template = callable_descriptor(b"X", raises=False)
                elif target == "callback-error":
                    template = callable_descriptor(b"X", raises=True)

                pattern_kind = PATTERN_KINDS[variant % len(PATTERN_KINDS)]
                pattern = {
                    "captures": rb"(?P<word>[a-z]+)(?P<number>[0-9]*)",
                    "zero-lookahead": rb"(?=(?P<word>[a-z]*)(?P<number>[0-9]*))",
                    "empty": rb"(?P<word>)(?P<number>)",
                    "optional-captures": rb"(?P<word>[a-z]+)?(?P<number>[0-9]+)?",
                }[pattern_kind]
                template_style = TEMPLATE_STYLES[(variant // len(PATTERN_KINDS)) % len(TEMPLATE_STYLES)]
                if template["kind"] == "bytes":
                    template_payload = {
                        "literal": b"X",
                        "named": rb"<\g<word>:\g<number>>",
                        "numeric": rb"<\1:\2>",
                        "invalid": rb"\q",
                        "missing": rb"\g<absent>",
                    }[template_style]
                    template = bytes_descriptor(template_payload)

                matrix.append({
                    "case": "shape-changing-buffer-semantics.v1." + format(len(matrix), "05d"),
                    "cohort": cohort,
                    "variant": variant,
                    "seed": seed,
                    "outer_shape": outer_shape,
                    "nested_shape": nested_shape,
                    "outer_size": SHAPE_SIZES[outer_shape],
                    "nested_size": SHAPE_SIZES[nested_shape],
                    "api": api,
                    "target": target,
                    "behavior": behavior,
                    "pattern_kind": pattern_kind,
                    "template_style": template_style,
                    "flags": FLAGS[variant % len(FLAGS)],
                    "count": COUNTS[(variant // len(APIS)) % len(COUNTS)],
                    "pos": WINDOW_STARTS[variant % len(WINDOW_STARTS)],
                    "endpos": WINDOW_ENDS[(variant // len(WINDOW_STARTS)) % len(WINDOW_ENDS)],
                    "pattern_hex": pattern.hex(),
                    "subject": subject,
                    "template": template,
                })
    return matrix


def validate_matrix(value: Any, expected: str = MATRIX_SHA256) -> str:
    checked_digest(expected, "prospectively frozen shape-changing property matrix")
    require(
        tuple(SHAPE_SIZES) == SHAPE_NAMES
        and tuple(SHAPE_SIZES.values()) == (0, 1, 2, 3, 5, 8, 13, 19)
        and len(SHAPE_NAMES) == 8
        and len(COHORTS) == 64
        and len(set(COHORTS)) == 64
        and VARIANTS_PER_COHORT == 160
        and CASE_COUNT == 10_240
        and VARIANTS_PER_COHORT == len(APIS) * len(TARGETS) * len(BEHAVIORS),
        "the exhaustive independently weighted shape denominator silently changed",
    )
    require(
        WITNESSED_REGRESSION_OUTER_SHAPE == "thirteen"
        and WITNESSED_REGRESSION_OUTER_SIZE == 13
        and SHAPE_SIZES[WITNESSED_REGRESSION_OUTER_SHAPE]
        == WITNESSED_REGRESSION_OUTER_SIZE
        and WITNESSED_REGRESSION_NESTED_SHAPES
        == ("zero", "one", "two", "five", "equal")
        and WITNESSED_REGRESSION_NESTED_SIZES == (0, 1, 2, 5, 8)
        and tuple(
            SHAPE_SIZES[shape]
            for shape in WITNESSED_REGRESSION_NESTED_SHAPES
        ) == WITNESSED_REGRESSION_NESTED_SIZES,
        "an actually witnessed outer-13 shape-changing regression was omitted",
    )
    require(
        type(value) is list and len(value) == CASE_COUNT,
        "every original outer/nested shape combination is mandatory",
    )
    original = build_matrix()
    require(
        value == original and digest(value) == expected,
        "the published shape seed, independent backing sizes, or case matrix changed",
    )
    observed: dict[str, int] = {cohort: 0 for cohort in COHORTS}
    observed_variants: dict[str, set[tuple[str, str, str]]] = {
        cohort: set() for cohort in COHORTS
    }
    expected_variants = {
        (api, target, behavior)
        for api in APIS
        for target in TARGETS
        for behavior in BEHAVIORS
    }
    seen: set[str] = set()
    for index, case in enumerate(value):
        require(
            type(case) is dict
            and set(case) == {
                "case", "cohort", "variant", "seed", "outer_shape", "nested_shape",
                "outer_size", "nested_size", "api", "target", "behavior",
                "pattern_kind", "template_style", "flags", "count", "pos",
                "endpos", "pattern_hex", "subject", "template",
            }
            and case.get("case") == "shape-changing-buffer-semantics.v1." + format(index, "05d")
            and case["case"] not in seen
            and case.get("cohort") == COHORTS[index // VARIANTS_PER_COHORT]
            and type(case.get("variant")) is int
            and case["variant"] == index % VARIANTS_PER_COHORT
            and type(case.get("seed")) is int
            and case["seed"] == PUBLISHED_SEED
            and case.get("outer_shape") in SHAPE_SIZES
            and case.get("nested_shape") in SHAPE_SIZES
            and type(case.get("outer_size")) is int
            and type(case.get("nested_size")) is int
            and case["outer_size"] == SHAPE_SIZES[case["outer_shape"]]
            and case["nested_size"] == SHAPE_SIZES[case["nested_shape"]]
            and case.get("api") in APIS
            and case.get("target") in TARGETS
            and case.get("behavior") in BEHAVIORS
            and case.get("pattern_kind") in PATTERN_KINDS
            and case.get("template_style") in TEMPLATE_STYLES
            and type(case.get("flags")) is int
            and case["flags"] in FLAGS
            and type(case.get("count")) is int
            and case["count"] in COUNTS
            and type(case.get("pos")) is int
            and case["pos"] in WINDOW_STARTS
            and (case.get("endpos") is None or type(case.get("endpos")) is int)
            and case["endpos"] in WINDOW_ENDS,
            "a complete independent shape, substitution, callback, or window case was forged",
        )
        exact_hex(case.get("pattern_hex"), label="pattern")
        validate_carrier(case["subject"], role="subject")
        validate_carrier(case["template"], role="template")
        for role in ("subject", "template"):
            carrier = case[role]
            if carrier["kind"] == "shape-exporter":
                require(
                    carrier["outer_shape"] == case["outer_shape"]
                    and carrier["nested_shape"] == case["nested_shape"]
                    and carrier["outer_size"] == case["outer_size"]
                    and carrier["nested_size"] == case["nested_size"]
                    and carrier["behavior"] == case["behavior"],
                    "a real independent subject or template backing shape changed",
                )
        variant = (case["api"], case["target"], case["behavior"])
        require(
            variant not in observed_variants[case["cohort"]],
            "an original shape API, placement, or failure case was duplicated",
        )
        observed_variants[case["cohort"]].add(variant)
        seen.add(case["case"])
        observed[case["cohort"]] += 1
    require(
        all(count == VARIANTS_PER_COHORT for count in observed.values())
        and all(
            variants == expected_variants
            for variants in observed_variants.values()
        ),
        "a genuine shape cohort or full API-placement-behavior cross product changed",
    )
    return expected


class NestedShapeExporter:
    """The actual visible nested backing, independent of its outer owner."""

    __slots__ = ("outer", "backing", "active")

    def __init__(self, outer: OuterShapeExporter, payload: bytes) -> None:
        require(type(payload) is bytes, "a legal nested exporter needs actual bytes")
        self.outer = outer
        self.backing = bytearray(payload)
        self.active = 0

    def __buffer__(self, flags: int) -> memoryview:
        require(type(flags) is int and flags >= 0, "a real nested PEP-688 flag is mandatory")
        previous = self.active
        if self.outer.behavior == "fail-nested":
            self.outer.append_event(
                "acquire-error", "nested", flags, previous, previous,
            )
            raise BufferError("frozen shape-changing nested exporter failure")
        self.active += 1
        self.outer.append_event("acquire", "nested", flags, previous, self.active)
        return memoryview(self.backing)

    def __release_buffer__(self, view: memoryview) -> None:
        require(
            type(view) is memoryview and self.active > 0,
            "a nested original exporter was released without its owned view",
        )
        previous = self.active
        if self.outer.behavior == "mutate":
            poison = b"!" * len(self.backing)
            require(len(poison) == len(self.backing), "nested live storage must not resize")
            self.backing[:] = poison
        self.active -= 1
        self.outer.append_event("release", "nested", None, previous, self.active)


class OuterShapeExporter:
    """A legal outer exporter that returns a differently sized nested buffer."""

    __slots__ = ("backing", "nested", "behavior", "events", "role", "active")

    def __init__(
        self,
        descriptor: Mapping[str, Any],
        events: list[dict[str, Any]],
    ) -> None:
        validate_carrier(descriptor, role=descriptor.get("role", "subject"))
        require(descriptor["kind"] == "shape-exporter", "an actual outer exporter is mandatory")
        self.backing = bytearray(bytes.fromhex(descriptor["outer_hex"]))
        self.behavior = descriptor["behavior"]
        self.events = events
        self.role = descriptor["role"]
        self.active = 0
        self.nested = NestedShapeExporter(self, bytes.fromhex(descriptor["nested_hex"]))

    def append_event(
        self,
        kind: str,
        owner: str,
        flags: int | None,
        before: int,
        after: int,
    ) -> None:
        self.events.append({
            "event": kind,
            "role": self.role,
            "owner": owner,
            "flags": flags,
            "active_before": before,
            "active_after": after,
            "outer_size": len(self.backing),
            "nested_size": len(self.nested.backing),
            "outer_hex": bytes(self.backing).hex(),
            "nested_hex": bytes(self.nested.backing).hex(),
            "behavior": self.behavior,
        })

    def __len__(self) -> int:
        self.append_event("length-probe", "outer", None, self.active, self.active)
        return len(self.backing)

    def __buffer__(self, flags: int) -> memoryview:
        require(type(flags) is int and flags >= 0, "a genuine outer buffer flag is mandatory")
        previous = self.active
        if self.behavior == "fail-outer":
            self.append_event("acquire-error", "outer", flags, previous, previous)
            raise BufferError("frozen shape-changing outer exporter failure")
        self.active += 1
        self.append_event("acquire", "outer", flags, previous, self.active)
        try:
            return memoryview(self.nested)
        except Exception:
            current = self.active
            self.active -= 1
            self.append_event("acquire-unwind", "outer", None, current, self.active)
            raise

    def __release_buffer__(self, view: memoryview) -> None:
        require(
            type(view) is memoryview and self.active > 0,
            "a genuine outer exporter was released without its owned nested view",
        )
        previous = self.active
        if self.behavior == "mutate":
            poison = b"?" * len(self.backing)
            require(len(poison) == len(self.backing), "outer live storage must not resize")
            self.backing[:] = poison
        self.active -= 1
        self.append_event("release", "outer", None, previous, self.active)


def decode_carrier(
    descriptor: Mapping[str, Any],
    events: list[dict[str, Any]],
    *,
    role: str,
) -> tuple[Any, OuterShapeExporter | None, list[memoryview]]:
    validate_carrier(descriptor, role=role)
    if descriptor["kind"] == "bytes":
        return bytes.fromhex(descriptor["hex"]), None, []
    if descriptor["kind"] == "callable":
        return bytes.fromhex(descriptor["hex"]), None, []
    exporter = OuterShapeExporter(descriptor, events)
    if descriptor["wrapped"]:
        actual = memoryview(exporter)
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
    if isinstance(value, OuterShapeExporter):
        return {
            "type": "shape-exporter",
            "role": value.role,
            "outer_size": len(value.backing),
            "nested_size": len(value.nested.backing),
            "outer_hex": bytes(value.backing).hex(),
            "nested_hex": bytes(value.nested.backing).hex(),
            "outer_active": value.active,
            "nested_active": value.nested.active,
            "behavior": value.behavior,
        }
    if type(value) in (list, tuple):
        return {
            "type": "list" if type(value) is list else "tuple",
            "items": [normalize_value(item) for item in value],
        }
    if type(value) is dict:
        pairs = [[normalize_value(key), normalize_value(item)] for key, item in value.items()]
        pairs.sort(key=lambda pair: canonical(pair[0]))
        return {"type": "dict", "items": pairs}
    raise ShapeOracleError("a genuine shape-changing result was omitted: " + type(value).__qualname__)


def validate_normalized_value(value: Any) -> None:
    require(type(value) is dict and type(value.get("type")) is str, "an exact typed observation is mandatory")
    kind = value["type"]
    if kind == "none":
        require(set(value) == {"type"}, "a null-safe zero-size result was forged")
    elif kind in {"bool", "int", "str"}:
        expected = {"bool": bool, "int": int, "str": str}[kind]
        require(
            set(value) == {"type", "value"} and type(value.get("value")) is expected,
            "an exact scalar match or offset type was forged",
        )
    elif kind in {"bytes", "bytearray"}:
        require(set(value) == {"type", "hex"}, "a bytes-like shape result lost its carrier")
        exact_hex(value.get("hex"), label="observed result")
    elif kind in {"tuple", "list"}:
        require(
            set(value) == {"type", "items"} and type(value.get("items")) is list,
            "a capture tuple or substitution count was forged",
        )
        for item in value["items"]:
            validate_normalized_value(item)
    elif kind == "dict":
        require(set(value) == {"type", "items"} and type(value.get("items")) is list, "a mapping result was forged")
        previous: bytes | None = None
        for pair in value["items"]:
            require(type(pair) is list and len(pair) == 2, "a mapping observation was omitted")
            validate_normalized_value(pair[0])
            validate_normalized_value(pair[1])
            ordering = canonical(pair[0])
            require(previous is None or previous < ordering, "a mapping observation was reordered")
            previous = ordering
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
            "a genuine returned buffer shape or mutability was forged",
        )
        exact_hex(value.get("hex"), label="observed memoryview")
        for name in ("shape", "strides"):
            item = value[name]
            require(
                item is None or (type(item) is list and all(type(number) is int for number in item)),
                "a genuine nested visible-memoryview dimension was forged",
            )
    elif kind == "released-memoryview":
        require(
            set(value) == {"type", "exception_module", "exception_type", "exception_args"}
            and type(value.get("exception_module")) is str
            and type(value.get("exception_type")) is str,
            "an actual released nested memoryview error was hidden",
        )
        validate_normalized_value(value["exception_args"])
    elif kind == "shape-exporter":
        require(
            set(value) == {
                "type", "role", "outer_size", "nested_size", "outer_hex",
                "nested_hex", "outer_active", "nested_active", "behavior",
            }
            and value.get("role") in {"subject", "template"}
            and type(value.get("outer_size")) is int
            and value["outer_size"] >= 0
            and type(value.get("nested_size")) is int
            and value["nested_size"] >= 0
            and type(value.get("outer_active")) is int
            and value["outer_active"] >= 0
            and type(value.get("nested_active")) is int
            and value["nested_active"] >= 0
            and value.get("behavior") in BEHAVIORS,
            "a live legal shape-changing exporter was hidden or forged",
        )
        outer = bytes.fromhex(exact_hex(value.get("outer_hex"), label="observed outer"))
        nested = bytes.fromhex(exact_hex(value.get("nested_hex"), label="observed nested"))
        require(
            len(outer) == value["outer_size"] and len(nested) == value["nested_size"],
            "the exact visible and outer backing lengths were substituted",
        )
    else:
        raise ShapeOracleError("an unfrozen nested-buffer result was injected")


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
        "module": (
            ORACLE_CALLBACK_CANONICAL_MODULE
            if type(error) is ShapeCallbackError
            else type(error).__module__
        ),
        "type": type(error).__qualname__,
        "message": str(error),
        "args": normalize_value(error.args),
    }


def validate_error(value: Any) -> None:
    require(type(value) is dict, "an exact original substitution exception is mandatory")
    if value.get("kind") == "ordinary-python-error":
        require(
            set(value) == {"kind", "module", "type", "message", "args"}
            and type(value.get("module")) is str
            and type(value.get("type")) is str
            and type(value.get("message")) is str,
            "a genuine Python exception class or exact error message was omitted",
        )
        validate_normalized_value(value["args"])
        return
    require(
        value.get("kind") == "public-regex-error"
        and set(value) == {
            "kind", "type", "args", "message", "pattern", "position", "line", "column",
        }
        and type(value.get("type")) is str,
        "a genuine original PatternError and offsets were omitted",
    )
    for name in ("args", "message", "pattern", "position", "line", "column"):
        validate_normalized_value(value[name])


def visible_subject_length(subject: Any) -> int:
    if isinstance(subject, OuterShapeExporter):
        return len(subject.nested.backing)
    if type(subject) is memoryview:
        try:
            return subject.nbytes
        except ValueError:
            return 0
    if type(subject) in (bytes, bytearray, str):
        return len(subject)
    raise ShapeOracleError("a genuine visible capture subject was omitted")


def normalize_match(match: Any, subject: Any, compiled: Any) -> dict[str, Any]:
    visible = visible_subject_length(subject)
    offsets = tuple((left, right) for left, right in match.regs)
    checks: list[dict[str, Any]] = []
    for index, (left, right) in enumerate(offsets):
        missing = left == -1 and right == -1
        within = missing or (0 <= left <= right <= visible)
        checks.append({
            "group": index,
            "start": left,
            "end": right,
            "missing": missing,
            "within_visible_nested_buffer": within,
        })
    return {
        "pattern_is_expected": match.re is compiled,
        "string_is_subject": match.string is subject,
        "visible_nested_length": visible,
        "group": normalize_value(match.group()),
        "groups": normalize_value(match.groups()),
        "groupdict": normalize_value(match.groupdict()),
        "regs": normalize_value(match.regs),
        "lastindex": normalize_value(match.lastindex),
        "lastgroup": normalize_value(match.lastgroup),
        "pos": normalize_value(match.pos),
        "endpos": normalize_value(match.endpos),
        "capture_offset_checks": checks,
    }


def validate_match(value: Any) -> None:
    require(
        type(value) is dict
        and set(value) == {
            "pattern_is_expected", "string_is_subject", "visible_nested_length",
            "group", "groups", "groupdict", "regs", "lastindex", "lastgroup",
            "pos", "endpos", "capture_offset_checks",
        }
        and value.get("pattern_is_expected") is True
        and value.get("string_is_subject") is True
        and type(value.get("visible_nested_length")) is int
        and value["visible_nested_length"] >= 0
        and type(value.get("capture_offset_checks")) is list,
        "a real match or independently visible nested capture was substituted",
    )
    for key in ("group", "groups", "groupdict", "regs", "lastindex", "lastgroup", "pos", "endpos"):
        validate_normalized_value(value[key])
    for index, check in enumerate(value["capture_offset_checks"]):
        require(
            type(check) is dict
            and set(check) == {
                "group", "start", "end", "missing", "within_visible_nested_buffer",
            }
            and type(check.get("group")) is int
            and check["group"] == index
            and type(check.get("start")) is int
            and type(check.get("end")) is int
            and type(check.get("missing")) is bool
            and type(check.get("within_visible_nested_buffer")) is bool
            and check["missing"] is (check["start"] == -1 and check["end"] == -1)
            and check["within_visible_nested_buffer"] is (
                check["missing"]
                or 0 <= check["start"] <= check["end"] <= value["visible_nested_length"]
            )
            and check["within_visible_nested_buffer"] is True,
            "a capture offset escaped or dereferenced the actual nested visible buffer",
        )


def validate_events(events: Any) -> list[dict[str, Any]]:
    require(type(events) is list, "the complete ordered nested exporter event ledger is mandatory")
    active: dict[tuple[str, str], int] = {
        (role, owner): 0
        for role in ("subject", "template")
        for owner in ("outer", "nested")
    }
    for event in events:
        require(type(event) is dict and type(event.get("event")) is str, "an original event was forged")
        kind = event["event"]
        if kind == "phase":
            require(
                set(event) == {"event", "name"}
                and type(event.get("name")) is str
                and bool(event["name"]),
                "a genuine shape-changing substitution phase was forged",
            )
            continue
        if kind == "callback":
            require(
                set(event) == {"event", "index", "raises", "match"}
                and type(event.get("index")) is int
                and event["index"] >= 0
                and type(event.get("raises")) is bool,
                "a real visible-buffer replacement callback was omitted",
            )
            validate_match(event["match"])
            continue
        require(
            set(event) == {
                "event", "role", "owner", "flags", "active_before",
                "active_after", "outer_size", "nested_size", "outer_hex",
                "nested_hex", "behavior",
            }
            and kind in {"acquire", "acquire-error", "acquire-unwind", "release", "length-probe"}
            and event.get("role") in {"subject", "template"}
            and event.get("owner") in {"outer", "nested"}
            and type(event.get("active_before")) is int
            and event["active_before"] >= 0
            and type(event.get("active_after")) is int
            and event["active_after"] >= 0
            and type(event.get("outer_size")) is int
            and event["outer_size"] >= 0
            and type(event.get("nested_size")) is int
            and event["nested_size"] >= 0
            and event.get("behavior") in BEHAVIORS,
            "a legal nested exporter size, owner, release, or acquisition was forged",
        )
        outer = bytes.fromhex(exact_hex(event.get("outer_hex"), label="outer event"))
        nested = bytes.fromhex(exact_hex(event.get("nested_hex"), label="nested event"))
        require(
            len(outer) == event["outer_size"]
            and len(nested) == event["nested_size"],
            "a genuine zero or differently sized backing event was substituted",
        )
        identity = (event["role"], event["owner"])
        require(
            event["active_before"] == active[identity],
            "a legal nested acquire, unwind, or release was reordered",
        )
        if kind == "acquire":
            require(
                type(event.get("flags")) is int
                and event["flags"] in {SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG}
                and event["active_after"] == active[identity] + 1,
                "a genuine SIMPLE or FULL nested buffer acquisition was forged",
            )
            active[identity] += 1
        elif kind == "acquire-error":
            require(
                type(event.get("flags")) is int
                and event["flags"] in {SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG}
                and event["active_after"] == active[identity]
                and (
                    (event["owner"] == "outer" and event["behavior"] == "fail-outer")
                    or (event["owner"] == "nested" and event["behavior"] == "fail-nested")
                ),
                "a genuine failing outer or nested buffer acquisition was hidden",
            )
        elif kind in {"release", "acquire-unwind"}:
            require(
                event.get("flags") is None
                and active[identity] > 0
                and event["active_after"] == active[identity] - 1,
                "an original nested-buffer release or failure unwind was forged",
            )
            active[identity] -= 1
        else:
            require(
                event.get("flags") is None
                and event["owner"] == "outer"
                and event["active_after"] == active[identity],
                "a genuine outer length probe was hidden",
            )
    return events


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
        "module": (
            ORACLE_CALLBACK_CANONICAL_MODULE
            if type(error) is ShapeCallbackError
            else type(error).__module__
        ),
        "type": type(error).__qualname__,
        "message": str(error),
        "args": normalize_value(error.args),
    }


def validate_error(value: Any) -> None:
    require(type(value) is dict, "a complete exact shape-changing exception is mandatory")
    if value.get("kind") == "ordinary-python-error":
        require(
            set(value) == {"kind", "module", "type", "message", "args"}
            and type(value.get("module")) is str
            and type(value.get("type")) is str
            and type(value.get("message")) is str,
            "a genuine exporter exception class or exact message was hidden",
        )
        validate_normalized_value(value["args"])
        return
    require(
        value.get("kind") == "public-regex-error"
        and set(value) == {
            "kind", "type", "args", "message", "pattern", "position", "line", "column",
        }
        and type(value.get("type")) is str,
        "a genuine shape-related pattern exception was forged",
    )
    for name in ("args", "message", "pattern", "position", "line", "column"):
        validate_normalized_value(value[name])


def normalize_warnings(value: Sequence[Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for item in value:
        require(
            isinstance(item.category, type)
            and isinstance(item.message, item.category),
            "a genuine original substitution warning was forged",
        )
        result.append({
            "category_module": item.category.__module__,
            "category": item.category.__qualname__,
            "message": str(item.message),
        })
    return result


def execute_case(case: Mapping[str, Any], engine: Any) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    callbacks: list[dict[str, Any]] = []
    views: list[memoryview] = []
    subject: Any = None
    template: Any = None
    subject_owner: OuterShapeExporter | None = None
    template_owner: OuterShapeExporter | None = None
    status = "raise"
    stage = "materialize"
    result: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    warning_observations: list[dict[str, str]] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            events.append({"event": "phase", "name": "materialize-start"})
            pattern = bytes.fromhex(case["pattern_hex"])
            subject, subject_owner, subject_views = decode_carrier(
                case["subject"], events, role="subject",
            )
            views.extend(subject_views)
            template, template_owner, template_views = decode_carrier(
                case["template"], events, role="template",
            )
            views.extend(template_views)
            events.append({"event": "phase", "name": "materialize-complete"})
            stage = "compile"
            compiled = engine.compile(pattern, case["flags"])

            def callback(match: Any) -> bytes:
                callback_event = {
                    "event": "callback",
                    "index": len(callbacks),
                    "raises": case["target"] == "callback-error",
                    "match": normalize_match(match, subject, compiled),
                }
                events.append(callback_event)
                callbacks.append(copy.deepcopy(callback_event))
                if callback_event["raises"]:
                    raise ShapeCallbackError("frozen shape-changing callback failure")
                return bytes.fromhex(case["template"]["hex"])

            replacement = callback if case["template"]["kind"] == "callable" else template
            stage = case["api"]
            events.append({"event": "phase", "name": "operation-start"})
            if stage == "module.sub":
                actual = engine.sub(
                    pattern, replacement, subject,
                    count=case["count"], flags=case["flags"],
                )
            elif stage == "module.subn":
                actual = engine.subn(
                    pattern, replacement, subject,
                    count=case["count"], flags=case["flags"],
                )
            elif stage == "pattern.sub":
                actual = compiled.sub(replacement, subject, count=case["count"])
            elif stage == "pattern.subn":
                actual = compiled.subn(replacement, subject, count=case["count"])
            elif stage == "match.expand":
                if case["endpos"] is None:
                    match = compiled.search(subject, case["pos"])
                else:
                    match = compiled.search(subject, case["pos"], case["endpos"])
                actual = None if match is None else match.expand(replacement)
            else:
                raise ShapeOracleError("an unfrozen shape-changing regex API was injected")
            result = normalize_value(actual)
            status = "return"
            events.append({"event": "phase", "name": "operation-return"})
        except ShapeOracleError:
            raise
        except Exception as error:
            failure = normalize_error(error, engine)
            events.append({"event": "phase", "name": "operation-raise"})
        finally:
            for view in reversed(views):
                try:
                    view.release()
                except ValueError:
                    pass
            events.append({"event": "phase", "name": "cleanup-complete"})
            warning_observations = normalize_warnings(caught)
    output = {
        "status": status,
        "stage": stage,
        "value": result,
        "exception": failure,
        "events": copy.deepcopy(events),
        "callbacks": copy.deepcopy(callbacks),
        "warnings": warning_observations,
        "subject_after": normalize_value(subject),
        "template_after": normalize_value(template),
        "subject_outer_active": subject_owner.active if subject_owner is not None else 0,
        "subject_nested_active": subject_owner.nested.active if subject_owner is not None else 0,
        "template_outer_active": template_owner.active if template_owner is not None else 0,
        "template_nested_active": template_owner.nested.active if template_owner is not None else 0,
        "count_requested": case["count"],
        "pos_requested": case["pos"],
        "endpos_requested": case["endpos"],
        "outer_size": case["outer_size"],
        "nested_size": case["nested_size"],
    }
    return validate_outcome(output)


def validate_outcome(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {
            "status", "stage", "value", "exception", "events", "callbacks",
            "warnings", "subject_after", "template_after",
            "subject_outer_active", "subject_nested_active",
            "template_outer_active", "template_nested_active",
            "count_requested", "pos_requested", "endpos_requested",
            "outer_size", "nested_size",
        }
        and value.get("status") in {"return", "raise"}
        and type(value.get("stage")) is str
        and type(value.get("callbacks")) is list
        and type(value.get("warnings")) is list
        and type(value.get("count_requested")) is int
        and type(value.get("pos_requested")) is int
        and (value.get("endpos_requested") is None or type(value.get("endpos_requested")) is int)
        and type(value.get("outer_size")) is int
        and value["outer_size"] >= 0
        and type(value.get("nested_size")) is int
        and value["nested_size"] >= 0,
        "a complete shape-changing buffer observation was omitted",
    )
    events = validate_events(value["events"])
    for role, owner, key in (
        ("subject", "outer", "subject_outer_active"),
        ("subject", "nested", "subject_nested_active"),
        ("template", "outer", "template_outer_active"),
        ("template", "nested", "template_nested_active"),
    ):
        current = value.get(key)
        require(type(current) is int and current >= 0, "a nested live exporter counter was forged")
        acquired = sum(
            1 for event in events
            if event.get("event") == "acquire"
            and event.get("role") == role and event.get("owner") == owner
        )
        released = sum(
            1 for event in events
            if event.get("event") in {"release", "acquire-unwind"}
            and event.get("role") == role and event.get("owner") == owner
        )
        require(
            current == acquired - released,
            "an actual nested exporter release, lifetime, or acquisition was hidden: " + key,
        )
    validate_normalized_value(value["subject_after"])
    validate_normalized_value(value["template_after"])
    if value["status"] == "return":
        require(value["exception"] is None, "a successful replacement hid an exception")
        validate_normalized_value(value["value"])
    else:
        require(value["value"] is None, "a failing replacement hid a result")
        validate_error(value["exception"])
    for callback in value["callbacks"]:
        require(
            type(callback) is dict
            and set(callback) == {"event", "index", "raises", "match"}
            and callback.get("event") == "callback"
            and type(callback.get("index")) is int
            and type(callback.get("raises")) is bool,
            "a real original callback event was hidden",
        )
        validate_match(callback["match"])
    require(
        [event for event in events if event.get("event") == "callback"] == value["callbacks"],
        "a replacement callback was removed from its genuine event order",
    )
    for warning in value["warnings"]:
        require(
            type(warning) is dict
            and set(warning) == {"category_module", "category", "message"}
            and all(type(warning.get(key)) is str for key in warning),
            "a genuine original warning was omitted",
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
        "use the exact isolated pinned stable CPython and shape oracle",
    )
    if not synthetic:
        require(
            os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
            "the exact Python or prospective shape oracle was replaced by a symlink",
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
        and type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
        "an actual exact pinned original source owner is mandatory: " + label,
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
            "an exact original source is not a bounded regular file: " + label,
        )
        remaining = before.st_size
        hasher = hashlib.sha256()
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk), "a pinned original source was truncated")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "a pinned original source has a hidden suffix")
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and hasher.hexdigest() == expected,
            "a frozen original CPython source changed: " + label,
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


def verify_standard_modules(value: Mapping[str, Any] | None = None) -> None:
    modules = sys.modules if value is None else value
    require(isinstance(modules, Mapping), "the genuine standard reference graph is mandatory")
    for name in modules:
        require(
            type(name) is str and name.partition(".")[0] not in FORBIDDEN_ENGINE_ROOTS,
            "a candidate or external matcher entered the isolated standard reference",
        )


def authenticate_standard_reference(source_pin: str) -> tuple[Any, dict[str, dict[str, Any]]]:
    verify_runtime()
    owners = {
        "oracle": read_pinned_file(
            SOURCE_ABSOLUTE,
            source_pin,
            maximum=MAX_SOURCE_BYTES,
            label="frozen shape-changing oracle",
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
            label="frozen original V5 suite",
        ),
        "ownership_audit": read_pinned_file(
            ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
            maximum=MAX_SOURCE_BYTES,
            label="frozen native no-delegation V3 audit",
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
            "an authentic standard reference parser was substituted: " + name,
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
        "the genuine CPython standard reference engine was forged",
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
        "the exact stable CPython, standard regex, V5, and V3 closure is mandatory",
    )
    for name, (path, source_hash) in expected.items():
        owner = value.get(name)
        require(
            type(owner) is dict
            and set(owner) == {"path", "sha256", "bytes", "device", "inode"}
            and owner.get("path") == path
            and owner.get("sha256") == source_hash
            and type(owner.get("bytes")) is int and owner["bytes"] > 0
            and type(owner.get("device")) is int and owner["device"] >= 0
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "a genuine original source owner was forged: " + name,
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
    require(type(value) is dict and value == expected, "a shape reference no-delegation guard was forged")
    return value


def validate_records(
    matrix: list[dict[str, Any]], records: Any, records_pin: str,
) -> list[dict[str, Any]]:
    checked_digest(records_pin, "complete original shape-changing observations")
    require(
        type(records) is list and len(records) == CASE_COUNT,
        "all independently shaped original buffer observations are mandatory",
    )
    for case, record in zip(matrix, records, strict=True):
        require(
            type(record) is dict
            and set(record) == {"case", "cohort", "api", "outer_size", "nested_size", "outcome"}
            and record.get("case") == case["case"]
            and record.get("cohort") == case["cohort"]
            and record.get("api") == case["api"]
            and type(record.get("outer_size")) is int
            and record["outer_size"] == case["outer_size"]
            and type(record.get("nested_size")) is int
            and record["nested_size"] == case["nested_size"],
            "an original zero-length or independently shaped observation was omitted",
        )
        outcome = validate_outcome(record["outcome"])
        require(
            outcome["outer_size"] == case["outer_size"]
            and outcome["nested_size"] == case["nested_size"]
            and outcome["count_requested"] == case["count"]
            and outcome["pos_requested"] == case["pos"]
            and outcome["endpos_requested"] == case["endpos"],
            "a genuine visible buffer size or capture window was substituted",
        )
    require(digest(records) == records_pin, "the complete independent shape outcomes were forged")
    return records


def observe_reference_worker(role: str, source_pin: str) -> dict[str, Any]:
    require(role in {"reference_a", "reference_b"}, "only isolated standard references may run")
    checked_digest(source_pin, "prospectively frozen independent shape source")
    matrix = build_matrix()
    validate_matrix(matrix)
    engine, owners = authenticate_standard_reference(source_pin)
    records: list[dict[str, Any]] = []
    checks = 0
    for case in matrix:
        verify_standard_modules()
        checks += 1
        try:
            observed = execute_case(case, engine)
        finally:
            verify_standard_modules()
            checks += 1
        records.append({
            "case": case["case"],
            "cohort": case["cohort"],
            "api": case["api"],
            "outer_size": case["outer_size"],
            "nested_size": case["nested_size"],
            "outcome": observed,
        })
    records_sha256 = digest(records)
    validate_records(matrix, records, records_sha256)
    after = authenticate_standard_reference(source_pin)[1]
    require(owners == after, "a pinned original source changed during shape observation")
    result = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": os.getpid(),
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
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
    return validate_reference_worker(
        result,
        role=role,
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=result["pid"],
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
        and type(expected_pid) is int and expected_pid > 0,
        "an exact independently isolated shape reference identity is mandatory",
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
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
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
        "a complete independent shape reference worker was forged",
    )
    for key, original in expected.items():
        require(
            value.get(key) == original and type(value.get(key)) is type(original),
            "a real shape-reference field was substituted: " + key,
        )
    validate_source_owners(value["source_owners"], source_pin)
    validate_reference_guard(value["reference_guard"])
    validate_records(matrix, value["records"], value["records_sha256"])
    return value


def encode_stream(value: Any) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_PROCESS_BYTES, "a complete worker stream is mandatory")
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
        "a complete reversible original shape reference stream was hidden: " + label,
    )
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (TypeError, ValueError, UnicodeError) as error:
        raise ShapeOracleError("a complete original shape stream is invalid: " + label) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == value["sha256"]
        and base64.b64encode(raw).decode("ascii") == value["base64"],
        "a complete shape-reference stream was truncated or substituted",
    )
    return raw


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
        "a genuine isolated shape reference process was forged",
    )
    stdout = decode_stream(value["stdout"], role + " stdout")
    stderr = decode_stream(value["stderr"], role + " stderr")
    require(
        stdout == canonical(dict(worker)) and stderr == b"",
        "a complete shape reference stream differs from its actual worker",
    )
    return value


def run_isolated_reference(
    role: str,
    source_pin: str,
    matrix: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in {"reference_a", "reference_b"}, "only genuine standard workers may run")
    command = [
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
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            cwd=ROOT,
            env={
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
        )
        stdout, stderr = process.communicate()
    except (OSError, subprocess.SubprocessError) as error:
        raise ReferenceWorkerFailure(
            "an exact isolated stable CPython shape reference could not start",
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
        raise ReferenceWorkerFailure("a genuine isolated standard shape worker failed", evidence)
    try:
        worker = validate_reference_worker(
            decode_canonical(stdout, role),
            role=role,
            source_pin=source_pin,
            matrix=matrix,
            expected_pid=process.pid,
        )
        validate_process_evidence(evidence, worker, role=role)
    except (ShapeOracleError, TypeError, ValueError, KeyError) as error:
        evidence["validation_error"] = {
            "type": type(error).__qualname__,
            "message": str(error),
        }
        raise ReferenceWorkerFailure(
            "a complete isolated shape worker failed evidence validation",
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
        "two independent genuine standard shape references disagree",
    )
    return first["records_sha256"]


def run_baseline(source_pin: str, matrix_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "explicitly frozen legal shape oracle")
    checked_digest(matrix_pin, "explicitly frozen legal shape property matrix")
    require(matrix_pin == MATRIX_SHA256, "the exact frozen shape matrix was substituted")
    matrix = build_matrix()
    validate_matrix(matrix, matrix_pin)
    _, owners = authenticate_standard_reference(source_pin)
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
    require(owners == after == first["source_owners"], "a genuine original source changed")
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
        "shape_sizes": dict(SHAPE_SIZES),
        "baseline_records_sha256": records_sha256,
        "source_owners": owners,
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
    """Deny all actual files, engines, workers, clocks, and randomness."""

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
            "matcher_invocations": 0,
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
                target = args[0]
                if type(target) is str and (
                    target == "candidates"
                    or target.startswith("candidates.")
                    or target.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS
                ):
                    selected = "candidate_imports"
            self.blocked[selected] += 1
            raise SourceOnlyError("synthetic shape controls cannot perform " + selected)

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        operations = (
            (builtins, "open", "file_reads"),
            (io, "open", "file_reads"),
            (os, "open", "file_reads"),
            (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"),
            (os, "fstat", "file_reads"),
            (os, "listdir", "file_reads"),
            (os, "scandir", "file_reads"),
            (os, "readlink", "file_reads"),
            (os, "write", "file_writes"),
            (os, "replace", "file_writes"),
            (os, "rename", "file_writes"),
            (os, "remove", "file_writes"),
            (os, "unlink", "file_writes"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (os, "fsync", "file_writes"),
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
            (builtins, "__import__", "dynamic_imports"),
            (importlib, "import_module", "dynamic_imports"),
        )
        for owner, name, category in operations:
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
            "inode": 1100 + index,
        }
        for index, (name, (path, pinned)) in enumerate(values.items())
    }


def synthetic_witnessed_regression_match(payload: bytes) -> dict[str, Any]:
    require(
        type(payload) is bytes
        and len(payload) in WITNESSED_REGRESSION_NESTED_SIZES,
        "a witnessed outer-13 visible nested capture payload is mandatory",
    )
    visible = len(payload)
    end = min(1, visible)
    capture = payload[:end]
    offsets = ((0, end), (0, end), (-1, -1))
    result = {
        "pattern_is_expected": True,
        "string_is_subject": True,
        "visible_nested_length": visible,
        "group": normalize_value(capture),
        "groups": normalize_value((capture, None)),
        "groupdict": normalize_value({"visible": capture, "missing": None}),
        "regs": normalize_value(offsets),
        "lastindex": normalize_value(1),
        "lastgroup": normalize_value("visible"),
        "pos": normalize_value(0),
        "endpos": normalize_value(visible),
        "capture_offset_checks": [
            {
                "group": index,
                "start": start,
                "end": stop,
                "missing": start == -1 and stop == -1,
                "within_visible_nested_buffer": (
                    (start == -1 and stop == -1)
                    or 0 <= start <= stop <= visible
                ),
            }
            for index, (start, stop) in enumerate(offsets)
        ],
    }
    validate_match(result)
    return result



def synthetic_callback_topology_outcome(
    case: Mapping[str, Any],
    engine: Any,
) -> dict[str, Any]:
    """Build complete callback evidence without calling any matcher."""
    require(
        type(case) is dict
        and case.get("target") == "callback-error"
        and case.get("api") in APIS[:-1]
        and case.get("behavior") in {"stable", "mutate"}
        and type(engine) is types.SimpleNamespace
        and getattr(engine, "error", object()) is None,
        "a source-only original callback topology case was forged",
    )
    subject = validate_carrier(case["subject"], role="subject")
    template = validate_carrier(case["template"], role="template")
    require(
        subject["kind"] == "shape-exporter"
        and template["kind"] == "callable"
        and template["raises"] is True,
        "a source-only original failing callback carrier was changed",
    )
    payload = bytes.fromhex(subject["nested_hex"])
    visible = len(payload)
    stop = min(1, visible)
    capture = payload[:stop]
    offsets = ((0, stop), (0, stop), (-1, -1))
    match = {
        "pattern_is_expected": True,
        "string_is_subject": True,
        "visible_nested_length": visible,
        "group": normalize_value(capture),
        "groups": normalize_value((capture, None)),
        "groupdict": normalize_value({
            "word": capture,
            "number": None,
        }),
        "regs": normalize_value(offsets),
        "lastindex": normalize_value(1),
        "lastgroup": normalize_value("word"),
        "pos": normalize_value(0),
        "endpos": normalize_value(visible),
        "capture_offset_checks": [
            {
                "group": index,
                "start": start,
                "end": end,
                "missing": start == -1 and end == -1,
                "within_visible_nested_buffer": (
                    (start == -1 and end == -1)
                    or 0 <= start <= end <= visible
                ),
            }
            for index, (start, end) in enumerate(offsets)
        ],
    }
    validate_match(match)
    callback = {
        "event": "callback",
        "index": 0,
        "raises": True,
        "match": match,
    }
    events = [
        {"event": "phase", "name": "materialize-start"},
        {"event": "phase", "name": "materialize-complete"},
        {"event": "phase", "name": "operation-start"},
        callback,
        {"event": "phase", "name": "operation-raise"},
        {"event": "phase", "name": "cleanup-complete"},
    ]
    subject_owner = OuterShapeExporter(subject, [])
    callback_error = ShapeCallbackError(
        "frozen shape-changing callback failure",
    )
    return validate_outcome({
        "status": "raise",
        "stage": case["api"],
        "value": None,
        "exception": normalize_error(callback_error, engine),
        "events": copy.deepcopy(events),
        "callbacks": [copy.deepcopy(callback)],
        "warnings": [],
        "subject_after": normalize_value(subject_owner),
        "template_after": normalize_value(
            bytes.fromhex(template["hex"]),
        ),
        "subject_outer_active": 0,
        "subject_nested_active": 0,
        "template_outer_active": 0,
        "template_nested_active": 0,
        "count_requested": case["count"],
        "pos_requested": case["pos"],
        "endpos_requested": case["endpos"],
        "outer_size": case["outer_size"],
        "nested_size": case["nested_size"],
    })


def synthetic_outcome(case: Mapping[str, Any]) -> dict[str, Any]:
    result = {
        "status": "return",
        "stage": case["api"],
        "value": normalize_value(None),
        "exception": None,
        "events": [
            {"event": "phase", "name": "materialize-start"},
            {"event": "phase", "name": "materialize-complete"},
            {"event": "phase", "name": "operation-start"},
            {"event": "phase", "name": "operation-return"},
            {"event": "phase", "name": "cleanup-complete"},
        ],
        "callbacks": [],
        "warnings": [],
        "subject_after": normalize_value(None),
        "template_after": normalize_value(None),
        "subject_outer_active": 0,
        "subject_nested_active": 0,
        "template_outer_active": 0,
        "template_nested_active": 0,
        "count_requested": case["count"],
        "pos_requested": case["pos"],
        "endpos_requested": case["endpos"],
        "outer_size": case["outer_size"],
        "nested_size": case["nested_size"],
    }
    return validate_outcome(result)


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "case": case["case"],
            "cohort": case["cohort"],
            "api": case["api"],
            "outer_size": case["outer_size"],
            "nested_size": case["nested_size"],
            "outcome": synthetic_outcome(case),
        }
        for case in matrix
    ]


def synthetic_reference(
    role: str,
    pid: int,
    source_pin: str,
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
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
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
        "a future independently owned native shape candidate was forged",
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
        "a future shape candidate borrowed a sibling or external matcher",
    )
    for key in ("adapter_sha256", "engine_sha256", "bridge_sha256"):
        checked_digest(value[key], "future independently owned shape candidate " + key)
    require(
        (value["engine_relative"] == value["bridge_relative"]) is (family == "c")
        and (value["engine_sha256"] == value["bridge_sha256"]) is (family == "c"),
        "only the genuinely combined C engine and bridge may alias",
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
    require(family in adapters, "a genuine independent candidate family is mandatory")
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

        def accept(label: str, value: Any) -> None:
            require(value, "a shape-changing synthetic positive control failed: " + label)
            accepted.append(label)

        def reject(label: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (ShapeOracleError, OSError, TypeError, ValueError, KeyError, IndexError, BufferError):
                rejected.append(label)
                return
            raise ShapeOracleError("forged shape-changing evidence was accepted: " + label)

        matrix = build_matrix()
        validate_matrix(matrix)
        accept("freeze-all-10240-independent-legal-buffer-shapes", len(matrix) == 10_240)
        accept("freeze-all-64-independent-outer-nested-pairs", len(COHORTS) == 64)
        accept("freeze-all-160-balanced-cross-product-variants", all(
            sum(row["cohort"] == cohort for row in matrix) == VARIANTS_PER_COHORT
            for cohort in COHORTS
        ))
        accept(
            "freeze-exact-eight-witnessed-and-independent-backing-lengths",
            tuple(SHAPE_SIZES.values()) == (0, 1, 2, 3, 5, 8, 13, 19),
        )
        accept("freeze-full-precision-unsigned-64-bit-seed", 0 <= PUBLISHED_SEED < 1 << 64)
        accept("freeze-exact-canonical-ordered-shape-matrix", digest(matrix) == MATRIX_SHA256)
        accept("freeze-every-zero-one-two-three-five-eight-thirteen-nineteen-outer-size", {
            row["outer_shape"] for row in matrix
        } == set(SHAPE_NAMES))
        accept("freeze-every-zero-one-two-three-five-eight-thirteen-nineteen-nested-size", {
            row["nested_shape"] for row in matrix
        } == set(SHAPE_NAMES))
        accept("freeze-full-64-cell-independent-shape-cartesian-product", {
            (row["outer_shape"], row["nested_shape"]) for row in matrix
        } == {(outer, nested) for outer in SHAPE_NAMES for nested in SHAPE_NAMES})
        accept(
            "freeze-exact-witnessed-outer-thirteen-regression-backing",
            WITNESSED_REGRESSION_OUTER_SIZE == 13
            and SHAPE_SIZES[WITNESSED_REGRESSION_OUTER_SHAPE] == 13,
        )
        accept(
            "freeze-every-exact-witnessed-nested-zero-one-two-five-eight",
            WITNESSED_REGRESSION_NESTED_SIZES == (0, 1, 2, 5, 8)
            and tuple(
                SHAPE_SIZES[shape]
                for shape in WITNESSED_REGRESSION_NESTED_SHAPES
            ) == WITNESSED_REGRESSION_NESTED_SIZES,
        )
        accept("cover-all-module-compiled-and-expand-apis", {row["api"] for row in matrix} == set(APIS))
        accept("cover-all-direct-wrapped-template-and-callback-targets", {
            row["target"] for row in matrix
        } == set(TARGETS))
        accept("cover-stable-mutating-outer-and-nested-failing-exporters", {
            row["behavior"] for row in matrix
        } == set(BEHAVIORS))
        accept("cover-empty-lookahead-optional-and-named-captures", {
            row["pattern_kind"] for row in matrix
        } == set(PATTERN_KINDS))
        accept("cover-literal-named-numbered-invalid-and-missing-templates", {
            row["template_style"] for row in matrix
        } == set(TEMPLATE_STYLES))
        accept("cover-zero-null-safe-nested-source", any(
            row["nested_size"] == 0 and row["outer_size"] > 0 for row in matrix
        ))
        accept("cover-zero-outer-nonempty-visible-backing", any(
            row["outer_size"] == 0 and row["nested_size"] > 0 for row in matrix
        ))
        accept("cover-shorter-and-longer-independent-visible-storage", any(
            row["nested_size"] < row["outer_size"] for row in matrix
        ) and any(row["nested_size"] > row["outer_size"] for row in matrix))
        accept("freeze-independent-v3-from-scratch-audit", OWNERSHIP_AUDIT_SHA256 == (
            "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
        ))

        accept(
            "preserve-falsified-immutable-original-shape-v1",
            HISTORICAL_V1_STATUS == "FALSIFIED"
            and HISTORICAL_V1_ORACLE_SHA256
            == "866dbf7bf4a48a867b3aaacd05cfa4f1346c747931543fa386835e783f0073aa"
            and HISTORICAL_V1_RECORDER_SHA256
            == "047bcc25a3b033fa374576c434b0e6ebcc6c97cf99965e9cc9083c012249529c",
        )
        accept(
            "preserve-all-twelve-signed-original-shape-evidence-files",
            len(HISTORICAL_V1_PINNED_FILES) == 12
            and all(
                type(relative) is str
                and bool(relative)
                and not relative.startswith("/")
                and ".." not in relative.split("/")
                and valid_digest(pinned)
                for relative, pinned
                in HISTORICAL_V1_PINNED_FILES.values()
            ),
        )
        accept(
            "preserve-complete-original-reference-candidate-and-ledger-digests",
            valid_digest(HISTORICAL_V1_REFERENCE_RECORDS_SHA256)
            and valid_digest(HISTORICAL_V1_C_CANDIDATE_RECORDS_SHA256)
            and valid_digest(HISTORICAL_V1_C_MISMATCH_LEDGER_SHA256)
            and len({
                HISTORICAL_V1_REFERENCE_RECORDS_SHA256,
                HISTORICAL_V1_C_CANDIDATE_RECORDS_SHA256,
                HISTORICAL_V1_C_MISMATCH_LEDGER_SHA256,
            }) == 3,
        )
        accept(
            "preserve-all-1392-real-losses-and-496-harness-artifacts",
            dict(HISTORICAL_V1_FAILURE_COUNTS) == {"c": 1_888}
            and dict(HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS)
            == {"c": 496}
            and dict(HISTORICAL_V1_REAL_FAILURE_COUNTS)
            == {"c": 1_392}
            and HISTORICAL_V1_FAILURE_COUNTS["c"]
            == HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS["c"]
            + HISTORICAL_V1_REAL_FAILURE_COUNTS["c"],
        )

        def deny_synthetic_matcher(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            boundary.blocked["matcher_invocations"] += 1
            raise SourceOnlyError(
                "source-only shape controls cannot call any matcher",
            )

        synthetic_engine = types.SimpleNamespace(
            error=None,
            compile=deny_synthetic_matcher,
            search=deny_synthetic_matcher,
            match=deny_synthetic_matcher,
            fullmatch=deny_synthetic_matcher,
            sub=deny_synthetic_matcher,
            subn=deny_synthetic_matcher,
            split=deny_synthetic_matcher,
            findall=deny_synthetic_matcher,
            finditer=deny_synthetic_matcher,
        )
        callback_cases = [
            case
            for case in matrix
            if case["target"] == "callback-error"
            and case["api"] in APIS[:-1]
            and case["behavior"] in {"stable", "mutate"}
        ]
        accept(
            "cover-all-512-source-only-original-callback-contexts",
            len(callback_cases) == 512
            and {
                case["api"] for case in callback_cases
            } == set(APIS[:-1])
            and {
                case["cohort"] for case in callback_cases
            } == set(COHORTS)
            and all(
                sum(
                    case["api"] == api
                    for case in callback_cases
                ) == 128
                for api in APIS[:-1]
            )
            and all(
                sum(
                    case["cohort"] == cohort
                    for case in callback_cases
                ) == 8
                for cohort in COHORTS
            ),
        )
        callback_topology_checks = 0
        original_callback_module = ShapeCallbackError.__module__
        try:
            for callback_case in callback_cases:
                ShapeCallbackError.__module__ = "__main__"
                script_observation = (
                    synthetic_callback_topology_outcome(
                        callback_case,
                        synthetic_engine,
                    )
                )
                ShapeCallbackError.__module__ = (
                    ORACLE_CALLBACK_CANONICAL_MODULE
                )
                imported_observation = (
                    synthetic_callback_topology_outcome(
                        callback_case,
                        synthetic_engine,
                    )
                )
                require(
                    script_observation == imported_observation
                    and canonical(script_observation)
                    == canonical(imported_observation)
                    and script_observation["status"] == "raise"
                    and script_observation["exception"]["kind"]
                    == "ordinary-python-error"
                    and script_observation["exception"]["type"]
                    == "ShapeCallbackError"
                    and script_observation["exception"]["module"]
                    == ORACLE_CALLBACK_CANONICAL_MODULE
                    and script_observation["exception"]["message"]
                    == "frozen shape-changing callback failure"
                    and script_observation["exception"]["args"]
                    == normalize_value((
                        "frozen shape-changing callback failure",
                    ))
                    and len(script_observation["callbacks"]) == 1
                    and script_observation["callbacks"][0]["raises"]
                    is True
                    and script_observation["outer_size"]
                    == callback_case["outer_size"]
                    and script_observation["nested_size"]
                    == callback_case["nested_size"],
                    "complete source-only script/import callback "
                    "topology evidence disagrees: "
                    + callback_case["case"],
                )
                callback_topology_checks += 1
        finally:
            ShapeCallbackError.__module__ = (
                original_callback_module
            )
        accept(
            "prove-all-512-synthetic-script-import-callback-pairs",
            callback_topology_checks == len(callback_cases)
            and callback_topology_checks == 512
            and ShapeCallbackError.__module__
            == original_callback_module
            and boundary.blocked["matcher_invocations"] == 0,
        )

        foreign_same_name = type(
            "ShapeCallbackError",
            (Exception,),
            {"__module__": "__main__"},
        )
        foreign_same_module = type(
            "ShapeCallbackError",
            (Exception,),
            {"__module__": ORACLE_CALLBACK_CANONICAL_MODULE},
        )
        own_subclass = type(
            "DerivedShapeCallbackError",
            (ShapeCallbackError,),
            {"__module__": "__main__"},
        )
        for label, foreign, expected_module in (
            ("same-name-foreign-user", foreign_same_name, "__main__"),
            (
                "same-name-and-module-foreign-user",
                foreign_same_module,
                ORACLE_CALLBACK_CANONICAL_MODULE,
            ),
            ("own-callback-subclass", own_subclass, "__main__"),
            ("ordinary-user-type-error", TypeError, "builtins"),
            ("ordinary-user-value-error", ValueError, "builtins"),
            ("ordinary-user-buffer-error", BufferError, "builtins"),
        ):
            instance = foreign(
                "frozen shape-changing callback failure",
            )
            observed = normalize_error(
                instance,
                synthetic_engine,
            )
            accept(
                "preserve-exact-user-exception-identity-" + label,
                type(instance) is not ShapeCallbackError
                and observed["kind"] == "ordinary-python-error"
                and observed["module"] == expected_module
                and observed["type"]
                == type(instance).__qualname__
                and observed["message"] == str(instance)
                and observed["args"]
                == normalize_value(instance.args)
                and validate_error(observed) is None,
            )
            if expected_module != (
                ORACLE_CALLBACK_CANONICAL_MODULE
            ):
                forged = copy.deepcopy(observed)
                forged["module"] = (
                    ORACLE_CALLBACK_CANONICAL_MODULE
                )
                reject(
                    "reject-canonicalized-foreign-exception-" + label,
                    lambda observed=observed, forged=forged: (
                        require(
                            observed == forged,
                            "a foreign user exception was silently "
                            "rewritten as the harness callback",
                        )
                    ),
                )
        own_callback = ShapeCallbackError(
            "frozen shape-changing callback failure",
        )
        own_observation = normalize_error(
            own_callback,
            synthetic_engine,
        )
        accept(
            "canonicalize-only-exact-owned-callback-class-identity",
            type(own_callback) is ShapeCallbackError
            and own_observation["kind"]
            == "ordinary-python-error"
            and own_observation["module"]
            == ORACLE_CALLBACK_CANONICAL_MODULE
            and own_observation["type"]
            == "ShapeCallbackError"
            and own_observation["message"]
            == "frozen shape-changing callback failure"
            and own_observation["args"]
            == normalize_value(own_callback.args)
            and validate_error(own_observation) is None,
        )

        for outer_shape in SHAPE_NAMES:
            for nested_shape in SHAPE_NAMES:
                outer_size = SHAPE_SIZES[outer_shape]
                nested_size = SHAPE_SIZES[nested_shape]
                event_log: list[dict[str, Any]] = []
                descriptor = exporter_descriptor(
                    role="subject",
                    outer_shape=outer_shape,
                    nested_shape=nested_shape,
                    outer_payload=shaped_bytes(b"OUTER", outer_size, b"shape"),
                    nested_payload=shaped_bytes(b"aa12bb34", nested_size, b"shape"),
                    behavior="stable",
                    wrapped=False,
                )
                exporter = OuterShapeExporter(descriptor, event_log)
                view = exporter.__buffer__(SIMPLE_BUFFER_FLAG)
                accept(
                    "honor-visible-nested-length-" + outer_shape + "-" + nested_shape,
                    type(view) is memoryview and view.nbytes == nested_size,
                )
                accept(
                    "preserve-independent-outer-length-" + outer_shape + "-" + nested_shape,
                    len(exporter.backing) == outer_size,
                )
                exporter.__release_buffer__(view)
                view.release()
                accept(
                    "release-full-nested-lifetime-" + outer_shape + "-" + nested_shape,
                    exporter.active == 0 and exporter.nested.active == 0
                    and validate_events(event_log) is event_log,
                )
                accept(
                    "freeze-simple-and-full-nested-flags-" + outer_shape + "-" + nested_shape,
                    [event["flags"] for event in event_log if event["event"] == "acquire"]
                    == [SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG],
                )

        for nested_shape in WITNESSED_REGRESSION_NESTED_SHAPES:
            nested_size = SHAPE_SIZES[nested_shape]
            cohort = (
                "outer-" + WITNESSED_REGRESSION_OUTER_SHAPE
                + "-nested-" + nested_shape
            )
            witnessed_rows = [row for row in matrix if row["cohort"] == cohort]
            accept(
                "retain-every-witnessed-outer-thirteen-nested-"
                + nested_shape + "-case",
                len(witnessed_rows) == VARIANTS_PER_COHORT
                and all(
                    row["outer_size"] == WITNESSED_REGRESSION_OUTER_SIZE
                    and row["nested_size"] == nested_size
                    for row in witnessed_rows
                ),
            )
            accept(
                "retain-every-witnessed-outer-thirteen-nested-"
                + nested_shape + "-api-placement-and-behavior",
                {
                    (row["api"], row["target"], row["behavior"])
                    for row in witnessed_rows
                } == {
                    (api, target, behavior)
                    for api in APIS
                    for target in TARGETS
                    for behavior in BEHAVIORS
                },
            )
            nested_payload = shaped_bytes(b"aa12bb34", nested_size, b"witness")
            observed_match = synthetic_witnessed_regression_match(nested_payload)
            accept(
                "preserve-null-safe-witnessed-outer-thirteen-nested-"
                + nested_shape + "-visible-capture-offsets",
                validate_match(observed_match) is None
                and observed_match["visible_nested_length"] == nested_size
                and all(
                    check["within_visible_nested_buffer"]
                    for check in observed_match["capture_offset_checks"]
                ),
            )
            forged_match = copy.deepcopy(observed_match)
            forged_match["capture_offset_checks"][0]["end"] = nested_size + 1
            forged_match["capture_offset_checks"][0][
                "within_visible_nested_buffer"
            ] = True
            reject(
                "reject-witnessed-outer-thirteen-nested-" + nested_shape
                + "-out-of-bounds-visible-offset",
                lambda forged_match=forged_match: validate_match(forged_match),
            )

            for role in ("subject", "template"):
                for behavior in BEHAVIORS:
                    witnessed_events: list[dict[str, Any]] = []
                    outer_payload = shaped_bytes(
                        b"OUTERalpha42",
                        WITNESSED_REGRESSION_OUTER_SIZE,
                        b"witness",
                    )
                    descriptor = exporter_descriptor(
                        role=role,
                        outer_shape=WITNESSED_REGRESSION_OUTER_SHAPE,
                        nested_shape=nested_shape,
                        outer_payload=outer_payload,
                        nested_payload=nested_payload,
                        behavior=behavior,
                        wrapped=False,
                    )
                    exporter = OuterShapeExporter(descriptor, witnessed_events)
                    label = (
                        "witnessed-outer-thirteen-nested-" + nested_shape
                        + "-" + role + "-" + behavior
                    )
                    if behavior in {"stable", "mutate"}:
                        view = exporter.__buffer__(SIMPLE_BUFFER_FLAG)
                        accept(
                            "preserve-" + label + "-exact-visible-output",
                            type(view) is memoryview
                            and view.nbytes == nested_size
                            and bytes(view) == nested_payload
                            and len(exporter.backing)
                            == WITNESSED_REGRESSION_OUTER_SIZE,
                        )
                        exporter.__release_buffer__(view)
                        view.release()
                        expected_outer = (
                            b"?" * WITNESSED_REGRESSION_OUTER_SIZE
                            if behavior == "mutate" else outer_payload
                        )
                        expected_nested = (
                            b"!" * nested_size
                            if behavior == "mutate" else nested_payload
                        )
                        accept(
                            "preserve-" + label + "-exact-backing-and-lifetime",
                            bytes(exporter.backing) == expected_outer
                            and bytes(exporter.nested.backing) == expected_nested
                            and exporter.active == exporter.nested.active == 0,
                        )
                        accept(
                            "preserve-" + label + "-exact-acquisition-flags",
                            [
                                event["flags"]
                                for event in witnessed_events
                                if event["event"] == "acquire"
                            ] == [
                                SIMPLE_BUFFER_FLAG,
                                FULL_READONLY_BUFFER_FLAG,
                            ],
                        )
                        accept(
                            "preserve-" + label + "-complete-lifo-event-ledger",
                            validate_events(witnessed_events) is witnessed_events
                            and [
                                (event["owner"], event["event"])
                                for event in witnessed_events
                            ] == [
                                ("outer", "acquire"),
                                ("nested", "acquire"),
                                ("outer", "release"),
                                ("nested", "release"),
                            ],
                        )
                    else:
                        observed_error: BaseException | None = None
                        try:
                            unexpected = exporter.__buffer__(SIMPLE_BUFFER_FLAG)
                        except BufferError as error:
                            observed_error = error
                        else:
                            exporter.__release_buffer__(unexpected)
                            unexpected.release()
                        message = (
                            "frozen shape-changing outer exporter failure"
                            if behavior == "fail-outer"
                            else "frozen shape-changing nested exporter failure"
                        )
                        if observed_error is not None:
                            exact_error = normalize_error(observed_error, object())
                        else:
                            exact_error = None
                        accept(
                            "preserve-" + label + "-exact-original-buffer-error",
                            type(observed_error) is BufferError
                            and type(exact_error) is dict
                            and validate_error(exact_error) is None
                            and exact_error["kind"] == "ordinary-python-error"
                            and exact_error["module"] == "builtins"
                            and exact_error["type"] == "BufferError"
                            and exact_error["message"] == message
                            and exact_error["args"] == normalize_value((message,)),
                        )
                        expected_events = (
                            [("outer", "acquire-error", SIMPLE_BUFFER_FLAG)]
                            if behavior == "fail-outer"
                            else [
                                ("outer", "acquire", SIMPLE_BUFFER_FLAG),
                                (
                                    "nested", "acquire-error",
                                    FULL_READONLY_BUFFER_FLAG,
                                ),
                                ("outer", "acquire-unwind", None),
                            ]
                        )
                        accept(
                            "preserve-" + label + "-exact-failure-flags-and-events",
                            validate_events(witnessed_events) is witnessed_events
                            and [
                                (
                                    event["owner"], event["event"],
                                    event["flags"],
                                )
                                for event in witnessed_events
                            ] == expected_events,
                        )
                        accept(
                            "preserve-" + label + "-complete-failure-unwind",
                            exporter.active == exporter.nested.active == 0
                            and bytes(exporter.backing) == outer_payload
                            and bytes(exporter.nested.backing) == nested_payload,
                        )

        for behavior in ("mutate", "fail-outer", "fail-nested"):
            events: list[dict[str, Any]] = []
            descriptor = exporter_descriptor(
                role="template",
                outer_shape="long",
                nested_shape="short",
                outer_payload=shaped_bytes(b"OUTER", SHAPE_SIZES["long"], b"shape"),
                nested_payload=shaped_bytes(b"aa12", SHAPE_SIZES["short"], b"shape"),
                behavior=behavior,
                wrapped=False,
            )
            exporter = OuterShapeExporter(descriptor, events)
            if behavior == "mutate":
                view = exporter.__buffer__(SIMPLE_BUFFER_FLAG)
                exporter.__release_buffer__(view)
                view.release()
                accept(
                    "preserve-exact-independently-sized-outer-and-nested-mutation",
                    bytes(exporter.backing) == b"?" * SHAPE_SIZES["long"]
                    and bytes(exporter.nested.backing) == b"!" * SHAPE_SIZES["short"]
                    and exporter.active == exporter.nested.active == 0
                    and validate_events(events) is events,
                )
            else:
                reject(
                    "preserve-exact-" + behavior + "-buffer-exception",
                    lambda exporter=exporter: exporter.__buffer__(SIMPLE_BUFFER_FLAG),
                )
                accept(
                    "unwind-all-owned-" + behavior + "-buffers",
                    exporter.active == exporter.nested.active == 0
                    and validate_events(events) is events,
                )

        for item in (
            None, True, False, 0, 1, "\ud800", b"", b"\x00\xff",
            bytearray(), bytearray(b"ab"), (), (1, -1), [], [0, b"a"],
            {"visible": 0, "outer": 19},
        ):
            observed = normalize_value(item)
            accept(
                "preserve-exact-shape-observable-" + str(len(accepted)),
                validate_normalized_value(observed) is None,
            )

        source_pin = hashlib.sha256(b"synthetic-shape-changing-oracle-v2").hexdigest()
        records = synthetic_records(matrix)
        pin = digest(records)
        owners = synthetic_source_owners(source_pin)
        accept("authenticate-complete-immutable-reference-source-closure", validate_source_owners(owners, source_pin) is owners)
        accept(
            "retain-all-10240-complete-synthetic-case-observations",
            validate_records(matrix, records, pin) is records,
        )
        first = synthetic_reference("reference_a", 7101, source_pin, records)
        second = synthetic_reference("reference_b", 7102, source_pin, records)
        first_process = synthetic_process(first)
        second_process = synthetic_process(second)
        accept("authenticate-first-source-only-synthetic-reference", validate_reference_worker(
            first, role="reference_a", source_pin=source_pin, matrix=matrix, expected_pid=7101,
        ) is first)
        accept("authenticate-second-source-only-synthetic-reference", validate_reference_worker(
            second, role="reference_b", source_pin=source_pin, matrix=matrix, expected_pid=7102,
        ) is second)
        accept("require-distinct-synthetic-reference-process-identities", first["pid"] != second["pid"])
        accept("preserve-complete-reversible-reference-stdout", decode_stream(
            first_process["stdout"], "reference_a",
        ) == canonical(first))
        accept("preserve-complete-empty-reference-stderr", decode_stream(
            first_process["stderr"], "reference_a",
        ) == b"")
        accept("require-two-identical-complete-synthetic-reference-vectors", validate_reference_pair(
            first, second, first_process, second_process,
            source_pin=source_pin, matrix=matrix,
        ) == pin)

        for family in ("rust", "c", "zig"):
            future = synthetic_candidate_pins(family)
            accept(
                "preserve-independently-owned-future-" + family + "-shape-engine",
                validate_future_candidate_pins(future) is future,
            )
            for key in future:
                forged = dict(future)
                if key == "family":
                    forged[key] = "external"
                elif key in {"adapter_sha256", "engine_sha256", "bridge_sha256"}:
                    forged[key] = "0" * 64
                elif key.endswith("sha256"):
                    forged[key] = hashlib.sha256(("foreign-" + key).encode("ascii")).hexdigest()
                else:
                    forged[key] = "candidates/foreign-regex.so"
                reject(
                    "reject-" + family + "-foreign-" + key,
                    lambda forged=forged: validate_future_candidate_pins(forged),
                )

        for key in (
            "case", "cohort", "variant", "seed", "outer_shape", "nested_shape",
            "outer_size", "nested_size", "api", "target", "behavior", "pattern_kind",
            "template_style", "flags", "count", "pos", "endpos", "pattern_hex",
            "subject", "template",
        ):
            forged = list(matrix)
            item = dict(forged[0])
            del item[key]
            forged[0] = item
            reject(
                "reject-omitted-complete-shape-case-" + key,
                lambda forged=forged: validate_matrix(forged),
            )
        for title, transform in (
            ("missing-first", lambda values: values.pop(0)),
            ("missing-last", lambda values: values.pop()),
            ("duplicate", lambda values: values.__setitem__(1, values[0])),
            ("reordered", lambda values: values.__setitem__(slice(0, 2), [values[1], values[0]])),
            ("added", lambda values: values.append(values[0])),
        ):
            forged = list(matrix)
            transform(forged)
            reject("reject-" + title + "-shape-matrix", lambda forged=forged: validate_matrix(forged))

        for key in (
            "schema", "status", "python", "role", "pid", "oracle_source_sha256",
            "matrix_sha256", "published_seed", "case_count", "cohort_count",
            "variants_per_cohort", "shape_sizes", "records_sha256", "records",
            "source_owners", "reference_guard", "actual_reference_workers",
            "actual_candidate_workers", "actual_candidate_imports", "clock_samples",
            "timing_trials_run", "workspace_files_written", "evidence_files_created",
            "benchmark_files_read", "hidden_cases_read", "performance",
            "candidate_qualified_for_hidden_benchmark", "final_winner_selected",
        ):
            forged = dict(first)
            del forged[key]
            reject(
                "reject-incomplete-original-worker-" + key,
                lambda forged=forged: validate_reference_worker(
                    forged,
                    role="reference_a",
                    source_pin=source_pin,
                    matrix=matrix,
                    expected_pid=7101,
                ),
            )
        for key in first["reference_guard"]:
            forged = dict(first["reference_guard"])
            if type(forged[key]) is bool:
                forged[key] = not forged[key]
            elif type(forged[key]) is int:
                forged[key] += 1
            else:
                forged[key] = "foreign"
            reject("reject-forged-shape-reference-guard-" + key, lambda forged=forged: validate_reference_guard(forged))
        for key in ("base64", "bytes", "sha256", "complete"):
            forged = dict(first_process["stdout"])
            if key == "base64":
                forged[key] = "e30="
            elif key == "bytes":
                forged[key] += 1
            elif key == "sha256":
                forged[key] = hashlib.sha256(b"foreign").hexdigest()
            else:
                forged[key] = False
            reject("reject-incomplete-genuine-shape-worker-" + key, lambda forged=forged: decode_stream(forged, "forged"))
        for title, forged in (
            ("duplicate-fields", b'{"role":"a","role":"b"}\n'),
            ("nonfinite", b'{"value":NaN}\n'),
            ("truncated", b'{"role":"a"'),
            ("hidden-suffix", b'{}\n{}\n'),
            ("noncanonical", b'{ "role": "a" }\n'),
        ):
            reject("reject-" + title + "-shape-worker-json", lambda forged=forged: decode_canonical(forged, title))

        for title, action in (
            (
                "matcher-invocation",
                lambda: synthetic_engine.compile("synthetic-shape"),
            ),
            ("file-read", lambda: builtins.open("synthetic-shape")),
            ("descriptor-read", lambda: os.open("synthetic-shape", os.O_RDONLY)),
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
            ("operating-system-randomness", lambda: os.urandom(8)),
            ("garbage-collection", lambda: gc.collect()),
        ):
            reject("block-real-" + title, action)
        accept("exercise-all-source-only-side-effect-denials", all(value > 0 for value in boundary.blocked.values()))
        accept(
            "load-zero-candidates-or-external-matchers",
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
        "published_seed_decimal": str(PUBLISHED_SEED),
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "historical_v1_status": HISTORICAL_V1_STATUS,
        "historical_v1_oracle_relative": HISTORICAL_V1_ORACLE_RELATIVE,
        "historical_v1_oracle_sha256": HISTORICAL_V1_ORACLE_SHA256,
        "historical_v1_recorder_relative": HISTORICAL_V1_RECORDER_RELATIVE,
        "historical_v1_recorder_sha256": HISTORICAL_V1_RECORDER_SHA256,
        "historical_v1_pinned_file_count": len(
            HISTORICAL_V1_PINNED_FILES,
        ),
        "historical_v1_reference_records_sha256": (
            HISTORICAL_V1_REFERENCE_RECORDS_SHA256
        ),
        "historical_v1_c_candidate_records_sha256": (
            HISTORICAL_V1_C_CANDIDATE_RECORDS_SHA256
        ),
        "historical_v1_c_mismatch_ledger_sha256": (
            HISTORICAL_V1_C_MISMATCH_LEDGER_SHA256
        ),
        "historical_v1_failure_counts": dict(
            HISTORICAL_V1_FAILURE_COUNTS,
        ),
        "historical_v1_oracle_artifact_counts": dict(
            HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS,
        ),
        "historical_v1_real_failure_counts": dict(
            HISTORICAL_V1_REAL_FAILURE_COUNTS,
        ),
        "source_only_callback_topology_pairs": (
            callback_topology_checks
        ),
        "actual_matcher_invocations": 0,
        "witnessed_regression_outer_size": WITNESSED_REGRESSION_OUTER_SIZE,
        "witnessed_regression_nested_sizes": list(
            WITNESSED_REGRESSION_NESTED_SIZES
        ),
        "witnessed_regression_cohort_count": len(
            WITNESSED_REGRESSION_NESTED_SHAPES
        ),
        "witnessed_regression_case_count": (
            len(WITNESSED_REGRESSION_NESTED_SHAPES)
            * VARIANTS_PER_COHORT
        ),
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
        description="Freeze exhaustive legal independently shape-changing buffer semantics",
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
                "source-only shape controls cannot pin or run a genuine reference",
            )
            result = source_self_test()
        else:
            verify_runtime()
            checked_digest(options.oracle_source_sha256, "explicitly frozen shape oracle source")
            checked_digest(options.matrix_sha256, "explicitly frozen shape matrix")
            require(options.matrix_sha256 == MATRIX_SHA256, "the exact frozen shape matrix changed")
            if options.internal_reference_worker:
                require(options.role in {"reference_a", "reference_b"}, "a genuine reference role is mandatory")
                result = observe_reference_worker(options.role, options.oracle_source_sha256)
            else:
                require(options.baseline and options.role is None, "only explicit two-reference shape observation is permitted")
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
    except (ShapeOracleError, OSError, TypeError, ValueError) as error:
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
