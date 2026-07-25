#!/usr/bin/env python3
"""Fresh public-practice-only comparisons for the from-scratch Rust candidate.

The source creates its own public cases. It never discovers, opens, enumerates,
or borrows a benchmark, performance fixture, secret, or hidden test. Importing
the source does not start a subprocess, import a candidate, or write a file.
Only the explicit ``--correctness-only`` or ``--run`` commands may start a
Rust-candidate worker. Correctness-only never samples a clock or writes a file.
A file is written only when ``--run`` also receives explicitly approved output.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
from importlib.machinery import EXTENSION_SUFFIXES, ExtensionFileLoader
import json
import math
import os
from pathlib import Path, PurePosixPath
import random
import stat
import statistics
import subprocess
import sys
import time
import types
from typing import Any, Callable, Mapping
import warnings


ROOT = Path("/home/dev-user/src/rebar")
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SOURCE_RELATIVE = "tools/rust_public_practice_benchmark_v1.py"
OUTPUT_PREFIX = "experiments/rust_public_practice_v1"
SCHEMA = "rebar-rust-fresh-public-practice-v1"
PRACTICE_LABEL = "PUBLIC PRACTICE ONLY; NOT A HIDDEN OR FINAL BENCHMARK"
PUBLISHED_SEED = 0x5245_4241_525F_5031
MATRIX_SHA256 = (
    "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e"
)
PINNED_STDLIB_RE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
)
DEFAULT_PAIRED_TRIALS = 12
DEFAULT_BATCH_ITERATIONS = 12
DEFAULT_WARMUP_ITERATIONS = 2
BOOTSTRAP_RESAMPLES = 1_000
MAX_PROCESS_BYTES = 16 * 1024 * 1024
MAX_OUTPUT_BYTES = 32 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 180

# Public, stable CPython regular-expression flag values. Keeping them here
# means preparing public practice cases never imports either matching engine.
IGNORECASE = 2
MULTILINE = 8
DOTALL = 16
VERBOSE = 64
ASCII = 256

OPERATIONS = (
    "module.compile",
    "module.search",
    "module.match",
    "module.fullmatch",
    "module.findall",
    "module.finditer",
    "module.split",
    "module.split.positional",
    "module.sub.literal",
    "module.sub.positional",
    "module.sub.positional_callback_error",
    "module.subn.literal",
    "module.subn.positional",
    "module.subn.positional_callback_error",
    "module.sub.callback",
    "module.subn.callback",
    "module.sub.callback_error",
    "pattern.search",
    "pattern.match",
    "pattern.fullmatch",
    "pattern.findall",
    "pattern.finditer",
    "pattern.split",
    "pattern.sub.literal",
    "pattern.subn.literal",
    "pattern.sub.callback",
    "pattern.subn.callback",
    "pattern.sub.callback_error",
    "pattern.scanner.search",
    "pattern.scanner.match",
    "pattern.scanner.loop",
    "scanner.scan",
    "scanner.scan.callback_error",
    "match.group",
    "match.expand",
    "compile.fresh.search",
)


class PracticeBenchmarkError(Exception):
    """Reject a substituted practice case, observable, process, or output."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PracticeBenchmarkError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    actual: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in actual,
                "duplicate process-document keys are forbidden")
        actual[key] = value
    return actual


def decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete bounded canonical process output is required: " + label)
    try:
        actual = json.loads(
            raw, object_pairs_hook=_unique_json_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                PracticeBenchmarkError("nonfinite process evidence is forbidden"),
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise PracticeBenchmarkError(
            "invalid complete public-practice process evidence: " + label,
        ) from error
    require(type(actual) is dict and canonical(actual) == raw,
            "noncanonical or truncated process evidence: " + label)
    return actual


def typed_text(value: str) -> dict[str, str]:
    require(type(value) is str, "an actual public text value is required")
    return {"type": "str", "value": value}


def typed_bytes(value: bytes) -> dict[str, str]:
    require(type(value) is bytes, "an actual public bytes value is required")
    return {"type": "bytes", "hex": value.hex()}


def typed_bytearray(value: bytearray) -> dict[str, str]:
    require(type(value) is bytearray,
            "an actual mutable public bytearray is required")
    return {"type": "bytearray", "hex": bytes(value).hex()}


def typed_memoryview(value: memoryview) -> dict[str, Any]:
    require(type(value) is memoryview and value.format == "B"
            and value.ndim == 1 and value.contiguous,
            "an authentic one-dimensional public byte memoryview is required")
    return {
        "type": "memoryview", "hex": value.tobytes().hex(),
        "readonly": value.readonly, "format": value.format,
        "shape": list(value.shape) if value.shape is not None else None,
    }


def encode_public_subject(value: Any) -> dict[str, Any]:
    if type(value) is str:
        return typed_text(value)
    if type(value) is bytes:
        return typed_bytes(value)
    if type(value) is bytearray:
        return typed_bytearray(value)
    if type(value) is memoryview:
        return typed_memoryview(value)
    raise PracticeBenchmarkError("an original public subject type was substituted")


def materialize_typed(value: Any) -> str | bytes | bytearray | memoryview:
    require(type(value) is dict, "an exact typed public practice input is mandatory")
    if set(value) == {"type", "value"} and value.get("type") == "str":
        require(type(value["value"]) is str,
                "the original public text input was substituted")
        return value["value"]
    if set(value) == {"type", "hex"} \
            and value.get("type") in ("bytes", "bytearray"):
        require(type(value["hex"]) is str,
                "the original public byte input was substituted")
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise PracticeBenchmarkError(
                "invalid original public practice byte encoding",
            ) from error
        require(actual.hex() == value["hex"],
                "noncanonical original public practice byte encoding")
        return actual if value["type"] == "bytes" else bytearray(actual)
    if set(value) == {"type", "hex", "readonly", "format", "shape"} \
            and value.get("type") == "memoryview":
        require(type(value.get("hex")) is str
                and type(value.get("readonly")) is bool
                and value.get("format") == "B"
                and type(value.get("shape")) is list
                and len(value["shape"]) == 1,
                "the original public memoryview shape or readonly flag changed")
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise PracticeBenchmarkError(
                "invalid original public memoryview byte encoding",
            ) from error
        require(actual.hex() == value["hex"]
                and value["shape"] == [len(actual)],
                "the original public memoryview bytes or exact shape changed")
        return memoryview(actual if value["readonly"] else bytearray(actual))
    raise PracticeBenchmarkError("an original typed public case was substituted")


def build_public_matrix() -> list[dict[str, Any]]:
    """Create all cases entirely from the original public literals below."""
    text_data: tuple[tuple[str, str, str, int], ...] = (
        (
            "text.ascii.ignorecase",
            r"(?P<word>[a-z]+)(?P<number>\d*)",
            "alpha42 BETA7 gamma alpha42", IGNORECASE,
        ),
        (
            "text.unicode.words",
            r"(?P<word>\w+)(?P<number>\d*)",
            "café Δelta_9 naïve ASCII_2", 0,
        ),
        (
            "text.multiline.anchors",
            r"^(?P<word>[a-z]+)(?P<number>\d*)$",
            "alpha1\nBETA\ngamma22\nalpha1", MULTILINE | IGNORECASE,
        ),
        (
            "text.lookbehind",
            r"(?<=ID:)(?P<word>[A-Z]+)(?P<number>\d+)",
            "ID:AB12 other ID:XY90 ID:CD34", 0,
        ),
        (
            "text.alternation",
            r"(?P<word>ab|a)(?P<number>\d*)",
            "ab12 a7 aba99 nothing", 0,
        ),
        (
            "text.verbose",
            r"(?P<word> [a-z]+ ) \s* (?P<number> \d* )",
            "alpha 12 BETA7 gamma 003", VERBOSE | IGNORECASE,
        ),
        (
            "text.dotall",
            r"(?P<word>a.+?z)(?P<number>\d*)",
            "a first\nsecond z12 and a third z9", DOTALL,
        ),
        (
            "text.boundary.long",
            r"\b(?P<word>[A-Za-z_]+)(?P<number>\d*)\b",
            "prefix_42 middle7 suffix_003 " * 24, ASCII,
        ),
        (
            "text.no_match",
            r"(?P<word>QZX_NEVER_PRESENT)(?P<number>\d+)",
            "alpha12 ordinary words gamma003", 0,
        ),
        (
            "text.full_string",
            r"(?P<word>[A-Za-z]+)-(?P<number>\d+)",
            "alpha-123", ASCII,
        ),
        (
            "text.ascii_unicode_boundary",
            r"\b(?P<word>\w+)(?P<number>\d*)\b",
            "café delta_9 naïve ASCII_2", ASCII,
        ),
        (
            "text.scanner_remainder",
            r"(?P<word>[A-Za-z]+)(?P<number>\d*)",
            "alpha12 beta7 !unconsumed tail9", 0,
        ),
    )
    byte_data: tuple[tuple[str, bytes, Any, int], ...] = (
        (
            "bytes.ascii.ignorecase",
            rb"(?P<word>[a-z]+)(?P<number>\d*)",
            b"alpha42 BETA7 gamma alpha42", IGNORECASE,
        ),
        (
            "bytes.high.bit",
            rb"(?P<word>\w+)(?P<number>\d*)",
            b"caf\xe9 delta_9 ASCII_2 \xff tail7", 0,
        ),
        (
            "bytes.multiline.anchors",
            rb"^(?P<word>[a-z]+)(?P<number>\d*)$",
            b"alpha1\nBETA\ngamma22\nalpha1", MULTILINE | IGNORECASE,
        ),
        (
            "bytes.lookbehind",
            rb"(?<=ID:)(?P<word>[A-Z]+)(?P<number>\d+)",
            b"ID:AB12 other ID:XY90 ID:CD34", 0,
        ),
        (
            "bytes.alternation",
            rb"(?P<word>ab|a)(?P<number>\d*)",
            b"ab12 a7 aba99 nothing", 0,
        ),
        (
            "bytes.verbose",
            rb"(?P<word> [a-z]+ ) \s* (?P<number> \d* )",
            b"alpha 12 BETA7 gamma 003", VERBOSE | IGNORECASE,
        ),
        (
            "bytes.dotall",
            rb"(?P<word>a.+?z)(?P<number>\d*)",
            b"a first\nsecond z12 and a third z9", DOTALL,
        ),
        (
            "bytes.boundary.long",
            rb"\b(?P<word>[A-Za-z_]+)(?P<number>\d*)\b",
            b"prefix_42 middle7 suffix_003 " * 24, ASCII,
        ),
        (
            "bytes.bytearray.scanner_remainder",
            rb"(?P<word>[A-Za-z]+)(?P<number>\d*)",
            bytearray(b"alpha12 beta7 !unconsumed tail9"), 0,
        ),
        (
            "bytes.memoryview.mutable.scanner_remainder",
            rb"(?P<word>[A-Za-z]+)(?P<number>\d*)",
            memoryview(bytearray(b"alpha12 beta7 !unconsumed tail9")), 0,
        ),
        (
            "bytes.memoryview.readonly.scanner_remainder",
            rb"(?P<word>[A-Za-z]+)(?P<number>\d*)",
            memoryview(b"alpha12 beta7 !unconsumed tail9"), 0,
        ),
        (
            "bytes.no_match",
            rb"(?P<word>QZX_NEVER_PRESENT)(?P<number>\d+)",
            b"alpha12 ordinary words gamma003", 0,
        ),
    )
    seeded = random.Random(PUBLISHED_SEED)
    datasets: list[tuple[str, str, dict[str, str], dict[str, str], int]] = []
    for name, expression, subject, flags in text_data:
        datasets.append((name, "text", typed_text(expression),
                         encode_public_subject(subject), flags))
    for name, expression, subject, flags in byte_data:
        datasets.append((name, "bytes", typed_bytes(expression),
                         encode_public_subject(subject), flags))

    cases: list[dict[str, Any]] = []
    for name, domain, expression, subject, flags in datasets:
        replacement = (
            typed_text(r"<\g<word>>") if domain == "text"
            else typed_bytes(rb"<\g<word>>")
        )
        for operation in OPERATIONS:
            if operation == "compile.fresh.search":
                lifecycle = "fresh-compile-and-match"
            elif operation == "module.compile":
                lifecycle = "module-compile"
            elif operation.startswith("module."):
                lifecycle = "module-call"
            elif operation.startswith("match."):
                lifecycle = "live-match"
            elif operation.startswith("pattern.scanner.") \
                    or operation.startswith("scanner.scan"):
                lifecycle = "live-scanner"
            else:
                lifecycle = "precompiled-pattern"
            cases.append({
                "case": "rust-public-practice.v1." + format(len(cases), "04d"),
                "dataset": name, "domain": domain, "operation": operation,
                "lifecycle": lifecycle, "pattern": expression,
                "subject": subject, "replacement": replacement,
                "flags": flags, "limit": seeded.randrange(1, 4),
                "weight_numerator": 1,
            })
    return cases


def validate_public_matrix(cases: Any) -> str:
    require(type(cases) is list and len(cases) == 24 * len(OPERATIONS)
            and cases == build_public_matrix()
            and len({item["case"] for item in cases}) == len(cases)
            and digest(cases) == MATRIX_SHA256,
            "the exact original public-practice seed, cases, or denominator changed")
    require(sum(item["domain"] == "text" for item in cases)
            == sum(item["domain"] == "bytes" for item in cases)
            == 12 * len(OPERATIONS),
            "public text and bytes must retain exactly equal case weights")
    for operation in OPERATIONS:
        require(sum(item["operation"] == operation for item in cases) == 24,
                "an entire original public API operation was hidden: " + operation)
    return MATRIX_SHA256


def verify_pinned_runtime(*, permit_candidate: bool = False) -> None:
    expected_source = str(ROOT / SOURCE_RELATIVE)
    expected_root = str(ROOT)
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == expected_root
            and os.path.realpath(expected_root) == expected_root
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON)
            and os.path.abspath(__file__) == expected_source
            and os.path.realpath(__file__) == expected_source,
            "use only the exact frozen no-symlink source, root, and CPython 3.14.6")
    if not permit_candidate:
        require(not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ), "a candidate escaped into a standard-library-only public self-test")


def authenticate_owned_module(module: Any, *, label: str) -> str:
    origin = getattr(module, "__file__", None)
    require(type(origin) is str and os.path.isabs(origin)
            and os.path.abspath(origin) == origin
            and os.path.realpath(origin) == origin
            and os.path.commonpath((str(ROOT), origin)) == str(ROOT),
            "the exact original owned " + label + " origin was substituted")
    return origin


