#!/usr/bin/env python3
"""Freeze and verify a fresh, source-bound public Python regex comparison.

Version 6 retains every one of version 5's 8,192 public cases, their weights,
the pinned CPython baseline, the isolated Unicode-safe workers, paired trials,
and confidence rules.  It changes only the evidence needed to qualify the
independently rebuilt Rust engine.  Public planning and self-tests never start
a candidate worker, perform timing, or access a final holdout.

Actual measurement requires a separately frozen, committed, and pushed public
manifest and an explicitly supplied version-6 exclusive measurement slot.
"""

from __future__ import annotations

import collections
import importlib
import json
import subprocess
import sys
import types
from pathlib import Path
from typing import Any, Mapping

from tools import postfinal_public_practice_v5 as frozen_v5


frozen_v4 = frozen_v5.frozen_v4
ROOT = frozen_v4.ROOT
V6_SOURCE_PATH = Path(__file__).resolve()

FROZEN_V5_VERSION = "postfinal-public-practice-v5"
FROZEN_V5_SOURCE_PATH = ROOT / "tools" / "postfinal_public_practice_v5.py"
FROZEN_V5_SOURCE_SHA256 = (
    "f4294a3b5434f43a92970635a958cf3b39db0eb926adef50e242ac0f6b9a1d22"
)
FROZEN_V5_MANIFEST_PATH = (
    ROOT / "performance" / "postfinal-public-v5" / "manifest.json"
)
FROZEN_V5_MANIFEST_SHA256 = (
    "c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96"
)

VERSION = "postfinal-public-practice-v6"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v6"
EVIDENCE_ROOT = VERSION_ROOT / "evidence"
MANIFEST_PATH = VERSION_ROOT / "manifest.json"
RAW_PATH = EVIDENCE_ROOT / f"{VERSION}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE_ROOT / f"{VERSION}-summary.json"
INTEGRITY_PATH = EVIDENCE_ROOT / f"{VERSION}-integrity.json"
POSTFINAL_PLAN_SCHEMA = "rebar-postfinal-public-practice-plan-v6"
POSTFINAL_REPORT_SCHEMA = "rebar-postfinal-public-practice-report-v6"
POSTFINAL_INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v6"
EXCLUSIVE_SLOT = VERSION

BASE_AUDIT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
)
BASE_AUDIT_SHA256 = (
    "5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551"
)
BASE_AUDIT_SOURCE_PATH = ROOT / "tools" / "postfinal_from_scratch_audit_v2.py"
BASE_AUDIT_SOURCE_SHA256 = (
    "6f540074c9f7f4bdffe9e53939efe4cec25e5c029ca1f73ec791d377bddc9306"
)

STRICT_AUDIT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V2.json"
)
STRICT_AUDIT_SHA256 = (
    "183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f"
)
STRICT_AUDIT_SOURCE_PATH = ROOT / "tools" / "postfinal_no_delegation_audit_v2.py"
STRICT_AUDIT_SOURCE_SHA256 = (
    "571c11885f9c9694025ea0434e57bfaa56651057eee62fa4396a2bcb95ae4cb5"
)
STRICT_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v2"
STRICT_AUDIT_CONTROL_COUNT = 32

IMMUTABLE_WORKER_SOURCE_PATH = (
    ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
)
IMMUTABLE_WORKER_SOURCE_SHA256 = (
    "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
)
IMMUTABLE_WORKER_REPORT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)
IMMUTABLE_WORKER_REPORT_SHA256 = (
    "c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b"
)
IMMUTABLE_WORKER_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"

UNIVERSAL_V4_SOURCE_PATH = (
    ROOT / "tools" / "python_re_universal_public_oracle_stage04.py"
)
UNIVERSAL_V4_SOURCE_SHA256 = (
    "922de8886671e5bfc9db58ba92c134f4bf76b06acb01476f6fc9a9e3321815a6"
)
UNIVERSAL_V4_REPORT_PATH = (
    ROOT / "candidates" / "evidence" / "python-re-universal-public-oracle-v4-all.json"
)
UNIVERSAL_V4_REPORT_SHA256 = (
    "facb736a3409f459cdc812e6dc740df399f98ebb84745a22b615ef130ccdb137"
)

FROZEN_PUBLIC_OPERATION_COUNTS = {
    "compile": 210,
    "escape": 161,
    "findall": 2_040,
    "finditer": 2_041,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 427,
    "search": 1_057,
    "split": 451,
    "sub": 447,
    "subn": 530,
}

PUBLIC_PARITY_FIELDS = (
    "schema",
    "python",
    "cohort",
    "expected_sha256",
    "source_fixture",
    "source_fixture_sha256",
    "source_fixture_uncompressed_sha256",
    "source_fixture_manifest_sha256",
    "source_v7_manifest_sha256",
    "source_v7_suite_sha256",
    "source_v7_runner_sha256",
    "source_public_pilot_sha256",
    "source_public_replay_sha256",
    "source_public_v3_manifest_sha256",
    "source_public_v3_runner_sha256",
    "modules",
    "selection_seed",
    "order_seed",
    "bootstrap_seed",
    "frozen_trials",
    "frozen_warmups",
    "frozen_bootstrap_samples",
    "default_trials",
    "default_bootstrap_samples",
    "cases",
    "source_public_cases",
    "eligible_practice_cases",
    "all_bounded_workload_categories",
    "bounded_public_api_capacities",
    "public_operations",
    "lifetimes",
    "inputs",
    "result_densities",
    "api_lifetimes",
    "categories",
    "maximum_subject_length",
    "maximum_result_count",
    "maximum_subject_limit",
    "maximum_result_limit",
    "maximum_operations_per_trial",
    "strict_regression_speedup_threshold",
    "selected_cases",
    "holdout_accessed",
    "held_out_cases_generated",
    "held_out_records_deserialized",
    "historical_performance_read",
    "timing_performed",
)

_FROZEN_V4_MAKE_MANIFEST = frozen_v5._FROZEN_V4_MAKE_MANIFEST
_FROZEN_V4_SELF_TEST = frozen_v5._FROZEN_V4_SELF_TEST
_FROZEN_V4_VERIFIED_AUDIT = frozen_v4.verified_from_scratch_audit
_FROZEN_V4_MEASURE = frozen_v4.measure
_FROZEN_V4_VERIFY = frozen_v4.verify
_FROZEN_V5_STAGE_PATHS = dict(frozen_v4.STAGE05_CORRECTNESS_PATHS)


