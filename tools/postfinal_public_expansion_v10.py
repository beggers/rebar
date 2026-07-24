#!/usr/bin/env python3
"""Freeze a corrected public-only, independently verified V10 comparison."""

from __future__ import annotations

import sys
from pathlib import Path


# ``python -I -B tools/...py`` deliberately ignores PYTHONPATH. Establish the
# exact repository root before importing either of the owned tools packages.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import collections
import gzip
import hashlib
import json
import os
import subprocess
import time
from typing import Any, Callable

from tools import postfinal_public_expansion_v8 as frozen_v8


PublicExpansionError = frozen_v8.PublicExpansionError
require = frozen_v8.require
json_bytes = frozen_v8.json_bytes
digest = frozen_v8.digest
canonical = frozen_v8.canonical
semantic_identity = frozen_v8.semantic_identity
unpack = frozen_v8.unpack
snapshot = frozen_v8.snapshot
decode_public_fixture_line = frozen_v8.decode_public_fixture_line
source_file_sha256 = frozen_v8.source_file_sha256
bounded_source_file_sha256 = frozen_v8.bounded_source_file_sha256
validate_public_source_documents = frozen_v8.validate_public_source_documents
validate_candidate_proofs = frozen_v8.validate_candidate_proofs
validate_stage10_pinset = frozen_v8.validate_stage10_pinset
validate_stage10_documents = frozen_v8.validate_stage10_documents
verify_live_owned_artifacts = frozen_v8.verify_live_owned_artifacts
result_cardinality = frozen_v8.result_cardinality
result_density = frozen_v8.result_density
source_kind = frozen_v8.source_kind
effective_subject = frozen_v8.effective_subject
append_public_pattern = frozen_v8.append_public_pattern
oracle_result = frozen_v8.oracle_result

PINNED_PYTHON = frozen_v8.PINNED_PYTHON
SEED_DOMAIN = "rebar/public-development/v10"
SELECTION_SEED = 2_026_072_450
ORDER_SEED = 2_026_072_451
BOOTSTRAP_SEED = 2_026_072_452
ORDER_SEED_DOMAIN = f"{SEED_DOMAIN}/paired-order"
BOOTSTRAP_SEED_DOMAIN = f"{SEED_DOMAIN}/bootstrap"
SCHEMA = "rebar-postfinal-public-development-plan-v10"
ORACLE_SCHEMA = "rebar-postfinal-public-development-self-oracle-v10"
SELF_TEST_SCHEMA = "rebar-postfinal-public-development-self-test-v10"
FIXTURE_VERIFICATION_SCHEMA = (
    "rebar-postfinal-public-development-fixture-verification-v10"
)
GENERATOR_RELATIVE = "tools/postfinal_public_expansion_v10.py"
MEASUREMENT_RUNNER_RELATIVE = "tools/postfinal_public_practice_v10.py"
PROTOCOL_RELATIVE = "performance/postfinal-public-v10/PROTOCOL.md"
MANIFEST_RELATIVE = "performance/postfinal-public-v10/manifest.json"
CATEGORY_COUNT = frozen_v8.CATEGORY_COUNT
CASES_PER_CATEGORY = frozen_v8.CASES_PER_CATEGORY
CASE_COUNT = frozen_v8.CASE_COUNT
ORIGINAL_CASE_COUNT = frozen_v8.ORIGINAL_CASE_COUNT
FIXTURE_CASE_COUNT = frozen_v8.FIXTURE_CASE_COUNT
ELIGIBLE_PUBLIC_CASES = 9_731
WARMUPS = frozen_v8.WARMUPS
PAIRED_TRIALS = frozen_v8.PAIRED_TRIALS
BOOTSTRAP_DRAWS = frozen_v8.BOOTSTRAP_DRAWS
SUBJECT_LIMIT = frozen_v8.SUBJECT_LIMIT
RESULT_LIMIT = frozen_v8.RESULT_LIMIT
MAX_PROGRAM_SOURCE_BYTES = frozen_v8.MAX_PROGRAM_SOURCE_BYTES
MAX_PROTOCOL_BYTES = frozen_v8.MAX_PROTOCOL_BYTES
MAX_OWNED_ARTIFACT_BYTES = frozen_v8.MAX_OWNED_ARTIFACT_BYTES
BASELINE = frozen_v8.BASELINE
CANDIDATES = frozen_v8.CANDIDATES
REQUIRED_FAMILIES = frozen_v8.REQUIRED_FAMILIES
REQUIRED_NATIVE_ROLES = frozen_v8.REQUIRED_NATIVE_ROLES
REQUIRED_NATIVE_FILES = frozen_v8.REQUIRED_NATIVE_FILES
NATIVE_RECORD_ROLES = frozen_v8.NATIVE_RECORD_ROLES
REQUIRED_SOURCE_PATHS = frozen_v8.REQUIRED_SOURCE_PATHS
PUBLIC_OPERATIONS = frozen_v8.PUBLIC_OPERATIONS
FIXTURE_SCHEMA = frozen_v8.FIXTURE_SCHEMA
FIXTURE_MANIFEST_SCHEMA = frozen_v8.FIXTURE_MANIFEST_SCHEMA
PACKING_MARKER = frozen_v8.PACKING_MARKER
STAGE10_SOURCE_RELATIVE = frozen_v8.STAGE10_SOURCE_RELATIVE
STAGE10_PROTOCOL_RELATIVE = frozen_v8.STAGE10_PROTOCOL_RELATIVE
STAGE10_SELF_ORACLE_RELATIVE = frozen_v8.STAGE10_SELF_ORACLE_RELATIVE
STAGE10_ALL_CANDIDATES_RELATIVE = frozen_v8.STAGE10_ALL_CANDIDATES_RELATIVE
STAGE10_SELF_ORACLE_SCHEMA = frozen_v8.STAGE10_SELF_ORACLE_SCHEMA
STAGE10_ALL_CANDIDATES_SCHEMA = frozen_v8.STAGE10_ALL_CANDIDATES_SCHEMA
STAGE10_NATIVE_LOADER_ALIASES = frozen_v8.STAGE10_NATIVE_LOADER_ALIASES
STAGE10_PINNED_SHA256 = dict(frozen_v8.STAGE10_PINNED_SHA256)
STAGE10_MATRIX_SHA256 = frozen_v8.STAGE10_MATRIX_SHA256
STAGE10_CASES = frozen_v8.STAGE10_CASES
STAGE10_COHORTS = frozen_v8.STAGE10_COHORTS
STAGE10_COHORT_CASES = dict(frozen_v8.STAGE10_COHORT_CASES)

V8_SOURCE_RELATIVE = "tools/postfinal_public_expansion_v8.py"
V8_RUNNER_RELATIVE = "tools/postfinal_public_practice_v8.py"
V8_PROTOCOL_RELATIVE = "performance/postfinal-public-v8/PROTOCOL.md"
V8_RECORDER_RELATIVE = "tools/postfinal_public_expansion_v8_failure.py"
V8_FAILURE_RELATIVE = (
    "performance/postfinal-public-v8/evidence/"
    "postfinal-public-freeze-failure-v8.json"
)
V7_PUBLIC_MANIFEST_RELATIVE = "performance/postfinal-public-v7/manifest.json"
V7_PUBLIC_MANIFEST_SHA256 = (
    "465c751c6756cbea73bc3dc6d4397e2777d04a107b9a607241697b148c9c5f26"
)
V8_FAILURE_PINNED_SHA256 = {
    V8_SOURCE_RELATIVE:
        "e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97",
    V8_RUNNER_RELATIVE:
        "7818577b36bb822cc99e02a07fcd5ba74e20f1ecf6f0dcb3c0913d2a97bd244f",
    V8_PROTOCOL_RELATIVE:
        "e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095",
    V8_RECORDER_RELATIVE:
        "800963bc33227c936a2f8506fa80057672acb1c831b772a1bb412aec6540eb94",
    V8_FAILURE_RELATIVE:
        "e46a5b0482293a016c1ba6d0bcadb4c5bcf97ea15af9a2027734ac855c688aba",
}
PUBLIC_FILE_SHA256 = {
    **frozen_v8.PUBLIC_FILE_SHA256,
    **V8_FAILURE_PINNED_SHA256,
    V7_PUBLIC_MANIFEST_RELATIVE: V7_PUBLIC_MANIFEST_SHA256,
}
V8_FIRST_FAILURE = {
    "id": "cal.unicode.words",
    "api": "findall",
    "category": "unicode",
    "cohort": "calibration",
    "recorded_sha256":
        "21f3db7cbb6c5d5bb6fcaf4dc6847779d647399a97f9e62a62861733a4fa1949",
    "legacy_utf8_sha256":
        "21f3db7cbb6c5d5bb6fcaf4dc6847779d647399a97f9e62a62861733a4fa1949",
    "frozen_v8_ascii_sha256":
        "af46c189444aa11a5f11a6894aaac409e79913384e82e6ea96e6668468f10885",
}
V8_AFFECTED_CASES = 577
V8_AFFECTED_APIS = {"escape": 48, "findall": 483, "split": 46}
V8_AFFECTED_INPUTS = {"text": 577}
V7_BOUNDED_PUBLIC_API_CAPACITIES = {
    "compile": 210,
    "escape": 161,
    "findall": 2_882,
    "finditer": 2_738,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 427,
    "search": 1_057,
    "split": 451,
    "sub": 447,
    "subn": 530,
}
STAGE10_CONTRACT_KEYS = frozenset({
    "source_path", "source_sha256", "protocol_path", "protocol_sha256",
    "self_oracle_path", "self_oracle_sha256", "all_candidates_path",
    "all_candidates_sha256", "matrix_sha256", "cohorts", "cases",
    "stdlib_checks", "candidate_checks",
})
V8_FAILURE_CONTRACT_KEYS = frozenset({
    "source_path", "source_sha256", "runner_path", "runner_sha256",
    "protocol_path", "protocol_sha256", "recorder_path", "recorder_sha256",
    "report_path", "report_sha256", "status", "failure_class",
    "public_fixture_cases", "failed_reference_answers", "first_failure_id",
    "first_failure_legacy_utf8_sha256",
    "first_failure_frozen_v8_ascii_sha256",
    "opaque_history_values_deserialized",
})
PROGRAM_KEYS = frozenset({
    "runner_path", "runner_sha256", "protocol_path", "protocol_sha256",
    "measurement_runner_path", "measurement_runner_sha256",
})
CLOCK_NAMES = (
    "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
    "perf_counter_ns", "process_time", "process_time_ns",
)


def legacy_result_digest(value: Any) -> str:
    """Use the exact original V5 UTF-8 result codec, never structural JSON."""
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise PublicExpansionError(
            "public regex result is not valid original UTF-8 JSON"
        ) from error
    return hashlib.sha256(encoded).hexdigest()


def seed_key(
    label: str, *, domain: str = SEED_DOMAIN, seed: int = SELECTION_SEED
) -> tuple[bytes, str]:
    require(isinstance(label, str) and bool(label), "empty V10 selection label")
    require(isinstance(domain, str) and bool(domain), "missing V10 seed domain")
    require(isinstance(seed, int) and not isinstance(seed, bool),
            "invalid V10 selection seed")
    return hashlib.sha256(json_bytes([domain, seed, label])).digest(), label


def candidate_imports() -> list[str]:
    return sorted(name for name in sys.modules
                  if name == "candidates" or name.startswith("candidates."))


def _expected_failure_reproduction() -> list[dict[str, Any]]:
    prefix = (
        "env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "
        f"{PINNED_PYTHON} -I -B "
    )
    return [
        {
            "mode": "direct isolated frozen practice runner",
            "command": prefix + "tools/postfinal_public_practice_v8.py --freeze",
            "exception_class": "ModuleNotFoundError",
            "exception_module": "builtins",
            "message": "No module named 'tools'",
        },
        {
            "mode": "isolated frozen practice runner with explicit repository root",
            "command": (
                prefix + "-c 'import sys;sys.path.insert(0,\".\");"
                "from tools.postfinal_public_practice_v8 import main;"
                "main([\"freeze\"])'"
            ),
            "exception_class": "PublicExpansionError",
            "exception_module": "tools.postfinal_public_expansion_v8",
            "message": "corrupt public reference answer",
        },
    ]


