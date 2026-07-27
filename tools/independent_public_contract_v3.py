#!/usr/bin/env python3
"""Run one frozen public regex category for one independently owned engine.

``--self-test`` is synthetic and cannot read files, import an engine, start a
worker, take a clock sample, or write evidence.  A real observation requires
both ``--candidate {rust,c,zig}`` and exactly one ``--category
{public,scanner,buffer}``.  There is deliberately no combined-category mode.

The original, independently frozen case matrices and outcome observers are
reused unchanged.  Two isolated, unmodified CPython references must reproduce
the exact previously frozen category baseline before one separately isolated
candidate is allowed to run under the corrected original V5 matcher-ownership guard.
Every case, warning, callback, exception, reference, and mismatch is retained.
This is a correctness oracle.  It never calls a performance or timing entry
point and does not create an evidence file.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
from dataclasses import dataclass
import gc
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


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/independent_public_contract_v3.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_STDLIB_RE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py"
)
SCHEMA = "rebar-independent-public-contract-v3"
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_MODULE = "tools.independent_original_cpython_suite_v5"
V5_SHA256 = "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
PREVIOUS_V2_RELATIVE = "tools/independent_public_contract_v2.py"
PREVIOUS_V2_MODULE = "tools.independent_public_contract_v2"
PREVIOUS_V2_SHA256 = "a0ae9621e06b760477a167705cc6e521cc7e9df4d44d126e39c614df89bd3e68"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"


class ContractError(Exception):
    """A frozen case, native owner, isolation boundary, or outcome changed."""


class SourceOnlyError(ContractError):
    """A synthetic control attempted an actual external observation."""


class WorkerFailure(ContractError):
    """A real isolated worker failed; retain both complete process streams."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


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
    adapter_sha256: str
    engine_sha256: str
    bridge_sha256: str
    owned_sources: tuple[tuple[str, str], ...]


CATEGORY_SPECS = types.MappingProxyType({
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

FAMILY_SPECS = types.MappingProxyType({
    "rust": FamilySpec(
        "rust", "candidates.rust_candidate", "candidates/rust_candidate.py",
        "candidates/_rust_engine.so", "candidates._rust_bridge",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX, False,
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
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
    ),
})

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ContractError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str and len(value) == 64 and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value)
    )


def checked_digest(value: Any, label: str) -> str:
    require(valid_digest(value), "an exact lowercase SHA-256 is required: " + label)
    return value


def category_spec(name: Any) -> CategorySpec:
    require(type(name) is str and name in CATEGORY_SPECS,
            "select exactly one frozen public, scanner, or buffer category")
    spec = CATEGORY_SPECS[name]
    require(
        isinstance(spec, CategorySpec) and spec.name == name
        and spec.module.startswith("tools.")
        and spec.source_relative.startswith("tools/")
        and spec.source_relative.endswith(".py")
        and valid_digest(spec.source_sha256)
        and valid_digest(spec.matrix_sha256)
        and valid_digest(spec.baseline_sha256)
        and type(spec.published_seed) is int and spec.published_seed > 0
        and type(spec.case_count) is int
        and spec.case_count == spec.group_count * spec.cases_per_group
        and spec.case_count in (864, 1024, 768),
        "an exact independently frozen public category was substituted",
    )
    return spec


def family_spec(name: Any) -> FamilySpec:
    require(type(name) is str and name in FAMILY_SPECS,
            "select exactly one independently owned Rust, C, or Zig family")
    spec = FAMILY_SPECS[name]
    require(
        isinstance(spec, FamilySpec)
        and spec.name == name
        and spec.adapter_module.startswith("candidates.")
        and spec.bridge_module.startswith("candidates.")
        and spec.adapter_module != spec.bridge_module
        and spec.adapter_relative.startswith("candidates/")
        and spec.engine_relative.startswith("candidates/")
        and spec.bridge_relative.startswith("candidates/")
        and spec.bridge_relative.endswith(EXTENSION_SUFFIX)
        and (spec.engine_relative == spec.bridge_relative) == (name == "c")
        and spec.owned_ctypes == (name == "zig")
        and type(spec.owned_source_relatives) is tuple
        and bool(spec.owned_source_relatives)
        and len(set(spec.owned_source_relatives))
        == len(spec.owned_source_relatives)
        and spec.adapter_relative in spec.owned_source_relatives
        and all(
            type(path) is str and path.startswith("candidates/")
            for path in spec.owned_source_relatives
        ),
        "the independently owned native family source closure was substituted",
    )
    return spec


def parse_owned_source(value: Any) -> tuple[str, str]:
    require(type(value) is str and value.count("=") == 1,
            "pin each exact owned source as relative/path=lowercase-sha256")
    relative, value_hash = value.split("=", 1)
    parts = owned_relative(relative)
    require(parts[0] == "candidates",
            "an owned candidate source escaped its approved candidates root")
    return relative, checked_digest(value_hash, "owned source " + relative)


def resolve_owner_pins(
    family: FamilySpec,
    adapter_sha256: Any,
    engine_sha256: Any,
    bridge_sha256: Any,
    owned_sources: Any,
) -> OwnerPins:
    require(type(owned_sources) in (list, tuple),
            "all exact independently owned source fingerprints are mandatory")
    items: dict[str, str] = {}
    for item in owned_sources:
        path, source_sha256 = parse_owned_source(item)
        require(path not in items,
                "a duplicate owned source fingerprint was provided: " + path)
        items[path] = source_sha256
    require(
        set(items) == set(family.owned_source_relatives)
        and len(items) == len(family.owned_source_relatives),
        "the complete owned source closure is missing, foreign, or substituted",
    )
    adapter = checked_digest(adapter_sha256, "independent native Python adapter")
    engine = checked_digest(engine_sha256, "independent native regex engine")
    bridge = checked_digest(bridge_sha256, "independent native Python bridge")
    require(items[family.adapter_relative] == adapter,
            "the selected Python adapter does not match its owned source closure")
    require((engine == bridge) == (family.name == "c"),
            "only the C family may use its exact shared native engine and bridge")
    return OwnerPins(
        adapter, engine, bridge,
        tuple((path, items[path]) for path in family.owned_source_relatives),
    )


def native_pins(family: FamilySpec, pins: OwnerPins) -> dict[str, str]:
    require(isinstance(pins, OwnerPins),
            "require exact explicit independently supplied candidate pins")
    require(tuple(path for path, _ in pins.owned_sources)
            == family.owned_source_relatives,
            "the complete source closure changed order or family")
    require(all(valid_digest(value) for _, value in pins.owned_sources),
            "every independently owned source needs an exact SHA-256")
    require(all(valid_digest(value) for value in (
        pins.adapter_sha256, pins.engine_sha256, pins.bridge_sha256,
    )), "every independent native component needs an exact SHA-256")
    require(dict(pins.owned_sources).get(family.adapter_relative)
            == pins.adapter_sha256,
            "the selected adapter fingerprint escaped its source closure")
    require((pins.engine_sha256 == pins.bridge_sha256)
            == (family.name == "c"),
            "only the C engine and native bridge may genuinely alias")
    return {
        "source": pins.adapter_sha256,
        "native_engine": pins.engine_sha256,
        "native_bridge": pins.bridge_sha256,
    }


def verify_runtime(*, candidate_loaded: bool = False) -> None:
    expected = str(ROOT / SOURCE_RELATIVE)
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path) and sys.path[0] == str(ROOT)
        and os.path.abspath(__file__) == expected
        and os.path.realpath(__file__) == expected
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
        "use only the exact isolated CPython 3.14.6 and frozen category controller",
    )
    if not candidate_loaded:
        require(
            not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate escaped into an original-only public controller",
        )


def owned_relative(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\\" not in relative and "\x00" not in relative,
            "an exact approved relative source is mandatory")
    parts = tuple(relative.split("/"))
    require(parts and all(part not in ("", ".", "..") for part in parts)
            and "/".join(parts) == relative,
            "an immutable source path escaped its frozen project root")
    return parts