def _owned_relative(path: Path) -> str:
    """Return the exact repository-owned spelling of a public evidence path."""

    resolved = path.resolve()
    frozen_v4.require(
        resolved.is_relative_to(ROOT.resolve()),
        "a public version-6 source or proof escaped its owned repository",
    )
    return str(resolved.relative_to(ROOT.resolve()))


def _make_mixed_proof_paths() -> tuple[tuple[str, Path], ...]:
    """Replace only the four Rust proofs; preserve both original peer families."""

    rust = {
        "rust-edge": (
            ROOT
            / "candidates"
            / "evidence"
            / "rust-v7-edge-oracle-rust-postfinal-inline-state-v1.json.gz"
        ),
        "rust-deep-public-contract": (
            ROOT
            / "candidates"
            / "audits"
            / "RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-INLINE-STATE-V1.json.gz"
        ),
        "rust-observability": (
            ROOT
            / "candidates"
            / "evidence"
            / "rust-v8-observability-rust-qualified-postfinal-inline-state-v1.json.gz"
        ),
        "rust-complete-correctness-campaign": (
            ROOT
            / "candidates"
            / "evidence"
            / "rust-v8-rust-postfinal-inline-state-v1-sealed-campaign.json"
        ),
    }
    result: list[tuple[str, Path]] = []
    for candidate in ("rust", "vm", "zig"):
        for suffix in (
            "edge",
            "deep-public-contract",
            "observability",
            "complete-correctness-campaign",
        ):
            role = f"{candidate}-{suffix}"
            path = rust[role] if candidate == "rust" else _FROZEN_V5_STAGE_PATHS[role]
            result.append((role, path))
    return tuple(result)


MIXED_CORRECTNESS_PATHS = _make_mixed_proof_paths()
MIXED_EDGE_ORACLES = tuple(
    path for role, path in MIXED_CORRECTNESS_PATHS if role.endswith("-edge")
)


def _validate_proof_contract(
    paths: tuple[tuple[str, Path], ...],
    edges: tuple[Path, ...],
    candidates: tuple[str, ...],
    deep_families: Mapping[str, str],
) -> None:
    """Reject missing, reordered, stale, shared, or cross-family proofs."""

    frozen_v4.require(
        candidates == ("rust", "vm", "zig"),
        "public version 6 must retain exactly three independently owned engines",
    )
    frozen_v4.require(
        dict(deep_families) == {"rust": "RUST", "vm": "C", "zig": "ZIG"},
        "public version 6 changed an independently owned proof family",
    )
    expected_roles = tuple(role for role, _path in MIXED_CORRECTNESS_PATHS)
    frozen_v4.require(
        isinstance(paths, tuple)
        and len(paths) == 12
        and all(isinstance(item, tuple) and len(item) == 2 for item in paths)
        and tuple(role for role, _path in paths) == expected_roles,
        "public version 6 omitted, reordered, or substituted a correctness role",
    )
    resolved: list[Path] = []
    for (role, observed), (_expected_role, expected) in zip(
        paths, MIXED_CORRECTNESS_PATHS, strict=True
    ):
        frozen_v4.require(
            isinstance(observed, Path)
            and observed.resolve() == expected.resolve()
            and observed.resolve().is_relative_to(ROOT.resolve()),
            f"public version 6 substituted the exact {role} correctness proof",
        )
        resolved.append(observed.resolve())
    frozen_v4.require(
        len(set(resolved)) == 12,
        "public version 6 shared or duplicated an independent correctness proof",
    )
    frozen_v4.require(
        isinstance(edges, tuple)
        and len(edges) == 3
        and all(isinstance(edge, Path) for edge in edges)
        and tuple(edge.resolve() for edge in edges)
        == tuple(edge.resolve() for edge in MIXED_EDGE_ORACLES),
        "public version 6 omitted, reordered, or substituted an engine edge proof",
    )


def require_stage05_correctness_path_contract() -> None:
    """Bind four new Rust reports and the eight preserved C and Zig reports."""

    _validate_proof_contract(
        frozen_v4.STAGE05_CORRECTNESS_PATHS,
        frozen_v4.DEFAULT_EDGE_ORACLES,
        frozen_v4.STAGE05_CANDIDATES,
        frozen_v4.STAGE05_DEEP_FAMILIES,
    )
    frozen_v4.require(
        frozen_v4.STAGE05_CANDIDATES == frozen_v4.UNIVERSAL_ORACLE_CANDIDATES,
        "public version 6 changed the independently verified universal families",
    )


def _validated_runtime_provenance(report: Mapping[str, Any]) -> dict[str, Any]:
    """Bind the current V2 verifier and its separately preserved V1 worker."""

    frozen_v4.require(
        isinstance(report, Mapping)
        and report.get("schema") == STRICT_AUDIT_SCHEMA
        and report.get("postfinal_schema") == STRICT_AUDIT_SCHEMA
        and report.get("status") == "PASS"
        and report.get("result") == "PASS"
        and report.get("passed") is True
        and report.get("audit_source_path")
        == _owned_relative(STRICT_AUDIT_SOURCE_PATH)
        and report.get("audit_source_sha256") == STRICT_AUDIT_SOURCE_SHA256
        and report.get("base_audit_report_path") == _owned_relative(BASE_AUDIT_PATH)
        and report.get("base_audit_report_sha256") == BASE_AUDIT_SHA256
        and report.get("base_audit_source_path")
        == _owned_relative(BASE_AUDIT_SOURCE_PATH)
        and report.get("base_audit_source_sha256") == BASE_AUDIT_SOURCE_SHA256
        and report.get("inherited_control_count") == 76,
        "the public version-6 V2 audit or its actual base was substituted",
    )
    frozen_v4.require(
        report.get("immutable_no_delegation_source_path")
        == _owned_relative(IMMUTABLE_WORKER_SOURCE_PATH)
        and report.get("immutable_no_delegation_source_sha256")
        == IMMUTABLE_WORKER_SOURCE_SHA256
        and report.get("immutable_no_delegation_report_path")
        == _owned_relative(IMMUTABLE_WORKER_REPORT_PATH)
        and report.get("immutable_no_delegation_report_sha256")
        == IMMUTABLE_WORKER_REPORT_SHA256
        and report.get("immutable_no_delegation_schema") == IMMUTABLE_WORKER_SCHEMA,
        "the public version-6 independently guarded V1 worker was substituted",
    )
    scope = report.get("scope")
    frozen_v4.require(
        isinstance(scope, Mapping)
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("immutable_v1_source_preserved") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the public version-6 guarded-worker isolation scope was weakened",
    )
    return {
        "postfinal_guarded_worker_source_path": str(
            IMMUTABLE_WORKER_SOURCE_PATH.resolve()
        ),
        "postfinal_guarded_worker_source_sha256": IMMUTABLE_WORKER_SOURCE_SHA256,
        "postfinal_guarded_worker_schema": IMMUTABLE_WORKER_SCHEMA,
        "postfinal_guarded_worker_report_path": str(
            IMMUTABLE_WORKER_REPORT_PATH.resolve()
        ),
        "postfinal_guarded_worker_report_sha256": IMMUTABLE_WORKER_REPORT_SHA256,
    }


