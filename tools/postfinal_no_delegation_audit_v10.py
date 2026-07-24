#!/usr/bin/env python3
"""Independently reject cached Python regex engines in real native workers."""

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
from tools import postfinal_from_scratch_audit_v10 as independent
from tools import postfinal_no_delegation_audit_v9 as previous_strict


core = independent.core
SCHEMA = "rebar-postfinal-no-delegation-audit-v10"
SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v10.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10.json"
FAILURE_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10-FAILURES.json"
)
REPORT_PATH = ROOT / REPORT_RELATIVE
FAILURE_PATH = ROOT / FAILURE_RELATIVE
BASE_SOURCE_RELATIVE = independent.SOURCE_RELATIVE
BASE_REPORT_RELATIVE = independent.REPORT_RELATIVE
BASE_SCHEMA = independent.SCHEMA
BASE_SOURCE_SHA256 = (
    "0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505"
)
PROTOCOL_RELATIVE = independent.PROTOCOL_RELATIVE
PROTOCOL_SHA256 = independent.PROTOCOL_SHA256
CORE_FAMILIES = independent.CORE_FAMILIES
MAX_SOURCE_BYTES = independent.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = independent.MAX_REPORT_BYTES


class AuditV10Error(source_v6.AuditV6Error):
    """A real native regex cache, owner, or independently pinned graph failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV10Error(message)


def verify_runtime() -> None:
    require(tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and Path(sys.executable).resolve()
            == independent.PINNED_EXECUTABLE.resolve()
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and Path(__file__).resolve() == SOURCE_PATH.resolve(),
            "the exact directly isolated V10 strict owner and trusted root are required")


def required_pins(
    base_report_sha256: str | None = None,
    *,
    synthetic: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    require(independent.SCHEMA == BASE_SCHEMA
            and independent.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE
            and independent.PROTOCOL_SHA256 == PROTOCOL_SHA256,
            "the actual independently frozen V10 owner or protocol changed")
    values: Mapping[str, Any] = {
        "base_source": BASE_SOURCE_SHA256,
        "base_report": base_report_sha256,
    }
    if synthetic is not None:
        require(isinstance(synthetic, Mapping)
                and set(synthetic) == {"base_source", "base_report"},
                "the source-only V10 base pins were weakened")
        values = synthetic
    require(values.get("base_source") == BASE_SOURCE_SHA256,
            "the exact independently frozen V10 owner source was substituted")
    for name, value in values.items():
        require(core.valid_sha256(value),
                "BLOCKED: the actual V10 " + name
                + " SHA-256 must be explicitly independently published")
    require(values["base_source"] != values["base_report"],
            "a source hash cannot stand in for an actual V10 passing owner report")
    return {name: str(value) for name, value in values.items()}


def destination_name(value: Any) -> str:
    require(type(value) is str,
            "the exact V10 strict evidence destination must be textual")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts
            and "\\" not in value and "\x00" not in value
            and path.as_posix() == value
            and value in {REPORT_RELATIVE, FAILURE_RELATIVE},
            "only separate exclusive V10 strict pass or failure paths are allowed")
    return value


def verify_fresh_report_targets() -> None:
    for path in (REPORT_PATH, FAILURE_PATH):
        require(path.resolve(strict=False) == path
                and path.parent.is_dir() and not path.parent.is_symlink()
                and not path.exists() and not path.is_symlink(),
                "refusing to retry or overwrite actual strict V10 evidence: "
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
            "a strict V10 audit requires the actual independently pinned base")
    require(isinstance(document, dict),
            "the actual all-family V10 ownership base is not complete JSON")
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
        "historical_v9_owner_failure_qualifies_current_build": False,
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
                "the actual cache-safe independently owned V10 base changed: " + key)
    graph = source_v6._validate_fresh_graph(document)
    require(graph["source_count"] == 12 and graph["native_binary_count"] == 5
            and document.get("verified_candidate_source_paths")
            == graph["source_paths"]
            and document.get("native_sha256_by_family")
            == graph["native_sha256_by_family"],
            "the actual complete V10 twelve-source/five-ELF graph was substituted")
    observed = document.get("actual_native_owner_workers")
    require(isinstance(observed, dict) and set(observed) == set(CORE_FAMILIES),
            "a genuine V10 base omitted an actual native family")
    for family in CORE_FAMILIES:
        independent.validate_worker(
            observed[family], family,
            graph["native_sha256_by_family"][family],
        )
    for label, field, expected_path, expected_hash, stderr_bytes in (
        ("V9", "actual_v9_native_owner_failure",
         independent.V9_OWNER_FAILURE_RELATIVE,
         independent.V9_OWNER_FAILURE_SHA256, 203),
        ("V8", "actual_v8_native_owner_failure",
         independent.V8_OWNER_FAILURE_RELATIVE,
         independent.V8_OWNER_FAILURE_SHA256, 216),
    ):
        incident = document.get(field)
        require(isinstance(incident, dict)
                and incident.get("path") == expected_path
                and incident.get("sha256") == expected_hash
                and incident.get("status") == "FAIL"
                and incident.get("stage") == "before-original-edge"
                and incident.get("actual_returncode") == 1
                and incident.get("stdout_bytes") == 0
                and incident.get("stderr_bytes") == stderr_bytes
                and incident.get("original_edge_worker_started") is False
                and incident.get("qualifies_current_engine") is False,
                "the real complete " + label + " owner failure was concealed")
        if label == "V9":
            require(incident.get("stdout_sha256")
                    == independent.EMPTY_STREAM_SHA256
                    and incident.get("stderr_sha256")
                    == independent.V9_OWNER_STDERR_SHA256,
                    "the real 203-byte V9 matcher-cache stderr was substituted")
    failures = document.get("historical_current_build_edge_failures")
    require(isinstance(failures, dict)
            and set(failures) == set(CORE_FAMILIES),
            "a true original historical full edge failure was omitted")
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
                "the actual complete historical edge was changed: " + family)
    scope = document.get("postfinal_scope")
    require(isinstance(scope, dict)
            and scope.get("append_only") is True
            and scope.get("exclusive_report_path") == BASE_REPORT_RELATIVE
            and scope.get("separate_pass_and_failure_destinations") is True
            and scope.get("previous_v9_owner_failure_preserved") is True
            and scope.get("previous_v8_owner_failure_preserved") is True
            and scope.get("historical_v9_owner_failure_qualifies_current_build")
            is False
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
            and scope.get("all_cached_matcher_descendants_poisoned_before_and_after")
            is True
            and scope.get("original_stage07_cached_alias_helper_used") is True
            and scope.get("native_identity_is_independent_of_public_module") is True
            and scope.get("mapped_binaries_hashed_against_static_elf") is True
            and scope.get("benchmark_or_timing_executed") is False
            and scope.get("holdout_or_case_fixture_access") is False,
            "the genuine complete cached-matcher-free V10 boundary was weakened")
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
            "the actual source-only V10 cache poison protections were weakened")
    return graph


def load_base_report(pins: Mapping[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    source_digest, _ = core.bounded_file(
        ROOT / BASE_SOURCE_RELATIVE, maximum=MAX_SOURCE_BYTES,
        label="actual immutable cache-safe V10 independently owned source",
    )
    require(source_digest == BASE_SOURCE_SHA256
            and source_digest == pins["base_source"]
            and Path(independent.__file__).resolve()
            == (ROOT / BASE_SOURCE_RELATIVE).resolve(),
            "the independently frozen V10 cache-safe owner source changed")
    observed, payload = core.bounded_file(
        ROOT / BASE_REPORT_RELATIVE, maximum=MAX_REPORT_BYTES,
        label="actual exclusively published passing V10 native-owner report",
        keep=True,
    )
    require(observed == pins["base_report"] and isinstance(payload, bytes),
            "the explicitly provided V10 base hash is not the actual real report")
    report = core.decode_report(payload, label="actual canonical passing V10 owner")
    require(core.canonical(report) + b"\n" == payload,
            "the actual complete passing V10 owner is not original canonical JSON")
    return report, validate_base_report(report, pins)


def synthetic_base(pins: Mapping[str, str]) -> dict[str, Any]:
    report = previous_strict.synthetic_base(pins)
    workers: dict[str, Any] = {}
    native: dict[str, dict[str, str]] = {}
    for family in CORE_FAMILIES:
        report_worker, fingerprint = independent.synthetic_worker(family)
        workers[family] = report_worker
        native[family] = fingerprint
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
        "historical_v9_owner_failure_qualifies_current_build": False,
        "historical_v8_owner_failure_qualifies_current_build": False,
        "historical_v7_results_qualify_current_build": False,
        "historical_first_campaign_failure_preserved": True,
        "native_sha256_by_family": native,
        "actual_native_owner_workers": workers,
        "completed_native_owner_worker_count": 3,
        "actual_native_owner_worker_failure": None,
        "actual_v9_native_owner_failure": independent.validate_v9_owner_failure(
            independent._synthetic_v9_owner_failure(),
        ),
        "actual_v8_native_owner_failure": independent.validate_v8_owner_failure(
            independent.previous._synthetic_v8_owner_failure(),
        ),
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": BASE_REPORT_RELATIVE,
            "separate_pass_and_failure_destinations": True,
            "previous_v9_owner_failure_preserved": True,
            "previous_v8_owner_failure_preserved": True,
            "historical_v9_owner_failure_qualifies_current_build": False,
            "historical_v8_owner_failure_qualifies_current_build": False,
            "previous_v7_reports_historical": True,
            "actual_edge_failures_preserved": True,
            "exact_current_owned_candidate_source_count": 12,
            "actual_current_native_binary_count": 5,
            "actual_native_matching_workers": 3,
            "genuine_public_pickle_checks": 48,
            "genuine_match_repr_checks": 6,
            "actual_python_matching_guards_per_family": 13,
            "actual_native_loader_guards_per_family": 5,
            "exact_stage07_sentinel_checked_before_and_after": True,
            "all_cached_matcher_descendants_poisoned_before_and_after": True,
            "original_stage07_cached_alias_helper_used": True,
            "native_identity_is_independent_of_public_module": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "postfinal_wrapper_self_test": {
            "schema": BASE_SCHEMA + "-self-test",
            "status": "PASS", "passed": True, "check_count": 966,
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
            "the genuine cache-safe V10 owner source-only controls failed")
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(not any(item["name"] == name for item in checks),
                "an actual strict V10 cached-matcher poison was repeated")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (AuditV10Error, independent.AuditV10Error,
                previous_strict.AuditV9Error,
                source_v6.AuditV6Error, AssertionError,
                OSError, TypeError, ValueError, KeyError):
            accept(name, True)
        else:
            accept(name, False)

    effects = core.previous.BlockSelfTestEffects()
    with effects:
        for row in inherited["checks"]:
            accept("independent-v10:" + row["name"], row.get("passed") is True)
        accept("directly-bootstrap-only-the-trusted-v10-strict-repository-root",
               bool(sys.path) and sys.path[0] == str(ROOT))
        names = run_audit.__code__.co_names
        accept("verify-the-actual-v10-base-before-any-history-or-worker",
               names.index("load_base_report") < names.index("verify_history")
               and names.index("load_base_report")
               < names.index("candidate_free_self_test")
               and names.index("load_base_report")
               < names.index("run_native_worker"))
        reject("reject-an-unpublished-actual-v10-owner-base-report",
               lambda: required_pins())
        synthetic_pin = hashlib.sha256(
            b"synthetic-only complete V10 source control, never production",
        ).hexdigest()
        pins = required_pins(synthetic_pin)
        base = synthetic_base(pins)
        accept("validate-all-real-shape-v10-native-families-in-memory-only",
               validate_base_report(copy.deepcopy(base), pins)
               ["source_count"] == 12)
        for actual_aliases in (0, 1):
            valid_counts = copy.deepcopy(base)
            for worker in valid_counts["actual_native_owner_workers"].values():
                worker["stage07_matcher_descendant_guards"].update({
                    "cached_alias_count": actual_aliases,
                    "helper_alias_replacement_count": actual_aliases,
                })
            accept("accept-genuine-zero-or-one-cached-holder-alias:"
                   + str(actual_aliases),
                   validate_base_report(valid_counts, pins)["source_count"] == 12)

        def poison(label: str,
                   action: Callable[[dict[str, Any]], None]) -> None:
            changed = copy.deepcopy(base)
            action(changed)
            reject("reject-v10-strict:" + label,
                   lambda: validate_base_report(changed, pins))

        for field, wrong in (
            ("schema", independent.previous.SCHEMA),
            ("postfinal_schema", independent.previous.SCHEMA),
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
            ("historical_v9_owner_failure_qualifies_current_build", True),
            ("historical_v8_owner_failure_qualifies_current_build", True),
            ("historical_v7_results_qualify_current_build", True),
        ):
            poison("substitute-an-actual-independent-base-field:" + field,
                   lambda report, field=field, wrong=wrong:
                   report.update({field: wrong}))
        for family in CORE_FAMILIES:
            poison("remove-an-actual-native-family:" + family,
                   lambda report, family=family:
                   report["actual_native_owner_workers"].pop(family))
            for flag in independent.SENTINEL_FLAGS:
                poison("forge-the-real-stage07-blocker:" + family + ":" + flag,
                       lambda report, family=family, flag=flag:
                       report["actual_native_owner_workers"][family]
                       ["stage07_guard_sentinel"].update({flag: False}))
            for phase in ("observations_before", "observations_after"):
                poison("remove-a-cache-safe-real-matcher-phase:"
                       + family + ":" + phase,
                       lambda report, family=family, phase=phase:
                       report["actual_native_owner_workers"][family]
                       ["stage07_matcher_descendant_guards"][phase].pop())
                for index, name in enumerate(
                    independent.REQUIRED_MATCHER_DESCENDANTS
                ):
                    for flag in independent.MATCHER_GUARD_FLAGS:
                        poison("restore-a-live-cached-cpython-matcher:"
                               + family + ":" + phase + ":" + name + ":" + flag,
                               lambda report, family=family, phase=phase,
                               index=index, flag=flag:
                               report["actual_native_owner_workers"][family]
                               ["stage07_matcher_descendant_guards"]
                               [phase][index].update({flag: False}))
            for field in ("cached_alias_count", "helper_alias_replacement_count"):
                poison("weaken-real-original-cached-matcher-aliases:"
                       + family + ":" + field,
                       lambda report, family=family, field=field:
                       report["actual_native_owner_workers"][family]
                       ["stage07_matcher_descendant_guards"].update({field: 0}))
                for wrong in (-1, False, True):
                    poison("reject-negative-or-bool-cached-matcher-alias:"
                           + family + ":" + field + ":" + repr(wrong),
                           lambda report, family=family, field=field, wrong=wrong:
                           report["actual_native_owner_workers"][family]
                           ["stage07_matcher_descendant_guards"].update({
                               field: wrong,
                           }))
            for field in (
                "regex_guard_observations", "regex_guard_observations_after",
                "foreign_engine_guard_observations",
                "foreign_engine_guard_observations_after",
                "native_loader_guard_observations",
                "native_loader_guard_observations_after",
                "standard_pickle_checks",
            ):
                poison("remove-an-actual-before-and-after-guard:"
                       + family + ":" + field,
                       lambda report, family=family, field=field:
                       report["actual_native_owner_workers"][family][field].pop())
            poison("hide-an-original-full-edge-failure:" + family,
                   lambda report, family=family:
                   report["historical_current_build_edge_failures"].pop(family))
        for incident_name, fields in (
            ("actual_v9_native_owner_failure", (
                ("status", "PASS"), ("sha256", "0" * 64),
                ("stderr_sha256", "0" * 64),
                ("stderr_bytes", 202), ("qualifies_current_engine", True),
                ("original_edge_worker_started", True),
            )),
            ("actual_v8_native_owner_failure", (
                ("status", "PASS"), ("sha256", "0" * 64),
                ("stderr_bytes", 0), ("qualifies_current_engine", True),
            )),
        ):
            for field, wrong in fields:
                poison("conceal-a-real-archived-native-failure:"
                       + incident_name + ":" + field,
                       lambda report, incident_name=incident_name,
                       field=field, wrong=wrong:
                       report[incident_name].update({field: wrong}))
        for flag, wrong in (
            ("append_only", False),
            ("separate_pass_and_failure_destinations", False),
            ("previous_v9_owner_failure_preserved", False),
            ("previous_v8_owner_failure_preserved", False),
            ("historical_v9_owner_failure_qualifies_current_build", True),
            ("historical_v8_owner_failure_qualifies_current_build", True),
            ("actual_edge_failures_preserved", False),
            ("exact_current_owned_candidate_source_count", 11),
            ("actual_current_native_binary_count", 4),
            ("actual_native_matching_workers", 2),
            ("genuine_public_pickle_checks", 47),
            ("genuine_match_repr_checks", 5),
            ("actual_python_matching_guards_per_family", 12),
            ("actual_native_loader_guards_per_family", 4),
            ("exact_stage07_sentinel_checked_before_and_after", False),
            ("all_cached_matcher_descendants_poisoned_before_and_after", False),
            ("original_stage07_cached_alias_helper_used", False),
            ("native_identity_is_independent_of_public_module", False),
            ("mapped_binaries_hashed_against_static_elf", False),
            ("benchmark_or_timing_executed", True),
            ("holdout_or_case_fixture_access", True),
        ):
            poison("weaken-actual-v10-independent-native-scope:" + flag,
                   lambda report, flag=flag, wrong=wrong:
                   report["postfinal_scope"].update({flag: wrong}))
        for flag, wrong in (
            ("passed", False), ("check_count", 149),
            ("candidate_imports", 1), ("subprocesses", 1),
            ("file_reads", 1), ("file_writes", 1), ("clock_samples", 1),
        ):
            poison("forge-actual-cache-safe-source-only-controls:" + flag,
                   lambda report, flag=flag, wrong=wrong:
                   report["postfinal_wrapper_self_test"].update({flag: wrong}))
        for key, value in (
            ("base_source", "0" * 64),
            ("base_report", None),
            ("base_report", BASE_SOURCE_SHA256),
            ("base_report", "invalid"),
        ):
            changed = dict(pins)
            changed[key] = value
            reject("reject-invalid-real-v10-external-pin:"
                   + key + ":" + str(value),
                   lambda changed=changed: required_pins(synthetic=changed))
        for value in (
            BASE_REPORT_RELATIVE,
            independent.FAILURE_RELATIVE,
            previous_strict.REPORT_RELATIVE,
            "performance/private-holdout.json",
            "../POSTFINAL-NO-DELEGATION-AUDIT-V10.json",
            "/tmp/POSTFINAL-NO-DELEGATION-AUDIT-V10.json",
        ):
            reject("reject-historical-or-forged-v10-strict-report:" + value,
                   lambda value=value: destination_name(value))
        for value in (REPORT_RELATIVE, FAILURE_RELATIVE):
            accept("allow-only-an-exact-independent-v10-strict-output:" + value,
                   destination_name(value) == value)

    require(len(checks) >= 150 and all(row["passed"] for row in checks),
            "a genuine strict V10 cached matcher or ownership poison escaped")
    require(effects.counts["processes"] == 0
            and effects.counts["files"] == 0
            and effects.counts["clocks"] == 0,
            "source-only V10 strict controls caused external production effects")
    core.ensure_candidate_free()
    verify_runtime()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "independent_v10_control_count": inherited["check_count"],
        "actual_base_report_digest_is_external": True,
        "base_source_sha256": BASE_SOURCE_SHA256,
        "stage07_source_sha256": independent.STAGE07_SHA256,
        "v9_native_owner_failure_sha256": independent.V9_OWNER_FAILURE_SHA256,
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
    core.validate_v3_report(current, label="actual strict cache-safe V10 native graph")
    live = source_v6._validate_fresh_graph(current)
    require(live == graph,
            "an actual native V10 source or ELF changed after its real base")
    workers: dict[str, dict[str, Any]] = {}
    failure: dict[str, Any] | None = None
    for family in CORE_FAMILIES:
        try:
            observed = independent.run_native_worker(
                family, live["native_sha256_by_family"][family],
            )
            workers[family] = observed
            if observed.get("status") != "PASS":
                failure = {
                    "schema": SCHEMA + "-actual-observed-native-owner-failure",
                    "status": "FAIL", "family": family,
                    "actual_native_owner_worker": observed,
                    "production_observations_invented": False,
                    "qualifies_current_engine": False,
                }
                break
        except independent.NativeWorkerFailure as error:
            failure = error.evidence
            break
    core.ensure_candidate_free()
    pickle_failures = sum(
        worker["standard_pickle_failure_count"]
        for worker in workers.values()
    )
    passed = (failure is None and len(workers) == len(CORE_FAMILIES)
              and pickle_failures == 0)
    actual_source, _ = core.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
        label="actual frozen independently authored V10 strict cache audit",
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
        "actual_v9_native_owner_failure": history[
            "actual_v9_native_owner_failure"
        ],
        "actual_v8_native_owner_failure": history[
            "actual_v8_native_owner_failure"
        ],
        "historical_v9_owner_failure_qualifies_current_build": False,
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
            "independently_pinned_fresh_v10_base": True,
            "base_report_hash_supplied_externally": True,
            "previous_v9_owner_failure_preserved": True,
            "previous_v8_owner_failure_preserved": True,
            "historical_v9_owner_failure_qualifies_current_build": False,
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
            "all_cached_matcher_descendants_poisoned_before_and_after": True,
            "original_stage07_cached_alias_helper_used": True,
            "persistent_cross_family_import_and_loader_guards": True,
            "native_identity_is_independent_of_public_module": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    require(live["source_count"] == 12 and live["native_binary_count"] == 5,
            "the genuine strict V10 native source or ELF denominator changed")
    if passed:
        require(report["verified_match_repr_checks"] == 6
                and report["verified_standard_pickle_count"] == 48,
                "a passing V10 strict audit weakened actual native owner obligations")
    else:
        require(failure is not None,
                "a genuine failed strict V10 worker observation was concealed")
    core.ensure_candidate_free()
    return report


def write_report(report: Mapping[str, Any], target: Path | None = None) -> str:
    require(isinstance(report, Mapping),
            "a strict V10 exclusive output must preserve a complete real report")
    expected = REPORT_PATH if report.get("passed") is True else FAILURE_PATH
    target = expected if target is None else target
    require(isinstance(target, Path)
            and target.resolve(strict=False) == expected
            and expected.parent.is_dir() and not expected.parent.is_symlink(),
            "an exclusively published strict V10 output escaped its exact path")
    destination_name(expected.relative_to(ROOT).as_posix())
    payload = core.canonical(report) + b"\n"
    require(0 < len(payload) <= MAX_REPORT_BYTES,
            "the actual bounded complete V10 strict report is too large")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(expected.parent, flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the actual exclusive strict V10 parent is not a safe directory")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(expected.name, create, 0o644, dir_fd=directory)
        try:
            view = memoryview(payload)
            while view:
                count = os.write(descriptor, view)
                require(count > 0,
                        "an exclusively created actual strict V10 report stalled")
                view = view[count:]
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
                    "a source-only V10 strict control cannot consume real evidence")
            report = candidate_free_self_test()
            sys.stdout.buffer.write(core.canonical(report) + b"\n")
            return 0
        required_pins(options.base_report_sha256)
        verify_fresh_report_targets()
        report = run_audit(str(options.base_report_sha256))
        actual_digest = write_report(report, options.output)
        summary = {
            "schema": SCHEMA,
            "status": report["status"], "result": report["result"],
            "passed": report["passed"],
            "report": REPORT_RELATIVE if report["passed"] else FAILURE_RELATIVE,
            "report_sha256": actual_digest,
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
        sys.stdout.buffer.write(core.canonical(summary) + b"\n")
        return int(not report["passed"])
    except (AuditV10Error, independent.AuditV10Error,
            previous_strict.AuditV9Error,
            independent.previous.refresh_v8.ProofV8Error,
            independent.previous.reference_v5.OfficialV5Error,
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
