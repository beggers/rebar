#!/usr/bin/env python3
"""Freeze, measure, and independently replay expanded public practice.

This is an additive, calibration-only experiment.  It never creates, opens,
replays, or substitutes a final benchmark.  Freezing deliberately fails until
all twelve current stage-05 correctness artifacts, the original 76-control audit, and
the independently committed additive no-delegation audit are all present and
bound to exactly the current production sources and native binaries.

Actual measurement uses four long-lived, separately guarded subprocesses.  The
controller never imports a production candidate.  In particular, the CPython
baseline and an independently implemented candidate never share an interpreter.
Interprocess requests, preparation, correctness comparisons, allocation
sampling, and process-memory observations are all outside the timed operation.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib
import json
import platform
import subprocess
import sys
import types
from pathlib import Path
from typing import Any

from tools import postfinal_public_practice_v3 as previous
from tools import rust_v7_calibration_pilot as pilot
from tools import rust_v7_multi_candidate_practice_audit as replay


ROOT = pilot.ROOT
VERSION = "postfinal-public-practice-v4"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v4"
EVIDENCE_ROOT = VERSION_ROOT / "evidence"
MANIFEST_PATH = VERSION_ROOT / "manifest.json"
RAW_PATH = EVIDENCE_ROOT / f"{VERSION}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE_ROOT / f"{VERSION}-summary.json"
INTEGRITY_PATH = EVIDENCE_ROOT / f"{VERSION}-integrity.json"

AUDIT_PATH = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
AUDIT_SOURCE_PATH = ROOT / "tools" / "audit_from_scratch.py"
POSTFINAL_AUDIT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)
POSTFINAL_AUDIT_SOURCE_PATH = ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
POSTFINAL_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"
POSTFINAL_AUDIT_CONTROL_COUNT = 32
UNIVERSAL_ORACLE_SOURCE_PATH = (
    ROOT / "tools" / "python_re_universal_public_oracle_stage03.py"
)
UNIVERSAL_ORACLE_SOURCE_SHA256 = (
    "477c3f7e9955a9207b9345fc281705b6d643446b5d5c933009fa22a64b8d44ce"
)
UNIVERSAL_ORACLE_FROZEN_SOURCE_PATH = (
    ROOT / "tools" / "python_re_universal_public_oracle_v1.py"
)
UNIVERSAL_ORACLE_FROZEN_SOURCE_SHA256 = (
    "744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0"
)
UNIVERSAL_ORACLE_REPORT_PATH = (
    ROOT
    / "candidates"
    / "evidence"
    / "python-re-universal-public-oracle-v3-all.json"
)
UNIVERSAL_ORACLE_SCHEMA = "rebar-python-re-universal-public-oracle-v1"
UNIVERSAL_ORACLE_SEED = 2026072417
UNIVERSAL_ORACLE_SEED_DOMAIN = "rebar/python-re/universal-public/v1"
UNIVERSAL_ORACLE_CANDIDATES = ("rust", "vm", "zig")
UNIVERSAL_ORACLE_GRAMMAR_FAMILIES = 16
UNIVERSAL_ORACLE_INPUT_STRATA = 16
UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM = 32
UNIVERSAL_ORACLE_CASES = (
    UNIVERSAL_ORACLE_GRAMMAR_FAMILIES
    * UNIVERSAL_ORACLE_INPUT_STRATA
    * UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM
)
UNIVERSAL_ORACLE_OBSERVATIONS_PER_CASE = 48
UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE = (
    UNIVERSAL_ORACLE_CASES * UNIVERSAL_ORACLE_OBSERVATIONS_PER_CASE
)
UNIVERSAL_ORACLE_TOTAL_OBSERVATIONS = (
    UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE
    * len(UNIVERSAL_ORACLE_CANDIDATES)
)
UNIVERSAL_ORACLE_PROOF_FIELDS = (
    "python_re_universal_oracle_source_path",
    "python_re_universal_oracle_source_sha256",
    "python_re_universal_oracle_report_path",
    "python_re_universal_oracle_report_sha256",
    "python_re_universal_oracle_schema",
    "python_re_universal_oracle_status",
    "python_re_universal_oracle_selected",
    "python_re_universal_oracle_candidates",
    "python_re_universal_oracle_cases",
    "python_re_universal_oracle_comparisons_per_case",
    "python_re_universal_oracle_comparisons_per_candidate",
    "python_re_universal_oracle_total_comparisons",
    "python_re_universal_oracle_mismatches",
    "python_re_universal_oracle_seed",
    "python_re_universal_oracle_seed_domain",
    "python_re_universal_oracle_case_sha256",
    "python_re_universal_oracle_grammar_family_count",
    "python_re_universal_oracle_input_stratum_count",
    "python_re_universal_oracle_examples_per_stratum",
    "python_re_universal_oracle_original_audit_sha256",
    "python_re_universal_oracle_postfinal_no_delegation_audit_sha256",
    "python_re_universal_oracle_frozen_source_path",
    "python_re_universal_oracle_frozen_source_sha256",
)
UNIVERSAL_ORACLE_NATIVE_FINGERPRINT_KEYS = {
    "rust": {
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so": (
            "candidates.rust_candidate:native-bridge"
        ),
        "candidates/_rust_engine.so": "candidates.rust_candidate:native-engine",
    },
    "vm": {
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so": (
            "candidates.vm_candidate:native-engine"
        ),
    },
    "zig": {
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so": (
            "candidates.zig_candidate:native-bridge"
        ),
        "candidates/_zig_probe.so": "candidates.zig_candidate:native-engine",
    },
}
UNIVERSAL_ORACLE_NATIVE_MAPPING_ROLES = {
    "rust": {
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so": "bridge",
        "candidates/_rust_engine.so": "engine",
    },
    "vm": {
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so": "native",
    },
    "zig": {
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so": "bridge",
        "candidates/_zig_probe.so": "engine",
    },
}

POSTFINAL_PLAN_SCHEMA = "rebar-postfinal-public-practice-plan-v4"
POSTFINAL_REPORT_SCHEMA = "rebar-postfinal-public-practice-report-v4"
POSTFINAL_INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v4"

MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
WORKER_FAMILIES = {
    "re": "re",
    "candidates.rust_candidate": "rust",
    "candidates.vm_candidate": "vm",
    "candidates.zig_candidate": "zig",
}

STAGE05_CANDIDATES = ("rust", "vm", "zig")
STAGE05_DEEP_FAMILIES = {"rust": "RUST", "vm": "C", "zig": "ZIG"}
STAGE05_CORRECTNESS_PATHS = tuple(
    (role, path)
    for candidate in STAGE05_CANDIDATES
    for role, path in (
        (
            f"{candidate}-edge",
            ROOT
            / "candidates"
            / "evidence"
            / (
                f"rust-v7-edge-oracle-{candidate}"
                "-post-final-stage-05-universal-parity.json.gz"
            ),
        ),
        (
            f"{candidate}-deep-public-contract",
            ROOT
            / "candidates"
            / "audits"
            / (
                f"RUST-V8-DEEP-CONTRACT-{STAGE05_DEEP_FAMILIES[candidate]}"
                "-POST-FINAL-STAGE-05-UNIVERSAL-PARITY.json.gz"
            ),
        ),
        (
            f"{candidate}-observability",
            ROOT
            / "candidates"
            / "evidence"
            / (
                f"rust-v8-observability-{candidate}"
                "-qualified-post-final-stage-05-universal-parity.json.gz"
            ),
        ),
        (
            f"{candidate}-complete-correctness-campaign",
            ROOT
            / "candidates"
            / "evidence"
            / (
                f"rust-v8-{candidate}"
                "-post-final-stage-05-universal-parity-sealed-campaign.json"
            ),
        ),
    )
)
DEFAULT_EDGE_ORACLES = tuple(
    path
    for role, path in STAGE05_CORRECTNESS_PATHS
    if role.endswith("-edge")
)

V3_MANIFEST_PATH = ROOT / "performance" / "postfinal-public-v3" / "manifest.json"
V3_MANIFEST_SHA256 = (
    "5f49f255271b8f71786e7fa67a61827b53c1330e1ad7afe29c8750991df4b90f"
)
V3_RUNNER_SHA256 = (
    "aa2b22de82894dc41622378d1bd782636358fa360454be37f3b8fedbc6e4989a"
)

CASES = 8_192
FIXTURE_CASES = 10_312
ELIGIBLE_CASES = 9_731
CATEGORIES = 260
PUBLIC_APIS = 12
TRIALS = 13
WARMUPS = 4
BOOTSTRAPS = 2_000
MAX_OPERATIONS = 16
SELECTION_SEED = 2026072404
ORDER_SEED = 2026072405
BOOTSTRAP_SEED = 2026072406
EXCLUSIVE_SLOT = VERSION
EXPECTED_ROWS = CASES * TRIALS * len(MODULES)
EXPECTED_CORRECTNESS_CHECKS = EXPECTED_ROWS * 3
EXPECTED_CONFIDENCE_INTERVALS = CASES * (len(MODULES) - 1) + len(MODULES) - 1
EXPECTED_RUNTIME_GUARD_CHECKS = len(MODULES) * (2 + 2 * CASES)
MAX_WORKER_RESPONSE_BYTES = 262_144
RUNTIME_NATIVE_HASH_POLICY = (
    "Force a complete SHA-256 of each actually mapped owned native ELF before "
    "the first case and after the last case; inspect /proc/self/maps, forbidden "
    "module reachability, native role identities, and exact file stat tuples "
    "before and after every case; reuse an already verified digest only while "
    "device, inode, size, nanosecond mtime, and nanosecond ctime remain "
    "unchanged. A malicious metadata-preserving change between the forced "
    "full hashes is not cryptographically ruled out."
)

EXPECTED_BOUNDED_API_COUNTS = {
    "compile": 210,
    "escape": 161,
    "findall": 2_882,
    "finditer": 2_738,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 427,
    "search": 1_057,
    "split": 451,
    "sub": 447,
    "subn": 530,
}

Entry = tuple[int, dict[str, Any], dict[str, Any]]
SelectedEntry = tuple[int, dict[str, Any], dict[str, Any], tuple[str, ...]]


def require(condition: bool, message: str) -> None:
    """Reject substituted evidence without changing an existing experiment."""

    if not condition:
        raise RuntimeError(message)


def require_candidate_free() -> None:
    """Keep planning, replay, and the paired controller candidate-free."""

    loaded = sorted(
        name
        for name in sys.modules
        if any(
            name == candidate or name.startswith(candidate + ".")
            for candidate in MODULES[1:]
        )
    )
    require(
        not loaded,
        f"the isolated public controller imported a production candidate: {loaded!r}",
    )


def require_pinned_python() -> None:
    require(
        platform.python_implementation() == "CPython"
        and tuple(sys.version_info[:3]) == (3, 14, 6),
        "expanded public practice requires pinned stable CPython 3.14.6",
    )
    require(
        Path(sys.executable).resolve() == replay.PINNED_PYTHON.resolve(),
        "expanded public practice requires the exact pinned CPython executable",
    )


def exact_versioned_path(value: Path, expected: Path, label: str) -> Path:
    resolved = value.resolve()
    require(
        resolved == expected.resolve(),
        f"{label} must use its exact additive {VERSION} evidence path",
    )
    require(
        resolved.is_relative_to(VERSION_ROOT.resolve()),
        f"{label} escaped the expanded public-practice evidence directory",
    )
    return resolved


def read_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"the required {label} is missing")
    try:
        with path.open("rb") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot decode the required {label}") from error
    require(isinstance(document, dict), f"the required {label} is not an object")
    return document


def valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def checked_owned_source(value: str, label: str) -> Path:
    require(isinstance(value, str) and bool(value), f"invalid {label} source")
    relative = Path(value)
    require(not relative.is_absolute(), f"{label} source escaped the repository")
    resolved = (ROOT / relative).resolve()
    root_build_source = ROOT / "pyproject.toml"
    require(
        resolved.is_relative_to(ROOT.resolve()),
        f"{label} source escaped the repository",
    )
    require(
        resolved.is_relative_to((ROOT / "candidates").resolve())
        or resolved.is_relative_to((ROOT / "tools").resolve())
        or (
            value == "pyproject.toml"
            and resolved == root_build_source.resolve()
            and not root_build_source.is_symlink()
        ),
        f"{label} is not an explicitly owned candidate, audit, or root build source",
    )
    require(resolved.is_file(), f"the {label} source is missing")
    return resolved


def verified_public_v3_source() -> None:
    """Bind the immutable public predecessor without decoding its case rows."""

    require_candidate_free()
    require(previous.VERSION == "postfinal-public-practice-v3", "public predecessor changed")
    require(previous.MODULES == MODULES, "the public predecessor changed its engines")
    require(previous.CASES == 4_096, "the public predecessor changed its denominator")
    require(previous.FIXTURE_CASES == FIXTURE_CASES, "the public source pool changed")
    require(previous.ELIGIBLE_CASES == ELIGIBLE_CASES, "the safe public capacity changed")
    require(previous.CATEGORIES == CATEGORIES, "the public category catalog changed")
    require(previous.PUBLIC_APIS == PUBLIC_APIS, "the public operation catalog changed")
    require(previous.TRIALS == TRIALS, "the inherited paired trial protocol changed")
    require(previous.BOOTSTRAPS == BOOTSTRAPS, "the inherited bootstrap protocol changed")
    require(previous.MAX_OPERATIONS == MAX_OPERATIONS, "the operation safety bound changed")
    require(
        previous.EXPECTED_BOUNDED_API_COUNTS == EXPECTED_BOUNDED_API_COUNTS,
        "the independently frozen bounded public API capacities changed",
    )
    require(
        pilot.file_sha256(V3_MANIFEST_PATH) == V3_MANIFEST_SHA256,
        "the frozen version-3 public manifest changed",
    )
    require(
        pilot.file_sha256(Path(previous.__file__).resolve()) == V3_RUNNER_SHA256,
        "the frozen version-3 public runner changed",
    )
    require(
        len({SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}) == 3,
        "expanded public selection, ordering, and bootstrap domains overlap",
    )
    require(
        not {SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}
        & {previous.SELECTION_SEED, previous.ORDER_SEED, previous.BOOTSTRAP_SEED},
        "expanded public practice reused a version-3 seed",
    )


def require_stage05_correctness_path_contract() -> None:
    """Bind exactly twelve fresh, candidate-specific stage-05 proof paths."""

    expected_roles = tuple(
        f"{candidate}-{suffix}"
        for candidate in STAGE05_CANDIDATES
        for suffix in (
            "edge",
            "deep-public-contract",
            "observability",
            "complete-correctness-campaign",
        )
    )
    require(
        STAGE05_CANDIDATES == UNIVERSAL_ORACLE_CANDIDATES,
        "stage-05 correctness changed the three independently owned families",
    )
    require(
        STAGE05_DEEP_FAMILIES == {"rust": "RUST", "vm": "C", "zig": "ZIG"},
        "stage-05 correctness changed a frozen native deep-contract family",
    )
    require(
        len(STAGE05_CORRECTNESS_PATHS) == 12
        and tuple(role for role, _path in STAGE05_CORRECTNESS_PATHS)
        == expected_roles
        and len({path.resolve() for _role, path in STAGE05_CORRECTNESS_PATHS})
        == 12,
        "stage-05 correctness omitted, duplicated, or swapped a family proof",
    )
    stage05_paths = dict(STAGE05_CORRECTNESS_PATHS)
    for candidate, family in STAGE05_DEEP_FAMILIES.items():
        require(
            stage05_paths[f"{candidate}-deep-public-contract"]
            == (
                ROOT
                / "candidates"
                / "audits"
                / (
                    f"RUST-V8-DEEP-CONTRACT-{family}"
                    "-POST-FINAL-STAGE-05-UNIVERSAL-PARITY.json.gz"
                )
            ),
            f"stage-05 {candidate} uses a foreign deep-contract family",
        )
    require(
        len(DEFAULT_EDGE_ORACLES) == 3
        and DEFAULT_EDGE_ORACLES
        == tuple(
            path
            for role, path in STAGE05_CORRECTNESS_PATHS
            if role.endswith("-edge")
        ),
        "stage-05 public practice omitted a fresh Rust, VM, or Zig edge proof",
    )


def verified_stage05_correctness_artifacts() -> list[dict[str, str]]:
    """Validate all twelve complete, current, candidate-bound stage-05 proofs."""

    require_candidate_free()
    require_stage05_correctness_path_contract()
    for role, path in STAGE05_CORRECTNESS_PATHS:
        require(
            path.is_file() and not path.is_symlink(),
            "expanded public freezing requires the complete current "
            f"stage-05 correctness proof: {role}",
        )

    from tools import rust_v8_multi_candidate_campaign as sealed_campaign
    from tools import rust_v8_multi_candidate_observability as observability

    artifacts: list[dict[str, str]] = []
    path_by_role = dict(STAGE05_CORRECTNESS_PATHS)
    try:
        for candidate in STAGE05_CANDIDATES:
            module = f"candidates.{candidate}_candidate"
            edge_path = path_by_role[f"{candidate}-edge"]
            deep_path = path_by_role[f"{candidate}-deep-public-contract"]
            observability_path = path_by_role[f"{candidate}-observability"]
            campaign_path = path_by_role[
                f"{candidate}-complete-correctness-campaign"
            ]

            spec, edge = sealed_campaign.validate_edge(edge_path, module)
            deep_proof = sealed_campaign.read_deep_document(
                deep_path,
                spec,
                edge,
            )
            _observability_archive, observations = observability.checked_gzip(
                observability_path,
                parent=ROOT / "candidates" / "evidence",
                description=f"stage-05 complete {candidate} observability",
            )
            sealed_campaign.validate_observability_document(
                observations,
                module,
                edge,
                deep_proof,
            )
            campaign_report = read_json(
                campaign_path,
                f"stage-05 complete {candidate} correctness campaign",
            )
            sealed_campaign.validate_report_structure(campaign_report, module)
            require(
                campaign_report.get("edge_oracle") == edge,
                f"stage-05 {candidate} campaign substituted its edge proof",
            )
            require(
                campaign_report.get("deep_proof") == deep_proof,
                f"stage-05 {candidate} campaign substituted its deep proof",
            )
            require(
                campaign_report.get("required_correctness_step_count")
                == len(campaign_report["steps"])
                and len(campaign_report["steps"]) >= 18,
                f"stage-05 {candidate} campaign omitted a correctness step",
            )
            for role in (
                f"{candidate}-edge",
                f"{candidate}-deep-public-contract",
                f"{candidate}-observability",
                f"{candidate}-complete-correctness-campaign",
            ):
                path = path_by_role[role]
                artifacts.append(
                    {
                        "role": role,
                        "path": str(
                            path.resolve().relative_to(ROOT.resolve())
                        ),
                        "sha256": pilot.file_sha256(path),
                    }
                )
    except (AssertionError, OSError, ValueError, TypeError) as error:
        raise RuntimeError(
            "expanded public freezing rejected a stale, incomplete, failing, "
            "or cross-candidate stage-05 correctness proof"
        ) from error

    require(
        len(artifacts) == 12
        and tuple(item["role"] for item in artifacts)
        == tuple(role for role, _path in STAGE05_CORRECTNESS_PATHS),
        "stage-05 correctness proof coverage is incomplete",
    )
    require_candidate_free()
    return artifacts


def verified_from_scratch_audit() -> tuple[
    str,
    dict[str, str],
    dict[str, str],
    dict[str, Any],
]:
    """Validate both independently bound audits without loading an engine."""

    require_candidate_free()
    require(
        AUDIT_SOURCE_PATH.is_file(),
        "the original 76-control from-scratch audit source is missing",
    )
    original = read_json(AUDIT_PATH, "original 76-control from-scratch audit")
    original_digest = pilot.file_sha256(AUDIT_PATH)
    original_source_digest = pilot.file_sha256(AUDIT_SOURCE_PATH)
    sources, native = replay.validate_independence(original)
    require(
        len(native) == 5,
        "the original from-scratch audit omitted an owned native library",
    )

    require(
        POSTFINAL_AUDIT_SOURCE_PATH.is_file(),
        "the committed additive no-delegation audit source is missing",
    )
    report = read_json(
        POSTFINAL_AUDIT_PATH,
        "current additive no-delegation PASS report",
    )
    audit_source_digest = pilot.file_sha256(POSTFINAL_AUDIT_SOURCE_PATH)
    require(
        report.get("schema") == POSTFINAL_AUDIT_SCHEMA,
        "the additive no-delegation audit schema changed",
    )
    require(
        report.get("result") == "PASS" and report.get("passed") is True,
        "the current additive no-delegation audit did not pass",
    )
    require(
        report.get("audit_source_sha256") == audit_source_digest,
        "the additive no-delegation audit source changed after verification",
    )
    require(
        report.get("audit_source_path")
        == str(POSTFINAL_AUDIT_SOURCE_PATH.resolve().relative_to(ROOT.resolve())),
        "the additive no-delegation audit source path was substituted",
    )
    require(
        report.get("base_audit_report_path")
        == str(AUDIT_PATH.resolve().relative_to(ROOT.resolve()))
        and report.get("base_audit_report_sha256") == original_digest,
        "the additive audit is not bound to the original 76-control PASS report",
    )
    require(
        report.get("base_audit_source_path")
        == str(AUDIT_SOURCE_PATH.resolve().relative_to(ROOT.resolve()))
        and report.get("base_audit_source_sha256") == original_source_digest,
        "the additive audit is not bound to the current original audit source",
    )
    require(
        report.get("inherited_control_count") == 76,
        "the additive audit weakened the original 76 malicious controls",
    )
    inherited_controls = report.get("inherited_self_test")
    require(
        isinstance(inherited_controls, dict)
        and inherited_controls.get("passed") is True
        and inherited_controls.get("check_count") == 76,
        "the additive audit omitted the passing original isolated controls",
    )

    families = report.get("families")
    require(
        isinstance(families, dict)
        and set(families) == {"ast", "rust", "vm", "zig"}
        and all(
            isinstance(evidence, dict) and evidence.get("passed") is True
            for evidence in families.values()
        ),
        "the additive audit omitted an independently implemented engine family",
    )

    audited_sources = report.get("source_fingerprints")
    require(
        isinstance(audited_sources, dict) and bool(audited_sources),
        "the additive audit has no closed owned-source fingerprints",
    )
    for relative, expected in audited_sources.items():
        require(
            isinstance(relative, str) and valid_sha256(expected),
            "the additive audit contains an invalid owned-source fingerprint",
        )
        source = checked_owned_source(relative, "additive audit")
        require(
            pilot.file_sha256(source) == expected,
            f"an additive-audited production source changed: {relative}",
        )
    for relative, expected in sources.items():
        require(
            audited_sources.get(relative) == expected,
            f"the additive and canonical source audits disagree: {relative}",
        )
    require(
        report.get("qualified_source_fingerprints") == sources,
        "the additive audit changed the canonical measured production-source set",
    )

    audited_native = report.get("native_elf_fingerprints")
    require(
        isinstance(audited_native, dict)
        and len(audited_native) == 5
        and audited_native == native,
        "the additive audit does not bind all five current independently owned native binaries",
    )
    native_provenance = report.get("native_elf_provenance")
    require(
        isinstance(native_provenance, dict)
        and native_provenance.get("passed") is True
        and native_provenance.get("audited_binary_count") == 5
        and native_provenance.get("expected_binary_count") == 5,
        "the additive audit did not independently verify all five native ELFs",
    )

    controls = report.get("self_test")
    require(isinstance(controls, dict), "the additive audit omitted its adversarial controls")
    checks = controls.get("checks")
    require(
        controls.get("passed") is True
        and controls.get("check_count") == POSTFINAL_AUDIT_CONTROL_COUNT
        and isinstance(checks, list)
        and len(checks) == POSTFINAL_AUDIT_CONTROL_COUNT
        and all(
            isinstance(check, dict)
            and isinstance(check.get("name"), str)
            and check.get("passed") is True
            for check in checks
        )
        and len({check["name"] for check in checks}) == POSTFINAL_AUDIT_CONTROL_COUNT
        and controls.get("failed") == [],
        "the additive no-delegation audit did not pass all 32 distinct poison controls",
    )
    require(
        controls.get("fixture_storage") == "in-memory only"
        and controls.get("candidate_imported") is False
        and controls.get("benchmark_or_timing_executed") is False
        and controls.get("holdout_or_case_fixture_access") is False,
        "an additive synthetic control imported an engine or accessed benchmark cases",
    )

    scope = report.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("explicit_source_paths_only") is True
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("candidate_imports")
        == "isolated guarded subprocesses only"
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the additive audit weakened its guarded runtime or public-only scope",
    )
    require_candidate_free()
    details: dict[str, Any] = {
        "postfinal_no_delegation_audit_path": str(POSTFINAL_AUDIT_PATH.resolve()),
        "postfinal_no_delegation_audit_sha256": pilot.file_sha256(
            POSTFINAL_AUDIT_PATH
        ),
        "postfinal_no_delegation_audit_source_path": str(
            POSTFINAL_AUDIT_SOURCE_PATH.resolve()
        ),
        "postfinal_no_delegation_audit_source_sha256": audit_source_digest,
        "postfinal_no_delegation_audit_schema": POSTFINAL_AUDIT_SCHEMA,
        "postfinal_no_delegation_control_count": POSTFINAL_AUDIT_CONTROL_COUNT,
    }
    return original_digest, sources, native, details


def require_no_universal_worker_failure(
    report: dict[str, Any],
    label: str,
) -> None:
    """Reject partial, crashed, or failed evidence even if a count is absent."""

    for field in (
        "failed",
        "failures",
        "crashes",
        "crash_count",
        "worker_crashes",
        "worker_failure",
        "worker_failures",
        "worker_errors",
        "worker_error",
        "error",
        "errors",
    ):
        if field in report:
            value = report[field]
            require(
                value is None
                or value is False
                or (
                    isinstance(value, int)
                    and not isinstance(value, bool)
                    and value == 0
                )
                or (isinstance(value, (list, dict)) and not value),
                f"the universal public {label} records a failure: {field}",
            )


def verified_python_re_universal_oracle(
    original_audit_sha256: str,
    qualified_sources: dict[str, str],
    native_fingerprints: dict[str, str],
    additive_audit: dict[str, Any],
) -> dict[str, Any]:
    """Require the complete zero-failure, all-engine CPython public oracle."""

    require_candidate_free()
    require(
        UNIVERSAL_ORACLE_SOURCE_PATH.is_file(),
        "the immutable stage-03 all-engine Python re public wrapper is missing",
    )
    require(
        pilot.file_sha256(UNIVERSAL_ORACLE_SOURCE_PATH)
        == UNIVERSAL_ORACLE_SOURCE_SHA256,
        "the immutable stage-03 universal public wrapper was changed",
    )
    require(
        UNIVERSAL_ORACLE_FROZEN_SOURCE_PATH.is_file()
        and pilot.file_sha256(UNIVERSAL_ORACLE_FROZEN_SOURCE_PATH)
        == UNIVERSAL_ORACLE_FROZEN_SOURCE_SHA256,
        "the immutable underlying V1 universal public source was changed",
    )
    require(
        UNIVERSAL_ORACLE_CASES == 8_192
        and UNIVERSAL_ORACLE_OBSERVATIONS_PER_CASE == 48
        and UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE == 393_216
        and UNIVERSAL_ORACLE_TOTAL_OBSERVATIONS == 1_179_648,
        "the prospective all-engine Python re oracle denominator changed",
    )
    report = read_json(
        UNIVERSAL_ORACLE_REPORT_PATH,
        "complete passing all-candidate Python re universal public oracle",
    )
    require_no_universal_worker_failure(report, "all-candidate report")
    require(
        report.get("schema") == UNIVERSAL_ORACLE_SCHEMA
        and report.get("status") == "PASS"
        and report.get("selected") == "all"
        and report.get("selected_candidates")
        == list(UNIVERSAL_ORACLE_CANDIDATES)
        and report.get("comparison_complete") is True
        and report.get("completed_candidates")
        == list(UNIVERSAL_ORACLE_CANDIDATES)
        and report.get("failed_candidate") is None
        and report.get("worker_failure") is None,
        "the universal public Python re oracle did not genuinely pass all three candidates",
    )
    require(
        report.get("python") == "3.14.6"
        and report.get("seed") == UNIVERSAL_ORACLE_SEED
        and report.get("seed_domain") == UNIVERSAL_ORACLE_SEED_DOMAIN,
        "the universal public Python re case generator or seed domain changed",
    )
    require(
        UNIVERSAL_ORACLE_SEED
        not in {
            SELECTION_SEED,
            ORDER_SEED,
            BOOTSTRAP_SEED,
            previous.SELECTION_SEED,
            previous.ORDER_SEED,
            previous.BOOTSTRAP_SEED,
        },
        "the universal Python re oracle reused a public benchmark seed domain",
    )
    require(
        report.get("cases") == UNIVERSAL_ORACLE_CASES
        and report.get("observations_per_case")
        == UNIVERSAL_ORACLE_OBSERVATIONS_PER_CASE
        and report.get("observations_per_candidate")
        == UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE
        and report.get("total_comparisons")
        == UNIVERSAL_ORACLE_TOTAL_OBSERVATIONS
        and report.get("planned_total_comparisons")
        == UNIVERSAL_ORACLE_TOTAL_OBSERVATIONS
        and report.get("mismatches") == 0,
        "the universal Python re oracle omitted, mismatched, or duplicated comparisons",
    )
    require(
        report.get("grammar_family_count") == UNIVERSAL_ORACLE_GRAMMAR_FAMILIES
        and report.get("input_stratum_count") == UNIVERSAL_ORACLE_INPUT_STRATA
        and report.get("examples_per_stratum")
        == UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM,
        "the universal Python re oracle changed its exhaustive public coverage",
    )
    family_counts = report.get("grammar_family_counts")
    stratum_counts = report.get("input_stratum_counts")
    require(
        isinstance(family_counts, dict)
        and len(family_counts) == UNIVERSAL_ORACLE_GRAMMAR_FAMILIES
        and all(
            type(count) is int
            and count == UNIVERSAL_ORACLE_CASES // UNIVERSAL_ORACLE_GRAMMAR_FAMILIES
            for count in family_counts.values()
        ),
        "the universal Python re oracle omitted a balanced grammar family",
    )
    require(
        isinstance(stratum_counts, dict)
        and len(stratum_counts) == UNIVERSAL_ORACLE_INPUT_STRATA
        and all(
            type(count) is int
            and count == UNIVERSAL_ORACLE_CASES // UNIVERSAL_ORACLE_INPUT_STRATA
            for count in stratum_counts.values()
        ),
        "the universal Python re oracle omitted a balanced public input stratum",
    )
    case_digest = report.get("case_sha256")
    require(
        valid_sha256(case_digest),
        "the universal Python re oracle has no frozen generated-case digest",
    )
    require(
        report.get("performance") == "NOT MEASURED"
        and report.get("benchmark_or_timing_executed") is False
        and report.get("performance_fixtures_read") == 0
        and report.get("holdout") == "NOT ACCESSED"
        and report.get("holdout_cases_read") == 0
        and report.get("external_regex_packages") == 0,
        "the universal Python re oracle performed timing or accessed nonpublic cases",
    )

    provenance = report.get("audit")
    require(
        isinstance(provenance, dict)
        and provenance.get("audit_path")
        == str(AUDIT_PATH.resolve().relative_to(ROOT.resolve()))
        and provenance.get("audit_sha256") == original_audit_sha256
        and provenance.get("oracle_source_path")
        == str(UNIVERSAL_ORACLE_SOURCE_PATH.resolve().relative_to(ROOT.resolve()))
        and provenance.get("oracle_source_sha256")
        == pilot.file_sha256(UNIVERSAL_ORACLE_SOURCE_PATH)
        and provenance.get("python_executable")
        == str(replay.PINNED_PYTHON.resolve())
        and provenance.get("selected_candidates")
        == list(UNIVERSAL_ORACLE_CANDIDATES),
        "the universal Python re oracle changed its audited source or pinned interpreter",
    )

    source_groups = provenance.get("source_sha256")
    require(
        isinstance(source_groups, dict)
        and set(source_groups) == set(UNIVERSAL_ORACLE_CANDIDATES),
        "the universal Python re oracle omitted an audited candidate source family",
    )
    flat_sources: dict[str, str] = {}
    for family in UNIVERSAL_ORACLE_CANDIDATES:
        family_sources = source_groups[family]
        require(
            isinstance(family_sources, dict) and bool(family_sources),
            f"the universal Python re oracle omitted {family} source fingerprints",
        )
        for relative, expected in family_sources.items():
            require(
                isinstance(relative, str)
                and valid_sha256(expected)
                and relative not in flat_sources,
                f"the universal Python re oracle duplicated a {family} source",
            )
            path = checked_owned_source(relative, f"universal {family}")
            require(
                pilot.file_sha256(path) == expected,
                f"an independently qualified universal {family} source changed",
            )
            flat_sources[relative] = expected
    require(
        flat_sources == qualified_sources,
        "the universal Python re and original audit production-source graphs disagree",
    )

    native_groups = provenance.get("native_binary_sha256")
    require(
        isinstance(native_groups, dict)
        and set(native_groups) == set(UNIVERSAL_ORACLE_CANDIDATES),
        "the universal Python re oracle omitted a candidate's native binaries",
    )
    for family in UNIVERSAL_ORACLE_CANDIDATES:
        expected_keys = UNIVERSAL_ORACLE_NATIVE_FINGERPRINT_KEYS[family]
        actual = native_groups[family]
        require(
            isinstance(actual, dict) and set(actual) == set(expected_keys),
            f"the universal Python re oracle changed {family} native binary roles",
        )
        for relative, fingerprint_key in expected_keys.items():
            expected = native_fingerprints.get(fingerprint_key)
            require(
                valid_sha256(expected)
                and actual.get(relative) == expected
                and pilot.file_sha256(
                    checked_owned_source(relative, f"universal {family} native")
                )
                == expected,
                f"the universal Python re oracle substituted {family}'s native ELF",
            )

    original_campaign = provenance.get("original_public_campaign")
    require(
        isinstance(original_campaign, dict)
        and set(original_campaign)
        == {"quote-parity-stage-03", "public-practice-v3"},
        "the universal Python re oracle dropped an original public campaign",
    )
    public_campaign = original_campaign["public-practice-v3"]
    require(
        isinstance(public_campaign, dict)
        and public_campaign.get("path")
        == "tools/postfinal_public_practice_v3.py"
        and public_campaign.get("sha256") == V3_RUNNER_SHA256,
        "the universal Python re oracle substituted the frozen public v3 source",
    )
    quote_campaign = original_campaign["quote-parity-stage-03"]
    require(
        isinstance(quote_campaign, dict)
        and quote_campaign.get("path")
        == "tools/rust_postfinal_quote_parity_stage03_oracle.py"
        and valid_sha256(quote_campaign.get("sha256"))
        and pilot.file_sha256(
            ROOT / "tools" / "rust_postfinal_quote_parity_stage03_oracle.py"
        )
        == quote_campaign["sha256"],
        "the universal Python re oracle substituted the original quote campaign",
    )

    reports = report.get("candidate_reports")
    require(
        isinstance(reports, dict)
        and set(reports) == set(UNIVERSAL_ORACLE_CANDIDATES),
        "the universal Python re oracle omitted or substituted a native candidate",
    )
    for family in UNIVERSAL_ORACLE_CANDIDATES:
        item = reports[family]
        require(
            isinstance(item, dict),
            f"the universal Python re {family} report is missing",
        )
        require_no_universal_worker_failure(item, family)
        module = f"candidates.{family}_candidate"
        reference_digest = item.get("reference_observation_sha256")
        require(
            item.get("candidate") == family
            and item.get("module") == module
            and item.get("status") == "PASS"
            and item.get("comparison_complete") is True
            and item.get("cases") == UNIVERSAL_ORACLE_CASES
            and item.get("case_sha256") == case_digest
            and item.get("checks")
            == UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE
            and item.get("expected_checks")
            == UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE
            and item.get("observations_per_case")
            == UNIVERSAL_ORACLE_OBSERVATIONS_PER_CASE
            and item.get("mismatches") == 0
            and item.get("worker_failure") is None
            and item.get("mismatch_examples") == []
            and item.get("mismatch_examples_truncated") is False
            and valid_sha256(reference_digest)
            and item.get("candidate_observation_sha256")
            == reference_digest,
            f"the universal Python re {family} comparison is partial or mismatched",
        )
        operation_counts = item.get("operation_counts")
        require(
            isinstance(operation_counts, dict)
            and bool(operation_counts)
            and all(
                isinstance(operation, str)
                and type(count) is int
                and count > 0
                for operation, count in operation_counts.items()
            )
            and sum(operation_counts.values())
            == UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE,
            f"the universal Python re {family} dropped an observable public operation",
        )
        guards = item.get("poison_guards")
        expected_guards = {
            "stdlib-re",
            "cpython-sre",
            "third-party-regex",
            "third-party-re2",
            "ast-candidate",
            *(
                f"{other}-candidate"
                for other in UNIVERSAL_ORACLE_CANDIDATES
                if other != family
            ),
        }
        require(
            isinstance(guards, dict)
            and set(guards) == expected_guards
            and all(value is True for value in guards.values()),
            f"the universal Python re {family} lost a no-delegation poison guard",
        )
        require(
            item.get("performance_fixtures_read") == 0
            and item.get("holdout_cases_read") == 0
            and item.get("external_regex_packages") == 0
            and item.get("benchmark_or_timing_executed") is False,
            f"the universal Python re {family} accessed timing or nonpublic data",
        )

        artifacts = item.get("candidate_artifacts")
        require(
            isinstance(artifacts, dict)
            and artifacts.get("family") == family
            and artifacts.get("module") == module,
            f"the universal Python re {family} substituted its loaded engine",
        )
        mappings = artifacts.get("native_mappings")
        expected_paths = UNIVERSAL_ORACLE_NATIVE_FINGERPRINT_KEYS[family]
        require(
            isinstance(mappings, list)
            and len(mappings) == len(expected_paths),
            f"the universal Python re {family} omitted an actual native mapping",
        )
        observed_paths: set[str] = set()
        for mapping in mappings:
            require(
                isinstance(mapping, dict),
                f"the universal Python re {family} returned invalid native evidence",
            )
            relative = mapping.get("path")
            require(
                isinstance(relative, str)
                and relative in expected_paths
                and relative not in observed_paths,
                f"the universal Python re {family} substituted a native role",
            )
            observed_paths.add(relative)
            require(
                mapping.get("role")
                == UNIVERSAL_ORACLE_NATIVE_MAPPING_ROLES[family][relative]
                and mapping.get("sha256")
                == native_fingerprints[expected_paths[relative]]
                and type(mapping.get("mapping_count")) is int
                and mapping["mapping_count"] > 0,
                f"the universal Python re {family} did not actually map its audited ELF",
            )
        require(
            observed_paths == set(expected_paths),
            f"the universal Python re {family} concealed a loaded native engine",
        )

    require_candidate_free()
    return {
        "python_re_universal_oracle_source_path": str(
            UNIVERSAL_ORACLE_SOURCE_PATH.resolve()
        ),
        "python_re_universal_oracle_source_sha256": provenance[
            "oracle_source_sha256"
        ],
        "python_re_universal_oracle_report_path": str(
            UNIVERSAL_ORACLE_REPORT_PATH.resolve()
        ),
        "python_re_universal_oracle_report_sha256": pilot.file_sha256(
            UNIVERSAL_ORACLE_REPORT_PATH
        ),
        "python_re_universal_oracle_schema": UNIVERSAL_ORACLE_SCHEMA,
        "python_re_universal_oracle_status": "PASS",
        "python_re_universal_oracle_selected": "all",
        "python_re_universal_oracle_candidates": list(
            UNIVERSAL_ORACLE_CANDIDATES
        ),
        "python_re_universal_oracle_cases": UNIVERSAL_ORACLE_CASES,
        "python_re_universal_oracle_comparisons_per_case": (
            UNIVERSAL_ORACLE_OBSERVATIONS_PER_CASE
        ),
        "python_re_universal_oracle_comparisons_per_candidate": (
            UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE
        ),
        "python_re_universal_oracle_total_comparisons": (
            UNIVERSAL_ORACLE_TOTAL_OBSERVATIONS
        ),
        "python_re_universal_oracle_mismatches": 0,
        "python_re_universal_oracle_seed": UNIVERSAL_ORACLE_SEED,
        "python_re_universal_oracle_seed_domain": UNIVERSAL_ORACLE_SEED_DOMAIN,
        "python_re_universal_oracle_case_sha256": case_digest,
        "python_re_universal_oracle_grammar_family_count": (
            UNIVERSAL_ORACLE_GRAMMAR_FAMILIES
        ),
        "python_re_universal_oracle_input_stratum_count": (
            UNIVERSAL_ORACLE_INPUT_STRATA
        ),
        "python_re_universal_oracle_examples_per_stratum": (
            UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM
        ),
        "python_re_universal_oracle_original_audit_sha256": (
            original_audit_sha256
        ),
        "python_re_universal_oracle_postfinal_no_delegation_audit_sha256": (
            additive_audit["postfinal_no_delegation_audit_sha256"]
        ),
        "python_re_universal_oracle_frozen_source_path": str(
            UNIVERSAL_ORACLE_FROZEN_SOURCE_PATH.resolve()
        ),
        "python_re_universal_oracle_frozen_source_sha256": (
            UNIVERSAL_ORACLE_FROZEN_SOURCE_SHA256
        ),
    }


def make_manifest(
    edge_paths: list[Path],
) -> tuple[types.SimpleNamespace, list[SelectedEntry], dict[str, Any]]:
    """Prospectively select 8,192 real, unique, calibration-only public cases."""

    require_candidate_free()
    require_pinned_python()
    verified_public_v3_source()
    require(
        tuple(path.resolve() for path in edge_paths)
        == tuple(path.resolve() for path in DEFAULT_EDGE_ORACLES),
        "expanded public practice requires the exact fresh stage-05 Rust, VM, and Zig edge proofs",
    )
    stage05_artifacts = verified_stage05_correctness_artifacts()
    audit_digest, source_fingerprints, native_fingerprints, additive_audit = (
        verified_from_scratch_audit()
    )
    universal_oracle = verified_python_re_universal_oracle(
        audit_digest,
        source_fingerprints,
        native_fingerprints,
        additive_audit,
    )

    require(pilot.MAX_CASES == 700, "the immutable original public pilot changed")
    require(pilot.MAX_SUBJECT == 8_192, "the inherited subject safety bound changed")
    require(pilot.MAX_RESULTS == 128, "the inherited result safety bound changed")
    require(pilot.MAX_OPERATIONS == MAX_OPERATIONS, "the inherited operation bound changed")
    source_suite, pairs, parent, _history, fixture_manifest = (
        pilot.load_calibration_fixture()
    )
    require(
        len(pairs) == FIXTURE_CASES
        and source_suite.CASES_PER_COHORT == FIXTURE_CASES,
        "the frozen calibration-only public fixture changed",
    )
    require(
        source_suite.TRIALS == TRIALS
        and source_suite.WARMUPS == WARMUPS
        and source_suite.BOOTSTRAPS == BOOTSTRAPS,
        "the inherited public warmup, paired-trial, or bootstrap protocol changed",
    )
    require(
        set(source_suite.SEEDS) == {pilot.PRACTICE},
        "the frozen public fixture exposes a noncalibration case domain",
    )
    require(
        set(MODULES) <= set(source_suite.MODULES),
        "an independently qualified baseline or native engine is missing",
    )
    require(
        not {SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}
        & {
            source_suite.SEEDS[pilot.PRACTICE],
            source_suite.ORDER_SEED,
            source_suite.BOOTSTRAP_SEED,
        },
        "expanded public practice reused an original calibration seed",
    )

    entries, quotas = previous.select_entries(
        pairs,
        CASES,
        SELECTION_SEED,
        expected_eligible=ELIGIBLE_CASES,
        expected_categories=CATEGORIES,
        expected_api_counts=EXPECTED_BOUNDED_API_COUNTS,
    )
    require(len(entries) == CASES, "the frozen 8,192-case denominator changed")
    require(
        len({case["id"] for _, case, _, _ in entries}) == CASES,
        "the expanded public selection duplicated a case",
    )
    require(
        len(quotas) == PUBLIC_APIS and sum(quotas.values()) == CASES,
        "capacity-aware public operation quotas changed",
    )
    require(
        all(0 < count <= EXPECTED_BOUNDED_API_COUNTS[api] for api, count in quotas.items()),
        "expanded public selection exceeded an actual bounded API capacity",
    )

    suite = types.SimpleNamespace(
        MODULES=source_suite.MODULES,
        CASES_PER_COHORT=source_suite.CASES_PER_COHORT,
        SEEDS={pilot.PRACTICE: SELECTION_SEED},
        ORDER_SEED=ORDER_SEED,
        BOOTSTRAP_SEED=BOOTSTRAP_SEED,
        TRIALS=TRIALS,
        WARMUPS=WARMUPS,
        BOOTSTRAPS=BOOTSTRAPS,
    )
    eligible = [
        (position, case, expected)
        for position, case, expected in pairs
        if pilot.bounded(case, expected)
    ]
    require(
        len(eligible) == ELIGIBLE_CASES,
        "the public calibration-only eligible capacity changed",
    )
    categories = collections.Counter(case["category"] for _, case, _, _ in entries)
    lifetimes = collections.Counter(case["lifecycle"] for _, case, _, _ in entries)
    inputs = collections.Counter(
        pilot.source_kind(case) for _, case, _, _ in entries
    )
    densities = collections.Counter(
        pilot.density(expected["result"]) for _, _, expected, _ in entries
    )
    api_lifetimes = collections.Counter(
        (case["api"], case["lifecycle"]) for _, case, _, _ in entries
    )
    require(len(categories) == CATEGORIES, "an existing public category was omitted")
    require(
        set(lifetimes) == {case["lifecycle"] for _, case, _ in eligible},
        "an available public lifecycle was omitted",
    )
    require(
        set(inputs) == {pilot.source_kind(case) for _, case, _ in eligible},
        "an available text or mutable-buffer representation was omitted",
    )
    require(
        set(densities)
        == {pilot.density(expected["result"]) for _, _, expected in eligible},
        "an available public result-density stratum was omitted",
    )
    require(
        set(api_lifetimes)
        == {(case["api"], case["lifecycle"]) for _, case, _ in eligible},
        "an available legal public API/lifecycle stratum was omitted",
    )

    edge_oracles = pilot.verified_edge_oracles(edge_paths, MODULES)
    require(
        len(edge_oracles) == len(MODULES) - 1,
        "a measured candidate has no independently qualified edge proof",
    )
    require_candidate_free()
    document: dict[str, Any] = {
        "schema": pilot.PLAN_SCHEMA,
        "postfinal_schema": POSTFINAL_PLAN_SCHEMA,
        "protocol_version": VERSION,
        "measurement": "balanced practice diagnostic; never a holdout ranking or final speed claim",
        "measurement_role": "additive expanded public practice only; not a held-out or final result",
        "python": parent["python"],
        "cohort": pilot.PRACTICE,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "historical_performance_read": False,
        "timing_performed": False,
        "expected_sha256": parent["expected_sha256"],
        "source_fixture": fixture_manifest["fixture"],
        "source_fixture_sha256": fixture_manifest["fixture_sha256"],
        "source_fixture_uncompressed_sha256": fixture_manifest[
            "uncompressed_fixture_sha256"
        ],
        "source_fixture_manifest_sha256": pilot.file_sha256(
            pilot.DEFAULT_FIXTURE_MANIFEST
        ),
        "source_v7_manifest_sha256": fixture_manifest["source_v7_manifest_sha256"],
        "source_v7_suite_sha256": fixture_manifest["source_v7_suite_sha256"],
        "source_v7_runner_sha256": fixture_manifest["source_v7_runner_sha256"],
        "source_public_pilot_sha256": pilot.file_sha256(
            Path(pilot.__file__).resolve()
        ),
        "source_public_replay_sha256": pilot.file_sha256(
            Path(replay.__file__).resolve()
        ),
        "source_public_v3_manifest_sha256": V3_MANIFEST_SHA256,
        "source_public_v3_runner_sha256": V3_RUNNER_SHA256,
        "runner_sha256": pilot.file_sha256(Path(__file__).resolve()),
        "from_scratch_audit_path": str(AUDIT_PATH.resolve()),
        "from_scratch_audit_sha256": audit_digest,
        "from_scratch_audit_source_path": str(AUDIT_SOURCE_PATH.resolve()),
        "from_scratch_audit_source_sha256": pilot.file_sha256(
            AUDIT_SOURCE_PATH
        ),
        **additive_audit,
        **universal_oracle,
        "qualified_source_fingerprints": source_fingerprints,
        "native_elf_fingerprints": native_fingerprints,
        "verified_edge_oracles": edge_oracles,
        "stage05_correctness_artifacts": stage05_artifacts,
        "modules": list(MODULES),
        "exclusive_slot": EXCLUSIVE_SLOT,
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "frozen_trials": TRIALS,
        "frozen_warmups": WARMUPS,
        "frozen_bootstrap_samples": BOOTSTRAPS,
        "default_trials": TRIALS,
        "default_bootstrap_samples": BOOTSTRAPS,
        "cases": len(entries),
        "source_public_cases": FIXTURE_CASES,
        "eligible_practice_cases": ELIGIBLE_CASES,
        "all_bounded_workload_categories": len(categories),
        "bounded_public_api_capacities": dict(
            sorted(EXPECTED_BOUNDED_API_COUNTS.items())
        ),
        "public_operations": quotas,
        "lifetimes": dict(sorted(lifetimes.items())),
        "inputs": dict(sorted(inputs.items())),
        "result_densities": dict(sorted(densities.items())),
        "api_lifetimes": {
            f"{api} / {lifecycle}": count
            for (api, lifecycle), count in sorted(api_lifetimes.items())
        },
        "categories": dict(sorted(categories.items())),
        "maximum_subject_length": max(
            pilot.input_length(case) for _, case, _, _ in entries
        ),
        "maximum_result_count": max(
            pilot.cardinality(expected["result"]) for _, _, expected, _ in entries
        ),
        "maximum_subject_limit": pilot.MAX_SUBJECT,
        "maximum_result_limit": pilot.MAX_RESULTS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "strict_regression_speedup_threshold": pilot.REGRESSION_SPEEDUP_THRESHOLD,
        "execution_topology": (
            "four persistent process-isolated engines; one pinned CPython baseline "
            "worker and one permanently guarded worker for each native candidate"
        ),
        "runtime_native_hash_policy": RUNTIME_NATIVE_HASH_POLICY,
        "execution_safety": (
            "Candidate-free paired controller; no shared baseline or cross-candidate "
            "interpreter; additive-audited import, reachable-regex, and native-loader "
            "guards; independently checked loaded native mappings before and after "
            "every frozen public case; exact pre-sample, allocation-sample, and "
            "post-timing CPython-answer gates for every paired observation."
        ),
        "selected_cases": [
            {
                "case": case["id"],
                "cohort": case["cohort"],
                "category": case["category"],
                "api": case["api"],
                "lifecycle": case["lifecycle"],
                "input": pilot.source_kind(case),
                "subject_length": pilot.input_length(case),
                "result_count": pilot.cardinality(expected["result"]),
                "result_density": pilot.density(expected["result"]),
                "frozen_operations": case["ops"],
                "expected_result_sha256": expected["result_sha256"],
                "selection_reasons": list(reasons),
            }
            for _, case, expected, reasons in entries
        ],
        "failed": 0,
    }
    require(
        document["maximum_subject_length"] <= pilot.MAX_SUBJECT,
        "the expanded public subject bound weakened",
    )
    require(
        document["maximum_result_count"] <= pilot.MAX_RESULTS,
        "the expanded public result bound weakened",
    )
    require(
        document["strict_regression_speedup_threshold"] == 5.0 / 6.0,
        "the strict substantial-regression threshold weakened",
    )
    return suite, entries, document


def load_frozen_manifest(
    path: Path,
) -> tuple[types.SimpleNamespace, list[SelectedEntry], dict[str, Any], str]:
    manifest_path = exact_versioned_path(
        path,
        MANIFEST_PATH,
        "frozen expanded public-practice manifest",
    )
    document = read_json(manifest_path, "frozen expanded public-practice manifest")
    require(
        document.get("postfinal_schema") == POSTFINAL_PLAN_SCHEMA,
        "the expanded public manifest schema changed",
    )
    require(
        document.get("protocol_version") == VERSION,
        "the expanded public protocol version changed",
    )
    proofs = document.get("verified_edge_oracles")
    require(
        isinstance(proofs, list) and len(proofs) == len(MODULES) - 1,
        "the frozen expanded public edge proofs are missing",
    )
    paths: list[Path] = []
    for proof in proofs:
        require(
            isinstance(proof, dict) and isinstance(proof.get("path"), str),
            "an expanded public edge proof has no frozen source path",
        )
        paths.append(Path(proof["path"]))
    suite, entries, actual = make_manifest(paths)
    require(
        document == actual,
        "the frozen expanded public cases, source, audits, or native artifacts changed",
    )
    return suite, entries, document, pilot.file_sha256(manifest_path)


def synthetic_self_test() -> dict[str, Any]:
    """Exercise only in-memory public selection and inherited poison controls."""

    require_candidate_free()
    require_stage05_correctness_path_contract()
    require(
        len(UNIVERSAL_ORACLE_PROOF_FIELDS) == 23
        and len(set(UNIVERSAL_ORACLE_PROOF_FIELDS)) == 23
        and UNIVERSAL_ORACLE_PROOF_FIELDS[-2:]
        == (
            "python_re_universal_oracle_frozen_source_path",
            "python_re_universal_oracle_frozen_source_sha256",
        ),
        "the complete stage-03 and immutable V1 public proof fields changed",
    )
    inherited = previous.synthetic_self_test()
    require(
        inherited.get("result") == "PASS"
        and inherited.get("holdout_accessed") is False
        and inherited.get("held_out_cases_generated") == 0
        and inherited.get("held_out_records_deserialized") == 0
        and inherited.get("timing_performed") is False
        and inherited.get("candidate_imported") is False,
        "candidate-free inherited public selection controls failed",
    )

    synthetic: list[Entry] = []
    for api_index, api in enumerate(sorted(EXPECTED_BOUNDED_API_COUNTS)):
        for variant in range(12 + api_index % 4):
            identifier = f"cal.postfinal.v4.synthetic.{api}.{variant:02d}"
            use_bytes = variant % 5 == 0
            result: Any = (
                None if variant % 4 == 0 else ["synthetic"] * (1 + variant % 3)
            )
            lifecycle = (
                "cold"
                if api == "compile"
                else "module"
                if api == "escape"
                else "compiled"
            )
            case: dict[str, Any] = {
                "id": identifier,
                "cohort": pilot.PRACTICE,
                "category": f"v4-synthetic-{api}-{variant % 2}",
                "api": api,
                "lifecycle": lifecycle,
                "pattern": b"synthetic" if use_bytes else "synthetic",
                "string": b"synthetic" if use_bytes else "synthetic",
                "flags": ["I"] if variant % 3 == 0 else [],
                "ops": MAX_OPERATIONS,
                "weight": 1,
            }
            if use_bytes:
                case["subject_kind"] = (
                    "bytes",
                    "bytearray",
                    "memoryview",
                )[variant % 3]
            if variant % 4 == 1:
                case["pos"] = 0
            expected = {
                "id": identifier,
                "cohort": pilot.PRACTICE,
                "category": case["category"],
                "result": result,
                "result_sha256": pilot.digest(result),
            }
            synthetic.append((len(synthetic), case, expected))

    selected, quotas = previous.select_entries(
        synthetic,
        96,
        SELECTION_SEED,
        expected_eligible=len(synthetic),
        expected_categories=24,
    )
    repeated, repeated_quotas = previous.select_entries(
        list(reversed(synthetic)),
        96,
        SELECTION_SEED,
        expected_eligible=len(synthetic),
        expected_categories=24,
    )
    require(
        selected == repeated and quotas == repeated_quotas,
        "expanded public selection depends on mutable fixture iteration order",
    )
    require(
        len(quotas) == PUBLIC_APIS and sum(quotas.values()) == 96,
        "expanded synthetic capacity-aware API quotas changed",
    )
    require(
        len({case["category"] for _, case, _, _ in selected}) == 24,
        "expanded synthetic category coverage changed",
    )
    require(
        all(pilot.bounded(case, expected) for _, case, expected, _ in selected),
        "expanded synthetic selection weakened a public safety bound",
    )
    require(
        len({SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}) == 3
        and not {SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}
        & {previous.SELECTION_SEED, previous.ORDER_SEED, previous.BOOTSTRAP_SEED},
        "expanded synthetic controls reused a public seed domain",
    )
    require(
        EXPECTED_ROWS == 425_984
        and EXPECTED_CORRECTNESS_CHECKS == 1_277_952
        and EXPECTED_CONFIDENCE_INTERVALS == 24_579
        and EXPECTED_RUNTIME_GUARD_CHECKS == 65_544
        and UNIVERSAL_ORACLE_CASES == 8_192
        and UNIVERSAL_ORACLE_OBSERVATIONS_PER_CASE == 48
        and UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE == 393_216
        and UNIVERSAL_ORACLE_TOTAL_OBSERVATIONS == 1_179_648
        and UNIVERSAL_ORACLE_SEED
        not in {
            SELECTION_SEED,
            ORDER_SEED,
            BOOTSTRAP_SEED,
            previous.SELECTION_SEED,
            previous.ORDER_SEED,
            previous.BOOTSTRAP_SEED,
        },
        "the prospective expanded paired denominators changed",
    )

    controls: list[dict[str, Any]] = []

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except (
            RuntimeError,
            replay.AuditError,
            KeyError,
            TypeError,
            ValueError,
        ):
            controls.append({"name": name, "passed": True})
            return
        raise RuntimeError(f"expanded synthetic poison was accepted: {name}")

    require(
        checked_owned_source("pyproject.toml", "synthetic root build")
        == (ROOT / "pyproject.toml").resolve(),
        "the exact audited root build input was not accepted",
    )
    owned_source_controls: list[dict[str, Any]] = []
    for name, value in (
        ("root-build-absolute-path", str((ROOT / "pyproject.toml").resolve())),
        ("root-build-parent-traversal", "candidates/../pyproject.toml"),
        ("root-build-alternate-spelling", "./pyproject.toml"),
        ("unauthorized-root-build-input", "other-root-build.toml"),
    ):
        try:
            checked_owned_source(value, name)
        except RuntimeError:
            owned_source_controls.append({"name": name, "passed": True})
        else:
            raise RuntimeError(f"expanded synthetic source poison was accepted: {name}")

    position, first_case, first_expected = synthetic[0]

    def substitute(case: dict[str, Any], expected: dict[str, Any]) -> list[Entry]:
        return [(position, case, expected), *synthetic[1:]]

    reject(
        "nonpublic-case-cohort",
        lambda: previous.select_entries(
            substitute({**first_case, "cohort": "holdout"}, first_expected),
            96,
            SELECTION_SEED,
        ),
    )
    reject(
        "nonpublic-answer-cohort",
        lambda: previous.select_entries(
            substitute(first_case, {**first_expected, "cohort": "holdout"}),
            96,
            SELECTION_SEED,
        ),
    )
    reject(
        "substituted-expected-digest",
        lambda: previous.select_entries(
            substitute(
                first_case,
                {**first_expected, "result_sha256": "0" * 64},
            ),
            96,
            SELECTION_SEED,
        ),
    )
    reject(
        "nonunit-public-case-weight",
        lambda: previous.select_entries(
            substitute({**first_case, "weight": 2}, first_expected),
            96,
            SELECTION_SEED,
        ),
    )
    reject(
        "duplicate-public-case",
        lambda: previous.select_entries(
            [*synthetic, synthetic[0]],
            96,
            SELECTION_SEED,
        ),
    )
    reject(
        "concealed-public-category",
        lambda: previous.select_entries(
            synthetic,
            96,
            SELECTION_SEED,
            expected_categories=25,
        ),
    )
    reject(
        "changed-eligible-public-denominator",
        lambda: previous.select_entries(
            synthetic,
            96,
            SELECTION_SEED,
            expected_eligible=len(synthetic) + 1,
        ),
    )
    reject(
        "oversubscribed-public-api",
        lambda: previous.allocate_quotas(
            collections.Counter({"search": 1}),
            collections.Counter(),
            2,
            SELECTION_SEED,
        ),
    )
    reject(
        "substituted-historical-manifest",
        lambda: exact_versioned_path(
            previous.MANIFEST_PATH,
            MANIFEST_PATH,
            "expanded synthetic public manifest",
        ),
    )
    reject(
        "substituted-historical-observations",
        lambda: exact_versioned_path(
            previous.RAW_PATH,
            RAW_PATH,
            "expanded synthetic public observations",
        ),
    )
    require(pilot.MAX_CASES == 700, "the original 700-case pilot was changed")
    require(
        pilot.MAX_SUBJECT == 8_192 and pilot.MAX_RESULTS == 128,
        "an inherited public bound was weakened",
    )
    require(
        pilot.REGRESSION_SPEEDUP_THRESHOLD == 5.0 / 6.0,
        "the strict public slowdown boundary was weakened",
    )
    require_candidate_free()
    return {
        "schema": POSTFINAL_INTEGRITY_SCHEMA + "-self-test",
        "result": "PASS",
        "protocol_version": VERSION,
        "synthetic_only": True,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "candidate_imported": False,
        "synthetic_cases": 96,
        "synthetic_public_operations": len(quotas),
        "synthetic_categories": 24,
        "prospective_cases": CASES,
        "prospective_paired_rows": EXPECTED_ROWS,
        "prospective_correctness_checks": EXPECTED_CORRECTNESS_CHECKS,
        "prospective_confidence_intervals": EXPECTED_CONFIDENCE_INTERVALS,
        "prospective_runtime_guard_checks": EXPECTED_RUNTIME_GUARD_CHECKS,
        "prospective_universal_oracle_cases": UNIVERSAL_ORACLE_CASES,
        "prospective_universal_oracle_comparisons_per_case": (
            UNIVERSAL_ORACLE_OBSERVATIONS_PER_CASE
        ),
        "prospective_universal_oracle_comparisons_per_candidate": (
            UNIVERSAL_ORACLE_OBSERVATIONS_PER_CANDIDATE
        ),
        "prospective_universal_oracle_total_comparisons": (
            UNIVERSAL_ORACLE_TOTAL_OBSERVATIONS
        ),
        "prospective_universal_oracle_proof_field_count": len(
            UNIVERSAL_ORACLE_PROOF_FIELDS
        ),
        "prospective_stage05_correctness_artifact_count": len(
            STAGE05_CORRECTNESS_PATHS
        ),
        "prospective_stage05_deep_family_mapping": dict(STAGE05_DEEP_FAMILIES),
        "prospective_stage05_fresh_edge_proof_count": len(
            DEFAULT_EDGE_ORACLES
        ),
        "owned_root_build_source": "pyproject.toml",
        "owned_source_poisoned_control_count": len(owned_source_controls),
        "owned_source_poisoned_controls": owned_source_controls,
        "inherited_poisoned_control_count": inherited[
            "inherited_poisoned_control_count"
        ],
        "previous_public_poisoned_control_count": inherited[
            "postfinal_poisoned_control_count"
        ],
        "postfinal_poisoned_control_count": len(controls),
        "postfinal_poisoned_controls": controls,
        "strict_regression_speedup_threshold": pilot.REGRESSION_SPEEDUP_THRESHOLD,
        "original_pilot_max_cases": pilot.MAX_CASES,
        "failed": 0,
    }


def freeze(args: argparse.Namespace) -> dict[str, Any]:
    """Publish only the user-authorized, source-bound public v4 manifest."""

    require_candidate_free()
    target = exact_versioned_path(
        args.output,
        MANIFEST_PATH,
        "frozen expanded public-practice manifest",
    )
    edge_paths = (
        list(args.edge_oracle) if args.edge_oracle else list(DEFAULT_EDGE_ORACLES)
    )
    _suite, entries, manifest = make_manifest(edge_paths)
    manifest_sha256 = pilot.save_json(target, manifest, replace_identical=True)
    require_candidate_free()
    return {
        "schema": POSTFINAL_PLAN_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "cases": len(entries),
        "source_public_cases": FIXTURE_CASES,
        "eligible_practice_cases": ELIGIBLE_CASES,
        "all_bounded_workload_categories": CATEGORIES,
        "public_operations": manifest["public_operations"],
        "trials": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "prospective_paired_raw_rows": EXPECTED_ROWS,
        "prospective_correctness_checks": EXPECTED_CORRECTNESS_CHECKS,
        "verified_independent_engine_count": len(MODULES) - 1,
        "verified_native_library_count": len(manifest["native_elf_fingerprints"]),
        **{
            key: manifest[key]
            for key in (
                "postfinal_no_delegation_audit_path",
                "postfinal_no_delegation_audit_sha256",
                "postfinal_no_delegation_audit_source_path",
                "postfinal_no_delegation_audit_source_sha256",
                "postfinal_no_delegation_audit_schema",
                "postfinal_no_delegation_control_count",
            )
        },
        **{
            key: manifest[key]
            for key in UNIVERSAL_ORACLE_PROOF_FIELDS
        },
        "runner_sha256": manifest["runner_sha256"],
        "manifest": str(target),
        "manifest_sha256": manifest_sha256,
        "failed": 0,
    }


def load_guarded_worker_module(
    expected_source_sha256: str,
) -> types.ModuleType:
    """Load only the frozen audit-owned worker bootstrap, not a candidate."""

    require_candidate_free()
    require(
        pilot.file_sha256(POSTFINAL_AUDIT_SOURCE_PATH) == expected_source_sha256,
        "the persistent guarded-worker source changed after public freezing",
    )
    module = importlib.import_module("tools.postfinal_no_delegation_audit_v1")
    require(
        Path(module.__file__).resolve() == POSTFINAL_AUDIT_SOURCE_PATH.resolve(),
        "the persistent guarded-worker source was substituted",
    )
    require(
        pilot.file_sha256(Path(module.__file__).resolve())
        == expected_source_sha256,
        "the imported persistent guarded-worker source is not source-bound",
    )
    require(
        callable(getattr(module, "guarded_worker_command", None))
        and callable(getattr(module, "validate_guarded_worker_response", None)),
        "the audited persistent worker guard does not expose its verified protocol",
    )
    require_candidate_free()
    return module


class PersistentGuardedWorker:
    """One independently guarded engine; no candidate enters the controller."""

    def __init__(
        self,
        runtime_audit: types.ModuleType,
        module: str,
        native_fingerprints: dict[str, str],
    ) -> None:
        self.runtime_audit = runtime_audit
        self.module = module
        self.family = WORKER_FAMILIES[module]
        self.native_fingerprints = native_fingerprints
        command = runtime_audit.guarded_worker_command(
            self.family,
            native_fingerprints,
            persistent=True,
        )
        require(
            isinstance(command, list)
            and all(isinstance(value, str) for value in command)
            and len(command) >= 4
            and Path(command[0]).resolve() == replay.PINNED_PYTHON.resolve()
            and "-I" in command
            and "-B" in command,
            f"the {module} worker is not an isolated pinned Python process",
        )
        self.process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        require(
            self.process.stdin is not None and self.process.stdout is not None,
            f"the {module} guarded worker has no bounded private protocol",
        )
        try:
            self.verify(force_hash=True)
        except (RuntimeError, replay.AuditError, OSError, ValueError):
            self.close()
            raise

    def request(self, document: dict[str, Any]) -> dict[str, Any]:
        require(
            self.process.poll() is None,
            f"the independently guarded {self.module} worker stopped",
        )
        require(
            self.process.stdin is not None and self.process.stdout is not None,
            f"the independently guarded {self.module} worker lost its protocol",
        )
        try:
            request = json.dumps(
                document,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            self.process.stdin.write(request + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError, TypeError, ValueError) as error:
            raise RuntimeError(
                f"the independently guarded {self.module} worker rejected a request"
            ) from error
        for response_index in range(2):
            try:
                encoded = self.process.stdout.readline(
                    MAX_WORKER_RESPONSE_BYTES + 1
                )
            except OSError as error:
                raise RuntimeError(
                    f"the independently guarded {self.module} worker response failed"
                ) from error
            require(
                bool(encoded)
                and len(encoded) <= MAX_WORKER_RESPONSE_BYTES
                and encoded.endswith("\n"),
                "the independently guarded "
                f"{self.module} worker returned an invalid response",
            )
            try:
                response = json.loads(encoded)
            except (UnicodeError, json.JSONDecodeError) as error:
                raise RuntimeError(
                    "the independently guarded "
                    f"{self.module} worker returned invalid JSON"
                ) from error
            require(
                isinstance(response, dict),
                "the independently guarded "
                f"{self.module} worker changed its protocol",
            )
            if (
                response_index == 0
                and response.get("op") in {"ready", "startup"}
                and document.get("op") not in {"ready", "startup"}
            ):
                require(
                    response.get("passed") is True,
                    f"the independently guarded {self.module} worker failed startup",
                )
                continue
            require(
                response.get("passed") is True
                and response.get("op") == document.get("op"),
                "the independently guarded "
                f"{self.module} worker rejected {document.get('op')!r}",
            )
            return response
        raise RuntimeError(
            f"the independently guarded {self.module} worker omitted its response"
        )

    def verify(self, *, force_hash: bool = False) -> dict[str, Any]:
        response = self.request(
            {"op": "verify", "force_hash": force_hash}
        )
        validated = self.runtime_audit.validate_guarded_worker_response(
            self.family,
            response,
            self.native_fingerprints,
        )
        require(
            isinstance(validated, dict),
            f"the {self.module} worker did not return a verified native mapping",
        )
        mapping = validated.get("native_mapping_provenance")
        require(
            isinstance(mapping, dict)
            and mapping.get("force_hash") is force_hash
            and mapping.get("digest_cache_key")
            == "device,inode,size,mtime_ns,ctime_ns",
            f"the {self.module} worker changed its frozen native hash policy",
        )
        if force_hash:
            records = mapping.get("observed_owned_mappings")
            require(
                isinstance(records, list)
                and all(
                    isinstance(record, dict)
                    and record.get("content_sha256_recomputed") is True
                    for record in records
                ),
                f"the {self.module} worker skipped a forced native content hash",
            )
        return validated

    def prepare(
        self,
        case: dict[str, Any],
        expected: dict[str, Any],
    ) -> None:
        response = self.request(
            {
                "op": "prepare",
                "case": pilot.pack_calibration_value(case),
                "expected": pilot.pack_calibration_value(expected),
            }
        )
        validated = self.runtime_audit.validate_guarded_worker_response(
            self.family,
            response,
            self.native_fingerprints,
        )
        require(
            isinstance(validated, dict)
            and response.get("case") == case["id"]
            and response.get("module") == self.module
            and response.get("expected_sha256") == expected["result_sha256"],
            f"the {self.module} worker substituted a frozen public case",
        )

    def observe(
        self,
        *,
        case: dict[str, Any],
        expected: dict[str, Any],
        trial: int,
        operations: int,
    ) -> dict[str, Any]:
        response = self.request(
            {
                "op": "observe",
                "case": case["id"],
                "trial": trial,
                "operations": operations,
                "warmups": WARMUPS,
            }
        )
        require(
            response.get("case") == case["id"]
            and response.get("module") == self.module
            and response.get("trial") == trial
            and response.get("operations") == operations
            and response.get("warmups") == WARMUPS
            and response.get("correctness_checks") == 3
            and response.get("expected_sha256") == expected["result_sha256"],
            f"the {self.module} worker omitted a frozen public correctness gate",
        )
        elapsed = response.get("elapsed_ns")
        require(
            isinstance(elapsed, int) and not isinstance(elapsed, bool) and elapsed > 0,
            f"the {self.module} worker produced a nonpositive native timing",
        )
        require(
            response.get("ns_per_op") == elapsed / operations,
            f"the {self.module} worker changed its prospective operation denominator",
        )
        memory = {
            "rss_before_kb": response.get("rss_before_kb"),
            "rss_after_kb": response.get("rss_after_kb"),
            "hwm_kb": response.get("hwm_kb"),
            "peak_traced_bytes": response.get("peak_traced_bytes"),
        }
        replay.validate_memory(memory)
        return response

    def close(self) -> None:
        if self.process.poll() is None:
            try:
                self.request({"op": "quit"})
            except (OSError, RuntimeError):
                self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=10)
        if self.process.stdin is not None:
            self.process.stdin.close()
        if self.process.stdout is not None:
            self.process.stdout.close()
        if self.process.stderr is not None:
            self.process.stderr.close()


def current_measured_fingerprints(
    sources: dict[str, str],
    native: dict[str, str],
) -> dict[str, str]:
    """Verify current owned bytes without importing production engines."""

    require_candidate_free()
    observed = {
        "re:module": pilot.file_sha256(replay.PINNED_RE),
        "candidates.rust_candidate:module": sources["candidates/rust_candidate.py"],
        "candidates.rust_candidate:bridge-source": sources[
            "candidates/rust/py_bridge.c"
        ],
        "candidates.rust_candidate:native-source": sources[
            "candidates/rust/src/lib.rs"
        ],
        "candidates.vm_candidate:module": sources["candidates/vm_candidate.py"],
        "candidates.zig_candidate:module": sources["candidates/zig_candidate.py"],
        **native,
    }
    return replay.validate_measured_fingerprints(
        {
            "candidate_binary_sha256_before": observed,
            "candidate_binary_sha256_after": observed,
        },
        sources,
        native,
    )


def require_matching_audits(
    plan: dict[str, Any],
) -> tuple[str, dict[str, str], dict[str, str], dict[str, Any]]:
    audit_digest, sources, native, additive = verified_from_scratch_audit()
    require(
        audit_digest == plan.get("from_scratch_audit_sha256"),
        "the frozen original 76-control independence audit changed",
    )
    require(
        sources == plan.get("qualified_source_fingerprints"),
        "an independently owned production source changed after public freezing",
    )
    require(
        native == plan.get("native_elf_fingerprints"),
        "an independently owned native binary changed after public freezing",
    )
    for key, value in additive.items():
        require(
            plan.get(key) == value,
            f"the frozen additive no-delegation audit changed: {key}",
        )
    universal = verified_python_re_universal_oracle(
        audit_digest,
        sources,
        native,
        additive,
    )
    for key, value in universal.items():
        require(
            plan.get(key) == value,
            f"the frozen all-engine Python re public oracle changed: {key}",
        )
    return audit_digest, sources, native, additive


def measure(args: argparse.Namespace) -> dict[str, Any]:
    """Run only explicitly authorized paired, process-isolated public timing."""

    require_candidate_free()
    require_pinned_python()
    require(
        args.exclusive_slot == EXCLUSIVE_SLOT,
        "the unique expanded public timing slot was not explicitly authorized",
    )
    require(args.cases == CASES, "the frozen 8,192-case denominator changed")
    require(args.trials == TRIALS, "the frozen 13 paired trials changed")
    require(args.bootstraps == BOOTSTRAPS, "the frozen bootstrap denominator changed")
    require(
        args.max_operations == MAX_OPERATIONS,
        "the frozen 16-operation safety bound changed",
    )
    suite, entries, plan, manifest_sha256 = load_frozen_manifest(args.manifest)
    raw_path = exact_versioned_path(
        args.raw,
        RAW_PATH,
        "expanded public paired observations",
    )
    summary_path = exact_versioned_path(
        args.output,
        SUMMARY_PATH,
        "expanded public paired summary",
    )
    require(
        not raw_path.exists(),
        "refusing to overwrite expanded public paired observations",
    )
    require(
        not summary_path.exists(),
        "refusing to overwrite expanded public practice results",
    )
    requested = list(args.module) if args.module else list(MODULES)
    names = pilot.selected_modules(suite, requested)
    require(
        names == MODULES,
        "isolated public timing must retain all four original independent engines",
    )
    audit_digest, sources, native, additive = require_matching_audits(plan)
    fingerprints_before = current_measured_fingerprints(sources, native)
    pilot.match_reported_fingerprints(plan["verified_edge_oracles"], fingerprints_before)
    runtime_audit = load_guarded_worker_module(
        additive["postfinal_no_delegation_audit_source_sha256"]
    )
    require_candidate_free()

    workers: dict[str, PersistentGuardedWorker] = {}
    observed: dict[tuple[str, int, str], dict[str, Any]] = {}
    raw_digest = hashlib.sha256()
    correctness_checks = 0
    runtime_guard_checks = 0
    try:
        for name in names:
            workers[name] = PersistentGuardedWorker(runtime_audit, name, native)
            runtime_guard_checks += 1

        raw_path.parent.mkdir(parents=True, exist_ok=True)
        with raw_path.open("xb") as destination:
            with gzip.GzipFile(
                filename="",
                fileobj=destination,
                mode="wb",
                compresslevel=9,
                mtime=0,
            ) as compressed:
                for position, (_index, case, expected, reasons) in enumerate(
                    entries,
                    1,
                ):
                    require(
                        case["cohort"] == pilot.PRACTICE,
                        "a noncalibration case reached expanded public timing",
                    )
                    for name in names:
                        workers[name].prepare(case, expected)
                        runtime_guard_checks += 1
                    operations = min(case["ops"], MAX_OPERATIONS)
                    for trial in range(TRIALS):
                        order = pilot.trial_order(
                            names,
                            case["id"],
                            trial,
                            ORDER_SEED,
                        )
                        for order_index, name in enumerate(order):
                            sample = workers[name].observe(
                                case=case,
                                expected=expected,
                                trial=trial,
                                operations=operations,
                            )
                            correctness_checks += sample["correctness_checks"]
                            row: dict[str, Any] = {
                                "schema": pilot.ROW_SCHEMA,
                                "measurement": (
                                    "bounded practice diagnostic only; "
                                    "not a holdout result"
                                ),
                                "case": case["id"],
                                "cohort": pilot.PRACTICE,
                                "category": case["category"],
                                "api": case["api"],
                                "lifecycle": case["lifecycle"],
                                "input": pilot.source_kind(case),
                                "result_density": pilot.density(
                                    expected["result"]
                                ),
                                "selection_reasons": list(reasons),
                                "module": name,
                                "trial": trial,
                                "order": order_index,
                                "operations": operations,
                                "frozen_operations": case["ops"],
                                "elapsed_ns": sample["elapsed_ns"],
                                "ns_per_op": sample["ns_per_op"],
                                "peak_traced_bytes": sample["peak_traced_bytes"],
                                "rss_before_kb": sample["rss_before_kb"],
                                "rss_after_kb": sample["rss_after_kb"],
                                "hwm_kb": sample["hwm_kb"],
                                "expected_sha256": sample["expected_sha256"],
                            }
                            require(
                                pilot.valid_process_memory(row),
                                "an isolated worker produced invalid memory evidence",
                            )
                            key = (case["id"], trial, name)
                            require(
                                key not in observed,
                                f"duplicate expanded public paired observation: {key!r}",
                            )
                            encoded = (
                                json.dumps(
                                    row,
                                    ensure_ascii=False,
                                    allow_nan=False,
                                    sort_keys=True,
                                    separators=(",", ":"),
                                )
                                + "\n"
                            ).encode("utf-8")
                            raw_digest.update(encoded)
                            compressed.write(encoded)
                            observed[key] = row
                    for name in names:
                        workers[name].verify()
                        runtime_guard_checks += 1
                    require_candidate_free()
                    if position % 32 == 0 or position == len(entries):
                        print(
                            json.dumps(
                                {
                                    "schema": POSTFINAL_REPORT_SCHEMA
                                    + "-progress",
                                    "protocol_version": VERSION,
                                    "cohort": pilot.PRACTICE,
                                    "holdout_accessed": False,
                                    "completed": position,
                                    "cases": len(entries),
                                },
                                sort_keys=True,
                            ),
                            flush=True,
                        )
        for name in names:
            workers[name].verify(force_hash=True)
            runtime_guard_checks += 1
    finally:
        for worker in workers.values():
            worker.close()

    require(
        len(observed) == EXPECTED_ROWS,
        "the isolated public paired raw-row denominator changed",
    )
    require(
        correctness_checks == EXPECTED_CORRECTNESS_CHECKS,
        "an isolated public CPython-answer correctness gate was omitted",
    )
    require(
        runtime_guard_checks == EXPECTED_RUNTIME_GUARD_CHECKS,
        "a per-case isolated native mapping or no-delegation check was omitted",
    )
    refreshed_digest, refreshed_sources, refreshed_native, refreshed_additive = (
        require_matching_audits(plan)
    )
    require(
        refreshed_digest == audit_digest
        and refreshed_sources == sources
        and refreshed_native == native
        and refreshed_additive == additive,
        "an independently verified audit changed during isolated public timing",
    )
    fingerprints_after = current_measured_fingerprints(
        refreshed_sources,
        refreshed_native,
    )
    require(
        fingerprints_after == fingerprints_before,
        "an isolated production source or native artifact changed during public timing",
    )
    pilot.match_reported_fingerprints(
        plan["verified_edge_oracles"],
        fingerprints_after,
    )
    results, rankings = pilot.summarize_measurements(
        suite,
        entries,
        names,
        observed,
        TRIALS,
        BOOTSTRAPS,
    )
    require(
        len(results) == CASES * (len(MODULES) - 1)
        and len(rankings) == len(MODULES) - 1,
        "an expanded public candidate-case result or candidate ranking was omitted",
    )

    summary: dict[str, Any] = {
        "schema": pilot.REPORT_SCHEMA,
        "postfinal_schema": POSTFINAL_REPORT_SCHEMA,
        "protocol_version": VERSION,
        "measurement": (
            "balanced practice diagnostic only; "
            "not a holdout result or final speed claim"
        ),
        "measurement_role": (
            "additive expanded public practice only; "
            "not a held-out or final result"
        ),
        "cohort": pilot.PRACTICE,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "exclusive_slot": EXCLUSIVE_SLOT,
        "manifest_path": str(MANIFEST_PATH.resolve()),
        "manifest_sha256": manifest_sha256,
        "runner_sha256": plan["runner_sha256"],
        "from_scratch_audit_sha256": audit_digest,
        "from_scratch_audit_source_path": plan[
            "from_scratch_audit_source_path"
        ],
        "from_scratch_audit_source_sha256": plan[
            "from_scratch_audit_source_sha256"
        ],
        **additive,
        **{
            key: plan[key]
            for key in UNIVERSAL_ORACLE_PROOF_FIELDS
        },
        "verified_edge_oracles": plan["verified_edge_oracles"],
        "stage05_correctness_artifacts": plan["stage05_correctness_artifacts"],
        "expected_sha256": plan["expected_sha256"],
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "modules": list(names),
        "cases": CASES,
        "all_bounded_workload_categories": CATEGORIES,
        "bounded_public_api_capacities": plan["bounded_public_api_capacities"],
        "public_operations": plan["public_operations"],
        "lifetimes": plan["lifetimes"],
        "inputs": plan["inputs"],
        "result_densities": plan["result_densities"],
        "api_lifetimes": plan["api_lifetimes"],
        "trials": TRIALS,
        "warmups": WARMUPS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "bootstrap_samples": BOOTSTRAPS,
        "strict_regression_speedup_threshold": (
            pilot.REGRESSION_SPEEDUP_THRESHOLD
        ),
        "execution_topology": plan["execution_topology"],
        "runtime_native_hash_policy": plan["runtime_native_hash_policy"],
        "execution_safety": plan["execution_safety"],
        "persistent_isolated_worker_count": len(workers),
        "per_case_runtime_guard_checks": runtime_guard_checks,
        "controller_candidate_imported": False,
        "raw_path": str(raw_path),
        "raw_sha256": raw_digest.hexdigest(),
        "compressed_raw_sha256": pilot.file_sha256(raw_path),
        "paired_raw_rows": EXPECTED_ROWS,
        "correctness_checks": correctness_checks,
        "candidate_binary_sha256_before": fingerprints_before,
        "candidate_binary_sha256_after": fingerprints_after,
        "case_results": results,
        "rankings": rankings,
        "regressions": [
            result for result in results if result["regression_gt_20pct"]
        ],
        "failed": 0,
    }
    replay.validate_measured_fingerprints(
        summary,
        refreshed_sources,
        refreshed_native,
    )
    summary_sha256 = pilot.save_json(summary_path, summary)
    require_candidate_free()
    return {
        "schema": POSTFINAL_REPORT_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "measurement": (
            "additive isolated public practice only; "
            "not a final or held-out result"
        ),
        "cohort": pilot.PRACTICE,
        "holdout_accessed": False,
        "cases": CASES,
        "modules": list(names),
        "paired_trials": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "paired_raw_rows": EXPECTED_ROWS,
        "correctness_checks": correctness_checks,
        "confidence_intervals": len(results) + len(rankings),
        "persistent_isolated_worker_count": len(workers),
        "per_case_runtime_guard_checks": runtime_guard_checks,
        "controller_candidate_imported": False,
        "strict_regressions": len(summary["regressions"]),
        "raw_sha256": raw_digest.hexdigest(),
        "compressed_raw_sha256": summary["compressed_raw_sha256"],
        "summary_sha256": summary_sha256,
        "from_scratch_audit_sha256": audit_digest,
        **additive,
        **{
            key: plan[key]
            for key in UNIVERSAL_ORACLE_PROOF_FIELDS
        },
        "failed": 0,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    """Replay exact expanded public observations without loading candidates."""

    require_candidate_free()
    require_pinned_python()
    _suite, entries, plan, manifest_sha256 = load_frozen_manifest(
        args.manifest
    )
    raw_path = exact_versioned_path(
        args.raw,
        RAW_PATH,
        "verified expanded public observations",
    )
    summary_path = exact_versioned_path(
        args.summary,
        SUMMARY_PATH,
        "verified expanded public summary",
    )
    output_path = exact_versioned_path(
        args.output,
        INTEGRITY_PATH,
        "expanded public integrity evidence",
    )
    require(
        not output_path.exists(),
        "refusing to overwrite independently replayed expanded public evidence",
    )
    summary = read_json(summary_path, "recorded expanded public summary")
    require(
        summary.get("postfinal_schema") == POSTFINAL_REPORT_SCHEMA
        and summary.get("protocol_version") == VERSION,
        "expanded public summary schema or protocol version changed",
    )
    require(
        summary.get("exclusive_slot") == EXCLUSIVE_SLOT,
        "expanded public summary substituted its authorized paired slot",
    )
    require(
        summary.get("raw_path") == str(raw_path),
        "expanded public summary substituted its observations",
    )
    require(
        summary.get("manifest_path") == str(MANIFEST_PATH.resolve())
        and summary.get("manifest_sha256") == manifest_sha256,
        "expanded public summary substituted its frozen prospective manifest",
    )
    require(
        summary.get("runner_sha256") == plan["runner_sha256"],
        "expanded public summary substituted its frozen runner source",
    )
    require(
        summary.get("from_scratch_audit_sha256")
        == plan["from_scratch_audit_sha256"],
        "expanded public summary substituted the original independence audit",
    )
    require(
        summary.get("from_scratch_audit_source_path")
        == plan["from_scratch_audit_source_path"]
        and summary.get("from_scratch_audit_source_sha256")
        == plan["from_scratch_audit_source_sha256"],
        "expanded public summary substituted the original audit source",
    )
    require(
        summary.get("verified_edge_oracles") == plan["verified_edge_oracles"]
        and summary.get("stage05_correctness_artifacts")
        == plan["stage05_correctness_artifacts"],
        "expanded public summary changed its frozen correctness proofs",
    )
    require(
        summary.get("held_out_cases_generated") == 0
        and summary.get("held_out_records_deserialized") == 0,
        "expanded public replay encountered a nonpublic case",
    )
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "expanded public evidence was misrepresented as final performance",
    )
    require(
        summary.get("execution_topology") == plan["execution_topology"]
        and summary.get("runtime_native_hash_policy")
        == plan["runtime_native_hash_policy"]
        and summary.get("execution_safety") == plan["execution_safety"]
        and summary.get("persistent_isolated_worker_count") == len(MODULES)
        and summary.get("per_case_runtime_guard_checks")
        == EXPECTED_RUNTIME_GUARD_CHECKS
        and summary.get("controller_candidate_imported") is False,
        "expanded public evidence omitted its actual persistent isolation guards",
    )
    for key in (
        "postfinal_no_delegation_audit_path",
        "postfinal_no_delegation_audit_sha256",
        "postfinal_no_delegation_audit_source_path",
        "postfinal_no_delegation_audit_source_sha256",
        "postfinal_no_delegation_audit_schema",
        "postfinal_no_delegation_control_count",
    ):
        require(
            summary.get(key) == plan.get(key),
            f"expanded public summary substituted its additive audit: {key}",
        )
    for key in UNIVERSAL_ORACLE_PROOF_FIELDS:
        require(
            summary.get(key) == plan.get(key),
            "expanded public summary substituted its passing all-engine "
            f"Python re oracle: {key}",
        )

    profile = replay.Profile(
        cases=CASES,
        trials=TRIALS,
        bootstraps=BOOTSTRAPS,
        categories=CATEGORIES,
        apis=PUBLIC_APIS,
    )
    replay.validate_plan(plan, profile)
    replay.validate_header(summary, plan, profile, None)
    audit_digest, sources, native, additive = require_matching_audits(plan)
    measured = replay.validate_measured_fingerprints(summary, sources, native)
    compressed_sha256 = pilot.file_sha256(raw_path)
    require(
        compressed_sha256 == summary.get("compressed_raw_sha256"),
        "expanded compressed paired observations changed",
    )
    with raw_path.open("rb") as source:
        observations = replay.read_observations(
            source,
            compressed_sha256,
            summary,
            plan,
            profile,
        )
    results, rankings = replay.recompute_results(plan, observations, profile)
    regressions = replay.validate_results(
        summary,
        results,
        rankings,
        profile,
    )
    controls = synthetic_self_test()
    require_candidate_free()

    document: dict[str, Any] = {
        "schema": POSTFINAL_INTEGRITY_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "measurement": (
            "independent replay of isolated expanded public practice; "
            "not a final or held-out result"
        ),
        "cohort": pilot.PRACTICE,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "candidate_imported": False,
        "module_order": list(MODULES),
        "cases_per_candidate": len(entries),
        "candidate_case_count": len(results),
        "trials_per_module_case": TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": len(observations) * 3,
        "bootstrap_draws": BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regression_speedup_threshold": (
            pilot.REGRESSION_SPEEDUP_THRESHOLD
        ),
        "strict_regressions": len(regressions),
        "manifest_sha256": manifest_sha256,
        "runner_sha256": plan["runner_sha256"],
        "summary_sha256": pilot.file_sha256(summary_path),
        "compressed_raw_sha256": compressed_sha256,
        "raw_sha256": summary["raw_sha256"],
        "from_scratch_audit_sha256": audit_digest,
        "from_scratch_audit_source_path": plan[
            "from_scratch_audit_source_path"
        ],
        "from_scratch_audit_source_sha256": plan[
            "from_scratch_audit_source_sha256"
        ],
        "from_scratch_control_count": 76,
        **additive,
        **{
            key: plan[key]
            for key in UNIVERSAL_ORACLE_PROOF_FIELDS
        },
        "verified_independent_engine_count": len(MODULES) - 1,
        "verified_native_library_count": len(native),
        "qualified_source_fingerprints": sources,
        "native_elf_fingerprints": native,
        "candidate_binary_sha256_before": measured,
        "candidate_binary_sha256_after": measured,
        "verified_edge_oracles": plan["verified_edge_oracles"],
        "stage05_correctness_artifacts": plan["stage05_correctness_artifacts"],
        "execution_topology": plan["execution_topology"],
        "runtime_native_hash_policy": plan["runtime_native_hash_policy"],
        "execution_safety": plan["execution_safety"],
        "persistent_isolated_worker_count": summary[
            "persistent_isolated_worker_count"
        ],
        "per_case_runtime_guard_checks": summary[
            "per_case_runtime_guard_checks"
        ],
        "controller_candidate_imported": False,
        "rankings": rankings,
        "regressions": regressions,
        "self_test": controls,
        "memory_limitation": (
            "Tracemalloc reports Python-visible temporary allocations. "
            "RSS and high-water marks are process-level observations in "
            "separate dedicated engine workers; they do not establish exact "
            "per-allocation native-engine memory."
        ),
        "failed": 0,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    integrity_sha256 = pilot.save_json(output_path, document)
    require_candidate_free()
    return {
        "schema": POSTFINAL_INTEGRITY_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "holdout_accessed": False,
        "timing_performed": False,
        "candidate_imported": False,
        "cases_per_candidate": CASES,
        "candidate_case_count": len(results),
        "trials_per_module_case": TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": len(observations) * 3,
        "bootstrap_draws": BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regressions": len(regressions),
        "verified_native_library_count": len(native),
        "inherited_poisoned_control_count": controls[
            "inherited_poisoned_control_count"
        ],
        "postfinal_poisoned_control_count": controls[
            "postfinal_poisoned_control_count"
        ],
        **additive,
        **{
            key: plan[key]
            for key in UNIVERSAL_ORACLE_PROOF_FIELDS
        },
        "output": str(output_path),
        "sha256": integrity_sha256,
        "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    test = commands.add_parser(
        "self-test",
        help="run only candidate-free in-memory expanded public poison controls",
    )
    test.set_defaults(handler=lambda _args: synthetic_self_test())

    plan = commands.add_parser(
        "freeze",
        help="freeze one source-bound 8,192-case calibration-only public manifest",
    )
    plan.add_argument("--output", type=Path, default=MANIFEST_PATH)
    plan.add_argument(
        "--edge-oracle",
        type=Path,
        action="append",
        help="exact fresh stage-05 Rust, VM, and Zig complete edge proof",
    )
    plan.set_defaults(handler=freeze)

    live = commands.add_parser(
        "measure",
        help="perform only explicitly authorized process-isolated public timing",
    )
    live.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    live.add_argument("--exclusive-slot", required=True)
    live.add_argument("--cases", type=pilot.positive_int, default=CASES)
    live.add_argument("--raw", type=Path, default=RAW_PATH)
    live.add_argument("--output", type=Path, default=SUMMARY_PATH)
    live.add_argument("--module", action="append")
    live.add_argument("--trials", type=pilot.positive_int, default=TRIALS)
    live.add_argument(
        "--max-operations",
        type=pilot.positive_int,
        default=MAX_OPERATIONS,
    )
    live.add_argument(
        "--bootstraps",
        type=pilot.positive_int,
        default=BOOTSTRAPS,
    )
    live.set_defaults(handler=measure)

    check = commands.add_parser(
        "verify",
        help="replay expanded public evidence without importing any candidate",
    )
    check.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    check.add_argument("--raw", type=Path, default=RAW_PATH)
    check.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    check.add_argument("--output", type=Path, default=INTEGRITY_PATH)
    check.set_defaults(handler=verify)

    args = parser.parse_args()
    try:
        result = args.handler(args)
    except (
        RuntimeError,
        replay.AuditError,
        OSError,
        subprocess.SubprocessError,
        KeyError,
        TypeError,
        ValueError,
        OverflowError,
        RecursionError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        print(
            json.dumps(
                {
                    "schema": POSTFINAL_INTEGRITY_SCHEMA,
                    "result": "FAIL",
                    "protocol_version": VERSION,
                    "holdout_accessed": False,
                    "timing_performed": False,
                    "error": str(error),
                    "failed": 1,
                },
                sort_keys=True,
            )
        )
        raise SystemExit(1) from error
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