def verified_from_scratch_audit() -> tuple[
    str, dict[str, str], dict[str, str], dict[str, Any]
]:
    """Retain every inherited real audit check and separately bind the worker."""

    frozen_v4.require_candidate_free()
    for path, expected, label in (
        (BASE_AUDIT_PATH, BASE_AUDIT_SHA256, "actual V2 from-scratch audit"),
        (
            BASE_AUDIT_SOURCE_PATH,
            BASE_AUDIT_SOURCE_SHA256,
            "actual V2 from-scratch audit source",
        ),
        (STRICT_AUDIT_PATH, STRICT_AUDIT_SHA256, "actual V2 isolation audit"),
        (
            STRICT_AUDIT_SOURCE_PATH,
            STRICT_AUDIT_SOURCE_SHA256,
            "actual V2 isolation audit source",
        ),
        (
            IMMUTABLE_WORKER_SOURCE_PATH,
            IMMUTABLE_WORKER_SOURCE_SHA256,
            "immutable V1 guarded-worker source",
        ),
        (
            IMMUTABLE_WORKER_REPORT_PATH,
            IMMUTABLE_WORKER_REPORT_SHA256,
            "immutable V1 guarded-worker provenance report",
        ),
    ):
        frozen_v4.require(
            path.is_file()
            and not path.is_symlink()
            and frozen_v4.pilot.file_sha256(path) == expected,
            f"the {label} is missing, changed, or substituted",
        )
    digest, sources, native, details = _FROZEN_V4_VERIFIED_AUDIT()
    frozen_v4.require(
        digest == BASE_AUDIT_SHA256
        and details.get("postfinal_no_delegation_audit_sha256")
        == STRICT_AUDIT_SHA256
        and details.get("postfinal_no_delegation_audit_source_sha256")
        == STRICT_AUDIT_SOURCE_SHA256
        and details.get("postfinal_no_delegation_control_count")
        == STRICT_AUDIT_CONTROL_COUNT,
        "the public version-6 real current-source audit chain was substituted",
    )
    report = frozen_v4.read_json(STRICT_AUDIT_PATH, "passing V2 isolation audit")
    runtime = _validated_runtime_provenance(report)
    frozen_v4.require_candidate_free()
    return digest, sources, native, {**details, **runtime}


def load_guarded_worker_module(expected_source_sha256: str) -> types.ModuleType:
    """Check V2's verifier, then load only its pinned immutable V1 bootstrap."""

    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    frozen_v4.require(
        expected_source_sha256 == STRICT_AUDIT_SOURCE_SHA256
        and frozen_v4.pilot.file_sha256(STRICT_AUDIT_SOURCE_PATH)
        == expected_source_sha256
        and frozen_v4.pilot.file_sha256(STRICT_AUDIT_PATH) == STRICT_AUDIT_SHA256,
        "the frozen current V2 guarded-worker verifier changed",
    )
    report = frozen_v4.read_json(STRICT_AUDIT_PATH, "frozen V2 isolation audit")
    runtime = _validated_runtime_provenance(report)
    frozen_v4.require(
        frozen_v4.pilot.file_sha256(IMMUTABLE_WORKER_SOURCE_PATH)
        == runtime["postfinal_guarded_worker_source_sha256"]
        and frozen_v4.pilot.file_sha256(IMMUTABLE_WORKER_REPORT_PATH)
        == runtime["postfinal_guarded_worker_report_sha256"],
        "the immutable source-bound guarded worker changed after public freezing",
    )
    module = importlib.import_module("tools.postfinal_no_delegation_audit_v1")
    frozen_v4.require(
        Path(getattr(module, "__file__", "")).resolve()
        == IMMUTABLE_WORKER_SOURCE_PATH.resolve()
        and getattr(module, "SCHEMA", None) == IMMUTABLE_WORKER_SCHEMA
        and frozen_v4.pilot.file_sha256(Path(module.__file__).resolve())
        == IMMUTABLE_WORKER_SOURCE_SHA256
        and callable(getattr(module, "guarded_worker_command", None))
        and callable(getattr(module, "validate_guarded_worker_response", None)),
        "the immutable audited guarded-worker bootstrap was substituted",
    )
    frozen_v4.require_candidate_free()
    return module