def read_owned(relative: str, expected: str, maximum: int) -> dict[str, Any]:
    parts = owned_relative(relative)
    checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "bound every exact immutable source or native owner")
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    regular_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    opened: list[int] = []
    try:
        opened.append(os.open(str(ROOT), directory_flags))
        for part in parts[:-1]:
            opened.append(os.open(part, directory_flags, dir_fd=opened[-1]))
        descriptor = os.open(parts[-1], regular_flags, dir_fd=opened[-1])
        opened.append(descriptor)
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and 0 < before.st_size <= maximum,
                "the exact immutable regular file is missing: " + relative)
        remaining = before.st_size
        hasher = hashlib.sha256()
        while remaining:
            piece = os.read(descriptor, min(remaining, 1_048_576))
            require(type(piece) is bytes and bool(piece),
                    "an exact immutable owner was truncated: " + relative)
            hasher.update(piece)
            remaining -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "an exact immutable owner grew: " + relative)
        after = os.fstat(descriptor)
        require(
            (after.st_dev, after.st_ino, after.st_size)
            == (before.st_dev, before.st_ino, before.st_size),
            "an immutable owner changed during authentication: " + relative,
        )
        require(hasher.hexdigest() == expected,
                "the exact frozen owner hash changed: " + relative)
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


def authenticate_source_module(
    module_name: str, relative: str, source_sha256: str,
) -> tuple[types.ModuleType, dict[str, Any]]:
    owner = read_owned(relative, source_sha256, MAX_SOURCE_BYTES)
    module = importlib.import_module(module_name)
    expected = str(ROOT / relative)
    spec = getattr(module, "__spec__", None)
    loader = getattr(spec, "loader", None)
    require(
        type(module) is types.ModuleType
        and module.__name__ == module_name
        and os.path.abspath(getattr(module, "__file__", "")) == expected
        and os.path.realpath(getattr(module, "__file__", "")) == expected
        and spec is not None and getattr(spec, "name", None) == module_name
        and getattr(spec, "origin", None) == expected
        and isinstance(loader, importlib.machinery.SourceFileLoader)
        and getattr(loader, "name", None) == module_name
        and getattr(loader, "path", None) == expected,
        "the exact frozen source module or loader was substituted: " + module_name,
    )
    require(read_owned(relative, source_sha256, MAX_SOURCE_BYTES) == owner,
            "the frozen source changed during import: " + relative)
    return module, owner


def validate_matrix_document(
    spec: CategorySpec,
    matrix: Any,
    expected_sha256: str,
    groups: tuple[str, ...],
) -> list[dict[str, Any]]:
    checked_digest(expected_sha256, spec.name + " case matrix")
    require(
        type(matrix) is list and len(matrix) == spec.case_count
        and type(groups) is tuple and len(groups) == spec.group_count
        and all(type(name) is str and bool(name) for name in groups)
        and len(set(groups)) == len(groups)
        and digest(matrix) == expected_sha256,
        "an exact frozen " + spec.name + " case denominator changed",
    )
    seen: set[str] = set()
    counts = {name: 0 for name in groups}
    domains = {"text": 0, "bytes": 0}
    for row in matrix:
        require(type(row) is dict and type(row.get("case")) is str
                and row["case"] not in seen,
                "a complete source-ordered " + spec.name + " case was replaced")
        seen.add(row["case"])
        key = row.get("operation") if spec.name == "public" else row.get("family")
        require(type(key) is str and key in counts,
                "an exact " + spec.name + " case group was hidden")
        counts[key] += 1
        if spec.name == "public":
            domain = row.get("domain")
            require(domain in domains,
                    "the original public text-or-bytes domain was replaced")
            domains[domain] += 1
    require(all(value == spec.cases_per_group for value in counts.values()),
            "an exact " + spec.name + " group denominator changed")
    if spec.name == "public":
        require(domains == {"text": 432, "bytes": 432},
                "the frozen equally weighted public text and bytes were changed")
    return matrix


def load_prerequisites(
    spec: CategorySpec,
) -> tuple[types.ModuleType, types.ModuleType, types.ModuleType,
           list[dict[str, Any]], tuple[str, ...], dict[str, dict[str, Any]]]:
    verify_runtime()
    v5, v5_owner = authenticate_source_module(
        V5_MODULE, V5_RELATIVE, V5_SHA256,
    )
    previous, previous_owner = authenticate_source_module(
        PREVIOUS_V2_MODULE, PREVIOUS_V2_RELATIVE, PREVIOUS_V2_SHA256,
    )
    module, category_owner = authenticate_source_module(
        spec.module, spec.source_relative, spec.source_sha256,
    )
    require(
        getattr(v5, "SOURCE_RELATIVE", None) == V5_RELATIVE
        and getattr(v5, "EXTENSION_SUFFIX", None) == EXTENSION_SUFFIX
        and getattr(v5, "current_source_sha256")() == V5_SHA256
        and getattr(previous, "SOURCE_RELATIVE", None)
        == PREVIOUS_V2_RELATIVE
        and getattr(previous, "SCHEMA", None)
        == "rebar-independent-public-contract-v2"
        and getattr(module, "SOURCE_RELATIVE", None) == spec.source_relative
        and getattr(module, "MATRIX_SHA256", None) == spec.matrix_sha256
        and getattr(module, "PUBLISHED_SEED", None) == spec.published_seed,
        "the exact immutable public V2, corrected V5 or category was changed",
    )
    for name in CATEGORY_SPECS:
        ours = category_spec(name)
        legacy = previous.category_spec(name)
        require(
            legacy.name == ours.name
            and legacy.module == ours.module
            and legacy.source_relative == ours.source_relative
            and legacy.source_sha256 == ours.source_sha256
            and legacy.matrix_sha256 == ours.matrix_sha256
            and legacy.baseline_sha256 == ours.baseline_sha256
            and legacy.published_seed == ours.published_seed
            and legacy.case_count == ours.case_count
            and legacy.group_count == ours.group_count
            and legacy.cases_per_group == ours.cases_per_group,
            "the literal original public category was weakened: " + name,
        )
    if spec.name == "public":
        groups = tuple(module.OPERATIONS)
        matrix = module.build_public_matrix()
        require(module.validate_public_matrix(matrix) == spec.matrix_sha256,
                "the exact 864 original public cases were substituted")
    else:
        require(getattr(module, "BASELINE_SHA256", None) == spec.baseline_sha256
                and getattr(module, "CASE_COUNT", None) == spec.case_count,
                "the frozen category baseline or denominator changed")
        groups = tuple(module.FAMILIES)
        matrix = module.build_matrix()
        require(module.validate_matrix(matrix) == spec.matrix_sha256,
                "the exact independently frozen category matrix changed")
    validate_matrix_document(spec, matrix, spec.matrix_sha256, groups)
    for name in FAMILY_SPECS:
        ours = family_spec(name)
        original = v5.family_spec(name)
        require(
            original.name == ours.name
            and original.adapter_module == ours.adapter_module
            and original.adapter_relative == ours.adapter_relative
            and original.engine_relative == ours.engine_relative
            and original.bridge_module == ours.bridge_module
            and original.bridge_relative == ours.bridge_relative
            and original.owned_ctypes == ours.owned_ctypes,
            "the corrected V5 independently owned family changed: " + name,
        )
    return v5, previous, module, matrix, groups, {
        "original_v5": v5_owner,
        "previous_v2": previous_owner,
        "category": category_owner,
    }


def authenticate_family_closure(
    v5: types.ModuleType,
    family: FamilySpec,
    pins: OwnerPins,
) -> dict[str, dict[str, Any]]:
    actual_pins = native_pins(family, pins)
    sources = dict(pins.owned_sources)
    require(
        set(sources) == set(family.owned_source_relatives)
        and sources.get(family.adapter_relative) == pins.adapter_sha256,
        "the exact caller-pinned complete owned source set was substituted",
    )
    result: dict[str, dict[str, Any]] = {}
    for path in family.owned_source_relatives:
        result[path] = read_owned(path, sources[path], MAX_SOURCE_BYTES)
    binaries = (
        (family.engine_relative, pins.engine_sha256),
        (family.bridge_relative, pins.bridge_sha256),
    )
    for path, expected in binaries:
        if path in result:
            require(result[path]["sha256"] == expected,
                    "an independently owned source and binary hash collided")
        else:
            result[path] = read_owned(path, expected, MAX_BINARY_BYTES)
    expected_paths = set(family.owned_source_relatives) | {
        family.engine_relative, family.bridge_relative,
    }
    require(set(result) == expected_paths,
            "the complete source and native closure changed family")
    original = v5.family_spec(family.name)
    require(v5.validate_pins(actual_pins, original) == actual_pins,
            "the corrected V5 exact native adapter ownership changed")
    return result


