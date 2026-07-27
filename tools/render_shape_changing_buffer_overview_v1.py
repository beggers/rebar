#!/usr/bin/env python3
"""Safely graph the independently frozen 10,240 changing-buffer checks.

The immutable inputs manifest is authored and frozen separately.  This
renderer authenticates the complete, lossless two-worker Python baseline
and any genuinely observed, independently owned Rust, C, or Zig results.
It never substitutes publication for a passing result, never changes the
10,240-case denominator, and never discards a historical failure.

Actual publication is confined to the two exact generated files.  Both are
staged and either committed together or restored together.  An existing pair
can be replaced only with explicit, authenticated hashes for both old files.
The hostile self-test is entirely in memory: files, workers, imports,
threads, clocks, randomness, and real publication are actively blocked.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import builtins
import codecs
import contextlib
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
import zlib
from collections.abc import Callable, Iterator, Mapping
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/render_shape_changing_buffer_overview_v1.py"
SCHEMA = "rebar-shape-changing-buffer-overview-v1"
MANIFEST_RELATIVE = (
    "docs/evidence/shape-changing-buffer-overview-v1.inputs.json"
)
SVG_RELATIVE = "docs/evidence/shape-changing-buffer-overview-v1.svg"
SUMMARY_RELATIVE = "docs/evidence/shape-changing-buffer-overview-v1.json"
EVIDENCE_DIRECTORY = "experiments/rust_public_practice_v1"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
ORACLE_RELATIVE = "tools/independent_shape_changing_buffer_semantics_v1.py"
ORACLE_SHA256 = (
    "866dbf7bf4a48a867b3aaacd05cfa4f1346c747931543fa386835e783f0073aa"
)
ORACLE_SCHEMA = "rebar-independent-shape-changing-buffer-semantics-v1"
RECORDER_RELATIVE = (
    "tools/record_independent_shape_changing_buffer_semantics_v1.py"
)
RECORDER_SHA256 = (
    "047bcc25a3b033fa374576c434b0e6ebcc6c97cf99965e9cc9083c012249529c"
)
RECORDER_SCHEMA = (
    "rebar-independent-shape-changing-buffer-semantics-recorder-v1"
)
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
V2_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
V2_SHA256 = (
    "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
)
MATRIX_SHA256 = (
    "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8"
)
PUBLISHED_SEED = 6_001_118_316_486_346_290
BASELINE_LABEL = "shared-suite-v1"
BASELINE_STEM = (
    EVIDENCE_DIRECTORY + "/shape-changing-buffer-semantics-v1-"
    + BASELINE_LABEL
)
BASELINE_ARCHIVE_RELATIVE = BASELINE_STEM + ".json.gz"
BASELINE_ARCHIVE_SHA256 = (
    "8bf48813d82966edbed05330ce26f6c8a3d80ee72c59a6dbfa104ff397906b5b"
)
BASELINE_ARCHIVE_BYTES = 11_933_273
BASELINE_RECEIPT_RELATIVE = BASELINE_STEM + "-publication-receipt.json"
BASELINE_RECEIPT_SHA256 = (
    "8744ebf8fb29924661d8c379b3fa1d7662e6dd44ebca49ecd7d37219f06ac7c9"
)
BASELINE_REPORT_SHA256 = (
    "8605fd0dd72e505f58eac0a6ea79ff4a5b9f21d0a0415ee1404aca6a848c0552"
)
BASELINE_REPORT_BYTES = 179_411_616
BASELINE_RECORDS_SHA256 = (
    "0aeddfa2835be5895bc6d88edae5ecc4945241c7ea456c0487497be4c47f8373"
)
SHAPE_NAMES = (
    "zero", "one", "two", "short", "five", "equal", "thirteen", "long",
)
SHAPE_SIZES = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "short": 3,
    "five": 5,
    "equal": 8,
    "thirteen": 13,
    "long": 19,
}
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
    "subject-direct", "subject-wrapped", "template-direct",
    "template-wrapped", "both-direct", "both-wrapped",
    "callback-return", "callback-error",
)
BEHAVIORS = ("stable", "mutate", "fail-outer", "fail-nested")
PATTERN_KINDS = (
    "captures", "zero-lookahead", "empty", "optional-captures",
)
TEMPLATE_STYLES = ("literal", "named", "numeric", "invalid", "missing")
FLAGS = (0, 2, 256, 258)
COUNTS = (0, 1, 2, 7)
WINDOW_STARTS = (
    -4, -1, 0, 1, 2, 3, 5, 8, 13, 19, 32, 2_147_483_647,
)
WINDOW_ENDS = (
    0, 1, 2, 3, 5, 8, 13, 19, 32, None, 2_147_483_647,
)
WITNESSED_OUTER_SIZE = 13
WITNESSED_NESTED_SIZES = (0, 1, 2, 5, 8)
VARIANTS_PER_COHORT = 160
CASE_COUNT = 10_240
WITNESSED_CASE_COUNT = 800
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_RECEIPT_BYTES = 8 * 1024 * 1024
MAX_PROCESS_BYTES = 512 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
MAX_ARCHIVE_BYTES = (
    MAX_UNCOMPRESSED_BYTES + MAX_UNCOMPRESSED_BYTES // 512 + 1_048_576
)
MAX_SELECTED_VALUE_BYTES = 768 * 1024 * 1024
CHUNK_BYTES = 131_072
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
FAMILY_ORDER = ("rust", "c", "zig")
FAMILY_LABELS = {
    "python": "Python baseline",
    "rust": "Rust",
    "c": "C",
    "zig": "Zig",
}
FAMILY_SPECS: dict[str, tuple[str, str, str, tuple[str, ...], bool]] = {
    "rust": (
        "candidates/rust_candidate.py",
        "candidates/_rust_engine.so",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
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
        False,
    ),
    "c": (
        "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
        False,
    ),
    "zig": (
        "candidates/zig_candidate.py",
        "candidates/_zig_probe.so",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
        True,
    ),
}
PINNED_STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/"
)
PINNED_STDLIB_SOURCES = {
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
}
TRUSTED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
GUARD_TRUE = (
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
GUARD_COUNTERS = (
    "cached_original_matcher_descendant_count",
    "cached_original_holder_count",
    "owned_ctypes_load_count",
    "owned_ctypes_symbol_count",
)
FORBIDDEN_ROOTS = frozenset({
    "candidates", "_regex", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "rebar", "regex",
    "rust_regex", "sre_compile", "sre_constants", "sre_parse",
    "vectorscan",
})


class OverviewError(Exception):
    """Frozen changing-buffer evidence was omitted, substituted, or forged."""


class SourceOnlyError(OverviewError):
    """An in-memory graph control attempted an actual external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OverviewError(message)


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
        raise OverviewError(
            "complete canonical changing-buffer evidence is mandatory",
        ) from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_hash(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(item in "0123456789abcdef" for item in value),
        "an exact noninvented lowercase SHA-256 is mandatory: " + label,
    )
    return value


def fixed_fields(
    value: Mapping[str, Any],
    expected: Mapping[str, Any],
    label: str,
) -> None:
    for name, original in expected.items():
        actual = value.get(name)
        require(
            type(actual) is type(original) and actual == original,
            label + " changed: " + name,
        )


def safe_parts(value: Any) -> tuple[str, ...]:
    require(
        type(value) is str
        and bool(value)
        and "\\" not in value
        and "\x00" not in value,
        "an exact safe relative changing-buffer path is mandatory",
    )
    parts = tuple(value.split("/"))
    require(
        all(part not in {"", ".", ".."} for part in parts)
        and "/".join(parts) == value,
        "a changing-buffer path escapes the independently approved root",
    )
    return parts


def validate_label(value: Any) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    require(
        type(value) is str
        and 1 <= len(value) <= 64
        and value[0] in alphabet
        and value[-1] in alphabet
        and all(item in alphabet + "-" for item in value)
        and "--" not in value,
        "an exact bounded changing-buffer evidence label is mandatory",
    )
    return value


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in items:
        require(
            type(name) is str and name not in result,
            "a duplicate JSON field hides a real changing-buffer failure",
        )
        result[name] = value
    return result


def decode_document(
    raw: Any,
    label: str,
    maximum: int = MAX_RECEIPT_BYTES,
) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= maximum,
        "complete bounded canonical evidence is mandatory: " + label,
    )

    def reject_nonfinite(_: str) -> None:
        raise OverviewError("nonfinite changing-buffer evidence is forbidden")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_object,
            parse_constant=reject_nonfinite,
        )
    except (
        OverviewError,
        TypeError,
        ValueError,
        UnicodeError,
        RecursionError,
    ) as error:
        raise OverviewError(
            "invalid complete changing-buffer evidence: " + label,
        ) from error
    require(
        type(value) is dict and canonical(value) == raw,
        "changing-buffer evidence was truncated, reordered, or gained a suffix",
    )
    return value


def shape_bytes(base: bytes, size: int, suffix: bytes) -> bytes:
    require(
        type(base) is bytes
        and bool(base)
        and type(size) is int
        and size >= 0
        and type(suffix) is bytes,
        "an independently sized legal outer or nested buffer is mandatory",
    )
    if size == 0:
        return b""
    result = base + suffix
    while len(result) < size:
        result += base
    return result[:size]


def bytes_descriptor(value: bytes) -> dict[str, Any]:
    require(type(value) is bytes, "an exact original bytes carrier is mandatory")
    return {"kind": "bytes", "hex": value.hex()}


def exporter_descriptor(
    role: str,
    outer: str,
    nested: str,
    outer_value: bytes,
    nested_value: bytes,
    behavior: str,
    wrapped: bool,
) -> dict[str, Any]:
    require(
        role in {"subject", "template"}
        and outer in SHAPE_SIZES
        and nested in SHAPE_SIZES
        and type(outer_value) is bytes
        and type(nested_value) is bytes
        and len(outer_value) == SHAPE_SIZES[outer]
        and len(nested_value) == SHAPE_SIZES[nested]
        and behavior in BEHAVIORS
        and type(wrapped) is bool,
        "a genuine independently changing PEP-688 buffer was substituted",
    )
    return {
        "kind": "shape-exporter",
        "role": role,
        "outer_shape": outer,
        "nested_shape": nested,
        "outer_size": len(outer_value),
        "nested_size": len(nested_value),
        "outer_hex": outer_value.hex(),
        "nested_hex": nested_value.hex(),
        "behavior": behavior,
        "wrapped": wrapped,
    }


def build_matrix() -> list[dict[str, Any]]:
    seeded = random.Random(PUBLISHED_SEED)
    rows: list[dict[str, Any]] = []
    patterns = {
        "captures": rb"(?P<word>[a-z]+)(?P<number>[0-9]*)",
        "zero-lookahead": (
            rb"(?=(?P<word>[a-z]*)(?P<number>[0-9]*))"
        ),
        "empty": rb"(?P<word>)(?P<number>)",
        "optional-captures": (
            rb"(?P<word>[a-z]+)?(?P<number>[0-9]+)?"
        ),
    }
    templates = {
        "literal": b"X",
        "named": rb"<\g<word>:\g<number>>",
        "numeric": rb"<\1:\2>",
        "invalid": rb"\q",
        "missing": rb"\g<absent>",
    }
    for outer in SHAPE_NAMES:
        for nested in SHAPE_NAMES:
            cohort = "outer-" + outer + "-nested-" + nested
            for variant in range(VARIANTS_PER_COHORT):
                noise = "".join(
                    seeded.choice("abcdef0123456789")
                    for _ in range(12)
                ).encode("ascii")
                api = APIS[variant % len(APIS)]
                target = TARGETS[
                    (variant // len(APIS)) % len(TARGETS)
                ]
                behavior = BEHAVIORS[
                    (
                        variant // (len(APIS) * len(TARGETS))
                    ) % len(BEHAVIORS)
                ]
                outer_subject = shape_bytes(
                    b"OUTERalpha42", SHAPE_SIZES[outer], noise,
                )
                nested_subject = shape_bytes(
                    b"aa12bb34cc56dd78xyz", SHAPE_SIZES[nested], noise,
                )
                outer_template = shape_bytes(
                    b"OUTER-template", SHAPE_SIZES[outer], noise,
                )
                nested_template = shape_bytes(
                    rb"<\g<word>:\g<number>>",
                    SHAPE_SIZES[nested],
                    noise,
                )
                wrapped = target.endswith("-wrapped")
                subject: dict[str, Any] = bytes_descriptor(nested_subject)
                template: dict[str, Any] = bytes_descriptor(b"X")
                if target.startswith(
                    ("subject-", "both-", "callback-"),
                ):
                    subject = exporter_descriptor(
                        "subject",
                        outer,
                        nested,
                        outer_subject,
                        nested_subject,
                        behavior,
                        wrapped,
                    )
                if target.startswith(("template-", "both-")):
                    template = exporter_descriptor(
                        "template",
                        outer,
                        nested,
                        outer_template,
                        nested_template,
                        behavior,
                        wrapped,
                    )
                if target in {"callback-return", "callback-error"}:
                    template = {
                        "kind": "callable",
                        "hex": b"X".hex(),
                        "raises": target == "callback-error",
                    }
                pattern_kind = PATTERN_KINDS[
                    variant % len(PATTERN_KINDS)
                ]
                template_style = TEMPLATE_STYLES[
                    (
                        variant // len(PATTERN_KINDS)
                    ) % len(TEMPLATE_STYLES)
                ]
                if template["kind"] == "bytes":
                    template = bytes_descriptor(
                        templates[template_style],
                    )
                rows.append({
                    "case": (
                        "shape-changing-buffer-semantics.v1."
                        + format(len(rows), "05d")
                    ),
                    "cohort": cohort,
                    "variant": variant,
                    "seed": PUBLISHED_SEED,
                    "outer_shape": outer,
                    "nested_shape": nested,
                    "outer_size": SHAPE_SIZES[outer],
                    "nested_size": SHAPE_SIZES[nested],
                    "api": api,
                    "target": target,
                    "behavior": behavior,
                    "pattern_kind": pattern_kind,
                    "template_style": template_style,
                    "flags": FLAGS[variant % len(FLAGS)],
                    "count": COUNTS[
                        (variant // len(APIS)) % len(COUNTS)
                    ],
                    "pos": WINDOW_STARTS[
                        variant % len(WINDOW_STARTS)
                    ],
                    "endpos": WINDOW_ENDS[
                        (
                            variant // len(WINDOW_STARTS)
                        ) % len(WINDOW_ENDS)
                    ],
                    "pattern_hex": patterns[pattern_kind].hex(),
                    "subject": subject,
                    "template": template,
                })
    require(
        len(rows) == CASE_COUNT
        and len(COHORTS) == 64
        and len(set(COHORTS)) == 64
        and VARIANTS_PER_COHORT
        == len(APIS) * len(TARGETS) * len(BEHAVIORS)
        and WITNESSED_CASE_COUNT
        == len(WITNESSED_NESTED_SIZES) * VARIANTS_PER_COHORT
        and digest(rows) == MATRIX_SHA256,
        "the independently frozen 10,240-case changing-buffer matrix changed",
    )
    return rows


def exact_hex(value: Any, label: str) -> bytes:
    require(
        type(value) is str
        and len(value) % 2 == 0
        and all(item in "0123456789abcdef" for item in value),
        "a complete canonical visible-buffer payload is mandatory: " + label,
    )
    try:
        decoded = bytes.fromhex(value)
    except ValueError as error:
        raise OverviewError(
            "a genuine changing-buffer payload was substituted: " + label,
        ) from error
    require(
        decoded.hex() == value,
        "a visible-buffer payload was not canonical: " + label,
    )
    return decoded


def validate_normalized(value: Any) -> None:
    require(
        type(value) is dict and type(value.get("type")) is str,
        "an exact typed changing-buffer result is mandatory",
    )
    kind = value["type"]
    if kind == "none":
        require(set(value) == {"type"}, "a genuine empty result was forged")
    elif kind in {"bool", "int", "str"}:
        expected = {"bool": bool, "int": int, "str": str}[kind]
        require(
            set(value) == {"type", "value"}
            and type(value.get("value")) is expected,
            "a genuine scalar, offset, or replacement was forged",
        )
    elif kind in {"bytes", "bytearray"}:
        require(
            set(value) == {"type", "hex"},
            "a genuine bytes-like replacement was truncated",
        )
        exact_hex(value["hex"], "normalized bytes")
    elif kind in {"tuple", "list"}:
        require(
            set(value) == {"type", "items"}
            and type(value.get("items")) is list,
            "a capture or substitution result was hidden",
        )
        for item in value["items"]:
            validate_normalized(item)
    elif kind == "dict":
        require(
            set(value) == {"type", "items"}
            and type(value.get("items")) is list,
            "an exact original mapping result was omitted",
        )
        previous: bytes | None = None
        for pair in value["items"]:
            require(
                type(pair) is list and len(pair) == 2,
                "a complete original mapping item was hidden",
            )
            validate_normalized(pair[0])
            validate_normalized(pair[1])
            current = canonical(pair[0])
            require(
                previous is None or previous < current,
                "an exact original mapping item was reordered",
            )
            previous = current
    elif kind == "memoryview":
        require(
            set(value) == {
                "type", "hex", "readonly", "format", "itemsize", "ndim",
                "shape", "strides", "contiguous", "c_contiguous",
                "f_contiguous",
            }
            and type(value.get("readonly")) is bool
            and type(value.get("format")) is str
            and type(value.get("itemsize")) is int
            and type(value.get("ndim")) is int
            and all(
                type(value.get(name)) is bool
                for name in (
                    "contiguous", "c_contiguous", "f_contiguous",
                )
            ),
            "a genuine returned buffer shape was omitted",
        )
        exact_hex(value["hex"], "normalized memoryview")
        for name in ("shape", "strides"):
            item = value[name]
            require(
                item is None
                or (
                    type(item) is list
                    and all(type(number) is int for number in item)
                ),
                "a genuine returned buffer dimension was hidden",
            )
    elif kind == "released-memoryview":
        require(
            set(value) == {
                "type", "exception_module", "exception_type",
                "exception_args",
            }
            and type(value.get("exception_module")) is str
            and type(value.get("exception_type")) is str,
            "an exact released-buffer exception was hidden",
        )
        validate_normalized(value["exception_args"])
    elif kind == "shape-exporter":
        require(
            set(value) == {
                "type", "role", "outer_size", "nested_size", "outer_hex",
                "nested_hex", "outer_active", "nested_active",
                "behavior",
            }
            and value.get("role") in {"subject", "template"}
            and value.get("behavior") in BEHAVIORS
            and all(
                type(value.get(name)) is int and value[name] >= 0
                for name in (
                    "outer_size", "nested_size", "outer_active",
                    "nested_active",
                )
            ),
            "an actual outer or nested buffer owner was substituted",
        )
        require(
            len(exact_hex(value["outer_hex"], "outer owner"))
            == value["outer_size"]
            and len(exact_hex(value["nested_hex"], "nested owner"))
            == value["nested_size"],
            "an original buffer's actual visible size was concealed",
        )
    else:
        raise OverviewError(
            "an unfrozen changing-buffer result type was injected",
        )


def validate_error(value: Any) -> None:
    require(type(value) is dict, "a complete real exception is mandatory")
    if value.get("kind") == "ordinary-python-error":
        require(
            set(value) == {
                "kind", "module", "type", "message", "args",
            }
            and all(
                type(value.get(name)) is str
                for name in ("module", "type", "message")
            ),
            "a genuine buffer exception class or message was hidden",
        )
        validate_normalized(value["args"])
        return
    require(
        value.get("kind") == "public-regex-error"
        and set(value) == {
            "kind", "type", "args", "message", "pattern",
            "position", "line", "column",
        }
        and type(value.get("type")) is str,
        "an original PatternError and its positions were omitted",
    )
    for name in (
        "args", "message", "pattern", "position", "line", "column",
    ):
        validate_normalized(value[name])


def validate_match(value: Any) -> None:
    require(
        type(value) is dict
        and set(value) == {
            "pattern_is_expected", "string_is_subject",
            "visible_nested_length", "group", "groups", "groupdict",
            "regs", "lastindex", "lastgroup", "pos", "endpos",
            "capture_offset_checks",
        }
        and value.get("pattern_is_expected") is True
        and value.get("string_is_subject") is True
        and type(value.get("visible_nested_length")) is int
        and value["visible_nested_length"] >= 0
        and type(value.get("capture_offset_checks")) is list,
        "a genuine callback match or visible capture was hidden",
    )
    for name in (
        "group", "groups", "groupdict", "regs", "lastindex",
        "lastgroup", "pos", "endpos",
    ):
        validate_normalized(value[name])
    for index, check in enumerate(value["capture_offset_checks"]):
        require(
            type(check) is dict
            and set(check) == {
                "group", "start", "end", "missing",
                "within_visible_nested_buffer",
            }
            and type(check.get("group")) is int
            and check["group"] == index
            and type(check.get("start")) is int
            and type(check.get("end")) is int
            and type(check.get("missing")) is bool
            and type(check.get("within_visible_nested_buffer")) is bool
            and check["missing"] is (
                check["start"] == -1 and check["end"] == -1
            )
            and check["within_visible_nested_buffer"] is (
                check["missing"]
                or 0 <= check["start"] <= check["end"]
                <= value["visible_nested_length"]
            )
            and check["within_visible_nested_buffer"] is True,
            "a capture escaped the actual independently sized buffer",
        )


def validate_events(value: Any) -> list[dict[str, Any]]:
    require(
        type(value) is list,
        "the complete ordered buffer acquisition ledger is mandatory",
    )
    active = {
        (role, owner): 0
        for role in ("subject", "template")
        for owner in ("outer", "nested")
    }
    for event in value:
        require(
            type(event) is dict and type(event.get("event")) is str,
            "a genuine buffer event was forged",
        )
        kind = event["event"]
        if kind == "phase":
            require(
                set(event) == {"event", "name"}
                and type(event.get("name")) is str
                and bool(event["name"]),
                "a genuine substitution phase was omitted",
            )
            continue
        if kind == "callback":
            require(
                set(event) == {"event", "index", "raises", "match"}
                and type(event.get("index")) is int
                and event["index"] >= 0
                and type(event.get("raises")) is bool,
                "a genuine replacement callback was omitted",
            )
            validate_match(event["match"])
            continue
        require(
            set(event) == {
                "event", "role", "owner", "flags", "active_before",
                "active_after", "outer_size", "nested_size", "outer_hex",
                "nested_hex", "behavior",
            }
            and kind in {
                "acquire", "acquire-error", "acquire-unwind", "release",
                "length-probe",
            }
            and event.get("role") in {"subject", "template"}
            and event.get("owner") in {"outer", "nested"}
            and event.get("behavior") in BEHAVIORS
            and all(
                type(event.get(name)) is int and event[name] >= 0
                for name in (
                    "active_before", "active_after", "outer_size",
                    "nested_size",
                )
            )
            and len(exact_hex(event["outer_hex"], "outer event"))
            == event["outer_size"]
            and len(exact_hex(event["nested_hex"], "nested event"))
            == event["nested_size"],
            "a genuine nested size, acquisition, or release was hidden",
        )
        identity = (event["role"], event["owner"])
        require(
            event["active_before"] == active[identity],
            "a genuine nested buffer acquisition was reordered",
        )
        if kind == "acquire":
            require(
                type(event["flags"]) is int
                and event["flags"] in {0, 284}
                and event["active_after"] == active[identity] + 1,
                "a SIMPLE or FULL buffer acquisition was forged",
            )
            active[identity] += 1
        elif kind == "acquire-error":
            require(
                type(event["flags"]) is int
                and event["flags"] in {0, 284}
                and event["active_after"] == active[identity]
                and (
                    (
                        event["owner"] == "outer"
                        and event["behavior"] == "fail-outer"
                    )
                    or (
                        event["owner"] == "nested"
                        and event["behavior"] == "fail-nested"
                    )
                ),
                "an actual outer or nested acquisition failure was hidden",
            )
        elif kind in {"release", "acquire-unwind"}:
            require(
                event["flags"] is None
                and active[identity] > 0
                and event["active_after"] == active[identity] - 1,
                "a genuine buffer release or failure unwind was hidden",
            )
            active[identity] -= 1
        else:
            require(
                event["flags"] is None
                and event["owner"] == "outer"
                and event["active_after"] == active[identity],
                "a genuine original outer-length probe was hidden",
            )
    return value


def validate_outcome(value: Any, *, candidate: bool = False) -> None:
    require(
        type(value) is dict and type(value.get("status")) is str,
        "a complete source-ordered changing-buffer result is mandatory",
    )
    if value["status"] == "contract-violation":
        require(
            candidate
            and set(value) == {
                "status", "violation", "partial_event_ledger",
                "partial_callback_ledger", "partial_warning_ledger",
                "complete_case_evidence_available",
            }
            and type(value.get("violation")) is dict
            and set(value["violation"]) == {"type", "message"}
            and type(value["violation"].get("type")) is str
            and type(value["violation"].get("message")) is str
            and value["partial_event_ledger"] is None
            and value["partial_callback_ledger"] is None
            and value["partial_warning_ledger"] is None
            and value["complete_case_evidence_available"] is False,
            "a real candidate contract violation was hidden",
        )
        return
    require(
        set(value) == {
            "status", "stage", "value", "exception", "events",
            "callbacks", "warnings", "subject_after", "template_after",
            "subject_outer_active", "subject_nested_active",
            "template_outer_active", "template_nested_active",
            "count_requested", "pos_requested", "endpos_requested",
            "outer_size", "nested_size",
        }
        and value["status"] in {"return", "raise"}
        and type(value.get("stage")) is str
        and type(value.get("callbacks")) is list
        and type(value.get("warnings")) is list
        and type(value.get("count_requested")) is int
        and type(value.get("pos_requested")) is int
        and (
            value.get("endpos_requested") is None
            or type(value.get("endpos_requested")) is int
        )
        and type(value.get("outer_size")) is int
        and value["outer_size"] >= 0
        and type(value.get("nested_size")) is int
        and value["nested_size"] >= 0,
        "a complete changing-size result, error, or offset was omitted",
    )
    events = validate_events(value["events"])
    for role, owner, name in (
        ("subject", "outer", "subject_outer_active"),
        ("subject", "nested", "subject_nested_active"),
        ("template", "outer", "template_outer_active"),
        ("template", "nested", "template_nested_active"),
    ):
        count = value.get(name)
        require(
            type(count) is int and count >= 0,
            "an actual live exporter counter was forged",
        )
        acquired = sum(
            event.get("event") == "acquire"
            and event.get("role") == role
            and event.get("owner") == owner
            for event in events
        )
        released = sum(
            event.get("event") in {"release", "acquire-unwind"}
            and event.get("role") == role
            and event.get("owner") == owner
            for event in events
        )
        require(
            count == acquired - released,
            "an original nested buffer lifetime was hidden: " + name,
        )
    validate_normalized(value["subject_after"])
    validate_normalized(value["template_after"])
    if value["status"] == "return":
        require(
            value["exception"] is None,
            "a successful replacement concealed an exception",
        )
        validate_normalized(value["value"])
    else:
        require(
            value["value"] is None,
            "a failing replacement concealed a successful result",
        )
        validate_error(value["exception"])
    for callback in value["callbacks"]:
        require(
            type(callback) is dict
            and set(callback) == {"event", "index", "raises", "match"}
            and callback.get("event") == "callback"
            and type(callback.get("index")) is int
            and type(callback.get("raises")) is bool,
            "a genuine changing-buffer callback was omitted",
        )
        validate_match(callback["match"])
    require(
        [
            event for event in events if event.get("event") == "callback"
        ] == value["callbacks"],
        "a real replacement callback was removed from its event order",
    )
    for warning in value["warnings"]:
        require(
            type(warning) is dict
            and set(warning) == {
                "category_module", "category", "message",
            }
            and all(type(warning.get(name)) is str for name in warning),
            "a complete original Python warning was omitted",
        )


RecordDigest = Callable[[Any], str]


def validate_records(
    matrix: list[dict[str, Any]],
    records: Any,
    expected: Any,
    *,
    candidate: bool = False,
    record_digest: RecordDigest = digest,
) -> list[dict[str, Any]]:
    expected = valid_hash(expected, "all 10,240 source-ordered outcomes")
    require(
        type(records) is list and len(records) == CASE_COUNT,
        "all 10,240 genuine changing-size buffer results are mandatory",
    )
    for case, record in zip(matrix, records, strict=True):
        require(
            type(record) is dict
            and set(record) == {
                "case", "cohort", "api", "outer_size", "nested_size",
                "outcome",
            }
            and record.get("case") == case["case"]
            and record.get("cohort") == case["cohort"]
            and record.get("api") == case["api"]
            and type(record.get("outer_size")) is int
            and record["outer_size"] == case["outer_size"]
            and type(record.get("nested_size")) is int
            and record["nested_size"] == case["nested_size"],
            "a real buffer case, visible size, or source order was concealed",
        )
        outcome = record["outcome"]
        validate_outcome(outcome, candidate=candidate)
        if outcome["status"] != "contract-violation":
            require(
                outcome["outer_size"] == case["outer_size"]
                and outcome["nested_size"] == case["nested_size"]
                and outcome["count_requested"] == case["count"]
                and outcome["pos_requested"] == case["pos"]
                and outcome["endpos_requested"] == case["endpos"],
                "an original backing size or search window was substituted",
            )
    require(
        record_digest(records) == expected,
        "the complete changing-buffer outcome vector failed its SHA-256",
    )
    return records


def validate_owner(
    value: Any,
    relative: str,
    expected: str,
    *,
    external: bool = False,
) -> dict[str, Any]:
    name = "path" if external else "relative"
    require(
        type(value) is dict
        and set(value) == {name, "sha256", "bytes", "device", "inode"}
        and value.get(name) == relative
        and value.get("sha256") == valid_hash(expected, relative)
        and type(value.get("bytes")) is int
        and value["bytes"] > 0
        and type(value.get("device")) is int
        and value["device"] >= 0
        and type(value.get("inode")) is int
        and value["inode"] > 0,
        "an independently frozen source or native owner was forged: "
        + relative,
    )
    return value


def validate_tool_closure(value: Any) -> dict[str, Any]:
    expected = {
        "recorder": (RECORDER_RELATIVE, RECORDER_SHA256),
        "shape_oracle": (ORACLE_RELATIVE, ORACLE_SHA256),
        "original_v5": (V5_RELATIVE, V5_SHA256),
        "from_scratch_audit_v3": (AUDIT_RELATIVE, AUDIT_SHA256),
    }
    require(
        type(value) is dict
        and set(value) == {*expected, "pinned_python"},
        "the full frozen recorder, shape oracle, V5, V3, and Python "
        "source closure is mandatory",
    )
    for key, (relative, source) in expected.items():
        validate_owner(value[key], relative, source)
    validate_owner(
        value["pinned_python"],
        PINNED_PYTHON,
        PINNED_PYTHON_SHA256,
        external=True,
    )
    return value


def validate_standard_owners(value: Any) -> dict[str, Any]:
    expected = {
        "oracle": (ROOT + "/" + ORACLE_RELATIVE, ORACLE_SHA256),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "v5_guard": (ROOT + "/" + V5_RELATIVE, V5_SHA256),
        "ownership_audit": (ROOT + "/" + AUDIT_RELATIVE, AUDIT_SHA256),
    }
    expected.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, source)
        for name, (filename, source) in PINNED_STDLIB_SOURCES.items()
    })
    require(
        type(value) is dict and set(value) == set(expected),
        "the complete isolated standard-Python owner closure is mandatory",
    )
    for name, (absolute, source) in expected.items():
        validate_owner(value[name], absolute, source, external=True)
    return value


