#!/usr/bin/env python3
"""Durably record the frozen, two-reference managed-buffer baseline only.

Synthetic self-tests never read the workspace, start a worker, import a
candidate, sample a clock, or publish evidence.  Real observation requires
``--record-baseline``, both exact frozen SHA-256 pins, and one fresh bounded
label.  Only the two precisely named, no-clobber evidence files can be written.
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
import importlib.machinery
import importlib.util
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
SOURCE_RELATIVE = "tools/record_independent_managed_buffer_lifetime_v1.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-managed-buffer-lifetime-v1-recorder"
ORACLE_RELATIVE = "tools/independent_managed_buffer_lifetime_v1.py"
ORACLE_ABSOLUTE = ROOT + "/" + ORACLE_RELATIVE
ORACLE_SCHEMA = "rebar-independent-managed-buffer-lifetime-v1"
ORACLE_SHA256 = (
    "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489"
)
MATRIX_SHA256 = (
    "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976"
)
PUBLISHED_SEED = 0x4D424C4946455631
CASES_PER_GROUP = 32
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
CASE_COUNT = len(GROUPS) * CASES_PER_GROUP
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/"
)
STDLIB_SOURCES = types.MappingProxyType({
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
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_REPORT_BYTES = 256 * 1024 * 1024
CONTROLLER_TIMEOUT_SECONDS = 240
FLAGS = (0, 2, 256, 258)
BASIC_APIS = (
    "search", "match", "fullmatch", "findall", "split", "sub", "subn",
    "finditer",
)
ALL_APIS = BASIC_APIS + (
    "match.group", "match.groups", "match.expand",
    "compiled.scanner.search", "compiled.scanner.match",
    "public.scanner.scan",
)
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "_regex", "fancy_regex", "google_re2", "hyperscan", "onig",
    "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class RecorderError(Exception):
    """A frozen baseline, complete process, or durable publication changed."""


class SourceOnlyError(RecorderError):
    """A synthetic-only control attempted a real external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RecorderError(message)


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
        raise RecorderError("complete evidence is not canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64 and len(set(value)) > 1
            and all(item in "0123456789abcdef" for item in value),
            "an exact lowercase SHA-256 is mandatory: " + label)
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in items:
        require(type(key) is str and key not in value,
                "a complete baseline JSON field was duplicated")
        value[key] = item
    return value


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "a complete bounded controller output is mandatory: " + label)

    def reject_constant(_: str) -> Any:
        raise RecorderError("nonfinite evidence is forbidden")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (RecorderError, TypeError, ValueError, UnicodeError,
            json.JSONDecodeError) as error:
        raise RecorderError(
            "a complete baseline controller document is invalid: " + label
        ) from error
    require(type(value) is dict and canonical(value) == raw,
            "a canonical baseline controller output was clipped or replaced")
    return value


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 64
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for item in value)
            and "--" not in value,
            "an exact bounded lowercase no-escape baseline label is mandatory")
    return value


def approved_paths(label: Any) -> tuple[str, str]:
    slug = "managed-buffer-lifetime-v1-" + validate_label(label)
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


def safe_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and bool(value)
            and "\\" not in value and "\x00" not in value,
            "an exact no-follow relative path is mandatory")
    parts = tuple(value.split("/"))
    require(all(part not in {"", ".", ".."} for part in parts)
            and "/".join(parts) == value,
            "a frozen source or publication path escaped its root")
    return parts


def directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


def regular_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0))


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == SOURCE_ABSOLUTE
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
            "use only the exact pinned, isolated CPython baseline recorder")
    verify_clean_modules()


def verify_clean_modules(modules: Mapping[str, Any] | None = None) -> None:
    actual = sys.modules if modules is None else modules
    require(isinstance(actual, Mapping), "a genuine module table is mandatory")
    for name in actual:
        require(type(name) is str, "a forged module name entered the recorder")
        root = name.partition(".")[0]
        require(root != "candidates" and root not in FORBIDDEN_ENGINE_ROOTS,
                "a candidate or external regex entered the baseline recorder")