def validate_outcome(spec: CategorySpec, outcome: Any) -> None:
    require(type(outcome) is dict and outcome.get("status") in ("return", "raise"),
            "a complete " + spec.name + " outcome was concealed")
    if spec.name == "public":
        expected = {"status", "callbacks", "warnings",
                    "value" if outcome["status"] == "return" else "exception"}
        require(set(outcome) == expected
                and type(outcome.get("callbacks")) is list,
                "a public result, replacement callback, or exception was hidden")
    elif spec.name == "scanner":
        expected = {
            "status", "callbacks", "warnings", "combined_pattern", "lexicon",
            "value" if outcome["status"] == "return" else "exception",
        }
        require(set(outcome) == expected
                and type(outcome.get("callbacks")) is list,
                "a scanner result, callback, or lexicon mutation was hidden")
    else:
        expected = {
            "status", "stage", "match_before", "source_after", "mutation",
            "warnings", "value" if outcome["status"] == "return" else "exception",
        }
        require(set(outcome) == expected and type(outcome.get("stage")) is str,
                "a buffer stage, exporter error, or source mutation was hidden")
    require(type(outcome.get("warnings")) is list,
            "a genuine ordered Python warning was concealed")
    if outcome["status"] == "raise":
        require(type(outcome.get("exception")) is dict,
                "a genuine public exception was concealed")


def validate_records(
    spec: CategorySpec,
    matrix: list[dict[str, Any]],
    records: Any,
    expected_digest: str,
) -> list[dict[str, Any]]:
    checked_digest(expected_digest, spec.name + " complete outcome vector")
    require(type(records) is list and len(records) == spec.case_count
            and digest(records) == expected_digest,
            "an exact complete " + spec.name + " outcome vector was substituted")
    for case, observed in zip(matrix, records, strict=True):
        fields = {"case", "outcome"} if spec.name == "public" else {
            "case", "family", "outcome",
        }
        require(type(observed) is dict and set(observed) == fields
                and observed.get("case") == case["case"],
                "a source-ordered " + spec.name + " observation was omitted")
        if spec.name != "public":
            require(observed.get("family") == case["family"],
                    "a source-ordered " + spec.name + " family was substituted")
        validate_outcome(spec, observed["outcome"])
    return records


def observe_case(
    spec: CategorySpec,
    module: types.ModuleType,
    case: Mapping[str, Any],
    engine: types.ModuleType,
) -> dict[str, Any]:
    if spec.name == "public":
        try:
            outcome = module.prepare_case(engine, case)()
        except module.PracticeBenchmarkError:
            raise
        except Exception as error:
            outcome = {
                "status": "raise",
                "exception": module.normalize_exception(error, engine),
                "callbacks": [],
                "warnings": [],
            }
        result = {"case": case["case"], "outcome": outcome}
    else:
        outcome = module.execute_case(case, engine)
        result = {
            "case": case["case"],
            "family": case["family"],
            "outcome": outcome,
        }
    validate_outcome(spec, outcome)
    return result


def authenticate_baseline() -> types.ModuleType:
    baseline = importlib.import_module("re")
    expected = str(PINNED_STDLIB_RE)
    require(
        type(baseline) is types.ModuleType and baseline.__name__ == "re"
        and os.path.abspath(getattr(baseline, "__file__", "")) == expected
        and os.path.realpath(getattr(baseline, "__file__", "")) == expected,
        "the exact original pinned CPython regex reference was substituted",
    )
    return baseline


GUARD_TRUE_FIELDS = (
    "original_matchers_blocked", "adapter_import_quarantined",
    "native_sre_blocked", "builtins_import_guarded", "importlib_import_guarded",
    "actual_object_identity_guarded", "warning_registry_introspection_safe",
    "warning_registry_exactly_absent", "cross_family_imports_blocked",
    "external_regex_imports_blocked",
)
GUARD_COUNTER_FIELDS = (
    "cached_original_matcher_descendant_count",
    "cached_original_holder_count",
    "owned_ctypes_load_count",
    "owned_ctypes_symbol_count",
)


def snapshot_guard(
    active: Mapping[str, Any], spec: CategorySpec, family: FamilySpec,
) -> dict[str, Any]:
    require(isinstance(active, Mapping),
            "the real warning-safe matcher ownership guard was omitted")
    result: dict[str, Any] = {}
    for name in GUARD_TRUE_FIELDS:
        require(active.get(name) is True,
                "a continuous real candidate ownership guard was lost: " + name)
        result[name] = True
    require(active.get("public_type_names_used_for_ownership") is False,
            "an independently owned re-compatible type was misclassified")
    result["public_type_names_used_for_ownership"] = False
    expected_checks = 2 * spec.case_count
    for name in ("actual_method_guard_checks", "actual_warning_registry_guard_checks"):
        require(active.get(name) == expected_checks,
                "an exact before-and-after category identity guard was omitted: " + name)
        result[name] = expected_checks
    require(active.get("owned_native_ffi_allowed") is family.owned_ctypes,
            "the exact independently owned Zig FFI policy was changed")
    result["owned_native_ffi_allowed"] = family.owned_ctypes
    require(
        active.get("trusted_stdlib_ctypes_preloaded") is family.owned_ctypes
        and active.get("trusted_stdlib_ctypes_builtin_verified")
        is family.owned_ctypes
        and active.get("trusted_stdlib_ctypes_pythonapi_initialized")
        is family.owned_ctypes
        and active.get("trusted_stdlib_ctypes_source_sha256")
        == ("349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
            if family.owned_ctypes else None),
        "the corrected genuinely preloaded trusted ctypes guard was changed",
    )
    result["trusted_stdlib_ctypes_preloaded"] = family.owned_ctypes
    result["trusted_stdlib_ctypes_builtin_verified"] = family.owned_ctypes
    result["trusted_stdlib_ctypes_pythonapi_initialized"] = family.owned_ctypes
    result["trusted_stdlib_ctypes_source_sha256"] = (
        "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
        if family.owned_ctypes else None
    )
    for name in GUARD_COUNTER_FIELDS:
        value = active.get(name)
        require(type(value) is int and value >= 0,
                "a real owned-native guard observation was hidden: " + name)
        result[name] = value
    if not family.owned_ctypes:
        require(result["owned_ctypes_load_count"] == 0
                and result["owned_ctypes_symbol_count"] == 0,
                "an unowned external native library escaped")
    else:
        require(result["owned_ctypes_load_count"] >= 1
                and result["owned_ctypes_symbol_count"] >= 1,
                "the independently owned Zig engine or its native symbols were not loaded")
    return result


