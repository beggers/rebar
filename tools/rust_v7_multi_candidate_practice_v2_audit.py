#!/usr/bin/env python3
"""Replay the single fully qualified, fused-Rust four-way public practice run.

The original v1 auditor and historical evidence are immutable.  This narrowly
bound v2 verifier reuses only their independently tested, candidate-free raw
and bootstrap mathematics.  It never imports a candidate, runs a benchmark, or
accesses the final holdout.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

from tools import rust_v7_multi_candidate_practice_audit as original


ROOT = original.ROOT
EVIDENCE = original.EVIDENCE
SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v2"
SLOT = "three-qualified-engines-fused-vectorcall-v2"
PREFIX = "three-qualified-engines-public-practice-v2"
RAW_PATH = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE / f"{PREFIX}-summary.json"
OUTPUT_PATH = EVIDENCE / f"{PREFIX}-integrity.json"
V1_INTEGRITY_PATH = original.OUTPUT_PATH
CAMPAIGN_PATH = ROOT / "candidates/evidence/rust-v8-rust-fused-vectorcall-sealed-campaign.json"
RUST_EDGE_PATH = ROOT / "candidates/evidence/rust-v7-edge-oracle-rust-fused-vectorcall.json.gz"
C_EDGE_PATH = ROOT / "candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-19.json.gz"
ZIG_EDGE_PATH = ROOT / "candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-11.json.gz"

V1_AUDITOR_SHA256 = "bc093f114fe15833cab8f7c8d59bd1970345b6ddb47bc33349854be1af7f0ded"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V1_CANONICAL_AUDIT_SHA256 = "94b00886ab790d096f243775540d2590c33ea7a316d9a6098cd40d52b19f6f09"
V2_AUDIT_SHA256 = "ee98f2098223585e4cc3d484d97d36a33c358ccdfd133e6db78c8dad89d1a355"
V2_SUMMARY_SHA256 = "db3cc7f4704df7b0a6b1283818d0dfdf96947d83d44752bf633a640a3e721cab"
V2_COMPRESSED_RAW_SHA256 = "81b1a8c99f8f460539d9b212127d2ba9c76720987d4dde49c5c0186f31c05e76"
V2_RAW_SHA256 = "3fd49183c18e31c3319c7f8df31ea1cf829a0e70d8be593ee89b349ffdd36718"
FUSED_CAMPAIGN_SHA256 = "d54d11835e6fd1d4b6bf81d6bdd9f72d219265fbd48142cb923274bf5b6f681e"
FUSED_EDGE_COMPRESSED_SHA256 = "e01962993a0535934a18e170f78721fd796d03b43145c499a86510b264f7288f"
FUSED_EDGE_PAYLOAD_SHA256 = "90fbd41d862cba6b926929dc99c53c4e981ed4da7a73d4652b20d3013d544ad4"
FUSED_RUST_SOURCE_SHA256 = "88a8a6b086061da69022a978eba3a0f0317a378f0a758c44ec84fb9c1c0b3c65"
FUSED_RUST_BRIDGE_SHA256 = "8a413cce5dde126fbcdeba269a4ee766f20ba80396db460a160864df4d8c6434"
OLD_RUST_SOURCE_SHA256 = "cfe81e9dc80bfbfadc34907918fe00fdbb2e3c4c6d8f3fd4efdff0e8783aa291"
OLD_RUST_BRIDGE_SHA256 = "bacce4e941dfa83a03eb87131c0ee8fe91feaa31ad02d97119a5c6bdce956e71"
EXPECTED_REGRESSIONS = 401
UNCHANGED_REFERENCE_CANDIDATES = [
    "re", "candidates.vm_candidate", "candidates.zig_candidate"
]


require = original.require
AuditError = original.AuditError


def validate_version_identity(
    summary: dict,
    plan: dict,
    profile: original.Profile,
    raw_path: Path,
) -> None:
    original.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == SLOT, "the optimized candidates were not measured in their one authorized v2 slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "the v2 summary points at different raw measurements")
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "the optimized public practice result was represented as final performance",
    )


def validate_historical_continuity(
    historical: dict,
    sources: dict[str, str],
    native: dict[str, str],
    measured: dict[str, str],
) -> None:
    require(historical.get("schema") == original.SCHEMA, "the preserved v1 experiment has a different schema")
    require(historical.get("result") == "PASS" and historical.get("failed") == 0, "the preserved v1 experiment did not independently pass")
    require(historical.get("holdout_accessed") is False and historical.get("timing_performed") is False, "the historical baseline accessed final cases or performed timing during verification")
    require(historical.get("module_order") == list(original.MODULES), "the historical comparison measured different engine families")
    require(historical.get("cases_per_candidate") == original.EXPECTED_CASES, "the historical comparison used different frozen cases")
    require(historical.get("trials_per_module_case") == original.EXPECTED_TRIALS, "the historical comparison used different paired trials")
    require(historical.get("bootstrap_draws") == original.EXPECTED_BOOTSTRAPS, "the historical comparison used different confidence draws")
    require(historical.get("frozen_plan_sha256") == original.EXPECTED_PLAN_SHA256, "the historical comparison used a different frozen practice plan")
    require(historical.get("source_sha256") == V1_AUDITOR_SHA256, "the immutable v1 auditor provenance changed")
    require(historical.get("from_scratch_audit_sha256") == V1_CANONICAL_AUDIT_SHA256, "the preserved historical independence audit changed")
    require(historical.get("strict_regressions") == original.EXPECTED_REGRESSIONS, "the historical experiment's actual 426 losses changed")
    old_sources = historical.get("qualified_source_fingerprints")
    old_native = historical.get("native_elf_fingerprints")
    old_measured = historical.get("candidate_binary_sha256_before")
    require(isinstance(old_sources, dict), "historical qualified source fingerprints are missing")
    require(isinstance(old_native, dict), "historical mapped-library fingerprints are missing")
    require(isinstance(old_measured, dict), "historical Python and engine fingerprints are missing")
    require(historical.get("candidate_binary_sha256_after") == old_measured, "the historical engines changed during paired measurement")

    unchanged_sources = (
        "candidates/_vm_native.c",
        "candidates/vm_candidate.py",
        "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
        "candidates/zig_candidate.py",
    )
    for path in unchanged_sources:
        require(sources.get(path) == old_sources.get(path), f"the reference C or Zig source changed: {path}")
    unchanged_roles = (
        "re:module",
        "candidates.vm_candidate:module",
        "candidates.vm_candidate:native-engine",
        "candidates.zig_candidate:module",
        "candidates.zig_candidate:native-bridge",
        "candidates.zig_candidate:native-engine",
    )
    for role in unchanged_roles:
        require(measured.get(role) == old_measured.get(role), f"the baseline, C, or Zig reference changed: {role}")
        if role in old_native:
            require(native.get(role) == old_native.get(role), f"a reference native-library mapping changed: {role}")

    require(old_sources.get("candidates/rust/py_bridge.c") == OLD_RUST_SOURCE_SHA256, "the recorded original Rust source is not v1")
    require(old_native.get("candidates.rust_candidate:native-bridge") == OLD_RUST_BRIDGE_SHA256, "the recorded original Rust binary is not v1")
    require(sources.get("candidates/rust/py_bridge.c") == FUSED_RUST_SOURCE_SHA256, "the fused Rust source does not match its qualified experiment")
    require(native.get("candidates.rust_candidate:native-bridge") == FUSED_RUST_BRIDGE_SHA256, "the fused Rust binary does not match its qualified experiment")
    require(FUSED_RUST_SOURCE_SHA256 != OLD_RUST_SOURCE_SHA256, "the v2 Rust source did not actually change")
    require(FUSED_RUST_BRIDGE_SHA256 != OLD_RUST_BRIDGE_SHA256, "the v2 Rust native bridge did not actually change")


def artifact_fingerprints(artifacts: object, module: str) -> dict[str, dict[str, str]]:
    require(isinstance(artifacts, list), f"{module} correctness artifacts are missing")
    results: dict[str, dict[str, str]] = {}
    for entry in artifacts:
        require(isinstance(entry, dict) and set(entry) == {"role", "path", "sha256"}, f"{module} correctness-artifact fields changed")
        role = entry.get("role")
        require(isinstance(role, str) and role not in results, f"{module} correctness artifact is duplicated")
        path = original.checked_production_path(entry.get("path"), f"{module} correctness artifact")
        digest = entry.get("sha256")
        require(original.sha256_file(path) == digest, f"{module} correctness-qualified production source changed")
        results[role] = {"path": original.display_path(path), "sha256": digest}
    return results


def validate_v2_edges(summary: dict, measured: dict[str, str]) -> list[dict]:
    require(
        original.sha256_file(original.EDGE_SOURCE_PATH) == original.EXPECTED_EDGE_SOURCE_SHA256,
        "the frozen independent correctness oracle changed",
    )
    stdlib, stdlib_digest = original.read_edge(
        original.STDLIB_EDGE_PATH, "pinned Python correctness report"
    )
    original.validate_edge_document(stdlib, "re")
    require(stdlib_digest == original.EXPECTED_STDLIB_EDGE_SHA256, "the pinned Python correctness proof changed")
    require(
        original.sha256_file(RUST_EDGE_PATH) == FUSED_EDGE_COMPRESSED_SHA256,
        "the optimized Rust edge proof is not the qualified fused-vectorcall run",
    )
    references = summary.get("verified_edge_oracles")
    require(
        isinstance(references, list) and len(references) == len(original.MODULES) - 1,
        "the v2 comparison omitted an independently qualified engine",
    )
    expected_paths = {
        "candidates.rust_candidate": RUST_EDGE_PATH,
        "candidates.vm_candidate": C_EDGE_PATH,
        "candidates.zig_candidate": ZIG_EDGE_PATH,
    }
    for module, reference in zip(original.MODULES[1:], references, strict=True):
        require(isinstance(reference, dict) and reference.get("module") == module, "a v2 correctness proof is reordered or substituted")
        path = expected_paths[module]
        require(reference.get("path") == str(path.resolve()), f"{module} used a different correctness report")
        require(reference.get("correctness_checks") == 223_198, f"{module} omitted frozen compatibility checks")
        require(reference.get("actual_sha256") == original.EXPECTED_EDGE_ANSWER_SHA256, f"{module} disagrees with frozen Python answers")
        require(reference.get("script_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, f"{module} changed the correctness oracle")
        require(reference.get("stdlib_baseline_sha256") == stdlib_digest, f"{module} changed the Python correctness baseline")
        report, digest = original.read_edge(path, f"{module} v2 correctness report")
        original.validate_edge_document(report, module)
        require(reference.get("report_sha256") == digest, f"{module} correctness proof changed after timing")
        if module == "candidates.rust_candidate":
            require(digest == FUSED_EDGE_PAYLOAD_SHA256, "the optimized Rust edge proof is not the exact fused-vectorcall experiment")
        artifacts = artifact_fingerprints(report.get("candidate_artifacts"), module)
        require(reference.get("candidate_artifacts") == artifacts, f"{module} measured different correctness-qualified sources")
        for role, artifact in artifacts.items():
            if role == "public-python":
                key = f"{module}:module"
            elif module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == artifact["sha256"], f"{module} timed an unqualified or substituted artifact")
    return references


def validate_full_campaign(campaign: dict, measured: dict[str, str]) -> None:
    require(campaign.get("schema") == "rebar-rust-campaign-gate-v1", "the fused Rust campaign format changed")
    require(campaign.get("candidate") == "candidates.rust_candidate", "the full campaign qualified a different engine")
    require(campaign.get("passed") is True, "the fused Rust full correctness campaign failed")
    require(campaign.get("holdout_accessed") is False, "the fused Rust correctness campaign accessed the final holdout")
    require(campaign.get("timing_performed") is False and campaign.get("performance") == "NOT MEASURED", "the correctness campaign performed a benchmark")
    require(campaign.get("required_correctness_step_count") == 22, "the fused Rust campaign changed its required correctness obligations")
    steps = campaign.get("steps")
    require(isinstance(steps, list) and len(steps) == 22, "the fused Rust campaign omitted a correctness stage")
    require(
        all(isinstance(step, dict) and step.get("passed") is True for step in steps),
        "the fused Rust campaign contains an unexplained failure",
    )
    require(campaign.get("pinned_cpython") == "3.14.6", "the fused Rust campaign changed Python baseline")
    require(campaign.get("python_executable") == str(original.PINNED_PYTHON), "the fused Rust campaign used a different Python executable")
    require(campaign.get("mode") == "sealed-practice-only", "the fused Rust campaign changed its isolation mode")
    edge = campaign.get("edge_oracle")
    require(isinstance(edge, dict), "the fused Rust full campaign omitted its correctness proof")
    require(edge.get("archive_sha256") == FUSED_EDGE_COMPRESSED_SHA256, "the fused Rust campaign references a substituted edge archive")
    require(edge.get("path") == str(RUST_EDGE_PATH.resolve()), "the fused Rust campaign references a different edge archive")
    require(edge.get("checks") == 223_198 and edge.get("failed") == 0, "the fused Rust campaign edge stage failed or dropped checks")
    require(edge.get("module") == "candidates.rust_candidate", "the fused Rust campaign qualified another candidate")
    campaign_artifacts = artifact_fingerprints(campaign.get("native_artifacts"), "candidates.rust_candidate")
    edge_artifacts = artifact_fingerprints(edge.get("candidate_artifacts"), "candidates.rust_candidate")
    require(campaign_artifacts == edge_artifacts, "the full campaign and Rust correctness report qualified different artifacts")
    for role, artifact in campaign_artifacts.items():
        key = "candidates.rust_candidate:module" if role == "public-python" else f"candidates.rust_candidate:{role}"
        require(measured.get(key) == artifact["sha256"], "the timed Rust implementation differs from its full 22-stage campaign")


def synthetic_history() -> tuple[dict, dict[str, str], dict[str, str], dict[str, str]]:
    unchanged_source_paths = (
        "candidates/_vm_native.c", "candidates/vm_candidate.py",
        "candidates/zig/mini_regex.zig", "candidates/zig/py_bridge.c",
        "candidates/zig_candidate.py",
    )
    old_sources = {
        path: hashlib.sha256(f"v2-synthetic-source:{path}".encode()).hexdigest()
        for path in unchanged_source_paths
    }
    old_sources["candidates/rust/py_bridge.c"] = OLD_RUST_SOURCE_SHA256
    current_sources = {**old_sources, "candidates/rust/py_bridge.c": FUSED_RUST_SOURCE_SHA256}
    old_measured = {
        role: hashlib.sha256(f"v2-synthetic-role:{role}".encode()).hexdigest()
        for role in (
            "re:module", "candidates.vm_candidate:module",
            "candidates.vm_candidate:native-engine", "candidates.zig_candidate:module",
            "candidates.zig_candidate:native-bridge", "candidates.zig_candidate:native-engine",
        )
    }
    old_native = {
        key: value for key, value in old_measured.items()
        if key.endswith(":native-engine") or key.endswith(":native-bridge")
    }
    old_native["candidates.rust_candidate:native-bridge"] = OLD_RUST_BRIDGE_SHA256
    current_native = {
        **old_native, "candidates.rust_candidate:native-bridge": FUSED_RUST_BRIDGE_SHA256
    }
    current_measured = {
        **old_measured, "candidates.rust_candidate:native-bridge": FUSED_RUST_BRIDGE_SHA256
    }
    historical = {
        "schema": original.SCHEMA, "result": "PASS", "failed": 0,
        "holdout_accessed": False, "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": V1_AUDITOR_SHA256,
        "from_scratch_audit_sha256": V1_CANONICAL_AUDIT_SHA256,
        "strict_regressions": original.EXPECTED_REGRESSIONS,
        "qualified_source_fingerprints": old_sources,
        "native_elf_fingerprints": old_native,
        "candidate_binary_sha256_before": old_measured,
        "candidate_binary_sha256_after": dict(old_measured),
    }
    return historical, current_sources, current_native, current_measured


def self_test() -> dict:
    legacy = original.self_test()
    require(legacy.get("result") == "PASS", "the frozen v1 synthetic replay no longer passes")
    original_controls = legacy.get("poisoned_controls")
    require(isinstance(original_controls, list) and len(original_controls) >= 28, "the immutable replay lost its synthetic corruption controls")
    plan, synthetic, _compressed, profile = original.synthetic_evidence()
    synthetic["exclusive_slot"] = SLOT
    synthetic["raw_path"] = str(RAW_PATH.resolve())
    synthetic["measurement"] = "balanced practice diagnostic only; not a holdout result or final speed claim"
    validate_version_identity(synthetic, plan, profile, RAW_PATH)
    previous, sources, native, measured = synthetic_history()
    validate_historical_continuity(previous, sources, native, measured)
    controls = [*original_controls]

    def rejected(name: str, function: object) -> None:
        try:
            function()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"synthetic v2 poison control was accepted: {name}")

    def version_poison(key: str, value: object) -> None:
        document = copy.deepcopy(synthetic)
        document[key] = value
        validate_version_identity(document, plan, profile, RAW_PATH)

    def history_poison(which: str, key: str, value: object) -> None:
        old = copy.deepcopy(previous)
        current_sources = dict(sources)
        current_native = dict(native)
        current_measured = dict(measured)
        targets = {
            "history": old,
            "old-sources": old["qualified_source_fingerprints"],
            "old-native": old["native_elf_fingerprints"],
            "sources": current_sources,
            "native": current_native,
            "measured": current_measured,
        }
        targets[which][key] = value
        validate_historical_continuity(old, current_sources, current_native, current_measured)

    rejected("v1-exclusive-slot-cross-contamination", lambda: version_poison("exclusive_slot", original.EXPECTED_SLOT))
    rejected("wrong-v2-exclusive-slot", lambda: version_poison("exclusive_slot", PREFIX))
    rejected("v1-raw-path-cross-contamination", lambda: version_poison("raw_path", str(original.RAW_PATH.resolve())))
    rejected("practice-falsely-claimed-final", lambda: version_poison("measurement", "final holdout result"))
    rejected("substituted-v1-historical-schema", lambda: history_poison("history", "schema", SCHEMA))
    rejected("historical-426-regressions-hidden", lambda: history_poison("history", "strict_regressions", 425))
    rejected("substituted-historical-audit", lambda: history_poison("history", "from_scratch_audit_sha256", "0" * 64))
    rejected("substituted-original-rust-source", lambda: history_poison("old-sources", "candidates/rust/py_bridge.c", FUSED_RUST_SOURCE_SHA256))
    rejected("substituted-original-rust-native", lambda: history_poison("old-native", "candidates.rust_candidate:native-bridge", FUSED_RUST_BRIDGE_SHA256))
    rejected("fused-rust-source-not-actually-new", lambda: history_poison("sources", "candidates/rust/py_bridge.c", OLD_RUST_SOURCE_SHA256))
    rejected("fused-rust-native-not-actually-new", lambda: history_poison("native", "candidates.rust_candidate:native-bridge", OLD_RUST_BRIDGE_SHA256))
    rejected("unchanged-c-reference-source-substituted", lambda: history_poison("sources", "candidates/_vm_native.c", "0" * 64))
    rejected("unchanged-zig-reference-source-substituted", lambda: history_poison("sources", "candidates/zig/mini_regex.zig", "0" * 64))
    rejected("unchanged-python-baseline-substituted", lambda: history_poison("measured", "re:module", "0" * 64))
    rejected("unchanged-c-reference-native-substituted", lambda: history_poison("native", "candidates.vm_candidate:native-engine", "0" * 64))
    rejected("unchanged-zig-reference-native-substituted", lambda: history_poison("native", "candidates.zig_candidate:native-engine", "0" * 64))
    require(len(controls) >= 44, "the v2 verifier omitted required original or version-isolation controls")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS",
        "synthetic_only": True, "holdout_accessed": False,
        "timing_performed": False, "original_poisoned_control_count": len(original_controls),
        "poisoned_control_count": len(controls), "poisoned_controls": controls,
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "unchanged_reference_candidates": UNCHANGED_REFERENCE_CANDIDATES,
        "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    require(
        platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6),
        "verification requires pinned CPython 3.14.6",
    )
    require(Path(sys.executable).resolve() == original.PINNED_PYTHON.resolve(), "verification requires the exact frozen Python executable")
    require(raw_path.resolve() == RAW_PATH.resolve(), "v2 cannot substitute its unique recorded raw practice observations")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "v2 cannot substitute its unique recorded practice summary")
    require(audit_path.resolve() == original.AUDIT_PATH.resolve(), "v2 cannot substitute its current canonical independence audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "v2 cannot overwrite or redirect any historical evidence")
    require(not output_path.exists(), "the unique v2 public practice integrity evidence already exists")
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the independent verifier imported a candidate")
    require(
        original.sha256_file(Path(original.__file__).resolve()) == V1_AUDITOR_SHA256,
        "the immutable v1 raw-replay and bootstrap verifier changed",
    )

    profile = original.Profile()
    plan = original.read_json(
        original.PLAN_PATH, "immutable 624-case public practice plan", original.EXPECTED_PLAN_SHA256
    )
    require(plan.get("expected_sha256") == original.EXPECTED_FROZEN_ANSWER_SHA256, "frozen public Python answers changed")
    original.validate_plan(plan, profile)
    summary = original.read_json(
        summary_path, "exact one-shot fused-vectorcall public practice summary", V2_SUMMARY_SHA256
    )
    validate_version_identity(summary, plan, profile, raw_path)
    require(summary.get("compressed_raw_sha256") == V2_COMPRESSED_RAW_SHA256, "the one-shot v2 compressed measurements changed")
    require(summary.get("raw_sha256") == V2_RAW_SHA256, "the one-shot v2 decompressed measurements changed")
    require(original.sha256_file(raw_path) == V2_COMPRESSED_RAW_SHA256, "the exact v2 compressed raw measurements changed")

    audit = original.read_json(audit_path, "fused-Rust canonical from-scratch audit", V2_AUDIT_SHA256)
    sources, native = original.validate_independence(audit)
    measured = original.validate_measured_fingerprints(summary, sources, native)
    previous = original.read_json(
        V1_INTEGRITY_PATH, "immutable historical v1 four-way comparison", V1_INTEGRITY_SHA256
    )
    validate_historical_continuity(previous, sources, native, measured)
    edge_proofs = validate_v2_edges(summary, measured)
    campaign = original.read_json(
        CAMPAIGN_PATH, "complete optimized Rust 22-stage correctness campaign", FUSED_CAMPAIGN_SHA256
    )
    validate_full_campaign(campaign, measured)

    try:
        with raw_path.open("rb") as source:
            observations = original.read_observations(
                source, V2_COMPRESSED_RAW_SHA256, summary, plan, profile
            )
    except OSError as error:
        raise AuditError("cannot open the exact v2 public practice observations") from error
    results, rankings = original.recompute_results(plan, observations, profile)
    regressions = original.validate_results(summary, results, rankings, profile)
    require(len(regressions) == EXPECTED_REGRESSIONS, "the optimized run concealed or altered its 401 actual strict slowdowns")
    controls = self_test()
    require(not any(name in sys.modules for name in original.MODULES[1:]), "v2 verification imported a measured candidate")

    document = {
        "schema": SCHEMA,
        "result": "PASS",
        "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of one recorded four-way public practice run; not final or held-out performance",
        "exclusive_slot": SLOT,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "candidate_case_count": len(results),
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": original.EXPECTED_CORRECTNESS_CHECKS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regression_speedup_threshold": original.REGRESSION_THRESHOLD,
        "strict_regressions": len(regressions),
        "summary_sha256": V2_SUMMARY_SHA256,
        "compressed_raw_sha256": V2_COMPRESSED_RAW_SHA256,
        "raw_sha256": V2_RAW_SHA256,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": original.sha256_file(Path(__file__).resolve()),
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": V2_AUDIT_SHA256,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(original.MODULES) - 1,
        "verified_native_library_count": len(native),
        "full_correctness_campaign_sha256": FUSED_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "rust_optimization_verified": True,
        "unchanged_reference_candidates": UNCHANGED_REFERENCE_CANDIDATES,
        "qualified_source_fingerprints": sources,
        "native_elf_fingerprints": native,
        "candidate_binary_sha256_before": summary["candidate_binary_sha256_before"],
        "candidate_binary_sha256_after": summary["candidate_binary_sha256_after"],
        "verified_edge_oracles": edge_proofs,
        "rankings": rankings,
        "regressions": regressions,
        "self_test": controls,
        "memory_limitation": (
            "Ratios cover only Python-traced temporary allocations. Shared-process "
            "RSS and high-water marks do not establish isolated native-engine memory."
        ),
        "failed": 0,
    }
    encoded = (
        json.dumps(document, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    try:
        with output_path.open("xb") as destination:
            destination.write(encoded)
            destination.flush()
            os.fsync(destination.fileno())
    except FileExistsError as error:
        raise AuditError("the one-off v2 integrity result already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the unique v2 practice integrity result") from error
    return {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False, "cases_per_candidate": original.EXPECTED_CASES,
        "candidate_case_count": len(results),
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": original.EXPECTED_CORRECTNESS_CHECKS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regressions": len(regressions),
        "verified_native_library_count": len(native),
        "full_correctness_campaign_steps": 22,
        "poisoned_control_count": controls["poisoned_control_count"],
        "rust_optimization_verified": True,
        "unchanged_reference_candidates": UNCHANGED_REFERENCE_CANDIDATES,
        "output": original.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(), "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run only candidate-free, in-memory synthetic corruption controls")
    check = commands.add_parser("verify", help="independently replay the exact optimized four-way public practice run")
    check.add_argument("--raw", type=Path, required=True)
    check.add_argument("--summary", type=Path, required=True)
    check.add_argument("--from-scratch-audit", type=Path, required=True)
    check.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "self-test":
            result = self_test()
        else:
            result = verify(args.raw, args.summary, args.from_scratch_audit, args.output)
    except (AuditError, KeyError, ValueError, TypeError, OverflowError, RecursionError) as error:
        print(json.dumps({
            "schema": SCHEMA, "result": "FAIL", "holdout_accessed": False,
            "timing_performed": False, "error": str(error), "failed": 1,
        }, sort_keys=True))
        raise SystemExit(1) from error
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
