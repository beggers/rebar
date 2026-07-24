#!/usr/bin/env python3
"""Preserve the genuine first full-public Python-reference digest failure."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_stage15 as original


SCHEMA = "rebar-python-re-public-contract-v15-reference-failure-v1"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage15_failure.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15-FAILURE.md"
REPORT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-contract-v15-reference-failures.json"
)
REPORT_PATH = ROOT / REPORT_RELATIVE

STAGE15_SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage15.py"
STAGE15_SOURCE_SHA256 = (
    "fc288f0771462a850d5ac4859ba05fe3731953e7160419ddcdbf98e8563ac580"
)
STAGE15_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15.md"
STAGE15_PROTOCOL_SHA256 = (
    "546c5e6152310eda173e182011cb13ab359e0960018b76cd6ce18c7b6006d691"
)
ORIGINAL_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle.json"
)
ORIGINAL_REFERENCE_SHA256 = (
    "755cb818f59259bb5adb05a93782afc3eef12e001c41a976ba4b9258ae54ac01"
)
FALSE_DECLARED_DIGEST = (
    "0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94"
)
ACTUAL_DURABLE_DIGEST = (
    "7a3bed83093800085fe1bd084820108142929f60e37632b3c24a02c6a4584d72"
)
# The original worker declared the ordinary transport digest.  The frozen V15
# validator deliberately hashes the surrogate-portable normalized structure.
# A complete stream containing an unpaired surrogate distinguishes the two.
DURABLE_TRANSPORT_DIGEST = FALSE_DECLARED_DIGEST
FROZEN_VALIDATOR_DIGEST = ACTUAL_DURABLE_DIGEST
CASES = 3_584
STDLIB_CHECKS = 7_168
DECLARED_DIGEST_COUNT = 4
SEED = 2026072479
SEED_DOMAIN = "rebar/python-re/public-contract/v15"
MATRIX_SHA256 = (
    "3e643ab0c455bc789e4939af2dba73af18abb033f2f34f003b49b1299b35eeeb"
)
STAGE14_SOURCE_RELATIVE = original.STAGE14_SOURCE_RELATIVE
STAGE14_SOURCE_SHA256 = (
    "5caba6e5d92935a1877fb34bd3c1e266d07c67385f847477041312959104ec58"
)
STAGE14_PROTOCOL_RELATIVE = original.STAGE14_PROTOCOL_RELATIVE
STAGE14_PROTOCOL_SHA256 = (
    "b20b5b3876fba06cdf41b9a99825157d0ca6ba84b8bc7abfd71b49e44fdd7505"
)
STAGE14_REFERENCE_RELATIVE = original.STAGE14_SELF_RELATIVE
STAGE14_REFERENCE_SHA256 = (
    "7da9c6aa5fa1db4ef0dea593d8f9d501ecc952aa62ed7bf5a0f17d0b726b04bf"
)
STAGE14_ALL_RELATIVE = original.STAGE14_ALL_RELATIVE
STAGE14_ALL_SHA256 = (
    "f9243bd27a4d4ae24c0c3f0b24785e381440fc19c8911b52719cc6813bc1e8cc"
)
OFFICIAL_FAILURE_RELATIVE = original.OFFICIAL_FAILURE_RELATIVE
OFFICIAL_FAILURE_SHA256 = (
    "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f"
)
OFFICIAL_SOURCE_RELATIVE = original.OFFICIAL_SOURCE_RELATIVE
OFFICIAL_SOURCE_SHA256 = original.OFFICIAL_SOURCE_SHA256
OFFICIAL_PROTOCOL_RELATIVE = original.OFFICIAL_PROTOCOL_RELATIVE
OFFICIAL_PROTOCOL_SHA256 = original.OFFICIAL_PROTOCOL_SHA256
OFFICIAL_REPORT_RELATIVE = original.OFFICIAL_REPORT_RELATIVE
OFFICIAL_REPORT_SHA256 = original.OFFICIAL_REPORT_SHA256
CORE_FAMILIES = ("rust", "vm", "zig")
REFERENCE_ROLES = ("stdlib-a", "stdlib-b")
MAX_REPORT_BYTES = original.official_locale.MAX_JSON_BYTES


class FailureRecorderError(AssertionError):
    """The genuine first reference failure was concealed or rewritten."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise FailureRecorderError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise FailureRecorderError(
            "the preserved public-reference evidence is not portable canonical JSON"
        ) from error


def portable_digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def frozen_validator_digest(value: Any) -> str:
    """Apply the actual unchanged, surrogate-aware frozen V15 contract."""

    digest = original.digest(value)
    require(original.official_locale.is_sha256(digest),
            "the unchanged frozen V15 record validator has no real digest")
    return digest


def destination(value: Any) -> str:
    require(type(value) is str and bool(value),
            "the one-use reference-failure destination must be text")
    path = PurePosixPath(value)
    require(not path.is_absolute()
            and ".." not in path.parts
            and "\\" not in value
            and "\x00" not in value
            and str(path) == value
            and value == REPORT_RELATIVE,
            "only the exact additive V15 reference-failure output is authorized")
    return value


