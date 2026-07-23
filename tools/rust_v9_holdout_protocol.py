#!/usr/bin/env python3
"""Prospectively sealed, from-scratch, real-operation regex holdout.

This is an additive v9 protocol.  It never imports a previous performance
protocol, opens a previous secret, or changes a previously frozen test.
Verification and synthetic controls do not generate final inputs.  Only the
explicit, single-use final command may open the v9 commitment.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import collections
import contextlib
import gzip
import hashlib
import hmac
import io
import json
import math
import os
import platform
import random
import select
import statistics
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "performance/v9/holdout-manifest.json"
SELF_TEST_PATH = ROOT / "performance/v9/evidence/HOLDOUT-PROTOCOL-SELF-TEST.json"
EVIDENCE_ROOT = ROOT / "performance/v9/evidence"
OPENING_PATH = "/tmp/rebar-v9-final-holdout-opening-20260723-24576-v1.bin"

SCHEMA = "rebar-v9-prospective-semantic-performance-holdout-v1"
CASE_SCHEMA = "rebar-v9-secret-keyed-semantic-case-v1"
BUFFER_SCHEMA = "rebar-v9-exact-buffer-wire-v1"
ROW_SCHEMA = "rebar-v9-real-public-operation-paired-row-v1"
MEMORY_ROW_SCHEMA = "rebar-v9-independent-memory-row-v1"
SUMMARY_SCHEMA = "rebar-v9-real-public-operation-summary-v1"
FREEZE_SCHEMA = "rebar-v9-current-native-candidate-freeze-v1"
SELF_TEST_SCHEMA = "rebar-v9-prospective-synthetic-self-test-v1"
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
DEEP_SCHEMA = "rebar-rust-v8-deep-public-contract-v1"

APIS = (
    "compile",
    "escape",
    "search",
    "match",
    "fullmatch",
    "findall",
    "finditer",
    "split",
    "sub",
    "subn",
    "match-surface",
    "scanner",
)
WORKLOADS = (
    "literal-and-long-prefix",
    "character-class-and-unicode",
    "anchors-boundaries-and-windows",
    "greedy-lazy-atomic-and-possessive",
    "alternation-groups-and-backreferences",
    "lookaround-and-zero-width",
    "replacement-split-and-result-density",
    "logs-paths-urls-identifiers-and-noise",
)
NORMAL_APIS = frozenset(
    {"search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn"}
)
BANNED_ENGINES = frozenset(
    {
        "re",
        "_sre",
        "sre_compile",
        "sre_parse",
        "regex",
        "re2",
        "google_re2",
        "pcre",
        "pcre2",
        "hyperscan",
        "onig",
        "oniguruma",
    }
)
FAMILY_BY_MODULE = {
    "candidates.vm_candidate": "vm",
    "candidates.rust_candidate": "rust",
    "candidates.zig_candidate": "zig",
    "candidates.ast_candidate": "ast",
}
ARTIFACT_ROLES = {
    "candidates.vm_candidate": frozenset({"public-python", "native-bridge"}),
    "candidates.rust_candidate": frozenset(
        {"public-python", "native-source", "bridge-source", "native-bridge", "native-engine"}
    ),
    "candidates.zig_candidate": frozenset(
        {"public-python", "native-bridge", "native-engine"}
    ),
    "candidates.ast_candidate": frozenset({"public-python"}),
}

CASES_PER_CELL = 256
CASES_PER_API = 2_048
CASE_COUNT = 24_576
PAIRED_ROUNDS = 31
OPERATIONS_PER_SAMPLE = 16
WARMUPS = 4
BOOTSTRAP_DRAWS = 9_999
MEMORY_INDICES = frozenset(range(0, CASES_PER_CELL, 16))
MEMORY_CASES = len(APIS) * len(WORKLOADS) * len(MEMORY_INDICES)
MINIMUM_WINS = (3 * CASE_COUNT + 4) // 5
STUDENT_T_DF30_975 = 2.0422724563012373
REGRESSION_THRESHOLD = 5.0 / 6.0
CASE_TIMEOUT_SECONDS = 5.0
ORDER_SEED = 20260723931
BOOTSTRAP_SEED = 20260723999
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
EDGE_RUNNER_SHA256 = "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
EDGE_ANSWER_SHA256 = "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
DEEP_SOURCE_SHA256 = "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978"
DEEP_FIXTURE_SHA256 = "c72a5e47f15c94ce13ce34d4918c05ef81eea5b010ac119b255264e60939ef16"
DEEP_ANSWER_SHA256 = "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8"
UNSEAL_AUTHORIZATION = "UNSEAL-FROZEN-V9-HOLDOUT-AFTER-CANDIDATE-SELECTION"
SYNTHETIC_OPENING = hashlib.sha256(
    b"rebar-v9-public-synthetic-domain-never-a-final-opening"
).digest()
SYNTHETIC_MANIFEST_COMMITMENT = hashlib.sha256(
    b"rebar-v9-public-in-memory-manifest-never-a-final-commitment"
).hexdigest()
REQUIRED_CAMPAIGN_STEPS = frozenset(
    {
        "frozen-correctness-v2",
        "frozen-correctness-v3",
        "official-cpython-tests",
        "upstream-public-surface",
        "replacement-and-callback-adversarial",
        "deep-replacement-and-callback-adversarial",
        "isolated-crash-and-resource-safety",
        "isolated-depth-and-overflow-safety",
        "full-unicode-plane",
    }
)
EXCLUDED_PERFORMANCE_STEPS = frozenset(
    {
        "frozen-performance-correctness-v6",
        "frozen-performance-v7-integrity",
        "frozen-performance-correctness-v7",
    }
)


class ProtocolError(RuntimeError):
    """A frozen independence, correctness, timing, or secrecy control failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProtocolError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def canonical_digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1_048_576), b""):
            result.update(block)
    return result.hexdigest()


def is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(letter in "0123456789abcdef" for letter in value)
    )


def manifest_binding(document: dict[str, Any]) -> str:
    return canonical_digest(
        {key: value for key, value in document.items() if key != "binding_sha256"}
    )


def make_manifest(opening_sha256: str) -> dict[str, Any]:
    """Describe a commitment supplied by its independent opening custodian."""
    require(is_digest(opening_sha256), "the opening commitment is not SHA-256")
    applicability: dict[str, dict[str, Any]] = {}
    for api in NORMAL_APIS:
        applicability[api] = {
            "input": ["str", "bytes"],
            "outcome": ["hit", "miss"],
            "surface": ["module", "compiled"],
            "variants_per_factor": 32,
        }
    applicability.update(
        {
            "compile": {
                "input": ["str", "bytes"],
                "lifecycle": ["cold-cache", "warm-cache"],
                "surface": ["module"],
                "variants_per_factor": 64,
            },
            "escape": {
                "input": ["str", "bytes"],
                "special_density": ["ordinary", "regex-special"],
                "surface": ["module"],
                "variants_per_factor": 64,
            },
            "match-surface": {
                "capture": ["numbered", "named", "optional", "multiple"],
                "input": ["str", "bytes"],
                "outcome": ["hit"],
                "surface": ["module", "compiled"],
                "variants_per_factor": 16,
            },
            "scanner": {
                "input": ["str", "bytes"],
                "progression": ["ordinary", "zero-width"],
                "scanner_method": ["search", "match"],
                "surface": ["compiled-pattern-scanner"],
                "variants_per_factor": 32,
            },
        }
    )
    document: dict[str, Any] = {
        "schema": SCHEMA,
        "state": "prospectively-sealed-not-materialized",
        "source": {
            "path": "tools/rust_v9_holdout_protocol.py",
            "sha256": file_digest(Path(__file__).resolve()),
            "derivation": "open independent additive correction of public v8",
        },
        "reference": {
            "implementation": "CPython",
            "version": "3.14.6",
            "unicode_version": "16.0.0",
            "enforced_worker_locale": "C",
        },
        "seal": {
            "algorithm": "sha256",
            "opening_bytes": 32,
            "opening_mode": "0600",
            "opening_path": OPENING_PATH,
            "opening_sha256": opening_sha256,
            "isolation": "procedural-same-unix-user-not-security-boundary",
            "case_derivation": "domain-separated-HMAC-SHA256-drives-real-regex-semantics",
        },
        "layout": {
            "apis": list(APIS),
            "workloads": list(WORKLOADS),
            "cases": CASE_COUNT,
            "cases_per_api": CASES_PER_API,
            "cases_per_cell": CASES_PER_CELL,
            "applicability": applicability,
            "semantic_identity": "keyed-pattern-subject-captures-flags-window-and-replacement",
            "mutable_buffer_transport": "actual-bytearray-or-memoryview-created-before-timing",
        },
        "trials": {
            "minimum_candidates": 3,
            "required_independent_native_families": ["vm", "rust", "zig"],
            "paired_rounds": PAIRED_ROUNDS,
            "warmups": WARMUPS,
            "operations_per_sample": OPERATIONS_PER_SAMPLE,
            "case_timeout_seconds": CASE_TIMEOUT_SECONDS,
            "timeout_method": "absolute-monotonic-whole-response-deadline",
            "order_seed": ORDER_SEED,
            "order_method": "seeded-counterbalanced-rotating-latin-square",
            "timed_operation": "actual-public-call-only-no-normalization-or-wire-decoding",
            "compiled_lifecycle": "retained-precompiled-object-outside-timed-operation",
            "four_engine_timed_rows": CASE_COUNT * PAIRED_ROUNDS * 4,
            "four_engine_correctness_snapshots": CASE_COUNT * PAIRED_ROUNDS * 4 * 3,
        },
        "statistics": {
            "confidence": 0.95,
            "case_method": "paired-log-student-t-df30",
            "case_student_t_critical": STUDENT_T_DF30_975,
            "case_win_lower_bound": 1.0,
            "minimum_significant_wins": MINIMUM_WINS,
            "overall_method": "stratified-paired-whole-case-cluster-percentile-bootstrap",
            "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "overall_lower_bound": 1.5,
            "runtime_regression": "candidate_time > 1.2 * baseline_time",
        },
        "correctness": {
            "snapshots_per_timed_row": 3,
            "mismatches_allowed": 0,
            "timeouts_allowed": 0,
            "crashes_allowed": 0,
            "edge_checks": 223_198,
            "edge_categories": 49,
            "edge_runner_sha256": EDGE_RUNNER_SHA256,
            "edge_answer_sha256": EDGE_ANSWER_SHA256,
            "grammar_checks": 20_480,
            "object_checks": 14_783,
            "unicode_checks": 4_494_555,
            "observable_checks": 479,
            "native_binder_checks": 34,
            "deep_contract_checks": 393,
            "deep_contract_source_sha256": DEEP_SOURCE_SHA256,
            "deep_contract_fixture_sha256": DEEP_FIXTURE_SHA256,
            "deep_contract_answer_sha256": DEEP_ANSWER_SHA256,
            "minimum_current_campaign_stages": 22,
            "goal_sha256": GOAL_SHA256,
            "named_private_waivers": [
                "PRIVATE-CACHE-LAYOUT",
                "PRIVATE-DEBUG-TEXT",
            ],
        },
        "independence": {
            "candidate_delegation": "forbidden",
            "external_regex_engines": "forbidden",
            "candidate_worker_python_regex": "forbidden",
            "native_identity": "edge-campaign-live-audit-and-live-mappings-all-exactly-bound",
            "minimum_distinct_semantic_pipelines": 3,
            "required_owned_native_artifacts": 5,
            "previous_holdout_access": "forbidden",
            "benchmark_detection": "forbidden",
            "memory_instrumentation": "separate-worker-tracemalloc-imports-re",
        },
        "memory": {
            "cases": MEMORY_CASES,
            "cases_per_cell": len(MEMORY_INDICES),
            "python_peak": "tracemalloc-python-allocations-only",
            "process_current": "procfs-resident-bytes",
            "process_peak": "whole-process-peak-resident-bytes",
            "boundary_cost": "included-in-actual-public-operation",
        },
        "history": {
            "original_v7_cases": 10_312,
            "original_v7_status": "preserved-not-accessed-by-v9",
            "v8_status": "preserved-sealed-not-accessed-by-v9",
            "v9_results": "NOT MEASURED",
            "combined_results": "NOT MEASURED",
        },
    }
    document["binding_sha256"] = manifest_binding(document)
    return document


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    require(path.resolve() == MANIFEST_PATH.resolve(), "v9 manifest path is not frozen")
    try:
        with path.open("rb") as source:
            document = json.load(source)
    except (OSError, ValueError, UnicodeError) as error:
        raise ProtocolError("cannot load the frozen v9 public manifest") from error
    require(isinstance(document, dict), "v9 manifest must be a JSON object")
    return document


def validate_manifest(document: dict[str, Any]) -> None:
    require(
        platform.python_implementation() == "CPython"
        and tuple(sys.version_info[:3]) == (3, 14, 6),
        "v9 requires the exact pinned CPython 3.14.6",
    )
    require(unicodedata.unidata_version == "16.0.0", "pinned Unicode data changed")
    seal = document.get("seal")
    require(isinstance(seal, dict), "v9 opening commitment is missing")
    opening_sha256 = seal.get("opening_sha256")
    require(is_digest(opening_sha256), "v9 opening commitment is invalid")
    expected = make_manifest(opening_sha256)
    require(
        hmac.compare_digest(canonical_bytes(document), canonical_bytes(expected)),
        "the complete v9 source, layout, controls, or prospective commitment changed",
    )
    require(
        hmac.compare_digest(document["binding_sha256"], manifest_binding(document)),
        "the exact v9 manifest binding is invalid",
    )
    require(
        CASE_COUNT == len(APIS) * len(WORKLOADS) * CASES_PER_CELL
        and MINIMUM_WINS == 14_746
        and MEMORY_CASES == 1_536,
        "a published v9 case, win, or memory denominator is false",
    )


