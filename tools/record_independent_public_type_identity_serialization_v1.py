#!/usr/bin/env python3
"""Durably preserve every frozen CPython public type and serialization case.

A baseline uses exactly two independently isolated, source-authenticated
CPython reference workers. Each separately pinned native family runs only
inside the frozen V5 matcher quarantine and full V3 ownership policy.

One exact canonical controller stream preserves every public result,
exception, warning, source owner, process and mismatch without multiplying
the 6,912-case vector. Source-only controls block real filesystem access,
matcher imports, native loads, subprocesses, timing, randomness and threads.
"""

from __future__ import annotations

import argparse
import base64
import builtins
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
import stat
import subprocess
import sys
import threading
import time
import types
from collections.abc import Callable, Iterator, Mapping
from typing import Any

ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/record_independent_public_type_identity_serialization_v1.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-public-type-identity-serialization-recorder-v1"
ORACLE_RELATIVE = "tools/independent_public_type_identity_serialization_v1.py"
ORACLE_MODULE = "tools.independent_public_type_identity_serialization_v1"
ORACLE_SCHEMA = "rebar-independent-public-type-identity-serialization-v1"
ORACLE_SHA256 = (
    "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20"
)
PARENT_RECORDER_RELATIVE = (
    "tools/record_independent_substitution_buffer_semantics_v2.py"
)
PARENT_RECORDER_SHA256 = (
    "a7cf45ce72a178fead7eb0d0789fd1f0f37ed63789fe086070eefa613e959a33"
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
PREVIOUS_POLICY_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
PREVIOUS_POLICY_SHA256 = (
    "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
)
MATRIX_SHA256 = (
    "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
)
PUBLISHED_SEED = 0x5459_5045_5345_5231
UINT64_MAX = (1 << 64) - 1
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
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_ARCHIVE_BYTES = 384 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 320 * 1024 * 1024
MAX_COMPACT_REPORT_METADATA_BYTES = 32 * 1024 * 1024
MAX_ENCODED_PROCESS_STREAM_BYTES = ((MAX_PROCESS_BYTES + 2) // 3) * 4
MAX_COMPACT_REPORT_BYTES = (
    2 * MAX_ENCODED_PROCESS_STREAM_BYTES
    + MAX_COMPACT_REPORT_METADATA_BYTES
)
MAX_NORMALIZATION_DEPTH = 24
PROCESS_TIMEOUT_SECONDS = 900

PICKLE_PROTOCOLS = (0, 1, 2, 3, 4, 5)
FLAG_VALUES = (0, 2, 8, 16, 64, 256, 10, 258)
PATTERN_EXAMPLES = (
    (r"(?P<word>[A-Za-z]+)(?P<number>[0-9]+)", "Alpha42"),
    (r"(?P<left>a+)(?P<right>b*)", "aaabb"),
    (r"(?P<word>\w+)-(?P<number>\d+)", "Token_42-73"),
    (r"(a)(?P<named>b)?", "ab"),
    (r"(?P<part>[A-F]+)(?P<digits>\d*)", "FACE12"),
    (r"(?P<word>[^\W\d_]+)(?P<number>\d*)", "Alpha42"),
    (r"(?P<outer>(?P<inner>a)b)c", "abc"),
    (r"(?P<first>^a)(?P<last>b$)", "ab"),
    (r"(?P<empty>)(?P<word>a*)", "aaa"),
    (r"(?P<one>a|ab)(?P<two>b*)", "abb"),
    (r"(?P<quoted>a\.b)", "a.b"),
    (r"(?P<word>[a-z]+)(?:-(?P<number>\d+))?", "alpha-42"),
)
COHORTS = (
    "module-public-all",
    "module-public-export-members",
    "module-accessible-extra",
    "module-pattern-match-types",
    "module-public-error-alias",
    "module-public-flag-members",
    "module-public-callables",
    "module-star-export-equivalence",
    "flags-short-aliases",
    "flags-intflag-membership",
    "flags-zero-and-combinations",
    "flags-unknown-bit-retention",
    "flags-representation",
    "flags-compile-roundtrip",
    "flags-invalid-text",
    "flags-invalid-bytes",
    "generic-pattern-text",
    "generic-pattern-bytes",
    "generic-match-text",
    "generic-match-bytes",
    "generic-pattern-origin-and-args",
    "generic-match-origin-and-args",
    "generic-pattern-extra-arguments",
    "generic-match-extra-arguments",
    "pattern-type-text",
    "pattern-type-bytes",
    "pattern-instance-identity",
    "match-instance-identity",
    "pattern-public-metadata",
    "match-public-metadata",
    "pattern-groupindex-immutability",
    "pattern-and-match-representation",
    "copy-pattern-text",
    "copy-pattern-bytes",
    "deepcopy-pattern-text",
    "deepcopy-pattern-bytes",
    "copy-match-text",
    "copy-match-bytes",
    "deepcopy-match-text",
    "deepcopy-match-bytes",
    "weakref-pattern-text",
    "weakref-pattern-bytes",
    "weakref-match-text",
    "weakref-match-bytes",
    "hash-pattern-text",
    "hash-pattern-bytes",
    "pattern-equality-text",
    "pattern-equality-bytes",
    "pickle-pattern-text",
    "pickle-pattern-bytes",
    "pickle-protocol-public-type",
    "pickle-protocol-pattern-flags",
    "pickle-protocol-groups",
    "pickle-protocol-groupindex",
    "pickle-protocol-match-behavior",
    "pickle-match-rejection",
    "cache-identity-text",
    "cache-identity-bytes",
    "cache-flag-separation",
    "cache-pattern-type-separation",
    "cache-purge-identity",
    "cache-fifo-boundary",
    "cache-lru-boundary",
    "cache-template-and-purge",
    "warnings-positional-sub",
    "warnings-positional-subn",
    "warnings-positional-split",
    "errors-duplicate-sub",
    "errors-duplicate-subn",
    "errors-duplicate-split",
    "errors-pattern-attributes",
    "errors-multiline-pattern-attributes",
)
VARIANTS_PER_COHORT = len(PATTERN_EXAMPLES) * len(FLAG_VALUES)
CASE_COUNT = len(COHORTS) * VARIANTS_PER_COHORT
MATRIX_SHA256 = (
    "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
)

FORBIDDEN_EXTERNAL_ROOTS = frozenset({
    "_regex", "cffi", "fancy_regex", "google_re2", "hyperscan", "onig",
    "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class RecorderError(Exception):
    """Reject incomplete, substituted or unsafe public evidence."""


class SourceOnlyError(RecorderError):
    """A source-only public control attempted an observable effect."""


class ObservationFailure(RecorderError):
    """Preserve the truthful state of an already started worker."""

    def __init__(
        self,
        message: str,
        *,
        mode: str,
        process: Mapping[str, Any],
        report: Mapping[str, Any] | None,
        report_publication: Mapping[str, Any] | None = None,
        receipt_publication: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.mode = mode
        self.process = dict(process)
        self.report = dict(report) if report is not None else None
        self.report_publication = (
            dict(report_publication)
            if report_publication is not None else None
        )
        self.receipt_publication = (
            dict(receipt_publication)
            if receipt_publication is not None else None
        )


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


def checked_digest(value: Any, label: str) -> str:
    return validate_digest(value, label)


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
        validate_digest(records, "all 5,120 frozen reference observations"),
    )


def make_owner_pins(
    family: Any, recorder: Any, adapter: Any, engine: Any, bridge: Any,
    sources: Any, baseline: BaselinePins,
) -> OwnerPins:
    spec = family_spec(family)
    require(isinstance(baseline, BaselinePins),
            "an exact previously published baseline is mandatory")
    validate_digest(recorder, "frozen substitution recorder")
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
    require(type(value) is bytes, "only exact text and bytes are matrix inputs")
    return {"kind": "bytes", "hex": value.hex()}


def decode_subject(value: Any, domain: str) -> str | bytes:
    require(
        domain in {"str", "bytes"} and type(value) is dict,
        "a complete exact-domain public matrix input is mandatory",
    )
    if domain == "str":
        require(
            set(value) == {"kind", "value"}
            and value.get("kind") == "str"
            and type(value.get("value")) is str,
            "a source-ordered public text input was substituted",
        )
        return value["value"]
    require(
        set(value) == {"kind", "hex"}
        and value.get("kind") == "bytes"
        and type(value.get("hex")) is str
        and len(value["hex"]) % 2 == 0,
        "a source-ordered public bytes input was substituted",
    )
    try:
        result = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise RecorderError(
            "a frozen public bytes input is not lowercase hexadecimal"
        ) from error
    require(
        result.hex() == value["hex"],
        "a frozen public bytes input was noncanonical",
    )
    return result


def cohort_domain(cohort: str, variant: int) -> str:
    if cohort.endswith("-text"):
        return "str"
    if cohort.endswith("-bytes"):
        return "bytes"
    if cohort == "flags-invalid-text":
        return "str"
    if cohort == "flags-invalid-bytes":
        return "bytes"
    return "str" if variant % 2 == 0 else "bytes"


def seed_rotation(seed: int, cohort_index: int) -> int:
    require(
        type(seed) is int and 0 <= seed <= UINT64_MAX,
        "preserve the exact full unsigned 64-bit published public seed",
    )
    require(
        type(cohort_index) is int and 0 <= cohort_index < len(COHORTS),
        "a frozen public cohort index escaped its source order",
    )
    value = (
        seed ^ ((cohort_index + 1) * 0x9E37_79B9_7F4A_7C15)
    ) & UINT64_MAX
    value ^= value >> 30
    value = (value * 0xBF58_476D_1CE4_E5B9) & UINT64_MAX
    value ^= value >> 27
    value = (value * 0x94D0_49BB_1331_11EB) & UINT64_MAX
    value ^= value >> 31
    return value % VARIANTS_PER_COHORT


def build_frozen_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(
        type(seed) is int and 0 <= seed <= UINT64_MAX,
        "an exact unsigned 64-bit public matrix seed is mandatory",
    )
    require(
        len(COHORTS) == 72
        and len(set(COHORTS)) == len(COHORTS)
        and len(PATTERN_EXAMPLES) == 12
        and len(FLAG_VALUES) == 8
        and VARIANTS_PER_COHORT == 96
        and CASE_COUNT == 6_912,
        "a complete 72-by-96 public property matrix was substituted",
    )
    matrix: list[dict[str, Any]] = []
    for cohort_index, cohort in enumerate(COHORTS):
        rotation = seed_rotation(seed, cohort_index)
        for variant in range(VARIANTS_PER_COHORT):
            slot = (variant + rotation) % VARIANTS_PER_COHORT
            pattern_index = slot % len(PATTERN_EXAMPLES)
            flags_index = slot // len(PATTERN_EXAMPLES)
            pattern_text, subject_text = PATTERN_EXAMPLES[pattern_index]
            domain = cohort_domain(cohort, variant)
            if domain == "str":
                pattern: str | bytes = pattern_text
                subject: str | bytes = subject_text
            else:
                pattern = pattern_text.encode("ascii")
                subject = subject_text.encode("ascii")
            matrix.append({
                "case": cohort + "/" + f"{variant:03d}",
                "cohort": cohort,
                "cohort_index": cohort_index,
                "variant": variant,
                "domain": domain,
                "pattern_index": pattern_index,
                "flags_index": flags_index,
                "flags": FLAG_VALUES[flags_index],
                "pattern": encode_subject(pattern),
                "subject": encode_subject(subject),
                "pickle_protocol": PICKLE_PROTOCOLS[
                    slot % len(PICKLE_PROTOCOLS)
                ],
                "published_seed": seed,
            })
    return matrix


def validate_matrix(
    value: Any,
    expected: str = MATRIX_SHA256,
) -> str:
    checked_digest(expected, "complete independently frozen public matrix")
    require(
        type(value) is list and len(value) == CASE_COUNT,
        "all 6,912 independently frozen public property cases are mandatory",
    )
    require(
        value == build_frozen_matrix(PUBLISHED_SEED),
        "a public case was omitted, reordered, duplicated, or substituted",
    )
    names: set[str] = set()
    counts = {name: 0 for name in COHORTS}
    pattern_pairs: dict[str, set[tuple[int, int]]] = {
        name: set() for name in COHORTS
    }
    protocol_counts = {
        name: {protocol: 0 for protocol in PICKLE_PROTOCOLS}
        for name in COHORTS
    }
    for row in value:
        require(
            type(row) is dict
            and set(row) == {
                "case", "cohort", "cohort_index", "variant", "domain",
                "pattern_index", "flags_index", "flags", "pattern",
                "subject", "pickle_protocol", "published_seed",
            },
            "a complete source-ordered public matrix case was forged",
        )
        identity = row["case"]
        require(
            type(identity) is str and identity not in names,
            "a distinct public case identity was silently reused",
        )
        names.add(identity)
        cohort = row["cohort"]
        require(
            cohort in counts
            and row["published_seed"] == PUBLISHED_SEED
            and row["domain"] in {"str", "bytes"}
            and row["pickle_protocol"] in PICKLE_PROTOCOLS,
            "a genuine public case family, seed, or domain was substituted",
        )
        decode_subject(row["pattern"], row["domain"])
        decode_subject(row["subject"], row["domain"])
        counts[cohort] += 1
        pair = (row["pattern_index"], row["flags_index"])
        require(
            pair not in pattern_pairs[cohort],
            "a public case padded its denominator with duplicate inputs",
        )
        pattern_pairs[cohort].add(pair)
        protocol_counts[cohort][row["pickle_protocol"]] += 1
    require(
        all(count == VARIANTS_PER_COHORT for count in counts.values())
        and all(
            len(pairs) == VARIANTS_PER_COHORT
            for pairs in pattern_pairs.values()
        )
        and all(
            all(
                count == VARIANTS_PER_COHORT // len(PICKLE_PROTOCOLS)
                for count in group.values()
            )
            for group in protocol_counts.values()
        ),
        "complete pattern, flag, cohort, or pickle-protocol balance was lost",
    )
    observed = digest(value)
    require(
        observed == expected,
        "the full canonical public property matrix fingerprint changed",
    )
    return observed


def validate_normalized_value(value: Any, depth: int = 0) -> None:
    require(
        type(depth) is int and 0 <= depth <= MAX_NORMALIZATION_DEPTH
        and type(value) is dict
        and type(value.get("kind")) is str,
        "a complete bounded normalized public observation was forged",
    )
    kind = value["kind"]
    if kind == "none":
        require(set(value) == {"kind"}, "a public None was substituted")
    elif kind in {"bool", "int", "str"}:
        expected = {"bool": bool, "int": int, "str": str}[kind]
        require(
            set(value) == {"kind", "value"}
            and type(value["value"]) is expected,
            "an exact public scalar type was substituted",
        )
    elif kind in {"bytes", "bytearray"}:
        require(
            set(value) == {"kind", "hex"}
            and type(value["hex"]) is str,
            "a complete public bytes observation was omitted",
        )
        try:
            raw = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise RecorderError(
                "public bytes are not exact canonical hexadecimal"
            ) from error
        require(
            raw.hex() == value["hex"],
            "a public bytes observation was noncanonical",
        )
    elif kind == "type":
        require(
            set(value) == {"kind", "name", "qualname", "module"}
            and all(
                type(value[name]) is str
                for name in ("name", "qualname", "module")
            ),
            "complete public type metadata was hidden",
        )
    elif kind == "int-subclass":
        require(
            set(value) == {"kind", "type", "value", "representation"}
            and type(value["value"]) is int
            and type(value["representation"]) is str,
            "a public flag integer or representation was forged",
        )
        validate_normalized_value(value["type"], depth + 1)
    elif kind in {"tuple", "list", "set", "frozenset"}:
        require(
            set(value) == {"kind", "items"}
            and type(value["items"]) is list,
            "a complete public sequence was hidden",
        )
        for item in value["items"]:
            validate_normalized_value(item, depth + 1)
        if kind in {"set", "frozenset"}:
            encodings = [canonical(item) for item in value["items"]]
            require(
                encodings == sorted(set(encodings)),
                "a public set was duplicated or noncanonically ordered",
            )
    elif kind == "mapping":
        require(
            set(value) == {"kind", "mappingproxy", "items"}
            and type(value["mappingproxy"]) is bool
            and type(value["items"]) is list,
            "a complete public mapping observation was forged",
        )
        encodings: list[bytes] = []
        for pair in value["items"]:
            require(
                type(pair) is dict and set(pair) == {"key", "value"},
                "a public mapping entry was incomplete",
            )
            validate_normalized_value(pair["key"], depth + 1)
            validate_normalized_value(pair["value"], depth + 1)
            encodings.append(canonical(pair["key"]))
        require(
            encodings == sorted(set(encodings)),
            "a public mapping was duplicated or silently reordered",
        )
    elif kind == "generic-alias":
        require(
            set(value) == {
                "kind", "representation", "origin", "arguments",
            }
            and type(value["representation"]) is str
            and type(value["arguments"]) is list,
            "a genuine public generic alias was incomplete",
        )
        validate_normalized_value(value["origin"], depth + 1)
        for item in value["arguments"]:
            validate_normalized_value(item, depth + 1)
    elif kind == "callable":
        require(
            set(value) == {"kind", "name", "module"}
            and type(value["name"]) is str
            and type(value["module"]) is str,
            "public callable identity was hidden",
        )
    else:
        raise RecorderError(
            "an unknown public normalized observation kind: " + kind
        )



def validate_error(value: Any) -> None:
    require(
        type(value) is dict and set(value) == {
            "type", "message", "arguments", "is_public_pattern_error",
            "has_message", "message_attribute", "has_pattern", "pattern",
            "has_position", "position", "has_line", "line",
            "has_column", "column",
        }
        and type(value.get("message")) is str
        and all(
            type(value[name]) is bool
            for name in (
                "is_public_pattern_error", "has_message", "has_pattern",
                "has_position", "has_line", "has_column",
            )
        ),
        "a complete exact public exception or error location was hidden",
    )
    for name in (
        "type", "arguments", "message_attribute", "pattern", "position",
        "line", "column",
    ):
        validate_normalized_value(value[name])



def validate_warning(value: Any) -> None:
    require(
        type(value) is dict and set(value) == {
            "category", "category_module", "message", "filename", "line",
        }
        and all(
            type(value[name]) is str
            for name in ("category", "category_module", "message", "filename")
        )
        and type(value["line"]) is int and value["line"] > 0,
        "a complete public warning, category, or source location was forged",
    )



def validate_outcome(value: Any) -> None:
    require(
        type(value) is dict
        and value.get("status") in {"return", "raise"}
        and type(value.get("warnings")) is list,
        "a public observation was omitted or falsely skipped",
    )
    if value["status"] == "return":
        require(
            set(value) == {"status", "value", "warnings"},
            "a genuine returning public observation was incomplete",
        )
        validate_normalized_value(value["value"])
    else:
        require(
            set(value) == {"status", "exception", "warnings"},
            "a genuine raising public observation was incomplete",
        )
        validate_error(value["exception"])
    for warning in value["warnings"]:
        validate_warning(warning)


def validate_records(
    matrix: list[dict[str, Any]],
    records: Any,
    expected: str,
) -> list[dict[str, Any]]:
    checked_digest(expected, "complete public property observation vector")
    require(
        type(records) is list and len(records) == CASE_COUNT,
        "all 6,912 public type and serialization observations are mandatory",
    )
    for case, record in zip(matrix, records, strict=True):
        require(
            type(record) is dict and set(record) == {
                "case", "cohort", "domain", "pattern_index",
                "flags", "pickle_protocol", "outcome",
            }
            and all(
                record.get(name) == case[name]
                for name in (
                    "case", "cohort", "domain", "pattern_index",
                    "flags", "pickle_protocol",
                )
            ),
            "a complete public observation was hidden or silently relabeled",
        )
        validate_outcome(record["outcome"])
    require(
        digest(records) == expected,
        "the complete public outcome vector was silently substituted",
    )
    return records



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
    require(type(maximum) is int and 0 < maximum <= MAX_ARCHIVE_BYTES,
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
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path)
        and sys.path[0] == ROOT
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == SOURCE_ABSOLUTE,
        "use only the pinned isolated CPython and exact public recorder",
    )
    if not candidate_loaded:
        require(
            not any(
                name == "candidates"
                or name.startswith("candidates.")
                or name.partition(".")[0] in FORBIDDEN_EXTERNAL_ROOTS
                for name in sys.modules
            ),
            "a native candidate or external matcher escaped isolation",
        )


def validate_frozen_source_owners(
    value: Any,
    recorder_pin: str,
) -> dict[str, Any]:
    owners = (
        ("recorder", SOURCE_RELATIVE, recorder_pin),
        ("parent_recorder", PARENT_RECORDER_RELATIVE, PARENT_RECORDER_SHA256),
        ("public_type_oracle", ORACLE_RELATIVE, ORACLE_SHA256),
        ("original_v5", V5_RELATIVE, V5_SHA256),
        ("from_scratch_audit_v3", AUDIT_RELATIVE, AUDIT_SHA256),
        ("previous_ownership_policy", PREVIOUS_POLICY_RELATIVE,
         PREVIOUS_POLICY_SHA256),
    )
    require(
        type(value) is dict and set(value) == {name for name, _, _ in owners},
        "an exact public oracle, recorder, V5, V3, or immutable owner is absent",
    )
    for name, relative, expected in owners:
        validate_owner(value[name], relative, expected)
    return value


def authenticate_frozen_tools(
    recorder_pin: str,
) -> tuple[Any, Any, Any, list[dict[str, Any]], dict[str, Any]]:
    verify_runtime()
    recorder, _ = read_owned_regular(
        SOURCE_RELATIVE, recorder_pin, MAX_SOURCE_BYTES,
    )
    parent, _ = read_owned_regular(
        PARENT_RECORDER_RELATIVE, PARENT_RECORDER_SHA256, MAX_SOURCE_BYTES,
    )
    policy, _ = read_owned_regular(
        PREVIOUS_POLICY_RELATIVE, PREVIOUS_POLICY_SHA256, MAX_SOURCE_BYTES,
    )
    oracle, oracle_owner = authenticate_module(
        ORACLE_MODULE, ORACLE_RELATIVE, ORACLE_SHA256,
    )
    v5, v5_owner = authenticate_module(V5_MODULE, V5_RELATIVE, V5_SHA256)
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
        and tuple(getattr(oracle, "PICKLE_PROTOCOLS", ())) == PICKLE_PROTOCOLS
        and tuple(getattr(oracle, "FLAG_VALUES", ())) == FLAG_VALUES
        and getattr(oracle, "V5_GUARD_SHA256", None) == V5_SHA256
        and getattr(oracle, "OWNERSHIP_AUDIT_SHA256", None) == AUDIT_SHA256
        and getattr(v5, "SOURCE_RELATIVE", None) == V5_RELATIVE
        and v5.current_source_sha256() == V5_SHA256
        and getattr(audit, "SOURCE_RELATIVE", None) == AUDIT_RELATIVE
        and dict(getattr(audit, "IMMUTABLE_POLICY_SHA256", {}))
        == {PREVIOUS_POLICY_RELATIVE: PREVIOUS_POLICY_SHA256,
            V5_RELATIVE: V5_SHA256},
        "the genuine frozen public oracle or V3/V5 ownership policy changed",
    )
    matrix = build_frozen_matrix()
    require(
        oracle.build_matrix() == matrix
        and oracle.validate_matrix(matrix, MATRIX_SHA256) == MATRIX_SHA256,
        "the genuine frozen 6,912-case public matrix was substituted",
    )
    return oracle, v5, audit, matrix, validate_frozen_source_owners(
        {
            "recorder": recorder,
            "parent_recorder": parent,
            "public_type_oracle": oracle_owner,
            "original_v5": v5_owner,
            "from_scratch_audit_v3": audit_owner,
            "previous_ownership_policy": policy,
        },
        recorder_pin,
    )


def approved_paths(
    kind: str,
    label: str,
    family: str | None = None,
) -> tuple[str, str]:
    validate_label(label)
    require(
        kind in {"baseline", "candidate"},
        "select only a standard public baseline or native candidate",
    )
    if kind == "baseline":
        require(family is None, "a public baseline cannot select a candidate")
        slug = "public-type-identity-serialization-v1-" + label
    else:
        slug = (
            family_spec(family).name
            + "-public-type-identity-serialization-v1-"
            + label
        )
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json.gz",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


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
            "the retained public type evidence directory was replaced")
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
                "refusing to overwrite frozen public type evidence: " + basename
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
                "a complete lossless public type report was replaced")
        archive_hasher = hashlib.sha256()
        remaining = archive_bytes
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "a published lossless public type report was truncated")
            archive_hasher.update(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b""
                and archive_hasher.hexdigest() == expected_archive,
                "a published public type archive gained or lost evidence")
        os.lseek(descriptor, 0, os.SEEK_SET)
        plain_hasher = hashlib.sha256()
        count = 0
        with io.FileIO(descriptor, "rb", closefd=False) as source:
            with gzip.GzipFile(fileobj=source, mode="rb") as compressed:
                while True:
                    block = compressed.read(131_072)
                    require(type(block) is bytes,
                            "lossless public type evidence produced invalid bytes")
                    if not block:
                        break
                    count += len(block)
                    require(count <= MAX_COMPACT_REPORT_BYTES,
                            "lossless public type evidence exceeds its safe bound")
                    plain_hasher.update(block)
        require(count == plain_bytes
                and plain_hasher.hexdigest() == expected_plain,
                "lossless public type evidence differs from its original report")
    finally:
        os.close(descriptor)
    verify_retained_directory(preflight)


