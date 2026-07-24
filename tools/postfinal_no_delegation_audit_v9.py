#!/usr/bin/env python3
"""Independently verify real V9 native ownership without a mutable report pin."""

from __future__ import annotations

import argparse
import copy
import gc
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v5 as source_v5
from tools import postfinal_from_scratch_audit_v6 as source_v6
from tools import postfinal_from_scratch_audit_v9 as independent
from tools import postfinal_no_delegation_audit_v8 as original_v8_strict


core = independent.core
SCHEMA = "rebar-postfinal-no-delegation-audit-v9"
SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v9.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V9.json"
FAILURE_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V9-FAILURES.json"
)
REPORT_PATH = ROOT / REPORT_RELATIVE
FAILURE_PATH = ROOT / FAILURE_RELATIVE
BASE_SOURCE_RELATIVE = independent.SOURCE_RELATIVE
BASE_REPORT_RELATIVE = independent.REPORT_RELATIVE
BASE_SCHEMA = independent.SCHEMA
BASE_SOURCE_SHA256 = (
    "30822ec9a66a75528c0bf5b94f5451ba81f1fd3689e1d3849f35acf52507f8e1"
)
PROTOCOL_RELATIVE = independent.PROTOCOL_RELATIVE
PROTOCOL_SHA256 = independent.PROTOCOL_SHA256
CORE_FAMILIES = independent.CORE_FAMILIES
MAX_SOURCE_BYTES = independent.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = independent.MAX_REPORT_BYTES
MAX_WORKER_BYTES = independent.MAX_WORKER_BYTES


