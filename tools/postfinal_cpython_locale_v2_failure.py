#!/usr/bin/env python3
"""Exclusively preserve the actual first failed V2 official Rust test."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v2 as official


SCHEMA = "rebar-postfinal-cpython-public-locale-v2-rust-failure-v1"
SOURCE_RELATIVE = "tools/postfinal_cpython_locale_v2_failure.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2-FAILURE.md"
REPORT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json"
)
REPORT_PATH = ROOT / REPORT_RELATIVE
MAX_CAPTURE_BYTES = 16 * 1024

OFFICIAL_SOURCE_SHA256 = (
    "e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1"
)
OFFICIAL_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md"
OFFICIAL_PROTOCOL_SHA256 = (
    "a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5"
)
STAGE12_SOURCE_RELATIVE = "tools/python_re_generic_alias_public_oracle_stage12.py"
STAGE12_SOURCE_SHA256 = (
    "361e080a0475f5ee7fd7d5da0386a4e2443775069aadca84e053bac357554aaa"
)
STAGE12_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V12.md"
STAGE12_PROTOCOL_SHA256 = (
    "1cec5253aabb5464c16d0de461bdd11463ddf11fafea9da6347b8a0af3d30cb1"
)
STAGE12_SELF_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle.json"
)
STAGE12_SELF_SHA256 = (
    "b235bd68afbbfa9b8e7e046d0e007385617c976c6e5a5f5b614cc7d93b891aff"
)
STAGE12_ALL_RELATIVE = (
    "candidates/evidence/python-re-generic-alias-public-oracle-v12-all.json"
)
STAGE12_ALL_SHA256 = (
    "6b0188e22f80a64e79252660d6b308d16d7a38ec01c45013bf67484b8d49be8c"
)
STAGE12_MATRIX_SHA256 = (
    "65c93cfbbc337ecd762a6b201bacc77e35eb72d201a9e8bc222d730714885aef"
)

FAILED_ROLE = "rust"
FAILED_MODULE = "candidates.rust_candidate"
FAILED_METHOD = "ReTests.test_match_repr"
EXPECTED_MATCH_REGEX = (
    r"<(candidates._rust_bridge\.)?Match object; "
    r"span=\(1, 12\), match='abracadabra'>"
)
OBSERVED_MATCH_REPR = "<re.Match object; span=(1, 12), match='abracadabra'>"
RUST_RUNNER_SUMMARY: dict[str, Any] = {
    "crashes": 0,
    "failed": 1,
    "methods": 146,
    "module": FAILED_MODULE,
    "passed": 145,
    "runner_sha256": (
        "d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb"
    ),
    "schema": "rebar-cpython-re-result-v1",
    "skipped": 0,
    "source_sha256": {
        "LICENSE": (
            "b0e25a78cffb43f4d92de8b61ccfa1f1f98ecbc22330b54b5251e7b6ba010231"
        ),
        "re_tests.py": (
            "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab"
        ),
        "test_re.py": (
            "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
        ),
    },
    "timeouts": 0,
}

# Faithful transcription of the already observed controller-emitted JSON.
# It is never represented as captured original stdout or stderr bytes.
TRANSCRIBED_CONTROLLER_FAILURE = (
    r'''{"error": "original CPython oracle rejected rust: ReTests.test_match_repr: AssertionError: Regex didn't match: \"<(candidates._rust_bridge\\\\.)?Match object; span=\\\\(1, 12\\\\), match='abracadabra'>\" not found in \"<re.Match object; span=(1, 12), match='abracadabra'>\"\n {\"crashes\": 0, \"failed\": 1, \"methods\": 146, \"module\": \"candidates.rust_candidate\", \"passed\": 145, \"runner_sha256\": \"d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb\", \"schema\": \"rebar-cpython-re-result-v1\", \"skipped\": 0, \"source_sha256\": {\"LICENSE\": \"b0e25a78cffb43f4d92de8b61ccfa1f1f98ecbc22330b54b5251e7b6ba010231\", \"re_tests.py\": \"ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab\", \"test_re.py\": \"879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2\"}, \"timeouts\": 0}\n", "schema": "rebar-postfinal-cpython-public-locale-v2", "status": "FAIL"}'''
)


class FailureRecorderError(AssertionError):
    """A real first official failure was omitted, forged, or misrepresented."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise FailureRecorderError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, allow_nan=False,
        separators=(",", ":"),
    ).encode("ascii")


def destination(value: Any) -> str:
    require(type(value) is str, "the one-use failure destination must be text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value == REPORT_RELATIVE,
        "only the exact, new, exclusive official Rust failure path is authorized",
    )
    return value


