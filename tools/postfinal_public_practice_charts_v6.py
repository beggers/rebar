#!/usr/bin/env python3
"""Render six fully verified, source-bound version-6 public-practice charts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from tools import postfinal_public_practice_charts_v5 as inherited
from tools import postfinal_public_practice_v6 as protocol


v4 = inherited.previous
require = inherited.require
valid_sha256 = inherited.valid_sha256

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "postfinal-public-practice-v6"
PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v6"
EVIDENCE = PUBLIC_ROOT / "evidence"
MANIFEST = PUBLIC_ROOT / "manifest.json"
SUMMARY = EVIDENCE / f"{PREFIX}-summary.json"
INTEGRITY = EVIDENCE / f"{PREFIX}-integrity.json"
PUBLIC_RAW = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"

PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
PLAN_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-plan-v6"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
SUMMARY_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-report-v6"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v6"

V5_RENDERER_PATH = ROOT / "tools" / "postfinal_public_practice_charts_v5.py"
V5_RENDERER_SHA256 = (
    "7684cf5d3696ce97699406ae5b6451d47482ad707c1b74261972a1f2bfd39196"
)
V4_RENDERER_PATH = ROOT / "tools" / "postfinal_public_practice_charts_v4.py"
V4_RENDERER_SHA256 = (
    "85ea57956381d67b76517c04a7d99777c72f1ea9bbd52670637b52376d913e79"
)
RUNNER_PATH = ROOT / "tools" / "postfinal_public_practice_v6.py"

V5_PREFIX = "postfinal-public-practice-v5"
V5_PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v5"
V5_EVIDENCE = V5_PUBLIC_ROOT / "evidence"
V5_MANIFEST = V5_PUBLIC_ROOT / "manifest.json"
V5_SUMMARY = V5_EVIDENCE / f"{V5_PREFIX}-summary.json"
V5_INTEGRITY = V5_EVIDENCE / f"{V5_PREFIX}-integrity.json"
V5_PUBLIC_RAW = V5_EVIDENCE / f"{V5_PREFIX}-raw.jsonl.gz"

_INHERITED_REQUIRE_AUDIT = v4.require_audit_binding
_INHERITED_REQUIRE_UNIVERSAL = v4.require_universal_oracle
_INHERITED_REQUIRE_ARTIFACTS = v4.require_stage05_artifacts
_INHERITED_REQUIRE_WORKERS = v4.require_worker_topology
_INHERITED_CHECK_MANIFEST = v4.check_v4_manifest


def _relative(path: Path) -> str:
    resolved = path.resolve()
    require(
        resolved.is_relative_to(ROOT.resolve()),
        "a public V6 chart source or proof escaped the owned repository",
    )
    return str(resolved.relative_to(ROOT.resolve()))


def _mixed_artifact_paths() -> dict[str, str]:
    return {
        role: _relative(path)
        for role, path in protocol.MIXED_CORRECTNESS_PATHS
    }


def _mixed_edge_paths() -> dict[str, str]:
    proofs = dict(protocol.MIXED_CORRECTNESS_PATHS)
    return {
        module: str(proofs[f"{family}-edge"].resolve())
        for module, family in zip(
            v4.MODULES[1:], ("rust", "vm", "zig"), strict=True
        )
    }


def require_inherited_source_binding(
    source_path: Path,
    source_sha256: str,
    *,
    expected_path: Path,
    expected_sha256: str,
) -> None:
    require(
        isinstance(source_path, Path)
        and source_path.resolve() == expected_path.resolve(),
        "an independently pinned public chart renderer source was substituted",
    )
    require(
        valid_sha256(source_sha256)
        and valid_sha256(expected_sha256)
        and source_sha256 == expected_sha256,
        "an independently pinned public chart renderer fingerprint changed",
    )


def verify_inherited_renderer_sources() -> None:
    """Read only the two explicitly authorized, immutable chart sources."""

    for module, expected_path, expected_sha256 in (
        (inherited, V5_RENDERER_PATH, V5_RENDERER_SHA256),
        (v4, V4_RENDERER_PATH, V4_RENDERER_SHA256),
    ):
        source_path = Path(module.__file__).resolve()
        require(
            source_path == expected_path.resolve(),
            "an imported inherited public chart renderer was substituted",
        )
        require_inherited_source_binding(
            source_path,
            hashlib.sha256(source_path.read_bytes()).hexdigest(),
            expected_path=expected_path,
            expected_sha256=expected_sha256,
        )


def require_runner_source_binding(
    source_path: Path,
    source_sha256: str,
    expected_sha256: str,
) -> None:
    require(
        isinstance(source_path, Path)
        and source_path.resolve() == RUNNER_PATH.resolve(),
        "the public V6 chart runner source was substituted",
    )
    require(
        valid_sha256(source_sha256)
        and valid_sha256(expected_sha256)
        and source_sha256 == expected_sha256,
        "the externally pinned public V6 runner source changed",
    )


def require_protocol_contract() -> None:
    """Check constants and proof identities without reading any evidence."""

    require(
        Path(protocol.__file__).resolve() == RUNNER_PATH.resolve()
        and protocol.VERSION == PREFIX
        and protocol.VERSION_ROOT.resolve() == PUBLIC_ROOT.resolve()
        and protocol.EVIDENCE_ROOT.resolve() == EVIDENCE.resolve()
        and protocol.MANIFEST_PATH.resolve() == MANIFEST.resolve()
        and protocol.RAW_PATH.resolve() == PUBLIC_RAW.resolve()
        and protocol.SUMMARY_PATH.resolve() == SUMMARY.resolve()
        and protocol.INTEGRITY_PATH.resolve() == INTEGRITY.resolve()
        and protocol.POSTFINAL_PLAN_SCHEMA == PLAN_POSTFINAL_SCHEMA
        and protocol.POSTFINAL_REPORT_SCHEMA == SUMMARY_POSTFINAL_SCHEMA
        and protocol.POSTFINAL_INTEGRITY_SCHEMA == INTEGRITY_SCHEMA
        and protocol.EXCLUSIVE_SLOT == PREFIX,
        "the chart renderer was bound to a different public V6 protocol",
    )
    protocol._validate_proof_contract(
        protocol.MIXED_CORRECTNESS_PATHS,
        protocol.MIXED_EDGE_ORACLES,
        ("rust", "vm", "zig"),
        {"rust": "RUST", "vm": "C", "zig": "ZIG"},
    )
    require(
        len(_mixed_artifact_paths()) == 12
        and len(_mixed_edge_paths()) == 3
        and len(protocol.FROZEN_PUBLIC_OPERATION_COUNTS) == 12
        and sum(protocol.FROZEN_PUBLIC_OPERATION_COUNTS.values()) == 8_192
        and protocol.STRICT_AUDIT_CONTROL_COUNT == 32,
        "the public V6 engines, correctness proofs, or workload weights changed",
    )


def _expected_audit_fields() -> dict[str, Any]:
    return {
        "from_scratch_audit_sha256": protocol.BASE_AUDIT_SHA256,
        "from_scratch_audit_source_path": str(
            protocol.BASE_AUDIT_SOURCE_PATH.resolve()
        ),
        "from_scratch_audit_source_sha256": (
            protocol.BASE_AUDIT_SOURCE_SHA256
        ),
        "postfinal_no_delegation_audit_path": str(
            protocol.STRICT_AUDIT_PATH.resolve()
        ),
        "postfinal_no_delegation_audit_sha256": protocol.STRICT_AUDIT_SHA256,
        "postfinal_no_delegation_audit_source_path": str(
            protocol.STRICT_AUDIT_SOURCE_PATH.resolve()
        ),
        "postfinal_no_delegation_audit_source_sha256": (
            protocol.STRICT_AUDIT_SOURCE_SHA256
        ),
        "postfinal_no_delegation_audit_schema": protocol.STRICT_AUDIT_SCHEMA,
        "postfinal_no_delegation_control_count": (
            protocol.STRICT_AUDIT_CONTROL_COUNT
        ),
    }


def _expected_worker_fields() -> dict[str, Any]:
    return {
        "postfinal_guarded_worker_source_path": str(
            protocol.IMMUTABLE_WORKER_SOURCE_PATH.resolve()
        ),
        "postfinal_guarded_worker_source_sha256": (
            protocol.IMMUTABLE_WORKER_SOURCE_SHA256
        ),
        "postfinal_guarded_worker_schema": protocol.IMMUTABLE_WORKER_SCHEMA,
        "postfinal_guarded_worker_report_path": str(
            protocol.IMMUTABLE_WORKER_REPORT_PATH.resolve()
        ),
        "postfinal_guarded_worker_report_sha256": (
            protocol.IMMUTABLE_WORKER_REPORT_SHA256
        ),
    }


def _expected_universal_fields() -> dict[str, Any]:
    return {
        "python_re_universal_oracle_source_path": str(
            protocol.UNIVERSAL_V4_SOURCE_PATH.resolve()
        ),
        "python_re_universal_oracle_source_sha256": (
            protocol.UNIVERSAL_V4_SOURCE_SHA256
        ),
        "python_re_universal_oracle_report_path": str(
            protocol.UNIVERSAL_V4_REPORT_PATH.resolve()
        ),
        "python_re_universal_oracle_report_sha256": (
            protocol.UNIVERSAL_V4_REPORT_SHA256
        ),
        "python_re_universal_oracle_original_audit_sha256": (
            protocol.BASE_AUDIT_SHA256
        ),
        "python_re_universal_oracle_postfinal_no_delegation_audit_sha256": (
            protocol.STRICT_AUDIT_SHA256
        ),
    }


def require_v6_audit_binding(
    document: object,
    *,
    reference: dict | None = None,
) -> None:
    _INHERITED_REQUIRE_AUDIT(document, reference=reference)
    require(isinstance(document, dict), "the actual public V6 V2 audits are missing")
    for key, expected in _expected_audit_fields().items():
        require(
            document.get(key) == expected
            and type(document.get(key)) is type(expected),
            f"the actual public V6 current-source audit changed {key}",
        )


def require_v6_universal_oracle(
    document: object,
    *,
    reference: dict | None = None,
) -> None:
    _INHERITED_REQUIRE_UNIVERSAL(document, reference=reference)
    require(
        isinstance(document, dict),
        "the complete public V6 stage-04 Python correctness proof is missing",
    )
    for key, expected in _expected_universal_fields().items():
        require(
            document.get(key) == expected
            and type(document.get(key)) is type(expected),
            f"the complete public V6 stage-04 Python proof changed {key}",
        )


def require_v6_correctness_artifacts(
    document: object,
    *,
    reference: dict | None = None,
) -> None:
    _INHERITED_REQUIRE_ARTIFACTS(document, reference=reference)
    require(isinstance(document, dict), "public V6 correctness proofs are missing")
    artifacts = document["stage05_correctness_artifacts"]
    expected = _mixed_artifact_paths()
    observed = {item["role"]: item["path"] for item in artifacts}
    require(
        observed == expected
        and sum(role.startswith("rust-") for role in observed) == 4
        and sum(
            role.startswith("vm-") or role.startswith("zig-")
            for role in observed
        )
        == 8,
        "public V6 substituted a fresh Rust or preserved C/Zig proof",
    )


def require_v6_worker_topology(
    document: object,
    *,
    reference: dict | None = None,
    measured: bool,
) -> None:
    _INHERITED_REQUIRE_WORKERS(
        document,
        reference=reference,
        measured=measured,
    )
    require(
        isinstance(document, dict),
        "public V6 omitted its independently audited guarded worker",
    )
    for key, expected in _expected_worker_fields().items():
        require(
            document.get(key) == expected
            and type(document.get(key)) is type(expected),
            f"public V6 substituted its immutable guarded worker: {key}",
        )
        if reference is not None:
            require(
                document[key] == reference.get(key),
                f"the independently replayed V6 guarded worker changed {key}",
            )


def require_v6_predecessor(document: object) -> None:
    require(isinstance(document, dict), "the frozen V6 predecessor is missing")
    expected: dict[str, Any] = {
        "source_public_v5_runner_path": _relative(
            protocol.FROZEN_V5_SOURCE_PATH
        ),
        "source_public_v5_runner_sha256": (
            protocol.FROZEN_V5_SOURCE_SHA256
        ),
        "source_public_v5_manifest_path": _relative(
            protocol.FROZEN_V5_MANIFEST_PATH
        ),
        "source_public_v5_manifest_sha256": (
            protocol.FROZEN_V5_MANIFEST_SHA256
        ),
        "public_v5_case_population_preserved": True,
        "public_v5_case_population_count": 8_192,
        "public_v5_workload_category_count": 260,
        "private_worker_wire_format": (
            protocol.frozen_v5.PRIVATE_WORKER_WIRE_FORMAT
        ),
        "private_worker_wire_ensure_ascii": True,
    }
    for key, value in expected.items():
        require(
            document.get(key) == value
            and type(document.get(key)) is type(value),
            f"public V6 changed its exact public V5 predecessor: {key}",
        )
    require(
        document.get("cases") == 8_192
        and document.get("all_bounded_workload_categories") == 260
        and document.get("public_operations")
        == protocol.FROZEN_PUBLIC_OPERATION_COUNTS
        and isinstance(document.get("categories"), dict)
        and len(document["categories"]) == 260
        and document.get("holdout_accessed") is False
        and document.get("held_out_cases_generated") == 0
        and document.get("held_out_records_deserialized") == 0
        and document.get("historical_performance_read") is False
        and document.get("timing_performed") is False,
        "public V6 changed its 8,192 cases, weights, category or holdout rules",
    )


def check_v6_manifest(
    document: object,
    *,
    manifest_sha256: str,
) -> dict[str, dict]:
    selected = _INHERITED_CHECK_MANIFEST(
        document,
        manifest_sha256=manifest_sha256,
    )
    require_v6_predecessor(document)
    return selected


@contextmanager
def v6_renderer(*, strict_bindings: bool = True) -> Iterator[None]:
    """Reversibly source-bind both immutable inherited renderers to V6."""

    v4.original.require_candidate_free()
    verify_inherited_renderer_sources()
    require_protocol_contract()
    wrapper_updates: dict[str, Any] = {
        "__file__": str(Path(__file__).resolve()),
        "PREFIX": PREFIX,
        "PUBLIC_ROOT": PUBLIC_ROOT,
        "EVIDENCE": EVIDENCE,
        "MANIFEST": MANIFEST,
        "SUMMARY": SUMMARY,
        "INTEGRITY": INTEGRITY,
        "PUBLIC_RAW": PUBLIC_RAW,
        "PLAN_SCHEMA": PLAN_SCHEMA,
        "PLAN_POSTFINAL_SCHEMA": PLAN_POSTFINAL_SCHEMA,
        "SUMMARY_SCHEMA": SUMMARY_SCHEMA,
        "SUMMARY_POSTFINAL_SCHEMA": SUMMARY_POSTFINAL_SCHEMA,
        "INTEGRITY_SCHEMA": INTEGRITY_SCHEMA,
    }
    core_updates: dict[str, Any] = {
        "NO_DELEGATION_AUDIT_PATH": str(
            protocol.STRICT_AUDIT_PATH.resolve()
        ),
        "NO_DELEGATION_SOURCE_PATH": str(
            protocol.STRICT_AUDIT_SOURCE_PATH.resolve()
        ),
        "NO_DELEGATION_SCHEMA": protocol.STRICT_AUDIT_SCHEMA,
        "NO_DELEGATION_CONTROL_COUNT": protocol.STRICT_AUDIT_CONTROL_COUNT,
        "ORIGINAL_AUDIT_SOURCE_PATH": str(
            protocol.BASE_AUDIT_SOURCE_PATH.resolve()
        ),
        "UNIVERSAL_ORACLE_SOURCE_PATH": str(
            protocol.UNIVERSAL_V4_SOURCE_PATH.resolve()
        ),
        "UNIVERSAL_ORACLE_SOURCE_SHA256": (
            protocol.UNIVERSAL_V4_SOURCE_SHA256
        ),
        "UNIVERSAL_ORACLE_REPORT_PATH": str(
            protocol.UNIVERSAL_V4_REPORT_PATH.resolve()
        ),
        "EDGE_PROOF_PATHS": _mixed_edge_paths(),
        "STAGE05_ARTIFACT_PATHS": _mixed_artifact_paths(),
    }
    if strict_bindings:
        core_updates.update(
            {
                "require_audit_binding": require_v6_audit_binding,
                "require_universal_oracle": require_v6_universal_oracle,
                "require_stage05_artifacts": require_v6_correctness_artifacts,
                "require_worker_topology": require_v6_worker_topology,
                "check_v4_manifest": check_v6_manifest,
            }
        )
    saved_wrapper = {
        name: getattr(inherited, name) for name in wrapper_updates
    }
    saved_core = {name: getattr(v4, name) for name in core_updates}
    try:
        for name, value in core_updates.items():
            setattr(v4, name, value)
        for name, value in wrapper_updates.items():
            setattr(inherited, name, value)
        yield
    finally:
        for name, value in saved_wrapper.items():
            setattr(inherited, name, value)
        for name, value in saved_core.items():
            setattr(v4, name, value)
        v4.original.require_candidate_free()


def require_v6_render_inputs(
    *,
    summary: Path,
    integrity: Path,
    manifest: Path,
    manifest_sha256: str,
    runner_sha256: str,
    output_dir: Path,
) -> None:
    for label, supplied, expected in (
        ("summary", summary, SUMMARY),
        ("integrity", integrity, INTEGRITY),
        ("manifest", manifest, MANIFEST),
        ("output evidence directory", output_dir, EVIDENCE),
    ):
        require(
            isinstance(supplied, Path)
            and supplied.resolve() == expected.resolve(),
            f"the public V6 {label} escaped its exact frozen V6 path",
        )
    require(
        valid_sha256(manifest_sha256),
        "an externally supplied genuine V6 --manifest-sha256 is required",
    )
    require(
        valid_sha256(runner_sha256),
        "an externally supplied genuine V6 --runner-sha256 is required",
    )


def reject_synthetic(label: str, action: Callable[[], Any]) -> None:
    try:
        action()
    except (
        KeyError,
        OSError,
        OverflowError,
        RuntimeError,
        TypeError,
        ValueError,
    ):
        return
    raise ValueError(f"the public V6 synthetic controls accepted {label}")


def _synthetic_v6_documents() -> tuple[dict, dict, dict]:
    """Generate and cross-bind all V6 audit evidence exclusively in memory."""

    manifest, summary, integrity = v4.synthetic_documents()
    common = {
        **_expected_audit_fields(),
        **_expected_worker_fields(),
        **_expected_universal_fields(),
    }
    for document in (manifest, summary, integrity):
        document.update(common)
    manifest.update(
        {
            "source_public_v5_runner_path": _relative(
                protocol.FROZEN_V5_SOURCE_PATH
            ),
            "source_public_v5_runner_sha256": (
                protocol.FROZEN_V5_SOURCE_SHA256
            ),
            "source_public_v5_manifest_path": _relative(
                protocol.FROZEN_V5_MANIFEST_PATH
            ),
            "source_public_v5_manifest_sha256": (
                protocol.FROZEN_V5_MANIFEST_SHA256
            ),
            "public_v5_case_population_preserved": True,
            "public_v5_case_population_count": 8_192,
            "public_v5_workload_category_count": 260,
            "private_worker_wire_format": (
                protocol.frozen_v5.PRIVATE_WORKER_WIRE_FORMAT
            ),
            "private_worker_wire_ensure_ascii": True,
            "historical_performance_read": False,
            "timing_performed": False,
        }
    )
    manifest_sha256 = v4.base.canonical_sha256(manifest)
    summary["manifest_sha256"] = manifest_sha256
    summary["runner_sha256"] = manifest["runner_sha256"]
    summary_sha256 = v4.base.canonical_sha256(summary)
    integrity["manifest_sha256"] = manifest_sha256
    integrity["summary_sha256"] = summary_sha256
    integrity["runner_sha256"] = manifest["runner_sha256"]
    return manifest, summary, integrity


def _changed_artifacts(
    document: dict,
    role: str,
    replacement: str,
) -> list[dict]:
    artifacts = copy.deepcopy(document["stage05_correctness_artifacts"])
    for artifact in artifacts:
        if artifact.get("role") == role:
            artifact["path"] = replacement
            return artifacts
    raise ValueError(f"synthetic public correctness role is missing: {role}")


def self_test() -> dict[str, Any]:
    """Test only in-memory charts and source pins; never read observations."""

    v4.original.require_candidate_free()
    additional_rejections = 0

    with v6_renderer(strict_bindings=False):
        inherited_report = inherited.self_test()
        require(
            inherited_report.get("result") == "PASS"
            and inherited_report.get("protocol_version") == PREFIX
            and inherited_report.get("charts") == 6
            and inherited_report.get("synthetic_cases_per_module") == 8_192
            and inherited_report.get("synthetic_workload_categories") == 260
            and inherited_report.get("stage05_independent_correctness_artifacts")
            == 12
            and type(inherited_report.get("adversarial_rejections")) is int
            and inherited_report["adversarial_rejections"] >= 90,
            "an inherited source-bound public V5/V4 chart control was removed",
        )

    fake_manifest_sha256 = hashlib.sha256(
        b"synthetic-only-v6-public-chart-manifest-pin"
    ).hexdigest()
    fake_runner_sha256 = hashlib.sha256(
        b"synthetic-only-v6-public-chart-runner-pin"
    ).hexdigest()

    with v6_renderer():
        with v4.v4_renderer(
            manifest_sha256=fake_manifest_sha256,
            runner_sha256=fake_runner_sha256,
            public_operations=dict(protocol.FROZEN_PUBLIC_OPERATION_COUNTS),
        ):
            manifest, summary, integrity = _synthetic_v6_documents()
            manifest_sha256 = v4.base.canonical_sha256(manifest)
            summary_sha256 = v4.base.canonical_sha256(summary)
            selected = v4.check_v4_manifest(
                manifest,
                manifest_sha256=manifest_sha256,
            )
            results = v4.check_v4_summary(
                summary,
                manifest=manifest,
                selected_cases=selected,
                summary_sha256=summary_sha256,
                manifest_sha256=manifest_sha256,
            )
            v4.check_v4_integrity(
                integrity,
                results,
                manifest=manifest,
                integrity_sha256=v4.base.canonical_sha256(integrity),
            )
            require(
                tuple(v4.build_v4_charts(results)) == v4.SUFFIXES
                and len(v4.SUFFIXES) == 6,
                "a required public V6 regression, memory, or ranking graph changed",
            )

            stale_rust = _relative(
                protocol._FROZEN_V5_STAGE_PATHS["rust-edge"]
            )
            stale_c = _relative(
                protocol._FROZEN_V5_STAGE_PATHS["vm-edge"]
            )
            document_poisons: tuple[tuple[str, str, str, Any], ...] = (
                ("stale V5 manifest version", "manifest", "protocol_version", V5_PREFIX),
                ("stale V5 exclusive slot", "manifest", "exclusive_slot", V5_PREFIX),
                ("stale V5 plan schema", "manifest", "postfinal_schema", "rebar-postfinal-public-practice-plan-v5"),
                ("changed V6 workload denominator", "manifest", "cases", 8_191),
                ("concealed V6 workload category", "manifest", "all_bounded_workload_categories", 259),
                ("changed V6 operation weights", "manifest", "public_operations", {**protocol.FROZEN_PUBLIC_OPERATION_COUNTS, "search": 1_056}),
                ("opened final holdout in plan", "manifest", "holdout_accessed", True),
                ("deserialized hidden records in plan", "manifest", "held_out_records_deserialized", 1),
                ("premature public timing in plan", "manifest", "timing_performed", True),
                ("changed V5 predecessor runner", "manifest", "source_public_v5_runner_sha256", "0" * 64),
                ("changed V5 predecessor manifest", "manifest", "source_public_v5_manifest_sha256", "0" * 64),
                ("substituted V5 predecessor source", "manifest", "source_public_v5_runner_path", "tools/foreign_runner.py"),
                ("unpreserved V5 case population", "manifest", "public_v5_case_population_preserved", False),
                ("changed V5 population denominator", "manifest", "public_v5_case_population_count", 8_191),
                ("changed V5 category denominator", "manifest", "public_v5_workload_category_count", 259),
                ("unsafe Unicode worker framing", "manifest", "private_worker_wire_ensure_ascii", False),
                ("changed V2 base audit", "manifest", "from_scratch_audit_sha256", "0" * 64),
                ("substituted V2 base audit source", "manifest", "from_scratch_audit_source_sha256", "0" * 64),
                ("changed V2 strict audit", "manifest", "postfinal_no_delegation_audit_sha256", "0" * 64),
                ("substituted V2 strict verifier", "manifest", "postfinal_no_delegation_audit_source_sha256", "0" * 64),
                ("accepted historical V1 as V2", "manifest", "postfinal_no_delegation_audit_schema", protocol.IMMUTABLE_WORKER_SCHEMA),
                ("removed V2 isolation control", "manifest", "postfinal_no_delegation_control_count", 31),
                ("changed immutable V1 worker", "manifest", "postfinal_guarded_worker_source_sha256", "0" * 64),
                ("changed immutable V1 worker proof", "manifest", "postfinal_guarded_worker_report_sha256", "0" * 64),
                ("changed immutable V1 worker schema", "manifest", "postfinal_guarded_worker_schema", protocol.STRICT_AUDIT_SCHEMA),
                ("substituted stage04 universal source", "manifest", "python_re_universal_oracle_source_sha256", "0" * 64),
                ("substituted stage04 universal report", "manifest", "python_re_universal_oracle_report_sha256", "0" * 64),
                ("concealed universal mismatch", "manifest", "python_re_universal_oracle_mismatches", 1),
                ("omitted universal candidate", "manifest", "python_re_universal_oracle_candidates", ["rust", "zig"]),
                ("stale Rust stage05 proof", "manifest", "stage05_correctness_artifacts", _changed_artifacts(manifest, "rust-edge", stale_rust)),
                ("cross-family Rust edge proof", "manifest", "stage05_correctness_artifacts", _changed_artifacts(manifest, "rust-edge", stale_c)),
                ("missing independent stage05 proof", "manifest", "stage05_correctness_artifacts", manifest["stage05_correctness_artifacts"][:-1]),
                ("stale V5 summary protocol", "summary", "protocol_version", V5_PREFIX),
                ("stale V5 summary schema", "summary", "postfinal_schema", "rebar-postfinal-public-practice-report-v5"),
                ("substituted summary runner", "summary", "runner_sha256", "0" * 64),
                ("substituted summary manifest", "summary", "manifest_sha256", "0" * 64),
                ("changed summary V2 base audit", "summary", "from_scratch_audit_sha256", "0" * 64),
                ("changed summary V2 strict audit", "summary", "postfinal_no_delegation_audit_sha256", "0" * 64),
                ("changed summary guarded worker", "summary", "postfinal_guarded_worker_source_sha256", "0" * 64),
                ("changed summary guarded-worker proof", "summary", "postfinal_guarded_worker_report_sha256", "0" * 64),
                ("changed summary universal report", "summary", "python_re_universal_oracle_report_sha256", "0" * 64),
                ("hidden actual public regression", "summary", "regressions", []),
                ("stale summary Rust proof", "summary", "stage05_correctness_artifacts", _changed_artifacts(summary, "rust-edge", stale_rust)),
                ("stale V5 integrity protocol", "integrity", "protocol_version", V5_PREFIX),
                ("stale V5 integrity schema", "integrity", "schema", "rebar-postfinal-public-practice-integrity-v5"),
                ("substituted integrity runner", "integrity", "runner_sha256", "0" * 64),
                ("substituted integrity manifest", "integrity", "manifest_sha256", "0" * 64),
                ("substituted integrity summary", "integrity", "summary_sha256", "0" * 64),
                ("changed integrity V2 base audit", "integrity", "from_scratch_audit_sha256", "0" * 64),
                ("changed integrity V2 strict audit", "integrity", "postfinal_no_delegation_audit_sha256", "0" * 64),
                ("changed integrity guarded worker", "integrity", "postfinal_guarded_worker_source_sha256", "0" * 64),
                ("changed integrity guarded-worker proof", "integrity", "postfinal_guarded_worker_report_sha256", "0" * 64),
                ("changed integrity universal report", "integrity", "python_re_universal_oracle_report_sha256", "0" * 64),
                ("invented native allocation evidence", "integrity", "memory_limitation", "all native allocations are exactly measured"),
                ("removed integrity correctness proofs", "integrity", "stage05_correctness_artifacts", []),
            )
            documents = {
                "manifest": manifest,
                "summary": summary,
                "integrity": integrity,
            }
            for label, kind, key, value in document_poisons:
                changed = copy.deepcopy(documents[kind])
                changed[key] = value
                if kind == "manifest":
                    action: Callable[[], Any] = (
                        lambda changed=changed: v4.check_v4_manifest(
                            changed,
                            manifest_sha256=v4.base.canonical_sha256(changed),
                        )
                    )
                elif kind == "summary":
                    action = lambda changed=changed: v4.check_v4_summary(
                        changed,
                        manifest=manifest,
                        selected_cases=selected,
                        summary_sha256=v4.base.canonical_sha256(changed),
                        manifest_sha256=manifest_sha256,
                    )
                else:
                    action = lambda changed=changed: v4.check_v4_integrity(
                        changed,
                        results,
                        manifest=manifest,
                        integrity_sha256=v4.base.canonical_sha256(changed),
                    )
                reject_synthetic(label, action)
                additional_rejections += 1

    genuine_inputs: dict[str, Any] = {
        "summary": SUMMARY,
        "integrity": INTEGRITY,
        "manifest": MANIFEST,
        "manifest_sha256": fake_manifest_sha256,
        "runner_sha256": fake_runner_sha256,
        "output_dir": EVIDENCE,
    }
    require_v6_render_inputs(**genuine_inputs)
    for label, key, value in (
        ("stale V5 summary path", "summary", V5_SUMMARY),
        ("stale V5 integrity path", "integrity", V5_INTEGRITY),
        ("stale V5 manifest path", "manifest", V5_MANIFEST),
        ("stale V5 output directory", "output_dir", V5_EVIDENCE),
        ("missing explicit V6 manifest hash", "manifest_sha256", ""),
        ("missing explicit V6 runner hash", "runner_sha256", ""),
        ("uppercase V6 manifest hash", "manifest_sha256", fake_manifest_sha256.upper()),
        ("uppercase V6 runner hash", "runner_sha256", fake_runner_sha256.upper()),
    ):
        changed = {**genuine_inputs, key: value}
        reject_synthetic(
            label,
            lambda changed=changed: require_v6_render_inputs(**changed),
        )
        additional_rejections += 1

    for label, action in (
        (
            "substituted inherited V5 renderer path",
            lambda: require_inherited_source_binding(
                V4_RENDERER_PATH,
                V5_RENDERER_SHA256,
                expected_path=V5_RENDERER_PATH,
                expected_sha256=V5_RENDERER_SHA256,
            ),
        ),
        (
            "substituted inherited V5 renderer fingerprint",
            lambda: require_inherited_source_binding(
                V5_RENDERER_PATH,
                "0" * 64,
                expected_path=V5_RENDERER_PATH,
                expected_sha256=V5_RENDERER_SHA256,
            ),
        ),
        (
            "substituted inherited V4 renderer path",
            lambda: require_inherited_source_binding(
                V5_RENDERER_PATH,
                V4_RENDERER_SHA256,
                expected_path=V4_RENDERER_PATH,
                expected_sha256=V4_RENDERER_SHA256,
            ),
        ),
        (
            "substituted inherited V4 renderer fingerprint",
            lambda: require_inherited_source_binding(
                V4_RENDERER_PATH,
                "0" * 64,
                expected_path=V4_RENDERER_PATH,
                expected_sha256=V4_RENDERER_SHA256,
            ),
        ),
        (
            "substituted V6 runner path",
            lambda: require_runner_source_binding(
                V5_RENDERER_PATH,
                fake_runner_sha256,
                fake_runner_sha256,
            ),
        ),
        (
            "substituted V6 runner source fingerprint",
            lambda: require_runner_source_binding(
                RUNNER_PATH,
                "0" * 64,
                fake_runner_sha256,
            ),
        ),
    ):
        reject_synthetic(label, action)
        additional_rejections += 1

    require_runner_source_binding(
        RUNNER_PATH,
        fake_runner_sha256,
        fake_runner_sha256,
    )
    v4.original.require_candidate_free()
    return {
        **inherited_report,
        "result": "PASS",
        "mode": (
            "candidate-free in-memory V6 poison controls; only pinned V5 "
            "and V4 chart sources are verified; no measured evidence read, "
            "no workers started, and no outputs written"
        ),
        "protocol_version": PREFIX,
        "inherited_v5_renderer_source_path": str(V5_RENDERER_PATH),
        "inherited_v5_renderer_source_sha256": V5_RENDERER_SHA256,
        "inherited_v4_renderer_source_path": str(V4_RENDERER_PATH),
        "inherited_v4_renderer_source_sha256": V4_RENDERER_SHA256,
        "inherited_adversarial_rejections": inherited_report[
            "adversarial_rejections"
        ],
        "v6_adversarial_rejections": additional_rejections,
        "adversarial_rejections": (
            inherited_report["adversarial_rejections"] + additional_rejections
        ),
        "charts": len(v4.SUFFIXES),
        "synthetic_cases_per_module": 8_192,
        "synthetic_workload_categories": 260,
        "mixed_correctness_artifact_count": 12,
        "fresh_rust_correctness_artifact_count": 4,
        "preserved_peer_correctness_artifact_count": 8,
        "actual_v2_base_audit_bound": True,
        "actual_v2_strict_audit_bound": True,
        "immutable_v1_guarded_worker_bound": True,
        "stage04_universal_oracle_bound": True,
        "candidate_imported": False,
        "worker_processes_started": 0,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "benchmark_or_timing_executed": False,
        "timing_performed": False,
        "manifest_binding": (
            "explicit --manifest-sha256 and --runner-sha256 required; "
            "actual source and independently replayed evidence cross-bound"
        ),
    }


def render(
    *,
    summary: Path,
    integrity: Path,
    manifest: Path,
    manifest_sha256: str,
    runner_sha256: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Render actual regressions only after every independent V6 proof passes."""

    v4.original.require_candidate_free()
    require_v6_render_inputs(
        summary=summary,
        integrity=integrity,
        manifest=manifest,
        manifest_sha256=manifest_sha256,
        runner_sha256=runner_sha256,
        output_dir=output_dir,
    )
    runner_source = Path(protocol.__file__).resolve()
    require_runner_source_binding(
        runner_source,
        hashlib.sha256(runner_source.read_bytes()).hexdigest(),
        runner_sha256,
    )
    with v6_renderer():
        report = inherited.render(
            summary=summary,
            integrity=integrity,
            manifest=manifest,
            manifest_sha256=manifest_sha256,
            runner_sha256=runner_sha256,
            output_dir=output_dir,
        )
    v4.original.require_candidate_free()
    require(
        report.get("result") == "PASS"
        and report.get("protocol_version") == PREFIX
        and report.get("manifest_sha256") == manifest_sha256
        and report.get("runner_sha256") == runner_sha256
        and report.get("public_cases_per_module") == 8_192
        and report.get("stage05_independent_correctness_artifacts") == 12
        and report.get("postfinal_no_delegation_control_count") == 32
        and report.get("controller_candidate_imported") is False
        and isinstance(report.get("charts"), list)
        and len(report["charts"]) == len(v4.SUFFIXES) == 6,
        "public V6 charts changed their real evidence, denominators or proofs",
    )
    return {
        **report,
        "inherited_v5_renderer_source_path": str(V5_RENDERER_PATH),
        "inherited_v5_renderer_source_sha256": V5_RENDERER_SHA256,
        "inherited_v4_renderer_source_path": str(V4_RENDERER_PATH),
        "inherited_v4_renderer_source_sha256": V4_RENDERER_SHA256,
        "mixed_correctness_artifact_count": 12,
        "fresh_rust_correctness_artifact_count": 4,
        "preserved_peer_correctness_artifact_count": 8,
        "actual_v2_base_audit_sha256": protocol.BASE_AUDIT_SHA256,
        "actual_v2_strict_audit_sha256": protocol.STRICT_AUDIT_SHA256,
        "immutable_v1_guarded_worker_source_sha256": (
            protocol.IMMUTABLE_WORKER_SOURCE_SHA256
        ),
        "immutable_v1_guarded_worker_report_sha256": (
            protocol.IMMUTABLE_WORKER_REPORT_SHA256
        ),
        "stage04_universal_oracle_report_sha256": (
            protocol.UNIVERSAL_V4_REPORT_SHA256
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render six independently replayed, source-bound public V6 "
            "charts without importing candidates or opening a holdout."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run only candidate-free, in-memory V6 poison controls",
    )
    parser.add_argument("--summary", type=Path, help="exact V6 public summary")
    parser.add_argument(
        "--integrity",
        type=Path,
        help="exact independently replayed V6 integrity",
    )
    parser.add_argument("--manifest", type=Path, help="exact frozen V6 manifest")
    parser.add_argument(
        "--manifest-sha256",
        help="required independently supplied genuine V6 manifest SHA-256",
    )
    parser.add_argument(
        "--runner-sha256",
        help="required independently supplied genuine V6 runner SHA-256",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="exact additive public-V6 evidence directory",
    )
    args = parser.parse_args(argv)
    supplied = (
        args.summary,
        args.integrity,
        args.manifest,
        args.manifest_sha256,
        args.runner_sha256,
        args.output_dir,
    )
    if args.self_test:
        if any(value is not None for value in supplied):
            parser.error(
                "synthetic controls cannot read measured evidence or write charts"
            )
    elif any(value is None for value in supplied):
        parser.error(
            "rendering requires explicit --summary, --integrity, --manifest, "
            "--manifest-sha256, --runner-sha256, and --output-dir"
        )
    elif not valid_sha256(args.manifest_sha256):
        parser.error("--manifest-sha256 must be a lowercase 64-character SHA-256")
    elif not valid_sha256(args.runner_sha256):
        parser.error("--runner-sha256 must be a lowercase 64-character SHA-256")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = (
            self_test()
            if args.self_test
            else render(
                summary=args.summary,
                integrity=args.integrity,
                manifest=args.manifest,
                manifest_sha256=args.manifest_sha256,
                runner_sha256=args.runner_sha256,
                output_dir=args.output_dir,
            )
        )
    except (
        KeyError,
        OSError,
        OverflowError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        print(f"source-bound public V6 chart rendering rejected: {error}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
