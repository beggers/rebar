#!/usr/bin/env python3
"""Run all original frozen correctness stages against freshly proven V7 engines."""

from __future__ import annotations

import copy
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from typing import Any, Iterator, Mapping
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v3 as official
from tools import postfinal_cpython_locale_v2_failure as failure_recorder
from tools import postfinal_from_scratch_audit_v7 as source_audit
from tools import postfinal_no_delegation_audit_v7 as strict_audit
from tools import python_re_universal_public_oracle_stage15_failure as public_failure
from tools import rust_v8_multi_candidate_campaign_postfinal_v5 as historical


ancestor = historical.ancestor
original = ancestor.original
hardened = ancestor.hardened
core = source_audit.core

SCHEMA = "rebar-v8-multi-candidate-sealed-campaign-postfinal-v7"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SOURCE_RELATIVE = "tools/rust_v8_multi_candidate_campaign_postfinal_v7.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-CAMPAIGN-V7.md"
PROTOCOL_PATH = ROOT / PROTOCOL_RELATIVE

BASE_SOURCE_SHA256 = (
    "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487"
)
BASE_REPORT_SHA256 = (
    "efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a"
)
STRICT_SOURCE_SHA256 = (
    "9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4"
)
STRICT_REPORT_SHA256 = (
    "1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34"
)
OFFICIAL_SOURCE_SHA256 = (
    "28b98c8913ca89ec2ba600484205c3bcb63ae22a86e33d4f7cf3c6f1a68c8a58"
)
OFFICIAL_PROTOCOL_SHA256 = (
    "a1f77b1628c03d42b9d8e2650c9b501d9be4cec917d765539c91c750154bd6ac"
)
OFFICIAL_REPORT_SHA256 = (
    "18a011a5ce6e47e52cd02e4cb0812c8f9f7919a069edd7d74e57631623b901b5"
)
OFFICIAL_V2_FAILURE_SHA256 = (
    "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f"
)

HISTORICAL_V5_SOURCE_RELATIVE = historical.SOURCE_RELATIVE
HISTORICAL_V5_SOURCE_SHA256 = (
    "50a39f8338b176b9376cac1437a7c0aaeb343594af0ebfea797a7beea04e86d9"
)
HISTORICAL_V4_SOURCE_RELATIVE = ancestor.SOURCE_RELATIVE
HISTORICAL_V4_SOURCE_SHA256 = (
    "67a7555976ab60c371c9aad1b7f94c112bd1c6aaf990e39c02f4484f3010e799"
)

STAGE14_SOURCE_RELATIVE = "tools/python_re_generic_alias_public_oracle_stage14.py"
STAGE14_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V14.md"
)
STAGE14_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v14-self-oracle.json"
)
STAGE14_ALL_RELATIVE = (
    "candidates/evidence/python-re-generic-alias-public-oracle-v14-all.json"
)
STAGE14_SCHEMA = "rebar-python-re-public-generic-alias-v14"
STAGE14_SEED = 2026072481
STAGE14_SEED_DOMAIN = "rebar/python-re/public-generic-alias/v14"
STAGE14_MATRIX_SHA256 = (
    "3d57a2eae1e880df934043856cf6d5ed32944908b7642611a3f060406453f1ab"
)
STAGE14_CASES = 128
STAGE14_CANDIDATE_CHECKS = 384
STAGE14_SOURCE_SHA256 = (
    "5caba6e5d92935a1877fb34bd3c1e266d07c67385f847477041312959104ec58"
)
STAGE14_PROTOCOL_SHA256 = (
    "b20b5b3876fba06cdf41b9a99825157d0ca6ba84b8bc7abfd71b49e44fdd7505"
)
STAGE14_REFERENCE_SHA256 = (
    "7da9c6aa5fa1db4ef0dea593d8f9d501ecc952aa62ed7bf5a0f17d0b726b04bf"
)
STAGE14_ALL_SHA256 = (
    "f9243bd27a4d4ae24c0c3f0b24785e381440fc19c8911b52719cc6813bc1e8cc"
)

STAGE17_SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage17.py"
STAGE17_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17.md"
STAGE17_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v17-self-oracle.json"
)
STAGE17_ALL_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v17-all.json"
)
STAGE17_SCHEMA = "rebar-python-re-public-contract-v17"
STAGE17_SEED = 2026072485
STAGE17_SEED_DOMAIN = "rebar/python-re/public-contract/v17"
STAGE17_MATRIX_SHA256 = (
    "e1c6ccf6cbb057f3e3cb708c1b4efe2a175bc77d6eda5e127cae18e5455cfa47"
)
STAGE17_CASES = 3584
STAGE17_CANDIDATE_CHECKS = 10752
STAGE17_SOURCE_SHA256 = (
    "9e5ca448ecc6a6de8745b0c84cf5b4ae5d92cd098914731a4047d45e6ce1b6d4"
)
STAGE17_PROTOCOL_SHA256 = (
    "8773d4fd2d0b9f04808b2a22358a233b44abfd892862aaaf224cd0d607081520"
)
STAGE17_REFERENCE_SHA256 = (
    "de1272f7c3681402b8787ea2a53de8228ef0341760505dc052c52b023e3d3c3d"
)
STAGE17_ALL_SHA256 = (
    "255644709afe8fa8ce41cefcfd029b7f865bbcd0314d528902bb5a56d52aa288"
)
STAGE17_READER_SOURCE_RELATIVE = (
    "tools/python_re_universal_public_oracle_stage17_evidence.py"
)
STAGE17_READER_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17-EVIDENCE.md"
)
# Root independently froze, maliciously tested, and actually verified the
# only exact-path, no-follow 32 MiB complete-evidence reader.
STAGE17_READER_SOURCE_SHA256 = (
    "fbaebec7bcfad26c94154dce2024ece8349ea54479fda6831d5331f4195fd4cb"
)
STAGE17_READER_PROTOCOL_SHA256 = (
    "c6b4a3b037ca79f7ccef0c7248ac5d7dbbb1a8f339155b277f8c36ad3c14191d"
)

STAGE15_FAILED_SOURCE_RELATIVE = public_failure.STAGE15_SOURCE_RELATIVE
STAGE15_FAILED_SOURCE_SHA256 = public_failure.STAGE15_SOURCE_SHA256
STAGE15_FAILED_PROTOCOL_RELATIVE = public_failure.STAGE15_PROTOCOL_RELATIVE
STAGE15_FAILED_PROTOCOL_SHA256 = public_failure.STAGE15_PROTOCOL_SHA256
STAGE15_RAW_REFERENCE_RELATIVE = public_failure.ORIGINAL_REFERENCE_RELATIVE
STAGE15_RAW_REFERENCE_SHA256 = public_failure.ORIGINAL_REFERENCE_SHA256
STAGE15_FAILURE_SOURCE_RELATIVE = public_failure.SOURCE_RELATIVE
STAGE15_FAILURE_SOURCE_SHA256 = (
    "07a522f263cd9e0baad022f91988d034b3cde3013b143bd1f9a77174fa0b58b6"
)
STAGE15_FAILURE_PROTOCOL_RELATIVE = public_failure.PROTOCOL_RELATIVE
STAGE15_FAILURE_PROTOCOL_SHA256 = (
    "6aa2b8e5bcd6867af60c570d19508a67e0094eedca4ab815266e0f91e2c83b03"
)
STAGE15_FAILURE_RELATIVE = public_failure.REPORT_RELATIVE
STAGE15_FAILURE_SHA256 = (
    "cb71e1a44549c7c76c3bf08900e6107d2b49e789e5002afc725d1e9df0c92880"
)
STAGE15_DECLARED_DIGEST = public_failure.DURABLE_TRANSPORT_DIGEST
STAGE15_FROZEN_VALIDATOR_DIGEST = public_failure.FROZEN_VALIDATOR_DIGEST

GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
CORE_FAMILIES = ("rust", "vm", "zig")
OFFICIAL_METHODS = 146
REQUIRED_STEP_COUNT = 22
EDGE_CHECKS = 223198
EDGE_CATEGORIES = 49
DEEP_CASES = 393
DEEP_SEEDED_CASES = 64
DEEP_SEED = 2026072347
OBSERVABILITY_CASES = 479
OBSERVABILITY_SEED = 2026072343
UNICODE_CASES = 4_494_555
ALIAS_COHORTS = {
    "ordinary-alias": 40,
    "diverse-argument": 48,
    "parameterized-type-rejection": 16,
    "alias-lifecycle": 24,
}
UNIVERSAL_COHORTS = {
    "public-surface": 256,
    "invalid-grammar": 256,
    "real-locale": 1024,
    "buffer-lifetime": 256,
    "object-contract": 256,
    "callback-scanner": 256,
    "shared-pattern-threads": 256,
    "bounded-unicode": 1024,
}
_ACTIVE_PROVENANCE: dict[str, Any] | None = None


def require(condition: Any, message: str) -> None:
    original.require(bool(condition), message)


def expected_edge_paths(family: str) -> dict[str, Path]:
    return historical.expected_edge_paths(family)


def validate_edge_artifacts(
    source: Mapping[str, Any], module: str, edge: Mapping[str, Any],
) -> None:
    historical.validate_edge_artifacts(source, module, edge)


def _pins(synthetic: Mapping[str, Any] | None = None) -> dict[str, str]:
    values: dict[str, Any] = {
        "source_audit_source": BASE_SOURCE_SHA256,
        "source_audit_report": BASE_REPORT_SHA256,
        "strict_audit_source": STRICT_SOURCE_SHA256,
        "strict_audit_report": STRICT_REPORT_SHA256,
        "official_source": OFFICIAL_SOURCE_SHA256,
        "official_protocol": OFFICIAL_PROTOCOL_SHA256,
        "official_report": OFFICIAL_REPORT_SHA256,
        "official_v2_failure": OFFICIAL_V2_FAILURE_SHA256,
        "stage14_source": STAGE14_SOURCE_SHA256,
        "stage14_protocol": STAGE14_PROTOCOL_SHA256,
        "stage14_reference": STAGE14_REFERENCE_SHA256,
        "stage14_all": STAGE14_ALL_SHA256,
        "stage17_source": STAGE17_SOURCE_SHA256,
        "stage17_protocol": STAGE17_PROTOCOL_SHA256,
        "stage17_reference": STAGE17_REFERENCE_SHA256,
        "stage17_all": STAGE17_ALL_SHA256,
        "stage17_reader_source": STAGE17_READER_SOURCE_SHA256,
        "stage17_reader_protocol": STAGE17_READER_PROTOCOL_SHA256,
        "stage15_failed_source": STAGE15_FAILED_SOURCE_SHA256,
        "stage15_failed_protocol": STAGE15_FAILED_PROTOCOL_SHA256,
        "stage15_raw_reference": STAGE15_RAW_REFERENCE_SHA256,
        "stage15_failure_source": STAGE15_FAILURE_SOURCE_SHA256,
        "stage15_failure_protocol": STAGE15_FAILURE_PROTOCOL_SHA256,
        "stage15_failure_report": STAGE15_FAILURE_SHA256,
    }
    if synthetic is not None:
        require(isinstance(synthetic, Mapping)
                and set(synthetic) == set(values),
                "a synthetic campaign omitted a mandatory fresh correctness gate")
        values = dict(synthetic)
    for name, value in values.items():
        require(core.valid_sha256(value),
                "the genuine V7 prerequisite is not published: " + name)
    require(len(set(values.values())) == len(values),
            "distinct correctness results cannot share a substituted fingerprint")
    return values


