#!/usr/bin/env python3
"""Bind the unchanged public Python oracle to genuinely locale-qualified engines."""

from __future__ import annotations

import hashlib
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator


WRAPPER = Path(__file__).resolve()
ROOT = WRAPPER.parent.parent
STAGE05_SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage05.py"
STAGE05_SOURCE_SHA256 = (
    "bcedc268d58cab828b82680f7471c2ced4f8a9aa3638271e71f8f4f146e4475f"
)
STAGE05_REPORT_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v5-all.json"
)
STAGE05_REPORT_SHA256 = (
    "d5b06b914d63f1b89cfd78c2f72c45f432755ce6895b6194e8e7d3fee9c0c2ca"
)
BASE_AUDIT_SCHEMA = "rebar-postfinal-from-scratch-audit-v5"
BASE_AUDIT_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v5.py"
BASE_AUDIT_SOURCE_SHA256 = (
    "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843"
)
BASE_AUDIT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"
)
BASE_AUDIT_REPORT_SHA256 = (
    "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
)
STRICT_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v5"
STRICT_AUDIT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v5.py"
STRICT_AUDIT_SOURCE_SHA256 = (
    "18a04023659e386780d6e9cd6b90065553254c18f2fe54ae78c37acbc468a7b6"
)
STRICT_AUDIT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json"
)
STRICT_AUDIT_REPORT_SHA256 = (
    "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
)
LOCALE_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v1.py"
LOCALE_SOURCE_SHA256 = (
    "b87bbdcddef2d19a462e8c4b37bd159f6c3a30ea9b4fe5d9471eff1f51fbcb55"
)
LOCALE_REPORT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json"
)
LOCALE_REPORT_SHA256 = (
    "bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621"
)
OUTPUT_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v6-all.json"
)
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
OUTPUT_CANDIDATES = frozenset({"rust", "vm", "zig", "all"})

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v1 as official_locale
from tools import postfinal_from_scratch_audit_v5 as base_v5
from tools import postfinal_no_delegation_audit_v5 as strict_v5
from tools import python_re_universal_public_oracle_stage05 as previous


frozen = previous.frozen
frozen.candidate_free()
frozen.require(
    Path(previous.__file__).resolve() == ROOT / STAGE05_SOURCE_RELATIVE
    and Path(base_v5.__file__).resolve() == ROOT / BASE_AUDIT_SOURCE_RELATIVE
    and Path(strict_v5.__file__).resolve() == ROOT / STRICT_AUDIT_SOURCE_RELATIVE
    and Path(official_locale.__file__).resolve() == ROOT / LOCALE_SOURCE_RELATIVE,
    "stage-06 must import the exact preserved public, V5, and locale controllers",
)
frozen.require(
    frozen.SCHEMA == "rebar-python-re-universal-public-oracle-v1"
    and frozen.SEED == 2026072417
    and frozen.SEED_DOMAIN == "rebar/python-re/universal-public/v1"
    and frozen.EXPECTED_CASES == 8_192
    and frozen.EXAMPLES_PER_STRATUM == 32
    and frozen.OBSERVATIONS_PER_CASE == 48
    and frozen.EXPECTED_OBSERVATIONS == 393_216
    and len(frozen.GRAMMAR_FAMILIES) == 16
    and len(frozen.INPUT_STRATA) == 16
    and frozenset(frozen.CANDIDATES) == frozenset(REQUIRED_CANDIDATES)
    and base_v5.SCHEMA == BASE_AUDIT_SCHEMA
    and strict_v5.SCHEMA == STRICT_AUDIT_SCHEMA
    and official_locale.SCHEMA == "rebar-postfinal-cpython-public-locale-v1",
    "stage-06 cannot change the frozen public cases, engines, or genuine locale proof",
)

SYNTHETIC_INTERPRETER = previous.SYNTHETIC_INTERPRETER
SYNTHETIC_BASE_SOURCE_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage06/synthetic-v5-base-source"
).hexdigest()
SYNTHETIC_BASE_REPORT_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage06/synthetic-v5-base-report"
).hexdigest()
SYNTHETIC_STRICT_SOURCE_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage06/synthetic-v5-strict-source"
).hexdigest()
SYNTHETIC_STRICT_REPORT_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage06/synthetic-v5-strict-report"
).hexdigest()


def stage06_default_output(candidate: str) -> Path:
    frozen.require(
        candidate in OUTPUT_CANDIDATES,
        "stage-06 requires an exact independently audited output identity",
    )
    return (
        frozen.EVIDENCE_ROOT
        / f"python-re-universal-public-oracle-v6-{candidate}.json"
    )


def stage06_require_all(candidate: str) -> None:
    frozen.require(
        candidate == "all",
        "stage-06 production must qualify all three independent native engines",
    )


def stage06_run_gate(candidate: str, output_argument: Path | None) -> int:
    stage06_require_all(candidate)
    return previous._immutable_run_gate(candidate, output_argument)


def stage06_build_cases() -> list[dict[str, Any]]:
    cases = previous.stage05_build_cases()
    frozen.require(
        len(cases) == 8_192
        and frozen.value_digest(cases) == previous.FROZEN_CASE_SHA256,
        "stage-06 changed the frozen 16-by-16-by-32 public case descriptors",
    )
    return cases


def stage06_synthetic_audit(
    selected: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, dict[str, str]], dict[str, dict[str, str]], str]:
    document, sources, binaries, interpreter = previous.stage05_synthetic_audit(
        selected
    )
    frozen.require(
        selected == REQUIRED_CANDIDATES and interpreter == SYNTHETIC_INTERPRETER,
        "stage-06 requires the exact three-engine in-memory public audit",
    )
    document.update(
        {
            "postfinal_schema": BASE_AUDIT_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "audit_source_path": BASE_AUDIT_SOURCE_RELATIVE,
            "audit_source_sha256": SYNTHETIC_BASE_SOURCE_SHA256,
            "previous_v4_audit_source_path": base_v5.previous.SOURCE_RELATIVE,
            "previous_v4_audit_source_sha256": base_v5.PREVIOUS_SOURCE_SHA256,
            "previous_v4_audit_report_path": base_v5.previous.REPORT_RELATIVE,
            "previous_v4_audit_report_sha256": base_v5.PREVIOUS_REPORT_SHA256,
            "previous_v4_postfinal_schema": base_v5.previous.SCHEMA,
            "previous_v4_report_historical": True,
            "verified_core_family_count": 3,
            "verified_distinct_pipeline_count": 4,
            "v5_allowed_locale_libc_primitives": sorted(base_v5.LOCALE_SYMBOLS),
            "v5_owned_locale_sources": dict(base_v5.OWNED_LOCALE_SOURCES),
        }
    )
    return document, sources, binaries, interpreter