def validate_v8_failure_document(document: Any) -> dict[str, Any]:
    """Authenticate the actual failed design without running or repairing it."""
    require(isinstance(document, dict), "preserved V8 failure is not an object")
    expected_top = {
        "schema": "rebar-postfinal-public-expansion-freeze-failure-v8",
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "recording_source_path": V8_RECORDER_RELATIVE,
        "recording_source_sha256": V8_FAILURE_PINNED_SHA256[V8_RECORDER_RELATIVE],
        "production_manifest_created": False,
        "production_cases_generated": 0,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "clock_samples": 0,
        "held_out_records_deserialized": 0,
        "performance": "NOT MEASURED",
    }
    for field, expected in expected_top.items():
        observed = document.get(field)
        require(type(observed) is type(expected) and observed == expected,
                f"preserved V8 failure was changed or concealed: {field}")
    failure = document.get("failure")
    require(isinstance(failure, dict), "preserved V8 failure class is absent")
    expected_failure = {
        "phase": "pre-candidate public fixture authentication",
        "class": "PublicExpansionError",
        "module": "tools.postfinal_public_expansion_v8",
        "message": "corrupt public reference answer",
        "cause": (
            "The authentic V5 fixture producer hashes Unicode results as "
            "unescaped UTF-8, while the frozen V8 expander incorrectly "
            "hashes those same result values as ASCII-escaped JSON."
        ),
    }
    require(failure == expected_failure, "actual V8 failure or cause was replaced")
    frozen_design = document.get("frozen_design")
    expected_design = {
        "goal_path": "GOAL.md",
        "goal_sha256": PUBLIC_FILE_SHA256["GOAL.md"],
        "expander_path": V8_SOURCE_RELATIVE,
        "expander_sha256": V8_FAILURE_PINNED_SHA256[V8_SOURCE_RELATIVE],
        "runner_path": V8_RUNNER_RELATIVE,
        "runner_sha256": V8_FAILURE_PINNED_SHA256[V8_RUNNER_RELATIVE],
        "protocol_path": V8_PROTOCOL_RELATIVE,
        "protocol_sha256": V8_FAILURE_PINNED_SHA256[V8_PROTOCOL_RELATIVE],
        "fixture_path":
            "performance/v7/evidence/rust-calibration-fixture.jsonl.gz",
        "fixture_sha256": PUBLIC_FILE_SHA256[
            "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
        ],
    }
    require(frozen_design == expected_design,
            "the preserved V8 failed source or public fixture was replaced")
    require(document.get("reproduction") == _expected_failure_reproduction(),
            "the actual two failed V8 invocation modes were changed")
    diagnosis = document.get("public_fixture_diagnosis")
    expected_diagnosis = {
        "public_fixture_cases": FIXTURE_CASE_COUNT,
        "legacy_utf8_digest_matches": FIXTURE_CASE_COUNT,
        "frozen_v8_ascii_digest_matches": FIXTURE_CASE_COUNT - V8_AFFECTED_CASES,
        "failed_reference_answers": V8_AFFECTED_CASES,
        "affected_public_api_counts": V8_AFFECTED_APIS,
        "affected_public_input_counts": V8_AFFECTED_INPUTS,
        "first_failure": V8_FIRST_FAILURE,
        "opaque_history_fields_skipped": FIXTURE_CASE_COUNT,
        "opaque_history_values_deserialized": 0,
    }
    require(diagnosis == expected_diagnosis,
            "the genuine 10,312-case, 577-failure V8 diagnosis changed")
    proof = {
        "source_path": V8_SOURCE_RELATIVE,
        "source_sha256": V8_FAILURE_PINNED_SHA256[V8_SOURCE_RELATIVE],
        "runner_path": V8_RUNNER_RELATIVE,
        "runner_sha256": V8_FAILURE_PINNED_SHA256[V8_RUNNER_RELATIVE],
        "protocol_path": V8_PROTOCOL_RELATIVE,
        "protocol_sha256": V8_FAILURE_PINNED_SHA256[V8_PROTOCOL_RELATIVE],
        "recorder_path": V8_RECORDER_RELATIVE,
        "recorder_sha256": V8_FAILURE_PINNED_SHA256[V8_RECORDER_RELATIVE],
        "report_path": V8_FAILURE_RELATIVE,
        "report_sha256": V8_FAILURE_PINNED_SHA256[V8_FAILURE_RELATIVE],
        "status": "FAIL",
        "failure_class": "PublicExpansionError",
        "public_fixture_cases": FIXTURE_CASE_COUNT,
        "failed_reference_answers": V8_AFFECTED_CASES,
        "first_failure_id": V8_FIRST_FAILURE["id"],
        "first_failure_legacy_utf8_sha256":
            V8_FIRST_FAILURE["legacy_utf8_sha256"],
        "first_failure_frozen_v8_ascii_sha256":
            V8_FIRST_FAILURE["frozen_v8_ascii_sha256"],
        "opaque_history_values_deserialized": 0,
    }
    require(set(proof) == V8_FAILURE_CONTRACT_KEYS,
            "preserved V8 failure proof changed its agreed 18-field contract")
    return proof


def _approved_repository_path(relative: str) -> Path:
    relative_path = Path(relative)
    require(not relative_path.is_absolute() and ".." not in relative_path.parts
            and str(relative_path) == relative,
            f"unapproved V10 provenance path: {relative}")
    path = ROOT / relative_path
    try:
        resolved = path.resolve(strict=True)
        inside = resolved.relative_to(ROOT.resolve())
    except (OSError, ValueError) as error:
        raise PublicExpansionError(
            f"missing or escaped V10 provenance path: {relative}"
        ) from error
    require(inside == relative_path and not path.is_symlink(),
            f"symbolic or substituted V10 provenance path: {relative}")
    return path


def verify_v8_failure_provenance() -> dict[str, Any]:
    before = candidate_imports()
    for relative, expected in sorted(V8_FAILURE_PINNED_SHA256.items()):
        path = _approved_repository_path(relative)
        actual = bounded_source_file_sha256(
            path, MAX_OWNED_ARTIFACT_BYTES, f"preserved V8 artifact {relative}"
        )
        require(actual == expected,
                f"the pushed genuine V8 failure artifact changed: {relative}")
    path = _approved_repository_path(V8_FAILURE_RELATIVE)
    try:
        document = json.loads(path.read_bytes())
    except (OSError, UnicodeError, ValueError) as error:
        raise PublicExpansionError(
            "cannot decode the pushed genuine V8 failure report"
        ) from error
    proof = validate_v8_failure_document(document)
    require(candidate_imports() == before,
            "a candidate entered V8 failure provenance authentication")
    return proof


class PublicHistorySpy:
    """Count archive-history keys and reject any deserialization of a value."""

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
                raise PublicExpansionError(
                    "opaque public archive history reached deserialization"
                )
        value, end = self.parser.raw_decode(text, index)
        if self.pending_history:
            if not isinstance(value, str) or value not in {
                "schema", "cohort", "position", "case", "expected"
            }:
                self.history_value_decodes += 1
                raise PublicExpansionError(
                    "an opaque public archive-history value was decoded"
                )
            self.pending_history = False
        if isinstance(value, str) and value == "historical":
            self.history_fields += 1
            self.pending_history = True
        return value, end


def public_subject_length(case: Any) -> int:
    require(isinstance(case, dict), "public workload case is not an object")
    subject = unpack(case.get("string"))
    require(subject is None or isinstance(
        subject, (str, bytes, bytearray, memoryview)
    ), "public workload has an unsupported subject")
    return 0 if subject is None else len(subject)


def bounded_public_case(case: Any, expected: Any) -> bool:
    """Apply safety limits to workload eligibility, not archive authentication."""
    require(isinstance(case, dict) and isinstance(expected, dict)
            and "result" in expected,
            "bounded public workload lacks its exact reference result")
    return (public_subject_length(case) <= SUBJECT_LIMIT
            and result_cardinality(expected["result"]) <= RESULT_LIMIT)


def require_bounded_public_case(
    case: Any, expected: Any, label: str,
) -> None:
    require(bounded_public_case(case, expected),
            f"{label} exceeds the frozen subject or result safety bound")