def _read_exact(
    relative: str, expected: str, *, document: bool,
) -> Mapping[str, Any] | str:
    require(type(relative) is str, "a frozen public correctness path must be text")
    parsed = PurePosixPath(relative)
    require(not parsed.is_absolute()
            and ".." not in parsed.parts
            and "\\" not in relative
            and "\x00" not in relative
            and str(parsed) == relative,
            "a frozen correctness prerequisite is private or noncanonical")
    path = ROOT / relative
    require(not path.is_symlink(), "a frozen public correctness path is symbolic")
    maximum = (source_audit.MAX_REPORT_BYTES if document
               else source_audit.MAX_SOURCE_BYTES)
    fingerprint, payload = core.bounded_file(
        path, maximum=maximum,
        label="actual root-published full V7 campaign input: " + relative,
        keep=document,
    )
    require(fingerprint == expected,
            "an exclusively published correctness result changed: " + relative)
    if not document:
        return fingerprint
    require(isinstance(payload, bytes),
            "an authenticated frozen correctness report returned no bytes")
    result = core.decode_report(payload, label="actual V7 gate: " + relative)
    require(isinstance(result, dict),
            "a real V7 correctness gate is not a JSON object")
    return result


def _actual_controller_digest() -> str:
    fingerprint, _ = core.bounded_file(
        SOURCE_PATH, maximum=source_audit.MAX_SOURCE_BYTES,
        label="actual frozen complete 22-stage V7 correctness controller",
    )
    require(core.valid_sha256(fingerprint),
            "the complete V7 controller has no actual source fingerprint")
    return fingerprint


