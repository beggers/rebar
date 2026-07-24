#!/usr/bin/env python3
"""Recheck complete Python regex behavior with durable, context-free evidence."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _stage17_os
    from pathlib import Path as _Stage17Path

    _stage17_root = str(_Stage17Path(__file__).resolve().parent.parent)
    _stage17_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_universal_public_oracle_stage17 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _stage17_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _stage17_entry,
         _stage17_root, *sys.argv[1:]],
    )

import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable, Iterator

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_stage15 as previous


stage07 = previous.stage07
stage10 = previous.stage10
stage06 = previous.stage06
frozen = previous.frozen
official_locale = previous.official_locale
source_v7 = previous.source_v7
official_v3 = previous.official_v3

SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage17.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17.md"
SCHEMA = "rebar-python-re-public-contract-v17"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SELF_ORACLE_SCHEMA = SCHEMA + "-self-oracle"
ALL_CANDIDATE_SCHEMA = SCHEMA + "-all-candidates"
METADATA_SCHEMA = SCHEMA + "-isolated-public-metadata"
METADATA_ENVIRONMENT = "REBAR_PUBLIC_CONTRACT_V17_AUTHENTICATED_METADATA"
OBSERVATION_DOMAIN = "rebar/python-re/public-contract/v17"
SEED = 2026072485
SEED_DOMAIN = OBSERVATION_DOMAIN
EXPECTED_CASES = 3_584
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
MATRIX_SHA256 = (
    "e1c6ccf6cbb057f3e3cb708c1b4efe2a175bc77d6eda5e127cae18e5455cfa47"
)
NATIVE_LOADER_ALIASES = previous.NATIVE_LOADER_ALIASES

V15_SOURCE_RELATIVE = previous.SOURCE_RELATIVE
V15_SOURCE_SHA256 = (
    "fc288f0771462a850d5ac4859ba05fe3731953e7160419ddcdbf98e8563ac580"
)
V15_PROTOCOL_RELATIVE = previous.PROTOCOL_RELATIVE
V15_PROTOCOL_SHA256 = (
    "546c5e6152310eda173e182011cb13ab359e0960018b76cd6ce18c7b6006d691"
)
V15_RAW_REFERENCE_RELATIVE = previous.SELF_ORACLE_RELATIVE
V15_RAW_REFERENCE_SHA256 = (
    "755cb818f59259bb5adb05a93782afc3eef12e001c41a976ba4b9258ae54ac01"
)
V15_DECLARED_RECORD_SHA256 = (
    "0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94"
)
V15_PORTABLE_RECORD_SHA256 = (
    "7a3bed83093800085fe1bd084820108142929f60e37632b3c24a02c6a4584d72"
)
V15_FAILURE_SOURCE_RELATIVE = (
    "tools/python_re_universal_public_oracle_stage15_failure.py"
)
V15_FAILURE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15-FAILURE.md"
)
V15_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v15-reference-failures.json"
)
V15_FAILURE_SCHEMA = "rebar-python-re-public-contract-v15-reference-failure-v1"
# Root actually published the corrected controller, protocol, and one genuine
# truthful failure report after an exclusively recorded real first attempt.
V15_FAILURE_SOURCE_SHA256 = (
    "07a522f263cd9e0baad022f91988d034b3cde3013b143bd1f9a77174fa0b58b6"
)
V15_FAILURE_PROTOCOL_SHA256 = (
    "6aa2b8e5bcd6867af60c570d19508a67e0094eedca4ab815266e0f91e2c83b03"
)
V15_FAILURE_SHA256 = (
    "cb71e1a44549c7c76c3bf08900e6107d2b49e789e5002afc725d1e9df0c92880"
)

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v17-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v17-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v17-all.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    role: (
        "candidates/evidence/python-re-universal-public-oracle-v17-"
        + role + "-failures.json"
    )
    for role in REQUIRED_CANDIDATES
}
APPROVED_OUTPUTS = (
    SELF_ORACLE_RELATIVE, SELF_ORACLE_FAILURE_RELATIVE,
    ALL_CANDIDATE_RELATIVE,
    *(CANDIDATE_FAILURE_RELATIVES[role] for role in REQUIRED_CANDIDATES),
)
WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_universal_public_oracle_stage17 import _worker_entry;"
    "raise SystemExit(_worker_entry(sys.argv[2],sys.argv[3]))"
)
METADATA_WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_universal_public_oracle_stage17 "
    "import _metadata_worker_entry;"
    "raise SystemExit(_metadata_worker_entry(sys.argv[2],sys.argv[3]))"
)

_FROZEN_JSON_DUMPS = json.dumps
_FROZEN_JSON_LOADS = json.loads
_FROZEN_SHA256 = hashlib.sha256


def canonical(value: Any) -> bytes:
    """Return the exact immutable ASCII JSON bytes persisted on disk."""

    return _FROZEN_JSON_DUMPS(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii", "strict")


def digest(value: Any) -> str:
    """Hash the normalized durable JSON representation exactly once."""

    return _FROZEN_SHA256(canonical(value)).hexdigest()


def _durable_round_trip(value: Any) -> tuple[Any, bytes]:
    payload = canonical(value)
    parsed = _FROZEN_JSON_LOADS(payload)
    frozen.require(
        canonical(parsed) == payload and digest(parsed) == digest(value),
        "the actual persisted JSON representation is not durable or idempotent",
    )
    return parsed, payload


def _cohort_seed(cohort: str) -> str:
    frozen.require(
        cohort in {name for name, _operation, _count in stage07.COHORTS},
        "the durable public matrix received an unknown original cohort",
    )
    return digest({"domain": SEED_DOMAIN, "seed": SEED, "cohort": cohort})


def _matrix_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cohort, operation, count in stage07.COHORTS:
        seed = _cohort_seed(cohort)
        for index in range(count):
            row: dict[str, Any] = {
                "id": f"{cohort}:{index:04d}",
                "cohort": cohort, "operation": operation,
                "index": index, "seed": seed,
            }
            if cohort == "real-locale":
                row.update({
                    "byte": index % 256,
                    "locale": ("iso88591", "utf8")[(index // 256) % 2],
                    "compiled_before_switch": bool(index // 512),
                })
            if cohort == "shared-pattern-threads":
                row["threads"] = (4, 8)[index % 2]
            rows.append(row)
    return rows


def validate_matrix(value: Any) -> None:
    frozen.require(
        isinstance(value, list)
        and len(value) == EXPECTED_CASES
        and len(stage07.COHORTS) == 8
        and len({row.get("id") for row in value
                 if isinstance(row, dict)}) == EXPECTED_CASES
        and value == _matrix_rows()
        and digest(value) == MATRIX_SHA256,
        "the durable V17 matrix changed an original public obligation",
    )


def build_matrix() -> list[dict[str, Any]]:
    rows = _matrix_rows()
    validate_matrix(rows)
    return rows


def _require_published_failure() -> None:
    published = (
        ("source", V15_FAILURE_SOURCE_SHA256),
        ("protocol", V15_FAILURE_PROTOCOL_SHA256),
        ("report", V15_FAILURE_SHA256),
    )
    for name, value in published:
        frozen.require(
            isinstance(value, str) and official_locale.is_sha256(value),
            "the truthful preserved V15 failure is not published: " + name,
        )
    frozen.require(
        len({value for _name, value in published}) == len(published),
        "the preserved V15 failure reuses a source or evidence fingerprint",
    )


def _verify_source(relative: str, expected: str) -> None:
    frozen.require(
        isinstance(expected, str) and official_locale.is_sha256(expected),
        "an actual durable-oracle source fingerprint is missing",
    )
    frozen.require(
        official_locale.sha256_path(
            official_locale.checked_repo_path(relative),
            maximum=frozen.MAX_SOURCE_BYTES,
        ) == expected,
        "a genuinely frozen public source or protocol changed: " + relative,
    )


def _contains_portable_surrogate(value: Any) -> bool:
    if isinstance(value, dict):
        if (
            value.get("type")
            == stage10.previous.SURROGATE_TAG
            and value.get("encoding") == "utf-8/surrogatepass"
        ):
            return True
        return any(_contains_portable_surrogate(item)
                   for item in value.values())
    if isinstance(value, list):
        return any(_contains_portable_surrogate(item) for item in value)
    return False


def _validate_falsified_v15_raw(
    document: Any, provenance: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "schema": previous.SELF_ORACLE_SCHEMA,
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": V15_SOURCE_RELATIVE,
        "source_sha256": V15_SOURCE_SHA256,
        "protocol_path": V15_PROTOCOL_RELATIVE,
        "protocol_sha256": V15_PROTOCOL_SHA256,
        "seed": previous.SEED, "seed_domain": previous.SEED_DOMAIN,
        "matrix_sha256": previous.MATRIX_SHA256,
        "cohorts": 8, "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "baseline_record_sha256": V15_DECLARED_RECORD_SHA256,
        "second_record_sha256": V15_DECLARED_RECORD_SHA256,
        "mismatches": 0, "failure_records": [],
        "candidate_imports": 0, "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen.require(isinstance(document, dict),
                   "the genuine falsely passing V15 report is absent")
    for name, value in required.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "the genuine preserved false-positive V15 result changed: " + name,
        )
    first = document.get("baseline_records")
    second = document.get("second_records")
    expected_ids = [row["id"] for row in previous.build_matrix()]
    frozen.require(
        isinstance(first, list) and isinstance(second, list)
        and len(first) == len(second) == EXPECTED_CASES
        and all(isinstance(row, dict) for row in first)
        and all(isinstance(row, dict) for row in second)
        and [row.get("id") for row in first] == expected_ids
        and [row.get("id") for row in second] == expected_ids
        and first == second
        and document.get("current_provenance") == provenance
        and digest(first) == V15_DECLARED_RECORD_SHA256
        and digest(second) == V15_DECLARED_RECORD_SHA256
        and previous.digest(first) == V15_PORTABLE_RECORD_SHA256
        and previous.digest(second) == V15_PORTABLE_RECORD_SHA256
        and previous.digest(stage10.previous._restore_portable(first))
        == V15_DECLARED_RECORD_SHA256
        and previous.digest(stage10.previous._restore_portable(second))
        == V15_DECLARED_RECORD_SHA256,
        "the actual durable V15 evidence or its double-encoding failure changed",
    )
    for identity in (
        "bounded-unicode:0010", "bounded-unicode:0011",
        "bounded-unicode:0026", "bounded-unicode:0027",
        "bounded-unicode:0042",
    ):
        match = next((row for row in first if row.get("id") == identity), None)
        frozen.require(
            isinstance(match, dict) and _contains_portable_surrogate(match),
            "the actual falsified surrogate-bearing row is absent: " + identity,
        )
    workers = document.get("reference_worker_reports")
    frozen.require(
        isinstance(workers, dict)
        and set(workers) == {"stdlib-a", "stdlib-b"},
        "the real falsely passing V15 report concealed a Python worker",
    )
    for role, observed in (("stdlib-a", first), ("stdlib-b", second)):
        worker = workers[role]
        frozen.require(
            isinstance(worker, dict)
            and worker.get("schema") == previous.SCHEMA + "-worker"
            and worker.get("status") == "PASS"
            and worker.get("role") == role
            and worker.get("python") == "3.14.6"
            and worker.get("source_sha256") == V15_SOURCE_SHA256
            and worker.get("seed") == previous.SEED
            and worker.get("seed_domain") == previous.SEED_DOMAIN
            and worker.get("matrix_sha256") == previous.MATRIX_SHA256
            and worker.get("cases") == EXPECTED_CASES
            and worker.get("records") == observed
            and worker.get("record_sha256") == V15_DECLARED_RECORD_SHA256
            and digest(worker["records"]) == V15_DECLARED_RECORD_SHA256
            and previous.digest(worker["records"])
            == V15_PORTABLE_RECORD_SHA256
            and worker.get("guard")
            == {"baseline_only": True, "candidate_imported": False}
            and worker.get("native_binary_sha256") == {},
            "a real falsely passing V15 Python worker was altered: " + role,
        )
    rejected = False
    try:
        previous._validate_complete_reference(document, provenance)
    except frozen.OracleIntegrityError:
        rejected = True
    frozen.require(
        rejected,
        "the independently falsified V15 report was falsely declared qualified",
    )
    return document


def _validate_failure_report(
    document: Any, *, raw: dict[str, Any], provenance: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "schema": V15_FAILURE_SCHEMA,
        "status": "FAIL", "result": "FAIL", "python": "3.14.6",
        "source_path": V15_FAILURE_SOURCE_RELATIVE,
        "source_sha256": V15_FAILURE_SOURCE_SHA256,
        "protocol_path": V15_FAILURE_PROTOCOL_RELATIVE,
        "protocol_sha256": V15_FAILURE_PROTOCOL_SHA256,
        "stage15_source_path": V15_SOURCE_RELATIVE,
        "stage15_source_sha256": V15_SOURCE_SHA256,
        "stage15_protocol_path": V15_PROTOCOL_RELATIVE,
        "stage15_protocol_sha256": V15_PROTOCOL_SHA256,
        "original_reference_path": V15_RAW_REFERENCE_RELATIVE,
        "original_reference_sha256": V15_RAW_REFERENCE_SHA256,
        "declared_record_sha256": V15_DECLARED_RECORD_SHA256,
        "actual_record_sha256": V15_PORTABLE_RECORD_SHA256,
        "durable_transport_record_sha256": V15_DECLARED_RECORD_SHA256,
        "frozen_validator_record_sha256": V15_PORTABLE_RECORD_SHA256,
        "declared_digest_count": 4,
        "actual_reference_record_count": EXPECTED_CASES * 2,
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "seed": previous.SEED,
        "seed_domain": previous.SEED_DOMAIN,
        "matrix_sha256": previous.MATRIX_SHA256,
        "benchmark_or_timing_executed": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen.require(isinstance(document, dict),
                   "the truthful genuine V15 failure result is absent")
    for name, value in required.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "the actual preserved V15 failure changed: " + name,
        )
    frozen.require(
        document.get("original_reference_document") == raw
        and document.get("current_provenance") == provenance,
        "the truthful V15 failure omitted actual source-bound reference rows",
    )
    rejections = document.get("validator_rejections")
    frozen.require(
        isinstance(rejections, list)
        and len(rejections) == 2
        and {item.get("context") for item in rejections
             if isinstance(item, dict)} == {"inside", "outside"}
        and all(
            isinstance(item, dict)
            and item.get("rejected") is True
            and item.get("exception_type") == "OracleIntegrityError"
            and isinstance(item.get("message"), str)
            and bool(item["message"])
            for item in rejections
        ),
        "the truthful failure concealed either real independent rejection",
    )
    return document


def _authenticate_current_provenance() -> dict[str, Any]:
    official_locale.verify_runtime()
    frozen.candidate_free()
    # Absolutely no evidence may be opened before the separately produced
    # truthful failure source, protocol, and report have all been published.
    _require_published_failure()
    frozen.require(
        isinstance(V15_FAILURE_SOURCE_SHA256, str)
        and isinstance(V15_FAILURE_PROTOCOL_SHA256, str)
        and isinstance(V15_FAILURE_SHA256, str),
        "the immutable V15 failure record is not published",
    )
    for relative, expected in (
        (V15_SOURCE_RELATIVE, V15_SOURCE_SHA256),
        (V15_PROTOCOL_RELATIVE, V15_PROTOCOL_SHA256),
        (V15_FAILURE_SOURCE_RELATIVE, V15_FAILURE_SOURCE_SHA256),
        (V15_FAILURE_PROTOCOL_RELATIVE, V15_FAILURE_PROTOCOL_SHA256),
    ):
        _verify_source(relative, expected)
    actual_v15_provenance = previous._authenticate_provenance()
    raw, raw_sha = stage06._read_public_document(
        V15_RAW_REFERENCE_RELATIVE,
        expected_sha256=V15_RAW_REFERENCE_SHA256,
    )
    frozen.require(raw_sha == V15_RAW_REFERENCE_SHA256,
                   "the genuine first false-positive V15 report changed")
    _validate_falsified_v15_raw(raw, actual_v15_provenance)
    incident, incident_sha = stage06._read_public_document(
        V15_FAILURE_RELATIVE, expected_sha256=V15_FAILURE_SHA256,
    )
    frozen.require(incident_sha == V15_FAILURE_SHA256,
                   "the truthful first V15 failure result changed")
    recorder = importlib.import_module(
        "tools.python_re_universal_public_oracle_stage15_failure",
    )
    frozen.require(
        Path(recorder.__file__).resolve()
        == official_locale.checked_repo_path(V15_FAILURE_SOURCE_RELATIVE)
        and callable(getattr(recorder, "validate_report", None)),
        "the genuine preserved-failure source lost its independent validator",
    )
    frozen.require(
        recorder.validate_report(incident) is incident,
        "the truthful V15 failure did not pass its own complete validator",
    )
    _validate_failure_report(
        incident, raw=raw, provenance=actual_v15_provenance,
    )
    source_sha = official_locale.sha256_path(
        official_locale.checked_repo_path(SOURCE_RELATIVE),
        maximum=frozen.MAX_SOURCE_BYTES,
    )
    protocol_sha = official_locale.sha256_path(
        official_locale.checked_repo_path(PROTOCOL_RELATIVE),
        maximum=frozen.MAX_SOURCE_BYTES,
    )
    validate_matrix(build_matrix())
    frozen.candidate_free()
    return {
        **actual_v15_provenance,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "observation_domain": OBSERVATION_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "stage15_source_path": V15_SOURCE_RELATIVE,
        "stage15_source_sha256": V15_SOURCE_SHA256,
        "stage15_protocol_path": V15_PROTOCOL_RELATIVE,
        "stage15_protocol_sha256": V15_PROTOCOL_SHA256,
        "stage15_raw_reference_path": V15_RAW_REFERENCE_RELATIVE,
        "stage15_raw_reference_sha256": V15_RAW_REFERENCE_SHA256,
        "stage15_reference_status": "FALSIFIED",
        "stage15_declared_record_sha256": V15_DECLARED_RECORD_SHA256,
        "stage15_actual_record_sha256": V15_PORTABLE_RECORD_SHA256,
        "stage15_durable_transport_record_sha256": (
            V15_DECLARED_RECORD_SHA256
        ),
        "stage15_frozen_validator_record_sha256": (
            V15_PORTABLE_RECORD_SHA256
        ),
        "stage15_failure_source_path": V15_FAILURE_SOURCE_RELATIVE,
        "stage15_failure_source_sha256": V15_FAILURE_SOURCE_SHA256,
        "stage15_failure_protocol_path": V15_FAILURE_PROTOCOL_RELATIVE,
        "stage15_failure_protocol_sha256": V15_FAILURE_PROTOCOL_SHA256,
        "stage15_failure_path": V15_FAILURE_RELATIVE,
        "stage15_failure_sha256": V15_FAILURE_SHA256,
        "stage15_reference_record_count": EXPECTED_CASES * 2,
        "stage15_candidate_runs": 0,
        "durable_json_canonicalization": "frozen-json-ascii-sort-keys-v17",
        "durable_reference_hash_domain": "persisted-normalized-json-once-v17",
    }


def _authenticate_provenance() -> dict[str, Any]:
    return _authenticate_current_provenance()


@contextmanager
def _stage17_context() -> Iterator[None]:
    """Bind every actual transport and matching process to one durable codec."""

    stage10_updates: dict[str, Any] = {
        "SOURCE_RELATIVE": SOURCE_RELATIVE,
        "PROTOCOL_RELATIVE": PROTOCOL_RELATIVE,
        "SCHEMA": SCHEMA,
        "SELF_TEST_SCHEMA": SELF_TEST_SCHEMA,
        "SELF_ORACLE_SCHEMA": SELF_ORACLE_SCHEMA,
        "ALL_CANDIDATE_SCHEMA": ALL_CANDIDATE_SCHEMA,
        "OBSERVATION_DOMAIN": OBSERVATION_DOMAIN,
        "MATRIX_SHA256": MATRIX_SHA256,
        "SELF_ORACLE_RELATIVE": SELF_ORACLE_RELATIVE,
        "SELF_ORACLE_FAILURE_RELATIVE": SELF_ORACLE_FAILURE_RELATIVE,
        "ALL_CANDIDATE_RELATIVE": ALL_CANDIDATE_RELATIVE,
        "CANDIDATE_FAILURE_RELATIVES": CANDIDATE_FAILURE_RELATIVES,
        "WORKER_BOOTSTRAP": WORKER_BOOTSTRAP,
        "METADATA_SCHEMA": METADATA_SCHEMA,
        "METADATA_ENVIRONMENT": METADATA_ENVIRONMENT,
        "METADATA_WORKER_BOOTSTRAP": METADATA_WORKER_BOOTSTRAP,
        "canonical": canonical,
        "digest": digest,
        "_authenticate_current_provenance": _authenticate_current_provenance,
    }
    stage07_updates: dict[str, Any] = {
        "SOURCE_RELATIVE": SOURCE_RELATIVE,
        "PROTOCOL_RELATIVE": PROTOCOL_RELATIVE,
        "SCHEMA": SCHEMA,
        "SELF_TEST_SCHEMA": SELF_TEST_SCHEMA,
        "SELF_ORACLE_SCHEMA": SELF_ORACLE_SCHEMA,
        "ALL_CANDIDATE_SCHEMA": ALL_CANDIDATE_SCHEMA,
        "SEED": SEED,
        "SEED_DOMAIN": SEED_DOMAIN,
        "MATRIX_SHA256": MATRIX_SHA256,
        "SELF_ORACLE_RELATIVE": SELF_ORACLE_RELATIVE,
        "SELF_ORACLE_FAILURE_RELATIVE": SELF_ORACLE_FAILURE_RELATIVE,
        "ALL_CANDIDATE_RELATIVE": ALL_CANDIDATE_RELATIVE,
        "CANDIDATE_FAILURE_RELATIVES": CANDIDATE_FAILURE_RELATIVES,
        "WORKER_BOOTSTRAP": WORKER_BOOTSTRAP,
        "canonical": canonical,
        "digest": digest,
        "build_matrix": build_matrix,
        "validate_matrix": validate_matrix,
        "_authenticate_current_provenance": _authenticate_current_provenance,
        "_validate_worker_report": (
            stage10.previous._FROZEN_VALIDATE_WORKER_REPORT
        ),
        "_worker_report": stage10._worker_report,
        "_run_worker": stage10._run_worker,
        "_worker_environment": stage10._worker_environment,
        "_surface_obligation": stage10._surface_obligation,
    }
    with previous._stage15_context():
        saved_stage10 = {key: getattr(stage10, key) for key in stage10_updates}
        saved_stage07 = {key: getattr(stage07, key) for key in stage07_updates}
        try:
            for key, value in stage10_updates.items():
                setattr(stage10, key, value)
            for key, value in stage07_updates.items():
                setattr(stage07, key, value)
            yield
        finally:
            for key, value in saved_stage07.items():
                setattr(stage07, key, value)
            for key, value in saved_stage10.items():
                setattr(stage10, key, value)


def _metadata_worker_entry(role: str, source_sha256: str) -> int:
    try:
        with _stage17_context():
            report = stage10._metadata_worker_report(role, source_sha256)
            parsed, payload = _durable_round_trip(report)
            frozen.require(
                parsed.get("record_sha256") == digest(parsed["records"]),
                "the isolated signature metadata is not durably normalized",
            )
            sys.stdout.buffer.write(payload + b"\n")
            sys.stdout.buffer.flush()
            return 0
    except (Exception, RecursionError) as error:
        failure = {
            "schema": METADATA_SCHEMA,
            "status": "FAIL", "role": role,
            "error": stage07._normalize(error),
            "production_matching_executed": False,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        sys.stdout.buffer.write(canonical(failure) + b"\n")
        sys.stdout.buffer.flush()
        return 1


def _worker_entry(role: str, source_sha256: str) -> int:
    """Never enter the old portable worker context or rewrite parsed rows."""

    try:
        with _stage17_context():
            provenance = _authenticate_current_provenance()
            frozen.require(
                provenance.get("source_sha256") == source_sha256,
                "the independent durable worker changed its frozen source",
            )
            payload = os.environ.pop(METADATA_ENVIRONMENT, None)
            if role in REQUIRED_CANDIDATES:
                frozen.require(
                    isinstance(payload, str)
                    and 0 < len(payload.encode("ascii"))
                    <= stage10.MAX_METADATA_BYTES
                    and "inspect" not in sys.modules
                    and "tokenize" not in sys.modules,
                    "the actual matcher omitted independently isolated metadata",
                )
                metadata = _FROZEN_JSON_LOADS(payload)
                stage10._CHILD_METADATA = stage10._validate_metadata_report(
                    metadata, role=role, source_sha256=source_sha256,
                )
                frozen.require(
                    stage10._CHILD_METADATA["native_binary_sha256"]
                    == provenance["native_sha256_by_family"].get(role),
                    "isolated metadata does not authenticate this native engine",
                )
            else:
                frozen.require(
                    role in ("stdlib-a", "stdlib-b")
                    and payload is None
                    and stage10._CHILD_METADATA is None,
                    "the genuine Python reference received native metadata",
                )
            try:
                report = stage07._worker_report(role, source_sha256)
                parsed, encoded = _durable_round_trip(report)
                frozen.require(
                    isinstance(parsed.get("records"), list)
                    and len(parsed["records"]) == EXPECTED_CASES
                    and parsed.get("record_sha256")
                    == digest(parsed["records"]),
                    "an isolated worker did not authenticate its durable rows",
                )
                sys.stdout.buffer.write(encoded + b"\n")
                sys.stdout.buffer.flush()
                return 0
            finally:
                stage10._CHILD_METADATA = None
    except (Exception, RecursionError) as error:
        report = {
            "schema": SCHEMA + "-worker", "status": "FAIL", "role": role,
            "error": stage07._normalize(error),
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        sys.stdout.buffer.write(canonical(report) + b"\n")
        sys.stdout.buffer.flush()
        return 1


def _cohort_cases() -> dict[str, int]:
    return {name: count for name, _operation, count in stage07.COHORTS}


def _validate_reference_worker(
    document: Any, *, role: str, provenance: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "schema": SCHEMA + "-worker",
        "status": "PASS", "role": role, "python": "3.14.6",
        "source_sha256": provenance["source_sha256"],
        "seed": SEED, "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cases": EXPECTED_CASES,
        "cohort_cases": _cohort_cases(),
        "guard": {"baseline_only": True, "candidate_imported": False},
        "native_binary_sha256": {},
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen.require(
        role in ("stdlib-a", "stdlib-b") and isinstance(document, dict),
        "a genuine context-independent Python worker is absent",
    )
    for key, value in required.items():
        frozen.require(
            document.get(key) == value
            and type(document.get(key)) is type(value),
            "a genuine durable Python worker changed " + role + ": " + key,
        )
    records = document.get("records")
    frozen.require(
        isinstance(records, list)
        and len(records) == EXPECTED_CASES
        and all(isinstance(row, dict) for row in records)
        and [row.get("id") for row in records]
        == [row["id"] for row in build_matrix()]
        and document.get("record_sha256") == digest(records)
        and _durable_round_trip(records)[0] == records,
        "a durable Python worker concealed a record or double-encoded Unicode",
    )
    return document


def _validate_complete_reference(
    document: Any, provenance: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance.get("source_sha256"),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance.get("protocol_sha256"),
        "seed": SEED, "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8, "cohort_cases": _cohort_cases(),
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "mismatches": 0, "failure_records": [],
        "current_provenance": provenance,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen.require(
        isinstance(document, dict) and isinstance(provenance, dict),
        "the complete durable two-process Python evidence is absent",
    )
    for key, value in required.items():
        frozen.require(
            document.get(key) == value
            and type(document.get(key)) is type(value),
            "the durable real Python reference changed: " + key,
        )
    workers = document.get("reference_worker_reports")
    frozen.require(
        isinstance(workers, dict)
        and set(workers) == {"stdlib-a", "stdlib-b"},
        "the durable Python reference omitted a real complete worker",
    )
    first_worker = _validate_reference_worker(
        workers["stdlib-a"], role="stdlib-a", provenance=provenance,
    )
    second_worker = _validate_reference_worker(
        workers["stdlib-b"], role="stdlib-b", provenance=provenance,
    )
    first = document.get("baseline_records")
    second = document.get("second_records")
    frozen.require(
        isinstance(first, list)
        and isinstance(second, list)
        and len(first) == len(second) == EXPECTED_CASES
        and first == first_worker["records"]
        and second == second_worker["records"]
        and first == second
        and document.get("baseline_record_sha256") == digest(first)
        and document.get("second_record_sha256") == digest(second)
        and first_worker["record_sha256"]
        == document["baseline_record_sha256"]
        and second_worker["record_sha256"]
        == document["second_record_sha256"],
        "a durable 3,584-row Python stream or actual worker digest changed",
    )
    parsed, _payload = _durable_round_trip(document)
    frozen.require(parsed == document,
                   "the genuine reference changes after actual JSON persistence")
    return document


def _validate_complete_all(
    document: Any, *, reference: dict[str, Any], provenance: dict[str, Any],
) -> dict[str, Any]:
    reference = _validate_complete_reference(reference, provenance)
    required = {
        "schema": ALL_CANDIDATE_SCHEMA,
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED, "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8, "cohort_cases": _cohort_cases(),
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": EXPECTED_CASES * len(REQUIRED_CANDIDATES),
        "baseline_record_sha256": reference["baseline_record_sha256"],
        "second_record_sha256": reference["second_record_sha256"],
        "self_oracle_path": SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": _FROZEN_SHA256(
            canonical(reference) + b"\n",
        ).hexdigest(),
        "mismatches": 0,
        "current_provenance": provenance,
        "candidate_cross_delegation": False,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen.require(isinstance(document, dict),
                   "the durable complete three-native comparison is missing")
    for key, value in required.items():
        frozen.require(
            document.get(key) == value
            and type(document.get(key)) is type(value),
            "the durable three-family proof changed: " + key,
        )
    first = document.get("baseline_records")
    second = document.get("second_reference_records")
    workers = document.get("reference_worker_reports")
    frozen.require(
        first == reference["baseline_records"]
        and second == reference["second_records"]
        and workers == reference["reference_worker_reports"]
        and digest(first) == reference["baseline_record_sha256"]
        and digest(second) == reference["second_record_sha256"],
        "the durable native comparison lost an actual complete Python stream",
    )
    reports = document.get("candidate_reports")
    frozen.require(
        isinstance(reports, dict)
        and set(reports) == set(REQUIRED_CANDIDATES),
        "the durable comparison omitted an independent native family",
    )
    ids = [row["id"] for row in build_matrix()]
    for role in REQUIRED_CANDIDATES:
        report = reports[role]
        records = report.get("records") if isinstance(report, dict) else None
        frozen.require(
            isinstance(report, dict)
            and report.get("candidate") == role
            and report.get("module") == "candidates." + role + "_candidate"
            and report.get("status") == "PASS"
            and report.get("cases") == EXPECTED_CASES
            and report.get("cohort_cases") == _cohort_cases()
            and isinstance(records, list)
            and len(records) == EXPECTED_CASES
            and all(isinstance(row, dict) for row in records)
            and [row.get("id") for row in records] == ids
            and records == first
            and report.get("record_sha256") == digest(records)
            and report.get("mismatches") == 0
            and report.get("failure_records") == []
            and report.get("failures_recorded") == 0
            and report.get("native_binary_sha256")
            == provenance["native_sha256_by_family"][role]
            and report.get("benchmark_or_timing_executed") is False
            and report.get("performance_fixtures_read") == 0
            and report.get("holdout_cases_read") == 0
            and report.get("performance") == "NOT MEASURED",
            "a durable 3,584-row native matcher changed its real result: " + role,
        )
        guard = report.get("guard")
        metadata = (guard.get("isolated_public_metadata")
                    if isinstance(guard, dict) else None)
        frozen.require(
            isinstance(guard, dict)
            and guard.get("family") == role
            and all(guard.get(key) is True for key in (
                "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
                "third_party_regex_blocked", "cross_family_blocked",
                "foreign_dynamic_libraries_blocked",
            ))
            and guard.get("native_loader_aliases_blocked")
            == list(NATIVE_LOADER_ALIASES)
            and isinstance(metadata, dict)
            and metadata.get("enabled") is True
            and metadata.get("schema") == METADATA_SCHEMA
            and metadata.get("role") == role
            and metadata.get("source_sha256") == provenance["source_sha256"]
            and metadata.get("surface_cases") == 256
            and official_locale.is_sha256(metadata.get("record_sha256"))
            and metadata.get("production_matching_executed") is False
            and metadata.get("metadata_and_matcher_processes_distinct") is True
            and metadata.get("matcher_inspect_loaded") is False
            and metadata.get("matcher_tokenizer_loaded") is False,
            "a durable native worker weakened its no-delegation guard: " + role,
        )
    parsed, _payload = _durable_round_trip(document)
    frozen.require(parsed == document,
                   "the native result changes after actual JSON persistence")
    return document


def _exclusive_evidence(document: dict[str, Any], relative: str) -> str:
    frozen.require(
        type(relative) is str and relative in APPROVED_OUTPUTS,
        "the durable oracle rejected an unauthorized evidence destination",
    )
    stage07.exact_output(relative, relative)
    parsed, encoded = _durable_round_trip(document)
    frozen.require(parsed == document,
                   "the exclusively persisted evidence is not normalized")
    payload = encoded + b"\n"
    target = ROOT / relative
    parent = target.parent
    frozen.require(
        parent.is_dir()
        and not parent.is_symlink()
        and parent.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))
        and not target.is_symlink(),
        "the exclusive durable result escaped its exact repository directory",
    )
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(parent, directory_flags)
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(target.name, flags, 0o600, dir_fd=directory)
        try:
            pending = memoryview(payload)
            while pending:
                count = os.write(descriptor, pending)
                frozen.require(count > 0,
                               "the one-use durable evidence write stalled")
                pending = pending[count:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.fsync(directory)
    finally:
        os.close(directory)
    return _FROZEN_SHA256(payload).hexdigest()


def _validated_exclusive_evidence(
    document: dict[str, Any], relative: str,
    validator: Callable[[dict[str, Any]], dict[str, Any]],
) -> str:
    """Independently validate the exact parsed output before touching disk."""

    frozen.require(
        stage07.SOURCE_RELATIVE != SOURCE_RELATIVE
        and stage07.digest is not digest,
        "exclusive validation must begin outside every mutable worker context",
    )
    parsed, payload = _durable_round_trip(document)
    frozen.require(
        parsed == document
        and canonical(parsed) == payload
        and validator(parsed) is parsed,
        "the exact future output failed independent outside-context validation",
    )
    with _stage17_context():
        frozen.require(
            stage07.canonical is canonical
            and stage07.digest is digest
            and canonical(parsed) == payload
            and validator(parsed) is parsed,
            "the exact future output changed inside the actual worker context",
        )
    frozen.require(
        stage07.SOURCE_RELATIVE != SOURCE_RELATIVE
        and stage07.digest is not digest
        and canonical(parsed) == payload
        and validator(parsed) is parsed,
        "the exact future output failed after the actual worker context ended",
    )
    return _exclusive_evidence(parsed, relative)


def _preserve_reference_failure(
    *, role: str, provenance: dict[str, Any], locales: dict[str, Any],
    workers: dict[str, Any],
    error: BaseException | None = None,
    failures: list[dict[str, Any]] | None = None,
) -> str:
    frozen.require(role in ("stdlib-a", "stdlib-b"),
                   "refusing to preserve an unknown Python reference failure")
    first = workers.get("stdlib-a")
    second = workers.get("stdlib-b")
    first_records = first.get("records") if isinstance(first, dict) else None
    second_records = second.get("records") if isinstance(second, dict) else None
    mismatches = failures if failures is not None else []
    report = {
        "schema": SELF_ORACLE_SCHEMA + "-failure",
        "status": "FAIL", "result": "FAIL", "python": "3.14.6",
        "failed_role": role,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED, "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8, "cohort_cases": _cohort_cases(),
        "expected_cases": EXPECTED_CASES,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "completed_stdlib_roles": list(workers),
        "reference_worker_reports": workers,
        "baseline_records": first_records,
        "second_records": second_records,
        "baseline_record_sha256": (
            digest(first_records) if isinstance(first_records, list) else None
        ),
        "second_record_sha256": (
            digest(second_records) if isinstance(second_records, list) else None
        ),
        "mismatches": len(mismatches),
        "failure_records": mismatches,
        "failures_recorded": len(mismatches),
        "worker_failure": (
            error.details if isinstance(error, stage07.PublicWorkerFailure)
            else {"kind": type(error).__name__,
                  "exception": stage07._normalize(error)}
            if error is not None else None
        ),
        "current_provenance": provenance,
        "locales": locales,
        "candidate_imports": 0, "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    fingerprint = _exclusive_evidence(report, SELF_ORACLE_FAILURE_RELATIVE)
    return SELF_ORACLE_FAILURE_RELATIVE + " (sha256 " + fingerprint + ")"


def run_self_oracle() -> dict[str, Any]:
    with _stage17_context():
        provenance = _authenticate_current_provenance()
        destination = ROOT / SELF_ORACLE_RELATIVE
        frozen.require(
            not destination.exists() and not destination.is_symlink(),
            "the genuinely durable one-use Python reference already exists",
        )
        frozen.candidate_free()
        with tempfile.TemporaryDirectory(
            prefix="rebar-public-contract-v17-locale-", dir="/tmp",
        ) as temporary:
            locales = stage07._locale_metadata(Path(temporary))
            workers: dict[str, dict[str, Any]] = {}
            for role in ("stdlib-a", "stdlib-b"):
                try:
                    worker = stage07._run_worker(
                        role,
                        source_sha256=provenance["source_sha256"],
                        locale_root=Path(temporary),
                    )
                    _validate_reference_worker(
                        worker, role=role, provenance=provenance,
                    )
                except (Exception, RecursionError) as error:
                    retained = _preserve_reference_failure(
                        role=role, provenance=provenance,
                        locales=locales, workers=workers, error=error,
                    )
                    raise frozen.OracleIntegrityError(
                        "the genuine durable Python failure was preserved in "
                        + retained,
                    ) from error
                workers[role] = worker
            first = workers["stdlib-a"]["records"]
            second = workers["stdlib-b"]["records"]
            mismatch_count, failures = stage07._mismatch_records(first, second)
            if mismatch_count:
                retained = _preserve_reference_failure(
                    role="stdlib-b", provenance=provenance,
                    locales=locales, workers=workers, failures=failures,
                )
                raise frozen.OracleIntegrityError(
                    "the complete durable Python streams disagree; preserved in "
                    + retained,
                )
            report = {
                "schema": SELF_ORACLE_SCHEMA,
                "status": "PASS", "result": "PASS", "python": "3.14.6",
                "source_path": SOURCE_RELATIVE,
                "source_sha256": provenance["source_sha256"],
                "protocol_path": PROTOCOL_RELATIVE,
                "protocol_sha256": provenance["protocol_sha256"],
                "seed": SEED, "seed_domain": SEED_DOMAIN,
                "matrix_sha256": MATRIX_SHA256,
                "cohorts": 8, "cohort_cases": _cohort_cases(),
                "cases": EXPECTED_CASES,
                "stdlib_checks": EXPECTED_CASES * 2,
                "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
                "reference_worker_reports": workers,
                "baseline_records": first,
                "second_records": second,
                "baseline_record_sha256": digest(first),
                "second_record_sha256": digest(second),
                "mismatches": 0, "failure_records": [],
                "current_provenance": provenance,
                "locales": locales,
                "candidate_imports": 0, "candidate_processes": 0,
                "benchmark_or_timing_executed": False,
                "performance_fixtures_read": 0,
                "holdout_cases_read": 0, "performance": "NOT MEASURED",
            }
            _validate_complete_reference(report, provenance)
    evidence_sha = _validated_exclusive_evidence(
        report, SELF_ORACLE_RELATIVE,
        lambda value: _validate_complete_reference(value, provenance),
    )
    frozen.candidate_free()
    return {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS", "result": "PASS",
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "complete_reference_record_arrays": 2,
        "complete_reference_worker_reports": 2,
        "mismatches": 0,
        "evidence": SELF_ORACLE_RELATIVE,
        "evidence_sha256": evidence_sha,
        "durable_round_trip_validated": True,
        "outside_context_validated": True,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _preserve_candidate_failure(
    *, role: str, provenance: dict[str, Any], reference: dict[str, Any],
    self_sha256: str, locales: dict[str, Any],
    completed: dict[str, Any],
    observed: list[dict[str, Any]] | None = None,
    failures: list[dict[str, Any]] | None = None,
    error: BaseException | None = None,
) -> str:
    frozen.require(role in REQUIRED_CANDIDATES,
                   "refusing to preserve an unowned native matching failure")
    differences = failures if failures is not None else []
    report = {
        "schema": ALL_CANDIDATE_SCHEMA + "-failure",
        "status": "FAIL", "result": "FAIL", "python": "3.14.6",
        "failed_role": role,
        "module": "candidates." + role + "_candidate",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED, "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8, "cohort_cases": _cohort_cases(),
        "cases": EXPECTED_CASES,
        "self_oracle_path": SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": self_sha256,
        "reference_worker_reports": reference["reference_worker_reports"],
        "baseline_records": reference["baseline_records"],
        "second_reference_records": reference["second_records"],
        "baseline_record_sha256": reference["baseline_record_sha256"],
        "second_record_sha256": reference["second_record_sha256"],
        "candidate_records": observed,
        "candidate_record_sha256": (
            digest(observed) if isinstance(observed, list) else None
        ),
        "mismatches": len(differences),
        "failure_records": differences,
        "failures_recorded": len(differences),
        "completed_candidate_reports": completed,
        "worker_failure": (
            error.details if isinstance(error, stage07.PublicWorkerFailure)
            else {"kind": type(error).__name__,
                  "exception": stage07._normalize(error)}
            if error is not None else None
        ),
        "current_provenance": provenance,
        "locales": locales,
        "candidate_cross_delegation": False,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    relative = CANDIDATE_FAILURE_RELATIVES[role]
    fingerprint = _exclusive_evidence(report, relative)
    return relative + " (sha256 " + fingerprint + ")"


def run_all_candidates() -> dict[str, Any]:
    with _stage17_context():
        provenance = _authenticate_current_provenance()
        destination = ROOT / ALL_CANDIDATE_RELATIVE
        frozen.require(
            not destination.exists() and not destination.is_symlink(),
            "the genuinely durable three-native report already exists",
        )
        reference, reference_sha = stage06._read_public_document(
            SELF_ORACLE_RELATIVE, expected_sha256=None,
        )
        _validate_complete_reference(reference, provenance)
        frozen.require(
            reference_sha
            == _FROZEN_SHA256(canonical(reference) + b"\n").hexdigest(),
            "the actual complete Python result is not its durable raw bytes",
        )
        completed: dict[str, Any] = {}
        with tempfile.TemporaryDirectory(
            prefix="rebar-public-contract-v17-locale-", dir="/tmp",
        ) as temporary:
            locale_root = Path(temporary)
            locales = stage07._locale_metadata(locale_root)
            frozen.require(
                locales == reference.get("locales"),
                "the actual native experiment changed its real Python locales",
            )
            for role in REQUIRED_CANDIDATES:
                try:
                    worker = stage07._run_worker(
                        role,
                        source_sha256=provenance["source_sha256"],
                        locale_root=locale_root,
                    )
                    records = worker.get("records")
                    frozen.require(
                        isinstance(records, list)
                        and len(records) == EXPECTED_CASES
                        and all(isinstance(row, dict) for row in records)
                        and [row.get("id") for row in records]
                        == [row["id"] for row in build_matrix()]
                        and worker.get("record_sha256") == digest(records),
                        "the actual native worker concealed a durable record",
                    )
                except (Exception, RecursionError) as error:
                    retained = _preserve_candidate_failure(
                        role=role, provenance=provenance,
                        reference=reference, self_sha256=reference_sha,
                        locales=locales, completed=completed,
                        error=error,
                    )
                    raise frozen.OracleIntegrityError(
                        "the actual durable native worker failure is in "
                        + retained,
                    ) from error
                mismatch_count, failures = stage07._mismatch_records(
                    reference["baseline_records"], records,
                )
                candidate = {
                    "candidate": role,
                    "module": "candidates." + role + "_candidate",
                    "status": "FAIL" if mismatch_count else "PASS",
                    "cases": EXPECTED_CASES,
                    "cohort_cases": _cohort_cases(),
                    "records": records,
                    "record_sha256": digest(records),
                    "mismatches": mismatch_count,
                    "failure_records": failures,
                    "failures_recorded": len(failures),
                    "native_binary_sha256": worker["native_binary_sha256"],
                    "guard": worker["guard"],
                    "benchmark_or_timing_executed": False,
                    "performance_fixtures_read": 0,
                    "holdout_cases_read": 0,
                    "performance": "NOT MEASURED",
                }
                completed[role] = candidate
                if mismatch_count:
                    retained = _preserve_candidate_failure(
                        role=role, provenance=provenance,
                        reference=reference, self_sha256=reference_sha,
                        locales=locales, completed=completed,
                        observed=records, failures=failures,
                    )
                    raise frozen.OracleIntegrityError(
                        "the actual " + role
                        + " durable mismatch is preserved in " + retained,
                    )
            report = {
                "schema": ALL_CANDIDATE_SCHEMA,
                "status": "PASS", "result": "PASS", "python": "3.14.6",
                "selected": "all",
                "selected_candidates": list(REQUIRED_CANDIDATES),
                "completed_candidates": list(REQUIRED_CANDIDATES),
                "comparison_complete": True,
                "source_path": SOURCE_RELATIVE,
                "source_sha256": provenance["source_sha256"],
                "protocol_path": PROTOCOL_RELATIVE,
                "protocol_sha256": provenance["protocol_sha256"],
                "seed": SEED, "seed_domain": SEED_DOMAIN,
                "matrix_sha256": MATRIX_SHA256,
                "cohorts": 8, "cohort_cases": _cohort_cases(),
                "cases_per_candidate": EXPECTED_CASES,
                "candidate_checks": EXPECTED_CASES * len(REQUIRED_CANDIDATES),
                "reference_worker_reports": reference[
                    "reference_worker_reports"
                ],
                "baseline_records": reference["baseline_records"],
                "second_reference_records": reference["second_records"],
                "baseline_record_sha256": reference[
                    "baseline_record_sha256"
                ],
                "second_record_sha256": reference["second_record_sha256"],
                "self_oracle_path": SELF_ORACLE_RELATIVE,
                "self_oracle_sha256": reference_sha,
                "candidate_reports": completed,
                "mismatches": 0,
                "current_provenance": provenance,
                "locales": locales,
                "candidate_cross_delegation": False,
                "external_regex_packages": 0,
                "benchmark_or_timing_executed": False,
                "performance_fixtures_read": 0,
                "holdout_cases_read": 0,
                "performance": "NOT MEASURED",
            }
            _validate_complete_all(
                report, reference=reference, provenance=provenance,
            )
    fingerprint = _validated_exclusive_evidence(
        report, ALL_CANDIDATE_RELATIVE,
        lambda value: _validate_complete_all(
            value, reference=reference, provenance=provenance,
        ),
    )
    frozen.candidate_free()
    return {
        "schema": ALL_CANDIDATE_SCHEMA,
        "status": "PASS", "result": "PASS", "selected": "all",
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": EXPECTED_CASES * len(REQUIRED_CANDIDATES),
        "complete_reference_record_arrays": 2,
        "complete_reference_worker_reports": 2,
        "complete_candidate_record_arrays": 3,
        "mismatches": 0,
        "durable_round_trip_validated": True,
        "outside_context_validated": True,
        "evidence": ALL_CANDIDATE_RELATIVE,
        "evidence_sha256": fingerprint,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _synthetic_full() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    native = {
        role: {
            relative: digest({"synthetic_durable_native": relative})
            for relative in source_v7.source_v6.OWNED_NATIVE_PATHS[
                role
            ].values()
        }
        for role in REQUIRED_CANDIDATES
    }
    provenance = {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": "a" * 64,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": "b" * 64,
        "native_sha256_by_family": native,
        "stage15_reference_status": "FALSIFIED",
        "stage15_raw_reference_sha256": V15_RAW_REFERENCE_SHA256,
    }
    reserved_surrogate = {
        "type": stage10.previous.SURROGATE_TAG,
        "encoding": "utf-8/surrogatepass", "hex": "eda080",
    }
    reserved_mapping = {
        "type": stage10.previous.SURROGATE_MAPPING_TAG,
        "items": [["nested", reserved_surrogate]],
    }
    records = []
    for row in build_matrix():
        observation: dict[str, Any] = {
            "id": row["id"], "cohort": row["cohort"],
            "status": "returned", "value": None, "warnings": [],
        }
        if row["id"] == "bounded-unicode:0010":
            observation["value"] = {
                "literal_high": "\ud800",
                "literal_low": "\udfff",
                "surrogate_key": {"\ud800": "surrogate-key-value"},
                "reserved_surrogate_envelope": reserved_surrogate,
                "reserved_mapping_envelope": reserved_mapping,
                "nested": ["\ud800", {"value": "\udfff"}],
            }
        records.append(observation)
    second = _FROZEN_JSON_LOADS(canonical(records))
    record_sha = digest(records)
    workers = {
        role: {
            "schema": SCHEMA + "-worker", "status": "PASS",
            "role": role, "python": "3.14.6",
            "source_sha256": provenance["source_sha256"],
            "seed": SEED, "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cases": EXPECTED_CASES,
            "cohort_cases": _cohort_cases(),
            "records": _FROZEN_JSON_LOADS(canonical(records)),
            "record_sha256": record_sha,
            "guard": {"baseline_only": True, "candidate_imported": False},
            "native_binary_sha256": {},
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        for role in ("stdlib-a", "stdlib-b")
    }
    reference = {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED, "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8, "cohort_cases": _cohort_cases(),
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "reference_worker_reports": workers,
        "baseline_records": records,
        "second_records": second,
        "baseline_record_sha256": record_sha,
        "second_record_sha256": record_sha,
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
    reports: dict[str, Any] = {}
    for role in REQUIRED_CANDIDATES:
        metadata = {
            "enabled": True, "schema": METADATA_SCHEMA,
            "role": role,
            "source_sha256": provenance["source_sha256"],
            "surface_cases": 256,
            "record_sha256": digest({"durable_synthetic_metadata": role}),
            "production_matching_executed": False,
            "metadata_and_matcher_processes_distinct": True,
            "matcher_inspect_loaded": False,
            "matcher_tokenizer_loaded": False,
        }
        guard = {
            "enabled": True, "family": role,
            "stdlib_re_blocked": True,
            "cpython_sre_blocked": True,
            "third_party_regex_blocked": True,
            "cross_family_blocked": True,
            "foreign_dynamic_libraries_blocked": True,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
            "isolated_public_metadata": metadata,
        }
        reports[role] = {
            "candidate": role,
            "module": "candidates." + role + "_candidate",
            "status": "PASS", "cases": EXPECTED_CASES,
            "cohort_cases": _cohort_cases(),
            "records": _FROZEN_JSON_LOADS(canonical(records)),
            "record_sha256": record_sha,
            "mismatches": 0,
            "failure_records": [],
            "failures_recorded": 0,
            "native_binary_sha256": native[role],
            "guard": guard,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
    report = {
        "schema": ALL_CANDIDATE_SCHEMA,
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cohort_cases": _cohort_cases(),
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": EXPECTED_CASES * len(REQUIRED_CANDIDATES),
        "reference_worker_reports": workers,
        "baseline_records": records,
        "second_reference_records": second,
        "baseline_record_sha256": record_sha,
        "second_record_sha256": record_sha,
        "self_oracle_path": SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": _FROZEN_SHA256(
            canonical(reference) + b"\n",
        ).hexdigest(),
        "candidate_reports": reports,
        "mismatches": 0,
        "current_provenance": provenance,
        "candidate_cross_delegation": False,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    return provenance, reference, report


def _synthetic_failure_report() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any],
]:
    raw = {"synthetic_only": True, "actual_raw_sha256": V15_RAW_REFERENCE_SHA256}
    provenance = {
        "synthetic_only": True,
        "source_path": V15_SOURCE_RELATIVE,
        "source_sha256": V15_SOURCE_SHA256,
    }
    report = {
        "schema": V15_FAILURE_SCHEMA,
        "status": "FAIL", "result": "FAIL", "python": "3.14.6",
        "source_path": V15_FAILURE_SOURCE_RELATIVE,
        "source_sha256": V15_FAILURE_SOURCE_SHA256,
        "protocol_path": V15_FAILURE_PROTOCOL_RELATIVE,
        "protocol_sha256": V15_FAILURE_PROTOCOL_SHA256,
        "stage15_source_path": V15_SOURCE_RELATIVE,
        "stage15_source_sha256": V15_SOURCE_SHA256,
        "stage15_protocol_path": V15_PROTOCOL_RELATIVE,
        "stage15_protocol_sha256": V15_PROTOCOL_SHA256,
        "original_reference_path": V15_RAW_REFERENCE_RELATIVE,
        "original_reference_sha256": V15_RAW_REFERENCE_SHA256,
        "original_reference_document": raw,
        "declared_record_sha256": V15_DECLARED_RECORD_SHA256,
        "actual_record_sha256": V15_PORTABLE_RECORD_SHA256,
        "durable_transport_record_sha256": V15_DECLARED_RECORD_SHA256,
        "frozen_validator_record_sha256": V15_PORTABLE_RECORD_SHA256,
        "declared_digest_count": 4,
        "actual_reference_record_count": EXPECTED_CASES * 2,
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "seed": previous.SEED,
        "seed_domain": previous.SEED_DOMAIN,
        "matrix_sha256": previous.MATRIX_SHA256,
        "validator_rejections": [
            {
                "context": label,
                "rejected": True,
                "exception_type": "OracleIntegrityError",
                "message": "synthetic complete real standard-Python comparison",
            }
            for label in ("outside", "inside")
        ],
        "current_provenance": provenance,
        "benchmark_or_timing_executed": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "performance": "NOT MEASURED",
    }
    return raw, provenance, report


def self_test() -> dict[str, Any]:
    """Prove transport and failure safety in memory without real workers."""

    frozen.candidate_free()
    inherited = stage10.self_test()
    native = source_v7.self_test()
    official = official_v3.self_test()
    frozen.require(
        inherited.get("status") == "PASS"
        and inherited.get("check_count", 0) >= 793
        and inherited.get("candidate_imports") == 0
        and inherited.get("candidate_processes") == 0
        and inherited.get("files_read") == 0
        and inherited.get("files_written") == 0
        and inherited.get("clock_samples") == 0,
        "the immutable universal source controls were weakened",
    )
    frozen.require(
        native.get("status") == "PASS"
        and native.get("passed") is True
        and native.get("check_count", 0) >= 468
        and native.get("candidate_imports") == 0
        and native.get("file_reads") == 0
        and native.get("file_writes") == 0
        and native.get("subprocesses") == 0,
        "the repaired independently owned native controls were weakened",
    )
    frozen.require(
        official.get("status") == "PASS"
        and official.get("passed") is True
        and official.get("check_count", 0) >= 96
        and official.get("candidate_imports") == 0
        and official.get("candidate_processes") == 0
        and official.get("files_read") == 0
        and official.get("subprocesses") == 0,
        "the genuinely passing official CPython source controls were weakened",
    )
    with stage06.previous._candidate_free_file_and_timing_guard() as effects:
        checks: list[dict[str, Any]] = []

        def check(name: str, condition: Any) -> None:
            frozen.require(
                isinstance(name, str) and bool(condition),
                "a genuinely durable synthetic control failed: " + str(name),
            )
            checks.append({"name": name, "passed": True})

        def reject(name: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (
                frozen.OracleIntegrityError, AssertionError, AttributeError,
                ImportError, KeyError, OSError, TypeError, UnicodeError,
                ValueError,
            ):
                check(name, True)
            else:
                check(name, False)

        check("inherit-all-793-frozen-independent-public-controls",
              inherited["check_count"] >= 793)
        check("inherit-all-468-repaired-owned-native-controls",
              native["check_count"] >= 468)
        check("inherit-all-96-genuine-official-cpython-controls",
              official["check_count"] >= 96)
        matrix = build_matrix()
        check("freeze-all-3584-original-public-case-identities",
              len(matrix) == EXPECTED_CASES
              and digest(matrix) == MATRIX_SHA256
              and len({row["id"] for row in matrix}) == EXPECTED_CASES)
        check("freeze-only-the-declared-new-durable-seed-domain",
              SEED == 2026072485
              and SEED_DOMAIN == "rebar/python-re/public-contract/v17"
              and MATRIX_SHA256 != previous.MATRIX_SHA256)
        for cohort, _operation, count in stage07.COHORTS:
            check("retain-the-exact-original-public-cohort/" + cohort,
                  sum(row["cohort"] == cohort for row in matrix) == count)
        for label, invalid in (
            ("omitted", matrix[:-1]),
            ("duplicate", [*matrix[:-1], dict(matrix[0])]),
            ("swapped", [matrix[1], matrix[0], *matrix[2:]]),
            ("identity", [{**matrix[0], "id": "foreign:0000"}, *matrix[1:]]),
            ("seed", [{**matrix[0], "seed": "0" * 64}, *matrix[1:]]),
            ("cohort", [{**matrix[0], "cohort": "foreign"}, *matrix[1:]]),
        ):
            reject("reject-altered-original-public-case-matrix/" + label,
                   lambda value=invalid: validate_matrix(value))

        reserved_surrogate = {
            "type": stage10.previous.SURROGATE_TAG,
            "encoding": "utf-8/surrogatepass", "hex": "eda080",
        }
        reserved_mapping = {
            "type": stage10.previous.SURROGATE_MAPPING_TAG,
            "items": [["nested", reserved_surrogate]],
        }
        codec_samples = {
            "literal-high-surrogate": {"value": "\ud800"},
            "literal-low-surrogate": {"value": "\udfff"},
            "astral-character": {"value": "\U0001d11e"},
            "surrogate-key": {"\ud800": "real-surrogate-key"},
            "genuine-existing-surrogate-envelope": reserved_surrogate,
            "genuine-existing-mapping-envelope": reserved_mapping,
            "nested-surrogate-and-envelopes": {
                "values": ["\ud800", reserved_surrogate, reserved_mapping,
                           {"deep": "\udfff"}],
            },
        }
        check("freeze-the-exact-plain-json-encoder-and-sha256",
              _FROZEN_JSON_DUMPS is json.dumps
              and _FROZEN_JSON_LOADS is json.loads
              and _FROZEN_SHA256 is hashlib.sha256)
        for label, item in codec_samples.items():
            parsed, payload = _durable_round_trip(item)
            check("round-trip-actual-serialized-unicode/" + label,
                  parsed == item and canonical(parsed) == payload)
            check("hash-the-exact-parsed-durable-json-once/" + label,
                  digest(parsed) == _FROZEN_SHA256(payload).hexdigest())
        for label in (
            "genuine-existing-surrogate-envelope",
            "genuine-existing-mapping-envelope",
            "nested-surrogate-and-envelopes",
        ):
            item = codec_samples[label]
            check("reject-twice-applied-portable-canonicalization/" + label,
                  canonical(item) != previous.canonical(item)
                  and digest(item) != previous.digest(item)
                  and _durable_round_trip(item)[0] == item)
        check("retain-exact-genuine-plain-transport-v15-digest",
              V15_DECLARED_RECORD_SHA256
              == "0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94")
        check("retain-exact-genuine-portable-validator-v15-digest",
              V15_PORTABLE_RECORD_SHA256
              == "7a3bed83093800085fe1bd084820108142929f60e37632b3c24a02c6a4584d72"
              and V15_PORTABLE_RECORD_SHA256 != V15_DECLARED_RECORD_SHA256)
        check("retain-only-the-byte-exact-falsified-first-v15-reference",
              V15_RAW_REFERENCE_SHA256
              == "755cb818f59259bb5adb05a93782afc3eef12e001c41a976ba4b9258ae54ac01")
        check("retain-only-the-actually-frozen-failed-v15-source",
              V15_SOURCE_SHA256
              == "fc288f0771462a850d5ac4859ba05fe3731953e7160419ddcdbf98e8563ac580")

        provenance, reference, all_report = _synthetic_full()
        check("validate-both-complete-parsed-python-worker-streams",
              _validate_complete_reference(reference, provenance) is reference)
        check("validate-all-10752-real-shape-independent-native-rows",
              _validate_complete_all(
                  all_report, reference=reference, provenance=provenance,
              ) is all_report)
        check("preserve-two-distinct-actual-python-worker-record-streams",
              len(reference["reference_worker_reports"]) == 2
              and reference["baseline_records"]
              is not reference["second_records"]
              and len(reference["baseline_records"])
              + len(reference["second_records"]) == 7_168)
        check("detect-the-authentic-surrogate-double-encoding-on-full-rows",
              previous.digest(reference["baseline_records"])
              != reference["baseline_record_sha256"])
        parsed_reference, reference_payload = _durable_round_trip(reference)
        parsed_all, all_payload = _durable_round_trip(all_report)
        check("validate-the-full-reference-as-actual-persisted-json",
              parsed_reference == reference
              and canonical(parsed_reference) == reference_payload
              and _validate_complete_reference(
                  parsed_reference, provenance,
              ) is parsed_reference)
        check("validate-the-full-native-result-as-actual-persisted-json",
              parsed_all == all_report
              and canonical(parsed_all) == all_payload
              and _validate_complete_all(
                  parsed_all, reference=parsed_reference,
                  provenance=provenance,
              ) is parsed_all)
        for field, poison in (
            ("schema", previous.SELF_ORACLE_SCHEMA),
            ("status", "FAIL"), ("result", "FAIL"),
            ("source_path", V15_SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("protocol_path", V15_PROTOCOL_RELATIVE),
            ("protocol_sha256", "0" * 64),
            ("seed", previous.SEED),
            ("seed_domain", previous.SEED_DOMAIN),
            ("matrix_sha256", previous.MATRIX_SHA256),
            ("cases", EXPECTED_CASES - 1),
            ("stdlib_checks", EXPECTED_CASES * 2 - 1),
            ("baseline_records", reference["baseline_records"][:-1]),
            ("second_records", reference["second_records"][:-1]),
            ("baseline_record_sha256",
             previous.digest(reference["baseline_records"])),
            ("second_record_sha256",
             previous.digest(reference["second_records"])),
            ("reference_worker_reports", {}),
            ("mismatches", 1),
            ("failure_records", [{"id": "fabricated"}]),
            ("current_provenance", {"foreign": True}),
            ("candidate_imports", 1),
            ("candidate_processes", 1),
            ("benchmark_or_timing_executed", True),
            ("holdout_cases_read", 1),
        ):
            reject(
                "reject-fabricated-durable-two-reference-proof/" + field,
                lambda key=field, value=poison: (
                    _validate_complete_reference(
                        {**reference, key: value}, provenance,
                    )
                ),
            )
        for role in ("stdlib-a", "stdlib-b"):
            actual = reference["reference_worker_reports"][role]
            for field, poison in (
                ("schema", previous.SCHEMA + "-worker"),
                ("role", "foreign"),
                ("records", actual["records"][:-1]),
                ("record_sha256", previous.digest(actual["records"])),
                ("guard", {"baseline_only": False}),
                ("native_binary_sha256", {"foreign": "0" * 64}),
            ):
                reject(
                    "reject-nondurable-isolated-python-worker/"
                    + role + "/" + field,
                    lambda chosen=role, key=field, value=poison: (
                        _validate_complete_reference(
                            {**reference, "reference_worker_reports": {
                                **reference["reference_worker_reports"],
                                chosen: {
                                    **reference[
                                        "reference_worker_reports"
                                    ][chosen],
                                    key: value,
                                },
                            }},
                            provenance,
                        )
                    ),
                )
        for field, poison in (
            ("schema", previous.ALL_CANDIDATE_SCHEMA),
            ("cases_per_candidate", EXPECTED_CASES - 1),
            ("candidate_checks", EXPECTED_CASES * 3 - 1),
            ("selected_candidates", ["rust", "vm"]),
            ("completed_candidates", ["rust", "vm"]),
            ("comparison_complete", False),
            ("reference_worker_reports", {}),
            ("baseline_records", all_report["baseline_records"][:-1]),
            ("second_reference_records",
             all_report["second_reference_records"][:-1]),
            ("baseline_record_sha256",
             previous.digest(all_report["baseline_records"])),
            ("second_record_sha256",
             previous.digest(all_report["second_reference_records"])),
            ("self_oracle_sha256", "0" * 64),
            ("candidate_reports", {}),
            ("current_provenance", {"foreign": True}),
            ("candidate_cross_delegation", True),
            ("external_regex_packages", 1),
            ("holdout_cases_read", 1),
        ):
            reject(
                "reject-fabricated-durable-three-native-result/" + field,
                lambda key=field, value=poison: _validate_complete_all(
                    {**all_report, key: value},
                    reference=reference, provenance=provenance,
                ),
            )
        for role in REQUIRED_CANDIDATES:
            actual = all_report["candidate_reports"][role]
            for field, poison in (
                ("candidate", "foreign"),
                ("module", "candidates.foreign_candidate"),
                ("records", actual["records"][:-1]),
                ("record_sha256", previous.digest(actual["records"])),
                ("native_binary_sha256", {}),
                ("guard", {}), ("mismatches", 1),
            ):
                reject(
                    "reject-double-encoded-native-evidence/"
                    + role + "/" + field,
                    lambda chosen=role, key=field, value=poison: (
                        _validate_complete_all(
                            {**all_report, "candidate_reports": {
                                **all_report["candidate_reports"],
                                chosen: {
                                    **all_report["candidate_reports"][chosen],
                                    key: value,
                                },
                            }},
                            reference=reference, provenance=provenance,
                        )
                    ),
                )

        raw, failure_provenance, incident = _synthetic_failure_report()
        check("authenticate-a-truthful-preserved-falsified-v15-result",
              _validate_failure_report(
                  incident, raw=raw, provenance=failure_provenance,
              ) is incident)
        for field, poison in (
            ("schema", previous.SELF_ORACLE_SCHEMA),
            ("status", "PASS"),
            ("result", "PASS"),
            ("stage15_source_sha256", "0" * 64),
            ("stage15_protocol_sha256", "0" * 64),
            ("original_reference_sha256", "0" * 64),
            ("declared_record_sha256", V15_PORTABLE_RECORD_SHA256),
            ("actual_record_sha256", V15_DECLARED_RECORD_SHA256),
            ("durable_transport_record_sha256", V15_PORTABLE_RECORD_SHA256),
            ("frozen_validator_record_sha256", V15_DECLARED_RECORD_SHA256),
            ("declared_digest_count", 3),
            ("actual_reference_record_count", EXPECTED_CASES * 2 - 1),
            ("candidate_imports", 1),
            ("candidate_processes", 1),
            ("candidate_reports_created", 1),
            ("validator_rejections", incident["validator_rejections"][:1]),
            ("original_reference_document", {"fabricated": True}),
            ("current_provenance", {"fabricated": True}),
        ):
            reject(
                "reject-concealed-genuine-v15-failure/" + field,
                lambda key=field, value=poison: _validate_failure_report(
                    {**incident, key: value},
                    raw=raw, provenance=failure_provenance,
                ),
            )

        names = (
            "V15_FAILURE_SOURCE_SHA256",
            "V15_FAILURE_PROTOCOL_SHA256",
            "V15_FAILURE_SHA256",
        )
        actual_pins = {name: globals()[name] for name in names}

        def synthetic_failure_pins(values: dict[str, Any]) -> None:
            old = {name: globals()[name] for name in names}
            try:
                for name in names:
                    globals()[name] = values[name]
                _require_published_failure()
            finally:
                for name, value in old.items():
                    globals()[name] = value

        valid = {
            name: format(index, "064x")
            for index, name in enumerate(names, start=1)
        }
        check("accept-only-three-distinct-published-real-failure-hashes",
              synthetic_failure_pins(valid) is None)
        for name in names:
            for label, poison in (
                ("unpublished", None),
                ("malformed", "not-a-sha256"),
                ("truncated", "0" * 63),
            ):
                reject(
                    "fail-before-workers-on-an-unpublished-real-incident/"
                    + name.lower() + "/" + label,
                    lambda key=name, value=poison: (
                        synthetic_failure_pins({**valid, key: value})
                    ),
                )
        reject(
            "reject-an-incident-source-reused-as-evidence",
            lambda: synthetic_failure_pins({
                **valid,
                "V15_FAILURE_SHA256": valid["V15_FAILURE_SOURCE_SHA256"],
            }),
        )
        if all(
            isinstance(value, str) and official_locale.is_sha256(value)
            for value in actual_pins.values()
        ):
            check("authenticate-all-three-actually-published-failure-proofs",
                  _require_published_failure() is None)
        else:
            reject("fail-closed-until-the-genuine-failure-report-is-published",
                   _require_published_failure)

        original_source = stage07.SOURCE_RELATIVE
        original_codec = stage07.canonical
        original_digest = stage07.digest
        original_validator = stage07._validate_worker_report
        with _stage17_context():
            check("bind-stage07-and-stage10-to-one-immutable-json-transport",
                  stage07.SOURCE_RELATIVE == SOURCE_RELATIVE
                  and stage07.SEED == SEED
                  and stage07.MATRIX_SHA256 == MATRIX_SHA256
                  and stage07.canonical is canonical
                  and stage07.digest is digest
                  and stage10.canonical is canonical
                  and stage10.digest is digest)
            check("reject-the-old-surrogate-restoring-worker-validator",
                  stage07._validate_worker_report
                  is stage10.previous._FROZEN_VALIDATE_WORKER_REPORT)
            for role in ("stdlib-a", "stdlib-b"):
                worker = parsed_reference["reference_worker_reports"][role]
                check(
                    "validate-an-actual-shape-plain-transport-worker/" + role,
                    stage07._validate_worker_report(
                        worker,
                        role=role,
                        source_sha256=provenance["source_sha256"],
                    ) is worker,
                )
            for role in REQUIRED_CANDIDATES:
                metadata, _module = stage10._synthetic_metadata(
                    matrix,
                    role=role,
                    source_sha256=provenance["source_sha256"],
                )
                validated_metadata = stage10._validate_metadata_report(
                    metadata,
                    role=role,
                    source_sha256=provenance["source_sha256"],
                )
                check(
                    "validate-all-256-genuine-shape-isolated-signatures/" + role,
                    len(validated_metadata["records"]) == 256
                    and validated_metadata["record_sha256"]
                    == digest(validated_metadata["records"]),
                )
            check("validate-durable-full-reference-inside-worker-context",
                  _validate_complete_reference(
                      parsed_reference, provenance,
                  ) is parsed_reference)
            check("validate-durable-full-candidates-inside-worker-context",
                  _validate_complete_all(
                      parsed_all, reference=parsed_reference,
                      provenance=provenance,
                  ) is parsed_all)
            check("retain-byte-identical-reference-inside-worker-context",
                  canonical(parsed_reference) == reference_payload
                  and digest(parsed_reference)
                  == _FROZEN_SHA256(reference_payload).hexdigest())
        check("restore-all-immutable-original-worker-globals",
              stage07.SOURCE_RELATIVE == original_source
              and stage07.canonical is original_codec
              and stage07.digest is original_digest
              and stage07._validate_worker_report is original_validator)
        check("validate-full-reference-again-after-worker-context-exits",
              _validate_complete_reference(
                  parsed_reference, provenance,
              ) is parsed_reference)
        check("validate-full-native-evidence-after-worker-context-exits",
              _validate_complete_all(
                  parsed_all, reference=parsed_reference,
                  provenance=provenance,
              ) is parsed_all)
        check("preserve-true-independent-isolated-metadata-and-matcher-entry",
              METADATA_WORKER_BOOTSTRAP != WORKER_BOOTSTRAP
              and "_metadata_worker_entry" in METADATA_WORKER_BOOTSTRAP
              and "_worker_entry" in WORKER_BOOTSTRAP)
        check("deny-all-five-genuine-foreign-native-library-loader-aliases",
              tuple(stage07.NATIVE_LOADER_ALIASES) == NATIVE_LOADER_ALIASES)
        check("authorize-six-fresh-one-use-durable-report-paths",
              len(APPROVED_OUTPUTS) == len(set(APPROVED_OUTPUTS)) == 6
              and not set(APPROVED_OUTPUTS).intersection(
                  set(previous.APPROVED_OUTPUTS)
                  | {V15_RAW_REFERENCE_RELATIVE, V15_FAILURE_RELATIVE}
              ))
        for output in APPROVED_OUTPUTS:
            label = Path(output).name
            check("accept-only-exact-durable-evidence-path/" + label,
                  stage07.exact_output(output, output) == output)
            for kind, invalid in (
                ("absolute", "/" + output),
                ("traversal", "../" + output),
                ("double-separator", output.replace("/", "//", 1)),
                ("nul", output + "\x00"),
                ("foreign-version", previous.SELF_ORACLE_RELATIVE),
            ):
                reject(
                    "reject-foreign-durable-evidence-path/" + label + "/" + kind,
                    lambda value=invalid, expected=output: (
                        stage07.exact_output(value, expected)
                    ),
                )
        check("never-start-a-reference-candidate-or-metadata-worker",
              effects["workers"] == 0)
        check("never-read-write-time-or-access-randomness",
              all(value == 0 for value in effects.values()))
        frozen.candidate_free()
        check("never-import-a-real-native-candidate", True)
        check_names = [item["name"] for item in checks]
        frozen.require(
            len(check_names) == len(set(check_names))
            and len(checks) >= 120,
            "a decisive durable-transport control was duplicated or omitted",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "stage": "stage17",
            "status": "PASS", "result": "PASS",
            "seed": SEED, "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cohorts": 8, "cohort_cases": _cohort_cases(),
            "cases": EXPECTED_CASES,
            "check_count": len(checks), "checks": checks,
            "failed": [],
            "inherited_stage10_control_count": inherited["check_count"],
            "inherited_v7_control_count": native["check_count"],
            "inherited_official_v3_control_count": official["check_count"],
            "candidate_imports": 0, "candidate_processes": 0,
            "metadata_processes": 0,
            "files_read": 0, "files_written": 0,
            "clock_samples": 0, "entropy_drawn": False,
            "self_oracle_executed": False,
            "production_evidence_written": False,
            "stage15_reference_status": "FALSIFIED",
            "stage15_declared_record_sha256": V15_DECLARED_RECORD_SHA256,
            "stage15_durable_transport_record_sha256": (
                V15_DECLARED_RECORD_SHA256
            ),
            "stage15_frozen_validator_record_sha256": (
                V15_PORTABLE_RECORD_SHA256
            ),
            "stage15_raw_reference_sha256": V15_RAW_REFERENCE_SHA256,
            "stage15_failure_source_pinned": (
                V15_FAILURE_SOURCE_SHA256 is not None
            ),
            "stage15_failure_protocol_pinned": (
                V15_FAILURE_PROTOCOL_SHA256 is not None
            ),
            "stage15_failure_report_pinned": V15_FAILURE_SHA256 is not None,
            "complete_reference_records_required": EXPECTED_CASES * 2,
            "complete_reference_worker_reports_required": 2,
            "complete_candidate_records_required": (
                EXPECTED_CASES * len(REQUIRED_CANDIDATES)
            ),
            "parsed_json_round_trip_validated": True,
            "outside_worker_context_validated": True,
            "isolated_surface_cases_per_candidate": 256,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
            "self_oracle_output": SELF_ORACLE_RELATIVE,
            "self_oracle_failure_output": SELF_ORACLE_FAILURE_RELATIVE,
            "all_candidate_output": ALL_CANDIDATE_RELATIVE,
            "candidate_failure_outputs": dict(CANDIDATE_FAILURE_RELATIVES),
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--candidate", choices=("all",))
    arguments = parser.parse_args(argv)
    try:
        if arguments.self_test:
            report = self_test()
        elif arguments.self_oracle:
            report = run_self_oracle()
        else:
            frozen.require(arguments.candidate == "all",
                           "all three genuinely owned native families are required")
            report = run_all_candidates()
        sys.stdout.buffer.write(canonical(report) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (
        frozen.OracleIntegrityError,
        AssertionError, AttributeError, ImportError,
        KeyError, OSError, TypeError, UnicodeError, ValueError,
        stage07.subprocess.SubprocessError,
    ) as error:
        sys.stderr.buffer.write(
            canonical({"schema": SCHEMA, "status": "FAIL", "error": str(error)})
            + b"\n",
        )
        sys.stderr.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
