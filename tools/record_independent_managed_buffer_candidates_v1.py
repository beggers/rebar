#!/usr/bin/env python3
"""Record one genuinely isolated native candidate on the frozen buffer oracle.

The existing two-CPython baseline is authenticated from its exact published
receipt and losslessly streamed gzip archive.  A candidate can run only in a
separate pinned process under the unchanged V5 no-delegation ownership and
warning guards.  Synthetic self-tests cannot read, publish, execute a worker,
import a candidate, or sample a clock.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import codecs
import contextlib
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
SOURCE_RELATIVE = "tools/record_independent_managed_buffer_candidates_v1.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-managed-buffer-candidate-recorder-v1"
MANAGED_RELATIVE = "tools/independent_managed_buffer_lifetime_v1.py"
MANAGED_MODULE = "tools.independent_managed_buffer_lifetime_v1"
MANAGED_SCHEMA = "rebar-independent-managed-buffer-lifetime-v1"
MANAGED_SHA256 = (
    "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489"
)
BASELINE_RECORDER_RELATIVE = (
    "tools/record_independent_managed_buffer_lifetime_v1.py"
)
BASELINE_RECORDER_MODULE = (
    "tools.record_independent_managed_buffer_lifetime_v1"
)
BASELINE_RECORDER_SHA256 = (
    "dddc90f3b6449deeb31098d062af9077e3bea558645b3f2d71de2cd4e6488abd"
)
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_MODULE = "tools.independent_original_cpython_suite_v5"
V5_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
OWNERSHIP_AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
OWNERSHIP_AUDIT_SHA256 = (
    "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
)
MATRIX_SHA256 = (
    "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976"
)
PUBLISHED_SEED = 0x4D424C4946455631
BASELINE_RECORDS_SHA256 = (
    "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df"
)
BASELINE_RECEIPT_RELATIVE = (
    "experiments/rust_public_practice_v1/"
    "managed-buffer-lifetime-v1-shared-suite-v1-publication-receipt.json"
)
BASELINE_RECEIPT_SHA256 = (
    "adb34ba45089983ac1857639995c51bdc3ae81e0656fa4b89fd5c0f72420b3ba"
)
BASELINE_ARCHIVE_RELATIVE = (
    "experiments/rust_public_practice_v1/"
    "managed-buffer-lifetime-v1-shared-suite-v1.json.gz"
)
BASELINE_ARCHIVE_SHA256 = (
    "1840d5c5faf0422cfaaae0e277cf5d9bc5ed954fe50beca3d9794b9fd33e5fba"
)
BASELINE_REPORT_RELATIVE = (
    "experiments/rust_public_practice_v1/"
    "managed-buffer-lifetime-v1-shared-suite-v1.json"
)
BASELINE_REPORT_SHA256 = (
    "8c1acb346f476be4f05edd3e7afa73c9a4196bdafa19c2b6f90259ce6b622b68"
)
BASELINE_REPORT_BYTES = 108_978_141
BASELINE_ARCHIVE_BYTES = 4_374_362
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
TRUSTED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_ARCHIVE_BYTES = 96 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_SELECTED_VALUE_BYTES = 64 * 1024 * 1024
CONTROLLER_TIMEOUT_SECONDS = 300
CASES_PER_GROUP = 32
GROUPS = (
    "direct-bytes-control", "direct-bytearray-control",
    "readonly-contiguous-view", "writable-contiguous-view",
    "readonly-sliced-contiguous-view", "writable-sliced-contiguous-view",
    "readonly-strided-view", "writable-strided-view",
    "released-before-operation", "released-after-match-before-group",
    "released-after-match-before-expand", "backing-mutated-after-match",
    "bytearray-resize-during-live-iterator",
    "bytearray-resize-after-iterator-teardown",
    "pep688-subject-acquire-release", "pep688-subject-overwrite-on-release",
    "pep688-subject-exporter-error", "pep688-template-exporter-error",
    "readonly-template-memoryview", "writable-template-memoryview",
    "strided-template-memoryview", "released-template-memoryview",
    "match-group-retained-lifetime", "iterator-create-and-advance-lifetime",
    "iterator-exhaust-release", "iterator-delete-and-gc-release",
    "native-scanner-search-lifetime", "native-scanner-match-lifetime",
    "public-scanner-branch-and-callback-identity",
    "public-scanner-lexicon-mutation-and-flags",
    "bytes-vs-unicode-type-separation",
    "unicode-surrogate-and-normalization-boundaries",
)
CASE_COUNT = len(GROUPS) * CASES_PER_GROUP
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
GUARD_TRUE_FIELDS = (
    "original_matchers_blocked", "adapter_import_quarantined",
    "native_sre_blocked", "builtins_import_guarded",
    "importlib_import_guarded", "actual_object_identity_guarded",
    "warning_registry_introspection_safe", "warning_registry_exactly_absent",
    "cross_family_imports_blocked", "external_regex_imports_blocked",
)
GUARD_COUNTER_FIELDS = (
    "cached_original_matcher_descendant_count",
    "cached_original_holder_count",
    "owned_ctypes_load_count",
    "owned_ctypes_symbol_count",
)
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "_regex", "fancy_regex", "google_re2", "hyperscan", "onig",
    "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class CandidateRecorderError(Exception):
    """A frozen baseline, independent owner, or complete evidence changed."""


class SourceOnlyError(CandidateRecorderError):
    """A synthetic control attempted an actual observation or mutation."""


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
class OwnerPins:
    family: str
    recorder: str
    adapter: str
    engine: str
    bridge: str
    owned_sources: tuple[tuple[str, str], ...]


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
        raise CandidateRecorderError(message)


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("ascii") + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise CandidateRecorderError("full evidence is not canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64 and len(set(value)) > 1
            and all(item in "0123456789abcdef" for item in value),
            "an exact lowercase SHA-256 is mandatory: " + label)
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "an exact complete JSON field was duplicated")
        result[key] = value
    return result


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "a complete bounded process document is mandatory: " + label)

    def reject_constant(_: str) -> Any:
        raise CandidateRecorderError("nonfinite evidence is forbidden")

    try:
        result = json.loads(
            raw, object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (CandidateRecorderError, ValueError, TypeError, UnicodeError,
            json.JSONDecodeError) as error:
        raise CandidateRecorderError("invalid complete evidence: " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "a complete canonical process document was substituted")
    return result


def validate_label(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 64
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for item in value)
            and "--" not in value,
            "an exact bounded lowercase nonescaping run label is mandatory")
    return value


def safe_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and bool(value)
            and "\\" not in value and "\x00" not in value,
            "an exact no-follow owned relative path is mandatory")
    parts = tuple(value.split("/"))
    require(all(part not in {"", ".", ".."} for part in parts)
            and "/".join(parts) == value,
            "an evidence or native path escaped its approved root")
    return parts


def family_spec(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independently owned Rust, C, or Zig family")
    spec = FAMILIES[value]
    require(isinstance(spec, FamilySpec)
            and spec.name == value
            and spec.adapter_module.startswith("candidates.")
            and spec.bridge_module.startswith("candidates.")
            and spec.adapter_module != spec.bridge_module
            and spec.owned_ctypes is (value == "zig")
            and (spec.engine_relative == spec.bridge_relative) is (value == "c")
            and type(spec.owned_source_relatives) is tuple
            and len(set(spec.owned_source_relatives))
            == len(spec.owned_source_relatives)
            and spec.adapter_relative in spec.owned_source_relatives
            and all(safe_parts(path)[0] == "candidates"
                    for path in spec.owned_source_relatives),
            "a foreign or aliased candidate family was selected")
    return spec


def parse_owned_source(value: Any) -> tuple[str, str]:
    require(type(value) is str and value.count("=") == 1,
            "pin each complete owned source as exact/path=sha256")
    relative, expected = value.split("=", 1)
    parts = safe_parts(relative)
    require(parts[0] == "candidates",
            "a source pin escaped the independently owned candidate closure")
    return relative, validate_digest(expected, relative)


def make_owner_pins(
    family: str, recorder: str, adapter: str, engine: str, bridge: str,
    sources: list[str],
) -> OwnerPins:
    spec = family_spec(family)
    validate_digest(recorder, "candidate recorder source")
    validate_digest(adapter, "independent candidate adapter")
    validate_digest(engine, "independent native regex engine")
    validate_digest(bridge, "independent native Python bridge")
    parsed = tuple(parse_owned_source(item) for item in sources)
    require(len(parsed) == len(spec.owned_source_relatives)
            and len({path for path, _ in parsed}) == len(parsed)
            and set(path for path, _ in parsed)
            == set(spec.owned_source_relatives),
            "pin every exact owned source without aliases or sibling engines")
    mapped = dict(parsed)
    require(mapped[spec.adapter_relative] == adapter,
            "the candidate adapter escaped its complete source closure")
    require((engine == bridge) is (family == "c"),
            "only the C family's owned native engine and bridge may alias")
    return OwnerPins(family, recorder, adapter, engine, bridge, tuple(
        (path, mapped[path]) for path in spec.owned_source_relatives
    ))


def native_pins(pins: OwnerPins) -> dict[str, str]:
    require(isinstance(pins, OwnerPins),
            "an independently owned candidate pin closure is mandatory")
    spec = family_spec(pins.family)
    require((pins.engine == pins.bridge) is (spec.name == "c"),
            "an independent native engine or bridge was aliased")
    return {
        "source": validate_digest(pins.adapter, "adapter"),
        "native_engine": validate_digest(pins.engine, "native engine"),
        "native_bridge": validate_digest(pins.bridge, "native bridge"),
    }


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
                    "an independently owned parent became a symlink")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino)
                == (named.st_dev, named.st_ino),
                "an exact frozen source, archive, or owner was replaced")
        yield descriptor, before
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "an exact frozen file changed while being authenticated")
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_owned_regular(
    relative: str, expected: str, maximum: int, *, retain: bool = False,
) -> tuple[dict[str, Any], bytes | None]:
    validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_UNCOMPRESSED_BYTES,
            "an exact bounded source or archive is mandatory")
    with open_owned_descriptor(relative) as (descriptor, before):
        require(0 < before.st_size <= maximum,
                "a source, archive, or receipt exceeds its precise safe bound")
        hasher = hashlib.sha256()
        remaining = before.st_size
        pieces: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "an exact frozen file was truncated")
            hasher.update(block)
            if retain:
                pieces.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b""
                and hasher.hexdigest() == expected,
                "an exact independently pinned owner or archive changed")
        owner = {
            "relative": relative,
            "sha256": expected,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
        return owner, b"".join(pieces) if retain else None


def verify_runtime(*, candidate_loaded: bool = False) -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == ROOT
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == SOURCE_ABSOLUTE
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
            "use only isolated pinned CPython and the exact candidate recorder")
    if not candidate_loaded:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "a candidate escaped into baseline-only authentication")


def authenticate_module(
    module_name: str, relative: str, expected: str,
) -> tuple[types.ModuleType, dict[str, Any]]:
    before, _ = read_owned_regular(relative, expected, MAX_SOURCE_BYTES)
    module = importlib.import_module(module_name)
    absolute = ROOT + "/" + relative
    loader_spec = getattr(module, "__spec__", None)
    loader = getattr(loader_spec, "loader", None)
    require(type(module) is types.ModuleType
            and module.__name__ == module_name
            and getattr(module, "__file__", None) == absolute
            and os.path.realpath(absolute) == absolute
            and loader_spec is not None
            and getattr(loader_spec, "name", None) == module_name
            and getattr(loader_spec, "origin", None) == absolute
            and isinstance(loader, importlib.machinery.SourceFileLoader)
            and getattr(loader, "name", None) == module_name
            and getattr(loader, "path", None) == absolute,
            "an immutable source module or genuine loader was substituted")
    after, _ = read_owned_regular(relative, expected, MAX_SOURCE_BYTES)
    require(before == after,
            "an authenticated frozen source changed during genuine import")
    return module, before


def encode_bytes(value: bytes) -> dict[str, str]:
    return {"kind": "bytes", "hex": value.hex()}


def encode_text(value: str) -> dict[str, str]:
    return {"kind": "str", "value": value}


def carrier_descriptor(kind: str, payload: bytes, *, start: int = 0,
                       stop: int | None = None, step: int = 1,
                       behavior: str = "none") -> dict[str, Any]:
    return {"kind": kind, "hex": payload.hex(), "start": start,
            "stop": len(payload) if stop is None else stop,
            "step": step, "behavior": behavior}


def template_descriptor(kind: str, payload: bytes, *, readonly: bool = True,
                        start: int = 0, stop: int | None = None,
                        step: int = 1, released: bool = False,
                        behavior: str = "none") -> dict[str, Any]:
    return {"kind": kind, "hex": payload.hex(), "readonly": readonly,
            "start": start, "stop": len(payload) if stop is None else stop,
            "step": step, "released": released, "behavior": behavior}


def build_frozen_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and seed >= 0,
            "an exact published deterministic matrix seed is mandatory")
    seeded = random.Random(seed)
    cases: list[dict[str, Any]] = []
    text_patterns = (
        r"(?P<word>\w+)(?P<number>\d*)", r"(?a:\w+)", "\ud800",
        "e\u0301", "\N{LATIN SMALL LETTER E WITH ACUTE}", r".",
        r"(?i:[a-z]+)", r"(?P<word>\w+)",
    )
    for group in GROUPS:
        for variant in range(CASES_PER_GROUP):
            noise = "".join(seeded.choice("abcdef0123456789")
                            for _ in range(8)).encode("ascii")
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
            elif group in {"readonly-sliced-contiguous-view",
                           "writable-sliced-contiguous-view"}:
                padded = b"<<" + payload + b">>"
                kind = ("readonly-memoryview"
                        if group == "readonly-sliced-contiguous-view"
                        else "mutable-memoryview")
                subject = carrier_descriptor(kind, padded, start=2,
                                             stop=len(padded) - 2)
            elif group in {"readonly-strided-view", "writable-strided-view"}:
                raw = b"".join(bytes((item, 33)) for item in payload)
                kind = ("readonly-memoryview"
                        if group == "readonly-strided-view"
                        else "mutable-memoryview")
                subject = carrier_descriptor(kind, raw, step=2)
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
                operation = ("match.group", "match.groups",
                             "match.expand")[variant % 3]
                action = "mutate-backing-after-match"
            elif group == "bytearray-resize-during-live-iterator":
                subject = carrier_descriptor("bytearray", payload)
                operation, action = "finditer", "resize-during-live-iterator"
            elif group == "bytearray-resize-after-iterator-teardown":
                subject = carrier_descriptor("bytearray", payload)
                operation, action = "finditer", "resize-after-iterator-teardown"
            elif group in {"pep688-subject-acquire-release",
                           "pep688-subject-overwrite-on-release"}:
                behavior = ("stable" if group == "pep688-subject-acquire-release"
                            else "overwrite")
                subject = carrier_descriptor("tracked-exporter", payload,
                                             behavior=behavior)
            elif group == "pep688-subject-exporter-error":
                subject = carrier_descriptor("failing-exporter", payload,
                                             behavior="error")
            elif group == "pep688-template-exporter-error":
                template = template_descriptor("failing-exporter", replacement,
                                               behavior="error")
                operation = ("match.expand", "sub", "subn")[variant % 3]
            elif group in {"readonly-template-memoryview",
                           "writable-template-memoryview"}:
                template = template_descriptor(
                    "template-memoryview", replacement,
                    readonly=group == "readonly-template-memoryview",
                )
                operation = ("match.expand", "sub", "subn")[variant % 3]
            elif group == "strided-template-memoryview":
                raw = b"".join(bytes((item, 33)) for item in replacement)
                template = template_descriptor("template-memoryview", raw,
                                               readonly=variant % 2 == 0, step=2)
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
                operation = ("match.group", "match.groups",
                             "match.expand")[variant % 3]
                action = "observe-match-retained-lifetime"
            elif group in {"iterator-create-and-advance-lifetime",
                           "iterator-exhaust-release",
                           "iterator-delete-and-gc-release"}:
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
            elif group in {"native-scanner-search-lifetime",
                           "native-scanner-match-lifetime"}:
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
            elif group in {"public-scanner-branch-and-callback-identity",
                           "public-scanner-lexicon-mutation-and-flags"}:
                operation = "public.scanner.scan"
                if variant % 4 == 1:
                    subject = carrier_descriptor("bytearray", payload)
                elif variant % 4 == 2:
                    subject = carrier_descriptor("readonly-memoryview", payload)
                elif variant % 4 == 3:
                    subject = carrier_descriptor("mutable-memoryview", payload)
                action = ("observe-public-scanner"
                          if group == "public-scanner-branch-and-callback-identity"
                          else "mutate-public-scanner-lexicon")
            elif group == "bytes-vs-unicode-type-separation":
                text = "café42 Δelta7 e\u0301 \ud800 😀 " + noise.decode("ascii")
                if variant % 2 == 0:
                    subject = encode_text(text)
                else:
                    pattern = encode_text(r"(?P<word>\w+)(?P<number>\d*)")
                operation = BASIC_APIS[variant % len(BASIC_APIS)]
            elif group == "unicode-surrogate-and-normalization-boundaries":
                subject = encode_text(
                    "café42 Δelta7 e\u0301 \ud800 😀 " + noise.decode("ascii")
                )
                pattern = encode_text(text_patterns[variant % len(text_patterns)])
                template = encode_text(
                    r"<\g<word>>" if variant % 2 == 0 else r"\g<0>"
                )
                operation = BASIC_APIS[variant % len(BASIC_APIS)]
            cases.append({
                "case": "managed-buffer-lifetime.v1." + format(len(cases), "04d"),
                "group": group, "variant": variant, "seed": seed,
                "flags": flags, "operation": operation, "action": action,
                "pattern": pattern, "subject": subject, "template": template,
            })
    return cases


def validate_matrix(matrix: Any) -> list[dict[str, Any]]:
    require(len(GROUPS) == 32 and CASES_PER_GROUP == 32 and CASE_COUNT == 1024,
            "the prospectively frozen managed-buffer denominator was changed")
    require(type(matrix) is list and len(matrix) == CASE_COUNT
            and matrix == build_frozen_matrix()
            and digest(matrix) == MATRIX_SHA256,
            "the exact frozen 1,024-case source-ordered matrix was substituted")
    for index, case in enumerate(matrix):
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
                and type(case.get("flags")) is int and case["flags"] in FLAGS
                and case.get("operation") in ALL_APIS,
                "a seeded property case or complete denominator was changed")
    return matrix


class StreamingJsonObject:
    """Select authenticated top-level gzip fields without loading the archive."""

    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.decoder = codecs.getincrementaldecoder("utf-8")("strict")
        self.json_decoder = json.JSONDecoder(object_pairs_hook=unique_json_object)
        self.buffer = ""
        self.position = 0
        self.ended = False
        self.bytes = 0
        self.sha256 = hashlib.sha256()

    def fill(self) -> bool:
        if self.ended:
            return False
        block = self.stream.read(131_072)
        require(type(block) is bytes,
                "an authenticated gzip archive produced non-byte data")
        if not block:
            self.buffer += self.decoder.decode(b"", final=True)
            self.ended = True
            return False
        self.bytes += len(block)
        require(self.bytes <= MAX_UNCOMPRESSED_BYTES,
                "the authenticated baseline archive exceeds its safe bound")
        self.sha256.update(block)
        self.buffer += self.decoder.decode(block, final=False)
        return True

    def compact(self) -> None:
        if self.position >= 262_144:
            self.buffer = self.buffer[self.position:]
            self.position = 0

    def peek(self) -> str | None:
        while self.position == len(self.buffer) and self.fill():
            pass
        return self.buffer[self.position] if self.position < len(self.buffer) else None

    def take(self) -> str:
        item = self.peek()
        require(item is not None, "a complete gzip JSON value was truncated")
        self.position += 1
        return item

    def whitespace(self) -> None:
        while self.peek() in (" ", "\t", "\n", "\r"):
            self.position += 1
            self.compact()

    def literal(self, expected: str) -> None:
        self.whitespace()
        require(self.take() == expected,
                "an authenticated streaming JSON delimiter was substituted")

    def decode_value(self) -> Any:
        self.whitespace()
        self.compact()
        while True:
            try:
                result, end = self.json_decoder.raw_decode(
                    self.buffer, self.position,
                )
            except json.JSONDecodeError as error:
                require(not self.ended,
                        "an authenticated selected JSON field is invalid")
                require(len(self.buffer) - self.position
                        <= MAX_SELECTED_VALUE_BYTES,
                        "an exact selected baseline vector exceeds its bound")
                if not self.fill():
                    raise CandidateRecorderError(
                        "an authenticated selected JSON field was truncated"
                    ) from error
                continue
            self.position = end
            return result

    def skip_value(self) -> None:
        self.whitespace()
        first = self.peek()
        require(first is not None,
                "an authenticated unselected archive value was truncated")
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
            string = False
            escaped = False
            while True:
                item = self.take()
                if string:
                    if escaped:
                        escaped = False
                    elif item == "\\":
                        escaped = True
                    elif item == '"':
                        string = False
                elif item == '"':
                    string = True
                elif item in ("{", "["):
                    stack.append("}" if item == "{" else "]")
                elif item in ("}", "]"):
                    require(bool(stack) and stack[-1] == item,
                            "an authenticated JSON container was corrupted")
                    stack.pop()
                    if not stack:
                        return
                self.compact()
        else:
            start = self.position
            while True:
                item = self.peek()
                if item is None or item in (",", "}", "]", " ", "\t", "\r", "\n"):
                    break
                self.position += 1
            raw = self.buffer[start:self.position]
            require(bool(raw), "a scalar archive value was omitted")
            try:
                actual, end = self.json_decoder.raw_decode(raw)
            except json.JSONDecodeError as error:
                raise CandidateRecorderError(
                    "an authenticated archive scalar is invalid"
                ) from error
            require(end == len(raw) and actual is not ...,  # no omitted scalar
                    "an authenticated archive scalar was corrupted")

    def select(self, required: frozenset[str]) -> dict[str, Any]:
        self.literal("{")
        seen: set[str] = set()
        selected: dict[str, Any] = {}
        self.whitespace()
        if self.peek() == "}":
            self.take()
        else:
            while True:
                key = self.decode_value()
                require(type(key) is str and key not in seen,
                        "a complete authenticated archive key was duplicated")
                seen.add(key)
                self.literal(":")
                if key in required:
                    selected[key] = self.decode_value()
                else:
                    self.skip_value()
                self.whitespace()
                next_item = self.take()
                if next_item == "}":
                    break
                require(next_item == ",",
                        "a complete archive object separator was substituted")
        self.whitespace()
        require(self.peek() is None,
                "an authenticated gzip archive gained hidden JSON suffixes")
        require(set(selected) == required,
                "a mandatory baseline property or reference vector was omitted")
        return selected


BASELINE_SELECTED_FIELDS = frozenset({
    "schema", "status", "label", "python", "oracle_source_sha256",
    "matrix_sha256", "published_seed", "group_count", "cases_per_group",
    "case_count", "groups", "source_closure_before", "source_closure_after",
    "source_closure_unchanged", "baseline_records_sha256",
    "baseline_reference_pids", "validated_reference_a_case_count",
    "validated_reference_b_case_count", "reference_a_records",
    "reference_b_records", "actual_reference_workers",
    "actual_candidate_workers", "actual_candidate_imports",
    "actual_baseline_controller_invocations", "clock_samples",
    "timing_trials_run", "benchmark_files_read", "hidden_cases_read",
    "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})


def validate_baseline_receipt(value: Any) -> dict[str, Any]:
    require(type(value) is dict,
            "the exact committed managed-buffer baseline receipt is mandatory")
    expected = {
        "schema": (
            "rebar-independent-managed-buffer-lifetime-v1-recorder"
            "-durable-publication-receipt"
        ),
        "status": "PASS",
        "baseline_result_status": "PASS",
        "label": "shared-suite-v1",
        "python": "3.14.6",
        "oracle_relative": MANAGED_RELATIVE,
        "oracle_source_sha256": MANAGED_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": 32,
        "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "report_relative": BASELINE_REPORT_RELATIVE,
        "report_sha256": BASELINE_REPORT_SHA256,
        "report_bytes": BASELINE_REPORT_BYTES,
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
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    for name, expected_value in expected.items():
        require(value.get(name) == expected_value,
                "the immutable passed baseline receipt changed: " + name)
    pids = value.get("baseline_reference_pids")
    require(type(pids) is list and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1],
            "the authentic baseline did not use two distinct CPython processes")
    return value


def authenticate_baseline_receipt() -> tuple[dict[str, Any], dict[str, Any]]:
    owner, raw = read_owned_regular(
        BASELINE_RECEIPT_RELATIVE, BASELINE_RECEIPT_SHA256,
        MAX_SOURCE_BYTES, retain=True,
    )
    require(raw is not None, "retain the complete authenticated baseline receipt")
    return validate_baseline_receipt(
        decode_document(raw, "exact committed baseline receipt")
    ), owner


def validate_baseline_archive(
    value: Any, matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any], managed: Any | None = None,
) -> dict[str, Any]:
    require(type(value) is dict and set(value) == BASELINE_SELECTED_FIELDS,
            "stream all exact required baseline properties without omission")
    expected = {
        "schema": (
            "rebar-independent-managed-buffer-lifetime-v1-recorder"
            "-complete-baseline-report"
        ),
        "status": "PASS",
        "label": "shared-suite-v1",
        "python": "3.14.6",
        "oracle_source_sha256": MANAGED_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "groups": list(GROUPS),
        "source_closure_unchanged": True,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    for name, expected_value in expected.items():
        require(value.get(name) == expected_value,
                "the lossless frozen baseline archive changed: " + name)
    require(value.get("baseline_reference_pids")
            == receipt.get("baseline_reference_pids")
            and value.get("source_closure_before")
            == value.get("source_closure_after")
            and type(value.get("source_closure_before")) is dict,
            "the archived reference process or source closure was substituted")
    first = value["reference_a_records"]
    second = value["reference_b_records"]
    require(type(first) is list and type(second) is list
            and len(first) == len(second) == CASE_COUNT
            and first == second
            and digest(first) == digest(second) == BASELINE_RECORDS_SHA256,
            "the two authentic complete baseline outcome vectors disagree")
    for row, a, b in zip(matrix, first, second, strict=True):
        require(type(a) is dict and type(b) is dict
                and a == b
                and set(a) == {"case", "group", "variant", "outcome"}
                and a["case"] == row["case"]
                and a["group"] == row["group"]
                and a["variant"] == row["variant"],
                "a source-ordered archived baseline case was substituted")
        require(type(a["outcome"]) is dict,
                "a complete archived baseline outcome was omitted")
    if managed is not None:
        try:
            managed.validate_records(matrix, first, BASELINE_RECORDS_SHA256)
            managed.validate_records(matrix, second, BASELINE_RECORDS_SHA256)
        except Exception as error:
            raise CandidateRecorderError(
                "the immutable managed oracle rejected its archived references"
            ) from error
    return value


def stream_baseline_archive(
    matrix: list[dict[str, Any]], receipt: Mapping[str, Any], managed: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    archive_owner, _ = read_owned_regular(
        BASELINE_ARCHIVE_RELATIVE, BASELINE_ARCHIVE_SHA256,
        MAX_ARCHIVE_BYTES,
    )
    require(archive_owner["bytes"] == BASELINE_ARCHIVE_BYTES,
            "the exact compressed baseline archive was substituted")
    with open_owned_descriptor(BASELINE_ARCHIVE_RELATIVE) as (fd, original):
        require(original.st_size == BASELINE_ARCHIVE_BYTES
                and (original.st_dev, original.st_ino)
                == (archive_owner["device"], archive_owner["inode"]),
                "the exact compressed baseline inode changed")
        with io.FileIO(fd, "rb", closefd=False) as source:
            with gzip.GzipFile(fileobj=source, mode="rb") as compressed:
                parser = StreamingJsonObject(compressed)
                selected = parser.select(BASELINE_SELECTED_FIELDS)
        require(parser.bytes == BASELINE_REPORT_BYTES
                and parser.sha256.hexdigest() == BASELINE_REPORT_SHA256,
                "lossless baseline decompression differs from the signed receipt")
    validate_baseline_archive(selected, matrix, receipt, managed)
    return selected, archive_owner


def authenticate_family_closure(
    v5: Any, pins: OwnerPins,
) -> dict[str, dict[str, Any]]:
    spec = family_spec(pins.family)
    actual = native_pins(pins)
    original = v5.family_spec(spec.name)
    require(original.name == spec.name
            and original.adapter_module == spec.adapter_module
            and original.adapter_relative == spec.adapter_relative
            and original.engine_relative == spec.engine_relative
            and original.bridge_module == spec.bridge_module
            and original.bridge_relative == spec.bridge_relative
            and original.owned_ctypes is spec.owned_ctypes
            and v5.validate_pins(actual, original) == actual,
            "the exact corrected V5 native family or alias policy changed")
    source_map = dict(pins.owned_sources)
    require(set(source_map) == set(spec.owned_source_relatives)
            and source_map.get(spec.adapter_relative) == pins.adapter,
            "the complete owned semantic engine source closure was substituted")
    result: dict[str, dict[str, Any]] = {}
    for path in spec.owned_source_relatives:
        result[path], _ = read_owned_regular(
            path, source_map[path], MAX_SOURCE_BYTES,
        )
    for path, expected in (
        (spec.engine_relative, pins.engine),
        (spec.bridge_relative, pins.bridge),
    ):
        if path in result:
            require(result[path]["sha256"] == expected,
                    "a source and native binary owner were aliased")
        else:
            result[path], _ = read_owned_regular(
                path, expected, MAX_BINARY_BYTES,
            )
    require(set(result) == set(spec.owned_source_relatives)
            | {spec.engine_relative, spec.bridge_relative},
            "an exact owned source or binary was omitted")
    return result


def authenticate_prerequisites(
    pins: OwnerPins,
) -> tuple[Any, Any, Any, list[dict[str, Any]], dict[str, Any]]:
    verify_runtime()
    spec = family_spec(pins.family)
    recorder_owner, _ = read_owned_regular(
        SOURCE_RELATIVE, pins.recorder, MAX_SOURCE_BYTES,
    )
    managed, managed_owner = authenticate_module(
        MANAGED_MODULE, MANAGED_RELATIVE, MANAGED_SHA256,
    )
    baseline, baseline_owner = authenticate_module(
        BASELINE_RECORDER_MODULE, BASELINE_RECORDER_RELATIVE,
        BASELINE_RECORDER_SHA256,
    )
    v5, v5_owner = authenticate_module(V5_MODULE, V5_RELATIVE, V5_SHA256)
    require(getattr(managed, "SCHEMA", None) == MANAGED_SCHEMA
            and getattr(managed, "MATRIX_SHA256", None) == MATRIX_SHA256
            and getattr(managed, "PUBLISHED_SEED", None) == PUBLISHED_SEED
            and getattr(managed, "CASE_COUNT", None) == CASE_COUNT
            and tuple(getattr(managed, "GROUPS", ())) == GROUPS
            and getattr(managed, "V5_GUARD_SHA256", None) == V5_SHA256
            and getattr(baseline, "ORACLE_SHA256", None) == MANAGED_SHA256
            and getattr(baseline, "MATRIX_SHA256", None) == MATRIX_SHA256
            and getattr(v5, "SOURCE_RELATIVE", None) == V5_RELATIVE
            and v5.current_source_sha256() == V5_SHA256,
            "a corrected original guard or frozen managed oracle was changed")
    matrix = build_frozen_matrix()
    validate_matrix(matrix)
    require(managed.build_matrix() == matrix
            and managed.validate_matrix(matrix) == MATRIX_SHA256
            and baseline.validate_matrix(matrix) == matrix,
            "the immutable baseline oracle and recorder changed 1,024 cases")
    chosen = v5.family_spec(spec.name)
    require(chosen.adapter_module == spec.adapter_module
            and chosen.bridge_module == spec.bridge_module
            and chosen.owned_ctypes is spec.owned_ctypes,
            "the exact corrected V5 candidate family was substituted")
    return managed, baseline, v5, matrix, {
        "recorder": recorder_owner,
        "managed_oracle": managed_owner,
        "baseline_recorder": baseline_owner,
        "original_v5": v5_owner,
    }


def snapshot_guard(active: Mapping[str, Any], spec: FamilySpec) -> dict[str, Any]:
    require(isinstance(active, Mapping),
            "the actual continuous V5 native ownership guard is mandatory")
    result: dict[str, Any] = {}
    for field in GUARD_TRUE_FIELDS:
        require(active.get(field) is True,
                "a genuine no-delegation matcher guard was lost: " + field)
        result[field] = True
    require(active.get("public_type_names_used_for_ownership") is False,
            "a re-compatible owned public type was falsely delegated")
    result["public_type_names_used_for_ownership"] = False
    for field in ("actual_method_guard_checks",
                  "actual_warning_registry_guard_checks"):
        require(type(active.get(field)) is int
                and active[field] == 2 * CASE_COUNT,
                "a before-and-after candidate identity guard was omitted")
        result[field] = active[field]
    require(active.get("owned_native_ffi_allowed") is spec.owned_ctypes,
            "the independently owned Zig-only native FFI policy changed")
    result["owned_native_ffi_allowed"] = spec.owned_ctypes
    for field in (
        "trusted_stdlib_ctypes_preloaded",
        "trusted_stdlib_ctypes_builtin_verified",
        "trusted_stdlib_ctypes_pythonapi_initialized",
    ):
        require(active.get(field) is spec.owned_ctypes,
                "the corrected safe Zig ctypes guard was substituted: " + field)
        result[field] = spec.owned_ctypes
    expected_ctypes = TRUSTED_CTYPES_SHA256 if spec.owned_ctypes else None
    require(active.get("trusted_stdlib_ctypes_source_sha256") == expected_ctypes,
            "the genuine preloaded pinned ctypes module was substituted")
    result["trusted_stdlib_ctypes_source_sha256"] = expected_ctypes
    for field in GUARD_COUNTER_FIELDS:
        count = active.get(field)
        require(type(count) is int and count >= 0,
                "a complete owned-native guard counter was concealed")
        result[field] = count
    if spec.owned_ctypes:
        require(result["owned_ctypes_load_count"] >= 1
                and result["owned_ctypes_symbol_count"] >= 1,
                "the exact independent Zig engine and symbols were not loaded")
    else:
        require(result["owned_ctypes_load_count"] == 0
                and result["owned_ctypes_symbol_count"] == 0,
                "an unowned external native engine was loaded")
    return result


def validate_native_provenance(
    value: Any, pins: OwnerPins,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    require(type(value) is dict
            and set(value) == {"source", "native_engine", "native_bridge"},
            "an exact genuinely guarded adapter and native owner are mandatory")
    expected = (
        ("source", spec.adapter_relative, pins.adapter),
        ("native_engine", spec.engine_relative, pins.engine),
        ("native_bridge", spec.bridge_relative, pins.bridge),
    )
    for key, path, expected_hash in expected:
        owner = value.get(key)
        require(type(owner) is dict
                and set(owner) == {
                    "relative", "sha256", "bytes", "device", "inode",
                }
                and owner.get("relative") == path
                and owner.get("sha256") == expected_hash
                and type(owner.get("bytes")) is int and owner["bytes"] > 0
                and type(owner.get("device")) is int and owner["device"] >= 0
                and type(owner.get("inode")) is int and owner["inode"] > 0,
                "a genuinely owned regex engine component changed: " + key)
    require((value["native_engine"] == value["native_bridge"])
            is (spec.name == "c"),
            "a C-only shared bridge or independent engine was aliased")
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
            "a full managed-buffer lifecycle, callback, or warning was hidden")
    if value["status"] == "return":
        require(value["exception"] is None,
                "a successful candidate concealed an actual exception")
    else:
        require(value["value"] is None and type(value["exception"]) is dict,
                "a failing candidate concealed its actual Python exception")
    canonical(value)


def validate_records(
    matrix: list[dict[str, Any]], value: Any, expected: str,
    managed: Any | None = None,
) -> list[dict[str, Any]]:
    validate_digest(expected, "complete source-ordered property outcomes")
    require(type(value) is list and len(value) == CASE_COUNT,
            "all 1,024 complete source-ordered candidate outcomes are mandatory")
    for case, record in zip(matrix, value, strict=True):
        require(type(record) is dict
                and set(record) == {"case", "group", "variant", "outcome"}
                and record.get("case") == case["case"]
                and record.get("group") == case["group"]
                and record.get("variant") == case["variant"],
                "a complete property case was hidden, reordered, or relabeled")
        validate_outcome(record["outcome"])
    require(digest(value) == expected,
            "the complete owned candidate observation vector was substituted")
    if managed is not None:
        try:
            managed.validate_records(matrix, value, expected)
        except Exception as error:
            raise CandidateRecorderError(
                "the frozen managed oracle rejected complete candidate records"
            ) from error
    return value


def execute_candidate_worker(pins: OwnerPins) -> dict[str, Any]:
    verify_runtime()
    spec = family_spec(pins.family)
    managed, _, v5, matrix, source_owners = authenticate_prerequisites(pins)
    receipt, receipt_owner = authenticate_baseline_receipt()
    reference, archive_owner = stream_baseline_archive(matrix, receipt, managed)
    before = authenticate_family_closure(v5, pins)
    warning, identity, _, _ = v5.load_frozen_oracles()
    genuine = importlib.import_module("re")
    require(type(genuine) is types.ModuleType and genuine.__name__ == "re",
            "the genuine original matcher owner was substituted")
    chosen = v5.family_spec(spec.name)
    owned = native_pins(pins)
    records: list[dict[str, Any]] = []
    guard_evidence: dict[str, Any] | None = None
    native_evidence: dict[str, Any] | None = None
    with warning.installed_warning_safe_guard(identity):
        with v5.chosen_original_guard(
            genuine, owned, chosen, identity, warning,
        ) as active:
            candidate = active.get("candidate")
            require(type(candidate) is types.ModuleType
                    and candidate.__name__ == spec.adapter_module,
                    "a sibling, fallback, or foreign matching engine escaped")
            require(active.get("actual_method_guard_checks") == 0
                    and active.get("actual_warning_registry_guard_checks") == 0,
                    "the real continuous ownership guards did not start at zero")
            for case in matrix:
                active["verify"]()
                active["actual_method_guard_checks"] += 1
                try:
                    outcome = managed.execute_case(case, candidate)
                    managed.validate_outcome(outcome)
                finally:
                    active["verify"]()
                    active["actual_method_guard_checks"] += 1
                records.append({
                    "case": case["case"], "group": case["group"],
                    "variant": case["variant"], "outcome": outcome,
                })
            guard_evidence = snapshot_guard(active, spec)
            provenance = active.get("native_provenance")
            require(v5.validate_owners(provenance, chosen, owned),
                    "a genuinely guarded adapter or native engine changed")
            native_evidence = validate_native_provenance(provenance, pins)
    require(guard_evidence is not None and native_evidence is not None,
            "the complete continuous V5 ownership guard was omitted")
    records_hash = digest(records)
    validate_records(matrix, records, records_hash, managed)
    after = authenticate_family_closure(v5, pins)
    require(before == after,
            "a complete from-scratch engine source changed during observation")
    return {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": "candidate-" + spec.name,
        "candidate_family": spec.name,
        "pid": os.getpid(),
        "recorder_source_sha256": pins.recorder,
        "managed_oracle_relative": MANAGED_RELATIVE,
        "managed_oracle_sha256": MANAGED_SHA256,
        "baseline_recorder_relative": BASELINE_RECORDER_RELATIVE,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP,
        "groups": list(GROUPS),
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": reference["baseline_reference_pids"],
        "baseline_receipt_owner": receipt_owner,
        "baseline_archive_owner": archive_owner,
        "source_provenance": source_owners,
        "native_provenance": native_evidence,
        "owned_source_closure": after,
        "matcher_guard": guard_evidence,
        "records_sha256": records_hash,
        "records": records,
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


def validate_guard(value: Any, spec: FamilySpec) -> dict[str, Any]:
    require(type(value) is dict, "a genuine continuous V5 guard is mandatory")
    for name in GUARD_TRUE_FIELDS:
        require(value.get(name) is True,
                "a native no-delegation guard was omitted: " + name)
    require(value.get("public_type_names_used_for_ownership") is False,
            "a compatible owned pattern was misclassified")
    for name in ("actual_method_guard_checks",
                 "actual_warning_registry_guard_checks"):
        require(type(value.get(name)) is int
                and value[name] == 2 * CASE_COUNT,
                "a before-and-after identity or warning guard was omitted")
    require(value.get("owned_native_ffi_allowed") is spec.owned_ctypes,
            "the independently owned Zig native FFI policy changed")
    for name in ("trusted_stdlib_ctypes_preloaded",
                 "trusted_stdlib_ctypes_builtin_verified",
                 "trusted_stdlib_ctypes_pythonapi_initialized"):
        require(value.get(name) is spec.owned_ctypes,
                "the corrected genuine ctypes preload was replaced")
    require(value.get("trusted_stdlib_ctypes_source_sha256")
            == (TRUSTED_CTYPES_SHA256 if spec.owned_ctypes else None),
            "the exact trusted standard ctypes source was replaced")
    for name in GUARD_COUNTER_FIELDS:
        require(type(value.get(name)) is int and value[name] >= 0,
                "a real owned engine guard counter was hidden")
    if spec.owned_ctypes:
        require(value["owned_ctypes_load_count"] >= 1
                and value["owned_ctypes_symbol_count"] >= 1,
                "the exact genuine Zig native owner never loaded")
    else:
        require(value["owned_ctypes_load_count"] == 0
                and value["owned_ctypes_symbol_count"] == 0,
                "a foreign native library was loaded")
    return value


def validate_owner(owner: Any, relative: str, expected: str) -> dict[str, Any]:
    require(type(owner) is dict
            and set(owner) == {"relative", "sha256", "bytes", "device", "inode"}
            and owner.get("relative") == relative
            and owner.get("sha256") == expected
            and type(owner.get("bytes")) is int and owner["bytes"] > 0
            and type(owner.get("device")) is int and owner["device"] >= 0
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "a pinned regular source or archive owner was substituted")
    return owner


def validate_worker(
    value: Any, pins: OwnerPins, matrix: list[dict[str, Any]],
    *, expected_pid: int, managed: Any | None = None,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    require(type(expected_pid) is int and expected_pid > 0,
            "an independently isolated candidate PID is mandatory")
    require(type(value) is dict, "a full genuinely isolated worker is mandatory")
    expected = {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED", "python": "3.14.6",
        "role": "candidate-" + spec.name,
        "candidate_family": spec.name,
        "pid": expected_pid,
        "recorder_source_sha256": pins.recorder,
        "managed_oracle_relative": MANAGED_RELATIVE,
        "managed_oracle_sha256": MANAGED_SHA256,
        "baseline_recorder_relative": BASELINE_RECORDER_RELATIVE,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT, "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP, "groups": list(GROUPS),
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "evidence_files_created": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(set(value) == set(expected) | {
        "baseline_reference_pids", "baseline_receipt_owner",
        "baseline_archive_owner", "source_provenance", "native_provenance",
        "owned_source_closure", "matcher_guard", "records_sha256", "records",
        "actual_candidate_imports",
    }, "a complete isolated candidate field was omitted or injected")
    for name, actual in expected.items():
        require(value.get(name) == actual,
                "a complete candidate process observation changed: " + name)
    pids = value.get("baseline_reference_pids")
    require(type(pids) is list and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1]
            and expected_pid not in pids,
            "a native candidate was aliased to a genuine reference process")
    require(type(value.get("actual_candidate_imports")) is int
            and value["actual_candidate_imports"] >= 2,
            "a genuine owned adapter or bridge was never imported")
    validate_owner(value["baseline_receipt_owner"],
                   BASELINE_RECEIPT_RELATIVE, BASELINE_RECEIPT_SHA256)
    archive = validate_owner(value["baseline_archive_owner"],
                             BASELINE_ARCHIVE_RELATIVE, BASELINE_ARCHIVE_SHA256)
    require(archive["bytes"] == BASELINE_ARCHIVE_BYTES,
            "the lossless baseline gzip owner was replaced")
    sources = value.get("source_provenance")
    require(type(sources) is dict
            and set(sources) == {
                "recorder", "managed_oracle", "baseline_recorder", "original_v5",
            }, "the complete frozen tool source closure was omitted")
    for key, relative, expected_hash in (
        ("recorder", SOURCE_RELATIVE, pins.recorder),
        ("managed_oracle", MANAGED_RELATIVE, MANAGED_SHA256),
        ("baseline_recorder", BASELINE_RECORDER_RELATIVE,
         BASELINE_RECORDER_SHA256),
        ("original_v5", V5_RELATIVE, V5_SHA256),
    ):
        validate_owner(sources.get(key), relative, expected_hash)
    validate_native_provenance(value["native_provenance"], pins)
    closure = value.get("owned_source_closure")
    expected_paths = set(spec.owned_source_relatives) | {
        spec.engine_relative, spec.bridge_relative,
    }
    require(type(closure) is dict and set(closure) == expected_paths,
            "a complete owned source or native closure was omitted")
    owned_sources = dict(pins.owned_sources)
    for path in spec.owned_source_relatives:
        validate_owner(closure[path], path, owned_sources[path])
    validate_owner(closure[spec.engine_relative], spec.engine_relative,
                   pins.engine)
    validate_owner(closure[spec.bridge_relative], spec.bridge_relative,
                   pins.bridge)
    validate_guard(value.get("matcher_guard"), spec)
    validate_records(matrix, value.get("records"),
                     value.get("records_sha256"), managed)
    return value


def capture_stream(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
            "retain complete bounded native process bytes: " + label)
    return {"base64": base64.b64encode(value).decode("ascii"),
            "bytes": len(value), "sha256": hashlib.sha256(value).hexdigest(),
            "complete": True}


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"base64", "bytes", "sha256", "complete"}
            and type(value.get("base64")) is str
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and validate_digest(value.get("sha256"), label)
            and value.get("complete") is True,
            "an exact isolated native process stream was hidden: " + label)
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise CandidateRecorderError("invalid exact native process base64") from error
    require(len(raw) == value["bytes"]
            and hashlib.sha256(raw).hexdigest() == value["sha256"]
            and base64.b64encode(raw).decode("ascii") == value["base64"],
            "an isolated native process stream was truncated or replaced")
    return raw


def run_one_candidate_worker(pins: OwnerPins) -> dict[str, Any]:
    spec = family_spec(pins.family)
    arguments = [
        PINNED_PYTHON, "-I", "-B", SOURCE_ABSOLUTE,
        "--internal-candidate-worker", "--candidate", spec.name,
        "--recorder-source-sha256", pins.recorder,
        "--oracle-source-sha256", MANAGED_SHA256,
        "--matrix-sha256", MATRIX_SHA256,
        "--baseline-receipt-sha256", BASELINE_RECEIPT_SHA256,
        "--baseline-archive-sha256", BASELINE_ARCHIVE_SHA256,
        "--baseline-records-sha256", BASELINE_RECORDS_SHA256,
        "--candidate-source-sha256", pins.adapter,
        "--native-engine-sha256", pins.engine,
        "--native-bridge-sha256", pins.bridge,
    ]
    for path, expected in pins.owned_sources:
        arguments.extend(("--owned-source-sha256", path + "=" + expected))
    try:
        process = subprocess.Popen(
            arguments, cwd=ROOT, shell=False,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=False,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"started": False, "pid": None, "returncode": None,
                "signal": None, "timed_out": False,
                "spawn_error": str(error), "stdout": b"", "stderr": b""}
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=CONTROLLER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes
            and type(process.returncode) is int,
            "the complete owned candidate lost its actual raw process streams")
    return {
        "started": True, "pid": process.pid, "returncode": process.returncode,
        "signal": -process.returncode if process.returncode < 0 else None,
        "timed_out": timed_out, "spawn_error": None,
        "stdout": stdout, "stderr": stderr,
    }


def approved_paths(family: Any, label: Any) -> tuple[str, str]:
    spec = family_spec(family)
    slug = spec.name + "-managed-buffer-lifetime-v1-" + validate_label(label)
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
            "retain exactly one approved no-follow evidence directory")
    retained = os.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode),
            "the retained candidate evidence directory was replaced")
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "the exact approved evidence path became a symlink")
        literal = os.fstat(current)
        require_directory_identity(
            (retained.st_dev, retained.st_ino),
            (value.get("directory_device"), value.get("directory_inode")),
            (literal.st_dev, literal.st_ino),
        )
    finally:
        for current in reversed(opened):
            os.close(current)
    return descriptor


@contextlib.contextmanager
def preflight_fresh_outputs(family: str, label: str) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(family, label)
    report_parts, receipt_parts = safe_parts(report), safe_parts(receipt)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "select exactly one owned gzip report and publication receipt")
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        opened.append(current)
        for component in report_parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an exact evidence parent became a symlink")
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise CandidateRecorderError(
                "refusing to overwrite owned candidate evidence: " + basename
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
            "fresh_paths_checked_before_candidate": True,
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
                "a complete streaming evidence encoder produced invalid data")
        yield part.encode("ascii")
    yield b"\n"


def readback_archive(
    preflight: Mapping[str, Any], basename: str,
    expected_gzip: str, expected_plain: str,
    expected_gzip_bytes: int, expected_plain_bytes: int,
) -> None:
    directory = verify_retained_directory(preflight)
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        owner = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(owner.st_mode)
                and (owner.st_dev, owner.st_ino)
                == (named.st_dev, named.st_ino)
                and owner.st_size == expected_gzip_bytes,
                "a lossless published gzip archive was replaced")
        encoded = hashlib.sha256()
        remaining = expected_gzip_bytes
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "a published gzip archive was truncated")
            encoded.update(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b""
                and encoded.hexdigest() == expected_gzip,
                "the complete gzip report was replaced or gained a suffix")
        os.lseek(descriptor, 0, os.SEEK_SET)
        plain = hashlib.sha256()
        count = 0
        with io.FileIO(descriptor, "rb", closefd=False) as file:
            with gzip.GzipFile(fileobj=file, mode="rb") as stream:
                while True:
                    raw = stream.read(131_072)
                    require(type(raw) is bytes,
                            "a lossless compressed report produced invalid bytes")
                    if not raw:
                        break
                    count += len(raw)
                    require(count <= MAX_UNCOMPRESSED_BYTES,
                            "a compressed report exceeded its bounded plain size")
                    plain.update(raw)
        require(count == expected_plain_bytes
                and plain.hexdigest() == expected_plain,
                "a published gzip archive lost or changed its original report")
    finally:
        os.close(descriptor)
    verify_retained_directory(preflight)


def publish_document(
    preflight: Mapping[str, Any], document: Mapping[str, Any],
    *, compressed: bool,
) -> dict[str, Any]:
    kind = "report" if compressed else "receipt"
    basename = preflight[kind + "_basename"]
    directory = verify_retained_directory(preflight)
    temporary = (
        ".rebar-managed-buffer-candidate-v1-" + basename + "-"
        + str(os.getpid())
    )
    safe_parts(temporary)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    identity: tuple[int, int] | None = None
    linked = False
    plain_sha = hashlib.sha256()
    plain_bytes = 0
    write_calls = 0
    try:
        original = os.fstat(descriptor)
        require(stat.S_ISREG(original.st_mode),
                "an owned candidate publication temporary is not regular")
        identity = (original.st_dev, original.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "a fresh candidate publication temporary was substituted")
        if compressed:
            with io.FileIO(descriptor, "wb", closefd=False) as output:
                with gzip.GzipFile(
                    filename="", fileobj=output, mode="wb",
                    compresslevel=9, mtime=0,
                ) as archive:
                    for piece in iter_canonical(document):
                        plain_bytes += len(piece)
                        require(plain_bytes <= MAX_UNCOMPRESSED_BYTES,
                                "a complete candidate report exceeds its bound")
                        plain_sha.update(piece)
                        archive.write(piece)
                        write_calls += 1
        else:
            for piece in iter_canonical(document):
                plain_bytes += len(piece)
                require(plain_bytes <= MAX_SOURCE_BYTES,
                        "a compact publication receipt exceeds its bound")
                plain_sha.update(piece)
                offset = 0
                while offset < len(piece):
                    count = os.write(descriptor, piece[offset:])
                    require(type(count) is int and count > 0,
                            "the complete candidate receipt was truncated")
                    offset += count
                    write_calls += 1
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        require(0 < actual.st_size <= MAX_ARCHIVE_BYTES,
                "the complete candidate gzip or receipt exceeds its bound")
        os.lseek(descriptor, 0, os.SEEK_SET)
        # O_WRONLY cannot be read; authenticate by an independent no-follow fd.
        verify_retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the complete owned publication changed before its atomic link")
        reader = os.open(temporary, regular_flags(), dir_fd=directory)
        try:
            encoded_sha = hashlib.sha256()
            remaining = actual.st_size
            while remaining:
                block = os.read(reader, min(remaining, 1_048_576))
                require(type(block) is bytes and bool(block),
                        "an atomic publication temporary was truncated")
                encoded_sha.update(block)
                remaining -= len(block)
            require(os.read(reader, 1) == b"",
                    "an atomic publication temporary gained a hidden suffix")
        finally:
            os.close(reader)
        os.link(temporary, basename, src_dir_fd=directory,
                dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        os.fsync(directory)
        verify_retained_directory(preflight)
        destination = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((destination.st_dev, destination.st_ino) == identity,
                "the atomic no-clobber publication was substituted")
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
            except (OSError, CandidateRecorderError):
                pass
        raise
    finally:
        os.close(descriptor)
    result = {
        "path": preflight[kind + "_relative"],
        "bytes": actual.st_size,
        "sha256": encoded_sha.hexdigest(),
        "uncompressed_bytes": plain_bytes,
        "uncompressed_sha256": plain_sha.hexdigest(),
        "compression": "gzip-mtime-zero-level-9" if compressed else "none",
        "actual_write_calls": write_calls,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True,
        "owned_temporary_removed": True,
        "complete_readback_verified": True,
    }
    if compressed:
        readback_archive(preflight, basename, result["sha256"],
                         result["uncompressed_sha256"], result["bytes"],
                         result["uncompressed_bytes"])
    else:
        require(result["sha256"] == result["uncompressed_sha256"]
                and result["bytes"] == result["uncompressed_bytes"],
                "a compact receipt was compressed or substituted")
        directory = verify_retained_directory(preflight)
        reader = os.open(basename, regular_flags(), dir_fd=directory)
        try:
            actual_raw = b""
            while len(actual_raw) < result["bytes"]:
                block = os.read(reader, min(1_048_576,
                                            result["bytes"] - len(actual_raw)))
                require(bool(block), "a durable receipt was truncated")
                actual_raw += block
            require(os.read(reader, 1) == b""
                    and actual_raw == canonical(dict(document)),
                    "the exact compact receipt was substituted")
        finally:
            os.close(reader)
    verify_retained_directory(preflight)
    return result


def build_complete_report(
    pins: OwnerPins, label: str, process: Mapping[str, Any],
    matrix: list[dict[str, Any]], receipt: Mapping[str, Any],
    reference: Mapping[str, Any], before: Mapping[str, Any],
    after: Mapping[str, Any] | None, *, managed: Any | None = None,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    validate_label(label)
    validate_matrix(matrix)
    validate_baseline_receipt(receipt)
    validate_baseline_archive(reference, matrix, receipt, managed)
    raw_stdout, raw_stderr = process.get("stdout"), process.get("stderr")
    stdout = capture_stream(raw_stdout, "complete candidate stdout")
    stderr = capture_stream(raw_stderr, "complete candidate stderr")
    failures: list[str] = []
    candidate: dict[str, Any] | None = None
    decoded: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append("the genuine owned candidate could not start: "
                        + str(process.get("spawn_error")))
    if process.get("timed_out") is True:
        failures.append("the genuine owned candidate exceeded its safe timeout")
    if raw_stdout:
        try:
            decoded = decode_document(raw_stdout, "isolated native candidate")
            candidate = validate_worker(
                decoded, pins, matrix, expected_pid=process.get("pid"),
                managed=managed,
            )
        except (CandidateRecorderError, ValueError, TypeError, KeyError) as error:
            failures.append("invalid complete candidate observation: " + str(error))
    if candidate is None:
        failures.append("all candidate outcomes remain unknown")
    if raw_stderr:
        failures.append("the genuine isolated candidate emitted complete stderr")
    if process.get("returncode") != (0 if candidate is not None and not raw_stderr else 1):
        failures.append("the genuine candidate crashed, timed out, or returned a wrong exit")
    if post_run_error is not None:
        failures.append("post-run owner authentication failed: " + post_run_error)
    if before != after:
        failures.append("the complete owned source closure changed during execution")
    by_group = {group: 0 for group in GROUPS}
    mismatches: list[dict[str, Any]] | None = None
    if candidate is not None:
        mismatches = []
        for row, original, actual in zip(
            matrix, reference["reference_a_records"], candidate["records"],
            strict=True,
        ):
            require(row["case"] == original["case"] == actual["case"]
                    and row["group"] == original["group"] == actual["group"],
                    "a complete baseline-to-candidate comparison was reordered")
            if original["outcome"] != actual["outcome"]:
                by_group[row["group"]] += 1
                mismatches.append({
                    "case": row["case"], "group": row["group"],
                    "input": row,
                    "baseline_outcome": original["outcome"],
                    "candidate_outcome": actual["outcome"],
                })
        if mismatches:
            failures.append("the genuine candidate differs on "
                            + str(len(mismatches)) + " frozen cases")
    return {
        "schema": SCHEMA + "-complete-candidate-report",
        "status": "FAIL" if failures else "PASS",
        "python": "3.14.6", "candidate_family": spec.name,
        "label": label,
        "recorder_source_sha256": pins.recorder,
        "managed_oracle_relative": MANAGED_RELATIVE,
        "managed_oracle_sha256": MANAGED_SHA256,
        "baseline_recorder_relative": BASELINE_RECORDER_RELATIVE,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS), "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT, "groups": list(GROUPS),
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": reference["baseline_reference_pids"],
        "candidate_owner_before": dict(before),
        "candidate_owner_after": dict(after) if after is not None else None,
        "candidate_owner_unchanged": before == after,
        "complete_candidate_process_stdout": stdout,
        "complete_candidate_process_stderr": stderr,
        "complete_decoded_candidate_process": decoded,
        "complete_candidate_result": candidate,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": (
            len(candidate["records"]) if candidate is not None else None
        ),
        "candidate_records_sha256": (
            candidate["records_sha256"] if candidate is not None else None
        ),
        "candidate_records": candidate["records"] if candidate else None,
        "baseline_records": reference["reference_a_records"],
        "mismatch_count": len(mismatches) if mismatches is not None else None,
        "all_mismatches": mismatches,
        "mismatches_by_group": by_group if mismatches is not None else None,
        "all_mismatches_preserved": True if mismatches is not None else None,
        "matcher_guard": candidate["matcher_guard"] if candidate else None,
        "actual_method_guard_checks": (
            candidate["matcher_guard"]["actual_method_guard_checks"]
            if candidate else None
        ),
        "actual_warning_registry_guard_checks": (
            candidate["matcher_guard"]["actual_warning_registry_guard_checks"]
            if candidate else None
        ),
        "actual_reference_workers": 0,
        "validated_prior_reference_workers": 2,
        "actual_candidate_workers": 1 if candidate else None,
        "actual_candidate_imports": (
            candidate["actual_candidate_imports"] if candidate else None
        ),
        "actual_candidate_process_invocations": int(process.get("started") is True),
        "actual_candidate_pid": process.get("pid"),
        "actual_candidate_process_returncode": process.get("returncode"),
        "actual_candidate_process_signal": process.get("signal"),
        "actual_candidate_process_timed_out": process.get("timed_out") is True,
        "actual_candidate_process_spawn_error": process.get("spawn_error"),
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def make_receipt(
    pins: OwnerPins, label: str, report: Mapping[str, Any],
    publication: Mapping[str, Any], preflight: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "candidate_result_status": report["status"],
        "python": "3.14.6", "candidate_family": pins.family,
        "label": label,
        "recorder_source_sha256": pins.recorder,
        "managed_oracle_sha256": MANAGED_SHA256,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_baseline_record_count": report["validated_baseline_record_count"],
        "validated_candidate_record_count": report["validated_candidate_record_count"],
        "candidate_records_sha256": report["candidate_records_sha256"],
        "mismatch_count": report["mismatch_count"],
        "mismatches_by_group": report["mismatches_by_group"],
        "all_mismatches_preserved": report["all_mismatches_preserved"],
        "actual_method_guard_checks": report["actual_method_guard_checks"],
        "actual_warning_registry_guard_checks": (
            report["actual_warning_registry_guard_checks"]
        ),
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_candidate_imports": report["actual_candidate_imports"],
        "actual_candidate_process_invocations": (
            report["actual_candidate_process_invocations"]
        ),
        "candidate_owner_before": report["candidate_owner_before"],
        "candidate_owner_after": report["candidate_owner_after"],
        "candidate_owner_unchanged": report["candidate_owner_unchanged"],
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
        "report_atomic_no_overwrite_link": (
            publication["atomic_no_overwrite_link"]
        ),
        "report_complete_readback_verified": (
            publication["complete_readback_verified"]
        ),
        "receipt_relative": preflight["receipt_relative"],
        "approved_fresh_path_count": preflight["approved_fresh_path_count"],
        "fresh_paths_checked_before_candidate": (
            preflight["fresh_paths_checked_before_candidate"]
        ),
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def record_candidate(pins: OwnerPins, label: str) -> dict[str, Any]:
    verify_runtime()
    spec = family_spec(pins.family)
    validate_label(label)
    managed, _, v5, matrix, _ = authenticate_prerequisites(pins)
    receipt, _ = authenticate_baseline_receipt()
    reference, _ = stream_baseline_archive(matrix, receipt, managed)
    before = authenticate_family_closure(v5, pins)
    with preflight_fresh_outputs(spec.name, label) as preflight:
        process = run_one_candidate_worker(pins)
        verify_retained_directory(preflight)
        after: dict[str, dict[str, Any]] | None = None
        post_run_error: str | None = None
        try:
            after = authenticate_family_closure(v5, pins)
            authenticate_prerequisites(pins)
        except (OSError, CandidateRecorderError) as error:
            post_run_error = str(error)
        report = build_complete_report(
            pins, label, process, matrix, receipt, reference, before, after,
            managed=managed, post_run_error=post_run_error,
        )
        report_publication = publish_document(preflight, report, compressed=True)
        receipt_document = make_receipt(
            pins, label, report, report_publication, preflight,
        )
        receipt_publication = publish_document(
            preflight, receipt_document, compressed=False,
        )
    verify_runtime()
    return {
        "schema": SCHEMA + "-recorded", "status": report["status"],
        "publication_status": "PASS", "candidate_family": spec.name,
        "label": label, "matrix_sha256": MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": report["validated_candidate_record_count"],
        "mismatch_count": report["mismatch_count"],
        "report_publication": report_publication,
        "receipt_publication": receipt_publication,
        "actual_candidate_process_invocations": (
            report["actual_candidate_process_invocations"]
        ),
        "all_failure_reasons": report["all_failure_reasons"],
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


class SourceOnlyBoundary:
    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "file_reads": 0, "file_writes": 0, "processes": 0,
            "candidate_imports": 0, "dynamic_imports": 0,
            "clock_samples": 0, "threads": 0,
            "garbage_collections": 0, "directory_syncs": 0,
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        self.originals.append((owner, name, getattr(owner, name)))

        def denied(*args: Any, **kwargs: Any) -> Any:
            actual = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if type(mode) is str and any(letter in mode for letter in "wax+"):
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
            raise SourceOnlyError("source-only controls cannot perform " + actual)

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        for owner, name, category in (
            (builtins, "open", "file_reads"), (io, "open", "file_reads"),
            (os, "open", "file_reads"), (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"), (os, "scandir", "file_reads"),
            (os, "listdir", "file_reads"), (os, "readlink", "file_reads"),
            (os, "replace", "file_writes"), (os, "rename", "file_writes"),
            (os, "link", "file_writes"), (os, "unlink", "file_writes"),
            (os, "mkdir", "file_writes"), (os, "makedirs", "file_writes"),
            (os, "fsync", "directory_syncs"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"), (os, "system", "processes"),
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


def synthetic_owner(relative: str, expected: str, index: int) -> dict[str, Any]:
    return {"relative": relative, "sha256": expected,
            "bytes": 4096 + index, "device": 7, "inode": 8000 + index}


def synthetic_pins(family: str) -> OwnerPins:
    spec = family_spec(family)
    adapter = "12" * 32
    engine = "34" * 32
    bridge = engine if family == "c" else "56" * 32
    raw = [
        path + "=" + (adapter if path == spec.adapter_relative
                       else hashlib.sha256(path.encode("ascii")).hexdigest())
        for path in spec.owned_source_relatives
    ]
    return make_owner_pins(family, "78" * 32, adapter, engine, bridge, raw)


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "case": row["case"], "group": row["group"],
        "variant": row["variant"],
        "outcome": {
            "status": "return", "stage": "synthetic-only",
            "value": {"type": "none"}, "exception": None,
            "events": [], "checkpoints": [], "callbacks": [], "warnings": [],
        },
    } for row in matrix]


def synthetic_guard(spec: FamilySpec) -> dict[str, Any]:
    result = {field: True for field in GUARD_TRUE_FIELDS}
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


def synthetic_receipt() -> dict[str, Any]:
    return {
        "schema": (
            "rebar-independent-managed-buffer-lifetime-v1-recorder"
            "-durable-publication-receipt"
        ),
        "status": "PASS", "baseline_result_status": "PASS",
        "label": "shared-suite-v1", "python": "3.14.6",
        "oracle_relative": MANAGED_RELATIVE,
        "oracle_source_sha256": MANAGED_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS), "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_reference_pids": [82, 83],
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "report_relative": BASELINE_REPORT_RELATIVE,
        "report_sha256": BASELINE_REPORT_SHA256,
        "report_bytes": BASELINE_REPORT_BYTES,
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_baseline": True,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def synthetic_baseline(
    matrix: list[dict[str, Any]], receipt: Mapping[str, Any],
) -> dict[str, Any]:
    records = synthetic_records(matrix)
    records_hash = digest(records)
    return {
        "schema": (
            "rebar-independent-managed-buffer-lifetime-v1-recorder"
            "-complete-baseline-report"
        ),
        "status": "PASS", "label": "shared-suite-v1", "python": "3.14.6",
        "oracle_source_sha256": MANAGED_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS), "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT, "groups": list(GROUPS),
        "source_closure_before": {"synthetic": True},
        "source_closure_after": {"synthetic": True},
        "source_closure_unchanged": True,
        # Never substitute a synthetic vector for the real archived baseline.
        "baseline_records_sha256": records_hash,
        "baseline_reference_pids": list(receipt["baseline_reference_pids"]),
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "reference_a_records": records, "reference_b_records": records,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def synthetic_worker(
    pins: OwnerPins, matrix: list[dict[str, Any]], *, pid: int = 81001,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    records = synthetic_records(matrix)
    closure = {
        path: synthetic_owner(path, expected, index)
        for index, (path, expected) in enumerate(pins.owned_sources, start=1)
    }
    for index, (path, expected) in enumerate((
        (spec.engine_relative, pins.engine),
        (spec.bridge_relative, pins.bridge),
    ), start=100):
        if path not in closure:
            closure[path] = synthetic_owner(path, expected, index)
    native = {
        "source": closure[spec.adapter_relative],
        "native_engine": closure[spec.engine_relative],
        "native_bridge": closure[spec.bridge_relative],
    }
    sources = {
        "recorder": synthetic_owner(SOURCE_RELATIVE, pins.recorder, 301),
        "managed_oracle": synthetic_owner(MANAGED_RELATIVE,
                                           MANAGED_SHA256, 302),
        "baseline_recorder": synthetic_owner(
            BASELINE_RECORDER_RELATIVE, BASELINE_RECORDER_SHA256, 303,
        ),
        "original_v5": synthetic_owner(V5_RELATIVE, V5_SHA256, 304),
    }
    archive_owner = synthetic_owner(
        BASELINE_ARCHIVE_RELATIVE, BASELINE_ARCHIVE_SHA256, 401,
    )
    archive_owner["bytes"] = BASELINE_ARCHIVE_BYTES
    return {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED", "python": "3.14.6",
        "role": "candidate-" + spec.name, "candidate_family": spec.name,
        "pid": pid, "recorder_source_sha256": pins.recorder,
        "managed_oracle_relative": MANAGED_RELATIVE,
        "managed_oracle_sha256": MANAGED_SHA256,
        "baseline_recorder_relative": BASELINE_RECORDER_RELATIVE,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_relative": V5_RELATIVE, "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT, "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP, "groups": list(GROUPS),
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": [82, 83],
        "baseline_receipt_owner": synthetic_owner(
            BASELINE_RECEIPT_RELATIVE, BASELINE_RECEIPT_SHA256, 400,
        ),
        "baseline_archive_owner": archive_owner,
        "source_provenance": sources,
        "native_provenance": native,
        "owned_source_closure": closure,
        "matcher_guard": synthetic_guard(spec),
        "records_sha256": digest(records), "records": records,
        "actual_reference_workers": 0, "actual_candidate_workers": 1,
        "actual_candidate_imports": 3,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "evidence_files_created": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def synthetic_stream_extract(
    raw: bytes, selected: frozenset[str], *, corrupt_crc: bool = False,
) -> tuple[dict[str, Any], int, str]:
    require(type(raw) is bytes and type(selected) is frozenset,
            "an exact in-memory gzip control is mandatory")
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    if corrupt_crc:
        require(len(compressed) >= 8,
                "a real in-memory gzip trailer is mandatory")
        compressed = compressed[:-8] + bytes((compressed[-8] ^ 1,)) \
            + compressed[-7:]
    with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as source:
        parser = StreamingJsonObject(source)
        result = parser.select(selected)
    return result, parser.bytes, parser.sha256.hexdigest()


def source_self_test() -> dict[str, Any]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "run synthetic-only controls under isolated pinned CPython")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate escaped into synthetic-only proof controls")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a distinct synthetic candidate control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a distinct synthetic candidate poison was duplicated")
        try:
            action()
        except (CandidateRecorderError, OSError, TypeError,
                ValueError, KeyError, OverflowError):
            rejected.append(name)
            return
        raise CandidateRecorderError(
            "a forged synthetic candidate control was accepted: " + name
        )

    with SourceOnlyBoundary() as blocked:
        streaming_document = {
            "kept": [
                {"type": "str", "value": "e\u0301 \ud800 😀"},
                {"type": "int", "value": 1024},
            ],
            "number": 108_978_141,
            "skipped": {
                "escaped": "quote \\\" and nested } ]",
                "large": "x" * 350_000,
                "nested": [{"a": [True, None, {"b": "escaped\\n"}]}],
            },
            "tail": {"digest": BASELINE_REPORT_SHA256},
        }
        streaming_raw = canonical(streaming_document)
        selected_names = frozenset({"kept", "number", "tail"})
        streamed, plain_count, plain_sha = synthetic_stream_extract(
            streaming_raw, selected_names,
        )
        accept("stream-authenticated-in-memory-gzip-without-archive-reads",
               streamed == {
                   "kept": streaming_document["kept"],
                   "number": streaming_document["number"],
                   "tail": streaming_document["tail"],
               })
        accept("preserve-every-original-streamed-archive-byte-and-sha256",
               plain_count == len(streaming_raw)
               and plain_sha == hashlib.sha256(streaming_raw).hexdigest())
        accept("skip-a-large-nested-json-subtree-with-bounded-streaming",
               len(streaming_document["skipped"]["large"]) > 262_144
               and "skipped" not in streamed)
        accept("preserve-surrogates-and-unicode-in-streamed-evidence",
               streamed["kept"][0]["value"] == "e\u0301 \ud800 😀")
        accept("stream-the-exact-canonical-evidence-encoder-without-files",
               b"".join(iter_canonical(streaming_document)) == streaming_raw)
        accept("produce-deterministic-mtime-zero-lossless-gzip-in-memory",
               gzip.compress(streaming_raw, compresslevel=9, mtime=0)
               == gzip.compress(streaming_raw, compresslevel=9, mtime=0))

        reject("reject-a-truncated-streamed-json-value",
               lambda: synthetic_stream_extract(
                   streaming_raw[:-4], selected_names,
               ))
        reject("reject-a-duplicate-streamed-top-level-key",
               lambda: synthetic_stream_extract(
                   b'{"kept":1,"kept":2}\n', frozenset({"kept"}),
               ))
        reject("reject-a-missing-mandatory-streamed-archive-value",
               lambda: synthetic_stream_extract(
                   streaming_raw, frozenset({"kept", "missing"}),
               ))
        reject("reject-a-hidden-streamed-archive-json-suffix",
               lambda: synthetic_stream_extract(
                   streaming_raw + b"{}", selected_names,
               ))
        reject("reject-an-invalid-skipped-streaming-scalar",
               lambda: synthetic_stream_extract(
                   b'{"kept":1,"skip":invalid}\n', frozenset({"kept"}),
               ))
        reject("reject-unbalanced-skipped-streaming-containers",
               lambda: synthetic_stream_extract(
                   b'{"kept":1,"skip":[1,2}\n', frozenset({"kept"}),
               ))
        reject("reject-a-losslessly-corrupted-gzip-crc",
               lambda: synthetic_stream_extract(
                   streaming_raw, selected_names, corrupt_crc=True,
               ))

        matrix = build_frozen_matrix()
        accept("reproduce-the-exact-independent-1024-case-frozen-matrix",
               validate_matrix(matrix) is matrix)
        accept("preserve-all-32-independently-seeded-case-groups",
               len(GROUPS) == 32 and all(
                   sum(case["group"] == group for case in matrix) == 32
                   for group in GROUPS
               ))
        accept("pin-the-exact-full-case-matrix-without-loading-the-oracle",
               digest(matrix) == MATRIX_SHA256)
        accept("preserve-the-exact-unrounded-large-published-seed",
               all(type(case["seed"]) is int
                   and case["seed"] == PUBLISHED_SEED for case in matrix))
        accept("retain-every-independent-regex-and-scanner-api",
               {case["operation"] for case in matrix} == set(ALL_APIS))
        accept("authenticate-the-exact-published-two-reference-receipt-shape",
               validate_baseline_receipt(synthetic_receipt())
               ["baseline_records_sha256"] == BASELINE_RECORDS_SHA256)
        accept("pin-the-exact-lossless-109mb-baseline-before-candidate-work",
               BASELINE_REPORT_BYTES == 108_978_141
               and BASELINE_ARCHIVE_BYTES == 4_374_362)

        for name in ("rust", "c", "zig"):
            pins = synthetic_pins(name)
            spec = family_spec(name)
            accept("authenticate-independent-" + name + "-source-closure",
                   isinstance(pins, OwnerPins)
                   and pins.family == name
                   and set(path for path, _ in pins.owned_sources)
                   == set(spec.owned_source_relatives))
            accept("validate-real-synthetic-" + name + "-guard",
                   validate_guard(synthetic_guard(spec), spec)
                   ["actual_method_guard_checks"] == 2048)
            worker = synthetic_worker(pins, matrix)
            accept("validate-complete-synthetic-" + name + "-native-worker",
                   validate_worker(worker, pins, matrix, expected_pid=81001)
                   is worker)
            report, receipt_path = approved_paths(name, "synthetic-proof")
            accept("restrict-" + name + "-to-exact-streamed-gzip-and-receipt",
                   report.endswith(
                       name + "-managed-buffer-lifetime-v1-synthetic-proof.json.gz"
                   ) and receipt_path.endswith(
                       name + "-managed-buffer-lifetime-v1-synthetic-proof"
                       + "-publication-receipt.json"
                   ) and report != receipt_path)

            for field, replacement in (
                ("schema", "foreign"),
                ("status", "PASS"),
                ("role", "candidate-foreign"),
                ("candidate_family", "foreign"),
                ("pid", 0),
                ("recorder_source_sha256", "cd" * 32),
                ("managed_oracle_sha256", "cd" * 32),
                ("baseline_recorder_sha256", "cd" * 32),
                ("original_v5_sha256", "cd" * 32),
                ("matrix_sha256", "cd" * 32),
                ("published_seed", PUBLISHED_SEED + 1),
                ("case_count", CASE_COUNT - 1),
                ("baseline_receipt_sha256", "cd" * 32),
                ("baseline_archive_sha256", "cd" * 32),
                ("baseline_uncompressed_report_sha256", "cd" * 32),
                ("baseline_uncompressed_report_bytes", BASELINE_REPORT_BYTES - 1),
                ("baseline_records_sha256", "cd" * 32),
                ("actual_reference_workers", 1),
                ("actual_candidate_workers", 0),
                ("actual_candidate_imports", 0),
                ("clock_samples", 1),
                ("timing_trials_run", 1),
                ("workspace_files_written", 1),
                ("evidence_files_created", 1),
                ("benchmark_files_read", 1),
                ("hidden_cases_read", 1),
                ("performance", "faster"),
                ("candidate_qualified_for_hidden_benchmark", True),
                ("final_winner_selected", True),
                ("records_sha256", "cd" * 32),
            ):
                forged = dict(worker)
                forged[field] = replacement
                reject("reject-" + name + "-forged-worker-" + field,
                       lambda forged=forged, pins=pins:
                       validate_worker(forged, pins, matrix, expected_pid=81001))

            for field, replacement in (
                ("public_type_names_used_for_ownership", True),
                ("actual_method_guard_checks", 2047),
                ("actual_warning_registry_guard_checks", 2047),
                ("owned_native_ffi_allowed", not spec.owned_ctypes),
                ("trusted_stdlib_ctypes_preloaded", not spec.owned_ctypes),
                ("trusted_stdlib_ctypes_builtin_verified", not spec.owned_ctypes),
                ("trusted_stdlib_ctypes_pythonapi_initialized", not spec.owned_ctypes),
                ("trusted_stdlib_ctypes_source_sha256", "cd" * 32),
                ("cached_original_matcher_descendant_count", -1),
                ("cached_original_holder_count", -1),
                ("owned_ctypes_load_count", -1),
                ("owned_ctypes_symbol_count", -1),
            ):
                guard = synthetic_guard(spec)
                guard[field] = replacement
                reject("reject-" + name + "-forged-continuous-guard-" + field,
                       lambda guard=guard, spec=spec:
                       validate_guard(guard, spec))
            for field in GUARD_TRUE_FIELDS:
                guard = synthetic_guard(spec)
                guard[field] = False
                reject("reject-" + name + "-lost-" + field,
                       lambda guard=guard, spec=spec:
                       validate_guard(guard, spec))

        for index, value in enumerate((
            None, True, 1, "", "UPPER", "white space", ".", "..",
            "../escape", "/absolute", "a/b", "a\\b", "nul\x00byte",
            "double--dash", "-leading", "trailing-", "a" * 65,
        )):
            reject("reject-escaping-publication-label-" + format(index, "02d"),
                   lambda value=value: approved_paths("c", value))

        for index, value in enumerate((
            None, True, 1, "", ".", "..", "/absolute", "a//b", "a/../b",
            "a/./b", "a\\b", "a\x00b",
        )):
            reject("reject-escaping-no-follow-source-" + format(index, "02d"),
                   lambda value=value: safe_parts(value))

        reject("reject-an-omitted-independent-case",
               lambda: validate_matrix(matrix[:-1]))
        reject("reject-an-added-independent-case",
               lambda: validate_matrix(matrix + [matrix[0]]))
        reject("reject-reordered-independent-cases",
               lambda: validate_matrix(list(reversed(matrix))))
        reject("reject-a-substituted-independent-seed",
               lambda: validate_matrix(build_frozen_matrix(PUBLISHED_SEED + 1)))
        for field, replacement in (
            ("case", "managed-buffer-lifetime.v1.9999"),
            ("group", GROUPS[-1]), ("variant", 33),
            ("seed", PUBLISHED_SEED + 1), ("flags", -1),
            ("operation", "candidate.alias"), ("action", "forged"),
        ):
            forged_matrix = list(matrix)
            forged_row = dict(forged_matrix[0])
            forged_row[field] = replacement
            forged_matrix[0] = forged_row
            reject("reject-substituted-source-ordered-case-" + field,
                   lambda forged_matrix=forged_matrix:
                   validate_matrix(forged_matrix))

        receipt = synthetic_receipt()
        reject("reject-synthetic-reference-vectors-as-authentic-baseline-data",
               lambda: validate_baseline_archive(
                   synthetic_baseline(matrix, receipt), matrix, receipt,
               ))
        for field, replacement in (
            ("schema", "foreign"), ("status", "FAIL"),
            ("baseline_result_status", "FAIL"), ("label", "foreign"),
            ("python", "3.14.5"), ("oracle_relative", "tools/foreign.py"),
            ("oracle_source_sha256", "cd" * 32),
            ("matrix_sha256", "cd" * 32),
            ("published_seed", PUBLISHED_SEED + 1),
            ("group_count", 31), ("cases_per_group", 31),
            ("case_count", CASE_COUNT - 1),
            ("baseline_records_sha256", "cd" * 32),
            ("validated_reference_a_case_count", CASE_COUNT - 1),
            ("validated_reference_b_case_count", CASE_COUNT - 1),
            ("actual_reference_workers", 1),
            ("actual_candidate_workers", 1),
            ("actual_candidate_imports", 1),
            ("actual_baseline_controller_invocations", 0),
            ("report_relative", "experiments/foreign.json"),
            ("report_sha256", "cd" * 32),
            ("report_bytes", BASELINE_REPORT_BYTES - 1),
            ("report_file_fsync_completed", False),
            ("report_directory_fsync_completed", False),
            ("report_atomic_no_overwrite_link", False),
            ("report_complete_readback_verified", False),
            ("receipt_relative", "experiments/foreign.json"),
            ("approved_fresh_path_count", 1),
            ("fresh_paths_checked_before_baseline", False),
            ("clock_samples", 1), ("timing_trials_run", 1),
            ("benchmark_files_read", 1), ("hidden_cases_read", 1),
            ("performance", "faster"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
        ):
            forged = dict(receipt)
            forged[field] = replacement
            reject("reject-forged-immutable-baseline-receipt-" + field,
                   lambda forged=forged: validate_baseline_receipt(forged))

        reject("reject-duplicate-controller-json",
               lambda: decode_document(b'{"x":1,"x":2}\n', "duplicate"))
        reject("reject-noncanonical-controller-json",
               lambda: decode_document(b'{ "x": 1 }\n', "noncanonical"))
        reject("reject-nonfinite-controller-json",
               lambda: decode_document(b'{"x":NaN}\n', "nonfinite"))

        reject("block-evidence-and-holdout-source-reads",
               lambda: builtins.open("performance/holdout.json", "rb"))
        reject("block-durable-candidate-report-writes",
               lambda: builtins.open("synthetic-candidate.json.gz", "wb"))
        reject("block-all-workspace-directory-enumeration",
               lambda: os.scandir("experiments"))
        reject("block-all-workspace-evidence-status",
               lambda: os.stat("experiments"))
        reject("block-all-no-clobber-publication-links",
               lambda: os.link("synthetic-old", "synthetic-new"))
        reject("block-all-publication-replacements",
               lambda: os.replace("synthetic-old", "synthetic-new"))
        reject("block-all-file-and-directory-syncs",
               lambda: os.fsync(100))
        reject("block-all-independent-candidate-imports",
               lambda: importlib.import_module("candidates.zig_candidate"))
        reject("block-all-original-guard-dynamic-imports",
               lambda: importlib.import_module(V5_MODULE))
        reject("block-all-actual-native-worker-processes",
               lambda: subprocess.Popen([PINNED_PYTHON, "-I", "-B"]))
        reject("block-all-background-worker-threads",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-all-performance-timing",
               lambda: time.perf_counter())
        reject("block-all-wall-clock-sampling", lambda: time.time())
        reject("block-all-garbage-collection", lambda: gc.collect())

        require(len(accepted) >= 16 and len(rejected) >= 150,
                "prove at least 150 distinct synthetic no-delegation controls")
        require(blocked.blocked["file_reads"] >= 3
                and blocked.blocked["file_writes"] >= 3
                and blocked.blocked["processes"] >= 1
                and blocked.blocked["candidate_imports"] >= 1
                and blocked.blocked["dynamic_imports"] >= 1
                and blocked.blocked["clock_samples"] >= 2
                and blocked.blocked["threads"] >= 1
                and blocked.blocked["garbage_collections"] >= 1
                and blocked.blocked["directory_syncs"] >= 1,
                "exercise every exact no-effect isolation denial")

    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a genuine candidate escaped synthetic-only recording controls")
    return {
        "schema": SCHEMA + "-synthetic-self-test", "status": "PASS",
        "python": "3.14.6", "managed_oracle_sha256": MANAGED_SHA256,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_sha256": V5_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "group_count": len(GROUPS), "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "accepted_count": len(accepted), "rejected_count": len(rejected),
        "accepted_controls": accepted, "rejected_controls": rejected,
        "blocked_effect_attempts": dict(blocked.blocked),
        "actual_baseline_archive_reads": 0,
        "actual_baseline_controller_invocations": 0,
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


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Durably record one truly independent managed-buffer candidate",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run in-memory zero-effect attack controls")
    modes.add_argument("--record-candidate", action="store_true",
                       help="record one exact isolated independent candidate")
    modes.add_argument("--internal-candidate-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--candidate", choices=("rust", "c", "zig"))
    parser.add_argument("--label")
    parser.add_argument("--recorder-source-sha256")
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--baseline-receipt-sha256")
    parser.add_argument("--baseline-archive-sha256")
    parser.add_argument("--baseline-records-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(options.candidate is None and options.label is None
                    and options.recorder_source_sha256 is None
                    and options.oracle_source_sha256 is None
                    and options.matrix_sha256 is None
                    and options.baseline_receipt_sha256 is None
                    and options.baseline_archive_sha256 is None
                    and options.baseline_records_sha256 is None
                    and options.candidate_source_sha256 is None
                    and options.native_engine_sha256 is None
                    and options.native_bridge_sha256 is None
                    and not options.owned_source_sha256,
                    "synthetic controls cannot authorize actual matching")
            result = source_self_test()
        else:
            require(validate_digest(options.oracle_source_sha256, "managed oracle")
                    == MANAGED_SHA256
                    and validate_digest(options.matrix_sha256, "frozen matrix")
                    == MATRIX_SHA256
                    and validate_digest(options.baseline_receipt_sha256,
                                        "actual baseline receipt")
                    == BASELINE_RECEIPT_SHA256
                    and validate_digest(options.baseline_archive_sha256,
                                        "actual lossless baseline archive")
                    == BASELINE_ARCHIVE_SHA256
                    and validate_digest(options.baseline_records_sha256,
                                        "actual baseline outcome vector")
                    == BASELINE_RECORDS_SHA256,
                    "pin the exact published genuine two-reference baseline")
            pins = make_owner_pins(
                options.candidate,
                options.recorder_source_sha256,
                options.candidate_source_sha256,
                options.native_engine_sha256,
                options.native_bridge_sha256,
                options.owned_source_sha256,
            )
            if options.internal_candidate_worker:
                require(options.label is None,
                        "an isolated worker cannot authorize publication")
                result = execute_candidate_worker(pins)
            else:
                require(options.record_candidate,
                        "select one explicit independently owned candidate")
                result = record_candidate(pins, validate_label(options.label))
        sys.stdout.buffer.write(canonical(result))
        return 0 if result.get("status") in {"PASS", "OBSERVED"} else 1
    except (CandidateRecorderError, OSError, subprocess.SubprocessError,
            TypeError, ValueError, KeyError, UnicodeError) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-complete-failure", "status": "FAIL",
            "error_type": type(error).__qualname__, "error": str(error),
            "managed_oracle_sha256": MANAGED_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
            "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
            "baseline_records_sha256": BASELINE_RECORDS_SHA256,
            "actual_reference_workers": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "benchmark_files_read": 0, "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
