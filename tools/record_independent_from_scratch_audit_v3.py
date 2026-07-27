#!/usr/bin/env python3
"""Durably record one explicitly pinned, independent V3 ownership audit.

``--self-test`` is strictly synthetic: it cannot read or write files, import a
candidate, start a worker, inspect a native binary, or sample a clock.  Only
``--record`` with every exact recorder, audit, candidate, source, lockfile, and
native pin can start one isolated V3 audit controller.  Complete success,
failure, timeout, crash, and subprocess streams are preserved in exactly two
fresh, durable, no-clobber report and receipt files.  Publishing a failure
successfully never turns that failure into an ownership pass.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
from dataclasses import dataclass
import gc
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/record_independent_from_scratch_audit_v3.py"
SCHEMA = "rebar-independent-from-scratch-audit-v3-recorder"
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
AUDIT_SCHEMA = "rebar-independent-from-scratch-audit-v3"
AUDIT_ORACLE = "independent-from-scratch-audit-v3"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_CTYPES = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/ctypes/__init__.py"
)
PINNED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
IMMUTABLE_POLICY_ITEMS = (
    (
        "tools/independent_from_scratch_audit_v2.py",
        "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d",
    ),
    (
        "tools/independent_original_cpython_suite_v5.py",
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
    ),
)
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 192 * 1024 * 1024

RUST_ENGINE_EXPORTS = frozenset({
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group",
    "rebar_name_len",
})
RUST_REQUIRED_BRIDGE_REFERENCES = frozenset({
    "rebar_compile", "rebar_compile_scanner", "rebar_match", "rebar_free",
})
ZIG_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures",
    "rebar_zig_collect_records", "rebar_zig_collect_records_wide",
    "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags",
    "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match",
    "rebar_zig_match_captures", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_tree", "rebar_zig_match_wide", "rebar_zig_name_copy",
    "rebar_zig_name_count", "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory", "rebar_zig_program_size",
})
ZIG_BRIDGE_REFERENCES = frozenset({
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
})
ZIG_CTYPES_SYMBOLS = frozenset({
    "rebar_zig_compile", "rebar_zig_free", "rebar_zig_groups",
    "rebar_zig_flags", "rebar_zig_program_memory", "rebar_zig_name_count",
    "rebar_zig_name_length", "rebar_zig_name_group", "rebar_zig_name_copy",
})
ZIG_SYSTEM_HELPERS = frozenset({
    "_PyUnicode_IsAlpha", "_PyUnicode_IsDecimalDigit", "_PyUnicode_IsDigit",
    "_PyUnicode_IsNumeric", "_PyUnicode_IsWhitespace",
    "_PyUnicode_ToLowercase", "_PyUnicode_ToUppercase", "tolower", "isalnum",
})


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    module: str
    bridge_module: str
    adapter: str
    bridge_source: str
    engine: str
    bridge: str
    sources: tuple[str, ...]
    binaries: tuple[str, ...]


FAMILY_SPECS = {
    "rust": FamilySpec(
        "rust",
        "candidates.rust_candidate",
        "candidates._rust_bridge",
        "candidates/rust_candidate.py",
        "candidates/rust/py_bridge.c",
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
        (
            "candidates/_rust_engine.so",
            "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        ),
    ),
    "c": FamilySpec(
        "c",
        "candidates.vm_candidate",
        "candidates._vm_native",
        "candidates/vm_candidate.py",
        "candidates/_vm_native.c",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
        ("candidates/_vm_native" + EXTENSION_SUFFIX,),
    ),
    "zig": FamilySpec(
        "zig",
        "candidates.zig_candidate",
        "candidates._zig_bridge",
        "candidates/zig_candidate.py",
        "candidates/zig/py_bridge.c",
        "candidates/_zig_probe.so",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
        (
            "candidates/_zig_probe.so",
            "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class OwnerPins:
    family: str
    recorder: str
    audit: str
    candidate: str
    native_engine: str
    native_bridge: str
    source_entries: tuple[str, ...]
    native_entries: tuple[str, ...]


class RecorderError(Exception):
    """An audit, family-owned closure, process, or publication is unsafe."""


class SourceOnlyError(RecorderError):
    """A synthetic control attempted a real effect."""


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
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise RecorderError("ownership evidence is not complete canonical JSON") from error


def validate_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value),
        "an exact independently caller-pinned SHA-256 is required: " + label,
    )
    return value


def verify_runtime(*, synthetic: bool = False) -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "use the exact isolated, no-bytecode, pinned CPython 3.14.6 recorder",
    )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "the audit recorder itself must never import a regex candidate",
    )
    if not synthetic:
        require(
            os.path.realpath(str(ROOT)) == str(ROOT)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "the exact pinned recorder, root, or interpreter is a symlink",
        )


def family_spec(value: Any) -> FamilySpec:
    require(
        type(value) is str and value in FAMILY_SPECS,
        "select exactly one independent Rust, C, or Zig candidate family",
    )
    spec = FAMILY_SPECS[value]
    require(
        type(spec) is FamilySpec
        and spec.name == value
        and spec.adapter in spec.sources
        and spec.bridge_source in spec.sources
        and spec.engine in spec.binaries
        and spec.bridge in spec.binaries
        and len(set(spec.sources)) == len(spec.sources)
        and len(set(spec.binaries)) == len(spec.binaries)
        and (spec.engine == spec.bridge) is (value == "c")
        and (len(spec.binaries) == 1) is (value == "c"),
        "an independently owned candidate family closure was substituted",
    )
    return spec


def safe_parts(relative: Any) -> tuple[str, ...]:
    require(
        type(relative) is str
        and bool(relative)
        and "\\" not in relative
        and "\x00" not in relative,
        "an exact bounded no-follow project-relative owner is mandatory",
    )
    parts = tuple(relative.split("/"))
    require(
        all(part not in ("", ".", "..") for part in parts)
        and "/".join(parts) == relative,
        "an ownership or evidence path escaped its canonical project root",
    )
    return parts


def parse_pin_entries(values: Any, label: str) -> dict[str, str]:
    require(
        type(values) in (tuple, list) and bool(values),
        "explicitly pin every independently owned " + label,
    )
    result: dict[str, str] = {}
    for item in values:
        require(type(item) is str, "a canonical path=SHA-256 pin is mandatory")
        relative, separator, pinned = item.partition("=")
        require(
            separator == "=" and "=" not in pinned,
            "a complete canonical path=SHA-256 pin is mandatory",
        )
        safe_parts(relative)
        validate_digest(pinned, label + " " + relative)
        require(
            relative not in result,
            "a caller repeated or concealed an owned artifact: " + relative,
        )
        result[relative] = pinned
    return dict(sorted(result.items()))


def validate_pins(pins: Any) -> tuple[FamilySpec, dict[str, Any]]:
    require(type(pins) is OwnerPins, "a complete caller-pinned V3 audit is mandatory")
    spec = family_spec(pins.family)
    for field in ("recorder", "audit", "candidate", "native_engine", "native_bridge"):
        validate_digest(getattr(pins, field), field)
    require(
        pins.audit == AUDIT_SHA256,
        "pin the exact independently frozen V3 ownership audit",
    )
    sources = parse_pin_entries(pins.source_entries, spec.name + " source")
    binaries = parse_pin_entries(pins.native_entries, spec.name + " native artifact")
    require(
        set(sources) == set(spec.sources),
        "pin every exact family-owned Python, native, Cargo, and lockfile source",
    )
    require(
        set(binaries) == set(spec.binaries),
        "pin every exact, distinct family-owned native binary",
    )
    require(
        sources[spec.adapter] == pins.candidate,
        "the explicit adapter pin does not match its complete owned closure",
    )
    require(
        binaries[spec.engine] == pins.native_engine,
        "the explicit native engine pin does not match its complete closure",
    )
    require(
        binaries[spec.bridge] == pins.native_bridge,
        "the explicit native bridge pin does not match its complete closure",
    )
    require(
        (pins.native_engine == pins.native_bridge) is (spec.name == "c"),
        "only the genuine combined C native engine and bridge may alias",
    )
    require(
        len(set(sources.values())) == len(sources)
        and len(set(binaries.values())) == len(binaries),
        "distinct owned source or native artifacts cannot share a substituted pin",
    )
    return spec, {
        "family": spec.name,
        "candidate_source_sha256": pins.candidate,
        "native_engine_sha256": pins.native_engine,
        "native_bridge_sha256": pins.native_bridge,
        "source_sha256": sources,
        "native_sha256": binaries,
        "immutable_policy_sha256": dict(IMMUTABLE_POLICY_ITEMS),
    }


def validate_label(value: Any) -> str:
    require(
        type(value) is str
        and 1 <= len(value) <= 64
        and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(letter in "abcdefghijklmnopqrstuvwxyz0123456789-" for letter in value)
        and "--" not in value,
        "a bounded, lowercase, nonescaping audit-run label is required",
    )
    return value


def approved_paths(family: Any, label: Any) -> tuple[str, str]:
    spec = family_spec(family)
    slug = spec.name + "-from-scratch-audit-v3-" + validate_label(label)
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


def directory_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def regular_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def read_owned_regular(relative: str, expected: str, maximum: int) -> dict[str, Any]:
    parts = safe_parts(relative)
    validate_digest(expected, relative)
    require(
        type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
        "an exact bounded source or native artifact is mandatory",
    )
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid owned repository root")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "an owned source parent was replaced by a symlink",
            )
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (before.st_dev, before.st_ino) == (named.st_dev, named.st_ino)
            and 0 < before.st_size <= maximum,
            "a caller-pinned owned source or binary is missing or substituted",
        )
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk), "an owned artifact was truncated")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "an owned artifact has a hidden suffix")
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "an independently owned artifact changed during authentication",
        )
        require(
            hasher.hexdigest() == expected,
            "an exact caller-pinned source or native binary changed: " + relative,
        )
        return {
            "relative": relative,
            "sha256": expected,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_pinned_external(absolute: Path, expected: str, maximum: int) -> dict[str, Any]:
    validate_digest(expected, str(absolute))
    require(
        absolute.is_absolute()
        and os.path.abspath(str(absolute)) == str(absolute)
        and os.path.realpath(str(absolute)) == str(absolute)
        and type(maximum) is int
        and 0 < maximum <= MAX_BINARY_BYTES,
        "an exact no-follow pinned CPython external owner is mandatory",
    )
    descriptor = os.open(str(absolute), regular_flags())
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
            "a pinned CPython external owner is not a bounded regular file",
        )
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk), "a pinned CPython owner was truncated")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "a pinned CPython owner has a hidden suffix")
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and hasher.hexdigest() == expected,
            "the pinned CPython interpreter or genuine FFI source was substituted",
        )
        return {
            "path": str(absolute),
            "sha256": expected,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        os.close(descriptor)


def validate_owned_file(value: Any, relative: str, expected: str, maximum: int) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {"relative", "sha256", "bytes", "device", "inode"}
        and value.get("relative") == relative
        and value.get("sha256") == expected
        and type(value.get("bytes")) is int
        and 0 < value["bytes"] <= maximum
        and type(value.get("device")) is int
        and value["device"] >= 0
        and type(value.get("inode")) is int
        and value["inode"] > 0,
        "an exact complete owned file identity was forged: " + relative,
    )
    return value


def validate_external_file(value: Any, absolute: Path, expected: str, maximum: int) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {"path", "sha256", "bytes", "device", "inode"}
        and value.get("path") == str(absolute)
        and value.get("sha256") == expected
        and type(value.get("bytes")) is int
        and 0 < value["bytes"] <= maximum
        and type(value.get("device")) is int
        and value["device"] >= 0
        and type(value.get("inode")) is int
        and value["inode"] > 0,
        "an exact pinned CPython external owner was forged",
    )
    return value


def authenticate_closure(pins: OwnerPins) -> dict[str, Any]:
    verify_runtime()
    spec, manifest = validate_pins(pins)
    closure = {
        "family": spec.name,
        "manifest": manifest,
        "recorder_owner": read_owned_regular(SOURCE_RELATIVE, pins.recorder, MAX_SOURCE_BYTES),
        "audit_owner": read_owned_regular(AUDIT_RELATIVE, pins.audit, MAX_SOURCE_BYTES),
        "policy_owners": {
            relative: read_owned_regular(relative, digest, MAX_SOURCE_BYTES)
            for relative, digest in IMMUTABLE_POLICY_ITEMS
        },
        "source_owners": {
            relative: read_owned_regular(relative, digest, MAX_SOURCE_BYTES)
            for relative, digest in manifest["source_sha256"].items()
        },
        "native_owners": {
            relative: read_owned_regular(relative, digest, MAX_BINARY_BYTES)
            for relative, digest in manifest["native_sha256"].items()
        },
        "python_owner": read_pinned_external(
            PINNED_PYTHON, PINNED_PYTHON_SHA256, MAX_BINARY_BYTES,
        ),
        "trusted_ctypes_owner": (
            read_pinned_external(PINNED_CTYPES, PINNED_CTYPES_SHA256, MAX_SOURCE_BYTES)
            if spec.name == "zig" else None
        ),
    }
    return validate_outer_closure(closure, pins)


def validate_outer_closure(value: Any, pins: OwnerPins) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    require(
        type(value) is dict
        and set(value) == {
            "family", "manifest", "recorder_owner", "audit_owner", "policy_owners",
            "source_owners", "native_owners", "python_owner", "trusted_ctypes_owner",
        }
        and value.get("family") == spec.name
        and value.get("manifest") == manifest,
        "a complete exact outer recorder and candidate ownership closure is mandatory",
    )
    validate_owned_file(value["recorder_owner"], SOURCE_RELATIVE, pins.recorder, MAX_SOURCE_BYTES)
    validate_owned_file(value["audit_owner"], AUDIT_RELATIVE, pins.audit, MAX_SOURCE_BYTES)
    policies = value["policy_owners"]
    sources = value["source_owners"]
    natives = value["native_owners"]
    require(
        type(policies) is dict
        and set(policies) == {relative for relative, _ in IMMUTABLE_POLICY_ITEMS}
        and type(sources) is dict
        and set(sources) == set(manifest["source_sha256"])
        and type(natives) is dict
        and set(natives) == set(manifest["native_sha256"]),
        "an immutable policy, owned source, lockfile, or native binary was omitted",
    )
    for relative, digest in IMMUTABLE_POLICY_ITEMS:
        validate_owned_file(policies[relative], relative, digest, MAX_SOURCE_BYTES)
    for relative, digest in manifest["source_sha256"].items():
        validate_owned_file(sources[relative], relative, digest, MAX_SOURCE_BYTES)
    for relative, digest in manifest["native_sha256"].items():
        validate_owned_file(natives[relative], relative, digest, MAX_BINARY_BYTES)
    validate_external_file(
        value["python_owner"], PINNED_PYTHON, PINNED_PYTHON_SHA256, MAX_BINARY_BYTES,
    )
    if spec.name == "zig":
        validate_external_file(
            value["trusted_ctypes_owner"],
            PINNED_CTYPES,
            PINNED_CTYPES_SHA256,
            MAX_SOURCE_BYTES,
        )
    else:
        require(
            value["trusted_ctypes_owner"] is None,
            "only the owned Zig candidate can authenticate the genuine pinned FFI",
        )
    return value


def require_directory_identity(
    retained: Any, expected: Any, literal: Any,
) -> None:
    require(
        type(retained) is tuple
        and type(expected) is tuple
        and type(literal) is tuple
        and len(retained) == len(expected) == len(literal) == 2
        and all(
            type(number) is int and number >= 0
            for identity in (retained, expected, literal)
            for number in identity
        )
        and retained == expected == literal,
        "the literal evidence path no longer names its retained owned directory",
    )


def retained_directory(preflight: Mapping[str, Any]) -> int:
    descriptor = preflight.get("directory_descriptor")
    require(
        type(descriptor) is int and descriptor >= 0,
        "retain the exact preflighted no-follow evidence directory",
    )
    retained = os.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode), "the retained evidence directory was replaced")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid literal evidence root")
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "a literal approved evidence parent was replaced with a symlink",
            )
        actual = os.fstat(current)
        require_directory_identity(
            (retained.st_dev, retained.st_ino),
            (preflight.get("directory_device"), preflight.get("directory_inode")),
            (actual.st_dev, actual.st_ino),
        )
    finally:
        for opened_descriptor in reversed(opened):
            os.close(opened_descriptor)
    return descriptor


@contextlib.contextmanager
def preflight_fresh_outputs(family: str, label: str) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(family, label)
    report_parts = safe_parts(report)
    receipt_parts = safe_parts(receipt)
    require(
        report_parts[:-1] == receipt_parts[:-1]
        and report_parts[:-1] == ("experiments", "rust_public_practice_v1")
        and report_parts[-1] != receipt_parts[-1],
        "preflight exactly two distinct owned V3 audit report and receipt paths",
    )
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid owned evidence root")
        for component in report_parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "an approved evidence parent follows a symlink",
            )
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError("refusing to overwrite existing V3 audit evidence: " + basename)
        info = os.fstat(current)
        result = {
            "report_relative": report,
            "receipt_relative": receipt,
            "report_basename": report_parts[-1],
            "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": info.st_dev,
            "directory_inode": info.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
        }
        retained_directory(result)
        yield result
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def readback(preflight: Mapping[str, Any], basename: str, expected: bytes) -> None:
    directory = retained_directory(preflight)
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        actual = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(
            stat.S_ISREG(actual.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (actual.st_dev, actual.st_ino) == (named.st_dev, named.st_ino)
            and actual.st_size == len(expected),
            "the durable V3 audit publication changed inode, type, or size",
        )
        remaining = len(expected)
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(
                type(chunk) is bytes and bool(chunk),
                "the complete durable V3 audit report was truncated",
            )
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "V3 audit evidence has a hidden suffix")
        require(b"".join(chunks) == expected, "complete V3 audit evidence was altered")
    finally:
        os.close(descriptor)
    retained_directory(preflight)


def publish_atomic(
    preflight: Mapping[str, Any], document: Mapping[str, Any], kind: str,
) -> dict[str, Any]:
    require(kind in ("report", "receipt"), "publish exactly one report and one receipt")
    directory = retained_directory(preflight)
    raw = canonical(dict(document))
    require(0 < len(raw) <= MAX_REPORT_BYTES, "a complete audit publication is unbounded")
    basename = preflight[kind + "_basename"]
    temporary = (
        ".rebar-from-scratch-audit-v3-"
        + basename
        + "-"
        + str(os.getpid())
        + "-"
        + hashlib.sha256(raw).hexdigest()[:24]
    )
    safe_parts(temporary)
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    retained_directory(preflight)
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    identity: tuple[int, int] | None = None
    linked = False
    write_calls = 0
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode), "the V3 audit temporary is not regular")
        identity = (initial.st_dev, initial.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity, "the audit temporary was replaced")
        position = 0
        while position < len(raw):
            count = os.write(descriptor, raw[position:])
            require(type(count) is int and count > 0, "the complete audit write was truncated")
            position += count
            write_calls += 1
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        require(
            (final.st_dev, final.st_ino) == identity and final.st_size == len(raw),
            "the complete V3 audit temporary lost bytes or ownership",
        )
        retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity, "the temporary changed before publication")
        os.link(
            temporary,
            basename,
            src_dir_fd=directory,
            dst_dir_fd=directory,
            follow_symlinks=False,
        )
        linked = True
        os.fsync(directory)
        retained_directory(preflight)
        destination = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(
            (destination.st_dev, destination.st_ino) == identity,
            "the no-overwrite V3 audit publication was substituted",
        )
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity, "refusing to unlink an unowned temporary")
        os.unlink(temporary, dir_fd=directory)
        os.fsync(directory)
        retained_directory(preflight)
    except BaseException:
        if not linked and identity is not None:
            try:
                named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
                if (named.st_dev, named.st_ino) == identity:
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
            except (OSError, RecorderError):
                pass
        raise
    finally:
        os.close(descriptor)
    readback(preflight, basename, raw)
    return {
        "path": preflight[kind + "_relative"],
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "actual_write_calls": write_calls,
        "atomic_no_overwrite_link_completed": True,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "owned_temporary_removed": True,
        "complete_readback_verified": True,
    }


def capture_stream(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
        "a complete bounded controller or native-worker stream is required: " + label,
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
        "a complete reversible ownership process stream was omitted: " + label,
    )
    validate_digest(value.get("sha256"), label)
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (TypeError, ValueError, UnicodeError) as error:
        raise RecorderError("a complete ownership process stream is invalid: " + label) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == value["sha256"]
        and base64.b64encode(raw).decode("ascii") == value["base64"],
        "a complete ownership process stream was truncated or substituted: " + label,
    )
    return raw


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result, "duplicate audit JSON fields conceal a failure")
        result[key] = value
    return result


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
        "the complete bounded genuine V3 audit stdout is required: " + label,
    )

    def reject_constant(_: str) -> Any:
        raise RecorderError("nonfinite ownership JSON is forbidden")

    try:
        result = json.loads(
            raw,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (RecorderError, TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise RecorderError("the complete V3 audit stdout is not canonical JSON: " + label) from error
    require(
        type(result) is dict and canonical(result) == raw,
        "complete V3 audit stdout was reordered, truncated, extended, or substituted",
    )
    return result


def expected_adapter(spec: FamilySpec) -> dict[str, Any]:
    if spec.name == "rust":
        return {
            "modules": sorted(("enum", "operator", "os", "types", "unicodedata", "warnings")),
            "from_imports": [["candidates", "_rust_bridge", None]],
        }
    if spec.name == "c":
        return {
            "modules": sorted(("enum", "os", "types", "unicodedata", "warnings")),
            "from_imports": [
                ["candidates", "_vm_native", None],
                ["copyreg", "_reconstructor", "_copy_reconstructor"],
                ["struct", "calcsize", "_native_calcsize"],
            ],
        }
    return {
        "modules": sorted(("ctypes", "enum", "os", "types", "unicodedata", "warnings")),
        "from_imports": [["candidates", "_zig_bridge", None]],
        "owned_ctypes": {
            "owned_library": "candidates/_zig_probe.so",
            "configured_symbols": sorted(ZIG_CTYPES_SYMBOLS),
        },
    }


def expected_bridge(spec: FamilySpec) -> dict[str, Any]:
    if spec.name == "rust":
        headers = ("Python.h", "stddef.h", "stdint.h", "string.h")
        imports = ("copyreg", "functools", "inspect")
    elif spec.name == "c":
        headers = ("Python.h", "ctype.h", "stddef.h", "stdint.h", "stdlib.h", "string.h")
        imports = ()
    else:
        headers = ("Python.h", "stddef.h", "stdint.h")
        imports = ()
    return {
        "includes": sorted(headers),
        "compatibility_imports": sorted(imports),
        "owned_compatible_scanner_names": 1,
    }


def expected_implementation(spec: FamilySpec) -> dict[str, Any]:
    if spec.name == "rust":
        return {
            "cargo": {
                "package": "rebar-rust-continuation",
                "package_count": 1,
                "external_package_count": 0,
                "build_script_count": 0,
            },
            "engine": {
                "source_count": 5,
                "owned_modules": ["newline", "search", "stack", "unicode_tables"],
            },
        }
    if spec.name == "c":
        return {"engine": "independently owned Python compiler and native C VM"}
    return {
        "engine": {
            "standard_library_imports": 1,
            "approved_unicode_and_system_helpers": sorted(ZIG_SYSTEM_HELPERS),
            "external_regex_package_count": 0,
        },
    }


def expected_dynamic(spec: FamilySpec, binary: str) -> tuple[list[str], list[str]]:
    require(binary in spec.binaries, "native ELF evidence crosses candidate-family ownership")
    if spec.name == "rust" and binary == spec.engine:
        return sorted(("libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2")), []
    if spec.name == "rust":
        return sorted(("_rust_engine.so", "libc.so.6")), ["$ORIGIN"]
    if spec.name == "c" or binary == spec.engine:
        return ["libc.so.6"], []
    return sorted(("_zig_probe.so", "libc.so.6")), ["$ORIGIN"]


def expected_exports(spec: FamilySpec, binary: str) -> list[str]:
    require(binary in spec.binaries, "native exports cross candidate-family ownership")
    if spec.name == "rust":
        return sorted(RUST_ENGINE_EXPORTS) if binary == spec.engine else ["PyInit__rust_bridge"]
    if spec.name == "c":
        return ["PyInit__vm_native"]
    return sorted(ZIG_ENGINE_EXPORTS) if binary == spec.engine else ["PyInit__zig_bridge"]


def validate_native(value: Any, spec: FamilySpec, manifest: Mapping[str, Any]) -> dict[str, Any]:
    require(
        type(value) is dict and set(value) == set(manifest["native_sha256"]),
        "inspect every and only the selected exact native ELF artifact",
    )
    for binary in spec.binaries:
        item = value.get(binary)
        needed, runpaths = expected_dynamic(spec, binary)
        require(
            type(item) is dict
            and set(item) == {
                "needed", "runpaths", "defined_exports",
                "undefined_symbol_count", "owned_engine_references",
            }
            and item.get("needed") == needed
            and item.get("runpaths") == runpaths
            and item.get("defined_exports") == expected_exports(spec, binary)
            and type(item.get("undefined_symbol_count")) is int
            and item["undefined_symbol_count"] > 0
            and type(item.get("owned_engine_references")) is list,
            "complete actual native ELF ownership, dependencies, or exports were forged: " + binary,
        )
        references = item["owned_engine_references"]
        require(
            all(type(name) is str for name in references)
            and references == sorted(set(references)),
            "owned native engine references are duplicated or noncanonical",
        )
        if spec.name == "rust" and binary == spec.bridge:
            require(
                set(references).issubset(RUST_ENGINE_EXPORTS)
                and RUST_REQUIRED_BRIDGE_REFERENCES.issubset(references),
                "the Rust bridge does not reference its own guarded native matcher",
            )
        elif spec.name == "zig" and binary == spec.bridge:
            require(
                references == sorted(ZIG_BRIDGE_REFERENCES),
                "the Zig bridge hides, duplicates, or borrows a native matcher",
            )
        else:
            require(references == [], "a native engine references a sibling matcher")
    return value


def validate_audit_owners(
    value: Any, pins: OwnerPins, outer: Mapping[str, Any],
) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    validate_outer_closure(dict(outer), pins)
    require(
        type(value) is dict
        and set(value) == {
            "family", "manifest", "source_owners", "native_owners",
            "policy_owners", "oracle_owner", "python_owner",
        }
        and value.get("family") == spec.name
        and value.get("manifest") == manifest
        and value.get("source_owners") == outer["source_owners"]
        and value.get("native_owners") == outer["native_owners"]
        and value.get("policy_owners") == outer["policy_owners"]
        and value.get("oracle_owner") == outer["audit_owner"]
        and value.get("python_owner") == outer["python_owner"],
        "the live audit and recorder did not inspect the same exact owned closure",
    )
    return value


def validate_runtime(
    value: Any,
    pins: OwnerPins,
    outer: Mapping[str, Any],
    controller_pid: int,
) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    expected: dict[str, Any] = {
        "schema": AUDIT_SCHEMA + "-isolated-worker",
        "status": "PASS",
        "family": spec.name,
        "oracle_source_sha256": pins.audit,
        "manifest": manifest,
        "forbidden_import_or_execution_count": 0,
        "caller_replacement_callback_supported": True,
        "owned_public_re_names_supported": True,
        "owned_public_sre_scanner_name_supported": True,
        "actual_standard_library_engine_loaded": False,
        "candidate_modules": sorted((spec.module, spec.bridge_module)),
        "owned_ctypes_library_load_count": 1 if spec.name == "zig" else 0,
        "owned_ctypes_symbols": sorted(ZIG_CTYPES_SYMBOLS) if spec.name == "zig" else [],
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
    require(
        type(value) is dict
        and set(value) == set(expected) | {
            "pid", "owners", "runtime_checks", "owned_graph_checks",
            "guarded_import_calls", "removed_preexisting_forbidden_module_count",
            "trusted_ctypes", "trusted_ctypes_owner",
        },
        "a complete genuinely isolated V3 native ownership worker is mandatory",
    )
    for key, original in expected.items():
        require(
            value.get(key) == original and type(value.get(key)) is type(original),
            "the guarded native audit worker was forged: " + key,
        )
    require(
        type(controller_pid) is int and controller_pid > 0
        and type(value.get("pid")) is int
        and value["pid"] > 0
        and value["pid"] != controller_pid,
        "the native candidate worker must be genuinely isolated from its controller",
    )
    validate_audit_owners(value["owners"], pins, outer)
    for key, minimum in (
        ("runtime_checks", 20),
        ("owned_graph_checks", 1),
        ("guarded_import_calls", 1),
        ("removed_preexisting_forbidden_module_count", 0),
    ):
        number = value[key]
        require(
            type(number) is int and number >= minimum,
            "the native audit omitted a live ownership guard: " + key,
        )
    if spec.name == "zig":
        require(
            value["trusted_ctypes"] == {
                "source": str(PINNED_CTYPES),
                "source_sha256": PINNED_CTYPES_SHA256,
                "native_module": "_ctypes",
                "native_origin": "built-in",
                "pythonapi_initialized": True,
                "foreign_loads_permitted": False,
            }
            and value["trusted_ctypes_owner"] == outer["trusted_ctypes_owner"],
            "Zig borrowed an ambient, external, or substituted native FFI",
        )
    else:
        require(
            value["trusted_ctypes"] is None
            and value["trusted_ctypes_owner"] is None,
            "Rust or C attempted a foreign native FFI loader",
        )
    return value


def validate_inner_process(value: Any, runtime: Mapping[str, Any], family: str) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {"family", "pid", "returncode", "stdout", "stderr"}
        and value.get("family") == family
        and type(value.get("pid")) is int
        and value["pid"] > 0
        and value["pid"] == runtime.get("pid")
        and type(value.get("returncode")) is int
        and value["returncode"] == 0,
        "the actual isolated candidate worker process was forged",
    )
    stdout = decode_stream(value["stdout"], family + " isolated-worker stdout")
    stderr = decode_stream(value["stderr"], family + " isolated-worker stderr")
    require(
        stdout == canonical(dict(runtime)) and stderr == b"",
        "complete genuine worker process streams do not match their native ownership result",
    )
    return value


def validate_audit_result(
    value: Any,
    pins: OwnerPins,
    outer: Mapping[str, Any],
    controller_pid: int,
) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    expected: dict[str, Any] = {
        "schema": AUDIT_SCHEMA + "-actual-audit",
        "oracle": AUDIT_ORACLE,
        "status": "PASS",
        "python": {
            "implementation": "cpython",
            "version": [3, 14, 6],
            "executable": str(PINNED_PYTHON),
            "sha256": PINNED_PYTHON_SHA256,
        },
        "oracle_source_sha256": pins.audit,
        "family": spec.name,
        "candidate_module": spec.module,
        "manifest": manifest,
        "unchanged_before_after": True,
        "actual_candidate_workers": 1,
        "external_regex_package_count": 0,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
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
        and set(value) == set(expected) | {"ownership", "runtime", "process"},
        "an actual complete frozen V3 ownership audit is mandatory",
    )
    for key, original in expected.items():
        require(
            value.get(key) == original and type(value.get(key)) is type(original),
            "the genuine V3 ownership audit changed: " + key,
        )
    ownership = value["ownership"]
    require(
        type(ownership) is dict
        and set(ownership) == {
            "family", "owners", "adapter", "bridge", "implementation",
            "native", "external_regex_package_count",
            "source_to_binary_reproducibility",
        }
        and ownership.get("family") == spec.name
        and ownership.get("adapter") == expected_adapter(spec)
        and ownership.get("bridge") == expected_bridge(spec)
        and ownership.get("implementation") == expected_implementation(spec)
        and type(ownership.get("external_regex_package_count")) is int
        and ownership["external_regex_package_count"] == 0
        and ownership.get("source_to_binary_reproducibility") == "NOT ESTABLISHED",
        "the exact from-scratch adapter, parser, compiler, bridge, or engine was forged",
    )
    validate_audit_owners(ownership["owners"], pins, outer)
    validate_native(ownership["native"], spec, manifest)
    runtime = validate_runtime(value["runtime"], pins, outer, controller_pid)
    require(
        runtime["owners"] == ownership["owners"],
        "the isolated native worker used a different source or binary closure",
    )
    validate_inner_process(value["process"], runtime, spec.name)
    return value


def validate_controller_failure(value: Any) -> dict[str, Any]:
    required = {
        "schema", "oracle", "status", "error_type", "error",
        "actual_candidate_workers", "clock_samples", "timing_trials_run",
        "workspace_files_written", "evidence_files_created",
        "benchmark_files_read", "hidden_cases_read", "performance",
    }
    require(
        type(value) is dict
        and set(value) in (required, required | {"complete_worker_failure"})
        and value.get("schema") == AUDIT_SCHEMA + "-failure"
        and value.get("oracle") == AUDIT_ORACLE
        and value.get("status") == "FAIL"
        and type(value.get("error_type")) is str
        and bool(value["error_type"])
        and type(value.get("error")) is str
        and bool(value["error"])
        and value.get("performance") == "NOT MEASURED",
        "a genuine failing V3 audit controller result was hidden or forged",
    )
    for key in (
        "actual_candidate_workers", "clock_samples", "timing_trials_run",
        "workspace_files_written", "evidence_files_created",
        "benchmark_files_read", "hidden_cases_read",
    ):
        require(
            type(value.get(key)) is int and value[key] == 0,
            "a failing ownership audit concealed a side effect: " + key,
        )
    if "complete_worker_failure" in value:
        require(
            type(value["complete_worker_failure"]) is dict
            and bool(value["complete_worker_failure"]),
            "a genuine isolated native crash or worker failure was omitted",
        )
    return value


def audit_command(pins: OwnerPins) -> list[str]:
    spec, manifest = validate_pins(pins)
    command = [
        str(PINNED_PYTHON),
        "-I",
        "-B",
        str(ROOT / AUDIT_RELATIVE),
        "--audit",
        "--family",
        spec.name,
        "--oracle-source-sha256",
        pins.audit,
        "--candidate-source-sha256",
        pins.candidate,
        "--native-engine-sha256",
        pins.native_engine,
        "--native-bridge-sha256",
        pins.native_bridge,
    ]
    for relative, digest in manifest["source_sha256"].items():
        command.extend(("--source-pin", relative + "=" + digest))
    for relative, digest in manifest["native_sha256"].items():
        command.extend(("--native-pin", relative + "=" + digest))
    return command


def run_one_audit(pins: OwnerPins) -> dict[str, Any]:
    command = audit_command(pins)
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            cwd=str(ROOT),
            env={
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            },
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {
            "started": False,
            "pid": None,
            "returncode": None,
            "timed_out": False,
            "signal": None,
            "spawn_error": type(error).__qualname__ + ": " + str(error),
            "stdout": b"",
            "stderr": b"",
        }
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=180)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    require(
        type(stdout) is bytes and type(stderr) is bytes,
        "preserve both complete byte streams of the one isolated audit controller",
    )
    code = process.returncode
    require(type(code) is int, "the exact audit controller has no genuine exit status")
    return {
        "started": True,
        "pid": process.pid,
        "returncode": code,
        "timed_out": timed_out,
        "signal": -code if code < 0 else None,
        "spawn_error": None,
        "stdout": stdout,
        "stderr": stderr,
    }


def validate_process_state(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {
            "started", "pid", "returncode", "timed_out", "signal",
            "spawn_error", "stdout", "stderr",
        }
        and type(value.get("started")) is bool
        and type(value.get("timed_out")) is bool
        and type(value.get("stdout")) is bytes
        and type(value.get("stderr")) is bytes
        and len(value["stdout"]) <= MAX_PROCESS_BYTES
        and len(value["stderr"]) <= MAX_PROCESS_BYTES,
        "the complete genuine V3 audit-controller process state was forged",
    )
    if value["started"]:
        require(
            type(value.get("pid")) is int
            and value["pid"] > 0
            and type(value.get("returncode")) is int
            and value.get("spawn_error") is None
            and (
                (value["returncode"] < 0
                 and type(value.get("signal")) is int
                 and value["signal"] == -value["returncode"])
                or (value["returncode"] >= 0 and value.get("signal") is None)
            ),
            "the actual audit controller PID, exit status, or signal was forged",
        )
    else:
        require(
            value.get("pid") is None
            and value.get("returncode") is None
            and value.get("signal") is None
            and value["timed_out"] is False
            and type(value.get("spawn_error")) is str
            and bool(value["spawn_error"])
            and value["stdout"] == b""
            and value["stderr"] == b"",
            "an audit process spawn failure was hidden or substituted",
        )
    return value


def build_complete_report(
    pins: OwnerPins,
    label: str,
    process: Mapping[str, Any],
    before: Mapping[str, Any],
    after: Mapping[str, Any] | None,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    validate_label(label)
    validate_outer_closure(dict(before), pins)
    state = validate_process_state(dict(process))
    stdout = capture_stream(state["stdout"], "V3 audit controller stdout")
    stderr = capture_stream(state["stderr"], "V3 audit controller stderr")
    failures: list[str] = []
    if not state["started"]:
        failures.append("the pinned V3 audit controller could not start: " + state["spawn_error"])
    if state["timed_out"]:
        failures.append("the genuine isolated V3 audit controller exceeded its timeout")
    if state["returncode"] != 0:
        failures.append("the actual V3 audit controller returned a failure or native signal")
    if state["stderr"]:
        failures.append("the complete V3 audit controller emitted diagnostic stderr")
    if post_run_error is not None:
        require(
            type(post_run_error) is str and bool(post_run_error),
            "a genuine post-audit owner failure cannot be suppressed",
        )
        failures.append("post-audit ownership authentication failed: " + post_run_error)
    if after is None:
        failures.append("the complete owned closure was not authenticated after the audit")
    else:
        try:
            validate_outer_closure(dict(after), pins)
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append("the complete post-audit ownership closure is invalid: " + str(error))
        if after != before:
            failures.append("the exact recorder, policies, sources, or binaries changed during the audit")
    decoded: dict[str, Any] | None = None
    if state["stdout"]:
        try:
            decoded = decode_document(state["stdout"], spec.name + " audit controller")
        except RecorderError as error:
            failures.append(str(error))
    else:
        failures.append("the complete genuine V3 audit controller stdout is missing")
    if decoded is not None:
        if decoded.get("status") == "PASS":
            try:
                validate_audit_result(
                    decoded,
                    pins,
                    before,
                    state["pid"] if type(state["pid"]) is int else -1,
                )
            except (RecorderError, TypeError, ValueError, KeyError) as error:
                failures.append("the complete V3 ownership audit was rejected: " + str(error))
        elif decoded.get("status") == "FAIL":
            try:
                validate_controller_failure(decoded)
            except (RecorderError, TypeError, ValueError, KeyError) as error:
                failures.append("genuine V3 failure evidence is incomplete: " + str(error))
            failures.append("the frozen V3 ownership audit reported a genuine failure")
        else:
            failures.append("the complete V3 controller result has no genuine audit status")
    worker_count = 0
    if decoded is not None and type(decoded.get("actual_candidate_workers")) is int:
        worker_count = decoded["actual_candidate_workers"]
    return {
        "schema": SCHEMA + "-complete-report",
        "status": "FAIL" if failures else "PASS",
        "label": label,
        "family": spec.name,
        "candidate_module": spec.module,
        "bridge_module": spec.bridge_module,
        "python": {
            "implementation": "cpython",
            "version": [3, 14, 6],
            "executable": str(PINNED_PYTHON),
            "sha256": PINNED_PYTHON_SHA256,
        },
        "frozen_recorder_relative": SOURCE_RELATIVE,
        "frozen_recorder_sha256": pins.recorder,
        "frozen_audit_relative": AUDIT_RELATIVE,
        "frozen_audit_sha256": pins.audit,
        "immutable_policy_sha256": dict(IMMUTABLE_POLICY_ITEMS),
        "manifest": manifest,
        "complete_artifacts_before": dict(before),
        "complete_artifacts_after": dict(after) if after is not None else None,
        "unchanged_before_after": after is not None and after == before,
        "complete_process_stdout": stdout,
        "complete_process_stderr": stderr,
        "actual_audit_process_started": state["started"],
        "actual_audit_process_count": 1 if state["started"] else 0,
        "actual_audit_process_pid": state["pid"],
        "actual_audit_process_returncode": state["returncode"],
        "actual_audit_process_signal": state["signal"],
        "actual_audit_process_timed_out": state["timed_out"],
        "actual_audit_process_spawn_error": state["spawn_error"],
        "actual_candidate_workers": worker_count,
        "complete_frozen_audit_result": decoded,
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written_before_publication": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def validate_publication(
    value: Any, relative: str, raw: bytes,
) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {
            "path", "sha256", "bytes", "actual_write_calls",
            "atomic_no_overwrite_link_completed", "file_fsync_completed",
            "directory_fsync_completed", "owned_temporary_removed",
            "complete_readback_verified",
        }
        and value.get("path") == relative
        and value.get("sha256") == hashlib.sha256(raw).hexdigest()
        and type(value.get("bytes")) is int
        and value["bytes"] == len(raw)
        and type(value.get("actual_write_calls")) is int
        and value["actual_write_calls"] > 0,
        "a complete durable no-clobber V3 audit publication was forged",
    )
    for key in (
        "atomic_no_overwrite_link_completed", "file_fsync_completed",
        "directory_fsync_completed", "owned_temporary_removed",
        "complete_readback_verified",
    ):
        require(value.get(key) is True, "a durable audit publication guard was omitted: " + key)
    return value


def build_receipt(
    pins: OwnerPins,
    label: str,
    report: Mapping[str, Any],
    report_publication: Mapping[str, Any],
) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    report_relative, receipt_relative = approved_paths(spec.name, label)
    report_raw = canonical(dict(report))
    validate_publication(report_publication, report_relative, report_raw)
    require(
        report.get("schema") == SCHEMA + "-complete-report"
        and report.get("family") == spec.name
        and report.get("label") == label
        and report.get("status") in ("PASS", "FAIL"),
        "a receipt must link the exact complete V3 audit result",
    )
    return {
        "schema": SCHEMA + "-publication-receipt",
        "publication_status": "PASS",
        "audit_status": report["status"],
        "family": spec.name,
        "label": label,
        "candidate_module": spec.module,
        "frozen_recorder_relative": SOURCE_RELATIVE,
        "frozen_recorder_sha256": pins.recorder,
        "frozen_audit_relative": AUDIT_RELATIVE,
        "frozen_audit_sha256": pins.audit,
        "immutable_policy_sha256": dict(IMMUTABLE_POLICY_ITEMS),
        "manifest": manifest,
        "report_publication": dict(report_publication),
        "receipt_relative": receipt_relative,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_candidate": True,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def validate_receipt(
    value: Any,
    pins: OwnerPins,
    label: str,
    report: Mapping[str, Any],
) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    report_relative, receipt_relative = approved_paths(spec.name, label)
    expected = {
        "schema": SCHEMA + "-publication-receipt",
        "publication_status": "PASS",
        "audit_status": report.get("status"),
        "family": spec.name,
        "label": label,
        "candidate_module": spec.module,
        "frozen_recorder_relative": SOURCE_RELATIVE,
        "frozen_recorder_sha256": pins.recorder,
        "frozen_audit_relative": AUDIT_RELATIVE,
        "frozen_audit_sha256": pins.audit,
        "immutable_policy_sha256": dict(IMMUTABLE_POLICY_ITEMS),
        "manifest": manifest,
        "receipt_relative": receipt_relative,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_candidate": True,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(
        type(value) is dict and set(value) == set(expected) | {"report_publication"},
        "a complete genuine V3 audit publication receipt is mandatory",
    )
    for key, original in expected.items():
        require(
            value.get(key) == original and type(value.get(key)) is type(original),
            "the audit receipt was forged or mislabeled: " + key,
        )
    validate_publication(value["report_publication"], report_relative, canonical(dict(report)))
    return value


def record_audit(pins: OwnerPins, label: str) -> dict[str, Any]:
    verify_runtime()
    spec, manifest = validate_pins(pins)
    validate_label(label)
    before = authenticate_closure(pins)
    with preflight_fresh_outputs(spec.name, label) as preflight:
        retained_directory(preflight)
        process = run_one_audit(pins)
        retained_directory(preflight)
        after: dict[str, Any] | None = None
        post_run_error: str | None = None
        try:
            after = authenticate_closure(pins)
        except (RecorderError, OSError, TypeError, ValueError) as error:
            post_run_error = type(error).__qualname__ + ": " + str(error)
        report = build_complete_report(pins, label, process, before, after, post_run_error)
        report_publication = publish_atomic(preflight, report, "report")
        validate_publication(
            report_publication, preflight["report_relative"], canonical(report),
        )
        receipt = build_receipt(pins, label, report, report_publication)
        validate_receipt(receipt, pins, label, report)
        receipt_publication = publish_atomic(preflight, receipt, "receipt")
        validate_publication(
            receipt_publication, preflight["receipt_relative"], canonical(receipt),
        )
    verify_runtime()
    return {
        "schema": SCHEMA + "-recorded",
        "status": report["status"],
        "publication_status": "PASS",
        "family": spec.name,
        "label": label,
        "frozen_recorder_relative": SOURCE_RELATIVE,
        "frozen_recorder_sha256": pins.recorder,
        "frozen_audit_relative": AUDIT_RELATIVE,
        "frozen_audit_sha256": pins.audit,
        "immutable_policy_sha256": dict(IMMUTABLE_POLICY_ITEMS),
        "manifest": manifest,
        "report_publication": report_publication,
        "receipt_publication": receipt_publication,
        "actual_audit_process_count": report["actual_audit_process_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "all_failure_reasons": report["all_failure_reasons"],
        "failure_count": report["failure_count"],
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    blocked = {
        "file_reads": 0,
        "file_writes": 0,
        "candidate_imports": 0,
        "dynamic_imports": 0,
        "processes": 0,
        "threads": 0,
        "clocks": 0,
        "randomness": 0,
        "garbage_collections": 0,
    }
    installed: list[tuple[Any, str, Any]] = []

    def deny(key: str, message: str) -> Callable[..., Any]:
        def fail(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            blocked[key] += 1
            raise SourceOnlyError(message)

        return fail

    def install(owner: Any, name: str, replacement: Any) -> None:
        original = getattr(owner, name, None)
        if original is not None:
            installed.append((owner, name, original))
            setattr(owner, name, replacement)

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (os, "fstat"), (os, "listdir"),
            (os, "scandir"), (Path, "open"), (Path, "read_bytes"),
            (Path, "read_text"), (Path, "stat"), (Path, "lstat"),
            (Path, "iterdir"),
        ):
            install(owner, name, deny("file_reads", "a synthetic audit cannot read files"))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "replace"), (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (os, "link"), (os, "symlink"), (Path, "write_bytes"),
            (Path, "write_text"), (Path, "unlink"), (Path, "mkdir"),
            (Path, "rename"), (Path, "replace"), (Path, "touch"),
        ):
            install(owner, name, deny("file_writes", "a synthetic audit cannot write files"))
        install(
            builtins,
            "__import__",
            deny("candidate_imports", "a synthetic audit cannot import any candidate"),
        )
        install(
            importlib,
            "import_module",
            deny("dynamic_imports", "a synthetic audit cannot dynamically import an engine"),
        )
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(
                subprocess,
                name,
                deny("processes", "a synthetic audit cannot start any process"),
            )
        for name in ("system", "fork", "posix_spawn", "posix_spawnp", "popen"):
            install(os, name, deny("processes", "a synthetic audit cannot delegate a process"))
        install(
            threading.Thread,
            "start",
            deny("threads", "a synthetic audit cannot start a background worker"),
        )
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time", "process_time_ns",
            "thread_time", "thread_time_ns",
        ):
            install(time, name, deny("clocks", "a synthetic audit cannot measure performance"))
        install(os, "urandom", deny("randomness", "a synthetic audit cannot consume OS randomness"))
        install(gc, "collect", deny("garbage_collections", "a synthetic audit cannot collect garbage"))
        yield blocked
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_digest(label: str) -> str:
    require(type(label) is str and bool(label), "a complete synthetic pin label is required")
    return hashlib.sha256(("rebar-v3-audit-recorder:" + label).encode("ascii")).hexdigest()


def synthetic_pins(spec: FamilySpec) -> OwnerPins:
    source_values = {
        relative: synthetic_digest(spec.name + ":source:" + relative)
        for relative in spec.sources
    }
    binary_values = {
        relative: synthetic_digest(spec.name + ":native:" + relative)
        for relative in spec.binaries
    }
    return OwnerPins(
        family=spec.name,
        recorder=synthetic_digest("recorder"),
        audit=AUDIT_SHA256,
        candidate=source_values[spec.adapter],
        native_engine=binary_values[spec.engine],
        native_bridge=binary_values[spec.bridge],
        source_entries=tuple(
            relative + "=" + source_values[relative]
            for relative in spec.sources
        ),
        native_entries=tuple(
            relative + "=" + binary_values[relative]
            for relative in spec.binaries
        ),
    )


def synthetic_owner(relative: str, digest: str, inode: int) -> dict[str, Any]:
    return {
        "relative": relative,
        "sha256": digest,
        "bytes": 131,
        "device": 7,
        "inode": inode,
    }


def synthetic_external(absolute: Path, digest: str, inode: int) -> dict[str, Any]:
    return {
        "path": str(absolute),
        "sha256": digest,
        "bytes": 197,
        "device": 11,
        "inode": inode,
    }


def synthetic_closure(pins: OwnerPins) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    next_inode = 100

    def owner(relative: str, digest: str) -> dict[str, Any]:
        nonlocal next_inode
        next_inode += 1
        return synthetic_owner(relative, digest, next_inode)

    result = {
        "family": spec.name,
        "manifest": manifest,
        "recorder_owner": owner(SOURCE_RELATIVE, pins.recorder),
        "audit_owner": owner(AUDIT_RELATIVE, pins.audit),
        "policy_owners": {
            relative: owner(relative, digest)
            for relative, digest in IMMUTABLE_POLICY_ITEMS
        },
        "source_owners": {
            relative: owner(relative, digest)
            for relative, digest in manifest["source_sha256"].items()
        },
        "native_owners": {
            relative: owner(relative, digest)
            for relative, digest in manifest["native_sha256"].items()
        },
        "python_owner": synthetic_external(
            PINNED_PYTHON, PINNED_PYTHON_SHA256, 801,
        ),
        "trusted_ctypes_owner": (
            synthetic_external(PINNED_CTYPES, PINNED_CTYPES_SHA256, 802)
            if spec.name == "zig" else None
        ),
    }
    return validate_outer_closure(result, pins)


def synthetic_audit_owners(
    pins: OwnerPins, closure: Mapping[str, Any],
) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    result = {
        "family": spec.name,
        "manifest": manifest,
        "source_owners": copy.deepcopy(closure["source_owners"]),
        "native_owners": copy.deepcopy(closure["native_owners"]),
        "policy_owners": copy.deepcopy(closure["policy_owners"]),
        "oracle_owner": copy.deepcopy(closure["audit_owner"]),
        "python_owner": copy.deepcopy(closure["python_owner"]),
    }
    return validate_audit_owners(result, pins, closure)


def synthetic_native(spec: FamilySpec) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for binary in spec.binaries:
        needed, runpaths = expected_dynamic(spec, binary)
        if spec.name == "rust" and binary == spec.bridge:
            references = sorted(RUST_REQUIRED_BRIDGE_REFERENCES)
            count = 143
        elif spec.name == "zig" and binary == spec.bridge:
            references = sorted(ZIG_BRIDGE_REFERENCES)
            count = 124
        elif spec.name == "rust":
            references = []
            count = 53
        elif spec.name == "zig":
            references = []
            count = 17
        else:
            references = []
            count = 130
        result[binary] = {
            "needed": needed,
            "runpaths": runpaths,
            "defined_exports": expected_exports(spec, binary),
            "undefined_symbol_count": count,
            "owned_engine_references": references,
        }
    return result


def synthetic_audit(
    pins: OwnerPins, closure: Mapping[str, Any], controller_pid: int,
) -> dict[str, Any]:
    spec, manifest = validate_pins(pins)
    owners = synthetic_audit_owners(pins, closure)
    worker_pid = controller_pid + 10_000
    runtime = {
        "schema": AUDIT_SCHEMA + "-isolated-worker",
        "status": "PASS",
        "family": spec.name,
        "pid": worker_pid,
        "oracle_source_sha256": pins.audit,
        "manifest": manifest,
        "owners": copy.deepcopy(owners),
        "runtime_checks": 24,
        "owned_graph_checks": 3,
        "guarded_import_calls": 4,
        "forbidden_import_or_execution_count": 0,
        "removed_preexisting_forbidden_module_count": 2,
        "caller_replacement_callback_supported": True,
        "owned_public_re_names_supported": True,
        "owned_public_sre_scanner_name_supported": True,
        "actual_standard_library_engine_loaded": False,
        "candidate_modules": sorted((spec.module, spec.bridge_module)),
        "owned_ctypes_library_load_count": 1 if spec.name == "zig" else 0,
        "owned_ctypes_symbols": sorted(ZIG_CTYPES_SYMBOLS) if spec.name == "zig" else [],
        "trusted_ctypes": (
            {
                "source": str(PINNED_CTYPES),
                "source_sha256": PINNED_CTYPES_SHA256,
                "native_module": "_ctypes",
                "native_origin": "built-in",
                "pythonapi_initialized": True,
                "foreign_loads_permitted": False,
            }
            if spec.name == "zig" else None
        ),
        "trusted_ctypes_owner": copy.deepcopy(closure["trusted_ctypes_owner"]),
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
    validate_runtime(runtime, pins, closure, controller_pid)
    process = {
        "family": spec.name,
        "pid": worker_pid,
        "returncode": 0,
        "stdout": capture_stream(canonical(runtime), spec.name + " synthetic worker stdout"),
        "stderr": capture_stream(b"", spec.name + " synthetic worker stderr"),
    }
    result = {
        "schema": AUDIT_SCHEMA + "-actual-audit",
        "oracle": AUDIT_ORACLE,
        "status": "PASS",
        "python": {
            "implementation": "cpython",
            "version": [3, 14, 6],
            "executable": str(PINNED_PYTHON),
            "sha256": PINNED_PYTHON_SHA256,
        },
        "oracle_source_sha256": pins.audit,
        "family": spec.name,
        "candidate_module": spec.module,
        "manifest": manifest,
        "ownership": {
            "family": spec.name,
            "owners": copy.deepcopy(owners),
            "adapter": expected_adapter(spec),
            "bridge": expected_bridge(spec),
            "implementation": expected_implementation(spec),
            "native": synthetic_native(spec),
            "external_regex_package_count": 0,
            "source_to_binary_reproducibility": "NOT ESTABLISHED",
        },
        "runtime": runtime,
        "process": process,
        "unchanged_before_after": True,
        "actual_candidate_workers": 1,
        "external_regex_package_count": 0,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
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
    return validate_audit_result(result, pins, closure, controller_pid)


def synthetic_publication(relative: str, document: Mapping[str, Any]) -> dict[str, Any]:
    raw = canonical(dict(document))
    result = {
        "path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "actual_write_calls": 1,
        "atomic_no_overwrite_link_completed": True,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "owned_temporary_removed": True,
        "complete_readback_verified": True,
    }
    return validate_publication(result, relative, raw)


def synthetic_failure(spec: FamilySpec) -> dict[str, Any]:
    del spec
    return {
        "schema": AUDIT_SCHEMA + "-failure",
        "oracle": AUDIT_ORACLE,
        "status": "FAIL",
        "error_type": "WorkerFailure",
        "error": "synthetic genuine independent ownership mismatch",
        "complete_worker_failure": {
            "family": "synthetic",
            "error_type": "AuditFailure",
            "error": "the actual isolated source owner was rejected",
        },
        "actual_candidate_workers": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime(synthetic=True)
    accepted: list[str] = []
    rejected: list[str] = []
    with source_only_boundary() as blocked:

        def accept(label: str, value: Any) -> None:
            require(value, "synthetic source-only positive control failed: " + label)
            accepted.append(label)

        def reject(label: str, operation: Callable[[], Any]) -> None:
            try:
                operation()
            except (RecorderError, OSError, ValueError, TypeError, KeyError, IndexError):
                rejected.append(label)
                return
            raise RecorderError("synthetic forged ownership evidence was accepted: " + label)

        for index, spec in enumerate(FAMILY_SPECS.values(), start=1):
            pins = synthetic_pins(spec)
            checked_spec, manifest = validate_pins(pins)
            closure = synthetic_closure(pins)
            controller_pid = 700 + index
            audit = synthetic_audit(pins, closure, controller_pid)
            raw = canonical(audit)
            process = {
                "started": True,
                "pid": controller_pid,
                "returncode": 0,
                "timed_out": False,
                "signal": None,
                "spawn_error": None,
                "stdout": raw,
                "stderr": b"",
            }
            report = build_complete_report(
                pins, "synthetic-proof", process, closure, copy.deepcopy(closure),
            )
            report_path, receipt_path = approved_paths(spec.name, "synthetic-proof")
            publication = synthetic_publication(report_path, report)
            receipt = build_receipt(pins, "synthetic-proof", report, publication)

            accept(spec.name + "-complete-dynamic-family-manifest", checked_spec is spec)
            accept(
                spec.name + "-complete-source-and-native-closure",
                len(manifest["source_sha256"]) == len(spec.sources)
                and len(manifest["native_sha256"]) == len(spec.binaries),
            )
            accept(
                spec.name + "-only-c-native-engine-bridge-alias",
                (pins.native_engine == pins.native_bridge) is (spec.name == "c"),
            )
            accept(
                spec.name + "-frozen-immutable-v2-and-v5-policies",
                manifest["immutable_policy_sha256"] == dict(IMMUTABLE_POLICY_ITEMS),
            )
            accept(
                spec.name + "-complete-synthetic-owned-artifact-identities",
                validate_outer_closure(closure, pins) is closure,
            )
            accept(
                spec.name + "-complete-canonical-audit-controller",
                decode_document(raw, spec.name) == audit,
            )
            accept(
                spec.name + "-complete-isolated-native-audit",
                validate_audit_result(audit, pins, closure, controller_pid) is audit,
            )
            accept(
                spec.name + "-genuinely-distinct-controller-and-worker-pids",
                audit["runtime"]["pid"] != controller_pid,
            )
            accept(
                spec.name + "-complete-reversible-isolated-worker-stdout",
                decode_stream(audit["process"]["stdout"], spec.name)
                == canonical(audit["runtime"]),
            )
            accept(
                spec.name + "-complete-empty-isolated-worker-stderr",
                decode_stream(audit["process"]["stderr"], spec.name) == b"",
            )
            accept(
                spec.name + "-complete-passing-report",
                report["status"] == "PASS"
                and report["failure_count"] == 0
                and report["all_failure_reasons"] == []
                and report["actual_audit_process_count"] == 1
                and report["actual_candidate_workers"] == 1
                and report["complete_frozen_audit_result"] == audit
                and decode_stream(report["complete_process_stdout"], spec.name) == raw
                and decode_stream(report["complete_process_stderr"], spec.name) == b"",
            )
            accept(
                spec.name + "-exactly-two-independent-fresh-output-names",
                report_path.startswith(APPROVED_DIRECTORY + "/" + spec.name + "-")
                and receipt_path.startswith(APPROVED_DIRECTORY + "/" + spec.name + "-")
                and report_path != receipt_path,
            )
            accept(
                spec.name + "-complete-durable-publication-metadata",
                validate_publication(publication, report_path, canonical(report)) is publication,
            )
            accept(
                spec.name + "-complete-authenticated-publication-receipt",
                validate_receipt(receipt, pins, "synthetic-proof", report) is receipt,
            )
            command = audit_command(pins)
            accept(
                spec.name + "-exact-one-explicit-pinned-v3-audit-command",
                command[:7] == [
                    str(PINNED_PYTHON), "-I", "-B", str(ROOT / AUDIT_RELATIVE),
                    "--audit", "--family", spec.name,
                ]
                and command.count("--audit") == 1
                and command.count("--source-pin") == len(spec.sources)
                and command.count("--native-pin") == len(spec.binaries),
            )

            failed_audit = synthetic_failure(spec)
            failed_raw = canonical(failed_audit)
            failed_process = {
                **process,
                "returncode": 1,
                "stdout": failed_raw,
                "stderr": b"synthetic complete native ownership failure\n",
            }
            failed_report = build_complete_report(
                pins, "synthetic-proof", failed_process, closure, copy.deepcopy(closure),
            )
            failed_publication = synthetic_publication(report_path, failed_report)
            failed_receipt = build_receipt(
                pins, "synthetic-proof", failed_report, failed_publication,
            )
            accept(
                spec.name + "-preserve-complete-genuine-failing-audit",
                failed_report["status"] == "FAIL"
                and failed_report["failure_count"] >= 3
                and failed_report["complete_frozen_audit_result"] == failed_audit
                and decode_stream(failed_report["complete_process_stdout"], spec.name)
                == failed_raw
                and decode_stream(failed_report["complete_process_stderr"], spec.name)
                == failed_process["stderr"],
            )
            accept(
                spec.name + "-publication-success-never-becomes-audit-success",
                validate_receipt(
                    failed_receipt, pins, "synthetic-proof", failed_report,
                ) is failed_receipt
                and failed_receipt["publication_status"] == "PASS"
                and failed_receipt["audit_status"] == "FAIL",
            )

            crash_process = {
                **process,
                "returncode": -11,
                "signal": 11,
                "stdout": b"synthetic native signal before complete JSON\n",
                "stderr": b"synthetic complete native crash traceback\n",
            }
            crash_report = build_complete_report(
                pins, "synthetic-proof", crash_process, closure, copy.deepcopy(closure),
            )
            accept(
                spec.name + "-preserve-complete-native-crash-and-signal",
                crash_report["status"] == "FAIL"
                and crash_report["actual_audit_process_signal"] == 11
                and crash_report["actual_audit_process_returncode"] == -11
                and crash_report["complete_frozen_audit_result"] is None
                and decode_stream(crash_report["complete_process_stdout"], spec.name)
                == crash_process["stdout"]
                and decode_stream(crash_report["complete_process_stderr"], spec.name)
                == crash_process["stderr"],
            )
            timeout_process = {
                **crash_process,
                "returncode": -9,
                "signal": 9,
                "timed_out": True,
            }
            timeout_report = build_complete_report(
                pins, "synthetic-proof", timeout_process, closure, copy.deepcopy(closure),
            )
            accept(
                spec.name + "-preserve-complete-native-timeout",
                timeout_report["status"] == "FAIL"
                and timeout_report["actual_audit_process_timed_out"] is True
                and timeout_report["actual_audit_process_signal"] == 9,
            )
            unstarted_process = {
                "started": False,
                "pid": None,
                "returncode": None,
                "timed_out": False,
                "signal": None,
                "spawn_error": "synthetic frozen interpreter cannot start",
                "stdout": b"",
                "stderr": b"",
            }
            unstarted_report = build_complete_report(
                pins, "synthetic-proof", unstarted_process, closure, copy.deepcopy(closure),
            )
            accept(
                spec.name + "-preserve-complete-controller-spawn-failure",
                unstarted_report["status"] == "FAIL"
                and unstarted_report["actual_audit_process_count"] == 0
                and unstarted_report["actual_audit_process_started"] is False
                and unstarted_report["actual_audit_process_spawn_error"]
                == unstarted_process["spawn_error"],
            )
            changed = copy.deepcopy(closure)
            changed["source_owners"][spec.adapter]["inode"] += 1
            changed_report = build_complete_report(
                pins, "synthetic-proof", process, closure, changed,
            )
            accept(
                spec.name + "-reject-genuine-post-audit-owner-substitution",
                changed_report["status"] == "FAIL"
                and changed_report["unchanged_before_after"] is False
                and changed_report["complete_frozen_audit_result"] == audit,
            )

            for field in (
                "schema", "oracle", "status", "python", "oracle_source_sha256",
                "family", "candidate_module", "manifest", "ownership", "runtime",
                "process", "unchanged_before_after", "actual_candidate_workers",
                "external_regex_package_count", "source_to_binary_reproducibility",
                "clock_samples", "timing_trials_run", "workspace_files_written",
                "evidence_files_created", "benchmark_files_read", "hidden_cases_read",
                "performance", "candidate_qualified_for_hidden_benchmark",
                "final_winner_selected",
            ):
                broken = copy.deepcopy(audit)
                del broken[field]
                reject(
                    spec.name + "-reject-missing-audit-" + field,
                    lambda broken=broken: validate_audit_result(
                        broken, pins, closure, controller_pid,
                    ),
                )

            poisons: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
                ("wrong-family", lambda item: item.__setitem__("family", "external")),
                ("borrowed-candidate", lambda item: item.__setitem__("candidate_module", "re")),
                ("stale-audit-pin", lambda item: item.__setitem__("oracle_source_sha256", IMMUTABLE_POLICY_ITEMS[0][1])),
                ("forged-python-version", lambda item: item["python"].__setitem__("version", [3, 14, 7])),
                ("forged-python-binary", lambda item: item["python"].__setitem__("sha256", synthetic_digest("foreign-python"))),
                ("forged-immutable-policy", lambda item: item["manifest"]["immutable_policy_sha256"].__setitem__(IMMUTABLE_POLICY_ITEMS[1][0], synthetic_digest("foreign-policy"))),
                ("missing-owned-source", lambda item: item["manifest"]["source_sha256"].pop(spec.adapter)),
                ("foreign-owned-source", lambda item: item["ownership"]["owners"]["source_owners"][spec.adapter].__setitem__("sha256", synthetic_digest("foreign-source"))),
                ("missing-owned-native", lambda item: item["manifest"]["native_sha256"].pop(spec.engine)),
                ("foreign-owned-native", lambda item: item["ownership"]["owners"]["native_owners"][spec.engine].__setitem__("sha256", synthetic_digest("foreign-native"))),
                ("forged-source-inode", lambda item: item["ownership"]["owners"]["source_owners"][spec.adapter].__setitem__("inode", True)),
                ("zero-source-inode", lambda item: item["ownership"]["owners"]["source_owners"][spec.adapter].__setitem__("inode", 0)),
                ("foreign-parser-adapter", lambda item: item["ownership"].__setitem__("adapter", {})),
                ("foreign-native-bridge", lambda item: item["ownership"].__setitem__("bridge", {})),
                ("foreign-implementation", lambda item: item["ownership"].__setitem__("implementation", {"engine": "pcre2"})),
                ("external-regex-package", lambda item: item["ownership"].__setitem__("external_regex_package_count", 1)),
                ("boolean-external-package-count", lambda item: item["ownership"].__setitem__("external_regex_package_count", False)),
                ("false-source-build-reproducibility", lambda item: item.__setitem__("source_to_binary_reproducibility", "ESTABLISHED")),
                ("false-native-build-reproducibility", lambda item: item["ownership"].__setitem__("source_to_binary_reproducibility", "ESTABLISHED")),
                ("hidden-holdout", lambda item: item.__setitem__("hidden_cases_read", 1)),
                ("hidden-benchmark", lambda item: item.__setitem__("benchmark_files_read", 1)),
                ("timing-trial", lambda item: item.__setitem__("timing_trials_run", 1)),
                ("performance-claim", lambda item: item.__setitem__("performance", "FASTER")),
                ("premature-qualification", lambda item: item.__setitem__("candidate_qualified_for_hidden_benchmark", True)),
                ("premature-winner", lambda item: item.__setitem__("final_winner_selected", True)),
                ("changed-owner-closure", lambda item: item.__setitem__("unchanged_before_after", False)),
                ("boolean-worker-counter", lambda item: item.__setitem__("actual_candidate_workers", True)),
                ("runtime-standard-engine", lambda item: item["runtime"].__setitem__("actual_standard_library_engine_loaded", True)),
                ("runtime-sibling-candidate", lambda item: item["runtime"].__setitem__("candidate_modules", ["candidates.external"])),
                ("runtime-forbidden-import", lambda item: item["runtime"].__setitem__("forbidden_import_or_execution_count", 1)),
                ("runtime-no-callback", lambda item: item["runtime"].__setitem__("caller_replacement_callback_supported", False)),
                ("runtime-no-owned-type", lambda item: item["runtime"].__setitem__("owned_public_re_names_supported", False)),
                ("runtime-no-owned-scanner", lambda item: item["runtime"].__setitem__("owned_public_sre_scanner_name_supported", False)),
                ("runtime-too-few-checks", lambda item: item["runtime"].__setitem__("runtime_checks", 19)),
                ("runtime-missing-object-graph", lambda item: item["runtime"].__setitem__("owned_graph_checks", 0)),
                ("runtime-missing-import-guard", lambda item: item["runtime"].__setitem__("guarded_import_calls", 0)),
                ("runtime-controller-pid-alias", lambda item: item["runtime"].__setitem__("pid", controller_pid)),
                ("runtime-zero-pid", lambda item: item["runtime"].__setitem__("pid", 0)),
                ("runtime-boolean-pid", lambda item: item["runtime"].__setitem__("pid", True)),
                ("runtime-foreign-ffi-load", lambda item: item["runtime"].__setitem__("owned_ctypes_library_load_count", 2)),
                ("runtime-foreign-ffi-symbol", lambda item: item["runtime"].__setitem__("owned_ctypes_symbols", ["regexec"])),
                ("runtime-foreign-owner-graph", lambda item: item["runtime"]["owners"].__setitem__("family", "foreign")),
                ("process-wrong-pid", lambda item: item["process"].__setitem__("pid", 1)),
                ("process-failing-exit", lambda item: item["process"].__setitem__("returncode", 1)),
                ("process-boolean-exit", lambda item: item["process"].__setitem__("returncode", False)),
                ("process-incomplete-stdout", lambda item: item["process"]["stdout"].__setitem__("complete", False)),
                ("process-foreign-stdout-hash", lambda item: item["process"]["stdout"].__setitem__("sha256", synthetic_digest("forged-stdout"))),
                ("process-hidden-stderr", lambda item: item["process"].__setitem__("stderr", capture_stream(b"hidden stderr", "synthetic"))),
                ("native-missing-elf", lambda item: item["ownership"]["native"].pop(spec.engine)),
                ("native-foreign-library", lambda item: item["ownership"]["native"][spec.engine].__setitem__("needed", ["libpcre2.so"])),
                ("native-foreign-runpath", lambda item: item["ownership"]["native"][spec.engine].__setitem__("runpaths", ["/external"])),
                ("native-foreign-export", lambda item: item["ownership"]["native"][spec.engine].__setitem__("defined_exports", ["regexec"])),
                ("native-hidden-symbols", lambda item: item["ownership"]["native"][spec.engine].__setitem__("undefined_symbol_count", 0)),
                ("native-boolean-symbol-count", lambda item: item["ownership"]["native"][spec.engine].__setitem__("undefined_symbol_count", True)),
                ("native-foreign-reference", lambda item: item["ownership"]["native"][spec.engine].__setitem__("owned_engine_references", ["regexec"])),
                ("extra-audit-field", lambda item: item.__setitem__("concealed_external_engine", True)),
            )
            for title, change in poisons:
                broken = copy.deepcopy(audit)
                change(broken)
                reject(
                    spec.name + "-reject-" + title,
                    lambda broken=broken: validate_audit_result(
                        broken, pins, closure, controller_pid,
                    ),
                )

            for relative in spec.sources:
                broken = copy.deepcopy(closure)
                broken["source_owners"].pop(relative)
                reject(
                    spec.name + "-reject-missing-owned-source-" + relative,
                    lambda broken=broken: validate_outer_closure(broken, pins),
                )
            for relative in spec.binaries:
                broken = copy.deepcopy(closure)
                broken["native_owners"].pop(relative)
                reject(
                    spec.name + "-reject-missing-owned-native-" + relative,
                    lambda broken=broken: validate_outer_closure(broken, pins),
                )
            for relative, _ in IMMUTABLE_POLICY_ITEMS:
                broken = copy.deepcopy(closure)
                broken["policy_owners"].pop(relative)
                reject(
                    spec.name + "-reject-missing-immutable-policy-" + relative,
                    lambda broken=broken: validate_outer_closure(broken, pins),
                )
            for other in FAMILY_SPECS.values():
                if other.name != spec.name:
                    foreign_pins = synthetic_pins(other)
                    foreign_closure = synthetic_closure(foreign_pins)
                    foreign_audit = synthetic_audit(foreign_pins, foreign_closure, 900 + index)
                    reject(
                        spec.name + "-reject-borrowed-" + other.name + "-engine",
                        lambda foreign_audit=foreign_audit: validate_audit_result(
                            foreign_audit, pins, closure, controller_pid,
                        ),
                    )

            for title, forged in (
                ("truncated", raw[:-1]),
                ("hidden-suffix", raw + b"{}\n"),
                ("noncanonical-whitespace", b" " + raw),
                ("duplicate-field", b'{"status":"PASS","status":"FAIL"}\n'),
                ("nonfinite", b'{"external_regex_package_count":NaN}\n'),
            ):
                reject(
                    spec.name + "-reject-" + title + "-controller-stdout",
                    lambda forged=forged: decode_document(forged, spec.name),
                )

            for title, change in (
                ("foreign-audit-status", lambda item: item.__setitem__("audit_status", "PASS")),
                ("foreign-report-hash", lambda item: item["report_publication"].__setitem__("sha256", synthetic_digest("wrong-report"))),
                ("omitted-report", lambda item: item.pop("report_publication")),
                ("foreign-receipt-path", lambda item: item.__setitem__("receipt_relative", "experiments/escape.json")),
                ("forgotten-fsync", lambda item: item["report_publication"].__setitem__("directory_fsync_completed", False)),
                ("forgotten-readback", lambda item: item["report_publication"].__setitem__("complete_readback_verified", False)),
                ("clobberable-link", lambda item: item["report_publication"].__setitem__("atomic_no_overwrite_link_completed", False)),
                ("forged-policy", lambda item: item["immutable_policy_sha256"].__setitem__(IMMUTABLE_POLICY_ITEMS[0][0], synthetic_digest("receipt-policy"))),
                ("publication-as-audit-success", lambda item: item.__setitem__("audit_status", "PASS")),
            ):
                document = copy.deepcopy(failed_receipt)
                change(document)
                reject(
                    spec.name + "-reject-" + title + "-receipt",
                    lambda document=document: validate_receipt(
                        document, pins, "synthetic-proof", failed_report,
                    ),
                )

            reject(
                spec.name + "-reject-duplicate-source-pin",
                lambda pins=pins: validate_pins(
                    OwnerPins(
                        pins.family, pins.recorder, pins.audit, pins.candidate,
                        pins.native_engine, pins.native_bridge,
                        pins.source_entries + (pins.source_entries[0],),
                        pins.native_entries,
                    ),
                ),
            )
            reject(
                spec.name + "-reject-duplicate-native-pin",
                lambda pins=pins: validate_pins(
                    OwnerPins(
                        pins.family, pins.recorder, pins.audit, pins.candidate,
                        pins.native_engine, pins.native_bridge,
                        pins.source_entries,
                        pins.native_entries + (pins.native_entries[0],),
                    ),
                ),
            )
            reject(
                spec.name + "-reject-stale-v2-audit-pin",
                lambda pins=pins: validate_pins(
                    OwnerPins(
                        pins.family, pins.recorder, IMMUTABLE_POLICY_ITEMS[0][1],
                        pins.candidate, pins.native_engine, pins.native_bridge,
                        pins.source_entries, pins.native_entries,
                    ),
                ),
            )

        accept(
            "all-three-genuinely-independent-native-families",
            set(FAMILY_SPECS) == {"rust", "c", "zig"},
        )
        accept(
            "literal-retained-evidence-directory-identity",
            require_directory_identity((7, 113), (7, 113), (7, 113)) is None,
        )
        for title, retained, expected, literal in (
            ("renamed-literal", (7, 113), (7, 113), (7, 114)),
            ("replaced-device", (7, 113), (7, 113), (8, 113)),
            ("replaced-retained", (7, 114), (7, 113), (7, 114)),
            ("forged-expected", (7, 113), (8, 113), (7, 113)),
            ("truncated-literal", (7, 113), (7, 113), (7,)),
            ("boolean-literal", (7, 113), (7, 113), (True, 113)),
            ("negative-literal", (7, 113), (7, 113), (-1, 113)),
        ):
            reject(
                "reject-" + title + "-evidence-directory",
                lambda retained=retained, expected=expected, literal=literal:
                    require_directory_identity(retained, expected, literal),
            )
        for label in (
            "", ".", "..", "../escape", "/absolute", "a/b", "a\\b",
            "a--b", "-bad", "bad-", "bad_name", "UPPER", "a" * 65,
        ):
            reject(
                "reject-unsafe-output-label-" + repr(label),
                lambda label=label: approved_paths("rust", label),
            )
        for name in ("", "re", "_sre", "../zig", "external", "RUST", "regex"):
            reject(
                "reject-external-family-" + repr(name),
                lambda name=name: family_spec(name),
            )
        for relative in (
            "", ".", "..", "/absolute", "../candidate", "a//b",
            "a/../b", "a/./b", "a\\b", "a\x00b",
        ):
            reject(
                "reject-escaping-owned-path-" + repr(relative),
                lambda relative=relative: safe_parts(relative),
            )
        for title, operation in (
            ("direct-file-read", lambda: builtins.open("synthetic-read")),
            ("descriptor-file-read", lambda: os.open("synthetic-read", os.O_RDONLY)),
            ("file-identity-read", lambda: os.stat("synthetic-read")),
            ("direct-file-write", lambda: os.write(1, b"synthetic")),
            ("dynamic-candidate-import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("direct-candidate-import", lambda: builtins.__import__("candidates.zig_candidate")),
            ("audit-process", lambda: subprocess.Popen(["synthetic"])),
            ("native-process", lambda: os.system("synthetic")),
            ("background-worker", lambda: threading.Thread().start()),
            ("wall-clock", lambda: time.time()),
            ("monotonic-clock", lambda: time.monotonic()),
            ("performance-clock", lambda: time.perf_counter()),
            ("operating-system-randomness", lambda: os.urandom(8)),
            ("garbage-collection", lambda: gc.collect()),
        ):
            reject("block-actual-" + title, operation)
        accept(
            "all-source-only-effects-genuinely-blocked",
            all(number > 0 for number in blocked.values()),
        )
        accept(
            "no-real-candidate-module-loaded",
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
        )

    verify_runtime(synthetic=True)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "frozen_audit_relative": AUDIT_RELATIVE,
        "frozen_audit_sha256": AUDIT_SHA256,
        "immutable_policy_sha256": dict(IMMUTABLE_POLICY_ITEMS),
        "families": ["rust", "c", "zig"],
        "positive_control_count": len(accepted),
        "positive_controls": accepted,
        "negative_control_count": len(rejected),
        "negative_controls": rejected,
        "source_only_blocked_operations": blocked,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_audit_process_count": 0,
        "actual_reference_workers": 0,
        "real_candidate_files_read": 0,
        "real_native_binary_files_read": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--record", action="store_true")
    parser.add_argument("--candidate", "--family", dest="candidate", choices=tuple(FAMILY_SPECS))
    parser.add_argument("--label")
    parser.add_argument("--recorder-source-sha256")
    parser.add_argument(
        "--audit-source-sha256",
        "--oracle-source-sha256",
        dest="audit_source_sha256",
    )
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--source-pin", action="append")
    parser.add_argument("--native-pin", action="append")
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        verify_runtime(synthetic=True)
        require(
            all(
                getattr(options, field) in (None, False)
                for field in (
                    "record", "candidate", "label", "recorder_source_sha256",
                    "audit_source_sha256", "candidate_source_sha256",
                    "native_engine_sha256", "native_bridge_sha256",
                    "source_pin", "native_pin",
                )
            ),
            "a source-only self-test cannot pin, authenticate, or execute a real candidate",
        )
        result = source_self_test()
    else:
        verify_runtime()
        require(options.record is True, "require explicit actual V3 ownership-audit recording")
        spec = family_spec(options.candidate)
        label = validate_label(options.label)
        pins = OwnerPins(
            family=spec.name,
            recorder=validate_digest(options.recorder_source_sha256, "frozen recorder source"),
            audit=validate_digest(options.audit_source_sha256, "frozen V3 audit source"),
            candidate=validate_digest(options.candidate_source_sha256, "owned candidate adapter"),
            native_engine=validate_digest(options.native_engine_sha256, "owned native engine"),
            native_bridge=validate_digest(options.native_bridge_sha256, "owned native bridge"),
            source_entries=tuple(options.source_pin or ()),
            native_entries=tuple(options.native_pin or ()),
        )
        validate_pins(pins)
        result = record_audit(pins, label)
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RecorderError, OSError, subprocess.SubprocessError, TypeError, ValueError) as error:
        print(
            "independent V3 ownership audit recording failed closed: " + str(error),
            file=sys.stderr,
        )
        raise SystemExit(1) from error
