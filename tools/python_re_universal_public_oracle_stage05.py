#!/usr/bin/env python3
"""Requalify all three engines against the unchanged frozen Python oracle."""

from __future__ import annotations

import builtins
import hashlib
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator


WRAPPER = Path(__file__).resolve()
ROOT = WRAPPER.parent.parent

FROZEN_SOURCE = ROOT / "tools/python_re_universal_public_oracle_v1.py"
FROZEN_SOURCE_SHA256 = (
    "744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0"
)
STAGE03_SOURCE = ROOT / "tools/python_re_universal_public_oracle_stage03.py"
STAGE03_SOURCE_SHA256 = (
    "477c3f7e9955a9207b9345fc281705b6d643446b5d5c933009fa22a64b8d44ce"
)
STAGE04_SOURCE = ROOT / "tools/python_re_universal_public_oracle_stage04.py"
STAGE04_SOURCE_SHA256 = (
    "922de8886671e5bfc9db58ba92c134f4bf76b06acb01476f6fc9a9e3321815a6"
)
V4_ALL_REPORT = (
    ROOT / "candidates/evidence/python-re-universal-public-oracle-v4-all.json"
)
V4_ALL_REPORT_SHA256 = (
    "facb736a3409f459cdc812e6dc740df399f98ebb84745a22b615ef130ccdb137"
)
FROZEN_CASE_SHA256 = (
    "8e5c120a4e637c30940363e20d6042324d65d9f7d03fbd35240ffabf2df282ae"
)

BASE_AUDIT_SCHEMA = "rebar-postfinal-from-scratch-audit-v3"
BASE_AUDIT_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v3.py"
BASE_AUDIT_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json"
STRICT_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v3"
STRICT_AUDIT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v3.py"
STRICT_AUDIT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json"
)

ORIGINAL_AUDIT_SOURCE_RELATIVE = "tools/audit_from_scratch.py"
ORIGINAL_AUDIT_SOURCE_SHA256 = (
    "4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024"
)
ORIGINAL_AUDIT_REPORT_RELATIVE = "candidates/audits/FROM-SCRATCH-AUDIT.json"
ORIGINAL_AUDIT_REPORT_SHA256 = (
    "c78449b1153221bd0d17854c4f6682062392d19a04cfd0a424a1c6f3fa3478cb"
)
PREVIOUS_BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v2.py"
PREVIOUS_BASE_SOURCE_SHA256 = (
    "6f540074c9f7f4bdffe9e53939efe4cec25e5c029ca1f73ec791d377bddc9306"
)
PREVIOUS_BASE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
PREVIOUS_BASE_REPORT_SHA256 = (
    "5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551"
)
PREVIOUS_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v2.py"
PREVIOUS_STRICT_SOURCE_SHA256 = (
    "571c11885f9c9694025ea0434e57bfaa56651057eee62fa4396a2bcb95ae4cb5"
)
PREVIOUS_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json"
)
PREVIOUS_STRICT_REPORT_SHA256 = (
    "183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f"
)
IMMUTABLE_WORKER_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"
IMMUTABLE_WORKER_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v1.py"
IMMUTABLE_WORKER_SOURCE_SHA256 = (
    "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
)
IMMUTABLE_WORKER_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)
IMMUTABLE_WORKER_REPORT_SHA256 = (
    "c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b"
)

V6_RUNNER_RELATIVE = "tools/postfinal_public_practice_v6.py"
V6_RUNNER_SHA256 = (
    "16a56d1573526894733b6284204ff3712b4d4e2a9c63027d51b8de1869df3fc3"
)
V6_MANIFEST_RELATIVE = "performance/postfinal-public-v6/manifest.json"
V6_MANIFEST_SHA256 = (
    "65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a"
)
V6_SUMMARY_RELATIVE = (
    "performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-summary.json"
)
V6_SUMMARY_SHA256 = (
    "539fe6ba0ac492ffab121845da21033676ad7e7154ce9107f7f1778f55ceed4c"
)
V6_INTEGRITY_RELATIVE = (
    "performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-integrity.json"
)
V6_INTEGRITY_SHA256 = (
    "8eb2e6bba6894a71f63e32cc35cca5317bb1beccc32c2905bbeacebedb868fd2"
)
V6_COMPRESSED_RAW_RELATIVE = (
    "performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-raw.jsonl.gz"
)
V6_COMPRESSED_RAW_SHA256 = (
    "ec5783d5ad02c9bcfd1814d881e4f3de872d54929a16f352dd7baa6b0222fd6b"
)

OUTPUT_CANDIDATES = frozenset({"rust", "vm", "zig", "all"})
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
SYNTHETIC_INTERPRETER = "/synthetic/pinned/bin/python3.14"
SYNTHETIC_BASE_SOURCE_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage05/synthetic-v3-base-source"
).hexdigest()
SYNTHETIC_BASE_REPORT_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage05/synthetic-v3-base-report"
).hexdigest()
SYNTHETIC_STRICT_SOURCE_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage05/synthetic-v3-strict-source"
).hexdigest()
SYNTHETIC_STRICT_REPORT_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage05/synthetic-v3-strict-report"
).hexdigest()

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_stage04 as previous


frozen = previous.frozen
frozen.candidate_free()
frozen.require(
    Path(previous.__file__).resolve() == STAGE04_SOURCE.resolve()
    and Path(frozen.__file__).resolve() == FROZEN_SOURCE.resolve(),
    "stage-05 did not import the exact immutable stage-04 and V1 public oracles",
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
    and frozenset(frozen.CANDIDATES) == frozenset(REQUIRED_CANDIDATES),
    "stage-05 cannot change the frozen seed, grammar, cases, operations, or engines",
)

_immutable_build_cases = previous._frozen_build_cases
_immutable_synthetic_audit = previous._frozen_synthetic_audit
_immutable_validate_audit_document = previous._frozen_validate_audit_document
_immutable_verified_provenance = previous._frozen_verified_provenance
_immutable_run_gate = frozen.run_gate


