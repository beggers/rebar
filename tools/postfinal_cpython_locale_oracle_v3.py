#!/usr/bin/env python3
"""Recheck all immutable official Python tests after the real V2 failure."""

from __future__ import annotations

import argparse
import copy
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v2 as previous
from tools import postfinal_cpython_locale_v2_failure as incident


original = previous.previous
SCHEMA = "rebar-postfinal-cpython-public-locale-v3"
SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v3.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V3.md"
REPORT_RELATIVE = "oracle/cpython-3.14.6/evidence/postfinal-locale-v3-all.json"
EVIDENCE_PATH = ROOT / REPORT_RELATIVE

V7_BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v7.py"
V7_BASE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"
V7_BASE_SCHEMA = "rebar-postfinal-from-scratch-audit-v7"
V7_BASE_SOURCE_SHA256: str | None = (
    "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487"
)
# Root pinned this only after actually executing and exclusively preserving
# the independently passed source audit; the strict proof remains fail-closed.
V7_BASE_REPORT_SHA256: str | None = (
    "efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a"
)
V7_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v7.py"
V7_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json"
)
V7_STRICT_SCHEMA = "rebar-postfinal-no-delegation-audit-v7"
V7_STRICT_SOURCE_SHA256: str | None = (
    "9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4"
)
V7_STRICT_REPORT_SHA256: str | None = (
    "1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34"
)

V2_FAILURE_SHA256 = (
    "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f"
)
CORE_FAMILIES = previous.CORE_FAMILIES
OWNED_BRIDGES = dict(previous.OWNED_BRIDGES)
MATCH_CASES = (
    ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
    ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
)