def read_owned_regular(
    relative: str, expected: str | None, maximum: int,
) -> dict[str, Any]:
    parts = safe_parts(relative)
    if expected is not None:
        validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "a bounded authentic frozen source is mandatory")
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact managed-baseline source root changed")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a frozen source parent became a symlink")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino)
                == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum,
                "a frozen managed-baseline source was replaced")
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "a frozen source was truncated during authentication")
            hasher.update(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "a frozen source gained an unauthenticated suffix")
        after = os.fstat(descriptor)
        actual = hasher.hexdigest()
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size)
                and (expected is None or actual == expected),
                "a frozen source owner or digest changed: " + relative)
        return {
            "relative": relative,
            "sha256": actual,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_pinned_absolute(
    absolute: str, expected: str, maximum: int,
) -> dict[str, Any]:
    validate_digest(expected, absolute)
    require(type(absolute) is str and os.path.isabs(absolute)
            and os.path.abspath(absolute) == absolute
            and os.path.realpath(absolute) == absolute
            and type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "a pinned standard-library path became unsafe")
    descriptor = os.open(absolute, regular_flags())
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and 0 < before.st_size <= maximum,
                "a genuine CPython source or binary was substituted")
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            raw = os.read(descriptor, min(remaining, 1_048_576))
            require(type(raw) is bytes and bool(raw),
                    "a genuine CPython source was truncated")
            hasher.update(raw)
            remaining -= len(raw)
        require(os.read(descriptor, 1) == b"",
                "a genuine CPython source gained a hidden suffix")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size)
                and hasher.hexdigest() == expected,
                "a genuine CPython source or executable changed")
        return {
            "path": absolute,
            "sha256": expected,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        os.close(descriptor)


def authenticate_source_closure() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {
        "recorder": read_owned_regular(
            SOURCE_RELATIVE, None, MAX_SOURCE_BYTES,
        ),
        "oracle": read_owned_regular(
            ORACLE_RELATIVE, ORACLE_SHA256, MAX_SOURCE_BYTES,
        ),
        "python": read_pinned_absolute(
            PINNED_PYTHON, PINNED_PYTHON_SHA256, MAX_BINARY_BYTES,
        ),
    }
    for name, (filename, expected) in STDLIB_SOURCES.items():
        result[name] = read_pinned_absolute(
            STDLIB_DIRECTORY + filename, expected, MAX_SOURCE_BYTES,
        )
    validate_source_closure(result)
    return result


def validate_source_closure(value: Any) -> dict[str, dict[str, Any]]:
    require(type(value) is dict
            and set(value) == {"recorder", "oracle", "python", *STDLIB_SOURCES},
            "the complete before-and-after CPython source closure is mandatory")
    for key, relative, expected in (
        ("recorder", SOURCE_RELATIVE, None),
        ("oracle", ORACLE_RELATIVE, ORACLE_SHA256),
    ):
        owner = value.get(key)
        require(type(owner) is dict
                and set(owner) == {
                    "relative", "sha256", "bytes", "device", "inode",
                }
                and owner.get("relative") == relative
                and (expected is None or owner.get("sha256") == expected)
                and validate_digest(owner.get("sha256"), relative)
                and type(owner.get("bytes")) is int and owner["bytes"] > 0
                and type(owner.get("device")) is int and owner["device"] >= 0
                and type(owner.get("inode")) is int and owner["inode"] > 0,
                "a frozen workspace source owner was replaced: " + key)
    expected_absolute: dict[str, tuple[str, str]] = {
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
    }
    for key, (filename, expected) in STDLIB_SOURCES.items():
        expected_absolute[key] = (STDLIB_DIRECTORY + filename, expected)
    for key, (path, expected) in expected_absolute.items():
        owner = value.get(key)
        require(type(owner) is dict
                and set(owner) == {"path", "sha256", "bytes", "device", "inode"}
                and owner.get("path") == path
                and owner.get("sha256") == expected
                and type(owner.get("bytes")) is int and owner["bytes"] > 0
                and type(owner.get("device")) is int and owner["device"] >= 0
                and type(owner.get("inode")) is int and owner["inode"] > 0,
                "a pinned CPython binary or regex source was replaced: " + key)
    return value


def encode_bytes(value: bytes) -> dict[str, str]:
    require(type(value) is bytes, "an exact frozen bytes payload is mandatory")
    return {"kind": "bytes", "hex": value.hex()}


def encode_text(value: str) -> dict[str, str]:
    require(type(value) is str, "an exact frozen Unicode payload is mandatory")
    return {"kind": "str", "value": value}


def carrier_descriptor(
    kind: str, payload: bytes, *, start: int = 0,
    stop: int | None = None, step: int = 1, behavior: str = "none",
) -> dict[str, Any]:
    require(type(kind) is str and type(payload) is bytes,
            "a real independently frozen subject descriptor is mandatory")
    return {
        "kind": kind,
        "hex": payload.hex(),
        "start": start,
        "stop": len(payload) if stop is None else stop,
        "step": step,
        "behavior": behavior,
    }


def template_descriptor(
    kind: str, payload: bytes, *, readonly: bool = True,
    start: int = 0, stop: int | None = None, step: int = 1,
    released: bool = False, behavior: str = "none",
) -> dict[str, Any]:
    require(type(kind) is str and type(payload) is bytes
            and type(readonly) is bool and type(released) is bool,
            "a real independently frozen template descriptor is mandatory")
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


def build_frozen_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and seed >= 0,
            "a complete deterministic managed-buffer seed is mandatory")
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
        for variant in range(CASES_PER_GROUP):
            noise = "".join(
                seeded.choice("abcdef0123456789") for _ in range(8)
            ).encode("ascii")
            payload = b"alpha42 beta7 !" + noise
            replacement = rb"<\g<word>>"
            subject = carrier_descriptor("bytes", payload)
            pattern = encode_bytes(rb"(?P<word>[A-Za-z]+)(?P<number>[0-9]*)")
            template = template_descriptor("bytes", replacement)
            operation = BASIC_APIS[variant % len(BASIC_APIS)]
            action = "none"
            flags = FLAGS[variant % len(FLAGS)]

            if group == "direct-bytearray-control":
                subject = carrier_descriptor("bytearray", payload)
            elif group == "readonly-contiguous-view":
                subject = carrier_descriptor("readonly-memoryview", payload)
            elif group == "writable-contiguous-view":
                subject = carrier_descriptor("mutable-memoryview", payload)
            elif group in {
                "readonly-sliced-contiguous-view",
                "writable-sliced-contiguous-view",
            }:
                padded = b"<<" + payload + b">>"
                kind = (
                    "readonly-memoryview"
                    if group == "readonly-sliced-contiguous-view"
                    else "mutable-memoryview"
                )
                subject = carrier_descriptor(
                    kind, padded, start=2, stop=len(padded) - 2,
                )
            elif group in {"readonly-strided-view", "writable-strided-view"}:
                interleaved = b"".join(bytes((item, 33)) for item in payload)
                kind = (
                    "readonly-memoryview" if group == "readonly-strided-view"
                    else "mutable-memoryview"
                )
                subject = carrier_descriptor(kind, interleaved, step=2)
            elif group == "released-before-operation":
                subject = carrier_descriptor(
                    "readonly-memoryview" if variant % 2 == 0
                    else "mutable-memoryview", payload,
                )
                action = "release-before-operation"
            elif group == "released-after-match-before-group":
                subject = carrier_descriptor(
                    "readonly-memoryview" if variant % 2 == 0
                    else "mutable-memoryview", payload,
                )
                operation = "match.group" if variant % 2 == 0 else "match.groups"
                action = "release-after-match"
            elif group == "released-after-match-before-expand":
                subject = carrier_descriptor(
                    "readonly-memoryview" if variant % 2 == 0
                    else "mutable-memoryview", payload,
                )
                operation = "match.expand"
                action = "release-after-match"
            elif group == "backing-mutated-after-match":
                subject = carrier_descriptor("mutable-memoryview", payload)
                operation = (
                    "match.group", "match.groups", "match.expand",
                )[variant % 3]
                action = "mutate-backing-after-match"
            elif group == "bytearray-resize-during-live-iterator":
                subject = carrier_descriptor("bytearray", payload)
                operation = "finditer"
                action = "resize-during-live-iterator"
            elif group == "bytearray-resize-after-iterator-teardown":
                subject = carrier_descriptor("bytearray", payload)
                operation = "finditer"
                action = "resize-after-iterator-teardown"
            elif group in {
                "pep688-subject-acquire-release",
                "pep688-subject-overwrite-on-release",
            }:
                behavior = (
                    "stable" if group == "pep688-subject-acquire-release"
                    else "overwrite"
                )
                subject = carrier_descriptor(
                    "tracked-exporter", payload, behavior=behavior,
                )
            elif group == "pep688-subject-exporter-error":
                subject = carrier_descriptor(
                    "failing-exporter", payload, behavior="error",
                )
            elif group == "pep688-template-exporter-error":
                template = template_descriptor(
                    "failing-exporter", replacement, behavior="error",
                )
                operation = ("match.expand", "sub", "subn")[variant % 3]
            elif group in {
                "readonly-template-memoryview", "writable-template-memoryview",
            }:
                template = template_descriptor(
                    "template-memoryview", replacement,
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
                subject = carrier_descriptor(
                    "tracked-exporter", payload,
                    behavior="overwrite" if variant % 2 else "stable",
                )
                operation = (
                    "match.group", "match.groups", "match.expand",
                )[variant % 3]
                action = "observe-match-retained-lifetime"
            elif group in {
                "iterator-create-and-advance-lifetime",
                "iterator-exhaust-release",
                "iterator-delete-and-gc-release",
            }:
                subject = carrier_descriptor(
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
            elif group in {
                "native-scanner-search-lifetime",
                "native-scanner-match-lifetime",
            }:
                subject = carrier_descriptor(
                    "tracked-exporter", payload,
                    behavior="overwrite" if variant % 2 else "stable",
                )
                operation = (
                    "compiled.scanner.search"
                    if group == "native-scanner-search-lifetime"
                    else "compiled.scanner.match"
                )
                action = "observe-native-scanner-lifetime"
            elif group in {
                "public-scanner-branch-and-callback-identity",
                "public-scanner-lexicon-mutation-and-flags",
            }:
                operation = "public.scanner.scan"
                if variant % 4 == 1:
                    subject = carrier_descriptor("bytearray", payload)
                elif variant % 4 == 2:
                    subject = carrier_descriptor("readonly-memoryview", payload)
                elif variant % 4 == 3:
                    subject = carrier_descriptor("mutable-memoryview", payload)
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
                    subject = encode_text(unicode_payload)
                else:
                    pattern = encode_text(r"(?P<word>\w+)(?P<number>\d*)")
                operation = BASIC_APIS[variant % len(BASIC_APIS)]
            elif group == "unicode-surrogate-and-normalization-boundaries":
                subject = encode_text(
                    "café42 Δelta7 e\u0301 \ud800 😀 "
                    + noise.decode("ascii")
                )
                pattern = encode_text(text_patterns[variant % len(text_patterns)])
                template = encode_text(
                    r"<\g<word>>" if variant % 2 == 0 else r"\g<0>"
                )
                operation = BASIC_APIS[variant % len(BASIC_APIS)]

            cases.append({
                "case": "managed-buffer-lifetime.v1." + format(len(cases), "04d"),
                "group": group,
                "variant": variant,
                "seed": seed,
                "flags": flags,
                "operation": operation,
                "action": action,
                "pattern": pattern,
                "subject": subject,
                "template": template,
            })
    return cases


def validate_matrix(value: Any) -> list[dict[str, Any]]:
    require(len(GROUPS) == 32 and CASES_PER_GROUP == 32 and CASE_COUNT == 1024,
            "the independently frozen case denominator silently changed")
    require(type(value) is list and len(value) == CASE_COUNT
            and value == build_frozen_matrix()
            and digest(value) == MATRIX_SHA256,
            "the complete prospectively frozen case matrix was substituted")
    for index, case in enumerate(value):
        require(type(case) is dict
                and set(case) == {
                    "case", "group", "variant", "seed", "flags", "operation",
                    "action", "pattern", "subject", "template",
                }
                and case.get("case")
                == "managed-buffer-lifetime.v1." + format(index, "04d")
                and case.get("group") == GROUPS[index // CASES_PER_GROUP]
                and type(case.get("variant")) is int
                and case["variant"] == index % CASES_PER_GROUP
                and type(case.get("seed")) is int
                and case["seed"] == PUBLISHED_SEED
                and type(case.get("flags")) is int
                and case["flags"] in FLAGS
                and case.get("operation") in ALL_APIS,
                "a managed-buffer property case was omitted or reordered")
    return value


def capture_stream(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
            "preserve every complete bounded process byte: " + label)
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
            and validate_digest(value.get("sha256"), label)
            and value.get("complete") is True,
            "a complete isolated process stream was omitted: " + label)
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise RecorderError("invalid process-stream base64: " + label) from error
    require(len(raw) == value["bytes"]
            and hashlib.sha256(raw).hexdigest() == value["sha256"]
            and base64.b64encode(raw).decode("ascii") == value["base64"],
            "a complete isolated process stream was truncated: " + label)
    return raw


def validate_reference_guard(value: Any) -> dict[str, Any]:
    require(type(value) is dict and set(value) == {
        "candidate_import_count", "external_regex_import_count",
        "actual_method_guard_checks", "required_method_guard_checks",
        "future_candidate_guard_relative", "future_candidate_guard_sha256",
        "future_ownership_audit_relative", "future_ownership_audit_sha256",
        "future_candidate_guard_installed",
    } and value.get("candidate_import_count") == 0
        and value.get("external_regex_import_count") == 0
        and value.get("actual_method_guard_checks") == 2 * CASE_COUNT
        and value.get("required_method_guard_checks") == 2 * CASE_COUNT
        and value.get("future_candidate_guard_relative") == V5_GUARD_RELATIVE
        and value.get("future_candidate_guard_sha256") == V5_GUARD_SHA256
        and value.get("future_ownership_audit_relative")
        == OWNERSHIP_AUDIT_RELATIVE
        and value.get("future_ownership_audit_sha256") == OWNERSHIP_AUDIT_SHA256
        and value.get("future_candidate_guard_installed") is False,
        "a genuine two-reference ownership guard was substituted")
    return value


def validate_standard_owners(
    value: Any, closure: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    require(type(value) is dict
            and set(value) == {"oracle", "python", *STDLIB_SOURCES},
            "the genuine reference omitted a complete pinned source closure")
    expected: dict[str, dict[str, Any]] = {
        "oracle": {
            "path": ORACLE_ABSOLUTE,
            "sha256": ORACLE_SHA256,
            "bytes": closure["oracle"]["bytes"],
            "device": closure["oracle"]["device"],
            "inode": closure["oracle"]["inode"],
        },
        "python": dict(closure["python"]),
    }
    for name in STDLIB_SOURCES:
        expected[name] = dict(closure[name])
    require(value == expected,
            "a reference used a different oracle, Python binary, or regex source")
    return value


def validate_outcome(value: Any) -> None:
    require(type(value) is dict
            and set(value) == {
                "status", "stage", "value", "exception", "events",
                "checkpoints", "callbacks", "warnings",
            }
            and value.get("status") in {"return", "raise"}
            and type(value.get("stage")) is str
            and type(value.get("events")) is list
            and type(value.get("checkpoints")) is list
            and type(value.get("callbacks")) is list
            and type(value.get("warnings")) is list,
            "a complete buffer lifetime, warning, or callback was concealed")
    if value["status"] == "return":
        require(value["exception"] is None,
                "a successful property observation concealed an exception")
    else:
        require(value["value"] is None and type(value.get("exception")) is dict,
                "a failing property observation concealed its exact exception")
    canonical(value)


def validate_records(
    matrix: list[dict[str, Any]], records: Any, expected: str,
) -> list[dict[str, Any]]:
    validate_digest(expected, "complete baseline records")
    require(type(records) is list and len(records) == CASE_COUNT,
            "all 1,024 complete standard-reference outcomes are mandatory")
    for case, record in zip(matrix, records, strict=True):
        require(type(record) is dict
                and set(record) == {"case", "group", "variant", "outcome"}
                and record.get("case") == case["case"]
                and record.get("group") == case["group"]
                and record.get("variant") == case["variant"],
                "an exact reference case was omitted, relabeled, or reordered")
        validate_outcome(record["outcome"])
    require(digest(records) == expected,
            "the entire genuine reference outcome vector was substituted")
    return records


def validate_reference_worker(
    value: Any, *, role: str, expected_pid: int,
    matrix: list[dict[str, Any]], closure: Mapping[str, Any],
    frozen: Any | None = None,
) -> dict[str, Any]:
    require(role in {"reference_a", "reference_b"}
            and type(expected_pid) is int and expected_pid > 0,
            "a distinct genuine reference role and process ID are mandatory")
    require(type(value) is dict, "a full genuine reference worker is mandatory")
    expected = {
        "schema": ORACLE_SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": expected_pid,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
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
    }, "a complete isolated worker field was added or omitted")
    for name, actual in expected.items():
        require(value.get(name) == actual,
                "a complete genuine CPython worker changed: " + name)
    validate_standard_owners(value["source_owners"], closure)
    validate_reference_guard(value["reference_guard"])
    validate_records(matrix, value["records"], value["records_sha256"])
    if frozen is not None:
        try:
            frozen.validate_reference_worker(
                value, role=role, source_pin=ORACLE_SHA256,
                matrix=matrix, expected_pid=expected_pid,
            )
        except Exception as error:
            raise RecorderError(
                "the unchanged frozen oracle rejected its genuine worker"
            ) from error
    return value


def validate_worker_process(
    evidence: Any, worker: Mapping[str, Any], role: str,
) -> dict[str, Any]:
    require(type(evidence) is dict
            and set(evidence) == {"role", "pid", "returncode", "stdout", "stderr"}
            and evidence.get("role") == role
            and type(evidence.get("pid")) is int
            and evidence["pid"] == worker.get("pid")
            and evidence.get("returncode") == 0,
            "a genuine standard-reference subprocess was forged")
    stdout = decode_stream(evidence.get("stdout"), role + " stdout")
    stderr = decode_stream(evidence.get("stderr"), role + " stderr")
    require(stderr == b"" and stdout == canonical(dict(worker)),
            "a genuine reference stream concealed or changed its outcomes")
    return evidence


def validate_baseline_result(
    value: Any, matrix: list[dict[str, Any]],
    closure: Mapping[str, Any], frozen: Any | None = None,
) -> dict[str, Any]:
    require(type(value) is dict, "a complete two-reference result is mandatory")
    expected = {
        "schema": ORACLE_SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
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
    require(set(value) == set(expected) | {
        "baseline_records_sha256", "source_owners", "reference_a",
        "reference_b", "reference_a_process", "reference_b_process",
    }, "a complete two-reference property baseline was forged")
    for name, actual in expected.items():
        require(value.get(name) == actual,
                "a complete two-reference baseline changed: " + name)
    validate_standard_owners(value["source_owners"], closure)
    first = validate_reference_worker(
        value["reference_a"], role="reference_a",
        expected_pid=value["reference_a"].get("pid"),
        matrix=matrix, closure=closure, frozen=frozen,
    )
    second = validate_reference_worker(
        value["reference_b"], role="reference_b",
        expected_pid=value["reference_b"].get("pid"),
        matrix=matrix, closure=closure, frozen=frozen,
    )
    validate_worker_process(value["reference_a_process"], first, "reference_a")
    validate_worker_process(value["reference_b_process"], second, "reference_b")
    require(first["pid"] != second["pid"]
            and first["source_owners"] == second["source_owners"]
            and first["records_sha256"] == second["records_sha256"]
            and first["records"] == second["records"]
            and value["baseline_records_sha256"] == first["records_sha256"],
            "two separately isolated CPython references did not exactly agree")
    if frozen is not None:
        try:
            frozen.validate_reference_pair(
                first, second,
                value["reference_a_process"], value["reference_b_process"],
                source_pin=ORACLE_SHA256, matrix=matrix,
            )
        except Exception as error:
            raise RecorderError(
                "the unchanged frozen oracle rejected both references"
            ) from error
    return value


def load_frozen_oracle() -> tuple[Any, list[dict[str, Any]]]:
    before = read_owned_regular(ORACLE_RELATIVE, ORACLE_SHA256, MAX_SOURCE_BYTES)
    verify_clean_modules()
    name = "_rebar_frozen_managed_buffer_lifetime_v1_recorder"
    require(name not in sys.modules,
            "a frozen managed oracle module was preseeded")
    specification = importlib.util.spec_from_file_location(name, ORACLE_ABSOLUTE)
    require(specification is not None
            and specification.origin == ORACLE_ABSOLUTE
            and isinstance(specification.loader,
                           importlib.machinery.SourceFileLoader),
            "the exact genuine frozen oracle loader was substituted")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    require(isinstance(module, types.ModuleType)
            and module.__name__ == name
            and getattr(module, "__file__", None) == ORACLE_ABSOLUTE
            and getattr(module, "SCHEMA", None) == ORACLE_SCHEMA
            and getattr(module, "SOURCE_RELATIVE", None) == ORACLE_RELATIVE
            and getattr(module, "MATRIX_SHA256", None) == MATRIX_SHA256
            and getattr(module, "PUBLISHED_SEED", None) == PUBLISHED_SEED
            and tuple(getattr(module, "GROUPS", ())) == GROUPS
            and getattr(module, "VARIANTS_PER_GROUP", None) == CASES_PER_GROUP
            and getattr(module, "CASE_COUNT", None) == CASE_COUNT
            and getattr(module, "PINNED_PYTHON", None) == PINNED_PYTHON
            and getattr(module, "PINNED_PYTHON_SHA256", None)
            == PINNED_PYTHON_SHA256
            and dict(getattr(module, "PINNED_STDLIB_SOURCES", {}))
            == dict(STDLIB_SOURCES)
            and getattr(module, "V5_GUARD_RELATIVE", None) == V5_GUARD_RELATIVE
            and getattr(module, "V5_GUARD_SHA256", None) == V5_GUARD_SHA256
            and getattr(module, "OWNERSHIP_AUDIT_RELATIVE", None)
            == OWNERSHIP_AUDIT_RELATIVE
            and getattr(module, "OWNERSHIP_AUDIT_SHA256", None)
            == OWNERSHIP_AUDIT_SHA256,
            "an independently frozen managed-buffer oracle was substituted")
    matrix = build_frozen_matrix()
    validate_matrix(matrix)
    try:
        require(module.build_matrix() == matrix
                and module.validate_matrix(matrix) == MATRIX_SHA256,
                "the immutable managed-buffer oracle disagrees with its recorder")
    except Exception as error:
        raise RecorderError("the frozen oracle rejected the exact case matrix") from error
    after = read_owned_regular(ORACLE_RELATIVE, ORACLE_SHA256, MAX_SOURCE_BYTES)
    require(before == after, "the frozen oracle changed during authenticated load")
    verify_clean_modules()
    return module, matrix


def require_directory_identity(
    retained: Any, expected: Any, literal: Any,
) -> None:
    require(type(retained) is tuple and type(expected) is tuple
            and type(literal) is tuple
            and len(retained) == len(expected) == len(literal) == 2
            and all(type(number) is int and number >= 0
                    for pair in (retained, expected, literal)
                    for number in pair)
            and retained == expected == literal,
            "the literal approved evidence directory was replaced")


def verify_retained_directory(preflight: Mapping[str, Any]) -> int:
    descriptor = preflight.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "retain one exact no-follow evidence directory")
    retained = os.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode),
            "the retained approved evidence directory was replaced")
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the literal approved repository root was replaced")
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an approved evidence parent became a symlink")
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
def preflight_fresh_outputs(label: str) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(label)
    report_parts = safe_parts(report)
    receipt_parts = safe_parts(receipt)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "preflight exactly two distinct managed-buffer publication paths")
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the genuine repository root was replaced")
        for component in report_parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a managed-buffer evidence parent became a symlink")
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError(
                "refusing to overwrite managed-buffer evidence: " + basename
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
            "fresh_paths_checked_before_baseline": True,
        }
        verify_retained_directory(result)
        yield result
    finally:
        for opened_descriptor in reversed(opened):
            os.close(opened_descriptor)