def authenticate_rust_candidate(candidate: Any) -> None:
    expected = str(ROOT / "candidates" / "rust_candidate.py")
    origin = authenticate_owned_module(candidate, label="Rust adapter")
    require(candidate.__name__ == "candidates.rust_candidate"
            and origin == expected,
            "the exact owned from-scratch Rust candidate adapter was substituted")

    bridge = sys.modules.get("candidates._rust_bridge")
    require(isinstance(bridge, types.ModuleType)
            and bridge.__name__ == "candidates._rust_bridge",
            "the exact owned native Rust bridge was omitted or substituted")
    bridge_origin = authenticate_owned_module(
        bridge, label="compiled candidates._rust_bridge",
    )
    candidate_root = str(ROOT / "candidates")
    require(os.path.commonpath((candidate_root, bridge_origin)) == candidate_root
            and any(bridge_origin.endswith(suffix)
                    for suffix in EXTENSION_SUFFIXES),
            "the native Rust bridge is not an owned real CPython extension")
    bridge_spec = getattr(bridge, "__spec__", None)
    bridge_loader = getattr(bridge_spec, "loader", None)
    require(bridge_spec is not None
            and getattr(bridge_spec, "name", None) == "candidates._rust_bridge"
            and getattr(bridge_spec, "origin", None) == bridge_origin
            and isinstance(bridge_loader, ExtensionFileLoader)
            and getattr(bridge_loader, "name", None) == "candidates._rust_bridge"
            and getattr(bridge_loader, "path", None) == bridge_origin,
            "the exact owned native extension identity or loader was forged")

    candidate_package = sys.modules.get("candidates")
    if candidate_package is not None \
            and getattr(candidate_package, "__file__", None) is not None:
        package_origin = authenticate_owned_module(
            candidate_package, label="Rust candidate package",
        )
        require(package_origin == str(ROOT / "candidates" / "__init__.py"),
                "the exact owned candidate-package origin was substituted")

    for name in (
        "compile", "search", "match", "fullmatch", "findall", "finditer",
        "split", "sub", "subn", "Scanner",
    ):
        public = getattr(candidate, name, None)
        if public is None:
            continue
        public_module_name = getattr(public, "__module__", None)
        require(public_module_name not in ("re", "_sre", "sre_compile"),
                "a Rust public operation directly delegates to CPython: " + name)
        if type(public_module_name) is str and public_module_name != "builtins":
            public_module = sys.modules.get(public_module_name)
            if public_module is not None and (
                public_module_name.startswith("candidates.")
                or "rust" in public_module_name.lower()
                or "rebar" in public_module_name.lower()
            ):
                authenticate_owned_module(
                    public_module, label="Rust public-operation bridge " + name,
                )

    for value in vars(candidate).values():
        if isinstance(value, types.ModuleType):
            name = value.__name__
            if (name.startswith("candidates.")
                    or "rust" in name.lower() or "rebar" in name.lower()):
                authenticate_owned_module(value, label="Rust native bridge " + name)
        elif type(value).__module__.startswith("ctypes"):
            library = getattr(value, "_name", None)
            if type(library) is str and os.path.isabs(library):
                require(os.path.abspath(library) == library
                        and os.path.realpath(library) == library
                        and os.path.commonpath((str(ROOT), library)) == str(ROOT),
                        "the loaded from-scratch Rust FFI bridge is not owned")


def normalize_pattern(pattern: Any) -> dict[str, Any]:
    groups = getattr(pattern, "groups")
    flags = getattr(pattern, "flags")
    mapping = getattr(pattern, "groupindex")
    require(type(groups) is int and type(flags) is int,
            "a regex pattern concealed its exact public group count or flags")
    return {
        "kind": "compiled-pattern",
        "pattern": normalize_value(getattr(pattern, "pattern")),
        "flags": flags, "groups": groups,
        "groupindex": [
            [name, index] for name, index in sorted(dict(mapping).items())
        ],
    }


def normalize_match(match: Any) -> dict[str, Any]:
    expression = getattr(match, "re")
    group_count = getattr(expression, "groups")
    require(type(group_count) is int and group_count >= 0,
            "a live match concealed its exact public capture-group count")
    return {
        "kind": "match", "pattern": normalize_pattern(expression),
        "string": normalize_value(getattr(match, "string")),
        "group": normalize_value(match.group(0)),
        "span": list(match.span(0)),
        "groups": [normalize_value(value) for value in match.groups()],
        "spans": [list(match.span(index)) for index in range(group_count + 1)],
        "groupdict": [
            [name, normalize_value(value)]
            for name, value in sorted(match.groupdict().items())
        ],
        "lastindex": match.lastindex, "lastgroup": match.lastgroup,
        "pos": match.pos, "endpos": match.endpos,
    }


def normalize_value(value: Any) -> Any:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        return {
            "kind": "memoryview", "hex": value.tobytes().hex(),
            "readonly": value.readonly, "format": value.format,
            "itemsize": value.itemsize, "ndim": value.ndim,
            "shape": list(value.shape) if value.shape is not None else None,
            "strides": list(value.strides) if value.strides is not None else None,
            "contiguous": value.contiguous,
        }
    if type(value) in (list, tuple):
        return {
            "kind": "list" if type(value) is list else "tuple",
            "items": [normalize_value(item) for item in value],
        }
    if isinstance(value, Mapping):
        return {
            "kind": "mapping",
            "items": [
                [normalize_value(key), normalize_value(item)]
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            ],
        }
    if hasattr(value, "group") and hasattr(value, "span") \
            and hasattr(value, "re"):
        return normalize_match(value)
    if hasattr(value, "pattern") and hasattr(value, "groupindex") \
            and hasattr(value, "groups") and hasattr(value, "flags"):
        return normalize_pattern(value)
    raise PracticeBenchmarkError(
        "a public API returned an unsupported observable: "
        + type(value).__qualname__,
    )


def normalize_exception(error: Exception, engine: Any = None) -> dict[str, Any]:
    public_error = getattr(engine, "error", None) if engine is not None else None
    if isinstance(public_error, type) and isinstance(error, public_error):
        return {
            "kind": "public-regex-pattern-error",
            "type": type(error).__qualname__,
            "is_engine_error": True,
            "args": normalize_value(error.args),
            "message": getattr(error, "msg", None),
            "pattern": normalize_value(getattr(error, "pattern", None)),
            "position": getattr(error, "pos", None),
            "line": getattr(error, "lineno", None),
            "column": getattr(error, "colno", None),
        }
    return {
        "kind": "ordinary-python-exception",
        "module": type(error).__module__,
        "type": type(error).__qualname__,
        "args": normalize_value(error.args),
    }


def normalize_warnings(records: Any) -> list[dict[str, Any]]:
    require(type(records) is list,
            "every genuine recorded public API warning must be retained")
    observations: list[dict[str, Any]] = []
    for warning in records:
        category = warning.category
        message = warning.message
        require(isinstance(category, type)
                and isinstance(message, Warning)
                and isinstance(message, category),
                "a genuine CPython warning category or message was substituted")
        observations.append({
            "category_module": category.__module__,
            "category": category.__qualname__,
            "message": str(message),
        })
    return observations


