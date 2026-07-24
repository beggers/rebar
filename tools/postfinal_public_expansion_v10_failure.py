#!/usr/bin/env python3
"""Preserve the genuine V10 public-selection failure without benchmarking.

``--self-test`` is entirely in-memory.  ``--diagnose`` selectively reads only
the authenticated public archive and the two public parent manifests.  Only
an explicitly requested ``--record`` may exclusively create the single public
failure report.  Archive history, historical results, candidates, workers,
holdouts, timers, and the public archive's fixture manifest are never read.
"""

from __future__ import annotations

import argparse
import builtins
import collections
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-postfinal-public-expansion-freeze-failure-v10"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
DIAGNOSIS_SCHEMA = SCHEMA + "-diagnosis"
RECORDER_RELATIVE = "tools/postfinal_public_expansion_v10_failure.py"
EVIDENCE_RELATIVE = (
    "performance/postfinal-public-v10/evidence/"
    "postfinal-public-freeze-failure-v10.json"
)
FIXTURE_RELATIVE = "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
V6_RELATIVE = "performance/postfinal-public-v6/manifest.json"
V7_RELATIVE = "performance/postfinal-public-v7/manifest.json"
V8_FAILURE_RELATIVE = (
    "performance/postfinal-public-v8/evidence/"
    "postfinal-public-freeze-failure-v8.json"
)
FROZEN_SHA256 = {
    "GOAL.md":
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    "tools/postfinal_public_expansion_v10.py":
        "ae0ff9664939b4d86a25fb860d93c02119a9a195ccf3fc32cbb805170a242065",
    "tools/postfinal_public_practice_v10.py":
        "e99a4241ceb69c6f5e685fd05dab134f585670418738f0bc5cb0da0b61ffa02d",
    "performance/postfinal-public-v10/PROTOCOL.md":
        "e918053c99255e1a528102738e02a1e5979d65eadf0049ef3beed84d26941257",
    V6_RELATIVE:
        "65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a",
    V7_RELATIVE:
        "465c751c6756cbea73bc3dc6d4397e2777d04a107b9a607241697b148c9c5f26",
    FIXTURE_RELATIVE:
        "c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5",
    "tools/postfinal_public_expansion_v8.py":
        "e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97",
    "tools/postfinal_public_practice_v8.py":
        "7818577b36bb822cc99e02a07fcd5ba74e20f1ecf6f0dcb3c0913d2a97bd244f",
    "performance/postfinal-public-v8/PROTOCOL.md":
        "e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095",
    "tools/postfinal_public_expansion_v8_failure.py":
        "800963bc33227c936a2f8506fa80057672acb1c831b772a1bb412aec6540eb94",
    V8_FAILURE_RELATIVE:
        "e46a5b0482293a016c1ba6d0bcadb4c5bcf97ea15af9a2027734ac855c688aba",
}
STAGE10_PINNED_SHA256 = {
    "tools/python_re_universal_public_oracle_stage10.py":
        "a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08",
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md":
        "c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543",
    "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json":
        "5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9",
    "candidates/evidence/python-re-universal-public-oracle-v10-all.json":
        "0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7",
}
FIXTURE_CASES = 10_312
ELIGIBLE_CASES = 9_731
INELIGIBLE_CASES = 581
ORIGINAL_CASES = 8_192
ORIGINAL_SEMANTIC_DISTINCT = 7_900
COLLISION_CLASSES = 87
COLLISION_PARTICIPANTS = 379
COLLISION_EXCESS = 292
MAX_COLLISION_SIZE = 65
DESCRIPTOR_KEYS = frozenset({
    "api", "case", "category", "cohort", "expected_result_sha256",
    "frozen_operations", "input", "lifecycle", "result_count",
    "result_density", "selection_reasons", "subject_length",
})
FAILURE_MESSAGE = "an original public case or semantic identity was repeated"
MAX_SOURCE_BYTES = 64 * 1024 * 1024
CLOCK_NAMES = (
    "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
    "perf_counter_ns", "process_time", "process_time_ns",
)