def readback(
    preflight: Mapping[str, Any], basename: str, expected: bytes,
) -> None:
    directory = verify_retained_directory(preflight)
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        actual = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(actual.st_mode) and stat.S_ISREG(named.st_mode)
                and (actual.st_dev, actual.st_ino)
                == (named.st_dev, named.st_ino)
                and actual.st_size == len(expected),
                "the published managed-buffer evidence was replaced")
        remaining = len(expected)
        hasher = hashlib.sha256()
        position = 0
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "published baseline evidence was truncated")
            require(part == expected[position:position + len(part)],
                    "published baseline evidence changed on disk")
            hasher.update(part)
            position += len(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b""
                and hasher.hexdigest() == hashlib.sha256(expected).hexdigest(),
                "published baseline evidence gained or lost bytes")
    finally:
        os.close(descriptor)
    verify_retained_directory(preflight)


def publish_atomic(
    preflight: Mapping[str, Any], document: Mapping[str, Any], kind: str,
) -> dict[str, Any]:
    require(kind in {"report", "receipt"},
            "publish only the two precise managed-buffer evidence files")
    raw = canonical(dict(document))
    require(0 < len(raw) <= MAX_REPORT_BYTES,
            "the full durable baseline document exceeds its safe bound")
    directory = verify_retained_directory(preflight)
    basename = preflight[kind + "_basename"]
    temporary = (
        ".rebar-managed-buffer-v1-" + basename + "-"
        + str(os.getpid()) + "-" + hashlib.sha256(raw).hexdigest()[:20]
    )
    safe_parts(temporary)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    identity: tuple[int, int] | None = None
    linked = False
    write_calls = 0
    try:
        original = os.fstat(descriptor)
        require(stat.S_ISREG(original.st_mode),
                "the fresh managed-buffer publication temporary is not regular")
        identity = (original.st_dev, original.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the owned publication temporary was replaced")
        position = 0
        while position < len(raw):
            count = os.write(descriptor, raw[position:])
            require(type(count) is int and count > 0,
                    "the complete managed-buffer report was truncated")
            position += count
            write_calls += 1
        os.fsync(descriptor)
        require(os.fstat(descriptor).st_size == len(raw),
                "durable managed-buffer evidence lost bytes")
        verify_retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the owned temporary changed before atomic publication")
        os.link(
            temporary, basename, src_dir_fd=directory,
            dst_dir_fd=directory, follow_symlinks=False,
        )
        linked = True
        os.fsync(directory)
        verify_retained_directory(preflight)
        destination = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((destination.st_dev, destination.st_ino) == identity,
                "the no-clobber durable destination was substituted")
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "refusing to remove a substituted publication temporary")
        os.unlink(temporary, dir_fd=directory)
        os.fsync(directory)
        verify_retained_directory(preflight)
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
    readback(preflight, basename, raw)
    return {
        "path": preflight[kind + "_relative"],
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "actual_write_calls": write_calls,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True,
        "owned_temporary_removed": True,
        "complete_readback_verified": True,
    }