def prepare_case(
    engine: Any, case: Mapping[str, Any],
) -> Callable[[], dict[str, Any]]:
    expression = materialize_typed(case["pattern"])
    subject = materialize_typed(case["subject"])
    replacement = materialize_typed(case["replacement"])
    flags = case["flags"]
    limit = case["limit"]
    operation = case["operation"]
    require(type(flags) is int and type(limit) is int and 1 <= limit <= 3
            and operation in OPERATIONS
            and (
                (type(expression) is str
                 and type(subject) is str and type(replacement) is str)
                or (type(expression) is bytes
                    and type(subject) in (bytes, bytearray, memoryview)
                    and type(replacement) is bytes)
            ),
            "the frozen public operation, flags, or matching domain changed")
    compiled: Any = None
    if operation.startswith("pattern.") or operation.startswith("match."):
        compiled = engine.compile(expression, flags)
    serial = 0

    def perform_without_warnings() -> dict[str, Any]:
        nonlocal serial
        callbacks: list[dict[str, Any]] = []

        def callback(match: Any) -> str | bytes:
            callbacks.append(normalize_match(match))
            token = match.group(0)
            if type(token) is bytes:
                return b"<" + token.upper() + b">"
            require(type(token) is str,
                    "the public replacement callback changed its source domain")
            return "<" + token.upper() + ">"

        def failing_callback(match: Any) -> str | bytes:
            callbacks.append(normalize_match(match))
            raise ValueError("fresh public practice replacement callback failure")

        def scanner_callback(scanner: Any, token: Any) -> str | bytes:
            combined = scanner.scanner
            actual_match = scanner.match
            callbacks.append({
                "kind": "scanner-token", "token": normalize_value(token),
                "match": normalize_match(actual_match),
                "combined_pattern": normalize_pattern(combined),
                "match_uses_combined_pattern": actual_match.re is combined,
            })
            if type(token) is bytes:
                return b"<" + token.upper() + b">"
            require(type(token) is str,
                    "the real Scanner callback changed its public token type")
            return "<" + token.upper() + ">"

        def failing_scanner_callback(scanner: Any, token: Any) -> str | bytes:
            combined = scanner.scanner
            actual_match = scanner.match
            callbacks.append({
                "kind": "scanner-token", "token": normalize_value(token),
                "match": normalize_match(actual_match),
                "combined_pattern": normalize_pattern(combined),
                "match_uses_combined_pattern": actual_match.re is combined,
            })
            raise ValueError("fresh public practice scanner callback failure")

        try:
            if operation == "module.compile":
                result = engine.compile(expression, flags)
            elif operation in (
                "module.search", "module.match", "module.fullmatch",
                "module.findall", "module.finditer",
            ):
                name = operation.split(".", 1)[1]
                result = getattr(engine, name)(expression, subject, flags)
                if name == "finditer":
                    result = list(result)
            elif operation == "module.split":
                result = engine.split(
                    expression, subject, maxsplit=limit, flags=flags,
                )
            elif operation == "module.split.positional":
                result = engine.split(expression, subject, limit, flags)
            elif operation == "module.sub.positional":
                result = engine.sub(
                    expression, replacement, subject, limit, flags,
                )
            elif operation == "module.sub.positional_callback_error":
                result = engine.sub(
                    expression, failing_callback, subject, limit, flags,
                )
            elif operation == "module.subn.positional":
                result = engine.subn(
                    expression, replacement, subject, limit, flags,
                )
            elif operation == "module.subn.positional_callback_error":
                result = engine.subn(
                    expression, failing_callback, subject, limit, flags,
                )
            elif operation in (
                "module.sub.literal", "module.subn.literal",
                "module.sub.callback", "module.subn.callback",
                "module.sub.callback_error",
            ):
                name = "subn" if operation.startswith("module.subn.") else "sub"
                if operation.endswith("callback_error"):
                    actual_replacement: Any = failing_callback
                elif operation.endswith("callback"):
                    actual_replacement = callback
                else:
                    actual_replacement = replacement
                result = getattr(engine, name)(
                    expression, actual_replacement, subject,
                    count=limit, flags=flags,
                )
            elif operation in (
                "pattern.search", "pattern.match", "pattern.fullmatch",
                "pattern.findall", "pattern.finditer",
            ):
                name = operation.split(".", 1)[1]
                result = getattr(compiled, name)(subject)
                if name == "finditer":
                    result = list(result)
            elif operation == "pattern.split":
                result = compiled.split(subject, maxsplit=limit)
            elif operation in (
                "pattern.sub.literal", "pattern.subn.literal",
                "pattern.sub.callback", "pattern.subn.callback",
                "pattern.sub.callback_error",
            ):
                name = "subn" if operation.startswith("pattern.subn.") else "sub"
                if operation.endswith("callback_error"):
                    actual_replacement = failing_callback
                elif operation.endswith("callback"):
                    actual_replacement = callback
                else:
                    actual_replacement = replacement
                result = getattr(compiled, name)(
                    actual_replacement, subject, count=limit,
                )
            elif operation == "pattern.scanner.search":
                scanner = compiled.scanner(subject)
                result = scanner.search()
            elif operation == "pattern.scanner.match":
                scanner = compiled.scanner(subject)
                result = scanner.match()
            elif operation == "pattern.scanner.loop":
                scanner = compiled.scanner(subject)
                result = []
                while True:
                    match = scanner.search()
                    if match is None:
                        break
                    result.append(match)
                    require(len(result) <= 512,
                            "an actual public scanner failed to make progress")
            elif operation in ("scanner.scan", "scanner.scan.callback_error"):
                whitespace = r"\s+" if type(expression) is str else rb"\s+"
                action = (
                    failing_scanner_callback
                    if operation.endswith("callback_error") else scanner_callback
                )
                scanner = engine.Scanner(
                    [(expression, action), (whitespace, None)], flags=flags,
                )
                result = scanner.scan(subject)
            elif operation == "match.group":
                match = compiled.search(subject)
                result = None if match is None else {
                    "match": normalize_match(match),
                    "group_zero": match.group(0),
                    "named_groups": dict(match.groupdict()),
                    "all_groups": match.groups(),
                }
            elif operation == "match.expand":
                match = compiled.search(subject)
                result = None if match is None else match.expand(replacement)
            elif operation == "compile.fresh.search":
                suffix = "(?#fresh-public-practice-" + str(serial) + ")"
                serial += 1
                fresh_expression = (
                    expression + suffix if type(expression) is str
                    else expression + suffix.encode("ascii")
                )
                match = engine.compile(fresh_expression, flags).search(subject)
                result = None if match is None else {
                    "group": match.group(0),
                    "span": tuple(match.span(0)),
                    "groups": tuple(match.groups()),
                    "groupdict": dict(match.groupdict()),
                }
            else:
                raise PracticeBenchmarkError("an unfrozen public case was injected")
            return {
                "status": "return", "value": normalize_value(result),
                "callbacks": callbacks,
            }
        except PracticeBenchmarkError:
            raise
        except Exception as error:
            return {
                "status": "raise", "exception": normalize_exception(error, engine),
                "callbacks": callbacks,
            }

    def perform() -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as observed_warnings:
            warnings.simplefilter("always")
            result = perform_without_warnings()
            result["warnings"] = normalize_warnings(observed_warnings)
            return result

    return perform


def load_engine(name: str) -> Any:
    require(name in ("stdlib", "rust"),
            "only the pinned baseline or named from-scratch Rust candidate is valid")
    if name == "stdlib":
        verify_pinned_runtime()
        engine = importlib.import_module("re")
        require(engine.__name__ == "re" and type(engine.__file__) is str
                and os.path.abspath(engine.__file__) == str(PINNED_STDLIB_RE)
                and os.path.realpath(engine.__file__) == str(PINNED_STDLIB_RE),
                "the exact pinned no-symlink CPython re baseline was substituted")
        return engine
    verify_pinned_runtime()
    engine = importlib.import_module("candidates.rust_candidate")
    authenticate_rust_candidate(engine)
    return engine


def observe_worker(role: str, engine_name: str) -> dict[str, Any]:
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    engine = load_engine(engine_name)
    records: list[dict[str, Any]] = []
    for case in matrix:
        try:
            result = prepare_case(engine, case)()
        except PracticeBenchmarkError:
            raise
        except Exception as error:
            result = {
                "status": "raise", "exception": normalize_exception(error, engine),
                "callbacks": [], "warnings": [],
            }
        records.append({"case": case["case"], "outcome": result})
    require(len(records) == len(matrix),
            "an exact original public practice correctness case was skipped")
    return {
        "schema": SCHEMA + "-isolated-observations", "status": "PASS",
        "label": PRACTICE_LABEL, "role": role, "engine": engine_name,
        "pid": os.getpid(), "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256, "case_count": len(matrix),
        "records_sha256": digest(records), "records": records,
        "candidate_import_count": (
            sum(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules)
        ),
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "files_written": 0,
    }


def _validate_expected_records(
    expected: Any, matrix: list[dict[str, Any]], expected_hash: Any,
) -> dict[str, dict[str, Any]]:
    require(type(expected) is list and len(expected) == len(matrix)
            and type(expected_hash) is str and digest(expected) == expected_hash,
            "the complete public baseline outcome vector was substituted")
    results: dict[str, dict[str, Any]] = {}
    for case, record in zip(matrix, expected, strict=True):
        require(type(record) is dict
                and set(record) == {"case", "outcome"}
                and record.get("case") == case["case"]
                and type(record.get("outcome")) is dict
                and record["outcome"].get("status") in ("return", "raise")
                and type(record["outcome"].get("callbacks")) is list
                and type(record["outcome"].get("warnings")) is list,
                "a full exact source-ordered public baseline case was removed")
        results[case["case"]] = record["outcome"]
    return results


