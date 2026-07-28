#!/usr/bin/env python3
"""Durably establish one pure, frozen, two-CPython public-contract baseline.

``--self-test`` is entirely synthetic: it cannot read a project file, import a
project module, start a process, measure time, or publish evidence.  Actual
recording requires ``--record``, one category, one fresh label, and explicit
recorder, frozen-contract, and matrix source pins.  The only actual workers are
the original V3 contract's isolated CPython ``reference_a`` and ``reference_b``.
No candidate is imported, observed, qualified, or selected.
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
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
import traceback
import types
from typing import Any, Callable, Iterator, Mapping
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/record_independent_public_contract_baselines_v1.py"
SCHEMA = "rebar-independent-public-contract-v3-pure-baselines-v1"
CONTRACT_RELATIVE = "tools/independent_public_contract_v3.py"
CONTRACT_MODULE = "tools.independent_public_contract_v3"
CONTRACT_SHA256 = (
    "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3"
)
CONTRACT_SCHEMA = "rebar-independent-public-contract-v3"
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
V2_RELATIVE = "tools/independent_public_contract_v2.py"
V2_SHA256 = (
    "a0ae9621e06b760477a167705cc6e521cc7e9df4d44d126e39c614df89bd3e68"
)
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
APPROVED_DIRECTORY = "oracle/cpython-3.14.6/evidence"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 192 * 1024 * 1024
MAX_ARCHIVE_BYTES = 96 * 1024 * 1024
MAX_RECEIPT_BYTES = 1024 * 1024
CHUNK_BYTES = 1024 * 1024
HEX_DIGITS = frozenset("0123456789abcdef")


@dataclass(frozen=True, slots=True)
class CategorySpec:
    name: str
    module: str
    source_relative: str
    source_sha256: str
    matrix_sha256: str
    baseline_sha256: str
    published_seed: int
    case_count: int
    group_count: int
    cases_per_group: int


CATEGORIES: Mapping[str, CategorySpec] = types.MappingProxyType({
    "public": CategorySpec(
        "public", "tools.rust_public_practice_benchmark_v1",
        "tools/rust_public_practice_benchmark_v1.py",
        "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
        "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
        "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
        0x5245_4241_525F_5031, 864, 36, 24,
    ),
    "scanner": CategorySpec(
        "scanner", "tools.rust_scanner_differential_v1",
        "tools/rust_scanner_differential_v1.py",
        "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
        "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
        "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
        0x5343_414E_4E45_5231, 1024, 32, 32,
    ),
    "buffer": CategorySpec(
        "buffer", "tools.rust_memoryview_expand_differential_v1",
        "tools/rust_memoryview_expand_differential_v1.py",
        "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
        "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
        "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
        0x4D45_5850_414E_4431, 768, 24, 32,
    ),
})

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


class BaselineError(Exception):
    """A pure reference, frozen source, or durable baseline was substituted."""


class SourceOnlyError(BaselineError):
    """An in-memory synthetic control attempted an external side effect."""


class PublicationFailure(BaselineError):
    """Retain every actual publication attempt without inventing success."""

    def __init__(self, message: str, ledger: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.ledger = dict(ledger)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BaselineError(message)


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise BaselineError("evidence is not complete canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and len(set(value)) > 1 and all(char in HEX_DIGITS for char in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "duplicate evidence keys are forbidden")
        result[key] = value
    return result


def decode_canonical(raw: Any, label: str, maximum: int) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= maximum,
        "complete bounded canonical bytes are mandatory: " + label,
    )
    try:
        document = json.loads(
            raw,
            object_pairs_hook=unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                BaselineError("nonfinite evidence is forbidden")
            ),
        )
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise BaselineError("invalid canonical evidence: " + label) from error
    require(type(document) is dict and canonical(document) == raw,
            "canonical bytes were changed or truncated: " + label)
    return document


def category_spec(value: Any) -> CategorySpec:
    require(type(value) is str and value in CATEGORIES,
            "select exactly one original public, scanner, or buffer category")
    spec = CATEGORIES[value]
    require(
        isinstance(spec, CategorySpec) and spec.name == value
        and spec.module.startswith("tools.")
        and spec.source_relative.startswith("tools/")
        and spec.source_relative.endswith(".py")
        and all(
            validate_digest(item, value + " frozen source")
            for item in (spec.source_sha256, spec.matrix_sha256,
                         spec.baseline_sha256)
        )
        and type(spec.published_seed) is int and spec.published_seed > 0
        and type(spec.group_count) is int and spec.group_count > 0
        and type(spec.cases_per_group) is int and spec.cases_per_group > 0
        and spec.case_count == spec.group_count * spec.cases_per_group
        and (spec.name, spec.case_count, spec.group_count,
             spec.cases_per_group) in {
            ("public", 864, 36, 24),
            ("scanner", 1024, 32, 32),
            ("buffer", 768, 24, 32),
        },
        "an independently frozen source, seed, or denominator changed",
    )
    return spec


def validate_label(value: Any) -> str:
    require(
        type(value) is str and 1 <= len(value) <= 48
        and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-"
                for char in value)
        and "--" not in value,
        "one bounded, lowercase, nonescaping baseline label is mandatory",
    )
    return value


def safe_parts(relative: Any) -> tuple[str, ...]:
    require(
        type(relative) is str and bool(relative)
        and "\\" not in relative and "\x00" not in relative,
        "an exact no-follow relative path is mandatory",
    )
    parts = tuple(relative.split("/"))
    require(
        bool(parts) and all(part not in ("", ".", "..") for part in parts)
        and "/".join(parts) == relative,
        "a source or baseline path escaped its exact approved root",
    )
    return parts


def approved_paths(category: Any, label: Any) -> tuple[str, str]:
    selected = category_spec(category)
    slug = (
        "public-contract-baseline-v1-" + selected.name
        + "-" + validate_label(label)
    )
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json.gz",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


def directory_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )


def regular_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path) and sys.path[0] == str(ROOT)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
        and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE)
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
        "use only the isolated, pinned, no-bytecode CPython 3.14.6 recorder",
    )
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "a pure CPython baseline recorder must never import a candidate",
    )


def read_owned_regular(relative: str, expected: str,
                       maximum: int) -> dict[str, Any]:
    parts = safe_parts(relative)
    validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_REPORT_BYTES,
            "bound every immutable original source")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact project root is not an owned directory")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an immutable source parent follows a symlink")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        initial = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            stat.S_ISREG(initial.st_mode) and stat.S_ISREG(named.st_mode)
            and (initial.st_dev, initial.st_ino)
            == (named.st_dev, named.st_ino)
            and 0 < initial.st_size <= maximum,
            "an immutable no-follow source was replaced: " + relative,
        )
        remaining = initial.st_size
        hasher = hashlib.sha256()
        while remaining:
            chunk = os.read(descriptor, min(remaining, CHUNK_BYTES))
            require(type(chunk) is bytes and 0 < len(chunk) <= remaining,
                    "an original source was truncated: " + relative)
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "an original source gained hidden trailing bytes: " + relative)
        final = os.fstat(descriptor)
        require(
            (initial.st_dev, initial.st_ino, initial.st_size)
            == (final.st_dev, final.st_ino, final.st_size)
            and hasher.hexdigest() == expected,
            "an exact frozen original source changed: " + relative,
        )
        return {
            "relative": relative, "sha256": expected,
            "bytes": initial.st_size, "device": initial.st_dev,
            "inode": initial.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def authenticate_contract(recorder_pin: str,
                          selected: CategorySpec) -> dict[str, Any]:
    verify_runtime()
    recorder_pin = validate_digest(recorder_pin, "baseline recorder source")
    sources = {
        "recorder": read_owned_regular(
            SOURCE_RELATIVE, recorder_pin, MAX_SOURCE_BYTES,
        ),
        "contract": read_owned_regular(
            CONTRACT_RELATIVE, CONTRACT_SHA256, MAX_SOURCE_BYTES,
        ),
        "original_v5": read_owned_regular(
            V5_RELATIVE, V5_SHA256, MAX_SOURCE_BYTES,
        ),
        "previous_v2": read_owned_regular(
            V2_RELATIVE, V2_SHA256, MAX_SOURCE_BYTES,
        ),
        "category": read_owned_regular(
            selected.source_relative, selected.source_sha256,
            MAX_SOURCE_BYTES,
        ),
    }
    contract = importlib.import_module(CONTRACT_MODULE)
    module_spec = getattr(contract, "__spec__", None)
    loader = getattr(module_spec, "loader", None)
    exact = str(ROOT / CONTRACT_RELATIVE)
    require(
        type(contract) is types.ModuleType
        and contract.__name__ == CONTRACT_MODULE
        and getattr(contract, "SCHEMA", None) == CONTRACT_SCHEMA
        and getattr(contract, "SOURCE_RELATIVE", None) == CONTRACT_RELATIVE
        and os.path.abspath(getattr(contract, "__file__", "")) == exact
        and os.path.realpath(getattr(contract, "__file__", "")) == exact
        and module_spec is not None
        and getattr(module_spec, "name", None) == CONTRACT_MODULE
        and getattr(module_spec, "origin", None) == exact
        and isinstance(loader, importlib.machinery.SourceFileLoader)
        and getattr(loader, "name", None) == CONTRACT_MODULE
        and getattr(loader, "path", None) == exact,
        "the pre-authenticated original V3 contract was substituted on import",
    )
    require(
        read_owned_regular(CONTRACT_RELATIVE, CONTRACT_SHA256,
                           MAX_SOURCE_BYTES) == sources["contract"],
        "the immutable V3 source changed during its authenticated import",
    )
    frozen = contract.category_spec(selected.name)
    require(
        all(
            getattr(frozen, field) == getattr(selected, field)
            for field in (
                "name", "module", "source_relative", "source_sha256",
                "matrix_sha256", "baseline_sha256", "published_seed",
                "case_count", "group_count", "cases_per_group",
            )
        ),
        "the exact independently frozen V3 category was substituted",
    )
    _, _, _, matrix, groups, owners = contract.load_prerequisites(frozen)
    contract.validate_matrix_document(
        frozen, matrix, selected.matrix_sha256, groups,
    )
    require(
        contract.canonical(matrix) == canonical(matrix)
        and digest(matrix) == selected.matrix_sha256
        and len(matrix) == selected.case_count
        and len(groups) == selected.group_count
        and all(
            owners[key] == sources[key]
            for key in ("original_v5", "previous_v2", "category")
        )
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "a complete original matrix, source closure, or zero-candidate guard changed",
    )
    return {
        "contract": contract, "category": frozen,
        "local_category": selected, "matrix": matrix,
        "groups": groups, "source_provenance": sources,
        "recorder_source_sha256": recorder_pin,
    }


def verify_source_closure(context: Mapping[str, Any]) -> dict[str, Any]:
    selected = context["local_category"]
    expected = context["source_provenance"]
    actual = {
        "recorder": read_owned_regular(
            SOURCE_RELATIVE, context["recorder_source_sha256"],
            MAX_SOURCE_BYTES,
        ),
        "contract": read_owned_regular(
            CONTRACT_RELATIVE, CONTRACT_SHA256, MAX_SOURCE_BYTES,
        ),
        "original_v5": read_owned_regular(
            V5_RELATIVE, V5_SHA256, MAX_SOURCE_BYTES,
        ),
        "previous_v2": read_owned_regular(
            V2_RELATIVE, V2_SHA256, MAX_SOURCE_BYTES,
        ),
        "category": read_owned_regular(
            selected.source_relative, selected.source_sha256,
            MAX_SOURCE_BYTES,
        ),
    }
    require(actual == expected,
            "the complete candidate-free frozen source closure changed")
    verify_runtime()
    return actual


def encode_stream(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "retain a complete bounded reference stream: " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
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
        "a complete pure reference stream was hidden: " + label,
    )
    expected = validate_digest(value.get("sha256"), label + " stream")
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise BaselineError("invalid complete process base64: " + label) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == expected
        and base64.b64encode(raw).decode("ascii") == value["base64"],
        "a reversible reference process stream was forged: " + label,
    )
    return raw


def validate_outcome(selected: CategorySpec, outcome: Any) -> None:
    require(type(outcome) is dict and outcome.get("status") in ("return", "raise"),
            "a complete original public outcome was hidden")
    result_field = "value" if outcome["status"] == "return" else "exception"
    if selected.name == "public":
        fields = {"status", "callbacks", "warnings", result_field}
    elif selected.name == "scanner":
        fields = {
            "status", "callbacks", "warnings", "combined_pattern",
            "lexicon", result_field,
        }
    else:
        fields = {
            "status", "stage", "match_before", "source_after",
            "mutation", "warnings", result_field,
        }
    require(
        set(outcome) == fields and type(outcome.get("warnings")) is list,
        "a callback, warning, scanner, buffer, exception, or outcome was hidden",
    )
    if selected.name in ("public", "scanner"):
        require(type(outcome.get("callbacks")) is list,
                "ordered replacement callbacks were omitted")
    if selected.name == "buffer":
        require(type(outcome.get("stage")) is str,
                "the original buffer observation stage was omitted")
    if result_field == "exception":
        require(type(outcome.get("exception")) is dict,
                "the complete original Python exception was hidden")


def validate_matrix_rows(
    selected: CategorySpec, matrix: Any, groups: Any,
    expected_sha256: str,
) -> list[dict[str, Any]]:
    validate_digest(expected_sha256, selected.name + " matrix")
    require(
        type(matrix) is list and len(matrix) == selected.case_count
        and type(groups) is tuple and len(groups) == selected.group_count
        and all(type(group) is str and bool(group) for group in groups)
        and len(set(groups)) == len(groups)
        and digest(matrix) == expected_sha256,
        "the complete source-ordered case matrix was substituted",
    )
    counts = {group: 0 for group in groups}
    domains = {"text": 0, "bytes": 0}
    seen: set[str] = set()
    for row in matrix:
        require(
            type(row) is dict and type(row.get("case")) is str
            and row["case"] not in seen,
            "an original case was missing, repeated, or reordered",
        )
        seen.add(row["case"])
        key = row.get("operation") if selected.name == "public" else row.get("family")
        require(type(key) is str and key in counts,
                "an original category group was changed")
        counts[key] += 1
        if selected.name == "public":
            domain = row.get("domain")
            require(domain in domains,
                    "an original public text-or-bytes domain was changed")
            domains[domain] += 1
    require(all(count == selected.cases_per_group for count in counts.values()),
            "an original complete group denominator was changed")
    if selected.name == "public":
        require(domains == {"text": 432, "bytes": 432},
                "the original 432 text and 432 bytes stimuli were changed")
    return matrix


def validate_records_rows(
    selected: CategorySpec, matrix: list[dict[str, Any]],
    records: Any, expected_sha256: str,
) -> list[dict[str, Any]]:
    validate_digest(expected_sha256, selected.name + " observation vector")
    require(
        type(records) is list and len(records) == selected.case_count
        and len(matrix) == selected.case_count
        and digest(records) == expected_sha256,
        "a complete source-ordered reference vector was substituted",
    )
    for stimulus, observation in zip(matrix, records, strict=True):
        fields = {"case", "outcome"} if selected.name == "public" else {
            "case", "family", "outcome",
        }
        require(
            type(observation) is dict and set(observation) == fields
            and observation.get("case") == stimulus.get("case")
            and (
                selected.name == "public"
                or observation.get("family") == stimulus.get("family")
            ),
            "a complete source-ordered stimulus or observation was changed",
        )
        validate_outcome(selected, observation["outcome"])
    return records


def validate_reference(
    context: Mapping[str, Any], role: str,
    document: Any, process: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in ("reference_a", "reference_b"),
            "a baseline can run only two original CPython references")
    contract = context["contract"]
    frozen = context["category"]
    selected = context["local_category"]
    matrix = context["matrix"]
    require(
        type(process) is dict and type(process.get("pid")) is int
        and process["pid"] > 0,
        "a genuine separate reference process and PID are mandatory",
    )
    actual = contract.validate_worker_document(
        document, role=role, category=frozen, family=None,
        source_pin=CONTRACT_SHA256, matrix=matrix,
        expected_pid=process["pid"], pins=None,
    )
    contract.validate_process_evidence(
        process, role=role, category=frozen, family=None,
        expected_pid=process["pid"], result=actual,
    )
    require(
        actual.get("candidate_import_count") == 0
        and actual.get("actual_candidate_workers") == 0
        and actual.get("candidate_family") is None
        and actual.get("native_provenance") is None
        and actual.get("owned_source_closure") is None
        and actual.get("matcher_guard") is None
        and actual.get("records_sha256") == selected.baseline_sha256
        and actual.get("published_seed") == selected.published_seed
        and actual.get("matrix_sha256") == selected.matrix_sha256
        and actual.get("case_count") == selected.case_count
        and decode_stream(process.get("stdout"), role + " stdout")
        == canonical(actual)
        and decode_stream(process.get("stderr"), role + " stderr") == b"",
        "a candidate, invalid reference, process stream, or foreign guard escaped",
    )
    validate_records_rows(
        selected, matrix, actual.get("records"),
        selected.baseline_sha256,
    )
    contract.validate_records(
        frozen, matrix, actual.get("records"), selected.baseline_sha256,
    )
    require(
        actual.get("source_provenance") == {
            key: context["source_provenance"][key]
            for key in ("original_v5", "previous_v2", "category")
        },
        "the original pure reference source owner changed",
    )
    return actual, process


def deterministic_archive(payload: Any) -> bytes:
    require(
        type(payload) is bytes and 0 < len(payload) <= MAX_REPORT_BYTES,
        "bound the complete canonical uncompressed baseline evidence",
    )
    compressed = gzip.compress(payload, compresslevel=9, mtime=0)
    require(
        type(compressed) is bytes and 10 <= len(compressed) <= MAX_ARCHIVE_BYTES
        and compressed[:2] == b"\x1f\x8b"
        and compressed[2] == 8 and compressed[3] & 0x08 == 0
        and compressed[4:8] == b"\x00\x00\x00\x00",
        "the bounded deterministic gzip header was changed",
    )
    require(bounded_inflate(compressed, MAX_REPORT_BYTES) == payload,
            "the deterministic gzip baseline failed its exact round trip")
    return compressed


def bounded_inflate(raw: Any, maximum: int) -> bytes:
    require(
        type(raw) is bytes and 10 <= len(raw) <= MAX_ARCHIVE_BYTES
        and type(maximum) is int and 0 < maximum <= MAX_REPORT_BYTES,
        "reject an unbounded or truncated baseline gzip",
    )
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        result = decoder.decompress(raw, maximum + 1)
        require(
            len(result) <= maximum and not decoder.unconsumed_tail
            and decoder.eof and not decoder.unused_data,
            "reject a gzip bomb, suffix, or concatenated gzip member",
        )
        tail = decoder.flush()
    except zlib.error as error:
        raise BaselineError("the bounded baseline gzip is corrupted") from error
    require(
        type(tail) is bytes and len(result) + len(tail) <= maximum
        and decoder.eof and not decoder.unused_data,
        "reject a gzip bomb or hidden second member",
    )
    return result + tail


def verify_directory_identity(
    retained: tuple[int, int], expected: tuple[int, int],
    literal: tuple[int, int],
) -> None:
    require(
        all(type(identity) is tuple and len(identity) == 2
            and all(type(item) is int and item >= 0 for item in identity)
            for identity in (retained, expected, literal))
        and retained == expected == literal,
        "the exact no-follow baseline evidence directory changed identity",
    )


def verify_retained_directory(preflight: Mapping[str, Any],
                              fs: Any = os) -> int:
    descriptor = preflight.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "retain the original no-follow baseline evidence directory")
    retained = fs.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode),
            "the retained baseline evidence descriptor is not a directory")
    opened: list[int] = []
    try:
        current = fs.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(fs.fstat(current).st_mode),
                "the literal baseline project root was replaced")
        for component in safe_parts(APPROVED_DIRECTORY):
            current = fs.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(fs.fstat(current).st_mode),
                    "the baseline evidence parent follows a symlink")
        literal = fs.fstat(current)
        verify_directory_identity(
            (retained.st_dev, retained.st_ino),
            (preflight.get("directory_device"),
             preflight.get("directory_inode")),
            (literal.st_dev, literal.st_ino),
        )
    finally:
        for opened_descriptor in reversed(opened):
            fs.close(opened_descriptor)
    return descriptor


@contextlib.contextmanager
def preflight_fresh_outputs(
    category: str, label: str, fs: Any = os,
) -> Iterator[dict[str, Any]]:
    archive, receipt = approved_paths(category, label)
    archive_parts = safe_parts(archive)
    receipt_parts = safe_parts(receipt)
    require(
        archive_parts[:-1] == receipt_parts[:-1]
        == safe_parts(APPROVED_DIRECTORY)
        and archive_parts[-1] != receipt_parts[-1]
        and archive_parts[-1].endswith(".json.gz")
        and receipt_parts[-1].endswith("-publication-receipt.json"),
        "preflight exactly two distinct original-only baseline outputs",
    )
    opened: list[int] = []
    try:
        current = fs.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(fs.fstat(current).st_mode),
                "the original baseline root was replaced")
        for component in archive_parts[:-1]:
            current = fs.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(fs.fstat(current).st_mode),
                    "a baseline evidence parent is missing or a symlink")
        for basename in (archive_parts[-1], receipt_parts[-1]):
            try:
                fs.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise BaselineError("refusing to overwrite baseline evidence: " + basename)
        info = fs.fstat(current)
        preflight = {
            "archive_relative": archive,
            "receipt_relative": receipt,
            "archive_basename": archive_parts[-1],
            "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": info.st_dev,
            "directory_inode": info.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_references": True,
        }
        verify_retained_directory(preflight, fs)
        yield preflight
    finally:
        for descriptor in reversed(opened):
            fs.close(descriptor)


def _error_summary(error: BaseException) -> dict[str, Any]:
    return {"type": type(error).__name__, "message": str(error)}


def _close_owned_descriptor(
    state: dict[str, Any], key: str, ledger: dict[str, Any],
    event_name: str, fs: Any,
) -> None:
    descriptor = state.get(key)
    require(type(descriptor) is int and descriptor >= 0,
            "close exactly one genuinely owned " + event_name + " descriptor")
    state[key] = None
    event = {"event": event_name, "fd": descriptor, "completed": False}
    ledger["descriptor_lifetime_events"].append(event)
    try:
        fs.close(descriptor)
    except BaseException as error:
        event["error"] = _error_summary(error)
        raise
    event["completed"] = True


def _readback_payload(
    preflight: Mapping[str, Any], basename: str,
    expected: bytes, identity: tuple[int, int],
    ledger: dict[str, Any], fs: Any,
) -> None:
    directory = verify_retained_directory(preflight, fs)
    state: dict[str, Any] = {"reader": None}
    ledger["readback_open_attempted"] = True
    descriptor = fs.open(basename, regular_flags(), dir_fd=directory)
    require(type(descriptor) is int and descriptor >= 0,
            "the durable baseline reader was not genuinely opened")
    state["reader"] = descriptor
    ledger["descriptor_lifetime_events"].append({
        "event": "reader-open", "fd": descriptor, "completed": True,
    })
    try:
        info = fs.fstat(descriptor)
        named = fs.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(
            stat.S_ISREG(info.st_mode) and stat.S_ISREG(named.st_mode)
            and (info.st_dev, info.st_ino) == identity
            and (named.st_dev, named.st_ino) == identity
            and info.st_size == len(expected),
            "the durable baseline changed its no-follow inode or full size",
        )
        remaining = len(expected)
        hasher = hashlib.sha256()
        pieces: list[bytes] = []
        while remaining:
            piece = fs.read(descriptor, min(remaining, CHUNK_BYTES))
            require(type(piece) is bytes and 0 < len(piece) <= remaining,
                    "the complete baseline readback was truncated")
            pieces.append(piece)
            hasher.update(piece)
            remaining -= len(piece)
        require(
            fs.read(descriptor, 1) == b""
            and b"".join(pieces) == expected
            and hasher.hexdigest() == hashlib.sha256(expected).hexdigest(),
            "the complete durable baseline readback was altered",
        )
        if basename.endswith(".json.gz"):
            require(
                bounded_inflate(b"".join(pieces), MAX_REPORT_BYTES)
                == bounded_inflate(expected, MAX_REPORT_BYTES),
                "the compressed baseline readback lost its complete original report",
            )
        ledger["complete_readback_verified"] = True
    finally:
        if state["reader"] is not None:
            _close_owned_descriptor(
                state, "reader", ledger, "reader-close", fs,
            )


def publish_payload(
    preflight: Mapping[str, Any], payload: bytes,
    kind: str, fs: Any = os,
) -> dict[str, Any]:
    require(kind in ("archive", "receipt"),
            "publish only the separately preflighted archive and receipt")
    maximum = MAX_ARCHIVE_BYTES if kind == "archive" else MAX_RECEIPT_BYTES
    require(type(payload) is bytes and 0 < len(payload) <= maximum,
            "bound the complete " + kind + " publication")
    directory = verify_retained_directory(preflight, fs)
    basename = preflight[kind + "_basename"]
    temporary = (
        ".rebar-public-baseline-v1-" + basename + "-"
        + str(os.getpid()) + "-" + hashlib.sha256(payload).hexdigest()[:20]
    )
    require(len(safe_parts(temporary)) == 1,
            "the baseline temporary escaped its original directory")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    ledger: dict[str, Any] = {
        "status": "PENDING", "kind": kind,
        "path": preflight[kind + "_relative"],
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "temporary_open_attempted": False,
        "temporary_open_completed": False,
        "write_attempts": [], "actual_write_calls": 0,
        "actual_bytes_written": 0,
        "file_fsync_attempted": False,
        "file_fsync_completed": False,
        "atomic_no_overwrite_link_attempted": False,
        "atomic_no_overwrite_link": False,
        "directory_fsync_attempts": [],
        "directory_fsync_completed": False,
        "readback_open_attempted": False,
        "complete_readback_verified": False,
        "cleanup_attempted": False,
        "owned_temporary_removed": False,
        "descriptor_lifetime_events": [],
    }
    state: dict[str, Any] = {"writer": None}
    identity: tuple[int, int] | None = None
    linked = False
    try:
        ledger["temporary_open_attempted"] = True
        descriptor = fs.open(temporary, flags, 0o644, dir_fd=directory)
        require(type(descriptor) is int and descriptor >= 0,
                "the no-follow exclusive baseline writer was not opened")
        state["writer"] = descriptor
        ledger["temporary_open_completed"] = True
        ledger["descriptor_lifetime_events"].append({
            "event": "writer-open", "fd": descriptor, "completed": True,
        })
        initial = fs.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode),
                "the exclusively owned baseline temporary is not a regular file")
        identity = (initial.st_dev, initial.st_ino)
        named = fs.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the exclusively owned baseline temporary was substituted")
        position = 0
        while position < len(payload):
            requested = min(len(payload) - position, CHUNK_BYTES)
            attempt = {
                "offset": position, "requested_bytes": requested,
                "returned_bytes": None, "completed": False,
            }
            ledger["write_attempts"].append(attempt)
            try:
                written = fs.write(descriptor, payload[position:position + requested])
            except BaseException as error:
                attempt["error"] = _error_summary(error)
                raise
            attempt["returned_bytes"] = written
            require(type(written) is int and 0 < written <= requested,
                    "reject a zero, boolean, negative, or oversized baseline write")
            attempt["completed"] = True
            ledger["actual_write_calls"] += 1
            ledger["actual_bytes_written"] += written
            position += written
        ledger["file_fsync_attempted"] = True
        fs.fsync(descriptor)
        ledger["file_fsync_completed"] = True
        require(fs.fstat(descriptor).st_size == len(payload),
                "the synced baseline temporary lost complete bytes")
        _close_owned_descriptor(
            state, "writer", ledger, "writer-close", fs,
        )
        verify_retained_directory(preflight, fs)
        named = fs.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == identity,
                "the synced baseline temporary changed before linking")
        ledger["atomic_no_overwrite_link_attempted"] = True
        fs.link(
            temporary, basename,
            src_dir_fd=directory, dst_dir_fd=directory,
            follow_symlinks=False,
        )
        linked = True
        ledger["atomic_no_overwrite_link"] = True
        sync = {"stage": "final-link", "attempted": True, "completed": False}
        ledger["directory_fsync_attempts"].append(sync)
        fs.fsync(directory)
        sync["completed"] = True
        ledger["directory_fsync_completed"] = True
        final = fs.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(
            stat.S_ISREG(final.st_mode)
            and (final.st_dev, final.st_ino) == identity,
            "the no-overwrite durable baseline was substituted",
        )
        _readback_payload(preflight, basename, payload, identity, ledger, fs)
        original = fs.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((original.st_dev, original.st_ino) == identity,
                "refusing to remove a substituted baseline temporary")
        ledger["cleanup_attempted"] = True
        fs.unlink(temporary, dir_fd=directory)
        ledger["owned_temporary_removed"] = True
        sync = {"stage": "temporary-removal", "attempted": True,
                "completed": False}
        ledger["directory_fsync_attempts"].append(sync)
        fs.fsync(directory)
        sync["completed"] = True
        verify_retained_directory(preflight, fs)
        ledger["status"] = "PASS"
        return ledger
    except BaseException as error:
        ledger["status"] = "FAIL"
        ledger["failure"] = _error_summary(error)
        if state["writer"] is not None:
            try:
                _close_owned_descriptor(
                    state, "writer", ledger, "writer-close", fs,
                )
            except BaseException as close_error:
                ledger["writer_cleanup_error"] = _error_summary(close_error)
        if identity is not None and not linked:
            ledger["cleanup_attempted"] = True
            try:
                named = fs.stat(
                    temporary, dir_fd=directory, follow_symlinks=False,
                )
                if (named.st_dev, named.st_ino) == identity:
                    fs.unlink(temporary, dir_fd=directory)
                    ledger["owned_temporary_removed"] = True
                    cleanup_sync = {
                        "stage": "failure-cleanup", "attempted": True,
                        "completed": False,
                    }
                    ledger["directory_fsync_attempts"].append(cleanup_sync)
                    fs.fsync(directory)
                    cleanup_sync["completed"] = True
            except BaseException as cleanup_error:
                ledger["cleanup_error"] = _error_summary(cleanup_error)
        raise PublicationFailure(
            "complete " + kind + " baseline publication failed",
            ledger,
        ) from error


def worker_failure_evidence(
    role: str, error: BaseException,
    process: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "role": role, "error_type": type(error).__name__,
        "error": str(error), "complete_traceback": traceback.format_exc(),
        "complete_original_worker_evidence": None,
        "genuine_process_started": False,
        "genuine_process_pid": None,
    }
    observed = getattr(error, "evidence", None)
    if type(observed) is not dict and type(process) is dict:
        observed = process
    if type(observed) is dict:
        result["complete_original_worker_evidence"] = copy.deepcopy(observed)
        pid = observed.get("pid")
        if type(pid) is int and pid > 0:
            result["genuine_process_started"] = True
            result["genuine_process_pid"] = pid
    return result


def reference_mismatches(
    first: list[dict[str, Any]], second: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    require(type(first) is list and type(second) is list,
            "retain both complete reference observation vectors")
    failures: list[dict[str, Any]] = []
    for index in range(max(len(first), len(second))):
        left = first[index] if index < len(first) else None
        right = second[index] if index < len(second) else None
        if left != right:
            failures.append({
                "index": index,
                "case": left.get("case") if type(left) is dict else (
                    right.get("case") if type(right) is dict else None
                ),
                "reference_a": left, "reference_b": right,
            })
    return failures


def build_baseline_report(
    context: Mapping[str, Any], label: str,
    workers: Mapping[str, Mapping[str, Any]],
    processes: Mapping[str, Mapping[str, Any]],
    failures: list[dict[str, Any]],
    closure_after: Mapping[str, Any] | None,
) -> dict[str, Any]:
    selected = context["local_category"]
    matrix = context["matrix"]
    groups = context["groups"]
    validate_matrix_rows(
        selected, matrix, groups, selected.matrix_sha256,
    )
    require(
        type(workers) is dict and type(processes) is dict
        and set(workers).issubset({"reference_a", "reference_b"})
        and set(processes) == set(workers)
        and type(failures) is list,
        "the complete pure reference ledger was substituted",
    )
    first = workers.get("reference_a")
    second = workers.get("reference_b")
    mismatches: list[dict[str, Any]] = []
    if first is not None and second is not None:
        mismatches = reference_mismatches(first["records"], second["records"])
        if processes["reference_a"]["pid"] == processes["reference_b"]["pid"]:
            failures = [*failures, {
                "role": "reference_b", "error_type": "BaselineError",
                "error": "the two isolated CPython reference PIDs are identical",
                "complete_original_worker_evidence": copy.deepcopy(
                    processes["reference_b"]
                ),
            }]
    passed = (
        not failures and not mismatches
        and set(workers) == {"reference_a", "reference_b"}
        and closure_after == context["source_provenance"]
    )
    pids = {
        role: processes[role]["pid"]
        for role in ("reference_a", "reference_b") if role in processes
    }
    domain_counts: dict[str, int] | None = None
    if selected.name == "public":
        domain_counts = {
            "text": sum(row.get("domain") == "text" for row in matrix),
            "bytes": sum(row.get("domain") == "bytes" for row in matrix),
        }
    return {
        "schema": SCHEMA,
        "status": "PASS" if passed else "FAIL",
        "phase": "correctness-oracle-baseline",
        "python": "3.14.6",
        "label": validate_label(label),
        "category": selected.name,
        "recorder_relative": SOURCE_RELATIVE,
        "recorder_source_sha256": context["recorder_source_sha256"],
        "contract_relative": CONTRACT_RELATIVE,
        "contract_source_sha256": CONTRACT_SHA256,
        "contract_schema": CONTRACT_SCHEMA,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "previous_v2_relative": V2_RELATIVE,
        "previous_v2_sha256": V2_SHA256,
        "category_source_relative": selected.source_relative,
        "category_source_sha256": selected.source_sha256,
        "published_seed": selected.published_seed,
        "matrix_sha256": selected.matrix_sha256,
        "frozen_baseline_records_sha256": selected.baseline_sha256,
        "case_count": selected.case_count,
        "group_count": selected.group_count,
        "cases_per_group": selected.cases_per_group,
        "public_domain_counts": domain_counts,
        "source_ordered_complete_stimuli": matrix,
        "source_ordered_groups": list(groups),
        "reference_workers": {
            role: workers[role]
            for role in ("reference_a", "reference_b") if role in workers
        },
        "isolated_reference_process_evidence": {
            role: processes[role]
            for role in ("reference_a", "reference_b") if role in processes
        },
        "reference_pids": pids,
        "distinct_reference_pids": (
            len(pids) == 2 and len(set(pids.values())) == 2
        ),
        "actual_reference_workers": len(pids),
        "observed_reference_case_counts": {
            role: len(workers[role]["records"])
            for role in ("reference_a", "reference_b") if role in workers
        },
        "reference_records_sha256": {
            role: workers[role]["records_sha256"]
            for role in ("reference_a", "reference_b") if role in workers
        },
        "reference_mismatch_count": len(mismatches),
        "all_reference_mismatches": mismatches,
        "complete_reference_worker_failures": failures,
        "reference_failure_count": len(failures),
        "source_provenance_before": context["source_provenance"],
        "source_provenance_after": closure_after,
        "source_closure_unchanged": (
            closure_after == context["source_provenance"]
        ),
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "candidate_family": None,
        "candidate_records": None,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }


def build_receipt(
    report: Mapping[str, Any], preflight: Mapping[str, Any],
    archive_publication: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        archive_publication.get("status") == "PASS"
        and archive_publication.get("file_fsync_completed") is True
        and archive_publication.get("directory_fsync_completed") is True
        and archive_publication.get("complete_readback_verified") is True
        and archive_publication.get("atomic_no_overwrite_link") is True
        and archive_publication.get("owned_temporary_removed") is True,
        "publish a receipt only after the entire archive is genuinely durable",
    )
    return {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": report["status"],
        "phase": "correctness-oracle-baseline",
        "category": report["category"],
        "label": report["label"],
        "python": report["python"],
        "recorder_relative": SOURCE_RELATIVE,
        "recorder_source_sha256": report["recorder_source_sha256"],
        "contract_relative": CONTRACT_RELATIVE,
        "contract_source_sha256": CONTRACT_SHA256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "previous_v2_relative": V2_RELATIVE,
        "previous_v2_sha256": V2_SHA256,
        "category_source_relative": report["category_source_relative"],
        "category_source_sha256": report["category_source_sha256"],
        "published_seed": report["published_seed"],
        "matrix_sha256": report["matrix_sha256"],
        "frozen_baseline_records_sha256": report[
            "frozen_baseline_records_sha256"
        ],
        "case_count": report["case_count"],
        "group_count": report["group_count"],
        "cases_per_group": report["cases_per_group"],
        "public_domain_counts": report["public_domain_counts"],
        "reference_pids": report["reference_pids"],
        "distinct_reference_pids": report["distinct_reference_pids"],
        "actual_reference_workers": report["actual_reference_workers"],
        "observed_reference_case_counts": report[
            "observed_reference_case_counts"
        ],
        "reference_records_sha256": report["reference_records_sha256"],
        "reference_mismatch_count": report["reference_mismatch_count"],
        "reference_failure_count": report["reference_failure_count"],
        "complete_reference_worker_failures": report[
            "complete_reference_worker_failures"
        ],
        "source_closure_unchanged": report["source_closure_unchanged"],
        "archive_relative": preflight["archive_relative"],
        "archive_bytes": archive_publication["bytes"],
        "archive_sha256": archive_publication["sha256"],
        "archive_publication": dict(archive_publication),
        "receipt_relative": preflight["receipt_relative"],
        "receipt_self_publication": (
            "PENDING until the separately returned actual receipt write, "
            "file sync, parent sync, and full readback have completed"
        ),
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_references": True,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }


def record_baseline(
    category: str, label: str, recorder_pin: str,
    contract_pin: str, matrix_pin: str,
) -> dict[str, Any]:
    verify_runtime()
    selected = category_spec(category)
    require(
        validate_digest(contract_pin, "original frozen V3 source")
        == CONTRACT_SHA256,
        "pin the exact independently frozen V3 contract before observation",
    )
    require(
        validate_digest(matrix_pin, selected.name + " frozen case matrix")
        == selected.matrix_sha256,
        "pin the exact original full-width category matrix before observation",
    )
    validate_label(label)
    context = authenticate_contract(recorder_pin, selected)
    validate_matrix_rows(
        selected, context["matrix"], context["groups"],
        selected.matrix_sha256,
    )
    with preflight_fresh_outputs(selected.name, label) as preflight:
        contract = context["contract"]
        workers: dict[str, dict[str, Any]] = {}
        processes: dict[str, dict[str, Any]] = {}
        failures: list[dict[str, Any]] = []
        for role in ("reference_a", "reference_b"):
            if failures:
                break
            observed_process: dict[str, Any] | None = None
            try:
                result, process = contract.run_isolated_worker(
                    role=role, category=context["category"],
                    family=None, source_pin=CONTRACT_SHA256,
                    matrix=context["matrix"], pins=None,
                )
                observed_process = process
                result, process = validate_reference(
                    context, role, result, process,
                )
                if any(item.get("pid") == process["pid"]
                       for item in processes.values()):
                    raise BaselineError(
                        "the two separately isolated reference PIDs collided"
                    )
                workers[role] = result
                processes[role] = process
                verify_source_closure(context)
            except BaseException as error:
                if isinstance(error, (KeyboardInterrupt, SystemExit)):
                    raise
                failures.append(worker_failure_evidence(
                    role, error, observed_process,
                ))
        try:
            closure_after = verify_source_closure(context)
        except Exception as error:
            closure_after = None
            failures.append(worker_failure_evidence("source-closure", error))
        report = build_baseline_report(
            context, label, workers, processes, failures, closure_after,
        )
        raw_report = canonical(report)
        require(0 < len(raw_report) <= MAX_REPORT_BYTES,
                "bound the complete pure reference baseline report")
        archive = deterministic_archive(raw_report)
        archive_publication = publish_payload(preflight, archive, "archive")
        receipt = build_receipt(report, preflight, archive_publication)
        raw_receipt = canonical(receipt)
        require(0 < len(raw_receipt) <= MAX_RECEIPT_BYTES,
                "bound the complete durable pure baseline receipt")
        receipt_publication = publish_payload(
            preflight, raw_receipt, "receipt",
        )
        require(
            receipt_publication["status"] == "PASS"
            and receipt_publication["file_fsync_completed"] is True
            and receipt_publication["directory_fsync_completed"] is True
            and receipt_publication["complete_readback_verified"] is True
            and receipt_publication["atomic_no_overwrite_link"] is True
            and receipt_publication["owned_temporary_removed"] is True,
            "the receipt itself has not completed genuine durable publication",
        )
        return {
            "schema": SCHEMA + "-complete-publication",
            "status": report["status"],
            "category": selected.name,
            "label": label,
            "python": "3.14.6",
            "contract_source_sha256": CONTRACT_SHA256,
            "recorder_source_sha256": context["recorder_source_sha256"],
            "matrix_sha256": selected.matrix_sha256,
            "frozen_baseline_records_sha256": selected.baseline_sha256,
            "published_seed": selected.published_seed,
            "case_count": selected.case_count,
            "reference_pids": report["reference_pids"],
            "distinct_reference_pids": report["distinct_reference_pids"],
            "actual_reference_workers": report["actual_reference_workers"],
            "reference_mismatch_count": report["reference_mismatch_count"],
            "complete_reference_worker_failures": report[
                "complete_reference_worker_failures"
            ],
            "archive_publication": archive_publication,
            "receipt_publication": receipt_publication,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "holdout": "NOT ACCESSED",
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {key: 0 for key in (
        "blocked_reads", "blocked_writes", "blocked_imports",
        "blocked_workers", "blocked_threads", "blocked_clocks",
        "blocked_gc_collections",
    )}
    installed: list[tuple[Any, str, Any]] = []

    def deny(key: str, message: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[key] += 1
            raise SourceOnlyError(message)
        return blocked

    def install(owner: Any, name: str, replacement: Any) -> None:
        original = getattr(owner, name, None)
        if original is not None:
            installed.append((owner, name, original))
            setattr(owner, name, replacement)

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"),
            (os, "read"), (os, "stat"), (os, "lstat"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
            (Path, "stat"),
        ):
            install(owner, name, deny(
                "blocked_reads", "synthetic baseline controls cannot read files",
            ))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"),
            (os, "rename"), (os, "replace"), (os, "mkdir"),
            (os, "rmdir"), (os, "fsync"), (os, "link"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "unlink"), (Path, "mkdir"), (Path, "rename"),
            (Path, "replace"),
        ):
            install(owner, name, deny(
                "blocked_writes", "synthetic baseline controls cannot write files",
            ))
        install(importlib, "import_module", deny(
            "blocked_imports", "synthetic baseline controls cannot import modules",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "synthetic baseline controls cannot import modules",
        ))
        for owner, name in ((subprocess, "Popen"), (subprocess, "run"),
                            (subprocess, "call"), (os, "system")):
            install(owner, name, deny(
                "blocked_workers", "synthetic baseline controls cannot run workers",
            ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "synthetic baseline controls cannot start threads",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "process_time_ns", "thread_time", "thread_time_ns",
        ):
            install(time, name, deny(
                "blocked_clocks", "synthetic baseline controls cannot sample time",
            ))
        install(gc, "collect", deny(
            "blocked_gc_collections",
            "synthetic baseline controls cannot collect garbage",
        ))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_outcome(selected: CategorySpec, index: int) -> dict[str, Any]:
    warnings = [] if index % 7 else [{
        "category": "FutureWarning", "message": "synthetic frozen warning",
    }]
    raised = index % 5 == 0
    if selected.name == "public":
        base = {"callbacks": [], "warnings": warnings}
    elif selected.name == "scanner":
        base = {
            "callbacks": [], "warnings": warnings,
            "combined_pattern": None, "lexicon": None,
        }
    else:
        base = {
            "stage": "expand", "match_before": None,
            "source_after": None, "mutation": None,
            "warnings": warnings,
        }
    if raised:
        return {
            **base, "status": "raise",
            "exception": {"type": "ValueError", "args": ["synthetic"]},
        }
    return {**base, "status": "return", "value": index}


def synthetic_category(
    selected: CategorySpec,
) -> tuple[list[dict[str, Any]], tuple[str, ...], list[dict[str, Any]]]:
    groups = tuple(
        "synthetic-group-" + format(index, "03d")
        for index in range(selected.group_count)
    )
    matrix: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for group_index, group in enumerate(groups):
        for variant in range(selected.cases_per_group):
            index = len(matrix)
            stimulus: dict[str, Any] = {
                "case": "synthetic." + selected.name + "." + format(index, "04d"),
            }
            if selected.name == "public":
                stimulus["operation"] = group
                stimulus["domain"] = (
                    "text" if variant < selected.cases_per_group // 2 else "bytes"
                )
            else:
                stimulus["family"] = group
            matrix.append(stimulus)
            observation: dict[str, Any] = {
                "case": stimulus["case"],
                "outcome": synthetic_outcome(selected, group_index + variant),
            }
            if selected.name != "public":
                observation["family"] = group
            records.append(observation)
    return matrix, groups, records


class SyntheticFilesystem:
    """Entirely in-memory descriptor adversary for genuine publication logic."""

    def __init__(
        self, *, faults: Mapping[str, Any] | None = None,
        write_returns: list[Any] | None = None,
        reuse_descriptors: bool = True,
    ) -> None:
        self.faults = dict(faults or {})
        self.write_returns = list(write_returns or [])
        self.reuse_descriptors = reuse_descriptors
        self.files: dict[str, dict[str, Any]] = {}
        self.handles: dict[int, dict[str, Any]] = {}
        self.released: list[int] = []
        self.next_fd = 11
        self.next_inode = 100
        self.dir_inodes = {
            "": 7, "oracle": 8, "oracle/cpython-3.14.6": 9,
            APPROVED_DIRECTORY: 10,
        }
        self.calls: list[str] = []

    def _fault(self, operation: str) -> None:
        item = self.faults.get(operation)
        if isinstance(item, BaseException):
            raise item
        if type(item) is list and item:
            current = item.pop(0)
            if isinstance(current, BaseException):
                raise current

    def _descriptor(self, handle: dict[str, Any]) -> int:
        if self.reuse_descriptors and self.released:
            descriptor = self.released.pop(0)
        else:
            descriptor = self.next_fd
            self.next_fd += 1
        self.handles[descriptor] = handle
        return descriptor

    def _join(self, basename: str, directory: int) -> str:
        require(directory in self.handles,
                "a synthetic directory descriptor was closed")
        owner = self.handles[directory]
        require(owner["kind"] == "directory",
                "a synthetic operation escaped its retained directory")
        return basename if not owner["path"] else owner["path"] + "/" + basename

    def open(self, name: str, flags: int, mode: int = 0o777,
             *, dir_fd: int | None = None) -> int:
        del mode
        self.calls.append("open")
        if dir_fd is None:
            require(name == str(ROOT), "the synthetic root was substituted")
            self._fault("open-root")
            return self._descriptor({"kind": "directory", "path": ""})
        path = self._join(name, dir_fd)
        if flags & getattr(os, "O_DIRECTORY", 0):
            self._fault("open-directory")
            if path not in self.dir_inodes:
                raise FileNotFoundError(path)
            return self._descriptor({"kind": "directory", "path": path})
        if flags & os.O_CREAT:
            self._fault("open-writer")
            require(flags & os.O_EXCL,
                    "synthetic publication lost its exclusive writer")
            require(flags & getattr(os, "O_NOFOLLOW", 0),
                    "synthetic publication lost its no-follow writer")
            if path in self.files:
                raise FileExistsError(path)
            inode = self.next_inode
            self.next_inode += 1
            entry = {"inode": inode, "data": bytearray(), "links": 1}
            self.files[path] = entry
            return self._descriptor({
                "kind": "writer", "path": path,
                "entry": entry, "position": 0,
            })
        self._fault("open-reader")
        if path not in self.files:
            raise FileNotFoundError(path)
        return self._descriptor({
            "kind": "reader", "path": path,
            "entry": self.files[path], "position": 0,
        })

    def fstat(self, descriptor: int) -> Any:
        self.calls.append("fstat")
        self._fault("fstat")
        handle = self.handles.get(descriptor)
        if handle is None:
            raise OSError("synthetic descriptor is closed")
        if handle["kind"] == "directory":
            return types.SimpleNamespace(
                st_mode=stat.S_IFDIR | 0o755, st_dev=3,
                st_ino=self.dir_inodes[handle["path"]], st_size=0,
            )
        entry = handle["entry"]
        return types.SimpleNamespace(
            st_mode=stat.S_IFREG | 0o644, st_dev=3,
            st_ino=entry["inode"], st_size=len(entry["data"]),
        )

    def stat(self, name: str, *, dir_fd: int,
             follow_symlinks: bool = True) -> Any:
        self.calls.append("stat")
        require(follow_symlinks is False,
                "synthetic publication followed an evidence symlink")
        self._fault("stat")
        path = self._join(name, dir_fd)
        entry = self.files.get(path)
        if entry is None:
            raise FileNotFoundError(path)
        return types.SimpleNamespace(
            st_mode=stat.S_IFREG | 0o644, st_dev=3,
            st_ino=entry["inode"], st_size=len(entry["data"]),
        )

    def write(self, descriptor: int, payload: bytes) -> Any:
        self.calls.append("write")
        self._fault("write")
        handle = self.handles.get(descriptor)
        require(handle is not None and handle["kind"] == "writer",
                "synthetic publication used a closed or foreign writer")
        result = self.write_returns.pop(0) if self.write_returns else len(payload)
        if isinstance(result, BaseException):
            raise result
        if type(result) is int and 0 < result <= len(payload):
            handle["entry"]["data"].extend(payload[:result])
        return result

    def read(self, descriptor: int, maximum: int) -> bytes:
        self.calls.append("read")
        self._fault("read")
        handle = self.handles.get(descriptor)
        require(handle is not None and handle["kind"] == "reader",
                "synthetic readback used a closed or foreign reader")
        require(type(maximum) is int and maximum > 0,
                "synthetic readback lost its exact positive bound")
        start = handle["position"]
        result = bytes(handle["entry"]["data"][start:start + maximum])
        handle["position"] += len(result)
        return result

    def fsync(self, descriptor: int) -> None:
        self.calls.append("fsync")
        handle = self.handles.get(descriptor)
        require(handle is not None,
                "synthetic publication synced a closed descriptor")
        stage = "fsync-directory" if handle["kind"] == "directory" else "fsync-file"
        self._fault(stage)

    def link(self, source: str, destination: str, *, src_dir_fd: int,
             dst_dir_fd: int, follow_symlinks: bool = True) -> None:
        self.calls.append("link")
        require(follow_symlinks is False,
                "synthetic publication followed a link")
        self._fault("link")
        first = self._join(source, src_dir_fd)
        second = self._join(destination, dst_dir_fd)
        if first not in self.files:
            raise FileNotFoundError(first)
        if second in self.files:
            raise FileExistsError(second)
        self.files[second] = self.files[first]
        self.files[first]["links"] += 1

    def unlink(self, name: str, *, dir_fd: int) -> None:
        self.calls.append("unlink")
        self._fault("unlink")
        path = self._join(name, dir_fd)
        if path not in self.files:
            raise FileNotFoundError(path)
        entry = self.files.pop(path)
        entry["links"] -= 1

    def close(self, descriptor: int) -> None:
        self.calls.append("close")
        handle = self.handles.pop(descriptor, None)
        if handle is None:
            raise OSError("synthetic descriptor was closed twice")
        self.released.append(descriptor)
        self.released.sort()
        self._fault("close-" + handle["kind"])


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []
    category_checks: dict[str, int] = {name: 0 for name in CATEGORIES}

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and bool(name),
                "every synthetic positive control needs a complete label")
        require(condition, "synthetic positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any],
               errors: tuple[type[BaseException], ...] = (
                   BaselineError, TypeError, ValueError, OSError,
               )) -> None:
        try:
            action()
        except errors:
            rejected.append(name)
            return
        raise BaselineError("synthetic hostile control was accepted: " + name)

    with source_only_boundary() as effects:
        accept("canonical-single-newline", canonical({"b": 2, "a": 1})
               == b'{"a":1,"b":2}\n')
        accept("canonical-roundtrip", decode_canonical(
            canonical({"value": [1, "two", None]}), "synthetic", 1024,
        ) == {"value": [1, "two", None]})
        for index, poison in enumerate((
            b"", b"{}", b"{}\n\n", b'{"a":1,"a":2}\n',
            b'{"value":NaN}\n', b'{"value":Infinity}\n',
            b'{"value":-Infinity}\n', b"[]\n", b"null\n",
            b'{ "a": 1}\n', b'{"a":1} \n', b'{"a":1}\r\n',
            b'{"a":1}\ntrailing', b'{"a":1',
        )):
            reject("canonical-hostile-" + format(index, "02d"),
                   lambda poison=poison: decode_canonical(poison, "poison", 1024))
        for index, invalid in enumerate((
            None, True, False, 0, -1, 1.0, "", "0" * 64,
            "a" * 63, "a" * 65, "A" * 64,
            "z" * 64, "0123456789abcdef" * 3,
        )):
            reject("digest-hostile-" + format(index, "02d"),
                   lambda invalid=invalid: validate_digest(invalid, "poison"))
        for index, invalid in enumerate((
            None, True, False, 0, -1, "", ".", "..", "../x", "x/../y",
            "x//y", "/tmp/x", "x\\y", "x\x00y",
        )):
            reject("path-hostile-" + format(index, "02d"),
                   lambda invalid=invalid: safe_parts(invalid))
        for index, invalid in enumerate((
            None, True, False, 0, "", "-x", "x-", "x--y",
            "UPPER", "x/y", "../x", "x_y", "x.y", "x y",
            "é", "x\x00y", "a" * 49,
        )):
            reject("label-hostile-" + format(index, "02d"),
                   lambda invalid=invalid: validate_label(invalid))

        for name in ("public", "scanner", "buffer"):
            selected = category_spec(name)
            matrix, groups, records = synthetic_category(selected)
            matrix_hash = digest(matrix)
            records_hash = digest(records)
            accept(name + "/all-source-ordered-matrix-cases",
                   validate_matrix_rows(selected, matrix, groups, matrix_hash)
                   is matrix)
            accept(name + "/all-source-ordered-reference-observations",
                   validate_records_rows(selected, matrix, records, records_hash)
                   is records)
            accept(name + "/full-width-published-seed",
                   selected.published_seed.bit_length() > 48)
            accept(name + "/category-denominator",
                   len(matrix) == len(records) == selected.case_count)
            accept(name + "/approved-distinct-relative-paths",
                   len(set(approved_paths(name, "source-test-v1"))) == 2)
            stream = encode_stream(canonical(records[0]), name)
            accept(name + "/complete-reversible-process-stream",
                   decode_stream(stream, name) == canonical(records[0]))
            for suffix, operation in (
                ("omitted-stimulus", lambda: validate_matrix_rows(
                    selected, matrix[:-1], groups, matrix_hash,
                )),
                ("reordered-stimulus", lambda: validate_matrix_rows(
                    selected, list(reversed(matrix)), groups, matrix_hash,
                )),
                ("duplicate-stimulus", lambda: validate_matrix_rows(
                    selected, [matrix[0], *matrix[1:-1], matrix[0]],
                    groups, matrix_hash,
                )),
                ("foreign-matrix-digest", lambda: validate_matrix_rows(
                    selected, matrix, groups, selected.matrix_sha256,
                )),
                ("omitted-group", lambda: validate_matrix_rows(
                    selected, matrix, groups[:-1], matrix_hash,
                )),
                ("duplicate-group", lambda: validate_matrix_rows(
                    selected, matrix, (*groups[:-1], groups[0]), matrix_hash,
                )),
                ("omitted-reference-case", lambda: validate_records_rows(
                    selected, matrix, records[:-1], records_hash,
                )),
                ("reordered-reference-case", lambda: validate_records_rows(
                    selected, matrix, list(reversed(records)), records_hash,
                )),
                ("foreign-reference-digest", lambda: validate_records_rows(
                    selected, matrix, records, selected.baseline_sha256,
                )),
                ("invalid-reference-stream", lambda: decode_stream(
                    {**stream, "bytes": stream["bytes"] + 1}, name,
                )),
                ("forged-reference-stream", lambda: decode_stream(
                    {**stream, "sha256": selected.matrix_sha256}, name,
                )),
                ("incomplete-reference-stream", lambda: decode_stream(
                    {**stream, "complete": False}, name,
                )),
                ("unknown-reference-stream-field", lambda: decode_stream(
                    {**stream, "foreign": True}, name,
                )),
                ("foreign-reference-base64", lambda: decode_stream(
                    {**stream, "base64": "*not-valid*"}, name,
                )),
            ):
                reject(name + "/" + suffix, operation)
            for outcome_index, mutation in enumerate((
                lambda value: value.pop("warnings"),
                lambda value: value.__setitem__("warnings", None),
                lambda value: value.__setitem__("status", "missing"),
                lambda value: value.__setitem__("foreign", True),
            )):
                broken = copy.deepcopy(records[1]["outcome"])
                mutation(broken)
                reject(name + "/outcome-hostile-" + str(outcome_index),
                       lambda broken=broken: validate_outcome(selected, broken))
            category_checks[name] = len(matrix)

        original_format_exc = traceback.format_exc
        traceback.format_exc = lambda: "synthetic complete traceback\n"
        try:
            for index, name in enumerate(("public", "scanner", "buffer")):
                original_process = {
                    "role": "reference_a",
                    "category": name,
                    "candidate_family": None,
                    "pid": 7901 + index,
                    "returncode": 0,
                    "stdout": encode_stream(canonical({
                        "category": name,
                        "role": "reference_a",
                        "status": "OBSERVED",
                    }), name + " synthetic stdout"),
                    "stderr": encode_stream(
                        b"", name + " synthetic stderr",
                    ),
                }
                failure = worker_failure_evidence(
                    "reference_a",
                    BaselineError("synthetic post-return validation failure"),
                    original_process,
                )
                accept(
                    name + "/post-return-worker-process-preserved",
                    failure["genuine_process_started"] is True
                    and failure["genuine_process_pid"] == 7901 + index
                    and failure["complete_original_worker_evidence"]
                    == original_process
                    and failure["complete_original_worker_evidence"]
                    is not original_process
                    and decode_stream(
                        failure["complete_original_worker_evidence"]["stdout"],
                        name + " retained stdout",
                    ) == decode_stream(
                        original_process["stdout"], name + " original stdout",
                    )
                    and decode_stream(
                        failure["complete_original_worker_evidence"]["stderr"],
                        name + " retained stderr",
                    ) == b"",
                )
                collision_process = {
                    **original_process,
                    "role": "reference_b",
                }
                collision = worker_failure_evidence(
                    "reference_b",
                    BaselineError("synthetic duplicate reference PID"),
                    collision_process,
                )
                accept(
                    name + "/duplicate-pid-process-preserved",
                    collision["role"] == "reference_b"
                    and collision["genuine_process_started"] is True
                    and collision["genuine_process_pid"] == 7901 + index
                    and collision["complete_original_worker_evidence"]
                    == collision_process,
                )
                start_failure = worker_failure_evidence(
                    "reference_a",
                    BaselineError("synthetic reference spawn failure"),
                    None,
                )
                accept(
                    name + "/unstarted-reference-never-fabricated",
                    start_failure["genuine_process_started"] is False
                    and start_failure["genuine_process_pid"] is None
                    and start_failure["complete_original_worker_evidence"]
                    is None,
                )
        finally:
            traceback.format_exc = original_format_exc

        payload = canonical({"schema": SCHEMA, "synthetic": True,
                             "items": list(range(64))})
        compressed = deterministic_archive(payload)
        accept("gzip-complete-exact-round-trip",
               bounded_inflate(compressed, len(payload)) == payload)
        accept("gzip-reproducible-header-and-bytes",
               deterministic_archive(payload) == compressed
               and compressed[4:8] == b"\x00\x00\x00\x00")
        for index, poison in enumerate((
            compressed[:-1], compressed[:8], compressed + b"hidden",
            compressed + compressed, compressed + gzip.compress(
                b"second", mtime=0,
            ), b"not-gzip-data", b"\x1f\x8b\x08" + b"\x00" * 8,
        )):
            reject("gzip-hostile-" + format(index, "02d"),
                   lambda poison=poison: bounded_inflate(poison, MAX_REPORT_BYTES))
        reject("gzip-decompression-bomb", lambda: bounded_inflate(
            gzip.compress(b"x" * 4096, mtime=0), 31,
        ))
        reject("gzip-zero-limit", lambda: bounded_inflate(compressed, 0))
        reject("gzip-boolean-limit", lambda: bounded_inflate(compressed, True))

        for reuse in (False, True):
            fake = SyntheticFilesystem(reuse_descriptors=reuse)
            with preflight_fresh_outputs("public", "synthetic-v1", fake) as prep:
                proof = publish_payload(prep, compressed, "archive", fake)
                receipt_raw = canonical({"archive": proof["sha256"]})
                receipt_proof = publish_payload(
                    prep, receipt_raw, "receipt", fake,
                )
                accept("publication-complete-" + str(int(reuse)),
                       proof["status"] == "PASS"
                       and receipt_proof["status"] == "PASS"
                       and proof["complete_readback_verified"]
                       and receipt_proof["complete_readback_verified"])
                events = proof["descriptor_lifetime_events"]
                accept("publication-descriptor-lifetime-" + str(int(reuse)),
                       [item["event"] for item in events] == [
                           "writer-open", "writer-close",
                           "reader-open", "reader-close",
                       ] and all(item["completed"] for item in events))
                accept("publication-descriptor-alias-policy-" + str(int(reuse)),
                       (events[0]["fd"] == events[2]["fd"]) is reuse)
                accept("publication-complete-write-ledger-" + str(int(reuse)),
                       proof["actual_bytes_written"] == len(compressed)
                       and all(item["completed"]
                               for item in proof["write_attempts"]))
                reject("publication-final-no-clobber-" + str(int(reuse)),
                       lambda: preflight_fresh_outputs(
                           "public", "synthetic-v1", fake,
                       ).__enter__())

        for index, poison in enumerate((0, -1, True, False, 1.0, len(compressed) + 1)):
            fake = SyntheticFilesystem(write_returns=[poison])
            with preflight_fresh_outputs(
                "public", "write-poison-" + str(index), fake,
            ) as prep:
                def bad_write() -> None:
                    try:
                        publish_payload(prep, compressed, "archive", fake)
                    except PublicationFailure as error:
                        ledger = error.ledger
                        require(
                            ledger["status"] == "FAIL"
                            and len(ledger["write_attempts"]) == 1
                            and ledger["write_attempts"][0]["returned_bytes"]
                            == poison
                            and ledger["write_attempts"][0]["completed"] is False
                            and ledger["actual_write_calls"] == 0
                            and ledger["actual_bytes_written"] == 0,
                            "a poisoned actual baseline write was fabricated",
                        )
                        raise
                reject("publication-poisoned-write-" + str(index), bad_write,
                       (PublicationFailure,))

        for index, stage in enumerate((
            "open-writer", "fsync-file", "link", "open-reader", "read",
            "unlink", "fsync-directory",
        )):
            fake = SyntheticFilesystem(faults={stage: OSError("synthetic " + stage)})
            with preflight_fresh_outputs(
                "buffer", "fault-" + str(index), fake,
            ) as prep:
                def bad_stage() -> None:
                    try:
                        publish_payload(prep, compressed, "archive", fake)
                    except PublicationFailure as error:
                        require(error.ledger.get("status") == "FAIL"
                                and type(error.ledger.get("failure")) is dict,
                                "a genuine partial publication failure was hidden")
                        if stage == "fsync-file":
                            require(error.ledger["file_fsync_attempted"] is True
                                    and error.ledger["file_fsync_completed"] is False,
                                    "a failed file fsync was represented as complete")
                        if stage == "link":
                            require(error.ledger[
                                "atomic_no_overwrite_link_attempted"
                            ] is True and error.ledger[
                                "atomic_no_overwrite_link"
                            ] is False,
                                "a failed no-clobber link was fabricated")
                        raise
                reject("publication-stage-fault-" + str(index), bad_stage,
                       (PublicationFailure,))

        fake = SyntheticFilesystem(write_returns=[1, 2, 3])
        with preflight_fresh_outputs("scanner", "short-writes-v1", fake) as prep:
            proof = publish_payload(prep, compressed, "archive", fake)
            accept("publication-complete-partial-write-loop",
                   proof["status"] == "PASS"
                   and proof["actual_write_calls"] >= 4
                   and proof["actual_bytes_written"] == len(compressed))

        for index, operation in enumerate((
            lambda: builtins.open("synthetic-read"),
            lambda: io.open("synthetic-read"),
            lambda: os.open("synthetic-read", os.O_RDONLY),
            lambda: os.read(0, 1),
            lambda: os.stat("synthetic-read"),
            lambda: Path("synthetic-read").read_bytes(),
            lambda: Path("synthetic-read").read_text(),
            lambda: os.write(1, b"synthetic"),
            lambda: os.unlink("synthetic-write"),
            lambda: os.replace("synthetic-old", "synthetic-new"),
            lambda: os.fsync(1),
            lambda: importlib.import_module(CONTRACT_MODULE),
            lambda: builtins.__import__("candidates"),
            lambda: subprocess.Popen(["synthetic"]),
            lambda: subprocess.run(["synthetic"]),
            lambda: threading.Thread().start(),
            lambda: time.perf_counter_ns(),
            lambda: time.monotonic_ns(),
            lambda: time.time_ns(),
            lambda: gc.collect(),
        )):
            reject("source-only-external-effect-" + format(index, "02d"),
                   operation, (SourceOnlyError,))

    require(
        len(set(accepted)) == len(accepted)
        and len(set(rejected)) == len(rejected),
        "every synthetic hostile control requires a unique label",
    )
    require(len(accepted) + len(rejected) > 100,
            "run more than 100 independently guarded synthetic controls")
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules)
        and CONTRACT_MODULE not in sys.modules,
        "the synthetic self-test imported an actual project or candidate",
    )
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "frozen_contract_source_sha256": CONTRACT_SHA256,
        "frozen_original_v5_sha256": V5_SHA256,
        "frozen_previous_v2_sha256": V2_SHA256,
        "checks": len(accepted) + len(rejected),
        "accepted_checks": len(accepted),
        "rejected_hostile_checks": len(rejected),
        "accepted_control_labels": accepted,
        "rejected_control_labels": rejected,
        "synthetic_case_denominators": category_checks,
        "synthetic_filesystem_only": True,
        "source_only_boundary": effects,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_project_module_imports": 0,
        "actual_workspace_files_read": 0,
        "actual_workspace_files_written": 0,
        "actual_evidence_files_created": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record exactly one pure, two-CPython frozen V3 baseline",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--record", action="store_true")
    parser.add_argument("--category", choices=tuple(CATEGORIES))
    parser.add_argument("--label")
    parser.add_argument("--recorder-source-sha256")
    parser.add_argument("--contract-source-sha256")
    parser.add_argument("--matrix-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(
            options.record is False
            and all(getattr(options, name) is None for name in (
                "category", "label", "recorder_source_sha256",
                "contract_source_sha256", "matrix_sha256",
            )),
            "a synthetic baseline control cannot select or execute an actual run",
        )
        result = source_self_test()
    else:
        require(options.record is True and options.category is not None
                and options.label is not None
                and options.recorder_source_sha256 is not None
                and options.contract_source_sha256 is not None
                and options.matrix_sha256 is not None,
                "pin exactly one category, label, recorder, V3, and matrix")
        result = record_baseline(
            options.category, options.label,
            options.recorder_source_sha256,
            options.contract_source_sha256,
            options.matrix_sha256,
        )
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        evidence: dict[str, Any] = {
            "schema": SCHEMA + "-complete-process-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error": str(error),
            "complete_traceback": traceback.format_exc(),
            "complete_publication_failure": (
                error.ledger if isinstance(error, PublicationFailure) else None
            ),
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "holdout": "NOT ACCESSED",
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        sys.stderr.buffer.write(canonical(evidence))
        sys.stderr.buffer.flush()
        raise SystemExit(1) from error
