#!/usr/bin/env python3
"""Durably record the independently frozen 2,854-case Scanner oracle.

Source-only controls neither open files nor observe a regular-expression
engine.  Recording a baseline explicitly runs the frozen oracle in an isolated
controller, which itself runs exactly two independent CPython reference
workers.  Recording one candidate separately authenticates the published
baseline, the complete independently owned native source closure, the frozen
V3 ownership policy, and the continuously active V5 no-delegation guard.

Every actual worker byte, scanner callback, warning, mismatch, and failure is
retained in a deterministic, no-clobber, lossless gzip report.  Publication
success is never confused with baseline or candidate correctness.
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
SOURCE_RELATIVE = "tools/record_independent_scanner_verbose_comments_v1.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-scanner-verbose-comments-recorder-v1"
ORACLE_RELATIVE = "tools/independent_scanner_verbose_comments_v1.py"
ORACLE_MODULE = "tools.independent_scanner_verbose_comments_v1"
ORACLE_SCHEMA = "rebar-independent-scanner-verbose-comments-v1"
ORACLE_SHA256 = (
    "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d"
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
    "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b"
)
PUBLISHED_SEED = 0x5343_4E56_4552_5631
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
VERBOSE = 64
SEMANTIC_CASE_COUNT = 2_560
TOKENIZER_CASE_COUNT = 294
CASE_COUNT = 2_854
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_ARCHIVE_BYTES = 96 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
PROCESS_TIMEOUT_SECONDS = 600
COMMENT_PAYLOADS = (
    "(((", "(?P<phantom>q)", "\\8", "(?(99)a|b)", "(?P=missing)",
    "(?x:", "(?-x:", "[unclosed(", ") ((( ???", "\\",
    "# another comment", "(?<=(", "(?<!(", "(?>(",
    "(?P<_phantom>(", "(?#not-really",
)
SEMANTIC_TAILS = (
    ("literal", "a", "a"),
    ("plain_capture", "(a)", "a"),
    ("named_capture", "(?P<real>a)", "a"),
    ("conditional_yes", "(a)?(?(1)b|c)", "ab"),
    ("conditional_no", "(a)?(?(1)b|c)", "c"),
    ("numeric_backreference", "(a)\\1", "aa"),
    ("named_backreference", "(?P<real>a)(?P=real)", "aa"),
    ("inner_verbose_scope", "(?x:a b)", "ab"),
)
SEMANTIC_ENDINGS = (("lf", "\n"), ("crlf", "\r\n"))
SEMANTIC_CONTEXTS = (
    "root_verbose", "global_verbose", "scoped_verbose",
    "nested_enable", "nested_disable",
)
TOKENIZER_ENDINGS = (
    ("none", ""), ("lf", "\n"), ("cr", "\r"), ("crlf", "\r\n"),
    ("lfcr", "\n\r"), ("double_lf", "\n\n"), ("latin1_nel", "\x85"),
)
TOKENIZER_CONTEXTS = ("root", "global", "scoped")
EXPECTED_COUNTS = types.MappingProxyType({
    "full-match": 2_612,
    "continued-comment-empty": 32,
    "prefix-then-fallback": 108,
    "continued-comment-unterminated": 102,
})
EXPECTED_NEGATIVE_COUNTS = types.MappingProxyType({
    "semantic": 48, "tokenizer": 54,
})
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


class CandidateContractViolation(RecorderError):
    """Preserve a genuine Scanner contract failure as a case outcome."""


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
        validate_digest(records, "all 2,854 frozen reference observations"),
    )


def make_owner_pins(
    family: Any, recorder: Any, adapter: Any, engine: Any, bridge: Any,
    sources: Any, baseline: BaselinePins,
) -> OwnerPins:
    spec = family_spec(family)
    require(isinstance(baseline, BaselinePins),
            "an exact previously published baseline is mandatory")
    validate_digest(recorder, "frozen scanner recorder")
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


def encode_subject(value: str | bytes) -> dict[str, str]:
    if type(value) is str:
        return {"kind": "str", "value": value}
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    raise RecorderError("an exact Unicode or bytes carrier is mandatory")


def decode_subject(value: Any, domain: str) -> str | bytes:
    require(type(value) is dict and domain in {"str", "bytes"},
            "an exact Scanner carrier is mandatory")
    if domain == "str":
        require(set(value) == {"kind", "value"}
                and value.get("kind") == "str"
                and type(value.get("value")) is str,
                "a complete Unicode scanner carrier was substituted")
        return value["value"]
    require(set(value) == {"kind", "hex"}
            and value.get("kind") == "bytes"
            and type(value.get("hex")) is str,
            "a complete bytes scanner carrier was substituted")
    try:
        result = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise RecorderError("a Scanner carrier is not canonical hex") from error
    require(result.hex() == value["hex"],
            "a Scanner carrier is not canonical lowercase hex")
    return result


def semantic_contexts(
    payload: str, ending: str, tail: str, subject: str,
) -> tuple[tuple[str, str, int, str], ...]:
    return (
        ("root_verbose", "# " + payload + ending + tail, VERBOSE, subject),
        ("global_verbose", "(?x)# " + payload + ending + tail, 0, subject),
        ("scoped_verbose", "(?x:# " + payload + ending + tail + ")", 0,
         subject),
        ("nested_enable",
         "(?-x:\\#(?x:# " + payload + ending + tail + "))",
         VERBOSE, "#" + subject),
        ("nested_disable",
         "(?x:# " + payload + ending + "(?-x:\\#)(?x:" + tail + "))",
         0, "#" + subject),
    )


def append_case(
    records: list[dict[str, Any]], *, seed: int, cohort: str,
    domain: str, context: str, phrase: str, flags: int, subject: str,
    ending: str, tail: str | None, payload_index: int | None,
    slash_count: int | None, expected: str,
) -> None:
    require(domain in {"str", "bytes"} and expected in EXPECTED_COUNTS,
            "an unfrozen Scanner property case was injected")
    native_phrase: str | bytes
    native_subject: str | bytes
    if domain == "bytes":
        native_phrase, native_subject = (
            phrase.encode("latin1"), subject.encode("latin1")
        )
    else:
        native_phrase, native_subject = phrase, subject
    parts = [cohort, domain, context, ending]
    if payload_index is not None:
        parts.extend((str(payload_index), str(tail)))
    if slash_count is not None:
        parts.append(str(slash_count))
    records.append({
        "case": "/".join(parts), "cohort": cohort, "context": context,
        "domain": domain, "flags": flags,
        "phrase": encode_subject(native_phrase),
        "subject": encode_subject(native_subject),
        "line_ending": ending, "tail": tail,
        "payload_index": payload_index, "slash_count": slash_count,
        "expected_kind": expected, "seed": seed,
    })


def build_frozen_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and seed == PUBLISHED_SEED,
            "the exact frozen 64-bit Scanner seed is mandatory")
    records: list[dict[str, Any]] = []
    for domain in ("str", "bytes"):
        for payload_index, payload in enumerate(COMMENT_PAYLOADS):
            for ending_name, ending in SEMANTIC_ENDINGS:
                for tail_name, tail, subject in SEMANTIC_TAILS:
                    for context, phrase, flags, actual in semantic_contexts(
                        payload, ending, tail, subject,
                    ):
                        slash_count = len(payload) - len(payload.rstrip("\\"))
                        continued = ending_name == "lf" and slash_count % 2 == 1
                        expected = (
                            "continued-comment-empty"
                            if continued and context in {
                                "root_verbose", "global_verbose"
                            }
                            else "continued-comment-unterminated"
                            if continued else "full-match"
                        )
                        append_case(
                            records, seed=seed, cohort="semantic",
                            domain=domain, context=context, phrase=phrase,
                            flags=flags, subject=actual, ending=ending_name,
                            tail=tail_name, payload_index=payload_index,
                            slash_count=None, expected=expected,
                        )
        for slash_count in range(7):
            for ending_name, ending in TOKENIZER_ENDINGS:
                body = "a # " + "\\" * slash_count + ending + "b"
                terminated = (
                    ending_name in {"crlf", "double_lf"}
                    or ending_name in {"lf", "lfcr"}
                    and slash_count % 2 == 0
                )
                for context in TOKENIZER_CONTEXTS:
                    phrase = (
                        body if context == "root"
                        else "(?x)" + body if context == "global"
                        else "(?x:" + body + ")"
                    )
                    expected = (
                        "full-match" if terminated
                        else "continued-comment-unterminated"
                        if context == "scoped"
                        else "prefix-then-fallback"
                    )
                    append_case(
                        records, seed=seed, cohort="tokenizer",
                        domain=domain, context=context, phrase=phrase,
                        flags=VERBOSE if context == "root" else 0,
                        subject="ab", ending=ending_name, tail=None,
                        payload_index=None, slash_count=slash_count,
                        expected=expected,
                    )
    require(len(records) == CASE_COUNT,
            "a complete deterministic Scanner case was omitted")
    random.Random(seed).shuffle(records)
    return records


def validate_matrix(value: Any) -> list[dict[str, Any]]:
    require(type(value) is list and len(value) == CASE_COUNT,
            "all 2,854 frozen source-ordered Scanner cases are mandatory")
    fields = {
        "case", "cohort", "context", "domain", "flags", "phrase",
        "subject", "line_ending", "tail", "payload_index", "slash_count",
        "expected_kind", "seed",
    }
    seen: set[str] = set()
    counts = {name: 0 for name in EXPECTED_COUNTS}
    negative = {"semantic": 0, "tokenizer": 0}
    cohorts = {"semantic": 0, "tokenizer": 0}
    for row in value:
        require(type(row) is dict and set(row) == fields,
                "a complete frozen Scanner case was added or concealed")
        case = row.get("case")
        domain = row.get("domain")
        cohort = row.get("cohort")
        expected = row.get("expected_kind")
        require(type(case) is str and case not in seen
                and domain in {"str", "bytes"} and cohort in cohorts
                and expected in counts and type(row.get("flags")) is int
                and row["flags"] in {0, VERBOSE}
                and type(row.get("seed")) is int
                and row["seed"] == PUBLISHED_SEED,
                "a frozen Scanner case, carrier, flag, or 64-bit seed changed")
        seen.add(case)
        decode_subject(row["phrase"], domain)
        decode_subject(row["subject"], domain)
        cohorts[cohort] += 1
        counts[expected] += 1
        if expected == "continued-comment-unterminated":
            negative[cohort] += 1
        if cohort == "semantic":
            require(row["context"] in SEMANTIC_CONTEXTS
                    and row["line_ending"] in {"lf", "crlf"}
                    and row["tail"] in {item[0] for item in SEMANTIC_TAILS}
                    and type(row["payload_index"]) is int
                    and 0 <= row["payload_index"] < len(COMMENT_PAYLOADS)
                    and row["slash_count"] is None,
                    "a frozen comment, scope, or capture case was hidden")
        else:
            require(row["context"] in TOKENIZER_CONTEXTS
                    and row["line_ending"]
                    in {item[0] for item in TOKENIZER_ENDINGS}
                    and row["tail"] is None
                    and row["payload_index"] is None
                    and type(row["slash_count"]) is int
                    and 0 <= row["slash_count"] <= 6,
                    "a frozen escaped-newline Scanner case was hidden")
    require(cohorts == {
        "semantic": SEMANTIC_CASE_COUNT,
        "tokenizer": TOKENIZER_CASE_COUNT,
    } and counts == dict(EXPECTED_COUNTS)
      and negative == dict(EXPECTED_NEGATIVE_COUNTS)
      and digest(value) == MATRIX_SHA256,
      "the frozen Scanner case counts, errors, source order, or digest changed")
    return value


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
    require(type(maximum) is int and 0 < maximum <= MAX_UNCOMPRESSED_BYTES,
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
    oracle, oracle_owner = authenticate_module(
        ORACLE_MODULE, ORACLE_RELATIVE, ORACLE_SHA256,
    )
    v5, v5_owner = authenticate_module(V5_MODULE, V5_RELATIVE, V5_SHA256)
    audit, audit_owner = authenticate_module(
        AUDIT_MODULE, AUDIT_RELATIVE, AUDIT_SHA256,
    )
    require(getattr(oracle, "SCHEMA", None) == ORACLE_SCHEMA
            and getattr(oracle, "MATRIX_SHA256", None) == MATRIX_SHA256
            and getattr(oracle, "PUBLISHED_SEED", None) == PUBLISHED_SEED
            and getattr(oracle, "CASE_COUNT", None) == CASE_COUNT
            and getattr(oracle, "SEMANTIC_CASE_COUNT", None)
            == SEMANTIC_CASE_COUNT
            and getattr(oracle, "TOKENIZER_CASE_COUNT", None)
            == TOKENIZER_CASE_COUNT
            and getattr(oracle, "V5_GUARD_SHA256", None) == V5_SHA256
            and getattr(oracle, "OWNERSHIP_AUDIT_SHA256", None) == AUDIT_SHA256
            and getattr(v5, "SOURCE_RELATIVE", None) == V5_RELATIVE
            and v5.current_source_sha256() == V5_SHA256
            and getattr(audit, "SOURCE_RELATIVE", None) == AUDIT_RELATIVE,
            "the frozen Scanner oracle or V3/V5 ownership policies changed")
    matrix = validate_matrix(build_frozen_matrix())
    require(oracle.build_matrix() == matrix
            and oracle.validate_matrix(matrix, MATRIX_SHA256) == MATRIX_SHA256,
            "the exact independently frozen 2,854-case matrix changed")
    return oracle, v5, audit, matrix, {
        "recorder": recorder_owner, "scanner_oracle": oracle_owner,
        "original_v5": v5_owner, "from_scratch_audit_v3": audit_owner,
    }


def approved_paths(
    kind: str, label: str, family: str | None = None,
) -> tuple[str, str]:
    validate_label(label)
    require(kind in {"baseline", "candidate"},
            "select only one reference or owned-candidate evidence class")
    if kind == "baseline":
        require(family is None, "a baseline cannot select a candidate")
        slug = "scanner-verbose-comments-v1-" + label
    else:
        spec = family_spec(family)
        slug = spec.name + "-scanner-verbose-comments-v1-" + label
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
            "the retained Scanner evidence directory was replaced")
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
                "refusing to overwrite frozen Scanner evidence: " + basename
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
                "a complete lossless Scanner report was replaced")
        archive_hasher = hashlib.sha256()
        remaining = archive_bytes
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "a published lossless Scanner report was truncated")
            archive_hasher.update(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b""
                and archive_hasher.hexdigest() == expected_archive,
                "a published Scanner archive gained or lost evidence")
        os.lseek(descriptor, 0, os.SEEK_SET)
        plain_hasher = hashlib.sha256()
        count = 0
        with io.FileIO(descriptor, "rb", closefd=False) as source:
            with gzip.GzipFile(fileobj=source, mode="rb") as compressed:
                while True:
                    block = compressed.read(131_072)
                    require(type(block) is bytes,
                            "lossless Scanner evidence produced invalid bytes")
                    if not block:
                        break
                    count += len(block)
                    require(count <= MAX_UNCOMPRESSED_BYTES,
                            "lossless Scanner evidence exceeds its safe bound")
                    plain_hasher.update(block)
        require(count == plain_bytes
                and plain_hasher.hexdigest() == expected_plain,
                "lossless Scanner evidence differs from its original report")
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
        ".rebar-scanner-verbose-recorder-v1-" + basename
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
                "a fresh Scanner evidence temporary is not regular")
        identity = (original.st_dev, original.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "a fresh Scanner evidence temporary was substituted")
        if compressed:
            with io.FileIO(descriptor, "wb", closefd=False) as output:
                with gzip.GzipFile(
                    filename="", fileobj=output, mode="wb",
                    compresslevel=9, mtime=0,
                ) as archive:
                    for piece in iter_canonical(document):
                        plain_bytes += len(piece)
                        require(plain_bytes <= MAX_UNCOMPRESSED_BYTES,
                                "a complete Scanner report exceeds its bound")
                        plain_hasher.update(piece)
                        archive.write(piece)
                        write_calls += 1
        else:
            for piece in iter_canonical(document):
                plain_bytes += len(piece)
                require(plain_bytes <= MAX_SOURCE_BYTES,
                        "a Scanner publication receipt exceeds its bound")
                plain_hasher.update(piece)
                offset = 0
                while offset < len(piece):
                    actual = os.write(descriptor, piece[offset:])
                    require(type(actual) is int and actual > 0,
                            "a complete Scanner receipt was truncated")
                    offset += actual
                    write_calls += 1
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        require(0 < actual.st_size <= MAX_ARCHIVE_BYTES,
                "a complete compressed report or receipt exceeds its bound")
        verify_retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "Scanner evidence changed before its no-clobber publication")
        reader = os.open(temporary, regular_flags(), dir_fd=directory)
        try:
            archive_hasher = hashlib.sha256()
            remaining = actual.st_size
            while remaining:
                block = os.read(reader, min(remaining, 1_048_576))
                require(type(block) is bytes and bool(block),
                        "an authenticated Scanner temporary was truncated")
                archive_hasher.update(block)
                remaining -= len(block)
            require(os.read(reader, 1) == b"",
                    "an authenticated Scanner temporary gained a suffix")
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
                "an atomically published Scanner report was substituted")
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
                "a Scanner receipt was compressed or substituted")
        directory = verify_retained_directory(preflight)
        reader = os.open(basename, regular_flags(), dir_fd=directory)
        try:
            parts: list[bytes] = []
            remaining = result["bytes"]
            while remaining:
                raw = os.read(reader, min(remaining, 1_048_576))
                require(bool(raw), "a durable Scanner receipt was truncated")
                parts.append(raw)
                remaining -= len(raw)
            require(os.read(reader, 1) == b""
                    and b"".join(parts) == canonical(dict(document)),
                    "a durable Scanner receipt differs from its exact source")
        finally:
            os.close(reader)
    verify_retained_directory(preflight)
    return result


def capture_stream(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
            "retain complete bounded worker process bytes: " + label)
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "bytes": len(value), "sha256": hashlib.sha256(value).hexdigest(),
        "complete": True,
    }


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict
            and set(value) == {"base64", "bytes", "sha256", "complete"}
            and type(value.get("base64")) is str
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and value.get("complete") is True,
            "a complete Scanner worker stream was concealed: " + label)
    validate_digest(value.get("sha256"), label)
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise RecorderError("invalid genuine process base64: " + label) from error
    require(len(raw) == value["bytes"]
            and hashlib.sha256(raw).hexdigest() == value["sha256"]
            and base64.b64encode(raw).decode("ascii") == value["base64"],
            "a complete Scanner worker stream was truncated or replaced")
    return raw


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
        "status": "PASS", "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "evidence_files_created": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(type(value) is dict and set(value) == set(expected) | {
        "baseline_records_sha256", "source_owners", "reference_a",
        "reference_b", "reference_a_process", "reference_b_process",
    }, "a complete two-worker frozen baseline was forged")
    for name, actual in expected.items():
        require(value.get(name) == actual,
                "a genuine two-reference baseline changed: " + name)
    validate_digest(value["baseline_records_sha256"],
                    "all source-ordered baseline observations")
    try:
        oracle.validate_source_owners(value["source_owners"], ORACLE_SHA256)
        actual_hash = oracle.validate_reference_pair(
            value["reference_a"], value["reference_b"],
            value["reference_a_process"], value["reference_b_process"],
            source_pin=ORACLE_SHA256, matrix=matrix,
        )
    except Exception as error:
        raise RecorderError(
            "the frozen Scanner oracle rejected its complete independent workers"
        ) from error
    require(actual_hash == value["baseline_records_sha256"]
            and value["source_owners"]
            == value["reference_a"]["source_owners"]
            == value["reference_b"]["source_owners"],
            "the two independently observed Scanner baselines disagree")
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
        "python": "3.14.6", "label": validate_label(label),
        "recorder_relative": SOURCE_RELATIVE,
        "recorder_source_sha256": recorder_pin,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
    }


def build_baseline_report(
    recorder_pin: str, label: str, process: Mapping[str, Any],
    oracle: Any, matrix: list[dict[str, Any]],
    before: Mapping[str, Any], after: Mapping[str, Any] | None,
    *, post_run_error: str | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    raw_stdout, raw_stderr = process.get("stdout"), process.get("stderr")
    stdout = capture_stream(raw_stdout, "complete baseline controller stdout")
    stderr = capture_stream(raw_stderr, "complete baseline controller stderr")
    result: dict[str, Any] | None = None
    decoded: dict[str, Any] | None = None
    structured_failure: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append("the pinned baseline could not start: "
                        + str(process.get("spawn_error")))
    if process.get("timed_out") is True:
        failures.append("the genuine reference controller exceeded its timeout")
    if raw_stdout:
        try:
            decoded = decode_document(raw_stdout, "genuine reference controller")
            if decoded.get("schema") == ORACLE_SCHEMA + "-two-reference-baseline":
                result = validate_baseline_result(decoded, oracle, matrix)
            elif decoded.get("schema") == ORACLE_SCHEMA + "-failure":
                structured_failure = validate_oracle_failure(decoded)
                failures.append("the frozen baseline reported: "
                                + structured_failure["error"])
            else:
                raise RecorderError("an unrecognized reference schema was emitted")
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append("invalid complete baseline observation: " + str(error))
    if result is None:
        failures.append("agreement on all 2,854 reference cases remains unknown")
    if raw_stderr:
        failures.append("the genuine reference controller emitted complete stderr")
    expected_exit = 0 if result is not None and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        failures.append("the reference controller crashed or returned a wrong exit")
    if post_run_error is not None:
        failures.append("post-run source authentication failed: " + post_run_error)
    if before != after:
        failures.append("a frozen source changed during baseline observation")
    first = result.get("reference_a") if result is not None else None
    second = result.get("reference_b") if result is not None else None
    return {
        "schema": SCHEMA + "-complete-baseline-report",
        "status": "FAIL" if failures else "PASS",
        **baseline_source_fields(recorder_pin, label),
        "source_closure_before": dict(before),
        "source_closure_after": dict(after) if after is not None else None,
        "source_closure_unchanged": before == after,
        "complete_baseline_process_stdout": stdout,
        "complete_baseline_process_stderr": stderr,
        "complete_decoded_baseline_process": decoded,
        "complete_baseline_result": result,
        "complete_structured_baseline_failure": structured_failure,
        "complete_reference_worker_failure": (
            structured_failure.get("complete_reference_worker_failure")
            if structured_failure else None
        ),
        "validated_reference_a_case_count": (
            len(first["records"]) if first is not None else None
        ),
        "validated_reference_b_case_count": (
            len(second["records"]) if second is not None else None
        ),
        "baseline_records_sha256": (
            result["baseline_records_sha256"] if result is not None else None
        ),
        "baseline_reference_pids": (
            [first["pid"], second["pid"]] if result is not None else None
        ),
        "reference_a_records": first["records"] if first else None,
        "reference_b_records": second["records"] if second else None,
        "reference_a_process": (
            result["reference_a_process"] if result else None
        ),
        "reference_b_process": (
            result["reference_b_process"] if result else None
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
        "actual_baseline_process_timed_out": process.get("timed_out") is True,
        "actual_baseline_process_spawn_error": process.get("spawn_error"),
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


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
    recorder_pin: str, oracle_pin: str, matrix_pin: str, label: str,
) -> dict[str, Any]:
    verify_runtime()
    validate_digest(recorder_pin, "explicitly frozen Scanner recorder")
    require(validate_digest(oracle_pin, "frozen Scanner oracle") == ORACLE_SHA256
            and validate_digest(matrix_pin, "frozen Scanner matrix")
            == MATRIX_SHA256,
            "pin the exact independently frozen Scanner oracle and matrix")
    oracle, _, _, matrix, before = authenticate_frozen_tools(recorder_pin)
    with preflight_fresh_outputs("baseline", label) as preflight:
        arguments = [
            PINNED_PYTHON, "-I", "-B", ROOT + "/" + ORACLE_RELATIVE,
            "--baseline", "--oracle-source-sha256", ORACLE_SHA256,
            "--matrix-sha256", MATRIX_SHA256,
        ]
        process = run_one_process(arguments)
        verify_retained_directory(preflight)
        after: dict[str, Any] | None = None
        post_error: str | None = None
        try:
            after = authenticate_frozen_tools(recorder_pin)[4]
        except (OSError, RecorderError) as error:
            post_error = str(error)
        report = build_baseline_report(
            recorder_pin, label, process, oracle, matrix, before, after,
            post_run_error=post_error,
        )
        report_publication = publish_document(preflight, report, compressed=True)
        receipt = make_baseline_receipt(
            recorder_pin, label, report, report_publication, preflight,
        )
        receipt_publication = publish_document(
            preflight, receipt, compressed=False,
        )
    verify_runtime()
    return {
        "schema": SCHEMA + "-recorded-baseline",
        "status": report["status"], "publication_status": "PASS",
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
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
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
            <= MAX_UNCOMPRESSED_BYTES,
            "the complete lossless baseline archive bounds were forged")
    validate_digest(value["report_uncompressed_sha256"],
                    "lossless uncompressed baseline")
    require(value["source_closure_before"] == value["source_closure_after"],
            "a frozen baseline tool owner changed during observation")
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
    value: Any, pins: OwnerPins, oracle: Any,
    matrix: list[dict[str, Any]], receipt: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("schema") == SCHEMA + "-complete-baseline-report"
            and value.get("status") == "PASS",
            "the signed two-reference Scanner baseline did not actually pass")
    for field, expected in baseline_source_fields(
        pins.recorder, pins.baseline.label,
    ).items():
        require(value.get(field) == expected,
                "the lossless baseline changed a frozen source field: " + field)
    require(value.get("source_closure_unchanged") is True
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
            and value.get("all_failure_reasons") == []
            and value.get("failure_count") == 0
            and value.get("clock_samples") == 0
            and value.get("timing_trials_run") == 0
            and value.get("benchmark_files_read") == 0
            and value.get("hidden_cases_read") == 0
            and value.get("performance") == "NOT MEASURED"
            and value.get("candidate_qualified_for_hidden_benchmark") is False
            and value.get("final_winner_selected") is False,
            "the full published baseline was substituted or did not pass")
    result = validate_baseline_result(
        value.get("complete_baseline_result"), oracle, matrix,
    )
    require(value.get("complete_decoded_baseline_process") == result
            and decode_stream(value.get("complete_baseline_process_stdout"),
                              "published baseline controller stdout")
            == canonical(result)
            and decode_stream(value.get("complete_baseline_process_stderr"),
                              "published baseline controller stderr") == b""
            and value.get("reference_a_records")
            == result["reference_a"]["records"]
            and value.get("reference_b_records")
            == result["reference_b"]["records"]
            and value.get("reference_a_process")
            == result["reference_a_process"]
            and value.get("reference_b_process")
            == result["reference_b_process"],
            "complete archived reference processes or observations were hidden")
    return value


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
                        require(plain_bytes <= MAX_UNCOMPRESSED_BYTES,
                                "lossless baseline exceeded its exact safe bound")
                        plain_hasher.update(block)
                        pieces.append(block)
        except (OSError, EOFError, gzip.BadGzipFile) as error:
            raise RecorderError(
                "the authenticated Scanner baseline gzip is not lossless"
            ) from error
    require(plain_bytes == receipt["report_uncompressed_bytes"]
            and plain_hasher.hexdigest()
            == receipt["report_uncompressed_sha256"],
            "the signed complete Scanner baseline was truncated or substituted")
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


def validate_candidate_outcome(value: Any, oracle: Any | None = None) -> None:
    require(type(value) is dict and type(value.get("status")) is str,
            "a genuine complete Scanner observation is mandatory")
    if value["status"] == "contract-violation":
        require(set(value) == {
            "status", "violation", "callbacks", "warnings", "combined_pattern",
        } and type(value.get("violation")) is dict
          and set(value["violation"]) == {"type", "message"}
          and type(value["violation"].get("type")) is str
          and type(value["violation"].get("message")) is str
          and type(value.get("callbacks")) is list
          and type(value.get("warnings")) is list,
          "a genuine Scanner compatibility violation was concealed")
        if oracle is not None:
            for callback in value["callbacks"]:
                require(type(callback) is dict,
                        "a genuine partial Scanner callback was hidden")
            if value["combined_pattern"] is not None:
                oracle.validate_pattern(value["combined_pattern"])
    else:
        require(value["status"] in {"return", "raise"},
                "an unknown or approximate Scanner result was injected")
        if oracle is not None:
            try:
                oracle.validate_outcome(value)
            except Exception as error:
                raise RecorderError(
                    "the frozen oracle rejected a complete candidate observation"
                ) from error
    canonical(value)


def validate_candidate_records(
    matrix: list[dict[str, Any]], records: Any, expected: Any,
    oracle: Any | None = None,
) -> list[dict[str, Any]]:
    validate_digest(expected, "all source-ordered candidate observations")
    require(type(records) is list and len(records) == CASE_COUNT,
            "all 2,854 actual source-ordered candidate outcomes are mandatory")
    for case, record in zip(matrix, records, strict=True):
        require(type(record) is dict
                and set(record) == {"case", "cohort", "expected_kind", "outcome"}
                and record.get("case") == case["case"]
                and record.get("cohort") == case["cohort"]
                and record.get("expected_kind") == case["expected_kind"],
                "a genuine candidate case was concealed or reordered")
        validate_candidate_outcome(record["outcome"], oracle)
    require(digest(records) == expected,
            "the complete native candidate observation vector changed")
    return records


def observe_candidate_case(
    case: Mapping[str, Any], candidate: Any, oracle: Any,
) -> dict[str, Any]:
    callbacks: list[dict[str, Any]] = []
    combined: dict[str, Any] | None = None

    def action(branch: int) -> Callable[[Any, Any], Any]:
        def callback(scanner: Any, token: Any) -> Any:
            current = scanner.match
            actual = scanner.scanner
            callbacks.append({
                "branch": branch,
                "token": oracle.normalize_value(token),
                "match": oracle.normalize_match(current),
                "combined_pattern": oracle.normalize_pattern(actual),
                "match_uses_combined_pattern": current.re is actual,
            })
            if len(callbacks) > 2:
                raise CandidateContractViolation(
                    "the owned Scanner failed to make forward progress"
                )
            return branch, token
        return callback

    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter("always")
        try:
            phrase = oracle.decode_subject(case["phrase"])
            subject = oracle.decode_subject(case["subject"])
            fallback = "." if case["domain"] == "str" else b"."
            lexicon = [(phrase, action(0)), (fallback, action(1))]
            scanner = candidate.Scanner(lexicon, flags=case["flags"])
            if scanner.lexicon is not lexicon:
                raise CandidateContractViolation(
                    "the original Scanner lexicon identity was substituted"
                )
            combined = oracle.normalize_pattern(scanner.scanner)
            if not (
                scanner.scanner.pattern is None
                and scanner.scanner.groups == 2
                and scanner.scanner.flags == case["flags"]
                and dict(scanner.scanner.groupindex) == {}
            ):
                raise CandidateContractViolation(
                    "the actual native combined scanner pattern was approximated"
                )
            tokens, remainder = scanner.scan(subject)
            result = {
                "status": "return",
                "value": oracle.normalize_value((tokens, remainder)),
                "callbacks": callbacks,
                "warnings": oracle.normalize_warnings(observed),
                "combined_pattern": combined,
            }
        except (CandidateContractViolation, oracle.ScannerCommentOracleError) as error:
            result = {
                "status": "contract-violation",
                "violation": {
                    "type": type(error).__qualname__, "message": str(error),
                },
                "callbacks": callbacks,
                "warnings": oracle.normalize_warnings(observed),
                "combined_pattern": combined,
            }
        except Exception as error:
            result = {
                "status": "raise",
                "exception": oracle.normalize_error(error, candidate),
                "callbacks": callbacks,
                "warnings": oracle.normalize_warnings(observed),
                "combined_pattern": combined,
            }
    validate_candidate_outcome(result, oracle)
    return result


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
    oracle, v5, audit, matrix, sources = authenticate_frozen_tools(pins.recorder)
    receipt, receipt_owner = authenticate_baseline_receipt(pins)
    reference, archive_owner = stream_baseline_archive(
        pins, oracle, matrix, receipt,
    )
    before, manifest = authenticate_family_closure(pins, v5, audit)
    warning, identity, _, _ = v5.load_frozen_oracles()
    original = importlib.import_module("re")
    require(type(original) is types.ModuleType and original.__name__ == "re",
            "the genuine original CPython guard owner was substituted")
    selected = v5.family_spec(spec.name)
    records: list[dict[str, Any]] = []
    guard: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    with warning.installed_warning_safe_guard(identity):
        with v5.chosen_original_guard(
            original, native_pins(pins), selected, identity, warning,
        ) as active:
            candidate = active.get("candidate")
            require(type(candidate) is types.ModuleType
                    and candidate.__name__ == spec.adapter_module,
                    "a sibling, standard, or external Scanner engine escaped")
            require(active.get("actual_method_guard_checks") == 0
                    and active.get("actual_warning_registry_guard_checks") == 0,
                    "continuous Scanner ownership guards did not start at zero")
            for row in matrix:
                active["verify"]()
                active["actual_method_guard_checks"] += 1
                try:
                    outcome = observe_candidate_case(row, candidate, oracle)
                finally:
                    active["verify"]()
                    active["actual_method_guard_checks"] += 1
                records.append({
                    "case": row["case"], "cohort": row["cohort"],
                    "expected_kind": row["expected_kind"], "outcome": outcome,
                })
            guard = snapshot_guard(active, spec)
            actual = active.get("native_provenance")
            require(v5.validate_owners(actual, selected, native_pins(pins)),
                    "the continuously guarded native engine changed")
            provenance = validate_native_provenance(actual, pins)
    require(guard is not None and provenance is not None,
            "complete continuous Scanner ownership evidence is mandatory")
    records_sha256 = digest(records)
    validate_candidate_records(matrix, records, records_sha256, oracle)
    after, final_manifest = authenticate_family_closure(pins, v5, audit)
    require(before == after and manifest == final_manifest,
            "an independently owned source or native engine changed")
    return {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED", "python": "3.14.6",
        "role": "candidate-" + spec.name, "pid": os.getpid(),
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
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "evidence_files_created": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def validate_candidate_worker(
    value: Any, pins: OwnerPins, matrix: list[dict[str, Any]],
    *, expected_pid: int, oracle: Any, audit: Any,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    require(type(expected_pid) is int and expected_pid > 0,
            "an independently isolated candidate worker PID is mandatory")
    expected = {
        "schema": SCHEMA + "-isolated-candidate-worker",
        "status": "OBSERVED", "python": "3.14.6",
        "role": "candidate-" + spec.name,
        "pid": expected_pid, "candidate_family": spec.name,
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
        "clock_samples": 0, "timing_trials_run": 0,
        "workspace_files_written": 0, "evidence_files_created": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    extras = {
        "baseline_reference_pids", "baseline_receipt_owner",
        "baseline_archive_owner", "source_provenance", "audit_manifest",
        "owned_source_closure", "native_provenance", "matcher_guard",
        "records_sha256", "records", "actual_candidate_imports",
    }
    require(type(value) is dict and set(value) == set(expected) | extras,
            "a complete guarded Scanner candidate worker was forged")
    for field, original in expected.items():
        require(value.get(field) == original,
                "a frozen isolated candidate observation changed: " + field)
    pids = value["baseline_reference_pids"]
    require(type(pids) is list and len(pids) == 2
            and all(type(item) is int and item > 0 for item in pids)
            and pids[0] != pids[1] and expected_pid not in pids,
            "a candidate process was aliased to a genuine reference worker")
    require(type(value["actual_candidate_imports"]) is int
            and value["actual_candidate_imports"] >= 2,
            "a genuinely owned candidate adapter or bridge was not imported")
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
    provenance = value["source_provenance"]
    require(type(provenance) is dict and set(provenance) == {
        "recorder", "scanner_oracle", "original_v5", "from_scratch_audit_v3",
    }, "a complete frozen Scanner tool source closure was omitted")
    for name, relative, source in (
        ("recorder", SOURCE_RELATIVE, pins.recorder),
        ("scanner_oracle", ORACLE_RELATIVE, ORACLE_SHA256),
        ("original_v5", V5_RELATIVE, V5_SHA256),
        ("from_scratch_audit_v3", AUDIT_RELATIVE, AUDIT_SHA256),
    ):
        validate_owner(provenance[name], relative, source)
    manifest = make_audit_manifest(pins, audit)
    require(value["audit_manifest"] == manifest,
            "the complete V3 native ownership manifest was substituted")
    try:
        audit.validate_serializable_owners(
            value["owned_source_closure"], spec.name, manifest, AUDIT_SHA256,
        )
    except Exception as error:
        raise RecorderError(
            "the frozen V3 audit rejected a complete native owner"
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


def build_candidate_report(
    pins: OwnerPins, label: str, process: Mapping[str, Any],
    matrix: list[dict[str, Any]], receipt: Mapping[str, Any],
    reference: Mapping[str, Any], before: Mapping[str, Any],
    after: Mapping[str, Any] | None, oracle: Any, audit: Any,
    *, post_run_error: str | None = None,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    validate_label(label)
    validate_matrix(matrix)
    validate_baseline_receipt(receipt, pins)
    validate_archived_baseline(reference, pins, oracle, matrix, receipt)
    raw_stdout, raw_stderr = process.get("stdout"), process.get("stderr")
    stdout = capture_stream(raw_stdout, "complete candidate process stdout")
    stderr = capture_stream(raw_stderr, "complete candidate process stderr")
    failures: list[str] = []
    decoded: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    if process.get("started") is not True:
        failures.append("the native candidate could not start: "
                        + str(process.get("spawn_error")))
    if process.get("timed_out") is True:
        failures.append("the native candidate exceeded its safe timeout")
    if raw_stdout:
        try:
            decoded = decode_document(raw_stdout, "complete native worker")
            candidate = validate_candidate_worker(
                decoded, pins, matrix, expected_pid=process.get("pid"),
                oracle=oracle, audit=audit,
            )
        except (RecorderError, TypeError, ValueError, KeyError) as error:
            failures.append("invalid complete candidate observation: " + str(error))
    if candidate is None:
        failures.append("all 2,854 genuine candidate outcomes remain unknown")
    if raw_stderr:
        failures.append("the genuine candidate emitted complete stderr")
    expected_exit = 0 if candidate is not None and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        failures.append("the native candidate crashed or returned a wrong exit")
    if post_run_error is not None:
        failures.append("post-run ownership authentication failed: "
                        + post_run_error)
    if before != after:
        failures.append("the complete owned native source closure changed")
    mismatch_counts = {name: 0 for name in EXPECTED_COUNTS}
    cohort_counts = {"semantic": 0, "tokenizer": 0}
    mismatches: list[dict[str, Any]] | None = None
    if candidate is not None:
        mismatches = []
        for row, original, actual in zip(
            matrix, reference["reference_a_records"], candidate["records"],
            strict=True,
        ):
            require(row["case"] == original["case"] == actual["case"]
                    and row["cohort"] == original["cohort"] == actual["cohort"]
                    and row["expected_kind"]
                    == original["expected_kind"] == actual["expected_kind"],
                    "a genuine baseline-to-candidate case was reordered")
            if original["outcome"] != actual["outcome"]:
                mismatch_counts[row["expected_kind"]] += 1
                cohort_counts[row["cohort"]] += 1
                mismatches.append({
                    "case": row["case"], "cohort": row["cohort"],
                    "expected_kind": row["expected_kind"],
                    "input": row,
                    "baseline_outcome": original["outcome"],
                    "candidate_outcome": actual["outcome"],
                })
        if mismatches:
            failures.append("the owned candidate differs on "
                            + str(len(mismatches)) + " frozen Scanner cases")
    return {
        "schema": SCHEMA + "-complete-candidate-report",
        "status": "FAIL" if failures else "PASS",
        "python": "3.14.6", "label": label,
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
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
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
        "baseline_records": reference["reference_a_records"],
        "candidate_records": candidate["records"] if candidate else None,
        "mismatch_count": len(mismatches) if mismatches is not None else None,
        "all_mismatches": mismatches,
        "mismatches_by_expected_kind": (
            mismatch_counts if mismatches is not None else None
        ),
        "mismatches_by_cohort": (
            cohort_counts if mismatches is not None else None
        ),
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
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 1 if candidate else None,
        "actual_candidate_imports": (
            candidate["actual_candidate_imports"] if candidate else None
        ),
        "actual_candidate_process_invocations": int(
            process.get("started") is True
        ),
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


def make_candidate_receipt(
    pins: OwnerPins, label: str, report: Mapping[str, Any],
    publication: Mapping[str, Any], preflight: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-durable-candidate-publication-receipt",
        "status": "PASS", "candidate_result_status": report["status"],
        "python": "3.14.6", "label": label,
        "candidate_family": pins.family,
        "candidate_source_sha256": pins.adapter,
        "native_engine_sha256": pins.engine,
        "native_bridge_sha256": pins.bridge,
        "baseline_label": pins.baseline.label,
        "recorder_source_sha256": pins.recorder,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
        "baseline_receipt_relative": approved_paths(
            "baseline", pins.baseline.label,
        )[1],
        "baseline_receipt_sha256": pins.baseline.receipt,
        "baseline_archive_relative": approved_paths(
            "baseline", pins.baseline.label,
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
        "mismatches_by_expected_kind": report["mismatches_by_expected_kind"],
        "mismatches_by_cohort": report["mismatches_by_cohort"],
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
        "fresh_paths_checked_before_candidate": (
            preflight["fresh_paths_checked_before_observation"]
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
    oracle, v5, audit, matrix, _ = authenticate_frozen_tools(pins.recorder)
    receipt, _ = authenticate_baseline_receipt(pins)
    reference, _ = stream_baseline_archive(pins, oracle, matrix, receipt)
    before, _ = authenticate_family_closure(pins, v5, audit)
    with preflight_fresh_outputs("candidate", label, spec.name) as preflight:
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
            pins, label, process, matrix, receipt, reference,
            before, after, oracle, audit, post_run_error=post_error,
        )
        publication = publish_document(preflight, report, compressed=True)
        receipt_document = make_candidate_receipt(
            pins, label, report, publication, preflight,
        )
        receipt_publication = publish_document(
            preflight, receipt_document, compressed=False,
        )
    verify_runtime()
    return {
        "schema": SCHEMA + "-recorded-candidate",
        "status": report["status"], "publication_status": "PASS",
        "python": "3.14.6", "candidate_family": spec.name, "label": label,
        "recorder_source_sha256": pins.recorder,
        "oracle_source_sha256": ORACLE_SHA256,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "baseline_records_sha256": pins.baseline.records,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": (
            report["validated_candidate_record_count"]
        ),
        "mismatch_count": report["mismatch_count"],
        "actual_candidate_process_invocations": (
            report["actual_candidate_process_invocations"]
        ),
        "report_publication": publication,
        "receipt_publication": receipt_publication,
        "all_failure_reasons": report["all_failure_reasons"],
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


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
                "source-only Scanner controls cannot perform " + selected
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


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "case": row["case"], "cohort": row["cohort"],
        "expected_kind": row["expected_kind"],
        "outcome": {
            "status": "contract-violation",
            "violation": {
                "type": "SyntheticOnly", "message": "no regex engine observed",
            },
            "callbacks": [], "warnings": [], "combined_pattern": None,
        },
    } for row in matrix]


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
    raise RecorderError("a forged Scanner control was accepted: " + name)


def source_self_test() -> dict[str, Any]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
            "run source-only controls under clean isolated pinned CPython")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, actual: Any) -> None:
        require(type(name) is str and name not in accepted and bool(actual),
                "a distinct synthetic Scanner control failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Callable[[], Any]) -> None:
        expect_rejection(name, operation, rejected)

    with SourceOnlyBoundary() as blocked:
        matrix = validate_matrix(build_frozen_matrix())
        accept("reproduce-all-2854-source-ordered-frozen-cases",
               len(matrix) == CASE_COUNT and digest(matrix) == MATRIX_SHA256)
        accept("retain-full-exact-64-bit-seed",
               PUBLISHED_SEED == 5_999_725_261_024_810_545
               and PUBLISHED_SEED > 2 ** 53
               and all(row["seed"] == PUBLISHED_SEED for row in matrix))
        accept("retain-2560-comment-and-294-tokenizer-cases",
               sum(row["cohort"] == "semantic" for row in matrix) == 2_560
               and sum(row["cohort"] == "tokenizer" for row in matrix) == 294)
        accept("retain-all-genuine-102-negative-python-cases",
               sum(row["expected_kind"] == "continued-comment-unterminated"
                   for row in matrix) == 102)
        accept("freeze-every-distinct-family-source-closure",
               all(family_spec(name).name == name for name in FAMILIES))
        accept("keep-c-only-native-engine-bridge-alias",
               all((family_spec(name).engine_relative
                    == family_spec(name).bridge_relative) is (name == "c")
                   for name in FAMILIES))
        baseline = synthetic_baseline_pins()
        accept("pin-baseline-receipt-archive-and-full-record-vector",
               isinstance(baseline, BaselinePins))
        rows = synthetic_records(matrix)
        vector_hash = digest(rows)
        accept("validate-all-complete-source-ordered-synthetic-observations",
               validate_candidate_records(matrix, rows, vector_hash) == rows)
        accept("keep-genuine-contract-failures-separate-from-public-errors",
               rows[0]["outcome"]["status"] == "contract-violation")
        fixture = canonical({
            "surrogate": "\ud800", "accent": "e\u0301", "emoji": "😀",
            "seed": PUBLISHED_SEED, "nested": [True, None, {"x": [1, 2]}],
        })
        accept("preserve-unicode-surrogates-and-exact-64-bit-json",
               decode_document(fixture, "in-memory") ["seed"] == PUBLISHED_SEED)
        accept("stream-exact-canonical-evidence-without-files",
               b"".join(iter_canonical(decode_document(fixture, "in-memory")))
               == fixture)
        compressed = gzip.compress(fixture, compresslevel=9, mtime=0)
        accept("deterministic-lossless-mtime-zero-gzip-in-memory",
               compressed == gzip.compress(fixture, compresslevel=9, mtime=0)
               and gzip.decompress(compressed) == fixture)
        stream = capture_stream(fixture, "in-memory")
        accept("retain-exact-complete-reversible-process-streams",
               decode_stream(stream, "in-memory") == fixture)
        for family in FAMILIES:
            pins = synthetic_owner_pins(family)
            accept("pin-every-exact-" + family + "-native-source", bool(pins))
            accept("enforce-every-" + family + "-no-delegation-guard",
                   validate_guard(synthetic_guard(family_spec(family)),
                                  family_spec(family)))
            report, receipt = approved_paths("candidate", "trial-v1", family)
            accept("isolate-exact-" + family + "-evidence-paths",
                   report.endswith(".json.gz")
                   and receipt.endswith("-publication-receipt.json")
                   and "/" + family + "-scanner-verbose-comments-v1-"
                   in report)

        for name, value in (
            ("empty", ""), ("uppercase", "ABC"), ("escaping", "../x"),
            ("slash", "a/b"), ("backslash", "a\\b"),
            ("double-dash", "a--b"), ("leading-dash", "-a"),
            ("trailing-dash", "a-"), ("dot", "a.b"),
            ("nul", "a\x00b"), ("bool", True),
            ("oversize", "a" * 65),
        ):
            reject("reject-" + name + "-run-label",
                   lambda value=value: validate_label(value))
        for name, value in (
            ("empty", ""), ("dot", "."), ("parent", "../x"),
            ("absolute", "/tmp/x"), ("double-slash", "a//b"),
            ("backslash", "a\\b"), ("nul", "a\x00b"),
        ):
            reject("reject-" + name + "-owner-path",
                   lambda value=value: safe_parts(value))
        for name, value in (
            ("short", "ab"), ("uppercase", "AB" * 32),
            ("constant", "0" * 64), ("nonhex", "g1" * 32),
            ("bool", True), ("none", None),
        ):
            reject("reject-" + name + "-source-digest",
                   lambda value=value: validate_digest(value, "synthetic"))
        for name, mutation in (
            ("drop-first", lambda xs: xs[1:]),
            ("drop-last", lambda xs: xs[:-1]),
            ("reverse-order", lambda xs: list(reversed(xs))),
            ("duplicate-first", lambda xs: [xs[0], *xs[1:-1], xs[0]]),
        ):
            reject("reject-" + name + "-frozen-matrix",
                   lambda mutation=mutation: validate_matrix(mutation(matrix)))
        for field, bad in (
            ("case", "forged/case"), ("cohort", "hidden"),
            ("context", "foreign"), ("domain", "memoryview"),
            ("flags", 128), ("line_ending", "hidden"),
            ("expected_kind", "hidden"), ("seed", PUBLISHED_SEED - 1),
        ):
            def poisoned_matrix(field: str = field, bad: Any = bad) -> Any:
                altered = list(matrix)
                altered[0] = {**matrix[0], field: bad}
                return validate_matrix(altered)
            reject("reject-forged-frozen-matrix-" + field, poisoned_matrix)
        reject("reject-truncated-53-bit-json-seed",
               lambda: build_frozen_matrix(float(PUBLISHED_SEED)))
        reject("reject-rounded-64-bit-json-seed",
               lambda: build_frozen_matrix(int(float(PUBLISHED_SEED))))
        for family in FAMILIES:
            pins = synthetic_owner_pins(family)
            spec = family_spec(family)
            raw = [path + "=" + source for path, source in pins.owned_sources]
            reject("reject-" + family + "-missing-owned-source",
                   lambda pins=pins, raw=raw: make_owner_pins(
                       pins.family, pins.recorder, pins.adapter,
                       pins.engine, pins.bridge, raw[:-1], pins.baseline,
                   ))
            reject("reject-" + family + "-duplicated-owned-source",
                   lambda pins=pins, raw=raw: make_owner_pins(
                       pins.family, pins.recorder, pins.adapter,
                       pins.engine, pins.bridge, [*raw, raw[0]], pins.baseline,
                   ))
            reject("reject-" + family + "-forged-adapter",
                   lambda pins=pins, raw=raw: make_owner_pins(
                       pins.family, pins.recorder, "ef" * 32,
                       pins.engine, pins.bridge, raw, pins.baseline,
                   ))
            incorrect_bridge = pins.engine if family != "c" else "ef" * 32
            reject("reject-" + family + "-cross-family-native-alias",
                   lambda pins=pins, raw=raw,
                   incorrect_bridge=incorrect_bridge: make_owner_pins(
                       pins.family, pins.recorder, pins.adapter,
                       pins.engine, incorrect_bridge, raw, pins.baseline,
                   ))
            guard = synthetic_guard(spec)
            for field in GUARD_TRUE_FIELDS:
                reject("reject-" + family + "-missing-" + field,
                       lambda guard=guard, field=field, spec=spec:
                       validate_guard({**guard, field: False}, spec))
            for field in (
                "actual_method_guard_checks",
                "actual_warning_registry_guard_checks",
            ):
                reject("reject-" + family + "-short-" + field,
                       lambda guard=guard, field=field, spec=spec:
                       validate_guard({**guard, field: 2 * CASE_COUNT - 1},
                                      spec))
            reject("reject-" + family + "-wrong-ffi-policy",
                   lambda guard=guard, spec=spec:
                   validate_guard({
                       **guard, "owned_native_ffi_allowed": not spec.owned_ctypes,
                   }, spec))
            reject("reject-" + family + "-forged-trusted-ffi-source",
                   lambda guard=guard, spec=spec:
                   validate_guard({
                       **guard, "trusted_stdlib_ctypes_source_sha256": "ef" * 32,
                   }, spec))
        for name, mutate in (
            ("truncated", lambda xs: xs[:-1]),
            ("reordered", lambda xs: list(reversed(xs))),
            ("duplicated", lambda xs: [xs[0], *xs[1:-1], xs[0]]),
        ):
            reject("reject-" + name + "-candidate-records",
                   lambda mutate=mutate: validate_candidate_records(
                       matrix, mutate(rows), vector_hash,
                   ))
        for field, value in (
            ("case", "substituted"), ("cohort", "substituted"),
            ("expected_kind", "substituted"),
        ):
            def poisoned_record(field: str = field, value: Any = value) -> Any:
                changed = list(rows)
                changed[0] = {**rows[0], field: value}
                return validate_candidate_records(matrix, changed, vector_hash)
            reject("reject-forged-candidate-record-" + field, poisoned_record)
        for field in ("status", "violation", "callbacks", "warnings",
                      "combined_pattern"):
            def missing_violation(field: str = field) -> Any:
                changed = dict(rows[0]["outcome"])
                changed.pop(field)
                return validate_candidate_outcome(changed)
            reject("reject-hidden-contract-failure-" + field,
                   missing_violation)
        for name, raw in (
            ("duplicate-json-key", b'{"a":1,"a":2}\n'),
            ("nan", b'{"a":NaN}\n'),
            ("positive-infinity", b'{"a":Infinity}\n'),
            ("negative-infinity", b'{"a":-Infinity}\n'),
            ("noncanonical-spacing", b'{"a": 1}\n'),
            ("missing-newline", b'{"a":1}'),
            ("trailing-evidence", b'{"a":1}\n{}\n'),
        ):
            reject("reject-" + name + "-worker-document",
                   lambda raw=raw: decode_document(raw, "synthetic"))
        for field, bad in (
            ("base64", "!!!"), ("bytes", len(fixture) + 1),
            ("sha256", "ef" * 32), ("complete", False),
        ):
            reject("reject-forged-worker-stream-" + field,
                   lambda field=field, bad=bad: decode_stream(
                       {**stream, field: bad}, "synthetic",
                   ))
        for family in ("python", "re", "regex", "pcre2", "other", None):
            reject("reject-foreign-family-" + str(family),
                   lambda family=family: family_spec(family))
        for mode, family in (
            ("baseline", "c"), ("candidate", "regex"), ("other", None),
        ):
            reject("reject-foreign-evidence-mode-" + str(mode)
                   + "-" + str(family),
                   lambda mode=mode, family=family:
                   approved_paths(mode, "trial-v1", family))

        def poison_gzip() -> bytes:
            corrupted = compressed[:-8] + bytes((compressed[-8] ^ 1,)) \
                + compressed[-7:]
            return gzip.decompress(corrupted)

        reject("reject-corrupt-in-memory-gzip-crc", poison_gzip)
        reject("block-real-file-read",
               lambda: builtins.open(SOURCE_ABSOLUTE, "rb"))
        reject("block-real-file-write",
               lambda: builtins.open("synthetic-forbidden", "wb"))
        reject("block-real-subprocess",
               lambda: subprocess.Popen([PINNED_PYTHON]))
        reject("block-real-candidate-import",
               lambda: importlib.import_module("candidates.rust_candidate"))
        reject("block-real-dynamic-import",
               lambda: importlib.import_module("json"))
        reject("block-real-clock", lambda: time.perf_counter_ns())
        reject("block-real-randomness", lambda: os.urandom(1))
        reject("block-real-garbage-collection", lambda: gc.collect())
        reject("block-real-directory-fsync", lambda: os.fsync(1))

        counts = dict(blocked.blocked)
    require(all(value >= 0 for value in counts.values())
            and counts["file_reads"] == 1 and counts["file_writes"] == 1
            and counts["processes"] == 1
            and counts["candidate_imports"] == 1
            and counts["dynamic_imports"] == 1
            and counts["clock_samples"] == 1
            and counts["garbage_collections"] == 1
            and counts["directory_syncs"] == 1
            and counts["randomness"] == 1
            and counts["threads"] == 0,
            "the synthetic-only external-effect boundary was bypassed")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate escaped source-only proof controls")
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_poison_count": len(rejected),
        "rejected_poisons": rejected,
        "source_only_boundary": counts,
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
        description="Durably record frozen original Scanner compatibility",
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
    require(validate_digest(options.oracle_source_sha256, "frozen Scanner oracle")
            == ORACLE_SHA256
            and validate_digest(options.matrix_sha256, "frozen Scanner matrix")
            == MATRIX_SHA256
            and validate_digest(options.ownership_audit_source_sha256,
                                "frozen V3 no-delegation audit") == AUDIT_SHA256,
            "explicitly pin the unchanged Scanner oracle, matrix, and V3 audit")
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