def run_one_baseline_controller() -> dict[str, Any]:
    arguments = [
        PINNED_PYTHON, "-I", "-B", ORACLE_ABSOLUTE,
        "--baseline", "--oracle-source-sha256", ORACLE_SHA256,
        "--matrix-sha256", MATRIX_SHA256,
    ]
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
            "signal": None,
            "timed_out": False,
            "spawn_error": str(error),
            "stdout": b"",
            "stderr": b"",
        }
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=CONTROLLER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes
            and type(process.returncode) is int,
            "the managed-buffer controller lost its full process streams")
    return {
        "started": True,
        "pid": process.pid,
        "returncode": process.returncode,
        "signal": -process.returncode if process.returncode < 0 else None,
        "timed_out": timed_out,
        "spawn_error": None,
        "stdout": stdout,
        "stderr": stderr,
    }


def validate_oracle_failure(value: Any) -> dict[str, Any]:
    require(type(value) is dict and value.get("schema") == ORACLE_SCHEMA + "-failure"
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
            "a genuine frozen managed-buffer failure was forged")
    allowed = {
        "schema", "status", "error_type", "error",
        "complete_reference_worker_failure", "actual_candidate_workers",
        "actual_candidate_imports", "clock_samples", "timing_trials_run",
        "workspace_files_written", "evidence_files_created",
        "benchmark_files_read", "hidden_cases_read", "performance",
    }
    require(set(value) <= allowed and allowed - set(value)
            <= {"complete_reference_worker_failure"},
            "a structured frozen failure omitted complete diagnostics")
    nested = value.get("complete_reference_worker_failure")
    if nested is not None:
        require(type(nested) is dict,
                "a complete genuine failed-reference process was concealed")
        if "stdout" in nested:
            decode_stream(nested["stdout"], "failed genuine reference stdout")
        if "stderr" in nested:
            decode_stream(nested["stderr"], "failed genuine reference stderr")
    return value