def publish_document(
    preflight: Mapping[str, Any], document: Mapping[str, Any],
    *, compressed: bool,
) -> dict[str, Any]:
    kind = "report" if compressed else "receipt"
    predicted_plain_bytes = (
        validate_compact_report_document(document)["complete_report_bytes"]
        if compressed else None
    )
    basename = preflight[kind + "_basename"]
    directory = verify_retained_directory(preflight)
    temporary = (
        ".rebar-public-type-recorder-v1-" + basename
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
                "a fresh public type evidence temporary is not regular")
        identity = (original.st_dev, original.st_ino)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "a fresh public type evidence temporary was substituted")
        if compressed:
            with io.FileIO(descriptor, "wb", closefd=False) as output:
                with gzip.GzipFile(
                    filename="", fileobj=output, mode="wb",
                    compresslevel=9, mtime=0,
                ) as archive:
                    for piece in iter_canonical(document):
                        plain_bytes += len(piece)
                        require(plain_bytes <= MAX_COMPACT_REPORT_BYTES,
                                "a complete public type report exceeds its bound")
                        plain_hasher.update(piece)
                        archive.write(piece)
                        write_calls += 1
        else:
            for piece in iter_canonical(document):
                plain_bytes += len(piece)
                require(plain_bytes <= MAX_SOURCE_BYTES,
                        "a public type publication receipt exceeds its bound")
                plain_hasher.update(piece)
                offset = 0
                while offset < len(piece):
                    actual = os.write(descriptor, piece[offset:])
                    require(type(actual) is int and actual > 0,
                            "a complete public type receipt was truncated")
                    offset += actual
                    write_calls += 1
        os.fsync(descriptor)
        if compressed:
            require(
                plain_bytes == predicted_plain_bytes,
                "the single-stream evidence differs from its proven exact size",
            )
        actual = os.fstat(descriptor)
        require(0 < actual.st_size <= MAX_ARCHIVE_BYTES,
                "a complete compressed report or receipt exceeds its bound")
        verify_retained_directory(preflight)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "public type evidence changed before its no-clobber publication")
        reader = os.open(temporary, regular_flags(), dir_fd=directory)
        try:
            archive_hasher = hashlib.sha256()
            remaining = actual.st_size
            while remaining:
                block = os.read(reader, min(remaining, 1_048_576))
                require(type(block) is bytes and bool(block),
                        "an authenticated public type temporary was truncated")
                archive_hasher.update(block)
                remaining -= len(block)
            require(os.read(reader, 1) == b"",
                    "an authenticated public type temporary gained a suffix")
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
                "an atomically published public type report was substituted")
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
                "a public type receipt was compressed or substituted")
        directory = verify_retained_directory(preflight)
        reader = os.open(basename, regular_flags(), dir_fd=directory)
        try:
            parts: list[bytes] = []
            remaining = result["bytes"]
            while remaining:
                raw = os.read(reader, min(remaining, 1_048_576))
                require(bool(raw), "a durable public type receipt was truncated")
                parts.append(raw)
                remaining -= len(raw)
            require(os.read(reader, 1) == b""
                    and b"".join(parts) == canonical(dict(document)),
                    "a durable public type receipt differs from its exact source")
        finally:
            os.close(reader)
    verify_retained_directory(preflight)
    return result



def validate_stream_byte_count(value: Any, label: str) -> int:
    require(
        type(value) is int and 0 <= value <= MAX_PROCESS_BYTES,
        "a complete worker stream exceeds its proven 96 MiB bound: " + label,
    )
    return value