def load_public_fixture(
    fixture_manifest: dict[str, Any],
    *, diagnosis: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Read public fields only and authenticate all genuine legacy results."""
    rows: dict[str, dict[str, Any]] = {}
    positions: set[int] = set()
    uncompressed = hashlib.sha256()
    spy = PublicHistorySpy()
    matched_ascii = 0
    mismatched = 0
    eligible = 0
    bounded_apis: collections.Counter[str] = collections.Counter()
    affected_apis: collections.Counter[str] = collections.Counter()
    affected_inputs: collections.Counter[str] = collections.Counter()
    first_failure: dict[str, Any] | None = None
    relative = "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
    fixture_path = _approved_repository_path(relative)
    with gzip.open(fixture_path, "rb") as stream:
        for raw in stream:
            uncompressed.update(raw)
            record = decode_public_fixture_line(raw, spy)
            require(record.get("schema") == FIXTURE_SCHEMA,
                    "changed public fixture record schema")
            require(record.get("cohort") == "calibration",
                    "non-public record entered the public calibration fixture")
            position = record["position"]
            require(isinstance(position, int) and not isinstance(position, bool)
                    and position >= 0 and position not in positions,
                    "invalid or duplicate public fixture position")
            positions.add(position)
            case, expected = record["case"], record["expected"]
            require(isinstance(case, dict) and isinstance(expected, dict),
                    "invalid public fixture case or reference answer")
            require(case.get("cohort") == expected.get("cohort") == "calibration",
                    "non-public case or answer entered calibration")
            identifier = case.get("id")
            require(isinstance(identifier, str) and bool(identifier)
                    and identifier not in rows and expected.get("id") == identifier,
                    "missing, duplicate or mismatched public case identifier")
            require(case.get("category") == expected.get("category"),
                    "public case and reference categories disagree")
            require(case.get("api") in PUBLIC_OPERATIONS,
                    "unknown public regex operation")
            require(case.get("weight") == 1, "public case weighting changed")
            recorded = expected.get("result_sha256")
            authentic = legacy_result_digest(expected.get("result"))
            require(authentic == recorded,
                    "corrupt original UTF-8 public reference answer")
            incorrect_ascii = digest(expected.get("result"))
            if incorrect_ascii == recorded:
                matched_ascii += 1
            else:
                mismatched += 1
                affected_apis[case["api"]] += 1
                input_kind = source_kind(case)
                affected_inputs[input_kind] += 1
                if first_failure is None:
                    first_failure = {
                        "id": identifier,
                        "api": case["api"],
                        "category": case["category"],
                        "cohort": case["cohort"],
                        "recorded_sha256": recorded,
                        "legacy_utf8_sha256": authentic,
                        "frozen_v8_ascii_sha256": incorrect_ascii,
                    }
            require(source_kind(case) in {
                "text", "bytes", "bytearray", "memoryview"
            }, "unsupported exact public input type")
            # The archive genuinely contains 581 public but unsafe source
            # workloads. Authenticate and retain them without ever making one
            # eligible for an actual selected or generated benchmark case.
            if bounded_public_case(case, expected):
                eligible += 1
                bounded_apis[case["api"]] += 1
            rows[identifier] = {
                "position": position, "case": case, "expected": expected
            }
    require(len(rows) == FIXTURE_CASE_COUNT,
            "the genuine public fixture denominator changed")
    require(eligible == ELIGIBLE_PUBLIC_CASES,
            "the exact 9,731 eligible bounded public source cases changed")
    require(dict(sorted(bounded_apis.items()))
            == V7_BOUNDED_PUBLIC_API_CAPACITIES,
            "the original frozen bounded public operation capacities changed")
    require(uncompressed.hexdigest()
            == fixture_manifest.get("uncompressed_fixture_sha256"),
            "the genuine uncompressed public fixture changed")
    require(matched_ascii == FIXTURE_CASE_COUNT - V8_AFFECTED_CASES
            and mismatched == V8_AFFECTED_CASES,
            "the actual falsified V8 ASCII denominator changed")
    require(dict(sorted(affected_apis.items())) == V8_AFFECTED_APIS,
            "the genuine affected V8 operation counts changed")
    require(dict(sorted(affected_inputs.items())) == V8_AFFECTED_INPUTS,
            "the genuine affected V8 input type counts changed")
    require(first_failure == V8_FIRST_FAILURE,
            "the actual first public V8 Unicode failure changed")
    require(spy.history_fields == FIXTURE_CASE_COUNT
            and spy.history_value_decodes == 0,
            "public archived history was missing or deserialized")
    if diagnosis is not None:
        diagnosis.update({
            "public_fixture_cases": len(rows),
            "eligible_public_cases": eligible,
            "excluded_unbounded_public_cases": len(rows) - eligible,
            "bounded_eligible_public_source_cases": eligible,
            "bounded_ineligible_public_source_cases": len(rows) - eligible,
            "bounded_public_api_capacities": dict(sorted(bounded_apis.items())),
            "legacy_utf8_digest_matches": len(rows),
            "frozen_v8_ascii_digest_matches": matched_ascii,
            "failed_reference_answers": mismatched,
            "affected_public_api_counts": dict(sorted(affected_apis.items())),
            "affected_public_input_counts": dict(sorted(affected_inputs.items())),
            "first_failure": first_failure,
            "opaque_history_fields_skipped": spy.history_fields,
            "opaque_history_values_deserialized": spy.history_value_decodes,
        })
    return rows


def public_program_fingerprints() -> dict[str, str]:
    """Bind all three actual new files dynamically, without circular pins."""
    owned = {
        "runner": (GENERATOR_RELATIVE, MAX_PROGRAM_SOURCE_BYTES),
        "protocol": (PROTOCOL_RELATIVE, MAX_PROTOCOL_BYTES),
        "measurement_runner":
            (MEASUREMENT_RUNNER_RELATIVE, MAX_PROGRAM_SOURCE_BYTES),
    }
    result: dict[str, str] = {}
    generator = _approved_repository_path(GENERATOR_RELATIVE)
    require(Path(__file__).resolve() == generator.resolve(),
            "V10 generator was not loaded from its exact owned source")
    for name, (relative, limit) in owned.items():
        path = _approved_repository_path(relative)
        result[f"{name}_path"] = relative
        result[f"{name}_sha256"] = bounded_source_file_sha256(
            path, limit, f"actual V10 {name}"
        )
    require(set(result) == PROGRAM_KEYS,
            "actual V10 generator, protocol or runner provenance is incomplete")
    return result


def validate_stage10_correctness_contract(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict)
            and set(document) == STAGE10_CONTRACT_KEYS,
            "Stage10 correctness must retain exactly its agreed 13 fields")
    pins = validate_stage10_pinset(STAGE10_PINNED_SHA256)
    expected = {
        "source_path": STAGE10_SOURCE_RELATIVE,
        "source_sha256": pins[STAGE10_SOURCE_RELATIVE],
        "protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "protocol_sha256": pins[STAGE10_PROTOCOL_RELATIVE],
        "self_oracle_path": STAGE10_SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": pins[STAGE10_SELF_ORACLE_RELATIVE],
        "all_candidates_path": STAGE10_ALL_CANDIDATES_RELATIVE,
        "all_candidates_sha256": pins[STAGE10_ALL_CANDIDATES_RELATIVE],
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": STAGE10_COHORTS,
        "cases": STAGE10_CASES,
        "stdlib_checks": STAGE10_CASES * 2,
        "candidate_checks": STAGE10_CASES * len(REQUIRED_FAMILIES),
    }
    require(document == expected,
            "the passing source-bound Stage10 contract was changed")
    return dict(document)


def validate_public_v7_parent(parent: Any, previous: Any) -> dict[str, Any]:
    """Preserve the actual already-pushed V7 and its exact V6 case parent."""
    require(isinstance(parent, dict) and isinstance(previous, dict),
            "the exact public V6 and V7 parent plans are not objects")
    require(parent.get("postfinal_schema")
            == "rebar-postfinal-public-practice-plan-v6",
            "the original frozen public V6 parent was substituted")
    expected = {
        "postfinal_schema": "rebar-postfinal-public-practice-plan-v7",
        "protocol_version": "postfinal-public-practice-v7",
        "runner_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_public_practice_v7.py"
        ],
        "source_public_v6_manifest_path":
            "performance/postfinal-public-v6/manifest.json",
        "source_public_v6_manifest_sha256": PUBLIC_FILE_SHA256[
            "performance/postfinal-public-v6/manifest.json"
        ],
        "source_public_v6_runner_path":
            "tools/postfinal_public_practice_v6.py",
        "source_public_v6_runner_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_public_practice_v6.py"
        ],
        "cases": ORIGINAL_CASE_COUNT,
        "source_public_cases": FIXTURE_CASE_COUNT,
        "eligible_practice_cases": ELIGIBLE_PUBLIC_CASES,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "cohort": "calibration",
        "selection_seed": 2_026_072_404,
        "order_seed": 2_026_072_405,
        "bootstrap_seed": 2_026_072_406,
        "frozen_warmups": WARMUPS,
        "frozen_trials": PAIRED_TRIALS,
        "frozen_bootstrap_samples": BOOTSTRAP_DRAWS,
        "maximum_subject_limit": SUBJECT_LIMIT,
        "maximum_result_limit": RESULT_LIMIT,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "historical_performance_read": False,
        "timing_performed": False,
    }
    for field, expected_value in expected.items():
        observed = previous.get(field)
        require(type(observed) is type(expected_value)
                and observed == expected_value,
                f"the pushed public V7 parent changed: {field}")
    for field in ("cases", "all_bounded_workload_categories", "cohort",
                  "public_operations", "categories", "selected_cases"):
        require(field in parent and field in previous
                and previous[field] == parent[field],
                f"the pushed public V7 changed a frozen V6 obligation: {field}")
    descriptors = previous["selected_cases"]
    require(isinstance(descriptors, list)
            and len(descriptors) == ORIGINAL_CASE_COUNT,
            "the pushed public V7 omitted an original V6 case descriptor")
    identifiers: set[str] = set()
    operations: collections.Counter[str] = collections.Counter()
    categories: collections.Counter[str] = collections.Counter()
    for descriptor in descriptors:
        require(isinstance(descriptor, dict),
                "the pushed public V7 contains an invalid case descriptor")
        identifier = descriptor.get("case")
        require(isinstance(identifier, str) and bool(identifier)
                and identifier not in identifiers
                and descriptor.get("cohort") == "calibration"
                and descriptor.get("api") in PUBLIC_OPERATIONS,
                "the pushed public V7 duplicated or changed a public case")
        identifiers.add(identifier)
        operations[descriptor["api"]] += 1
        categories[descriptor["category"]] += 1
    require(dict(operations) == parent["public_operations"]
            and dict(categories) == parent["categories"],
            "the pushed V7 silently reweighted V6 operations or categories")
    return {
        "path": V7_PUBLIC_MANIFEST_RELATIVE,
        "sha256": V7_PUBLIC_MANIFEST_SHA256,
        "cases": ORIGINAL_CASE_COUNT,
        "source_v6_manifest_path":
            "performance/postfinal-public-v6/manifest.json",
        "source_v6_manifest_sha256": PUBLIC_FILE_SHA256[
            "performance/postfinal-public-v6/manifest.json"
        ],
        "selected_cases_preserved": ORIGINAL_CASE_COUNT,
        "historical_performance_read": False,
        "timing_performed": False,
    }


def verify_public_provenance(
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Gate actual V8 failure and full genuine Stage10 before fixture use."""
    before = candidate_imports()
    failed_design = verify_v8_failure_provenance()
    parent, fixture, provenance = frozen_v8.verify_public_provenance()
    previous_path = _approved_repository_path(V7_PUBLIC_MANIFEST_RELATIVE)
    require(bounded_source_file_sha256(
        previous_path, MAX_OWNED_ARTIFACT_BYTES,
        "pushed original public V7 comparison manifest",
    ) == V7_PUBLIC_MANIFEST_SHA256,
            "the exact already-pushed public V7 manifest was replaced")
    try:
        previous_parent = json.loads(previous_path.read_bytes())
    except (OSError, UnicodeError, ValueError) as error:
        raise PublicExpansionError(
            "cannot decode the exact pushed public V7 manifest"
        ) from error
    provenance = dict(provenance)
    provenance["stage10"] = validate_stage10_correctness_contract(
        provenance.get("stage10")
    )
    provenance["v8_failure"] = failed_design
    provenance["v7_public_parent"] = validate_public_v7_parent(
        parent, previous_parent
    )
    require(candidate_imports() == before,
            "a candidate entered public V10 provenance verification")
    return parent, fixture, provenance


def make_variant(template: dict[str, Any], serial: int) -> dict[str, Any]:
    require(isinstance(serial, int) and not isinstance(serial, bool)
            and serial >= 0, "invalid V10 public variant number")
    case = template["case"]
    if "expected" in template:
        require_bounded_public_case(
            case, template["expected"], "generated public source template"
        )
    label = f"{case['category']}:{case['id']}:{serial}"
    token = seed_key(label)[0].hex()[:20]
    suffix = f"-r10-{token}" if case["api"] == "escape" else f"(?#r10-{token})"
    variant = dict(case)
    variant["id"] = f"cal.public.v10.{token}"
    variant["pattern"] = append_public_pattern(case["pattern"], suffix)
    require(variant.get("cohort") == "calibration"
            and variant.get("category") == case.get("category")
            and variant.get("api") == case.get("api")
            and variant.get("lifecycle") == case.get("lifecycle")
            and variant.get("flags") == case.get("flags")
            and variant.get("string") == case.get("string"),
            "V10 variant changed its source category, operation or typed input")
    require({key: value for key, value in variant.items()
             if key not in {"id", "pattern"}}
            == {key: value for key, value in case.items()
                if key not in {"id", "pattern"}},
            "V10 variant changed frozen public operation arguments")
    return variant


def select_public_cases(
    parent: dict[str, Any], fixture: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    original = parent.get("selected_cases")
    require(isinstance(original, list) and len(original) == ORIGINAL_CASE_COUNT,
            "the exact original 8,192 public cases are missing")
    originals: list[dict[str, Any]] = []
    identities: set[str] = set()
    identifiers: set[str] = set()
    by_category: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    eligible = 0
    for record in fixture.values():
        case, expected = record["case"], record["expected"]
        if bounded_public_case(case, expected):
            by_category[case["category"]].append(record)
            eligible += 1
    declared_eligible = parent.get("eligible_practice_cases")
    if declared_eligible is not None:
        require(type(declared_eligible) is int
                and declared_eligible == ELIGIBLE_PUBLIC_CASES
                and eligible == declared_eligible,
                "the original 9,731 bounded public source capacity changed")
    require(len(by_category) == CATEGORY_COUNT,
            "the exact original public category universe changed")
    counts: collections.Counter[str] = collections.Counter()
    for descriptor in original:
        require(isinstance(descriptor, dict), "invalid original case descriptor")
        identifier = descriptor.get("case")
        require(isinstance(identifier, str) and identifier in fixture,
                "original case is absent from its pinned public fixture")
        record = fixture[identifier]
        case = record["case"]
        expected = record["expected"]
        require_bounded_public_case(case, expected,
                                   "preserved original selected public case")
        require(descriptor.get("cohort") == case.get("cohort") == "calibration"
                and descriptor.get("category") == case.get("category")
                and descriptor.get("api") == case.get("api")
                and descriptor.get("lifecycle") == case.get("lifecycle")
                and descriptor.get("input") == source_kind(case),
                "an original case descriptor or exact input type changed")
        require(legacy_result_digest(expected.get("result"))
                == expected.get("result_sha256"),
                "original public case lost its authentic UTF-8 answer")
        require(descriptor.get("expected_result_sha256")
                == expected.get("result_sha256"),
                "an exact original public reference answer changed")
        require(descriptor.get("subject_length") == public_subject_length(case)
                and descriptor.get("result_count")
                == result_cardinality(expected["result"]),
                "an original selected workload concealed its actual safe bounds")
        identity = semantic_identity(case)
        require(identity not in identities and identifier not in identifiers,
                "an original public case or semantic identity was repeated")
        identities.add(identity)
        identifiers.add(identifier)
        counts[case["category"]] += 1
        originals.append({
            "case": case, "expected": expected, "descriptor": descriptor,
            "source_id": identifier, "generated": False,
        })
    require(set(counts) == set(by_category)
            and all(count <= CASES_PER_CATEGORY for count in counts.values()),
            "original public categories exceed their balanced V10 allocation")
    generated: list[dict[str, Any]] = []
    for category in sorted(by_category):
        templates = sorted(
            by_category[category],
            key=lambda item: seed_key(f"template:{category}:{item['case']['id']}"),
        )
        require(bool(templates), "public category has no actual public template")
        serial = 0
        while counts[category] < CASES_PER_CATEGORY:
            template = templates[serial % len(templates)]
            require_bounded_public_case(
                template["case"], template["expected"],
                "generated public source template",
            )
            variant = make_variant(template, serial)
            require(public_subject_length(variant) <= SUBJECT_LIMIT,
                    "a generated public workload exceeded its subject bound")
            identity = semantic_identity(variant)
            require(identity not in identities
                    and variant["id"] not in identifiers,
                    "generated V10 public case or semantic identity collided")
            identities.add(identity)
            identifiers.add(variant["id"])
            counts[category] += 1
            generated.append({
                "case": variant, "expected": None, "descriptor": None,
                "source_id": template["case"]["id"], "generated": True,
            })
            serial += 1
    require(len(originals) == ORIGINAL_CASE_COUNT
            and len(originals) + len(generated) == CASE_COUNT
            and len(identities) == CASE_COUNT
            and len(identifiers) == CASE_COUNT
            and len(counts) == CATEGORY_COUNT
            and all(count == CASES_PER_CATEGORY for count in counts.values()),
            "V10 expansion is not exactly 260 unique categories by 128")
    return originals + generated


def run_oracle_worker(role: str) -> None:
    require(role in {"first", "second"}, "unknown independent V10 oracle role")
    require(sys.flags.isolated == 1
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and Path(sys.executable).resolve() == PINNED_PYTHON.resolve(),
            "the V10 reference worker is not the pinned isolated CPython")
    require(candidate_imports() == [],
            "a candidate entered the independent V10 reference worker")
    try:
        request = json.loads(sys.stdin.buffer.read())
    except (UnicodeError, ValueError) as error:
        raise PublicExpansionError("invalid V10 reference worker request") from error
    require(isinstance(request, dict)
            and request.get("domain") == SEED_DOMAIN,
            "the V10 reference worker received another experiment domain")
    cases = request.get("cases")
    require(isinstance(cases, list) and len(cases) == CASE_COUNT,
            "the V10 reference worker case denominator changed")
    answers: list[dict[str, Any]] = []
    for case in cases:
        require(isinstance(case, dict)
                and case.get("cohort") == "calibration",
                "a non-public case entered the isolated V10 reference")
        require(public_subject_length(case) <= SUBJECT_LIMIT,
                "an oversized selected workload entered the V10 reference")
        result = oracle_result(case)
        require(result_cardinality(result) <= RESULT_LIMIT,
                "the isolated V10 reference exceeded its result limit")
        answers.append({
            "id": case["id"], "result": result,
            "result_sha256": legacy_result_digest(result),
        })
    require(candidate_imports() == [],
            "a candidate entered an isolated V10 CPython reference")
    response = {
        "schema": ORACLE_SCHEMA, "role": role, "python": "3.14.6",
        "domain": SEED_DOMAIN, "cases": len(answers), "answers": answers,
        "candidate_imports": [], "timing": "NOT MEASURED",
    }
    sys.stdout.buffer.write(json_bytes(response) + b"\n")


def require_independent_cpython_answers(
    rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    require(len(rows) == CASE_COUNT,
            "the independent V10 reference population changed")
    for row in rows:
        require(public_subject_length(row["case"]) <= SUBJECT_LIMIT,
                "an oversized workload entered the independent V10 reference")
        if not row["generated"]:
            require_bounded_public_case(
                row["case"], row["expected"],
                "preserved public reference workload",
            )
    request = json_bytes({
        "domain": SEED_DOMAIN, "cases": [row["case"] for row in rows]
    })
    verified: list[list[dict[str, Any]]] = []
    for role in ("first", "second"):
        command = [
            str(PINNED_PYTHON), "-I", "-B", str(ROOT / GENERATOR_RELATIVE),
            "--oracle-worker", "--role", role,
        ]
        try:
            completed = subprocess.run(
                command, input=request, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=False,
            )
        except OSError as error:
            raise PublicExpansionError(
                "cannot start an independently isolated V10 CPython reference"
            ) from error
        require(completed.returncode == 0,
                f"independent isolated V10 reference {role} failed")
        try:
            response = json.loads(completed.stdout)
        except (UnicodeError, ValueError) as error:
            raise PublicExpansionError(
                f"invalid independent V10 reference {role} answer"
            ) from error
        require(isinstance(response, dict)
                and response.get("schema") == ORACLE_SCHEMA
                and response.get("role") == role
                and response.get("python") == "3.14.6"
                and response.get("domain") == SEED_DOMAIN
                and response.get("cases") == CASE_COUNT
                and response.get("candidate_imports") == []
                and response.get("timing") == "NOT MEASURED",
                "an independent V10 reference is stale or contaminated")
        answers = response.get("answers")
        require(isinstance(answers, list) and len(answers) == CASE_COUNT,
                "an independent V10 reference answer denominator changed")
        verified.append(answers)
    require(verified[0] == verified[1],
            "the two independent V10 CPython references disagree")
    for row, answer in zip(rows, verified[0], strict=True):
        require(isinstance(answer, dict)
                and answer.get("id") == row["case"]["id"],
                "an independent V10 reference reordered its cases")
        require(legacy_result_digest(answer.get("result"))
                == answer.get("result_sha256"),
                "an independent V10 reference used the wrong result digest")
        if not row["generated"]:
            require(answer["result"] == row["expected"]["result"]
                    and answer["result_sha256"]
                    == row["expected"]["result_sha256"],
                    "CPython disagrees with a preserved original UTF-8 answer")
    return verified[0]


def _validate_program(document: Any) -> dict[str, str]:
    require(isinstance(document, dict) and set(document) == PROGRAM_KEYS,
            "V10 must dynamically bind its actual generator, protocol and runner")
    exact_paths = {
        "runner_path": GENERATOR_RELATIVE,
        "protocol_path": PROTOCOL_RELATIVE,
        "measurement_runner_path": MEASUREMENT_RUNNER_RELATIVE,
    }
    for key, expected in exact_paths.items():
        require(document.get(key) == expected,
                f"V10 program substituted an owned source: {key}")
    hexadecimal = frozenset("0123456789abcdef")
    for key in ("runner_sha256", "protocol_sha256",
                "measurement_runner_sha256"):
        value = document.get(key)
        require(isinstance(value, str) and len(value) == 64
                and set(value) <= hexadecimal,
                f"V10 program source has no actual SHA-256: {key}")
    return dict(document)


def build_manifest(
    parent: dict[str, Any], rows: list[dict[str, Any]],
    answers: list[dict[str, Any]], provenance: dict[str, Any],
    program: dict[str, str],
) -> dict[str, Any]:
    require(len(rows) == len(answers) == CASE_COUNT,
            "the V10 manifest does not cover all 33,280 public cases")
    program = _validate_program(program)
    require(isinstance(provenance, dict), "V10 provenance is not an object")
    stage10 = validate_stage10_correctness_contract(provenance.get("stage10"))
    failed_design = provenance.get("v8_failure")
    require(isinstance(failed_design, dict)
            and set(failed_design) == V8_FAILURE_CONTRACT_KEYS,
            "V10 omitted the exact agreed 18-field genuine V8 failure proof")
    expected_failure = {
        "source_path": V8_SOURCE_RELATIVE,
        "source_sha256": V8_FAILURE_PINNED_SHA256[V8_SOURCE_RELATIVE],
        "runner_path": V8_RUNNER_RELATIVE,
        "runner_sha256": V8_FAILURE_PINNED_SHA256[V8_RUNNER_RELATIVE],
        "protocol_path": V8_PROTOCOL_RELATIVE,
        "protocol_sha256": V8_FAILURE_PINNED_SHA256[V8_PROTOCOL_RELATIVE],
        "recorder_path": V8_RECORDER_RELATIVE,
        "recorder_sha256": V8_FAILURE_PINNED_SHA256[V8_RECORDER_RELATIVE],
        "report_path": V8_FAILURE_RELATIVE,
        "report_sha256": V8_FAILURE_PINNED_SHA256[V8_FAILURE_RELATIVE],
        "status": "FAIL",
        "failure_class": "PublicExpansionError",
        "public_fixture_cases": FIXTURE_CASE_COUNT,
        "failed_reference_answers": V8_AFFECTED_CASES,
        "first_failure_id": V8_FIRST_FAILURE["id"],
        "first_failure_legacy_utf8_sha256":
            V8_FIRST_FAILURE["legacy_utf8_sha256"],
        "first_failure_frozen_v8_ascii_sha256":
            V8_FIRST_FAILURE["frozen_v8_ascii_sha256"],
        "opaque_history_values_deserialized": 0,
    }
    require(failed_design == expected_failure,
            "V10 changed, omitted or sanitized the actual failed V8 design")
    descriptors = list(parent["selected_cases"])
    records: list[dict[str, Any]] = []
    identities: list[str] = []
    observed: set[str] = set()
    operations: collections.Counter[str] = collections.Counter()
    categories: collections.Counter[str] = collections.Counter()
    for row, answer in zip(rows, answers, strict=True):
        case = row["case"]
        require(isinstance(answer, dict)
                and answer.get("id") == case.get("id"),
                "V10 manifest answer changed its public case identity")
        require_bounded_public_case(case, answer,
                                   "selected V10 public manifest workload")
        require(legacy_result_digest(answer.get("result"))
                == answer.get("result_sha256"),
                "V10 manifest answer is not authenticated as original UTF-8")
        identity = semantic_identity(case)
        require(identity not in observed,
                "the V10 manifest repeats a structural semantic identity")
        observed.add(identity)
        identities.append(identity)
        operations[case["api"]] += 1
        categories[case["category"]] += 1
        expected = {
            "cohort": "calibration", "id": case["id"],
            "category": case["category"], "result": answer["result"],
            "result_sha256": answer["result_sha256"],
        }
        if row["generated"]:
            descriptors.append({
                "case": case["id"], "cohort": "calibration",
                "category": case["category"], "api": case["api"],
                "lifecycle": case["lifecycle"], "input": source_kind(case),
                "source_case": row["source_id"],
                "expected_result_sha256": answer["result_sha256"],
                "frozen_operations": case["ops"],
                "subject_length": len(unpack(case["string"]))
                    if case["string"] is not None else 0,
                "result_count": result_cardinality(answer["result"]),
                "result_density": result_density(answer["result"]),
                "selection_reasons": ["public-development-v10-balanced-category"],
            })
        else:
            require(row.get("expected") == expected,
                    "V10 changed an original public result or result digest")
        records.append({
            "case": case, "expected": expected,
            "source_case": row["source_id"],
            "semantic_identity": identity, "generated": row["generated"],
        })
    require(descriptors[:ORIGINAL_CASE_COUNT] == parent["selected_cases"],
            "V10 changed or reordered an original public case descriptor")
    require(len(descriptors) == len(records) == len(observed) == CASE_COUNT,
            "V10 does not publish all distinct public examples")
    require(set(operations) == set(PUBLIC_OPERATIONS)
            and sum(operations.values()) == CASE_COUNT,
            "V10 lost a public operation or changed an operation denominator")
    require(len(categories) == CATEGORY_COUNT
            and all(value == CASES_PER_CATEGORY
                    for value in categories.values()),
            "V10 did not balance all 260 public categories equally")
    return {
        "schema": SCHEMA, "python": "3.14.6", "cohort": "calibration",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "seed_domain": SEED_DOMAIN, "selection_seed": SELECTION_SEED,
        "order_seed_domain": ORDER_SEED_DOMAIN, "order_seed": ORDER_SEED,
        "bootstrap_seed_domain": BOOTSTRAP_SEED_DOMAIN,
        "bootstrap_seed": BOOTSTRAP_SEED,
        **program,
        "cases": CASE_COUNT, "original_cases_preserved": ORIGINAL_CASE_COUNT,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "cases_per_category": CASES_PER_CATEGORY,
        "public_operations": dict(sorted(operations.items())),
        "categories": dict(sorted(categories.items())),
        "semantic_identity_count": len(identities),
        "semantic_identity_sha256": digest(identities),
        "frozen_warmups": WARMUPS, "frozen_trials": PAIRED_TRIALS,
        "frozen_bootstrap_samples": BOOTSTRAP_DRAWS,
        "expected_raw_rows": CASE_COUNT * (len(CANDIDATES) + 1) * PAIRED_TRIALS,
        "expected_correctness_answers":
            CASE_COUNT * (len(CANDIDATES) + 1) * PAIRED_TRIALS * 3,
        "expected_confidence_intervals":
            (CASE_COUNT + 1) * len(CANDIDATES),
        "expected_process_native_checks": CASE_COUNT * 8 + 8,
        "baseline": BASELINE, "candidates": list(CANDIDATES),
        "maximum_subject_limit": SUBJECT_LIMIT,
        "maximum_result_limit": RESULT_LIMIT,
        "source_public_cases": FIXTURE_CASE_COUNT,
        "eligible_practice_cases": ELIGIBLE_PUBLIC_CASES,
        "excluded_unbounded_public_cases":
            FIXTURE_CASE_COUNT - ELIGIBLE_PUBLIC_CASES,
        "bounded_eligible_public_source_cases": ELIGIBLE_PUBLIC_CASES,
        "bounded_ineligible_public_source_cases":
            FIXTURE_CASE_COUNT - ELIGIBLE_PUBLIC_CASES,
        "bounded_public_api_capacities":
            dict(sorted(V7_BOUNDED_PUBLIC_API_CAPACITIES.items())),
        "goal_sha256": PUBLIC_FILE_SHA256["GOAL.md"],
        "source_public_manifest":
            "performance/postfinal-public-v6/manifest.json",
        "source_public_manifest_sha256": PUBLIC_FILE_SHA256[
            "performance/postfinal-public-v6/manifest.json"
        ],
        "source_public_v6_manifest_path":
            "performance/postfinal-public-v6/manifest.json",
        "source_public_v6_manifest_sha256": PUBLIC_FILE_SHA256[
            "performance/postfinal-public-v6/manifest.json"
        ],
        "source_public_v7_manifest_path": V7_PUBLIC_MANIFEST_RELATIVE,
        "source_public_v7_manifest_sha256": V7_PUBLIC_MANIFEST_SHA256,
        "source_public_fixture":
            "performance/v7/evidence/rust-calibration-fixture.jsonl.gz",
        "source_public_fixture_sha256": PUBLIC_FILE_SHA256[
            "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
        ],
        "pinned_public_input_sha256": dict(sorted(PUBLIC_FILE_SHA256.items())),
        "qualified_source_fingerprints": provenance["sources"],
        "native_elf_fingerprints": provenance["native"],
        "stage10_correctness": stage10,
        "v8_failure": dict(failed_design),
        "independent_cpython_self_oracle": {
            "workers": 2, "schema": ORACLE_SCHEMA,
            "python": "3.14.6", "failed": 0,
        },
        "selected_cases": descriptors, "case_records": records,
        "candidate_imports": [], "historical_results_read": 0,
        "opaque_history_fields_skipped": FIXTURE_CASE_COUNT,
        "opaque_history_values_deserialized": 0,
        "public_fixture_original_answers_validated": FIXTURE_CASE_COUNT,
        "standalone_startup_cost": "NOT MEASURED",
        "standalone_ffi_cost": "NOT MEASURED",
        "inside_native_allocation": "NOT MEASURED",
        "timing_performed": False, "performance": "NOT MEASURED",
    }


def exclusive_manifest_write(
    manifest: dict[str, Any], program: dict[str, str],
    provenance: dict[str, Any],
) -> Path:
    require(public_program_fingerprints() == _validate_program(program),
            "an actual V10 generator, protocol or runner changed before output")
    verify_live_owned_artifacts(provenance)
    require(all(manifest.get(key) == value for key, value in program.items()),
            "the V10 manifest does not bind all three actual owned files")
    path = ROOT / MANIFEST_RELATIVE
    require(path.parent.is_dir(), "the approved V10 protocol directory is missing")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o644)
    except FileExistsError as error:
        raise PublicExpansionError(
            "the V10 public manifest already exists; overwrite is forbidden"
        ) from error
    except OSError as error:
        raise PublicExpansionError(
            "cannot exclusively create the approved V10 public manifest"
        ) from error
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(json_bytes(manifest) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    directory_flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        directory_flags |= os.O_DIRECTORY
    directory = os.open(path.parent, directory_flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return path


def freeze_public_development() -> None:
    """Explicit prospective action; never invoked by a synthetic self-test."""
    require(sys.flags.isolated == 1
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and Path(sys.executable).resolve() == PINNED_PYTHON.resolve(),
            "V10 freeze requires the pinned isolated CPython 3.14.6")
    require(candidate_imports() == [],
            "a candidate contaminated the V10 freeze controller")
    program = public_program_fingerprints()
    parent, fixture_manifest, provenance = verify_public_provenance()
    fixture = load_public_fixture(fixture_manifest)
    rows = select_public_cases(parent, fixture)
    answers = require_independent_cpython_answers(rows)
    for row, answer in zip(rows, answers, strict=True):
        if not row["generated"]:
            continue
        source_result = fixture[row["source_id"]]["expected"]["result"]
        api = row["case"]["api"]
        if api not in {"compile", "escape"}:
            require(answer["result"] == source_result,
                    "a V10 regex comment changed actual matching semantics")
        elif api == "compile":
            result = answer["result"]
            require(isinstance(result, dict) and isinstance(source_result, dict)
                    and {key: value for key, value in result.items()
                         if key != "pattern"}
                    == {key: value for key, value in source_result.items()
                        if key != "pattern"},
                    "a V10 compilation variant changed flags or capture structure")
    require(public_program_fingerprints() == program,
            "an actual V10 source changed during the dual reference workers")
    verify_live_owned_artifacts(provenance)
    require(candidate_imports() == [],
            "a candidate entered the V10 reference-only freeze controller")
    manifest = build_manifest(parent, rows, answers, provenance, program)
    output = exclusive_manifest_write(manifest, program, provenance)
    print(json.dumps({
        "schema": SCHEMA, "status": "PASS", "cases": CASE_COUNT,
        "categories": CATEGORY_COUNT, "cases_per_category": CASES_PER_CATEGORY,
        "public_operations": manifest["public_operations"],
        "manifest": str(output.relative_to(ROOT)),
        "performance": "NOT MEASURED",
    }, sort_keys=True, ensure_ascii=True, allow_nan=False))


def verify_public_fixture_only() -> dict[str, Any]:
    """Explicit real-data probe: read only; no worker, candidate or timing."""
    require(sys.flags.isolated == 1
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and Path(sys.executable).resolve() == PINNED_PYTHON.resolve(),
            "live V10 fixture verification requires pinned isolated CPython")
    before = candidate_imports()
    require(before == [], "a candidate contaminated read-only fixture verification")
    blocked: collections.Counter[str] = collections.Counter()
    original_run = subprocess.run
    original_popen = subprocess.Popen
    original_os_open = os.open
    original_clocks = {name: getattr(time, name) for name in CLOCK_NAMES}

    def deny_process(*_args: Any, **_kwargs: Any) -> Any:
        blocked["process"] += 1
        raise PublicExpansionError(
            "read-only public fixture verification cannot start a worker"
        )

    def deny_output(*_args: Any, **_kwargs: Any) -> Any:
        blocked["output"] += 1
        raise PublicExpansionError(
            "read-only public fixture verification cannot create files"
        )

    def deny_clock(*_args: Any, **_kwargs: Any) -> Any:
        blocked["clock"] += 1
        raise PublicExpansionError(
            "read-only public fixture verification cannot sample a clock"
        )

    subprocess.run = deny_process  # type: ignore[assignment]
    subprocess.Popen = deny_process  # type: ignore[assignment]
    os.open = deny_output  # type: ignore[assignment]
    for name in CLOCK_NAMES:
        setattr(time, name, deny_clock)
    try:
        failure = verify_v8_failure_provenance()
        public_parents: dict[str, dict[str, Any]] = {}
        for relative in (
            "performance/postfinal-public-v6/manifest.json",
            V7_PUBLIC_MANIFEST_RELATIVE,
        ):
            path = _approved_repository_path(relative)
            require(bounded_source_file_sha256(
                path, MAX_OWNED_ARTIFACT_BYTES,
                f"pushed original public comparison {relative}",
            ) == PUBLIC_FILE_SHA256[relative],
                    f"a genuine frozen public comparison changed: {relative}")
            try:
                document = json.loads(path.read_bytes())
            except (OSError, UnicodeError, ValueError) as error:
                raise PublicExpansionError(
                    f"cannot decode a pushed public comparison: {relative}"
                ) from error
            require(isinstance(document, dict),
                    f"pushed public comparison is not an object: {relative}")
            public_parents[relative] = document
        for relative in (
            "tools/postfinal_public_practice_v6.py",
            "tools/postfinal_public_practice_v7.py",
            "performance/postfinal-public-v7/PROTOCOL.md",
        ):
            path = _approved_repository_path(relative)
            require(bounded_source_file_sha256(
                path, MAX_OWNED_ARTIFACT_BYTES,
                f"pushed original public comparison source {relative}",
            ) == PUBLIC_FILE_SHA256[relative],
                    f"a frozen public comparison source changed: {relative}")
        parent = public_parents[
            "performance/postfinal-public-v6/manifest.json"
        ]
        previous_parent = public_parents[V7_PUBLIC_MANIFEST_RELATIVE]
        public_parent = validate_public_v7_parent(parent, previous_parent)
        manifest_relative = (
            "performance/v7/evidence/rust-calibration-fixture-manifest.json"
        )
        manifest_path = _approved_repository_path(manifest_relative)
        manifest_hash = bounded_source_file_sha256(
            manifest_path, MAX_OWNED_ARTIFACT_BYTES, "pinned public fixture manifest"
        )
        require(manifest_hash == PUBLIC_FILE_SHA256[manifest_relative],
                "the genuine public fixture manifest changed")
        try:
            fixture_manifest = json.loads(manifest_path.read_bytes())
        except (OSError, UnicodeError, ValueError) as error:
            raise PublicExpansionError(
                "cannot decode the pinned public fixture manifest"
            ) from error
        require(isinstance(fixture_manifest, dict)
                and fixture_manifest.get("schema") == FIXTURE_MANIFEST_SCHEMA
                and fixture_manifest.get("python") == "3.14.6"
                and fixture_manifest.get("cohort") == "calibration"
                and fixture_manifest.get("cases") == FIXTURE_CASE_COUNT
                and fixture_manifest.get("failed") == 0,
                "the public-only reference fixture manifest changed")
        fixture_relative = (
            "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
        )
        require(fixture_manifest.get("fixture") == fixture_relative
                and fixture_manifest.get("fixture_sha256")
                == PUBLIC_FILE_SHA256[fixture_relative],
                "the live public fixture is not the approved original")
        fixture_path = _approved_repository_path(fixture_relative)
        require(bounded_source_file_sha256(
            fixture_path, MAX_OWNED_ARTIFACT_BYTES, "pinned public fixture"
        ) == PUBLIC_FILE_SHA256[fixture_relative],
                "the actual compressed public fixture changed")
        diagnosis: dict[str, Any] = {}
        rows = load_public_fixture(fixture_manifest, diagnosis=diagnosis)
        require(len(rows) == FIXTURE_CASE_COUNT
                and failure["failed_reference_answers"]
                == diagnosis["failed_reference_answers"]
                and failure["first_failure_id"]
                == diagnosis["first_failure"]["id"],
                "actual V8 failure does not match all genuine fixture records")
        require(candidate_imports() == before == [],
                "a candidate entered read-only public fixture verification")
        require(not blocked,
                "read-only public fixture verification attempted a denied effect")
        return {
            "schema": FIXTURE_VERIFICATION_SCHEMA,
            "status": "PASS", "result": "PASS", "python": "3.14.6",
            "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
            "v8_failure": failure,
            "v7_public_parent": public_parent,
            "source_public_v6_manifest_path":
                "performance/postfinal-public-v6/manifest.json",
            "source_public_v6_manifest_sha256": PUBLIC_FILE_SHA256[
                "performance/postfinal-public-v6/manifest.json"
            ],
            "source_public_v7_manifest_path": V7_PUBLIC_MANIFEST_RELATIVE,
            "source_public_v7_manifest_sha256": V7_PUBLIC_MANIFEST_SHA256,
            **diagnosis,
            "fixture_files_read": 1,
            "candidate_imports": [],
            "candidate_processes": 0,
            "oracle_processes_started": 0,
            "clock_samples": 0,
            "files_written": 0,
            "manifest_files_written": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
    finally:
        subprocess.run = original_run  # type: ignore[assignment]
        subprocess.Popen = original_popen  # type: ignore[assignment]
        os.open = original_os_open  # type: ignore[assignment]
        for name, clock in original_clocks.items():
            setattr(time, name, clock)


def synthetic_v8_failure_document() -> dict[str, Any]:
    """Build only an invented in-memory copy of the exact public contract."""
    return {
        "schema": "rebar-postfinal-public-expansion-freeze-failure-v8",
        "status": "FAIL", "result": "FAIL", "python": "3.14.6",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "frozen_design": {
            "goal_path": "GOAL.md",
            "goal_sha256": PUBLIC_FILE_SHA256["GOAL.md"],
            "expander_path": V8_SOURCE_RELATIVE,
            "expander_sha256": V8_FAILURE_PINNED_SHA256[V8_SOURCE_RELATIVE],
            "runner_path": V8_RUNNER_RELATIVE,
            "runner_sha256": V8_FAILURE_PINNED_SHA256[V8_RUNNER_RELATIVE],
            "protocol_path": V8_PROTOCOL_RELATIVE,
            "protocol_sha256": V8_FAILURE_PINNED_SHA256[V8_PROTOCOL_RELATIVE],
            "fixture_path":
                "performance/v7/evidence/rust-calibration-fixture.jsonl.gz",
            "fixture_sha256": PUBLIC_FILE_SHA256[
                "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
            ],
        },
        "failure": {
            "phase": "pre-candidate public fixture authentication",
            "class": "PublicExpansionError",
            "module": "tools.postfinal_public_expansion_v8",
            "message": "corrupt public reference answer",
            "cause": (
                "The authentic V5 fixture producer hashes Unicode results as "
                "unescaped UTF-8, while the frozen V8 expander incorrectly "
                "hashes those same result values as ASCII-escaped JSON."
            ),
        },
        "reproduction": _expected_failure_reproduction(),
        "public_fixture_diagnosis": {
            "public_fixture_cases": FIXTURE_CASE_COUNT,
            "legacy_utf8_digest_matches": FIXTURE_CASE_COUNT,
            "frozen_v8_ascii_digest_matches":
                FIXTURE_CASE_COUNT - V8_AFFECTED_CASES,
            "failed_reference_answers": V8_AFFECTED_CASES,
            "affected_public_api_counts": dict(V8_AFFECTED_APIS),
            "affected_public_input_counts": dict(V8_AFFECTED_INPUTS),
            "first_failure": dict(V8_FIRST_FAILURE),
            "opaque_history_fields_skipped": FIXTURE_CASE_COUNT,
            "opaque_history_values_deserialized": 0,
        },
        "recording_source_path": V8_RECORDER_RELATIVE,
        "recording_source_sha256":
            V8_FAILURE_PINNED_SHA256[V8_RECORDER_RELATIVE],
        "production_manifest_created": False,
        "production_cases_generated": 0,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "clock_samples": 0,
        "held_out_records_deserialized": 0,
        "performance": "NOT MEASURED",
    }


def self_test() -> dict[str, Any]:
    """Use synthetic values only; poison every filesystem, clock and worker."""
    checks: list[str] = []
    blocked: collections.Counter[str] = collections.Counter()
    before = candidate_imports()
    original_run = subprocess.run
    original_popen = subprocess.Popen
    original_gzip = gzip.open
    original_path_open = Path.open
    original_path_read = Path.read_bytes
    original_os_open = os.open
    original_clocks = {name: getattr(time, name) for name in CLOCK_NAMES}

    def deny(kind: str) -> Callable[..., Any]:
        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            blocked[kind] += 1
            raise PublicExpansionError(
                f"synthetic V10 self-test cannot access {kind}"
            )
        return forbidden

    subprocess.run = deny("subprocess")  # type: ignore[assignment]
    subprocess.Popen = deny("worker")  # type: ignore[assignment]
    gzip.open = deny("compressed-fixture")  # type: ignore[assignment]
    Path.open = deny("filesystem-path")  # type: ignore[assignment]
    Path.read_bytes = deny("filesystem-read")  # type: ignore[assignment]
    os.open = deny("filesystem-write")  # type: ignore[assignment]
    for name in CLOCK_NAMES:
        setattr(time, name, deny(f"clock-{name}"))

    def check(label: str, value: object) -> None:
        require(label not in checks, f"duplicate V10 synthetic control: {label}")
        require(value, f"V10 synthetic control failed: {label}")
        checks.append(label)

    def rejected(label: str, function: Callable[[], Any]) -> None:
        try:
            function()
        except (PublicExpansionError, TypeError, ValueError, UnicodeError):
            check(label, True)
        else:
            raise PublicExpansionError(f"V10 accepted synthetic poison: {label}")

    try:
        check("isolated-direct-repository-bootstrap-is-explicit",
              sys.path[0] == str(ROOT))
        check("pinned-isolated-python-is-3-14-6",
              sys.flags.isolated == 1
              and tuple(sys.version_info[:3]) == (3, 14, 6)
              and Path(sys.executable) == PINNED_PYTHON)
        check("v10-selection-domain-is-exact",
              SEED_DOMAIN == "rebar/public-development/v10")
        check("v10-selection-seed-is-exact", SELECTION_SEED == 2026072450)
        check("v10-order-seed-is-exact", ORDER_SEED == 2026072451)
        check("v10-bootstrap-seed-is-exact", BOOTSTRAP_SEED == 2026072452)
        check("v10-three-seeds-are-distinct",
              len({SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}) == 3)
        check("v10-order-domain-is-separated",
              ORDER_SEED_DOMAIN == "rebar/public-development/v10/paired-order")
        check("v10-bootstrap-domain-is-separated",
              BOOTSTRAP_SEED_DOMAIN == "rebar/public-development/v10/bootstrap")
        check("v10-three-domains-are-distinct",
              len({SEED_DOMAIN, ORDER_SEED_DOMAIN, BOOTSTRAP_SEED_DOMAIN}) == 3)
        check("v10-selection-is-deterministic",
              seed_key("synthetic") == seed_key("synthetic"))
        check("wrong-selection-seed-changes-public-selection",
              seed_key("synthetic")
              != seed_key("synthetic", seed=SELECTION_SEED + 1))
        check("wrong-selection-domain-changes-public-selection",
              seed_key("synthetic")
              != seed_key("synthetic", domain="rebar/public-development/v8"))
        nested_unicode = {
            "caf\u00e9": ["\u03c0", "\U0001f600", {"na\u00efve": "\u96ea"}]
        }
        true_encoded = json.dumps(
            nested_unicode, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        check("original-result-codec-is-exact-unescaped-utf8",
              legacy_result_digest(nested_unicode)
              == hashlib.sha256(true_encoded).hexdigest())
        check("nested-unicode-rejects-frozen-v8-ascii-result-codec",
              legacy_result_digest(nested_unicode) != digest(nested_unicode))
        check("structural-json-remains-canonical-ascii",
              json_bytes(nested_unicode).isascii()
              and b"\\u" in json_bytes(nested_unicode))
        check("structural-identity-still-uses-ascii-codec",
              digest(nested_unicode)
              == hashlib.sha256(json_bytes(nested_unicode)).hexdigest())
        check("ascii-result-codecs-agree-when-they-should",
              legacy_result_digest({"plain": ["ascii", 1]})
              == digest({"plain": ["ascii", 1]}))
        check("frozen-v8-result-codec-is-falsified-not-edited",
              frozen_v8.digest(nested_unicode) == digest(nested_unicode)
              and frozen_v8.digest(nested_unicode)
              != legacy_result_digest(nested_unicode))
        rejected("lone-surrogate-result-fails-closed",
                 lambda: legacy_result_digest({"bad": "\ud800"}))
        check("structural-lone-surrogate-remains-lossless",
              canonical("\ud800") != canonical("\ufffd"))
        check("bytes-and-text-never-share-structural-identity",
              canonical(b"abc") != canonical("abc"))
        check("bytes-and-bytearray-never-share-structural-identity",
              canonical(b"abc") != canonical(bytearray(b"abc")))
        check("bytearray-and-memoryview-never-share-structural-identity",
              canonical(bytearray(b"abc")) != canonical(memoryview(b"abc")))
        check("tuple-and-list-never-share-structural-identity",
              canonical((1, 2)) != canonical([1, 2]))
        check("bool-and-int-never-share-structural-identity",
              canonical(True) != canonical(1))
        check("mapping-identity-is-independent-of-key-insertion-order",
              canonical({"a": 1, "b": 2})
              == canonical({"b": 2, "a": 1}))
        rejected("invalid-packed-bytes-fail-closed",
                 lambda: canonical({PACKING_MARKER: "bytes", "hex": "bad!"}))
        rejected("unknown-packed-input-type-fails-closed",
                 lambda: canonical({PACKING_MARKER: "foreign", "hex": "61"}))
        rejected("packed-input-extra-fields-fail-closed",
                 lambda: canonical({
                     PACKING_MARKER: "bytes", "hex": "61", "other": 1
                 }))
        check("five-actual-v8-failure-artifacts-are-explicit",
              len(V8_FAILURE_PINNED_SHA256) == 5)
        check("exact-already-pushed-v7-public-manifest-is-pinned",
              PUBLIC_FILE_SHA256[V7_PUBLIC_MANIFEST_RELATIVE]
              == "465c751c6756cbea73bc3dc6d4397e2777d04a107b9a607241697b148c9c5f26")
        check("exact-already-pushed-v7-public-runner-is-pinned",
              PUBLIC_FILE_SHA256["tools/postfinal_public_practice_v7.py"]
              == "cc5b79daf3a0d018d15c76d01665cf94a30d3838c5a5c21389cba51444e96e7e")
        check("exact-already-pushed-v7-public-protocol-is-pinned",
              PUBLIC_FILE_SHA256["performance/postfinal-public-v7/PROTOCOL.md"]
              == "c8fed02bde3d2b096905a44db99405b47801743749053e8dc402cb70cc1f51c0")
        check("exact-frozen-bounded-public-eligible-count-is-9731",
              ELIGIBLE_PUBLIC_CASES == 9_731)
        check("exact-frozen-unbounded-public-source-count-is-581",
              FIXTURE_CASE_COUNT - ELIGIBLE_PUBLIC_CASES == 581)
        check("frozen-bounded-operation-capacities-sum-exactly-to-9731",
              set(V7_BOUNDED_PUBLIC_API_CAPACITIES) == set(PUBLIC_OPERATIONS)
              and sum(V7_BOUNDED_PUBLIC_API_CAPACITIES.values()) == 9_731)
        for relative, expected in sorted(V8_FAILURE_PINNED_SHA256.items()):
            check("pinned-v8-artifact-" + relative.replace("/", "-")
                  .replace(".", "-"),
                  PUBLIC_FILE_SHA256.get(relative) == expected
                  and isinstance(expected, str) and len(expected) == 64)
        check("immutable-goal-remains-explicitly-pinned",
              PUBLIC_FILE_SHA256["GOAL.md"]
              == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62")
        report = synthetic_v8_failure_document()
        failure_proof = validate_v8_failure_document(report)
        check("preserved-v8-failure-contract-has-exactly-18-fields",
              set(failure_proof) == V8_FAILURE_CONTRACT_KEYS
              and len(failure_proof) == 18)
        check("preserved-v8-failure-report-remains-fail",
              failure_proof["status"] == "FAIL")
        check("preserved-v8-failure-denominator-remains-10312",
              failure_proof["public_fixture_cases"] == 10_312)
        check("preserved-v8-real-failure-count-remains-577",
              failure_proof["failed_reference_answers"] == 577)
        check("preserved-v8-first-real-failure-remains-unicode",
              failure_proof["first_failure_id"] == "cal.unicode.words")
        check("preserved-v8-first-authentic-utf8-digest-remains-pinned",
              failure_proof["first_failure_legacy_utf8_sha256"]
              == "21f3db7cbb6c5d5bb6fcaf4dc6847779d647399a97f9e62a62861733a4fa1949")
        check("preserved-v8-first-incorrect-ascii-digest-remains-pinned",
              failure_proof["first_failure_frozen_v8_ascii_sha256"]
              == "af46c189444aa11a5f11a6894aaac409e79913384e82e6ea96e6668468f10885")
        check("preserved-v8-affected-operation-counts-remain-exact",
              V8_AFFECTED_APIS == {"escape": 48, "findall": 483, "split": 46}
              and sum(V8_AFFECTED_APIS.values()) == 577)
        check("preserved-v8-history-remains-opaque",
              failure_proof["opaque_history_values_deserialized"] == 0)

        def reject_failure(
            label: str, mutate: Callable[[dict[str, Any]], None]
        ) -> None:
            poisoned = json.loads(json_bytes(report))
            mutate(poisoned)
            rejected(label, lambda: validate_v8_failure_document(poisoned))

        reject_failure("v8-failure-falsely-reclassified-pass-is-rejected",
                       lambda value: value.update(status="PASS"))
        reject_failure("v8-failure-result-falsely-reclassified-pass-is-rejected",
                       lambda value: value.update(result="PASS"))
        reject_failure("v8-failure-timing-contamination-is-rejected",
                       lambda value: value.update(benchmark_or_timing_executed=True))
        reject_failure("v8-failure-candidate-contamination-is-rejected",
                       lambda value: value.update(candidate_processes=1))
        reject_failure("v8-failure-clock-contamination-is-rejected",
                       lambda value: value.update(clock_samples=1))
        reject_failure("v8-failure-concealed-mismatch-is-rejected",
                       lambda value: value["public_fixture_diagnosis"]
                       .update(failed_reference_answers=576))
        reject_failure("v8-failure-wrong-authentic-result-hash-is-rejected",
                       lambda value: value["public_fixture_diagnosis"]
                       ["first_failure"].update(legacy_utf8_sha256="0" * 64))
        reject_failure("v8-failure-wrong-ascii-result-hash-is-rejected",
                       lambda value: value["public_fixture_diagnosis"]
                       ["first_failure"].update(frozen_v8_ascii_sha256="0" * 64))
        reject_failure("v8-failure-decoded-archive-history-is-rejected",
                       lambda value: value["public_fixture_diagnosis"]
                       .update(opaque_history_values_deserialized=1))
        reject_failure("v8-failure-invented-runpy-command-is-rejected",
                       lambda value: value["reproduction"][1]
                       .update(command="python -c 'import runpy'"))
        reject_failure("v8-failure-substituted-recorder-is-rejected",
                       lambda value: value.update(recording_source_sha256="0" * 64))
        reject_failure("v8-failure-substituted-frozen-source-is-rejected",
                       lambda value: value["frozen_design"]
                       .update(expander_sha256="0" * 64))

        base_case = {
            "id": "cal.synthetic.v10.unicode", "cohort": "calibration",
            "category": "synthetic-unicode", "api": "findall",
            "lifecycle": "compiled", "pattern": "caf\u00e9",
            "string": "caf\u00e9 \u96ea", "flags": [], "ops": 1, "weight": 1,
        }
        base_result = ["caf\u00e9", "\u96ea"]
        base_expected = {
            "id": base_case["id"], "cohort": "calibration",
            "category": base_case["category"], "result": base_result,
            "result_sha256": legacy_result_digest(base_result),
        }
        opaque = {
            "case": base_case, "cohort": "calibration",
            "expected": base_expected,
            "historical": {"poison": [{"opaque": "must-never-be-read"}]},
            "position": 0, "schema": FIXTURE_SCHEMA,
        }
        spy = PublicHistorySpy()
        decoded = decode_public_fixture_line(json_bytes(opaque) + b"\n", spy)
        check("selective-decoder-preserves-only-approved-public-fields",
              set(decoded) == {
                  "schema", "cohort", "position", "case", "expected"
              })
        check("selective-decoder-never-returns-archive-history",
              "historical" not in decoded)
        check("selective-decoder-counts-opaque-archive-key",
              spy.history_fields == 1)
        check("selective-decoder-never-deserializes-archive-value",
              spy.history_value_decodes == 0)
        check("selective-decoder-preserves-actual-unicode-result",
              decoded["expected"]["result"] == base_result)
        check("selective-unicode-result-authenticates-with-original-utf8",
              legacy_result_digest(decoded["expected"]["result"])
              == decoded["expected"]["result_sha256"])
        check("selective-unicode-result-falsifies-frozen-v8-ascii",
              digest(decoded["expected"]["result"])
              != decoded["expected"]["result_sha256"])
        oversized_archive_case = {
            **base_case,
            "id": "cal.synthetic.v10.archived-oversized-subject",
            "string": "x" * (SUBJECT_LIMIT + 1),
        }
        oversized_archive_expected = {
            **base_expected,
            "id": oversized_archive_case["id"],
        }
        oversized_archive = {
            "case": oversized_archive_case, "cohort": "calibration",
            "expected": oversized_archive_expected,
            "historical": {"poison": ["never decode archived history"]},
            "position": 1, "schema": FIXTURE_SCHEMA,
        }
        oversized_spy = PublicHistorySpy()
        archived = decode_public_fixture_line(
            json_bytes(oversized_archive) + b"\n", oversized_spy
        )
        check("oversized-public-archive-record-is-decoded-and-authenticated",
              legacy_result_digest(archived["expected"]["result"])
              == archived["expected"]["result_sha256"])
        check("oversized-public-archive-record-is-never-eligible",
              not bounded_public_case(archived["case"], archived["expected"]))
        check("oversized-public-archive-history-is-never-deserialized",
              oversized_spy.history_fields == 1
              and oversized_spy.history_value_decodes == 0)
        rejected("oversized-public-subject-cannot-become-a-selected-workload",
                 lambda: require_bounded_public_case(
                     archived["case"], archived["expected"], "synthetic subject"
                 ))
        oversized_result = ["safe"] * (RESULT_LIMIT + 1)
        oversized_result_expected = {
            **base_expected,
            "result": oversized_result,
            "result_sha256": legacy_result_digest(oversized_result),
        }
        check("oversized-archived-reference-result-remains-authentic",
              legacy_result_digest(oversized_result_expected["result"])
              == oversized_result_expected["result_sha256"])
        check("oversized-archived-reference-result-is-not-eligible",
              not bounded_public_case(base_case, oversized_result_expected))
        rejected("oversized-reference-result-cannot-become-a-selected-workload",
                 lambda: require_bounded_public_case(
                     base_case, oversized_result_expected, "synthetic result"
                 ))
        rejected("unexpected-selective-fixture-field-is-rejected",
                 lambda: decode_public_fixture_line(
                     json_bytes(dict(opaque, foreign=True))
                 ))
        rejected("truncated-selective-fixture-row-is-rejected",
                 lambda: decode_public_fixture_line(b'{"case":'))
        variant = make_variant({"case": base_case}, 0)
        check("v10-variant-retains-exact-public-category",
              variant["category"] == base_case["category"])
        check("v10-variant-retains-exact-public-operation",
              variant["api"] == base_case["api"])
        check("v10-variant-retains-exact-typed-subject",
              variant["string"] == base_case["string"])
        check("v10-variant-retains-exact-flags-and-lifecycle",
              variant["flags"] == base_case["flags"]
              and variant["lifecycle"] == base_case["lifecycle"])
        check("v10-variant-uses-fresh-v10-public-identity",
              variant["id"].startswith("cal.public.v10."))
        check("v10-variant-uses-semantic-v10-regex-comment",
              "(?#r10-" in variant["pattern"])
        check("v10-variant-changes-structural-semantic-identity",
              semantic_identity(variant) != semantic_identity(base_case))
        check("v10-variant-generation-is-deterministic",
              make_variant({"case": base_case}, 0) == variant)
        check("distinct-v10-variant-does-not-collide",
              semantic_identity(make_variant({"case": base_case}, 1))
              != semantic_identity(variant))
        rejected("negative-v10-variant-is-rejected",
                 lambda: make_variant({"case": base_case}, -1))
        rejected("boolean-v10-variant-is-rejected",
                 lambda: make_variant({"case": base_case}, True))
        typed_binary = dict(
            base_case,
            pattern={PACKING_MARKER: "bytes", "hex": "6162"},
            string={PACKING_MARKER: "bytes", "hex": "616263"},
        )
        check("v10-bytearray-subject-type-is-preserved",
              source_kind(dict(typed_binary, subject_kind="bytearray"))
              == "bytearray")
        check("v10-memoryview-subject-type-is-preserved",
              source_kind(dict(typed_binary, subject_kind="memoryview"))
              == "memoryview")
        check("v10-bytearray-materializes-the-exact-buffer",
              isinstance(effective_subject(
                  dict(typed_binary, subject_kind="bytearray")
              ), bytearray))
        check("v10-memoryview-materializes-the-exact-buffer",
              isinstance(effective_subject(
                  dict(typed_binary, subject_kind="memoryview")
              ), memoryview))
        escape_case = dict(
            typed_binary, api="escape", string=None,
            id="cal.synthetic.v10.escape", lifecycle="module",
        )
        escape_variant = make_variant({"case": escape_case}, 0)
        check("v10-binary-escape-retains-real-bytes",
              isinstance(unpack(escape_variant["pattern"]), bytes))
        check("v10-escape-adds-literal-not-regex-comment",
              b"-r10-" in unpack(escape_variant["pattern"])
              and b"(?#" not in unpack(escape_variant["pattern"]))

        synthetic = frozen_v8.synthetic_qualification_inputs()
        audit, strict, locale, universal, pins, reference, all_candidates = synthetic
        provenance = validate_candidate_proofs(audit, strict, locale, universal)
        check("all-independent-from-scratch-v5-family-proofs-remain-required",
              set(provenance["sources"]) == REQUIRED_SOURCE_PATHS)
        check("all-five-actual-family-native-roles-remain-required",
              set(provenance["native"]) == REQUIRED_NATIVE_ROLES)
        check("all-four-passing-stage10-artifact-pins-remain-complete",
              validate_stage10_pinset(STAGE10_PINNED_SHA256)
              == STAGE10_PINNED_SHA256)
        check("synthetic-stage10-proof-requires-both-independent-references",
              validate_stage10_documents(
                  reference, all_candidates, pins, provenance
              )["stdlib_checks"] == 7_168)
        synthetic_stage10 = {
            "source_path": STAGE10_SOURCE_RELATIVE,
            "source_sha256": STAGE10_PINNED_SHA256[STAGE10_SOURCE_RELATIVE],
            "protocol_path": STAGE10_PROTOCOL_RELATIVE,
            "protocol_sha256": STAGE10_PINNED_SHA256[STAGE10_PROTOCOL_RELATIVE],
            "self_oracle_path": STAGE10_SELF_ORACLE_RELATIVE,
            "self_oracle_sha256":
                STAGE10_PINNED_SHA256[STAGE10_SELF_ORACLE_RELATIVE],
            "all_candidates_path": STAGE10_ALL_CANDIDATES_RELATIVE,
            "all_candidates_sha256":
                STAGE10_PINNED_SHA256[STAGE10_ALL_CANDIDATES_RELATIVE],
            "matrix_sha256": STAGE10_MATRIX_SHA256,
            "cohorts": STAGE10_COHORTS, "cases": STAGE10_CASES,
            "stdlib_checks": STAGE10_CASES * 2,
            "candidate_checks": STAGE10_CASES * len(REQUIRED_FAMILIES),
        }
        check("stage10-manifest-contract-has-exactly-thirteen-fields",
              len(synthetic_stage10) == 13
              and validate_stage10_correctness_contract(synthetic_stage10)
              == synthetic_stage10)
        for field in sorted(STAGE10_CONTRACT_KEYS):
            omitted = dict(synthetic_stage10)
            omitted.pop(field)
            rejected("stage10-rejects-omitted-" + field.replace("_", "-"),
                     lambda value=omitted:
                     validate_stage10_correctness_contract(value))
        rejected("stage10-rejects-an-extra-proof-field",
                 lambda: validate_stage10_correctness_contract({
                     **synthetic_stage10, "invented_stage": "PASS"
                 }))
        rejected("stage10-rejects-a-substituted-matrix",
                 lambda: validate_stage10_correctness_contract({
                     **synthetic_stage10, "matrix_sha256": "0" * 64
                 }))
        rejected("stage10-rejects-one-missing-rust-candidate-answer",
                 lambda: validate_stage10_correctness_contract({
                     **synthetic_stage10, "candidate_checks": 10_751
                 }))

        parent, fixture, fixture_manifest = frozen_v8.synthetic_public_inputs()
        parent["source_public_cases"] = FIXTURE_CASE_COUNT
        parent["eligible_practice_cases"] = ELIGIBLE_PUBLIC_CASES
        parent["maximum_subject_limit"] = SUBJECT_LIMIT
        parent["maximum_result_limit"] = RESULT_LIMIT
        source_records = list(fixture.values())
        for record in source_records[ELIGIBLE_PUBLIC_CASES:]:
            overflow = [None] * (RESULT_LIMIT + 1)
            record["expected"]["result"] = overflow
            record["expected"]["result_sha256"] = legacy_result_digest(overflow)
        oversized_template = next(
            record for record in source_records[ELIGIBLE_PUBLIC_CASES:]
            if record["case"]["api"] not in {"compile", "escape"}
            and source_kind(record["case"]) == "text"
        )
        oversized_template["case"]["string"] = "x" * (SUBJECT_LIMIT + 1)
        oversized_template["expected"]["result"] = None
        oversized_template["expected"]["result_sha256"] = (
            legacy_result_digest(None)
        )
        check("synthetic-full-public-archive-retains-all-10312-records",
              len(source_records) == FIXTURE_CASE_COUNT)
        check("synthetic-public-archive-has-exactly-9731-eligible-records",
              sum(bounded_public_case(row["case"], row["expected"])
                  for row in source_records) == ELIGIBLE_PUBLIC_CASES)
        check("synthetic-public-archive-explicitly-excludes-581-unsafe-records",
              sum(not bounded_public_case(row["case"], row["expected"])
                  for row in source_records)
              == FIXTURE_CASE_COUNT - ELIGIBLE_PUBLIC_CASES)
        check("synthetic-unselected-oversized-subject-remains-in-public-archive",
              oversized_template["case"]["id"] in fixture
              and not bounded_public_case(
                  oversized_template["case"], oversized_template["expected"]
              ))
        rejected("oversized-public-template-cannot-generate-a-workload",
                 lambda: make_variant(oversized_template, 0))
        validate_public_source_documents(parent, fixture_manifest)
        synthetic_v7 = {
            "postfinal_schema": "rebar-postfinal-public-practice-plan-v7",
            "protocol_version": "postfinal-public-practice-v7",
            "runner_sha256": PUBLIC_FILE_SHA256[
                "tools/postfinal_public_practice_v7.py"
            ],
            "source_public_v6_manifest_path":
                "performance/postfinal-public-v6/manifest.json",
            "source_public_v6_manifest_sha256": PUBLIC_FILE_SHA256[
                "performance/postfinal-public-v6/manifest.json"
            ],
            "source_public_v6_runner_path":
                "tools/postfinal_public_practice_v6.py",
            "source_public_v6_runner_sha256": PUBLIC_FILE_SHA256[
                "tools/postfinal_public_practice_v6.py"
            ],
            "cases": ORIGINAL_CASE_COUNT,
            "source_public_cases": FIXTURE_CASE_COUNT,
            "eligible_practice_cases": ELIGIBLE_PUBLIC_CASES,
            "all_bounded_workload_categories": CATEGORY_COUNT,
            "cohort": "calibration",
            "selection_seed": 2_026_072_404,
            "order_seed": 2_026_072_405,
            "bootstrap_seed": 2_026_072_406,
            "frozen_warmups": WARMUPS,
            "frozen_trials": PAIRED_TRIALS,
            "frozen_bootstrap_samples": BOOTSTRAP_DRAWS,
            "maximum_subject_limit": SUBJECT_LIMIT,
            "maximum_result_limit": RESULT_LIMIT,
            "holdout_accessed": False,
            "held_out_cases_generated": 0,
            "held_out_records_deserialized": 0,
            "historical_performance_read": False,
            "timing_performed": False,
            "public_operations": parent["public_operations"],
            "categories": parent["categories"],
            "selected_cases": parent["selected_cases"],
        }
        synthetic_v7_proof = validate_public_v7_parent(parent, synthetic_v7)
        check("synthetic-v7-preserves-all-8192-exact-v6-descriptors",
              synthetic_v7_proof["selected_cases_preserved"] == 8_192)
        check("synthetic-v7-binds-the-exact-pushed-manifest-hash",
              synthetic_v7_proof["sha256"] == V7_PUBLIC_MANIFEST_SHA256)
        changed_v7 = dict(synthetic_v7)
        changed_v7["selected_cases"] = [
            {**synthetic_v7["selected_cases"][0],
             "case": "cal.synthetic.substituted-v7"},
            *synthetic_v7["selected_cases"][1:],
        ]
        rejected("substituted-pushed-v7-original-case-is-rejected",
                 lambda: validate_public_v7_parent(parent, changed_v7))
        rejected("pushed-v7-wrong-original-case-count-is-rejected",
                 lambda: validate_public_v7_parent(
                     parent, dict(synthetic_v7, cases=8_191)
                 ))
        rejected("pushed-v7-concealed-historical-timing-is-rejected",
                 lambda: validate_public_v7_parent(
                     parent, dict(synthetic_v7, historical_performance_read=True)
                 ))
        rejected("pushed-v7-opened-holdout-is-rejected",
                 lambda: validate_public_v7_parent(
                     parent, dict(synthetic_v7, holdout_accessed=True)
                 ))
        selected_fixture = dict(fixture)
        selected_source = next(
            fixture[item["case"]] for item in parent["selected_cases"]
            if fixture[item["case"]]["case"]["api"]
            not in {"compile", "escape"}
            and source_kind(fixture[item["case"]]["case"]) == "text"
        )
        selected_identifier = selected_source["case"]["id"]
        selected_fixture[selected_identifier] = {
            **selected_source,
            "case": {
                **selected_source["case"],
                "string": "x" * (SUBJECT_LIMIT + 1),
            },
        }
        rejected("oversized-preserved-original-subject-is-rejected",
                 lambda: select_public_cases(parent, selected_fixture))
        selected_result_fixture = dict(fixture)
        unsafe_original_result = [None] * (RESULT_LIMIT + 1)
        selected_result_fixture[selected_identifier] = {
            **selected_source,
            "expected": {
                **selected_source["expected"],
                "result": unsafe_original_result,
                "result_sha256": legacy_result_digest(unsafe_original_result),
            },
        }
        rejected("oversized-preserved-original-result-is-rejected",
                 lambda: select_public_cases(parent, selected_result_fixture))
        rows = select_public_cases(parent, fixture)
        check("synthetic-fixture-retains-exact-10312-public-source-cases",
              len(fixture) == 10_312)
        check("synthetic-v10-expansion-retains-exact-33280-cases",
              len(rows) == 33_280)
        check("synthetic-v10-preserves-all-8192-original-identities-in-order",
              [row["case"]["id"] for row in rows[:ORIGINAL_CASE_COUNT]]
              == [item["case"] for item in parent["selected_cases"]])
        counts = collections.Counter(row["case"]["category"] for row in rows)
        check("synthetic-v10-retains-exactly-260-categories",
              len(counts) == 260)
        check("synthetic-v10-retains-exactly-128-cases-in-every-category",
              all(value == 128 for value in counts.values()))
        check("synthetic-v10-retains-all-twelve-python-operations",
              {row["case"]["api"] for row in rows} == set(PUBLIC_OPERATIONS))
        check("synthetic-v10-has-33280-unique-semantic-identities",
              len({semantic_identity(row["case"]) for row in rows}) == 33_280)
        empty = legacy_result_digest(None)
        answers = [{
            "id": row["case"]["id"], "result": None,
            "result_sha256": empty,
        } for row in rows]
        program = {
            "runner_path": GENERATOR_RELATIVE,
            "runner_sha256": hashlib.sha256(b"synthetic-v10-generator").hexdigest(),
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": hashlib.sha256(b"synthetic-v10-protocol").hexdigest(),
            "measurement_runner_path": MEASUREMENT_RUNNER_RELATIVE,
            "measurement_runner_sha256":
                hashlib.sha256(b"synthetic-v10-measurement-runner").hexdigest(),
        }
        provenance = {
            **provenance, "stage10": synthetic_stage10,
            "v8_failure": failure_proof,
        }
        manifest = build_manifest(parent, rows, answers, provenance, program)
        check("synthetic-manifest-uses-distinct-v10-schema",
              manifest["schema"] == SCHEMA)
        check("synthetic-manifest-preserves-byte-exact-original-descriptors",
              json_bytes(manifest["selected_cases"][:ORIGINAL_CASE_COUNT])
              == json_bytes(parent["selected_cases"]))
        check("synthetic-manifest-publishes-all-distinct-v10-case-identities",
              manifest["semantic_identity_count"] == CASE_COUNT
              and len(manifest["case_records"]) == CASE_COUNT)
        check("synthetic-manifest-uses-ascii-structural-identity-digest",
              manifest["semantic_identity_sha256"]
              == digest([item["semantic_identity"]
                         for item in manifest["case_records"]]))
        check("synthetic-manifest-retains-exact-observed-operation-denominators",
              set(manifest["public_operations"]) == set(PUBLIC_OPERATIONS)
              and sum(manifest["public_operations"].values()) == CASE_COUNT)
        check("synthetic-manifest-preserves-all-four-exact-input-types",
              {item["input"] for item in manifest["selected_cases"]}
              == {"text", "bytes", "bytearray", "memoryview"})
        check("synthetic-manifest-binds-all-three-dynamic-owned-program-files",
              all(manifest.get(key) == value
                  for key, value in program.items()))
        check("synthetic-manifest-binds-exact-v10-domain-and-three-seeds",
              manifest["seed_domain"] == SEED_DOMAIN
              and (manifest["selection_seed"], manifest["order_seed"],
                   manifest["bootstrap_seed"])
              == (2026072450, 2026072451, 2026072452))
        check("synthetic-manifest-binds-only-the-thirteen-field-stage10-proof",
              set(manifest["stage10_correctness"]) == STAGE10_CONTRACT_KEYS)
        check("synthetic-manifest-binds-only-the-eighteen-field-v8-failure",
              set(manifest["v8_failure"]) == V8_FAILURE_CONTRACT_KEYS)
        check("synthetic-manifest-pins-all-five-actual-v8-failure-artifacts",
              all(manifest["pinned_public_input_sha256"].get(path) == value
                  for path, value in V8_FAILURE_PINNED_SHA256.items()))
        check("synthetic-manifest-explicitly-binds-both-v6-and-v7-parents",
              manifest["source_public_v6_manifest_path"]
              == "performance/postfinal-public-v6/manifest.json"
              and manifest["source_public_v6_manifest_sha256"]
              == PUBLIC_FILE_SHA256[
                  "performance/postfinal-public-v6/manifest.json"
              ]
              and manifest["source_public_v7_manifest_path"]
              == V7_PUBLIC_MANIFEST_RELATIVE
              and manifest["source_public_v7_manifest_sha256"]
              == V7_PUBLIC_MANIFEST_SHA256)
        check("synthetic-manifest-pins-already-pushed-v7-public-manifest",
              manifest["pinned_public_input_sha256"].get(
                  V7_PUBLIC_MANIFEST_RELATIVE
              ) == V7_PUBLIC_MANIFEST_SHA256)
        check("synthetic-manifest-records-all-original-utf8-verifications",
              manifest["public_fixture_original_answers_validated"] == 10_312)
        check("synthetic-manifest-records-exactly-9731-eligible-public-sources",
              manifest["eligible_practice_cases"] == 9_731
              and manifest["bounded_eligible_public_source_cases"] == 9_731)
        check("synthetic-manifest-records-all-581-unbounded-public-sources",
              manifest["excluded_unbounded_public_cases"] == 581
              and manifest["bounded_ineligible_public_source_cases"] == 581)
        check("synthetic-manifest-records-the-exact-frozen-bounded-api-capacity",
              manifest["bounded_public_api_capacities"]
              == V7_BOUNDED_PUBLIC_API_CAPACITIES)
        check("synthetic-manifest-records-zero-archive-history-deserialization",
              manifest["opaque_history_fields_skipped"] == 10_312
              and manifest["opaque_history_values_deserialized"] == 0)
        check("synthetic-manifest-does-not-invent-a-ffi-cost",
              manifest["standalone_ffi_cost"] == "NOT MEASURED")
        check("synthetic-manifest-does-not-invent-interpreter-startup",
              manifest["standalone_startup_cost"] == "NOT MEASURED")
        check("synthetic-manifest-does-not-invent-native-allocations",
              manifest["inside_native_allocation"] == "NOT MEASURED")
        check("synthetic-manifest-does-not-invent-performance",
              manifest["performance"] == "NOT MEASURED"
              and manifest["timing_performed"] is False)
        bad_answer = dict(answers[0], result="caf\u00e9")
        bad_answer["result_sha256"] = digest(bad_answer["result"])
        rejected("manifest-rejects-old-frozen-ascii-unicode-result-digest",
                 lambda: build_manifest(
                     parent, rows, [bad_answer, *answers[1:]], provenance, program
                 ))
        missing_runner = dict(program)
        missing_runner.pop("measurement_runner_sha256")
        rejected("manifest-rejects-omitted-separate-measurement-runner-hash",
                 lambda: build_manifest(
                     parent, rows, answers, provenance, missing_runner
                 ))
        rejected("manifest-rejects-substituted-v10-generator-path",
                 lambda: build_manifest(
                     parent, rows, answers, provenance,
                     dict(program, runner_path=V8_SOURCE_RELATIVE)
                 ))
        rejected("manifest-rejects-substituted-v10-measurement-runner-path",
                 lambda: build_manifest(
                     parent, rows, answers, provenance,
                     dict(program, measurement_runner_path=V8_RUNNER_RELATIVE)
                 ))
        rejected("manifest-rejects-substituted-v10-protocol-path",
                 lambda: build_manifest(
                     parent, rows, answers, provenance,
                     dict(program, protocol_path=V8_PROTOCOL_RELATIVE)
                 ))
        rejected("manifest-rejects-an-omitted-v8-failure-proof",
                 lambda: build_manifest(
                     parent, rows, answers,
                     {key: value for key, value in provenance.items()
                      if key != "v8_failure"},
                     program,
                 ))
        rejected("manifest-rejects-a-falsely-passing-v8-failure-proof",
                 lambda: build_manifest(
                     parent, rows, answers,
                     {**provenance,
                      "v8_failure": {**failure_proof, "status": "PASS"}},
                     program,
                 ))
        rejected("manifest-rejects-an-incomplete-reference-answer-population",
                 lambda: build_manifest(
                     parent, rows, answers[:-1], provenance, program
                 ))
        check("all-twelve-public-operations-remain-explicit",
              len(PUBLIC_OPERATIONS) == len(set(PUBLIC_OPERATIONS)) == 12)
        check("all-three-owned-native-candidate-families-remain-explicit",
              len(CANDIDATES) == len(set(CANDIDATES)) == 3)
        check("baseline-remains-unmodified-cpython-re", BASELINE == "re")
        check("balanced-case-denominator-remains-exact",
              CATEGORY_COUNT * CASES_PER_CATEGORY == 33_280)
        check("original-case-denominator-remains-exact",
              ORIGINAL_CASE_COUNT == 8_192)
        check("paired-trial-denominator-remains-exact", PAIRED_TRIALS == 13)
        check("warmup-denominator-remains-exact", WARMUPS == 4)
        check("bootstrap-denominator-remains-exact", BOOTSTRAP_DRAWS == 2_000)
        check("all-raw-row-denominators-remain-exact",
              manifest["expected_raw_rows"] == 1_730_560)
        check("all-correctness-answer-denominators-remain-exact",
              manifest["expected_correctness_answers"] == 5_191_680)
        check("all-confidence-interval-denominators-remain-exact",
              manifest["expected_confidence_intervals"] == 99_843)
        check("all-process-and-native-denominators-remain-exact",
              manifest["expected_process_native_checks"] == 266_248)
        check("exact-subject-limit-remains-explicit", SUBJECT_LIMIT == 8_192)
        check("exact-result-limit-remains-explicit", RESULT_LIMIT == 128)

        rejected("synthetic-self-test-blocks-real-subprocess",
                 lambda: subprocess.run(["synthetic-forbidden"]))
        rejected("synthetic-self-test-blocks-real-worker",
                 lambda: subprocess.Popen(["synthetic-forbidden"]))
        rejected("synthetic-self-test-blocks-real-compressed-fixture",
                 lambda: gzip.open("synthetic-forbidden.gz", "rb"))
        rejected("synthetic-self-test-blocks-real-filesystem-path",
                 lambda: Path("synthetic-forbidden").open("rb"))
        rejected("synthetic-self-test-blocks-real-file-read",
                 lambda: Path("synthetic-forbidden").read_bytes())
        rejected("synthetic-self-test-blocks-real-file-creation",
                 lambda: os.open("synthetic-forbidden", os.O_CREAT))
        for name in CLOCK_NAMES:
            rejected("synthetic-self-test-blocks-" + name.replace("_", "-")
                     + "-clock", lambda clock=name: getattr(time, clock)())
        check("every-file-worker-and-clock-poison-was-actively-exercised",
              dict(blocked) == {
                  "subprocess": 1, "worker": 1,
                  "compressed-fixture": 1, "filesystem-path": 1,
                  "filesystem-read": 1, "filesystem-write": 1,
                  **{f"clock-{name}": 1 for name in CLOCK_NAMES},
              })
        check("no-candidate-is-ever-imported-by-synthetic-self-test",
              candidate_imports() == before == [])
        return {
            "schema": SELF_TEST_SCHEMA, "status": "PASS",
            "synthetic_controls": len(checks), "controls": checks,
            "fixture_files_read": 0,
            "actual_public_fixture_rows_read": 0,
            "actual_archived_history_values_deserialized": 0,
            "oracle_processes_started": 0,
            "candidate_imports": [],
            "candidate_processes": 0,
            "files_read": 0, "files_written": 0,
            "manifest_files_written": 0,
            "clock_samples": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
    finally:
        subprocess.run = original_run  # type: ignore[assignment]
        subprocess.Popen = original_popen  # type: ignore[assignment]
        gzip.open = original_gzip  # type: ignore[assignment]
        Path.open = original_path_open  # type: ignore[assignment]
        Path.read_bytes = original_path_read  # type: ignore[assignment]
        os.open = original_os_open  # type: ignore[assignment]
        for name, clock in original_clocks.items():
            setattr(time, name, clock)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--self-test", action="store_true",
                         help="run exclusively synthetic in-memory controls")
    actions.add_argument("--verify-public-fixture", action="store_true",
                         help="read-only authentication of the public fixture")
    actions.add_argument("--freeze", action="store_true",
                         help="explicitly freeze the corrected public V10 suite")
    actions.add_argument("--oracle-worker", action="store_true",
                         help=argparse.SUPPRESS)
    parser.add_argument("--role", choices=("first", "second"),
                        help=argparse.SUPPRESS)
    arguments = parser.parse_args(argv)
    if arguments.self_test:
        require(arguments.role is None,
                "synthetic self-test cannot become a reference worker")
        result = self_test()
        print(json.dumps(result, sort_keys=True,
                         ensure_ascii=True, allow_nan=False))
    elif arguments.verify_public_fixture:
        require(arguments.role is None,
                "read-only fixture verification cannot become a worker")
        result = verify_public_fixture_only()
        print(json.dumps(result, sort_keys=True,
                         ensure_ascii=True, allow_nan=False))
    elif arguments.oracle_worker:
        require(arguments.role is not None,
                "isolated V10 reference worker role is missing")
        run_oracle_worker(arguments.role)
    else:
        require(arguments.role is None,
                "V10 freeze cannot become a reference worker")
        freeze_public_development()


if __name__ == "__main__":
    try:
        main()
    except PublicExpansionError as error:
        print(json.dumps({
            "schema": SCHEMA, "status": "FAIL", "error": str(error),
            "performance": "NOT MEASURED",
        }, sort_keys=True, ensure_ascii=True, allow_nan=False), file=sys.stderr)
        raise SystemExit(1) from error