def stage06_validate_audit_document(
    document: Any,
    selected: tuple[str, ...],
    actual_sources: dict[str, dict[str, str]],
    actual_binaries: dict[str, dict[str, str]],
    interpreter: str,
) -> None:
    frozen.require(
        isinstance(document, dict) and selected == REQUIRED_CANDIDATES,
        "stage-06 requires a complete, three-family V5 source audit",
    )
    exact: dict[str, Any] = {
        "schema_version": 1,
        "audit": "bounded-from-scratch-engine-provenance",
        "postfinal_schema": BASE_AUDIT_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": BASE_AUDIT_SOURCE_RELATIVE,
        "previous_v4_audit_source_path": base_v5.previous.SOURCE_RELATIVE,
        "previous_v4_audit_source_sha256": base_v5.PREVIOUS_SOURCE_SHA256,
        "previous_v4_audit_report_path": base_v5.previous.REPORT_RELATIVE,
        "previous_v4_audit_report_sha256": base_v5.PREVIOUS_REPORT_SHA256,
        "previous_v4_postfinal_schema": base_v5.previous.SCHEMA,
        "previous_v4_report_historical": True,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
    }
    for field, value in exact.items():
        frozen.require(
            document.get(field) == value
            and type(document.get(field)) is type(value),
            f"the stage-06 V5 base audit changed {field}",
        )
    expected_source = (
        SYNTHETIC_BASE_SOURCE_SHA256
        if interpreter == SYNTHETIC_INTERPRETER
        else BASE_AUDIT_SOURCE_SHA256
    )
    frozen.require(
        document.get("audit_source_sha256") == expected_source
        and document.get("v5_allowed_locale_libc_primitives")
        == sorted(base_v5.LOCALE_SYMBOLS)
        and document.get("v5_owned_locale_sources")
        == dict(base_v5.OWNED_LOCALE_SOURCES),
        "stage-06 lost the exact source fingerprint or widened locale delegation",
    )
    previous._immutable_validate_audit_document(
        document, selected, actual_sources, actual_binaries, interpreter
    )
    if interpreter != SYNTHETIC_INTERPRETER:
        try:
            base_v5.validate_v5_report(
                document, label="the actual complete stage-06 V5 source audit"
            )
        except (AssertionError, base_v5.AuditV5Error, TypeError, ValueError) as error:
            raise frozen.OracleIntegrityError(
                "stage-06 rejected the actual complete V5 source audit"
            ) from error


def stage06_synthetic_strict_audit(
    sources: dict[str, dict[str, str]],
    binaries: dict[str, dict[str, str]],
) -> dict[str, Any]:
    document = previous.stage05_synthetic_strict_audit(sources, binaries)
    document.update(
        {
            "schema": STRICT_AUDIT_SCHEMA,
            "postfinal_schema": STRICT_AUDIT_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "audit_source_path": STRICT_AUDIT_SOURCE_RELATIVE,
            "audit_source_sha256": SYNTHETIC_STRICT_SOURCE_SHA256,
            "base_audit_postfinal_schema": BASE_AUDIT_SCHEMA,
            "base_audit_report_path": BASE_AUDIT_REPORT_RELATIVE,
            "base_audit_report_sha256": SYNTHETIC_BASE_REPORT_SHA256,
            "base_audit_source_path": BASE_AUDIT_SOURCE_RELATIVE,
            "base_audit_source_sha256": SYNTHETIC_BASE_SOURCE_SHA256,
            "previous_v4_audit_source_path": strict_v5.previous.SOURCE_RELATIVE,
            "previous_v4_audit_source_sha256": strict_v5.PREVIOUS_SOURCE_SHA256,
            "previous_v4_source_report_path": base_v5.previous.REPORT_RELATIVE,
            "previous_v4_source_report_sha256": base_v5.PREVIOUS_REPORT_SHA256,
            "previous_v4_source_report_historical": True,
            "previous_v4_strict_report_created": False,
            "verified_core_family_count": 3,
            "verified_distinct_pipeline_count": 4,
            "v5_allowed_locale_libc_primitives": sorted(base_v5.LOCALE_SYMBOLS),
            "v5_owned_locale_sources": dict(base_v5.OWNED_LOCALE_SOURCES),
            "families": {
                name: {"passed": True}
                for name in ("ast", "rust", "vm", "zig")
            },
            "postfinal_wrapper_self_test": {
                "schema": STRICT_AUDIT_SCHEMA + "-self-test",
                "status": "PASS",
                "result": "PASS",
                "passed": True,
                "check_count": 676,
                "failed": [],
                "fixture_storage": "in-memory only",
                "candidate_imported": False,
                "candidate_imports": 0,
                "file_reads": 0,
                "file_writes": 0,
                "subprocesses": 0,
                "clock_samples": 0,
                "production_entropy_drawn": False,
                "holdout_or_case_fixture_access": False,
                "benchmark_or_timing_executed": False,
                "production_cases_materialized": 0,
                "report_written": False,
            },
        }
    )
    document["scope"] = {
        **document["scope"],
        "base_v5_report_only": True,
        "production_report_path": STRICT_AUDIT_REPORT_RELATIVE,
        "immutable_v1_reports_mutated": False,
        "immutable_v2_reports_mutated": False,
        "immutable_v3_reports_mutated": False,
        "immutable_v4_reports_mutated": False,
        "previous_v4_source_report_historical": True,
    }
    return document