def stage05_validate_frozen_fingerprints(
    *,
    oracle_sha256: str,
    stage03_sha256: str,
    stage04_sha256: str,
    stage04_report_sha256: str,
    v6_runner_sha256: str,
    v6_manifest_sha256: str,
    v6_summary_sha256: str,
    v6_integrity_sha256: str,
    v6_compressed_raw_sha256: str,
) -> None:
    expected = {
        "immutable V1 oracle": (oracle_sha256, FROZEN_SOURCE_SHA256),
        "immutable stage-03 oracle": (stage03_sha256, STAGE03_SOURCE_SHA256),
        "immutable stage-04 oracle": (stage04_sha256, STAGE04_SOURCE_SHA256),
        "immutable all-engine stage-04 report": (
            stage04_report_sha256,
            V4_ALL_REPORT_SHA256,
        ),
        "archived V6 benchmark source": (v6_runner_sha256, V6_RUNNER_SHA256),
        "archived V6 frozen public manifest": (v6_manifest_sha256, V6_MANIFEST_SHA256),
        "archived V6 summary fingerprint": (v6_summary_sha256, V6_SUMMARY_SHA256),
        "archived V6 integrity fingerprint": (v6_integrity_sha256, V6_INTEGRITY_SHA256),
        "archived V6 raw-stream fingerprint": (
            v6_compressed_raw_sha256,
            V6_COMPRESSED_RAW_SHA256,
        ),
    }
    for label, (actual, required) in expected.items():
        frozen.require(
            actual == required,
            f"stage-05 substituted the independently preserved {label}",
        )


def stage05_frozen_fingerprint_values() -> dict[str, str]:
    return {
        "oracle_sha256": FROZEN_SOURCE_SHA256,
        "stage03_sha256": STAGE03_SOURCE_SHA256,
        "stage04_sha256": STAGE04_SOURCE_SHA256,
        "stage04_report_sha256": V4_ALL_REPORT_SHA256,
        "v6_runner_sha256": V6_RUNNER_SHA256,
        "v6_manifest_sha256": V6_MANIFEST_SHA256,
        "v6_summary_sha256": V6_SUMMARY_SHA256,
        "v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "v6_compressed_raw_sha256": V6_COMPRESSED_RAW_SHA256,
    }


def stage05_default_output(candidate: str) -> Path:
    frozen.require(
        candidate in OUTPUT_CANDIDATES,
        "stage-05 requires an exact independent public evidence identity",
    )
    return (
        frozen.EVIDENCE_ROOT
        / f"python-re-universal-public-oracle-v5-{candidate}.json"
    )


def stage05_require_all(candidate: str) -> None:
    frozen.require(
        candidate == "all",
        "stage-05 production exclusively qualifies all three independent engines",
    )


def stage05_run_gate(candidate: str, output_argument: Path | None) -> int:
    stage05_require_all(candidate)
    return _immutable_run_gate(candidate, output_argument)


def stage05_build_cases() -> list[dict[str, Any]]:
    cases = _immutable_build_cases()
    frozen.require(
        len(cases) == 8_192
        and frozen.value_digest(cases) == FROZEN_CASE_SHA256,
        "stage-05 changed the exact immutable 8,192 public descriptors",
    )
    return cases


def stage05_synthetic_audit(
    selected: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, dict[str, str]], dict[str, dict[str, str]], str]:
    document, sources, binaries, interpreter = _immutable_synthetic_audit(selected)
    frozen.require(
        interpreter == SYNTHETIC_INTERPRETER,
        "stage-05 changed the exact candidate-free synthetic interpreter",
    )
    document.update(
        {
            "postfinal_schema": BASE_AUDIT_SCHEMA,
            "status": "PASS",
            "audit_source_path": BASE_AUDIT_SOURCE_RELATIVE,
            "audit_source_sha256": SYNTHETIC_BASE_SOURCE_SHA256,
            "original_audit_source_path": ORIGINAL_AUDIT_SOURCE_RELATIVE,
            "original_audit_source_sha256": ORIGINAL_AUDIT_SOURCE_SHA256,
            "original_v1_audit_report_path": ORIGINAL_AUDIT_REPORT_RELATIVE,
            "original_v1_audit_report_sha256": ORIGINAL_AUDIT_REPORT_SHA256,
            "previous_v2_audit_source_path": PREVIOUS_BASE_SOURCE_RELATIVE,
            "previous_v2_audit_source_sha256": PREVIOUS_BASE_SOURCE_SHA256,
            "previous_v2_audit_report_path": PREVIOUS_BASE_REPORT_RELATIVE,
            "previous_v2_audit_report_sha256": PREVIOUS_BASE_REPORT_SHA256,
        }
    )
    return document, sources, binaries, interpreter


def stage05_validate_audit_document(
    document: Any,
    selected: tuple[str, ...],
    actual_sources: dict[str, dict[str, str]],
    actual_binaries: dict[str, dict[str, str]],
    interpreter: str,
) -> None:
    frozen.require(isinstance(document, dict), "the stage-05 V3 base audit is invalid")
    frozen.require(
        document.get("postfinal_schema") == BASE_AUDIT_SCHEMA
        and document.get("schema_version") == 1
        and document.get("audit") == "bounded-from-scratch-engine-provenance"
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("passed") is True,
        "stage-05 requires the exact passing independently owned V3 base audit",
    )
    frozen.require(
        document.get("audit_source_path") == BASE_AUDIT_SOURCE_RELATIVE,
        "the stage-05 V3 base audit source path was substituted",
    )
    source_sha256 = document.get("audit_source_sha256")
    frozen.require(
        isinstance(source_sha256, str)
        and len(source_sha256) == 64
        and all(character in "0123456789abcdef" for character in source_sha256),
        "the stage-05 V3 base audit source fingerprint is invalid",
    )
    if interpreter == SYNTHETIC_INTERPRETER:
        frozen.require(
            source_sha256 == SYNTHETIC_BASE_SOURCE_SHA256,
            "the in-memory stage-05 V3 base audit source was poisoned",
        )
    else:
        frozen.require(
            source_sha256
            == frozen.sha256_path(ROOT / BASE_AUDIT_SOURCE_RELATIVE, frozen.MAX_SOURCE_BYTES),
            "the real stage-05 V3 base audit source does not match its report",
        )
    expected_history = {
        "original_audit_source_path": ORIGINAL_AUDIT_SOURCE_RELATIVE,
        "original_audit_source_sha256": ORIGINAL_AUDIT_SOURCE_SHA256,
        "original_v1_audit_report_path": ORIGINAL_AUDIT_REPORT_RELATIVE,
        "original_v1_audit_report_sha256": ORIGINAL_AUDIT_REPORT_SHA256,
        "previous_v2_audit_source_path": PREVIOUS_BASE_SOURCE_RELATIVE,
        "previous_v2_audit_source_sha256": PREVIOUS_BASE_SOURCE_SHA256,
        "previous_v2_audit_report_path": PREVIOUS_BASE_REPORT_RELATIVE,
        "previous_v2_audit_report_sha256": PREVIOUS_BASE_REPORT_SHA256,
    }
    for field, value in expected_history.items():
        frozen.require(
            document.get(field) == value,
            f"the stage-05 V3 base audit substituted immutable {field}",
        )
    _immutable_validate_audit_document(
        document,
        selected,
        actual_sources,
        actual_binaries,
        interpreter,
    )


