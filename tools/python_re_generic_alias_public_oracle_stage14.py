#!/usr/bin/env python3
"""Retest all public regex aliases against freshly audited native-owned engines."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _stage14_os
    from pathlib import Path as _Stage14Path

    _stage14_root = str(_Stage14Path(__file__).resolve().parent.parent)
    _stage14_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_generic_alias_public_oracle_stage14 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _stage14_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _stage14_entry,
         _stage14_root, *sys.argv[1:]],
    )

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from tools import python_re_generic_alias_public_oracle_stage12 as previous


stage11 = previous.previous
stage07 = previous.stage07
stage06 = previous.stage06
frozen = previous.frozen
official_locale = previous.official_locale
canonical = previous.canonical
digest = previous.digest
ROOT = Path(__file__).resolve().parent.parent

SOURCE_RELATIVE = "tools/python_re_generic_alias_public_oracle_stage14.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V14.md"
SCHEMA = "rebar-python-re-public-generic-alias-v14"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
WORKER_SCHEMA = SCHEMA + "-worker"
SELF_ORACLE_SCHEMA = SCHEMA + "-self-oracle"
ALL_CANDIDATE_SCHEMA = SCHEMA + "-all-candidates"
SEED = 2026072481
SEED_DOMAIN = "rebar/python-re/public-generic-alias/v14"
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
EXPECTED_CASES = 128

STAGE11_SOURCE_RELATIVE = previous.STAGE11_SOURCE_RELATIVE
STAGE11_SOURCE_SHA256 = previous.STAGE11_SOURCE_SHA256
STAGE11_PROTOCOL_RELATIVE = previous.STAGE11_PROTOCOL_RELATIVE
STAGE11_PROTOCOL_SHA256 = previous.STAGE11_PROTOCOL_SHA256
STAGE11_MATRIX_SHA256 = previous.STAGE11_MATRIX_SHA256
STAGE11_SELF_RELATIVE = previous.STAGE11_SELF_RELATIVE
STAGE11_SELF_SHA256 = previous.STAGE11_SELF_SHA256
STAGE11_RUST_FAILURE_RELATIVE = previous.STAGE11_RUST_FAILURE_RELATIVE
STAGE11_RUST_FAILURE_SHA256 = previous.STAGE11_RUST_FAILURE_SHA256

STAGE12_SOURCE_RELATIVE = (
    "tools/python_re_generic_alias_public_oracle_stage12.py"
)
STAGE12_SOURCE_SHA256 = (
    "361e080a0475f5ee7fd7d5da0386a4e2443775069aadca84e053bac357554aaa"
)
STAGE12_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V12.md"
)
STAGE12_PROTOCOL_SHA256 = (
    "1cec5253aabb5464c16d0de461bdd11463ddf11fafea9da6347b8a0af3d30cb1"
)
STAGE12_MATRIX_SHA256 = (
    "65c93cfbbc337ecd762a6b201bacc77e35eb72d201a9e8bc222d730714885aef"
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

OFFICIAL_V2_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v2.py"
OFFICIAL_V2_SOURCE_SHA256 = (
    "e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1"
)
OFFICIAL_V2_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md"
)
OFFICIAL_V2_PROTOCOL_SHA256 = (
    "a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5"
)
OFFICIAL_V2_FAILURE_SOURCE_RELATIVE = (
    "tools/postfinal_cpython_locale_v2_failure.py"
)
OFFICIAL_V2_FAILURE_SOURCE_SHA256 = (
    "42069714991730daff44351eb76ef2fe44478720eb0c51d76b9ea162600b96a5"
)
OFFICIAL_V2_FAILURE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2-FAILURE.md"
)
OFFICIAL_V2_FAILURE_PROTOCOL_SHA256 = (
    "75e9a2709c7755de96ae23106db536a38bfd97a80fb37c5ea3f6a98139e26818"
)
OFFICIAL_V2_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json"
)
OFFICIAL_V2_FAILURE_SHA256 = (
    "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f"
)
OFFICIAL_V3_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v3.py"
OFFICIAL_V3_SOURCE_SHA256 = (
    "28b98c8913ca89ec2ba600484205c3bcb63ae22a86e33d4f7cf3c6f1a68c8a58"
)
OFFICIAL_V3_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V3.md"
)
OFFICIAL_V3_PROTOCOL_SHA256 = (
    "a1f77b1628c03d42b9d8e2650c9b501d9be4cec917d765539c91c750154bd6ac"
)
OFFICIAL_V3_REPORT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v3-all.json"
)
OFFICIAL_V3_REPORT_SHA256 = (
    "18a011a5ce6e47e52cd02e4cb0812c8f9f7919a069edd7d74e57631623b901b5"
)
OFFICIAL_V3_SCHEMA = "rebar-postfinal-cpython-public-locale-v3"
OFFICIAL_V3_SELECTED_METHOD_SHA256 = (
    "d33571d09a3a9cb428a84dece5af233e66267b831d3043c90e3ad77cb8de5178"
)
GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)

V7_BASE_AUDIT_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v7.py"
V7_BASE_AUDIT_SOURCE_SHA256: str | None = (
    "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487"
)
V7_BASE_AUDIT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"
)
V7_BASE_AUDIT_SHA256: str | None = (
    "efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a"
)
V7_BASE_AUDIT_SCHEMA = "rebar-postfinal-from-scratch-audit-v7"
V7_STRICT_AUDIT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v7.py"
V7_STRICT_AUDIT_SOURCE_SHA256: str | None = (
    "9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4"
)
V7_STRICT_AUDIT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json"
)
V7_STRICT_AUDIT_SHA256: str | None = (
    "1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34"
)
V7_STRICT_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v7"

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v14-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-generic-alias-v14-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-generic-alias-public-oracle-v14-all.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    role: (
        "candidates/evidence/python-re-generic-alias-public-oracle-v14-"
        + role + "-failures.json"
    )
    for role in REQUIRED_CANDIDATES
}
APPROVED_OUTPUTS = (
    SELF_ORACLE_RELATIVE,
    SELF_ORACLE_FAILURE_RELATIVE,
    ALL_CANDIDATE_RELATIVE,
    *(CANDIDATE_FAILURE_RELATIVES[role] for role in REQUIRED_CANDIDATES),
)
CORE_SOURCE_PATHS = previous.CORE_SOURCE_PATHS
NATIVE_PATHS = previous.NATIVE_PATHS
OWNED_NATIVE_MODULES = {
    "rust": "candidates._rust_bridge",
    "vm": "candidates._vm_native",
    "zig": "candidates._zig_bridge",
}


def _cohort_seed(cohort: str) -> str:
    frozen.require(cohort in dict(stage11.COHORTS), "unknown V14 alias cohort")
    return digest({"domain": SEED_DOMAIN, "seed": SEED, "cohort": cohort})


def _matrix_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def append(cohort: str, origin: str, argument: str, action: str) -> None:
        rows.append({
            "id": cohort + ":" + origin + ":" + argument + ":" + action,
            "cohort": cohort,
            "origin": origin,
            "argument": argument,
            "action": action,
            "seed": _cohort_seed(cohort),
        })

    for origin in stage11.ORIGINS:
        for argument in stage11.NORMAL_ARGUMENTS:
            for action in stage11.NORMAL_ACTIONS:
                append("ordinary-alias", origin, argument, action)
    for origin in stage11.ORIGINS:
        for argument in stage11.DIVERSE_ARGUMENTS:
            for action in stage11.DIVERSE_ACTIONS:
                append("diverse-argument", origin, argument, action)
    for origin in stage11.ORIGINS:
        for argument in stage11.NORMAL_ARGUMENTS:
            for action in stage11.REJECTION_ACTIONS:
                append("parameterized-type-rejection", origin, argument, action)
    for origin in stage11.ORIGINS:
        for argument in stage11.NORMAL_ARGUMENTS:
            for action in stage11.LIFECYCLE_ACTIONS:
                append("alias-lifecycle", origin, argument, action)
    return rows


MATRIX_SHA256 = (
    "3d57a2eae1e880df934043856cf6d5ed32944908b7642611a3f060406453f1ab"
)


def validate_matrix(value: Any) -> None:
    frozen.require(
        isinstance(value, list)
        and len(value) == EXPECTED_CASES
        and value == _matrix_rows()
        and digest(value) == MATRIX_SHA256
        and len({row["id"] for row in value}) == EXPECTED_CASES,
        "the V14 public-alias matrix omitted, reordered, or changed a real case",
    )
    for cohort, count in stage11.COHORTS:
        frozen.require(
            sum(row["cohort"] == cohort for row in value) == count,
            "the V14 public-alias matrix weakened cohort " + cohort,
        )


def build_matrix() -> list[dict[str, Any]]:
    rows = _matrix_rows()
    validate_matrix(rows)
    return rows


def _verify_source(relative: str, expected: str) -> None:
    frozen.require(
        isinstance(expected, str) and official_locale.is_sha256(expected),
        "an exact V14 historical-source fingerprint is missing: " + relative,
    )
    frozen.require(
        official_locale.sha256_path(
            official_locale.checked_repo_path(relative),
            maximum=frozen.MAX_SOURCE_BYTES,
        ) == expected,
        "a frozen historical source or protocol changed: " + relative,
    )


def _validate_stage12_reference(document: Any) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the true V12 reference is absent")
    expected: dict[str, Any] = {
        "schema": "rebar-python-re-public-generic-alias-v12-self-oracle",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": STAGE12_SOURCE_RELATIVE,
        "source_sha256": STAGE12_SOURCE_SHA256,
        "protocol_path": STAGE12_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE12_PROTOCOL_SHA256,
        "seed": 2026072471,
        "seed_domain": "rebar/python-re/public-generic-alias/v12",
        "matrix_sha256": STAGE12_MATRIX_SHA256,
        "cohorts": 4,
        "cohort_cases": dict(stage11.COHORTS),
        "cases": EXPECTED_CASES,
        "stdlib_checks": 256,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, value in expected.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "the actual 256-check V12 Python reference changed: " + name,
        )
    records = document.get("baseline_records")
    frozen.require(
        isinstance(records, list)
        and len(records) == EXPECTED_CASES
        and all(isinstance(row, dict) for row in records)
        and [row.get("id") for row in records]
        == [row["id"] for row in _matrix_rows()]
        and document.get("baseline_record_sha256") == digest(records)
        and document.get("second_record_sha256") == digest(records)
        and isinstance(document.get("current_provenance"), dict),
        "the historical V12 reference omitted an actual Python observation",
    )
    return document


def _validate_stage12_all(
    document: Any, reference: dict[str, Any],
) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the true V12 candidates are absent")
    expected: dict[str, Any] = {
        "schema": "rebar-python-re-public-generic-alias-v12-all-candidates",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": STAGE12_SOURCE_RELATIVE,
        "source_sha256": STAGE12_SOURCE_SHA256,
        "protocol_path": STAGE12_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE12_PROTOCOL_SHA256,
        "seed": 2026072471,
        "seed_domain": "rebar/python-re/public-generic-alias/v12",
        "matrix_sha256": STAGE12_MATRIX_SHA256,
        "cohorts": 4,
        "cohort_cases": dict(stage11.COHORTS),
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": 384,
        "self_oracle_path": STAGE12_SELF_RELATIVE,
        "self_oracle_sha256": STAGE12_SELF_SHA256,
        "baseline_record_sha256": reference["baseline_record_sha256"],
        "candidate_cross_delegation": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, value in expected.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "the historical 384-check V12 experiment changed: " + name,
        )
    reports = document.get("candidate_reports")
    frozen.require(
        isinstance(reports, dict) and set(reports) == set(REQUIRED_CANDIDATES),
        "a genuinely completed V12 native family was omitted or fabricated",
    )
    for role in REQUIRED_CANDIDATES:
        outcome = reports[role]
        frozen.require(
            isinstance(outcome, dict)
            and outcome.get("candidate") == role
            and outcome.get("module") == "candidates." + role + "_candidate"
            and outcome.get("status") == "PASS"
            and outcome.get("cases") == EXPECTED_CASES
            and outcome.get("cohort_cases") == dict(stage11.COHORTS)
            and outcome.get("record_sha256")
            == reference["baseline_record_sha256"]
            and outcome.get("mismatches") == 0
            and outcome.get("failure_records") == []
            and outcome.get("failures_recorded") == 0
            and outcome.get("benchmark_or_timing_executed") is False
            and outcome.get("performance_fixtures_read") == 0
            and outcome.get("holdout_cases_read") == 0
            and outcome.get("performance") == "NOT MEASURED",
            "the real historical V12 family result changed: " + role,
        )
        guard = outcome.get("guard")
        frozen.require(
            isinstance(guard, dict)
            and guard.get("family") == role
            and all(guard.get(name) is True for name in (
                "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
                "third_party_regex_blocked", "cross_family_blocked",
                "foreign_dynamic_libraries_blocked",
            ))
            and guard.get("native_loader_aliases_blocked")
            == list(stage07.NATIVE_LOADER_ALIASES)
            and guard.get("matcher_inspect_loaded") is False
            and guard.get("matcher_tokenizer_loaded") is False,
            "the genuinely passing historical V12 guard changed: " + role,
        )
        origins = outcome.get("public_origins")
        frozen.require(
            isinstance(origins, dict)
            and set(origins) == {"Pattern", "Match"}
            and all(
                isinstance(origins[name], dict)
                and origins[name].get("public_name") == name
                and origins[name].get("actual_name") == name
                and origins[name].get("actual_qualified_name") == name
                and origins[name].get("actual_module") == (
                    OWNED_NATIVE_MODULES[role] if name == "Match"
                    else "candidates." + role + "_candidate"
                )
                for name in ("Pattern", "Match")
            ),
            "a historical V12 class was misattributed: " + role,
        )
        native = outcome.get("native_binary_sha256")
        frozen.require(
            isinstance(native, dict)
            and set(native) == set(NATIVE_PATHS[role].values())
            and all(official_locale.is_sha256(value) for value in native.values()),
            "a historical V12 owned native observation changed: " + role,
        )
    frozen.require(
        isinstance(document.get("current_provenance"), dict),
        "the genuinely passing V12 experiment omitted historical provenance",
    )
    return document


def _validate_official_v2_failure(document: Any) -> dict[str, Any]:
    frozen.require(
        isinstance(document, dict), "the genuine official V2 failure is absent",
    )
    expected: dict[str, Any] = {
        "schema": "rebar-postfinal-cpython-public-locale-v2-rust-failure-v1",
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "source_path": OFFICIAL_V2_FAILURE_SOURCE_RELATIVE,
        "source_sha256": OFFICIAL_V2_FAILURE_SOURCE_SHA256,
        "protocol_path": OFFICIAL_V2_FAILURE_PROTOCOL_RELATIVE,
        "protocol_sha256": OFFICIAL_V2_FAILURE_PROTOCOL_SHA256,
        "failed_role": "rust",
        "failed_module": "candidates.rust_candidate",
        "failed_method": "ReTests.test_match_repr",
        "official_v2_status": "FAIL",
        "official_v2_complete_result_created": False,
        "official_v2_complete_result_path": (
            "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-all.json"
        ),
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    for name, value in expected.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "the genuine official 145-of-146 failure changed: " + name,
        )
    roles = document.get("roles")
    frozen.require(
        isinstance(roles, dict)
        and set(roles) == {"re", "rust", "vm", "zig"},
        "the genuine official failure invented or omitted an executed role",
    )
    baseline = roles["re"]
    frozen.require(
        isinstance(baseline, dict)
        and baseline.get("execution") == "EXECUTED"
        and baseline.get("status") == "NOT RECORDED"
        and baseline.get("individual_method_records_preserved") is False
        and baseline.get("inferred_pass") is False,
        "the unrecorded official baseline must never be claimed to have passed",
    )
    rust = roles["rust"]
    frozen.require(
        isinstance(rust, dict)
        and rust.get("execution") == "EXECUTED"
        and rust.get("status") == "FAIL"
        and rust.get("module") == "candidates.rust_candidate"
        and rust.get("methods") == 146
        and rust.get("passed") == 145
        and rust.get("failed") == 1
        and rust.get("skipped") == 0
        and rust.get("crashes") == 0
        and rust.get("timeouts") == 0
        and rust.get("failed_method") == "ReTests.test_match_repr"
        and rust.get("individual_method_records_preserved") is False,
        "the genuine first Rust representation failure was concealed",
    )
    for role in ("vm", "zig"):
        pending = roles[role]
        frozen.require(
            isinstance(pending, dict)
            and pending.get("execution") == "NOT RUN"
            and pending.get("status") == "NOT RUN"
            and pending.get("individual_method_records_preserved") is False
            and pending.get("inferred_pass") is False,
            "the genuinely unexecuted official family was fabricated: " + role,
        )
    provenance = document.get("actual_current_provenance")
    frozen.require(
        isinstance(provenance, dict)
        and provenance.get("official_source_path") == OFFICIAL_V2_SOURCE_RELATIVE
        and provenance.get("official_source_sha256") == OFFICIAL_V2_SOURCE_SHA256
        and provenance.get("official_protocol_path") == OFFICIAL_V2_PROTOCOL_RELATIVE
        and provenance.get("official_protocol_sha256") == OFFICIAL_V2_PROTOCOL_SHA256
        and provenance.get("source_audit_source_path")
        == previous.V6_BASE_AUDIT_SOURCE_RELATIVE
        and provenance.get("source_audit_source_sha256")
        == previous.V6_BASE_AUDIT_SOURCE_SHA256
        and provenance.get("source_audit_report_path")
        == previous.V6_BASE_AUDIT_RELATIVE
        and provenance.get("source_audit_report_sha256")
        == previous.V6_BASE_AUDIT_SHA256
        and provenance.get("strict_audit_source_path")
        == previous.V6_STRICT_AUDIT_SOURCE_RELATIVE
        and provenance.get("strict_audit_source_sha256")
        == previous.V6_STRICT_AUDIT_SOURCE_SHA256
        and provenance.get("strict_audit_report_path")
        == previous.V6_STRICT_AUDIT_RELATIVE
        and provenance.get("strict_audit_report_sha256")
        == previous.V6_STRICT_AUDIT_SHA256
        and provenance.get("selected_methods") == 146
        and provenance.get("corpus_cases") == 403
        and provenance.get("named_waiver_count") == 8
        and provenance.get("verified_owned_source_count") == 12
        and provenance.get("verified_native_binary_count") == 5
        and provenance.get("verified_standard_pickle_count") == 48,
        "the real official failure was detached from its historical sources",
    )
    aliases = provenance.get("stage12")
    frozen.require(
        isinstance(aliases, dict)
        and aliases.get("source_path") == STAGE12_SOURCE_RELATIVE
        and aliases.get("source_sha256") == STAGE12_SOURCE_SHA256
        and aliases.get("protocol_path") == STAGE12_PROTOCOL_RELATIVE
        and aliases.get("protocol_sha256") == STAGE12_PROTOCOL_SHA256
        and aliases.get("self_oracle_path") == STAGE12_SELF_RELATIVE
        and aliases.get("self_oracle_sha256") == STAGE12_SELF_SHA256
        and aliases.get("all_candidates_path") == STAGE12_ALL_RELATIVE
        and aliases.get("all_candidates_sha256") == STAGE12_ALL_SHA256
        and aliases.get("cases") == EXPECTED_CASES
        and aliases.get("stdlib_checks") == 256
        and aliases.get("candidate_checks") == 384
        and aliases.get("completed_candidates") == list(REQUIRED_CANDIDATES),
        "the genuine official failure misrepresented the real V12 experiment",
    )
    first = document.get("first_run")
    frozen.require(
        isinstance(first, dict)
        and first.get("controller") == OFFICIAL_V2_SOURCE_RELATIVE
        and first.get("exit_code") == 1
        and first.get("rerun") is False,
        "the first official execution was silently replaced by a rerun",
    )
    failure = first.get("failure")
    frozen.require(
        isinstance(failure, dict)
        and failure.get("failed_role") == "rust"
        and failure.get("failed_module") == "candidates.rust_candidate"
        and failure.get("failed_method") == "ReTests.test_match_repr"
        and failure.get("exception_type") == "AssertionError"
        and failure.get("failure_rerun") is False
        and failure.get("original_method_records_preserved") is False
        and failure.get("raw_stream_bytes") == "NOT RECORDED"
        and failure.get("raw_stream_sha256") == "NOT RECORDED"
        and failure.get("actual_match_repr")
        == "<re.Match object; span=(1, 12), match='abracadabra'>",
        "the actual first official match representation was fabricated",
    )
    scope = document.get("scope")
    frozen.require(
        isinstance(scope, dict)
        and scope.get("actual_first_failure_preserved") is True
        and scope.get("baseline_method_records_fabricated") is False
        and scope.get("failure_reproduced_or_rerun") is False
        and scope.get("raw_controller_stream_recorded") is False
        and scope.get("unexecuted_candidate_results_invented") is False
        and scope.get("candidate_imports") == 0
        and scope.get("candidate_processes") == 0
        and scope.get("official_test_processes_started") == 0
        and scope.get("locale_compilations") == 0
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_access") is False
        and scope.get("performance_fixture_access") is False,
        "the real official failure was rerun, fabricated, or benchmarked",
    )
    return document


def _validate_official_v3_report(
    document: Any,
    *,
    source_fingerprints: dict[str, str],
    native_fingerprints: dict[str, str],
) -> dict[str, Any]:
    frozen.require(
        isinstance(document, dict)
        and document.get("schema") == OFFICIAL_V3_SCHEMA
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("python") == "3.14.6"
        and document.get("source_path") == OFFICIAL_V3_SOURCE_RELATIVE
        and document.get("source_sha256") == OFFICIAL_V3_SOURCE_SHA256
        and document.get("goal_sha256") == GOAL_SHA256
        and document.get("qualified_source_fingerprints") == source_fingerprints
        and document.get("native_elf_fingerprints") == native_fingerprints
        and document.get("holdout_accessed") is False
        and document.get("timing_performed") is False
        and document.get("performance") == "NOT MEASURED",
        "the actual passing official V3 result or current ownership changed",
    )
    audits = document.get("audits")
    frozen.require(
        isinstance(audits, dict)
        and set(audits) == {"from_scratch", "no_delegation"}
        and audits["from_scratch"] == {
            "path": V7_BASE_AUDIT_RELATIVE,
            "postfinal_schema": V7_BASE_AUDIT_SCHEMA,
            "sha256": V7_BASE_AUDIT_SHA256,
            "source_path": V7_BASE_AUDIT_SOURCE_RELATIVE,
            "source_sha256": V7_BASE_AUDIT_SOURCE_SHA256,
        }
        and audits["no_delegation"] == {
            "path": V7_STRICT_AUDIT_RELATIVE,
            "postfinal_schema": V7_STRICT_AUDIT_SCHEMA,
            "sha256": V7_STRICT_AUDIT_SHA256,
            "source_path": V7_STRICT_AUDIT_SOURCE_RELATIVE,
            "source_sha256": V7_STRICT_AUDIT_SOURCE_SHA256,
        },
        "the actual passing official V3 suite used stale native-engine proofs",
    )
    original = document.get("original_oracle")
    frozen.require(
        isinstance(original, dict)
        and original.get("selected_methods") == 146
        and original.get("total_public_methods") == 152
        and original.get("corpus_cases") == 403
        and original.get("selected_method_sha256")
        == OFFICIAL_V3_SELECTED_METHOD_SHA256
        and original.get("runner_path") == "tools/cpython_re_oracle.py"
        and original.get("runner_sha256")
        == "d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb"
        and original.get("manifest_path")
        == "oracle/cpython-3.14.6/manifest.json"
        and original.get("manifest_sha256")
        == "2c89ce37e474cb6f59d61f86ad810662b50b83bbdce3610c04523fe092688597"
        and isinstance(original.get("all_named_waivers"), dict)
        and set(original["all_named_waivers"]) == {
            "DebugTests",
            "ImplementationTest",
            "ReTests.test_large_search",
            "ReTests.test_large_subn",
            "ReTests.test_memory_leaks",
            "ReTests.test_re_groupref_overflow",
            "ReTests.test_regression_gh94675",
            "ReTests.test_search_anchor_at_beginning",
        },
        "the actual official V3 test matrix, upstream source, or waivers changed",
    )
    roles = document.get("roles")
    frozen.require(
        isinstance(roles, dict)
        and set(roles) == {"re", *REQUIRED_CANDIDATES},
        "the genuine four-role official V3 suite omitted an engine",
    )
    expected_ids: list[str] | None = None
    for role in ("re", *REQUIRED_CANDIDATES):
        result = roles[role]
        expected_module = (
            "re" if role == "re" else "candidates." + role + "_candidate"
        )
        frozen.require(
            isinstance(result, dict)
            and result.get("module") == expected_module
            and result.get("methods") == 146
            and result.get("passed") == 146
            and result.get("failed") == 0
            and result.get("failures") == 0
            and result.get("errors") == 0
            and result.get("crashes") == 0
            and result.get("skipped") == 0
            and result.get("timeouts") == 0
            and result.get("locale_caching_passed") is True
            and result.get("locale_compiled_passed") is True
            and result.get("holdout_accessed") is False
            and result.get("timing_performed") is False
            and result.get("performance") == "NOT MEASURED",
            "an actual 146-of-146 official V3 engine result changed: " + role,
        )
        records = result.get("records")
        frozen.require(
            isinstance(records, list)
            and len(records) == 146
            and all(
                isinstance(row, dict)
                and isinstance(row.get("test"), str)
                and row.get("status") == "passed"
                and row.get("skipped") == 0
                and row.get("reason") is None
                for row in records
            ),
            "an actual official V3 method was skipped or concealed: " + role,
        )
        identifiers = [row["test"] for row in records]
        frozen.require(
            len(set(identifiers)) == 146
            and {
                "ReTests.test_match_repr",
                "ReTests.test_locale_caching",
                "ReTests.test_locale_compiled",
            }.issubset(identifiers)
            and (expected_ids is None or identifiers == expected_ids),
            "the genuine official V3 method identities changed: " + role,
        )
        if expected_ids is None:
            expected_ids = identifiers
    scope = document.get("official_scope")
    expected_scope: dict[str, Any] = {
        "genuine_official_methods_per_engine": 146,
        "original_public_methods": 152,
        "original_upstream_corpus_cases": 403,
        "real_locale_methods_per_engine": 2,
        "independently_run_engine_count": 4,
        "verified_owned_source_count": 12,
        "verified_native_binary_count": 5,
        "verified_standard_pickle_count": 48,
        "verified_real_native_match_repr_count": 6,
        "named_waiver_count": 8,
        "genuine_official_v2_rust_failure_preserved": True,
        "official_v2_success_report_exists": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }
    frozen.require(
        isinstance(scope, dict)
        and all(
            scope.get(name) == value
            and type(scope.get(name)) is type(value)
            for name, value in expected_scope.items()
        ),
        "the official V3 suite weakened the true upstream test denominator",
    )
    locale = document.get("locale_reference")
    frozen.require(
        isinstance(locale, dict)
        and locale.get("status") == "PASS"
        and locale.get("python") == "3.14.6"
        and locale.get("candidate_modules_loaded") is False
        and locale.get("genuine_locales") is True
        and locale.get("compiled_locale_switch") is True
        and locale.get("holdout_accessed") is False
        and locale.get("timing_performed") is False,
        "the real official V3 private-locale reference was weakened",
    )
    locales = document.get("locales")
    frozen.require(
        isinstance(locales, dict)
        and locales.get("genuine") is True
        and locales.get("private") is True
        and locales.get("holdout_accessed") is False
        and locales.get("timing_performed") is False
        and locales.get("performance") == "NOT MEASURED"
        and isinstance(locales.get("utf8"), dict)
        and locales["utf8"].get("name") == "en_US.utf8"
        and isinstance(locales.get("iso88591"), dict)
        and locales["iso88591"].get("name") == "en_US.iso88591",
        "the actual official V3 run omitted the genuine isolated Python locales",
    )
    supersedes = document.get("supersedes")
    frozen.require(
        isinstance(supersedes, dict)
        and isinstance(supersedes.get("version_two"), dict),
        "the actual passing official suite omitted the real prior failure",
    )
    failure = supersedes["version_two"]
    frozen.require(
        failure.get("source_path") == OFFICIAL_V2_SOURCE_RELATIVE
        and failure.get("source_sha256") == OFFICIAL_V2_SOURCE_SHA256
        and failure.get("protocol_path") == OFFICIAL_V2_PROTOCOL_RELATIVE
        and failure.get("protocol_sha256") == OFFICIAL_V2_PROTOCOL_SHA256
        and failure.get("failure_source_path") == OFFICIAL_V2_FAILURE_SOURCE_RELATIVE
        and failure.get("failure_source_sha256") == OFFICIAL_V2_FAILURE_SOURCE_SHA256
        and failure.get("failure_protocol_path")
        == OFFICIAL_V2_FAILURE_PROTOCOL_RELATIVE
        and failure.get("failure_protocol_sha256")
        == OFFICIAL_V2_FAILURE_PROTOCOL_SHA256
        and failure.get("failure_report_path") == OFFICIAL_V2_FAILURE_RELATIVE
        and failure.get("failure_report_sha256") == OFFICIAL_V2_FAILURE_SHA256
        and failure.get("failed_role") == "rust"
        and failure.get("failed_method") == "ReTests.test_match_repr"
        and failure.get("rust_passed") == 145
        and failure.get("rust_methods") == 146
        and failure.get("c_official") == "NOT RUN"
        and failure.get("zig_official") == "NOT RUN"
        and failure.get("official_all_report_exists") is False
        and failure.get("historical") is True
        and failure.get("qualifies_current_sources") is False,
        "the genuine passing official suite concealed the actual V2 failure",
    )
    return document


def _require_pinned_v7_audits() -> None:
    for name, value in (
        ("V7_BASE_AUDIT_SOURCE_SHA256", V7_BASE_AUDIT_SOURCE_SHA256),
        ("V7_BASE_AUDIT_SHA256", V7_BASE_AUDIT_SHA256),
        ("V7_STRICT_AUDIT_SOURCE_SHA256", V7_STRICT_AUDIT_SOURCE_SHA256),
        ("V7_STRICT_AUDIT_SHA256", V7_STRICT_AUDIT_SHA256),
    ):
        frozen.require(
            isinstance(value, str) and official_locale.is_sha256(value),
            "the actual repaired V7 independence proof is not yet pinned: " + name,
        )


def _validate_guard(value: Any, role: str) -> None:
    frozen.require(
        isinstance(value, dict)
        and value.get("family") == role
        and all(value.get(name) is True for name in (
            "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
            "third_party_regex_blocked", "cross_family_blocked",
            "foreign_dynamic_libraries_blocked",
        ))
        and value.get("native_loader_aliases_blocked")
        == list(stage07.NATIVE_LOADER_ALIASES),
        "the real V7 native proof weakened an isolation guard: " + role,
    )


def _validate_repr_rows(value: Any, role: str) -> list[dict[str, Any]]:
    frozen.require(
        role in REQUIRED_CANDIDATES
        and isinstance(value, list)
        and len(value) == 2,
        "an audited family omitted a real string or bytes match: " + role,
    )
    bridge = OWNED_NATIVE_MODULES[role]
    normalized: list[dict[str, Any]] = []
    for row, (kind, pattern, subject, matched) in zip(value, (
        ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
        ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
    ), strict=True):
        expected = (
            "<" + bridge + ".Match object; span=(1, 12), match="
            + repr(matched) + ">"
        )
        frozen.require(
            isinstance(row, dict)
            and row.get("id") == role + ":match-repr:" + kind
            and row.get("kind") == kind
            and row.get("span") == [1, 12]
            and row.get("pattern_representation") == repr(pattern)
            and row.get("subject_representation") == repr(subject)
            and row.get("matched_representation") == repr(matched)
            and row.get("match_module", row.get("match_type_module")) == bridge
            and row.get(
                "match_qualified_name", row.get("match_type_qualified_name"),
            ) == "Match"
            and row.get("actual_repr", row.get("observed_repr")) == expected
            and row.get("expected_repr") == expected
            and row.get("native_type_identity") is True
            and row.get("genuine_matching_executed") is True
            and row.get("passed") is True
            and ("role" not in row or row.get("role") == role),
            "a real V7 match representation was forged or delegated: "
            + role + "/" + kind,
        )
        normalized.append({
            "role": role,
            "kind": kind,
            "match_type_module": bridge,
            "match_type_qualified_name": "Match",
            "span": [1, 12],
            "observed_repr": expected,
            "passed": True,
        })
    return normalized


def _validate_source_owner(
    value: Any, role: str, native: dict[str, str],
) -> None:
    candidate = "candidates." + role + "_candidate"
    bridge = OWNED_NATIVE_MODULES[role]
    frozen.require(
        isinstance(value, dict)
        and value.get("schema")
        == previous.V6_BASE_AUDIT_SCHEMA + "-owned-types"
        and value.get("status") == "PASS"
        and value.get("result") == "PASS"
        and value.get("passed") is True
        and value.get("family") == role
        and value.get("candidate_module") == candidate
        and value.get("native_bridge_module") == bridge
        and value.get("native_sha256") == native
        and value.get("standard_pickle_checks") == 16
        and value.get("candidate_regex_matching_executed") is False
        and value.get("third_party_regex_packages") == 0
        and value.get("benchmark_or_timing_executed") is False
        and value.get("fixture_accessed") is False
        and value.get("loaded_candidate_modules") == sorted({candidate, bridge}),
        "the V7 source omitted genuine native-owned standard pickle: " + role,
    )
    _validate_guard(value.get("guard"), role)
    owners = value.get("public_types")
    frozen.require(
        isinstance(owners, dict) and set(owners) == {"Pattern", "Match"},
        "the source proof omitted a real public Python type: " + role,
    )
    for name in ("Pattern", "Match"):
        owner = owners[name]
        frozen.require(
            isinstance(owner, dict)
            and owner.get("module") == (bridge if name == "Match" else candidate)
            and owner.get("name") == name
            and owner.get("qualified_name") == name
            and owner.get("native_bridge_module") == bridge
            and owner.get("candidate_identity") is True
            and owner.get("native_bridge_identity") is (name == "Match")
            and owner.get("genuinely_importable") is True,
            "the V7 source substituted a real owned public type: "
            + role + "/" + name,
        )
    expected = [
        (origin + ":" + argument + ":" + label, origin, argument, label, protocol)
        for origin in ("Pattern", "Match")
        for argument in ("str", "bytes")
        for label, protocol in (
            ("protocol-0", 0), ("protocol-2", 2), ("protocol-4", 4),
            ("highest-protocol", stage11.pickle.HIGHEST_PROTOCOL),
        )
    ]
    records = value.get("records")
    frozen.require(
        isinstance(records, list)
        and len(records) == 16
        and all(isinstance(row, dict) for row in records)
        and [
            (
                row.get("id"), row.get("origin"), row.get("argument"),
                row.get("protocol_name"), row.get("protocol"),
            )
            for row in records
        ] == expected
        and all(
            row.get("passed") is True
            and row.get("genuine_generic_alias") is True
            and row.get("same_owned_native_origin") is True
            and row.get("standard_pickle_round_trip") is True
            for row in records
        ),
        "the V7 source omitted one of 16 real pickle controls: " + role,
    )


def _validate_source_repr(
    value: Any, role: str, native: dict[str, str],
) -> list[dict[str, Any]]:
    bridge = OWNED_NATIVE_MODULES[role]
    candidate = "candidates." + role + "_candidate"
    frozen.require(
        isinstance(value, dict)
        and value.get("schema") == V7_BASE_AUDIT_SCHEMA + "-match-repr-worker"
        and value.get("status") == "PASS"
        and value.get("result") == "PASS"
        and value.get("passed") is True
        and value.get("family") == role
        and value.get("candidate_module") == candidate
        and value.get("native_bridge_module") == bridge
        and value.get("native_binary_sha256") == native
        and value.get("match_repr_checks") == 2
        and value.get("genuine_matching_executed") is True
        and value.get("external_regex_packages") == 0
        and value.get("benchmark_or_timing_executed") is False
        and value.get("fixture_accessed") is False
        and value.get("loaded_candidate_modules") == sorted({candidate, bridge}),
        "the V7 source omitted genuine native matching: " + role,
    )
    _validate_guard(value.get("guard"), role)
    return _validate_repr_rows(value.get("records"), role)


def _validate_strict_owner(
    value: Any, role: str, native: dict[str, str],
) -> list[dict[str, Any]]:
    bridge = OWNED_NATIVE_MODULES[role]
    candidate = "candidates." + role + "_candidate"
    frozen.require(
        isinstance(value, dict)
        and value.get("schema")
        == "rebar-postfinal-no-delegation-public-owner-worker-v7"
        and value.get("status") == "PASS"
        and value.get("role") == role
        and value.get("standard_pickle_check_count") == 16
        and value.get("match_representation_check_count") == 2
        and value.get("match_repr_checks") == 2
        and value.get("genuine_matching_executed") is True
        and value.get("native_binary_sha256") == native
        and value.get("cached_json_decoder_regex_blocked") is True
        and value.get("benchmark_or_timing_executed") is False
        and value.get("holdout_or_case_fixture_access") is False
        and value.get("loaded_candidate_modules") == sorted({candidate, bridge}),
        "the strict V7 proof omitted a real isolated native owner: " + role,
    )
    _validate_guard(value.get("guard"), role)
    owners = value.get("public_type_ownership")
    frozen.require(
        isinstance(owners, dict) and set(owners) == {"Pattern", "Match"},
        "the strict V7 worker omitted a genuine public type: " + role,
    )
    for name in ("Pattern", "Match"):
        owner = owners[name]
        frozen.require(
            isinstance(owner, dict)
            and owner.get("module") == (bridge if name == "Match" else candidate)
            and owner.get("name") == name
            and owner.get("qualified_name") == name
            and owner.get("genuinely_importable") is True,
            "the strict V7 worker substituted a public owner: "
            + role + "/" + name,
        )
    controls = value.get("standard_pickle_checks")
    expected = [
        (origin, argument, protocol)
        for origin in ("Pattern", "Match")
        for argument in ("str", "bytes")
        for protocol in (0, 2, 4, stage11.pickle.HIGHEST_PROTOCOL)
    ]
    frozen.require(
        isinstance(controls, list)
        and len(controls) == 16
        and all(isinstance(row, dict) for row in controls)
        and [
            (row.get("origin"), row.get("argument"), row.get("protocol"))
            for row in controls
        ] == expected
        and all(row.get("passed") is True for row in controls),
        "the strict V7 worker omitted ordinary Python pickle: " + role,
    )
    return _validate_repr_rows(value.get("match_representation_checks"), role)


def _validate_v7_audit_identities(
    base: Any,
    strict: Any,
    *,
    base_source_sha256: str,
    strict_source_sha256: str,
    base_report_sha256: str,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    for label, value in (
        ("base source", base_source_sha256),
        ("strict source", strict_source_sha256),
        ("base report", base_report_sha256),
    ):
        frozen.require(
            isinstance(value, str) and official_locale.is_sha256(value),
            "an actual repaired V7 fingerprint is missing: " + label,
        )
    for document, schema, source, fingerprint, label in (
        (
            base, V7_BASE_AUDIT_SCHEMA, V7_BASE_AUDIT_SOURCE_RELATIVE,
            base_source_sha256, "from-scratch",
        ),
        (
            strict, V7_STRICT_AUDIT_SCHEMA, V7_STRICT_AUDIT_SOURCE_RELATIVE,
            strict_source_sha256, "no-delegation",
        ),
    ):
        frozen.require(
            isinstance(document, dict)
            and document.get("schema") == schema
            and document.get("postfinal_schema") == schema
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("passed") is True
            and document.get("audit_source_path") == source
            and document.get("audit_source_sha256") == fingerprint
            and document.get("verified_core_family_count") == 3
            and document.get("verified_distinct_pipeline_count") == 4
            and document.get("verified_match_repr_checks") == 6,
            "the actual repaired V7 " + label + " proof did not pass",
        )
        families = document.get("families")
        frozen.require(
            isinstance(families, dict)
            and set(REQUIRED_CANDIDATES).issubset(families)
            and all(
                isinstance(families[role], dict)
                and families[role].get("passed") is True
                for role in REQUIRED_CANDIDATES
            ),
            "the actual V7 " + label + " proof omitted a native family",
        )
        manifest = document.get("manifest_provenance")
        frozen.require(
            isinstance(manifest, dict)
            and manifest.get("passed") is True
            and manifest.get("issues") == []
            and manifest.get("python_dependencies") == []
            and manifest.get("rust_third_party_dependency_count") == 0,
            "the actual repaired V7 engine wraps an external implementation",
        )
        native = document.get("native_elf_provenance")
        frozen.require(
            isinstance(native, dict)
            and native.get("passed") is True
            and native.get("issues") == []
            and native.get("expected_binary_count") == 5
            and native.get("audited_binary_count") == 5
            and isinstance(native.get("families"), dict)
            and set(native["families"]) == set(REQUIRED_CANDIDATES)
            and all(
                isinstance(native["families"][role], dict)
                and native["families"][role].get("passed") is True
                and native["families"][role].get("issues") == []
                for role in REQUIRED_CANDIDATES
            ),
            "the actual V7 " + label + " proof omitted an owned native engine",
        )

    all_paths = {
        path for paths in CORE_SOURCE_PATHS.values() for path in paths
    }
    frozen.require(
        base.get("verified_candidate_source_count") == 12
        and isinstance(base.get("verified_candidate_source_paths"), list)
        and len(base["verified_candidate_source_paths"]) == 12
        and set(base["verified_candidate_source_paths"]) == all_paths
        and base.get("verified_native_role_count") == 5
        and base.get("standard_pickle_checks_per_family") == 16
        and base.get("standard_pickle_checks") == 48
        and base.get("match_repr_checks_per_family") == 2
        and base.get("historical_stage12_only") is True
        and base.get("stage12_candidate_results_qualify_current_sources")
        is False
        and base.get("official_v2_rust_failure_path")
        == OFFICIAL_V2_FAILURE_RELATIVE
        and base.get("official_v2_rust_failure_sha256")
        == OFFICIAL_V2_FAILURE_SHA256
        and base.get("official_v2_rust_failure_historical") is True
        and base.get("previous_v6_audit_source_path")
        == previous.V6_BASE_AUDIT_SOURCE_RELATIVE
        and base.get("previous_v6_audit_source_sha256")
        == previous.V6_BASE_AUDIT_SOURCE_SHA256
        and base.get("previous_v6_audit_report_path")
        == previous.V6_BASE_AUDIT_RELATIVE
        and base.get("previous_v6_audit_report_sha256")
        == previous.V6_BASE_AUDIT_SHA256
        and base.get("previous_v6_report_historical") is True
        and base.get("previous_v6_strict_audit_source_path")
        == previous.V6_STRICT_AUDIT_SOURCE_RELATIVE
        and base.get("previous_v6_strict_audit_source_sha256")
        == previous.V6_STRICT_AUDIT_SOURCE_SHA256
        and base.get("previous_v6_strict_audit_report_path")
        == previous.V6_STRICT_AUDIT_RELATIVE
        and base.get("previous_v6_strict_audit_report_sha256")
        == previous.V6_STRICT_AUDIT_SHA256
        and base.get("previous_v6_strict_report_historical") is True,
        "the V7 source proof weakened real ownership or falsified its history",
    )
    frozen.require(
        strict.get("base_audit_source_path") == V7_BASE_AUDIT_SOURCE_RELATIVE
        and strict.get("base_audit_source_sha256") == base_source_sha256
        and strict.get("base_audit_report_path") == V7_BASE_AUDIT_RELATIVE
        and strict.get("base_audit_report_sha256") == base_report_sha256
        and strict.get("base_audit_postfinal_schema") == V7_BASE_AUDIT_SCHEMA
        and strict.get("previous_v6_audit_source_path")
        == previous.V6_STRICT_AUDIT_SOURCE_RELATIVE
        and strict.get("previous_v6_audit_source_sha256")
        == previous.V6_STRICT_AUDIT_SOURCE_SHA256
        and strict.get("previous_v6_audit_report_path")
        == previous.V6_STRICT_AUDIT_RELATIVE
        and strict.get("previous_v6_audit_report_sha256")
        == previous.V6_STRICT_AUDIT_SHA256
        and strict.get("previous_v6_report_historical") is True
        and strict.get("previous_v6_source_audit_source_path")
        == previous.V6_BASE_AUDIT_SOURCE_RELATIVE
        and strict.get("previous_v6_source_audit_source_sha256")
        == previous.V6_BASE_AUDIT_SOURCE_SHA256
        and strict.get("previous_v6_source_audit_report_path")
        == previous.V6_BASE_AUDIT_RELATIVE
        and strict.get("previous_v6_source_audit_report_sha256")
        == previous.V6_BASE_AUDIT_SHA256
        and strict.get("previous_v6_source_report_historical") is True
        and strict.get("verified_public_type_family_count") == 3
        and strict.get("verified_standard_pickle_count") == 48
        and strict.get("official_v2_failure_preserved") is True
        and strict.get("official_v2_failure_qualifies_current_engines") is False,
        "the strict V7 proof is not bound to the actual repaired source audit",
    )
    failure = strict.get("official_v2_failure_provenance")
    frozen.require(
        isinstance(failure, dict)
        and failure.get("path") == OFFICIAL_V2_FAILURE_RELATIVE
        and failure.get("sha256") == OFFICIAL_V2_FAILURE_SHA256
        and failure.get("status") == "FAIL"
        and failure.get("result") == "FAIL"
        and failure.get("failed_role") == "rust"
        and failure.get("failed_method") == "ReTests.test_match_repr"
        and failure.get("historical") is True
        and failure.get("qualifies_current_engines") is False,
        "the strict V7 proof misrepresented the genuine official failure",
    )
    frozen.require(
        strict.get("manifest_provenance") == base.get("manifest_provenance")
        and strict.get("native_elf_provenance")
        == base.get("native_elf_provenance"),
        "the two fresh V7 audits disagree on the actual native-owned engines",
    )
    fingerprints = strict.get("qualified_source_fingerprints")
    frozen.require(
        isinstance(fingerprints, dict)
        and set(fingerprints) == all_paths
        and len(fingerprints) == 12
        and all(
            isinstance(value, str) and official_locale.is_sha256(value)
            for value in fingerprints.values()
        ),
        "the actual V7 strict proof omitted one of 12 native-owned sources",
    )
    flattened = strict.get("native_elf_fingerprints")
    labels = {label for paths in NATIVE_PATHS.values() for label in paths}
    frozen.require(
        isinstance(flattened, dict)
        and set(flattened) == labels
        and len(flattened) == 5
        and all(
            isinstance(value, str) and official_locale.is_sha256(value)
            for value in flattened.values()
        ),
        "the actual V7 strict proof omitted one of five real native engines",
    )
    base_owners = base.get("public_type_ownership")
    base_repr = base.get("public_match_repr")
    strict_owners = strict.get("public_type_ownership")
    strict_repr = strict.get("strict_public_match_repr")
    frozen.require(
        all(
            isinstance(section, dict)
            and set(section) == set(REQUIRED_CANDIDATES)
            for section in (base_owners, base_repr, strict_owners, strict_repr)
        )
        and strict.get("public_match_repr") == base_repr
        and strict_repr == strict_owners,
        "the fresh V7 proofs omitted or substituted real public ownership",
    )
    sources: dict[str, dict[str, str]] = {}
    natives: dict[str, dict[str, str]] = {}
    for role in REQUIRED_CANDIDATES:
        sources[role] = {
            path: fingerprints[path] for path in CORE_SOURCE_PATHS[role]
        }
        natives[role] = {
            path: flattened[label]
            for label, path in NATIVE_PATHS[role].items()
        }
        raw = base["native_elf_provenance"]["families"][role].get("files")
        records = list(raw.values()) if isinstance(raw, dict) else raw
        frozen.require(
            isinstance(records, list)
            and len(records) == len(NATIVE_PATHS[role])
            and all(isinstance(item, dict) for item in records),
            "the V7 source concealed a native ELF identity: " + role,
        )
        actual: dict[str, str] = {}
        for record in records:
            path, fingerprint = record.get("file"), record.get("sha256")
            frozen.require(
                isinstance(path, str)
                and path in natives[role]
                and path not in actual
                and isinstance(fingerprint, str)
                and official_locale.is_sha256(fingerprint),
                "the V7 source duplicated or substituted a native ELF: " + role,
            )
            actual[path] = fingerprint
        frozen.require(
            actual == natives[role],
            "the fresh V7 proofs disagree on an actual owned native: " + role,
        )
        _validate_source_owner(base_owners[role], role, natives[role])
        source_repr = _validate_source_repr(base_repr[role], role, natives[role])
        owner_repr = _validate_strict_owner(
            strict_owners[role], role, natives[role],
        )
        frozen.require(
            source_repr == owner_repr,
            "the independent fresh V7 match representations differ: " + role,
        )
    frozen.require(
        sum(map(len, sources.values())) == 12
        and sum(map(len, natives.values())) == 5,
        "the repaired V7 audit silently changed the ownership denominator",
    )
    return sources, natives


def _validate_v7_audits(
    base: Any, strict: Any,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    _require_pinned_v7_audits()
    frozen.require(
        isinstance(V7_BASE_AUDIT_SOURCE_SHA256, str)
        and isinstance(V7_BASE_AUDIT_SHA256, str)
        and isinstance(V7_STRICT_AUDIT_SOURCE_SHA256, str),
        "actual passing V7 proofs are mandatory before any candidate executes",
    )
    sources, natives = _validate_v7_audit_identities(
        base,
        strict,
        base_source_sha256=V7_BASE_AUDIT_SOURCE_SHA256,
        strict_source_sha256=V7_STRICT_AUDIT_SOURCE_SHA256,
        base_report_sha256=V7_BASE_AUDIT_SHA256,
    )
    for records in sources.values():
        for path, expected in records.items():
            _verify_source(path, expected)
    for records in natives.values():
        for path, expected in records.items():
            frozen.require(
                official_locale.sha256_path(
                    official_locale.checked_repo_path(path),
                ) == expected,
                "an actual rebuilt V7 native engine changed: " + path,
            )
    return sources, natives


def _authenticate_provenance() -> dict[str, Any]:
    official_locale.verify_runtime()
    frozen.candidate_free()
    for path, expected in (
        (STAGE11_SOURCE_RELATIVE, STAGE11_SOURCE_SHA256),
        (STAGE11_PROTOCOL_RELATIVE, STAGE11_PROTOCOL_SHA256),
        (STAGE12_SOURCE_RELATIVE, STAGE12_SOURCE_SHA256),
        (STAGE12_PROTOCOL_RELATIVE, STAGE12_PROTOCOL_SHA256),
        (OFFICIAL_V2_SOURCE_RELATIVE, OFFICIAL_V2_SOURCE_SHA256),
        (OFFICIAL_V2_PROTOCOL_RELATIVE, OFFICIAL_V2_PROTOCOL_SHA256),
        (OFFICIAL_V2_FAILURE_SOURCE_RELATIVE, OFFICIAL_V2_FAILURE_SOURCE_SHA256),
        (
            OFFICIAL_V2_FAILURE_PROTOCOL_RELATIVE,
            OFFICIAL_V2_FAILURE_PROTOCOL_SHA256,
        ),
        (OFFICIAL_V3_SOURCE_RELATIVE, OFFICIAL_V3_SOURCE_SHA256),
        (OFFICIAL_V3_PROTOCOL_RELATIVE, OFFICIAL_V3_PROTOCOL_SHA256),
    ):
        _verify_source(path, expected)

    old_reference, old_reference_sha = stage06._read_public_document(
        STAGE11_SELF_RELATIVE, expected_sha256=STAGE11_SELF_SHA256,
    )
    previous._validate_preserved_stage11_reference(old_reference)
    old_failure, old_failure_sha = stage06._read_public_document(
        STAGE11_RUST_FAILURE_RELATIVE,
        expected_sha256=STAGE11_RUST_FAILURE_SHA256,
    )
    previous._validate_preserved_stage11_failure(old_failure, old_reference)
    stage12_reference, stage12_reference_sha = stage06._read_public_document(
        STAGE12_SELF_RELATIVE, expected_sha256=STAGE12_SELF_SHA256,
    )
    _validate_stage12_reference(stage12_reference)
    stage12_candidates, stage12_candidates_sha = stage06._read_public_document(
        STAGE12_ALL_RELATIVE, expected_sha256=STAGE12_ALL_SHA256,
    )
    _validate_stage12_all(stage12_candidates, stage12_reference)
    official_failure, official_failure_sha = stage06._read_public_document(
        OFFICIAL_V2_FAILURE_RELATIVE,
        expected_sha256=OFFICIAL_V2_FAILURE_SHA256,
    )
    _validate_official_v2_failure(official_failure)
    frozen.require(
        old_reference_sha == STAGE11_SELF_SHA256
        and old_failure_sha == STAGE11_RUST_FAILURE_SHA256
        and stage12_reference_sha == STAGE12_SELF_SHA256
        and stage12_candidates_sha == STAGE12_ALL_SHA256
        and official_failure_sha == OFFICIAL_V2_FAILURE_SHA256,
        "an actual V11, V12, or official CPython result was substituted",
    )

    _require_pinned_v7_audits()
    frozen.require(
        isinstance(V7_BASE_AUDIT_SOURCE_SHA256, str)
        and isinstance(V7_BASE_AUDIT_SHA256, str)
        and isinstance(V7_STRICT_AUDIT_SOURCE_SHA256, str)
        and isinstance(V7_STRICT_AUDIT_SHA256, str),
        "no V14 candidate can execute before both genuine V7 reports exist",
    )
    _verify_source(V7_BASE_AUDIT_SOURCE_RELATIVE, V7_BASE_AUDIT_SOURCE_SHA256)
    _verify_source(
        V7_STRICT_AUDIT_SOURCE_RELATIVE, V7_STRICT_AUDIT_SOURCE_SHA256,
    )
    base, base_sha = stage06._read_public_document(
        V7_BASE_AUDIT_RELATIVE, expected_sha256=V7_BASE_AUDIT_SHA256,
    )
    strict, strict_sha = stage06._read_public_document(
        V7_STRICT_AUDIT_RELATIVE, expected_sha256=V7_STRICT_AUDIT_SHA256,
    )
    frozen.require(
        base_sha == V7_BASE_AUDIT_SHA256
        and strict_sha == V7_STRICT_AUDIT_SHA256,
        "a genuinely passing repaired V7 audit was replaced",
    )
    sources, natives = _validate_v7_audits(base, strict)
    official_v3, official_v3_sha = stage06._read_public_document(
        OFFICIAL_V3_REPORT_RELATIVE,
        expected_sha256=OFFICIAL_V3_REPORT_SHA256,
    )
    all_sources = {
        path: fingerprint
        for records in sources.values()
        for path, fingerprint in records.items()
    }
    all_natives = {
        label: natives[role][path]
        for role in REQUIRED_CANDIDATES
        for label, path in NATIVE_PATHS[role].items()
    }
    _validate_official_v3_report(
        official_v3,
        source_fingerprints=all_sources,
        native_fingerprints=all_natives,
    )
    frozen.require(
        official_v3_sha == OFFICIAL_V3_REPORT_SHA256,
        "the genuinely passing 584-check official CPython report changed",
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
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "previous_stage11_source_path": STAGE11_SOURCE_RELATIVE,
        "previous_stage11_source_sha256": STAGE11_SOURCE_SHA256,
        "previous_stage11_protocol_path": STAGE11_PROTOCOL_RELATIVE,
        "previous_stage11_protocol_sha256": STAGE11_PROTOCOL_SHA256,
        "previous_stage11_self_oracle_path": STAGE11_SELF_RELATIVE,
        "previous_stage11_self_oracle_sha256": STAGE11_SELF_SHA256,
        "previous_stage11_failure_path": STAGE11_RUST_FAILURE_RELATIVE,
        "previous_stage11_failure_sha256": STAGE11_RUST_FAILURE_SHA256,
        "previous_stage11_failure_count": 16,
        "previous_stage11_nonmatching_families": ["vm", "zig"],
        "historical_stage12_source_path": STAGE12_SOURCE_RELATIVE,
        "historical_stage12_source_sha256": STAGE12_SOURCE_SHA256,
        "historical_stage12_protocol_path": STAGE12_PROTOCOL_RELATIVE,
        "historical_stage12_protocol_sha256": STAGE12_PROTOCOL_SHA256,
        "historical_stage12_self_oracle_path": STAGE12_SELF_RELATIVE,
        "historical_stage12_self_oracle_sha256": STAGE12_SELF_SHA256,
        "historical_stage12_all_candidate_path": STAGE12_ALL_RELATIVE,
        "historical_stage12_all_candidate_sha256": STAGE12_ALL_SHA256,
        "historical_stage12_stdlib_checks": 256,
        "historical_stage12_candidate_checks": 384,
        "historical_stage12_qualifies_current_sources": False,
        "official_v2_source_path": OFFICIAL_V2_SOURCE_RELATIVE,
        "official_v2_source_sha256": OFFICIAL_V2_SOURCE_SHA256,
        "official_v2_protocol_path": OFFICIAL_V2_PROTOCOL_RELATIVE,
        "official_v2_protocol_sha256": OFFICIAL_V2_PROTOCOL_SHA256,
        "official_v2_failure_path": OFFICIAL_V2_FAILURE_RELATIVE,
        "official_v2_failure_sha256": OFFICIAL_V2_FAILURE_SHA256,
        "official_v2_failure_status": "FAIL",
        "official_v2_failed_role": "rust",
        "official_v2_failed_method": "ReTests.test_match_repr",
        "official_v2_baseline_status": "NOT RECORDED",
        "official_v2_unexecuted_roles": ["vm", "zig"],
        "official_v2_failure_qualifies_current_sources": False,
        "official_v3_source_path": OFFICIAL_V3_SOURCE_RELATIVE,
        "official_v3_source_sha256": OFFICIAL_V3_SOURCE_SHA256,
        "official_v3_protocol_path": OFFICIAL_V3_PROTOCOL_RELATIVE,
        "official_v3_protocol_sha256": OFFICIAL_V3_PROTOCOL_SHA256,
        "official_v3_report_path": OFFICIAL_V3_REPORT_RELATIVE,
        "official_v3_report_sha256": OFFICIAL_V3_REPORT_SHA256,
        "official_v3_status": "PASS",
        "official_v3_completed_roles": ["re", *REQUIRED_CANDIDATES],
        "official_v3_methods_per_role": 146,
        "official_v3_total_method_checks": 584,
        "official_v3_failed_methods": 0,
        "official_v3_skipped_methods": 0,
        "official_v3_crashes": 0,
        "official_v3_v2_failure_preserved": True,
        "base_audit_source_path": V7_BASE_AUDIT_SOURCE_RELATIVE,
        "base_audit_source_sha256": V7_BASE_AUDIT_SOURCE_SHA256,
        "base_audit_path": V7_BASE_AUDIT_RELATIVE,
        "base_audit_sha256": V7_BASE_AUDIT_SHA256,
        "strict_audit_source_path": V7_STRICT_AUDIT_SOURCE_RELATIVE,
        "strict_audit_source_sha256": V7_STRICT_AUDIT_SOURCE_SHA256,
        "strict_audit_path": V7_STRICT_AUDIT_RELATIVE,
        "strict_audit_sha256": V7_STRICT_AUDIT_SHA256,
        "source_sha256_by_family": sources,
        "native_sha256_by_family": natives,
        "stage10_provenance": {"native_sha256_by_family": natives},
        "native_source_count": 12,
        "native_binary_count": 5,
        "verified_standard_pickle_count": 48,
        "verified_match_repr_count": 6,
    }


WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_generic_alias_public_oracle_stage14 "
    "import _worker_entry;"
    "raise SystemExit(_worker_entry(sys.argv[2],sys.argv[3]))"
)


@contextmanager
def _stage14_context() -> Iterator[None]:
    updates: dict[str, Any] = {
        "SOURCE_RELATIVE": SOURCE_RELATIVE,
        "PROTOCOL_RELATIVE": PROTOCOL_RELATIVE,
        "SCHEMA": SCHEMA,
        "SELF_TEST_SCHEMA": SELF_TEST_SCHEMA,
        "WORKER_SCHEMA": WORKER_SCHEMA,
        "SELF_ORACLE_SCHEMA": SELF_ORACLE_SCHEMA,
        "ALL_CANDIDATE_SCHEMA": ALL_CANDIDATE_SCHEMA,
        "SEED": SEED,
        "SEED_DOMAIN": SEED_DOMAIN,
        "MATRIX_SHA256": MATRIX_SHA256,
        "SELF_ORACLE_RELATIVE": SELF_ORACLE_RELATIVE,
        "SELF_ORACLE_FAILURE_RELATIVE": SELF_ORACLE_FAILURE_RELATIVE,
        "ALL_CANDIDATE_RELATIVE": ALL_CANDIDATE_RELATIVE,
        "CANDIDATE_FAILURE_RELATIVES": CANDIDATE_FAILURE_RELATIVES,
        "APPROVED_OUTPUTS": APPROVED_OUTPUTS,
        "WORKER_BOOTSTRAP": WORKER_BOOTSTRAP,
        "build_matrix": build_matrix,
        "validate_matrix": validate_matrix,
        "_authenticate_provenance": _authenticate_provenance,
    }
    original = {name: getattr(previous, name) for name in updates}
    try:
        for name, value in updates.items():
            setattr(previous, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(previous, name, value)


def _worker_entry(role: str, source_sha256: str) -> int:
    with _stage14_context():
        return previous._worker_entry(role, source_sha256)


def _validate_reference_worker(
    document: Any,
    *,
    role: str,
    source_sha256: str,
) -> dict[str, Any]:
    frozen.require(
        role in ("stdlib-a", "stdlib-b")
        and isinstance(document, dict),
        "a full independent Python reference worker is absent",
    )
    expected: dict[str, Any] = {
        "schema": WORKER_SCHEMA,
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_sha256": source_sha256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cases": EXPECTED_CASES,
        "cohort_cases": dict(stage11.COHORTS),
        "guard": {"baseline_only": True, "candidate_imported": False},
        "native_binary_sha256": {},
        "inspect_loaded": False,
        "tokenize_loaded": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, value in expected.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "an actual independent V14 Python worker changed " + role
            + ": " + name,
        )
    records = document.get("records")
    frozen.require(
        isinstance(records, list)
        and len(records) == EXPECTED_CASES
        and all(isinstance(row, dict) for row in records)
        and [row.get("id") for row in records]
        == [row["id"] for row in _matrix_rows()]
        and document.get("record_sha256") == digest(records),
        "an independent V14 Python worker omitted, changed, or reordered a case: "
        + role,
    )
    origins = document.get("public_origins")
    frozen.require(
        isinstance(origins, dict)
        and set(origins) == {"Pattern", "Match"}
        and all(
            isinstance(origins[name], dict)
            and origins[name].get("public_name") == name
            and origins[name].get("actual_name") == name
            and origins[name].get("actual_qualified_name") == name
            and origins[name].get("actual_module") == "re"
            for name in ("Pattern", "Match")
        ),
        "an independent V14 Python worker replaced a real standard-library type: "
        + role,
    )
    return document


def _validate_complete_self_oracle(
    document: Any, provenance: dict[str, Any],
) -> dict[str, Any]:
    frozen.require(
        isinstance(document, dict) and isinstance(provenance, dict),
        "the full two-process V14 Python reference is absent",
    )
    expected: dict[str, Any] = {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance.get("source_sha256"),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance.get("protocol_sha256"),
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": len(stage11.COHORTS),
        "cohort_cases": dict(stage11.COHORTS),
        "current_provenance": provenance,
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, value in expected.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "the full two-process V14 Python reference changed: " + name,
        )
    source_sha256 = provenance.get("source_sha256")
    frozen.require(
        isinstance(source_sha256, str)
        and official_locale.is_sha256(source_sha256),
        "the full V14 Python reference lost its exact source fingerprint",
    )
    workers = document.get("reference_worker_reports")
    frozen.require(
        isinstance(workers, dict)
        and set(workers) == {"stdlib-a", "stdlib-b"},
        "the V14 Python reference concealed an independently executed process",
    )
    first = _validate_reference_worker(
        workers["stdlib-a"], role="stdlib-a", source_sha256=source_sha256,
    )
    second = _validate_reference_worker(
        workers["stdlib-b"], role="stdlib-b", source_sha256=source_sha256,
    )
    first_records = document.get("baseline_records")
    second_records = document.get("second_records")
    frozen.require(
        isinstance(first_records, list)
        and isinstance(second_records, list)
        and len(first_records) == len(second_records) == EXPECTED_CASES
        and first_records == first["records"]
        and second_records == second["records"]
        and document.get("baseline_record_sha256") == digest(first_records)
        and document.get("second_record_sha256") == digest(second_records)
        and first.get("record_sha256") == document["baseline_record_sha256"]
        and second.get("record_sha256") == document["second_record_sha256"]
        and first_records == second_records,
        "the V14 reference omitted, reordered, or forged one of 256 observations",
    )
    return document


def _persist_reference_failure(
    *,
    role: str,
    provenance: dict[str, Any],
    workers: dict[str, Any],
    error: BaseException | None = None,
    differences: list[dict[str, Any]] | None = None,
) -> str:
    frozen.require(
        role in ("stdlib-a", "stdlib-b"),
        "refusing to preserve a foreign standard-library reference failure",
    )
    first = workers.get("stdlib-a")
    second = workers.get("stdlib-b")
    first_records = first.get("records") if isinstance(first, dict) else None
    second_records = second.get("records") if isinstance(second, dict) else None
    actual = differences if differences is not None else []
    details = None
    if error is not None:
        details = (
            error.details
            if isinstance(error, stage07.PublicWorkerFailure)
            else {
                "kind": type(error).__name__,
                "exception": stage07._normalize(error),
            }
        )
    document = {
        "schema": SELF_ORACLE_SCHEMA + "-failure",
        "status": "FAIL",
        "result": "FAIL",
        **stage11._base_document(provenance),
        "failed_role": role,
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
        "mismatches": len(actual),
        "failure_records": actual,
        "failures_recorded": len(actual),
        "worker_failure": details,
        "candidate_imports": 0,
        "candidate_processes": 0,
    }
    fingerprint = stage11._exclusive_evidence(
        document, SELF_ORACLE_FAILURE_RELATIVE,
    )
    return SELF_ORACLE_FAILURE_RELATIVE + " (sha256 " + fingerprint + ")"


def run_self_oracle() -> dict[str, Any]:
    with _stage14_context(), previous._stage12_context():
        provenance = stage11._authenticate_provenance()
        frozen.require(
            not (ROOT / SELF_ORACLE_RELATIVE).exists(),
            "the exclusively frozen full two-reference V14 result already exists",
        )
        workers: dict[str, Any] = {}
        for role in ("stdlib-a", "stdlib-b"):
            try:
                worker = stage11._run_worker(
                    role, source_sha256=provenance["source_sha256"],
                )
                _validate_reference_worker(
                    worker,
                    role=role,
                    source_sha256=provenance["source_sha256"],
                )
            except (Exception, RecursionError) as error:
                preserved = _persist_reference_failure(
                    role=role,
                    provenance=provenance,
                    workers=workers,
                    error=error,
                )
                raise frozen.OracleIntegrityError(
                    "the real independent Python V14 failure was preserved in "
                    + preserved
                ) from error
            workers[role] = worker
        baseline = workers["stdlib-a"]["records"]
        second_records = workers["stdlib-b"]["records"]
        differences = stage11._mismatches(baseline, second_records)
        if differences:
            preserved = _persist_reference_failure(
                role="stdlib-b",
                provenance=provenance,
                workers=workers,
                differences=differences,
            )
            raise frozen.OracleIntegrityError(
                "the genuine two-process V14 Python disagreement was preserved in "
                + preserved
            )
        document = {
            "schema": SELF_ORACLE_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            **stage11._base_document(provenance),
            "cases": EXPECTED_CASES,
            "stdlib_checks": EXPECTED_CASES * 2,
            "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
            "reference_worker_reports": workers,
            "baseline_records": baseline,
            "second_records": second_records,
            "baseline_record_sha256": digest(baseline),
            "second_record_sha256": digest(second_records),
            "mismatches": 0,
            "failure_records": [],
            "candidate_imports": 0,
            "candidate_processes": 0,
        }
        _validate_complete_self_oracle(document, provenance)
        fingerprint = stage11._exclusive_evidence(document, SELF_ORACLE_RELATIVE)
        return {
            "schema": SELF_ORACLE_SCHEMA,
            "status": "PASS",
            "cases": EXPECTED_CASES,
            "stdlib_checks": EXPECTED_CASES * 2,
            "baseline_records_preserved": EXPECTED_CASES,
            "second_records_preserved": EXPECTED_CASES,
            "reference_records_preserved": EXPECTED_CASES * 2,
            "mismatches": 0,
            "evidence": SELF_ORACLE_RELATIVE,
            "evidence_sha256": fingerprint,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }


def _validate_complete_candidate_report(
    document: Any,
    *,
    baseline: list[dict[str, Any]],
    second_reference: list[dict[str, Any]],
    provenance: dict[str, Any],
    self_oracle_sha256: str,
) -> dict[str, Any]:
    frozen.require(
        isinstance(document, dict)
        and document.get("schema") == ALL_CANDIDATE_SCHEMA
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("python") == "3.14.6"
        and document.get("source_path") == SOURCE_RELATIVE
        and document.get("source_sha256") == provenance.get("source_sha256")
        and document.get("protocol_path") == PROTOCOL_RELATIVE
        and document.get("protocol_sha256") == provenance.get("protocol_sha256")
        and document.get("seed") == SEED
        and document.get("seed_domain") == SEED_DOMAIN
        and document.get("matrix_sha256") == MATRIX_SHA256
        and document.get("cohorts") == len(stage11.COHORTS)
        and document.get("cohort_cases") == dict(stage11.COHORTS)
        and document.get("selected") == "all"
        and document.get("selected_candidates") == list(REQUIRED_CANDIDATES)
        and document.get("completed_candidates") == list(REQUIRED_CANDIDATES)
        and document.get("comparison_complete") is True
        and document.get("cases_per_candidate") == EXPECTED_CASES
        and document.get("candidate_checks") == 384
        and document.get("self_oracle_path") == SELF_ORACLE_RELATIVE
        and document.get("self_oracle_sha256") == self_oracle_sha256
        and document.get("reference_checks") == EXPECTED_CASES * 2
        and document.get("baseline_records") == baseline
        and document.get("second_reference_records") == second_reference
        and document.get("second_records") == second_reference
        and document.get("baseline_record_sha256") == digest(baseline)
        and document.get("second_record_sha256") == digest(second_reference)
        and isinstance(baseline, list)
        and isinstance(second_reference, list)
        and len(baseline) == len(second_reference) == EXPECTED_CASES
        and baseline == second_reference
        and all(isinstance(row, dict) for row in baseline)
        and all(isinstance(row, dict) for row in second_reference)
        and [row.get("id") for row in baseline]
        == [row["id"] for row in _matrix_rows()]
        and [row.get("id") for row in second_reference]
        == [row["id"] for row in _matrix_rows()]
        and document.get("candidate_cross_delegation") is False
        and document.get("mismatches") == 0
        and document.get("current_provenance") == provenance
        and document.get("benchmark_or_timing_executed") is False
        and document.get("performance_fixtures_read") == 0
        and document.get("holdout_cases_read") == 0
        and document.get("performance") == "NOT MEASURED",
        "the V14 comparison concealed its baseline, denominator, or provenance",
    )
    workers = document.get("reference_worker_reports")
    frozen.require(
        isinstance(workers, dict)
        and set(workers) == {"stdlib-a", "stdlib-b"}
        and isinstance(provenance.get("source_sha256"), str),
        "the final V14 comparison concealed an actual Python reference worker",
    )
    first_worker = _validate_reference_worker(
        workers["stdlib-a"],
        role="stdlib-a",
        source_sha256=provenance["source_sha256"],
    )
    second_worker = _validate_reference_worker(
        workers["stdlib-b"],
        role="stdlib-b",
        source_sha256=provenance["source_sha256"],
    )
    frozen.require(
        first_worker["records"] == baseline
        and second_worker["records"] == second_reference
        and first_worker["record_sha256"] == document["baseline_record_sha256"]
        and second_worker["record_sha256"] == document["second_record_sha256"],
        "the final V14 comparison forged an actual independent Python worker",
    )
    outcomes = document.get("candidate_reports")
    frozen.require(
        isinstance(outcomes, dict)
        and set(outcomes) == set(REQUIRED_CANDIDATES),
        "the V14 comparison omitted an independently executed family",
    )
    ids = [row["id"] for row in _matrix_rows()]
    for role in REQUIRED_CANDIDATES:
        result = outcomes[role]
        frozen.require(
            isinstance(result, dict)
            and result.get("candidate") == role
            and result.get("module") == "candidates." + role + "_candidate"
            and result.get("status") == "PASS"
            and result.get("cases") == EXPECTED_CASES
            and result.get("cohort_cases") == dict(stage11.COHORTS)
            and result.get("records") == baseline
            and isinstance(result.get("records"), list)
            and len(result["records"]) == EXPECTED_CASES
            and [row.get("id") for row in result["records"]] == ids
            and result.get("record_sha256") == digest(result["records"])
            and result.get("mismatches") == 0
            and result.get("failure_records") == []
            and result.get("failures_recorded") == 0
            and result.get("benchmark_or_timing_executed") is False
            and result.get("performance_fixtures_read") == 0
            and result.get("holdout_cases_read") == 0
            and result.get("performance") == "NOT MEASURED",
            "the V14 evidence concealed a real native observation: " + role,
        )
        _validate_guard(result.get("guard"), role)
        expected_native = provenance.get("native_sha256_by_family", {}).get(role)
        frozen.require(
            isinstance(expected_native, dict)
            and result.get("native_binary_sha256") == expected_native,
            "the V14 evidence substituted an actual owned native: " + role,
        )
    return document


def _persist_candidate_failure(
    *,
    role: str,
    provenance: dict[str, Any],
    reference: dict[str, Any],
    self_oracle_sha256: str,
    completed: dict[str, Any],
    observed: list[dict[str, Any]] | None = None,
    differences: list[dict[str, Any]] | None = None,
    error: BaseException | None = None,
) -> str:
    frozen.require(
        role in REQUIRED_CANDIDATES,
        "refusing to preserve an unknown V14 native-engine failure",
    )
    records = differences if differences is not None else []
    details = None
    if error is not None:
        details = (
            error.details
            if isinstance(error, stage07.PublicWorkerFailure)
            else {
                "kind": type(error).__name__,
                "exception": stage07._normalize(error),
            }
        )
    document = {
        "schema": ALL_CANDIDATE_SCHEMA + "-failure",
        "status": "FAIL",
        "result": "FAIL",
        **stage11._base_document(provenance),
        "failed_role": role,
        "expected_cases": EXPECTED_CASES,
        "reference_checks": EXPECTED_CASES * 2,
        "self_oracle_path": SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": self_oracle_sha256,
        "reference_worker_reports": reference["reference_worker_reports"],
        "baseline_records": reference["baseline_records"],
        "second_reference_records": reference["second_records"],
        "second_records": reference["second_records"],
        "baseline_record_sha256": reference["baseline_record_sha256"],
        "second_record_sha256": reference["second_record_sha256"],
        "candidate_records": observed,
        "mismatches": len(records),
        "failure_records": records,
        "failures_recorded": len(records),
        "worker_failure": details,
        "completed_candidate_reports": completed,
    }
    path = CANDIDATE_FAILURE_RELATIVES[role]
    fingerprint = stage11._exclusive_evidence(document, path)
    return path + " (sha256 " + fingerprint + ")"


def run_all_candidates() -> dict[str, Any]:
    with _stage14_context(), previous._stage12_context():
        provenance = stage11._authenticate_provenance()
        frozen.require(
            not (ROOT / ALL_CANDIDATE_RELATIVE).exists(),
            "the exclusive complete-observation V14 report already exists",
        )
        reference, self_sha256 = stage06._read_public_document(
            SELF_ORACLE_RELATIVE, expected_sha256=None,
        )
        _validate_complete_self_oracle(reference, provenance)
        baseline = reference["baseline_records"]
        second_reference = reference["second_records"]
        outcomes: dict[str, Any] = {}
        for role in REQUIRED_CANDIDATES:
            try:
                worker = stage11._run_worker(
                    role, source_sha256=provenance["source_sha256"],
                )
            except (Exception, RecursionError) as error:
                retained = _persist_candidate_failure(
                    role=role,
                    provenance=provenance,
                    reference=reference,
                    completed=outcomes,
                    self_oracle_sha256=self_sha256,
                    error=error,
                )
                raise frozen.OracleIntegrityError(
                    "the actual guarded V14 failure was preserved in " + retained
                ) from error
            differences = stage11._mismatches(baseline, worker["records"])
            outcome = {
                "candidate": role,
                "module": "candidates." + role + "_candidate",
                "status": "FAIL" if differences else "PASS",
                "cases": EXPECTED_CASES,
                "cohort_cases": dict(stage11.COHORTS),
                "records": worker["records"],
                "record_sha256": worker["record_sha256"],
                "mismatches": len(differences),
                "failure_records": differences,
                "failures_recorded": len(differences),
                "guard": worker["guard"],
                "native_binary_sha256": worker["native_binary_sha256"],
                "public_origins": worker["public_origins"],
                "benchmark_or_timing_executed": False,
                "performance_fixtures_read": 0,
                "holdout_cases_read": 0,
                "performance": "NOT MEASURED",
            }
            outcomes[role] = outcome
            if differences:
                retained = _persist_candidate_failure(
                    role=role,
                    provenance=provenance,
                    reference=reference,
                    observed=worker["records"],
                    differences=differences,
                    completed=outcomes,
                    self_oracle_sha256=self_sha256,
                )
                raise frozen.OracleIntegrityError(
                    "the actual " + role + " V14 mismatch was preserved in "
                    + retained
                )
        report = {
            "schema": ALL_CANDIDATE_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "selected": "all",
            "selected_candidates": list(REQUIRED_CANDIDATES),
            "completed_candidates": list(REQUIRED_CANDIDATES),
            "comparison_complete": True,
            **stage11._base_document(provenance),
            "cases_per_candidate": EXPECTED_CASES,
            "candidate_checks": 384,
            "reference_checks": EXPECTED_CASES * 2,
            "self_oracle_path": SELF_ORACLE_RELATIVE,
            "self_oracle_sha256": self_sha256,
            "reference_worker_reports": reference["reference_worker_reports"],
            "baseline_records": baseline,
            "second_reference_records": second_reference,
            "second_records": second_reference,
            "baseline_record_sha256": reference["baseline_record_sha256"],
            "second_record_sha256": reference["second_record_sha256"],
            "candidate_reports": outcomes,
            "candidate_cross_delegation": False,
            "mismatches": 0,
        }
        _validate_complete_candidate_report(
            report,
            baseline=baseline,
            second_reference=second_reference,
            provenance=provenance,
            self_oracle_sha256=self_sha256,
        )
        evidence_sha = stage11._exclusive_evidence(report, ALL_CANDIDATE_RELATIVE)
        return {
            "schema": ALL_CANDIDATE_SCHEMA,
            "status": "PASS",
            "cases_per_candidate": EXPECTED_CASES,
            "candidate_checks": 384,
            "completed_candidates": list(REQUIRED_CANDIDATES),
            "baseline_records_preserved": EXPECTED_CASES,
            "second_reference_records_preserved": EXPECTED_CASES,
            "reference_records_preserved": EXPECTED_CASES * 2,
            "candidate_records_preserved": 384,
            "mismatches": 0,
            "evidence": ALL_CANDIDATE_RELATIVE,
            "evidence_sha256": evidence_sha,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }


def _synthetic_guard(role: str) -> dict[str, Any]:
    return {
        "family": role,
        "enabled": True,
        "stdlib_re_blocked": True,
        "cpython_sre_blocked": True,
        "third_party_regex_blocked": True,
        "cross_family_blocked": True,
        "foreign_dynamic_libraries_blocked": True,
        "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
        "matcher_inspect_loaded": False,
        "matcher_tokenizer_loaded": False,
    }


def _synthetic_stage12_reference(
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    original = previous._synthetic_stage11_reference(matrix)
    records = original["baseline_records"]
    return {
        **original,
        "schema": "rebar-python-re-public-generic-alias-v12-self-oracle",
        "source_path": STAGE12_SOURCE_RELATIVE,
        "source_sha256": STAGE12_SOURCE_SHA256,
        "protocol_path": STAGE12_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE12_PROTOCOL_SHA256,
        "seed": 2026072471,
        "seed_domain": "rebar/python-re/public-generic-alias/v12",
        "matrix_sha256": STAGE12_MATRIX_SHA256,
        "baseline_records": records,
        "baseline_record_sha256": digest(records),
        "second_record_sha256": digest(records),
        "current_provenance": {"synthetic_only": True},
    }


def _synthetic_stage12_all(reference: dict[str, Any]) -> dict[str, Any]:
    outcomes = {}
    for role in REQUIRED_CANDIDATES:
        outcomes[role] = {
            "candidate": role,
            "module": "candidates." + role + "_candidate",
            "status": "PASS",
            "cases": EXPECTED_CASES,
            "cohort_cases": dict(stage11.COHORTS),
            "record_sha256": reference["baseline_record_sha256"],
            "mismatches": 0,
            "failure_records": [],
            "failures_recorded": 0,
            "guard": _synthetic_guard(role),
            "native_binary_sha256": {
                path: digest({"synthetic_only": True, "role": role, "path": path})
                for path in NATIVE_PATHS[role].values()
            },
            "public_origins": {
                name: {
                    "public_name": name,
                    "actual_name": name,
                    "actual_qualified_name": name,
                    "actual_module": (
                        OWNED_NATIVE_MODULES[role] if name == "Match"
                        else "candidates." + role + "_candidate"
                    ),
                }
                for name in ("Pattern", "Match")
            },
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
    return {
        "schema": "rebar-python-re-public-generic-alias-v12-all-candidates",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": STAGE12_SOURCE_RELATIVE,
        "source_sha256": STAGE12_SOURCE_SHA256,
        "protocol_path": STAGE12_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE12_PROTOCOL_SHA256,
        "seed": 2026072471,
        "seed_domain": "rebar/python-re/public-generic-alias/v12",
        "matrix_sha256": STAGE12_MATRIX_SHA256,
        "cohorts": 4,
        "cohort_cases": dict(stage11.COHORTS),
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": 384,
        "self_oracle_path": STAGE12_SELF_RELATIVE,
        "self_oracle_sha256": STAGE12_SELF_SHA256,
        "baseline_record_sha256": reference["baseline_record_sha256"],
        "candidate_cross_delegation": False,
        "candidate_reports": outcomes,
        "current_provenance": {"synthetic_only": True},
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


def _synthetic_official_failure() -> dict[str, Any]:
    return {
        "schema": "rebar-postfinal-cpython-public-locale-v2-rust-failure-v1",
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "source_path": OFFICIAL_V2_FAILURE_SOURCE_RELATIVE,
        "source_sha256": OFFICIAL_V2_FAILURE_SOURCE_SHA256,
        "protocol_path": OFFICIAL_V2_FAILURE_PROTOCOL_RELATIVE,
        "protocol_sha256": OFFICIAL_V2_FAILURE_PROTOCOL_SHA256,
        "failed_role": "rust",
        "failed_module": "candidates.rust_candidate",
        "failed_method": "ReTests.test_match_repr",
        "official_v2_status": "FAIL",
        "official_v2_complete_result_created": False,
        "official_v2_complete_result_path": (
            "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-all.json"
        ),
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
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
                "module": "candidates.rust_candidate",
                "methods": 146,
                "passed": 145,
                "failed": 1,
                "skipped": 0,
                "crashes": 0,
                "timeouts": 0,
                "failed_method": "ReTests.test_match_repr",
                "individual_method_records_preserved": False,
            },
            **{
                role: {
                    "execution": "NOT RUN",
                    "status": "NOT RUN",
                    "individual_method_records_preserved": False,
                    "inferred_pass": False,
                }
                for role in ("vm", "zig")
            },
        },
        "actual_current_provenance": {
            "official_source_path": OFFICIAL_V2_SOURCE_RELATIVE,
            "official_source_sha256": OFFICIAL_V2_SOURCE_SHA256,
            "official_protocol_path": OFFICIAL_V2_PROTOCOL_RELATIVE,
            "official_protocol_sha256": OFFICIAL_V2_PROTOCOL_SHA256,
            "source_audit_source_path": previous.V6_BASE_AUDIT_SOURCE_RELATIVE,
            "source_audit_source_sha256": previous.V6_BASE_AUDIT_SOURCE_SHA256,
            "source_audit_report_path": previous.V6_BASE_AUDIT_RELATIVE,
            "source_audit_report_sha256": previous.V6_BASE_AUDIT_SHA256,
            "strict_audit_source_path": previous.V6_STRICT_AUDIT_SOURCE_RELATIVE,
            "strict_audit_source_sha256": previous.V6_STRICT_AUDIT_SOURCE_SHA256,
            "strict_audit_report_path": previous.V6_STRICT_AUDIT_RELATIVE,
            "strict_audit_report_sha256": previous.V6_STRICT_AUDIT_SHA256,
            "selected_methods": 146,
            "corpus_cases": 403,
            "named_waiver_count": 8,
            "verified_owned_source_count": 12,
            "verified_native_binary_count": 5,
            "verified_standard_pickle_count": 48,
            "stage12": {
                "source_path": STAGE12_SOURCE_RELATIVE,
                "source_sha256": STAGE12_SOURCE_SHA256,
                "protocol_path": STAGE12_PROTOCOL_RELATIVE,
                "protocol_sha256": STAGE12_PROTOCOL_SHA256,
                "self_oracle_path": STAGE12_SELF_RELATIVE,
                "self_oracle_sha256": STAGE12_SELF_SHA256,
                "all_candidates_path": STAGE12_ALL_RELATIVE,
                "all_candidates_sha256": STAGE12_ALL_SHA256,
                "cases": 128,
                "stdlib_checks": 256,
                "candidate_checks": 384,
                "completed_candidates": list(REQUIRED_CANDIDATES),
            },
        },
        "first_run": {
            "controller": OFFICIAL_V2_SOURCE_RELATIVE,
            "exit_code": 1,
            "rerun": False,
            "failure": {
                "failed_role": "rust",
                "failed_module": "candidates.rust_candidate",
                "failed_method": "ReTests.test_match_repr",
                "exception_type": "AssertionError",
                "failure_rerun": False,
                "original_method_records_preserved": False,
                "raw_stream_bytes": "NOT RECORDED",
                "raw_stream_sha256": "NOT RECORDED",
                "actual_match_repr": (
                    "<re.Match object; span=(1, 12), match='abracadabra'>"
                ),
            },
        },
        "scope": {
            "actual_first_failure_preserved": True,
            "baseline_method_records_fabricated": False,
            "failure_reproduced_or_rerun": False,
            "raw_controller_stream_recorded": False,
            "unexecuted_candidate_results_invented": False,
            "candidate_imports": 0,
            "candidate_processes": 0,
            "official_test_processes_started": 0,
            "locale_compilations": 0,
            "benchmark_or_timing_executed": False,
            "holdout_access": False,
            "performance_fixture_access": False,
        },
    }


def _synthetic_v7_documents() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, str], dict[str, str],
]:
    source_hashes = {
        path: digest({"synthetic_only": True, "source": path})
        for paths in CORE_SOURCE_PATHS.values()
        for path in paths
    }
    native_hashes = {
        label: digest({"synthetic_only": True, "native": path})
        for paths in NATIVE_PATHS.values()
        for label, path in paths.items()
    }
    families: dict[str, Any] = {"ast": {"passed": True}}
    native_families: dict[str, Any] = {}
    source_owners: dict[str, Any] = {}
    source_matches: dict[str, Any] = {}
    strict_owners: dict[str, Any] = {}
    for role in REQUIRED_CANDIDATES:
        bridge = OWNED_NATIVE_MODULES[role]
        candidate = "candidates." + role + "_candidate"
        native = {
            path: native_hashes[label]
            for label, path in NATIVE_PATHS[role].items()
        }
        guard = _synthetic_guard(role)
        families[role] = {"passed": True}
        native_families[role] = {
            "passed": True,
            "issues": [],
            "files": {
                label.rsplit(":", 1)[-1]: {
                    "file": path,
                    "sha256": native_hashes[label],
                }
                for label, path in NATIVE_PATHS[role].items()
            },
        }
        pickle_rows = []
        owner_rows = []
        for origin in ("Pattern", "Match"):
            for argument in ("str", "bytes"):
                for label, protocol in (
                    ("protocol-0", 0), ("protocol-2", 2),
                    ("protocol-4", 4),
                    ("highest-protocol", stage11.pickle.HIGHEST_PROTOCOL),
                ):
                    pickle_rows.append({
                        "origin": origin,
                        "argument": argument,
                        "protocol": protocol,
                        "passed": True,
                    })
                    owner_rows.append({
                        "id": origin + ":" + argument + ":" + label,
                        "origin": origin,
                        "argument": argument,
                        "protocol_name": label,
                        "protocol": protocol,
                        "passed": True,
                        "genuine_generic_alias": True,
                        "same_owned_native_origin": True,
                        "standard_pickle_round_trip": True,
                    })
        public = {
            name: {
                "module": bridge if name == "Match" else candidate,
                "name": name,
                "qualified_name": name,
                "genuinely_importable": True,
            }
            for name in ("Pattern", "Match")
        }
        repr_rows = []
        for kind, pattern, subject, matched in (
            ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
            ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
        ):
            actual = (
                "<" + bridge + ".Match object; span=(1, 12), match="
                + repr(matched) + ">"
            )
            repr_rows.append({
                "id": role + ":match-repr:" + kind,
                "role": role,
                "kind": kind,
                "match_module": bridge,
                "match_type_module": bridge,
                "match_qualified_name": "Match",
                "match_type_qualified_name": "Match",
                "span": [1, 12],
                "pattern_representation": repr(pattern),
                "subject_representation": repr(subject),
                "matched_representation": repr(matched),
                "actual_repr": actual,
                "observed_repr": actual,
                "expected_repr": actual,
                "native_type_identity": True,
                "genuine_matching_executed": True,
                "passed": True,
            })
        source_owners[role] = {
            "schema": previous.V6_BASE_AUDIT_SCHEMA + "-owned-types",
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "family": role,
            "candidate_module": candidate,
            "native_bridge_module": bridge,
            "native_sha256": native,
            "standard_pickle_checks": 16,
            "public_types": {
                name: {
                    **values,
                    "native_bridge_module": bridge,
                    "candidate_identity": True,
                    "native_bridge_identity": name == "Match",
                }
                for name, values in public.items()
            },
            "records": owner_rows,
            "guard": dict(guard),
            "loaded_candidate_modules": sorted({candidate, bridge}),
            "candidate_regex_matching_executed": False,
            "third_party_regex_packages": 0,
            "benchmark_or_timing_executed": False,
            "fixture_accessed": False,
        }
        source_matches[role] = {
            "schema": V7_BASE_AUDIT_SCHEMA + "-match-repr-worker",
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "family": role,
            "candidate_module": candidate,
            "native_bridge_module": bridge,
            "native_binary_sha256": native,
            "guard": dict(guard),
            "loaded_candidate_modules": sorted({candidate, bridge}),
            "records": stage11.copy.deepcopy(repr_rows),
            "match_repr_checks": 2,
            "genuine_matching_executed": True,
            "external_regex_packages": 0,
            "benchmark_or_timing_executed": False,
            "fixture_accessed": False,
        }
        strict_owners[role] = {
            "schema": "rebar-postfinal-no-delegation-public-owner-worker-v7",
            "status": "PASS",
            "role": role,
            "public_type_ownership": public,
            "standard_pickle_checks": pickle_rows,
            "standard_pickle_check_count": 16,
            "native_binary_sha256": native,
            "guard": dict(guard),
            "cached_json_decoder_regex_blocked": True,
            "loaded_candidate_modules": sorted({candidate, bridge}),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "match_representation_checks": repr_rows,
            "match_representation_check_count": 2,
            "match_repr_checks": 2,
            "genuine_matching_executed": True,
        }
    native_proof = {
        "passed": True,
        "issues": [],
        "expected_binary_count": 5,
        "audited_binary_count": 5,
        "families": native_families,
    }
    manifest = {
        "passed": True,
        "issues": [],
        "python_dependencies": [],
        "rust_third_party_dependency_count": 0,
    }
    base = {
        "schema": V7_BASE_AUDIT_SCHEMA,
        "postfinal_schema": V7_BASE_AUDIT_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": V7_BASE_AUDIT_SOURCE_RELATIVE,
        "audit_source_sha256": "a" * 64,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_candidate_source_paths": list(source_hashes),
        "verified_native_role_count": 5,
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": 48,
        "match_repr_checks_per_family": 2,
        "verified_match_repr_checks": 6,
        "historical_stage12_only": True,
        "stage12_candidate_results_qualify_current_sources": False,
        "official_v2_rust_failure_path": OFFICIAL_V2_FAILURE_RELATIVE,
        "official_v2_rust_failure_sha256": OFFICIAL_V2_FAILURE_SHA256,
        "official_v2_rust_failure_historical": True,
        "previous_v6_audit_source_path": previous.V6_BASE_AUDIT_SOURCE_RELATIVE,
        "previous_v6_audit_source_sha256": previous.V6_BASE_AUDIT_SOURCE_SHA256,
        "previous_v6_audit_report_path": previous.V6_BASE_AUDIT_RELATIVE,
        "previous_v6_audit_report_sha256": previous.V6_BASE_AUDIT_SHA256,
        "previous_v6_report_historical": True,
        "previous_v6_strict_audit_source_path": (
            previous.V6_STRICT_AUDIT_SOURCE_RELATIVE
        ),
        "previous_v6_strict_audit_source_sha256": (
            previous.V6_STRICT_AUDIT_SOURCE_SHA256
        ),
        "previous_v6_strict_audit_report_path": previous.V6_STRICT_AUDIT_RELATIVE,
        "previous_v6_strict_audit_report_sha256": previous.V6_STRICT_AUDIT_SHA256,
        "previous_v6_strict_report_historical": True,
        "families": families,
        "manifest_provenance": manifest,
        "native_elf_provenance": native_proof,
        "public_type_ownership": source_owners,
        "public_match_repr": source_matches,
    }
    strict = {
        "schema": V7_STRICT_AUDIT_SCHEMA,
        "postfinal_schema": V7_STRICT_AUDIT_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": V7_STRICT_AUDIT_SOURCE_RELATIVE,
        "audit_source_sha256": "b" * 64,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_public_type_family_count": 3,
        "verified_standard_pickle_count": 48,
        "verified_match_repr_checks": 6,
        "base_audit_source_path": V7_BASE_AUDIT_SOURCE_RELATIVE,
        "base_audit_source_sha256": "a" * 64,
        "base_audit_report_path": V7_BASE_AUDIT_RELATIVE,
        "base_audit_report_sha256": "c" * 64,
        "base_audit_postfinal_schema": V7_BASE_AUDIT_SCHEMA,
        "previous_v6_audit_source_path": previous.V6_STRICT_AUDIT_SOURCE_RELATIVE,
        "previous_v6_audit_source_sha256": previous.V6_STRICT_AUDIT_SOURCE_SHA256,
        "previous_v6_audit_report_path": previous.V6_STRICT_AUDIT_RELATIVE,
        "previous_v6_audit_report_sha256": previous.V6_STRICT_AUDIT_SHA256,
        "previous_v6_report_historical": True,
        "previous_v6_source_audit_source_path": (
            previous.V6_BASE_AUDIT_SOURCE_RELATIVE
        ),
        "previous_v6_source_audit_source_sha256": (
            previous.V6_BASE_AUDIT_SOURCE_SHA256
        ),
        "previous_v6_source_audit_report_path": previous.V6_BASE_AUDIT_RELATIVE,
        "previous_v6_source_audit_report_sha256": previous.V6_BASE_AUDIT_SHA256,
        "previous_v6_source_report_historical": True,
        "official_v2_failure_provenance": {
            "path": OFFICIAL_V2_FAILURE_RELATIVE,
            "sha256": OFFICIAL_V2_FAILURE_SHA256,
            "status": "FAIL",
            "result": "FAIL",
            "failed_role": "rust",
            "failed_method": "ReTests.test_match_repr",
            "historical": True,
            "qualifies_current_engines": False,
        },
        "official_v2_failure_preserved": True,
        "official_v2_failure_qualifies_current_engines": False,
        "families": stage11.copy.deepcopy(families),
        "manifest_provenance": stage11.copy.deepcopy(manifest),
        "native_elf_provenance": stage11.copy.deepcopy(native_proof),
        "qualified_source_fingerprints": source_hashes,
        "native_elf_fingerprints": native_hashes,
        "public_type_ownership": strict_owners,
        "public_match_repr": stage11.copy.deepcopy(source_matches),
        "strict_public_match_repr": stage11.copy.deepcopy(strict_owners),
    }
    return base, strict, source_hashes, native_hashes


def _synthetic_official_v3_report(
    source_fingerprints: dict[str, str],
    native_fingerprints: dict[str, str],
) -> dict[str, Any]:
    names = [
        "ReTests.test_match_repr",
        "ReTests.test_locale_caching",
        "ReTests.test_locale_compiled",
        *["SyntheticOfficial.test_" + str(index) for index in range(143)],
    ]
    records = [
        {"test": name, "status": "passed", "skipped": 0, "reason": None}
        for name in names
    ]
    roles = {
        role: {
            "module": (
                "re" if role == "re" else "candidates." + role + "_candidate"
            ),
            "methods": 146,
            "passed": 146,
            "failed": 0,
            "failures": 0,
            "errors": 0,
            "crashes": 0,
            "skipped": 0,
            "timeouts": 0,
            "locale_caching_passed": True,
            "locale_compiled_passed": True,
            "holdout_accessed": False,
            "timing_performed": False,
            "performance": "NOT MEASURED",
            "records": stage11.copy.deepcopy(records),
        }
        for role in ("re", *REQUIRED_CANDIDATES)
    }
    return {
        "schema": OFFICIAL_V3_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": OFFICIAL_V3_SOURCE_RELATIVE,
        "source_sha256": OFFICIAL_V3_SOURCE_SHA256,
        "goal_sha256": GOAL_SHA256,
        "qualified_source_fingerprints": source_fingerprints,
        "native_elf_fingerprints": native_fingerprints,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
        "audits": {
            "from_scratch": {
                "path": V7_BASE_AUDIT_RELATIVE,
                "postfinal_schema": V7_BASE_AUDIT_SCHEMA,
                "sha256": V7_BASE_AUDIT_SHA256,
                "source_path": V7_BASE_AUDIT_SOURCE_RELATIVE,
                "source_sha256": V7_BASE_AUDIT_SOURCE_SHA256,
            },
            "no_delegation": {
                "path": V7_STRICT_AUDIT_RELATIVE,
                "postfinal_schema": V7_STRICT_AUDIT_SCHEMA,
                "sha256": V7_STRICT_AUDIT_SHA256,
                "source_path": V7_STRICT_AUDIT_SOURCE_RELATIVE,
                "source_sha256": V7_STRICT_AUDIT_SOURCE_SHA256,
            },
        },
        "original_oracle": {
            "selected_methods": 146,
            "total_public_methods": 152,
            "corpus_cases": 403,
            "selected_method_sha256": OFFICIAL_V3_SELECTED_METHOD_SHA256,
            "runner_path": "tools/cpython_re_oracle.py",
            "runner_sha256": (
                "d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb"
            ),
            "manifest_path": "oracle/cpython-3.14.6/manifest.json",
            "manifest_sha256": (
                "2c89ce37e474cb6f59d61f86ad810662b50b83bbdce3610c04523fe092688597"
            ),
            "all_named_waivers": {
                name: "SYNTHETIC ONLY"
                for name in (
                    "DebugTests",
                    "ImplementationTest",
                    "ReTests.test_large_search",
                    "ReTests.test_large_subn",
                    "ReTests.test_memory_leaks",
                    "ReTests.test_re_groupref_overflow",
                    "ReTests.test_regression_gh94675",
                    "ReTests.test_search_anchor_at_beginning",
                )
            },
        },
        "roles": roles,
        "official_scope": {
            "genuine_official_methods_per_engine": 146,
            "original_public_methods": 152,
            "original_upstream_corpus_cases": 403,
            "real_locale_methods_per_engine": 2,
            "independently_run_engine_count": 4,
            "verified_owned_source_count": 12,
            "verified_native_binary_count": 5,
            "verified_standard_pickle_count": 48,
            "verified_real_native_match_repr_count": 6,
            "named_waiver_count": 8,
            "genuine_official_v2_rust_failure_preserved": True,
            "official_v2_success_report_exists": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "locale_reference": {
            "status": "PASS",
            "python": "3.14.6",
            "candidate_modules_loaded": False,
            "genuine_locales": True,
            "compiled_locale_switch": True,
            "holdout_accessed": False,
            "timing_performed": False,
        },
        "locales": {
            "genuine": True,
            "private": True,
            "holdout_accessed": False,
            "timing_performed": False,
            "performance": "NOT MEASURED",
            "utf8": {"name": "en_US.utf8"},
            "iso88591": {"name": "en_US.iso88591"},
        },
        "supersedes": {
            "version_two": {
                "source_path": OFFICIAL_V2_SOURCE_RELATIVE,
                "source_sha256": OFFICIAL_V2_SOURCE_SHA256,
                "protocol_path": OFFICIAL_V2_PROTOCOL_RELATIVE,
                "protocol_sha256": OFFICIAL_V2_PROTOCOL_SHA256,
                "failure_source_path": OFFICIAL_V2_FAILURE_SOURCE_RELATIVE,
                "failure_source_sha256": OFFICIAL_V2_FAILURE_SOURCE_SHA256,
                "failure_protocol_path": OFFICIAL_V2_FAILURE_PROTOCOL_RELATIVE,
                "failure_protocol_sha256": OFFICIAL_V2_FAILURE_PROTOCOL_SHA256,
                "failure_report_path": OFFICIAL_V2_FAILURE_RELATIVE,
                "failure_report_sha256": OFFICIAL_V2_FAILURE_SHA256,
                "failed_role": "rust",
                "failed_method": "ReTests.test_match_repr",
                "rust_passed": 145,
                "rust_methods": 146,
                "c_official": "NOT RUN",
                "zig_official": "NOT RUN",
                "official_all_report_exists": False,
                "historical": True,
                "qualifies_current_sources": False,
            },
        },
    }


def _synthetic_reference_worker(
    role: str,
    records: list[dict[str, Any]],
    source_sha256: str,
) -> dict[str, Any]:
    frozen.require(
        role in ("stdlib-a", "stdlib-b"),
        "an in-memory Python reference requested an invalid role",
    )
    actual = stage11.copy.deepcopy(records)
    return {
        "schema": WORKER_SCHEMA,
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_sha256": source_sha256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cases": EXPECTED_CASES,
        "cohort_cases": dict(stage11.COHORTS),
        "records": actual,
        "record_sha256": digest(actual),
        "guard": {"baseline_only": True, "candidate_imported": False},
        "native_binary_sha256": {},
        "public_origins": {
            name: {
                "public_name": name,
                "actual_name": name,
                "actual_qualified_name": name,
                "actual_module": "re",
            }
            for name in ("Pattern", "Match")
        },
        "inspect_loaded": False,
        "tokenize_loaded": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


def _synthetic_complete_self_oracle(
    records: list[dict[str, Any]],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    source_sha256 = provenance.get("source_sha256")
    frozen.require(
        isinstance(source_sha256, str)
        and official_locale.is_sha256(source_sha256),
        "an in-memory dual reference omitted its source-bound fingerprint",
    )
    first = _synthetic_reference_worker("stdlib-a", records, source_sha256)
    second = _synthetic_reference_worker("stdlib-b", records, source_sha256)
    first_records = first["records"]
    second_records = second["records"]
    return {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": len(stage11.COHORTS),
        "cohort_cases": dict(stage11.COHORTS),
        "current_provenance": provenance,
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "reference_worker_reports": {
            "stdlib-a": first,
            "stdlib-b": second,
        },
        "baseline_records": first_records,
        "second_records": second_records,
        "baseline_record_sha256": digest(first_records),
        "second_record_sha256": digest(second_records),
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


_INSPECT_PRESENT_AT_IMPORT = "inspect" in sys.modules
_TOKENIZE_PRESENT_AT_IMPORT = "tokenize" in sys.modules


def self_test() -> dict[str, Any]:
    frozen.candidate_free()
    with stage06.previous._candidate_free_file_and_timing_guard() as effects:
        checks: list[dict[str, Any]] = []

        def check(name: str, condition: Any) -> None:
            frozen.require(condition, "V14 candidate-free control failed: " + name)
            checks.append({"name": name, "passed": True})

        def reject(name: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (
                frozen.OracleIntegrityError, AssertionError, AttributeError,
                ImportError, KeyError, OSError, TypeError, UnicodeError, ValueError,
            ):
                check(name, True)
                return
            check(name, False)

        matrix = build_matrix()
        check("exactly-128-public-behaviors", len(matrix) == EXPECTED_CASES)
        check("fresh-v14-seed", SEED == 2026072481)
        check(
            "fresh-v14-independent-domain",
            SEED_DOMAIN == "rebar/python-re/public-generic-alias/v14",
        )
        check("fresh-v14-matrix-is-exactly-frozen", digest(matrix) == MATRIX_SHA256)
        check(
            "v14-matrix-does-not-reuse-v11-or-v12",
            MATRIX_SHA256 not in {STAGE11_MATRIX_SHA256, STAGE12_MATRIX_SHA256},
        )
        check(
            "all-128-public-case-identities-are-distinct",
            len({row["id"] for row in matrix}) == EXPECTED_CASES,
        )
        for name, count in stage11.COHORTS:
            check(
                "complete-public-cohort-" + name,
                sum(row["cohort"] == name for row in matrix) == count,
            )
        check("all-ten-ordinary-public-observations", len(stage11.NORMAL_ACTIONS) == 10)
        check("all-eight-unusual-type-arguments", len(stage11.DIVERSE_ARGUMENTS) == 8)
        check("all-four-public-type-rejections", len(stage11.REJECTION_ACTIONS) == 4)
        check("all-six-copy-and-pickle-lifecycles", len(stage11.LIFECYCLE_ACTIONS) == 6)
        check(
            "ordinary-standard-python-pickle-is-unmodified",
            stage11.pickle.dumps.__module__ in ("_pickle", "pickle")
            and stage11.pickle.loads.__module__ in ("_pickle", "pickle"),
        )
        check(
            "genuine-typing-type-variable-is-retained",
            isinstance(stage11.TYPE_PARAMETER, stage11.typing.TypeVar),
        )
        check(
            "all-five-unowned-native-loaders-remain-blocked",
            stage07.NATIVE_LOADER_ALIASES == (
                "ctypes.CDLL", "ctypes.cdll.LoadLibrary",
                "ctypes.cdll._dlltype", "ctypes._dlopen", "_ctypes.dlopen",
            ),
        )
        check(
            "three-from-scratch-families-remain-mandatory",
            REQUIRED_CANDIDATES == stage11.REQUIRED_CANDIDATES,
        )
        check(
            "all-twelve-repaired-native-source-paths-are-declared",
            sum(map(len, CORE_SOURCE_PATHS.values())) == 12,
        )
        check(
            "all-five-repaired-native-engine-paths-are-declared",
            sum(map(len, NATIVE_PATHS.values())) == 5,
        )
        check(
            "v7-base-producer-is-authenticated-with-its-actual-hash",
            V7_BASE_AUDIT_SOURCE_SHA256
            == "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487",
        )
        check(
            "fresh-v7-audits-cannot-reuse-historical-v6-destinations",
            {
                V7_BASE_AUDIT_RELATIVE, V7_STRICT_AUDIT_RELATIVE,
            }.isdisjoint({
                previous.V6_BASE_AUDIT_RELATIVE,
                previous.V6_STRICT_AUDIT_RELATIVE,
            }),
        )
        if any(value is None for value in (
            V7_BASE_AUDIT_SOURCE_SHA256, V7_BASE_AUDIT_SHA256,
            V7_STRICT_AUDIT_SOURCE_SHA256, V7_STRICT_AUDIT_SHA256,
        )):
            reject(
                "unpublished-v7-proofs-cannot-authorize-a-candidate",
                _require_pinned_v7_audits,
            )
        else:
            check(
                "all-four-genuine-v7-source-and-report-pins-are-complete",
                all(official_locale.is_sha256(value) for value in (
                    V7_BASE_AUDIT_SOURCE_SHA256, V7_BASE_AUDIT_SHA256,
                    V7_STRICT_AUDIT_SOURCE_SHA256, V7_STRICT_AUDIT_SHA256,
                )),
            )

        base, strict, source_hashes, native_hashes = _synthetic_v7_documents()

        def validate_pair(left: Any, right: Any) -> Any:
            return _validate_v7_audit_identities(
                left,
                right,
                base_source_sha256="a" * 64,
                strict_source_sha256="b" * 64,
                base_report_sha256="c" * 64,
            )

        verified_sources, verified_natives = validate_pair(base, strict)
        check(
            "fresh-cross-audit-binds-all-twelve-repaired-source-identities",
            {
                path: value
                for records in verified_sources.values()
                for path, value in records.items()
            } == source_hashes,
        )
        check(
            "fresh-cross-audit-binds-all-five-native-path-identities",
            all(
                verified_natives[role] == {
                    path: native_hashes[label]
                    for label, path in NATIVE_PATHS[role].items()
                }
                for role in REQUIRED_CANDIDATES
            ),
        )
        check(
            "all-48-standard-pickle-controls-are-independently-owned",
            sum(
                len(base["public_type_ownership"][role]["records"])
                for role in REQUIRED_CANDIDATES
            ) == 48,
        )
        check(
            "all-six-real-string-and-bytes-match-representations-are-bound",
            sum(
                len(base["public_match_repr"][role]["records"])
                for role in REQUIRED_CANDIDATES
            ) == 6,
        )
        synthetic_official_v3 = _synthetic_official_v3_report(
            source_hashes, native_hashes,
        )
        _validate_official_v3_report(
            synthetic_official_v3,
            source_fingerprints=source_hashes,
            native_fingerprints=native_hashes,
        )
        check(
            "preserves-all-584-real-official-python-and-candidate-methods",
            sum(
                len(synthetic_official_v3["roles"][role]["records"])
                for role in ("re", *REQUIRED_CANDIDATES)
            ) == 584,
        )
        check(
            "official-v3-current-source-and-audit-ownership-is-bound",
            synthetic_official_v3["qualified_source_fingerprints"]
            == source_hashes
            and synthetic_official_v3["native_elf_fingerprints"]
            == native_hashes,
        )
        check(
            "official-v3-pass-preserves-the-genuine-v2-rust-failure",
            synthetic_official_v3["supersedes"]["version_two"][
                "failure_report_sha256"
            ] == OFFICIAL_V2_FAILURE_SHA256,
        )
        for field, poisoned in (
            ("schema", "rebar-postfinal-cpython-public-locale-v2"),
            ("status", "FAIL"),
            ("result", "FAIL"),
            ("source_path", OFFICIAL_V2_SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("goal_sha256", "0" * 64),
            ("holdout_accessed", True),
            ("timing_performed", True),
            ("performance", "MEASURED"),
        ):
            reject(
                "rejects-fabricated-official-v3-result-" + field,
                lambda field=field, poisoned=poisoned: (
                    _validate_official_v3_report(
                        {**synthetic_official_v3, field: poisoned},
                        source_fingerprints=source_hashes,
                        native_fingerprints=native_hashes,
                    )
                ),
            )
        for role in ("re", *REQUIRED_CANDIDATES):
            for field, poisoned in (
                ("passed", 145), ("failed", 1), ("skipped", 1),
                ("crashes", 1), ("locale_caching_passed", False),
                ("locale_compiled_passed", False),
            ):
                changed = stage11.copy.deepcopy(synthetic_official_v3)
                changed["roles"][role][field] = poisoned
                reject(
                    "rejects-weakened-official-v3-" + role + "-" + field,
                    lambda document=changed: _validate_official_v3_report(
                        document,
                        source_fingerprints=source_hashes,
                        native_fingerprints=native_hashes,
                    ),
                )
            omitted = stage11.copy.deepcopy(synthetic_official_v3)
            omitted["roles"][role]["records"].pop()
            reject(
                "rejects-concealed-official-v3-method-" + role,
                lambda document=omitted: _validate_official_v3_report(
                    document,
                    source_fingerprints=source_hashes,
                    native_fingerprints=native_hashes,
                ),
            )
        hidden_failure = stage11.copy.deepcopy(synthetic_official_v3)
        hidden_failure["supersedes"]["version_two"]["rust_passed"] = 146
        reject(
            "rejects-concealed-real-official-v2-rust-failure-in-v3",
            lambda: _validate_official_v3_report(
                hidden_failure,
                source_fingerprints=source_hashes,
                native_fingerprints=native_hashes,
            ),
        )
        changed_official_sources = dict(source_hashes)
        changed_official_sources[next(iter(changed_official_sources))] = "0" * 64
        reject(
            "rejects-stale-official-v3-current-native-owned-source",
            lambda: _validate_official_v3_report(
                synthetic_official_v3,
                source_fingerprints=changed_official_sources,
                native_fingerprints=native_hashes,
            ),
        )
        changed_official_natives = dict(native_hashes)
        changed_official_natives[next(iter(changed_official_natives))] = "0" * 64
        reject(
            "rejects-stale-official-v3-current-native-binary",
            lambda: _validate_official_v3_report(
                synthetic_official_v3,
                source_fingerprints=source_hashes,
                native_fingerprints=changed_official_natives,
            ),
        )
        for field, poisoned in (
            ("schema", previous.V6_BASE_AUDIT_SCHEMA),
            ("postfinal_schema", previous.V6_BASE_AUDIT_SCHEMA),
            ("audit_source_path", previous.V6_BASE_AUDIT_SOURCE_RELATIVE),
            ("audit_source_sha256", "0" * 64),
            ("verified_core_family_count", 2),
            ("verified_distinct_pipeline_count", 3),
            ("verified_candidate_source_count", 11),
            ("verified_native_role_count", 4),
            ("standard_pickle_checks", 47),
            ("verified_match_repr_checks", 5),
            ("historical_stage12_only", False),
            ("stage12_candidate_results_qualify_current_sources", True),
            ("official_v2_rust_failure_sha256", "0" * 64),
            ("previous_v6_report_historical", False),
        ):
            reject(
                "rejects-forged-v7-source-proof-" + field,
                lambda field=field, poisoned=poisoned: validate_pair(
                    {**base, field: poisoned}, strict,
                ),
            )
        for field, poisoned in (
            ("schema", previous.V6_STRICT_AUDIT_SCHEMA),
            ("postfinal_schema", previous.V6_STRICT_AUDIT_SCHEMA),
            ("audit_source_path", previous.V6_STRICT_AUDIT_SOURCE_RELATIVE),
            ("audit_source_sha256", "0" * 64),
            ("base_audit_source_path", previous.V6_BASE_AUDIT_SOURCE_RELATIVE),
            ("base_audit_source_sha256", "0" * 64),
            ("base_audit_report_path", previous.V6_BASE_AUDIT_RELATIVE),
            ("base_audit_report_sha256", "0" * 64),
            ("base_audit_postfinal_schema", previous.V6_BASE_AUDIT_SCHEMA),
            ("verified_public_type_family_count", 2),
            ("verified_standard_pickle_count", 47),
            ("verified_match_repr_checks", 5),
            ("official_v2_failure_preserved", False),
            ("official_v2_failure_qualifies_current_engines", True),
            ("previous_v6_report_historical", False),
        ):
            reject(
                "rejects-forged-v7-no-delegation-proof-" + field,
                lambda field=field, poisoned=poisoned: validate_pair(
                    base, {**strict, field: poisoned},
                ),
            )
        for role in REQUIRED_CANDIDATES:
            no_source = dict(source_hashes)
            no_source.pop(CORE_SOURCE_PATHS[role][0])
            reject(
                "rejects-omitted-current-" + role + "-source",
                lambda values=no_source: validate_pair(
                    base, {**strict, "qualified_source_fingerprints": values},
                ),
            )
            no_native = dict(native_hashes)
            no_native.pop(next(iter(NATIVE_PATHS[role])))
            reject(
                "rejects-omitted-current-" + role + "-native-engine",
                lambda values=no_native: validate_pair(
                    base, {**strict, "native_elf_fingerprints": values},
                ),
            )
            no_owner = dict(base["public_type_ownership"])
            no_owner.pop(role)
            reject(
                "rejects-omitted-source-owned-public-types-" + role,
                lambda values=no_owner: validate_pair(
                    {**base, "public_type_ownership": values}, strict,
                ),
            )
            no_match = dict(base["public_match_repr"])
            no_match.pop(role)
            reject(
                "rejects-omitted-source-owned-match-representation-" + role,
                lambda values=no_match: validate_pair(
                    {**base, "public_match_repr": values}, strict,
                ),
            )
            fake_owner = stage11.copy.deepcopy(strict["public_type_ownership"])
            fake_owner[role]["public_type_ownership"]["Match"]["module"] = "re"
            reject(
                "rejects-delegated-standard-library-match-owner-" + role,
                lambda values=fake_owner: validate_pair(
                    base,
                    {
                        **strict,
                        "public_type_ownership": values,
                        "strict_public_match_repr": values,
                    },
                ),
            )
            fake_repr = stage11.copy.deepcopy(base["public_match_repr"])
            fake_repr[role]["records"][0]["actual_repr"] = (
                "<re.Match object; span=(1, 12), match='abracadabra'>"
            )
            reject(
                "rejects-genuinely-failed-hardcoded-standard-library-repr-"
                + role,
                lambda values=fake_repr: validate_pair(
                    {**base, "public_match_repr": values},
                    {**strict, "public_match_repr": values},
                ),
            )
            missing_pickle = stage11.copy.deepcopy(base["public_type_ownership"])
            missing_pickle[role]["records"].pop()
            reject(
                "rejects-omitted-genuine-standard-pickle-control-" + role,
                lambda values=missing_pickle: validate_pair(
                    {**base, "public_type_ownership": values}, strict,
                ),
            )
        changed_manifest = {**strict["manifest_provenance"], "synthetic": True}
        reject(
            "rejects-disagreeing-source-and-strict-package-manifests",
            lambda: validate_pair(
                base, {**strict, "manifest_provenance": changed_manifest},
            ),
        )
        changed_native = stage11.copy.deepcopy(strict["native_elf_provenance"])
        changed_native["families"]["rust"]["files"]["native-bridge"][
            "sha256"
        ] = "0" * 64
        reject(
            "rejects-disagreeing-cross-audit-native-binaries",
            lambda: validate_pair(
                base, {**strict, "native_elf_provenance": changed_native},
            ),
        )
        swapped = dict(native_hashes)
        rust_labels = list(NATIVE_PATHS["rust"])
        swapped[rust_labels[0]], swapped[rust_labels[1]] = (
            swapped[rust_labels[1]], swapped[rust_labels[0]],
        )
        reject(
            "rejects-swapped-repaired-native-path-fingerprints",
            lambda: validate_pair(
                base, {**strict, "native_elf_fingerprints": swapped},
            ),
        )

        v11_reference = previous._synthetic_stage11_reference(matrix)
        previous._validate_preserved_stage11_reference(v11_reference)
        check("preserves-all-128-actual-historical-v11-reference-identities", True)
        v11_failure = previous._synthetic_stage11_failure(v11_reference)
        previous._validate_preserved_stage11_failure(v11_failure, v11_reference)
        check("preserves-all-16-genuine-v11-rust-pickle-failures", True)
        for name, replacement in (
            ("status", "PASS"), ("failed_role", "vm"),
            ("mismatches", 15), ("failures_recorded", 15),
            ("performance", "MEASURED"),
        ):
            reject(
                "rejects-fabricated-historical-v11-" + name,
                lambda name=name, replacement=replacement: (
                    previous._validate_preserved_stage11_failure(
                        {**v11_failure, name: replacement}, v11_reference,
                    )
                ),
            )
        v12_reference = _synthetic_stage12_reference(matrix)
        _validate_stage12_reference(v12_reference)
        check("preserves-all-256-genuine-historical-v12-python-checks", True)
        v12_all = _synthetic_stage12_all(v12_reference)
        _validate_stage12_all(v12_all, v12_reference)
        check("preserves-all-384-genuine-historical-v12-candidate-checks", True)
        for name, replacement in (
            ("status", "FAIL"), ("cases", 127), ("stdlib_checks", 255),
            ("matrix_sha256", "0" * 64),
            ("candidate_imports", 1), ("performance", "MEASURED"),
        ):
            reject(
                "rejects-fabricated-historical-v12-reference-" + name,
                lambda name=name, replacement=replacement: (
                    _validate_stage12_reference(
                        {**v12_reference, name: replacement},
                    )
                ),
            )
        for name, replacement in (
            ("status", "FAIL"), ("candidate_checks", 383),
            ("self_oracle_sha256", "0" * 64),
            ("candidate_cross_delegation", True),
            ("performance", "MEASURED"),
        ):
            reject(
                "rejects-fabricated-historical-v12-candidates-" + name,
                lambda name=name, replacement=replacement: (
                    _validate_stage12_all(
                        {**v12_all, name: replacement}, v12_reference,
                    )
                ),
            )
        for role in REQUIRED_CANDIDATES:
            omitted = dict(v12_all["candidate_reports"])
            omitted.pop(role)
            reject(
                "rejects-omitted-actually-passing-historical-v12-" + role,
                lambda values=omitted: _validate_stage12_all(
                    {**v12_all, "candidate_reports": values}, v12_reference,
                ),
            )

        official_failure = _synthetic_official_failure()
        _validate_official_v2_failure(official_failure)
        check("preserves-genuine-145-of-146-official-rust-failure", True)
        check(
            "never-invents-an-unrecorded-official-python-baseline",
            official_failure["roles"]["re"]["status"] == "NOT RECORDED",
        )
        check(
            "never-invents-official-c-or-zig-results",
            all(
                official_failure["roles"][role]["execution"] == "NOT RUN"
                for role in ("vm", "zig")
            ),
        )
        for name, replacement in (
            ("status", "PASS"), ("failed_role", "zig"),
            ("failed_method", "ReTests.test_search"),
            ("official_v2_status", "PASS"),
            ("official_v2_complete_result_created", True),
            ("performance", "MEASURED"), ("timing_performed", True),
            ("holdout_accessed", True),
        ):
            reject(
                "rejects-fabricated-official-v2-failure-" + name,
                lambda name=name, replacement=replacement: (
                    _validate_official_v2_failure(
                        {**official_failure, name: replacement},
                    )
                ),
            )
        for role, mutation in (
            ("re", {"status": "PASS", "inferred_pass": True}),
            ("rust", {"passed": 146, "failed": 0, "status": "PASS"}),
            ("vm", {"execution": "EXECUTED", "status": "PASS"}),
            ("zig", {"execution": "EXECUTED", "status": "PASS"}),
        ):
            poisoned = stage11.copy.deepcopy(official_failure)
            poisoned["roles"][role].update(mutation)
            reject(
                "rejects-fabricated-official-v2-role-" + role,
                lambda document=poisoned: _validate_official_v2_failure(document),
            )

        fake_reference = stage11._synthetic_module("rebar_stage14_synthetic_reference")
        fake_owned = stage11._synthetic_module("rebar_stage14_synthetic_owned")
        comparable = [
            row for row in matrix if not row["action"].startswith("pickle-")
        ]
        check(
            "honest-native-owner-normalization-never-fabricates-a-mismatch",
            len(comparable) == 112
            and [stage11.evaluate_case(fake_reference, row) for row in comparable]
            == [stage11.evaluate_case(fake_owned, row) for row in comparable],
        )
        forged = stage11._synthetic_module(
            "rebar_stage14_synthetic_foreign", forged=True,
        )
        observation = stage11.evaluate_case(forged, matrix[1])
        check(
            "foreign-public-alias-origin-cannot-pass-normalization",
            observation.get("status") == "returned"
            and observation.get("value", {}).get("same_public_origin") is False
            and observation.get("value", {}).get("origin", {}).get("name")
            == "list",
        )
        for index, poisoned in enumerate((
            matrix[:-1], matrix[1:], list(reversed(matrix)),
            [matrix[0], *matrix[:-1]],
            [{**matrix[0], "action": "concealed"}, *matrix[1:]],
            [{**matrix[0], "origin": "foreign"}, *matrix[1:]],
            [{**matrix[0], "argument": "foreign"}, *matrix[1:]],
            [{**matrix[0], "seed": "0" * 64}, *matrix[1:]],
            [{**matrix[0], "cohort": "foreign"}, *matrix[1:]],
            [{**matrix[0], "id": matrix[1]["id"]}, *matrix[1:]],
        )):
            reject(
                "rejects-mutated-frozen-v14-public-case-" + str(index),
                lambda value=poisoned: validate_matrix(value),
            )

        saved_v12 = (
            previous.SOURCE_RELATIVE,
            previous.PROTOCOL_RELATIVE,
            previous.MATRIX_SHA256,
            previous.WORKER_BOOTSTRAP,
            previous.APPROVED_OUTPUTS,
            previous.build_matrix,
        )
        saved_v11 = (
            stage11.SOURCE_RELATIVE,
            stage11.PROTOCOL_RELATIVE,
            stage11.MATRIX_SHA256,
            stage11.WORKER_BOOTSTRAP,
            stage11.APPROVED_OUTPUTS,
            stage11.build_matrix,
        )
        with _stage14_context():
            check(
                "fresh-controller-binds-only-the-v14-source-and-protocol",
                previous.SOURCE_RELATIVE == SOURCE_RELATIVE
                and previous.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE,
            )
            check(
                "fresh-controller-binds-all-128-v14-production-cases",
                previous.MATRIX_SHA256 == MATRIX_SHA256
                and previous.build_matrix() == matrix,
            )
            with previous._stage12_context():
                check(
                    "isolated-production-worker-is-bound-to-v14-source",
                    stage11.SOURCE_RELATIVE == SOURCE_RELATIVE
                    and stage11.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE
                    and stage11.WORKER_BOOTSTRAP == WORKER_BOOTSTRAP,
                )
                check(
                    "isolated-worker-denies-all-v11-and-v12-evidence-paths",
                    stage11.APPROVED_OUTPUTS == APPROVED_OUTPUTS
                    and set(APPROVED_OUTPUTS).isdisjoint(saved_v11[4])
                    and set(APPROVED_OUTPUTS).isdisjoint(saved_v12[4]),
                )
        check(
            "source-context-restores-the-actual-historical-v12-controller",
            (
                previous.SOURCE_RELATIVE,
                previous.PROTOCOL_RELATIVE,
                previous.MATRIX_SHA256,
                previous.WORKER_BOOTSTRAP,
                previous.APPROVED_OUTPUTS,
                previous.build_matrix,
            ) == saved_v12,
        )
        check(
            "source-context-restores-the-actual-historical-v11-controller",
            (
                stage11.SOURCE_RELATIVE,
                stage11.PROTOCOL_RELATIVE,
                stage11.MATRIX_SHA256,
                stage11.WORKER_BOOTSTRAP,
                stage11.APPROVED_OUTPUTS,
                stage11.build_matrix,
            ) == saved_v11,
        )

        baseline = v12_reference["baseline_records"]
        synthetic_provenance = {
            "synthetic_only": True,
            "source_path": SOURCE_RELATIVE,
            "source_sha256": "e" * 64,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": "f" * 64,
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "native_sha256_by_family": verified_natives,
        }
        full_reference = _synthetic_complete_self_oracle(
            baseline, synthetic_provenance,
        )
        _validate_complete_self_oracle(full_reference, synthetic_provenance)
        first_reference = full_reference["baseline_records"]
        second_reference = full_reference["second_records"]
        check(
            "self-evidence-preserves-all-256-independently-executed-python-rows",
            len(first_reference) == len(second_reference) == EXPECTED_CASES
            and first_reference == second_reference
            and len(full_reference["reference_worker_reports"]) == 2,
        )
        check(
            "self-evidence-preserves-two-actual-source-bound-worker-reports",
            set(full_reference["reference_worker_reports"])
            == {"stdlib-a", "stdlib-b"}
            and all(
                len(full_reference["reference_worker_reports"][role]["records"])
                == EXPECTED_CASES
                for role in ("stdlib-a", "stdlib-b")
            ),
        )
        check(
            "self-evidence-binds-both-actual-reference-content-fingerprints",
            full_reference["baseline_record_sha256"] == digest(first_reference)
            and full_reference["second_record_sha256"] == digest(second_reference),
        )
        for field, poisoned in (
            ("status", "FAIL"),
            ("source_path", STAGE12_SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("protocol_path", STAGE12_PROTOCOL_RELATIVE),
            ("seed", 2026072471),
            ("matrix_sha256", STAGE12_MATRIX_SHA256),
            ("stdlib_checks", 255),
            ("independent_stdlib_roles", ["stdlib-a"]),
            ("baseline_record_sha256", "0" * 64),
            ("second_record_sha256", "0" * 64),
            ("mismatches", 1),
            ("candidate_imports", 1),
            ("candidate_processes", 1),
            ("performance", "MEASURED"),
        ):
            reject(
                "rejects-incomplete-dual-python-reference-" + field,
                lambda field=field, poisoned=poisoned: (
                    _validate_complete_self_oracle(
                        {**full_reference, field: poisoned},
                        synthetic_provenance,
                    )
                ),
            )
        for role, field in (
            ("stdlib-a", "baseline_records"),
            ("stdlib-b", "second_records"),
        ):
            for mode in ("omitted", "reordered", "duplicated"):
                changed_reference = stage11.copy.deepcopy(full_reference)
                rows = changed_reference[field]
                if mode == "omitted":
                    rows.pop()
                elif mode == "reordered":
                    rows.reverse()
                else:
                    rows[-1] = stage11.copy.deepcopy(rows[0])
                changed_reference["reference_worker_reports"][role]["records"] = (
                    stage11.copy.deepcopy(rows)
                )
                fingerprint = digest(rows)
                digest_key = (
                    "baseline_record_sha256" if role == "stdlib-a"
                    else "second_record_sha256"
                )
                changed_reference[digest_key] = fingerprint
                changed_reference["reference_worker_reports"][role][
                    "record_sha256"
                ] = fingerprint
                reject(
                    "rejects-" + mode + "-actual-python-reference-" + role,
                    lambda document=changed_reference: (
                        _validate_complete_self_oracle(
                            document, synthetic_provenance,
                        )
                    ),
                )
            substituted = stage11.copy.deepcopy(full_reference)
            substituted[field][0]["warnings"] = [{"synthetic_substitution": True}]
            substituted["reference_worker_reports"][role]["records"] = (
                stage11.copy.deepcopy(substituted[field])
            )
            actual_sha = digest(substituted[field])
            digest_key = (
                "baseline_record_sha256" if role == "stdlib-a"
                else "second_record_sha256"
            )
            substituted[digest_key] = actual_sha
            substituted["reference_worker_reports"][role][
                "record_sha256"
            ] = actual_sha
            reject(
                "rejects-substituted-actual-python-reference-" + role,
                lambda document=substituted: _validate_complete_self_oracle(
                    document, synthetic_provenance,
                ),
            )
            omitted_worker = stage11.copy.deepcopy(full_reference)
            omitted_worker["reference_worker_reports"].pop(role)
            reject(
                "rejects-omitted-actual-independent-python-worker-" + role,
                lambda document=omitted_worker: _validate_complete_self_oracle(
                    document, synthetic_provenance,
                ),
            )
            foreign_worker = stage11.copy.deepcopy(full_reference)
            foreign_worker["reference_worker_reports"][role]["public_origins"][
                "Match"
            ]["actual_module"] = "candidates._rust_bridge"
            reject(
                "rejects-foreign-actual-python-reference-owner-" + role,
                lambda document=foreign_worker: _validate_complete_self_oracle(
                    document, synthetic_provenance,
                ),
            )
        synthetic_outcomes = {
            role: {
                "candidate": role,
                "module": "candidates." + role + "_candidate",
                "status": "PASS",
                "cases": EXPECTED_CASES,
                "cohort_cases": dict(stage11.COHORTS),
                "records": stage11.copy.deepcopy(baseline),
                "record_sha256": digest(baseline),
                "mismatches": 0,
                "failure_records": [],
                "failures_recorded": 0,
                "guard": _synthetic_guard(role),
                "native_binary_sha256": verified_natives[role],
                "benchmark_or_timing_executed": False,
                "performance_fixtures_read": 0,
                "holdout_cases_read": 0,
                "performance": "NOT MEASURED",
            }
            for role in REQUIRED_CANDIDATES
        }
        complete = {
            "schema": ALL_CANDIDATE_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": synthetic_provenance["source_sha256"],
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": synthetic_provenance["protocol_sha256"],
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cohorts": len(stage11.COHORTS),
            "cohort_cases": dict(stage11.COHORTS),
            "selected": "all",
            "selected_candidates": list(REQUIRED_CANDIDATES),
            "completed_candidates": list(REQUIRED_CANDIDATES),
            "comparison_complete": True,
            "cases_per_candidate": EXPECTED_CASES,
            "candidate_checks": 384,
            "reference_checks": EXPECTED_CASES * 2,
            "self_oracle_path": SELF_ORACLE_RELATIVE,
            "self_oracle_sha256": "d" * 64,
            "reference_worker_reports": full_reference["reference_worker_reports"],
            "baseline_records": first_reference,
            "second_reference_records": second_reference,
            "second_records": second_reference,
            "baseline_record_sha256": full_reference["baseline_record_sha256"],
            "second_record_sha256": full_reference["second_record_sha256"],
            "candidate_reports": synthetic_outcomes,
            "candidate_cross_delegation": False,
            "mismatches": 0,
            "current_provenance": synthetic_provenance,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        _validate_complete_candidate_report(
            complete,
            baseline=first_reference,
            second_reference=second_reference,
            provenance=synthetic_provenance,
            self_oracle_sha256="d" * 64,
        )
        check("final-evidence-preserves-all-128-first-python-observations", True)
        check("final-evidence-preserves-all-128-second-python-observations", True)
        check("final-evidence-preserves-all-256-actual-python-observations", True)
        check("final-evidence-preserves-all-384-real-candidate-observations", True)
        for role in REQUIRED_CANDIDATES:
            omitted = stage11.copy.deepcopy(complete)
            omitted["candidate_reports"][role]["records"].pop()
            reject(
                "rejects-concealed-final-candidate-observation-" + role,
                lambda document=omitted: _validate_complete_candidate_report(
                    document,
                    baseline=first_reference,
                    second_reference=second_reference,
                    provenance=synthetic_provenance,
                    self_oracle_sha256="d" * 64,
                ),
            )
        for field in (
            "baseline_records", "second_reference_records", "second_records",
        ):
            omitted_reference = stage11.copy.deepcopy(complete)
            omitted_reference[field].pop()
            reject(
                "rejects-concealed-final-python-reference-" + field,
                lambda document=omitted_reference: (
                    _validate_complete_candidate_report(
                        document,
                        baseline=first_reference,
                        second_reference=second_reference,
                        provenance=synthetic_provenance,
                        self_oracle_sha256="d" * 64,
                    )
                ),
            )
            reversed_reference = stage11.copy.deepcopy(complete)
            reversed_reference[field].reverse()
            reject(
                "rejects-reordered-final-python-reference-" + field,
                lambda document=reversed_reference: (
                    _validate_complete_candidate_report(
                        document,
                        baseline=first_reference,
                        second_reference=second_reference,
                        provenance=synthetic_provenance,
                        self_oracle_sha256="d" * 64,
                    )
                ),
            )
        for field in ("baseline_record_sha256", "second_record_sha256"):
            reject(
                "rejects-forged-final-python-reference-fingerprint-" + field,
                lambda name=field: _validate_complete_candidate_report(
                    {**complete, name: "0" * 64},
                    baseline=first_reference,
                    second_reference=second_reference,
                    provenance=synthetic_provenance,
                    self_oracle_sha256="d" * 64,
                ),
            )
        for role in ("stdlib-a", "stdlib-b"):
            omitted_worker = stage11.copy.deepcopy(complete)
            omitted_worker["reference_worker_reports"].pop(role)
            reject(
                "rejects-concealed-final-actual-python-worker-" + role,
                lambda document=omitted_worker: _validate_complete_candidate_report(
                    document,
                    baseline=first_reference,
                    second_reference=second_reference,
                    provenance=synthetic_provenance,
                    self_oracle_sha256="d" * 64,
                ),
            )
        check("six-exclusive-v14-success-and-failure-destinations", len(set(APPROVED_OUTPUTS)) == 6)
        check(
            "never-overwrites-the-preserved-v11-failed-experiment",
            set(APPROVED_OUTPUTS).isdisjoint(stage11.APPROVED_OUTPUTS),
        )
        check(
            "never-overwrites-the-preserved-v12-passing-experiment",
            set(APPROVED_OUTPUTS).isdisjoint(previous.APPROVED_OUTPUTS),
        )
        check(
            "fresh-v14-production-bootstrap-is-independent-and-source-bound",
            "_stage14" in WORKER_BOOTSTRAP and "_worker_entry" in WORKER_BOOTSTRAP,
        )
        check(
            "candidate-free-synthetic-test-imports-no-matching-engine",
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
        )
        check(
            "candidate-free-synthetic-test-imports-no-inspector",
            ("inspect" in sys.modules) == _INSPECT_PRESENT_AT_IMPORT,
        )
        check(
            "candidate-free-synthetic-test-imports-no-tokenizer",
            ("tokenize" in sys.modules) == _TOKENIZE_PRESENT_AT_IMPORT,
        )
        check("candidate-free-synthetic-test-opens-no-file", effects["files"] == 0)
        check("candidate-free-synthetic-test-starts-no-process", effects["workers"] == 0)
        check("candidate-free-synthetic-test-reads-no-clock", effects["timing"] == 0)
        check("candidate-free-synthetic-test-draws-no-entropy", effects["entropy"] == 0)
        check(
            "all-synthetic-files-workers-clocks-and-entropy-remain-zero",
            all(value == 0 for value in effects.values()),
        )
        frozen.candidate_free()
        names = [check["name"] for check in checks]
        frozen.require(
            len(names) == len(set(names)) and len(checks) >= 100,
            "the candidate-free V14 forgery controls were weakened",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "stage": "stage14",
            "status": "PASS",
            "result": "PASS",
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cohorts": 4,
            "cohort_cases": dict(stage11.COHORTS),
            "cases": EXPECTED_CASES,
            "check_count": len(checks),
            "checks": checks,
            "failed": [],
            "preserved_stage11_reference_sha256": STAGE11_SELF_SHA256,
            "preserved_stage11_failure_sha256": STAGE11_RUST_FAILURE_SHA256,
            "preserved_stage11_failure_count": 16,
            "preserved_stage12_reference_sha256": STAGE12_SELF_SHA256,
            "preserved_stage12_candidate_sha256": STAGE12_ALL_SHA256,
            "preserved_stage12_stdlib_checks": 256,
            "preserved_stage12_candidate_checks": 384,
            "preserved_official_v2_failure_sha256": OFFICIAL_V2_FAILURE_SHA256,
            "preserved_official_v2_failure_status": "FAIL",
            "preserved_official_v2_unexecuted_roles": ["vm", "zig"],
            "preserved_official_v3_source_sha256": OFFICIAL_V3_SOURCE_SHA256,
            "preserved_official_v3_protocol_sha256": OFFICIAL_V3_PROTOCOL_SHA256,
            "preserved_official_v3_report_sha256": OFFICIAL_V3_REPORT_SHA256,
            "preserved_official_v3_status": "PASS",
            "preserved_official_v3_role_count": 4,
            "preserved_official_v3_methods_per_role": 146,
            "preserved_official_v3_total_method_checks": 584,
            "v7_source_audit_pinned": V7_BASE_AUDIT_SHA256 is not None,
            "v7_strict_audit_pinned": V7_STRICT_AUDIT_SHA256 is not None,
            "owned_source_count": 12,
            "owned_native_binary_count": 5,
            "verified_synthetic_standard_pickle_checks": 48,
            "verified_synthetic_match_repr_checks": 6,
            "final_synthetic_baseline_records": 128,
            "final_synthetic_second_reference_records": 128,
            "final_synthetic_reference_records": 256,
            "final_synthetic_candidate_records": 384,
            "candidate_imports": 0,
            "candidate_processes": 0,
            "inspect_present_before_self_test": _INSPECT_PRESENT_AT_IMPORT,
            "inspect_imported_by_self_test": (
                ("inspect" in sys.modules) != _INSPECT_PRESENT_AT_IMPORT
            ),
            "tokenize_present_before_self_test": _TOKENIZE_PRESENT_AT_IMPORT,
            "tokenize_imported_by_self_test": (
                ("tokenize" in sys.modules) != _TOKENIZE_PRESENT_AT_IMPORT
            ),
            "files_read": 0,
            "files_written": 0,
            "clock_samples": 0,
            "entropy_drawn": False,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
            "self_oracle_executed": False,
            "production_evidence_written": False,
            "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
            "self_oracle_output": SELF_ORACLE_RELATIVE,
            "self_oracle_failure_output": SELF_ORACLE_FAILURE_RELATIVE,
            "all_candidate_output": ALL_CANDIDATE_RELATIVE,
            "candidate_failure_outputs": dict(CANDIDATE_FAILURE_RELATIVES),
        }


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        if arguments == ["--self-test"]:
            result = self_test()
        elif arguments == ["--self-oracle"]:
            result = run_self_oracle()
        elif arguments == ["--candidate", "all"]:
            result = run_all_candidates()
        else:
            raise frozen.OracleIntegrityError(
                "select exactly --self-test, --self-oracle, or --candidate all"
            )
        sys.stdout.buffer.write(canonical(result) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (
        frozen.OracleIntegrityError, AssertionError, OSError,
        TypeError, UnicodeError, ValueError, stage07.subprocess.SubprocessError,
    ) as error:
        sys.stderr.buffer.write(
            canonical({"schema": SCHEMA, "status": "FAIL", "error": str(error)})
            + b"\n"
        )
        sys.stderr.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