def stage06_validate_strict_audit(
    document: Any,
    *,
    base_report_sha256: str,
    base_source_sha256: str,
    strict_source_sha256: str,
    sources: dict[str, dict[str, str]],
    binaries: dict[str, dict[str, str]],
) -> None:
    frozen.require(isinstance(document, dict), "the V5 no-delegation proof is absent")
    expected: dict[str, Any] = {
        "schema": STRICT_AUDIT_SCHEMA,
        "postfinal_schema": STRICT_AUDIT_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": STRICT_AUDIT_SOURCE_RELATIVE,
        "audit_source_sha256": strict_source_sha256,
        "base_audit_postfinal_schema": BASE_AUDIT_SCHEMA,
        "base_audit_report_path": BASE_AUDIT_REPORT_RELATIVE,
        "base_audit_report_sha256": base_report_sha256,
        "base_audit_source_path": BASE_AUDIT_SOURCE_RELATIVE,
        "base_audit_source_sha256": base_source_sha256,
        "inherited_control_count": 76,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "previous_v4_audit_source_path": strict_v5.previous.SOURCE_RELATIVE,
        "previous_v4_audit_source_sha256": strict_v5.PREVIOUS_SOURCE_SHA256,
        "previous_v4_source_report_path": base_v5.previous.REPORT_RELATIVE,
        "previous_v4_source_report_sha256": base_v5.PREVIOUS_REPORT_SHA256,
        "previous_v4_source_report_historical": True,
        "previous_v4_strict_report_created": False,
    }
    for field, value in expected.items():
        frozen.require(
            document.get(field) == value
            and type(document.get(field)) is type(value),
            f"the stage-06 V5 no-delegation proof changed {field}",
        )
    frozen.require(
        document.get("qualified_source_fingerprints")
        == previous._flatten_source_fingerprints(sources)
        and document.get("native_elf_fingerprints")
        == previous._flatten_native_fingerprints(binaries),
        "the V5 strict proof lost an actual owned source or native engine",
    )
    families = document.get("families")
    frozen.require(
        isinstance(families, dict)
        and set(families) == {"ast", "rust", "vm", "zig"}
        and all(
            isinstance(families[name], dict)
            and families[name].get("passed") is True
            for name in ("rust", "vm", "zig")
        )
        and document.get("v5_allowed_locale_libc_primitives")
        == sorted(base_v5.LOCALE_SYMBOLS)
        and document.get("v5_owned_locale_sources")
        == dict(base_v5.OWNED_LOCALE_SOURCES),
        "the V5 strict proof changed independent families or locale primitives",
    )
    controls = document.get("self_test")
    frozen.require(
        isinstance(controls, dict)
        and controls.get("check_count") == 32
        and controls.get("passed") is True
        and controls.get("failed") == []
        and controls.get("fixture_storage") == "in-memory only"
        and controls.get("candidate_imported") is False
        and controls.get("benchmark_or_timing_executed") is False
        and controls.get("holdout_or_case_fixture_access") is False,
        "the V5 strict proof weakened the exact immutable 32-control worker",
    )
    wrapper = document.get("postfinal_wrapper_self_test")
    frozen.require(
        isinstance(wrapper, dict)
        and wrapper.get("schema") == STRICT_AUDIT_SCHEMA + "-self-test"
        and wrapper.get("status") == "PASS"
        and wrapper.get("result") == "PASS"
        and wrapper.get("passed") is True
        and type(wrapper.get("check_count")) is int
        and wrapper["check_count"] >= 676
        and wrapper.get("failed") == []
        and wrapper.get("fixture_storage") == "in-memory only"
        and wrapper.get("candidate_imported") is False
        and wrapper.get("candidate_imports") == 0
        and wrapper.get("file_reads") == 0
        and wrapper.get("file_writes") == 0
        and wrapper.get("subprocesses") == 0
        and wrapper.get("clock_samples") == 0
        and wrapper.get("production_entropy_drawn") is False
        and wrapper.get("benchmark_or_timing_executed") is False
        and wrapper.get("holdout_or_case_fixture_access") is False
        and wrapper.get("production_cases_materialized") == 0
        and wrapper.get("report_written") is False,
        "the V5 strict proof lost its 676 candidate-free poison controls",
    )
    scope = document.get("scope")
    frozen.require(
        isinstance(scope, dict)
        and scope.get("explicit_source_paths_only") is True
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("immutable_v1_source_preserved") is True
        and scope.get("immutable_v1_reports_mutated") is False
        and scope.get("immutable_v2_reports_mutated") is False
        and scope.get("immutable_v3_reports_mutated") is False
        and scope.get("immutable_v4_reports_mutated") is False
        and scope.get("previous_v4_source_report_historical") is True
        and scope.get("base_v5_report_only") is True
        and scope.get("production_report_path") == STRICT_AUDIT_REPORT_RELATIVE
        and scope.get("candidate_imports") == "isolated guarded subprocesses only"
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the V5 strict proof weakened isolated native execution or evidence ownership",
    )


def _locale_selected_digest(records: list[dict[str, Any]]) -> str:
    names = sorted(record["test"] for record in records)
    return hashlib.sha256(official_locale.canonical(names)).hexdigest()