def timing_worker(role: str, engine_name: str) -> dict[str, Any]:
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    request = decode_canonical(
        sys.stdin.buffer.read(MAX_PROCESS_BYTES + 1),
        role + " complete original public timing request",
    )
    checks = {
        "schema": SCHEMA + "-timing-request",
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
    }
    for key, value in checks.items():
        require(request.get(key) == value,
                "the fixed public timing protocol changed: " + key)
    trial = request.get("trial")
    iterations = request.get("iterations")
    warmups = request.get("warmups")
    order = request.get("case_order")
    require(type(trial) is int and 0 <= trial < 1_000
            and type(iterations) is int and 1 <= iterations <= 1_000
            and type(warmups) is int and 0 <= warmups <= 100,
            "the fixed public paired trial or iteration count was substituted")
    expected_by_case = _validate_expected_records(
        request.get("expected_records"), matrix, request.get("expected_sha256"),
    )
    case_by_id = {case["case"]: case for case in matrix}
    require(type(order) is list and len(order) == len(matrix)
            and all(type(case_id) is str for case_id in order)
            and len(set(order)) == len(matrix)
            and set(order) == set(case_by_id),
            "an exact timed public case was omitted, duplicated, or substituted")
    engine = load_engine(engine_name)
    rows: list[dict[str, Any]] = []
    for position, case_id in enumerate(order):
        case = case_by_id[case_id]
        expected = expected_by_case[case_id]
        try:
            executor = prepare_case(engine, case)
            for _ in range(warmups):
                require(executor() == expected,
                        "a public warmup correctness mismatch: " + case_id)
            before = time.perf_counter_ns()
            for _ in range(iterations):
                require(executor() == expected,
                        "a public timed correctness mismatch: " + case_id)
            after = time.perf_counter_ns()
            require(executor() == expected,
                    "a public post-timing correctness mismatch: " + case_id)
        except Exception as error:
            raise PracticeBenchmarkError(
                "correctness-gated public timing failed at " + case_id
                + ": " + type(error).__qualname__ + ": " + str(error),
            ) from error
        elapsed = after - before
        require(type(elapsed) is int and elapsed > 0,
                "an actual public monotonic timed interval was not observed")
        rows.append({
            "case": case_id, "trial": trial, "position": position,
            "elapsed_ns": elapsed, "batch_iterations": iterations,
            "correctness_checks": warmups + iterations + 1,
            "expected_outcome_sha256": digest(expected),
        })
    return {
        "schema": SCHEMA + "-isolated-timing", "status": "PASS",
        "label": PRACTICE_LABEL, "role": role, "engine": engine_name,
        "pid": os.getpid(), "python": "3.14.6", "trial": trial,
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "expected_sha256": request["expected_sha256"],
        "case_count": len(matrix), "rows_sha256": digest(rows), "rows": rows,
        "candidate_import_count": (
            sum(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules)
        ),
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "files_written": 0,
    }


def run_isolated_worker(
    role: str, engine: str, mode: str, *, request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    require(type(role) is str and engine in ("stdlib", "rust")
            and mode in ("observe", "timing")
            and ((mode == "observe" and request is None)
                 or (mode == "timing" and type(request) is dict)),
            "only an explicit isolated public practice worker is permitted")
    command = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--internal-worker", "--engine", engine,
        "--worker-mode", mode, "--role", role,
    ]
    payload = None if request is None else canonical(request)
    require(payload is None or len(payload) <= MAX_PROCESS_BYTES,
            "an actual complete public timing request exceeds its safe bound")
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(ROOT), shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "LC_ALL": "C", "PATH": "/usr/bin:/bin",
        },
    )
    if mode == "observe":
        # No timeout: subprocess timeouts themselves sample a monotonic clock.
        # Correctness-only and baseline self-tests are strictly untimed.
        stdout, stderr = process.communicate(input=payload)
    else:
        try:
            stdout, stderr = process.communicate(
                input=payload, timeout=WORKER_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as error:
            process.kill()
            stdout, stderr = process.communicate()
            raise PracticeBenchmarkError(
                "the isolated public practice worker timed out: " + role,
            ) from error
    require(process.returncode == 0 and stderr == b"",
            "the isolated public practice worker failed: " + role
            + "; exit=" + str(process.returncode)
            + "; stderr=" + stderr[-1_500:].decode("utf-8", "replace"))
    document = decode_canonical(stdout, role + " complete worker stdout")
    require(document.get("status") == "PASS"
            and document.get("label") == PRACTICE_LABEL
            and document.get("role") == role
            and document.get("engine") == engine
            and type(document.get("pid")) is int
            and document["pid"] == process.pid
            and document.get("python") == "3.14.6"
            and document.get("published_seed") == PUBLISHED_SEED
            and document.get("matrix_sha256") == MATRIX_SHA256
            and document.get("benchmark_files_read") == 0
            and document.get("hidden_cases_read") == 0
            and document.get("files_written") == 0,
            "the authentic isolated practice process or protocol was forged")
    if engine == "stdlib":
        require(document.get("candidate_import_count") == 0,
                "the original-only worker imported a candidate")
    else:
        require(type(document.get("candidate_import_count")) is int
                and document["candidate_import_count"] > 0,
                "the explicit Rust worker did not import the named candidate")
    matrix = build_public_matrix()
    if mode == "observe":
        require(document.get("schema") == SCHEMA + "-isolated-observations"
                and document.get("case_count") == len(matrix),
                "a full original public correctness worker was substituted")
        _validate_expected_records(
            document.get("records"), matrix, document.get("records_sha256"),
        )
    else:
        require(request is not None
                and document.get("schema") == SCHEMA + "-isolated-timing"
                and document.get("case_count") == len(matrix)
                and document.get("trial") == request["trial"]
                and document.get("expected_sha256")
                == request["expected_sha256"]
                and type(document.get("rows")) is list
                and len(document["rows"]) == len(matrix)
                and document.get("rows_sha256") == digest(document["rows"]),
                "a complete paired correctness-gated timing was substituted")
        for position, (case_id, row) in enumerate(zip(
            request["case_order"], document["rows"], strict=True,
        )):
            require(type(row) is dict and row.get("case") == case_id
                    and row.get("trial") == request["trial"]
                    and row.get("position") == position
                    and type(row.get("elapsed_ns")) is int
                    and row["elapsed_ns"] > 0
                    and row.get("batch_iterations") == request["iterations"]
                    and row.get("correctness_checks")
                    == request["warmups"] + request["iterations"] + 1,
                    "an actual paired trial, count, or correctness gate was forged")
    return document


def geometric_mean(values: list[float]) -> float:
    require(type(values) is list and bool(values)
            and all(type(value) in (float, int)
                    and math.isfinite(value) and value > 0 for value in values),
            "a geometric mean requires all actual finite positive case ratios")
    return math.exp(math.fsum(math.log(value) for value in values) / len(values))


def bootstrap_case_interval(
    pairs: list[tuple[int, int]], seed: int,
) -> dict[str, float | int | str]:
    require(type(pairs) is list and bool(pairs)
            and all(type(pair) is tuple and len(pair) == 2
                    and all(type(value) is int and value > 0 for value in pair)
                    for pair in pairs),
            "every original paired public trial is required for its interval")
    generator = random.Random(seed)
    estimates: list[float] = []
    count = len(pairs)
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [pairs[generator.randrange(count)] for _ in range(count)]
        estimates.append(geometric_mean([
            baseline / candidate for baseline, candidate in sample
        ]))
    estimates.sort()
    lower = estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.025)]
    upper = estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.975)]
    return {
        "method": "published-seed paired percentile bootstrap",
        "confidence_level": 0.95,
        "resamples": BOOTSTRAP_RESAMPLES,
        "lower": lower, "upper": upper,
    }


def bootstrap_overall_interval(
    cases: list[list[tuple[int, int]]], seed: int,
) -> dict[str, float | int | str]:
    require(type(cases) is list and bool(cases)
            and all(type(pairs) is list and bool(pairs) for pairs in cases),
            "all equally weighted public cases are mandatory for overall intervals")
    generator = random.Random(seed)
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        paired_case_estimates: list[float] = []
        for _ in range(len(cases)):
            sample_case = cases[generator.randrange(len(cases))]
            resampled_ratios: list[float] = []
            for _ in range(len(sample_case)):
                baseline, candidate = sample_case[
                    generator.randrange(len(sample_case))
                ]
                require(type(baseline) is int and baseline > 0
                        and type(candidate) is int and candidate > 0,
                        "an invalid original overall paired trial was injected")
                resampled_ratios.append(baseline / candidate)
            paired_case_estimates.append(geometric_mean(resampled_ratios))
        estimates.append(geometric_mean(paired_case_estimates))
    estimates.sort()
    return {
        "method": (
            "published-seed equally weighted case-and-paired-trial "
            "geometric-mean bootstrap"
        ),
        "confidence_level": 0.95,
        "resamples": BOOTSTRAP_RESAMPLES,
        "lower": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.025)],
        "upper": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.975)],
    }


