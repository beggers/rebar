#!/usr/bin/env python3
"""Freeze additional, untimed CPython 3.14.6 public re compatibility.

The 6,912 cases are a separate denominator: 72 meaningful public-behavior
cohorts, each crossed with all 12 distinct patterns and all eight
applicable flag combinations. They include public exports and flag aliases,
typed Pattern and Match aliases, object and copying identity, weak
references, all six pickle protocols for text and bytes, observable cache
and purge behavior, warnings, and complete public error attributes.

Only two independently isolated and source-authenticated standard CPython
workers may establish the baseline. A candidate runs only within the frozen
V5 original matcher quarantine, with the full V3 from-scratch source and
native ownership closure explicitly pinned by the caller. Raw pickle
bytes, native hash values, object addresses, and private DEBUG
disassembly are not mistaken for public behavior.

The --self-test is synthetic. It cannot read or write a file, import a
matcher, start a worker or thread, collect garbage, sample a clock, open
hidden data, or run either a baseline or a candidate.
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
SOURCE_RELATIVE = (
    "tools/independent_public_type_identity_serialization_v1.py"
)
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-public-type-identity-serialization-v1"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
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
V5_GUARD_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_GUARD_MODULE = "tools.independent_original_cpython_suite_v5"
V5_GUARD_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
OWNERSHIP_AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
OWNERSHIP_AUDIT_MODULE = "tools.independent_from_scratch_audit_v3"
OWNERSHIP_AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
PREVIOUS_OWNERSHIP_POLICY_RELATIVE = (
    "tools/independent_from_scratch_audit_v2.py"
)
PREVIOUS_OWNERSHIP_POLICY_SHA256 = (
    "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
)
PINNED_STDLIB_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
IMMUTABLE_OWNERSHIP_POLICY_SHA256 = types.MappingProxyType({
    PREVIOUS_OWNERSHIP_POLICY_RELATIVE: PREVIOUS_OWNERSHIP_POLICY_SHA256,
    V5_GUARD_RELATIVE: V5_GUARD_SHA256,
})
PUBLISHED_SEED = 0x5459_5045_5345_5231
UINT64_MAX = (1 << 64) - 1
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_NORMALIZATION_DEPTH = 24
PROCESS_TIMEOUT_SECONDS = 180
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
FAMILY_NAMES = ("rust", "c", "zig")
FAMILY_PATHS = types.MappingProxyType({
    "rust": types.MappingProxyType({
        "adapter": "candidates/rust_candidate.py",
        "engine": "candidates/_rust_engine.so",
        "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "sources": (
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
        "binaries": (
            "candidates/_rust_engine.so",
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        ),
    }),
    "c": types.MappingProxyType({
        "adapter": "candidates/vm_candidate.py",
        "engine": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "bridge": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "sources": (
            "candidates/vm_candidate.py",
            "candidates/_vm_native.c",
        ),
        "binaries": (
            "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        ),
    }),
    "zig": types.MappingProxyType({
        "adapter": "candidates/zig_candidate.py",
        "engine": "candidates/_zig_probe.so",
        "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "sources": (
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
        "binaries": (
            "candidates/_zig_probe.so",
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        ),
    }),
})

if not sys.path or sys.path[0] != ROOT:
    sys.path.insert(0, ROOT)


class PublicTypeOracleError(Exception):
    """A frozen observation, process, or native owner was forged."""


class SourceOnlyError(PublicTypeOracleError):
    """A synthetic control attempted an external side effect."""


class WorkerFailure(PublicTypeOracleError):
    """Preserve every complete stream from a genuinely failed worker."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


class TextSubclass(str):
    """An actual public text subclass, not a substitute matcher."""