def _validate_public_parity(
    original: Mapping[str, Any], document: Mapping[str, Any]
) -> None:
    """Require identical public cases, categories, weights, and paired rules."""

    frozen_v4.require(
        isinstance(original, Mapping)
        and isinstance(document, Mapping)
        and original.get("postfinal_schema")
        == "rebar-postfinal-public-practice-plan-v5"
        and original.get("protocol_version") == FROZEN_V5_VERSION
        and original.get("runner_sha256") == FROZEN_V5_SOURCE_SHA256
        and document.get("postfinal_schema") == POSTFINAL_PLAN_SCHEMA
        and document.get("protocol_version") == VERSION
        and frozen_v4.valid_sha256(document.get("runner_sha256")),
        "public version 6 does not bind the exact immutable public predecessor",
    )
    for field in PUBLIC_PARITY_FIELDS:
        frozen_v4.require(
            field in original
            and field in document
            and document[field] == original[field],
            f"public version 6 changed the original public workload: {field}",
        )
    frozen_v4.require(
        original.get("cases") == 8_192
        and original.get("all_bounded_workload_categories") == 260
        and original.get("modules") == list(frozen_v4.MODULES)
        and original.get("public_operations") == FROZEN_PUBLIC_OPERATION_COUNTS
        and sum(FROZEN_PUBLIC_OPERATION_COUNTS.values()) == 8_192
        and original.get("selection_seed") == 2026072404
        and original.get("order_seed") == 2026072405
        and original.get("bootstrap_seed") == 2026072406
        and original.get("frozen_warmups") == 4
        and original.get("frozen_trials") == 13
        and original.get("frozen_bootstrap_samples") == 2_000
        and original.get("holdout_accessed") is False
        and original.get("held_out_cases_generated") == 0
        and original.get("held_out_records_deserialized") == 0
        and original.get("historical_performance_read") is False
        and original.get("timing_performed") is False,
        "public version 6 weakened a frozen workload, confidence, or holdout rule",
    )
    selected = original.get("selected_cases")
    frozen_v4.require(
        isinstance(selected, list) and len(selected) == 8_192,
        "public version 6 changed the exact public case denominator",
    )
    identifiers: set[str] = set()
    api_counts: collections.Counter[str] = collections.Counter()
    category_counts: collections.Counter[str] = collections.Counter()
    for entry in selected:
        frozen_v4.require(
            isinstance(entry, dict)
            and isinstance(entry.get("case"), str)
            and entry["case"] not in identifiers
            and entry.get("cohort") == frozen_v4.pilot.PRACTICE
            and isinstance(entry.get("api"), str)
            and isinstance(entry.get("category"), str)
            and frozen_v4.valid_sha256(entry.get("expected_result_sha256"))
            and isinstance(entry.get("selection_reasons"), list)
            and type(entry.get("frozen_operations")) is int
            and entry["frozen_operations"] > 0,
            "public version 6 concealed, duplicated, or weakened a public case",
        )
        identifiers.add(entry["case"])
        api_counts[entry["api"]] += 1
        category_counts[entry["category"]] += 1
    frozen_v4.require(
        dict(api_counts) == FROZEN_PUBLIC_OPERATION_COUNTS
        and isinstance(original.get("categories"), dict)
        and len(original["categories"]) == 260
        and dict(category_counts) == original["categories"],
        "public version 6 changed a public operation or workload category weight",
    )


def _verified_frozen_v5_manifest() -> dict[str, Any]:
    """Read only the immutable public plan, never historical observations."""

    frozen_v4.require_candidate_free()
    frozen_v4.require(
        frozen_v5.VERSION == FROZEN_V5_VERSION
        and Path(frozen_v5.__file__).resolve() == FROZEN_V5_SOURCE_PATH.resolve()
        and FROZEN_V5_SOURCE_PATH.is_file()
        and not FROZEN_V5_SOURCE_PATH.is_symlink()
        and frozen_v4.pilot.file_sha256(FROZEN_V5_SOURCE_PATH)
        == FROZEN_V5_SOURCE_SHA256,
        "the immutable public version-5 runner was changed or substituted",
    )
    frozen_v4.require(
        FROZEN_V5_MANIFEST_PATH.is_file()
        and not FROZEN_V5_MANIFEST_PATH.is_symlink()
        and frozen_v4.pilot.file_sha256(FROZEN_V5_MANIFEST_PATH)
        == FROZEN_V5_MANIFEST_SHA256,
        "the immutable public version-5 plan was changed or substituted",
    )
    document = frozen_v4.read_json(
        FROZEN_V5_MANIFEST_PATH,
        "immutable 8,192-case public version-5 prospective plan",
    )
    frozen_v4.require_candidate_free()
    return document


def make_manifest(
    edge_paths: list[Path],
) -> tuple[Any, list[Any], dict[str, Any]]:
    """Preserve the exact V5 public population under freshly audited engines."""

    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    frozen_v4.require(
        UNIVERSAL_V4_SOURCE_PATH.is_file()
        and not UNIVERSAL_V4_SOURCE_PATH.is_symlink()
        and frozen_v4.pilot.file_sha256(UNIVERSAL_V4_SOURCE_PATH)
        == UNIVERSAL_V4_SOURCE_SHA256
        and UNIVERSAL_V4_REPORT_PATH.is_file()
        and not UNIVERSAL_V4_REPORT_PATH.is_symlink()
        and frozen_v4.pilot.file_sha256(UNIVERSAL_V4_REPORT_PATH)
        == UNIVERSAL_V4_REPORT_SHA256,
        "the complete passing version-4 universal public oracle was substituted",
    )
    predecessor = _verified_frozen_v5_manifest()
    suite, entries, document = _FROZEN_V4_MAKE_MANIFEST(edge_paths)
    frozen_v4.require(
        document.get("protocol_version") == VERSION
        and document.get("postfinal_schema") == POSTFINAL_PLAN_SCHEMA
        and document.get("exclusive_slot") == EXCLUSIVE_SLOT
        and document.get("runner_sha256")
        == frozen_v4.pilot.file_sha256(V6_SOURCE_PATH),
        "the public version-6 plan changed its exact frozen source or protocol",
    )
    _validate_public_parity(predecessor, document)
    provenance: dict[str, Any] = {
        "source_public_v5_runner_path": _owned_relative(FROZEN_V5_SOURCE_PATH),
        "source_public_v5_runner_sha256": FROZEN_V5_SOURCE_SHA256,
        "source_public_v5_manifest_path": _owned_relative(FROZEN_V5_MANIFEST_PATH),
        "source_public_v5_manifest_sha256": FROZEN_V5_MANIFEST_SHA256,
        "public_v5_case_population_preserved": True,
        "public_v5_case_population_count": 8_192,
        "public_v5_workload_category_count": 260,
        "private_worker_wire_format": frozen_v5.PRIVATE_WORKER_WIRE_FORMAT,
        "private_worker_wire_ensure_ascii": True,
    }
    for field, value in provenance.items():
        frozen_v4.require(
            field not in document,
            f"public version-6 predecessor provenance collides with {field}",
        )
        document[field] = value
    frozen_v4.require_candidate_free()
    return suite, entries, document