def summarize_paired_trials(
    matrix: list[dict[str, Any]], raw_rows: list[dict[str, Any]],
    *, trial_count: int,
) -> dict[str, Any]:
    validate_public_matrix(matrix)
    require(type(trial_count) is int and trial_count > 0
            and type(raw_rows) is list
            and len(raw_rows) == len(matrix) * trial_count,
            "all cases and paired trials are required in the public denominator")
    by_case: dict[str, list[dict[str, Any]]] = {
        case["case"]: [] for case in matrix
    }
    for row in raw_rows:
        require(type(row) is dict and row.get("case") in by_case
                and type(row.get("trial")) is int
                and 0 <= row["trial"] < trial_count
                and type(row.get("baseline_elapsed_ns")) is int
                and row["baseline_elapsed_ns"] > 0
                and type(row.get("rust_elapsed_ns")) is int
                and row["rust_elapsed_ns"] > 0,
                "an original paired public timing row was substituted")
        by_case[row["case"]].append(row)
    summaries: list[dict[str, Any]] = []
    all_pairs: list[list[tuple[int, int]]] = []
    for index, case in enumerate(matrix):
        rows = sorted(by_case[case["case"]], key=lambda item: item["trial"])
        require(len(rows) == trial_count
                and [row["trial"] for row in rows] == list(range(trial_count)),
                "an actual paired public trial was duplicated or omitted")
        pairs = [
            (row["baseline_elapsed_ns"], row["rust_elapsed_ns"])
            for row in rows
        ]
        all_pairs.append(pairs)
        baseline_median = statistics.median([pair[0] for pair in pairs])
        rust_median = statistics.median([pair[1] for pair in pairs])
        ratio = geometric_mean([
            baseline / candidate for baseline, candidate in pairs
        ])
        interval = bootstrap_case_interval(
            pairs, PUBLISHED_SEED ^ ((index + 1) * 0x9E37_79B9),
        )
        summaries.append({
            "case": case["case"], "dataset": case["dataset"],
            "domain": case["domain"], "operation": case["operation"],
            "lifecycle": case["lifecycle"], "flags": case["flags"],
            "weight_numerator": 1,
            "weight_denominator": len(matrix),
            "paired_trial_count": trial_count,
            "baseline_median_batch_ns_descriptive": baseline_median,
            "rust_median_batch_ns_descriptive": rust_median,
            "median_batch_ratio_descriptive": baseline_median / rust_median,
            "point_estimator": "geometric mean of all paired trial ratios",
            "speedup_vs_baseline": ratio,
            "rust_change_percent": (1.0 / ratio - 1.0) * 100.0,
            "speedup_confidence_interval": interval,
            "statistically_faster": interval["lower"] > 1.0,
            "statistically_slower": interval["upper"] < 1.0,
            "regression_exceeds_20_percent": (1.0 / ratio) > 1.2,
        })
    overall = geometric_mean([
        item["speedup_vs_baseline"] for item in summaries
    ])
    interval = bootstrap_overall_interval(
        all_pairs, PUBLISHED_SEED ^ 0xA110_CAFE,
    )
    faster = sum(item["statistically_faster"] for item in summaries)
    slower = sum(item["statistically_slower"] for item in summaries)
    regressions = [
        item for item in summaries if item["regression_exceeds_20_percent"]
    ]
    return {
        "label": PRACTICE_LABEL,
        "weight_policy": "each of the frozen public cases has identical weight",
        "point_estimator": (
            "equally weighted geometric mean of each case's "
            "geometric mean of all original paired trial ratios"
        ),
        "timed_interval": (
            "full public regex operation, result materialization, exact "
            "observable and warning normalization, and per-call "
            "baseline-outcome correctness comparison; not native-only timing"
        ),
        "case_denominator": len(matrix),
        "paired_trials_per_case": trial_count,
        "baseline_first_paired_rounds": (trial_count + 1) // 2,
        "rust_first_paired_rounds": trial_count // 2,
        "pair_order_is_exactly_balanced": trial_count % 2 == 0,
        "total_complete_paired_rows": len(raw_rows),
        "text_case_count": sum(item["domain"] == "text" for item in matrix),
        "bytes_case_count": sum(item["domain"] == "bytes" for item in matrix),
        "operation_count": len(OPERATIONS),
        "weighted_geomean_speedup_vs_baseline": overall,
        "overall_speedup_confidence_interval": interval,
        "statistically_faster_case_count": faster,
        "statistically_faster_fraction": faster / len(matrix),
        "statistically_slower_case_count": slower,
        "regression_over_20_percent_count": len(regressions),
        "all_regressions_over_20_percent": regressions,
        "all_case_results": summaries,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def run_correctness_only() -> dict[str, Any]:
    """Compare every public result without sampling a clock or writing a file."""
    verify_pinned_runtime()
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    baseline = run_isolated_worker(
        "untimed_public_baseline_correctness", "stdlib", "observe",
    )
    candidate = run_isolated_worker(
        "untimed_public_rust_correctness", "rust", "observe",
    )
    require(baseline["pid"] != candidate["pid"],
            "the full public correctness engines are not isolated processes")
    baseline_records = baseline["records"]
    candidate_records = candidate["records"]
    mismatches: list[dict[str, Any]] = []
    for case, original, rust in zip(
        matrix, baseline_records, candidate_records, strict=True,
    ):
        require(original["case"] == rust["case"] == case["case"],
                "the original complete correctness case order was substituted")
        if original["outcome"] != rust["outcome"]:
            mismatches.append({
                "case": case["case"],
                "dataset": case["dataset"], "domain": case["domain"],
                "operation": case["operation"],
                "lifecycle": case["lifecycle"], "flags": case["flags"],
                "pattern": case["pattern"], "subject": case["subject"],
                "replacement": case["replacement"], "limit": case["limit"],
                "baseline_outcome": original["outcome"],
                "rust_outcome": rust["outcome"],
            })
    require(len(baseline_records) == len(candidate_records) == len(matrix)
            and len(mismatches) <= len(matrix),
            "a full-vector public correctness observation was omitted")
    return {
        "schema": SCHEMA + "-actual-untimed-correctness",
        "status": "PASS" if not mismatches else "FAIL",
        "label": PRACTICE_LABEL,
        "python": "3.14.6", "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_denominator": len(matrix),
        "actual_baseline_cases": len(baseline_records),
        "actual_rust_cases": len(candidate_records),
        "baseline_records_sha256": baseline["records_sha256"],
        "rust_records_sha256": candidate["records_sha256"],
        "baseline_pid": baseline["pid"], "rust_pid": candidate["pid"],
        "mismatch_count": len(mismatches),
        "first_mismatch": mismatches[0] if mismatches else None,
        "all_mismatches": mismatches,
        "actual_candidate_workers": 1,
        "timing_trials_run": 0, "clock_samples": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "files_written": 0, "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def run_public_practice(
    *, trials: int, iterations: int, warmups: int,
) -> dict[str, Any]:
    verify_pinned_runtime()
    require(type(trials) is int and 2 <= trials <= 100
            and type(iterations) is int and 1 <= iterations <= 1_000
            and type(warmups) is int and 0 <= warmups <= 100,
            "public paired trial, batch, and warmup counts must be explicit")
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    baseline = run_isolated_worker(
        "public_baseline_correctness", "stdlib", "observe",
    )
    candidate = run_isolated_worker(
        "public_rust_correctness", "rust", "observe",
    )
    require(baseline["pid"] != candidate["pid"],
            "the actual baseline and Rust correctness processes are not isolated")
    baseline_records = baseline["records"]
    candidate_records = candidate["records"]
    require(baseline_records == candidate_records
            and baseline["records_sha256"] == candidate["records_sha256"],
            "the Rust candidate failed the complete original public correctness gate")
    raw_rows: list[dict[str, Any]] = []
    trial_provenance: list[dict[str, Any]] = []
    for trial in range(trials):
        case_order = [case["case"] for case in matrix]
        random.Random(PUBLISHED_SEED ^ (trial + 1)).shuffle(case_order)
        request = {
            "schema": SCHEMA + "-timing-request",
            "published_seed": PUBLISHED_SEED,
            "matrix_sha256": MATRIX_SHA256, "trial": trial,
            "iterations": iterations, "warmups": warmups,
            "expected_sha256": baseline["records_sha256"],
            "expected_records": baseline_records,
            "case_order": case_order,
        }
        order = ("stdlib", "rust") if trial % 2 == 0 else ("rust", "stdlib")
        actual: dict[str, dict[str, Any]] = {}
        for position, engine in enumerate(order):
            role = "public_trial_" + format(trial, "03d") + "_" + engine
            document = run_isolated_worker(
                role, engine, "timing", request=request,
            )
            actual[engine] = document
            trial_provenance.append({
                "trial": trial, "engine": engine,
                "pair_execution_position": position,
                "pid": document["pid"],
                "rows_sha256": document["rows_sha256"],
            })
        require(actual["stdlib"]["pid"] != actual["rust"]["pid"],
                "an actual paired trial reused its reference process")
        for baseline_row, rust_row in zip(
            actual["stdlib"]["rows"], actual["rust"]["rows"], strict=True,
        ):
            require(baseline_row["case"] == rust_row["case"]
                    and baseline_row["trial"] == rust_row["trial"] == trial
                    and baseline_row["position"] == rust_row["position"]
                    and baseline_row["expected_outcome_sha256"]
                    == rust_row["expected_outcome_sha256"],
                    "an actual paired public timing lost its common correctness case")
            raw_rows.append({
                "case": baseline_row["case"], "trial": trial,
                "case_order_position": baseline_row["position"],
                "pair_order": list(order),
                "baseline_pid": actual["stdlib"]["pid"],
                "rust_pid": actual["rust"]["pid"],
                "batch_iterations": iterations,
                "correctness_checks_per_engine": baseline_row["correctness_checks"],
                "expected_outcome_sha256": baseline_row["expected_outcome_sha256"],
                "baseline_elapsed_ns": baseline_row["elapsed_ns"],
                "rust_elapsed_ns": rust_row["elapsed_ns"],
            })
    require(len(raw_rows) == len(matrix) * trials,
            "a complete paired public practice case or trial was omitted")
    return {
        "schema": SCHEMA + "-actual-public-practice-report",
        "status": "PASS", "label": PRACTICE_LABEL,
        "python": "3.14.6", "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": len(matrix),
        "matrix": matrix,
        "correctness_reference_records_sha256": baseline["records_sha256"],
        "correctness_reference_records": baseline_records,
        "baseline_correctness_pid": baseline["pid"],
        "rust_correctness_pid": candidate["pid"],
        "paired_trials": trials, "batch_iterations": iterations,
        "warmup_iterations": warmups,
        "trial_process_provenance": trial_provenance,
        "raw_paired_rows_sha256": digest(raw_rows),
        "raw_paired_rows": raw_rows,
        "results": summarize_paired_trials(matrix, raw_rows, trial_count=trials),
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "candidate_production_reference_delegation": (
            "NOT AUDITED BY PUBLIC PRACTICE"
        ),
        "final_winner_selected": False,
    }


def approved_output_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and bool(value)
            and "\x00" not in value and "\\" not in value,
            "an exact approved public-practice output path is mandatory")
    if os.path.isabs(value):
        prefix = str(ROOT) + os.sep
        require(value.startswith(prefix),
                "an output outside the approved repository root is forbidden")
        relative = value[len(prefix):]
    else:
        relative = value
    pure = PurePosixPath(relative)
    require(not pure.is_absolute() and ".." not in pure.parts
            and pure.as_posix() == relative
            and len(pure.parts) >= 3
            and pure.parts[0:2] == ("experiments", "rust_public_practice_v1")
            and pure.parts[-1].endswith(".json")
            and pure.parts[-1] not in (".json",),
            "write only an explicitly named JSON under " + OUTPUT_PREFIX)
    return pure.parts