class FailureEvidenceError(RuntimeError):
    """A public, immutable, selective, or exclusive failure gate failed."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise FailureEvidenceError(message)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("ascii")


def legacy_result_digest(value: Any) -> str:
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise FailureEvidenceError("an authentic result is not UTF-8 JSON") from error
    return hashlib.sha256(encoded).hexdigest()


def candidate_imports() -> list[str]:
    return sorted(
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    )


def require_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and bool(sys.flags.isolated)
        and bool(sys.dont_write_bytecode)
        and Path(sys.executable).resolve() == PINNED_PYTHON.resolve(),
        "the exact isolated, bytecode-free CPython 3.14.6 is required",
    )


def pinned_repository_path(relative: str) -> Path:
    require(isinstance(relative, str) and bool(relative), "invalid public path")
    requested = Path(relative)
    require(
        not requested.is_absolute()
        and ".." not in requested.parts
        and str(requested) == relative,
        "a public path is not canonical",
    )
    path = ROOT / requested
    try:
        resolved = path.resolve(strict=True)
        inside = resolved.relative_to(ROOT.resolve())
    except (OSError, ValueError) as error:
        raise FailureEvidenceError(
            f"an approved public source is missing: {relative}"
        ) from error
    require(
        inside == requested and not path.is_symlink() and path.is_file(),
        f"an approved public source was replaced: {relative}",
    )
    return path


def bounded_sha256(path: Path) -> str:
    require(isinstance(path, Path), "invalid bounded source")
    try:
        metadata = path.stat()
    except OSError as error:
        raise FailureEvidenceError("an approved source is missing") from error
    require(
        path.is_file() and not path.is_symlink()
        and 0 < metadata.st_size <= MAX_SOURCE_BYTES,
        "an approved source is not a bounded regular file",
    )
    hasher = hashlib.sha256()
    observed = 0
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                observed += len(block)
                require(observed <= MAX_SOURCE_BYTES, "public source grew during hashing")
                hasher.update(block)
    except OSError as error:
        raise FailureEvidenceError("an approved source cannot be read") from error
    require(observed == metadata.st_size, "public source changed during hashing")
    return hasher.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in sorted(FROZEN_SHA256.items()):
        actual = bounded_sha256(pinned_repository_path(relative))
        require(actual == expected, f"a pushed public artifact changed: {relative}")
        observed[relative] = actual
    return observed


def verify_stage10_inputs() -> dict[str, str]:
    """Hash the four frozen correctness artifacts without decoding evidence."""
    observed: dict[str, str] = {}
    for relative, expected in sorted(STAGE10_PINNED_SHA256.items()):
        actual = bounded_sha256(pinned_repository_path(relative))
        require(
            actual == expected,
            f"a genuine passing Stage10 correctness artifact changed: {relative}",
        )
        observed[relative] = actual
    require(len(observed) == 4, "an actual Stage10 correctness artifact is absent")
    return observed


def load_public_json(relative: str) -> dict[str, Any]:
    path = pinned_repository_path(relative)
    try:
        with path.open("rb") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, ValueError) as error:
        raise FailureEvidenceError(f"invalid approved public JSON: {relative}") from error
    require(isinstance(document, dict), f"public JSON is not an object: {relative}")
    return document


def load_frozen_decoder() -> Any:
    relative = "tools/postfinal_public_expansion_v10.py"
    path = pinned_repository_path(relative)
    require(
        bounded_sha256(path) == FROZEN_SHA256[relative],
        "the actual failed V10 selective decoder was replaced",
    )
    before = candidate_imports()
    spec = importlib.util.spec_from_file_location(
        "rebar_frozen_public_v10_failure_decoder", path
    )
    require(spec is not None and spec.loader is not None, "V10 cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        raise FailureEvidenceError("the pinned V10 decoder cannot be loaded") from error
    require(candidate_imports() == before, "V10 decoder imported a candidate")
    for name in (
        "decode_public_fixture_line", "semantic_identity", "bounded_public_case",
        "source_kind", "legacy_result_digest", "PublicHistorySpy",
        "validate_v8_failure_document", "json_bytes", "public_subject_length",
        "result_cardinality",
    ):
        require(callable(getattr(module, name, None)), f"V10 lost its public {name}")
    require(
        module.STAGE10_PINNED_SHA256 == STAGE10_PINNED_SHA256,
        "the actual V10 changed the frozen Stage10 correctness fingerprints",
    )
    require(
        module.FIXTURE_CASE_COUNT == FIXTURE_CASES
        and module.ELIGIBLE_PUBLIC_CASES == ELIGIBLE_CASES
        and module.ORIGINAL_CASE_COUNT == ORIGINAL_CASES,
        "the actual V10 changed its public or original denominators",
    )
    return module


def validate_parent_manifests() -> tuple[dict[str, Any], dict[str, Any]]:
    v6 = load_public_json(V6_RELATIVE)
    v7 = load_public_json(V7_RELATIVE)
    for version, parent in ((6, v6), (7, v7)):
        require(
            parent.get("postfinal_schema")
            == f"rebar-postfinal-public-practice-plan-v{version}"
            and parent.get("python") == "3.14.6"
            and parent.get("cohort") == "calibration"
            and type(parent.get("cases")) is int
            and parent["cases"] == ORIGINAL_CASES,
            f"the approved V{version} public-parent header changed",
        )
    selected6 = v6.get("selected_cases")
    selected7 = v7.get("selected_cases")
    require(
        isinstance(selected6, list)
        and isinstance(selected7, list)
        and len(selected6) == ORIGINAL_CASES
        and selected6 == selected7,
        "the original 8,192 V6/V7 public descriptors are not byte-equivalent",
    )
    categories = v7.get("categories")
    operations = v7.get("public_operations")
    require(
        isinstance(categories, dict) and len(categories) == 260
        and all(isinstance(key, str) and type(value) is int and value > 0
                for key, value in categories.items())
        and sum(categories.values()) == ORIGINAL_CASES,
        "the V7 parent changed its 260 original public categories",
    )
    require(
        isinstance(operations, dict) and len(operations) == 12
        and all(isinstance(key, str) and type(value) is int and value > 0
                for key, value in operations.items())
        and sum(operations.values()) == ORIGINAL_CASES,
        "the V7 parent changed its 12 original public operations",
    )
    seen: set[str] = set()
    counted_categories: collections.Counter[str] = collections.Counter()
    counted_operations: collections.Counter[str] = collections.Counter()
    for index, descriptor in enumerate(selected7):
        require(
            isinstance(descriptor, dict) and set(descriptor) == DESCRIPTOR_KEYS,
            f"public original descriptor {index} has unapproved fields",
        )
        identifier = descriptor.get("case")
        category = descriptor.get("category")
        operation = descriptor.get("api")
        require(
            isinstance(identifier, str) and bool(identifier)
            and identifier not in seen and category in categories
            and operation in operations
            and descriptor.get("cohort") == "calibration",
            f"public original descriptor {index} is invalid or duplicated",
        )
        seen.add(identifier)
        counted_categories[category] += 1
        counted_operations[operation] += 1
    require(
        dict(sorted(counted_categories.items())) == categories
        and dict(sorted(counted_operations.items())) == operations,
        "the public parent misstates original workload counts",
    )
    return v6, v7


def diagnose_public_fixture(module: Any, parent: dict[str, Any]) -> dict[str, Any]:
    fixture = pinned_repository_path(FIXTURE_RELATIVE)
    records: dict[str, dict[str, Any]] = {}
    positions: set[int] = set()
    uncompressed = hashlib.sha256()
    spy = module.PublicHistorySpy()
    eligible = 0
    before = candidate_imports()
    try:
        with gzip.open(fixture, "rb") as stream:
            for raw in stream:
                uncompressed.update(raw)
                document = module.decode_public_fixture_line(raw, spy)
                require("historical" not in document, "archive history was exposed")
                require(
                    document.get("schema") == module.FIXTURE_SCHEMA
                    and document.get("cohort") == "calibration",
                    "a non-public archive record was decoded",
                )
                position = document.get("position")
                require(
                    type(position) is int and position >= 0
                    and position not in positions,
                    "a public archive position is invalid or repeated",
                )
                positions.add(position)
                case = document.get("case")
                expected = document.get("expected")
                require(
                    isinstance(case, dict) and isinstance(expected, dict),
                    "a public archive case or reference is invalid",
                )
                identifier = case.get("id")
                require(
                    isinstance(identifier, str) and bool(identifier)
                    and identifier not in records
                    and expected.get("id") == identifier
                    and case.get("cohort") == "calibration"
                    and expected.get("cohort") == "calibration"
                    and case.get("category") == expected.get("category"),
                    "a public archive case and reference do not agree",
                )
                result = expected.get("result")
                recorded = expected.get("result_sha256")
                require(
                    legacy_result_digest(result) == recorded
                    and module.legacy_result_digest(result) == recorded,
                    "a public reference does not match its genuine UTF-8 producer",
                )
                require(
                    module.source_kind(case)
                    in {"text", "bytes", "bytearray", "memoryview"},
                    "a public archive subject has an unsupported input kind",
                )
                eligible += int(module.bounded_public_case(case, expected))
                records[identifier] = {"case": case, "expected": expected}
    except FailureEvidenceError:
        raise
    except Exception as error:
        raise FailureEvidenceError(
            "the exact selective public V10 decoder rejected the public archive"
        ) from error

    require(len(records) == FIXTURE_CASES, "the public archive denominator changed")
    require(
        eligible == ELIGIBLE_CASES
        and len(records) - eligible == INELIGIBLE_CASES,
        "the 9,731 eligible and 581 excluded public denominators changed",
    )
    require(
        spy.history_fields == FIXTURE_CASES and spy.history_value_decodes == 0,
        "an opaque archived history was missing or decoded",
    )

    grouped: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    seen_ids: set[str] = set()
    first_collision: dict[str, Any] | None = None
    for position, descriptor in enumerate(parent["selected_cases"]):
        identifier = descriptor["case"]
        require(
            identifier not in seen_ids and identifier in records,
            "an original public ID is duplicated or absent from its public archive",
        )
        seen_ids.add(identifier)
        record = records[identifier]
        case, expected = record["case"], record["expected"]
        require(
            module.bounded_public_case(case, expected)
            and descriptor["cohort"] == case.get("cohort") == "calibration"
            and descriptor["category"] == case.get("category")
            and descriptor["api"] == case.get("api")
            and descriptor["lifecycle"] == case.get("lifecycle")
            and descriptor["input"] == module.source_kind(case)
            and descriptor["expected_result_sha256"]
            == expected.get("result_sha256")
            and descriptor["subject_length"] == module.public_subject_length(case)
            and descriptor["result_count"]
            == module.result_cardinality(expected["result"]),
            f"an authentic original public descriptor changed at position {position}",
        )
        identity = module.semantic_identity(case)
        require(
            isinstance(identity, str) and len(identity) == 64,
            "the actual V10 semantic identity is invalid",
        )
        member = {
            "position": position,
            "id": identifier,
            "category": descriptor["category"],
            "api": descriptor["api"],
            "reference_result_sha256": expected["result_sha256"],
        }
        previous = grouped[identity]
        if previous and first_collision is None:
            original = previous[0]
            first_collision = {
                "semantic_identity": identity,
                "first_position": original["position"],
                "duplicate_position": position,
                "first_id": original["id"],
                "duplicate_id": identifier,
                "category": descriptor["category"],
                "api": descriptor["api"],
                "first_reference_result_sha256":
                    original["reference_result_sha256"],
                "duplicate_reference_result_sha256":
                    expected["result_sha256"],
            }
        previous.append(member)

    collisions = [
        {"semantic_identity": identity, "size": len(members), "members": members}
        for identity, members in sorted(grouped.items())
        if len(members) > 1
    ]
    participants = sum(item["size"] for item in collisions)
    conflicting = sum(
        len({member["reference_result_sha256"] for member in item["members"]}) > 1
        for item in collisions
    )
    require(
        len(seen_ids) == ORIGINAL_CASES
        and len(grouped) == ORIGINAL_SEMANTIC_DISTINCT
        and len(collisions) == COLLISION_CLASSES
        and participants == COLLISION_PARTICIPANTS
        and participants - len(collisions) == COLLISION_EXCESS
        and max(item["size"] for item in collisions) == MAX_COLLISION_SIZE
        and conflicting == 0,
        "the actual original V10 semantic-collision accounting changed",
    )
    require(
        first_collision is not None
        and first_collision["first_position"] == 136
        and first_collision["duplicate_position"] == 137
        and first_collision["first_id"] == "cal.large.long-ending.00"
        and first_collision["duplicate_id"] == "cal.large.long-ending.01"
        and first_collision["category"] == "large-long-ending"
        and first_collision["api"] == "search"
        and first_collision["first_reference_result_sha256"]
        == first_collision["duplicate_reference_result_sha256"],
        "the real first frozen V10 semantic collision changed",
    )
    require(candidate_imports() == before, "public diagnosis imported a candidate")
    return {
        "public_fixture_cases": len(records),
        "legacy_utf8_digest_matches": len(records),
        "eligible_public_cases": eligible,
        "excluded_public_cases": len(records) - eligible,
        "opaque_history_fields_skipped": spy.history_fields,
        "opaque_history_values_deserialized": spy.history_value_decodes,
        "public_uncompressed_sha256": uncompressed.hexdigest(),
        "original_case_count": len(seen_ids),
        "original_unique_identifier_count": len(seen_ids),
        "original_semantic_distinct_count": len(grouped),
        "original_semantic_duplicate_class_count": len(collisions),
        "original_semantic_duplicate_participant_count": participants,
        "original_semantic_duplicate_record_count": participants - len(collisions),
        "original_semantic_max_group_size": max(item["size"] for item in collisions),
        "conflicting_reference_result_digest_groups": conflicting,
        "first_semantic_collision": first_collision,
        "original_semantic_collision_groups": collisions,
    }


def stage10_contract(module: Any) -> dict[str, Any]:
    require(
        module.STAGE10_PINNED_SHA256 == STAGE10_PINNED_SHA256
        and module.STAGE10_CASES == 3_584
        and module.STAGE10_COHORTS == 8
        and module.STAGE10_MATRIX_SHA256
        == "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db",
        "the failed V10 source no longer binds the real passing Stage10",
    )
    return {
        "source_path": "tools/python_re_universal_public_oracle_stage10.py",
        "source_sha256": STAGE10_PINNED_SHA256[
            "tools/python_re_universal_public_oracle_stage10.py"
        ],
        "protocol_path": "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md",
        "protocol_sha256": STAGE10_PINNED_SHA256[
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md"
        ],
        "self_oracle_path":
            "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json",
        "self_oracle_sha256": STAGE10_PINNED_SHA256[
            "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json"
        ],
        "all_candidates_path":
            "candidates/evidence/python-re-universal-public-oracle-v10-all.json",
        "all_candidates_sha256": STAGE10_PINNED_SHA256[
            "candidates/evidence/python-re-universal-public-oracle-v10-all.json"
        ],
        "matrix_sha256": module.STAGE10_MATRIX_SHA256,
        "cohorts": module.STAGE10_COHORTS,
        "cases": module.STAGE10_CASES,
        "stdlib_checks": 7_168,
        "candidate_checks": 10_752,
    }


def collect_diagnosis() -> tuple[dict[str, str], dict[str, Any], dict[str, Any], dict[str, Any]]:
    require_runtime()
    before = candidate_imports()
    require(not before, "a candidate was already loaded into failure diagnosis")
    fingerprints = verify_frozen_inputs()
    stage10_fingerprints = verify_stage10_inputs()
    module = load_frozen_decoder()
    _v6, v7 = validate_parent_manifests()
    try:
        v8 = module.validate_v8_failure_document(load_public_json(V8_FAILURE_RELATIVE))
    except FailureEvidenceError:
        raise
    except Exception as error:
        raise FailureEvidenceError("the genuine V8 failure was modified") from error
    require(isinstance(v8, dict) and len(v8) == 18, "V8 failure proof is not exact")
    diagnosis = diagnose_public_fixture(module, v7)
    correctness = stage10_contract(module)
    require(
        verify_frozen_inputs() == fingerprints,
        "a frozen public source changed during selective collision diagnosis",
    )
    require(
        verify_stage10_inputs() == stage10_fingerprints,
        "a passing Stage10 correctness artifact changed during diagnosis",
    )
    require(not candidate_imports(), "failure diagnosis imported a candidate")
    return fingerprints, diagnosis, v8, correctness


def evidence_document(
    fingerprints: dict[str, str], diagnosis: dict[str, Any],
    v8: dict[str, Any], correctness: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "frozen_design": {
            "goal_path": "GOAL.md",
            "goal_sha256": fingerprints["GOAL.md"],
            "expander_path": "tools/postfinal_public_expansion_v10.py",
            "expander_sha256": fingerprints["tools/postfinal_public_expansion_v10.py"],
            "runner_path": "tools/postfinal_public_practice_v10.py",
            "runner_sha256": fingerprints["tools/postfinal_public_practice_v10.py"],
            "protocol_path": "performance/postfinal-public-v10/PROTOCOL.md",
            "protocol_sha256": fingerprints["performance/postfinal-public-v10/PROTOCOL.md"],
            "v6_parent_path": V6_RELATIVE,
            "v6_parent_sha256": fingerprints[V6_RELATIVE],
            "v7_parent_path": V7_RELATIVE,
            "v7_parent_sha256": fingerprints[V7_RELATIVE],
            "fixture_path": FIXTURE_RELATIVE,
            "fixture_sha256": fingerprints[FIXTURE_RELATIVE],
        },
        "failure": {
            "phase": "pre-candidate original public-case semantic selection",
            "class": "PublicExpansionError",
            "module": "tools.postfinal_public_expansion_v8",
            "message": FAILURE_MESSAGE,
            "source_path": "tools/postfinal_public_expansion_v10.py",
            "source_line": 814,
            "exit_code": 1,
            "cause": (
                "The preserved 8,192 V6/V7 public case identifiers are unique, "
                "but only 7,900 actual V10 semantic identities are unique. "
                "The immutable original-selection uniqueness gate rejects the "
                "first repeated semantic identity before starting any worker."
            ),
        },
        "reproduction": {
            "mode": "direct pinned isolated frozen V10 practice runner",
            "command": (
                "env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "
                + str(PINNED_PYTHON)
                + " -I -B tools/postfinal_public_practice_v10.py --freeze"
            ),
            "exit_code": 1,
            "exception_class": "PublicExpansionError",
            "exception_module": "tools.postfinal_public_expansion_v8",
            "message": FAILURE_MESSAGE,
            "failure_source_path": "tools/postfinal_public_expansion_v10.py",
            "failure_source_line": 814,
            "executed_by_recorder": False,
        },
        "public_fixture_diagnosis": diagnosis,
        "v8_failure": v8,
        "stage10_correctness": correctness,
        "recording_source_path": RECORDER_RELATIVE,
        "recording_source_sha256": bounded_sha256(Path(__file__).resolve()),
        "production_manifest_created": False,
        "production_cases_generated": 0,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "clock_samples": 0,
        "held_out_records_deserialized": 0,
        "performance": "NOT MEASURED",
    }


def exclusive_record(document: dict[str, Any]) -> Path:
    output = ROOT / EVIDENCE_RELATIVE
    expected_root = (ROOT / "performance/postfinal-public-v10").resolve()
    parent = output.parent
    require(
        parent.parent.resolve() == expected_root,
        "the V10 report escaped its exact public directory",
    )
    if not parent.exists():
        parent.mkdir(mode=0o755, parents=False, exist_ok=False)
    require(
        parent.is_dir() and not parent.is_symlink()
        and parent.resolve().parent == expected_root,
        "the V10 failure evidence directory was replaced",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(output, flags, 0o644)
    except FileExistsError as error:
        raise FailureEvidenceError("the V10 failure report already exists") from error
    except OSError as error:
        raise FailureEvidenceError("the exclusive V10 report cannot be created") from error
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical_json(document) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    directory = os.open(parent, directory_flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return output


def diagnose() -> None:
    fingerprints, diagnosis, v8, correctness = collect_diagnosis()
    require(
        len(fingerprints) == len(FROZEN_SHA256)
        and len(v8) == 18 and len(correctness) == 13,
        "the read-only public failure contracts changed",
    )
    print(json.dumps({
        "schema": DIAGNOSIS_SCHEMA,
        "status": "PASS",
        "failed_design_status": "FAIL",
        "failure_class": "PublicExpansionError",
        "failure_message": FAILURE_MESSAGE,
        "public_fixture_cases": diagnosis["public_fixture_cases"],
        "eligible_public_cases": diagnosis["eligible_public_cases"],
        "excluded_public_cases": diagnosis["excluded_public_cases"],
        "opaque_history_fields_skipped": diagnosis["opaque_history_fields_skipped"],
        "opaque_history_values_deserialized": 0,
        "original_case_count": diagnosis["original_case_count"],
        "original_semantic_distinct_count":
            diagnosis["original_semantic_distinct_count"],
        "original_semantic_duplicate_class_count":
            diagnosis["original_semantic_duplicate_class_count"],
        "original_semantic_duplicate_participant_count":
            diagnosis["original_semantic_duplicate_participant_count"],
        "original_semantic_duplicate_record_count":
            diagnosis["original_semantic_duplicate_record_count"],
        "original_semantic_max_group_size":
            diagnosis["original_semantic_max_group_size"],
        "conflicting_reference_result_digest_groups":
            diagnosis["conflicting_reference_result_digest_groups"],
        "first_semantic_collision": diagnosis["first_semantic_collision"],
        "v8_failure_preserved": True,
        "stage10_correctness_preserved": True,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "clock_samples": 0,
        "files_written": 0,
        "evidence_recorded": False,
        "performance": "NOT MEASURED",
    }, sort_keys=True, ensure_ascii=True))


def record() -> None:
    fingerprints, diagnosis, v8, correctness = collect_diagnosis()
    document = evidence_document(fingerprints, diagnosis, v8, correctness)
    output = exclusive_record(document)
    print(json.dumps({
        "schema": SCHEMA,
        "status": "RECORDED",
        "design_result": "FAIL",
        "evidence": str(output.relative_to(ROOT)),
        "original_semantic_duplicate_class_count": COLLISION_CLASSES,
        "original_semantic_duplicate_participant_count": COLLISION_PARTICIPANTS,
        "original_semantic_duplicate_record_count": COLLISION_EXCESS,
        "opaque_history_values_deserialized": 0,
        "candidate_processes": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
    }, sort_keys=True, ensure_ascii=True))


def _skip_opaque(source: str, offset: int) -> int:
    while offset < len(source) and source[offset] in " \t\r\n":
        offset += 1
    require(offset < len(source), "synthetic opaque history is truncated")
    first = source[offset]
    if first == '"':
        cursor = offset + 1
        while cursor < len(source):
            if source[cursor] == "\\":
                cursor += 2
            elif source[cursor] == '"':
                return cursor + 1
            else:
                cursor += 1
        raise FailureEvidenceError("synthetic opaque string is incomplete")
    if first in "[{":
        stack = ["]" if first == "[" else "}"]
        cursor = offset + 1
        quoted = False
        while cursor < len(source) and stack:
            character = source[cursor]
            if quoted:
                if character == "\\":
                    cursor += 2
                    continue
                if character == '"':
                    quoted = False
            elif character == '"':
                quoted = True
            elif character in "[{":
                stack.append("]" if character == "[" else "}")
            elif character in "]}":
                require(character == stack.pop(), "synthetic opaque brackets mismatch")
            cursor += 1
        require(not stack and not quoted, "synthetic opaque history is incomplete")
        return cursor
    cursor = offset
    while cursor < len(source) and source[cursor] not in ",}] \t\r\n":
        cursor += 1
    require(cursor > offset, "synthetic opaque scalar is invalid")
    return cursor


class SyntheticHistorySpy:
    def __init__(self) -> None:
        self.parser = json.JSONDecoder()
        self.history_fields = 0
        self.history_value_decodes = 0
        self.pending_history = False

    def raw_decode(self, text: str, index: int = 0) -> tuple[Any, int]:
        if self.pending_history:
            cursor = index
            while cursor < len(text) and text[cursor] in " \t\r\n":
                cursor += 1
            if cursor >= len(text) or text[cursor] != '"':
                self.history_value_decodes += 1
                raise FailureEvidenceError("synthetic archive history was decoded")
        value, end = self.parser.raw_decode(text, index)
        if self.pending_history:
            if not isinstance(value, str) or value not in {
                "schema", "cohort", "position", "case", "expected",
            }:
                self.history_value_decodes += 1
                raise FailureEvidenceError("synthetic opaque history was deserialized")
            self.pending_history = False
        if value == "historical":
            self.history_fields += 1
            self.pending_history = True
        return value, end


def decode_synthetic(raw: bytes, spy: SyntheticHistorySpy) -> dict[str, Any]:
    try:
        source = raw.decode("utf-8")
    except UnicodeError as error:
        raise FailureEvidenceError("synthetic public line is invalid UTF-8") from error

    def trim(position: int) -> int:
        while position < len(source) and source[position] in " \t\r\n":
            position += 1
        return position

    offset = trim(0)
    require(offset < len(source) and source[offset] == "{", "invalid synthetic object")
    offset += 1
    public = frozenset({"schema", "cohort", "position", "case", "expected"})
    observed: set[str] = set()
    result: dict[str, Any] = {}
    while True:
        offset = trim(offset)
        require(offset < len(source), "truncated synthetic object")
        if source[offset] == "}":
            offset += 1
            break
        try:
            key, offset = spy.raw_decode(source, offset)
        except (ValueError, UnicodeError) as error:
            raise FailureEvidenceError("invalid synthetic public field") from error
        require(
            isinstance(key, str) and key not in observed
            and (key in public or key == "historical"),
            "repeated or forbidden synthetic public field",
        )
        observed.add(key)
        offset = trim(offset)
        require(offset < len(source) and source[offset] == ":", "missing synthetic colon")
        offset = trim(offset + 1)
        if key == "historical":
            offset = _skip_opaque(source, offset)
        else:
            try:
                value, offset = spy.raw_decode(source, offset)
            except (ValueError, UnicodeError) as error:
                raise FailureEvidenceError("invalid synthetic public value") from error
            result[key] = value
        offset = trim(offset)
        require(offset < len(source), "truncated synthetic separator")
        if source[offset] == "}":
            offset += 1
            break
        require(source[offset] == ",", "invalid synthetic separator")
        offset += 1
    require(trim(offset) == len(source), "trailing synthetic fixture content")
    require(set(result) == public, "incomplete synthetic public record")
    return result


def synthetic_identity(case: dict[str, Any]) -> str:
    required = ("api", "pattern", "flags", "string", "lifecycle")
    require(isinstance(case, dict) and all(key in case for key in required),
            "incomplete synthetic semantic identity")
    nonsemantic = {
        "api", "pattern", "flags", "string", "lifecycle", "id",
        "category", "cohort", "ops", "weight",
    }
    arguments = {key: value for key, value in case.items() if key not in nonsemantic}
    return hashlib.sha256(canonical_json([
        case["api"], case["pattern"], case["flags"], case["string"],
        case["lifecycle"], arguments,
    ])).hexdigest()


def self_test() -> None:
    require_runtime()
    checks: list[str] = []
    blocked: collections.Counter[str] = collections.Counter()
    before = candidate_imports()
    require(not before, "a candidate entered the synthetic failure self-test")
    old_run = subprocess.run
    old_popen = subprocess.Popen
    old_gzip = gzip.open
    old_builtin_open = builtins.open
    old_path_open = Path.open
    old_read = Path.read_bytes
    old_os_open = os.open
    old_clocks = {name: getattr(time, name) for name in CLOCK_NAMES}

    def reject(kind: str) -> Any:
        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            blocked[kind] += 1
            raise FailureEvidenceError("synthetic failure blocked " + kind)
        return forbidden

    def check(name: str, value: object) -> None:
        require(name not in checks, "synthetic control was counted twice")
        require(value, "synthetic failure control failed: " + name)
        checks.append(name)

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except FailureEvidenceError:
            check(name, True)
        else:
            raise FailureEvidenceError("synthetic poison was accepted: " + name)

    subprocess.run = reject("worker")  # type: ignore[assignment]
    subprocess.Popen = reject("process")  # type: ignore[assignment]
    gzip.open = reject("fixture")  # type: ignore[assignment]
    builtins.open = reject("builtin-file")  # type: ignore[assignment]
    Path.open = reject("path")  # type: ignore[assignment]
    Path.read_bytes = reject("file")  # type: ignore[assignment]
    os.open = reject("output")  # type: ignore[assignment]
    for name in CLOCK_NAMES:
        setattr(time, name, reject("clock"))

    try:
        check("exact-root-bootstrap", sys.path[0] == str(ROOT))
        check("all-twelve-pushed-inputs-pinned", len(FROZEN_SHA256) == 12)
        check("immutable-objective-is-pinned", FROZEN_SHA256["GOAL.md"] ==
              "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62")
        check("failed-v10-generator-is-pinned", FROZEN_SHA256[
            "tools/postfinal_public_expansion_v10.py"] ==
              "ae0ff9664939b4d86a25fb860d93c02119a9a195ccf3fc32cbb805170a242065")
        check("failed-v10-runner-is-pinned", FROZEN_SHA256[
            "tools/postfinal_public_practice_v10.py"] ==
              "e99a4241ceb69c6f5e685fd05dab134f585670418738f0bc5cb0da0b61ffa02d")
        check("failed-v10-protocol-is-pinned", FROZEN_SHA256[
            "performance/postfinal-public-v10/PROTOCOL.md"] ==
              "e918053c99255e1a528102738e02a1e5979d65eadf0049ef3beed84d26941257")
        check("both-parent-manifests-are-pinned",
              V6_RELATIVE in FROZEN_SHA256 and V7_RELATIVE in FROZEN_SHA256)
        check("compressed-public-fixture-is-pinned", FROZEN_SHA256[FIXTURE_RELATIVE] ==
              "c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5")
        check("genuine-v8-failure-is-pinned", FROZEN_SHA256[V8_FAILURE_RELATIVE] ==
              "e46a5b0482293a016c1ba6d0bcadb4c5bcf97ea15af9a2027734ac855c688aba")
        check("all-four-stage10-contract-fingerprints-pinned",
              len(STAGE10_PINNED_SHA256) == 4)
        check("stage10-source-fingerprint-is-pinned", STAGE10_PINNED_SHA256[
            "tools/python_re_universal_public_oracle_stage10.py"] ==
              "a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08")
        check("stage10-protocol-fingerprint-is-pinned", STAGE10_PINNED_SHA256[
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md"] ==
              "c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543")
        check("stage10-python-oracle-fingerprint-is-pinned", STAGE10_PINNED_SHA256[
            "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json"] ==
              "5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9")
        check("stage10-candidate-proof-fingerprint-is-pinned", STAGE10_PINNED_SHA256[
            "candidates/evidence/python-re-universal-public-oracle-v10-all.json"] ==
              "0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7")
        check("public-denominator-is-10312", FIXTURE_CASES == 10_312)
        check("eligibility-denominators-are-exact",
              ELIGIBLE_CASES == 9_731 and INELIGIBLE_CASES == 581
              and ELIGIBLE_CASES + INELIGIBLE_CASES == FIXTURE_CASES)
        check("original-case-denominator-is-8192", ORIGINAL_CASES == 8_192)
        check("genuine-distinct-semantic-denominator-is-7900",
              ORIGINAL_SEMANTIC_DISTINCT == 7_900)
        check("genuine-collision-accounting-is-exact",
              COLLISION_CLASSES == 87 and COLLISION_PARTICIPANTS == 379
              and COLLISION_EXCESS == 292
              and COLLISION_PARTICIPANTS - COLLISION_CLASSES == COLLISION_EXCESS
              and ORIGINAL_CASES - ORIGINAL_SEMANTIC_DISTINCT == COLLISION_EXCESS
              and MAX_COLLISION_SIZE == 65)
        check("genuine-error-message-is-preserved",
              FAILURE_MESSAGE == "an original public case or semantic identity was repeated")
        check("actual-report-is-exclusive-and-v10-only",
              EVIDENCE_RELATIVE ==
              "performance/postfinal-public-v10/evidence/"
              "postfinal-public-freeze-failure-v10.json")
        check("forbidden-fixture-manifest-is-not-approved",
              not any("fixture-manifest" in item for item in FROZEN_SHA256))
        check("authentic-unicode-result-uses-unescaped-utf8",
              legacy_result_digest(["caf\u00e9", "\u03a9"])
              != hashlib.sha256(canonical_json(["caf\u00e9", "\u03a9"])).hexdigest())
        check("unicode-result-codec-is-deterministic",
              legacy_result_digest(["caf\u00e9", "\u03a9"])
              == legacy_result_digest(["caf\u00e9", "\u03a9"]))

        original = {
            "id": "cal.synthetic.00", "cohort": "calibration",
            "category": "synthetic", "api": "search", "pattern": "x+$",
            "flags": 0, "string": "xxx", "lifecycle": "compiled", "weight": 1,
        }
        duplicated = dict(original, id="cal.synthetic.01")
        check("distinct-original-identifiers-can-collide-semantically",
              original["id"] != duplicated["id"]
              and synthetic_identity(original) == synthetic_identity(duplicated))
        for key, value in (
            ("api", "match"), ("pattern", "y+$"), ("flags", 2),
            ("string", "yyy"), ("lifecycle", "module"), ("limit", 2),
        ):
            changed = dict(original)
            changed[key] = value
            check("semantic-mutation-is-rejected-" + key,
                  synthetic_identity(changed) != synthetic_identity(original))

        value = ["caf\u00e9", "\u03a9"]
        synthetic = {
            "schema": "rebar-rust-sealed-calibration-fixture-v7",
            "cohort": "calibration", "position": 0,
            "case": original,
            "expected": {
                "id": original["id"], "cohort": "calibration",
                "category": "synthetic", "result": value,
                "result_sha256": legacy_result_digest(value),
            },
            "historical": {"poison": [{"never": "decode"}, {"nested": [1, 2]}]},
        }
        spy = SyntheticHistorySpy()
        decoded = decode_synthetic(canonical_json(synthetic) + b"\n", spy)
        check("selective-decoder-retains-only-five-public-fields",
              set(decoded) == {"schema", "cohort", "position", "case", "expected"})
        check("opaque-archive-history-is-never-returned", "historical" not in decoded)
        check("opaque-archive-history-key-is-counted", spy.history_fields == 1)
        check("opaque-archive-history-value-is-never-decoded",
              spy.history_value_decodes == 0)
        check("synthetic-reference-remains-valid-utf8",
              legacy_result_digest(decoded["expected"]["result"])
              == decoded["expected"]["result_sha256"])

        poison = SyntheticHistorySpy()
        poison.pending_history = True
        rejected("history-value-deserialization-is-rejected",
                 lambda: poison.raw_decode('{"secret":true}', 0))
        check("attempted-history-deserialization-is-counted",
              poison.history_value_decodes == 1)
        rejected("worker-start-is-blocked", lambda: subprocess.run(["forbidden"]))
        rejected("process-start-is-blocked", lambda: subprocess.Popen(["forbidden"]))
        rejected("compressed-fixture-read-is-blocked",
                 lambda: gzip.open("forbidden.jsonl.gz", "rb"))
        rejected("builtin-file-read-is-blocked",
                 lambda: builtins.open("forbidden", "rb"))
        rejected("path-read-is-blocked", lambda: Path("forbidden").open("rb"))
        rejected("read-bytes-is-blocked", lambda: Path("forbidden").read_bytes())
        rejected("exclusive-output-is-blocked",
                 lambda: os.open("forbidden", os.O_WRONLY | os.O_CREAT | os.O_EXCL))
        for name in CLOCK_NAMES:
            rejected("clock-is-blocked-" + name,
                     lambda clock=name: getattr(time, clock)())
        check("all-forbidden-file-worker-and-clock-guards-fired",
              dict(blocked) == {
                  "worker": 1, "process": 1, "fixture": 1,
                  "builtin-file": 1, "path": 1, "file": 1,
                  "output": 1, "clock": len(CLOCK_NAMES),
              })
        check("synthetic-self-test-imported-no-candidate", not candidate_imports())
    finally:
        subprocess.run = old_run  # type: ignore[assignment]
        subprocess.Popen = old_popen  # type: ignore[assignment]
        gzip.open = old_gzip  # type: ignore[assignment]
        builtins.open = old_builtin_open  # type: ignore[assignment]
        Path.open = old_path_open  # type: ignore[assignment]
        Path.read_bytes = old_read  # type: ignore[assignment]
        os.open = old_os_open  # type: ignore[assignment]
        for name, clock in old_clocks.items():
            setattr(time, name, clock)

    print(json.dumps({
        "schema": SELF_TEST_SCHEMA, "status": "PASS",
        "synthetic_controls": len(checks), "checks": checks,
        "actual_public_fixture_rows_read": 0,
        "actual_archived_history_values_deserialized": 0,
        "candidate_imports": [], "candidate_processes": 0,
        "clock_samples": 0, "files_read": 0, "files_written": 0,
        "evidence_recorded": False, "performance": "NOT MEASURED",
    }, sort_keys=True, ensure_ascii=True))


def main(arguments: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run in-memory mutation, history, worker, and clock controls")
    modes.add_argument("--diagnose", action="store_true",
                       help="selectively verify public collision data without writing")
    modes.add_argument("--record", action="store_true",
                       help="exclusively record the authenticated actual V10 failure")
    values = parser.parse_args(arguments)
    if values.self_test:
        self_test()
    elif values.diagnose:
        diagnose()
    else:
        record()


if __name__ == "__main__":
    try:
        main()
    except FailureEvidenceError as error:
        print(json.dumps({
            "schema": SCHEMA, "status": "FAIL", "error": str(error),
            "performance": "NOT MEASURED",
        }, sort_keys=True, ensure_ascii=True), file=sys.stderr)
        raise SystemExit(1) from error