def make_worker_document(
    *, role: str, category: CategorySpec, family: FamilySpec | None,
    source_pin: str, matrix: list[dict[str, Any]],
    records: list[dict[str, Any]], source_owners: Mapping[str, Any],
    native_provenance: Mapping[str, Any] | None,
    owned_closure: Mapping[str, Any] | None,
    guard: Mapping[str, Any] | None,
) -> dict[str, Any]:
    records_sha256 = digest(records)
    validate_records(category, matrix, records, records_sha256)
    return {
        "schema": SCHEMA + "-isolated-category-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "category": category.name,
        "candidate_family": family.name if family is not None else None,
        "controller_source_sha256": source_pin,
        "category_source_relative": category.source_relative,
        "category_source_sha256": category.source_sha256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "previous_v2_relative": PREVIOUS_V2_RELATIVE,
        "previous_v2_sha256": PREVIOUS_V2_SHA256,
        "published_seed": category.published_seed,
        "matrix_sha256": category.matrix_sha256,
        "frozen_baseline_records_sha256": category.baseline_sha256,
        "case_count": category.case_count,
        "records_sha256": records_sha256,
        "records": records,
        "source_provenance": dict(source_owners),
        "native_provenance": dict(native_provenance)
        if native_provenance is not None else None,
        "owned_source_closure": dict(owned_closure)
        if owned_closure is not None else None,
        "matcher_guard": dict(guard) if guard is not None else None,
        "pid": os.getpid(),
        "candidate_import_count": sum(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "actual_candidate_workers": 0 if family is None else 1,
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


def execute_reference_worker(
    category: CategorySpec, role: str, source_pin: str,
) -> dict[str, Any]:
    require(role in ("reference_a", "reference_b"),
            "select one exact, independent standard-library reference")
    verify_runtime()
    read_owned(SOURCE_RELATIVE, source_pin, MAX_SOURCE_BYTES)
    _, _, module, matrix, _, owners = load_prerequisites(category)
    baseline = authenticate_baseline()
    records = [observe_case(category, module, case, baseline) for case in matrix]
    require(digest(records) == category.baseline_sha256,
            "the complete frozen CPython " + category.name + " baseline changed")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a native candidate entered the isolated standard reference")
    return make_worker_document(
        role=role, category=category, family=None, source_pin=source_pin,
        matrix=matrix, records=records, source_owners=owners,
        native_provenance=None, owned_closure=None, guard=None,
    )


def execute_candidate_worker(
    category: CategorySpec, family: FamilySpec, source_pin: str,
    pins: OwnerPins,
) -> dict[str, Any]:
    verify_runtime()
    read_owned(SOURCE_RELATIVE, source_pin, MAX_SOURCE_BYTES)
    v5, _, module, matrix, _, owners = load_prerequisites(category)
    closure_before = authenticate_family_closure(v5, family, pins)
    warning, identity, _, _ = v5.load_frozen_oracles()
    baseline = authenticate_baseline()
    chosen = v5.family_spec(family.name)
    actual_pins = native_pins(family, pins)
    records: list[dict[str, Any]] = []
    native_provenance: dict[str, Any] | None = None
    guard_evidence: dict[str, Any] | None = None
    with warning.installed_warning_safe_guard(identity):
        with v5.chosen_original_guard(
            baseline, actual_pins, chosen, identity, warning,
        ) as active:
            candidate = active.get("candidate")
            require(type(candidate) is types.ModuleType
                    and candidate.__name__ == family.adapter_module,
                    "the independently owned category adapter was substituted")
            require(active.get("actual_method_guard_checks") == 0
                    and active.get("actual_warning_registry_guard_checks") == 0,
                    "the per-category matcher guards did not start from zero")
            for case in matrix:
                active["verify"]()
                active["actual_method_guard_checks"] += 1
                try:
                    observed = observe_case(category, module, case, candidate)
                finally:
                    active["verify"]()
                    active["actual_method_guard_checks"] += 1
                records.append(observed)
            guard_evidence = snapshot_guard(active, category, family)
            provenance = active.get("native_provenance")
            require(v5.validate_owners(provenance, chosen, actual_pins),
                    "the actual selected native owner changed under its guard")
            native_provenance = dict(provenance)
    require(native_provenance is not None and guard_evidence is not None,
            "the real candidate guard or native provenance was omitted")
    closure_after = authenticate_family_closure(v5, family, pins)
    require(closure_before == closure_after,
            "the owned native source closure changed during observation")
    return make_worker_document(
        role="candidate-" + family.name, category=category, family=family,
        source_pin=source_pin, matrix=matrix, records=records,
        source_owners=owners, native_provenance=native_provenance,
        owned_closure=closure_after, guard=guard_evidence,
    )


def unique_json(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in items:
        require(type(name) is str and name not in result,
                "duplicate complete isolated worker fields are forbidden")
        result[name] = value
    return result


def decode_worker(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "a complete bounded category worker output is mandatory: " + label)
    try:
        result = json.loads(
            raw, object_pairs_hook=unique_json,
            parse_constant=lambda _: (_ for _ in ()).throw(
                ContractError("nonfinite category worker output is forbidden")
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise ContractError(
            "the complete isolated category output is not canonical: " + label
        ) from error
    require(type(result) is dict and canonical(result) == raw,
            "a complete canonical category worker stream was substituted")
    return result


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "retain the entire bounded isolated category process stream")
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
        "a complete reversible isolated process stream was omitted: " + label,
    )
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise ContractError(
            "the exact isolated process stream is not valid base64: " + label
        ) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == value["sha256"]
        and base64.b64encode(raw).decode("ascii") == value["base64"],
        "the complete isolated process bytes were forged: " + label,
    )
    return raw


def validate_process_evidence(
    evidence: Any,
    *, role: str, category: CategorySpec, family: FamilySpec | None,
    expected_pid: int, result: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        type(evidence) is dict
        and set(evidence) == {
            "role", "category", "candidate_family", "pid", "returncode",
            "stdout", "stderr",
        }
        and evidence.get("role") == role
        and evidence.get("category") == category.name
        and evidence.get("candidate_family")
        == (family.name if family is not None else None)
        and type(expected_pid) is int and expected_pid > 0
        and evidence.get("pid") == expected_pid
        and evidence.get("returncode") == 0,
        "a real isolated category process, family, role, or exit was forged",
    )
    stdout = decode_stream(evidence.get("stdout"), role + " stdout")
    stderr = decode_stream(evidence.get("stderr"), role + " stderr")
    require(
        stderr == b"" and canonical(dict(result)) == stdout,
        "the complete validated category result differs from its real process",
    )
    return evidence


def validate_worker_document(
    result: Any,
    *, role: str, category: CategorySpec, family: FamilySpec | None,
    source_pin: str, matrix: list[dict[str, Any]], expected_pid: int,
    pins: OwnerPins | None = None,
) -> dict[str, Any]:
    require(type(result) is dict, "a complete category worker is mandatory")
    expected = {
        "schema": SCHEMA + "-isolated-category-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "category": category.name,
        "candidate_family": family.name if family is not None else None,
        "controller_source_sha256": source_pin,
        "category_source_relative": category.source_relative,
        "category_source_sha256": category.source_sha256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "previous_v2_relative": PREVIOUS_V2_RELATIVE,
        "previous_v2_sha256": PREVIOUS_V2_SHA256,
        "published_seed": category.published_seed,
        "matrix_sha256": category.matrix_sha256,
        "frozen_baseline_records_sha256": category.baseline_sha256,
        "case_count": category.case_count,
        "pid": expected_pid,
        "actual_candidate_workers": 0 if family is None else 1,
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
    for name, actual in expected.items():
        require(result.get(name) == actual,
                "a frozen isolated category worker changed: " + name)
    records = validate_records(
        category, matrix, result.get("records"),
        result.get("records_sha256"),
    )
    require(len(records) == category.case_count,
            "a genuine category worker silently omitted observations")
    sources = result.get("source_provenance")
    require(type(sources) is dict
            and set(sources) == {"original_v5", "previous_v2", "category"},
            "the immutable original, predecessor, or category was omitted")
    for key, relative, expected_hash in (
        ("original_v5", V5_RELATIVE, V5_SHA256),
        ("previous_v2", PREVIOUS_V2_RELATIVE, PREVIOUS_V2_SHA256),
        ("category", category.source_relative, category.source_sha256),
    ):
        owner = sources.get(key)
        require(type(owner) is dict and set(owner)
                == {"relative", "sha256", "bytes", "device", "inode"}
                and owner.get("relative") == relative
                and owner.get("sha256") == expected_hash
                and type(owner.get("bytes")) is int and owner["bytes"] > 0
                and type(owner.get("device")) is int and owner["device"] >= 0
                and type(owner.get("inode")) is int and owner["inode"] > 0,
                "an exact immutable worker source owner was forged: " + key)
    if family is None:
        require(pins is None
                and result.get("candidate_import_count") == 0
                and result.get("native_provenance") is None
                and result.get("owned_source_closure") is None
                and result.get("matcher_guard") is None
                and result.get("records_sha256") == category.baseline_sha256,
                "a candidate or substituted outcome escaped into a reference")
    else:
        require(isinstance(pins, OwnerPins),
                "pin the exact real complete candidate family source closure")
        actual_pins = native_pins(family, pins)
        require(type(result.get("candidate_import_count")) is int
                and result["candidate_import_count"] >= 3,
                "the actual independent native candidate was not loaded")
        snapshot_guard(result.get("matcher_guard"), category, family)
        closure = result.get("owned_source_closure")
        expected_paths = set(family.owned_source_relatives) | {
            family.engine_relative, family.bridge_relative,
        }
        require(type(closure) is dict and set(closure) == expected_paths,
                "the complete caller-pinned family source closure was changed")
        expected_sources = dict(pins.owned_sources)
        for path, expected_hash in (
            *pins.owned_sources,
            (family.engine_relative, pins.engine_sha256),
            (family.bridge_relative, pins.bridge_sha256),
        ):
            owner = closure.get(path)
            require(type(owner) is dict
                    and set(owner) == {
                        "relative", "sha256", "bytes", "device", "inode",
                    }
                    and owner.get("relative") == path
                    and owner.get("sha256") == expected_hash
                    and type(owner.get("bytes")) is int and owner["bytes"] > 0
                    and type(owner.get("device")) is int and owner["device"] >= 0
                    and type(owner.get("inode")) is int and owner["inode"] > 0,
                    "a complete independently owned source was forged: " + path)
        require(expected_sources[family.adapter_relative]
                == actual_pins["source"],
                "the independently selected adapter escaped its source closure")
        provenance = result.get("native_provenance")
        require(type(provenance) is dict
                and set(provenance) == {
                    "source", "native_engine", "native_bridge",
                },
                "the independent family native provenance was omitted")
        for name, path, expected_hash in (
            ("source", family.adapter_relative, pins.adapter_sha256),
            ("native_engine", family.engine_relative, pins.engine_sha256),
            ("native_bridge", family.bridge_relative, pins.bridge_sha256),
        ):
            owner = provenance.get(name)
            require(type(owner) is dict and owner.get("relative") == path
                    and owner.get("sha256") == expected_hash,
                    "an independently owned native component changed: " + name)
    return result


def run_isolated_worker(
    *, role: str, category: CategorySpec, family: FamilySpec | None,
    source_pin: str, matrix: list[dict[str, Any]],
    pins: OwnerPins | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in ("reference_a", "reference_b") if family is None
            else role == "candidate-" + family.name,
            "select exactly one real isolated category worker")
    arguments = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--internal-worker", "--category", category.name,
        "--role", role, "--oracle-source-sha256", source_pin,
        "--matrix-sha256", category.matrix_sha256,
    ]
    if family is not None:
        require(isinstance(pins, OwnerPins),
                "propagate every exact candidate owner to its isolated worker")
        native_pins(family, pins)
        arguments.extend((
            "--family", family.name,
            "--candidate-source-sha256", pins.adapter_sha256,
            "--native-engine-sha256", pins.engine_sha256,
            "--native-bridge-sha256", pins.bridge_sha256,
        ))
        for path, value in pins.owned_sources:
            arguments.extend(("--owned-source-sha256", path + "=" + value))
    else:
        require(pins is None,
                "a genuine isolated reference cannot receive candidate owners")
    try:
        process = subprocess.Popen(
            arguments, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(ROOT), shell=False,
            env={
                "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                "LC_ALL": "C", "PATH": "/usr/bin:/bin",
            },
        )
        stdout, stderr = process.communicate()
    except (OSError, subprocess.SubprocessError) as error:
        raise WorkerFailure(
            "the exact isolated " + category.name + " worker could not start",
            {"role": role, "category": category.name,
             "error_type": type(error).__name__, "error": str(error)},
        ) from error
    evidence = {
        "role": role,
        "category": category.name,
        "candidate_family": family.name if family is not None else None,
        "pid": process.pid,
        "returncode": process.returncode,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    if process.returncode != 0 or stderr:
        raise WorkerFailure(
            "the real isolated category worker failed: " + role, evidence,
        )
    try:
        result = validate_worker_document(
            decode_worker(stdout, role), role=role, category=category,
            family=family, source_pin=source_pin, matrix=matrix,
            expected_pid=process.pid, pins=pins,
        )
        validate_process_evidence(
            evidence, role=role, category=category, family=family,
            expected_pid=process.pid, result=result,
        )
    except (ContractError, TypeError, ValueError, KeyError) as error:
        evidence["validation_error"] = {
            "type": type(error).__name__, "message": str(error),
        }
        raise WorkerFailure(
            "the isolated complete category output was rejected: " + role,
            evidence,
        ) from error
    return result, evidence


def run_candidate(
    category: CategorySpec, family: FamilySpec, source_pin: str,
    pins: OwnerPins,
) -> dict[str, Any]:
    verify_runtime()
    read_owned(SOURCE_RELATIVE, source_pin, MAX_SOURCE_BYTES)
    v5, _, _, matrix, groups, owners = load_prerequisites(category)
    native_pins(family, pins)
    before = authenticate_family_closure(v5, family, pins)
    first, first_process = run_isolated_worker(
        role="reference_a", category=category, family=None,
        source_pin=source_pin, matrix=matrix,
    )
    second, second_process = run_isolated_worker(
        role="reference_b", category=category, family=None,
        source_pin=source_pin, matrix=matrix,
    )
    require(
        first["pid"] != second["pid"]
        and first["records_sha256"] == second["records_sha256"]
        == category.baseline_sha256
        and first["records"] == second["records"],
        "two complete independent CPython references did not exactly agree",
    )
    candidate, candidate_process = run_isolated_worker(
        role="candidate-" + family.name, category=category,
        family=family, source_pin=source_pin, matrix=matrix, pins=pins,
    )
    require(candidate["pid"] not in (first["pid"], second["pid"]),
            "the category references and native worker were not isolated")
    by_group = {name: 0 for name in groups}
    mismatches: list[dict[str, Any]] = []
    for case, original, observed in zip(
        matrix, first["records"], candidate["records"], strict=True,
    ):
        require(case["case"] == original["case"] == observed["case"],
                "a source-ordered category comparison was silently changed")
        if original["outcome"] != observed["outcome"]:
            group = case["operation"] if category.name == "public" else case["family"]
            by_group[group] += 1
            mismatches.append({
                "case": case["case"],
                "group": group,
                "input": case,
                "baseline_outcome": original["outcome"],
                "candidate_outcome": observed["outcome"],
            })
    after = authenticate_family_closure(v5, family, pins)
    require(before == after == candidate["owned_source_closure"],
            "the independent native family changed during its category run")
    return {
        "schema": SCHEMA + "-actual-category-result",
        "status": "PASS" if not mismatches else "FAIL",
        "python": "3.14.6",
        "candidate_family": family.name,
        "category": category.name,
        "controller_source_sha256": source_pin,
        "category_source_relative": category.source_relative,
        "category_source_sha256": category.source_sha256,
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "previous_v2_relative": PREVIOUS_V2_RELATIVE,
        "previous_v2_sha256": PREVIOUS_V2_SHA256,
        "published_seed": category.published_seed,
        "matrix_sha256": category.matrix_sha256,
        "case_denominator": category.case_count,
        "group_count": category.group_count,
        "cases_per_group": category.cases_per_group,
        "baseline_reference_count": 2,
        "baseline_reference_pids": [first["pid"], second["pid"]],
        "baseline_records_sha256": first["records_sha256"],
        "second_reference_records_sha256": second["records_sha256"],
        "candidate_records_sha256": candidate["records_sha256"],
        "actual_baseline_cases": len(first["records"]),
        "actual_second_reference_cases": len(second["records"]),
        "actual_candidate_cases": len(candidate["records"]),
        "baseline_records": first["records"],
        "second_reference_records": second["records"],
        "candidate_records": candidate["records"],
        "mismatch_count": len(mismatches),
        "mismatches_by_group": by_group,
        "all_mismatches": mismatches,
        "first_mismatch": mismatches[0] if mismatches else None,
        "candidate_pid": candidate["pid"],
        "isolated_process_evidence": [
            first_process,
            second_process,
            candidate_process,
        ],
        "source_provenance": dict(owners),
        "native_provenance": candidate["native_provenance"],
        "owned_source_closure": after,
        "owned_source_closure_unchanged": True,
        "matcher_guard": candidate["matcher_guard"],
        "actual_reference_workers": 2,
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


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "actual_file_reads": 0,
        "actual_file_writes": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_threads_started": 0,
        "clock_samples": 0,
        "gc_collections": 0,
        "hidden_cases_read": 0,
        "performance_files_read": 0,
        "blocked_reads": 0,
        "blocked_writes": 0,
        "blocked_imports": 0,
        "blocked_workers": 0,
        "blocked_threads": 0,
        "blocked_clocks": 0,
        "blocked_gc_collections": 0,
    }
    installed: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    def deny(counter: str, message: str) -> Callable[..., Any]:
        def blocked(*arguments: Any, **keywords: Any) -> Any:
            effects[counter] += 1
            raise SourceOnlyError(message)
        return blocked

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (Path, "open"),
            (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, deny("blocked_reads",
                                     "a synthetic public control cannot read a file"))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "replace"), (os, "link"), (os, "symlink"),
            (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name, deny("blocked_writes",
                                     "a synthetic public control cannot write"))
        install(importlib, "import_module", deny(
            "blocked_imports", "a synthetic control cannot import an engine",
        ))
        install(builtins, "__import__", deny(
            "blocked_imports", "a synthetic control cannot import a module",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, deny(
                "blocked_workers", "a synthetic control cannot start a worker",
            ))
        install(threading.Thread, "start", deny(
            "blocked_threads", "a synthetic control cannot start a thread",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time", "process_time_ns",
        ):
            install(time, name, deny(
                "blocked_clocks", "a synthetic control cannot sample a clock",
            ))
        install(gc, "collect", deny(
            "blocked_gc_collections", "a synthetic control cannot run GC",
        ))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_outcome(spec: CategorySpec, index: int) -> dict[str, Any]:
    warnings: list[dict[str, str]] = []
    if index % 7 == 0:
        warnings.append({
            "category_module": "builtins", "category": "FutureWarning",
            "message": "synthetic frozen category warning",
        })
    if spec.name == "public":
        if index % 5 == 0:
            return {
                "status": "raise",
                "exception": {"kind": "ordinary-python-exception",
                              "module": "builtins", "type": "ValueError",
                              "args": ["synthetic public failure"]},
                "callbacks": [], "warnings": warnings,
            }
        return {"status": "return", "value": index,
                "callbacks": [], "warnings": warnings}
    if spec.name == "scanner":
        common = {
            "callbacks": [], "warnings": warnings,
            "combined_pattern": None, "lexicon": None,
        }
        if index % 5 == 0:
            return {
                **common, "status": "raise",
                "exception": {"kind": "ordinary-python-error",
                              "module": "builtins", "type": "ValueError",
                              "args": ["synthetic scanner failure"]},
            }
        return {**common, "status": "return", "value": index}
    common = {
        "stage": "expand", "match_before": None,
        "source_after": None, "mutation": None, "warnings": warnings,
    }
    if index % 5 == 0:
        return {
            **common, "status": "raise",
            "exception": {"kind": "ordinary-python-error",
                          "module": "builtins", "type": "BufferError",
                          "args": ["synthetic exporter failure"]},
        }
    return {**common, "status": "return", "value": index}


def synthetic_category(
    spec: CategorySpec,
) -> tuple[list[dict[str, Any]], tuple[str, ...], list[dict[str, Any]]]:
    groups = tuple("synthetic-group-" + str(index)
                   for index in range(spec.group_count))
    matrix: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for group_index, group in enumerate(groups):
        for variant in range(spec.cases_per_group):
            number = len(matrix)
            case: dict[str, Any] = {
                "case": "synthetic." + spec.name + "." + format(number, "04d"),
            }
            if spec.name == "public":
                case["operation"] = group
                case["domain"] = "text" if variant < 12 else "bytes"
            else:
                case["family"] = group
            matrix.append(case)
            outcome = synthetic_outcome(spec, group_index + variant)
            row: dict[str, Any] = {"case": case["case"], "outcome": outcome}
            if spec.name != "public":
                row["family"] = group
            records.append(row)
    return matrix, groups, records


def synthetic_owner_pins(family: FamilySpec) -> OwnerPins:
    """Construct entirely synthetic owner pins without observing any file."""
    require(family_spec(family.name) is family,
            "select an exact independently owned synthetic candidate family")

    def synthetic_sha256(label: str) -> str:
        return hashlib.sha256(
            ("synthetic-independent-owner:" + family.name + ":" + label)
            .encode("ascii")
        ).hexdigest()

    sources = tuple(
        path + "=" + synthetic_sha256("source:" + path)
        for path in family.owned_source_relatives
    )
    adapter = synthetic_sha256("source:" + family.adapter_relative)
    engine = synthetic_sha256("native-engine")
    bridge = engine if family.name == "c" else synthetic_sha256("native-bridge")
    return resolve_owner_pins(family, adapter, engine, bridge, sources)


def synthetic_guard(spec: CategorySpec, family: FamilySpec) -> dict[str, Any]:
    result: dict[str, Any] = {name: True for name in GUARD_TRUE_FIELDS}
    result.update({
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": 2 * spec.case_count,
        "actual_warning_registry_guard_checks": 2 * spec.case_count,
        "owned_native_ffi_allowed": family.owned_ctypes,
        "trusted_stdlib_ctypes_preloaded": family.owned_ctypes,
        "trusted_stdlib_ctypes_builtin_verified": family.owned_ctypes,
        "trusted_stdlib_ctypes_pythonapi_initialized": family.owned_ctypes,
        "trusted_stdlib_ctypes_source_sha256": (
            "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
            if family.owned_ctypes else None
        ),
        "cached_original_matcher_descendant_count": 5,
        "cached_original_holder_count": 7,
        "owned_ctypes_load_count": 1 if family.owned_ctypes else 0,
        "owned_ctypes_symbol_count": 3 if family.owned_ctypes else 0,
    })
    return result


def synthetic_process(
    spec: CategorySpec, family: FamilySpec | None, role: str, pid: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    result = {
        "schema": SCHEMA + "-synthetic-isolated-process",
        "status": "OBSERVED",
        "role": role,
        "category": spec.name,
        "candidate_family": family.name if family is not None else None,
        "pid": pid,
    }
    evidence = {
        "role": role,
        "category": spec.name,
        "candidate_family": family.name if family is not None else None,
        "pid": pid,
        "returncode": 0,
        "stdout": encode_stream(canonical(result)),
        "stderr": encode_stream(b""),
    }
    return result, evidence


def copy_process_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **dict(evidence),
        "stdout": dict(evidence["stdout"]),
        "stderr": dict(evidence["stderr"]),
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted = 0
    rejected = 0
    synthetic_cases = {name: 0 for name in CATEGORY_SPECS}

    def accept(condition: Any, label: str) -> None:
        nonlocal accepted
        require(condition, "an actual synthetic positive control failed: " + label)
        accepted += 1

    def reject(action: Callable[[], Any], label: str) -> None:
        nonlocal rejected
        try:
            action()
        except (ContractError, ValueError, TypeError, KeyError, OSError):
            rejected += 1
            return
        raise ContractError("an actual synthetic rejection escaped: " + label)

    with source_only_boundary() as effects:
        accept(set(CATEGORY_SPECS) == {"public", "scanner", "buffer"},
               "exact three separately executable frozen categories")
        accept(set(FAMILY_SPECS) == {"rust", "c", "zig"},
               "exact three independently selected native families")
        for invalid in (None, "", "all", "*", "public,scanner", "PUBLIC", 0,
                        ["public"], "public/buffer"):
            reject(lambda value=invalid: category_spec(value),
                   "reject combined or substituted category " + repr(invalid))
        for invalid in (None, "", "all", "stdlib", "re", "RUST", 0,
                        ["rust"], "rust,c"):
            reject(lambda value=invalid: family_spec(value),
                   "reject combined or delegated native family " + repr(invalid))
        for family_name in FAMILY_SPECS:
            family = family_spec(family_name)
            pins = synthetic_owner_pins(family)
            sources = tuple(path + "=" + value for path, value in pins.owned_sources)
            accept(len(sources) == len(family.owned_source_relatives),
                   family_name + " retain every independently owned synthetic source")
            accept(resolve_owner_pins(
                family, pins.adapter_sha256, pins.engine_sha256,
                pins.bridge_sha256, sources,
            ) == pins, family_name + " accept exact complete source ownership")
            accept(resolve_owner_pins(
                family, pins.adapter_sha256, pins.engine_sha256,
                pins.bridge_sha256, tuple(reversed(sources)),
            ) == pins, family_name + " normalize complete source pin order")
            accept(native_pins(family, pins) == {
                "source": pins.adapter_sha256,
                "native_engine": pins.engine_sha256,
                "native_bridge": pins.bridge_sha256,
            }, family_name + " preserve exact independent native pins")
            for index, path in enumerate(family.owned_source_relatives):
                reject(lambda position=index: resolve_owner_pins(
                    family, pins.adapter_sha256, pins.engine_sha256,
                    pins.bridge_sha256,
                    sources[:position] + sources[position + 1:],
                ), family_name + " reject omitted owned source " + path)
                reject(lambda position=index: resolve_owner_pins(
                    family, pins.adapter_sha256, pins.engine_sha256,
                    pins.bridge_sha256, sources + (sources[position],),
                ), family_name + " reject duplicate owned source " + path)
            wrong_adapter = hashlib.sha256(
                ("synthetic-foreign-adapter:" + family_name).encode("ascii")
            ).hexdigest()
            reject(lambda: resolve_owner_pins(
                family, wrong_adapter, pins.engine_sha256,
                pins.bridge_sha256, sources,
            ), family_name + " reject substituted Python adapter hash")
            wrong_native = hashlib.sha256(
                ("synthetic-foreign-native:" + family_name).encode("ascii")
            ).hexdigest()
            reject(lambda: resolve_owner_pins(
                family, pins.adapter_sha256, pins.engine_sha256,
                wrong_native if family_name == "c" else pins.engine_sha256,
                sources,
            ), family_name + " reject forged native alias policy")
            for invalid in (None, "", "0" * 64, "A" * 64, "z" * 64, 3):
                reject(lambda item=invalid: resolve_owner_pins(
                    family, item, pins.engine_sha256,
                    pins.bridge_sha256, sources,
                ), family_name + " reject malformed candidate adapter hash")
                reject(lambda item=invalid: resolve_owner_pins(
                    family, pins.adapter_sha256, item,
                    pins.bridge_sha256, sources,
                ), family_name + " reject malformed native engine hash")
                reject(lambda item=invalid: resolve_owner_pins(
                    family, pins.adapter_sha256, pins.engine_sha256,
                    item, sources,
                ), family_name + " reject malformed native bridge hash")
            for foreign_name in FAMILY_SPECS:
                if foreign_name != family_name:
                    foreign = family_spec(foreign_name)
                    reject(lambda chosen=foreign: resolve_owner_pins(
                        chosen, pins.adapter_sha256, pins.engine_sha256,
                        pins.bridge_sha256, sources,
                    ), family_name + " reject the " + foreign_name + " source family")
            for entry in (
                "candidates/foreign.py=" + pins.adapter_sha256,
                "../candidates/escape.py=" + pins.adapter_sha256,
                "candidates//escape.py=" + pins.adapter_sha256,
                "candidates/escape.py=not-a-sha256",
                "candidates/escape.py",
            ):
                reject(lambda value=entry: resolve_owner_pins(
                    family, pins.adapter_sha256, pins.engine_sha256,
                    pins.bridge_sha256, sources + (value,),
                ), family_name + " reject foreign or escaping synthetic owner")
        for name in CATEGORY_SPECS:
            spec = category_spec(name)
            accept(spec.name == name, "authenticate synthetic " + name + " category")
            matrix, groups, records = synthetic_category(spec)
            matrix_hash = digest(matrix)
            record_hash = digest(records)
            accept(validate_matrix_document(spec, matrix, matrix_hash, groups)
                   is matrix, "retain all synthetic " + name + " cases")
            accept(validate_records(spec, matrix, records, record_hash) is records,
                   "retain every synthetic " + name + " outcome")
            synthetic_cases[name] = len(records)
            accept(any(row["outcome"]["status"] == "raise" for row in records),
                   "retain every synthetic " + name + " error")
            accept(any(row["outcome"]["warnings"] for row in records),
                   "retain every synthetic " + name + " warning")
            reject(lambda: validate_matrix_document(
                spec, matrix[:-1], matrix_hash, groups,
            ), "reject omitted " + name + " matrix case")
            reject(lambda: validate_matrix_document(
                spec, matrix + [matrix[0]], matrix_hash, groups,
            ), "reject duplicated " + name + " matrix case")
            reject(lambda: validate_matrix_document(
                spec, matrix, "0" * 64, groups,
            ), "reject forged " + name + " matrix hash")
            reject(lambda: validate_matrix_document(
                spec, matrix, matrix_hash, groups[:-1],
            ), "reject omitted " + name + " category family")
            reject(lambda: validate_records(
                spec, matrix, records[:-1], record_hash,
            ), "reject omitted " + name + " result")
            reject(lambda: validate_records(
                spec, matrix, list(reversed(records)), record_hash,
            ), "reject reordered " + name + " results")
            reject(lambda: validate_records(
                spec, matrix, records, "a" * 64,
            ), "reject forged " + name + " outcome digest")
            workers: list[tuple[str, FamilySpec | None, int]] = [
                ("reference_a", None, 101),
                ("reference_b", None, 102),
            ]
            workers.extend(
                ("candidate-" + family_name, family_spec(family_name), 103 + index)
                for index, family_name in enumerate(FAMILY_SPECS)
            )
            for role, selected, pid in workers:
                process_result, process_evidence = synthetic_process(
                    spec, selected, role, pid,
                )
                accept(
                    validate_process_evidence(
                        process_evidence, role=role, category=spec,
                        family=selected, expected_pid=pid,
                        result=process_result,
                    ) is process_evidence,
                    name + "/" + role + " preserve complete reversible streams",
                )
                for field, replacement in (
                    ("role", "candidate-foreign"),
                    ("category", "all"),
                    ("candidate_family", "foreign"),
                    ("pid", pid + 100),
                    ("returncode", 1),
                ):
                    poisoned = copy_process_evidence(process_evidence)
                    poisoned[field] = replacement
                    reject(
                        lambda value=poisoned: validate_process_evidence(
                            value, role=role, category=spec, family=selected,
                            expected_pid=pid, result=process_result,
                        ),
                        name + "/" + role + " reject process " + field,
                    )
                for field in ("bytes", "sha256", "complete"):
                    poisoned = copy_process_evidence(process_evidence)
                    poisoned["stdout"][field] = (
                        poisoned["stdout"]["bytes"] + 1
                        if field == "bytes"
                        else "a" * 64 if field == "sha256" else False
                    )
                    reject(
                        lambda value=poisoned: validate_process_evidence(
                            value, role=role, category=spec, family=selected,
                            expected_pid=pid, result=process_result,
                        ),
                        name + "/" + role + " reject forged stdout " + field,
                    )
                poisoned = copy_process_evidence(process_evidence)
                poisoned["stdout"]["base64"] = "!not-canonical-base64!"
                reject(
                    lambda value=poisoned: validate_process_evidence(
                        value, role=role, category=spec, family=selected,
                        expected_pid=pid, result=process_result,
                    ),
                    name + "/" + role + " reject malformed reversible stdout",
                )
                poisoned = copy_process_evidence(process_evidence)
                del poisoned["stdout"]["sha256"]
                reject(
                    lambda value=poisoned: validate_process_evidence(
                        value, role=role, category=spec, family=selected,
                        expected_pid=pid, result=process_result,
                    ),
                    name + "/" + role + " reject omitted stdout evidence",
                )
                poisoned = copy_process_evidence(process_evidence)
                poisoned["stdout"]["unapproved"] = True
                reject(
                    lambda value=poisoned: validate_process_evidence(
                        value, role=role, category=spec, family=selected,
                        expected_pid=pid, result=process_result,
                    ),
                    name + "/" + role + " reject extra stdout evidence",
                )
                poisoned = copy_process_evidence(process_evidence)
                poisoned["stderr"] = encode_stream(b"synthetic worker failure")
                reject(
                    lambda value=poisoned: validate_process_evidence(
                        value, role=role, category=spec, family=selected,
                        expected_pid=pid, result=process_result,
                    ),
                    name + "/" + role + " reject concealed complete stderr",
                )
                forged_result = dict(process_result)
                forged_result["status"] = "FORGED"
                reject(
                    lambda value=forged_result: validate_process_evidence(
                        process_evidence, role=role, category=spec,
                        family=selected, expected_pid=pid, result=value,
                    ),
                    name + "/" + role + " reject forged worker document",
                )
            for family_name in FAMILY_SPECS:
                family = family_spec(family_name)
                accept(snapshot_guard(synthetic_guard(spec, family), spec, family)
                       ["actual_method_guard_checks"] == 2 * spec.case_count,
                       name + "/" + family_name + " exact before-and-after guards")
                for field in GUARD_TRUE_FIELDS:
                    poisoned = synthetic_guard(spec, family)
                    poisoned[field] = False
                    reject(lambda value=poisoned: snapshot_guard(value, spec, family),
                           name + "/" + family_name + " reject guard " + field)
                for field in ("actual_method_guard_checks",
                              "actual_warning_registry_guard_checks"):
                    for amount in (-1, 1):
                        poisoned = synthetic_guard(spec, family)
                        poisoned[field] += amount
                        reject(lambda value=poisoned: snapshot_guard(
                            value, spec, family,
                        ), name + "/" + family_name + " reject wrong " + field)
                poisoned = synthetic_guard(spec, family)
                poisoned["owned_native_ffi_allowed"] = not family.owned_ctypes
                reject(lambda value=poisoned: snapshot_guard(value, spec, family),
                       name + "/" + family_name + " reject foreign FFI")
                for field in (
                    "trusted_stdlib_ctypes_preloaded",
                    "trusted_stdlib_ctypes_builtin_verified",
                    "trusted_stdlib_ctypes_pythonapi_initialized",
                ):
                    poisoned = synthetic_guard(spec, family)
                    poisoned[field] = not family.owned_ctypes
                    reject(lambda value=poisoned: snapshot_guard(
                        value, spec, family,
                    ), name + "/" + family_name + " reject trusted FFI " + field)
                poisoned = synthetic_guard(spec, family)
                poisoned["trusted_stdlib_ctypes_source_sha256"] = (
                    None if family.owned_ctypes
                    else "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
                )
                reject(lambda value=poisoned: snapshot_guard(
                    value, spec, family,
                ), name + "/" + family_name + " reject substituted trusted FFI source")
                if not family.owned_ctypes:
                    for field in ("owned_ctypes_load_count",
                                  "owned_ctypes_symbol_count"):
                        poisoned = synthetic_guard(spec, family)
                        poisoned[field] = 1
                        reject(lambda value=poisoned: snapshot_guard(
                            value, spec, family,
                        ), name + "/" + family_name + " reject unowned FFI")
                else:
                    for field in ("owned_ctypes_load_count",
                                  "owned_ctypes_symbol_count"):
                        poisoned = synthetic_guard(spec, family)
                        poisoned[field] = 0
                        reject(lambda value=poisoned: snapshot_guard(
                            value, spec, family,
                        ), name + "/" + family_name + " reject omitted owned FFI")
        for value in (None, "", "z" * 64, "A" * 64, "0" * 64, "12", 4):
            reject(lambda item=value: checked_digest(item, "synthetic poison"),
                   "reject a forged immutable SHA-256")
        for path in ("", "/tmp/escape", "../escape", "tools/../x",
                     "tools//x", "tools\\x", "tools/\x00x"):
            reject(lambda item=path: owned_relative(item),
                   "reject an unowned or escaping source path")
        for action, label in (
            (lambda: builtins.open("synthetic-forbidden"), "file read"),
            (lambda: os.open("synthetic-forbidden", os.O_RDONLY), "native file read"),
            (lambda: importlib.import_module("candidates.rust_candidate"),
             "candidate import"),
            (lambda: subprocess.Popen(["synthetic-forbidden"]), "process worker"),
            (lambda: os.write(-1, b"synthetic-forbidden"), "file write"),
            (lambda: os.link("synthetic-source", "synthetic-target"),
             "hard-link write"),
            (lambda: threading.Thread().start(), "thread worker"),
            (lambda: time.perf_counter_ns(), "performance clock"),
            (lambda: time.monotonic_ns(), "monotonic clock"),
            (lambda: gc.collect(), "garbage collection"),
        ):
            reject(action, "block synthetic " + label)
        accept(synthetic_cases == {
            "public": 864, "scanner": 1024, "buffer": 768,
        }, "keep every category denominator separate")
        accept(effects["actual_file_reads"] == 0
               and effects["actual_file_writes"] == 0
               and effects["actual_candidate_imports"] == 0
               and effects["actual_reference_workers"] == 0
               and effects["actual_candidate_workers"] == 0
               and effects["clock_samples"] == 0
               and effects["gc_collections"] == 0,
               "execute no candidate, reference, file, clock, or garbage collection")
        effect_snapshot = dict(effects)
    require(accepted >= 20 and rejected >= 160,
            "the genuine synthetic category control suite is incomplete")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a real candidate escaped into a synthetic category self-test")
    return {
        "schema": SCHEMA + "-synthetic-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "self_test_only": True,
        "categories": ["public", "scanner", "buffer"],
        "families": ["rust", "c", "zig"],
        "original_v5_relative": V5_RELATIVE,
        "original_v5_sha256": V5_SHA256,
        "previous_v2_relative": PREVIOUS_V2_RELATIVE,
        "previous_v2_sha256": PREVIOUS_V2_SHA256,
        "frozen_category_pins": {
            name: {
                "source_relative": spec.source_relative,
                "source_sha256": spec.source_sha256,
                "matrix_sha256": spec.matrix_sha256,
                "baseline_sha256": spec.baseline_sha256,
                "published_seed": spec.published_seed,
                "case_count": spec.case_count,
                "group_count": spec.group_count,
                "cases_per_group": spec.cases_per_group,
            }
            for name, spec in CATEGORY_SPECS.items()
        },
        "frozen_family_owner_allowlists": {
            name: {
                "adapter_module": spec.adapter_module,
                "adapter_relative": spec.adapter_relative,
                "engine_relative": spec.engine_relative,
                "bridge_module": spec.bridge_module,
                "bridge_relative": spec.bridge_relative,
                "owned_native_ffi_allowed": spec.owned_ctypes,
                "owned_source_relatives": list(spec.owned_source_relatives),
                "caller_pinned_source_hashes_required": True,
                "native_engine_equals_bridge": name == "c",
            }
            for name, spec in FAMILY_SPECS.items()
        },
        "synthetic_case_denominators": synthetic_cases,
        "synthetic_positive_controls": accepted,
        "synthetic_rejection_controls": rejected,
        "synthetic_side_effect_boundary": effect_snapshot,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_files_read": 0,
        "actual_native_binary_reads": 0,
        "actual_oracle_source_reads": 0,
        "actual_baseline_cases": 0,
        "actual_candidate_cases": 0,
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
        description="Compare one frozen Python regex category and one owned engine",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--candidate", choices=tuple(FAMILY_SPECS))
    modes.add_argument("--internal-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--category", choices=tuple(CATEGORY_SPECS))
    parser.add_argument("--family", choices=tuple(FAMILY_SPECS),
                        help=argparse.SUPPRESS)
    parser.add_argument(
        "--role", choices=("reference_a", "reference_b", "candidate-rust",
                            "candidate-c", "candidate-zig"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    parser.add_argument("--owned-source-sha256", action="append")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "candidate", "category", "family", "role",
            "oracle_source_sha256", "matrix_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256", "owned_source_sha256",
        )), "a synthetic source self-test cannot select or pin a real engine")
        result = source_self_test()
    elif options.candidate:
        require(options.category is not None and options.family is None
                and options.role is None,
                "a real run requires exactly one candidate and one category")
        category = category_spec(options.category)
        require(checked_digest(
            options.matrix_sha256, "the independently frozen category matrix",
        ) == category.matrix_sha256,
                "the caller did not pin the exact frozen category matrix")
        family = family_spec(options.candidate)
        pins = resolve_owner_pins(
            family, options.candidate_source_sha256,
            options.native_engine_sha256, options.native_bridge_sha256,
            options.owned_source_sha256,
        )
        result = run_candidate(
            category, family,
            checked_digest(options.oracle_source_sha256,
                           "the independently frozen category controller"),
            pins,
        )
    else:
        require(options.category is not None and options.role is not None
                and options.candidate is None,
                "an internal worker requires exactly one frozen category and role")
        category = category_spec(options.category)
        source_pin = checked_digest(
            options.oracle_source_sha256, "the frozen internal category controller",
        )
        require(checked_digest(
            options.matrix_sha256, "the frozen isolated category matrix",
        ) == category.matrix_sha256,
                "the isolated worker changed its exact frozen category matrix")
        if options.role in ("reference_a", "reference_b"):
            require(options.family is None
                    and options.candidate_source_sha256 is None
                    and options.native_engine_sha256 is None
                    and options.native_bridge_sha256 is None
                    and options.owned_source_sha256 is None,
                    "a standard-library reference cannot choose or pin a candidate")
            result = execute_reference_worker(category, options.role, source_pin)
        else:
            require(options.family is not None
                    and options.role == "candidate-" + options.family,
                    "an isolated native worker selected a foreign family")
            family = family_spec(options.family)
            pins = resolve_owner_pins(
                family, options.candidate_source_sha256,
                options.native_engine_sha256, options.native_bridge_sha256,
                options.owned_source_sha256,
            )
            result = execute_candidate_worker(category, family, source_pin, pins)
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") in ("PASS", "OBSERVED") else 1

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        evidence: dict[str, Any] = {
            "schema": SCHEMA + "-complete-category-process-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error": str(error),
            "complete_traceback": traceback.format_exc(),
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
        if isinstance(error, WorkerFailure):
            evidence["complete_worker_failure"] = dict(error.evidence)
        sys.stderr.buffer.write(canonical(evidence))
        sys.stderr.buffer.flush()
        raise SystemExit(1) from error