def write_approved_output(value: str, document: Mapping[str, Any]) -> dict[str, Any]:
    parts = approved_output_parts(value)
    payload = canonical(dict(document))
    require(0 < len(payload) <= MAX_OUTPUT_BYTES,
            "a complete bounded public-practice report is required")
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    opened: list[int] = []
    writer: int | None = None
    directory: int | None = None
    writer_info: Any = None
    durable = False
    try:
        current = os.open(str(ROOT), directory_flags)
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the actual public-practice root is not a real directory")
        for name in parts[:-1]:
            try:
                following = os.open(name, directory_flags, dir_fd=current)
            except FileNotFoundError:
                os.mkdir(name, mode=0o755, dir_fd=current)
                following = os.open(name, directory_flags, dir_fd=current)
            opened.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "an approved output component is not a no-follow directory")
            current = following
        directory = current
        writer = os.open(
            parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o644, dir_fd=directory,
        )
        writer_info = os.fstat(writer)
        require(stat.S_ISREG(writer_info.st_mode),
                "the exclusively created practice report is not a regular file")
        written = os.write(writer, payload)
        require(type(written) is int and written == len(payload),
                "the explicit public-practice report write was short or forged")
        os.fsync(writer)
        os.fsync(directory)
        durable = True
        return {
            "path": "/".join(parts),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload), "actual_write_calls": 1,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
        }
    finally:
        if writer is not None and not durable and writer_info is not None \
                and directory is not None:
            try:
                actual = os.stat(
                    parts[-1], dir_fd=directory, follow_symlinks=False,
                )
                if stat.S_ISREG(actual.st_mode) \
                        and actual.st_dev == writer_info.st_dev \
                        and actual.st_ino == writer_info.st_ino:
                    os.unlink(parts[-1], dir_fd=directory)
                    os.fsync(directory)
            except OSError:
                pass
        if writer is not None:
            os.close(writer)
        for descriptor in reversed(opened):
            os.close(descriptor)