def encoded_stream_byte_count(value: Any, label: str) -> int:
    size = validate_stream_byte_count(value, label)
    encoded = ((size + 2) // 3) * 4
    require(
        0 <= encoded <= MAX_ENCODED_PROCESS_STREAM_BYTES,
        "a complete reversible process base64 stream exceeds 128 MiB",
    )
    return encoded


def validate_compact_metadata_byte_count(value: Any) -> int:
    require(
        type(value) is int
        and 0 < value <= MAX_COMPACT_REPORT_METADATA_BYTES,
        "complete compact evidence metadata exceeds its frozen 32 MiB bound",
    )
    return value


def validate_compact_bounds() -> dict[str, int]:
    require(
        MAX_PROCESS_BYTES == 96 * 1024 * 1024
        and MAX_ENCODED_PROCESS_STREAM_BYTES == 128 * 1024 * 1024
        and MAX_COMPACT_REPORT_METADATA_BYTES == 32 * 1024 * 1024
        and MAX_COMPACT_REPORT_BYTES == 288 * 1024 * 1024
        and MAX_UNCOMPRESSED_BYTES == 320 * 1024 * 1024
        and MAX_ARCHIVE_BYTES == 384 * 1024 * 1024
        and MAX_COMPACT_REPORT_BYTES < MAX_UNCOMPRESSED_BYTES
        and MAX_UNCOMPRESSED_BYTES < MAX_ARCHIVE_BYTES,
        "the prospectively frozen lossless two-stream budget was weakened",
    )
    return {
        "maximum_raw_process_stream_bytes": MAX_PROCESS_BYTES,
        "maximum_encoded_process_stream_bytes": (
            MAX_ENCODED_PROCESS_STREAM_BYTES
        ),
        "maximum_process_stream_count": 2,
        "maximum_compact_report_metadata_bytes": (
            MAX_COMPACT_REPORT_METADATA_BYTES
        ),
        "maximum_compact_report_bytes": MAX_COMPACT_REPORT_BYTES,
        "maximum_uncompressed_bytes": MAX_UNCOMPRESSED_BYTES,
        "maximum_archive_bytes": MAX_ARCHIVE_BYTES,
    }


def capture_stream(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is bytes,
            "retain complete genuine bounded worker process bytes: " + label)
    validate_stream_byte_count(len(value), label)
    result = {
        "base64": base64.b64encode(value).decode("ascii"),
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": True,
    }
    require(
        len(result["base64"])
        == encoded_stream_byte_count(len(value), label),
        "the complete base64 process stream changed its proven byte bound",
    )
    return result



def decode_stream(value: Any, label: str) -> bytes:
    require(
        type(value) is dict
        and set(value) == {"base64", "bytes", "sha256", "complete"}
        and type(value.get("base64")) is str
        and type(value.get("bytes")) is int
        and value.get("complete") is True,
        "a complete reversible public type worker stream was concealed: "
        + label,
    )
    validate_stream_byte_count(value["bytes"], label)
    validate_digest(value["sha256"], label)
    require(
        len(value["base64"])
        == encoded_stream_byte_count(value["bytes"], label),
        "a full isolated process stream lost its exact base64 length",
    )
    try:
        original = base64.b64decode(
            value["base64"].encode("ascii"), validate=True,
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise RecorderError(
            "a complete native process stream is not canonical base64: "
            + label
        ) from error
    require(
        len(original) == value["bytes"]
        and hashlib.sha256(original).hexdigest() == value["sha256"]
        and base64.b64encode(original).decode("ascii") == value["base64"],
        "a complete native worker stream was truncated or substituted",
    )
    return original


def validate_compact_report_document(
    document: Any,
) -> dict[str, int]:
    validate_compact_bounds()
    require(
        type(document) is dict
        and document.get("schema") in {
            SCHEMA + "-complete-baseline-report",
            SCHEMA + "-complete-candidate-report",
        },
        "only one exact bounded public type evidence report can be published",
    )
    kind = (
        "baseline"
        if document["schema"] == SCHEMA + "-complete-baseline-report"
        else "candidate"
    )
    forbidden_duplicates = {
        "complete_decoded_baseline_process",
        "complete_baseline_result",
        "reference_a_records",
        "reference_b_records",
        "reference_a_process",
        "reference_b_process",
        "complete_decoded_candidate_process",
        "complete_candidate_result",
        "baseline_records",
        "candidate_records",
    }
    require(
        not (set(document) & forbidden_duplicates),
        "a complete canonical process or frozen vector was duplicated",
    )
    stdout_field = "complete_" + kind + "_process_stdout"
    stderr_field = "complete_" + kind + "_process_stderr"
    require(
        stdout_field in document and stderr_field in document,
        "retain each original isolated process stdout and stderr exactly once",
    )
    metadata = dict(document)
    encoded_bytes = 0
    for field in (stdout_field, stderr_field):
        stream = document[field]
        original = decode_stream(stream, field)
        require(
            len(original) == stream["bytes"],
            "a compact report substituted its complete raw process evidence",
        )
        encoded_bytes += len(stream["base64"])
        metadata[field] = {**stream, "base64": ""}
    require(
        encoded_bytes <= 2 * MAX_ENCODED_PROCESS_STREAM_BYTES,
        "two complete process streams exceed their exact base64 ceiling",
    )
    metadata_bytes = validate_compact_metadata_byte_count(
        len(canonical(metadata))
    )
    actual_bytes = metadata_bytes + encoded_bytes
    require(
        0 < actual_bytes <= MAX_COMPACT_REPORT_BYTES
        and actual_bytes < MAX_UNCOMPRESSED_BYTES,
        "a complete two-stream report exceeds its prospectively proven bound",
    )
    return {
        "metadata_bytes": metadata_bytes,
        "encoded_process_stream_bytes": encoded_bytes,
        "complete_report_bytes": actual_bytes,
    }



def run_one_process(
    arguments: list[str],
    *,
    mode: str = "baseline",
) -> dict[str, Any]:
    require(type(arguments) is list and bool(arguments)
            and arguments[0] == PINNED_PYTHON
            and all(type(item) is str for item in arguments)
            and mode in {"baseline", "candidate"},
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
    except Exception as error:
        return {
            "started": False, "pid": None, "returncode": None,
            "signal": None, "timed_out": False,
            "spawn_error": str(error), "stdout": b"", "stderr": b"",
        }
    timed_out = False
    try:
        try:
            stdout, stderr = process.communicate(
                timeout=PROCESS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            stdout, stderr = process.communicate()
        require(
            type(stdout) is bytes
            and type(stderr) is bytes
            and type(process.returncode) is int,
            "a genuine isolated worker lost its complete process streams",
        )
    except Exception as error:
        raw_stdout = getattr(error, "stdout", None)
        if raw_stdout is None:
            raw_stdout = getattr(error, "output", None)
        raw_stderr = getattr(error, "stderr", None)
        observed_stdout = raw_stdout if type(raw_stdout) is bytes else None
        observed_stderr = raw_stderr if type(raw_stderr) is bytes else None
        code = process.returncode
        if type(code) is not int:
            code = None
        raise ObservationFailure(
            "an already started public worker lost process communication: "
            + str(error),
            mode=mode,
            process={
                "started": True,
                "pid": process.pid,
                "returncode": code,
                "signal": -code if code is not None and code < 0 else None,
                "timed_out": timed_out
                or isinstance(error, subprocess.TimeoutExpired),
                "spawn_error": None,
                "stdout": observed_stdout,
                "stderr": observed_stderr,
            },
            report=None,
        ) from error
    return {
        "started": True, "pid": process.pid,
        "returncode": process.returncode,
        "signal": -process.returncode if process.returncode < 0 else None,
        "timed_out": timed_out, "spawn_error": None,
        "stdout": stdout, "stderr": stderr,
    }


def baseline_source_fields(
    recorder_pin: str,
    label: str,
) -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "label": validate_label(label),
        "recorder_relative": SOURCE_RELATIVE,
        "recorder_source_sha256": validate_digest(
            recorder_pin, "prospectively frozen public recorder"
        ),
        "parent_recorder_relative": PARENT_RECORDER_RELATIVE,
        "parent_recorder_sha256": PARENT_RECORDER_SHA256,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "previous_ownership_policy_relative": PREVIOUS_POLICY_RELATIVE,
        "previous_ownership_policy_sha256": PREVIOUS_POLICY_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "cohorts": list(COHORTS),
        "pickle_protocols": list(PICKLE_PROTOCOLS),
        "flag_values": list(FLAG_VALUES),
        "distinct_patterns_per_cohort": len(PATTERN_EXAMPLES),
        **validate_compact_bounds(),
    }


def validate_public_baseline_result(
    value: Any,
    oracle: Any,
    matrix: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
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
    additional = {
        "baseline_records_sha256", "source_owners", "reference_processes",
    }
    require(
        type(value) is dict and set(value) == set(expected) | additional,
        "the complete independently isolated public reference pair was forged",
    )
    for name, original in expected.items():
        require(
            value.get(name) == original
            and type(value.get(name)) is type(original),
            "a genuine frozen public reference field changed: " + name,
        )
    validate_digest(value["baseline_records_sha256"], "all public references")
    processes = value["reference_processes"]
    require(
        type(processes) is list and len(processes) == 2,
        "preserve both complete independently isolated public processes",
    )
    workers: list[dict[str, Any]] = []
    try:
        oracle.validate_source_owners(value["source_owners"], ORACLE_SHA256)
        for role, process in zip(
            ("reference_a", "reference_b"),
            processes,
            strict=True,
        ):
            require(
                type(process) is dict and process.get("role") == role,
                "an original complete public process was omitted or reordered",
            )
            worker = decode_document(
                decode_stream(process.get("stdout"), role + " stdout"),
                role + " complete canonical worker",
            )
            oracle.validate_reference_worker(
                worker,
                role=role,
                source_pin=ORACLE_SHA256,
                matrix=matrix,
                expected_pid=process.get("pid"),
            )
            oracle.validate_process_evidence(process, worker, role=role)
            workers.append(worker)
        observed = oracle.validate_reference_pair(
            workers[0],
            workers[1],
            processes[0],
            processes[1],
            source_pin=ORACLE_SHA256,
            matrix=matrix,
        )
    except Exception as error:
        raise RecorderError(
            "the frozen public oracle rejected its complete reference pair"
        ) from error
    require(
        observed == value["baseline_records_sha256"]
        and workers[0]["source_owners"]
        == workers[1]["source_owners"]
        == value["source_owners"]
        and workers[0]["records"] == workers[1]["records"],
        "the two losslessly reconstructed public references disagree",
    )
    return value, workers[0], workers[1]


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
    validate_frozen_source_owners(before, recorder_pin)
    if after is not None:
        validate_frozen_source_owners(after, recorder_pin)
    raw_stdout = process.get("stdout")
    raw_stderr = process.get("stderr")
    stdout = capture_stream(raw_stdout, "complete public controller stdout")
    stderr = capture_stream(raw_stderr, "complete public controller stderr")
    reasons: list[str] = []
    result: dict[str, Any] | None = None
    first: dict[str, Any] | None = None
    second: dict[str, Any] | None = None
    if process.get("started") is not True:
        reasons.append(
            "the isolated genuine public baseline could not start: "
            + str(process.get("spawn_error"))
        )
    if process.get("timed_out") is True:
        reasons.append("the independently isolated public baseline timed out")
    if raw_stdout:
        try:
            result, first, second = validate_public_baseline_result(
                decode_document(raw_stdout, "complete public baseline stdout"),
                oracle,
                matrix,
            )
        except Exception as error:
            reasons.append("invalid complete public baseline: " + str(error))
    if first is None or second is None:
        reasons.append(
            "agreement on all 6,912 public reference cases remains unknown"
        )
    if raw_stderr:
        reasons.append("the isolated public baseline emitted retained stderr")
    expected_exit = 0 if result is not None and not raw_stderr else 1
    if process.get("returncode") != expected_exit:
        reasons.append("the genuine public controller crashed or returned incorrectly")
    if post_run_error is not None:
        reasons.append("post-run public ownership changed: " + post_run_error)
    if before != after:
        reasons.append("an authenticated public source changed during observation")
    references: int | str = (
        2 if first is not None and second is not None
        else "UNKNOWN" if process.get("started") is True
        else 0
    )
    document = {
        "schema": SCHEMA + "-complete-baseline-report",
        "status": "FAIL" if reasons else "PASS",
        **baseline_source_fields(recorder_pin, label),
        "source_closure_before": dict(before),
        "source_closure_after": dict(after) if after is not None else None,
        "source_closure_unchanged": before == after,
        "complete_baseline_process_stdout": stdout,
        "complete_baseline_process_stderr": stderr,
        "complete_process_representation": "single-canonical-controller-stream",
        "baseline_result_reconstruction": (
            "decode-controller-then-authenticate-both-public-worker-streams"
        ),
        "baseline_result_sha256": digest(result) if result is not None else None,
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
            [first["pid"], second["pid"]]
            if first is not None and second is not None else None
        ),
        "actual_reference_workers": references,
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
        "all_failure_reasons": reasons,
        "failure_count": len(reasons),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    validate_compact_report_document(document)
    return document


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
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def validate_baseline_receipt(
    value: Any,
    pins: OwnerPins,
) -> dict[str, Any]:
    baseline = pins.baseline
    archive_relative, receipt_relative = approved_paths(
        "baseline", baseline.label,
    )
    expected = {
        "schema": SCHEMA + "-durable-baseline-publication-receipt",
        "status": "PASS",
        "baseline_result_status": "PASS",
        **baseline_source_fields(pins.recorder, baseline.label),
        "baseline_records_sha256": baseline.records,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "source_closure_unchanged": True,
        "report_relative": archive_relative,
        "report_sha256": baseline.archive,
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
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    extra = {
        "baseline_reference_pids",
        "source_closure_before",
        "source_closure_after",
        "report_bytes",
        "report_uncompressed_sha256",
        "report_uncompressed_bytes",
    }
    require(
        type(value) is dict and set(value) == set(expected) | extra,
        "the complete two-reference public baseline receipt was forged",
    )
    for name, original in expected.items():
        require(
            value.get(name) == original
            and type(value.get(name)) is type(original),
            "a signed public baseline receipt changed: " + name,
        )
    pids = value["baseline_reference_pids"]
    require(
        type(pids) is list
        and len(pids) == 2
        and all(type(pid) is int and pid > 0 for pid in pids)
        and pids[0] != pids[1],
        "two independently isolated genuine public PIDs are mandatory",
    )
    require(
        type(value["report_bytes"]) is int
        and 0 < value["report_bytes"] <= MAX_ARCHIVE_BYTES
        and type(value["report_uncompressed_bytes"]) is int
        and 0 < value["report_uncompressed_bytes"] <= MAX_COMPACT_REPORT_BYTES,
        "the signed lossless public archive exceeds its proven bound",
    )
    validate_digest(
        value["report_uncompressed_sha256"],
        "signed complete uncompressed public baseline",
    )
    validate_frozen_source_owners(value["source_closure_before"], pins.recorder)
    validate_frozen_source_owners(value["source_closure_after"], pins.recorder)
    require(
        value["source_closure_before"] == value["source_closure_after"],
        "a signed public baseline owner changed",
    )
    return value


def authenticate_baseline_receipt(
    pins: OwnerPins,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _, relative = approved_paths("baseline", pins.baseline.label)
    owner, raw = read_owned_regular(
        relative, pins.baseline.receipt, MAX_SOURCE_BYTES, retain=True,
    )
    require(raw is not None, "retain the complete signed public receipt")
    return (
        validate_baseline_receipt(
            decode_document(raw, "signed complete public receipt"),
            pins,
        ),
        owner,
    )


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
        and value.get("status") == "PASS"
        and len(canonical(value)) == receipt["report_uncompressed_bytes"]
        and digest(value) == receipt["report_uncompressed_sha256"],
        "the exact compact public baseline differs from its signed receipt",
    )
    for name, original in baseline_source_fields(
        pins.recorder, pins.baseline.label,
    ).items():
        require(
            value.get(name) == original
            and type(value.get(name)) is type(original),
            "the signed public baseline changed a frozen field: " + name,
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
        and value.get("complete_process_representation")
        == "single-canonical-controller-stream"
        and value.get("failure_count") == 0
        and value.get("all_failure_reasons") == []
        and value.get("clock_samples") == 0
        and value.get("timing_trials_run") == 0
        and value.get("benchmark_files_read") == 0
        and value.get("hidden_cases_read") == 0
        and value.get("performance") == "NOT MEASURED",
        "the complete signed public baseline did not pass",
    )
    validate_compact_report_document(value)
    require(
        decode_stream(
            value["complete_baseline_process_stderr"],
            "complete signed public baseline stderr",
        ) == b"",
        "a successful signed public reference concealed stderr",
    )
    result, first, second = validate_public_baseline_result(
        decode_document(
            decode_stream(
                value["complete_baseline_process_stdout"],
                "complete signed public controller stdout",
            ),
            "complete signed public baseline controller",
        ),
        oracle,
        matrix,
    )
    require(
        digest(result) == value.get("baseline_result_sha256")
        and result["baseline_records_sha256"] == pins.baseline.records
        and [first["pid"], second["pid"]]
        == value["baseline_reference_pids"],
        "both complete public reference streams were substituted",
    )
    return {
        **value,
        "complete_baseline_result": result,
        "reference_a_records": first["records"],
        "reference_b_records": second["records"],
        "reference_a_process": result["reference_processes"][0],
        "reference_b_process": result["reference_processes"][1],
    }


def revalidate_derived_baseline(
    value: Any,
    pins: OwnerPins,
    oracle: Any,
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    derived_fields = frozenset({
        "complete_baseline_result",
        "reference_a_records",
        "reference_b_records",
        "reference_a_process",
        "reference_b_process",
    })
    require(
        type(value) is dict and derived_fields <= set(value),
        "retain all five exactly reconstructed signed public reference fields",
    )
    compact = {
        name: original
        for name, original in value.items()
        if name not in derived_fields
    }
    validated = validate_archived_baseline(
        compact, pins, oracle, matrix, receipt,
    )
    for name in derived_fields:
        require(
            type(value[name]) is type(validated[name])
            and value[name] == validated[name],
            "a signed in-memory public reference was forged: " + name,
        )
    return validated


def stream_baseline_archive(
    pins: OwnerPins,
    oracle: Any,
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    relative, _ = approved_paths("baseline", pins.baseline.label)
    owner, _ = read_owned_regular(
        relative, pins.baseline.archive, MAX_ARCHIVE_BYTES,
    )
    require(
        owner["bytes"] == receipt["report_bytes"],
        "the signed lossless public archive size was changed",
    )
    with open_owned_descriptor(relative) as (descriptor, observed):
        require(
            (observed.st_dev, observed.st_ino)
            == (owner["device"], owner["inode"]),
            "the signed lossless public archive inode was exchanged",
        )
        pieces: list[bytes] = []
        plain_hash = hashlib.sha256()
        plain_count = 0
        try:
            with io.FileIO(descriptor, "rb", closefd=False) as source:
                with gzip.GzipFile(fileobj=source, mode="rb") as compressed:
                    while True:
                        chunk = compressed.read(131_072)
                        require(
                            type(chunk) is bytes,
                            "a signed public archive returned invalid evidence",
                        )
                        if not chunk:
                            break
                        plain_count += len(chunk)
                        require(
                            plain_count <= MAX_COMPACT_REPORT_BYTES,
                            "the signed public archive exceeds its frozen bound",
                        )
                        plain_hash.update(chunk)
                        pieces.append(chunk)
        except (OSError, EOFError, gzip.BadGzipFile) as error:
            raise RecorderError(
                "the exact signed public gzip is corrupted or incomplete"
            ) from error
    require(
        plain_count == receipt["report_uncompressed_bytes"]
        and plain_hash.hexdigest() == receipt["report_uncompressed_sha256"],
        "the signed complete public archive was truncated or substituted",
    )
    return (
        validate_archived_baseline(
            decode_document(b"".join(pieces), "signed complete public baseline"),
            pins,
            oracle,
            matrix,
            receipt,
        ),
        owner,
    )


def make_audit_manifest(
    pins: OwnerPins,
    oracle: Any,
    audit: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    spec = family_spec(pins.family)
    sources = [
        relative + "=" + pinned
        for relative, pinned in pins.owned_sources
    ]
    native_map = {spec.engine_relative: pins.engine}
    if spec.bridge_relative != spec.engine_relative:
        native_map[spec.bridge_relative] = pins.bridge
    binaries = [
        relative + "=" + pinned
        for relative, pinned in native_map.items()
    ]
    try:
        manifest = oracle.validate_family_manifest(
            spec.name, pins.adapter, pins.engine, pins.bridge,
            sources, binaries,
        )
        audited = audit.validate_family_pins(
            spec.name, pins.adapter, pins.engine, pins.bridge,
            sources, binaries,
        )
        audit.validate_manifest(audited, spec.name)
    except Exception as error:
        raise RecorderError(
            "the frozen public oracle or complete V3 native manifest rejected "
            + spec.name
        ) from error
    require(
        audited == {
            **manifest,
            "immutable_policy_sha256": {
                PREVIOUS_POLICY_RELATIVE: PREVIOUS_POLICY_SHA256,
                V5_RELATIVE: V5_SHA256,
            },
        },
        "the public family manifest does not match exact V3/V5 ownership",
    )
    return manifest, audited


def authenticate_family_closure(
    pins: OwnerPins,
    oracle: Any,
    v5: Any,
    audit: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    spec = family_spec(pins.family)
    native_pins = {
        "source": pins.adapter,
        "native_engine": pins.engine,
        "native_bridge": pins.bridge,
    }
    try:
        chosen = v5.family_spec(spec.name)
        require(
            chosen.adapter_module == spec.adapter_module
            and chosen.adapter_relative == spec.adapter_relative
            and chosen.engine_relative == spec.engine_relative
            and chosen.bridge_module == spec.bridge_module
            and chosen.bridge_relative == spec.bridge_relative
            and chosen.owned_ctypes is spec.owned_ctypes
            and v5.validate_pins(native_pins, chosen) == native_pins,
            "the frozen public native family escaped its exact V5 owner",
        )
        manifest, audited = make_audit_manifest(pins, oracle, audit)
        complete = audit.authenticate_closure(
            spec.name, audited, AUDIT_SHA256,
        )
        serializable = audit.serializable_owners(complete)
        audit.validate_serializable_owners(
            serializable, spec.name, audited, AUDIT_SHA256,
        )
    except Exception as error:
        raise RecorderError(
            "the complete genuinely owned public source/native closure failed"
        ) from error
    return serializable, manifest


def run_candidate_process(
    pins: OwnerPins,
    oracle: Any,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        arguments = oracle.candidate_arguments(manifest, ORACLE_SHA256)
    except Exception as error:
        raise RecorderError(
            "the frozen public oracle could not build its isolated native worker"
        ) from error
    require(
        type(arguments) is list
        and len(arguments) >= 16
        and arguments[:4] == [
            PINNED_PYTHON,
            "-I",
            "-B",
            ROOT + "/" + ORACLE_RELATIVE,
        ]
        and "--internal-candidate-worker" in arguments
        and "--candidate" in arguments
        and pins.family in arguments,
        "execute only the exact frozen V5-guarded public candidate worker",
    )
    return run_one_process(arguments, mode="candidate")


def reconstruct_mismatch_evidence(
    matrix: list[dict[str, Any]],
    references: list[dict[str, Any]],
    observed: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int]]:
    require(
        type(matrix) is list
        and type(references) is list
        and type(observed) is list
        and len(matrix) == len(references) == len(observed) == CASE_COUNT,
        "retain all 6,912 frozen reference and native public observations",
    )
    by_cohort = {name: 0 for name in COHORTS}
    by_domain = {"str": 0, "bytes": 0}
    evidence: list[dict[str, Any]] = []
    for index, (case, first, second) in enumerate(
        zip(matrix, references, observed, strict=True)
    ):
        require(
            type(first) is dict
            and type(second) is dict
            and all(
                first.get(name) == second.get(name) == case.get(name)
                for name in (
                    "case", "cohort", "domain",
                    "pattern_index", "flags", "pickle_protocol",
                )
            )
            and case["cohort"] in by_cohort
            and case["domain"] in by_domain,
            "a complete public mismatch case or source order was forged",
        )
        if first["outcome"] != second["outcome"]:
            by_cohort[case["cohort"]] += 1
            by_domain[case["domain"]] += 1
            evidence.append({
                "index": index,
                "case": case["case"],
                "cohort": case["cohort"],
                "domain": case["domain"],
                "pattern_index": case["pattern_index"],
                "flags": case["flags"],
                "pickle_protocol": case["pickle_protocol"],
                "baseline_outcome_sha256": digest(first["outcome"]),
                "candidate_outcome_sha256": digest(second["outcome"]),
            })
    require(
        sum(by_cohort.values()) == sum(by_domain.values()) == len(evidence),
        "a genuine public mismatch was silently omitted",
    )
    return evidence, by_cohort, by_domain


def validate_mismatch_evidence(
    evidence: Any,
    matrix: list[dict[str, Any]],
    references: list[dict[str, Any]],
    observed: list[dict[str, Any]],
    expected: str,
) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int]]:
    validate_digest(expected, "lossless public mismatch ledger")
    original, by_cohort, by_domain = reconstruct_mismatch_evidence(
        matrix, references, observed,
    )
    require(
        type(evidence) is list
        and evidence == original
        and digest(evidence) == expected,
        "a public mismatch was omitted, reordered or disconnected from outcomes",
    )
    return original, by_cohort, by_domain


def build_candidate_report(
    pins: OwnerPins,
    label: str,
    process: Mapping[str, Any],
    matrix: list[dict[str, Any]],
    receipt: Mapping[str, Any],
    reference: Mapping[str, Any],
    before: Mapping[str, Any],
    after: Mapping[str, Any] | None,
    manifest: Mapping[str, Any],
    oracle: Any,
    *,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    spec = family_spec(pins.family)
    validate_label(label)
    validate_baseline_receipt(receipt, pins)
    restored = revalidate_derived_baseline(
        reference, pins, oracle, matrix, receipt,
    )
    stdout_raw, stderr_raw = process.get("stdout"), process.get("stderr")
    stdout = capture_stream(stdout_raw, "complete native public stdout")
    stderr = capture_stream(stderr_raw, "complete native public stderr")
    reasons: list[str] = []
    candidate: dict[str, Any] | None = None
    if process.get("started") is not True:
        reasons.append(
            "the independently owned public candidate could not start: "
            + str(process.get("spawn_error"))
        )
    if process.get("timed_out") is True:
        reasons.append("the isolated native public candidate timed out")
    if stdout_raw:
        try:
            candidate = oracle.validate_candidate_worker(
                decode_document(
                    stdout_raw, "complete guarded public candidate stdout",
                ),
                manifest=manifest,
                source_pin=ORACLE_SHA256,
                matrix=matrix,
                expected_pid=process.get("pid"),
            )
        except Exception as error:
            reasons.append("invalid complete public candidate: " + str(error))
    if candidate is None:
        reasons.append("all 6,912 public candidate outcomes remain unknown")
    if stderr_raw:
        reasons.append("the isolated public candidate emitted complete stderr")
    expected_exit = 0 if candidate is not None and not stderr_raw else 1
    if process.get("returncode") != expected_exit:
        reasons.append("the native public candidate crashed or returned wrongly")
    if post_run_error is not None:
        reasons.append("post-run public native ownership changed: " + post_run_error)
    if before != after:
        reasons.append("the complete independently owned source closure changed")
    mismatches = None
    by_cohort = None
    by_domain = None
    mismatch_hash = None
    if candidate is not None:
        mismatches, by_cohort, by_domain = reconstruct_mismatch_evidence(
            matrix,
            restored["reference_a_records"],
            candidate["records"],
        )
        mismatch_hash = digest(mismatches)
        validate_mismatch_evidence(
            mismatches,
            matrix,
            restored["reference_a_records"],
            candidate["records"],
            mismatch_hash,
        )
        if mismatches:
            reasons.append(
                "the native candidate differs on "
                + str(len(mismatches))
                + " frozen public cases"
            )
    actual_candidates: int | str = (
        1 if candidate is not None
        else "UNKNOWN" if process.get("started") is True
        else 0
    )
    guard = candidate["candidate_guard"] if candidate is not None else None
    document = {
        "schema": SCHEMA + "-complete-candidate-report",
        "status": "FAIL" if reasons else "PASS",
        **baseline_source_fields(pins.recorder, label),
        "candidate_family": spec.name,
        "candidate_source_sha256": pins.adapter,
        "native_engine_sha256": pins.engine,
        "native_bridge_sha256": pins.bridge,
        "baseline_label": pins.baseline.label,
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
        "audit_manifest": dict(manifest),
        "complete_candidate_process_stdout": stdout,
        "complete_candidate_process_stderr": stderr,
        "complete_process_representation": "single-canonical-candidate-stream",
        "baseline_records_reconstruction": (
            "authenticate-pinned-complete-public-baseline-archive"
        ),
        "candidate_records_reconstruction": (
            "decode-and-validate-complete-guarded-public-candidate-stdout"
        ),
        "mismatch_outcome_reconstruction": (
            "frozen-public-matrix-plus-signed-baseline-plus-candidate-stdout"
        ),
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": (
            len(candidate["records"]) if candidate is not None else None
        ),
        "candidate_records_sha256": (
            candidate["records_sha256"] if candidate is not None else None
        ),
        "matched_case_count": (
            CASE_COUNT - len(mismatches) if mismatches is not None else None
        ),
        "mismatch_count": len(mismatches) if mismatches is not None else None,
        "all_mismatches": mismatches,
        "mismatch_evidence_sha256": mismatch_hash,
        "mismatches_by_cohort": by_cohort,
        "mismatches_by_domain": by_domain,
        "all_mismatches_preserved": True if mismatches is not None else None,
        "actual_method_guard_checks": (
            guard["actual_method_guard_checks"] if guard is not None else None
        ),
        "actual_warning_registry_guard_checks": (
            guard["actual_warning_registry_guard_checks"]
            if guard is not None else None
        ),
        "validated_prior_reference_workers": 2,
        "actual_reference_workers": 0,
        "actual_candidate_workers": actual_candidates,
        "actual_candidate_imports": (
            candidate["actual_candidate_imports"]
            if candidate is not None
            else "UNKNOWN" if process.get("started") is True
            else 0
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
        "actual_candidate_process_spawn_error": process.get("spawn_error"),
        "all_failure_reasons": reasons,
        "failure_count": len(reasons),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    validate_compact_report_document(document)
    return document



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
        **baseline_source_fields(pins.recorder, label),
        "candidate_family": pins.family,
        "candidate_source_sha256": pins.adapter,
        "native_engine_sha256": pins.engine,
        "native_bridge_sha256": pins.bridge,
        "baseline_label": pins.baseline.label,
        "baseline_receipt_sha256": pins.baseline.receipt,
        "baseline_archive_sha256": pins.baseline.archive,
        "baseline_records_sha256": pins.baseline.records,
        "baseline_reference_pids": report["baseline_reference_pids"],
        "validated_baseline_record_count": (
            report["validated_baseline_record_count"]
        ),
        "validated_candidate_record_count": (
            report["validated_candidate_record_count"]
        ),
        "matched_case_count": report["matched_case_count"],
        "mismatch_count": report["mismatch_count"],
        "mismatch_evidence_sha256": report["mismatch_evidence_sha256"],
        "mismatches_by_cohort": report["mismatches_by_cohort"],
        "mismatches_by_domain": report["mismatches_by_domain"],
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
        "report_atomic_no_overwrite_link": (
            publication["atomic_no_overwrite_link"]
        ),
        "report_complete_readback_verified": (
            publication["complete_readback_verified"]
        ),
        "receipt_relative": preflight["receipt_relative"],
        "approved_fresh_path_count": preflight["approved_fresh_path_count"],
        "fresh_paths_checked_before_candidate": (
            preflight["fresh_paths_checked_before_observation"]
        ),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def capture_failure_stream(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {
            "base64": None,
            "bytes": "UNKNOWN",
            "sha256": None,
            "complete": False,
            "capture_failure": True,
        }
    require(type(value) is bytes, "retain complete failed process bytes: " + label)
    if len(value) <= MAX_PROCESS_BYTES:
        return capture_stream(value, label)
    return {
        "base64": None,
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": False,
        "maximum_complete_stream_bytes": MAX_PROCESS_BYTES,
        "size_limit_exceeded": True,
    }


def validate_failure_stream(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is dict, "retain exact failed public process evidence")
    if value.get("complete") is True:
        decode_stream(value, label)
        return value
    if value.get("capture_failure") is True:
        require(
            set(value) == {
                "base64", "bytes", "sha256", "complete", "capture_failure",
            }
            and value.get("base64") is None
            and value.get("bytes") == "UNKNOWN"
            and value.get("sha256") is None
            and value.get("complete") is False,
            "unobserved failed public process bytes were falsely measured",
        )
        return value
    require(
        set(value) == {
            "base64", "bytes", "sha256", "complete",
            "maximum_complete_stream_bytes", "size_limit_exceeded",
        }
        and value.get("base64") is None
        and type(value.get("bytes")) is int
        and value["bytes"] > MAX_PROCESS_BYTES
        and value.get("complete") is False
        and value.get("maximum_complete_stream_bytes") == MAX_PROCESS_BYTES
        and value.get("size_limit_exceeded") is True,
        "an oversized failed public process was silently truncated",
    )
    validate_digest(value["sha256"], label)
    return value


def validate_observation_failure_document(value: Any) -> dict[str, Any]:
    expected = {
        "schema": SCHEMA + "-post-invocation-failure",
        "status": "FAIL",
        "publication_status": "FAIL",
        "parent_recorder_relative": PARENT_RECORDER_RELATIVE,
        "parent_recorder_sha256": PARENT_RECORDER_SHA256,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        **validate_compact_bounds(),
        "actual_process_invocations": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    extra = {
        "mode", "error_type", "error", "actual_process_pid",
        "actual_process_returncode", "actual_process_signal",
        "actual_process_timed_out", "actual_process_spawn_error",
        "complete_actual_process_stdout", "complete_actual_process_stderr",
        "actual_reference_workers", "actual_candidate_workers",
        "actual_candidate_imports", "actual_baseline_controller_invocations",
        "actual_candidate_process_invocations",
        "validated_reference_a_case_count", "validated_reference_b_case_count",
        "validated_candidate_record_count", "baseline_reference_pids",
        "published_report", "published_receipt",
        "published_evidence_file_count", "workspace_files_written",
        "evidence_files_created", "reference_outcomes_known",
        "candidate_outcomes_known",
    }
    require(
        type(value) is dict and set(value) == set(expected) | extra,
        "a complete genuine post-invocation public failure was hidden",
    )
    for name, original in expected.items():
        require(
            value.get(name) == original
            and type(value.get(name)) is type(original),
            "an actual failed public process changed a pinned field: " + name,
        )
    require(
        value["mode"] in {"baseline", "candidate"}
        and type(value.get("error_type")) is str
        and type(value.get("error")) is str
        and type(value.get("actual_process_pid")) is int
        and value["actual_process_pid"] > 0
        and (
            value.get("actual_process_returncode") is None
            or type(value["actual_process_returncode"]) is int
        )
        and (
            value.get("actual_process_signal") is None
            or type(value["actual_process_signal"]) is int
        )
        and type(value.get("actual_process_timed_out")) is bool
        and (
            value.get("actual_process_spawn_error") is None
            or type(value["actual_process_spawn_error"]) is str
        ),
        "a genuine public process PID, exit, timeout or failure was forged",
    )
    validate_failure_stream(
        value["complete_actual_process_stdout"], "failed public stdout",
    )
    validate_failure_stream(
        value["complete_actual_process_stderr"], "failed public stderr",
    )
    if value["mode"] == "baseline":
        require(
            value["actual_baseline_controller_invocations"] == 1
            and value["actual_candidate_process_invocations"] == 0
            and value["actual_candidate_workers"] == 0
            and value["actual_candidate_imports"] == 0
            and value["actual_reference_workers"] in {2, "UNKNOWN"},
            "an already started public reference was falsely called unrun",
        )
    else:
        require(
            value["actual_baseline_controller_invocations"] == 0
            and value["actual_candidate_process_invocations"] == 1
            and value["actual_reference_workers"] == 0
            and value["actual_candidate_workers"] in {1, "UNKNOWN"}
            and (
                value["actual_candidate_imports"] == "UNKNOWN"
                or type(value["actual_candidate_imports"]) is int
                and value["actual_candidate_imports"] >= 2
            ),
            "an already started public native worker was falsely called unrun",
        )
    require(
        value["reference_outcomes_known"]
        is (value["actual_reference_workers"] == 2)
        and value["candidate_outcomes_known"]
        is (value["actual_candidate_workers"] == 1),
        "unknown public results were falsely reported as measured",
    )
    published = int(value["published_report"] is not None) + int(
        value["published_receipt"] is not None
    )
    require(
        value["published_evidence_file_count"] == published
        and value["workspace_files_written"] == published
        and value["evidence_files_created"] == published
        and (
            value["published_receipt"] is None
            or value["published_report"] is not None
        ),
        "partial public archive or receipt publication was concealed",
    )
    if value["actual_reference_workers"] == 2:
        pids = value["baseline_reference_pids"]
        require(
            type(pids) is list and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1]
            and value["validated_reference_a_case_count"] == CASE_COUNT
            and value["validated_reference_b_case_count"] == CASE_COUNT,
            "a known complete public reference or denominator was forged",
        )
    else:
        require(
            value["validated_reference_a_case_count"] is None
            and value["validated_reference_b_case_count"] is None
            and (
                value["baseline_reference_pids"] is None
                or value["mode"] == "candidate"
            ),
            "unknown standard public outcomes were silently fabricated",
        )
    if value["actual_candidate_workers"] == 1:
        require(
            value["validated_candidate_record_count"] == CASE_COUNT,
            "a known public candidate denominator was substituted",
        )
    else:
        require(
            value["validated_candidate_record_count"] is None,
            "an unknown public native outcome was falsely disclosed",
        )
    return value


def observation_failure_document(
    error: ObservationFailure,
) -> dict[str, Any]:
    require(
        isinstance(error, ObservationFailure)
        and error.mode in {"baseline", "candidate"}
        and type(error.process) is dict
        and error.process.get("started") is True
        and type(error.process.get("pid")) is int
        and error.process["pid"] > 0,
        "retain an actual started public reference or native process",
    )
    report = error.report
    references: int | str = (
        report.get("actual_reference_workers")
        if report is not None
        else "UNKNOWN" if error.mode == "baseline"
        else 0
    )
    candidates: int | str = (
        report.get("actual_candidate_workers")
        if report is not None
        else "UNKNOWN" if error.mode == "candidate"
        else 0
    )
    if references is None:
        references = "UNKNOWN"
    if candidates is None:
        candidates = "UNKNOWN"
    published = int(error.report_publication is not None) + int(
        error.receipt_publication is not None
    )
    value = {
        "schema": SCHEMA + "-post-invocation-failure",
        "status": "FAIL",
        "publication_status": "FAIL",
        "mode": error.mode,
        "error_type": type(error).__qualname__,
        "error": str(error),
        "parent_recorder_relative": PARENT_RECORDER_RELATIVE,
        "parent_recorder_sha256": PARENT_RECORDER_SHA256,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        **validate_compact_bounds(),
        "actual_process_invocations": 1,
        "actual_process_pid": error.process["pid"],
        "actual_process_returncode": error.process.get("returncode"),
        "actual_process_signal": error.process.get("signal"),
        "actual_process_timed_out": error.process.get("timed_out") is True,
        "actual_process_spawn_error": error.process.get("spawn_error"),
        "complete_actual_process_stdout": capture_failure_stream(
            error.process.get("stdout"), "failed complete public stdout",
        ),
        "complete_actual_process_stderr": capture_failure_stream(
            error.process.get("stderr"), "failed complete public stderr",
        ),
        "actual_reference_workers": references,
        "actual_candidate_workers": candidates,
        "actual_candidate_imports": (
            0 if error.mode == "baseline"
            else report.get("actual_candidate_imports", "UNKNOWN")
            if report is not None else "UNKNOWN"
        ),
        "actual_baseline_controller_invocations": int(
            error.mode == "baseline"
        ),
        "actual_candidate_process_invocations": int(
            error.mode == "candidate"
        ),
        "validated_reference_a_case_count": (
            report.get("validated_reference_a_case_count")
            if report is not None else None
        ),
        "validated_reference_b_case_count": (
            report.get("validated_reference_b_case_count")
            if report is not None else None
        ),
        "validated_candidate_record_count": (
            report.get("validated_candidate_record_count")
            if report is not None else None
        ),
        "baseline_reference_pids": (
            report.get("baseline_reference_pids")
            if report is not None else None
        ),
        "published_report": error.report_publication,
        "published_receipt": error.receipt_publication,
        "published_evidence_file_count": published,
        "workspace_files_written": published,
        "evidence_files_created": published,
        "reference_outcomes_known": references == 2,
        "candidate_outcomes_known": candidates == 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return validate_observation_failure_document(value)


def record_baseline(
    recorder_pin: str,
    oracle_pin: str,
    matrix_pin: str,
    label: str,
) -> dict[str, Any]:
    verify_runtime()
    require(
        validate_digest(oracle_pin, "frozen public type oracle")
        == ORACLE_SHA256
        and validate_digest(matrix_pin, "frozen public type matrix")
        == MATRIX_SHA256,
        "explicitly pin the unchanged genuine public oracle and matrix",
    )
    oracle, _, _, matrix, before = authenticate_frozen_tools(
        validate_digest(recorder_pin, "frozen public evidence recorder")
    )
    process = None
    report = None
    publication = None
    receipt_publication = None
    try:
        with preflight_fresh_outputs("baseline", label) as preflight:
            process = run_one_process([
                PINNED_PYTHON, "-I", "-B", ROOT + "/" + ORACLE_RELATIVE,
                "--record-baseline",
                "--oracle-source-sha256", ORACLE_SHA256,
                "--matrix-sha256", MATRIX_SHA256,
            ])
            verify_retained_directory(preflight)
            after = None
            post_error = None
            try:
                after = authenticate_frozen_tools(recorder_pin)[4]
            except Exception as error:
                post_error = str(error)
            report = build_baseline_report(
                recorder_pin, label, process, oracle, matrix, before, after,
                post_run_error=post_error,
            )
            publication = publish_document(preflight, report, compressed=True)
            receipt = make_baseline_receipt(
                recorder_pin, label, report, publication, preflight,
            )
            receipt_publication = publish_document(
                preflight, receipt, compressed=False,
            )
            verify_runtime()
            require(
                report is not None and publication is not None
                and receipt_publication is not None,
                "a complete public baseline publication was concealed",
            )
    except Exception as error:
        if process is not None and process.get("started") is True:
            raise ObservationFailure(
                "post-invocation public baseline failure: " + str(error),
                mode="baseline",
                process=process,
                report=report,
                report_publication=publication,
                receipt_publication=receipt_publication,
            ) from error
        raise
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
        "source_closure_unchanged": report["source_closure_unchanged"],
        "report_publication": publication,
        "receipt_publication": receipt_publication,
        "all_failure_reasons": report["all_failure_reasons"],
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def record_candidate(pins: OwnerPins, label: str) -> dict[str, Any]:
    verify_runtime()
    spec = family_spec(pins.family)
    oracle, v5, audit, matrix, _ = authenticate_frozen_tools(pins.recorder)
    receipt, _ = authenticate_baseline_receipt(pins)
    reference, _ = stream_baseline_archive(pins, oracle, matrix, receipt)
    before, manifest = authenticate_family_closure(pins, oracle, v5, audit)
    process = None
    report = None
    publication = None
    receipt_publication = None
    try:
        with preflight_fresh_outputs(
            "candidate", label, spec.name,
        ) as preflight:
            process = run_candidate_process(pins, oracle, manifest)
            verify_retained_directory(preflight)
            after = None
            post_error = None
            try:
                after, after_manifest = authenticate_family_closure(
                    pins, oracle, v5, audit,
                )
                require(
                    manifest == after_manifest,
                    "the complete signed public native manifest changed",
                )
                authenticate_frozen_tools(pins.recorder)
            except Exception as error:
                post_error = str(error)
            report = build_candidate_report(
                pins, label, process, matrix, receipt,
                reference, before, after, manifest, oracle,
                post_run_error=post_error,
            )
            publication = publish_document(preflight, report, compressed=True)
            receipt_document = make_candidate_receipt(
                pins, label, report, publication, preflight,
            )
            receipt_publication = publish_document(
                preflight, receipt_document, compressed=False,
            )
            verify_runtime()
            require(
                report is not None and publication is not None
                and receipt_publication is not None,
                "a complete public native publication was concealed",
            )
    except Exception as error:
        if process is not None and process.get("started") is True:
            raise ObservationFailure(
                "post-invocation public candidate failure: " + str(error),
                mode="candidate",
                process=process,
                report=report,
                report_publication=publication,
                receipt_publication=receipt_publication,
            ) from error
        raise
    return {
        "schema": SCHEMA + "-recorded-candidate",
        "status": report["status"],
        "publication_status": "PASS",
        **baseline_source_fields(pins.recorder, label),
        "candidate_family": spec.name,
        "baseline_label": pins.baseline.label,
        "baseline_records_sha256": pins.baseline.records,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": (
            report["validated_candidate_record_count"]
        ),
        "matched_case_count": report["matched_case_count"],
        "mismatch_count": report["mismatch_count"],
        "mismatch_evidence_sha256": report["mismatch_evidence_sha256"],
        "actual_reference_workers": 0,
        "validated_prior_reference_workers": 2,
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_candidate_imports": report["actual_candidate_imports"],
        "actual_candidate_process_invocations": (
            report["actual_candidate_process_invocations"]
        ),
        "actual_method_guard_checks": report["actual_method_guard_checks"],
        "actual_warning_registry_guard_checks": (
            report["actual_warning_registry_guard_checks"]
        ),
        "source_closure_unchanged": report["candidate_owner_unchanged"],
        "report_publication": publication,
        "receipt_publication": receipt_publication,
        "all_failure_reasons": report["all_failure_reasons"],
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


PINNED_STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/"
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
UPSTREAM_TEST_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-upstream-source/"
    "Python-3.14.6/Lib/test/"
)
UPSTREAM_TEST_SOURCES = types.MappingProxyType({
    "upstream_test_re": (
        "test_re.py",
        "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
    ),
    "upstream_re_tests": (
        "re_tests.py",
        "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab",
    ),
})

IMMUTABLE_OWNERSHIP_POLICY_SHA256 = types.MappingProxyType({
    PREVIOUS_POLICY_RELATIVE: PREVIOUS_POLICY_SHA256,
    V5_RELATIVE: V5_SHA256,
})
FAMILY_NAMES = tuple(FAMILIES)
FAMILY_PATHS = types.MappingProxyType({
    name: types.MappingProxyType({
        "adapter": spec.adapter_relative,
        "engine": spec.engine_relative,
        "bridge": spec.bridge_relative,
        "sources": spec.owned_source_relatives,
        "binaries": tuple(dict.fromkeys((
            spec.engine_relative, spec.bridge_relative,
        ))),
    })
    for name, spec in FAMILIES.items()
})


def encode_stream(raw: bytes) -> dict[str, Any]:
    return capture_stream(raw, "synthetic complete public process")


def validate_source_owners(
    value: Any,
    source_pin: str,
) -> dict[str, dict[str, Any]]:
    expected: dict[str, tuple[str, str]] = {
        "oracle": (ROOT + "/" + ORACLE_RELATIVE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "v5_guard": (ROOT + "/" + V5_RELATIVE, V5_SHA256),
        "ownership_audit": (
            ROOT + "/" + AUDIT_RELATIVE,
            AUDIT_SHA256,
        ),
    }
    expected.update({
        name: (UPSTREAM_TEST_DIRECTORY + filename, pinned)
        for name, (filename, pinned) in UPSTREAM_TEST_SOURCES.items()
    })
    expected.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, pinned)
        for name, (filename, pinned) in PINNED_STDLIB_SOURCES.items()
    })
    require(
        type(value) is dict and set(value) == set(expected),
        "a complete pinned CPython, upstream, V5, or V3 owner was omitted",
    )
    for name, (path, pinned) in expected.items():
        owner = value.get(name)
        require(
            type(owner) is dict
            and set(owner) == {"path", "sha256", "bytes", "device", "inode"}
            and owner.get("path") == path
            and owner.get("sha256") == pinned
            and type(owner.get("bytes")) is int
            and owner["bytes"] > 0
            and type(owner.get("device")) is int
            and owner["device"] >= 0
            and type(owner.get("inode")) is int
            and owner["inode"] > 0,
            "a complete pinned public source owner was forged: " + name,
        )
    return value


def make_reference_guard(checks: int) -> dict[str, Any]:
    return {
        "candidate_import_count": 0,
        "external_regex_import_count": 0,
        "actual_method_guard_checks": checks,
        "required_method_guard_checks": 2 * CASE_COUNT,
        "preloaded_support_modules_guarded": True,
        "v5_guard_relative": V5_RELATIVE,
        "v5_guard_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "candidate_guard_installed": False,
    }


def validate_reference_guard(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and value == make_reference_guard(2 * CASE_COUNT),
        "a complete standard-reference and helper-identity guard was forged",
    )
    return value

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
        "an independently isolated genuine reference PID is mandatory",
    )
    expected = {
        "schema": ORACLE_SCHEMA + "-isolated-public-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "candidate_family": None,
        "pid": expected_pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "native_owners": None,
        "candidate_guard": None,
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
        "a complete genuine public reference worker was forged",
    )
    for name, original in expected.items():
        require(
            value[name] == original,
            "a genuine public reference field was substituted: " + name,
        )
    validate_source_owners(value["source_owners"], source_pin)
    validate_reference_guard(value["reference_guard"])
    validate_records(matrix, value["records"], value["records_sha256"])
    return value



def validate_process_evidence(
    value: Any,
    worker: Mapping[str, Any],
    *,
    role: str,
) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {
            "role", "pid", "returncode", "timed_out", "stdout", "stderr",
        }
        and value.get("role") == role
        and type(value.get("pid")) is int
        and value["pid"] > 0
        and value["pid"] == worker.get("pid")
        and value.get("returncode") == 0
        and value.get("timed_out") is False,
        "an independently isolated public worker process was substituted",
    )
    stdout = decode_stream(value["stdout"], role + " stdout")
    stderr = decode_stream(value["stderr"], role + " stderr")
    require(
        stderr == b"" and stdout == canonical(dict(worker)),
        "a complete canonical public worker outcome vector was concealed",
    )
    return value



def parse_pin_entries(values: Any, label: str) -> dict[str, str]:
    require(
        type(values) is list and bool(values),
        "explicitly pin every exact independent " + label,
    )
    result: dict[str, str] = {}
    for entry in values:
        require(type(entry) is str, "a complete path=SHA-256 pin is required")
        path, separator, source_hash = entry.partition("=")
        require(
            separator == "="
            and "=" not in source_hash
            and path.startswith("candidates/")
            and "\\" not in path
            and "\x00" not in path
            and all(part not in {"", ".", ".."} for part in path.split("/"))
            and path not in result,
            "an independent candidate pin was duplicated or escaped its root",
        )
        result[path] = validate_digest(source_hash, label + " " + path)
    return result


def validate_family_manifest(
    family: Any,
    candidate_source: Any,
    native_engine: Any,
    native_bridge: Any,
    source_entries: Any,
    native_entries: Any,
) -> dict[str, Any]:
    require(
        type(family) is str and family in FAMILY_NAMES,
        "select exactly one independent Rust, C, or Zig native owner",
    )
    spec = FAMILY_PATHS[family]
    sources = parse_pin_entries(source_entries, family + " source")
    natives = parse_pin_entries(native_entries, family + " native artifact")
    validate_digest(candidate_source, family + " independently owned adapter")
    validate_digest(native_engine, family + " independently owned engine")
    validate_digest(native_bridge, family + " independently owned bridge")
    require(
        set(sources) == set(spec["sources"])
        and set(natives) == set(spec["binaries"])
        and sources[spec["adapter"]] == candidate_source
        and natives[spec["engine"]] == native_engine
        and natives[spec["bridge"]] == native_bridge
        and (native_engine == native_bridge) == (family == "c")
        and len(set(sources.values())) == len(sources)
        and len(set(natives.values())) == len(natives),
        "the complete independent native source, lockfile, or engine "
        "closure was substituted",
    )
    return {
        "family": family,
        "candidate_source_sha256": candidate_source,
        "native_engine_sha256": native_engine,
        "native_bridge_sha256": native_bridge,
        "source_sha256": dict(sorted(sources.items())),
        "native_sha256": dict(sorted(natives.items())),
    }



def validate_relative_owner(
    value: Any,
    relative: str,
    expected: str,
) -> dict[str, Any]:
    validate_digest(expected, "exact independently owned " + relative)
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
        "a complete independently owned native file was forged: " + relative,
    )
    return value


def validate_native_evidence(
    value: Any,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    family = manifest["family"]
    require(
        type(value) is dict
        and set(value) == {
            "manifest", "audit_source_sha256", "owners",
            "v5_native_provenance",
        }
        and value.get("audit_source_sha256") == AUDIT_SHA256,
        "a complete independently frozen V3 native audit was omitted",
    )
    expected_manifest = {
        "family": family,
        "candidate_source_sha256": manifest["candidate_source_sha256"],
        "native_engine_sha256": manifest["native_engine_sha256"],
        "native_bridge_sha256": manifest["native_bridge_sha256"],
        "source_sha256": dict(manifest["source_sha256"]),
        "native_sha256": dict(manifest["native_sha256"]),
        "immutable_policy_sha256": dict(IMMUTABLE_OWNERSHIP_POLICY_SHA256),
    }
    require(
        type(value["manifest"]) is dict
        and value["manifest"] == expected_manifest,
        "the complete V3 candidate or immutable policy manifest changed",
    )
    owners = value["owners"]
    require(
        type(owners) is dict
        and set(owners) == {
            "family",
            "manifest",
            "source_owners",
            "native_owners",
            "policy_owners",
            "oracle_owner",
            "python_owner",
        }
        and owners.get("family") == family
        and owners.get("manifest") == expected_manifest,
        "the complete genuine V3 owner closure was substituted",
    )
    source_owners = owners.get("source_owners")
    native_owners = owners.get("native_owners")
    policy_owners = owners.get("policy_owners")
    require(
        type(source_owners) is dict
        and set(source_owners) == set(manifest["source_sha256"])
        and type(native_owners) is dict
        and set(native_owners) == set(manifest["native_sha256"])
        and type(policy_owners) is dict
        and set(policy_owners) == set(IMMUTABLE_OWNERSHIP_POLICY_SHA256),
        "a V3 source, native artifact, or immutable policy was omitted",
    )
    for relative, source_hash in manifest["source_sha256"].items():
        validate_relative_owner(
            source_owners[relative],
            relative,
            source_hash,
        )
    for relative, source_hash in manifest["native_sha256"].items():
        validate_relative_owner(
            native_owners[relative],
            relative,
            source_hash,
        )
    for relative, source_hash in IMMUTABLE_OWNERSHIP_POLICY_SHA256.items():
        validate_relative_owner(
            policy_owners[relative],
            relative,
            source_hash,
        )
    validate_relative_owner(
        owners["oracle_owner"],
        AUDIT_RELATIVE,
        AUDIT_SHA256,
    )
    python = owners["python_owner"]
    require(
        type(python) is dict
        and set(python) == {
            "path", "sha256", "bytes", "device", "inode",
        }
        and python.get("path") == PINNED_PYTHON
        and python.get("sha256") == PINNED_PYTHON_SHA256
        and type(python.get("bytes")) is int and python["bytes"] > 0
        and type(python.get("device")) is int and python["device"] >= 0
        and type(python.get("inode")) is int and python["inode"] > 0,
        "the genuine V3-owned pinned CPython executable was replaced",
    )
    provenance = value["v5_native_provenance"]
    require(
        type(provenance) is dict
        and set(provenance) == {
            "source", "native_engine", "native_bridge",
        },
        "the complete per-process V5 native provenance was hidden",
    )
    spec = FAMILY_PATHS[family]
    validate_relative_owner(
        provenance["source"],
        spec["adapter"],
        manifest["candidate_source_sha256"],
    )
    validate_relative_owner(
        provenance["native_engine"],
        spec["engine"],
        manifest["native_engine_sha256"],
    )
    validate_relative_owner(
        provenance["native_bridge"],
        spec["bridge"],
        manifest["native_bridge_sha256"],
    )
    return value



def snapshot_candidate_guard(
    active: Mapping[str, Any],
    family: str,
) -> dict[str, Any]:
    expected_true = (
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
    require(
        isinstance(active, Mapping)
        and all(active.get(name) is True for name in expected_true)
        and active.get("public_type_names_used_for_ownership") is False
        and active.get("actual_method_guard_checks") == 2 * CASE_COUNT
        and active.get("actual_warning_registry_guard_checks")
        == 2 * CASE_COUNT
        and active.get("owned_native_ffi_allowed") is (family == "zig")
        and active.get("trusted_stdlib_ctypes_preloaded")
        is (family == "zig")
        and active.get("trusted_stdlib_ctypes_builtin_verified")
        is (family == "zig")
        and active.get("trusted_stdlib_ctypes_pythonapi_initialized")
        is (family == "zig")
        and active.get("trusted_stdlib_ctypes_source_sha256")
        == (
            TRUSTED_CTYPES_SHA256
            if family == "zig" else None
        ),
        "a continuous per-case V5 public native-ownership guard was lost",
    )
    evidence: dict[str, Any] = {
        name: active[name] for name in expected_true
    }
    for name in (
        "public_type_names_used_for_ownership",
        "actual_method_guard_checks",
        "actual_warning_registry_guard_checks",
        "owned_native_ffi_allowed",
        "trusted_stdlib_ctypes_preloaded",
        "trusted_stdlib_ctypes_builtin_verified",
        "trusted_stdlib_ctypes_pythonapi_initialized",
        "trusted_stdlib_ctypes_source_sha256",
        "owned_ctypes_load_count",
        "owned_ctypes_symbol_count",
        "cached_original_matcher_descendant_count",
        "cached_original_holder_count",
    ):
        require(
            name in active,
            "a complete V5 guard field was omitted: " + name,
        )
        evidence[name] = active[name]
    for name in (
        "owned_ctypes_load_count",
        "owned_ctypes_symbol_count",
        "cached_original_matcher_descendant_count",
        "cached_original_holder_count",
    ):
        require(
            type(evidence[name]) is int and evidence[name] >= 0,
            "a genuine exact native guard counter was forged: " + name,
        )
    if family == "zig":
        require(
            evidence["owned_ctypes_load_count"] >= 1
            and evidence["owned_ctypes_symbol_count"] >= 1,
            "Zig did not actually load its exact owned native FFI engine",
        )
    else:
        require(
            evidence["owned_ctypes_load_count"] == 0
            and evidence["owned_ctypes_symbol_count"] == 0,
            "an unowned native FFI engine escaped into Rust or C",
        )
    return evidence



def validate_candidate_worker(
    value: Any,
    *,
    manifest: Mapping[str, Any],
    source_pin: str,
    matrix: list[dict[str, Any]],
    expected_pid: int,
) -> dict[str, Any]:
    family = manifest["family"]
    require(
        type(value) is dict
        and type(expected_pid) is int and expected_pid > 0
        and value.get("schema") == ORACLE_SCHEMA + "-isolated-public-worker"
        and value.get("status") == "OBSERVED"
        and value.get("python") == "3.14.6"
        and value.get("role") == "candidate-" + family
        and value.get("candidate_family") == family
        and value.get("pid") == expected_pid
        and value.get("oracle_source_sha256") == source_pin
        and value.get("matrix_sha256") == MATRIX_SHA256
        and value.get("published_seed") == PUBLISHED_SEED
        and value.get("case_count") == CASE_COUNT
        and value.get("cohort_count") == len(COHORTS)
        and value.get("variants_per_cohort") == VARIANTS_PER_COHORT
        and value.get("reference_guard") is None
        and value.get("actual_reference_workers") == 0
        and value.get("actual_candidate_workers") == 1
        and type(value.get("actual_candidate_imports")) is int
        and value["actual_candidate_imports"] >= 2
        and value.get("clock_samples") == 0
        and value.get("timing_trials_run") == 0
        and value.get("workspace_files_written") == 0
        and value.get("evidence_files_created") == 0
        and value.get("benchmark_files_read") == 0
        and value.get("hidden_cases_read") == 0
        and value.get("performance") == "NOT MEASURED"
        and value.get("candidate_qualified_for_hidden_benchmark") is False
        and value.get("final_winner_selected") is False
        and set(value) == {
            "schema", "status", "python", "role", "candidate_family",
            "pid", "oracle_source_sha256", "matrix_sha256",
            "published_seed", "case_count", "cohort_count",
            "variants_per_cohort", "records_sha256", "records",
            "source_owners", "reference_guard", "native_owners",
            "candidate_guard", "actual_reference_workers",
            "actual_candidate_workers", "actual_candidate_imports",
            "clock_samples", "timing_trials_run", "workspace_files_written",
            "evidence_files_created", "benchmark_files_read",
            "hidden_cases_read", "performance",
            "candidate_qualified_for_hidden_benchmark", "final_winner_selected",
        },
        "a genuine complete independently guarded public candidate was forged",
    )
    validate_source_owners(value["source_owners"], source_pin)
    validate_records(matrix, value["records"], value["records_sha256"])
    validate_native_evidence(value["native_owners"], manifest)
    snapshot_candidate_guard(value["candidate_guard"], family)
    return value



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
    validate_process_evidence(
        first_process,
        first,
        role="reference_a",
    )
    validate_process_evidence(
        second_process,
        second,
        role="reference_b",
    )
    require(
        first["pid"] != second["pid"]
        and first["source_owners"] == second["source_owners"]
        and first["records_sha256"] == second["records_sha256"]
        and first["records"] == second["records"],
        "two independently isolated genuine public references disagree",
    )
    return first["records_sha256"]



def synthetic_source_owners(source_pin: str) -> dict[str, dict[str, Any]]:
    values: dict[str, tuple[str, str]] = {
        "oracle": (ROOT + "/" + ORACLE_RELATIVE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "v5_guard": (ROOT + "/" + V5_RELATIVE, V5_SHA256),
        "ownership_audit": (
            ROOT + "/" + AUDIT_RELATIVE,
            AUDIT_SHA256,
        ),
    }
    values.update({
        name: (UPSTREAM_TEST_DIRECTORY + filename, pinned)
        for name, (filename, pinned) in UPSTREAM_TEST_SOURCES.items()
    })
    values.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, pinned)
        for name, (filename, pinned) in PINNED_STDLIB_SOURCES.items()
    })
    return {
        name: {
            "path": path,
            "sha256": pinned,
            "bytes": 4_096 + index,
            "device": 7,
            "inode": 10_000 + index,
        }
        for index, (name, (path, pinned)) in enumerate(values.items())
    }


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "case": case["case"],
            "cohort": case["cohort"],
            "domain": case["domain"],
            "pattern_index": case["pattern_index"],
            "flags": case["flags"],
            "pickle_protocol": case["pickle_protocol"],
            "outcome": {
                "status": "return",
                "value": {
                    "kind": "tuple",
                    "items": [
                        {"kind": "str", "value": case["case"]},
                        {"kind": "int", "value": case["flags"]},
                        {"kind": "int", "value": case["pickle_protocol"]},
                    ],
                },
                "warnings": [],
            },
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
        "schema": ORACLE_SCHEMA + "-isolated-public-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "candidate_family": None,
        "pid": pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "records_sha256": digest(records),
        "records": records,
        "source_owners": synthetic_source_owners(source_pin),
        "reference_guard": make_reference_guard(2 * CASE_COUNT),
        "native_owners": None,
        "candidate_guard": None,
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
        "timed_out": False,
        "stdout": encode_stream(canonical(dict(worker))),
        "stderr": encode_stream(b""),
    }


def synthetic_family_manifest(family: str) -> dict[str, Any]:
    require(
        family in FAMILY_NAMES,
        "a genuine synthetic native family is mandatory",
    )
    spec = FAMILY_PATHS[family]

    def frozen(relative: str, kind: str) -> str:
        return hashlib.sha256(
            (
                ORACLE_SCHEMA + ":" + family + ":" + kind + ":" + relative
            ).encode("ascii")
        ).hexdigest()

    sources = {
        relative: frozen(relative, "source")
        for relative in spec["sources"]
    }
    natives = {
        relative: frozen(relative, "native")
        for relative in spec["binaries"]
    }
    return validate_family_manifest(
        family,
        sources[spec["adapter"]],
        natives[spec["engine"]],
        natives[spec["bridge"]],
        [
            relative + "=" + source_hash
            for relative, source_hash in sources.items()
        ],
        [
            relative + "=" + source_hash
            for relative, source_hash in natives.items()
        ],
    )


def synthetic_relative_owner(
    relative: str,
    source_hash: str,
    index: int,
) -> dict[str, Any]:
    return {
        "relative": relative,
        "sha256": source_hash,
        "bytes": 8_192 + index,
        "device": 11,
        "inode": 20_000 + index,
    }


def synthetic_native_evidence(
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    family = manifest["family"]
    spec = FAMILY_PATHS[family]
    audit_manifest = {
        **dict(manifest),
        "immutable_policy_sha256": dict(IMMUTABLE_OWNERSHIP_POLICY_SHA256),
    }
    source_owners = {
        relative: synthetic_relative_owner(relative, source_hash, index)
        for index, (relative, source_hash) in enumerate(
            manifest["source_sha256"].items(),
            start=100,
        )
    }
    native_owners = {
        relative: synthetic_relative_owner(relative, source_hash, index)
        for index, (relative, source_hash) in enumerate(
            manifest["native_sha256"].items(),
            start=200,
        )
    }
    policy_owners = {
        relative: synthetic_relative_owner(relative, source_hash, index)
        for index, (relative, source_hash) in enumerate(
            IMMUTABLE_OWNERSHIP_POLICY_SHA256.items(),
            start=300,
        )
    }
    owners = {
        "family": family,
        "manifest": audit_manifest,
        "source_owners": source_owners,
        "native_owners": native_owners,
        "policy_owners": policy_owners,
        "oracle_owner": synthetic_relative_owner(
            AUDIT_RELATIVE,
            AUDIT_SHA256,
            400,
        ),
        "python_owner": {
            "path": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
            "bytes": 16_384,
            "device": 11,
            "inode": 30_000,
        },
    }
    provenance = {
        "source": source_owners[spec["adapter"]],
        "native_engine": native_owners[spec["engine"]],
        "native_bridge": native_owners[spec["bridge"]],
    }
    evidence = {
        "manifest": audit_manifest,
        "audit_source_sha256": AUDIT_SHA256,
        "owners": owners,
        "v5_native_provenance": provenance,
    }
    return validate_native_evidence(evidence, manifest)


def synthetic_candidate_guard(family: str) -> dict[str, Any]:
    is_zig = family == "zig"
    guard: dict[str, Any] = {
        "original_matchers_blocked": True,
        "adapter_import_quarantined": True,
        "native_sre_blocked": True,
        "builtins_import_guarded": True,
        "importlib_import_guarded": True,
        "actual_object_identity_guarded": True,
        "warning_registry_introspection_safe": True,
        "warning_registry_exactly_absent": True,
        "cross_family_imports_blocked": True,
        "external_regex_imports_blocked": True,
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "owned_native_ffi_allowed": is_zig,
        "trusted_stdlib_ctypes_preloaded": is_zig,
        "trusted_stdlib_ctypes_builtin_verified": is_zig,
        "trusted_stdlib_ctypes_pythonapi_initialized": is_zig,
        "trusted_stdlib_ctypes_source_sha256": (
            TRUSTED_CTYPES_SHA256 if is_zig else None
        ),
        "owned_ctypes_load_count": 1 if is_zig else 0,
        "owned_ctypes_symbol_count": 9 if is_zig else 0,
        "cached_original_matcher_descendant_count": 5,
        "cached_original_holder_count": 7,
    }
    return snapshot_candidate_guard(guard, family)


def synthetic_candidate(
    family: str,
    pid: int,
    source_pin: str,
    records: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = synthetic_family_manifest(family)
    worker = {
        "schema": ORACLE_SCHEMA + "-isolated-public-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": "candidate-" + family,
        "candidate_family": family,
        "pid": pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "records_sha256": digest(records),
        "records": records,
        "source_owners": synthetic_source_owners(source_pin),
        "reference_guard": None,
        "native_owners": synthetic_native_evidence(manifest),
        "candidate_guard": synthetic_candidate_guard(family),
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
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    validate_candidate_worker(
        worker,
        manifest=manifest,
        source_pin=source_pin,
        matrix=build_frozen_matrix(),
        expected_pid=pid,
    )
    return worker, manifest




class SyntheticPublicOracle:
    """Strict frozen-shaped evidence validator without matcher operations."""

    validate_source_owners = staticmethod(validate_source_owners)
    validate_records = staticmethod(validate_records)
    validate_outcome = staticmethod(validate_outcome)
    validate_reference_worker = staticmethod(validate_reference_worker)
    validate_process_evidence = staticmethod(validate_process_evidence)
    validate_reference_pair = staticmethod(validate_reference_pair)
    validate_family_manifest = staticmethod(validate_family_manifest)
    validate_candidate_worker = staticmethod(validate_candidate_worker)


class SyntheticExternalOracleFailure(Exception):
    """Model the frozen public oracle's independent exception hierarchy."""


class SyntheticExternalAuditFailure(Exception):
    """Model the independently owned V3 audit's exception hierarchy."""


class HostileSyntheticPublicOracle(SyntheticPublicOracle):
    """Reject a real-shaped reference or candidate without external effects."""

    def __init__(
        self,
        *,
        reject_reference: bool = False,
        reject_candidate: bool = False,
        reject_manifest: bool = False,
    ) -> None:
        self.reject_reference = reject_reference
        self.reject_candidate = reject_candidate
        self.reject_manifest = reject_manifest

    def validate_reference_worker(self, value: Any, **kwargs: Any) -> Any:
        if self.reject_reference:
            raise SyntheticExternalOracleFailure(
                "synthetic genuine-public-oracle reference rejection"
            )
        return validate_reference_worker(value, **kwargs)

    def validate_candidate_worker(self, value: Any, **kwargs: Any) -> Any:
        if self.reject_candidate:
            raise SyntheticExternalOracleFailure(
                "synthetic genuine-public-oracle native rejection"
            )
        return validate_candidate_worker(value, **kwargs)

    def validate_family_manifest(self, *args: Any, **kwargs: Any) -> Any:
        if self.reject_manifest:
            raise SyntheticExternalOracleFailure(
                "synthetic genuine-public-oracle manifest rejection"
            )
        return validate_family_manifest(*args, **kwargs)


class HostileSyntheticPublicAudit:
    """Raise an actual-shaped independent V3 audit error without imports."""

    def validate_family_pins(self, *args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        raise SyntheticExternalAuditFailure(
            "synthetic genuine-V3 native-manifest rejection"
        )


class SourceOnlyBoundary:
    """Deny actual filesystem, matcher, clock, native, and worker effects."""

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
            "native_loads": 0,
            "directory_syncs": 0,
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
                if type(mode) is str and any(
                    letter in mode for letter in "wax+"
                ):
                    selected = "file_writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY
                    | os.O_RDWR
                    | os.O_CREAT
                    | os.O_TRUNC
                    | os.O_APPEND
                ):
                    selected = "file_writes"
            elif category == "dynamic_imports" and args:
                target = args[0]
                if type(target) is str and (
                    target == "candidates"
                    or target.startswith("candidates.")
                    or target.partition(".")[0] in FORBIDDEN_EXTERNAL_ROOTS
                ):
                    selected = "candidate_imports"
            self.blocked[selected] += 1
            raise SourceOnlyError(
                "synthetic public type controls cannot perform " + selected
            )

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        protections: tuple[tuple[Any, str, str], ...] = (
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
            (os, "link", "file_writes"),
            (os, "fsync", "directory_syncs"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (os, "system", "processes"),
            (os, "fork", "processes"),
            (os, "posix_spawn", "processes"),
            (
                importlib.machinery.ExtensionFileLoader,
                "exec_module",
                "native_loads",
            ),
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
        )
        for owner, name, category in protections:
            self.install(owner, name, category)
        ctypes_module = sys.modules.get("ctypes")
        if type(ctypes_module) is types.ModuleType:
            for name in ("CDLL", "PyDLL"):
                self.install(ctypes_module, name, "native_loads")
        native = sys.modules.get("_ctypes")
        if type(native) is types.ModuleType:
            self.install(native, "dlopen", "native_loads")
        return self

    def __exit__(
        self,
        error_type: Any,
        error: Any,
        traceback: Any,
    ) -> bool:
        del error_type, error, traceback
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False



def synthetic_owner(relative: str, source: str, number: int) -> dict[str, Any]:
    return {
        "relative": relative,
        "sha256": source,
        "bytes": 4_096 + number,
        "device": 7,
        "inode": 80_000 + number,
    }


def synthetic_frozen_source_owners(
    recorder_pin: str,
) -> dict[str, Any]:
    return validate_frozen_source_owners(
        {
            "recorder": synthetic_owner(SOURCE_RELATIVE, recorder_pin, 1),
            "parent_recorder": synthetic_owner(
                PARENT_RECORDER_RELATIVE, PARENT_RECORDER_SHA256, 2,
            ),
            "public_type_oracle": synthetic_owner(
                ORACLE_RELATIVE, ORACLE_SHA256, 3,
            ),
            "original_v5": synthetic_owner(V5_RELATIVE, V5_SHA256, 4),
            "from_scratch_audit_v3": synthetic_owner(
                AUDIT_RELATIVE, AUDIT_SHA256, 5,
            ),
            "previous_ownership_policy": synthetic_owner(
                PREVIOUS_POLICY_RELATIVE, PREVIOUS_POLICY_SHA256, 6,
            ),
        },
        recorder_pin,
    )


def synthetic_complete_baseline(
    matrix: list[dict[str, Any]],
    records: list[dict[str, Any]],
    recorder_pin: str,
    oracle: SyntheticPublicOracle,
) -> tuple[dict[str, Any], dict[str, Any]]:
    first = synthetic_reference(
        "reference_a", 82_001, ORACLE_SHA256, records,
    )
    second = synthetic_reference(
        "reference_b", 82_002, ORACLE_SHA256, records,
    )
    result = {
        "schema": ORACLE_SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "baseline_records_sha256": digest(records),
        "source_owners": first["source_owners"],
        "reference_processes": [
            synthetic_process(first),
            synthetic_process(second),
        ],
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
    process = {
        "started": True,
        "pid": 83_001,
        "returncode": 0,
        "signal": None,
        "timed_out": False,
        "spawn_error": None,
        "stdout": canonical(result),
        "stderr": b"",
    }
    owners = synthetic_frozen_source_owners(recorder_pin)
    report = build_baseline_report(
        recorder_pin,
        "shared-suite-v1",
        process,
        oracle,
        matrix,
        owners,
        owners,
    )
    require(
        report["status"] == "PASS"
        and report["actual_reference_workers"] == 2
        and report["validated_reference_a_case_count"] == CASE_COUNT
        and report["validated_reference_b_case_count"] == CASE_COUNT,
        "all genuinely shaped in-memory public reference cases are mandatory",
    )
    return report, owners


def synthetic_complete_receipt(
    pins: OwnerPins,
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    report_relative, receipt_relative = approved_paths(
        "baseline", pins.baseline.label,
    )
    publication = {
        "path": report_relative,
        "sha256": pins.baseline.archive,
        "bytes": 12_345,
        "uncompressed_sha256": digest(baseline),
        "uncompressed_bytes": len(canonical(baseline)),
        "compression": "gzip-mtime-zero-level-9",
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
        "atomic_no_overwrite_link": True,
        "complete_readback_verified": True,
    }
    preflight = {
        "receipt_relative": receipt_relative,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_observation": True,
    }
    return validate_baseline_receipt(
        make_baseline_receipt(
            pins.recorder,
            pins.baseline.label,
            baseline,
            publication,
            preflight,
        ),
        pins,
    )


def expect_rejection(
    name: str,
    operation: Callable[[], Any],
    rejected: list[str],
) -> None:
    require(
        type(name) is str and name not in rejected and callable(operation),
        "a distinct public poison control was repeated",
    )
    try:
        operation()
    except (
        RecorderError, OSError, TypeError, ValueError,
        KeyError, AttributeError, OverflowError,
        UnicodeError, EOFError, gzip.BadGzipFile,
    ):
        rejected.append(name)
        return
    raise RecorderError(
        "a forged public source-only control was accepted: " + name
    )


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, actual: Any) -> None:
        require(
            type(name) is str and name not in accepted and bool(actual),
            "a distinct synthetic public control failed: " + name,
        )
        accepted.append(name)

    def reject(name: str, operation: Callable[[], Any]) -> None:
        expect_rejection(name, operation, rejected)

    with SourceOnlyBoundary() as boundary:
        matrix = build_frozen_matrix()
        accept(
            "pin-complete-public-type-oracle-and-audited-parent-recorder",
            ORACLE_SHA256
            == "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20"
            and PARENT_RECORDER_SHA256
            == "a7cf45ce72a178fead7eb0d0789fd1f0f37ed63789fe086070eefa613e959a33"
            and V5_SHA256
            == "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
            and AUDIT_SHA256
            == "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee",
        )
        accept(
            "preserve-exact-64-bit-public-type-seed-without-json-rounding",
            PUBLISHED_SEED == 6_077_977_430_793_212_465
            and PUBLISHED_SEED > 2 ** 53
            and str(PUBLISHED_SEED) == "6077977430793212465",
        )
        accept(
            "reproduce-all-6912-frozen-public-type-and-serialization-cases",
            len(matrix) == 6_912
            and validate_matrix(matrix, MATRIX_SHA256) == MATRIX_SHA256
            and digest(matrix) == MATRIX_SHA256,
        )
        accept(
            "preserve-all-72-balanced-96-variant-public-cohorts",
            len(COHORTS) == 72 and VARIANTS_PER_COHORT == 96
            and all(
                sum(row["cohort"] == name for row in matrix) == 96
                for name in COHORTS
            ),
        )
        accept(
            "preserve-all-twelve-patterns-and-eight-flags-per-public-cohort",
            len(PATTERN_EXAMPLES) == 12
            and len(FLAG_VALUES) == 8
            and all(
                len({
                    (row["pattern_index"], row["flags_index"])
                    for row in matrix if row["cohort"] == name
                }) == 96
                for name in COHORTS
            ),
        )
        accept(
            "preserve-all-six-pickle-protocols-in-every-public-cohort",
            len(PICKLE_PROTOCOLS) == 6
            and all(
                {
                    row["pickle_protocol"] for row in matrix
                    if row["cohort"] == name
                } == set(PICKLE_PROTOCOLS)
                for name in COHORTS
            ),
        )
        accept(
            "preserve-both-text-and-bytes-public-domains",
            {row["domain"] for row in matrix} == {"str", "bytes"},
        )
        bounds = validate_compact_bounds()
        accept(
            "prove-96-mib-process-and-exact-128-mib-base64-ceilings",
            encoded_stream_byte_count(96 * 1024 * 1024, "synthetic ceiling")
            == 128 * 1024 * 1024
            and bounds["maximum_raw_process_stream_bytes"]
            == 96 * 1024 * 1024,
        )
        accept(
            "prove-two-lossless-streams-and-32-mib-fit-288-mib-report",
            bounds["maximum_process_stream_count"] == 2
            and 2 * bounds["maximum_encoded_process_stream_bytes"]
            + bounds["maximum_compact_report_metadata_bytes"]
            == bounds["maximum_compact_report_bytes"]
            == 288 * 1024 * 1024
            and bounds["maximum_compact_report_bytes"]
            < bounds["maximum_uncompressed_bytes"]
            < bounds["maximum_archive_bytes"],
        )
        records = synthetic_records(matrix)
        records_pin = digest(records)
        accept(
            "retain-all-6912-complete-public-values-errors-and-warnings",
            validate_records(matrix, records, records_pin) == records,
        )
        accept(
            "retain-every-source-ordered-domain-flags-and-pickle-protocol",
            all(
                all(
                    observed[name] == case[name]
                    for name in (
                        "case", "cohort", "domain",
                        "pattern_index", "flags", "pickle_protocol",
                    )
                )
                for case, observed in zip(matrix, records, strict=True)
            ),
        )
        fixture = canonical({
            "seed": PUBLISHED_SEED,
            "seed_decimal": str(PUBLISHED_SEED),
            "lone_surrogate": "\ud800",
            "combining": "e\u0301",
            "emoji": "\U0001f642",
            "nested": [None, True, {"number": 7}],
        })
        restored = decode_document(fixture, "synthetic canonical public JSON")
        accept(
            "retain-lone-surrogate-unicode-and-exact-full-width-public-seed",
            restored["seed"] == PUBLISHED_SEED
            and restored["seed_decimal"] == "6077977430793212465"
            and canonical(restored) == fixture,
        )
        accept(
            "stream-exact-public-canonical-evidence-without-files",
            b"".join(iter_canonical(restored)) == fixture,
        )
        archive = gzip.compress(fixture, compresslevel=9, mtime=0)
        accept(
            "preserve-deterministic-zero-mtime-lossless-public-gzip",
            archive == gzip.compress(fixture, compresslevel=9, mtime=0)
            and gzip.decompress(archive) == fixture,
        )
        stress = bytes(range(256)) * 4_096
        stress_stream = capture_stream(stress, "one-MiB synthetic public stream")
        accept(
            "reverse-a-complete-real-sized-one-mib-public-process-stream",
            len(stress) == 1_048_576
            and decode_stream(stress_stream, "synthetic public stress")
            == stress
            and len(stress_stream["base64"])
            == encoded_stream_byte_count(
                len(stress), "synthetic public stress",
            ),
        )
        compact_fixture = {
            "schema": SCHEMA + "-complete-baseline-report",
            "complete_baseline_process_stdout": stress_stream,
            "complete_baseline_process_stderr": capture_stream(
                b"", "synthetic empty public stderr",
            ),
            "synthetic_only": True,
        }
        budget = validate_compact_report_document(compact_fixture)
        accept(
            "prove-exact-canonical-single-stream-public-report-byte-count",
            budget["complete_report_bytes"] == len(canonical(compact_fixture))
            and budget["metadata_bytes"] <= MAX_COMPACT_REPORT_METADATA_BYTES
            and budget["encoded_process_stream_bytes"]
            == len(stress_stream["base64"]),
        )
        owner_pin = "de" * 32
        owners = synthetic_frozen_source_owners(owner_pin)
        accept(
            "authenticate-six-complete-public-oracle-and-v3-v5-source-owners",
            len(owners) == 6
            and validate_frozen_source_owners(owners, owner_pin) == owners,
        )
        synthetic_oracle = SyntheticPublicOracle()
        baseline, frozen_owners = synthetic_complete_baseline(
            matrix, records, owner_pin, synthetic_oracle,
        )
        accept(
            "retain-two-complete-6912-case-standard-public-reference-streams",
            baseline["status"] == "PASS"
            and baseline["baseline_reference_pids"] == [82_001, 82_002]
            and baseline["validated_reference_a_case_count"] == 6_912
            and baseline["validated_reference_b_case_count"] == 6_912
            and frozen_owners == owners
            and "complete_baseline_result" not in baseline
            and "reference_a_records" not in baseline
            and "reference_b_records" not in baseline
            and validate_compact_report_document(
                baseline
            )["complete_report_bytes"] == len(canonical(baseline)),
        )
        complete_reference_process = {
            "started": True,
            "pid": 83_001,
            "returncode": 0,
            "signal": None,
            "timed_out": False,
            "spawn_error": None,
            "stdout": decode_stream(
                baseline["complete_baseline_process_stdout"],
                "synthetic full public controller",
            ),
            "stderr": b"",
        }
        hostile_reference_oracle = HostileSyntheticPublicOracle(
            reject_reference=True,
        )
        reject(
            "normalize-independent-frozen-public-reference-exception",
            lambda: validate_public_baseline_result(
                decode_document(
                    complete_reference_process["stdout"],
                    "complete source-only hostile public controller",
                ),
                hostile_reference_oracle,
                matrix,
            ),
        )
        hostile_reference_report = build_baseline_report(
            owner_pin,
            "shared-suite-v1",
            complete_reference_process,
            hostile_reference_oracle,
            matrix,
            owners,
            owners,
        )
        accept(
            "retain-real-shaped-frozen-oracle-reference-error-as-unknown",
            hostile_reference_report["status"] == "FAIL"
            and hostile_reference_report["actual_reference_workers"]
            == "UNKNOWN"
            and hostile_reference_report[
                "actual_baseline_controller_invocations"
            ] == 1
            and hostile_reference_report[
                "validated_reference_a_case_count"
            ] is None
            and hostile_reference_report[
                "validated_reference_b_case_count"
            ] is None
            and decode_stream(
                hostile_reference_report[
                    "complete_baseline_process_stdout"
                ],
                "synthetic unknown public reference",
            ) == complete_reference_process["stdout"],
        )
        hostile_reference_failure = observation_failure_document(
            ObservationFailure(
                "synthetic frozen public oracle reference exception",
                mode="baseline",
                process=complete_reference_process,
                report=hostile_reference_report,
            )
        )
        accept(
            "retain-independent-public-reference-exception-pid-and-stream",
            hostile_reference_failure["actual_process_pid"] == 83_001
            and hostile_reference_failure["actual_reference_workers"]
            == "UNKNOWN"
            and hostile_reference_failure["reference_outcomes_known"]
            is False
            and decode_stream(
                hostile_reference_failure["complete_actual_process_stdout"],
                "synthetic frozen-oracle failed controller",
            ) == complete_reference_process["stdout"],
        )
        changed = list(records)
        for index in (0, 1):
            changed[index] = {
                **records[index],
                "outcome": {
                    "status": "return",
                    "value": {
                        "kind": "str",
                        "value": "synthetic-public-mismatch-" + str(index),
                    },
                    "warnings": [],
                },
            }
        mismatch, mismatch_cohorts, mismatch_domains = (
            reconstruct_mismatch_evidence(matrix, records, changed)
        )
        mismatch_pin = digest(mismatch)
        accept(
            "preserve-all-public-mismatch-outcomes-with-exact-source-order",
            len(mismatch) == 2
            and [item["index"] for item in mismatch] == [0, 1]
            and sum(mismatch_cohorts.values()) == 2
            and sum(mismatch_domains.values()) == 2
            and validate_mismatch_evidence(
                mismatch, matrix, records, changed, mismatch_pin,
            )[0] == mismatch,
        )
        for family in FAMILIES:
            worker, manifest = synthetic_candidate(
                family,
                84_001 + tuple(FAMILIES).index(family),
                ORACLE_SHA256,
                records,
            )
            spec = family_spec(family)
            pins = make_owner_pins(
                family,
                owner_pin,
                manifest["candidate_source_sha256"],
                manifest["native_engine_sha256"],
                manifest["native_bridge_sha256"],
                [
                    path + "=" + source
                    for path, source in manifest["source_sha256"].items()
                ],
                make_baseline_pins(
                    "shared-suite-v1",
                    "12" * 32,
                    "34" * 32,
                    records_pin,
                ),
            )
            receipt = synthetic_complete_receipt(pins, baseline)
            derived = validate_archived_baseline(
                baseline, pins, synthetic_oracle, matrix, receipt,
            )
            accept(
                "rederive-" + family
                + "-complete-signed-public-baseline-without-duplication",
                revalidate_derived_baseline(
                    derived, pins, synthetic_oracle, matrix, receipt,
                ) == derived
                and derived["reference_a_records"] == records
                and derived["reference_b_records"] == records,
            )
            closure = worker["native_owners"]["owners"]
            process = {
                "started": True,
                "pid": worker["pid"],
                "returncode": 0,
                "signal": None,
                "timed_out": False,
                "spawn_error": None,
                "stdout": canonical(worker),
                "stderr": b"",
            }
            report = build_candidate_report(
                pins, "trial-v1", process, matrix,
                receipt, derived, closure, closure,
                manifest, synthetic_oracle,
            )
            accept(
                "pass-complete-" + family
                + "-6912-case-signed-public-native-report",
                report["status"] == "PASS"
                and report["validated_baseline_record_count"] == CASE_COUNT
                and report["validated_candidate_record_count"] == CASE_COUNT
                and report["mismatch_count"] == 0
                and report["matched_case_count"] == CASE_COUNT
                and report["actual_method_guard_checks"] == 2 * CASE_COUNT
                and report["actual_warning_registry_guard_checks"]
                == 2 * CASE_COUNT
                and validate_compact_report_document(
                    report
                )["complete_report_bytes"] == len(canonical(report))
                and "candidate_records" not in report
                and "reference_a_records" not in report,
            )
            hostile_candidate_oracle = HostileSyntheticPublicOracle(
                reject_candidate=True,
            )
            hostile_candidate_report = build_candidate_report(
                pins,
                "trial-v1",
                process,
                matrix,
                receipt,
                derived,
                closure,
                closure,
                manifest,
                hostile_candidate_oracle,
            )
            hostile_candidate_failure = observation_failure_document(
                ObservationFailure(
                    "synthetic independently owned public candidate error",
                    mode="candidate",
                    process=process,
                    report=hostile_candidate_report,
                )
            )
            accept(
                "retain-" + family
                + "-frozen-oracle-exception-with-full-unknown-worker",
                hostile_candidate_report["status"] == "FAIL"
                and hostile_candidate_report["actual_candidate_workers"]
                == "UNKNOWN"
                and hostile_candidate_report[
                    "validated_candidate_record_count"
                ] is None
                and hostile_candidate_failure["actual_process_pid"]
                == process["pid"]
                and hostile_candidate_failure["actual_candidate_workers"]
                == "UNKNOWN"
                and hostile_candidate_failure["candidate_outcomes_known"]
                is False
                and decode_stream(
                    hostile_candidate_failure[
                        "complete_actual_process_stdout"
                    ],
                    "synthetic frozen-oracle failed native worker",
                ) == process["stdout"],
            )
            reject(
                "normalize-" + family
                + "-independent-v3-audit-custom-exception",
                lambda pins=pins: make_audit_manifest(
                    pins,
                    synthetic_oracle,
                    HostileSyntheticPublicAudit(),
                ),
            )
            reject(
                "normalize-" + family
                + "-frozen-public-oracle-manifest-custom-exception",
                lambda pins=pins: make_audit_manifest(
                    pins,
                    HostileSyntheticPublicOracle(reject_manifest=True),
                    HostileSyntheticPublicAudit(),
                ),
            )
            bad_worker, bad_manifest = synthetic_candidate(
                family,
                85_001 + tuple(FAMILIES).index(family),
                ORACLE_SHA256,
                changed,
            )
            require(bad_manifest == manifest, "a synthetic family escaped")
            bad_report = build_candidate_report(
                pins,
                "trial-v1",
                {
                    **process,
                    "pid": bad_worker["pid"],
                    "stdout": canonical(bad_worker),
                },
                matrix,
                receipt,
                derived,
                closure,
                closure,
                manifest,
                synthetic_oracle,
            )
            accept(
                "preserve-every-" + family
                + "-real-shaped-public-type-mismatch",
                bad_report["status"] == "FAIL"
                and bad_report["mismatch_count"] == 2
                and bad_report["all_mismatches"] == mismatch
                and bad_report["mismatch_evidence_sha256"] == mismatch_pin
                and bad_report["all_mismatches_preserved"] is True
                and bad_report["validated_candidate_record_count"]
                == CASE_COUNT,
            )
            accept(
                "enforce-" + family + "-independent-v3-v5-native-owners",
                validate_native_evidence(
                    worker["native_owners"], manifest,
                ) == worker["native_owners"]
                and snapshot_candidate_guard(
                    worker["candidate_guard"], family,
                ) == worker["candidate_guard"]
                and spec.owned_ctypes is (family == "zig")
                and (pins.engine == pins.bridge) is (family == "c"),
            )
            accept(
                "isolate-" + family + "-exact-public-report-and-receipt-paths",
                approved_paths("candidate", "trial-v1", family)[0].endswith(
                    ".json.gz"
                )
                and approved_paths(
                    "candidate", "trial-v1", family,
                )[1].endswith("-publication-receipt.json")
                and ("/" + family + "-public-type-identity-serialization-v1-")
                in approved_paths("candidate", "trial-v1", family)[0],
            )
            for field, poisoned in (
                ("status", "FAIL"),
                ("baseline_result_status", "FAIL"),
                ("parent_recorder_sha256", "ef" * 32),
                ("oracle_source_sha256", "ef" * 32),
                ("original_v5_sha256", "ef" * 32),
                ("ownership_audit_sha256", "ef" * 32),
                ("previous_ownership_policy_sha256", "ef" * 32),
                ("matrix_sha256", "ef" * 32),
                ("published_seed", PUBLISHED_SEED - 1),
                ("published_seed_decimal", str(PUBLISHED_SEED - 1)),
                ("case_count", CASE_COUNT - 1),
                ("cohort_count", len(COHORTS) - 1),
                ("variants_per_cohort", VARIANTS_PER_COHORT - 1),
                ("cohorts", list(COHORTS[:-1])),
                ("pickle_protocols", list(PICKLE_PROTOCOLS[:-1])),
                ("flag_values", list(FLAG_VALUES[:-1])),
                ("distinct_patterns_per_cohort", 11),
                ("maximum_raw_process_stream_bytes", MAX_PROCESS_BYTES + 1),
                (
                    "maximum_encoded_process_stream_bytes",
                    MAX_ENCODED_PROCESS_STREAM_BYTES + 1,
                ),
                (
                    "maximum_compact_report_metadata_bytes",
                    MAX_COMPACT_REPORT_METADATA_BYTES + 1,
                ),
                ("maximum_compact_report_bytes", MAX_COMPACT_REPORT_BYTES + 1),
                ("baseline_records_sha256", "ef" * 32),
                ("report_sha256", "ef" * 32),
                ("report_relative", "experiments/forged-public.json.gz"),
                ("baseline_reference_pids", [82_001, 82_001]),
                ("actual_reference_workers", 1),
                ("actual_candidate_workers", 1),
                ("actual_candidate_imports", 1),
                ("actual_baseline_controller_invocations", 2),
                ("source_closure_unchanged", False),
                ("report_compression", "none"),
                ("report_file_fsync_completed", False),
                ("report_directory_fsync_completed", False),
                ("report_atomic_no_overwrite_link", False),
                ("report_complete_readback_verified", False),
                ("approved_fresh_path_count", 1),
                ("fresh_paths_checked_before_baseline", False),
                ("clock_samples", 1),
                ("timing_trials_run", 1),
                ("benchmark_files_read", 1),
                ("hidden_cases_read", 1),
                ("performance", "MEASURED"),
                ("candidate_qualified_for_hidden_benchmark", True),
                ("final_winner_selected", True),
            ):
                reject(
                    "reject-" + family + "-forged-public-baseline-" + field,
                    lambda field=field, poisoned=poisoned,
                    receipt=receipt, pins=pins: validate_baseline_receipt(
                        {**receipt, field: poisoned}, pins,
                    ),
                )
            guard = worker["candidate_guard"]
            for field in (
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
            ):
                reject(
                    "reject-" + family + "-lost-public-guard-" + field,
                    lambda guard=guard, field=field, family=family:
                    snapshot_candidate_guard(
                        {**guard, field: False}, family,
                    ),
                )
            for field in (
                "actual_method_guard_checks",
                "actual_warning_registry_guard_checks",
            ):
                reject(
                    "reject-" + family + "-short-public-guard-" + field,
                    lambda guard=guard, field=field, family=family:
                    snapshot_candidate_guard(
                        {**guard, field: 2 * CASE_COUNT - 1}, family,
                    ),
                )
            if family == "rust":
                for field in (
                    "complete_baseline_result",
                    "reference_a_records",
                    "reference_b_records",
                    "reference_a_process",
                    "reference_b_process",
                ):
                    reject(
                        "reject-omitted-signed-public-derived-" + field,
                        lambda field=field: revalidate_derived_baseline(
                            {
                                key: value
                                for key, value in derived.items()
                                if key != field
                            },
                            pins, synthetic_oracle, matrix, receipt,
                        ),
                    )
                    original = derived[field]
                    forgery = (
                        {**original, "synthetic_forgery": True}
                        if type(original) is dict
                        else list(reversed(original))
                    )
                    reject(
                        "reject-forged-signed-public-derived-" + field,
                        lambda field=field, forgery=forgery:
                        revalidate_derived_baseline(
                            {**derived, field: forgery},
                            pins, synthetic_oracle, matrix, receipt,
                        ),
                    )
                reject(
                    "reject-signed-public-archive-enriched-with-live-vectors",
                    lambda: validate_archived_baseline(
                        derived, pins, synthetic_oracle, matrix, receipt,
                    ),
                )
                reject(
                    "reject-extra-unsigned-public-compact-archive-field",
                    lambda: validate_archived_baseline(
                        {**baseline, "unsigned_public_forgery": True},
                        pins, synthetic_oracle, matrix, receipt,
                    ),
                )

        for name, operation in (
            ("omitted", lambda: mismatch[1:]),
            ("reordered", lambda: list(reversed(mismatch))),
            ("duplicated", lambda: [mismatch[0], mismatch[0]]),
            (
                "baseline-digest",
                lambda: [
                    {**mismatch[0], "baseline_outcome_sha256": "ef" * 32},
                    mismatch[1],
                ],
            ),
            (
                "candidate-digest",
                lambda: [
                    {**mismatch[0], "candidate_outcome_sha256": "ef" * 32},
                    mismatch[1],
                ],
            ),
        ):
            reject(
                "reject-" + name + "-lossless-public-mismatch",
                lambda operation=operation: validate_mismatch_evidence(
                    operation(), matrix, records, changed, mismatch_pin,
                ),
            )
        for field in (
            "recorder",
            "parent_recorder",
            "public_type_oracle",
            "original_v5",
            "from_scratch_audit_v3",
            "previous_ownership_policy",
        ):
            reject(
                "reject-omitted-frozen-public-owner-" + field,
                lambda field=field: validate_frozen_source_owners(
                    {
                        name: value for name, value in owners.items()
                        if name != field
                    },
                    owner_pin,
                ),
            )
            reject(
                "reject-forged-frozen-public-owner-" + field,
                lambda field=field: validate_frozen_source_owners(
                    {
                        **owners,
                        field: {**owners[field], "sha256": "ef" * 32},
                    },
                    owner_pin,
                ),
            )
        for field in (
            "complete_decoded_baseline_process",
            "complete_baseline_result",
            "reference_a_records",
            "reference_b_records",
            "reference_a_process",
            "reference_b_process",
            "complete_decoded_candidate_process",
            "complete_candidate_result",
            "baseline_records",
            "candidate_records",
        ):
            reject(
                "reject-duplicated-compact-public-payload-" + field,
                lambda field=field: validate_compact_report_document(
                    {**compact_fixture, field: []}
                ),
            )
        for name, number in (
            ("negative", -1),
            ("bool", True),
            ("one-byte-over", MAX_PROCESS_BYTES + 1),
        ):
            reject(
                "reject-" + name + "-public-process-stream-size",
                lambda number=number: validate_stream_byte_count(
                    number, "synthetic public poison",
                ),
            )
        reject(
            "reject-one-byte-over-public-metadata-budget",
            lambda: validate_compact_metadata_byte_count(
                MAX_COMPACT_REPORT_METADATA_BYTES + 1,
            ),
        )
        for name, mutation in (
            ("first", lambda rows: rows[1:]),
            ("last", lambda rows: rows[:-1]),
            ("reverse", lambda rows: list(reversed(rows))),
            ("duplicate", lambda rows: [rows[0], *rows[1:-1], rows[0]]),
        ):
            reject(
                "reject-" + name + "-frozen-public-matrix",
                lambda mutation=mutation: validate_matrix(mutation(matrix)),
            )
        for field, poisoned in (
            ("case", "forged-public-case"),
            ("cohort", "forged-cohort"),
            ("cohort_index", -1),
            ("variant", -1),
            ("domain", "external"),
            ("pattern_index", 12),
            ("flags_index", 8),
            ("flags", 512),
            ("pickle_protocol", 6),
            ("published_seed", PUBLISHED_SEED - 1),
        ):
            def poison_matrix(
                field: str = field,
                poisoned: Any = poisoned,
            ) -> str:
                forged = list(matrix)
                forged[0] = {**matrix[0], field: poisoned}
                return validate_matrix(forged)

            reject("reject-forged-public-matrix-" + field, poison_matrix)
        reject(
            "reject-rounded-53-bit-public-seed",
            lambda: validate_matrix(
                build_frozen_matrix(int(float(PUBLISHED_SEED)))
            ),
        )
        reject(
            "reject-floating-public-seed",
            lambda: build_frozen_matrix(float(PUBLISHED_SEED)),
        )
        for name, mutation in (
            ("first", lambda rows: rows[1:]),
            ("last", lambda rows: rows[:-1]),
            ("reverse", lambda rows: list(reversed(rows))),
            ("duplicate", lambda rows: [rows[0], *rows[1:-1], rows[0]]),
        ):
            reject(
                "reject-" + name + "-complete-public-record-vector",
                lambda mutation=mutation: validate_records(
                    matrix, mutation(records), records_pin,
                ),
            )
        for field, poisoned in (
            ("case", "forged-case"),
            ("cohort", "forged"),
            ("domain", "bytes" if records[0]["domain"] == "str" else "str"),
            ("pattern_index", 99),
            ("flags", 512),
            ("pickle_protocol", 99),
        ):
            def poison_records(
                field: str = field,
                poisoned: Any = poisoned,
            ) -> list[dict[str, Any]]:
                forged = list(records)
                forged[0] = {**records[0], field: poisoned}
                return validate_records(matrix, forged, records_pin)

            reject("reject-forged-public-record-" + field, poison_records)
        for field in ("status", "value", "warnings"):
            reject(
                "reject-omitted-complete-public-outcome-" + field,
                lambda field=field: validate_outcome({
                    key: value
                    for key, value in records[0]["outcome"].items()
                    if key != field
                }),
            )
        for kind in (
            "bool", "int", "str", "bytes", "bytearray",
            "type", "int-subclass", "tuple", "list", "set",
            "frozenset", "mapping", "generic-alias", "callable",
        ):
            reject(
                "reject-incomplete-normalized-public-" + kind,
                lambda kind=kind: validate_normalized_value({"kind": kind}),
            )
        for name, poisoned in (
            ("negative", -1),
            ("oversized", MAX_NORMALIZATION_DEPTH + 1),
            ("boolean", True),
        ):
            reject(
                "reject-" + name + "-public-normalization-depth",
                lambda poisoned=poisoned: validate_normalized_value(
                    {"kind": "none"}, poisoned,
                ),
            )
        for name, raw in (
            ("duplicate-key", b'{"a":1,"a":2}\n'),
            ("nan", b'{"a":NaN}\n'),
            ("positive-infinity", b'{"a":Infinity}\n'),
            ("negative-infinity", b'{"a":-Infinity}\n'),
            ("noncanonical-spacing", b'{"a": 1}\n'),
            ("missing-newline", b'{"a":1}'),
            ("trailing-document", b'{"a":1}\n{}\n'),
        ):
            reject(
                "reject-" + name + "-canonical-public-document",
                lambda raw=raw: decode_document(raw, "synthetic poison"),
            )
        for field, poisoned in (
            ("base64", "!!!"),
            ("bytes", len(stress) + 1),
            ("sha256", "ef" * 32),
            ("complete", False),
        ):
            reject(
                "reject-forged-public-process-stream-" + field,
                lambda field=field, poisoned=poisoned: decode_stream(
                    {**stress_stream, field: poisoned},
                    "synthetic public stream",
                ),
            )
        for name, value in (
            ("empty", ""),
            ("uppercase", "ABC"),
            ("escape", "../x"),
            ("slash", "a/b"),
            ("backslash", "a\\b"),
            ("double-dash", "a--b"),
            ("leading-dash", "-a"),
            ("trailing-dash", "a-"),
            ("dot", "a.b"),
            ("nul", "a\x00b"),
            ("bool", True),
            ("oversized", "a" * 65),
        ):
            reject(
                "reject-" + name + "-public-publication-label",
                lambda value=value: validate_label(value),
            )
        for name, value in (
            ("empty", ""),
            ("dot", "."),
            ("parent", "../x"),
            ("absolute", "/tmp/x"),
            ("double-slash", "a//b"),
            ("backslash", "a\\b"),
            ("nul", "a\x00b"),
        ):
            reject(
                "reject-" + name + "-public-no-follow-owner-path",
                lambda value=value: safe_parts(value),
            )
        for name, value in (
            ("short", "ab"),
            ("uppercase", "AB" * 32),
            ("constant", "0" * 64),
            ("nonhex", "g1" * 32),
            ("boolean", True),
            ("none", None),
        ):
            reject(
                "reject-" + name + "-public-owner-digest",
                lambda value=value: validate_digest(value, "synthetic"),
            )
        for family in ("re", "regex", "pcre2", "python", "other", None):
            reject(
                "reject-external-public-candidate-family-" + str(family),
                lambda family=family: family_spec(family),
            )
        reject(
            "reject-public-no-follow-directory-inode-replacement",
            lambda: require_directory_identity((7, 1), (7, 1), (7, 2)),
        )
        reject(
            "reject-cross-family-public-baseline-path",
            lambda: approved_paths("baseline", "shared-suite-v1", "rust"),
        )
        fail_process = {
            "started": True,
            "pid": 86_001,
            "returncode": 1,
            "signal": None,
            "timed_out": False,
            "spawn_error": None,
            "stdout": b"synthetic complete public failure stdout\n",
            "stderr": b"synthetic complete public failure stderr\n",
        }
        failed_reference = observation_failure_document(
            ObservationFailure(
                "synthetic post-invocation public baseline failure",
                mode="baseline",
                process=fail_process,
                report=None,
            )
        )
        accept(
            "retain-started-public-reference-pid-and-truthful-unknown-outcomes",
            failed_reference["actual_process_pid"] == 86_001
            and failed_reference["actual_reference_workers"] == "UNKNOWN"
            and failed_reference["reference_outcomes_known"] is False
            and decode_stream(
                failed_reference["complete_actual_process_stdout"],
                "synthetic failed public stdout",
            ) == fail_process["stdout"]
            and decode_stream(
                failed_reference["complete_actual_process_stderr"],
                "synthetic failed public stderr",
            ) == fail_process["stderr"],
        )
        failed_candidate = observation_failure_document(
            ObservationFailure(
                "synthetic post-invocation public native failure",
                mode="candidate",
                process={**fail_process, "pid": 86_002},
                report=None,
            )
        )
        accept(
            "retain-started-public-native-pid-and-truthful-unknown-outcomes",
            failed_candidate["actual_process_pid"] == 86_002
            and failed_candidate["actual_candidate_workers"] == "UNKNOWN"
            and failed_candidate["candidate_outcomes_known"] is False,
        )
        unobserved_native = observation_failure_document(
            ObservationFailure(
                "synthetic started public-worker communication failure",
                mode="candidate",
                process={
                    **fail_process,
                    "pid": 86_003,
                    "returncode": None,
                    "stdout": None,
                    "stderr": None,
                },
                report=None,
            )
        )
        accept(
            "preserve-started-process-unknown-communication-without-false-bytes",
            unobserved_native["actual_process_pid"] == 86_003
            and unobserved_native["actual_candidate_workers"] == "UNKNOWN"
            and unobserved_native["actual_process_returncode"] is None
            and unobserved_native["complete_actual_process_stdout"]
            == {
                "base64": None,
                "bytes": "UNKNOWN",
                "sha256": None,
                "complete": False,
                "capture_failure": True,
            }
            and unobserved_native["complete_actual_process_stderr"]
            == unobserved_native["complete_actual_process_stdout"]
            and unobserved_native["candidate_outcomes_known"] is False,
        )
        for name, value in (
            (
                "false-zero-reference",
                {**failed_reference, "actual_reference_workers": 0},
            ),
            (
                "false-zero-candidate",
                {**failed_candidate, "actual_candidate_workers": 0},
            ),
            (
                "false-known-reference",
                {**failed_reference, "reference_outcomes_known": True},
            ),
            (
                "false-known-candidate",
                {**failed_candidate, "candidate_outcomes_known": True},
            ),
            (
                "omitted-partial-publication",
                {**failed_reference, "published_evidence_file_count": 1},
            ),
            (
                "substituted-oracle-owner",
                {**failed_reference, "oracle_source_sha256": "ef" * 32},
            ),
            (
                "substituted-matrix",
                {**failed_candidate, "matrix_sha256": "ef" * 32},
            ),
            (
                "rounded-published-seed",
                {
                    **failed_reference,
                    "published_seed_decimal": str(int(float(PUBLISHED_SEED))),
                },
            ),
            (
                "falsely-empty-unobserved-process-stdout",
                {
                    **unobserved_native,
                    "complete_actual_process_stdout": {
                        "base64": None,
                        "bytes": 0,
                        "sha256": None,
                        "complete": False,
                        "capture_failure": True,
                    },
                },
            ),
            (
                "falsely-hashed-unobserved-process-stderr",
                {
                    **unobserved_native,
                    "complete_actual_process_stderr": {
                        **unobserved_native[
                            "complete_actual_process_stderr"
                        ],
                        "sha256": "ef" * 32,
                    },
                },
            ),
        ):
            reject(
                "reject-" + name + "-post-invocation-public-failure",
                lambda value=value: validate_observation_failure_document(
                    value
                ),
            )

        def poisoned_archive() -> bytes:
            poisoned = archive[:-8] + bytes(
                (archive[-8] ^ 1,)
            ) + archive[-7:]
            return gzip.decompress(poisoned)

        reject("reject-corrupt-public-gzip-crc", poisoned_archive)
        reject(
            "block-real-public-source-file-read",
            lambda: builtins.open(SOURCE_ABSOLUTE, "rb"),
        )
        reject(
            "block-real-public-source-file-write",
            lambda: builtins.open(SOURCE_ABSOLUTE, "wb"),
        )
        reject(
            "block-real-public-filesystem-metadata",
            lambda: os.stat(SOURCE_ABSOLUTE),
        )
        reject(
            "block-real-public-candidate-import",
            lambda: importlib.import_module("candidates.rust_candidate"),
        )
        reject(
            "block-real-public-external-regex-package",
            lambda: importlib.import_module("regex"),
        )
        reject(
            "block-real-public-standard-matcher-import",
            lambda: importlib.import_module("re"),
        )
        reject(
            "block-real-public-isolated-worker",
            lambda: subprocess.Popen([PINNED_PYTHON, "-I", "-B"]),
        )
        reject(
            "block-real-public-native-extension",
            lambda: importlib.machinery.ExtensionFileLoader(
                "synthetic_forbidden_public_native",
                ROOT + "/candidates/synthetic_forbidden_public_native.so",
            ).exec_module(types.ModuleType("synthetic_forbidden_public_native")),
        )
        reject(
            "block-real-public-background-thread",
            lambda: threading.Thread(target=lambda: None).start(),
        )
        reject("block-real-public-wall-clock", lambda: time.time())
        reject("block-real-public-monotonic-clock", lambda: time.monotonic())
        reject(
            "block-real-public-performance-clock",
            lambda: time.perf_counter(),
        )
        reject("block-real-public-operating-system-randomness", lambda: os.urandom(1))
        reject("block-real-public-garbage-collection", lambda: gc.collect())
        reject("block-real-public-directory-fsync", lambda: os.fsync(1))

        def actual_preflight() -> None:
            with preflight_fresh_outputs("baseline", "shared-suite-v1"):
                raise RecorderError("no-clobber source controls escaped")

        reject(
            "block-real-public-no-clobber-publication-preflight",
            actual_preflight,
        )
        blocked = dict(boundary.blocked)
        accept(
            "exercise-all-eleven-public-source-only-effect-protections",
            all(
                blocked[name] > 0
                for name in (
                    "file_reads",
                    "file_writes",
                    "processes",
                    "candidate_imports",
                    "dynamic_imports",
                    "native_loads",
                    "threads",
                    "clock_samples",
                    "garbage_collections",
                    "randomness",
                    "directory_syncs",
                )
            ),
        )
        accept(
            "load-no-native-candidate-or-external-public-regex-package",
            not any(
                name == "candidates"
                or name.startswith("candidates.")
                or name.partition(".")[0] in FORBIDDEN_EXTERNAL_ROOTS
                for name in sys.modules
            ),
        )

    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "parent_recorder_relative": PARENT_RECORDER_RELATIVE,
        "parent_recorder_sha256": PARENT_RECORDER_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "ownership_audit_relative": AUDIT_RELATIVE,
        "ownership_audit_sha256": AUDIT_SHA256,
        "previous_ownership_policy_relative": PREVIOUS_POLICY_RELATIVE,
        "previous_ownership_policy_sha256": PREVIOUS_POLICY_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "pickle_protocols": list(PICKLE_PROTOCOLS),
        "flag_values": list(FLAG_VALUES),
        **validate_compact_bounds(),
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_poison_count": len(rejected),
        "rejected_poisons": rejected,
        "source_only_blocked_operations": blocked,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_original_matcher_operations": 0,
        "actual_support_preload_calls": 0,
        "actual_oracle_execute_case_calls": 0,
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


def parse_arguments(
    arguments: list[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Durably record frozen CPython public regular-expression types, "
            "identity, serialization, flags, warnings, errors and cache"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--record-baseline", action="store_true")
    modes.add_argument("--record-candidate", action="store_true")
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
    parser.add_argument(
        "--native-artifact-sha256", action="append", default=[],
    )
    return parser.parse_args(arguments)


def make_cli_pins(options: argparse.Namespace) -> OwnerPins:
    require(
        validate_digest(
            options.oracle_source_sha256, "frozen public type oracle",
        ) == ORACLE_SHA256
        and validate_digest(
            options.matrix_sha256, "frozen public type matrix",
        ) == MATRIX_SHA256
        and validate_digest(
            options.ownership_audit_source_sha256,
            "frozen V3 public ownership audit",
        ) == AUDIT_SHA256,
        "pin the unchanged genuine public oracle, matrix and V3 audit",
    )
    baseline = make_baseline_pins(
        options.baseline_label,
        options.baseline_receipt_sha256,
        options.baseline_archive_sha256,
        options.baseline_records_sha256,
    )
    pins = make_owner_pins(
        options.candidate,
        options.recorder_source_sha256,
        options.candidate_source_sha256,
        options.native_engine_sha256,
        options.native_bridge_sha256,
        options.owned_source_sha256,
        baseline,
    )
    spec = family_spec(pins.family)
    expected_native = {spec.engine_relative: pins.engine}
    if spec.engine_relative != spec.bridge_relative:
        expected_native[spec.bridge_relative] = pins.bridge
    provided_native = dict(
        parse_owned_source(value)
        for value in options.native_artifact_sha256
    )
    require(
        len(provided_native) == len(options.native_artifact_sha256)
        and provided_native == expected_native,
        "explicitly pin every distinct owned public native artifact",
    )
    return pins


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
                and not options.owned_source_sha256
                and not options.native_artifact_sha256,
                "source-only public controls cannot select any real owner",
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
                and not options.owned_source_sha256
                and not options.native_artifact_sha256,
                "a genuine public baseline cannot select a native candidate",
            )
            result = record_baseline(
                options.recorder_source_sha256,
                options.oracle_source_sha256,
                options.matrix_sha256,
                options.label,
            )
        else:
            require(
                options.record_candidate,
                "select only a frozen public baseline or native candidate",
            )
            result = record_candidate(make_cli_pins(options), options.label)
        sys.stdout.buffer.write(canonical(result))
        return 0 if result.get("status") == "PASS" else 1
    except ObservationFailure as error:
        sys.stdout.buffer.write(canonical(observation_failure_document(error)))
        return 1
    except Exception as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "actual_reference_workers": 0,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "actual_original_matcher_operations": 0,
            "actual_support_preload_calls": 0,
            "actual_oracle_execute_case_calls": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