def validate_audit_manifest(
    value: Any,
    family: str,
    adapter: str,
    engine: str,
    bridge: str,
) -> dict[str, Any]:
    adapter_path, engine_path, bridge_path, source_paths, _ = (
        FAMILY_SPECS[family]
    )
    require(
        type(value) is dict
        and set(value) == {
            "family", "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256", "source_sha256", "native_sha256",
            "immutable_policy_sha256",
        }
        and value.get("family") == family
        and value.get("candidate_source_sha256") == adapter
        and value.get("native_engine_sha256") == engine
        and value.get("native_bridge_sha256") == bridge,
        "a complete independently written native-engine audit was forged",
    )
    sources = value.get("source_sha256")
    native = value.get("native_sha256")
    require(
        type(sources) is dict
        and set(sources) == set(source_paths)
        and type(native) is dict
        and set(native) == {engine_path, bridge_path}
        and sources.get(adapter_path) == adapter
        and native.get(engine_path) == engine
        and native.get(bridge_path) == bridge,
        "an independent semantic source, native engine, or bridge was hidden",
    )
    for relative, source in (*sources.items(), *native.items()):
        safe_parts(relative)
        valid_hash(source, relative)
    require(
        len(set(sources.values())) == len(sources)
        and len(set(native.values())) == len(native)
        and (engine == bridge) is (family == "c")
        and value.get("immutable_policy_sha256") == {
            V2_RELATIVE: V2_SHA256,
            V5_RELATIVE: V5_SHA256,
        },
        "a native engine was aliased or its no-delegation policy changed",
    )
    return value


def validate_candidate_closure(
    value: Any,
    family: str,
    adapter: str,
    engine: str,
    bridge: str,
) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {
            "family", "manifest", "source_owners", "native_owners",
            "policy_owners", "oracle_owner", "python_owner",
        }
        and value.get("family") == family,
        "a genuinely owned candidate source-and-binary closure is mandatory",
    )
    manifest = validate_audit_manifest(
        value["manifest"], family, adapter, engine, bridge,
    )
    sources = value.get("source_owners")
    native = value.get("native_owners")
    policies = value.get("policy_owners")
    require(
        type(sources) is dict
        and set(sources) == set(manifest["source_sha256"])
        and type(native) is dict
        and set(native) == set(manifest["native_sha256"])
        and type(policies) is dict
        and set(policies) == {V2_RELATIVE, V5_RELATIVE},
        "a genuine candidate source, engine, bridge, or policy was omitted",
    )
    for relative, source in manifest["source_sha256"].items():
        validate_owner(sources[relative], relative, source)
    for relative, source in manifest["native_sha256"].items():
        validate_owner(native[relative], relative, source)
    validate_owner(policies[V2_RELATIVE], V2_RELATIVE, V2_SHA256)
    validate_owner(policies[V5_RELATIVE], V5_RELATIVE, V5_SHA256)
    validate_owner(value["oracle_owner"], AUDIT_RELATIVE, AUDIT_SHA256)
    validate_owner(
        value["python_owner"],
        PINNED_PYTHON,
        PINNED_PYTHON_SHA256,
        external=True,
    )
    return value


def validate_guard(value: Any, family: str) -> dict[str, Any]:
    require(
        type(value) is dict,
        "a complete continuously active no-delegation guard is mandatory",
    )
    for name in GUARD_TRUE:
        require(
            value.get(name) is True,
            "an independently owned regex guard was disabled: " + name,
        )
    require(
        value.get("public_type_names_used_for_ownership") is False,
        "a public type cannot establish native semantic ownership",
    )
    for name in (
        "actual_method_guard_checks",
        "actual_warning_registry_guard_checks",
    ):
        require(
            type(value.get(name)) is int
            and value[name] == 2 * CASE_COUNT,
            "all before-and-after native guards are mandatory: " + name,
        )
    ffi = FAMILY_SPECS[family][4]
    require(
        value.get("owned_native_ffi_allowed") is ffi,
        "the independently owned Zig-only native binding policy changed",
    )
    for name in (
        "trusted_stdlib_ctypes_preloaded",
        "trusted_stdlib_ctypes_builtin_verified",
        "trusted_stdlib_ctypes_pythonapi_initialized",
    ):
        require(
            value.get(name) is ffi,
            "the genuinely owned native binding guard changed: " + name,
        )
    require(
        value.get("trusted_stdlib_ctypes_source_sha256")
        == (TRUSTED_CTYPES_SHA256 if ffi else None),
        "the frozen trusted Zig-only binding was substituted",
    )
    for name in GUARD_COUNTERS:
        require(
            type(value.get(name)) is int and value[name] >= 0,
            "a continuous native guard counter was hidden: " + name,
        )
    if ffi:
        require(
            value["owned_ctypes_load_count"] > 0
            and value["owned_ctypes_symbol_count"] > 0,
            "the genuinely owned Zig engine and symbols never loaded",
        )
    else:
        require(
            value["owned_ctypes_load_count"] == 0
            and value["owned_ctypes_symbol_count"] == 0,
            "an unowned external native matcher was loaded",
        )
    return value


def capture_stream(raw: bytes) -> dict[str, Any]:
    require(
        type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
        "a complete bounded isolated worker stream is mandatory",
    )
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
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
        "a complete source-authenticated worker stream is mandatory: "
        + label,
    )
    source = valid_hash(value.get("sha256"), label)
    try:
        raw = base64.b64decode(
            value["base64"].encode("ascii"),
            validate=True,
        )
    except (
        TypeError, ValueError, UnicodeError, binascii.Error,
    ) as error:
        raise OverviewError(
            "a complete changing-buffer worker stream was forged: " + label,
        ) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == source
        and base64.b64encode(raw).decode("ascii") == value["base64"],
        "a genuine isolated worker stream was truncated: " + label,
    )
    return raw


def source_fields(label: str) -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "label": validate_label(label),
        "recorder_relative": RECORDER_RELATIVE,
        "recorder_source_sha256": RECORDER_SHA256,
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
        "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
        "witnessed_regression_nested_sizes": list(WITNESSED_NESTED_SIZES),
        "witnessed_regression_cohort_count": len(
            WITNESSED_NESTED_SIZES,
        ),
        "witnessed_regression_case_count": WITNESSED_CASE_COUNT,
    }


