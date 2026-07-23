#!/usr/bin/env python3
"""Independently replay the single fully qualified Zig Stage-12 practice run.

All three earlier public experiments remain immutable.  Their replay helpers
and purely synthetic controls are reused without executing a regex candidate,
running a benchmark, or accessing any held-out workload.
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
from tools import rust_v7_multi_candidate_practice_v2_audit as second
from tools import rust_v7_multi_candidate_practice_v3_audit as third


ROOT = original.ROOT
EVIDENCE = original.EVIDENCE
SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v4"
SLOT = "three-qualified-engines-zig-span-256-v4"
PREFIX = "three-qualified-engines-public-practice-v4"
RAW_PATH = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE / f"{PREFIX}-summary.json"
OUTPUT_PATH = EVIDENCE / f"{PREFIX}-integrity.json"
CAMPAIGN_PATH = ROOT / "candidates/evidence/rust-v8-zig-stage-12-sealed-campaign.json"
ZIG_EDGE_PATH = ROOT / "candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-12.json.gz"

V1_AUDITOR_SHA256 = "bc093f114fe15833cab8f7c8d59bd1970345b6ddb47bc33349854be1af7f0ded"
V2_AUDITOR_SHA256 = "4dee19924cb0e4312ff9b62c70dd105f1f49aa4a7f3eeedaa650d9f9f5d853d4"
V3_AUDITOR_SHA256 = "1bd6a03a0d8e25b3041a31e095f97647f7d2e0b317e8ae3b8adf9b25113aefd4"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V3_INTEGRITY_SHA256 = "aa1921230845a01aa03d607bd8609b3475dc659cacda5e6135d8b7064ed60c22"
V4_AUDIT_SHA256 = "d68a14b5a2c4f181871afbc23c2d6e90150e7eb4752e9d636f035a8ad9cdf796"
V4_SUMMARY_SHA256 = "e23164b077b2bfa1abccaf8cce93a068bc7ea9b7ef444ef55905cc2fbd573e0c"
V4_COMPRESSED_RAW_SHA256 = "628b23d7797312fce35436a4709bb278995f1513b381c9cc302ee6caf5bda6fe"
V4_RAW_SHA256 = "1639451c8167062e0b7d847c969c6a1c4d613e784d86c7ca09044e9786085da0"
ZIG_CAMPAIGN_SHA256 = "f89fe9081421d28a291feab1b664c21a7c372762a548569856c6572e4a23eba6"
RUST_CAMPAIGN_SHA256 = "89793a597ac74551742d05bdf1c5af61f1121d89466e00ac2902c8942aaeef4d"
ZIG_EDGE_COMPRESSED_SHA256 = "b51fa4a87157f768433c28364d18771b089dfca80fdd997de442afb4ccdaf7d6"
ZIG_EDGE_PAYLOAD_SHA256 = "3abc55fe1722defb478f32a571c7eb0d00fa9bd93b7ac6ddc7a9227bdde3b2b8"
STAGE12_ZIG_SOURCE_SHA256 = "cb14210092d9ec92a2ac8c458d7b713342c8662bcf3318f954e0c520bc7b1589"
STAGE12_ZIG_BRIDGE_SHA256 = "4d1eb307eabc8b254ac0724aeb8ba106105d9879b7d46054b2355621fb330a92"
STAGE11_ZIG_SOURCE_SHA256 = "cdcf335f92f90c7ce98a93add914dabd0b607dc2742a4e7190a2187e538e959d"
STAGE11_ZIG_BRIDGE_SHA256 = "4d0dc7ece7ef42e34a8f425fab55429460e2fd66c587ce13c70539979393d13c"
UNCHANGED_ZIG_ENGINE_SHA256 = "70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614"
INITIAL_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
EXPECTED_REGRESSIONS = 402
UNCHANGED_REFERENCE_CANDIDATES = [
    "re", "candidates.rust_candidate", "candidates.vm_candidate"
]


AuditError = original.AuditError
require = original.require


def validate_version_identity(
    summary: dict, plan: dict, profile: original.Profile, raw_path: Path
) -> None:
    original.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == SLOT, "Zig Stage 12 changed its unique authorized practice slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "Zig Stage 12 substituted its raw practice observations")
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "Zig practice observations were represented as final performance",
    )


def validate_historical_continuity(
    v1: dict, v2: dict, v3: dict,
    sources: dict[str, str], native: dict[str, str], measured: dict[str, str],
) -> None:
    require(v3.get("schema") == third.SCHEMA, "the historical v3 comparison was replaced")
    require(v3.get("result") == "PASS" and v3.get("failed") == 0, "the historical v3 comparison did not independently pass")
    require(v3.get("holdout_accessed") is False and v3.get("timing_performed") is False, "historical v3 evidence accessed or timed held-out cases")
    require(v3.get("module_order") == list(original.MODULES), "historical v3 measured different candidate families")
    require(v3.get("cases_per_candidate") == original.EXPECTED_CASES, "historical v3 changed the practice case denominator")
    require(v3.get("trials_per_module_case") == original.EXPECTED_TRIALS, "historical v3 changed the paired trial denominator")
    require(v3.get("bootstrap_draws") == original.EXPECTED_BOOTSTRAPS, "historical v3 changed the bootstrap protocol")
    require(v3.get("frozen_plan_sha256") == original.EXPECTED_PLAN_SHA256, "historical v3 changed the 624 frozen practice cases")
    require(v3.get("source_sha256") == V3_AUDITOR_SHA256, "the immutable v3 verifier source changed")
    require(v3.get("historical_v1_integrity_sha256") == V1_INTEGRITY_SHA256, "historical v3 no longer binds its original v1 result")
    require(v3.get("historical_v2_integrity_sha256") == V2_INTEGRITY_SHA256, "historical v3 no longer binds its original v2 result")
    require(v3.get("from_scratch_audit_sha256") == third.V3_AUDIT_SHA256, "the historical v3 canonical independence proof changed")
    require(v3.get("strict_regressions") == third.EXPECTED_REGRESSIONS, "the historical v3 actual slowdown denominator changed")
    require(v3.get("full_correctness_campaign_sha256") == RUST_CAMPAIGN_SHA256, "the historical capacity-16 Rust campaign changed")
    require(v3.get("full_correctness_campaign_steps") == 22, "historical capacity-16 Rust did not pass all correctness stages")
    require(v3.get("initial_audit_failure_sha256") == INITIAL_FAILURE_SHA256, "the genuine historical Rust audit failure was concealed")
    require(v3.get("rust_optimization_verified") is True, "the previous Rust optimization was not independently qualified")
    require(v3.get("capacity16_optimization_verified") is True, "the previous Rust capacity-16 optimization was not independently qualified")
    previous_sources = v3.get("qualified_source_fingerprints")
    previous_native = v3.get("native_elf_fingerprints")
    previous_measured = v3.get("candidate_binary_sha256_before")
    require(isinstance(previous_sources, dict), "historical v3 source fingerprints are missing")
    require(isinstance(previous_native, dict), "historical v3 mapped-library fingerprints are missing")
    require(isinstance(previous_measured, dict), "historical v3 production fingerprints are missing")
    require(v3.get("candidate_binary_sha256_after") == previous_measured, "historical v3 changed artifacts during timing")
    third.validate_historical_continuity(
        v1, v2, previous_sources, previous_native, previous_measured
    )

    changed_source = "candidates/zig/py_bridge.c"
    changed_native = "candidates.zig_candidate:native-bridge"
    require(set(sources) == set(previous_sources), "v4 added or removed an independently audited production source")
    require(set(native) == set(previous_native), "v4 added or removed a mapped native regex engine")
    require(set(measured) == set(previous_measured), "v4 added or removed a measured baseline or candidate artifact")
    for path, digest in previous_sources.items():
        if path != changed_source:
            require(sources.get(path) == digest, f"the Zig-only experiment changed another production source: {path}")
    for role, digest in previous_native.items():
        if role != changed_native:
            require(native.get(role) == digest, f"the Zig-only experiment changed another native library: {role}")
    for role, digest in previous_measured.items():
        if role != changed_native:
            require(measured.get(role) == digest, f"the Zig-only experiment changed another measured candidate: {role}")

    require(previous_sources.get(changed_source) == STAGE11_ZIG_SOURCE_SHA256, "historical v3 did not contain the actual Stage-11 Zig bridge source")
    require(previous_native.get(changed_native) == STAGE11_ZIG_BRIDGE_SHA256, "historical v3 did not contain the actual Stage-11 Zig native bridge")
    require(sources.get(changed_source) == STAGE12_ZIG_SOURCE_SHA256, "the Stage-12 Zig source does not match its audited change")
    require(native.get(changed_native) == STAGE12_ZIG_BRIDGE_SHA256, "the Stage-12 Zig bridge does not match its audited binary")
    require(measured.get(changed_native) == STAGE12_ZIG_BRIDGE_SHA256, "the measured Zig bridge differs from the audited bridge")
    require(native.get("candidates.zig_candidate:native-engine") == UNCHANGED_ZIG_ENGINE_SHA256, "the supposedly unchanged owned Zig engine was substituted")
    require(STAGE12_ZIG_SOURCE_SHA256 != STAGE11_ZIG_SOURCE_SHA256, "the Stage-12 Zig source did not actually change")
    require(STAGE12_ZIG_BRIDGE_SHA256 != STAGE11_ZIG_BRIDGE_SHA256, "the Stage-12 Zig native bridge did not actually change")


def validate_v4_edges(summary: dict, measured: dict[str, str]) -> list[dict]:
    require(original.sha256_file(original.EDGE_SOURCE_PATH) == original.EXPECTED_EDGE_SOURCE_SHA256, "the frozen all-family correctness oracle changed")
    reference, reference_digest = original.read_edge(original.STDLIB_EDGE_PATH, "frozen Python matching reference")
    original.validate_edge_document(reference, "re")
    require(reference_digest == original.EXPECTED_STDLIB_EDGE_SHA256, "the frozen Python matching proof changed")
    require(original.sha256_file(ZIG_EDGE_PATH) == ZIG_EDGE_COMPRESSED_SHA256, "the Stage-12 Zig matching proof was substituted")
    require(original.sha256_file(third.RUST_EDGE_PATH) == third.V3_EDGE_COMPRESSED_SHA256, "the unchanged capacity-16 Rust matching proof was substituted")
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list) and len(proofs) == len(original.MODULES) - 1, "v4 omitted a candidate correctness gate")
    paths = {
        "candidates.rust_candidate": third.RUST_EDGE_PATH,
        "candidates.vm_candidate": second.C_EDGE_PATH,
        "candidates.zig_candidate": ZIG_EDGE_PATH,
    }
    for module, proof in zip(original.MODULES[1:], proofs, strict=True):
        require(isinstance(proof, dict) and proof.get("module") == module, "v4 correctness proofs are incomplete, substituted, or reordered")
        path = paths[module]
        require(proof.get("path") == str(path.resolve()), f"{module} names an unexpected independent correctness report")
        require(proof.get("correctness_checks") == 223_198, f"{module} omitted frozen Python compatibility cases")
        require(proof.get("actual_sha256") == original.EXPECTED_EDGE_ANSWER_SHA256, f"{module} does not match the frozen Python correctness oracle")
        require(proof.get("script_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, f"{module} used an altered matching-oracle implementation")
        require(proof.get("stdlib_baseline_sha256") == reference_digest, f"{module} changed the pinned Python correctness baseline")
        report, payload_digest = original.read_edge(path, f"{module} Stage-12 practice matching proof")
        original.validate_edge_document(report, module)
        require(proof.get("report_sha256") == payload_digest, f"{module} changed its edge proof after the one-off measurement")
        if module == "candidates.zig_candidate":
            require(payload_digest == ZIG_EDGE_PAYLOAD_SHA256, "the Zig proof is not the exact audited Stage-12 implementation")
        if module == "candidates.rust_candidate":
            require(payload_digest == third.V3_EDGE_PAYLOAD_SHA256, "v4 substituted the unchanged capacity-16 Rust implementation")
        artifacts = second.artifact_fingerprints(report.get("candidate_artifacts"), module)
        require(proof.get("candidate_artifacts") == artifacts, f"{module} timed different production artifacts than its correctness proof")
        for role, artifact in artifacts.items():
            if role == "public-python":
                key = f"{module}:module"
            elif module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == artifact["sha256"], f"{module} timed a missing, unqualified, or cross-family native artifact")
    return proofs


def validate_zig_campaign(campaign: dict, sources: dict[str, str], measured: dict[str, str]) -> None:
    require(campaign.get("schema") == "rebar-rust-campaign-gate-v1", "the frozen Zig campaign format changed")
    require(campaign.get("candidate") == "candidates.zig_candidate", "the Stage-12 campaign qualified another engine")
    require(campaign.get("passed") is True, "the full Stage-12 Zig correctness campaign did not pass")
    require(campaign.get("holdout_accessed") is False, "the full Stage-12 campaign accessed a final workload")
    require(campaign.get("timing_performed") is False and campaign.get("performance") == "NOT MEASURED", "the full Stage-12 correctness campaign performed benchmark timing")
    require(campaign.get("required_correctness_step_count") == 22, "the full Stage-12 campaign changed its correctness obligations")
    stages = campaign.get("steps")
    require(isinstance(stages, list) and len(stages) == 22, "the Stage-12 campaign omitted an official correctness stage")
    require(all(isinstance(stage, dict) and stage.get("passed") is True for stage in stages), "the Stage-12 Zig campaign contains an unexplained mismatch or crash")
    require(campaign.get("pinned_cpython") == "3.14.6", "the Stage-12 Zig campaign changed its Python baseline")
    require(campaign.get("python_executable") == str(original.PINNED_PYTHON), "the Stage-12 Zig campaign used another Python executable")
    require(campaign.get("mode") == "sealed-practice-only", "the Stage-12 Zig campaign changed its isolation mode")
    edge = campaign.get("edge_oracle")
    require(isinstance(edge, dict), "the Stage-12 campaign omitted its independent matching proof")
    require(edge.get("archive_sha256") == ZIG_EDGE_COMPRESSED_SHA256, "the Stage-12 campaign referenced a different compressed matching proof")
    require(edge.get("path") == str(ZIG_EDGE_PATH.resolve()), "the Stage-12 campaign referenced a different edge path")
    require(edge.get("checks") == 223_198 and edge.get("failed") == 0, "the Stage-12 campaign matching stage dropped or failed cases")
    require(edge.get("module") == "candidates.zig_candidate", "the Stage-12 campaign qualified a different candidate")
    complete = second.artifact_fingerprints(campaign.get("native_artifacts"), "candidates.zig_candidate")
    production = second.artifact_fingerprints(edge.get("production_artifacts"), "candidates.zig_candidate")
    qualified_edge = second.artifact_fingerprints(edge.get("candidate_artifacts"), "candidates.zig_candidate")
    require(complete == production, "the Stage-12 campaign changed its own production parser, bridge, or engine")
    for role, artifact in qualified_edge.items():
        require(complete.get(role) == artifact, "the Stage-12 edge report differs from the fully qualified Zig implementation")
    for role, artifact in complete.items():
        if role in {"bridge-source", "native-source"}:
            require(sources.get(artifact["path"]) == artifact["sha256"], "the Stage-12 campaign used an unaudited Zig compiler or bridge source")
        else:
            key = "candidates.zig_candidate:module" if role == "public-python" else f"candidates.zig_candidate:{role}"
            require(measured.get(key) == artifact["sha256"], "the Stage-12 timed Zig engine differs from its passing complete campaign")


def synthetic_histories() -> tuple[dict, dict, dict, dict[str, str], dict[str, str], dict[str, str]]:
    v1, v2, stage11_sources, stage11_native, stage11_measured = third.synthetic_histories()
    # Give the pure synthetic Zig history the same original Stage-11 identities
    # across all preserved experiments, without reading a production source.
    zig_source = "candidates/zig/py_bridge.c"
    zig_bridge = "candidates.zig_candidate:native-bridge"
    for historical in (v1, v2):
        historical["qualified_source_fingerprints"][zig_source] = STAGE11_ZIG_SOURCE_SHA256
        historical["native_elf_fingerprints"][zig_bridge] = STAGE11_ZIG_BRIDGE_SHA256
        historical["candidate_binary_sha256_before"][zig_bridge] = STAGE11_ZIG_BRIDGE_SHA256
        historical["candidate_binary_sha256_after"][zig_bridge] = STAGE11_ZIG_BRIDGE_SHA256
    stage11_sources[zig_source] = STAGE11_ZIG_SOURCE_SHA256
    stage11_native[zig_bridge] = STAGE11_ZIG_BRIDGE_SHA256
    stage11_measured[zig_bridge] = STAGE11_ZIG_BRIDGE_SHA256
    v3 = {
        "schema": third.SCHEMA, "result": "PASS", "failed": 0,
        "holdout_accessed": False, "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": V3_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": third.V3_AUDIT_SHA256,
        "strict_regressions": third.EXPECTED_REGRESSIONS,
        "full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "qualified_source_fingerprints": dict(stage11_sources),
        "native_elf_fingerprints": dict(stage11_native),
        "candidate_binary_sha256_before": dict(stage11_measured),
        "candidate_binary_sha256_after": dict(stage11_measured),
    }
    sources = {**stage11_sources, zig_source: STAGE12_ZIG_SOURCE_SHA256}
    native = {**stage11_native, zig_bridge: STAGE12_ZIG_BRIDGE_SHA256}
    measured = {**stage11_measured, zig_bridge: STAGE12_ZIG_BRIDGE_SHA256}
    native["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
    measured["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
    stage11_native["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
    stage11_measured["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
    v3["native_elf_fingerprints"]["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
    v3["candidate_binary_sha256_before"]["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
    v3["candidate_binary_sha256_after"]["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
    # Keep preserved v1 and v2 reference controls consistent in the synthetic
    # ancestry before invoking their unchanged, fail-closed validators.
    for historical in (v1, v2):
        historical["native_elf_fingerprints"]["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
        historical["candidate_binary_sha256_before"]["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
        historical["candidate_binary_sha256_after"]["candidates.zig_candidate:native-engine"] = UNCHANGED_ZIG_ENGINE_SHA256
    return v1, v2, v3, sources, native, measured


def self_test() -> dict:
    inherited = third.self_test()
    require(inherited.get("result") == "PASS", "the preserved v3 synthetic replay failed")
    earlier = inherited.get("poisoned_controls")
    require(isinstance(earlier, list) and len(earlier) >= 65, "the Stage-12 verifier dropped its 65 inherited corruption controls")
    plan, sample, _compressed, profile = original.synthetic_evidence()
    sample["exclusive_slot"] = SLOT
    sample["raw_path"] = str(RAW_PATH.resolve())
    sample["measurement"] = "balanced practice diagnostic only; not a holdout result or final speed claim"
    validate_version_identity(sample, plan, profile, RAW_PATH)
    v1, v2, v3, sources, native, measured = synthetic_histories()
    validate_historical_continuity(v1, v2, v3, sources, native, measured)
    controls = [*earlier]

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"the Stage-12 synthetic verifier accepted poisoned evidence: {name}")

    def poison_version(key: str, value: object) -> None:
        poisoned = copy.deepcopy(sample)
        poisoned[key] = value
        validate_version_identity(poisoned, plan, profile, RAW_PATH)

    def poison_history(which: str, key: str, value: object) -> None:
        first = copy.deepcopy(v1)
        second_history = copy.deepcopy(v2)
        third_history = copy.deepcopy(v3)
        current_sources = dict(sources)
        current_native = dict(native)
        current_measured = dict(measured)
        options = {
            "v1": first, "v2": second_history, "v3": third_history,
            "v3-sources": third_history["qualified_source_fingerprints"],
            "v3-native": third_history["native_elf_fingerprints"],
            "sources": current_sources, "native": current_native,
            "measured": current_measured,
        }
        options[which][key] = value
        validate_historical_continuity(
            first, second_history, third_history,
            current_sources, current_native, current_measured,
        )

    reject("v1-slot-cross-contamination", lambda: poison_version("exclusive_slot", original.EXPECTED_SLOT))
    reject("v2-slot-cross-contamination", lambda: poison_version("exclusive_slot", second.SLOT))
    reject("v3-slot-cross-contamination", lambda: poison_version("exclusive_slot", third.SLOT))
    reject("v4-output-prefix-incorrectly-used-as-slot", lambda: poison_version("exclusive_slot", PREFIX))
    reject("v1-raw-cross-contamination", lambda: poison_version("raw_path", str(original.RAW_PATH.resolve())))
    reject("v2-raw-cross-contamination", lambda: poison_version("raw_path", str(second.RAW_PATH.resolve())))
    reject("v3-raw-cross-contamination", lambda: poison_version("raw_path", str(third.RAW_PATH.resolve())))
    reject("practice-falsely-reported-as-final", lambda: poison_version("measurement", "final unseen benchmark"))
    reject("v1-history-replaced-with-v4", lambda: poison_history("v1", "schema", SCHEMA))
    reject("v2-history-replaced-with-v4", lambda: poison_history("v2", "schema", SCHEMA))
    reject("v3-history-replaced-with-v4", lambda: poison_history("v3", "schema", SCHEMA))
    reject("v3-actual-387-losses-hidden", lambda: poison_history("v3", "strict_regressions", third.EXPECTED_REGRESSIONS - 1))
    reject("v3-capacity16-full-campaign-substituted", lambda: poison_history("v3", "full_correctness_campaign_sha256", "0" * 64))
    reject("v3-rust-failure-record-concealed", lambda: poison_history("v3", "initial_audit_failure_sha256", "0" * 64))
    reject("v3-zig-source-replaced-with-stage12", lambda: poison_history("v3-sources", "candidates/zig/py_bridge.c", STAGE12_ZIG_SOURCE_SHA256))
    reject("v3-zig-binary-replaced-with-stage12", lambda: poison_history("v3-native", "candidates.zig_candidate:native-bridge", STAGE12_ZIG_BRIDGE_SHA256))
    reject("stage12-zig-source-not-actually-new", lambda: poison_history("sources", "candidates/zig/py_bridge.c", STAGE11_ZIG_SOURCE_SHA256))
    reject("stage12-zig-bridge-not-actually-new", lambda: poison_history("native", "candidates.zig_candidate:native-bridge", STAGE11_ZIG_BRIDGE_SHA256))
    reject("unchanged-zig-owned-engine-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-engine", "0" * 64))
    reject("unchanged-rust-source-substituted", lambda: poison_history("sources", "candidates/rust/py_bridge.c", "0" * 64))
    reject("unchanged-rust-native-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-bridge", "0" * 64))
    reject("unchanged-c-source-substituted", lambda: poison_history("sources", "candidates/_vm_native.c", "0" * 64))
    reject("unchanged-c-native-substituted", lambda: poison_history("native", "candidates.vm_candidate:native-engine", "0" * 64))
    reject("unchanged-python-baseline-substituted", lambda: poison_history("measured", "re:module", "0" * 64))
    require(len(controls) >= 89, "the Stage-12 verifier omitted historical or Zig-only isolation controls")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS", "synthetic_only": True,
        "holdout_accessed": False, "timing_performed": False,
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "inherited_poisoned_control_count": len(earlier),
        "poisoned_control_count": len(controls), "poisoned_controls": controls,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    require(platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6), "v4 verification requires pinned CPython 3.14.6")
    require(Path(sys.executable).resolve() == original.PINNED_PYTHON.resolve(), "v4 verification requires the exact baseline executable")
    require(raw_path.resolve() == RAW_PATH.resolve(), "v4 may not overwrite or substitute recorded historical observations")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "v4 may not overwrite or substitute a recorded historical summary")
    require(audit_path.resolve() == original.AUDIT_PATH.resolve(), "v4 may not substitute its actual source-independence audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "v4 may not overwrite or redirect earlier experiment evidence")
    require(not output_path.exists(), "the unique Stage-12 integrity result already exists")
    require(not any(name in sys.modules for name in original.MODULES[1:]), "v4 verification unexpectedly imported a candidate")
    require(original.sha256_file(Path(original.__file__).resolve()) == V1_AUDITOR_SHA256, "the frozen v1 replay source changed")
    require(original.sha256_file(Path(second.__file__).resolve()) == V2_AUDITOR_SHA256, "the frozen v2 replay source changed")
    require(original.sha256_file(Path(third.__file__).resolve()) == V3_AUDITOR_SHA256, "the frozen v3 replay source changed")
    require(original.sha256_file(third.INITIAL_FAILURE_PATH) == INITIAL_FAILURE_SHA256, "the actual historical Rust first-failure evidence was changed or removed")

    profile = original.Profile()
    plan = original.read_json(original.PLAN_PATH, "immutable 624-case practice plan", original.EXPECTED_PLAN_SHA256)
    require(plan.get("expected_sha256") == original.EXPECTED_FROZEN_ANSWER_SHA256, "v4 changed its frozen Python expected answers")
    original.validate_plan(plan, profile)
    summary = original.read_json(summary_path, "one-shot Stage-12 Zig public practice summary", V4_SUMMARY_SHA256)
    validate_version_identity(summary, plan, profile, raw_path)
    require(summary.get("compressed_raw_sha256") == V4_COMPRESSED_RAW_SHA256, "the Stage-12 practice gzip observations changed")
    require(summary.get("raw_sha256") == V4_RAW_SHA256, "the Stage-12 decompressed practice observations changed")
    require(original.sha256_file(raw_path) == V4_COMPRESSED_RAW_SHA256, "the exact Stage-12 compressed timing record changed")

    audit = original.read_json(audit_path, "Stage-12 five-library from-scratch audit", V4_AUDIT_SHA256)
    sources, native = original.validate_independence(audit)
    measured = original.validate_measured_fingerprints(summary, sources, native)
    v1 = original.read_json(original.OUTPUT_PATH, "immutable historical v1 practice experiment", V1_INTEGRITY_SHA256)
    v2 = original.read_json(second.OUTPUT_PATH, "immutable historical v2 practice experiment", V2_INTEGRITY_SHA256)
    v3 = original.read_json(third.OUTPUT_PATH, "immutable historical v3 practice experiment", V3_INTEGRITY_SHA256)
    validate_historical_continuity(v1, v2, v3, sources, native, measured)
    edge_proofs = validate_v4_edges(summary, measured)
    zig_campaign = original.read_json(CAMPAIGN_PATH, "passing complete Stage-12 Zig campaign", ZIG_CAMPAIGN_SHA256)
    validate_zig_campaign(zig_campaign, sources, measured)
    rust_campaign = original.read_json(third.CAMPAIGN_PATH, "preserved complete capacity-16 Rust campaign", RUST_CAMPAIGN_SHA256)
    third.validate_full_campaign(rust_campaign, measured)

    try:
        with raw_path.open("rb") as source:
            observations = original.read_observations(source, V4_COMPRESSED_RAW_SHA256, summary, plan, profile)
    except OSError as error:
        raise AuditError("cannot open the one-off Stage-12 paired practice observations") from error
    case_results, rankings = original.recompute_results(plan, observations, profile)
    regressions = original.validate_results(summary, case_results, rankings, profile)
    require(len(regressions) == EXPECTED_REGRESSIONS, "the Stage-12 experiment concealed or changed its actual 402 substantial slowdowns")
    controls = self_test()
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the Stage-12 results verifier imported a candidate")

    document = {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of one recorded Zig Stage-12 four-way public practice run; not final or held-out performance",
        "exclusive_slot": SLOT,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "candidate_case_count": len(case_results),
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": original.EXPECTED_CORRECTNESS_CHECKS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "confidence_intervals_recomputed": len(case_results) + len(rankings),
        "strict_regression_speedup_threshold": original.REGRESSION_THRESHOLD,
        "strict_regressions": len(regressions),
        "summary_sha256": V4_SUMMARY_SHA256,
        "compressed_raw_sha256": V4_COMPRESSED_RAW_SHA256,
        "raw_sha256": V4_RAW_SHA256,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": original.sha256_file(Path(__file__).resolve()),
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": V4_AUDIT_SHA256,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(original.MODULES) - 1,
        "verified_native_library_count": len(native),
        "full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "rust_full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "rust_full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
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
        raise AuditError("the unique Stage-12 Zig integrity output already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the unique Stage-12 Zig integrity output") from error
    return {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "cases_per_candidate": original.EXPECTED_CASES,
        "candidate_case_count": len(case_results),
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": original.EXPECTED_CORRECTNESS_CHECKS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "confidence_intervals_recomputed": len(case_results) + len(rankings),
        "strict_regressions": len(regressions),
        "verified_native_library_count": len(native),
        "full_correctness_campaign_steps": 22,
        "rust_full_correctness_campaign_steps": 22,
        "poisoned_control_count": controls["poisoned_control_count"],
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "output": original.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(), "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run only candidate-free synthetic corruption and historical-isolation controls")
    check = commands.add_parser("verify", help="replay the exact fully qualified Stage-12 Zig public practice experiment")
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