def build_complete_report(
    label: str,
    process: Mapping[str, Any],
    matrix: list[dict[str, Any]],
    before: Mapping[str, Any],
    after: Mapping[str, Any] | None,
    *,
    frozen: Any | None = None,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    validate_label(label)
    validate_matrix(matrix)
    validate_source_closure(before)
    if after is not None:
        validate_source_closure(after)
    failures: list[str] = []
    raw_stdout = process.get("stdout")
    raw_stderr = process.get("stderr")
    stdout = capture_stream(raw_stdout, "complete actual baseline stdout")
    stderr = capture_stream(raw_stderr, "complete actual baseline stderr")
    result: dict[str, Any] | None = None
    decoded: dict[str, Any] | None = None
    structured_failure: dict[str, Any] | None = None
    worker_failure: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append(
            "the exact managed-buffer baseline could not start: "
            + str(process.get("spawn_error"))
        )
    if process.get("timed_out") is True:
        failures.append("the exact managed-buffer baseline exceeded its timeout")
    if raw_stdout:
        try:
            decoded = decode_document(raw_stdout, "complete baseline controller")
            if decoded.get("schema") == ORACLE_SCHEMA + "-two-reference-baseline":
                result = validate_baseline_result(decoded, matrix, before, frozen)
            elif decoded.get("schema") == ORACLE_SCHEMA + "-failure":
                structured_failure = validate_oracle_failure(decoded)
                worker_failure = structured_failure.get(
                    "complete_reference_worker_failure"
                )
                failures.append(
                    "the frozen genuine baseline reported: "
                    + structured_failure["error"]
                )
            else:
                raise RecorderError("an unrecognized baseline schema was emitted")
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append("invalid complete baseline controller result: " + str(error))
    if result is None:
        failures.append("the 1,024-case reference agreement remains unknown")
    if raw_stderr:
        failures.append("the genuine managed-buffer controller emitted stderr")
    expected_exit = 0 if result is not None and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        failures.append("the genuine controller crashed, timed out, or returned a wrong exit")
    if post_run_error is not None:
        failures.append("post-run frozen source authentication failed: " + post_run_error)
    if before != after:
        failures.append("a frozen source or standard binary changed during observation")
    return {
        "schema": SCHEMA + "-complete-baseline-report",
        "status": "FAIL" if failures else "PASS",
        "label": label,
        "python": "3.14.6",
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "source_closure_before": dict(before),
        "source_closure_after": dict(after) if after is not None else None,
        "source_closure_unchanged": before == after,
        "complete_baseline_process_stdout": stdout,
        "complete_baseline_process_stderr": stderr,
        "complete_baseline_result": result,
        "complete_structured_controller_document": decoded,
        "complete_structured_baseline_failure": structured_failure,
        "complete_reference_worker_failure": worker_failure,
        "validated_reference_a_case_count": (
            len(result["reference_a"]["records"])
            if result is not None else None
        ),
        "validated_reference_b_case_count": (
            len(result["reference_b"]["records"])
            if result is not None else None
        ),
        "baseline_records_sha256": (
            result["baseline_records_sha256"] if result is not None else None
        ),
        "baseline_reference_pids": (
            [result["reference_a"]["pid"], result["reference_b"]["pid"]]
            if result is not None else None
        ),
        "reference_a_records": (
            result["reference_a"]["records"] if result is not None else None
        ),
        "reference_b_records": (
            result["reference_b"]["records"] if result is not None else None
        ),
        "reference_a_process": (
            result["reference_a_process"] if result is not None else None
        ),
        "reference_b_process": (
            result["reference_b_process"] if result is not None else None
        ),
        "actual_reference_workers": (
            result["actual_reference_workers"] if result is not None else None
        ),
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": int(process.get("started") is True),
        "actual_baseline_controller_pid": process.get("pid"),
        "actual_baseline_process_returncode": process.get("returncode"),
        "actual_baseline_process_signal": process.get("signal"),
        "actual_baseline_process_timed_out": process.get("timed_out") is True,
        "actual_baseline_process_spawn_error": process.get("spawn_error"),
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


def make_receipt(
    label: str,
    report: Mapping[str, Any],
    report_publication: Mapping[str, Any],
    preflight: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS",
        "baseline_result_status": report["status"],
        "label": validate_label(label),
        "python": "3.14.6",
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
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
        "actual_baseline_process_signal": report["actual_baseline_process_signal"],
        "actual_baseline_process_timed_out": (
            report["actual_baseline_process_timed_out"]
        ),
        "complete_reference_worker_failure": (
            report["complete_reference_worker_failure"]
        ),
        "source_closure_before": report["source_closure_before"],
        "source_closure_after": report["source_closure_after"],
        "source_closure_unchanged": report["source_closure_unchanged"],
        "report_relative": report_publication["path"],
        "report_sha256": report_publication["sha256"],
        "report_bytes": report_publication["bytes"],
        "report_actual_write_calls": report_publication["actual_write_calls"],
        "report_file_fsync_completed": (
            report_publication["file_fsync_completed"]
        ),
        "report_directory_fsync_completed": (
            report_publication["directory_fsync_completed"]
        ),
        "report_atomic_no_overwrite_link": (
            report_publication["atomic_no_overwrite_link"]
        ),
        "report_complete_readback_verified": (
            report_publication["complete_readback_verified"]
        ),
        "receipt_relative": preflight["receipt_relative"],
        "approved_fresh_path_count": preflight["approved_fresh_path_count"],
        "fresh_paths_checked_before_baseline": (
            preflight["fresh_paths_checked_before_baseline"]
        ),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def record_baseline(label: str, oracle_pin: str, matrix_pin: str) -> dict[str, Any]:
    verify_runtime()
    validate_label(label)
    require(validate_digest(oracle_pin, "frozen managed-buffer oracle")
            == ORACLE_SHA256
            and validate_digest(matrix_pin, "frozen managed-buffer matrix")
            == MATRIX_SHA256,
            "pin the exact independently frozen managed-buffer oracle and matrix")
    before = authenticate_source_closure()
    frozen, matrix = load_frozen_oracle()
    require(authenticate_source_closure() == before,
            "the authenticated source closure changed before baseline recording")
    with preflight_fresh_outputs(label) as preflight:
        verify_retained_directory(preflight)
        process = run_one_baseline_controller()
        verify_retained_directory(preflight)
        after: dict[str, dict[str, Any]] | None = None
        post_run_error: str | None = None
        try:
            after = authenticate_source_closure()
        except (OSError, RecorderError) as error:
            post_run_error = str(error)
        report = build_complete_report(
            label, process, matrix, before, after,
            frozen=frozen, post_run_error=post_run_error,
        )
        report_publication = publish_atomic(preflight, report, "report")
        receipt = make_receipt(label, report, report_publication, preflight)
        receipt_publication = publish_atomic(preflight, receipt, "receipt")
    verify_runtime()
    return {
        "schema": SCHEMA + "-recorded",
        "status": report["status"],
        "publication_status": "PASS",
        "label": label,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "validated_reference_a_case_count": (
            report["validated_reference_a_case_count"]
        ),
        "validated_reference_b_case_count": (
            report["validated_reference_b_case_count"]
        ),
        "baseline_records_sha256": report["baseline_records_sha256"],
        "baseline_reference_pids": report["baseline_reference_pids"],
        "actual_reference_workers": report["actual_reference_workers"],
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "report_publication": report_publication,
        "receipt_publication": receipt_publication,
        "actual_baseline_controller_invocations": (
            report["actual_baseline_controller_invocations"]
        ),
        "all_failure_reasons": report["all_failure_reasons"],
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


class SourceOnlyBoundary:
    """Deny all real effects while validating in-memory recorder controls."""

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
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)
        self.originals.append((owner, name, previous))

        def denied(*args: Any, **kwargs: Any) -> Any:
            actual = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if type(mode) is str and any(item in mode for item in "wax+"):
                    actual = "file_writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT
                    | os.O_TRUNC | os.O_APPEND
                ):
                    actual = "file_writes"
            if category == "dynamic_imports" and args:
                target = args[0]
                if type(target) is str and (
                    target == "candidates" or target.startswith("candidates.")
                ):
                    actual = "candidate_imports"
            self.blocked[actual] += 1
            raise SourceOnlyError(
                "synthetic baseline recording cannot perform " + actual
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
            (os, "link", "file_writes"),
            (os, "unlink", "file_writes"),
            (os, "remove", "file_writes"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (os, "fsync", "directory_syncs"),
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


def synthetic_closure() -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {
        "recorder": {
            "relative": SOURCE_RELATIVE,
            "sha256": "12" * 32,
            "bytes": 12345,
            "device": 7,
            "inode": 1101,
        },
        "oracle": {
            "relative": ORACLE_RELATIVE,
            "sha256": ORACLE_SHA256,
            "bytes": 54321,
            "device": 7,
            "inode": 1102,
        },
        "python": {
            "path": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
            "bytes": 32387816,
            "device": 7,
            "inode": 1103,
        },
    }
    for number, (name, (filename, expected)) in enumerate(
        STDLIB_SOURCES.items(), start=1104,
    ):
        values[name] = {
            "path": STDLIB_DIRECTORY + filename,
            "sha256": expected,
            "bytes": 4096 + number,
            "device": 7,
            "inode": number,
        }
    return values


def standard_owners_from_closure(
    closure: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    result = {
        "oracle": {
            "path": ORACLE_ABSOLUTE,
            "sha256": ORACLE_SHA256,
            "bytes": closure["oracle"]["bytes"],
            "device": closure["oracle"]["device"],
            "inode": closure["oracle"]["inode"],
        },
        "python": dict(closure["python"]),
    }
    for name in STDLIB_SOURCES:
        result[name] = dict(closure[name])
    return result


def synthetic_reference_guard() -> dict[str, Any]:
    return {
        "candidate_import_count": 0,
        "external_regex_import_count": 0,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "required_method_guard_checks": 2 * CASE_COUNT,
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "future_candidate_guard_installed": False,
    }


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "case": case["case"],
        "group": case["group"],
        "variant": case["variant"],
        "outcome": {
            "status": "return",
            "stage": "synthetic-only",
            "value": {"type": "none"},
            "exception": None,
            "events": [],
            "checkpoints": [],
            "callbacks": [],
            "warnings": [],
        },
    } for case in matrix]


def synthetic_worker(
    role: str, pid: int, matrix: list[dict[str, Any]],
    records: list[dict[str, Any]], closure: Mapping[str, Any],
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
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
        "records_sha256": digest(records),
        "records": records,
        "source_owners": standard_owners_from_closure(closure),
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


def synthetic_worker_process(worker: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "role": worker["role"],
        "pid": worker["pid"],
        "returncode": 0,
        "stdout": capture_stream(canonical(dict(worker)), "synthetic worker"),
        "stderr": capture_stream(b"", "synthetic worker stderr"),
    }


def synthetic_baseline(
    matrix: list[dict[str, Any],], closure: Mapping[str, Any],
) -> dict[str, Any]:
    records = synthetic_records(matrix)
    first = synthetic_worker("reference_a", 58001, matrix, records, closure)
    second = synthetic_worker("reference_b", 58002, matrix, records, closure)
    return {
        "schema": ORACLE_SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
        "baseline_records_sha256": digest(records),
        "source_owners": standard_owners_from_closure(closure),
        "reference_a": first,
        "reference_b": second,
        "reference_a_process": synthetic_worker_process(first),
        "reference_b_process": synthetic_worker_process(second),
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


def source_self_test() -> dict[str, Any]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "run source-only controls under isolated pinned CPython 3.14.6")
    verify_clean_modules()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a synthetic durable-baseline positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a synthetic durable-baseline rejection was duplicated")
        try:
            action()
        except (RecorderError, ValueError, TypeError, KeyError,
                OSError, OverflowError):
            rejected.append(name)
            return
        raise RecorderError(
            "a forged durable-baseline control was accepted: " + name
        )

    with SourceOnlyBoundary() as boundary:
        matrix = build_frozen_matrix()
        accept("independently-reproduce-all-1024-exact-frozen-cases",
               validate_matrix(matrix) is matrix)
        accept("pin-the-exact-32-groups-and-32-cases-each",
               len(GROUPS) == 32 and CASES_PER_GROUP == 32
               and all(sum(case["group"] == group for case in matrix) == 32
                       for group in GROUPS))
        accept("preserve-the-exact-frozen-independent-matrix-hash",
               digest(matrix) == MATRIX_SHA256)
        accept("preserve-the-exact-no-loss-published-integer-seed",
               all(type(case["seed"]) is int
                   and case["seed"] == PUBLISHED_SEED for case in matrix))
        accept("preserve-all-original-public-and-scanner-operations",
               {case["operation"] for case in matrix} == set(ALL_APIS))
        accept("pin-the-exact-frozen-v5-zig-safe-ownership-policy",
               validate_digest(V5_GUARD_SHA256, "V5 guard") == V5_GUARD_SHA256)
        accept("pin-the-exact-independent-no-delegation-audit",
               validate_digest(OWNERSHIP_AUDIT_SHA256, "audit")
               == OWNERSHIP_AUDIT_SHA256)
        accept("retain-exact-distinct-no-clobber-report-and-receipt-paths",
               approved_paths("synthetic-proof") == (
                   APPROVED_DIRECTORY
                   + "/managed-buffer-lifetime-v1-synthetic-proof.json",
                   APPROVED_DIRECTORY
                   + "/managed-buffer-lifetime-v1-synthetic-proof"
                   + "-publication-receipt.json",
               ))
        closure = synthetic_closure()
        accept("authenticate-the-entire-in-memory-pinned-source-closure",
               validate_source_closure(closure) is closure)
        result = synthetic_baseline(matrix, closure)
        accept("preserve-two-complete-distinct-genuine-reference-vectors",
               validate_baseline_result(result, matrix, closure) is result)
        first = result["reference_a"]
        second = result["reference_b"]
        accept("preserve-all-2048-real-before-and-after-reference-guards",
               validate_reference_guard(first["reference_guard"])
               is first["reference_guard"])
        accept("preserve-first-complete-reversible-process-stream",
               validate_worker_process(
                   result["reference_a_process"], first, "reference_a",
               ) is result["reference_a_process"])
        accept("preserve-second-complete-reversible-process-stream",
               validate_worker_process(
                   result["reference_b_process"], second, "reference_b",
               ) is result["reference_b_process"])

        passing_process = {
            "started": True,
            "pid": 57001,
            "returncode": 0,
            "signal": None,
            "timed_out": False,
            "spawn_error": None,
            "stdout": canonical(result),
            "stderr": b"",
        }
        report = build_complete_report(
            "synthetic-proof", passing_process, matrix, closure, closure,
        )
        accept("preserve-a-complete-passing-two-reference-report",
               report["status"] == "PASS"
               and report["validated_reference_a_case_count"] == CASE_COUNT
               and report["validated_reference_b_case_count"] == CASE_COUNT
               and report["actual_reference_workers"] == 2)
        accept("preserve-every-ordered-baseline-outcome-without-publication",
               report["reference_a_records"] == first["records"]
               and report["reference_b_records"] == second["records"])

        crash = {
            **passing_process,
            "returncode": -11,
            "signal": 11,
            "stdout": b"",
            "stderr": b"synthetic isolated crash",
        }
        crash_report = build_complete_report(
            "synthetic-proof", crash, matrix, closure, closure,
        )
        accept("preserve-unknown-worker-outcomes-after-an-isolated-crash",
               crash_report["status"] == "FAIL"
               and crash_report["actual_baseline_process_signal"] == 11
               and crash_report["validated_reference_a_case_count"] is None
               and crash_report["validated_reference_b_case_count"] is None
               and crash_report["baseline_records_sha256"] is None
               and crash_report["actual_reference_workers"] is None)

        timeout = {
            **crash,
            "returncode": -9,
            "signal": 9,
            "timed_out": True,
            "stderr": b"synthetic isolated timeout",
        }
        timed_report = build_complete_report(
            "synthetic-proof", timeout, matrix, closure, closure,
        )
        accept("preserve-unknown-worker-outcomes-after-an-isolated-timeout",
               timed_report["status"] == "FAIL"
               and timed_report["actual_baseline_process_timed_out"] is True
               and timed_report["validated_reference_a_case_count"] is None
               and timed_report["validated_reference_b_case_count"] is None
               and timed_report["actual_reference_workers"] is None)

        unstarted = {
            "started": False,
            "pid": None,
            "returncode": None,
            "signal": None,
            "timed_out": False,
            "spawn_error": "synthetic launch rejected",
            "stdout": b"",
            "stderr": b"",
        }
        not_started = build_complete_report(
            "synthetic-proof", unstarted, matrix, closure, closure,
        )
        accept("preserve-an-unstarted-reference-as-unknown-not-zero",
               not_started["status"] == "FAIL"
               and not_started["actual_baseline_controller_invocations"] == 0
               and not_started["validated_reference_a_case_count"] is None
               and not_started["actual_reference_workers"] is None)

        structured = {
            "schema": ORACLE_SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": "ReferenceWorkerFailure",
            "error": "synthetic genuine reference failed",
            "complete_reference_worker_failure": {
                "role": "reference_b",
                "pid": 58002,
                "returncode": -11,
                "stdout": capture_stream(b"", "failed synthetic stdout"),
                "stderr": capture_stream(
                    b"synthetic complete crash", "failed synthetic stderr",
                ),
            },
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        structured_process = {
            **passing_process,
            "returncode": 1,
            "stdout": canonical(structured),
        }
        failed = build_complete_report(
            "synthetic-proof", structured_process, matrix, closure, closure,
        )
        accept("retain-all-structured-failed-reference-process-bytes",
               failed["status"] == "FAIL"
               and failed["complete_structured_baseline_failure"] == structured
               and failed["complete_reference_worker_failure"]
               == structured["complete_reference_worker_failure"]
               and failed["validated_reference_a_case_count"] is None)

        for index, label in enumerate((
            None, True, 1, "", "UPPER", "white space", ".", "..", "../escape",
            "/absolute", "nested/path", "back\\slash", "double--dash",
            "-leading", "trailing-", "nul\x00byte", "a" * 65,
        )):
            reject("reject-unsafe-fresh-publication-label-" + format(index, "02d"),
                   lambda label=label: approved_paths(label))

        for index, value in enumerate((
            None, True, 0, "", ".", "..", "/absolute", "a//b", "a/../b",
            "a/./b", "a\\b", "a\x00b",
        )):
            reject("reject-escaping-no-follow-path-" + format(index, "02d"),
                   lambda value=value: safe_parts(value))

        reject("reject-an-omitted-frozen-matrix-case",
               lambda: validate_matrix(matrix[:-1]))
        reject("reject-an-extra-frozen-matrix-case",
               lambda: validate_matrix(matrix + [matrix[0]]))
        reject("reject-reordered-frozen-matrix-cases",
               lambda: validate_matrix(list(reversed(matrix))))
        reject("reject-a-substituted-published-seed",
               lambda: validate_matrix(build_frozen_matrix(PUBLISHED_SEED + 1)))
        for field, replacement in (
            ("case", "managed-buffer-lifetime.v1.9999"),
            ("group", GROUPS[-1]),
            ("variant", 33),
            ("seed", PUBLISHED_SEED + 1),
            ("flags", -1),
            ("operation", "candidate.match"),
            ("action", "forged"),
        ):
            altered = list(matrix)
            row = dict(altered[0])
            row[field] = replacement
            altered[0] = row
            reject("reject-frozen-case-field-" + field,
                   lambda altered=altered: validate_matrix(altered))

        records = first["records"]
        expected_records = first["records_sha256"]
        reject("reject-an-omitted-full-reference-outcome",
               lambda: validate_records(matrix, records[:-1], expected_records))
        reject("reject-reordered-full-reference-outcomes",
               lambda: validate_records(matrix, list(reversed(records)),
                                        expected_records))
        reject("reject-a-forged-full-reference-digest",
               lambda: validate_records(matrix, records, "56" * 32))
        for field, replacement in (
            ("case", "managed-buffer-lifetime.v1.0999"),
            ("group", GROUPS[-1]),
            ("variant", 33),
        ):
            altered_records = list(records)
            changed = dict(altered_records[0])
            changed[field] = replacement
            altered_records[0] = changed
            reject("reject-forged-complete-reference-record-" + field,
                   lambda altered_records=altered_records:
                   validate_records(matrix, altered_records,
                                    digest(altered_records)))

        for field, replacement in (
            ("status", "unknown"),
            ("stage", None),
            ("exception", {"hidden": True}),
            ("events", None),
            ("checkpoints", None),
            ("callbacks", None),
            ("warnings", None),
        ):
            outcome = dict(records[0]["outcome"])
            outcome[field] = replacement
            reject("reject-forged-full-lifecycle-outcome-" + field,
                   lambda outcome=outcome: validate_outcome(outcome))

        for field, replacement in (
            ("candidate_import_count", 1),
            ("external_regex_import_count", 1),
            ("actual_method_guard_checks", 2047),
            ("required_method_guard_checks", 2047),
            ("future_candidate_guard_relative", "tools/foreign.py"),
            ("future_candidate_guard_sha256", "34" * 32),
            ("future_ownership_audit_relative", "tools/foreign-audit.py"),
            ("future_ownership_audit_sha256", "34" * 32),
            ("future_candidate_guard_installed", True),
        ):
            guard = dict(first["reference_guard"])
            guard[field] = replacement
            reject("reject-forged-isolated-reference-guard-" + field,
                   lambda guard=guard: validate_reference_guard(guard))

        for name in ("recorder", "oracle", "python", *STDLIB_SOURCES):
            forged = dict(closure)
            owner = dict(forged[name])
            owner["sha256"] = "invalid" if name == "recorder" else "89" * 32
            forged[name] = owner
            reject("reject-forged-before-after-source-owner-" + name,
                   lambda forged=forged: validate_source_closure(forged))
        for name in ("oracle", "python", *STDLIB_SOURCES):
            forged = dict(first["source_owners"])
            owner = dict(forged[name])
            owner["sha256"] = "89" * 32
            forged[name] = owner
            reject("reject-forged-genuine-worker-source-owner-" + name,
                   lambda forged=forged:
                   validate_standard_owners(forged, closure))

        for field, replacement in (
            ("schema", "foreign-baseline"),
            ("status", "FAIL"),
            ("python", "3.14.5"),
            ("oracle_source_sha256", "56" * 32),
            ("matrix_sha256", "78" * 32),
            ("published_seed", PUBLISHED_SEED + 1),
            ("group_count", 31),
            ("cases_per_group", 31),
            ("case_count", CASE_COUNT - 1),
            ("groups", list(reversed(GROUPS))),
            ("actual_reference_workers", 1),
            ("actual_candidate_workers", 1),
            ("actual_candidate_imports", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("workspace_files_written", 1),
            ("evidence_files_created", 1),
            ("benchmark_files_read", 1),
            ("hidden_cases_read", 1),
            ("performance", "faster"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
            ("baseline_records_sha256", "12" * 32),
        ):
            forged = dict(result)
            forged[field] = replacement
            reject("reject-forged-two-reference-baseline-" + field,
                   lambda forged=forged:
                   validate_baseline_result(forged, matrix, closure))

        for field, replacement in (
            ("schema", "foreign-worker"),
            ("status", "PASS"),
            ("role", "candidate-rust"),
            ("pid", 0),
            ("oracle_source_sha256", "34" * 32),
            ("matrix_sha256", "34" * 32),
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
            ("performance", "faster"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
            ("records_sha256", "56" * 32),
        ):
            worker = dict(first)
            worker[field] = replacement
            reject("reject-forged-reference-worker-" + field,
                   lambda worker=worker: validate_reference_worker(
                       worker, role="reference_a", expected_pid=58001,
                       matrix=matrix, closure=closure,
                   ))

        same_pid = dict(second)
        same_pid["pid"] = 58001
        altered_result = dict(result)
        altered_result["reference_b"] = same_pid
        altered_result["reference_b_process"] = synthetic_worker_process(same_pid)
        reject("reject-reusing-one-process-as-two-independent-references",
               lambda: validate_baseline_result(altered_result, matrix, closure))

        for role, key, worker in (
            ("reference_a", "reference_a_process", first),
            ("reference_b", "reference_b_process", second),
        ):
            for field, replacement in (
                ("role", "candidate-zig"),
                ("pid", 99999),
                ("returncode", 1),
                ("stderr", capture_stream(b"concealed stderr", "synthetic")),
            ):
                process = dict(result[key])
                process[field] = replacement
                reject("reject-forged-" + role + "-process-" + field,
                       lambda process=process, worker=worker, role=role:
                       validate_worker_process(process, worker, role))
            for field, replacement in (
                ("base64", "!"),
                ("bytes", result[key]["stdout"]["bytes"] + 1),
                ("sha256", "78" * 32),
                ("complete", False),
            ):
                stream = dict(result[key]["stdout"])
                stream[field] = replacement
                reject("reject-forged-" + role + "-stream-" + field,
                       lambda stream=stream, role=role:
                       decode_stream(stream, role + " synthetic"))

        reject("reject-duplicate-complete-controller-json-fields",
               lambda: decode_document(b'{"x":1,"x":2}\n', "duplicate"))
        reject("reject-noncanonical-complete-controller-json",
               lambda: decode_document(b'{ "x": 1 }\n', "noncanonical"))
        reject("reject-nonfinite-complete-controller-json",
               lambda: decode_document(b'{"x":NaN}\n', "nonfinite"))
        reject("reject-candidate-contamination-in-source-only-module-table",
               lambda: verify_clean_modules({
                   "re": object(), "candidates.zig_candidate": object(),
               }))
        reject("reject-external-regex-contamination-in-source-only-module-table",
               lambda: verify_clean_modules({"re": object(), "regex": object()}))

        for field, replacement in (
            ("schema", "foreign-failure"),
            ("status", "PASS"),
            ("error_type", 3),
            ("error", None),
            ("actual_candidate_workers", 1),
            ("actual_candidate_imports", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("workspace_files_written", 1),
            ("evidence_files_created", 1),
            ("benchmark_files_read", 1),
            ("hidden_cases_read", 1),
            ("performance", "faster"),
        ):
            forged = dict(structured)
            forged[field] = replacement
            reject("reject-forged-complete-structured-failure-" + field,
                   lambda forged=forged: validate_oracle_failure(forged))

        reject("block-source-only-holdout-and-evidence-file-reads",
               lambda: builtins.open("performance/held-out.json", "rb"))
        reject("block-source-only-durable-publication-writes",
               lambda: builtins.open("forbidden-managed-buffer.json", "wb"))
        reject("block-source-only-workspace-directory-enumeration",
               lambda: os.scandir("experiments"))
        reject("block-source-only-evidence-file-status",
               lambda: os.stat("experiments"))
        reject("block-source-only-evidence-replacement",
               lambda: os.replace("synthetic-before", "synthetic-after"))
        reject("block-source-only-no-clobber-durable-links",
               lambda: os.link("synthetic-before", "synthetic-after"))
        reject("block-source-only-file-and-directory-sync",
               lambda: os.fsync(12345))
        reject("block-source-only-candidate-imports",
               lambda: importlib.import_module("candidates.vm_candidate"))
        reject("block-source-only-dynamic-oracle-imports",
               lambda: importlib.import_module("tools.independent_managed_buffer_lifetime_v1"))
        reject("block-source-only-baseline-controller-processes",
               lambda: subprocess.Popen([PINNED_PYTHON, "-I", "-B"]))
        reject("block-source-only-background-threads",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-source-only-performance-timing",
               lambda: time.perf_counter())
        reject("block-source-only-wall-clock-samples",
               lambda: time.time())
        reject("block-source-only-garbage-collection",
               lambda: gc.collect())

        require(len(accepted) >= 16 and len(rejected) >= 100,
                "at least 100 independent fail-closed controls are mandatory")
        require(boundary.blocked["file_reads"] >= 3
                and boundary.blocked["file_writes"] >= 3
                and boundary.blocked["processes"] >= 1
                and boundary.blocked["candidate_imports"] >= 1
                and boundary.blocked["dynamic_imports"] >= 1
                and boundary.blocked["threads"] >= 1
                and boundary.blocked["clock_samples"] >= 2
                and boundary.blocked["garbage_collections"] >= 1
                and boundary.blocked["directory_syncs"] >= 1,
                "all real durable-publication effects must be blocked and exercised")

    verify_clean_modules()
    return {
        "schema": SCHEMA + "-synthetic-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "blocked_effect_attempts": dict(boundary.blocked),
        "actual_baseline_controller_invocations": 0,
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
        description="Durably preserve one frozen two-reference property baseline",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run synthetic no-effect recorder controls")
    modes.add_argument("--record-baseline", action="store_true",
                       help="publish exactly one frozen two-reference baseline")
    parser.add_argument("--label")
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(options.label is None
                    and options.oracle_source_sha256 is None
                    and options.matrix_sha256 is None,
                    "source-only controls cannot authorize actual observation")
            result = source_self_test()
            sys.stdout.buffer.write(canonical(result))
            return 0
        require(options.record_baseline,
                "exactly one explicit baseline recording mode is mandatory")
        result = record_baseline(
            validate_label(options.label),
            validate_digest(options.oracle_source_sha256, "frozen oracle"),
            validate_digest(options.matrix_sha256, "frozen matrix"),
        )
        sys.stdout.buffer.write(canonical(result))
        return 0 if result["status"] == "PASS" else 1
    except (RecorderError, OSError, ValueError, TypeError,
            subprocess.SubprocessError) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-recorder-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "oracle_source_sha256": ORACLE_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