def _expected(overrides: Mapping[str, str] | None = None) -> dict[str, str]:
    values = {
        "raw": ORIGINAL_REFERENCE_SHA256,
        "declared": FALSE_DECLARED_DIGEST,
        "actual": ACTUAL_DURABLE_DIGEST,
    }
    if overrides is not None:
        require(isinstance(overrides, Mapping)
                and set(overrides) == set(values),
                "a synthetic reference failure omitted a mandatory digest")
        values = dict(overrides)
    require(all(original.official_locale.is_sha256(value)
                for value in values.values())
            and len(set(values.values())) == len(values),
            "a genuine raw, false, or portable reference digest was substituted")
    return values


def validate_provenance(value: Any) -> dict[str, Any]:
    require(isinstance(value, dict),
            "the actual failed Python streams have no current native provenance")
    expected: dict[str, Any] = {
        "source_path": STAGE15_SOURCE_RELATIVE,
        "source_sha256": STAGE15_SOURCE_SHA256,
        "protocol_path": STAGE15_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE15_PROTOCOL_SHA256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "observation_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "base_audit_source_path": original.V7_BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": original.V7_BASE_SOURCE_SHA256,
        "base_audit_path": original.V7_BASE_REPORT_RELATIVE,
        "base_audit_sha256": original.V7_BASE_REPORT_SHA256,
        "strict_audit_source_path": original.V7_STRICT_SOURCE_RELATIVE,
        "strict_audit_source_sha256": original.V7_STRICT_SOURCE_SHA256,
        "strict_audit_path": original.V7_STRICT_REPORT_RELATIVE,
        "strict_audit_sha256": original.V7_STRICT_REPORT_SHA256,
        "native_source_count": 12,
        "native_binary_count": 5,
        "official_source_path": OFFICIAL_SOURCE_RELATIVE,
        "official_source_sha256": OFFICIAL_SOURCE_SHA256,
        "official_protocol_path": OFFICIAL_PROTOCOL_RELATIVE,
        "official_protocol_sha256": OFFICIAL_PROTOCOL_SHA256,
        "official_report_path": OFFICIAL_REPORT_RELATIVE,
        "official_report_sha256": OFFICIAL_REPORT_SHA256,
        "official_methods_per_role": 146,
        "official_role_count": 4,
        "official_skipped": 0,
        "official_v2_failure_path": OFFICIAL_FAILURE_RELATIVE,
        "official_v2_failure_sha256": OFFICIAL_FAILURE_SHA256,
        "official_v2_failure_historical": True,
        "stage14_source_path": STAGE14_SOURCE_RELATIVE,
        "stage14_source_sha256": STAGE14_SOURCE_SHA256,
        "stage14_protocol_path": STAGE14_PROTOCOL_RELATIVE,
        "stage14_protocol_sha256": STAGE14_PROTOCOL_SHA256,
        "stage14_self_oracle_path": STAGE14_REFERENCE_RELATIVE,
        "stage14_self_oracle_sha256": STAGE14_REFERENCE_SHA256,
        "stage14_all_candidate_path": STAGE14_ALL_RELATIVE,
        "stage14_all_candidate_sha256": STAGE14_ALL_SHA256,
        "stage14_cases_per_candidate": 128,
        "stage14_candidate_checks": 384,
        "historical_stage10_only": True,
        "historical_stage10_qualifies_current_sources": False,
    }
    for key, observed in expected.items():
        require(value.get(key) == observed
                and type(value.get(key)) is type(observed),
                "the genuine failed reference provenance changed: " + key)
    source_map = value.get("source_sha256_by_family")
    native_map = value.get("native_sha256_by_family")
    require(isinstance(source_map, dict)
            and set(source_map) == set(CORE_FAMILIES)
            and isinstance(native_map, dict)
            and set(native_map) == set(CORE_FAMILIES),
            "the failed reference omitted an independently owned native family")
    for family in CORE_FAMILIES:
        sources = source_map[family]
        natives = native_map[family]
        require(isinstance(sources, dict)
                and set(sources)
                == set(original.source_v7.source_v6.OWNED_SOURCE_PATHS[family])
                and all(original.official_locale.is_sha256(digest)
                        for digest in sources.values())
                and isinstance(natives, dict)
                and set(natives)
                == set(original.source_v7.source_v6.OWNED_NATIVE_PATHS[
                    family
                ].values())
                and all(original.official_locale.is_sha256(digest)
                        for digest in natives.values()),
                "the failed reference changed a real owned native: " + family)
    return value