def case_descriptors() -> list[dict[str, Any]]:
    """Public coordinates only: no hidden seed, pattern, or subject."""
    result: list[dict[str, Any]] = []
    for api in APIS:
        for workload in WORKLOADS:
            for index in range(CASES_PER_CELL):
                row: dict[str, Any] = {
                    "schema": CASE_SCHEMA,
                    "id": f"v9.{api}.{workload}.{index:03d}",
                    "api": api,
                    "workload": workload,
                    "index": index,
                }
                if api in NORMAL_APIS:
                    row.update(
                        surface=("module", "compiled")[index & 1],
                        input=("str", "bytes")[(index >> 1) & 1],
                        outcome=("hit", "miss")[(index >> 2) & 1],
                        variant=index >> 3,
                    )
                elif api == "compile":
                    row.update(
                        surface="module",
                        input=("str", "bytes")[(index >> 1) & 1],
                        lifecycle=("cold-cache", "warm-cache")[index & 1],
                        variant=index >> 2,
                    )
                elif api == "escape":
                    row.update(
                        surface="module",
                        input=("str", "bytes")[(index >> 1) & 1],
                        special_density=("ordinary", "regex-special")[index & 1],
                        variant=index >> 2,
                    )
                elif api == "match-surface":
                    row.update(
                        surface=("module", "compiled")[index & 1],
                        input=("str", "bytes")[(index >> 1) & 1],
                        outcome="hit",
                        capture=("numbered", "named", "optional", "multiple")[
                            (index >> 2) & 3
                        ],
                        variant=index >> 4,
                    )
                else:
                    row.update(
                        surface="compiled-pattern-scanner",
                        input=("str", "bytes")[(index >> 1) & 1],
                        scanner_method=("search", "match")[index & 1],
                        progression=("ordinary", "zero-width")[(index >> 2) & 1],
                        variant=index >> 3,
                    )
                result.append(row)
    return result


def validate_descriptors(rows: list[dict[str, Any]]) -> None:
    require(len(rows) == CASE_COUNT, "v9 must contain exactly 24,576 cases")
    identifiers: set[str] = set()
    cells: collections.Counter[tuple[str, str]] = collections.Counter()
    factors: collections.Counter[tuple[Any, ...]] = collections.Counter()
    for row in rows:
        require(isinstance(row, dict) and row.get("schema") == CASE_SCHEMA, "invalid case")
        api = row.get("api")
        workload = row.get("workload")
        index = row.get("index")
        identifier = row.get("id")
        require(api in APIS and workload in WORKLOADS, "unknown frozen case stratum")
        require(isinstance(index, int) and 0 <= index < CASES_PER_CELL, "invalid case index")
        require(
            identifier == f"v9.{api}.{workload}.{index:03d}"
            and identifier not in identifiers,
            "a v9 case is substituted, missing, or duplicated",
        )
        identifiers.add(identifier)
        cells[(api, workload)] += 1
        if api in NORMAL_APIS:
            key = (api, workload, row.get("surface"), row.get("input"), row.get("outcome"))
            require(
                row.get("variant") == index >> 3,
                "the genuine matching variant coordinate changed",
            )
        elif api == "compile":
            key = (api, workload, row.get("surface"), row.get("input"), row.get("lifecycle"))
            require(row.get("variant") == index >> 2, "compile variant changed")
        elif api == "escape":
            key = (
                api,
                workload,
                row.get("surface"),
                row.get("input"),
                row.get("special_density"),
            )
            require(row.get("variant") == index >> 2, "escape variant changed")
        elif api == "match-surface":
            require(row.get("outcome") == "hit", "a missing match cannot be inspected")
            key = (api, workload, row.get("surface"), row.get("input"), row.get("capture"))
            require(row.get("variant") == index >> 4, "match-object variant changed")
        else:
            require(
                row.get("surface") == "compiled-pattern-scanner",
                "scanner is not a genuine compiled-pattern scanner",
            )
            key = (
                api,
                workload,
                row.get("input"),
                row.get("scanner_method"),
                row.get("progression"),
            )
            require(row.get("variant") == index >> 3, "scanner variant changed")
        factors[key] += 1
    require(
        len(cells) == len(APIS) * len(WORKLOADS)
        and set(cells.values()) == {CASES_PER_CELL},
        "v9 API/workload weights are incomplete or unequal",
    )
    for (api, _workload, *_rest), count in factors.items():
        expected = (
            32
            if api in NORMAL_APIS or api == "scanner"
            else 16
            if api == "match-surface"
            else 64
        )
        require(count == expected, f"genuine {api} lifecycle or subject factors are unbalanced")


def encode_subject(value: str | bytes, source_kind: str) -> str | bytes | dict[str, str]:
    if source_kind in ("bytearray", "memoryview"):
        require(isinstance(value, bytes), "mutable subject has no real byte payload")
        return {"schema": BUFFER_SCHEMA, "kind": source_kind, "hex": value.hex()}
    require(
        source_kind in ("str", "bytes")
        and isinstance(value, str if source_kind == "str" else bytes),
        "the actual text or bytes subject has the wrong type",
    )
    return value


def decode_subject(
    value: str | bytes | dict[str, str], source_kind: str
) -> str | bytes | bytearray | memoryview:
    if source_kind in ("bytearray", "memoryview"):
        require(
            isinstance(value, dict)
            and set(value) == {"schema", "kind", "hex"}
            and value.get("schema") == BUFFER_SCHEMA
            and value.get("kind") == source_kind
            and isinstance(value.get("hex"), str),
            "the actual mutable buffer wire representation was substituted",
        )
        try:
            payload = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise ProtocolError("mutable buffer contains invalid exact bytes") from error
        return bytearray(payload) if source_kind == "bytearray" else memoryview(payload)
    require(
        source_kind in ("str", "bytes")
        and isinstance(value, str if source_kind == "str" else bytes),
        "wire subject is not the promised actual Python type",
    )
    return value


def _keyed_stream(opening: bytes, identifier: str, synthetic: bool) -> bytes:
    require(isinstance(opening, bytes) and len(opening) == 32, "invalid case opening")
    require(isinstance(identifier, str), "case has no frozen public identity")
    if synthetic:
        require(
            identifier.startswith("synthetic.v9.")
            and hmac.compare_digest(opening, SYNTHETIC_OPENING),
            "synthetic generation cannot use a final case or a nonpublic opening",
        )
        domain = b"rebar-v9-public-synthetic-semantic-case\x00"
    else:
        require(identifier.startswith("v9."), "real case escaped its frozen final domain")
        domain = b"rebar-v9-unseen-real-semantic-case\x00"
    identity = identifier.encode("utf-8")
    return b"".join(
        hmac.new(opening, domain + identity + bytes((block,)), hashlib.sha256).digest()
        for block in range(3)
    )


def _letters(stream: bytes, offset: int, length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join(alphabet[stream[(offset + index) % len(stream)] % 26] for index in range(length))


def _digits(stream: bytes, offset: int, length: int) -> str:
    return "".join(str(stream[(offset + index) % len(stream)] % 10) for index in range(length))


def materialize_case(
    descriptor: dict[str, Any], opening: bytes, *, synthetic: bool = False
) -> dict[str, Any]:
    """Derive genuine unknown matching behavior, never a no-op comment."""
    require(descriptor.get("schema") == CASE_SCHEMA, "case is outside the frozen schema")
    identifier = descriptor.get("id")
    stream = _keyed_stream(opening, identifier, synthetic)
    api = descriptor.get("api")
    workload = descriptor.get("workload")
    variant = descriptor.get("variant")
    require(api in APIS and workload in WORKLOADS, "case escaped its public stratum")
    require(isinstance(variant, int) and variant >= 0, "case variant is invalid")
    word = _letters(stream, 0, 8 + stream[20] % 7)
    second = _letters(stream, 24, 4 + stream[21] % 5)
    digits = _digits(stream, 40, 2 + stream[22] % 5)
    group = "g" + _letters(stream, 52, 8)
    other_group = "n" + _letters(stream, 63, 8)
    miss = "!" + _letters(stream, 74, 7) + "!"

    if workload == "literal-and-long-prefix":
        pattern = word
        hit = word
    elif workload == "character-class-and-unicode":
        letter_count = 2 + stream[25] % 7
        number_count = 2 + stream[26] % 5
        characters = _letters(stream, 4, letter_count)
        if descriptor.get("input") == "str" and stream[27] & 1:
            characters = characters[:-1] + ("é", "ø", "ß", "Ω")[stream[28] % 4]
            pattern = rf"[^\W\d_]{{{letter_count}}}[0-9]{{{number_count}}}"
        else:
            pattern = rf"[A-Za-z]{{{letter_count}}}[0-9]{{{number_count}}}"
        hit = characters + _digits(stream, 32, number_count)
    elif workload == "anchors-boundaries-and-windows":
        hit = word + digits
        pattern = rf"\A{word}{digits}\Z"
    elif workload == "greedy-lazy-atomic-and-possessive":
        atom = _letters(stream, 5, 2 + stream[29] % 3)
        repeats = 1 + stream[30] % 4
        alternatives = (
            rf"(?:{atom}){{{repeats}}}",
            rf"(?:{atom}){{{repeats}}}?",
            rf"(?>{atom}){{{repeats}}}",
            rf"(?:{atom}){{{repeats}}}+",
        )
        pattern = alternatives[stream[31] % len(alternatives)]
        hit = atom * repeats
    elif workload == "alternation-groups-and-backreferences":
        pattern = (
            rf"(?P<{group}>{word}|{second})"
            rf"(?P<{other_group}>[0-9]{{{len(digits)}}})(?P={group})"
        )
        hit = word + digits + word
    elif workload == "lookaround-and-zero-width":
        core = word + digits
        if api in {"search", "findall", "finditer", "split", "sub", "subn", "scanner"}:
            lead = _letters(stream, 70, 2)
            tail = _letters(stream, 72, 2)
            pattern = rf"(?<={lead}){core}(?={tail})"
            hit = lead + core + tail
        else:
            pattern = rf"(?={core})({core})"
            hit = core
    elif workload == "replacement-split-and-result-density":
        pattern = rf"(?P<{group}>{word})"
        repeat = 1 + stream[35] % 4
        hit = (
            ",".join([word] * repeat)
            if api in {"findall", "finditer", "split", "sub", "subn", "scanner"}
            else word
        )
    else:
        shape = stream[36] % 4
        if shape == 0:
            pattern = rf"(?P<{group}>{word})=(?P<{other_group}>{digits})"
            hit = word + "=" + digits
        elif shape == 1:
            pattern = rf"{word}/{second}/{digits}"
            hit = word + "/" + second + "/" + digits
        elif shape == 2:
            pattern = rf"{word}@{second}\.test"
            hit = word + "@" + second + ".test"
        else:
            pattern = rf"{word}-{digits}-{second}"
            hit = word + "-" + digits + "-" + second

    if api == "escape":
        subject = (
            "[" + word + "]+.(" + second + ")?{" + digits + "}"
            if descriptor.get("special_density") == "regex-special"
            else word + "_" + second + "_" + digits
        )
    elif api == "match-surface":
        pattern = (
            rf"(?P<{group}>{word})(?P<{other_group}>[0-9]{{{len(digits)}}})"
            rf"(?P<optional{_letters(stream, 81, 4)}>[A-Z]{{1,3}})?"
        )
        subject = word + digits
        if stream[43] & 1:
            subject += _letters(stream, 86, 1 + stream[44] % 3).upper()
    elif api == "scanner" and descriptor.get("progression") == "zero-width":
        letter = _letters(stream, 19, 1)
        pattern = rf"(?={letter})"
        subject = letter * (1 + stream[45] % 6)
    else:
        subject = hit if descriptor.get("outcome", "hit") == "hit" else miss

    is_bytes = descriptor.get("input") == "bytes"
    if is_bytes:
        pattern = pattern.encode("ascii")
        subject = subject.encode("ascii")
    flags = (2 if stream[46] & 1 else 0) | (8 if stream[47] & 1 else 0)
    source_kind = (
        ("bytes", "bytearray", "memoryview")[stream[48] % 3]
        if is_bytes and api not in {"compile", "escape"}
        else "bytes"
        if is_bytes
        else "str"
    )
    case: dict[str, Any] = {
        **descriptor,
        "pattern": pattern,
        "subject": subject,
        "source_kind": source_kind,
        "flags": flags,
        "replacement": (
            (b"<" + word.encode("ascii") + b"-\\g<0>>")
            if is_bytes
            else "<" + word + r"-\g<0>>"
        ),
        "callback": api in {"sub", "subn"} and bool(stream[49] & 1),
        "count": stream[50] % 5,
        "maxsplit": stream[51] % 5,
    }
    if (
        api in {"search", "match", "fullmatch", "findall", "finditer"}
        and descriptor.get("surface") == "compiled"
        and workload != "anchors-boundaries-and-windows"
        and stream[53] & 1
    ):
        prefix = _letters(stream, 54, 1 + stream[55] % 4)
        suffix = _letters(stream, 60, 1 + stream[61] % 4)
        prefix_value = prefix.encode("ascii") if is_bytes else prefix
        suffix_value = suffix.encode("ascii") if is_bytes else suffix
        case["subject"] = prefix_value + subject + suffix_value
        case["window"] = (len(prefix_value), len(prefix_value) + len(subject))
    case["subject"] = encode_subject(case["subject"], source_kind)
    require(len(subject) <= 8192, "keyed subject exceeds its fixed safety limit")
    return case


def counterbalanced_order(
    modules: tuple[str, ...], identifier: str, round_index: int, seed: int
) -> tuple[str, ...]:
    require(modules and modules[0] == "re", "the genuine Python baseline is missing")
    require(len(modules) == len(set(modules)), "an isolated engine was duplicated")
    require(0 <= round_index < PAIRED_ROUNDS, "round escaped the frozen schedule")
    digest = hashlib.sha256(
        f"rebar-v9-balanced-order:{seed}:{identifier}".encode("utf-8")
    ).digest()
    order = list(modules)
    random.Random(int.from_bytes(digest[:16], "big")).shuffle(order)
    start = (int.from_bytes(digest[16:24], "big") + round_index) % len(order)
    return tuple(order[start:] + order[:start])


def case_confidence(logs: list[float]) -> tuple[float, float]:
    require(len(logs) == PAIRED_ROUNDS, "a paired case has missing rounds")
    require(all(math.isfinite(value) for value in logs), "paired log ratio is nonfinite")
    mean = statistics.fmean(logs)
    spread = STUDENT_T_DF30_975 * statistics.stdev(logs) / math.sqrt(PAIRED_ROUNDS)
    low, high = math.exp(mean - spread), math.exp(mean + spread)
    require(math.isfinite(low) and math.isfinite(high), "case confidence is nonfinite")
    return low, high


def percentile(values: list[float], quantile: float) -> float:
    require(bool(values) and 0.0 <= quantile <= 1.0, "invalid bootstrap percentile")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def bootstrap_clusters(
    cells: list[list[float]], *, seed: int, draws: int, per_cell: int
) -> tuple[float, float]:
    require(bool(cells) and draws > 0 and per_cell > 0, "bootstrap has no exact strata")
    require(all(len(cell) == per_cell for cell in cells), "bootstrap cell is incomplete")
    require(
        all(math.isfinite(value) for cell in cells for value in cell),
        "bootstrap contains a nonfinite paired case",
    )
    generator = random.Random(seed)
    denominator = len(cells) * per_cell
    samples: list[float] = []
    for _ in range(draws):
        total = 0.0
        for cell in cells:
            total += sum(cell[generator.randrange(per_cell)] for _ in range(per_cell))
        value = math.exp(total / denominator)
        require(math.isfinite(value), "bootstrap produced a nonfinite speed")
        samples.append(value)
    return percentile(samples, 0.025), percentile(samples, 0.975)


def stratified_bootstrap(
    cells: dict[tuple[str, str], list[float]], seed: int
) -> tuple[float, float]:
    require(
        set(cells) == {(api, workload) for api in APIS for workload in WORKLOADS},
        "bootstrap omitted or substituted a frozen workload",
    )
    return bootstrap_clusters(
        [cells[(api, workload)] for api in APIS for workload in WORKLOADS],
        seed=seed,
        draws=BOOTSTRAP_DRAWS,
        per_cell=CASES_PER_CELL,
    )


def is_significant_win(lower: float) -> bool:
    require(math.isfinite(lower) and lower > 0, "invalid case confidence")
    return lower > 1.0


def is_runtime_regression(speedup: float) -> bool:
    require(math.isfinite(speedup) and speedup > 0, "invalid runtime speedup")
    return speedup < REGRESSION_THRESHOLD


def read_json_document(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rb") as source:
                payload = source.read()
        else:
            with path.open("rb") as source:
                payload = source.read()
        document = json.loads(payload)
    except (OSError, UnicodeError, ValueError) as error:
        raise ProtocolError(f"cannot decode {label}") from error
    require(isinstance(document, dict), f"{label} is not a JSON object")
    return document, payload


def validate_modules(modules: tuple[str, ...]) -> None:
    require(bool(modules) and modules[0] == "re", "stdlib baseline was substituted")
    require(len(modules) == len(set(modules)), "an engine is missing or repeated")
    require(len(modules) >= 4, "at least three full engines are required")
    require(
        all(module in FAMILY_BY_MODULE for module in modules[1:]),
        "candidate is not one of the owned production implementations",
    )
    selected = {FAMILY_BY_MODULE[module] for module in modules[1:]}
    require(
        {"vm", "rust", "zig"} <= selected,
        "the three separately implemented VM, Rust, and Zig engines are mandatory",
    )


def validate_candidate_source(path: Path) -> None:
    candidates = (ROOT / "candidates").resolve()
    path = path.resolve()
    require(path.is_file() and path.is_relative_to(candidates), "source escaped production")
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as error:
        raise ProtocolError("candidate source is not auditable Python") from error
    for node in ast.walk(tree):
        names: list[str | None]
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module]
        else:
            continue
        for name in names:
            require(
                not isinstance(name, str) or name.split(".", 1)[0] not in BANNED_ENGINES,
                "candidate statically delegates to a prohibited regex engine",
            )


def verify_edge_proofs(
    modules: tuple[str, ...], paths: list[Path]
) -> dict[str, dict[str, Any]]:
    require(len(paths) == len(modules) - 1, "every candidate requires an edge proof")
    root = (ROOT / "candidates").resolve()
    proof_root = (root / "evidence").resolve()
    expected_modules = set(modules[1:])
    result: dict[str, dict[str, Any]] = {}
    for given in paths:
        path = given.resolve()
        require(path.is_file() and path.is_relative_to(proof_root), "edge proof escaped evidence")
        report, payload = read_json_document(path, "complete frozen compatibility proof")
        module = report.get("module")
        require(
            module in expected_modules and module not in result,
            "candidate edge proof is missing, reused, or substituted",
        )
        require(
            report.get("schema") == EDGE_SCHEMA
            and report.get("python") == "3.14.6"
            and report.get("unicode") == "16.0.0"
            and report.get("locale") == "C"
            and report.get("failed") == 0
            and report.get("correctness_checks") == 223_198,
            "candidate does not pass the pinned complete correctness oracle",
        )
        categories = report.get("categories")
        require(
            isinstance(categories, dict)
            and len(categories) == 49
            and all(isinstance(count, int) for count in categories.values())
            and sum(categories.values()) == 223_198,
            "candidate removed a frozen correctness category",
        )
        require(
            report.get("expected_sha256")
            == report.get("actual_sha256")
            == EDGE_ANSWER_SHA256,
            "candidate does not reproduce every frozen Python answer",
        )
        require(
            report.get("performance") == "NOT MEASURED"
            and report.get("holdout") == "NOT ACCESSED",
            "candidate proof is not performance blind",
        )
        records = report.get("candidate_artifacts")
        require(isinstance(records, list), "candidate native identities are absent")
        artifacts: dict[str, dict[str, str]] = {}
        for record in records:
            require(
                isinstance(record, dict)
                and set(record) == {"role", "path", "sha256"},
                "candidate artifact identity fields were modified",
            )
            role = record["role"]
            require(
                role in ARTIFACT_ROLES[module] and role not in artifacts,
                "candidate artifact role is duplicated or foreign",
            )
            raw = record["path"]
            require(isinstance(raw, str) and is_digest(record["sha256"]), "invalid artifact")
            candidate_path = Path(raw)
            resolved = (
                candidate_path.resolve()
                if candidate_path.is_absolute()
                else (ROOT / candidate_path).resolve()
            )
            require(
                resolved.is_file() and resolved.is_relative_to(root),
                "candidate artifact escaped its source tree",
            )
            require(
                hmac.compare_digest(file_digest(resolved), record["sha256"]),
                "candidate source or native code changed after qualification",
            )
            if role == "public-python":
                require(
                    resolved == (root / f"{module.rsplit('.', 1)[-1]}.py").resolve(),
                    "candidate Python source belongs to a different engine",
                )
                validate_candidate_source(resolved)
            artifacts[role] = {
                "path": str(resolved),
                "sha256": record["sha256"],
            }
        require(
            set(artifacts) == ARTIFACT_ROLES[module],
            "a qualified source, bridge, or native engine is missing",
        )
        result[module] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "artifacts": artifacts,
        }
    require(set(result) == expected_modules, "not every independent engine was qualified")
    return result