def stage06_validate_locale_proof(
    document: Any,
    *,
    base_report_sha256: str,
    base_source_sha256: str,
    strict_report_sha256: str,
    strict_source_sha256: str,
    sources: dict[str, dict[str, str]],
    binaries: dict[str, dict[str, str]],
    selected_method_sha256: str = official_locale.SELECTED_METHOD_SHA256,
) -> None:
    frozen.require(isinstance(document, dict), "the genuine four-role locale proof is missing")
    exact = {
        "schema": official_locale.SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "goal_sha256": official_locale.GOAL_SHA256,
        "source_path": LOCALE_SOURCE_RELATIVE,
        "source_sha256": LOCALE_SOURCE_SHA256,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    for field, value in exact.items():
        frozen.require(
            document.get(field) == value
            and type(document.get(field)) is type(value),
            f"the genuine official locale proof changed {field}",
        )
    original = document.get("original_oracle")
    frozen.require(
        isinstance(original, dict)
        and original.get("manifest_path") == official_locale.ORIGINAL_MANIFEST_PATH
        and original.get("manifest_sha256") == official_locale.ORIGINAL_MANIFEST_SHA256
        and original.get("runner_path") == official_locale.ORIGINAL_RUNNER_PATH
        and original.get("runner_sha256") == official_locale.ORIGINAL_RUNNER_SHA256
        and original.get("source_sha256") == official_locale.SOURCE_HASHES
        and original.get("total_public_methods") == 152
        and original.get("selected_methods") == 146
        and original.get("selected_method_sha256") == selected_method_sha256
        and original.get("named_waivers") == official_locale.METHOD_WAIVERS
        and original.get("named_class_waivers") == official_locale.CLASS_WAIVERS
        and original.get("all_named_waivers")
        == official_locale.CLASS_WAIVERS | official_locale.METHOD_WAIVERS
        and original.get("corpus_cases") == 403,
        "the genuine locale proof changed official methods, sources, or private waivers",
    )
    audits = document.get("audits")
    expected_audits = {
        "from_scratch": {
            "path": BASE_AUDIT_REPORT_RELATIVE,
            "sha256": base_report_sha256,
            "postfinal_schema": BASE_AUDIT_SCHEMA,
            "source_path": BASE_AUDIT_SOURCE_RELATIVE,
            "source_sha256": base_source_sha256,
        },
        "no_delegation": {
            "path": STRICT_AUDIT_REPORT_RELATIVE,
            "sha256": strict_report_sha256,
            "postfinal_schema": STRICT_AUDIT_SCHEMA,
            "source_path": STRICT_AUDIT_SOURCE_RELATIVE,
            "source_sha256": strict_source_sha256,
        },
    }
    frozen.require(
        audits == expected_audits,
        "the genuine locale proof is not bound to both actual current V5 audits",
    )
    flat_sources = previous._flatten_source_fingerprints(sources)
    flat_natives = previous._flatten_native_fingerprints(binaries)
    frozen.require(
        set(flat_sources) == official_locale.SOURCE_PATHS
        and set(flat_natives) == set(official_locale.NATIVE_PATHS)
        and document.get("qualified_source_fingerprints") == flat_sources
        and document.get("native_elf_fingerprints") == flat_natives,
        "the genuine locale proof lost a current owned source or native mapping",
    )
    locales = document.get("locales")
    frozen.require(
        isinstance(locales, dict)
        and locales.get("private") is True
        and locales.get("genuine") is True
        and locales.get("holdout_accessed") is False
        and locales.get("timing_performed") is False
        and locales.get("performance") == "NOT MEASURED",
        "the official suite did not use genuine isolated, untimed locales",
    )
    for encoding, name in official_locale.LOCALE_NAMES.items():
        metadata = locales.get(encoding)
        frozen.require(
            isinstance(metadata, dict)
            and metadata.get("name") == name
            and official_locale.is_sha256(metadata.get("source_sha256"))
            and official_locale.is_sha256(metadata.get("charmap_sha256")),
            f"the genuine {encoding} locale input was omitted or poisoned",
        )
    reference = {
        "status": "PASS",
        "python": "3.14.6",
        "candidate_modules_loaded": False,
        "genuine_locales": True,
        "compiled_locale_switch": True,
        "holdout_accessed": False,
        "timing_performed": False,
    }
    frozen.require(
        document.get("locale_reference") == reference,
        "the genuine isolated Python locale self-reference failed",
    )
    roles = document.get("roles")
    frozen.require(
        isinstance(roles, dict) and set(roles) == set(official_locale.ROLE_MODULES),
        "the locale proof omitted Python or an independently owned native engine",
    )
    baseline_ids: frozenset[str] | None = None
    for role, module in official_locale.ROLE_MODULES.items():
        result = roles.get(role)
        frozen.require(
            isinstance(result, dict)
            and result.get("module") == module
            and result.get("methods") == 146
            and result.get("passed") == 146
            and result.get("skipped") == 0
            and result.get("failed") == 0
            and result.get("failures") == 0
            and result.get("errors") == 0
            and result.get("crashes") == 0
            and result.get("timeouts") == 0
            and result.get("locale_caching_passed") is True
            and result.get("locale_compiled_passed") is True
            and result.get("holdout_accessed") is False
            and result.get("timing_performed") is False
            and result.get("performance") == "NOT MEASURED"
            and isinstance(result.get("records"), list)
            and len(result["records"]) == 146,
            f"the official {role} role did not genuinely pass all 146 upstream methods",
        )
        adapted = {
            **result,
            "schema": "rebar-cpython-re-result-v1",
            "runner_sha256": official_locale.ORIGINAL_RUNNER_SHA256,
            "source_sha256": dict(official_locale.SOURCE_HASHES),
        }
        try:
            verified = official_locale.validate_role(
                adapted, module, expected_ids=baseline_ids
            )
        except (AssertionError, TypeError, ValueError, KeyError) as error:
            raise frozen.OracleIntegrityError(
                f"the official {role} locale method records are not genuine"
            ) from error
        identities = frozenset(record["test"] for record in verified["records"])
        if baseline_ids is None:
            baseline_ids = identities
            frozen.require(
                _locale_selected_digest(verified["records"])
                == selected_method_sha256,
                "the locale baseline substituted the frozen 146 upstream identities",
            )


def _read_public_document(
    relative: str,
    *,
    expected_sha256: str | None,
) -> tuple[dict[str, Any], str]:
    path = official_locale.checked_repo_path(relative)
    digest = official_locale.sha256_path(path, maximum=official_locale.MAX_JSON_BYTES)
    frozen.require(
        expected_sha256 is None or digest == expected_sha256,
        f"the authenticated stage-06 public proof changed: {relative}",
    )
    document = official_locale.read_json(path)
    frozen.require(
        official_locale.sha256_path(path, maximum=official_locale.MAX_JSON_BYTES)
        == digest,
        f"the authenticated stage-06 public proof changed during reading: {relative}",
    )
    return document, digest


def stage06_production_preflight() -> None:
    frozen.candidate_free()
    fingerprints = {
        STAGE05_SOURCE_RELATIVE: STAGE05_SOURCE_SHA256,
        BASE_AUDIT_SOURCE_RELATIVE: BASE_AUDIT_SOURCE_SHA256,
        STRICT_AUDIT_SOURCE_RELATIVE: STRICT_AUDIT_SOURCE_SHA256,
        LOCALE_SOURCE_RELATIVE: LOCALE_SOURCE_SHA256,
    }
    for relative, expected in fingerprints.items():
        path = official_locale.checked_repo_path(relative)
        frozen.require(
            official_locale.sha256_path(path, maximum=frozen.MAX_SOURCE_BYTES)
            == expected,
            f"the preserved stage-06 public controller changed: {relative}",
        )
    previous.stage05_validate_frozen_fingerprints(
        **previous.stage05_frozen_fingerprint_values()
    )
    historical, _digest = _read_public_document(
        STAGE05_REPORT_RELATIVE, expected_sha256=STAGE05_REPORT_SHA256
    )
    previous.stage05_validate_previous_report(historical)
    base_document, _base = _read_public_document(
        BASE_AUDIT_REPORT_RELATIVE, expected_sha256=BASE_AUDIT_REPORT_SHA256
    )
    try:
        base_v5.validate_v5_report(
            base_document, label="the complete live locale-aware V5 source audit"
        )
    except (AssertionError, base_v5.AuditV5Error, TypeError, ValueError) as error:
        raise frozen.OracleIntegrityError(
            "the actual current locale-aware V5 source audit failed"
        ) from error
    _read_public_document(
        STRICT_AUDIT_REPORT_RELATIVE, expected_sha256=STRICT_AUDIT_REPORT_SHA256
    )
    _read_public_document(
        LOCALE_REPORT_RELATIVE, expected_sha256=LOCALE_REPORT_SHA256
    )
    frozen.candidate_free()


def stage06_verified_provenance(selected: tuple[str, ...]) -> dict[str, Any]:
    stage06_require_all("all" if selected == REQUIRED_CANDIDATES else "partial")
    stage06_production_preflight()
    provenance = previous._immutable_verified_provenance(selected)
    frozen.require(
        provenance.get("audit_path") == BASE_AUDIT_REPORT_RELATIVE
        and provenance.get("audit_sha256") == BASE_AUDIT_REPORT_SHA256
        and provenance.get("oracle_source_path")
        == WRAPPER.relative_to(ROOT).as_posix(),
        "stage-06 did not bind its exact current public runner and V5 source audit",
    )
    sources = provenance.get("source_sha256")
    binaries = provenance.get("native_binary_sha256")
    frozen.require(
        isinstance(sources, dict) and isinstance(binaries, dict),
        "stage-06 omitted the owned source and live native-role fingerprints",
    )
    base, base_digest = _read_public_document(
        BASE_AUDIT_REPORT_RELATIVE, expected_sha256=BASE_AUDIT_REPORT_SHA256
    )
    strict, strict_digest = _read_public_document(
        STRICT_AUDIT_REPORT_RELATIVE, expected_sha256=STRICT_AUDIT_REPORT_SHA256
    )
    stage06_validate_strict_audit(
        strict,
        base_report_sha256=base_digest,
        base_source_sha256=BASE_AUDIT_SOURCE_SHA256,
        strict_source_sha256=STRICT_AUDIT_SOURCE_SHA256,
        sources=sources,
        binaries=binaries,
    )
    try:
        locale_sources, locale_natives = official_locale.validate_audits(
            base,
            strict,
            source_relative=BASE_AUDIT_REPORT_RELATIVE,
            strict_relative=STRICT_AUDIT_REPORT_RELATIVE,
            source_digest=base_digest,
        )
    except (AssertionError, TypeError, ValueError, KeyError) as error:
        raise frozen.OracleIntegrityError(
            "the genuine locale producer rejected the actual paired V5 audits"
        ) from error
    frozen.require(
        locale_sources == previous._flatten_source_fingerprints(sources)
        and locale_natives == previous._flatten_native_fingerprints(binaries),
        "the genuine locale suite and public oracle selected different live engines",
    )
    locale_report, locale_digest = _read_public_document(
        LOCALE_REPORT_RELATIVE, expected_sha256=LOCALE_REPORT_SHA256
    )
    stage06_validate_locale_proof(
        locale_report,
        base_report_sha256=base_digest,
        base_source_sha256=BASE_AUDIT_SOURCE_SHA256,
        strict_report_sha256=strict_digest,
        strict_source_sha256=STRICT_AUDIT_SOURCE_SHA256,
        sources=sources,
        binaries=binaries,
    )
    frozen.candidate_free()
    return {
        **provenance,
        "postfinal_audit_schema": BASE_AUDIT_SCHEMA,
        "postfinal_audit_source_path": BASE_AUDIT_SOURCE_RELATIVE,
        "postfinal_audit_source_sha256": BASE_AUDIT_SOURCE_SHA256,
        "postfinal_no_delegation_audit_path": STRICT_AUDIT_REPORT_RELATIVE,
        "postfinal_no_delegation_audit_sha256": strict_digest,
        "postfinal_no_delegation_audit_source_path": STRICT_AUDIT_SOURCE_RELATIVE,
        "postfinal_no_delegation_audit_source_sha256": STRICT_AUDIT_SOURCE_SHA256,
        "postfinal_no_delegation_audit_schema": STRICT_AUDIT_SCHEMA,
        "postfinal_no_delegation_control_count": 32,
        "postfinal_no_delegation_wrapper_control_count": 676,
        "original_oracle_source_path": previous.FROZEN_SOURCE.relative_to(ROOT).as_posix(),
        "original_oracle_source_sha256": previous.FROZEN_SOURCE_SHA256,
        "previous_oracle_source_path": STAGE05_SOURCE_RELATIVE,
        "previous_oracle_source_sha256": STAGE05_SOURCE_SHA256,
        "previous_all_candidate_report_path": STAGE05_REPORT_RELATIVE,
        "previous_all_candidate_report_sha256": STAGE05_REPORT_SHA256,
        "guarded_worker_source_path": previous.IMMUTABLE_WORKER_SOURCE_RELATIVE,
        "guarded_worker_source_sha256": previous.IMMUTABLE_WORKER_SOURCE_SHA256,
        "guarded_worker_report_path": previous.IMMUTABLE_WORKER_REPORT_RELATIVE,
        "guarded_worker_report_sha256": previous.IMMUTABLE_WORKER_REPORT_SHA256,
        "guarded_worker_schema": previous.IMMUTABLE_WORKER_SCHEMA,
        "immutable_public_case_sha256": previous.FROZEN_CASE_SHA256,
        "official_locale_source_path": LOCALE_SOURCE_RELATIVE,
        "official_locale_source_sha256": LOCALE_SOURCE_SHA256,
        "official_locale_report_path": LOCALE_REPORT_RELATIVE,
        "official_locale_report_sha256": locale_digest,
        "official_locale_schema": official_locale.SCHEMA,
        "official_locale_roles": list(official_locale.ROLE_MODULES),
        "official_locale_methods_per_role": 146,
        "official_locale_total_method_results": 584,
        "official_locale_skipped": 0,
        "official_locale_selected_method_sha256": (
            official_locale.SELECTED_METHOD_SHA256
        ),
        "previous_public_timing_evidence_read": False,
    }


@contextmanager
def _stage05_inherited_context() -> Iterator[None]:
    updates = {
        "RUNNER": previous.WRAPPER,
        "AUDIT_PATH": ROOT / previous.BASE_AUDIT_REPORT_RELATIVE,
        "default_output": previous.stage05_default_output,
        "build_cases": previous.stage05_build_cases,
        "synthetic_audit": previous.stage05_synthetic_audit,
        "validate_audit_document": previous.stage05_validate_audit_document,
        "verified_provenance": previous.stage05_verified_provenance,
        "self_test": previous.stage05_self_test,
        "run_gate": previous.stage05_run_gate,
    }
    original = {name: getattr(frozen, name) for name in updates}
    try:
        for name, value in updates.items():
            setattr(frozen, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(frozen, name, value)


def _synthetic_locale_proof(
    sources: dict[str, dict[str, str]],
    binaries: dict[str, dict[str, str]],
) -> tuple[dict[str, Any], str]:
    identities = sorted(official_locale.REQUIRED_LOCALE_TESTS)
    identities.extend(
        f"ReTests.test_stage06_synthetic_{index:03d}" for index in range(144)
    )
    records = [
        {
            "test": name,
            "status": "passed",
            "skipped": 0,
            "reason": None,
            "failures": [],
        }
        for name in identities
    ]
    selected_digest = _locale_selected_digest(records)
    roles = {
        role: {
            "module": module,
            "methods": 146,
            "passed": 146,
            "skipped": 0,
            "failed": 0,
            "failures": 0,
            "errors": 0,
            "crashes": 0,
            "timeouts": 0,
            "locale_caching_passed": True,
            "locale_compiled_passed": True,
            "records": json.loads(frozen.canonical(records)),
            "holdout_accessed": False,
            "timing_performed": False,
            "performance": "NOT MEASURED",
        }
        for role, module in official_locale.ROLE_MODULES.items()
    }
    locale_digest = hashlib.sha256(
        b"rebar/python-re/universal-public/stage06/synthetic-genuine-locale"
    ).hexdigest()
    document = {
        "schema": official_locale.SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "goal_sha256": official_locale.GOAL_SHA256,
        "source_path": LOCALE_SOURCE_RELATIVE,
        "source_sha256": LOCALE_SOURCE_SHA256,
        "original_oracle": {
            "manifest_path": official_locale.ORIGINAL_MANIFEST_PATH,
            "manifest_sha256": official_locale.ORIGINAL_MANIFEST_SHA256,
            "runner_path": official_locale.ORIGINAL_RUNNER_PATH,
            "runner_sha256": official_locale.ORIGINAL_RUNNER_SHA256,
            "source_sha256": dict(official_locale.SOURCE_HASHES),
            "total_public_methods": 152,
            "selected_methods": 146,
            "selected_method_sha256": selected_digest,
            "named_waivers": dict(official_locale.METHOD_WAIVERS),
            "named_class_waivers": dict(official_locale.CLASS_WAIVERS),
            "all_named_waivers": (
                official_locale.CLASS_WAIVERS | official_locale.METHOD_WAIVERS
            ),
            "corpus_cases": 403,
        },
        "audits": {
            "from_scratch": {
                "path": BASE_AUDIT_REPORT_RELATIVE,
                "sha256": SYNTHETIC_BASE_REPORT_SHA256,
                "postfinal_schema": BASE_AUDIT_SCHEMA,
                "source_path": BASE_AUDIT_SOURCE_RELATIVE,
                "source_sha256": SYNTHETIC_BASE_SOURCE_SHA256,
            },
            "no_delegation": {
                "path": STRICT_AUDIT_REPORT_RELATIVE,
                "sha256": SYNTHETIC_STRICT_REPORT_SHA256,
                "postfinal_schema": STRICT_AUDIT_SCHEMA,
                "source_path": STRICT_AUDIT_SOURCE_RELATIVE,
                "source_sha256": SYNTHETIC_STRICT_SOURCE_SHA256,
            },
        },
        "qualified_source_fingerprints": (
            previous._flatten_source_fingerprints(sources)
        ),
        "native_elf_fingerprints": previous._flatten_native_fingerprints(binaries),
        "locales": {
            "private": True,
            "genuine": True,
            "iso88591": {
                "name": official_locale.LOCALE_NAMES["iso88591"],
                "source_sha256": locale_digest,
                "charmap_sha256": locale_digest,
            },
            "utf8": {
                "name": official_locale.LOCALE_NAMES["utf8"],
                "source_sha256": locale_digest,
                "charmap_sha256": locale_digest,
            },
            "holdout_accessed": False,
            "timing_performed": False,
            "performance": "NOT MEASURED",
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
        "roles": roles,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    return document, selected_digest


def stage06_self_test() -> dict[str, Any]:
    """Run inherited and V5/locale poison controls without files or workers."""

    frozen.candidate_free()
    with previous._candidate_free_file_and_timing_guard() as effects:
        with _stage05_inherited_context():
            inherited = previous.stage05_self_test()
        frozen.require(
            inherited.get("stage") == "stage05"
            and inherited.get("check_count", 0) >= 170
            and inherited.get("candidate_imports") == 0
            and inherited.get("candidate_processes") == 0
            and inherited.get("files_read") == 0
            and inherited.get("files_written") == 0
            and inherited.get("performance_fixtures_read") == 0
            and inherited.get("holdout_cases_read") == 0
            and inherited.get("external_regex_packages") == 0
            and inherited.get("benchmark_or_timing_executed") is False,
            "stage-06 lost the 170 immutable candidate-free public controls",
        )
        checks = list(inherited["checks"])

        def check(name: str, condition: Any) -> None:
            frozen.require(
                condition, f"candidate-free stage-06 control failed: {name}"
            )
            checks.append({"name": name, "passed": True})

        def reject(name: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (
                frozen.OracleIntegrityError,
                AssertionError,
                KeyError,
                TypeError,
                ValueError,
            ):
                check(name, True)
            else:
                check(name, False)

        selected = REQUIRED_CANDIDATES
        source, sources, binaries, interpreter = stage06_synthetic_audit(selected)
        stage06_validate_audit_document(
            source, selected, sources, binaries, interpreter
        )
        check("stage06-accepts-exact-in-memory-v5-source-audit", True)

        def reject_base(field: str, replacement: Any) -> None:
            poisoned = json.loads(frozen.canonical(source))
            poisoned[field] = replacement
            reject(
                "stage06-rejects-poisoned-v5-source-" + field.replace("_", "-"),
                lambda: stage06_validate_audit_document(
                    poisoned, selected, sources, binaries, interpreter
                ),
            )

        for field, replacement in (
            ("schema_version", 2),
            ("audit", "foreign-regex-engine"),
            ("postfinal_schema", previous.BASE_AUDIT_SCHEMA),
            ("status", "FAIL"),
            ("result", "FAIL"),
            ("passed", False),
            ("audit_source_path", previous.BASE_AUDIT_SOURCE_RELATIVE),
            ("audit_source_sha256", "0" * 64),
            ("previous_v4_audit_source_path", "tools/foreign.py"),
            ("previous_v4_audit_source_sha256", "0" * 64),
            ("previous_v4_audit_report_path", BASE_AUDIT_REPORT_RELATIVE),
            ("previous_v4_audit_report_sha256", "0" * 64),
            ("previous_v4_postfinal_schema", BASE_AUDIT_SCHEMA),
            ("previous_v4_report_historical", False),
            ("verified_core_family_count", 2),
            ("verified_distinct_pipeline_count", 3),
            ("v5_allowed_locale_libc_primitives", ["tolower", "regexec"]),
            ("v5_owned_locale_sources", {"rust": "foreign.c"}),
        ):
            reject_base(field, replacement)

        strict = stage06_synthetic_strict_audit(sources, binaries)
        strict_args: dict[str, Any] = {
            "base_report_sha256": SYNTHETIC_BASE_REPORT_SHA256,
            "base_source_sha256": SYNTHETIC_BASE_SOURCE_SHA256,
            "strict_source_sha256": SYNTHETIC_STRICT_SOURCE_SHA256,
            "sources": sources,
            "binaries": binaries,
        }
        stage06_validate_strict_audit(strict, **strict_args)
        check("stage06-accepts-exact-in-memory-v5-no-delegation-audit", True)

        def reject_strict(field: str, replacement: Any) -> None:
            poisoned = json.loads(frozen.canonical(strict))
            poisoned[field] = replacement
            reject(
                "stage06-rejects-poisoned-v5-strict-" + field.replace("_", "-"),
                lambda: stage06_validate_strict_audit(poisoned, **strict_args),
            )

        for field, replacement in (
            ("schema", previous.STRICT_AUDIT_SCHEMA),
            ("postfinal_schema", previous.STRICT_AUDIT_SCHEMA),
            ("status", "FAIL"),
            ("result", "FAIL"),
            ("passed", False),
            ("audit_source_path", previous.STRICT_AUDIT_SOURCE_RELATIVE),
            ("audit_source_sha256", "0" * 64),
            ("base_audit_postfinal_schema", previous.BASE_AUDIT_SCHEMA),
            ("base_audit_report_path", previous.BASE_AUDIT_REPORT_RELATIVE),
            ("base_audit_report_sha256", "0" * 64),
            ("base_audit_source_path", previous.BASE_AUDIT_SOURCE_RELATIVE),
            ("base_audit_source_sha256", "0" * 64),
            ("inherited_control_count", 75),
            ("verified_core_family_count", 2),
            ("verified_distinct_pipeline_count", 3),
            ("previous_v4_audit_source_path", "tools/foreign.py"),
            ("previous_v4_audit_source_sha256", "0" * 64),
            ("previous_v4_source_report_path", BASE_AUDIT_REPORT_RELATIVE),
            ("previous_v4_source_report_sha256", "0" * 64),
            ("previous_v4_source_report_historical", False),
            ("previous_v4_strict_report_created", True),
            ("v5_allowed_locale_libc_primitives", ["regexec"]),
            ("v5_owned_locale_sources", {}),
        ):
            reject_strict(field, replacement)

        for family in ("rust", "vm", "zig"):
            poisoned = json.loads(frozen.canonical(strict))
            poisoned["families"][family]["passed"] = False
            reject(
                f"stage06-rejects-unqualified-v5-native-family-{family}",
                lambda value=poisoned: stage06_validate_strict_audit(
                    value, **strict_args
                ),
            )
        for field in ("qualified_source_fingerprints", "native_elf_fingerprints"):
            poisoned = json.loads(frozen.canonical(strict))
            poisoned[field].pop(next(iter(poisoned[field])))
            reject(
                "stage06-rejects-missing-v5-" + field.replace("_", "-"),
                lambda value=poisoned: stage06_validate_strict_audit(
                    value, **strict_args
                ),
            )
        for field, replacement in (
            ("check_count", 675),
            ("passed", False),
            ("candidate_imported", True),
            ("candidate_imports", 1),
            ("file_reads", 1),
            ("file_writes", 1),
            ("subprocesses", 1),
            ("clock_samples", 1),
            ("production_entropy_drawn", True),
            ("holdout_or_case_fixture_access", True),
            ("benchmark_or_timing_executed", True),
        ):
            poisoned = json.loads(frozen.canonical(strict))
            poisoned["postfinal_wrapper_self_test"][field] = replacement
            reject(
                "stage06-rejects-v5-wrapper-" + field.replace("_", "-"),
                lambda value=poisoned: stage06_validate_strict_audit(
                    value, **strict_args
                ),
            )

        locale, selected_digest = _synthetic_locale_proof(sources, binaries)
        locale_args: dict[str, Any] = {
            "base_report_sha256": SYNTHETIC_BASE_REPORT_SHA256,
            "base_source_sha256": SYNTHETIC_BASE_SOURCE_SHA256,
            "strict_report_sha256": SYNTHETIC_STRICT_REPORT_SHA256,
            "strict_source_sha256": SYNTHETIC_STRICT_SOURCE_SHA256,
            "sources": sources,
            "binaries": binaries,
            "selected_method_sha256": selected_digest,
        }
        stage06_validate_locale_proof(locale, **locale_args)
        check("stage06-accepts-in-memory-genuine-four-role-locale-proof", True)

        def reject_locale(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
            poisoned = json.loads(frozen.canonical(locale))
            mutate(poisoned)
            reject(
                "stage06-rejects-locale-" + name,
                lambda: stage06_validate_locale_proof(poisoned, **locale_args),
            )

        for field, replacement in (
            ("schema", "rebar-fake-locale-v1"),
            ("status", "FAIL"),
            ("result", "FAIL"),
            ("python", "3.14.5"),
            ("goal_sha256", "0" * 64),
            ("source_path", STAGE05_SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("holdout_accessed", True),
            ("timing_performed", True),
            ("performance", "guessed"),
        ):
            reject_locale(
                "top-level-" + field.replace("_", "-"),
                lambda value, field=field, replacement=replacement: value.update(
                    {field: replacement}
                ),
            )
        for field, replacement in (
            ("manifest_sha256", "0" * 64),
            ("runner_sha256", "0" * 64),
            ("source_sha256", {}),
            ("total_public_methods", 151),
            ("selected_methods", 145),
            ("selected_method_sha256", "0" * 64),
            ("named_waivers", {}),
            ("named_class_waivers", {}),
            ("all_named_waivers", {}),
            ("corpus_cases", 402),
        ):
            reject_locale(
                "official-" + field.replace("_", "-"),
                lambda value, field=field, replacement=replacement: value[
                    "original_oracle"
                ].update({field: replacement}),
            )
        for audit in ("from_scratch", "no_delegation"):
            for field, replacement in (
                ("path", "candidates/audits/FOREIGN.json"),
                ("sha256", "0" * 64),
                ("postfinal_schema", "historical-v3"),
                ("source_path", "tools/foreign.py"),
                ("source_sha256", "0" * 64),
            ):
                reject_locale(
                    audit + "-" + field.replace("_", "-"),
                    lambda value, audit=audit, field=field, replacement=replacement: value[
                        "audits"
                    ][audit].update({field: replacement}),
                )
        for role in official_locale.ROLE_MODULES:
            for field, replacement in (
                ("methods", 145),
                ("passed", 145),
                ("skipped", 1),
                ("failed", 1),
                ("failures", 1),
                ("errors", 1),
                ("crashes", 1),
                ("timeouts", 1),
                ("locale_caching_passed", False),
                ("locale_compiled_passed", False),
                ("holdout_accessed", True),
                ("timing_performed", True),
            ):
                reject_locale(
                    role + "-" + field.replace("_", "-"),
                    lambda value, role=role, field=field, replacement=replacement: value[
                        "roles"
                    ][role].update({field: replacement}),
                )
            reject_locale(
                role + "-individual-method-skip",
                lambda value, role=role: value["roles"][role]["records"][0].update(
                    {"status": "skipped", "skipped": 1}
                ),
            )
            reject_locale(
                role + "-omitted-locale-method",
                lambda value, role=role: value["roles"][role]["records"][0].update(
                    {"test": "ReTests.test_stage06_substituted"}
                ),
            )
        for encoding in official_locale.LOCALE_NAMES:
            reject_locale(
                "missing-genuine-" + encoding,
                lambda value, encoding=encoding: value["locales"].pop(encoding),
            )
            reject_locale(
                "poisoned-genuine-" + encoding,
                lambda value, encoding=encoding: value["locales"][encoding].update(
                    {"charmap_sha256": "invalid"}
                ),
            )
        reject_locale(
            "non-genuine-private-locales",
            lambda value: value["locales"].update({"genuine": False}),
        )
        reject_locale(
            "candidate-loaded-python-self-reference",
            lambda value: value["locale_reference"].update(
                {"candidate_modules_loaded": True}
            ),
        )

        cases = stage06_build_cases()
        check("stage06-preserves-all-original-8192-public-descriptors", len(cases) == 8192)
        check(
            "stage06-preserves-exact-public-case-fingerprint",
            frozen.value_digest(cases) == previous.FROZEN_CASE_SHA256,
        )
        check(
            "stage06-preserves-all-16-grammar-and-16-input-strata",
            len({case["family"] for case in cases}) == 16
            and len({case["stratum"] for case in cases}) == 16,
        )
        check(
            "stage06-preserves-all-48-three-engine-observations",
            frozen.OBSERVATIONS_PER_CASE == 48
            and frozen.EXPECTED_OBSERVATIONS * len(REQUIRED_CANDIDATES)
            == 1_179_648,
        )
        for candidate in REQUIRED_CANDIDATES:
            reject(
                "stage06-rejects-partial-production-" + candidate,
                lambda candidate=candidate: stage06_require_all(candidate),
            )
        for version in ("v1", "v2", "v3", "v4", "v5"):
            reject(
                "stage06-rejects-overwriting-historical-" + version,
                lambda version=version: frozen.validate_output(
                    frozen.EVIDENCE_ROOT
                    / f"python-re-universal-public-oracle-{version}-all.json",
                    "all",
                ),
            )
        check(
            "stage06-preserves-exclusive-v6-all-output",
            frozen.validate_output(stage06_default_output("all"), "all")
            == stage06_default_output("all").resolve(),
        )
        check(
            "stage06-guards-all-real-files-workers-clocks-and-entropy",
            all(value == 0 for value in effects.values()),
        )
        frozen.candidate_free()
        check("stage06-never-imports-a-production-candidate", True)
        names = [item["name"] for item in checks]
        frozen.require(
            len(names) == len(set(names)) and len(checks) >= 300,
            "stage-06 controls are duplicated or incomplete",
        )
        return {
            **inherited,
            "stage": "stage06",
            "postfinal_audit_schema": BASE_AUDIT_SCHEMA,
            "postfinal_audit_source_sha256": BASE_AUDIT_SOURCE_SHA256,
            "postfinal_audit_report_sha256": BASE_AUDIT_REPORT_SHA256,
            "postfinal_no_delegation_audit_schema": STRICT_AUDIT_SCHEMA,
            "postfinal_no_delegation_audit_source_sha256": (
                STRICT_AUDIT_SOURCE_SHA256
            ),
            "postfinal_no_delegation_audit_report_sha256": (
                STRICT_AUDIT_REPORT_SHA256
            ),
            "previous_oracle_source_sha256": STAGE05_SOURCE_SHA256,
            "previous_all_candidate_report_sha256": STAGE05_REPORT_SHA256,
            "official_locale_schema": official_locale.SCHEMA,
            "official_locale_source_sha256": LOCALE_SOURCE_SHA256,
            "official_locale_report_sha256": LOCALE_REPORT_SHA256,
            "official_locale_role_count": 4,
            "official_locale_methods_per_role": 146,
            "official_locale_skipped": 0,
            "production_candidate_policy": (
                "all three independently audited locale-qualified engines only"
            ),
            "exclusive_output": OUTPUT_RELATIVE,
            "checks": checks,
            "check_count": len(checks),
            "guarded_file_access_attempts": effects["files"],
            "guarded_worker_start_attempts": effects["workers"],
            "guarded_timing_attempts": effects["timing"],
            "guarded_entropy_attempts": effects["entropy"],
        }


frozen.RUNNER = WRAPPER
frozen.AUDIT_PATH = ROOT / BASE_AUDIT_REPORT_RELATIVE
frozen.default_output = stage06_default_output
frozen.build_cases = stage06_build_cases
frozen.synthetic_audit = stage06_synthetic_audit
frozen.validate_audit_document = stage06_validate_audit_document
frozen.verified_provenance = stage06_verified_provenance
frozen.self_test = stage06_self_test
frozen.run_gate = stage06_run_gate


if __name__ == "__main__":
    if "--self-test" not in sys.argv[1:] and "--worker" not in sys.argv[1:]:
        stage06_production_preflight()
    raise SystemExit(frozen.main())
