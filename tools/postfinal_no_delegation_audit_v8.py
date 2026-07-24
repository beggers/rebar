#!/usr/bin/env python3
"""Prove native-owned Python-compatible matching without engine delegation."""

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v5 as source_v5
from tools import postfinal_from_scratch_audit_v6 as source_v6
from tools import postfinal_from_scratch_audit_v8 as independent
from tools import postfinal_no_delegation_audit_v7 as historical_v7


core = independent.core
SCHEMA = "rebar-postfinal-no-delegation-audit-v8"
SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v8.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V8.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
BASE_SOURCE_RELATIVE = independent.SOURCE_RELATIVE
BASE_REPORT_RELATIVE = independent.REPORT_RELATIVE
BASE_SCHEMA = independent.SCHEMA
BASE_SOURCE_SHA256 = (
    "14b8daeebfb620eafa778529f6bf11e1a4f48256dd010b25621f4e94666692c6"
)
PROTOCOL_RELATIVE = "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V8.md"
PROTOCOL_SHA256 = (
    "5c60e6ce63ff1e4c5593eaafe29971cb3557b1a0389dcd5cf41cfb00647bc399"
)
# The real source-audit report does not yet exist. Root must inject its
# actually observed exclusive SHA-256 in a separate source-first chunk.
BASE_REPORT_SHA256: str | None = None
CORE_FAMILIES = independent.CORE_FAMILIES
MAX_SOURCE_BYTES = independent.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = independent.MAX_REPORT_BYTES
MAX_WORKER_BYTES = independent.MAX_WORKER_BYTES


