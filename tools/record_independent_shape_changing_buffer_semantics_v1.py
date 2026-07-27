#!/usr/bin/env python3
"""Durably preserve every frozen changing-buffer observation and failure.

An explicitly pinned baseline starts exactly one isolated oracle controller
and requires two independently identified stable-CPython reference workers.
An explicitly pinned candidate starts exactly one independently owned Rust,
C, or Zig worker under the immutable V3 ownership audit and continuous V5
anti-delegation guard. Every one of the 10,240 cases, complete nested buffer
events, callbacks, errors, process streams, and actual mismatches is retained
in a lossless, no-overwrite, deterministic compressed report and receipt.

Source-only controls cannot read a file, load an engine, start a worker, write
evidence, read a holdout, or measure performance. A successful publication is
never presented as a passing baseline or candidate.
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
from collections.abc import Callable, Iterator, Mapping
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/record_independent_shape_changing_buffer_semantics_v1.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-shape-changing-buffer-semantics-recorder-v1"
ORACLE_RELATIVE = "tools/independent_shape_changing_buffer_semantics_v1.py"
ORACLE_MODULE = "tools.independent_shape_changing_buffer_semantics_v1"
ORACLE_SCHEMA = "rebar-independent-shape-changing-buffer-semantics-v1"
ORACLE_SHA256 = (
    "866dbf7bf4a48a867b3aaacd05cfa4f1346c747931543fa386835e783f0073aa"
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
MATRIX_SHA256 = (
    "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8"
)
PUBLISHED_SEED = 0x5348_4150_4542_4632
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
IMMUTABLE_V3_POLICY_SHA256 = types.MappingProxyType({
    "tools/independent_from_scratch_audit_v2.py": (
        "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
    ),
    V5_RELATIVE: V5_SHA256,
})
TRUSTED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
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
COHORTS = tuple(
    "outer-" + outer + "-nested-" + nested
    for outer in SHAPE_NAMES
    for nested in SHAPE_NAMES
)
APIS = (
    "module.sub", "module.subn", "pattern.sub", "pattern.subn",
    "match.expand",
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
PATTERN_KINDS = (
    "captures", "zero-lookahead", "empty", "optional-captures",
)
TEMPLATE_STYLES = ("literal", "named", "numeric", "invalid", "missing")
FLAGS = (0, 2, 256, 258)
COUNTS = (0, 1, 2, 7)
WINDOW_STARTS = (-4, -1, 0, 1, 2, 3, 5, 8, 13, 19, 32, 2_147_483_647)
WINDOW_ENDS = (0, 1, 2, 3, 5, 8, 13, 19, 32, None, 2_147_483_647)
WITNESSED_REGRESSION_OUTER_SHAPE = "thirteen"
WITNESSED_REGRESSION_OUTER_SIZE = 13
WITNESSED_REGRESSION_NESTED_SHAPES = (
    "zero", "one", "two", "five", "equal",
)
WITNESSED_REGRESSION_NESTED_SIZES = (0, 1, 2, 5, 8)
VARIANTS_PER_COHORT = 160
CASE_COUNT = 10_240
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 512 * 1024 * 1024
MAX_MATRIX_BYTES = 64 * 1024 * 1024
MAX_REPORT_METADATA_BYTES = 64 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
MAX_ARCHIVE_BYTES = (
    MAX_UNCOMPRESSED_BYTES
    + (MAX_UNCOMPRESSED_BYTES // 512)
    + 1_048_576
)
PROCESS_TIMEOUT_SECONDS = 1_800
ACTUAL_PROCESS_CONTEXTS: list[dict[str, Any]] = []
ACTUAL_VALIDATED_REFERENCE_WORKERS = 0
GUARD_TRUE_FIELDS = (
    "original_matchers_blocked",
    "adapter_import_quarantined",
    "native_sre_blocked",
    "builtins_import_guarded",
    "importlib_import_guarded",
    "actual_object_identity_guarded",
    "warning_registry_introspection_safe",
    "warning_registry_exactly_absent",
    "cross_family_imports_blocked",
    "external_regex_imports_blocked",
)
GUARD_COUNTER_FIELDS = (
    "cached_original_matcher_descendant_count",
    "cached_original_holder_count",
    "owned_ctypes_load_count",
    "owned_ctypes_symbol_count",
)


class RecorderError(Exception):
    """A frozen case, genuine worker, owner, or durable report was changed."""


class SourceOnlyError(RecorderError):
    """A source-only control attempted a real external side effect."""


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
        "rust",
        "candidates.rust_candidate",
        "candidates/rust_candidate.py",
        "candidates/_rust_engine.so",
        "candidates._rust_bridge",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        False,
        (
            "candidates/rust_candidate.py",
            "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml",
            "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs",
            "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs",
            "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
    ),
    "c": FamilySpec(
        "c",
        "candidates.vm_candidate",
        "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates._vm_native",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        False,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    ),
    "zig": FamilySpec(
        "zig",
        "candidates.zig_candidate",
        "candidates/zig_candidate.py",
        "candidates/_zig_probe.so",
        "candidates._zig_bridge",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        True,
        (
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
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
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise RecorderError("complete changing-buffer evidence is not canonical") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def base64_byte_bound(value: Any) -> int:
    require(
        type(value) is int and 0 <= value <= MAX_PROCESS_BYTES,
        "an exact complete process-stream byte bound is mandatory",
    )
    return 4 * ((value + 2) // 3)


def report_size_upper_bound(
    kind: str,
    stdout_bytes: int,
    stderr_bytes: int,
) -> int:
    require(
        kind in {"baseline", "candidate"}
        and type(stdout_bytes) is int
        and type(stderr_bytes) is int
        and stdout_bytes >= 0
        and stderr_bytes >= 0
        and stdout_bytes + stderr_bytes <= MAX_PROCESS_BYTES,
        "the exact complete combined worker-stream budget was exceeded",
    )
    total = (
        base64_byte_bound(stdout_bytes)
        + base64_byte_bound(stderr_bytes)
        + MAX_REPORT_METADATA_BYTES
    )
    if kind == "candidate":
        total += 2 * MAX_PROCESS_BYTES + MAX_MATRIX_BYTES
    require(
        total <= MAX_UNCOMPRESSED_BYTES,
        "lossless full-scale changing-buffer evidence exceeds its proved bound",
    )
    return total


def validate_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value),
        "an exact independently frozen SHA-256 is mandatory: " + label,
    )
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for name, item in items:
        require(
            type(name) is str and name not in value,
            "duplicate JSON fields conceal a changing-buffer result",
        )
        value[name] = item
    return value


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_UNCOMPRESSED_BYTES,
        "complete bounded changing-buffer evidence is mandatory: " + label,
    )

    def reject_constant(_: str) -> Any:
        raise RecorderError("nonfinite changing-buffer evidence is forbidden")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (
        RecorderError,
        TypeError,
        ValueError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        raise RecorderError(
            "a complete changing-buffer document is invalid: " + label
        ) from error
    require(
        type(value) is dict and canonical(value) == raw,
        "a changing-buffer document was truncated, reordered, or substituted",
    )
    return value


def validate_label(value: Any) -> str:
    require(
        type(value) is str
        and 1 <= len(value) <= 64
        and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-" for item in value)
        and "--" not in value,
        "an exact bounded lowercase nonescaping run label is mandatory",
    )
    return value


def safe_parts(value: Any) -> tuple[str, ...]:
    require(
        type(value) is str
        and bool(value)
        and "\\" not in value
        and "\x00" not in value,
        "an exact project-relative no-follow owner is mandatory",
    )
    parts = tuple(value.split("/"))
    require(
        all(part not in {"", ".", ".."} for part in parts)
        and "/".join(parts) == value,
        "an owned source or publication escaped the approved project",
    )
    return parts


def family_spec(value: Any) -> FamilySpec:
    require(
        type(value) is str and value in FAMILIES,
        "select exactly one independently owned Rust, C, or Zig engine",
    )
    spec = FAMILIES[value]
    require(
        isinstance(spec, FamilySpec)
        and spec.name == value
        and spec.adapter_module.startswith("candidates.")
        and spec.bridge_module.startswith("candidates.")
        and spec.adapter_module != spec.bridge_module
        and spec.owned_ctypes is (value == "zig")
        and (spec.engine_relative == spec.bridge_relative) is (value == "c")
        and len(set(spec.owned_source_relatives))
        == len(spec.owned_source_relatives)
        and spec.adapter_relative in spec.owned_source_relatives
        and all(
            safe_parts(relative)[0] == "candidates"
            for relative in spec.owned_source_relatives
        ),
        "a sibling, external, partial, or aliased regex family was selected",
    )
    return spec


def parse_owned_source(value: Any) -> tuple[str, str]:
    require(
        type(value) is str and value.count("=") == 1,
        "pin every exact owned source as relative/path=sha256",
    )
    relative, expected = value.split("=", 1)
    require(
        safe_parts(relative)[0] == "candidates",
        "an independently owned source escaped its native family",
    )
    return relative, validate_digest(expected, relative)


def make_baseline_pins(
    label: Any,
    receipt: Any,
    archive: Any,
    records: Any,
) -> BaselinePins:
    return BaselinePins(
        validate_label(label),
        validate_digest(receipt, "published two-reference shape receipt"),
        validate_digest(archive, "complete compressed shape baseline"),
        validate_digest(records, "all 10,240 original shape observations"),
    )


def make_owner_pins(
    family: Any,
    recorder: Any,
    adapter: Any,
    engine: Any,
    bridge: Any,
    sources: Any,
    baseline: BaselinePins,
) -> OwnerPins:
    spec = family_spec(family)
    require(
        isinstance(baseline, BaselinePins),
        "an independently published passing two-reference baseline is mandatory",
    )
    validate_digest(recorder, "frozen changing-buffer recorder")
    validate_digest(adapter, "independently owned candidate adapter")
    validate_digest(engine, "independently owned native engine")
    validate_digest(bridge, "independently owned native Python bridge")
    require(
        type(sources) is list,
        "explicitly pin the complete candidate source and lockfile closure",
    )
    parsed = tuple(parse_owned_source(item) for item in sources)
    require(
        len(parsed) == len(spec.owned_source_relatives)
        and len({relative for relative, _ in parsed}) == len(parsed)
        and {relative for relative, _ in parsed}
        == set(spec.owned_source_relatives),
        "a native parser, compiler, executor, bridge, or lockfile was omitted",
    )
    mapped = dict(parsed)
    require(
        mapped[spec.adapter_relative] == adapter,
        "the public candidate adapter escaped its independently pinned closure",
    )
    require(
        (engine == bridge) is (spec.name == "c"),
        "only the genuinely combined C engine and bridge may alias",
    )
    return OwnerPins(
        spec.name,
        recorder,
        adapter,
        engine,
        bridge,
        tuple(
            (relative, mapped[relative])
            for relative in spec.owned_source_relatives
        ),
        baseline,
    )


def exact_hex(value: Any, label: str) -> str:
    require(type(value) is str, "an exact byte payload is mandatory: " + label)
    try:
        actual = bytes.fromhex(value)
    except ValueError as error:
        raise RecorderError("an exact byte payload was forged: " + label) from error
    require(
        actual.hex() == value,
        "a changing-buffer byte payload is not canonical: " + label,
    )
    return value


def shaped_bytes(base: bytes, size: int, suffix: bytes) -> bytes:
    require(
        type(base) is bytes
        and bool(base)
        and type(size) is int
        and size >= 0
        and type(suffix) is bytes,
        "an exact independently shaped visible payload is mandatory",
    )
    if not size:
        return b""
    material = base + suffix
    while len(material) < size:
        material += base
    return material[:size]


def bytes_descriptor(payload: bytes) -> dict[str, Any]:
    require(type(payload) is bytes, "a genuine bytes control is mandatory")
    return {"kind": "bytes", "hex": payload.hex()}


def callable_descriptor(payload: bytes, *, raises: bool) -> dict[str, Any]:
    require(
        type(payload) is bytes and type(raises) is bool,
        "a frozen returning or failing replacement callback is mandatory",
    )
    return {"kind": "callable", "hex": payload.hex(), "raises": raises}


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
        "a frozen independently shaped PEP-688 exporter was forged",
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


def validate_carrier(value: Any, *, role: str) -> dict[str, Any]:
    require(
        role in {"subject", "template"} and type(value) is dict,
        "a complete frozen replacement carrier is mandatory",
    )
    if value.get("kind") == "bytes":
        require(set(value) == {"kind", "hex"}, "a bytes carrier was changed")
        exact_hex(value["hex"], role)
        return value
    if value.get("kind") == "callable":
        require(
            role == "template"
            and set(value) == {"kind", "hex", "raises"}
            and type(value.get("raises")) is bool,
            "a genuine returning or failing callback was substituted",
        )
        exact_hex(value["hex"], "replacement callback")
        return value
    require(
        set(value) == {
            "kind",
            "role",
            "outer_shape",
            "nested_shape",
            "outer_size",
            "nested_size",
            "outer_hex",
            "nested_hex",
            "behavior",
            "wrapped",
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
        "an independently sized subject or template exporter was forged",
    )
    outer = bytes.fromhex(exact_hex(value["outer_hex"], "outer backing"))
    nested = bytes.fromhex(exact_hex(value["nested_hex"], "nested backing"))
    require(
        len(outer) == value["outer_size"]
        and len(nested) == value["nested_size"],
        "the original outer or visible nested backing size was substituted",
    )
    return value


def build_frozen_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(
        type(seed) is int and seed == PUBLISHED_SEED and 0 <= seed < 1 << 64,
        "the exact independently published full-precision seed is mandatory",
    )
    seeded = random.Random(seed)
    matrix: list[dict[str, Any]] = []
    for outer_shape in SHAPE_NAMES:
        for nested_shape in SHAPE_NAMES:
            cohort = "outer-" + outer_shape + "-nested-" + nested_shape
            for variant in range(VARIANTS_PER_COHORT):
                noise = "".join(
                    seeded.choice("abcdef0123456789") for _ in range(12)
                ).encode("ascii")
                api = APIS[variant % len(APIS)]
                target = TARGETS[(variant // len(APIS)) % len(TARGETS)]
                behavior = BEHAVIORS[
                    (variant // (len(APIS) * len(TARGETS))) % len(BEHAVIORS)
                ]
                outer_subject = shaped_bytes(
                    b"OUTERalpha42", SHAPE_SIZES[outer_shape], noise,
                )
                nested_subject = shaped_bytes(
                    b"aa12bb34cc56dd78xyz", SHAPE_SIZES[nested_shape], noise,
                )
                outer_template = shaped_bytes(
                    b"OUTER-template", SHAPE_SIZES[outer_shape], noise,
                )
                nested_template = shaped_bytes(
                    rb"<\g<word>:\g<number>>",
                    SHAPE_SIZES[nested_shape],
                    noise,
                )
                wrapped = target.endswith("-wrapped")
                subject = bytes_descriptor(nested_subject)
                template = bytes_descriptor(b"X")
                if (
                    target.startswith("subject-")
                    or target.startswith("both-")
                    or target.startswith("callback-")
                ):
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
                    "zero-lookahead": (
                        rb"(?=(?P<word>[a-z]*)(?P<number>[0-9]*))"
                    ),
                    "empty": rb"(?P<word>)(?P<number>)",
                    "optional-captures": (
                        rb"(?P<word>[a-z]+)?(?P<number>[0-9]+)?"
                    ),
                }[pattern_kind]
                template_style = TEMPLATE_STYLES[
                    (variant // len(PATTERN_KINDS)) % len(TEMPLATE_STYLES)
                ]
                if template["kind"] == "bytes":
                    template = bytes_descriptor({
                        "literal": b"X",
                        "named": rb"<\g<word>:\g<number>>",
                        "numeric": rb"<\1:\2>",
                        "invalid": rb"\q",
                        "missing": rb"\g<absent>",
                    }[template_style])
                matrix.append({
                    "case": (
                        "shape-changing-buffer-semantics.v1."
                        + format(len(matrix), "05d")
                    ),
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
                    "endpos": WINDOW_ENDS[
                        (variant // len(WINDOW_STARTS)) % len(WINDOW_ENDS)
                    ],
                    "pattern_hex": pattern.hex(),
                    "subject": subject,
                    "template": template,
                })
    return matrix


def validate_matrix(value: Any) -> list[dict[str, Any]]:
    require(
        tuple(SHAPE_SIZES) == SHAPE_NAMES
        and tuple(SHAPE_SIZES.values()) == (0, 1, 2, 3, 5, 8, 13, 19)
        and len(COHORTS) == 64
        and len(set(COHORTS)) == 64
        and len(APIS) == 5
        and len(TARGETS) == 8
        and len(BEHAVIORS) == 4
        and VARIANTS_PER_COHORT
        == len(APIS) * len(TARGETS) * len(BEHAVIORS)
        == 160
        and CASE_COUNT == len(COHORTS) * VARIANTS_PER_COHORT == 10_240
        and WITNESSED_REGRESSION_OUTER_SHAPE == "thirteen"
        and SHAPE_SIZES[WITNESSED_REGRESSION_OUTER_SHAPE]
        == WITNESSED_REGRESSION_OUTER_SIZE
        == 13
        and tuple(
            SHAPE_SIZES[item] for item in WITNESSED_REGRESSION_NESTED_SHAPES
        ) == WITNESSED_REGRESSION_NESTED_SIZES
        == (0, 1, 2, 5, 8),
        "an original independent shape or witnessed regression was omitted",
    )
    require(
        type(value) is list and len(value) == CASE_COUNT,
        "all 10,240 frozen original changing-buffer cases are mandatory",
    )
    seen: set[str] = set()
    observed: dict[str, set[tuple[str, str, str]]] = {
        cohort: set() for cohort in COHORTS
    }
    expected = {
        (api, target, behavior)
        for api in APIS
        for target in TARGETS
        for behavior in BEHAVIORS
    }
    for index, case in enumerate(value):
        require(
            type(case) is dict
            and set(case) == {
                "case",
                "cohort",
                "variant",
                "seed",
                "outer_shape",
                "nested_shape",
                "outer_size",
                "nested_size",
                "api",
                "target",
                "behavior",
                "pattern_kind",
                "template_style",
                "flags",
                "count",
                "pos",
                "endpos",
                "pattern_hex",
                "subject",
                "template",
            }
            and case.get("case")
            == "shape-changing-buffer-semantics.v1." + format(index, "05d")
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
            and (
                case.get("endpos") is None
                or type(case.get("endpos")) is int
            )
            and case["endpos"] in WINDOW_ENDS,
            "a complete frozen shape, API, failure, or offset case was forged",
        )
        exact_hex(case["pattern_hex"], "frozen pattern")
        for role in ("subject", "template"):
            carrier = validate_carrier(case[role], role=role)
            if carrier["kind"] == "shape-exporter":
                require(
                    carrier["outer_shape"] == case["outer_shape"]
                    and carrier["nested_shape"] == case["nested_shape"]
                    and carrier["outer_size"] == case["outer_size"]
                    and carrier["nested_size"] == case["nested_size"]
                    and carrier["behavior"] == case["behavior"],
                    "an independently owned nested backing was changed",
                )
        variant = (case["api"], case["target"], case["behavior"])
        require(
            variant not in observed[case["cohort"]],
            "an original shape API, placement, or behavior was duplicated",
        )
        observed[case["cohort"]].add(variant)
        seen.add(case["case"])
    require(
        all(variants == expected for variants in observed.values())
        and len(canonical(value)) <= MAX_MATRIX_BYTES
        and digest(value) == MATRIX_SHA256,
        "the complete 64-by-160 frozen shape matrix was silently reweighted",
    )
    return value


def directory_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def regular_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


@contextlib.contextmanager
def open_owned_descriptor(
    relative: str,
) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_parts(relative)
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        require(
            stat.S_ISDIR(os.fstat(current).st_mode),
            "the exact frozen project root was replaced",
        )
        for part in parts[:-1]:
            current = os.open(part, directory_flags(), dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "an independently owned parent became a symlink",
            )
        current = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(current)
        before = os.fstat(current)
        named = os.stat(
            parts[-1],
            dir_fd=opened[-2],
            follow_symlinks=False,
        )
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (before.st_dev, before.st_ino)
            == (named.st_dev, named.st_ino),
            "an exact frozen source or lossless archive was replaced",
        )
        yield current, before
        after = os.fstat(current)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "an independently owned file changed during authentication",
        )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_owned_regular(
    relative: str,
    expected: str,
    maximum: int,
    *,
    retain: bool = False,
) -> tuple[dict[str, Any], bytes | None]:
    validate_digest(expected, relative)
    require(
        type(maximum) is int
        and 0 < maximum <= max(
            MAX_UNCOMPRESSED_BYTES,
            MAX_ARCHIVE_BYTES,
        ),
        "an exact safe source, native, or complete archive bound is mandatory",
    )
    with open_owned_descriptor(relative) as (descriptor, before):
        require(
            0 < before.st_size <= maximum,
            "a complete pinned source or archive exceeds its safe bound",
        )
        remaining = before.st_size
        hasher = hashlib.sha256()
        parts: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(
                type(block) is bytes and bool(block),
                "a frozen complete source or archive was truncated",
            )
            hasher.update(block)
            if retain:
                parts.append(block)
            remaining -= len(block)
        require(
            os.read(descriptor, 1) == b""
            and hasher.hexdigest() == expected,
            "a pinned complete source or archive was substituted",
        )
        owner = {
            "relative": relative,
            "sha256": expected,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
        return owner, b"".join(parts) if retain else None


def read_pinned_external(
    absolute: str,
    expected: str,
    maximum: int,
) -> dict[str, Any]:
    validate_digest(expected, absolute)
    require(
        type(absolute) is str
        and os.path.isabs(absolute)
        and os.path.abspath(absolute) == absolute
        and os.path.realpath(absolute) == absolute
        and type(maximum) is int
        and 0 < maximum <= MAX_BINARY_BYTES,
        "an actual no-follow pinned stable CPython file is mandatory",
    )
    descriptor = os.open(absolute, regular_flags())
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
            "a pinned stable executable is not a bounded regular file",
        )
        remaining = before.st_size
        hasher = hashlib.sha256()
        while remaining:
            raw = os.read(descriptor, min(remaining, 1_048_576))
            require(bool(raw), "the pinned stable executable was truncated")
            hasher.update(raw)
            remaining -= len(raw)
        after = os.fstat(descriptor)
        require(
            os.read(descriptor, 1) == b""
            and (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and hasher.hexdigest() == expected,
            "the exact stable CPython executable was substituted",
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


def validate_owner(
    value: Any,
    relative: str,
    expected: str,
) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {
            "relative", "sha256", "bytes", "device", "inode",
        }
        and value.get("relative") == relative
        and value.get("sha256") == expected
        and type(value.get("bytes")) is int
        and value["bytes"] > 0
        and type(value.get("device")) is int
        and value["device"] >= 0
        and type(value.get("inode")) is int
        and value["inode"] > 0,
        "an exact immutable project source or evidence owner was forged",
    )
    return value


def validate_external_owner(
    value: Any,
    absolute: str,
    expected: str,
) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {"path", "sha256", "bytes", "device", "inode"}
        and value.get("path") == absolute
        and value.get("sha256") == expected
        and type(value.get("bytes")) is int
        and value["bytes"] > 0
        and type(value.get("device")) is int
        and value["device"] >= 0
        and type(value.get("inode")) is int
        and value["inode"] > 0,
        "an exact pinned external CPython owner was forged",
    )
    return value


def verify_runtime(
    *,
    candidate_loaded: bool = False,
    synthetic: bool = False,
) -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path)
        and sys.path[0] == ROOT
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == SOURCE_ABSOLUTE,
        "use only the exact isolated stable CPython and changing-buffer recorder",
    )
    if not synthetic:
        require(
            os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
            "the frozen executable or recorder was replaced by a symlink",
        )
    if not candidate_loaded:
        require(
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
            "an independently owned candidate escaped into the reference",
        )


def authenticate_module(
    module_name: str,
    relative: str,
    expected: str,
) -> tuple[types.ModuleType, dict[str, Any]]:
    before, _ = read_owned_regular(relative, expected, MAX_SOURCE_BYTES)
    module = importlib.import_module(module_name)
    absolute = ROOT + "/" + relative
    module_spec = getattr(module, "__spec__", None)
    loader = getattr(module_spec, "loader", None)
    require(
        type(module) is types.ModuleType
        and module.__name__ == module_name
        and getattr(module, "__file__", None) == absolute
        and os.path.realpath(absolute) == absolute
        and module_spec is not None
        and getattr(module_spec, "name", None) == module_name
        and getattr(module_spec, "origin", None) == absolute
        and isinstance(loader, importlib.machinery.SourceFileLoader)
        and getattr(loader, "name", None) == module_name
        and getattr(loader, "path", None) == absolute,
        "an independently frozen source module or loader was substituted",
    )
    after, _ = read_owned_regular(relative, expected, MAX_SOURCE_BYTES)
    require(
        before == after,
        "a pinned frozen source changed while being imported",
    )
    return module, before


def authenticate_frozen_tools(
    recorder_pin: str,
) -> tuple[
    Any,
    Any,
    Any,
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    verify_runtime()
    recorder_owner, _ = read_owned_regular(
        SOURCE_RELATIVE, recorder_pin, MAX_SOURCE_BYTES,
    )
    python_owner = read_pinned_external(
        PINNED_PYTHON,
        PINNED_PYTHON_SHA256,
        MAX_BINARY_BYTES,
    )
    oracle, oracle_owner = authenticate_module(
        ORACLE_MODULE, ORACLE_RELATIVE, ORACLE_SHA256,
    )
    v5, v5_owner = authenticate_module(
        V5_MODULE, V5_RELATIVE, V5_SHA256,
    )
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
        and dict(getattr(oracle, "SHAPE_SIZES", {})) == dict(SHAPE_SIZES)
        and getattr(oracle, "WITNESSED_REGRESSION_OUTER_SIZE", None)
        == WITNESSED_REGRESSION_OUTER_SIZE
        and tuple(
            getattr(oracle, "WITNESSED_REGRESSION_NESTED_SIZES", ())
        ) == WITNESSED_REGRESSION_NESTED_SIZES
        and getattr(oracle, "V5_GUARD_SHA256", None) == V5_SHA256
        and getattr(oracle, "OWNERSHIP_AUDIT_SHA256", None) == AUDIT_SHA256
        and getattr(v5, "SOURCE_RELATIVE", None) == V5_RELATIVE
        and v5.current_source_sha256() == V5_SHA256
        and getattr(audit, "SOURCE_RELATIVE", None) == AUDIT_RELATIVE,
        "the frozen changing-buffer oracle or V3/V5 ownership policy changed",
    )
    matrix = validate_matrix(build_frozen_matrix())
    try:
        require(
            oracle.build_matrix() == matrix
            and oracle.validate_matrix(matrix, MATRIX_SHA256) == MATRIX_SHA256,
            "the original 10,240-case independently frozen matrix changed",
        )
    except Exception as error:
        if isinstance(error, RecorderError):
            raise
        raise RecorderError(
            "the immutable shape oracle rejected its complete frozen matrix",
        ) from error
    return oracle, v5, audit, matrix, {
        "recorder": recorder_owner,
        "shape_oracle": oracle_owner,
        "original_v5": v5_owner,
        "from_scratch_audit_v3": audit_owner,
        "pinned_python": python_owner,
    }


def validate_frozen_source_closure(
    value: Any,
    recorder_pin: str,
) -> dict[str, dict[str, Any]]:
    require(
        type(value) is dict
        and set(value) == {
            "recorder",
            "shape_oracle",
            "original_v5",
            "from_scratch_audit_v3",
            "pinned_python",
        },
        "the complete immutable recorder, oracle, guard, and Python closure is mandatory",
    )
    for name, relative, expected in (
        ("recorder", SOURCE_RELATIVE, recorder_pin),
        ("shape_oracle", ORACLE_RELATIVE, ORACLE_SHA256),
        ("original_v5", V5_RELATIVE, V5_SHA256),
        ("from_scratch_audit_v3", AUDIT_RELATIVE, AUDIT_SHA256),
    ):
        validate_owner(value.get(name), relative, expected)
    validate_external_owner(
        value.get("pinned_python"),
        PINNED_PYTHON,
        PINNED_PYTHON_SHA256,
    )
    return value


def approved_paths(
    kind: str,
    label: str,
    family: str | None = None,
) -> tuple[str, str]:
    validate_label(label)
    require(
        kind in {"baseline", "candidate"},
        "select only one complete reference or candidate evidence class",
    )
    if kind == "baseline":
        require(family is None, "a standard baseline cannot select an engine")
        slug = "shape-changing-buffer-semantics-v1-" + label
    else:
        spec = family_spec(family)
        slug = spec.name + "-shape-changing-buffer-semantics-v1-" + label
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json.gz",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


def require_directory_identity(a: Any, b: Any, c: Any) -> None:
    require(
        type(a) is tuple
        and type(b) is tuple
        and type(c) is tuple
        and len(a) == len(b) == len(c) == 2
        and all(
            type(item) is int and item >= 0
            for identity in (a, b, c)
            for item in identity
        )
        and a == b == c,
        "the exact retained approved evidence directory was replaced",
    )


def verify_retained_directory(value: Mapping[str, Any]) -> int:
    descriptor = value.get("directory_descriptor")
    require(
        type(descriptor) is int and descriptor >= 0,
        "retain exactly one approved no-follow evidence directory",
    )
    retained = os.fstat(descriptor)
    require(
        stat.S_ISDIR(retained.st_mode),
        "the retained approved publication directory was replaced",
    )
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "the approved changing-buffer evidence path became a symlink",
            )
        current_owner = os.fstat(current)
        require_directory_identity(
            (retained.st_dev, retained.st_ino),
            (value.get("directory_device"), value.get("directory_inode")),
            (current_owner.st_dev, current_owner.st_ino),
        )
    finally:
        for current in reversed(opened):
            os.close(current)
    return descriptor


@contextlib.contextmanager
def preflight_fresh_outputs(
    kind: str,
    label: str,
    family: str | None = None,
) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(kind, label, family)
    report_parts = safe_parts(report)
    receipt_parts = safe_parts(receipt)
    require(
        report_parts[:-1]
        == receipt_parts[:-1]
        == ("experiments", "rust_public_practice_v1")
        and report_parts[-1] != receipt_parts[-1],
        "select exactly one distinct complete archive and durable receipt",
    )
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        for part in report_parts[:-1]:
            current = os.open(part, directory_flags(), dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact approved evidence parent became a symlink",
            )
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError(
                "refusing to overwrite frozen changing-buffer evidence: "
                + basename
            )
        actual = os.fstat(current)
        result = {
            "report_relative": report,
            "receipt_relative": receipt,
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
        for descriptor in reversed(opened):
            os.close(descriptor)


def iter_canonical(value: Mapping[str, Any]) -> Iterator[bytes]:
    encoder = json.JSONEncoder(
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    try:
        for part in encoder.iterencode(dict(value)):
            require(
                type(part) is str,
                "a complete changing-buffer encoder produced invalid data",
            )
            yield part.encode("ascii")
        yield b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise RecorderError(
            "complete changing-buffer evidence is not canonical JSON",
        ) from error


def readback_archive(
    preflight: Mapping[str, Any],
    basename: str,
    expected_archive: str,
    expected_plain: str,
    archive_bytes: int,
    plain_bytes: int,
) -> None:
    validate_digest(expected_archive, "published complete shape archive")
    validate_digest(expected_plain, "published complete shape observations")
    directory = verify_retained_directory(preflight)
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        owner = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(
            stat.S_ISREG(owner.st_mode)
            and (owner.st_dev, owner.st_ino)
            == (named.st_dev, named.st_ino)
            and owner.st_size == archive_bytes,
            "the complete compressed changing-buffer report was replaced",
        )
        archived = hashlib.sha256()
        remaining = archive_bytes
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(
                type(block) is bytes and bool(block),
                "a complete compressed changing-buffer report was truncated",
            )
            archived.update(block)
            remaining -= len(block)
        require(
            os.read(descriptor, 1) == b""
            and archived.hexdigest() == expected_archive,
            "a published changing-buffer archive gained or lost evidence",
        )
        os.lseek(descriptor, 0, os.SEEK_SET)
        plain = hashlib.sha256()
        actual_bytes = 0
        try:
            with io.FileIO(descriptor, "rb", closefd=False) as source:
                with gzip.GzipFile(fileobj=source, mode="rb") as archive:
                    while True:
                        block = archive.read(131_072)
                        require(
                            type(block) is bytes,
                            "a lossless shape archive produced invalid bytes",
                        )
                        if not block:
                            break
                        actual_bytes += len(block)
                        require(
                            actual_bytes <= MAX_UNCOMPRESSED_BYTES,
                            "a complete shape report exceeds its safe bound",
                        )
                        plain.update(block)
        except (OSError, EOFError, gzip.BadGzipFile) as error:
            raise RecorderError(
                "a published changing-buffer archive is not lossless",
            ) from error
        require(
            actual_bytes == plain_bytes
            and plain.hexdigest() == expected_plain,
            "a lossless changing-buffer report differs from every original byte",
        )
    finally:
        os.close(descriptor)
    verify_retained_directory(preflight)


def publish_document(
    preflight: Mapping[str, Any],
    document: Mapping[str, Any],
    *,
    compressed: bool,
) -> dict[str, Any]:
    kind = "report" if compressed else "receipt"
    basename = preflight[kind + "_basename"]
    directory = verify_retained_directory(preflight)
    temporary = (
        ".rebar-shape-changing-recorder-v1-"
        + basename
        + "-"
        + str(os.getpid())
    )
    safe_parts(temporary)
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    identity: tuple[int, int] | None = None
    linked = False
    plain = hashlib.sha256()
    plain_bytes = 0
    write_calls = 0
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode),
            "a fresh shape-evidence temporary is not regular",
        )
        identity = (before.st_dev, before.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require(
            (named.st_dev, named.st_ino) == identity,
            "a fresh changing-buffer temporary was substituted",
        )
        if compressed:
            with io.FileIO(descriptor, "wb", closefd=False) as output:
                with gzip.GzipFile(
                    filename="",
                    fileobj=output,
                    mode="wb",
                    compresslevel=9,
                    mtime=0,
                ) as archive:
                    for piece in iter_canonical(document):
                        plain_bytes += len(piece)
                        require(
                            plain_bytes <= MAX_UNCOMPRESSED_BYTES,
                            "the complete shape report exceeds its safe bound",
                        )
                        plain.update(piece)
                        archive.write(piece)
                        write_calls += 1
        else:
            for piece in iter_canonical(document):
                plain_bytes += len(piece)
                require(
                    plain_bytes <= MAX_SOURCE_BYTES,
                    "a complete publication receipt exceeds its safe bound",
                )
                plain.update(piece)
                offset = 0
                while offset < len(piece):
                    actual = os.write(descriptor, piece[offset:])
                    require(
                        type(actual) is int and actual > 0,
                        "a complete changing-buffer receipt was truncated",
                    )
                    offset += actual
                    write_calls += 1
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        require(
            0 < actual.st_size <= MAX_ARCHIVE_BYTES,
            "a complete compressed shape report exceeds its safe bound",
        )
        verify_retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require(
            (named.st_dev, named.st_ino) == identity,
            "changing-buffer evidence changed before no-clobber publication",
        )
        reader = os.open(temporary, regular_flags(), dir_fd=directory)
        try:
            archive_digest = hashlib.sha256()
            remaining = actual.st_size
            while remaining:
                block = os.read(reader, min(remaining, 1_048_576))
                require(
                    type(block) is bytes and bool(block),
                    "an authenticated complete shape report was truncated",
                )
                archive_digest.update(block)
                remaining -= len(block)
            require(
                os.read(reader, 1) == b"",
                "an authenticated complete report gained a hidden suffix",
            )
        finally:
            os.close(reader)
        os.link(
            temporary,
            basename,
            src_dir_fd=directory,
            dst_dir_fd=directory,
            follow_symlinks=False,
        )
        linked = True
        os.fsync(directory)
        verify_retained_directory(preflight)
        destination = os.stat(
            basename,
            dir_fd=directory,
            follow_symlinks=False,
        )
        require(
            (destination.st_dev, destination.st_ino) == identity,
            "an atomically published changing-buffer report was substituted",
        )
        named = os.stat(
            temporary,
            dir_fd=directory,
            follow_symlinks=False,
        )
        require(
            (named.st_dev, named.st_ino) == identity,
            "refusing to remove a substituted publication temporary",
        )
        os.unlink(temporary, dir_fd=directory)
        os.fsync(directory)
    except BaseException:
        if not linked and identity is not None:
            try:
                named = os.stat(
                    temporary,
                    dir_fd=directory,
                    follow_symlinks=False,
                )
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
        "sha256": archive_digest.hexdigest(),
        "uncompressed_bytes": plain_bytes,
        "uncompressed_sha256": plain.hexdigest(),
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
            preflight,
            basename,
            result["sha256"],
            result["uncompressed_sha256"],
            result["bytes"],
            result["uncompressed_bytes"],
        )
    else:
        require(
            result["bytes"] == result["uncompressed_bytes"]
            and result["sha256"] == result["uncompressed_sha256"],
            "a complete changing-buffer receipt was compressed or changed",
        )
        directory = verify_retained_directory(preflight)
        reader = os.open(basename, regular_flags(), dir_fd=directory)
        try:
            parts: list[bytes] = []
            remaining = result["bytes"]
            while remaining:
                block = os.read(reader, min(remaining, 1_048_576))
                require(bool(block), "a durable complete receipt was truncated")
                parts.append(block)
                remaining -= len(block)
            require(
                os.read(reader, 1) == b""
                and b"".join(parts) == canonical(dict(document)),
                "a durable changing-buffer receipt differs from its source",
            )
        finally:
            os.close(reader)
    verify_retained_directory(preflight)
    return result


def capture_stream(value: Any, label: str) -> dict[str, Any]:
    require(
        type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
        "retain complete bounded isolated worker bytes: " + label,
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
        and value.get("complete") is True,
        "a complete shape worker process stream was concealed: " + label,
    )
    validate_digest(value.get("sha256"), label)
    try:
        raw = base64.b64decode(
            value["base64"].encode("ascii"),
            validate=True,
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise RecorderError(
            "a complete changing-buffer process stream is invalid: " + label,
        ) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == value["sha256"]
        and base64.b64encode(raw).decode("ascii") == value["base64"],
        "a genuine isolated changing-buffer stream was truncated or replaced",
    )
    return raw


def run_one_process(arguments: list[str]) -> dict[str, Any]:
    require(
        type(arguments) is list
        and bool(arguments)
        and arguments[0] == PINNED_PYTHON
        and len(arguments) >= 4
        and arguments[1:3] == ["-I", "-B"]
        and all(type(item) is str for item in arguments),
        "start only one explicitly pinned isolated stable-CPython process",
    )
    if (
        arguments[3] == ROOT + "/" + ORACLE_RELATIVE
        and "--baseline" in arguments[4:]
    ):
        role = "baseline-controller"
    elif (
        arguments[3] == SOURCE_ABSOLUTE
        and "--internal-candidate-worker" in arguments[4:]
    ):
        role = "candidate-worker"
    else:
        raise RecorderError(
            "a process escaped the pinned baseline or one-candidate worker",
        )
    try:
        process = subprocess.Popen(
            arguments,
            cwd=ROOT,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            env={
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {
            "started": False,
            "pid": None,
            "returncode": None,
            "signal": None,
            "timed_out": False,
            "spawn_error": str(error),
            "stdout": b"",
            "stderr": b"",
        }
    context: dict[str, Any] = {
        "role": role,
        "pid": process.pid,
        "returncode": None,
        "signal": None,
        "timed_out": False,
        "stdout": None,
        "stderr": None,
        "stream_capture_complete": False,
    }
    ACTUAL_PROCESS_CONTEXTS.append(context)
    timed_out = False
    try:
        stdout, stderr = process.communicate(
            timeout=PROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    context["returncode"] = process.returncode
    context["signal"] = (
        -process.returncode
        if type(process.returncode) is int and process.returncode < 0
        else None
    )
    context["timed_out"] = timed_out
    if type(stdout) is bytes:
        if len(stdout) <= MAX_PROCESS_BYTES:
            context["stdout"] = capture_stream(
                stdout,
                "actual " + role + " failure-context stdout",
            )
        else:
            context["stdout"] = {
                "base64": None,
                "bytes": len(stdout),
                "sha256": hashlib.sha256(stdout).hexdigest(),
                "complete": False,
                "failure": "complete process stream exceeded its safe bound",
            }
    if type(stderr) is bytes:
        if len(stderr) <= MAX_PROCESS_BYTES:
            context["stderr"] = capture_stream(
                stderr,
                "actual " + role + " failure-context stderr",
            )
        else:
            context["stderr"] = {
                "base64": None,
                "bytes": len(stderr),
                "sha256": hashlib.sha256(stderr).hexdigest(),
                "complete": False,
                "failure": "complete process stream exceeded its safe bound",
            }
    context["stream_capture_complete"] = (
        type(stdout) is bytes
        and type(stderr) is bytes
        and len(stdout) + len(stderr) <= MAX_PROCESS_BYTES
    )
    require(
        type(stdout) is bytes
        and type(stderr) is bytes
        and len(stdout) + len(stderr) <= MAX_PROCESS_BYTES
        and type(process.returncode) is int,
        "a genuine isolated shape process lost its complete bounded streams",
    )
    return {
        "started": True,
        "pid": process.pid,
        "returncode": process.returncode,
        "signal": (
            -process.returncode if process.returncode < 0 else None
        ),
        "timed_out": timed_out,
        "spawn_error": None,
        "stdout": stdout,
        "stderr": stderr,
    }


def canonical_identity(
    value: Mapping[str, Any],
    maximum: int,
) -> tuple[int, str]:
    require(
        type(maximum) is int
        and 0 < maximum <= MAX_UNCOMPRESSED_BYTES,
        "an exact lossless canonical-report size bound is mandatory",
    )
    hasher = hashlib.sha256()
    count = 0
    for part in iter_canonical(value):
        count += len(part)
        require(
            count <= maximum,
            "a complete canonical changing-buffer report exceeded its bound",
        )
        hasher.update(part)
    return count, hasher.hexdigest()


def build_failure_document(
    error: BaseException,
    contexts: list[dict[str, Any]],
    *,
    validated_reference_workers: int,
) -> dict[str, Any]:
    require(
        isinstance(error, BaseException)
        and type(contexts) is list
        and type(validated_reference_workers) is int
        and validated_reference_workers in {0, 2},
        "complete actual changing-buffer failure accounting is mandatory",
    )
    reference_controllers = 0
    candidate_workers = 0
    retained: list[dict[str, Any]] = []
    for context in contexts:
        require(
            type(context) is dict
            and set(context) == {
                "role",
                "pid",
                "returncode",
                "signal",
                "timed_out",
                "stdout",
                "stderr",
                "stream_capture_complete",
            }
            and context.get("role")
            in {"baseline-controller", "candidate-worker"}
            and type(context.get("pid")) is int
            and context["pid"] > 0
            and (
                context.get("returncode") is None
                or type(context.get("returncode")) is int
            )
            and (
                context.get("signal") is None
                or (
                    type(context.get("signal")) is int
                    and context["signal"] > 0
                )
            )
            and type(context.get("timed_out")) is bool
            and type(context.get("stream_capture_complete")) is bool,
            "a started genuine process or actual PID was concealed",
        )
        for name in ("stdout", "stderr"):
            stream = context[name]
            if stream is None:
                require(
                    context["stream_capture_complete"] is False,
                    "an actual incomplete process stream was hidden",
                )
            elif stream.get("complete") is True:
                decode_stream(
                    stream,
                    "complete actual " + context["role"] + " " + name,
                )
            else:
                require(
                    type(stream) is dict
                    and set(stream) == {
                        "base64", "bytes", "sha256", "complete", "failure",
                    }
                    and stream["base64"] is None
                    and type(stream["bytes"]) is int
                    and stream["bytes"] > MAX_PROCESS_BYTES
                    and validate_digest(
                        stream["sha256"],
                        "honest oversized process " + name,
                    )
                    and stream["complete"] is False
                    and type(stream["failure"]) is str,
                    "an oversized actual process stream was claimed complete",
                )
        if context["role"] == "baseline-controller":
            reference_controllers += 1
        else:
            candidate_workers += 1
        retained.append(dict(context))
    require(
        reference_controllers <= 1
        and candidate_workers <= 1
        and (reference_controllers == 0 or candidate_workers == 0)
        and (
            validated_reference_workers == 0
            or reference_controllers == 1
        ),
        "an actual baseline or native process was duplicated or misclassified",
    )
    actual_reference_workers: int | None
    if validated_reference_workers == 2:
        actual_reference_workers = 2
    elif reference_controllers:
        actual_reference_workers = None
    else:
        actual_reference_workers = 0
    return {
        "schema": SCHEMA + "-failure",
        "status": "FAIL",
        "error_type": type(error).__qualname__,
        "error": str(error),
        "actual_reference_workers": actual_reference_workers,
        "actual_reference_worker_count_known": (
            actual_reference_workers is not None
        ),
        "actual_candidate_workers": candidate_workers,
        "actual_candidate_imports": (
            None if candidate_workers else 0
        ),
        "actual_baseline_controller_invocations": reference_controllers,
        "actual_candidate_process_invocations": candidate_workers,
        "actual_process_context_count": len(retained),
        "actual_process_contexts": retained,
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


def baseline_source_fields(
    recorder_pin: str,
    label: str,
) -> dict[str, Any]:
    validate_digest(recorder_pin, "frozen changing-buffer recorder")
    return {
        "python": "3.14.6",
        "label": validate_label(label),
        "recorder_relative": SOURCE_RELATIVE,
        "recorder_source_sha256": recorder_pin,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "pinned_python": PINNED_PYTHON,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "witnessed_regression_outer_size": (
            WITNESSED_REGRESSION_OUTER_SIZE
        ),
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
    }


def validate_baseline_result(
    value: Any,
    oracle: Any,
    matrix: list[dict[str, Any]],
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
        "shape_sizes": dict(SHAPE_SIZES),
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
            "baseline_records_sha256",
            "source_owners",
            "reference_a",
            "reference_b",
            "reference_a_process",
            "reference_b_process",
        },
        "a complete independently frozen two-reference baseline was forged",
    )
    for name, original in expected.items():
        require(
            value.get(name) == original
            and type(value.get(name)) is type(original),
            "a genuine changing-buffer baseline was changed: " + name,
        )
    validate_digest(
        value["baseline_records_sha256"],
        "all 10,240 source-ordered reference observations",
    )
    try:
        oracle.validate_source_owners(
            value["source_owners"],
            ORACLE_SHA256,
        )
        actual = oracle.validate_reference_pair(
            value["reference_a"],
            value["reference_b"],
            value["reference_a_process"],
            value["reference_b_process"],
            source_pin=ORACLE_SHA256,
            matrix=matrix,
        )
    except Exception as error:
        raise RecorderError(
            "the frozen shape oracle rejected both complete standard workers",
        ) from error
    first = value["reference_a"]
    second = value["reference_b"]
    require(
        actual == value["baseline_records_sha256"]
        and first["records_sha256"] == actual
        and second["records_sha256"] == actual
        and value["source_owners"]
        == first["source_owners"]
        == second["source_owners"]
        and type(first["pid"]) is int
        and type(second["pid"]) is int
        and first["pid"] != second["pid"],
        "the two independently isolated shape reference workers disagree",
    )
    return value


def validate_oracle_failure(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
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
        "a complete genuine shape reference failure was forged",
    )
    nested = value.get("complete_reference_worker_failure")
    if nested is not None:
        require(
            type(nested) is dict,
            "a failed genuine isolated reference process was concealed",
        )
        if "stdout" in nested:
            decode_stream(nested["stdout"], "failed shape reference stdout")
        if "stderr" in nested:
            decode_stream(nested["stderr"], "failed shape reference stderr")
    return value


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
    failures: list[str] = []
    raw_stdout = process.get("stdout")
    raw_stderr = process.get("stderr")
    stdout = capture_stream(raw_stdout, "complete shape baseline stdout")
    stderr = capture_stream(raw_stderr, "complete shape baseline stderr")
    upper_bound = report_size_upper_bound(
        "baseline",
        len(raw_stdout),
        len(raw_stderr),
    )
    decoded: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    structured_failure: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append(
            "the pinned shape baseline could not start: "
            + str(process.get("spawn_error"))
        )
    if process.get("timed_out") is True:
        failures.append(
            "the genuine two-reference shape controller exceeded its timeout"
        )
    if raw_stdout:
        try:
            decoded = decode_document(
                raw_stdout,
                "genuine two-reference shape controller",
            )
            if decoded.get("schema") == (
                ORACLE_SCHEMA + "-two-reference-baseline"
            ):
                result = validate_baseline_result(decoded, oracle, matrix)
            elif decoded.get("schema") == ORACLE_SCHEMA + "-failure":
                structured_failure = validate_oracle_failure(decoded)
                failures.append(
                    "the frozen shape baseline reported: "
                    + structured_failure["error"]
                )
            else:
                raise RecorderError(
                    "an unrecognized genuine shape reference was emitted",
                )
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append(
                "invalid complete shape reference observation: "
                + str(error)
            )
    if result is None:
        failures.append(
            "agreement on all 10,240 changing-buffer cases remains unknown"
        )
    if raw_stderr:
        failures.append(
            "the genuine changing-buffer baseline emitted complete stderr"
        )
    expected_exit = 0 if result is not None and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        failures.append(
            "the genuine shape baseline crashed or returned the wrong exit"
        )
    if post_run_error is not None:
        failures.append(
            "post-run frozen source authentication failed: "
            + post_run_error
        )
    if before != after:
        failures.append(
            "the complete pinned changing-buffer source closure changed"
        )
    first = result["reference_a"] if result is not None else None
    second = result["reference_b"] if result is not None else None
    report = {
        "schema": SCHEMA + "-complete-baseline-report",
        "status": "FAIL" if failures else "PASS",
        **baseline_source_fields(recorder_pin, label),
        "source_closure_before": dict(before),
        "source_closure_after": dict(after) if after is not None else None,
        "source_closure_unchanged": before == after,
        "complete_baseline_process_stdout": stdout,
        "complete_baseline_process_stderr": stderr,
        "lossless_evidence_layout": (
            "one-authenticated-baseline-controller-stdout"
        ),
        "duplicate_reference_vectors": False,
        "mathematical_report_bytes_upper_bound": upper_bound,
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "structured_baseline_failure_type": (
            structured_failure["error_type"]
            if structured_failure is not None
            else None
        ),
        "structured_baseline_failure_message": (
            structured_failure["error"]
            if structured_failure is not None
            else None
        ),
        "validated_reference_a_case_count": (
            len(first["records"]) if first is not None else None
        ),
        "validated_reference_b_case_count": (
            len(second["records"]) if second is not None else None
        ),
        "baseline_records_sha256": (
            result["baseline_records_sha256"]
            if result is not None
            else None
        ),
        "baseline_reference_pids": (
            [first["pid"], second["pid"]]
            if first is not None and second is not None
            else None
        ),
        "actual_reference_workers": 2 if result is not None else None,
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
        "actual_baseline_process_spawn_error": process.get("spawn_error"),
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    canonical_identity(
        report,
        report["mathematical_report_bytes_upper_bound"],
    )
    return report


def make_baseline_receipt(
    recorder_pin: str,
    label: str,
    report: Mapping[str, Any],
    publication: Mapping[str, Any],
    preflight: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-durable-baseline-publication-receipt",
        "status": "PASS",
        "baseline_result_status": report["status"],
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
        "lossless_evidence_layout": report["lossless_evidence_layout"],
        "duplicate_reference_vectors": report["duplicate_reference_vectors"],
        "mathematical_report_bytes_upper_bound": (
            report["mathematical_report_bytes_upper_bound"]
        ),
        "maximum_report_uncompressed_bytes": (
            report["maximum_report_uncompressed_bytes"]
        ),
        "report_relative": publication["path"],
        "report_sha256": publication["sha256"],
        "report_bytes": publication["bytes"],
        "report_uncompressed_sha256": (
            publication["uncompressed_sha256"]
        ),
        "report_uncompressed_bytes": publication["uncompressed_bytes"],
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
        "fresh_paths_checked_before_baseline": (
            preflight["fresh_paths_checked_before_observation"]
        ),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def record_baseline(
    recorder_pin: str,
    oracle_pin: str,
    matrix_pin: str,
    label: str,
) -> dict[str, Any]:
    global ACTUAL_VALIDATED_REFERENCE_WORKERS
    verify_runtime()
    validate_digest(recorder_pin, "explicitly frozen shape recorder")
    require(
        validate_digest(
            oracle_pin,
            "independently frozen changing-buffer oracle",
        ) == ORACLE_SHA256
        and validate_digest(
            matrix_pin,
            "independently frozen changing-buffer matrix",
        ) == MATRIX_SHA256,
        "pin the exact frozen 10,240-case changing-buffer oracle and matrix",
    )
    oracle, _, _, matrix, before = authenticate_frozen_tools(recorder_pin)
    validate_frozen_source_closure(before, recorder_pin)
    with preflight_fresh_outputs("baseline", label) as preflight:
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
            after = authenticate_frozen_tools(recorder_pin)[4]
            validate_frozen_source_closure(after, recorder_pin)
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
        if report["actual_reference_workers"] == 2:
            ACTUAL_VALIDATED_REFERENCE_WORKERS = 2
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
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def validate_baseline_receipt(
    value: Any,
    pins: OwnerPins,
) -> dict[str, Any]:
    report_relative, receipt_relative = approved_paths(
        "baseline",
        pins.baseline.label,
    )
    expected = {
        "schema": SCHEMA + "-durable-baseline-publication-receipt",
        "status": "PASS",
        "baseline_result_status": "PASS",
        **baseline_source_fields(pins.recorder, pins.baseline.label),
        "baseline_records_sha256": pins.baseline.records,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "source_closure_unchanged": True,
        "lossless_evidence_layout": (
            "one-authenticated-baseline-controller-stdout"
        ),
        "duplicate_reference_vectors": False,
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "report_relative": report_relative,
        "report_sha256": pins.baseline.archive,
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_relative,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_baseline": True,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    extras = {
        "baseline_reference_pids",
        "source_closure_before",
        "source_closure_after",
        "report_bytes",
        "report_uncompressed_sha256",
        "report_uncompressed_bytes",
        "mathematical_report_bytes_upper_bound",
    }
    require(
        type(value) is dict and set(value) == set(expected) | extras,
        "the complete two-reference changing-buffer receipt was forged",
    )
    for name, original in expected.items():
        require(
            value.get(name) == original
            and type(value.get(name)) is type(original),
            "the frozen changing-buffer receipt changed: " + name,
        )
    pids = value["baseline_reference_pids"]
    require(
        type(pids) is list
        and len(pids) == 2
        and all(type(pid) is int and pid > 0 for pid in pids)
        and pids[0] != pids[1],
        "the two independent frozen shape reference PIDs were aliased",
    )
    require(
        type(value["report_bytes"]) is int
        and 0 < value["report_bytes"] <= MAX_ARCHIVE_BYTES
        and type(value["report_uncompressed_bytes"]) is int
        and 0 < value["report_uncompressed_bytes"]
        <= MAX_UNCOMPRESSED_BYTES,
        "the complete lossless changing-buffer archive bounds were forged",
    )
    require(
        type(value["mathematical_report_bytes_upper_bound"]) is int
        and 0 < value["mathematical_report_bytes_upper_bound"]
        <= MAX_UNCOMPRESSED_BYTES
        and value["report_uncompressed_bytes"]
        <= value["mathematical_report_bytes_upper_bound"],
        "the lossless two-reference baseline has no proved full-scale byte bound",
    )
    validate_digest(
        value["report_uncompressed_sha256"],
        "all complete uncompressed changing-buffer observations",
    )
    validate_frozen_source_closure(
        value["source_closure_before"],
        pins.recorder,
    )
    require(
        value["source_closure_before"] == value["source_closure_after"],
        "a frozen changing-buffer source changed during the baseline",
    )
    return value


def authenticate_baseline_receipt(
    pins: OwnerPins,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _, relative = approved_paths(
        "baseline",
        pins.baseline.label,
    )
    owner, raw = read_owned_regular(
        relative,
        pins.baseline.receipt,
        MAX_SOURCE_BYTES,
        retain=True,
    )
    require(raw is not None, "retain the complete published shape receipt")
    return (
        validate_baseline_receipt(
            decode_document(raw, "published shape baseline receipt"),
            pins,
        ),
        owner,
    )


def reconstruct_baseline_result(
    report: Mapping[str, Any],
    oracle: Any,
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    raw = decode_stream(
        report.get("complete_baseline_process_stdout"),
        "one authenticated published shape baseline stdout",
    )
    require(
        decode_stream(
            report.get("complete_baseline_process_stderr"),
            "one authenticated published shape baseline stderr",
        ) == b"",
        "a complete published reference emitted hidden standard errors",
    )
    observed = validate_baseline_result(
        decode_document(
            raw,
            "complete decoded-on-demand shape baseline",
        ),
        oracle,
        matrix,
    )
    require(
        observed["baseline_records_sha256"]
        == report.get("baseline_records_sha256")
        and [
            observed["reference_a"]["pid"],
            observed["reference_b"]["pid"],
        ] == report.get("baseline_reference_pids"),
        "the one preserved original worker stream lost a reference or case",
    )
    return observed


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
        "the prior signed two-reference shape baseline did not actually pass",
    )
    for name, original in baseline_source_fields(
        pins.recorder,
        pins.baseline.label,
    ).items():
        require(
            value.get(name) == original,
            "a complete shape baseline source field changed: " + name,
        )
    require(
        value.get("source_closure_unchanged") is True
        and value.get("source_closure_before")
        == value.get("source_closure_after")
        == receipt["source_closure_before"]
        and value.get("validated_reference_a_case_count") == CASE_COUNT
        and value.get("validated_reference_b_case_count") == CASE_COUNT
        and value.get("baseline_records_sha256") == pins.baseline.records
        and value.get("baseline_reference_pids")
        == receipt["baseline_reference_pids"]
        and value.get("actual_reference_workers") == 2
        and value.get("actual_candidate_workers") == 0
        and value.get("actual_candidate_imports") == 0
        and value.get("actual_baseline_controller_invocations") == 1
        and value.get("lossless_evidence_layout")
        == "one-authenticated-baseline-controller-stdout"
        and value.get("duplicate_reference_vectors") is False
        and value.get("maximum_report_uncompressed_bytes")
        == MAX_UNCOMPRESSED_BYTES
        and value.get("mathematical_report_bytes_upper_bound")
        == receipt["mathematical_report_bytes_upper_bound"]
        and 0 < value["mathematical_report_bytes_upper_bound"]
        <= MAX_UNCOMPRESSED_BYTES
        and value.get("all_failure_reasons") == []
        and value.get("failure_count") == 0
        and value.get("clock_samples") == 0
        and value.get("timing_trials_run") == 0
        and value.get("benchmark_files_read") == 0
        and value.get("hidden_cases_read") == 0
        and value.get("performance") == "NOT MEASURED"
        and value.get("source_to_binary_reproducibility")
        == "NOT ESTABLISHED"
        and value.get("candidate_qualified_for_hidden_benchmark") is False
        and value.get("final_winner_selected") is False,
        "the complete two-reference shape baseline was changed or failed",
    )
    require(
        not set(value) & {
            "complete_decoded_baseline_process",
            "complete_baseline_result",
            "reference_a_records",
            "reference_b_records",
            "reference_a_process",
            "reference_b_process",
            "complete_structured_baseline_failure",
            "complete_reference_worker_failure",
        },
        "a baseline redundantly duplicated decoded original worker vectors",
    )
    reconstruct_baseline_result(value, oracle, matrix)
    return value


def stream_baseline_archive(
    pins: OwnerPins,
    oracle: Any,
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    relative, _ = approved_paths(
        "baseline",
        pins.baseline.label,
    )
    owner, _ = read_owned_regular(
        relative,
        pins.baseline.archive,
        MAX_ARCHIVE_BYTES,
    )
    require(
        owner["bytes"] == receipt["report_bytes"],
        "the exact complete lossless shape baseline archive size changed",
    )
    with open_owned_descriptor(relative) as (descriptor, before):
        require(
            (before.st_dev, before.st_ino)
            == (owner["device"], owner["inode"]),
            "the complete lossless reference archive inode changed",
        )
        plain = hashlib.sha256()
        blocks: list[bytes] = []
        count = 0
        try:
            with io.FileIO(descriptor, "rb", closefd=False) as source:
                with gzip.GzipFile(fileobj=source, mode="rb") as archive:
                    while True:
                        block = archive.read(131_072)
                        require(
                            type(block) is bytes,
                            "the complete lossless baseline produced invalid bytes",
                        )
                        if not block:
                            break
                        count += len(block)
                        require(
                            count <= MAX_UNCOMPRESSED_BYTES,
                            "the complete shape baseline exceeded its safe bound",
                        )
                        plain.update(block)
                        blocks.append(block)
        except (OSError, EOFError, gzip.BadGzipFile) as error:
            raise RecorderError(
                "the signed changing-buffer baseline is not lossless",
            ) from error
    require(
        count == receipt["report_uncompressed_bytes"]
        and plain.hexdigest() == receipt["report_uncompressed_sha256"],
        "the complete signed shape baseline was truncated or substituted",
    )
    report = decode_document(
        b"".join(blocks),
        "all signed changing-buffer reference observations",
    )
    return (
        validate_archived_baseline(
            report,
            pins,
            oracle,
            matrix,
            receipt,
        ),
        owner,
    )


def make_audit_manifest(
    pins: OwnerPins,
    audit: Any,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    native = {spec.engine_relative: pins.engine}
    if spec.bridge_relative != spec.engine_relative:
        native[spec.bridge_relative] = pins.bridge
    try:
        manifest = audit.validate_family_pins(
            spec.name,
            pins.adapter,
            pins.engine,
            pins.bridge,
            [
                relative + "=" + expected
                for relative, expected in pins.owned_sources
            ],
            [
                relative + "=" + expected
                for relative, expected in native.items()
            ],
        )
        audit.validate_manifest(manifest, spec.name)
    except Exception as error:
        raise RecorderError(
            "the immutable V3 no-delegation audit rejected this owned family",
        ) from error
    return manifest


def native_pins(pins: OwnerPins) -> dict[str, str]:
    family_spec(pins.family)
    return {
        "source": validate_digest(
            pins.adapter,
            "independently owned Python adapter",
        ),
        "native_engine": validate_digest(
            pins.engine,
            "independently owned native matching engine",
        ),
        "native_bridge": validate_digest(
            pins.bridge,
            "independently owned native Python bridge",
        ),
    }


def authenticate_family_closure(
    pins: OwnerPins,
    v5: Any,
    audit: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    spec = family_spec(pins.family)
    selected = v5.family_spec(spec.name)
    expected_pins = native_pins(pins)
    require(
        selected.adapter_module == spec.adapter_module
        and selected.adapter_relative == spec.adapter_relative
        and selected.engine_relative == spec.engine_relative
        and selected.bridge_module == spec.bridge_module
        and selected.bridge_relative == spec.bridge_relative
        and selected.owned_ctypes is spec.owned_ctypes
        and v5.validate_pins(expected_pins, selected) == expected_pins,
        "the immutable V5 native family, bridge, or FFI policy changed",
    )
    manifest = make_audit_manifest(pins, audit)
    try:
        closure = audit.authenticate_closure(
            spec.name,
            manifest,
            AUDIT_SHA256,
        )
        serializable = audit.serializable_owners(closure)
        audit.validate_serializable_owners(
            serializable,
            spec.name,
            manifest,
            AUDIT_SHA256,
        )
    except Exception as error:
        raise RecorderError(
            "the immutable V3 audit rejected the complete native closure",
        ) from error
    return serializable, manifest


def validate_guard(
    value: Any,
    spec: FamilySpec,
) -> dict[str, Any]:
    require(
        type(value) is dict,
        "a continuously active V5 no-delegation guard is mandatory",
    )
    for name in GUARD_TRUE_FIELDS:
        require(
            value.get(name) is True,
            "a native regex anti-delegation guard was omitted: " + name,
        )
    require(
        value.get("public_type_names_used_for_ownership") is False,
        "a compatible public candidate type was misclassified as native proof",
    )
    for name in (
        "actual_method_guard_checks",
        "actual_warning_registry_guard_checks",
    ):
        require(
            type(value.get(name)) is int
            and value[name] == 2 * CASE_COUNT,
            "a before-and-after native ownership guard was omitted: " + name,
        )
    require(
        value.get("owned_native_ffi_allowed") is spec.owned_ctypes,
        "the independently owned Zig-only FFI policy changed",
    )
    for name in (
        "trusted_stdlib_ctypes_preloaded",
        "trusted_stdlib_ctypes_builtin_verified",
        "trusted_stdlib_ctypes_pythonapi_initialized",
    ):
        require(
            value.get(name) is spec.owned_ctypes,
            "the exact owned native FFI guard changed: " + name,
        )
    require(
        value.get("trusted_stdlib_ctypes_source_sha256")
        == (TRUSTED_CTYPES_SHA256 if spec.owned_ctypes else None),
        "the independently owned Zig-only ctypes FFI was substituted",
    )
    for name in GUARD_COUNTER_FIELDS:
        require(
            type(value.get(name)) is int and value[name] >= 0,
            "a continuous actual native ownership counter was concealed",
        )
    if spec.owned_ctypes:
        require(
            value["owned_ctypes_load_count"] >= 1
            and value["owned_ctypes_symbol_count"] >= 1,
            "the genuinely owned Zig engine and symbols were never loaded",
        )
    else:
        require(
            value["owned_ctypes_load_count"] == 0
            and value["owned_ctypes_symbol_count"] == 0,
            "an unowned external engine was loaded through native FFI",
        )
    return value


def snapshot_guard(
    active: Mapping[str, Any],
    spec: FamilySpec,
) -> dict[str, Any]:
    result = {name: active.get(name) for name in GUARD_TRUE_FIELDS}
    result.update({
        "public_type_names_used_for_ownership": (
            active.get("public_type_names_used_for_ownership")
        ),
        "actual_method_guard_checks": (
            active.get("actual_method_guard_checks")
        ),
        "actual_warning_registry_guard_checks": (
            active.get("actual_warning_registry_guard_checks")
        ),
        "owned_native_ffi_allowed": (
            active.get("owned_native_ffi_allowed")
        ),
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
    result.update({
        name: active.get(name)
        for name in GUARD_COUNTER_FIELDS
    })
    return validate_guard(result, spec)


def validate_candidate_outcome(
    value: Any,
    oracle: Any,
) -> dict[str, Any]:
    require(
        type(value) is dict and type(value.get("status")) is str,
        "a complete genuine changing-buffer candidate observation is mandatory",
    )
    if value["status"] == "contract-violation":
        require(
            set(value) == {
                "status",
                "violation",
                "partial_event_ledger",
                "partial_callback_ledger",
                "partial_warning_ledger",
                "complete_case_evidence_available",
            }
            and type(value.get("violation")) is dict
            and set(value["violation"]) == {"type", "message"}
            and type(value["violation"].get("type")) is str
            and type(value["violation"].get("message")) is str
            and value.get("partial_event_ledger") is None
            and value.get("partial_callback_ledger") is None
            and value.get("partial_warning_ledger") is None
            and value.get("complete_case_evidence_available") is False,
            "a genuine changing-buffer contract failure was hidden",
        )
    else:
        require(
            value["status"] in {"return", "raise"},
            "an approximate changing-buffer result was injected",
        )
        try:
            oracle.validate_outcome(value)
        except Exception as error:
            raise RecorderError(
                "the immutable shape oracle rejected a candidate event ledger",
            ) from error
    canonical(value)
    return value


def validate_candidate_records(
    matrix: list[dict[str, Any]],
    records: Any,
    expected: Any,
    oracle: Any,
) -> list[dict[str, Any]]:
    validate_digest(
        expected,
        "all 10,240 source-ordered native candidate observations",
    )
    require(
        type(records) is list and len(records) == CASE_COUNT,
        "all 10,240 actual candidate shape observations are mandatory",
    )
    for case, record in zip(matrix, records, strict=True):
        require(
            type(record) is dict
            and set(record) == {
                "case",
                "cohort",
                "api",
                "outer_size",
                "nested_size",
                "outcome",
            }
            and record.get("case") == case["case"]
            and record.get("cohort") == case["cohort"]
            and record.get("api") == case["api"]
            and type(record.get("outer_size")) is int
            and record["outer_size"] == case["outer_size"]
            and type(record.get("nested_size")) is int
            and record["nested_size"] == case["nested_size"],
            "a genuine candidate case, size, or source order was concealed",
        )
        outcome = validate_candidate_outcome(record["outcome"], oracle)
        if outcome["status"] != "contract-violation":
            require(
                outcome["outer_size"] == case["outer_size"]
                and outcome["nested_size"] == case["nested_size"]
                and outcome["count_requested"] == case["count"]
                and outcome["pos_requested"] == case["pos"]
                and outcome["endpos_requested"] == case["endpos"],
                "a real visible size, offset, or substitution was hidden",
            )
    require(
        digest(records) == expected,
        "the complete changing-buffer candidate observation vector changed",
    )
    return records


def observe_candidate_case(
    case: Mapping[str, Any],
    candidate: Any,
    oracle: Any,
) -> dict[str, Any]:
    try:
        outcome = oracle.execute_case(case, candidate)
    except oracle.ShapeOracleError as error:
        outcome = {
            "status": "contract-violation",
            "violation": {
                "type": type(error).__qualname__,
                "message": str(error),
            },
            "partial_event_ledger": None,
            "partial_callback_ledger": None,
            "partial_warning_ledger": None,
            "complete_case_evidence_available": False,
        }
    return validate_candidate_outcome(outcome, oracle)


def validate_native_provenance(
    value: Any,
    pins: OwnerPins,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    require(
        type(value) is dict
        and set(value) == {"source", "native_engine", "native_bridge"},
        "complete genuinely guarded native provenance is mandatory",
    )
    for name, relative, expected in (
        ("source", spec.adapter_relative, pins.adapter),
        ("native_engine", spec.engine_relative, pins.engine),
        ("native_bridge", spec.bridge_relative, pins.bridge),
    ):
        validate_owner(value.get(name), relative, expected)
    require(
        (value["native_engine"] == value["native_bridge"])
        is (spec.name == "c"),
        "an independently owned engine or native bridge was aliased",
    )
    return value


def execute_candidate_worker(pins: OwnerPins) -> dict[str, Any]:
    verify_runtime()
    spec = family_spec(pins.family)
    oracle, v5, audit, matrix, sources = authenticate_frozen_tools(
        pins.recorder,
    )
    receipt, receipt_owner = authenticate_baseline_receipt(pins)
    reference, archive_owner = stream_baseline_archive(
        pins,
        oracle,
        matrix,
        receipt,
    )
    validate_archived_baseline(
        reference,
        pins,
        oracle,
        matrix,
        receipt,
    )
    before, manifest = authenticate_family_closure(pins, v5, audit)
    warning, identity, _, _ = v5.load_frozen_oracles()
    original = importlib.import_module("re")
    require(
        type(original) is types.ModuleType and original.__name__ == "re",
        "the genuine original CPython guard owner was substituted",
    )
    selected = v5.family_spec(spec.name)
    records: list[dict[str, Any]] = []
    guard: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    with warning.installed_warning_safe_guard(identity):
        with v5.chosen_original_guard(
            original,
            native_pins(pins),
            selected,
            identity,
            warning,
        ) as active:
            candidate = active.get("candidate")
            require(
                type(candidate) is types.ModuleType
                and candidate.__name__ == spec.adapter_module,
                "a standard, external, or sibling regex engine escaped",
            )
            require(
                active.get("actual_method_guard_checks") == 0
                and active.get("actual_warning_registry_guard_checks") == 0,
                "continuous candidate guards did not start at zero",
            )
            for case in matrix:
                active["verify"]()
                active["actual_method_guard_checks"] += 1
                try:
                    outcome = observe_candidate_case(
                        case,
                        candidate,
                        oracle,
                    )
                finally:
                    active["verify"]()
                    active["actual_method_guard_checks"] += 1
                records.append({
                    "case": case["case"],
                    "cohort": case["cohort"],
                    "api": case["api"],
                    "outer_size": case["outer_size"],
                    "nested_size": case["nested_size"],
                    "outcome": outcome,
                })
            guard = snapshot_guard(active, spec)
            actual_provenance = active.get("native_provenance")
            require(
                v5.validate_owners(
                    actual_provenance,
                    selected,
                    native_pins(pins),
                ),
                "the continuously guarded native shape engine changed",
            )
            provenance = validate_native_provenance(
                actual_provenance,
                pins,
            )
    require(
        guard is not None and provenance is not None,
        "complete continuous native candidate ownership is mandatory",
    )
    records_sha256 = digest(records)
    validate_candidate_records(
        matrix,
        records,
        records_sha256,
        oracle,
    )
    after, final_manifest = authenticate_family_closure(
        pins,
        v5,
        audit,
    )
    require(
        before == after and manifest == final_manifest,
        "an independently owned candidate source or native engine changed",
    )
    return {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": "candidate-" + spec.name,
        "pid": os.getpid(),
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
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def validate_candidate_worker(
    value: Any,
    pins: OwnerPins,
    matrix: list[dict[str, Any]],
    *,
    expected_pid: int,
    oracle: Any,
    audit: Any,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    require(
        type(expected_pid) is int and expected_pid > 0,
        "an exact independently isolated candidate PID is mandatory",
    )
    expected = {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": "candidate-" + spec.name,
        "pid": expected_pid,
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
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    extras = {
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
        type(value) is dict and set(value) == set(expected) | extras,
        "a complete guarded changing-buffer candidate worker was forged",
    )
    for name, original in expected.items():
        require(
            value.get(name) == original
            and type(value.get(name)) is type(original),
            "a genuine isolated shape candidate changed: " + name,
        )
    pids = value["baseline_reference_pids"]
    require(
        type(pids) is list
        and len(pids) == 2
        and all(type(pid) is int and pid > 0 for pid in pids)
        and pids[0] != pids[1]
        and expected_pid not in pids,
        "a candidate PID collided with a genuine original reference",
    )
    require(
        type(value.get("actual_candidate_imports")) is int
        and value["actual_candidate_imports"] >= 2,
        "a genuinely owned candidate adapter or native bridge was not loaded",
    )
    validate_owner(
        value.get("baseline_receipt_owner"),
        approved_paths("baseline", pins.baseline.label)[1],
        pins.baseline.receipt,
    )
    validate_owner(
        value.get("baseline_archive_owner"),
        approved_paths("baseline", pins.baseline.label)[0],
        pins.baseline.archive,
    )
    validate_frozen_source_closure(
        value.get("source_provenance"),
        pins.recorder,
    )
    manifest = make_audit_manifest(pins, audit)
    require(
        value.get("audit_manifest") == manifest,
        "the complete immutable V3 native manifest was substituted",
    )
    try:
        audit.validate_serializable_owners(
            value.get("owned_source_closure"),
            spec.name,
            manifest,
            AUDIT_SHA256,
        )
    except Exception as error:
        raise RecorderError(
            "the V3 audit rejected a complete genuine native owner",
        ) from error
    validate_native_provenance(
        value.get("native_provenance"),
        pins,
    )
    validate_guard(value.get("matcher_guard"), spec)
    validate_candidate_records(
        matrix,
        value.get("records"),
        value.get("records_sha256"),
        oracle,
    )
    return value


def run_candidate_process(pins: OwnerPins) -> dict[str, Any]:
    arguments = [
        PINNED_PYTHON,
        "-I",
        "-B",
        SOURCE_ABSOLUTE,
        "--internal-candidate-worker",
        "--candidate",
        pins.family,
        "--recorder-source-sha256",
        pins.recorder,
        "--oracle-source-sha256",
        ORACLE_SHA256,
        "--matrix-sha256",
        MATRIX_SHA256,
        "--ownership-audit-source-sha256",
        AUDIT_SHA256,
        "--baseline-label",
        pins.baseline.label,
        "--baseline-receipt-sha256",
        pins.baseline.receipt,
        "--baseline-archive-sha256",
        pins.baseline.archive,
        "--baseline-records-sha256",
        pins.baseline.records,
        "--candidate-source-sha256",
        pins.adapter,
        "--native-engine-sha256",
        pins.engine,
        "--native-bridge-sha256",
        pins.bridge,
    ]
    for relative, expected in pins.owned_sources:
        arguments.extend((
            "--owned-source-sha256",
            relative + "=" + expected,
        ))
    return run_one_process(arguments)


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
    validate_archived_baseline(
        reference,
        pins,
        oracle,
        matrix,
        receipt,
    )
    baseline_result = reconstruct_baseline_result(
        reference,
        oracle,
        matrix,
    )
    raw_stdout = process.get("stdout")
    raw_stderr = process.get("stderr")
    stdout = capture_stream(
        raw_stdout,
        "complete changing-buffer candidate stdout",
    )
    stderr = capture_stream(
        raw_stderr,
        "complete changing-buffer candidate stderr",
    )
    upper_bound = report_size_upper_bound(
        "candidate",
        len(raw_stdout),
        len(raw_stderr),
    )
    failures: list[str] = []
    decoded: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append(
            "the independently owned shape candidate could not start: "
            + str(process.get("spawn_error"))
        )
    if process.get("timed_out") is True:
        failures.append(
            "the native changing-buffer candidate exceeded its safe timeout"
        )
    if raw_stdout:
        try:
            decoded = decode_document(
                raw_stdout,
                "complete guarded changing-buffer candidate",
            )
            candidate = validate_candidate_worker(
                decoded,
                pins,
                matrix,
                expected_pid=process.get("pid"),
                oracle=oracle,
                audit=audit,
            )
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append(
                "invalid complete native changing-buffer observation: "
                + str(error)
            )
    if candidate is None:
        failures.append(
            "all 10,240 genuine candidate buffer observations remain unknown"
        )
    if raw_stderr:
        failures.append(
            "the genuine changing-buffer candidate emitted complete stderr"
        )
    expected_exit = 0 if candidate is not None and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        failures.append(
            "the owned changing-buffer candidate crashed or returned a wrong exit"
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
    mismatch_by_cohort = {cohort: 0 for cohort in COHORTS}
    mismatch_by_api = {api: 0 for api in APIS}
    mismatch_by_target = {target: 0 for target in TARGETS}
    mismatch_by_behavior = {behavior: 0 for behavior in BEHAVIORS}
    witnessed_mismatch_by_nested_size = {
        str(size): 0 for size in WITNESSED_REGRESSION_NESTED_SIZES
    }
    mismatches: list[dict[str, Any]] | None = None
    if candidate is not None:
        mismatches = []
        for case, original, actual in zip(
            matrix,
            baseline_result["reference_a"]["records"],
            candidate["records"],
            strict=True,
        ):
            require(
                case["case"] == original["case"] == actual["case"]
                and case["cohort"] == original["cohort"] == actual["cohort"]
                and case["api"] == original["api"] == actual["api"]
                and case["outer_size"]
                == original["outer_size"]
                == actual["outer_size"]
                and case["nested_size"]
                == original["nested_size"]
                == actual["nested_size"],
                "a complete shape baseline or candidate case was reordered",
            )
            if original["outcome"] != actual["outcome"]:
                mismatch_by_cohort[case["cohort"]] += 1
                mismatch_by_api[case["api"]] += 1
                mismatch_by_target[case["target"]] += 1
                mismatch_by_behavior[case["behavior"]] += 1
                if (
                    case["outer_size"] == WITNESSED_REGRESSION_OUTER_SIZE
                    and case["nested_size"]
                    in WITNESSED_REGRESSION_NESTED_SIZES
                ):
                    witnessed_mismatch_by_nested_size[
                        str(case["nested_size"])
                    ] += 1
                mismatches.append({
                    "case": case["case"],
                    "cohort": case["cohort"],
                    "api": case["api"],
                    "target": case["target"],
                    "behavior": case["behavior"],
                    "outer_size": case["outer_size"],
                    "nested_size": case["nested_size"],
                    "input": case,
                    "baseline_outcome": original["outcome"],
                    "candidate_outcome": actual["outcome"],
                })
        if mismatches:
            failures.append(
                "the owned candidate differs on "
                + str(len(mismatches))
                + " frozen changing-buffer cases"
            )
    report = {
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
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "pinned_python": PINNED_PYTHON,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "witnessed_regression_outer_size": (
            WITNESSED_REGRESSION_OUTER_SIZE
        ),
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
        "lossless_evidence_layout": (
            "one-authenticated-candidate-worker-stdout-and-full-mismatches"
        ),
        "duplicate_candidate_vectors": False,
        "duplicate_reference_vectors": False,
        "mathematical_report_bytes_upper_bound": upper_bound,
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": (
            len(candidate["records"])
            if candidate is not None
            else None
        ),
        "candidate_records_sha256": (
            candidate["records_sha256"]
            if candidate is not None
            else None
        ),
        "mismatch_count": (
            len(mismatches) if mismatches is not None else None
        ),
        "all_mismatches": mismatches,
        "mismatches_by_cohort": (
            mismatch_by_cohort if mismatches is not None else None
        ),
        "mismatches_by_api": (
            mismatch_by_api if mismatches is not None else None
        ),
        "mismatches_by_target": (
            mismatch_by_target if mismatches is not None else None
        ),
        "mismatches_by_behavior": (
            mismatch_by_behavior if mismatches is not None else None
        ),
        "witnessed_regression_mismatches_by_nested_size": (
            witnessed_mismatch_by_nested_size
            if mismatches is not None
            else None
        ),
        "all_mismatches_preserved": (
            True if mismatches is not None else None
        ),
        "matcher_guard": (
            candidate["matcher_guard"] if candidate is not None else None
        ),
        "actual_method_guard_checks": (
            candidate["matcher_guard"]["actual_method_guard_checks"]
            if candidate is not None
            else None
        ),
        "actual_warning_registry_guard_checks": (
            candidate["matcher_guard"][
                "actual_warning_registry_guard_checks"
            ]
            if candidate is not None
            else None
        ),
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": (
            1 if candidate is not None else None
        ),
        "actual_candidate_imports": (
            candidate["actual_candidate_imports"]
            if candidate is not None
            else None
        ),
        "actual_candidate_process_invocations": int(
            process.get("started") is True
        ),
        "actual_candidate_pid": process.get("pid"),
        "actual_candidate_process_returncode": process.get("returncode"),
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
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    canonical_identity(
        report,
        report["mathematical_report_bytes_upper_bound"],
    )
    return report


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
        "label": validate_label(label),
        "candidate_family": pins.family,
        "candidate_source_sha256": pins.adapter,
        "native_engine_sha256": pins.engine,
        "native_bridge_sha256": pins.bridge,
        "baseline_label": pins.baseline.label,
        "recorder_source_sha256": pins.recorder,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "witnessed_regression_outer_size": (
            WITNESSED_REGRESSION_OUTER_SIZE
        ),
        "witnessed_regression_nested_sizes": list(
            WITNESSED_REGRESSION_NESTED_SIZES
        ),
        "witnessed_regression_case_count": (
            len(WITNESSED_REGRESSION_NESTED_SHAPES)
            * VARIANTS_PER_COHORT
        ),
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
        "mismatches_by_cohort": report["mismatches_by_cohort"],
        "mismatches_by_api": report["mismatches_by_api"],
        "mismatches_by_target": report["mismatches_by_target"],
        "mismatches_by_behavior": report["mismatches_by_behavior"],
        "witnessed_regression_mismatches_by_nested_size": (
            report["witnessed_regression_mismatches_by_nested_size"]
        ),
        "all_mismatches_preserved": report["all_mismatches_preserved"],
        "actual_method_guard_checks": report["actual_method_guard_checks"],
        "actual_warning_registry_guard_checks": (
            report["actual_warning_registry_guard_checks"]
        ),
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_candidate_imports": report["actual_candidate_imports"],
        "actual_candidate_process_invocations": (
            report["actual_candidate_process_invocations"]
        ),
        "candidate_owner_before": report["candidate_owner_before"],
        "candidate_owner_after": report["candidate_owner_after"],
        "candidate_owner_unchanged": report["candidate_owner_unchanged"],
        "lossless_evidence_layout": report["lossless_evidence_layout"],
        "duplicate_candidate_vectors": report["duplicate_candidate_vectors"],
        "duplicate_reference_vectors": report["duplicate_reference_vectors"],
        "mathematical_report_bytes_upper_bound": (
            report["mathematical_report_bytes_upper_bound"]
        ),
        "maximum_report_uncompressed_bytes": (
            report["maximum_report_uncompressed_bytes"]
        ),
        "report_relative": publication["path"],
        "report_sha256": publication["sha256"],
        "report_bytes": publication["bytes"],
        "report_uncompressed_sha256": (
            publication["uncompressed_sha256"]
        ),
        "report_uncompressed_bytes": publication["uncompressed_bytes"],
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
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
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
    before, _ = authenticate_family_closure(pins, v5, audit)
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
            after = authenticate_family_closure(pins, v5, audit)[0]
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
        receipt = make_candidate_receipt(
            pins,
            label,
            report,
            publication,
            preflight,
        )
        receipt_publication = publish_document(
            preflight,
            receipt,
            compressed=False,
        )
    verify_runtime()
    return {
        "schema": SCHEMA + "-recorded-candidate",
        "status": report["status"],
        "publication_status": "PASS",
        "python": "3.14.6",
        "candidate_family": spec.name,
        "label": label,
        "recorder_source_sha256": pins.recorder,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "baseline_records_sha256": pins.baseline.records,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": (
            report["validated_candidate_record_count"]
        ),
        "mismatch_count": report["mismatch_count"],
        "all_mismatches_preserved": report["all_mismatches_preserved"],
        "actual_candidate_process_invocations": (
            report["actual_candidate_process_invocations"]
        ),
        "actual_reference_workers": 0,
        "actual_candidate_workers": report["actual_candidate_workers"],
        "report_publication": publication,
        "receipt_publication": receipt_publication,
        "all_failure_reasons": report["all_failure_reasons"],
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


class SourceOnlyBoundary:
    """Make real files, worker processes, engines, and clocks impossible."""

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
            "directory_syncs": 0,
            "randomness": 0,
        }

    def install(
        self,
        owner: Any,
        name: str,
        category: str,
    ) -> None:
        if not hasattr(owner, name):
            return
        self.originals.append((owner, name, getattr(owner, name)))

        def denied(*args: Any, **kwargs: Any) -> Any:
            selected = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if (
                    type(mode) is str
                    and any(flag in mode for flag in "wax+")
                ) or (
                    type(mode) is int
                    and mode & (
                        os.O_WRONLY
                        | os.O_RDWR
                        | os.O_CREAT
                        | os.O_TRUNC
                        | os.O_APPEND
                    )
                ):
                    selected = "file_writes"
            elif category == "dynamic_imports" and args:
                target = args[0]
                if type(target) is str and (
                    target == "candidates"
                    or target.startswith("candidates.")
                    or target.partition(".")[0] in {
                        "_regex",
                        "_sre",
                        "fancy_regex",
                        "google_re2",
                        "hyperscan",
                        "oniguruma",
                        "pcre",
                        "pcre2",
                        "re2",
                        "regex",
                        "rebar",
                    }
                ):
                    selected = "candidate_imports"
            self.blocked[selected] += 1
            raise SourceOnlyError(
                "source-only changing-buffer controls cannot perform "
                + selected
            )

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        operations = (
            (builtins, "open", "file_reads"),
            (io, "open", "file_reads"),
            (os, "open", "file_reads"),
            (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"),
            (os, "scandir", "file_reads"),
            (os, "listdir", "file_reads"),
            (os, "readlink", "file_reads"),
            (os, "write", "file_writes"),
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
        for owner, name, category in operations:
            self.install(owner, name, category)
        return self

    def __exit__(
        self,
        error_type: Any,
        error: Any,
        trace: Any,
    ) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False


def synthetic_owner(
    relative: str,
    source: str,
    number: int,
) -> dict[str, Any]:
    return {
        "relative": relative,
        "sha256": validate_digest(source, relative),
        "bytes": 4_096 + number,
        "device": 7,
        "inode": 90_000 + number,
    }


def synthetic_external_owner(
    absolute: str,
    source: str,
    number: int,
) -> dict[str, Any]:
    return {
        "path": absolute,
        "sha256": validate_digest(source, absolute),
        "bytes": 4_096 + number,
        "device": 7,
        "inode": 100_000 + number,
    }


def synthetic_frozen_source_closure(
    recorder_pin: str,
) -> dict[str, dict[str, Any]]:
    return {
        "recorder": synthetic_owner(
            SOURCE_RELATIVE,
            recorder_pin,
            1,
        ),
        "shape_oracle": synthetic_owner(
            ORACLE_RELATIVE,
            ORACLE_SHA256,
            2,
        ),
        "original_v5": synthetic_owner(
            V5_RELATIVE,
            V5_SHA256,
            3,
        ),
        "from_scratch_audit_v3": synthetic_owner(
            AUDIT_RELATIVE,
            AUDIT_SHA256,
            4,
        ),
        "pinned_python": synthetic_external_owner(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            5,
        ),
    }


def synthetic_reference_owners() -> dict[str, dict[str, Any]]:
    result = {
        "oracle": synthetic_external_owner(
            ROOT + "/" + ORACLE_RELATIVE,
            ORACLE_SHA256,
            11,
        ),
        "python": synthetic_external_owner(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            12,
        ),
        "v5_guard": synthetic_external_owner(
            ROOT + "/" + V5_RELATIVE,
            V5_SHA256,
            13,
        ),
        "ownership_audit": synthetic_external_owner(
            ROOT + "/" + AUDIT_RELATIVE,
            AUDIT_SHA256,
            14,
        ),
    }
    for index, (name, (filename, source)) in enumerate(
        PINNED_STDLIB_SOURCES.items(),
        start=15,
    ):
        result[name] = synthetic_external_owner(
            PINNED_STDLIB_DIRECTORY + filename,
            source,
            index,
        )
    return result


def synthetic_outcome(
    case: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "status": "return",
        "stage": case["api"],
        "value": {"type": "none"},
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
        "subject_after": {"type": "none"},
        "template_after": {"type": "none"},
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


def synthetic_records(
    matrix: list[dict[str, Any]],
) -> list[dict[str, Any]]:
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


def synthetic_reference_guard() -> dict[str, Any]:
    return {
        "candidate_import_count": 0,
        "external_regex_import_count": 0,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "required_method_guard_checks": 2 * CASE_COUNT,
        "future_candidate_guard_relative": V5_RELATIVE,
        "future_candidate_guard_sha256": V5_SHA256,
        "future_ownership_audit_relative": AUDIT_RELATIVE,
        "future_ownership_audit_sha256": AUDIT_SHA256,
        "future_candidate_guard_installed": False,
    }


def synthetic_reference_worker(
    role: str,
    pid: int,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    require(
        role in {"reference_a", "reference_b"}
        and type(pid) is int
        and pid > 0,
        "an independently identified synthetic reference is mandatory",
    )
    return {
        "schema": ORACLE_SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": pid,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "records_sha256": digest(records),
        "records": records,
        "source_owners": synthetic_reference_owners(),
        "reference_guard": synthetic_reference_guard(),
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


def synthetic_reference_process(
    worker: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "role": worker["role"],
        "pid": worker["pid"],
        "returncode": 0,
        "stdout": capture_stream(
            canonical(dict(worker)),
            "synthetic reference stdout",
        ),
        "stderr": capture_stream(
            b"",
            "synthetic reference stderr",
        ),
    }


class SyntheticOracle:
    """Validate synthetic structures without importing or running an engine."""

    def validate_source_owners(
        self,
        value: Any,
        source_pin: str,
    ) -> dict[str, dict[str, Any]]:
        require(
            source_pin == ORACLE_SHA256,
            "the frozen synthetic reference oracle was substituted",
        )
        expected: dict[str, tuple[str, str]] = {
            "oracle": (ROOT + "/" + ORACLE_RELATIVE, ORACLE_SHA256),
            "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
            "v5_guard": (ROOT + "/" + V5_RELATIVE, V5_SHA256),
            "ownership_audit": (
                ROOT + "/" + AUDIT_RELATIVE,
                AUDIT_SHA256,
            ),
        }
        expected.update({
            name: (PINNED_STDLIB_DIRECTORY + filename, source)
            for name, (filename, source)
            in PINNED_STDLIB_SOURCES.items()
        })
        require(
            type(value) is dict and set(value) == set(expected),
            "a complete synthetic original source owner was omitted",
        )
        for name, (absolute, source) in expected.items():
            validate_external_owner(
                value.get(name),
                absolute,
                source,
            )
        return value

    def validate_outcome(self, value: Any) -> dict[str, Any]:
        require(
            type(value) is dict
            and set(value) == {
                "status",
                "stage",
                "value",
                "exception",
                "events",
                "callbacks",
                "warnings",
                "subject_after",
                "template_after",
                "subject_outer_active",
                "subject_nested_active",
                "template_outer_active",
                "template_nested_active",
                "count_requested",
                "pos_requested",
                "endpos_requested",
                "outer_size",
                "nested_size",
            }
            and value.get("status") == "return"
            and value.get("stage") in APIS
            and value.get("value") == {"type": "none"}
            and value.get("exception") is None
            and value.get("events") == [
                {"event": "phase", "name": "materialize-start"},
                {"event": "phase", "name": "materialize-complete"},
                {"event": "phase", "name": "operation-start"},
                {"event": "phase", "name": "operation-return"},
                {"event": "phase", "name": "cleanup-complete"},
            ]
            and value.get("callbacks") == []
            and value.get("warnings") == []
            and value.get("subject_after") == {"type": "none"}
            and value.get("template_after") == {"type": "none"}
            and value.get("subject_outer_active") == 0
            and value.get("subject_nested_active") == 0
            and value.get("template_outer_active") == 0
            and value.get("template_nested_active") == 0
            and type(value.get("count_requested")) is int
            and type(value.get("pos_requested")) is int
            and (
                value.get("endpos_requested") is None
                or type(value.get("endpos_requested")) is int
            )
            and type(value.get("outer_size")) is int
            and value["outer_size"] in SHAPE_SIZES.values()
            and type(value.get("nested_size")) is int
            and value["nested_size"] in SHAPE_SIZES.values(),
            "a complete source-only nested event or ownership ledger was forged",
        )
        return value

    def validate_records(
        self,
        matrix: list[dict[str, Any]],
        records: Any,
        records_pin: str,
    ) -> list[dict[str, Any]]:
        validate_digest(records_pin, "complete synthetic reference cases")
        require(
            type(records) is list and len(records) == CASE_COUNT,
            "all 10,240 synthetic reference observations are mandatory",
        )
        for case, record in zip(matrix, records, strict=True):
            require(
                type(record) is dict
                and set(record) == {
                    "case",
                    "cohort",
                    "api",
                    "outer_size",
                    "nested_size",
                    "outcome",
                }
                and record.get("case") == case["case"]
                and record.get("cohort") == case["cohort"]
                and record.get("api") == case["api"]
                and record.get("outer_size") == case["outer_size"]
                and record.get("nested_size") == case["nested_size"],
                "a complete source-only reference case was omitted",
            )
            outcome = self.validate_outcome(record["outcome"])
            require(
                outcome["outer_size"] == case["outer_size"]
                and outcome["nested_size"] == case["nested_size"]
                and outcome["count_requested"] == case["count"]
                and outcome["pos_requested"] == case["pos"]
                and outcome["endpos_requested"] == case["endpos"],
                "a synthetic nested size, offset, or event was changed",
            )
        require(
            digest(records) == records_pin,
            "the complete synthetic source-ordered shape vector changed",
        )
        return records

    def validate_reference_worker(
        self,
        value: Any,
        *,
        role: str,
        source_pin: str,
        matrix: list[dict[str, Any]],
        expected_pid: int,
    ) -> dict[str, Any]:
        expected = {
            "schema": ORACLE_SCHEMA + "-isolated-reference-worker",
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
            role in {"reference_a", "reference_b"}
            and type(expected_pid) is int
            and expected_pid > 0
            and source_pin == ORACLE_SHA256
            and type(value) is dict
            and set(value) == set(expected) | {
                "records_sha256",
                "records",
                "source_owners",
                "reference_guard",
            },
            "a complete independent synthetic reference was forged",
        )
        for name, original in expected.items():
            require(
                value.get(name) == original
                and type(value.get(name)) is type(original),
                "an independent synthetic reference changed: " + name,
            )
        self.validate_source_owners(value["source_owners"], source_pin)
        require(
            value.get("reference_guard") == synthetic_reference_guard(),
            "a complete synthetic reference anti-delegation guard changed",
        )
        self.validate_records(
            matrix,
            value["records"],
            value["records_sha256"],
        )
        return value

    def validate_process(
        self,
        value: Any,
        worker: Mapping[str, Any],
        role: str,
    ) -> dict[str, Any]:
        require(
            type(value) is dict
            and set(value) == {
                "role", "pid", "returncode", "stdout", "stderr",
            }
            and value.get("role") == role
            and value.get("pid") == worker["pid"]
            and value.get("returncode") == 0
            and decode_stream(
                value.get("stdout"),
                role + " complete synthetic stdout",
            ) == canonical(dict(worker))
            and decode_stream(
                value.get("stderr"),
                role + " complete synthetic stderr",
            ) == b"",
            "a complete independent synthetic worker process was forged",
        )
        return value

    def validate_reference_pair(
        self,
        first: Mapping[str, Any],
        second: Mapping[str, Any],
        first_process: Mapping[str, Any],
        second_process: Mapping[str, Any],
        *,
        source_pin: str,
        matrix: list[dict[str, Any]],
    ) -> str:
        self.validate_reference_worker(
            first,
            role="reference_a",
            source_pin=source_pin,
            matrix=matrix,
            expected_pid=first.get("pid"),
        )
        self.validate_reference_worker(
            second,
            role="reference_b",
            source_pin=source_pin,
            matrix=matrix,
            expected_pid=second.get("pid"),
        )
        self.validate_process(first_process, first, "reference_a")
        self.validate_process(second_process, second, "reference_b")
        require(
            first["pid"] != second["pid"]
            and first["source_owners"] == second["source_owners"]
            and first["records_sha256"] == second["records_sha256"]
            and first["records"] == second["records"],
            "two genuinely independent synthetic reference PIDs collided",
        )
        return first["records_sha256"]


def synthetic_baseline_result(
    matrix: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    del matrix
    first = synthetic_reference_worker("reference_a", 8_101, records)
    second = synthetic_reference_worker("reference_b", 8_102, records)
    return {
        "schema": ORACLE_SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "baseline_records_sha256": digest(records),
        "source_owners": first["source_owners"],
        "reference_a": first,
        "reference_b": second,
        "reference_a_process": synthetic_reference_process(first),
        "reference_b_process": synthetic_reference_process(second),
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


def synthetic_process_state(
    result: Mapping[str, Any],
    *,
    pid: int,
) -> dict[str, Any]:
    require(
        type(pid) is int and pid > 0,
        "an exact synthetic process identity is mandatory",
    )
    return {
        "started": True,
        "pid": pid,
        "returncode": 0,
        "signal": None,
        "timed_out": False,
        "spawn_error": None,
        "stdout": canonical(dict(result)),
        "stderr": b"",
    }


def synthetic_actual_process_context(
    role: str,
    pid: int,
    value: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        role in {"baseline-controller", "candidate-worker"}
        and type(pid) is int
        and pid > 0,
        "an exact synthetic started process role and PID are mandatory",
    )
    return {
        "role": role,
        "pid": pid,
        "returncode": 0,
        "signal": None,
        "timed_out": False,
        "stdout": capture_stream(
            canonical(dict(value)),
            "source-only genuine-process accounting",
        ),
        "stderr": capture_stream(
            b"",
            "source-only genuine-process standard errors",
        ),
        "stream_capture_complete": True,
    }


def synthetic_owner_pins(
    family: str,
    *,
    recorder_pin: str,
    baseline: BaselinePins,
) -> OwnerPins:
    spec = family_spec(family)
    adapter = hashlib.sha256(
        ("synthetic-shape-adapter-" + family).encode("ascii")
    ).hexdigest()
    engine = hashlib.sha256(
        ("synthetic-shape-engine-" + family).encode("ascii")
    ).hexdigest()
    bridge = (
        engine
        if family == "c"
        else hashlib.sha256(
            ("synthetic-shape-bridge-" + family).encode("ascii")
        ).hexdigest()
    )
    sources = [
        relative
        + "="
        + (
            adapter
            if relative == spec.adapter_relative
            else hashlib.sha256(
                ("synthetic-owned-shape-" + relative).encode("ascii")
            ).hexdigest()
        )
        for relative in spec.owned_source_relatives
    ]
    return make_owner_pins(
        family,
        recorder_pin,
        adapter,
        engine,
        bridge,
        sources,
        baseline,
    )


class SyntheticAudit:
    """Exercise the frozen V3 owner contract without touching real files."""

    def validate_family_pins(
        self,
        family: str,
        adapter: str,
        engine: str,
        bridge: str,
        source_entries: list[str],
        native_entries: list[str],
    ) -> dict[str, Any]:
        spec = family_spec(family)
        source_map = dict(
            parse_owned_source(item)
            for item in source_entries
        )
        native_map = dict(
            parse_owned_source(item)
            for item in native_entries
        )
        require(
            len(source_map) == len(source_entries)
            and set(source_map) == set(spec.owned_source_relatives)
            and source_map.get(spec.adapter_relative) == adapter
            and set(native_map)
            == {spec.engine_relative, spec.bridge_relative}
            and native_map.get(spec.engine_relative) == engine
            and native_map.get(spec.bridge_relative) == bridge
            and (engine == bridge) is (family == "c")
            and len(set(source_map.values())) == len(source_map)
            and len(set(native_map.values())) == len(native_map),
            "a synthetic V3 native parser, bridge, or owner was omitted",
        )
        return {
            "family": family,
            "candidate_source_sha256": adapter,
            "native_engine_sha256": engine,
            "native_bridge_sha256": bridge,
            "source_sha256": dict(sorted(source_map.items())),
            "native_sha256": dict(sorted(native_map.items())),
            "immutable_policy_sha256": dict(IMMUTABLE_V3_POLICY_SHA256),
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
            and type(value.get("source_sha256")) is dict
            and type(value.get("native_sha256")) is dict,
            "a complete synthetic V3 native manifest is mandatory",
        )
        expected = self.validate_family_pins(
            value.get("family"),
            value.get("candidate_source_sha256"),
            value.get("native_engine_sha256"),
            value.get("native_bridge_sha256"),
            [
                relative + "=" + expected
                for relative, expected
                in value["source_sha256"].items()
            ],
            [
                relative + "=" + expected
                for relative, expected
                in value["native_sha256"].items()
            ],
        )
        require(
            value == expected and value["family"] == family,
            "a synthetic immutable V3 family manifest was substituted",
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
            and value.get("manifest") == manifest
            and source_pin == AUDIT_SHA256,
            "a complete synthetic independent V3 native closure was forged",
        )
        self.validate_manifest(value["manifest"], family)
        sources = value["source_owners"]
        natives = value["native_owners"]
        policies = value["policy_owners"]
        require(
            type(sources) is dict
            and set(sources) == set(manifest["source_sha256"])
            and type(natives) is dict
            and set(natives) == set(manifest["native_sha256"])
            and type(policies) is dict
            and set(policies) == set(IMMUTABLE_V3_POLICY_SHA256),
            "a complete synthetic native, policy, or lockfile was omitted",
        )
        for relative, expected in manifest["source_sha256"].items():
            validate_owner(sources.get(relative), relative, expected)
        for relative, expected in manifest["native_sha256"].items():
            validate_owner(natives.get(relative), relative, expected)
        for relative, expected in IMMUTABLE_V3_POLICY_SHA256.items():
            validate_owner(policies.get(relative), relative, expected)
        validate_owner(
            value["oracle_owner"],
            AUDIT_RELATIVE,
            AUDIT_SHA256,
        )
        validate_external_owner(
            value["python_owner"],
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
        )
        return value


def synthetic_native_closure(
    pins: OwnerPins,
    audit: SyntheticAudit,
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = make_audit_manifest(pins, audit)
    source_owners = {
        relative: synthetic_owner(relative, expected, 200 + index)
        for index, (relative, expected)
        in enumerate(manifest["source_sha256"].items())
    }
    native_owners = {
        relative: synthetic_owner(relative, expected, 300 + index)
        for index, (relative, expected)
        in enumerate(manifest["native_sha256"].items())
    }
    policy_owners = {
        relative: synthetic_owner(relative, expected, 400 + index)
        for index, (relative, expected)
        in enumerate(IMMUTABLE_V3_POLICY_SHA256.items())
    }
    closure = {
        "family": pins.family,
        "manifest": manifest,
        "source_owners": source_owners,
        "native_owners": native_owners,
        "policy_owners": policy_owners,
        "oracle_owner": synthetic_owner(
            AUDIT_RELATIVE,
            AUDIT_SHA256,
            499,
        ),
        "python_owner": synthetic_external_owner(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            500,
        ),
    }
    audit.validate_serializable_owners(
        closure,
        pins.family,
        manifest,
        AUDIT_SHA256,
    )
    return closure, manifest


def synthetic_guard(
    spec: FamilySpec,
) -> dict[str, Any]:
    value = {name: True for name in GUARD_TRUE_FIELDS}
    value.update({
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
    return validate_guard(value, spec)


def synthetic_candidate_worker(
    pins: OwnerPins,
    records: list[dict[str, Any]],
    *,
    pid: int,
    audit: SyntheticAudit,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    closure, manifest = synthetic_native_closure(pins, audit)
    native_provenance = {
        "source": closure["source_owners"][spec.adapter_relative],
        "native_engine": closure["native_owners"][spec.engine_relative],
        "native_bridge": closure["native_owners"][spec.bridge_relative],
    }
    archive_relative, receipt_relative = approved_paths(
        "baseline",
        pins.baseline.label,
    )
    return {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": "candidate-" + spec.name,
        "pid": pid,
        "candidate_family": spec.name,
        **baseline_source_fields(
            pins.recorder,
            pins.baseline.label,
        ),
        "baseline_receipt_relative": receipt_relative,
        "baseline_receipt_sha256": pins.baseline.receipt,
        "baseline_archive_relative": archive_relative,
        "baseline_archive_sha256": pins.baseline.archive,
        "baseline_records_sha256": pins.baseline.records,
        "baseline_reference_pids": [8_101, 8_102],
        "baseline_receipt_owner": synthetic_owner(
            receipt_relative,
            pins.baseline.receipt,
            601,
        ),
        "baseline_archive_owner": synthetic_owner(
            archive_relative,
            pins.baseline.archive,
            602,
        ),
        "source_provenance": synthetic_frozen_source_closure(
            pins.recorder,
        ),
        "audit_manifest": manifest,
        "owned_source_closure": closure,
        "native_provenance": native_provenance,
        "matcher_guard": synthetic_guard(spec),
        "records_sha256": digest(records),
        "records": records,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": 3,
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


def synthetic_preflight(
    kind: str,
    label: str,
    family: str | None = None,
) -> dict[str, Any]:
    report, receipt = approved_paths(kind, label, family)
    return {
        "report_relative": report,
        "receipt_relative": receipt,
        "report_basename": safe_parts(report)[-1],
        "receipt_basename": safe_parts(receipt)[-1],
        "directory_descriptor": 71,
        "directory_device": 7,
        "directory_inode": 71_001,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_observation": True,
    }


def synthetic_publication(
    path: str,
    *,
    compressed: bool,
    expected: str | None = None,
) -> dict[str, Any]:
    require(
        safe_parts(path)[:2]
        == ("experiments", "rust_public_practice_v1"),
        "a synthetic changing-buffer publication escaped the approved path",
    )
    archive = (
        validate_digest(expected, "synthetic complete archive")
        if expected is not None
        else hashlib.sha256(
            ("synthetic-shape-publication:" + path).encode("ascii")
        ).hexdigest()
    )
    plain = hashlib.sha256(
        ("synthetic-shape-plain:" + path).encode("ascii")
    ).hexdigest()
    return {
        "path": path,
        "bytes": 4_097,
        "sha256": archive,
        "uncompressed_bytes": 24_097,
        "uncompressed_sha256": plain,
        "compression": "gzip-mtime-zero-level-9" if compressed else "none",
        "actual_write_calls": 4,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True,
        "owned_temporary_removed": True,
        "complete_readback_verified": True,
    }


def expect_rejection(
    label: str,
    operation: Callable[[], Any],
    rejected: list[str],
) -> None:
    require(
        type(label) is str
        and bool(label)
        and label not in rejected
        and callable(operation),
        "an independent source-only forged control was duplicated",
    )
    try:
        operation()
    except (
        RecorderError,
        OSError,
        TypeError,
        ValueError,
        KeyError,
        IndexError,
        OverflowError,
        UnicodeError,
        EOFError,
        gzip.BadGzipFile,
    ):
        rejected.append(label)
        return
    raise RecorderError(
        "a forged changing-buffer recorder control was accepted: " + label
    )


def source_self_test() -> dict[str, Any]:
    verify_runtime(synthetic=True)
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceOnlyBoundary() as boundary:

        def accept(label: str, value: Any) -> None:
            require(
                type(label) is str
                and bool(label)
                and label not in accepted
                and bool(value),
                "an independent source-only positive control failed: "
                + str(label),
            )
            accepted.append(label)

        def reject(
            label: str,
            operation: Callable[[], Any],
        ) -> None:
            expect_rejection(label, operation, rejected)

        matrix = validate_matrix(build_frozen_matrix())
        accept("freeze-all-10240-source-ordered-original-cases", (
            len(matrix) == CASE_COUNT == 10_240
        ))
        accept("freeze-all-64-independent-shape-cohorts", (
            len(COHORTS) == 64
        ))
        accept("freeze-full-160-way-api-placement-behavior-cross-product", (
            VARIANTS_PER_COHORT
            == len(APIS) * len(TARGETS) * len(BEHAVIORS)
            == 160
        ))
        accept("freeze-exact-full-precision-unsigned-64-bit-seed", (
            PUBLISHED_SEED == 6_001_118_316_486_346_290
            and 0 <= PUBLISHED_SEED < 1 << 64
            and all(row["seed"] == PUBLISHED_SEED for row in matrix)
        ))
        accept("freeze-exact-original-changing-buffer-matrix", (
            digest(matrix) == MATRIX_SHA256
        ))
        accept("freeze-all-eight-exact-independent-backing-sizes", (
            tuple(SHAPE_SIZES.values()) == (0, 1, 2, 3, 5, 8, 13, 19)
        ))
        accept("freeze-all-five-exact-witnessed-nested-lengths", (
            WITNESSED_REGRESSION_OUTER_SIZE == 13
            and WITNESSED_REGRESSION_NESTED_SIZES == (0, 1, 2, 5, 8)
        ))
        accept("freeze-original-shape-oracle-source", (
            ORACLE_SHA256
            == "866dbf7bf4a48a867b3aaacd05cfa4f1346c747931543fa386835e783f0073aa"
        ))
        accept("freeze-independent-v3-no-delegation-audit", (
            AUDIT_SHA256
            == "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
        ))
        accept("freeze-original-v5-continuous-ownership-guard", (
            V5_SHA256
            == "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
        ))
        accept(
            "prove-at-least-two-gibibytes-of-lossless-report-capacity",
            MAX_UNCOMPRESSED_BYTES >= 2 * 1024 * 1024 * 1024,
        )
        accept(
            "prove-gzip-expansion-can-fit-without-an-unproven-compressed-cap",
            MAX_ARCHIVE_BYTES
            >= MAX_UNCOMPRESSED_BYTES
            + (MAX_UNCOMPRESSED_BYTES // 512)
            + 1_048_576,
        )
        near_limit_baseline_bound = report_size_upper_bound(
            "baseline",
            MAX_PROCESS_BYTES - 1,
            1,
        )
        near_limit_candidate_bound = report_size_upper_bound(
            "candidate",
            MAX_PROCESS_BYTES - 1,
            1,
        )
        accept(
            "prove-full-limit-baseline-base64-and-stderr-bound",
            0 < near_limit_baseline_bound <= MAX_UNCOMPRESSED_BYTES,
        )
        accept(
            "prove-full-limit-candidate-base64-reference-and-mismatch-bound",
            0 < near_limit_candidate_bound <= MAX_UNCOMPRESSED_BYTES,
        )
        accept(
            "prove-canonical-full-10240-case-matrix-byte-bound",
            len(canonical(matrix)) <= MAX_MATRIX_BYTES,
        )
        for name, stdout_bytes, stderr_bytes in (
            ("empty", 0, 0),
            ("one", 1, 0),
            ("two", 2, 0),
            ("three", 3, 0),
            ("split", MAX_PROCESS_BYTES // 2, MAX_PROCESS_BYTES // 2),
            ("near-limit", MAX_PROCESS_BYTES - 1, 1),
            ("full-limit", MAX_PROCESS_BYTES, 0),
        ):
            accept(
                "prove-near-bound-exact-base64-accounting-" + name,
                report_size_upper_bound(
                    "baseline",
                    stdout_bytes,
                    stderr_bytes,
                ) <= MAX_UNCOMPRESSED_BYTES
                and report_size_upper_bound(
                    "candidate",
                    stdout_bytes,
                    stderr_bytes,
                ) <= MAX_UNCOMPRESSED_BYTES
                and base64_byte_bound(stdout_bytes)
                == 4 * ((stdout_bytes + 2) // 3)
                and base64_byte_bound(stderr_bytes)
                == 4 * ((stderr_bytes + 2) // 3),
            )
        reject(
            "reject-combined-process-stdout-and-stderr-overflow",
            lambda: report_size_upper_bound(
                "candidate",
                MAX_PROCESS_BYTES,
                1,
            ),
        )
        reject(
            "reject-single-process-base64-bound-overflow",
            lambda: base64_byte_bound(MAX_PROCESS_BYTES + 1),
        )
        for nested_shape in WITNESSED_REGRESSION_NESTED_SHAPES:
            selected = [
                case
                for case in matrix
                if case["outer_shape"] == WITNESSED_REGRESSION_OUTER_SHAPE
                and case["nested_shape"] == nested_shape
            ]
            accept(
                "retain-every-witnessed-outer-thirteen-nested-"
                + nested_shape
                + "-case",
                len(selected) == VARIANTS_PER_COHORT
                and all(
                    case["outer_size"] == WITNESSED_REGRESSION_OUTER_SIZE
                    and case["nested_size"] == SHAPE_SIZES[nested_shape]
                    for case in selected
                ),
            )
            accept(
                "retain-every-witnessed-outer-thirteen-nested-"
                + nested_shape
                + "-api-placement-and-failure",
                {
                    (case["api"], case["target"], case["behavior"])
                    for case in selected
                }
                == {
                    (api, target, behavior)
                    for api in APIS
                    for target in TARGETS
                    for behavior in BEHAVIORS
                },
            )

        recorder_pin = hashlib.sha256(
            b"source-only-shape-changing-recorder-v1"
        ).hexdigest()
        sources = synthetic_frozen_source_closure(recorder_pin)
        accept(
            "authenticate-complete-synthetic-original-source-closure",
            validate_frozen_source_closure(sources, recorder_pin) is sources,
        )
        oracle = SyntheticOracle()
        records = synthetic_records(matrix)
        records_pin = digest(records)
        accept(
            "retain-all-10240-complete-synthetic-original-observations",
            oracle.validate_records(
                matrix,
                records,
                records_pin,
            ) is records,
        )
        result = synthetic_baseline_result(matrix, records)
        accept(
            "authenticate-two-distinct-complete-original-reference-workers",
            validate_baseline_result(result, oracle, matrix) is result,
        )
        accept(
            "reject-reference-pid-reuse-by-construction",
            result["reference_a"]["pid"]
            != result["reference_b"]["pid"],
        )
        accept(
            "retain-all-reference-a-events-errors-and-release-records",
            len(result["reference_a"]["records"]) == CASE_COUNT,
        )
        accept(
            "retain-all-reference-b-events-errors-and-release-records",
            len(result["reference_b"]["records"]) == CASE_COUNT,
        )
        accept(
            "authenticate-complete-independent-reference-a-stream",
            decode_stream(
                result["reference_a_process"]["stdout"],
                "synthetic reference a",
            ) == canonical(result["reference_a"]),
        )
        accept(
            "authenticate-complete-independent-reference-b-stream",
            decode_stream(
                result["reference_b_process"]["stdout"],
                "synthetic reference b",
            ) == canonical(result["reference_b"]),
        )

        baseline_label = "source-only-shape-v1"
        baseline_process = synthetic_process_state(
            result,
            pid=8_100,
        )
        baseline_report = build_baseline_report(
            recorder_pin,
            baseline_label,
            baseline_process,
            oracle,
            matrix,
            sources,
            sources,
        )
        accept(
            "preserve-complete-synthetic-baseline-report-without-publication",
            baseline_report["status"] == "PASS"
            and baseline_report["validated_reference_a_case_count"]
            == CASE_COUNT
            and baseline_report["validated_reference_b_case_count"]
            == CASE_COUNT
            and baseline_report["all_failure_reasons"] == [],
        )
        full_scale_baseline_bytes, full_scale_baseline_sha256 = (
            canonical_identity(
                baseline_report,
                baseline_report["mathematical_report_bytes_upper_bound"],
            )
        )
        accept(
            "prove-complete-two-reference-baseline-fits-its-actual-byte-bound",
            0 < full_scale_baseline_bytes
            <= baseline_report["mathematical_report_bytes_upper_bound"]
            <= MAX_UNCOMPRESSED_BYTES,
        )
        accept(
            "preserve-exact-original-worker-stdout-without-duplicated-vectors",
            baseline_report["lossless_evidence_layout"]
            == "one-authenticated-baseline-controller-stdout"
            and baseline_report["duplicate_reference_vectors"] is False
            and not set(baseline_report) & {
                "complete_decoded_baseline_process",
                "complete_baseline_result",
                "reference_a_records",
                "reference_b_records",
                "reference_a_process",
                "reference_b_process",
            }
            and reconstruct_baseline_result(
                baseline_report,
                oracle,
                matrix,
            ) == result,
        )
        baseline_preflight = synthetic_preflight(
            "baseline",
            baseline_label,
        )
        archive_pin = hashlib.sha256(
            b"source-only-shape-compressed-baseline"
        ).hexdigest()
        baseline_publication = synthetic_publication(
            baseline_preflight["report_relative"],
            compressed=True,
            expected=archive_pin,
        )
        baseline_publication["uncompressed_bytes"] = (
            full_scale_baseline_bytes
        )
        baseline_publication["uncompressed_sha256"] = (
            full_scale_baseline_sha256
        )
        baseline_receipt = make_baseline_receipt(
            recorder_pin,
            baseline_label,
            baseline_report,
            baseline_publication,
            baseline_preflight,
        )
        baseline_pins = make_baseline_pins(
            baseline_label,
            hashlib.sha256(canonical(baseline_receipt)).hexdigest(),
            archive_pin,
            records_pin,
        )
        rust_pins = synthetic_owner_pins(
            "rust",
            recorder_pin=recorder_pin,
            baseline=baseline_pins,
        )
        accept(
            "authenticate-complete-two-reference-publication-receipt",
            validate_baseline_receipt(
                baseline_receipt,
                rust_pins,
            ) is baseline_receipt,
        )
        accept(
            "authenticate-all-complete-archived-reference-records",
            validate_archived_baseline(
                baseline_report,
                rust_pins,
                oracle,
                matrix,
                baseline_receipt,
            ) is baseline_report,
        )
        memory_document = canonical({
            "schema": SCHEMA + "-source-only-lossless-gzip",
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
        })
        compressed = gzip.compress(
            memory_document,
            compresslevel=9,
            mtime=0,
        )
        accept(
            "prove-deterministic-lossless-gzip-without-opening-a-file",
            compressed
            == gzip.compress(
                memory_document,
                compresslevel=9,
                mtime=0,
            )
            and gzip.decompress(compressed) == memory_document,
        )

        audit = SyntheticAudit()
        for index, family in enumerate(("rust", "c", "zig"), start=1):
            pins = synthetic_owner_pins(
                family,
                recorder_pin=recorder_pin,
                baseline=baseline_pins,
            )
            spec = family_spec(family)
            closure, manifest = synthetic_native_closure(pins, audit)
            accept(
                "authenticate-complete-owned-" + family + "-v3-native-closure",
                audit.validate_serializable_owners(
                    closure,
                    family,
                    manifest,
                    AUDIT_SHA256,
                ) is closure,
            )
            guard = synthetic_guard(spec)
            accept(
                "authenticate-continuous-" + family + "-v5-native-guard",
                validate_guard(guard, spec) is guard,
            )
            worker = synthetic_candidate_worker(
                pins,
                records,
                pid=9_100 + index,
                audit=audit,
            )
            accept(
                "authenticate-one-independently-isolated-"
                + family
                + "-shape-worker",
                validate_candidate_worker(
                    worker,
                    pins,
                    matrix,
                    expected_pid=9_100 + index,
                    oracle=oracle,
                    audit=audit,
                ) is worker,
            )
            accept(
                "retain-all-10240-complete-" + family + "-shape-observations",
                len(worker["records"]) == CASE_COUNT,
            )
            accept(
                "keep-" + family + "-candidate-pid-distinct-from-references",
                worker["pid"] not in worker["baseline_reference_pids"],
            )
            accept(
                "guard-" + family + "-before-and-after-every-frozen-case",
                guard["actual_method_guard_checks"]
                == guard["actual_warning_registry_guard_checks"]
                == 2 * CASE_COUNT,
            )
            accept(
                "enforce-owned-only-" + family + "-native-ffi",
                guard["owned_native_ffi_allowed"] is (family == "zig"),
            )
            for name in (
                "schema",
                "status",
                "python",
                "role",
                "pid",
                "candidate_family",
                "recorder_source_sha256",
                "oracle_source_sha256",
                "original_v5_sha256",
                "ownership_audit_sha256",
                "matrix_sha256",
                "published_seed",
                "case_count",
                "cohort_count",
                "variants_per_cohort",
                "shape_sizes",
                "witnessed_regression_outer_size",
                "witnessed_regression_nested_sizes",
                "witnessed_regression_case_count",
                "baseline_receipt_relative",
                "baseline_receipt_sha256",
                "baseline_archive_relative",
                "baseline_archive_sha256",
                "baseline_records_sha256",
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
                "validated_prior_reference_workers",
                "actual_reference_workers",
                "actual_candidate_workers",
                "actual_candidate_imports",
                "clock_samples",
                "timing_trials_run",
                "workspace_files_written",
                "evidence_files_created",
                "benchmark_files_read",
                "hidden_cases_read",
                "performance",
                "source_to_binary_reproducibility",
                "candidate_qualified_for_hidden_benchmark",
                "final_winner_selected",
            ):
                forged = dict(worker)
                forged.pop(name, None)
                reject(
                    "reject-omitted-" + family + "-candidate-field-" + name,
                    lambda forged=forged, pins=pins, pid=9_100 + index: (
                        validate_candidate_worker(
                            forged,
                            pins,
                            matrix,
                            expected_pid=pid,
                            oracle=oracle,
                            audit=audit,
                        )
                    ),
                )
            for name in GUARD_TRUE_FIELDS:
                forged = dict(guard)
                forged[name] = False
                reject(
                    "reject-" + family + "-missing-native-guard-" + name,
                    lambda forged=forged, spec=spec: validate_guard(
                        forged,
                        spec,
                    ),
                )
            for name in (
                "actual_method_guard_checks",
                "actual_warning_registry_guard_checks",
            ):
                forged = dict(guard)
                forged[name] -= 1
                reject(
                    "reject-" + family + "-incomplete-case-guard-" + name,
                    lambda forged=forged, spec=spec: validate_guard(
                        forged,
                        spec,
                    ),
                )
            collided = dict(worker)
            collided["pid"] = collided["baseline_reference_pids"][0]
            reject(
                "reject-" + family + "-candidate-reference-pid-collision",
                lambda collided=collided, pins=pins: (
                    validate_candidate_worker(
                        collided,
                        pins,
                        matrix,
                        expected_pid=collided["pid"],
                        oracle=oracle,
                        audit=audit,
                    )
                ),
            )
            for candidate_family in ("rust", "c", "zig"):
                if candidate_family == family:
                    continue
                forged = dict(worker)
                forged["candidate_family"] = candidate_family
                reject(
                    "reject-" + family + "-borrowed-" + candidate_family
                    + "-native-family",
                    lambda forged=forged, pins=pins, pid=9_100 + index: (
                        validate_candidate_worker(
                            forged,
                            pins,
                            matrix,
                            expected_pid=pid,
                            oracle=oracle,
                            audit=audit,
                        )
                    ),
                )

        success_worker = synthetic_candidate_worker(
            rust_pins,
            records,
            pid=9_401,
            audit=audit,
        )
        closure, _ = synthetic_native_closure(rust_pins, audit)
        success_process = synthetic_process_state(
            success_worker,
            pid=success_worker["pid"],
        )
        success_report = build_candidate_report(
            rust_pins,
            "source-only-success-v1",
            success_process,
            matrix,
            baseline_receipt,
            baseline_report,
            closure,
            closure,
            oracle,
            audit,
        )
        accept(
            "validate-all-10240-baseline-to-candidate-record-comparisons",
            success_report["status"] == "PASS"
            and success_report["mismatch_count"] == 0
            and success_report["validated_candidate_record_count"]
            == CASE_COUNT
            and success_report["all_mismatches"] == [],
        )
        accept(
            "preserve-candidate-stdout-once-without-decoded-vector-duplication",
            success_report["lossless_evidence_layout"]
            == "one-authenticated-candidate-worker-stdout-and-full-mismatches"
            and success_report["duplicate_candidate_vectors"] is False
            and success_report["duplicate_reference_vectors"] is False
            and not set(success_report) & {
                "complete_decoded_candidate_process",
                "complete_candidate_result",
                "baseline_records",
                "candidate_records",
            }
            and decode_document(
                decode_stream(
                    success_report["complete_candidate_process_stdout"],
                    "one complete synthetic candidate worker",
                ),
                "one complete decoded synthetic candidate worker",
            ) == success_worker,
        )

        mismatch_records = list(records)
        witnessed_indices: list[int] = []
        for nested_size in WITNESSED_REGRESSION_NESTED_SIZES:
            index = next(
                index
                for index, case in enumerate(matrix)
                if case["outer_size"] == WITNESSED_REGRESSION_OUTER_SIZE
                and case["nested_size"] == nested_size
            )
            witnessed_indices.append(index)
            forged_record = dict(mismatch_records[index])
            forged_record["outcome"] = {
                "status": "contract-violation",
                "violation": {
                    "type": "SyntheticVisibleBufferMismatch",
                    "message": (
                        "outer=13 nested=" + str(nested_size)
                    ),
                },
                "partial_event_ledger": None,
                "partial_callback_ledger": None,
                "partial_warning_ledger": None,
                "complete_case_evidence_available": False,
            }
            mismatch_records[index] = forged_record
        mismatch_worker = synthetic_candidate_worker(
            rust_pins,
            mismatch_records,
            pid=9_402,
            audit=audit,
        )
        mismatch_process = synthetic_process_state(
            mismatch_worker,
            pid=mismatch_worker["pid"],
        )
        mismatch_report = build_candidate_report(
            rust_pins,
            "source-only-witnessed-failures-v1",
            mismatch_process,
            matrix,
            baseline_receipt,
            baseline_report,
            closure,
            closure,
            oracle,
            audit,
        )
        accept(
            "preserve-all-five-actual-witnessed-regression-mismatch-vectors",
            mismatch_report["status"] == "FAIL"
            and mismatch_report["mismatch_count"] == 5
            and len(mismatch_report["all_mismatches"]) == 5
            and mismatch_report[
                "witnessed_regression_mismatches_by_nested_size"
            ] == {
                "0": 1,
                "1": 1,
                "2": 1,
                "5": 1,
                "8": 1,
            }
            and mismatch_report["all_mismatches_preserved"] is True,
        )
        for nested_size in WITNESSED_REGRESSION_NESTED_SIZES:
            observed = [
                item
                for item in mismatch_report["all_mismatches"]
                if item["outer_size"] == 13
                and item["nested_size"] == nested_size
            ]
            accept(
                "retain-complete-witnessed-outer-thirteen-nested-"
                + str(nested_size)
                + "-input-and-both-outcomes",
                len(observed) == 1
                and observed[0]["input"]["outer_size"] == 13
                and observed[0]["input"]["nested_size"] == nested_size
                and observed[0]["baseline_outcome"]["status"] == "return"
                and observed[0]["candidate_outcome"]["status"]
                == "contract-violation",
            )
        failure_preflight = synthetic_preflight(
            "candidate",
            "source-only-witnessed-failures-v1",
            "rust",
        )
        failure_publication = synthetic_publication(
            failure_preflight["report_relative"],
            compressed=True,
        )
        failure_receipt = make_candidate_receipt(
            rust_pins,
            "source-only-witnessed-failures-v1",
            mismatch_report,
            failure_publication,
            failure_preflight,
        )
        accept(
            "never-confuse-successful-publication-with-candidate-correctness",
            failure_receipt["status"] == "PASS"
            and failure_receipt["candidate_result_status"] == "FAIL"
            and failure_receipt["mismatch_count"] == 5
            and failure_receipt["all_mismatches_preserved"] is True,
        )

        all_failure_records: list[dict[str, Any]] = []
        for case, original in zip(
            matrix,
            records,
            strict=True,
        ):
            actual = dict(original)
            actual["outcome"] = {
                "status": "contract-violation",
                "violation": {
                    "type": "SyntheticFullScaleBufferMismatch",
                    "message": case["case"],
                },
                "partial_event_ledger": None,
                "partial_callback_ledger": None,
                "partial_warning_ledger": None,
                "complete_case_evidence_available": False,
            }
            all_failure_records.append(actual)
        full_failure_worker = synthetic_candidate_worker(
            rust_pins,
            all_failure_records,
            pid=9_403,
            audit=audit,
        )
        full_failure_process = synthetic_process_state(
            full_failure_worker,
            pid=full_failure_worker["pid"],
        )
        full_failure_report = build_candidate_report(
            rust_pins,
            "source-only-full-scale-failures-v1",
            full_failure_process,
            matrix,
            baseline_receipt,
            baseline_report,
            closure,
            closure,
            oracle,
            audit,
        )
        full_scale_candidate_bytes, full_scale_candidate_sha256 = (
            canonical_identity(
                full_failure_report,
                full_failure_report[
                    "mathematical_report_bytes_upper_bound"
                ],
            )
        )
        accept(
            "preserve-all-10240-worst-case-complete-candidate-mismatch-vectors",
            full_failure_report["status"] == "FAIL"
            and full_failure_report["mismatch_count"] == CASE_COUNT
            and len(full_failure_report["all_mismatches"]) == CASE_COUNT
            and full_failure_report["validated_candidate_record_count"]
            == CASE_COUNT
            and full_failure_report["all_mismatches_preserved"] is True,
        )
        accept(
            "prove-full-scale-all-case-mismatch-report-fits-actual-byte-bound",
            0 < full_scale_candidate_bytes
            <= full_failure_report[
                "mathematical_report_bytes_upper_bound"
            ]
            <= MAX_UNCOMPRESSED_BYTES,
        )
        accept(
            "preserve-all-64-worst-case-shape-cohorts-without-reweighting",
            full_failure_report["mismatches_by_cohort"]
            == {cohort: VARIANTS_PER_COHORT for cohort in COHORTS},
        )
        accept(
            "preserve-all-five-full-scale-witnessed-regression-cohorts",
            full_failure_report[
                "witnessed_regression_mismatches_by_nested_size"
            ] == {
                "0": VARIANTS_PER_COHORT,
                "1": VARIANTS_PER_COHORT,
                "2": VARIANTS_PER_COHORT,
                "5": VARIANTS_PER_COHORT,
                "8": VARIANTS_PER_COHORT,
            },
        )
        accept(
            "prove-full-failure-report-never-duplicates-worker-vectors",
            full_failure_report["duplicate_candidate_vectors"] is False
            and full_failure_report["duplicate_reference_vectors"] is False
            and not set(full_failure_report) & {
                "complete_decoded_candidate_process",
                "complete_candidate_result",
                "candidate_records",
                "baseline_records",
            },
        )
        full_preflight = synthetic_preflight(
            "candidate",
            "source-only-full-scale-failures-v1",
            "rust",
        )
        full_publication = synthetic_publication(
            full_preflight["report_relative"],
            compressed=True,
        )
        full_publication["uncompressed_bytes"] = (
            full_scale_candidate_bytes
        )
        full_publication["uncompressed_sha256"] = (
            full_scale_candidate_sha256
        )
        full_failure_receipt = make_candidate_receipt(
            rust_pins,
            "source-only-full-scale-failures-v1",
            full_failure_report,
            full_publication,
            full_preflight,
        )
        accept(
            "retain-all-10240-failures-in-an-honest-successful-receipt",
            full_failure_receipt["status"] == "PASS"
            and full_failure_receipt["candidate_result_status"] == "FAIL"
            and full_failure_receipt["mismatch_count"] == CASE_COUNT
            and full_failure_receipt["duplicate_candidate_vectors"] is False
            and full_failure_receipt["duplicate_reference_vectors"] is False,
        )

        source_only_failure = build_failure_document(
            RecorderError("source-only synthetic no-worker failure"),
            [],
            validated_reference_workers=0,
        )
        accept(
            "truthfully-preserve-zero-workers-before-any-process-start",
            source_only_failure["actual_reference_workers"] == 0
            and source_only_failure["actual_reference_worker_count_known"]
            is True
            and source_only_failure["actual_candidate_workers"] == 0
            and source_only_failure["actual_process_context_count"] == 0,
        )
        baseline_context = synthetic_actual_process_context(
            "baseline-controller",
            baseline_process["pid"],
            result,
        )
        unknown_reference_failure = build_failure_document(
            RecorderError(
                "source-only synthetic publication failed after baseline",
            ),
            [baseline_context],
            validated_reference_workers=0,
        )
        accept(
            "never-claim-zero-reference-workers-after-controller-start",
            unknown_reference_failure["actual_reference_workers"] is None
            and unknown_reference_failure[
                "actual_reference_worker_count_known"
            ] is False
            and unknown_reference_failure[
                "actual_baseline_controller_invocations"
            ] == 1
            and unknown_reference_failure[
                "actual_process_context_count"
            ] == 1
            and unknown_reference_failure[
                "actual_process_contexts"
            ][0]["pid"] == baseline_process["pid"],
        )
        accept(
            "retain-complete-real-controller-stream-on-publication-failure",
            decode_stream(
                unknown_reference_failure[
                    "actual_process_contexts"
                ][0]["stdout"],
                "synthetic retained failed controller stdout",
            ) == canonical(result),
        )
        known_reference_failure = build_failure_document(
            RecorderError(
                "source-only synthetic publication failed after verification",
            ),
            [baseline_context],
            validated_reference_workers=2,
        )
        accept(
            "retain-two-validated-references-on-publication-failure",
            known_reference_failure["actual_reference_workers"] == 2
            and known_reference_failure[
                "actual_reference_worker_count_known"
            ] is True
            and known_reference_failure[
                "actual_baseline_controller_invocations"
            ] == 1,
        )
        candidate_context = synthetic_actual_process_context(
            "candidate-worker",
            full_failure_worker["pid"],
            full_failure_worker,
        )
        known_candidate_failure = build_failure_document(
            RecorderError(
                "source-only synthetic publication failed after candidate",
            ),
            [candidate_context],
            validated_reference_workers=0,
        )
        accept(
            "never-claim-zero-candidate-workers-after-native-process-start",
            known_candidate_failure["actual_reference_workers"] == 0
            and known_candidate_failure["actual_candidate_workers"] == 1
            and known_candidate_failure[
                "actual_candidate_process_invocations"
            ] == 1
            and known_candidate_failure["actual_candidate_imports"] is None
            and known_candidate_failure[
                "actual_process_contexts"
            ][0]["pid"] == full_failure_worker["pid"],
        )
        accept(
            "retain-complete-real-candidate-stream-on-publication-failure",
            decode_stream(
                known_candidate_failure[
                    "actual_process_contexts"
                ][0]["stdout"],
                "synthetic retained failed native stdout",
            ) == canonical(full_failure_worker),
        )
        reject(
            "reject-mixed-reference-and-candidate-failure-process-context",
            lambda: build_failure_document(
                RecorderError("forged mixed synthetic process"),
                [baseline_context, candidate_context],
                validated_reference_workers=0,
            ),
        )
        reject(
            "reject-two-validated-references-without-started-controller",
            lambda: build_failure_document(
                RecorderError("forged source-only reference accounting"),
                [],
                validated_reference_workers=2,
            ),
        )

        for name in (
            "schema",
            "status",
            "python",
            "oracle_source_sha256",
            "matrix_sha256",
            "published_seed",
            "case_count",
            "cohort_count",
            "variants_per_cohort",
            "shape_sizes",
            "baseline_records_sha256",
            "source_owners",
            "reference_a",
            "reference_b",
            "reference_a_process",
            "reference_b_process",
            "actual_reference_workers",
            "actual_candidate_workers",
            "actual_candidate_imports",
            "clock_samples",
            "timing_trials_run",
            "workspace_files_written",
            "evidence_files_created",
            "benchmark_files_read",
            "hidden_cases_read",
            "performance",
            "candidate_qualified_for_hidden_benchmark",
            "final_winner_selected",
        ):
            forged = dict(result)
            forged.pop(name, None)
            reject(
                "reject-omitted-two-reference-baseline-field-" + name,
                lambda forged=forged: validate_baseline_result(
                    forged,
                    oracle,
                    matrix,
                ),
            )
        for name in (
            "schema",
            "status",
            "baseline_result_status",
            "recorder_source_sha256",
            "oracle_source_sha256",
            "original_v5_sha256",
            "ownership_audit_sha256",
            "matrix_sha256",
            "published_seed",
            "case_count",
            "shape_sizes",
            "witnessed_regression_outer_size",
            "witnessed_regression_nested_sizes",
            "witnessed_regression_case_count",
            "baseline_records_sha256",
            "validated_reference_a_case_count",
            "validated_reference_b_case_count",
            "baseline_reference_pids",
            "actual_reference_workers",
            "source_closure_before",
            "source_closure_after",
            "source_closure_unchanged",
            "report_relative",
            "report_sha256",
            "report_bytes",
            "report_uncompressed_sha256",
            "report_uncompressed_bytes",
            "report_compression",
            "report_file_fsync_completed",
            "report_directory_fsync_completed",
            "report_atomic_no_overwrite_link",
            "report_complete_readback_verified",
            "receipt_relative",
            "approved_fresh_path_count",
            "fresh_paths_checked_before_baseline",
            "performance",
            "source_to_binary_reproducibility",
            "candidate_qualified_for_hidden_benchmark",
            "final_winner_selected",
        ):
            forged = dict(baseline_receipt)
            forged.pop(name, None)
            reject(
                "reject-omitted-durable-baseline-receipt-field-" + name,
                lambda forged=forged: validate_baseline_receipt(
                    forged,
                    rust_pins,
                ),
            )
        collided_reference = dict(result)
        forged_second = dict(result["reference_b"])
        forged_second["pid"] = result["reference_a"]["pid"]
        collided_reference["reference_b"] = forged_second
        reject(
            "reject-colliding-two-reference-worker-pids",
            lambda: validate_baseline_result(
                collided_reference,
                oracle,
                matrix,
            ),
        )
        forged_receipt = dict(baseline_receipt)
        forged_receipt["baseline_reference_pids"] = [8_101, 8_101]
        reject(
            "reject-colliding-durable-reference-receipt-pids",
            lambda: validate_baseline_receipt(
                forged_receipt,
                rust_pins,
            ),
        )
        for name in ("base64", "bytes", "sha256", "complete"):
            forged = dict(
                result["reference_a_process"]["stdout"],
            )
            if name == "base64":
                forged[name] = "e30="
            elif name == "bytes":
                forged[name] += 1
            elif name == "sha256":
                forged[name] = hashlib.sha256(
                    b"forged-changing-buffer-reference"
                ).hexdigest()
            else:
                forged[name] = False
            reject(
                "reject-incomplete-original-reference-stream-" + name,
                lambda forged=forged: decode_stream(
                    forged,
                    "poisoned original process",
                ),
            )
        for title, poisoned in (
            ("duplicate-json-fields", b'{"case":1,"case":2}\n'),
            ("nonfinite-json", b'{"case":NaN}\n'),
            ("truncated-json", b'{"case":'),
            ("hidden-json-suffix", b'{}\n{}\n'),
            ("noncanonical-json", b'{ "case": 1 }\n'),
            ("empty-json", b""),
        ):
            reject(
                "reject-" + title + "-shape-evidence",
                lambda poisoned=poisoned: decode_document(
                    poisoned,
                    title,
                ),
            )
        for title, mutation in (
            ("missing-first", lambda rows: rows.pop(0)),
            ("missing-last", lambda rows: rows.pop()),
            ("duplicate", lambda rows: rows.__setitem__(1, rows[0])),
            (
                "reordered",
                lambda rows: rows.__setitem__(
                    slice(0, 2),
                    [rows[1], rows[0]],
                ),
            ),
            ("hidden-added", lambda rows: rows.append(rows[0])),
        ):
            forged = list(matrix)
            mutation(forged)
            reject(
                "reject-" + title + "-frozen-shape-matrix",
                lambda forged=forged: validate_matrix(forged),
            )
        for name in (
            "case",
            "cohort",
            "variant",
            "seed",
            "outer_shape",
            "nested_shape",
            "outer_size",
            "nested_size",
            "api",
            "target",
            "behavior",
            "pattern_kind",
            "template_style",
            "flags",
            "count",
            "pos",
            "endpos",
            "pattern_hex",
            "subject",
            "template",
        ):
            forged = list(matrix)
            first = dict(forged[0])
            first.pop(name, None)
            forged[0] = first
            reject(
                "reject-omitted-complete-frozen-shape-case-" + name,
                lambda forged=forged: validate_matrix(forged),
            )
        for title, invalid in (
            ("empty-label", ""),
            ("uppercase-label", "Shape"),
            ("absolute-label", "/shape"),
            ("dot-label", ".shape"),
            ("parent-label", "../shape"),
            ("separator-label", "shape/run"),
            ("backslash-label", "shape\\run"),
            ("double-dash-label", "shape--run"),
            ("trailing-dash-label", "shape-"),
            ("long-label", "s" * 65),
        ):
            reject(
                "reject-" + title,
                lambda invalid=invalid: validate_label(invalid),
            )
        for title, invalid in (
            ("absolute-publication", "/tmp/shape.json"),
            ("parent-escape", "../shape.json"),
            ("empty-component", "experiments//shape"),
            ("dot-component", "experiments/./shape"),
            ("backslash-escape", "experiments\\shape"),
            ("null-escape", "experiments/\x00shape"),
        ):
            reject(
                "reject-" + title,
                lambda invalid=invalid: safe_parts(invalid),
            )
        for name in ("rust", "c", "zig"):
            pins = synthetic_owner_pins(
                name,
                recorder_pin=recorder_pin,
                baseline=baseline_pins,
            )
            for title, operation in (
                (
                    "missing-owned-source",
                    lambda pins=pins: make_owner_pins(
                        pins.family,
                        pins.recorder,
                        pins.adapter,
                        pins.engine,
                        pins.bridge,
                        [
                            relative + "=" + expected
                            for relative, expected
                            in pins.owned_sources[:-1]
                        ],
                        pins.baseline,
                    ),
                ),
                (
                    "wrong-owned-adapter",
                    lambda pins=pins: make_owner_pins(
                        pins.family,
                        pins.recorder,
                        hashlib.sha256(
                            b"foreign-owned-shape-adapter"
                        ).hexdigest(),
                        pins.engine,
                        pins.bridge,
                        [
                            relative + "=" + expected
                            for relative, expected in pins.owned_sources
                        ],
                        pins.baseline,
                    ),
                ),
                (
                    "forged-native-alias",
                    lambda pins=pins: make_owner_pins(
                        pins.family,
                        pins.recorder,
                        pins.adapter,
                        pins.engine,
                        (
                            hashlib.sha256(
                                b"foreign-shape-c-bridge"
                            ).hexdigest()
                            if pins.family == "c"
                            else pins.engine
                        ),
                        [
                            relative + "=" + expected
                            for relative, expected in pins.owned_sources
                        ],
                        pins.baseline,
                    ),
                ),
            ):
                reject(
                    "reject-" + name + "-" + title,
                    operation,
                )
        for title, operation in (
            (
                "file-read",
                lambda: builtins.open("synthetic-changing-buffer"),
            ),
            (
                "descriptor-read",
                lambda: os.open(
                    "synthetic-changing-buffer",
                    os.O_RDONLY,
                ),
            ),
            (
                "hidden-holdout-read",
                lambda: builtins.open(
                    "performance/hidden-changing-buffer-holdout"
                ),
            ),
            (
                "file-write",
                lambda: os.write(1, b"synthetic-changing-buffer"),
            ),
            (
                "candidate-import",
                lambda: importlib.import_module(
                    "candidates.rust_candidate"
                ),
            ),
            (
                "external-engine-import",
                lambda: builtins.__import__("regex"),
            ),
            (
                "frozen-oracle-import",
                lambda: importlib.import_module(ORACLE_MODULE),
            ),
            (
                "reference-worker",
                lambda: subprocess.Popen([PINNED_PYTHON, "-I", "-B"]),
            ),
            (
                "process-delegation",
                lambda: os.system("synthetic-changing-buffer"),
            ),
            (
                "background-thread",
                lambda: threading.Thread().start(),
            ),
            (
                "wall-clock",
                lambda: time.time(),
            ),
            (
                "monotonic-clock",
                lambda: time.monotonic(),
            ),
            (
                "performance-clock",
                lambda: time.perf_counter(),
            ),
            (
                "directory-durability",
                lambda: os.fsync(1),
            ),
            (
                "operating-system-randomness",
                lambda: os.urandom(8),
            ),
            (
                "garbage-collection",
                lambda: gc.collect(),
            ),
        ):
            reject(
                "block-real-" + title,
                operation,
            )
        accept(
            "exercise-every-source-only-side-effect-denial",
            all(count > 0 for count in boundary.blocked.values()),
        )
        accept(
            "explicitly-block-background-thread-execution",
            boundary.blocked["threads"] >= 1,
        )
        accept(
            "explicitly-block-holdout-and-all-file-reads",
            boundary.blocked["file_reads"] >= 3,
        )
        accept(
            "load-zero-candidates-or-external-regular-expression-engines",
            not any(
                name == "candidates"
                or name.startswith("candidates.")
                or name.partition(".")[0]
                in {
                    "_regex",
                    "fancy_regex",
                    "google_re2",
                    "hyperscan",
                    "oniguruma",
                    "pcre",
                    "pcre2",
                    "re2",
                    "regex",
                    "rebar",
                }
                for name in sys.modules
            ),
        )
        accept(
            "start-zero-real-baseline-candidate-or-background-processes",
            ACTUAL_PROCESS_CONTEXTS == []
            and ACTUAL_VALIDATED_REFERENCE_WORKERS == 0,
        )
    verify_runtime(synthetic=True)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "witnessed_regression_outer_size": (
            WITNESSED_REGRESSION_OUTER_SIZE
        ),
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
        "maximum_process_combined_stream_bytes": MAX_PROCESS_BYTES,
        "maximum_matrix_bytes": MAX_MATRIX_BYTES,
        "maximum_report_metadata_bytes": MAX_REPORT_METADATA_BYTES,
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "maximum_report_compressed_bytes": MAX_ARCHIVE_BYTES,
        "near_limit_baseline_report_bytes_upper_bound": (
            near_limit_baseline_bound
        ),
        "near_limit_candidate_report_bytes_upper_bound": (
            near_limit_candidate_bound
        ),
        "full_scale_baseline_uncompressed_bytes": (
            full_scale_baseline_bytes
        ),
        "full_scale_baseline_uncompressed_sha256": (
            full_scale_baseline_sha256
        ),
        "full_scale_all_failure_candidate_uncompressed_bytes": (
            full_scale_candidate_bytes
        ),
        "full_scale_all_failure_candidate_uncompressed_sha256": (
            full_scale_candidate_sha256
        ),
        "full_scale_all_failure_candidate_case_count": CASE_COUNT,
        "duplicate_baseline_reference_vectors": False,
        "duplicate_candidate_vectors": False,
        "positive_control_count": len(accepted),
        "positive_controls": accepted,
        "negative_control_count": len(rejected),
        "negative_controls": rejected,
        "source_only_blocked_operations": dict(boundary.blocked),
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 0,
        "actual_candidate_process_invocations": 0,
        "actual_process_context_count": 0,
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


def parse_arguments(
    arguments: list[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Durably record every frozen changing-buffer reference "
            "and independently owned candidate result"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--self-test",
        action="store_true",
        help="run only completely effect-blocked synthetic controls",
    )
    modes.add_argument(
        "--record-baseline",
        action="store_true",
        help="publish exactly two isolated original CPython references",
    )
    modes.add_argument(
        "--record-candidate",
        action="store_true",
        help="publish one independently owned guarded native candidate",
    )
    modes.add_argument(
        "--internal-candidate-worker",
        action="store_true",
        help=argparse.SUPPRESS,
    )
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
    parser.add_argument(
        "--owned-source-sha256",
        action="append",
        default=[],
    )
    return parser.parse_args(arguments)


def make_cli_pins(options: argparse.Namespace) -> OwnerPins:
    require(
        validate_digest(
            options.oracle_source_sha256,
            "frozen changing-buffer oracle",
        ) == ORACLE_SHA256
        and validate_digest(
            options.matrix_sha256,
            "frozen changing-buffer property matrix",
        ) == MATRIX_SHA256
        and validate_digest(
            options.ownership_audit_source_sha256,
            "immutable V3 no-delegation audit",
        ) == AUDIT_SHA256,
        "explicitly pin the immutable changing-buffer oracle, matrix, and audit",
    )
    baseline = make_baseline_pins(
        options.baseline_label,
        options.baseline_receipt_sha256,
        options.baseline_archive_sha256,
        options.baseline_records_sha256,
    )
    return make_owner_pins(
        options.candidate,
        options.recorder_source_sha256,
        options.candidate_source_sha256,
        options.native_engine_sha256,
        options.native_bridge_sha256,
        options.owned_source_sha256,
        baseline,
    )


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(
                options.label is None
                and options.candidate is None
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
                "source-only shape recorder controls cannot select a real "
                "file, candidate, reference, or evidence",
            )
            result = source_self_test()
        elif options.record_baseline:
            require(
                options.candidate is None
                and options.ownership_audit_source_sha256 is None
                and options.baseline_label is None
                and options.baseline_receipt_sha256 is None
                and options.baseline_archive_sha256 is None
                and options.baseline_records_sha256 is None
                and options.candidate_source_sha256 is None
                and options.native_engine_sha256 is None
                and options.native_bridge_sha256 is None
                and options.owned_source_sha256 == [],
                "an isolated original shape baseline cannot select a "
                "candidate, audit, native library, or existing evidence",
            )
            result = record_baseline(
                options.recorder_source_sha256,
                options.oracle_source_sha256,
                options.matrix_sha256,
                options.label,
            )
        else:
            pins = make_cli_pins(options)
            if options.internal_candidate_worker:
                require(
                    options.label is None,
                    "one isolated shape candidate worker cannot publish",
                )
                result = execute_candidate_worker(pins)
            else:
                require(
                    options.record_candidate is True,
                    "select exactly one genuine candidate recording mode",
                )
                result = record_candidate(
                    pins,
                    options.label,
                )
        sys.stdout.buffer.write(canonical(result))
        return 0 if result.get("status") in {"PASS", "OBSERVED"} else 1
    except (
        RecorderError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        OverflowError,
        EOFError,
        gzip.BadGzipFile,
    ) as error:
        failure = build_failure_document(
            error,
            ACTUAL_PROCESS_CONTEXTS,
            validated_reference_workers=(
                ACTUAL_VALIDATED_REFERENCE_WORKERS
            ),
        )
        sys.stdout.buffer.write(canonical(failure))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