def _record_artifacts(value: object, output: list[dict[str, Any]], depth: int = 0) -> None:
    require(depth <= 16, "native evidence exceeds safe nesting")
    if isinstance(value, dict):
        if (
            isinstance(value.get("role"), str)
            and is_digest(value.get("sha256"))
            and isinstance(value.get("path", value.get("file")), str)
        ):
            output.append(value)
        for item in value.values():
            if isinstance(item, (dict, list)):
                _record_artifacts(item, output, depth + 1)
    elif isinstance(value, list):
        require(len(value) <= 100_000, "native proof exceeds safe bounds")
        for item in value:
            if isinstance(item, (dict, list)):
                _record_artifacts(item, output, depth + 1)


def _matches_current_artifacts(
    records: list[dict[str, Any]],
    expected: dict[str, dict[str, str]],
    label: str,
) -> None:
    seen: dict[str, dict[str, str]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        role = record.get("role")
        if role not in expected:
            continue
        raw_path = record.get("path", record.get("file"))
        if not isinstance(raw_path, str):
            continue
        path = Path(raw_path)
        resolved = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
        if (
            str(resolved) == expected[role]["path"]
            and hmac.compare_digest(record["sha256"], expected[role]["sha256"])
        ):
            seen[role] = expected[role]
    require(
        set(seen) == set(expected),
        f"{label} is stale or does not bind every exact current candidate artifact",
    )


def verify_campaigns(
    modules: tuple[str, ...],
    paths: list[Path],
    edges: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    require(len(paths) == len(modules) - 1, "every engine requires a live campaign")
    candidate_root = (ROOT / "candidates/evidence").resolve()
    result: dict[str, dict[str, Any]] = {}
    for given in paths:
        path = given.resolve()
        require(
            path.is_file() and path.is_relative_to(candidate_root),
            "current campaign escaped candidate evidence",
        )
        report, payload = read_json_document(path, "current 22-stage campaign")
        module = report.get("candidate")
        require(module in modules[1:] and module not in result, "campaign candidate mismatch")
        require(
            report.get("schema")
            in {
                "rebar-rust-campaign-gate-v1",
                "rebar-v9-candidate-campaign-v1",
                "rebar-independent-candidate-campaign-v1",
            },
            "current campaign schema is not approved",
        )
        require(
            report.get("pinned_cpython") == "3.14.6"
            and report.get("mode") == "sealed-practice-only"
            and report.get("passed") is True
            and report.get("holdout_accessed") is False
            and report.get("performance") == "NOT MEASURED"
            and report.get("timing_performed") is False,
            "candidate campaign is failing, stale, or performance-contaminated",
        )
        goal = report.get("goal")
        require(
            isinstance(goal, dict)
            and goal.get("passed") is True
            and goal.get("actual_sha256") == goal.get("expected_sha256") == GOAL_SHA256,
            "campaign changed the immutable project objective",
        )
        steps = report.get("steps")
        require(
            isinstance(steps, list)
            and len(steps) >= 22
            and all(isinstance(step, dict) and step.get("passed") is True for step in steps),
            "candidate does not pass every one of at least 22 required stages",
        )
        names = {step.get("name") for step in steps}
        require(
            REQUIRED_CAMPAIGN_STEPS <= names,
            "current campaign removed a public correctness or safety obligation",
        )
        unicode_steps = [step for step in steps if step.get("name") == "full-unicode-plane"]
        require(
            len(unicode_steps) == 1
            and unicode_steps[0].get("expected_checks") == 4_494_555,
            "current campaign removed exact full-Unicode coverage",
        )
        exclusions = report.get("excluded_steps")
        require(
            isinstance(exclusions, list)
            and {
                entry.get("name") for entry in exclusions if isinstance(entry, dict)
            }
            == EXCLUDED_PERFORMANCE_STEPS,
            "current campaign reads or omits a frozen performance exclusion",
        )
        records: list[dict[str, Any]] = []
        _record_artifacts(report.get("candidate_artifacts"), records)
        _record_artifacts(report.get("native_artifacts"), records)
        _record_artifacts(report.get("artifact_binding"), records)
        for step in steps:
            raw = step.get("artifact")
            if not isinstance(raw, str):
                continue
            artifact_path = Path(raw)
            resolved = (
                artifact_path.resolve()
                if artifact_path.is_absolute()
                else (ROOT / artifact_path).resolve()
            )
            require(
                resolved.is_file() and resolved.is_relative_to(candidate_root),
                "campaign step reads an unapproved or historical fixture",
            )
            expected_digest = step.get("artifact_sha256")
            require(
                is_digest(expected_digest)
                and hmac.compare_digest(file_digest(resolved), expected_digest),
                "current campaign step evidence was replaced",
            )
            nested, _nested_payload = read_json_document(resolved, "current campaign step")
            _record_artifacts(nested, records)
        _matches_current_artifacts(
            records,
            edges[module]["artifacts"],
            f"22-stage {module} campaign",
        )
        result[module] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "stages": len(steps),
            "artifacts": edges[module]["artifacts"],
        }
    require(set(result) == set(modules[1:]), "a candidate has no live full campaign")
    return result


def verify_deep_contracts(
    modules: tuple[str, ...],
    paths: list[Path],
    edges: dict[str, dict[str, Any]],
) -> dict[str, dict[str, str]]:
    require(len(paths) == len(modules) - 1, "each candidate requires the public contract")
    suite = ROOT / "tools/rust_v8_deep_contract_oracle.py"
    require(
        suite.is_file() and hmac.compare_digest(file_digest(suite), DEEP_SOURCE_SHA256),
        "the separately frozen real-user contract has changed",
    )
    root = (ROOT / "candidates").resolve()
    result: dict[str, dict[str, str]] = {}
    for given in paths:
        path = given.resolve()
        require(path.is_file() and path.is_relative_to(root), "public proof escaped candidates")
        report, payload = read_json_document(path, "frozen 393-case public contract")
        require(
            report.get("schema") == DEEP_SCHEMA
            and report.get("status") == "PASS"
            and report.get("python") == "3.14.6"
            and report.get("checks") == 393
            and report.get("public_mismatch_count") == 0
            and report.get("public_mismatches") == []
            and report.get("fixture_sha256") == DEEP_FIXTURE_SHA256
            and report.get("suite_sha256") == DEEP_SOURCE_SHA256
            and report.get("reference_a_sha256")
            == report.get("reference_b_sha256")
            == report.get("candidate_sha256")
            == DEEP_ANSWER_SHA256
            and report.get("performance") == "NOT MEASURED"
            and report.get("holdout") == "NOT ACCESSED",
            "candidate does not pass the exact current real-user contract",
        )
        native = report.get("native_artifacts")
        require(isinstance(native, list), "public contract omits actual native proof")
        sources = [
            item
            for item in native
            if isinstance(item, dict) and item.get("role") == "public-python"
        ]
        require(len(sources) == 1, "public contract does not identify one actual engine")
        matching = [
            module
            for module in modules[1:]
            if hmac.compare_digest(
                str(sources[0].get("sha256", "")),
                edges[module]["artifacts"]["public-python"]["sha256"],
            )
        ]
        require(len(matching) == 1 and matching[0] not in result, "public proof reused")
        module = matching[0]
        _matches_current_artifacts(native, edges[module]["artifacts"], "deep public contract")
        result[module] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    require(set(result) == set(modules[1:]), "one candidate lacks its full public contract")
    return result


def verify_from_scratch_audit(
    given: Path,
    modules: tuple[str, ...],
    edges: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    expected_path = (ROOT / "candidates/audits/FROM-SCRATCH-AUDIT.json").resolve()
    path = given.resolve()
    require(path == expected_path and path.is_file(), "live native from-scratch audit missing")
    report, payload = read_json_document(path, "current all-family from-scratch audit")
    require(
        report.get("schema_version") == 1
        and report.get("audit") == "bounded-from-scratch-engine-provenance"
        and report.get("passed") is True
        and report.get("result") == "PASS"
        and report.get("minimum_required_independent_families") == 3
        and report.get("verified_core_family_count", 0) >= 3
        and report.get("verified_distinct_pipeline_count", 0) >= 3,
        "engines are not fully audited distinct from-scratch implementations",
    )
    scope = report.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("holdout_or_case_fixture_access") is False
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("mapped_binaries_hashed_against_static_elf") is True,
        "native audit accessed benchmarks or did not check real mapped ELF code",
    )
    lock = report.get("manifest_provenance")
    require(
        isinstance(lock, dict)
        and lock.get("passed") is True
        and lock.get("rust_third_party_dependency_count") == 0,
        "Rust uses an unapproved external implementation or lockfile",
    )
    families = report.get("families")
    native_elf = report.get("native_elf_provenance")
    mapping = report.get("runtime_native_mapping_provenance")
    require(
        isinstance(families, dict)
        and isinstance(native_elf, dict)
        and native_elf.get("passed") is True
        and native_elf.get("expected_binary_count")
        == native_elf.get("audited_binary_count")
        == 5
        and isinstance(mapping, dict)
        and mapping.get("passed") is True,
        "all five owned native binaries are not currently verified",
    )
    elf_families = native_elf.get("families")
    mapping_families = mapping.get("families")
    require(
        isinstance(elf_families, dict) and isinstance(mapping_families, dict),
        "audit lacks per-family current ELF and runtime mapping records",
    )
    signatures: set[tuple[str, str, str]] = set()
    verified_native = 0
    role_map = {"bridge": "native-bridge", "engine": "native-engine", "native": "native-bridge"}
    for module in modules[1:]:
        family_name = FAMILY_BY_MODULE[module]
        family = families.get(family_name)
        require(
            isinstance(family, dict) and family.get("passed") is True,
            "selected candidate has no current independent native audit",
        )
        source = family.get("python_source")
        expected_source = edges[module]["artifacts"]["public-python"]
        require(
            isinstance(source, dict)
            and source.get("passed") is True
            and isinstance(source.get("file"), str)
            and str((ROOT / source["file"]).resolve()) == expected_source["path"]
            and hmac.compare_digest(str(source.get("sha256", "")), expected_source["sha256"]),
            "from-scratch audit used a stale candidate Python source",
        )
        pipeline = family.get("owned_pipeline")
        require(
            isinstance(pipeline, dict)
            and pipeline.get("passed") is True
            and pipeline.get("issues") == [],
            "selected semantic parser, compiler, or executor is not owned",
        )
        signature = tuple(str(pipeline.get(name, "")) for name in ("parser", "compiler", "executor"))
        require(all(signature) and signature not in signatures, "candidate reuses another engine")
        signatures.add(signature)
        for native_source in family.get("native_sources", []):
            require(
                isinstance(native_source, dict)
                and native_source.get("passed") is True
                and native_source.get("issues") == []
                and isinstance(native_source.get("file"), str)
                and is_digest(native_source.get("sha256")),
                "owned native parser or bridge source is unaudited",
            )
            source_path = (ROOT / native_source["file"]).resolve()
            require(
                source_path.is_file()
                and source_path.is_relative_to((ROOT / "candidates").resolve())
                and hmac.compare_digest(file_digest(source_path), native_source["sha256"]),
                "a native parser or compiler changed after its audit",
            )
        if family_name == "ast":
            continue
        elf_family = elf_families.get(family_name)
        runtime = family.get("isolated_runtime")
        require(
            isinstance(elf_family, dict)
            and elf_family.get("passed") is True
            and isinstance(runtime, dict)
            and runtime.get("passed") is True,
            "candidate has no approved actual native ELF runtime",
        )
        files = elf_family.get("files")
        provenance = runtime.get("native_mapping_provenance")
        require(
            isinstance(files, dict)
            and isinstance(provenance, dict)
            and provenance.get("passed") is True,
            "current native ELF and actual process mapping are absent",
        )
        observed = provenance.get("observed_owned_mappings")
        require(
            isinstance(observed, list)
            and provenance.get("expected_owned_mapping_count")
            == provenance.get("observed_owned_mapping_count")
            == len(observed),
            "owned mapping count does not match the isolated worker",
        )
        for alias, file_record in files.items():
            require(
                alias in role_map and isinstance(file_record, dict),
                "unknown external native library entered a candidate",
            )
            role = role_map[alias]
            expected = edges[module]["artifacts"].get(role)
            require(expected is not None, "candidate edge proof omits audited native code")
            raw_path = file_record.get("file")
            require(
                isinstance(raw_path, str)
                and str((ROOT / raw_path).resolve()) == expected["path"]
                and hmac.compare_digest(str(file_record.get("sha256", "")), expected["sha256"])
                and file_record.get("forbidden_regex_symbols") == []
                and file_record.get("cross_candidate_symbols") == [],
                "live static ELF audit does not match the approved current engine",
            )
            matches = [
                row
                for row in observed
                if isinstance(row, dict)
                and row.get("role") == alias
                and row.get("file") == raw_path
                and hmac.compare_digest(str(row.get("sha256", "")), expected["sha256"])
                and row.get("matches_static_elf") is True
            ]
            require(len(matches) == 1, "audited native code is not actually mapped")
            verified_native += 1
    require(
        verified_native == 5 and len(signatures) >= 3,
        "the three selected distinct families do not own all five native engines",
    )
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "owned_native_artifacts": verified_native,
        "distinct_pipelines": len(signatures),
    }