COMMON_SOURCE_FIELDS = frozenset(source_fields(BASELINE_LABEL))
BASELINE_FIELDS = COMMON_SOURCE_FIELDS | frozenset({
    "schema",
    "status",
    "source_closure_before",
    "source_closure_after",
    "source_closure_unchanged",
    "complete_baseline_process_stdout",
    "complete_baseline_process_stderr",
    "lossless_evidence_layout",
    "duplicate_reference_vectors",
    "mathematical_report_bytes_upper_bound",
    "maximum_report_uncompressed_bytes",
    "structured_baseline_failure_type",
    "structured_baseline_failure_message",
    "validated_reference_a_case_count",
    "validated_reference_b_case_count",
    "baseline_records_sha256",
    "baseline_reference_pids",
    "actual_reference_workers",
    "actual_candidate_workers",
    "actual_candidate_imports",
    "actual_baseline_controller_invocations",
    "actual_baseline_controller_pid",
    "actual_baseline_process_returncode",
    "actual_baseline_process_signal",
    "actual_baseline_process_timed_out",
    "actual_baseline_process_spawn_error",
    "all_failure_reasons",
    "failure_count",
    "clock_samples",
    "timing_trials_run",
    "benchmark_files_read",
    "hidden_cases_read",
    "performance",
    "source_to_binary_reproducibility",
    "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})
CANDIDATE_FIELDS = frozenset({
    "schema",
    "status",
    "python",
    "label",
    "candidate_family",
    "candidate_source_sha256",
    "native_engine_sha256",
    "native_bridge_sha256",
    "baseline_label",
    "recorder_relative",
    "recorder_source_sha256",
    "oracle_relative",
    "oracle_source_sha256",
    "original_v5_relative",
    "original_v5_sha256",
    "ownership_audit_relative",
    "ownership_audit_sha256",
    "pinned_python",
    "pinned_python_sha256",
    "matrix_sha256",
    "published_seed",
    "case_count",
    "cohort_count",
    "variants_per_cohort",
    "shape_sizes",
    "witnessed_regression_outer_size",
    "witnessed_regression_nested_sizes",
    "witnessed_regression_cohort_count",
    "witnessed_regression_case_count",
    "baseline_receipt_relative",
    "baseline_receipt_sha256",
    "baseline_archive_relative",
    "baseline_archive_sha256",
    "baseline_records_sha256",
    "baseline_reference_pids",
    "candidate_owner_before",
    "candidate_owner_after",
    "candidate_owner_unchanged",
    "complete_candidate_process_stdout",
    "complete_candidate_process_stderr",
    "lossless_evidence_layout",
    "duplicate_candidate_vectors",
    "duplicate_reference_vectors",
    "mathematical_report_bytes_upper_bound",
    "maximum_report_uncompressed_bytes",
    "validated_baseline_record_count",
    "validated_candidate_record_count",
    "candidate_records_sha256",
    "mismatch_count",
    "all_mismatches",
    "mismatches_by_cohort",
    "mismatches_by_api",
    "mismatches_by_target",
    "mismatches_by_behavior",
    "witnessed_regression_mismatches_by_nested_size",
    "all_mismatches_preserved",
    "matcher_guard",
    "actual_method_guard_checks",
    "actual_warning_registry_guard_checks",
    "validated_prior_reference_workers",
    "actual_reference_workers",
    "actual_candidate_workers",
    "actual_candidate_imports",
    "actual_candidate_process_invocations",
    "actual_candidate_pid",
    "actual_candidate_process_returncode",
    "actual_candidate_process_signal",
    "actual_candidate_process_timed_out",
    "actual_candidate_process_spawn_error",
    "all_failure_reasons",
    "failure_count",
    "clock_samples",
    "timing_trials_run",
    "benchmark_files_read",
    "hidden_cases_read",
    "performance",
    "source_to_binary_reproducibility",
    "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})


def evidence_pin(
    value: Any,
    seen: set[str],
) -> tuple[str, str]:
    require(
        type(value) is dict and set(value) == {"relative", "sha256"},
        "an exact independently frozen report and receipt are mandatory",
    )
    relative = value.get("relative")
    parts = safe_parts(relative)
    require(
        len(parts) == 3
        and parts[:2] == ("experiments", "rust_public_practice_v1")
        and relative not in seen,
        "changing-buffer evidence was reused or escaped its directory",
    )
    seen.add(relative)
    return relative, valid_hash(value.get("sha256"), relative)


def approved_paths(
    label: str,
    family: str | None = None,
) -> tuple[str, str]:
    label = validate_label(label)
    if family is None:
        stem = "shape-changing-buffer-semantics-v1-" + label
    else:
        require(
            family in FAMILY_ORDER,
            "only a genuinely independently written family may be graphed",
        )
        stem = (
            family + "-shape-changing-buffer-semantics-v1-" + label
        )
    return (
        EVIDENCE_DIRECTORY + "/" + stem + ".json.gz",
        EVIDENCE_DIRECTORY + "/" + stem
        + "-publication-receipt.json",
    )


def validate_reference_guard(value: Any) -> None:
    require(
        value == {
            "candidate_import_count": 0,
            "external_regex_import_count": 0,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "required_method_guard_checks": 2 * CASE_COUNT,
            "future_candidate_guard_relative": V5_RELATIVE,
            "future_candidate_guard_sha256": V5_SHA256,
            "future_ownership_audit_relative": AUDIT_RELATIVE,
            "future_ownership_audit_sha256": AUDIT_SHA256,
            "future_candidate_guard_installed": False,
        },
        "an independently isolated stable-Python guard was disabled",
    )


def validate_reference_worker(
    value: Any,
    role: str,
    matrix: list[dict[str, Any]],
    records_hash: str,
    record_digest: RecordDigest,
) -> dict[str, Any]:
    expected = {
        "schema": ORACLE_SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "records_sha256": records_hash,
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
            "pid", "records", "source_owners", "reference_guard",
        },
        "a complete independent stable-Python worker was concealed",
    )
    fixed_fields(value, expected, "the isolated original Python worker")
    require(
        type(value.get("pid")) is int and value["pid"] > 0,
        "an exact independently isolated Python worker PID is mandatory",
    )
    validate_standard_owners(value["source_owners"])
    validate_reference_guard(value["reference_guard"])
    validate_records(
        matrix,
        value["records"],
        records_hash,
        record_digest=record_digest,
    )
    return value


def validate_reference_process(
    value: Any,
    worker: Mapping[str, Any],
    role: str,
) -> None:
    require(
        type(value) is dict
        and set(value) == {
            "role", "pid", "returncode", "stdout", "stderr",
        }
        and value.get("role") == role
        and value.get("pid") == worker["pid"]
        and type(value.get("returncode")) is int
        and value["returncode"] == 0,
        "a genuine isolated original Python worker was substituted",
    )
    require(
        decode_stream(value["stdout"], role + " stdout")
        == canonical(dict(worker))
        and decode_stream(value["stderr"], role + " stderr") == b"",
        "a complete independently observed Python stream was concealed",
    )


def validate_baseline_receipt(
    value: Any,
    archive_path: str,
    archive_hash: str,
    receipt_path: str,
) -> dict[str, Any]:
    expected = {
        "schema": (
            RECORDER_SCHEMA + "-durable-baseline-publication-receipt"
        ),
        "status": "PASS",
        "baseline_result_status": "PASS",
        **source_fields(BASELINE_LABEL),
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
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
        "report_relative": archive_path,
        "report_sha256": archive_hash,
        "report_bytes": BASELINE_ARCHIVE_BYTES,
        "report_uncompressed_sha256": BASELINE_REPORT_SHA256,
        "report_uncompressed_bytes": BASELINE_REPORT_BYTES,
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_path,
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
        "mathematical_report_bytes_upper_bound",
    }
    require(
        type(value) is dict and set(value) == set(expected) | extras,
        "the exact durable 10,240-case Python baseline receipt is mandatory",
    )
    fixed_fields(
        value,
        expected,
        "the exact independently frozen Python changing-buffer receipt",
    )
    pids = value["baseline_reference_pids"]
    require(
        type(pids) is list
        and len(pids) == 2
        and all(type(pid) is int and pid > 0 for pid in pids)
        and pids[0] != pids[1],
        "the two genuinely independent original workers were aliased",
    )
    bound = value["mathematical_report_bytes_upper_bound"]
    require(
        type(bound) is int
        and BASELINE_REPORT_BYTES <= bound <= MAX_UNCOMPRESSED_BYTES,
        "a complete lossless Python baseline has no safe exact bound",
    )
    before = validate_tool_closure(value["source_closure_before"])
    after = validate_tool_closure(value["source_closure_after"])
    require(
        before == after,
        "an independently frozen original source changed while running",
    )
    return value


def validate_baseline_result(
    value: Any,
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
    record_digest: RecordDigest,
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
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
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
            "source_owners", "reference_a", "reference_b",
            "reference_a_process", "reference_b_process",
        },
        "the complete two-reference original Python result was hidden",
    )
    fixed_fields(
        value,
        expected,
        "the two independently frozen stable-Python references",
    )
    shared = validate_standard_owners(value["source_owners"])
    first = validate_reference_worker(
        value["reference_a"],
        "reference_a",
        matrix,
        BASELINE_RECORDS_SHA256,
        record_digest,
    )
    second = validate_reference_worker(
        value["reference_b"],
        "reference_b",
        matrix,
        BASELINE_RECORDS_SHA256,
        record_digest,
    )
    require(
        first["pid"] != second["pid"]
        and [first["pid"], second["pid"]]
        == receipt["baseline_reference_pids"]
        and first["source_owners"] == second["source_owners"] == shared
        and first["records"] == second["records"],
        "the two independent 10,240-case Python workers disagree",
    )
    validate_reference_process(
        value["reference_a_process"], first, "reference_a",
    )
    validate_reference_process(
        value["reference_b_process"], second, "reference_b",
    )
    return value


def validate_baseline(
    value: Any,
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
    record_digest: RecordDigest,
) -> list[dict[str, Any]]:
    expected = {
        "schema": RECORDER_SCHEMA + "-complete-baseline-report",
        "status": "PASS",
        **source_fields(BASELINE_LABEL),
        "source_closure_unchanged": True,
        "lossless_evidence_layout": (
            "one-authenticated-baseline-controller-stdout"
        ),
        "duplicate_reference_vectors": False,
        "mathematical_report_bytes_upper_bound": (
            receipt["mathematical_report_bytes_upper_bound"]
        ),
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "structured_baseline_failure_type": None,
        "structured_baseline_failure_message": None,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": receipt["baseline_reference_pids"],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "actual_baseline_process_returncode": 0,
        "actual_baseline_process_signal": None,
        "actual_baseline_process_timed_out": False,
        "actual_baseline_process_spawn_error": None,
        "all_failure_reasons": [],
        "failure_count": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(
        type(value) is dict and set(value) == BASELINE_FIELDS,
        "the complete canonical lossless original Python report is mandatory",
    )
    fixed_fields(
        value,
        expected,
        "the complete independently observed Python baseline",
    )
    require(
        type(value.get("actual_baseline_controller_pid")) is int
        and value["actual_baseline_controller_pid"] > 0
        and value["actual_baseline_controller_pid"]
        not in receipt["baseline_reference_pids"],
        "the genuine two-worker controller PID was concealed or aliased",
    )
    before = validate_tool_closure(value["source_closure_before"])
    after = validate_tool_closure(value["source_closure_after"])
    require(
        before == after == receipt["source_closure_before"],
        "a frozen Python baseline source changed",
    )
    controller = decode_stream(
        value["complete_baseline_process_stdout"],
        "the complete two-reference original controller stdout",
    )
    require(
        decode_stream(
            value["complete_baseline_process_stderr"],
            "the complete two-reference original controller stderr",
        ) == b"",
        "the independently frozen original emitted hidden errors",
    )
    result = validate_baseline_result(
        decode_document(
            controller,
            "the complete two-reference changing-buffer controller",
            MAX_PROCESS_BYTES,
        ),
        matrix,
        receipt,
        record_digest,
    )
    return result["reference_a"]["records"]


def validate_mismatch_counts(
    value: Mapping[str, Any],
    count: int,
) -> None:
    require(
        type(count) is int and 0 <= count <= CASE_COUNT,
        "an exact full-denominator mismatch count is mandatory",
    )
    expectations = (
        ("mismatches_by_cohort", COHORTS, VARIANTS_PER_COHORT),
        ("mismatches_by_api", APIS, CASE_COUNT),
        ("mismatches_by_target", TARGETS, CASE_COUNT),
        ("mismatches_by_behavior", BEHAVIORS, CASE_COUNT),
    )
    for name, labels, maximum in expectations:
        observed = value.get(name)
        require(
            type(observed) is dict
            and set(observed) == set(labels)
            and all(
                type(observed[item]) is int
                and 0 <= observed[item] <= maximum
                for item in labels
            )
            and sum(observed.values()) == count,
            "a real changing-buffer failure was hidden: " + name,
        )
    witnessed = value.get(
        "witnessed_regression_mismatches_by_nested_size",
    )
    require(
        type(witnessed) is dict
        and set(witnessed)
        == {str(size) for size in WITNESSED_NESTED_SIZES}
        and all(
            type(witnessed[str(size)]) is int
            and 0 <= witnessed[str(size)] <= VARIANTS_PER_COHORT
            for size in WITNESSED_NESTED_SIZES
        )
        and sum(witnessed.values()) <= count
        and sum(witnessed.values()) <= WITNESSED_CASE_COUNT,
        "an actually witnessed short-buffer failure was concealed",
    )


def validate_candidate_receipt(
    value: Any,
    family: str,
    adapter: str,
    baseline: Mapping[str, Any],
    report_path: str,
    report_hash: str,
    receipt_path: str,
) -> dict[str, Any]:
    require(
        type(value) is dict,
        "a complete source-pinned candidate receipt is mandatory",
    )
    label = validate_label(value.get("label"))
    require(
        approved_paths(label, family) == (report_path, receipt_path),
        "a changing-buffer candidate escaped its exact owned label",
    )
    engine = valid_hash(
        value.get("native_engine_sha256"),
        family + " native engine",
    )
    bridge = valid_hash(
        value.get("native_bridge_sha256"),
        family + " native bridge",
    )
    expected = {
        "schema": (
            RECORDER_SCHEMA + "-durable-candidate-publication-receipt"
        ),
        "status": "PASS",
        "python": "3.14.6",
        "label": label,
        "candidate_family": family,
        "candidate_source_sha256": adapter,
        "native_engine_sha256": engine,
        "native_bridge_sha256": bridge,
        "baseline_label": BASELINE_LABEL,
        "recorder_source_sha256": RECORDER_SHA256,
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
        "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
        "witnessed_regression_nested_sizes": list(
            WITNESSED_NESTED_SIZES,
        ),
        "witnessed_regression_case_count": WITNESSED_CASE_COUNT,
        "baseline_receipt_relative": baseline["receipt_relative"],
        "baseline_receipt_sha256": baseline["receipt_sha256"],
        "baseline_archive_relative": baseline["archive_relative"],
        "baseline_archive_sha256": baseline["archive_sha256"],
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": baseline["reference_pids"],
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_process_invocations": 1,
        "candidate_owner_unchanged": True,
        "lossless_evidence_layout": (
            "one-authenticated-candidate-worker-stdout-and-full-mismatches"
        ),
        "duplicate_candidate_vectors": False,
        "duplicate_reference_vectors": False,
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "report_relative": report_path,
        "report_sha256": report_hash,
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_path,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_candidate": True,
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
        "candidate_result_status",
        "candidate_records_sha256",
        "mismatch_count",
        "mismatches_by_cohort",
        "mismatches_by_api",
        "mismatches_by_target",
        "mismatches_by_behavior",
        "witnessed_regression_mismatches_by_nested_size",
        "actual_candidate_imports",
        "candidate_owner_before",
        "candidate_owner_after",
        "mathematical_report_bytes_upper_bound",
        "report_bytes",
        "report_uncompressed_sha256",
        "report_uncompressed_bytes",
    }
    require(
        set(value) == set(expected) | extras,
        "a complete lossless candidate publication receipt was hidden",
    )
    fixed_fields(
        value,
        expected,
        "the genuinely owned candidate publication receipt",
    )
    result_status = value.get("candidate_result_status")
    mismatches = value.get("mismatch_count")
    require(
        result_status in {"PASS", "FAIL"}
        and type(mismatches) is int
        and 0 <= mismatches <= CASE_COUNT
        and (result_status == "PASS") is (mismatches == 0),
        "successful publication was substituted for genuine correctness",
    )
    valid_hash(
        value.get("candidate_records_sha256"),
        "all 10,240 genuinely observed native outcomes",
    )
    valid_hash(
        value.get("report_uncompressed_sha256"),
        "the complete native changing-buffer report",
    )
    require(
        type(value.get("actual_candidate_imports")) is int
        and value["actual_candidate_imports"] >= 2,
        "the independently owned native adapter and bridge never loaded",
    )
    require(
        type(value.get("report_bytes")) is int
        and 0 < value["report_bytes"] <= MAX_ARCHIVE_BYTES
        and type(value.get("report_uncompressed_bytes")) is int
        and 0 < value["report_uncompressed_bytes"]
        <= MAX_UNCOMPRESSED_BYTES
        and type(value.get("mathematical_report_bytes_upper_bound"))
        is int
        and value["report_uncompressed_bytes"]
        <= value["mathematical_report_bytes_upper_bound"]
        <= MAX_UNCOMPRESSED_BYTES,
        "a lossless full-scale candidate report size was concealed",
    )
    before = validate_candidate_closure(
        value["candidate_owner_before"],
        family,
        adapter,
        engine,
        bridge,
    )
    after = validate_candidate_closure(
        value["candidate_owner_after"],
        family,
        adapter,
        engine,
        bridge,
    )
    require(
        before == after,
        "an independently written source or native engine changed",
    )
    validate_mismatch_counts(value, mismatches)
    return value


def validate_native_provenance(
    value: Any,
    family: str,
    adapter: str,
    engine: str,
    bridge: str,
) -> None:
    adapter_path, engine_path, bridge_path, _, _ = FAMILY_SPECS[family]
    require(
        type(value) is dict
        and set(value) == {"source", "native_engine", "native_bridge"},
        "the complete genuine native candidate provenance is mandatory",
    )
    validate_owner(value["source"], adapter_path, adapter)
    validate_owner(value["native_engine"], engine_path, engine)
    validate_owner(value["native_bridge"], bridge_path, bridge)
    require(
        (value["native_engine"] == value["native_bridge"])
        is (family == "c"),
        "an independently owned native bridge was incorrectly aliased",
    )


def validate_candidate_worker(
    value: Any,
    receipt: Mapping[str, Any],
    baseline: Mapping[str, Any],
    matrix: list[dict[str, Any]],
    closure: Mapping[str, Any],
    record_digest: RecordDigest,
) -> dict[str, Any]:
    family = receipt["candidate_family"]
    expected = {
        "schema": RECORDER_SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": "candidate-" + family,
        "candidate_family": family,
        **source_fields(BASELINE_LABEL),
        "baseline_receipt_relative": baseline["receipt_relative"],
        "baseline_receipt_sha256": baseline["receipt_sha256"],
        "baseline_archive_relative": baseline["archive_relative"],
        "baseline_archive_sha256": baseline["archive_sha256"],
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
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
        "pid",
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
        "a complete genuinely isolated native worker was concealed",
    )
    fixed_fields(
        value,
        expected,
        "the genuine guarded changing-buffer candidate worker",
    )
    require(
        type(value.get("pid")) is int
        and value["pid"] > 0
        and value["pid"] not in baseline["reference_pids"]
        and value.get("baseline_reference_pids")
        == baseline["reference_pids"]
        and value.get("actual_candidate_imports")
        == receipt["actual_candidate_imports"]
        and value.get("records_sha256")
        == receipt["candidate_records_sha256"],
        "a genuine native process, worker PID, or record vector was forged",
    )
    validate_owner(
        value["baseline_receipt_owner"],
        baseline["receipt_relative"],
        baseline["receipt_sha256"],
    )
    validate_owner(
        value["baseline_archive_owner"],
        baseline["archive_relative"],
        baseline["archive_sha256"],
    )
    validate_tool_closure(value["source_provenance"])
    audit = validate_audit_manifest(
        value["audit_manifest"],
        family,
        receipt["candidate_source_sha256"],
        receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    owned = validate_candidate_closure(
        value["owned_source_closure"],
        family,
        receipt["candidate_source_sha256"],
        receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    require(
        owned == closure and owned["manifest"] == audit,
        "the actual candidate escaped its complete native ownership",
    )
    validate_native_provenance(
        value["native_provenance"],
        family,
        receipt["candidate_source_sha256"],
        receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    validate_guard(value["matcher_guard"], family)
    validate_records(
        matrix,
        value["records"],
        receipt["candidate_records_sha256"],
        candidate=True,
        record_digest=record_digest,
    )
    return value


def validate_candidate(
    value: Any,
    receipt: Mapping[str, Any],
    baseline: Mapping[str, Any],
    matrix: list[dict[str, Any]],
    original: list[dict[str, Any]],
    record_digest: RecordDigest,
) -> dict[str, Any]:
    expected = {
        "schema": RECORDER_SCHEMA + "-complete-candidate-report",
        "status": receipt["candidate_result_status"],
        "python": "3.14.6",
        "label": receipt["label"],
        "candidate_family": receipt["candidate_family"],
        "candidate_source_sha256": receipt["candidate_source_sha256"],
        "native_engine_sha256": receipt["native_engine_sha256"],
        "native_bridge_sha256": receipt["native_bridge_sha256"],
        "baseline_label": BASELINE_LABEL,
        "recorder_relative": RECORDER_RELATIVE,
        "recorder_source_sha256": RECORDER_SHA256,
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
        "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
        "witnessed_regression_nested_sizes": list(
            WITNESSED_NESTED_SIZES,
        ),
        "witnessed_regression_cohort_count": len(
            WITNESSED_NESTED_SIZES,
        ),
        "witnessed_regression_case_count": WITNESSED_CASE_COUNT,
        "baseline_receipt_relative": baseline["receipt_relative"],
        "baseline_receipt_sha256": baseline["receipt_sha256"],
        "baseline_archive_relative": baseline["archive_relative"],
        "baseline_archive_sha256": baseline["archive_sha256"],
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": baseline["reference_pids"],
        "candidate_owner_unchanged": True,
        "lossless_evidence_layout": (
            "one-authenticated-candidate-worker-stdout-and-full-mismatches"
        ),
        "duplicate_candidate_vectors": False,
        "duplicate_reference_vectors": False,
        "mathematical_report_bytes_upper_bound": (
            receipt["mathematical_report_bytes_upper_bound"]
        ),
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "candidate_records_sha256": receipt["candidate_records_sha256"],
        "mismatch_count": receipt["mismatch_count"],
        "mismatches_by_cohort": receipt["mismatches_by_cohort"],
        "mismatches_by_api": receipt["mismatches_by_api"],
        "mismatches_by_target": receipt["mismatches_by_target"],
        "mismatches_by_behavior": receipt["mismatches_by_behavior"],
        "witnessed_regression_mismatches_by_nested_size": receipt[
            "witnessed_regression_mismatches_by_nested_size"
        ],
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": receipt["actual_candidate_imports"],
        "actual_candidate_process_invocations": 1,
        "actual_candidate_process_returncode": 0,
        "actual_candidate_process_signal": None,
        "actual_candidate_process_timed_out": False,
        "actual_candidate_process_spawn_error": None,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(
        type(value) is dict and set(value) == CANDIDATE_FIELDS,
        "the complete lossless native changing-buffer report is mandatory",
    )
    fixed_fields(
        value,
        expected,
        "the genuinely owned complete candidate report",
    )
    family = receipt["candidate_family"]
    closure = validate_candidate_closure(
        value["candidate_owner_before"],
        family,
        receipt["candidate_source_sha256"],
        receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    final = validate_candidate_closure(
        value["candidate_owner_after"],
        family,
        receipt["candidate_source_sha256"],
        receipt["native_engine_sha256"],
        receipt["native_bridge_sha256"],
    )
    require(
        closure == final == receipt["candidate_owner_before"]
        == receipt["candidate_owner_after"],
        "the genuine source-to-native closure changed during observation",
    )
    worker_raw = decode_stream(
        value["complete_candidate_process_stdout"],
        "the complete genuine native candidate stdout",
    )
    require(
        decode_stream(
            value["complete_candidate_process_stderr"],
            "the complete genuine native candidate stderr",
        ) == b"",
        "a genuine native worker emitted concealed errors",
    )
    worker = validate_candidate_worker(
        decode_document(
            worker_raw,
            "the complete genuine native candidate worker",
            MAX_PROCESS_BYTES,
        ),
        receipt,
        baseline,
        matrix,
        closure,
        record_digest,
    )
    require(
        value.get("actual_candidate_pid") == worker["pid"]
        and value.get("matcher_guard") == worker["matcher_guard"],
        "a genuine native process or continuous guard was replaced",
    )
    mismatches: list[dict[str, Any]] = []
    by_cohort = {name: 0 for name in COHORTS}
    by_api = {name: 0 for name in APIS}
    by_target = {name: 0 for name in TARGETS}
    by_behavior = {name: 0 for name in BEHAVIORS}
    witnessed = {
        str(size): 0 for size in WITNESSED_NESTED_SIZES
    }
    for case, standard, actual in zip(
        matrix,
        original,
        worker["records"],
        strict=True,
    ):
        require(
            case["case"] == standard["case"] == actual["case"]
            and case["cohort"] == standard["cohort"] == actual["cohort"]
            and case["api"] == standard["api"] == actual["api"]
            and case["outer_size"] == standard["outer_size"]
            == actual["outer_size"]
            and case["nested_size"] == standard["nested_size"]
            == actual["nested_size"],
            "a source-ordered original or native result was hidden",
        )
        if standard["outcome"] != actual["outcome"]:
            by_cohort[case["cohort"]] += 1
            by_api[case["api"]] += 1
            by_target[case["target"]] += 1
            by_behavior[case["behavior"]] += 1
            if (
                case["outer_size"] == WITNESSED_OUTER_SIZE
                and case["nested_size"] in WITNESSED_NESTED_SIZES
            ):
                witnessed[str(case["nested_size"])] += 1
            mismatches.append({
                "case": case["case"],
                "cohort": case["cohort"],
                "api": case["api"],
                "target": case["target"],
                "behavior": case["behavior"],
                "outer_size": case["outer_size"],
                "nested_size": case["nested_size"],
                "input": case,
                "baseline_outcome": standard["outcome"],
                "candidate_outcome": actual["outcome"],
            })
    require(
        value.get("all_mismatches") == mismatches
        and value["mismatch_count"] == len(mismatches)
        and value["mismatches_by_cohort"] == by_cohort
        and value["mismatches_by_api"] == by_api
        and value["mismatches_by_target"] == by_target
        and value["mismatches_by_behavior"] == by_behavior
        and value["witnessed_regression_mismatches_by_nested_size"]
        == witnessed,
        "a real buffer mismatch, regression, or complete failure was hidden",
    )
    reasons = value.get("all_failure_reasons")
    require(
        type(reasons) is list
        and all(type(reason) is str and bool(reason) for reason in reasons)
        and type(value.get("failure_count")) is int
        and value["failure_count"] == len(reasons)
        and (len(reasons) == 0) is (len(mismatches) == 0)
        and (value["status"] == "PASS") is (len(mismatches) == 0),
        "a genuine candidate crash, failure, or mismatch was concealed",
    )
    return {
        "passed": CASE_COUNT - len(mismatches),
        "failed": len(mismatches),
        "not_measured": 0,
        "mismatches_by_cohort": by_cohort,
        "mismatches_by_api": by_api,
        "mismatches_by_target": by_target,
        "mismatches_by_behavior": by_behavior,
        "witnessed_regression_mismatches_by_nested_size": witnessed,
    }


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == ROOT + "/" + SOURCE_RELATIVE
        and os.path.realpath(__file__) == ROOT + "/" + SOURCE_RELATIVE,
        "use only this exact source and isolated pinned Python 3.14.6",
    )
    for name in tuple(sys.modules):
        require(
            type(name) is str
            and name.partition(".")[0] not in FORBIDDEN_ROOTS,
            "the changing-buffer chart imported an implementation or engine",
        )


def validate_owned_limit(value: Any) -> int:
    require(
        type(value) is int
        and 0 < value <= MAX_ARCHIVE_BYTES,
        "an exact bounded project-owned graph input is mandatory",
    )
    return value


@contextlib.contextmanager
def open_owned(
    relative: str,
    maximum: int,
) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_parts(relative)
    maximum = validate_owned_limit(maximum)
    regular = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directory_flags = regular | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags)
        opened.append(current)
        require(
            stat.S_ISDIR(os.fstat(current).st_mode),
            "the exact graph workspace was substituted",
        )
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "a frozen changing-buffer parent became a symlink",
            )
        descriptor = os.open(parts[-1], regular, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(
            parts[-1],
            dir_fd=current,
            follow_symlinks=False,
        )
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (
                before.st_dev, before.st_ino, before.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            )
            and 0 < before.st_size <= maximum,
            "an owned no-follow graph input was substituted or oversized",
        )
        yield descriptor, before
        final = os.fstat(descriptor)
        named = os.stat(
            parts[-1],
            dir_fd=current,
            follow_symlinks=False,
        )
        require(
            (
                before.st_dev, before.st_ino, before.st_size,
            ) == (
                final.st_dev, final.st_ino, final.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            ),
            "a source-pinned correctness input changed while being read",
        )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_frozen(
    relative: str,
    source: str,
    maximum: int,
) -> bytes:
    expected = valid_hash(source, relative)
    with open_owned(relative, maximum) as (descriptor, info):
        remaining = info.st_size
        observed = hashlib.sha256()
        chunks: list[bytes] = []
        while remaining:
            block = os.read(
                descriptor,
                min(CHUNK_BYTES, remaining),
            )
            require(
                type(block) is bytes and bool(block),
                "a frozen changing-buffer input was truncated",
            )
            observed.update(block)
            remaining -= len(block)
            chunks.append(block)
        require(
            os.read(descriptor, 1) == b""
            and observed.hexdigest() == expected,
            "a frozen changing-buffer source failed its exact SHA-256",
        )
        return b"".join(chunks)


def authenticate_external(
    absolute: str,
    source: str,
    maximum: int,
) -> None:
    expected = valid_hash(source, absolute)
    require(
        type(absolute) is str
        and absolute
        in {
            PINNED_PYTHON,
            *(
                PINNED_STDLIB_DIRECTORY + filename
                for filename, _ in PINNED_STDLIB_SOURCES.values()
            ),
        }
        and os.path.realpath(absolute) == absolute
        and type(maximum) is int
        and 0 < maximum <= MAX_BINARY_BYTES,
        "only exact pinned original CPython inputs may be authenticated",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        named = os.stat(absolute, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and (
                before.st_dev, before.st_ino, before.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            )
            and 0 < before.st_size <= maximum,
            "the pinned stable Python owner was replaced",
        )
        remaining = before.st_size
        observed = hashlib.sha256()
        while remaining:
            block = os.read(
                descriptor,
                min(CHUNK_BYTES, remaining),
            )
            require(
                type(block) is bytes and bool(block),
                "the pinned stable Python source was truncated",
            )
            observed.update(block)
            remaining -= len(block)
        final = os.fstat(descriptor)
        named = os.stat(absolute, follow_symlinks=False)
        require(
            os.read(descriptor, 1) == b""
            and observed.hexdigest() == expected
            and (
                before.st_dev, before.st_ino, before.st_size,
            ) == (
                final.st_dev, final.st_ino, final.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            ),
            "the exact stable original Python source failed authentication",
        )
    finally:
        os.close(descriptor)


class VerifiedGzipReader:
    """Authenticate exactly one complete, bounded frozen gzip member."""

    def __init__(
        self,
        descriptor: int,
        archive_bytes: int,
        archive_sha256: str,
        original_bytes: int,
        original_sha256: str,
    ) -> None:
        require(
            type(descriptor) is int
            and type(archive_bytes) is int
            and 0 < archive_bytes <= MAX_ARCHIVE_BYTES
            and type(original_bytes) is int
            and 0 < original_bytes <= MAX_UNCOMPRESSED_BYTES,
            "exact bounded compressed and original evidence is mandatory",
        )
        self.descriptor = descriptor
        self.archive_bytes = archive_bytes
        self.archive_sha256 = valid_hash(
            archive_sha256,
            "complete changing-buffer gzip",
        )
        self.original_bytes = original_bytes
        self.original_sha256 = valid_hash(
            original_sha256,
            "complete restored changing-buffer report",
        )
        self.inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        self.compressed_hash = hashlib.sha256()
        self.original_hash = hashlib.sha256()
        self.compressed_count = 0
        self.original_count = 0
        self.pending = b""
        self.finished = False

    def read(self, requested: int) -> bytes:
        require(
            type(requested) is int and 0 < requested <= CHUNK_BYTES,
            "stream only bounded complete frozen evidence blocks",
        )
        result = bytearray()
        while len(result) < requested and not self.finished:
            if (
                not self.pending
                and self.compressed_count < self.archive_bytes
            ):
                block = os.read(
                    self.descriptor,
                    min(
                        CHUNK_BYTES,
                        self.archive_bytes - self.compressed_count,
                    ),
                )
                require(
                    type(block) is bytes and bool(block),
                    "a genuinely authenticated gzip was truncated",
                )
                self.compressed_count += len(block)
                self.compressed_hash.update(block)
                self.pending = block
            if self.pending:
                limit = min(
                    requested - len(result),
                    self.original_bytes - self.original_count + 1,
                )
                try:
                    plain = self.inflater.decompress(
                        self.pending,
                        limit,
                    )
                except (
                    zlib.error, ValueError, OverflowError,
                ) as error:
                    raise OverviewError(
                        "the changing-buffer gzip archive is invalid",
                    ) from error
                require(
                    not self.inflater.unused_data,
                    "extra gzip members and trailing bytes are forbidden",
                )
                self.pending = self.inflater.unconsumed_tail
                if plain:
                    self.original_count += len(plain)
                    require(
                        self.original_count <= self.original_bytes,
                        "gzip expansion exceeded its frozen safe bound",
                    )
                    self.original_hash.update(plain)
                    result.extend(plain)
                continue
            require(
                self.compressed_count == self.archive_bytes
                and self.inflater.eof
                and not self.inflater.unused_data
                and os.read(self.descriptor, 1) == b"",
                "a complete single-member gzip footer is mandatory",
            )
            try:
                tail = self.inflater.flush(CHUNK_BYTES)
            except (zlib.error, ValueError) as error:
                raise OverviewError(
                    "the lossless changing-buffer gzip footer is invalid",
                ) from error
            require(
                not tail
                and self.compressed_hash.hexdigest()
                == self.archive_sha256
                and self.original_count == self.original_bytes
                and self.original_hash.hexdigest()
                == self.original_sha256,
                "a complete lossless report failed its exact size or SHA-256",
            )
            self.finished = True
        return bytes(result)


class StreamingObject:
    """Validate every report field while streaming its authenticated gzip."""

    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.utf8 = codecs.getincrementaldecoder("utf-8")("strict")
        self.decoder = json.JSONDecoder(
            object_pairs_hook=unique_object,
        )
        self.buffer = ""
        self.position = 0
        self.ended = False

    def fill(self) -> bool:
        if self.ended:
            return False
        block = self.stream.read(CHUNK_BYTES)
        require(
            type(block) is bytes,
            "a streamed complete report emitted non-byte evidence",
        )
        if not block:
            self.buffer += self.utf8.decode(b"", final=True)
            self.ended = True
            return False
        self.buffer += self.utf8.decode(block, final=False)
        return True

    def compact(self) -> None:
        if self.position >= 2 * CHUNK_BYTES:
            self.buffer = self.buffer[self.position:]
            self.position = 0

    def peek(self) -> str | None:
        while self.position == len(self.buffer) and self.fill():
            pass
        if self.position < len(self.buffer):
            return self.buffer[self.position]
        return None

    def take(self) -> str:
        value = self.peek()
        require(
            value is not None,
            "the complete changing-buffer report was truncated",
        )
        self.position += 1
        return value

    def whitespace(self) -> None:
        while self.peek() in (" ", "\t", "\r", "\n"):
            self.position += 1
            self.compact()

    def literal(self, expected: str) -> None:
        self.whitespace()
        require(
            self.take() == expected,
            "an authenticated report delimiter was substituted",
        )

    def value(self) -> Any:
        self.whitespace()
        self.compact()
        while True:
            try:
                result, ending = self.decoder.raw_decode(
                    self.buffer,
                    self.position,
                )
            except json.JSONDecodeError as error:
                require(
                    not self.ended,
                    "a complete streamed JSON value was clipped",
                )
                require(
                    len(self.buffer) - self.position
                    <= MAX_SELECTED_VALUE_BYTES,
                    "a complete streamed worker exceeds its safe bound",
                )
                if not self.fill():
                    raise OverviewError(
                        "a complete streamed JSON value is missing",
                    ) from error
                continue
            self.position = ending
            return result

    def skip(self) -> None:
        self.whitespace()
        first = self.peek()
        require(
            first is not None,
            "a complete report value was truncated",
        )
        if first == '"':
            self.take()
            escaped = False
            while True:
                item = self.take()
                if escaped:
                    escaped = False
                elif item == "\\":
                    escaped = True
                elif item == '"':
                    return
                self.compact()
        elif first in ("{", "["):
            stack: list[str] = []
            quoted = False
            escaped = False
            while True:
                item = self.take()
                if quoted:
                    if escaped:
                        escaped = False
                    elif item == "\\":
                        escaped = True
                    elif item == '"':
                        quoted = False
                elif item == '"':
                    quoted = True
                elif item in ("{", "["):
                    stack.append("}" if item == "{" else "]")
                elif item in ("}", "]"):
                    require(
                        bool(stack) and stack[-1] == item,
                        "an unselected complete JSON container is invalid",
                    )
                    stack.pop()
                    if not stack:
                        return
                self.compact()
        else:
            beginning = self.position
            while True:
                item = self.peek()
                if item is None or item in (
                    ",", "}", "]", " ", "\t", "\r", "\n",
                ):
                    break
                self.position += 1
            raw = self.buffer[beginning:self.position]
            try:
                _, ending = self.decoder.raw_decode(raw)
            except json.JSONDecodeError as error:
                raise OverviewError(
                    "an unselected complete JSON scalar was forged",
                ) from error
            require(
                ending == len(raw),
                "an unselected complete JSON scalar was corrupted",
            )

    def select(self, fields: frozenset[str]) -> dict[str, Any]:
        require(
            type(fields) is frozenset and bool(fields),
            "an exact complete streamed evidence schema is mandatory",
        )
        self.literal("{")
        found: set[str] = set()
        result: dict[str, Any] = {}
        self.whitespace()
        if self.peek() == "}":
            self.take()
        else:
            while True:
                key = self.value()
                require(
                    type(key) is str and key not in found,
                    "a complete report field was duplicated",
                )
                found.add(key)
                self.literal(":")
                if key in fields:
                    result[key] = self.value()
                else:
                    self.skip()
                self.whitespace()
                ending = self.take()
                if ending == "}":
                    break
                require(
                    ending == ",",
                    "a complete report separator was substituted",
                )
        self.whitespace()
        require(
            self.peek() is None
            and found == fields
            and set(result) == fields,
            "a complete report field was omitted, injected, or concealed",
        )
        return result


def read_archive(
    relative: str,
    archive_hash: str,
    fields: frozenset[str],
    original_hash: str,
    original_bytes: int,
    archive_bytes: int,
) -> dict[str, Any]:
    with open_owned(relative, MAX_ARCHIVE_BYTES) as (
        descriptor,
        info,
    ):
        require(
            info.st_size == archive_bytes,
            "the complete lossless gzip changed its authenticated size",
        )
        stream = VerifiedGzipReader(
            descriptor,
            archive_bytes,
            archive_hash,
            original_bytes,
            original_hash,
        )
        result = StreamingObject(stream).select(fields)
        require(
            stream.finished,
            "the complete changing-buffer archive was not authenticated",
        )
        return result


Loader = Callable[
    [str, str, str, str | None, int | None, int | None],
    dict[str, Any],
]


def actual_loader(
    relative: str,
    expected: str,
    kind: str,
    original_hash: str | None,
    original_bytes: int | None,
    archive_bytes: int | None,
) -> dict[str, Any]:
    parts = safe_parts(relative)
    require(
        len(parts) == 3
        and parts[:2] == ("experiments", "rust_public_practice_v1"),
        "read only explicitly pinned changing-buffer correctness evidence",
    )
    if kind == "receipt":
        require(
            relative.endswith("-publication-receipt.json")
            and original_hash is None
            and original_bytes is None
            and archive_bytes is None,
            "only exact durable correctness receipts may be read",
        )
        return decode_document(
            read_frozen(relative, expected, MAX_RECEIPT_BYTES),
            relative,
        )
    require(
        kind in {"baseline", "candidate"}
        and relative.endswith(".json.gz")
        and type(original_hash) is str
        and type(original_bytes) is int
        and type(archive_bytes) is int,
        "only exact lossless changing-buffer archives may be read",
    )
    return read_archive(
        relative,
        expected,
        BASELINE_FIELDS if kind == "baseline" else CANDIDATE_FIELDS,
        original_hash,
        original_bytes,
        archive_bytes,
    )


MANIFEST_FIELDS = frozenset({
    "schema",
    "python",
    "case_denominator",
    "cohort_count",
    "variants_per_cohort",
    "shape_sizes",
    "witnessed_regression_outer_size",
    "witnessed_regression_nested_sizes",
    "witnessed_regression_case_denominator",
    "oracle_source_sha256",
    "recorder_source_sha256",
    "ownership_audit_sha256",
    "original_v5_sha256",
    "pinned_python_sha256",
    "matrix_sha256",
    "published_seed",
    "baseline",
    "families",
})


def manifest_rows(
    manifest: Any,
    loader: Loader,
    *,
    record_digest: RecordDigest = digest,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(
        type(manifest) is dict and set(manifest) == MANIFEST_FIELDS,
        "the exact independently frozen 10,240-case graph manifest "
        "is mandatory",
    )
    fixed_fields(
        manifest,
        {
            "schema": SCHEMA + "-inputs",
            "python": "3.14.6",
            "case_denominator": CASE_COUNT,
            "cohort_count": len(COHORTS),
            "variants_per_cohort": VARIANTS_PER_COHORT,
            "shape_sizes": dict(SHAPE_SIZES),
            "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
            "witnessed_regression_nested_sizes": list(
                WITNESSED_NESTED_SIZES,
            ),
            "witnessed_regression_case_denominator": (
                WITNESSED_CASE_COUNT
            ),
            "oracle_source_sha256": ORACLE_SHA256,
            "recorder_source_sha256": RECORDER_SHA256,
            "ownership_audit_sha256": AUDIT_SHA256,
            "original_v5_sha256": V5_SHA256,
            "pinned_python_sha256": PINNED_PYTHON_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
        },
        "the exact 10,240-case shape matrix and full 64-bit seed",
    )
    matrix = build_matrix()
    seen: set[str] = set()
    declared_baseline = manifest.get("baseline")
    require(
        type(declared_baseline) is dict
        and set(declared_baseline) == {
            "label", "archive", "receipt", "records_sha256",
        }
        and declared_baseline.get("label") == BASELINE_LABEL
        and declared_baseline.get("records_sha256")
        == BASELINE_RECORDS_SHA256,
        "the actual separately frozen two-worker baseline is mandatory",
    )
    receipt_path, receipt_hash = evidence_pin(
        declared_baseline["receipt"],
        seen,
    )
    archive_path, archive_hash = evidence_pin(
        declared_baseline["archive"],
        seen,
    )
    require(
        (
            archive_path,
            archive_hash,
            receipt_path,
            receipt_hash,
        ) == (
            BASELINE_ARCHIVE_RELATIVE,
            BASELINE_ARCHIVE_SHA256,
            BASELINE_RECEIPT_RELATIVE,
            BASELINE_RECEIPT_SHA256,
        )
        and approved_paths(BASELINE_LABEL)
        == (archive_path, receipt_path),
        "the genuine frozen Python report or receipt was substituted",
    )
    receipt = validate_baseline_receipt(
        loader(
            receipt_path,
            receipt_hash,
            "receipt",
            None,
            None,
            None,
        ),
        archive_path,
        archive_hash,
        receipt_path,
    )
    original = validate_baseline(
        loader(
            archive_path,
            archive_hash,
            "baseline",
            receipt["report_uncompressed_sha256"],
            receipt["report_uncompressed_bytes"],
            receipt["report_bytes"],
        ),
        matrix,
        receipt,
        record_digest,
    )
    baseline = {
        "label": BASELINE_LABEL,
        "archive_relative": archive_path,
        "archive_sha256": archive_hash,
        "archive_bytes": BASELINE_ARCHIVE_BYTES,
        "receipt_relative": receipt_path,
        "receipt_sha256": receipt_hash,
        "report_uncompressed_sha256": BASELINE_REPORT_SHA256,
        "report_uncompressed_bytes": BASELINE_REPORT_BYTES,
        "records_sha256": BASELINE_RECORDS_SHA256,
        "reference_pids": receipt["baseline_reference_pids"],
    }
    zero_cohorts = {name: 0 for name in COHORTS}
    zero_apis = {name: 0 for name in APIS}
    zero_targets = {name: 0 for name in TARGETS}
    zero_behaviors = {name: 0 for name in BEHAVIORS}
    zero_witnessed = {
        str(size): 0 for size in WITNESSED_NESTED_SIZES
    }
    rows: list[dict[str, Any]] = [{
        "family": "python",
        "label": FAMILY_LABELS["python"],
        "state": "RUN",
        "case_denominator": CASE_COUNT,
        "passed": CASE_COUNT,
        "failed": 0,
        "not_measured": 0,
        "mismatches_by_cohort": zero_cohorts,
        "mismatches_by_api": zero_apis,
        "mismatches_by_target": zero_targets,
        "mismatches_by_behavior": zero_behaviors,
        "witnessed_regression_mismatches_by_nested_size": (
            zero_witnessed
        ),
    }]
    families = manifest.get("families")
    require(
        type(families) is list and len(families) == len(FAMILY_ORDER),
        "Rust, C, and Zig must all remain visible and independent",
    )
    for family, selected in zip(
        FAMILY_ORDER,
        families,
        strict=True,
    ):
        require(
            type(selected) is dict
            and set(selected) == {
                "family", "candidate_source_sha256", "state",
                "report", "receipt", "superseded",
            }
            and selected.get("family") == family
            and selected.get("state") in {"RUN", "NOT MEASURED"}
            and type(selected.get("superseded")) is list,
            "a native family, real measurement, or historical loss "
            "was concealed",
        )
        adapter = valid_hash(
            selected["candidate_source_sha256"],
            family + " independently owned source",
        )
        history: list[dict[str, Any]] = []
        for previous in selected["superseded"]:
            require(
                type(previous) is dict
                and set(previous) == {"report", "receipt"},
                "a complete superseded correctness report was hidden",
            )
            previous_receipt_path, previous_receipt_hash = evidence_pin(
                previous["receipt"],
                seen,
            )
            previous_report_path, previous_report_hash = evidence_pin(
                previous["report"],
                seen,
            )
            historical_receipt = loader(
                previous_receipt_path,
                previous_receipt_hash,
                "receipt",
                None,
                None,
                None,
            )
            require(
                type(historical_receipt) is dict
                and historical_receipt.get("candidate_family") == family,
                "a historical failure was taken from a different engine",
            )
            historical_adapter = valid_hash(
                historical_receipt.get("candidate_source_sha256"),
                family + " historical genuine source",
            )
            valid_receipt = validate_candidate_receipt(
                historical_receipt,
                family,
                historical_adapter,
                baseline,
                previous_report_path,
                previous_report_hash,
                previous_receipt_path,
            )
            historical_report = loader(
                previous_report_path,
                previous_report_hash,
                "candidate",
                valid_receipt["report_uncompressed_sha256"],
                valid_receipt["report_uncompressed_bytes"],
                valid_receipt["report_bytes"],
            )
            observed_history = validate_candidate(
                historical_report,
                valid_receipt,
                baseline,
                matrix,
                original,
                record_digest,
            )
            history.append({
                "candidate_source_sha256": historical_adapter,
                "report": {
                    "relative": previous_report_path,
                    "sha256": previous_report_hash,
                },
                "receipt": {
                    "relative": previous_receipt_path,
                    "sha256": previous_receipt_hash,
                },
                **observed_history,
            })
        row: dict[str, Any] = {
            "family": family,
            "label": FAMILY_LABELS[family],
            "candidate_source_sha256": adapter,
            "state": selected["state"],
            "case_denominator": CASE_COUNT,
            "superseded": history,
        }
        if selected["state"] == "NOT MEASURED":
            require(
                selected["report"] is None
                and selected["receipt"] is None,
                "a genuinely unmeasured family cannot claim a current run",
            )
            row.update({
                "passed": 0,
                "failed": 0,
                "not_measured": CASE_COUNT,
                "report": None,
                "receipt": None,
                "mismatches_by_cohort": None,
                "mismatches_by_api": None,
                "mismatches_by_target": None,
                "mismatches_by_behavior": None,
                "witnessed_regression_mismatches_by_nested_size": None,
            })
        else:
            report_path, report_hash = evidence_pin(
                selected["report"],
                seen,
            )
            current_receipt_path, current_receipt_hash = evidence_pin(
                selected["receipt"],
                seen,
            )
            candidate_receipt = validate_candidate_receipt(
                loader(
                    current_receipt_path,
                    current_receipt_hash,
                    "receipt",
                    None,
                    None,
                    None,
                ),
                family,
                adapter,
                baseline,
                report_path,
                report_hash,
                current_receipt_path,
            )
            candidate_report = loader(
                report_path,
                report_hash,
                "candidate",
                candidate_receipt["report_uncompressed_sha256"],
                candidate_receipt["report_uncompressed_bytes"],
                candidate_receipt["report_bytes"],
            )
            row.update(validate_candidate(
                candidate_report,
                candidate_receipt,
                baseline,
                matrix,
                original,
                record_digest,
            ))
            row["report"] = {
                "relative": report_path,
                "sha256": report_hash,
            }
            row["receipt"] = {
                "relative": current_receipt_path,
                "sha256": current_receipt_hash,
            }
        require(
            all(
                type(row.get(name)) is int and row[name] >= 0
                for name in ("passed", "failed", "not_measured")
            )
            and row["passed"] + row["failed"] + row["not_measured"]
            == CASE_COUNT,
            "a genuine family silently changed the 10,240-case denominator",
        )
        rows.append(row)
    return baseline, rows


def escape_xml(value: str) -> str:
    require(
        type(value) is str,
        "all accessible changing-buffer graph text must be escaped",
    )
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def make_svg(
    rows: list[dict[str, Any]],
    source: str,
    manifest: str,
) -> bytes:
    require(
        type(rows) is list
        and len(rows) == 4
        and [row.get("family") for row in rows]
        == ["python", *FAMILY_ORDER],
        "show original Python, Rust, C, and Zig in the exact same order",
    )
    source = valid_hash(source, "frozen changing-buffer renderer")
    manifest = valid_hash(manifest, "frozen changing-buffer manifest")
    colors = (
        ("passed", "#15803d", "Matches Python"),
        ("failed", "#dc2626", "Does not match Python"),
        ("not_measured", "#94a3b8", "Not yet measured"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" '
        'height="580" viewBox="0 0 1120 580" role="img" '
        'aria-labelledby="shape-buffer-title shape-buffer-description">',
        '<title id="shape-buffer-title">'
        'Python compatibility when a buffer changes size</title>',
        '<desc id="shape-buffer-description">'
        'Original Python, Rust, C, and Zig are compared with the same '
        '10,240 independently frozen Python checks. Green means a result '
        'matches Python, red means it does not, and gray means it has '
        'not yet been measured. These are compatibility checks, '
        'not speed measurements.</desc>',
        '<rect width="1120" height="580" rx="18" fill="#f8fafc"/>',
        '<text x="42" y="53" fill="#0f172a" '
        'font-family="system-ui,sans-serif" font-size="26" '
        'font-weight="700">Python compatibility when buffers '
        'change size</text>',
        '<text x="42" y="82" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="15">'
        'The same 10,240 Python checks for every implementation '
        '&#183; speed not measured</text>',
    ]
    for index, (_, color, label) in enumerate(colors):
        x = 43 + index * 262
        parts.append(
            f'<rect x="{x}" y="105" width="14" height="14" rx="3" '
            f'fill="{color}"/><text x="{x + 22}" y="117" '
            'fill="#334155" font-family="system-ui,sans-serif" '
            f'font-size="13">{escape_xml(label)}</text>',
        )
    for index, row in enumerate(rows):
        require(
            all(
                type(row.get(name)) is int and row[name] >= 0
                for name in ("passed", "failed", "not_measured")
            )
            and row.get("case_denominator") == CASE_COUNT
            and row["passed"] + row["failed"] + row["not_measured"]
            == CASE_COUNT,
            "a plotted family changed its genuine case denominator",
        )
        top = 151 + index * 80
        label = escape_xml(row["label"])
        if row["not_measured"]:
            caption = "NOT MEASURED"
            caption_color = "#64748b"
        else:
            caption = (
                f'{row["passed"]:,} / {CASE_COUNT:,} match Python'
            )
            caption_color = (
                "#dc2626" if row["failed"] else "#15803d"
            )
        parts.extend((
            f'<text x="43" y="{top + 17}" fill="#0f172a" '
            'font-family="system-ui,sans-serif" font-size="17" '
            f'font-weight="700">{label}</text>',
            f'<text x="1040" y="{top + 17}" '
            f'fill="{caption_color}" text-anchor="end" '
            'font-family="system-ui,sans-serif" font-size="14" '
            f'font-weight="600">{escape_xml(caption)}</text>',
            f'<rect x="43" y="{top + 28}" width="997" height="25" '
            'rx="6" fill="#e2e8f0"/>',
        ))
        cumulative = 0
        for field, color, meaning in colors:
            beginning = 43 + cumulative * 997 // CASE_COUNT
            cumulative += row[field]
            ending = 43 + cumulative * 997 // CASE_COUNT
            if ending > beginning:
                parts.append(
                    f'<rect x="{beginning}" y="{top + 28}" '
                    f'width="{ending - beginning}" height="25" '
                    f'fill="{color}"><title>{label}: '
                    f'{row[field]:,} {escape_xml(meaning.lower())} '
                    f'out of {CASE_COUNT:,}</title></rect>',
                )
    parts.extend((
        '<text x="43" y="491" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="12">'
        'Includes all 64 ways the outer and inner buffers can differ, '
        'including empty and shorter buffers.</text>',
        '<text x="43" y="511" fill="#475569" '
        'font-family="system-ui,sans-serif" font-size="12">'
        'Every failure and earlier result remains in the complete '
        'evidence. Speed and the final holdout are not measured.</text>',
        f'<text x="43" y="550" fill="#64748b" '
        'font-family="system-ui,sans-serif" font-size="10">'
        f'Manifest SHA-256: {manifest} '
        f'&#183; renderer SHA-256: {source}</text>',
        "</svg>\n",
    ))
    return "\n".join(parts).encode("utf-8")


SUMMARY_FIELDS = frozenset({
    "schema",
    "python",
    "source_relative",
    "source_sha256",
    "manifest_relative",
    "manifest_sha256",
    "svg_relative",
    "svg_sha256",
    "oracle_relative",
    "oracle_source_sha256",
    "recorder_relative",
    "recorder_source_sha256",
    "ownership_audit_relative",
    "ownership_audit_sha256",
    "original_v5_relative",
    "original_v5_sha256",
    "pinned_python_sha256",
    "matrix_sha256",
    "published_seed",
    "case_denominator",
    "cohort_count",
    "variants_per_cohort",
    "shape_sizes",
    "witnessed_regression_outer_size",
    "witnessed_regression_nested_sizes",
    "witnessed_regression_case_denominator",
    "independent_of_original_2807_case_denominator",
    "independent_of_memory_1024_case_denominator",
    "independent_of_scanner_2854_case_denominator",
    "baseline",
    "families",
    "actual_candidate_workers",
    "actual_candidate_imports",
    "hidden_cases_read",
    "benchmark_files_read",
    "clock_samples",
    "timing_trials_run",
    "performance",
    "final_holdout_opened",
    "winner_selected",
})


def build_documents(
    manifest: Mapping[str, Any],
    source: str,
    manifest_hash: str,
    loader: Loader,
    *,
    record_digest: RecordDigest = digest,
) -> tuple[bytes, bytes]:
    source = valid_hash(source, "frozen changing-buffer chart renderer")
    manifest_hash = valid_hash(
        manifest_hash,
        "frozen changing-buffer chart manifest",
    )
    baseline, rows = manifest_rows(
        manifest,
        loader,
        record_digest=record_digest,
    )
    svg = make_svg(rows, source, manifest_hash)
    summary = {
        "schema": SCHEMA + "-summary",
        "python": "3.14.6",
        "source_relative": SOURCE_RELATIVE,
        "source_sha256": source,
        "manifest_relative": MANIFEST_RELATIVE,
        "manifest_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "recorder_relative": RECORDER_RELATIVE,
        "recorder_source_sha256": RECORDER_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_denominator": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
        "witnessed_regression_nested_sizes": list(
            WITNESSED_NESTED_SIZES,
        ),
        "witnessed_regression_case_denominator": WITNESSED_CASE_COUNT,
        "independent_of_original_2807_case_denominator": True,
        "independent_of_memory_1024_case_denominator": True,
        "independent_of_scanner_2854_case_denominator": True,
        "baseline": baseline,
        "families": rows,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    require(
        set(summary) == SUMMARY_FIELDS,
        "a complete generated changing-buffer summary was omitted",
    )
    return svg, canonical(summary)


def read_existing_output(
    directory: int,
    basename: str,
    operations: Any = os,
) -> tuple[bytes, os.stat_result] | None:
    require(
        basename in {
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        },
        "only the two independently approved graph outputs may be read",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = operations.open(
            basename,
            flags,
            dir_fd=directory,
        )
    except FileNotFoundError:
        return None
    try:
        first = operations.fstat(descriptor)
        named = operations.stat(
            basename,
            dir_fd=directory,
            follow_symlinks=False,
        )
        require(
            stat.S_ISREG(first.st_mode)
            and (
                first.st_dev, first.st_ino, first.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            )
            and 0 < first.st_size <= MAX_SOURCE_BYTES,
            "an existing output is a symlink, nonregular, or oversized",
        )
        remaining = first.st_size
        blocks: list[bytes] = []
        while remaining:
            block = operations.read(
                descriptor,
                min(CHUNK_BYTES, remaining),
            )
            require(
                type(block) is bytes and bool(block),
                "a genuine previous chart output was truncated",
            )
            remaining -= len(block)
            blocks.append(block)
        require(
            operations.read(descriptor, 1) == b"",
            "a previous chart output gained hidden trailing bytes",
        )
        final = operations.fstat(descriptor)
        named = operations.stat(
            basename,
            dir_fd=directory,
            follow_symlinks=False,
        )
        require(
            (
                first.st_dev, first.st_ino, first.st_size,
            ) == (
                final.st_dev, final.st_ino, final.st_size,
            ) == (
                named.st_dev, named.st_ino, named.st_size,
            ),
            "a previous chart output changed while authenticated",
        )
        return b"".join(blocks), first
    finally:
        operations.close(descriptor)


def validate_previous_outputs(
    old_svg: Any,
    old_summary: Any,
    previous_svg: Any,
    previous_summary: Any,
    source: str,
) -> dict[str, Any]:
    require(
        type(old_svg) is bytes
        and 0 < len(old_svg) <= MAX_SOURCE_BYTES
        and type(old_summary) is bytes
        and 0 < len(old_summary) <= MAX_SOURCE_BYTES,
        "authenticate both complete previous chart files before replacing",
    )
    svg_hash = valid_hash(previous_svg, "previous exact SVG")
    summary_hash = valid_hash(previous_summary, "previous exact summary")
    source = valid_hash(source, "current exact chart source")
    require(
        hashlib.sha256(old_svg).hexdigest() == svg_hash
        and hashlib.sha256(old_summary).hexdigest() == summary_hash,
        "an explicitly frozen previous graph file was substituted",
    )
    document = decode_document(
        old_summary,
        "the complete previous changing-buffer summary",
        MAX_SOURCE_BYTES,
    )
    require(
        set(document) == SUMMARY_FIELDS,
        "a prior graph field, source, or historical result was hidden",
    )
    fixed_fields(
        document,
        {
            "schema": SCHEMA + "-summary",
            "python": "3.14.6",
            "source_relative": SOURCE_RELATIVE,
            "source_sha256": source,
            "manifest_relative": MANIFEST_RELATIVE,
            "svg_relative": SVG_RELATIVE,
            "svg_sha256": svg_hash,
            "oracle_relative": ORACLE_RELATIVE,
            "oracle_source_sha256": ORACLE_SHA256,
            "recorder_relative": RECORDER_RELATIVE,
            "recorder_source_sha256": RECORDER_SHA256,
            "ownership_audit_relative": AUDIT_RELATIVE,
            "ownership_audit_sha256": AUDIT_SHA256,
            "original_v5_relative": V5_RELATIVE,
            "original_v5_sha256": V5_SHA256,
            "pinned_python_sha256": PINNED_PYTHON_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "published_seed": PUBLISHED_SEED,
            "case_denominator": CASE_COUNT,
            "cohort_count": len(COHORTS),
            "variants_per_cohort": VARIANTS_PER_COHORT,
            "shape_sizes": dict(SHAPE_SIZES),
            "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
            "witnessed_regression_nested_sizes": list(
                WITNESSED_NESTED_SIZES,
            ),
            "witnessed_regression_case_denominator": (
                WITNESSED_CASE_COUNT
            ),
            "independent_of_original_2807_case_denominator": True,
            "independent_of_memory_1024_case_denominator": True,
            "independent_of_scanner_2854_case_denominator": True,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_opened": False,
            "winner_selected": False,
        },
        "the prior independently frozen correctness-only graph",
    )
    valid_hash(
        document.get("manifest_sha256"),
        "the exact prior independently authored graph manifest",
    )
    baseline = document.get("baseline")
    require(
        type(baseline) is dict
        and set(baseline) == {
            "label",
            "archive_relative",
            "archive_sha256",
            "archive_bytes",
            "receipt_relative",
            "receipt_sha256",
            "report_uncompressed_sha256",
            "report_uncompressed_bytes",
            "records_sha256",
            "reference_pids",
        }
        and baseline["label"] == BASELINE_LABEL
        and baseline["archive_relative"] == BASELINE_ARCHIVE_RELATIVE
        and baseline["archive_sha256"] == BASELINE_ARCHIVE_SHA256
        and baseline["archive_bytes"] == BASELINE_ARCHIVE_BYTES
        and baseline["receipt_relative"] == BASELINE_RECEIPT_RELATIVE
        and baseline["receipt_sha256"] == BASELINE_RECEIPT_SHA256
        and baseline["report_uncompressed_sha256"]
        == BASELINE_REPORT_SHA256
        and baseline["report_uncompressed_bytes"] == BASELINE_REPORT_BYTES
        and baseline["records_sha256"] == BASELINE_RECORDS_SHA256
        and type(baseline.get("reference_pids")) is list
        and len(baseline["reference_pids"]) == 2
        and all(
            type(pid) is int and pid > 0
            for pid in baseline["reference_pids"]
        )
        and len(set(baseline["reference_pids"])) == 2,
        "the previous graph substituted its genuine original baseline",
    )
    rows = document.get("families")
    require(
        type(rows) is list and len(rows) == 4,
        "a previous graph concealed Python, Rust, C, or Zig",
    )
    seen: set[str] = set()
    for expected, row in zip(
        ("python", *FAMILY_ORDER),
        rows,
        strict=True,
    ):
        require(
            type(row) is dict
            and row.get("family") == expected
            and row.get("label") == FAMILY_LABELS[expected]
            and type(row.get("case_denominator")) is int
            and row["case_denominator"] == CASE_COUNT
            and all(
                type(row.get(name)) is int and row[name] >= 0
                for name in ("passed", "failed", "not_measured")
            )
            and row["passed"] + row["failed"] + row["not_measured"]
            == CASE_COUNT,
            "a previous family changed its genuine case denominator",
        )
        if expected == "python":
            require(
                row.get("state") == "RUN"
                and row["passed"] == CASE_COUNT
                and row["failed"] == 0
                and row["not_measured"] == 0,
                "the previous graph forged the passing Python baseline",
            )
            validate_mismatch_counts(row, 0)
            continue
        require(
            set(row) == {
                "family",
                "label",
                "candidate_source_sha256",
                "state",
                "case_denominator",
                "superseded",
                "passed",
                "failed",
                "not_measured",
                "report",
                "receipt",
                "mismatches_by_cohort",
                "mismatches_by_api",
                "mismatches_by_target",
                "mismatches_by_behavior",
                "witnessed_regression_mismatches_by_nested_size",
            }
            and row.get("state") in {"RUN", "NOT MEASURED"}
            and type(row.get("superseded")) is list,
            "a prior candidate or superseded history was hidden",
        )
        valid_hash(
            row.get("candidate_source_sha256"),
            expected + " previous independent source",
        )
        if row["state"] == "NOT MEASURED":
            require(
                row["passed"] == 0
                and row["failed"] == 0
                and row["not_measured"] == CASE_COUNT
                and row["report"] is None
                and row["receipt"] is None
                and all(
                    row[name] is None
                    for name in (
                        "mismatches_by_cohort",
                        "mismatches_by_api",
                        "mismatches_by_target",
                        "mismatches_by_behavior",
                        "witnessed_regression_mismatches_by_nested_size",
                    )
                ),
                "a previous graph misclassified missing measurements",
            )
        else:
            require(
                row["not_measured"] == 0,
                "a previous actual candidate retained unknown cases",
            )
            validate_mismatch_counts(row, row["failed"])
            evidence_pin(row["report"], seen)
            evidence_pin(row["receipt"], seen)
        for historical in row["superseded"]:
            require(
                type(historical) is dict
                and set(historical) == {
                    "candidate_source_sha256",
                    "report",
                    "receipt",
                    "passed",
                    "failed",
                    "not_measured",
                    "mismatches_by_cohort",
                    "mismatches_by_api",
                    "mismatches_by_target",
                    "mismatches_by_behavior",
                    "witnessed_regression_mismatches_by_nested_size",
                }
                and type(historical.get("passed")) is int
                and type(historical.get("failed")) is int
                and historical["passed"] >= 0
                and historical["failed"] >= 0
                and historical.get("not_measured") == 0
                and historical["passed"] + historical["failed"]
                == CASE_COUNT,
                "a complete superseded genuine candidate was discarded",
            )
            valid_hash(
                historical["candidate_source_sha256"],
                expected + " historical genuine source",
            )
            validate_mismatch_counts(
                historical,
                historical["failed"],
            )
            evidence_pin(historical["report"], seen)
            evidence_pin(historical["receipt"], seen)
    return document


def approve_publication(
    old_svg: bytes | None,
    old_summary: bytes | None,
    new_svg: bytes,
    new_summary: bytes,
    replace: bool,
    previous_svg: str | None,
    previous_summary: str | None,
    source: str,
) -> bool:
    require(
        type(new_svg) is bytes
        and 0 < len(new_svg) <= MAX_SOURCE_BYTES
        and type(new_summary) is bytes
        and 0 < len(new_summary) <= MAX_SOURCE_BYTES
        and type(replace) is bool,
        "bounded complete chart bytes and an explicit replacement "
        "choice are mandatory",
    )
    if not replace:
        require(
            previous_svg is None and previous_summary is None,
            "previous pins cannot silently authorize graph replacement",
        )
        require(
            (old_svg is None and old_summary is None)
            or (old_svg == new_svg and old_summary == new_summary),
            "refusing a partial pair or an unapproved chart overwrite",
        )
        return False
    validate_previous_outputs(
        old_svg,
        old_summary,
        previous_svg,
        previous_summary,
        source,
    )
    return old_svg != new_svg or old_summary != new_summary


def retained_directory(
    directory: int,
    identity: tuple[int, int],
    operations: Any,
) -> None:
    require(
        type(directory) is int
        and directory >= 0
        and type(identity) is tuple
        and len(identity) == 2
        and all(type(number) is int and number >= 0 for number in identity),
        "retain exactly one independently approved no-follow directory",
    )
    observed = operations.fstat(directory)
    require(
        stat.S_ISDIR(observed.st_mode)
        and (observed.st_dev, observed.st_ino) == identity,
        "the retained generated-chart directory was substituted",
    )


def owned_stage(
    directory: int,
    basename: str,
    raw: bytes,
    operations: Any,
) -> tuple[str, tuple[int, int, int]]:
    require(
        basename in {
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        }
        and type(raw) is bytes
        and 0 < len(raw) <= MAX_SOURCE_BYTES,
        "stage only the two exact derived changing-buffer outputs",
    )
    temporary = (
        ".rebar-shape-changing-buffer-overview-v1-stage-"
        + basename
        + "-"
        + str(os.getpid())
        + "-"
        + hashlib.sha256(raw).hexdigest()[:20]
    )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = operations.open(
        temporary,
        flags,
        0o644,
        dir_fd=directory,
    )
    first = operations.fstat(descriptor)
    try:
        require(
            stat.S_ISREG(first.st_mode),
            "the exact staged chart must be a private regular file",
        )
        offset = 0
        while offset < len(raw):
            written = operations.write(
                descriptor,
                raw[offset:],
            )
            require(
                type(written) is int and written > 0,
                "the complete staged chart was not fully written",
            )
            offset += written
        operations.fsync(descriptor)
        current = operations.fstat(descriptor)
        named = operations.stat(
            temporary,
            dir_fd=directory,
            follow_symlinks=False,
        )
        identity = (
            first.st_dev,
            first.st_ino,
            len(raw),
        )
        require(
            (
                current.st_dev,
                current.st_ino,
                current.st_size,
            ) == (
                named.st_dev,
                named.st_ino,
                named.st_size,
            ) == identity,
            "a fully flushed private graph stage was substituted",
        )
        return temporary, identity
    except BaseException:
        try:
            named = operations.stat(
                temporary,
                dir_fd=directory,
                follow_symlinks=False,
            )
            if (named.st_dev, named.st_ino) == (
                first.st_dev,
                first.st_ino,
            ):
                operations.unlink(
                    temporary,
                    dir_fd=directory,
                )
                operations.fsync(directory)
        except (OSError, OverviewError):
            pass
        raise
    finally:
        operations.close(descriptor)


def remove_owned_name(
    directory: int,
    basename: str,
    identity: tuple[int, int, int],
    operations: Any,
) -> None:
    try:
        named = operations.stat(
            basename,
            dir_fd=directory,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return
    require(
        stat.S_ISREG(named.st_mode)
        and (
            named.st_dev,
            named.st_ino,
            named.st_size,
        ) == identity,
        "refusing to remove an unowned graph transaction file",
    )
    operations.unlink(basename, dir_fd=directory)


def atomic_publish_pair(
    directory: int,
    identity: tuple[int, int],
    old_svg: bytes | None,
    old_summary: bytes | None,
    new_svg: bytes,
    new_summary: bytes,
    operations: Any = os,
) -> None:
    """Publish both fresh files or safely replace and restore both together."""
    retained_directory(directory, identity, operations)
    require(
        (old_svg is None) is (old_summary is None),
        "a partial generated chart pair cannot be published",
    )
    fresh = old_svg is None
    pairs = (
        (
            safe_parts(SVG_RELATIVE)[-1],
            old_svg,
            new_svg,
        ),
        (
            safe_parts(SUMMARY_RELATIVE)[-1],
            old_summary,
            new_summary,
        ),
    )
    stages: dict[str, tuple[str, tuple[int, int, int]]] = {}
    backups: dict[str, tuple[str, tuple[int, int, int]]] = {}
    committed: list[str] = []
    originals = {
        name: previous
        for name, previous, _ in pairs
    }
    updates = {
        name: updated
        for name, _, updated in pairs
    }
    try:
        for name, previous, updated in pairs:
            current = read_existing_output(
                directory,
                name,
                operations,
            )
            require(
                (
                    fresh and current is None
                )
                or (
                    not fresh
                    and current is not None
                    and current[0] == previous
                ),
                "the complete graph pair changed before staging",
            )
            stages[name] = owned_stage(
                directory,
                name,
                updated,
                operations,
            )
            retained_directory(directory, identity, operations)
        if not fresh:
            for name, previous, _ in pairs:
                current = read_existing_output(
                    directory,
                    name,
                    operations,
                )
                require(
                    current is not None and current[0] == previous,
                    "the authenticated chart changed before backup",
                )
                backup = (
                    ".rebar-shape-changing-buffer-overview-v1-backup-"
                    + name
                    + "-"
                    + str(os.getpid())
                    + "-"
                    + hashlib.sha256(previous).hexdigest()[:20]
                )
                operations.link(
                    name,
                    backup,
                    src_dir_fd=directory,
                    dst_dir_fd=directory,
                    follow_symlinks=False,
                )
                named = operations.stat(
                    backup,
                    dir_fd=directory,
                    follow_symlinks=False,
                )
                original = current[1]
                require(
                    stat.S_ISREG(named.st_mode)
                    and (
                        named.st_dev,
                        named.st_ino,
                        named.st_size,
                    ) == (
                        original.st_dev,
                        original.st_ino,
                        original.st_size,
                    ),
                    "a rollback backup escaped its exact previous graph",
                )
                backups[name] = (
                    backup,
                    (
                        named.st_dev,
                        named.st_ino,
                        named.st_size,
                    ),
                )
                retained_directory(directory, identity, operations)
        operations.fsync(directory)
        for name, previous, updated in pairs:
            current = read_existing_output(
                directory,
                name,
                operations,
            )
            require(
                (
                    fresh and current is None
                )
                or (
                    not fresh
                    and current is not None
                    and current[0] == previous
                ),
                "a graph output changed immediately before commit",
            )
            temporary, staged_identity = stages[name]
            named = operations.stat(
                temporary,
                dir_fd=directory,
                follow_symlinks=False,
            )
            require(
                (
                    named.st_dev,
                    named.st_ino,
                    named.st_size,
                ) == staged_identity,
                "the fully staged changing-buffer output was replaced",
            )
            if fresh:
                operations.link(
                    temporary,
                    name,
                    src_dir_fd=directory,
                    dst_dir_fd=directory,
                    follow_symlinks=False,
                )
            else:
                operations.replace(
                    temporary,
                    name,
                    src_dir_fd=directory,
                    dst_dir_fd=directory,
                )
            committed.append(name)
            observed = read_existing_output(
                directory,
                name,
                operations,
            )
            require(
                observed is not None and observed[0] == updated,
                "a committed changing-buffer graph failed exact readback",
            )
            retained_directory(directory, identity, operations)
        operations.fsync(directory)
        for name, _, updated in pairs:
            observed = read_existing_output(
                directory,
                name,
                operations,
            )
            require(
                observed is not None and observed[0] == updated,
                "the complete committed graph pair failed verification",
            )
        retained_directory(directory, identity, operations)
    except BaseException as original_error:
        rollback_error: BaseException | None = None
        try:
            for name in reversed(committed):
                observed = read_existing_output(
                    directory,
                    name,
                    operations,
                )
                require(
                    observed is not None
                    and observed[0] == updates[name],
                    "refusing to roll back an externally altered graph",
                )
                if fresh:
                    temporary, stage_identity = stages[name]
                    del temporary
                    remove_owned_name(
                        directory,
                        name,
                        stage_identity,
                        operations,
                    )
                else:
                    backup, backup_identity = backups[name]
                    named = operations.stat(
                        backup,
                        dir_fd=directory,
                        follow_symlinks=False,
                    )
                    require(
                        (
                            named.st_dev,
                            named.st_ino,
                            named.st_size,
                        ) == backup_identity,
                        "a rollback backup was substituted",
                    )
                    operations.replace(
                        backup,
                        name,
                        src_dir_fd=directory,
                        dst_dir_fd=directory,
                    )
                    restored = read_existing_output(
                        directory,
                        name,
                        operations,
                    )
                    require(
                        restored is not None
                        and restored[0] == originals[name],
                        "an exact previous graph could not be restored",
                    )
                    del backups[name]
            for name, (
                backup,
                backup_identity,
            ) in list(backups.items()):
                remove_owned_name(
                    directory,
                    backup,
                    backup_identity,
                    operations,
                )
                del backups[name]
            for name, (
                temporary,
                stage_identity,
            ) in list(stages.items()):
                if fresh or name not in committed:
                    remove_owned_name(
                        directory,
                        temporary,
                        stage_identity,
                        operations,
                    )
            operations.fsync(directory)
            for name, previous, _ in pairs:
                observed = read_existing_output(
                    directory,
                    name,
                    operations,
                )
                require(
                    (
                        fresh and observed is None
                    )
                    or (
                        not fresh
                        and observed is not None
                        and observed[0] == previous
                    ),
                    "the failed transaction did not restore the full pair",
                )
        except BaseException as error:
            rollback_error = error
        if rollback_error is not None:
            raise OverviewError(
                "changing-buffer graph publication failed; preserve "
                "owned rollback files because full recovery is unverified",
            ) from rollback_error
        raise original_error
    for name, (
        backup,
        backup_identity,
    ) in list(backups.items()):
        remove_owned_name(
            directory,
            backup,
            backup_identity,
            operations,
        )
        del backups[name]
    if fresh:
        for _, (
            temporary,
            stage_identity,
        ) in list(stages.items()):
            remove_owned_name(
                directory,
                temporary,
                stage_identity,
                operations,
            )
    operations.fsync(directory)
    for name, _, updated in pairs:
        observed = read_existing_output(
            directory,
            name,
            operations,
        )
        require(
            observed is not None and observed[0] == updated,
            "the final safe graph pair changed after publication",
        )


def render(
    source: str,
    manifest_relative: str,
    manifest_hash: str,
    *,
    replace: bool = False,
    previous_svg: str | None = None,
    previous_summary: str | None = None,
) -> dict[str, Any]:
    verify_runtime()
    source = valid_hash(source, "explicitly frozen chart renderer")
    manifest_hash = valid_hash(
        manifest_hash,
        "independently frozen immutable graph inputs",
    )
    require(
        manifest_relative == MANIFEST_RELATIVE,
        "render only the independently authored frozen inputs manifest",
    )
    for relative, expected in (
        (SOURCE_RELATIVE, source),
        (ORACLE_RELATIVE, ORACLE_SHA256),
        (RECORDER_RELATIVE, RECORDER_SHA256),
        (AUDIT_RELATIVE, AUDIT_SHA256),
        (V5_RELATIVE, V5_SHA256),
        (V2_RELATIVE, V2_SHA256),
    ):
        read_frozen(relative, expected, MAX_SOURCE_BYTES)
    authenticate_external(
        PINNED_PYTHON,
        PINNED_PYTHON_SHA256,
        MAX_BINARY_BYTES,
    )
    for filename, expected in PINNED_STDLIB_SOURCES.values():
        authenticate_external(
            PINNED_STDLIB_DIRECTORY + filename,
            expected,
            MAX_SOURCE_BYTES,
        )
    manifest = decode_document(
        read_frozen(
            MANIFEST_RELATIVE,
            manifest_hash,
            MAX_SOURCE_BYTES,
        ),
        "the immutable independently authored changing-buffer manifest",
        MAX_SOURCE_BYTES,
    )
    svg, summary = build_documents(
        manifest,
        source,
        manifest_hash,
        actual_loader,
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    opened: list[int] = []
    replaced = False
    try:
        current = os.open(ROOT, flags)
        opened.append(current)
        for part in ("docs", "evidence"):
            current = os.open(
                part,
                flags,
                dir_fd=current,
            )
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact independently owned graph parent was replaced",
            )
        directory_info = os.fstat(current)
        identity = (
            directory_info.st_dev,
            directory_info.st_ino,
        )
        old_svg_value = read_existing_output(
            current,
            safe_parts(SVG_RELATIVE)[-1],
        )
        old_summary_value = read_existing_output(
            current,
            safe_parts(SUMMARY_RELATIVE)[-1],
        )
        old_svg = (
            None if old_svg_value is None else old_svg_value[0]
        )
        old_summary = (
            None if old_summary_value is None else old_summary_value[0]
        )
        replaced = approve_publication(
            old_svg,
            old_summary,
            svg,
            summary,
            replace,
            previous_svg,
            previous_summary,
            source,
        )
        if old_svg is None or replaced:
            atomic_publish_pair(
                current,
                identity,
                old_svg,
                old_summary,
                svg,
                summary,
            )
        else:
            require(
                old_svg == svg and old_summary == summary,
                "an identical no-overwrite graph pair was substituted",
            )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)
    verify_runtime()
    document = decode_document(
        summary,
        "the generated complete changing-buffer summary",
        MAX_SOURCE_BYTES,
    )
    return {
        "schema": SCHEMA + "-rendered",
        "status": "PASS",
        "source_sha256": source,
        "manifest_relative": MANIFEST_RELATIVE,
        "manifest_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "summary_relative": SUMMARY_RELATIVE,
        "summary_sha256": hashlib.sha256(summary).hexdigest(),
        "case_denominator": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "published_seed": PUBLISHED_SEED,
        "replaced_generated_pair": replaced,
        "rows": [
            {
                "family": row["family"],
                "passed": row["passed"],
                "failed": row["failed"],
                "not_measured": row["not_measured"],
            }
            for row in document["families"]
        ],
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }


class SourceOnlyBoundary:
    """Prevent every actual external effect during synthetic chart tests."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "reads": 0,
            "writes": 0,
            "workers": 0,
            "imports": 0,
            "threads": 0,
            "clocks": 0,
            "garbage_collections": 0,
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
        original = getattr(owner, name)
        self.originals.append((owner, name, original))

        def denied(*args: Any, **kwargs: Any) -> Any:
            actual = category
            if category == "reads":
                mode = (
                    args[1]
                    if len(args) > 1
                    else kwargs.get("mode", "r")
                )
                if type(mode) is str and any(
                    item in mode for item in "wax+"
                ):
                    actual = "writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY
                    | os.O_RDWR
                    | os.O_CREAT
                    | os.O_TRUNC
                    | os.O_APPEND
                ):
                    actual = "writes"
            self.blocked[actual] += 1
            raise SourceOnlyError(
                "source-only changing-buffer controls forbid " + actual,
            )

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        for owner, name, category in (
            (builtins, "open", "reads"),
            (io, "open", "reads"),
            (os, "open", "reads"),
            (os, "stat", "reads"),
            (os, "lstat", "reads"),
            (os, "scandir", "reads"),
            (os, "listdir", "reads"),
            (os, "readlink", "reads"),
            (os, "write", "writes"),
            (os, "replace", "writes"),
            (os, "rename", "writes"),
            (os, "link", "writes"),
            (os, "unlink", "writes"),
            (os, "remove", "writes"),
            (os, "mkdir", "writes"),
            (os, "makedirs", "writes"),
            (os, "fsync", "writes"),
            (subprocess, "run", "workers"),
            (subprocess, "Popen", "workers"),
            (os, "system", "workers"),
            (os, "fork", "workers"),
            (os, "posix_spawn", "workers"),
            (importlib, "import_module", "imports"),
            (builtins, "__import__", "imports"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clocks"),
            (time, "time_ns", "clocks"),
            (time, "monotonic", "clocks"),
            (time, "monotonic_ns", "clocks"),
            (time, "perf_counter", "clocks"),
            (time, "perf_counter_ns", "clocks"),
            (gc, "collect", "garbage_collections"),
            (os, "urandom", "randomness"),
        ):
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


def synthetic_stream(
    raw: bytes,
    *,
    archive: bytes | None = None,
    archive_hash: str | None = None,
    original_hash: str | None = None,
    original_bytes: int | None = None,
    fields: frozenset[str] = frozenset({"proof", "value"}),
) -> dict[str, Any]:
    require(
        type(raw) is bytes and bool(raw),
        "an exclusively in-memory complete gzip control is mandatory",
    )
    if archive is None:
        compressor = zlib.compressobj(
            level=9,
            wbits=16 + zlib.MAX_WBITS,
        )
        archive = compressor.compress(raw) + compressor.flush()
    require(
        type(archive) is bytes and bool(archive),
        "an exclusively in-memory gzip member is mandatory",
    )
    selected_archive = (
        hashlib.sha256(archive).hexdigest()
        if archive_hash is None
        else archive_hash
    )
    selected_original = (
        hashlib.sha256(raw).hexdigest()
        if original_hash is None
        else original_hash
    )
    selected_bytes = (
        len(raw) if original_bytes is None else original_bytes
    )
    descriptor = -10_240_071
    position = 0
    previous = os.read

    def read_memory(
        selected: int,
        requested: int,
    ) -> bytes:
        nonlocal position
        require(
            selected == descriptor
            and type(requested) is int
            and requested > 0,
            "a synthetic gzip attempted to read a genuine descriptor",
        )
        block = archive[position:position + requested]
        position += len(block)
        return block

    os.read = read_memory
    try:
        stream = VerifiedGzipReader(
            descriptor,
            len(archive),
            selected_archive,
            selected_bytes,
            selected_original,
        )
        value = StreamingObject(stream).select(fields)
        require(
            stream.finished and position == len(archive),
            "the complete in-memory gzip was not authenticated",
        )
        return value
    finally:
        os.read = previous


def synthetic_owner(
    relative: str,
    source: str,
    index: int,
    *,
    external: bool = False,
) -> dict[str, Any]:
    return {
        "path" if external else "relative": relative,
        "sha256": valid_hash(source, relative),
        "bytes": 4_096 + index,
        "device": 7,
        "inode": 100_000 + index,
    }


def synthetic_tool_closure() -> dict[str, Any]:
    return {
        "recorder": synthetic_owner(
            RECORDER_RELATIVE, RECORDER_SHA256, 1,
        ),
        "shape_oracle": synthetic_owner(
            ORACLE_RELATIVE, ORACLE_SHA256, 2,
        ),
        "original_v5": synthetic_owner(
            V5_RELATIVE, V5_SHA256, 3,
        ),
        "from_scratch_audit_v3": synthetic_owner(
            AUDIT_RELATIVE, AUDIT_SHA256, 4,
        ),
        "pinned_python": synthetic_owner(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            5,
            external=True,
        ),
    }


def synthetic_standard_owners() -> dict[str, Any]:
    result = {
        "oracle": synthetic_owner(
            ROOT + "/" + ORACLE_RELATIVE,
            ORACLE_SHA256,
            11,
            external=True,
        ),
        "python": synthetic_owner(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            12,
            external=True,
        ),
        "v5_guard": synthetic_owner(
            ROOT + "/" + V5_RELATIVE,
            V5_SHA256,
            13,
            external=True,
        ),
        "ownership_audit": synthetic_owner(
            ROOT + "/" + AUDIT_RELATIVE,
            AUDIT_SHA256,
            14,
            external=True,
        ),
    }
    for index, (
        name,
        (filename, source),
    ) in enumerate(PINNED_STDLIB_SOURCES.items(), start=15):
        result[name] = synthetic_owner(
            PINNED_STDLIB_DIRECTORY + filename,
            source,
            index,
            external=True,
        )
    return result


def synthetic_outcome(case: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": "return",
        "stage": case["api"],
        "value": {
            "type": "bytes",
            "hex": "58",
        },
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
        "subject_after": {"type": "bytes", "hex": ""},
        "template_after": {"type": "bytes", "hex": "58"},
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


def synthetic_guard(family: str) -> dict[str, Any]:
    ffi = FAMILY_SPECS[family][4]
    guard = {
        name: True for name in GUARD_TRUE
    }
    guard.update({
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "owned_native_ffi_allowed": ffi,
        "trusted_stdlib_ctypes_preloaded": ffi,
        "trusted_stdlib_ctypes_builtin_verified": ffi,
        "trusted_stdlib_ctypes_pythonapi_initialized": ffi,
        "trusted_stdlib_ctypes_source_sha256": (
            TRUSTED_CTYPES_SHA256 if ffi else None
        ),
        "cached_original_matcher_descendant_count": 0,
        "cached_original_holder_count": 0,
        "owned_ctypes_load_count": 1 if ffi else 0,
        "owned_ctypes_symbol_count": 2 if ffi else 0,
    })
    return guard


def synthetic_family_closure(
    family: str,
    adapter: str,
    engine: str,
    bridge: str,
) -> dict[str, Any]:
    adapter_path, engine_path, bridge_path, source_paths, _ = (
        FAMILY_SPECS[family]
    )
    source_map = {
        relative: (
            adapter
            if relative == adapter_path
            else hashlib.sha256(
                (family + ":" + relative).encode("ascii"),
            ).hexdigest()
        )
        for relative in source_paths
    }
    native = {engine_path: engine}
    if bridge_path != engine_path:
        native[bridge_path] = bridge
    manifest = {
        "family": family,
        "candidate_source_sha256": adapter,
        "native_engine_sha256": engine,
        "native_bridge_sha256": bridge,
        "source_sha256": dict(sorted(source_map.items())),
        "native_sha256": dict(sorted(native.items())),
        "immutable_policy_sha256": {
            V2_RELATIVE: V2_SHA256,
            V5_RELATIVE: V5_SHA256,
        },
    }
    return {
        "family": family,
        "manifest": manifest,
        "source_owners": {
            relative: synthetic_owner(relative, source, 100 + index)
            for index, (relative, source) in enumerate(
                manifest["source_sha256"].items(),
            )
        },
        "native_owners": {
            relative: synthetic_owner(relative, source, 200 + index)
            for index, (relative, source) in enumerate(
                manifest["native_sha256"].items(),
            )
        },
        "policy_owners": {
            V2_RELATIVE: synthetic_owner(
                V2_RELATIVE, V2_SHA256, 300,
            ),
            V5_RELATIVE: synthetic_owner(
                V5_RELATIVE, V5_SHA256, 301,
            ),
        },
        "oracle_owner": synthetic_owner(
            AUDIT_RELATIVE, AUDIT_SHA256, 302,
        ),
        "python_owner": synthetic_owner(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            303,
            external=True,
        ),
    }


def synthetic_reference(
    role: str,
    pid: int,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
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
        "records_sha256": BASELINE_RECORDS_SHA256,
        "records": records,
        "source_owners": synthetic_standard_owners(),
        "reference_guard": {
            "candidate_import_count": 0,
            "external_regex_import_count": 0,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "required_method_guard_checks": 2 * CASE_COUNT,
            "future_candidate_guard_relative": V5_RELATIVE,
            "future_candidate_guard_sha256": V5_SHA256,
            "future_ownership_audit_relative": AUDIT_RELATIVE,
            "future_ownership_audit_sha256": AUDIT_SHA256,
            "future_candidate_guard_installed": False,
        },
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


def synthetic_process(
    worker: Mapping[str, Any],
    role: str,
) -> dict[str, Any]:
    return {
        "role": role,
        "pid": worker["pid"],
        "returncode": 0,
        "stdout": capture_stream(canonical(dict(worker))),
        "stderr": capture_stream(b""),
    }


def synthetic_fixtures() -> tuple[
    dict[str, Any],
    dict[tuple[str, str], dict[str, Any]],
    RecordDigest,
    list[dict[str, Any]],
]:
    matrix = build_matrix()
    records = [{
        "case": case["case"],
        "cohort": case["cohort"],
        "api": case["api"],
        "outer_size": case["outer_size"],
        "nested_size": case["nested_size"],
        "outcome": synthetic_outcome(case),
    } for case in matrix]
    original_synthetic_hash = digest(records)

    def synthetic_digest(value: Any) -> str:
        actual = digest(value)
        if actual == original_synthetic_hash:
            return BASELINE_RECORDS_SHA256
        return actual

    owners = synthetic_tool_closure()
    first = synthetic_reference("reference_a", 82, records)
    second = synthetic_reference("reference_b", 83, records)
    controller = {
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
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "source_owners": synthetic_standard_owners(),
        "reference_a": first,
        "reference_b": second,
        "reference_a_process": synthetic_process(
            first, "reference_a",
        ),
        "reference_b_process": synthetic_process(
            second, "reference_b",
        ),
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
    bound = BASELINE_REPORT_BYTES + 1
    baseline_report = {
        "schema": RECORDER_SCHEMA + "-complete-baseline-report",
        "status": "PASS",
        **source_fields(BASELINE_LABEL),
        "source_closure_before": owners,
        "source_closure_after": owners,
        "source_closure_unchanged": True,
        "complete_baseline_process_stdout": capture_stream(
            canonical(controller),
        ),
        "complete_baseline_process_stderr": capture_stream(b""),
        "lossless_evidence_layout": (
            "one-authenticated-baseline-controller-stdout"
        ),
        "duplicate_reference_vectors": False,
        "mathematical_report_bytes_upper_bound": bound,
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "structured_baseline_failure_type": None,
        "structured_baseline_failure_message": None,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": [82, 83],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "actual_baseline_controller_pid": 81,
        "actual_baseline_process_returncode": 0,
        "actual_baseline_process_signal": None,
        "actual_baseline_process_timed_out": False,
        "actual_baseline_process_spawn_error": None,
        "all_failure_reasons": [],
        "failure_count": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    baseline_receipt = {
        "schema": (
            RECORDER_SCHEMA + "-durable-baseline-publication-receipt"
        ),
        "status": "PASS",
        "baseline_result_status": "PASS",
        **source_fields(BASELINE_LABEL),
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_reference_pids": [82, 83],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "source_closure_before": owners,
        "source_closure_after": owners,
        "source_closure_unchanged": True,
        "lossless_evidence_layout": (
            "one-authenticated-baseline-controller-stdout"
        ),
        "duplicate_reference_vectors": False,
        "mathematical_report_bytes_upper_bound": bound,
        "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "report_relative": BASELINE_ARCHIVE_RELATIVE,
        "report_sha256": BASELINE_ARCHIVE_SHA256,
        "report_bytes": BASELINE_ARCHIVE_BYTES,
        "report_uncompressed_sha256": BASELINE_REPORT_SHA256,
        "report_uncompressed_bytes": BASELINE_REPORT_BYTES,
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": BASELINE_RECEIPT_RELATIVE,
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
    evidence: dict[tuple[str, str], dict[str, Any]] = {
        (
            BASELINE_RECEIPT_RELATIVE,
            BASELINE_RECEIPT_SHA256,
        ): baseline_receipt,
        (
            BASELINE_ARCHIVE_RELATIVE,
            BASELINE_ARCHIVE_SHA256,
        ): baseline_report,
    }
    adapters = {
        family: hashlib.sha256(
            ("synthetic-shape-adapter:" + family).encode("ascii"),
        ).hexdigest()
        for family in FAMILY_ORDER
    }

    def add_candidate(
        family: str,
        label: str,
        mismatch_count: int,
        adapter: str,
    ) -> tuple[dict[str, str], dict[str, str]]:
        engine = hashlib.sha256(
            (
                "synthetic-shape-engine:" + family + ":" + label
            ).encode("ascii"),
        ).hexdigest()
        bridge = (
            engine
            if family == "c"
            else hashlib.sha256(
                (
                    "synthetic-shape-bridge:" + family + ":" + label
                ).encode("ascii"),
            ).hexdigest()
        )
        closure = synthetic_family_closure(
            family,
            adapter,
            engine,
            bridge,
        )
        selected_records: list[dict[str, Any]] = []
        mismatch_rows: list[dict[str, Any]] = []
        by_cohort = {name: 0 for name in COHORTS}
        by_api = {name: 0 for name in APIS}
        by_target = {name: 0 for name in TARGETS}
        by_behavior = {name: 0 for name in BEHAVIORS}
        witnessed = {
            str(size): 0 for size in WITNESSED_NESTED_SIZES
        }
        for index, (case, original) in enumerate(
            zip(matrix, records, strict=True),
        ):
            if index < mismatch_count:
                outcome = copy.deepcopy(original["outcome"])
                outcome["value"] = {
                    "type": "bytes",
                    "hex": "59",
                }
                observed = {
                    **original,
                    "outcome": outcome,
                }
                by_cohort[case["cohort"]] += 1
                by_api[case["api"]] += 1
                by_target[case["target"]] += 1
                by_behavior[case["behavior"]] += 1
                if (
                    case["outer_size"] == WITNESSED_OUTER_SIZE
                    and case["nested_size"]
                    in WITNESSED_NESTED_SIZES
                ):
                    witnessed[str(case["nested_size"])] += 1
                mismatch_rows.append({
                    "case": case["case"],
                    "cohort": case["cohort"],
                    "api": case["api"],
                    "target": case["target"],
                    "behavior": case["behavior"],
                    "outer_size": case["outer_size"],
                    "nested_size": case["nested_size"],
                    "input": case,
                    "baseline_outcome": original["outcome"],
                    "candidate_outcome": outcome,
                })
            else:
                observed = original
            selected_records.append(observed)
        records_hash = synthetic_digest(selected_records)
        report_path, receipt_path = approved_paths(label, family)
        report_hash = hashlib.sha256(
            ("synthetic-report:" + family + ":" + label).encode(
                "ascii",
            ),
        ).hexdigest()
        receipt_hash = hashlib.sha256(
            ("synthetic-receipt:" + family + ":" + label).encode(
                "ascii",
            ),
        ).hexdigest()
        imports = 3 if family == "zig" else 2
        guard = synthetic_guard(family)
        native_paths = FAMILY_SPECS[family]
        worker = {
            "schema": RECORDER_SCHEMA + "-isolated-candidate-worker",
            "status": "OBSERVED",
            "python": "3.14.6",
            "role": "candidate-" + family,
            "pid": 200 + len(evidence),
            "candidate_family": family,
            **source_fields(BASELINE_LABEL),
            "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
            "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
            "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
            "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
            "baseline_records_sha256": BASELINE_RECORDS_SHA256,
            "baseline_reference_pids": [82, 83],
            "baseline_receipt_owner": synthetic_owner(
                BASELINE_RECEIPT_RELATIVE,
                BASELINE_RECEIPT_SHA256,
                401,
            ),
            "baseline_archive_owner": synthetic_owner(
                BASELINE_ARCHIVE_RELATIVE,
                BASELINE_ARCHIVE_SHA256,
                402,
            ),
            "source_provenance": owners,
            "audit_manifest": closure["manifest"],
            "owned_source_closure": closure,
            "native_provenance": {
                "source": closure["source_owners"][native_paths[0]],
                "native_engine": closure["native_owners"][
                    native_paths[1]
                ],
                "native_bridge": closure["native_owners"][
                    native_paths[2]
                ],
            },
            "matcher_guard": guard,
            "records_sha256": records_hash,
            "records": selected_records,
            "validated_prior_reference_workers": 2,
            "actual_reference_workers": 0,
            "actual_candidate_workers": 1,
            "actual_candidate_imports": imports,
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
        worker_stdout = capture_stream(canonical(worker))
        bound_candidate = max(
            len(worker_stdout["base64"]) + 1_048_576,
            2_097_152,
        )
        status = "FAIL" if mismatch_count else "PASS"
        reasons = (
            [
                "the owned candidate differs on "
                + str(mismatch_count)
                + " frozen changing-buffer cases",
            ]
            if mismatch_count
            else []
        )
        report = {
            "schema": RECORDER_SCHEMA + "-complete-candidate-report",
            "status": status,
            "python": "3.14.6",
            "label": label,
            "candidate_family": family,
            "candidate_source_sha256": adapter,
            "native_engine_sha256": engine,
            "native_bridge_sha256": bridge,
            "baseline_label": BASELINE_LABEL,
            "recorder_relative": RECORDER_RELATIVE,
            "recorder_source_sha256": RECORDER_SHA256,
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
            "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
            "witnessed_regression_nested_sizes": list(
                WITNESSED_NESTED_SIZES,
            ),
            "witnessed_regression_cohort_count": len(
                WITNESSED_NESTED_SIZES,
            ),
            "witnessed_regression_case_count": WITNESSED_CASE_COUNT,
            "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
            "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
            "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
            "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
            "baseline_records_sha256": BASELINE_RECORDS_SHA256,
            "baseline_reference_pids": [82, 83],
            "candidate_owner_before": closure,
            "candidate_owner_after": closure,
            "candidate_owner_unchanged": True,
            "complete_candidate_process_stdout": worker_stdout,
            "complete_candidate_process_stderr": capture_stream(b""),
            "lossless_evidence_layout": (
                "one-authenticated-candidate-worker-stdout-and-full-mismatches"
            ),
            "duplicate_candidate_vectors": False,
            "duplicate_reference_vectors": False,
            "mathematical_report_bytes_upper_bound": bound_candidate,
            "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
            "validated_baseline_record_count": CASE_COUNT,
            "validated_candidate_record_count": CASE_COUNT,
            "candidate_records_sha256": records_hash,
            "mismatch_count": mismatch_count,
            "all_mismatches": mismatch_rows,
            "mismatches_by_cohort": by_cohort,
            "mismatches_by_api": by_api,
            "mismatches_by_target": by_target,
            "mismatches_by_behavior": by_behavior,
            "witnessed_regression_mismatches_by_nested_size": witnessed,
            "all_mismatches_preserved": True,
            "matcher_guard": guard,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
            "validated_prior_reference_workers": 2,
            "actual_reference_workers": 0,
            "actual_candidate_workers": 1,
            "actual_candidate_imports": imports,
            "actual_candidate_process_invocations": 1,
            "actual_candidate_pid": worker["pid"],
            "actual_candidate_process_returncode": 0,
            "actual_candidate_process_signal": None,
            "actual_candidate_process_timed_out": False,
            "actual_candidate_process_spawn_error": None,
            "all_failure_reasons": reasons,
            "failure_count": len(reasons),
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "source_to_binary_reproducibility": "NOT ESTABLISHED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        report_uncompressed_hash = hashlib.sha256(
            ("synthetic-original:" + family + ":" + label).encode(
                "ascii",
            ),
        ).hexdigest()
        receipt = {
            "schema": (
                RECORDER_SCHEMA
                + "-durable-candidate-publication-receipt"
            ),
            "status": "PASS",
            "candidate_result_status": status,
            "python": "3.14.6",
            "label": label,
            "candidate_family": family,
            "candidate_source_sha256": adapter,
            "native_engine_sha256": engine,
            "native_bridge_sha256": bridge,
            "baseline_label": BASELINE_LABEL,
            "recorder_source_sha256": RECORDER_SHA256,
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
            "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
            "witnessed_regression_nested_sizes": list(
                WITNESSED_NESTED_SIZES,
            ),
            "witnessed_regression_case_count": WITNESSED_CASE_COUNT,
            "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
            "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
            "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
            "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
            "baseline_records_sha256": BASELINE_RECORDS_SHA256,
            "baseline_reference_pids": [82, 83],
            "validated_baseline_record_count": CASE_COUNT,
            "validated_candidate_record_count": CASE_COUNT,
            "candidate_records_sha256": records_hash,
            "mismatch_count": mismatch_count,
            "mismatches_by_cohort": by_cohort,
            "mismatches_by_api": by_api,
            "mismatches_by_target": by_target,
            "mismatches_by_behavior": by_behavior,
            "witnessed_regression_mismatches_by_nested_size": witnessed,
            "all_mismatches_preserved": True,
            "actual_method_guard_checks": 2 * CASE_COUNT,
            "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
            "validated_prior_reference_workers": 2,
            "actual_reference_workers": 0,
            "actual_candidate_workers": 1,
            "actual_candidate_imports": imports,
            "actual_candidate_process_invocations": 1,
            "candidate_owner_before": closure,
            "candidate_owner_after": closure,
            "candidate_owner_unchanged": True,
            "lossless_evidence_layout": report[
                "lossless_evidence_layout"
            ],
            "duplicate_candidate_vectors": False,
            "duplicate_reference_vectors": False,
            "mathematical_report_bytes_upper_bound": bound_candidate,
            "maximum_report_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
            "report_relative": report_path,
            "report_sha256": report_hash,
            "report_bytes": 8_192,
            "report_uncompressed_sha256": report_uncompressed_hash,
            "report_uncompressed_bytes": 16_384,
            "report_compression": "gzip-mtime-zero-level-9",
            "report_file_fsync_completed": True,
            "report_directory_fsync_completed": True,
            "report_atomic_no_overwrite_link": True,
            "report_complete_readback_verified": True,
            "receipt_relative": receipt_path,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "source_to_binary_reproducibility": "NOT ESTABLISHED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        evidence[(report_path, report_hash)] = report
        evidence[(receipt_path, receipt_hash)] = receipt
        return (
            {"relative": report_path, "sha256": report_hash},
            {"relative": receipt_path, "sha256": receipt_hash},
        )

    rust_report, rust_receipt = add_candidate(
        "rust",
        "synthetic-pass-v1",
        0,
        adapters["rust"],
    )
    c_report, c_receipt = add_candidate(
        "c",
        "synthetic-current-failure-v1",
        37,
        adapters["c"],
    )
    historical_adapter = hashlib.sha256(
        b"synthetic-historical-c-adapter",
    ).hexdigest()
    previous_report, previous_receipt = add_candidate(
        "c",
        "synthetic-prior-failure-v1",
        53,
        historical_adapter,
    )
    manifest = {
        "schema": SCHEMA + "-inputs",
        "python": "3.14.6",
        "case_denominator": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "shape_sizes": dict(SHAPE_SIZES),
        "witnessed_regression_outer_size": WITNESSED_OUTER_SIZE,
        "witnessed_regression_nested_sizes": list(
            WITNESSED_NESTED_SIZES,
        ),
        "witnessed_regression_case_denominator": WITNESSED_CASE_COUNT,
        "oracle_source_sha256": ORACLE_SHA256,
        "recorder_source_sha256": RECORDER_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_sha256": V5_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "baseline": {
            "label": BASELINE_LABEL,
            "archive": {
                "relative": BASELINE_ARCHIVE_RELATIVE,
                "sha256": BASELINE_ARCHIVE_SHA256,
            },
            "receipt": {
                "relative": BASELINE_RECEIPT_RELATIVE,
                "sha256": BASELINE_RECEIPT_SHA256,
            },
            "records_sha256": BASELINE_RECORDS_SHA256,
        },
        "families": [
            {
                "family": "rust",
                "candidate_source_sha256": adapters["rust"],
                "state": "RUN",
                "report": rust_report,
                "receipt": rust_receipt,
                "superseded": [],
            },
            {
                "family": "c",
                "candidate_source_sha256": adapters["c"],
                "state": "RUN",
                "report": c_report,
                "receipt": c_receipt,
                "superseded": [{
                    "report": previous_report,
                    "receipt": previous_receipt,
                }],
            },
            {
                "family": "zig",
                "candidate_source_sha256": adapters["zig"],
                "state": "NOT MEASURED",
                "report": None,
                "receipt": None,
                "superseded": [],
            },
        ],
    }
    return manifest, evidence, synthetic_digest, records


class SyntheticPublication:
    """Exercise full fresh and replacement transactions with fake files."""

    def __init__(
        self,
        svg: bytes | None,
        summary: bytes | None,
        *,
        fail_replace: int | None = None,
        fail_link: int | None = None,
        fail_stage_write: bool = False,
    ) -> None:
        self.directory = 71
        self.next_descriptor = 80
        self.next_inode = 100_000
        self.files: dict[str, dict[str, Any]] = {}
        self.descriptors: dict[int, dict[str, Any]] = {}
        self.replace_count = 0
        self.publish_link_count = 0
        self.fail_replace = fail_replace
        self.fail_link = fail_link
        self.fail_stage_write = fail_stage_write
        self.failed_once = False
        self.sync_count = 0
        if svg is not None:
            self.install(safe_parts(SVG_RELATIVE)[-1], svg)
        if summary is not None:
            self.install(safe_parts(SUMMARY_RELATIVE)[-1], summary)

    def install(self, name: str, raw: bytes) -> None:
        self.next_inode += 1
        self.files[name] = {
            "raw": bytearray(raw),
            "device": 7,
            "inode": self.next_inode,
        }

    def info(self, value: Mapping[str, Any]) -> os.stat_result:
        return os.stat_result((
            stat.S_IFREG | 0o644,
            value["inode"],
            value["device"],
            1,
            0,
            0,
            len(value["raw"]),
            0,
            0,
            0,
        ))

    def open(
        self,
        name: str,
        flags: int,
        mode: int = 0o644,
        *,
        dir_fd: int | None = None,
    ) -> int:
        del mode
        require(
            dir_fd == self.directory and type(name) is str,
            "the fake chart transaction escaped its fake directory",
        )
        if flags & os.O_CREAT:
            require(
                flags & os.O_EXCL and name not in self.files,
                "a fake graph staging file was not exclusive",
            )
            self.install(name, b"")
        elif name not in self.files:
            raise FileNotFoundError(name)
        self.next_descriptor += 1
        descriptor = self.next_descriptor
        self.descriptors[descriptor] = {
            "entry": self.files[name],
            "offset": 0,
            "writable": bool(
                flags & (os.O_WRONLY | os.O_RDWR),
            ),
        }
        return descriptor

    def fstat(self, descriptor: int) -> os.stat_result:
        if descriptor == self.directory:
            return os.stat_result((
                stat.S_IFDIR | 0o755,
                7_001,
                7,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
            ))
        require(
            descriptor in self.descriptors,
            "a fake chart transaction used a real descriptor",
        )
        return self.info(
            self.descriptors[descriptor]["entry"],
        )

    def stat(
        self,
        name: str,
        *,
        dir_fd: int | None = None,
        follow_symlinks: bool = False,
    ) -> os.stat_result:
        require(
            dir_fd == self.directory
            and follow_symlinks is False,
            "a fake chart transaction accessed a real path",
        )
        if name not in self.files:
            raise FileNotFoundError(name)
        return self.info(self.files[name])

    def read(self, descriptor: int, count: int) -> bytes:
        require(
            descriptor in self.descriptors
            and type(count) is int
            and count > 0,
            "a fake chart transaction attempted a genuine read",
        )
        selected = self.descriptors[descriptor]
        start = selected["offset"]
        result = bytes(
            selected["entry"]["raw"][start:start + count],
        )
        selected["offset"] = start + len(result)
        return result

    def write(self, descriptor: int, value: bytes) -> int:
        require(
            descriptor in self.descriptors
            and self.descriptors[descriptor]["writable"]
            and type(value) is bytes,
            "a fake chart transaction attempted a genuine write",
        )
        if self.fail_stage_write and not self.failed_once:
            self.failed_once = True
            raise OSError("synthetic staged chart write failure")
        selected = self.descriptors[descriptor]
        selected["entry"]["raw"].extend(value)
        selected["offset"] += len(value)
        return len(value)

    def fsync(self, descriptor: int) -> None:
        require(
            descriptor == self.directory
            or descriptor in self.descriptors,
            "a fake chart transaction synchronized a real descriptor",
        )
        self.sync_count += 1

    def close(self, descriptor: int) -> None:
        require(
            descriptor in self.descriptors,
            "a fake chart transaction closed a real descriptor",
        )
        del self.descriptors[descriptor]

    def link(
        self,
        source: str,
        destination: str,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = False,
    ) -> None:
        require(
            src_dir_fd == dst_dir_fd == self.directory
            and follow_symlinks is False
            and source in self.files
            and destination not in self.files,
            "a fake chart link escaped the in-memory transaction",
        )
        if destination in {
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        }:
            self.publish_link_count += 1
            if (
                self.fail_link == self.publish_link_count
                and not self.failed_once
            ):
                self.failed_once = True
                raise OSError(
                    "synthetic atomic no-overwrite graph link failure",
                )
        self.files[destination] = self.files[source]

    def replace(
        self,
        source: str,
        destination: str,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        require(
            src_dir_fd == dst_dir_fd == self.directory
            and source in self.files
            and destination in self.files,
            "a fake graph replacement escaped its chart pair",
        )
        if source.startswith(
            ".rebar-shape-changing-buffer-overview-v1-stage-",
        ):
            self.replace_count += 1
            if (
                self.fail_replace == self.replace_count
                and not self.failed_once
            ):
                self.failed_once = True
                raise OSError(
                    "synthetic atomic paired graph replacement failure",
                )
        self.files[destination] = self.files.pop(source)

    def unlink(
        self,
        name: str,
        *,
        dir_fd: int | None = None,
    ) -> None:
        require(
            dir_fd == self.directory
            and name in self.files
            and (
                name.startswith(
                    ".rebar-shape-changing-buffer-overview-v1-",
                )
                or name in {
                    safe_parts(SVG_RELATIVE)[-1],
                    safe_parts(SUMMARY_RELATIVE)[-1],
                }
            ),
            "a fake transaction attempted to delete a real file",
        )
        del self.files[name]

    def pair(self) -> tuple[bytes | None, bytes | None]:
        result: list[bytes | None] = []
        for name in (
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        ):
            entry = self.files.get(name)
            result.append(
                None if entry is None else bytes(entry["raw"]),
            )
        return result[0], result[1]

    def only_outputs_remain(self) -> bool:
        output_names = {
            safe_parts(SVG_RELATIVE)[-1],
            safe_parts(SUMMARY_RELATIVE)[-1],
        }
        return (
            not (set(self.files) - output_names)
            and not self.descriptors
        )


def self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(
            type(name) is str
            and bool(name)
            and name not in accepted
            and name not in rejected
            and condition is True,
            "a genuine source-only control failed: " + name,
        )
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(
            type(name) is str
            and bool(name)
            and name not in accepted
            and name not in rejected,
            "a hostile source-only control was duplicated",
        )
        try:
            action()
        except (
            OverviewError,
            SourceOnlyError,
            OSError,
            TypeError,
            ValueError,
            KeyError,
            IndexError,
            OverflowError,
            UnicodeError,
            binascii.Error,
            zlib.error,
        ):
            rejected.append(name)
            return
        raise OverviewError(
            "hostile changing-buffer evidence was accepted: " + name,
        )

    with SourceOnlyBoundary() as boundary:
        matrix = build_matrix()
        accept(
            "reproduce-all-10240-independently-frozen-buffer-cases",
            len(matrix) == CASE_COUNT
            and digest(matrix) == MATRIX_SHA256,
        )
        accept(
            "preserve-the-exact-frozen-64-bit-seed",
            PUBLISHED_SEED == 6_001_118_316_486_346_290
            and all(case["seed"] == PUBLISHED_SEED for case in matrix),
        )
        accept(
            "preserve-all-64-equally-weighted-shape-cohorts",
            len(COHORTS) == 64
            and all(
                sum(case["cohort"] == cohort for case in matrix)
                == VARIANTS_PER_COHORT
                for cohort in COHORTS
            ),
        )
        accept(
            "preserve-all-800-actually-witnessed-short-buffer-cases",
            sum(
                case["outer_size"] == WITNESSED_OUTER_SIZE
                and case["nested_size"] in WITNESSED_NESTED_SIZES
                for case in matrix
            ) == WITNESSED_CASE_COUNT,
        )
        accept(
            "accept-the-exact-restored-original-report-byte-bound",
            validate_owned_limit(MAX_UNCOMPRESSED_BYTES)
            == MAX_UNCOMPRESSED_BYTES,
        )
        accept(
            "accept-the-exact-proved-compressed-archive-byte-bound",
            validate_owned_limit(MAX_ARCHIVE_BYTES) == MAX_ARCHIVE_BYTES,
        )
        reject(
            "reject-a-compressed-archive-above-its-proved-byte-bound",
            lambda: validate_owned_limit(MAX_ARCHIVE_BYTES + 1),
        )
        reject(
            "reject-a-zero-sized-project-input-byte-bound",
            lambda: validate_owned_limit(0),
        )
        reject(
            "reject-a-negative-project-input-byte-bound",
            lambda: validate_owned_limit(-1),
        )
        reject(
            "reject-a-boolean-project-input-byte-bound",
            lambda: validate_owned_limit(True),
        )
        accept(
            "accept-exact-compressed-and-restored-gzip-maximums",
            (
                lambda reader: (
                    reader.archive_bytes == MAX_ARCHIVE_BYTES
                    and reader.original_bytes == MAX_UNCOMPRESSED_BYTES
                )
            )(VerifiedGzipReader(
                -10_240_072,
                MAX_ARCHIVE_BYTES,
                BASELINE_ARCHIVE_SHA256,
                MAX_UNCOMPRESSED_BYTES,
                BASELINE_REPORT_SHA256,
            )),
        )
        reject(
            "reject-a-gzip-member-above-the-compressed-archive-maximum",
            lambda: VerifiedGzipReader(
                -10_240_072,
                MAX_ARCHIVE_BYTES + 1,
                BASELINE_ARCHIVE_SHA256,
                MAX_UNCOMPRESSED_BYTES,
                BASELINE_REPORT_SHA256,
            ),
        )
        reject(
            "reject-a-gzip-report-above-the-restored-original-maximum",
            lambda: VerifiedGzipReader(
                -10_240_072,
                MAX_ARCHIVE_BYTES,
                BASELINE_ARCHIVE_SHA256,
                MAX_UNCOMPRESSED_BYTES + 1,
                BASELINE_REPORT_SHA256,
            ),
        )
        raw = canonical({"proof": "lossless", "value": [1, 2, 3]})
        accept(
            "authenticate-an-entire-single-member-in-memory-gzip",
            synthetic_stream(raw)
            == {"proof": "lossless", "value": [1, 2, 3]},
        )
        compressor = zlib.compressobj(
            level=9,
            wbits=16 + zlib.MAX_WBITS,
        )
        archive = compressor.compress(raw) + compressor.flush()
        for name, options in (
            (
                "reject-a-truncated-lossless-gzip",
                {"archive": archive[:-1]},
            ),
            (
                "reject-gzip-trailing-bytes",
                {"archive": archive + b"hidden"},
            ),
            (
                "reject-an-extra-gzip-member",
                {"archive": archive + archive},
            ),
            (
                "reject-a-forged-compressed-gzip-hash",
                {"archive_hash": "01" * 32},
            ),
            (
                "reject-a-forged-uncompressed-gzip-hash",
                {"original_hash": "02" * 32},
            ),
            (
                "reject-a-forged-uncompressed-gzip-length",
                {"original_bytes": len(raw) + 1},
            ),
        ):
            reject(
                name,
                lambda options=options: synthetic_stream(
                    raw,
                    **options,
                ),
            )
        reject(
            "reject-duplicate-streamed-json-fields",
            lambda: synthetic_stream(
                b'{"proof":1,"proof":2,"value":[]}\n',
            ),
        )
        reject(
            "reject-an-omitted-streamed-json-field",
            lambda: synthetic_stream(b'{"proof":"missing"}\n'),
        )
        reject(
            "reject-an-extra-streamed-json-field",
            lambda: synthetic_stream(
                b'{"proof":1,"value":[],"hidden":2}\n',
            ),
        )
        (
            manifest,
            evidence,
            synthetic_digest,
            evidence_records,
        ) = synthetic_fixtures()

        def loader(
            relative: str,
            source: str,
            kind: str,
            original_hash: str | None,
            original_bytes: int | None,
            archive_bytes: int | None,
        ) -> dict[str, Any]:
            require(
                kind in {"receipt", "baseline", "candidate"},
                "a synthetic changing-buffer evidence type was forged",
            )
            if kind == "receipt":
                require(
                    original_hash is None
                    and original_bytes is None
                    and archive_bytes is None,
                    "a synthetic receipt claimed compressed report bytes",
                )
            else:
                require(
                    type(original_hash) is str
                    and type(original_bytes) is int
                    and type(archive_bytes) is int,
                    "a complete synthetic archive was not source-pinned",
                )
            selected = evidence.get((relative, source))
            require(
                type(selected) is dict,
                "a synthetic correctness receipt or report was substituted",
            )
            return selected

        baseline, rows = manifest_rows(
            manifest,
            loader,
            record_digest=synthetic_digest,
        )
        accept(
            "authenticate-both-independent-complete-python-workers",
            baseline["reference_pids"] == [82, 83],
        )
        accept(
            "show-python-rust-c-and-zig-in-consistent-order",
            [row["family"] for row in rows]
            == ["python", "rust", "c", "zig"],
        )
        accept(
            "preserve-all-four-identical-10240-case-denominators",
            all(
                row["case_denominator"] == CASE_COUNT
                and row["passed"]
                + row["failed"]
                + row["not_measured"]
                == CASE_COUNT
                for row in rows
            ),
        )
        accept(
            "show-only-a-genuinely-observed-full-candidate-pass",
            rows[1]["passed"] == CASE_COUNT
            and rows[1]["failed"] == 0
            and rows[1]["not_measured"] == 0,
        )
        accept(
            "never-confuse-successful-publication-with-correctness",
            rows[2]["passed"] == CASE_COUNT - 37
            and rows[2]["failed"] == 37,
        )
        accept(
            "preserve-every-superseded-failing-owned-source",
            len(rows[2]["superseded"]) == 1
            and rows[2]["superseded"][0]["failed"] == 53,
        )
        accept(
            "keep-a-truly-unobserved-zig-engine-not-measured",
            rows[3]["passed"] == 0
            and rows[3]["failed"] == 0
            and rows[3]["not_measured"] == CASE_COUNT,
        )
        source = hashlib.sha256(
            b"synthetic-shape-chart-source",
        ).hexdigest()
        manifest_hash = digest(manifest)
        svg, summary = build_documents(
            manifest,
            source,
            manifest_hash,
            loader,
            record_digest=synthetic_digest,
        )
        document = decode_document(
            summary,
            "the complete synthetic changing-buffer graph summary",
            MAX_SOURCE_BYTES,
        )
        accept(
            "render-an-accessible-plain-language-changing-buffer-chart",
            b"<svg" in svg
            and b"Python compatibility when buffers" in svg
            and b"10,240 / 10,240 match Python" in svg
            and b"10,203 / 10,240 match Python" in svg
            and b"NOT MEASURED" in svg
            and b"shape-buffer-title" in svg
            and b"shape-buffer-description" in svg,
        )
        accept(
            "keep-original-memory-and-scanner-denominators-independent",
            document[
                "independent_of_original_2807_case_denominator"
            ] is True
            and document[
                "independent_of_memory_1024_case_denominator"
            ] is True
            and document[
                "independent_of_scanner_2854_case_denominator"
            ] is True,
        )
        accept(
            "retain-all-current-and-historical-short-buffer-losses",
            document["families"][2]["failed"] == 37
            and document["families"][2]["superseded"][0]["failed"]
            == 53
            and document["performance"] == "NOT MEASURED"
            and document["final_holdout_opened"] is False,
        )
        accept(
            "regenerate-byte-identical-chart-and-canonical-summary",
            (svg, summary) == build_documents(
                manifest,
                source,
                manifest_hash,
                loader,
                record_digest=synthetic_digest,
            ),
        )

        def changed_manifest(name: str, value: Any) -> None:
            changed = dict(manifest)
            changed[name] = value
            manifest_rows(
                changed,
                loader,
                record_digest=synthetic_digest,
            )

        for name, value in (
            ("schema", "foreign"),
            ("python", "3.14.5"),
            ("case_denominator", CASE_COUNT - 1),
            ("cohort_count", 63),
            ("variants_per_cohort", VARIANTS_PER_COHORT - 1),
            ("shape_sizes", {**SHAPE_SIZES, "zero": 1}),
            ("witnessed_regression_outer_size", 12),
            (
                "witnessed_regression_nested_sizes",
                list(WITNESSED_NESTED_SIZES[:-1]),
            ),
            (
                "witnessed_regression_case_denominator",
                WITNESSED_CASE_COUNT - 1,
            ),
            ("oracle_source_sha256", "01" * 32),
            ("recorder_source_sha256", "02" * 32),
            ("ownership_audit_sha256", "03" * 32),
            ("original_v5_sha256", "04" * 32),
            ("pinned_python_sha256", "05" * 32),
            ("matrix_sha256", "06" * 32),
            ("published_seed", float(PUBLISHED_SEED)),
            ("published_seed", PUBLISHED_SEED - 1),
            ("families", manifest["families"][:-1]),
            ("families", list(reversed(manifest["families"]))),
        ):
            reject(
                "reject-forged-shape-manifest-"
                + name
                + "-"
                + str(len(rejected)),
                lambda name=name, value=value: changed_manifest(
                    name,
                    value,
                ),
            )
        selected_baseline = evidence[(
            BASELINE_RECEIPT_RELATIVE,
            BASELINE_RECEIPT_SHA256,
        )]
        for name, value in (
            ("status", "FAIL"),
            ("baseline_result_status", "FAIL"),
            ("recorder_source_sha256", "11" * 32),
            ("oracle_source_sha256", "12" * 32),
            ("original_v5_sha256", "13" * 32),
            ("ownership_audit_sha256", "14" * 32),
            ("pinned_python_sha256", "15" * 32),
            ("matrix_sha256", "16" * 32),
            ("published_seed", PUBLISHED_SEED - 1),
            ("case_count", CASE_COUNT - 1),
            ("cohort_count", 63),
            ("variants_per_cohort", 159),
            ("validated_reference_a_case_count", CASE_COUNT - 1),
            ("validated_reference_b_case_count", CASE_COUNT - 1),
            ("actual_reference_workers", 1),
            ("actual_candidate_workers", 1),
            ("source_closure_unchanged", False),
            ("baseline_records_sha256", "17" * 32),
            ("report_sha256", "18" * 32),
            ("report_bytes", BASELINE_ARCHIVE_BYTES - 1),
            ("report_uncompressed_sha256", "19" * 32),
            ("report_uncompressed_bytes", BASELINE_REPORT_BYTES - 1),
            ("report_compression", "none"),
            ("report_file_fsync_completed", False),
            ("report_directory_fsync_completed", False),
            ("report_atomic_no_overwrite_link", False),
            ("report_complete_readback_verified", False),
            ("hidden_cases_read", 1),
            ("benchmark_files_read", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("performance", "faster"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
        ):
            forged = dict(selected_baseline)
            forged[name] = value
            reject(
                "reject-forged-genuine-baseline-receipt-" + name,
                lambda forged=forged: validate_baseline_receipt(
                    forged,
                    BASELINE_ARCHIVE_RELATIVE,
                    BASELINE_ARCHIVE_SHA256,
                    BASELINE_RECEIPT_RELATIVE,
                ),
            )
        current = manifest["families"][1]
        current_receipt = evidence[(
            current["receipt"]["relative"],
            current["receipt"]["sha256"],
        )]
        current_report = evidence[(
            current["report"]["relative"],
            current["report"]["sha256"],
        )]
        for name, value in (
            ("status", "FAIL"),
            ("candidate_result_status", "PASS"),
            ("candidate_family", "rust"),
            ("candidate_source_sha256", "21" * 32),
            ("native_engine_sha256", "22" * 32),
            ("native_bridge_sha256", "23" * 32),
            ("recorder_source_sha256", "24" * 32),
            ("oracle_source_sha256", "25" * 32),
            ("original_v5_sha256", "26" * 32),
            ("ownership_audit_sha256", "27" * 32),
            ("pinned_python_sha256", "28" * 32),
            ("matrix_sha256", "29" * 32),
            ("published_seed", PUBLISHED_SEED - 1),
            ("case_count", CASE_COUNT - 1),
            ("cohort_count", 63),
            ("variants_per_cohort", 159),
            (
                "witnessed_regression_case_count",
                WITNESSED_CASE_COUNT - 1,
            ),
            ("baseline_receipt_sha256", "31" * 32),
            ("baseline_archive_sha256", "32" * 32),
            ("baseline_records_sha256", "33" * 32),
            ("validated_baseline_record_count", CASE_COUNT - 1),
            ("validated_candidate_record_count", CASE_COUNT - 1),
            ("mismatch_count", 36),
            ("all_mismatches_preserved", False),
            ("actual_method_guard_checks", 2 * CASE_COUNT - 1),
            (
                "actual_warning_registry_guard_checks",
                2 * CASE_COUNT - 1,
            ),
            ("actual_reference_workers", 1),
            ("actual_candidate_workers", 0),
            ("actual_candidate_imports", 0),
            ("actual_candidate_process_invocations", 0),
            ("candidate_owner_unchanged", False),
            ("report_sha256", "35" * 32),
            ("report_compression", "none"),
            ("report_file_fsync_completed", False),
            ("report_directory_fsync_completed", False),
            ("report_atomic_no_overwrite_link", False),
            ("report_complete_readback_verified", False),
            ("hidden_cases_read", 1),
            ("benchmark_files_read", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("performance", "faster"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
        ):
            forged = dict(current_receipt)
            forged[name] = value
            reject(
                "reject-forged-genuine-candidate-receipt-" + name,
                lambda forged=forged: validate_candidate_receipt(
                    forged,
                    "c",
                    current["candidate_source_sha256"],
                    baseline,
                    current["report"]["relative"],
                    current["report"]["sha256"],
                    current["receipt"]["relative"],
                ),
            )
        for name, value in (
            ("status", "PASS"),
            ("candidate_source_sha256", "41" * 32),
            ("case_count", CASE_COUNT - 1),
            ("cohort_count", 63),
            ("validated_candidate_record_count", CASE_COUNT - 1),
            ("candidate_records_sha256", "42" * 32),
            ("mismatch_count", 36),
            ("all_mismatches", current_report["all_mismatches"][:-1]),
            ("actual_method_guard_checks", 2 * CASE_COUNT - 1),
            (
                "actual_warning_registry_guard_checks",
                2 * CASE_COUNT - 1,
            ),
            ("actual_candidate_workers", 0),
            ("actual_candidate_process_returncode", 1),
            ("all_failure_reasons", []),
            ("failure_count", 0),
            ("hidden_cases_read", 1),
            ("benchmark_files_read", 1),
            ("clock_samples", 1),
            ("performance", "faster"),
        ):
            forged = dict(current_report)
            forged[name] = value
            reject(
                "reject-forged-complete-candidate-report-" + name,
                lambda forged=forged: validate_candidate(
                    forged,
                    current_receipt,
                    baseline,
                    matrix,
                    evidence_records,
                    synthetic_digest,
                ),
            )

        for path in (
            "", "/tmp/escape", "../escape", "a/../b", "a//b",
            "a\\b", "a/\x00/b",
        ):
            reject(
                "reject-unsafe-graph-path-" + repr(path),
                lambda path=path: safe_parts(path),
            )
        reject(
            "reject-duplicate-canonical-json-fields",
            lambda: decode_document(
                b'{"proof":1,"proof":2}\n',
                "synthetic duplicate",
            ),
        )
        reject(
            "reject-noncanonical-json-evidence",
            lambda: decode_document(
                b'{"proof": 1}\n',
                "synthetic noncanonical",
            ),
        )
        reject(
            "reject-nonfinite-json-evidence",
            lambda: decode_document(
                b'{"proof":NaN}\n',
                "synthetic nonfinite",
            ),
        )
        reject(
            "reject-a-truncated-isolated-worker-stream",
            lambda: decode_stream(
                {
                    **capture_stream(b"synthetic"),
                    "bytes": 8,
                },
                "synthetic worker",
            ),
        )
        reject(
            "reject-a-forged-isolated-worker-digest",
            lambda: decode_stream(
                {
                    **capture_stream(b"synthetic"),
                    "sha256": "51" * 32,
                },
                "synthetic worker",
            ),
        )
        reject(
            "reject-aliased-original-python-worker-pids",
            lambda: validate_baseline_receipt(
                {
                    **selected_baseline,
                    "baseline_reference_pids": [82, 82],
                },
                BASELINE_ARCHIVE_RELATIVE,
                BASELINE_ARCHIVE_SHA256,
                BASELINE_RECEIPT_RELATIVE,
            ),
        )
        reject(
            "reject-a-hidden-short-buffer-regression-count",
            lambda: validate_mismatch_counts(
                {
                    **current_receipt,
                    "witnessed_regression_mismatches_by_nested_size": {
                        **current_receipt[
                            "witnessed_regression_mismatches_by_nested_size"
                        ],
                        "0": VARIANTS_PER_COHORT + 1,
                    },
                },
                37,
            ),
        )
        reject(
            "reject-a-hidden-buffer-cohort-failure",
            lambda: validate_mismatch_counts(
                {
                    **current_receipt,
                    "mismatches_by_cohort": {
                        **current_receipt["mismatches_by_cohort"],
                        COHORTS[0]: current_receipt[
                            "mismatches_by_cohort"
                        ][COHORTS[0]] + 1,
                    },
                },
                37,
            ),
        )

        old_svg = b"<svg>earlier frozen changing-buffer graph</svg>\n"
        old_document = dict(document)
        old_document["svg_sha256"] = hashlib.sha256(
            old_svg,
        ).hexdigest()
        old_summary = canonical(old_document)
        old_svg_hash = hashlib.sha256(old_svg).hexdigest()
        old_summary_hash = hashlib.sha256(old_summary).hexdigest()
        accept(
            "authenticate-both-complete-previous-frozen-chart-files",
            validate_previous_outputs(
                old_svg,
                old_summary,
                old_svg_hash,
                old_summary_hash,
                source,
            )["families"][2]["superseded"][0]["failed"] == 53,
        )
        accept(
            "allow-exactly-idempotent-no-overwrite-publication",
            approve_publication(
                svg,
                summary,
                svg,
                summary,
                False,
                None,
                None,
                source,
            ) is False,
        )
        accept(
            "require-both-explicit-old-hashes-for-paired-refresh",
            approve_publication(
                old_svg,
                old_summary,
                svg,
                summary,
                True,
                old_svg_hash,
                old_summary_hash,
                source,
            ) is True,
        )
        for name, values in (
            (
                "reject-an-unapproved-changing-buffer-refresh",
                (
                    old_svg,
                    old_summary,
                    False,
                    None,
                    None,
                ),
            ),
            (
                "reject-a-missing-previous-svg",
                (
                    None,
                    old_summary,
                    True,
                    old_svg_hash,
                    old_summary_hash,
                ),
            ),
            (
                "reject-a-missing-previous-summary",
                (
                    old_svg,
                    None,
                    True,
                    old_svg_hash,
                    old_summary_hash,
                ),
            ),
            (
                "reject-a-forged-previous-svg",
                (
                    old_svg,
                    old_summary,
                    True,
                    "61" * 32,
                    old_summary_hash,
                ),
            ),
            (
                "reject-a-forged-previous-summary",
                (
                    old_svg,
                    old_summary,
                    True,
                    old_svg_hash,
                    "62" * 32,
                ),
            ),
            (
                "reject-replacement-pins-without-explicit-consent",
                (
                    svg,
                    summary,
                    False,
                    hashlib.sha256(svg).hexdigest(),
                    hashlib.sha256(summary).hexdigest(),
                ),
            ),
            (
                "reject-a-partial-fresh-svg-only-publication",
                (
                    svg,
                    None,
                    False,
                    None,
                    None,
                ),
            ),
            (
                "reject-a-partial-fresh-summary-only-publication",
                (
                    None,
                    summary,
                    False,
                    None,
                    None,
                ),
            ),
        ):
            reject(
                name,
                lambda values=values: approve_publication(
                    values[0],
                    values[1],
                    svg,
                    summary,
                    values[2],
                    values[3],
                    values[4],
                    source,
                ),
            )
        fresh = SyntheticPublication(None, None)
        atomic_publish_pair(
            fresh.directory,
            (7, 7_001),
            None,
            None,
            svg,
            summary,
            fresh,
        )
        accept(
            "atomically-publish-both-fresh-outputs-without-real-files",
            fresh.pair() == (svg, summary)
            and fresh.only_outputs_remain()
            and fresh.sync_count >= 3,
        )
        for count in (1, 2):
            failed = SyntheticPublication(
                None,
                None,
                fail_link=count,
            )
            reject(
                "roll-back-both-fresh-outputs-after-link-"
                + str(count),
                lambda failed=failed: atomic_publish_pair(
                    failed.directory,
                    (7, 7_001),
                    None,
                    None,
                    svg,
                    summary,
                    failed,
                ),
            )
            accept(
                "restore-a-truly-empty-pair-after-link-"
                + str(count),
                failed.pair() == (None, None)
                and failed.only_outputs_remain(),
            )
        refreshed = SyntheticPublication(old_svg, old_summary)
        atomic_publish_pair(
            refreshed.directory,
            (7, 7_001),
            old_svg,
            old_summary,
            svg,
            summary,
            refreshed,
        )
        accept(
            "atomically-replace-both-frozen-graphs-without-real-files",
            refreshed.pair() == (svg, summary)
            and refreshed.only_outputs_remain()
            and refreshed.sync_count >= 3,
        )
        for count in (1, 2):
            failed = SyntheticPublication(
                old_svg,
                old_summary,
                fail_replace=count,
            )
            reject(
                "roll-back-both-prior-graphs-after-replace-"
                + str(count),
                lambda failed=failed: atomic_publish_pair(
                    failed.directory,
                    (7, 7_001),
                    old_svg,
                    old_summary,
                    svg,
                    summary,
                    failed,
                ),
            )
            accept(
                "restore-the-exact-prior-pair-after-replace-"
                + str(count),
                failed.pair() == (old_svg, old_summary)
                and failed.only_outputs_remain(),
            )
        failed_stage = SyntheticPublication(
            old_svg,
            old_summary,
            fail_stage_write=True,
        )
        reject(
            "roll-back-the-pair-after-a-staged-write-failure",
            lambda: atomic_publish_pair(
                failed_stage.directory,
                (7, 7_001),
                old_svg,
                old_summary,
                svg,
                summary,
                failed_stage,
            ),
        )
        accept(
            "retain-the-complete-prior-pair-after-staging-failure",
            failed_stage.pair() == (old_svg, old_summary)
            and failed_stage.only_outputs_remain(),
        )
        for name, action in (
            (
                "block-all-genuine-evidence-file-reads",
                lambda: builtins.open(
                    BASELINE_ARCHIVE_RELATIVE,
                    "rb",
                ),
            ),
            (
                "block-all-genuine-derived-graph-writes",
                lambda: builtins.open(SVG_RELATIVE, "wb"),
            ),
            (
                "block-no-follow-real-evidence-access",
                lambda: os.open(
                    BASELINE_RECEIPT_RELATIVE,
                    os.O_RDONLY,
                ),
            ),
            (
                "block-any-performance-or-hidden-directory",
                lambda: os.stat("performance"),
            ),
            (
                "block-any-candidate-or-external-engine-import",
                lambda: importlib.import_module(
                    "candidates.zig_candidate",
                ),
            ),
            (
                "block-candidate-and-reference-worker-processes",
                lambda: subprocess.run([PINNED_PYTHON]),
            ),
            (
                "block-all-background-worker-threads",
                lambda: threading.Thread(
                    target=lambda: None,
                ).start(),
            ),
            (
                "block-all-performance-clock-measurement",
                lambda: time.perf_counter(),
            ),
            (
                "block-silent-generated-graph-replacement",
                lambda: os.replace("synthetic-a", "synthetic-b"),
            ),
            (
                "block-genuine-no-overwrite-graph-publication",
                lambda: os.link("synthetic-a", "synthetic-b"),
            ),
            (
                "block-genuine-chart-directory-synchronization",
                lambda: os.fsync(-1),
            ),
            (
                "block-all-garbage-collection-side-effects",
                lambda: gc.collect(),
            ),
            (
                "block-external-random-seed-generation",
                lambda: os.urandom(8),
            ),
        ):
            reject(name, action)
        accept(
            "exercise-every-source-only-external-effect-boundary",
            all(count > 0 for count in boundary.blocked.values()),
        )
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "oracle_source_sha256": ORACLE_SHA256,
        "recorder_source_sha256": RECORDER_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "original_v5_sha256": V5_SHA256,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_denominator": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "witnessed_regression_case_denominator": (
            WITNESSED_CASE_COUNT
        ),
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "workspace_files_read": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render only the independently frozen 10,240-case "
            "Python changing-size buffer comparison"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--self-test",
        action="store_true",
        help="run only isolated, fully in-memory hostile source controls",
    )
    modes.add_argument(
        "--render",
        action="store_true",
        help="render only the exact independently frozen inputs manifest",
    )
    parser.add_argument("--source-sha256")
    parser.add_argument("--manifest")
    parser.add_argument("--manifest-sha256")
    parser.add_argument(
        "--replace-generated",
        action="store_true",
    )
    parser.add_argument("--previous-svg-sha256")
    parser.add_argument("--previous-summary-sha256")
    options = parser.parse_args(arguments)
    try:
        if options.self_test:
            require(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256",
                        "manifest",
                        "manifest_sha256",
                        "previous_svg_sha256",
                        "previous_summary_sha256",
                    )
                )
                and options.replace_generated is False,
                "source-only controls cannot authorize files or publication",
            )
            result = self_test()
        else:
            require(
                options.render is True,
                "explicitly select the frozen changing-buffer graph",
            )
            result = render(
                options.source_sha256,
                options.manifest,
                options.manifest_sha256,
                replace=options.replace_generated,
                previous_svg=options.previous_svg_sha256,
                previous_summary=options.previous_summary_sha256,
            )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (
        OverviewError,
        OSError,
        TypeError,
        ValueError,
        KeyError,
        IndexError,
        OverflowError,
        UnicodeError,
        RecursionError,
        binascii.Error,
        zlib.error,
    ) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error": str(error),
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_opened": False,
            "winner_selected": False,
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