def validate_capture(value: Any) -> dict[str, Any]:
    require(type(value) is str, "the observed controller JSON must be text")
    try:
        encoded = value.encode("ascii")
    except UnicodeError as error:
        raise FailureRecorderError("the observed failure is not ASCII") from error
    require(0 < len(encoded) <= MAX_CAPTURE_BYTES,
            "the original observed failure exceeds its safety bound")
    try:
        captured = json.loads(value)
    except (ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise FailureRecorderError("the transcribed failure is invalid JSON") from error
    require(
        isinstance(captured, dict)
        and set(captured) == {"error", "schema", "status"}
        and captured.get("schema") == official.SCHEMA
        and captured.get("status") == "FAIL",
        "the supplied JSON is not the genuinely failed frozen official controller",
    )
    escaped = EXPECTED_MATCH_REGEX.replace("\\", "\\\\")
    prefix = (
        "original CPython oracle rejected rust: "
        "ReTests.test_match_repr: AssertionError: Regex didn't match: "
        f'"{escaped}" not found in "{OBSERVED_MATCH_REPR}"\n '
    )
    expected = prefix + json.dumps(
        RUST_RUNNER_SUMMARY, sort_keys=True, ensure_ascii=True,
    ) + "\n"
    require(captured.get("error") == expected,
            "the observed method, mismatch, or 145/146 Rust result was altered")
    return {
        "capture": "faithfully transcribed controller-emitted JSON",
        "raw_stream_bytes": "NOT RECORDED",
        "raw_stream_sha256": "NOT RECORDED",
        "controller_output": captured,
        "normalized_transcription_sha256": (
            hashlib.sha256(canonical(captured)).hexdigest()
        ),
        "failed_role": FAILED_ROLE,
        "failed_module": FAILED_MODULE,
        "failed_method": FAILED_METHOD,
        "exception_type": "AssertionError",
        "expected_match_regex": EXPECTED_MATCH_REGEX,
        "actual_match_repr": OBSERVED_MATCH_REPR,
        "runner_summary": copy.deepcopy(RUST_RUNNER_SUMMARY),
        "original_method_records_preserved": False,
        "failure_rerun": False,
    }


def validate_stage12(reference: Any, candidates: Any) -> dict[str, Any]:
    require(isinstance(reference, dict) and isinstance(candidates, dict),
            "both actual stage-twelve correctness reports are required")
    require(
        reference.get("schema")
        == "rebar-python-re-public-generic-alias-v12-self-oracle"
        and reference.get("status") == "PASS"
        and reference.get("result") == "PASS"
        and reference.get("source_path") == STAGE12_SOURCE_RELATIVE
        and reference.get("source_sha256") == STAGE12_SOURCE_SHA256
        and reference.get("protocol_path") == STAGE12_PROTOCOL_RELATIVE
        and reference.get("protocol_sha256") == STAGE12_PROTOCOL_SHA256
        and reference.get("matrix_sha256") == STAGE12_MATRIX_SHA256
        and reference.get("cohorts") == 4
        and reference.get("cases") == 128
        and reference.get("stdlib_checks") == 256
        and reference.get("mismatches") == 0
        and reference.get("candidate_imports") == 0
        and reference.get("candidate_processes") == 0
        and reference.get("holdout_cases_read") == 0
        and reference.get("performance_fixtures_read") == 0
        and reference.get("benchmark_or_timing_executed") is False,
        "the actual source-bound, two-reference stage-twelve result changed",
    )
    require(
        candidates.get("schema")
        == "rebar-python-re-public-generic-alias-v12-all-candidates"
        and candidates.get("status") == "PASS"
        and candidates.get("result") == "PASS"
        and candidates.get("source_path") == STAGE12_SOURCE_RELATIVE
        and candidates.get("source_sha256") == STAGE12_SOURCE_SHA256
        and candidates.get("protocol_path") == STAGE12_PROTOCOL_RELATIVE
        and candidates.get("protocol_sha256") == STAGE12_PROTOCOL_SHA256
        and candidates.get("matrix_sha256") == STAGE12_MATRIX_SHA256
        and candidates.get("self_oracle_path") == STAGE12_SELF_RELATIVE
        and candidates.get("self_oracle_sha256") == STAGE12_SELF_SHA256
        and candidates.get("cohorts") == 4
        and candidates.get("cases_per_candidate") == 128
        and candidates.get("candidate_checks") == 384
        and candidates.get("completed_candidates") == list(official.CORE_FAMILIES)
        and candidates.get("comparison_complete") is True
        and candidates.get("holdout_cases_read") == 0
        and candidates.get("performance_fixtures_read") == 0
        and candidates.get("benchmark_or_timing_executed") is False,
        "the real passing 384-observation, all-candidate result changed",
    )
    provenance = reference.get("current_provenance")
    require(isinstance(provenance, dict)
            and provenance == candidates.get("current_provenance"),
            "the actual stage-twelve reference and engines use different proofs")
    for name, expected in (
        ("source_path", STAGE12_SOURCE_RELATIVE),
        ("source_sha256", STAGE12_SOURCE_SHA256),
        ("protocol_path", STAGE12_PROTOCOL_RELATIVE),
        ("protocol_sha256", STAGE12_PROTOCOL_SHA256),
        ("matrix_sha256", STAGE12_MATRIX_SHA256),
        ("base_audit_source_path", official.V6_BASE_SOURCE_RELATIVE),
        ("base_audit_source_sha256", official.V6_BASE_SOURCE_SHA256),
        ("base_audit_path", official.V6_BASE_REPORT_RELATIVE),
        ("base_audit_sha256", official.V6_BASE_REPORT_SHA256),
        ("strict_audit_source_path", official.V6_STRICT_SOURCE_RELATIVE),
        ("strict_audit_source_sha256", official.V6_STRICT_SOURCE_SHA256),
        ("strict_audit_path", official.V6_STRICT_REPORT_RELATIVE),
        ("strict_audit_sha256", official.V6_STRICT_REPORT_SHA256),
        ("native_source_count", 12),
        ("native_binary_count", 5),
    ):
        require(provenance.get(name) == expected,
                "an exact stage-twelve provenance field was changed: " + name)
    reports = candidates.get("candidate_reports")
    require(isinstance(reports, dict)
            and set(reports) == set(official.CORE_FAMILIES),
            "a passing stage-twelve engine was omitted")
    for family in official.CORE_FAMILIES:
        item = reports[family]
        require(isinstance(item, dict)
                and item.get("status") == "PASS"
                and item.get("cases") == 128
                and item.get("mismatches") == 0
                and item.get("holdout_cases_read") == 0
                and item.get("benchmark_or_timing_executed") is False,
                "the actual stage-twelve engine proof was forged: " + family)
    return {
        "source_path": STAGE12_SOURCE_RELATIVE,
        "source_sha256": STAGE12_SOURCE_SHA256,
        "protocol_path": STAGE12_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE12_PROTOCOL_SHA256,
        "matrix_sha256": STAGE12_MATRIX_SHA256,
        "self_oracle_path": STAGE12_SELF_RELATIVE,
        "self_oracle_sha256": STAGE12_SELF_SHA256,
        "all_candidates_path": STAGE12_ALL_RELATIVE,
        "all_candidates_sha256": STAGE12_ALL_SHA256,
        "cohorts": 4,
        "cases": 128,
        "stdlib_checks": 256,
        "candidate_checks": 384,
        "completed_candidates": list(official.CORE_FAMILIES),
    }


def read_bound(relative: str, expected: str) -> dict[str, Any]:
    path = official.previous.checked_repo_path(relative)
    require(official.previous.sha256_path(path) == expected,
            "a preserved real report was changed: " + relative)
    return official.previous.read_json(path)


def authenticate_provenance() -> dict[str, Any]:
    official.previous.verify_runtime()
    require(not official._candidate_modules(),
            "failure authentication cannot load a candidate")
    for relative, expected in (
        (official.SOURCE_RELATIVE, OFFICIAL_SOURCE_SHA256),
        (OFFICIAL_PROTOCOL_RELATIVE, OFFICIAL_PROTOCOL_SHA256),
        (STAGE12_SOURCE_RELATIVE, STAGE12_SOURCE_SHA256),
        (STAGE12_PROTOCOL_RELATIVE, STAGE12_PROTOCOL_SHA256),
    ):
        path = official.previous.checked_repo_path(relative)
        require(official.previous.sha256_path(path) == expected,
                "an immutable frozen controller or protocol changed: " + relative)
    require(
        official.previous.ORIGINAL_RUNNER_SHA256
        == RUST_RUNNER_SUMMARY["runner_sha256"]
        and official.previous.SOURCE_HASHES == RUST_RUNNER_SUMMARY["source_sha256"],
        "the captured real failure used a different official upstream runner",
    )
    pins = official._pin_values()
    for relative, expected in (
        (official.V6_BASE_SOURCE_RELATIVE, pins["base_source"]),
        (official.V6_STRICT_SOURCE_RELATIVE, pins["strict_source"]),
    ):
        path = official.previous.checked_repo_path(relative)
        require(official.previous.sha256_path(path) == expected,
                "a genuine current V6 source controller was substituted")
    base = read_bound(official.V6_BASE_REPORT_RELATIVE, pins["base_report"])
    strict = read_bound(official.V6_STRICT_REPORT_RELATIVE, pins["strict_report"])
    sources, natives = official.validate_v6_audits(
        base, strict,
        source_relative=official.V6_BASE_REPORT_RELATIVE,
        strict_relative=official.V6_STRICT_REPORT_RELATIVE,
        source_digest=pins["base_report"],
    )
    official.previous.verify_production_fingerprints(sources, natives)
    reference = read_bound(STAGE12_SELF_RELATIVE, STAGE12_SELF_SHA256)
    candidates = read_bound(STAGE12_ALL_RELATIVE, STAGE12_ALL_SHA256)
    stage12 = validate_stage12(reference, candidates)
    manifest = official.previous.checked_repo_path(
        official.previous.ORIGINAL_MANIFEST_PATH,
    )
    require(
        official.previous.sha256_path(manifest)
        == official.previous.ORIGINAL_MANIFEST_SHA256,
        "the unchanged official 146-method manifest was substituted",
    )
    official.previous.validate_manifest(official.previous.read_json(manifest))
    official._validate_historical_v1()
    require(not official._candidate_modules(),
            "an engine leaked into source-only failure authentication")
    return {
        "official_source_path": official.SOURCE_RELATIVE,
        "official_source_sha256": OFFICIAL_SOURCE_SHA256,
        "official_protocol_path": OFFICIAL_PROTOCOL_RELATIVE,
        "official_protocol_sha256": OFFICIAL_PROTOCOL_SHA256,
        "original_manifest_path": official.previous.ORIGINAL_MANIFEST_PATH,
        "original_manifest_sha256": official.previous.ORIGINAL_MANIFEST_SHA256,
        "original_runner_path": official.previous.ORIGINAL_RUNNER_PATH,
        "original_runner_sha256": official.previous.ORIGINAL_RUNNER_SHA256,
        "upstream_source_sha256": dict(official.previous.SOURCE_HASHES),
        "total_public_methods": 152,
        "selected_methods": 146,
        "corpus_cases": 403,
        "named_waiver_count": 8,
        "source_audit_source_path": official.V6_BASE_SOURCE_RELATIVE,
        "source_audit_source_sha256": pins["base_source"],
        "source_audit_report_path": official.V6_BASE_REPORT_RELATIVE,
        "source_audit_report_sha256": pins["base_report"],
        "strict_audit_source_path": official.V6_STRICT_SOURCE_RELATIVE,
        "strict_audit_source_sha256": pins["strict_source"],
        "strict_audit_report_path": official.V6_STRICT_REPORT_RELATIVE,
        "strict_audit_report_sha256": pins["strict_report"],
        "verified_owned_source_count": len(sources),
        "verified_native_binary_count": len(natives),
        "verified_standard_pickle_count": 48,
        "stage12": stage12,
    }


def build_report(
    capture: Mapping[str, Any], provenance: Mapping[str, Any],
    *, source_sha256: str, protocol_sha256: str,
) -> dict[str, Any]:
    require(official.previous.is_sha256(source_sha256)
            and official.previous.is_sha256(protocol_sha256),
            "the failure recorder and protocol require exact source hashes")
    return {
        "schema": SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "goal_sha256": official.previous.GOAL_SHA256,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha256,
        "failed_role": FAILED_ROLE,
        "failed_module": FAILED_MODULE,
        "failed_method": FAILED_METHOD,
        "official_v2_status": "FAIL",
        "official_v2_complete_result_path": official.REPORT_RELATIVE,
        "official_v2_complete_result_created": False,
        "first_run": {
            "controller": official.SOURCE_RELATIVE,
            "command": [
                str(official.previous.PINNED), "-I", "-B",
                official.SOURCE_RELATIVE, "--audit",
            ],
            "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
            "exit_code": 1,
            "rerun": False,
            "failure": dict(capture),
        },
        "roles": {
            "re": {
                "execution": "EXECUTED",
                "status": "NOT RECORDED",
                "individual_method_records_preserved": False,
                "inferred_pass": False,
            },
            "rust": {
                "execution": "EXECUTED",
                "status": "FAIL",
                "module": FAILED_MODULE,
                "methods": 146,
                "passed": 145,
                "failed": 1,
                "skipped": 0,
                "crashes": 0,
                "timeouts": 0,
                "failed_method": FAILED_METHOD,
                "individual_method_records_preserved": False,
                "runner_summary": copy.deepcopy(RUST_RUNNER_SUMMARY),
            },
            "vm": {
                "execution": "NOT RUN", "status": "NOT RUN",
                "individual_method_records_preserved": False,
                "inferred_pass": False,
            },
            "zig": {
                "execution": "NOT RUN", "status": "NOT RUN",
                "individual_method_records_preserved": False,
                "inferred_pass": False,
            },
        },
        "actual_current_provenance": dict(provenance),
        "scope": {
            "actual_first_failure_preserved": True,
            "raw_controller_stream_recorded": False,
            "controller_output_semantically_transcribed": True,
            "failure_reproduced_or_rerun": False,
            "candidate_imports": 0,
            "candidate_processes": 0,
            "official_test_processes_started": 0,
            "locale_compilations": 0,
            "baseline_method_records_fabricated": False,
            "unexecuted_candidate_results_invented": False,
            "performance_fixture_access": False,
            "holdout_access": False,
            "benchmark_or_timing_executed": False,
            "production_output_path": REPORT_RELATIVE,
        },
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }


def validate_report(report: Any) -> dict[str, Any]:
    require(isinstance(report, dict), "the recorded first failure must be an object")
    require(
        report.get("schema") == SCHEMA
        and report.get("status") == "FAIL"
        and report.get("result") == "FAIL"
        and report.get("python") == "3.14.6"
        and report.get("goal_sha256") == official.previous.GOAL_SHA256
        and report.get("source_path") == SOURCE_RELATIVE
        and official.previous.is_sha256(report.get("source_sha256"))
        and report.get("protocol_path") == PROTOCOL_RELATIVE
        and official.previous.is_sha256(report.get("protocol_sha256"))
        and report.get("failed_role") == FAILED_ROLE
        and report.get("failed_module") == FAILED_MODULE
        and report.get("failed_method") == FAILED_METHOD
        and report.get("official_v2_status") == "FAIL"
        and report.get("official_v2_complete_result_path") == official.REPORT_RELATIVE
        and report.get("official_v2_complete_result_created") is False,
        "the genuine first official Rust failure was hidden or rewritten",
    )
    first = report.get("first_run")
    require(
        isinstance(first, dict)
        and first.get("controller") == official.SOURCE_RELATIVE
        and first.get("command") == [
            str(official.previous.PINNED), "-I", "-B",
            official.SOURCE_RELATIVE, "--audit",
        ]
        and first.get("environment") == {"PYTHONDONTWRITEBYTECODE": "1"}
        and first.get("exit_code") == 1
        and first.get("rerun") is False
        and first.get("failure") == validate_capture(TRANSCRIBED_CONTROLLER_FAILURE),
        "the real first-run command or semantically transcribed error was changed",
    )
    roles = report.get("roles")
    require(isinstance(roles, dict) and set(roles) == {"re", "rust", "vm", "zig"},
            "an actual official role was omitted or fabricated")
    baseline = roles["re"]
    require(
        isinstance(baseline, dict)
        and baseline.get("execution") == "EXECUTED"
        and baseline.get("status") == "NOT RECORDED"
        and baseline.get("individual_method_records_preserved") is False
        and baseline.get("inferred_pass") is False,
        "the unpreserved original Python baseline was fabricated",
    )
    rust = roles["rust"]
    require(
        isinstance(rust, dict)
        and rust.get("execution") == "EXECUTED"
        and rust.get("status") == "FAIL"
        and rust.get("module") == FAILED_MODULE
        and rust.get("methods") == 146
        and rust.get("passed") == 145
        and rust.get("failed") == 1
        and rust.get("skipped") == 0
        and rust.get("crashes") == 0
        and rust.get("timeouts") == 0
        and rust.get("failed_method") == FAILED_METHOD
        and rust.get("individual_method_records_preserved") is False
        and rust.get("runner_summary") == RUST_RUNNER_SUMMARY,
        "the real 145/146 first Rust official failure changed",
    )
    for family in ("vm", "zig"):
        role = roles[family]
        require(
            isinstance(role, dict)
            and role.get("execution") == "NOT RUN"
            and role.get("status") == "NOT RUN"
            and role.get("individual_method_records_preserved") is False
            and role.get("inferred_pass") is False,
            "an official result was invented for unrun candidate " + family,
        )
    scope = report.get("scope")
    require(isinstance(scope, dict), "the failure preservation scope is missing")
    for name, expected in (
        ("actual_first_failure_preserved", True),
        ("raw_controller_stream_recorded", False),
        ("controller_output_semantically_transcribed", True),
        ("failure_reproduced_or_rerun", False),
        ("candidate_imports", 0),
        ("candidate_processes", 0),
        ("official_test_processes_started", 0),
        ("locale_compilations", 0),
        ("baseline_method_records_fabricated", False),
        ("unexecuted_candidate_results_invented", False),
        ("performance_fixture_access", False),
        ("holdout_access", False),
        ("benchmark_or_timing_executed", False),
        ("production_output_path", REPORT_RELATIVE),
    ):
        require(scope.get(name) == expected,
                "the read-only failure preservation scope changed: " + name)
    require(report.get("holdout_accessed") is False
            and report.get("timing_performed") is False
            and report.get("performance") == "NOT MEASURED",
            "correctness failure recording cannot imply a performance result")
    return report


def write_exclusive(report: Mapping[str, Any]) -> None:
    destination(REPORT_RELATIVE)
    parent = REPORT_PATH.parent
    require(parent.is_dir() and not parent.is_symlink(),
            "the exact failure-evidence parent is not safe")
    require(not REPORT_PATH.is_symlink(),
            "the exclusive failure output cannot be a symbolic link")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(REPORT_PATH, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            output.write(canonical(report) + b"\n")
            output.flush()
            os.fsync(output.fileno())
        directory = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def record_failure() -> dict[str, Any]:
    official.previous.verify_runtime()
    require(not official._candidate_modules(),
            "recording a past failure must not import a real candidate")
    destination(REPORT_RELATIVE)
    require(not REPORT_PATH.exists() and not REPORT_PATH.is_symlink(),
            "the actual first Rust failure was already exclusively recorded")
    require(not official.EVIDENCE_PATH.exists()
            and not official.EVIDENCE_PATH.is_symlink(),
            "the failed official V2 gate unexpectedly has a passing report")
    captured = validate_capture(TRANSCRIBED_CONTROLLER_FAILURE)
    provenance = authenticate_provenance()
    source = official.previous.checked_repo_path(SOURCE_RELATIVE)
    protocol = official.previous.checked_repo_path(PROTOCOL_RELATIVE)
    report = build_report(
        captured, provenance,
        source_sha256=official.previous.sha256_path(source),
        protocol_sha256=official.previous.sha256_path(protocol),
    )
    validate_report(report)
    require(not official._candidate_modules(),
            "a candidate leaked into the no-worker failure recorder")
    write_exclusive(report)
    return report


def synthetic_stage12() -> tuple[dict[str, Any], dict[str, Any]]:
    provenance: dict[str, Any] = {
        "source_path": STAGE12_SOURCE_RELATIVE,
        "source_sha256": STAGE12_SOURCE_SHA256,
        "protocol_path": STAGE12_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE12_PROTOCOL_SHA256,
        "matrix_sha256": STAGE12_MATRIX_SHA256,
        "base_audit_source_path": official.V6_BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": official.V6_BASE_SOURCE_SHA256,
        "base_audit_path": official.V6_BASE_REPORT_RELATIVE,
        "base_audit_sha256": official.V6_BASE_REPORT_SHA256,
        "strict_audit_source_path": official.V6_STRICT_SOURCE_RELATIVE,
        "strict_audit_source_sha256": official.V6_STRICT_SOURCE_SHA256,
        "strict_audit_path": official.V6_STRICT_REPORT_RELATIVE,
        "strict_audit_sha256": official.V6_STRICT_REPORT_SHA256,
        "native_source_count": 12,
        "native_binary_count": 5,
    }
    common: dict[str, Any] = {
        "status": "PASS", "result": "PASS",
        "source_path": STAGE12_SOURCE_RELATIVE,
        "source_sha256": STAGE12_SOURCE_SHA256,
        "protocol_path": STAGE12_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE12_PROTOCOL_SHA256,
        "matrix_sha256": STAGE12_MATRIX_SHA256,
        "cohorts": 4,
        "current_provenance": provenance,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
    }
    baseline = {
        **copy.deepcopy(common),
        "schema": "rebar-python-re-public-generic-alias-v12-self-oracle",
        "cases": 128, "stdlib_checks": 256, "mismatches": 0,
        "candidate_imports": 0, "candidate_processes": 0,
    }
    candidates = {
        **copy.deepcopy(common),
        "schema": "rebar-python-re-public-generic-alias-v12-all-candidates",
        "self_oracle_path": STAGE12_SELF_RELATIVE,
        "self_oracle_sha256": STAGE12_SELF_SHA256,
        "cases_per_candidate": 128,
        "candidate_checks": 384,
        "completed_candidates": list(official.CORE_FAMILIES),
        "comparison_complete": True,
        "candidate_reports": {
            family: {
                "status": "PASS", "cases": 128, "mismatches": 0,
                "holdout_cases_read": 0,
                "benchmark_or_timing_executed": False,
            }
            for family in official.CORE_FAMILIES
        },
    }
    return baseline, candidates


def self_test() -> dict[str, Any]:
    official.previous.verify_runtime()
    require(not official._candidate_modules(),
            "failure controls must begin without any candidate")
    effects = official._BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, value: Any) -> None:
        require(not any(record["name"] == name for record in checks),
                "a recorder safety control was counted twice")
        checks.append({"name": name, "passed": bool(value)})

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (AssertionError, KeyError, TypeError, ValueError, UnicodeError, OSError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited = official.self_test()
        check(
            "preserve-113-official-v2-and-73-original-no-effect-controls",
            inherited.get("status") == "PASS"
            and inherited.get("passed") is True
            and inherited.get("check_count", 0) >= 113
            and inherited.get("inherited_v1_control_count", 0) >= 73
            and inherited.get("candidate_imports") == 0
            and inherited.get("files_read") == 0
            and inherited.get("subprocesses") == 0
            and inherited.get("clock_samples") == 0,
        )
        capture = validate_capture(TRANSCRIBED_CONTROLLER_FAILURE)
        check("faithfully-validate-actual-captured-controller-json",
              capture["failed_method"] == FAILED_METHOD)
        check("never-label-transcription-as-original-stdout-bytes",
              capture["raw_stream_bytes"] == "NOT RECORDED"
              and capture["raw_stream_sha256"] == "NOT RECORDED")
        for label, updates in (
            ("foreign-controller", {"schema": SCHEMA}),
            ("fake-passing-status", {"status": "PASS"}),
            ("missing-observed-error", {"error": None}),
            ("invented-controller-records", {"records": []}),
        ):
            changed = dict(capture["controller_output"])
            changed.update(updates)
            reject("reject-" + label, lambda changed=changed: validate_capture(
                json.dumps(changed, sort_keys=True, ensure_ascii=True)
            ))
        for label, old, new in (
            ("foreign-failing-family", "rejected rust:", "rejected zig:"),
            ("foreign-failing-method", FAILED_METHOD, "ReTests.test_scanner"),
            ("false-match-owner", "candidates._rust_bridge", "re"),
            ("hidden-rust-failure", r'\"failed\": 1', r'\"failed\": 0'),
            ("false-rust-perfect-pass", r'\"passed\": 145', r'\"passed\": 146'),
            ("different-public-denominator", r'\"methods\": 146', r'\"methods\": 145'),
            ("substituted-official-runner",
             RUST_RUNNER_SUMMARY["runner_sha256"], "0" * 64),
        ):
            altered = TRANSCRIBED_CONTROLLER_FAILURE.replace(old, new)
            check("really-poison-" + label, altered != TRANSCRIBED_CONTROLLER_FAILURE)
            reject("reject-" + label,
                   lambda altered=altered: validate_capture(altered))
        reject("reject-nontext-failure", lambda: validate_capture(7))
        reject("reject-unbounded-failure",
               lambda: validate_capture("x" * (MAX_CAPTURE_BYTES + 1)))

        reference, candidates = synthetic_stage12()
        passed = validate_stage12(reference, candidates)
        check("retain-actual-256-reference-and-384-candidate-contract",
              passed["stdlib_checks"] == 256 and passed["candidate_checks"] == 384)
        for label, target, field, value in (
            ("wrong-reference-schema", "reference", "schema", "fake"),
            ("concealed-reference-mismatch", "reference", "mismatches", 1),
            ("missing-reference-case", "reference", "cases", 127),
            ("reference-candidate-loaded", "reference", "candidate_imports", 1),
            ("wrong-candidate-schema", "candidates", "schema", "fake"),
            ("concealed-candidate-case", "candidates", "candidate_checks", 383),
            ("fake-completion", "candidates", "comparison_complete", False),
            ("omitted-zig", "candidates", "completed_candidates", ["rust", "vm"]),
            ("false-self-reference", "candidates", "self_oracle_sha256", "0" * 64),
            ("illicit-performance-fixture", "candidates", "performance_fixtures_read", 1),
            ("illicit-timing", "candidates", "benchmark_or_timing_executed", True),
        ):
            left, right = copy.deepcopy(reference), copy.deepcopy(candidates)
            (left if target == "reference" else right)[field] = value
            reject("reject-" + label,
                   lambda left=left, right=right: validate_stage12(left, right))
        for family in official.CORE_FAMILIES:
            changed = copy.deepcopy(candidates)
            changed["candidate_reports"][family]["mismatches"] = 1
            reject("reject-concealed-stage12-" + family + "-failure",
                   lambda changed=changed: validate_stage12(reference, changed))

        source_sha = hashlib.sha256(b"synthetic-recorder-source").hexdigest()
        protocol_sha = hashlib.sha256(b"synthetic-recorder-protocol").hexdigest()
        report = build_report(capture, {"synthetic_only": True},
                              source_sha256=source_sha,
                              protocol_sha256=protocol_sha)
        check("accept-exact-synthetic-preserved-first-failure",
              validate_report(report) is report)
        for label, field, value in (
            ("false-passing-failure-report", "status", "PASS"),
            ("substituted-failure-role", "failed_role", "zig"),
            ("substituted-failure-method", "failed_method", "ReTests.test_scanner"),
            ("invented-all-role-success-report", "official_v2_complete_result_created", True),
            ("fabricated-speed", "performance", "1.5x"),
        ):
            changed = copy.deepcopy(report)
            changed[field] = value
            reject("reject-" + label,
                   lambda changed=changed: validate_report(changed))
        for label, family, field, value in (
            ("fake-baseline-records", "re", "individual_method_records_preserved", True),
            ("invented-baseline-pass", "re", "status", "PASS"),
            ("hidden-rust-official-failure", "rust", "status", "PASS"),
            ("invented-perfect-rust", "rust", "passed", 146),
            ("invented-c-official-result", "vm", "status", "PASS"),
            ("invented-zig-official-result", "zig", "status", "PASS"),
        ):
            changed = copy.deepcopy(report)
            changed["roles"][family][field] = value
            reject("reject-" + label,
                   lambda changed=changed: validate_report(changed))
        for field, value in (
            ("raw_controller_stream_recorded", True),
            ("failure_reproduced_or_rerun", True),
            ("candidate_imports", 1),
            ("candidate_processes", 1),
            ("official_test_processes_started", 1),
            ("locale_compilations", 1),
            ("baseline_method_records_fabricated", True),
            ("unexecuted_candidate_results_invented", True),
            ("performance_fixture_access", True),
            ("holdout_access", True),
            ("benchmark_or_timing_executed", True),
        ):
            changed = copy.deepcopy(report)
            changed["scope"][field] = value
            reject("reject-false-preservation-scope-" + field,
                   lambda changed=changed: validate_report(changed))

        check("accept-only-exclusive-failure-evidence",
              destination(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, value in (
            ("historical-v1-evidence", official.V1_REPORT_RELATIVE),
            ("counterfeit-v2-success-evidence", official.REPORT_RELATIVE),
            ("stage12-reference-evidence", STAGE12_SELF_RELATIVE),
            ("stage12-candidate-evidence", STAGE12_ALL_RELATIVE),
            ("v6-source-evidence", official.V6_BASE_REPORT_RELATIVE),
            ("v6-strict-evidence", official.V6_STRICT_REPORT_RELATIVE),
            ("absolute-evidence", "/" + REPORT_RELATIVE),
            ("traversing-evidence", "oracle/cpython-3.14.6/evidence/../fake.json"),
            ("foreign-evidence", "oracle/cpython-3.14.6/evidence/fake.json"),
            ("backslash-evidence", "oracle\\cpython-3.14.6\\evidence\\fake.json"),
            ("nul-evidence", REPORT_RELATIVE + "\x00"),
            ("nontext-evidence", 7),
        ):
            reject("reject-" + label, lambda value=value: destination(value))
        check("never-import-any-regex-candidate", not official._candidate_modules())

    for label, kind in (
        ("zero-evidence-or-project-file-access", "files"),
        ("zero-official-or-candidate-workers", "processes"),
        ("zero-timing-or-clock-samples", "clocks"),
        ("zero-production-entropy", "entropy"),
    ):
        check(label, effects.counts[kind] == 0)
    failures = [item["name"] for item in checks if item["passed"] is not True]
    require(not failures, "failure-recorder synthetic control failed: " + ", ".join(failures))
    require(not official._candidate_modules(),
            "a candidate leaked into the synthetic failure recorder")
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "check_count": len(checks),
        "checks": checks,
        "inherited_official_v2_control_count": inherited["check_count"],
        "inherited_official_v1_control_count": inherited["inherited_v1_control_count"],
        "capture": "faithfully transcribed semantic JSON",
        "raw_stream_bytes": "NOT RECORDED",
        "raw_stream_sha256": "NOT RECORDED",
        "candidate_imports": 0,
        "candidate_processes": 0,
        "official_test_processes_started": 0,
        "files_read": effects.counts["files"],
        "files_written": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "locales_compiled": 0,
        "failure_reproduced_or_rerun": False,
        "report_written": False,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true",
                      help="run blocked, synthetic failure-preservation controls")
    mode.add_argument("--record", action="store_true",
                      help="exclusively preserve the observed first official failure")
    options = parser.parse_args(arguments)
    try:
        report = self_test() if options.self_test else record_failure()
    except (AssertionError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"schema": SCHEMA, "status": "FAIL", "error": str(error)},
                         ensure_ascii=True, sort_keys=True), file=sys.stderr)
        return 1
    if options.self_test:
        print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    else:
        print(json.dumps({
            "schema": SCHEMA,
            "recording_status": "PASS",
            "recorded_experiment_status": "FAIL",
            "failed_role": FAILED_ROLE,
            "failed_method": FAILED_METHOD,
            "rust_passed": 145,
            "rust_methods": 146,
            "c_official": "NOT RUN",
            "zig_official": "NOT RUN",
            "evidence": REPORT_RELATIVE,
            "failure_rerun": False,
            "performance": "NOT MEASURED",
        }, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