def validate_official_document(
    document: Mapping[str, Any], source: Mapping[str, Any],
    strict: Mapping[str, Any], pins: Mapping[str, str],
    *, module: str | None = None,
) -> None:
    require(isinstance(document, Mapping)
            and document.get("schema") == official.SCHEMA
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("python") == "3.14.6"
            and document.get("goal_sha256") == GOAL_SHA256
            and document.get("source_path") == official.SOURCE_RELATIVE
            and document.get("source_sha256") == pins["official_source"]
            and document.get("holdout_accessed") is False
            and document.get("timing_performed") is False
            and document.get("performance") == "NOT MEASURED",
            "the actual V3 four-role official Python experiment did not pass")
    audits = document.get("audits")
    require(isinstance(audits, Mapping)
            and set(audits) == {"from_scratch", "no_delegation"},
            "the genuine official result omitted a fresh independence proof")
    expected = {
        "from_scratch": (
            source_audit.REPORT_RELATIVE,
            pins["source_audit_report"],
            source_audit.SCHEMA,
            source_audit.SOURCE_RELATIVE,
            pins["source_audit_source"],
        ),
        "no_delegation": (
            strict_audit.REPORT_RELATIVE,
            pins["strict_audit_report"],
            strict_audit.SCHEMA,
            strict_audit.SOURCE_RELATIVE,
            pins["strict_audit_source"],
        ),
    }
    for name, (path, digest, schema, controller, controller_hash) in expected.items():
        result = audits[name]
        require(isinstance(result, Mapping)
                and result.get("path") == path
                and result.get("sha256") == digest
                and result.get("postfinal_schema") == schema
                and result.get("source_path") == controller
                and result.get("source_sha256") == controller_hash,
                "the actual official run substituted its " + name + " proof")
    require(document.get("qualified_source_fingerprints")
            == strict.get("qualified_source_fingerprints")
            and document.get("native_elf_fingerprints")
            == strict.get("native_elf_fingerprints")
            and source.get("native_elf_provenance")
            == strict.get("native_elf_provenance")
            and source.get("manifest_provenance")
            == strict.get("manifest_provenance"),
            "the genuine four-role official test used different native engines")
    upstream = document.get("original_oracle")
    require(isinstance(upstream, Mapping)
            and upstream.get("total_public_methods") == 152
            and upstream.get("selected_methods") == OFFICIAL_METHODS
            and upstream.get("corpus_cases") == 403
            and upstream.get("source_sha256") == official.original.SOURCE_HASHES
            and upstream.get("runner_sha256")
            == official.original.ORIGINAL_RUNNER_SHA256
            and upstream.get("manifest_sha256")
            == official.original.ORIGINAL_MANIFEST_SHA256
            and upstream.get("selected_method_sha256")
            == official.original.SELECTED_METHOD_SHA256
            and upstream.get("named_class_waivers")
            == official.original.CLASS_WAIVERS
            and upstream.get("all_named_waivers")
            == (official.original.CLASS_WAIVERS
                | official.original.METHOD_WAIVERS)
            and len(upstream["all_named_waivers"]) == 8,
            "the unchanged original Python test corpus or named waivers changed")
    scope = document.get("official_scope")
    required_scope = {
        "genuine_official_methods_per_engine": OFFICIAL_METHODS,
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
    require(isinstance(scope, Mapping)
            and all(scope.get(name) == value
                    for name, value in required_scope.items()),
            "the complete official methods, locale, failure, or source scope changed")
    locales = document.get("locales")
    reference = document.get("locale_reference")
    require(isinstance(locales, Mapping)
            and locales.get("genuine") is True
            and locales.get("private") is True
            and isinstance(locales.get("iso88591"), Mapping)
            and locales["iso88591"].get("name") == "en_US.iso88591"
            and isinstance(locales.get("utf8"), Mapping)
            and locales["utf8"].get("name") == "en_US.utf8"
            and isinstance(reference, Mapping)
            and reference.get("status") == "PASS"
            and reference.get("genuine_locales") is True
            and reference.get("compiled_locale_switch") is True
            and reference.get("candidate_modules_loaded") is False,
            "the upstream official test lacks genuinely compiled private locales")
    history = document.get("supersedes")
    require(isinstance(history, Mapping)
            and isinstance(history.get("version_two"), Mapping),
            "the genuine failed official V2 experiment was omitted")
    prior = history["version_two"]
    require(prior.get("failure_report_path") == failure_recorder.REPORT_RELATIVE
            and prior.get("failure_report_sha256") == pins["official_v2_failure"]
            and prior.get("failed_role") == "rust"
            and prior.get("failed_method") == "ReTests.test_match_repr"
            and prior.get("rust_passed") == 145
            and prior.get("rust_methods") == 146
            and prior.get("c_official") == "NOT RUN"
            and prior.get("zig_official") == "NOT RUN"
            and prior.get("official_all_report_exists") is False
            and prior.get("historical") is True
            and prior.get("qualifies_current_sources") is False,
            "the genuine official V2 failure was hidden or falsely qualified")
    roles = document.get("roles")
    require(isinstance(roles, Mapping)
            and set(roles) == set(official.original.ROLE_MODULES),
            "the actual V3 official report omitted Python or an independent engine")
    baseline_ids: frozenset[str] | None = None
    for family, candidate in official.original.ROLE_MODULES.items():
        result = roles[family]
        require(isinstance(result, Mapping)
                and result.get("module") == candidate
                and result.get("methods") == OFFICIAL_METHODS
                and result.get("passed") == OFFICIAL_METHODS
                and result.get("skipped") == 0
                and result.get("failed") == 0
                and result.get("failures") == 0
                and result.get("crashes") == 0
                and result.get("timeouts") == 0
                and result.get("locale_caching_passed") is True
                and result.get("locale_compiled_passed") is True
                and result.get("holdout_accessed") is False
                and result.get("timing_performed") is False
                and result.get("performance") == "NOT MEASURED",
                "a genuine official 146/146 result is incomplete: " + family)
        records = result.get("records")
        require(isinstance(records, list)
                and len(records) == OFFICIAL_METHODS,
                "the genuine official result concealed named method evidence")
        identifiers: set[str] = set()
        for row in records:
            require(isinstance(row, Mapping)
                    and isinstance(row.get("test"), str)
                    and row["test"] not in identifiers
                    and row.get("status") == "passed"
                    and row.get("skipped") == 0
                    and row.get("reason") is None
                    and not row.get("failures"),
                    "an original official method failed, skipped, or repeated")
            identifiers.add(row["test"])
        require("ExternalTests.test_re_tests" in identifiers
                and official.original.REQUIRED_LOCALE_TESTS <= identifiers,
                "the 403 original corpus cases or real locale tests were omitted")
        if baseline_ids is None:
            baseline_ids = frozenset(identifiers)
        else:
            require(frozenset(identifiers) == baseline_ids,
                    "a rebuilt engine ran different original official Python tests")
    if module is not None:
        family = original.family_for(module)
        require(roles[family]["module"] == module,
                "the official proof was swapped with another candidate")


def _stage_spec(label: str) -> dict[str, Any]:
    if label == "stage14":
        return {
            "label": label,
            "schema": STAGE14_SCHEMA,
            "source": STAGE14_SOURCE_RELATIVE,
            "protocol": STAGE14_PROTOCOL_RELATIVE,
            "reference": STAGE14_REFERENCE_RELATIVE,
            "all": STAGE14_ALL_RELATIVE,
            "seed": STAGE14_SEED,
            "seed_domain": STAGE14_SEED_DOMAIN,
            "matrix": STAGE14_MATRIX_SHA256,
            "cases": STAGE14_CASES,
            "candidate_checks": STAGE14_CANDIDATE_CHECKS,
            "cohorts": ALIAS_COHORTS,
        }
    require(label == "stage17", "an unrelated correctness stage was requested")
    return {
        "label": label,
        "schema": STAGE17_SCHEMA,
        "source": STAGE17_SOURCE_RELATIVE,
        "protocol": STAGE17_PROTOCOL_RELATIVE,
        "reference": STAGE17_REFERENCE_RELATIVE,
        "all": STAGE17_ALL_RELATIVE,
        "seed": STAGE17_SEED,
        "seed_domain": STAGE17_SEED_DOMAIN,
        "matrix": STAGE17_MATRIX_SHA256,
        "cases": STAGE17_CASES,
        "candidate_checks": STAGE17_CANDIDATE_CHECKS,
        "cohorts": UNIVERSAL_COHORTS,
    }


def _validate_stage_provenance(
    value: Any, spec: Mapping[str, Any], pins: Mapping[str, str],
) -> dict[str, Any]:
    require(isinstance(value, Mapping),
            "the full " + str(spec["label"]) + " proof has no source provenance")
    label = str(spec["label"])
    expected = {
        "source_path": spec["source"],
        "source_sha256": pins[label + "_source"],
        "protocol_path": spec["protocol"],
        "protocol_sha256": pins[label + "_protocol"],
        "seed": spec["seed"],
        "seed_domain": spec["seed_domain"],
        "matrix_sha256": spec["matrix"],
        "base_audit_source_path": source_audit.SOURCE_RELATIVE,
        "base_audit_source_sha256": pins["source_audit_source"],
        "base_audit_path": source_audit.REPORT_RELATIVE,
        "base_audit_sha256": pins["source_audit_report"],
        "strict_audit_source_path": strict_audit.SOURCE_RELATIVE,
        "strict_audit_source_sha256": pins["strict_audit_source"],
        "strict_audit_path": strict_audit.REPORT_RELATIVE,
        "strict_audit_sha256": pins["strict_audit_report"],
        "native_source_count": 12,
        "native_binary_count": 5,
    }
    for key, actual in expected.items():
        aliases = {
            "base_audit_path": "base_audit_report_path",
            "base_audit_sha256": "base_audit_report_sha256",
            "strict_audit_path": "strict_audit_report_path",
            "strict_audit_sha256": "strict_audit_report_sha256",
        }
        observed = value.get(key, value.get(aliases.get(key, "")))
        require(observed == actual,
                "the full " + label + " provenance changed: " + key)
    if label == "stage14":
        actual_upstream = {
            "official_v3_source_path": official.SOURCE_RELATIVE,
            "official_v3_source_sha256": pins["official_source"],
            "official_v3_protocol_path": official.PROTOCOL_RELATIVE,
            "official_v3_protocol_sha256": pins["official_protocol"],
            "official_v3_report_path": official.REPORT_RELATIVE,
            "official_v3_report_sha256": pins["official_report"],
            "official_v3_status": "PASS",
            "official_v3_completed_roles": ["re", *CORE_FAMILIES],
            "official_v3_methods_per_role": OFFICIAL_METHODS,
            "official_v3_total_method_checks": OFFICIAL_METHODS * 4,
            "official_v3_failed_methods": 0,
            "official_v3_skipped_methods": 0,
            "official_v3_crashes": 0,
            "official_v3_v2_failure_preserved": True,
            "official_v2_failure_path": failure_recorder.REPORT_RELATIVE,
            "official_v2_failure_sha256": pins["official_v2_failure"],
            "official_v2_failure_status": "FAIL",
            "official_v2_failed_role": "rust",
            "official_v2_failed_method": "ReTests.test_match_repr",
            "official_v2_failure_qualifies_current_sources": False,
        }
    else:
        actual_upstream = {
            "observation_domain": spec["seed_domain"],
            "official_source_path": official.SOURCE_RELATIVE,
            "official_source_sha256": pins["official_source"],
            "official_protocol_path": official.PROTOCOL_RELATIVE,
            "official_protocol_sha256": pins["official_protocol"],
            "official_report_path": official.REPORT_RELATIVE,
            "official_report_sha256": pins["official_report"],
            "official_methods_per_role": OFFICIAL_METHODS,
            "official_role_count": 4,
            "official_skipped": 0,
            "official_v2_failure_path": failure_recorder.REPORT_RELATIVE,
            "official_v2_failure_sha256": pins["official_v2_failure"],
            "official_v2_failure_historical": True,
            "stage14_source_path": STAGE14_SOURCE_RELATIVE,
            "stage14_source_sha256": pins["stage14_source"],
            "stage14_protocol_path": STAGE14_PROTOCOL_RELATIVE,
            "stage14_protocol_sha256": pins["stage14_protocol"],
            "stage14_self_oracle_path": STAGE14_REFERENCE_RELATIVE,
            "stage14_self_oracle_sha256": pins["stage14_reference"],
            "stage14_all_candidate_path": STAGE14_ALL_RELATIVE,
            "stage14_all_candidate_sha256": pins["stage14_all"],
            "stage14_cases_per_candidate": STAGE14_CASES,
            "stage14_candidate_checks": STAGE14_CANDIDATE_CHECKS,
            "historical_stage10_only": True,
            "stage15_source_path": STAGE15_FAILED_SOURCE_RELATIVE,
            "stage15_source_sha256": pins["stage15_failed_source"],
            "stage15_protocol_path": STAGE15_FAILED_PROTOCOL_RELATIVE,
            "stage15_protocol_sha256": pins["stage15_failed_protocol"],
            "stage15_raw_reference_path": STAGE15_RAW_REFERENCE_RELATIVE,
            "stage15_raw_reference_sha256": pins["stage15_raw_reference"],
            "stage15_reference_status": "FALSIFIED",
            "stage15_declared_record_sha256": STAGE15_DECLARED_DIGEST,
            "stage15_actual_record_sha256": STAGE15_FROZEN_VALIDATOR_DIGEST,
            "stage15_durable_transport_record_sha256": STAGE15_DECLARED_DIGEST,
            "stage15_frozen_validator_record_sha256": (
                STAGE15_FROZEN_VALIDATOR_DIGEST
            ),
            "stage15_failure_source_path": STAGE15_FAILURE_SOURCE_RELATIVE,
            "stage15_failure_source_sha256": pins["stage15_failure_source"],
            "stage15_failure_protocol_path": STAGE15_FAILURE_PROTOCOL_RELATIVE,
            "stage15_failure_protocol_sha256": pins["stage15_failure_protocol"],
            "stage15_failure_path": STAGE15_FAILURE_RELATIVE,
            "stage15_failure_sha256": pins["stage15_failure_report"],
            "stage15_reference_record_count": STAGE17_CASES * 2,
            "stage15_candidate_runs": 0,
            "durable_json_canonicalization": "frozen-json-ascii-sort-keys-v17",
            "durable_reference_hash_domain": (
                "persisted-normalized-json-once-v17"
            ),
        }
    for key, actual in actual_upstream.items():
        require(value.get(key) == actual
                and type(value.get(key)) is type(actual),
                "the genuine " + label + " upstream provenance changed: " + key)
    require(value.get("verified_standard_pickle_count", 48) == 48
            and value.get("verified_match_repr_count", 6) == 6,
            "the public proof dropped real owned-type or native matching checks")
    return dict(value)


def validate_public_experiment(
    label: str, reference: Mapping[str, Any],
    all_candidates: Mapping[str, Any], pins: Mapping[str, str],
) -> None:
    spec = _stage_spec(label)
    cases = int(spec["cases"])
    required = {
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": spec["source"],
        "source_sha256": pins[label + "_source"],
        "protocol_path": spec["protocol"],
        "protocol_sha256": pins[label + "_protocol"],
        "seed": spec["seed"],
        "seed_domain": spec["seed_domain"],
        "matrix_sha256": spec["matrix"],
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, document in (("two-reference oracle", reference),
                           ("complete candidate oracle", all_candidates)):
        require(isinstance(document, Mapping),
                "the actual " + label + " " + name + " is absent")
        for field, expected in required.items():
            require(document.get(field) == expected
                    and type(document.get(field)) is type(expected),
                    "the actual " + label + " " + name + " changed: " + field)
    proof = _validate_stage_provenance(
        reference.get("current_provenance"), spec, pins,
    )
    require(all_candidates.get("current_provenance") == proof,
            "the two " + label + " proofs run different actual engines")
    baseline = reference.get("baseline_records")
    second_reference = reference.get("second_records")
    require(reference.get("schema") == spec["schema"] + "-self-oracle"
            and reference.get("cases") == cases
            and reference.get("stdlib_checks") == cases * 2
            and reference.get("mismatches") == 0
            and reference.get("failure_records") == []
            and reference.get("candidate_imports") == 0
            and reference.get("candidate_processes") == 0
            and reference.get("independent_stdlib_roles")
            == ["stdlib-a", "stdlib-b"]
            and isinstance(baseline, list)
            and len(baseline) == cases
            and all(isinstance(row, Mapping) for row in baseline)
            and isinstance(second_reference, list)
            and len(second_reference) == cases
            and all(isinstance(row, Mapping) for row in second_reference)
            and second_reference == baseline
            and reference.get("baseline_record_sha256")
            == original.digest_value(baseline)
            and reference.get("second_record_sha256")
            == original.digest_value(second_reference),
            "the genuine " + label + " double Python oracle concealed an observation")
    expected_cohorts = dict(spec["cohorts"])
    require(reference.get("cohorts") == len(expected_cohorts)
            and reference.get("cohort_cases") == expected_cohorts,
            "the actual " + label + " property/fuzz cohorts were weakened")
    identifiers: list[str] = []
    for row in baseline:
        identity = row.get("id")
        require(isinstance(identity, str),
                "the " + label + " Python reference omitted a case identity")
        identifiers.append(identity)
    require(len(set(identifiers)) == cases,
            "the " + label + " Python reference duplicated or dropped a case")
    require(all_candidates.get("schema")
            == spec["schema"] + "-all-candidates"
            and all_candidates.get("selected") == "all"
            and all_candidates.get("selected_candidates") == list(CORE_FAMILIES)
            and all_candidates.get("completed_candidates") == list(CORE_FAMILIES)
            and all_candidates.get("comparison_complete") is True
            and all_candidates.get("cases_per_candidate") == cases
            and all_candidates.get("candidate_checks") == spec["candidate_checks"]
            and all_candidates.get("cohorts") == len(expected_cohorts)
            and all_candidates.get("cohort_cases") == expected_cohorts
            and all_candidates.get("self_oracle_path") == spec["reference"]
            and all_candidates.get("self_oracle_sha256")
            == pins[label + "_reference"]
            and all_candidates.get("baseline_record_sha256")
            == reference["baseline_record_sha256"]
            and all_candidates.get("baseline_records") == baseline
            and isinstance(all_candidates.get("second_reference_records"), list)
            and len(all_candidates["second_reference_records"]) == cases
            and all_candidates["second_reference_records"] == second_reference
            and original.digest_value(all_candidates["second_reference_records"])
            == reference["second_record_sha256"]
            and all_candidates.get("candidate_cross_delegation") is False
            and all_candidates.get("mismatches") == 0,
            "the actual full " + label
            + " result concealed a full Python reference or mismatch")
    if label == "stage17":
        require(all_candidates.get("external_regex_packages") == 0
                and type(all_candidates.get("external_regex_packages")) is int,
                "the genuine public/fuzz experiment delegated to an external regex")
    outcomes = all_candidates.get("candidate_reports")
    require(isinstance(outcomes, Mapping)
            and set(outcomes) == set(CORE_FAMILIES),
            "the full " + label + " proof omitted an independent family")
    expected_native = proof.get("native_sha256_by_family")
    require(isinstance(expected_native, Mapping)
            and set(expected_native) == set(CORE_FAMILIES),
            "the " + label + " proof omitted real native mappings")
    for family in CORE_FAMILIES:
        result = outcomes[family]
        require(isinstance(result, Mapping)
                and result.get("candidate") == family
                and result.get("module")
                == "candidates." + family + "_candidate"
                and result.get("status") == "PASS"
                and result.get("cases") == cases
                and result.get("cohort_cases") == expected_cohorts
                and result.get("records") == baseline
                and isinstance(result.get("records"), list)
                and len(result["records"]) == cases
                and [row.get("id") for row in result["records"]] == identifiers
                and result.get("record_sha256")
                == reference["baseline_record_sha256"]
                and result.get("mismatches") == 0
                and result.get("failure_records") == []
                and result.get("failures_recorded") == 0
                and result.get("native_binary_sha256") == expected_native[family]
                and result.get("benchmark_or_timing_executed") is False
                and result.get("performance_fixtures_read") == 0
                and result.get("holdout_cases_read") == 0
                and result.get("performance") == "NOT MEASURED",
                "the " + label + " proof omitted an actual candidate record: " + family)
        official.previous._validate_guard(result.get("guard"), family)


def validate_preserved_public_failure(
    incident: Any, raw: Any, pins: Mapping[str, str],
) -> dict[str, Any]:
    require(isinstance(incident, dict) and isinstance(raw, dict),
            "the genuine first Stage15 failure and original stream are required")
    require(public_failure.validate_report(incident) is incident,
            "the separately preserved actual V15 failure rejected its own proof")
    expected: dict[str, Any] = {
        "schema": public_failure.SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "source_path": STAGE15_FAILURE_SOURCE_RELATIVE,
        "source_sha256": pins["stage15_failure_source"],
        "protocol_path": STAGE15_FAILURE_PROTOCOL_RELATIVE,
        "protocol_sha256": pins["stage15_failure_protocol"],
        "stage15_source_path": STAGE15_FAILED_SOURCE_RELATIVE,
        "stage15_source_sha256": pins["stage15_failed_source"],
        "stage15_protocol_path": STAGE15_FAILED_PROTOCOL_RELATIVE,
        "stage15_protocol_sha256": pins["stage15_failed_protocol"],
        "original_reference_path": STAGE15_RAW_REFERENCE_RELATIVE,
        "original_reference_sha256": pins["stage15_raw_reference"],
        "original_reference_status": "PASS",
        "original_reference_is_valid": False,
        "cases": STAGE17_CASES,
        "stdlib_checks": STAGE17_CASES * 2,
        "actual_reference_record_count": STAGE17_CASES * 2,
        "actual_reference_worker_count": 2,
        "declared_record_sha256": STAGE15_DECLARED_DIGEST,
        "actual_record_sha256": STAGE15_FROZEN_VALIDATOR_DIGEST,
        "durable_transport_record_sha256": STAGE15_DECLARED_DIGEST,
        "frozen_validator_record_sha256": STAGE15_FROZEN_VALIDATOR_DIGEST,
        "declared_digest_count": 4,
        "digest_mismatch_count": 4,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "reference_rerun": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    for key, value in expected.items():
        require(incident.get(key) == value
                and type(incident.get(key)) is type(value),
                "the genuine preserved V15 failure changed: " + key)
    require(incident.get("original_reference_document") == raw,
            "the genuine first false-positive reference records were replaced")
    require(incident.get("candidate_status_by_family")
            == {family: "NOT RUN" for family in CORE_FAMILIES},
            "an unrun V15 native candidate was silently declared qualified")
    rejections = incident.get("validator_rejections")
    require(isinstance(rejections, list)
            and len(rejections) == 2
            and {item.get("context") for item in rejections
                 if isinstance(item, Mapping)} == {"outside", "inside"}
            and all(isinstance(item, Mapping)
                    and item.get("rejected") is True
                    and item.get("exception_type") == "OracleIntegrityError"
                    and isinstance(item.get("message"), str)
                    and bool(item.get("message"))
                    for item in rejections),
            "the original V15 validator must reject both authentic contexts")
    records = raw.get("baseline_records")
    second = raw.get("second_records")
    workers = raw.get("reference_worker_reports")
    require(isinstance(records, list)
            and isinstance(second, list)
            and len(records) == len(second) == STAGE17_CASES
            and records == second
            and isinstance(workers, Mapping)
            and set(workers) == {"stdlib-a", "stdlib-b"},
            "the first false-positive discarded a complete actual Python stream")
    for label, rows in (("stdlib-a", records), ("stdlib-b", second)):
        worker = workers[label]
        require(isinstance(worker, Mapping)
                and worker.get("records") == rows
                and worker.get("record_sha256") == STAGE15_DECLARED_DIGEST
                and public_failure.portable_digest(rows)
                == STAGE15_DECLARED_DIGEST
                and public_failure.frozen_validator_digest(rows)
                == STAGE15_FROZEN_VALIDATOR_DIGEST,
                "the genuine V15 worker transport or frozen contract changed: "
                + label)
    return incident


def _preflight() -> dict[str, Any]:
    pins = _pins()
    for relative, digest in (
        (source_audit.SOURCE_RELATIVE, pins["source_audit_source"]),
        (strict_audit.SOURCE_RELATIVE, pins["strict_audit_source"]),
        (official.SOURCE_RELATIVE, pins["official_source"]),
        (official.PROTOCOL_RELATIVE, pins["official_protocol"]),
        (HISTORICAL_V5_SOURCE_RELATIVE, HISTORICAL_V5_SOURCE_SHA256),
        (HISTORICAL_V4_SOURCE_RELATIVE, HISTORICAL_V4_SOURCE_SHA256),
        (STAGE14_SOURCE_RELATIVE, pins["stage14_source"]),
        (STAGE14_PROTOCOL_RELATIVE, pins["stage14_protocol"]),
        (STAGE17_SOURCE_RELATIVE, pins["stage17_source"]),
        (STAGE17_PROTOCOL_RELATIVE, pins["stage17_protocol"]),
        (STAGE17_READER_SOURCE_RELATIVE, pins["stage17_reader_source"]),
        (STAGE17_READER_PROTOCOL_RELATIVE, pins["stage17_reader_protocol"]),
        (STAGE15_FAILED_SOURCE_RELATIVE, pins["stage15_failed_source"]),
        (STAGE15_FAILED_PROTOCOL_RELATIVE, pins["stage15_failed_protocol"]),
        (STAGE15_FAILURE_SOURCE_RELATIVE, pins["stage15_failure_source"]),
        (STAGE15_FAILURE_PROTOCOL_RELATIVE, pins["stage15_failure_protocol"]),
    ):
        _read_exact(relative, digest, document=False)
    source = _read_exact(source_audit.REPORT_RELATIVE,
                         pins["source_audit_report"], document=True)
    strict = _read_exact(strict_audit.REPORT_RELATIVE,
                         pins["strict_audit_report"], document=True)
    require(isinstance(source, dict) and isinstance(strict, dict),
            "the complete current V7 independence reports are absent")
    sources, natives = official.validate_v7_audits(
        source, strict,
        source_relative=source_audit.REPORT_RELATIVE,
        strict_relative=strict_audit.REPORT_RELATIVE,
        source_digest=pins["source_audit_report"],
    )
    failure = _read_exact(failure_recorder.REPORT_RELATIVE,
                          pins["official_v2_failure"], document=True)
    require(isinstance(failure, dict),
            "the genuine preserved first official Rust failure is missing")
    failure_recorder.validate_report(failure)
    locale = _read_exact(official.REPORT_RELATIVE,
                         pins["official_report"], document=True)
    require(isinstance(locale, Mapping),
            "the genuine official four-role result is missing")
    validate_official_document(locale, source, strict, pins)
    failed_raw = _read_exact(
        STAGE15_RAW_REFERENCE_RELATIVE,
        pins["stage15_raw_reference"],
        document=True,
    )
    incident = _read_exact(
        STAGE15_FAILURE_RELATIVE,
        pins["stage15_failure_report"],
        document=True,
    )
    validate_preserved_public_failure(incident, failed_raw, pins)
    reader = importlib.import_module(
        "tools.python_re_universal_public_oracle_stage17_evidence",
    )
    require(getattr(reader, "SOURCE_RELATIVE", None)
            == STAGE17_READER_SOURCE_RELATIVE
            and getattr(reader, "PROTOCOL_RELATIVE", None)
            == STAGE17_READER_PROTOCOL_RELATIVE
            and getattr(reader, "SCHEMA", None)
            == "rebar-python-re-public-contract-v17-bounded-evidence-v1"
            and getattr(reader, "MAX_EVIDENCE_BYTES", None) == 32 * 1024 * 1024
            and callable(getattr(reader, "read_exact_evidence", None))
            and callable(getattr(reader, "validate_v17_evidence", None)),
            "the one frozen exact-path Stage17 evidence reader was substituted")
    rebound = reader.validate_v17_evidence()
    require(isinstance(rebound, Mapping)
            and rebound.get("schema") == reader.SCHEMA
            and rebound.get("status") == "PASS"
            and rebound.get("result") == "PASS"
            and rebound.get("reference_sha256") == pins["stage17_reference"]
            and rebound.get("all_candidates_sha256") == pins["stage17_all"]
            and rebound.get("reference_bytes") == 11_556_111
            and rebound.get("all_candidates_bytes") == 20_220_593
            and rebound.get("max_evidence_bytes") == 32 * 1024 * 1024
            and rebound.get("benchmark_or_timing_executed") is False
            and rebound.get("performance_fixtures_read") == 0
            and rebound.get("holdout_cases_read") == 0
            and rebound.get("performance") == "NOT MEASURED",
            "the full durable 32 MiB Stage17 evidence reader omitted real rows")
    experiments: dict[str, dict[str, Any]] = {}
    for label in ("stage14", "stage17"):
        spec = _stage_spec(label)
        if label == "stage17":
            reference = rebound.get("reference")
            all_candidates = rebound.get("all_candidates")
            require(reference.get("current_provenance")
                    == rebound.get("current_provenance")
                    if isinstance(reference, Mapping) else False,
                    "the authentic Stage17 shared reader changed current engines")
        else:
            reference = _read_exact(spec["reference"],
                                    pins[label + "_reference"], document=True)
            all_candidates = _read_exact(spec["all"],
                                         pins[label + "_all"], document=True)
        require(isinstance(reference, Mapping)
                and isinstance(all_candidates, Mapping),
                "the genuine " + label + " evidence is missing")
        validate_public_experiment(label, reference, all_candidates, pins)
        module_name = str(spec["source"])[:-3].replace("/", ".")
        producer = importlib.import_module(module_name)
        require(getattr(producer, "SCHEMA", None) == spec["schema"]
                and getattr(producer, "SOURCE_RELATIVE", None) == spec["source"]
                and getattr(producer, "PROTOCOL_RELATIVE", None) == spec["protocol"]
                and getattr(producer, "SELF_ORACLE_RELATIVE", None)
                == spec["reference"]
                and getattr(producer, "ALL_CANDIDATE_RELATIVE", None)
                == spec["all"]
                and getattr(producer, "EXPECTED_CASES", None) == spec["cases"]
                and getattr(producer, "SEED", None) == spec["seed"]
                and getattr(producer, "MATRIX_SHA256", None) == spec["matrix"],
                "the genuine frozen " + label + " producer was substituted")
        if label == "stage14":
            verified_reference = producer._validate_complete_self_oracle(
                dict(reference), dict(reference["current_provenance"]),
            )
            require(verified_reference == reference,
                    "the real stage14 producer rejected its complete Python streams")
            producer._validate_complete_candidate_report(
                dict(all_candidates),
                baseline=list(reference["baseline_records"]),
                second_reference=list(reference["second_records"]),
                provenance=dict(all_candidates["current_provenance"]),
                self_oracle_sha256=pins[label + "_reference"],
            )
        else:
            provenance = dict(reference["current_provenance"])
            verified_reference = producer._validate_complete_reference(
                dict(reference), provenance,
            )
            require(verified_reference == reference,
                    "the real durable stage17 rejected its complete Python streams")
            require(producer._durable_round_trip(dict(reference))[0] == reference,
                    "the full stage17 Python proof is not stable persisted JSON")
            verified_all = producer._validate_complete_all(
                dict(all_candidates),
                reference=dict(reference),
                provenance=provenance,
            )
            require(verified_all == all_candidates
                    and producer._durable_round_trip(dict(all_candidates))[0]
                    == all_candidates,
                    "the complete stage17 three-family proof is not durable JSON")
        experiments[label] = {
            "reference": reference,
            "all_candidates": all_candidates,
        }
    official.original.verify_production_fingerprints(sources, natives)
    require(original.campaign.GOAL_SHA256 == GOAL_SHA256,
            "the immutable full user objective was changed")
    return {
        "pins": pins,
        "source": source,
        "strict": strict,
        "official": locale,
        "failure": failure,
        "stage15_raw_reference": failed_raw,
        "stage15_failure": incident,
        "stage17_reader": rebound,
        "experiments": experiments,
        "sources": sources,
        "natives": natives,
    }


def static_family_audit(module: str, edge: dict[str, Any]) -> dict[str, Any]:
    state = _ACTIVE_PROVENANCE
    require(isinstance(state, dict),
            "the full V7 campaign selected a family without actual preflight")
    require(module in original.MODULES,
            "the full campaign selected an unowned regex engine")
    validate_edge_artifacts(state["source"], module, edge)
    official.original.verify_production_fingerprints(
        state["sources"], state["natives"],
    )
    controller = _actual_controller_digest()
    require(controller == state["controller_sha256"],
            "the actual source-bound full V7 controller changed")
    result = dict(state["source"])
    result["sealed_locale_provenance"] = {
        "schema": official.SCHEMA,
        "path": official.REPORT_RELATIVE,
        "sha256": state["pins"]["official_report"],
        "source_path": official.SOURCE_RELATIVE,
        "source_sha256": state["pins"]["official_source"],
        "protocol_path": official.PROTOCOL_RELATIVE,
        "protocol_sha256": state["pins"]["official_protocol"],
        "official_methods": OFFICIAL_METHODS,
        "candidate_family": original.family_for(module),
        "all_roles": ["re", "rust", "vm", "zig"],
    }
    result["sealed_no_delegation_provenance"] = {
        "schema": strict_audit.SCHEMA,
        "path": strict_audit.REPORT_RELATIVE,
        "sha256": state["pins"]["strict_audit_report"],
        "source_path": strict_audit.SOURCE_RELATIVE,
        "source_sha256": state["pins"]["strict_audit_source"],
        "native_match_repr_checks": 6,
        "standard_pickle_checks": 48,
    }
    for label in ("stage14", "stage17"):
        spec = _stage_spec(label)
        result["sealed_" + label + "_provenance"] = {
            "schema": str(spec["schema"]) + "-all-candidates",
            "path": spec["all"],
            "sha256": state["pins"][label + "_all"],
            "source_path": spec["source"],
            "source_sha256": state["pins"][label + "_source"],
            "protocol_path": spec["protocol"],
            "protocol_sha256": state["pins"][label + "_protocol"],
            "self_oracle_path": spec["reference"],
            "self_oracle_sha256": state["pins"][label + "_reference"],
            "cases_per_family": spec["cases"],
            "candidate_checks": spec["candidate_checks"],
            "seed": spec["seed"],
            "matrix_sha256": spec["matrix"],
            "full_candidate_records_preserved": True,
        }
    result["sealed_stage17_provenance"].update({
        "evidence_reader_source_path": STAGE17_READER_SOURCE_RELATIVE,
        "evidence_reader_source_sha256": (
            state["pins"]["stage17_reader_source"]
        ),
        "evidence_reader_protocol_path": STAGE17_READER_PROTOCOL_RELATIVE,
        "evidence_reader_protocol_sha256": (
            state["pins"]["stage17_reader_protocol"]
        ),
        "reference_bytes": 11_556_111,
        "all_candidate_bytes": 20_220_593,
        "max_evidence_bytes": 32 * 1024 * 1024,
        "reader_maximum_bytes": 32 * 1024 * 1024,
        "durable_reference_records_preserved": True,
    })
    result["sealed_stage15_failure_provenance"] = {
        "schema": public_failure.SCHEMA,
        "path": STAGE15_FAILURE_RELATIVE,
        "sha256": state["pins"]["stage15_failure_report"],
        "source_path": STAGE15_FAILURE_SOURCE_RELATIVE,
        "source_sha256": state["pins"]["stage15_failure_source"],
        "protocol_path": STAGE15_FAILURE_PROTOCOL_RELATIVE,
        "protocol_sha256": state["pins"]["stage15_failure_protocol"],
        "status": "FAIL",
        "result": "FAIL",
        "failed_source_path": STAGE15_FAILED_SOURCE_RELATIVE,
        "failed_source_sha256": state["pins"]["stage15_failed_source"],
        "failed_protocol_path": STAGE15_FAILED_PROTOCOL_RELATIVE,
        "failed_protocol_sha256": state["pins"]["stage15_failed_protocol"],
        "original_reference_path": STAGE15_RAW_REFERENCE_RELATIVE,
        "original_reference_sha256": state["pins"]["stage15_raw_reference"],
        "cases": STAGE17_CASES,
        "stdlib_checks": STAGE17_CASES * 2,
        "actual_reference_record_count": STAGE17_CASES * 2,
        "actual_reference_worker_count": 2,
        "candidate_processes": 0,
        "candidate_reports_created": 0,
        "candidate_status_by_family": {
            family: "NOT RUN" for family in CORE_FAMILIES
        },
        "declared_record_sha256": STAGE15_DECLARED_DIGEST,
        "actual_record_sha256": STAGE15_FROZEN_VALIDATOR_DIGEST,
        "durable_transport_record_sha256": STAGE15_DECLARED_DIGEST,
        "frozen_validator_record_sha256": STAGE15_FROZEN_VALIDATOR_DIGEST,
        "declared_digest_count": 4,
        "full_reference_records_preserved": True,
        "validator_rejection_count": 2,
        "historical": True,
        "qualifies_current_engines": False,
    }
    result["sealed_official_v2_failure"] = {
        "schema": failure_recorder.SCHEMA,
        "path": failure_recorder.REPORT_RELATIVE,
        "sha256": state["pins"]["official_v2_failure"],
        "status": "FAIL",
        "failed_role": "rust",
        "failed_method": "ReTests.test_match_repr",
        "historical": True,
        "qualifies_current_engines": False,
    }
    result["sealed_campaign_controller"] = {
        "postfinal_schema": SCHEMA,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": controller,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": state["protocol_sha256"],
        "historical_v5_source_path": HISTORICAL_V5_SOURCE_RELATIVE,
        "historical_v5_source_sha256": HISTORICAL_V5_SOURCE_SHA256,
        "historical_v5_qualifies_current_engines": False,
        "expected_complete_production_role_count": len(
            expected_edge_paths(original.family_for(module))
        ),
    }
    return result


def output_path(path: Path, module: str) -> Path:
    result = ancestor.ORIGINAL_OUTPUT_PATH(path, module)
    family = original.family_for(module)
    require(result.name
            == f"rust-v8-{family}-postfinal-locale-v7-sealed-campaign.json",
            "only the exact fresh exclusively created V7 family output is allowed")
    return result


def validate_report_structure(report: dict[str, Any], module: str) -> None:
    state = _ACTIVE_PROVENANCE
    require(isinstance(state, dict),
            "the full V7 correctness report escaped its genuine preflight")
    require(isinstance(report, dict)
            and report.get("schema") == original.SCHEMA
            and report.get("candidate") == module
            and report.get("pinned_cpython") == "3.14.6"
            and report.get("mode") == "sealed-practice-only"
            and report.get("passed") is True
            and report.get("holdout_accessed") is False
            and report.get("timing_performed") is False
            and report.get("performance") == "NOT MEASURED",
            "the genuine full 22-stage V7 campaign failed or accessed performance")
    digest = _actual_controller_digest()
    require(digest == state["controller_sha256"],
            "the frozen full V7 correctness controller was replaced")
    fields = {
        "postfinal_schema": SCHEMA,
        "controller_source_path": SOURCE_RELATIVE,
        "controller_source_sha256": digest,
        "controller_protocol_path": PROTOCOL_RELATIVE,
        "controller_protocol_sha256": state["protocol_sha256"],
        "ancestor_source_path": HISTORICAL_V5_SOURCE_RELATIVE,
        "ancestor_source_sha256": HISTORICAL_V5_SOURCE_SHA256,
        "historical_ancestor_qualifies_current_engines": False,
    }
    existing = set(fields) & set(report)
    if not state["armed"]:
        require(not existing,
                "the actual complete V7 report arrived with counterfeit source fields")
        report.update(fields)
        state["armed"] = True
    else:
        require(existing == set(fields),
                "the restored actual V7 report dropped its source provenance")
    require(all(report.get(name) == value for name, value in fields.items()),
            "the actual complete V7 controller or protocol changed during execution")
    goal = report.get("goal")
    require(isinstance(goal, Mapping)
            and goal.get("passed") is True
            and goal.get("actual_sha256") == GOAL_SHA256
            and goal.get("expected_sha256") == GOAL_SHA256,
            "the complete V7 campaign does not bind the immutable user objective")
    excluded = report.get("excluded_steps")
    require(isinstance(excluded, list)
            and len(excluded) == len(original.EXCLUDED_NAMES)
            and {item.get("name") for item in excluded
                 if isinstance(item, Mapping)}
            == frozenset(original.EXCLUDED_NAMES),
            "the full correctness campaign removed a performance exclusion")
    steps = report.get("steps")
    require(isinstance(steps, list)
            and len(steps) == REQUIRED_STEP_COUNT
            and report.get("required_correctness_step_count") == REQUIRED_STEP_COUNT,
            "the actual complete campaign omitted one of the 22 frozen stages")
    names: set[str] = set()
    for step in steps:
        require(isinstance(step, Mapping)
                and step.get("passed") is True
                and step.get("status") in (None, "passed")
                and step.get("candidate") == module,
                "an actual frozen correctness stage failed or changed engine")
        name = step.get("name")
        evidence = step.get("evidence")
        require(isinstance(name, str)
                and bool(name)
                and name not in names
                and isinstance(evidence, dict)
                and step.get("evidence_sha256") == original.digest_value(evidence)
                and step.get("holdout_accessed") is False
                and step.get("timing_performed") is False
                and step.get("performance") == "NOT MEASURED",
                "an actual frozen stage concealed evidence, failed, or sampled time")
        names.add(name)
    require(original.REQUIRED_NAMES <= names,
            "the full V7 campaign omitted a required frozen correctness obligation")
    denominators = {
        "frozen-correctness-v2": 8244,
        "frozen-correctness-v3": 44084,
        "official-cpython-tests": OFFICIAL_METHODS,
        "upstream-public-surface": 190,
        "replacement-and-callback-adversarial": 8862,
        "deep-replacement-and-callback-adversarial": 11266,
        "isolated-crash-and-resource-safety": 254,
        "isolated-depth-and-overflow-safety": 348,
        "full-unicode-plane": UNICODE_CASES,
        "frozen-cross-family-observability": OBSERVABILITY_CASES,
    }
    for name, count in denominators.items():
        row = next((item for item in steps if item["name"] == name), None)
        require(isinstance(row, Mapping)
                and row.get("expected_checks") == count,
                "the full V7 frozen correctness denominator changed: " + name)
    official_step = next(item for item in steps
                         if item["name"] == "official-cpython-tests")
    observed_official = official_step["evidence"]
    require(observed_official.get("module") == module
            and observed_official.get("methods") == OFFICIAL_METHODS
            and observed_official.get("passed") == OFFICIAL_METHODS
            and observed_official.get("skipped") == 0,
            "the live genuine-private-locale official campaign stage failed")
    unicode = next(item for item in steps if item["name"] == "full-unicode-plane")
    require(unicode["evidence"].get("correctness_checks") == UNICODE_CASES,
            "the actual full-plane campaign dropped a Unicode property observation")
    for name in (
        "independent-native-boundary-self-oracle",
        "independent-native-boundary-integrity",
        "independent-native-boundary-poison",
        "independent-native-boundary-compatibility",
    ):
        require(name in names,
                "the complete campaign dropped a real native safety stage: " + name)
    evidence = next(item for item in steps
                    if item["name"] == "from-scratch-static-audit")["evidence"]
    locale = evidence.get("sealed_locale_provenance")
    strict = evidence.get("sealed_no_delegation_provenance")
    failure = evidence.get("sealed_official_v2_failure")
    controller = evidence.get("sealed_campaign_controller")
    require(evidence.get("postfinal_schema") == source_audit.SCHEMA
            and evidence.get("audit_source_sha256")
            == state["pins"]["source_audit_source"]
            and isinstance(locale, Mapping)
            and locale.get("schema") == official.SCHEMA
            and locale.get("sha256") == state["pins"]["official_report"]
            and isinstance(strict, Mapping)
            and strict.get("schema") == strict_audit.SCHEMA
            and strict.get("sha256") == state["pins"]["strict_audit_report"]
            and strict.get("native_match_repr_checks") == 6
            and strict.get("standard_pickle_checks") == 48
            and isinstance(failure, Mapping)
            and failure.get("sha256") == state["pins"]["official_v2_failure"]
            and failure.get("status") == "FAIL"
            and failure.get("qualifies_current_engines") is False
            and isinstance(controller, Mapping)
            and controller.get("postfinal_schema") == SCHEMA
            and controller.get("source_sha256") == digest
            and controller.get("protocol_sha256") == state["protocol_sha256"]
            and controller.get("historical_v5_qualifies_current_engines") is False,
            "the complete V7 campaign omitted a genuine fresh proof or prior failure")
    for label in ("stage14", "stage17"):
        spec = _stage_spec(label)
        proof = evidence.get("sealed_" + label + "_provenance")
        require(isinstance(proof, Mapping)
                and proof.get("schema") == spec["schema"] + "-all-candidates"
                and proof.get("path") == spec["all"]
                and proof.get("sha256") == state["pins"][label + "_all"]
                and proof.get("source_path") == spec["source"]
                and proof.get("source_sha256")
                == state["pins"][label + "_source"]
                and proof.get("protocol_path") == spec["protocol"]
                and proof.get("protocol_sha256")
                == state["pins"][label + "_protocol"]
                and proof.get("self_oracle_path") == spec["reference"]
                and proof.get("self_oracle_sha256")
                == state["pins"][label + "_reference"]
                and proof.get("cases_per_family") == spec["cases"]
                and proof.get("candidate_checks") == spec["candidate_checks"]
                and proof.get("full_candidate_records_preserved") is True
                and proof.get("seed") == spec["seed"]
                and proof.get("matrix_sha256") == spec["matrix"],
                "the complete campaign dropped a frozen " + label + " proof")
    rebound = evidence["sealed_stage17_provenance"]
    require(rebound.get("evidence_reader_source_path")
            == STAGE17_READER_SOURCE_RELATIVE
            and rebound.get("evidence_reader_source_sha256")
            == state["pins"]["stage17_reader_source"]
            and rebound.get("evidence_reader_protocol_path")
            == STAGE17_READER_PROTOCOL_RELATIVE
            and rebound.get("evidence_reader_protocol_sha256")
            == state["pins"]["stage17_reader_protocol"]
            and rebound.get("reference_bytes") == 11_556_111
            and rebound.get("all_candidate_bytes") == 20_220_593
            and rebound.get("max_evidence_bytes") == 32 * 1024 * 1024
            and rebound.get("reader_maximum_bytes") == 32 * 1024 * 1024
            and rebound.get("durable_reference_records_preserved") is True,
            "the complete durable 10,752-case proof lost its source-frozen reader")
    incident = evidence.get("sealed_stage15_failure_provenance")
    require(isinstance(incident, Mapping)
            and incident.get("schema") == public_failure.SCHEMA
            and incident.get("path") == STAGE15_FAILURE_RELATIVE
            and incident.get("sha256")
            == state["pins"]["stage15_failure_report"]
            and incident.get("source_path") == STAGE15_FAILURE_SOURCE_RELATIVE
            and incident.get("source_sha256")
            == state["pins"]["stage15_failure_source"]
            and incident.get("protocol_path")
            == STAGE15_FAILURE_PROTOCOL_RELATIVE
            and incident.get("protocol_sha256")
            == state["pins"]["stage15_failure_protocol"]
            and incident.get("status") == "FAIL"
            and incident.get("result") == "FAIL"
            and incident.get("failed_source_path")
            == STAGE15_FAILED_SOURCE_RELATIVE
            and incident.get("failed_source_sha256")
            == state["pins"]["stage15_failed_source"]
            and incident.get("failed_protocol_path")
            == STAGE15_FAILED_PROTOCOL_RELATIVE
            and incident.get("failed_protocol_sha256")
            == state["pins"]["stage15_failed_protocol"]
            and incident.get("original_reference_path")
            == STAGE15_RAW_REFERENCE_RELATIVE
            and incident.get("original_reference_sha256")
            == state["pins"]["stage15_raw_reference"]
            and incident.get("cases") == STAGE17_CASES
            and incident.get("stdlib_checks") == STAGE17_CASES * 2
            and incident.get("actual_reference_record_count")
            == STAGE17_CASES * 2
            and incident.get("actual_reference_worker_count") == 2
            and incident.get("candidate_processes") == 0
            and incident.get("candidate_reports_created") == 0
            and incident.get("candidate_status_by_family")
            == {family: "NOT RUN" for family in CORE_FAMILIES}
            and incident.get("declared_digest_count") == 4
            and incident.get("validator_rejection_count") == 2
            and incident.get("declared_record_sha256")
            == STAGE15_DECLARED_DIGEST
            and incident.get("durable_transport_record_sha256")
            == STAGE15_DECLARED_DIGEST
            and incident.get("actual_record_sha256")
            == STAGE15_FROZEN_VALIDATOR_DIGEST
            and incident.get("frozen_validator_record_sha256")
            == STAGE15_FROZEN_VALIDATOR_DIGEST
            and incident.get("full_reference_records_preserved") is True
            and incident.get("historical") is True
            and incident.get("qualifies_current_engines") is False,
            "the complete V7 campaign concealed or qualified the genuine V15 failure")
    edge = report.get("edge_oracle")
    deep = report.get("deep_proof")
    require(isinstance(edge, dict)
            and edge.get("module") == module
            and edge.get("checks") == EDGE_CHECKS
            and edge.get("category_count") == EDGE_CATEGORIES
            and edge.get("failed") == 0,
            "the complete frozen edge checks changed or contain a real mismatch")
    validate_edge_artifacts(state["source"], module, edge)
    require(isinstance(deep, dict)
            and deep.get("candidate_module") == module
            and deep.get("checks") == DEEP_CASES
            and deep.get("seed") == DEEP_SEED
            and deep.get("public_mismatches") == 0
            and report.get("native_artifacts") == edge.get("production_artifacts")
            and deep.get("native_artifacts") == edge.get("production_artifacts"),
            "the complete deep frozen public proof changed, failed, or swapped natives")


@contextmanager
def current_v7_campaign() -> Iterator[None]:
    global _ACTIVE_PROVENANCE
    require(_ACTIVE_PROVENANCE is None,
            "another source-bound complete V7 family campaign is already running")
    state = _preflight()
    state["controller_sha256"] = _actual_controller_digest()
    protocol, _ = core.bounded_file(
        PROTOCOL_PATH, maximum=source_audit.MAX_SOURCE_BYTES,
        label="actual frozen complete V7 correctness campaign protocol",
    )
    require(core.valid_sha256(protocol),
            "the actual complete V7 campaign protocol is not frozen")
    state["protocol_sha256"] = protocol
    with tempfile.TemporaryDirectory(
        prefix="rebar-v7-full-campaign-real-locale-", dir="/tmp"
    ) as private:
        locale_root = Path(private)
        compiled = official.original.build_private_locales(locale_root)
        locale_reference = official.original.verify_locale_reference(locale_root)
        require(compiled.get("genuine") is True
                and locale_reference.get("status") == "PASS"
                and locale_reference.get("compiled_locale_switch") is True,
                "the full V7 campaign could not independently prove real locales")
        previous_locpath = os.environ.get("LOCPATH")
        original_expected = ancestor.EXPECTED_LOCPATH
        with ancestor.current_locale_campaign():
            require(original.static_family_audit is ancestor.static_family_audit
                    and original.output_path is ancestor.output_path
                    and original.validate_report_structure
                    is ancestor.validate_report_structure,
                    "the immutable original 22-stage provider was substituted")
            ancestor.EXPECTED_LOCPATH = str(locale_root)
            os.environ["LOCPATH"] = str(locale_root)
            state["armed"] = False
            _ACTIVE_PROVENANCE = state
            original.static_family_audit = static_family_audit
            original.output_path = output_path
            original.validate_report_structure = validate_report_structure
            try:
                yield
            finally:
                original.validate_report_structure = ancestor.validate_report_structure
                original.output_path = ancestor.output_path
                original.static_family_audit = ancestor.static_family_audit
                _ACTIVE_PROVENANCE = None
                ancestor.EXPECTED_LOCPATH = original_expected
                if previous_locpath is None:
                    os.environ.pop("LOCPATH", None)
                else:
                    os.environ["LOCPATH"] = previous_locpath


def _synthetic_pins() -> dict[str, str]:
    return {
        name: hardened._synthetic_digest("complete-v7-campaign:" + name)
        for name in (
            "source_audit_source", "source_audit_report",
            "strict_audit_source", "strict_audit_report",
            "official_source", "official_protocol", "official_report",
            "official_v2_failure",
            "stage14_source", "stage14_protocol", "stage14_reference",
            "stage14_all",
            "stage17_source", "stage17_protocol", "stage17_reference",
            "stage17_all", "stage17_reader_source", "stage17_reader_protocol",
            "stage15_failed_source", "stage15_failed_protocol",
            "stage15_raw_reference", "stage15_failure_source",
            "stage15_failure_protocol", "stage15_failure_report",
        )
    }


def _synthetic_guard(family: str) -> dict[str, Any]:
    return {
        "family": family,
        "enabled": True,
        "stdlib_re_blocked": True,
        "cpython_sre_blocked": True,
        "third_party_regex_blocked": True,
        "cross_family_blocked": True,
        "foreign_dynamic_libraries_blocked": True,
        "native_loader_aliases_blocked": list(
            strict_audit.NATIVE_LOADER_ALIASES
        ),
    }


def _synthetic_experiment(
    label: str, pins: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    spec = _stage_spec(label)
    records = [{
        "id": "synthetic-" + label + "-case-" + str(index),
        "synthetic_only": True,
    } for index in range(int(spec["cases"]))]
    digest = original.digest_value(records)
    natives = {
        family: {
            str(path): hardened._synthetic_digest(
                "complete-v7:" + family + ":" + str(path)
            )
            for path in source_audit.source_v6.OWNED_NATIVE_PATHS[family].values()
        }
        for family in CORE_FAMILIES
    }
    provenance: dict[str, Any] = {
        "source_path": spec["source"],
        "source_sha256": pins[label + "_source"],
        "protocol_path": spec["protocol"],
        "protocol_sha256": pins[label + "_protocol"],
        "seed": spec["seed"],
        "seed_domain": spec["seed_domain"],
        "matrix_sha256": spec["matrix"],
        "base_audit_source_path": source_audit.SOURCE_RELATIVE,
        "base_audit_source_sha256": pins["source_audit_source"],
        "base_audit_path": source_audit.REPORT_RELATIVE,
        "base_audit_sha256": pins["source_audit_report"],
        "strict_audit_source_path": strict_audit.SOURCE_RELATIVE,
        "strict_audit_source_sha256": pins["strict_audit_source"],
        "strict_audit_path": strict_audit.REPORT_RELATIVE,
        "strict_audit_sha256": pins["strict_audit_report"],
        "native_source_count": 12,
        "native_binary_count": 5,
        "verified_standard_pickle_count": 48,
        "verified_match_repr_count": 6,
        "native_sha256_by_family": natives,
    }
    if label == "stage14":
        provenance.update({
            "official_v3_source_path": official.SOURCE_RELATIVE,
            "official_v3_source_sha256": pins["official_source"],
            "official_v3_protocol_path": official.PROTOCOL_RELATIVE,
            "official_v3_protocol_sha256": pins["official_protocol"],
            "official_v3_report_path": official.REPORT_RELATIVE,
            "official_v3_report_sha256": pins["official_report"],
            "official_v3_status": "PASS",
            "official_v3_completed_roles": ["re", *CORE_FAMILIES],
            "official_v3_methods_per_role": OFFICIAL_METHODS,
            "official_v3_total_method_checks": OFFICIAL_METHODS * 4,
            "official_v3_failed_methods": 0,
            "official_v3_skipped_methods": 0,
            "official_v3_crashes": 0,
            "official_v3_v2_failure_preserved": True,
            "official_v2_failure_path": failure_recorder.REPORT_RELATIVE,
            "official_v2_failure_sha256": pins["official_v2_failure"],
            "official_v2_failure_status": "FAIL",
            "official_v2_failed_role": "rust",
            "official_v2_failed_method": "ReTests.test_match_repr",
            "official_v2_failure_qualifies_current_sources": False,
        })
    else:
        provenance.update({
            "observation_domain": spec["seed_domain"],
            "official_source_path": official.SOURCE_RELATIVE,
            "official_source_sha256": pins["official_source"],
            "official_protocol_path": official.PROTOCOL_RELATIVE,
            "official_protocol_sha256": pins["official_protocol"],
            "official_report_path": official.REPORT_RELATIVE,
            "official_report_sha256": pins["official_report"],
            "official_methods_per_role": OFFICIAL_METHODS,
            "official_role_count": 4,
            "official_skipped": 0,
            "official_v2_failure_path": failure_recorder.REPORT_RELATIVE,
            "official_v2_failure_sha256": pins["official_v2_failure"],
            "official_v2_failure_historical": True,
            "stage14_source_path": STAGE14_SOURCE_RELATIVE,
            "stage14_source_sha256": pins["stage14_source"],
            "stage14_protocol_path": STAGE14_PROTOCOL_RELATIVE,
            "stage14_protocol_sha256": pins["stage14_protocol"],
            "stage14_self_oracle_path": STAGE14_REFERENCE_RELATIVE,
            "stage14_self_oracle_sha256": pins["stage14_reference"],
            "stage14_all_candidate_path": STAGE14_ALL_RELATIVE,
            "stage14_all_candidate_sha256": pins["stage14_all"],
            "stage14_cases_per_candidate": STAGE14_CASES,
            "stage14_candidate_checks": STAGE14_CANDIDATE_CHECKS,
            "historical_stage10_only": True,
            "stage15_source_path": STAGE15_FAILED_SOURCE_RELATIVE,
            "stage15_source_sha256": pins["stage15_failed_source"],
            "stage15_protocol_path": STAGE15_FAILED_PROTOCOL_RELATIVE,
            "stage15_protocol_sha256": pins["stage15_failed_protocol"],
            "stage15_raw_reference_path": STAGE15_RAW_REFERENCE_RELATIVE,
            "stage15_raw_reference_sha256": pins["stage15_raw_reference"],
            "stage15_reference_status": "FALSIFIED",
            "stage15_declared_record_sha256": STAGE15_DECLARED_DIGEST,
            "stage15_actual_record_sha256": STAGE15_FROZEN_VALIDATOR_DIGEST,
            "stage15_durable_transport_record_sha256": STAGE15_DECLARED_DIGEST,
            "stage15_frozen_validator_record_sha256": (
                STAGE15_FROZEN_VALIDATOR_DIGEST
            ),
            "stage15_failure_source_path": STAGE15_FAILURE_SOURCE_RELATIVE,
            "stage15_failure_source_sha256": pins["stage15_failure_source"],
            "stage15_failure_protocol_path": STAGE15_FAILURE_PROTOCOL_RELATIVE,
            "stage15_failure_protocol_sha256": pins["stage15_failure_protocol"],
            "stage15_failure_path": STAGE15_FAILURE_RELATIVE,
            "stage15_failure_sha256": pins["stage15_failure_report"],
            "stage15_reference_record_count": STAGE17_CASES * 2,
            "stage15_candidate_runs": 0,
            "durable_json_canonicalization": "frozen-json-ascii-sort-keys-v17",
            "durable_reference_hash_domain": (
                "persisted-normalized-json-once-v17"
            ),
        })
    shared = {
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": spec["source"],
        "source_sha256": pins[label + "_source"],
        "protocol_path": spec["protocol"],
        "protocol_sha256": pins[label + "_protocol"],
        "seed": spec["seed"],
        "seed_domain": spec["seed_domain"],
        "matrix_sha256": spec["matrix"],
        "cohorts": len(spec["cohorts"]),
        "cohort_cases": dict(spec["cohorts"]),
        "current_provenance": provenance,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    reference = {
        **copy.deepcopy(shared),
        "schema": str(spec["schema"]) + "-self-oracle",
        "cases": spec["cases"],
        "stdlib_checks": int(spec["cases"]) * 2,
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "baseline_records": records,
        "second_records": copy.deepcopy(records),
        "baseline_record_sha256": digest,
        "second_record_sha256": digest,
    }
    outcomes = {
        family: {
            "candidate": family,
            "module": "candidates." + family + "_candidate",
            "status": "PASS",
            "cases": spec["cases"],
            "cohort_cases": dict(spec["cohorts"]),
            "records": records,
            "record_sha256": digest,
            "mismatches": 0,
            "failure_records": [],
            "failures_recorded": 0,
            "native_binary_sha256": natives[family],
            "guard": _synthetic_guard(family),
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        for family in CORE_FAMILIES
    }
    all_candidates = {
        **copy.deepcopy(shared),
        "schema": str(spec["schema"]) + "-all-candidates",
        "selected": "all",
        "selected_candidates": list(CORE_FAMILIES),
        "completed_candidates": list(CORE_FAMILIES),
        "comparison_complete": True,
        "cases_per_candidate": spec["cases"],
        "candidate_checks": spec["candidate_checks"],
        "self_oracle_path": spec["reference"],
        "self_oracle_sha256": pins[label + "_reference"],
        "baseline_record_sha256": digest,
        "baseline_records": records,
        "second_reference_records": copy.deepcopy(records),
        "candidate_cross_delegation": False,
        "mismatches": 0,
        "candidate_reports": outcomes,
    }
    if label == "stage17":
        all_candidates["external_regex_packages"] = 0
    return reference, all_candidates


def self_test() -> dict[str, Any]:
    controls: list[dict[str, Any]] = []

    def check(name: str, value: Any) -> None:
        controls.append({"id": name, "passed": bool(value)})

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (AssertionError, TypeError, ValueError, KeyError, OSError):
            check(name, True)
        else:
            check(name, False)

    with (
        mock.patch.object(subprocess, "Popen",
                          side_effect=AssertionError(
                              "full V7 synthetic checks cannot launch a worker"
                          )) as workers,
        mock.patch.object(source_audit, "audit",
                          side_effect=AssertionError(
                              "full V7 synthetic checks cannot run a source audit"
                          )) as source_runs,
        mock.patch.object(strict_audit, "run_audit",
                          side_effect=AssertionError(
                              "full V7 synthetic checks cannot run a strict audit"
                          )) as strict_runs,
        mock.patch.object(core, "bounded_file",
                          side_effect=AssertionError(
                              "full V7 synthetic checks cannot read production"
                          )) as files,
        mock.patch.object(tempfile, "TemporaryDirectory",
                          side_effect=AssertionError(
                              "full V7 synthetic checks cannot create a locale"
                          )) as locales,
    ):
        inherited = historical.self_test()
        require(isinstance(inherited, Mapping)
                and inherited.get("schema") == historical.SELF_TEST_SCHEMA
                and inherited.get("passed") is True
                and inherited.get("poison_control_count", 0) >= 120
                and inherited.get("inherited_v4_control_count", 0) >= 93
                and inherited.get("inherited_hardened_control_count", 0) >= 43
                and inherited.get("inherited_campaign_control_count", 0) >= 46
                and inherited.get("candidate_processes_started") == 0
                and inherited.get("production_audits_run") == 0
                and inherited.get("production_report_reads") == 0,
                "the immutable original complete 22-stage malicious controls failed")
        for row in inherited["poison_controls"]:
            check("v5:" + row["id"], row["passed"] is True)
        check("preserve-all-actual-22-stage-independent-family-plans",
              all(value == REQUIRED_STEP_COUNT for value
                  in inherited["actual_planned_step_counts"].values()))
        check("preserve-complete-full-unicode-plane-denominator",
              UNICODE_CASES == 4_494_555)
        check("preserve-complete-original-native-edge-denominator",
              EDGE_CHECKS == original.contract.EDGE_CHECKS
              and EDGE_CATEGORIES == original.contract.EDGE_CATEGORIES)
        check("preserve-exact-frozen-property-fuzz-seed",
              DEEP_SEED == original.contract.FROZEN_SEED
              and DEEP_CASES == original.contract.FROZEN_CASES
              and DEEP_SEEDED_CASES == original.contract.FROZEN_SEEDED_CASES)
        check("preserve-full-cross-family-observability-seed",
              OBSERVABILITY_SEED == original.OBSERVABILITY_SEED
              and OBSERVABILITY_CASES == 479)
        check("preserve-four-real-official-146-method-runs",
              OFFICIAL_METHODS == 146)
        check("pin-actual-genuine-v7-source-controller",
              BASE_SOURCE_SHA256 == official.V7_BASE_SOURCE_SHA256)
        check("pin-actual-genuine-v7-source-report",
              BASE_REPORT_SHA256 == official.V7_BASE_REPORT_SHA256)
        check("pin-actual-genuine-v7-strict-controller",
              STRICT_SOURCE_SHA256 == official.V7_STRICT_SOURCE_SHA256)
        check("pin-actual-genuine-v7-strict-report",
              STRICT_REPORT_SHA256 == official.V7_STRICT_REPORT_SHA256)
        check("pin-actual-genuine-v3-official-four-role-result",
              core.valid_sha256(OFFICIAL_SOURCE_SHA256)
              and core.valid_sha256(OFFICIAL_PROTOCOL_SHA256)
              and core.valid_sha256(OFFICIAL_REPORT_SHA256))
        check("preserve-actual-failed-official-v2-result",
              OFFICIAL_V2_FAILURE_SHA256 == official.V2_FAILURE_SHA256)
        check("pin-actual-corrected-stage14-full-reference-and-three-families",
              all(core.valid_sha256(item) for item in (
                  STAGE14_SOURCE_SHA256, STAGE14_PROTOCOL_SHA256,
                  STAGE14_REFERENCE_SHA256, STAGE14_ALL_SHA256,
              )))
        check("pin-actual-durable-stage17-full-reference-and-three-families",
              all(core.valid_sha256(item) for item in (
                  STAGE17_SOURCE_SHA256, STAGE17_PROTOCOL_SHA256,
                  STAGE17_REFERENCE_SHA256, STAGE17_ALL_SHA256,
              )))
        check("preserve-genuine-falsified-first-stage15-without-candidate-pass",
              STAGE15_FAILURE_SOURCE_SHA256
              == "07a522f263cd9e0baad022f91988d034b3cde3013b143bd1f9a77174fa0b58b6"
              and STAGE15_FAILURE_PROTOCOL_SHA256
              == "6aa2b8e5bcd6867af60c570d19508a67e0094eedca4ab815266e0f91e2c83b03"
              and STAGE15_FAILURE_SHA256
              == "cb71e1a44549c7c76c3bf08900e6107d2b49e789e5002afc725d1e9df0c92880"
              and STAGE15_RAW_REFERENCE_SHA256
              == "755cb818f59259bb5adb05a93782afc3eef12e001c41a976ba4b9258ae54ac01"
              and STAGE15_DECLARED_DIGEST != STAGE15_FROZEN_VALIDATOR_DIGEST)
        synthetic_pins = _synthetic_pins()
        for key in (
            "stage17_reader_source", "stage17_reader_protocol",
            "stage17_source", "stage17_protocol", "stage17_reference",
            "stage17_all", "stage15_failure_source", "stage15_failure_protocol",
            "stage15_failure_report", "stage15_raw_reference",
        ):
            reject("reject-full-campaign-before-real-proof/" + key,
                   lambda name=key: _pins({**synthetic_pins, name: None}))
            reject("reject-substituted-real-proof/" + key,
                   lambda name=key: _pins({
                       **synthetic_pins,
                       name: synthetic_pins["official_report"],
                   }))
        with mock.patch.object(
            sys.modules[__name__],
            "_pins",
            side_effect=AssertionError(
                "synthetic full-campaign controls cannot authenticate real evidence"
            ),
        ):
            reject("reject-real-preflight-before-all-proofs-with-zero-file-reads",
                   _preflight)
        pins = _pins(synthetic_pins)
        for label in ("stage14", "stage17"):
            reference, candidates = _synthetic_experiment(label, pins)
            validate_public_experiment(label, reference, candidates, pins)
            check("accept-complete-double-reference-and-three-family-records:" + label,
                  True)

            def poison_reference(name: str, mutation: Any) -> None:
                def attempt() -> None:
                    wrong = copy.deepcopy(reference)
                    mutation(wrong)
                    validate_public_experiment(label, wrong, candidates, pins)

                reject(name + ":" + label, attempt)

            def poison_all(name: str, mutation: Any) -> None:
                def attempt() -> None:
                    wrong = copy.deepcopy(candidates)
                    mutation(wrong)
                    validate_public_experiment(label, reference, wrong, pins)

                reject(name + ":" + label, attempt)

            for name, mutation in (
                ("reject-missing-dual-stdlib-observation",
                 lambda item: item.update(stdlib_checks=item["stdlib_checks"] - 1)),
                ("reject-reference-public-mismatch",
                 lambda item: item.update(mismatches=1)),
                ("reject-reference-candidate-import",
                 lambda item: item.update(candidate_imports=1)),
                ("reject-missing-reference-record",
                 lambda item: item["baseline_records"].pop()),
                ("reject-missing-full-self-oracle-second-reference-record",
                 lambda item: item["second_records"].pop()),
                ("reject-tampered-real-second-reference-record",
                 lambda item: item["second_records"][0].update(
                     synthetic_only=False
                 )),
                ("reject-reference-forged-baseline-fingerprint",
                 lambda item: item.update(baseline_record_sha256="0" * 64)),
                ("reject-reference-forged-second-fingerprint",
                 lambda item: item.update(second_record_sha256="0" * 64)),
                ("reject-reference-mutated-original-seed",
                 lambda item: item.update(seed=0)),
                ("reject-reference-holdout-access",
                 lambda item: item.update(holdout_cases_read=1)),
            ):
                poison_reference(name, mutation)
            for name, mutation in (
                ("reject-incomplete-three-family-denominator",
                 lambda item: item.update(
                     candidate_checks=item["candidate_checks"] - 1
                 )),
                ("reject-dropped-independent-family",
                 lambda item: item["candidate_reports"].pop("zig")),
                ("reject-cross-family-delegation",
                 lambda item: item.update(candidate_cross_delegation=True)),
                ("reject-hidden-real-public-mismatch",
                 lambda item: item["candidate_reports"]["rust"].update(
                     mismatches=1
                 )),
                ("reject-missing-actual-candidate-record",
                 lambda item: item["candidate_reports"]["vm"]["records"].pop()),
                ("reject-cross-family-native-module",
                 lambda item: item["candidate_reports"]["zig"].update(
                     module="candidates.rust_candidate"
                 )),
                ("reject-disabled-native-guard",
                 lambda item: item["candidate_reports"]["rust"]["guard"].update(
                     stdlib_re_blocked=False
                 )),
                ("reject-omitted-native-loader-guard",
                 lambda item: item["candidate_reports"]["vm"]["guard"].update(
                     native_loader_aliases_blocked=[]
                 )),
                ("reject-forged-owned-native-fingerprint",
                 lambda item: item["candidate_reports"]["zig"].update(
                     native_binary_sha256={}
                 )),
                ("reject-hidden-performance-sampling",
                 lambda item: item.update(benchmark_or_timing_executed=True)),
                ("reject-unpublished-reference-digest",
                 lambda item: item.update(self_oracle_sha256="0" * 64)),
                ("reject-missing-full-baseline-record",
                 lambda item: item["baseline_records"].pop()),
                ("reject-missing-full-final-second-reference-record",
                 lambda item: item["second_reference_records"].pop()),
                ("reject-tampered-full-second-reference-record",
                 lambda item: item["second_reference_records"][0].update(
                     synthetic_only=False
                 )),
            ):
                poison_all(name, mutation)
            if label == "stage17":
                poison_all(
                    "reject-external-regex-package",
                    lambda item: item.update(external_regex_packages=1),
                )
        failure_rows, failure_provenance, failure_expected = (
            public_failure._synthetic_failure()
        )
        failure_document = public_failure.build_report(
            failure_rows,
            failure_provenance,
            source_sha256=hardened._synthetic_digest(
                "synthetic-v7-preserved-stage15-failure-source"
            ),
            protocol_sha256=hardened._synthetic_digest(
                "synthetic-v7-preserved-stage15-failure-protocol"
            ),
            raw_sha256=failure_expected["raw"],
            _expected_digests=failure_expected,
        )
        check("retain-complete-dual-reference-false-stage15-history",
              public_failure.validate_report(
                  failure_document,
                  _expected_digests=failure_expected,
              ) is failure_document)
        for label, key, value in (
            ("false-stage15-success", "status", "PASS"),
            ("concealed-stage15-failure-result", "result", "PASS"),
            ("invented-stage15-candidate-run", "candidate_processes", 1),
            ("invented-stage15-candidate-report", "candidate_reports_created", 1),
            ("hidden-stage15-durable-transport",
             "durable_transport_record_sha256", "0" * 64),
            ("hidden-stage15-frozen-validator",
             "frozen_validator_record_sha256", "0" * 64),
            ("weakened-original-stage15-reference", "actual_reference_record_count", 1),
        ):
            poisoned = {**failure_document, key: value}
            reject("reject-" + label,
                   lambda wrong=poisoned: public_failure.validate_report(
                       wrong,
                       _expected_digests=failure_expected,
                   ))
        for family, denominator in (("rust", 5), ("vm", 3), ("zig", 5)):
            module = "candidates." + family + "_candidate"
            source, edge = historical._synthetic_edge(module)
            validate_edge_artifacts(source, module, edge)
            check("preserve-complete-owned-native-edge-roles:" + family,
                  len(expected_edge_paths(family)) == denominator)

            def omit_native() -> None:
                changed = copy.deepcopy(edge)
                changed["production_artifacts"].pop()
                validate_edge_artifacts(source, module, changed)

            reject("reject-an-omitted-owned-native-role:" + family,
                   omit_native)
        check("never-launch-a-candidate-reference-or-property-worker",
              workers.call_count == 0)
        check("never-run-a-production-v7-source-audit",
              source_runs.call_count == 0)
        check("never-run-a-production-v7-no-delegation-audit",
              strict_runs.call_count == 0)
        check("never-read-production-correctness-or-historical-evidence",
              files.call_count == 0)
        check("never-create-or-compile-real-locale-inputs",
              locales.call_count == 0)
        check("restore-immutable-original-stage-planner",
              original.generic_steps is ancestor.ORIGINAL_GENERIC_STEPS)
        check("restore-immutable-original-official-child-runner",
              original.child_step is ancestor.ORIGINAL_CHILD_STEP)
        check("restore-immutable-original-static-audit-provider",
              original.static_family_audit is ancestor.ORIGINAL_STATIC_AUDIT)
        check("restore-immutable-original-exclusive-output-provider",
              original.output_path is ancestor.ORIGINAL_OUTPUT_PATH)
        check("restore-immutable-original-full-report-validator",
              original.validate_report_structure
              is ancestor.ORIGINAL_VALIDATE_REPORT)

    identifiers = [item["id"] for item in controls]
    failed_identifiers = [
        item["id"] for item in controls if item["passed"] is not True
    ]
    repeated_identifiers = sorted({
        identity for identity in identifiers
        if identifiers.count(identity) != 1
    })
    require(len(controls) >= 175
            and len(identifiers) == len(set(identifiers))
            and not failed_identifiers,
            "a complete frozen full-V7 campaign malicious control was weakened: "
            + json.dumps({
                "controls": len(controls),
                "failed": failed_identifiers,
                "repeated": repeated_identifiers,
            }, ensure_ascii=True, sort_keys=True))
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "python": "3.14.6",
        "synthetic_only": True,
        "inherited_v5_schema": historical.SELF_TEST_SCHEMA,
        "inherited_v5_control_count": inherited["poison_control_count"],
        "inherited_v4_control_count": inherited["inherited_v4_control_count"],
        "inherited_hardened_control_count": inherited[
            "inherited_hardened_control_count"
        ],
        "inherited_campaign_control_count": inherited[
            "inherited_campaign_control_count"
        ],
        "candidate_modules": list(original.MODULES),
        "actual_planned_step_counts": inherited[
            "actual_planned_step_counts"
        ],
        "official_method_count": OFFICIAL_METHODS,
        "full_unicode_observation_count": UNICODE_CASES,
        "frozen_edge_observation_count": EDGE_CHECKS,
        "frozen_deep_case_count": DEEP_CASES,
        "frozen_property_seed": DEEP_SEED,
        "observability_seed": OBSERVABILITY_SEED,
        "stage14_case_count": STAGE14_CASES,
        "stage14_candidate_check_count": STAGE14_CANDIDATE_CHECKS,
        "stage17_case_count": STAGE17_CASES,
        "stage17_candidate_check_count": STAGE17_CANDIDATE_CHECKS,
        "stage14_production_executed": False,
        "stage17_production_executed": False,
        "stage15_actual_failure_preserved": True,
        "stage15_failure_qualified_as_success": False,
        "stage15_candidate_processes_started": 0,
        "stage17_evidence_reader_executed": False,
        "official_v2_failure_hidden": False,
        "poison_control_count": len(controls),
        "poison_controls": controls,
        "candidate_processes_started": 0,
        "candidate_reports_written": 0,
        "production_audits_run": 0,
        "historical_audits_run": 0,
        "historical_audit_fallback_available": False,
        "production_report_reads": 0,
        "locales_compiled": 0,
        "performance_processes_started": 0,
        "performance_fixtures_opened": 0,
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
        "failed": 0,
    }


def main(arguments: list[str] | None = None) -> int:
    options = original.parse_arguments(arguments)
    if options.self_test:
        require(options.module is None
                and options.edge_oracle is None
                and options.deep_proof is None
                and options.output is None,
                "full V7 synthetic controls cannot run or write a campaign")
        print(json.dumps(self_test(), ensure_ascii=True, sort_keys=True),
              flush=True)
        return 0
    require(options.module in original.MODULES,
            "the complete V7 campaign requires exactly one explicit family")
    require(options.edge_oracle is not None
            and options.deep_proof is not None
            and options.output is not None,
            "the complete V7 campaign requires exact edge, deep, and output proofs")
    with current_v7_campaign():
        return original.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