class OfficialV3Error(AssertionError):
    """The fresh official test cannot safely qualify a repaired engine."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OfficialV3Error(message)


def destination(value: Any) -> str:
    require(type(value) is str, "the official output path must be text")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute()
        and ".." not in parsed.parts
        and "\\" not in value
        and "\x00" not in value
        and str(parsed) == value
        and value == REPORT_RELATIVE,
        "only the exact new exclusive version-three official report is authorized",
    )
    return value


def pins(overrides: Mapping[str, Any] | None = None) -> dict[str, str]:
    actual: Mapping[str, Any]
    if overrides is None:
        actual = {
            "base_source": V7_BASE_SOURCE_SHA256,
            "base_report": V7_BASE_REPORT_SHA256,
            "strict_source": V7_STRICT_SOURCE_SHA256,
            "strict_report": V7_STRICT_REPORT_SHA256,
        }
    else:
        actual = overrides
    require(
        isinstance(actual, Mapping)
        and set(actual) == {
            "base_source", "base_report", "strict_source", "strict_report"
        }
        and all(original.is_sha256(value) for value in actual.values())
        and len(set(actual.values())) == 4,
        "all four actual current V7 source and strict report hashes are required",
    )
    return {key: str(value) for key, value in actual.items()}


def validate_match_rows(value: Any, family: str) -> list[dict[str, Any]]:
    if isinstance(value, list):
        rows = value
    elif isinstance(value, Mapping):
        rows = value.get("records", value.get("match_representation_checks"))
    else:
        rows = None
    require(isinstance(rows, list) and len(rows) == 2,
            "a native engine omitted an actual official string or bytes match")
    normalized: list[dict[str, Any]] = []
    for index, (kind, pattern, subject, matched) in enumerate(MATCH_CASES):
        row = rows[index]
        require(isinstance(row, Mapping), "an official match record is malformed")
        owner = row.get(
            "match_type_module", row.get("match_module", row.get("owner_module")),
        )
        qualified = row.get(
            "match_type_qualified_name",
            row.get("match_qualified_name", row.get("qualified_name")),
        )
        actual = row.get("observed_repr", row.get("actual_repr"))
        expected = (
            "<" + OWNED_BRIDGES[family] + ".Match object; span=(1, 12), match="
            + repr(matched) + ">"
        )
        require(
            row.get("id") == family + ":match-repr:" + kind
            and row.get("kind") == kind
            and row.get("passed") is True
            and owner == OWNED_BRIDGES[family]
            and qualified == "Match"
            and row.get("span") == [1, 12]
            and row.get("pattern_representation") == repr(pattern)
            and row.get("subject_representation") == repr(subject)
            and row.get("matched_representation") == repr(matched)
            and actual == expected
            and row.get("expected_repr") == expected
            and row.get("native_type_identity") is True
            and row.get("genuine_matching_executed") is True,
            "the actual repaired official representation failed: "
            + family + "/" + kind,
        )
        normalized.append({
            "role": family, "kind": kind,
            "match_type_module": owner,
            "match_type_qualified_name": "Match",
            "span": [1, 12], "observed_repr": expected,
            "passed": True,
        })
    return normalized


def validate_v7_audits(
    source: dict[str, Any], strict: dict[str, Any], *,
    source_relative: str, strict_relative: str, source_digest: str,
    _synthetic_pins: Mapping[str, Any] | None = None,
) -> tuple[dict[str, str], dict[str, str]]:
    current = pins(_synthetic_pins)
    require(source_relative == V7_BASE_REPORT_RELATIVE,
            "a stale V6 source audit cannot qualify the newly repaired engines")
    require(strict_relative == V7_STRICT_REPORT_RELATIVE,
            "a stale V6 strict audit cannot qualify the newly repaired engines")
    require(source_digest == current["base_report"],
            "the current V7 source report was replaced")
    require(isinstance(source, dict) and isinstance(strict, dict),
            "both genuinely passing V7 independence reports are required")
    for label, document, schema, controller, expected in (
        ("source", source, V7_BASE_SCHEMA,
         V7_BASE_SOURCE_RELATIVE, current["base_source"]),
        ("strict", strict, V7_STRICT_SCHEMA,
         V7_STRICT_SOURCE_RELATIVE, current["strict_source"]),
    ):
        require(
            document.get("schema") == schema
            and document.get("postfinal_schema") == schema
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("passed") is True
            and document.get("audit_source_path") == controller
            and document.get("audit_source_sha256") == expected
            and document.get("verified_core_family_count") == 3
            and document.get("verified_distinct_pipeline_count") == 4,
            "the current repaired " + label + " audit is missing or false",
        )
        families = document.get("families")
        require(isinstance(families, dict)
                and set(families) == previous.ALL_FAMILIES,
                "an independently written native family was omitted")
        for family in CORE_FAMILIES:
            require(isinstance(families[family], dict)
                    and families[family].get("passed") is True,
                    "the repaired native pipeline did not pass: " + family)
    require(
        source.get("previous_v6_report_historical") is True
        and source.get("previous_v6_strict_report_historical") is True
        and source.get("official_v2_source_path") == previous.SOURCE_RELATIVE
        and source.get("official_v2_source_sha256")
        == incident.OFFICIAL_SOURCE_SHA256
        and source.get("official_v2_protocol_path")
        == incident.OFFICIAL_PROTOCOL_RELATIVE
        and source.get("official_v2_protocol_sha256")
        == incident.OFFICIAL_PROTOCOL_SHA256
        and source.get("official_v2_rust_failure_path") == incident.REPORT_RELATIVE
        and source.get("official_v2_rust_failure_sha256") == V2_FAILURE_SHA256
        and source.get("official_v2_rust_failure_historical") is True,
        "the V7 source audit hid the authentic first Rust official failure",
    )
    require(
        strict.get("base_audit_source_path") == V7_BASE_SOURCE_RELATIVE
        and strict.get("base_audit_source_sha256") == current["base_source"]
        and strict.get("base_audit_report_path") == V7_BASE_REPORT_RELATIVE
        and strict.get("base_audit_report_sha256") == current["base_report"]
        and strict.get("base_audit_postfinal_schema") == V7_BASE_SCHEMA
        and strict.get("previous_v6_report_historical") is True
        and strict.get("previous_v6_source_report_historical") is True
        and strict.get("inherited_control_count") == 76
        and strict.get("official_v2_failure_preserved") is True
        and strict.get("official_v2_failure_qualifies_current_engines") is False,
        "the V7 strict proof mixed stale sources or hid the real V2 failure",
    )
    sources, binaries, by_family = previous._base_graph(source)
    require(strict.get("qualified_source_fingerprints") == sources,
            "the strict audit omitted any of the twelve repaired sources")
    require(strict.get("native_elf_fingerprints") == binaries,
            "the strict audit omitted any of the five rebuilt binaries")
    require(strict.get("native_elf_provenance") == source.get("native_elf_provenance")
            and strict.get("manifest_provenance") == source.get("manifest_provenance"),
            "the separate audits disagree on engines, binaries, or dependencies")
    require(source.get("standard_pickle_checks") == 48
            and source.get("standard_pickle_checks_per_family") == 16
            and strict.get("verified_standard_pickle_count") == 48
            and strict.get("verified_public_type_family_count") == 3
            and source.get("verified_match_repr_checks") == 6
            and source.get("match_repr_checks_per_family") == 2
            and strict.get("verified_match_repr_checks") == 6,
            "the repaired proofs omitted a real pickle or official display case")
    source_owners = source.get("public_type_ownership")
    strict_owners = strict.get("public_type_ownership")
    source_repr = source.get("public_match_repr")
    strict_repr = strict.get("public_match_repr")
    require(all(isinstance(value, dict) and set(value) == set(CORE_FAMILIES)
                for value in (source_owners, strict_owners, source_repr, strict_repr)),
            "a real owned type or match representation family was omitted")
    require(strict_repr == source_repr,
            "strict and source auditors observed different native match records")
    for family in CORE_FAMILIES:
        base_owner = source_owners[family]
        require(
            isinstance(base_owner, dict)
            and base_owner.get("schema") == previous.V6_BASE_SCHEMA + "-owned-types"
            and base_owner.get("status") == "PASS"
            and base_owner.get("passed") is True
            and base_owner.get("family") == family
            and base_owner.get("native_sha256") == by_family[family]
            and base_owner.get("standard_pickle_checks") == 16
            and isinstance(base_owner.get("records"), list)
            and len(base_owner["records"]) == 16
            and all(isinstance(item, dict)
                    and item.get("passed") is True
                    and item.get("standard_pickle_round_trip") is True
                    for item in base_owner["records"]),
            "the repaired source proof omitted true public pickle types: " + family,
        )
        worker = strict_owners[family]
        require(
            isinstance(worker, dict)
            and worker.get("schema")
            == "rebar-postfinal-no-delegation-public-owner-worker-v7"
            and worker.get("status") == "PASS"
            and worker.get("role") == family
            and worker.get("native_binary_sha256") == by_family[family]
            and worker.get("standard_pickle_check_count") == 16
            and worker.get("match_representation_check_count") == 2
            and worker.get("match_repr_checks") == 2
            and worker.get("genuine_matching_executed") is True
            and worker.get("cached_json_decoder_regex_blocked") is True
            and worker.get("benchmark_or_timing_executed") is False
            and worker.get("holdout_or_case_fixture_access") is False
            and isinstance(worker.get("standard_pickle_checks"), list)
            and len(worker["standard_pickle_checks"]) == 16
            and all(isinstance(row, dict) and row.get("passed") is True
                    for row in worker["standard_pickle_checks"]),
            "the guarded strict worker omitted real pickle or match behavior: " + family,
        )
        previous._validate_guard(worker.get("guard"), family)
        representation = source_repr[family]
        require(
            isinstance(representation, dict)
            and representation.get("schema") == V7_BASE_SCHEMA + "-match-repr-worker"
            and representation.get("status") == "PASS"
            and representation.get("result") == "PASS"
            and representation.get("passed") is True
            and representation.get("family") == family
            and representation.get("candidate_module")
            == "candidates." + family + "_candidate"
            and representation.get("native_bridge_module") == OWNED_BRIDGES[family]
            and representation.get("native_binary_sha256") == by_family[family]
            and representation.get("match_repr_checks") == 2
            and representation.get("genuine_matching_executed") is True
            and representation.get("external_regex_packages") == 0
            and representation.get("benchmark_or_timing_executed") is False
            and representation.get("fixture_accessed") is False,
            "the source omitted a genuinely executed official match: " + family,
        )
        previous._validate_guard(representation.get("guard"), family)
        source_rows = validate_match_rows(representation, family)
        strict_rows = validate_match_rows(
            worker.get("match_representation_checks"), family,
        )
        require(source_rows == strict_rows,
                "independent actual match workers disagree: " + family)
    scope = strict.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("fresh_v7_source_report_only") is True
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("actual_string_and_bytes_match_repr_verified") is True
        and scope.get("actual_official_v2_rust_failure_preserved") is True
        and scope.get("all_five_native_loader_aliases_blocked") is True
        and scope.get("enum_json_decoder_registry_bypass_blocked") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the genuine V7 independence scope or exact repr repair was weakened",
    )
    return sources, binaries


def validate_history() -> dict[str, Any]:
    prior = previous._validate_historical_v1()
    for path, expected in (
        (previous.SOURCE_RELATIVE, incident.OFFICIAL_SOURCE_SHA256),
        (incident.OFFICIAL_PROTOCOL_RELATIVE, incident.OFFICIAL_PROTOCOL_SHA256),
        (incident.SOURCE_RELATIVE, "42069714991730daff44351eb76ef2fe44478720eb0c51d76b9ea162600b96a5"),
        (incident.PROTOCOL_RELATIVE, "75e9a2709c7755de96ae23106db536a38bfd97a80fb37c5ea3f6a98139e26818"),
    ):
        candidate = original.checked_repo_path(path)
        require(original.sha256_path(candidate) == expected,
                "a frozen authentic official experiment changed: " + path)
    failure_path = original.checked_repo_path(incident.REPORT_RELATIVE)
    require(original.sha256_path(failure_path) == V2_FAILURE_SHA256,
            "the genuine first official Rust failure was concealed or changed")
    failure = original.read_json(failure_path)
    incident.validate_report(failure)
    require(not previous.EVIDENCE_PATH.exists()
            and not previous.EVIDENCE_PATH.is_symlink(),
            "the failed official V2 experiment cannot become a passing result")
    return {
        "version_one": prior,
        "version_two": {
            "source_path": previous.SOURCE_RELATIVE,
            "source_sha256": incident.OFFICIAL_SOURCE_SHA256,
            "protocol_path": incident.OFFICIAL_PROTOCOL_RELATIVE,
            "protocol_sha256": incident.OFFICIAL_PROTOCOL_SHA256,
            "failure_source_path": incident.SOURCE_RELATIVE,
            "failure_source_sha256": failure["source_sha256"],
            "failure_protocol_path": incident.PROTOCOL_RELATIVE,
            "failure_protocol_sha256": failure["protocol_sha256"],
            "failure_report_path": incident.REPORT_RELATIVE,
            "failure_report_sha256": V2_FAILURE_SHA256,
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
    }


@contextmanager
def scoped_original(history: Mapping[str, Any]) -> Iterator[None]:
    saved = {
        "SCHEMA": original.SCHEMA,
        "SOURCE_PATH": original.SOURCE_PATH,
        "EVIDENCE_PATH": original.EVIDENCE_PATH,
        "validate_audits": original.validate_audits,
        "exclusive_evidence": original.exclusive_evidence,
    }

    def write(document: dict[str, Any]) -> None:
        require(
            document.get("schema") == SCHEMA
            and document.get("source_path") == SOURCE_RELATIVE
            and document.get("python") == "3.14.6",
            "the unchanged official runner produced a different controller result",
        )
        roles = document.get("roles")
        require(isinstance(roles, dict)
                and set(roles) == set(original.ROLE_MODULES),
                "the actual official run omitted a Python or candidate engine")
        for role, evidence in roles.items():
            require(
                isinstance(evidence, dict)
                and evidence.get("methods") == 146
                and evidence.get("passed") == 146
                and evidence.get("failed") == 0
                and evidence.get("skipped") == 0
                and evidence.get("crashes") == 0
                and evidence.get("timeouts") == 0
                and evidence.get("locale_caching_passed") is True
                and evidence.get("locale_compiled_passed") is True
                and isinstance(evidence.get("records"), list)
                and len(evidence["records"]) == 146
                and previous.REQUIRED_CORPUS_METHOD in {
                    record.get("test")
                    for record in evidence["records"]
                    if isinstance(record, dict)
                },
                "the actual original official test failed or skipped: " + role,
            )
        document["supersedes"] = copy.deepcopy(dict(history))
        document["official_scope"] = {
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
        saved["exclusive_evidence"](document)

    original.SCHEMA = SCHEMA
    original.SOURCE_PATH = SOURCE_RELATIVE
    original.EVIDENCE_PATH = EVIDENCE_PATH
    original.validate_audits = validate_v7_audits
    original.exclusive_evidence = write
    try:
        yield
    finally:
        for key, value in saved.items():
            setattr(original, key, value)


def run_audit() -> dict[str, Any]:
    original.verify_runtime()
    require(not previous._candidate_modules(),
            "the official controller cannot preload any native matching engine")
    selected = pins()
    destination(REPORT_RELATIVE)
    require(not EVIDENCE_PATH.exists() and not EVIDENCE_PATH.is_symlink(),
            "the exclusively created V3 official result already exists")
    history = validate_history()
    for path, expected in (
        (V7_BASE_SOURCE_RELATIVE, selected["base_source"]),
        (V7_STRICT_SOURCE_RELATIVE, selected["strict_source"]),
        (V7_BASE_REPORT_RELATIVE, selected["base_report"]),
        (V7_STRICT_REPORT_RELATIVE, selected["strict_report"]),
    ):
        current = original.checked_repo_path(path)
        require(original.sha256_path(current) == expected,
                "a genuinely passing V7 controller or report changed: " + path)
    source = original.read_json(original.checked_repo_path(V7_BASE_REPORT_RELATIVE))
    strict = original.read_json(original.checked_repo_path(V7_STRICT_REPORT_RELATIVE))
    sources, binaries = validate_v7_audits(
        source, strict,
        source_relative=V7_BASE_REPORT_RELATIVE,
        strict_relative=V7_STRICT_REPORT_RELATIVE,
        source_digest=selected["base_report"],
    )
    original.verify_production_fingerprints(sources, binaries)
    require(not previous._candidate_modules(),
            "an actual candidate escaped its required subprocess")
    with scoped_original(history):
        report = original.run_audit(V7_BASE_REPORT_RELATIVE, V7_STRICT_REPORT_RELATIVE)
    require(report.get("schema") == SCHEMA
            and report.get("source_path") == SOURCE_RELATIVE
            and report.get("supersedes") == history,
            "the complete fresh official result was not exclusively preserved")
    require(not previous._candidate_modules(),
            "the actual official run loaded an engine into its controller")
    return report


def synthetic_v7() -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    old_pins, source, strict = previous._synthetic_documents()
    synthetic = {
        key: hashlib.sha256(("official-v3:" + key).encode("ascii")).hexdigest()
        for key in ("base_source", "base_report", "strict_source", "strict_report")
    }
    source = copy.deepcopy(source)
    strict = copy.deepcopy(strict)
    source.update({
        "schema": V7_BASE_SCHEMA,
        "postfinal_schema": V7_BASE_SCHEMA,
        "audit_source_path": V7_BASE_SOURCE_RELATIVE,
        "audit_source_sha256": synthetic["base_source"],
        "previous_v6_report_historical": True,
        "previous_v6_strict_report_historical": True,
        "official_v2_source_path": previous.SOURCE_RELATIVE,
        "official_v2_source_sha256": incident.OFFICIAL_SOURCE_SHA256,
        "official_v2_protocol_path": incident.OFFICIAL_PROTOCOL_RELATIVE,
        "official_v2_protocol_sha256": incident.OFFICIAL_PROTOCOL_SHA256,
        "official_v2_rust_failure_path": incident.REPORT_RELATIVE,
        "official_v2_rust_failure_sha256": V2_FAILURE_SHA256,
        "official_v2_rust_failure_historical": True,
        "verified_match_repr_checks": 6,
        "match_repr_checks_per_family": 2,
    })
    source_workers: dict[str, Any] = {}
    strict_workers: dict[str, Any] = {}
    for family in CORE_FAMILIES:
        bridge = OWNED_BRIDGES[family]
        native = source["native_sha256_by_family"][family]
        base_owner = source["public_type_ownership"][family]
        guard = copy.deepcopy(base_owner["guard"])
        rows: list[dict[str, Any]] = []
        for kind, pattern, subject, matched in MATCH_CASES:
            expected = (
                "<" + bridge + ".Match object; span=(1, 12), match="
                + repr(matched) + ">"
            )
            rows.append({
                "id": family + ":match-repr:" + kind,
                "kind": kind,
                "span": [1, 12],
                "pattern_representation": repr(pattern),
                "subject_representation": repr(subject),
                "matched_representation": repr(matched),
                "match_module": bridge,
                "match_type_module": bridge,
                "match_qualified_name": "Match",
                "match_type_qualified_name": "Match",
                "actual_repr": expected,
                "observed_repr": expected,
                "expected_repr": expected,
                "native_type_identity": True,
                "genuine_matching_executed": True,
                "passed": True,
            })
        source_workers[family] = {
            "schema": V7_BASE_SCHEMA + "-match-repr-worker",
            "status": "PASS", "result": "PASS", "passed": True,
            "family": family,
            "candidate_module": "candidates." + family + "_candidate",
            "native_bridge_module": bridge,
            "native_binary_sha256": native,
            "match_repr_checks": 2,
            "genuine_matching_executed": True,
            "external_regex_packages": 0,
            "benchmark_or_timing_executed": False,
            "fixture_accessed": False,
            "guard": copy.deepcopy(guard),
            "records": copy.deepcopy(rows),
        }
        old_owner = strict["public_type_ownership"][family]
        strict_workers[family] = {
            **copy.deepcopy(old_owner),
            "schema": "rebar-postfinal-no-delegation-public-owner-worker-v7",
            "match_representation_check_count": 2,
            "match_repr_checks": 2,
            "genuine_matching_executed": True,
            "match_representation_checks": copy.deepcopy(rows),
        }
    source["public_match_repr"] = source_workers
    strict.update({
        "schema": V7_STRICT_SCHEMA,
        "postfinal_schema": V7_STRICT_SCHEMA,
        "audit_source_path": V7_STRICT_SOURCE_RELATIVE,
        "audit_source_sha256": synthetic["strict_source"],
        "base_audit_source_path": V7_BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": synthetic["base_source"],
        "base_audit_report_path": V7_BASE_REPORT_RELATIVE,
        "base_audit_report_sha256": synthetic["base_report"],
        "base_audit_postfinal_schema": V7_BASE_SCHEMA,
        "previous_v6_report_historical": True,
        "previous_v6_source_report_historical": True,
        "official_v2_failure_preserved": True,
        "official_v2_failure_qualifies_current_engines": False,
        "public_type_ownership": strict_workers,
        "public_match_repr": copy.deepcopy(source_workers),
        "strict_public_match_repr": copy.deepcopy(strict_workers),
        "verified_match_repr_checks": 6,
        "scope": {
            **strict["scope"],
            "fresh_v7_source_report_only": True,
            "actual_string_and_bytes_match_repr_verified": True,
            "actual_official_v2_rust_failure_preserved": True,
        },
    })
    del old_pins
    return synthetic, source, strict


def self_test() -> dict[str, Any]:
    original.verify_runtime()
    require(not previous._candidate_modules(),
            "the official V3 synthetic controls cannot preload a candidate")
    effects = previous._BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, value: Any) -> None:
        require(not any(item["name"] == name for item in checks),
                "an official V3 poison check was duplicated")
        checks.append({"name": name, "passed": bool(value)})

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (AssertionError, KeyError, TypeError, ValueError, OSError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited = previous.self_test()
        check("preserve-all-113-official-v2-and-73-original-controls",
              inherited.get("status") == "PASS"
              and inherited.get("passed") is True
              and inherited.get("check_count", 0) >= 113
              and inherited.get("inherited_v1_control_count", 0) >= 73
              and inherited.get("candidate_imports") == 0
              and inherited.get("files_read") == 0
              and inherited.get("subprocesses") == 0
              and inherited.get("clock_samples") == 0)
        synthetic, source, strict = synthetic_v7()

        def inspect(left: dict[str, Any], right: dict[str, Any],
                    **changes: Any) -> Any:
            arguments: dict[str, Any] = {
                "source_relative": V7_BASE_REPORT_RELATIVE,
                "strict_relative": V7_STRICT_REPORT_RELATIVE,
                "source_digest": synthetic["base_report"],
                "_synthetic_pins": synthetic,
            }
            arguments.update(changes)
            return validate_v7_audits(left, right, **arguments)

        sources, native = inspect(source, strict)
        check("accept-all-twelve-repaired-owned-sources-and-five-native-engines",
              len(sources) == 12 and len(native) == 5)
        check("pin-only-actual-published-v7-source",
              V7_BASE_SOURCE_SHA256
              == "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487")
        all_pinned = all(
            original.is_sha256(value)
            for value in (
                V7_BASE_SOURCE_SHA256, V7_BASE_REPORT_SHA256,
                V7_STRICT_SOURCE_SHA256, V7_STRICT_REPORT_SHA256,
            )
        )
        if all_pinned:
            check("accept-only-four-genuine-root-pinned-v7-proofs",
                  len(pins()) == 4)
        else:
            reject("fail-closed-until-all-four-v7-proofs-are-actually-published",
                   pins)
        for name in synthetic:
            for label, poison in (("missing", None), ("invalid", "bad")):
                changed = dict(synthetic)
                changed[name] = poison
                reject("reject-" + name + "-" + label,
                       lambda changed=changed: pins(changed))
        duplicate = dict(synthetic)
        duplicate["strict_report"] = duplicate["base_report"]
        reject("reject-shared-source-or-report-hash", lambda: pins(duplicate))

        check("accept-only-a-new-exclusive-v3-official-report",
              destination(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, path in (
            ("old-v1-official-report", original.EVIDENCE_PATH.relative_to(ROOT).as_posix()),
            ("falsified-v2-official-report", previous.REPORT_RELATIVE),
            ("preserved-v2-rust-failure", incident.REPORT_RELATIVE),
            ("v7-source-report", V7_BASE_REPORT_RELATIVE),
            ("v7-strict-report", V7_STRICT_REPORT_RELATIVE),
            ("absolute-report", "/" + REPORT_RELATIVE),
            ("traversing-report", "oracle/cpython-3.14.6/evidence/../fake.json"),
            ("foreign-report", "oracle/cpython-3.14.6/evidence/fake.json"),
            ("backslash-report", "oracle\\cpython-3.14.6\\evidence\\fake.json"),
            ("nul-report", REPORT_RELATIVE + "\x00"),
            ("nontext-report", 7),
        ):
            reject("reject-" + label, lambda path=path: destination(path))

        for label, owner, key, poison in (
            ("source-schema", "source", "schema", previous.V6_BASE_SCHEMA),
            ("source-failure", "source", "status", "FAIL"),
            ("source-controller", "source", "audit_source_path", previous.SOURCE_RELATIVE),
            ("source-controller-sha", "source", "audit_source_sha256", synthetic["strict_source"]),
            ("source-missing-pickle", "source", "standard_pickle_checks", 47),
            ("source-missing-repr", "source", "verified_match_repr_checks", 5),
            ("source-hidden-v2-failure", "source", "official_v2_rust_failure_historical", False),
            ("source-false-v2-failure-hash", "source", "official_v2_rust_failure_sha256", "0" * 64),
            ("strict-schema", "strict", "schema", previous.V6_STRICT_SCHEMA),
            ("strict-failure", "strict", "status", "FAIL"),
            ("strict-controller", "strict", "audit_source_path", previous.SOURCE_RELATIVE),
            ("strict-controller-sha", "strict", "audit_source_sha256", synthetic["base_source"]),
            ("strict-base-path", "strict", "base_audit_report_path", previous.V6_BASE_REPORT_RELATIVE),
            ("strict-base-sha", "strict", "base_audit_report_sha256", synthetic["strict_report"]),
            ("strict-missing-source", "strict", "qualified_source_fingerprints", {}),
            ("strict-missing-native", "strict", "native_elf_fingerprints", {}),
            ("strict-hidden-v2-failure", "strict", "official_v2_failure_preserved", False),
            ("strict-false-prior-qualification", "strict",
             "official_v2_failure_qualifies_current_engines", True),
            ("strict-missing-pickle", "strict", "verified_standard_pickle_count", 47),
            ("strict-missing-repr", "strict", "verified_match_repr_checks", 5),
        ):
            left, right = copy.deepcopy(source), copy.deepcopy(strict)
            (left if owner == "source" else right)[key] = poison
            reject("reject-" + label,
                   lambda left=left, right=right: inspect(left, right))
        for family in CORE_FAMILIES:
            for owner in ("source", "strict"):
                left, right = copy.deepcopy(source), copy.deepcopy(strict)
                target = left if owner == "source" else right
                target["families"][family]["passed"] = False
                reject("reject-failed-" + owner + "-native-family-" + family,
                       lambda left=left, right=right: inspect(left, right))
                left, right = copy.deepcopy(source), copy.deepcopy(strict)
                target = left if owner == "source" else right
                del target["public_type_ownership"][family]
                reject("reject-missing-" + owner + "-owned-type-" + family,
                       lambda left=left, right=right: inspect(left, right))
            for label, field, poison in (
                ("old-hardcoded-python-repr", "actual_repr",
                 "<re.Match object; span=(1, 12), match='abracadabra'>"),
                ("foreign-match-owner", "match_type_module", "re"),
                ("false-match-span", "span", [0, 11]),
                ("failed-actual-match", "passed", False),
                ("mocked-matching", "genuine_matching_executed", False),
            ):
                left, right = copy.deepcopy(source), copy.deepcopy(strict)
                left["public_match_repr"][family]["records"][0][field] = poison
                reject("reject-" + family + "-" + label,
                       lambda left=left, right=right: inspect(left, right))
            left, right = copy.deepcopy(source), copy.deepcopy(strict)
            right["public_type_ownership"][family]["match_representation_checks"].pop()
            reject("reject-missing-strict-official-bytes-repr-" + family,
                   lambda left=left, right=right: inspect(left, right))
            left, right = copy.deepcopy(source), copy.deepcopy(strict)
            right["public_type_ownership"][family]["guard"]["stdlib_re_blocked"] = False
            reject("reject-strict-stdlib-regex-delegation-" + family,
                   lambda left=left, right=right: inspect(left, right))
        for key, poison in (
            ("fresh_v7_source_report_only", False),
            ("actual_string_and_bytes_match_repr_verified", False),
            ("actual_official_v2_rust_failure_preserved", False),
            ("closed_owned_source_graph", False),
            ("all_five_native_loader_aliases_blocked", False),
            ("enum_json_decoder_registry_bypass_blocked", False),
            ("benchmark_or_timing_executed", True),
            ("holdout_or_case_fixture_access", True),
        ):
            changed = copy.deepcopy(strict)
            changed["scope"][key] = poison
            reject("reject-weakened-native-independence-" + key,
                   lambda changed=changed: inspect(source, changed))
        reject("reject-stale-version-six-source-report",
               lambda: inspect(source, strict,
                               source_relative=previous.V6_BASE_REPORT_RELATIVE))
        reject("reject-stale-version-six-strict-report",
               lambda: inspect(source, strict,
                               strict_relative=previous.V6_STRICT_REPORT_RELATIVE))
        check("preserve-original-six-public-and-two-private-waivers",
              len(original.METHOD_WAIVERS) == 6
              and len(original.CLASS_WAIVERS) == 2)
        check("preserve-two-genuine-upstream-locale-methods",
              original.REQUIRED_LOCALE_TESTS == frozenset({
                  "ReTests.test_locale_caching", "ReTests.test_locale_compiled",
              }))
        check("preserve-the-real-403-pattern-official-corpus",
              previous.REQUIRED_CORPUS_METHOD == "ExternalTests.test_re_tests")
        check("never-import-any-candidate", not previous._candidate_modules())
    for name, kind in (
        ("zero-files-read-or-written", "files"),
        ("zero-official-or-candidate-processes", "processes"),
        ("zero-clock-samples", "clocks"),
        ("zero-production-entropy", "entropy"),
    ):
        check(name, effects.counts[kind] == 0)
    failed = [item["name"] for item in checks if item["passed"] is not True]
    require(not failed, "an official V3 safety control failed: " + ", ".join(failed))
    require(not previous._candidate_modules(),
            "a candidate escaped into the official self-test")
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS", "result": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "inherited_v2_control_count": inherited["check_count"],
        "inherited_v1_control_count": inherited["inherited_v1_control_count"],
        "candidate_imports": 0, "candidate_processes": 0,
        "files_read": effects.counts["files"], "files_written": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "locales_compiled": 0, "official_tests_executed": 0,
        "production_cases_materialized": 0, "report_written": False,
        "v7_base_source_pinned": V7_BASE_SOURCE_SHA256 is not None,
        "v7_base_report_pinned": V7_BASE_REPORT_SHA256 is not None,
        "v7_strict_source_pinned": V7_STRICT_SOURCE_SHA256 is not None,
        "v7_strict_report_pinned": V7_STRICT_REPORT_SHA256 is not None,
        "holdout_accessed": False, "timing_performed": False,
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true",
                      help="run candidate-free, blocked synthetic safety controls")
    mode.add_argument("--audit", action="store_true",
                      help="exclusively run all four genuine original CPython suites")
    args = parser.parse_args(arguments)
    try:
        report = self_test() if args.self_test else run_audit()
    except (AssertionError, OSError, subprocess.SubprocessError,
            UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"schema": SCHEMA, "status": "FAIL", "error": str(error)},
                         ensure_ascii=True, sort_keys=True), file=sys.stderr)
        return 1
    if args.self_test:
        print(json.dumps(report, sort_keys=True, ensure_ascii=True))
    else:
        print(json.dumps({
            "schema": SCHEMA, "status": "PASS", "evidence": REPORT_RELATIVE,
            "roles": {
                family: {
                    key: value for key, value in result.items() if key != "records"
                }
                for family, result in report["roles"].items()
            },
            "actual_official_v2_failure_preserved": True,
            "performance": "NOT MEASURED",
        }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