def source_self_test() -> dict[str, Any]:
    verify_pinned_runtime()
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    require(len(matrix) == 864 and len(OPERATIONS) == 36,
            "the exact balanced original public practice denominator changed")
    first = run_isolated_worker("public_selftest_baseline_a", "stdlib", "observe")
    second = run_isolated_worker("public_selftest_baseline_b", "stdlib", "observe")
    require(first["pid"] != second["pid"],
            "the two actual baseline self-test processes are not independent")
    require(first["records"] == second["records"]
            and first["records_sha256"] == second["records_sha256"],
            "the pinned original CPython disagreed with itself on public cases")
    actual_records = {
        record["case"]: record["outcome"] for record in first["records"]
    }
    scanner_remainder_cases = (
        ("text.scanner_remainder", "str", None),
        ("bytes.bytearray.scanner_remainder", "bytearray", None),
        ("bytes.memoryview.mutable.scanner_remainder", "memoryview", False),
        ("bytes.memoryview.readonly.scanner_remainder", "memoryview", True),
    )
    expected_remainder_hex = b"!unconsumed tail9".hex()
    for dataset, expected_kind, readonly in scanner_remainder_cases:
        scan_case = next(
            case for case in matrix
            if case["dataset"] == dataset and case["operation"] == "scanner.scan"
        )
        observed = actual_records[scan_case["case"]]
        require(observed.get("status") == "return"
                and len(observed.get("callbacks", ())) == 2
                and type(observed.get("value")) is dict
                and observed["value"].get("kind") == "tuple"
                and type(observed["value"].get("items")) is list
                and len(observed["value"]["items"]) == 2,
                "the genuine baseline Scanner remainder was not observed: "
                + dataset)
        for callback in observed["callbacks"]:
            require(type(callback) is dict
                    and callback.get("kind") == "scanner-token"
                    and callback.get("match_uses_combined_pattern") is True
                    and type(callback.get("match")) is dict
                    and callback["match"].get("kind") == "match"
                    and callback["match"].get("lastindex") == 1
                    and type(callback.get("combined_pattern")) is dict
                    and callback["combined_pattern"].get("kind")
                    == "compiled-pattern"
                    and callback["combined_pattern"].get("groups") == 2,
                    "the actual live combined Scanner callback match was hidden: "
                    + dataset)
        remainder = observed["value"]["items"][1]
        if expected_kind == "str":
            require(remainder == "!unconsumed tail9",
                    "the genuine public text Scanner remainder was changed")
        else:
            require(type(remainder) is dict
                    and remainder.get("kind") == expected_kind
                    and remainder.get("hex") == expected_remainder_hex,
                    "the original byte-like Scanner remainder was coerced: "
                    + dataset)
            if expected_kind == "memoryview":
                require(remainder.get("readonly") is readonly
                        and remainder.get("shape") == [17]
                        and remainder.get("strides") == [1]
                        and remainder.get("format") == "B"
                        and remainder.get("contiguous") is True,
                        "an original Scanner memoryview lost its shape or mutability")
        error_case = next(
            case for case in matrix
            if case["dataset"] == dataset
            and case["operation"] == "scanner.scan.callback_error"
        )
        error = actual_records[error_case["case"]]
        require(error.get("status") == "raise"
                and len(error.get("callbacks", ())) == 1
                and type(error.get("exception")) is dict
                and error["exception"].get("module") == "builtins"
                and error["exception"].get("type") == "ValueError",
                "the genuine Scanner callback sequence or error was omitted: "
                + dataset)
        error_callback = error["callbacks"][0]
        require(type(error_callback) is dict
                and error_callback.get("match_uses_combined_pattern") is True
                and type(error_callback.get("match")) is dict
                and error_callback["match"].get("lastindex") == 1
                and type(error_callback.get("combined_pattern")) is dict
                and error_callback["combined_pattern"].get("groups") == 2,
                "the live combined Scanner match before a real error was hidden: "
                + dataset)

    positional_warning_operations = (
        ("module.split.positional", "return"),
        ("module.sub.positional", "return"),
        ("module.subn.positional", "return"),
        ("module.sub.positional_callback_error", "raise"),
        ("module.subn.positional_callback_error", "raise"),
    )
    for operation, expected_status in positional_warning_operations:
        warning_case = next(
            case for case in matrix
            if case["dataset"] == "text.ascii.ignorecase"
            and case["operation"] == operation
        )
        actual = actual_records[warning_case["case"]]
        warnings_observed = actual.get("warnings")
        require(actual.get("status") == expected_status
                and type(warnings_observed) is list
                and len(warnings_observed) == 1
                and warnings_observed[0].get("category_module") == "builtins"
                and warnings_observed[0].get("category") == "DeprecationWarning"
                and type(warnings_observed[0].get("message")) is str,
                "a genuine 3.14 positional warning or raised outcome was hidden: "
                + operation)
    fake_pairs = [(100, 100), (103, 103), (107, 107), (109, 109)]
    first_interval = bootstrap_case_interval(fake_pairs, PUBLISHED_SEED)
    second_interval = bootstrap_case_interval(fake_pairs, PUBLISHED_SEED)
    require(first_interval == second_interval
            and first_interval["lower"] == first_interval["upper"] == 1.0,
            "the published-seed baseline-vs-baseline bootstrap is not deterministic")
    overall = bootstrap_overall_interval(
        [fake_pairs, list(reversed(fake_pairs))], PUBLISHED_SEED,
    )
    require(overall["lower"] == overall["upper"] == 1.0,
            "the equally weighted baseline self-comparison was not exactly 1x")
    rejected_paths: list[str] = []
    for forbidden in (
        "/tmp/foreign-public-practice.json",
        "../foreign-public-practice.json",
        "experiments/foreign-public-practice.json",
        "experiments/rust_public_practice_v1/../foreign.json",
        "experiments/rust_public_practice_v1/not-json.txt",
    ):
        try:
            approved_output_parts(forbidden)
        except PracticeBenchmarkError:
            rejected_paths.append(forbidden)
        else:
            raise PracticeBenchmarkError(
                "an unapproved public-practice output path was accepted",
            )
    require(len(rejected_paths) == 5
            and not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ), "a source self-test inspected or imported a candidate")
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "label": PRACTICE_LABEL, "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": len(matrix), "operation_count": len(OPERATIONS),
        "dataset_count": 24, "text_case_count": 432,
        "bytes_case_count": 432,
        "weight_policy": "each of the 864 public cases has identical weight",
        "baseline_vs_baseline_reference_count": 2,
        "baseline_reference_pids": [first["pid"], second["pid"]],
        "baseline_records_sha256": first["records_sha256"],
        "seeded_bootstrap_baseline_speedup": 1.0,
        "seeded_bootstrap_baseline_confidence_interval": first_interval,
        "seeded_overall_baseline_confidence_interval": overall,
        "rejected_unapproved_output_count": len(rejected_paths),
        "verified_scanner_remainder_types": [
            "str", "bytearray", "mutable memoryview", "readonly memoryview",
        ],
        "verified_scanner_callback_error_cases": len(scanner_remainder_cases),
        "verified_positional_warning_operations": [
            operation for operation, _ in positional_warning_operations
        ],
        "default_paired_rounds": DEFAULT_PAIRED_TRIALS,
        "default_pair_order_exactly_balanced": (
            DEFAULT_PAIRED_TRIALS % 2 == 0
        ),
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Correctness-gated fresh PUBLIC PRACTICE ONLY Rust comparisons; "
            "never a hidden or final benchmark"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--correctness-only", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--internal-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--output")
    parser.add_argument("--trials", type=int, default=DEFAULT_PAIRED_TRIALS)
    parser.add_argument("--iterations", type=int,
                        default=DEFAULT_BATCH_ITERATIONS)
    parser.add_argument("--warmups", type=int,
                        default=DEFAULT_WARMUP_ITERATIONS)
    parser.add_argument("--engine", choices=("stdlib", "rust"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--worker-mode", choices=("observe", "timing"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--role", help=argparse.SUPPRESS)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(options.output is None and options.engine is None
                and options.worker_mode is None and options.role is None,
                "source-only public self-tests cannot run or write a candidate")
        document = source_self_test()
    elif options.correctness_only:
        require(options.output is None and options.engine is None
                and options.worker_mode is None and options.role is None,
                "untimed correctness cannot write, time, or inject worker roles")
        require(options.trials == DEFAULT_PAIRED_TRIALS
                and options.iterations == DEFAULT_BATCH_ITERATIONS
                and options.warmups == DEFAULT_WARMUP_ITERATIONS,
                "untimed correctness cannot consume timing-trial parameters")
        document = run_correctness_only()
    elif options.run:
        require(options.engine is None and options.worker_mode is None
                and options.role is None,
                "the explicit paired public run cannot inject a worker role")
        if options.output is not None:
            approved_output_parts(options.output)
        document = run_public_practice(
            trials=options.trials, iterations=options.iterations,
            warmups=options.warmups,
        )
        if options.output is not None:
            publication = write_approved_output(options.output, document)
            document = {
                "schema": SCHEMA + "-published-public-practice-summary",
                "status": "PASS", "label": PRACTICE_LABEL,
                "matrix_sha256": MATRIX_SHA256,
                "case_count": document["case_count"],
                "raw_paired_rows_sha256": document["raw_paired_rows_sha256"],
                "results": document["results"],
                "publication": publication,
                "hidden_cases_read": 0,
                "final_winner_selected": False,
            }
    else:
        require(options.output is None and options.engine in ("stdlib", "rust")
                and options.worker_mode in ("observe", "timing")
                and type(options.role) is str and bool(options.role),
                "an internal isolated worker requires an exact explicit role")
        if options.worker_mode == "observe":
            document = observe_worker(options.role, options.engine)
        else:
            document = timing_worker(options.role, options.engine)
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PracticeBenchmarkError as error:
        print(
            "fresh public practice failed closed: " + str(error),
            file=sys.stderr,
        )
        raise SystemExit(1) from error