def _synthetic_runtime_report() -> dict[str, Any]:
    return {
        "schema": STRICT_AUDIT_SCHEMA,
        "postfinal_schema": STRICT_AUDIT_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": _owned_relative(STRICT_AUDIT_SOURCE_PATH),
        "audit_source_sha256": STRICT_AUDIT_SOURCE_SHA256,
        "base_audit_report_path": _owned_relative(BASE_AUDIT_PATH),
        "base_audit_report_sha256": BASE_AUDIT_SHA256,
        "base_audit_source_path": _owned_relative(BASE_AUDIT_SOURCE_PATH),
        "base_audit_source_sha256": BASE_AUDIT_SOURCE_SHA256,
        "inherited_control_count": 76,
        "immutable_no_delegation_source_path": _owned_relative(
            IMMUTABLE_WORKER_SOURCE_PATH
        ),
        "immutable_no_delegation_source_sha256": IMMUTABLE_WORKER_SOURCE_SHA256,
        "immutable_no_delegation_report_path": _owned_relative(
            IMMUTABLE_WORKER_REPORT_PATH
        ),
        "immutable_no_delegation_report_sha256": IMMUTABLE_WORKER_REPORT_SHA256,
        "immutable_no_delegation_schema": IMMUTABLE_WORKER_SCHEMA,
        "scope": {
            "persistent_measurement_worker_available": True,
            "immutable_v1_source_preserved": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    }


def _synthetic_public_manifests() -> tuple[dict[str, Any], dict[str, Any]]:
    """Construct all public-parity poison fixtures exclusively in memory."""

    api_sequence = [
        api
        for api, count in FROZEN_PUBLIC_OPERATION_COUNTS.items()
        for _position in range(count)
    ]
    categories = {
        f"synthetic-category-{index:03d}": 31 + (index < 132)
        for index in range(260)
    }
    selected = [
        {
            "case": f"cal.public.v6.synthetic.{index:05d}",
            "cohort": frozen_v4.pilot.PRACTICE,
            "category": f"synthetic-category-{index % 260:03d}",
            "api": api,
            "lifecycle": "compiled",
            "input": "text",
            "subject_length": 8,
            "result_count": 1,
            "result_density": "one",
            "frozen_operations": 1,
            "expected_result_sha256": "a" * 64,
            "selection_reasons": ["synthetic-public-workload"],
        }
        for index, api in enumerate(api_sequence)
    ]
    shared: dict[str, Any] = {
        "schema": frozen_v4.pilot.PLAN_SCHEMA,
        "python": "3.14.6",
        "cohort": frozen_v4.pilot.PRACTICE,
        "expected_sha256": "b" * 64,
        "source_fixture": "public-in-memory-synthetic-fixture",
        "source_fixture_sha256": "c" * 64,
        "source_fixture_uncompressed_sha256": "d" * 64,
        "source_fixture_manifest_sha256": "e" * 64,
        "source_v7_manifest_sha256": "f" * 64,
        "source_v7_suite_sha256": "1" * 64,
        "source_v7_runner_sha256": "2" * 64,
        "source_public_pilot_sha256": "3" * 64,
        "source_public_replay_sha256": "4" * 64,
        "source_public_v3_manifest_sha256": "5" * 64,
        "source_public_v3_runner_sha256": "6" * 64,
        "modules": list(frozen_v4.MODULES),
        "selection_seed": 2026072404,
        "order_seed": 2026072405,
        "bootstrap_seed": 2026072406,
        "frozen_trials": 13,
        "frozen_warmups": 4,
        "frozen_bootstrap_samples": 2_000,
        "default_trials": 13,
        "default_bootstrap_samples": 2_000,
        "cases": 8_192,
        "source_public_cases": 10_312,
        "eligible_practice_cases": 9_731,
        "all_bounded_workload_categories": 260,
        "bounded_public_api_capacities": dict(
            frozen_v4.EXPECTED_BOUNDED_API_COUNTS
        ),
        "public_operations": dict(FROZEN_PUBLIC_OPERATION_COUNTS),
        "lifetimes": {"compiled": 8_192},
        "inputs": {"text": 8_192},
        "result_densities": {"one": 8_192},
        "api_lifetimes": {
            f"{api} / compiled": count
            for api, count in FROZEN_PUBLIC_OPERATION_COUNTS.items()
        },
        "categories": categories,
        "maximum_subject_length": 8,
        "maximum_result_count": 1,
        "maximum_subject_limit": 8_192,
        "maximum_result_limit": 128,
        "maximum_operations_per_trial": 16,
        "strict_regression_speedup_threshold": 5.0 / 6.0,
        "selected_cases": selected,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "historical_performance_read": False,
        "timing_performed": False,
    }
    original = {
        **shared,
        "postfinal_schema": "rebar-postfinal-public-practice-plan-v5",
        "protocol_version": FROZEN_V5_VERSION,
        "runner_sha256": FROZEN_V5_SOURCE_SHA256,
    }
    document = {
        **shared,
        "postfinal_schema": POSTFINAL_PLAN_SCHEMA,
        "protocol_version": VERSION,
        "runner_sha256": "7" * 64,
    }
    return original, document


def synthetic_self_test() -> dict[str, Any]:
    """Run only in-memory proof, worker, Unicode, and public-case controls."""

    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    inherited = _FROZEN_V4_SELF_TEST()
    frozen_v4.require(
        inherited.get("result") == "PASS"
        and inherited.get("protocol_version") == VERSION
        and inherited.get("schema") == POSTFINAL_INTEGRITY_SCHEMA + "-self-test"
        and inherited.get("candidate_imported") is False
        and inherited.get("holdout_accessed") is False
        and inherited.get("held_out_cases_generated") == 0
        and inherited.get("held_out_records_deserialized") == 0
        and inherited.get("timing_performed") is False
        and inherited.get("failed") == 0
        and inherited.get("prospective_cases") == 8_192
        and inherited.get("synthetic_public_operations") == 12
        and inherited.get("prospective_stage05_correctness_artifact_count") == 12
        and inherited.get("prospective_stage05_fresh_edge_proof_count") == 3
        and inherited.get("prospective_universal_oracle_proof_field_count") == 23
        and inherited.get("prospective_stage05_deep_family_mapping")
        == {"rust": "RUST", "vm": "C", "zig": "ZIG"}
        and inherited.get("owned_source_poisoned_control_count") == 4
        and inherited.get("postfinal_poisoned_control_count") == 10,
        "the immutable candidate-free public correctness controls failed",
    )

    controls: list[dict[str, Any]] = []

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except (
            RuntimeError,
            frozen_v4.replay.AuditError,
            KeyError,
            TypeError,
            ValueError,
            OverflowError,
            RecursionError,
        ):
            controls.append({"name": name, "passed": True})
            return
        raise RuntimeError(f"public version-6 synthetic poison was accepted: {name}")

    wire_controls: list[dict[str, Any]] = []
    for name, value in (
        ("lone-high-surrogate", "\ud800"),
        ("lone-low-surrogate", "\udfff"),
        ("separated-lone-surrogates", "\ud800x\udfff"),
        ("emoji", "\U0001f600"),
        ("astral-code-point", "\U00010348"),
        ("combining-text", "e\u0301"),
        ("escaped-newline", "left\nright"),
    ):
        document = {
            "op": "prepare",
            "case": {"pattern": value, "string": value},
            "expected": {"value": value},
        }
        encoded = frozen_v5.encode_private_worker_request(document)
        frozen_v4.require(
            encoded.isascii()
            and "\n" not in encoded
            and json.loads(encoded) == document
            and frozen_v5.encode_private_worker_request(json.loads(encoded))
            == encoded,
            f"public version 6 lost the immutable Unicode-safe worker: {name}",
        )
        wire_controls.append({"name": name, "passed": True})

    circular: dict[str, Any] = {}
    circular["self"] = circular
    for name, document in (
        ("wire-nan", {"op": "prepare", "value": float("nan")}),
        ("wire-positive-infinity", {"op": "prepare", "value": float("inf")}),
        ("wire-negative-infinity", {"op": "prepare", "value": float("-inf")}),
        ("wire-unserializable-object", {"op": "prepare", "value": object()}),
        ("wire-unserializable-bytes", {"op": "prepare", "value": b"private"}),
        ("wire-circular-document", circular),
    ):
        reject(name, lambda value=document: frozen_v5.encode_private_worker_request(value))

    expected_paths = MIXED_CORRECTNESS_PATHS
    candidates = ("rust", "vm", "zig")
    families = {"rust": "RUST", "vm": "C", "zig": "ZIG"}

    def check_paths(
        paths: tuple[tuple[str, Path], ...] = expected_paths,
        edges: tuple[Path, ...] = MIXED_EDGE_ORACLES,
        names: tuple[str, ...] = candidates,
        mapping: Mapping[str, str] = families,
    ) -> None:
        _validate_proof_contract(paths, edges, names, mapping)

    check_paths()
    old_rust_edge = _FROZEN_V5_STAGE_PATHS["rust-edge"]
    old_rust_deep = _FROZEN_V5_STAGE_PATHS["rust-deep-public-contract"]
    for name, action in (
        (
            "missing-rust-correctness-proof",
            lambda: check_paths(paths=expected_paths[1:]),
        ),
        (
            "historical-rust-edge-proof",
            lambda: check_paths(
                paths=(("rust-edge", old_rust_edge), *expected_paths[1:])
            ),
        ),
        (
            "historical-rust-deep-proof",
            lambda: check_paths(
                paths=(
                    expected_paths[0],
                    ("rust-deep-public-contract", old_rust_deep),
                    *expected_paths[2:],
                )
            ),
        ),
        (
            "reordered-independent-proof",
            lambda: check_paths(
                paths=(expected_paths[1], expected_paths[0], *expected_paths[2:])
            ),
        ),
        (
            "cross-family-correctness-proof",
            lambda: check_paths(
                paths=(
                    ("rust-edge", dict(expected_paths)["vm-edge"]),
                    *expected_paths[1:],
                )
            ),
        ),
        (
            "missing-independent-edge",
            lambda: check_paths(edges=MIXED_EDGE_ORACLES[:2]),
        ),
        (
            "reordered-independent-edges",
            lambda: check_paths(edges=tuple(reversed(MIXED_EDGE_ORACLES))),
        ),
        (
            "historical-independent-rust-edge",
            lambda: check_paths(edges=(old_rust_edge, *MIXED_EDGE_ORACLES[1:])),
        ),
        (
            "omitted-independent-candidate",
            lambda: check_paths(names=("rust", "vm")),
        ),
        (
            "cross-family-deep-contract",
            lambda: check_paths(mapping={"rust": "C", "vm": "RUST", "zig": "ZIG"}),
        ),
    ):
        reject(name, action)

    runtime = _synthetic_runtime_report()
    _validated_runtime_provenance(runtime)
    for name, change in (
        ("historical-v1-accepted-as-current-v2", {"schema": IMMUTABLE_WORKER_SCHEMA}),
        ("changed-current-audit-schema", {"postfinal_schema": "foreign-audit"}),
        ("failing-current-audit", {"passed": False}),
        ("failing-current-audit-status", {"status": "FAIL"}),
        ("substituted-current-verifier", {"audit_source_sha256": "0" * 64}),
        ("substituted-current-base", {"base_audit_report_sha256": "0" * 64}),
        ("weakened-inherited-controls", {"inherited_control_count": 75}),
        (
            "foreign-v1-worker-source",
            {"immutable_no_delegation_source_path": "tools/foreign_worker.py"},
        ),
        (
            "substituted-v1-worker-binary-source",
            {"immutable_no_delegation_source_sha256": "0" * 64},
        ),
        (
            "substituted-v1-worker-proof",
            {"immutable_no_delegation_report_sha256": "0" * 64},
        ),
        (
            "substituted-v1-worker-schema",
            {"immutable_no_delegation_schema": "foreign-worker"},
        ),
        (
            "holdout-accessing-worker-scope",
            {"scope": {**runtime["scope"], "holdout_or_case_fixture_access": True}},
        ),
        (
            "timing-worker-scope",
            {"scope": {**runtime["scope"], "benchmark_or_timing_executed": True}},
        ),
        (
            "unavailable-independent-worker",
            {
                "scope": {
                    **runtime["scope"],
                    "persistent_measurement_worker_available": False,
                }
            },
        ),
        (
            "unpreserved-v1-worker",
            {"scope": {**runtime["scope"], "immutable_v1_source_preserved": False}},
        ),
    ):
        reject(
            name,
            lambda replacement=change: _validated_runtime_provenance(
                {**runtime, **replacement}
            ),
        )

    original, document = _synthetic_public_manifests()
    _validate_public_parity(original, document)
    first = document["selected_cases"][0]
    for name, change in (
        ("changed-public-case-denominator", {"cases": 8_191}),
        ("changed-public-selection-seed", {"selection_seed": 2026072407}),
        ("changed-paired-trial-denominator", {"frozen_trials": 12}),
        ("changed-confidence-denominator", {"frozen_bootstrap_samples": 1_999}),
        ("concealed-public-workload-category", {"all_bounded_workload_categories": 259}),
        (
            "changed-public-operation-weights",
            {
                "public_operations": {
                    **FROZEN_PUBLIC_OPERATION_COUNTS,
                    "search": FROZEN_PUBLIC_OPERATION_COUNTS["search"] - 1,
                }
            },
        ),
        (
            "substituted-public-case",
            {
                "selected_cases": [
                    {**first, "case": "cal.public.v6.synthetic.substituted"},
                    *document["selected_cases"][1:],
                ]
            },
        ),
        ("opened-final-holdout", {"holdout_accessed": True}),
        ("deserialized-final-case", {"held_out_records_deserialized": 1}),
        ("read-historical-timing", {"historical_performance_read": True}),
        ("premature-public-timing", {"timing_performed": True}),
        ("substituted-public-version", {"protocol_version": FROZEN_V5_VERSION}),
    ):
        reject(
            name,
            lambda replacement=change: _validate_public_parity(
                original, {**document, **replacement}
            ),
        )

    names = [item["name"] for item in controls]
    frozen_v4.require(
        len(controls) == 43
        and len(set(names)) == len(names)
        and all(item.get("passed") is True for item in controls)
        and len(wire_controls) == 7
        and frozen_v4.PersistentGuardedWorker is frozen_v5.PersistentGuardedWorker,
        "public version 6 omitted or weakened an independent synthetic poison",
    )
    frozen_v4.require_candidate_free()
    return {
        **inherited,
        "source_public_v5_runner_path": _owned_relative(FROZEN_V5_SOURCE_PATH),
        "source_public_v5_runner_sha256": FROZEN_V5_SOURCE_SHA256,
        "source_public_v5_manifest_sha256": FROZEN_V5_MANIFEST_SHA256,
        "public_predecessor_evidence_accessed": False,
        "actual_v2_audits_accessed": False,
        "actual_universal_report_accessed": False,
        "private_worker_wire_format": frozen_v5.PRIVATE_WORKER_WIRE_FORMAT,
        "private_worker_wire_ensure_ascii": True,
        "private_worker_wire_control_count": len(wire_controls),
        "private_worker_wire_controls": wire_controls,
        "postfinal_v6_poisoned_control_count": len(controls),
        "postfinal_v6_poisoned_controls": controls,
        "mixed_correctness_artifact_count": len(MIXED_CORRECTNESS_PATHS),
        "fresh_rust_correctness_artifact_count": 4,
        "preserved_peer_correctness_artifact_count": 8,
        "worker_processes_started": 0,
        "benchmark_or_timing_executed": False,
        "failed": 0,
    }


def freeze(args: Any) -> dict[str, Any]:
    """Exclusively create a prospective public plan; never start or time workers."""

    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    target = frozen_v4.exact_versioned_path(
        args.output,
        MANIFEST_PATH,
        "frozen public version-6 prospective manifest",
    )
    frozen_v4.require(
        not target.exists(),
        "refusing to overwrite the exclusively frozen public version-6 manifest",
    )
    edge_paths = (
        list(args.edge_oracle) if args.edge_oracle else list(MIXED_EDGE_ORACLES)
    )
    _suite, entries, document = make_manifest(edge_paths)
    manifest_sha256 = frozen_v4.pilot.save_json(target, document)
    frozen_v4.require_candidate_free()
    audit_fields = (
        "postfinal_no_delegation_audit_path",
        "postfinal_no_delegation_audit_sha256",
        "postfinal_no_delegation_audit_source_path",
        "postfinal_no_delegation_audit_source_sha256",
        "postfinal_no_delegation_audit_schema",
        "postfinal_no_delegation_control_count",
        "postfinal_guarded_worker_source_path",
        "postfinal_guarded_worker_source_sha256",
        "postfinal_guarded_worker_schema",
        "postfinal_guarded_worker_report_path",
        "postfinal_guarded_worker_report_sha256",
    )
    return {
        "schema": POSTFINAL_PLAN_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "freeze_only": True,
        "candidate_imported": False,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "benchmark_or_timing_executed": False,
        "worker_processes_started": 0,
        "cases": len(entries),
        "source_public_cases": frozen_v4.FIXTURE_CASES,
        "eligible_practice_cases": frozen_v4.ELIGIBLE_CASES,
        "all_bounded_workload_categories": frozen_v4.CATEGORIES,
        "public_operations": document["public_operations"],
        "trials": frozen_v4.TRIALS,
        "bootstrap_draws": frozen_v4.BOOTSTRAPS,
        "prospective_paired_raw_rows": frozen_v4.EXPECTED_ROWS,
        "prospective_correctness_checks": frozen_v4.EXPECTED_CORRECTNESS_CHECKS,
        "verified_independent_engine_count": len(frozen_v4.MODULES) - 1,
        "verified_native_library_count": len(document["native_elf_fingerprints"]),
        **{key: document[key] for key in audit_fields},
        **{key: document[key] for key in frozen_v4.UNIVERSAL_ORACLE_PROOF_FIELDS},
        "source_public_v5_runner_sha256": FROZEN_V5_SOURCE_SHA256,
        "source_public_v5_manifest_sha256": FROZEN_V5_MANIFEST_SHA256,
        "public_v5_case_population_preserved": True,
        "runner_sha256": document["runner_sha256"],
        "manifest": str(target),
        "manifest_sha256": manifest_sha256,
        "failed": 0,
    }


def _require_committed_and_pushed_freeze() -> None:
    """Permit actual timing only after the exact public plan reached main."""

    frozen_v4.require_candidate_free()

    def git(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    required_paths = (
        V6_SOURCE_PATH,
        MANIFEST_PATH,
        VERSION_ROOT / "PROTOCOL.md",
    )
    owned: list[str] = []
    for path in required_paths:
        frozen_v4.require(
            path.is_file() and not path.is_symlink(),
            "the exact public version-6 source, manifest, or protocol is missing",
        )
        owned.append(_owned_relative(path))

    for chart_path in (
        ROOT / "tools" / "postfinal_public_practice_charts_v6.py",
        ROOT / "tools" / "postfinal_public_practice_presentation_v2.py",
    ):
        relative = _owned_relative(chart_path)
        tracked_chart = git("ls-files", "--error-unmatch", "--", relative)
        if chart_path.exists() or chart_path.is_symlink():
            frozen_v4.require(
                chart_path.is_file() and not chart_path.is_symlink(),
                "a public version-6 chart source was substituted or escaped",
            )
            owned.append(relative)
        else:
            frozen_v4.require(
                tracked_chart.returncode != 0,
                "a committed public version-6 chart source was removed",
            )

    tracked = git("ls-files", "--error-unmatch", "--", *owned)
    frozen_v4.require(
        tracked.returncode == 0,
        "the public version-6 source, manifest, protocol, and chart sources "
        "must be committed before timing",
    )
    clean = git("status", "--porcelain", "--", *owned)
    frozen_v4.require(
        clean.returncode == 0 and not clean.stdout.strip(),
        "the committed public version-6 source, manifest, protocol, or charts "
        "have uncommitted changes",
    )
    branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    frozen_v4.require(
        branch.returncode == 0 and branch.stdout.strip() == "main",
        "public version-6 measurement is authorized only on the frozen main branch",
    )
    pushed = git("merge-base", "--is-ancestor", "HEAD", "origin/main")
    frozen_v4.require(
        pushed.returncode == 0,
        "the public version-6 source and manifest must be pushed before timing",
    )
    frozen_v4.require_candidate_free()


def measure(args: Any) -> dict[str, Any]:
    """Require the pushed plan and explicit V6 slot before public timing."""

    frozen_v4.require(
        getattr(args, "exclusive_slot", None) == EXCLUSIVE_SLOT,
        "public version-6 timing requires its explicit, unique V6 slot",
    )
    _require_committed_and_pushed_freeze()
    return _FROZEN_V4_MEASURE(args)


def verify(args: Any) -> dict[str, Any]:
    """Independently replay only the explicitly frozen, pushed public run."""

    _require_committed_and_pushed_freeze()
    return _FROZEN_V4_VERIFY(args)


for name, value in {
    "__file__": str(V6_SOURCE_PATH),
    "VERSION": VERSION,
    "VERSION_ROOT": VERSION_ROOT,
    "EVIDENCE_ROOT": EVIDENCE_ROOT,
    "MANIFEST_PATH": MANIFEST_PATH,
    "RAW_PATH": RAW_PATH,
    "SUMMARY_PATH": SUMMARY_PATH,
    "INTEGRITY_PATH": INTEGRITY_PATH,
    "POSTFINAL_PLAN_SCHEMA": POSTFINAL_PLAN_SCHEMA,
    "POSTFINAL_REPORT_SCHEMA": POSTFINAL_REPORT_SCHEMA,
    "POSTFINAL_INTEGRITY_SCHEMA": POSTFINAL_INTEGRITY_SCHEMA,
    "EXCLUSIVE_SLOT": EXCLUSIVE_SLOT,
    "AUDIT_PATH": BASE_AUDIT_PATH,
    "AUDIT_SOURCE_PATH": BASE_AUDIT_SOURCE_PATH,
    "POSTFINAL_AUDIT_PATH": STRICT_AUDIT_PATH,
    "POSTFINAL_AUDIT_SOURCE_PATH": STRICT_AUDIT_SOURCE_PATH,
    "POSTFINAL_AUDIT_SCHEMA": STRICT_AUDIT_SCHEMA,
    "POSTFINAL_AUDIT_CONTROL_COUNT": STRICT_AUDIT_CONTROL_COUNT,
    "UNIVERSAL_ORACLE_SOURCE_PATH": UNIVERSAL_V4_SOURCE_PATH,
    "UNIVERSAL_ORACLE_SOURCE_SHA256": UNIVERSAL_V4_SOURCE_SHA256,
    "UNIVERSAL_ORACLE_REPORT_PATH": UNIVERSAL_V4_REPORT_PATH,
    "STAGE05_CORRECTNESS_PATHS": MIXED_CORRECTNESS_PATHS,
    "DEFAULT_EDGE_ORACLES": MIXED_EDGE_ORACLES,
    "PersistentGuardedWorker": frozen_v5.PersistentGuardedWorker,
    "require_stage05_correctness_path_contract": (
        require_stage05_correctness_path_contract
    ),
    "verified_from_scratch_audit": verified_from_scratch_audit,
    "load_guarded_worker_module": load_guarded_worker_module,
    "make_manifest": make_manifest,
    "synthetic_self_test": synthetic_self_test,
    "freeze": freeze,
    "measure": measure,
    "verify": verify,
}.items():
    setattr(frozen_v4, name, value)


def __getattr__(name: str) -> Any:
    """Expose unchanged, independently replayable public comparison rules."""

    return getattr(frozen_v4, name)


def main(arguments: list[str] | None = None) -> None:
    """Require an explicit public self-test, freeze, measurement, or replay."""

    argv = list(sys.argv[1:] if arguments is None else arguments)
    if argv:
        argv[0] = {
            "--self-test": "self-test",
            "prepare": "freeze",
            "--prepare": "freeze",
            "--freeze": "freeze",
            "replay": "verify",
        }.get(argv[0], argv[0])
    original_argv = sys.argv
    try:
        sys.argv = [str(V6_SOURCE_PATH), *argv]
        frozen_v4.main()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    main()