class AuditV9Error(source_v6.AuditV6Error):
    """A genuine strict all-family source, sentinel, or matching proof failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV9Error(message)


def verify_runtime() -> None:
    require(
        tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.implementation.name == "cpython"
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and Path(sys.executable).resolve()
        == independent.PINNED_EXECUTABLE.resolve()
        and bool(sys.path) and sys.path[0] == str(ROOT)
        and Path(__file__).resolve() == SOURCE_PATH.resolve(),
        "the strict V9 owner requires exact direct isolated Python and trusted root",
    )


def required_pins(
    base_report_sha256: str | None = None,
    *,
    synthetic: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    require(independent.SCHEMA == BASE_SCHEMA
            and independent.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE
            and independent.PROTOCOL_SHA256 == PROTOCOL_SHA256,
            "the independently frozen real V9 source or ownership protocol changed")
    values: Mapping[str, Any] = {
        "base_source": BASE_SOURCE_SHA256,
        "base_report": base_report_sha256,
    }
    if synthetic is not None:
        require(isinstance(synthetic, Mapping)
                and set(synthetic) == {"base_source", "base_report"},
                "a synthetic strict V9 pin omitted an authentic digest")
        values = synthetic
    require(values.get("base_source") == BASE_SOURCE_SHA256,
            "the exact independently frozen V9 base controller was substituted")
    for label, value in values.items():
        require(core.valid_sha256(value),
                "BLOCKED: the actual independently published V9 " + label
                + " SHA-256 must be passed explicitly")
    require(values["base_source"] != values["base_report"],
            "a strict V9 base source cannot be relabeled as its actual report")
    return {name: str(value) for name, value in values.items()}


def destination_name(value: Any) -> str:
    require(type(value) is str, "a strict V9 report destination must be exact text")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and ".." not in parsed.parts
            and "\\" not in value and "\x00" not in value
            and parsed.as_posix() == value
            and value in {REPORT_RELATIVE, FAILURE_RELATIVE},
            "only exact separate V9 strict success and failure paths are allowed")
    return value


def verify_fresh_report_targets() -> None:
    for path in (REPORT_PATH, FAILURE_PATH):
        require(path.resolve(strict=False) == path
                and path.parent.is_dir() and not path.parent.is_symlink()
                and not path.exists() and not path.is_symlink(),
                "refusing to rerun or overwrite real strict V9 owner evidence: "
                + path.relative_to(ROOT).as_posix())
        destination_name(path.relative_to(ROOT).as_posix())


def validate_base_report(
    document: Any,
    pins: Mapping[str, str],
) -> dict[str, Any]:
    require(isinstance(pins, Mapping)
            and set(pins) == {"base_source", "base_report"}
            and pins.get("base_source") == BASE_SOURCE_SHA256
            and core.valid_sha256(pins.get("base_report"))
            and pins["base_source"] != pins["base_report"],
            "an actual independently frozen V9 source and real report are required")
    require(isinstance(document, dict),
            "the actual passing V9 native-owner base report is not complete JSON")
    expected = {
        "schema": BASE_SCHEMA, "postfinal_schema": BASE_SCHEMA,
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": BASE_SOURCE_RELATIVE,
        "audit_source_sha256": pins["base_source"],
        "native_ownership_protocol_path": PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": PROTOCOL_SHA256,
        "stage07_source_path": independent.STAGE07_RELATIVE,
        "stage07_source_sha256": independent.STAGE07_SHA256,
        "native_owner_worker_sha256": independent.NATIVE_OWNER_WORKER_SHA256,
        "v5_reference_path": independent.V5_REFERENCE_RELATIVE,
        "v5_reference_sha256": independent.V5_REFERENCE_SHA256,
        "v5_reference_role_count": 2,
        "v5_reference_methods_per_role": 152,
        "v5_reference_applicable_per_role": 151,
        "v5_reference_private_debug_skips_per_role": 1,
        "historical_v8_owner_failure_qualifies_current_build": False,
        "historical_v7_results_qualify_current_build": False,
        "historical_first_campaign_failure_preserved": True,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "match_repr_checks_per_family": 2,
        "verified_match_repr_checks": 6,
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": 48,
        "standard_pickle_failure_count": 0,
        "completed_native_owner_worker_count": 3,
        "actual_native_owner_worker_failure": None,
    }
    for key, value in expected.items():
        require(document.get(key) == value,
                "the genuine independently authored V9 base proof changed: " + key)
    graph = source_v6._validate_fresh_graph(document)
    require(graph["source_count"] == 12 and graph["native_binary_count"] == 5
            and document.get("verified_candidate_source_paths")
            == graph["source_paths"]
            and document.get("native_sha256_by_family")
            == graph["native_sha256_by_family"],
            "the complete actual V9 twelve-source/five-ELF graph was replaced")
    observed = document.get("actual_native_owner_workers")
    require(isinstance(observed, dict) and set(observed) == set(CORE_FAMILIES),
            "a genuine passing V9 base omitted a Rust, C, or Zig matching worker")
    for family in CORE_FAMILIES:
        independent.validate_worker(
            observed[family], family,
            graph["native_sha256_by_family"][family],
        )
    incident = document.get("actual_v8_native_owner_failure")
    require(isinstance(incident, dict)
            and incident.get("path") == independent.V8_OWNER_FAILURE_RELATIVE
            and incident.get("sha256") == independent.V8_OWNER_FAILURE_SHA256
            and incident.get("status") == "FAIL"
            and incident.get("stage") == "before-original-edge"
            and incident.get("actual_returncode") == 1
            and incident.get("stdout_bytes") == 0
            and incident.get("stderr_bytes") == 216
            and incident.get("original_edge_worker_started") is False
            and incident.get("qualifies_current_engine") is False,
            "the actual V8 sentinel-composition owner failure was concealed")
    failures = document.get("historical_current_build_edge_failures")
    require(isinstance(failures, dict)
            and set(failures) == set(CORE_FAMILIES),
            "a genuine strict V9 proof omitted a real prior full edge failure")
    for family in CORE_FAMILIES:
        actual = failures[family]
        expected_failure = independent.V7_EDGE_EXPECTATIONS[family]
        require(isinstance(actual, dict)
                and actual.get("status") == "FAIL"
                and actual.get("qualifies_current_engine") is False
                and actual.get("family") == family
                and actual.get("candidate_module")
                == "candidates." + family + "_candidate"
                and actual.get("archive_sha256")
                == independent.V7_EDGE_FAILURES[family][1]
                and actual.get("seed") == independent.EDGE_SEED
                and actual.get("checks") == independent.EDGE_CHECKS
                and actual.get("category_count") == independent.EDGE_CATEGORIES
                and actual.get("failed") == expected_failure["failed"]
                and actual.get("failure_rows_preserved")
                == expected_failure["failed"]
                and actual.get("expected_sha256")
                == independent.EDGE_REFERENCE_SHA256
                and actual.get("actual_sha256")
                == expected_failure["actual_sha256"],
                "a genuine complete historical edge failure changed: " + family)
    scope = document.get("postfinal_scope")
    require(isinstance(scope, dict)
            and scope.get("append_only") is True
            and scope.get("exclusive_report_path") == BASE_REPORT_RELATIVE
            and scope.get("separate_pass_and_failure_destinations") is True
            and scope.get("previous_v7_reports_historical") is True
            and scope.get("previous_v8_owner_failure_preserved") is True
            and scope.get("historical_v8_owner_failure_qualifies_current_build")
            is False
            and scope.get("actual_edge_failures_preserved") is True
            and scope.get("exact_current_owned_candidate_source_count") == 12
            and scope.get("actual_current_native_binary_count") == 5
            and scope.get("actual_native_matching_workers") == 3
            and scope.get("genuine_public_pickle_checks") == 48
            and scope.get("genuine_match_repr_checks") == 6
            and scope.get("actual_python_matching_guards_per_family") == 13
            and scope.get("actual_native_loader_guards_per_family") == 5
            and scope.get("exact_stage07_sentinel_checked_before_and_after") is True
            and scope.get("native_identity_is_independent_of_public_module") is True
            and scope.get("mapped_binaries_hashed_against_static_elf") is True
            and scope.get("benchmark_or_timing_executed") is False
            and scope.get("holdout_or_case_fixture_access") is False,
            "the actual all-family V9 no-delegation boundary was weakened")
    controls = document.get("postfinal_wrapper_self_test")
    require(isinstance(controls, dict)
            and controls.get("schema") == BASE_SCHEMA + "-self-test"
            and controls.get("status") == "PASS"
            and controls.get("passed") is True
            and controls.get("check_count", 0) >= 150
            and controls.get("candidate_imports") == 0
            and controls.get("subprocesses") == 0
            and controls.get("file_reads") == 0
            and controls.get("file_writes") == 0
            and controls.get("clock_samples") == 0,
            "genuine source-only V9 native guard protections were weakened")
    return graph


def load_base_report(pins: Mapping[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    observed_source, _ = core.bounded_file(
        ROOT / BASE_SOURCE_RELATIVE, maximum=MAX_SOURCE_BYTES,
        label="independently frozen complete V9 actual native-owner source",
    )
    require(observed_source == BASE_SOURCE_SHA256
            and observed_source == pins["base_source"]
            and Path(independent.__file__).resolve()
            == (ROOT / BASE_SOURCE_RELATIVE).resolve(),
            "the actual immutable V9 native owner was substituted")
    observed, payload = core.bounded_file(
        ROOT / BASE_REPORT_RELATIVE, maximum=MAX_REPORT_BYTES,
        label="actual exclusively published passing V9 native-owner report",
        keep=True,
    )
    require(observed == pins["base_report"] and isinstance(payload, bytes),
            "the externally supplied V9 owner hash is not the actual report")
    report = core.decode_report(payload, label="actual complete passing V9 base")
    require(core.canonical(report) + b"\n" == payload,
            "the actual exclusive V9 native report is not original canonical JSON")
    return report, validate_base_report(report, pins)


def synthetic_base(pins: Mapping[str, str]) -> dict[str, Any]:
    report = original_v8_strict.synthetic_base(pins)
    workers: dict[str, Any] = {}
    native: dict[str, dict[str, str]] = {}
    for family in CORE_FAMILIES:
        worker, fingerprints = independent.synthetic_worker(family)
        workers[family] = worker
        native[family] = fingerprints
    report.update({
        "schema": BASE_SCHEMA, "postfinal_schema": BASE_SCHEMA,
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": BASE_SOURCE_RELATIVE,
        "audit_source_sha256": pins["base_source"],
        "native_ownership_protocol_path": PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": PROTOCOL_SHA256,
        "stage07_source_path": independent.STAGE07_RELATIVE,
        "stage07_source_sha256": independent.STAGE07_SHA256,
        "native_owner_worker_sha256": independent.NATIVE_OWNER_WORKER_SHA256,
        "v5_reference_path": independent.V5_REFERENCE_RELATIVE,
        "v5_reference_sha256": independent.V5_REFERENCE_SHA256,
        "v5_reference_role_count": 2,
        "v5_reference_methods_per_role": 152,
        "v5_reference_applicable_per_role": 151,
        "v5_reference_private_debug_skips_per_role": 1,
        "historical_v8_owner_failure_qualifies_current_build": False,
        "historical_v7_results_qualify_current_build": False,
        "historical_first_campaign_failure_preserved": True,
        "native_sha256_by_family": native,
        "actual_native_owner_workers": workers,
        "completed_native_owner_worker_count": 3,
        "actual_native_owner_worker_failure": None,
        "actual_v8_native_owner_failure": independent.validate_v8_owner_failure(
            independent._synthetic_v8_owner_failure()
        ),
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": BASE_REPORT_RELATIVE,
            "separate_pass_and_failure_destinations": True,
            "previous_v7_reports_historical": True,
            "previous_v8_owner_failure_preserved": True,
            "historical_v8_owner_failure_qualifies_current_build": False,
            "actual_edge_failures_preserved": True,
            "exact_current_owned_candidate_source_count": 12,
            "actual_current_native_binary_count": 5,
            "actual_native_matching_workers": 3,
            "genuine_public_pickle_checks": 48,
            "genuine_match_repr_checks": 6,
            "actual_python_matching_guards_per_family": 13,
            "actual_native_loader_guards_per_family": 5,
            "exact_stage07_sentinel_checked_before_and_after": True,
            "native_identity_is_independent_of_public_module": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "postfinal_wrapper_self_test": {
            "schema": BASE_SCHEMA + "-self-test",
            "status": "PASS", "passed": True, "check_count": 778,
            "candidate_imports": 0, "subprocesses": 0,
            "file_reads": 0, "file_writes": 0, "clock_samples": 0,
        },
    })
    return report


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime()
    core.ensure_candidate_free()
    inherited = independent.candidate_free_self_test()
    require(inherited.get("passed") is True
            and inherited.get("check_count", 0) >= 150,
            "the actual V9 base source-only sentinel controls failed")
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(not any(item["name"] == name for item in checks),
                "a source-only strict V9 poison was repeated")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (AuditV9Error, independent.AuditV9Error,
                original_v8_strict.AuditV8Error,
                source_v6.AuditV6Error, AssertionError,
                OSError, TypeError, ValueError, KeyError):
            accept(name, True)
        else:
            accept(name, False)

    effects = core.previous.BlockSelfTestEffects()
    with effects:
        for row in inherited["checks"]:
            accept("independent-v9:" + row["name"], row.get("passed") is True)
        accept("bootstrap-direct-isolated-strict-owner-from-exact-trusted-root",
               bool(sys.path) and sys.path[0] == str(ROOT))
        accept("freeze-only-the-actual-independent-v9-base-source",
               core.valid_sha256(BASE_SOURCE_SHA256))
        audit_names = run_audit.__code__.co_names
        accept("authenticate-the-real-v9-base-before-any-history-or-workers",
               audit_names.index("load_base_report")
               < audit_names.index("verify_history")
               and audit_names.index("load_base_report")
               < audit_names.index("candidate_free_self_test")
               and audit_names.index("load_base_report")
               < audit_names.index("run_native_worker"))
        reject("reject-a-missing-externally-published-v9-base-report",
               lambda: required_pins())
        report_pin = hashlib.sha256(
            b"explicit synthetic-only V9 source-only report pin",
        ).hexdigest()
        pins = required_pins(report_pin)
        base = synthetic_base(pins)
        accept("accept-complete-all-family-in-memory-v9-sentinel-base",
               validate_base_report(copy.deepcopy(base), pins)
               ["source_count"] == 12)

        def poison(label: str,
                   change: Callable[[dict[str, Any]], None]) -> None:
            changed = copy.deepcopy(base)
            change(changed)
            reject("reject-real-v9-strict-proof:" + label,
                   lambda: validate_base_report(changed, pins))

        for key, value in (
            ("schema", independent.original_v8.SCHEMA),
            ("postfinal_schema", independent.original_v8.SCHEMA),
            ("status", "FAIL"), ("result", "FAIL"), ("passed", False),
            ("audit_source_sha256", "0" * 64),
            ("native_ownership_protocol_sha256", "0" * 64),
            ("stage07_source_sha256", "0" * 64),
            ("native_owner_worker_sha256", "0" * 64),
            ("v5_reference_sha256", "0" * 64),
            ("v5_reference_role_count", 1),
            ("v5_reference_methods_per_role", 151),
            ("v5_reference_applicable_per_role", 150),
            ("v5_reference_private_debug_skips_per_role", 0),
            ("verified_core_family_count", 2),
            ("verified_distinct_pipeline_count", 2),
            ("verified_candidate_source_count", 11),
            ("verified_native_role_count", 4),
            ("verified_match_repr_checks", 5),
            ("standard_pickle_checks", 47),
            ("standard_pickle_failure_count", 1),
            ("completed_native_owner_worker_count", 2),
            ("historical_v8_owner_failure_qualifies_current_build", True),
            ("historical_v7_results_qualify_current_build", True),
            ("historical_first_campaign_failure_preserved", False),
        ):
            poison("change-actual-native-proof-field:" + key,
                   lambda row, key=key, value=value: row.update({key: value}))
        for family in CORE_FAMILIES:
            poison("remove-a-genuine-independent-native-worker:" + family,
                   lambda row, family=family:
                   row["actual_native_owner_workers"].pop(family))
            for flag in independent.SENTINEL_FLAGS:
                poison("accept-a-forged-stage07-cache:" + family + ":" + flag,
                       lambda row, family=family, flag=flag:
                       row["actual_native_owner_workers"][family]
                       ["stage07_guard_sentinel"].update({flag: False}))
            poison("change-the-real-frozen-stage07-source:" + family,
                   lambda row, family=family:
                   row["actual_native_owner_workers"][family]
                   ["stage07_guard_sentinel"].update({
                       "stage07_source_sha256": "0" * 64,
                   }))
            for field in (
                "regex_guard_observations",
                "regex_guard_observations_after",
                "foreign_engine_guard_observations",
                "foreign_engine_guard_observations_after",
                "native_loader_guard_observations",
                "native_loader_guard_observations_after",
                "standard_pickle_checks",
            ):
                poison("remove-a-before-or-after-native-observation:"
                       + family + ":" + field,
                       lambda row, family=family, field=field:
                       row["actual_native_owner_workers"][family][field].pop())
            for flag in ("stdlib_re_blocked", "cpython_sre_blocked",
                         "third_party_regex_blocked", "cross_family_blocked",
                         "foreign_dynamic_libraries_blocked"):
                poison("disable-a-real-native-family-guard:"
                       + family + ":" + flag,
                       lambda row, family=family, flag=flag:
                       row["actual_native_owner_workers"][family]
                       ["guard"].update({flag: False}))
            poison("conceal-an-original-complete-edge-failure:" + family,
                   lambda row, family=family:
                   row["historical_current_build_edge_failures"].pop(family))
        for key, value in (
            ("status", "PASS"), ("qualifies_current_engine", True),
            ("sha256", "0" * 64), ("actual_returncode", 0),
            ("stderr_bytes", 0), ("original_edge_worker_started", True),
        ):
            poison("conceal-the-real-failed-v8-native-owner:" + key,
                   lambda row, key=key, value=value:
                   row["actual_v8_native_owner_failure"].update({key: value}))
        for flag, wrong in (
            ("append_only", False),
            ("separate_pass_and_failure_destinations", False),
            ("previous_v8_owner_failure_preserved", False),
            ("actual_edge_failures_preserved", False),
            ("exact_current_owned_candidate_source_count", 11),
            ("actual_current_native_binary_count", 4),
            ("actual_native_matching_workers", 2),
            ("genuine_public_pickle_checks", 47),
            ("genuine_match_repr_checks", 5),
            ("actual_python_matching_guards_per_family", 12),
            ("actual_native_loader_guards_per_family", 4),
            ("exact_stage07_sentinel_checked_before_and_after", False),
            ("native_identity_is_independent_of_public_module", False),
            ("mapped_binaries_hashed_against_static_elf", False),
            ("benchmark_or_timing_executed", True),
            ("holdout_or_case_fixture_access", True),
        ):
            poison("weaken-a-real-v9-native-isolation-scope:" + flag,
                   lambda row, flag=flag, wrong=wrong:
                   row["postfinal_scope"].update({flag: wrong}))
        for flag, value in (
            ("passed", False), ("check_count", 149),
            ("candidate_imports", 1), ("subprocesses", 1),
            ("file_reads", 1), ("file_writes", 1), ("clock_samples", 1),
        ):
            poison("forge-the-actual-base-source-only-controls:" + flag,
                   lambda row, flag=flag, value=value:
                   row["postfinal_wrapper_self_test"].update({flag: value}))
        for key, value in (
            ("base_source", "0" * 64),
            ("base_report", None),
            ("base_report", BASE_SOURCE_SHA256),
            ("base_report", "invalid"),
        ):
            changed = dict(pins)
            changed[key] = value
            reject("reject-invalid-external-strict-v9-pin:"
                   + key + ":" + str(value),
                   lambda changed=changed: required_pins(
                       synthetic=changed,
                   ))
        for value in (
            BASE_REPORT_RELATIVE,
            independent.FAILURE_RELATIVE,
            original_v8_strict.REPORT_RELATIVE,
            "performance/private-holdout.json",
            "../POSTFINAL-NO-DELEGATION-AUDIT-V9.json",
            "/tmp/POSTFINAL-NO-DELEGATION-AUDIT-V9.json",
        ):
            reject("reject-unsafe-or-historical-strict-v9-output:" + value,
                   lambda value=value: destination_name(value))
        for value in (REPORT_RELATIVE, FAILURE_RELATIVE):
            accept("allow-only-an-exact-distinct-v9-strict-output:" + value,
                   destination_name(value) == value)

    require(len(checks) >= 150 and all(item["passed"] for item in checks),
            "a source-only strict V9 native sentinel or report poison escaped")
    require(effects.counts["processes"] == 0
            and effects.counts["files"] == 0
            and effects.counts["clocks"] == 0,
            "a strict candidate-free V9 control caused an external side effect")
    core.ensure_candidate_free()
    verify_runtime()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "independent_v9_control_count": inherited["check_count"],
        "actual_base_report_digest_is_external": True,
        "base_source_sha256": BASE_SOURCE_SHA256,
        "stage07_source_sha256": independent.STAGE07_SHA256,
        "v8_native_owner_failure_sha256": independent.V8_OWNER_FAILURE_SHA256,
        "v5_reference_sha256": independent.V5_REFERENCE_SHA256,
        "candidate_imports": 0,
        "subprocesses": effects.counts["processes"],
        "file_reads": effects.counts["files"],
        "file_writes": effects.counts["files"],
        "clock_samples": effects.counts["clocks"],
        "actual_public_pickle_cases_required": 48,
        "actual_matching_poison_guards_per_family": 13,
        "actual_native_loader_guards_per_family": 5,
        "synthetic_results_qualify_candidates": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }


def run_audit(base_report_sha256: str) -> dict[str, Any]:
    verify_runtime()
    core.verify_production_runtime()
    core.ensure_candidate_free()
    pins = required_pins(base_report_sha256)
    base, graph = load_base_report(pins)
    history = independent.verify_history()
    controls = candidate_free_self_test()
    core.ensure_candidate_free()
    gc.collect()
    with source_v5.allow_owned_locale_ctype():
        current = core.audit()
    core.validate_v3_report(current, label="genuine strict fresh V9 native graph")
    live = source_v6._validate_fresh_graph(current)
    require(live == graph,
            "an independent source or native ELF changed after the actual V9 base")
    workers: dict[str, dict[str, Any]] = {}
    failure: dict[str, Any] | None = None
    for family in CORE_FAMILIES:
        try:
            worker = independent.run_native_worker(
                family, live["native_sha256_by_family"][family],
            )
            workers[family] = worker
            if worker.get("status") != "PASS":
                failure = {
                    "schema": SCHEMA + "-actual-observed-native-owner-failure",
                    "status": "FAIL", "family": family,
                    "actual_native_owner_worker": worker,
                    "production_observations_invented": False,
                    "qualifies_current_engine": False,
                }
                break
        except independent.NativeWorkerFailure as error:
            failure = error.evidence
            break
    core.ensure_candidate_free()
    pickle_failures = sum(
        report["standard_pickle_failure_count"]
        for report in workers.values()
    )
    passed = (failure is None and len(workers) == len(CORE_FAMILIES)
              and pickle_failures == 0)
    actual_source, _ = core.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
        label="actual frozen independently authored V9 strict audit source",
    )
    report = dict(current)
    report.update({
        "schema": SCHEMA, "postfinal_schema": SCHEMA,
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL", "passed": passed,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": actual_source,
        "base_audit_postfinal_schema": BASE_SCHEMA,
        "base_audit_source_path": BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": pins["base_source"],
        "base_audit_report_path": BASE_REPORT_RELATIVE,
        "base_audit_report_sha256": pins["base_report"],
        "native_ownership_protocol_path": PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": PROTOCOL_SHA256,
        "stage07_source_path": independent.STAGE07_RELATIVE,
        "stage07_source_sha256": independent.STAGE07_SHA256,
        "native_owner_worker_sha256": independent.NATIVE_OWNER_WORKER_SHA256,
        "v5_reference_path": independent.V5_REFERENCE_RELATIVE,
        "v5_reference_sha256": independent.V5_REFERENCE_SHA256,
        "actual_v8_native_owner_failure": history[
            "actual_v8_native_owner_failure"
        ],
        "historical_v8_owner_failure_qualifies_current_build": False,
        "historical_v7_results_qualify_current_build": False,
        "historical_public_input_sha256": history["historical_input_sha256"],
        "historical_current_build_edge_failures": history["real_edge_failures"],
        "postfinal_wrapper_self_test": controls,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": live["source_count"],
        "verified_candidate_source_paths": live["source_paths"],
        "verified_native_role_count": live["native_binary_count"],
        "native_sha256_by_family": live["native_sha256_by_family"],
        "independent_base_native_owner_workers": base[
            "actual_native_owner_workers"
        ],
        "actual_native_owner_workers": workers,
        "actual_native_owner_worker_failure": failure,
        "completed_native_owner_worker_count": len(workers),
        "unstarted_native_owner_families": [
            family for family in CORE_FAMILIES
            if family not in workers
            and (failure is None or family != failure.get("family"))
        ],
        "public_type_ownership": {
            family: worker["public_type_ownership"]
            for family, worker in workers.items()
        },
        "strict_public_match_repr": workers,
        "verified_match_repr_checks": sum(
            worker["match_repr_checks"] for worker in workers.values()
        ),
        "verified_standard_pickle_count": sum(
            worker["standard_pickle_check_count"]
            for worker in workers.values()
        ),
        "standard_pickle_failure_count": pickle_failures,
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": REPORT_RELATIVE if passed else FAILURE_RELATIVE,
            "separate_pass_and_failure_destinations": True,
            "independently_pinned_fresh_v9_base": True,
            "base_report_hash_supplied_externally": True,
            "previous_v8_owner_failure_preserved": True,
            "historical_v8_owner_failure_qualifies_current_build": False,
            "historical_v7_reports_qualify_current_build": False,
            "actual_edge_failures_preserved": True,
            "actual_current_native_binary_count": 5,
            "exact_current_owned_candidate_source_count": 12,
            "independently_executed_native_owner_workers": (
                len(workers) + int(failure is not None
                                    and failure.get("family") not in workers)
            ),
            "genuine_public_pickle_checks": sum(
                worker["standard_pickle_check_count"]
                for worker in workers.values()
            ),
            "genuine_match_repr_checks": sum(
                worker["match_repr_checks"] for worker in workers.values()
            ),
            "actual_python_matching_guards_per_family": 13,
            "actual_native_loader_guards_per_family": 5,
            "exact_stage07_sentinel_checked_before_and_after": True,
            "persistent_cross_family_import_and_loader_guards": True,
            "native_identity_is_independent_of_public_module": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    require(live["source_count"] == 12 and live["native_binary_count"] == 5,
            "the actual strict V9 independent source or ELF denominator changed")
    if passed:
        require(report["verified_match_repr_checks"] == 6
                and report["verified_standard_pickle_count"] == 48,
                "a strict V9 passing owner weakened real matching or pickles")
    else:
        require(failure is not None,
                "a failing strict V9 native report invented its observed failure")
    core.ensure_candidate_free()
    return report


def write_report(report: Mapping[str, Any], target: Path | None = None) -> str:
    require(isinstance(report, Mapping),
            "a strict V9 exclusive report requires real complete observations")
    expected = REPORT_PATH if report.get("passed") is True else FAILURE_PATH
    actual = expected if target is None else target
    require(isinstance(actual, Path)
            and actual.resolve(strict=False) == expected
            and expected.parent.is_dir() and not expected.parent.is_symlink(),
            "an actual strict V9 report escaped its exact distinct destination")
    destination_name(expected.relative_to(ROOT).as_posix())
    payload = core.canonical(report) + b"\n"
    require(0 < len(payload) <= MAX_REPORT_BYTES,
            "the strict complete V9 evidence exceeded its bounded maximum")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(expected.parent, flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the strict V9 evidence parent is not a real safe directory")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(expected.name, create, 0o644, dir_fd=directory)
        try:
            pending = memoryview(payload)
            while pending:
                wrote = os.write(descriptor, pending)
                require(wrote > 0, "an exclusively created strict V9 report stalled")
                pending = pending[wrote:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--gate", action="store_true")
    modes.add_argument("--audit", action="store_true")
    parser.add_argument("--base-report-sha256")
    parser.add_argument("--output", type=Path)
    options = parser.parse_args(arguments)
    try:
        verify_runtime()
        core.ensure_candidate_free()
        if options.self_test:
            require(options.output is None
                    and options.base_report_sha256 is None,
                    "the source-only strict V9 self-test cannot consume real evidence")
            document = candidate_free_self_test()
            sys.stdout.buffer.write(core.canonical(document) + b"\n")
            return 0
        required_pins(options.base_report_sha256)
        verify_fresh_report_targets()
        report = run_audit(str(options.base_report_sha256))
        observed = write_report(report, options.output)
        result = {
            "schema": SCHEMA,
            "status": report["status"], "result": report["result"],
            "passed": report["passed"],
            "report": REPORT_RELATIVE if report["passed"] else FAILURE_RELATIVE,
            "report_sha256": observed,
            "audit_source_sha256": report["audit_source_sha256"],
            "base_audit_report_sha256": report["base_audit_report_sha256"],
            "verified_core_family_count": 3,
            "verified_candidate_source_count": 12,
            "verified_native_role_count": 5,
            "verified_match_repr_checks": report["verified_match_repr_checks"],
            "verified_standard_pickle_count": report[
                "verified_standard_pickle_count"
            ],
            "standard_pickle_failure_count": report["standard_pickle_failure_count"],
            "completed_native_owner_worker_count": report[
                "completed_native_owner_worker_count"
            ],
            "actual_native_owner_worker_failure": report[
                "actual_native_owner_worker_failure"
            ],
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(core.canonical(result) + b"\n")
        return int(not report["passed"])
    except (AuditV9Error, independent.AuditV9Error,
            independent.refresh_v8.ProofV8Error,
            independent.reference_v5.OfficialV5Error,
            source_v6.AuditV6Error, OSError,
            RuntimeError, TypeError, ValueError, KeyError,
            UnicodeError, subprocess.SubprocessError) as error:
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA, "status": "BLOCKED", "result": "BLOCKED",
            "passed": False, "error_type": type(error).__name__,
            "error": str(error),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