def checked_evidence_path(path: Path, label: str, *, exists: bool) -> Path:
    root = EVIDENCE_ROOT.resolve()
    resolved = path.resolve()
    require(resolved.parent == root, f"{label} escaped exclusive v9 evidence")
    require(resolved.is_file() if exists else not resolved.exists(), f"invalid {label} path")
    return resolved


def verify_freeze(
    path: Path,
    document: dict[str, Any],
    modules: tuple[str, ...],
    edges: dict[str, dict[str, Any]],
    campaigns: dict[str, dict[str, Any]],
    contracts: dict[str, dict[str, str]],
    audit: dict[str, Any],
) -> dict[str, Any]:
    resolved = checked_evidence_path(path, "current candidate freeze", exists=True)
    freeze, payload = read_json_document(resolved, "one-use stopping-commit freeze")
    require(
        freeze.get("schema") == FREEZE_SCHEMA
        and freeze.get("protocol_binding_sha256") == document["binding_sha256"]
        and freeze.get("baseline") == "re"
        and freeze.get("from_scratch_audit_sha256") == audit["sha256"]
        and freeze.get("opening_read") is False
        and freeze.get("hidden_cases_generated") == 0
        and freeze.get("performance_measured") is False,
        "candidate selection is not prospectively and independently frozen",
    )
    commit = freeze.get("stopping_commit")
    require(
        isinstance(commit, str)
        and len(commit) in {40, 64}
        and all(letter in "0123456789abcdef" for letter in commit),
        "candidate selection has no complete immutable stopping commit",
    )
    rows = freeze.get("candidates")
    require(
        isinstance(rows, list) and len(rows) == len(modules) - 1,
        "stopping freeze omitted a complete independent candidate",
    )
    seen: set[str] = set()
    for row in rows:
        require(isinstance(row, dict), "invalid frozen engine")
        module = row.get("module")
        require(module in modules[1:] and module not in seen, "frozen engine duplicated")
        require(
            row.get("edge_sha256") == edges[module]["sha256"]
            and row.get("campaign_sha256") == campaigns[module]["sha256"]
            and row.get("deep_contract_sha256") == contracts[module]["sha256"]
            and row.get("artifacts") == edges[module]["artifacts"],
            "complete candidate evidence is stale or uses different native code",
        )
        seen.add(module)
    require(seen == set(modules[1:]), "one measured candidate was not frozen")
    return {
        "document": freeze,
        "path": str(resolved.relative_to(ROOT)),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


ISOLATED_WORKER = r'''
import _locale
import builtins
import hashlib
import importlib
import marshal
import os
import resource
import sys
import time

ROOT, NAME, KIND = sys.argv[1:]
BANNED = frozenset(("re", "_sre", "sre_compile", "sre_parse", "regex", "re2", "google_re2", "pcre", "pcre2", "hyperscan", "onig", "oniguruma"))
BUFFER_SCHEMA = "rebar-v9-exact-buffer-wire-v1"
OPERATIONS = 16
original_import = builtins.__import__

def send(value):
    payload = marshal.dumps(value)
    for part in (len(payload).to_bytes(8, "big"), payload):
        view = memoryview(part)
        while view:
            written = os.write(1, view)
            if written <= 0:
                raise RuntimeError("failed to send isolated response")
            view = view[written:]

def receive():
    header = bytearray()
    while len(header) < 8:
        block = os.read(0, 8 - len(header))
        if not block:
            return None
        header.extend(block)
    length = int.from_bytes(header, "big")
    if not 0 < length <= 4 * 1024 * 1024:
        raise RuntimeError("invalid isolated request length")
    payload = bytearray()
    while len(payload) < length:
        block = os.read(0, min(65536, length - len(payload)))
        if not block:
            raise RuntimeError("truncated isolated request")
        payload.extend(block)
    return marshal.loads(bytes(payload))

def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
    if isinstance(name, str) and name.split(".", 1)[0] in BANNED:
        raise ImportError("candidate cannot delegate to a built-in or external regex engine")
    return original_import(name, globals, locals, fromlist, level)

def loaded_native():
    result = {}
    prefix = os.path.realpath(os.path.join(ROOT, "candidates")) + os.sep
    with original_import("builtins").open("/proc/self/maps", "r", encoding="utf-8", errors="surrogateescape") as source:
        for line in source:
            fields = line.split(maxsplit=5)
            if len(fields) != 6:
                continue
            path = fields[5].strip()
            if path.startswith(prefix) and ".so" in os.path.basename(path) and not path.endswith(" (deleted)"):
                if path not in result:
                    digest = hashlib.sha256()
                    with original_import("builtins").open(path, "rb") as item:
                        for block in iter(lambda: item.read(1048576), b""):
                            digest.update(block)
                    result[path] = digest.hexdigest()
    return result

def clean_state(inspect_native=False):
    if NAME == "re" or KIND != "timing":
        return {"forbidden_loaded": [], "foreign_candidates": [], "external_regex_libraries": []}
    forbidden = sorted(name for name in sys.modules if name.split(".", 1)[0] in BANNED)
    foreign = sorted(name for name in sys.modules if name.startswith("candidates.") and name.endswith("_candidate") and name != NAME)
    external = []
    if inspect_native:
        with original_import("builtins").open("/proc/self/maps", "r", encoding="utf-8", errors="surrogateescape") as source:
            for line in source:
                fields = line.split(maxsplit=5)
                if len(fields) == 6:
                    path = fields[5].strip()
                    basename = os.path.basename(path).lower()
                    if any(word in basename for word in ("libpcre", "libregex", "libre2", "libhyperscan", "libonig")):
                        external.append(path)
    state = {"forbidden_loaded": forbidden, "foreign_candidates": foreign, "external_regex_libraries": sorted(set(external))}
    if any(state.values()):
        raise RuntimeError("candidate delegates to a prohibited regex implementation")
    return state

def actual_subject(value, kind):
    if kind in ("bytearray", "memoryview"):
        if not isinstance(value, dict) or set(value) != {"schema", "kind", "hex"} or value.get("schema") != BUFFER_SCHEMA or value.get("kind") != kind:
            raise RuntimeError("mutable subject was not transported with its exact real type")
        payload = bytes.fromhex(value["hex"])
        return bytearray(payload) if kind == "bytearray" else memoryview(payload)
    expected = bytes if kind == "bytes" else str if kind == "str" else None
    if expected is None or not isinstance(value, expected):
        raise RuntimeError("subject is not the actual frozen Python type")
    return value

def normalize(value, subject, depth=0):
    if depth > 12:
        raise RuntimeError("normalized observation exceeds its fixed depth")
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, bytes):
        return {"type": "bytes", "hex": value.hex(), "is_subject": value is subject}
    if isinstance(value, (list, tuple)):
        if len(value) > 128:
            raise RuntimeError("result exceeds its fixed observation bound")
        return {"type": type(value).__name__, "items": [normalize(item, subject, depth + 1) for item in value]}
    if isinstance(value, dict):
        return {"type": "dict", "items": [[str(key), normalize(item, subject, depth + 1)] for key, item in sorted(value.items())]}
    if hasattr(value, "span") and hasattr(value, "groups") and hasattr(value, "groupdict"):
        return {
            "type": "match",
            "span": normalize(value.span(), subject, depth + 1),
            "groups": normalize(value.groups(), subject, depth + 1),
            "groupdict": normalize(value.groupdict(), subject, depth + 1),
            "lastindex": value.lastindex,
            "lastgroup": value.lastgroup,
            "regs": normalize(value.regs, subject, depth + 1),
            "same_subject": value.string is subject,
            "whole_match_is_subject": value.group(0) is subject,
        }
    if hasattr(value, "pattern") and hasattr(value, "flags") and hasattr(value, "groupindex"):
        return {
            "type": "compiled-pattern",
            "pattern": normalize(value.pattern, subject, depth + 1),
            "flags": value.flags,
            "groups": value.groups,
            "groupindex": normalize(dict(value.groupindex), subject, depth + 1),
        }
    if hasattr(value, "__iter__"):
        iterator, items = iter(value), []
        for _ in range(129):
            try:
                item = next(iterator)
            except StopIteration:
                return {"type": "iterator", "items": items}
            if len(items) >= 128:
                raise RuntimeError("iterator exceeds its fixed observation bound")
            items.append(normalize(item, subject, depth + 1))
    raise RuntimeError("public result is not independently observable")

class PreparedCase:
    def __init__(self, module, case):
        self.module = module
        self.case = case
        self.api = case["api"]
        self.pattern = case["pattern"]
        self.flags = case["flags"]
        self.subject = actual_subject(case["subject"], case["source_kind"])
        self.events = []
        self.compiled = None
        if case.get("surface") == "compiled" or self.api == "scanner":
            self.compiled = module.compile(self.pattern, self.flags)
        if case.get("callback"):
            def callback(match):
                self.events.append((match.span(), match.group(0), match.lastindex))
                return b"X" if isinstance(self.subject, (bytes, bytearray, memoryview)) else "X"
            self.replacement = callback
        else:
            self.replacement = case.get("replacement")

    def before_operation(self):
        self.events.clear()
        if self.api == "compile":
            if self.case.get("lifecycle") == "cold-cache":
                self.module.purge()
            elif self.case.get("lifecycle") == "warm-cache":
                self.module.compile(self.pattern, self.flags)

    def perform(self):
        api, case, subject = self.api, self.case, self.subject
        if api == "compile":
            return self.module.compile(self.pattern, self.flags)
        if api == "escape":
            return self.module.escape(subject)
        if api == "match-surface":
            match = (
                self.compiled.search(subject)
                if case["surface"] == "compiled"
                else self.module.search(self.pattern, subject, self.flags)
            )
            if match is None:
                raise RuntimeError("match-object workload did not produce an actual match")
            mode = case["capture"]
            if mode == "numbered":
                return (match.group(0), match.span(), match.groups())
            if mode == "named":
                return (match.groupdict(), match.lastgroup, match.lastindex)
            if mode == "optional":
                return (match.groups(None), match.regs)
            return (match.group(0), match.groups(), match.groupdict(), match.regs)
        if api == "scanner":
            scanner = self.compiled.scanner(subject)
            method = getattr(scanner, case["scanner_method"])
            results = []
            for _ in range(64):
                match = method()
                if match is None:
                    return results
                results.append(match)
            raise RuntimeError("compiled scanner violated zero-width progression")
        if case["surface"] == "compiled":
            method = getattr(self.compiled, api)
            if api in ("sub", "subn"):
                return method(self.replacement, subject, case.get("count", 0))
            if api == "split":
                return method(subject, case.get("maxsplit", 0))
            if case.get("window") and api in ("search", "match", "fullmatch", "findall", "finditer"):
                return method(subject, case["window"][0], case["window"][1])
            return method(subject)
        method = getattr(self.module, api)
        if api in ("sub", "subn"):
            return method(self.pattern, self.replacement, subject, case.get("count", 0), self.flags)
        if api == "split":
            return method(self.pattern, subject, case.get("maxsplit", 0), self.flags)
        return method(self.pattern, subject, self.flags)

    def observe(self, value=None, error=None):
        if error is not None:
            return {
                "status": "error",
                "type": type(error).__module__ + "." + type(error).__qualname__,
                "message": str(error),
                "args": normalize(error.args, self.subject),
                "position": getattr(error, "pos", None),
                "line": getattr(error, "lineno", None),
                "column": getattr(error, "colno", None),
                "callbacks": normalize(self.events, self.subject),
            }
        return {
            "status": "ok",
            "result": normalize(value, self.subject),
            "callbacks": normalize(self.events, self.subject),
        }

    def untimed(self):
        self.before_operation()
        try:
            value = self.perform()
        except Exception as error:
            return self.observe(error=error)
        return self.observe(value=value)

def rss_bytes():
    with original_import("builtins").open("/proc/self/statm", "r", encoding="ascii") as source:
        return int(source.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")

try:
    current_locale = _locale.setlocale(_locale.LC_ALL, "C")
    if current_locale != "C" or _locale.setlocale(_locale.LC_ALL) != "C":
        raise RuntimeError("actual worker does not run in the frozen C locale")
    if NAME == "re":
        module = importlib.import_module("re")
    else:
        if any(name.split(".", 1)[0] in BANNED for name in sys.modules):
            raise RuntimeError("candidate startup already contains a regex engine")
        sys.path.insert(0, ROOT)
        builtins.__import__ = blocked_import
        module = importlib.import_module(NAME)
    source_path = os.path.realpath(getattr(module, "__file__", ""))
    source_sha256 = None
    if source_path:
        digest = hashlib.sha256()
        with original_import("builtins").open(source_path, "rb") as source:
            for chunk in iter(lambda: source.read(1048576), b""):
                digest.update(chunk)
        source_sha256 = digest.hexdigest()
    tracemalloc = None
    if KIND == "memory":
        builtins.__import__ = original_import
        tracemalloc = importlib.import_module("tracemalloc")
        if NAME != "re":
            builtins.__import__ = blocked_import
    state = clean_state(True)
    send({
        "kind": "ready",
        "module": NAME,
        "worker": KIND,
        "locale": _locale.setlocale(_locale.LC_ALL),
        "source": source_path,
        "source_sha256": source_sha256,
        "native": loaded_native(),
        **state,
    })
    prepared = None
    prepared_id = None
    while True:
        request = receive()
        if request is None or request.get("action") == "close":
            break
        action = request.get("action")
        if action == "prepare":
            prepared = PreparedCase(module, request["case"])
            prepared_id = request["case"]["id"]
            send({
                "kind": "prepared",
                "case": prepared_id,
                "precompiled": prepared.compiled is not None,
                "subject_type": type(prepared.subject).__name__,
                "locale": _locale.setlocale(_locale.LC_ALL),
            })
        elif action == "warmup" and prepared is not None:
            send({"kind": "warmup", "case": prepared_id, "observation": prepared.untimed()})
        elif action == "sample" and KIND == "timing" and prepared is not None:
            clean_state()
            before = prepared.untimed()
            elapsed = 0
            value = None
            error = None
            for _ in range(OPERATIONS):
                prepared.before_operation()
                started = time.perf_counter_ns()
                try:
                    value = prepared.perform()
                except Exception as caught:
                    error = caught
                elapsed += time.perf_counter_ns() - started
                if error is not None:
                    break
            observed = prepared.observe(value=value, error=error)
            after = prepared.untimed()
            send({
                "kind": "sample",
                "case": prepared_id,
                "before": before,
                "observed": observed,
                "after": after,
                "operations": OPERATIONS if error is None else 0,
                "elapsed_ns": elapsed,
                "locale": _locale.setlocale(_locale.LC_ALL),
                **clean_state(),
            })
        elif action == "memory" and KIND == "memory" and prepared is not None:
            before_rss = rss_bytes()
            prepared.before_operation()
            tracemalloc.start()
            try:
                value = prepared.perform()
                current, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            observation = prepared.observe(value=value)
            send({
                "kind": "memory",
                "case": prepared_id,
                "observation": observation,
                "python_current_bytes": current,
                "python_peak_bytes": peak,
                "process_current_before_bytes": before_rss,
                "process_current_after_bytes": rss_bytes(),
                "process_peak_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                "instrumentation_worker": True,
                "locale": _locale.setlocale(_locale.LC_ALL),
            })
        elif action == "provenance":
            send({
                "kind": "provenance",
                "module": NAME,
                "source": source_path,
                "source_sha256": source_sha256,
                "native": loaded_native(),
                "locale": _locale.setlocale(_locale.LC_ALL),
                **clean_state(True),
            })
        else:
            raise RuntimeError("worker action is invalid or missing a prepared real case")
except BaseException as error:
    try:
        send({"kind": "error", "type": type(error).__name__, "message": str(error)})
    except BaseException:
        pass
    raise
'''


class IsolatedWorker:
    """Persistent native-provenance worker with one absolute I/O deadline."""

    def __init__(self, module: str, kind: str, timeout: float) -> None:
        require(kind in {"timing", "memory"}, "invalid isolated worker type")
        self.module = module
        self.kind = kind
        self.timeout = timeout
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        environment["LC_ALL"] = "C"
        environment["LANG"] = "C"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        started = time.perf_counter_ns()
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-I",
                "-S",
                "-B",
                "-c",
                ISOLATED_WORKER,
                str(ROOT),
                module,
                kind,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=environment,
        )
        self.ready = self.receive(time.monotonic() + max(15.0, timeout))
        self.startup_elapsed_ns = time.perf_counter_ns() - started
        require(
            self.ready.get("kind") == "ready"
            and self.ready.get("module") == module
            and self.ready.get("worker") == kind
            and self.ready.get("locale") == "C"
            and self.startup_elapsed_ns > 0,
            "isolated worker does not have pinned identity, C locale, and cold startup",
        )
        if module != "re" and kind == "timing":
            require(
                self.ready.get("forbidden_loaded") == []
                and self.ready.get("foreign_candidates") == []
                and self.ready.get("external_regex_libraries") == [],
                "isolated candidate loaded a built-in or foreign regex engine",
            )

    def _read_exact(self, size: int, deadline: float) -> bytes:
        require(self.process.stdout is not None, "isolated worker has no response")
        result = bytearray()
        while len(result) < size:
            remaining = deadline - time.monotonic()
            require(remaining > 0, "isolated response exceeded its whole-frame deadline")
            ready, _, _ = select.select([self.process.stdout], [], [], remaining)
            require(bool(ready), "isolated candidate exceeded its complete response deadline")
            block = os.read(self.process.stdout.fileno(), size - len(result))
            require(bool(block), "isolated candidate crashed or closed its response")
            result.extend(block)
        return bytes(result)

    def receive(self, deadline: float) -> dict[str, Any]:
        import marshal

        header = self._read_exact(8, deadline)
        size = int.from_bytes(header, "big")
        require(0 < size <= 4 * 1024 * 1024, "worker returned an oversized frame")
        response = marshal.loads(self._read_exact(size, deadline))
        require(isinstance(response, dict), "worker response has no exact identity")
        require(response.get("kind") != "error", f"isolated worker failed: {response.get('message')}")
        return response

    def call(
        self, action: str, case: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        import marshal

        require(self.process.stdin is not None, "isolated worker has no request pipe")
        request: dict[str, Any] = {"action": action}
        if case is not None:
            request["case"] = case
        payload = marshal.dumps(request)
        deadline = time.monotonic() + self.timeout
        try:
            self.process.stdin.write(len(payload).to_bytes(8, "big"))
            self.process.stdin.write(payload)
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise ProtocolError("isolated candidate crashed during a frozen case") from error
        require(time.monotonic() < deadline, "isolated request exceeded its whole deadline")
        return self.receive(deadline)

    def close(self) -> None:
        if self.process.stdin is not None and self.process.poll() is None:
            import marshal

            payload = marshal.dumps({"action": "close"})
            try:
                self.process.stdin.write(len(payload).to_bytes(8, "big") + payload)
                self.process.stdin.flush()
            except (BrokenPipeError, OSError):
                pass
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=2)


