#!/usr/bin/env python3
"""Independently recheck every Python regex behavior after repaired native builds."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _stage15_os
    from pathlib import Path as _Stage15Path

    _stage15_root = str(_Stage15Path(__file__).resolve().parent.parent)
    _stage15_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_universal_public_oracle_stage15 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _stage15_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _stage15_entry,
         _stage15_root, *sys.argv[1:]],
    )

import argparse
from contextlib import contextmanager
import importlib
from pathlib import Path
import tempfile
import types
from typing import Any, Callable, Iterator

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v3 as official_v3
from tools import postfinal_from_scratch_audit_v7 as source_v7
from tools import python_re_generic_alias_public_oracle_stage11 as old_aliases
from tools import python_re_universal_public_oracle_stage10 as stage10


stage07 = stage10.stage07
stage06 = stage10.stage06
frozen = stage10.frozen
official_locale = stage10.official_locale
canonical = stage10.canonical
digest = stage10.digest

SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage15.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15.md"
SCHEMA = "rebar-python-re-public-contract-v15"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SELF_ORACLE_SCHEMA = SCHEMA + "-self-oracle"
ALL_CANDIDATE_SCHEMA = SCHEMA + "-all-candidates"
METADATA_SCHEMA = SCHEMA + "-isolated-public-metadata"
METADATA_ENVIRONMENT = "REBAR_PUBLIC_CONTRACT_V15_AUTHENTICATED_METADATA"
OBSERVATION_DOMAIN = "rebar/python-re/public-contract/v15"
SEED = 2026072479
SEED_DOMAIN = OBSERVATION_DOMAIN
EXPECTED_CASES = 3_584
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
MATRIX_SHA256 = (
    "3e643ab0c455bc789e4939af2dba73af18abb033f2f34f003b49b1299b35eeeb"
)
ORIGINAL_MATRIX_SHA256 = (
    "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db"
)
NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL", "ctypes.cdll.LoadLibrary", "ctypes.cdll._dlltype",
    "ctypes._dlopen", "_ctypes.dlopen",
)

V7_BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v7.py"
V7_BASE_SOURCE_SHA256 = (
    "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487"
)
V7_BASE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"
V7_BASE_REPORT_SHA256 = (
    "efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a"
)
V7_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v7.py"
V7_STRICT_SOURCE_SHA256 = (
    "9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4"
)
V7_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json"
)
V7_STRICT_REPORT_SHA256 = (
    "1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34"
)
OFFICIAL_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v3.py"
OFFICIAL_SOURCE_SHA256 = (
    "28b98c8913ca89ec2ba600484205c3bcb63ae22a86e33d4f7cf3c6f1a68c8a58"
)
OFFICIAL_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V3.md"
OFFICIAL_PROTOCOL_SHA256 = (
    "a1f77b1628c03d42b9d8e2650c9b501d9be4cec917d765539c91c750154bd6ac"
)
OFFICIAL_REPORT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v3-all.json"
)
OFFICIAL_REPORT_SHA256 = (
    "18a011a5ce6e47e52cd02e4cb0812c8f9f7919a069edd7d74e57631623b901b5"
)
OFFICIAL_SELECTED_METHOD_SHA256 = (
    "d33571d09a3a9cb428a84dece5af233e66267b831d3043c90e3ad77cb8de5178"
)
GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
OFFICIAL_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json"
)
OFFICIAL_FAILURE_SHA256 = (
    "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f"
)

STAGE10_SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage10.py"
STAGE10_SOURCE_SHA256 = (
    "a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08"
)
STAGE10_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md"
STAGE10_PROTOCOL_SHA256 = (
    "c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543"
)
STAGE10_SELF_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json"
)
STAGE10_SELF_SHA256 = (
    "5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9"
)
STAGE10_ALL_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v10-all.json"
)
STAGE10_ALL_SHA256 = (
    "0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7"
)

STAGE14_SOURCE_RELATIVE = (
    "tools/python_re_generic_alias_public_oracle_stage14.py"
)
STAGE14_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V14.md"
)
STAGE14_SELF_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v14-self-oracle.json"
)
STAGE14_ALL_RELATIVE = (
    "candidates/evidence/python-re-generic-alias-public-oracle-v14-all.json"
)
# Root independently produced and published all four corrected, complete V14
# proofs. Any missing, malformed, reused, or substituted proof fails closed.
STAGE14_SOURCE_SHA256 = (
    "5caba6e5d92935a1877fb34bd3c1e266d07c67385f847477041312959104ec58"
)
STAGE14_PROTOCOL_SHA256 = (
    "b20b5b3876fba06cdf41b9a99825157d0ca6ba84b8bc7abfd71b49e44fdd7505"
)
STAGE14_SELF_SHA256 = (
    "7da9c6aa5fa1db4ef0dea593d8f9d501ecc952aa62ed7bf5a0f17d0b726b04bf"
)
STAGE14_ALL_SHA256 = (
    "f9243bd27a4d4ae24c0c3f0b24785e381440fc19c8911b52719cc6813bc1e8cc"
)
STAGE14_SEED = 2026072481
STAGE14_SEED_DOMAIN = "rebar/python-re/public-generic-alias/v14"
STAGE14_MATRIX_SHA256 = (
    "3d57a2eae1e880df934043856cf6d5ed32944908b7642611a3f060406453f1ab"
)

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v15-all.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    role: (
        "candidates/evidence/python-re-universal-public-oracle-v15-"
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
    "from tools.python_re_universal_public_oracle_stage15 import _worker_entry;"
    "raise SystemExit(_worker_entry(sys.argv[2],sys.argv[3]))"
)
METADATA_WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_universal_public_oracle_stage15 "
    "import _metadata_worker_entry;"
    "raise SystemExit(_metadata_worker_entry(sys.argv[2],sys.argv[3]))"
)


def _cohort_seed(cohort: str) -> str:
    frozen.require(cohort in {name for name, _, _ in stage07.COHORTS},
                   "the full universal matrix received a foreign public cohort")
    return digest({"domain": SEED_DOMAIN, "seed": SEED, "cohort": cohort})


def _matrix_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cohort, operation, count in stage07.COHORTS:
        seed = _cohort_seed(cohort)
        for index in range(count):
            row: dict[str, Any] = {
                "id": f"{cohort}:{index:04d}", "cohort": cohort,
                "operation": operation, "index": index, "seed": seed,
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
        and value == _matrix_rows()
        and digest(value) == MATRIX_SHA256
        and len({row["id"] for row in value}) == EXPECTED_CASES,
        "the full repaired-engine matrix omitted or changed a true Python case",
    )


def build_matrix() -> list[dict[str, Any]]:
    rows = _matrix_rows()
    validate_matrix(rows)
    return rows


def _require_published_stage14() -> None:
    published = (
        ("source", STAGE14_SOURCE_SHA256),
        ("protocol", STAGE14_PROTOCOL_SHA256),
        ("reference", STAGE14_SELF_SHA256),
        ("all-candidates", STAGE14_ALL_SHA256),
    )
    for name, value in published:
        frozen.require(
            isinstance(value, str) and official_locale.is_sha256(value),
            "the rebuilt stage-14 generic-alias experiment is not published: " + name,
        )
    frozen.require(
        len({value for _name, value in published}) == len(published),
        "the rebuilt generic-alias proofs reuse an artifact fingerprint",
    )


def _verify_source(relative: str, expected: str) -> None:
    frozen.require(isinstance(expected, str)
                   and official_locale.is_sha256(expected),
                   "an actual public source or protocol is not pinned")
    source = official_locale.checked_repo_path(relative)
    frozen.require(
        official_locale.sha256_path(source, maximum=frozen.MAX_SOURCE_BYTES)
        == expected,
        "a complete repaired-engine proof was changed: " + relative,
    )


def _validate_official_v3(document: Any, *,
                          base: dict[str, Any],
                          strict: dict[str, Any]) -> dict[str, Any]:
    frozen.require(
        isinstance(document, dict)
        and document.get("schema") == "rebar-postfinal-cpython-public-locale-v3"
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("python") == "3.14.6"
        and document.get("source_path") == OFFICIAL_SOURCE_RELATIVE
        and document.get("source_sha256") == OFFICIAL_SOURCE_SHA256
        and document.get("goal_sha256") == GOAL_SHA256
        and document.get("holdout_accessed") is False
        and document.get("timing_performed") is False
        and document.get("performance") == "NOT MEASURED",
        "the actual repaired four-role official Python test is missing or unsafe",
    )
    audit = document.get("audits")
    frozen.require(
        isinstance(audit, dict)
        and isinstance(audit.get("from_scratch"), dict)
        and isinstance(audit.get("no_delegation"), dict)
        and audit["from_scratch"].get("path") == V7_BASE_REPORT_RELATIVE
        and audit["from_scratch"].get("sha256") == V7_BASE_REPORT_SHA256
        and audit["from_scratch"].get("source_path") == V7_BASE_SOURCE_RELATIVE
        and audit["from_scratch"].get("source_sha256") == V7_BASE_SOURCE_SHA256
        and audit["no_delegation"].get("path") == V7_STRICT_REPORT_RELATIVE
        and audit["no_delegation"].get("sha256") == V7_STRICT_REPORT_SHA256
        and audit["no_delegation"].get("source_path") == V7_STRICT_SOURCE_RELATIVE
        and audit["no_delegation"].get("source_sha256") == V7_STRICT_SOURCE_SHA256
        and document.get("qualified_source_fingerprints")
        == strict.get("qualified_source_fingerprints")
        and document.get("native_elf_fingerprints")
        == strict.get("native_elf_fingerprints"),
        "the official Python run did not test the exact V7-audited engines",
    )
    original = document.get("original_oracle")
    frozen.require(
        isinstance(original, dict)
        and original.get("selected_methods") == 146
        and original.get("total_public_methods") == 152
        and original.get("corpus_cases") == 403
        and original.get("selected_method_sha256")
        == OFFICIAL_SELECTED_METHOD_SHA256
        and original.get("runner_path") == "tools/cpython_re_oracle.py"
        and original.get("runner_sha256")
        == "d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb"
        and original.get("manifest_path")
        == "oracle/cpython-3.14.6/manifest.json"
        and original.get("manifest_sha256")
        == "2c89ce37e474cb6f59d61f86ad810662b50b83bbdce3610c04523fe092688597"
        and isinstance(original.get("all_named_waivers"), dict)
        and set(original["all_named_waivers"]) == {
            "DebugTests", "ImplementationTest", "ReTests.test_large_search",
            "ReTests.test_large_subn", "ReTests.test_memory_leaks",
            "ReTests.test_re_groupref_overflow",
            "ReTests.test_regression_gh94675",
            "ReTests.test_search_anchor_at_beginning",
        },
        "the actual official Python cases, source, or named waivers changed",
    )
    scope = document.get("official_scope")
    frozen.require(
        isinstance(scope, dict)
        and scope.get("genuine_official_methods_per_engine") == 146
        and scope.get("original_public_methods") == 152
        and scope.get("original_upstream_corpus_cases") == 403
        and scope.get("real_locale_methods_per_engine") == 2
        and scope.get("independently_run_engine_count") == 4
        and scope.get("verified_owned_source_count") == 12
        and scope.get("verified_native_binary_count") == 5
        and scope.get("verified_standard_pickle_count") == 48
        and scope.get("verified_real_native_match_repr_count") == 6
        and scope.get("named_waiver_count") == 8
        and scope.get("genuine_official_v2_rust_failure_preserved") is True
        and scope.get("official_v2_success_report_exists") is False
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the actual official methods, corpus, locales, or failure were weakened",
    )
    roles = document.get("roles")
    frozen.require(isinstance(roles, dict)
                   and set(roles) == {"re", *REQUIRED_CANDIDATES},
                   "the genuine official test omitted Python or a repaired engine")
    reference_ids: list[str] | None = None
    for role in ("re", *REQUIRED_CANDIDATES):
        actual = roles[role]
        expected_module = (
            "re" if role == "re" else "candidates." + role + "_candidate"
        )
        records = actual.get("records") if isinstance(actual, dict) else None
        frozen.require(
            isinstance(actual, dict)
            and actual.get("module") == expected_module
            and actual.get("methods") == 146
            and actual.get("passed") == 146
            and actual.get("failed") == 0
            and actual.get("failures") == 0
            and actual.get("errors") == 0
            and actual.get("skipped") == 0
            and actual.get("crashes") == 0
            and actual.get("timeouts") == 0
            and actual.get("locale_caching_passed") is True
            and actual.get("locale_compiled_passed") is True
            and actual.get("holdout_accessed") is False
            and actual.get("timing_performed") is False
            and actual.get("performance") == "NOT MEASURED"
            and isinstance(records, list)
            and len(records) == 146
            and all(
                isinstance(record, dict)
                and isinstance(record.get("test"), str)
                and record.get("status") == "passed"
                and record.get("skipped") == 0
                and record.get("reason") is None
                for record in records
            )
            and len({row["test"] for row in records}) == 146
            and {
                "ExternalTests.test_re_tests", "ReTests.test_match_repr",
                "ReTests.test_locale_caching", "ReTests.test_locale_compiled",
            }.issubset({row["test"] for row in records})
            and (reference_ids is None
                 or [row["test"] for row in records] == reference_ids),
            "a complete real official CPython method result is missing: " + role,
        )
        if reference_ids is None:
            reference_ids = [row["test"] for row in records]
    return document


def _validate_stage14_reference(document: Any, *,
                                module: Any,
                                current: dict[str, Any]) -> dict[str, Any]:
    frozen.require(
        getattr(module, "SEED", None) == STAGE14_SEED
        and getattr(module, "SEED_DOMAIN", None) == STAGE14_SEED_DOMAIN
        and getattr(module, "MATRIX_SHA256", None) == STAGE14_MATRIX_SHA256,
        "the actually frozen rebuilt generic-alias matrix was substituted",
    )
    required: dict[str, Any] = {
        "schema": "rebar-python-re-public-generic-alias-v14-self-oracle",
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": STAGE14_SOURCE_RELATIVE,
        "source_sha256": STAGE14_SOURCE_SHA256,
        "protocol_path": STAGE14_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE14_PROTOCOL_SHA256,
        "seed": module.SEED, "seed_domain": module.SEED_DOMAIN,
        "matrix_sha256": module.MATRIX_SHA256,
        "cohorts": 4, "cohort_cases": dict(old_aliases.COHORTS),
        "cases": 128,
        "stdlib_checks": 256, "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0, "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen.require(isinstance(document, dict),
                   "the current genuine generic-alias Python reference is absent")
    for key, value in required.items():
        frozen.require(document.get(key) == value
                       and type(document.get(key)) is type(value),
                       "the genuine stage14 Python reference changed: " + key)
    rows = document.get("baseline_records")
    second = document.get("second_records")
    frozen.require(
        isinstance(rows, list)
        and isinstance(second, list)
        and len(rows) == 128
        and len(second) == 128
        and all(isinstance(row, dict) for row in rows)
        and all(isinstance(row, dict) for row in second)
        and [row.get("id") for row in rows]
        == [row["id"] for row in module.build_matrix()]
        and [row.get("id") for row in second]
        == [row["id"] for row in module.build_matrix()]
        and second == rows
        and document.get("baseline_record_sha256") == digest(rows)
        and document.get("second_record_sha256") == digest(second)
        and document.get("independent_stdlib_roles")
        == ["stdlib-a", "stdlib-b"]
        and document.get("current_provenance") == current,
        "an independently rerun generic-alias reference omitted a real stream",
    )
    workers = document.get("reference_worker_reports")
    frozen.require(
        isinstance(workers, dict)
        and set(workers) == {"stdlib-a", "stdlib-b"},
        "the generic-alias proof concealed an actual isolated Python worker",
    )
    for role, expected_records in (("stdlib-a", rows), ("stdlib-b", second)):
        worker = workers[role]
        observed = worker.get("records") if isinstance(worker, dict) else None
        origins = worker.get("public_origins") if isinstance(worker, dict) else None
        frozen.require(
            isinstance(worker, dict)
            and worker.get("schema")
            == "rebar-python-re-public-generic-alias-v14-worker"
            and worker.get("status") == "PASS"
            and worker.get("role") == role
            and worker.get("python") == "3.14.6"
            and worker.get("source_sha256") == STAGE14_SOURCE_SHA256
            and worker.get("seed") == STAGE14_SEED
            and worker.get("seed_domain") == STAGE14_SEED_DOMAIN
            and worker.get("matrix_sha256") == STAGE14_MATRIX_SHA256
            and worker.get("cases") == 128
            and worker.get("cohort_cases") == dict(old_aliases.COHORTS)
            and isinstance(observed, list)
            and len(observed) == 128
            and observed == expected_records
            and worker.get("record_sha256") == digest(observed)
            and worker.get("guard")
            == {"baseline_only": True, "candidate_imported": False}
            and worker.get("native_binary_sha256") == {}
            and isinstance(origins, dict)
            and set(origins) == {"Pattern", "Match"}
            and all(
                isinstance(origins.get(name), dict)
                and origins[name].get("actual_module") == "re"
                for name in ("Pattern", "Match")
            )
            and worker.get("inspect_loaded") is False
            and worker.get("tokenize_loaded") is False
            and worker.get("benchmark_or_timing_executed") is False
            and worker.get("performance_fixtures_read") == 0
            and worker.get("holdout_cases_read") == 0
            and worker.get("performance") == "NOT MEASURED",
            "an actual isolated generic-alias reference was concealed: " + role,
        )
    return document


def _validate_stage14_all(document: Any, *, module: Any,
                          reference: dict[str, Any],
                          current: dict[str, Any]) -> dict[str, Any]:
    expected: dict[str, Any] = {
        "schema": "rebar-python-re-public-generic-alias-v14-all-candidates",
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": STAGE14_SOURCE_RELATIVE,
        "source_sha256": STAGE14_SOURCE_SHA256,
        "protocol_path": STAGE14_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE14_PROTOCOL_SHA256,
        "seed": module.SEED, "seed_domain": module.SEED_DOMAIN,
        "matrix_sha256": module.MATRIX_SHA256,
        "cohorts": 4, "cohort_cases": dict(old_aliases.COHORTS),
        "cases_per_candidate": 128,
        "candidate_checks": 384, "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        "candidate_cross_delegation": False,
        "mismatches": 0,
        "self_oracle_path": STAGE14_SELF_RELATIVE,
        "self_oracle_sha256": STAGE14_SELF_SHA256,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen.require(isinstance(document, dict),
                   "the current actual three-family generic-alias result is absent")
    for key, value in expected.items():
        frozen.require(document.get(key) == value
                       and type(document.get(key)) is type(value),
                       "the actual current generic-alias result changed: " + key)
    frozen.require(
        isinstance(document.get("baseline_records"), list)
        and len(document["baseline_records"]) == 128
        and document["baseline_records"] == reference["baseline_records"]
        and isinstance(document.get("second_reference_records"), list)
        and len(document["second_reference_records"]) == 128
        and document["second_reference_records"] == reference["second_records"]
        and isinstance(document.get("second_records"), list)
        and len(document["second_records"]) == 128
        and document["second_records"] == reference["second_records"]
        and document.get("baseline_record_sha256")
        == reference["baseline_record_sha256"]
        and document.get("second_record_sha256")
        == reference["second_record_sha256"]
        and document.get("reference_worker_reports")
        == reference["reference_worker_reports"]
        and document.get("current_provenance") == current,
        "the current generic-alias results concealed either actual Python stream",
    )
    reports = document.get("candidate_reports")
    frozen.require(isinstance(reports, dict)
                   and set(reports) == set(REQUIRED_CANDIDATES),
                   "a real independently matching alias candidate was omitted")
    for role in REQUIRED_CANDIDATES:
        report = reports[role]
        records = report.get("records") if isinstance(report, dict) else None
        frozen.require(
            isinstance(report, dict)
            and report.get("candidate") == role
            and report.get("module") == "candidates." + role + "_candidate"
            and report.get("status") == "PASS"
            and report.get("cases") == 128
            and report.get("cohort_cases") == dict(old_aliases.COHORTS)
            and isinstance(records, list)
            and len(records) == 128
            and all(isinstance(row, dict) for row in records)
            and records == reference["baseline_records"]
            and [row.get("id") for row in records]
            == [row["id"] for row in module.build_matrix()]
            and report.get("mismatches") == 0
            and report.get("failure_records") == []
            and report.get("failures_recorded") == 0
            and report.get("record_sha256")
            == reference["baseline_record_sha256"]
            and report.get("record_sha256") == digest(records)
            and report.get("native_binary_sha256")
            == current["native_sha256_by_family"][role]
            and report.get("benchmark_or_timing_executed") is False
            and report.get("performance_fixtures_read") == 0
            and report.get("holdout_cases_read") == 0
            and report.get("performance") == "NOT MEASURED",
            "a real rebuilt generic-alias family failed: " + role,
        )
        origins = report.get("public_origins")
        native_module = {
            "rust": "candidates._rust_bridge",
            "vm": "candidates._vm_native",
            "zig": "candidates._zig_bridge",
        }[role]
        frozen.require(
            isinstance(origins, dict)
            and set(origins) == {"Pattern", "Match"}
            and all(
                isinstance(origins.get(name), dict)
                and origins[name].get("public_name") == name
                and origins[name].get("actual_name") == name
                and origins[name].get("actual_qualified_name") == name
                and origins[name].get("actual_module") == (
                    native_module if name == "Match"
                    else "candidates." + role + "_candidate"
                )
                for name in ("Pattern", "Match")
            ),
            "a repaired public generic alias uses a foreign class: " + role,
        )
        guard = report.get("guard")
        frozen.require(
            isinstance(guard, dict)
            and guard.get("family") == role
            and all(guard.get(name) is True for name in (
                "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
                "third_party_regex_blocked", "cross_family_blocked",
                "foreign_dynamic_libraries_blocked",
            ))
            and guard.get("native_loader_aliases_blocked")
            == list(NATIVE_LOADER_ALIASES)
            and guard.get("matcher_inspect_loaded") is False
            and guard.get("matcher_tokenizer_loaded") is False,
            "a current generic-alias native guard was weakened: " + role,
        )
    return document


def _authenticate_current_provenance() -> dict[str, Any]:
    official_locale.verify_runtime()
    frozen.candidate_free()
    # Do not read a production report or start a worker before all four real
    # stage-fourteen artifact fingerprints have actually been published.
    _require_published_stage14()
    for relative, expected in (
        (V7_BASE_SOURCE_RELATIVE, V7_BASE_SOURCE_SHA256),
        (V7_STRICT_SOURCE_RELATIVE, V7_STRICT_SOURCE_SHA256),
        (OFFICIAL_SOURCE_RELATIVE, OFFICIAL_SOURCE_SHA256),
        (OFFICIAL_PROTOCOL_RELATIVE, OFFICIAL_PROTOCOL_SHA256),
        (STAGE10_SOURCE_RELATIVE, STAGE10_SOURCE_SHA256),
        (STAGE10_PROTOCOL_RELATIVE, STAGE10_PROTOCOL_SHA256),
    ):
        _verify_source(relative, expected)
    frozen.require(
        STAGE14_SOURCE_SHA256 is not None
        and STAGE14_PROTOCOL_SHA256 is not None
        and STAGE14_SELF_SHA256 is not None
        and STAGE14_ALL_SHA256 is not None,
        "an unpublished rebuilt generic-alias report cannot qualify production",
    )
    _verify_source(STAGE14_SOURCE_RELATIVE, STAGE14_SOURCE_SHA256)
    _verify_source(STAGE14_PROTOCOL_RELATIVE, STAGE14_PROTOCOL_SHA256)

    base, base_sha = stage06._read_public_document(
        V7_BASE_REPORT_RELATIVE, expected_sha256=V7_BASE_REPORT_SHA256,
    )
    strict, strict_sha = stage06._read_public_document(
        V7_STRICT_REPORT_RELATIVE, expected_sha256=V7_STRICT_REPORT_SHA256,
    )
    frozen.require(base_sha == V7_BASE_REPORT_SHA256
                   and strict_sha == V7_STRICT_REPORT_SHA256,
                   "an actually passed V7 native independence audit was substituted")
    sources, natives = official_v3.validate_v7_audits(
        base, strict,
        source_relative=V7_BASE_REPORT_RELATIVE,
        strict_relative=V7_STRICT_REPORT_RELATIVE,
        source_digest=V7_BASE_REPORT_SHA256,
    )
    official_v3.original.verify_production_fingerprints(sources, natives)
    graph = source_v7.source_v6._validate_fresh_graph(base)
    frozen.require(
        graph.get("source_count") == 12
        and graph.get("native_binary_count") == 5
        and graph.get("native_sha256_by_family")
        == base.get("native_sha256_by_family")
        and sources == strict.get("qualified_source_fingerprints")
        and natives == strict.get("native_elf_fingerprints")
        and strict.get("native_elf_provenance")
        == base.get("native_elf_provenance"),
        "the repaired V7 reports disagree on actual source or mapped native bytes",
    )

    actual_failure, failure_sha = stage06._read_public_document(
        OFFICIAL_FAILURE_RELATIVE, expected_sha256=OFFICIAL_FAILURE_SHA256,
    )
    source_v7._validate_historical_failure(actual_failure)
    frozen.require(failure_sha == OFFICIAL_FAILURE_SHA256,
                   "the first genuine failed Rust official run was rewritten")

    official, official_sha = stage06._read_public_document(
        OFFICIAL_REPORT_RELATIVE, expected_sha256=OFFICIAL_REPORT_SHA256,
    )
    _validate_official_v3(official, base=base, strict=strict)
    frozen.require(official_sha == OFFICIAL_REPORT_SHA256,
                   "the genuine four-role official result was substituted")

    aliases = importlib.import_module(
        "tools.python_re_generic_alias_public_oracle_stage14"
    )
    frozen.require(
        Path(aliases.__file__).resolve()
        == official_locale.checked_repo_path(STAGE14_SOURCE_RELATIVE)
        and callable(getattr(aliases, "_authenticate_provenance", None))
        and callable(getattr(aliases, "_validate_complete_self_oracle", None))
        and callable(
            getattr(aliases, "_validate_complete_candidate_report", None)
        ),
        "the rebuilt generic-alias source was replaced or does not authenticate",
    )
    alias_provenance = aliases._authenticate_provenance()
    frozen.require(
        isinstance(alias_provenance, dict)
        and alias_provenance.get("source_path") == STAGE14_SOURCE_RELATIVE
        and alias_provenance.get("source_sha256") == STAGE14_SOURCE_SHA256
        and alias_provenance.get("protocol_path") == STAGE14_PROTOCOL_RELATIVE
        and alias_provenance.get("protocol_sha256") == STAGE14_PROTOCOL_SHA256
        and alias_provenance.get("base_audit_source_path")
        == V7_BASE_SOURCE_RELATIVE
        and alias_provenance.get("base_audit_source_sha256")
        == V7_BASE_SOURCE_SHA256
        and alias_provenance.get("base_audit_path") == V7_BASE_REPORT_RELATIVE
        and alias_provenance.get("base_audit_sha256") == V7_BASE_REPORT_SHA256
        and alias_provenance.get("strict_audit_source_path")
        == V7_STRICT_SOURCE_RELATIVE
        and alias_provenance.get("strict_audit_source_sha256")
        == V7_STRICT_SOURCE_SHA256
        and alias_provenance.get("strict_audit_path")
        == V7_STRICT_REPORT_RELATIVE
        and alias_provenance.get("strict_audit_sha256")
        == V7_STRICT_REPORT_SHA256
        and alias_provenance.get("native_source_count") == 12
        and alias_provenance.get("native_binary_count") == 5
        and alias_provenance.get("native_sha256_by_family")
        == graph["native_sha256_by_family"],
        "the mandatory new generic-alias test did not use the current V7 engines",
    )
    alias_reference, reference_sha = stage06._read_public_document(
        STAGE14_SELF_RELATIVE, expected_sha256=STAGE14_SELF_SHA256,
    )
    aliases._validate_complete_self_oracle(alias_reference, alias_provenance)
    validated_reference = _validate_stage14_reference(
        alias_reference, module=aliases, current=alias_provenance,
    )
    alias_report, alias_sha = stage06._read_public_document(
        STAGE14_ALL_RELATIVE, expected_sha256=STAGE14_ALL_SHA256,
    )
    aliases._validate_complete_candidate_report(
        alias_report,
        baseline=validated_reference["baseline_records"],
        second_reference=validated_reference["second_records"],
        provenance=alias_provenance,
        self_oracle_sha256=STAGE14_SELF_SHA256,
    )
    _validate_stage14_all(
        alias_report, module=aliases,
        reference=validated_reference, current=alias_provenance,
    )
    frozen.require(reference_sha == STAGE14_SELF_SHA256
                   and alias_sha == STAGE14_ALL_SHA256,
                   "a real rebuilt stage-fourteen reference or family was hidden")

    historical_reference, historical_reference_sha = stage06._read_public_document(
        STAGE10_SELF_RELATIVE, expected_sha256=STAGE10_SELF_SHA256,
    )
    historical_all, historical_all_sha = stage06._read_public_document(
        STAGE10_ALL_RELATIVE, expected_sha256=STAGE10_ALL_SHA256,
    )
    frozen.require(
        isinstance(historical_reference, dict)
        and historical_reference.get("schema")
        == "rebar-python-re-public-contract-v10-self-oracle"
        and historical_reference.get("status") == "PASS"
        and historical_reference.get("cases") == EXPECTED_CASES
        and historical_reference.get("stdlib_checks") == EXPECTED_CASES * 2
        and historical_reference.get("mismatches") == 0
        and historical_reference.get("matrix_sha256") == ORIGINAL_MATRIX_SHA256
        and historical_reference.get("source_sha256") == STAGE10_SOURCE_SHA256
        and historical_reference_sha == STAGE10_SELF_SHA256
        and isinstance(historical_all, dict)
        and historical_all.get("schema")
        == "rebar-python-re-public-contract-v10-all-candidates"
        and historical_all.get("status") == "PASS"
        and historical_all.get("cases_per_candidate") == EXPECTED_CASES
        and historical_all.get("candidate_checks") == EXPECTED_CASES * 3
        and historical_all.get("completed_candidates")
        == list(REQUIRED_CANDIDATES)
        and historical_all.get("self_oracle_sha256") == STAGE10_SELF_SHA256
        and historical_all_sha == STAGE10_ALL_SHA256
        and isinstance(historical_all.get("current_provenance"), dict)
        and historical_all["current_provenance"].get("native_sha256_by_family")
        != graph["native_sha256_by_family"],
        "the genuinely historical universal result was substituted for new engines",
    )

    source = official_locale.checked_repo_path(SOURCE_RELATIVE)
    protocol = official_locale.checked_repo_path(PROTOCOL_RELATIVE)
    source_sha = official_locale.sha256_path(
        source, maximum=frozen.MAX_SOURCE_BYTES,
    )
    protocol_sha = official_locale.sha256_path(
        protocol, maximum=frozen.MAX_SOURCE_BYTES,
    )
    validate_matrix(build_matrix())
    frozen.candidate_free()
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha,
        "seed": SEED, "seed_domain": SEED_DOMAIN,
        "observation_domain": OBSERVATION_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "base_audit_source_path": V7_BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": V7_BASE_SOURCE_SHA256,
        "base_audit_path": V7_BASE_REPORT_RELATIVE,
        "base_audit_sha256": V7_BASE_REPORT_SHA256,
        "strict_audit_source_path": V7_STRICT_SOURCE_RELATIVE,
        "strict_audit_source_sha256": V7_STRICT_SOURCE_SHA256,
        "strict_audit_path": V7_STRICT_REPORT_RELATIVE,
        "strict_audit_sha256": V7_STRICT_REPORT_SHA256,
        "source_sha256_by_family": {
            family: {
                relative: sources[relative]
                for relative in source_v7.source_v6.OWNED_SOURCE_PATHS[family]
            }
            for family in REQUIRED_CANDIDATES
        },
        "native_sha256_by_family": graph["native_sha256_by_family"],
        "native_source_count": 12, "native_binary_count": 5,
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
        "stage14_self_oracle_path": STAGE14_SELF_RELATIVE,
        "stage14_self_oracle_sha256": STAGE14_SELF_SHA256,
        "stage14_all_candidate_path": STAGE14_ALL_RELATIVE,
        "stage14_all_candidate_sha256": STAGE14_ALL_SHA256,
        "stage14_cases_per_candidate": 128,
        "stage14_candidate_checks": 384,
        "historical_stage10_self_oracle_path": STAGE10_SELF_RELATIVE,
        "historical_stage10_self_oracle_sha256": STAGE10_SELF_SHA256,
        "historical_stage10_all_candidate_path": STAGE10_ALL_RELATIVE,
        "historical_stage10_all_candidate_sha256": STAGE10_ALL_SHA256,
        "historical_stage10_only": True,
        "historical_stage10_qualifies_current_sources": False,
        "stage10_provenance": {
            "native_sha256_by_family": historical_all[
                "current_provenance"
            ]["native_sha256_by_family"],
        },
    }


def _authenticate_provenance() -> dict[str, Any]:
    """Expose the current full-proof authenticator to later public oracles."""

    return _authenticate_current_provenance()


@contextmanager
def _stage15_context() -> Iterator[None]:
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
        "build_matrix": build_matrix,
        "validate_matrix": validate_matrix,
        "_authenticate_current_provenance": _authenticate_current_provenance,
        "_worker_report": stage10._worker_report,
        "_run_worker": stage10._run_worker,
        "_worker_environment": stage10._worker_environment,
        "_surface_obligation": stage10._surface_obligation,
    }
    with stage10.previous._stage08_context():
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
    with _stage15_context():
        return stage10._metadata_worker_entry(role, source_sha256)


def _worker_entry(role: str, source_sha256: str) -> int:
    with _stage15_context():
        return stage10._worker_entry(role, source_sha256)


def _validate_complete_reference(document: Any,
                                 provenance: dict[str, Any]) -> dict[str, Any]:
    frozen.require(isinstance(document, dict),
                   "two actual complete standard-Python streams are missing")
    expected: dict[str, Any] = {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED, "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256, "cohorts": 8,
        "cohort_cases": {
            name: count for name, _operation, count in stage07.COHORTS
        },
        "cases": EXPECTED_CASES,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "stdlib_checks": EXPECTED_CASES * 2,
        "mismatches": 0, "failure_records": [],
        "candidate_imports": 0, "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, value in expected.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "a complete genuine Python reference changed: " + name,
        )
    first = document.get("baseline_records")
    second = document.get("second_records")
    frozen.require(
        isinstance(first, list) and isinstance(second, list)
        and len(first) == EXPECTED_CASES
        and len(second) == EXPECTED_CASES
        and all(isinstance(record, dict) for record in first)
        and all(isinstance(record, dict) for record in second)
        and first == second
        and [record.get("id") for record in first]
        == [row["id"] for row in build_matrix()]
        and [record.get("id") for record in second]
        == [row["id"] for row in build_matrix()]
        and digest(first) == document.get("baseline_record_sha256")
        and digest(second) == document.get("second_record_sha256")
        and document.get("current_provenance") == provenance,
        "a complete real standard-Python comparison was omitted or fabricated",
    )
    workers = document.get("reference_worker_reports")
    frozen.require(
        isinstance(workers, dict)
        and set(workers) == {"stdlib-a", "stdlib-b"},
        "the complete Python reference omitted a genuine isolated worker",
    )
    for role, records in (("stdlib-a", first), ("stdlib-b", second)):
        worker = workers[role]
        frozen.require(
            isinstance(worker, dict)
            and worker.get("schema") == SCHEMA + "-worker"
            and worker.get("status") == "PASS"
            and worker.get("role") == role
            and worker.get("python") == "3.14.6"
            and worker.get("source_sha256") == provenance["source_sha256"]
            and worker.get("seed") == SEED
            and worker.get("seed_domain") == SEED_DOMAIN
            and worker.get("matrix_sha256") == MATRIX_SHA256
            and worker.get("cases") == EXPECTED_CASES
            and worker.get("cohort_cases") == expected["cohort_cases"]
            and isinstance(worker.get("records"), list)
            and len(worker["records"]) == EXPECTED_CASES
            and worker["records"] == records
            and worker.get("record_sha256") == digest(records)
            and worker.get("guard")
            == {"baseline_only": True, "candidate_imported": False}
            and worker.get("native_binary_sha256") == {}
            and worker.get("benchmark_or_timing_executed") is False
            and worker.get("performance_fixtures_read") == 0
            and worker.get("holdout_cases_read") == 0
            and worker.get("performance") == "NOT MEASURED",
            "a genuine complete Python worker was concealed: " + role,
        )
    return document


def run_self_oracle() -> dict[str, Any]:
    with _stage15_context():
        provenance = _authenticate_current_provenance()
        destination = ROOT / SELF_ORACLE_RELATIVE
        frozen.require(not destination.exists() and not destination.is_symlink(),
                       "the exclusive stage-fifteen Python baseline already exists")
        frozen.candidate_free()
        with tempfile.TemporaryDirectory(
            prefix="rebar-public-contract-v15-locale-", dir="/tmp",
        ) as temporary:
            locale_root = Path(temporary)
            locales = stage07._locale_metadata(locale_root)
            baseline_a: dict[str, Any] | None = None
            baseline_b: dict[str, Any] | None = None
            for role in ("stdlib-a", "stdlib-b"):
                try:
                    result = stage07._run_worker(
                        role, source_sha256=provenance["source_sha256"],
                        locale_root=locale_root,
                    )
                except (Exception, RecursionError) as error:
                    retained = stage07._preserve_worker_failure(
                        role=role, error=error,
                        provenance=provenance, locales=locales,
                        baseline_records=(
                            baseline_a["records"] if baseline_a else None
                        ),
                    )
                    raise frozen.OracleIntegrityError(
                        "the genuine Python reference failure is preserved in "
                        + retained
                    ) from error
                if role == "stdlib-a":
                    baseline_a = result
                else:
                    baseline_b = result
            frozen.require(
                isinstance(baseline_a, dict)
                and isinstance(baseline_b, dict),
                "two genuine standard-Python processes did not complete",
            )
            mismatches, failures = stage07._mismatch_records(
                baseline_a["records"], baseline_b["records"],
            )
            report: dict[str, Any] = {
                "schema": SELF_ORACLE_SCHEMA,
                "status": "PASS" if not mismatches else "FAIL",
                "result": "PASS" if not mismatches else "FAIL",
                "python": "3.14.6",
                "source_path": SOURCE_RELATIVE,
                "source_sha256": provenance["source_sha256"],
                "protocol_path": PROTOCOL_RELATIVE,
                "protocol_sha256": provenance["protocol_sha256"],
                "seed": SEED, "seed_domain": SEED_DOMAIN,
                "matrix_sha256": MATRIX_SHA256,
                "cohorts": len(stage07.COHORTS),
                "cohort_cases": {
                    name: count for name, _operation, count in stage07.COHORTS
                },
                "cases": EXPECTED_CASES,
                "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
                "stdlib_checks": EXPECTED_CASES * 2,
                "baseline_record_sha256": baseline_a["record_sha256"],
                "second_record_sha256": baseline_b["record_sha256"],
                "baseline_records": baseline_a["records"],
                "second_records": baseline_b["records"],
                "reference_worker_reports": {
                    "stdlib-a": baseline_a,
                    "stdlib-b": baseline_b,
                },
                "mismatches": mismatches,
                "failure_records": failures,
                "current_provenance": provenance,
                "locales": locales,
                "candidate_imports": 0, "candidate_processes": 0,
                "benchmark_or_timing_executed": False,
                "performance_fixtures_read": 0,
                "holdout_cases_read": 0,
                "performance": "NOT MEASURED",
            }
            if mismatches:
                report["schema"] = SELF_ORACLE_SCHEMA + "-failure"
                report["failures_recorded"] = len(failures)
                evidence = stage07._exclusive_evidence(
                    report, SELF_ORACLE_FAILURE_RELATIVE,
                )
                raise frozen.OracleIntegrityError(
                    "two genuine Python workers disagree on " + str(mismatches)
                    + " full cases; failure preserved in "
                    + SELF_ORACLE_FAILURE_RELATIVE + " (sha256 " + evidence + ")"
                )
            _validate_complete_reference(report, provenance)
            evidence = stage07._exclusive_evidence(
                report, SELF_ORACLE_RELATIVE,
            )
        frozen.candidate_free()
        return {
            "schema": SELF_ORACLE_SCHEMA,
            "status": "PASS", "result": "PASS",
            "cases": EXPECTED_CASES,
            "stdlib_checks": EXPECTED_CASES * 2,
            "complete_reference_record_arrays": 2,
            "mismatches": 0,
            "evidence": SELF_ORACLE_RELATIVE,
            "evidence_sha256": evidence,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }


def run_all_candidates() -> dict[str, Any]:
    with _stage15_context():
        provenance = _authenticate_current_provenance()
        destination = ROOT / ALL_CANDIDATE_RELATIVE
        frozen.require(not destination.exists() and not destination.is_symlink(),
                       "the exclusive rebuilt all-candidate report already exists")
        baseline, baseline_sha = stage06._read_public_document(
            SELF_ORACLE_RELATIVE, expected_sha256=None,
        )
        reference = _validate_complete_reference(baseline, provenance)
        expected = reference["baseline_records"]
        reports: dict[str, dict[str, Any]] = {}
        with tempfile.TemporaryDirectory(
            prefix="rebar-public-contract-v15-locale-", dir="/tmp",
        ) as temporary:
            locale_root = Path(temporary)
            locales = stage07._locale_metadata(locale_root)
            frozen.require(locales == reference.get("locales"),
                           "candidate locales differ from the genuine baseline")
            for role in REQUIRED_CANDIDATES:
                try:
                    worker = stage07._run_worker(
                        role, source_sha256=provenance["source_sha256"],
                        locale_root=locale_root,
                    )
                except (Exception, RecursionError) as error:
                    retained = stage07._preserve_worker_failure(
                        role=role, error=error,
                        provenance=provenance, locales=locales,
                        baseline_records=expected,
                        completed_reports=reports,
                        self_oracle_sha256=baseline_sha,
                    )
                    raise frozen.OracleIntegrityError(
                        "the genuinely guarded " + role
                        + " worker failure is preserved in " + retained
                    ) from error
                actual = worker.get("records")
                frozen.require(
                    isinstance(actual, list)
                    and len(actual) == EXPECTED_CASES
                    and all(isinstance(row, dict) for row in actual)
                    and [row.get("id") for row in actual]
                    == [row["id"] for row in build_matrix()]
                    and digest(actual) == worker.get("record_sha256"),
                    "a full native worker omitted or substituted real records: "
                    + role,
                )
                mismatches, failures = stage07._mismatch_records(
                    expected, actual,
                )
                outcome: dict[str, Any] = {
                    "candidate": role,
                    "module": "candidates." + role + "_candidate",
                    "status": "PASS" if not mismatches else "FAIL",
                    "cases": EXPECTED_CASES,
                    "cohort_cases": worker["cohort_cases"],
                    "records": actual,
                    "record_sha256": worker["record_sha256"],
                    "mismatches": mismatches,
                    "failure_records": failures,
                    "failures_recorded": len(failures),
                    "native_binary_sha256": worker["native_binary_sha256"],
                    "guard": worker["guard"],
                    "benchmark_or_timing_executed": False,
                    "performance_fixtures_read": 0,
                    "holdout_cases_read": 0,
                    "performance": "NOT MEASURED",
                }
                reports[role] = outcome
                if mismatches:
                    failure = {
                        "schema": ALL_CANDIDATE_SCHEMA + "-failure",
                        "status": "FAIL", "result": "FAIL",
                        "candidate": role,
                        "module": "candidates." + role + "_candidate",
                        "python": "3.14.6",
                        "source_path": SOURCE_RELATIVE,
                        "source_sha256": provenance["source_sha256"],
                        "protocol_path": PROTOCOL_RELATIVE,
                        "protocol_sha256": provenance["protocol_sha256"],
                        "seed": SEED, "seed_domain": SEED_DOMAIN,
                        "matrix_sha256": MATRIX_SHA256,
                        "cohorts": 8,
                        "cohort_cases": worker["cohort_cases"],
                        "cases": EXPECTED_CASES,
                        "self_oracle_path": SELF_ORACLE_RELATIVE,
                        "self_oracle_sha256": baseline_sha,
                        "baseline_record_sha256": reference[
                            "baseline_record_sha256"
                        ],
                        "candidate_record_sha256": worker["record_sha256"],
                        "baseline_records": expected,
                        "second_reference_records": reference["second_records"],
                        "candidate_records": actual,
                        "mismatches": mismatches,
                        "failure_records": failures,
                        "failures_recorded": len(failures),
                        "completed_candidate_reports": reports,
                        "current_provenance": provenance,
                        "locales": locales,
                        "native_binary_sha256": worker["native_binary_sha256"],
                        "guard": worker["guard"],
                        "benchmark_or_timing_executed": False,
                        "performance_fixtures_read": 0,
                        "holdout_cases_read": 0,
                        "performance": "NOT MEASURED",
                    }
                    path = CANDIDATE_FAILURE_RELATIVES[role]
                    evidence = stage07._exclusive_evidence(failure, path)
                    raise frozen.OracleIntegrityError(
                        "the " + role + " candidate failed " + str(mismatches)
                        + " actual public cases; every row was preserved in "
                        + path + " (sha256 " + evidence + ")"
                    )
                frozen.require(
                    actual == expected
                    and worker["record_sha256"]
                    == reference["baseline_record_sha256"],
                    "a candidate's complete real answer array disagrees: " + role,
                )
            frozen.require(set(reports) == set(REQUIRED_CANDIDATES),
                           "the full rebuilt comparison omitted a native family")
            evidence_document = {
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
                "cohorts": 8,
                "cohort_cases": {
                    name: count for name, _operation, count in stage07.COHORTS
                },
                "cases_per_candidate": EXPECTED_CASES,
                "candidate_checks": EXPECTED_CASES * 3,
                "baseline_records": expected,
                "second_reference_records": reference["second_records"],
                "baseline_record_sha256": reference["baseline_record_sha256"],
                "second_record_sha256": reference["second_record_sha256"],
                "candidate_reports": reports,
                "mismatches": 0,
                "self_oracle_path": SELF_ORACLE_RELATIVE,
                "self_oracle_sha256": baseline_sha,
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
                evidence_document, reference=reference, provenance=provenance,
            )
            evidence = stage07._exclusive_evidence(
                evidence_document, ALL_CANDIDATE_RELATIVE,
            )
        frozen.candidate_free()
        return {
            "schema": ALL_CANDIDATE_SCHEMA,
            "status": "PASS", "result": "PASS", "selected": "all",
            "cases_per_candidate": EXPECTED_CASES,
            "candidate_checks": EXPECTED_CASES * 3,
            "complete_candidate_record_arrays": 3,
            "complete_reference_record_arrays": 2,
            "mismatches": 0,
            "evidence": ALL_CANDIDATE_RELATIVE,
            "evidence_sha256": evidence,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }


def _validate_complete_all(document: Any, *,
                           reference: dict[str, Any],
                           provenance: dict[str, Any]) -> dict[str, Any]:
    expected: dict[str, Any] = {
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
        "cohorts": 8,
        "cohort_cases": {
            name: count for name, _operation, count in stage07.COHORTS
        },
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": EXPECTED_CASES * 3,
        "baseline_record_sha256": reference["baseline_record_sha256"],
        "second_record_sha256": reference["second_record_sha256"],
        "mismatches": 0,
        "self_oracle_path": SELF_ORACLE_RELATIVE,
        "candidate_cross_delegation": False,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen.require(isinstance(document, dict),
                   "the full actual three-engine evidence is missing")
    for name, value in expected.items():
        frozen.require(document.get(name) == value
                       and type(document.get(name)) is type(value),
                       "the full three-engine evidence changed: " + name)
    first = document.get("baseline_records")
    second = document.get("second_reference_records")
    frozen.require(
        first == reference["baseline_records"]
        and second == reference["second_records"]
        and isinstance(first, list)
        and isinstance(second, list)
        and len(first) == EXPECTED_CASES
        and len(second) == EXPECTED_CASES
        and digest(first) == reference["baseline_record_sha256"]
        and digest(second) == reference["second_record_sha256"]
        and document.get("self_oracle_sha256")
        == stage07.hashlib.sha256(canonical(reference) + b"\n").hexdigest()
        and document.get("current_provenance") == provenance,
        "the final full comparison omitted a complete actual Python reference",
    )
    reports = document.get("candidate_reports")
    frozen.require(isinstance(reports, dict)
                   and set(reports) == set(REQUIRED_CANDIDATES),
                   "the full comparison omitted an independently owned candidate")
    expected_ids = [row["id"] for row in build_matrix()]
    for role in REQUIRED_CANDIDATES:
        candidate = reports[role]
        frozen.require(
            isinstance(candidate, dict)
            and candidate.get("candidate") == role
            and candidate.get("module") == "candidates." + role + "_candidate"
            and candidate.get("status") == "PASS"
            and candidate.get("cases") == EXPECTED_CASES
            and candidate.get("cohort_cases")
            == {name: count for name, _operation, count in stage07.COHORTS}
            and candidate.get("mismatches") == 0
            and candidate.get("failure_records") == []
            and candidate.get("failures_recorded") == 0
            and candidate.get("native_binary_sha256")
            == provenance["native_sha256_by_family"][role]
            and candidate.get("benchmark_or_timing_executed") is False
            and candidate.get("performance_fixtures_read") == 0
            and candidate.get("holdout_cases_read") == 0
            and candidate.get("performance") == "NOT MEASURED",
            "the complete native candidate provenance is invalid: " + role,
        )
        records = candidate.get("records")
        frozen.require(
            isinstance(records, list)
            and len(records) == EXPECTED_CASES
            and all(isinstance(record, dict) for record in records)
            and [record.get("id") for record in records] == expected_ids
            and records == first
            and digest(records) == candidate.get("record_sha256"),
            "the candidate concealed or changed a full actual answer: " + role,
        )
        guard = candidate.get("guard")
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
            "the complete answer used an unowned matcher or metadata process: "
            + role,
        )
    return document


def _synthetic_stage14() -> tuple[Any, dict[str, Any], dict[str, Any], dict[str, Any]]:
    rows = []
    for original in old_aliases.build_matrix():
        row = dict(original)
        row["seed"] = digest({
            "domain": STAGE14_SEED_DOMAIN,
            "seed": STAGE14_SEED,
            "cohort": row["cohort"],
        })
        rows.append(row)
    frozen.require(
        len(rows) == 128 and digest(rows) == STAGE14_MATRIX_SHA256,
        "the synthetic generic-alias control changed the genuine frozen matrix",
    )
    module = types.SimpleNamespace(
        SEED=STAGE14_SEED,
        SEED_DOMAIN=STAGE14_SEED_DOMAIN,
        MATRIX_SHA256=STAGE14_MATRIX_SHA256,
        build_matrix=lambda: [dict(row) for row in rows],
    )
    native = {
        role: {
            path: digest({"synthetic": True, "native": path})
            for path in source_v7.source_v6.OWNED_NATIVE_PATHS[role].values()
        }
        for role in REQUIRED_CANDIDATES
    }
    current = {"native_sha256_by_family": native}
    actual_records = [
        {"id": row["id"], "cohort": row["cohort"],
         "status": "returned", "value": None, "warnings": []}
        for row in rows
    ]
    second_records = [dict(row) for row in actual_records]
    record_sha = digest(actual_records)
    baseline_origins = {
        name: {
            "public_name": name, "actual_name": name,
            "actual_qualified_name": name, "actual_module": "re",
        }
        for name in ("Pattern", "Match")
    }
    reference_workers = {
        role: {
            "schema": "rebar-python-re-public-generic-alias-v14-worker",
            "status": "PASS", "role": role, "python": "3.14.6",
            "source_sha256": STAGE14_SOURCE_SHA256,
            "seed": STAGE14_SEED, "seed_domain": STAGE14_SEED_DOMAIN,
            "matrix_sha256": STAGE14_MATRIX_SHA256,
            "cases": 128, "cohort_cases": dict(old_aliases.COHORTS),
            "records": [dict(row) for row in actual_records],
            "record_sha256": record_sha,
            "guard": {"baseline_only": True, "candidate_imported": False},
            "native_binary_sha256": {},
            "public_origins": baseline_origins,
            "inspect_loaded": False, "tokenize_loaded": False,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0, "performance": "NOT MEASURED",
        }
        for role in ("stdlib-a", "stdlib-b")
    }
    reference = {
        "schema": "rebar-python-re-public-generic-alias-v14-self-oracle",
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": STAGE14_SOURCE_RELATIVE,
        "source_sha256": STAGE14_SOURCE_SHA256,
        "protocol_path": STAGE14_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE14_PROTOCOL_SHA256,
        "seed": module.SEED, "seed_domain": module.SEED_DOMAIN,
        "matrix_sha256": module.MATRIX_SHA256,
        "cohorts": 4, "cohort_cases": dict(old_aliases.COHORTS),
        "cases": 128, "stdlib_checks": 256,
        "baseline_records": actual_records,
        "second_records": second_records,
        "reference_worker_reports": reference_workers,
        "baseline_record_sha256": record_sha,
        "second_record_sha256": record_sha,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "mismatches": 0, "failure_records": [],
        "current_provenance": current,
        "candidate_imports": 0, "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    candidate_reports: dict[str, dict[str, Any]] = {}
    for role in REQUIRED_CANDIDATES:
        guard = {
            "enabled": True, "family": role,
            "stdlib_re_blocked": True, "cpython_sre_blocked": True,
            "third_party_regex_blocked": True, "cross_family_blocked": True,
            "foreign_dynamic_libraries_blocked": True,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
            "matcher_inspect_loaded": False,
            "matcher_tokenizer_loaded": False,
        }
        candidate_reports[role] = {
            "candidate": role,
            "module": "candidates." + role + "_candidate",
            "status": "PASS", "cases": 128,
            "cohort_cases": dict(old_aliases.COHORTS),
            "records": [dict(row) for row in actual_records],
            "mismatches": 0, "failure_records": [],
            "failures_recorded": 0, "record_sha256": record_sha,
            "native_binary_sha256": native[role], "guard": guard,
            "public_origins": {
                name: {
                    "public_name": name,
                    "actual_name": name,
                    "actual_qualified_name": name,
                    "actual_module": (
                        {
                            "rust": "candidates._rust_bridge",
                            "vm": "candidates._vm_native",
                            "zig": "candidates._zig_bridge",
                        }[role]
                        if name == "Match"
                        else "candidates." + role + "_candidate"
                    ),
                }
                for name in ("Pattern", "Match")
            },
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0, "performance": "NOT MEASURED",
        }
    all_report = {
        "schema": "rebar-python-re-public-generic-alias-v14-all-candidates",
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": STAGE14_SOURCE_RELATIVE,
        "source_sha256": STAGE14_SOURCE_SHA256,
        "protocol_path": STAGE14_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE14_PROTOCOL_SHA256,
        "seed": module.SEED, "seed_domain": module.SEED_DOMAIN,
        "matrix_sha256": module.MATRIX_SHA256,
        "cohorts": 4, "cohort_cases": dict(old_aliases.COHORTS),
        "cases_per_candidate": 128,
        "candidate_checks": 384,
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        "candidate_cross_delegation": False,
        "mismatches": 0,
        "self_oracle_path": STAGE14_SELF_RELATIVE,
        "self_oracle_sha256": STAGE14_SELF_SHA256,
        "baseline_records": [dict(row) for row in actual_records],
        "second_reference_records": [dict(row) for row in second_records],
        "second_records": [dict(row) for row in second_records],
        "baseline_record_sha256": record_sha,
        "second_record_sha256": record_sha,
        "reference_worker_reports": reference_workers,
        "candidate_reports": candidate_reports,
        "current_provenance": current,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    return module, current, reference, all_report


def _synthetic_full() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    native = {
        role: {
            path: digest({"stage15_synthetic": True, "native": path})
            for path in source_v7.source_v6.OWNED_NATIVE_PATHS[role].values()
        }
        for role in REQUIRED_CANDIDATES
    }
    provenance = {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": "a" * 64,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": "b" * 64,
        "native_sha256_by_family": native,
    }
    records = [
        {"id": row["id"], "cohort": row["cohort"],
         "status": "returned", "value": None, "warnings": []}
        for row in build_matrix()
    ]
    second = [dict(row) for row in records]
    record_sha = digest(records)
    cohort_cases = {
        name: count for name, _operation, count in stage07.COHORTS
    }
    reference_workers = {
        role: {
            "schema": SCHEMA + "-worker", "status": "PASS",
            "role": role, "python": "3.14.6",
            "source_sha256": provenance["source_sha256"],
            "seed": SEED, "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cases": EXPECTED_CASES, "cohort_cases": cohort_cases,
            "records": [dict(row) for row in records],
            "record_sha256": record_sha,
            "guard": {"baseline_only": True, "candidate_imported": False},
            "native_binary_sha256": {},
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0, "performance": "NOT MEASURED",
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
        "cohorts": 8,
        "cohort_cases": cohort_cases,
        "cases": EXPECTED_CASES,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "stdlib_checks": EXPECTED_CASES * 2,
        "baseline_record_sha256": record_sha,
        "second_record_sha256": record_sha,
        "baseline_records": records,
        "second_records": second,
        "reference_worker_reports": reference_workers,
        "mismatches": 0, "failure_records": [],
        "current_provenance": provenance,
        "candidate_imports": 0, "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    outcomes: dict[str, dict[str, Any]] = {}
    for role in REQUIRED_CANDIDATES:
        metadata = {
            "enabled": True, "schema": METADATA_SCHEMA,
            "role": role, "source_sha256": provenance["source_sha256"],
            "surface_cases": 256,
            "record_sha256": digest({"synthetic_metadata": True, "role": role}),
            "production_matching_executed": False,
            "metadata_and_matcher_processes_distinct": True,
            "matcher_inspect_loaded": False,
            "matcher_tokenizer_loaded": False,
        }
        guard = {
            "enabled": True, "family": role,
            "stdlib_re_blocked": True, "cpython_sre_blocked": True,
            "third_party_regex_blocked": True,
            "cross_family_blocked": True,
            "foreign_dynamic_libraries_blocked": True,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
            "isolated_public_metadata": metadata,
        }
        outcomes[role] = {
            "candidate": role,
            "module": "candidates." + role + "_candidate",
            "status": "PASS", "cases": EXPECTED_CASES,
            "cohort_cases": reference["cohort_cases"],
            "records": [dict(row) for row in records],
            "record_sha256": record_sha,
            "mismatches": 0, "failure_records": [],
            "failures_recorded": 0,
            "native_binary_sha256": native[role],
            "guard": guard,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
    all_report = {
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
        "cohorts": 8,
        "cohort_cases": reference["cohort_cases"],
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": EXPECTED_CASES * 3,
        "baseline_records": records,
        "second_reference_records": reference["second_records"],
        "baseline_record_sha256": record_sha,
        "second_record_sha256": record_sha,
        "candidate_reports": outcomes,
        "mismatches": 0,
        "self_oracle_path": SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": stage07.hashlib.sha256(
            canonical(reference) + b"\n",
        ).hexdigest(),
        "current_provenance": provenance,
        "candidate_cross_delegation": False,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    return provenance, reference, all_report


def _synthetic_official_v3() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any],
]:
    """Build all 584 official-method controls in memory, without a candidate."""

    source_fingerprints = {
        relative: digest({"synthetic_official_source": relative})
        for role in REQUIRED_CANDIDATES
        for relative in source_v7.source_v6.OWNED_SOURCE_PATHS[role]
    }
    native_fingerprints = {
        role + ":" + label: digest({"synthetic_official_native": relative})
        for role in REQUIRED_CANDIDATES
        for label, relative in
        source_v7.source_v6.OWNED_NATIVE_PATHS[role].items()
    }
    base: dict[str, Any] = {"synthetic_only": True}
    strict = {
        "qualified_source_fingerprints": source_fingerprints,
        "native_elf_fingerprints": native_fingerprints,
    }
    names = [
        "ExternalTests.test_re_tests",
        "ReTests.test_match_repr",
        "ReTests.test_locale_caching",
        "ReTests.test_locale_compiled",
        *("SyntheticTests.test_" + f"{index:03d}" for index in range(142)),
    ]
    records = [
        {"test": name, "status": "passed", "skipped": 0, "reason": None}
        for name in names
    ]
    roles = {
        role: {
            "module": "re" if role == "re"
            else "candidates." + role + "_candidate",
            "methods": 146, "passed": 146, "failed": 0,
            "failures": 0, "errors": 0, "skipped": 0,
            "crashes": 0, "timeouts": 0,
            "locale_caching_passed": True,
            "locale_compiled_passed": True,
            "records": [dict(record) for record in records],
            "holdout_accessed": False, "timing_performed": False,
            "performance": "NOT MEASURED",
        }
        for role in ("re", *REQUIRED_CANDIDATES)
    }
    document = {
        "schema": "rebar-postfinal-cpython-public-locale-v3",
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": OFFICIAL_SOURCE_RELATIVE,
        "source_sha256": OFFICIAL_SOURCE_SHA256,
        "goal_sha256": GOAL_SHA256,
        "qualified_source_fingerprints": source_fingerprints,
        "native_elf_fingerprints": native_fingerprints,
        "holdout_accessed": False, "timing_performed": False,
        "performance": "NOT MEASURED",
        "audits": {
            "from_scratch": {
                "path": V7_BASE_REPORT_RELATIVE,
                "sha256": V7_BASE_REPORT_SHA256,
                "source_path": V7_BASE_SOURCE_RELATIVE,
                "source_sha256": V7_BASE_SOURCE_SHA256,
            },
            "no_delegation": {
                "path": V7_STRICT_REPORT_RELATIVE,
                "sha256": V7_STRICT_REPORT_SHA256,
                "source_path": V7_STRICT_SOURCE_RELATIVE,
                "source_sha256": V7_STRICT_SOURCE_SHA256,
            },
        },
        "original_oracle": {
            "selected_methods": 146, "total_public_methods": 152,
            "corpus_cases": 403,
            "selected_method_sha256": OFFICIAL_SELECTED_METHOD_SHA256,
            "runner_path": "tools/cpython_re_oracle.py",
            "runner_sha256": (
                "d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb"
            ),
            "manifest_path": "oracle/cpython-3.14.6/manifest.json",
            "manifest_sha256": (
                "2c89ce37e474cb6f59d61f86ad810662b50b83bbdce3610c04523fe092688597"
            ),
            "all_named_waivers": {
                name: {"synthetic_only": True}
                for name in (
                    "DebugTests", "ImplementationTest",
                    "ReTests.test_large_search", "ReTests.test_large_subn",
                    "ReTests.test_memory_leaks",
                    "ReTests.test_re_groupref_overflow",
                    "ReTests.test_regression_gh94675",
                    "ReTests.test_search_anchor_at_beginning",
                )
            },
        },
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
        "roles": roles,
    }
    return document, base, strict


def self_test() -> dict[str, Any]:
    """Reject fabricated proofs in memory without files, workers, or timing."""

    frozen.candidate_free()
    universal = stage10.self_test()
    owned = source_v7.self_test()
    official = official_v3.self_test()
    frozen.require(
        universal.get("status") == "PASS"
        and universal.get("check_count", 0) >= 793
        and universal.get("candidate_imports") == 0
        and universal.get("candidate_processes") == 0
        and universal.get("files_read") == 0
        and universal.get("files_written") == 0
        and universal.get("clock_samples") == 0
        and universal.get("holdout_cases_read") == 0
        and universal.get("benchmark_or_timing_executed") is False,
        "the complete frozen universal source controls were weakened",
    )
    frozen.require(
        owned.get("status") == "PASS"
        and owned.get("passed") is True
        and owned.get("check_count", 0) >= 468
        and owned.get("candidate_imports") == 0
        and owned.get("file_reads") == 0
        and owned.get("file_writes") == 0
        and owned.get("subprocesses") == 0
        and owned.get("clock_samples") == 0,
        "the repaired twelve-source, five-native V7 controls were weakened",
    )
    frozen.require(
        official.get("status") == "PASS"
        and official.get("passed") is True
        and official.get("check_count", 0) >= 96
        and official.get("candidate_imports") == 0
        and official.get("candidate_processes") == 0
        and official.get("files_read") == 0
        and official.get("files_written") == 0
        and official.get("subprocesses") == 0
        and official.get("clock_samples") == 0
        and official.get("official_tests_executed") == 0
        and official.get("holdout_accessed") is False
        and official.get("timing_performed") is False,
        "the genuine repaired official Python source controls were weakened",
    )

    with stage06.previous._candidate_free_file_and_timing_guard() as effects:
        checks: list[dict[str, Any]] = []

        def check(name: str, condition: Any) -> None:
            frozen.require(
                type(name) is str and bool(condition),
                "a repaired universal synthetic control failed: " + str(name),
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

        for prefix, inherited in (
            ("frozen-v10/", universal),
            ("repaired-v7/", owned),
            ("official-v3/", official),
        ):
            for item in inherited["checks"]:
                check(prefix + item["name"], item.get("passed") is True)
        check("retain-all-793-full-universal-synthetic-controls",
              universal["check_count"] >= 793)
        check("retain-all-468-repaired-native-independence-controls",
              owned["check_count"] >= 468)
        check("retain-all-96-repaired-official-cpython-controls",
              official["check_count"] >= 96)

        matrix = build_matrix()
        check("freeze-all-3584-original-public-obligations",
              len(matrix) == EXPECTED_CASES and digest(matrix) == MATRIX_SHA256)
        check("retain-the-original-eight-obligation-identities",
              len(stage07.COHORTS) == 8
              and len({row["id"] for row in matrix}) == EXPECTED_CASES)
        check("refresh-only-the-explicit-frozen-stage15-seed",
              SEED == 2026072479
              and SEED_DOMAIN == "rebar/python-re/public-contract/v15"
              and MATRIX_SHA256 != ORIGINAL_MATRIX_SHA256)
        check("retain-the-authenticated-33-public-exports",
              len(stage10.SURFACE_EXPORTS) == 33
              and {"Scanner", "Pattern", "Match", "RegexFlag", "NOFLAG",
                   "PatternError", "error", "purge"}
              <= set(stage10.SURFACE_EXPORTS))
        for cohort, _operation, count in stage07.COHORTS:
            check("retain-exact-frozen-obligation-cohort/" + cohort,
                  sum(row["cohort"] == cohort for row in matrix) == count)
        locales = [row for row in matrix if row["cohort"] == "real-locale"]
        check("retain-all-256-real-locale-bytes-and-switch-states",
              {(row["byte"], row["locale"], row["compiled_before_switch"])
               for row in locales}
              == {(byte, locale, switched)
                  for byte in range(256)
                  for locale in ("iso88591", "utf8")
                  for switched in (False, True)})
        threaded = [
            row for row in matrix if row["cohort"] == "shared-pattern-threads"
        ]
        for size in (4, 8):
            check("retain-128-real-" + str(size) + "-thread-cases",
                  sum(row["threads"] == size for row in threaded) == 128)
        check("isolate-authenticated-signatures-from-real-matching",
              METADATA_WORKER_BOOTSTRAP != WORKER_BOOTSTRAP
              and "_metadata_worker_entry" in METADATA_WORKER_BOOTSTRAP
              and "_worker_entry" in WORKER_BOOTSTRAP)
        check("publish-one-current-proof-authenticator-for-later-public-oracles",
              callable(_authenticate_current_provenance)
              and callable(_authenticate_provenance))
        check("never-import-inspect-or-tokenize-into-matching-source",
              "inspect" not in globals() and "tokenize" not in globals())
        check("deny-all-five-actual-foreign-native-loader-aliases",
              tuple(stage07.NATIVE_LOADER_ALIASES) == NATIVE_LOADER_ALIASES)
        check("retain-twelve-truly-owned-native-source-paths",
              sum(len(source_v7.source_v6.OWNED_SOURCE_PATHS[role])
                  for role in REQUIRED_CANDIDATES) == 12)
        check("retain-five-truly-owned-native-binary-paths",
              sum(len(source_v7.source_v6.OWNED_NATIVE_PATHS[role])
                  for role in REQUIRED_CANDIDATES) == 5)
        check("preserve-all-7168-actual-independent-python-obligations",
              EXPECTED_CASES * 2 == 7_168)
        check("preserve-all-10752-actual-independent-native-obligations",
              EXPECTED_CASES * len(REQUIRED_CANDIDATES) == 10_752)
        check("preserve-all-584-genuine-official-python-methods",
              146 * (1 + len(REQUIRED_CANDIDATES)) == 584)
        check("preserve-the-first-genuine-145-of-146-rust-failure",
              OFFICIAL_FAILURE_SHA256
              == "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f")
        for label, fingerprint in (
            ("base-audit-source", V7_BASE_SOURCE_SHA256),
            ("base-audit-report", V7_BASE_REPORT_SHA256),
            ("strict-audit-source", V7_STRICT_SOURCE_SHA256),
            ("strict-audit-report", V7_STRICT_REPORT_SHA256),
            ("official-source", OFFICIAL_SOURCE_SHA256),
            ("official-protocol", OFFICIAL_PROTOCOL_SHA256),
            ("official-report", OFFICIAL_REPORT_SHA256),
            ("historical-failure", OFFICIAL_FAILURE_SHA256),
        ):
            check("pin-an-actually-published-current-proof/" + label,
                  official_locale.is_sha256(fingerprint))

        for label, poisoned in (
            ("omitted-case", matrix[:-1]),
            ("duplicated-case", [*matrix[:-1], dict(matrix[0])]),
            ("reordered-cases", [matrix[1], matrix[0], *matrix[2:]]),
            ("old-domain", [{**matrix[0], "seed": "0" * 64}, *matrix[1:]]),
            ("foreign-case-id", [{**matrix[0], "id": "foreign:0000"},
                                 *matrix[1:]]),
            ("foreign-cohort", [{**matrix[0], "cohort": "foreign"},
                                *matrix[1:]]),
            ("changed-input-index", [{**matrix[0], "index": -1},
                                     *matrix[1:]]),
            ("foreign-type", tuple(matrix)),
        ):
            reject("reject-fabricated-full-matrix/" + label,
                   lambda value=poisoned: validate_matrix(value))

        real_official, synthetic_base, synthetic_strict = _synthetic_official_v3()
        check("accept-all-four-independent-146-method-official-proof-streams",
              _validate_official_v3(
                  real_official, base=synthetic_base, strict=synthetic_strict,
              ) is real_official)
        for field, poison in (
            ("schema", "rebar-postfinal-cpython-public-locale-v2"),
            ("status", "FAIL"), ("result", "FAIL"),
            ("python", "3.14.5"),
            ("source_path", V7_BASE_SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("goal_sha256", "0" * 64),
            ("holdout_accessed", True),
            ("timing_performed", True), ("performance", "estimated"),
            ("qualified_source_fingerprints", {}),
            ("native_elf_fingerprints", {}),
        ):
            reject(
                "reject-forged-genuine-official-v3/" + field,
                lambda key=field, value=poison: _validate_official_v3(
                    {**real_official, key: value},
                    base=synthetic_base, strict=synthetic_strict,
                ),
            )
        for field, poison in (
            ("genuine_official_methods_per_engine", 145),
            ("original_upstream_corpus_cases", 402),
            ("independently_run_engine_count", 3),
            ("verified_standard_pickle_count", 47),
            ("verified_real_native_match_repr_count", 5),
            ("named_waiver_count", 7),
            ("genuine_official_v2_rust_failure_preserved", False),
        ):
            reject(
                "reject-weakened-genuine-official-scope/" + field,
                lambda key=field, value=poison: _validate_official_v3(
                    {**real_official,
                     "official_scope": {
                         **real_official["official_scope"], key: value,
                     }},
                    base=synthetic_base, strict=synthetic_strict,
                ),
            )
        for role in ("re", *REQUIRED_CANDIDATES):
            original_role = real_official["roles"][role]
            for label, poison in (
                ("missing-record", original_role["records"][:-1]),
                ("fabricated-status", [
                    {**original_role["records"][0], "status": "skipped"},
                    *original_role["records"][1:],
                ]),
                ("duplicate-method", [
                    original_role["records"][0],
                    original_role["records"][0],
                    *original_role["records"][2:],
                ]),
            ):
                reject(
                    "reject-concealed-official-method/" + role + "/" + label,
                    lambda chosen=role, value=poison: _validate_official_v3(
                        {**real_official, "roles": {
                            **real_official["roles"],
                            chosen: {
                                **real_official["roles"][chosen],
                                "records": value,
                            },
                        }},
                        base=synthetic_base, strict=synthetic_strict,
                    ),
                )

        alias_module, alias_current, alias_reference, alias_all = (
            _synthetic_stage14()
        )
        check("accept-both-complete-128-row-fresh-generic-alias-references",
              _validate_stage14_reference(
                  alias_reference, module=alias_module, current=alias_current,
              ) is alias_reference)
        check("accept-all-384-actual-repaired-generic-alias-native-rows",
              _validate_stage14_all(
                  alias_all, module=alias_module,
                  reference=alias_reference, current=alias_current,
              ) is alias_all)
        check("preserve-both-distinct-genuine-alias-reference-processes",
              alias_reference["baseline_records"]
              is not alias_reference["second_records"]
              and set(alias_reference["reference_worker_reports"])
              == {"stdlib-a", "stdlib-b"})
        for field, poison in (
            ("schema", "rebar-python-re-public-generic-alias-v12-self-oracle"),
            ("status", "FAIL"), ("result", "FAIL"),
            ("python", "3.14.5"),
            ("source_path", STAGE10_SOURCE_RELATIVE),
            ("protocol_path", STAGE10_PROTOCOL_RELATIVE),
            ("seed", STAGE14_SEED - 1),
            ("seed_domain", "rebar/python-re/public-generic-alias/v12"),
            ("matrix_sha256", "0" * 64),
            ("cohorts", 3), ("cohort_cases", {}),
            ("cases", 127), ("stdlib_checks", 255),
            ("mismatches", 1), ("failure_records", [{"id": "concealed"}]),
            ("candidate_imports", 1), ("candidate_processes", 1),
            ("benchmark_or_timing_executed", True),
            ("performance_fixtures_read", 1), ("holdout_cases_read", 1),
            ("performance", "estimated"),
            ("baseline_records", alias_reference["baseline_records"][:-1]),
            ("second_records", alias_reference["second_records"][:-1]),
            ("baseline_record_sha256", "0" * 64),
            ("second_record_sha256", "0" * 64),
            ("independent_stdlib_roles", ["stdlib-a"]),
            ("current_provenance", {"foreign": True}),
            ("reference_worker_reports", {}),
        ):
            reject(
                "reject-incomplete-repaired-generic-alias-reference/" + field,
                lambda key=field, value=poison: _validate_stage14_reference(
                    {**alias_reference, key: value},
                    module=alias_module, current=alias_current,
                ),
            )
        for role in ("stdlib-a", "stdlib-b"):
            actual_worker = alias_reference["reference_worker_reports"][role]
            for field, poison in (
                ("role", "foreign"),
                ("records", actual_worker["records"][:-1]),
                ("record_sha256", "0" * 64),
                ("guard", {"baseline_only": False}),
                ("native_binary_sha256", {"foreign": "0" * 64}),
                ("inspect_loaded", True),
                ("tokenize_loaded", True),
            ):
                reject(
                    "reject-concealed-generic-alias-python-worker/"
                    + role + "/" + field,
                    lambda chosen=role, key=field, value=poison: (
                        _validate_stage14_reference(
                            {**alias_reference, "reference_worker_reports": {
                                **alias_reference["reference_worker_reports"],
                                chosen: {
                                    **alias_reference[
                                        "reference_worker_reports"
                                    ][chosen],
                                    key: value,
                                },
                            }},
                            module=alias_module, current=alias_current,
                        )
                    ),
                )
        for field, poison in (
            ("schema", "rebar-python-re-public-generic-alias-v12-all-candidates"),
            ("cases_per_candidate", 127), ("candidate_checks", 383),
            ("selected_candidates", ["rust", "vm"]),
            ("completed_candidates", ["rust", "vm"]),
            ("comparison_complete", False),
            ("baseline_records", alias_all["baseline_records"][:-1]),
            ("second_reference_records",
             alias_all["second_reference_records"][:-1]),
            ("second_records", alias_all["second_records"][:-1]),
            ("baseline_record_sha256", "0" * 64),
            ("second_record_sha256", "0" * 64),
            ("candidate_reports", {}),
            ("current_provenance", {"foreign": True}),
            ("candidate_cross_delegation", True),
            ("benchmark_or_timing_executed", True),
            ("holdout_cases_read", 1),
        ):
            reject(
                "reject-incomplete-three-family-generic-alias-proof/" + field,
                lambda key=field, value=poison: _validate_stage14_all(
                    {**alias_all, key: value}, module=alias_module,
                    reference=alias_reference, current=alias_current,
                ),
            )
        for role in REQUIRED_CANDIDATES:
            actual_candidate = alias_all["candidate_reports"][role]
            for field, poison in (
                ("candidate", "foreign"),
                ("module", "candidates.foreign_candidate"),
                ("records", actual_candidate["records"][:-1]),
                ("record_sha256", "0" * 64),
                ("mismatches", 1),
                ("native_binary_sha256", {}),
                ("guard", {}), ("public_origins", {}),
                ("benchmark_or_timing_executed", True),
            ):
                reject(
                    "reject-concealed-generic-alias-native-row/"
                    + role + "/" + field,
                    lambda chosen=role, key=field, value=poison: (
                        _validate_stage14_all(
                            {**alias_all, "candidate_reports": {
                                **alias_all["candidate_reports"],
                                chosen: {
                                    **alias_all["candidate_reports"][chosen],
                                    key: value,
                                },
                            }},
                            module=alias_module,
                            reference=alias_reference, current=alias_current,
                        )
                    ),
                )

        provenance, reference, complete = _synthetic_full()
        check("validate-both-full-reference-streams-without-global-patching",
              _validate_complete_reference(reference, provenance) is reference)
        check("validate-all-three-full-families-without-global-patching",
              _validate_complete_all(
                  complete, reference=reference, provenance=provenance,
              ) is complete)
        check("retain-two-independent-full-python-worker-evidence-streams",
              set(reference["reference_worker_reports"])
              == {"stdlib-a", "stdlib-b"}
              and reference["baseline_records"]
              is not reference["second_records"])
        for field, poison in (
            ("schema", "rebar-python-re-public-contract-v10-self-oracle"),
            ("status", "FAIL"), ("result", "FAIL"),
            ("python", "3.14.5"),
            ("source_path", STAGE10_SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("protocol_path", STAGE10_PROTOCOL_RELATIVE),
            ("protocol_sha256", "0" * 64),
            ("seed", SEED - 1), ("seed_domain", "foreign"),
            ("matrix_sha256", "0" * 64),
            ("cohorts", 7), ("cohort_cases", {}),
            ("cases", EXPECTED_CASES - 1),
            ("stdlib_checks", EXPECTED_CASES * 2 - 1),
            ("independent_stdlib_roles", ["stdlib-a"]),
            ("baseline_records", reference["baseline_records"][:-1]),
            ("second_records", reference["second_records"][:-1]),
            ("baseline_record_sha256", "0" * 64),
            ("second_record_sha256", "0" * 64),
            ("reference_worker_reports", {}),
            ("mismatches", 1),
            ("failure_records", [{"id": "concealed"}]),
            ("current_provenance", {"foreign": True}),
            ("candidate_imports", 1), ("candidate_processes", 1),
            ("benchmark_or_timing_executed", True),
            ("performance_fixtures_read", 1),
            ("holdout_cases_read", 1), ("performance", "estimated"),
        ):
            reject(
                "reject-concealed-complete-standard-python-stream/" + field,
                lambda key=field, value=poison: _validate_complete_reference(
                    {**reference, key: value}, provenance,
                ),
            )
        for role in ("stdlib-a", "stdlib-b"):
            actual_worker = reference["reference_worker_reports"][role]
            for field, poison in (
                ("schema", "foreign-worker"), ("role", "foreign"),
                ("source_sha256", "0" * 64),
                ("records", actual_worker["records"][:-1]),
                ("record_sha256", "0" * 64),
                ("guard", {"baseline_only": False}),
                ("native_binary_sha256", {"foreign": "0" * 64}),
                ("benchmark_or_timing_executed", True),
            ):
                reject(
                    "reject-concealed-full-python-worker/" + role + "/" + field,
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
            ("schema", "rebar-python-re-public-contract-v10-all-candidates"),
            ("status", "FAIL"),
            ("selected", "rust"),
            ("selected_candidates", ["rust", "vm"]),
            ("completed_candidates", ["rust", "vm"]),
            ("comparison_complete", False),
            ("source_sha256", "0" * 64),
            ("protocol_sha256", "0" * 64),
            ("seed", SEED - 1),
            ("matrix_sha256", ORIGINAL_MATRIX_SHA256),
            ("cohorts", 7), ("cohort_cases", {}),
            ("cases_per_candidate", EXPECTED_CASES - 1),
            ("candidate_checks", EXPECTED_CASES * 3 - 1),
            ("baseline_records", complete["baseline_records"][:-1]),
            ("second_reference_records",
             complete["second_reference_records"][:-1]),
            ("baseline_record_sha256", "0" * 64),
            ("second_record_sha256", "0" * 64),
            ("self_oracle_path", STAGE10_SELF_RELATIVE),
            ("self_oracle_sha256", "0" * 64),
            ("current_provenance", {"foreign": True}),
            ("candidate_reports", {}),
            ("candidate_cross_delegation", True),
            ("external_regex_packages", 1),
            ("benchmark_or_timing_executed", True),
            ("performance_fixtures_read", 1),
            ("holdout_cases_read", 1),
        ):
            reject(
                "reject-concealed-full-independent-native-comparison/" + field,
                lambda key=field, value=poison: _validate_complete_all(
                    {**complete, key: value},
                    reference=reference, provenance=provenance,
                ),
            )
        for role in REQUIRED_CANDIDATES:
            actual_candidate = complete["candidate_reports"][role]
            for field, poison in (
                ("candidate", "foreign"),
                ("module", "candidates.foreign_candidate"),
                ("status", "FAIL"),
                ("cases", EXPECTED_CASES - 1),
                ("cohort_cases", {}),
                ("records", actual_candidate["records"][:-1]),
                ("record_sha256", "0" * 64),
                ("mismatches", 1),
                ("failure_records", [{"id": "concealed"}]),
                ("native_binary_sha256", {}),
                ("guard", {}),
                ("benchmark_or_timing_executed", True),
                ("performance_fixtures_read", 1),
                ("holdout_cases_read", 1),
            ):
                reject(
                    "reject-concealed-3584-native-records/"
                    + role + "/" + field,
                    lambda chosen=role, key=field, value=poison: (
                        _validate_complete_all(
                            {**complete, "candidate_reports": {
                                **complete["candidate_reports"],
                                chosen: {
                                    **complete["candidate_reports"][chosen],
                                    key: value,
                                },
                            }},
                            reference=reference, provenance=provenance,
                        )
                    ),
                )
            metadata = actual_candidate["guard"]["isolated_public_metadata"]
            for field, poison in (
                ("enabled", False), ("schema", "foreign-metadata"),
                ("role", "foreign"),
                ("source_sha256", "0" * 64),
                ("surface_cases", 255),
                ("record_sha256", "not-a-sha256"),
                ("production_matching_executed", True),
                ("metadata_and_matcher_processes_distinct", False),
                ("matcher_inspect_loaded", True),
                ("matcher_tokenizer_loaded", True),
            ):
                reject(
                    "reject-reused-or-untrusted-signature-process/"
                    + role + "/" + field,
                    lambda chosen=role, key=field, value=poison: (
                        _validate_complete_all(
                            {**complete, "candidate_reports": {
                                **complete["candidate_reports"],
                                chosen: {
                                    **complete["candidate_reports"][chosen],
                                    "guard": {
                                        **complete[
                                            "candidate_reports"
                                        ][chosen]["guard"],
                                        "isolated_public_metadata": {
                                            **complete[
                                                "candidate_reports"
                                            ][chosen]["guard"][
                                                "isolated_public_metadata"
                                            ],
                                            key: value,
                                        },
                                    },
                                },
                            }},
                            reference=reference, provenance=provenance,
                        )
                    ),
                )

        pins = (
            "STAGE14_SOURCE_SHA256", "STAGE14_PROTOCOL_SHA256",
            "STAGE14_SELF_SHA256", "STAGE14_ALL_SHA256",
        )
        actual_pins = {name: globals()[name] for name in pins}

        def synthetic_pins(values: dict[str, Any]) -> None:
            old = {name: globals()[name] for name in pins}
            try:
                for name in pins:
                    globals()[name] = values[name]
                _require_published_stage14()
            finally:
                for name, value in old.items():
                    globals()[name] = value

        valid_pins = {
            name: format(index, "064x")
            for index, name in enumerate(pins, start=1)
        }
        check("accept-four-distinct-genuinely-published-stage14-fingerprints",
              synthetic_pins(valid_pins) is None)
        for name in pins:
            for label, value in (
                ("missing", None),
                ("malformed", "not-a-sha256"),
                ("truncated", "0" * 63),
                ("wrong-type", False),
            ):
                reject(
                    "fail-before-any-real-worker-on-unpublished-stage14/"
                    + name.lower() + "/" + label,
                    lambda key=name, poison=value: synthetic_pins({
                        **valid_pins, key: poison,
                    }),
                )
        reject(
            "reject-a-stage14-source-reused-as-reference-evidence",
            lambda: synthetic_pins({
                **valid_pins,
                "STAGE14_SELF_SHA256": valid_pins["STAGE14_SOURCE_SHA256"],
            }),
        )
        if all(
            isinstance(value, str) and official_locale.is_sha256(value)
            for value in actual_pins.values()
        ):
            check("require-four-actually-published-current-stage14-proofs",
                  _require_published_stage14() is None)
        else:
            reject("fail-closed-before-files-workers-or-unpublished-stage14",
                   _require_published_stage14)

        check("approve-only-six-distinct-exclusive-stage15-destinations",
              len(APPROVED_OUTPUTS) == len(set(APPROVED_OUTPUTS)) == 6)
        check("never-reuse-historical-universal-or-generic-alias-outputs",
              not set(APPROVED_OUTPUTS).intersection({
                  STAGE10_SELF_RELATIVE, STAGE10_ALL_RELATIVE,
                  STAGE14_SELF_RELATIVE, STAGE14_ALL_RELATIVE,
              }))
        for output in APPROVED_OUTPUTS:
            label = Path(output).name
            check("accept-only-one-use-evidence-path/" + label,
                  stage07.exact_output(output, output) == output)
            for kind, poisoned in (
                ("absolute", "/" + output),
                ("traversal", "../" + output),
                ("double-separator", output.replace("/", "//", 1)),
                ("nul", output + "\x00"),
                ("different-approved-file",
                 next(value for value in APPROVED_OUTPUTS if value != output)),
            ):
                reject(
                    "reject-foreign-one-use-evidence/" + label + "/" + kind,
                    lambda value=poisoned, expected=output: (
                        stage07.exact_output(value, expected)
                    ),
                )

        original_source = stage07.SOURCE_RELATIVE
        original_seed = stage07.SEED
        original_matrix = stage07.MATRIX_SHA256
        original_run_worker = stage07._run_worker
        with _stage15_context():
            check("bind-the-exact-full-public-controller-and-matrix",
                  stage07.SOURCE_RELATIVE == SOURCE_RELATIVE
                  and stage07.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE
                  and stage07.SEED == SEED
                  and stage07.SEED_DOMAIN == SEED_DOMAIN
                  and stage07.MATRIX_SHA256 == MATRIX_SHA256
                  and stage07.build_matrix is build_matrix)
            check("bind-the-true-independent-metadata-and-matcher-processes",
                  stage07._run_worker is stage10._run_worker
                  and stage07._worker_report is stage10._worker_report
                  and stage07._worker_environment
                  is stage10._worker_environment
                  and stage07._surface_obligation
                  is stage10._surface_obligation)
            check("retain-context-free-full-python-validator-in-worker-context",
                  _validate_complete_reference(reference, provenance)
                  is reference)
            check("retain-context-free-three-family-validator-in-worker-context",
                  _validate_complete_all(
                      complete, reference=reference, provenance=provenance,
                  ) is complete)
        check("restore-immutable-original-universal-controller-and-workers",
              stage07.SOURCE_RELATIVE == original_source
              and stage07.SEED == original_seed
              and stage07.MATRIX_SHA256 == original_matrix
              and stage07._run_worker is original_run_worker)
        check("never-start-a-baseline-metadata-or-candidate-process",
              effects["workers"] == 0)
        check("never-read-write-time-or-access-randomness",
              all(value == 0 for value in effects.values()))
        frozen.candidate_free()
        check("never-import-a-real-native-candidate-or-regex-package", True)
        names = [item["name"] for item in checks]
        frozen.require(
            len(names) == len(set(names)) and len(checks) >= 1_500,
            "a full repaired universal control was duplicated or omitted",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "stage": "stage15", "status": "PASS", "result": "PASS",
            "seed": SEED, "seed_domain": SEED_DOMAIN,
            "observation_domain": OBSERVATION_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cohorts": len(stage07.COHORTS),
            "cohort_cases": {
                name: count for name, _operation, count in stage07.COHORTS
            },
            "cases": EXPECTED_CASES,
            "checks": checks, "check_count": len(checks), "failed": [],
            "inherited_stage10_control_count": universal["check_count"],
            "inherited_v7_control_count": owned["check_count"],
            "inherited_official_v3_control_count": official["check_count"],
            "candidate_imports": 0, "candidate_processes": 0,
            "metadata_processes": 0,
            "files_read": 0, "files_written": 0,
            "clock_samples": 0, "entropy_drawn": False,
            "self_oracle_executed": False,
            "production_evidence_written": False,
            "stage14_source_pinned": STAGE14_SOURCE_SHA256 is not None,
            "stage14_protocol_pinned": STAGE14_PROTOCOL_SHA256 is not None,
            "stage14_reference_pinned": STAGE14_SELF_SHA256 is not None,
            "stage14_all_candidates_pinned": STAGE14_ALL_SHA256 is not None,
            "stage14_complete_reference_records_required": 256,
            "stage14_complete_candidate_records_required": 384,
            "complete_reference_records_required": EXPECTED_CASES * 2,
            "complete_candidate_records_required": (
                EXPECTED_CASES * len(REQUIRED_CANDIDATES)
            ),
            "isolated_surface_cases_per_candidate": 256,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
            "self_oracle_output": SELF_ORACLE_RELATIVE,
            "self_oracle_failure_output": SELF_ORACLE_FAILURE_RELATIVE,
            "all_candidate_output": ALL_CANDIDATE_RELATIVE,
            "candidate_failure_outputs": dict(CANDIDATE_FAILURE_RELATIVES),
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0, "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--candidate", choices=("all",))
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            report = self_test()
        elif args.self_oracle:
            report = run_self_oracle()
        else:
            frozen.require(
                args.candidate == "all",
                "all three independently owned native families are mandatory",
            )
            report = run_all_candidates()
        sys.stdout.buffer.write(canonical(report) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (
        frozen.OracleIntegrityError, AssertionError, AttributeError,
        ImportError, KeyError, OSError, TypeError, UnicodeError, ValueError,
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