def _capture_rejections(document: dict[str, Any],
                        provenance: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def invoke(context: str) -> None:
        try:
            original._validate_complete_reference(document, provenance)
        except (AssertionError, RuntimeError, KeyError, TypeError, ValueError) as error:
            message = str(error)
            require("complete real standard-Python comparison" in message,
                    "the unchanged V15 validator rejected an unrelated obligation")
            records.append({
                "context": context,
                "rejected": True,
                "exception_type": type(error).__name__,
                "message": message,
            })
        else:
            raise FailureRecorderError(
                "the unchanged V15 reference validator accepted a false digest: "
                + context
            )

    invoke("outside")
    with original._stage15_context():
        invoke("inside")
    require([item["context"] for item in records] == ["outside", "inside"]
            and all(item["rejected"] is True for item in records),
            "both original isolated validator contexts were not actually rejected")
    return records


def validate_failed_reference(
    document: Any,
    provenance: dict[str, Any],
    *,
    raw_sha256: str,
    _expected_digests: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    pinned = _expected(_expected_digests)
    require(raw_sha256 == pinned["raw"],
            "the exact original first V15 reference bytes were substituted")
    validate_provenance(provenance)
    require(isinstance(document, dict),
            "the actually recorded original failed Python reference is missing")
    expected: dict[str, Any] = {
        "schema": original.SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": STAGE15_SOURCE_RELATIVE,
        "source_sha256": STAGE15_SOURCE_SHA256,
        "protocol_path": STAGE15_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE15_PROTOCOL_SHA256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cohort_cases": {
            name: count for name, _operation, count in original.stage07.COHORTS
        },
        "cases": CASES,
        "stdlib_checks": STDLIB_CHECKS,
        "independent_stdlib_roles": list(REFERENCE_ROLES),
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for key, observed in expected.items():
        require(document.get(key) == observed
                and type(document.get(key)) is type(observed),
                "the preserved genuine false-PASS report changed: " + key)
    require(document.get("current_provenance") == provenance,
            "the false-PASS reference was detached from its authenticated graph")
    first = document.get("baseline_records")
    second = document.get("second_records")
    require(isinstance(first, list)
            and isinstance(second, list)
            and len(first) == CASES
            and len(second) == CASES
            and all(isinstance(row, dict) for row in first)
            and all(isinstance(row, dict) for row in second)
            and first == second,
            "one of the two original complete Python streams was concealed")
    matrix = original.build_matrix()
    identifiers = [row["id"] for row in matrix]
    require([row.get("id") for row in first] == identifiers
            and [row.get("id") for row in second] == identifiers,
            "the original full frozen reference matrix was reordered or weakened")
    transport_first = portable_digest(first)
    transport_second = portable_digest(second)
    contract_first = frozen_validator_digest(first)
    contract_second = frozen_validator_digest(second)
    require(transport_first == pinned["declared"]
            and transport_second == pinned["declared"]
            and contract_first == pinned["actual"]
            and contract_second == pinned["actual"]
            and transport_first != contract_first,
            "the complete original streams do not retain both genuine digests")
    require(document.get("baseline_record_sha256") == pinned["declared"]
            and document.get("second_record_sha256") == pinned["declared"]
            and pinned["declared"] != pinned["actual"],
            "the two genuinely false top-level record hashes were hidden")
    workers = document.get("reference_worker_reports")
    require(isinstance(workers, dict)
            and set(workers) == set(REFERENCE_ROLES),
            "one of the two actually isolated reference workers was omitted")
    for role, records in zip(REFERENCE_ROLES, (first, second), strict=True):
        worker = workers[role]
        require(isinstance(worker, dict),
                "the real Python worker evidence is missing: " + role)
        expected_worker: dict[str, Any] = {
            "schema": original.SCHEMA + "-worker",
            "status": "PASS",
            "role": role,
            "python": "3.14.6",
            "source_sha256": STAGE15_SOURCE_SHA256,
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cases": CASES,
            "cohort_cases": expected["cohort_cases"],
            "record_sha256": pinned["declared"],
            "guard": {"baseline_only": True, "candidate_imported": False},
            "native_binary_sha256": {},
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        for key, observed in expected_worker.items():
            require(worker.get(key) == observed
                    and type(worker.get(key)) is type(observed),
                    "the preserved actual reference worker changed: "
                    + role + "/" + key)
        observed_records = worker.get("records")
        require(isinstance(observed_records, list)
                and len(observed_records) == CASES
                and observed_records == records
                and [row.get("id") for row in observed_records] == identifiers
                and portable_digest(observed_records) == pinned["declared"]
                and frozen_validator_digest(observed_records)
                == pinned["actual"],
                "a complete real Python worker stream was changed: " + role)
    return document


def _scope() -> dict[str, Any]:
    return {
        "original_reference_preserved_byte_for_byte": True,
        "original_reference_rewritten": False,
        "reference_or_candidate_rerun": False,
        "actual_reference_workers_reexecuted": False,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "candidate_result_inferred": False,
        "unexecuted_candidate_status": "NOT RUN",
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "benchmark_or_timing_executed": False,
        "locale_compilations": 0,
        "production_workers_started": 0,
        "authorized_output": REPORT_RELATIVE,
    }


def build_report(
    document: dict[str, Any],
    provenance: dict[str, Any],
    *,
    source_sha256: str,
    protocol_sha256: str,
    raw_sha256: str,
    _expected_digests: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    require(original.official_locale.is_sha256(source_sha256)
            and original.official_locale.is_sha256(protocol_sha256)
            and source_sha256 != protocol_sha256,
            "the additive failure recorder was not genuinely source-frozen")
    expected = _expected(_expected_digests)
    validate_failed_reference(document, provenance, raw_sha256=raw_sha256,
                              _expected_digests=_expected_digests)
    rejections = _capture_rejections(document, provenance)
    return {
        "schema": SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha256,
        "stage15_source_path": STAGE15_SOURCE_RELATIVE,
        "stage15_source_sha256": STAGE15_SOURCE_SHA256,
        "stage15_protocol_path": STAGE15_PROTOCOL_RELATIVE,
        "stage15_protocol_sha256": STAGE15_PROTOCOL_SHA256,
        "original_reference_path": ORIGINAL_REFERENCE_RELATIVE,
        "original_reference_sha256": raw_sha256,
        "original_reference_status": "PASS",
        "original_reference_is_valid": False,
        "original_reference_document": copy.deepcopy(document),
        "current_provenance": copy.deepcopy(provenance),
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cohort_cases": {
            name: count for name, _operation, count in original.stage07.COHORTS
        },
        "cases": CASES,
        "stdlib_checks": STDLIB_CHECKS,
        "actual_reference_record_count": STDLIB_CHECKS,
        "actual_reference_worker_count": len(REFERENCE_ROLES),
        "actual_reference_roles": list(REFERENCE_ROLES),
        "declared_record_sha256": expected["declared"],
        "actual_record_sha256": expected["actual"],
        "durable_transport_record_sha256": expected["declared"],
        "frozen_validator_record_sha256": expected["actual"],
        "declared_digest_count": DECLARED_DIGEST_COUNT,
        "digest_mismatch_count": DECLARED_DIGEST_COUNT,
        "validator_rejections": rejections,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "candidate_status_by_family": {
            family: "NOT RUN" for family in CORE_FAMILIES
        },
        "failure_preserved": True,
        "reference_rerun": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "benchmark_or_timing_executed": False,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
        "scope": _scope(),
    }


def validate_report(
    report: Any,
    *,
    _expected_digests: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    expected = _expected(_expected_digests)
    require(isinstance(report, dict),
            "the complete genuine V15 reference-failure report is missing")
    fields: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "protocol_path": PROTOCOL_RELATIVE,
        "stage15_source_path": STAGE15_SOURCE_RELATIVE,
        "stage15_source_sha256": STAGE15_SOURCE_SHA256,
        "stage15_protocol_path": STAGE15_PROTOCOL_RELATIVE,
        "stage15_protocol_sha256": STAGE15_PROTOCOL_SHA256,
        "original_reference_path": ORIGINAL_REFERENCE_RELATIVE,
        "original_reference_sha256": expected["raw"],
        "original_reference_status": "PASS",
        "original_reference_is_valid": False,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cohort_cases": {
            name: count for name, _operation, count in original.stage07.COHORTS
        },
        "cases": CASES,
        "stdlib_checks": STDLIB_CHECKS,
        "actual_reference_record_count": STDLIB_CHECKS,
        "actual_reference_worker_count": 2,
        "actual_reference_roles": list(REFERENCE_ROLES),
        "declared_record_sha256": expected["declared"],
        "actual_record_sha256": expected["actual"],
        "durable_transport_record_sha256": expected["declared"],
        "frozen_validator_record_sha256": expected["actual"],
        "declared_digest_count": DECLARED_DIGEST_COUNT,
        "digest_mismatch_count": DECLARED_DIGEST_COUNT,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "candidate_status_by_family": {
            family: "NOT RUN" for family in CORE_FAMILIES
        },
        "failure_preserved": True,
        "reference_rerun": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "benchmark_or_timing_executed": False,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    for name, actual in fields.items():
        require(report.get(name) == actual
                and type(report.get(name)) is type(actual),
                "the preserved genuine reference failure changed: " + name)
    source = report.get("source_sha256")
    protocol = report.get("protocol_sha256")
    require(original.official_locale.is_sha256(source)
            and original.official_locale.is_sha256(protocol)
            and source != protocol,
            "the genuine failure recorder lacks distinct source fingerprints")
    provenance = report.get("current_provenance")
    validate_provenance(provenance)
    document = report.get("original_reference_document")
    validate_failed_reference(
        document, provenance,
        raw_sha256=report["original_reference_sha256"],
        _expected_digests=_expected_digests,
    )
    expected_rejections = _capture_rejections(document, provenance)
    require(report.get("validator_rejections") == expected_rejections,
            "the original unchanged validator did not reject both real contexts")
    require(report.get("scope") == _scope(),
            "the failure recorder reran, fabricated, or benchmarked production")
    return report


def authenticate_provenance() -> dict[str, Any]:
    original.official_locale.verify_runtime()
    original.frozen.candidate_free()
    require(original.SOURCE_RELATIVE == STAGE15_SOURCE_RELATIVE
            and original.PROTOCOL_RELATIVE == STAGE15_PROTOCOL_RELATIVE
            and original.SELF_ORACLE_RELATIVE == ORIGINAL_REFERENCE_RELATIVE
            and original.EXPECTED_CASES == CASES
            and original.SEED == SEED
            and original.SEED_DOMAIN == SEED_DOMAIN
            and original.MATRIX_SHA256 == MATRIX_SHA256,
            "the actually falsified immutable V15 producer was substituted")
    for relative, expected in (
        (STAGE15_SOURCE_RELATIVE, STAGE15_SOURCE_SHA256),
        (STAGE15_PROTOCOL_RELATIVE, STAGE15_PROTOCOL_SHA256),
    ):
        path = original.official_locale.checked_repo_path(relative)
        observed = original.official_locale.sha256_path(
            path, maximum=original.frozen.MAX_SOURCE_BYTES,
        )
        require(observed == expected,
                "a genuinely frozen V15 source changed before failure capture: "
                + relative)
    actual = original._authenticate_current_provenance()
    validate_provenance(actual)
    original.frozen.candidate_free()
    return actual


def write_exclusive(report: Mapping[str, Any]) -> str:
    destination(REPORT_RELATIVE)
    parent = REPORT_PATH.parent
    require(parent.is_dir() and not parent.is_symlink(),
            "the exact genuine-failure output parent is not a safe directory")
    require(not REPORT_PATH.is_symlink(),
            "the additive failure output cannot traverse a symbolic link")
    payload = canonical(report) + b"\n"
    require(0 < len(payload) <= MAX_REPORT_BYTES,
            "the complete preserved reference evidence exceeds its bounded size")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(REPORT_PATH, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        directory = os.open(
            parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    return hashlib.sha256(payload).hexdigest()


def record_failure() -> dict[str, Any]:
    original.official_locale.verify_runtime()
    original.frozen.candidate_free()
    destination(REPORT_RELATIVE)
    require(not REPORT_PATH.exists() and not REPORT_PATH.is_symlink(),
            "the one-use genuine first-reference failure was already preserved")
    provenance = authenticate_provenance()
    document, raw_sha = original.stage06._read_public_document(
        ORIGINAL_REFERENCE_RELATIVE,
        expected_sha256=ORIGINAL_REFERENCE_SHA256,
    )
    validate_failed_reference(document, provenance, raw_sha256=raw_sha)
    source_path = original.official_locale.checked_repo_path(SOURCE_RELATIVE)
    protocol_path = original.official_locale.checked_repo_path(PROTOCOL_RELATIVE)
    source_sha = original.official_locale.sha256_path(
        source_path, maximum=original.frozen.MAX_SOURCE_BYTES,
    )
    protocol_sha = original.official_locale.sha256_path(
        protocol_path, maximum=original.frozen.MAX_SOURCE_BYTES,
    )
    report = build_report(
        document, provenance,
        source_sha256=source_sha,
        protocol_sha256=protocol_sha,
        raw_sha256=raw_sha,
    )
    require(validate_report(report) is report,
            "the complete preserved V15 reference failure did not self-validate")
    original.frozen.candidate_free()
    original_path = original.official_locale.checked_repo_path(
        ORIGINAL_REFERENCE_RELATIVE,
    )
    require(original.official_locale.sha256_path(
        original_path, maximum=original.official_locale.MAX_JSON_BYTES,
    ) == ORIGINAL_REFERENCE_SHA256,
            "the genuine failed original reference changed before preservation")
    evidence_sha = write_exclusive(report)
    require(original.official_locale.sha256_path(
        original_path, maximum=original.official_locale.MAX_JSON_BYTES,
    ) == ORIGINAL_REFERENCE_SHA256,
            "the genuine first reference was changed while recording the failure")
    original.frozen.candidate_free()
    return {
        "schema": SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "evidence": REPORT_RELATIVE,
        "evidence_sha256": evidence_sha,
        "original_reference_path": ORIGINAL_REFERENCE_RELATIVE,
        "original_reference_sha256": ORIGINAL_REFERENCE_SHA256,
        "declared_record_sha256": FALSE_DECLARED_DIGEST,
        "actual_record_sha256": ACTUAL_DURABLE_DIGEST,
        "durable_transport_record_sha256": DURABLE_TRANSPORT_DIGEST,
        "frozen_validator_record_sha256": FROZEN_VALIDATOR_DIGEST,
        "cases": CASES,
        "stdlib_checks": STDLIB_CHECKS,
        "declared_digest_count": DECLARED_DIGEST_COUNT,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _synthetic_failure() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, str]
]:
    rows = [{
        "id": item["id"], "cohort": item["cohort"],
        "synthetic_only": True,
        "value": "\ud800" if index == 0 else index,
    } for index, item in enumerate(original.build_matrix())]
    declared = portable_digest(rows)
    actual = frozen_validator_digest(rows)
    require(declared != actual,
            "the synthetic control omitted the genuine surrogate digest failure")
    raw = portable_digest({"synthetic_original_bytes": True})
    expected = {"raw": raw, "declared": declared, "actual": actual}
    source_families = {
        family: {
            relative: portable_digest({"synthetic_source": relative})
            for relative in original.source_v7.source_v6.OWNED_SOURCE_PATHS[
                family
            ]
        }
        for family in CORE_FAMILIES
    }
    native_families = {
        family: {
            relative: portable_digest({"synthetic_native": relative})
            for relative in original.source_v7.source_v6.OWNED_NATIVE_PATHS[
                family
            ].values()
        }
        for family in CORE_FAMILIES
    }
    provenance: dict[str, Any] = {
        "source_path": STAGE15_SOURCE_RELATIVE,
        "source_sha256": STAGE15_SOURCE_SHA256,
        "protocol_path": STAGE15_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE15_PROTOCOL_SHA256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "observation_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "base_audit_source_path": original.V7_BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": original.V7_BASE_SOURCE_SHA256,
        "base_audit_path": original.V7_BASE_REPORT_RELATIVE,
        "base_audit_sha256": original.V7_BASE_REPORT_SHA256,
        "strict_audit_source_path": original.V7_STRICT_SOURCE_RELATIVE,
        "strict_audit_source_sha256": original.V7_STRICT_SOURCE_SHA256,
        "strict_audit_path": original.V7_STRICT_REPORT_RELATIVE,
        "strict_audit_sha256": original.V7_STRICT_REPORT_SHA256,
        "native_source_count": 12,
        "native_binary_count": 5,
        "source_sha256_by_family": source_families,
        "native_sha256_by_family": native_families,
        "official_source_path": OFFICIAL_SOURCE_RELATIVE,
        "official_source_sha256": OFFICIAL_SOURCE_SHA256,
        "official_protocol_path": OFFICIAL_PROTOCOL_RELATIVE,
        "official_protocol_sha256": OFFICIAL_PROTOCOL_SHA256,
        "official_report_path": OFFICIAL_REPORT_RELATIVE,
        "official_report_sha256": OFFICIAL_REPORT_SHA256,
        "official_methods_per_role": 146,
        "official_role_count": 4,
        "official_skipped": 0,
        "official_v2_failure_path": OFFICIAL_FAILURE_RELATIVE,
        "official_v2_failure_sha256": OFFICIAL_FAILURE_SHA256,
        "official_v2_failure_historical": True,
        "stage14_source_path": STAGE14_SOURCE_RELATIVE,
        "stage14_source_sha256": STAGE14_SOURCE_SHA256,
        "stage14_protocol_path": STAGE14_PROTOCOL_RELATIVE,
        "stage14_protocol_sha256": STAGE14_PROTOCOL_SHA256,
        "stage14_self_oracle_path": STAGE14_REFERENCE_RELATIVE,
        "stage14_self_oracle_sha256": STAGE14_REFERENCE_SHA256,
        "stage14_all_candidate_path": STAGE14_ALL_RELATIVE,
        "stage14_all_candidate_sha256": STAGE14_ALL_SHA256,
        "stage14_cases_per_candidate": 128,
        "stage14_candidate_checks": 384,
        "historical_stage10_only": True,
        "historical_stage10_qualifies_current_sources": False,
    }
    cohorts = {
        name: count for name, _operation, count in original.stage07.COHORTS
    }
    workers = {
        role: {
            "schema": original.SCHEMA + "-worker",
            "status": "PASS",
            "role": role,
            "python": "3.14.6",
            "source_sha256": STAGE15_SOURCE_SHA256,
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cases": CASES,
            "cohort_cases": cohorts,
            "records": copy.deepcopy(rows),
            "record_sha256": declared,
            "guard": {"baseline_only": True, "candidate_imported": False},
            "native_binary_sha256": {},
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        for role in REFERENCE_ROLES
    }
    document: dict[str, Any] = {
        "schema": original.SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": STAGE15_SOURCE_RELATIVE,
        "source_sha256": STAGE15_SOURCE_SHA256,
        "protocol_path": STAGE15_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE15_PROTOCOL_SHA256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": len(cohorts),
        "cohort_cases": cohorts,
        "cases": CASES,
        "stdlib_checks": STDLIB_CHECKS,
        "independent_stdlib_roles": list(REFERENCE_ROLES),
        "baseline_records": copy.deepcopy(rows),
        "second_records": copy.deepcopy(rows),
        "reference_worker_reports": workers,
        "baseline_record_sha256": declared,
        "second_record_sha256": declared,
        "mismatches": 0,
        "failure_records": [],
        "current_provenance": provenance,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    return document, provenance, expected


def self_test() -> dict[str, Any]:
    original.official_locale.verify_runtime()
    original.frozen.candidate_free()
    inherited = original.self_test()
    require(inherited.get("status") == "PASS"
            and inherited.get("result") == "PASS"
            and inherited.get("check_count", 0) >= 1_700
            and inherited.get("candidate_imports") == 0
            and inherited.get("candidate_processes") == 0
            and inherited.get("files_read") == 0
            and inherited.get("files_written") == 0
            and inherited.get("clock_samples") == 0
            and inherited.get("production_evidence_written") is False
            and inherited.get("benchmark_or_timing_executed") is False,
            "the immutable full-public candidate-free safety controls failed")
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        require(type(name) is str and bool(name)
                and not any(row["name"] == name for row in checks),
                "a genuine first-failure safety control was duplicated: " + str(name))
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, operation: Callable[[], Any]) -> None:
        try:
            operation()
        except (
            FailureRecorderError, original.frozen.OracleIntegrityError,
            AssertionError, RuntimeError, KeyError, TypeError,
            ValueError, OSError, UnicodeError,
        ):
            check(name, True)
        else:
            check(name, False)

    with original.stage06.previous._candidate_free_file_and_timing_guard() as effects:
        document, provenance, expected = _synthetic_failure()
        observed = validate_failed_reference(
            document, provenance, raw_sha256=expected["raw"],
            _expected_digests=expected,
        )
        check("accept-only-complete-synthetic-two-worker-digest-failure",
              observed is document)
        check("preserve-all-7168-original-reference-observations",
              len(document["baseline_records"])
              + len(document["second_records"]) == STDLIB_CHECKS)
        check("preserve-both-complete-original-stdlib-worker-streams",
              set(document["reference_worker_reports"]) == set(REFERENCE_ROLES))
        check("preserve-four-actually-false-worker-and-reference-digests",
              document["baseline_record_sha256"]
              == document["second_record_sha256"]
              == document["reference_worker_reports"]["stdlib-a"]["record_sha256"]
              == document["reference_worker_reports"]["stdlib-b"]["record_sha256"]
              == expected["declared"]
              and expected["declared"] != expected["actual"])
        check("retain-durable-transport-digest-of-both-complete-worker-streams",
              portable_digest(document["baseline_records"])
              == expected["declared"]
              and portable_digest(document["second_records"])
              == expected["declared"])
        check("retain-distinct-frozen-surrogate-aware-validator-digest",
              frozen_validator_digest(document["baseline_records"])
              == expected["actual"]
              and frozen_validator_digest(document["second_records"])
              == expected["actual"]
              and expected["actual"] != expected["declared"])
        rejections = _capture_rejections(document, provenance)
        check("reject-false-reference-outside-and-inside-original-context",
              [item["context"] for item in rejections] == ["outside", "inside"])
        source_sha = portable_digest({"synthetic_recorder_source": True})
        protocol_sha = portable_digest({"synthetic_recorder_protocol": True})
        report = build_report(
            document, provenance,
            source_sha256=source_sha,
            protocol_sha256=protocol_sha,
            raw_sha256=expected["raw"],
            _expected_digests=expected,
        )
        check("accept-complete-exclusive-synthetic-genuine-failure",
              validate_report(report, _expected_digests=expected) is report)

        for label, field, value in (
            ("false-passing-reference-failure", "status", "PASS"),
            ("false-passing-reference-result", "result", "PASS"),
            ("wrong-original-reference-path", "original_reference_path", REPORT_RELATIVE),
            ("rewritten-original-reference-bytes", "original_reference_sha256", "0" * 64),
            ("forged-false-worker-digest", "declared_record_sha256", "0" * 64),
            ("forged-portable-observation-digest", "actual_record_sha256", "0" * 64),
            ("forged-durable-transport-digest",
             "durable_transport_record_sha256", "0" * 64),
            ("forged-frozen-surrogate-validator-digest",
             "frozen_validator_record_sha256", "0" * 64),
            ("hidden-fourth-digest-failure", "declared_digest_count", 3),
            ("concealed-reference-observation", "actual_reference_record_count", 7167),
            ("concealed-reference-role", "actual_reference_worker_count", 1),
            ("forged-original-validity", "original_reference_is_valid", True),
            ("invented-candidate-process", "candidate_processes", 1),
            ("invented-candidate-evidence", "candidate_reports_created", 1),
            ("candidate-import", "candidate_imports", 1),
            ("rerun-original-reference", "reference_rerun", True),
            ("fabricated-performance", "performance", "1.5x"),
            ("hidden-benchmark", "benchmark_or_timing_executed", True),
            ("hidden-holdout", "holdout_cases_read", 1),
            ("foreign-protocol", "stage15_protocol_sha256", "0" * 64),
            ("foreign-failed-producer", "stage15_source_sha256", "0" * 64),
        ):
            poisoned = dict(report)
            poisoned[field] = value
            reject("reject-" + label,
                   lambda wrong=poisoned: validate_report(
                       wrong, _expected_digests=expected,
                   ))
        for label, mutation in (
            ("missing-full-first-reference",
             lambda item: item["baseline_records"].pop()),
            ("missing-full-second-reference",
             lambda item: item["second_records"].pop()),
            ("missing-reference-worker",
             lambda item: item["reference_worker_reports"].pop("stdlib-b")),
            ("missing-first-worker-record",
             lambda item: item["reference_worker_reports"]["stdlib-a"][
                 "records"
             ].pop()),
            ("missing-second-worker-record",
             lambda item: item["reference_worker_reports"]["stdlib-b"][
                 "records"
             ].pop()),
            ("concealed-first-worker-digest",
             lambda item: item["reference_worker_reports"]["stdlib-a"].update(
                 record_sha256=expected["actual"]
             )),
            ("concealed-second-worker-digest",
             lambda item: item["reference_worker_reports"]["stdlib-b"].update(
                 record_sha256=expected["actual"]
             )),
            ("forged-first-top-level-digest",
             lambda item: item.update(baseline_record_sha256=expected["actual"])),
            ("forged-second-top-level-digest",
             lambda item: item.update(second_record_sha256=expected["actual"])),
            ("changed-original-matrix-case",
             lambda item: item["baseline_records"][0].update(id="fake:0000")),
            ("changed-original-public-answer",
             lambda item: item["second_records"][0].update(value=-1)),
            ("hidden-reference-performance",
             lambda item: item.update(benchmark_or_timing_executed=True)),
        ):
            poisoned = copy.deepcopy(document)
            mutation(poisoned)
            reject("reject-" + label,
                   lambda wrong=poisoned: validate_failed_reference(
                       wrong, provenance,
                       raw_sha256=expected["raw"],
                       _expected_digests=expected,
                   ))
        for role in REFERENCE_ROLES:
            poisoned = dict(report)
            poisoned["validator_rejections"] = [
                item for item in report["validator_rejections"]
                if item["context"] != ("outside" if role == "stdlib-a"
                                       else "inside")
            ]
            reject("reject-omitted-validator-rejection/" + role,
                   lambda wrong=poisoned: validate_report(
                       wrong, _expected_digests=expected,
                   ))
        for family in CORE_FAMILIES:
            poisoned = {
                **report,
                "candidate_status_by_family": {
                    **report["candidate_status_by_family"],
                    family: "PASS",
                },
            }
            reject("reject-invented-candidate-success/" + family,
                   lambda wrong=poisoned: validate_report(
                       wrong, _expected_digests=expected,
                   ))
        check("accept-only-exact-additive-failure-output",
              destination(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, poisoned in (
            ("original-false-pass-reference", ORIGINAL_REFERENCE_RELATIVE),
            ("old-stage15-native-output", original.ALL_CANDIDATE_RELATIVE),
            ("genuine-generic-alias-reference", STAGE14_REFERENCE_RELATIVE),
            ("genuine-generic-alias-candidates", STAGE14_ALL_RELATIVE),
            ("first-official-rust-failure", OFFICIAL_FAILURE_RELATIVE),
            ("absolute-reference-failure", "/" + REPORT_RELATIVE),
            ("traversing-reference-failure", "../" + REPORT_RELATIVE),
            ("backslash-reference-failure", REPORT_RELATIVE.replace("/", "\\")),
            ("nul-reference-failure", REPORT_RELATIVE + "\x00"),
            ("nontext-reference-failure", 7),
        ):
            reject("reject-" + label,
                   lambda value=poisoned: destination(value))
        check("never-launch-reference-candidate-or-native-workers",
              effects["workers"] == 0)
        check("never-read-or-rewrite-original-production-evidence",
              effects["files"] == 0)
        check("never-sample-performance-clock-or-holdout",
              effects["timing"] == 0)
        check("never-draw-production-entropy",
              effects["entropy"] == 0)
        check("all-candidate-free-effect-counters-remain-zero",
              all(value == 0 for value in effects.values()))
        original.frozen.candidate_free()

    failures = [item["name"] for item in checks if item["passed"] is not True]
    require(not failures and len(checks) >= 50,
            "a genuine first-reference failure control was weakened: "
            + json.dumps(failures, ensure_ascii=True))
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "synthetic_only": True,
        "checks": checks,
        "check_count": len(checks),
        "failed": [],
        "inherited_stage15_control_count": inherited["check_count"],
        "cases": CASES,
        "stdlib_checks": STDLIB_CHECKS,
        "declared_digest_count": DECLARED_DIGEST_COUNT,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "files_read": 0,
        "files_written": 0,
        "clock_samples": 0,
        "workers_started": 0,
        "reference_rerun": False,
        "actual_reference_read": False,
        "failure_report_written": False,
        "production_evidence_written": False,
        "approved_output": REPORT_RELATIVE,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preserve only the actually observed first V15 digest failure.",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run in-memory candidate-free recorder safety checks")
    modes.add_argument("--record", action="store_true",
                       help="exclusively preserve the frozen actual first failure")
    arguments = parser.parse_args(argv)
    result = self_test() if arguments.self_test else record_failure()
    print(json.dumps(result, ensure_ascii=True, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