def verify_live_worker(
    worker: IsolatedWorker, module: str, edge: dict[str, Any] | None
) -> None:
    ready = worker.ready
    require(
        ready.get("module") == module and ready.get("locale") == "C",
        "isolated worker identity or actual locale was changed",
    )
    if module == "re":
        return
    require(edge is not None, "candidate worker has no current native correctness proof")
    artifacts = edge["artifacts"]
    public = artifacts["public-python"]
    require(
        ready.get("source") == public["path"]
        and hmac.compare_digest(str(ready.get("source_sha256", "")), public["sha256"]),
        "loaded candidate source differs from the sealed full-oracle proof",
    )
    mapped = ready.get("native")
    require(isinstance(mapped, dict), "isolated worker has no actual native mappings")
    for role in ("native-bridge", "native-engine"):
        if role not in artifacts:
            continue
        expected = artifacts[role]
        require(
            hmac.compare_digest(str(mapped.get(expected["path"], "")), expected["sha256"]),
            "candidate does not actually map its approved current native engine",
        )


def open_blinded_seed(document: dict[str, Any]) -> bytes:
    """Open only after authorization, candidate freeze, and one-use marker."""
    import stat

    seal = document["seal"]
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(seal["opening_path"], flags)
    except OSError as error:
        raise ProtocolError("the independently held v9 opening is unavailable") from error
    try:
        metadata = os.fstat(descriptor)
        require(
            stat.S_ISREG(metadata.st_mode)
            and stat.S_IMODE(metadata.st_mode) == 0o600
            and metadata.st_uid == os.geteuid()
            and metadata.st_size == 32,
            "v9 opening is substituted, insecure, or not exactly 32 bytes",
        )
        opening = os.read(descriptor, 33)
    finally:
        os.close(descriptor)
    require(
        len(opening) == 32
        and hmac.compare_digest(
            hashlib.sha256(opening).hexdigest(), seal["opening_sha256"]
        ),
        "v9 opening does not match its prospective SHA-256 commitment",
    )
    return opening