class BytesSubclass(bytes):
    """An actual public bytes subclass, not a substitute matcher."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublicTypeOracleError(message)


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
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise PublicTypeOracleError(
            "a complete public observation is not canonical JSON"
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
    require(
        valid_digest(value),
        "an exact independently frozen SHA-256 is mandatory: " + label,
    )
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for name, item in items:
        require(
            type(name) is str and name not in value,
            "a duplicate canonical public-evidence field was concealed",
        )
        value[name] = item
    return value


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
        "a complete bounded public worker stream is mandatory: " + label,
    )
    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=lambda item: (_ for _ in ()).throw(
                PublicTypeOracleError(
                    "nonfinite public-evidence number: " + item
                )
            ),
        )
    except (
        PublicTypeOracleError, TypeError, ValueError, UnicodeError,
        json.JSONDecodeError,
    ) as error:
        raise PublicTypeOracleError(
            "a complete canonical public worker stream was invalid: " + label
        ) from error
    require(
        type(value) is dict and canonical(value) == raw,
        "a public worker stream was truncated, padded, or reordered: " + label,
    )
    return value


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
        raise PublicTypeOracleError(
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


def build_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
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
        value == build_matrix(PUBLISHED_SEED),
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


def normalized_public_module(module: Any, engine: Any) -> str:
    if module == getattr(engine, "__name__", None):
        return "re"
    require(type(module) is str, "a public type module is not a genuine string")
    return module


def normalize_value(
    value: Any,
    engine: Any,
    depth: int = 0,
) -> dict[str, Any]:
    require(
        type(depth) is int and 0 <= depth <= MAX_NORMALIZATION_DEPTH,
        "a public observation exceeded its bounded normalization depth",
    )
    if value is None:
        return {"kind": "none"}
    if type(value) is bool:
        return {"kind": "bool", "value": value}
    if type(value) is int:
        return {"kind": "int", "value": value}
    if type(value) is str:
        return {"kind": "str", "value": value}
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if isinstance(value, types.GenericAlias):
        return {
            "kind": "generic-alias",
            "representation": repr(value),
            "origin": normalize_value(value.__origin__, engine, depth + 1),
            "arguments": [
                normalize_value(item, engine, depth + 1)
                for item in value.__args__
            ],
        }
    if isinstance(value, type):
        return {
            "kind": "type",
            "name": value.__name__,
            "qualname": value.__qualname__,
            "module": normalized_public_module(
                getattr(value, "__module__", None),
                engine,
            ),
        }
    if isinstance(value, int):
        return {
            "kind": "int-subclass",
            "type": normalize_value(type(value), engine, depth + 1),
            "value": int(value),
            "representation": repr(value),
        }
    if type(value) is tuple:
        return {
            "kind": "tuple",
            "items": [
                normalize_value(item, engine, depth + 1) for item in value
            ],
        }
    if type(value) is list:
        return {
            "kind": "list",
            "items": [
                normalize_value(item, engine, depth + 1) for item in value
            ],
        }
    if isinstance(value, (dict, types.MappingProxyType)):
        pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for key, item in value.items():
            pairs.append((
                normalize_value(key, engine, depth + 1),
                normalize_value(item, engine, depth + 1),
            ))
        pairs.sort(key=lambda pair: canonical(pair[0]))
        return {
            "kind": "mapping",
            "mappingproxy": isinstance(value, types.MappingProxyType),
            "items": [
                {"key": key, "value": item} for key, item in pairs
            ],
        }
    if isinstance(value, (set, frozenset)):
        values = [
            normalize_value(item, engine, depth + 1) for item in value
        ]
        values.sort(key=canonical)
        return {
            "kind": "frozenset" if isinstance(value, frozenset) else "set",
            "items": values,
        }
    if callable(value):
        return {
            "kind": "callable",
            "name": getattr(value, "__name__", type(value).__name__),
            "module": normalized_public_module(
                getattr(value, "__module__", type(value).__module__),
                engine,
            ),
        }
    raise PublicTypeOracleError(
        "a public observation contains an unsupported, noncanonical object: "
        + type(value).__qualname__
    )


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
            raise PublicTypeOracleError(
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
        raise PublicTypeOracleError(
            "an unknown public normalized observation kind: " + kind
        )


def normalize_error(error: Exception, engine: Any) -> dict[str, Any]:
    public_error = getattr(engine, "PatternError", None)
    return {
        "type": normalize_value(type(error), engine),
        "message": str(error),
        "arguments": normalize_value(error.args, engine),
        "is_public_pattern_error": (
            isinstance(public_error, type)
            and isinstance(error, public_error)
        ),
        "has_message": hasattr(error, "msg"),
        "message_attribute": normalize_value(
            getattr(error, "msg", None), engine
        ),
        "has_pattern": hasattr(error, "pattern"),
        "pattern": normalize_value(getattr(error, "pattern", None), engine),
        "has_position": hasattr(error, "pos"),
        "position": normalize_value(getattr(error, "pos", None), engine),
        "has_line": hasattr(error, "lineno"),
        "line": normalize_value(getattr(error, "lineno", None), engine),
        "has_column": hasattr(error, "colno"),
        "column": normalize_value(getattr(error, "colno", None), engine),
    }


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


def normalize_warning(item: Any) -> dict[str, Any]:
    require(
        isinstance(getattr(item, "message", None), Warning)
        and isinstance(getattr(item, "category", None), type)
        and type(getattr(item, "filename", None)) is str
        and type(getattr(item, "lineno", None)) is int,
        "a genuine complete Python warning was substituted",
    )
    return {
        "category": item.category.__name__,
        "category_module": item.category.__module__,
        "message": str(item.message),
        "filename": os.path.basename(item.filename),
        "line": item.lineno,
    }


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


def preload_support_modules() -> dict[str, Any]:
    modules = {
        name: importlib.import_module(name)
        for name in ("copy", "enum", "pickle", "typing", "weakref")
    }
    require(
        all(
            type(module) is types.ModuleType
            and module.__name__ == name
            and sys.modules.get(name) is module
            for name, module in modules.items()
        ),
        "the genuine public observation support modules were substituted",
    )
    modules["types"] = types
    modules["warnings"] = warnings
    modules["_identity_probes"] = (
        modules["copy"].copy,
        modules["copy"].deepcopy,
        modules["enum"].IntFlag,
        modules["pickle"].dumps,
        modules["pickle"].loads,
        modules["typing"].get_origin,
        modules["typing"].get_args,
        modules["weakref"].ref,
        types.GenericAlias,
        warnings.catch_warnings,
        warnings.simplefilter,
    )
    verify_support_modules(modules)
    return modules


def verify_support_modules(support: Mapping[str, Any]) -> None:
    require(
        isinstance(support, Mapping)
        and set(support) == {
            "copy", "enum", "pickle", "typing", "weakref",
            "types", "warnings", "_identity_probes",
        }
        and all(
            type(support[name]) is types.ModuleType
            and support[name].__name__ == name
            and sys.modules.get(name) is support[name]
            for name in ("copy", "enum", "pickle", "typing", "weakref")
        )
        and support["types"] is types
        and support["warnings"] is warnings,
        "a genuine preloaded observation helper was replaced",
    )
    require(
        type(support["_identity_probes"]) is tuple
        and support["_identity_probes"] == (
            support["copy"].copy,
            support["copy"].deepcopy,
            support["enum"].IntFlag,
            support["pickle"].dumps,
            support["pickle"].loads,
            support["typing"].get_origin,
            support["typing"].get_args,
            support["weakref"].ref,
            types.GenericAlias,
            warnings.catch_warnings,
            warnings.simplefilter,
        ),
        "a candidate modified a copy, pickle, typing, or warning helper",
    )


def filler_pattern(pattern: str | bytes, token: str) -> str | bytes:
    suffix = "(?#rebar-public-" + token + ")"
    if type(pattern) is bytes:
        return b"(?:" + pattern + b")" + suffix.encode("ascii")
    return "(?:" + pattern + ")" + suffix


def cache_probe(
    engine: Any,
    pattern: str | bytes,
    subject: str | bytes,
    flags: int,
    case_id: str,
    *,
    limit: int,
    refresh: bool,
) -> dict[str, Any]:
    require(
        type(limit) is int and 0 <= limit <= 512,
        "a public cache-boundary observation exceeded its frozen bound",
    )
    engine.purge()
    original = engine.compile(pattern, flags)
    touch_was_identical = False
    for index in range(limit):
        if refresh and index == limit // 2:
            touch_was_identical = engine.compile(pattern, flags) is original
        engine.compile(
            filler_pattern(
                pattern,
                case_id.replace("/", "-") + "-" + str(index),
            ),
            flags,
        )
    after = engine.compile(pattern, flags)
    return {
        "limit": limit,
        "refresh": refresh,
        "touch_was_identical": touch_was_identical,
        "same_identity_after_churn": after is original,
        "pattern_equality_after_churn": after == original,
        "matching_result_after_churn": after.search(subject) is not None,
    }


def match_snapshot(match: Any, engine: Any) -> dict[str, Any]:
    if match is None:
        return {"matched": False}
    return {
        "matched": True,
        "type": normalize_value(type(match), engine),
        "group": normalize_value(match.group(0), engine),
        "groups": normalize_value(match.groups(), engine),
        "groupdict": normalize_value(match.groupdict(), engine),
        "span": normalize_value(match.span(), engine),
        "lastindex": normalize_value(match.lastindex, engine),
        "lastgroup": normalize_value(match.lastgroup, engine),
        "position": normalize_value(match.pos, engine),
        "end_position": normalize_value(match.endpos, engine),
    }


def public_action(
    case: Mapping[str, Any],
    engine: Any,
    support: Mapping[str, Any],
) -> Any:
    cohort = case["cohort"]
    domain = case["domain"]
    pattern = decode_subject(case["pattern"], domain)
    subject = decode_subject(case["subject"], domain)
    flags = case["flags"]
    protocol = case["pickle_protocol"]
    copy_module = support["copy"]
    pickle_module = support["pickle"]
    typing_module = support["typing"]
    enum_module = support["enum"]
    weakref_module = support["weakref"]
    compiled = engine.compile(pattern, flags)
    match = compiled.search(subject)
    public_exports = getattr(engine, "__all__")

    if cohort == "module-public-all":
        return tuple(public_exports)
    if cohort == "module-public-export-members":
        return tuple(
            (name, hasattr(engine, name), callable(getattr(engine, name, None)))
            for name in public_exports
        )
    if cohort == "module-accessible-extra":
        return tuple(
            (name, hasattr(engine, name), name in public_exports)
            for name in ("DEBUG", "Scanner", "__version__", "NOFLAG")
        )
    if cohort == "module-pattern-match-types":
        return (
            engine.Pattern,
            engine.Match,
            type(compiled) is engine.Pattern,
            match is not None and type(match) is engine.Match,
        )
    if cohort == "module-public-error-alias":
        return (
            engine.PatternError is engine.error,
            issubclass(engine.PatternError, Exception),
            engine.PatternError.__module__,
            engine.PatternError.__name__,
        )
    if cohort == "module-public-flag-members":
        return tuple(
            (name, hasattr(engine, name), getattr(engine, name, None))
            for name in (
                "ASCII", "IGNORECASE", "LOCALE", "MULTILINE",
                "DOTALL", "VERBOSE", "UNICODE", "NOFLAG", "DEBUG",
            )
        )
    if cohort == "module-public-callables":
        return tuple(
            (name, callable(getattr(engine, name, None)))
            for name in (
                "compile", "search", "match", "fullmatch", "findall",
                "finditer", "split", "sub", "subn", "escape", "purge",
                "Scanner",
            )
        )
    if cohort == "module-star-export-equivalence":
        return (
            len(public_exports),
            len(set(public_exports)),
            tuple((name, hasattr(engine, name)) for name in public_exports),
        )
    if cohort == "flags-short-aliases":
        return tuple(
            (
                short,
                long,
                getattr(engine, short) is getattr(engine, long),
                int(getattr(engine, short)),
            )
            for short, long in (
                ("A", "ASCII"), ("I", "IGNORECASE"),
                ("L", "LOCALE"), ("M", "MULTILINE"),
                ("S", "DOTALL"), ("X", "VERBOSE"),
                ("U", "UNICODE"),
            )
        )
    if cohort == "flags-intflag-membership":
        observed = engine.RegexFlag(flags)
        return (
            isinstance(observed, enum_module.IntFlag),
            isinstance(observed, int),
            type(observed) is engine.RegexFlag,
            int(observed),
            observed,
        )
    if cohort == "flags-zero-and-combinations":
        return (
            engine.NOFLAG,
            engine.RegexFlag(0),
            engine.NOFLAG is engine.RegexFlag(0),
            engine.RegexFlag(flags),
            int(engine.RegexFlag(flags)),
            bool(engine.RegexFlag(flags)),
        )
    if cohort == "flags-unknown-bit-retention":
        unknown = engine.RegexFlag(flags | (1 << 20))
        return (
            unknown,
            int(unknown),
            isinstance(unknown, enum_module.IntFlag),
            int(unknown & engine.RegexFlag(flags)),
        )
    if cohort == "flags-representation":
        observed = engine.RegexFlag(flags)
        return (repr(observed), str(observed), int(observed))
    if cohort == "flags-compile-roundtrip":
        return (
            compiled.flags,
            int(compiled.flags),
            compiled.flags & flags == flags,
            engine.compile(pattern, engine.RegexFlag(flags)) is compiled,
        )
    if cohort == "flags-invalid-text":
        return engine.compile(
            pattern,
            int(engine.ASCII) | int(engine.UNICODE),
        )
    if cohort == "flags-invalid-bytes":
        return engine.compile(
            pattern,
            int(engine.ASCII) | int(engine.LOCALE),
        )
    if cohort.startswith("generic-"):
        owner = engine.Pattern if "pattern" in cohort else engine.Match
        if cohort.endswith("-text"):
            arguments: Any = str
        elif cohort.endswith("-bytes"):
            arguments = bytes
        elif "extra-arguments" in cohort:
            arguments = (str, bytes)
        else:
            arguments = str if domain == "str" else bytes
        alias = owner[arguments]
        return {
            "alias": alias,
            "is_generic_alias": isinstance(alias, types.GenericAlias),
            "origin": typing_module.get_origin(alias),
            "arguments": typing_module.get_args(alias),
            "dunder_origin": alias.__origin__,
            "dunder_arguments": alias.__args__,
            "representation": repr(alias),
        }
    if cohort in {"pattern-type-text", "pattern-type-bytes"}:
        return (type(compiled), type(compiled) is engine.Pattern)
    if cohort == "pattern-instance-identity":
        return (
            isinstance(compiled, engine.Pattern),
            type(compiled) is engine.Pattern,
            engine.compile(compiled) is compiled,
        )
    if cohort == "match-instance-identity":
        return (
            match is not None,
            match is not None and isinstance(match, engine.Match),
            match is not None and type(match) is engine.Match,
            match is not None and match.re is compiled,
        )
    if cohort == "pattern-public-metadata":
        return (
            compiled.pattern,
            compiled.flags,
            compiled.groups,
            dict(compiled.groupindex),
            type(compiled.pattern),
        )
    if cohort == "match-public-metadata":
        return match_snapshot(match, engine)
    if cohort == "pattern-groupindex-immutability":
        index = compiled.groupindex
        prior = dict(index)
        mutation_error: Exception | None = None
        try:
            index["synthetic-public-group"] = 999
        except Exception as error:
            mutation_error = error
        return {
            "mapping": index,
            "before": prior,
            "after": dict(compiled.groupindex),
            "unchanged": dict(compiled.groupindex) == prior,
            "mutation_error": (
                normalize_error(mutation_error, engine)
                if mutation_error is not None else None
            ),
        }
    if cohort == "pattern-and-match-representation":
        return (repr(compiled), repr(match))
    if cohort.startswith("copy-") or cohort.startswith("deepcopy-"):
        operation = (
            copy_module.deepcopy
            if cohort.startswith("deepcopy-") else copy_module.copy
        )
        original = match if "-match-" in cohort else compiled
        copied = operation(original)
        return {
            "same_identity": copied is original,
            "same_type": type(copied) is type(original),
            "match": (
                match_snapshot(copied, engine)
                if "-match-" in cohort
                else match_snapshot(copied.search(subject), engine)
            ),
        }
    if cohort.startswith("weakref-"):
        original = match if "-match-" in cohort else compiled
        observed = weakref_module.ref(original)
        return (
            observed() is original,
            type(observed).__module__,
            type(observed).__name__,
        )
    if cohort.startswith("hash-pattern-"):
        equivalent = engine.compile(pattern, engine.RegexFlag(flags))
        return (
            isinstance(hash(compiled), int),
            compiled == equivalent,
            hash(compiled) == hash(equivalent),
            len({compiled, equivalent}),
        )
    if cohort.startswith("pattern-equality-"):
        equivalent = engine.compile(pattern, engine.RegexFlag(flags))
        different = engine.compile(
            filler_pattern(pattern, case["case"].replace("/", "-")),
            flags,
        )
        return (
            compiled == equivalent,
            compiled != different,
            equivalent == compiled,
            len({compiled, equivalent, different}),
        )
    if cohort.startswith("pickle-"):
        if cohort == "pickle-match-rejection":
            return pickle_module.dumps(match, protocol=protocol)
        payload = pickle_module.dumps(compiled, protocol=protocol)
        restored = pickle_module.loads(payload)
        return {
            "protocol": protocol,
            "roundtrip_type": type(restored),
            "same_public_type": type(restored) is type(compiled),
            "same_pattern": restored.pattern == compiled.pattern,
            "same_flags": restored.flags == compiled.flags,
            "same_groups": restored.groups == compiled.groups,
            "same_groupindex": (
                dict(restored.groupindex) == dict(compiled.groupindex)
            ),
            "same_public_equality": restored == compiled,
            "restored_match": match_snapshot(restored.search(subject), engine),
            "original_match": match_snapshot(match, engine),
        }
    if cohort in {"cache-identity-text", "cache-identity-bytes"}:
        return (
            engine.compile(pattern, flags) is compiled,
            engine.compile(pattern, engine.RegexFlag(flags)) is compiled,
        )
    if cohort == "cache-flag-separation":
        different = engine.compile(pattern, flags ^ 2)
        return (
            different is compiled,
            different == compiled,
            compiled.flags,
            different.flags,
        )
    if cohort == "cache-pattern-type-separation":
        subclass = (
            TextSubclass(pattern)
            if domain == "str" else BytesSubclass(pattern)
        )
        subclass_pattern = engine.compile(subclass, flags)
        return (
            subclass_pattern is compiled,
            subclass_pattern == compiled,
            type(subclass_pattern.pattern),
            subclass_pattern.search(subject) is not None,
        )
    if cohort == "cache-purge-identity":
        before = engine.compile(pattern, flags)
        result = engine.purge()
        after = engine.compile(pattern, flags)
        return (
            result,
            before is compiled,
            before is after,
            before == after,
            match_snapshot(after.search(subject), engine),
        )
    if cohort == "cache-fifo-boundary":
        return cache_probe(
            engine, pattern, subject, flags, case["case"],
            limit=256, refresh=False,
        )
    if cohort == "cache-lru-boundary":
        return cache_probe(
            engine, pattern, subject, flags, case["case"],
            limit=512, refresh=True,
        )
    if cohort == "cache-template-and-purge":
        replacement = r"\g<0>" if domain == "str" else rb"\g<0>"
        before = compiled.sub(replacement, subject)
        engine.purge()
        refreshed = engine.compile(pattern, flags)
        return (
            before,
            refreshed.sub(replacement, subject),
            before == refreshed.sub(replacement, subject),
            compiled is refreshed,
        )
    replacement = "x" if domain == "str" else b"x"
    if cohort == "warnings-positional-sub":
        return engine.sub(pattern, replacement, subject, 1)
    if cohort == "warnings-positional-subn":
        return engine.subn(pattern, replacement, subject, 1)
    if cohort == "warnings-positional-split":
        return engine.split(pattern, subject, 1)
    if cohort == "errors-duplicate-sub":
        return engine.sub(pattern, replacement, subject, 1, count=1)
    if cohort == "errors-duplicate-subn":
        return engine.subn(pattern, replacement, subject, 1, count=1)
    if cohort == "errors-duplicate-split":
        return engine.split(pattern, subject, 1, maxsplit=1)
    if cohort == "errors-pattern-attributes":
        broken: str | bytes = (
            "(?P<same>a)(?P<same>b)"
            if domain == "str" else b"(?P<same>a)(?P<same>b)"
        )
        return engine.compile(broken, flags)
    if cohort == "errors-multiline-pattern-attributes":
        broken = (
            "(a)\n(?P<same>a)(?P<same>b)"
            if domain == "str" else b"(a)\n(?P<same>a)(?P<same>b)"
        )
        return engine.compile(broken, flags)
    raise PublicTypeOracleError(
        "a frozen public case has no matching observation: " + cohort
    )


def observe_case(
    case: Mapping[str, Any],
    engine: Any,
    support: Mapping[str, Any],
) -> dict[str, Any]:
    verify_support_modules(support)
    with warnings.catch_warnings(record=True) as observed_warnings:
        warnings.simplefilter("always")
        try:
            actual = public_action(case, engine, support)
        except Exception as error:
            outcome: dict[str, Any] = {
                "status": "raise",
                "exception": normalize_error(error, engine),
                "warnings": [],
            }
        else:
            outcome = {
                "status": "return",
                "value": normalize_value(actual, engine),
                "warnings": [],
            }
    outcome["warnings"] = [
        normalize_warning(item) for item in observed_warnings
    ]
    validate_outcome(outcome)
    verify_support_modules(support)
    return {
        "case": case["case"],
        "cohort": case["cohort"],
        "domain": case["domain"],
        "pattern_index": case["pattern_index"],
        "flags": case["flags"],
        "pickle_protocol": case["pickle_protocol"],
        "outcome": outcome,
    }


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


def verify_runtime(*, synthetic: bool = False) -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path)
        and sys.path[0] == ROOT
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == SOURCE_ABSOLUTE,
        "use only the exact isolated pinned CPython 3.14.6 and frozen source",
    )
    require(
        not any(
            name == "candidates"
            or name.startswith("candidates.")
            or name.partition(".")[0] in FORBIDDEN_EXTERNAL_ROOTS
            for name in sys.modules
        ),
        "a candidate or external matcher entered the source/reference worker",
    )
    if not synthetic:
        require(
            os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE
            and os.path.realpath(ROOT) == ROOT,
            "a pinned public oracle or project root was redirected",
        )


def read_pinned_file(
    absolute: str,
    expected: str,
    *,
    label: str,
    maximum: int = MAX_SOURCE_BYTES,
) -> dict[str, Any]:
    checked_digest(expected, label)
    require(
        type(absolute) is str
        and os.path.isabs(absolute)
        and os.path.abspath(absolute) == absolute
        and os.path.realpath(absolute) == absolute
        and type(maximum) is int
        and 0 < maximum <= MAX_BINARY_BYTES,
        "an exact, bounded, nonsymlink public owner is mandatory: " + label,
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise PublicTypeOracleError(
            "an actual pinned public owner could not be opened: " + label
        ) from error
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and 0 < before.st_size <= maximum,
            "a pinned public owner is not a bounded regular file: " + label,
        )
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(
                type(part) is bytes and bool(part),
                "an actual public source was truncated: " + label,
            )
            hasher.update(part)
            remaining -= len(part)
        require(
            os.read(descriptor, 1) == b"",
            "a pinned public owner grew during observation: " + label,
        )
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and hasher.hexdigest() == expected,
            "an exact public source owner was substituted: " + label,
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


def verify_reference_modules() -> None:
    for name in tuple(sys.modules):
        require(
            type(name) is str
            and name != "candidates"
            and not name.startswith("candidates.")
            and name.partition(".")[0] not in FORBIDDEN_EXTERNAL_ROOTS,
            "a candidate or external regular-expression engine entered "
            "an isolated standard reference: " + str(name),
        )


def authenticate_standard_reference(
    source_pin: str,
) -> tuple[types.ModuleType, dict[str, dict[str, Any]]]:
    verify_runtime()
    checked_digest(source_pin, "prospectively frozen public type oracle")
    owners: dict[str, dict[str, Any]] = {
        "oracle": read_pinned_file(
            SOURCE_ABSOLUTE, source_pin, label="public type oracle",
        ),
        "python": read_pinned_file(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            label="stable CPython executable",
            maximum=MAX_BINARY_BYTES,
        ),
        "v5_guard": read_pinned_file(
            ROOT + "/" + V5_GUARD_RELATIVE,
            V5_GUARD_SHA256,
            label="independently frozen V5 ownership guard",
        ),
        "ownership_audit": read_pinned_file(
            ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
            label="independently frozen V3 from-scratch audit",
        ),
    }
    for name, (filename, pinned) in UPSTREAM_TEST_SOURCES.items():
        owners[name] = read_pinned_file(
            UPSTREAM_TEST_DIRECTORY + filename,
            pinned,
            label="genuine original CPython public source " + name,
        )
    engine = importlib.import_module("re")
    for name, (filename, pinned) in PINNED_STDLIB_SOURCES.items():
        absolute = PINNED_STDLIB_DIRECTORY + filename
        module = importlib.import_module(name)
        require(
            type(module) is types.ModuleType
            and module.__name__ == name
            and getattr(module, "__file__", None) == absolute,
            "a genuine CPython matcher source was substituted: " + name,
        )
        owners[name] = read_pinned_file(
            absolute, pinned, label="pinned standard matcher " + name
        )
    native = sys.modules.get("_sre")
    require(
        type(engine) is types.ModuleType
        and engine.__name__ == "re"
        and type(native) is types.ModuleType
        and getattr(getattr(native, "__spec__", None), "origin", None)
        == "built-in"
        and getattr(engine, "PatternError", None)
        is getattr(engine, "error", None),
        "the actual standard CPython reference matcher was substituted",
    )
    verify_reference_modules()
    return engine, owners


def validate_source_owners(
    value: Any,
    source_pin: str,
) -> dict[str, dict[str, Any]]:
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
        "v5_guard_relative": V5_GUARD_RELATIVE,
        "v5_guard_sha256": V5_GUARD_SHA256,
        "ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "candidate_guard_installed": False,
    }


def validate_reference_guard(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and value == make_reference_guard(2 * CASE_COUNT),
        "a complete standard-reference and helper-identity guard was forged",
    )
    return value


def observe_reference_worker(
    role: str,
    source_pin: str,
) -> dict[str, Any]:
    require(
        role in {"reference_a", "reference_b"},
        "only one of the two genuine standard reference roles is permitted",
    )
    matrix = build_matrix()
    validate_matrix(matrix)
    engine, owners_before = authenticate_standard_reference(source_pin)
    support = preload_support_modules()
    records: list[dict[str, Any]] = []
    checks = 0
    for case in matrix:
        verify_reference_modules()
        verify_support_modules(support)
        checks += 1
        try:
            record = observe_case(case, engine, support)
        finally:
            verify_reference_modules()
            verify_support_modules(support)
            checks += 1
        records.append(record)
    records_sha256 = digest(records)
    validate_records(matrix, records, records_sha256)
    owners_after = authenticate_standard_reference(source_pin)[1]
    require(
        owners_before == owners_after,
        "a pinned standard public source changed during observation",
    )
    document = {
        "schema": SCHEMA + "-isolated-public-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "candidate_family": None,
        "pid": os.getpid(),
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "records_sha256": records_sha256,
        "records": records,
        "source_owners": owners_before,
        "reference_guard": make_reference_guard(checks),
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
    return validate_reference_worker(
        document,
        role=role,
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=document["pid"],
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
        and type(expected_pid) is int
        and expected_pid > 0,
        "an independently isolated genuine reference PID is mandatory",
    )
    expected = {
        "schema": SCHEMA + "-isolated-public-worker",
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


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(
        type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
        "a complete bounded public worker stream is mandatory",
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
        and valid_digest(value.get("sha256"))
        and value.get("complete") is True,
        "a complete reversible public worker stream was hidden: " + label,
    )
    try:
        raw = base64.b64decode(
            value["base64"].encode("ascii"), validate=True
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise PublicTypeOracleError(
            "a public worker stream is not exact canonical base64: " + label
        ) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == value["sha256"]
        and base64.b64encode(raw).decode("ascii") == value["base64"],
        "a complete public worker stream was truncated or substituted: "
        + label,
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
        result[path] = checked_digest(source_hash, label + " " + path)
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
    checked_digest(candidate_source, family + " independently owned adapter")
    checked_digest(native_engine, family + " independently owned engine")
    checked_digest(native_bridge, family + " independently owned bridge")
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


def load_candidate_guards() -> tuple[Any, Any]:
    read_pinned_file(
        ROOT + "/" + V5_GUARD_RELATIVE,
        V5_GUARD_SHA256,
        label="complete frozen V5 matcher guard",
    )
    read_pinned_file(
        ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
        OWNERSHIP_AUDIT_SHA256,
        label="complete frozen V3 from-scratch ownership audit",
    )
    v5 = importlib.import_module(V5_GUARD_MODULE)
    audit = importlib.import_module(OWNERSHIP_AUDIT_MODULE)
    require(
        type(v5) is types.ModuleType
        and v5.__name__ == V5_GUARD_MODULE
        and getattr(v5, "SOURCE_RELATIVE", None) == V5_GUARD_RELATIVE
        and v5.current_source_sha256() == V5_GUARD_SHA256
        and type(audit) is types.ModuleType
        and audit.__name__ == OWNERSHIP_AUDIT_MODULE
        and getattr(audit, "SOURCE_RELATIVE", None)
        == OWNERSHIP_AUDIT_RELATIVE
        and getattr(audit, "PINNED_PYTHON_SHA256", None)
        == PINNED_PYTHON_SHA256,
        "a genuine immutable V5 or V3 native ownership policy was replaced",
    )
    return v5, audit


def validate_relative_owner(
    value: Any,
    relative: str,
    expected: str,
) -> dict[str, Any]:
    checked_digest(expected, "exact independently owned " + relative)
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
        and value.get("audit_source_sha256") == OWNERSHIP_AUDIT_SHA256,
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
        OWNERSHIP_AUDIT_RELATIVE,
        OWNERSHIP_AUDIT_SHA256,
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
            PINNED_STDLIB_CTYPES_SHA256
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


def execute_candidate_worker(
    manifest: Mapping[str, Any],
    source_pin: str,
) -> dict[str, Any]:
    family = manifest["family"]
    matrix = build_matrix()
    validate_matrix(matrix)
    reference, source_owners = authenticate_standard_reference(source_pin)
    support = preload_support_modules()
    v5, audit = load_candidate_guards()
    expected = audit.validate_family_pins(
        family,
        manifest["candidate_source_sha256"],
        manifest["native_engine_sha256"],
        manifest["native_bridge_sha256"],
        [
            path + "=" + value
            for path, value in manifest["source_sha256"].items()
        ],
        [
            path + "=" + value
            for path, value in manifest["native_sha256"].items()
        ],
    )
    closure_before = audit.authenticate_closure(
        family,
        expected,
        OWNERSHIP_AUDIT_SHA256,
    )
    native_before = audit.serializable_owners(closure_before)
    audit.validate_serializable_owners(
        native_before,
        family,
        expected,
        OWNERSHIP_AUDIT_SHA256,
    )
    chosen = v5.family_spec(family)
    pins = {
        "source": manifest["candidate_source_sha256"],
        "native_engine": manifest["native_engine_sha256"],
        "native_bridge": manifest["native_bridge_sha256"],
    }
    warning, identity, _, _ = v5.load_frozen_oracles()
    records: list[dict[str, Any]] = []
    guard_snapshot: dict[str, Any] | None = None
    native_provenance: dict[str, Any] | None = None
    with warning.installed_warning_safe_guard(identity):
        with v5.chosen_original_guard(
            reference,
            pins,
            chosen,
            identity,
            warning,
        ) as active:
            candidate = active.get("candidate")
            require(
                type(candidate) is types.ModuleType
                and candidate.__name__ == chosen.adapter_module
                and active.get("actual_method_guard_checks") == 0
                and active.get("actual_warning_registry_guard_checks") == 0,
                "a complete chosen candidate guard did not start from zero",
            )
            for case in matrix:
                active["verify"]()
                verify_support_modules(support)
                active["actual_method_guard_checks"] += 1
                try:
                    record = observe_case(case, candidate, support)
                finally:
                    active["verify"]()
                    verify_support_modules(support)
                    active["actual_method_guard_checks"] += 1
                records.append(record)
            guard_snapshot = snapshot_candidate_guard(active, family)
            provenance = active.get("native_provenance")
            require(
                v5.validate_owners(provenance, chosen, pins),
                "the candidate escaped its independently owned native bridge",
            )
            native_provenance = dict(provenance)
    require(
        guard_snapshot is not None and native_provenance is not None,
        "the actual continuous candidate guard or native owner was omitted",
    )
    closure_after = audit.authenticate_closure(
        family,
        expected,
        OWNERSHIP_AUDIT_SHA256,
    )
    native_after = audit.serializable_owners(closure_after)
    require(
        native_before == native_after,
        "the complete V3-owned candidate closure changed during matching",
    )
    records_sha256 = digest(records)
    validate_records(matrix, records, records_sha256)
    native_evidence = {
        "manifest": dict(expected),
        "audit_source_sha256": OWNERSHIP_AUDIT_SHA256,
        "owners": native_after,
        "v5_native_provenance": native_provenance,
    }
    validate_native_evidence(native_evidence, manifest)
    return {
        "schema": SCHEMA + "-isolated-public-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": "candidate-" + family,
        "candidate_family": family,
        "pid": os.getpid(),
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "records_sha256": records_sha256,
        "records": records,
        "source_owners": source_owners,
        "reference_guard": None,
        "native_owners": native_evidence,
        "candidate_guard": guard_snapshot,
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
        and value.get("schema") == SCHEMA + "-isolated-public-worker"
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


def run_isolated_process(
    role: str,
    arguments: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        type(role) is str
        and (
            role in {"reference_a", "reference_b"}
            or role in {"candidate-rust", "candidate-c", "candidate-zig"}
        )
        and type(arguments) is list
        and all(type(item) is str for item in arguments)
        and arguments[:3] == [PINNED_PYTHON, "-I", "-B"],
        "a public worker escaped its exact isolated CPython command",
    )
    process: subprocess.Popen[bytes] | None = None
    stdout = b""
    stderr = b""
    timed_out = False
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
        try:
            stdout, stderr = process.communicate(
                timeout=PROCESS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            stdout, stderr = process.communicate()
    except (OSError, subprocess.SubprocessError) as error:
        raise WorkerFailure(
            "a genuine isolated public worker could not start",
            {
                "role": role,
                "pid": process.pid if process is not None else None,
                "error_type": type(error).__qualname__,
                "error": str(error),
                "stdout": encode_stream(stdout),
                "stderr": encode_stream(stderr),
            },
        ) from error
    require(process is not None, "a genuine public process was not created")
    evidence = {
        "role": role,
        "pid": process.pid,
        "returncode": process.returncode,
        "timed_out": timed_out,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    if timed_out or process.returncode != 0 or stderr:
        raise WorkerFailure(
            "an isolated public worker failed; preserve both complete streams",
            evidence,
        )
    try:
        worker = decode_canonical(stdout, role)
        validate_process_evidence(evidence, worker, role=role)
    except (PublicTypeOracleError, TypeError, ValueError, KeyError) as error:
        failed = dict(evidence)
        failed["validation_error"] = {
            "type": type(error).__qualname__,
            "message": str(error),
        }
        raise WorkerFailure(
            "a complete genuine public worker stream failed validation",
            failed,
        ) from error
    return worker, evidence


def reference_arguments(role: str, source_pin: str) -> list[str]:
    return [
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


def run_reference_pair(
    source_pin: str,
) -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str,
]:
    verify_runtime()
    matrix = build_matrix()
    validate_matrix(matrix)
    first, first_process = run_isolated_process(
        "reference_a",
        reference_arguments("reference_a", source_pin),
    )
    second, second_process = run_isolated_process(
        "reference_b",
        reference_arguments("reference_b", source_pin),
    )
    records_sha256 = validate_reference_pair(
        first,
        second,
        first_process,
        second_process,
        source_pin=source_pin,
        matrix=matrix,
    )
    return first, second, first_process, second_process, records_sha256


def run_baseline(source_pin: str, matrix_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "exact frozen public type oracle source")
    require(
        checked_digest(matrix_pin, "exact frozen public type matrix")
        == MATRIX_SHA256,
        "a different public compatibility matrix was substituted",
    )
    _, owners_before = authenticate_standard_reference(source_pin)
    first, second, first_process, second_process, records_sha256 = (
        run_reference_pair(source_pin)
    )
    _, owners_after = authenticate_standard_reference(source_pin)
    require(
        owners_before == owners_after == first["source_owners"]
        == second["source_owners"],
        "the original public baseline sources changed during observation",
    )
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
        "baseline_records_sha256": records_sha256,
        "source_owners": owners_before,
        "reference_processes": [first_process, second_process],
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


def candidate_arguments(
    manifest: Mapping[str, Any],
    source_pin: str,
) -> list[str]:
    arguments = [
        PINNED_PYTHON,
        "-I",
        "-B",
        SOURCE_ABSOLUTE,
        "--internal-candidate-worker",
        "--candidate",
        manifest["family"],
        "--oracle-source-sha256",
        source_pin,
        "--matrix-sha256",
        MATRIX_SHA256,
        "--ownership-audit-source-sha256",
        OWNERSHIP_AUDIT_SHA256,
        "--candidate-source-sha256",
        manifest["candidate_source_sha256"],
        "--native-engine-sha256",
        manifest["native_engine_sha256"],
        "--native-bridge-sha256",
        manifest["native_bridge_sha256"],
    ]
    for path, value in manifest["source_sha256"].items():
        arguments.extend(["--owned-source-sha256", path + "=" + value])
    for path, value in manifest["native_sha256"].items():
        arguments.extend(["--native-artifact-sha256", path + "=" + value])
    return arguments


def run_candidate(
    manifest: Mapping[str, Any],
    source_pin: str,
    matrix_pin: str,
    baseline_pin: str,
) -> dict[str, Any]:
    verify_runtime()
    require(
        checked_digest(source_pin, "prospectively frozen public type oracle")
        and checked_digest(matrix_pin, "prospectively frozen public matrix")
        == MATRIX_SHA256,
        "an exact frozen public oracle and matrix are mandatory",
    )
    checked_digest(baseline_pin, "frozen dual-reference public outcome vector")
    matrix = build_matrix()
    validate_matrix(matrix)
    first, second, first_process, second_process, actual_baseline = (
        run_reference_pair(source_pin)
    )
    require(
        actual_baseline == baseline_pin,
        "fresh independent references do not reproduce the frozen baseline",
    )
    role = "candidate-" + manifest["family"]
    candidate, candidate_process = run_isolated_process(
        role,
        candidate_arguments(manifest, source_pin),
    )
    validate_candidate_worker(
        candidate,
        manifest=manifest,
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=candidate_process["pid"],
    )
    require(
        candidate["pid"] not in {first["pid"], second["pid"]},
        "the independent candidate reused a genuine reference worker PID",
    )
    mismatches = []
    for reference, observed in zip(
        first["records"],
        candidate["records"],
        strict=True,
    ):
        if reference["outcome"] != observed["outcome"]:
            mismatches.append({
                "case": reference["case"],
                "cohort": reference["cohort"],
                "reference": reference["outcome"],
                "candidate": observed["outcome"],
            })
    return {
        "schema": SCHEMA + "-candidate-comparison",
        "status": "PASS" if not mismatches else "FAIL",
        "python": "3.14.6",
        "candidate_family": manifest["family"],
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "baseline_records_sha256": baseline_pin,
        "candidate_records_sha256": candidate["records_sha256"],
        "mismatch_count": len(mismatches),
        "matched_case_count": CASE_COUNT - len(mismatches),
        "mismatches": mismatches,
        "source_owners": first["source_owners"],
        "native_owners": candidate["native_owners"],
        "candidate_guard": candidate["candidate_guard"],
        "reference_processes": [first_process, second_process],
        "candidate_process": candidate_process,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": candidate["actual_candidate_imports"],
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
        "schema": SCHEMA + "-isolated-public-worker",
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
                SCHEMA + ":" + family + ":" + kind + ":" + relative
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
            OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
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
        "audit_source_sha256": OWNERSHIP_AUDIT_SHA256,
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
            PINNED_STDLIB_CTYPES_SHA256 if is_zig else None
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
        "schema": SCHEMA + "-isolated-public-worker",
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
        matrix=build_matrix(),
        expected_pid=pid,
    )
    return worker, manifest


def source_self_test() -> dict[str, Any]:
    verify_runtime(synthetic=True)
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(
            type(name) is str and name not in accepted and bool(condition),
            "a positive synthetic public control failed: " + name,
        )
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(
            type(name) is str and name not in rejected and callable(action),
            "a negative synthetic public control was reused",
        )
        try:
            action()
        except (
            PublicTypeOracleError,
            TypeError,
            ValueError,
            KeyError,
            OSError,
            OverflowError,
        ):
            rejected.append(name)
            return
        raise PublicTypeOracleError(
            "a forged synthetic public control was accepted: " + name
        )

    with SourceOnlyBoundary() as boundary:
        matrix = build_matrix()
        observed_matrix = digest(matrix)
        if not valid_digest(MATRIX_SHA256):
            return {
                "schema": SCHEMA + "-synthetic-self-test",
                "status": "UNFROZEN",
                "python": "3.14.6",
                "published_seed": PUBLISHED_SEED,
                "observed_matrix_sha256": observed_matrix,
                "case_count": CASE_COUNT,
                "cohort_count": len(COHORTS),
                "variants_per_cohort": VARIANTS_PER_COHORT,
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
            }
        accept(
            "freeze-all-6912-source-ordered-public-property-cases",
            validate_matrix(matrix) == MATRIX_SHA256,
        )
        accept(
            "preserve-the-full-unsigned-64-bit-public-seed",
            PUBLISHED_SEED == 0x5459_5045_5345_5231
            and (1 << 53) < PUBLISHED_SEED <= UINT64_MAX,
        )
        accept(
            "freeze-72-distinct-meaningful-public-behavior-cohorts",
            len(COHORTS) == len(set(COHORTS)) == 72,
        )
        accept(
            "freeze-96-distinct-pattern-and-flag-inputs-in-every-cohort",
            all(
                len({
                    (row["pattern_index"], row["flags_index"])
                    for row in matrix if row["cohort"] == name
                }) == VARIANTS_PER_COHORT
                for name in COHORTS
            ),
        )
        accept(
            "preserve-both-real-text-and-bytes-public-domains",
            {row["domain"] for row in matrix} == {"str", "bytes"},
        )
        accept(
            "preserve-all-six-real-pickle-protocols-in-every-cohort",
            all(
                {
                    row["pickle_protocol"] for row in matrix
                    if row["cohort"] == name
                } == set(PICKLE_PROTOCOLS)
                for name in COHORTS
            ),
        )
        accept(
            "preserve-all-eight-independent-public-flag-combinations",
            all(
                {
                    row["flags"] for row in matrix
                    if row["cohort"] == name
                } == set(FLAG_VALUES)
                for name in COHORTS
            ),
        )
        accept(
            "pin-all-four-genuine-standard-matcher-sources",
            set(PINNED_STDLIB_SOURCES) == {
                "re", "re._compiler", "re._parser", "re._constants",
            }
            and all(
                valid_digest(pinned)
                for _, pinned in PINNED_STDLIB_SOURCES.values()
            ),
        )
        accept(
            "pin-both-literal-original-upstream-public-test-sources",
            set(UPSTREAM_TEST_SOURCES) == {
                "upstream_test_re", "upstream_re_tests",
            }
            and all(
                valid_digest(pinned)
                for _, pinned in UPSTREAM_TEST_SOURCES.values()
            ),
        )
        accept(
            "pin-independent-original-v5-and-from-scratch-v3-guards",
            valid_digest(V5_GUARD_SHA256)
            and valid_digest(OWNERSHIP_AUDIT_SHA256),
        )
        accept(
            "distinguish-genuine-text-and-bytes-public-inputs",
            encode_subject("a") != encode_subject(b"a"),
        )
        accept(
            "preserve-lone-unicode-surrogates-in-canonical-evidence",
            b"\\ud800" in canonical(
                {"kind": "str", "value": "\ud800"},
            ),
        )
        source_pin = hashlib.sha256(
            (SCHEMA + ":synthetic-source").encode("ascii"),
        ).hexdigest()
        records = synthetic_records(matrix)
        records_pin = digest(records)
        accept(
            "retain-all-6912-complete-synthetic-public-outcomes",
            validate_records(matrix, records, records_pin) is records,
        )
        first = synthetic_reference(
            "reference_a", 42_001, source_pin, records,
        )
        second = synthetic_reference(
            "reference_b", 42_002, source_pin, records,
        )
        first_process = synthetic_process(first)
        second_process = synthetic_process(second)
        accept(
            "require-two-independent-synthetic-reference-identities",
            validate_reference_pair(
                first,
                second,
                first_process,
                second_process,
                source_pin=source_pin,
                matrix=matrix,
            ) == records_pin,
        )
        accept(
            "retain-full-reversible-standard-worker-stdout",
            decode_stream(
                first_process["stdout"],
                "synthetic standard stdout",
            ) == canonical(first),
        )
        accept(
            "retain-exact-empty-standard-worker-stderr",
            decode_stream(
                first_process["stderr"],
                "synthetic standard stderr",
            ) == b"",
        )
        accept(
            "guard-each-public-case-before-and-after-observation",
            validate_reference_guard(
                make_reference_guard(2 * CASE_COUNT),
            )["actual_method_guard_checks"] == 2 * CASE_COUNT,
        )

        for family in FAMILY_NAMES:
            manifest = synthetic_family_manifest(family)
            accept(
                "preserve-independent-" + family + "-source-and-native-owners",
                manifest["family"] == family
                and set(manifest["source_sha256"])
                == set(FAMILY_PATHS[family]["sources"])
                and set(manifest["native_sha256"])
                == set(FAMILY_PATHS[family]["binaries"]),
            )
            source_entries = [
                path + "=" + item
                for path, item in manifest["source_sha256"].items()
            ]
            native_entries = [
                path + "=" + item
                for path, item in manifest["native_sha256"].items()
            ]
            controls = (
                (
                    "missing-source",
                    manifest["candidate_source_sha256"],
                    manifest["native_engine_sha256"],
                    manifest["native_bridge_sha256"],
                    source_entries[:-1],
                    native_entries,
                ),
                (
                    "duplicate-source",
                    manifest["candidate_source_sha256"],
                    manifest["native_engine_sha256"],
                    manifest["native_bridge_sha256"],
                    source_entries + [source_entries[0]],
                    native_entries,
                ),
                (
                    "foreign-adapter",
                    "a1" * 32,
                    manifest["native_engine_sha256"],
                    manifest["native_bridge_sha256"],
                    source_entries,
                    native_entries,
                ),
                (
                    "foreign-engine",
                    manifest["candidate_source_sha256"],
                    "b2" * 32,
                    manifest["native_bridge_sha256"],
                    source_entries,
                    native_entries,
                ),
                (
                    "foreign-bridge",
                    manifest["candidate_source_sha256"],
                    manifest["native_engine_sha256"],
                    "c3" * 32,
                    source_entries,
                    native_entries,
                ),
                (
                    "missing-native",
                    manifest["candidate_source_sha256"],
                    manifest["native_engine_sha256"],
                    manifest["native_bridge_sha256"],
                    source_entries,
                    native_entries[:-1],
                ),
            )
            for name, adapter, engine, bridge, sources, natives in controls:
                reject(
                    "reject-" + family + "-" + name,
                    lambda adapter=adapter, engine=engine, bridge=bridge,
                    sources=sources, natives=natives: validate_family_manifest(
                        family,
                        adapter,
                        engine,
                        bridge,
                        sources,
                        natives,
                    ),
                )
            candidate_pid = 43_000 + FAMILY_NAMES.index(family)
            candidate_worker, candidate_manifest = synthetic_candidate(
                family,
                candidate_pid,
                source_pin,
                records,
            )
            candidate_process = synthetic_process(candidate_worker)
            accept(
                "validate-complete-synthetic-" + family + "-candidate-worker",
                validate_candidate_worker(
                    candidate_worker,
                    manifest=candidate_manifest,
                    source_pin=source_pin,
                    matrix=matrix,
                    expected_pid=candidate_pid,
                ) is candidate_worker,
            )
            accept(
                "validate-complete-synthetic-" + family + "-native-closure",
                validate_native_evidence(
                    candidate_worker["native_owners"],
                    candidate_manifest,
                ) is candidate_worker["native_owners"],
            )
            accept(
                "retain-complete-synthetic-" + family + "-candidate-stdout",
                validate_process_evidence(
                    candidate_process,
                    candidate_worker,
                    role="candidate-" + family,
                ) is candidate_process,
            )

            for field, forged in (
                ("role", "candidate-foreign"),
                ("candidate_family", "foreign"),
                ("pid", candidate_pid + 100),
                ("oracle_source_sha256", "a2" * 32),
                ("matrix_sha256", "b3" * 32),
                ("published_seed", PUBLISHED_SEED + 1),
                ("case_count", CASE_COUNT - 1),
                ("cohort_count", len(COHORTS) - 1),
                ("variants_per_cohort", VARIANTS_PER_COHORT - 1),
                ("records_sha256", "c4" * 32),
                ("actual_reference_workers", 1),
                ("actual_candidate_workers", 0),
                ("actual_candidate_imports", 0),
                ("clock_samples", 1),
                ("timing_trials_run", 1),
                ("workspace_files_written", 1),
                ("evidence_files_created", 1),
                ("benchmark_files_read", 1),
                ("hidden_cases_read", 1),
                ("performance", "MEASURED"),
                ("candidate_qualified_for_hidden_benchmark", True),
                ("final_winner_selected", True),
            ):
                changed_worker = dict(candidate_worker)
                changed_worker[field] = forged
                reject(
                    "reject-" + family + "-forged-candidate-worker-" + field,
                    lambda changed_worker=changed_worker,
                    candidate_manifest=candidate_manifest,
                    candidate_pid=candidate_pid: validate_candidate_worker(
                        changed_worker,
                        manifest=candidate_manifest,
                        source_pin=source_pin,
                        matrix=matrix,
                        expected_pid=candidate_pid,
                    ),
                )

            for field, forged in (
                ("original_matchers_blocked", False),
                ("adapter_import_quarantined", False),
                ("native_sre_blocked", False),
                ("builtins_import_guarded", False),
                ("importlib_import_guarded", False),
                ("actual_object_identity_guarded", False),
                ("warning_registry_introspection_safe", False),
                ("warning_registry_exactly_absent", False),
                ("cross_family_imports_blocked", False),
                ("external_regex_imports_blocked", False),
                ("public_type_names_used_for_ownership", True),
                ("actual_method_guard_checks", 2 * CASE_COUNT - 1),
                ("actual_warning_registry_guard_checks", 2 * CASE_COUNT - 1),
                ("owned_native_ffi_allowed", family != "zig"),
                ("trusted_stdlib_ctypes_preloaded", family != "zig"),
                ("trusted_stdlib_ctypes_builtin_verified", family != "zig"),
                (
                    "trusted_stdlib_ctypes_pythonapi_initialized",
                    family != "zig",
                ),
                (
                    "trusted_stdlib_ctypes_source_sha256",
                    "f7" * 32,
                ),
                ("owned_ctypes_load_count", -1),
                ("owned_ctypes_symbol_count", -1),
                ("cached_original_matcher_descendant_count", -1),
                ("cached_original_holder_count", -1),
            ):
                changed_guard = dict(candidate_worker["candidate_guard"])
                changed_guard[field] = forged
                reject(
                    "reject-" + family + "-forged-native-guard-" + field,
                    lambda changed_guard=changed_guard,
                    family=family: snapshot_candidate_guard(
                        changed_guard,
                        family,
                    ),
                )

            genuine_native = candidate_worker["native_owners"]
            owner_fields = genuine_native["owners"]
            source_name = next(iter(candidate_manifest["source_sha256"]))
            native_name = next(iter(candidate_manifest["native_sha256"]))
            policy_name = next(iter(IMMUTABLE_OWNERSHIP_POLICY_SHA256))
            forged_audit_manifest = dict(genuine_native["manifest"])
            forged_audit_manifest["immutable_policy_sha256"] = {
                **dict(IMMUTABLE_OWNERSHIP_POLICY_SHA256),
                policy_name: "a8" * 32,
            }
            omitted_sources = dict(owner_fields["source_owners"])
            omitted_sources.pop(source_name)
            forged_source = dict(owner_fields["source_owners"])
            forged_source[source_name] = {
                **forged_source[source_name],
                "sha256": "b9" * 32,
            }
            forged_native = dict(owner_fields["native_owners"])
            forged_native[native_name] = {
                **forged_native[native_name],
                "sha256": "ca" * 32,
            }
            forged_policy = dict(owner_fields["policy_owners"])
            forged_policy[policy_name] = {
                **forged_policy[policy_name],
                "sha256": "db" * 32,
            }
            forged_v5 = dict(genuine_native["v5_native_provenance"])
            forged_v5["native_bridge"] = {
                **forged_v5["native_bridge"],
                "sha256": "ec" * 32,
            }
            native_controls = (
                (
                    "audit-source",
                    {**genuine_native, "audit_source_sha256": "fd" * 32},
                ),
                (
                    "immutable-policy-manifest",
                    {**genuine_native, "manifest": forged_audit_manifest},
                ),
                (
                    "missing-source-owner",
                    {
                        **genuine_native,
                        "owners": {
                            **owner_fields,
                            "source_owners": omitted_sources,
                        },
                    },
                ),
                (
                    "forged-source-owner",
                    {
                        **genuine_native,
                        "owners": {
                            **owner_fields,
                            "source_owners": forged_source,
                        },
                    },
                ),
                (
                    "forged-native-owner",
                    {
                        **genuine_native,
                        "owners": {
                            **owner_fields,
                            "native_owners": forged_native,
                        },
                    },
                ),
                (
                    "forged-policy-owner",
                    {
                        **genuine_native,
                        "owners": {
                            **owner_fields,
                            "policy_owners": forged_policy,
                        },
                    },
                ),
                (
                    "forged-audit-oracle-owner",
                    {
                        **genuine_native,
                        "owners": {
                            **owner_fields,
                            "oracle_owner": {
                                **owner_fields["oracle_owner"],
                                "sha256": "ad" * 32,
                            },
                        },
                    },
                ),
                (
                    "forged-pinned-python-owner",
                    {
                        **genuine_native,
                        "owners": {
                            **owner_fields,
                            "python_owner": {
                                **owner_fields["python_owner"],
                                "sha256": "be" * 32,
                            },
                        },
                    },
                ),
                (
                    "forged-v5-native-bridge-provenance",
                    {
                        **genuine_native,
                        "v5_native_provenance": forged_v5,
                    },
                ),
            )
            for name, forged_evidence in native_controls:
                reject(
                    "reject-" + family + "-" + name,
                    lambda forged_evidence=forged_evidence,
                    candidate_manifest=candidate_manifest:
                    validate_native_evidence(
                        forged_evidence,
                        candidate_manifest,
                    ),
                )
                poisoned_worker = {
                    **candidate_worker,
                    "native_owners": forged_evidence,
                }
                reject(
                    "reject-" + family + "-candidate-with-" + name,
                    lambda poisoned_worker=poisoned_worker,
                    candidate_manifest=candidate_manifest,
                    candidate_pid=candidate_pid:
                    validate_candidate_worker(
                        poisoned_worker,
                        manifest=candidate_manifest,
                        source_pin=source_pin,
                        matrix=matrix,
                        expected_pid=candidate_pid,
                    ),
                )
            reject(
                "reject-" + family + "-substituted-candidate-stdout",
                lambda candidate_process=candidate_process,
                candidate_worker=candidate_worker,
                family=family: validate_process_evidence(
                    {
                        **candidate_process,
                        "stdout": first_process["stdout"],
                    },
                    candidate_worker,
                    role="candidate-" + family,
                ),
            )

        reject(
            "reject-an-altered-full-64-bit-public-seed",
            lambda: validate_matrix(build_matrix(PUBLISHED_SEED + 1)),
        )
        reject(
            "reject-a-truncated-public-property-matrix",
            lambda: validate_matrix(matrix[:-1]),
        )
        reject(
            "reject-a-padded-public-property-matrix",
            lambda: validate_matrix(matrix + [matrix[0]]),
        )
        reject(
            "reject-a-reordered-public-property-matrix",
            lambda: validate_matrix(matrix[1:] + matrix[:1]),
        )
        reject(
            "reject-a-duplicated-public-property-input",
            lambda: validate_matrix([matrix[0], *matrix[2:], matrix[0]]),
        )
        original = matrix[0]
        changes = (
            ("case", original["case"] + "/hidden"),
            ("cohort", "hidden"),
            ("cohort_index", (original["cohort_index"] + 1) % len(COHORTS)),
            ("variant", (original["variant"] + 1) % VARIANTS_PER_COHORT),
            ("domain", "hidden"),
            ("pattern_index", (original["pattern_index"] + 1) % 12),
            ("flags_index", (original["flags_index"] + 1) % 8),
            ("flags", original["flags"] ^ 2),
            ("pattern", {"kind": "bytes", "hex": "00"}),
            ("subject", {"kind": "bytes", "hex": "00"}),
            ("pickle_protocol", 99),
            ("published_seed", PUBLISHED_SEED + 1),
        )
        for field, forged in changes:
            changed = dict(original)
            changed[field] = forged
            reject(
                "reject-a-forged-public-matrix-" + field,
                lambda changed=changed: validate_matrix(
                    [changed, *matrix[1:]],
                ),
            )
        reject(
            "reject-truncated-public-case-outcomes",
            lambda: validate_records(matrix, records[:-1], records_pin),
        )
        reject(
            "reject-reordered-public-case-outcomes",
            lambda: validate_records(
                matrix,
                records[1:] + records[:1],
                records_pin,
            ),
        )
        reject(
            "reject-a-substituted-complete-public-outcome-digest",
            lambda: validate_records(matrix, records, "d4" * 32),
        )
        reject(
            "reject-duplicate-canonical-public-evidence-fields",
            lambda: decode_canonical(
                b'{"value":1,"value":2}\n',
                "duplicate synthetic evidence",
            ),
        )
        reject(
            "reject-noncanonical-public-evidence-whitespace",
            lambda: decode_canonical(
                b'{ "value":1}\n',
                "noncanonical synthetic evidence",
            ),
        )
        reject(
            "reject-nonfinite-public-evidence-values",
            lambda: decode_canonical(
                b'{"value":NaN}\n',
                "nonfinite synthetic evidence",
            ),
        )
        reject(
            "reject-a-truncated-public-worker-stdout",
            lambda: decode_stream(
                {
                    **first_process["stdout"],
                    "bytes": first_process["stdout"]["bytes"] - 1,
                },
                "truncated synthetic public stdout",
            ),
        )
        reject(
            "reject-an-incomplete-public-worker-stdout",
            lambda: decode_stream(
                {**first_process["stdout"], "complete": False},
                "incomplete synthetic public stdout",
            ),
        )
        reject(
            "reject-the-same-pid-for-both-standard-workers",
            lambda: validate_reference_pair(
                first,
                {**second, "pid": first["pid"]},
                first_process,
                second_process,
                source_pin=source_pin,
                matrix=matrix,
            ),
        )
        reject(
            "reject-a-substituted-standard-worker-stdout",
            lambda: validate_process_evidence(
                {
                    **first_process,
                    "stdout": second_process["stdout"],
                },
                first,
                role="reference_a",
            ),
        )
        for field, forged in (
            ("candidate_import_count", 1),
            ("external_regex_import_count", 1),
            ("actual_method_guard_checks", 2 * CASE_COUNT - 1),
            ("required_method_guard_checks", 2 * CASE_COUNT - 1),
            ("preloaded_support_modules_guarded", False),
            ("v5_guard_relative", "tools/foreign_guard.py"),
            ("v5_guard_sha256", "e5" * 32),
            ("ownership_audit_relative", "tools/foreign_audit.py"),
            ("ownership_audit_sha256", "f6" * 32),
            ("candidate_guard_installed", True),
        ):
            changed_guard = make_reference_guard(2 * CASE_COUNT)
            changed_guard[field] = forged
            reject(
                "reject-a-forged-public-reference-guard-" + field,
                lambda changed_guard=changed_guard: (
                    validate_reference_guard(changed_guard)
                ),
            )
        for field, forged in (
            ("role", "reference_b"),
            ("pid", 42_002),
            ("matrix_sha256", "e5" * 32),
            ("published_seed", PUBLISHED_SEED + 1),
            ("case_count", CASE_COUNT - 1),
            ("cohort_count", len(COHORTS) - 1),
            ("variants_per_cohort", VARIANTS_PER_COHORT - 1),
            ("actual_reference_workers", 0),
            ("actual_candidate_workers", 1),
            ("actual_candidate_imports", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("workspace_files_written", 1),
            ("evidence_files_created", 1),
            ("benchmark_files_read", 1),
            ("hidden_cases_read", 1),
            ("performance", "MEASURED"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
        ):
            forged_worker = dict(first)
            forged_worker[field] = forged
            reject(
                "reject-a-forged-public-standard-worker-" + field,
                lambda forged_worker=forged_worker: (
                    validate_reference_worker(
                        forged_worker,
                        role="reference_a",
                        source_pin=source_pin,
                        matrix=matrix,
                        expected_pid=42_001,
                    )
                ),
            )

        reject(
            "block-genuine-public-source-file-reads",
            lambda: builtins.open(SOURCE_ABSOLUTE, "rb"),
        )
        reject(
            "block-genuine-public-source-file-writes",
            lambda: builtins.open(SOURCE_ABSOLUTE, "wb"),
        )
        reject(
            "block-all-genuine-filesystem-metadata",
            lambda: os.stat(SOURCE_ABSOLUTE),
        )
        reject(
            "block-all-genuine-native-candidate-imports",
            lambda: importlib.import_module("candidates.rust_candidate"),
        )
        reject(
            "block-all-external-regular-expression-package-imports",
            lambda: importlib.import_module("regex"),
        )
        reject(
            "block-genuine-standard-matcher-imports",
            lambda: importlib.import_module("re"),
        )
        reject(
            "block-all-genuine-isolated-reference-workers",
            lambda: subprocess.Popen([PINNED_PYTHON, "-I", "-B"]),
        )
        reject(
            "block-all-genuine-native-extension-execution",
            lambda: importlib.machinery.ExtensionFileLoader(
                "synthetic_forbidden_native_extension",
                ROOT + "/candidates/synthetic_forbidden_native.so",
            ).exec_module(
                types.ModuleType("synthetic_forbidden_native_extension")
            ),
        )
        reject(
            "block-background-native-worker-threads",
            lambda: threading.Thread(target=lambda: None).start(),
        )
        reject("block-wall-clock-sampling", lambda: time.time())
        reject("block-monotonic-clock-sampling", lambda: time.monotonic())
        reject("block-performance-clock-sampling", lambda: time.perf_counter())
        reject(
            "block-operating-system-randomness",
            lambda: os.urandom(1),
        )
        reject(
            "block-garbage-collection-side-effects",
            lambda: gc.collect(),
        )
        blocked = dict(boundary.blocked)
        accept(
            "exercise-all-source-only-side-effect-protections",
            all(
                blocked[name] > 0
                for name in (
                    "file_reads",
                    "file_writes",
                    "processes",
                    "native_loads",
                    "candidate_imports",
                    "dynamic_imports",
                    "clock_samples",
                    "threads",
                    "garbage_collections",
                    "randomness",
                )
            ),
        )
        accept(
            "load-no-candidate-or-external-regular-expression-package",
            not any(
                name == "candidates"
                or name.startswith("candidates.")
                or name.partition(".")[0] in FORBIDDEN_EXTERNAL_ROOTS
                for name in sys.modules
            ),
        )

    return {
        "schema": SCHEMA + "-synthetic-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "pickle_protocols": list(PICKLE_PROTOCOLS),
        "flag_values": list(FLAG_VALUES),
        "positive_control_count": len(accepted),
        "negative_control_count": len(rejected),
        "positive_controls": accepted,
        "negative_controls": rejected,
        "source_only_blocked_operations": blocked,
        "v5_guard_relative": V5_GUARD_RELATIVE,
        "v5_guard_sha256": V5_GUARD_SHA256,
        "ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
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


def parse_arguments(
    arguments: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Independently frozen CPython 3.14.6 public regex types, "
            "identity, flags, serialization, cache, warnings, and errors"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--record-baseline", action="store_true")
    modes.add_argument("--record-candidate", action="store_true")
    modes.add_argument(
        "--internal-reference-worker",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    modes.add_argument(
        "--internal-candidate-worker",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--role", choices=("reference_a", "reference_b"))
    parser.add_argument("--candidate", choices=FAMILY_NAMES)
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--baseline-records-sha256")
    parser.add_argument("--ownership-audit-source-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument(
        "--owned-source-sha256",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--native-artifact-sha256",
        action="append",
        default=[],
    )
    return parser.parse_args(arguments)


def options_manifest(options: argparse.Namespace) -> dict[str, Any]:
    require(
        checked_digest(
            options.ownership_audit_source_sha256,
            "exact independently frozen V3 ownership audit",
        ) == OWNERSHIP_AUDIT_SHA256,
        "the candidate selected a substituted from-scratch ownership policy",
    )
    return validate_family_manifest(
        options.candidate,
        options.candidate_source_sha256,
        options.native_engine_sha256,
        options.native_bridge_sha256,
        options.owned_source_sha256,
        options.native_artifact_sha256,
    )


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(
            options.role is None
            and options.candidate is None
            and options.oracle_source_sha256 is None
            and options.matrix_sha256 is None
            and options.baseline_records_sha256 is None
            and options.ownership_audit_source_sha256 is None
            and options.candidate_source_sha256 is None
            and options.native_engine_sha256 is None
            and options.native_bridge_sha256 is None
            and not options.owned_source_sha256
            and not options.native_artifact_sha256,
            "a source-only self-test cannot select a genuine worker or owner",
        )
        result = source_self_test()
    else:
        verify_runtime()
        source_pin = checked_digest(
            options.oracle_source_sha256,
            "prospectively frozen exact public type oracle source",
        )
        require(
            checked_digest(
                options.matrix_sha256,
                "prospectively frozen exact public property matrix",
            ) == MATRIX_SHA256,
            "the public compatibility denominator or matrix was changed",
        )
        if options.record_baseline:
            require(
                options.role is None
                and options.candidate is None
                and options.baseline_records_sha256 is None
                and options.ownership_audit_source_sha256 is None
                and options.candidate_source_sha256 is None
                and options.native_engine_sha256 is None
                and options.native_bridge_sha256 is None
                and not options.owned_source_sha256
                and not options.native_artifact_sha256,
                "a genuine standard baseline cannot select a candidate",
            )
            result = run_baseline(source_pin, options.matrix_sha256)
        elif options.internal_reference_worker:
            require(
                options.role in {"reference_a", "reference_b"}
                and options.candidate is None
                and options.baseline_records_sha256 is None
                and options.ownership_audit_source_sha256 is None
                and options.candidate_source_sha256 is None
                and options.native_engine_sha256 is None
                and options.native_bridge_sha256 is None
                and not options.owned_source_sha256
                and not options.native_artifact_sha256,
                "an isolated standard worker cannot select a native candidate",
            )
            result = observe_reference_worker(options.role, source_pin)
        elif options.internal_candidate_worker:
            require(
                options.role is None
                and options.baseline_records_sha256 is None,
                "an independently owned candidate worker escaped its role",
            )
            result = execute_candidate_worker(
                options_manifest(options),
                source_pin,
            )
        else:
            require(
                options.record_candidate
                and options.role is None,
                "an exact public candidate comparison mode is mandatory",
            )
            result = run_candidate(
                options_manifest(options),
                source_pin,
                options.matrix_sha256,
                checked_digest(
                    options.baseline_records_sha256,
                    "frozen two-reference public outcome vector",
                ),
            )
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WorkerFailure as error:
        sys.stderr.buffer.write(canonical({
            "schema": SCHEMA + "-controller-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "message": str(error),
            "process_evidence": error.evidence,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        sys.stderr.buffer.flush()
        raise SystemExit(1)
    except (
        PublicTypeOracleError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        sys.stderr.buffer.write(canonical({
            "schema": SCHEMA + "-controller-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "message": str(error),
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        sys.stderr.buffer.flush()
        raise SystemExit(1)