def _flatten_source_fingerprints(
    sources: dict[str, dict[str, str]],
) -> dict[str, str]:
    flattened: dict[str, str] = {}
    for candidate in REQUIRED_CANDIDATES:
        frozen.require(candidate in sources, "a strict V3 source family is missing")
        for relative, digest in sources[candidate].items():
            frozen.require(relative not in flattened, "strict V3 candidates share a source")
            flattened[relative] = digest
    return flattened


def _flatten_native_fingerprints(
    binaries: dict[str, dict[str, str]],
) -> dict[str, str]:
    flattened: dict[str, str] = {}
    for candidate in REQUIRED_CANDIDATES:
        frozen.require(candidate in binaries, "a strict V3 native engine is missing")
        specification = frozen.CANDIDATES[candidate]
        for role, relative in specification["binaries"].items():
            public_role = "native-engine" if role == "native" else f"native-{role}"
            identity = f'{specification["module"]}:{public_role}'
            frozen.require(
                relative in binaries[candidate] and identity not in flattened,
                "a strict V3 native role was omitted or duplicated",
            )
            flattened[identity] = binaries[candidate][relative]
    frozen.require(len(flattened) == 5, "stage-05 lost an actual native engine role")
    return flattened


def stage05_synthetic_strict_audit(
    sources: dict[str, dict[str, str]],
    binaries: dict[str, dict[str, str]],
) -> dict[str, Any]:
    return {
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
        "inherited_control_count": 76,
        "qualified_source_fingerprints": _flatten_source_fingerprints(sources),
        "native_elf_fingerprints": _flatten_native_fingerprints(binaries),
        "previous_v2_audit_source_path": PREVIOUS_STRICT_SOURCE_RELATIVE,
        "previous_v2_audit_source_sha256": PREVIOUS_STRICT_SOURCE_SHA256,
        "previous_v2_audit_report_path": PREVIOUS_STRICT_REPORT_RELATIVE,
        "previous_v2_audit_report_sha256": PREVIOUS_STRICT_REPORT_SHA256,
        "immutable_no_delegation_source_path": IMMUTABLE_WORKER_SOURCE_RELATIVE,
        "immutable_no_delegation_source_sha256": IMMUTABLE_WORKER_SOURCE_SHA256,
        "immutable_no_delegation_report_path": IMMUTABLE_WORKER_REPORT_RELATIVE,
        "immutable_no_delegation_report_sha256": IMMUTABLE_WORKER_REPORT_SHA256,
        "immutable_no_delegation_schema": IMMUTABLE_WORKER_SCHEMA,
        "self_test": {
            "check_count": 32,
            "passed": True,
            "failed": [],
            "fixture_storage": "in-memory only",
            "candidate_imported": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "scope": {
            "explicit_source_paths_only": True,
            "closed_owned_source_graph": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "persistent_measurement_worker_available": True,
            "immutable_v1_source_preserved": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "candidate_imports": "isolated guarded subprocesses only",
        },
    }


def stage05_validate_strict_audit(
    document: Any,
    *,
    base_report_sha256: str,
    base_source_sha256: str,
    strict_source_sha256: str,
    sources: dict[str, dict[str, str]],
    binaries: dict[str, dict[str, str]],
) -> None:
    frozen.require(isinstance(document, dict), "the stage-05 strict V3 audit is invalid")
    exact: dict[str, Any] = {
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
        "previous_v2_audit_source_path": PREVIOUS_STRICT_SOURCE_RELATIVE,
        "previous_v2_audit_source_sha256": PREVIOUS_STRICT_SOURCE_SHA256,
        "previous_v2_audit_report_path": PREVIOUS_STRICT_REPORT_RELATIVE,
        "previous_v2_audit_report_sha256": PREVIOUS_STRICT_REPORT_SHA256,
        "immutable_no_delegation_source_path": IMMUTABLE_WORKER_SOURCE_RELATIVE,
        "immutable_no_delegation_source_sha256": IMMUTABLE_WORKER_SOURCE_SHA256,
        "immutable_no_delegation_report_path": IMMUTABLE_WORKER_REPORT_RELATIVE,
        "immutable_no_delegation_report_sha256": IMMUTABLE_WORKER_REPORT_SHA256,
        "immutable_no_delegation_schema": IMMUTABLE_WORKER_SCHEMA,
    }
    for field, value in exact.items():
        frozen.require(
            document.get(field) == value and type(document.get(field)) is type(value),
            f"the stage-05 strict V3 independence proof changed {field}",
        )
    frozen.require(
        document.get("qualified_source_fingerprints")
        == _flatten_source_fingerprints(sources),
        "the strict V3 audit does not bind every actual independently owned source",
    )
    frozen.require(
        document.get("native_elf_fingerprints")
        == _flatten_native_fingerprints(binaries),
        "the strict V3 audit does not bind all five actual native roles",
    )
    checks = document.get("self_test")
    frozen.require(
        isinstance(checks, dict)
        and checks.get("check_count") == 32
        and checks.get("passed") is True
        and checks.get("failed") == []
        and checks.get("fixture_storage") == "in-memory only"
        and checks.get("candidate_imported") is False
        and checks.get("benchmark_or_timing_executed") is False
        and checks.get("holdout_or_case_fixture_access") is False,
        "the strict V3 audit weakened its 32 independent malicious-source controls",
    )
    scope = document.get("scope")
    frozen.require(
        isinstance(scope, dict)
        and scope.get("explicit_source_paths_only") is True
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("immutable_v1_source_preserved") is True
        and scope.get("candidate_imports") == "isolated guarded subprocesses only"
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the strict V3 audit weakened production isolation or accessed timing",
    )


def stage05_validate_previous_report(document: Any) -> None:
    frozen.require(isinstance(document, dict), "the immutable stage-04 report is invalid")
    frozen.require(
        document.get("schema") == frozen.SCHEMA
        and document.get("status") == "PASS"
        and document.get("selected") == "all"
        and document.get("selected_candidates") == list(REQUIRED_CANDIDATES)
        and document.get("completed_candidates") == list(REQUIRED_CANDIDATES)
        and document.get("failed_candidate") is None
        and document.get("comparison_complete") is True
        and document.get("python") == "3.14.6"
        and document.get("seed") == frozen.SEED
        and document.get("seed_domain") == frozen.SEED_DOMAIN
        and document.get("cases") == frozen.EXPECTED_CASES
        and document.get("examples_per_stratum") == frozen.EXAMPLES_PER_STRATUM
        and document.get("grammar_family_count") == len(frozen.GRAMMAR_FAMILIES)
        and document.get("input_stratum_count") == len(frozen.INPUT_STRATA)
        and document.get("case_sha256") == FROZEN_CASE_SHA256
        and document.get("observations_per_case") == frozen.OBSERVATIONS_PER_CASE
        and document.get("observations_per_candidate") == frozen.EXPECTED_OBSERVATIONS
        and document.get("total_comparisons")
        == frozen.EXPECTED_OBSERVATIONS * len(REQUIRED_CANDIDATES)
        and document.get("planned_total_comparisons")
        == frozen.EXPECTED_OBSERVATIONS * len(REQUIRED_CANDIDATES)
        and document.get("mismatches") == 0
        and document.get("worker_failure") is None
        and document.get("performance") == "NOT MEASURED"
        and document.get("benchmark_or_timing_executed") is False
        and document.get("performance_fixtures_read") == 0
        and document.get("holdout_cases_read") == 0
        and document.get("external_regex_packages") == 0,
        "the exact passing all-engine stage-04 comparison was weakened",
    )


def stage05_production_preflight() -> None:
    """Authenticate owned public sources without reading measured timing."""

    frozen.candidate_free()
    actual = {
        "oracle_sha256": frozen.sha256_path(FROZEN_SOURCE, frozen.MAX_SOURCE_BYTES),
        "stage03_sha256": frozen.sha256_path(STAGE03_SOURCE, frozen.MAX_SOURCE_BYTES),
        "stage04_sha256": frozen.sha256_path(STAGE04_SOURCE, frozen.MAX_SOURCE_BYTES),
        "stage04_report_sha256": frozen.sha256_path(V4_ALL_REPORT, frozen.MAX_AUDIT_BYTES),
        "v6_runner_sha256": frozen.sha256_path(
            ROOT / V6_RUNNER_RELATIVE, frozen.MAX_SOURCE_BYTES
        ),
        "v6_manifest_sha256": frozen.sha256_path(
            ROOT / V6_MANIFEST_RELATIVE, frozen.MAX_AUDIT_BYTES
        ),
        "v6_summary_sha256": V6_SUMMARY_SHA256,
        "v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "v6_compressed_raw_sha256": V6_COMPRESSED_RAW_SHA256,
    }
    stage05_validate_frozen_fingerprints(**actual)
    with V4_ALL_REPORT.open("rb") as stream:
        payload = stream.read(frozen.MAX_AUDIT_BYTES + 1)
    frozen.require(
        len(payload) <= frozen.MAX_AUDIT_BYTES,
        "the immutable all-candidate stage-04 proof exceeds its bounded size",
    )
    try:
        report = json.loads(payload)
    except (UnicodeError, ValueError) as error:
        raise frozen.OracleIntegrityError(
            "cannot decode the immutable all-candidate stage-04 public proof"
        ) from error
    stage05_validate_previous_report(report)
    frozen.candidate_free()


def stage05_verified_provenance(selected: tuple[str, ...]) -> dict[str, Any]:
    frozen.require(
        selected == REQUIRED_CANDIDATES,
        "stage-05 must preserve all three independently implemented engines",
    )
    stage05_production_preflight()
    provenance = _immutable_verified_provenance(selected)
    frozen.require(
        provenance.get("audit_path") == BASE_AUDIT_REPORT_RELATIVE
        and provenance.get("oracle_source_path") == WRAPPER.relative_to(ROOT).as_posix(),
        "stage-05 did not bind its actual V3 source audit and own public runner",
    )
    base_digest = provenance.get("audit_sha256")
    frozen.require(
        isinstance(base_digest, str)
        and len(base_digest) == 64
        and all(character in "0123456789abcdef" for character in base_digest),
        "the actual stage-05 V3 base audit fingerprint is invalid",
    )
    source_hashes = provenance.get("source_sha256")
    native_hashes = provenance.get("native_binary_sha256")
    frozen.require(
        isinstance(source_hashes, dict) and isinstance(native_hashes, dict),
        "stage-05 did not preserve all independently owned source and native hashes",
    )
    base_source_sha256 = frozen.sha256_path(
        ROOT / BASE_AUDIT_SOURCE_RELATIVE,
        frozen.MAX_SOURCE_BYTES,
    )
    strict_source_sha256 = frozen.sha256_path(
        ROOT / STRICT_AUDIT_SOURCE_RELATIVE,
        frozen.MAX_SOURCE_BYTES,
    )
    strict_path = ROOT / STRICT_AUDIT_REPORT_RELATIVE
    strict_report_sha256 = frozen.sha256_path(strict_path, frozen.MAX_AUDIT_BYTES)
    with strict_path.open("rb") as stream:
        payload = stream.read(frozen.MAX_AUDIT_BYTES + 1)
    frozen.require(
        len(payload) <= frozen.MAX_AUDIT_BYTES,
        "the complete V3 strict audit exceeds its explicit bounded size",
    )
    try:
        strict_document = json.loads(payload)
    except (UnicodeError, ValueError) as error:
        raise frozen.OracleIntegrityError(
            "cannot decode the actual current V3 independence audit"
        ) from error
    stage05_validate_strict_audit(
        strict_document,
        base_report_sha256=base_digest,
        base_source_sha256=base_source_sha256,
        strict_source_sha256=strict_source_sha256,
        sources=source_hashes,
        binaries=native_hashes,
    )
    frozen.require(
        frozen.sha256_path(ROOT / ORIGINAL_AUDIT_SOURCE_RELATIVE, frozen.MAX_SOURCE_BYTES)
        == ORIGINAL_AUDIT_SOURCE_SHA256
        and frozen.sha256_path(ROOT / ORIGINAL_AUDIT_REPORT_RELATIVE, frozen.MAX_AUDIT_BYTES)
        == ORIGINAL_AUDIT_REPORT_SHA256
        and frozen.sha256_path(ROOT / PREVIOUS_BASE_SOURCE_RELATIVE, frozen.MAX_SOURCE_BYTES)
        == PREVIOUS_BASE_SOURCE_SHA256
        and frozen.sha256_path(ROOT / PREVIOUS_BASE_REPORT_RELATIVE, frozen.MAX_AUDIT_BYTES)
        == PREVIOUS_BASE_REPORT_SHA256
        and frozen.sha256_path(ROOT / PREVIOUS_STRICT_SOURCE_RELATIVE, frozen.MAX_SOURCE_BYTES)
        == PREVIOUS_STRICT_SOURCE_SHA256
        and frozen.sha256_path(ROOT / PREVIOUS_STRICT_REPORT_RELATIVE, frozen.MAX_AUDIT_BYTES)
        == PREVIOUS_STRICT_REPORT_SHA256
        and frozen.sha256_path(ROOT / IMMUTABLE_WORKER_SOURCE_RELATIVE, frozen.MAX_SOURCE_BYTES)
        == IMMUTABLE_WORKER_SOURCE_SHA256
        and frozen.sha256_path(ROOT / IMMUTABLE_WORKER_REPORT_RELATIVE, frozen.MAX_AUDIT_BYTES)
        == IMMUTABLE_WORKER_REPORT_SHA256,
        "stage-05 changed immutable V1/V2 independence or guarded-worker evidence",
    )
    frozen.candidate_free()
    return {
        **provenance,
        "postfinal_audit_schema": BASE_AUDIT_SCHEMA,
        "postfinal_audit_source_path": BASE_AUDIT_SOURCE_RELATIVE,
        "postfinal_audit_source_sha256": base_source_sha256,
        "postfinal_no_delegation_audit_path": STRICT_AUDIT_REPORT_RELATIVE,
        "postfinal_no_delegation_audit_sha256": strict_report_sha256,
        "postfinal_no_delegation_audit_source_path": STRICT_AUDIT_SOURCE_RELATIVE,
        "postfinal_no_delegation_audit_source_sha256": strict_source_sha256,
        "postfinal_no_delegation_audit_schema": STRICT_AUDIT_SCHEMA,
        "postfinal_no_delegation_control_count": 32,
        "original_oracle_source_path": FROZEN_SOURCE.relative_to(ROOT).as_posix(),
        "original_oracle_source_sha256": FROZEN_SOURCE_SHA256,
        "previous_stage03_oracle_source_path": STAGE03_SOURCE.relative_to(ROOT).as_posix(),
        "previous_stage03_oracle_source_sha256": STAGE03_SOURCE_SHA256,
        "previous_oracle_source_path": STAGE04_SOURCE.relative_to(ROOT).as_posix(),
        "previous_oracle_source_sha256": STAGE04_SOURCE_SHA256,
        "previous_all_candidate_report_path": V4_ALL_REPORT.relative_to(ROOT).as_posix(),
        "previous_all_candidate_report_sha256": V4_ALL_REPORT_SHA256,
        "original_audit_source_path": ORIGINAL_AUDIT_SOURCE_RELATIVE,
        "original_audit_source_sha256": ORIGINAL_AUDIT_SOURCE_SHA256,
        "original_v1_audit_report_path": ORIGINAL_AUDIT_REPORT_RELATIVE,
        "original_v1_audit_report_sha256": ORIGINAL_AUDIT_REPORT_SHA256,
        "previous_v2_base_audit_source_path": PREVIOUS_BASE_SOURCE_RELATIVE,
        "previous_v2_base_audit_source_sha256": PREVIOUS_BASE_SOURCE_SHA256,
        "previous_v2_base_audit_report_path": PREVIOUS_BASE_REPORT_RELATIVE,
        "previous_v2_base_audit_report_sha256": PREVIOUS_BASE_REPORT_SHA256,
        "previous_v2_no_delegation_source_path": PREVIOUS_STRICT_SOURCE_RELATIVE,
        "previous_v2_no_delegation_source_sha256": PREVIOUS_STRICT_SOURCE_SHA256,
        "previous_v2_no_delegation_report_path": PREVIOUS_STRICT_REPORT_RELATIVE,
        "previous_v2_no_delegation_report_sha256": PREVIOUS_STRICT_REPORT_SHA256,
        "guarded_worker_source_path": IMMUTABLE_WORKER_SOURCE_RELATIVE,
        "guarded_worker_source_sha256": IMMUTABLE_WORKER_SOURCE_SHA256,
        "guarded_worker_report_path": IMMUTABLE_WORKER_REPORT_RELATIVE,
        "guarded_worker_report_sha256": IMMUTABLE_WORKER_REPORT_SHA256,
        "guarded_worker_schema": IMMUTABLE_WORKER_SCHEMA,
        "immutable_public_case_sha256": FROZEN_CASE_SHA256,
        "previous_public_v6_runner_path": V6_RUNNER_RELATIVE,
        "previous_public_v6_runner_sha256": V6_RUNNER_SHA256,
        "previous_public_v6_manifest_path": V6_MANIFEST_RELATIVE,
        "previous_public_v6_manifest_sha256": V6_MANIFEST_SHA256,
        "previous_public_v6_summary_path": V6_SUMMARY_RELATIVE,
        "previous_public_v6_summary_sha256": V6_SUMMARY_SHA256,
        "previous_public_v6_integrity_path": V6_INTEGRITY_RELATIVE,
        "previous_public_v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "previous_public_v6_compressed_raw_path": V6_COMPRESSED_RAW_RELATIVE,
        "previous_public_v6_compressed_raw_sha256": V6_COMPRESSED_RAW_SHA256,
        "previous_public_v6_timing_evidence_read": False,
    }


@contextmanager
def _stage04_inherited_context() -> Iterator[None]:
    """Temporarily restore the exact immutable, file-free stage-04 controls."""

    updates = {
        "RUNNER": previous.WRAPPER,
        "AUDIT_PATH": previous.ROOT / previous.AUDIT_REPORT_RELATIVE,
        "default_output": previous.stage04_default_output,
        "build_cases": previous.stage04_build_cases,
        "synthetic_audit": previous.stage04_synthetic_audit,
        "validate_audit_document": previous.stage04_validate_audit_document,
        "verified_provenance": previous.stage04_verified_provenance,
        "self_test": previous.stage04_self_test,
        "run_gate": _immutable_run_gate,
    }
    original = {name: getattr(frozen, name) for name in updates}
    try:
        for name, value in updates.items():
            setattr(frozen, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(frozen, name, value)


@contextmanager
def _candidate_free_file_and_timing_guard() -> Iterator[dict[str, int]]:
    """Reject every direct synthetic file, process, timing, or entropy access."""

    counts = {"files": 0, "workers": 0, "timing": 0, "entropy": 0}

    def reject_file(*_arguments: Any, **_keywords: Any) -> Any:
        counts["files"] += 1
        raise frozen.OracleIntegrityError("stage-05 self-test attempted a real file read")

    def reject_worker(*_arguments: Any, **_keywords: Any) -> Any:
        counts["workers"] += 1
        raise frozen.OracleIntegrityError("stage-05 self-test attempted to start a worker")

    def reject_timing(*_arguments: Any, **_keywords: Any) -> Any:
        counts["timing"] += 1
        raise frozen.OracleIntegrityError("stage-05 self-test attempted benchmark timing")

    def reject_entropy(*_arguments: Any, **_keywords: Any) -> Any:
        counts["entropy"] += 1
        raise frozen.OracleIntegrityError("stage-05 self-test attempted production entropy")

    patches: list[tuple[Any, str, Any]] = [
        (builtins, "open", builtins.open),
        (Path, "open", Path.open),
        (Path, "read_bytes", Path.read_bytes),
        (Path, "read_text", Path.read_text),
        (frozen, "sha256_path", frozen.sha256_path),
        (subprocess, "Popen", subprocess.Popen),
        (subprocess, "run", subprocess.run),
        (os, "open", os.open),
        (os, "urandom", os.urandom),
        (time, "perf_counter", time.perf_counter),
        (time, "perf_counter_ns", time.perf_counter_ns),
        (time, "monotonic", time.monotonic),
        (time, "monotonic_ns", time.monotonic_ns),
    ]
    try:
        for owner, name, _original in patches:
            if owner is subprocess:
                replacement = reject_worker
            elif owner is time:
                replacement = reject_timing
            elif owner is os and name == "urandom":
                replacement = reject_entropy
            else:
                replacement = reject_file
            setattr(owner, name, replacement)
        yield counts
    finally:
        for owner, name, original in reversed(patches):
            setattr(owner, name, original)


def _synthetic_previous_report() -> dict[str, Any]:
    return {
        "schema": frozen.SCHEMA,
        "status": "PASS",
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "failed_candidate": None,
        "comparison_complete": True,
        "python": "3.14.6",
        "seed": frozen.SEED,
        "seed_domain": frozen.SEED_DOMAIN,
        "cases": frozen.EXPECTED_CASES,
        "examples_per_stratum": frozen.EXAMPLES_PER_STRATUM,
        "grammar_family_count": len(frozen.GRAMMAR_FAMILIES),
        "input_stratum_count": len(frozen.INPUT_STRATA),
        "case_sha256": FROZEN_CASE_SHA256,
        "observations_per_case": frozen.OBSERVATIONS_PER_CASE,
        "observations_per_candidate": frozen.EXPECTED_OBSERVATIONS,
        "total_comparisons": frozen.EXPECTED_OBSERVATIONS * len(REQUIRED_CANDIDATES),
        "planned_total_comparisons": (
            frozen.EXPECTED_OBSERVATIONS * len(REQUIRED_CANDIDATES)
        ),
        "mismatches": 0,
        "worker_failure": None,
        "performance": "NOT MEASURED",
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
    }


def _stage05_file_free_self_test() -> dict[str, Any]:
    frozen.candidate_free()
    with _stage04_inherited_context():
        inherited = previous.stage04_self_test()
    frozen.require(
        inherited.get("stage") == "stage04"
        and inherited.get("check_count", 0) >= 66
        and inherited.get("candidate_imports") == 0
        and inherited.get("candidate_processes") == 0
        and inherited.get("files_read") == 0
        and inherited.get("files_written") == 0
        and inherited.get("performance_fixtures_read") == 0
        and inherited.get("holdout_cases_read") == 0
        and inherited.get("external_regex_packages") == 0
        and inherited.get("benchmark_or_timing_executed") is False,
        "stage-05 failed to preserve the complete candidate-free stage-04 oracle",
    )
    checks: list[dict[str, Any]] = list(inherited["checks"])

    def check(name: str, condition: Any) -> None:
        frozen.require(condition, f"candidate-free public stage-05 control failed: {name}")
        checks.append({"name": name, "passed": True})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (frozen.OracleIntegrityError, KeyError, TypeError, ValueError):
            check(name, True)
        else:
            check(name, False)

    fingerprints = stage05_frozen_fingerprint_values()
    stage05_validate_frozen_fingerprints(**fingerprints)
    check("stage05-preserves-all-exact-immutable-source-and-V6-fingerprints", True)
    for field in fingerprints:
        reject(
            f"stage05-rejects-substituted-{field.replace('_', '-')}",
            lambda field=field: stage05_validate_frozen_fingerprints(
                **{**fingerprints, field: "0" * 64}
            ),
        )

    selected = REQUIRED_CANDIDATES
    document, sources, binaries, interpreter = stage05_synthetic_audit(selected)
    stage05_validate_audit_document(document, selected, sources, binaries, interpreter)
    check("stage05-accepts-complete-in-memory-v3-base-audit", True)

    def reject_base(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        poisoned = json.loads(frozen.canonical(document))
        mutate(poisoned)
        reject(
            name,
            lambda: stage05_validate_audit_document(
                poisoned,
                selected,
                sources,
                binaries,
                interpreter,
            ),
        )

    reject_base("stage05-rejects-missing-v3-base-schema", lambda value: value.pop("postfinal_schema"))
    reject_base("stage05-rejects-historical-v2-base-schema", lambda value: value.update(postfinal_schema="rebar-postfinal-from-scratch-audit-v2"))
    reject_base("stage05-rejects-failed-v3-base-status", lambda value: value.update(status="FAIL"))
    reject_base("stage05-rejects-failed-v3-base-result", lambda value: value.update(result="FAIL"))
    reject_base("stage05-rejects-failed-v3-base-flag", lambda value: value.update(passed=False))
    reject_base("stage05-rejects-substituted-v3-base-source", lambda value: value.update(audit_source_path=PREVIOUS_BASE_SOURCE_RELATIVE))
    reject_base("stage05-rejects-malformed-v3-base-source-hash", lambda value: value.update(audit_source_sha256="0"))
    reject_base("stage05-rejects-poisoned-v3-base-source-hash", lambda value: value.update(audit_source_sha256="0" * 64))
    reject_base("stage05-rejects-substituted-original-base-source", lambda value: value.update(original_audit_source_path=BASE_AUDIT_SOURCE_RELATIVE))
    reject_base("stage05-rejects-poisoned-original-base-source", lambda value: value.update(original_audit_source_sha256="0" * 64))
    reject_base("stage05-rejects-substituted-original-base-report", lambda value: value.update(original_v1_audit_report_path=BASE_AUDIT_REPORT_RELATIVE))
    reject_base("stage05-rejects-poisoned-original-base-report", lambda value: value.update(original_v1_audit_report_sha256="0" * 64))
    reject_base("stage05-rejects-substituted-previous-v2-base-source", lambda value: value.update(previous_v2_audit_source_path=BASE_AUDIT_SOURCE_RELATIVE))
    reject_base("stage05-rejects-poisoned-previous-v2-base-source", lambda value: value.update(previous_v2_audit_source_sha256="0" * 64))
    reject_base("stage05-rejects-substituted-previous-v2-base-report", lambda value: value.update(previous_v2_audit_report_path=BASE_AUDIT_REPORT_RELATIVE))
    reject_base("stage05-rejects-poisoned-previous-v2-base-report", lambda value: value.update(previous_v2_audit_report_sha256="0" * 64))

    strict = stage05_synthetic_strict_audit(sources, binaries)
    strict_kwargs = {
        "base_report_sha256": SYNTHETIC_BASE_REPORT_SHA256,
        "base_source_sha256": SYNTHETIC_BASE_SOURCE_SHA256,
        "strict_source_sha256": SYNTHETIC_STRICT_SOURCE_SHA256,
        "sources": sources,
        "binaries": binaries,
    }
    stage05_validate_strict_audit(strict, **strict_kwargs)
    check("stage05-accepts-complete-in-memory-v3-strict-audit", True)

    def reject_strict(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        poisoned = json.loads(frozen.canonical(strict))
        mutate(poisoned)
        reject(name, lambda: stage05_validate_strict_audit(poisoned, **strict_kwargs))

    for field in (
        "schema",
        "postfinal_schema",
        "status",
        "result",
        "passed",
        "audit_source_path",
        "audit_source_sha256",
        "base_audit_postfinal_schema",
        "base_audit_report_path",
        "base_audit_report_sha256",
        "base_audit_source_path",
        "base_audit_source_sha256",
        "inherited_control_count",
        "previous_v2_audit_source_path",
        "previous_v2_audit_source_sha256",
        "previous_v2_audit_report_path",
        "previous_v2_audit_report_sha256",
        "immutable_no_delegation_source_path",
        "immutable_no_delegation_source_sha256",
        "immutable_no_delegation_report_path",
        "immutable_no_delegation_report_sha256",
        "immutable_no_delegation_schema",
    ):
        reject_strict(
            f"stage05-rejects-poisoned-strict-{field.replace('_', '-')}",
            lambda value, field=field: value.update(
                {field: False if isinstance(value.get(field), bool) else 0}
            ),
        )
    reject_strict(
        "stage05-rejects-omitted-strict-owned-source",
        lambda value: value["qualified_source_fingerprints"].pop(
            "candidates/rust/src/lib.rs"
        ),
    )
    reject_strict(
        "stage05-rejects-poisoned-strict-owned-source",
        lambda value: value["qualified_source_fingerprints"].update(
            {"candidates/rust/src/lib.rs": "0" * 64}
        ),
    )
    reject_strict(
        "stage05-rejects-omitted-strict-native-engine",
        lambda value: value["native_elf_fingerprints"].pop(
            "candidates.rust_candidate:native-engine"
        ),
    )
    reject_strict(
        "stage05-rejects-poisoned-strict-native-engine",
        lambda value: value["native_elf_fingerprints"].update(
            {"candidates.rust_candidate:native-engine": "0" * 64}
        ),
    )
    reject_strict(
        "stage05-rejects-missing-strict-control",
        lambda value: value["self_test"].update(check_count=31),
    )
    reject_strict(
        "stage05-rejects-failed-strict-control",
        lambda value: value["self_test"].update(passed=False),
    )
    reject_strict(
        "stage05-rejects-strict-control-worker",
        lambda value: value["self_test"].update(candidate_imported=True),
    )
    reject_strict(
        "stage05-rejects-strict-control-timing",
        lambda value: value["self_test"].update(benchmark_or_timing_executed=True),
    )
    reject_strict(
        "stage05-rejects-strict-control-holdout",
        lambda value: value["self_test"].update(holdout_or_case_fixture_access=True),
    )
    for field, poisoned in (
        ("explicit_source_paths_only", False),
        ("closed_owned_source_graph", False),
        ("mapped_binaries_hashed_against_static_elf", False),
        ("persistent_measurement_worker_available", False),
        ("immutable_v1_source_preserved", False),
        ("benchmark_or_timing_executed", True),
        ("holdout_or_case_fixture_access", True),
        ("candidate_imports", "shared production interpreter"),
    ):
        reject_strict(
            f"stage05-rejects-poisoned-strict-scope-{field.replace('_', '-')}",
            lambda value, field=field, poisoned=poisoned: value["scope"].update(
                {field: poisoned}
            ),
        )

    previous_report = _synthetic_previous_report()
    stage05_validate_previous_report(previous_report)
    check("stage05-accepts-exact-in-memory-all-engine-stage04-proof", True)
    for field, replacement in (
        ("status", "FAIL"),
        ("selected", "rust"),
        ("completed_candidates", ["rust", "vm"]),
        ("comparison_complete", False),
        ("cases", 8_191),
        ("grammar_family_count", 15),
        ("input_stratum_count", 15),
        ("examples_per_stratum", 31),
        ("case_sha256", "0" * 64),
        ("observations_per_case", 47),
        ("total_comparisons", 1_179_647),
        ("mismatches", 1),
        ("performance", "1.5x guessed"),
        ("benchmark_or_timing_executed", True),
        ("performance_fixtures_read", 1),
        ("holdout_cases_read", 1),
        ("external_regex_packages", 1),
    ):
        reject(
            f"stage05-rejects-poisoned-prior-report-{field.replace('_', '-')}",
            lambda field=field, replacement=replacement: stage05_validate_previous_report(
                {**previous_report, field: replacement}
            ),
        )

    cases = stage05_build_cases()
    check("stage05-preserves-exact-all-8192-public-case-descriptors", len(cases) == 8_192)
    check("stage05-preserves-exact-public-case-fingerprint", frozen.value_digest(cases) == FROZEN_CASE_SHA256)
    check(
        "stage05-preserves-all-16-grammar-and-16-input-families",
        len({case["family"] for case in cases}) == 16
        and len({case["stratum"] for case in cases}) == 16,
    )
    check(
        "stage05-preserves-32-examples-per-frozen-stratum",
        frozen.EXAMPLES_PER_STRATUM == 32,
    )
    check(
        "stage05-preserves-all-48-observations-per-public-case",
        frozen.OBSERVATIONS_PER_CASE == 48,
    )
    check(
        "stage05-preserves-all-1179648-three-engine-comparisons",
        frozen.EXPECTED_OBSERVATIONS * len(REQUIRED_CANDIDATES) == 1_179_648,
    )
    check(
        "stage05-preserves-all-exact-v5-candidate-specific-path-validation",
        all(
            frozen.validate_output(stage05_default_output(name), name)
            == stage05_default_output(name).resolve()
            for name in OUTPUT_CANDIDATES
        ),
    )
    for candidate in ("rust", "vm", "zig"):
        reject(
            f"stage05-rejects-production-without-all-engines-{candidate}",
            lambda candidate=candidate: stage05_require_all(candidate),
        )
    for version in ("v1", "v2", "v3", "v4"):
        reject(
            f"stage05-rejects-overwriting-historical-{version}-all-evidence",
            lambda version=version: frozen.validate_output(
                frozen.EVIDENCE_ROOT
                / f"python-re-universal-public-oracle-{version}-all.json",
                "all",
            ),
        )
    reject(
        "stage05-rejects-cross-candidate-output",
        lambda: frozen.validate_output(stage05_default_output("zig"), "all"),
    )
    reject(
        "stage05-rejects-parent-traversal-output",
        lambda: frozen.validate_output(
            frozen.EVIDENCE_ROOT.parent / "python-re-universal-public-oracle-v5-all.json",
            "all",
        ),
    )
    check(
        "stage05-preserves-exact-all-candidate-exclusive-output",
        frozen.validate_output(stage05_default_output("all"), "all")
        == stage05_default_output("all").resolve(),
    )
    frozen.candidate_free()
    check("stage05-never-imports-a-production-engine", True)
    return {
        **inherited,
        "stage": "stage05",
        "postfinal_audit_schema": BASE_AUDIT_SCHEMA,
        "postfinal_no_delegation_audit_schema": STRICT_AUDIT_SCHEMA,
        "original_oracle_source_sha256": FROZEN_SOURCE_SHA256,
        "previous_stage03_oracle_source_sha256": STAGE03_SOURCE_SHA256,
        "previous_oracle_source_sha256": STAGE04_SOURCE_SHA256,
        "previous_all_candidate_report_sha256": V4_ALL_REPORT_SHA256,
        "previous_public_v6_runner_sha256": V6_RUNNER_SHA256,
        "previous_public_v6_manifest_sha256": V6_MANIFEST_SHA256,
        "previous_public_v6_summary_sha256": V6_SUMMARY_SHA256,
        "previous_public_v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "previous_public_v6_compressed_raw_sha256": V6_COMPRESSED_RAW_SHA256,
        "previous_public_v6_timing_evidence_read": False,
        "production_candidate_policy": "all three independently audited engines only",
        "exclusive_output": stage05_default_output("all").relative_to(ROOT).as_posix(),
        "checks": checks,
        "check_count": len(checks),
    }


def stage05_self_test() -> dict[str, Any]:
    """Guard inherited and new checks against actual files, timing, and workers."""

    frozen.candidate_free()
    with _candidate_free_file_and_timing_guard() as counts:
        report = _stage05_file_free_self_test()
        frozen.require(
            all(value == 0 for value in counts.values()),
            "stage-05 candidate-free controls accessed files, workers, timing, or entropy",
        )
        frozen.require(
            report.get("check_count", 0) >= 66
            and report.get("cases") == 8_192
            and report.get("observations_per_case") == 48
            and report.get("observations_per_candidate") == 393_216
            and report.get("candidate_imports") == 0
            and report.get("candidate_processes") == 0
            and report.get("files_read") == 0
            and report.get("files_written") == 0
            and report.get("performance_fixtures_read") == 0
            and report.get("holdout_cases_read") == 0
            and report.get("external_regex_packages") == 0
            and report.get("benchmark_or_timing_executed") is False,
            "stage-05 weakened the original immutable, zero-delegation public oracle",
        )
        report["checks"].append(
            {
                "name": "stage05-guards-all-real-files-workers-timing-and-entropy",
                "passed": True,
            }
        )
        report["check_count"] = len(report["checks"])
        report["guarded_file_access_attempts"] = counts["files"]
        report["guarded_worker_start_attempts"] = counts["workers"]
        report["guarded_timing_attempts"] = counts["timing"]
        report["guarded_entropy_attempts"] = counts["entropy"]
    frozen.candidate_free()
    return report


frozen.RUNNER = WRAPPER
frozen.AUDIT_PATH = ROOT / BASE_AUDIT_REPORT_RELATIVE
frozen.default_output = stage05_default_output
frozen.build_cases = stage05_build_cases
frozen.synthetic_audit = stage05_synthetic_audit
frozen.validate_audit_document = stage05_validate_audit_document
frozen.verified_provenance = stage05_verified_provenance
frozen.self_test = stage05_self_test
frozen.run_gate = stage05_run_gate


if __name__ == "__main__":
    if "--self-test" not in sys.argv[1:] and "--worker" not in sys.argv[1:]:
        stage05_production_preflight()
    raise SystemExit(frozen.main())