class RawEvidence:
    """Exclusive compressed line stream with reproducible uncompressed hashing."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.stream: Any = None
        self.compressed: Any = None
        self.digest = hashlib.sha256()
        self.rows = 0

    def __enter__(self) -> "RawEvidence":
        self.stream = self.path.open("xb")
        self.compressed = gzip.GzipFile(
            filename="",
            fileobj=self.stream,
            mode="wb",
            compresslevel=6,
            mtime=0,
        )
        return self

    def append(self, value: dict[str, Any]) -> None:
        line = canonical_bytes(value) + b"\n"
        self.compressed.write(line)
        self.digest.update(line)
        self.rows += 1

    def __exit__(self, error_type: Any, error: Any, traceback: Any) -> None:
        if self.compressed is not None:
            self.compressed.close()
        if self.stream is not None:
            self.stream.close()


def require_observation(actual: Any, expected: dict[str, Any], label: str) -> None:
    require(actual == expected, f"pinned CPython result mismatch: {label}")


def final_measurement(args: argparse.Namespace, document: dict[str, Any]) -> dict[str, Any]:
    require(
        args.authorize_final_unseal == UNSEAL_AUTHORIZATION,
        "v9 has not received explicit irreversible final authorization",
    )
    validate_manifest(document)
    modules = tuple(args.module)
    validate_modules(modules)
    edges = verify_edge_proofs(modules, args.edge_oracle)
    campaigns = verify_campaigns(modules, args.campaign_proof, edges)
    contracts = verify_deep_contracts(modules, args.deep_proof, edges)
    audit = verify_from_scratch_audit(args.from_scratch_audit, modules, edges)
    freeze = verify_freeze(
        args.candidate_freeze, document, modules, edges, campaigns, contracts, audit
    )
    descriptors = case_descriptors()
    validate_descriptors(descriptors)
    raw_path = checked_evidence_path(args.raw, "complete v9 paired raw evidence", exists=False)
    memory_path = checked_evidence_path(args.memory, "complete v9 separate memory", exists=False)
    summary_path = checked_evidence_path(args.output, "complete v9 final results", exists=False)
    marker_path = checked_evidence_path(args.unseal_marker, "one-use v9 marker", exists=False)
    require(
        len({raw_path, memory_path, summary_path, marker_path}) == 4,
        "one-use final evidence paths overlap",
    )
    workers: dict[str, IsolatedWorker] = {}
    memory_workers: dict[str, IsolatedWorker] = {}
    cell_logs = {
        module: {(api, workload): [] for api in APIS for workload in WORKLOADS}
        for module in modules[1:]
    }
    results_by_case: dict[str, list[dict[str, Any]]] = {
        module: [] for module in modules[1:]
    }
    checks = 0
    opening: bytes | None = None
    try:
        for module in modules:
            worker = IsolatedWorker(module, "timing", CASE_TIMEOUT_SECONDS)
            verify_live_worker(worker, module, edges.get(module))
            workers[module] = worker
        marker = {
            "schema": "rebar-v9-single-use-final-unseal-v1",
            "protocol_binding_sha256": document["binding_sha256"],
            "candidate_freeze_sha256": freeze["sha256"],
            "opening_sha256": document["seal"]["opening_sha256"],
            "modules": list(modules),
            "state": "irreversibly-authorized-no-retry",
        }
        with marker_path.open("x", encoding="utf-8") as destination:
            json.dump(marker, destination, allow_nan=False, sort_keys=True, indent=2)
            destination.write("\n")
        opening = open_blinded_seed(document)
        with RawEvidence(raw_path) as raw:
            for descriptor in descriptors:
                case = materialize_case(descriptor, opening)
                for module in modules:
                    ready = workers[module].call("prepare", case)
                    require(
                        ready.get("kind") == "prepared"
                        and ready.get("case") == descriptor["id"]
                        and ready.get("locale") == "C",
                        "actual case was not prepared with real types and C locale",
                    )
                    if descriptor.get("surface") == "compiled" or descriptor["api"] == "scanner":
                        require(
                            ready.get("precompiled") is True,
                            "compiled workload has no genuinely retained compiled pattern",
                        )
                baseline = workers["re"].call("warmup")
                expected = baseline.get("observation")
                require(
                    baseline.get("kind") == "warmup"
                    and baseline.get("case") == descriptor["id"]
                    and isinstance(expected, dict)
                    and expected.get("status") == "ok",
                    "generated final workload is not valid for pinned CPython",
                )
                for warmup in range(WARMUPS):
                    for module in counterbalanced_order(
                        modules, descriptor["id"], warmup, ORDER_SEED
                    ):
                        observation = workers[module].call("warmup")
                        require_observation(
                            observation.get("observation"),
                            expected,
                            f"{descriptor['id']}:warmup:{module}",
                        )
                per_case: dict[str, list[float]] = {
                    module: [] for module in modules[1:]
                }
                for round_index in range(PAIRED_ROUNDS):
                    order = counterbalanced_order(
                        modules, descriptor["id"], round_index, ORDER_SEED
                    )
                    paired: dict[str, dict[str, Any]] = {}
                    for position, module in enumerate(order):
                        sample = workers[module].call("sample")
                        require(
                            sample.get("kind") == "sample"
                            and sample.get("case") == descriptor["id"]
                            and sample.get("locale") == "C"
                            and sample.get("operations") == OPERATIONS_PER_SAMPLE,
                            "timed sample changed its identity, locale, or exact operations",
                        )
                        for gate in ("before", "observed", "after"):
                            require_observation(
                                sample.get(gate),
                                expected,
                                f"{descriptor['id']}:{round_index}:{module}:{gate}",
                            )
                            checks += 1
                        elapsed = sample.get("elapsed_ns")
                        require(
                            isinstance(elapsed, int)
                            and not isinstance(elapsed, bool)
                            and elapsed > 0,
                            "actual-operation timing is not positive",
                        )
                        if module != "re":
                            require(
                                sample.get("forbidden_loaded") == []
                                and sample.get("foreign_candidates") == []
                                and sample.get("external_regex_libraries") == [],
                                "candidate delegated during a real timed call",
                            )
                        paired[module] = sample
                        raw.append(
                            {
                                "schema": ROW_SCHEMA,
                                "case": descriptor["id"],
                                "api": descriptor["api"],
                                "workload": descriptor["workload"],
                                "round": round_index,
                                "module": module,
                                "position": position,
                                "operations": OPERATIONS_PER_SAMPLE,
                                "elapsed_ns": elapsed,
                                "ns_per_op": elapsed / OPERATIONS_PER_SAMPLE,
                                "locale": "C",
                                "correctness_pre": True,
                                "correctness_timed": True,
                                "correctness_post": True,
                            }
                        )
                    require(set(paired) == set(modules), "a paired candidate is missing")
                    baseline_ns = paired["re"]["elapsed_ns"]
                    for module in modules[1:]:
                        per_case[module].append(
                            math.log(baseline_ns / paired[module]["elapsed_ns"])
                        )
                for module in modules[1:]:
                    logs = per_case[module]
                    mean = statistics.fmean(logs)
                    speedup = math.exp(mean)
                    low, high = case_confidence(logs)
                    results_by_case[module].append(
                        {
                            "case": descriptor["id"],
                            "api": descriptor["api"],
                            "workload": descriptor["workload"],
                            "paired_rounds": PAIRED_ROUNDS,
                            "operations_per_sample": OPERATIONS_PER_SAMPLE,
                            "speedup": speedup,
                            "confidence_low": low,
                            "confidence_high": high,
                            "statistically_faster": is_significant_win(low),
                            "runtime_regression_over_20_percent": is_runtime_regression(speedup),
                        }
                    )
                    cell_logs[module][(descriptor["api"], descriptor["workload"])].append(mean)
            expected_rows = CASE_COUNT * PAIRED_ROUNDS * len(modules)
            require(raw.rows == expected_rows, "a case, round, or engine was omitted")
            require(checks == expected_rows * 3, "a real-operation correctness gate was removed")
            raw_summary = {
                "path": str(raw_path.relative_to(ROOT)),
                "rows": raw.rows,
                "operations_per_row": OPERATIONS_PER_SAMPLE,
                "uncompressed_rows_sha256": raw.digest.hexdigest(),
            }

        memory_descriptors = [
            descriptor for descriptor in descriptors if descriptor["index"] in MEMORY_INDICES
        ]
        require(len(memory_descriptors) == MEMORY_CASES, "memory case denominator changed")
        for module in modules:
            worker = IsolatedWorker(module, "memory", CASE_TIMEOUT_SECONDS)
            verify_live_worker(worker, module, edges.get(module))
            memory_workers[module] = worker
        with RawEvidence(memory_path) as memory:
            for descriptor in memory_descriptors:
                case = materialize_case(descriptor, opening)
                for module in modules:
                    prepared = memory_workers[module].call("prepare", case)
                    require(
                        prepared.get("kind") == "prepared"
                        and prepared.get("case") == descriptor["id"]
                        and prepared.get("locale") == "C",
                        "separate memory worker has no actual prepared case",
                    )
                observations = {
                    module: memory_workers[module].call("memory") for module in modules
                }
                expected = observations["re"].get("observation")
                require(
                    isinstance(expected, dict) and expected.get("status") == "ok",
                    "baseline separate-memory result is invalid",
                )
                for module, record in observations.items():
                    require(
                        record.get("kind") == "memory"
                        and record.get("case") == descriptor["id"]
                        and record.get("locale") == "C",
                        "separate memory record has the wrong case or locale",
                    )
                    require_observation(
                        record.get("observation"), expected, "independent memory correctness"
                    )
                    fields = (
                        "python_current_bytes",
                        "python_peak_bytes",
                        "process_current_before_bytes",
                        "process_current_after_bytes",
                        "process_peak_bytes",
                    )
                    for field in fields:
                        require(
                            isinstance(record.get(field), int)
                            and not isinstance(record[field], bool)
                            and record[field] >= 0,
                            f"invalid separate process or Python memory: {field}",
                        )
                    memory.append(
                        {
                            "schema": MEMORY_ROW_SCHEMA,
                            "case": descriptor["id"],
                            "api": descriptor["api"],
                            "workload": descriptor["workload"],
                            "module": module,
                            "locale": "C",
                            **{field: record[field] for field in fields},
                            "python_memory_is_native_memory": False,
                            "instrumentation_worker": True,
                            "correctness": True,
                        }
                    )
            require(
                memory.rows == MEMORY_CASES * len(modules),
                "separate memory case or engine was omitted",
            )
            memory_summary = {
                "path": str(memory_path.relative_to(ROOT)),
                "rows": memory.rows,
                "cases_per_module": MEMORY_CASES,
                "uncompressed_rows_sha256": memory.digest.hexdigest(),
                "python_peak_definition": "tracemalloc-python-allocations-only",
                "process_peak_definition": "whole-process-peak-rss-bytes",
            }

        ranked: list[dict[str, Any]] = []
        for index, module in enumerate(modules[1:]):
            individual = results_by_case[module]
            require(len(individual) == CASE_COUNT, "candidate case denominator changed")
            cells = cell_logs[module]
            flattened = [
                value
                for api in APIS
                for workload in WORKLOADS
                for value in cells[(api, workload)]
            ]
            require(len(flattened) == CASE_COUNT, "overall case denominator changed")
            low, high = stratified_bootstrap(cells, BOOTSTRAP_SEED + index)
            wins = sum(row["statistically_faster"] for row in individual)
            regressions = [
                row for row in individual if row["runtime_regression_over_20_percent"]
            ]
            ranked.append(
                {
                    "module": module,
                    "cases": CASE_COUNT,
                    "geomean_speedup": math.exp(statistics.fmean(flattened)),
                    "confidence_low": low,
                    "confidence_high": high,
                    "bootstrap_draws": BOOTSTRAP_DRAWS,
                    "statistically_faster_cases": wins,
                    "minimum_statistically_faster_cases": MINIMUM_WINS,
                    "regression_count": len(regressions),
                    "regressions": regressions,
                    "case_results": individual,
                    "meets_speed_requirement": low >= 1.5,
                    "meets_case_requirement": wins >= MINIMUM_WINS,
                    "success": low >= 1.5 and wins >= MINIMUM_WINS,
                }
            )
        for module, worker in workers.items():
            state = worker.call("provenance")
            require(
                state.get("kind") == "provenance"
                and state.get("module") == module
                and state.get("locale") == "C",
                "final current worker provenance was removed",
            )
            if module == "re":
                continue
            require(
                state.get("forbidden_loaded") == []
                and state.get("foreign_candidates") == []
                and state.get("external_regex_libraries") == []
                and state.get("source_sha256")
                == edges[module]["artifacts"]["public-python"]["sha256"],
                "candidate delegated or changed source during the final measurement",
            )
            for role in ("native-bridge", "native-engine"):
                if role in edges[module]["artifacts"]:
                    artifact = edges[module]["artifacts"][role]
                    require(
                        state.get("native", {}).get(artifact["path"])
                        == artifact["sha256"],
                        "native matching engine changed after its frozen qualification",
                    )
        summary = {
            "schema": SUMMARY_SCHEMA,
            "protocol_binding_sha256": document["binding_sha256"],
            "manifest_sha256": canonical_digest(document),
            "candidate_freeze": freeze,
            "from_scratch_audit": audit,
            "python": "3.14.6",
            "locale": "C",
            "modules": list(modules),
            "cases": CASE_COUNT,
            "paired_rounds": PAIRED_ROUNDS,
            "operations_per_sample": OPERATIONS_PER_SAMPLE,
            "warmups": WARMUPS,
            "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
            "correctness_snapshots": checks,
            "cold_process_startup": [
                {
                    "module": module,
                    "elapsed_ns": workers[module].startup_elapsed_ns,
                    "included_in_main_speedup": False,
                    "definition": "isolated-process-start-import-and-current-native-proof",
                }
                for module in modules
            ],
            "raw": raw_summary,
            "memory": memory_summary,
            "results": ranked,
            "opening_sha256": document["seal"]["opening_sha256"],
            "opening_hex": opening.hex(),
            "original_holdout_accessed": False,
            "v8_holdout_accessed": False,
            "original_v7_cases": 10_312,
            "combined_results": "NOT MEASURED",
            "failed": 0,
        }
        with summary_path.open("x", encoding="utf-8") as destination:
            json.dump(summary, destination, allow_nan=False, sort_keys=True, indent=2)
            destination.write("\n")
        return {
            "schema": SUMMARY_SCHEMA,
            "path": str(summary_path.relative_to(ROOT)),
            "cases": CASE_COUNT,
            "paired_rounds": PAIRED_ROUNDS,
            "operations_per_sample": OPERATIONS_PER_SAMPLE,
            "raw_rows": raw_summary["rows"],
            "correctness_snapshots": checks,
            "memory_rows": memory_summary["rows"],
            "opening_published_only_in_final_summary": True,
            "failed": 0,
        }
    finally:
        for worker in memory_workers.values():
            worker.close()
        for worker in workers.values():
            worker.close()


def validate_paired_rows(
    rows: list[dict[str, Any]],
    descriptors: list[dict[str, Any]],
    modules: tuple[str, ...],
    rounds: int,
    seed: int,
) -> None:
    require(1 <= rounds <= PAIRED_ROUNDS, "incorrect number of paired rounds")
    require(
        len(rows) == len(descriptors) * rounds * len(modules),
        "a paired case, round, or candidate disappeared",
    )
    identifiers = {row["id"] for row in descriptors}
    found: set[tuple[str, int, str]] = set()
    for row in rows:
        require(isinstance(row, dict) and row.get("schema") == ROW_SCHEMA, "invalid row")
        identifier, round_index, module = row.get("case"), row.get("round"), row.get("module")
        require(
            identifier in identifiers
            and isinstance(round_index, int)
            and 0 <= round_index < rounds
            and module in modules,
            "observed paired row is not frozen",
        )
        identity = (identifier, round_index, module)
        require(identity not in found, "paired row is duplicated")
        found.add(identity)
        elapsed = row.get("elapsed_ns")
        require(
            isinstance(elapsed, int)
            and not isinstance(elapsed, bool)
            and elapsed > 0
            and row.get("operations") == OPERATIONS_PER_SAMPLE
            and row.get("locale") == "C",
            "paired row changed its operation count, locale, or positive elapsed time",
        )
        require(
            all(row.get(name) is True for name in ("correctness_pre", "correctness_timed", "correctness_post")),
            "paired row omitted a complete pinned-Python observation",
        )
        require(
            row.get("position")
            == counterbalanced_order(modules, identifier, round_index, seed).index(module),
            "paired row changed its counterbalanced engine order",
        )
    require(
        len(found) == len(descriptors) * rounds * len(modules),
        "paired case/round/candidate denominator changed",
    )


@contextlib.contextmanager
def synthetic_io_guard() -> Iterator[list[str]]:
    """Reject secret, v6/v7/v8, and poison paths before filesystem access."""
    original_builtin = builtins.open
    original_io = io.open
    original_os_open = os.open
    attempts: list[str] = []

    def reject(value: Any) -> None:
        if not isinstance(value, (str, bytes, os.PathLike)):
            return
        path = os.fsdecode(value)
        if any(
            marker in path
            for marker in (
                "/performance/v6/",
                "/performance/v7/",
                "/performance/v8/",
                "/fixtures/",
                "/__rebar_v9_synthetic_poison__/",
                "rebar-v8-final-holdout-opening-",
                "rebar-v9-final-holdout-opening-",
            )
        ):
            attempts.append(path)
            raise ProtocolError("synthetic verifier refused a final secret or old fixture")

    def guarded_builtin(path: Any, *args: Any, **kwargs: Any) -> Any:
        reject(path)
        return original_builtin(path, *args, **kwargs)

    def guarded_io(path: Any, *args: Any, **kwargs: Any) -> Any:
        reject(path)
        return original_io(path, *args, **kwargs)

    def guarded_os_open(path: Any, *args: Any, **kwargs: Any) -> Any:
        reject(path)
        return original_os_open(path, *args, **kwargs)

    builtins.open = guarded_builtin
    io.open = guarded_io
    os.open = guarded_os_open
    try:
        yield attempts
    finally:
        builtins.open = original_builtin
        io.open = original_io
        os.open = original_os_open


def expect_rejection(name: str, action: Any) -> dict[str, str]:
    try:
        action()
    except (ProtocolError, OSError, ValueError, TypeError, OverflowError) as error:
        return {"name": name, "result": "rejected", "error": type(error).__name__}
    raise ProtocolError(f"synthetic corruption was incorrectly accepted: {name}")


def synthetic_rows(
    descriptor: dict[str, Any], modules: tuple[str, ...], rounds: int, seed: int
) -> list[dict[str, Any]]:
    result = []
    for trial in range(rounds):
        for position, module in enumerate(
            counterbalanced_order(modules, descriptor["id"], trial, seed)
        ):
            elapsed = 1600 + trial
            result.append(
                {
                    "schema": ROW_SCHEMA,
                    "case": descriptor["id"],
                    "round": trial,
                    "module": module,
                    "position": position,
                    "operations": OPERATIONS_PER_SAMPLE,
                    "elapsed_ns": elapsed,
                    "ns_per_op": elapsed / OPERATIONS_PER_SAMPLE,
                    "locale": "C",
                    "correctness_pre": True,
                    "correctness_timed": True,
                    "correctness_post": True,
                }
            )
    return result


def self_test(document: dict[str, Any]) -> dict[str, Any]:
    """Use only public coordinates and domain-separated synthetic openings."""
    checks: list[dict[str, str]] = []
    with synthetic_io_guard() as attempted:
        validate_manifest(document)
        require(
            not hmac.compare_digest(
                hashlib.sha256(SYNTHETIC_OPENING).hexdigest(),
                document["seal"]["opening_sha256"],
            ),
            "public synthetic controls collide with the secret final commitment",
        )
        descriptors = case_descriptors()
        validate_descriptors(descriptors)
        require(
            all(
                "pattern" not in row and "subject" not in row and "seed" not in row
                for row in descriptors
            ),
            "public frozen coordinates leak a final case",
        )
        checks.append({"name": "24576-coordinates-zero-final-inputs", "result": "passed"})

        manifest_poison = (
            ("wrong-schema", ("schema",), "wrong"),
            ("already-opened", ("state",), "opened"),
            ("wrong-cpython", ("reference", "version"), "3.14.5"),
            ("wrong-unicode", ("reference", "unicode_version"), "15.0.0"),
            ("unverified-worker-locale", ("reference", "enforced_worker_locale"), "C.UTF-8"),
            ("missing-keyed-semantics", ("layout", "semantic_identity"), "comment-only"),
            ("missing-final-case", ("layout", "cases"), CASE_COUNT - 1),
            ("extra-final-case", ("layout", "cases"), CASE_COUNT + 1),
            ("changed-cell-size", ("layout", "cases_per_cell"), CASES_PER_CELL - 1),
            ("changed-api-denominator", ("layout", "cases_per_api"), CASES_PER_API - 1),
            ("changed-opening-commitment", ("seal", "opening_sha256"), "0" * 64),
            ("changed-opening-path", ("seal", "opening_path"), "/tmp/invalid-v9-opening"),
            ("weak-opening-permissions", ("seal", "opening_mode"), "0644"),
            ("fictional-same-user-security", ("seal", "isolation"), "security-boundary"),
            ("missing-paired-round", ("trials", "paired_rounds"), PAIRED_ROUNDS - 1),
            ("missing-operation", ("trials", "operations_per_sample"), OPERATIONS_PER_SAMPLE - 1),
            ("normalization-inside-clock", ("trials", "timed_operation"), "normalized-and-exhausted"),
            ("fake-compiled-pattern", ("trials", "compiled_lifecycle"), "compile-inside-timing"),
            ("resettable-timeout", ("trials", "timeout_method"), "timeout-per-frame-chunk"),
            ("missing-candidate", ("trials", "minimum_candidates"), 2),
            ("missing-paired-row", ("trials", "four_engine_timed_rows"), 3_047_423),
            ("missing-correctness-snapshot", ("trials", "four_engine_correctness_snapshots"), 9_142_271),
            ("reduced-bootstrap", ("statistics", "overall_bootstrap_draws"), 9_998),
            ("7372-style-win-denominator", ("statistics", "minimum_significant_wins"), MINIMUM_WINS - 1),
            ("weakened-overall-speed", ("statistics", "overall_lower_bound"), 1.49),
            ("dropped-edge-check", ("correctness", "edge_checks"), 223_197),
            ("changed-edge-answer", ("correctness", "edge_answer_sha256"), "0" * 64),
            ("missing-unicode-check", ("correctness", "unicode_checks"), 4_494_554),
            ("missing-campaign-stage", ("correctness", "minimum_current_campaign_stages"), 21),
            ("removed-native-proof", ("independence", "required_owned_native_artifacts"), 4),
            ("allowed-delegation", ("independence", "candidate_delegation"), "allowed"),
            ("allowed-benchmark-detection", ("independence", "benchmark_detection"), "allowed"),
            ("wrong-memory-denominator", ("memory", "cases"), MEMORY_CASES - 1),
            ("python-memory-called-native", ("memory", "python_peak"), "native-allocations"),
            ("opened-v8", ("history", "v8_status"), "opened"),
            ("premature-v9-speed", ("history", "v9_results"), "MEASURED"),
            ("changed-binding", ("binding_sha256",), "0" * 64),
        )
        for name, path, value in manifest_poison:
            changed = json.loads(canonical_bytes(document))
            cursor: dict[str, Any] = changed
            for component in path[:-1]:
                cursor = cursor[component]
            cursor[path[-1]] = value
            checks.append(
                expect_rejection(
                    name,
                    lambda corrupted=changed: validate_manifest(corrupted),
                )
            )

        for name, changed in (
            ("missing-public-descriptor", descriptors[:-1]),
            ("duplicate-public-descriptor", [*descriptors[:-1], descriptors[0]]),
        ):
            checks.append(
                expect_rejection(
                    name,
                    lambda corrupted=changed: validate_descriptors(corrupted),
                )
            )

        reference = __import__("re")
        signatures: set[str] = set()
        subject_types: collections.Counter[str] = collections.Counter()
        synthetic_count = 0
        for api_index, api in enumerate(APIS):
            family = WORKLOADS[api_index % len(WORKLOADS)]
            pool = [
                row for row in descriptors if row["api"] == api and row["workload"] == family
            ]
            require(len(pool) == CASES_PER_CELL, "synthetic cell is incomplete")
            requested = (
                ("str", "bytes")
                if api in {"compile", "escape"}
                else ("str", "bytes", "bytearray", "memoryview")
            )
            for kind in requested:
                found: dict[str, Any] | None = None
                for row in pool:
                    clone = dict(row)
                    clone["id"] = f"synthetic.v9.{api}.{family}.{row['index']:03d}.{kind}"
                    generated = materialize_case(clone, SYNTHETIC_OPENING, synthetic=True)
                    if generated["source_kind"] == kind:
                        found = generated
                        break
                require(found is not None, "real mutable-buffer control is missing")
                subject = decode_subject(found["subject"], found["source_kind"])
                require(
                    type(subject)
                    is {
                        "str": str,
                        "bytes": bytes,
                        "bytearray": bytearray,
                        "memoryview": memoryview,
                    }[kind],
                    "synthetic wire transport did not reconstruct its actual object",
                )
                if api == "escape":
                    reference.escape(subject)
                else:
                    reference.compile(found["pattern"], found["flags"])
                subject_types[kind] += 1
                synthetic_count += 1

        literal_pool = [
            row
            for row in descriptors
            if row["api"] == "search" and row["workload"] == "literal-and-long-prefix"
        ]
        for row in literal_pool:
            clone = dict(row)
            clone["id"] = f"synthetic.v9.unique.{row['index']:03d}"
            case = materialize_case(clone, SYNTHETIC_OPENING, synthetic=True)
            key = canonical_digest(
                {
                    "pattern": (
                        case["pattern"].hex()
                        if isinstance(case["pattern"], bytes)
                        else case["pattern"]
                    ),
                    "subject": (
                        case["subject"].hex()
                        if isinstance(case["subject"], bytes)
                        else case["subject"]
                    ),
                    "source_kind": case["source_kind"],
                }
            )
            require(key not in signatures, "HMAC cases changed only labels or comments")
            signatures.add(key)
        require(len(signatures) == CASES_PER_CELL, "secret-keyed semantic diversity is false")
        checks.append({"name": "256-genuinely-distinct-synthetic-match-semantics", "result": "passed"})

        for name, action in (
            (
                "final-descriptor-in-synthetic-domain",
                lambda: materialize_case(descriptors[0], SYNTHETIC_OPENING, synthetic=True),
            ),
            (
                "synthetic-opening-in-real-domain",
                lambda: materialize_case(
                    {**descriptors[0], "id": "synthetic.v9.invalid"},
                    SYNTHETIC_OPENING,
                ),
            ),
            (
                "wrong-synthetic-opening",
                lambda: materialize_case(
                    {**descriptors[0], "id": "synthetic.v9.invalid"},
                    b"\0" * 32,
                    synthetic=True,
                ),
            ),
            (
                "invalid-mutable-buffer-kind",
                lambda: decode_subject(
                    {"schema": BUFFER_SCHEMA, "kind": "memoryview", "hex": "6162"},
                    "bytearray",
                ),
            ),
            (
                "invalid-mutable-buffer-payload",
                lambda: decode_subject(
                    {"schema": BUFFER_SCHEMA, "kind": "bytearray", "hex": "no-hex"},
                    "bytearray",
                ),
            ),
        ):
            checks.append(expect_rejection(name, action))

        modules = (
            "re",
            "candidates.vm_candidate",
            "candidates.rust_candidate",
            "candidates.zig_candidate",
        )
        validate_modules(modules)
        for name, wrong_modules in (
            (
                "substituted-baseline",
                (
                    "candidates.vm_candidate",
                    "re",
                    "candidates.rust_candidate",
                    "candidates.zig_candidate",
                ),
            ),
            (
                "duplicated-engine",
                (
                    "re",
                    "candidates.vm_candidate",
                    "candidates.vm_candidate",
                    "candidates.zig_candidate",
                ),
            ),
            (
                "missing-zig-family",
                (
                    "re",
                    "candidates.vm_candidate",
                    "candidates.rust_candidate",
                    "candidates.ast_candidate",
                ),
            ),
            (
                "external-regex-wrapper",
                (
                    "re",
                    "candidates.vm_candidate",
                    "candidates.rust_candidate",
                    "candidates.regex",
                ),
            ),
        ):
            checks.append(
                expect_rejection(
                    name,
                    lambda selected=wrong_modules: validate_modules(selected),
                )
            )
        first = collections.Counter(
            counterbalanced_order(modules, "synthetic.v9.pair", trial, ORDER_SEED)[0]
            for trial in range(PAIRED_ROUNDS)
        )
        require(
            set(first) == set(modules) and max(first.values()) - min(first.values()) <= 1,
            "31-round Latin ordering is not actually counterbalanced",
        )
        checks.append({"name": "31-paired-four-engine-counterbalanced-rounds", "result": "passed"})
        descriptor = {"id": "synthetic.v9.pair"}
        rows = synthetic_rows(descriptor, modules, 3, ORDER_SEED)
        validate_paired_rows(rows, [descriptor], modules, 3, ORDER_SEED)
        for name, changed in (
            ("missing-row", rows[:-1]),
            ("duplicate-row", [*rows[:-1], dict(rows[0])]),
            ("zero-time", [{**rows[0], "elapsed_ns": 0}, *rows[1:]]),
            ("wrong-operation-count", [{**rows[0], "operations": 1}, *rows[1:]]),
            ("wrong-actual-locale", [{**rows[0], "locale": "C.UTF-8"}, *rows[1:]]),
            ("missing-before-gate", [{**rows[0], "correctness_pre": False}, *rows[1:]]),
            ("missing-timed-gate", [{**rows[0], "correctness_timed": False}, *rows[1:]]),
            ("missing-after-gate", [{**rows[0], "correctness_post": False}, *rows[1:]]),
            ("wrong-order", [{**rows[0], "position": 99}, *rows[1:]]),
        ):
            checks.append(
                expect_rejection(
                    name,
                    lambda data=changed: validate_paired_rows(
                        data, [descriptor], modules, 3, ORDER_SEED
                    ),
                )
            )

        homogeneous = [[0.0, 0.0], [math.log(4.0), math.log(4.0)]]
        require(
            bootstrap_clusters(homogeneous, seed=ORDER_SEED, draws=127, per_cell=2)
            == (2.0, 2.0),
            "bootstrap does not retain exact workload weights",
        )
        varied = [[0.0, math.log(2.0)], [math.log(3.0), math.log(4.0)]]
        random_source = random.Random(ORDER_SEED)
        reference_draws: list[float] = []
        for _ in range(127):
            first_cell = sum(varied[0][random_source.randrange(2)] for _ in range(2))
            second_cell = sum(varied[1][random_source.randrange(2)] for _ in range(2))
            reference_draws.append(math.exp((first_cell + second_cell) / 4.0))
        require(
            bootstrap_clusters(varied, seed=ORDER_SEED, draws=127, per_cell=2)
            == (
                percentile(reference_draws, 0.025),
                percentile(reference_draws, 0.975),
            ),
            "stratified whole-case resampling disagrees with an independent control",
        )
        checks.append({"name": "independent-synthetic-stratified-bootstrap", "result": "passed"})
        for name, cells, draws, per_cell in (
            ("missing-bootstrap-cell", [], 127, 2),
            ("unequal-bootstrap-cell", [[0.0], [0.0, 0.0]], 127, 2),
            ("missing-bootstrap-draws", homogeneous, 0, 2),
            ("nonfinite-bootstrap-case", [[0.0, float("nan")], [0.0, 0.0]], 127, 2),
        ):
            checks.append(
                expect_rejection(
                    name,
                    lambda values=cells, count=draws, size=per_cell: bootstrap_clusters(
                        values,
                        seed=ORDER_SEED,
                        draws=count,
                        per_cell=size,
                    ),
                )
            )

        synthetic_artifact_path = str(
            (ROOT / "candidates" / "__v9_synthetic_native_identity__.so").resolve()
        )
        synthetic_artifact = {
            "role": "native-engine",
            "path": synthetic_artifact_path,
            "sha256": "a" * 64,
        }
        expected_artifacts = {
            "native-engine": {
                "path": synthetic_artifact_path,
                "sha256": "a" * 64,
            }
        }
        _matches_current_artifacts(
            [synthetic_artifact],
            expected_artifacts,
            "synthetic live native identity",
        )
        checks.append({"name": "exact-synthetic-current-native-identity", "result": "passed"})
        for name, records in (
            ("missing-live-native-identity", []),
            (
                "stale-live-native-digest",
                [{**synthetic_artifact, "sha256": "b" * 64}],
            ),
            (
                "swapped-live-native-path",
                [
                    {
                        **synthetic_artifact,
                        "path": str(
                            (ROOT / "candidates" / "__wrong_v9_synthetic_engine__.so").resolve()
                        ),
                    }
                ],
            ),
            (
                "foreign-live-native-role",
                [{**synthetic_artifact, "role": "native-bridge"}],
            ),
        ):
            checks.append(
                expect_rejection(
                    name,
                    lambda observed=records: _matches_current_artifacts(
                        observed,
                        expected_artifacts,
                        "synthetic live native identity",
                    ),
                )
            )

        require(
            case_confidence([0.0] * PAIRED_ROUNDS) == (1.0, 1.0)
            and not is_significant_win(1.0)
            and is_significant_win(math.nextafter(1.0, math.inf))
            and MINIMUM_WINS == 14_746,
            "confidence, exact equality, or significant-win cutoff changed",
        )
        for value, expected in (
            (0.8, True),
            (0.833, True),
            (5.0 / 6.0, False),
            (0.834, False),
            (1.0, False),
        ):
            require(
                is_runtime_regression(value) is expected,
                "strict 20-percent runtime regression boundary changed",
            )
        for name, value in (
            ("zero-speedup", 0.0),
            ("negative-speedup", -1.0),
            ("nan-speedup", float("nan")),
            ("infinite-speedup", float("inf")),
        ):
            checks.append(
                expect_rejection(name, lambda item=value: is_runtime_regression(item))
            )
        poison = "/__rebar_v9_synthetic_poison__/never-open"
        checks.append(expect_rejection("secret-and-previous-fixture-io", lambda: os.open(poison, os.O_RDONLY)))
        require(attempted == [poison], "synthetic verification reached an actual secret")
    return {
        "schema": SELF_TEST_SCHEMA,
        "manifest_path": (
            "synthetic-only-in-memory-never-a-frozen-manifest"
            if document["seal"]["opening_sha256"] == SYNTHETIC_MANIFEST_COMMITMENT
            else "performance/v9/holdout-manifest.json"
        ),
        "manifest_mode": (
            "synthetic-only-uncommitted"
            if document["seal"]["opening_sha256"] == SYNTHETIC_MANIFEST_COMMITMENT
            else "committed-prospective-manifest"
        ),
        "manifest_sha256": canonical_digest(document),
        "source_sha256": file_digest(Path(__file__).resolve()),
        "cases": CASE_COUNT,
        "apis": len(APIS),
        "workloads": len(WORKLOADS),
        "cases_per_cell": CASES_PER_CELL,
        "paired_rounds": PAIRED_ROUNDS,
        "operations_per_sample": OPERATIONS_PER_SAMPLE,
        "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
        "minimum_significant_wins": MINIMUM_WINS,
        "synthetic_structure_cases": synthetic_count,
        "synthetic_semantically_unique_cases": len(signatures),
        "synthetic_actual_subject_types": dict(sorted(subject_types.items())),
        "check_count": len(checks),
        "poison_rejections": sum(item["result"] == "rejected" for item in checks),
        "checks_sha256": canonical_digest(checks),
        "opening_read": False,
        "previous_holdout_accessed": False,
        "hidden_cases_generated": 0,
        "candidate_imported": False,
        "timing_performed": False,
        "memory_measured": False,
        "failed": 0,
    }


def verify_recorded_self_test(document: dict[str, Any]) -> dict[str, Any]:
    require(SELF_TEST_PATH.is_file(), "committed synthetic-only v9 evidence is absent")
    observed, _payload = read_json_document(SELF_TEST_PATH, "committed v9 synthetic controls")
    require(observed == self_test(document), "frozen v9 synthetic controls are stale")
    return observed


def qualify_candidates(
    args: argparse.Namespace, document: dict[str, Any]
) -> tuple[
    tuple[str, ...],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, str]],
    dict[str, Any],
]:
    validate_manifest(document)
    modules = tuple(args.module)
    validate_modules(modules)
    edges = verify_edge_proofs(modules, args.edge_oracle)
    campaigns = verify_campaigns(modules, args.campaign_proof, edges)
    contracts = verify_deep_contracts(modules, args.deep_proof, edges)
    audit = verify_from_scratch_audit(args.from_scratch_audit, modules, edges)
    return modules, edges, campaigns, contracts, audit


def freeze_candidate_selection(
    args: argparse.Namespace, document: dict[str, Any]
) -> dict[str, Any]:
    modules, edges, campaigns, contracts, audit = qualify_candidates(args, document)
    stopping = args.stopping_commit
    require(
        isinstance(stopping, str)
        and len(stopping) in {40, 64}
        and all(letter in "0123456789abcdef" for letter in stopping),
        "stopping point is not a complete Git object digest",
    )
    target = checked_evidence_path(args.candidate_freeze, "new candidate freeze", exists=False)
    freeze = {
        "schema": FREEZE_SCHEMA,
        "protocol_binding_sha256": document["binding_sha256"],
        "stopping_commit": stopping,
        "baseline": "re",
        "from_scratch_audit_sha256": audit["sha256"],
        "candidates": [
            {
                "module": module,
                "edge_sha256": edges[module]["sha256"],
                "campaign_sha256": campaigns[module]["sha256"],
                "deep_contract_sha256": contracts[module]["sha256"],
                "artifacts": edges[module]["artifacts"],
            }
            for module in modules[1:]
        ],
        "opening_read": False,
        "hidden_cases_generated": 0,
        "performance_measured": False,
    }
    with target.open("x", encoding="utf-8") as destination:
        json.dump(freeze, destination, allow_nan=False, sort_keys=True, indent=2)
        destination.write("\n")
    return {
        "schema": FREEZE_SCHEMA,
        "path": str(target.relative_to(ROOT)),
        "sha256": file_digest(target),
        "candidates": len(modules) - 1,
        "opening_read": False,
        "hidden_cases_generated": 0,
        "performance_measured": False,
        "failed": 0,
    }


def add_candidate_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--module", action="append", required=True)
    parser.add_argument("--edge-oracle", type=Path, action="append", required=True)
    parser.add_argument("--campaign-proof", type=Path, action="append", required=True)
    parser.add_argument("--deep-proof", type=Path, action="append", required=True)
    parser.add_argument("--from-scratch-audit", type=Path, required=True)
    parser.add_argument("--candidate-freeze", type=Path, required=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    manifest = commands.add_parser(
        "manifest",
        help="print prospective public metadata for an independently supplied SHA-256 commitment",
    )
    manifest.add_argument(
        "--opening-sha256",
        required=True,
        help="only the independent custodian's digest; never supply or print the opening",
    )

    verify = commands.add_parser("verify", help="verify metadata without opening a holdout")
    verify.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    verify.add_argument("--evidence", action="store_true")

    test = commands.add_parser(
        "self-test",
        help="run only domain-separated synthetic poison controls",
    )
    test.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    test.add_argument(
        "--public-synthetic-only",
        action="store_true",
        help="use only a public in-memory dummy commitment; never create or open a manifest or secret",
    )

    freeze = commands.add_parser(
        "freeze-candidates",
        help="bind approved current native identities without reading final cases",
    )
    add_candidate_arguments(freeze)
    freeze.add_argument("--stopping-commit", required=True)

    preflight = commands.add_parser(
        "preflight",
        help="check frozen full-oracle campaigns and current native proofs without unsealing",
    )
    add_candidate_arguments(preflight)

    final = commands.add_parser(
        "final",
        help="explicitly and irreversibly run the prospectively sealed v9 test",
    )
    add_candidate_arguments(final)
    final.add_argument("--authorize-final-unseal", required=True)
    final.add_argument("--raw", type=Path, required=True)
    final.add_argument("--memory", type=Path, required=True)
    final.add_argument("--output", type=Path, required=True)
    final.add_argument("--unseal-marker", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "manifest":
        document = make_manifest(args.opening_sha256)
        print(json.dumps(document, allow_nan=False, sort_keys=True, indent=2))
        return 0
    if args.command == "self-test" and args.public_synthetic_only:
        document = make_manifest(SYNTHETIC_MANIFEST_COMMITMENT)
        print(json.dumps(self_test(document), allow_nan=False, sort_keys=True))
        return 0
    document = load_manifest(args.manifest)
    if args.command == "self-test":
        print(json.dumps(self_test(document), allow_nan=False, sort_keys=True))
    elif args.command == "freeze-candidates":
        print(
            json.dumps(
                freeze_candidate_selection(args, document),
                allow_nan=False,
                sort_keys=True,
            )
        )
    elif args.command == "preflight":
        modules, edges, campaigns, contracts, audit = qualify_candidates(args, document)
        freeze_document = verify_freeze(
            args.candidate_freeze,
            document,
            modules,
            edges,
            campaigns,
            contracts,
            audit,
        )
        print(
            json.dumps(
                {
                    "schema": FREEZE_SCHEMA,
                    "candidate_freeze_sha256": freeze_document["sha256"],
                    "cases": CASE_COUNT,
                    "candidates": len(modules) - 1,
                    "opening_read": False,
                    "hidden_cases_generated": 0,
                    "performance_measured": False,
                    "failed": 0,
                },
                allow_nan=False,
                sort_keys=True,
            )
        )
    elif args.command == "final":
        print(json.dumps(final_measurement(args, document), allow_nan=False, sort_keys=True))
    else:
        validate_manifest(document)
        report: dict[str, Any] = {
            "schema": SCHEMA,
            "manifest_sha256": canonical_digest(document),
            "source_sha256": document["source"]["sha256"],
            "cases": CASE_COUNT,
            "apis": len(APIS),
            "workloads": len(WORKLOADS),
            "paired_rounds": PAIRED_ROUNDS,
            "operations_per_sample": OPERATIONS_PER_SAMPLE,
            "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
            "significant_wins_required": MINIMUM_WINS,
            "opening_read": False,
            "previous_holdout_accessed": False,
            "hidden_cases_generated": 0,
            "candidate_imported": False,
            "timing_performed": False,
            "failed": 0,
        }
        if args.evidence:
            evidence = verify_recorded_self_test(document)
            report["poison_rejections"] = evidence["poison_rejections"]
            report["self_test_sha256"] = canonical_digest(evidence)
        print(json.dumps(report, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProtocolError as error:
        print(f"v9 sealed protocol rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error