class AuditV8Error(source_v6.AuditV6Error):
    """A real strict native-owner, public pickle, or no-delegation proof failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV8Error(message)


def destination_name(value: Any) -> str:
    require(type(value) is str, "the exclusive V8 strict destination is not text")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts
            and "\\" not in value and "\x00" not in value
            and str(path) == value and value == REPORT_RELATIVE,
            "only the distinct exclusive V8 no-delegation report is authorized")
    return value


def verify_fresh_report_target(target: Path = REPORT_PATH) -> Path:
    require(isinstance(target, Path),
            "the exclusively created V8 strict report requires an exact path")
    absolute = target if target.is_absolute() else ROOT / target
    require(absolute.resolve() == absolute,
            "the V8 strict report is not its exact canonical path")
    require(absolute.is_relative_to(ROOT),
            "the V8 strict report escaped the approved workspace")
    destination_name(absolute.relative_to(ROOT).as_posix())
    require(absolute.parent == REPORT_PATH.parent
            and absolute.parent.is_dir() and not absolute.parent.is_symlink(),
            "the V8 strict report parent is unsafe")
    require(not absolute.exists() and not absolute.is_symlink(),
            "refusing to rerun workers or overwrite an existing V8 strict report")
    return absolute


def required_pins(
    synthetic: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    require(independent.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE
            and independent.PROTOCOL_SHA256 == PROTOCOL_SHA256,
            "the independently frozen V8 native-ownership protocol changed")
    values: dict[str, Any] = {
        "base_source": BASE_SOURCE_SHA256,
        "base_report": BASE_REPORT_SHA256,
    }
    if synthetic is not None:
        require(isinstance(synthetic, Mapping) and set(synthetic) == set(values),
                "the synthetic V8 strict source proof omitted an independent pin")
        values = dict(synthetic)
    for label, digest in values.items():
        require(core.valid_sha256(digest),
                "the actual exclusively generated V8 " + label
                + " fingerprint has not been independently published")
    require(values["base_source"] != values["base_report"],
            "the V8 base source and report cannot share an invented digest")
    return {name: str(value) for name, value in values.items()}


def validate_base_report(
    document: Any, pins: Mapping[str, str],
) -> dict[str, Any]:
    require(isinstance(document, dict),
            "the independently authored V8 base source report is not an object")
    expected = {
        "schema": BASE_SCHEMA, "postfinal_schema": BASE_SCHEMA,
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": BASE_SOURCE_RELATIVE,
        "audit_source_sha256": pins["base_source"],
        "native_ownership_protocol_path": PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": PROTOCOL_SHA256,
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
    }
    for key, value in expected.items():
        require(document.get(key) == value,
                "the independent V8 native source proof changed: " + key)
    graph = source_v6._validate_fresh_graph(document)
    require(graph["source_count"] == 12 and graph["native_binary_count"] == 5,
            "the actual independent V8 source graph lost owned source or native ELF")
    require(document.get("verified_candidate_source_paths") == graph["source_paths"]
            and document.get("native_sha256_by_family")
            == graph["native_sha256_by_family"],
            "the independent V8 source report substituted native provenance")
    observations = document.get("actual_native_owner_workers")
    require(isinstance(observations, dict)
            and set(observations) == set(CORE_FAMILIES),
            "the independent V8 source report omitted a genuine matching family")
    for family in CORE_FAMILIES:
        independent.validate_worker(
            observations[family], family, graph["native_sha256_by_family"][family]
        )
    historical = document.get("historical_current_build_edge_failures")
    require(isinstance(historical, dict)
            and set(historical) == set(CORE_FAMILIES)
            and set(independent.V7_EDGE_FAILURES) == set(CORE_FAMILIES),
            "the independent V8 audit omitted a real Rust, C, or Zig edge failure")
    for family in CORE_FAMILIES:
        evidence = historical[family]
        expected_failure = independent.V7_EDGE_EXPECTATIONS[family]
        failed = expected_failure["failed"]
        require(isinstance(evidence, dict)
                and evidence.get("status") == "FAIL"
                and evidence.get("qualifies_current_engine") is False
                and evidence.get("family") == family
                and evidence.get("candidate_module")
                == "candidates." + family + "_candidate"
                and evidence.get("archive_sha256")
                == independent.V7_EDGE_FAILURES[family][1]
                and evidence.get("seed") == independent.EDGE_SEED
                and evidence.get("checks") == independent.EDGE_CHECKS
                and evidence.get("category_count") == independent.EDGE_CATEGORIES
                and evidence.get("failed") == failed
                and evidence.get("failure_rows_preserved") == failed
                and evidence.get("expected_sha256")
                == independent.EDGE_REFERENCE_SHA256
                and core.valid_sha256(evidence.get("actual_sha256"))
                and evidence.get("actual_sha256")
                == expected_failure["actual_sha256"],
                "a real complete frozen edge failure was hidden or substituted: " + family)
    scope = document.get("postfinal_scope")
    require(isinstance(scope, dict)
            and scope.get("append_only") is True
            and scope.get("exclusive_report_path") == BASE_REPORT_RELATIVE
            and scope.get("previous_v7_reports_historical") is True
            and scope.get("actual_edge_failures_preserved") is True
            and scope.get("exact_current_owned_candidate_source_count") == 12
            and scope.get("actual_current_native_binary_count") == 5
            and scope.get("actual_native_matching_workers") == 3
            and scope.get("genuine_public_pickle_checks") == 48
            and scope.get("genuine_match_repr_checks") == 6
            and scope.get("actual_python_matching_guards_per_family") == 13
            and scope.get("native_identity_is_independent_of_public_module") is True
            and scope.get("mapped_binaries_hashed_against_static_elf") is True
            and scope.get("benchmark_or_timing_executed") is False
            and scope.get("holdout_or_case_fixture_access") is False,
            "the independent V8 source audit weakened actual native-owner isolation")
    controls = document.get("postfinal_wrapper_self_test")
    require(isinstance(controls, dict)
            and controls.get("schema") == BASE_SCHEMA + "-self-test"
            and controls.get("passed") is True
            and controls.get("check_count", 0) >= 540
            and controls.get("candidate_imports") == 0
            and controls.get("subprocesses") == 0
            and controls.get("file_reads") == 0
            and controls.get("file_writes") == 0
            and controls.get("clock_samples") == 0,
            "the independent V8 source-only ownership protections were weakened")
    return graph


def load_base_report(pins: Mapping[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    actual_source, _ = core.bounded_file(
        ROOT / BASE_SOURCE_RELATIVE, maximum=MAX_SOURCE_BYTES,
        label="independently frozen V8 native source-audit controller",
    )
    require(actual_source == pins["base_source"]
            and Path(independent.__file__).resolve() == ROOT / BASE_SOURCE_RELATIVE,
            "the independently frozen V8 source controller changed")
    observed, payload = core.bounded_file(
        ROOT / BASE_REPORT_RELATIVE, maximum=MAX_REPORT_BYTES,
        label="exclusively generated passing V8 native source audit", keep=True,
    )
    require(observed == pins["base_report"] and isinstance(payload, bytes),
            "the actual published passing V8 source report was changed")
    document = core.decode_report(payload,
                                  label="actual complete passing V8 source audit")
    return document, validate_base_report(document, pins)


def synthetic_base(pins: Mapping[str, str]) -> dict[str, Any]:
    workers: dict[str, Any] = {}
    native: dict[str, dict[str, str]] = {}
    families: dict[str, Any] = {}
    all_paths: list[str] = []
    native_files: dict[str, Any] = {}
    for family in CORE_FAMILIES:
        worker, fingerprints = independent.synthetic_worker(family)
        workers[family] = worker
        native[family] = fingerprints
        source_paths = independent.OWNED_SOURCE_PATHS[family]
        all_paths.extend(source_paths)
        public = source_paths[0]
        families[family] = {
            "passed": True,
            "owned_pipeline": {"passed": True, "issues": []},
            "python_source": {
                "file": public, "passed": True, "issues": [],
                "sha256": hashlib.sha256(("synthetic:" + public).encode()).hexdigest(),
            },
            "native_sources": [
                {
                    "file": path, "passed": True, "issues": [],
                    "sha256": hashlib.sha256(("synthetic:" + path).encode()).hexdigest(),
                }
                for path in source_paths[1:]
            ],
        }
        native_files[family] = {
            "files": {
                role: {
                    "file": relative,
                    "sha256": fingerprints[relative],
                    "elf_class": 64,
                    "forbidden_regex_symbols": [],
                    "cross_candidate_symbols": [],
                    "runpaths": (["$ORIGIN"] if family in {"rust", "zig"}
                                 and role == "bridge" else []),
                    "needed": [],
                }
                for role, relative in independent.OWNED_NATIVE_PATHS[family].items()
            },
        }
    families["ast"] = {"passed": True}
    return {
        "schema": BASE_SCHEMA, "postfinal_schema": BASE_SCHEMA,
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": BASE_SOURCE_RELATIVE,
        "audit_source_sha256": pins["base_source"],
        "native_ownership_protocol_path": independent.PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": independent.PROTOCOL_SHA256,
        "historical_v7_results_qualify_current_build": False,
        "historical_first_campaign_failure_preserved": True,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_candidate_source_paths": all_paths,
        "verified_native_role_count": 5,
        "native_sha256_by_family": native,
        "match_repr_checks_per_family": 2,
        "verified_match_repr_checks": 6,
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": 48,
        "standard_pickle_failure_count": 0,
        "actual_native_owner_workers": workers,
        "families": families,
        "native_elf_provenance": {
            "passed": True, "audited_binary_count": 5,
            "expected_binary_count": 5, "families": native_files,
        },
        "manifest_provenance": {
            "passed": True, "issues": [], "python_dependencies": [],
            "rust_third_party_dependency_count": 0,
            "rust_lock_packages": ["rebar-rust-continuation"],
        },
        "runtime_native_mapping_provenance": {"passed": True},
        "historical_current_build_edge_failures": {
            family: {
                "status": "FAIL", "qualifies_current_engine": False,
                "family": family,
                "candidate_module": "candidates." + family + "_candidate",
                "archive_sha256": independent.V7_EDGE_FAILURES[family][1],
                "seed": independent.EDGE_SEED,
                "checks": independent.EDGE_CHECKS,
                "category_count": independent.EDGE_CATEGORIES,
                "failed": independent.V7_EDGE_EXPECTATIONS[family]["failed"],
                "failure_rows_preserved": independent.V7_EDGE_EXPECTATIONS[family][
                    "failed"
                ],
                "expected_sha256": independent.EDGE_REFERENCE_SHA256,
                "actual_sha256": independent.V7_EDGE_EXPECTATIONS[family][
                    "actual_sha256"
                ],
            }
            for family in CORE_FAMILIES
        },
        "postfinal_scope": {
            "append_only": True, "exclusive_report_path": BASE_REPORT_RELATIVE,
            "previous_v7_reports_historical": True,
            "actual_edge_failures_preserved": True,
            "exact_current_owned_candidate_source_count": 12,
            "actual_current_native_binary_count": 5,
            "actual_native_matching_workers": 3,
            "genuine_public_pickle_checks": 48,
            "genuine_match_repr_checks": 6,
            "actual_python_matching_guards_per_family": 13,
            "native_identity_is_independent_of_public_module": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "postfinal_wrapper_self_test": {
            "schema": BASE_SCHEMA + "-self-test", "passed": True,
            "check_count": 540, "candidate_imports": 0,
            "subprocesses": 0, "file_reads": 0,
            "file_writes": 0, "clock_samples": 0,
        },
    }


def candidate_free_self_test() -> dict[str, Any]:
    core.ensure_candidate_free()
    inherited = historical_v7.candidate_free_self_test()
    require(inherited.get("passed") is True
            and inherited.get("check_count", 0) >= 120,
            "the unchanged historical V7 no-delegation protections failed")
    independent_controls = independent.candidate_free_self_test()
    require(independent_controls.get("passed") is True
            and independent_controls.get("check_count", 0) >= 540,
            "the independently authored V8 ownership controls failed")
    checks: list[dict[str, Any]] = []

    def accepted(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (AuditV8Error, independent.AuditV8Error,
                source_v6.AuditV6Error, AssertionError, TypeError,
                ValueError, KeyError, OSError):
            accepted(name, True)
        else:
            accepted(name, False)

    effects = core.previous.BlockSelfTestEffects()
    with effects:
        for item in inherited["checks"]:
            accepted("historical-strict-v7:" + item["name"],
                     item.get("passed") is True)
        for item in independent_controls["checks"]:
            accepted("independent-v8:" + item["name"],
                     item.get("passed") is True)
        rejected("reject-unpublished-real-v8-base-report-hash",
                 lambda: required_pins())
        synthetic = required_pins({
            "base_source": BASE_SOURCE_SHA256,
            "base_report": hashlib.sha256(b"explicit synthetic V8 base report").hexdigest(),
        })
        base = synthetic_base(synthetic)
        accepted("accept-complete-source-bound-in-memory-v8-native-base",
                 validate_base_report(copy.deepcopy(base), synthetic)["source_count"] == 12)

        def poison(label: str, change: Callable[[dict[str, Any]], None]) -> None:
            changed = copy.deepcopy(base)
            change(changed)
            rejected("reject-v8-strict-base:" + label,
                     lambda: validate_base_report(changed, synthetic))

        for key, value in (
            ("status", "FAIL"), ("result", "FAIL"), ("passed", False),
            ("audit_source_sha256", "0" * 64),
            ("native_ownership_protocol_sha256", "0" * 64),
            ("verified_core_family_count", 2),
            ("verified_distinct_pipeline_count", 2),
            ("verified_candidate_source_count", 11),
            ("verified_native_role_count", 4),
            ("verified_match_repr_checks", 5),
            ("standard_pickle_checks", 47),
            ("standard_pickle_failure_count", 1),
            ("historical_v7_results_qualify_current_build", True),
            ("historical_first_campaign_failure_preserved", False),
        ):
            poison("changed-" + key,
                   lambda row, key=key, value=value: row.update({key: value}))
        for family in CORE_FAMILIES:
            poison("foreign-public-match-owner:" + family,
                   lambda row, family=family:
                   row["actual_native_owner_workers"][family][
                       "public_type_ownership"
                   ]["Match"].update(native_owner_module="candidates._foreign"))
            poison("missing-cpython-public-module:" + family,
                   lambda row, family=family:
                   row["actual_native_owner_workers"][family][
                       "public_type_ownership"
                   ]["Match"].update(public_module="candidates._foreign"))
            poison("non-cpython-pattern-groupindex:" + family,
                   lambda row, family=family:
                   row["actual_native_owner_workers"][family]["records"][0][
                       "pattern_readonly_groupindex_error"
                   ].update(message="foreign.Pattern"))
            poison("dropped-pickle-observation:" + family,
                   lambda row, family=family:
                   row["actual_native_owner_workers"][family][
                       "standard_pickle_checks"
                   ].pop())
            poison("missing-persistent-stdlib-guard:" + family,
                   lambda row, family=family:
                   row["actual_native_owner_workers"][family]["guard"].update(
                       stdlib_re_blocked=False
                   ))
            poison("missing-native-elf-mapping:" + family,
                   lambda row, family=family:
                   row["native_elf_provenance"]["families"][family]["files"].clear())
        for family in CORE_FAMILIES:
            poison("conceal-actual-frozen-edge-failure:" + family,
                   lambda row, family=family:
                   row["historical_current_build_edge_failures"].pop(family))
            for field, value in (
                ("status", "PASS"),
                ("qualifies_current_engine", True),
                ("family", "foreign"),
                ("candidate_module", "candidates.foreign_candidate"),
                ("archive_sha256", "0" * 64),
                ("seed", 0),
                ("checks", independent.EDGE_CHECKS - 1),
                ("category_count", independent.EDGE_CATEGORIES - 1),
                ("failed", 0),
                ("failure_rows_preserved", 0),
                ("expected_sha256", "0" * 64),
                ("actual_sha256", independent.EDGE_REFERENCE_SHA256),
            ):
                poison("changed-real-edge-failure:" + family + ":" + field,
                       lambda row, family=family, field=field, value=value:
                       row["historical_current_build_edge_failures"][family].update({
                           field: value
                       }))
        for path in (
            BASE_REPORT_RELATIVE,
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json",
            "performance/private-holdout.json",
            "../POSTFINAL-NO-DELEGATION-AUDIT-V8.json",
        ):
            rejected("reject-unapproved-strict-output:" + path,
                     lambda path=path: destination_name(path))
        accepted("accept-exact-distinct-exclusive-v8-strict-report",
                 destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        rejected("reject-missing-synthetic-base-report-pin",
                 lambda: required_pins({"base_source": BASE_SOURCE_SHA256,
                                        "base_report": None}))
        rejected("reject-same-source-and-report-pin",
                 lambda: required_pins({"base_source": BASE_SOURCE_SHA256,
                                        "base_report": BASE_SOURCE_SHA256}))

    require(len(checks) >= 700 and all(row["passed"] for row in checks),
            "a strict source-only V8 native or pickle poison was accepted")
    require(len({row["name"] for row in checks}) == len(checks),
            "a strict V8 no-delegation poison case was repeated")
    require(effects.counts["processes"] == 0
            and effects.counts["files"] == 0
            and effects.counts["clocks"] == 0,
            "the strict candidate-free V8 control caused a production side effect")
    core.ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "historical_v7_strict_control_count": inherited["check_count"],
        "independent_v8_source_control_count": independent_controls["check_count"],
        "real_base_report_sha256_published": BASE_REPORT_SHA256 is not None,
        "candidate_imports": 0, "subprocesses": effects.counts["processes"],
        "file_reads": effects.counts["files"],
        "file_writes": effects.counts["files"],
        "clock_samples": effects.counts["clocks"],
        "actual_public_pickle_cases_required": 48,
        "actual_matching_poison_guards_per_family": 13,
        "synthetic_results_qualify_candidates": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }


def run_audit() -> dict[str, Any]:
    core.verify_production_runtime()
    core.ensure_candidate_free()
    pins = required_pins()
    history = independent.verify_history()
    controls = candidate_free_self_test()
    base, approved_graph = load_base_report(pins)
    core.ensure_candidate_free()
    gc.collect()
    with source_v5.allow_owned_locale_ctype():
        fresh = core.audit()
    core.validate_v3_report(fresh, label="fresh independent strict V8 native source graph")
    live = source_v6._validate_fresh_graph(fresh)
    require(live == approved_graph,
            "an actual owned native source or binary changed after its V8 base audit")
    strict: dict[str, dict[str, Any]] = {}
    worker_failure: dict[str, Any] | None = None
    for family in CORE_FAMILIES:
        try:
            strict[family] = independent.run_native_worker(
                family, live["native_sha256_by_family"][family]
            )
        except independent.NativeWorkerFailure as error:
            worker_failure = error.evidence
            break
    core.ensure_candidate_free()
    pickle_failures = sum(
        worker["standard_pickle_failure_count"] for worker in strict.values()
    )
    source_sha256, _ = core.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
        label="actual exclusively frozen V8 no-delegation audit source",
    )
    passed = worker_failure is None and len(strict) == len(CORE_FAMILIES)
    passed = passed and not pickle_failures
    report = dict(fresh)
    report.update({
        "schema": SCHEMA, "postfinal_schema": SCHEMA,
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL", "passed": passed,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": source_sha256,
        "base_audit_postfinal_schema": BASE_SCHEMA,
        "base_audit_source_path": BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": pins["base_source"],
        "base_audit_report_path": BASE_REPORT_RELATIVE,
        "base_audit_report_sha256": pins["base_report"],
        "native_ownership_protocol_path": independent.PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": independent.PROTOCOL_SHA256,
        "historical_public_input_sha256": history["historical_input_sha256"],
        "historical_current_build_edge_failures": history["real_edge_failures"],
        "historical_v7_results_qualify_current_build": False,
        "postfinal_wrapper_self_test": controls,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": live["source_count"],
        "verified_candidate_source_paths": live["source_paths"],
        "verified_native_role_count": live["native_binary_count"],
        "native_sha256_by_family": live["native_sha256_by_family"],
        "independent_base_native_owner_workers": base["actual_native_owner_workers"],
        "actual_native_owner_workers": strict,
        "actual_native_owner_worker_failure": worker_failure,
        "completed_native_owner_worker_count": len(strict),
        "unstarted_native_owner_families": [
            family for family in CORE_FAMILIES
            if family not in strict
            and (worker_failure is None or family != worker_failure.get("family"))
        ],
        "public_type_ownership": {
            family: worker["public_type_ownership"]
            for family, worker in strict.items()
        },
        "strict_public_match_repr": strict,
        "verified_match_repr_checks": sum(
            worker["match_repr_checks"] for worker in strict.values()
        ),
        "verified_standard_pickle_count": sum(
            worker["standard_pickle_check_count"] for worker in strict.values()
        ),
        "standard_pickle_failure_count": pickle_failures,
        "postfinal_scope": {
            "append_only": True, "exclusive_report_path": REPORT_RELATIVE,
            "independently_pinned_fresh_v8_base": True,
            "historical_v7_report_preserved": True,
            "historical_v7_reports_qualify_current_build": False,
            "actual_edge_failures_preserved": True,
            "actual_current_native_binary_count": 5,
            "exact_current_owned_candidate_source_count": 12,
            "independently_executed_native_owner_workers": len(strict)
                + int(worker_failure is not None),
            "genuine_public_pickle_checks": sum(
                worker["standard_pickle_check_count"] for worker in strict.values()
            ),
            "genuine_match_repr_checks": sum(
                worker["match_repr_checks"] for worker in strict.values()
            ),
            "actual_python_matching_guards_per_family": 13,
            "persistent_cross_family_import_and_loader_guards": True,
            "native_identity_is_independent_of_public_module": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    require(report["verified_candidate_source_count"] == 12
            and report["verified_native_role_count"] == 5,
            "the strict V8 current native or source denominator changed")
    if passed:
        require(report["verified_match_repr_checks"] == 6
                and report["verified_standard_pickle_count"] == 48,
                "a passing strict V8 audit weakened genuine matching or pickle")
    else:
        require(worker_failure is not None or pickle_failures > 0,
                "a failing strict V8 audit invented its real matching failure")
    core.ensure_candidate_free()
    return report


def write_report(report: Mapping[str, Any], target: Path = REPORT_PATH) -> str:
    require(isinstance(target, Path), "the V8 strict output must be an exact path")
    relative = (
        target.relative_to(ROOT).as_posix()
        if target.is_absolute() and target.is_relative_to(ROOT)
        else target.as_posix() if not target.is_absolute() else ""
    )
    destination_name(relative)
    parent = REPORT_PATH.parent.resolve(strict=True)
    require(not target.is_symlink() and target.name == REPORT_PATH.name
            and target.parent.resolve(strict=True) == parent,
            "the exclusive V8 strict report escaped its authorized destination")
    payload = core.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES,
            "the complete strict V8 report exceeds its bounded size")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(parent, flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the exclusively opened strict V8 directory is not genuine")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(REPORT_PATH.name, create, 0o644, dir_fd=directory)
        try:
            pending = memoryview(payload)
            while pending:
                wrote = os.write(descriptor, pending)
                require(wrote > 0, "the exclusive V8 strict report write stalled")
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
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    options = parser.parse_args(arguments)
    try:
        core.ensure_candidate_free()
        if options.self_test:
            require(options.output == REPORT_PATH,
                    "the strict source-only self-test cannot create evidence")
            result = candidate_free_self_test()
            sys.stdout.buffer.write(core.canonical(result) + b"\n")
            return 0
        verify_fresh_report_target(options.output)
        report = run_audit()
        digest = write_report(report, options.output)
        summary = {
            "schema": SCHEMA, "status": report["status"],
            "result": report["result"], "passed": report["passed"],
            "report": REPORT_RELATIVE, "report_sha256": digest,
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
    except (source_v6.AuditV6Error, independent.AuditV8Error,
            OSError, RuntimeError, TypeError, ValueError, KeyError,
            UnicodeError, subprocess.SubprocessError) as error:
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA, "status": "FAIL", "result": "FAIL", "passed": False,
            "error_type": type(error).__name__, "error": str(error),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
